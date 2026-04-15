# Sender-Receiver game

`oTree`: 6.0.11

`python`: 3.12.4

# **📖 Experiment Architecture (Updated March 2026)**

## **1️⃣ Overview**
This experiment has been restructured from a live 2-player interactive game into a **1-player simulation**. All live participants now play exclusively as **Player B (Receivers)**. The actions of Player A (Senders) are simulated using historical data collected from previous experimental sessions.

## **2️⃣ Single-Player Architecture**
- **Group Size**: `players_per_group = None` (Each participant is in their own group of 1).
- **Role Assignment**: Every participant is assigned the role of `Player B` (Receiver).
- **Historical Data Integration**: Instead of waiting for a live Player A to send a message, the system loads historical messages and secret numbers from a pre-generated CSV file (`messages_for_receivers.csv`).

## **3️⃣ Data Mapping & Assignment**
- During `creating_session` (Round 1), each live participant is randomly assigned a unique `sender_code` from `messages_for_receivers.csv`.
- For all 4 rounds, the live participant faces the exact sequence of `secret_number`, `sender_message`, and `sender_choice` of their assigned historical sender.
- Assigned codes are marked `used = 1` in the CSV after session creation to avoid reuse across sessions.
- **Pool exhaustion guard**: if the number of unused codes is smaller than the number of participants in the session, the system falls back to the full pool (all rows) before shuffling, so no two participants in the same session ever share a sender code.

### CSV files
| File | Description |
|---|---|
| `messages_for_receivers.csv` | Default file for `ExpertRep`. Columns: `code`, `secret_number_R1`–`R24`, `sender_message_R1`–`R24`, `sender_choice_R1`–`R24`, `used` |
| `messages_for_receivers_belief.csv` | File used by `Belief` treatment (same structure as default file, with independent `used` tracking) |
| `messages_for_receivers_with_X.csv` | File used by `FixBelief`. Adds `X_R1`–`X_R24` (how many of 4 senders delegated each round) |
| `messages_for_receivers_with_X_secrets.csv` | File used by `NoUncertainty`. Includes `X_R1`–`X_R24` and bundled secret numbers `secret_number_1_R1`–`secret_number_4_R24` for 4-sender evaluation |

### `sender_choice` values
- `1`–`7`: Sender manually chose that number to send.
- `8`: Sender delegated to the computer (honest — message equals true secret number).

## **4️⃣ Payoffs & Incentives**
- **Decoding Task**: Paid based on a piece-rate (`PIECE_RATE_DECODE` = 500 COP) per correct answer.
- **Sender-Receiver Game**: Quadratic scoring rule; only `PREDEFINED_RECEIVER_ROUNDS` are payoff-relevant. Bonus = `BONUS_AMOUNT` (4000 COP).
- **Honesty Guess** (`HonestyGuess` page): Participant guesses the % of times their assigned sender delegated to the computer. Incentivized with `HONESTY_GUESS_BONUS` (1000 COP) via quadratic scoring.
- **Honesty Certainty** (`HonestyCertainty` page): Follow-up confidence question for the honesty guess.
- **Credulity Guess** (`FollowingGuess` page): Participant guesses the % of times other receivers followed the message when it was 7. Incentivized with `CREDULITY_GUESS_BONUS` (1000 COP).
- **Explanation Task** (`ExplanationTask` page): Participant writes their guessing strategy. A post-session ChatGPT evaluation determines the bonus (`EXPLANATION_BONUS` = 4000 COP).

## **5️⃣ Treatments**

The treatment is set in `settings.py` via the `treatment` key in each session config and stored in `player.participant.treatment`. Assignment happens in `welcome/__init__.py` with a single line:
```python
player.participant.treatment = player.session.config['treatment']
```

Active treatments:

| Treatment | Session name | Description |
|---|---|---|
| `ExpertRep` | `sender_receiver_game_expertrep` | Baseline: receiver enters a direct guess via slider |
| `Belief` | `sender_receiver_game_belief` | Receiver states a belief % about lying; computer computes optimal guess |
| `FixBelief` | `sender_receiver_game_fixbelief` | Receiver sees delegation composition from a 4-sender message bundle (`X` delegated, `4-X` did not delegate) and enters one direct guess |
| `NoUncertainty` | `sender_receiver_game_nouncertainty` | Receiver sees one message from a 4-sender bundle, enters one direct guess, and payoff is computed by aggregating performance against all 4 bundled secret numbers |

### **ExpertRep**
The baseline treatment. Player A had the option to delegate message selection to a computer that always sends the true secret number. Player B sees the message and moves a slider to enter a direct guess of the secret number.

### **Belief**
Player B states their **belief about the likelihood that Player A delegated to the computer** (i.e., was honest). The computer then automatically computes and submits the **optimal guess** using the quadratic scoring rule:

$$g^* = p \cdot \text{message} + (1 - p) \cdot 4$$

where $p$ is the stated belief (fraction honest/delegated) and $4$ is the unconditional mean of the secret number. The belief is stored in `player.belief_honest_pct` (0–100 integer, `initial=0`). The optimal guess is computed server-side in `ReceiverGuess.before_next_page` and written to `player.receiver_guess`. The belief slider starts at 0% (left) and only reveals the submit button once the participant moves it. On timeout without interaction, `belief_honest_pct` remains 0, so the computer submits `g* = 4` (no trust). The decoding step is skipped for this treatment.

### **FixBelief**
Receiver sees that each observed message comes from a bundle of 4 prior senders and is informed how many delegated (`X`) vs did not delegate (`4-X`). Receiver still submits one direct guess.

### **NoUncertainty**
Receiver sees one message per round from a 4-sender bundle (plus `X` delegation composition) and submits one guess. Unlike other direct-guess treatments, this single guess is evaluated against all 4 sender secret numbers from the bundle (`secret_number_1_Rt` to `secret_number_4_Rt`), and round performance is based on the average accuracy across those 4 realizations.

**Important:** the binary scoring rule is still used in `NoUncertainty`. The only change is how the receiver win probability is constructed: first compute accuracy against each of the 4 bundled secret numbers, then average those 4 accuracies into a single receiver probability, and finally apply the same binary draw used in other treatments.

## **6️⃣ Page Sequence**

```
PreviousExperimentInfo → instructions1 → instructions2 → TimeLimit → Decode (always hidden)
→ instructions3 → instructions4
→ role_info                  [includes BeliefTransition content for Belief treatment]
→ ControlQuestions ×5       [round 1, repeats until all correct]
→ TutorialIntro
→ ReceiverTutorial          [ExpertRep only, round 1]
→ FixBeliefTutorial         [FixBelief only, round 1]
→ NoUncertaintyTutorial     [NoUncertainty only, round 1]
→ BeliefTutorial            [Belief only, round 1]
→ start_page
→ Round_number → ReceiverGuess → Results    [every round]
→ HonestyGuess → HonestyCertainty → FollowingGuess → ExplanationTask   [last round only]
```

Key per-treatment differences:

| Page / Logic | ExpertRep | Belief | FixBelief | NoUncertainty |
|---|---|---|---|---|
| CSV source | `messages_for_receivers.csv` | `messages_for_receivers_belief.csv` | `messages_for_receivers_with_X.csv` | `messages_for_receivers_with_X_secrets.csv` |
| Tutorial page | `ReceiverTutorial` | `BeliefTutorial` | `FixBeliefTutorial` | `NoUncertaintyTutorial` |
| `ReceiverGuess` inputs | direct guess | belief slider + computed guess | direct guess + X info | direct guess + X info + 4-box bundle visual |
| Payoff evaluation | vs one secret number | vs one secret number (computer guess) | vs one secret number | vs 4 secret numbers (average score) |
| Results feedback | direct guess and true number | belief + computed guess | direct guess and true number + bundle context | direct guess + full 4-secret bundle evaluation summary |

## **7️⃣ Key Pages**

### `PreviousExperimentInfo.html`
Uses arrow-reveal blocks (same pattern as `instructions1.html`). Three sections:
1. Always visible: context about the previous experiment (Player A/B roles, delegation).
2. Arrow 1 → "Your Task Today": describes today's task; for Belief, a treatment-conditional paragraph explains that they will report a belief % instead of a direct guess.
3. Arrow 2 → "About the Instructions Below": why to read the historical instructions carefully. Reveals the Next button.

### `BeliefTransition.html`
Its content is integrated into `role_info.html`, shown conditionally for Belief participants. The legacy `BeliefTransition` file/class remains in the repository but is not included in `page_sequence`. The integrated block explains:
- The previous experiment had Player B guess directly; today's task is different.
- They will report a belief about the likelihood that Player A delegated to the computer.
- The computer submits the **guess that maximises their bonus** given that belief — so they should report their true belief.
- The formula $g^* = p \times m + (1-p) \times 4$ is hidden behind a "Show the formula" modal button.

### `BeliefTutorial.html`
Interactive intro.js-guided tutorial for the belief slider (replaces `ReceiverTutorial` for Belief). Tour steps:
1. Introduction
2. Left-pane reminder
3. Round number
4. Player A's message
5. Belief slider — **blocked** until participant moves it; unblocks Next on first interaction
6. Optimal guess card — shows the computed guess after the slider is moved
7. Submit button

### `ReceiverGuess.html` (Belief decision screen)
In Belief treatment, the Spanish elicitation is framed as a **probability/likelihood** question (not “how often”): participants report the percentage probability that Player A delegated to the computer. The UI then displays the implied optimal guess and submits it on confirmation.

### `ControlQuestions.html`
`Q_task` is now treatment-aware:
- ExpertRep: correct answer = *"Adivinar el número secreto"*; options list = `O_task`
- Belief: correct answer = *"Reportar mi creencia sobre cuántas veces el Jugador A delegó al computador"*; options list = `O_task_Belief` (no "Adivinar" option shown)
- Hint (`H_task_Belief`) explains the belief mechanism on wrong answer.

Additional treatment-specific checks:
- FixBelief includes `Q_fixbelief_understanding`.
- NoUncertainty includes `Q_nouncertainty_understanding`.

### `ReceiverGuess.html` (NoUncertainty)
The decision screen explicitly displays the message as coming from a 4-sender bundle and includes a 4-box visual (computer vs chose) to show delegation composition (`X` delegated, `4-X` did not delegate).

### `Results.html` (NoUncertainty)
Results page shows that the single submitted guess was evaluated against all 4 secret numbers in the bundle and reports the round's average accuracy across those 4 comparisons.

## **8️⃣ Survey**
The final survey (`survey` app) collects: `age`, `gender`, `education`, `student`, `experiments`, `reasoning`, `chosen_role`. The fundaciones opinion table was removed. All fields are in Spanish.

## **9️⃣ Obsolete Features (Removed)**
- **Live Matching Protocol**: Pool-based matching system removed; no live Player As.
- **Wait Pages**: All synchronization wait pages removed.
- **Sender UI**: Pages for Player A actions removed from the page sequence.
- **Babbling / Decode treatments**: Removed from all logic and templates. Only `ExpertRep`, `Belief`, `FixBelief`, `NoUncertainty` are active.

## **🔟 Repository Naming & Current Working Copy (March 2026)**

- `SR_otree-NEW-2026` is the **current active project folder**.
- `SR_otree-NEW-2026_BACKUP` is a **backup snapshot** kept for archival/reference purposes.

### What changed during this reorganization
- The previous backup folder named `SR_otree-NEW-2026` was renamed to `SR_otree-NEW-2026_BACKUP`.
- The working folder that had been named `SR_otree-NEW-2026_treatment_timing` was renamed to `SR_otree-NEW-2026` and is now the canonical active version.

This keeps the active project under the standard name while preserving the pre-change copy as a clearly labeled backup.
