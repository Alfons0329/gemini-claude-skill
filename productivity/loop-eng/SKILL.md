---
name: loop-eng
description: Runs one stage of the ticket pipeline (spec, rca, impl, verify, pr-create, pr-review, kb-update), reading and writing the artifacts that carry context between stages so each stage can start cold in its own session.
disable-model-invocation: true
---

**User-invoked.** A stage commits work, and some open pull requests — an agent that could fire the next stage on its own is an agent able to cross the session boundary the whole design depends on (see "One stage, one session" below). Start it by typing the command; nothing here fires itself.

## Stages

Seven stages, one skill. Each stage's actual procedure — what "climb the ladder" or "two-perspective verification" means in practice — lives in its own `reference/<file>.md`, loaded only when that stage runs. This file holds only what every stage shares: dispatch, the artifact contract, and the rules that don't change per stage.

| # | Stage token | Reads | Produces | Procedure |
|---|---|---|---|---|
| 1 | `spec` | `<id>-ticket.md` | `<id>-spec.md` — **one of two producers, see below** | `reference/spec-create.md` |
| 1b | `rca` | `<id>-ticket.md`, `<id>-spec.md` — **bug tickets only** | `<id>-rca.md` | `reference/ticket-rca.md` |
| 2 | `impl` | `<id>-spec.md`, plus `<id>-rca.md` on a bug ticket | code in the target repo, `<id>-qa.md`, `<id>-qa-e2e.md` scaffold | `reference/ticket-impl.md` |
| 3 | `verify` | `<id>-spec.md`, `<id>-rca.md` (bug tickets), `<id>-qa.md`, the `-qa-e2e.md` scaffold, and its own `<id>-qa-adv.md` on a re-run | `<id>-qa-adv.md` authored blind, `Result:` lines in both QA plans, filled-in and run `<id>-qa-e2e.md`, `<id>-verify-trace.md` | `reference/ticket-verify.md` |
| 4 | `pr-create` | `<id>-spec.md`, `<id>-qa.md`, `<id>-qa-adv.md`, `<id>-qa-e2e.md` | `<id>-pr.md` drafted, then the PR opened from it; tracker updates printed for the operator | `reference/pr-lifecycle.md` |
| 5 | `pr-review` | the diff, `<id>-spec.md` | inline review comments, `<id>-security-review.md` when there are findings | `reference/pr-lifecycle.md` |
| 6 | `kb-update` | `<id>-rca.md` (bug tickets), `<id>-qa.md`, `<id>-qa-adv.md`, the diff | `docs/` updated in the **target** repo, on the feature branch | `reference/kb-update.md` |

Only `spec`, `rca`, `impl`, `verify`, `pr-create`, `pr-review`, and `kb-update` are valid stage tokens. A stage may only read the artifacts named in its own row above — nothing else in a ticket directory is pipeline input (see "The artifact contract").

**`<id>-spec.md` has two legitimate producers**, and every stage downstream treats them identically — the artifact is the contract, never the session that wrote it:

- **The `spec` stage**, when the ticket already names an observable outcome.
- **The operator**, when it doesn't. A ticket naming a want rather than an outcome is grilled outside this skill, by whatever method the team uses, and the result saved to `<id>-spec.md` by hand — exactly as `<id>-ticket.md` already is. `reference/spec-create.md` routes between the two and never grills on its own.

## Running it

```
/loop-eng <stage> <ticket> [mode] [--human "<free text>"]

stages:  spec | rca | impl | verify | pr-create | pr-review | kb-update
modes:   fix-qa | fix-sec          (impl only)
--human: optional per-invocation context, valid on every stage
```

Artifact paths are never passed as arguments. Resolve the ticket directory once (below), then derive every filename from `<ticket>` — one fewer thing to get wrong, and one fewer way for two stages to disagree about where a file lives.

`pr-review` also takes the PR URL as a positional argument after `<ticket>` (it has no other way to find the diff to review).

## Resolving the ticket directory

Every artifact lives under a **progress root** — a directory outside every target repo, personal to this machine, never in a target repo's own context file. Read it from the user-level project-context file (`~/.claude/CLAUDE.md`, `~/.gemini/GEMINI.md`, or the current harness's equivalent). **If that file documents no progress root, stop and say so** — name the missing line, don't guess a location and don't fall back to a target repo.

Given `<ticket>`:

- **Contains `/`** — it's a path, not an ID. Resolve it relative to the progress root. The ticket ID for filenames is the last path segment.
- **No `/`** — search recursively beneath the progress root for a directory named exactly `<ticket>`.
  - **Exactly one hit** — use it.
  - **Zero hits** — create `<progress-root>/<ticket>/` and say where.
  - **Two or more hits** — stop, list every match, ask which. Never guess between candidates and never invent a second home for a ticket that already has one.

A pointed invocation (`/loop-eng verify <grouping>/.../eng-1`) and a searched one (`/loop-eng verify eng-1`) that land on the same directory produce identical filenames.

**Parent epic tracker.** If a tracker file sits above the ticket directory (grouping level), any stage may read it for context — it's opt-in, made by hand, never created by a stage. Only `kb-update` — always the pipeline's last stage for a given ticket, whether or not `verify` was skipped along the way — appends exactly one line on completion: `<ticket-id>  done` or `<ticket-id>  blocked: <one line>`. No per-AC detail goes upward, and a missing tracker means nothing is written and nothing is said.

## One stage, one session

Run the stage, commit, report, stop. **Never continue into the next stage in the same session**, even when the next stage is obvious and the context is already loaded. No stage triggers another — the operator decides when each one runs, and that decision point is a checkpoint they can redirect at.

This is the rule the whole design rests on. A session that ran `impl` cannot be trusted to run `verify` — it already knows what it expects to pass, and would be grading its own homework. The only thing that crosses a session boundary is whatever got committed to git; no session inherits another's reasoning.

## The artifact contract

Filenames are always `<ticket-id-lowercase>-<artifact>.md` — one spelling per artifact, lowercase throughout, so a dozen open ticket files sort and read cleanly.

Two kinds of artifact, and the difference is load-bearing:

| | Artifacts | Read by a later stage? |
|---|---|---|
| **Drivers** | `-spec.md`, `-rca.md`, `-qa.md`, `-qa-adv.md`, `-qa-e2e.md` | **Yes** — these are the contract; every stage row above names which ones it reads. |
| **Records** | `-progress.md`, `-verify-trace.md`, `-pr.md`, `-security-review.md` | **No** — written once, for a human to read on demand. Never loaded as pipeline input. One named exception: `impl <id> fix-sec` reads `-security-review.md`, because that record *is* the finding the invocation exists to repair (`reference/ticket-impl.md`, "Repair mode: `fix-sec`"). |

A record is never a shortcut for re-deriving what a driver already says. `<id>-verify-trace.md` exists so a human can audit a triage ruling later; nothing downstream reads it — `pr-create`'s "how it was verified" comes from `<id>-qa.md`'s own `Result:` lines (a driver), not from re-opening the trace. `<id>-progress.md` is read by the operator coming back from time away, not by the next stage. Both stay short by construction: a record that grows into prose has stopped being a record and started being a second, unreliable copy of a driver.

**Every stage appends one or two lines to `<id>-progress.md`** when it finishes, in the register of a commit message — what was done, what state the ticket is in now. This is unconditional, independent of which stage token ran.

**A ticket directory also accumulates scratch** — logs, scripts, captured bundles. Only the artifacts named in the stage table are ever read by a stage; everything else is invisible to the pipeline, and a stage that wanders into a stale log bundle is drawing conclusions from the wrong run.

**The test plans are frozen against their own author.** `<id>-qa.md`, `<id>-qa-adv.md` and `<id>-qa-e2e.md` are read-only to `impl` on a `fix-qa` invocation: it changes the code until the cases pass, and adds regression tests in the target repo, but never a case's `Setup:`, `Action:` or `Expected:`. A case that is genuinely wrong is the operator's to correct, through the `## Correction log` (`reference/ticket-verify.md`). Without the freeze, the cheapest way to turn a suite green is to lower the bar it sets.

**Missing or malformed input fails fast.** Never improvise a substitute, never proceed on a partial read. Name three things: which artifact is missing, the exact path it was looked for at, and the command that produces it:

> `No <ticket-id>-qa.md at <resolved-path>. Run /loop-eng impl <ticket-id> first.`

**`<id>-spec.md` names both of its producers**, because the right one depends on the ticket and sending an ambiguous ticket into `spec` only bounces it straight back out:

> ```
> No <ticket-id>-spec.md at <resolved-path>.
>
>   Ticket already names the observable outcome?
>     → /loop-eng spec <ticket-id>
>
>   Ticket names a want, not an outcome?
>     → grill it with your own method, save the result there, then re-run.
> ```

The same shape covers a missing `<id>-ticket.md` (produced by the operator, not a stage):

> `No ticket.md for <ticket-id>. Save the ticket text to <resolved-path>/<ticket-id>-ticket.md and re-run.`

## Reading the project context file

Every operational fact — the test command, environment prerequisites, branch and commit conventions, house patterns, domain vocabulary — lives in the **target repo's** project context file (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`), never in this skill. It's loaded automatically at session start, so reading it costs nothing extra.

**Every stage must degrade gracefully when that file documents nothing it needs.** Never block on the gap, never invent a convention and present it as the repo's. Instead, proceed on a named fallback and say plainly that the fallback fired — a silent one produces output indistinguishable from a verified run, which is exactly the failure this pipeline exists to prevent. The concrete fallback text is specific to what each stage needs and lives in that stage's `reference/*.md`; this file only sets the rule that every stage must have one.

## `--human` — per-invocation context

Valid on every stage. Carries a fact true of *this ticket only* — not durable enough for the project context file, not knowable from the artifacts alone.

```
/loop-eng spec <ticket-id> --human "Only reproduces on kernel 6.8.10; triage to that version only."
```

1. **Written into the stage's own artifact, verbatim, under a `## Human input` heading.** Sessions share nothing but committed files, so input that stays only in the session evaporates before the next stage runs.
2. **It outranks inference, but never silently.** Where it contradicts the project context file or the spec, the stage says so and asks which wins rather than quietly deviating. Record the resolution next to the input.
3. **Repetition means it belongs in the project context file instead.** The same `--human` text passed on a third ticket was never per-invocation — it's a repo fact being re-typed. Say so.
4. **On a repair invocation, it appends, dated — it never replaces.** What an instruction *used to be* often explains why the code looks the way it does. A later entry may countermand an earlier one in words; it never deletes it from the record.

```
## Human input
2026-08-14  Only reproduces on <version>; triage to that version only.
2026-08-15  Ignore the above — also reproduces on <other>. Widen the triage.
```

## Waiting vs. exiting

A stage that needs the operator either blocks in-session or writes down what it needs and exits — decided by how long the operator would be away, not by which stage is running:

| | Wait (block in-session) | Exit and get re-invoked |
|---|---|---|
| When | Answerable in seconds without leaving the keyboard | Requires leaving: a manual checklist, an environment fix, another team |
| Example | `impl` confirming a seam before writing a test | `verify`'s manual E2E checklist when no automation tooling exists |

*Always block* leaves a session open long enough for its context to go stale against a world that moved. *Never block* charges a full cold session for a ten-second question. Pick per the cost of the operator's actual attention, not a blanket rule.

A stage that exits names exactly what it needs and how to return it — results come back through `--human` on the next invocation, which lands in the artifact per the rules above:

```
Wrote <ticket-id>-qa-e2e.md — 6 cases. Run them, then:
  /loop-eng verify <ticket-id> --human "E2E-1..5 pass, E2E-6 fails: <what happened>"
```

## Escalation

Applies wherever a stage's own procedure calls for a bounded retry (concretely, today: `verify`'s `fix-qa` loop, and `pr-review`'s `fix-sec` gate). The budget depends on what failed, and the two are opposites:

| Cause | Retries | Escalate after | What the human is asked for |
|---|---|---|---|
| **Environment** (the test never reached the code) | **0** — a thousand attempts give a thousand identical failures | immediately | fix the unmet precondition — name it and its evidence |
| **Spec gap** (the criterion for this behaviour was never written) | **0** — there is nothing to satisfy | immediately | rule on the behaviour — add an acceptance criterion, or declare a non-goal |
| **Code bug** (the code doesn't do what the criterion says) | up to 2, each a new hypothesis | 2 attempts | judge the code — the repro, both attempts, the ranked hypothesis list |

On an environment failure: don't enter a repair mode, don't edit code, don't edit a driver artifact. Report the unmet precondition and its evidence, and stop. A spec gap takes the same shape for the same reason — editing code to satisfy an expectation the spec never made is inventing the requirement and implementing it in one move.

On a code bug that's still failing after the budget: stop, don't spin. Report the documented repro, both attempts and why each didn't hold, and the current ranked hypothesis list. Wait for direction — anything touching a decision beyond this session's own scope is recommended and waited on, never applied unilaterally.

**Repair-mode scope.** `fix-qa` belongs to the `impl ↔ verify` loop only, and must close *before* a PR is opened — a correctness finding raised later in `pr-review` is addressed by editing and re-pushing, not by re-entering `fix-qa`. The one review finding with its own named repair loop is a security finding: `/loop-eng impl <id> fix-sec`.

## Done when

- The ticket directory resolved to exactly one path, by search, by path override, or by creation — never by guessing between candidates.
- The stage read only the artifacts its row in "Stages" names, and failed fast (naming artifact, path, and producing command) on anything missing.
- Nothing carried forward except what got committed — no session assumed context from an earlier one.
- Every test plan this session did not author came out of it byte-identical — the freeze held.
- `<id>-progress.md` gained its one or two lines.
- Any `--human` text landed verbatim, dated, under `## Human input` in this stage's own artifact.
- The session stopped after one stage — it did not chain into the next.
