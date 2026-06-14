# SPEC: Gemini 'interview-me' Skill

**Topic:** Implementation of the `interview-me` skill for Gemini CLI.
**Status:** Complete - Alignment & Implementation Finalized.

## Handover Section
For the next session agent:
1.  Read the `SPEC.md` (this file) and `interview-me/SKILL.md`.
2.  The skill is already installed at the **user scope**.
3.  The user must run `/skills reload` to activate it.
4.  Test the skill by triggering it with a new topic, e.g., "interview me about refactoring update-notion".
5.  Verify that it follows the structured MCQ format and visible gap classification as specified.

## Open Items
- **User Override:** Currently, the `SPEC.md` filename is default. Ensure the skill correctly prompts for or accepts an override path if the user specifies one in the initial command.
- **Advanced Integration:** Further refine the logic for detecting and triggering other skills (Meta-Skill Integration).

## Core Workflow

### 1. Research & Analysis (Silent Phase)
- **Context Loading:** Automatically read `MEMORY.md` and `GEMINI.md` in the workspace.
- **Reference Reading:** Read any spec files or documents provided in the trigger command.
- **External Resources:** If a URL (Jira, Confluence, GitHub) is provided, use `web_fetch` to analyze the content.
- **Deep Codebase Search:** Use `grep_search` and `glob` to find existing patterns, similar implementations, and potential technical conflicts.
- **Gap Classification:** Categorize information gaps:
    - `ALREADY_KNOWN`: Found in existing docs/code.
    - `DERIVABLE`: Follows from project conventions.
    - `DESIGN_DECISION`: Requires human judgment.
    - `CONSTRAINT`: External limits (platform, legal, deadline).
    - `NON_OBVIOUS`: Surprising details for a new reader.

### 2. The Interview (Active Phase)
- **Persona:** Peer Programmer (supportive, collaborative).
- **Format:** Structured rounds of up to 4 multiple-choice questions using `ask_user`.
- **Classification Visibility:** Show the gap classification (e.g., `[DESIGN_DECISION]`) next to each question.
- **Conflict Handling:** Explicitly flag contradictions between user answers and `GEMINI.md` conventions.
- **Uncertainty:** For "I don't know" answers, the agent proposes a reasonable technical default and asks for confirmation.
- **Frequency:** Summarize "what we know so far" after every round to ensure continuous alignment.

### 3. Documentation (Final Phase)
- **Output File:** Defaults to `SPEC.md` in the current directory, unless overridden by the user.
- **Update Mechanism:** Full rewrite using `write_file`.
- **Meta-Skill Integration:** Proactively suggest or trigger other relevant installed skills based on the topic.
- **Stop Signal:** On "stop" or "start" commands, immediately summarize all queued/unanswered questions as "Open Items".

## Document Structure
1.  **Topic & Status**
2.  **Resolved Decisions** (with rationale and classification)
3.  **Confirmed Constraints**
4.  **Technical Implementation Notes**
5.  **Handover Section:** Specific, actionable instructions for a "fresh session" agent to pick up the work.
6.  **Open Items:** Unresolved questions or deferred decisions.

## Technical Implementation (Skill Definition)
- **Name:** `interview-me`
- **Location:** `interview-me/SKILL.md`
- **Tools Used:** `ask_user`, `read_file`, `grep_search`, `glob`, `web_fetch`, `write_file`.
