---
name: interview-me
description: Interviews you with multiple-choice rounds until a shared mental model is reached, then writes a structured spec a fresh session can implement from. Reads all available context first and asks only about what is genuinely open — never about what is already written down or derivable. Project-independent: works for any team, codebase, or domain, and reads conventions from the repo rather than assuming them. Trigger with "interview me about X", "let's align on Y", "close the open questions in <file>", or /interview-me <file-or-topic>.
allowed-tools: AskUserQuestion, Read, Glob, Grep, Bash, Write, Edit
---

# Interview-Me

Builds shared understanding between you and Claude *before* implementation starts, then commits it to a document the next session can act on cold.

**The core idea** (from [Thariq's spec workflow](https://x.com/trq212)): start with as little as one sentence. Claude interviews you with probing questions. After enough rounds you have a precise spec *you* shaped — not one Claude invented.

**Why it matters:** most friction on long tasks comes not from a missing spec but from unaligned mental models about non-obvious decisions. This forces alignment before code exists, when changing your mind is still free.

---

## When to use

Use when genuine ambiguity exists — where different people would make different choices:

- Starting a complex ticket: architectural change, multi-file refactor, a big technical decision
- Closing named open questions in an existing spec
- Cross-functional work where assumptions need to be explicit
- Onboarding to an unfamiliar system
- Any time a previous session made choices you would not have made

**Do not use when the work is already fully specified:** one-line edits, renames, config bumps, single-file scripts with no design decisions, or anything where the answer is already in the code and just needs reading.

> **Rule of thumb:** if you could hand the task to three engineers and expect three identical results, skip this skill. If you'd expect three different results, use it.

---

## Inputs

| Input | Required | Example |
|---|---|---|
| Topic, ticket, or file to work from (`$ARGUMENTS`) | Yes | `productivity/loop-eng/SPEC.md`, `"refactor the auth layer"` |
| Output path | No — defaults to writing back into the input file, or `{topic}-spec.md` if the input was a bare topic | `docs/auth-refactor-spec.md` |

---

## Workflow

### Step 1 — Read everything first, silently

Before asking a single question:

- Read the input file or spec passed as `$ARGUMENTS`
- Read `CLAUDE.md` in the working repo — build/test commands, branch and commit conventions, house patterns
- `Glob`/`Grep` the codebase for existing patterns the work would touch or should reuse
- Fetch any URL provided

Build an internal map of **what is already known** vs **what is genuinely open**.

> The interview's quality is decided here. A question about something already written down is a wasted round and signals Claude didn't prepare.

**Never embed conventions in this skill.** Test order, branch naming, commit format, and framework choices are *read from the repo at runtime* and recorded under "Pre-filled context" — never assumed. This is what keeps the skill portable across employers and projects.

### Step 2 — Classify every gap

| Class | Meaning | Becomes a question? |
|---|---|---|
| `ALREADY_KNOWN` | Stated in the spec, `CLAUDE.md`, or a provided doc | **No** — pre-fill silently |
| `DERIVABLE` | Follows from existing conventions or code | **No** — state the assumption, confirm once in bulk |
| `DESIGN_DECISION` | Needs human judgment; different people would choose differently | **Yes** |
| `CONSTRAINT` | External limit — deadline, platform, legal, another team's API | **Yes** |
| `NON_OBVIOUS` | Would surprise a competent reader unfamiliar with this system | **Yes** |

The first two classes exist to *suppress* questions. They matter as much as the three that generate them.

### Step 3 — Interview in rounds with AskUserQuestion

**Format rules:**

- Use `AskUserQuestion` for **every** question — never plain prose the user must compose an answer to
- Up to **4 questions per round**; use all four slots when there are four real gaps
- Always give 2–4 concrete `options`. Reacting to options is far faster than composing an answer
- If the source document already proposes a default, make it the **first** option and mark it `(Recommended)`
- Put the *tradeoff* in each option's `description`, so the choice is decidable without re-reading the source
- Prefix each question with its class — `[DESIGN_DECISION]`, `[CONSTRAINT]`, `[NON_OBVIOUS]` — so the user sees why they're being asked
- Priority when there are more gaps than slots: `NON_OBVIOUS` > `DESIGN_DECISION` > `CONSTRAINT`

**Question quality bar:**

| Bad question | Why it's bad | Good version |
|---|---|---|
| "What does this function do?" | Derivable by reading the code | "This is called from two paths — should the new behavior apply to both, or only one?" |
| "Should we write tests?" | Every `CLAUDE.md` answers this | "Testing this needs a live HTTP server — mock it, or spin up the real one in the test?" |
| "What's the goal?" | Already in the ticket | "The ticket says 'improve reliability' — retry logic, circuit breaker, or both?" |
| "Anything else?" | Open-ended catch-all | (ask a specific gap instead) |

**Conflict handling.** If an answer contradicts something in `CLAUDE.md` or an existing convention, say so immediately and ask which wins. Never silently record an answer that breaks a documented rule.

**Stop conditions** — any one ends the interview:

- All `DESIGN_DECISION` and `CONSTRAINT` gaps are resolved
- Two consecutive rounds surface no new gaps
- The user gives any stop signal — "stop", "good enough", "let's go", "start"

### Step 4 — Summarize between rounds

After each round, before the next batch:

```
Resolved so far:
- [decision: chose X, because Y]
- [constraint confirmed: Z]

Still open:
- [gap 1 — next question]
- [gap 2 — next question]
```

This lets misunderstandings get corrected early, before they compound.

### Step 5 — Write the output document

Write using the template in `reference/output-format.md`.

If `$ARGUMENTS` was an existing document, **write resolutions back into it** — each into the section it belongs to, shrinking any "Open Questions" section as items close. Do not create a parallel spec.

The result must be self-contained: a fresh session reading only this file should start implementing without asking anything.

### Step 6 — Report back

```
## Interview complete

Topic: {topic}
Rounds: {N} ({M} questions)
Written to: {path}

Decisions recorded:  {N}
Pre-filled, not asked: {N} facts from existing context
Open items remaining:  {N} (need external input before coding)

Next: start a fresh session, read {path}, implement.
```

---

## Key behaviors

- **Read before asking.** A question answerable from the provided docs is a wasted round.
- **No obvious questions.** If a competent engineer would find the question condescending or already answered, don't ask it.
- **Options over open questions.** Concrete choices, always. Freeform typing is the slow path.
- **Summarize between rounds.** Understanding compounds; confirm before probing deeper.
- **Don't stop early.** If the user defers a `DESIGN_DECISION` with "whatever you think," briefly explain why their judgment is needed and re-ask with options. Their spec, their call.
- **Self-regulate after 3 rounds.** If `DESIGN_DECISION` gaps remain open after three rounds, stop and ask: *"We've covered a lot — continue, or are we aligned enough to start?"* Alignment stops paying once the back-and-forth costs more than the ambiguity.
- **Respect a stop signal instantly.** On "stop" / "good enough" / "let's go" / "start": ask nothing further, write the document with what's been gathered, and mark the rest as open items.
- **Write for a stranger.** The output is read by a future session with no memory of this conversation.
- **Suggest, don't invoke.** If another installed skill fits the implementation phase, name it in the handover — don't run it.
- **Stay project-independent.** Carry no assumptions about language, tracker, or test strategy. Everything specific comes from the repo or from the user.

---

## Output files

| File | Purpose |
|---|---|
| The input document, updated in place | Resolutions folded into their sections; open-question list shrinks |
| `{topic}-spec.md` | Used only when the input was a bare topic rather than a file |
