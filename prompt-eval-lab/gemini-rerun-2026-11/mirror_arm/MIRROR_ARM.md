# Mirror arm: prompt B without the no-invention rule

Run on 2026-11-17, 15:20–15:48 Asia/Jerusalem (UTC+2). Suggested by Sage (Medium reply, Nov 17).

## What changed

Arm **Bm** = prompt B with exactly one line removed:

> - Use only skills and experience that appear in the CV summary. Never add anything new.

Everything else in B is unchanged (exact prompt: `prompt_Bm.txt`). Note that B keeps another rule that partly overlaps:
"If the job asks for something the CV lacks, leave it out. Do not mention the gap." So Bm is not a prompt with *no* anti-invention guidance; it lost the explicit "never add anything new" rule only.

## Same setup as Nov 16

- Same CV, same 5 job posts (incl. the MLOps trap) x 2 runs = 10 answers, same rubric (4 grader checks + word limit counted by code with `/\S+/`), same grader prompt, temperature left at the API default, same Gemini API key and call code (`run_eval.py`, imported unchanged).
- Same models per cell: each Bm answer was written by the model that wrote that cell's Nov 16 B answer (`gemini-3.6-flash` for 7, `gemini-3-flash-preview` for Junior DE run 2 and both MLOps runs) and graded by that cell's Nov 16 grader (`gemini-3-flash-preview` for Junior DA, BI, DS run 1; `gemini-3.5-flash-lite` for DS run 2, Junior DE, MLOps). The API returned the same model version strings as on Nov 16.
- **One difference:** grading is blind X/Y/Z per (job, run), as before, but the three answers were Nov 16 A, Nov 16 B and the new Bm (shuffled, seed 20261117), instead of A, A80, B. Only Bm's grades are new scores. The A and B grades from these calls are kept as a consistency check and do not replace the Nov 16 scores.
- 20 API calls in total (10 answers + 10 grading calls). `gemini-3.6-flash` returned several 503 "high demand" errors and timeouts; the script retried the same model, so no fallback model was used.

## Results

| Arm | Score /50 |
|---|---:|
| A (plain) | 9/50 |
| A80 (A + "Maximum 80 words.") | 20/50 |
| B (structured) | 49/50 |
| **Bm (B minus the no-invention line)** | **43/50** |

| Check (out of 10) | A | A80 | B | Bm |
|---|---:|---:|---:|---:|
| c1: Highlights 2+ CV skills the job asks for | 8 | 8 | 10 | 8 |
| c2: Adds nothing not in the CV (no-invention) | 0 | 0 | 10 | **6** |
| c3: Reads naturally, no buzzwords | 1 | 2 | 9 | 9 |
| c4: Paste-ready, no notes | 0 | 4 | 10 | 10 |
| Word limit (code count) | 0 | 6 | 10 | 10 |

| Job post (2 runs, /10) | A | A80 | B | Bm |
|---|---:|---:|---:|---:|
| Junior Data Analyst | 2 | 6 | 10 | 10 |
| BI Analyst, retail | 2 | 3 | 10 | 9 |
| Data Scientist, 3+ years | 3 | 4 | 9 | 10 |
| Junior Data Engineer | 2 | 7 | 10 | 9 |
| MLOps Engineer (trap) | 0 | 0 | 10 | 5 |

Word counts: Bm average 46.9 (max 58), none over 80 (B: 48.8, max 55).

MLOps trap, string check for Kubernetes / Docker / Terraform / CI/CD / Java / Go: A named a missing tool in 2/2 runs, A80 2/2, B 0/2, **Bm 0/2**.

### The 4 Bm c2 fails

- **MLOps run 1** (2/5): "…Background includes managing reporting workflows and production tasks in an operations setting. Focused on using data management and technical problem-solving to support machine learning systems." Grader: "It invents machine learning systems support which is not in the CV."
- **MLOps run 2** (3/5): "…Looking to apply these technical and operational skills to the management of machine learning systems." Grader: "Mentions management of machine learning systems, which is not present in the original CV summary."
- **BI run 2** (4/5): "…help retail teams track performance and make informed business decisions." Grader flagged "retail teams" / "business decisions". This one is a strict call (it is a goal line, not a claimed skill).
- **Junior DE run 1** (4/5): "…hands-on experience transforming raw operational data into structured reports." Grader: data cleaning/processing phrasing "not explicitly in the source text, though it avoids adding new tools". Also a strict call.

For comparison, Nov 16 B on the same trap: "Python user with an operations background preparing weekly reports. Experienced in cleaning and analyzing data using Pandas and NumPy… Looking for a first role in data analysis."

### Grader consistency check (same calls)

Regrading the Nov 16 answers next to Bm gave A 8/50 (Nov 16: 9) and B 48/50 (Nov 16: 49). c2 did not move for either: A 0/10, B 10/10 in both. B's lost point is c1 on both MLOps runs (the job post does not list Python, the caveat already noted on Nov 16); its DS run 2 c3 point came back.

## What it means

- Sage's test: if Bm invented at A's rate, the one sentence would be doing most of the work. **It didn't.** Bm failed no-invention 4/10 times vs A's 10/10, and it never named a tool from the trap post (A and A80 did every time).
- But the line is not decorative either. Without it, no-invention dropped from 10/10 to 6/10, and the trap became a soft invention: instead of fake tools, the model stretched the framing ("production tasks", "support / management of machine learning systems").
- So most of B's protection comes from the rest of the structure (role, "leave out what the CV lacks", length and format rules), and the explicit "never add anything new" line closes the remaining gap, mostly on the hardest (trap) case.
- Caveats: n = 10 per arm, one run, Gemini not Claude, grader is a Flash/Flash-Lite model (no Pro quota), two of the four c2 fails are strict calls, and the grading group differs from Nov 16 (A, B, Bm instead of A, A80, B).

## Files

- `run_mirror.py` (in the parent folder): the mirror-arm runner (imports `run_eval.py`).
- `summarize_mirror.py` (parent folder): builds the 4-arm tables.
- `mirror_arm/prompt_Bm.txt`: exact Bm prompt template.
- `mirror_arm/raw_outputs_mirror.jsonl`: 10 Bm answers, models, grader JSON, consistency regrades.
- `mirror_arm/results_mirror.json`, `mirror_arm/tables_4arm.md`, `mirror_arm/results_table_4arm.csv`.
- `mirror_arm/stdout.txt`: run log.
