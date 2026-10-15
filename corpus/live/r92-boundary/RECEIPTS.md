# r92-boundary receipts — run inventory, conditions, replay

Seat `BOUNDARY` (LEAF) | lane `r92-boundary` | round 92 | host **plazir27** (devin).
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
GodotPhysics2D. Every run bounded by `timeout -s KILL 25`.

All writes are `reports/round-92/r92-boundary.md` (new, untracked) and
`corpus/live/r92-boundary/**`. No tracked file written, no commit.

## Probes

| probe | sha256 (prefix) | role |
|---|---|---|
| `probes/scout_tilemap_lattice.gd` | `a699138945ec7c1c` | byte-copy of the r92 scout's frozen 13-arm probe |
| `probes/r92b_probe.gd` | see `manifest.sha256` | seat's per-physics-frame pollers (`sched`/`phys`/`nav`) |
| `probes/r92b_navmech.gd` | see `manifest.sha256` | nav mechanism probe (`mech` warm / `cold` phase) |
| `../r91-scout/probes/nav_lattice.gd` | `efb496e5fe08e667` | r91 scout's frozen probe, used as the positive control |

Launch shape (battery): `godot --headless [--fixed-fps N] --path <proj> --script res://<script> -- --arm=<arm>`
`proj/` and `proj_tps120/` are byte-copies of the r92 scout's launch projects
(`8de8b3af…` / `0b7c6491…`).

## 667 receipts, 639 rc sidecars, all `rc=0`, 0 timeouts, 0 watchdog FAILs

| batch | condition | arms | reps | runs | loadavg start→end (yes hogs incl. ambient) |
|---|---|---|---|---|---|
| `quiet` (`q60_*`) | 60 tps default | 13 + 3 own | 3 + 2 | 39+6 | 61.16→64.06 (48→32) |
| `load` (`l60_*`) | 60 tps + **12 seat hogs** | 13 + 3 own | 3 + 2 | 39+6 | 64.06→67.85 (44→32) |
| `ff30` (`f30_*`) | `--fixed-fps 30` | 13 + 3 own | 3 + 2 | 39+6 | 67.85→57.33 |
| `ff60` (`f60_*`) | `--fixed-fps 60` | 13 + 3 own | 3 + 2 | 39+6 | 57.33→56.62 |
| `ff120` (`f120_*`) | `--fixed-fps 120` | 13 + 3 own | 3 + 2 | 39+6 | 56.62→67.75 |
| `ff120load` (`f120l_*`) | `--fixed-fps 120` + 12 hogs | 13 + 3 own | 2 + 2 | 26+6 | 71.22→72.50 (60→32) |
| `tps120` (`t120_*`) | 120-tps project, default scheduler | 13 + 3 own | 3 + 2 | 39+6 | 72.50→71.63 |
| `q60b` (`q60b_*`) | repeat quiet window | 13 + 3 own | 2 + 2 | 26+6 | 80.82→75.84 (64→32) |
| `ff10` (`f10_*`) | `--fixed-fps 10` (0.167 idle:physics) | 13 + 3 own | 2 + 2 | 26+6 | 75.84→75.76 |
| `ff20` (`f20_*`) | `--fixed-fps 20` (0.33) | 13 + 3 own | 2 + 2 | 26+6 | 75.76→76.90 |
| `ff600` (`f600_*`) | `--fixed-fps 600` (10.0) | 13 + 3 own | 2 + 2 | 26+6 | 76.90→73.67 |
| `ff30load` (`f30l_*`) | `--fixed-fps 30` + 12 hogs | 13 + 3 own | 2 + 2 | 26+6 | 73.67→92.94 (76→48) |
| `load32` (`l32_*`) | 60 tps + **32 seat hogs** | 13 + 3 own | 2 + 2 | 26+6 | 92.94→**145.25** (80→96) |
| `scan` (`runs/scan/`) | ff 240/300/400/480/600/900 × scout+own nav | 2 scripts | 2 | 28 | 150.6 (after ff600load hogs) |
| `scan2` (`runs/scan2/`) | ff 150/180/200/210 + tps120×{none,120,240,480} | 2 scripts | 2 | 32 | 150.6 |
| `reps` (`runs/reps/`) | scout nav rate: default ×20, ff120 ×20, ff150 ×10, ff600 ×10 | 1 | — | 60 | 103–110 |
| `mech` (`runs/mech/`) | navmech `cold`/`mech` × {default,ff120,ff150,ff240,ff600,t120_ff480,t120} | 1 | 2 | 28 | 97–110 |
| `control` (`runs/control/`) | r91 scout `nav_lattice.gd --arm=sync` × {default, ff120, ff30} | 1 | 3 | 9 | 149 |
| `extreme` (`runs/extreme/`) | ff 5 / 1 × {physics,timing,quadrant,nav} | 4 arms | 2 | 16 | 97 |

Batch wall times: 0.58–2.51 s per run (max `ol32`, 32-hog load); the 25 s bound was
never approached. No run left running. The seat's own `yes` hogs were killed after
every load batch (`stop_load` + EXIT trap); `ps` shows **no orphaned `yes`**
(ppid≠1); the 32–112 `yes` processes visible throughout belong to concurrent lanes
and were left untouched.

## Replay

```bash
cd corpus/live/r92-boundary
bash run_matrix.sh quiet load ff30 ff60 ff120 ff120load tps120   # wave 1
bash run_matrix.sh q60b ff10 ff20 ff600 ff30load load32          # wave 2
bash run_control.sh        # r91 scout nav_lattice sync positive control
bash run_nav_scan.sh       # ff240..900 nav ratio scan
bash run_nav_scan2.sh      # ff150..210 + tps120 crossing
bash run_nav_reps.sh       # scout nav rate test
python3 analyze_r92b.py    # -> runs/analyze_r92b.json
python3 verify_r92b.py .   # production classify_process gating
```

## Verification transcripts

`python3 verify_r92b.py` (production `classify_process`, AST-extracted from
`corpus/fixtures/run_battery.py`, segment sha256 `749fa0607e7707e6` — the same
segment r89/r90/r91/r92 pinned):

```
classify_process segment sha256=749fa0607e7707e6
boundary receipts=416  scout control receipts=64
[BOUNDARY/ROWS(full-line)] rows=13 receipts_checked=416 rejected=2
    q60 39/0  l60 39/0  f30 39/0  f60 39/0  f120 39/0  f120l 26/0  t120 39/0
    q60b 26/0  f10 26/0  f20 26/0  f600 26/2  f30l 26/0  l32 26/0
    REJECTED ('r92_tilemap_nav', 'f600', 'f600_nav.rep1.out')
    REJECTED ('r92_tilemap_nav', 'f600', 'f600_nav.rep2.out')
[BOUNDARY/ROWS_PREFIX(census-tail-cut)] rows=13 receipts_checked=416 rejected=2   (same two)
[SCOUT-CONTROL/ROWS] rows=13 receipts_checked=64 rejected=0
```

`python3 analyze_r92b.py`: 13 × 13 condition cells — every cell `OK` except
`nav / f600` (`regions_f1=1` → `0`, both reps); stderr is byte-identical to the
scout's after normalising only the probe filename in engine backtraces
(`res://scout_tilemap_lattice.gd` → `res://tilemap_lattice.gd`; engine source paths
and line numbers unchanged).

`runs/control/` (positive control, r91 scout `sync` arm — default vs ff120/ff30):
`chg_settled=true` 3/3 in default, `false` 3/3 at ff120 and ff30;
`first_reach=8,-1,-1` default vs `-1` 3/3 ff120 — the harness sees scheduler
sensitivity.
