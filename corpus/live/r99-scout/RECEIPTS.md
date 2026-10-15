# r99-scout receipts — headless in-engine audio lattice (Godot 4.7.2, `--headless`, Dummy driver)

Launch shape for every canonical receipt:

```
godot --headless --path proj --script res://audio_lattice.gd -- --arm=<cell>
```

`timeout -s KILL 40` (canonical) / `60` (loadtest). stdout/stderr split into
`runs/r99_<cell>.rep<N>.{out,err,rc}`; loadtest copies live in `runs/loadtest/`.
`proj/project.godot` is the byte-copy of `corpus/fixtures/project.godot`
(`8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9`).

## Canonical cells (18) — 147 receipts

| cell | reps | pinned prefix uniq | notes |
|---|---|---|---|
| `census` | 3 + 3 load | 1 | driver/mix-rate/bus/devices census |
| `bus` | 3 + 3 load | 1 | bus add/route/effect/invalid-fallback readbacks |
| `autoplay` | 3 + 3 load | 1 | autoplay timing |
| `stoppos` | 3 + 3 load | 1 | stop() zeroes the position |
| `peak_calib` | 3 + 3 load | 1 | peak dB scale vs source level |
| `mixblock` | 6 + 3 load | 1 | 128-frame quantum / 4096-frame block law |
| `advance` | 6 + 3 load | 1 | position advance under Dummy |
| `finish` | 6 + 3 load | 1 | finish transition + `finished` signal |
| `loop_degenerate` | 6 + 3 load | 1 | `LOOP_FORWARD` default-points self-termination |
| `loop_pts` | 6 + 3 load | 1 | explicit loop points wrap |
| `gen` | 6 + 3 load | 1 | generator capacity/push/skips/clear refusal (2 expected ERROR lines) |
| `gen_peak` | 6 + 3 load | 1 | generator output is mixed (live peak) |
| `poly` | 6 + 3 load | 1 | `max_polyphony` voices |
| `bus_peak` | 6 + 3 load | 1 | live vs idle bus peak |
| `p2d` | 6 + 3 load | 1 | 2D props, listener, attenuation/cutoff lattice |
| `pan_law` | 6 + 3 load | 1 | pan = clamp(x/128, ±0.5)·panning_strength |
| `gen2d` | 6 + 3 load | 1 | generator on `AudioStreamPlayer2D` (center pan −6.02 dB) |
| `pause` | 6 + 3 load | 1 | `stream_paused` freeze + `is_playing()==false` |

`runs/analyze_r99.json` (from `analyze_r99.py`): `UNSTABLE=[]` for pinned prefixes,
`CRASH_CELLS=[]`, `ERR_NONZERO=['gen']` (the two deterministic refused-`clear_buffer()`
ERROR lines only). Load window: loadavg 95.95–115.07, 16 own `yes` hogs, own-PID kill.

## Discovery probes (not rows — mechanism hunting)

| probe | arms | key receipts |
|---|---|---|
| `discover.gd` | census, advance, finish, gen, poly, bus, autoplay, p2d | `runs/disc-*.out` |
| `discover2.gd` | loop, loop_pts, pitch, pause, playpos, mixclock, gen2, poly2, drain | `runs/d2-*.out` |
| `discover3.gd` | p2d_peak, poly3, clearhold, finish2, stoppos, block | `runs/d3-*.out` |
| `discover4.gd` | finwait, peakcal, clearwait, pause2 | `runs/d4-*.out` |
| `discover5.gd` | firstread, peakcal2, skips, genconsume | `runs/d5-*.out` |
| `discover6.gd` | pan, p2dgen | `runs/d6-*.out` |
| `discover7.gd` | loop_trace, loop_short, pan_knee | `runs/d7-*.out` |
| ad-hoc | `proj/panknee*.gd`, `proj/loopdbg.gd`, `proj/p2dgen2.gd` | stdout captured in the report |

## r88-probe causal reproduction

`proj/r88_audio_repro.gd` is a copy of the r88 dead seat's `r88_probe.gd` (one added
`--fix-loop` switch). Launch shape: `godot --headless --path proj --arm audio_pos
--script res://r88_audio_repro.gd [-- --fix-loop]`.
`runs/r88-repro-verbatim.rep{1..3}` (3/3 byte-identical, 0 B stderr) reproduces the
r88-pinned row `playing=false pos=0.000 peaks=[-200.00×4]`;
`runs/r88-repro-fixloop.rep{1..6}` flip the same probe to `playing=true pos=0.096` with
live peaks (peak sample varies with mix-block phase; 2 leaked-ObjectDB WARNING lines are
r88's probe's own no-free artifact).

## Author rows

`author-rows.py.txt` (18 `ROWS` + 18 `ROWS_PREFIX` + 1 `EXPECTED_ERRORS` entry),
built by `make_author_rows.py`, verified by `verify_rows.py` against **every**
canonical + loadtest receipt with the production `classify_process`
(AST-extracted from `corpus/fixtures/run_battery.py`, segment sha256
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`):
`ROWS 147/147 accepted`, `ROWS_PREFIX 147/147 accepted`, `rejected=[]`.

## Reproduce

```
bash run_cells.sh && bash run_loadtest.sh && python3 analyze_r99.py \
  && python3 make_author_rows.py && python3 verify_rows.py
```
Expect `UNSTABLE=[]` for prefixes, `ROWS 147/147`, `ROWS_PREFIX 147/147`, `rejected=[]`.
