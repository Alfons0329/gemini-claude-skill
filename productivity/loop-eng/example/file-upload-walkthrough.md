# Walkthrough — one vague feature ticket, end to end

The rules in `SKILL.md` and `reference/` are abstract on purpose. This is one ticket running through all of them, written from the operator's seat.

It is deliberately a **vague feature ticket owned end to end** — the shape where the loop earns the most, because nobody upstream has decided anything and nobody downstream will catch what you get wrong.

Four things go wrong along the way. Those are the interesting parts; the green stretches between them are not.

---

## The ticket

```
PROJ-401: Let user upload file in Client
"Users should be able to upload a file in the client."
```

One sentence. Save it by hand — this step is always the operator's:

```bash
mkdir -p ~/progress/proj-401
$EDITOR ~/progress/proj-401/proj-401-ticket.md
```

---

## Hiccup 1 — `spec` refuses to write a spec

```
/loop-eng spec proj-401
```

The stage asks its routing question — does the ticket name an observable outcome, or only a want? — and answers it the second way:

```
PROJ-401 names a want, not an observable outcome — no format, size limit,
destination, or post-upload state is decided.

Grill it with your own method, save the result to
~/progress/proj-401/proj-401-spec.md with the sections below,
then run /loop-eng impl proj-401.
```

**This is the stage working, not failing.** Arguing a human out of a vague requirement is a conversation, not a procedure, and the method belongs to your team. What the pipeline fixes is the shape of the answer.

**What you do:** open a grilling session — whatever skill or habit you use — outside this skill.

### The grilling session

One question at a time, and the useful ones are the ones you can't answer:

```
Q: Which formats?                    → PDF, PNG, JPG.
Q: What's the size limit?            → ...nobody has told me.        [GAP]
Q: Where does the file go?           → S3, we already have a bucket.
Q: Does the database record it?      → Yes — user, filename, key, timestamp.
Q: Same filename uploaded twice?     → ...that's a product call.     [GAP]
Q: Interrupted mid-upload?           → No resume this round.         → non-goal
```

Two questions you couldn't answer became parked gaps. One became a non-goal. Save the result as `proj-401-spec.md`:

```markdown
## Acceptance criteria
AC-1  Given a PDF, PNG or JPG under the limit
      When the user submits the upload
      Then the API returns 201 with the upload id

AC-2  Given a file of any other type
      When the user submits the upload
      Then the API returns 400 naming the accepted types

AC-3  Given an upload returned 201
      When the object store is queried
      Then the object exists and its bytes match what was sent

AC-4  Given an upload returned 201
      When the database is queried
      Then a record exists with user, filename, key and timestamp

## Non-goals
- Resumable upload. Interrupted means re-upload.
- Virus scanning. Separate ticket.

## Open gaps
[GAP-1] Maximum file size                      Status: awaiting PM
  Scenario:   a user picks a 2GB video
  Not ours:   drives storage cost and how long the client blocks
  Options:    A 10MB (cheap, excludes anything past a photo)
              B 50MB (covers ordinary documents, cost acceptable)
  Recommend:  B

[GAP-2] Same filename uploaded twice           Status: awaiting PM
  Scenario:   a user uploads report.pdf twice
  Not ours:   overwriting loses user data — a product decision, not a technical one
  Options:    A overwrite, keep prior versions (+1 version table, ~1 day)
              B reject and ask them to rename (~0.5 day, worse experience)
  Recommend:  A

## Evidence
AC-3  existing uploadToS3() — src/storage/s3.ts:42
```

Note what each gap carries: the scenario, **why it isn't yours to settle**, the options with costs, and **your recommendation**. A bare "what should the size limit be?" hands the thinking upward along with the decision, and costs the decider days while they invent the options themselves.

---

## Hiccup 2 — `impl` won't start with gaps open

```
/loop-eng impl proj-401
```

```
GAP-1 still open in proj-401-spec.md: "Maximum file size"
GAP-2 still open in proj-401-spec.md: "Same filename uploaded twice"
Close them with the decider, then record the ruling in ## Open gaps and re-run.
```

Not one line of code was written. That is the gate doing its job: building past a parked gap means guessing at somebody else's call and burying the guess in code, where it will read like a decision somebody made.

**What you do:** paste the `## Open gaps` section to the decider. Don't summarise it — the format already exists so they can rule in two minutes.

```
You → PM: "Two calls needed on PROJ-401, options and my recommendation
           for each." <paste>

PM (15 min later): "50MB. And overwrite but keep versions — people
                    should be able to get the old one back."
```

**Record the ruling, then turn it into criteria.** A ruling that stays inside the gap entry binds nothing — no case tests it, no stage reads it:

```markdown
## Open gaps
[GAP-1] Maximum file size          Status: Resolved 2026-09-13 — PM ruled B (50MB)
[GAP-2] Same filename twice        Status: Resolved 2026-09-13 — PM ruled A (overwrite + versions)

## Acceptance criteria
AC-7  Given a file larger than 50MB
      When the user submits the upload
      Then the API returns 413 and no object is written

AC-8  Given a user uploads a filename they have used before
      When the upload succeeds
      Then the new version is current and the prior version is still retrievable
```

Re-run `/loop-eng impl proj-401`. The gate passes.

### What `impl` does

Climbs the ladder and stops at the first rung that holds — `uploadToS3()` already exists for avatars, so the storage path is reuse, not new code. Only the size check, the type check and the version table are written fresh.

It stops once to confirm the seams with you (ten seconds, the only in-session wait in the pipeline), runs red→green, and commits:

- **`proj-401-qa.md`** — 8 cases, one per criterion.
- **`proj-401-qa-e2e.md`** — one line: *"the file picker on the upload page."* No steps, no assertions. That is the scaffold doing its job.

---

## Hiccup 3 — the adversarial pass goes red three ways

```
/loop-eng verify proj-401
```

### Step 0 — the second plan, written blind

Before opening `proj-401-qa.md`, the session writes `proj-401-qa-adv.md` from the spec alone. Sweeping the five buckets:

```
Contract      no file in the request · wrong Content-Type · two files in one request
Boundary      0-byte file · exactly 50MB · 50MB + 1 byte · 255-char filename ·
              unicode filename · a file with no extension
State         two uploads of the same filename, concurrently
Resource      the object store returns 503
Persistence   201 came back — is the row actually in the database?
              does the object actually exist, five seconds later?
```

Then the per-criterion question. On AC-3:

> AC-3 says the stored bytes match what was sent. What assumption, if false, makes this produce a *silently wrong* answer rather than an error?
>
> → that the stream wasn't truncated in transit. A truncated upload still returns 201, and the object still exists — just shorter. Nothing here compares checksums.

**14 cases. `impl` wrote 8.** Every `Expected:` came from the spec's own words, never from running the code and recording the output.

### Steps 1–3 — pre-flight, dev pass, adversarial pass

Pre-flight runs the avatar-upload test, which predates this ticket: **green**, so the machine is sound. Dev pass runs `proj-401-qa.md`: **8 green**.

> Stopping here is where you would open the PR — and you would feel thorough doing it.

Adversarial pass runs the other 14:

```
11 green

RED-1  50MB + 1 byte        → 201, not 413        presses AC-7    → code bug
RED-2  concurrent same name → both written, one version row lost
                                                  presses AC-8    → code bug
RED-3  file with no extension → 500               presses nothing → SPEC GAP
```

Plus the coverage gap: *6 of 14 adversarial cases had no counterpart in the dev plan.*

**What you do — classify before fixing anything.** Three reds, two different routes:

- **RED-1 and RED-2** press criteria that already exist. The code owes the spec something → `fix-qa`.
- **RED-3** presses nothing. Nobody ever decided what a file with no extension should do → **spec gap**, zero retries.

RED-3 is a technical call, not a product one — `Not ours:` can't be filled in honestly, which is the tell that it's yours. Decide it and write it down:

```markdown
AC-9  Given a file with no extension
      When the user submits the upload
      Then the API returns 400, as for a rejected type
```

No second trip to the PM. `## Open gaps` is for what you genuinely can't settle.

### `fix-qa`

```
/loop-eng impl proj-401 fix-qa
```

```
RED-1  hypothesis: the size check reads Content-Length, which the client can lie about
       → count bytes actually written, abort past the limit → green
RED-2  hypothesis: no lock on (user, filename)
       → unique constraint + retry on conflict → green
```

Both held on attempt 1, inside the budget of 2. Throughout, `proj-401-qa.md` and `proj-401-qa-adv.md` were **read-only** — turning `assert 413` into `assert status in (200, 413)` was never on the table.

### `verify`, second run

```
/loop-eng verify proj-401
```

```
proj-401-qa-adv.md header: "Authored against: AC-1..AC-8"
spec now has:              AC-1..AC-9          ← you added AC-9

→ stale → re-authored in full
```

Safe, because this is a fresh session that never saw the last run. The new plan includes a case for AC-9.

Pre-flight green, dev pass green, adversarial pass green. Then the E2E steps, written from the spec — not from the scaffold, not from what the app now does:

```
E2E-4  open the upload page → pick a 60MB PDF → submit
       assert: an error appears, and it states the 50MB limit
```

`curl` proves the API returns 413. Only this proves a human can tell why. **VERIFY PASS.**

---

## Hiccup 4 — the security gate

```
/loop-eng pr-create proj-401
/loop-eng pr-review proj-401 <pr-url>
```

```
Path traversal: filename is concatenated into the object key without
filtering "../" — an attacker can write anywhere in the bucket.
→ proj-401-security-review.md
```

```
/loop-eng impl proj-401 fix-sec     # fix, then back to pr-review
/loop-eng kb-update proj-401
```

`kb-update` writes the durable lesson — *size limits count bytes written, never trust Content-Length* — into the target repo's `docs/`, where every future session reads it automatically.

---

## The four hiccups

| | What stopped you | What you did | Roughly |
|---|---|---|---|
| 1 | `spec` refused a vague ticket | grilled it yourself, saved the spec | 30 min |
| 2 | `impl` refused open gaps | pasted them to the PM; rulings became criteria | 15 min, mostly waiting |
| 3 | adversarial pass, three reds | classified: two to `fix-qa`, one you ruled on yourself | 40 min |
| 4 | security gate | `fix-sec` | 20 min |

## The same ticket without any of it

```
PM:  "Let users upload a file."
You: sure (privately assuming 10MB)
     happy path tested, green, merged, shipped

day 4   "why can't I upload a 30MB deck?"          GAP-1, never asked
day 9   "my report.pdf got overwritten"            GAP-2, never asked
day 15  "concurrent uploads lose a version row"    nobody thought of it
day 31  "someone wrote to our bucket root"         path traversal
```

Four interruptions, against four production incidents — each one arriving when it is most expensive and least yours to schedule.

**Hiccup 2 is the one worth the most.** How large a file a user may upload was never an engineering decision. The gate exists so you find that out before the code exists, rather than after someone files a bug about the number you guessed.

---

## See also

| File | What it holds |
|---|---|
| `solo-feature-owner.md` | the same end-to-end ownership, at feature rather than ticket scale |
| `self-check.md` | the build-completion test — does the loop actually close? |
| `../SPEC.md` §5.1a | why the adversarial pass exists, and what it can't catch |
| `../SPEC.md` §9 Q19 | the two spec routes, the gap gate, and why the `spec` stage stayed |
