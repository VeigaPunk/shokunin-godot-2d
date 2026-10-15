# r88-critic receipts (seat-owned scratch)

All paths relative to `corpus/live/r88-critic/`. Nothing here is committed;
nothing tracked was written. Every godot launch was bounded
(`timeout -s KILL 20`); every hog batch was bounded and reaped (0 stray
`yes`/`godot` at seat exit).

## Layout

| path | what it is |
|---|---|
| `run_arms.py` | seat runner: fresh arm executions in the battery's exact launch shape (`--path proj --script res://<s> -- --arm=<a>`), sequential or `--concurrent K`, optional `--load N` (`yes` hogs) |
| `proj/` | scratch project (`project.godot` copy + probe copies; sha256s in `logs/probe-shas.txt`) |
| `runs/<tag>/` | per-run `.out/.err/.rc/.wall` (rc+wall not written for `--concurrent` batches; the runner prints rc per process) |
| `full1/` | full 215-row battery on the committed tree (`20261015T183307178445Z/verdicts.json`) |
| `gate/mutfix/` | fixtures copy with the floor-gate mutation (`spr.frame = 3` → `= 1`, in-bounds, no ERROR) |
| `gate/runs-mut/` | full 215-row battery on the mutated copy — FAIL, gate fires |
| `logs/` | runner logs, probe shas, battery stdout/stderr |

## Key tags

| tag | protocol | headline |
|---|---|---|
| `load6` | 8 arms × 6, `--load 20` | 48/48 rc=0; 8/8 pins byte-identical 6/6 |
| `conc_lb4` | 4-way concurrent `mp_loopback` | 2/4 contaminated (`rc=[20,0]`), fixture still prints PASS |
| `conc_sp3`, `conc_sp3b`, `sp2_r1..r4` | 3-way / 2-way concurrent `mp_spawner` (+instrumented copy) | every loser contaminated at `bound_hit=291..297`; child provenance = the winner's `SpawnableOne` |
| `mode_quiet`, `quiet_real` | author's file, mode probe + real arms | Case B (74.5675 / 118.4614) 8/8 + 3/3 |
| `strip_quiet`, `striplight` | author's EXACT arm code in minimal files | Case A 6/6 (66.5952) and 4/4 (107.9190) |
| `min_quiet`, `min_load31`, `minbig_quiet` | minimal arm shape; +600 unused funcs; under 31 hogs | A 6/6; bimodal 3A/3B; inflated 4/4 B |
| `audio_vac` | `p.play()` removed | pinned payload still matches 2/2 |
| `audio_ack` | post-play ack + 20-frame timeline, `--load 24` | ack=true 6/6; flip f7/f8; f20 false 6/6 |
| `phys_quiet/load/c1..c3` | phys_peer, quiet → 8-way concurrent under load | 50/50 `ev_step_delta=0` |
| `phys_x1..x5` | phys_peer 12-way concurrent, `--load 32` | 60 runs: delta 0:29, 1:15, 2:8, 3:6, 4:2 |
| `sp_load31` | mp_spawner ×6, `--load 31` | wall 2.60–2.75 s, pins identical |
| `arms/overlap.*`, `arms/ovl_c*` | overlap_probe after its mut-run failure | 22/22 PASS (one FAIL was the known r69 class) |

## Reproduce

```
cd corpus/live/r88-critic
python3 run_arms.py --tag load6 --arms mp_offline,mp_loopback,mp_spawner,light_props,sprite_meta,sprite_phys,audio_pos,vis_not --reps 6 --load 20
python3 run_arms.py --tag conc_lb4 --arms mp_loopback --concurrent 4
python3 run_arms.py --tag conc_sp3 --arms mp_spawner --concurrent 3
python3 run_arms.py --tag mode_quiet --arms mode --reps 8 --script r88_mode.gd
python3 run_arms.py --tag strip_quiet --arms x --reps 6 --script r88_strip.gd
python3 run_arms.py --tag minbig_quiet --arms run --reps 4 --script r88_min_big.gd
python3 run_arms.py --tag audio_vac --arms audio_pos --reps 2 --script r88_neg.gd
python3 run_arms.py --tag phys_x1 --arms phys_peer --concurrent 12 --load 32 --script input_lattice.gd
```

Full batteries (bounded, ~4 min each):

```
timeout -s KILL 900 python3 -B corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs corpus/live/r88-critic/full1
timeout -s KILL 900 python3 -B corpus/live/r88-critic/gate/mutfix/run_battery.py --godot /usr/bin/godot --runs corpus/live/r88-critic/gate/runs-mut
```

## Host context

- Host load during the review: 2.9–16 (battery windows), ~40 during the
  `phys_x*` oversubscription window; 32 cpus.
- A concurrent `r88-simplifier` battery ran from the same repo during the
  review (`corpus/live/r88-simplifier/runs-before/…`, `pgrep` logged at
  18:33Z; its MP rows completed before `full1` started).
- `full1` load window: ~10 (own hogs included).
