# `spec` — turn a ticket into testable acceptance criteria

Reads `<id>-ticket.md`. Fails fast in the shape SKILL.md's artifact contract defines if it's absent — name the exact path looked for and the fact that the operator, not a stage, produces it.

## Procedure

1. **Read `<id>-ticket.md`** — the ticket text, pasted by the operator before this stage ever runs. This is the only ticket source; there is no tracker fetch.
2. **Read the project context file** (`CLAUDE.md` / `GEMINI.md` / `AGENTS.md`, per SKILL.md's "Reading the project context file") for the repo's ticket-ID format, domain vocabulary, and house patterns that would sharpen the acceptance criteria. **If it documents none of this, proceed without it** and say plainly that no repo-specific conventions were found — the criteria below are written from the ticket text alone.
3. **If a parent epic tracker is readable** (SKILL.md, "Resolving the ticket directory"), read it for context on what the epic covers. Never create it if absent, never write to it here — only the pipeline's last stage for this ticket does that.
4. **Classify the ticket**: bug, story, chore, or task. State the classification plainly in the spec's header — it decides whether the operator runs `rca` next (bug, `reference/ticket-rca.md`) or goes straight to `impl` (everything else — `rca` is a no-op on anything not classified `bug`).
5. **Interview to close ambiguity.** Delegate the interview mechanics to the `interview-me` skill rather than reimplementing them — invoke it against the ticket text and this stage's open questions. Only what's genuinely undecided after reading the ticket and the project context file gets asked; never interview on what's already written down or derivable.
6. **Write `<id>-spec.md`** with two required sections, in this shape:

   ```markdown
   ## Acceptance criteria
   AC-1  Given <precondition>
         When <action>
         Then <observable outcome>

   ## Evidence
   AC-1                           <path>:<line>
   claim: "<load-bearing claim>"  <path>:<line>
   ```

   Each acceptance criterion is a **numbered, individually testable** `Given/When/Then` statement — the numbering is what lets `<id>-qa.md`, `pr-review` findings, and `rca`'s *Fix verification tied to this RCA* section cite `AC-3` unambiguously. The evidence index maps every load-bearing claim to a `file:line` or commit SHA; `rca` traces from it and cannot verify a root-cause claim without one. A claim with no source is marked `[NEEDS CONFIRMATION]`, never asserted as fact.

7. **Commit `<id>-spec.md`** to the progress repo and stop, per SKILL.md's "One stage, one session." Append the progress line.

## Done when

- The spec's classification names bug, story, chore, or task, and the operator can tell from it alone whether `rca` runs next.
- Every acceptance criterion is numbered and independently testable.
- Every load-bearing claim in the spec has a matching row in `## Evidence`, or is marked `[NEEDS CONFIRMATION]`.
- Nothing was asked in the interview that the ticket text or the project context file already answered.
