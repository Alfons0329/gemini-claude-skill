# `rca` — root cause and escape analysis, bug tickets only

**No-op on a story, chore, or task.** There is no defect to root-cause, and forcing one produces a document that says nothing. If the spec's classification (`reference/spec-create.md` step 4) isn't `bug`, say so and stop without writing `<id>-rca.md`.

On a bug ticket, this runs in its own fresh session between `spec` and `impl`. It gates `impl` — see "The stop-and-report gate" below.

Reads `<id>-ticket.md` and `<id>-spec.md`. The spec owns *what is broken and how it will be fixed*; this stage owns *why it shipped and why it escaped*, and must not restate the spec's fix detail — link to it (`AC-3`, etc.) instead of repeating it.

**Not the same thing as `verify`'s diagnosis.** `reference/ticket-verify.md`'s "Building the discriminating repro" section debugs a failure `verify` just produced, in the current session, against the current code. This stage explains why a defect reached users and wasn't caught before — escape analysis over history: commits, requirements, and the test surface as it stood when the code was written. Different question, different evidence, different session; don't conflate the two.

## Procedure

1. **Read the project context file** for branch/commit conventions that help locate the introducing commit. If it documents none, work from `git log`/`git blame` directly and note where a convention would have made the trace faster — that observation is exactly the kind of thing `kb-update` (`reference/kb-update.md`) wants later.
2. **Confirm the spec's root-cause claim against the actual code** — the central job of this stage. Check that the named guard or branch really sits at the cited line, that the commits say what the spec says they say, and that a second defect folded into the same ticket is genuinely independent rather than a symptom of the first.
3. **The stop-and-report gate.** If the claim does not hold under that check, stop here and report what was found instead. The repair path is back to `spec`, not forward into a fix built on a wrong mechanism — writing the RCA anyway would rationalize a fix that doesn't yet exist rather than test the claim that produces it.
4. **Write `<id>-rca.md`**, in exactly three parts, in this order:

   **1 — At a glance.** The triage surface, readable alone. One row per defect:

   ```markdown
   | # | What's broken | Where | Effect | Fix |
   ```

   `What's broken` names the mechanism, not the symptom. `Where` gives the `file:line` call chain. Add a supporting table only when it would change a triager's mind — blast radius, or a derivation table where the mechanism turns on two things that look equivalent but aren't. Cut any table that just restates the spec's files-touched list.

   **2 — TL;DR.** The root cause in one line, leading with mechanism, never blame. Two or three supporting bullets only where the one-liner needs them to be believable — an assumption defensible in isolation, a requirement aimed at a different scenario, a test surface that didn't exist yet.

   **3 — Deep dive.** One named subsection per defect or per cause. Each cites the commit that introduced the gap, names the assumption that was correct in isolation and wrong in composition, and explains what kept it hidden. Close with three fixed subsections, always in this order:

   - **What would have caught it** — numbered, *generalizable* process rules, not ticket-specific notes. This is the RCA's primary input to `kb-update` (`reference/kb-update.md`) on a bug ticket.
   - **Fix verification tied to this RCA** — the load-bearing section. Escape analysis routinely surfaces a scenario nobody would have written an acceptance criterion for; each such finding becomes a numbered criterion here, cited back to the spec's numbering (`AC-6`, `E2E-5`). `impl` and `verify` are bound by these exactly as they are by the spec's own criteria — this is what makes the RCA generative rather than a retrospective.
   - **Reference** — every load-bearing claim mapped to its source: `file:line`, commit SHA, or a section of a prior ticket's spec/QA artifact. An unsourced claim is marked `[NEEDS CONFIRMATION]` and surfaced, never asserted.

5. **Commit `<id>-rca.md`** and stop, per SKILL.md's "One stage, one session." Append the progress line.

## Done when

- The stage is a clean no-op on any non-bug ticket, with nothing written.
- The root-cause claim was checked against the code before anything else ran, and the gate fired if it didn't hold.
- The three parts appear in order, and the deep dive's three closing subsections are all present.
- Every criterion under *Fix verification tied to this RCA* cites a spec (or its own) numbering that `impl`/`verify` can bind to.
- Every claim in *Reference* is sourced or marked `[NEEDS CONFIRMATION]`.
