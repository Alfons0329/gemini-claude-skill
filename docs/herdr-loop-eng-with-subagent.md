# herdr, subagents, and the loop-eng stage boundary

Two questions, answered from the running system on 2026-09-02.

1. What does [herdr](https://herdr.dev) actually buy `loop-eng`?
2. Can the six stages run as subagents in one window instead of six windows?

Short answers: herdr buys you the end of babysitting, without touching the
pipeline. Subagents cannot replace the windows — one of the reasons is a hard
blocker you would hit in the first minute — but they have a real place *inside*
a stage.

The setup and the tmux-to-herdr mapping live in the dotfiles repo, at
`docs/herdr-loop-eng-tutorial.md` (branch `herdr`, commit `893a569`). This file
is the `loop-eng` side: what the pipeline requires, and why the two questions
have the answers they do.

---

## 1. What herdr changes

**Nothing about the pipeline.** Stage order, the artifact contract, one stage
per session, only-committed-files-cross — all unchanged. herdr is a
multiplexer. It replaces the tmux window, not the stage.

What it changes is the thing you actually spend attention on.

### The problem it solves

With four tickets in flight, the question you ask thirty times a day is *which
of these is waiting on me?* In tmux, answering it means visiting every window,
because a session that stopped ten minutes ago on a permission prompt looks
exactly like one that is still thinking.

herdr classifies each agent pane as `working` / `blocked` / `done` / `idle` and
shows it in a sidebar. `blocked` is the state that matters — it means an agent
is sitting on a question, burning your wall-clock while you look elsewhere.

```sh
herdr agent list
herdr agent wait w1:t2 --until blocked --until done --timeout 900000
```

That second line is the shape worth internalising: **block until something
needs you, instead of polling.** It converts the pipeline from "check on six
windows" to "get told."

### Why this matters for `loop-eng` specifically

`loop-eng` is a *staged* pipeline with an explicit rule about when a stage waits
versus when it exits (`SKILL.md`, "Waiting vs. exiting"). That rule is decided
by how long the operator would be away:

| | Wait (block in-session) | Exit and get re-invoked |
|---|---|---|
| When | Answerable in seconds | Requires leaving the keyboard |
| Example | `impl` confirming a seam | `verify`'s manual E2E checklist |

The left column is exactly what `--until blocked` detects. The cost of a
blocking checkpoint has always been that *you have to notice it*. herdr makes
noticing free, which makes the left column cheaper, which means fewer stages
have to exit and pay for a full cold session to ask a ten-second question.

That is the whole benefit, stated plainly: **herdr lowers the price of a
blocking question, so the pipeline can use more of them.**

### The line not to cross

herdr can drive its own panes — `herdr agent prompt`, `herdr pane send-keys`.
Those fire a stage. Firing a stage from a script removes the checkpoint that
makes the boundary a boundary.

The dotfiles tutorial has the full fine/not-fine table under "The boundary you
must not cross." The one-line version: **observing and staging are fine, firing
is not.** `herdr pane send-text` types a command without submitting it — it
removes the typing, not the decision, which is the correct amount to remove.

---

## 2. Six stages as subagents in one window

**No — and there are three reasons, in descending order of how fast they bite.**

### Reason 1: a subagent cannot invoke `/loop-eng` at all

`productivity/loop-eng/SKILL.md` carries `disable-model-invocation: true`. That
flag means exactly what it says: a model cannot reach the skill. Only a human
typing the command can.

A subagent is a model.

This is observable right now, not a prediction. In the session that wrote this
file, `~/.claude/skills/` contains `loop-eng` on disk, and the session's own
available-skills list does not include it. The skill is installed and
unreachable, on purpose.

So a subagent has exactly one way to run a stage: the parent pastes the stage's
instructions into the subagent's prompt. Which fails for the next reason.

### Reason 2: the parent becomes the leak

If the parent briefs the subagents, then one context has read `spec`'s
reasoning, `impl`'s reasoning, and `verify`'s reasoning. That is precisely the
context the pipeline is built to prevent from existing.

`verify` is valuable because it never saw `impl` talk itself into an answer.
The cold run on 2026-08-30 (`productivity/loop-eng/example/smb-run-2026-08-30.md`)
is the demonstration: `pr-review`, which had not seen `impl` reason, found that
the spec's "dedicated local Samba user" was not literally what got built, and
that an acceptance criterion tested half of what it claimed. `impl` had
rationalised both. A sibling subagent briefed by the same parent inherits the
rationalisation.

A briefing is not a committed artifact. Rule 3 — *only committed files cross a
boundary* — is violated the moment the parent summarises.

### Reason 3: subagents cannot ask, and `loop-eng` asks a lot

This is the caveat you already identified, and it is worse than it looks
because **the failure is silent**. A subagent with no way to ask either guesses
and reports success, or stalls. Both come back as a report that reads fine.

The stages need a human at these named points:

| Stage | Where it needs you | Source |
|---|---|---|
| `spec` | closing scope on an ambiguous ticket | the smb-1 run interviewed the operator on six points |
| `impl` | **seams — "the one blocking checkpoint"** | `reference/ticket-impl.md:34` |
| `impl` | no runner documented → ask once rather than guess | `reference/ticket-impl.md:41` |
| `verify` | environment failure → escalate immediately, 0 retries | `SKILL.md`, Escalation |
| `verify` | wrong assertion / wrong test step → operator decides | `reference/ticket-verify.md:65-66` |
| `verify` | no E2E tooling → writes the checklist and exits | `reference/ticket-verify.md:42-49` |
| `pr-create` | no PR host documented → ask | the smb-1 run hit this and asked |
| any | code bug still failing after 2 attempts → wait for direction | `SKILL.md`, Escalation |

The escalation table is the sharpest case. An environment failure gets **zero**
retries, because a thousand attempts give a thousand identical failures — the
correct behaviour is to stop and ask. A subagent that cannot ask has no correct
behaviour available to it there.

### What this means

The multi-window setup was never a workaround. **It is the mechanism.** Six
windows are six sessions, and a session boundary is the only thing that makes a
stage's isolation real.

You reached for subagents to solve a real problem — not wanting to babysit six
windows. That problem is real. Subagents are the wrong fix for it.

**herdr is the right fix.** `herdr agent list` and `--until blocked` remove the
babysitting without removing the boundary. Same six sessions; you just stop
having to check on them.

---

## 3. Where subagents *do* belong

Inside a single stage, for read-only fan-out with no decision attached.

The test: **does the work end in a question or a commit?** If it ends in a
finding the parent stage judges, a subagent is right. If it ends in a decision
or a write, it is not.

Precedent from the cold run — `pr-review` ran its three review axes
(standards / spec-match / deletion) as parallel subagents, and that was correct:

- each axis is a read-only analysis of the same diff
- none of them decides anything; they return findings
- the `pr-review` **session** — a real session, invoked by you — owns the
  verdict and posts it

| Fits a subagent | Needs its own session |
|---|---|
| the three review axes in `pr-review` | any of the seven stages |
| "find every caller of this function" during `rca` | anything that asks the operator |
| "does this repo already have this helper?" — the ladder's rung 2 in `impl` | anything that commits, pushes, or opens a PR |
| surveying test conventions before writing cases | anything whose isolation is the point |

Note what the left column has in common: every entry is a **search**, and the
answer comes back as evidence, not as a choice.

---

## 4. So what should the layout be?

Unchanged in structure, better in ergonomics.

- **One herdr session per epic.** One tab per ticket, one pane per stage —
  the same shape as the tmux session-per-epic, window-per-stage layout in the
  screenshot, which is what the dotfiles tutorial maps over.
- **Close a stage's pane when the stage reports and stops.** Do not reuse it.
  Reuse is how two stages end up in one context.
- **Let the sidebar tell you who is blocked.** Do not visit panes to find out.
- **Subagents live inside a pane**, spawned by the stage session that is already
  running there, for searches only.

The thing you are protecting is one sentence: *the session that ran `impl` must
not run `verify`.* Every rule above is downstream of it, and neither herdr nor a
subagent gets to soften it.

---

## See also

- `~/code/dotfiles/docs/herdr-loop-eng-tutorial.md` (branch `herdr`) — install,
  the tmux→herdr mapping, epic layout script, remote/build-server use, and the
  full boundary table
- `productivity/loop-eng/SKILL.md` — "One stage one session", "Waiting vs.
  exiting", "Escalation"
- `productivity/loop-eng/example/smb-run-2026-08-30.md` — the cold run, and what
  cross-session isolation actually caught
