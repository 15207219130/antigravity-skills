---
description: "Systematic paper review workflow: verify contributions, math, references, and overall quality"
---

# Paper Review Workflow

Use this workflow to conduct a rigorous self-review of an academic paper draft before submission. The review covers **6 dimensions**, each producing a structured verdict.

## Prerequisites

- A compiled paper draft (e.g., `paper/main.tex`)
- Source code used to generate results (e.g., `src/`)
- Experiment result data (e.g., `results/`)

## How to Use

Tell Antigravity: **"Review my paper using /paper-review"** or reference `/paper-review`.

## Review Output

All findings are written to `paper/.pipeline/review_report.md` with severity tags:
- 🔴 **CRITICAL** — Must fix before submission (factual errors, broken math, fake refs)
- 🟡 **MAJOR** — Strongly recommended fix (overclaimed contributions, missing assumptions)
- 🟢 **MINOR** — Polish items (wording, formatting, style)

---

## Dimension 1: Contribution Verification

**Goal:** Verify that each claimed contribution is genuinely supported by the paper's content.

// turbo
1. Read `paper/main.tex` and extract the numbered contribution list from the Introduction.
2. For each contribution, perform the following checks:
   - **Existence check**: Is there a corresponding section that delivers this contribution? (e.g., "We formulate a Stackelberg game" → Is there a Section with the actual formulation?)
   - **Novelty check**: Does the Literature Review explicitly identify a gap that this contribution fills? Are there statements like "no existing work does X" that support the novelty claim?
   - **Evidence check**: For empirical contributions (e.g., "we show that combined subsidies dominate"), is there a table/figure in the Experiments section with numbers that support this?
   - **Overclaim check**: Does the contribution use superlatives ("first", "novel", "unique") that may not be justified by the evidence presented?
3. Write findings to `paper/.pipeline/review_report.md` under `## 1. Contribution Verification`.

## Dimension 2: Mathematical Correctness

**Goal:** Verify all equations, derivations, and formal definitions for correctness and consistency.

// turbo
4. Read all mathematical content in `main.tex` (equations, definitions, theorems, algorithms).
5. For each equation/block, check:
   - **Notation consistency**: Are all symbols defined in the notation table? Is each symbol used consistently throughout (e.g., $\mathcal{K}$ always means operators)?
   - **Dimensional analysis**: Do units match on both sides of each equation? (e.g., cost in 万元, emissions in kg)
   - **Index consistency**: Are summation indices and set memberships correct? (e.g., $v \notin \mathcal{V}^+$ vs $v \in \mathcal{V}^+$ used in the right places)
   - **Constraint completeness**: Are all constraints from the code present in the formulation? Compare with `src/operator_model.py`.
   - **Objective alignment**: Does the LaTeX objective function match the code implementation? Compare term-by-term with the Gurobi model in `src/operator_model.py` and `src/game_solver.py`.
   - **Definition correctness**: Are formal definitions (Nash equilibrium, Stackelberg equilibrium) mathematically precise?
6. Append findings to `review_report.md` under `## 2. Mathematical Correctness`.

## Dimension 3: Reference / Hallucination Audit

**Goal:** Detect fabricated or hallucinated references that do not exist.

// turbo
7. Extract all `\cite{}` commands and all entries in `references.bib`.
8. For each reference entry:
   - **Existence check**: Use `search_web` to verify the paper exists (search by title + authors).
   - **Attribution check**: Is the cited claim actually made in the referenced paper?
   - **Orphan check**: Are there `.bib` entries that are never `\cite{}`d?
   - **Missing citation check**: Are there uncited factual claims in the text? (e.g., "LEZs have been implemented in over 250 European cities" — needs a source)
9. Append findings to `review_report.md` under `## 3. Reference Audit`.

## Dimension 4: Code–Paper Consistency

**Goal:** Ensure numerical results in the paper exactly match the code output.

// turbo
10. Read `src/results/all_experiments.json` and extract all numerical values.
11. Compare every number in the paper's tables (Tables 2–5) against the JSON data:
    - Emission values, cost values, reduction percentages, subsidy expenditures
    - Rounding: are numbers rounded consistently?
12. Check that parameter values in Table 1 match `src/data_generator.py`.
13. Append findings to `review_report.md` under `## 4. Code–Paper Consistency`.

## Dimension 5: Logical Flow and Narrative

**Goal:** Check that the paper tells a coherent story with no logical gaps.

// turbo
14. Verify the following narrative chain:
    - Introduction gap → Literature Review confirms gap → Model addresses gap → Experiments validate model → Conclusions reflect experiments
15. Check for:
    - **Forward references**: Does the paper promise something it doesn't deliver?
    - **Dangling labels**: Are all `\ref{}` and `\eqref{}` targets defined?
    - **Section transitions**: Does each section end with a bridge to the next?
    - **Assumption coverage**: Are all assumptions (e.g., Assumption 1) justified and referenced later?
16. Append findings to `review_report.md` under `## 5. Logical Flow`.

## Dimension 6: Formatting and Style

**Goal:** Check conformance to journal style and academic writing standards.

// turbo
17. Check:
    - **Journal format**: Does the document class and formatting match the target journal (e.g., `elsarticle`)?
    - **Table/Figure numbering**: Are all tables and figures numbered sequentially and referenced in the text?
    - **Equation numbering**: Are important equations numbered? Are trivial inline equations unnecessarily numbered?
    - **Consistent terminology**: Is the same concept always referred to by the same term?
    - **Tense consistency**: Past tense for results, present for general truths
    - **Abstract completeness**: Does the abstract contain: problem, method, key result, implication?
18. Append findings to `review_report.md` under `## 6. Formatting and Style`.

---

## Final Verdict

// turbo
19. Count findings by severity: CRITICAL / MAJOR / MINOR.
20. Write a `## Summary` section at the top of `review_report.md` with:
    - Total counts by severity
    - Overall recommendation: **REVISE** (if any CRITICAL), **POLISH** (if MAJOR only), **READY** (if MINOR only)
    - Top 3 priority items to fix
21. Present `review_report.md` to the user for review.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/paper-review` | Full 6-dimension review |
| "Check my math" | Dimension 2 only |
| "Audit references" | Dimension 3 only |
| "Verify contributions" | Dimension 1 only |
| "Check code-paper alignment" | Dimension 4 only |
