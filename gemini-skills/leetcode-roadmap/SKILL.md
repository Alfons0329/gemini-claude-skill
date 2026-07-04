---
name: leetcode-roadmap
description: Automated study roadmap and batch-classification page generator for LeetCode/NeetCode topics. Organizes problem sets into sequential study batches on Notion parent pages.
---

# LeetCode Roadmap Skill

Automates the process of generating structured, batched study roadmaps on parent topic pages in Notion, populated with direct database page links, topic-level applicability checklists, and standard references.

## Core Workflow

### 1. Trigger
- **Command:** `/leetcode-roadmap <problem_set_source> <notion_parent_page>`
- **Validation:** 
  - Ensure a valid webpage URL or local file path is provided as the problem set source.
  - Ensure a valid Notion parent page URL or ID is provided.

### 2. Extraction Phase (Silent Phase)
- **Web scraping / Local reading:** Retrieve problem numbers, titles, difficulties, and sub-topics from the source.
- **Database Query:** Query the parent page's inline database to identify existing page references and match them with extracted problems.

### 3. Database Updates
- For any extracted problem that is missing from the database, create a new row page inside the database.
- Properties to set:
  - `Title`: Problem ID & Name (e.g. `206. Reverse Linked List`)
  - `Difficulty`: `Easy` / `Medium` / `Hard`
  - `Series`: `Neet150` / `Grind75` (if inferred)
  - `Skills`: Consolidate the main topic name and the specific sub-topic (e.g. `["Binary Tree", "Prerequisites"]`).

### 4. Batch Classification Rules
Sort the problems into 3 to 5 logical study batches that flow sequentially from easiest/foundational to advanced/hard.
- **Batch 1: Prerequisites & Basic Traversals:** Core traversals, inversions, or simple transformations (primarily Easy problems).
- **Batches 2-3: Core Sub-patterns & Mid-level CRUD:** Sub-topics grouped by algorithmic variants (e.g. Fixed-Size vs. Variable-Size window, DFS vs. BFS, tree search/insertion/deletion).
- **Batch 4-5: Cache Designs & Advanced/Hard Manipulations:** Hard problems, design questions, complex structures (deques, DP, serialization, recursion with edge-case splicing).

### 5. Parent Page Re-generation
Reconstruct the markdown contents of the parent page to follow this exact format:
- **💡 When should I use... Header:** Include a high-level summary of the topic's applicability criteria and an authoritative reference link (e.g., GeeksforGeeks).
- **Inline Database Block:** Insert the `<database ...>Problems</database>` tag.
- **Batched Roadmap:** Display the structured list of batches (e.g. `### 📂 Batch 1: ...`), listing each problem as a markdown checkbox/bullet linked directly to its database row page.

## Summary & Termination
After successfully updating Notion, provide a summary:
1. **Target:** [Notion Parent Page Title]
2. **Created/Located Pages:** Number of database rows successfully matched/created.
3. **Batches Formed:** List of the batch categories created.
4. **Next Steps:** Suggest the first batch of problems to begin practicing.
