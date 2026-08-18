# `verify` — two-perspective verification, then structured diagnosis on failure

Renamed from `ticket-qa`: "QA" in a command name reads as "Question & Answer" at a glance, and this stage runs no interview — it verifies. (Artifact filenames keep the industry-standard `-qa`/`-qa-e2e` suffix; "Quality Assurance" is unambiguous there.)

Reads `<id>-spec.md`, `<id>-rca.md` on a bug ticket, `<id>-qa.md`, and the `<id>-qa-e2e.md` scaffold — never `impl`'s session or reasoning, only what it committed (SKILL.md, "One stage, one session"). Runs in this order: environment pre-flight, dev pass, E2E pass. VERIFY isn't reported PASS until both passes are green.

**The escape hatch.** A change with no user-facing or E2E surface, where unit coverage is judged sufficient, may skip this stage entirely — the flow becomes `impl → pr-create → pr-review`. The one condition: the skip is **never silent**. `pr-create` states the reason in the PR body, so a reviewer sees verification was consciously waived, not forgotten.

## 1. Environment pre-flight

Before trusting any result below, confirm the loop that's about to run is actually measuring the code and not a broken machine.

Run the **control case** named in `<id>-qa.md`'s `## Test Environment` section — any case that predates this ticket and doesn't touch the change.

- **Control passes** → the environment is sound; the change is implicated. Continue to the dev pass.
- **Control fails too** → the environment is implicated and nothing about the diff is in evidence. Stop here — zero retries, per SKILL.md's "Escalation" table. Report the unmet precondition and its evidence.

Also confirm the control case can still **fail** on demand — a suite that can't go red is not evidence of anything, and a misconfigured environment can produce a false green as easily as a false red (a stale or mocked service answering for the real one).

**First ticket in a repo — no control case exists yet.** Fall back to the repo's own test suite, run with whatever command the project context file names, on a selection untouched by the change. Already red before the change → the environment is implicated and the pre-flight has done its job. Green → sound, proceed.

**If the project context file documents no test command at all**, the pre-flight is unavailable — say so in `<id>-verify-trace.md` rather than skipping quietly:

> `Pre-flight unavailable: no test command documented in the project context file. The triage below is unverified.`

A silent skip would produce triage that *looks* verified and isn't; a stated one tells the reader exactly how much weight the conclusion carries.

## 2. Dev pass

Run every case in `<id>-qa.md` against the local stack — the API/integration level: `curl`, an RPC client, a test runner hitting the seam directly. Fast, deterministic, close to the code, but blind to anything that only breaks in the real client.

**`verify` writes the `Result:` line for each case, directly into `<id>-qa.md`.** Never hand-edit those lines — they're this stage's own output, the same way `Setup:`/`Action:`/`Expected:` are `impl`'s.

Don't proceed to the E2E pass until every dev-pass case is green (or explicitly triaged per step 4).

## 3. E2E pass

Only once the dev pass is green. Drive the real client the way a person actually would — the check the dev pass structurally can't perform, because a real user never runs `curl` from their client.

**This session authors the actual steps, independently.** `impl`'s scaffold names only *what flow* is touched; it never saw this session's reasoning and this session never saw `impl`'s. Write the concrete clickable steps and assertions from `<id>-spec.md`'s acceptance criteria — plus, on a bug ticket, the criteria `<id>-rca.md` added under *Fix verification tied to this RCA* — as the source of truth for what "correct" means. Not the scaffold's suggestions, not the implementation's own behavior.

**If no E2E automation tooling exists in the target repo**, don't fake it and don't skip it silently: write the filled-in steps as a **manual checklist** for the operator to execute by hand.

A checklist takes hours or days, so per SKILL.md's "Waiting vs. exiting," **this session exits rather than waiting.** Name exactly how to return the results:

```
Wrote <ticket-id>-qa-e2e.md — 6 cases. Run them, then:
  /loop-eng verify <ticket-id> --human "E2E-1..5 pass, E2E-6 fails: <what happened>"
```

The returned text lands verbatim in the artifact per SKILL.md's `--human` rules, so the next invocation has the results in writing.

## Evidence: `<id>-verify-trace.md`

Both passes write their evidence here as they run — each case, the command, the output, the acceptance criterion it maps to — plus the control case and its verdict. A triage ruling with no record behind it can be believed but not reviewed; this file is what makes it reviewable. It's a record, never read back in as pipeline input (SKILL.md, "The artifact contract") — written for a human, once.

## 4. Triaging a failure

**A `FAIL` does not automatically mean the implementation is broken.** Classify before fixing anything — routing a bad test case into a code-fix loop is how correct code gets "fixed" until it matches a wrong expectation. The pre-flight above already separates *environment* from *the other three*; if it passed, triage among what's left:

| Failure type | What it means | Who fixes it | How |
|---|---|---|---|
| **Environment** | Pre-flight caught it — see step 1 | operator | fix the unmet precondition; zero retries |
| **Code bug** | The implementation doesn't do what the acceptance criterion says | the `impl` session | `/loop-eng impl <id> fix-qa` — bounded, see `reference/ticket-impl.md` |
| **Wrong assertion** | The `Expected:` value in the case is itself incorrect | operator | edit `Expected:` in `<id>-qa.md`, add a `## Correction log` row, re-run `verify` |
| **Wrong test step** | The `Setup:`/`Action:` block is wrong — `impl` wrote the test wrong | operator | edit the block, add a `## Correction log` row, re-run `verify` |

A failure signature corroborates but never decides on its own: an environment failure typically dies *before* the assertion (connection refused, auth rejected, missing binary or config, timeout); a code bug reaches the assertion and returns the wrong value.

**`fix-qa` means "the code is wrong."** Editing `<id>-qa.md` means "the doc is wrong." Never route a bad assertion or a bad test step into `fix-qa` — that silently rewrites working code to satisfy a typo.

**Who writes what in `<id>-qa.md`:** `verify` writes `Result:` lines only. The operator writes `## Correction log` rows — what was wrong, what changed:

```markdown
| Date       | Case    | What was wrong                    | Correction                     |
|------------|---------|------------------------------------|---------------------------------|
| 2026-08-01 | Case 03 | Setup used the wrong fixture path | Pointed it at ./fixtures/v2/   |
```

A future reader then sees the original expectation and why it moved, instead of a doc that quietly always agreed with the code.

## Building the discriminating repro (diagnosis phases 1–2)

When a failure is classified **code bug** and the cause isn't obvious, this session — not `fix-qa` — does the first two phases of structured diagnosis, because they're what the classification itself depends on:

1. **Build a feedback loop first**: a tight, deterministic, fast, agent-runnable command that goes red on this exact bug — failing test, `curl` against the dev server, CLI + fixture diff, replayed trace, bisection harness, in roughly that order of preference. **The loop must discriminate, not merely go red** — one that's also red on the control case is measuring the environment, not the bug, and confirms every hypothesis equally. If a discriminating loop can't be built, stop and say so rather than theorizing.
2. **Reproduce, then minimize** to the smallest scenario that still goes red — cut one variable at a time, re-running after each cut.

Document this repro in the ticket's working notes and hand off:

```
VERIFY: AC-4 red, classified as a code bug. Repro documented. Run:
  /loop-eng impl <ticket-id> fix-qa
```

Phases 3–6 (hypothesize, instrument, fix, cleanup) belong to `fix-qa` — see `reference/ticket-impl.md` — because each `fix-qa` attempt re-does hypothesis ranking against what the previous attempt disproved, and that's implementation work, not verification work.

## Retry budgets

Zero for environment, two for a code bug, both defined once in SKILL.md's "Escalation" — this stage doesn't repeat them, only triggers them via the table above.

## Done when

- The pre-flight ran before any other result was trusted, and its outcome (including "unavailable") is in `<id>-verify-trace.md`.
- The dev pass is fully green before the E2E pass starts.
- The E2E steps were written from the spec's (and, on a bug, the RCA's) acceptance criteria — not copied from the scaffold or reverse-engineered from what the app already does.
- Every case's evidence — command, output, mapped AC — is in `<id>-verify-trace.md`, including the control case's verdict.
- Every `FAIL` was classified into exactly one of the four rows before anything was fixed or edited.
- `<id>-qa.md`'s `Result:` lines were written by this stage; any `## Correction log` row was not.
