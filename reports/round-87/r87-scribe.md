# r87 scribe — round record-integrity audit

Seat `SCRIBE` (g2d lane r87) | host **devin** | read-only audit; the only write is
this file. Audit window **2026-10-15T14:09–14:30-0300** (UTC 17:09–17:30).
Work commit under audit `ebcf2bb` (14:26:47). **HEAD moved mid-audit to
`1ecca1b`** (14:28:38, SCORECARD backfill) — both states recorded below.

No fixture, harness, runner, report-of-record, LOG, or SCORECARD write; no
commit, no push, no re-run of any battery. Every number below is from an
existing artifact on disk or a read-only command over it.

---

## 0. Custody totals — `sha256sum -c` per seat dir

| seat dir | manifest | verify pass/total | notes |
|---|---|---|---|
| `corpus/live/r87-scout/` | `MANIFEST.sha256` (101 lines) | **101/101 OK, 0 FAIL** | incl. all 20 `runs/` receipts (jpbe/ei_bound/jmode/ei_test ×3 reps + ei_test rep1) |
| `corpus/live/r87-boundary/` | `MANIFEST.sha256` (1283 lines) | **1283/1283 OK, 0 FAIL** | `proj/`, `runs/` (r3), `runs-v1/` (r12), 10 censuses, `ref-pins.json`, `run_boundary.py` |
| `corpus/live/r87-author/` | **none** | n/a (0/0) | 3 battery reps (`battery-rep{1,2,3}.stdout`, 0 B stderr) + `runs{1,2,3}/<stamp>/verdicts.json` + `save-process-verdicts.json` |
| `corpus/live/r87-baseline/` | **none** | n/a (0/0) | 2 reps + frozen `tree/` + `compare.py`/`tuples.py`/`rowtable.py` + `env.txt`, `rep-timing.txt`, `freeze-head.txt` |
| `corpus/live/r87-boundary-readonly/` | **no dir** | n/a | report-only seat (capability-blocked labrat; orchestrator wrote the report from its payload; source = scout receipts) |
| `corpus/live/r87-critic/` | empty dir (14:29:32) | n/a | concurrent seat, in flight |
| `corpus/live/r87-reviewer/` | no manifest | n/a | concurrent seat, in flight: `canon.stdout` 7803 B, `canon.stderr` 0 B, `rb.diff` 28533 B, `runs-canon/` |
| `r87-verifier` / `r87-simplifier` / `r87-scribe` | absent | n/a | not yet landed at window close |

**Manifest-covered total: 1384/1384 files verify, 0 mismatches, 0 missing.**

Commands (verbatim):

```
(cd corpus/live/r87-scout    && sha256sum -c MANIFEST.sha256)   # 101/101 OK
(cd corpus/live/r87-boundary && sha256sum -c MANIFEST.sha256)   # 1283/1283 OK
```

## 1. Seat coverage in `reports/round-87/`

Present at 14:30:07 (mtime): `r87-scout.md` 13:05:30, `r87-boundary-readonly.md`
14:07:38, `r87-baseline.md` 14:08:02, `r87-boundary.md` 14:15:47,
`r87-author.md` 14:25:17. All five seats named in the dispatch are on disk.
Absent as reports (landing concurrently): `r87-critic.md`, `r87-reviewer.md`,
`r87-simplifier.md`, `r87-verifier.md` (+ this scribe, + no fold/adjudicator
report).

`LOG.md` (mtime 13:07:31) carries **no round-87 section** — last entry is round
86. So no LOG-referenced r87 artifact can be dangling (vacuous); the r87 LOG
entry is simply not yet written.

**Dangling-reference sweep** (F2 custody pattern): every backticked
`corpus/…`/`reports/…` path cited by the five round-87 reports resolves —
41 distinct refs, **0 missing**. Repo-wide, the only out-of-round refs are
`reports/round-89/r89-scout.md` → `reports/round-87/r87-boundary-readonly.md`
(present) and a probe-hash table row (not a path).

## 2. Author report claims vs committed diff

`git show ebcf2bb --stat`:

```
corpus/fixtures/ei_bound.gd      |  14 +
corpus/fixtures/input_lattice.gd | 854 +++++
corpus/fixtures/r87_edge.gd      | 195 ++
corpus/fixtures/run_battery.py   |  80 +++-
4 files changed, 1140 insertions(+), 3 deletions(-)
```

| author claim | check | result |
|---|---|---|
| `input_lattice.gd` `2b68531d…` / 854 lines | `sha256sum` tree **and** `git show ebcf2bb:…` | **match** (identical blob; 854) |
| `r87_edge.gd` `7cd80727…` / 195 lines | same | **match** (195) |
| `ei_bound.gd` `0493a257…` / 14 lines | same | **match** (14) |
| CASES 175 → 200 (+25) | parsed `CASES` literal from `git show 00a1416:…` vs work blob | **match**: 175 → **200** |
| 207 rows / battery | `runs2`,`runs3` `verdicts.json` | **match**: 207 rows, 207 PASS, top `PASS`; `runs1` 205 PASS/2 FAIL |
| pre-fix rep1 FAIL×2 = `pre_frame`, `r87_edge_jpbe` | `runs1` verdict records | **match** (exactly those two) |
| `expected_errors` += 3 | verdict records | **match**: `null_edge` 4 entries, `r87_edge_jpbe` 1, `ei_bound_refusal` 1 |
| "20 verbatim rows + 4 mode-envelope rows + 2 edge rows" | row census | **off-by-one (F2)** |

Row census ground truth (25 new CASES rows = 23 `input_lattice_*` + 2 edge):
scout `author-rows.py.txt` contains exactly **20** `('input_lattice_…` rows;
`press_phys`/`release_edge`/`ui_ns` appear **only in its header comment** as
"OMITTED AS UNPINNABLE-AS-WRITTEN (bimodal)", and `pre_frame` **is inside** the
20. So the four-payload envelope set (`press_phys`, `release_edge`, `ui_ns`,
`pre_frame`) double-counts `pre_frame`: 20 + 4 + 2 = 26 ≠ the committed 25.
Correct decomposition: 20 scout rows (`pre_frame` re-cut) + 3 newly-armed
envelopes + 2 edge = **25**. The same off-by-one is in commit message `ebcf2bb`.

**Corroborations of the author's headline numbers** (independent re-derivation,
no re-run):

- prior-row identity vs baseline: `common=182, new_only=25, old_only=0` — exact;
  signature-level mismatches across the common 182 = **0**.
- the single meta tuple diff is exactly the census: baseline
  `rows_with_expected_errors=49` → author `52`, **added** `ei_bound_refusal`,
  `input_lattice_null_edge`, `r87_edge_jpbe`, **removed** none,
  `dead_entry_count=0` on both sides. Author's explanation confirmed.
- `pre_frame` per-rep emission: `runs1` `post_ph=[]` (FAIL vs the string pin),
  `runs2` `post_ph=[ph+0{pf0=1/1.00/1/0}]`, `runs3` `post_ph=[]` — the report's
  rep-count table is exactly right. (The stdout case line prints the *expected*
  evidence tuple, not the observation, so stdout lines are identical across
  reps by construction — the observation lives in `record["output"]`.)

## 3. `expected_errors` whitelist ↔ producing arm

Every r87 allowlist entry has a live producing arm **today**: census entries
`input_lattice_null_edge` (4 entries × 1 matched line), `r87_edge_jpbe`
(1 × 1), `ei_bound_refusal` (1 entry × **4** matched lines, the `ei=32/33/…`
refusal repeats), all `dead_in_run=false`, `dead_entry_count=0` in all three
reps. **But the floor gate does not cover them** — see F3.

## 4. Timestamps / ordering

```
12:52–13:05  scout corpus (runs/ 12:52, ei_test 13:05, MANIFEST 13:05)
13:05:30     reports/round-87/r87-scout.md
13:07:31     LOG.md last touched (round-86 entry; no r87 section)
13:53:54 fad0b1e  forward scout reports r82/r84/r87/r88
14:07:09     baseline rep2 end (17:07:09Z)
14:07:35–38  r87-baseline corpus / r87-boundary-readonly.md  → 96c0b13 14:07:38
14:10:11 7fd640f  r89 scout (+ r87 baseline report, r87 exact_match/device-bank)
14:14:51–16:12  r87-boundary corpus → 00a1416 14:16:12
14:20:55     r87-author corpus complete; battery rep3 14:23
14:25:17     reports/round-87/r87-author.md
14:26:47 ebcf2bb  r87 work commit (4 files)
14:27:53     SCORECARD.md rewritten in worktree (observed by this seat)
14:28:38 1ecca1b  SCORECARD backfill committed (50 insertions)
14:29:25/32  r87-reviewer / r87-critic corpus dirs appear (concurrent)
14:30:07     audit close — tracked drift EMPTY
```

Consistent with a lane where forward scouts land early; two record notes:
`7fd640f` (r89-named) carries the **r87** baseline report, and the baseline
seat's own disclosure (orchestrator committed `96c0b13` after rep2) matches the
clock exactly (rep2 end 14:07:09, commit 14:07:38). Baseline provenance is
hash-anchored: `rep-timing.txt` harness sha `b3ef9a2f…` **equals**
`git show 00a1416:corpus/fixtures/run_battery.py | sha256sum`, and both
baseline receipts hold 182 rows with **0** r87 rows — a true pre-change replay.

## 5. Uncommitted tracked-file drift

At **14:27:5x**: `git status --porcelain` = ` M SCORECARD.md`, diff
`index 0cd04bf..cadb3df` (+50, r79/r80/r81/r85/r86 verdict blocks). At
**14:28:38** the identical blob pair landed as commit `1ecca1b` ("SCORECARD
backfill … 82-84 skipped"), so that drift was the orchestrator's **in-flight
backfill, not foreign-fleet residue**, and it is resolved. At **14:30:07**
tracked drift is **empty**. All remaining `??` entries are untracked scratch
(`corpus/live/*` prior rounds + this round, `reports/round-87/r87-author.md`,
one `corpus/fixtures/__pycache__/*.pyc`) — no tracked modification outside the
concurrent seats' committed work.

---

## Findings

- **F1 (custody, non-blocking).** `reports/round-87/r87-author.md` is
  **untracked** while its four sibling reports are tracked, and
  `corpus/live/r87-author/` + `corpus/live/r87-baseline/` carry **no
  `MANIFEST.sha256`** (unlike scout/boundary). The seat whose bytes are the
  committed diff has both its report and its receipts outside any hash-anchored
  or tracked custody. Evidence-loss risk on worktree cleanup; the committed
  fixture blobs are the only hash anchor for the author lane.
- **F2 (record, non-blocking).** Author §"run_battery.py changes" item 1 states
  26 insertions (20 verbatim + 4 envelope + 2 edge) against a committed **25**;
  the 4-payload envelope set double-counts `pre_frame`, which is one of the 20
  scout rows. Propagated verbatim into commit message `ebcf2bb`.
- **F3 (gate scope, non-blocking; class recurrence).** The r79-C2/r80-C1
  dead-entry floor gate `phys2d_expected_errors_all_matched` filters
  `r["case"].startswith("phys2d_")`. The three new r87 allowlists live on
  `input_lattice_null_edge` / `r87_edge_jpbe` / `ei_bound_refusal` — **outside
  the gate**. Dead entries are carried as *data* (`dead_entry_count`,
  `dead_entries`) and are explicitly "not a failure". Live state today is clean
  (0 dead, all entries matched), so nothing is currently unverified; the hazard
  is that a future dead r87 entry would pass silently, exactly the class the
  r80 fold closed for `phys2d_*`.
- **F4 (wording nit).** Author rep-count table says `ei_bound_refusal` carries
  "4 whitelisted ERROR lines" while its own §3 (correctly) says 1 line; census
  shows 1 entry matching 4 emitted lines. Internally reconcilable, ambiguous as
  written (`null_edge` is the 4-entry case).
- **F5 (citation).** Author §"Full battery — before/after" labels the baseline
  row 182/PASS but cites
  `python3 -B corpus/fixtures/run_battery.py --runs corpus/live/r87-author/runsN`;
  those receipts are the 207-row author runs. The 182 figure is independently
  supported by `corpus/live/r87-baseline/runs{1,2}` (182/182 PASS). Claim true,
  citation mislabeled.
- **F6 (custody nit).** The author's `compare.py` outputs
  (`common=182/new_only=25/old_only=0`, `tuple_mismatches=1 (meta)`,
  `output-normalized identical=173/differing=2`, `rep3 vs rep2 mismatches=0`)
  have **no receipt file** on disk. Independent coarse re-derivation corroborates
  the row-set arithmetic, the 0 signature-level mismatches, the 49→52 census
  delta, and the named `export_readiness`/`export_preset_missing` diff (my
  un-normalized sweep is a superset because `compare.py` strips pids/paths/
  elapsed tokens) — reproducible, but not custodied.
- **F7 (provenance staleness).** `r87-author.md` header says HEAD `fad0b1e`,
  "nothing committed", and closes with "No commit made; worktree carries
  `M run_battery.py`, `?? input_lattice.gd` …". True at 14:25:17, superseded at
  14:26:47 by `ebcf2bb` (exactly those 4 files, blob hashes equal to the report's
  claims). No evidence loss; the report must not be read as an
  uncommitted-tree statement.
- **F8 (drift, resolved).** Observed ` M SCORECARD.md` at 14:27:5x, committed as
  `1ecca1b` at 14:28:38; HEAD moved `ebcf2bb` → `1ecca1b` during the audit. Not
  foreign-fleet residue this round (contrast r79–r86 closes).
- **F9 (F2-pattern closure).** The read-only seat's F2 ("scout `runs/` does not
  exist") is **falsified**: `runs/` holds exactly the 20 files the manifest
  lists (mtimes 12:52–13:05) and 101/101 verify, `runs/jmode.rep1.out` readable.
  Ordering note: F2's text is inconsistent with those mtimes (files existed at
  12:52, F2 committed 14:07:38) — it describes a pre-materialization snapshot.
- **F10 (round coverage, time-stamped).** 5/5 named seats reported;
  critic/reviewer/simplifier/verifier reports absent at 14:30:07 with reviewer
  and critic corpus dirs live (14:29:25/14:29:32). No LOG r87 entry yet.

**Adjacent, out of round scope:** `corpus/live/r83-scout/` exists with no
`reports/round-83/` (r83 scout-only); `1ecca1b` explicitly skips 82–84.

## Bounded claims

Everything here is a read-only inspection of artifacts on this host at the
window above; `sha256sum -c` proves byte-identity to each manifest, not that the
manifest is complete. "Pass/total" means lines verified / lines in that
manifest. Fixture claims are anchored to commit `ebcf2bb`; HEAD is `1ecca1b` at
close. Concurrent seats were mid-flight and their receipts may have changed
after 14:30:07. No execution evidence was produced by this seat, and none of the
above upgrades any report-only or contract-only statement into execution
evidence.

Artifacts: this file (`reports/round-87/r87-scribe.md`).
