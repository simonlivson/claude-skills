---
name: project-kickoff
description: Start any new project (software, ML, research, YouTube channel, newsletter, news site, startup idea) from one reusable template, then fill in its goal, audience, metrics and phases by interviewing the user. Use when the user says start, kick off, set up or scaffold a new project or idea.
---

# Project kickoff

One setup for every project, so each one starts organized and every agent (Claude Code, Codex, Gemini CLI) reads the same short instructions.

## When to use
- The user wants to start a new project or idea, or says "kick off this project" inside a fresh project folder.

## Inputs
- Project name and type: software-ml, research, content-business or startup-validation (ask if unclear).
- Whatever the user already knows about the goal, audience and deadline.

## Steps
1. **Create the folder.** If `~/LLM-Instructions/new-project.ps1` exists, give the user the exact command to run (`-Name <name> -Flavor <type>`) or run it if allowed. If the folder already exists with a PROJECT.md, skip to step 2. With no template available, create only: AGENTS.md, CLAUDE.md (`@AGENTS.md`), GEMINI.md (`@./AGENTS.md`), PROJECT.md, tasks/todo.md, memory/notes.md, .gitignore with `.env`, .env.example.
2. **Interview, briefly.** Ask at most 6 questions, in one message: goal in one sentence, who it's for, how success is measured (number + date), what's out of scope, deadline, and the first deliverable.
3. **Fill PROJECT.md** sections 1 to 4 from the answers only. Mark anything missing as **[to fill]**. Split the work into 3 to 5 phases, smallest useful version first.
4. **Fill AGENTS.md** Run and Check lines if the project has code; otherwise write "n/a".
5. **Read the flavor note** (`reference/flavor.md`) and add its folders and metrics where they fit.
6. **Log the kickoff** in the PROJECT.md decisions log and put the first 3 tasks in tasks/todo.md.
7. **Stop and show** the filled PROJECT.md. Suggest `/plan-phase 1` as the next step.

## Output format
The filled PROJECT.md, the 3 first tasks, and one line: "Next: /plan-phase 1".

## Guardrails
- Don't invent goals, numbers or audiences. Unknown stays **[to fill]**.
- No commit, push, account sign-up or purchase. Keys go in `.env`, never in a file that is committed.
- Keep AGENTS.md short: only what an agent can't see from the files.
