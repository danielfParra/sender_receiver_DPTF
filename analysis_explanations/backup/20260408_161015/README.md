# Explanation Task Analysis

This folder contains a standalone script to evaluate participant explanations with GPT.

Path and environment configuration live in `analysis_explanations/config.py`.

## What the script does

- Reads an oTree export file (`N5_sender_receiver_game_YYYY-MM-DD.csv`) from `analysis_explanations/data_raw/`.
- Identifies participants from round 24 only.
- Includes participants with empty explanations and flags them with `explanation_empty = 1`.
- Randomly samples 10 rounds once at script start.
- Uses `player.sender_message_encoded` as LLM input.
- Uses GPT model `gpt-5.4-mini` with `temperature = 0`.
- Outputs one row per participant code in a results CSV.

## Setup

1. Install dependencies:

```bash
pip install -r analysis_explanations/requirements.txt
```

2. Set API key (safe option):

- Copy `analysis_explanations/.env.example` to `analysis_explanations/.env`.
- Put your key there as `OPENAI_API_KEY=...`.
- The `.env` file is ignored by git.
- The script loads this file automatically through `python-dotenv`.

Alternative: export `OPENAI_API_KEY` in your shell.

3. Edit prompts if needed:

- `analysis_explanations/prompts/system_prompt.txt`
- `analysis_explanations/prompts/user_prompt_template.txt`

These files are the single source of truth for prompting.
The user template must contain placeholders `{{EXPLANATION}}` and `{{ROUNDS_JSON}}`.
Predicted guesses may be integers or decimals with exactly one decimal digit.

## Scoring Rule Rationale

Why this rule and not a continuous score:
We considered a continuous quadratic scoring rule of the form score = 100 - (100/36) * (guess_human - guess_LLM)^2, which penalizes larger differences more. However, we rejected it because the penalty was too flat in the middle of the scale - a difference of 3 points (half the scale) still yielded a score of 75/100, meaning nearly everyone would earn a high bonus regardless of agreement quality.
The threshold rule solves this by drawing a hard line: only close agreement (difference of 0 or 1) is rewarded. This is also consistent with the experimental economics literature - Arrieta & Nielsen (2025) use an equivalent fixed-prize-for-correct-guess rule in their replication paradigm rather than a continuous score.

## API key examples

Windows CMD:

```bash
set OPENAI_API_KEY=your_key_here
```

PowerShell:

```bash
$env:OPENAI_API_KEY="your_key_here"
```

## Run

```bash
python analysis_explanations/run_explanation_analysis.py
```

PowerShell launcher:

```powershell
.\analysis_explanations\run_analysis.ps1
```

If PowerShell blocks `.ps1` scripts because of execution policy, use the CMD launcher instead:

```cmd
analysis_explanations\run_analysis.cmd
```

You can also pass arguments through the launcher, for example:

```powershell
.\analysis_explanations\run_analysis.ps1 --seed 12345
```

CMD example:

```cmd
analysis_explanations\run_analysis.cmd --seed 12345
```

Optional arguments:

- `--input <path>`: Use a specific CSV file.
- `--seed <int>`: Force deterministic random seed.
- `--round-for-explanations <int>`: Default is `24`.
- `--sample-size <int>`: Default is `10`.

## Main output columns

- `participant.code`
- `participant.label`
- `explanation_empty`
- `selected_rounds`
- `participant_guesses_sample`
- `llm_predictions_sample`
- `round_matches_sample`
- `matches_count`
- `bonus_probability`
- `bonus_draw_u`
- `won_bonus_rule`
- `score`
- `won_bonus`
- `status`

Output files are written to:

- `analysis_explanations/results/`
- `analysis_explanations/runs/`
