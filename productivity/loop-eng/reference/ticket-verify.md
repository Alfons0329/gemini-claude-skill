# `verify` — three-pass verification, then structured diagnosis on failure

Renamed from `ticket-qa`: "QA" in a command name reads as "Question & Answer" at a glance, and this stage runs no interview — it verifies. (Artifact filenames keep the industry-standard `-qa` prefix; "Quality Assurance" is unambiguous there.)

Reads `<id>-spec.md`, `<id>-rca.md` on a bug ticket, `<id>-qa.md`, and the `<id>-qa-e2e.md` scaffold — never `impl`'s session or reasoning, only what it committed (SKILL.md, "One stage, one session"). Runs in this order: **author the adversarial cases, environment pre-flight, dev pass, adversarial pass, E2E pass.** VERIFY isn't reported PASS until all three passes are green.

**The three QA plans divide along two axes**, and the new one shares a layer with `impl`'s plan and an author with the end-user plan:

| | Layer | Author | Asks |
|---|---|---|---|
| `<id>-qa.md` | the seam — `curl`, an RPC client, a test runner | `impl` | does the contract hold on the path it was built for? |
| `<id>-qa-adv.md` | the seam, same as above | `verify`, blind | can the contract be broken? |
| `<id>-qa-e2e.md` | the real client — a browser, a device | `verify`, blind | is it right for the person using it? |

The adversarial pass is not browser-level chaos. It presses the same seam the dev pass does, from a source that never saw the dev pass.

**The escape hatch.** A change with no user-facing or E2E surface, where unit coverage is judged sufficient, may skip this stage entirely — the flow becomes `impl → pr-create → pr-review`. The one condition: the skip is **never silent**. `pr-create` states the reason in the PR body, so a reviewer sees verification was consciously waived, not forgotten. There is no partial skip: a `verify` that runs, runs all three passes.

## 0. Author the adversarial cases — blind

**First, before anything else.** `<id>-qa.md` holds `impl`'s judgement about what is worth checking, and reading it first anchors this session on exactly the blind spot it exists to catch. The pre-flight's control case lives inside that file, so authoring has to come before even that.

The line is not the code — it's `impl`'s test plan. Code names the shape of the seam, and a case that can't name the endpoint can't call it. So authoring runs in two layers:

**Layer 1 — intent.** Reads `<id>-spec.md` (and `<id>-rca.md` on a bug ticket), including its `## Non-goals`. Reads no code and no `<id>-qa.md`. Each case names the criterion it presses, the condition, and the expected behaviour. Write them to `<id>-qa-adv.md` and commit — that commit is the line, crossed once.

**Layer 2 — command.** Now the code and the project context file are open, and each intent becomes something executable. Intents are frozen here: a case that turns out unrunnable — no tooling, no environment — is recorded `Result: not run` with the reason, **never deleted**. Deletion at this step is how every inconvenient case quietly evaporates and the pass goes green again.

### Where the cases come from

Five buckets, swept every run:

1. **Contract violations** — malformed payload, missing required field, wrong type at the seam.
2. **Boundary** — empty, zero, maximum, negative, unicode, off-by-one, **null or uninitialized**.
3. **State & concurrency** — the same request twice, an illegal state transition, interruption mid-flight, timeout.
4. **Resource failure** — a dependency down, slow, or returning an error.
5. **Persistence & side effect** — it returned success: did the write land? does it survive a restart? what does a half-completed write leave behind? The other four ask what happens when input is strange; this one asserts the effect rather than the return value.

Then one question per acceptance criterion, which reaches further than any fixed list:

> What assumption does this criterion rest on such that, if it were false, the criterion would produce a **silently wrong answer** rather than an error?

Loud failures get found. A crash is a gift; a plausible wrong value ships. The question is anchored to a criterion, so it cannot wander outside scope, yet it reaches classes no checklist anticipated.

### `Expected:` comes from an independent source

Generating a case is not the same as being able to fail it. Every `Expected:` value is written in Layer 1 from the spec's own words, a known-good literal, or a worked example — **never by running the code and recording what came back**. A case whose expected value was read off the implementation agrees with it by construction and is green forever, which is precisely the tautological anti-pattern `reference/ticket-impl.md` already bars for `<id>-qa.md`.

Where the spec never says what the right answer is, this session doesn't know either — that's a **spec gap** (step 4), not something to guess at.

### The scope guard

**Every case cites the acceptance criterion or non-goal it presses.** A case citing neither is out of scope and is dropped at authoring, before it is ever written down.

This is what keeps an adversary from demanding split-brain handling from a hand-run shell script, and it is also what makes a rejected case stay rejected: once a behaviour is written into `## Non-goals`, the case pressing it is dropped here rather than re-raised by every future cold session.

Security and authorization belong to `pr-review`'s security gate (`reference/pr-lifecycle.md`), and regression breadth to the full-suite run `reference/ticket-impl.md` already requires. Neither is a bucket here.

### Re-runs reuse; stale files are re-authored

`<id>-qa-adv.md` records the criteria it was authored against, in its header:

```markdown
Authored against: AC-1..AC-6, RCA-2   (spec as of <commit sha>)
```

- **File exists and covers every current criterion** → use it as-is. A session returning from `fix-qa` has already seen everything; re-authoring would produce a contaminated list.
- **Spec has criteria the file doesn't cover** — exactly what closing a spec gap produces → the file is stale. Re-author it in full. That is safe here and only here, because this is a fresh session that never saw the previous run. Without this, a newly added criterion would never be adversarially tested and the screen would stay green — the same silent pass this stage exists to prevent.

**Done when** `<id>-qa-adv.md` is committed, every case cites a criterion or non-goal, every `Expected:` names its independent source, and no case was written after `<id>-qa.md` was opened.

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

Don't proceed until every dev-pass case is green (or explicitly triaged per step 4).

## 3. Adversarial pass

Run `<id>-qa-adv.md` against the same local stack, writing each `Result:` line into that file.

**Then the coverage gap.** With both plans now open, list every adversarial case that has no counterpart in `<id>-qa.md`. It goes at the end of `<id>-qa-adv.md` under `## Coverage gap`, not only into the trace — `kb-update` reads it, and a record is never pipeline input (SKILL.md, "The artifact contract"):

```
Coverage gap — 6 of 14 adversarial cases had no counterpart in the dev plan:
  ADV-2  empty payload            presses AC-1
  ADV-7  null identifier          presses AC-3
  ...
```

This list is the stage's most useful output even when every case passes: it is a written record of what the implementation was never asked about. `kb-update` harvests from it — a gap that recurs across tickets is a house pattern nobody wrote down.

**Record what each case actually reached.** For every case, the trace says whether it ran against the real seam or against a double. A case satisfied entirely by a stub proves the stub agrees with itself, so it is recorded `not run`, never `PASS` — a green with nothing behind it is worse than no case at all, because it spends a reviewer's trust and buys nothing with it.

Don't proceed to the E2E pass until this pass is green (or explicitly triaged per step 4).

## 4. E2E pass

Only once the dev and adversarial passes are green. Drive the real client the way a person actually would — the check the seam-level passes structurally can't perform, because a real user never runs `curl` from their client.

**This session authors the actual steps, independently.** `impl`'s scaffold names only *what flow* is touched; it never saw this session's reasoning and this session never saw `impl`'s. Write the concrete clickable steps and assertions from `<id>-spec.md`'s acceptance criteria — plus, on a bug ticket, the criteria `<id>-rca.md` added under *Fix verification tied to this RCA* — as the source of truth for what "correct" means. Not the scaffold's suggestions, not the implementation's own behavior.

Three of step 0's rules carry over, because they govern honest authoring rather than which layer is under test: **every case cites a criterion or non-goal**, **every `Expected:` comes from an independent source**, and the file is **frozen against `impl`** once written. The five buckets do not carry over — a browser driver replaying boundary and concurrency cases is slow and duplicates the adversarial pass, and the end-user layer exists to catch what only breaks in the real client: an unwired handler, a layer eating the click, a script error the seam never sees.

**If no E2E automation tooling exists in the target repo**, don't fake it and don't skip it silently: write the filled-in steps as a **manual checklist** for the operator to execute by hand.

A checklist takes hours or days, so per SKILL.md's "Waiting vs. exiting," **this session exits rather than waiting.** Name exactly how to return the results:

```
Wrote <ticket-id>-qa-e2e.md — 6 cases. Run them, then:
  /loop-eng verify <ticket-id> --human "E2E-1..5 pass, E2E-6 fails: <what happened>"
```

The returned text lands verbatim in the artifact per SKILL.md's `--human` rules, so the next invocation has the results in writing.

## Evidence: `<id>-verify-trace.md`

All three passes write their evidence here as they run — each case, the command, the output, whether it reached the real seam or a double, and the acceptance criterion it maps to — plus the control case and its verdict, and the adversarial pass's coverage gap list. A triage ruling with no record behind it can be believed but not reviewed; this file is what makes it reviewable. It's a record, never read back in as pipeline input (SKILL.md, "The artifact contract") — written for a human, once.

## 5. Triaging a failure

**A `FAIL` does not automatically mean the implementation is broken.** Classify before fixing anything — routing a bad test case into a code-fix loop is how correct code gets "fixed" until it matches a wrong expectation. The pre-flight above already separates *environment* from *the other three*; if it passed, triage among what's left:

| Failure type | What it means | Who fixes it | How |
|---|---|---|---|
| **Environment** | Pre-flight caught it — see step 1 | operator | fix the unmet precondition; zero retries |
| **Code bug** | The implementation doesn't do what an existing acceptance criterion says | the `impl` session | `/loop-eng impl <id> fix-qa` — bounded, see `reference/ticket-impl.md` |
| **Spec gap** | The case presses behaviour the spec never decided — usually an adversarial case with nothing to cite but the criterion it was reaching past | operator | rule on it: add an acceptance criterion, or write it into `## Non-goals`. Zero retries |
| **Wrong assertion** | The `Expected:` value in the case is itself incorrect | operator | edit `Expected:` in the plan, add a `## Correction log` row, re-run `verify` |
| **Wrong test step** | The `Setup:`/`Action:` block is wrong | operator | edit the block, add a `## Correction log` row, re-run `verify` |

A failure signature corroborates but never decides on its own: an environment failure typically dies *before* the assertion (connection refused, auth rejected, missing binary or config, timeout); a code bug reaches the assertion and returns the wrong value.

**Code bug and spec gap are separated by one question: is there a criterion this behaviour violates?** If yes, the code owes the spec something — `fix-qa`. If no, nobody ever decided what correct means here, and the honest move is to decide it, in writing, before any code changes. Editing code to satisfy an expectation the spec never made invents the requirement and implements it in the same breath, and leaves no record that either happened.

Both exits from a spec gap write into the spec, and both close the loop permanently: a new criterion is tested from then on, and a non-goal is dropped at authoring by step 0's scope guard instead of being re-raised by every future cold session. Adding a criterion also makes `<id>-qa-adv.md` stale, so the next `verify` re-authors it — that is the intended path, not a side effect.

**`fix-qa` means "the code is wrong."** Editing a plan means "the doc is wrong." Ruling on a spec gap means "nobody had decided yet." Never route the second or third into `fix-qa` — that silently rewrites working code to satisfy a typo, or to satisfy a requirement invented seconds earlier.

**Who writes what in the QA plans:** `verify` writes `Result:` lines in all three, plus the full body of `<id>-qa-adv.md` and `<id>-qa-e2e.md`. The operator writes `## Correction log` rows — what was wrong, what changed:

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

Zero for environment, zero for a spec gap, two for a code bug — all defined once in SKILL.md's "Escalation." This stage doesn't repeat them, only triggers them via the table above.

## Done when

- `<id>-qa-adv.md` was authored and committed **before** `<id>-qa.md` was opened, and every case in it cites a criterion or a non-goal.
- Every `Expected:` in a plan this session authored came from the spec, a known-good literal, or a worked example — never from running the code.
- The pre-flight ran before any other result was trusted, and its outcome (including "unavailable") is in `<id>-verify-trace.md`.
- The dev pass is fully green before the adversarial pass starts, and both before the E2E pass.
- The E2E steps were written from the spec's (and, on a bug, the RCA's) acceptance criteria — not copied from the scaffold or reverse-engineered from what the app already does.
- Every case's evidence — command, output, real seam or double, mapped AC — is in `<id>-verify-trace.md`, including the control case's verdict and the coverage gap list.
- Every `FAIL` was classified into exactly one of the five rows before anything was fixed or edited.
- The `Result:` lines were written by this stage; any `## Correction log` row was not.
