# Self-check — does the loop actually close?

Run this **after** writing `SKILL.md` and the six `reference/*.md` files, before calling the build done.

Nothing here executes code. It is a paper trace: walk a requirement through every stage and confirm each handoff lands.

**Answer every check with a `file:line` citation, not a summary.** A check answered "yes, that's covered" has not been run — the point is to open the file and find the sentence, because the sentence is often missing.

---

## The test input

`smb-client-server.md` in this directory:

> Create an SMB client → server architecture locally on this machine.

Chosen deliberately. It is a **cold start with nothing in place**:

| What is missing | Which fallback it fires |
|---|---|
| no tracker | ticket text pasted by hand (§9 Q10) |
| no `CLAUDE.md` | every stage's documents-nothing fallback (§7.1) |
| no test command | pre-flight unavailable (§9 Q12) |
| no pre-existing tests | no control case (§5.5, §9 Q12) |
| no E2E tooling | manual checklist, session exits (§9 Q9) |

A loop that survives this one survives a mature repo trivially. The reverse is not true, which is why this is the test case.

---

## Check A — the handoff chain

Fill this in from the files you just wrote. Every cell is a citation.

| Stage | Where its input is named | Where its output is named | Where missing-input behaviour is named |
|---|---|---|---|
| `spec` | | | |
| `rca` | | | |
| `impl` | | | |
| `verify` | | | |
| `pr-create` | | | |
| `pr-review` | | | |
| `kb-update` | | | |

**Fails if** any cell is empty, or any stage's stated input is not some earlier stage's stated output.

The classic break: `verify` says it reads "the QA plan" while `impl` says it writes `<id>-qa.md`. Two names, one file, and a cold session that finds neither.

---

## Check B — the cycle closes

The loop is only a loop if the last stage feeds the first one of the **next** ticket.

1. Where does `kb-update` write? (expect the target repo's `docs/`, and proposed `CLAUDE.md` content — §9 Q5)
2. Where does `spec` read repo conventions from? (expect `CLAUDE.md` — §7.1)
3. Do those two meet?

**Fails if** `kb-update` writes somewhere no later stage ever reads. That is not a cycle, it is a diary — ticket 8 learns nothing from ticket 1, and the main compounding benefit of the whole design is gone.

---

## Check C — cold start, every fallback fires

Trace the SMB requirement with **no `CLAUDE.md` anywhere**. For each, cite where the behaviour is written:

- [ ] `spec` runs with no tracker — where does it say the ticket text comes from `<id>-ticket.md`, and what does it say when that file is absent?
- [ ] Each stage names what it does when `CLAUDE.md` documents nothing. **Every stage. Check all seven.**
- [ ] `verify` finds no test command. Does it emit the *pre-flight unavailable* line, or does it quietly continue?
- [ ] `verify` finds no pre-existing test to use as a control case. Which fallback runs, and what does it say when that is missing too?
- [ ] `verify` finds no E2E tooling. Does it write the manual checklist, name the exact re-invocation command, and exit?

**Fails if** any fallback is silent. A silent fallback produces output that looks identical to a verified run. That is the failure this whole design exists to prevent — see `../README.md`, "Don't fake verify".

---

## Check D — every failure path lands somewhere

No dead ends. Cite where each is handled:

| Failure | Expected landing |
|---|---|
| `verify` red, environment implicated | escalate immediately, **zero** retries (§5.6) |
| `verify` red, code bug | `impl <id> fix-qa`, at most 2 attempts (§5.6) |
| still red after the budget | stop, hand the human the repro, both attempts, and the ranked hypotheses |
| security finding in `pr-review` | blocks, writes `<id>-security-review.md`, repairs via `impl <id> fix-sec` (§6.1) |
| an input artifact is missing or malformed | fail fast naming the artifact, the path searched, and the command that produces it (§9 Q8) |
| ticket directory not found, or found twice | create-and-say, or stop and list the matches (§9 Q13) |

**Fails if** any row has no home, or if two rows land in the same place with different retry budgets.

---

## Check E — nothing is restated

`SKILL.md` owns every shared rule. The reference files point at them.

```bash
cd <repo-root>
grep -rn 'one stage per invocation\|never chain\|Human input\|append.*dated' \
  productivity/loop-eng/reference/
```

**Fails if** a reference file re-explains a rule rather than naming it. Seven copies of one rule means changing it is a seven-file edit, and the sixth gets missed silently.

---

## Check F — `SKILL.md` stands alone

The one check worth a **fresh session**, because this session cannot perform it: it remembers what it meant to write, and cannot tell that apart from what it actually wrote.

Open a new session and give it exactly this:

> Read only `productivity/loop-eng/SKILL.md`. Do not read `SPEC.md` or anything under `reference/`. Then tell me: to run `/loop-eng verify <ticket-id>`, what would you have to guess?

**Fails if** the answer names anything a cold operator would also have to guess. Every gap it lists is a gap a real Monday-morning session hits.

---

## Passing

All six checks, every citation filled, `SPEC.md` §8's eight items written.

Then the build is done — not before.
