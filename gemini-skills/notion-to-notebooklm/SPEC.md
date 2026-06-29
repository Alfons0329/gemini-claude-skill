# SPEC: Notion to NotebookLM Skill

**Topic:** Put Notion pages (and subpages) into NotebookLM-friendly format.
**Status:** Ready for Implementation.

## Goals & Background
Extract Notion pages (and their nested subpages) into a unified, NotebookLM-actionable Markdown format. This allows users to easily ingest documentation into NotebookLM for generating audio overviews, study guides, and notes, maximizing productivity for commuting or quick learning.

## Resolved Decisions
1. **Notion Page Traversal Strategy & Breadcrumb Path Naming** `[DESIGN_DECISION]`
   - **Decision:** Recursively traverse parent pages upwards using Notion MCP/API to construct the full breadcrumb path (e.g., `system-design--distributed-system.md` for a page under 'System Design').
   - **Rationale:** Preserves folder-like structure context from Notion without relying on brittle URL slug parsing, allowing clear distinction between pages with duplicate titles.
2. **Handling Nested Subpages & Output Formatting** `[DESIGN_DECISION]`
   - **Decision:** Flatten recursively (DFS) and concatenate the subpage contents as-is. Do not shrink or expand header levels. Simply append the original Markdown representation of each subpage sequentially.
   - **Rationale:** Keeping the Markdown representation unmodified ensures we preserve original formatting structures (tables, lists, headers) exactly as the user authored them.
3. **Human Override Parsing & Exclusions** `[DESIGN_DECISION]`
   - **Decision:** Leverage a quick LLM call in the skill environment (before running the Python script) to parse the `--human-override` instruction and generate a structured list of exclusions/formatting rules to pass to the script.
   - **Rationale:** Natural language overrides (e.g., "Do not export subpage virtual memory") are best interpreted dynamically by an LLM rather than fragile hardcoded regex rules.
4. **Helper Script Tech Stack & Authentication** `[CONSTRAINT]`
   - **Decision:** The helper script will be a Python script stored in `$HOME/code/gemini-claude-skill/shared/scripts`, utilizing the official `notion-client` library, and authenticating via the `NOTION_TOKEN` environment variable.
   - **Rationale:** Standardizing on Python and `notion-client` ensures portability, performance, and compatibility across developer environments, while utilizing standard environment variables for secure authentication.

## Confirmed Constraints
- **Read-Only Access:** The skill and scripts must operate in a strictly read-only mode relative to Notion. They must NOT create, delete, or modify any Notion pages or blocks.
- **Fail Fast:** Surface any Notion API / MCP errors immediately to the user without guessing or attempting silent recovery.
- **Git Tracking:** Only commit `SPEC.md`. Do not track or commit `EXAMPLE.md`.

## Technical Implementation Notes
- **Page ID Extraction:** Parse the Notion URL (e.g., `https://www.notion.so/Distributed-System-330dd15eb37180ca90d4eaf841451f55`) to extract the 32-character hexadecimal UUID at the end of the URL path (e.g., `330dd15eb37180ca90d4eaf841451f55` -> `330dd15e-b371-80ca-90d4-eaf841451f55`).
- **Traversal Flow:**
  1. Retrieve the root page using `API-retrieve-a-page` or page ID API to verify access and get the title.
  2. Perform breadcrumb lookup by recursively fetching parent page info if possible.
  3. Fetch block children of the page using `API-get-block-children`. Find child blocks of type `child_page`.
  4. Recursively fetch each child page's contents unless excluded by the user's `--human-override`.
  5. Fetch page contents as Markdown (utilizing Notion block traversal or `API-retrieve-page-markdown` from Notion MCP).
  6. Output a single concatenated Markdown file to the specified `<output-path>`.
- **Output Filename:** Name in lowercase, breadcrumbs separated by `--`, with spaces replaced by single dashes `-`.

## Handover Section
To begin implementation in the next session:
1. Navigate to the helper script directory [shared/scripts](file:///Users/alfonshwu/code/gemini-claude-skill/shared/scripts).
2. Implement `notion_to_markdown.py` which:
   - Accepts arguments: `<notion-page-url>`, `<output-path>`, and optionally `--exclude` (list of subpage titles or IDs parsed from override).
   - Extracts page ID, fetches blocks, traverses nested pages recursively, and constructs breadcrumbs.
   - Outputs the combined Markdown file to `<output-path>` named in the breadcrumb format (e.g., `system-design--distributed-system.md`).
3. Define the `/notion-to-notebooklm` skill in `gemini-skills/notion-to-notebooklm/SKILL.md` to:
   - Handle argument parsing.
   - Use an LLM call to process `--human-override` into a clean structured list of exclusions.
   - Invoke the Python helper script with the correct parameters.
4. Verify by running local tests with active Notion tokens.

## Open Items
- None. All major decisions and constraints are resolved and aligned.
