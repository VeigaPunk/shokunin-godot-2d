# Round 80 baseline report — freeze + frozen tuple set (host: devin)

Seat: g2d baseline (LEAF). Read-only on tracked files: no fixture/runner edit, no
commit, no LOG/SCORECARD write. All artifacts under `corpus/live/r80-baseline/`
(untracked scratch) plus this report.

Battery scope per brief: the **tracked Godot battery**
(`corpus/fixtures/run_battery.py`, **111 rows** = 104 seeded `CASES` + 7 meta).
The r80 author is concurrently landing a new fixture (`phys2d_motion.gd` + 28
`CASES` rows, pre-measured by `reports/round-80/r80-scout.md`); **the frozen
reference is rows 1–111 only** and the author's rows are excluded by
construction (they are not in the frozen bytes).

**STATUS: COMPLETE.** Frozen `d9320dd` at **05:48:10Z** and replayed four times:
twice on the clean live tree as the brief requires (rep1, rep2) and twice from a
`d9320dd` worktree materialized after the author's tracked write (rep3, rep4).
**111/111 PASS in rep1, rep2, rep4**; rep3 is 110/111 with the single FAIL
root-caused to an intermittent SDL gamepad `ERROR:` line, not lattice drift
(§4). The frozen tuple set is
`corpus/live/r80-baseline/freeze/godot-tuples-rep1.txt` (sha256
`ffb7a2c4f8da40c4…`), **row-for-row body-identical to rep2 and rep4**.

**`lsp` disclosure.** No `lsp` device is exposed in this session and no GDScript
language server is installed. This seat made no symbol-aware edit (a read-only
freeze has no rename/reference/definition work): it wrote new scratch files
(`corpus/live/r80-baseline/**`) and this new report. Nothing was hand-renamed.

---

## 0. Timeline — freeze provably predates the r80 arm's tracked write

All times UTC. Receipts first-hand: `freeze-head.txt`, `freeze-digests.txt`,
`rep-timing.txt`, `freeze/worktree-receipt.txt`, run stdout headers.

| time (UTC) | event |
|---|---|
| **05:48:10Z** | freeze capture: HEAD `d9320dd` ×2, `git log -1` = *r79 report-last: adjudicator ADMIT-corr + ledger* (2026-10-15T02:43:44-03:00); `git diff HEAD -- corpus/fixtures/` **empty**; `run_battery.py` sha `48c4a379…`; 63 tracked fixture files |
| 05:48:14Z | `env.txt` (Godot 4.7.2.stable.arch_linux.ed1daf0bf, Python 3.14.7, 32 cpus, load 1.69) |
| **05:48:20.716Z** | **rep1** start (live tree) |
| 05:49:37.173Z | author creates **untracked** `corpus/fixtures/phys2d_motion.gd` (stat mtime) — during rep1, *after* rep1's scratch copy (rep1 scratch has 0 `phys2d_motion` entries) |
| **05:50:26Z** | **rep1** end, rc=0, **126.298 s**, **111/111 PASS** |
| **05:50:27.030Z** | **rep2** start (live tree); scratch copies the now-present `phys2d_motion.gd` |
| 05:51:34.527Z | author's **first tracked write**: `run_battery.py` `48c4a379…` → `66bfe3e2…` (`git diff HEAD --stat`: **+70 lines, insertion-only**) — during rep2 |
| **05:52:30Z** | **rep2** end, rc=0, **123.580 s**, **111/111 PASS** (frozen 111-row bytes, see §1) |
| **05:53:02Z** | frozen worktree materialized at `d9320dd` (`git worktree add --detach`); inside it `run_battery.py` = `48c4a379…`, `phys2d_motion.gd` **ABSENT** |
| **05:53:07.835Z** | **rep3** start (frozen worktree) |
| **05:54:57Z** | **rep3** end, rc=1, 109.502 s, 110/111 — one FAIL (`wrong_key`), SDL gamepad `ERROR:` line (§4) |
| **05:55:07.953Z** | **rep4** start (frozen worktree) |
| **05:56:56Z** | **rep4** end, rc=0, 108.375 s, **111/111 PASS** |
| 05:58:02Z | closing state: live harness `66bfe3e2…`, live `CASES` = **132 rows** (= 104 frozen seeded + 28 r80) → 139 total rows with the 7 meta |

Author-divergence evidence is the stat mtimes above plus `git diff HEAD --stat`
(insertion-only, no deletions) and the frozen worktree's verified content. No
replay can have seen post-freeze bytes: rep1's harness sha is identical
pre/post; rep2's verdicts carry **111 rows and zero `phys2d_motion` cases**
(Python loaded the module at 05:50:27Z, 67 s before the tracked write).

---

## 1. Frozen-tree provenance

- Frozen HEAD: `d9320ddf339a600997de363878d81c698a43b427` — *r79 report-last:
  adjudicator ADMIT-corr + ledger*, committed 2026-10-15T02:43:44-03:00.
  Parent chain `f777925` (r79 work + fold) → `884a4c4` (r78 report-last).
- `corpus/fixtures/run_battery.py` last changed in **`f777925`**; `d9320dd`
  touches no fixture (`git diff --stat f777925 d9320dd -- corpus/fixtures/`
  **empty**). Frozen harness sha256
  `48c4a379c01779158a6ba657057d3bf352854c93dab3a05a83c6e1f78269ebd4`; other
  frozen digests: `phys2d_events.gd` `f952e2f0…`, `causal_chain.gd` `03461872…`,
  `project.godot` `8de8b3af…`.
- **Frozen worktree** (brief-sanctioned freeze after the mid-measurement tracked
  write): `/home/vgpnk/Projects/shokunin/r80-baseline-frozen-worktree`,
  detached at `d9320dd`, `run_battery.py` `48c4a379…` (identical to the live
  pre-landing bytes), `phys2d_motion.gd` absent, 63 tracked fixtures.
  `freeze/worktree-receipt.txt`.
- **rep2 ran the frozen bytes despite the tracked write landing inside its
  window.** Three independent receipts: (a) 111 rows, 104 seeded + 7 meta, the
  exact frozen row list (`freeze/row-names.txt`); (b) zero `phys2d_motion`
  cases in the receipt; (c) the tracked write is 67 s after module load.
  The only observable effect of the author's untracked file is in rep2's
  *scratch* (copied 05:50:27Z, after 05:49:37Z): Godot's editor progress counter
  in the two export rows reads `update_scripts_classes … (30 steps)` vs
  `(29 steps)` in rep1/rep3/rep4. That token is **not** part of any verdict
  tuple; it is the sole non-tuple output delta in §3.
- Pre-move surface: `CASES` 104 rows; 7 meta rows
  (`probe_save_independent_process`, `probe_spontaneous_crash_classification`,
  `probe_descendant_pipe_eof`, `probe_descendant_signature_spoof`,
  `probe_while_live_signature_gate`, `probe_descendant_error_spoof`,
  `probe_error_clause_surface`).

### Exact invocations

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`PYTHONDONTWRITEBYTECODE=1 python3 -B`, absolute `--runs` paths (no `.pyc`
written into `corpus/fixtures/`):

```
python3 -B corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r80-baseline/runs1   # rep1
python3 -B corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r80-baseline/runs2   # rep2
python3 -B <wt>/corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r80-baseline/runs3   # rep3
python3 -B <wt>/corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r80-baseline/runs4   # rep4
```

`<wt>` = `/home/vgpnk/Projects/shokunin/r80-baseline-frozen-worktree`.
Environment (`env.txt`): Linux 7.2.3-arch1-3 x86_64, Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python 3.14.7,
node v24.21.0, `io.DEFAULT_BUFFER_SIZE` 131072, 32 cpus; load 1.69 at freeze,
4.30 at close.

---

## 2. The frozen reference tuples

Per-row Godot **verdict tuple**: `(case, script, flags, expected_exit,
actual_exit, signature, verdict, error, expected_errors)` for the 104 seeded
rows; for the 7 meta rows `(case, verdict, canonical JSON of the row minus
declared-volatile keys)`. Extractor: `tuples.py` (r79's, copied verbatim),
comparator: `compare.py` (r79's, copied verbatim).

| artifact | sha256 |
|---|---|
| **`freeze/godot-tuples-rep1.txt` — THE FROZEN SET** | `ffb7a2c4f8da40c41bd2de9dba4137c235dc05e00f323b5b54661beb20f63174` |
| `freeze/godot-tuples-rep2.txt` | `9a75782ccd6255ebadb713e9f691c4a0725b12ddf0e044cd34a2f3e106d5819f` |
| `freeze/godot-tuples-rep3-flake.txt` | `4f328d2fed79676934d296480003aa7dec980ca98b4b8dfad6e2bd6a3bd775d3` |
| `freeze/godot-tuples-rep4-worktree.txt` | `150a60c593539977ea38565c379c1d8eab9f2c68282235601ebb7305c5be3282` |
| rep1 `verdicts.json` | `29982f8daeeb1199c9e293e7e35725bb4b407f19f31bdb394c80a322891616db` |
| rep2 `verdicts.json` | `30ae28da67b8334c068559f3fa71fd2c478906b0e35eea590e8efc2640751e77` |
| rep3 `verdicts.json` | `c0e26b64722ce16ad50dbc911d0bf405e9e0bd3e1f2cb037a297ece5ac98cb45` |
| rep4 `verdicts.json` | `7ba83e952896861cc2f5ed71edfb056aac2c35569fe6666d7f4ac453c65dce5f` |

All 111 frozen rows verdict **PASS** in rep1, rep2, rep4. The tuple-set *bodies*
(the 111 `case<TAB>verdict<TAB>sha` lines) of rep1, rep2 and rep4 are
**byte-identical**; the file shas differ only in the header line that records
the source `verdicts.json` sha.

---

## 3. Frozen stability and reference comparisons

`compare.py godot` (`godot-compare-rep1.txt`, `godot-compare-rep1-external.txt`,
`godot-compare-rep1-postland.txt`; rep2/rep4 runs in the same receipts).

### 3.1 Internal (frozen bytes, rows 1–111) — ZERO tuple drift

| mine → ref | common | new/old only | tuple mism | output-normalized |
|---|---|---|---|---|
| rep1 → **rep2** | 111 | 0/0 | **0** | 102 identical, 2 differing, 7 not-carried |
| rep1 → **rep4** (frozen worktree) | 111 | 0/0 | **0** | **104 identical, 0 differing**, 7 not-carried |
| rep2 → rep1 | 111 | 0/0 | **0** | — |
| rep4 → rep1 and rep2 | 111 | 0/0 | **0** / **0** | — |
| rep1 → rep3 (flake rep) | 111 | 0/0 | 2 | 103 identical, 1 differing, 7 not-carried |

The 2 rep1↔rep2 output diffs are the export rows' `update_scripts_classes`
step counter (29 vs 30), explained in §1 by rep2's scratch carrying the
author's untracked `phys2d_motion.gd`; rep1 vs the frozen-worktree rep4 is
**output-normalized identical on all 104 carried outputs**, which is the cleanest statement
of frozen-tree equivalence (live-tree pre-landing bytes ≡ worktree bytes under
the declared volatile masks of §5 C2).

### 3.2 vs pre-fold 111-row receipts (six receipts, all carrying pre-fold bytes)

Every one of these six receipts was produced before commit `f777925`
(05:43:12Z) and, independently of commit timing, carries **pre-fold bytes** —
proven by its missing fold-added pin fields (below).

| ref | common | new/old | tuple mism | root cause of every mismatch |
|---|---|---|---|---|
| `r79-author/runs/…T235547072468Z` | 111 | 0/0 | 3 | 2 seeded pins + 1 meta discrimination (below) |
| `r79-author/runs/…T045301196389Z` | 111 | 0/0 | 3 | same |
| `r79-author/runs/…T045607640159Z` | 111 | 0/0 | 3 | same |
| `r79-simplifier/control-runs/…T051454229720Z` | 111 | 0/0 | 3 | same |
| `r79-simplifier/fold-runs/…T051725980038Z` | 111 | 0/0 | 3 | same |
| `r80-scout/runs/…T050846740845Z` | 111 | 0/0 | 3 | same |

The 3 mismatches are **the r79 fold's own corrections**, not drift:
`phys2d_events_cm_max0` and `phys2d_events_cm_off` differ **only in the pinned
expected signature** — frozen pins carry the fold-added fields
(`post_monitor=true post_max=0` and `post_monitor=false post_max=4`) that the
pre-fold pins lack; the measured output bodies are otherwise identical. The meta
row `probe_error_clause_surface` differs by the fold-added discrimination
`phys2d_expected_errors_all_matched: true`. Every pre-fold ref is therefore a
**pre-correction** artifact and must not be used as the r80 post-landing
reference without this delta note.

### 3.3 vs 88-row r79-baseline frozen refs and a negative control

| ref | common | new/old | tuple mism |
|---|---|---|---|
| `r79-baseline/freeze/godot-runs/…T235028993722Z` (88 rows) | 88 | 0/**23** | 1 (fold discrimination) |
| `r79-baseline/freeze/godot-runs2/…T235235106974Z` (88 rows) | 88 | 0/**23** | 1 (fold discrimination) |
| CONTROL `r79-author/runs/…T235129005491Z` (pre-fold **FAIL**) | 111 | 0/0 | **4** (2 seeded + 2 meta) |

`new_only` 0 / `old_only` 23 = exactly the r79 `phys2d_events` rows, the
r79→r80 lattice growth. The control receipt is a FAIL run and the comparator
sees it (4 mismatches) — the 0-mismatch results above are not vacuous.

### 3.4 vs post-landing 139-row receipts (secondary; rows 1–111 unchanged)

| ref | rows | common | old_only | tuple mism |
|---|---|---|---|---|
| `r80-author/runs/…T055428670225Z` (PASS) | 139 | 111 | **28** = exactly the `phys2d_motion` rows | 1 (meta census only) |
| `r80-author/runs/…T055149737742Z` (FAIL) | 139 | 111 | 28 | 2 (`phys2d_events_cm_max0` FAIL in that receipt + census) |
| `r84-scout/runs/…T055511508939Z` (PASS) | 139 | 111 | 28 | 1 (meta census only) |

The single meta mismatch against the PASS receipts is the
`probe_error_clause_surface` census, which counts across the whole battery:
`rows_with_expected_errors` 43→45 and `scan_clause_census.ERROR:_per_line_lines`
53→61 — the expected effect of 28 added rows, not a row-1–111 change. **No
seeded row of the frozen 111 differs against any post-landing receipt.**

---

## 4. rep3 — the one FAIL, root-caused to host input state (not lattice drift)

rep3 (frozen worktree, `d9320dd`, harness sha verified identical before and
after) returned rc=1 with **exactly one** non-PASS row:

```
case: wrong_key   script: causal_chain.gd   flags: ["--wrong-key-negative"]
signature matched: "PASS wrong_key=F receipts=0 intent=false physics_moves=0 …"
verdict: FAIL     (expected_errors: [])
extra output lines:
  ERROR: Error opening gamepad at index 1: Couldn't find mapping for device (1)
     at: process_events (drivers/sdl/joypad_sdl.cpp:141)
```

The frozen classifier (`classify_process`, `run_battery.py` lines 215–233)
fails any row carrying an `ERROR:` line outside `expected_errors`; the SDL
joypad enumeration emitted one. The host shows **no** `/dev/input/js*` and no
joystick in `/proc/bus/input/devices`, so this is SDL/udev enumeration noise,
not a device the battery drives. Precedent in-repo: the identical two lines
flipped `checkbox_toggle` in
`corpus/live/r59-audio-executor/seven-flags/20261013T133719712820Z/verdicts.json`
(2026-10-13). Occurrence rate here: **1 of 4 reps**.

The flake's *complete* tuple footprint is exactly two rows (verified by
character-level diff of the canonical tuples):
1. `wrong_key`: `verdict` PASS→FAIL plus the 2 output lines;
2. meta `probe_error_clause_surface`: the census counter
   `ERROR:_per_line_lines` 53→54 (the extra `ERROR:` line is counted).

A verifier seeing a lone FAIL row carrying `joypad_sdl.cpp:141` should treat it
as host input state and re-run, not as a regression.

---

## 5. Remaining risks / caveats

- **C1 — meta rows are compared on verdict-bearing fields only.** Per-arm
  launch records (`arms`, `seam_split_run`, raw streams, pids, elapsed) are
  excluded by declaration; a regression inside an arm record that leaves
  `verdict`/`discriminations` intact is not caught by this freeze (it is caught
  by the battery's own meta verdict, which *is* in the tuple).
- **C2 — masked volatile classes** (secondary output comparison only; the tuple
  comparison is unmasked): run paths under `corpus/live/**`, pids, ASLR
  `Load address`/`0x…` addresses, `tween_flash` transient floats, fixture
  line-number tokens. The gamepad `ERROR:` line is deliberately **not** masked.
- **C3 — host input flake (§4).** Named row `wrong_key`, named anchor
  `drivers/sdl/joypad_sdl.cpp:141`. Any `expected_errors=[]` row can be flipped
  by it. It is not lattice drift and not this seat's to fix.
- **C4 — scope boundary.** The frozen set is **111 rows**; the live tree is now
  **139 rows** (132 `CASES` + 7 meta). Comparisons against this freeze must use
  the 111 common rows; the 28 `phys2d_motion` rows are outside this baseline.
- **C5 — pre-fold refs are stale by construction (§3.2).** Six 111-row receipts
  predate `f777925` and differ from frozen bytes on 3 rows by the fold's own
  corrections. Do not use them as the r80 post-landing reference without the
  delta note.
- **C6 — frozen worktree left registered (deliberate).**
  `/home/vgpnk/Projects/shokunin/r80-baseline-frozen-worktree` is a detached
  `d9320dd` worktree and appears in `git worktree list`. It is the round's
  frozen-tree evidence; operator cleanup is `git worktree remove
  /home/vgpnk/Projects/shokunin/r80-baseline-frozen-worktree` (no branch, no
  commit, main worktree untouched).
- **C7 — this seat's writes.** Tracked-file state before and after is identical
  except the author's own in-flight edits (`post-run-dirty-state.txt`:
  ` M SCORECARD.md` pre-existing, ` M corpus/fixtures/run_battery.py`,
  `?? corpus/fixtures/phys2d_motion.gd`, `?? …/__pycache__/*.pyc` pre-existing).
  Nothing under `corpus/fixtures/` was written by this seat (`python3 -B` +
  `PYTHONDONTWRITEBYTECODE=1` throughout).

## 6. Verdict

Frozen HEAD `d9320dd` reproduces the closed r79 lattice at the 111-row scope:
**111/111 PASS in three independent samples** (rep1 and rep2 on the clean live
tree — rep2 provably on frozen bytes across the author's tracked write — and
rep4 from a materialized `d9320dd` worktree), **0 tuple mismatches among
rep1/rep2/rep4**, and rep1 ≡ rep4 output-normalized identical on all 104 carried
rows. The one non-PASS sample (rep3) is a single intermittent SDL gamepad
`ERROR:` line, named and root-caused, not lattice drift. The r80 before-state is
`corpus/live/r80-baseline/freeze/godot-tuples-rep1.txt` (sha256 `ffb7a2c4…`,
111 rows, all PASS) with receipt shas in `freeze/receipt-shas.txt`; the frozen
rows provably predate the r80 arm's first tracked write by 3 min 24 s.
