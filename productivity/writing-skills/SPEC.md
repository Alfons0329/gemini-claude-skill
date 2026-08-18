# Specification: `writing-skills`

**Status:** Active.
**Scope:** The authoring standard for every skill in this repository, and for the private company-specific skills built on top of a clone of it. Governs form — layout, frontmatter, invocation, pruning. It does not govern what any individual skill does.

## 1. Why this exists as its own skill

`loop-eng` is the first skill here written to be handed to a cold session and built from a spec, and it will not be the last. Without a written standard, each one is laid out from whatever the authoring session happened to recall, and the set drifts in shape even where every individual skill is correct.

The role is a **teacher**, not a worker: it produces other skills, and it is never part of a daily loop. Expect to invoke it a handful of times a year.

## 2. Why not depend on `mattpocock/skills` directly

The obvious move is to install [`writing-for-agents`](https://github.com/mattpocock/skills) and point every authoring session at it. Three facts about the intended deployment rule it out:

1. **A `git clone` has to be sufficient.** This repository gets cloned onto a corporate machine where `npx` may be proxied, allow-listed, or unavailable. A standard reachable only through a package fetch is a standard that is sometimes absent.
2. **The upstream name is not stable.** `writing-great-skills` was renamed to `writing-for-agents` with no alias. Anything pinned to the old name broke. A document depended on for years should not be able to rename itself.
3. **It does not carry the rule this repository most needs** — the boundary between the public method and private company facts (§3). That rule is the whole reason a standard is required here rather than merely useful.

Its *ideas* are used heavily and credited in `NOTICE.md`. What is rejected is the runtime dependency, not the content.

## 3. The three-layer split

| Layer | Holds | Lifetime |
|---|---|---|
| Public skills repository | method, mental models, stage order | permanent |
| Company skills repository (private) | facts true across one company | one employer |
| Repository context file (`CLAUDE.md` / `GEMINI.md` / `AGENTS.md`) | facts true of one repository | one repository |

This is `../loop-eng/SPEC.md` §7.1 applied one level up. There, the kernel/user-space split separated a portable skill from one repository's facts. Here the same split separates a portable *skill set* from one company's, with the per-repository layer unchanged beneath both.

**A single test decides placement: strip every proper noun.** Something useful survives → method, one layer up. Nothing survives → a fact, filed where it is true.

The same test was already written for a different purpose — `../loop-eng/SPEC.md` §9 Q5 uses it to route a learning between the kernel and a repository's context file. One rule now serves three jobs. That is deliberate: a second, similar-but-different test would be a rule to remember and get wrong.

**The test has one enforcement point that matters** — the moment a method improvement discovered while writing a private skill moves toward the public repository. Every other direction is safe. Gating that one crossing is cheaper and more reliable than auditing whole files.

**Consequence: the standard is publishable by construction.** It contains no slot a company fact could occupy, so none can leak, and publishability stops depending on reviewer discipline. Same argument as `../loop-eng/SPEC.md` §7.1, same conclusion.

## 4. Invocation — model-invoked, deliberately

Phase 3 of `SKILL.md` sets the house default to **user-invoked**: zero standing context cost, and no skill can fire another by accident. This skill overrides that default, and the override is the kind Phase 3 requires a reason for.

**The reason is the primary use case.** The next consumer is a cold implementation session writing seven files against a finished spec. A user-invoked standard only reaches that session when the human remembers to type its name in each one; the failure is silent, and produces exactly the drift the standard exists to prevent. Model-invocation makes the standard load when a `SKILL.md` is touched, which is the only moment it is needed.

**The cost is one always-loaded description line**, which is why the description is written as a pointer rather than a summary.

**`loop-eng` does not get this treatment.** It commits work and opens pull requests, and its `SPEC.md` §3.1 forbids chaining stages inside one session. An agent able to fire it autonomously is an agent able to skip the boundary that makes the pipeline's verification trustworthy. It stays user-invoked.

## 5. Why the ladder comes first

Phase 1 asks whether to write a skill at all, before any question about how to write one. This ordering is the point: most candidate skills are a fact, a one-liner, or something an installed skill already does, and each of those is better served by the repository's context file — which loads automatically and costs no invocation.

A standard that opened with frontmatter would produce well-formed skills that should not exist. Same shape as the laziest-solution-first ladder in `../loop-eng/SPEC.md` §4, applied to documents instead of code.

## 6. Scope decisions

- **New skills only.** The seven existing skills in `interview/` and `productivity/` are not retrofitted. They work, and rewriting them buys consistency at the cost of churn in files that are not misbehaving. Retrofit one when it misbehaves, not on a schedule.
- **One file, no `reference/` directory.** The standard is short enough to read top to bottom, and every phase applies on every run. Disclosing part of it behind a pointer would hide material each run needs — the failure mode Phase 5 warns about. If it grows past what one sitting can hold, the split is by phase, not by topic.
- **No installer, no link script here.** How skills reach `~/.claude/skills/` is a property of the machine, not of the standard. Keeping it out means the standard says nothing that a different harness would have to contradict.

## 7. Open questions

**Q1 — What prefix marks a company skill?**
The public and private sets both install into one directory, so two skills sharing a name is a coin flip about which resolves. A short company prefix on the private set removes the collision. Deciding late is expensive: a rename breaks every document that names the skill, which is exactly how the upstream rename in §2 caused damage.
*Recommended default:* a short lowercase prefix chosen on the first company skill and never changed.

**Q2 — Does the standard govern the context files it names?**
`SKILL.md` Phase 1 routes one-line rules into `CLAUDE.md` / `GEMINI.md` / `AGENTS.md`, and the frontmatter description claims those files as a trigger, but no phase says how to structure one. `../loop-eng/SPEC.md` §7.1 already rules on what the loop *reads* from that file. The gap is what belongs in it generally.
*Recommended default:* add one phase covering context files, and keep the boundary explicit — this skill governs how such a file is written; `loop-eng` governs what the loop reads from it. Neither restates the other.
