# Self-check results — 2026-09-14

Run against `example/self-check.md` after the adversarial-verify change (commits `e8a69af`, `fbf7587`), which added a third QA plan, a third pass, a fifth triage row, a second producer for `<id>-spec.md`, and a gate on `impl`.

Checks A–E and G ran here. **Check F is deliberately not run in this session** — it requires a session that has not read these files, for the reason the check itself gives.

Paths below are relative to `productivity/loop-eng/`.

> Supersedes the 2026-08-28 run. That one passed against the pre-change files; its citations no longer resolve.

---

## Check A — the handoff chain

| Stage | Input named | Output named | Missing-input behaviour |
|---|---|---|---|
| `spec` | `SKILL.md:15`, `reference/spec-create.md:3` | `SKILL.md:15`, `reference/spec-create.md:34-66` | `reference/spec-create.md:3`, `SKILL.md:92-100` |
| `rca` | `SKILL.md:16`, `reference/ticket-rca.md:7` | `SKILL.md:16` | `SKILL.md:85-87`; no-op path `reference/ticket-rca.md:3` |
| `impl` | `SKILL.md:17`, `reference/ticket-impl.md:3` | `SKILL.md:17`, `reference/ticket-impl.md:56-81` | `SKILL.md:85-87`; gap gate `reference/ticket-impl.md:5-16` |
| `verify` | `SKILL.md:18`, `reference/ticket-verify.md:5` | `SKILL.md:18`, `reference/ticket-verify.md:19-70,91,99` | `SKILL.md:85-87` |
| `pr-create` | `SKILL.md:19`, `reference/pr-lifecycle.md:7` | `SKILL.md:19`, `reference/pr-lifecycle.md:9` | `SKILL.md:85-87` |
| `pr-review` | `SKILL.md:20,42`, `reference/pr-lifecycle.md:41` | `SKILL.md:20`, `reference/pr-lifecycle.md:56` | `SKILL.md:85-87` |
| `kb-update` | `SKILL.md:21`, `reference/kb-update.md:3` | `SKILL.md:21`, `reference/kb-update.md:11-27` | `SKILL.md:85-87` |

**Every driver has a named producer**, checked by sweeping the stage table for each filename:

```
-spec.md      spec  (SKILL.md:15)  or the operator  (SKILL.md:25-28)
-rca.md       rca
-qa.md        impl
-qa-adv.md    verify, authored blind
-qa-e2e.md    impl scaffolds it, verify authors the steps
```

**`<id>-spec.md`'s second producer is the change most able to break this check**, so it was swept separately: every place naming how to obtain the file must name both routes, or an ambiguous ticket gets sent into `spec`, which bounces it straight back out.

```bash
grep -rn 'spec <ticket-id> first\|spec <TICKET-ID> first' --include='*.md' .
```

No hits. The fail-fast messages at `SKILL.md:92-100` and `SPEC.md:825-833` both branch on whether the ticket names an outcome.

Passes.

## Check B — the cycle closes

1. `kb-update` writes to the target repo's `docs/` — `reference/kb-update.md:7`.
2. Every stage reads the project context file — rule at `SKILL.md:102-106`.
3. They meet at `reference/kb-update.md:51` and `:61`: a `docs/` entry a future stage would need carries a one-line `CLAUDE.md` pointer, because no stage browses `docs/` on its own.

**One new input on this path.** `reference/kb-update.md:5` reads `<id>-qa-adv.md`'s coverage gap list — the adversarial cases the dev plan never contained. That is why the list lives at the end of `<id>-qa-adv.md` (a driver) rather than only in `<id>-verify-trace.md`: a record is never pipeline input (`SKILL.md:74-75`), so a gap list filed there would have been unreadable by the stage that wants it.

Passes.

## Check C — cold start, every fallback fires

- [x] `spec` with no tracker — ticket text from `<id>-ticket.md` (`reference/spec-create.md:3`); absent, fails fast naming path and producer (`SKILL.md:99-100`).
- [x] All stages name a documents-nothing fallback: `spec` `reference/spec-create.md:29` · `rca` `reference/ticket-rca.md:13` · `impl` `reference/ticket-impl.md:54` · `verify` `reference/ticket-verify.md:85` · `pr-create` `reference/pr-lifecycle.md:27` · `pr-review` `reference/pr-lifecycle.md:62` · `kb-update` `reference/kb-update.md:28`. Rule set once at `SKILL.md:106`.
- [x] No test command — emits the *pre-flight unavailable* line, `reference/ticket-verify.md:85-87`. It covers all three passes: the sentence says the triage below is unverified, and the adversarial pass sits below it.
- [x] No pre-existing control case — falls back to the repo's own suite (`reference/ticket-verify.md:83`); missing that too, the announcement above.
- [x] No E2E tooling — writes the manual checklist, names the exact re-invocation command, and exits (`reference/ticket-verify.md:130-137`).

Every fallback announces. None is silent.

## Check D — every failure path lands

| Failure | Landing | Citation |
|---|---|---|
| `verify` red, environment | zero retries, escalate immediately | `reference/ticket-verify.md:149`; `SKILL.md:154` |
| `verify` red, code bug | `impl <id> fix-qa`, at most 2 attempts | `reference/ticket-verify.md:150`; `SKILL.md:156` |
| `verify` red, presses no criterion | **spec gap** — zero retries, operator rules | `reference/ticket-verify.md:151`; `SKILL.md:155` |
| still red after the budget | stop; repro, both attempts, ranked hypotheses | `SKILL.md:160`; `reference/ticket-impl.md:97` |
| security finding in `pr-review` | blocks, writes `-security-review.md`, repairs via `fix-sec` | `reference/pr-lifecycle.md:56`; `reference/ticket-impl.md:100` |
| wrong assertion / wrong test step | operator edits, `## Correction log` row | `reference/ticket-verify.md:152-153` |
| dev case whose `Action:` is prose | triaged as a wrong test step, never counted as covered | `reference/ticket-verify.md:114` |
| input artifact missing or malformed | fail fast — artifact, path searched, producing command | `SKILL.md:85-100` |
| `<id>-spec.md` missing | fail fast naming **both** producers | `SKILL.md:92-100` |
| `## Open gaps` entry unruled at `impl` | `impl` stops before the ladder; `rca` unaffected | `reference/ticket-impl.md:5-16` |
| ticket directory not found / found twice | create-and-say / stop-and-list | `SKILL.md:52-54` |

**Three budgets, no collisions.** Zero for environment and zero for a spec gap, two for a code bug (`SKILL.md:154-156`). The two zero-retry rows land in different places — the machine, and a ruling written into the spec — so no row shares a landing with a different budget.

**Spec gap does not overlap code bug.** One question separates them: does a criterion exist that this behaviour violates (`reference/ticket-verify.md:155`). If yes the code owes the spec something; if no, nobody decided, and editing code would invent the requirement and implement it in one move.

**The gap-quality rule is checked here too** (`example/self-check.md:101`): a `[GAP]` lacking `Recommend:` or `Not ours:` fails, enforced at `reference/spec-create.md:62`.

Passes.

## Check E — nothing is restated

```
grep -rn 'one stage per invocation\|never chain\|Human input\|append.*dated' reference/
```

No hits. Shared rules live only in `SKILL.md`.

**The freeze rule was checked separately**, being new and the most tempting to repeat:

| Where | What it is |
|---|---|
| `SKILL.md:83` | the rule — the one home |
| `reference/ticket-impl.md:87` | cites it by name ("SKILL.md, The artifact contract"), then adds only what is specific to repair |
| `reference/ticket-verify.md:126` | one clause noting E2E inherits it |

One definition, two pointers. `reference/ticket-verify.md:27` uses "frozen" for a different thing — intents frozen between authoring layers — and is not a restatement.

Passes.

## Check G — a blind spot does not survive the handoff

Traced a criterion whose failure mode the spec never mentions: an input that can be null where nothing says what null means.

| Step | Where | Citation |
|---|---|---|
| 1. Authored blind, before `<id>-qa.md` is opened | reads spec only; no code, no dev plan | `reference/ticket-verify.md:19,25` |
| 2. The null case is generated regardless | boundary bucket names null explicitly | `reference/ticket-verify.md:34` |
| 3. It can actually go red | `Expected:` from the spec, never from running the code | `reference/ticket-verify.md:47` |
| 4. It presses no criterion → caught | spec gap row; exits are a new criterion or a non-goal | `reference/ticket-verify.md:151` |
| 5. A new criterion re-arms the adversary | header check marks the file stale; re-authored in full | `reference/ticket-verify.md:61-68` |

**No path exists where the case is generated, passes, and nobody learns anything.** Step 3 is what makes this real rather than theatre: a case whose expected value was read off the implementation is green forever, and generating it would have proved nothing.

Reverse direction — the guard cannot be quietly switched off:

- [x] No documented way to skip the adversarial pass alone — whole-stage skip only, stated in the PR body (`reference/ticket-verify.md:17`).
- [x] `impl` may change nothing in any of the three plans during `fix-qa` (`reference/ticket-impl.md:87`), and its diff is bounded to what the failure implicates (`:89`).
- [x] A case satisfied entirely by a double is recorded `not run`, never `PASS` (`reference/ticket-verify.md:116`).
- [x] A prose `Action:` cannot be counted as covered (`reference/ticket-verify.md:114`), and `reference/ticket-impl.md:62` requires a runnable command — so a gap cannot hide behind a sentence that sounds like a test.

Passes.

## Check F — `SKILL.md` stands alone

**Not run.** Requires a session that has not read these files; this one reviewed them and cannot tell what it meant to write apart from what is on the page. Prompt is in `self-check.md`, "Check F".

It is worth more now than at the last run: `verify` gained an artifact, two authoring layers and a third pass, and a cold operator reading only `SKILL.md` has more to guess than before.

---

## Status

A–E and G pass. No breaks found. F outstanding.

Two limits, restated here because a passing checklist can read as a stronger claim than it is (`SPEC.md` §5.1a):

- The adversary's blindness is **ordering, not isolation** — a session that decided to peek could.
- No adversary catches a business rule that is wrong in the spec itself. Spec, code, cases and adversary are then wrong together, in agreement.
