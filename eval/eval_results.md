# RAG Evaluation Report

Dataset: 15 questions (12 answerable and 3 unanswerable).

PASS: Expected keywords are present, or an unanswerable question is correctly refused.  
FAIL: The model returned an answer that did not meet the evaluation criteria.  
ERROR: The API or evaluation request failed. Errors are not counted as failures.

Note: This is a simple keyword-based evaluation. Answers should also be reviewed for factual accuracy.

## Summary

| Config | Top-k | Answerable passed | Refusals passed | Total passed | Errors | Passed with citation |
|---|---:|---:|---:|---:|---:|---:|
| A | 3 | 7/12 | 3/3 | 10/15 | 0 | 7 |
| B | 6 | 10/12 | 3/3 | 13/15 | 0 | 10 |

Best configuration by total passed: Config B

## Config A details (top-k 3)

| # | Result | Answer | Citations |
|---:|---|---|---:|
| 1 | FAIL | I don't know. This is not in the MoHFW documents I have. | 0 |
| 2 | FAIL | OPV, Vitamin A, fIPV, PCV, and Penta are due at 6 weeks. | 2 |
| 3 | FAIL | I don't know. This is not in the MoHFW documents I have. | 0 |
| 4 | PASS | It is given intramuscularly in the anterolateral (mid‑thigh) of the newborn. | 1 |
| 5 | PASS | 0.1 ml | 2 |
| 6 | PASS | I don't know. This is not in the MoHFW documents I have. | 0 |
| 7 | PASS | Pentavalent can be given up to 1 year of age. | 2 |
| 8 | PASS | The first Measles/Rubella dose is given after the child completes 9 months of age, up to 12 months. | 1 |
| 9 | FAIL | I don't know. This is not in the MoHFW documents I have. | 0 |
| 10 | PASS | Pregnant women receive the Tetanus Toxoid (TT) vaccine. The first dose is given as early as possible after pregnancy is confirmed, and the second dose is given 4 weeks later. If a woman has not received two doses in a previous pregnancy, the recommended booster schedule applies. | 2 |
| 11 | FAIL | I don't know. This is not in the MoHFW documents I have. | 0 |
| 12 | PASS | The OPV booster is given at 16‑24 months of age. | 1 |
| 13 | PASS | The second DPT booster is given at 5‑6 years of age. | 2 |
| 14 | PASS | I don't know. This is not in the MoHFW documents I have. | 0 |
| 15 | PASS | I don't know. This is not in the MoHFW documents I have. | 0 |

## Config B details (top-k 6)

| # | Result | Answer | Citations |
|---:|---|---|---:|
| 1 | PASS | It is not too late. Vaccines scheduled for 6 weeks can be given after 6 weeks, up to 1 year of age. | 1 |
| 2 | FAIL | OPV, Vitamin A, fractional IPV, Penta and PCV are due at 6 weeks. | 2 |
| 3 | FAIL | I don't know. This is not in the MoHFW documents I have. | 0 |
| 4 | PASS | It is given intramuscularly in the anterolateral side of the left mid‑thigh. | 2 |
| 5 | PASS | The BCG dose after one month of age is 0.1 ml. | 1 |
| 6 | PASS | I don't know. This is not in the MoHFW documents I have. | 0 |
| 7 | PASS | Pentavalent can be given up to the child's first birthday (i.e., before 1 year of age). | 2 |
| 8 | PASS | The first Measles‑Rubella dose is given after the child reaches 9 months of age (between 9 and 12 months). | 1 |
| 9 | PASS | The first dose is given at 9 months of age, together with the measles vaccine, and the amount is 1 ml (100,000 IU). | 2 |
| 10 | PASS | Pregnant women receive the Tetanus Toxoid (TT) vaccine. The first dose is given as early as possible after pregnancy is confirmed, and the second dose is given 4 weeks after the first dose. If a woman has not received two doses in a previous pregnancy, the recommended booster schedule applies. | 2 |
| 11 | PASS | 0.5 ml is given at birth, and it should be administered within 24 hours (maximum protection if given within 12 hours). | 2 |
| 12 | PASS | The OPV booster is given at 16‑24 months of age. | 1 |
| 13 | PASS | The second DPT booster is given at 5‑6 years of age. | 2 |
| 14 | PASS | I don't know. This is not in the MoHFW documents I have. | 0 |
| 15 | PASS | I don't know. This is not in the MoHFW documents I have. | 0 |

