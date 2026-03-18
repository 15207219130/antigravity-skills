# Antigravity Skills

Reusable AI agent skills for academic paper writing, designed for the Antigravity coding assistant.

## Skills (8 agents)

| Skill | Description |
|-------|-------------|
| `paper-coordinator` | Orchestrates the multi-agent pipeline |
| `literature-search` | Searches for papers, generates BibTeX |
| `literature-review` | Synthesizes literature into thematic narrative |
| `math-modeling` | Formulates equations, maintains notation |
| `programming` | Implements algorithms, runs experiments |
| `plotting` | Creates publication-quality figures |
| `academic-writing` | Drafts LaTeX sections in formal style |
| `paper-reviewer` | Reviews drafts with structured feedback |

## Workflow

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `paper-pipeline` | `/paper-pipeline` | Full paper writing pipeline with feedback loops |

## Setup on a New Machine

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/antigravity-skills.git ~/.agents

# Link to your project
cd your-project
mkdir -p .agents
ln -sf ~/.agents/skills .agents/skills
ln -sf ~/.agents/workflows .agents/workflows
```
