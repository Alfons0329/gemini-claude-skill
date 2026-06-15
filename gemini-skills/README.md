# Gemini CLI Skills

A collection of specialized agent skills for the [Gemini CLI](https://github.com/google/gemini-cli) to assist with technical alignment, interview preparation, and competitive programming.

## Available Skills

| Skill | Description |
| :--- | :--- |
| **Interview-Me** | Builds shared understanding between an engineer and Gemini CLI before work starts. Surfaces non-obvious decisions, constraints, and assumptions. |
| **LeetCode Discuss** | Interactive Socratic tutor or Google-style interviewer for competitive programming problems. |
| **LeetCode Note** | Automates the process of saving finalized LeetCode insights into Notion or local markdown files. |
| **Resume-JD Interview** | Simulates a high-pressure interview with a Hiring Manager tailored to a specific resume and job description. |
| **System Design Interview** | FAANG-style architectural interview for Staff-level roles, focusing on scalability and domain-specific tradeoffs. |

## Installation

These skills are distributed as `.skill` files, which are packaged zip archives. You can install them using the `gemini skills install` command.

### 1. Prerequisite
Ensure you have the [Gemini CLI](https://github.com/google/gemini-cli) installed and configured on your system (Mac or Linux).

### 2. Install Skills
To install a skill globally (user scope), run the following command in your terminal:

```bash
gemini skills install <path_to_skill_file>.skill
```

To install it for the current workspace only:

```bash
gemini skills install <path_to_skill_file>.skill --scope workspace
```

### 3. Activate Skills
If you are already in an active Gemini CLI session, reload the skills registry to activate the newly installed skills:

```text
/skills reload
```

## Listing and Managing Skills
You can view all installed skills using the following commands:

*   **Terminal:** `gemini skills list`
*   **Interactive Session:** `/skills list`
