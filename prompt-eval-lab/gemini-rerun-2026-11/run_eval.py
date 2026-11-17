#!/usr/bin/env python3
"""Rerun of Simon Livson's Prompt Eval Lab with a third arm (A80).

Source of truth: https://github.com/simonlivson/claude-skills/tree/main/prompt-eval-lab
(the EXAMPLE object and gradePrompt() in prompt-eval-lab/index.html).

This is a Python reimplementation, not a Claude-artifact run. Answers and grades
are produced by Gemini, so the scores are a new experiment, not a replication
of the original 47/50 vs 18/50 Claude result.

Arms
----
A    : plain prompt, verbatim from the repo.
A80  : prompt A plus one extra line, 'Maximum 80 words.', and nothing else.
       The line is appended after a blank line so it is not glued to the job post.
B    : structured prompt, verbatim from the repo, with {maxWords}=80.

Protocol
--------
5 job posts x 2 runs x 3 arms = 30 answers.

Grading is blind and in one call per (job post, run): the three answers are
shown to the grader as X, Y and Z in a shuffled order. This is a minimal
adaptation of the original X/Y pairwise grader (which used a coin flip).
Each answer is graded once. The permutation is recorded.

Word limit (80) is counted by code with the same rule as the JS lab:
    len(re.findall(r'\\S+', text.strip()))
which matches (s.trim().match(/\\S+/g) || []).length.

Models
------
Preferred answer model: newest Flash (gemini-3.8-flash, then 3.7, then 3.6).
Preferred grader model: newest Pro (gemini-3.1-pro-preview / gemini-pro-latest).
If a preferred model is unavailable or out of quota, the script falls back to
the nearest working model and records the exact names + versions used.

Temperature is left at the API default (do not set it).
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
import time
import traceback
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RAW_PATH = ROOT / "raw_outputs.jsonl"
RESULTS_JSON = ROOT / "results.json"
RESULTS_MD = ROOT / "results_table.md"
RESULTS_CSV = ROOT / "results_table.csv"
LOG_PATH = ROOT / "run.log"

# ---------------------------------------------------------------------------
# Verbatim materials from prompt-eval-lab/index.html EXAMPLE + gradePrompt()
# ---------------------------------------------------------------------------

TASK = "Tailor my CV summary to a job post"

CV = (
    "Junior data analyst who recently completed a data science course. "
    "Hands-on with Python, Pandas and NumPy for cleaning and analysing data, "
    "and Seaborn and Plotly for charts and dashboards. Previously worked in an "
    "operations role, preparing weekly sales reports. Looking for a first role "
    "in data analysis."
)

CASES = [
    {
        "key": "junior-da",
        "name": "Junior Data Analyst (good match)",
        "text": (
            "Junior Data Analyst, e-commerce startup. Requirements: Python or SQL, "
            "experience cleaning messy data, building dashboards (Plotly, Tableau or similar), "
            "clear communication with non-technical teams. Bootcamp graduates welcome."
        ),
    },
    {
        "key": "bi-retail",
        "name": "BI Analyst, retail (good match)",
        "text": (
            "Business Intelligence Analyst, retail chain. Build weekly sales reports and "
            "dashboards, write SQL queries, present findings to store managers. Nice to have: "
            "Python, Excel automation."
        ),
    },
    {
        "key": "ds-stretch",
        "name": "Data Scientist, 3+ years (stretch)",
        "text": (
            "Data Scientist, 3+ years. Build and deploy machine learning models "
            "(regression, classification), run A/B tests. Python, scikit-learn, SQL. "
            "AWS experience a plus."
        ),
    },
    {
        "key": "junior-de",
        "name": "Junior Data Engineer (neighbor field)",
        "text": (
            "Junior Data Engineer. Build ETL pipelines with Python and SQL, work with "
            "Airflow and Spark, maintain a data warehouse on GCP."
        ),
    },
    {
        "key": "mlops-trap",
        "name": "MLOps Engineer (trap)",
        "text": (
            "MLOps Engineer. Required: Kubernetes, Docker, Terraform, CI/CD for ML models, "
            "2+ years running production ML systems. Java or Go a plus."
        ),
    },
]

RUBRIC = [
    "Highlights at least 2 skills that are in the CV and that the job post asks for",
    "Adds no skill, tool, degree or experience that is not in the CV summary",
    "Reads naturally, without buzzwords or filler phrases",
    "Written in first person or CV style and ready to paste, with no notes or explanations",
]

MAX_WORDS = 80
RUNS = 2

# Prompt A, verbatim from EXAMPLE.pA
PROMPT_A = (
    "Rewrite my CV summary for this job.\n"
    "\n"
    "CV summary:\n"
    "{cv}\n"
    "\n"
    "Job post:\n"
    "{job}"
)

# Prompt A plus one extra line and nothing else.
PROMPT_A80 = PROMPT_A + "\n\nMaximum 80 words."

# Prompt B, verbatim from EXAMPLE.pB
PROMPT_B = (
    "You are a career coach helping a junior candidate apply for jobs.\n"
    "\n"
    "Task: rewrite the CV summary below so it fits the job post.\n"
    "\n"
    "Rules:\n"
    "- Use only skills and experience that appear in the CV summary. Never add anything new.\n"
    "- Lead with the 2-3 CV skills that match the job best.\n"
    "- If the job asks for something the CV lacks, leave it out. Do not mention the gap.\n"
    "- Maximum {maxWords} words, plain language, no buzzwords.\n"
    "- Return only the new summary, nothing else.\n"
    "\n"
    "CV summary:\n"
    "{cv}\n"
    "\n"
    "Job post:\n"
    "{job}"
)

PROMPTS = {"A": PROMPT_A, "A80": PROMPT_A80, "B": PROMPT_B}
ARMS = ["A", "A80", "B"]

# Preferred then fallback. Exact names recorded at runtime.
# Known from pre-run probes on this API key (2026-11-16):
# - gemini-3.8-flash / 3.7-flash: 503 high demand or read timeouts
# - gemini-3.1-pro-preview / gemini-pro-latest: free-tier quota 0
# - gemini-2.5-flash / 2.5-pro: retired for new users
# - gemini-3.6-flash: works (serviceTier=standard)
# Preferred names are still tried first with a short probe, then we fall back quickly.
ANSWER_MODEL_CANDIDATES = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.5-flash-lite",
]
GRADER_MODEL_CANDIDATES = [
    "gemini-3.1-pro-preview",
    "gemini-pro-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
]

# Used when the chosen answer/grader model hits a daily cap mid-run.
FALLBACK_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]

# Tools named in the MLOps trap post (plus common aliases) that are not in the CV.
TRAP_PATTERNS = [
    ("Kubernetes", re.compile(r"\bkubernetes\b|\bk8s\b", re.I)),
    ("Docker", re.compile(r"\bdocker\b", re.I)),
    ("Terraform", re.compile(r"\bterraform\b", re.I)),
    ("CI/CD", re.compile(r"\bci\s*/\s*cd\b|\bcicd\b|\bci-cd\b|\bcontinuous integration\b", re.I)),
    ("Java", re.compile(r"\bjava\b", re.I)),
    ("Go", re.compile(r"\bGolang\b|\bGoLang\b|(?<![A-Za-z])Go(?![A-Za-z])")),
]

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
REQUEST_TIMEOUT = 180
MAX_RETRIES = 12

# Reproducible shuffles; the actual X/Y/Z assignment is also stored per row.
SHUFFLE_SEED = 20261116


def log(msg: str) -> None:
    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def word_count(text: str) -> int:
    """Match the lab: (s.trim().match(/\\S+/g) || []).length"""
    return len(re.findall(r"\S+", text.strip()))


def fill(tpl: str, cv: str, job: str, mw: int) -> str:
    """Match the lab: split/join replacement of {cv}, {job}, {maxWords}."""
    return (
        tpl.replace("{cv}", cv)
        .replace("{job}", job)
        .replace("{maxWords}", str(mw))
    )


def extract_text(resp: dict[str, Any]) -> str:
    texts: list[str] = []
    for cand in resp.get("candidates") or []:
        parts = (cand.get("content") or {}).get("parts") or []
        for part in parts:
            if part.get("thought"):
                continue
            if "text" in part:
                texts.append(part["text"])
    return "".join(texts).strip()


def parse_json_loose(text: str) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise


def api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set")
    return key


class DailyQuotaError(RuntimeError):
    """Free-tier daily quota exhausted; retry wait is many hours."""


def parse_retry_seconds(err_body: str, headers=None) -> float | None:
    """Parse Retry-After header or 'Please retry in 23s' / '1m15s' / '18h17m41s'."""
    if headers:
        ra = headers.get("Retry-After")
        if ra:
            try:
                return float(ra)
            except ValueError:
                pass
    m = re.search(r"Please retry in ([0-9.hms]+)", err_body, re.I)
    if not m:
        return None
    token = m.group(1)
    hours = minutes = seconds = 0.0
    mh = re.search(r"([0-9.]+)h", token)
    mm = re.search(r"([0-9.]+)m", token)
    ms = re.search(r"([0-9.]+)s", token)
    if mh:
        hours = float(mh.group(1))
    if mm:
        minutes = float(mm.group(1))
    if ms:
        seconds = float(ms.group(1))
    total = hours * 3600 + minutes * 60 + seconds
    return total if total > 0 else None


def quota_hint(err_body: str) -> str:
    mets = re.findall(r"metric: ([^,\s]+)", err_body)
    models = re.findall(r"model: ([^,\s]+)", err_body)
    retry = re.search(r"Please retry in ([0-9.hms]+)", err_body, re.I)
    bits = []
    if mets:
        bits.append("metrics=" + ",".join(dict.fromkeys(mets)))
    if models:
        bits.append("models=" + ",".join(dict.fromkeys(models)))
    if retry:
        bits.append("retry_in=" + retry.group(1))
    return "; ".join(bits)


def generate(
    model: str,
    prompt: str,
    *,
    json_mode: bool = False,
    retries: int = MAX_RETRIES,
    timeout: int = REQUEST_TIMEOUT,
) -> dict[str, Any]:
    """Call generateContent. Never logs the API key. Returns {text, raw, model_version, usage}."""
    url = API_URL.format(model=model)
    body: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }
    if json_mode:
        body["generationConfig"] = {"responseMimeType": "application/json"}
    payload = json.dumps(body).encode()
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key(),
    }

    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, data=payload, method="POST", headers=headers)
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = json.loads(resp.read().decode())
            elapsed = time.time() - t0
            text = extract_text(raw)
            finish = None
            cands = raw.get("candidates") or []
            if cands:
                finish = cands[0].get("finishReason")
            if not text:
                raise RuntimeError(f"empty model text (finish={finish})")
            time.sleep(4)
            return {
                "text": text,
                "raw": raw,
                "model": model,
                "model_version": raw.get("modelVersion"),
                "usage": raw.get("usageMetadata"),
                "finish_reason": finish,
                "elapsed_s": round(elapsed, 2),
                "attempts": attempt,
            }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode(errors="replace")
            elapsed = time.time() - t0
            code = e.code
            # Keep a short, key-free error summary.
            try:
                msg = json.loads(err_body)["error"]["message"].split("\n")[0][:300]
            except Exception:
                msg = err_body[:300]
            hint = quota_hint(err_body)
            last_err = RuntimeError(f"HTTP {code} {model}: {msg}" + (f" ({hint})" if hint else ""))
            retryable = code in {408, 429, 500, 502, 503, 504}
            # 404 "no longer available" and hard quota-0 should not be retried many times.
            hard_quota = code == 429 and "limit: 0" in err_body
            parsed = parse_retry_seconds(err_body, e.headers)
            # Daily / long-window quotas are not worth waiting out in this run.
            if parsed is not None and parsed > 15 * 60:
                log(f"  {model}: HTTP {code} long quota wait ({parsed:.0f}s). {hint or msg}")
                raise DailyQuotaError(f"HTTP {code} {model}: daily quota; retry in {parsed:.0f}s. {hint or msg}")
            if hard_quota or code in {400, 401, 403, 404}:
                log(f"  {model}: non-retryable HTTP {code} in {elapsed:.1f}s: {msg} {hint}")
                raise last_err
            if attempt < retries and retryable:
                if parsed is not None:
                    wait = min(max(parsed + 2, 15), 90)
                elif code == 429:
                    wait = min(15 * attempt, 90)
                else:
                    wait = min(2 ** attempt, 45)
                log(f"  {model}: HTTP {code} in {elapsed:.1f}s, retry {attempt}/{retries} after {wait}s: {hint or msg}")
                time.sleep(wait)
                continue
            log(f"  {model}: HTTP {code} failed after {attempt} attempts: {hint or msg}")
            raise last_err
        except Exception as e:
            elapsed = time.time() - t0
            last_err = e
            if attempt < retries:
                wait = min(2 ** attempt, 45)
                log(f"  {model}: {type(e).__name__} in {elapsed:.1f}s, retry {attempt}/{retries} after {wait}s: {e}")
                time.sleep(wait)
                continue
            log(f"  {model}: failed after {attempt} attempts: {type(e).__name__}: {e}")
            raise
    raise last_err or RuntimeError("generate failed")


def pick_model(candidates: list[str], role: str) -> tuple[str, str]:
    """Return (model_id, model_version) for the first candidate that responds."""
    probe = 'Reply with exactly the word PONG and nothing else.'
    errors: list[str] = []
    for name in candidates:
        log(f"Probing {role} model {name}...")
        try:
            # Short probe: don't spend minutes on 503/quota-0 models.
            result = generate(name, probe, retries=1, timeout=45)
            if "PONG" not in result["text"].upper():
                log(f"  unexpected probe text from {name}: {result['text'][:80]!r} (accepting anyway)")
            log(f"  selected {role} model {name} (version={result['model_version']})")
            return name, result["model_version"] or name
        except Exception as e:
            errors.append(f"{name}: {e}")
            log(f"  {name} not usable: {e}")
    raise SystemExit(f"No usable {role} model. Tried: " + " | ".join(errors))


def grade_prompt(cv: str, job: str, crits: list[str], x: str, y: str, z: str) -> str:
    """Original gradePrompt(), extended from X/Y to X/Y/Z with the same wording."""
    listing = "\n".join(f"c{i+1}: {c}" for i, c in enumerate(crits))
    shape = ",".join(
        f'"c{i+1}":{{"pass":true,"why":"one short sentence"}}' for i in range(len(crits))
    )
    return (
        "You are a strict, fair grader for a prompt evaluation. Three candidate outputs, "
        "X, Y and Z, were written for the same task: rewrite a candidate's CV summary to fit a job post.\n"
        "\n"
        "Grade each output on every criterion below, independently. A criterion passes only if it is clearly met. "
        "When checking for invented content, compare every skill, tool, degree and experience in the output against "
        "the original CV summary; anything not there counts as invented, even if the job post asks for it.\n"
        "\n"
        "Original CV summary:\n"
        f'"""{cv}"""\n'
        "\n"
        "Job post:\n"
        f'"""{job}"""\n'
        "\n"
        "Criteria:\n"
        f"{listing}\n"
        "\n"
        "Output X:\n"
        f'"""{x}"""\n'
        "\n"
        "Output Y:\n"
        f'"""{y}"""\n'
        "\n"
        "Output Z:\n"
        f'"""{z}"""\n'
        "\n"
        "Reply with only JSON in this shape:\n"
        f'{{"X":{{{shape}}},"Y":{{{shape}}},"Z":{{{shape}}}}}'
    )


def phrase_window(text: str, match: re.Match[str], window: int = 12) -> str:
    start = max(0, match.start() - 80)
    end = min(len(text), match.end() + 80)
    snippet = text[start:end].strip()
    # Tighten to nearby words.
    words = snippet.split()
    # Fallback to a short slice if messy.
    if len(words) > window * 2:
        # find match text in snippet
        rel = match.start() - start
        # keep ~window words around
        snippet = " ".join(snippet.split())
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


def trap_string_check(text: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for label, pat in TRAP_PATTERNS:
        for m in pat.finditer(text):
            hits.append(
                {
                    "tool": label,
                    "matched": m.group(0),
                    "phrase": phrase_window(text, m),
                }
            )
    return hits


def load_existing() -> dict[str, dict[str, Any]]:
    """Map record_id -> row from an existing jsonl, for resume."""
    rows: dict[str, dict[str, Any]] = {}
    if not RAW_PATH.exists():
        return rows
    with RAW_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            rows[row["record_id"]] = row
    return rows


def append_row(row: dict[str, Any]) -> None:
    with RAW_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_grader(payload: dict[str, Any], label: str, n_crits: int) -> list[dict[str, Any]]:
    block = payload.get(label) or {}
    checks = []
    for i in range(n_crits):
        key = f"c{i+1}"
        c = block.get(key) or {}
        checks.append({"pass": c.get("pass") is True, "why": str(c.get("why") or "")})
    return checks


def summarize(rows: list[dict[str, Any]], meta: dict[str, Any]) -> dict[str, Any]:
    n_per_arm = len(CASES) * RUNS  # 10
    points_per_answer = len(RUBRIC) + 1  # 5
    max_points = n_per_arm * points_per_answer  # 50

    totals = {arm: 0 for arm in ARMS}
    per_check = {arm: {f"c{i+1}": 0 for i in range(len(RUBRIC))} for arm in ARMS}
    for arm in ARMS:
        per_check[arm]["word_limit"] = 0

    word_stats: dict[str, list[int]] = {arm: [] for arm in ARMS}
    per_job: dict[str, dict[str, Any]] = {}
    for case in CASES:
        per_job[case["key"]] = {
            "name": case["name"],
            "scores": {arm: [] for arm in ARMS},
            "totals": {arm: 0 for arm in ARMS},
        }

    trap_findings: list[dict[str, Any]] = []

    by_id = {r["record_id"]: r for r in rows}

    for case in CASES:
        for run in range(1, RUNS + 1):
            for arm in ARMS:
                rid = f"{case['key']}|{run}|{arm}"
                row = by_id.get(rid)
                if not row or not row.get("checks"):
                    continue
                totals[arm] += row["score"]
                word_stats[arm].append(row["word_count"])
                per_job[case["key"]]["scores"][arm].append(row["score"])
                per_job[case["key"]]["totals"][arm] += row["score"]
                for i in range(len(RUBRIC)):
                    if row["checks"][f"c{i+1}"]["pass"]:
                        per_check[arm][f"c{i+1}"] += 1
                if row["checks"]["word_limit"]["pass"]:
                    per_check[arm]["word_limit"] += 1
                if case["key"] == "mlops-trap":
                    trap_findings.append(
                        {
                            "arm": arm,
                            "run": run,
                            "word_count": row["word_count"],
                            "c2_pass": row["checks"]["c2"]["pass"],
                            "c2_why": row["checks"]["c2"]["why"],
                            "score": row["score"],
                            "trap_string_hits": row.get("trap_string_hits") or [],
                            "text": row["text"],
                        }
                    )

    def avg(xs: list[int]) -> float | None:
        return round(sum(xs) / len(xs), 2) if xs else None

    a_over = sum(1 for w in word_stats["A"] if w > MAX_WORDS)
    summary = {
        "meta": meta,
        "max_points": max_points,
        "n_answers_per_arm": n_per_arm,
        "points_per_answer": points_per_answer,
        "totals": {arm: {"score": totals[arm], "out_of": max_points} for arm in ARMS},
        "per_check_out_of": n_per_arm,
        "per_check": per_check,
        "word_counts": {
            arm: {
                "n": len(word_stats[arm]),
                "average": avg(word_stats[arm]),
                "min": min(word_stats[arm]) if word_stats[arm] else None,
                "max": max(word_stats[arm]) if word_stats[arm] else None,
                "over_80": sum(1 for w in word_stats[arm] if w > MAX_WORDS),
                "values": word_stats[arm],
            }
            for arm in ARMS
        },
        "a_answers_over_80": a_over,
        "per_job": per_job,
        "trap_findings": trap_findings,
        "check_labels": {
            "c1": RUBRIC[0],
            "c2": RUBRIC[1],
            "c3": RUBRIC[2],
            "c4": RUBRIC[3],
            "word_limit": f"Under {MAX_WORDS} words (counted by code with /\\S+/)",
        },
    }
    return summary


def render_tables(summary: dict[str, Any]) -> tuple[str, str]:
    arms = ARMS
    max_pts = summary["max_points"]
    n = summary["per_check_out_of"]
    labels = summary["check_labels"]

    md: list[str] = []
    md.append("# Prompt Eval Lab rerun — results")
    md.append("")
    meta = summary["meta"]
    md.append(f"- Answer model: `{meta.get('answer_model')}` (version `{meta.get('answer_model_version')}`)")
    md.append(f"- Grader model: `{meta.get('grader_model')}` (version `{meta.get('grader_model_version')}`)")
    md.append(f"- Protocol: {meta.get('protocol')}")
    md.append(f"- Generated at: {meta.get('finished_at')}")
    md.append("")
    md.append("## Totals (out of 50)")
    md.append("")
    md.append("| Arm | Score |")
    md.append("|---|---:|")
    for arm in arms:
        md.append(f"| {arm} | {summary['totals'][arm]['score']}/{max_pts} |")
    md.append("")
    md.append("## Per-check counts (out of 10)")
    md.append("")
    md.append("| Criterion | A | A80 | B |")
    md.append("|---|---:|---:|---:|")
    for key in ["c1", "c2", "c3", "c4", "word_limit"]:
        cells = " | ".join(f"{summary['per_check'][arm][key]}/{n}" for arm in arms)
        md.append(f"| {key}: {labels[key]} | {cells} |")
    md.append("")
    md.append("## Word counts")
    md.append("")
    md.append("| Arm | n | Average | Min | Max | Over 80 |")
    md.append("|---|---:|---:|---:|---:|---:|")
    for arm in arms:
        w = summary["word_counts"][arm]
        md.append(
            f"| {arm} | {w['n']} | {w['average']} | {w['min']} | {w['max']} | {w['over_80']} |"
        )
    md.append("")
    md.append(f"Prompt A exceeded 80 words on **{summary['a_answers_over_80']}** of {n} answers.")
    md.append("")
    md.append("## Per job post (sum of 2 runs, out of 10 points each)")
    md.append("")
    md.append("| Job post | A | A80 | B |")
    md.append("|---|---:|---:|---:|")
    for case in CASES:
        job = summary["per_job"][case["key"]]
        md.append(
            f"| {job['name']} | {job['totals']['A']}/10 | {job['totals']['A80']}/10 | {job['totals']['B']}/10 |"
        )
    md.append("")
    md.append("## MLOps trap findings")
    md.append("")
    for item in summary["trap_findings"]:
        hits = item["trap_string_hits"]
        hit_s = ", ".join(f"{h['tool']} (“{h['phrase']}”)" for h in hits) if hits else "no tool-name hits"
        md.append(
            f"- **{item['arm']} run {item['run']}** ({item['word_count']} words, "
            f"score {item['score']}/5): c2 {'PASS' if item['c2_pass'] else 'FAIL'} — {item['c2_why']} "
            f"String check: {hit_s}"
        )
        md.append("")
        md.append(f"  > {item['text'].replace(chr(10), ' / ')}")
        md.append("")

    # CSV: per-check plus totals and word stats
    csv_lines = ["section,item,A,A80,B"]
    csv_lines.append(
        "total,score_out_of_50,"
        + ",".join(str(summary["totals"][arm]["score"]) for arm in arms)
    )
    for key in ["c1", "c2", "c3", "c4", "word_limit"]:
        csv_lines.append(
            "per_check,"
            + key
            + ","
            + ",".join(str(summary["per_check"][arm][key]) for arm in arms)
        )
    csv_lines.append(
        "word_count,average,"
        + ",".join(str(summary["word_counts"][arm]["average"]) for arm in arms)
    )
    csv_lines.append(
        "word_count,over_80,"
        + ",".join(str(summary["word_counts"][arm]["over_80"]) for arm in arms)
    )
    for case in CASES:
        job = summary["per_job"][case["key"]]
        csv_lines.append(
            "per_job,"
            + case["key"]
            + ","
            + ",".join(str(job["totals"][arm]) for arm in arms)
        )
    return "\n".join(md) + "\n", "\n".join(csv_lines) + "\n"


def run() -> int:
    LOG_PATH.touch(exist_ok=True)
    log("Starting Prompt Eval Lab rerun")
    existing = load_existing()
    log(f"Already completed rows: {len(existing)}")

    # If we already have all 30 graded rows, just (re)write the tables.
    need_models = any(
        f"{case['key']}|{run}|{arm}" not in existing or not existing[f"{case['key']}|{run}|{arm}"].get("checks")
        for case in CASES
        for run in range(1, RUNS + 1)
        for arm in ARMS
    )

    answer_model = grader_model = None
    answer_ver = grader_ver = None
    if existing:
        # Reuse previously recorded models if present, so a resume stays consistent.
        sample = next(iter(existing.values()))
        answer_model = sample.get("answer_model")
        answer_ver = sample.get("answer_model_version")
        grader_model = sample.get("grader_model")
        grader_ver = sample.get("grader_model_version")

    if need_models:
        if not answer_model:
            answer_model, answer_ver = pick_model(ANSWER_MODEL_CANDIDATES, "answer")
        else:
            log(f"Resuming with answer model {answer_model} (version={answer_ver})")
        if not grader_model:
            # Do not probe models already known to be daily-capped (3.6-flash / Pro).
            try:
                grader_model, grader_ver = pick_model(FALLBACK_MODELS, "grader")
            except SystemExit:
                grader_model, grader_ver = pick_model(GRADER_MODEL_CANDIDATES, "grader")
        else:
            log(f"Resuming with grader model {grader_model} (version={grader_ver})")

    # Cache answers before grading, including ungraded ones already on disk.
    answers: dict[str, dict[str, Any]] = dict(existing)

    # --- Generate missing answers ---
    for case in CASES:
        for run in range(1, RUNS + 1):
            for arm in ARMS:
                rid = f"{case['key']}|{run}|{arm}"
                if rid in answers and answers[rid].get("text"):
                    continue
                prompt = fill(PROMPTS[arm], CV, case["text"], MAX_WORDS)
                log(f"Writing {rid} with {answer_model}...")
                try:
                    result = generate(answer_model, prompt)
                except DailyQuotaError as e:
                    log(f"  {answer_model} hit a daily cap; switching remaining answers to a fallback model. {e}")
                    answer_model, answer_ver = pick_model(
                        [m for m in FALLBACK_MODELS if m != answer_model], "answer-fallback"
                    )
                    result = generate(answer_model, prompt)
                text = result["text"]
                wc = word_count(text)
                row = {
                    "record_id": rid,
                    "job_key": case["key"],
                    "job_name": case["name"],
                    "run": run,
                    "arm": arm,
                    "answer_model": answer_model,
                    "answer_model_version": result["model_version"] or answer_ver,
                    "grader_model": None,
                    "grader_model_version": None,
                    "text": text,
                    "word_count": wc,
                    "word_limit_pass": wc <= MAX_WORDS,
                    "checks": None,
                    "score": None,
                    "grader_label": None,
                    "grader_order": None,
                    "trap_string_hits": trap_string_check(text) if case["key"] == "mlops-trap" else [],
                    "answer_usage": result["usage"],
                    "answer_elapsed_s": result["elapsed_s"],
                    "answer_finish_reason": result["finish_reason"],
                }
                answers[rid] = row
                append_row(row)
                log(f"  wrote {rid}: {wc} words, finish={result['finish_reason']}")

    # --- Grade missing (job, run) groups ---
    rng = random.Random(SHUFFLE_SEED)
    for case in CASES:
        for run in range(1, RUNS + 1):
            group = [answers[f"{case['key']}|{run}|{arm}"] for arm in ARMS]
            if all(r.get("checks") for r in group):
                continue
            order = ARMS[:]
            rng.shuffle(order)  # X, Y, Z assignment
            labels = ["X", "Y", "Z"]
            texts = [answers[f"{case['key']}|{run}|{arm}"]["text"] for arm in order]
            prompt = grade_prompt(CV, case["text"], RUBRIC, texts[0], texts[1], texts[2])
            log(f"Grading {case['key']} run {run} as {dict(zip(labels, order))} with {grader_model}...")
            try:
                result = generate(grader_model, prompt, json_mode=True)
            except DailyQuotaError as e:
                log(f"  {grader_model} hit a daily cap; switching remaining grading to a fallback model. {e}")
                grader_model, grader_ver = pick_model(
                    [m for m in FALLBACK_MODELS if m != grader_model], "grader-fallback"
                )
                result = generate(grader_model, prompt, json_mode=True)
            try:
                payload = parse_json_loose(result["text"])
            except Exception:
                log(f"  grader JSON parse failed, raw starts: {result['text'][:400]!r}")
                raise
            # Rewrite the three rows. Because jsonl is append-only, we will compact later.
            for label, arm in zip(labels, order):
                rid = f"{case['key']}|{run}|{arm}"
                row = dict(answers[rid])
                checks_list = parse_grader(payload, label, len(RUBRIC))
                wc = row["word_count"]
                checks = {
                    f"c{i+1}": checks_list[i] for i in range(len(RUBRIC))
                }
                checks["word_limit"] = {
                    "pass": wc <= MAX_WORDS,
                    "why": f"Counted by code: {wc} words.",
                }
                score = sum(1 for i in range(len(RUBRIC)) if checks[f"c{i+1}"]["pass"])
                score += 1 if checks["word_limit"]["pass"] else 0
                row.update(
                    {
                        "grader_model": grader_model,
                        "grader_model_version": result["model_version"] or grader_ver,
                        "checks": checks,
                        "score": score,
                        "grader_label": label,
                        "grader_order": order,
                        "grader_usage": result["usage"],
                        "grader_elapsed_s": result["elapsed_s"],
                        "grader_raw_json": payload,
                    }
                )
                answers[rid] = row
                append_row(row)
                log(f"  {rid} -> {score}/5  c={[checks[f'c{i+1}']['pass'] for i in range(4)]} words={wc}")

    # Compact jsonl to the latest version of each record_id.
    compact = [answers[f"{case['key']}|{run}|{arm}"] for case in CASES for run in range(1, RUNS + 1) for arm in ARMS]
    with RAW_PATH.open("w", encoding="utf-8") as f:
        for row in compact:
            # Keep grader_raw_json (useful) but drop any huge raw API blob if present.
            row = dict(row)
            row.pop("raw", None)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    finished = datetime.now().astimezone().isoformat(timespec="seconds")
    meta = {
        "answer_model": answer_model or compact[0].get("answer_model"),
        "answer_model_version": answer_ver or compact[0].get("answer_model_version"),
        "grader_model": grader_model or compact[0].get("grader_model"),
        "grader_model_version": grader_ver or compact[0].get("grader_model_version"),
        "protocol": (
            "3 arms (A, A80, B); 5 job posts x 2 runs; blind X/Y/Z grading with shuffled "
            f"order (seed={SHUFFLE_SEED}); word limit counted by /\\S+/; temperature=API default."
        ),
        "source": "https://github.com/simonlivson/claude-skills/tree/main/prompt-eval-lab",
        "finished_at": finished,
        "timezone_note": "timestamps are local to the box (Asia/Jerusalem, UTC+2)",
        "caveats": [
            "Gemini rather than Claude; not a replication of the original 47/50 vs 18/50.",
            "Small n: 10 answers per arm.",
            "Single experiment (no second full rerun).",
            "Grader adapted from X/Y to X/Y/Z with shuffled order.",
        ],
    }
    summary = summarize(compact, meta)
    # Add model-availability caveat if grader is not a Pro model.
    gm = meta["grader_model"] or ""
    if "pro" not in gm:
        summary["meta"]["caveats"].append(
            f"No Pro model was usable on this API key (gemini-3.1-pro-preview / gemini-pro-latest "
            f"had free-tier quota 0; gemini-2.5-pro is retired for new users). Graded with {gm} instead."
        )
    RESULTS_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md, csv = render_tables(summary)
    RESULTS_MD.write_text(md, encoding="utf-8")
    RESULTS_CSV.write_text(csv, encoding="utf-8")
    log(f"Wrote {RAW_PATH}, {RESULTS_JSON}, {RESULTS_MD}, {RESULTS_CSV}")
    print(md)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception:
        log("FATAL:\n" + traceback.format_exc())
        sys.exit(1)
