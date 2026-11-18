---
name: model-router
description: Choose which tool and model to use for a task, switch models mid-session, conserve usage limits, or hand work between Claude Code, Codex CLI, and Gemini CLI. Use when picking a tool or model, running /model, checking usage, or handing off to another tool.
---

# Model router

Pick the right tool and a model that matches the work. Start cheap, move up if the result is weak, and check the output before trusting it. Exact model names change; `/model` is the source of truth for the signed-in account.

## When to use
- Choosing a tool or model, switching models, checking usage, or handing work to another tool.

## Pick the tool
- **Claude Code:** coding and multi-file repo changes.
- **Codex CLI (ChatGPT):** a second review of code or drafts, and quick scripts.
- **Gemini CLI:** long documents, large inputs, and prompt-eval reruns.
- **ChatGPT, Gemini, or Claude web apps:** second opinions (no repo edits).

## Pick the model

| Task | Tool | Start with |
|---|---|---|
| Everyday coding, multi-file changes | Claude Code | `sonnet` |
| Simple edits, lookups, boilerplate | Claude Code | `haiku` |
| Plan, then implement | Claude Code | `opusplan` (Opus plans, Sonnet executes) |
| Hard debugging or architecture | Claude Code | `opus` (or `fable` for the longest tasks) |
| Second review, PR review, quick scripts | Codex CLI | `gpt-6.2-sol` at default or medium effort |
| Hardest review or cross-service debug | Codex CLI | `gpt-6.2-astra`; raise effort if needed |
| Small, bounded Codex edits | Codex CLI | `gpt-6-luna` at low effort |
| Long docs, large inputs, eval reruns | Gemini CLI | `auto` or `pro`; `flash` or `flash-lite` for simple or high-volume runs |
| Second opinion | ChatGPT, Gemini, or Claude web | the app default; a stronger model if the first answer is weak |

On a Claude Pro sign-in, the account default may be Opus, which uses more included usage than Sonnet. Prefer Sonnet for routine coding. Fable is not a plan default and may require usage credits; check the `/model` picker.

Current families as of this writing: Claude Code aliases resolve to Haiku 5.5, Sonnet 5.5, Opus 5.5, and Fable 5.2 on the Anthropic API. Codex current IDs include `gpt-6.2-sol`, `gpt-6.2-astra`, and `gpt-6-luna`. Gemini aliases are `auto`, `pro`, `flash`, and `flash-lite` (Auto can route to Gemini 3 when offered).

## How to switch
**Claude Code:** `/model` opens the picker (Enter saves the default; `s` applies to this session only). `/model sonnet` (or `haiku`, `opus`, `opusplan`, `fable`) switches immediately. One session: `claude --model sonnet`. Check the current model with `/status`. Set effort with `/effort` or in the `/model` picker (`low`, `medium`, `high`, `xhigh`, `max`; current models default to `medium`).

**Codex CLI:** `/model` chooses the model and reasoning effort; `/reasoning` adjusts effort only. One run: `codex --model gpt-6.2-sol` or `codex -m gpt-6.2-sol`. Optional default in `~/.codex/config.toml`: `model = "gpt-6.2-sol"` and `model_reasoning_effort = "medium"`. Start at the default or `low` / `medium` effort; raise it in `/model` when needed. Higher levels (including Extra High, Max, and Ultra) appear in the picker when the model supports them. Ultra uses subagents; Luna supports up to Max, not Ultra.

**Gemini CLI:** `/model` opens the picker (Auto, Pro, Flash, Flash-Lite, or Manual). One session: `gemini --model pro` or `gemini -m flash`. Aliases: `auto` (default), `pro`, `flash`, `flash-lite`. A `model.name` value in settings or the `GEMINI_MODEL` variable also sets the model; `--model` wins.

## Save usage
- Match the model to the job. The strongest tier is for hard work, not routine edits.
- `/clear` when starting a new task (all three tools). That is the most effective saving.
- Mid-task, free context with `/compact` in Claude Code and Codex, or `/compress` in Gemini CLI.
- Check context and usage: Claude Code `/context` and `/usage` (or `/cost` on API billing); Codex `/status` and `/usage`; Gemini `/stats` or `/stats model`.
- Point at file paths instead of pasting large files. Keep prompts short. Prefer a skill over a long instruction file.
- For a large change, plan first (`/plan`, or `/model opusplan` in Claude Code), then execute.

## Hand off
When work should continue in another tool:
1. Run `/handoff` (writes `memory/handoff.md`, or `HANDOFF.md` in the project root).
2. Start the other tool in the same project folder.
3. Run `/prime` so it reads only the project file, the todo list, the handoff, and recent git state.

Do not paste the whole previous transcript. The handoff is the context.

## When to escalate
Start on the cheaper or default row in the table. Move up one step (a stronger model, or higher effort) only if the result is weak, incomplete, or wrong. Don't jump to the top tier first. After a successful hard task, switch back down for the next routine one.

## Guardrails
- Treat `/model` as the source of truth. Don't assume a model ID still exists.
- Check output from any tool before trusting it. Use a second tool for a review when the change is important.
- No secrets or keys in handoffs, prompts, or settings examples.

## Sources
- Claude Code models, aliases, `/model`, `/effort`: [Model configuration](https://code.claude.com/docs/en/model-config) and [Help Center model IDs](https://support.claude.com/en/articles/11940350-claude-code-model-configuration)
- Claude Code usage, `/clear`, `/compact`: [Models, usage, and limits](https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code)
- Claude Code `/context`, `/usage`, `/cost`: [Commands](https://code.claude.com/docs/en/commands) and [Manage costs](https://code.claude.com/docs/en/costs)
- Codex models, `/model`, effort: [Models](https://learn.chatgpt.com/docs/models), [Model selection](https://learn.chatgpt.com/docs/model-selection), and [GPT-6.2 (17 Nov 2026)](https://learn.chatgpt.com/docs/whats-new/gpt-62-astra-sol)
- Codex CLI flags and commands: [CLI reference](https://learn.chatgpt.com/docs/cli/reference.md), [Codex CLI](https://learn.chatgpt.com/docs/codex/cli), [Developer commands](https://learn.chatgpt.com/docs/developer-commands)
- Gemini CLI `/model` and aliases: [Model selection](https://geminicli.com/docs/cli/model/) and [Cheatsheet](https://geminicli.com/docs/cli/cli-reference/)
- Gemini routing and settings: [Model routing](https://geminicli.com/docs/cli/model-routing/)
- Gemini `/clear`, `/compress`, `/stats`: [CLI commands](https://geminicli.com/docs/reference/commands/)
