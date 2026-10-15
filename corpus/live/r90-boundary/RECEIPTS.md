# r90-boundary receipts — RigidBody2D lattice stress (round 90)

Seat `BOUNDARY` (LEAF) | lane `r90-boundary` | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`).
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at session start `0628932`.

**281 receipted runs** (299 launches; the t30 rerun overwrote its own 18 receipts),
**every launch `timeout -s KILL 25`-bounded, all rc=0**
(no bound hit, no crash, no stray child). Nothing tracked was written; this
directory and `reports/round-90/r90-boundary.md` are untracked additions.

## Layout

| artefact | role |
|---|---|
| `probes/b90.gd` | boundary probe, 9 arms: `order write lag damp impulse comcase backend stall settle` (`--arm=`, `--case=`, `--stall=`, `--stall_at=`, `--delay=`, `--frames=`) |
| `probes/b90_watch.gd` | `_integrate_forces` forwarder (required by `b90.gd`) |
| `probes/scout_rb_lattice.gd` | **byte-copy** of the r90 scout probe (sha256 `4f201e85…`) |
| `probes/scout_rb_watch.gd` | byte-copy of the scout's `rb_watch.gd` (sha256 `e349faa0…`), installed as `rb_watch.gd` |
| `proj/` | 60 tps, engine DEFAULT (fixtures project shape) |
| `proj_tps30/`, `proj_tps120/`, `proj_tps240/` | `physics/common/physics_ticks_per_second=30/120/240` |
| `proj_dummy/` | `physics/2d/physics_engine="Dummy"` |
| `proj_jolt2d/` | `physics/2d/physics_engine="Jolt Physics"` (3D-only name) |
| `proj_garbage/` | `physics/2d/physics_engine="garbage_xyz"` |
| `run_cells.sh` | driver; batches `base com load1 load2 delay dummy t30 par all` |
| `analyze_boundary.py` → `analyze_boundary.json`, `analysis.txt` | per-cell rc/uniq/at-lines + claim checks |
| `runs/` | 281 receipts × `.out/.err/.rc/.wall` (`.wall` absent for the 26 `p_*` concurrent runs) |
| `manifest.sha256` | every artefact under this directory except itself |

## Batches (host loadavg ~14–26 from concurrent lanes throughout; this seat adds its own)

| batch | window (UTC) | scope | load |
|---|---|---|---|
| `base` | 19:12:22–19:14:53 | 33 cells × 3 reps = 99 runs: order @60/120/30 tps, write, lag @30/60/120/240 tps × N=30/60/120, damp @60/120, impulse, backend ×4, damp-dummy, stall ×3, settle, **scout verbatim ×9 cells** | none added |
| `com` | 19:14:53–19:15:20 | 18 COM scenarios × 3 reps = 54 runs (one scenario per process) | none added |
| `load1` | 19:15:20–19:16:31 | 39 runs under **32 × `yes>/dev/null`** system-wide; loadavg 20.10 → 25.91 | L1 |
| `load2` | 19:16:31–19:17:06 | 15 runs with **godot `taskset -c 0,1`** and **12 × `yes` pinned `taskset -c 0-3`** | L2 |
| `delay` | 19:17:06–19:17:33 | 18 runs: order with `--delay=0/20/50/100/200/300` (startup-race positive control) | none added |
| `par` | 19:17:33–19:17:41 | 26 runs: 8-way / 6-way **concurrent** godot processes | self |
| `t30` | 19:18:04–19:19:04 (two passes) | 36 runs: order ×9 and lag ×9 at 30 tps (pairing-race distribution); the identical second pass overwrote the first pass's 18 receipts | none added |
| `dummy` | 19:19:29–19:19:48 | 12 runs: order/impulse/scout-freezelock/scout-contacts under `PhysicsServer2DDummy` | none added |

All load hogs were killed at batch end (`load_stopped=1`); `pgrep -fa '^yes$'`
is empty at report time. The smoke runs used for probe syntax checks were
discarded before the receipt sweep (single coherent probe revision, sha256 in
`manifest.sha256`).

## Reproduce

```bash
cd corpus/live/r90-boundary
bash run_cells.sh all        # ~7 min; needs `godot` on PATH; BOUND=25 default
python3 analyze_boundary.py  # expect every cell rc=0, pass_uniq=1, pins all_ok
```
