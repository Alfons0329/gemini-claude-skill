---
name: writing-skills
description: The standard for writing a skill. Use when creating a new skill, editing a SKILL.md, or writing a project context file (CLAUDE.md, GEMINI.md, AGENTS.md).
---

The house standard for every skill in this repo family, and for the company-private skills built on top of it.

This is a **teacher**, not a worker. It holds method only — no company names, no paths, no credentials. There is no slot in it where a company fact would fit, which is what makes it publishable by construction rather than by review.

```
/writing-skills [skill-name]
```

Invoke it when writing a new skill, when editing an existing `SKILL.md`, or when a project context file needs rules added.

---

## Phase 1 — Decide whether to write one at all

Climb this ladder. Stop at the first rung that holds.

1. Is this one sentence? Say it in the project context file (`CLAUDE.md` / `GEMINI.md` / `AGENTS.md`) — it loads automatically and costs no invocation.
2. Does an installed skill already cover it? Use that one.
3. Is it a fact about one repo, not a method? It belongs in that repo's context file.
4. Only then: write a skill.

**Done when** you can name the rung you stopped on, out loud, in one sentence.

A skill earns its own file when it carries a **procedure** — ordered work with a shape you want repeated identically every run. Facts are not procedures.

## Phase 2 — Place it in a layer

Three layers, separated by how far each one travels.

| Layer | Holds | Example |
|---|---|---|
| **Public skills repo** | method, mental models, stage order | "run the control case before triaging a failure" |
| **Company skills repo** (private) | facts true across the whole company | "auth token is in `$API_TOKEN`; VPN binary at `<path>`" |
| **Repo context file** | facts true of one repository | "the test command is `<cmd>`; CI job is `<name>`" |

**One test decides it.** Take the sentence. Delete every proper noun. Something useful survives → it is method, and it belongs one layer up. Nothing survives → it is a fact, and it belongs where the fact is true.

Run this test again in the other direction whenever a method improvement discovered in a private repo moves toward the public one. That crossing is the only place a company fact can leak, so it is the only place that needs a gate.

**Done when** every section of the draft sits in exactly one layer, and you can say which.

## Phase 3 — Choose the invocation

**Default: user-invoked.** Only a human typing the name can start it. It costs zero context on every other turn, and no other skill can fire it by accident.

Make it **model-invoked** only when the agent must reach it on its own, or another skill must. State the reason in `SPEC.md`. A skill that runs work with side effects — commits, PRs, deploys — stays user-invoked, because auto-firing a stage is how a pipeline skips its own gates.

Mechanics differ per harness. Set the one your harness reads, and name the choice in `SPEC.md` so it survives a port:

- Claude Code — `disable-model-invocation: true` in the frontmatter.
- Codex — `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.
- Any harness without such a flag — say "user-invoked" in the first line of the body, so a reader knows the intent even where the harness cannot enforce it.

**Done when** the frontmatter and `SPEC.md` agree on the answer.

## Phase 4 — Write the frontmatter

```yaml
---
name: <matches the directory name>
description: <what it does, then when to reach for it>
---
```

The `description` is the only part of a model-invoked skill loaded on every turn, so it pays rent constantly. Three rules:

- **Lead with the defining word.** It does its triggering work at the front.
- **One trigger per branch.** Two phrasings of the same situation are one branch written twice.
- **Cut anything the body already carries.** The description is a pointer, not a summary.

A user-invoked skill's `description` is read by a human browsing a slash-command list. Write it as a plain one-line summary and drop the trigger phrasing — nothing is matching against it.

**Done when** every clause in the description names either what it does or a distinct situation that should reach it.

## Phase 5 — Lay out the file

Three tiers, ranked by how soon the agent needs the material:

1. **Steps** — the ordered actions, in the main file.
2. **Reference** — rules and definitions consulted on demand, in the main file.
3. **Disclosed reference** — pushed into `reference/<topic>.md` and reached by a pointer, loaded only when that pointer fires.

Push too little down and the main file bloats. Push too much and the agent misses what it needed.

**Branching decides it.** Material every run needs stays inline. Material only some runs reach goes behind a pointer.

Keep related material together under one heading — a definition, its rules, and its exceptions read as one thing or they read as three.

Structure the steps as numbered phases: setup, run, wrap up. Name the phases for what happens in them.

**Done when** a reader can follow the main file top to bottom without opening a `reference/` file, and every `reference/` file has exactly one pointer aimed at it.

## Phase 6 — Give every step a completion criterion

Each step ends on a condition the agent can check. Two properties matter:

- **Checkable** — can the agent tell done from not-done? A vague bound invites stopping early, with the remaining steps pulling attention forward.
- **Demanding** — "every acceptance criterion has a matching case" produces more work than "write some cases." The bar lives in the wording.

The strongest criteria are both.

**Done when** every phase ends on a line starting *"Done when…"* and each one names something observable.

## Phase 7 — Prune

Read the draft line by line and cut on four tests:

- **No-ops.** Does this line change behavior versus what the agent would do anyway? Settle disagreements by running the skill, not by arguing. When a line fails, delete the whole sentence.
- **Duplication.** Each meaning gets exactly one home, so changing behavior is a one-place edit.
- **Cache.** The environment is a source of truth. A skill that restates `package.json` scripts or a directory listing is a copy that goes stale. Record what the agent cannot find by looking — the unwritten convention, the reason behind a choice, the trap nothing confesses.
- **Relevance.** Does this still bear on what the skill does?

**Done when** one full pass produces no cut.

## Phase 8 — Write `SPEC.md`

Every skill ships `SKILL.md` and `SPEC.md` side by side, in a directory named after the skill.

`SKILL.md` is what the agent runs. `SPEC.md` is why it is shaped that way: the decisions taken, the alternatives rejected and the reason, the invocation choice from Phase 3, and any question still open.

**Done when** a stranger reading only `SPEC.md` can say why a plausible-sounding alternative was rejected.

---

## Reference — writing that steers

**Leading words.** Pick one compact word the model already knows and repeat it as a token, never as a restated sentence — *seam*, *ladder*, *control case*, *red*. It accumulates meaning across the document and anchors a whole region of behavior in a few characters. An invented word recruits nothing and costs definition tokens; reach for an existing one first.

Hunt for passages that collapse into one: "fast, repeatable, low-overhead" is *tight*. "A test you believe in" is *red*.

**Say what to do.** Naming a banned behavior drags it into context and makes it more available, not less. Write the target — "keep comments to one line" — so the banned version is never spoken. Reserve a prohibition for a hard guardrail with no positive phrasing, and pair it with the target even then.

**Write for many agents.** This repo's skills run on Claude Code, Gemini CLI, Antigravity CLI, and others:

- Name tools by their alternatives — `WebFetch` / `web_fetch` / `read_url_content`; `Grep` / `grep_search`.
- Use repository-relative paths — `shared/scripts/notion_to_markdown.py`, never a machine-specific home directory.
- Refer to the project context file generically — `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`.

---

## Done when

- The skill stopped on a named rung of the Phase 1 ladder.
- Every section sits in exactly one layer, and the proper-noun test agrees.
- Frontmatter `name` matches the directory name.
- The invocation choice is set in the frontmatter and explained in `SPEC.md`.
- Every phase ends on a checkable *"Done when"*.
- Every `reference/` file has exactly one pointer aimed at it.
- A pruning pass produced no cut.
- `SPEC.md` exists beside `SKILL.md`.
- No proper noun in the file names a company, a service, a person, or a machine-specific path.
