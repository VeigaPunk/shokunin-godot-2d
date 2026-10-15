# r91-boundary receipts — Navigation2D under quiet / 16-hog load / --fixed-fps 30/60/120

Seat `BOUNDARY` (LEAF), lane `r91-boundary`, round 91, host **devin**.
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), `--headless`, GodotPhysics2D.
**403 fresh runs** (346 rc=0, 57 rc=134 expected SIGABRT, **0 timeout** / rc=137).
Every run is `timeout -s KILL 25`-bounded; stdout/stderr split into per-cell sidecars plus `.rc`
and `.wall`. All receipts under `runs/`. Batches: 9. Driver: `run_matrix.sh <batch>`.

## Launch shape (battery convention)

```
godot --headless [--fixed-fps N] --path proj --script res://<probe>.gd -- --arm=<arm>
```

Probes (all frozen in `probes/` and copied byte-identical into `proj/`):

| probe | sha256 | role |
|---|---|---|
| `scout_nav_lattice.gd` | `efb496e5fe08e667…` | **byte-copy** of the r91 scout's frozen probe (`nav_lattice.gd`) — verbatim cells `sv_*` |
| `r91b_nav.gd` | see `manifest.sha256` | seat attack probe: `gate`, `change`, `agent`, `avoid`, `bake`, 6 teardown arms |
| `r91b_agent_diag.gd` | see `manifest.sha256` | agent query-order diagnostic (`v1…v9`) + discriminating bent-path lane (`bent`) |
| `proj/project.godot` | `8de8b3af9cc737ed…` | byte-copy of `corpus/fixtures/project.godot` |

## Batch table (all 9)

| batch | conditions | runs | loadavg start → end | notes |
|---|---|---|---|---|
| `quiet` | 60 tps, no seat hogs | 60 | 58.51 → 72.42 | 20 cells × 3 |
| `load` | 60 tps + **16 seat hogs** | 100 | 76.28 → 93.33 | 20 cells × 5; seat hogs killed after |
| `ff30` | `--fixed-fps 30` | 60 | 89.78 → (89.78…) | 20 cells × 3 |
| `ff120` | `--fixed-fps 120` | 60 | 112.57 → 112.57 | 20 cells × 3 |
| `ff120load` | `--fixed-fps 120` + 16 seat hogs | 60 | 96.03 → 100.07 | 20 cells × 3 |
| `quiet2` | 60 tps repeat window | 18 | 100.07 → 118.17 | 6 mode-prone cells × 3 |
| `ab` | paired default vs ff30/ff60/ff120, interleaved | 24 | 117.36 → 106.80 | 6 pairs × 4 variants, 1 rep each |
| `disc` | scout's own `discover.gd` crash arms | 9 | 106.80 → 98.33 | `navfree2/5/6` × 3, `--path ../r91-scout/proj` |
| `diag2` | v9 triple + bent, quiet + 16 hogs | 12 | 95.02 → 88.63 | 2 cells × 3 × 2 windows |

`runs/rc-summary.txt` carries the per-batch `loadavg_start/end`, hog counts and timeout check;
`runs/analyze_r91b.json` + `analysis.txt` are the machine summary (`analyze_r91b.py`).

## Cell inventory

- **scout-verbatim** (`scout_nav_lattice.gd`): `sv_sync`, `sv_region`, `sv_agent`, `sv_avoid`, `sv_bake`.
- **attack** (`r91b_nav.gd`): `b_gate`, `b_change`, `b_agent`, `b_avoid`, `b_bake`.
- **agent diagnostic** (`r91b_agent_diag.gd`): `d_v1` (scout-exact), `d_v5` (fin read first),
  `d_v7` (reached ×2), `d_v8` (fin ×2 then reached), `d_v9` (same-frame reached→fin→reached triple),
  `d_bent` (L-shaped path: straight-line vs path length).
- **teardown** (`r91b_nav.gd`): `c_noclear`, `c_clear0`, `c_clear1`, `c_clear2`, `c_leak_cb`, `c_leak_clean`.
- **scout discovery** (`../r91-scout/proj/discover.gd`): `dc_navfree2`, `dc_navfree5`, `dc_navfree6`.

## Replay

```
cd corpus/live/r91-boundary
bash run_matrix.sh quiet; bash run_matrix.sh load; bash run_matrix.sh ff30; bash run_matrix.sh ff120
bash run_matrix.sh ff120load; bash run_matrix.sh quiet2; bash run_matrix.sh ab; bash run_matrix.sh disc
bash run_matrix.sh diag2
python3 analyze_r91b.py
```

## Load discipline

`start_load N` records the exact `yes` PIDs it spawned; `stop_load` (also the EXIT trap) kills only
those PIDs. System-wide `pgrep -c -x yes` counts include other lanes' hogs (12–72 across this
session) and were never touched. No godot process from this lane remained after any batch
(`pgrep -fa 'r91b_nav|r91b_agent_diag|scout_nav_lattice|discover.gd'` → 0).
