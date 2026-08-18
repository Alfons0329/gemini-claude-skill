# SPEC: `interview-me`

**Topic:** Interview-driven spec building — close open decisions through multiple-choice rounds, then write a document a fresh session can implement from.
**Status:** Consolidated. Supersedes the earlier cross-agent version at `interview/interview-me/`.

## Goal

One canonical skill, tuned for Claude Code, usable in **any** company or project. It is both a standalone tool and the interview engine the loop's `spec` stage delegates to (`../loop-eng/SPEC.md` §8).

## Lineage

Three inputs were merged:

1. **Thariq's spec workflow** (`@trq212`, popularised by [VelvetShark's video](https://youtu.be/ob9WWuYlS5Q)) — the core idea: start from as little as one sentence, let `AskUserQuestion` interview you, implement in a fresh session. Contributed the "questions must not be obvious" filter.
2. **This repo's earlier cross-agent version** — contributed visible gap classification, conflict handling, and meta-skill suggestion.
3. **A mature in-house implementation the author used daily** — contributed the two suppressor gap-classes, the question-quality bar, do-not-use criteria, priority ordering, stop conditions, self-regulation, and the separate output template.

Reconstructed as generic method. No employer names, ticket identifiers, internal acronyms, customer scenarios, or house conventions.

## Resolved Decisions

1. **Claude Code only — cross-agent support deliberately dropped.** `[DESIGN_DECISION]`
   Real `allowed-tools`, `AskUserQuestion` named directly, `$ARGUMENTS`, trigger phrases in the description. *Rationale:* generic tool naming (`ask_user` / `ask_question`) failed to reliably trigger `AskUserQuestion`, producing plain-text questions — the exact opposite of the intent. Productivity in the one harness actually used beats portability to harnesses that aren't.
   **This is a conscious exception to the repo-wide cross-AI-agent rule in `CLAUDE.md`.**

2. **The skill reads conventions; it never embeds them.** `[CONSTRAINT]`
   Test order, branch naming, commit format, and framework choices are read from `CLAUDE.md` at runtime and recorded under "Pre-filled context." *Rationale:* the in-house version declared itself project-independent while hardcoding its employer's test-order convention into the output template — silently imposing it on any other project. Reading at runtime is what actually makes the skill portable. Same decision as Q3 in `../loop-eng/SPEC.md`, now resolved there in §7.1.

3. **Two of the five gap classes exist to suppress questions.** `[NON_OBVIOUS]`
   `ALREADY_KNOWN` pre-fills silently; `DERIVABLE` states the assumption and confirms once in bulk. *Rationale:* the earlier version of this skill specified all five classes but implemented only the three that *generate* questions — so it had no mechanism to stay quiet. The suppressors are the operational form of "don't ask obvious questions."

4. **Recommended defaults become the first option, marked `(Recommended)`.** `[DESIGN_DECISION]`
   *Rationale:* turns each round into confirm-or-override rather than invent-from-scratch, which is materially faster and more accurate for the user.

5. **Bounded by design: ≤4 questions per round, self-regulation checkpoint after 3 rounds.** `[CONSTRAINT]`
   Paired with a counter-rule — *don't* stop early when the user defers a design decision with "whatever you think." *Rationale:* alignment stops paying once the back-and-forth costs more than the ambiguity it resolves, but deferring a genuine judgment call to Claude defeats the point of the skill.

6. **Output is written back into the input document, not to a parallel file.** `[DESIGN_DECISION]`
   The full template is used only when the input was a bare topic. *Rationale:* the primary use is closing named open questions in a spec that already exists; a second file would fork the source of truth.

## Consolidation

Three divergent copies existed. Resolved to one source and one install:

| Was | Now |
|---|---|
| `interview/interview-me/` (cross-agent) | removed — superseded |
| `~/.claude/commands/interview-me.md` (hand-patched hybrid) | removed — replaced by the skill install |
| in-house version (private) | remains private; contributed technique only |

Canonical source: this directory. Installed user-scoped to `~/.claude/skills/interview-me/` so it is available in every repo, not just this one — a requirement, since the skill's whole purpose is portability across projects and employers.

## Handover

1. Verify the install resolves: `/interview-me` should appear after `/reload-skills`.
2. First real use: close the open questions in `../loop-eng/SPEC.md` §9 — ten live gaps (Q3 and Q4 are resolved), each carrying a recommended default, which is ~3 rounds at 4 per round.
3. If `AskUserQuestion` is not used for every question, that is a bug in the skill, not a preference.

## Open Items

- The repo-wide "cross-AI-Agent actionable" rule in `CLAUDE.md` now has a documented exception. Decide whether to amend that rule or keep this as a one-off carve-out.
