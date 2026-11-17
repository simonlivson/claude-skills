---
name: medium-article-from-repo
description: Turn a GitHub repository or project folder into a draft Medium article that leads with the real result, explains how it was built, and says what didn't work. Use when the user asks to write a blog post, Medium article, or write-up about one of their repos or projects.
---

# Medium article from a repo

## When to use
- The user names a repo, a project folder, or a finished bootcamp project and asks for an article or write-up.

## Inputs
- The repo (README, code, results files, notebooks). Required.
- Target reader (default: people learning AI/ML, and hiring managers).
- Any angle or length the user wants (default 700 to 1,000 words).

## Steps
1. **Collect facts from the repo only:** goal, data, method, tools, and every number in READMEs, result files and notebook outputs. Write each number with the file it came from.
2. **Find the honest story:** what the result was, what surprised, what failed or was limited (small sample, ceiling effects, untested cases).
3. **Outline** and show it before drafting long text if the user wants to steer:
   - Title: plain and specific, with the result if there is one.
   - Opening (2 to 3 sentences): the result first, with the number.
   - The problem and why it matters.
   - How it was built: data, method, tools, in steps.
   - Results: a small table or bullets with the exact numbers.
   - What didn't work and the limits.
   - What's next.
   - Link to the repo.
4. **Draft** in the user's voice: short sentences, first person, plain words.
5. **Fact table:** after the draft, list every number and claim with its source file.

## Output format
- Markdown article ready to paste into Medium, then a "Facts used" table (claim, value, source file).

## Guardrails
- Draft only. Never publish, schedule or post a link to it.
- Every number must match the repo exactly. If a number is missing, write "not stated" and flag it for the user.
- Lead with the result, name the tool, the number and the limit. Say what didn't work.
- Don't claim experience the repo doesn't show (for example RAG, SQL, production ML) and don't use "passionate" or "motivated".
- The user rewrites in his own words. The draft is a starting point.
- Never paste API keys, tokens or private data from the repo.
