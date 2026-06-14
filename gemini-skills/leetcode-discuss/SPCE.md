# SPEC: LeetCode Discuss Skill

**Topic:** Interactive discussion and interview simulation for LeetCode/competitive programming problems.
**Status:** Refined - Implementation Ready.

## Goal
To provide a structured, interactive environment for discussing LeetCode problems, focusing on either deliberate practice (Socratic hints) or mock interview simulation (Google-style assessment).

## Core Workflow

### 1. Initialization
- **Trigger:** `/leetcode-discuss [mode] [url/id] [accepted/rejected]`
- **Modes:** 
    - `practice` (Default): Focuses on identifying errors and providing Socratic hints.
    - `interview`: Simulates a high-stakes technical interview.
- **Problem Context:** The skill fetches problem details from generic URLs (e.g., LeetCode, NeetCode) to establish truth. If the `[accepted/rejected]` flag is missing, the agent must ask for it immediately.

### 2. Practice Mode (The "Target" Flow)
- **Rejected Case:**
    - User provides code + self-analysis.
    - Agent evaluates analysis and implementation.
    - **Hint Strategy:** High-level Socratic hints (Logic -> Pseudo-code). Avoid direct code fixes.
    - Iterative loop until the user achieves "Accepted" status on the platform.
- **Accepted Case:**
    - Agent performs a **Holistic Review**: Correctness, Big O (Time/Space), edge cases, and readability.
    - **Follow-up Phase:** Fixed depth (1 standard follow-up + 1 contextual follow-up).

### 3. Interview Mode (Mock Interview)
- **Phase 1: Clarification (Mandatory):** 
    - Even if the user provides code, the agent **redirects** to a clarification phase.
    - User must ask/answer questions about input specs, constraints, and edge cases.
- **Phase 2: Execution:**
    - User provides the implementation.
    - Agent assesses the "rush to code" vs. "thoughtfulness" balance.
- **Phase 3: Deep Dive:**
    - Evaluation of tradeoffs and complexity.
    - Two follow-up questions (Hybrid: 1 Standard, 1 Contextual).

## Technical Implementation Details
- **Persona:** Google Interviewer (Peer Programmer tone: supportive but rigorous).
- **Feedback Rubric:** Algorithm-centric. While soft on language-specific idioms, it must prioritize clean, efficient, and readable logic.
- **State Management:** Stateless per call. The agent relies on the context provided in the current turn.
- **Mode Switching:** Users can dynamically switch modes mid-discussion (e.g., "Let's switch to interview mode for the follow-ups").

## Document Structure (Output Template)
When the discussion concludes, the agent should summarize:
1.  **Resolved Problem:** ID/Name.
2.  **Key Takeaways:** Specific logic gaps fixed or new patterns learned.
3.  **Interview Feedback:** Assessment of communication, clarification, and technical accuracy.
4.  **Open Items:** Any follow-ups or optimizations deferred by the user.

## Handover Section
For the implementation session:
1.  Create `leetcode-discuss/SKILL.md`.
2.  Implement tool calls for `web_fetch` to handle LeetCode/NeetCode URLs.
3.  Define the Socratic hint logic to ensure it doesn't default to direct code fixes.
4.  Set up the "Interview Mode" state machine to enforce the Clarification Phase before accepting code.
