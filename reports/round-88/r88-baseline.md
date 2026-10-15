# Round 88 baseline (g2d) — frozen-tree regression replay (host: devin)

Seat: `g2d-r88-baseline` (LEAF, executor / frozen `probeParent`). Read-only on
tracked files: no fixture or runner edit, no commit, no LOG/SCORECARD write.
All artifacts under `corpus/live/r88-baseline/` (untracked scratch) plus this
new report. All Godot launches `--headless`, `timeout`-bounded (harness 8 s/row,
60 s for the two export rows; outer `timeout 900` per rep).

**STATUS: FROZEN TREE IS GREEN IN THE CANONICAL QUIET CONDITION — 207/207 PASS
on rep1 with 207/207 tuple byte-identity vs the r87 landing receipt. Two
distinct PRE-EXISTING, LOAD-SENSITIVE flakes were observed on the frozen tree
(rep2: `crash_spontaneous_sigabrt` 8 s crash-dump timeout + 2-meta cascade;
supplementary rep3: `input_lattice_phys_peer` alt mode `ev_step_delta=2`).
Nothing was fixed; the frozen tree stayed byte-pure through all reps.**

| headline | value |
|---|---|
| rows replayed | **207** (200 seeded `CASES` + 7 meta) × 3 reps on the frozen tree |
| rep1 (canonical) | **207/207 PASS**, rc=0, stderr 0 B, 201.363 s |
| rep2 (canonical) | 204/207 PASS, rc=1 — pre-existing flake A (crash-row timeout, 3 FAIL) |
| rep3 (supplementary) | 206/207 PASS, rc=1 — pre-existing flake B (phys_peer alt mode, 1 FAIL) |
| rep1 vs r87 landing receipt `be5b0222…` | **tuple byte-identical 207/207, 0 mismatches** |
| rep1 vs rep2 | tuple byte-identical **204/207**; the 3 exceptions are exactly the flake-A cascade |
| rep1 vs rep3 | tuple byte-identical **206/207**; the 1 exception is exactly flake B |
| 5 envelope cells (`pre_frame`/`press_phys`/`release_edge`/`ui_ns`/`api_press`) | **5/5 tuple-identical and PASS in every rep**; observed modes vary (matrix §4.3) |
| declared-volatile rows | 8, raw-stdout-only; normalized-identical except envelope payload text |
| frozen-tree purity after reps | content `git diff --quiet HEAD` rc=0; file-set 0 differences |
| r88 author landing (post-freeze) | fixtures 18:14:01Z; live harness +42 lines / 8 new rows 18:15:14Z (live scope 207→215); every receipt here is the frozen 207-row pre-author scope |
| SDL joypad `ERROR:` flake | not observed (0 joypad lines in any rep) |

**HEAD disclosure.** Frozen and replayed at
`d15c54da464e940e0f314148eadca406d8d05def` (*r87 report-last: adjudicator
ADMIT-corr, LOG + SCORECARD verdict*), unchanged pre/post every rep. `git diff
7ef247c d15c54d -- corpus/fixtures/` is **empty**, so the frozen fixture bytes
are exactly the r87 landing bytes and the r87 verifier2 receipt
(`corpus/live/r87-verifier2/runs1/20261015T174757647842Z/verdicts.json`, sha
`be5b022207415bbc8a4b52b9b6f213fb9ea5b5f2b745b1a9f3b9c48e7d4234d7`) is the
canonical reference for them.

**Live-tree movement during this seat — the r88 author landed work (disclosed,
does not invalidate the freeze).** Untracked `corpus/fixtures/r88_surfaces.gd` +
`corpus/fixtures/r88_spawnable.tscn` appeared at **18:14:01Z** (21 s after rep2
ended), then the live `corpus/fixtures/run_battery.py` was edited at
**18:15:14Z** — +42 lines: 8 new `r88_surfaces_*` CASES rows (live `CASES`
200→208, live scope 207→215), the `r88_surfaces_sprite_phys` expected-error
whitelist, and the r88-prefix floor-gate extension — i.e. 12 s after rep3
started. All three reps ran from the **frozen** tree, so every receipt here is
the 207-row pre-author scope (rep3 receipt rows=207, verified); the frozen
harness sha stayed `69512316…` and the frozen tree stayed pure. Live HEAD was
`d15c54d` (uncommitted working-tree edits only) at last check. The r88 author's
landing is outside this baseline by construction.

**Post-hoc HEAD move (disclosed, does not invalidate the pin).** After the reps,
the r88-boundary seat committed `d3e16fb` (*r88 boundary: FALSIFIED audio
playing=false pin …*). `git diff d15c54d d3e16fb -- corpus/fixtures/` is
**empty** — that commit adds `corpus/live/r88-boundary/**` and
`reports/round-88/r88-boundary.md` only — so the fixture bytes this baseline
froze are still the current tracked fixture bytes. The pin of record stays
`d15c54d`; the r88 author's `r88_surfaces.gd` / `run_battery.py` edits remain
uncommitted working-tree changes.

**`lsp` disclosure.** No `lsp` device is exposed in this session (same host
state as r87-baseline); no GDScript/Python server is installed. This seat made
no symbol-aware edit — a read-only freeze/replay has no rename/reference work.

**Subagent disclosure.** This seat is the frozen `probeParent` and dispatched
**exactly one** read-only `ufo-labrat` (grant consumed) for an independent rep3
on the frozen tree. The probe seat's tool surface exposed only
`read`/`grep`/`find_file_by_name` — **no shell/exec capability** — so it could
not run the battery; it verified the receipt layout read-only and wrote
nothing. No re-dispatch was made (grant exhausted); the supplementary rep3 was
run by this seat directly and is labeled as such throughout.

---

## 0. Timeline (UTC, first-hand)

| time | event |
|---|---|
| 18:06:41Z | freeze start (`git archive --format=tar HEAD`) |
| 18:06:44Z | freeze done — 1.6 GB, 92 691 tracked entries + 68 symlinks |
| 18:06:44Z | identity proven: file-set 0 diff; `git diff --quiet HEAD` rc=0; harness sha == `git show HEAD:` |
| **18:06:56Z** | **rep1** start (load 3.85) |
| **18:10:17Z** | **rep1** end, rc=0, **201.363 s**, 207/207 PASS |
| **18:10:20Z** | **rep2** start (load 2.89) |
| **18:13:40Z** | **rep2** end, rc=1, **199.523 s**, 204/207 PASS — flake A |
| 18:13:4xZ | comparisons, labrat dispatch (no-shell return) |
| 18:14:01Z | r88 author lands untracked fixtures `r88_surfaces.gd` + `r88_spawnable.tscn` (21 s after rep2 end) |
| **18:15:02Z** | **rep3** start (supplementary; load 4.28, concurrent r88 seats) |
| 18:15:14Z | r88 author edits live `run_battery.py` (+42 lines: 8 new `r88_surfaces_*` rows, live scope 207→215) — 12 s after rep3 start; rep3 reads the frozen copy |
| **18:18:38Z** | **rep3** end, rc=1, **216.425 s**, 206/207 PASS — flake B (load 42.74) |
| 18:19Z | post-run: frozen tree content rc=0, file-set 0 diff; live HEAD `d15c54d`; no tracked modification by this seat |

Environment (`env.txt`): Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`), Python 3.14.7, Linux 7.2.3-arch1-3 x86_64, 32 cpus,
load 4.31 at freeze, 822 G free.

---

## 1. Frozen-tree provenance

- Frozen HEAD `d15c54da464e940e0f314148eadca406d8d05def`; freeze method
  `git archive --format=tar HEAD | tar -x -C corpus/live/r88-baseline/tree` —
  tracked bytes only, no worktree mutation.
- **File-set identity**: `git ls-files -z | sort -z` vs the extracted tree's
  file+symlink listing (`find . \( -type f -o -type l \) -printf '%P\0'`) =
  **0 differences**, **92 691 entries both sides**; symlinks 68 vs 68.
- **Content identity**: `GIT_DIR=…/.git GIT_WORK_TREE=…/tree git diff --quiet
  HEAD` → **rc=0** (no content/type difference on any tracked path).
- Frozen `corpus/fixtures/run_battery.py` sha256
  `69512316fc0104e09ec3caf6c71afdf8b9cf01fa37fc93d04b138c0ff751a1bf` equals
  `git show HEAD:corpus/fixtures/run_battery.py`.
- Row census: `CASES` = 200 (AST count) + 7 meta
  (`probe_save_independent_process`, `probe_spontaneous_crash_classification`,
  `probe_descendant_pipe_eof`, `probe_descendant_signature_spoof`,
  `probe_while_live_signature_gate`, `probe_descendant_error_spoof`,
  `probe_error_clause_surface`) = **207** (`freeze/row-names.txt`).
- **Post-replay purity** (after all 3 reps): content rc=0; file-set 0
  differences vs the pre-rep listing → no rep wrote into the frozen tree.

### Exact invocations

Runner `corpus/live/r88-baseline/run-reps.sh` (cwd = frozen tree, absolute
`--runs` paths, `PYTHONDONTWRITEBYTECODE=1 python3 -B`, outer `timeout 900`):

```
cd corpus/live/r88-baseline/tree
timeout 900 python3 -B corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r88-baseline/runs1   # rep1
timeout 900 python3 -B corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r88-baseline/runs2   # rep2
timeout 900 python3 -B corpus/fixtures/run_battery.py --runs <abs>/corpus/live/r88-baseline/runs3   # rep3 (supplementary)
```

---

## 2. Receipts and the frozen reference tuples

Per-row Godot **verdict tuple**: `(case, script, flags, expected_exit,
actual_exit, signature, verdict, error, expected_errors)` for seeded rows;
`(case, verdict, canonical JSON minus declared-volatile keys)` for meta rows.
Extractor `tuples.py` (sha `e60eebce…`) and comparator `compare.py` (sha
`a28d65e9…`) copied verbatim from `corpus/live/r87-baseline/` (the shas quoted
in the r87 baseline report); r88 wrapper `r88_compare.py` adds envelope-cell
classification.

| artifact | sha256 |
|---|---|
| **rep1 `runs1/20261015T180656420800Z/verdicts.json` — THE FROZEN SET (207/207 PASS)** | `91b3708dc36981f21a7edc3f6695407da1eeafd984d9a7fdbd735b256bb180e7` |
| rep2 `runs2/20261015T181020682010Z/verdicts.json` (204 PASS + 3 FAIL) | `c400cf2fa2bfa3601db63b0c0acaac09958f2745c07c2e3974e16bac446e076b` |
| rep3 `runs3/20261015T181502387628Z/verdicts.json` (206 PASS + 1 FAIL) | `3d1bfb400f84b2fb179cdc51852dba6ac9e78fed806225e2b6a1b32a696f03c9` |
| `freeze/godot-tuples-rep1.txt` (207 rows, all PASS) | `1dbf9deae1d8a7746767d0faa724fbc00a3284411eb69aad6d3bdb4dd1507777` |
| `freeze/godot-tuples-rep2.txt` | `c5f374d9a8dd1fe784e4cae25dec1204a6c0e00d0c0fbafc19791e9de9f450bf` |
| `freeze/godot-tuples-rep3.txt` | `f0e29f459efc824138e64b108ce9753feafa199bcaa9810f2c1a0c6a0456754a` |
| tuple **bodies** rep1 / rep2 / rep3 (207 rows each) | `4734189b…` / `0d159eea…` / `c289a253…` |
| rep1/rep2/rep3 stdout | `1e139f0d…` / `83050132…` / `e199c7d0…` |
| rep1/rep2/rep3 stderr | all `e3b0c442…` (0 B) |
| frozen harness | `69512316fc0104e09ec3caf6c71afdf8b9cf01fa37fc93d04b138c0ff751a1bf` |

Full sha list: `freeze/receipt-shas.txt`. Comparisons:
`freeze/compare-rep1.txt` (rep1→rep2), `freeze/compare-rep1-all.txt`
(rep1→{rep2,rep3,r87verifier2}), `freeze/compare-rep1-vs-r87.txt`
(rep1→{r87verifier2,r87critic2}), `freeze/compare-rep2-vs-r87.txt`,
per-row tables `freeze/row-table-rep1-vs-rep2.txt`,
`freeze/row-table-rep1-vs-r87verifier2.txt`.

---

## 3. Comparisons (metrics as in r81/r86/r87)

| mine → ref | common | new/old | tuple byte-identical | tuple mism | raw stdout | normalized |
|---|---|---|---|---|---|---|
| **rep1 → r87 verifier2 `be5b0222…` (canonical)** | 207 | 0/0 | **207/207** | **0** | 190 identical, 10 differing (2 envelope + 8 volatile), 7 not-carried | **198 identical, 2 differing** (2 envelope payload texts) |
| rep1 → r87 critic2 `a0a80fc0…` | 207 | 0/0 | **207/207** | **0** | 188 identical, 12 differing (4 envelope + 8 volatile), 7 not-carried | 196 identical, 4 differing |
| rep1 → r87 fold-check `ae6c5106…` | 207 | 0/0 | 207/207 | 0 | (same class) | (same class) |
| **rep1 → rep2** | 207 | 0/0 | **204/207** | **3** (flake A cascade) | 190 identical, 10 differing (2 envelope + 8 volatile), 7 not-carried | 197 identical, **3 differing** (flake A) |
| **rep1 → rep3** | 207 | 0/0 | **206/207** | **1** (flake B) | 188 identical, 12 differing (3 envelope + 8 volatile + **1 other**), 7 not-carried | 196 identical, **4 differing** (3 envelope + flake B) |

**Zero drift vs the r87 canonical receipt on the frozen bytes**: rep1
reproduces `be5b0222…` on all 207 tuples. The rep1→rep2 / rep1→rep3 mismatches
are exactly the two flakes below — no other row differs anywhere.

### 3.1 Envelope-cell matrix (all 5 cells PASS in every run)

`mode[k]` = the k-th whitelisted payload (order as in the frozen `CASES`
`signature` list) matched in the row's merged output. The tuple stores the full
payload list, so tuple identity holds regardless of observed mode.

| cell | rep1 | rep2 | rep3 | r87verifier2 | r87critic2 | r87foldcheck |
|---|---|---|---|---|---|---|
| `input_lattice_api_press` | mode[0] | mode[0] | mode[0] | mode[0] | mode[0] | mode[0] |
| `input_lattice_pre_frame` | mode[1] | mode[1] | mode[0] | mode[1] | mode[0] | mode[0] |
| `input_lattice_press_phys` | mode[1] | mode[0] | mode[0] | mode[0] | mode[0] | mode[0] |
| `input_lattice_release_edge` | mode[0] | mode[1] | mode[0] | mode[1] | mode[1] | mode[0] |
| `input_lattice_ui_ns` | mode[0] | mode[0] | mode[1] | mode[0] | mode[1] | mode[0] |

All 25 cells (5 × 5 runs) PASSed; tuple identity on the 5 cells is True in
every comparison. `api_press` showed only mode[0] in these 5 runs (the r87
critic's 27/30-under-load alt mode is the rare arm; consistent).

### 3.2 Declared-volatile class (raw stdout only)

8 rows, identical to the r81/r86/r87 declared class:
`crash_spontaneous_sigabrt` (ASLR `Load address:`),
`descendant_pipe_detached_control` / `descendant_pipe_forged_signature_release`
(godot_pid), `save_process_writer` / `save_process_reader` /
`save_process_missing` (pid + run path), `save_roundtrip` (run path),
`tween_flash` (transient float jitter; pin is a prefix). All are
normalized-identical except where a flake row or an envelope payload text
intervenes; the residual non-normalized diffs vs the canonical receipt are
exactly the 2 envelope payload texts (`press_phys`, `release_edge`).

---

## 4. Pre-existing flake A — `crash_spontaneous_sigabrt` 8 s crash-dump timeout (rep2)

**Evidence (rep2, load 2.89→3.02, concurrent seats live).** Row expected
`exit=-6` (SIGABRT); observed `actual_exit=None`, `error="TIMEOUT after 8
seconds"`. The captured output shows the crash **did** happen — `handle_crash:
Program crashed with signal 4`, `Dumping the backtrace.` — and then **stops at
`Load address: 560fe605b000`**; rep1's output for the same row continues with
the symbolized frame list (`[1] 7f05e923e6f0 (libc.so.6+3e6f0) …`). The
process was still inside the crash handler's backtrace dump when the harness's
8 s row budget expired and killed it.

**Cascade (pure consequence, same 3 rows as the r75 precedent).**
`probe_spontaneous_crash_classification` FAIL — its 4 discriminations are all
`true`, but the meta's conjunctive pass requires `sigabrt["verdict"]=="PASS"`
and `actual_exit==-6` (`sigabrt_exit=None` in the payload);
`probe_error_clause_surface` FAIL — `prior_meta_rows_stable_29_discriminations`
= false. Top-level battery FAIL. All other 204 rows PASS.

**Precedent and rate.** `reports/round-75/r75-baseline.md` §"crash_spontaneous_sigabrt
flake" documents the same row failing in the `-9` external-SIGKILL sub-mode,
cascading to the same two meta rows, with a clean identical-command rerun.
Historical scan of every receipt on disk: **774 receipts carry this row, exactly
1 was non-PASS** (the r75 receipt). rep2 is the 2nd ever observed non-PASS and
the first in the 8 s-timeout sub-mode. **This is rep-level host nondeterminism,
not a fixture/HEAD property** — the frozen bytes and harness sha were constant
across all reps and the tree stayed pure.

---

## 5. Pre-existing flake B — `input_lattice_phys_peer` alt mode (rep3, supplementary)

**Why rep3 exists.** Flake A left the non-recurrence question open (r75
precedent: flake → clean rerun). The one `probeParent` labrat grant returned no
execution capability, so this seat ran one supplementary rep on the same frozen
tree (same invocation; receipts `runs3/`). It did **not** reproduce flake A:
`crash_spontaneous_sigabrt` PASSed (`exit=-6`, backtrace frames present) — even
under heavy load. It instead surfaced a **second, distinct pre-existing flake**.

**Evidence (rep3, load 4.28→42.74 during the run).** `input_lattice_phys_peer`
exit 0, stderr 0 B, verdict FAIL only because the pinned signature did not
appear. The frozen pin (from `CASES`) says
`same_tick[0/0.00/0/0] ev_step_delta=0 cells=d-1{…} d+0{…} d+1{s1=px=1/1.00/1/0,s0=px=1/1.00/1/0} …`;
rep3 observed
`same_tick[0/0.00/0/0] ev_step_delta=2 cells=d-1{…0…} d+0{…0…} d+1{…0…} d+2{…0…} d+3{s1=px=1/1.00/1/0,…}`
— the press landed **two physics steps later** (rep1 and rep2 both observed
`ev_step_delta=0`). Single-row FAIL, no cascade.

**Class.** Interposed-physics-step nondeterminism — the same class the r87
boundary seat closed for `just_*` (selector = interposed-steps==0) and the r87
critic F1 found for `api_press` (release→idle→press gap admits an interposed
step). `phys_peer` is currently pinned single-mode; under load the alt mode is
reachable. **Historical rate: 15 receipts carry the row, 0 non-PASS before
today.** This is a candidate for envelope re-pin by the r88 author/boundary
(r87 `api_press` fold precedent) — **not fixed here** (baseline seat: document,
do not fix).

---

## 6. Host contention notes

- **During rep1**: `r88-boundary` was writing its probe scripts
  (`analyze_boundary.py` 18:08:21Z); `game-dev-3d-shokunin` r92-critic battery
  started 18:07:55Z. Load 3.85 → 2.80.
- **During rep2**: `r88-boundary/run_boundary.py` created 18:11:40Z; 3d
  r92-verifier battery started 18:09:56Z; both 3d seats' godot processes were
  still live at 18:15Z. Load 2.89 → 3.02. Flake A occurred here.
- **Between rep2 and rep3**: `r88_surfaces.gd` + `r88_spawnable.tscn` landed
  18:14:01Z (21 s after rep2 ended); an `r88_surfaces.gd --arm=mp_spawner`
  probe ran at ~18:15Z.
- **During rep3**: load 4.28 → **42.74** (mid-run 39.76) with the r88 seats
  active; flake B occurred here.
- **No lingering processes from this seat** after any rep
  (`pgrep godot | grep r88-baseline` = 0); the frozen tree received no writes.
- Attribution is bounded as in r75: both flakes are environment/load
  interactions (slow crash-dump path; interposed-step scheduling), not
  provable single-cause effects, and neither is a property of the frozen bytes.

---

## 7. Remaining risks / caveats

- **C1 — only rep1 is fully green.** Both subsequent reps flaked (different
  rows, both load-correlated). The 207-row tuple set in
  `freeze/godot-tuples-rep1.txt` is the frozen anchor; before/after comparisons
  for the r88 author must intersect on it and should record load. The live
  harness now carries the author's 8 new `r88_surfaces_*` rows (live scope 215,
  working-tree edit at 18:15:14Z) — those rows are outside this baseline.
- **C2 — crash-row 8 s budget.** The SIGABRT row's dump can exceed the 8 s row
  timeout under contention; historical rate 1/774, now 2/777 with the new
  sub-mode. Not a fixture defect; a host-budget interaction.
- **C3 — `phys_peer` single-mode pin is falsified under load** (`ev_step_delta`
  0 vs 2). Author/boundary decision; the r87 envelope pattern is the precedent.
- **C4 — meta rows are cascade-sensitive**: 2 of 7 meta rows can FAIL purely as
  a function of one seeded row's environment behavior (by design).
- **C5 — envelope mode distribution is not re-derived by 3 reps**; observed
  modes are recorded per rep in §3.1. `api_press` alt mode was not observed
  here (r87 recorded 27/30 mode0 under load).
- **C6 — volatile class** (§3.2) is raw-stdout-only by construction.
- **C7 — probe grant consumed without empirical yield**: the labrat seat had no
  shell tool; no independent rep exists. rep3 is this seat's own supplementary
  rep (disclosed), not an independent one.
- **C8 — freeze footprint**: `corpus/live/r88-baseline/tree/` is 1.6 GB of
  untracked scratch; prunable with `rm -rf corpus/live/r88-baseline/tree`.
- **C9 — `lsp` unavailable** (no device): no symbol-aware work was required;
  disclosed rather than silently hand-edited.
- **C10 — this seat's writes**: new untracked paths only —
  `corpus/live/r88-baseline/**` (tree, runs1–3, freeze, runner/comparator
  scripts, stdouts, env/timing receipts) and this report. **No tracked file was
  modified by this seat**: the single `M` entry in `git status --porcelain`
  (`corpus/fixtures/run_battery.py`) is the r88 author's 18:15:14Z working-tree
  edit disclosed in §0, not this seat's.

---

## 8. Verdict

The pre-round platform at frozen HEAD `d15c54d` is **green in the canonical
quiet condition**: rep1 = **207/207 PASS**, rc=0, stderr 0 B, and
**207/207 tuple byte-identity against the r87 landing receipt `be5b0222…`**
(fixture bytes identical to `7ef247c`; zero drift). The five documented
mode-envelope cells PASS in every rep with tuple identity intact; the 8
declared-volatile rows differ only in their declared tokens.

Two **pre-existing, load-sensitive flakes** were observed on the frozen tree and
documented with reps and receipts — `crash_spontaneous_sigabrt` 8 s crash-dump
timeout (rep2; 2nd ever non-PASS in 777 receipts, cascading to 2 meta rows) and
`input_lattice_phys_peer` `ev_step_delta=2` alt mode (supplementary rep3; first
ever non-PASS in 16 receipts). **Neither was fixed**; the frozen tree stayed
byte-pure (content rc=0, file-set 0 diff) and live HEAD stayed `d15c54d`
throughout. The r88 author's input set is
`corpus/live/r88-baseline/freeze/godot-tuples-rep1.txt` (sha256
`1dbf9deae1d8a7746767d0faa724fbc00a3284411eb69aad6d3bdb4dd1507777`, 207 rows,
all PASS) with receipt shas in `freeze/receipt-shas.txt`.
