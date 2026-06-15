---
name: resume-jd-interview
description: Mock interview simulation based on a specific resume and job description. Use when a user provides a resume and job description (JD) and asks for an interview simulation, interview prep, or to be interviewed for that specific role.
---

# Resume-JD Interview Skill

Simulates a realistic, high-pressure interview with a Hiring Manager focused on a specific job description and candidate resume. The skill assesses technical depth, experience verification, and behavioral fit.

## Core Workflow

### 1. Initialization
- **Trigger:** `/resume-interview <resume_path> <jd_url> [mode: technical|behavioral]`
- **Research Phase (Silent):**
    - Analyze the resume from the provided path.
    - Fetch and analyze the JD from the URL using `web_fetch`.
- **JD Confirmation Phase:**
    - Summarize the core "Must Have" skills and requirements identified from the JD.
    - **Hard Gate:** The user must confirm: "Yes, this is the role I'm preparing for" before the interview begins.

### 2. Interview Phase
- **Persona:** Hiring Manager (Direct, technical, detail-oriented, professional, and observant).
- **Format:**
    - **Length:** 5 to 7 deep questions.
    - **Progress Tracking:** Every prompt must include a header (e.g., `[Question 3 of 7]`).
    - **Flow:** Topic-to-Topic. Ask one main question, receive the answer, and move to the next topic.
- **Mode-Specific Logic:**
    - **Technical Mode:** Focuses on **Experience Verification** (how you used X), **Depth Verification** (internals/grilling), and **Scenario-Based Testing** (designing solutions for the JD's specific domain).
    - **Behavioral Mode:** Focuses on soft skills and past conflict/resolution using the STAR method.
- **Gap Probing:** If the resume is missing a required skill from the JD, explicitly ask how the candidate would bridge that gap.

### 3. Termination & Report
- **Exit:** Triggered after the final question or if the user says "stop/end".
- **End-of-Session Report:**
    - **Answer Feedback:** Provide a specific critique of the user's responses throughout the session.
    - **Resume Optimization Tips:** Offer actionable suggestions to better align the resume with the specific JD.
    - **Hiring Assessment:** Provide a final rating on a 4-point scale: **Strong Hire**, **Hire**, **Leaning No**, or **No Hire**, with a brief justification.
