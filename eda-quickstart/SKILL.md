---
name: eda-quickstart
description: Run a quick, explained exploratory data analysis on a new dataset (shape, types, missing values, distributions, target balance, correlations, leakage risks) and suggest the next modeling steps. Use when the user shares a CSV, dataframe or Kaggle or bootcamp dataset and asks to explore, understand, clean or start working on it.
---

# EDA quickstart

A first look at a dataset that is fast, reproducible and explained, so the next step is obvious.

## When to use
- A new CSV or dataframe, a bootcamp exercise dataset, or "what's in this data?" before modeling.

## Inputs
- The file path or dataframe, and the target column if there is one (ask if it's a modeling task).
- The goal: description only, classification, regression or clustering.

## Steps
1. **Load and describe**: shape, dtypes, `head()`, memory. Note ID-like and date columns.
2. **Data quality**: missing values per column (count and %), duplicates, constant columns, obviously wrong values (negative ages, impossible dates).
3. **Univariate**: numeric summaries and histograms; top categories for categoricals; flag skew and outliers.
4. **Target**: class balance or target distribution. Say what metric that implies (for example F1 or PR-AUC when classes are imbalanced).
5. **Relationships**: correlations with the target, strongest pairs, and a few grouped means for categoricals.
6. **Leakage check**: columns that wouldn't be known at prediction time, or that encode the target.
7. **Next steps**: cleaning plan, encoding and scaling choices, a baseline model and how to split (stratified, by time, by group).

## Output format
Runnable code cells (pandas, matplotlib or seaborn), each with a markdown cell above it saying what it checks and why, then a short findings list with the real numbers from the output.

## Guardrails
- Report only numbers the code actually printed. Never guess a value.
- Don't drop rows or columns without saying how many and why.
- Keep file paths relative so the notebook runs in Colab and locally. No API keys in cells.
