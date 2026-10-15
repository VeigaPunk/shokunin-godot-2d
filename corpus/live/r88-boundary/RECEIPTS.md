# r88 BOUNDARY seat — RECEIPTS

Seat `BOUNDARY` (LEAF) | lane `r88-boundary` | round 88 | host **devin**.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`d15c54d`**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, `--headless`,
GodotPhysics2D, 60 tps, `DisplayServer.get_name()=="headless"`, `audio_driver=Dummy`,
`render=vulkan`/`forward_plus` with an empty device list, root viewport `64x64`).

**No git mutation, no tracked file written, no commit.** Writes are
`corpus/live/r88-boundary/**` and `reports/round-88/r88-boundary.md` (new, untracked).
The concurrent author lane's in-flight `corpus/fixtures/run_battery.py` (+42 lines) and
`corpus/fixtures/r88_{surfaces.gd,spawnable.tscn}` are **not** this seat's and are not
touched here.
The frozen-probeParent depth-2 `ufo-labrat` was dispatched exactly once; it reports it has
**no exec/write tooling** (read-only seat) and produced zero data — see the report §6.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server
installed; all claims are carried by fresh-process execution receipts and engine-emitted
error text, never by source reading.

## Layout

```
proj/project.godot     unique name "R88BoundarySeat" (no physics overrides)
proj/b88_mp.gd         MP loopback edges: mp_lb, mp_names, mp_cycles, mp_genid, mp_offline
proj/b88_light.gd      hang_min, fixed, fixed_sync, control
proj/b88_audio.gd      timeline (per-frame playing/pos/peak under Dummy)
proj/b88_vis.gd        base, variants (huge rect/camera/SubViewport), forcedraw
proj/b88_sprite.gd     oob0/1/2/3/neg, phys, fall, fall_anchor, fall_sync, meta
run_boundary.py        the battery runner (fresh process per run)
analyze_boundary.py    per-tag stability table (rc/wall/uniq/ERROR counts/normalized uid)
runs/                  all .out/.err/.rc/.wall receipts + analysis.txt
```

Launch shapes (every run is one fresh process under `timeout -s KILL 25`):

- own probes: `godot --headless --path proj --script res://<probe> -- --arm=<arm> [--port=] [--delay=]`
  (arm parsed from `OS.get_cmdline_user_args()`, battery convention; prints `R88B arm=` first;
  `ARM_MISSING` + rc=1 if the arm is absent — the scout's directive 9).
- scout verbatim: `godot --headless --path ../r88-scout/proj --script res://r88_probe.gd --arm <arm>`
  (`r88_probe_fix.gd` for the repaired light leg), because that script reads `OS.get_cmdline_args()`.

**Timeout semantics.** `timeout -s KILL 25` SIGKILLs the timed-out process, so a hung run
reports **rc = -9** to Python (137 in bash) at **wall = 25.00 s**; the `124` of the scout's
`timeout 60` was the default TERM. Same hang class, different signal. No run left a child
behind (`pgrep -af r88-boundary` empty at exit; the 32-core host also carried other lanes).

## Battery — 132 fresh processes across 32 tags, every rc=0 except the hang arms

(The two `fixed_sync` tags in the table below were added after the main battery and run
separately, 6 more processes; the current `PLAN` reproduces 138 runs.)

| tag | probe.arm | reps | rc | payload stability | supports |
|---|---|---|---|---|---|
| b88_mp.mp_lb | own mp_lb | 6 | 0×6 | raw 6, **uid-normalized 1** | claims 1,2 |
| b88_mp.mp_names | own mp_names | 3 | 0×3 | raw 3, **norm 1** | claim 2 (name/order invariance) |
| b88_mp.mp_cycles | own mp_cycles | 3 | 0×3 | raw 3, **norm 1** (10 cycles each) | claim 2 |
| b88_mp.mp_genid | own mp_genid | 3 | 0×3 | random samples (expected) | claim 1 (normalization tail) |
| b88_mp.mp_offline | own mp_offline | 3 | 0×3 | 1 | claim 1 sibling |
| b88_light.hang_min | own hang_min | 3 | **-9×3** (25.00 s) | 1 out, 1 err (SERR=1) | claim 3 (hang class) |
| b88_light.fixed | own fixed | 6 | 0×6 | 1 (Case A) | claim 3 |
| b88_light.fixed_sync | own fixed_sync | 3 | 0×3 | 1 (guard=1, 118.4614) | claim 3 (recipe) |
| b88_light.fixed_sync_delay | own fixed_sync --delay=200 | 3 | 0×3 | 1 (guard=1, 118.4614) | claim 3 (recipe) |
| b88_light.control | own control | 3 | 0×3 | 1 | claim 3 (non-vacuity) |
| b88_audio.timeline | own timeline | 6 | 0×6 | **2** (flip f9 ×5, f10 ×1) | claim 4 |
| b88_vis.base | own base | 6 | 0×6 | 1 | claim 4 |
| b88_vis.variants | own variants | 3 | 0×3 | 1 | claim 4 |
| b88_vis.forcedraw | own forcedraw | 3 | 0×3 | 1 | claim 4 |
| b88_sprite.oob0/1 | own oob0,oob1 | 3+3 | 0×6 | 1 each, ERR=0 | claim 5 |
| b88_sprite.oob2 | own oob2 | 3 | 0×3 | 1, ERR=1 | claim 5 |
| b88_sprite.oob3 | own oob3 | 6 | 0×6 | 1, ERR=1 | claim 5 |
| b88_sprite.oobneg | own oobneg | 3 | 0×3 | 1, ERR=1 | claim 5 |
| b88_sprite.phys | own phys | 6 | 0×6 | 1 (Case A 66.5952), ERR=1 | claims 5, 2-race |
| b88_sprite.fall | own fall | 3 | 0×3 | 1 (Case A, 59:466.6694) | race |
| b88_sprite.fall_delay | own fall --delay=200 | 3 | 0×3 | 1 (Case B, 59:482.2250) | race proof |
| b88_sprite.fall_anchor[_delay] | own fall_anchor | 3+3 | 0×6 | 1 each, but A≠B values | race |
| b88_sprite.fall_sync[_delay] | own fall_sync | 3+3 | 0×6 | **1 across both** (124.5675) | race recipe |
| b88_sprite.meta | own meta | 3 | 0×3 | 1 | sprite metadata |
| verbatim.light_props_hang | r88_probe.gd light_props | 3 | **-9×3** (25.00 s) | 1 out, 1 err | claim 3 |
| verbatim.light_props_fix | r88_probe_fix.gd light_props | 6 | 0×6 | 1 (Case B, 118.4614) | claim 3 |
| verbatim.rb_gravity | r88_probe.gd rb_gravity | 6 | 0×6 | 1 (Case B, 124.5675/482.2250) | race |
| verbatim.sprite_phys | r88_probe.gd sprite_phys | 6 | 0×6 | 1 (Case B, 74.5675), ERR=1 | claims 5, race |
| verbatim.mp_loopback | r88_probe.gd mp_loopback | 6 | 0×6 | raw 6, **norm 1** | claims 1,2 |
| verbatim.audio_pos | r88_probe.gd audio_pos | 6 | 0×6 | 1 | claim 4 |
| verbatim.vis_not | r88_probe.gd vis_not | 6 | 0×6 | 1 | claim 4 |

## Stress / edge protocols (manual, same fresh-process + `timeout -s KILL 25` shape)

| cells | what | result |
|---|---|---|
| `runs/stress_audio.rep0..7` | 8 **concurrent** audio timelines | all rc=0; `playing=false` at f19 in 8/8; flip frame spread f6..f13 |
| `runs/stress_fall.rep0..7` | 8 **concurrent** small-probe falls | all rc=0; **8/8 Case B** (59:482.2250) |
| `runs/seq_fall.rep0..2` | 3 sequential falls after the stress | **B, A, B** (466.6694 / 482.2250 both observed) |
| `runs/stress_mp_distinct.rep0..5` | 6 concurrent mp_lb, distinct ports | all rc=0, `rc=[0,0]`, frames=4 wait=1 — counters stable under load |
| `runs/stress_mp_same.rep0..2` | 3 concurrent mp_lb, **same port 42050** | 1 winner (full pin); 2 losers `rc=[20,0]`, order truncated to 2, `limb_s=[]`, frames=600 wait=600 — silent cross-process contamination, rc still 0 |

## Reproduce

```bash
cd corpus/live/r88-boundary
python3 run_boundary.py                 # 132 runs, ~4 min (six 25 s hang arms)
python3 run_boundary.py --only <tag> --reps N [--extra "--delay=200"]
python3 analyze_boundary.py > runs/analysis.txt
```

`runs/analysis.txt` is the frozen per-tag table (rc vector, wall range, out/err uniq,
uid-normalized uniq, ERROR counts, and every distinct payload for unstable tags).
`manifest.sha256` covers every artefact in this directory plus the report.
