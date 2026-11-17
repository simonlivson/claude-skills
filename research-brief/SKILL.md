---
name: research-brief
description: Research a question from several sources and write a short brief where every claim has a source link, with conflicts and gaps shown. Use when the user asks to research, investigate, compare, or get up to speed on a topic, market, company, tool or technology.
---

# Research brief

A brief that someone can act on and check. Sources first, conclusions second.

## When to use
- "Research X", "what's the state of Y", "compare A vs B", market or competitor scans, tool choices.

## Inputs
- The question, and the decision it should support (ask if not given).
- Time window (default: last 12 months) and any sources the user trusts or wants excluded.

## Steps
1. **Restate the question** in one sentence and list 3 to 5 sub-questions.
2. **Collect 5 to 10 sources.** Prefer primary sources: official docs, papers, filings, the company's own pages, talks by the people involved. Note the date of each.
3. **Extract claims** per source: one line each, with the link. Keep numbers exactly as written.
4. **Cross-check.** A key claim needs two independent sources or one primary source. Mark single-source claims.
5. **Synthesize** per sub-question. Show where sources disagree instead of picking one silently.
6. **Answer the decision**: recommendation, confidence (high, medium, low) and what would change it.

## Output format
```
Question: ...
Answer (3 lines): ...
Findings:
- <claim> [source](link), date
Disagreements / gaps: ...
Recommendation: ... (confidence: ...)
Sources: numbered list with dates
```
Keep it under one page. Save it to `output/` or `notes/` when working in a project folder.

## Guardrails
- Only claim what a source says. If it isn't found, write "not found" rather than filling the gap.
- Say when a source is old, an opinion, or sponsored.
- Not financial, legal or medical advice.
