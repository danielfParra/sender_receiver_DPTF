import argparse
import csv
import glob
import json
import os
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from openai import OpenAI

from config import DATA_RAW_DIR, ENV_FILE, PROMPTS_DIR, RESULTS_DIR, RUNS_DIR, get_openai_api_key, load_analysis_env


MODEL_NAME = "gpt-5.4-mini"
TEMPERATURE = 0
EXPECTED_SAMPLE_SIZE = 10

SUPPORTED_TREATMENTS = ("ExpertRep", "FixBelief", "NoUncertainty", "Belief")
DIRECT_GUESS_TREATMENTS = {"ExpertRep", "FixBelief", "NoUncertainty"}
TREATMENT_PROMPT_FILES = {
    "ExpertRep": "ExpertRep.txt",
    "FixBelief": "FixBelief.txt",
    "NoUncertainty": "NoUncertainty.txt",
    "Belief": "Belief.txt",
}

COL_PARTICIPANT_CODE = "participant.code"
COL_PARTICIPANT_LABEL = "participant.label"
COL_SESSION_CODE = "session.code"
COL_ROUND = "subsession.round_number"
COL_EXPLANATION = "player.strategy_explanation"
COL_MESSAGE_ENCODED = "player.sender_message_encoded"
COL_MESSAGE_RAW = "player.sender_message"
COL_GUESS = "player.receiver_guess"
COL_TREATMENT = "player.treatment"
COL_X_COUNT = "player.x_count"
COL_BELIEF_HONEST_PCT = "player.belief_honest_pct"


@dataclass
class ParticipantRow:
    key: Tuple[str, str]
    participant_code: str
    participant_label: str
    explanation: str
    explanation_empty: int
    treatment: str


@dataclass
class GPTPredictionResult:
    predicted_guesses: Dict[int, float]
    predicted_beliefs_pct: Optional[Dict[int, int]]
    raw_content: str
    output_mode: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze oTree explanation task with GPT and export one row per participant."
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Optional path to an oTree export CSV. If omitted, uses latest data_raw/N5_sender_receiver_game_YYYY-MM-DD.csv",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed. If omitted, a seed is generated and saved in run metadata.",
    )
    parser.add_argument(
        "--round-for-explanations",
        type=int,
        default=24,
        help="Round number used to identify participant explanations.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=EXPECTED_SAMPLE_SIZE,
        help="Number of random rounds used for replication scoring.",
    )
    parser.add_argument(
        "--raw-dir",
        default=DATA_RAW_DIR,
        help="Directory where manually downloaded oTree CSV files are stored.",
    )
    parser.add_argument(
        "--results-dir",
        default=RESULTS_DIR,
        help="Directory for output CSV results.",
    )
    parser.add_argument(
        "--runs-dir",
        default=RUNS_DIR,
        help="Directory for run metadata and raw model outputs.",
    )
    parser.add_argument(
        "--prompts-dir",
        default=PROMPTS_DIR,
        help="Directory containing system_prompt.txt, user_prompt_template.txt, and prompts/treatments/*.txt",
    )
    parser.add_argument(
        "--env-file",
        default=ENV_FILE,
        help="Path to optional .env file with OPENAI_API_KEY",
    )
    return parser.parse_args()


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_prompts(prompts_dir: str) -> Tuple[str, str]:
    system_path = os.path.join(prompts_dir, "system_prompt.txt")
    user_template_path = os.path.join(prompts_dir, "user_prompt_template.txt")

    if not os.path.exists(system_path):
        raise FileNotFoundError(f"Missing prompt file: {system_path}")
    if not os.path.exists(user_template_path):
        raise FileNotFoundError(f"Missing prompt file: {user_template_path}")

    system_prompt = read_text_file(system_path)
    user_template = read_text_file(user_template_path)

    required_placeholders = [
        "{{TREATMENT}}",
        "{{TREATMENT_INSTRUCTIONS}}",
        "{{EXPLANATION}}",
        "{{ROUNDS_JSON}}",
    ]
    missing = [x for x in required_placeholders if x not in user_template]
    if missing:
        raise ValueError(
            "user_prompt_template.txt is missing placeholders: " + ", ".join(missing)
        )

    return system_prompt, user_template


def load_treatment_prompts(prompts_dir: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    treatment_dir = os.path.join(prompts_dir, "treatments")
    prompts: Dict[str, str] = {}
    paths: Dict[str, str] = {}

    for treatment, filename in TREATMENT_PROMPT_FILES.items():
        path = os.path.join(treatment_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing treatment prompt file: {path}")
        prompts[treatment] = read_text_file(path)
        paths[treatment] = path

    return prompts, paths


def detect_input_file(raw_dir: str) -> str:
    pattern = os.path.join(raw_dir, "N5_sender_receiver_game_*.csv")
    candidates = glob.glob(pattern)
    if not candidates:
        raise FileNotFoundError(
            f"No files found in {raw_dir}. Add a file named N5_sender_receiver_game_YYYY-MM-DD.csv"
        )

    def date_key(path: str) -> datetime:
        name = os.path.basename(path)
        match = re.search(r"N5_sender_receiver_game_(\d{4}-\d{2}-\d{2})\.csv$", name)
        if not match:
            return datetime.min
        return datetime.strptime(match.group(1), "%Y-%m-%d")

    candidates.sort(key=lambda p: (date_key(p), os.path.getmtime(p)), reverse=True)
    return candidates[0]


def read_csv_rows(path: str) -> List[Dict[str, str]]:
    last_error: Optional[Exception] = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            with open(path, "r", encoding=encoding, newline="") as f:
                return list(csv.DictReader(f))
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Could not read CSV file {path}: {last_error}")


def safe_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        return int(float(text))
    except Exception:
        return None


def safe_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except Exception:
        return None


def clean_text(value: Optional[str]) -> str:
    return "" if value is None else str(value).strip()


def normalize_treatment(value: Optional[str], allow_blank: bool = False) -> str:
    text = clean_text(value)
    if text == "":
        if allow_blank:
            return ""
        raise ValueError("Encountered blank treatment value.")

    lookup = {
        "expertrep": "ExpertRep",
        "fixbelief": "FixBelief",
        "nouncertainty": "NoUncertainty",
        "belief": "Belief",
    }
    normalized = lookup.get(text.lower())
    if normalized is None:
        raise ValueError(
            f"Unsupported treatment '{text}'. Expected one of: {', '.join(SUPPORTED_TREATMENTS)}"
        )
    return normalized


def normalize_predicted_guess(value: float) -> float:
    value = max(0.0, min(7.0, value))
    return round(value, 1)


def normalize_predicted_belief_pct(value: float) -> int:
    value = max(0.0, min(100.0, value))
    return int(round(value))


def ensure_columns(rows: List[Dict[str, str]], required_cols: List[str]) -> None:
    if not rows:
        raise ValueError("Input CSV has no data rows.")
    cols = set(rows[0].keys())
    missing = [c for c in required_cols if c not in cols]
    if missing:
        raise ValueError(f"Input CSV missing required columns: {missing}")


def validate_required_treatment_columns(rows: List[Dict[str, str]]) -> None:
    cols = set(rows[0].keys())
    treatments_seen = {
        normalize_treatment(row.get(COL_TREATMENT), allow_blank=True)
        for row in rows
        if clean_text(row.get(COL_TREATMENT)) != ""
    }

    if any(t in {"FixBelief", "NoUncertainty"} for t in treatments_seen) and COL_X_COUNT not in cols:
        raise ValueError(
            f"Input CSV missing required treatment-specific column: {COL_X_COUNT}"
        )


def build_participant_roster(rows: List[Dict[str, str]], round_for_explanations: int) -> List[ParticipantRow]:
    roster: List[ParticipantRow] = []
    seen = set()

    for row in rows:
        round_num = safe_int(row.get(COL_ROUND))
        if round_num != round_for_explanations:
            continue

        session_code = clean_text(row.get(COL_SESSION_CODE))
        participant_code = clean_text(row.get(COL_PARTICIPANT_CODE))
        participant_label = clean_text(row.get(COL_PARTICIPANT_LABEL))
        explanation = clean_text(row.get(COL_EXPLANATION))
        treatment = normalize_treatment(row.get(COL_TREATMENT))

        key = (session_code, participant_code)
        if key in seen:
            continue
        seen.add(key)

        roster.append(
            ParticipantRow(
                key=key,
                participant_code=participant_code,
                participant_label=participant_label,
                explanation=explanation,
                explanation_empty=1 if explanation == "" else 0,
                treatment=treatment,
            )
        )

    if not roster:
        raise ValueError(
            f"No participants found in round {round_for_explanations}. "
            "Check the input file and round setting."
        )

    return roster


def build_round_index(rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], Dict[int, Dict[str, str]]]:
    index: Dict[Tuple[str, str], Dict[int, Dict[str, str]]] = {}
    for row in rows:
        session_code = clean_text(row.get(COL_SESSION_CODE))
        participant_code = clean_text(row.get(COL_PARTICIPANT_CODE))
        round_num = safe_int(row.get(COL_ROUND))
        if round_num is None:
            continue
        key = (session_code, participant_code)
        if key not in index:
            index[key] = {}
        index[key][round_num] = row
    return index


def validate_participant_treatments(
    round_index: Dict[Tuple[str, str], Dict[int, Dict[str, str]]],
    roster: List[ParticipantRow],
) -> None:
    for participant in roster:
        rows_for_participant = round_index.get(participant.key, {})
        observed = set()
        for row in rows_for_participant.values():
            raw_treatment = clean_text(row.get(COL_TREATMENT))
            if raw_treatment == "":
                continue
            observed.add(normalize_treatment(raw_treatment))

        if not observed:
            raise ValueError(
                f"No treatment values found across rounds for participant {participant.participant_code}."
            )
        if len(observed) != 1:
            raise ValueError(
                f"Inconsistent treatment values for participant {participant.participant_code}: {sorted(observed)}"
            )
        observed_value = next(iter(observed))
        if observed_value != participant.treatment:
            raise ValueError(
                f"Treatment mismatch for participant {participant.participant_code}: "
                f"round-{participant.treatment} roster value differs from full-history value {observed_value}."
            )


def get_available_rounds(
    round_index: Dict[Tuple[str, str], Dict[int, Dict[str, str]]],
    roster: List[ParticipantRow],
) -> List[int]:
    all_round_sets = []
    for participant in roster:
        per_round = round_index.get(participant.key, {})
        available_for_participant = set()
        for round_num, row in per_round.items():
            msg = clean_text(row.get(COL_MESSAGE_ENCODED))
            guess = safe_float(row.get(COL_GUESS))
            sender_message_numeric = safe_float(row.get(COL_MESSAGE_RAW))
            if msg == "" or guess is None or sender_message_numeric is None:
                continue

            if participant.treatment in {"FixBelief", "NoUncertainty"}:
                x_count = safe_int(row.get(COL_X_COUNT))
                if x_count is None or not 0 <= x_count <= 4:
                    continue

            available_for_participant.add(round_num)
        all_round_sets.append(available_for_participant)

    if not all_round_sets:
        return []

    common = set.intersection(*all_round_sets)
    return sorted(common)


def extract_json(text: str) -> Dict:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("Model output does not contain valid JSON object.")


def prediction_output_mode(treatment: str) -> str:
    return "predict_belief_then_compute_guess" if treatment == "Belief" else "predict_guess_directly"


def build_prompt(
    treatment: str,
    treatment_prompt: str,
    explanation: str,
    rounds_payload: List[Dict[str, object]],
    system_prompt: str,
    user_template: str,
) -> Tuple[str, str]:
    user_prompt = (
        user_template.replace("{{TREATMENT}}", treatment)
        .replace("{{TREATMENT_INSTRUCTIONS}}", treatment_prompt)
        .replace("{{EXPLANATION}}", explanation)
        .replace("{{ROUNDS_JSON}}", json.dumps(rounds_payload, ensure_ascii=True))
    )
    return system_prompt, user_prompt


def build_round_context(
    participant: ParticipantRow,
    selected_rounds: List[int],
    per_round: Dict[int, Dict[str, str]],
) -> Tuple[List[Optional[float]], List[Dict[str, object]], Dict[int, Dict[str, object]], bool]:
    participant_guesses: List[Optional[float]] = []
    rounds_payload: List[Dict[str, object]] = []
    round_meta: Dict[int, Dict[str, object]] = {}
    missing_round_data = False

    for round_num in selected_rounds:
        row = per_round.get(round_num)
        if row is None:
            participant_guesses.append(None)
            missing_round_data = True
            continue

        message_encoded = clean_text(row.get(COL_MESSAGE_ENCODED))
        human_guess = safe_float(row.get(COL_GUESS))
        sender_message_numeric = safe_float(row.get(COL_MESSAGE_RAW))
        if message_encoded == "" or human_guess is None or sender_message_numeric is None:
            participant_guesses.append(None)
            missing_round_data = True
            continue

        payload: Dict[str, object] = {
            "round": round_num,
            "sender_message_encoded": message_encoded,
        }

        if participant.treatment in {"FixBelief", "NoUncertainty"}:
            x_count = safe_int(row.get(COL_X_COUNT))
            if x_count is None or not 0 <= x_count <= 4:
                participant_guesses.append(None)
                missing_round_data = True
                continue
            payload.update(
                {
                    "x_count": x_count,
                    "strategic_sender_count": 4 - x_count,
                    "delegation_probability": round(x_count / 4.0, 4),
                    "delegation_probability_pct": int(x_count * 25),
                }
            )

        participant_guesses.append(human_guess)
        rounds_payload.append(payload)
        round_meta[round_num] = {
            "sender_message_numeric": sender_message_numeric,
        }

    return participant_guesses, rounds_payload, round_meta, missing_round_data


def compute_guess_from_belief_pct(predicted_belief_pct: int, sender_message_numeric: float) -> float:
    p = predicted_belief_pct / 100.0
    msg = sender_message_numeric if sender_message_numeric > 0 else 4.0
    optimal = p * msg + (1 - p) * 4.0
    return round(max(1.0, min(7.0, optimal)), 1)


def call_gpt_predictions(
    client: OpenAI,
    participant: ParticipantRow,
    rounds_payload: List[Dict[str, object]],
    round_meta: Dict[int, Dict[str, object]],
    system_prompt: str,
    user_template: str,
    treatment_prompt: str,
    max_attempts: int = 3,
) -> GPTPredictionResult:
    system_prompt, user_prompt = build_prompt(
        participant.treatment,
        treatment_prompt,
        participant.explanation,
        rounds_payload,
        system_prompt,
        user_template,
    )
    last_error: Optional[Exception] = None
    output_mode = prediction_output_mode(participant.treatment)

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=TEMPERATURE,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = response.choices[0].message.content or ""
            payload = extract_json(content)
            predictions = payload.get("predictions")
            if not isinstance(predictions, list):
                raise ValueError("'predictions' key missing or not a list.")

            expected_rounds = {int(x["round"]) for x in rounds_payload}

            if participant.treatment == "Belief":
                belief_predictions: Dict[int, int] = {}
                guess_predictions: Dict[int, float] = {}

                for item in predictions:
                    if not isinstance(item, dict):
                        continue
                    round_num = safe_int(item.get("round"))
                    pred_belief_pct = safe_float(item.get("predicted_belief_pct"))
                    if round_num is None or pred_belief_pct is None:
                        continue
                    belief_pct = normalize_predicted_belief_pct(pred_belief_pct)
                    belief_predictions[round_num] = belief_pct

                if set(belief_predictions.keys()) != expected_rounds:
                    raise ValueError(
                        f"Belief predictions missing rounds. Expected {sorted(expected_rounds)}, "
                        f"got {sorted(belief_predictions.keys())}."
                    )

                for round_num, belief_pct in belief_predictions.items():
                    sender_message_numeric = float(round_meta[round_num]["sender_message_numeric"])
                    guess_predictions[round_num] = compute_guess_from_belief_pct(
                        belief_pct, sender_message_numeric
                    )

                return GPTPredictionResult(
                    predicted_guesses=guess_predictions,
                    predicted_beliefs_pct=belief_predictions,
                    raw_content=content,
                    output_mode=output_mode,
                )

            guess_predictions = {}
            for item in predictions:
                if not isinstance(item, dict):
                    continue
                round_num = safe_int(item.get("round"))
                pred = safe_float(item.get("predicted_guess"))
                if round_num is None or pred is None:
                    continue
                guess_predictions[round_num] = normalize_predicted_guess(pred)

            if set(guess_predictions.keys()) != expected_rounds:
                raise ValueError(
                    f"Predictions missing rounds. Expected {sorted(expected_rounds)}, "
                    f"got {sorted(guess_predictions.keys())}."
                )

            return GPTPredictionResult(
                predicted_guesses=guess_predictions,
                predicted_beliefs_pct=None,
                raw_content=content,
                output_mode=output_mode,
            )
        except Exception as exc:
            last_error = exc
            if attempt < max_attempts:
                time.sleep(1.5 * attempt)

    raise RuntimeError(f"GPT prediction call failed after retries: {last_error}")


def round_match(human_guess: float, llm_guess: float, threshold: float = 1.0) -> int:
    return 1 if abs(human_guess - llm_guess) <= threshold else 0


def write_csv(path: str, rows: List[Dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def format_seconds(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def main() -> None:
    args = parse_args()
    start_time = time.time()

    os.makedirs(args.results_dir, exist_ok=True)
    os.makedirs(args.runs_dir, exist_ok=True)

    load_analysis_env(args.env_file)
    system_prompt, user_template = load_prompts(args.prompts_dir)
    treatment_prompts, treatment_prompt_paths = load_treatment_prompts(args.prompts_dir)

    input_path = args.input or detect_input_file(args.raw_dir)
    rows = read_csv_rows(input_path)

    ensure_columns(
        rows,
        [
            COL_PARTICIPANT_CODE,
            COL_PARTICIPANT_LABEL,
            COL_SESSION_CODE,
            COL_ROUND,
            COL_EXPLANATION,
            COL_MESSAGE_ENCODED,
            COL_MESSAGE_RAW,
            COL_GUESS,
            COL_TREATMENT,
        ],
    )
    validate_required_treatment_columns(rows)

    roster = build_participant_roster(rows, args.round_for_explanations)
    round_index = build_round_index(rows)
    validate_participant_treatments(round_index, roster)

    available_rounds = get_available_rounds(round_index, roster)
    if len(available_rounds) < args.sample_size:
        raise ValueError(
            f"Not enough common rounds with treatment-complete message+guess data. "
            f"Need {args.sample_size}, got {len(available_rounds)}."
        )

    seed = args.seed if args.seed is not None else random.SystemRandom().randint(1, 10**9)
    rng = random.Random(seed)
    selected_rounds = sorted(rng.sample(available_rounds, args.sample_size))
    treatments_seen = sorted({p.treatment for p in roster})

    print("Starting explanation analysis...")
    print(f"Input file: {input_path}")
    print(f"Participants in round {args.round_for_explanations}: {len(roster)}")
    print(f"Treatments seen: {treatments_seen}")
    print(f"Selected rounds ({args.sample_size}): {selected_rounds}")
    print(f"Model: {MODEL_NAME} | Temperature: {TEMPERATURE}")
    print(f"Seed: {seed}")

    api_key = get_openai_api_key()
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    result_rows: List[Dict[str, object]] = []
    raw_llm_rows: List[Dict[str, object]] = []
    stats = {
        "ok": 0,
        "empty_explanation_skipped": 0,
        "missing_round_data": 0,
        "llm_error": 0,
    }
    scores_ok: List[float] = []

    total_participants = len(roster)
    for idx, participant in enumerate(roster, start=1):
        elapsed = time.time() - start_time
        avg_per_participant = elapsed / idx
        eta = avg_per_participant * (total_participants - idx)
        print(
            f"[{idx}/{total_participants}] participant={participant.participant_code} "
            f"treatment={participant.treatment} "
            f"elapsed={format_seconds(elapsed)} eta={format_seconds(eta)}"
        )

        per_round = round_index.get(participant.key, {})
        participant_guesses, rounds_payload, round_meta, missing_round_data = build_round_context(
            participant,
            selected_rounds,
            per_round,
        )

        llm_output_mode = prediction_output_mode(participant.treatment)
        llm_predictions: List[Optional[float]] = [None] * len(selected_rounds)
        predicted_beliefs: List[Optional[int]] = [None] * len(selected_rounds)
        matches: List[Optional[int]] = [None] * len(selected_rounds)
        mean_score = None
        matches_count = None
        bonus_probability = None
        bonus_draw_u = None
        won_bonus_rule = "won_if_bonus_draw_u_lt_bonus_probability"
        won_bonus = None

        if participant.explanation_empty == 1:
            status = "empty_explanation_skipped"
            stats[status] += 1
        elif missing_round_data:
            status = "missing_round_data"
            stats[status] += 1
        else:
            try:
                treatment_prompt = treatment_prompts[participant.treatment]
                prediction_result = call_gpt_predictions(
                    client,
                    participant,
                    rounds_payload,
                    round_meta,
                    system_prompt,
                    user_template,
                    treatment_prompt,
                )

                for i, round_num in enumerate(selected_rounds):
                    llm_pred = prediction_result.predicted_guesses[round_num]
                    human_guess = float(participant_guesses[i])
                    match_score = round_match(human_guess, llm_pred, threshold=1.0)
                    llm_predictions[i] = llm_pred
                    matches[i] = match_score
                    if prediction_result.predicted_beliefs_pct is not None:
                        predicted_beliefs[i] = prediction_result.predicted_beliefs_pct[round_num]

                matches_count = int(sum(x for x in matches if x is not None))
                bonus_probability = matches_count / len(matches)
                mean_score = bonus_probability * 100.0
                bonus_draw_u = rng.random()
                won_bonus = 1 if bonus_draw_u < bonus_probability else 0
                status = "ok"
                stats[status] += 1
                scores_ok.append(mean_score)

                raw_llm_rows.append(
                    {
                        "session_code": participant.key[0],
                        "participant_code": participant.participant_code,
                        "treatment": participant.treatment,
                        "treatment_prompt_file": treatment_prompt_paths[participant.treatment],
                        "llm_output_mode": prediction_result.output_mode,
                        "selected_rounds": json.dumps(selected_rounds),
                        "prompt_round_payload": json.dumps(rounds_payload, ensure_ascii=True),
                        "llm_predictions": json.dumps(prediction_result.predicted_guesses, ensure_ascii=True),
                        "predicted_beliefs_pct": json.dumps(
                            prediction_result.predicted_beliefs_pct, ensure_ascii=True
                        )
                        if prediction_result.predicted_beliefs_pct is not None
                        else "",
                        "raw_response_content": prediction_result.raw_content,
                    }
                )
            except Exception as exc:
                status = f"llm_error: {str(exc)}"
                stats["llm_error"] += 1

        result_rows.append(
            {
                "participant.code": participant.participant_code,
                "participant.label": participant.participant_label,
                "treatment": participant.treatment,
                "llm_output_mode": llm_output_mode,
                "explanation_empty": participant.explanation_empty,
                "selected_rounds": json.dumps(selected_rounds),
                "participant_guesses_sample": json.dumps(participant_guesses),
                "llm_predictions_sample": json.dumps(llm_predictions),
                "predicted_beliefs_sample": json.dumps(predicted_beliefs)
                if participant.treatment == "Belief"
                else "",
                "round_matches_sample": json.dumps(matches),
                "matches_count": matches_count,
                "bonus_probability": None if bonus_probability is None else round(bonus_probability, 6),
                "bonus_draw_u": None if bonus_draw_u is None else round(bonus_draw_u, 6),
                "won_bonus_rule": won_bonus_rule,
                "score": None if mean_score is None else round(mean_score, 6),
                "won_bonus": won_bonus,
                "status": status,
            }
        )

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    input_stem = os.path.splitext(os.path.basename(input_path))[0]

    result_csv = os.path.join(args.results_dir, f"explanation_results_{input_stem}_{ts}.csv")
    write_csv(result_csv, result_rows)

    raw_llm_csv = os.path.join(args.runs_dir, f"raw_llm_{input_stem}_{ts}.csv")
    write_csv(raw_llm_csv, raw_llm_rows)

    manifest = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "input_file": input_path,
        "prompts_dir": args.prompts_dir,
        "env_file": args.env_file,
        "round_for_explanations": args.round_for_explanations,
        "selected_rounds": selected_rounds,
        "seed": seed,
        "sample_size": args.sample_size,
        "model": MODEL_NAME,
        "temperature": TEMPERATURE,
        "prompt_schema_version": 2,
        "scoring_rule": "threshold_bonus_abs_diff_leq_1",
        "bonus_rule": "bonus_probability_equals_share_of_matches_across_sampled_rounds",
        "belief_prediction_mode": "predict_belief_then_compute_guess",
        "treatments_seen": treatments_seen,
        "treatment_prompt_files": treatment_prompt_paths,
        "result_csv": result_csv,
        "raw_llm_csv": raw_llm_csv,
        "participants_total": len(roster),
        "participants_empty_explanation": sum(p.explanation_empty for p in roster),
        "participants_ok": stats["ok"],
        "participants_missing_round_data": stats["missing_round_data"],
        "participants_llm_error": stats["llm_error"],
    }

    manifest_path = os.path.join(args.runs_dir, f"run_manifest_{input_stem}_{ts}.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("Analysis completed.")
    print(f"Input file: {input_path}")
    print(f"Treatments seen: {treatments_seen}")
    print(f"Selected rounds: {selected_rounds}")
    print(f"Seed: {seed}")
    print(f"Result CSV: {result_csv}")
    print(f"Manifest: {manifest_path}")
    print("Run stats:")
    print(f"  ok: {stats['ok']}")
    print(f"  empty_explanation_skipped: {stats['empty_explanation_skipped']}")
    print(f"  missing_round_data: {stats['missing_round_data']}")
    print(f"  llm_error: {stats['llm_error']}")
    if scores_ok:
        print(f"  avg_score_ok: {sum(scores_ok)/len(scores_ok):.2f}")
        print(f"  min_score_ok: {min(scores_ok):.2f}")
        print(f"  max_score_ok: {max(scores_ok):.2f}")
    total_elapsed = time.time() - start_time
    print(f"Total runtime: {format_seconds(total_elapsed)}")


if __name__ == "__main__":
    main()
