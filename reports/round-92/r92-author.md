# r92 author — TileMapLayer/TileSet lattice landed (14 rows)

Seat `AUTHOR` (g2d lane r92) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.
Work is worktree-only — **nothing committed**. No `lsp` device / no GDScript
server on this host (same as r89–r91 authors); all semantic validation is
fresh-process execution + runtime introspection + engine diagnostics.

Scope per dispatch: land the scout TileMapLayer probe into
`corpus/fixtures/` with **only boundary-surviving claims** — nav reads carry
envelopes, never fixed frames; the SIGSEGV hazard row carries
`required_stderr` fragments; tombstone encoding pinned verbatim.
`run_battery.py` touched **insertion-only** (`+161, -0`).

## Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/tilemap_lattice.gd` | `a699138945ec7c1c1e6c97b6bf052d0941596610ad4cb9d08d184c07409d3dfb` (929 lines) | **byte-copy** of the frozen r92-scout probe `corpus/live/r92-scout/probes/tilemap_lattice.gd` — no fixture folds; every boundary fold lands row-side in the signatures |

`project.godot` untouched.

## Boundary folds applied (r92-boundary `7a45a60`, all measured)

1. **`r92_tilemap_nav` is a 2-payload envelope on `regions_f1`.** The cold
   cell-write's navigation-region registration flushes through the
   idle/process pass, not the physics step — `regions_f1=1` at
   idle:physics ≤ 2 (the production harness: default scheduler + load +
   the 120-tps project; 93/93 committed receipts incl. boundary's 65
   quiet/load matrix reps) and `regions_f1=0` at ratio ≥ 2.5
   (`--fixed-fps` ≥ 150 at 60 tps, ff480 at 120 tps; ff150 0/10, ff600
   0/10 — boundary §4.1). payload[0] is the production/pinned mode. The
   settled form `regions_f2=1` is single-valued across **all 126 boundary
   nav receipts** and stays pinned in **both** payloads — the envelope
   moves the frame-counted read, never the law. This is the task's
   "envelopes, never fixed frames" applied to the one falsified field.
2. **No `update_internals()`/`map_force_update()` claim on the nav path.**
   Boundary F7 refuted both as synchronous nav levers (`n_force=0
   n_upd=0`; one `await process_frame` flushes, `n_proc1=1`). The
   physics-path pins stay in `r92_tilemap_timing` where the synchronous
   apply was measured (`update_set_same_frame=hit`,
   `update_erase_same_frame=null` quartets).
3. **`r92_tilemap_nullts_crash` arms the null-TileSet hazard** (scout
   §4.7/§5.1): null `tile_set` + `set_cell` + `get_cell_tile_data` →
   signal 11, then the engine crash handler's `abort()` exits the
   process **`-6`** (SIGABRT) — measured 3/3 fresh reps in the battery
   launch shape (`corpus/live/r92-author/fresh-reps/nullts.*`). **Author
   correction to the scout's label:** the scout reported "rc=134
   SIGSEGV" — 134 = 128+6 is the same SIGABRT termination through its
   bash `timeout` wrapper; the Python `subprocess` returncode is `-6`.
   The signature is the last pre-crash diagnostic
   (`R92 nullts about_to_call_tile_data=1`) on **stdout** — the PASS line
   is never reached — and `required_stderr` pins the signal-11
   crash-handler header (`handle_crash: Program crashed with signal 11`)
   plus the `_nullts` backtrace site (`res://tilemap_lattice.gd:927`), so
   the row is bound to this null-deref, not the signal class alone —
   same shape as `geo2d_lattice_lineempty`/`nav_lattice_teardown_crash`.
   ASLR'd addresses and the C++ backtrace are deliberately unpinned.
4. **Tombstone encoding pinned verbatim** (scout §4.4): `tile_map_data` =
   2-byte header + 12-byte little-endian records; `erase_cell`
   tombstones in place (`0xFF` tail at unchanged length), `clear()`
   tombstones every record — the buffer is a high-water mark, never a
   live-cell count (`tomb_erase_bytes`, `tomb_clear_*`, `stride=12` all
   inside the signature).
5. The other 12 rows carry **no envelope** — they survived ratio
   1/60…15, loadavg 145, the 120-tps project, and the probe's watchdog
   byte-identical (boundary verdict table rows 4–5, F1–F3 refuted).

## run_battery.py changes (insertion-only, +161 lines, `5e518281…`)

1. **CASES 251 → 265 tuples** (result rows 258 → **272** incl. meta):
   14 `r92_tilemap_*` rows inserted after `nav_lattice_teardown_clean`,
   ahead of the crash/descendant tail —
   `descendant_pipe_detached_control`'s sleep-8 gap stays adjacent to the
   meta probes. `git diff` shows **161 insertions, 0 deletions**.
2. **`expected_errors` += 9 cases** (exact-match, per-line): the nine
   error-emitting arms' documented refusal lines, verbatim from scout
   §6.1 — `atlas` (2), `cells` (2), `custom` (3), `terrain` (1),
   `pattern` (1), `encoding` (2), `fixinvalid` (3), `srcids` (3),
   `physics` (1). Repeated identical lines are covered by one exact
   entry (same as `geo2d_lattice_polyendpoly`). `census`/`timing`/
   `quadrant`/`nav` emit no `ERROR:` line and carry no entry; nav's only
   stderr is the `make_polygons_from_outlines` deprecation WARNING (no
   `ERROR:` substring — classifier-inert).
3. **`required_stderr` += 1 case**: `r92_tilemap_nullts_crash` → the two
   fragments above; signature additionally anchored to stdout.
4. **Floor gate extended**: `r92_expected_errors_all_matched` covering
   `case.startswith("r92_")` — same named-by-round /
   covers-round-prefixes shape as r87–r91. A dead r92 allowlist entry
   fails `probe_error_clause_surface` loudly.

## New-cell inventory (14 rows)

| case | surface | pin shape |
|---|---|---|
| `r92_tilemap_census` | class/property/default census | layer/TileSet/atlas defaults, `layer_props=n16[…]`, `layer_no_collision_priority=1`, terrain/tileshape/neighbor enum orders, `invalid_source=-1`, engine method counts |
| `r92_tilemap_atlas` | atlas source + alternative tiles | `sid_first=0`, idempotent-refusal `tiles_after_dup=2`, `alt_id=1` distinct TileData, `next_source_id=1` (lowest-free-slot law), `tex_region` |
| `r92_tilemap_cells` | cell lattice | empty sentinel `-1/(-1,-1)/-1/null`, same-frame data visibility, poison cells stored verbatim (`bad_src_readback=42`), map/local mapping, 8-of-16 neighbor law (refusals return input cell), empty-cell flip reads `1/1/1` |
| `r92_tilemap_custom` | custom data layers | type-advisory wrong-type write verbatim, per-type defaults, loud unregistered-name refusals, `duplicate(true)` layer survival + distinct TileData |
| `r92_tilemap_terrain` | terrain sets + placement | `-1` defaults, `set_cells_terrain_connect` silently drops non-carrying cells (`n2` of 3), loud OOB refusals place `n0[]` |
| `r92_tilemap_pattern` | TileMapPattern | bounding-box `get_pattern`, sparse holes, `set_pattern` offset + cross-layer, `map_pattern` pure translation, empty-pattern `(0,0)` |
| `r92_tilemap_encoding` | `tile_map_data` bytes | header + 12-Byte records verbatim, `stride=12`, in-place tombstones for erase/clear, array==bytes identity, destructive malformed-data refusals |
| `r92_tilemap_fixinvalid` | invalid-tile repair | `fix_invalid_tiles` deletes poison cells, removed-source cells persist-until-repaired |
| `r92_tilemap_srcids` | source-id allocation | lowest-free-slot law, `set_source_id` move, three `-1` refusal paths |
| `r92_tilemap_physics` | per-tile collision + quadrant levers | lever quartets (`_same_frame`/`_f1`), collider-is-layer identity (`travel=0.0000,1.9531` 4-dp float), `has_body_rid` measured negative |
| `r92_tilemap_timing` | one-physics-step law | `set_cell`/`erase_cell`/transform/`collision_enabled`/`notify_*` deferral quartets; `update_internals()` the only synchronous lever |
| `r92_tilemap_quadrant` | physics quadrant control | partitioning-not-correctness knob: 4 boundary-straddling cells hit under size 16 and 2 |
| `r92_tilemap_nav` | nav region registration | **envelope** on `regions_f1` (1@ratio≤2 / 0@≥2.5); `regions_f2=1` + disable/re-enable/erase lever trio pinned in both payloads |
| `r92_tilemap_nullts_crash` | SIGSEGV negative control | exit `-6` + stdout diagnostic + `required_stderr` pair |

## Fresh-arm evidence (pre-battery)

Every arm ×3 fresh in the battery's exact launch shape (`godot
--headless --path <scratch-copy-of-fixtures> --script
res://tilemap_lattice.gd -- --arm=<a>` via `subprocess.run`, no shell
wrapper): `corpus/live/r92-author/fresh-reps/` — 42 receipts
(`out`/`err`/`rc`).

- **All 13 PASS-arm rows classify OK ×3 through the production
  `classify_process`** (AST-extracted, segment sha `749fa0607e7707e6` —
  the same segment r89/r90/r91/r92 pinned), replicating `execute()`'s
  full path (rc + envelope-aware signature + allowlist + required_stderr
  + SCRIPT/Parse clauses); `verify_author.py` reports `fails=0`.
- **stdout AND stderr byte-identical across all 3 reps** for every PASS
  arm (13/13); nullts stdout identical ×3, stderr differs only in
  ASLR'd addresses (unpinned by design).
- All 9 allowlists **load-bearing** (`bare=False` on all 27 receipts —
  without the entry, classification fails).
- `nullts` ×3: `rc=-6`, stdout signature present, both stderr fragments
  present — required_stderr + stdout-anchor both satisfied.
- `nav` rep PASS lines carry `regions_f1=1` (payload[0], the production
  mode).

## Labrat advisory (agent `6d41d70c`, read-only, no edits)

Hypothesis — *the 14 rows exactly cover the committed measurement
corpus (canonical sigs, nav envelope exhaustiveness, allowlist
load-bearing, crash-row pins)*: **CONFIRMED** on all four clauses.
51/51 scout canonical + 22/22 loadtest/tps120 + 39/39 author-fresh
outs match their signatures; the nav envelope partitions **all 139**
committed nav-script receipts — payload[0]=93 (every receipt at
idle:physics ≤ 2), payload[1]=46 (every receipt ≥ 2.5), **neither=0**;
all 9 allowlists verbatim-matched in every rep, no dead entries, no
uncovered `ERROR:` line; nullts signature-on-stdout + both
fragments-on-stderr + `rc=-6` ×3. Caveats flagged (informational):
`corpus/live/**/runs/` trees are gitignored regenerable scratch;
scout's `134` vs battery's `-6` is the same termination under two
encodings; foreign-probe nav receipts (`r92b_*`) match neither payload
— out of the row's evidence domain by design.

## Full battery — final bytes

| run | rows | verdict |
|---|---|---|
| `runs4/20261016T000237277486Z` | 272 | **PASS** — 272/272, `r92_expected_errors_all_matched=true`, tilemap 14/14, error-clause meta all discriminations |
| `runs5/20261016T000655453477Z` | 272 | **PASS** — 272/272, `r92_expected_errors_all_matched=true`, tilemap 14/14 |

**Two green runs (272/272) on the final bytes.** Both nav rows matched
payload[0] (`regions_f1=1`) — the production scheduler regime — and the
nullts crash row recorded `actual_exit=-6` with both `required_stderr`
fragments in both runs.

Interim runs (`runs1`–`runs3`) each failed only on the **documented
volatile classes** — `negative_transition` (×3: `get_instance_id` on a
null `current_scene`, the known scene-install race), `transition` (×2),
`overlap`, `audio_playback`, `audio_bus_route_invalid_control` — the
same classes r91's author report names under this host's foreign
oversubscription (loadavg 68–86, 48 foreign `yes` hogs throughout). The
only meta knock-on was `census_bare_classifier_consistent`, which
follows `negative_transition`'s dead allowlist entries when the fixture
dies early — a flake consequence, not a row defect. No r92 row flaked
in any of the 5 runs (14/14 PASS ×5).

## Host notes / remaining risks

- Host ran under heavy foreign oversubscription (loadavg ~68–86, 48
  `yes` hogs — none mine). All 14 signatures are byte-stability-verified
  state/encoding/lever reads; the one frame-counted field
  (`regions_f1`) carries the measured envelope.
- `class_method_counts`, enum orders, and `srv_methods`-class values
  are build-version tokens — they flip loudly on an engine bump
  (intended, same class as existing census pins). The scout's
  `ROWS_PREFIX` variant (census tail cut before `class_method_counts=`)
  is staged at `corpus/live/r92-scout/author-rows.py.txt` if a bump
  ever moves them.
- `regions_f1=0` is admitted **only** inside the envelope — under a
  `--fixed-fps ≥150`-class harness the row still passes via payload[1]
  while `regions_f2=1` continues to assert the settled registration.
  The two-step claim is universal; only the one-step read is modal.
- The nullts pin's `_nullts … :927` site token is bound to this frozen
  probe's line numbering — any future fixture fold must re-pin it
  (deliberate: the sha is recorded, and a moved crash site SHOULD
  fail loudly).
- `nav`'s stderr carries only the deprecation WARNING; a future
  classifier that tightens WARNING handling would reject the row
  (scout hazard #11 — unchanged by this seat).
- Deliberately un-authored boundary vectors: `update_internals`/
  `map_force_update` as nav levers (refuted), `regions_f1` as a
  universal fixed frame (falsified), `has_body_rid` as a positive
  witness (measured negative — pinned only as the negative).
- No commit. Worktree: `M corpus/fixtures/run_battery.py` (+161,
  insertion-only), `?? corpus/fixtures/tilemap_lattice.gd`,
  `?? corpus/live/r92-author/`, this report.

## Evidence index

`corpus/live/r92-author/` — `manifest.sha256` (1510 lines) covers all:

| artefact | path |
|---|---|
| fresh-arm receipts (14 arms × 3 reps, out/err/rc) | `fresh-reps/` |
| author verifier (production classify_process, AST-extracted) | `verify_author.py` |
| battery runs 1–5 (interim flake runs + two green) | `runs{1..5}/<stamp>/verdicts.json`, `battery{1..5}.log` |
| source reports | `reports/round-92/r92-scout.md`, `reports/round-92/r92-boundary.md` |
