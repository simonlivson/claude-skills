#!/usr/bin/env python3
"""Mirror arm (Nov 17, 2026): prompt B with ONLY the no-invention rule removed.

Reuses run_eval.py verbatim: same CV, same 5 job posts x 2 runs, same fill(),
same generate() (Gemini API, temperature = API default), same grader prompt,
same /\\S+/ word count, same trap string check.

Arm "Bm" = PROMPT_B minus the single line
  "- Use only skills and experience that appear in the CV summary. Never add anything new."
Everything else in B is unchanged (including "If the job asks for something the CV
lacks, leave it out. Do not mention the gap.").

Model matching: each Bm answer is written by the same answer model that wrote the
Nov 16 B answer for that (job, run), and graded by the same grader model that graded
that (job, run) group on Nov 16.

Grading: blind X/Y/Z in one call per (job, run), with the Nov 16 A and B answers plus
the new Bm answer, shuffled (seed 20261117). Only the Bm grades are new scores; the
fresh A/B grades are stored as a grader-consistency check and do NOT replace the
Nov 16 A/B scores.
"""
from __future__ import annotations
import json, random, sys
from datetime import datetime
from pathlib import Path
import run_eval as R

OUT = R.ROOT / "mirror_arm"
RAW = OUT / "raw_outputs_mirror.jsonl"
NOINV_LINE = "- Use only skills and experience that appear in the CV summary. Never add anything new.\n"
assert NOINV_LINE in R.PROMPT_B
PROMPT_BM = R.PROMPT_B.replace(NOINV_LINE, "")
SEED = 20261117

def main() -> int:
    R.LOG_PATH = OUT / "run_mirror.log"
    old = {}
    for l in open(R.RAW_PATH, encoding="utf-8"):
        r = json.loads(l); old[r["record_id"]] = r
    done = {}
    if RAW.exists():
        for l in open(RAW, encoding="utf-8"):
            r = json.loads(l); done[r["record_id"]] = r
    (OUT / "prompt_Bm.txt").write_text(PROMPT_BM, encoding="utf-8")
    R.log("Mirror arm start; already done: %d" % len(done))
    rng = random.Random(SEED)
    for case in R.CASES:
        for run in range(1, R.RUNS + 1):
            rid = f"{case['key']}|{run}|Bm"
            order = ["A", "B", "Bm"]; rng.shuffle(order)  # draw every time so a resume keeps the same order
            if rid in done and done[rid].get("checks"):
                continue
            b = old[f"{case['key']}|{run}|B"]
            amodel, gmodel = b["answer_model"], b["grader_model"]
            row = done.get(rid)
            if not row:
                prompt = R.fill(PROMPT_BM, R.CV, case["text"], R.MAX_WORDS)
                R.log(f"Writing {rid} with {amodel}...")
                res = R.generate(amodel, prompt)
                wc = R.word_count(res["text"])
                row = {"record_id": rid, "job_key": case["key"], "job_name": case["name"], "run": run, "arm": "Bm",
                       "answer_model": amodel, "answer_model_version": res["model_version"], "text": res["text"],
                       "word_count": wc, "answer_usage": res["usage"], "answer_finish_reason": res["finish_reason"],
                       "trap_string_hits": R.trap_string_check(res["text"]) if case["key"] == "mlops-trap" else []}
                with open(RAW, "a", encoding="utf-8") as f: f.write(json.dumps(row, ensure_ascii=False) + "\n")
                R.log(f"  wrote {rid}: {wc} words")
            texts = {"A": old[f"{case['key']}|{run}|A"]["text"], "B": b["text"], "Bm": row["text"]}
            gp = R.grade_prompt(R.CV, case["text"], R.RUBRIC, *[texts[a] for a in order])
            R.log(f"Grading {case['key']} run {run} as {dict(zip('XYZ', order))} with {gmodel}...")
            res = R.generate(gmodel, gp, json_mode=True)
            payload = R.parse_json_loose(res["text"])
            regrade = {}
            for label, arm in zip("XYZ", order):
                cl = R.parse_grader(payload, label, len(R.RUBRIC))
                wc = R.word_count(texts[arm])
                checks = {f"c{i+1}": cl[i] for i in range(len(R.RUBRIC))}
                checks["word_limit"] = {"pass": wc <= R.MAX_WORDS, "why": f"Counted by code: {wc} words."}
                score = sum(1 for k in checks if checks[k]["pass"])
                regrade[arm] = {"checks": checks, "score": score, "label": label}
            row = dict(row)
            row.update({"grader_model": gmodel, "grader_model_version": res["model_version"],
                        "checks": regrade["Bm"]["checks"], "score": regrade["Bm"]["score"],
                        "grader_label": regrade["Bm"]["label"], "grader_order": order,
                        "grader_raw_json": payload,
                        "consistency_regrade": {a: {"score": regrade[a]["score"],
                                                    "checks": {k: v["pass"] for k, v in regrade[a]["checks"].items()},
                                                    "nov16_score": old[f"{case['key']}|{run}|{a}"]["score"]}
                                                for a in ("A", "B")}})
            done[rid] = row
            with open(RAW, "a", encoding="utf-8") as f: f.write(json.dumps(row, ensure_ascii=False) + "\n")
            R.log(f"  {rid} -> {row['score']}/5 c={[row['checks'][f'c{i+1}']['pass'] for i in range(4)]}")
    # compact
    rows = [done[f"{c['key']}|{r}|Bm"] for c in R.CASES for r in range(1, R.RUNS + 1)]
    with open(RAW, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    R.log("Mirror arm finished at " + datetime.now().astimezone().isoformat(timespec="seconds"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
