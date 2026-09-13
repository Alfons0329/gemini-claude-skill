# Self-check results — 2026-08-28

Run against `example/self-check.md` after the build session wrote `SKILL.md` and the six `reference/*.md` files (commits `157b6b3`, `f3f4463`, `ee62146`).

> **Superseded in part.** The adversarial-verify change (`SPEC.md` §9 Q18, Q19) landed after this run. Every `file:line` citation below predates it and no longer resolves, and Checks A, D and G need re-running against the current files. The reasoning stands; the line numbers do not.

Checks A–E ran here. **Check F is deliberately not run in this session** — it requires a session that has not read these files, for the reason the check itself gives.

Paths below are relative to `productivity/loop-eng/`.

---

## Check A — the handoff chain

| Stage | Input named | Output named | Missing-input behaviour |
|---|---|---|---|
| `spec` | `SKILL.md:15`, `reference/spec-create.md:3,7` | `SKILL.md:15`, `reference/spec-create.md:12` | `reference/spec-create.md:3`, `SKILL.md:82-84` |
| `rca` | `SKILL.md:16`, `reference/ticket-rca.md:7` | `SKILL.md:16`, `reference/ticket-rca.md:16` | `SKILL.md:78-80`; no-op path `reference/ticket-rca.md:3` |
| `impl` | `SKILL.md:17`, `reference/ticket-impl.md:3` | `SKILL.md:17`, `reference/ticket-impl.md:45-50` | `SKILL.md:78-80` |
| `verify` | `SKILL.md:18`, `reference/ticket-verify.md:5` | `SKILL.md:18`, `reference/ticket-verify.md:32,53` | `SKILL.md:78-80` |
| `pr-create` | `SKILL.md:19`, `reference/pr-lifecycle.md:7` | `SKILL.md:19`, `reference/pr-lifecycle.md:9` | `SKILL.md:78-80` |
| `pr-review` | `SKILL.md:20,37`, `reference/pr-lifecycle.md:41` | `SKILL.md:20`, `reference/pr-lifecycle.md:56` | `SKILL.md:78-80` |
| `kb-update` | `SKILL.md:21`, `reference/kb-update.md:3` | `SKILL.md:21`, `reference/kb-update.md:11-24` | `SKILL.md:78-80` |

Every stage's stated input is an earlier stage's stated output, or is named as operator-produced (`<id>-ticket.md`, `reference/spec-create.md:7`; the PR URL, `SKILL.md:37`). No name drift: `impl` writes `<id>-qa.md` / `<id>-qa-e2e.md` and `verify` reads those exact names.

**One break found and fixed.** `SKILL.md`'s records table said records are *never* loaded as pipeline input, while `reference/ticket-impl.md:67` has `fix-sec` read `<id>-security-review.md` directly. A cold session reading only `SKILL.md` would have refused the one read the repair mode depends on. `SKILL.md:70` now carries the exception explicitly.

## Check B — the cycle closes

1. `kb-update` writes to the target repo's `docs/` — `reference/kb-update.md:5,11-24`.
2. `spec` (and every other stage) reads the project context file — `reference/spec-create.md:8`, `SKILL.md:86-90`.
3. They meet at `reference/kb-update.md:36` and step 4 at `:49`: a `docs/` entry a future stage would need is accompanied by a one-line `CLAUDE.md` pointer, because no stage browses `docs/` on its own.

Passes. This is the check that was most at risk — a `docs/` write with no pointer back would have made the pipeline a diary rather than a loop. Commit `f3f4463` had already broadened this rule from `spec`-only to every stage.

## Check C — cold start, every fallback fires

- [x] `spec` with no tracker — ticket text comes from `<id>-ticket.md` (`reference/spec-create.md:7`); absent, it fails fast naming path and producer (`SKILL.md:82-84`).
- [x] All seven stages name a documents-nothing fallback: `spec` `reference/spec-create.md:8` · `rca` `reference/ticket-rca.md:13` · `impl` `reference/ticket-impl.md:41` · `verify` `reference/ticket-verify.md:22-24` · `pr-create` `reference/pr-lifecycle.md:27` · `pr-review` `reference/pr-lifecycle.md:52,62` · `kb-update` `reference/kb-update.md:26`. Rule set once at `SKILL.md:90`.
- [x] No test command — emits the *pre-flight unavailable* line, `reference/ticket-verify.md:22-24`.
- [x] No pre-existing control case — falls back to the repo's own suite (`reference/ticket-verify.md:20`); when that is missing too, the unavailable announcement above.
- [x] No E2E tooling — writes the manual checklist, names the exact re-invocation command, and exits, `reference/ticket-verify.md:42-49`.

Every fallback announces. None is silent.

One hard stop, deliberate rather than a fallback: no progress root documented in the user-level context file → stop and name the missing line (`SKILL.md:41`). It announces, so it does not fail this check.

## Check D — every failure path lands

| Failure | Landing | Citation |
|---|---|---|
| `verify` red, environment | zero retries, escalate immediately | `reference/ticket-verify.md:16,63`; `SKILL.md:133-138` |
| `verify` red, code bug | `impl <id> fix-qa`, at most 2 attempts | `reference/ticket-verify.md:64`; `reference/ticket-impl.md:58,63`; `SKILL.md:136` |
| still red after the budget | stop; repro, both attempts, ranked hypotheses | `SKILL.md:140`; `reference/ticket-impl.md:63` |
| security finding in `pr-review` | blocks, writes `-security-review.md`, repairs via `fix-sec` | `reference/pr-lifecycle.md:56`; `reference/ticket-impl.md:67` |
| input artifact missing or malformed | fail fast — artifact, path searched, producing command | `SKILL.md:78-84` |
| ticket directory not found / found twice | create-and-say / stop-and-list | `SKILL.md:48-49` |

Four further paths also land: wrong assertion (`reference/ticket-verify.md:65`), wrong test step (`:66`), the RCA stop-and-report gate when the spec's root-cause claim fails (`reference/ticket-rca.md:15`), and no documented progress root (`SKILL.md:41`).

No two rows share a landing with different budgets. `fix-sec` having no numeric cap is stated as a decision, not an omission — `reference/ticket-impl.md:67`.

## Check E — nothing is restated

```
grep -rn 'one stage per invocation\|never chain\|Human input\|append.*dated' reference/
```

No hits. Shared rules live only in `SKILL.md` — one stage per session `:55-59`, the artifact contract `:61-84`, `--human` handling `:92-109`, wait-vs-exit `:111-127`, escalation `:129-142`. Reference files cite them by section name and never restate them (e.g. `reference/ticket-verify.md:100` explicitly defers both retry budgets to `SKILL.md`).

## Check F — `SKILL.md` stands alone

**Not run.** Requires a session that has not read these files; this one wrote and reviewed them and cannot tell what it meant to write apart from what is on the page. Prompt is in `self-check.md`, "Check F".

---

## Status

A–E pass, with one break found and fixed under A. F outstanding — the build is not done until it runs.
