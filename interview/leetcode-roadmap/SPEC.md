# SPEC: LeetCode Roadmap Skill

**Topic:** Automated study roadmap and batch-classification page generator for LeetCode/NeetCode topics.
**Status:** Refined - Implementation Ready.

## Goal
To automate the generation of structured, batched study roadmaps on parent topic pages in Notion, populated with direct database page links, topic-level applicability checklists, and standard references.

---

## Core Workflow

### 1. Trigger & Parameters
- **Trigger:** `/leetcode-roadmap <problem_set_source> <notion_parent_page>`
- **Parameters:**
    - `problem_set_source`: A webpage URL (e.g. neetcode.io/practice) or a local file path containing list of LeetCode/NeetCode problems.
    - `notion_parent_page`: The Notion page URL or ID of the parent manual page (e.g., the Trees or Linked List main page).

### 2. Problem List Extraction
- **Web Source:** Fetch the page contents and parse to extract problem numbers, titles, difficulties (Easy, Medium, Hard), and topics.
- **Local File Source:** Read the local file contents, parsing lines or markdown checklists to extract problem numbers/titles.

### 3. Database Sync & Page Insertion
1. Retrieve the Notion parent page schema to find the associated inline database (data source ID).
2. Query the data source to see which of the target problems already exist in the database.
3. For any missing problems, create them as new database rows with metadata set:
   - `Title`: Problem ID & Name (e.g., `450. Delete Node in a BST`)
   - `Difficulty`: `Easy` / `Medium` / `Hard`
   - `Series`: `Neet150` / `Grind75` (if inferred)
   - `Skills`: Algorithmic sub-topic tags (e.g. `["Binary Tree", "Prerequisites"]`)
4. Retrieve the full list of database sub-page IDs and direct URLs for all problems.

### 4. Batch-Classification Logic
Group the problems into 3 to 5 logical study batches that flow sequentially from easiest/foundational to advanced/hard. Use the following classification rules:
- **Batch 1: Prerequisites & Basic Traversals:** Core traversals, inversions, or simple transformations (primarily Easy problems).
- **Batches 2-3: Core Sub-patterns & Mid-level CRUD:** Sub-topics grouped by algorithmic variants (e.g. Fixed-Size vs. Variable-Size window, DFS vs. BFS, tree search/insertion/deletion).
- **Batch 4-5: Cache Designs & Advanced/Hard Manipulations:** Hard problems, design questions, complex structures (deques, DP, serialization, recursion with edge-case splicing).

### 5. Parent Page Generation & Partial Overwrite
Rewrite the parent manual page content to fit the standardized layout:
1. **💡 When should I use... Header:** Include a high-level summary of the topic's applicability criteria and an authoritative reference link (e.g., GeeksforGeeks).
2. **Inline Database Block:** Insert the `<database ...>Problems</database>` tag.
3. **Batched Roadmap:** Display the structured list of batches (e.g. `### 📂 Batch 1: ...`), listing each problem as a markdown checkbox/bullet linked directly to its database row page.

---

## Technical Handover Details
1. **Notion Database Interaction:** The skill must fetch and mutate database rows using standard Notion API integrations.
2. **Batch Classification Heuristic:** Build a rule-based tag classifier mapping known LeetCode problem IDs/categories to their sequential batch tiers.
3. **Parent Re-generation:** Overwrite the parent page markdown structure while retaining the database connection and inline block reference.

## Invocation

**User-invoked** (`disable-model-invocation: true`).

This skill rewrites Notion parent pages and mutates database rows. Per the house standard (`productivity/writing-skills/SKILL.md`,
Phase 3), a skill with side effects stays user-invoked: a model that can reach it
on its own can perform those writes without anyone asking for them, and a Notion
page overwritten by accident has no undo the skill can offer.

The flag above is the Claude Code mechanism. On a harness with no equivalent, the
first line of `SKILL.md`'s body states the same intent in prose, so a reader knows
what was meant even where it cannot be enforced.

