# r91 author — Navigation2D lattice landed (11 rows)

Seat `AUTHOR` (g2d lane r91) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.
Work is worktree-only — **nothing committed**. No `lsp` device / no GDScript
server on this host (same as r89/r90 author); all semantic validation is
fresh-process execution + runtime introspection + engine diagnostics.

Scope per dispatch: land the scout Navigation2D probe into
`corpus/fixtures/` with **only boundary-surviving claims**, scheduler/rate
dependence expressed as `iteration_id`/prefix envelopes (never universal
frame counts), and the teardown-crash negative control armed.

## Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/nav_lattice.gd` | `088843399ce37eb272dfb8cbf7e2a115f1b9af01a44859ea05610297875e3796` (882 lines) | folded variant of the frozen scout probe `corpus/live/r91-scout/probes/nav_lattice.gd` (scout sha `efb496e5fe08e6679c19c5f2a7a1eef86098f97f4a6407edab10451859afe5f9`, 676 lines) — boundary folds below |

`project.godot` untouched.

## Boundary folds applied (all measured in `corpus/live/r91-boundary/`)

1. **No scheduler field inside any pin.** `settle=`, `iter=`, `ladder=`,
   `first_reach=`, `first_reach_sync=`, `walk_steps=`, `reached_at=`,
   `first_reachable=`, `iter_b=`, `link_iter=`, `gate=`, `chg_iter_same=`,
   `chg_iter_settled=` moved to trailing diagnostic tails. Measured
   falsifiers: 60-tps sync tails 8–10 frames under ambient load, 43 frames
   at `--fixed-fps 30`, no sync within 60 frames at `--fixed-fps 120`; the
   scout's own ladder was not constant. `print` order in every arm is
   *pinned block first, tail last*.
2. **Sync gate, not sync guess.** `_await_sync()` polls
   `map_get_iteration_id(map) >= 2 AND reach` (necessary + sufficient:
   boundary attack 1 — no reach before iter>=2 in 61/61 gate runs) with
   `SYNC_BOUND := 48`. Exhaustion calls `_stale()`: prints
   `STALE nav_lattice <arm>` (satisfies no signature) + `_exit_code = 2`.
   A sync stall fails loudly instead of printing a PASS-shaped payload off
   an unsynced map (boundary §2.1: the scout's 24-frame bound silently
   proceeded stale in 8 bake runs under fixed-fps).
3. **Same-frame OLD-answer reads unpinned.** `dis_same` (sync, region)
   and `fwd_disabled_same` (link) are tails — invalidation can land in
   frame 0 (1/5 at 60 tps under load; boundary §3). `chg_same=false` stays
   pinned: the *new* answer never appears same-frame (100% of 60-tps
   runs).
4. **fin-before-reached query order.** The agent arm reads
   `is_navigation_finished()` before `is_target_reached()` every frame
   (boundary §6: the scout's `reached_at=-1` was a query-order artifact —
   `is_target_reached` can be stale until `is_navigation_finished`
   refreshes the state). `reached_at`/`walk_steps`/`first_reachable`
   remain diagnostics.
5. **Avoidance invariants probe-side.** The pin carries
   `sum_bound_ok=true dirs_ok=true` (asserted in-fixture: exactly 5 paired
   measured frames, each `|a|+|b| <= 20.001`, `a.x>0`, `b.x<0` — the ORCA
   bound, never above 20.0000 in 100 boundary samples). The
   process-dependent split digits (`seq_*`, `vel_*`, `sum_max`) are tails.
6. **Teardown-crash negative control armed.** `teardown_crash` exits with
   a live avoidance callback → deterministic double-free at server
   teardown: `NAV_LATTICE_TEARDOWN_CRASH armed=live_cb has_cb=true` on
   stdout, `double free or corruption (!prev)` on stderr, subprocess
   returncode `-6` (51/51 boundary + 9/9 scout-discovery repro).
   `teardown_clean` is the discipline control (clear callback + ≥1 frame +
   free → exit 0, `survived=true has_cb=false`); a cleared-callback leak
   also exits clean — the crash requires a **live** callback.

Also landed: the scout's stable structural claims verbatim —
`NavigationAgent2D extends Node` (no `position`), hand-built polygon lists
do not connect across a shared edge while two regions do, collider-only
source geometry bakes to an empty navmesh silently
(`collider_only_polys=0`), `map_get_random_point` unpinnable.

## run_battery.py changes (insertion-only, +88 lines, `f5725ca4…`)

1. **CASES 240 → 251 tuples** (result rows 247 → **258** incl. meta):
   11 `nav_lattice_*` rows inserted after `r90_lattice_lag`, ahead of the
   crash/descendant tail — `descendant_pipe_detached_control`'s
   sleep-8 gap stays adjacent to the meta probes.
2. **`expected_errors` += 2 cases** (exact-match, per-line):
   - `nav_lattice_sync` →
     `ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.`
     (pre-sync `map_get_closest_point`, `nav_map_2d.cpp:165`; fires exactly
     once per run — `map_get_path`/`map_get_regions`/`map_get_iteration_id`
     pre-sync are silent).
   - `nav_lattice_bake` →
     `ERROR: The root node needs to be inside the SceneTree.`
     (orphan `bake_navigation_polygon` → `parse_source_geometry_data`,
     `godot_navigation_server_2d.cpp:115`). The
     `make_polygons_from_outlines` deprecation WARNING carries no
     `ERROR:` substring — needs no entry.
3. **`required_stderr` += 1 case**: `nav_lattice_teardown_crash` →
   `('double free or corruption',)` — binds the `rc=-6` to the glibc
   heap-corruption abort (not the signal class alone); the `(!prev)` tail
   deliberately unpinned. Same shape as `geo2d_lattice_lineempty`; the
   signature is additionally anchored to stdout.
4. **Floor gate extended**: `r91_expected_errors_all_matched` covering
   `case.startswith("nav_lattice_")` — same named-by-round /
   covers-round-prefixes shape as r87–r90. A dead r91 allowlist entry
   fails `probe_error_clause_surface` loudly.

## New-cell inventory (11 rows)

| case | surface | pin shape |
|---|---|---|
| `nav_lattice_census` | method/enum/default census | `srv_methods=199 poly_methods=134`, `srv_info`/`pgt`/`sgm`/`sp`/`pp`/`md`/`alg` enum values, `poly_defaults`/`reg_defaults`/`agent_defaults`/`qp_defaults` — build-hash constants (host-conditional class, per existing pins) |
| `nav_lattice_path` | two-region L + gap geometry | exact vertex lists for `diag`/`diag_raw`/`same`/`out_start`/`out_target`/`gap`, closest-point + owner-RID checks, `gap20` margin-bridge path + `gap20_margin=20.0000` |
| `nav_lattice_query` | `query_path` parameter lattice | `postproc` pp0/pp1/pp2 vertex lists, `metadata` flag lattice (`md0/1/2/4/7` rids/types/owners counts), `maxlen`/`maxrad`/`maxdist`/`maxpolys`/`simplify` truncation geometry, `layers0=[]`, `length=282.8427` |
| `nav_lattice_sync` | map-sync law + live mutation | `pre_iter=0 pre_regions=0 pre_path=[] pre_closest=(0,0)` (pre-sync state), map defaults, `chg_same=false chg_settled=true dis_settled=false`; ladder/gate/iter/dis_same in tail |
| `nav_lattice_region` | region steering | full vertex lists for `base`/`top_cost1`/`bot_cost1`/`enter500`/`l1`/`l2`/`l3`/`dis_settled`/`reenabled`/`swapped`/`restored` + `counts=` (4 regs, costs, enabled flags) |
| `nav_lattice_agent` | NavigationAgent2D node walk | `settled=` quintuple, `fin=true reached=true reachable=true`, `dist=2.2741`, `final_pos`/`final_target`, `path` vertex list, `desired=4.0 target_desired=8.0`; walk counters in tail |
| `nav_lattice_avoid` | RVO avoidance invariants | `pa`/`pb` spawn, `warm_n_a=16 n_a=21 n_b=21` receipt counts, `sum_bound_ok=true dirs_ok=true`, `has_cb_a=true`, radii/speed/obstacle fields; seq/vel payloads in tail |
| `nav_lattice_bake` | outline bake + modern bake | `outline_polys=4 outline_verts=8`, hole-detour paths, `parse_obs=1 parse_trav=0`, `baked_polys=4`, `collider_only_polys=0` (silent-empty receipt), route-B `through`/`around`/`outside` paths |
| `nav_lattice_link` | link traversal | `bidir_default/en_default`, fwd/rev vertex lists, `fwd_disabled_settled` truncation, `cost300` still-traversed path, `layer1`/`layer2` filtering, link property reads |
| `nav_lattice_teardown_crash` | negative control | exit `-6` + stdout marker + stderr `double free or corruption` (required_stderr) |
| `nav_lattice_teardown_clean` | discipline control | `survived=true has_cb=false`, exit 0 |

## Fresh-arm evidence (pre-battery)

Every arm ×3 fresh in the battery's exact launch shape
(`godot --headless --path corpus/fixtures --script res://nav_lattice.gd --
--arm=<a>` via `subprocess.run`, no shell wrapper; `teardown_crash`
verified through Python's `-6` convention):
`corpus/live/r91-author/fresh-reps/` — 33 receipts (`out`/`err`/`rc`).

- **All 11 signatures machine-verified as substrings of all 3 reps** of
  each arm (script, not eyeball) — rep receipts diff only inside declared
  diagnostic tails (`settle`, `iter`, `gate`, `ladder`, `seq_a`/`seq_b`,
  `vel_a`/`vel_b`, `sum_max`, `walk_steps`, `reached_at`, `dis_same`,
  `fwd_disabled_same`).
- `sync`/`bake` stderr: exactly one whitelisted `ERROR:` line each across
  all reps — allowlist entries are **load-bearing** (production
  `classify_process` AST-extracted: `bare=False` for all 6
  sync+bake receipts, `True` with the entry; `teardown_clean`/`census`
  `bare=True`).
- `teardown_crash` ×3: `rc=-6`, stdout marker present,
  `double free or corruption (!prev)` on stderr — `required_stderr` and
  stdout-anchored signature both satisfied.
- `region` rep-to-rep diff confined to `settle=` tail; `avoid` diffs
  confined to `seq_*`/`vel_*`/`sum_max` tails; `agent` tail counters
  (`walk_steps=28 reached_at=28 first_reachable=5`) stable here but
  deliberately unpinned.
- Bake arm additionally emits the `make_polygons_from_outlines`
  deprecation WARNING (no `ERROR:` token — needs no allowlist).

## Labrat advisory (agent `6594ae95`, read-only, no edits)

Hypothesis — *signatures are true substrings of fresh output in the
battery launch shape; all scheduler fields strictly post-pin*: **CONSISTENT
as far as statically verifiable**. Field-by-field source check: every
CASES signature is a contiguous prefix ending at the declared token; all
named scheduler/race fields appear only after the pin; `_await_sync`
bound/`STALE`+exit-2 path verified; exactly-once PASS-line invariant holds
(13 print sites, 1 per arm + STALE + unknown-arm fallback).
`expected_errors` entries confirmed load-bearing against committed
boundary captures; `teardown_crash` stderr shape confirmed (rc=−6
convention, `double free or corruption`, `(!prev)` unpinned).
Caveats flagged: no committed load-mode rep for `link`
(`fwd_disabled_settled` rests on scout receipts — weakest row), agent
`dist/final_pos` are scheduler-adjacent (stability rests on sync gating,
stall now fails loud as STALE rather than mis-PASS), census values are
build-hash constants. Its exec gap (no process tool) is covered by my
fresh-rep + full-battery evidence above/below.

## Full battery — final bytes

| run | rows | verdict |
|---|---|---|
| author rep1 `corpus/live/r91-author/runs1/20261015T223815564642Z` | 258 | **PASS** — 258/258, `r91_expected_errors_all_matched=true`, nav 11/11 |
| author rep2 `corpus/live/r91-author/runs2/20261015T224213073214Z` | 258 | **PASS** — 258/258, `r91_expected_errors_all_matched=true`, nav 11/11 |

**Two green runs (258/258) on the final bytes.** Both census rows
(`nav_lattice_sync` `matched_lines=1`, `nav_lattice_bake`
`matched_lines=1`) bare-reject / allowlist-pass; `teardown_crash` row
records `actual_exit=-6` + `required_stderr` match in both runs.
`project.godot` scan counts in `export_readiness` unaffected (fixture
added under `corpus/fixtures/` is part of the project copy — the export
verdict stayed PASS both runs).

Zero flakes observed in either run — including the documented volatile
classes (`overlap`, `transition`, `negative_transition`,
`audio_playback`, `audio_bus_route`, `input_lattice_press_phys`) that
failed intermittently during r90's green hunt under similar load.

## Host notes / remaining risks

- Host ran under heavy foreign oversubscription throughout
  (load ~51–65 during authoring, ~52–118 during boundary measurement —
  none of it mine). All nav pins are geometry/state, not timing, by
  construction; the only observed per-rep variance lives in declared
  tails. If a stall ever exhausts `SYNC_BOUND=48` the arm emits
  `STALE nav_lattice <arm>` + exit 2 — a loud failure, not a mis-PASS.
- `srv_methods=199`, `poly_methods=134`, enum arrays, and default values
  are build-version tokens — they flip loudly on an engine bump
  (intended, same class as existing census pins).
- 4-dp vertex pins ride the engine's navmesh vertex order — stable on
  this build across all reps; a solver/partition change moves last
  decimals (same caveat class as r89/r90 geometry pins).
- `link` row: no committed load-mode coverage beyond scout receipts +
  my 5 fresh reps (3 pre-battery + 2 battery) — weakest-evidenced row
  (labrat flag #2), mitigated by its pin ending at deterministic state
  fields with all timing in the tail.
- `nav_lattice_teardown_clean` queries `agent_has_avoidance_callback` on
  the freed RID — measured silent (`has_cb=false`, `err_bytes=0` ×3
  fresh reps + 2 battery runs; labrat confirmed against boundary cells).
  If a future engine build makes freed-RID reads loud, the fix is to
  query before `free_rid` (value already captured) — a fixture edit, not
  a battery change.
- Deliberately un-authored boundary vectors: universal frame counts,
  `--fixed-fps` runs, same-frame old-answer reads, avoidance split
  digits, `reached_at`/`walk_steps` cadence — none sit inside any pin.
- No commit. Worktree: `M corpus/fixtures/run_battery.py` (+88,
  insertion-only), `?? corpus/fixtures/nav_lattice.gd`,
  `?? corpus/live/r91-author/`, this report.

## Evidence index

`corpus/live/r91-author/` — `manifest.sha256` covers all:

| artefact | path |
|---|---|
| fresh-arm receipts (11 arms × 3 reps, out/err/rc) | `fresh-reps/` |
| battery run 1 (green) | `runs1/20261015T223815564642Z/verdicts.json` |
| battery run 2 (green) | `runs2/20261015T224213073214Z/verdicts.json` |
| source reports | `reports/round-91/r91-scout.md`, `reports/round-91/r91-boundary.md` |
