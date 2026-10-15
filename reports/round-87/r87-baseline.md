# Round 87 baseline (g2d) — frozen-tree regression replay (host: devin)

Seat: `g2d-r87-baseline` (LEAF, executor). Read-only on tracked files: no fixture
or runner edit, no commit, no LOG/SCORECARD write. All artifacts under
`corpus/live/r87-baseline/` (untracked scratch) plus this new report.
All Godot launches `--headless` and `timeout`-bounded (harness 8 s/row, 60 s for
the two export rows; outer `timeout 900` per rep).

**STATUS: COMPLETE — 182 rows replayed twice, 182/182 PASS in both reps,
182/182 rows byte-identical to the committed r86 landing receipt, 0 drift rows.**

| headline | value |
|---|---|
| rows replayed | **182** (175 seeded `CASES` + 7 meta) × 2 reps |
| rep1 / rep2 verdict | 182/182 PASS / 182/182 PASS, rc=0, stderr 0 B |
| tuple byte-identical vs committed receipt | **182/182** |
| drift rows vs committed receipt | **none (0)** |
| internal rep1 × rep2 | 182/182 byte-identical; tuple bodies sha256 `50988e1d…` both reps |
| SDL joypad `ERROR:` flake | not observed (0 of 2 reps) |

**HEAD disclosure.** Dispatch cited `fad0b1e`; actual HEAD at freeze and through
both reps was `fad0b1e6566e33650fb13eb37725b9c7ad4a62f4` (unchanged pre/post each
rep, `rep-timing.txt`). `git diff 01dd32b fad0b1e -- corpus/fixtures/` is
**empty**, so the frozen fixture bytes are also exactly the r86 fold bytes.

**Post-hoc HEAD move (disclosed, does not invalidate the pin).** After rep2 the
orchestrator committed `96c0b13` (*r87: read-only boundary analysis*). That commit
touches **one file** — `reports/round-87/r87-boundary-readonly.md` (+84) — and
`git diff fad0b1e 96c0b13 -- corpus/fixtures/` is **empty**, so the fixture bytes
this baseline froze are still the current tracked fixture bytes. The pin of record
stays `fad0b1e`.

**`lsp` disclosure.** No `lsp` device is exposed in this session (same host state
as `r87-scout`); no GDScript/Python server is installed. This seat made no
symbol-aware edit — a read-only freeze/replay has no rename/reference work. Every
write is a new untracked scratch file under `corpus/live/r87-baseline/` plus this
new report; nothing was hand-renamed.

**Subagent disclosure.** This seat is the frozen `probeParent` and dispatched
**zero** descendants. The probe grant is permissive ("may dispatch exactly one
read-only labrat"); the canonical assignment requests no probe and the wave
already assigns a separate `ufo-labrat` boundary seat (`corpus/live/r87-boundary/`
is live), so no empirical hypothesis was left unfalsified by a probe here.

---

## 0. Timeline (UTC, first-hand)

| time | event |
|---|---|
| 17:01:23Z | `git archive HEAD \| tar -x -C corpus/live/r87-baseline/tree` start |
| 17:01:27Z | freeze done — 1.6 GB, 90 876 regular files + 68 symlinks |
| ~17:01:3xZ | freeze verified: file-list diff vs `git ls-files` = 0; harness sha = HEAD blob |
| **17:01:36.085Z** | **rep1** receipt stamp; pre-marker `harness=b3ef9a2f… live_head=fad0b1e…` |
| **17:04:18Z** | **rep1** end, rc=0, **162.308 s**, 182/182 PASS |
| 17:04:19Z | pre-rep2 marker, same harness sha, same live HEAD |
| **17:07:09Z** | **rep2** end, rc=0, **169.732 s**, 182/182 PASS (`runs2/20261015T170420012317Z`) |
| 17:07:35Z | post-run: `git status` shows **no tracked modification**; post-rep full-tree `diff -rq` vs a fresh `git archive HEAD` = **0 differences** |

Environment (`env.txt`): Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`), Python 3.14.7, Linux 7.2.3-arch1-3 x86_64, 32 cpus, load
0.81 at capture.

---

## 1. Frozen-tree provenance

- Frozen HEAD `fad0b1e6566e33650fb13eb37725b9c7ad4a62f4` (reconcile: late r78
  wave-B reports + fleet-round-1 audit + forward scouts; fixture bytes equal to
  `01dd32b`).
- Freeze method: `git archive --format=tar HEAD | tar -x -C
  corpus/live/r87-baseline/tree` — **tracked bytes only**, no worktree mutation.
- Integrity: `diff` of `git ls-files` (90 944 entries) against the extracted
  tree's file+symlink list = **0 lines** (68 tracked symlinks preserved); frozen
  `corpus/fixtures/run_battery.py` sha256
  `b3ef9a2f5843356c84ef73fe0cf54018930261163e8e9d2a1a4848c70796c99a` equals
  `git show HEAD:corpus/fixtures/run_battery.py`.
- Row census: `CASES` = 175 (AST count) + 7 meta
  (`probe_save_independent_process`, `probe_spontaneous_crash_classification`,
  `probe_descendant_pipe_eof`, `probe_descendant_signature_spoof`,
  `probe_while_live_signature_gate`, `probe_descendant_error_spoof`,
  `probe_error_clause_surface`) = **182** (`freeze/row-names.txt`).
- Post-replay: a fresh archive of HEAD diffed `-rq` against the frozen tree =
  **0 differences** → neither rep wrote into the frozen tree.

### Exact invocations

Runner `corpus/live/r87-baseline/run-reps.sh` (cwd = frozen tree, absolute
`--runs` paths, `PYTHONDONTWRITEBYTECODE=1 python3 -B`, outer `timeout 900`):

```
cd corpus/live/r87-baseline/tree
timeout 900 python3 -B corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r87-baseline/runs1   # rep1
timeout 900 python3 -B corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r87-baseline/runs2   # rep2
```

---

## 2. The frozen reference tuples

Per-row Godot **verdict tuple**: `(case, script, flags, expected_exit,
actual_exit, signature, verdict, error, expected_errors)` for the 175 seeded
rows; `(case, verdict, canonical JSON minus declared-volatile keys)` for the 7
meta rows. Extractor `tuples.py` and comparator `compare.py` copied verbatim from
`corpus/live/r81-baseline/` (shas `e60eebce…` / `a28d65e9…`); byte-level counts
added by `r87_compare.py` / `rowtable.py` (this seat).

| artifact | sha256 |
|---|---|
| **`freeze/godot-tuples-rep1.txt` — THE FROZEN SET** | `4222d822b842d1b2035c9aa59c6574233bfa11bdf98627fae87133fb7957d637` |
| `freeze/godot-tuples-rep2.txt` | `d09075336cbcdb325d395318c6969048a73cae71d8945892994be780353abbe8` |
| rep1 `runs1/20261015T170136085777Z/verdicts.json` | `56bfa6017413be7f84578a95a267b5261e988da5108c65606170650b04dffea0` |
| rep2 `runs2/20261015T170420012317Z/verdicts.json` | `c443fb40236a739a733bc9ebc99ac468440d1ffc3eca0ae00b9a512289c6e712` |

The 182 tuple **bodies** are byte-identical between rep1 and rep2 (sha256
`50988e1dfca9b221cbc85d821b9882c5dc0f432b540c3e06d1a20556820345f6`); the file
shas differ only in the header line recording the source `verdicts.json` sha.
All receipt shas: `freeze/receipt-shas.txt`.

---

## 3. Stability and reference comparisons

Metrics: **tuple byte-identical** = canonical stable-tuple JSON byte-equal;
**raw stdout** = merged `output` list joined, NO normalization; **normalized** =
r81 masking of declared-volatile tokens. Comparisons:
`freeze/compare-rep1.txt`, `freeze/compare-rep1-external.txt`,
`freeze/compare-rep2-fold.txt`, per-row table
`freeze/row-table-rep1-vs-fold-r86.txt`.

### 3.1 Internal (frozen bytes ×2) — ZERO drift

| mine → ref | common | new/old | tuple byte-identical | tuple mism | raw stdout | normalized |
|---|---|---|---|---|---|---|
| rep1 → rep2 | 182 | 0/0 | **182/182** | **0** | 167 identical, 8 differing, 7 not-carried | **175 identical, 0 differing**, 7 not-carried |

### 3.2 vs the committed receipt for the frozen bytes — ZERO drift

The r86 fold receipt `corpus/live/runs/20261015T160405358447Z/verdicts.json`
(182 rows, PASS, sha `481d0810…`) was produced on the *same fixture bytes* as
HEAD (`01dd32b→fad0b1e` fixture diff empty).

| mine → ref | common | new/old | tuple byte-identical | tuple mism | raw stdout | normalized |
|---|---|---|---|---|---|---|
| rep1 → r86 fold receipt | 182 | 0/0 | **182/182** | **0** | 167 identical, 8 differing, 7 not-carried | **175 identical, 0 differing** |
| rep2 → r86 fold receipt | 182 | 0/0 | **182/182** | **0** | (same class) | **175 identical, 0 differing** |

**Drift rows: none.** The 8 raw-stdout-differing rows are exactly the
declared-volatile class, named individually in
`freeze/row-table-rep1-vs-fold-r86.txt`:

| row | differing token | class |
|---|---|---|
| `crash_spontaneous_sigabrt` | `Load address: 56442fe2b000` vs `55be0ed72000` | ASLR |
| `descendant_pipe_detached_control` | `godot_pid=1125575` vs `1338489` | pid |
| `descendant_pipe_forged_signature_release` | `godot_pid=1125676` vs `1338529` | pid |
| `save_process_writer` | `pid=… path=…/r87-baseline/runs1/…` | pid + run path |
| `save_process_reader` | same class | pid + run path |
| `save_process_missing` | same class | pid + run path |
| `save_roundtrip` | `user_path=…/r87-baseline/runs1/…` | run path |
| `tween_flash` | `transient_modulate=(0.7046, 0.7908, 0.8877, 1.0)` vs `(0.704, 0.7919, 0.8892, 1.0)` | transient float jitter (pin is a prefix) |

All 8 are inside the r81/r86 declared-volatile mask; every one of them is
normalized-identical. The 7 meta rows carry no `output` list (compared on
verdict-bearing fields only, both PASS). Seeded-row raw identity is therefore
**167/175** with the residual fully attributed; normalized identity **175/175**.

### 3.3 vs pre-fold r86 receipts (known pre-final artifacts)

| ref | common | tuple byte-identical | mismatches | normalized |
|---|---|---|---|---|
| `r86-verify/run1/…T133754513801Z` | 182 | 176/182 | 6 | 169 identical, **6 differing** |
| `r86-verify/run2/…T134054380982Z` | 182 | 176/182 | 6 | 169 identical, 6 differing |
| `r86-author-battery/…T130812159398Z` | 182 | 176/182 | 6 | 169 identical, 6 differing |

The 6 mismatches are `phys2d_backends_{dummy_degenerate, dummy_timeout,
gate_duality, gate_matrix, lattice, xcheck}` — precisely the rows the r86 fold
**re-pinned** (`reports/round-86/r86-fold.md`: "All 8 CASES rows repinned"), with
the fold's discovered-bimodality envelopes replacing the pre-fold literal pins
(`moved=17.867` → `mv=pos|zero`, `dur_ms` → `dur_ge`, `thr[…]` → `thr_ok`). The
other 2 of the 8 new rows (`phys2d_backends_census`, `phys2d_backends_jolt3d_live`)
are byte-unchanged. These three refs were produced before the fold landed and are
**not** drift against the frozen bytes; both frozen reps reproduce the folded
bytes exactly (182/182 vs §3.2).

### 3.4 vs r85 (174-row scope) — intersection clean, growth expected

| ref | common | new_only | tuple byte-identical | mismatches | normalized |
|---|---|---|---|---|---|
| `r85-foldc-final2/…T085238195177Z` | 174 | **8** | **174/174** | **0** | 167 identical, **0 differing**, 7 not-carried |

`new_only` = exactly the 8 `phys2d_backends_*` rows landed by r86. Zero drift on
the intersection.

### 3.5 vs the last git-tracked battery receipt (111 rows, r79)

No *git-tracked* receipt exists at the 182-row scope: `git ls-files` receipts top
out at r79 (`r79-verify/runs-clean` = 111 rows; the largest tracked
`verdicts.json` anywhere is a 149-row r79-baseline extract of an r64 receipt).
Against `r79-verify/runs-clean/…T050805946857Z`:

| ref | common | new_only | tuple byte-identical | mismatches | normalized |
|---|---|---|---|---|---|
| r79-verify/runs-clean | 111 | **71** | 108/111 | 3 | 100 identical, 4 differing |

- 2 mismatches are `phys2d_events_cm_max0` / `phys2d_events_cm_off` — signature
  fields extended by r80+ (`valid=true exit1_fr…` appended; `phys2d_events.gd`
  line numbers moved, masked by normalization).
- 1 mismatch is the `probe_error_clause_surface` meta census, which counts across
  the whole battery and therefore scales with +71 rows (r81 §3.3 precedent).
- `new_only` = the r80–r86 growth (phys2d_motion/joints/backends + camera_proc
  lattice). Expected, not drift.

### 3.6 SDL joypad flake watch

Named host class (`drivers/sdl/joypad_sdl.cpp:141`, precedent r80 §4 / r81 §3.4):
**not observed** — 0 joypad lines, 0 `FAIL` lines, 0 non-PASS rows, 0 stderr
bytes in either rep. The 5 `ERROR:` lines in each stdout are the expected
negative-control signatures (`export_preset_missing`, `checkbox_toggle_disconnected`,
`button_group_selection_disconnected`, `save_corrupt_negative`,
`save_process_missing`), all PASS.

---

## 4. Remaining risks / caveats

- **C1 — "committed receipts" reading.** The r86 receipts used in §3.2 are on
  disk but **untracked in git**; no git-tracked receipt covers 182 rows (§3.5).
  Both comparisons are reported; the primary is the r86 fold receipt, which is
  the receipt for the exact frozen bytes. If a later seat re-defines the
  reference set, the tuple bodies in `freeze/godot-tuples-rep1.txt` are the
  frozen anchor.
- **C2 — masked volatile classes.** Raw-stdout identity is 167/175 seeded rows by
  construction; the 8 rows are enumerated in §3.2. The gamepad `ERROR:` line is
  deliberately *not* masked and did not appear.
- **C3 — meta rows compared on verdict-bearing fields only** (r81 C1): per-arm
  launch records (pids, paths, timing) are declared volatile; both reps PASSed
  the meta verdicts.
- **C4 — concurrent seats.** `corpus/live/r87-boundary/` is live (separate
  labrat seat); no tracked byte changed during either rep (`git diff HEAD --
  corpus/fixtures reports` empty; HEAD identical pre/post). Load 0.81 → low
  timing-flake risk; 0 observed.
- **C5 — bimodal envelope rows.** The 8 `phys2d_backends_*` rows carry
  mode-envelope pins (r90/r87 lesson), so a mode flip inside the envelope keeps
  `PASS` while changing raw output. Both reps matched the committed receipt's
  envelope on all 8 (tuple byte-identical), so no flip was realized here; the
  envelope's mode *distribution* is not re-derived by a 2-rep replay.
- **C6 — `lsp` unavailable** (no device in session): no symbol-aware work was
  required; disclosed rather than silently hand-edited.
- **C7 — freeze footprint.** `corpus/live/r87-baseline/tree/` is a 1.6 GB
  directory copy inside the repo's untracked scratch; prunable with
  `rm -rf corpus/live/r87-baseline/tree` (no branch, no worktree registration,
  main worktree untouched).
- **C8 — this seat's writes.** `post-run-dirty-state.txt`: **no tracked
  modification** (`git status --porcelain` filtered of `??` is empty). New
  untracked paths: `corpus/live/r87-baseline/**` (tree, runs1, runs2, freeze,
  runner/extractor scripts, stdouts, env/timing receipts) and this report.

---

## 5. Verdict

Frozen HEAD `fad0b1e` reproduces the closed r86 lattice at the 182-row scope:
**182 rows replayed twice inside the frozen tree, 182/182 PASS in both reps,
182/182 tuple byte-identical to the committed r86 landing receipt
(`corpus/live/runs/20261015T160405358447Z`), 0 drift rows, tuple bodies
byte-identical across reps.** The r87 before-state is
`corpus/live/r87-baseline/freeze/godot-tuples-rep1.txt` (sha256
`4222d822b842d1b2035c9aa59c6574233bfa11bdf98627fae87133fb7957d637`, 182 rows,
all PASS) with receipt shas in `freeze/receipt-shas.txt`. The r87 author's
`input_lattice.gd` landing is outside this baseline by construction (absent from
the frozen bytes; post-landing comparisons must intersect on these 182 rows).
