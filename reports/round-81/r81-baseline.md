# Round 81 baseline report — freeze + frozen tuple set (host: devin)

Seat: g2d baseline (LEAF). Read-only on tracked files: no fixture/runner edit, no
commit, no LOG/SCORECARD write. All artifacts under `corpus/live/r81-baseline/`
(untracked scratch) plus this report. Frozen worktree `/tmp/r81-frozen`
(detached, see C6).

Battery scope per brief: the **tracked Godot battery**
(`corpus/fixtures/run_battery.py`, **139 rows** = 132 seeded `CASES` + 7 meta).
The r81 author is concurrently landing `corpus/fixtures/phys2d_joints.gd`;
**that file and its CASES rows are absent from the frozen bytes** and therefore
outside this baseline by construction.

**STATUS: COMPLETE.** Frozen `27f465c` and replayed twice from the detached
worktree: **139/139 PASS in rep1 and rep2**, **0 tuple mismatches** between
them, tuple bodies byte-identical, all 132 carried outputs identical. The
frozen tuple set is
`corpus/live/r81-baseline/freeze/godot-tuples-rep1.txt` (sha256
`925560751be7a6a8ac0eccca804212e1d517c75a27e2ff9ecbeb08f27ce8b033`). The SDL
joypad `ERROR:` flake class was **not observed** (0 of 2 reps).

**HEAD disclosure.** The dispatch cited `f27f952`; actual HEAD at freeze was
`27f465c` (*r80 LOG: ADMIT-corr*, LOG.md +18 only — `git diff f27f952 27f465c --
corpus/fixtures/` is **empty**, so fixture bytes are identical either way).

**`lsp` disclosure.** No `lsp` device is exposed in this session. This seat
made no symbol-aware edit (a read-only freeze has no rename/reference work): it
wrote new scratch files (`corpus/live/r81-baseline/**`), the detached worktree,
and this new report. Nothing was hand-renamed.

---

## 0. Timeline

All times UTC. Receipts first-hand: `freeze-head.txt`, `rep-timing.txt`,
`env.txt`, `freeze/worktree-receipt.txt`, run stdout/stderr.

| time (UTC) | event |
|---|---|
| ~06:39:5xZ | `git worktree add --detach /tmp/r81-frozen HEAD` — detached at `27f465c67995dfe3607bc4b7ed0b7492b95ec835` |
| 06:40:12Z | `env.txt` (Godot 4.7.2.stable.arch_linux.ed1daf0bf, Python 3.14.7, 32 cpus, load 2.19) |
| **06:40:17.915Z** | **rep1** start (frozen worktree); harness `d13797a8…`, `phys2d_joints.gd` absent |
| **06:42:06Z** | **rep1** end, rc=0, **108.085 s**, **139/139 PASS** |
| ~06:42:0xZ | author's `phys2d_joints.gd` observed as **untracked** file in live tree (first seen during rep1 window) |
| **06:42:46.152Z** | **rep2** start (frozen worktree); harness `d13797a8…` unchanged |
| **06:44:41Z** | **rep2** end, rc=0, **115.880 s**, **139/139 PASS** |
| 06:44:4xZ | closing state: live HEAD still `27f465c`; live tree shows author's in-flight ` M corpus/fixtures/run_battery.py` + `?? phys2d_joints.gd` — **no tracked landing during either rep** |

rep1/rep2 pre/post markers record identical harness sha and identical live HEAD
(`rep-timing.txt`), so no tracked bytes could have entered either replay.

---

## 1. Frozen-tree provenance

- Frozen HEAD: `27f465c67995dfe3607bc4b7ed0b7492b95ec835` — *r80 LOG:
  ADMIT-corr*, committed 2026-10-15T03:29:17-03:00. Parent `f27f952` (r80
  phys2d_motion lattice, folded ADMIT-corr); the LOG commit touches no fixture.
- Frozen harness sha256
  `d13797a8a7d43c45d59aaeead31248a509648611fc679349ed76dca9b521b58e`
  (identical before and after each rep). 132 seeded `CASES` rows + 7 meta rows
  (`probe_audio_warning_captured_r12` arm, `probe_save_independent_process`,
  `probe_spontaneous_crash_classification`, `probe_descendant_pipe_eof`,
  `probe_descendant_signature_spoof`, `probe_while_live_signature_gate`,
  `probe_descendant_error_spoof`, `probe_error_clause_surface` — the battery's
  own meta census) = **139 rows** (`freeze/row-names.txt`).
- `phys2d_joints.gd` **absent** from the frozen tree (verified at pre-rep1 and
  pre-rep2 markers); the author's joints work is excluded by construction.
- Frozen worktree: `/tmp/r81-frozen`, detached at `27f465c`, registered in
  `git worktree list` (`freeze/worktree-receipt.txt`).

### Exact invocations

cwd `/tmp/r81-frozen`, `PYTHONDONTWRITEBYTECODE=1 python3 -B`, absolute `--runs`
paths (runner: `corpus/live/r81-baseline/run-reps.sh`):

```
python3 -B corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r81-baseline/runs1   # rep1
python3 -B corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r81-baseline/runs2   # rep2
```

Environment (`env.txt`): Linux 7.2.3-arch1-3 x86_64, Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python 3.14.7,
node v24.21.0, `io.DEFAULT_BUFFER_SIZE` 131072, 32 cpus; load 2.19 at env
capture.

---

## 2. The frozen reference tuples

Per-row Godot **verdict tuple**: `(case, script, flags, expected_exit,
actual_exit, signature, verdict, error, expected_errors)` for the 132 seeded
rows; for the 7 meta rows `(case, verdict, canonical JSON minus
declared-volatile keys)`. Extractor `tuples.py`, comparator `compare.py`
(r80's, copied verbatim — shas in the receipt dir).

| artifact | sha256 |
|---|---|
| **`freeze/godot-tuples-rep1.txt` — THE FROZEN SET** | `925560751be7a6a8ac0eccca804212e1d517c75a27e2ff9ecbeb08f27ce8b033` |
| `freeze/godot-tuples-rep2.txt` | `211a75c59b62493c0863b85b8bdc3c2b5fcfe12bcafc11958faf5c72d80003c9` |
| rep1 `verdicts.json` | `e33e123b3904544c8c215b29d67007330b360efe4b988c647b8baad32feb2d11` |
| rep2 `verdicts.json` | `bb6368bf33df3af5b319e962c707313b12442192d7100c2758d7ca9122052ee8` |

All 139 rows verdict **PASS** in both reps. The tuple-set *bodies* (the 139
`case<TAB>verdict<TAB>sha` lines) are **byte-identical** between rep1 and rep2;
file shas differ only in the header line recording the source `verdicts.json`
sha. Receipt shas in `freeze/receipt-shas.txt`.

---

## 3. Stability and reference comparisons

`compare.py godot` outputs: `godot-compare-rep1-rep2.txt`,
`godot-compare-rep1-external.txt`.

### 3.1 Internal (frozen bytes ×2) — ZERO drift

| mine → ref | common | new/old | tuple mism | output-normalized |
|---|---|---|---|---|
| rep1 → rep2 | 139 | 0/0 | **0** | **132 identical, 0 differing**, 7 not-carried |

### 3.2 vs r80 post-landing receipts (139-row refs)

| ref | common | new/old | tuple mism | note |
|---|---|---|---|---|
| `r80-author/runs/…T055428670225Z` (PASS) | 139 | 0/0 | 1 | `phys2d_motion_ccd_edge` — **pre-final artifact**, below |

The single mismatch is `phys2d_motion_ccd_edge`: the frozen pin
(`run_battery.py:166`) and the committed fixture (`phys2d_motion.gd:295`,
`_finish("ccd_edge … %s w[%s]")`) always carry the `w[hit=true travel=…
cls=StaticBody2D]` segment; the r80-author receipt's signature/output **lack
it**. `f27f952→27f465c` has zero fixture diff, so the ref's shorter row was
produced from the author's **mid-flight working bytes** before the final
pin/extension landed — the same class as r80 §3.2's pre-fold receipts. It is
not drift in this freeze: rep1 and rep2 reproduce the pinned `w[...]` bytes
identically. **Do not use `r80-author/…T055428670225Z` as an r81 reference
without this delta note.**

### 3.3 vs r80-baseline frozen ref (111-row scope)

| ref | common | new_only | old_only | tuple mism |
|---|---|---|---|---|
| `r80-baseline/runs1/…T054820716045Z` | 111 | **28** | 0 | 1 (meta census only) |

`new_only` = exactly the 28 `phys2d_motion_*` rows (the r80 lattice growth,
expected). The lone meta mismatch is `probe_error_clause_surface`'s census,
which counts across the whole battery — expected to scale with +28 rows, not a
row-1–111 change. Output diffs: the two export rows' `update_scripts_classes`
counter (29→30 steps) because `phys2d_motion.gd` is now a registered global
class in the frozen tree; the token is outside every verdict tuple.

### 3.4 SDL joypad flake watch

Named host class (`drivers/sdl/joypad_sdl.cpp:141`, precedent r80 §4 /
`r59-audio-executor`). **Not observed in rep1 or rep2** — zero non-PASS rows,
zero stray `ERROR:` verdict effects. No re-run was triggered.

---

## 4. Remaining risks / caveats

- **C1 — meta rows compared on verdict-bearing fields only** (carried from
  r80): per-arm launch records (pids, paths, timing) are declared volatile; a
  regression inside an arm record that leaves `verdict`/`discriminations`
  intact is caught only by the battery's own meta verdict — which is in the
  tuple and PASSed twice.
- **C2 — masked volatile classes** (secondary output comparison only): run
  paths under `corpus/live/**`, pids, ASLR addresses, `tween_flash` transient
  floats, fixture line-number tokens. The gamepad `ERROR:` line is deliberately
  not masked.
- **C3 — host input flake.** `joypad_sdl.cpp:141` can flip any
  `expected_errors=[]` row; 0/2 observed here. A lone FAIL carrying that line
  is host input state — re-run once before flagging, per the brief.
- **C4 — scope boundary.** The frozen set is **139 rows** at `27f465c`; the
  r81 author's `phys2d_joints` rows are outside this baseline (absent from the
  frozen bytes). Post-landing comparisons must intersect on the 139 common
  rows.
- **C5 — r80-author mid-flight receipt is a pre-final artifact** for
  `phys2d_motion_ccd_edge` (§3.2). Not a reference for this freeze.
- **C6 — frozen worktree left registered at `/tmp/r81-frozen` (deliberate,
  ephemeral).** `/tmp` does not survive reboot; the stale registration is then
  prunable with `git worktree prune`. Cleanup now:
  `git worktree remove /tmp/r81-frozen` (no branch, no commit, main worktree
  untouched).
- **C7 — rep1 wall time is stamp→end-marker (108.085 s, ±1 s).** `bc` is absent
  on this host; the runner was patched to `awk` before rep2 (115.880 s exact).
  Both durations are also bound by the stamped dir name and end markers in
  `rep-timing.txt`.
- **C8 — this seat's writes.** `post-run-dirty-state.txt`: ` M SCORECARD.md`
  (pre-existing), ` M corpus/fixtures/run_battery.py` and
  `?? corpus/fixtures/phys2d_joints.gd` (author's in-flight landing),
  `?? …/__pycache__/love_battery.cpython-314.pyc` (pre-existing). Nothing under
  `corpus/fixtures/` was written by this seat (`python3 -B` +
  `PYTHONDONTWRITEBYTECODE=1` throughout); no tracked file changed.

## 5. Verdict

Frozen HEAD `27f465c` reproduces the closed r80 lattice at the 139-row scope:
**139/139 PASS in two independent worktree replays, 0 tuple mismatches, tuple
bodies byte-identical, all 132 carried outputs identical.** The r81
before-state is
`corpus/live/r81-baseline/freeze/godot-tuples-rep1.txt` (sha256
`92556075…`, 139 rows, all PASS) with receipt shas in
`freeze/receipt-shas.txt`; the author's `phys2d_joints` landing never entered
the frozen bytes (untracked in live tree throughout both reps; absent in the
worktree). Largest single receipt file is 286,629 bytes — far under the 100 MB
bound; total receipt dir 4.6 MB.
