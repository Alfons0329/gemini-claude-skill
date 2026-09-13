# `impl` — laziest solution first, then TDD discipline

Reads `<id>-spec.md`, and `<id>-rca.md` too on a bug ticket. On a bug ticket the **confirmed mechanism is the RCA's, not the spec's suspicion**, and any criteria under its *Fix verification tied to this RCA* section bind exactly as the spec's own acceptance criteria do.

## The gate: every open gap is closed first

**Before the ladder, before any code**, read `<id>-spec.md`'s `## Open gaps`. Every entry must carry a ruling. Any entry still open stops this stage in the fail-fast shape SKILL.md defines — nothing is written, no rung is climbed:

```
GAP-2 still open in <ticket-id>-spec.md: "<the one-line title>"
Close it with the decider, then record the ruling in ## Open gaps and re-run.
```

A gap is parked precisely because it is somebody else's call — a product rule, a legal constraint, a cross-team trade-off. Building past one means guessing at that call and burying the guess in code, where it looks like a decision somebody made. The cost of stopping is a message; the cost of guessing is a rewrite after launch.

**This gate is `impl`'s alone.** `rca` runs unblocked: root-causing needs no ruling, and what it turns up is often exactly the evidence that closes a gap.

## Before writing any code: climb the ladder

Understand the problem and trace the real flow first, then take the first rung that holds and stop:

1. Does this need to be built at all?
2. Does it already exist in this codebase? Reuse the helper or pattern that's already here.
3. Does the standard library do it?
4. Does a native platform feature cover it?
5. Does an already-installed dependency solve it?
6. Can it be one line?
7. Only then: write the minimum code that works.

No abstraction that wasn't asked for, no new dependency that can be avoided, deletion over addition, boring over clever, fewest files possible. The shortest working diff wins — **but only once the problem is understood**; a small change in the wrong place isn't lazy, it's a second bug.

**Not lazy about:** understanding the problem, input validation at trust boundaries, error handling that prevents data loss, security, accessibility, or anything explicitly requested.

**Mark a deliberate shortcut** when a rung is taken that cuts a real corner with a known ceiling:

```
// ponytail: single global lock, fine under ~100 req/s. Swap for a per-key
// mutex if throughput grows.
```

`kb-update` harvests these into a ledger — leave the marker rather than letting the deferral rot into "later means never."

## The ladder and TDD run at different moments

The ladder decides *whether code gets written*; TDD governs *how code that must exist gets written*. If rung 2 holds, there's no new code and so no test to write. Everything below applies from rung 7 onward.

1. **Seams first — the one blocking checkpoint.** Before writing any test, name the public interfaces under test and confirm them with the operator. This is answerable in seconds without leaving the keyboard, so per SKILL.md's "Waiting vs. exiting" the session **waits in-session** for this one. No test against internals, no test at an unconfirmed seam.
2. **Red → green, one slice at a time.** One seam, one failing test, then only enough code to pass it. Don't anticipate future tests or add speculative features.
3. **Refactoring is a separate step**, not part of the red→green loop — it happens at review time, in `pr-review`'s standards axis (`reference/pr-lifecycle.md`, "Three-axis review"), not mixed into implementation.
4. **Anti-patterns to actively avoid** while writing tests:
   - *Implementation-coupled* — mocking internals, testing private methods, asserting via a side channel instead of the public interface. Tell: it breaks on refactor even though behavior didn't change.
   - *Tautological* — the expected value is computed the same way the code computes it, so it can't disagree. Expected values come from an independent source: a known-good literal, a worked example, the spec.
   - *Horizontal slicing* — writing all tests before any implementation. Do vertical slices instead: one test → one implementation → repeat.
5. **Mechanical checks during implementation:** typecheck regularly, run the single relevant test file regularly, run the full suite once at the end. Use the test command the project context file documents; **if it documents none, ask the operator for it once rather than guessing a runner** — a wrong guess produces a false green or a false red before any real work has happened.

## The two verification artifacts

Produced alongside the code, for `verify` to consume:

- **`<id>-qa.md`** — the dev-perspective test plan: what was actually tested during red→green. One case per acceptance criterion, each with an explicit `Setup:`, `Action:`, `Expected:` block a cold reader can execute. Two fixed sections are mandatory:
  - `## Test Environment` — **checkable preconditions, not prose.** Each precondition pairs with the command that confirms it, so `verify`'s pre-flight has something to run rather than something to read. Name which existing case serves as the **control case** for that pre-flight — it must predate this ticket and not touch the change.
  - `## Correction log` — an empty table, header only. `verify` never writes here; only the operator does, when a case's `Expected:`/`Setup:`/`Action:` turns out to be wrong (`reference/ticket-verify.md`).
- **`<id>-qa-e2e.md`** — a **bare scaffold, not a test plan.** Name only *what screens or flow this ticket touches* (e.g. "the hello-world button on the home screen"). Do **not** write concrete steps, click order, or pass/fail assertions — that decision belongs entirely to `verify`, specifically so this session can't unconsciously write an end-user test shaped around what it already knows will pass.

Commit code and both artifacts to the target repo's feature branch when done, then stop per SKILL.md's "One stage, one session" — hand off to `verify`.

## Repair mode: `fix-qa`

Entered as `/loop-eng impl <id> fix-qa`, only from `verify`'s classification of a failure as a **code bug** (`reference/ticket-verify.md`, "Triaging a failure") — never for an environment failure or a bad QA case, and never after a PR is already open (SKILL.md, "Repair-mode scope").

**The test plans are frozen here** — SKILL.md, "The artifact contract." Change the code until the cases pass and add regression tests in the target repo; the three QA plans come out of this session byte-identical. A case that is genuinely wrong is the operator's to correct through the `## Correction log`, which is also the record of why it moved.

`verify` already built the tight, discriminating repro and handed it forward. This mode runs the rest of the diagnosis, bounded at **2 attempts** (SKILL.md, "Escalation"):

1. Read the repro `verify` documented and the ranked hypothesis list it produced.
2. **One attempt = one pass**: pick the top untested hypothesis, instrument one probe for it (prefer a debugger/REPL over logs; tag any debug log `[DEBUG-xxxx]` for one-grep cleanup), then fix and write the regression test *before* the fix — but only at a seam that exercises the real bug pattern. If no correct seam exists, flag that absence as a finding rather than accepting a shallow one.
3. **Cleanup before handing back**: confirm the original repro no longer reproduces, remove every `[DEBUG-...]` log and throwaway harness, and state the confirmed hypothesis in the commit message.
4. If this attempt doesn't hold, that's one of the two — re-rank the remaining hypotheses (the operator may re-rank instantly from context this session doesn't have) and either try again or, at 2 failed attempts, stop and report the repro, both attempts, and the current ranked list per SKILL.md's escalation table. Don't attempt a third.

## Repair mode: `fix-sec`

Entered as `/loop-eng impl <id> fix-sec`, only from a `pr-review` security-gate finding (`reference/pr-lifecycle.md`, "The security gate (runs first)"). This is the one place a stage reads `<id>-security-review.md` directly — a record everywhere else, but here it's the sole record of the specific finding this invocation exists to repair, not general pipeline context. Implement the fix, note it in the commit, and hand back to `pr-review` for re-review — there's no separate retry cap named for this path; a security finding is fixed once and re-checked, not iterated against a hypothesis list.

## Done when

- `## Open gaps` carried a ruling on every entry before the first rung was climbed.
- The ladder was climbed and the rung actually stopped at is named, even if it's rung 7.
- Any deliberate shortcut carries a `ponytail:` comment naming the ceiling.
- The seam list was confirmed with the operator before the first test was written.
- `<id>-qa.md` has one case per acceptance criterion, a checkable `## Test Environment` with a named control case, and an empty `## Correction log`.
- `<id>-qa-e2e.md` names a flow, not steps or assertions.
- On `fix-qa`, the attempt count never exceeds 2, escalation happened exactly at the cap, and all three QA plans are unchanged.
