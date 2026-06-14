# SPEC: LeetCode Note Skill

**Topic:** Automated note-taking and pattern-guide generation for LeetCode problems.
**Status:** Refined - Implementation Ready.

## Goal
To streamline the process of summarizing LeetCode discussions into structured personal notes, either as individual problem entries or as holistic pattern-based study guides.

## Core Workflow

### 1. Trigger & Parameters
- **Trigger:** `/leetcode-note [urls...] [mode: template/none]`
- **Parameters:**
    - `urls`: 1 to 5 LeetCode/NeetCode URLs.
    - `template` (Optional): If present, triggers the **Holistic Pattern Note** mode. Default is **Per-Problem Note** mode.

### 2. Context Extraction (Silent Phase)
- **Log Parsing:** Read the current conversation history to extract "Key Takeaways," "Intuition," and "Approach."
- **Consensus Rule:** Takeaways must reflect the *consensus* reached during the `/leetcode-discuss` session. The skill should only proceed if the user achieved a "Strong Hire" or a clear consensus in the discussion.
- **Code Retrieval:** Use the raw code provided by the user in the chat log. **DO NOT** modify logic or add AI-generated comments unless they were part of the finalized chat code block.

### 3. Validation & Mode Check
- **Link Verification:** Before writing, the skill must verify the provided Notion link:
    - **Per-Problem Mode:** Title/ID on the Notion page must match the problem being discussed.
    - **Pattern Mode:** The page topic must match the problem's detected category (e.g., Binary Search).
- **Error Handling:** If there is a mismatch (e.g., DP problem linked to a Binary Search page), return `ERR BAD REQUEST` and ask for the correct link.

### 4. Note Generation Modes

#### Mode A: Per-Problem Note
- **Structure:**
    1.  **Header:** Problem ID and Name.
    2.  **Intuition & Approach:** Summarized from consensus discussion.
    3.  **Complexity:** Big O (Time/Space) from the discussion.
    4.  **Feedback (Conditional):** Include "Interview Feedback" only if the source discussion was in `interview` mode.
    5.  **Code:** Raw user code block.
- **Processing:** Sequential batch processing for up to 5 URLs.

#### Mode B: Holistic Pattern Note (Template)
- **Structure:** Summarizes patterns across multiple problems (e.g., Dijkstra’s philosophy, [L, R) intervals).
- **Update Logic:** **Partial Overwrite**. 
    - Use **Header-Based Parsing** to identify relevant sections (e.g., "Pattern 1: Exact Match").
    - Overwrite only the sections concerned by the current batch of problems.
    - Preserve unrelated sections of the guide.
- **Constraints:** Strict Single Pattern per command. If the batch contains multiple patterns, ask the user to split the request.

### 5. Technical Implementation Details
- **Notion Integration:** Uses Page-Specific URLs provided by the user. 
- **Initialization:** If a page is empty, notify the user. User is responsible for manual page setup.
- **Grouping:** Auto-infer the pattern/group from `web_fetch` (e.g., NeetCode categories) and ask for user confirmation before classification.

## Handover Section
For the implementation session:
1.  Implement a log parser that can identify consensus points in the `leetcode-discuss` conversation.
2.  Set up the Notion API integration to handle both full rewrites (per-problem) and header-based partial updates (holistic).
3.  Add strict validation logic to prevent "Topic Drift" (mode/content mismatch).
4.  Ensure batch processing handles potential API timeouts gracefully without losing state for completed items.
