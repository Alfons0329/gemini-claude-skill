# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code), Gemini CLI, Antigravity CLI, and other AI coding agents when working with code in this repository.

## What this repo is

A personal collection of agent **skills** — packaged prompt/workflow definitions, not application code. There is no build, lint, or test suite; the deliverable for each skill is Markdown (plus, for specific skills, helper scripts). Skills are formatted to be **cross-AI-Agent actionable** across Claude Code, Gemini CLI, Antigravity CLI, etc.

## Layout

- `interview/` — interview, algorithm, system design, and role preparation skills:
  - `leetcode-discuss/` — competitive programming mock interview / Socratic practice skill.
  - `leetcode-note/` — automated LeetCode discussion & Notion note-taking skill.
  - `leetcode-roadmap/` — batched study roadmap generator for Notion.
  - `resume-jd-interview/` — mock hiring manager interview based on resume & JD.
  - `sys-design-interview/` — Staff-level system design mock interview simulation.
  - `algo-quiz/` — placeholder for algorithm quiz skill.
  - `sys-design-roadmap/` — placeholder for system design roadmap skill.
- `productivity/` — workflow & productivity skills:
  - `writing-skills/` — the authoring standard every other skill here follows. Read it before creating or editing a `SKILL.md`.
  - `harness-eng/` — the AI-assisted ticket pipeline (spec → impl → verify → PR → KB).
  - `interview-me/` — interactive interviewing & spec drafting skill.
  - `notion-to-notebooklm/` — Notion recursive markdown export for NotebookLM & podcast prompts.
  - `update-notion/` — placeholder for Notion sync skill.
- `shared/scripts/` — helper scripts invoked by skills at runtime (e.g., `notion_to_markdown.py`).
- `temp_skill/`, `temp_leetcode/` — staging ground for skill drafts before promotion into `interview/` or `productivity/`.

## Conventions when adding or editing a skill

**`productivity/writing-skills/SKILL.md` is the authoritative standard** — layout, frontmatter, invocation, and pruning. Read it before creating or editing a `SKILL.md`. The rules below are this repository's own additions.

- Every `SKILL.md` starts with YAML frontmatter:
  ```yaml
  ---
  name: <skill-name>          # matches the directory name
  description: <what it does and when to use it>  # used by AI agents for skill discovery
  ---
  ```
- Make all skills **cross-AI-Agent actionable**:
  - Avoid single-agent hardcoded names; use multi-agent tool mappings (e.g., `web_fetch` / `read_url_content` / `WebFetch`, `ask_user` / `ask_question`, `grep_search` / `Grep`).
  - Use repository-relative paths (e.g., `shared/scripts/notion_to_markdown.py`) rather than machine-specific absolute home paths (`/Users/...`).
  - Refer generically to project context files (`CLAUDE.md`, `GEMINI.md`, `MEMORY.md`).
- Document the invocation syntax as a slash command near the top of the workflow (e.g. `/leetcode-discuss [mode] [url/id] [status]`).
- Structure the workflow as numbered phases: Initialization (silent research phase), Execution/Interview phase, and Termination/Summary phase.
- Write `SPEC.md` alongside `SKILL.md` when designing a new skill to record design decisions and rationale.
