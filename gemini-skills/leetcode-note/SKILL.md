---
name: leetcode-note
description: Automated note-taking and pattern-guide generation for LeetCode problems. Summarizes discussions into structured personal notes or holistic pattern-based study guides.
---

# LeetCode Note Skill

Automates the process of saving finalized LeetCode discussions into Notion or local markdown files. This skill ensures your study guides and problem notes stay synchronized with your latest insights.

## Core Workflow

### 1. Trigger
- **Command:** `/leetcode-note [urls...] [mode: template/none]`
- **Validation:** 
  - Ensure 1-5 URLs are provided.
  - If `template` is used, ensure all URLs belong to the same algorithmic pattern (e.g., all are Binary Search).

### 2. Context Extraction (Silent Phase)
- **Log Parsing:** Analyze the conversation history. Look for the "Consensus" or "Strong Hire" conclusion.
- **Data Points:**
  - **Intuition & Approach:** The finalized logic agreed upon.
  - **Complexity:** The agreed-upon Time/Space analysis.
  - **Code:** The raw code block from the user's final correct submission.
  - **Feedback:** Include "Interview Feedback" if the source discussion was in `interview` mode.

### 3. Verification & Mode Check
- **Notion Link:** Ask the user for the Notion link if not already stored or provided.
- **Mismatch Detection:** 
  - Compare the LeetCode problem ID/Title with the Notion page title.
  - If in `template` mode, verify the page topic matches the problem's detected category.
  - Return `ERR BAD REQUEST` if there is a mismatch.

### 4. Note Generation

#### Mode A: Per-Problem Note (Default)
- **Format:**
  - Header: Problem ID & Name
  - Body: Intuition, Approach, Complexity, Feedback (optional), and Code.
- **Action:** Full rewrite or append to the target page.

#### Mode B: Holistic Pattern Note (`template` mode)
- **Logic:** **Partial Overwrite**.
- **Header-Based Parsing:** Identify specific sections (e.g., "Pattern 2: Lower Bound") and update only those relevant to the current discussion.
- **Constraint:** One pattern per command.

### 5. Technical Details
- **External Fetch:** Use `web_fetch` to retrieve official problem details from LeetCode/NeetCode to confirm ID and metadata.
- **State:** Stateless. RELY on the current session's history for takeaways.
- **Code:** Do not modify user logic.

## Summary & Termination
After successfully updating Notion, provide a summary:
1. **Target:** [Notion Page Title]
2. **Updated Sections:** List of sections or problems added.
3. **Next Steps:** Suggest the next pattern to study or review.
