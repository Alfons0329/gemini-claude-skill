# `pr-create` and `pr-review` — draft, open, then gate and review

Two stage tokens, one file, because they're two ends of the same artifact: the PR `pr-create` opens is exactly what `pr-review` reviews.

## `pr-create`

Reads `<id>-spec.md`, `<id>-qa.md`, `<id>-qa-e2e.md`.

1. **Draft `<id>-pr.md` before opening anything** — the body is read while it's still cheap to change, and the file stays in the ticket directory afterward as the record of what was claimed:

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

2. **Paste acceptance criteria verbatim, never summarized.** The spec lives in the progress repo, which no reviewer can open — the PR body is the only place the intended behavior appears to them. A summary would also break `pr-review`'s spec axis below, which quotes spec lines a reviewer must be able to check against the real wording.
3. **`## How it was verified` is drawn from `<id>-qa.md`'s `Result:` lines and `<id>-qa-e2e.md`'s run results** — both drivers this stage already has open. If `verify` was skipped under its documented-skip escape hatch (`reference/ticket-verify.md`), state that plainly here instead, with the reason — the one condition on that skip is that it's never silent, and this section is where it stops being silent.
4. **Open the PR from the drafted body** once it reads the way it should. Use whatever the project context file documents for opening a PR against this repo's host. **If it documents nothing**, don't guess a host or CLI — ask the operator once which tool to use, the same way `reference/ticket-impl.md` asks once for an undocumented test command rather than guessing a runner.
5. **Never touch the tracker.** Print the updates the operator should make and stop:

   ```
   Tracker updates for you:
     [ ] move <ticket-id> to In Review
     [ ] link this PR on the ticket
   ```

6. **The parent epic tracker, if present, is read-only here.** This stage may read it for context; only `kb-update` writes the closing line (SKILL.md, "Resolving the ticket directory").
7. Commit `<id>-pr.md` and stop, per SKILL.md's "One stage, one session." Append the progress line.

## `pr-review`

Reads the diff between a fixed point (a commit/branch/tag the operator names, or `main` by default) and `HEAD`, plus `<id>-spec.md`. Runs the security gate first; the three-axis review only proceeds once that gate is clear.

### The security gate (runs first)

Scan the same diff for **security defects only**, framed by the **current OWASP Top 10** — the industry's shared vocabulary, so a finding lands in a category any reviewer anywhere already recognizes. The list itself isn't transcribed here on purpose: OWASP re-ranks between editions, and a copy pinned into a skill goes stale in the one way that never announces itself — nothing breaks, the scan just keeps checking a previous decade's categories. Read the current list at review time.

Two categories get called out because they're specifically what an **agent-written** diff gets wrong, and both read past easily:

- **New or outdated dependencies.** An agent reaches for a library rather than the ten lines that would have done it. `reference/ticket-impl.md`'s ladder catches most of this at rung 5, but review here whatever dependency did survive into the diff — what it is, why it's needed, whether it's currently maintained.
- **Server-side request forgery.** A URL that arrives from user input and gets fetched server-side. Shows up whenever an agent wires up "fetch this and show it," done readily and without alarm.

**If no current OWASP reference is reachable**, this floor still applies, and the scan states it ran degraded: injection, authn/authz gaps, credential or PII exposure in logs and errors, unsafe deserialization, missing input validation at trust boundaries, plus the two categories above.

**Keep it narrow.** This is not a code-quality pass — quality findings belong to the three-axis review below. A gate that drifts into style stops being a gate, because a blocking finding that's really a preference teaches everyone to route around the block.

A finding here **blocks the PR** and writes `<id>-security-review.md`. Its repair loop is named and distinct: `/loop-eng impl <id> fix-sec` (`reference/ticket-impl.md`). Nothing else in this stage's findings uses that repair loop — see SKILL.md's "Repair-mode scope."

### Three-axis review

Once the gate is clear, review the diff along **three independent axes**, each run as a **parallel sub-agent** (`Agent` tool, `general-purpose` type, one message with all three calls) so none pollutes another's context:

- **Standards axis** — does the diff conform to this repo's documented standards (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, etc.), *plus* a fixed baseline that applies even when the repo documents nothing: Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality, Message Chains, Middle Man, Refused Bequest. A documented repo standard always overrides the baseline. Baseline smells are judgment calls; documented-standard breaches can be hard violations.
- **Spec axis** — does the diff faithfully implement `<id>-spec.md`? Report missing or partial requirements, scope creep, and requirements that look implemented but are wrong — quoting the spec line for each finding.
- **Deletion axis** — what in this diff shouldn't exist? Reinvented standard library, an unneeded dependency, speculative abstraction, dead flexibility, boilerplate nobody asked for. One line per finding: where it is, what to cut, what replaces it. This axis only hunts excess — it says nothing about correctness.

**Report the three axes under separate headings, never merged or re-ranked against each other.** A change can legitimately pass one axis and fail another — correct behavior that breaks conventions, clean code that does the wrong thing, and a faithful implementation that's twice the size it needs to be are three different findings, and collapsing them hides the third almost every time.

Correctness findings raised here are addressed by editing and re-pushing — they don't re-enter `fix-qa` (SKILL.md, "Repair-mode scope"); that loop closed before this PR ever opened.

## Done when

- `pr-create` drafted `<id>-pr.md` before opening anything, and every acceptance criterion in it is pasted verbatim, not summarized.
- `## How it was verified` reflects `<id>-qa.md`/`<id>-qa-e2e.md`'s actual results, and any skipped verification states its reason in `## Deliberately skipped`.
- `pr-create` printed tracker updates rather than performing them.
- `pr-review`'s security gate ran, and completely, before either the standards, spec, or deletion axis started.
- A security finding blocked the PR and wrote `<id>-security-review.md`; a quality finding did not.
- All three axes ran as parallel sub-agents and are reported under separate, unmerged headings.
