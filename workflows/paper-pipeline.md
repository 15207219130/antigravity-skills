---
description: "Full pipeline for writing an academic paper using the 8-agent system with feedback loops"
---

# Paper Pipeline Workflow

Use this workflow when writing or revising an academic paper. It invokes the multi-agent skill system.

## Prerequisites

Ensure the following skills exist in `.agents/skills/`:
- `paper-coordinator`, `literature-search`, `literature-review`
- `math-modeling`, `programming`, `plotting`
- `academic-writing`, `paper-reviewer`

## How to Use

Tell Antigravity: **"Use the paper pipeline to [your request]"** or reference `/paper-pipeline`.

Antigravity will read `.agents/skills/paper-coordinator/SKILL.md` and follow the coordination protocol.

## Pipeline Stages

### Stage 1: Planning
1. Read the user's request and current paper state
2. Create `paper/.pipeline/plan.md` with task breakdown
3. Present plan to user for approval

### Stage 2: Research (if needed)
// turbo
4. Read `.agents/skills/literature-search/SKILL.md` — search for papers
// turbo
5. Read `.agents/skills/literature-review/SKILL.md` — write review section

### Stage 3: Formulation (if needed)
// turbo
6. Read `.agents/skills/math-modeling/SKILL.md` — formulate game-theoretic models

### Stage 4: Implementation (if needed)
// turbo
7. Read `.agents/skills/programming/SKILL.md` — implement & run experiments
// turbo
8. Read `.agents/skills/plotting/SKILL.md` — create figures

### Stage 5: Writing
// turbo
9. Read `.agents/skills/academic-writing/SKILL.md` — draft sections

### Stage 6: Review
// turbo
10. Read `.agents/skills/paper-reviewer/SKILL.md` — review draft
11. If CRITICAL/MAJOR issues found → go to relevant Stage and repeat
12. If only MINOR issues → fix in-place, then done

### Stage 7: Finalize
// turbo
13. Compile LaTeX: `cd paper && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex`
14. Present final paper to user

## Quick Reference: Slash Commands

| Command | What it does |
|---------|-------------|
| `/paper-pipeline` | Run the full pipeline |
| "Search literature on [topic]" | Triggers Literature Search skill |
| "Formulate the game model" | Triggers Math Modeling skill |
| "Write the method section" | Triggers Academic Writing skill |
| "Review the paper" | Triggers Paper Reviewer skill |
| "Create a figure for [data]" | Triggers Plotting skill |
