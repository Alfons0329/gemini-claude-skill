# Specification: Harness Engineering — Phase 1 (Baseline Ticket Pipeline)

**Status:** Active — build target for this repo.
**Scope:** A single mid-level IC (~5 YoE) working tickets inside an existing codebase at a large company. Not a team-wide rollout, not a config-binding CLI, not cross-session orchestration — see `spec-phase-2.md` for that tier, deliberately deferred.

## 1. Why Phase 1 alone is enough at this level

The leverage for an IC at this level is entirely inside one ticket's lifecycle: spec it, implement it, verify it, get it reviewed, ship it, record what was learned. Nothing here requires:
- binding company-specific config dynamically (a "config seam"),
- merging into an existing team's workflow (`merge-harness`),
- managing context across long-running multi-week efforts (`handoff`, `bootcamp`),
- routing ambiguous requests to sub-skills (`harness-router`),
- owning backlog/roadmap ambiguity (`wayfinder`, `triage`).

Those are staff/tech-lead concerns — adopting them now would be building infrastructure for pain not yet felt, which the harness-engineering doctrine itself argues against (decide from a loop, not a hypothesis).

## 2. Attribution

- **`mattpocock/skills`** ([repo](https://github.com/mattpocock/skills), MIT licensed) — the TDD/seams discipline in §4 and the two-axis code review in §6. See `../NOTICE.md`.
- **Everything else is the author's own**, including the session-handoff artifact model (§3.1), the pipeline-invocation shape (§3.2), and the failure-triage table (§5.5). These are a from-memory reconstruction of a pipeline the author designed and ran daily for ~3 months, written as generic method only — no employer names, ticket identifiers, repository paths, internal URLs, or domain specifics.

## 2.1 Why this shape, and not a plausible-sounding alternative

Every decision below was run in anger for ~3 months on real tickets before being written down. Two in particular are counterintuitive enough that they'd likely be designed *out* of a from-scratch pipeline, and are here because practice demanded them:

- **`/ticket-verify` authors the E2E test, not `/ticket-impl`** (§5.2) — costs an extra cold session; the payoff is that the test can't inherit the implementer's blind spots.
- **A failing test triages three ways before anything is "fixed"** (§5.5) — the obvious design routes every red test into a code fix, which is precisely how a correct implementation gets edited until it satisfies a typo.

## 3. Pipeline Overview

```
SPEC ──> IMPL ──> VERIFY ──> PR-CREATE ──> PR-REVIEW (security-gated) ──> UPDATE-KB
```

| # | Stage | Command | Status |
|---|---|---|---|
| 1 | SPEC | `/spec-create` | unchanged — structured interview, produces `<ticket-id>-spec.md` |
| 2 | IMPL | `/ticket-impl` | **enhanced** — TDD-disciplined (§4) |
| 3 | VERIFY | `/ticket-verify` | **enhanced** — two-perspective verification + failure triage (§5) |
| 4 | PR-CREATE | `/pr-create` | unchanged — open the PR with a stakeholder-readable body, reconcile the tracker |
| 5 | PR-REVIEW | `/pr-review` | **enhanced** — security gate, then two-axis review (§6) |
| 6 | UPDATE-KB | `/kb-update` | unchanged — feedback loop writing learnings back to `docs/` |

**SEC-SCAN is no longer a standalone stage.** Security is a gate *inside* `/pr-review` (§6), because it needs exactly the artifact `/pr-review` already has — the full diff against a fixed point. A separate session would re-derive that same context to check one narrow axis. Its repair path stays named and distinct: `/ticket-impl <id> fix-sec` (§5.5).

### 3.1 Session boundaries

Each stage runs in its **own fresh session**. The only thing that crosses the boundary is whatever got committed to git — no session inherits another's reasoning or context. This is deliberate, not incidental: it's what makes `/ticket-verify`'s end-user pass trustworthy (§5.2) — it can't inherit `/ticket-impl`'s blind spots if it never saw `/ticket-impl`'s session in the first place.

```
You (boss) → pick a ticket → run /spec-create with interview grill
                                      ↓
                            spec.md committed to git
                                      ↓
                    new session reads spec → /ticket-impl
                                      ↓
                    code + qa.md + qa-e2e.md scaffold committed to git
                                      ↓
                    new session reads spec + qa.md + scaffold → /ticket-verify
                                      ↓
                         PASS → /pr-create → /pr-review → /kb-update
                         FAIL → document repro, fix loop (max 2x) → escalate to boss
```

**The artifact is the whole contract.** Each session commits its output and the next session reads those files *cold* — no shared memory, no "as we discussed earlier":

| Session | Produces |
|---|---|
| 1 — `/spec-create` | `<ticket-id>-spec.md` (spec + acceptance criteria + open questions) |
| 2 — `/ticket-impl` | code changes + `<ticket-id>-qa.md` (dev test plan) + `<ticket-id>-qa-e2e.md` (bare scaffold, §4) |
| 3 — `/ticket-verify` | `qa.md` filled with `Result:` lines + `qa-e2e.md` filled in and run (§5.2) |
| 4 — `/pr-create` | PR opened with a stakeholder-readable body; tracker reconciled |
| 5 — `/pr-review` | inline review comments + `<ticket-id>-security-review.md` if security findings |
| 6 — `/kb-update` | `docs/` updated in the target repo |

Because the contract is files rather than context, each stage can run in a **different session, a different model, or be picked up by a different engineer** — the artifacts carry everything needed.

### 3.2 Running the pipeline

Invoke each stage yourself, in a fresh session, passing the previous stage's committed artifact:

```bash
# Session 1 — generate the spec from the ticket
/spec-create <TICKET-ID>

# Optional — align on ambiguities before implementing
/interview-me <artifact-dir>/<ticket-id>-spec.md

# Session 2 — implement from the spec
/ticket-impl <TICKET-ID> <artifact-dir>/<ticket-id>-spec.md

# Session 3 — verify (dev pass, then E2E pass)
/ticket-verify <TICKET-ID> <artifact-dir>/<ticket-id>-qa.md

# Session 4 — open the PR (run manually; not auto-chained)
/pr-create <TICKET-ID> <artifact-dir>/

# Session 5 — review the PR once it's open
/pr-review <TICKET-ID> <artifact-dir>/ <pr-url>

# Session 6 — write learnings back (auto-triggered by /pr-review on PASS, or run manually)
/kb-update <TICKET-ID> <artifact-dir>/
```

Stages are **not auto-chained past verify** — you decide when to open the PR and when to review it. That's the point of acting as the boss: each transition is a checkpoint you can redirect at.

## 4. `/ticket-impl` — TDD discipline (from `implement` + `tdd`)

- **Seams first.** Before writing any test, name the public interfaces under test ("seams") and confirm them with the user. No test against internals, no test at an unconfirmed seam.
- **Red → green, one slice at a time.** One seam, one failing test, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **Refactoring is a separate step**, not part of the red→green loop — it happens at review time (§6), not mixed into implementation.
- **Anti-patterns to actively avoid** while writing tests:
  - *Implementation-coupled* — mocking internals, testing private methods, or asserting via a side channel instead of the public interface. Tell: it breaks on refactor even though behavior didn't change.
  - *Tautological* — the expected value is computed the same way the code computes it (so it can't disagree). Expected values must come from an independent source: a known-good literal, a worked example, the spec.
  - *Horizontal slicing* — writing all tests before any implementation. Do vertical slices instead: one test → one implementation → repeat.
- **Mechanical checks during implementation:** typecheck regularly, run the single relevant test file regularly, run the full suite once at the end.
- **Produce two verification artifacts alongside the code** (consumed by `/ticket-verify`, §5):
  - `<ticket-id>-qa.md` — the dev-perspective test plan: what was actually tested during red→green (the seams, the commands to re-run them). One case per acceptance criterion, each with an explicit `Setup:`, `Action:`, and `Expected:` block so a cold reader can execute it. Must also carry two fixed sections: `## Test Environment` (what has to be standing up — services, fixtures, config — for the cases to run at all) and an empty `## Correction log` table for §5.5.
  - `<ticket-id>-qa-e2e.md` — a **bare scaffold, not a test plan**. Name only *what screens/flow this ticket touches* (e.g. "the hello-world button on the home screen"). Do **not** write concrete steps, click order, or pass/fail assertions here — that decision belongs entirely to `/ticket-verify`'s fresh session (§5.2), specifically so the implementer can't unconsciously write an end-user test that's secretly shaped around what it already knows will pass.
- Commit to the current branch when done; hand off to `/ticket-verify` (§5).

## 5. `/ticket-verify` — two-perspective verification, then structured diagnosis on failure

Renamed from `ticket-qa`: "QA" in a command name reads as "Question & Answer" at a glance — this stage runs no interview, it verifies. (Artifact filenames keep the industry-standard `-qa`/`-qa-e2e` suffix since "Quality Assurance" is unambiguous in that context.)

### 5.1 Why two perspectives

One test perspective isn't enough, because the two catch different failure classes:

- **Dev perspective (API/integration level)** — stand up the local stack and its dependent services, then exercise the change directly (`curl`, an RPC client, a test runner hitting the seam). Fast, deterministic, close to the code. Blind to anything that only breaks in the actual client (wrong event binding, a CSS layer eating the click, a JS error the API layer never sees).
- **End-user perspective (E2E/UI level)** — drive the real client the way a person actually would (browser automation clicking the real button, a mobile driver tapping the real screen). Catches what the API-level check can't see, but is slower and shouldn't be the only signal either — a person could recreate correct-looking behavior on top of a broken or accidentally-right contract.

**Worked example** — a hello-world fullstack app where pressing a button echoes "Hello, World" (illustrative — swap `curl` for whatever seam actually fits the ticket: an RPC call, a queue message, a CLI invocation):
- *Dev perspective*: run the local dev stack (frontend + backend + whatever it depends on), then `curl -X POST localhost:PORT/api/echo` and assert the JSON body is `{"message": "Hello, World"}`. This verifies the *contract*, not the button.
- *End-user perspective*: open the actual running app in a browser, click the actual button element, assert the DOM now renders the text "Hello, World". This is the only check that would catch, say, the button's `onClick` never being wired up even though the `/api/echo` endpoint is flawless — a real end user never runs `curl` from their client.

A real user only ever exercises the second one. Shipping on the first alone is checking the contract, not the product.

### 5.2 Ownership split — why `/ticket-verify` authors the E2E test, not `/ticket-impl`

`/ticket-impl` is not trusted to decide what "correct from a user's perspective" means, because it can unconsciously write an E2E test shaped around what it already knows will pass — the same blind spot code review avoids by never letting one axis see the other's reasoning (§6). So authorship of the real E2E test is split from authorship of the code:

- `/ticket-impl` may only name *what flow* is touched (the bare scaffold, §4) — never the concrete steps or assertions.
- `/ticket-verify` runs in a session that never saw `/ticket-impl`'s reasoning (§3.1) — only the committed spec, code, `qa.md`, and the scaffold. From that, it independently writes the actual clickable steps and assertions and treats the acceptance criteria in `<ticket-id>-spec.md` as the source of truth for what "correct" means — not the scaffold's suggestions, and not the implementation's behavior.

**If no E2E automation tooling exists in the target repo** (no Playwright/Cypress/equivalent), don't fake it or skip it silently: write the filled-in steps as a **manual checklist** for the boss to execute and confirm, and say so explicitly in the report.

### 5.3 Sequencing within `/ticket-verify`

`/ticket-verify` does not report VERIFY as passed until **both** passes are green, in this order:

1. **Dev pass** — run `<ticket-id>-qa.md` (produced by `/ticket-impl`, §4) against the local stack. Fast feedback first.
2. **E2E pass** — only once the dev pass is green, write the real steps into `<ticket-id>-qa-e2e.md` per §5.2 and run them (or hand the manual checklist to the boss).

If either pass fails, don't guess — classify it (§5.5) and, if it's a code bug, run the diagnosis discipline (§5.4) before forming any hypothesis.

**Skipping VERIFY entirely** is allowed for changes with no user-facing or E2E surface where you judge unit coverage sufficient — the flow becomes `/ticket-impl → /pr-create → /pr-review`. The one condition: **the skip is never silent.** State the reason in the PR body so a reviewer sees that verification was consciously waived rather than forgotten.

### 5.4 Structured diagnosis on failure (from `diagnosing-bugs`)

When either pass fails and the cause isn't obvious:

1. **Build a feedback loop first.** A tight, deterministic, fast, agent-runnable command that goes red on this exact bug (failing test, curl against dev server, CLI + fixture diff, replayed trace, bisection harness — in roughly that order of preference). This step is the actual skill; everything after is mechanical. If you can't build one, stop and say so explicitly rather than theorizing.
2. **Reproduce, then minimize** the repro to the smallest scenario that still goes red — cut one variable at a time, re-running after each cut.
3. **Generate 3–5 ranked, falsifiable hypotheses** before testing any of them ("if X is the cause, changing Y makes it disappear"). Show the ranked list to the user before testing — they may re-rank instantly from context you don't have.
4. **Instrument** — one probe per hypothesis, one variable at a time. Prefer a debugger/REPL over logs; tag any debug log with a unique prefix (`[DEBUG-xxxx]`) so cleanup is one grep.
5. **Fix + regression test** — write the regression test before the fix, but only at a seam that exercises the real bug pattern; a shallow seam gives false confidence. If no correct seam exists, that absence is itself a finding to flag.
6. **Cleanup + postmortem** — confirm the original repro no longer reproduces, all `[DEBUG-...]` logs are removed, throwaway harnesses are deleted, and the correct hypothesis is stated in the commit/PR message.

### 5.5 Triaging a failure — is the code wrong, or is the doc wrong?

A `FAIL` does not automatically mean the implementation is broken. `/ticket-impl` wrote the test cases, so the case itself can be wrong. **Classify the failure before fixing anything** — routing a bad test case into a code-fix loop is how a correct implementation gets "fixed" until it matches a wrong expectation:

| Failure type | What it means | Who fixes it | How |
|---|---|---|---|
| **Code bug** | The implementation doesn't do what the acceptance criterion says | the impl session | route back: `/ticket-impl <id> fix-qa` (bounded — §5.6) |
| **Wrong assertion** | The `Expected:` value in the QA case is itself incorrect | you (human) | edit `Expected:` in the case, add a `## Correction log` row, re-run `/ticket-verify` |
| **Wrong test step** | The `Setup:` or `Action:` block is incorrect — the impl session wrote the test wrong | you (human) | edit the `Setup:`/`Action:` block, add a `## Correction log` row, re-run `/ticket-verify` |

> **The rule:** `fix-qa` means *"the code is wrong."* Editing the QA doc means *"the doc is wrong."* Never use `fix-qa` to paper over a bad assertion or a bad test step — that silently rewrites working code to satisfy a typo.

**Who writes what in `qa.md`** — the two halves have different owners, and mixing them destroys the audit trail:

- `/ticket-verify` writes the `Result:` lines. Never hand-edit those.
- You write `## Correction log` rows, recording what was wrong and what you changed.

```
| Date       | Case    | What was wrong                  | Correction                    |
|------------|---------|---------------------------------|-------------------------------|
| 2026-08-01 | Case 03 | Setup used the wrong fixture path | Pointed it at ./fixtures/v2/ |
```

A future reader then sees both the original expectation and why it moved, instead of a doc that quietly always agreed with the code.

**Scope of `fix-qa`:** it belongs to the `/ticket-impl ↔ /ticket-verify` loop only, and that loop must close *before* a PR is opened. Correctness findings raised later in `/pr-review` (§6) do **not** re-enter `fix-qa` — you address the comment and re-push. The only named repair loop that starts from review is a **security** finding: `/ticket-impl <id> fix-sec`.

### 5.6 Bounded retry & escalation

The `fix-qa` loop is not allowed to run indefinitely. On a failure classified as a **code bug**:

1. **Document the reproduction step first** — the tight, red-capable command from §5.4 phase 1, committed to the ticket's working notes, before attempting any fix.
2. **Run the fix loop at most twice.** Each attempt is one full pass through §5.4 phases 3–5 (hypothesize → instrument → fix). Two failed attempts is the cap — not two hypotheses within one attempt.
3. **Escalate, don't spin.** If VERIFY still fails after 2 attempts, stop. Report back to the boss with: the documented repro, both attempts and why each didn't hold, and the current ranked hypothesis list. Wait for direction rather than continuing to guess — the same "recommend and wait" principle `spec-phase-2.md` names for anything touching decisions beyond the session's own scope.

## 6. `/pr-review` — security gate, then two-axis review

### 6.1 Security gate (runs first)

Before the two axes below, scan the same diff for security defects only — injection, authn/authz gaps, credential or PII exposure in logs and errors, unsafe deserialization, missing input validation at trust boundaries. Keep it narrow: this is not a code-quality pass, and quality findings belong to §6.2.

A finding here **blocks the PR** and writes `<ticket-id>-security-review.md`. It is the one review finding with a named repair loop back into implementation: `/ticket-impl <id> fix-sec`. Everything else in §6.2 is addressed by editing and re-pushing, not by re-entering a repair mode (§5.5).

### 6.2 Two-axis review (from `code-review`)

Review the diff between a fixed point (a commit/branch/tag the user names, or `main` by default) and `HEAD`, along **two independent axes**, each run as a **parallel sub-agent** (`Agent` tool, `general-purpose` type, one message with both calls) so neither pollutes the other's context:

- **Standards axis** — does the diff conform to this repo's documented standards (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, etc.), *plus* a fixed Fowler smell baseline that applies even when the repo documents nothing: Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality, Message Chains, Middle Man, Refused Bequest. A documented repo standard always overrides the baseline. Baseline smells are always judgement calls; documented-standard breaches can be hard violations.
- **Spec axis** — does the diff faithfully implement the originating ticket/spec? Report missing/partial requirements, scope creep, and requirements that look implemented but are wrong — quoting the spec line for each finding.

Report the two axes under separate headings, never merged or re-ranked against each other — a change can legitimately pass one axis and fail the other (e.g. correct behavior that breaks conventions, or clean code that does the wrong thing).

## 7. Directory Structure

```
productivity/harness-eng/
├── spec.md                    # index — links here and to spec-phase-2.md
├── spec-phase-1.md            # this document
├── spec-phase-2.md            # deferred kernel, not being built now
├── NOTICE.md                  # attribution to mattpocock/skills (MIT)
└── phase-1/
    ├── spec-create/SKILL.md
    ├── ticket-impl/SKILL.md    # §4
    ├── ticket-verify/SKILL.md  # §5
    ├── pr-lifecycle/SKILL.md   # /pr-create + /pr-review (§6)
    └── kb-update/SKILL.md
```

No installer CLI, no `--phase`/`--overwrite`/`--global` flags, no config seam. These are plain `SKILL.md` files following this repo's existing convention (frontmatter `name`/`description`, phased workflow) — installed the same way as every other skill here. That machinery only earns its keep at the Phase 2 scale (binding many companies' specifics to one portable kernel), which is out of scope here.

## 8. Handover Checklist

- [ ] Write `phase-1/spec-create/SKILL.md` — unchanged from the original inventory description; delegates to `interview-me` for the interview mechanics.
- [ ] Write `phase-1/ticket-impl/SKILL.md` implementing §4 verbatim as its workflow, including producing both `-qa.md` (with `## Test Environment` + empty `## Correction log`) and the `-qa-e2e.md` scaffold, plus the `fix-qa` and `fix-sec` repair modes.
- [ ] Write `phase-1/ticket-verify/SKILL.md` implementing: independent E2E authorship (§5.2), dev-pass-then-e2e-pass sequencing and the documented-skip escape hatch (§5.3), six-phase diagnosis (§5.4), failure triage and `## Correction log` ownership (§5.5), and the bounded-retry/escalation cap (§5.6).
- [ ] Write `phase-1/pr-lifecycle/SKILL.md` with `/pr-create` unchanged, and `/pr-review` implementing the §6.1 security gate (blocking, writes `-security-review.md`, repairs via `fix-sec`) followed by §6.2's two-axis parallel-subagent review.
- [ ] Write `phase-1/kb-update/SKILL.md` — unchanged.
- [ ] Write `NOTICE.md` at `productivity/harness-eng/` crediting `mattpocock/skills` (MIT) for the techniques in §4 and §6.
- [ ] Rewrite `spec.md` as a short index pointing to this file and `spec-phase-2.md`, with no personal Notion links.

## 9. Open Questions

**Close these before writing any `SKILL.md`.** Each carries a recommended default; resolving one means confirming or overriding it, then folding the answer into the section named and deleting the item here.

### Blocking — a skill cannot be written without these

**Q1 — What is the spec template, and what shape is an acceptance criterion?** (§3 stage 1, §8 item 1)
`/spec-create` is the only stage with no written spec, yet three later stages depend on its output shape: `qa.md` is one case per AC (§4), `/ticket-verify` treats AC as the source of truth for "correct" (§5.2), and `/pr-review`'s spec axis quotes spec lines (§6.2). Undefined AC format means the pipeline's central contract is undefined. Also unresolved: where ticket text comes from (tracker API / pasted text / URL), and what "open questions" means operationally in a generated spec.
*Recommended default:* AC as numbered, individually testable `Given/When/Then` statements — numbered so `qa.md` cases and `/pr-review` findings can cite `AC-3` unambiguously.

**Q2 — Where do ticket artifacts live?** (§3.1, §3.2 `<artifact-dir>`)
§3.1 makes "committed to git" the contract but never says which repo or path. If artifacts live in the target repo they appear in the PR diff; if they live elsewhere, "committed" needs redefining.
*Recommended default:* a per-ticket directory inside the target repo (e.g. `.harness/<ticket-id>/`), committed on the feature branch — it travels with the code, and reviewers can see the spec and QA plan alongside the diff.

**Q3 — Where do skills read project conventions from?** (§4)
§4 tells the impl session to "typecheck regularly, run the single relevant test file" — but nothing says how a cold session learns the build command, test command, branch naming, or commit format.
*Recommended default:* read `CLAUDE.md` in the target repo's root (with `GEMINI.md` / `AGENTS.md` as fallbacks for other agents). This is the one piece of config-binding Phase 1 genuinely needs, and it is free — the file already exists in most repos and `/init` generates it.

**Q4 — What is the repair-mode invocation syntax?** (§5.5, §6.1 vs §3.2)
§5.5 writes `/ticket-impl <id> fix-qa`; §3.2 writes `/ticket-impl <TICKET-ID> <artifact-dir>/<ticket-id>-spec.md`. Is the mode a third positional argument, or does it replace the spec path?
*Recommended default:* a trailing optional mode token — `/ticket-impl <id> <spec-path> [fix-qa|fix-sec]` — so the spec path is always present and the mode is additive.

### Would produce a vague skill if left open

**Q5 — What does `/kb-update` actually write?** (§3 stage 6, §8 item 5)
No spec exists: what counts as a learning worth recording, where under `docs/` it lands, and how it avoids re-stating what the repo already documents. Also an inconsistency — §3.2 says it is auto-triggered by `/pr-review` on PASS, but §6 never mentions triggering it.
*Recommended default:* append-only entries under `docs/learnings/`, one file per ticket, and record only what was *non-obvious* — a wrong assumption corrected, a convention discovered, a trap for the next engineer. Never restate what the diff already shows.

**Q6 — What goes in the PR body, and what does "reconcile the tracker" mean?** (§3 stage 4)
§5.3 requires a skipped VERIFY to state its reason *in the PR body*, so body structure is load-bearing. "Reconcile the tracker" is also the least portable instruction in Phase 1 — it is precisely the binding that `spec-phase-2.md`'s config seam exists to solve, deliberately absent here.
*Recommended default:* a fixed body template (what changed / why / how it was verified / anything deliberately skipped, with reason), and tracker reconciliation stated as an explicit manual step for Phase 1 rather than automated — naming the Phase 2 gap instead of pretending it is generic.

### Ambiguities — one sentence each will do

**Q7 — Is `/ticket-impl` interactive?** §4 says seams are "confirmed with the user," which is the only human checkpoint inside an otherwise autonomous stage. Is that deliberate, and does the session block on it?
**Q8 — What happens when an input artifact is missing or malformed?** A cold `/ticket-verify` invoked before impl committed needs a defined fail-fast behavior rather than improvising.
**Q9 — How does the manual-checklist path hand off?** (§5.2) When no E2E tooling exists, the boss executes the checklist — does the session block and wait for results, or exit and get re-invoked with them?
