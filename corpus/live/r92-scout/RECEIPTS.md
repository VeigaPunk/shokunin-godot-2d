# r92-scout receipts — TileMapLayer/TileSet authorability lattice

Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps (plus a generated 120 tps project variant), GodotPhysics2D.

## Frozen artefacts

| artefact | path | sha256 |
|---|---|---|
| frozen primary probe (13 arms + 1 hazard arm) | `probes/tilemap_lattice.gd` | `a699138945ec7c1c…` |
| discovery micro-probe (23 arms) | `probes/discover.gd` | `858438b8ec8f98c1…` |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed…` |
| 120 tps launch project | `proj_tps120/project.godot` | `0b7c64916f8c2aee…` |
| driver (13 cells, 51 runs) | `run_cells.sh` | see `manifest.sha256` |
| loadtest driver (13 cells, load avg 118) | `run_loadtest.sh` | see `manifest.sha256` |
| stability analyzer → json | `analyze_r92.py` → `runs/analyze_r92.json` | see `manifest.sha256` |
| row builder / verifier / forge test | `make_author_rows.py`, `verify_rows.py`, `forge_rows.py` | see `manifest.sha256` |
| author rows | `author-rows.py.txt` | see `manifest.sha256` |

## Run inventory

| block | cells | runs | rc |
|---|---|---|---|
| canonical | 13 (9 × 3 reps, 4 × 6 reps) | 51 | all 0 |
| loadtest (16 deliberate `yes` hogs; load avg 118.85 at start) | 13 | 13 | all 0 |
| 120 tps variant | 3 (timing, physics, nav) × 3 | 9 | all 0 |
| discovery / smoke | — | 60+ | see `runs/disc*` |

**Byte-stability:** every canonical cell is `out_uniq=1 err_uniq=1 rc=[0]`
(`runs/analyze_r92.json`, `UNSTABLE=[]`, `CRASH_CELLS=[]`). Every loadtest receipt is
byte-identical to its canonical rep (`LOAD_REJECTIONS: []`). Every 120 tps receipt is
byte-identical to its 60 tps counterpart.

## Row verification

```
$ python3 verify_rows.py
[ROWS(full-line, GATING)] rows=13 receipts_checked=64 rejected=[]
[ROWS_PREFIX(census-tail-cut)] rows=13 receipts_checked=64 rejected=[]
classify_process segment sha256=749fa0607e7707e6

$ python3 forge_rows.py
TOTAL mutants=368 rejected=368 accepted=0
```

`classify_process` was AST-extracted verbatim from `corpus/fixtures/run_battery.py`
(segment sha256 `749fa0607e7707e6` — the same segment r89/r90/r91 pinned).

## Hazard receipts (not rows)

| hazard | receipts | rc |
|---|---|---|
| `tm_nullts` — null TileSet + written cell + `get_cell_tile_data` ⇒ SIGSEGV | `runs/hazard-nullts.r{1,2,3}.{out,err}` | 134 ×3 |
| minimal-trigger isolation | `runs/disc4-fresh_td.*` (safe), `runs/disc4-setcell_td.r{1,2,3}.*` (crash ×3) | 0 / 134 |
