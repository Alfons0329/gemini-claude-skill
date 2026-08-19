# `kb-update` — write learnings back, where the team can find them

Always the pipeline's last stage for a ticket (SKILL.md, "Resolving the ticket directory"). Reads `<id>-rca.md` on a bug ticket, `<id>-qa.md`, and the diff itself.

**The knowledge base lives in the target repo's `docs/` tree, not the progress repo.** This is the deliberate counterpart to where tickets live: personal working artifacts stay out of company git; durable documentation the team needs belongs in it. Conflating the two makes each one worse.

**Written on the feature branch**, so it reaches the team through the same PR review as the code — no silent writes into shared documentation, no separate approval path to remember.

## Where it goes

```
<repo>/docs/
├── README.md                     # orients a reader arriving cold
├── shared/                       # repo-wide, project-agnostic
│   ├── architecture-<topic>.md
│   ├── ops-<topic>.md
│   └── repo-orientation.md
├── project/<project-slug>/       # scoped to one project or epic
│   ├── README.md
│   └── design-<phase>.md
└── <initiative-slug>/            # a standalone effort with its own life
```

**Scope picks the directory.** True of the whole repository regardless of what you're working on → `docs/shared/`. True of one project or epic → `docs/project/<slug>/`. Every directory carries a `README.md` orienting someone arriving cold — a directory of documents with no entry point is a pile, not a knowledge base.

**If the project context file documents its own docs layout convention, that overrides the shape above** — the same rule `reference/pr-lifecycle.md`'s standards axis applies to code conventions holds here for documentation conventions. The layout above is this stage's fallback for a repo that documents nothing, not a house style to impose over an existing one.

## What to write

**Record only what was non-obvious** — a wrong assumption corrected, a convention discovered, a trap laid for the next engineer. Never restate what the diff already shows; a diff-restating entry is a second, staler copy of something `git log` already says better.

**On a bug ticket, this stops being improvisation.** `<id>-rca.md`'s *What would have caught it* list is already exactly this material — generalizable process rules, already sourced — and is this stage's primary input. Write those forward rather than re-deriving them.

**Harvest `ponytail:` markers** left in the diff (`reference/ticket-impl.md`) into a debt ledger under `docs/shared/` — one entry per marker, the ceiling it named and the upgrade path, so a deliberate shortcut stays visible to the team instead of rotting into "later means never."

**Close the loop back to every stage, not just `spec`.** A `docs/` entry alone isn't found automatically — no stage browses `docs/` on its own, each only reads the project context file (SKILL.md, "Reading the project context file" — this is true for every stage, not only `spec`). So where a `docs/shared/` entry records a convention some *future stage* would otherwise have to re-discover the hard way — a coding trap `impl` would re-hit, a precondition `verify` would need, not only something `spec` needs before writing acceptance criteria — also propose a one-line addition to the target repo's `CLAUDE.md` pointing at it: `See docs/shared/<file>.md for <what>.` Without this, a lesson this stage just wrote down would never reach any future ticket's session, and the pipeline would stop compounding across tickets — which is the entire point of writing it down at all.

## The graduation test — kernel or repo?

**Strip every proper noun from the candidate learning.** Something useful survives → it's a method improvement, not a repo fact, and belongs in the kernel skill itself (this file, `SKILL.md`, or a sibling `reference/*.md`) — no single repo owns it. Nothing survives → it's documentation, and lands in `docs/` per the scope rule above.

Mixing the two is how a portable kernel silently acquires one employer's conventions — the same failure mode `writing-skills`' Phase 2 proper-noun test exists to catch, applied here at the point where it's most likely to happen: right after a real lesson was just learned.

## Procedure

1. Read `<id>-rca.md` (bug tickets), `<id>-qa.md`, and the diff.
2. Draft the `docs/` entry (or entries) per the scope rule, plus a ledger entry for any `ponytail:` marker in the diff.
3. Run the graduation test on each candidate learning; route kernel-shaped ones to a follow-up edit of the kernel skill rather than into `docs/`.
4. For any `docs/` entry a future ticket's session — any stage, not only `spec` — would otherwise have to rediscover the hard way, propose the one-line `CLAUDE.md` pointer described above.
5. Commit the `docs/` (and any `CLAUDE.md`) changes on the feature branch alongside (or as a follow-up commit to) the code. If a parent epic tracker is present, append the one closing line — `<ticket-id>  done` or `<ticket-id>  blocked: <one line>` — per SKILL.md; never create the tracker if it isn't already there.
6. Append the progress line and stop.

## Done when

- Every `docs/` entry states something non-obvious — no entry merely restates the diff.
- Every bug ticket's *What would have caught it* items landed somewhere, sourced back to the RCA.
- Every `ponytail:` marker in the diff has a matching ledger row.
- Every candidate learning was run through the graduation test, and its destination (kernel vs. `docs/`) matches the result.
- Any `docs/` entry a future stage's session would need automatically found has a matching one-line pointer proposed in `CLAUDE.md` — the loop back is closed, not just written down.
- The parent epic tracker, if one exists, gained exactly one line — never more, never per-AC detail.
