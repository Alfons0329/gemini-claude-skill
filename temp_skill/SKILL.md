---
name: interview-me
description: Interviews the engineer about a project, ticket, or decision using ask_user until a shared mutual understanding is reached, then writes a structured spec/handover doc. Use when starting a complex task, architectural change, or when you need to align on non-obvious technical tradeoffs.
---

# Interview-Me Skill

Builds shared mutual understanding between an engineer and Gemini CLI before work starts. This skill ensures that non-obvious decisions, constraints, and assumptions are surfaced and documented.

## Core Principles

- **Read Before Asking:** Silently analyze all available context (`MEMORY.md`, `GEMINI.md`, provided docs, related code via `grep_search`) to avoid redundant questions.
- **Technical Focus:** Prioritize technical implementation, tradeoffs, and architectural decisions.
- **Peer Programmer Persona:** Act as a collaborative partner, not just a questionnaire.
- **Structured Alignment:** Use structured rounds (MCQs) and frequent summaries to maintain alignment.

## Workflow

### Step 1: Silent Research
Before asking any questions, build an internal map of what is known vs. unknown.
- Read `MEMORY.md` and `GEMINI.md`.
- Read the initial input spec or ticket.
- Use `web_fetch` for any provided URLs.
- Search the codebase for similar patterns using `grep_search`.

### Step 2: Gap Classification
Classify every missing piece of information:
- `DESIGN_DECISION`: Requires human judgment.
- `CONSTRAINT`: External limits or requirements.
- `NON_OBVIOUS`: Technical nuances that would surprise a new contributor.

### Step 3: Structured Interview
Ask questions in rounds using `ask_user`.
- **Limit:** Max 4 questions per round.
- **Format:** Prefer multiple-choice options (`options` field) to speed up response time.
- **Labeling:** Prepend the classification to each question (e.g., `[DESIGN_DECISION] How should we handle retry logic?`).
- **Defaults:** If the user is unsure, propose a reasonable technical default based on project conventions.

### Step 4: Frequent Summaries
After each round, summarize what has been resolved and what is still open. This confirms the agent's understanding before proceeding.

### Step 5: Final Documentation
Write a structured `SPEC.md` (or user-specified file) containing:
- **Topic & Status**
- **Resolved Decisions** (with rationale)
- **Implementation Notes**
- **Handover Section:** Clear instructions for the next session to begin implementation.
- **Open Items:** Any questions marked for later or unanswered due to a "stop" signal.

## Termination
Respect any "stop", "start", or "go" signals immediately. Do not ask further questions; instead, move straight to Step 5, marking all pending questions as "Open Items".

## Integration
Detect if other installed skills (e.g., `skill-creator`, `database-expert`) are relevant to the topic and suggest using them during the implementation phase.
