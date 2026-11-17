# Gemini rerun (Nov 2026): 4 prompt arms

A new experiment on the same "tailor my CV summary to a job post" task as [Prompt Eval Lab](../index.html), run with Gemini through the API instead of Claude. It is **not** a replication of the original Claude result (47/50 vs 18/50).

## Arms

- **A**: the plain prompt from the lab, verbatim.
- **A80**: A plus one line, "Maximum 80 words."
- **B**: the structured prompt from the lab, verbatim (80-word limit).
- **Bm** (mirror arm, added Nov 17): B with only the line "Use only skills and experience that appear in the CV summary. Never add anything new." removed.

## Setup

Same CV, 5 job posts (two good matches, a stretch, a neighbor field, and an MLOps "trap" asking for tools the CV doesn't have) x 2 runs = 10 answers per arm. Each answer is scored on 4 pass/fail checks by a blind Gemini grader (answers shown as X/Y/Z in shuffled order) plus an 80-word limit counted by code. 5 points per answer, 50 per arm.

Models: answers by `gemini-3.6-flash` (22 of 30 on Nov 16) and `gemini-3-flash-preview` (the rest, incl. all MLOps answers); grading by `gemini-3-flash-preview` and `gemini-3.5-flash-lite`. Each Bm answer used the same answer and grader model as the B answer in its cell. Pro models had no free-tier quota, so a Pro grader wasn't possible. Temperature was left at the API default.

## Results

| Arm | Score /50 | c1 matching skills | c2 adds nothing new | c3 natural | c4 paste-ready | Under 80 words |
|---|---:|---:|---:|---:|---:|---:|
| A | 9/50 | 8 | 0 | 1 | 0 | 0 |
| A80 | 20/50 | 8 | 0 | 2 | 4 | 6 |
| B | 49/50 | 10 | 10 | 9 | 10 | 10 |
| Bm | 43/50 | 8 | 6 | 9 | 10 | 10 |

On the MLOps trap, A and A80 named a missing tool (Kubernetes, Docker, Terraform, CI/CD) in every run. B and Bm never did. Bm still stretched the framing on the trap ("support / management of machine learning systems"), which the grader counted as invented.

## What I take from it

- A length line alone (A80) fixes some of the length and format problems but none of the invented skills.
- Removing B's no-invention line (Bm) did not bring invention back to A's level (c2: 6/10 vs 0/10). Most of the protection comes from the rest of the structure. The line closes the remaining gap, mostly on the trap case.

## Caveats

- Small n (10 answers per arm), one run, Flash-level graders.
- Bm was graded next to the Nov 16 A and B answers, not A80. Regrading A and B in those calls gave 8/50 and 48/50 (vs 9 and 49), with no change on c2.
- Two of Bm's four c2 fails are strict calls (a goal line, and "transforming raw operational data").
- Bm still contains "If the job asks for something the CV lacks, leave it out," which overlaps with the removed rule.

## Files

- `run_eval.py`: Nov 16 run (A, A80, B). Needs `GEMINI_API_KEY`.
- `run_mirror.py`, `summarize_mirror.py`: Nov 17 mirror arm and 4-arm tables.
- `raw_outputs.jsonl`, `results.json`, `results_table.csv`: Nov 16 answers, grades and tables.
- `mirror_arm/`: Bm prompt, answers, grades, the 4-arm CSV and a detailed write-up (`MIRROR_ARM.md`).
