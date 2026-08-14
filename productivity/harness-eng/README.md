# harness-eng — first three months

A walkthrough for adopting this harness from day one on a new team, in an unfamiliar codebase.

One ticket becomes several focused sessions, each with one job. The only thing crossing between them is what got committed. `SPEC.md` is the full design and the reasoning behind every decision; this file is how to actually start.

---

## Setup — ten minutes, day one

```bash
git clone git@github.com:Alfons0329/gemini-claude-skill.git ~/skills
mkdir -p ~/.claude/skills
ln -sf ~/skills/productivity/harness-eng    ~/.claude/skills/
ln -sf ~/skills/productivity/writing-skills ~/.claude/skills/
ln -sf ~/skills/productivity/interview-me   ~/.claude/skills/
```

Symlinks rather than copies, so `git pull` updates every installed skill at once.

```bash
mkdir -p ~/progress && cd ~/progress && git init
echo "Personal notes. Real ticket IDs inside. Never add a public remote." > README.md
git add -A && git commit -m "init"
```

Then one line in your **personal** context file, `~/.claude/CLAUDE.md` — not any team repo's:

```
Harness artifacts live under ~/progress/, one directory per ticket ID.
```

Nothing else to install. No config, no CLI, no per-repo copies.

---

## Week 1 — `spec` only

There is no working local stack yet. At a large company that takes one to two weeks. Run the one stage that needs nothing:

```bash
mkdir -p ~/progress/<ticket-id>
# paste the ticket text into ~/progress/<ticket-id>/<ticket-id>-ticket.md

/harness-eng spec <ticket-id>
```

Read what comes back. Where the spec is wrong, the ticket was ambiguous — which is now a specific question to ask your team instead of a vague feeling that you are lost.

---

## Month 1 — take bug tickets on purpose

```bash
/harness-eng spec <ticket-id>
/harness-eng rca  <ticket-id>     # bug tickets only
```

`rca` makes you read git history and old commits to explain why a defect shipped.

**A story ticket teaches you where the files are. A bug ticket teaches you why they are like that.** Ask for bugs early, deliberately.

Start each repo's `CLAUDE.md` this month too. Anything you look up twice, write down there. After a few weeks a cold session knows what you know.

`verify` still gets skipped — say so in the PR body, with the reason. Never silently.

---

## Month 2 — the whole loop

The stack works now.

```bash
/harness-eng spec      <ticket-id>
/harness-eng impl      <ticket-id>
/harness-eng verify    <ticket-id>
/harness-eng pr-create <ticket-id>
/harness-eng pr-review <ticket-id> <pr-url>
/harness-eng kb-update <ticket-id>
```

Six sessions. One stage each.

`kb-update` starts paying here: it writes to the target repo's `docs/`, so the team gets what you learned, not just you.

---

## Month 3 — the harness starts improving itself

**Learnings graduate.** Strip every proper noun from something you learned. Still useful → it is a method improvement, and belongs in the kernel skill. Nothing left → it is a repo fact, and belongs in that repo's `CLAUDE.md`.

**A private company skill set begins**, in a separate repo, authored with `/writing-skills`. Prefix those names so they cannot collide with the public set.

---

## Four rules

1. **One stage, one session.** The design rests on this. A session that wrote the code cannot be trusted to test it.
2. **The same `--human` on three tickets running** was never per-ticket context. Move it to `CLAUDE.md`.
3. **Never give `~/progress` a public remote.** Real ticket IDs, real service names, real defect writeups.
4. **A red test is not automatically a code bug.** The control case decides. A broken environment gets zero retries — go fix the machine.

---

## Don't fake `verify`

The single discipline that matters most, and the one an agent erodes fastest.

It fails in two ways that look identical from outside:

- **A pass that never ran.** "All six cases pass" when the stack was never up.
- **A pass that ran against nothing real.** A mock so complete it always agrees; a stub standing in for the service. It genuinely executes and genuinely goes green, and proves nothing.

The second is worse, because it is not a lie. Everyone believes it, including whoever wrote it.

A small worked example. The criterion:

```
AC-1  Given the token has expired
      When the client calls refresh
      Then a new token is returned
```

The fake pass:

```python
def test_refresh():
    mock_server.respond({"token": "new-token"})   # tell the mock what to say
    result = client.refresh()
    assert result.token == "new-token"            # green
```

That test asserts the mock returned what it was just told to return. The real service was never reached, no token ever expired, and the refresh path was never executed. It passes on a laptop with the network off, and it passes even if `refresh` is deleted and replaced with a hardcoded string.

The honest version drives a genuinely expired token against the running service and asserts on what comes back — or, where that cannot be run yet, reports *skipped, no stack* and says so in the PR body.

**An agent is heavily rewarded for producing green.** Told to verify, it will find *a* way to make something pass — spin up a mock, stub the dependency, relax the assertion — and it never feels the thing that stops a person from writing "tested ✓" on something they did not test. So the guard cannot be *be honest*; it has to be structural.

**The honest outcome is not "skip it" — it is saying which of these happened.** Three are all fine:

| Outcome | What goes in writing |
|---|---|
| Verified | the trace — command, output, the acceptance criterion each maps to |
| Skipped | the reason, in the PR body (§5.3) |
| Could not check | "Pre-flight unavailable: no test command documented. The triage below is unverified." (§9 Q12) |

There is a fourth, and it is the only bad one: **green with nothing behind it.**

**It is worse than no test.** A PR saying *no tests, here is why* gets read carefully. A PR saying *tested ✓* gets waved through. A faked pass spends your reviewer's attention and buys nothing with it — and then it ships.

Three things in the design stop it, none relying on good intentions:

- **The control case** (§5.5) — run a test that predates your change. Green means the environment is real. Red means you are measuring a broken machine, and every conclusion below it is worthless.
- **`<ticket-id>-verify-trace.md`** (§9 Q15) — a claim with a record behind it can be checked; a claim without it can only be believed.
- **Zero retries on a broken environment** (§5.6) — escalate immediately, never retry. Retrying is precisely how *let me just mock it* gets invented.

---

## The one thing worth remembering

After a week away:

```bash
cat ~/progress/*/<ticket-id>-progress.md
```

One or two lines per stage. The whole ticket, recovered in five seconds.

---

## Where to look next

| File | What it holds |
|---|---|
| `SPEC.md` | the full design, and why each decision beat its alternatives |
| `SPEC.md` §9 | every question that was closed, and the reasoning — read before re-opening one |
| `../writing-skills/SKILL.md` | the standard this skill was written to |
| `NOTICE.md` | attribution — `mattpocock/skills` and `dietrichgebert/ponytail`, both MIT |
