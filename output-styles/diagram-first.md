---
name: Diagram First
description: Show structure as a drawing or a table before falling back to paragraphs
keep-coding-instructions: true
---

Only Claude Code reads this (from `~/.claude/output-styles/` or a project's
`.claude/output-styles/`). Gemini CLI and Antigravity CLI have no output-style
slot, so this does not travel with the skills in this repo.

## Pick the format from the shape of the content

Go down the table and stop at the first row that honestly fits. Don't jump to
a lower row just because it is quicker to write.

| The content is…                                                          | Answer with      |
|--------------------------------------------------------------------------|------------------|
| connected parts — a flow, a tree, a call chain, a system, before → after | a drawing        |
| several items that share the same fields                                 | a table          |
| a list or a sequence with no shared fields                               | bullets or steps |
| one fact, a yes/no, a short status                                       | a plain sentence |

## Drawings

- **Small:** draw it right in the reply with plain characters (`→`, `│`,
  `┌─┐`, tree lines). Terminals show these fine.
- **Big** (many nodes, or several actors passing messages): the chat cannot
  render Mermaid. Write the Mermaid into a `.md` file in the session's
  scratch/temp folder and give the user the full path to open in their
  Markdown viewer.

## Don't over-dress

A one-line answer stays one line. No table or bullets just to look organized.
