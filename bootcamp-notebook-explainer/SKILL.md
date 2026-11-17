---
name: bootcamp-notebook-explainer
description: Explain a bootcamp Jupyter notebook or exercise solution so the learner fully understands the code's structure, not just what it outputs. Use when the user shares a notebook, a code cell, or a DI_Bootcamp exercise path and asks to explain it, walk through it, or prepare to submit or present it.
---

# Bootcamp notebook explainer

The goal is understanding. The learner must be able to read, change and defend every line, so explain the structure first and the details second.

## When to use
- A bootcamp notebook (`WeekN/DayM/...ipynb`), an exercise solution, or a single cell is shared with "explain", "walk me through", "what does this do", or "help me understand before I submit".

## Inputs
- The notebook or code (required).
- The exercise text or task, if available. If missing, infer the task from the Markdown cells and say so.
- Which week or day it is, if known, so explanations only use techniques taught by then.

## Steps
1. **Big picture (3 to 5 lines):** what problem the notebook solves, the input data, and the final output or metric.
2. **Structure map:** list the sections in order (imports, load data, clean, split, model, evaluate, conclusions) with the cell numbers for each.
3. **Walk through each section:** for every cell, say what it does, why it is there, and what would break without it. Explain each function or library call the first time it appears (arguments that matter, what it returns, the shape of the data before and after).
4. **Data flow:** trace one variable (for example `X_train`) from creation to final use, so the learner sees how the pieces connect.
5. **Key ideas:** name the ML or Python concept behind the tricky parts (for example a Pipeline preventing data leakage, a stratified split, a random seed) in plain words.
6. **Results:** read the real numbers from the outputs. Say what they mean and what their limits are. Never invent or round differently.
7. **Check questions:** end with 3 short questions the learner should be able to answer, with answers hidden below a "Answers" heading.

## Output format
- Headings: Big picture, Structure, Cell by cell, Data flow, Key ideas, Results, Check yourself.
- Short paragraphs and bullets. Code references in backticks with cell numbers.

## Guardrails
- Explain only what the code does. Don't rewrite it unless asked; if a fix is needed, show the smallest change and say why.
- Stay within techniques the course has taught up to that day.
- Only real numbers from the notebook outputs. If outputs are missing, say "not run yet".
- Never commit, push or submit anything. Never print API keys or tokens found in the notebook; point them out so they can be removed.
