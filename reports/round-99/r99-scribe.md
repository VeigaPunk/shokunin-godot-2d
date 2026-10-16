# r99 scribe — custody audit of landing `254e79dd`

Seat `SCRIBE` (g2d lane `r99-scribe`) | host **devin** | lane repo
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` (main @ `2dcbb6f6`, clean
tracked tree) | audit target: **r99 landing `254e79dd`** (author landing, parent
`9d421fb2` = r98) | author artifact: branch `wt-r99` @ `fe1a996e` | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`) | host loadavg
**9.8–16.2 on 32 cores** during the battery run (many sibling lanes were
executing Godot batteries concurrently) | `/tmp` is a 16 G tmpfs that was
**13 G full** and intermittently returned `Disk quota exceeded` (see §3).

**Verdict: CUSTODY BROKEN** on the author-artifact → landing link (§2 F1–F4).
The author's *own* evidence (hashes, receipts, run counts, manifest) is
**INTACT** and reproduces exactly — but the landed bytes are **not** the bytes
that report pins and measures, and the landing carries a defect (a duplicated
CASES row) that no r99 receipt covers. The landed bytes themselves are now
**measured green** by this seat's full battery (492/492, §3), so the round's
semantic outcome holds and the judge has the missing receipt; the break is in
artifact identity, not in the r99 rows. Nothing here re-adjudicates the r99
laws; that is the critic/reviewer/verifier seat's remit.

---

## 0. Method (exact commands, read-only)

| # | command (cwd = lane repo unless noted) | outcome |
|---|---|---|
| 1 | `git log --oneline -15`, `git rev-parse HEAD`, `git status --porcelain` | HEAD `2dcbb6f6`; tracked tree clean; only `?? corpus/live/*` untracked |
| 2 | `git show --name-status 254e79dd` / `fe1a996e` | landing touches 5 paths; branch commit touches 4 (no `.pyc`) |
| 3 | `git diff --numstat 9d421fb2 254e79dd` | run_battery.py **+151/−2** (not insertion-only) |
| 4 | `git diff --numstat 89f85ed8 fe1a996e` | run_battery.py **+150/−0** (author's own base) |
| 5 | `git show <c>:corpus/fixtures/run_battery.py \| sha256sum` for `89f85ed8/f67094bb/9d421fb2/fe1a996e/254e79dd` | see §1 table |
| 6 | `sha256sum` of the frozen probes (`corpus/live/r99-scout/{probes,proj}`, `corpus/live/r99-boundary/{probes,proj,proj2d}`) + both landed fixtures | all copies byte-identical (§2 F6) |
| 7 | `python3` AST: extract `CASES`, hash each tuple's source segment; difflib opcode analysis of r96→author and r98→landing; module-minus-`CASES` AST compare; `classify_process`/`classify_streams` source-segment hashes | r99 tuples byte-identical across branch/landing; **1 duplicate row in the landing** (§2 F2) |
| 8 | `git show 254e79dd:.../*.pyc \| xxd` (16-byte header) | magic `0x0e2b` (CPython 3.14), flags 0 (timestamp), source mtime `0x6ad1ec01` (06:18:57 −0300), **source size 489915 = landed source size** (§2 F4) |
| 9 | `sha256sum -c manifest.sha256` (author receipts, wt-r99) | **90/90 OK** |
| 10 | `python3` summaries of the three receipt `verdicts.json` (wt-r99 `corpus/live/runs/20261016T08{4826713464,5534654592,9022167156}Z`) | 446/447, 445/447, 447/447; r99 21/21 each (§2 F6) |
| 11 | `git archive 254e79dd corpus/fixtures \| tar -x -C /tmp/r99-landing` | fresh archive checkout, 2.3 M, landed hashes confirmed |
| 12 | `python3 corpus/fixtures/run_battery.py --runs /home/vgpnk/r99-scribe-runs/runs` (cwd `/tmp/r99-landing`, detached with `setsid` after attempt 1 died) | **PASS, 492/492, 21/21 r99 rows, 8 m 15 s** (§3) |
| 13 | `sha256sum` of the archive fixtures after the run; `git status --porcelain --untracked-files=no` in the lane repo | hashes unchanged; tracked tree still clean |

No tracked file in the lane repo was written except this report; no commit, no
push, no deploy; no sibling lane's tree touched.

---

## 1. Custody chain (what actually happened, from the repository alone)

```
89f85ed8 (r96 author) ──fe1a996e  wt-r99  "r99 author: audio lattice 21 rows (+150/-0), green 447/447"   06:18:26  Devin
9d421fb2 (r98 author) ──254e79dd  main    "r99 author: headless audio lattice (21 rows, +150/-0), green 447/447"  06:19:07  game-dev-2d-shokunin
```

`fe1a996e` was authored by identity `Devin <devin@cognition.ai>` — the same
identity and the same ~90-second window as the capture commits on the sibling
author branches (`wt-r98` @ 06:17:46, `wt-r100` @ 06:19:07). The author seat's
report (written 06:09, worktree mtime) predates it, so the capture commit is
attributed to the orchestrator's batch capture, **not** to the author. The
landing on `main` is not that commit: it is a **re-application of the r99 delta
onto the r98 tree** (parent `9d421fb2`, not `89f85ed8`).

| artifact | author branch `fe1a996e` | landing `254e79dd` | report §0 claim | status |
|---|---|---|---|---|
| `corpus/fixtures/audio_lattice.gd` (773 lines) | blob `2e06913d` / sha `165571c4…` | same | `165571c4…` | ✅ |
| `corpus/fixtures/r99b_modes.gd` (453 lines) | blob `b4993a06` / sha `b680e6f2…` | same | `b680e6f2…` | ✅ |
| `reports/round-99/r99-author.md` | blob `261823c7` / sha `efa821c6…` | same | (n/a) | ✅ text not amended |
| `corpus/fixtures/run_battery.py` | blob `bcb40060` / sha **`71d38d91…`** | blob `3e20b0eb` / sha **`fd2ed16c…`** | `71d38d91…` | ❌ **mismatch** |
| `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` | absent from commit | present (`M`, 443 425 B) | not listed | ❌ extra tracked change |
| CASES entries | 440 (419 r96 + 21 r99), 0 duplicates | **485** (463 r98 + 21 r99 + **1 duplicate**) | 440 | ❌ |
| battery results | 447 = 440 + 7 meta | 492 = 485 + 7 meta (**measured**, §3) | 447 | ❌ for the landing |

The r99 *content* delta is nevertheless byte-identical between the two trees:
the 21 CASES tuples (18 `r99_audio_*` + 3 `r99b_*`) hash equal as AST source
segments; the two 9-line non-CASES insertions (the `r99_audio_gen`
`expected_errors` entry, 518 B, and the `r99_expected_errors_all_matched` floor
gate, 463 B) are byte-identical; `module − CASES` differs only by comments; and
`classify_process` (segment sha256 **`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`**)
is byte-identical in r98, the author branch and the landing. So the *authored
rows* shipped verbatim — inside a file that is not the authored file.

---

## 2. Findings

### F1 — [custody break] The landed `run_battery.py` is not the artifact the report pins and measures
The report's §0 table pins `71d38d91…` and §3 asserts "the battery digest is
identical to the one the smoke pass and runs A/B/C ran on, so the green run is
on the shipped bytes". The landed blob hashes to `fd2ed16c…` (blob `3e20b0eb`,
489 915 B vs the author's 465 444 B). **No battery run in evidence measured the
landed bytes.** The nearest attempt is `corpus/live/runs/20261016T091958733038Z`
(06:19:58 −0300, 51 s after the landing; its `scratch/` carries
`audio_lattice.gd` + `r99b_modes.gd`), which has **no `verdicts.json`** and no
log — an abandoned run, unattributed (the receipt records no seed or owner). The landing's own `__pycache__` entry proves the landed
file was *imported/compiled* at 06:18:57 (header size field 489 915 = landed
source size), which is not an execution. Evidence: commands 3, 5, 8, 11. This
seat's §3 run now supplies the receipt the landing lacked — it is green
(492/492, r99 21/21) — but that does not make the report's `71d38d91…` claim
true of the landing, and it does not cover the duplicate row.

### F2 — [integrity defect, landing-only] Duplicated CASES row `crash_spontaneous_sigabrt`
The landing's `CASES` list contains the tuple
`("crash_spontaneous_sigabrt", "spontaneous_crash_probe.gd", ["--spontaneous-crash"], -6, …)`
**twice** — once at its r98 position (line 1403, appended to the `r98c_flush`
signature line) and once in the reflowed crash tail (line 1535). CASES = 485
where 484 (= 463 + 21) is expected. No other revision of this file has any
duplicate name (r96 419, author 440, r98 463 — all clean). Mechanism: the
integration reflow kept the r98-position copy *and* re-added the crash tail
after the r99 block.

Consequences (code-read, **confirmed against the run in §3**): the crash probe is
executed **twice per battery run** (two `results` records, `exit=-6`, both
PASS); `results` gains one record (492 instead of 491); `census_rows` (which
iterates `results`) reports `rows_with_expected_errors = 76` instead of 75 and
lists the row twice. The meta probes read
`crash_records = {r["case"]: r for r in results …}`, a name-keyed dict, so the
last record wins and no meta gate changes shape — `census_bare_classifier_consistent`,
`census_covers_all_allowlisted_rows`, `census_allowlisted_reproduces_verdicts`
and every `*_expected_errors_all_matched` gate were all `true` in that run. The
duplicate is therefore **verdict-inert but not free**: it is an unmeasured
change to the shipped instrument that no receipt describes, and it makes the
shipped row count differ from every figure in the report and the commit
subject. Minimal repair (not performed — scribe writes no product code): delete
the retained r98-position copy of the tuple at
`corpus/fixtures/run_battery.py:1403`'s tail (or the reflowed tail copy),
restoring CASES to 484 and the r99 delta to a pure insertion.

### F3 — [claims] "insertion-only `+150/−0`" and "green 447/447" do not describe the landing
`git diff --numstat 9d421fb2 254e79dd -- corpus/fixtures/run_battery.py` = **151
insertions / 2 deletions** (the two deleted lines are the crash-tail rows,
re-added in the reflow; the `# --- r99 block:` header was merged onto the tail
of the preceding `r98c_flush` signature line). The author's own diff
(`89f85ed8 → fe1a996e`) *is* `150/0`, and its receipt
`r99_insertion.diff` (base blob `c004d26b` = the r96 file) is a true
insertion-only diff — the claim is accurate for the author's base and false for
the landing. Likewise the commit subject / report "green 447/447" belongs to
the r96+r99 tree (440 CASES); the landed tree has 485 CASES and its own row
count, measured in §3.

### F4 — [disclosure gap] §4 "Files changed" omits the committed `__pycache__` change
The landing modifies `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`
(443 425 B; first tracked at `ec2cda6a`, r69 — so committing the cache is
pre-existing hygiene debt, not an r99 invention). The author's captured commit
does not contain it; it was produced by an import of the *rebased* file at
06:18:57 and committed with the landing. The report's §4 list is therefore
incomplete **with respect to the landing**, and the artifact is a stale-mtime
build cache that any future import will regenerate.

### F5 — [state drift, not author fault] "nothing committed" is stale at audit time
§4 says "No commit, no push, no deploy" and the header says HEAD `89f85ed8`
"working-tree changes only". At audit time the branch `wt-r99` carries the
orchestrator's capture commit `fe1a996e` (06:18:26), and the landing is a
rebase onto r98 whose effect the report cannot describe. Recorded because the
report is the custody document the judge will read: its *artifact identity*
claims describe a pre-integration tree, and the integration changed the file.

### F6 — [verified] Everything else in the report reproduces
| claim | evidence | status |
|---|---|---|
| fixture byte-copy of the frozen probes | 5 copies of `audio_lattice.gd` (`r99-scout/probes`,`r99-scout/proj`,`r99-boundary/probes`,`r99-boundary/proj`,`r99-boundary/proj2d`) all `165571c4…`; 3 copies of `r99b_modes.gd` all `b680e6f2…`; probes frozen 17:30 / 18:25 (Oct 15), fixtures written 06:18 (Oct 16) | ✅ |
| `run_battery.py` `+150/−0`, insertion-only | `git diff --numstat 89f85ed8 fe1a996e`; `r99_insertion.diff` = 150 insertions / 0 deletions vs base blob `c004d26b` (r96 file) | ✅ (author's base) |
| CASES 419 → 440; results 426 → 447 | AST count; three receipt `verdicts.json` all 447 rows | ✅ (author's base) |
| runs A/B/C = 446/447, 445/447, 447/447 | receipts `20261016T084826713464Z` (FAIL `transition`), `…085534654592Z` (FAIL `negative_transition` + `probe_error_clause_surface`, `dead_entry_count=2`, both `negative_transition`), `…090222167156Z` (all PASS, `dead_entry_count=0`) | ✅ |
| all 21 r99 rows PASS in every run; `r99_expected_errors_all_matched=true`; `gen` `matched_lines=2`, `dead_in_run=false` | the three receipts | ✅ |
| smoke 21/21 PASS, fresh process, `rc=0`; `gen` stderr 462 B, 0 B on the other 20 | `smoke/` 63 files, all `.rc`=0, 21 `PASS`; exactly one non-empty `.err` (`r99_audio_gen`, 462 B, the two `clear_buffer` `ERROR:` lines) | ✅ |
| receipt survival 267/267 battery, 204/210 paced, 113/222 unpaced (= 699) | `receipt_survival.json` sums exactly to the quoted totals; segment sha `749fa060…` matches the shipped `classify_process` | ✅ |
| `invalid_idx=-1` disclosure | scout `runs/smoke-bus.out` (pre-freeze, 17:12) reads `invalid_idx=0`; all other scout/boundary receipts read `-1` | ✅ |
| `transition` "12 PASS/1 FAIL over the r95 census of 48 runs" | `reports/round-95/r95-critic.md:329` (`transition` 12/1 over 48 `verdicts.json`) | ✅ |
| receipt manifest | `sha256sum -c manifest.sha256` → 90/90 OK | ✅ |
| r99b pins and the two folded keys as described | shipped signatures match §2 (`r99b_startphase` `imm_uniq=1`, `r99b_mixfree` `all_jumps_q=true period_is_block=true`, `r99b_finfree_played` `played_gt_02=true`); `r99_audio_mixblock` ends at `all_jumps_q=true`, `r99_audio_finish` ends at `finished_seen=true`, `r99_audio_pause` pins prefix only, `loop_degenerate` pinned through `wraps=0` | ✅ |

### F7 — [unverifiable] Labrat "5/5 CONFIRMED"
The report discloses the labrat dispatch and its substrate limits, but no
receipt artifact for it exists under `corpus/live/r99-author/` (or anywhere in
the worktree). Treated as an unverified advisory claim, exactly as the report
itself scopes it.

---

## 3. Full battery on the landed bytes (`254e79dd`)

Tree: fresh `git archive 254e79dd corpus/fixtures` checkout at `/tmp/r99-landing`
(fixture hashes re-confirmed pre-run: `fd2ed16c…`, `165571c4…`, `b680e6f2…`).

- **Attempt 1** (`--runs` default under `/tmp`): aborted at row ~240
  (`nav_lattice_agent`) with `Disk quota exceeded` on the log/scratch writes —
  the 16 G `/tmp` tmpfs was 13 G full (host caveat, not a battery fault). No
  `verdicts.json`; nothing measured.
- **Attempt 2** (detached, `--runs /home/vgpnk/r99-scribe-runs/runs`): **result
  below.**

**Result — green, 492/492, on the landed bytes** (receipt:
`/home/vgpnk/r99-scribe-runs/runs/20261016T093458985123Z/verdicts.json`,
log `/home/vgpnk/r99-scribe-runs/battery2.log`, wall 8 m 15 s, `loadavg`
9.8–16.2, `seed = /tmp/r99-landing/corpus/fixtures`, `godot = godot`):

| measurement | value |
|---|---|
| payload verdict | **PASS** |
| result rows | **492 = 485 CASES (incl. the F2 duplicate) + 7 meta probes** — *not* the report's 447 |
| row verdicts | **492 PASS / 0 FAIL** (no flake row fired in this run) |
| the 21 r99 rows | **21/21 PASS** (`r99_audio_*` 18/18, `r99b_*` 3/3) |
| r99 gate | `r99_expected_errors_all_matched = true`; `r99_audio_gen` entry `ERROR: Condition "active" is true.` matched **2 lines**, `dead_in_run=false` (the row's merged output carries both `clear_buffer` `ERROR:` lines, 12 output lines total) |
| census gate | `census_bare_classifier_consistent = true`, `census_covers_all_allowlisted_rows = true`, `census_allowlisted_reproduces_verdicts = true`, all r87–r99 `*_expected_errors_all_matched = true`, `prior_meta_rows_stable_29_discriminations = true` |
| census size | `rows_with_expected_errors = 76` — one above the 75 the pre-duplicate CASES shape implies; the duplicated crash row is listed twice in the census (both records `PASS`, `exit=-6`, allowlist entry live) |
| duplicate, measured | `crash_spontaneous_sigabrt` × 2 in `results` (both PASS) — F2's prediction confirmed: the probe really does execute twice; the meta gates are unaffected because `crash_records` is name-keyed |
| post-run fixture hashes | `fd2ed16c…` / `165571c4…` / `b680e6f2…` unchanged; lane repo tracked tree still clean |

Reading: the **r99 rows themselves are sound on the landed bytes** — an
independent full-battery run is green, so the round's semantic outcome holds.
What is *not* sound is the custody link: the landed file carries one
unmeasured duplicate row (F2), its bytes are not the bytes the report pinned
(F1), and the "447/447" figure in the commit subject describes a tree that was
never landed (F3).

---

## 4. Touched surfaces

- **Written:** `reports/round-99/r99-scribe.md` (this file, untracked; not
  committed, per contract).
- **Read-only outside the repo:** `/tmp/r99-landing` (archive checkout),
  `/home/vgpnk/r99-scribe-runs/` (my battery receipts/log), the lane's
  `corpus/live/**` and the `wt-r99` worktree receipts.
- **Not touched:** no product code, no tracked file other than this report, no
  `project.godot`, no sibling lane's tree, no commit/push/deploy, no other
  runtime.

## 5. Out of scope

- Semantic re-adjudication of the r99 laws / the two folded keys / the boundary
  falsifications (critic, reviewer, verifier seats).
- r97, r98, r100 and other-lane content; the r100 wave-B frontier.
- The `wt-r99` receipts are untracked evidence in a linked worktree: they are
  readable and were read, but they are not part of any commit and are not on
  the landing. Whether the orchestrator commits them is not my call.

## 6. Artifact paths (evidence)

| path | what |
|---|---|
| `reports/round-99/r99-author.md` (landing + branch, identical) | the audited report |
| `corpus/fixtures/run_battery.py` @ `254e79dd` / @ `fe1a996e` | `fd2ed16c…` vs `71d38d91…` |
| `corpus/fixtures/audio_lattice.gd`, `r99b_modes.gd` @ `254e79dd` | `165571c4…`, `b680e6f2…` |
| `corpus/live/r99-scout/{probes,proj}/audio_lattice.gd`, `corpus/live/r99-boundary/{probes,proj,proj2d}/*` | frozen probe copies (all identical) |
| `wt-r99:corpus/live/r99-author/{battery_runs_ABC.json,fixture_sha256*.txt,manifest.sha256,receipt_survival.json,r99_insertion.diff,smoke/,bus_reps/}` | author receipts (untracked in the linked worktree) |
| `wt-r99:corpus/live/runs/20261016T08{4826713464,5534654592,9022167156}Z/verdicts.json` | author battery runs A/B/C |
| `corpus/live/runs/20261016T091958733038Z/` | abandoned run on a tree carrying the landed fixtures (no `verdicts.json`) |
| `/tmp/r99-landing`, `/home/vgpnk/r99-scribe-runs/` | this seat's archive checkout and battery receipts |
