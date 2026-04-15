

|variable                    |type      |description                                                            |levels                           |
|:---------------------------|:---------|:----------------------------------------------------------------------|:--------------------------------|
|id_in_session               |integer   |Unique participant identifier within the session                       |                                 |
|code                        |character |Anonymous participant code                                             |                                 |
|payoff                      |integer   |Cumulative payoff (in pesos) for the session                           |                                 |
|id_in_group                 |integer   |Position in the pair (1 = Sender/A, 2 = Receiver/B)                    |1 = Sender (A); 2 = Receiver (B) |
|role                        |factor    |Role assignment: Player A (sender) or Player B (receiver)              |Player A; Player B               |
|player_payoff               |integer   |Round‑level payoff from the decoding bonus                             |                                 |
|pool                        |integer   |Matching pool ID used for pairing participants                         |                                 |
|decoding_answer             |logical   |Answer to the decoding task (if any)                                   |                                 |
|receiver_type               |factor    |Receiver treatment type: decode or direct                              |                                 |
|is_sender_payoff_relevant   |integer   |Indicator that this round counts toward Player A’s payoff              |                                 |
|is_receiver_payoff_relevant |integer   |Indicator that this round counts toward Player B’s payoff              |                                 |
|honesty_guess               |integer   |Participant’s % guess of the group’s honesty rate (end of game)        |                                 |
|credulity_guess             |integer   |Participant’s % guess of the group’s credulity rate (end of game)      |                                 |
|secret_number               |integer   |True secret number drawn each round (1–7)                              |                                 |
|sender_choice               |integer   |Raw numeric choice by Player A before encoding                         |                                 |
|sender_message              |integer   |Final numeric message sent (0 if timeout)                              |                                 |
|sender_message_encoded      |character |Encoded message string received by Player B                            |                                 |
|receiver_guess              |numeric   |Numeric guess submitted by Player B (0 if timeout)                     |                                 |
|sender_win_prob             |numeric   |Computed probability that the sender wins the bonus                    |                                 |
|receiver_win_prob           |numeric   |Computed probability that the receiver wins the bonus                  |                                 |
|sender_wins                 |integer   |Indicator whether the sender won the bonus                             |                                 |
|receiver_wins               |integer   |Indicator whether the receiver won the bonus                           |                                 |
|honesty_rate                |numeric   |Observed group honesty rate (fraction truthful)                        |                                 |
|credulity_rate              |numeric   |Observed group credulity rate (fraction high guesses when message = 7) |                                 |
|round_number                |integer   |Experiment round index (1–num_rounds)                                  |                                 |
|treatment                   |factor    |Experimental condition assigned                                        |                                 |
|session_code                |character |Alphanumeric code identifying the session                              |                                 |
|session                     |integer   |Numeric session ID                                                     |                                 |
|id                          |integer   |Global participant ID: unique sequential across sessions               |                                 |
|correct_answers             |integer   |Count of correctly solved decoding tasks so far                        |                                 |
|age                         |integer   |Participant age in years                                               |                                 |
|gender                      |integer   |Numeric gender code                                                    |0 = Female; 1 = Male             |
|gender_add                  |logical   |Did participant specify a non‑binary/other gender?                     |                                 |
|education                   |integer   |Numeric code for highest education level                               |                                 |
|student                     |factor    |Student status: Student vs Non‑Student                                 |Student; Non‑Student             |
|experiments                 |integer   |Number of prior experiments participated in                            |                                 |
|reasoning                   |character |Free‑text strategy reasoning                                           |                                 |
|chosen_role                 |factor    |Participant’s stated preferred role                                    |                                 |
|pool_cluster                |integer   |Hierarchical cluster ID derived from pool                              |                                 |
|treatment2                  |factor    |Secondary treatment label (duplicate of treatment)                     |                                 |


