# Specification: Harness Engineering — Phase 1 (Baseline Ticket Pipeline)

**Status:** Active — build target for this repo.
**Scope:** A single mid-level IC (~5 YoE) working tickets inside an existing codebase at a large company. Not a team-wide rollout, not a config-binding CLI, not cross-session orchestration — that tier is deliberately deferred and this document does not depend on it.

## 1. Why Phase 1 alone is enough at this level

The leverage for an IC at this level is entirely inside one ticket's lifecycle: spec it, implement it, verify it, get it reviewed, ship it, record what was learned. Nothing here requires:
- binding company-specific config dynamically (a "config seam"),
- merging into an existing team's workflow (`merge-harness`),
- managing context across long-running multi-week efforts (`handoff`, `bootcamp`),
- routing ambiguous requests to sub-skills (`harness-router`),
- owning backlog/roadmap ambiguity (`wayfinder`, `triage`).

Those are staff/tech-lead concerns — adopting them now would be building infrastructure for pain not yet felt, which the harness-engineering doctrine itself argues against (decide from a loop, not a hypothesis).

## 2. Attribution

- **`mattpocock/skills`** ([repo](https://github.com/mattpocock/skills), MIT licensed) — the TDD/seams discipline in §4 and the standards/spec code-review axes in §6. See `NOTICE.md`.
- **`dietrichgebert/ponytail`** ([repo](https://github.com/dietrichgebert/ponytail), MIT licensed) — the seven-rung ladder and the `ponytail:` shortcut marker in §4, and the deletion axis in §6.2. See `NOTICE.md`.
- **Everything else is the author's own**, including the session-handoff artifact model (§3.1), the single-skill kernel and the kernel/user-space split (§7.1), the `--human` layer (§7.2), the RCA branch and its three-part output (§3.3), and the failure-triage table (§5.5). These are a from-memory reconstruction of a pipeline the author designed and ran daily for ~3 months, written as generic method only — no employer names, ticket identifiers, repository paths, internal URLs, or domain specifics.

## 2.1 Why this shape, and not a plausible-sounding alternative

Every decision below was run in anger for ~3 months on real tickets before being written down. Two in particular are counterintuitive enough that they'd likely be designed *out* of a from-scratch pipeline, and are here because practice demanded them:

- **`verify` authors the E2E test, not `impl`** (§5.2) — costs an extra cold session; the payoff is that the test can't inherit the implementer's blind spots.
- **A failing test is triaged, never assumed** (§5.5) — the obvious design routes every red test into a code fix, which is precisely how a correct implementation gets edited until it satisfies a typo, or until it satisfies a test that never ran at all.

## 3. Pipeline Overview

```
Story: SPEC ─────────> IMPL ──> VERIFY ──> PR-CREATE ──> PR-REVIEW (security-gated) ──> UPDATE-KB
Bug:   SPEC ──> RCA ──> IMPL ──> VERIFY ──> PR-CREATE ──> PR-REVIEW (security-gated) ──> UPDATE-KB
```

| # | Stage | Stage token | What it does |
|---|---|---|---|
| 1 | SPEC | `spec` | structured interview, produces `<ticket-id>-spec.md` |
| 1b | RCA | `rca` | **bug tickets only** — root-cause + escape analysis before any fix is written (§3.3) |
| 2 | IMPL | `impl` | TDD-disciplined, laziest-solution-first (§4) |
| 3 | VERIFY | `verify` | two-perspective verification + failure triage (§5) |
| 4 | PR-CREATE | `pr-create` | draft `<id>-pr.md`, open the PR from it, print the tracker updates for the operator (Q6) |
| 5 | PR-REVIEW | `pr-review` | security gate, then three-axis review (§6) |
| 6 | UPDATE-KB | `kb-update` | feedback loop writing learnings back to `docs/` |

All seven are stages of **one skill**, not seven skills — see §7.1. Each runs as `/harness-eng <stage> <ticket-id>` (§3.2).

**SEC-SCAN is not a standalone stage.** Security is a gate *inside* `pr-review` (§6), because it needs exactly the artifact that stage already has — the full diff against a fixed point. A separate session would re-derive that same context to check one narrow axis. Its repair path stays named and distinct: `/harness-eng impl <id> fix-sec` (§5.5).

### 3.1 Session boundaries

Each stage runs in its **own fresh session**. The only thing that crosses the boundary is whatever got committed to git — no session inherits another's reasoning or context. This is deliberate, not incidental: it's what makes the `verify` stage's end-user pass trustworthy (§5.2) — it can't inherit `impl`'s blind spots if it never saw `impl`'s session in the first place.

```
You (boss) → save the ticket text to <id>-ticket.md → /harness-eng spec
                                      ↓
                       <id>-spec.md committed to the progress repo
                                      ↓
                    new session reads spec → /harness-eng impl
                                      ↓
                  code (target repo) + <id>-qa.md + <id>-qa-e2e.md scaffold
                                      ↓
             new session reads spec + qa.md + scaffold → /harness-eng verify
                                      ↓
                         PASS → pr-create → pr-review → kb-update
                         FAIL → document repro, fix loop (max 2x) → escalate to boss
```

**Two repositories, two kinds of commit.** Code lands in the target repo on a feature branch. Every artifact lands in a separate personal progress repo, one directory per ticket (Q2). Both are git, so §3.1's contract holds for each; only the code is ever seen by the team.

**One stage per invocation.** Run the stage, commit, report, stop. Never continue into the next stage in the same session, even when the next stage is obvious and the context is already loaded.

This is the rule the whole design rests on. A session that ran `impl` cannot be trusted to run `verify`, because it already knows what it expects to pass — it would be grading its own homework. The session boundary is the guarantee, not a formality.

**The artifact is the whole contract.** Each session commits its output and the next session reads those files *cold* — no shared memory, no "as we discussed earlier":

| Session | Reads | Produces |
|---|---|---|
| 0 — *the operator* | the tracker | `<id>-ticket.md` — pasted by hand, before any stage (Q10) |
| 1 — `spec` | `<id>-ticket.md` | `<id>-spec.md` — numbered `Given/When/Then` acceptance criteria + evidence index + open questions (Q1) |
| 1b — `rca` *(bug tickets only)* | `<id>-ticket.md`, `<id>-spec.md` | `<id>-rca.md` — root cause, escape analysis, extra acceptance criteria the analysis demands (§3.3) |
| 2 — `impl` | `<id>-spec.md`, `<id>-rca.md` | code in the target repo + `<id>-qa.md` (dev test plan) + `<id>-qa-e2e.md` (bare scaffold, §4) |
| 3 — `verify` | `<id>-spec.md`, `<id>-qa.md`, scaffold | `<id>-qa.md` with `Result:` lines + `<id>-qa-e2e.md` authored and run (§5.2) + `<id>-verify-trace.md` (Q15) |
| 4 — `pr-create` | `<id>-spec.md`, `<id>-verify-trace.md` | `<id>-pr.md` drafted, then the PR opened from it; tracker updates printed for the operator (Q6) |
| 5 — `pr-review` | the diff, `<id>-spec.md` | inline review comments + `<id>-security-review.md` when there are findings (§6.1) |
| 6 — `kb-update` | `<id>-rca.md`, `<id>-verify-trace.md` | `docs/` updated in the **target** repo, on the feature branch (Q5) |

Two artifacts sit outside this sequence because every stage touches them:

- **`<id>-progress.md`** — each stage appends one or two lines, in the register of a commit message. It exists so that a week away costs one short file to read rather than five long ones (Q15).
- **`## Human input`** — any stage invoked with `--human` writes that text verbatim into its own artifact, appended and dated (§7.2, Q11). Otherwise the input dies at the session boundary.

Filenames follow `<ticket-id-lowercase>-<artifact>.md` throughout, and **stages read only the artifacts named above** — a ticket directory also collects logs, scripts, and captured bundles, and those are scratch (Q16).

Because the contract is files rather than context, each stage can run in a **different session, a different model, or be picked up by a different engineer** — the artifacts carry everything needed.

### 3.2 Running the pipeline

One skill, one grammar:

```
/harness-eng <stage> <ticket> [mode] [--human "<free text>"]

stages:  spec | rca | impl | verify | pr-create | pr-review | kb-update
modes:   fix-qa | fix-sec          (impl only — §5.5)
--human: optional per-invocation context, valid on every stage (§7.2)

<ticket>: a bare ticket ID, searched for beneath the progress root — or,
          when it contains "/", a path relative to that root (Q13)
```

**Before the first stage**, save the ticket text to `<id>-ticket.md` in the ticket directory (Q10). Every stage after that is invoked by you, **each in a fresh session**:

```bash
# Session 1 — generate the spec from the ticket
/harness-eng spec <TICKET-ID>

# Optional — align on ambiguities before implementing
/interview-me <ticket-dir>/<ticket-id>-spec.md

# Session 1b — BUG TICKETS ONLY: root-cause before any fix is written (§3.3)
/harness-eng rca <TICKET-ID>

# Session 2 — implement from the spec (and the RCA, if this is a bug)
/harness-eng impl <TICKET-ID>

# Session 3 — verify (environment pre-flight, dev pass, then E2E pass)
/harness-eng verify <TICKET-ID>

# Session 4 — draft the body, then open the PR (run manually; nothing chains)
/harness-eng pr-create <TICKET-ID>

# Session 5 — review the PR once it's open
/harness-eng pr-review <TICKET-ID> <pr-url>

# Session 6 — write learnings back
/harness-eng kb-update <TICKET-ID>
```

Repair modes, inside the `impl ↔ verify` loop only (§5.5):

```bash
/harness-eng impl <TICKET-ID> fix-qa
/harness-eng impl <TICKET-ID> fix-sec
```

Per-invocation human context, valid on any stage:

```bash
/harness-eng spec <TICKET-ID> --human "Only reproduces on kernel 6.8.10; triage to that version only."
```

**Artifact paths are never passed as arguments.** Each stage resolves the ticket directory once (Q13), then derives every filename from the ticket ID (Q16) — one fewer thing to get wrong, and one fewer way for two stages to disagree about where a file lives.

**No stage triggers another.** You decide when each one runs; that is the point of acting as the boss, and each transition is a checkpoint you can redirect at. This holds for `kb-update` too — an earlier draft had `pr-review` fire it on PASS, which contradicts the one-stage-per-invocation rule and is withdrawn (Q5).

**A stage that needs you either waits or exits, decided by how long you would be away** (Q7/Q9). A seam confirmation is answered in seconds, so the session waits. A manual E2E checklist takes hours or days, so the session writes down what it needs, tells you how to return the results, and stops.

### 3.3 Bug tickets — the RCA branch

The one place the pipeline branches on ticket type. On a bug, the `rca` stage runs in its own fresh session between SPEC and IMPL. On a story, chore, or task it does not run at all — there is no defect to root-cause, and forcing one produces a document that says nothing.

**Why before IMPL, not after.** The root cause determines the fix. An RCA written after the fix exists can only rationalize what was already built — it inherits the implementer's conclusion instead of testing it. Running it first means a wrong root cause costs a spec revision rather than a wasted implementation session. It also lands as an independent check on the `spec` stage: a cold session that never saw the spec's reasoning re-derives the mechanism from the code, and the spec is where a wrong root-cause claim is cheapest to catch.

**Input:** `<ticket-id>-spec.md` plus the ticket text. The spec owns *what is broken and how it will be fixed*; the RCA owns *why it shipped and why it escaped*, and must not restate the spec's fix detail — it links to it.

**Output:** `<ticket-id>-rca.md`, in three fixed parts, in this order:

1. **At a glance** — the triage surface, read alone. One row per defect: `| # | What's broken | Where | Effect | Fix |`, where `What's broken` names the mechanism rather than the symptom and `Where` gives the `file:line` call chain. Supporting tables only when they would change a triager's mind — blast radius, or a derivation table when the mechanism turns on the difference between two things that look equivalent. A table that restates the spec's files-touched list gets cut.
2. **TL;DR** — the root cause in one line, leading with mechanism, never blame. Two or three supporting bullets only where the one-liner needs them to be believable: an assumption that was defensible in isolation, a requirement aimed at a different scenario, a test surface that did not exist yet.
3. **Deep dive** — one named subsection per defect or per cause. Each cites the commit that introduced the gap, names the assumption that was correct in isolation and wrong in composition, and explains what kept it hidden.

The deep dive closes with three fixed subsections:

- **What would have caught it** — numbered, *generalizable* process rules, not ticket-specific notes. These are the RCA's output to `kb-update` (§3 stage 6), and on bug tickets they are its primary input.
- **Fix verification tied to this RCA** — the load-bearing section, and the reason the branch sits where it does. Escape analysis routinely surfaces a scenario nobody would have written an acceptance criterion for. Each such finding becomes a numbered criterion here, cited back to the spec's numbering (`AC-6`, `E2E-5`), and `impl` and `verify` are bound by it exactly as they are by the spec's own criteria. This is what makes the RCA generative rather than a retrospective.
- **Reference** — every load-bearing claim mapped to its source: `file:line`, commit SHA, or a section of a prior ticket's spec/QA artifact. A claim that cannot be sourced is marked `[NEEDS CONFIRMATION]` and surfaced, never asserted.

**Not the same thing as §5.4.** The six-phase diagnosis in §5.4 debugs a failure this pipeline just produced — a red test, in the current session. The RCA explains why a defect reached users and was not caught, which is escape analysis over history: commits, requirements, and the test surface as it stood when the code was written. Different question, different evidence, different session.

**The RCA gates IMPL.** Its central job is confirming the spec's root-cause claim against the actual code — that the named guard or branch really is at the cited line, that the commits say what the spec says they say, that a second defect folded into the ticket is genuinely independent rather than a symptom of the first. If the claim does not hold, stop and report; the repair path is back to `spec`, not forward into a fix built on a wrong mechanism.

## 4. `impl` — laziest solution first, then TDD discipline (from `implement` + `tdd`)

- **On a bug ticket, read `<ticket-id>-rca.md` alongside the spec.** The confirmed mechanism is the RCA's, not the spec's suspicion, and any criteria under its *Fix verification tied to this RCA* section (§3.3) are binding exactly as the spec's own are.

**Before writing any code, climb the ladder** (from `ponytail`). Understand the problem and trace the real flow first, then take the first rung that holds and stop:

1. Does this need to be built at all?
2. Does it already exist in this codebase? Reuse the helper or pattern that is already here.
3. Does the standard library do it?
4. Does a native platform feature cover it?
5. Does an already-installed dependency solve it?
6. Can it be one line?
7. Only then: write the minimum code that works.

Rules that follow from it: no abstraction that wasn't asked for, no new dependency that can be avoided, deletion over addition, boring over clever, fewest files possible. The shortest working diff wins — **but only once the problem is understood.** A small change in the wrong place isn't lazy, it's a second bug.

Not lazy about: understanding the problem, input validation at trust boundaries, error handling that prevents data loss, security, accessibility, or anything explicitly requested.

**The ladder and TDD are not in tension** — they run at different moments. The ladder decides *whether code gets written*; TDD governs *how code that must exist gets written*. If rung 2 holds, there is no new code, so there is no test to write. The discipline below applies from rung 7 onward.

**Mark deliberate shortcuts.** When a rung is taken that cuts a real corner with a known ceiling, leave a `ponytail:` comment naming the ceiling and the upgrade path:

```
// ponytail: single global lock, fine under ~100 req/s. Swap for a per-key
// mutex if throughput grows.
```

`kb-update` (§3 stage 6) harvests these, so a deferral stays visible instead of rotting into "later means never."

- **Seams first.** Before writing any test, name the public interfaces under test ("seams") and confirm them with the user. No test against internals, no test at an unconfirmed seam.
- **Red → green, one slice at a time.** One seam, one failing test, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **Refactoring is a separate step**, not part of the red→green loop — it happens at review time (§6), not mixed into implementation.
- **Anti-patterns to actively avoid** while writing tests:
  - *Implementation-coupled* — mocking internals, testing private methods, or asserting via a side channel instead of the public interface. Tell: it breaks on refactor even though behavior didn't change.
  - *Tautological* — the expected value is computed the same way the code computes it (so it can't disagree). Expected values must come from an independent source: a known-good literal, a worked example, the spec.
  - *Horizontal slicing* — writing all tests before any implementation. Do vertical slices instead: one test → one implementation → repeat.
- **Mechanical checks during implementation:** typecheck regularly, run the single relevant test file regularly, run the full suite once at the end.
- **Produce two verification artifacts alongside the code** (consumed by `verify`, §5):
  - `<ticket-id>-qa.md` — the dev-perspective test plan: what was actually tested during red→green (the seams, the commands to re-run them). One case per acceptance criterion, each with an explicit `Setup:`, `Action:`, and `Expected:` block so a cold reader can execute it. Must also carry two fixed sections: `## Test Environment` and an empty `## Correction log` table for §5.5.
    `## Test Environment` is a list of **checkable preconditions**, not prose — each one paired with the command that confirms it, so §5.5's pre-flight has something to run rather than something to read. It also names which existing case serves as the **control case** for that pre-flight.
  - `<ticket-id>-qa-e2e.md` — a **bare scaffold, not a test plan**. Name only *what screens/flow this ticket touches* (e.g. "the hello-world button on the home screen"). Do **not** write concrete steps, click order, or pass/fail assertions here — that decision belongs entirely to the `verify` session (§5.2), specifically so the implementer can't unconsciously write an end-user test that's secretly shaped around what it already knows will pass.
- Commit to the current branch when done; hand off to `verify` (§5).

## 5. `verify` — two-perspective verification, then structured diagnosis on failure

Renamed from `ticket-qa`: "QA" in a command name reads as "Question & Answer" at a glance — this stage runs no interview, it verifies. (Artifact filenames keep the industry-standard `-qa`/`-qa-e2e` suffix since "Quality Assurance" is unambiguous in that context.)

### 5.1 Why two perspectives

One test perspective isn't enough, because the two catch different failure classes:

- **Dev perspective (API/integration level)** — stand up the local stack and its dependent services, then exercise the change directly (`curl`, an RPC client, a test runner hitting the seam). Fast, deterministic, close to the code. Blind to anything that only breaks in the actual client (wrong event binding, a CSS layer eating the click, a JS error the API layer never sees).
- **End-user perspective (E2E/UI level)** — drive the real client the way a person actually would (browser automation clicking the real button, a mobile driver tapping the real screen). Catches what the API-level check can't see, but is slower and shouldn't be the only signal either — a person could recreate correct-looking behavior on top of a broken or accidentally-right contract.

**Worked example** — a hello-world fullstack app where pressing a button echoes "Hello, World" (illustrative — swap `curl` for whatever seam actually fits the ticket: an RPC call, a queue message, a CLI invocation):
- *Dev perspective*: run the local dev stack (frontend + backend + whatever it depends on), then `curl -X POST localhost:PORT/api/echo` and assert the JSON body is `{"message": "Hello, World"}`. This verifies the *contract*, not the button.
- *End-user perspective*: open the actual running app in a browser, click the actual button element, assert the DOM now renders the text "Hello, World". This is the only check that would catch, say, the button's `onClick` never being wired up even though the `/api/echo` endpoint is flawless — a real end user never runs `curl` from their client.

A real user only ever exercises the second one. Shipping on the first alone is checking the contract, not the product.

### 5.2 Ownership split — why `verify` authors the E2E test, not `impl`

The `impl` stage is not trusted to decide what "correct from a user's perspective" means, because it can unconsciously write an E2E test shaped around what it already knows will pass — the same blind spot code review avoids by never letting one axis see the other's reasoning (§6). So authorship of the real E2E test is split from authorship of the code:

- `impl` may only name *what flow* is touched (the bare scaffold, §4) — never the concrete steps or assertions.
- `verify` runs in a session that never saw `impl`'s reasoning (§3.1) — only the committed spec, code, `qa.md`, and the scaffold. From that, it independently writes the actual clickable steps and assertions and treats the acceptance criteria in `<ticket-id>-spec.md` — plus, on a bug ticket, those added by `<ticket-id>-rca.md` (§3.3) — as the source of truth for what "correct" means, not the scaffold's suggestions and not the implementation's behavior.

**If no E2E automation tooling exists in the target repo** (no browser-driver or equivalent), don't fake it or skip it silently: write the filled-in steps as a **manual checklist** for the boss to execute.

**The session then exits rather than waiting** (Q7/Q9) — a checklist takes hours or days, and a session held open that long carries context that has gone stale against a world that moved. It names exactly how to return the results:

```
Wrote <ticket-id>-qa-e2e.md — 6 cases. Run them, then:
  /harness-eng verify <ticket-id> --human "E2E-1..5 pass, E2E-6 fails: <what happened>"
```

The returned text lands verbatim in the artifact (§7.2), so the next session has the results in writing rather than in someone's memory.

### 5.3 Sequencing within `verify`

`verify` does not report VERIFY as passed until **both** passes are green, in this order:

1. **Dev pass** — run `<ticket-id>-qa.md` (produced by `impl`, §4) against the local stack. Fast feedback first.
2. **E2E pass** — only once the dev pass is green, write the real steps into `<ticket-id>-qa-e2e.md` per §5.2 and run them (or hand the manual checklist to the boss).

Both passes write their evidence to `<ticket-id>-verify-trace.md` as they run — each case, the command, the output, and the acceptance criterion it maps to, plus the control case and its verdict (Q15). §5.5 asks this stage to rule between a broken environment and broken code; a ruling with no record behind it can be believed but not reviewed.

If either pass fails, don't guess — classify it (§5.5) and, if it's a code bug, run the diagnosis discipline (§5.4) before forming any hypothesis.

**Skipping VERIFY entirely** is allowed for changes with no user-facing or E2E surface where you judge unit coverage sufficient — the flow becomes `impl → pr-create → pr-review`. The one condition: **the skip is never silent.** State the reason in the PR body so a reviewer sees that verification was consciously waived rather than forgotten.

### 5.4 Structured diagnosis on failure (from `diagnosing-bugs`)

When either pass fails and the cause isn't obvious:

1. **Build a feedback loop first.** A tight, deterministic, fast, agent-runnable command that goes red on this exact bug (failing test, curl against dev server, CLI + fixture diff, replayed trace, bisection harness — in roughly that order of preference). This step is the actual skill; everything after is mechanical. If you can't build one, stop and say so explicitly rather than theorizing.
   **The loop must discriminate, not merely go red.** A loop that is also red on a pre-existing control case (§5.5) is measuring the environment, not the bug — it will confirm every hypothesis equally and is worthless as evidence.
2. **Reproduce, then minimize** the repro to the smallest scenario that still goes red — cut one variable at a time, re-running after each cut.
3. **Generate 3–5 ranked, falsifiable hypotheses** before testing any of them ("if X is the cause, changing Y makes it disappear"). Show the ranked list to the user before testing — they may re-rank instantly from context you don't have.
4. **Instrument** — one probe per hypothesis, one variable at a time. Prefer a debugger/REPL over logs; tag any debug log with a unique prefix (`[DEBUG-xxxx]`) so cleanup is one grep.
5. **Fix + regression test** — write the regression test before the fix, but only at a seam that exercises the real bug pattern; a shallow seam gives false confidence. If no correct seam exists, that absence is itself a finding to flag.
6. **Cleanup + postmortem** — confirm the original repro no longer reproduces, all `[DEBUG-...]` logs are removed, throwaway harnesses are deleted, and the correct hypothesis is stated in the commit/PR message.

### 5.5 Triaging a failure — did the test even run, and then: code or doc?

A `FAIL` does not automatically mean the implementation is broken. **Classify the failure before fixing anything** — routing a bad test case into a code-fix loop is how a correct implementation gets "fixed" until it matches a wrong expectation.

**First, the pre-flight: did the test actually exercise the code?**

Three of the four classes below assume the test *ran*. A fourth cause sits underneath them all — the harness never reached the code at all. Expired credentials, a down VPN, a service that isn't up, the wrong config file. It produces a `FAIL` identical to a real code bug, and routing it into `fix-qa` spends two attempts editing correct code to satisfy a test that never executed.

Run a **control case**: any case in `<ticket-id>-qa.md` that predates this ticket and does not touch the change.

- **Control passes** → the environment is sound; the change is implicated. Continue to the three-way triage below.
- **Control fails too** → the environment is implicated and nothing about the diff is in evidence. Stop.

It must be a *pre-existing* case. A newly written case is supposed to fail before the code lands — that is red in red→green, not a signal.

Failure signature corroborates but does not decide: an environment failure typically dies before the assertion (connection refused, auth rejected, binary or config missing, connect timeout), while a code bug reaches the assertion and returns the wrong value.

Also confirm the control case can still **fail** — a suite that cannot go red is not evidence of anything, and a misconfigured environment can produce a false green just as easily as a false red (pointing at a stale or mocked service).

| Failure type | What it means | Who fixes it | How |
|---|---|---|---|
| **Environment** | The test never reached the code — the control case fails too | you (human) | fix the unmet precondition. **Zero retries** — never enter `fix-qa` (§5.6) |
| **Code bug** | The implementation doesn't do what the acceptance criterion says | the impl session | route back: `/harness-eng impl <id> fix-qa` (bounded — §5.6) |
| **Wrong assertion** | The `Expected:` value in the QA case is itself incorrect | you (human) | edit `Expected:` in the case, add a `## Correction log` row, re-run `verify` |
| **Wrong test step** | The `Setup:` or `Action:` block is incorrect — the impl session wrote the test wrong | you (human) | edit the `Setup:`/`Action:` block, add a `## Correction log` row, re-run `verify` |

> **The rule:** `fix-qa` means *"the code is wrong."* Editing the QA doc means *"the doc is wrong."* Never use `fix-qa` to paper over a bad assertion or a bad test step — that silently rewrites working code to satisfy a typo.

**Who writes what in `qa.md`** — the two halves have different owners, and mixing them destroys the audit trail:

- `verify` writes the `Result:` lines. Never hand-edit those.
- You write `## Correction log` rows, recording what was wrong and what you changed.

```
| Date       | Case    | What was wrong                  | Correction                    |
|------------|---------|---------------------------------|-------------------------------|
| 2026-08-01 | Case 03 | Setup used the wrong fixture path | Pointed it at ./fixtures/v2/ |
```

A future reader then sees both the original expectation and why it moved, instead of a doc that quietly always agreed with the code.

**Scope of `fix-qa`:** it belongs to the `impl ↔ verify` loop only, and that loop must close *before* a PR is opened. Correctness findings raised later in `pr-review` (§6) do **not** re-enter `fix-qa` — you address the comment and re-push. The only named repair loop that starts from review is a **security** finding: `/harness-eng impl <id> fix-sec`.

### 5.6 Bounded retry & escalation

**The retry budget depends on which class the failure is**, and the two are opposites:

| Cause | Retries that help | Escalate after | What the human is asked for |
|---|---|---|---|
| **Environment** | **0** — a thousand attempts give a thousand identical failures | immediately | "Precondition X unmet: `<evidence>`" — fix the machine |
| **Code bug** | up to 2 — each is a new hypothesis | 2 attempts | the repro, both attempts, the ranked hypothesis list |

Both cap far below "keep trying," for opposite reasons: retrying a broken environment cannot produce new information, while retrying a code bug past two attempts stops being hypothesis-driven and becomes guessing. The human is also being asked for two different things — repair their machine versus judge the code — so collapsing both into one "escalate" wastes the escalation.

**On an ENVIRONMENT failure:** do not enter `fix-qa`, do not edit the code, do not edit the QA doc. Report the unmet precondition and its evidence, and stop. If the environment cannot be restored in reasonable time, the documented-skip path in §5.3 is the exit — stated in the PR body, never silent.

**On a CODE BUG,** the `fix-qa` loop is bounded:

1. **Document the reproduction step first** — the tight, red-capable command from §5.4 phase 1, committed to the ticket's working notes, before attempting any fix.
2. **Run the fix loop at most twice.** Each attempt is one full pass through §5.4 phases 3–5 (hypothesize → instrument → fix). Two failed attempts is the cap — not two hypotheses within one attempt.
3. **Escalate, don't spin.** If VERIFY still fails after 2 attempts, stop. Report back to the boss with: the documented repro, both attempts and why each didn't hold, and the current ranked hypothesis list. Wait for direction rather than continuing to guess — anything touching decisions beyond this session's own scope is recommended and waited on, never applied.

## 6. `pr-review` — security gate, then three-axis review

### 6.1 Security gate (runs first)

Before the three axes below, scan the same diff for security defects only — injection, authn/authz gaps, credential or PII exposure in logs and errors, unsafe deserialization, missing input validation at trust boundaries. Keep it narrow: this is not a code-quality pass, and quality findings belong to §6.2.

A finding here **blocks the PR** and writes `<ticket-id>-security-review.md`. It is the one review finding with a named repair loop back into implementation: `/harness-eng impl <id> fix-sec`. Everything else in §6.2 is addressed by editing and re-pushing, not by re-entering a repair mode (§5.5).

### 6.2 Three-axis review

Review the diff between a fixed point (a commit/branch/tag the user names, or `main` by default) and `HEAD`, along **three independent axes**, each run as a **parallel sub-agent** (`Agent` tool, `general-purpose` type, one message with all three calls) so none pollutes another's context:

- **Standards axis** — does the diff conform to this repo's documented standards (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, etc.), *plus* a fixed Fowler smell baseline that applies even when the repo documents nothing: Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality, Message Chains, Middle Man, Refused Bequest. A documented repo standard always overrides the baseline. Baseline smells are always judgement calls; documented-standard breaches can be hard violations.
- **Spec axis** — does the diff faithfully implement the originating ticket/spec? Report missing/partial requirements, scope creep, and requirements that look implemented but are wrong — quoting the spec line for each finding.
- **Deletion axis** (from `ponytail`) — what in this diff should not exist? Reinvented standard library, a dependency that wasn't needed, speculative abstraction, dead flexibility, boilerplate nobody asked for. One line per finding: where it is, what to cut, what replaces it. This axis only hunts excess — it says nothing about correctness.

Report the three axes under separate headings, never merged or re-ranked against each other — a change can legitimately pass one and fail another. Correct behavior that breaks conventions, clean code that does the wrong thing, and a faithful correct implementation that is twice the size it needs to be are three different findings, and collapsing them hides the third almost every time.

## 7. Directory Structure

```
productivity/harness-eng/          # source — publishable as-is
├── SKILL.md                       # the engine: dispatch, boundaries, escalation
├── SPEC.md                        # this document
├── NOTICE.md                      # attribution — mattpocock/skills, ponytail (both MIT)
├── reference/
│   ├── spec-create.md
│   ├── ticket-rca.md              # §3.3 — bug tickets only
│   ├── ticket-impl.md             # §4
│   ├── ticket-verify.md           # §5
│   ├── pr-lifecycle.md            # pr-create + pr-review (§6)
│   └── kb-update.md
└── deferred/
    └── spec-phase-2.md            # NOT ACTIVE — not a build target

~/.claude/skills/harness-eng/      # install — one copy, resolves in every repo
```

Same shape as every other skill in this repo: `SKILL.md` and `SPEC.md` side by side. No index file — the directory is the index.

**The split between the two levels is what keeps sessions small.** `SKILL.md` holds everything shared across stages — the dispatch table, the one-stage-per-invocation rule (§3.1), the artifact contract, the `CLAUDE.md` read and its fallback (§7.1), `--human` handling (§7.2), and escalation (§5.6) — written once, never restated. Each `reference/<stage>.md` holds only that stage's procedure and is read on demand, so a `verify` session never loads `ticket-impl.md`.

No installer CLI, no `--phase`/`--overwrite`/`--global` flags, no config seam. This is a plain skill directory following this repo's existing convention, installed the same way as every other skill here. Machinery for binding many companies' specifics to one kernel only earns its keep at a scale this document does not have.

### 7.1 Kernel only — where company specifics live

Claude Code resolves skills from two places: user-level `~/.claude/skills/` and project-level `.claude/skills/`. **This uses the user level only, and installs exactly one skill.**

- **The skill is the kernel: workflow and reasoning, nothing else.** Installed once, globally, identical in every repo. No per-repo copy, no tailored variant, no override layer, and no second skill per stage.
- **Everything company- or repo-specific lives in that repo's `CLAUDE.md`** — test commands, environment prerequisites, branch and commit conventions, house patterns, domain vocabulary.

**The engine is strictly agnostic.** It does not know what branch you are on, where the compiler is, what the test command is, or what code style is required. It knows the loop: which stage runs, what artifact that stage consumes, what it produces, when to stop, and when to escalate. Every operational fact is user space, and user space is `CLAUDE.md`.

Three layers, separated by how long each one lives:

| Kernel — `SKILL.md` + `reference/`<br>*(permanent, every repo)* | User space — target repo `CLAUDE.md`<br>*(durable, this repo)* | `--human`<br>*(one invocation)* |
|---|---|---|
| Stage order and the bug branch | Which tracker, which ticket-ID format | "only reproduces on kernel 6.8.10" |
| The artifact contract between sessions | Where artifacts are committed | "reporter is on the enterprise tier" |
| "run the relevant test file, then the suite" | What the test command actually is | "I already ran the slow suite" |
| Climb the ladder, then test at a seam | That shell-outs are mocked at an interface seam here | "check the retry path first — that's my hunch" |
| Two-perspective verification | That the stack needs VPN + `KUBECONFIG=<path>` | "no staging today; manual checklist only" |
| Failure triage and the retry caps | Which reviewer to escalate to | "escalate straight to me" |

Two reasons the split is not merely a preference:

1. **A per-repo copy is a fork.** Ten repos means ten copies drifting apart, and a kernel fix has to be re-applied ten times — with no signal when one is missed. One name must mean one behavior. The same argument rules out one skill per stage: seven skills would restate the shared rules seven times.
2. **`CLAUDE.md` is loaded automatically at session start.** A separate bindings file would require the skill to *remember* to read it, which fails silently when it doesn't. Reading `CLAUDE.md` costs the kernel nothing and is already in context before the skill runs.

The consequence is that the kernel is **publishable by construction**: there is no slot in it where a company fact could sit, so none can leak. Publishability stops depending on reviewer discipline.

**Write bindings as facts about the repo, not as instructions to the harness.** "The integration stack is reachable only over VPN; `KUBECONFIG` must point at `<path>`" is true for a human onboarding and stays true if the harness is replaced. "When running `verify`, remind me about the VPN" is neither. The first is uncontroversial to commit to a file the whole team shares; the second is workflow trivia in a shared namespace.

**The skill must degrade gracefully when `CLAUDE.md` documents nothing.** Each stage names its own fallback and proceeds — never blocks, never invents a convention and presents it as the repo's. §6.2 already does this correctly, applying its smell baseline "even when the repo documents nothing"; the same rule holds everywhere.

`interview-me` remains a separate installed skill. "One skill" scopes to the harness loop, not to the whole skill set — `interview-me` is useful on its own, outside any pipeline, and the `spec` stage delegates to it rather than reimplementing it.

### 7.2 `--human` — per-invocation context

`--human "<free text>"` is valid on every stage. It carries what neither other layer can: a fact true of *this ticket only*.

```bash
/harness-eng spec <TICKET-ID> --human "Only reproduces on kernel 6.8.10; triage to that version only."
```

Three rules make it safe:

1. **It is written into the stage's artifact, verbatim, under a `## Human input` heading.** Sessions share nothing but committed files (§3.1), so input that stays in the session evaporates before the next stage runs. Without this rule the flag would create exactly the invisible cross-session state the artifact contract exists to prevent.
2. **It outranks inference, but never silently.** Where it contradicts `CLAUDE.md` or the spec, the stage says so and asks which wins rather than quietly deviating. The resolution is recorded next to the input.
3. **Repetition means it belongs in `CLAUDE.md`.** The same `--human` text passed on a third ticket was never per-invocation context — it is a repo fact being re-typed. Same test as §3 stage 6 applies to learnings: transient goes on the command line, durable goes into user space.
4. **On a repair invocation it appends, dated — it never replaces** (Q11). What an instruction *used to be* is often the only thing that explains why the code looks the way it does. A later entry may countermand an earlier one in words; it never deletes it from the record.

## 8. Handover Checklist

**Applies to everything below:** kernel only (§7.1) — no company facts, no hardcoded conventions, and an explicit fallback for when the target repo's `CLAUDE.md` documents nothing. One skill, installed user-level to `~/.claude/skills/harness-eng/`. Follow `../writing-skills/SKILL.md`, the house authoring standard, throughout.

**Rules that bind every file below**, resolved in §9 and not restated per item: filenames are `<ticket-id-lowercase>-<artifact>.md` and only the named artifacts are ever read (Q16); a missing or malformed input fails fast naming the artifact, the path searched, and the command that produces it (Q8); a stage waits only for an answer given in seconds and otherwise exits with instructions for returning results (Q7/Q9); every stage appends one or two lines to `<id>-progress.md` (Q15); no stage triggers another (§3.1).

- [ ] Write `SKILL.md` — frontmatter (`name`, `description`, `disable-model-invocation: true` per Q14), the stage dispatch table, argument grammar including `[mode]` and `--human` (§3.2), ticket-directory resolution by search with the `/`-means-path override (Q13), the one-stage-per-invocation rule (§3.1), the artifact contract and filename convention (§3.1, Q16), the `CLAUDE.md` read and its fallback (§7.1), `--human` handling including dated append (§7.2), the wait-or-exit rule (Q7/Q9), and escalation (§5.6). **Contains no stage-specific procedure** — those live in `reference/`.
- [ ] Write `reference/spec-create.md` — reads `<id>-ticket.md` and fails fast if absent (Q10); delegates to `interview-me` for the interview mechanics; produces numbered `Given/When/Then` acceptance criteria and the evidence index (Q1). Reads a parent epic AC tracker for context if one is present (Q17).
- [ ] Write `reference/ticket-rca.md` implementing §3.3 — no-op on non-bug tickets, the three-part output in its fixed order, the *Fix verification tied to this RCA* section, and the stop-and-report gate when the spec's root-cause claim fails verification against the code (Q10).
- [ ] Write `reference/ticket-impl.md` implementing §4 — the ladder first, then the TDD discipline, the `ponytail:` shortcut marker, both QA artifacts (`-qa.md` with checkable `## Test Environment` preconditions, a named control case, and an empty `## Correction log`; plus the `-qa-e2e.md` scaffold), the seam confirmation as the one blocking checkpoint (Q7), and the `fix-qa` / `fix-sec` repair modes.
- [ ] Write `reference/ticket-verify.md` implementing: the §5.5 environment pre-flight, its control-case discriminator and the first-ticket fallback with its *pre-flight unavailable* announcement (Q12), independent E2E authorship (§5.2), dev-pass-then-e2e-pass sequencing and the documented-skip escape hatch (§5.3), six-phase diagnosis (§5.4), the four-way failure triage and `## Correction log` ownership (§5.5), `<id>-verify-trace.md` as the evidence record (Q15), the exit-and-be-re-invoked handoff on the manual checklist path (Q9), and both retry budgets — zero for environment, two for a code bug (§5.6).
- [ ] Write `reference/pr-lifecycle.md` with `pr-create` drafting `<id>-pr.md` (TL;DR, what changed, why, acceptance criteria pasted verbatim, how verified, deliberately skipped) then opening the PR from it and printing tracker updates rather than performing them (Q6), plus the one coarse line appended to a parent epic tracker when one exists (Q17); and `pr-review` implementing the §6.1 security gate (blocking, writes `-security-review.md`, repairs via `fix-sec`) followed by §6.2's three-axis parallel-subagent review.
- [ ] Write `reference/kb-update.md` — Q5: scope picks `docs/shared/` or `docs/project/<slug>/` in the **target** repo, written on the feature branch so it reaches the team through PR review; the proper-noun graduation test routing method improvements out to the kernel instead; and harvesting `ponytail:` markers into a ledger under `docs/shared/`.
- [ ] Update `NOTICE.md` crediting `mattpocock/skills` (MIT) for §4 and §6, and `dietrichgebert/ponytail` (MIT) for the ladder in §4 and the deletion axis in §6.2.

## 9. Open Questions

**All closed.** Every question below is resolved and folded into the sections it affects; nothing here blocks writing `SKILL.md`. Resolved items keep their number rather than being deleted — other documents cite them, and the reasoning behind a decision is worth more than the decision alone when someone later wants to change it.

Q15, Q16 and Q17 were opened *during* the closing pass, from evidence about how the pipeline is actually run: two artifact types in daily use that this document had never named, a filename convention it had left implicit, and a parent-epic level it did not know existed.

### Blocking — a skill cannot be written without these

**Q1 — What is the spec template, and what shape is an acceptance criterion?** ~~(§3 stage 1, §8 item 1)~~ — **RESOLVED.**
An acceptance criterion is a **numbered `Given/When/Then` statement**, individually testable. Numbering is what lets `qa.md` cases, `pr-review` findings, and the RCA's *Fix verification* section (§3.3) cite `AC-3` unambiguously; E2E cases are numbered in their own series (`E2E-5`).

The spec carries a second required section, an **evidence index**, mapping each load-bearing claim to a `file:line` or commit SHA. `rca` traces from it (§3.3) and cannot verify a root-cause claim without one — without the index it re-derives every claim's provenance and cannot distinguish a verified claim from a guessed one.

```markdown
## Acceptance criteria
AC-1  Given <precondition>
      When <action>
      Then <observable outcome>

## Evidence
AC-1                        <path>:<line>
claim: "<load-bearing claim>"  <path>:<line>
```

Ticket text as an input is resolved by Q10. *(Number retained — other documents cite "Q1".)*

**Q2 — Where do ticket artifacts live?** ~~(§3.1, §3.2)~~ — **RESOLVED.**
Artifacts live in a **separate personal progress repository**, outside every target repo, with one directory per ticket ID. It is a real git repository, so §3.1's "committed to git" contract holds unchanged.

```
~/<progress-root>/
├── <grouping>/            # optional — epic, team, whatever you like
│   └── <ticket-id>/
│       ├── ticket.md
│       ├── spec.md
│       ├── qa.md
│       └── ...
```

**Resolution of the progress root is a machine-personal fact**, not a repo fact: it is recorded in the *user-level* context file (`~/.claude/CLAUDE.md` or the harness's equivalent), never in a target repo's `CLAUDE.md`. A target repo's context file is shared with the team, and a personal notes path does not belong in it. This is the one fact that lives at neither of §7.1's two layers — it is true of the machine, across every repo on it.

**Finding a ticket's directory** is resolved by Q13, since intermediate grouping means the path is not derivable from the ticket ID alone.

Three alternatives were rejected:

| Rejected | Why |
|---|---|
| `.harness/<id>/` committed in the target repo | Puts personal working notes in shared source — a change a teammate is right to object to. Also disappears on `git checkout main`, and a ticket spanning two repos has no single home. |
| `.harness/<id>/` gitignored in the target repo | Never committed, so it has no history at all — this abandons §3.1's contract outright while buying no privacy the separate repo does not already give. |
| Epic passed as part of the ticket argument | Makes every invocation longer and requires the human to remember which grouping a ticket sits under; a cold session cannot remind them. |

Two consequences carried elsewhere:

1. **Reviewers no longer see the spec beside the diff.** `pr-create` must therefore *paste* the acceptance criteria into the PR body as text rather than link to a file no reviewer can open (Q6).
2. **The progress repository accumulates real ticket IDs, service names, and root-cause writeups.** It stays local-only or on a private remote. A public remote on it would undo, in one push, the separation this whole document is built to preserve. Its `README.md` says so on line one.

A note on what this does *not* buy: on a company-issued machine the artifacts are still on company hardware and company backups. The separation is from company *git* — no PR noise, no permission conversation, and the history leaves with you. It is not secrecy, and should not be planned as if it were. *(Number retained — other documents cite "Q2".)*

**Q13 — How does a cold session find a ticket's artifact directory?** ~~(§3.2, Q2)~~ — **RESOLVED.**
Search for a directory named `<ticket-id>` anywhere beneath the progress root. Grouping under that root is free-form and is expected to vary — by epic, by year, by team, by whatever made sense at the time — so no fixed depth or naming scheme may be assumed.

| Hits | Behaviour |
|---|---|
| exactly 1 | use it |
| 0 | create `<root>/<ticket-id>/` and say where |
| 2 or more | stop, list every match, ask which |

**The human is the fallback, and pointing is a first-class input rather than an error path.** When the search does not land, the operator names the directory; the session never guesses between candidates and never invents a second home for a ticket that already has one.

**Mechanism: a `<ticket-id>` argument containing `/` is a path, not an identifier**, resolved relative to the progress root. This makes pointing a normal invocation rather than an interactive repair, and it carries no state between sessions:

```bash
/harness-eng verify eng-1                    # search
/harness-eng verify <grouping>/<...>/eng-1   # pointed
```

The ticket ID for artifact-naming purposes is the last path segment, so a pointed invocation and a searched one produce identical filenames. *(Number retained — other documents cite "Q13".)*

**Q16 — What are artifacts named?** — **RESOLVED.** `<ticket-id-lowercase>-<artifact>.md`, one spelling per artifact, throughout.

| Artifact | Filename | Written by |
|---|---|---|
| ticket text | `<id>-ticket.md` | the operator, before any stage (Q10) |
| spec | `<id>-spec.md` | `spec` |
| root cause | `<id>-rca.md` | `rca` — bug tickets only |
| dev QA plan | `<id>-qa.md` | `impl` |
| end-user QA plan | `<id>-qa-e2e.md` | `verify` (§5.2) |
| verification evidence | `<id>-verify-trace.md` | `verify` (Q15) |
| PR body draft | `<id>-pr.md` | `pr-create` (Q6) |
| security findings | `<id>-security-review.md` | `pr-review` (§6.1) |
| resume point | `<id>-progress.md` | every stage, append-only (Q15) |

**The ticket-ID prefix is load-bearing**, not decoration: a dozen of these are open in an editor at once, and `spec.md` twelve times over is unreadable. **Lowercase throughout** — mixed case on the same ticket's files is a real cost paid every time you type a path or sort a directory.

**Stages read only the artifacts named above.** A ticket directory also accumulates working material — logs, scripts, captured bundles, build detritus — and a cold session that wanders into a stale log bundle draws conclusions from evidence belonging to a different run. The named set is the contract; everything else in the directory is scratch, and invisible to the pipeline.

**Q14 — Is `harness-eng` user-invoked or model-invoked?** — **RESOLVED.**
**User-invoked** (`disable-model-invocation: true` in Claude Code; the equivalent flag on other harnesses). This is the house default set by `../writing-skills/SKILL.md` Phase 3, and it is the right one here for a specific reason: the stages commit work and open pull requests, and §3.1 forbids chaining stages inside one session. An agent able to fire a stage autonomously is an agent able to cross the session boundary that makes `verify`'s end-user pass trustworthy. The frontmatter `description` is therefore human-facing — a one-line summary for a slash-command list, with trigger phrasing stripped, since nothing matches against it.

**Q3 — Where do skills read project conventions from?** ~~(§4)~~ — **RESOLVED, see §7.1.**
Skills are kernel-only and installed user-level; every company- and repo-specific fact lives in that repo's `CLAUDE.md`, which is loaded automatically at session start. No per-repo skill copies. Each stage must name a fallback for when `CLAUDE.md` documents nothing. *(Number retained — other documents cite "Q3".)*

**Q4 — What is the repair-mode invocation syntax?** ~~(§5.5, §6.1 vs §3.2)~~ — **RESOLVED, see §3.2.**
The single grammar answers it: `/harness-eng <stage> <ticket-id> [mode] [--human "<text>"]`. Mode is a trailing optional token valid only on `impl`; artifact paths are derived from `<ticket-id>` rather than passed, which removes the argument-shape inconsistency the question was about. *(Number retained — other documents cite "Q4".)*

### Would produce a vague skill if left open

**Q5 — What does `kb-update` actually write?** ~~(§3 stage 6, §8)~~ — **RESOLVED.**

**The knowledge base lives in the target repo's `docs/` tree, not in the progress repo.** This is the deliberate counterpart to Q2, not a contradiction of it: personal working artifacts stay out of company git, and durable documentation the team needs belongs in it. The two are different things with different audiences, and conflating them is what makes each one worse.

```
<repo>/docs/
├── README.md                     # orients a reader arriving cold
├── shared/                       # repo-wide, project-agnostic
│   ├── architecture-<topic>.md
│   ├── ops-<topic>.md
│   └── repo-orientation.md
├── project/<project-slug>/       # scoped to one project or epic
│   ├── README.md
│   └── design-<phase>.md
└── <initiative-slug>/            # a standalone effort with its own life
```

**Scope picks the directory.** True of the whole repository regardless of what you are working on → `docs/shared/`. True of one project or epic → `docs/project/<slug>/`. Every directory carries a `README.md` that orients someone arriving cold; a directory of documents with no entry point is a pile, not a knowledge base.

**Written on the feature branch**, so it reaches the team through the same PR review as the code. No silent writes into shared documentation, and no separate approval path to remember.

**Record only what was non-obvious** — a wrong assumption corrected, a convention discovered, a trap laid for the next engineer. Never restate what the diff already shows. On bug tickets this stops being improvisation: the RCA's *What would have caught it* list (§3.3) is already exactly this material, already sourced, and is the stage's primary input.

**A third destination sits outside every repo.** Apply the graduation test — **strip every proper noun.** Something survives → it is a method improvement and belongs in the kernel skill itself, which no repo owns. Nothing survives → it is documentation, and lands in `docs/` per the scope rule above. Mixing the two is how a portable kernel silently acquires one employer's conventions.

This stage also harvests `ponytail:` markers (§4) into a debt ledger under `docs/shared/`, so deliberate shortcuts stay visible to the team instead of rotting into "later means never."

**Triggering:** §3.2's claim that `pr-review` auto-triggers this stage is withdrawn — it contradicts the one-stage-per-invocation rule (§3.1). `kb-update` is invoked like every other stage. *(Number retained — other documents cite "Q5".)*

**Q10 — Where does the RCA get the ticket text, and is `rca` blocking?** ~~(§3.3)~~ — **RESOLVED.**
The operator saves the ticket text to `<ticket-dir>/ticket.md` before running any stage. `spec` and `rca` both read that one file — one source, archived beside the artifacts it produced, and readable with no network. A missing `ticket.md` is a fail-fast (Q8), not an improvisation:

> `No ticket.md for <ticket-id>. Save the ticket text to <resolved-path>/ticket.md and re-run.`

**No tracker binding, in either direction.** A fetch-command-from-`CLAUDE.md` variant was rejected: it adds a second code path to the most-run stage in exchange for a capability that depends on company CLI access, and it puts a tracker-shaped hole in the kernel where §7.1 says none should exist. The cost is accepted honestly — pasting loses whatever lives in tracker comments, and the operator is free to paste those into `ticket.md` too.

**`rca` blocks only on a failed root-cause verification.** Where the spec's root-cause claim does not survive checking against the code, the stage stops and reports rather than writing an RCA built on a claim it just disproved. Otherwise it writes the document and exits, and IMPL reads it cold. *(Number retained — other documents cite "Q10".)*

**Q15 — Are `progress` and `verify-trace` artifacts part of the pipeline?** — **RESOLVED.** Both, and neither is a new stage.

**`<ticket-id>-progress.md` is a resume point, not a journal.** One or two lines per stage run, written in the register of a commit message: what was done, what state the ticket is now in. Its whole purpose is that after a week away you recover the thread from one short file instead of reconstructing it from five long ones. Length is the feature — a progress file that grows into prose has stopped doing the job it exists for.

```markdown
2026-08-14  spec    6 ACs, 2 open questions
2026-08-14  impl    done; mocked at <interface>
2026-08-15  verify  AC-4 red, code bug -> fix-qa
```

**`<ticket-id>-verify-trace.md` is `verify`'s evidence.** Each case, the command run, the output seen, and which AC it maps to — including the control case and its verdict (§5.5). Without it a triage decision is a claim; with it the decision is checkable by someone who was not there. §5.5 asks a session to rule between environment and code, and a ruling with no record behind it cannot be reviewed, only believed.

Both are naming conventions applied by stages that already exist: every stage appends to `progress`, and `verify` alone writes the trace.

**Q17 — What may a stage do with a parent epic's AC tracker?** — **RESOLVED.** Read it for context; append exactly one coarse line when the ticket finishes; never create it.

**The parent level is told whether a child is done, and nothing else.** An epic tracks business-unit progress, not engineering detail — it wants *this sub-ticket is complete*, not a per-AC breakdown. Pushing AC-level state upward recreates the child's own artifacts one level up, where they go stale the moment the child moves.

```markdown
<child-ticket-id>  done
<child-ticket-id>  blocked: <one line>
```

Three properties keep this safe:

- **Append-only, one line, at ticket end.** Two tickets in flight can never contend for the same line.
- **Never created.** No tracker file present → nothing is written and nothing is said. The tracker is opt-in, made by hand when an epic is worth tracking.
- **Read is unconditional, write is terminal.** Any stage may read the tracker to learn what the epic covers; only the final stage writes, and only that one line.

**Why not full ignorance.** A tracker sitting one directory up is context already on disk, and a session blind to it re-derives from `--human` what it could have read for free. Why not a live rollup: that is cross-ticket orchestration, which §1 defers, and it is how a parent file becomes a second source of truth about a child's state.

**Q6 — What goes in the PR body, and what does "reconcile the tracker" mean?** ~~(§3 stage 4)~~ — **RESOLVED.**

`pr-create` **drafts the body to `<ticket-id>-pr.md` before opening anything**, so the body is read while it is still cheap to change. The file stays in the ticket directory afterward as the record of what was claimed.

```markdown
## TL;DR
<one to three lines — a reviewer decides here whether to read on>

## What changed
## Why
## Acceptance criteria
AC-1  Given … When … Then …            [verified]
AC-2  …                                [skipped: <reason>]

## How it was verified
## Deliberately skipped
```

**Acceptance criteria are pasted verbatim, not summarised.** Q2 put the spec in a repository no reviewer can open, so the PR body is now the only place the intended behaviour appears. A summary would also break §6.2's spec axis, which quotes spec lines a reviewer must be able to check. §5.3's requirement — a skipped `verify` states its reason in the PR body — is carried by the `Deliberately skipped` section.

**The stage never touches the tracker.** It prints the updates the operator should make and stops:

```
Tracker updates for you:
  [ ] move <ticket-id> to In Review
  [ ] link this PR on the ticket
```

Automating this needs a tracker command from `CLAUDE.md`, which is the same tracker-shaped hole in the kernel that Q10 rejected, in the same document that says no such hole exists (§7.1). Naming the manual step honestly costs two lines of output and keeps the kernel true. *(Number retained — other documents cite "Q6".)*

**Q11 — On a repair invocation, does `--human` append or replace?** ~~(§7.2)~~ — **RESOLVED.**
**Append, dated.** Same argument as §5.5's `## Correction log`: what an instruction *used to be* is often the only thing that explains why the code looks the way it does, and a silent overwrite destroys that trail. A later entry may countermand an earlier one in words; it never deletes it from the record.

```markdown
## Human input
2026-08-14  Only reproduces on <version>; triage to that version only.
2026-08-15  Ignore the above — also reproduces on <other>. Widen the triage.
```

*(Number retained — other documents cite "Q11".)*

**Q12 — What serves as the control case on the first ticket in a repo?** ~~(§5.5)~~ — **RESOLVED.**
Fall back to the repo's own test suite, run with whatever command `CLAUDE.md` names, on a selection untouched by the change. Already red before the change → the environment is implicated and the pre-flight has done its job. Green → the environment is sound and triage proceeds.

Where `CLAUDE.md` documents no test command at all, the pre-flight is **unavailable**, and the stage says so in the artifact rather than skipping quietly:

> `Pre-flight unavailable: no test command documented in CLAUDE.md. The triage below is unverified.`

That sentence is the whole point of the fallback. A silent skip produces triage that *looks* the same as verified triage; a stated one tells the reader exactly how much weight the conclusion carries.

Two alternatives were rejected: asking the operator to confirm the environment is a claim the session cannot check, and authoring a throwaway trivial test proves only that the test runner starts — not that the database, the network, or the fixtures the real cases need are up. *(Number retained — other documents cite "Q12".)*

### Ambiguities — resolved

**Q7 + Q9 — When a stage needs the operator, does the session wait or exit?** ~~(§4, §5.2)~~ — **RESOLVED.** These were one question wearing two names.

**The split is by how long the operator is away, not by which stage is running.**

| Wait | Exit and get re-invoked |
|---|---|
| Answerable in seconds without leaving the keyboard | Requires leaving: running a manual checklist, waiting on an environment, asking another team |
| e.g. `impl` confirming a seam (§4) | e.g. `verify`'s manual E2E path when no tooling exists (§5.2) |

So `impl` **is** interactive, deliberately, at exactly one point: the seam confirmation. That checkpoint is cheap and in-flow, and paying a whole extra session for it would be worse than the interruption.

A stage that exits writes down precisely what it needs and how to return it, then stops. Results come back through `--human` on the next invocation, which §7.2 already files into the artifact verbatim:

```
Wrote <ticket-id>-qa-e2e.md — 6 cases. Run them, then:
  /harness-eng verify <ticket-id> --human "E2E-1..5 pass, E2E-6 fails: <what happened>"
```

**Why not one blanket rule.** *Always block* leaves a session open overnight with its context going stale against a world that moved. *Never block* charges a full cold session for a ten-second question. The cost that matters is the operator's attention, and it is not uniform across the two cases.

**Q8 — What happens when an input artifact is missing or malformed?** — **RESOLVED.** Fail fast, and say three things: which artifact is missing, the exact path it was looked for at, and the command that produces it. Never improvise a substitute, never proceed on a partial read. Same shape as Q10's `ticket.md` message:

> `No <ticket-id>-spec.md at <resolved-path>. Run /harness-eng spec <ticket-id> first.`

*(Numbers retained — other documents cite "Q7", "Q8", "Q9".)*
