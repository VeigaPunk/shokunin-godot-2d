# r97-boundary receipts — SceneTree lattice attacked under quiet / 12-hog load / `--fixed-fps` 1·30·60·120

Host: `godot 4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), `--headless`, 60 tps,
`SceneTree` root class `Window`. Every launch is `timeout -s KILL 25`-bounded (the seat's
bound; never hit). **342 receipts, all `rc=0`, all stderr 0 B, no `FAIL`, no `ERROR:` line,
no `137`.**

## Probes (two files, on purpose)

| file | role | sha256 |
|---|---|---|
| `probes/r97b_lattice.gd` | frozen attack probe, 6 arms — the revision behind the **324**-receipt matrix | `f37961f879c5b75ae6f46ce1c4ec5fce0109e314a8488b41ab8712c8d1ca9d52` |
| `probes/r97b_extra.gd` | secondary probe, 2 arms (`order_churn`, `unique_boundary`) — **18** receipts | `c801556147ae29d6e72945cc7a95763ac93c476080993f5f70edd75ce2228339` |
| `proj/stree_lattice.gd` | the **frozen r97-scout probe**, byte-identical to `corpus/live/r97-scout/probes/stree_lattice.gd` | `4dd18e10e84f0da289688ea384f4029056cd2da7eeed32eeaa5d11f6e34a2c45` |
| `proj/project.godot` | launch project, byte-copy of `corpus/fixtures/project.godot` | `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` |

The two own probes are kept in **separate files** so that every matrix receipt can be traced
to one frozen revision (the r94 boundary evidence defect — receipts predating the frozen
probe — is not repeated). `proj/` also carries `scene_a.tscn`, `scene_b.tscn`,
`scene_marker.gd` (byte-copies of the r97-scout launch project) so the scout's
`scene_probe` cell runs unchanged.

## Cells per mode (54 per mode × 6 modes)

| tag | script | arm | flags |
|---|---|---|---|
| `r97b_order_ticks` | `r97b_lattice.gd` | `order_ticks` | — |
| `r97b_order_priority` | `r97b_lattice.gd` | `order_priority` | — |
| `r97b_defer_capture_order` | `r97b_lattice.gd` | `defer_capture_order` | — |
| `r97b_defer_phase` | `r97b_lattice.gd` | `defer_phase` | — |
| `r97b_frame_shape` | `r97b_lattice.gd` | `frame_shape` | — |
| `r97b_phys_await` | `r97b_lattice.gd` | `phys_await` | — |
| `scout_census` | `stree_lattice.gd` | `census` | — |
| `scout_group_order` | `stree_lattice.gd` | `group_order` | — |
| `scout_group_order_rev` | `stree_lattice.gd` | `group_order` | `--rev` |
| `scout_group_flags` | `stree_lattice.gd` | `group_flags` | — |
| `scout_group_lifecycle` | `stree_lattice.gd` | `group_lifecycle` | — |
| `scout_group_setters` | `stree_lattice.gd` | `group_setters` | — |
| `scout_signal_order` | `stree_lattice.gd` | `signal_order` | — |
| `scout_signal_flags` | `stree_lattice.gd` | `signal_flags` | — |
| `scout_defer_ladder` | `stree_lattice.gd` | `defer_ladder` | — |
| `scout_defer_slots` | `stree_lattice.gd` | `defer_slots` | — |
| `scout_defer_order` | `stree_lattice.gd` | `defer_order` | — |
| `scout_scene_probe` | `stree_lattice.gd` | `scene_probe` | — |

Modes (`runs/<mode>/`): `quiet` (60 tps, no seat hogs), `load` (60 tps + **12 own `yes`
hogs**, PID-tracked, `own_hogs_killed=12`), `ff30`, `ff60`, `ff120`, `ff1`
(`--fixed-fps N`). 3 reps per cell. `runs/<mode>/hogs.txt` records the load averages and the
hog PIDs; `hogs_extra.txt` does the same for the secondary batches
(`runs/{quiet,ff60,load}/r97b_order_churn.*` + `r97b_unique_boundary.*`).

## Stability

- **Within a mode**: every `scout_*` cell is byte-stable (`out_uniq=1 err_uniq=1
  pass_uniq=1 rc=[0] errB=[0]`). Four own cells carry host-coupled counts by design
  (`p1_phys_n`, `n_phys`, `phys_per_frame`, `await_seq`/`await_dpf`) — the law-bearing keys
  are stable; see `runs/analyze_r97b.json` buckets (`LAW`/`HOST`/`MODE`/`BOTH`).
- **Across modes**: 12/12 `scout_*` cells are byte-identical in all six modes
  (`runs/analysis.txt`, `=== cross-mode: scout cells vs quiet ===`).
- **Row replay**: the production `classify_process` (AST-extracted from
  `corpus/fixtures/run_battery.py`, segment sha `749fa0607e7707e6…`) classifies the scout's
  `ROWS` and `ROWS_PREFIX` against 36 receipts per mode → **216/216 accepted each,
  `rejected=[]`**.

## Reproduce

```
bash run_modes.sh quiet 3 && bash run_modes.sh load 3 && bash run_modes.sh ff30 3 && \
bash run_modes.sh ff60 3 && bash run_modes.sh ff120 3 && bash run_modes.sh ff1 3 && \
bash run_extra.sh quiet 3 && bash run_extra.sh ff60 3 && bash run_extra.sh load 3 && \
python3 analyze_r97b.py
```

## Host cleanup

All launches `timeout -s KILL 25`-bounded; none hit. The two `load` batches started 12 own
`yes` hogs each and killed exactly those PIDs (`own_hogs_killed=12` twice). No seat-owned
godot process left running (the only godot processes at session end belong to other lanes:
g3d `r93` battery, `r96b_phase`, `r90-author`). No tracked file written, no commit.
