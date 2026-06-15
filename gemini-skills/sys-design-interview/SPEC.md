# SPEC: System Design Interview Skill

**Topic:** Mock system design interview simulation based on a job description and resume.
**Status:** Finalized - Ready for Implementation.

## Goal
To simulate a high-level Staff Engineer interview focused on architectural scalability, domain-specific constraints, and technical tradeoffs. The skill helps candidates prepare for FAANG-style system design rounds by combining general distributed systems foundations with deep-dives into specific JD requirements.

## Core Workflow

### 1. Initialization
- **Trigger:** `/sys-design-interview <resume_path> <jd_url> [mode: jd-based|general]`
- **Research Phase (Silent):**
    - Read and analyze the candidate's resume from `<resume_path>`.
    - Fetch and analyze the JD from `<jd_url>` using `web_fetch`.
- **Mode-Specific Setup:**
    - **jd-based:** Identify core architectural challenges and domain constraints from the JD.
    - **general:** Identify 3 common system design topics (e.g., URL shortener, Rate Limiter, News Feed) tailored to the level of the role.
- **Confirmation Phase:**
    - **JD/Resume Summary:** Briefly summarize the "Must Have" skills and candidate profile.
    - **Topic Selection:**
        - If `general`: Present a list of 3 tailored system design options for the user to choose from.
        - If `jd-based`: Propose the primary architectural focus (e.g., "Designing the memory subsystem for an NVIDIA SoC") and wait for confirmation.

### 2. Interview Phase
- **Persona:** Staff Engineer (Direct, architectural-focused, explores scalability, availability, reliability, and cost-efficiency).
- **Format:**
    - **Length:** 5 to 7 deep questions.
    - **Progress Tracking:** Every prompt must include a header (e.g., `[Question 2 of 6]`).
    - **Assistance:** Provide **Socratic hints** if the user appears stuck or asks for guidance.
- **Evaluation Strategy (FAANG Best Practice):**
    - **Balanced Approach:** Start with foundational high-level design (capacity estimation, API design). Pivot to "Deep Dives" into specific JD constraints or "Widow-maker" scenarios (e.g., handling 100x traffic spikes, hardware-specific optimizations).

### 3. Termination & Report
- **Exit:** Triggered after the final question or if the user says "stop/end".
- **End-of-Session Report:**
    - **Answer Feedback:** Detailed critique of architectural decisions and tradeoff analysis.
    - **Resume Optimization Tips:** How to better reflect system design experience on the resume for this specific role.
    - **Hiring Assessment:** 4-point scale (**Strong Hire**, **Hire**, **Leaning No**, **No Hire**) with a Staff-level justification.

## Technical Implementation Notes
- **Persona Tone:** Professional, senior, and challenging but collaborative.
- **State Management:** Must track the current question index, the chosen topic, and the user's design choices for the final report.
- **Hint Logic:** Use Socratic questioning to nudge the user toward identifying bottlenecks rather than giving the answer directly.

## Handover Section
For the implementation session:
1. Implement the collaborative topic selection for `general` mode using `ask_user`.
2. Ensure the "Staff Engineer" persona focuses more on "Why" and "Tradeoffs" than "How".
3. The "Deep Dive" logic should specifically target keywords found in the JD (e.g., "low latency", "high throughput", "distributed consensus").
