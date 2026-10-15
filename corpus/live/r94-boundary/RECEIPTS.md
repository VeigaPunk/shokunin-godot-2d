# r94-boundary receipts — CPUParticles2D lattice under quiet / load / `--fixed-fps` / tps

Seat `g2d r94 boundary` (LEAF; frozen `probeParent`) | lane `game-dev-2d-shokunin` |
host **devin** | runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`),
`--headless`. No tracked file written, no commit. One labrat dispatch (read-only) returned
INCONCLUSIVE with no receipts (no shell in its seat); see report §9.

## What is here

| artefact | path | notes |
|---|---|---|
| **scout frozen probe (byte-copy)** | `probes/scout_particles_lattice.gd` | sha256 `e6a2e0f55c6bbeaa…` = `corpus/live/r94-scout/probes/particles_lattice.gd` |
| scout discover-6 (byte-copy) | `probes/scout_discover6.gd` | sha256 `213d4cb1dd2a2bc0…` = `corpus/live/r94-scout/probes/discover6.gd` |
| **seat attack probe** | `probes/r94b_particles.gd` | 28 arms: frame_ratio, clock_unit, tps30, tps120, ffprop, ff1_long, amount_sync, amount_attr, amount_pre, amount_cont, amount_phase, amount_b1..b4, contam_a..k + contam_first, gpu_probe, req_var |
| launch project | `proj/project.godot` | sha256 `8de8b3af…` = `corpus/fixtures/project.godot` |
| matrix driver | `run_matrix.sh` | batches quiet/load/ff30/ff60/ff120/ff120load/ab; `timeout -s KILL 25`; hog trap |
| reprobe driver | `run_reprobe.sh` | final probe revision: contamination matrix + amount bisect |
| analyzer | `analyze_r94b.py` → `runs/analyze_r94b.json`, `runs/analysis.txt` | production `classify_process` (AST, segment sha `749fa0607e7707e6…`) + integer envelopes + arm payloads |
| receipts | `runs/<batch>/r94_*` (scout cells), `runs/<batch>/r94b_*` (attack arms) `.{out,err,rc,wall}` | 734 runs |
| batch log | `runs/rc-summary.txt` | loadavg per batch, hog counts, timeout check |
| manifest | `manifest.sha256` | covers every artefact in this directory |

## Batch table (734 launches, 0 timeouts, 0 non-zero rc, 0 B stderr)

| batch | dir | conditions | runs | loadavg start→end |
|---|---|---|---|---|
| quiet | `runs/quiet` | 60 tps, no seat hogs | 138 | 69.4 → 125.7 |
| load | `runs/load` | 60 tps + **16 seat `yes` hogs** | 114 | 125.7 → 118.2 |
| ff30 | `runs/ff30` | `--fixed-fps 30` | 111 | 118.2 → 98.1 |
| ff60 | `runs/ff60` | `--fixed-fps 60` (1:1 ratio control) | 111 | 98.1 → 112.5 |
| ff120 | `runs/ff120` | `--fixed-fps 120` | 111 | 112.5 → 93.9 |
| ff120load | `runs/ff120load` | `--fixed-fps 120` + 16 hogs | 62 | 93.9 → 104.1 |
| ab | `runs/ab` | paired default vs ff30/ff60/ff120, interleaved, 3 pairs | 36 | 104.1 → 93.3 |
| reprobe | `runs/reprobe` | final revision: `contam_*` + `amount_b1..b4` + cont/phase | 51 | 89.1 |
| smoke (not part of the evidence) | `runs/smoke` | probe authoring checks | 25 | — |

Per batch: the scout's 19 frozen cells (3 reps) + 24 attack arms (2–3 reps) + the scout's
own `discover6` amount arms (2–3 reps).

## Replay

```bash
cd corpus/live/r94-boundary
bash run_matrix.sh all      # 683 runs, ~15 min at loadavg 70-130
bash run_reprobe.sh         # 51 runs, final probe revision
python3 analyze_r94b.py     # runs/analysis.txt + runs/analyze_r94b.json
```

Expected analyzer output: `classify_process segment sha256=749fa0607e7707e6…`,
`[scout_canonical] rejected=0`, `[scout_loadtest] rejected=0`,
`[quiet] rejected=0`, `[load] rejected=0`, `[ff30] rejected=3` (all
`r94_particles_cpu_pause`, `ok=false`), `[ff60] rejected=0`, `[ff120] rejected=0`,
`[ff120load] rejected=0`.

## Headline receipts

| finding | receipt |
|---|---|
| `cpu_pause` rejects 3/3 at ff30 | `runs/ff30/r94_particles_cpu_pause.rep{1,2,3}.out` |
| ff30 ladder is 2 ticks low, deterministically | `runs/ab/ab{1,2,3}_f30_cpu_lifetime.rep1.out` |
| particle clock is a time accumulator | `runs/quiet/r94b_clock_unit.rep1.out` |
| process:physics ratio per mode | `runs/{quiet,ff30,ff60,ff120}/r94b_frame_ratio.rep1.out` |
| tps scaling (30/120) | `runs/quiet/r94b_tps{30,120}.rep{1,2,3}.out`, `runs/load/…` |
| `fixed_fps=1` never finishes (4 s bound) | `runs/{quiet,ff30,ff60,ff120}/r94b_ff1_long.rep*.out` |
| request lattice `floor(L/step)+1` | `runs/quiet/r94b_req_var.rep{1,2,3}.out`, `runs/load/…`, `runs/ff120/…` |
| amount hazard not synchronous / same-frame | `runs/quiet/r94b_amount_sync.rep*.out`, `runs/quiet/r94b_amount_attr.rep*.out` |
| continuous-amount F17 flips at ff60 | `runs/ff60/r94b_disc6_amount_cont.rep1.out` (n_fin=1) vs quiet/load/ff30/ff120 (n_fin=0) |
| amount bisect (set tick, not handler/API) | `runs/reprobe/r94b_amount_b{1,2,3,4}.rep{1,2,3}.out` |
| contamination = `add_pf` rule, no global state | `runs/reprobe/r94b_contam_{g,j,k,first,f}.rep*.out` |
| GPU flip range [1,7] | `runs/{quiet,load,ff30,ff120}/r94_particles_gpu_headless.rep*.out` |

## Integrity note (read this before citing the scout's 143/143)

The scout's frozen probe was written at **2026-10-15 16:51:26**; 135 of the 143 receipts
they verified predate it (only `cpu_request`, 6 canonical + 2 loadtest, were re-run on the
frozen revision). `corpus/live/r94-scout/RECEIPTS.md` cites a different probe hash
(`09dd77238668b315…`) than `manifest.sha256`/report (`e6a2e0f5…`). The pre-freeze revision is
unrecoverable (receipts are gitignored; the repo has a single r94 commit). All receipts in
*this* directory were produced by the byte-copy of the frozen probe (sha
`e6a2e0f5…b930`) except where a receipt names `scout_discover6.gd` — see report §2.
