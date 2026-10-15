# r89 verifier-2 — independent non-author verification of the FOLDED r89 bytes (`53a0be7`)

Seat `VERIFIER` (g2d lane r89, verifier-r2 — non-author on the fold) | host
**devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`,
`--headless`, 60 tps, GodotPhysics2D), Python 3.14.7, 32 cores. Target:
`53a0be77ea22d256eedb1c8b36e0d8491bbb235c` (*r89 fold: SP1+F5 deletions,
required_stderr pin closes crash-cause-blind hole*). Fold report:
`r89-fold.md`; pre-fold baselines `8cea888` (r89 author, 228 CASES) and
`ee20575` (r90 author / declared fold base HEAD, 240 CASES). Receipts:
`corpus/live/r89-verify2/` (`manifest.sha256` — 46 entries, all OK).

No `lsp` device / no GDScript or Python language server on this host
(unchanged lane state, same as every r89 seat); verification is fresh-process
execution + AST/byte analysis only. **Zero descendants spawned** — the
probeParent labrat licence was not needed; every check discharged against
fresh receipts on this seat. **No tracked writes beyond this report, no
commits.**

## Method — frozen tree

```
git archive 53a0be7 | tar -x -C corpus/live/r89-verify2/tree
```

- **Fileset**: `git ls-tree -r --name-only 53a0be7` (99,633) vs extracted
  `find -type f -o -type l` (99,633) — **0 diffs** (`freeze-fileset-diff.txt`
  empty).
- **Content**: `GIT_DIR=$PWD/.git GIT_WORK_TREE=tree git diff --quiet 53a0be7`
  → **rc=0**.
- **Frozen fixture shas** (`key-shas.txt`): `geo2d_lattice.gd` =
  `dcce4c749023…` (**530 lines**, `--check-only`-clean per fold),
  `run_battery.py` = `2679180a598a…`, `input89_edges.gd` = `601c223ed7a3…`,
  `rb_lattice.gd` = `10da2291295c…`, `rb_watch.gd` = `e349faa07154…`,
  `project.godot` = `8de8b3af9cc7…` — all match the fold report's declared
  pins byte-for-byte.

## Results per dispatch item

### 1. SP1 + F5 deletions — CONFIRMED (530-line probe, arms gone, pins identical)

`diff` of `8cea888:corpus/fixtures/geo2d_lattice.gd` (581 lines, sha
`9784716b5d69…`) vs frozen `dcce4c74…` (530 lines) is **exactly −51 lines**:

| hunk | content | lines |
|---|---|---|
| dispatch `:103–104` | `"bridge_hole": _arm_bridge_hole()` / `"bridge_hole2": _arm_bridge_hole2()` entries removed | −2 |
| `:383–429` | `_arm_bridge_hole()` + `_arm_bridge_hole2()` bodies incl. the falsified *"merge() of a contained square yields TWO contours"* comment | −47 |
| `:550,555` | SP1 dead accumulator `var names: PackedStringArray = []` + `names.append(...)` | −2 |

- `grep bridge_hole` on the frozen probe: **0 hits** (dispatch + bodies +
  comment all gone); the only `bridge_hole` token in `run_battery.py` is the
  provenance comment at `:422` documenting the deletion.
- Live fallback demonstration (`runs-probe/deleted_arm_fallback.out`):
  `godot --headless --path proj --script res://geo2d_lattice.gd --
  --arm=bridge_hole` → rc=0, emits `R89 bridge_hole sig=[8 methods]` +
  census PASS line — verbatim replays of the deleted arms land on the
  `_: _arm_census()` fallback exactly as the fold disclosed.
- `names` appears nowhere in the folded probe (accumulator gone).

**CASES pin comparison** (`scripts/cases_compare.py` → `cases-compare.json`,
AST `literal_eval` of every CASES tuple):

- r89 family (18 `geo2d_lattice_*` + 2 `input89_edges_*`): **20/20 tuples
  byte-identical** vs `8cea888` — none missing, none dropped, none mutated.
- r90 family (`r90_lattice_*`): **12/12 tuples byte-identical** vs `ee20575`
  (the commit that introduced them; `8cea888` predates the family).
- Whole battery: **all 240 CASES tuples identical `ee20575` → `53a0be7`** —
  the fold touched zero row bytes (`all_diff_rows_vs_ee20575: []`); CASES
  count 240 both sides. The pin mechanism is harness-side only, as claimed.

### 2. Full battery ×2 on the folded bytes — both 247/247, every r89 row PASS with the pin populated

Sequential runs from the frozen tree (`python3 run_battery.py --runs
corpus/live/r89-verify2/runs{1,2}`), under real foreign load (loadavg
51–83 across the window — sibling lanes' hogs; no extra hogs needed):

| rep | stamp | verdict | r89 rows | r90 rows | stderr |
|---|---|---|---|---|---|
| runs1 | `20261015T223032116353Z` | **PASS 247/247** | 20/20 | 12/12 | 0 B |
| runs2 | `20261015T223404791057Z` | **PASS 247/247** | 20/20 | 12/12 | 0 B |

verdicts.json sha: run1 `45508550341f…`, run2 `eb53e3f9fb5a…`
(`check-run{1,2}.json`, `ok:true` both).

- **`geo2d_lattice_lineempty`**: `actual_exit=-6`, `verdict=PASS`, and
  `record["required_stderr"]` = `["Clipper2Lib::Point<double>",
  "Assertion '__n < this->size()' failed."]` — **populated in both runs**.
  Merged record shows the R89 sig line and the libstdc++
  `stl_vector.h:1253 … operator[] … Clipper2Lib::Point<double> … Assertion
  '__n < this->size()' failed.` text; per-stream attribution proven in §3.
  No other r89/r90 row carries a stray `required_stderr` (`[]` everywhere
  else).
- **Emitted-line byte-identity**: for all 32 r89+r90 rows in both runs the
  emitted output line is **byte-equal to a pinned CASES payload** (exact
  equality, not substring) — `sig_byte_check` all `exact_line:true`.
  `input89_edges_exact` emitted envelope payload[1] (`…inex=false]`,
  loaded mode) in both runs — consistent with loadavg>50 and the documented
  load-bimodal `just_after_flush` token; it remains one of the two
  whitelisted payloads, byte-exact.
- **Gates**: `phys2d/r87/r88/r89/r90_expected_errors_all_matched` all `true`
  in both runs; `dead_entry_count=0`, `dead_entries=[]`; all 7 meta probes
  PASS (`probe_save_independent_process`, spontaneous-crash, pipe-EOF,
  signature-spoof, while-live, error-spoof, error-clause-surface).

**Tuple + normalized-output compare vs pre-fold canonical greens**
(`corpus/live/r87-baseline/compare.py godot`, refs = r90-author green runs
`runs9/20261015T212551992799Z` and `runs12/20261015T220233737605Z` — the
`ee20575`-era 247/247 receipts):

| mine | ref | common | tuple_mismatches | OUT-DIFFs (normalized) |
|---|---|---|---|---|
| run1 | runs9-green | 247 | **0** | 6 — input_lattice envelope modes ×3, `mp_loopback` uids, `release` held_moves 4↔3, `route_toggle` frames 15↔14 |
| run1 | runs12-green | 247 | **0** | 3 — `mp_loopback` uids, `release` held_moves, `tween_flash` frames_observed |
| run2 | runs9-green | 247 | **0** | 4 — envelope modes ×2, `mp_loopback` uids, `route_toggle` frames |
| run2 | runs12-green | 247 | **0** | 3 — envelope mode, `mp_loopback` uids, `tween_flash` frames |
| run2 | run1 (mine) | 247 | **0** | 3 — envelope mode, `mp_loopback` uids, `release` held_moves |

Every diff is a documented volatile class (envelope payloads, ENet uids,
`frames=`/timing jitter, `transient_modulate` float). **Zero normalized
output diffs and zero tuple mismatches on any `geo2d_lattice_*`,
`input89_*`, or `r90_*` row** — folded rows are byte-identical to the
pre-fold pins and to pre-fold fresh output. (`polyendpoly`'s GDScript
backtrace `:577/:578` → `:526/:527` shift declared by the fold is absorbed
by the established `.<ext>:<N>` rule; verdict-inert.)

### 3. F1 crash-cause blindness — closed; forges flip FAIL (independent re-derivation)

`scripts/fp_pin_verify.py` AST-extracts **both** `classify_process` **and**
the `required_stderr` dict literal from the *frozen* `run_battery.py` (no
hardcoded copies — classifier segment sha `749fa0607e77…`, identical to the
fold's recorded `749fa060…`), then launches each probe under the battery
launch shape with streams separate and applies the production predicate
twice (bare merged-blob classify, and pinned = classify ∧ fragments⊆stderr
∧ sig⊆stdout). Receipts `runs-probe/` + `fp_pin_verify.json` (`ok:true`):

| probe | bare classify (pre-fold semantics) | pinned classify (fold semantics) | evidence |
|---|---|---|---|
| folded `geo2d_lattice.gd --arm=lineempty` (real Clipper2 abort) | PASS | **PASS** | rc −6; sig on stdout; both fragments on stderr (334 B) |
| `fp_wrongcause.gd` (sig on stdout + foreign INF-vertex abort) | PASS (the demonstrated false positive) | **FAIL** | 0 B stderr → Clipper2 fragments absent |
| `fp_stderr_sig.gd` (sig on stderr only + same wrong-cause abort) | PASS | **FAIL** | sig not stdout-anchored |

`DISCRIMINATION PASS`. The row now binds the −6 to the Clipper2
empty-polyline assert class and anchors the signature to stdout — both
demonstrated false-positive shapes now fail loudly. Forge probe bytes
copied verbatim from `corpus/live/r89-critic/probes/` (sha `164ec480…` /
`19ad775d…`, byte-identical to the fold's copies).

### 4. r90 rows — untouched

12/12 PASS in both runs; CASES tuples byte-identical to `ee20575` (§1);
emitted PASS lines byte-exact vs pins; zero tuple/output diffs vs the
`ee20575`-era green runs (§2). The r90 gate `r90_expected_errors_all_matched`
= `true` in both runs.

## Verdict

**VERIFIED** — the committed `53a0be7` fold bytes do exactly what the fold
report claims: −51-line SP1+F5 deletion on a 530-line probe with arms
provably gone (dispatch fallback demonstrated live), a populated
`required_stderr` pin that keeps the real `lineempty` abort PASS while
flipping both critic forges to FAIL, 20/20 r89 and 12/12 r90 rows green
across two full 247-row batteries under load, and verdict tuples identical
to both pre-fold canonical green runs with only documented volatile output
classes differing.

## Remaining risks (inherited, disclosed by the fold — re-confirmed here)

- The `required_stderr` fragments are **toolchain-pinned** (libstdc++
  `__n < this->size()` + `Clipper2Lib::Point<double>`): a libstdc++ bump or
  a fixed empty-polyline path flips the row to loud FAIL — intended.
- Pin covers `lineempty` only; `crash_spontaneous_sigabrt` /
  `crash_self_sigkill` keep the merged-blob convention (no stderr assert
  exists there to pin — same shape as before).
- Verbatim replays of `bridge_hole`/`bridge_hole2` degrade to the census
  fallback (demonstrated); scout `run_cells.sh` history stays valid.
- The single pre-existing flake classes (`overlap`, `negative_transition`,
  `audio_bus_route_invalid_control`, census cascade) did **not** fire in
  either of my runs; nothing new flaked on r89/r90 rows.

- **Foreign uncommitted worktree state observed** (concurrent sibling lane):
  `M corpus/fixtures/run_battery.py` (+~67-line r91 `nav_lattice` block) and
  `M corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` — **not this
  seat's, untouched**. Every verification artifact here was produced on the
  `git archive` frozen tree, so the worktree dirt cannot contaminate any
  result above; it only explains the ambient loadavg.

## Blockers

**None.** Commit/integration decision remains with the operator.

## Evidence index (`corpus/live/r89-verify2/`)

| artefact | path |
|---|---|
| frozen tree (99,633 files, byte-identical to `53a0be7`) | `tree/` + `freeze-lstree.txt`, `freeze-extracted.txt`, `freeze-fileset-diff.txt` (0 lines) |
| battery reps | `runs1/20261015T223032116353Z/verdicts.json`, `runs2/20261015T223404791057Z/verdicts.json`, `battery-run{1,2}.{stdout,stderr}` (stderr 0 B) |
| per-run checks | `check-run1.json`, `check-run2.json` (`ok:true`) |
| green-run + self compares | `compare-run1-vs-greens.txt`, `compare-run2-vs-greens.txt`, `compare-run2-vs-run1.txt` |
| CASES pin compare | `scripts/cases_compare.py` → `cases-compare.json` (`ok:true`) |
| F1 forge discrimination | `scripts/fp_pin_verify.py`, `runs-probe/fp_pin_verify.json` (`ok:true`), `runs-probe/{folded_lineempty,fp_wrongcause,fp_stderr_sig}.{out,err,rc}` |
| deleted-arm fallback | `runs-probe/deleted_arm_fallback.{out,err}` |
| probe project | `proj/` (frozen `geo2d_lattice.gd` + `project.godot` + forge copies), `probes/` |
| byte/sha state | `key-shas.txt`, `uptime.txt`, `manifest.sha256` (46 entries, `sha256sum -c` all OK) |

Seat output complete.
