# r98-boundary receipts — CanvasItem claims under quiet / 16-hog load / `--fixed-fps` 1-30-120 / ff30+load / `--frame-delay 100`

Seat `BOUNDARY` (LEAF), lane `r98-boundary`, round 98, host **devin**.
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), `--headless`, `RendererDummy`.
**263 runs, 7 batches, 0 timeouts (0 × rc=137), 0 non-zero rc.** Every run is
`timeout -s KILL 25`-bounded; stdout/stderr split into per-cell sidecars plus `.rc` and
`.wall_ms`. All receipts under `runs/`. Driver: `bash run_matrix.sh <batch>`.

## Launch shape (battery convention)

```
godot --headless [--fixed-fps N | --frame-delay 100] --path proj \
  --script res://<canvas_lattice.gd | r98b_attack.gd> -- --arm=<arm> [--var=..]
```

| artefact | path | sha256 (prefix) |
|---|---|---|
| attack probe (14 cells, 10 arms) | `probes/r98b_attack.gd` | `2e71c7158c4f53db…` (the exact file the batches ran) |
| frozen scout probe, BYTE-COPY | `probes/scout_canvas_lattice.gd` | `866480a1aaa0a385…` = scout's `canvas_lattice.gd` |
| supplementary R*K*S enumeration | `probes/r98b_rksenum.gd` | see `manifest.sha256` |
| launch project (fixtures byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| driver (7 batches) | `run_matrix.sh` | see `manifest.sha256` |
| analyzer → json/text | `analyze_r98b.py` → `runs/analyze_r98b.json`, `analysis.txt` | see `manifest.sha256` |

`proj/canvas_lattice.gd` and `proj/r98b_attack.gd` are copies made by the driver at batch
start; both project dirs are untracked scratch.

## Batch table (all 7)

| batch | conditions | runs | loadavg (rc-summary start→end) | notes |
|---|---|---|---|---|
| `quiet` | 60 tps, **no seat hogs** | 58 | 84.32 → 81.40 | host already loaded by other lanes |
| `load` | 60 tps + **16 seat `yes` hogs** | 58 | 81.40 → 92.15 | own hogs killed by EXIT trap; no `pkill` |
| `ff1` | `--fixed-fps 1` | 29 | 92.15 → 94.56 | ~60 physics ticks per process frame |
| `ff30` | `--fixed-fps 30` | 29 | 94.56 → 96.84 | 2 ticks per frame |
| `ff120` | `--fixed-fps 120` | 29 | 96.84 → 96.14 | 0–1 ticks per frame |
| `ff30load` | `--fixed-fps 30` + 16 hogs | 29 | 96.14 → 101.54 | combined mode |
| `slow` | `--frame-delay 100` (no fixed-fps) | 29 | 91.06 → 78.56 | the multi-tick-frame control: ~6–7 ticks/frame |

Per-batch cells: 15 frozen-scout cells (`r98_canvas_*`, reps 2/2/1/1/1/1/1) + 14 attack
cells (`r98b_*`, reps 2/2/1/1/1/1/1). Wall times 0.7–1.4 s except `slow` max 7.4 s.

## Cell inventory (attack probe arms)

- `qflush` — queue from `_physics_process`: same-process-frame flush, per-tick vs per-frame
  coalescing, self-queue swallow, tick-separated hide.
- `qorder` — draw-callback order per frame: tree queue, reverse queue, 3-tick staggered
  queue, tick-offset stagger (r95 tick-phase lesson).
- `latch_canon|t1|t3|imm|second` — the scout's context-dependent redraw latch + tick-offset
  / immediate / second-write variants.
- `gskew` — `global_skew`/`global_rotation`/`global_scale` round-trip under a non-uniform parent.
- `skewgrid` — 200-combo exact-equality grid for `get_transform()` vs `Transform2D(r,s,k,p)`
  and vs the scout's `R·K·S` product, incl. degenerate/negative scales, |skew| > PI.
- `epssweep` — zero/degenerate-scale readback vs parent scale (epsilon law).
- `clipmatrix` — `clip_children` refusal matrix (prior values, == MAX, negatives, recovery).
- `notifyphase` — transform/reparent notification flush vs tick/frame waits.
- `visphase` — visibility-chain counts, process-frame vs physics-frame ladder.
- `env` — launch-mode fingerprint (informational).

## Reproduce

```
bash run_matrix.sh quiet && bash run_matrix.sh load && bash run_matrix.sh ff1 &&
bash run_matrix.sh ff30 && bash run_matrix.sh ff120 && bash run_matrix.sh ff30load &&
bash run_matrix.sh slow && python3 analyze_r98b.py
```

Expect `SCOUT_DIFF=[]`, `ERR_MISMATCH=[]`, `NONZERO_RC=[]`; `UNSTABLE` only for the
tick-phase keys of `r98b_qflush`/`r98b_qorder`/`r98b_env` in quiet/load (documented in
`reports/round-98/r98-boundary.md` §3).

## Supplementary one-off

`probes/r98b_rksenum.gd` (2 reps, `runs/rksenum/`, byte-identical): enumerates the 60
non-degenerate combos where the scout's `R·K·S` product is not bit-equal to the 4-arg
constructor (max abs component diff 4.77e-7 — float32 rounding, not a structural
difference).

## Independent probe (frozen probeParent)

One read-only `ufo-labrat` seat audited the final receipt set against
`reports/round-98/r98-boundary.md`: **10/10 checks CONFIRMED, no counterexamples**
(qflush ff1/slow/quiet payloads, skewgrid/epssweep/clipmatrix vectors, the byte-identity of
`runs/slow/r98_canvas_queue.rep1.out` with the scout's receipt, 263 `.out` files, all `.rc`
= 0 / no 137, and the analyzer flags).

## Host cleanup

- Own load hogs: 16 `yes` started in `load`/`ff30load`, all killed by the EXIT trap
  (never `pkill`); other lanes' hogs untouched.
- No stray probes: `pgrep -fc 'canvas_lattice|r98b_attack'` → 0 after each batch.
- No tracked file written, no commit.
