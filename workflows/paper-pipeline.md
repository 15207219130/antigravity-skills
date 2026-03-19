---
description: "Full pipeline for writing an academic paper using the 8-agent system with math verification and feedback loops"
---

# Paper Pipeline Workflow

Use this workflow when writing or revising an academic paper. It invokes the multi-agent skill system.

## Prerequisites

Ensure the following skills exist in `~/.agents/skills/`:
- `paper-coordinator`, `literature-search`, `literature-review`
- `math-modeling`, `math-reviewer`, `programming`, `plotting`
- `academic-writing`, `paper-reviewer`

## How to Use

Tell Antigravity: **"Use the paper pipeline to [your request]"** or reference `/paper-pipeline`.

Antigravity will read `~/.agents/skills/paper-coordinator/SKILL.md` and follow the coordination protocol.

## Pipeline Stages

### Stage 1: Planning
1. Read the user's request and current paper state
2. Create `paper/.pipeline/plan.md` with task breakdown
3. Present plan to user for approval

### Stage 2: Research (if needed)
// turbo
4. Read `~/.agents/skills/literature-search/SKILL.md` — search for papers
// turbo
5. Read `~/.agents/skills/literature-review/SKILL.md` — write review section

### Stage 3: Formulation (if needed)
// turbo
6. Read `~/.agents/skills/math-modeling/SKILL.md` — formulate equations
   - Apply Claim Strength Ladder: classify every formal statement
   - Run Statistical Rigor Checklist for all probabilistic derivations
   - Check Common Pitfalls list before finalizing

### Stage 4: Math Verification
// turbo
7. Read `~/.agents/skills/math-reviewer/SKILL.md` — run 4-panel expert review
   - Panel A: Operations Research & Optimization
   - Panel B: Statistics & Probability
   - Panel C: Machine Learning & Learning Theory
   - Panel D: Stochastic Optimization & Decision Theory
8. If CRITICAL math issues found → return to Stage 3 with specific corrections
9. If MAJOR math issues → fix in-place, re-run affected panels
10. If only MINOR → note for Stage 6

### Stage 5: Implementation (if needed)
// turbo
11. Read `~/.agents/skills/programming/SKILL.md` — implement & run experiments
// turbo
12. Read `~/.agents/skills/plotting/SKILL.md` — create figures

### Stage 6: Writing
// turbo
13. Read `~/.agents/skills/academic-writing/SKILL.md` — draft sections

### Stage 7: General Review
// turbo
14. Read `~/.agents/skills/paper-reviewer/SKILL.md` — review draft
// turbo
15. Read `~/.agents/skills/math-reviewer/SKILL.md` — second math pass on integrated text
16. If CRITICAL/MAJOR issues found → go to relevant Stage and repeat
17. If only MINOR issues → fix in-place, then done

### Stage 8: Finalize
// turbo
18. Compile LaTeX: `cd paper && /Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex && /Library/TeX/texbin/bibtex main && /Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex && /Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex`
19. Present final paper to user

## Quick Reference: Slash Commands

| Command | What it does |
|---------|-------------|
| `/paper-pipeline` | Run the full pipeline |
| "Search literature on [topic]" | Triggers Literature Search skill |
| "Write the method section" | Triggers Academic Writing skill |
| "Review the paper" | Triggers Paper Reviewer skill |
| "Review the math" | Triggers Math Reviewer skill |
| "Create a figure for [data]" | Triggers Plotting skill |
