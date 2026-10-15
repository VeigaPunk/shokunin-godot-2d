# r95-boundary receipts — DirectSpaceState2D multi-hit ORDER under quiet / 16-hog load / `--fixed-fps` 1-30-120 / threaded physics

Seat `BOUNDARY` (LEAF), lane `r95-boundary`, round 95, host **devin**.
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), `--headless`, GodotPhysics2D, 60 tps.
**261 fresh runs, 8 batches, 0 timeouts (0 × rc=137), 0 non-zero rc, 0 bytes of stderr.**
Every run is `timeout -s KILL 25`-bounded; stdout/stderr split into per-cell sidecars plus `.rc`
and `.wall_ms`. All receipts under `runs/`. Driver: `bash run_matrix.sh <batch>`.

## Launch shape (battery convention)

```
godot --headless [--fixed-fps N] --path <proj> --script res://r95b_order.gd -- --arm=<arm> [--k=..]
```

| artefact | path | sha256 (prefix) |
|---|---|---|
| attack probe (15 arms) | `probes/r95b_order.gd` | see `manifest.sha256` |
| launch project (fixtures byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| threaded-physics project (unstated mode) | `proj_thr/project.godot` | `+[physics] 2d/run_on_separate_thread=true` |
| driver (8 batches) | `run_matrix.sh` | see `manifest.sha256` |
| analyzer → json/text | `analyze_r95b.py` → `runs/analyze_r95b.json`, `analysis.txt` | see `manifest.sha256` |

`proj/r95b_order.gd` and `proj_thr/r95b_order.gd` are byte-copies of `probes/r95b_order.gd`
(the driver copies them at batch start; both project dirs are untracked scratch).

## Batch table (all 8)

| batch | conditions | runs | loadavg (rc-summary) | notes |
|---|---|---|---|---|
| `quiet` | 60 tps, **no seat hogs** | 132 | 72.21 → 76+ | 55 cells; host already at loadavg ~72 from other lanes |
| `load` | 60 tps + **16 seat `yes` hogs** | 53 | 121.31 → 153.41 | own hogs killed by EXIT trap; no `pkill` |
| `ff1` | `--fixed-fps 1` | 8 | 146.99 | 1 process frame ≈ 59–60 physics ticks |
| `ff30` | `--fixed-fps 30` | 16 | 147.91 | 2 physics ticks per process frame |
| `ff120` | `--fixed-fps 120` | 16 | 147.05 | 0–1 physics ticks per process frame |
| `thr` | `physics/2d/run_on_separate_thread=true` | 13 | 147.41 | the scout's §8 declared unknown |
| `label` | 60 tps | 8 | 149.50 | `scoutrev` label-permutation proof |
| `extra` | 60 tps | 15 | 150.01 | `periodx` k = 2…10 period scan |

## Cell inventory (probe arms)

- `canon` — canonical 5-body pile, dense tick ladder t0…t64 + interleaved query stability.
- `perm0…perm7` — **fixed tag→position map, permuted CREATION order** (the clean add-order test).
- `scoutrev` — byte-level replication of the scout's `--rev` construction (index-based positions).
- `warm_k{0,1,2,3,5,8,13,32}` / `warm_keep{8,64}` — K far-away bodies created+freed (or kept) before the pile.
- `free_which_{a..e}` / `free_order_{ab,ba,ac,ca}` — free-order permutations for the same final set.
- `readd_{a,c}` — free + re-add at the same position.
- `cap40_p{0,1,2}` — 40-body pile, permuted creation order, 5-tick `set32` ladder.
- `layers_k{0,1}` — pile ± one `CanvasLayer` body at the same spot.
- `celloff_x{0,0.25,0.5,1,2,4,8,16,32,64,1000,-1000}`, `celloff_xm0.25`, `celloff_y1000` — translation isolation.
- `rigid` — rigid pile (solver determinism fingerprint).
- `procwait` — `await process_frame` ×4 (scheduler sensitivity).
- `period_k{2,3,4,6,8}`, `periodx_k{2,3,4,5,6,7,8,10}` (+ `periodx_k5s8`) — cycle-length scan.
- `twopiles` — pile A at y=0, pile B at y=1000 (co-presence isolation).
- `env` — mode facts (tps, `run_on_separate_thread`, frame accounting).

## Replay

```
cd corpus/live/r95-boundary
bash run_matrix.sh quiet; bash run_matrix.sh load; bash run_matrix.sh ff1
bash run_matrix.sh ff30; bash run_matrix.sh ff120; bash run_matrix.sh thr
bash run_matrix.sh label; bash run_matrix.sh extra
python3 analyze_r95b.py
```

## Host hygiene

- The seat's own 16 `yes` hogs were started and killed **by PID** (`kill "$p"` in the EXIT
  trap + explicit `stop_load`); `pkill` was never used. Other lanes' hogs (48 → 112 during
  the session) were untouched.
- 0 timeouts, no stray probe process after any batch (`pgrep -fa r95b_order` → none),
  no `.godot/` cache written into any tracked project dir (both launch projects are
  untracked scratch under this lane).
- No tracked file written and no commit (`git status --porcelain` at session end shows only
  the pre-existing ` M corpus/fixtures/run_battery.py` from a concurrent lane plus untracked
  `corpus/live/*` and this lane's new report).
