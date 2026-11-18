# Claude Skills

Reusable [Claude Skills](https://agentskills.io/home): small folders with a `SKILL.md` file of instructions that Claude loads on its own whenever a task matches the skill's description.

## Skills

| Skill | What it does |
|---|---|
| [crypto-whitepaper-summary](crypto-whitepaper-summary/SKILL.md) | Turns any crypto whitepaper into a one-page research note: what it is, how it works, token model, team and backers, risks, and a verdict. Uses only facts from the document and writes "not stated" when something is missing. |
| [bootcamp-notebook-explainer](bootcamp-notebook-explainer/SKILL.md) | Explains a bootcamp notebook so you understand its structure: big picture, section map, cell-by-cell walkthrough, data flow, key ideas, real results, and 3 check questions. |
| [verified-social-reply](verified-social-reply/SKILL.md) | Drafts a short X or LinkedIn reply after checking every fact against the source. Skips when the facts can't be confirmed. Draft only. |
| [medium-article-from-repo](medium-article-from-repo/SKILL.md) | Turns a repo into a draft Medium article: result first, how it was built, what didn't work, and a table of every number with its source file. |
| [cv-tailoring-no-invention](cv-tailoring-no-invention/SKILL.md) | Tailors a CV summary to a job post using only what the CV already says. Built from Prompt Eval Lab: 47/50 vs 18/50, and the no-invention line took the invention check from 6/10 to 10/10. |
| [project-kickoff](project-kickoff/SKILL.md) | Starts any new project (code, research, YouTube, newsletter, startup idea) from one template, then fills in goal, audience, metrics and phases from a short interview. |
| [research-brief](research-brief/SKILL.md) | Researches a question from 5 to 10 sources and writes a one-page brief where every claim has a link, with disagreements and gaps shown. |
| [youtube-video-to-notes](youtube-video-to-notes/SKILL.md) | Turns a YouTube video into timestamped notes: key points, tools mentioned, steps to copy, and what to verify. |
| [eda-quickstart](eda-quickstart/SKILL.md) | A fast, explained first look at a new dataset: quality, distributions, target balance, correlations, leakage risks and next steps. |
| [model-router](model-router/SKILL.md) | Picks the right tool and model for the task (Claude Code, Codex CLI, or Gemini CLI), shows how to switch models, save usage, and hand work between tools. |

## Prompt Eval Lab

[Prompt Eval Lab](prompt-eval-lab/index.html) is a single-page tool for A/B testing two versions of a prompt. It runs both on the same test cases, has Claude grade every answer against a pass/fail rubric without knowing which version wrote it, and shows which prompt won. Word limits are counted by code, not judged by the model.

My result: on a "tailor my CV summary to a job post" task, the structured prompt won 47/50 vs 18/50 for the plain prompt.

Follow-up: a separate Gemini rerun with four prompt arms (plain, plain plus a word limit, structured, and structured without its no-invention rule) is in [gemini-rerun-2026-11](prompt-eval-lab/gemini-rerun-2026-11/).

The eval runs through Claude's artifact runtime, so it needs to be opened as a Claude artifact. Opened anywhere else, the page loads and can be edited, but the Run button stays off.

## How to use

1. Download the skill folder (or zip it).
2. In Claude, open Settings, find Skills, and upload the zipped folder.
3. Use it as usual (for example, share a whitepaper and ask for a summary). Claude picks up the matching skill automatically.

## How I built this

- For the whitepaper skill, I designed the note structure and the rule that it may only use facts from the document, and must write “not stated” when something is missing. That rule comes from how I used to write research notes: inventing a team or a token metric is worse than leaving a gap.
- I used an AI assistant to help draft and tighten the `SKILL.md` wording. I edited it so the skill stays conservative and does not pad missing facts.
- For Prompt Eval Lab, I set the task, the two prompts, and the pass/fail rubric. Claude graded the answers without being told which prompt wrote them. Word limits are counted by code, not by the model. The structured prompt won 47/50 against 18/50 for the plain prompt, which is a much clearer separation than my later LLM-as-judge test on easy questions.

Not financial advice.

