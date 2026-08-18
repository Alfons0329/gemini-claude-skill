# Specification: Loop Engineering — Phase 2 (Portable Kernel Extension)

> ## ⛔ NOT ACTIVE — NOT A BUILD TARGET
>
> Deferred reference design for a scope the active loop does not have. **Do not read, cite, or draw requirements from this file when working on Phase 1** — `../SPEC.md` is complete and self-contained on its own. Nothing here is installed, implemented, or planned.

**Status:** Deferred. Not being built. Kept as a reference design in case scope grows past a single IC (e.g. onboarding a team, or taking on tech-lead-shaped ambiguity ownership). Revisit only when the pain this solves is actually felt — per the doctrine's own rule against building infrastructure ahead of a hypothesis.

## 1. What this tier is for

Where Phase 1 (`../SPEC.md`) is one engineer's ticket lifecycle, Phase 2 is about portability: taking that lifecycle and making it something you can hand to a different team, stack, or company without rewriting it — plus the meta-work of onboarding others onto it and managing session continuity across long efforts.

## 2. Kernel vs. build analogy

- **Kernel space** — generic mindset, workflows, skill definitions, config templates. Zero company/stack secrets. Portable across any team.
- **User space** — project-specific tracker IDs, CI/test stack, coding standards, release process.

**Phase 1 already implements this split**, and did so without any of the machinery below: one kernel skill installed user-level, with every repo-specific fact living in that repo's `CLAUDE.md` (`../SPEC.md` §7.1). Anything in this document would therefore be an *extension* of that split, not a replacement for it — and would have to justify itself against a solution that already works and costs nothing.

## 3. The five rules (from the source framework)

1. No hypothesis without a loop — a failing command with output, before any theory.
2. One decision per session.
3. Reference artifacts by path; don't restate them.
4. Recommend and wait — anything touching someone else's work is proposed, not applied.
5. Additive over destructive — nothing renamed or deleted as a side effect of adoption.

## 4. Skill inventory — corrected against the real `mattpocock/skills` repo

The original draft of this document named 13 skills across 4 layers, attributed loosely to "Matt Pocock's kernel." Verified against the actual repo (MIT licensed) via the GitHub API, the mapping is:

| Original name | Real-repo status | Note |
|---|---|---|
| `setup-harness` | ≈ `setup-matt-pocock-skills` | close analog, renamed |
| `grilling` | `grilling`, `grill-me` (productivity), `grill-with-docs` (engineering) | 3 distinct variants exist, not 1 |
| `research` | ✅ `research` | matches |
| `codebase-design` | ✅ `codebase-design` | matches |
| `domain-modeling` | ✅ `domain-modeling` | matches |
| `wayfinder` | ✅ `wayfinder` | matches |
| `to-tickets` | ✅ `to-tickets` | matches |
| `diagnose` | `diagnosing-bugs` | renamed; full content already pulled into `../SPEC.md` §5 |
| `triage` | ✅ `triage` | matches |
| `merge-harness` | no exact match — closest are `resolving-merge-conflicts` and `setup-matt-pocock-skills` | this repo's own synthesis |
| `handoff` | ✅ `handoff` (productivity) | matches |
| `bootcamp` | **not present anywhere in the source repo** | own invention — own it explicitly if kept, don't attribute to Matt Pocock |
| `harness-router` | **not present anywhere in the source repo** | same — own invention |

Skills in the real repo not previously listed here: `ask-matt`, `code-review` (used in Phase 1 §6), `implement` (used in Phase 1 §4), `improve-codebase-architecture`, `prototype`, `tdd` (used in Phase 1 §4), `to-spec`, `teach`, `writing-great-skills`.

**Important correction:** the "config seam" (`docs/agents/{issue-tracker,artifact-paths,conventions,domain}.md`) and the "Front Door vs. Primitive" invocation split described below are **this repo's own extensions**, not literal Matt Pocock patterns. His actual `.agents/` directory (`invocation.md`, `writing-docs.md`) documents a different axis entirely — **model-invoked vs. user-invoked** (a frontmatter flag, `disable-model-invocation: true`, controlling whether the AI can auto-fire a skill or only a human typing its name can reach it). Don't present the config-seam idea as sourced from his repo if this is ever published — it should be credited as original design inspired by the kernel/build-split concept, not a direct port.

## 5. Config Seam (original design, not from the source repo)

Four contract files in `docs/agents/`, synthesized from free-form input at setup time:

1. `docs/agents/issue-tracker.md` — tracker type (Jira, Linear, GitHub, local markdown) and query/update commands.
2. `docs/agents/artifact-paths.md` — target locations for specs, QA docs, learning records.
3. `docs/agents/conventions.md` — build/lint/test/branch/commit-message formats.
4. `docs/agents/domain.md` — project glossary, domain concepts, ADR links.

## 6. Distribution mechanism (revised)

The original draft specified a bash CLI (`setup-loop-eng --phase --codebase --human --overwrite --global`). The real repo doesn't do this — it distributes via the Claude Code plugin marketplace or `npx skills@latest add`, and binds project specifics via an **in-session skill** (`setup-matt-pocock-skills`), not an external script. If Phase 2 is ever built, prefer that model: a skill invoked inside a session, not a standalone installer binary.

## 7. Privacy / distribution architecture (if ever made public)

Three-tier separation, so the public kernel repo never carries personal or company data:

- **Tier 1 — public kernel**: skill definitions, doctrine, templates. Zero URLs, zero org names, generic concept language only.
- **Tier 2 — private runtime input**: actual company docs / internal wiki links, passed at runtime (a flag value or a local gitignored file), never committed to the public repo.
- **Tier 3 — generated per-project seam**: `docs/agents/*.md`, generated fresh inside whatever target repo runs the setup skill — also never lives in the public skill repo.

## 8. Atomicity constraint (if ever built)

Phase 1 and Phase 2 should not coexist in the same active loop — mixing creates conflicting session contracts. A switch between them (or a guideline update) should be an atomic replacement, not a partial merge. This constraint only matters once there's an installer to enforce it; Phase 1 alone has no such switch to protect.
