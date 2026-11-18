---
name: cv-tailoring-no-invention
description: Tailor a CV summary to a specific job post without adding any skill or experience the CV doesn't already contain. Use when the user shares a job post and asks to adapt, tailor, or rewrite their CV summary, profile, or "about" text for it.
---

# CV tailoring without invention

Rewrite a CV summary so it fits a job post, using only what is already in the CV.

## Why this skill exists (evidence)
This is the structured prompt from my Prompt Eval Lab, turned into a skill.
- **Prompt Eval Lab (Claude, blinded A/B):** the structured prompt won **47/50 vs 18/50** for the plain prompt.
- **Gemini rerun (Nov 2026), invention check** ("adds nothing not in the CV", 10 answers per arm, including an MLOps trap post asking for tools the CV lacks): structured prompt with the no-invention line **10/10**; the same prompt with only that line removed **6/10**; the plain prompt **0/10**.
- Details: `prompt-eval-lab/` and `prompt-eval-lab/gemini-rerun-2026-11/` in this repo.

## When to use
- A job post plus a CV summary (or full CV), with a request to tailor, adapt or rewrite the summary.

## Inputs
- CV summary (required). If only a full CV is given, use its summary section, or ask which part to tailor.
- Job post (required).
- Word limit (default 80).

## Steps
1. List the job's main requirements.
2. List the skills and experience in the CV summary that match. Use nothing else.
3. Rewrite with these rules (the tested prompt):
   - Lead with the 2-3 CV skills that match the job best.
   - If the job asks for something the CV lacks, leave it out. Do not mention the gap.
   - Use only skills and experience that appear in the CV summary. Never add anything new.
   - Maximum 80 words (or the user's limit), plain language, no buzzwords.
   - Return only the new summary, nothing else.
4. **Self-check before answering:** compare every skill, tool, title and number in the new summary against the CV. Remove anything not in it. Count the words.
5. After the summary, give a short separate note (only if the user wants it) listing job requirements the CV doesn't cover, so the user can decide what to do. Never put those in the summary.

See `references/examples.md` for a sample good summary and a bad invented one (fictional CV, not the user's).

## Output format
- The tailored summary as plain text, ready to paste.
- Optional, below a line: "Not in your CV (left out): ..." and the word count.

## Guardrails
- The no-invention line is mandatory and must stay word for word: "Use only skills and experience that appear in the CV summary. Never add anything new."
- No stretched framing either (for example "supported ML systems" when the CV says nothing about it). If in doubt, leave it out.
- Keep numbers exactly as in the CV.
- Draft only. Never submit an application or send the CV.
