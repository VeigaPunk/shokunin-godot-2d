# r94-scout receipts — CPUParticles2D + GPUParticles2D emission lattice

Seat `g2d r94 scout` | lane `game-dev-2d-shokunin` | host **devin** | runtime
**Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
default 60 physics ticks/s. No tracked file written, no commit, no subagent
execution (the one permitted labrat dispatch returned INCONCLUSIVE — its
substrate exposed no shell/write tool, see report §9).

## What is here

| artefact | path | notes |
|---|---|---|
| **frozen primary probe** (19 arms) | `probes/particles_lattice.gd` | `sha256 09dd77238668b315…`; one `PASS particles_lattice <arm> …` line per arm |
| discovery probes 1–7 | `probes/discover.gd` … `discover7.gd` | exploratory; every finding in the report cites `runs/disc*` |
| launch project (fixtures byte-copy) | `proj/project.godot` | `sha256 8de8b3af9cc737ed…` = `corpus/fixtures/project.godot` |
| canonical driver | `run_cells.sh` | 19 cells: 3 pure ×3 reps, 16 timing ×6 reps = **105 runs** |
| loadtest driver | `run_loadtest.sh` | same 19 cells ×2 reps under `yes` hogs = **38 runs** |
| analyzer | `analyze_r94.py` → `runs/analyze_r94.json`, `runs/analyze_r94.txt` | reps / out_uniq / err_uniq / rc / common prefix |
| author rows + builder + verifier | `author-rows.py.txt`, `make_author_rows.py`, `verify_rows.py` | 19 `ROWS` (full line) + 19 `ROWS_PREFIX` (gating) |
| per-cell receipts | `runs/r94_particles_*.rep*.{out,err,rc}` | 105 canonical + 38 loadtest |
| discovery receipts | `runs/disc*.{out,err}` (54), `runs/smoke*.{out,err}` (16) | exploratory evidence |
| canonical unique-line dump | `runs/canonical-lines.txt` | every unique PASS line per cell |
| manifest | `manifest.sha256` | covers every artefact in this directory |

## Canonical matrix (105 runs)

All 19 cells rc=0, **0 B stderr on every run** (no ERROR/WARNING/SCRIPT ERROR
anywhere; `err_uniq=1` and `err_bytes=[0]` for all cells in
`runs/analyze_r94.json`).

- byte-stable full line (12 cells): `census`, `ppm`, `convert`,
  `cpu_never`, `cpu_contam`, `cpu_oneshot_off`, `cpu_oneshot_flag`,
  `cpu_retrigger`, `cpu_lt_mid`, `cpu_speed_mid`, `cpu_amount_mid`,
  `cpu_request`
- ±1-tick measured tail (7 cells): `cpu_lifetime`, `cpu_expl`,
  `cpu_speed_pre`, `cpu_stop`, `cpu_pause`, `cpu_restart`, `gpu_headless`
  — every one of these keeps a byte-stable boolean prefix before `" | "`.

## Loadtest (38 runs)

`runs/loadtest/load-summary.txt`: started at loadavg **110.2 / 93.2 / 61.6**
(8 own `yes` hogs plus ~88 host hogs from concurrent lanes), all rc=[0 0],
0 B stderr. Two cells (`census`, `cpu_amount_mid`) were re-run in a second
block at loadavg 47.9 → 45.2 and stayed byte-identical.

## Rows verification

`python3 verify_rows.py` (production `classify_process` AST-extracted from
`corpus/fixtures/run_battery.py`, segment sha256 `749fa0607e7707e6`):

- `ROWS_PREFIX` (gating): 19 rows × **143 receipts** (105 canonical + 38
  loadtest) → **`rejected=[]`**
- `ROWS` (full line, informational): 30 rejections across the 7 cells with the
  ±1-tick tail (expected; use in a quiet window or as mode envelopes)

## Reproduce

```sh
cd corpus/live/r94-scout
bash run_cells.sh            # 105 canonical runs (~3 min)
python3 analyze_r94.py       # stability table + runs/analyze_r94.json
python3 make_author_rows.py && python3 verify_rows.py
HOGS=8 REPS=2 bash run_loadtest.sh   # 38 runs under load
```

`run_cells.sh` copies `probes/particles_lattice.gd` into `proj/` before running
(the battery does the same copy step). Nothing outside this directory is
touched.
