---
name: notion-to-notebooklm
description: Extracts Notion pages and subpages recursively to a single concatenated Markdown file ready for NotebookLM.
---

# Notion to NotebookLM Skill

Extracts a Notion page and all of its subpages recursively and saves them as a single concatenated Markdown file. Supports natural language human overrides (e.g., exclusions) by translating them via LLM prior to executing the export.

## Arguments
- `notion-page-url` (required): The Notion page URL or ID to work with.
- `output-path` (required): The path to save the output downloaded data (can be a directory or a specific file name ending in `.md`).
- `--human-override` (optional): Human instructions for customization, e.g. "Do not export subpage virtual memory", "Exclude page X".

## Core Workflow

### Step 1: Argument Validation
- Ensure both `<notion-page-url>` and `<output-path>` are provided.
- If missing, immediately prompt the user for the missing argument(s).

### Step 2: Human Override Translation (LLM Phase)
- If a `--human-override` value is provided, analyze the text to identify any page titles, subpage names, or page IDs that the user wants to exclude or customize.
- Translate the natural language override into a structured, comma-separated list of exclusions.
  - *Example:* `Do not export subpage virtual memory` -> `virtual memory`
  - *Example:* `Exclude pages named OS Review and memory-hierarchy` -> `OS Review,memory-hierarchy`
  - *Example:* If no exclusions are specified or override is empty, the list is empty.

### Step 3: Script Execution
- Locate the Python helper script at [notion_to_markdown.py](shared/scripts/notion_to_markdown.py).
- Build the command line argument list. If exclusions were extracted from the override in Step 2, append `--exclude "<comma-separated-list>"` to the command.
- Execute the script using `run_command` in the workspace directory:
  ```bash
  python3 shared/scripts/notion_to_markdown.py "<notion-page-url>" "<output-path>" [--exclude "<exclusions>"]
  ```
- Ensure the command environment has the `NOTION_TOKEN` environment variable populated.

### Step 4: Error Handling & Output
- If the script execution fails (non-zero exit code), immediately surface the script's stderr output and errors to the user. Do not attempt to guess or modify the results.
- If the script execution succeeds, report the success to the user, displaying the path of the generated markdown file and a summary of pages processed.
