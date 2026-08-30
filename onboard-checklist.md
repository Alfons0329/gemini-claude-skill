# Onboarding checklist

How to install this skill set on a new machine at a new company, and how to
set up the context files so the loop runs without hiccups.

Nothing here names an employer, a repo, or a stack. It works anywhere.

---

## 1. Install — five minutes

```bash
git clone <this-repo-url> ~/skills
cd ~/skills
./setup.sh
```

That script is idempotent — run it again any time. It:

- symlinks `loop-eng`, `writing-skills`, and `interview-me` into every agent
  skills directory that exists (`~/.claude/skills`, and `~/.gemini/skills` /
  `~/.antigravity/skills` if those agents are installed)
- creates `~/progress` as a **private** git repo, with a README saying so
- adds the progress-root line to `~/.claude/CLAUDE.md`

Flags: `--all` installs the interview-prep skills too. `--dry-run` prints what
it would do and changes nothing. Run the dry run first on a work laptop.

**Then restart your agent session.** Skills are loaded at startup. A symlink
made mid-session does nothing until you restart.

Confirm:

```bash
ls -l ~/.claude/skills          # loop-eng -> ~/skills/productivity/loop-eng
ls ~/progress                   # README.md
```

`loop-eng` will **not** show up in the session's skill list. That is correct —
it carries `disable-model-invocation: true`, so only you can start a stage.
`writing-skills` will show up. If neither does, the symlinks did not take.

### If the company forbids cloning personal repos onto the work machine

Copy the three skill directories instead of cloning:

```bash
mkdir -p ~/.claude/skills
cp -R /path/to/loop-eng ~/.claude/skills/loop-eng
```

Everything else in this document is unchanged. You lose `git pull` updates.

---

## 2. Where each kind of context goes

Four layers. Each answers a different question. Putting a fact in the wrong
layer is the single biggest source of friction.

| Layer | File | Holds | Committed? | Lifetime |
|---|---|---|---|---|
| 1 | the skill (`~/skills/...`) | the workflow itself — stage order, the artifact contract, when to stop | public repo | forever, every job |
| 2 | `~/.claude/CLAUDE.md` | facts true on **this laptop only** | never | this machine |
| 3 | `<repo>/CLAUDE.md` | facts true for **this repo**, for everyone on the team | yes, in the repo | that repo |
| 4 | `--human "…"` on one command | facts true for **this one ticket** | no — but the stage writes it into the artifact | one run |

The test, in daily form:

> Would a teammate need this? → layer 3.
> Only true on your laptop? → layer 2.
> True no matter who you work for? → layer 1.
> True only for this ticket? → layer 4.

A private company-skills repo, if you ever build one, slots between 1 and 2.

---

## 3. What to put in each file

### Layer 2 — `~/.claude/CLAUDE.md`

This file is **never created for you**. It does not exist until you write it.

Keep it tiny. Only things that are true about your machine, not your employer.
Every line here is loaded into every session in every repo, so a long one taxes
all of them.

```markdown
# Personal context

Loop-eng artifacts live under ~/progress/, one directory per ticket ID.
```

That one line is the whole requirement. `setup.sh` writes it.

Good candidates to add later: a non-default editor, a personal scratch
directory, a shell quirk. Bad candidates: the team's test command, the VPN
name, service names — those are layer 3, and putting them here means your
teammates never get them.

### Layer 3 — `<repo>/CLAUDE.md`

This is where the leverage is. Every fact here is one thing a cold session
stops having to guess, forever, for everyone.

Write it on day one with whatever you know, even if that is three lines. Add
one line every time you have to explain something to the agent twice. After a
few weeks a cold session knows what you know.

Template — delete the rows you cannot fill yet:

```markdown
# CLAUDE.md

## What this service is
One paragraph. What it does, who calls it, what it calls.

## Build and test
- Install:  <command>
- Test:     <command>
- One test: <command>
- Lint:     <command>

## Running it locally
What has to be true first — VPN, a config file, an env var, a tunnel.
If the local stack does not work yet, say so here. That is a fact too.

## Conventions
- Where tests live, and what they are named.
- What gets mocked at which seam.
- Anything a reviewer will ask for that is not obvious from the code.

## Gotchas
Things that surprised you. One line each.
```

Two rules that keep it working:

- **Every claim needs a command that proves it.** "Tests are run with `make
  test`" is useful. "The test suite is comprehensive" is not.
- **Delete stale lines when you find them.** A wrong `CLAUDE.md` is worse than
  no `CLAUDE.md` — the agent trusts it and stops checking.

The `kb-update` stage proposes additions to this file at the end of every
ticket. Take them. That is the mechanism that makes ticket 30 cheaper than
ticket 1.

### Layer 4 — `--human`

For the thing that is true this once and nowhere else.

```
/loop-eng spec ABC-123 --human "Only reproduces on the EU region. Scope to that."
```

The stage writes it into the artifact under `## Human input`, so the next
session sees it. Sessions do not talk to each other — anything you only say in
chat is gone.

**If you type the same note three tickets in a row, it was never per-ticket.**
Move it to layer 3.

---

## 4. The private progress repo

`~/progress` holds one directory per ticket: the ticket text, the spec, the QA
plan, the verify trace, the PR body, the running log.

It will contain real ticket IDs, real service names, and real root-cause
writeups. **Never give it a public remote.** If the company provides a private
internal git host and allows it, that is fine. Nothing else is.

Keep code and artifacts in two different places on purpose: artifacts in
`~/progress/<id>/`, code in the actual repo. The artifacts outlive the branch.

---

## 5. The loop itself

One ticket, several sessions, each with one job. The only thing that crosses
between sessions is what got written to disk.

| # | Command | Needs | Produces |
|---|---|---|---|
| 0 | *(you, by hand)* | the ticket text | `<id>-ticket.md` |
| 1 | `/loop-eng spec <id>` | ticket text | `<id>-spec.md` — acceptance criteria |
| 2 | `/loop-eng rca <id>` | bug tickets only | `<id>-rca.md` — root cause |
| 3 | `/loop-eng impl <id>` | the spec | code, `<id>-qa.md` |
| 4 | `/loop-eng verify <id>` | the QA plan | pass/fail + `<id>-verify-trace.md` |
| 5 | `/loop-eng pr-create <id>` | spec + QA | the PR |
| 6 | `/loop-eng pr-review <id>` | the PR | review comments |
| 7 | `/loop-eng kb-update <id>` | everything | repo docs + `CLAUDE.md` additions |

Repair loops: `/loop-eng impl <id> fix-qa` and `... fix-sec`. Both are started
by you, never by a session.

**One stage, one session. Never two.** The point of a fresh `verify` session is
that it never saw `impl` reason its way to the answer. A session that does both
is grading its own homework.

---

## 6. Ramping up on an unfamiliar codebase

**Week 1 — run `spec` only.** It is the one stage that needs no working local
stack, and getting a stack running at a large company routinely takes a week.
You still get value on day one.

**Week 1 — start that repo's `CLAUDE.md`.** Three lines is a fine start.

**Month 1 — ask for bug tickets on purpose.** A feature ticket teaches you
where files live. A bug ticket forces `rca` to read git history and old
commits, which teaches you *why* the code is shaped the way it is. That is the
faster education.

**Month 1 — `verify` may be unrunnable. Skip it, but never silently.** Say so
in the PR body, with the reason. A skipped step that is written down is a known
gap. A skipped step that is not is a lie.

**Month 2 — the full loop**, once the stack works.

**Month 3 — graduate what you learned.** Strip the proper nouns from a lesson.
If something survives, it is a method and belongs one layer up. If nothing
survives, it was a fact — file it in that repo's `CLAUDE.md`.

---

## 7. Gotchas, found the hard way

- `~/.claude/CLAUDE.md` is **never auto-created**. No error tells you it is
  missing; sessions just quietly know less.
- Skills load **at session start**. Symlink, then restart.
- A skill with `disable-model-invocation: true` will not appear in the session
  skill list. That is on purpose, not a broken install.
- `setup.sh` refuses to overwrite a real directory sitting where a symlink
  should go. If it prints `SKIP`, you have an old copied version there — delete
  it and re-run.
- Never brief a session on what the previous session did. If a session cannot
  proceed from the committed artifacts alone, **that is the finding.** Write it
  down. Do not help it.
- A fallback that fires silently looks exactly like a real result. If a stage
  had to guess, it should say so out loud.

---

## 8. When you leave

Take the method, leave the facts.

- `~/progress` and every repo `CLAUDE.md` stay behind. They are the company's.
- Anything that graduated to layer 1 comes with you — but check it first: strip
  every proper noun, and confirm nothing employer-specific rode along in the
  wording or the examples.
- Before pushing anything public, grep the diff and the history for ticket ID
  patterns, internal hostnames, and service names.
