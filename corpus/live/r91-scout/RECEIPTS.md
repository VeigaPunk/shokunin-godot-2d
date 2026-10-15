# r91-scout receipts — Navigation2D authorability lattice

Host: `godot 4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), `--headless`, 60 tps,
GodotPhysics2D. Every launch is `timeout -s KILL`-bounded; no run was left running.

## Probe revisions (both under `probes/`)

| file | role |
|---|---|
| `probes/discover.gd` | discovery micro-probe (20 arms: API census, sync feasibility, avoidance teardown matrix, bake routes) — `runs/disc-*.{out,err}` |
| `probes/nav_lattice.gd` | **frozen primary probe** (9 arms) — canonical receipts under `runs/r91_*.{out,err,rc}` |

## Canonical cells (45 runs, all rc=0)

| cell | arm | reps | receipts |
|---|---|---|---|
| nav_census | census | 3 | `runs/r91_nav_census.rep{1,2,3}.*` |
| nav_path | path | 3 | `runs/r91_nav_path.rep{1,2,3}.*` |
| nav_query | query | 3 | `runs/r91_nav_query.rep{1,2,3}.*` |
| nav_sync | sync | 6 | `runs/r91_nav_sync.rep{1..6}.*` |
| nav_region | region | 6 | `runs/r91_nav_region.rep{1..6}.*` |
| nav_agent | agent | 6 | `runs/r91_nav_agent.rep{1..6}.*` |
| nav_avoid | avoid | 6 | `runs/r91_nav_avoid.rep{1..6}.*` |
| nav_bake | bake | 6 | `runs/r91_nav_bake.rep{1..6}.*` |
| nav_link | link | 6 | `runs/r91_nav_link.rep{1..6}.*` |

`runs/rc-summary.txt` records the driver's rc vectors + host line.
`runs/analyze_r91.json` is the per-cell stability report (`UNSTABLE=['nav_avoid']`).

## Loadtest receipts (31 runs, load avg 20–25, deliberate `yes` hogs)

`runs/loadtest/nav_{census,path,query,sync,region,agent,avoid,bake,link}.rep{1,2,3}.*`
(plus `nav_sync.rep{4..7}` from the first hog block). These prove the async-sync
counters (`settle=`, `iter=`, `ladder=`, `first_reach*`) are load-sensitive while the
settled payloads are not: full-line signatures fail 1/3–2/3 under load for
path/query/sync, stable-prefix signatures pass 76/76 receipts (see `verify_rows.py`).

## Discovery receipts (selected; all under `runs/`)

| receipt | what it measured |
|---|---|
| `disc-census.*` | ClassDB method/enum census for the nav classes |
| `disc-navmin.*` | first path query: `map_force_update` in `_initialize` does not sync; RID-leak ERROR lines |
| `disc-navdbg.*` | sync ladder (region appears f1, bounds f3, path f4) + the pre-sync refusal ERROR `nav_map_2d.cpp:165` |
| `disc-navstep.*` | force_update bumps iteration id but paths stay empty pre-region-raster |
| `disc-navbakedbg.*` | bake in `_initialize` → `ERROR: The root node needs to be inside the SceneTree.` |
| `disc-navagentdbg.*` | `NavigationAgent2D` is a Node; first `get_next_path_position()`=(0,0) pre-sync |
| `disc-navavoid3.*` | server avoidance callbacks fire; free-with-callback crash (`double free or corruption`, rc=134) |
| `disc-navavoid4.*` | callback fires with input velocity; positions do not integrate server-side |
| `disc-navavoid5.*` | close approach → decelerating safe velocity; leak-at-exit also crashes |
| `disc-navfree{1..7}.*` | teardown matrix: only callback+free crashes; clear-callback + ≥1 frame is clean; node `queue_free` clean |
| `disc-navbake{4,5,6,7,8}.*` | bake routes: outline route works; collider-only bakes empty; modern route needs a traversable outline; bake output feeds a server region |
| `disc-navpoly2.*` | two hand-built polygons in ONE NavigationPolygon do not connect; two regions do |
| `disc-navsync2/3.*` | change-application timing: live changes 2–3 frames, `map_force_update` not synchronous; async=false initial sync ~2 frames |
| `disc-navlinkdbg.*` | link traversal + waypoints; state changes need a frame |
| `disc-navclasses.*` | NavigationLink2D / NavigationMeshSourceGeometryData2D exist; enums |
| `smoke*/disc-*` | arm smoke tests and probe-revision traces (superseded by the frozen probe) |

## Rows / verification

- `author-rows.py.txt` — 9 rows: `ROWS` (full-line, verified on canonical reps) and
  `ROWS_PREFIX` (**recommended**, stable-prefix; verified on canonical + loadtest) +
  `EXPECTED_ERRORS` (sync pre-sync refusal, bake orphan-node refusal).
- `verify_rows.py` — extracts `classify_process` from `corpus/fixtures/run_battery.py`
  by AST (segment sha256 `749fa060…`, same segment r89/r90 pinned) and classifies every
  row against every receipt: `ROWS_PREFIX` **76/76 accepted, rejected=[]**.
- Reproduce: `bash run_cells.sh && python3 analyze_r91.py && python3 make_author_rows.py &&
  python3 verify_rows.py`.
