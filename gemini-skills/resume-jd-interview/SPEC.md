# SPEC: Resume-JD Interview Skill

**Topic:** Mock interview simulation based on a specific resume and job description.
**Status:** Refined - Implementation Ready.

## Goal
To help candidates prepare for specific roles by simulating a realistic, high-pressure interview with a Hiring Manager. The skill focuses on verifying experience, probing technical depth, and assessing behavioral fit.

## Core Workflow

### 1. Initialization
- **Trigger:** `/resume-interview <resume_path> <jd_url> [mode: technical|behavioral]`
- **Research Phase (Silent):**
    - Agent reads the resume from the provided path (supports PDF, Docx, Text).
    - Agent fetches the JD from the URL using `web_fetch`.
- **JD Confirmation Phase:**
    - Agent summarizes the core "Must Have" skills and requirements.
    - User must confirm: "Yes, this is the role I'm preparing for" before the interview begins.

### 2. Interview Phase
- **Persona:** Hiring Manager (Direct, technical, and detail-oriented).
- **Format:**
    - **Length:** 5 to 7 deep questions.
    - **Progress Tracking:** Every prompt must include a header (e.g., `[Question 3 of 7]`).
    - **Flow:** Topic-to-Topic. The agent asks one main question, receives the answer, and moves to the next topic.
- **Mode-Specific Logic:**
    - **Technical Mode:** Focuses on **Experience Verification** (how you used X), **Depth Verification** (internals/grilling), and **Scenario-Based Testing** (designing solutions for the JD's specific domain).
    - **Behavioral Mode:** Focuses on soft skills and past conflict/resolution using the STAR method.
- **Gap Probing:** If the resume is missing a required skill from the JD, the agent must explicitly ask how the candidate would bridge that gap.

### 3. Termination & Report
- **Exit:** Triggered after the final question or if the user says "stop/end".
- **End-of-Session Report:**
    - **Answer Feedback:** Specific critique of the user's responses.
    - **Resume Optimization Tips:** Actionable suggestions to better align the resume with the specific JD.
    - **Hiring Assessment:** A final rating on a 4-point scale: **Strong Hire**, **Hire**, **Leaning No**, or **No Hire**, with a brief justification.

## Technical Implementation Details
- **Inputs:** Path-based parsing for local resume files; `web_fetch` for external JDs.
- **State:** Tracks question count and the summarized "Must Haves" during the session.
- **Persona:** Professional, rigorous, and observant.

## Handover Section
For the implementation session:
1. Ensure the PDF/Docx parser is correctly integrated to handle various resume formats.
2. Implement the "JD Confirmation" block as a hard gate before the first question.
3. The report generator must store all answers during the session to provide the final summary.
