# Claude Skills

Reusable [Claude Skills](https://agentskills.io/home): small folders with a `SKILL.md` file of instructions that Claude loads on its own whenever a task matches the skill's description.

## Skills

| Skill | What it does |
|---|---|
| [crypto-whitepaper-summary](crypto-whitepaper-summary/SKILL.md) | Turns any crypto whitepaper into a one-page research note: what it is, how it works, token model, team and backers, risks, and a verdict. Uses only facts from the document and writes "not stated" when something is missing. |

## Prompt Eval Lab

[Prompt Eval Lab](prompt-eval-lab/index.html) is a single-page tool for A/B testing two versions of a prompt. It runs both on the same test cases, has Claude grade every answer against a pass/fail rubric without knowing which version wrote it, and shows which prompt won. Word limits are counted by code, not judged by the model.

My result: on a "tailor my CV summary to a job post" task, the structured prompt won 47/50 vs 18/50 for the plain prompt.

The eval runs through Claude's artifact runtime, so it needs to be opened as a Claude artifact. Opened anywhere else, the page loads and can be edited, but the Run button stays off.

## How to use

1. Download the skill folder (or zip it).
2. In Claude, open Settings, find Skills, and upload the zipped folder.
3. Share a whitepaper and ask for a summary. Claude picks up the skill automatically.

## How I built this

- For the whitepaper skill, I designed the note structure and the rule that it may only use facts from the document, and must write “not stated” when something is missing. That rule comes from how I used to write research notes: inventing a team or a token metric is worse than leaving a gap.
- I used an AI assistant to help draft and tighten the `SKILL.md` wording. I edited it so the skill stays conservative and does not pad missing facts.
- For Prompt Eval Lab, I set the task, the two prompts, and the pass/fail rubric. Claude graded the answers without being told which prompt wrote them. Word limits are counted by code, not by the model. The structured prompt won 47/50 against 18/50 for the plain prompt, which is a much clearer separation than my later LLM-as-judge test on easy questions.

Not financial advice.

