# Explanation Task Analysis

This folder contains a standalone script to evaluate participant explanations with GPT.

Path and environment configuration live in `analysis_explanations/config.py`.

## What the script does

- Reads an oTree export file (`N5_sender_receiver_game_YYYY-MM-DD.csv`) from `analysis_explanations/data_raw/`.
- Identifies participants from round 24 only.
- Includes participants with empty explanations and flags them with `explanation_empty = 1`.
- Reads treatment from `player.treatment`.
- Builds treatment-aware prompts so GPT sees the same round context the participant saw.
- Uses `player.sender_message_encoded` as the message input in all treatments.
- Adds `player.x_count` to the prompt for `FixBelief` and `NoUncertainty`.
- For `Belief`, asks GPT to predict the participant's belief about delegation and then computes the final guess in code using the experiment rule.
- Randomly samples 10 rounds once at script start.
- Uses GPT model `gpt-5.4-mini` with `temperature = 0`.
- Outputs one row per participant code in a results CSV.

## Required CSV columns

Base columns:

- `participant.code`
- `participant.label`
- `session.code`
- `subsession.round_number`
- `player.strategy_explanation`
- `player.sender_message`
- `player.sender_message_encoded`
- `player.receiver_guess`
- `player.treatment`

Treatment-specific columns:

- `player.x_count` is required when the file contains `FixBelief` or `NoUncertainty`.

## Prompt files

These files are the single source of truth for prompting:

- `analysis_explanations/prompts/system_prompt.txt`
- `analysis_explanations/prompts/user_prompt_template.txt`
- `analysis_explanations/prompts/treatments/ExpertRep.txt`
- `analysis_explanations/prompts/treatments/FixBelief.txt`
- `analysis_explanations/prompts/treatments/NoUncertainty.txt`
- `analysis_explanations/prompts/treatments/Belief.txt`

The user template must contain:

- `{{TREATMENT}}`
- `{{TREATMENT_INSTRUCTIONS}}`
- `{{EXPLANATION}}`
- `{{ROUNDS_JSON}}`

## Treatment behavior

- `ExpertRep`: GPT predicts a direct numeric guess from the message and explanation.
- `FixBelief`: GPT predicts a direct numeric guess and receives round-level `x_count`.
- `NoUncertainty`: GPT predicts a direct numeric guess and receives round-level `x_count`.
- `Belief`: GPT predicts `predicted_belief_pct`, then the script computes the implied final guess using `p * message + (1 - p) * 4`.

## Scoring rule

For each sampled round:

- It counts as a match if `|human_guess - llm_guess| <= 1`.

Then:

- `bonus_probability = matches_count / sample_size`
- `score = bonus_probability * 100`

## Setup

1. Install dependencies:

```bash
pip install -r analysis_explanations/requirements.txt
```

2. Set API key:

- Copy `analysis_explanations/.env.example` to `analysis_explanations/.env`.
- Put your key there as `OPENAI_API_KEY=...`.

3. Edit prompts if needed:

- `analysis_explanations/prompts/`

## Run

```bash
python analysis_explanations/run_explanation_analysis.py
```

PowerShell launcher:

```powershell
.\analysis_explanations\run_analysis.ps1
```

CMD launcher:

```cmd
analysis_explanations\run_analysis.cmd
```

Optional arguments:

- `--input <path>`: Use a specific CSV file.
- `--seed <int>`: Force deterministic random seed.
- `--round-for-explanations <int>`: Default is `24`.
- `--sample-size <int>`: Default is `10`.

## Main output columns

- `participant.code`
- `participant.label`
- `treatment`
- `llm_output_mode`
- `explanation_empty`
- `selected_rounds`
- `participant_guesses_sample`
- `llm_predictions_sample`
- `predicted_beliefs_sample`
- `round_matches_sample`
- `matches_count`
- `bonus_probability`
- `bonus_draw_u`
- `won_bonus_rule`
- `score`
- `won_bonus`
- `status`

Additional run metadata is written to:

- `analysis_explanations/results/`
- `analysis_explanations/runs/`
- `analysis_explanations/backup/`
