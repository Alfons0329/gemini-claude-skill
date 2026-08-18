# One person, one whole feature

A walkthrough for the other common shape: a small structured company where one engineer owns a feature end to end — PRD, design, build, test, ship.

The running example is a video site. Two epics: **upload a video**, **play a video back**.

---

## Read this first

**The loop starts at "you have a ticket."** Everything before that — turning a PRD into epics, turning epics into tickets — is not in it, on purpose. `SPEC.md` §1 says so: that is tech-lead scope, and it is deferred.

So this walkthrough has three phases, and only the third one is the loop.

| Phase | What happens | Harness? |
|---|---|---|
| A | PRD → epics | no |
| B | epic → tickets | no |
| C | each ticket → shipped | **yes** |

Phases A and B are described here anyway, because a good phase C on badly-cut tickets is wasted effort.

---

## Why this matters more when you are alone

On a team, other people catch your mistakes. Alone, nobody does.

That is the actual problem the loop solves for you. Every stage boundary stands in for a person you do not have:

| Missing person | What replaces them |
|---|---|
| The QA engineer | `verify` writes the end-user test in a session that never saw your code (§5.2) |
| The code reviewer | `pr-review` reads the diff on three axes, cold (§6.2) |
| The colleague who says "did you actually run that?" | the control case (§5.5) and `verify-trace.md` |
| The senior who asks "why did this break?" | `rca` runs before the fix, not after (§3.3) |

**You cannot review your own work by trying harder.** You already know what you meant. A session that never saw you write it does not.

---

## Phase A — PRD to epics

Not the loop. Use plain sessions, then lock the decisions.

**Step 1. Read the PRD and find the fights.**

Ask an agent to list what the PRD does *not* say. That list is your real work.

```
"Read this PRD. List every decision it leaves open —
 things where two engineers would build different products."
```

**Step 2. Settle them.**

```bash
/interview-me <path-to-prd>
```

This is what `interview-me` is for: ambiguity where different people would choose differently. It asks, you answer, and the answers get written into the document.

Do this **before** any epic exists. Changing your mind is free here and expensive later.

**Step 3. Cut epics along user stories, not along code.**

```
EPIC-1  As a creator, I upload a video and it becomes watchable.
EPIC-2  As a viewer, I play a video and it plays smoothly.
```

Not "the storage layer" and "the transcoder." Those are components. A component epic can be 100% done while no user can do anything.

**Test for a good epic:** can you say what a user can do when it is finished? If not, re-cut it.

---

## Phase B — epic to tickets

Still not the loop. Do it by hand. It takes an hour and it decides everything after.

```
EPIC-1  Upload a video
├── YT-11  accept a file and store it
├── YT-12  transcode to three resolutions
├── YT-13  generate a thumbnail
└── YT-14  show upload progress to the creator

EPIC-2  Play a video back
├── YT-21  stream a stored video
├── YT-22  switch quality when bandwidth drops
└── YT-23  resume where the viewer left off
```

**One rule for sizing.** A ticket is the right size when its acceptance criteria fit in one `impl` session.

Roughly: **three to six criteria.** Ten means it is two tickets. One means it is probably part of another.

You do not know the criteria yet — `spec` writes those. So size by feel now, and **split when `spec` comes back with twelve of them.** That is the signal, and it is free to act on.

**Make the folders.**

```bash
mkdir -p ~/progress/epic-1-upload/YT-1{1,2,3,4}
mkdir -p ~/progress/epic-2-playback/YT-2{1,2,3}
```

Grouping is free-form — stages find a ticket by searching for its ID (§9 Q13).

**Make one tracker per epic.** Coarse only:

```
~/progress/epic-1-upload/epic-ac-tracker.md

YT-11  done
YT-12  done
YT-13  blocked: no GPU box yet
YT-14
```

Done or not done. Nothing else. The epic is the CEO — it wants each unit's status, not its engineering detail (§9 Q17).

---

## Phase C — one ticket, end to end

This is the loop. Here is `YT-11` in full.

**Before anything.** Write the ticket yourself — there is no tracker handing you one:

```
~/progress/epic-1-upload/YT-11/yt-11-ticket.md

Accept a video file upload and store it so later stages can find it.
Part of EPIC-1. Creator picks a file, it lands in storage, we get an ID back.
Out of scope: transcoding (YT-12), thumbnails (YT-13).
```

Writing "out of scope" here is worth the thirty seconds. It is what stops one ticket eating its neighbours.

**Session 1 — spec.**

```bash
/loop-eng spec YT-11
```

Out comes `yt-11-spec.md`:

```
AC-1  Given a creator selects a valid video file
      When they confirm the upload
      Then the file is stored and an ID is returned

AC-2  Given a file larger than the size limit
      When they confirm the upload
      Then it is rejected before any bytes are stored
```

Four criteria, say. Right-sized. Move on.

**Session 2 — impl.**

```bash
/loop-eng impl YT-11
```

It climbs the ladder first (§4) — *does this need building? does the framework already do it?* Alone, this rung matters more than usual: there is nobody to say "we already have a helper for that."

Then red→green, one criterion at a time. It writes `yt-11-qa.md` — your test plan — and a bare scaffold for the end-user test.

It will stop once to confirm a seam. That is the one place it waits (§9 Q7).

**Session 3 — verify. This is the one that saves you.**

```bash
/loop-eng verify YT-11
```

A fresh session. It never saw you write the code.

It runs a **control case** first — an old test, untouched by your change. Green means your machine is fine. Red means stop, the environment is broken, and nothing below is evidence.

Then it writes the real end-user test itself and runs it. It is allowed to disagree with you, and it does not know what you were hoping would pass.

**When it fails, it does not assume your code is wrong.** It rules between a broken machine and a broken change, and writes the evidence to `yt-11-verify-trace.md`. Two retries on a code bug. Zero on a broken machine — you go fix the machine.

**Session 4 — pr-create.**

```bash
/loop-eng pr-create YT-11
```

Drafts `yt-11-pr.md`, then opens the PR from it. TL;DR at the top, criteria pasted in full.

Alone, the PR body is not paperwork — it is the only written record of what you meant, six months from now.

**Session 5 — pr-review.**

```bash
/loop-eng pr-review YT-11 <pr-url>
```

Security gate first, blocking. Then three axes: does it follow the rules, does it match the spec, **what can be deleted**.

That third axis is the one you cannot do for yourself. Your code always looks like the right size to you.

**Session 6 — kb-update.**

```bash
/loop-eng kb-update YT-11
```

Writes what you learned into the repo's `docs/`. Then append one line to the epic tracker:

```
YT-11  done
```

---

## Then the next ticket

Repeat for `YT-12`. And `YT-13`.

**It gets faster, and here is why.** Each `kb-update` writes into `docs/` and into `CLAUDE.md`. By `YT-14`, the cold session already knows how your storage layer works, because `YT-11` wrote it down.

Ticket 1 is slow. Ticket 8 is not.

---

## Four traps in this mode

**1. Component epics.** "The storage layer" can be finished while nobody can upload anything. Cut along what a user can do.

**2. Writing the spec and code in one session.** You will want to — the context is right there, and you are in a hurry because it is all on you. Do not. That session is grading its own homework, and alone there is nobody else to catch it.

**3. Skipping `verify` because you already know it works.** You are the only person who thinks so. That is the problem, not the reassurance.

**4. Ten tickets in flight.** Owning the whole feature does not mean building it all at once. One ticket, one loop. The epic tracker exists so you can see progress without holding it all in your head.

---

## Where to look next

| File | What it holds |
|---|---|
| `../README.md` | the other walkthrough — joining an existing team |
| `../SPEC.md` | the full design and the reasoning behind it |
| `../../interview-me/SKILL.md` | the PRD phase — settling ambiguity before anything is built |
