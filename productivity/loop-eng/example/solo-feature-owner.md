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

**Phases A and B are your grilling**, done once at feature scale rather than per ticket. `spec` refuses a ticket that names only a want (§9 Q19) — and phase B is where a want stops being one. Cut the tickets well and every one of them takes route B; cut them badly and `spec` hands each one back to you.

---

## Why this matters more when you are alone

On a team, other people catch your mistakes. Alone, nobody does.

That is the actual problem the loop solves for you. Every stage boundary stands in for a person you do not have:

| Missing person | What replaces them |
|---|---|
| The QA engineer who checks it works | `verify` writes the end-user test in a session that never saw your code (§5.2) |
| The QA engineer who tries to break it | the adversarial pass — a second test plan written from the spec *before* yours is opened (§5.1a) |
| The code reviewer | `pr-review` reads the diff on three axes, cold (§6.2) |
| The colleague who says "did you actually run that?" | the control case (§5.5) and `verify-trace.md` |
| The PM who says "that's not your call to make" | `## Open gaps`, and `impl` refusing to start while one is unruled (§9 Q19) |
| The senior who asks "why did this break?" | `rca` runs before the fix, not after (§3.3) |

**You cannot review your own work by trying harder.** You already know what you meant. A session that never saw you write it does not.

The second row is the one people skip, and it is the one that bites. Checking that a feature works is easy when you built it — you walk the path you already had in mind. Nobody is walking the other paths, so nothing tells you they exist.

---

## Phase A — PRD to epics

Not the loop. Use plain sessions, then lock the decisions.

**Step 1. Read the PRD and find the fights.**

Ask an agent to list what the PRD does *not* say. That list is your real work.

```
"Read this PRD. List every decision it leaves open —
 things where two engineers would build different products."
```

**Step 2. Settle them.** Use whatever you settle ambiguity with — a grilling skill, an interview skill, a whiteboard. One option:

```bash
/interview-me <path-to-prd>
```

What matters is not the tool but the property: something asks, you answer, and **the answers land in the document** rather than in your memory of the conversation. An ambiguity you resolved but did not write down is one you will resolve differently next month.

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

Out comes `yt-11-spec.md`, in four sections:

```
## Acceptance criteria
AC-1  Given a creator selects a valid video file
      When they confirm the upload
      Then the file is stored and an ID is returned

AC-2  Given a file larger than the size limit
      When they confirm the upload
      Then it is rejected before any bytes are stored

## Non-goals
- Transcoding (YT-12), thumbnails (YT-13).
- Resumable upload. Interrupted means re-upload.

## Open gaps
[GAP-1] What is the size limit?               Status: awaiting <decider>
  Scenario:   a creator picks a 4GB raw camera file
  Not ours:   drives storage cost and what we can promise creators
  Options:    A 2GB (covers phone footage, cheap)
              B 20GB (covers camera originals, ~8x the bill)
  Recommend:  A for launch, revisit on the first complaint
```

Four criteria, say. Right-sized. Move on.

**`## Non-goals` is the same "out of scope" line you wrote in the ticket, now somewhere a machine reads it.** `verify` presses your criteria to their limit and drops any case that cites neither a criterion nor a non-goal — so this section is what stops a fresh session asking you about resumable upload on every single run.

**`## Open gaps` is the awkward one when you are alone**, and worth thinking through once rather than every ticket:

- **There is usually still a decider** — a founder, a PM, a design partner, the customer who asked for this. Send them the gap. The format exists so they can rule in a minute.
- **When there genuinely isn't one, `Not ours:` is the test.** If you cannot honestly write down why this is not your call, it is your call. Make it, record it as a criterion or a non-goal, and park nothing.

What you must not do is leave it blank and decide it silently in code. `impl` will not start while a gap is open — and alone, that refusal is the only thing standing between "I picked 2GB" and "2GB is what the product promises.

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

A fresh session. It never saw you write the code — and before it opens your test plan, it writes its own.

That ordering is the whole point. `yt-11-qa.md` is *your* list of what is worth checking, so reading it first would hand the fresh session your blind spots. Instead it reads only the spec and writes `yt-11-qa-adv.md`: the boundary cases, the concurrent ones, the dependency-down ones, and one question per criterion — *what assumption, if false, makes this return a plausible wrong answer instead of an error?*

Then three passes, in order:

| Pass | What runs | Who wrote it |
|---|---|---|
| **dev** | `yt-11-qa.md` at the seam | you, via `impl` |
| **adversarial** | `yt-11-qa-adv.md`, same seam | the fresh session, blind |
| **E2E** | `yt-11-qa-e2e.md`, the real client | the fresh session, blind |

A **control case** runs before all of them — an old test, untouched by your change. Green means your machine is fine. Red means stop, the environment is broken, and nothing below is evidence.

**The adversarial pass reports a coverage gap even when everything is green:** the cases it thought of that yours did not contain. Alone, that list is the closest thing you have to a colleague reading your test plan and raising an eyebrow. Five criteria might give you five cases and it twelve — the seven-case difference is the part nobody was ever going to mention to you.

**When something fails, it does not assume your code is wrong.** It rules between a broken machine, a broken change, and *a behaviour nobody ever decided* — that last one is a **spec gap**, and it goes back to you as a decision, not into a fix loop. Evidence lands in `yt-11-verify-trace.md`. Two retries on a code bug. Zero on a broken machine or a spec gap.

**Session 4 — pr-create.**

```bash
/loop-eng pr-create YT-11
```

Drafts `yt-11-pr.md`, then opens the PR from it. TL;DR at the top, criteria pasted in full, and the three case counts reported separately — *"5 dev, 12 adversarial, 4 end-user"* — rather than added together.

Alone, the PR body is not paperwork — it is the only written record of what you meant, six months from now. The split counts are part of that: they say the change was pushed on, not merely walked through.

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

## Five traps in this mode

**1. Component epics.** "The storage layer" can be finished while nobody can upload anything. Cut along what a user can do.

**2. Writing the spec and code in one session.** You will want to — the context is right there, and you are in a hurry because it is all on you. Do not. That session is grading its own homework, and alone there is nobody else to catch it.

**3. Skipping `verify` because you already know it works.** You are the only person who thinks so. That is the problem, not the reassurance.

**4. Deciding a gap in your head because you are also the PM.** The most natural move in this mode, and the most expensive. Wearing both hats does not merge them: you still made a product decision, you just left no record that you made one. Six months later nobody — including you — can tell a considered trade-off from a default you never noticed choosing. Write it in `## Open gaps` with the options and your recommendation, rule on it in the same sitting if there is nobody to send it to, and move. It costs a minute.

**5. Ten tickets in flight.** Owning the whole feature does not mean building it all at once. One ticket, one loop. The epic tracker exists so you can see progress without holding it all in your head.

---

## Where to look next

| File | What it holds |
|---|---|
| `../README.md` | the other walkthrough — joining an existing team |
| `file-upload-walkthrough.md` | one vague ticket in close-up, including what to do when each stage refuses |
| `../SPEC.md` §5.1a | why the adversarial pass exists, and what it still cannot catch |
| `../SPEC.md` §9 Q19 | the two spec routes, and why `impl` refuses to start on an open gap |
| `../SPEC.md` | the full design and the reasoning behind it |
| `../../interview-me/SKILL.md` | one option for the PRD phase — settling ambiguity before anything is built |
