#!/usr/bin/env python3
"""Build the 4-arm tables (Nov 16 A/A80/B + Nov 17 mirror arm Bm)."""
import json
from pathlib import Path
import run_eval as R
ROOT = R.ROOT; OUT = ROOT / "mirror_arm"
old = {json.loads(l)["record_id"]: json.loads(l) for l in open(ROOT / "raw_outputs.jsonl", encoding="utf-8")}
bm = {json.loads(l)["record_id"]: json.loads(l) for l in open(OUT / "raw_outputs_mirror.jsonl", encoding="utf-8")}
rows = {**old, **bm}
ARMS = ["A", "A80", "B", "Bm"]; KEYS = ["c1", "c2", "c3", "c4", "word_limit"]
tot = {a: 0 for a in ARMS}; pc = {a: {k: 0 for k in KEYS} for a in ARMS}; wc = {a: [] for a in ARMS}
pj = {c["key"]: {a: 0 for a in ARMS} for c in R.CASES}
trap_hits = {a: 0 for a in ARMS}
for c in R.CASES:
    for run in (1, 2):
        for a in ARMS:
            r = rows[f"{c['key']}|{run}|{a}"]
            tot[a] += r["score"]; pj[c["key"]][a] += r["score"]; wc[a].append(r["word_count"])
            for k in KEYS: pc[a][k] += r["checks"][k]["pass"]
            if c["key"] == "mlops-trap" and r.get("trap_string_hits"): trap_hits[a] += 1
# consistency regrade
reg = {a: {"nov16": 0, "nov17": 0, "c2_nov16": 0, "c2_nov17": 0} for a in ("A", "B")}
for r in bm.values():
    for a in ("A", "B"):
        cr = r["consistency_regrade"][a]
        reg[a]["nov16"] += cr["nov16_score"]; reg[a]["nov17"] += cr["score"]
        reg[a]["c2_nov16"] += old[r["record_id"].replace("|Bm", f"|{a}")]["checks"]["c2"]["pass"]
        reg[a]["c2_nov17"] += cr["checks"]["c2"]
summary = {"totals_out_of_50": tot, "per_check_out_of_10": pc, "per_job_out_of_10": pj,
           "word_counts": {a: {"avg": round(sum(wc[a]) / 10, 1), "min": min(wc[a]), "max": max(wc[a]),
                               "over_80": sum(w > 80 for w in wc[a])} for a in ARMS},
           "mlops_trap_answers_naming_a_missing_tool_out_of_2": trap_hits,
           "grader_consistency_regrade_nov17": reg,
           "bm_models": {rid: {"answer": r["answer_model_version"], "grader": r["grader_model_version"]} for rid, r in bm.items()}}
(OUT / "results_mirror.json").write_text(json.dumps(summary, indent=2) + "\n")
lab = {"c1": "Highlights 2+ CV skills the job asks for", "c2": "Adds nothing not in the CV (no-invention)",
       "c3": "Reads naturally, no buzzwords", "c4": "Paste-ready, no notes", "word_limit": "Under 80 words (code count)"}
L = ["| Arm | Score /50 |", "|---|---:|"] + [f"| {a} | {tot[a]}/50 |" for a in ARMS]
L += ["", "| Check (out of 10) | A | A80 | B | Bm (mirror) |", "|---|---:|---:|---:|---:|"]
L += [f"| {k}: {lab[k]} | " + " | ".join(str(pc[a][k]) for a in ARMS) + " |" for k in KEYS]
L += ["", "| Job post (2 runs, /10) | A | A80 | B | Bm |", "|---|---:|---:|---:|---:|"]
L += [f"| {c['name']} | " + " | ".join(str(pj[c['key']][a]) for a in ARMS) + " |" for c in R.CASES]
L += ["", "| Words | A | A80 | B | Bm |", "|---|---:|---:|---:|---:|"]
for s in ("avg", "max", "over_80"):
    L.append(f"| {s} | " + " | ".join(str(summary['word_counts'][a][s]) for a in ARMS) + " |")
(OUT / "tables_4arm.md").write_text("\n".join(L) + "\n")
csv = ["section,item," + ",".join(ARMS), "total,score_out_of_50," + ",".join(str(tot[a]) for a in ARMS)]
csv += [f"per_check,{k}," + ",".join(str(pc[a][k]) for a in ARMS) for k in KEYS]
csv += [f"per_job,{c['key']}," + ",".join(str(pj[c['key']][a]) for a in ARMS) for c in R.CASES]
csv += ["word_count,average," + ",".join(str(summary['word_counts'][a]['avg']) for a in ARMS)]
(OUT / "results_table_4arm.csv").write_text("\n".join(csv) + "\n")
print("\n".join(L)); print(json.dumps({"trap": trap_hits, "regrade": reg}, indent=1))
