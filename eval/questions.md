# TeekaTimer: 10 test questions

| # | Question | Expected answer (from MoHFW Unit 2 schedule) |
|---|----------|-----------------------------------------------|
| 1 | My baby is 7 weeks old and missed the 6-week session. Is it too late for the 6-week vaccines? | No. The latest ages are 5 years for OPV and 1 year for Pentavalent, fractional IPV and rotavirus. Please confirm with the ANM. |
| 2 | Which vaccines are due at 6 weeks? | OPV 1, Pentavalent 1, Fractional IPV, and Rotavirus and PCV where applicable |
| 3 | Which vaccines are given at birth? | BCG, Hepatitis B birth dose and OPV-0 |
| 4 | Where is the Hepatitis B birth dose given? | 0.5 ml intramuscular, antero-lateral side of mid-thigh (left), within 24 hours |
| 5 | What is the BCG dose after the baby is one month old? | 0.1 ml intradermal on the left upper arm (0.05 ml until 1 month) |
| 6 | Which hospital in Kopargaon gives free vaccines on Sunday? | CANNOT BE ANSWERED from this data. The app must say "I don't know" and refer to the health worker. |
| 7 | Until what age can Pentavalent be given? | Up to 1 year of age |
| 8 | When is the first Measles/Rubella dose given? | At 9 completed months to 12 months |
| 9 | When is the first Vitamin A dose and how much is given? | At 9 months, 1 ml (1 lakh IU), oral |
| 10 | Which vaccine do pregnant women get and when? | TT-1 early in pregnancy, TT-2 4 weeks after TT-1 |

## Results of the first TF-IDF run
- Q1 to Q5 and Q7: the top result was relevant and correct
- Q6: "I don't know" (correct, the data cannot answer it)
- Q8: returned the 2nd Measles/Rubella dose instead of the 1st
- Q9: returned the 2nd to 9th Vitamin A dose instead of the 1st
- Q10: "I don't know" (wrong), probably because the records say "pregnancy" and the question says "pregnant women"

Note: Q6 was changed on 14 Nov. The first Q6 (paracetamol) turned out to be answerable, because the handbook mentions paracetamol in the adverse events chapter (6 chunks on pages 177, 188, 196 and 197). The new Q6 asks about a local hospital, which the national documents cannot answer.
