# Gemini & Claude AI Agent Skills

A collection of cross-AI-Agent skills compatible with **Claude Code**, **Gemini CLI**, **Antigravity CLI**, and other AI assistant platforms.

## Getting started

**1. Read [`onboard-checklist.md`](onboard-checklist.md).** It is the manual for
using these skills at any company: where each kind of `CLAUDE.md` goes, what
belongs in each one, how to ramp on a codebase you have never seen, and the
gotchas that cost time the first few times.

**2. Install:**

```bash
git clone https://github.com/Alfons0329/gemini-claude-skill.git ~/skills
cd ~/skills
./setup.sh
```

Then restart your agent session — skills are loaded at startup.

`./setup.sh --dry-run` prints what it would do and changes nothing; run that
first on a machine you do not own. `./setup.sh --all` installs the interview
prep skills too. The script is idempotent — safe to re-run any time.

## Repository Structure

```
├── interview/                  # Interview & competitive coding skills
│   ├── leetcode-discuss/       # Socratic tutor & Google-style mock interviews
│   ├── leetcode-note/          # Automated LeetCode note sync to Notion
│   ├── leetcode-roadmap/       # Batched study roadmap generator
│   ├── resume-jd-interview/    # Hiring manager mock interview (Resume + JD)
│   ├── sys-design-interview/   # Staff-level system design simulation
│   ├── algo-quiz/              # Algorithm practice quiz (placeholder)
│   └── sys-design-roadmap/     # System design roadmap (placeholder)
│
├── productivity/               # Workflow & content automation skills
│   ├── loop-eng/               # The ticket pipeline: spec -> impl -> verify -> PR -> KB
│   ├── writing-skills/         # The authoring standard every skill here follows
│   ├── interview-me/           # Technical alignment & spec drafting
│   ├── notion-to-notebooklm/   # Recursive Notion markdown export & podcast prompt generator
│   └── update-notion/          # Notion updates & sync (placeholder)
│
└── shared/                     # Shared runtime assets
    └── scripts/                # Helper scripts (e.g. notion_to_markdown.py)
```

## Cross-AI-Agent Compatibility

All skills are formatted with standard YAML frontmatter and tool-agnostic workflow instructions, making them directly actionable across:
- **Claude Code** (`claude`)
- **Gemini CLI** (`gemini`)
- **Antigravity CLI** (`agy`)
