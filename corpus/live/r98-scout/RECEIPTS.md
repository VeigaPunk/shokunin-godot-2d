# r98-scout receipts — CanvasItem draw/transform lattice (15 cells)

Host: `godot 4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), `--headless`, `RendererDummy`,
default 60 physics ticks/s, root viewport 64x64 in `--script` mode. Every launch is
`timeout -s KILL`-bounded (30 s; none hit); no run was left running.

## Probe revisions (under `probes/`)

| file | role |
|---|---|
| `probes/discover.gd` | discovery micro-probe (15 arms: census, queue timing, draw surface, legality contexts, visibility chain, clip, z-order, modulate, transform/skew, notifications, redraw triggers, canvas transforms) — `runs/disc/d_*.{out,err}` |
| `probes/canvas_lattice.gd` | **frozen primary probe** (15 arms) — canonical receipts under `runs/r98_canvas_*.{out,err,rc}` |
| `probes/skewchk.gd`, `showchk.gd`, `trigchk.gd`, `late.gd`, `late2.gd`, `ablate.gd`, `minimal.gd`, `bisect.gd` | focused falsification ladders for the context-dependent redraw finding (see report §4/§7 F12–F14); 2 reps each under `runs/ladder/` |
| `probes/sigs.gd`, `consts.gd` | ClassDB signature/constant dumps (report-only) |

`probes/canvas_lattice.gd` sha256 `866480a1aaa0a385ad5a0e56a3066af4e5341db2e4ab5a5963366aef949394f0`
— frozen before the first canonical launch and byte-identical to `proj/canvas_lattice.gd`.

## Canonical cells (84 runs, all rc=0)

| cell | arm | reps | receipts |
|---|---|---|---|
| r98_canvas_census | census | 3 | `runs/r98_canvas_census.rep{1..3}.*` |
| r98_canvas_modulate | modulate | 3 | `runs/r98_canvas_modulate.rep{1..3}.*` |
| r98_canvas_queue | queue | 6 | `runs/r98_canvas_queue.rep{1..6}.*` |
| r98_canvas_draw_surface | draw_surface | 6 | `runs/r98_canvas_draw_surface.rep{1..6}.*` |
| r98_canvas_draw_refusal | draw_refusal | 6 | `runs/r98_canvas_draw_refusal.rep{1..6}.*` |
| r98_canvas_vis_chain | vis_chain | 6 | `runs/r98_canvas_vis_chain.rep{1..6}.*` |
| r98_canvas_clip | clip | 6 | `runs/r98_canvas_clip.rep{1..6}.*` |
| r98_canvas_zorder | zorder | 6 | `runs/r98_canvas_zorder.rep{1..6}.*` |
| r98_canvas_xform_skew | xform_skew | 6 | `runs/r98_canvas_xform_skew.rep{1..6}.*` |
| r98_canvas_xform_mirror | xform_mirror | 6 | `runs/r98_canvas_xform_mirror.rep{1..6}.*` |
| r98_canvas_xform_global | xform_global | 6 | `runs/r98_canvas_xform_global.rep{1..6}.*` |
| r98_canvas_notify | notify | 6 | `runs/r98_canvas_notify.rep{1..6}.*` |
| r98_canvas_draw_state | draw_state | 6 | `runs/r98_canvas_draw_state.rep{1..6}.*` |
| r98_canvas_redraw_triggers | redraw_triggers | 6 | `runs/r98_canvas_redraw_triggers.rep{1..6}.*` |
| r98_canvas_redraw_context | redraw_context | 6 | `runs/r98_canvas_redraw_context.rep{1..6}.*` |

`runs/rc-summary.txt` records the driver's per-cell rc vectors + host line.
`runs/analyze_r98.json` / `runs/analyze_r98.txt` — **`UNSTABLE=[]`, `CRASH_CELLS=[]`**,
every cell `out_uniq=1 err_uniq=1 pass_uniq=1 rc=[0]`.

stderr bytes: **0 B for 13 of 15 cells**; `clip` 272 B (one expected
`Condition "p_clip_mode >= CLIP_CHILDREN_MAX"` ERROR per run) and `draw_refusal` 637 B
(two expected `Drawing is only allowed inside…` ERRORs per run) — both allowlisted in
`author-rows.py.txt` `EXPECTED_ERRORS`.

## Loadtest receipts (45 runs, load avg 74–86, 8 own `yes` hogs)

`runs/loadtest/r98_canvas_*.rep{1..3}.{out,err,rc}` + `runs/loadtest/rc-summary.txt`
(per-cell load avg + own-hog accounting). Only this seat's own hog PIDs were killed
(`own_hogs_killed=8`; no `pkill`/foreign kills). `analyze_r98.txt`:
**`LOADTEST_UNSTABLE=[]`, `LOADTEST_CRASH_CELLS=[]`** — every cell single-valued ×3.

## Row verification

`python3 verify_rows.py` classifies every row against **every** canonical + loadtest
receipt (stdout+stderr merged like `run_process`) with the production `classify_process`
(AST-extracted from `corpus/fixtures/run_battery.py`, segment sha256 `749fa060…` — the
same segment r89/r90/r91/r95 pinned):

- **`ROWS` (full-line): 129/129 receipts accepted, `rejected=[]`**
- **`ROWS_PREFIX` (gating): 129/129 accepted, `rejected=[]`**
- `EXPECTED_ERRORS`: two exact engine lines (draw_refusal, clip); no other cell emits
  `ERROR:`, `SCRIPT ERROR:` or `Parse Error:` anywhere.

Reproduce: `bash run_cells.sh && bash run_loadtest.sh && python3 analyze_r98.py &&
python3 make_author_rows.py && python3 verify_rows.py` (expect `UNSTABLE=[]`,
`LOADTEST_UNSTABLE=[]`, `ROWS 129/129`, `ROWS_PREFIX 129/129`, `rejected=[]`).
