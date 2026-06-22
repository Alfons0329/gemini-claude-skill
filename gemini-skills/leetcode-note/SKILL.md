---
name: leetcode-note
description: Automated note-taking and pattern-guide generation for LeetCode problems. Summarizes discussions into structured personal notes or holistic pattern-based study guides.
---

# LeetCode Note Skill

Automates the process of saving finalized LeetCode discussions directly into Notion. This skill ensures your study guides and problem notes stay synchronized with your latest insights without generating local markdown files in the workspace.

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

#### Formatting Guidelines (Mandatory)
- **Inline Code:** Use `CODE` style (backticks in Markdown, code annotation in Notion) for all variables (e.g., `l`, `m`, `r`), expressions (e.g., `m = l + (r-l)/2`), code snippets (e.g., `nums[m] <= nums[r-1]`), and complexity notations (e.g., `O(log N)`).
- **Bold Headers:** Use bold for section headers within the body (e.g., **Intuition:**, **Complexity:**).
- **Rich Text:** Ensure descriptions are comprehensive and reflect the specific insights from the discussion.
- **Notion-First with Local Fallback:** Attempt to synchronize notes directly to the Notion page. If Notion is inaccessible after a reasonable retry limit (e.g., 3 attempts), write the local `.md` file to the workspace instead. Be sure to provide the local path to the user, and allow them to override it if needed.

#### Mode A: Per-Problem Note (Default)
- **Format:**
  - Header: Problem ID & Name
  - Body: Intuition, Approach, Complexity, Follow-ups (if any), and Code.
- **Action:** Full rewrite or append to the target page.

#### Mode B: Holistic Pattern Note (`template` mode)
- **Logic:** **Partial Overwrite**.
- **Header-Based Parsing:** Identify specific sections (e.g., "Pattern 2: Lower Bound") and update only those relevant to the current discussion.
- **Intuition Section:** Always check for and update the `## 💡 When should I use this algorithmic approach?` section at the top of the page with a clear explanation of the pattern's applicability and an authoritative reference link (e.g., from GeeksforGeeks).
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
