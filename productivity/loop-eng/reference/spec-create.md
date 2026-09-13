# `spec` — turn a ticket into testable acceptance criteria

Reads `<id>-ticket.md`. Fails fast in the shape SKILL.md's artifact contract defines if it's absent — name the exact path looked for and the fact that the operator, not a stage, produces it.

## Route first: is this ticket this stage's job at all?

`<id>-spec.md` has two producers (SKILL.md, "Stages"), and the ticket decides which one. Ask one question of the ticket text:

> **Does it name an observable outcome — something you could write a `Then` clause about — or only a want?**

| The ticket | Route | What happens |
|---|---|---|
| Names an outcome. *"Upload fails when the file exceeds 2GB."* The correct behaviour is derivable even where the number isn't. | **B** | This stage, procedure below. |
| Names a want. *"Let the user upload a file."* Format, limit, destination, and post-state are all undecided. | **A** | Stop. The operator grills it outside this skill. |

On route A, say so and stop — don't interview, don't guess a shape, don't write a thin spec that looks finished:

```
<ticket-id> names a want, not an observable outcome — <the undecided dimensions>.
Grill it with your own method, save the result to <resolved-path>/<ticket-id>-spec.md
with the sections below, then run /loop-eng impl <ticket-id>.
```

**This stage never grills.** Arguing a human out of a vague requirement is a conversation, not a procedure, and the method is the team's own — some bring a grilling skill, some an interview skill, some a whiteboard. What the pipeline fixes is the *shape* of the answer, never how it was reached. A route-A spec carries the same sections as a route-B one, and every stage downstream treats the two identically.

## Procedure

1. **Read `<id>-ticket.md`** — the ticket text, pasted by the operator before this stage ever runs. This is the only ticket source; there is no tracker fetch.
2. **Read the project context file** (`CLAUDE.md` / `GEMINI.md` / `AGENTS.md`, per SKILL.md's "Reading the project context file") for the repo's ticket-ID format, domain vocabulary, and house patterns that would sharpen the acceptance criteria. **If it documents none of this, proceed without it** and say plainly that no repo-specific conventions were found — the criteria below are written from the ticket text alone.
3. **If a parent epic tracker is readable** (SKILL.md, "Resolving the ticket directory"), read it for context on what the epic covers. Never create it if absent, never write to it here — only the pipeline's last stage for this ticket does that.
4. **Classify the ticket**: bug, story, chore, or task. State the classification plainly in the spec's header — it decides whether the operator runs `rca` next (bug, `reference/ticket-rca.md`) or goes straight to `impl` (everything else — `rca` is a no-op on anything not classified `bug`).
5. **Interview to close ambiguity.** Delegate the interview mechanics to the `interview-me` skill rather than reimplementing them — invoke it against the ticket text and this stage's open questions. Only what's genuinely undecided after reading the ticket and the project context file gets asked; never interview on what's already written down or derivable.
6. **Write `<id>-spec.md`** with four required sections, in this shape. A route-A spec carries the same four:

   ```markdown
   ## Acceptance criteria
   AC-1  Given <precondition>
         When <action>
         Then <observable outcome>

   ## Non-goals
   - <what this ticket deliberately does not do>

   ## Open gaps
   [GAP-1] <one-line title>                   Status: awaiting <decider>
     Scenario:      <when this comes up, in one line>
     Not ours:      <why engineering cannot settle it alone — who it affects>
     Options:       A <option + cost>  /  B <option + cost>
     Recommend:     <which, and why>

   ## Evidence
   AC-1                           <path>:<line>
   claim: "<load-bearing claim>"  <path>:<line>
   ```

   Each acceptance criterion is a **numbered, individually testable** `Given/When/Then` statement — the numbering is what lets `<id>-qa.md`, `pr-review` findings, and `rca`'s *Fix verification tied to this RCA* section cite `AC-3` unambiguously. The evidence index maps every load-bearing claim to a `file:line` or commit SHA; `rca` traces from it and cannot verify a root-cause claim without one. A claim with no source is marked `[NEEDS CONFIRMATION]`, never asserted as fact.

   **`## Non-goals` is required, and `none` is an answer.** Writing it down turns *decided against* into something a later session can read, which silence never is. `verify`'s adversarial pass presses the criteria to their limit and drops any case that cites neither a criterion nor a non-goal (`reference/ticket-verify.md`), so this section is simultaneously the scope brake and the reason a ruled-out behaviour stays ruled out instead of being re-raised by every cold session that follows.

   **`## Open gaps` is required, and `none` is an answer.** It parks what this ticket cannot settle on its own — a product rule, a legal constraint, a cross-team trade-off — so the interview keeps moving instead of stalling on a question nobody in the room can answer. `impl` refuses to start while any entry is unruled (`reference/ticket-impl.md`).

   **Every gap carries `Recommend:` and `Not ours:`, and an entry missing either is not a gap.** A bare question hands the thinking upward along with the decision; the options and the recommendation are engineering's work, and ruling on them is the decider's. Handed a question, a decider needs days to invent the options first; handed a recommendation, they need a minute to agree or overrule. And when `Not ours:` can't be filled in honestly, that is the tell that the call *is* yours — make it, record it as a criterion or a non-goal, and park nothing.

7. **Where the ruling lands.** A closed gap is rewritten in place — `Status: Resolved <date> — <ruling>` — and the ruling becomes a numbered acceptance criterion or a non-goal. Left only in the gap entry it binds nothing: no case tests it and no stage reads it. The entry stays for the record, because what a decision *used to be* explains the code later.

8. **Commit `<id>-spec.md`** to the progress repo and stop, per SKILL.md's "One stage, one session." Append the progress line.

## Done when

- The route was named out loud: this stage wrote the spec, or it stopped and said which dimensions were undecided.
- The spec's classification names bug, story, chore, or task, and the operator can tell from it alone whether `rca` runs next.
- Every acceptance criterion is numbered and independently testable.
- `## Non-goals` and `## Open gaps` both exist, even if both say `none`.
- Every gap names a decider, its options, why it isn't engineering's call, and a recommended option — and every gap that could have been answered here was answered here instead of parked.
- Every load-bearing claim in the spec has a matching row in `## Evidence`, or is marked `[NEEDS CONFIRMATION]`.
- Nothing was asked in the interview that the ticket text or the project context file already answered.
