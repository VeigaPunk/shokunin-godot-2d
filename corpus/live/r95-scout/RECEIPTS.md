# r95-scout receipts — PhysicsDirectSpaceState2D query lattice + ordering

Host: `godot 4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), `--headless`, 60 tps,
GodotPhysics2D (`GodotPhysicsDirectSpaceState2D`). Every launch is `timeout -s KILL`-bounded;
no run was left running.

## Probe revisions (both under `probes/`)

| file | role |
|---|---|
| `probes/discover.gd` | discovery micro-probe (18 arms: census, ray/point/shape/cast/rest semantics, ordering permutations, freshness, space scope, alt-construction ordering) — `runs/disc/*`, `runs/discord/*`, `runs/alt/*` |
| `probes/dss_lattice.gd` | **frozen primary probe** (13 arms + 3 `--rev` variants = 17 cells) — canonical receipts under `runs/r95_*.{out,err,rc}` |

`probes/dss_lattice.gd` sha256 `77ae4adb8a47ccf5…` (frozen revision used for **all** 99
canonical + 51 loadtest receipts). The pre-freeze revision leaked server-tier RIDs and printed
`ERROR: N RID allocations … were leaked at exit` on **stdout** — preserved as evidence under
`runs/leak-hazard/` (§H3 of the report).

## Canonical cells (99 runs, all rc=0, all stderr 0 B)

| cell | arm | flags | reps | receipts |
|---|---|---|---|---|
| dss_census | census | — | 3 | `runs/r95_dss_census.rep{1..3}.*` |
| dss_ray_flags | ray_flags | — | 6 | `runs/r95_dss_ray_flags.rep{1..6}.*` |
| dss_ray_geom | ray_geom | — | 6 | `runs/r95_dss_ray_geom.rep{1..6}.*` |
| dss_ray_order | ray_order | — | 6 | `runs/r95_dss_ray_order.rep{1..6}.*` |
| dss_ray_order_rev | ray_order | `--rev` | 6 | `runs/r95_dss_ray_order_rev.rep{1..6}.*` |
| dss_point_cap | point_cap | — | 6 | `runs/r95_dss_point_cap.rep{1..6}.*` |
| dss_point_cap_rev | point_cap | `--rev` | 6 | `runs/r95_dss_point_cap_rev.rep{1..6}.*` |
| dss_point_edge | point_edge | — | 6 | `runs/r95_dss_point_edge.rep{1..6}.*` |
| dss_point_canvas | point_canvas | — | 6 | `runs/r95_dss_point_canvas.rep{1..6}.*` |
| dss_shape_lattice | shape_lattice | — | 6 | `runs/r95_dss_shape_lattice.rep{1..6}.*` |
| dss_shape_lattice_rev | shape_lattice | `--rev` | 6 | `runs/r95_dss_shape_lattice_rev.rep{1..6}.*` |
| dss_order_core | order_core | — | 6 | `runs/r95_dss_order_core.rep{1..6}.*` |
| dss_order_core_rev | order_core | `--rev` | 6 | `runs/r95_dss_order_core_rev.rep{1..6}.*` |
| dss_layer_forms | layer_forms | — | 6 | `runs/r95_dss_layer_forms.rep{1..6}.*` |
| dss_cast_rest | cast_rest | — | 6 | `runs/r95_dss_cast_rest.rep{1..6}.*` |
| dss_excl_space | excl_space | — | 6 | `runs/r95_dss_excl_space.rep{1..6}.*` |
| dss_fresh | fresh | — | 6 | `runs/r95_dss_fresh.rep{1..6}.*` |

`runs/rc-summary.txt` records the driver's rc vectors + host line.
`runs/analyze_r95.json` is the per-cell stability report — **`UNSTABLE=[]`, `CRASH_CELLS=[]`**,
every cell `out_uniq=1 err_uniq=1 pass_uniq=1 rc=[0]` with 0 B stderr.

**Naming:** receipt/driver prefixes are `dss_<arm>` (`dss_shape_lattice`, `dss_ray_order_rev`, …);
the **battery case names** in `author-rows.py.txt` are `dss_lattice_<arm>` with two exceptions —
`dss_lattice_shape` / `dss_lattice_shape_rev` (arm `shape_lattice`) — see `RUN_PREFIX` in
`verify_rows.py`, which maps case names to receipt prefixes.

## Loadtest receipts (51 runs, load avg 95–109, 16 own `yes` hogs)

`runs/loadtest/dss_*.rep{1,2,3}.{out,err,rc}` + `runs/loadtest/rc-summary.txt` (per-cell load
avg). Host baseline was already ~90 (other lanes); the hog block raised it to ~109. Only this
seat's own hog PIDs were killed (`own_hogs_killed=16`, `host_yes_remaining=72`).

## Discovery receipts (all under `runs/`)

| receipt dir | what it measured |
|---|---|
| `runs/disc/d_*.{out,err}` | 17-arm first-pass discovery (API census, flags, geometry, ordering, layer, space, freshness) |
| `runs/disc/d_rest_semantics.out` | `get_rest_info` sweep ladder (m50…m600, exclude/mask/off-axis) — entry-vs-exit contact transition |
| `runs/discord/*` | early 4-process ordering cross-check + `--rev` pairs (superseded by the frozen cells) |
| `runs/alt/alt_p{0,1,2}.{1,2,3}.out` | **independent-construction falsification**: 6 mixed-shape colliders (circle/capsule/rotated rect), 3 add-order permutations × 3 fresh processes + translated pile |
| `runs/leak-hazard/pre_fix_*.out` | the stdout RID-leak ERROR captured before the probe fix |
| `runs/smoke/*` | frozen-probe arm smoke tests (superseded by the canonical cells) |

## Rows / verification

- `author-rows.py.txt` — 17 rows: `ROWS` (full-line) and `ROWS_PREFIX` (**recommended**; cut
  before the multi-hit order vectors for the 4 order-vector cells) + `EXPECTED_ERRORS = {}`.
- `verify_rows.py` — extracts `classify_process` from `corpus/fixtures/run_battery.py` by AST
  (segment sha256 `749fa060…`, the same segment r89/r90/r91 pinned) and classifies every row
  against every canonical **and** loadtest receipt (stdout+stderr merged as `run_process` does):
  **`ROWS` 150/150 accepted, `ROWS_PREFIX` 150/150 accepted, `rejected=[]`.**
- Reproduce: `bash run_cells.sh && bash run_loadtest.sh && python3 analyze_r95.py &&
  python3 make_author_rows.py && python3 verify_rows.py`.
