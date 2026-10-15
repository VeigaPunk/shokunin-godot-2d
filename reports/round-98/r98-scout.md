# game-dev-2d round 98 — scout (r98-scout): the CanvasItem draw/transform lattice, pre-measured; 15 rows verbatim-ready

Seat `SCOUT` (LEAF; frozen `probeParent` — one labrat dispatch, **completed**, §9) | lane
`r98-scout` | round 98 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
`RendererDummy` (headless has no rendering server), default 60 physics ticks/s, root
viewport 64×64 in `--script` mode. Repo `~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at
session start **`2c4b1ff`** (*r94 scout*), HEAD at session end **`61355e2`** (*r89 reviewer* —
concurrent lanes committed while this seat ran; none of those commits touch this seat's
artefacts). The launch `project.godot` is the byte-copy of `corpus/fixtures/project.godot`
(`8de8b3af…`).

**No git mutation, no tracked file written, no commit.** Writes are this report and
`corpus/live/r98-scout/**` only; `git status --porcelain` shows exactly one new path
(`?? corpus/live/r98-scout/`) plus this report. The only tracked modification in
`git status` is a **concurrent lane's** `corpus/fixtures/run_battery.py` (+74 lines, the
r90 `rb_lattice` block, zero `r98`/`canvas_lattice` tokens) — this seat never touched it,
and no tracked file under `corpus/fixtures/` was written by this seat (the probe was
never copied there).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on
this host; `definition`/`references`/`hover` were **unavailable for every file touched**.
All symbol/API knowledge below comes from runtime `ClassDB` introspection inside the probes
(`census`/`sigs`/`consts` arms) and from the engine's own error text — never from engine
source (none on this host). Every mechanism statement is marked **[I]** and kept separate
from the measurements.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Primary: the `CanvasItem` draw/transform lattice** — `queue_redraw()` timing and
coalescing; the `draw_*` primitive surface and its **legal call contexts**
(`_draw` / `NOTIFICATION_DRAW` / `draw` signal) including the engine's refusal path;
`Node2D` transform/skew decomposition (`Transform2D` matrix convention, global
readbacks, mirrors, non-uniform parents, zero scale, global setters, `translate`/
`apply_scale`, normalisation); `z_index`/`z_as_relative`/`y_sort_enabled`/
`show_behind_parent` readback semantics and the **headless draw-notification order**;
`modulate`/`self_modulate` readback semantics; the visibility chain (ancestor
inheritance, signals, draw suppression); `clip_children` readbacks and refusals;
`CanvasItem` transform notifications and canvas re-entry.

Why this surface **[O]/[I]**:

- The battery has **no row** that touches `queue_redraw`, `_draw`, any `draw_*`
  primitive, `z_index`, `skew`, `clip_children`, or `modulate` (the only `modulate`
  mention in `corpus/fixtures/*.gd` is `tween_flash.gd` tweening a *value*). The
  CanvasItem-internal draw/transform machinery is a clean coverage gap on the most
  author-facing 2D class there is.
- It is adjacent to, but disjoint from, the surfaces already pinned: r85 owns the
  **camera/CanvasLayer/canvas-space** transforms and the CanvasLayer-level draw order
  (`cl_draworder`: layer notifications are creation-ordered, not layer-sorted); r88 owns
  the visibility notifier; r94 owns particle visibility pause; r92/r93/r95/r97 are
  sibling seats this wave. This round is the **item-level** side of the same world.
- **Falsifiability was immediate.** The first discovery pass refuted five of the
  scout's own first-pass assumptions: (a) "draw calls are only legal inside `_draw()`"
  — there are three legal contexts; (b) "transform writes never queue a redraw" — false
  in a measurable context (§3.14, §7 F12); (c) "`z_index` orders draws" — the headless
  draw order is queue/creation order and never z-sorted; (d) "an invalid `clip_children`
  value clamps" — it is refused with an ERROR and keeps the old value; (e) "a negative
  `clip_children` is rejected" — it is stored as its uint32 cast.
- Everything pinned here is reachable from GDScript under `--headless` (no rendering
  server needed) — but the *rendered* output is not: see §8.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` (15 arms, fresh process each) | feasibility: draw timing, draw surface + contexts, visibility, clip, z-order, modulate, transform/skew, notifications, redraw triggers | `runs/disc/d_*.{out,err}` |
| 2 | focused ladders (`skewchk`/`showchk`/`trigchk`/`late`/`late2`/`ablate`/`minimal`/`bisect`, 2 reps each) | falsification of the context-dependent redraw finding (isolation + ablation + minimal sequence) | `runs/ladder/*.{out,err,rc}` |
| 3 | `bash run_cells.sh` | **15 cells** (2 pure ×3, 13 frame-bound ×6) = **84 runs** | `runs/r98_canvas_*.{out,err,rc}` |
| 4 | `python3 analyze_r98.py` | per-cell reps / out_uniq / err_uniq / rc / PASS-line uniqueness + common prefix | `runs/analyze_r98.json`, `runs/analyze_r98.txt` |
| 5 | `HOGS=8 REPS=3 bash run_loadtest.sh` | **45 runs** over all 15 cells, load avg 74–86 | `runs/loadtest/` |
| 6 | `python3 make_author_rows.py` → `verify_rows.py` | 15 rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) | `author-rows.py.txt` |

**160 retained receipts** (84 canonical + 45 loadtest + 15 discovery + 16 ladder) plus
~60 transient smoke/first-pass launches that were not retained. Every run
`timeout -s KILL`-bounded (30 s; none hit), no run left running
(`pgrep -fa canvas_lattice` → none).

**Byte-stability [M]: 15 of 15 cells are `out_uniq=1 err_uniq=1 pass_uniq=1 rc=[0]`**
(`runs/analyze_r98.json`: `UNSTABLE=[]`, `CRASH_CELLS=[]`), including every cell whose
PASS line carries frame numbers, float matrices or a signal-delta vector.

**Load-stability [M]:** re-running all 15 cells ×3 at load avg 74–86 (8 own `yes` hogs on
a host already ~65–75 from other lanes) gave **45/45 rc=0**, `LOADTEST_UNSTABLE=[]`,
`LOADTEST_CRASH_CELLS=[]`, and **zero row rejections** — `verify_rows.py` → `ROWS`
**129/129 accepted**, `ROWS_PREFIX` **129/129 accepted**, `rejected=[]`.

**stderr discipline [M]:** 13 of 15 cells emit **0 B stderr**; `clip` emits one expected
`Condition "p_clip_mode >= CLIP_CHILDREN_MAX"` ERROR per run and `draw_refusal` two
expected `Drawing is only allowed inside…` ERRORs per run — both allowlisted in
`author-rows.py.txt` `EXPECTED_ERRORS`. No other cell emits `ERROR:`, `SCRIPT ERROR:` or
`Parse Error:`.

**Arm-dispatch integrity [O]:** every arm prints its own name on the `PASS` line
(`PASS canvas_lattice <arm> …`), parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan), so a silent `_:` fallback is
impossible to miss.

**Delegated probe [O]:** the frozen probeParent dispatched exactly one read-only
`ufo-labrat` seat (receipt-level audit of PASS stability, key traceability and law L1);
it completed and its report is summarised in §9.

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| **API census** (props, draw methods, signatures, constants, defaults, absence of getters) | **PINNABLE** | 3 | uniq=1 |
| **`queue_redraw` timing ladder** (same-frame flush, coalescing, self-queue swallow, hidden/out-of-tree suppression, show/re-add redraw) | **PINNABLE law** | 6 | uniq=1 |
| **`draw_*` surface** (32 primitives callable in `_draw`, canvas RID, draw-state isolation) | **PINNABLE** | 6 | uniq=1 |
| **Legal draw contexts + refusal** (`_draw`/`NOTIFICATION_DRAW`/`draw` signal vs. elsewhere) | **PINNABLE law + hazard** | 6 | uniq=1 (expected ERROR) |
| **Visibility chain** (ancestor inheritance, per-toggle signal/notification counts, draw suppression) | **PINNABLE law** | 6 | uniq=1 |
| **`clip_children`** (enum readbacks, `>= MAX` refusal, negative uint32 cast) | **PINNABLE law + hazard** | 6 | uniq=1 (expected ERROR) |
| **Z-order observables** (local readbacks; notification order is queue/creation order, never z-sorted) | **PINNABLE law (order unreadable visually)** | 6 | uniq=1 |
| **Modulation** (local readbacks, independence, no clamping, no effective-modulate getter) | **PINNABLE; effective composition NOT readable** | 3 | uniq=1 |
| **Transform/skew convention** (`R·K·S·T`, ctor equivalence, skew basis) | **PINNABLE law** | 6 | uniq=1 |
| **Mirror / non-uniform parent / zero scale** | **PINNABLE law + hazard** | 6 | uniq=1 |
| **Global setters + `translate`/`apply_scale`/normalisation/`top_level`** | **PINNABLE law** | 6 | uniq=1 |
| **Transform notifications + canvas re-entry** | **PINNABLE law** | 6 | uniq=1 |
| **Draw state vs node transform + canvas spaces** | **PINNABLE** | 6 | uniq=1 |
| **Redraw triggers (clean context)** | **PINNABLE table** | 6 | uniq=1 |
| **Redraw triggers (context-dependent)** | **PINNABLE falsification** | 6 | uniq=1 |
| **Rendered output / effective z order / effective modulate** | **NOT READABLE HEADLESS** | — | — |

---

## 3. Measured values, verbatim

All payloads are `runs/r98_canvas_<cell>.rep1.out`; matrices are `(xx,xy;yx,yy;ox,oy)`
at `%.4f`. No RIDs/object ids are printed anywhere.

### 3.1 Census (`census`) — [M]

```
PASS canvas_lattice census consts=NOTIFICATION_DRAW=30,NOTIFICATION_VISIBILITY_CHANGED=31,
  NOTIFICATION_ENTER_CANVAS=32,NOTIFICATION_EXIT_CANVAS=33,NOTIFICATION_TRANSFORM_CHANGED=2000,
  NOTIFICATION_LOCAL_TRANSFORM_CHANGED=35,CLIP_CHILDREN_DISABLED=0,CLIP_CHILDREN_ONLY=1,
  CLIP_CHILDREN_AND_DRAW=2,CLIP_CHILDREN_MAX=3,TEXTURE_FILTER_PARENT_NODE=0,
  TEXTURE_REPEAT_PARENT_NODE=0,OVERSAMPLING_WITH_SCALE_PARENT_NODE=0
  props=Visibility,visible,modulate,self_modulate,show_behind_parent,top_level,clip_children,
  oversampling_with_scale,light_mask,visibility_layer,Ordering,z_index,z_as_relative,
  y_sort_enabled,Texture,texture_filter,texture_repeat,Material,material,use_parent_material
  draw_n=32
  sigs=draw_ellipse_arc(center:5,major:3,minor:3,start_angle:3,end_angle:3,point_count:2,color:20,width:3,antialiased:1)|
       draw_rect(rect:7,color:20,filled:1,width:3,antialiased:1)|
       draw_string(font:24,pos:5,text:4,alignment:2,width:3,font_size:2,modulate:20,justification_flags:2,direction:2,orientation:2,oversampling:3)|
       draw_mesh(mesh:24,texture:24,transform:11,modulate:20)|
       draw_set_transform(position:5,rotation:3,scale:5)|draw_set_transform_matrix(xform:11)|
       draw_animation_slice(animation_length:3,slice_begin:3,slice_end:3,offset:3)
  defaults=z=0,zrel=1,ysort=0,behind=0,light=1,vislayer=1,clip=0,oversample=0,texfilter=0,texrepeat=0
  has_pivot=0 has_global_modulate=0 has_global_z=0 rs_getters=3 notify_default=0 local_notify_default=0
```
(line wrapped for print; the receipt is one line)

- `CanvasItem` exposes exactly **32 `draw_*` methods** on this build **[M]**.
- **There is no pivot on `CanvasItem`/`Node2D`** (`has_pivot=0`; `_edit_get_pivot()`
  returns `(0,0)` — an editor helper, §3.11). Pivot is a `Control` property.
- **There is no effective-modulate or effective-z getter** (`has_global_modulate=0`,
  `has_global_z=0`); the only `RenderingServer` `canvas_item_get*` methods are the three
  instance-shader-parameter getters (`rs_getters=3`) **[M]** — this is the boundary that
  makes effective composition/ordering unreadable headless (§8).
- `draw_set_transform` takes **(position, rotation, scale) — no skew parameter**; a
  skewing draw transform requires `draw_set_transform_matrix(Transform2D)` **[M]**.
- Transform notifications are **opt-in** (`notify_default=0 local_notify_default=0`) **[M]**.
- Notification ids (dumped via `ClassDB`, report-only): `10 ENTER_TREE`, `11 EXIT_TREE`,
  `13 READY`, `17 PROCESS`, `18 PARENTED`, `19 UNPARENTED`, `27 POST_ENTER_TREE`,
  `30 DRAW`, `31 VISIBILITY_CHANGED`, `32 ENTER_CANVAS`, `33 EXIT_CANVAS`,
  `35 LOCAL_TRANSFORM_CHANGED`, `2000 TRANSFORM_CHANGED`, `2010 TRANSLATION_CHANGED`.

### 3.2 `queue_redraw` timing ladder (`queue`) — [M]

```
PASS canvas_lattice queue add_same=1 add_n=1 proc_same=1 proc_n=1 coalesce_n=1 from_draw_n=1
  hidden_n=0 show_n=1 hide_before_flush_n=0 out_n=0 readd_n=1 outadd_n=1
  events_tail=q@pf0|d@pf0|d@pf1|d@pf2|d@pf6|d@pf8|d@pf10|d@pf12
```

- **Same-frame flush:** a node added at process frame N draws at process frame N
  (`add_same=1`); a `queue_redraw()` issued from `_process` at frame N draws at frame N
  (`proc_same=1`, `events_tail` shows `q@pf0` immediately followed by `d@pf0`) **[M]**.
- **Coalescing:** three `queue_redraw()` calls in one frame produce exactly **one**
  `_draw` (`coalesce_n=1`) **[M]**.
- **Self-queue is swallowed:** `queue_redraw()` from inside `_draw()` produces **no**
  extra draw (`from_draw_n=1` = only the external queue's draw; the ladder probe
  `qtime3` recorded one draw and then silence over 3 frames) — `pending_update` is still
  set during the callback **[M]**. Authors who want a continuous redraw loop need
  `call_deferred("queue_redraw")`/a process hook, not a self-queue.
- **Hidden / out-of-tree suppression:** queueing while hidden or outside the tree draws
  nothing (`hidden_n=0`, `out_n=0`); queueing and hiding before the flush also draws
  nothing (`hide_before_flush_n=0`) **[M]**.
- **Show / re-add redraw:** becoming visible draws once (`show_n=1`); remove+re-add
  draws once (`readd_n=1`); queue-while-outside then re-add draws once (`outadd_n=1`) **[M]**.
- `events_tail` is the last 8 raw events of the frozen ladder; the frame numbers are
  deterministic for this sequence but the *law* is stated as same-frame/coalesce, not as
  a frame-number pin (the gating prefix of this cell cuts before `events_tail`).

### 3.3 `draw_*` surface + contexts (`draw_surface`) — [M]

```
PASS canvas_lattice draw_surface ok_n=33 rid=1 xform_same=1 matrix_same=1 order=nsd
```

- All **33** legal draw calls complete with **no ERROR** in `_draw`: `draw_line`,
  `draw_dashed_line`, `draw_polyline`, `draw_polyline_colors`, `draw_ellipse_arc`,
  `draw_arc`, `draw_multiline`, `draw_multiline_colors`, `draw_rect` (×2),
  `draw_circle`, `draw_ellipse`, `draw_texture`, `draw_texture_rect`,
  `draw_texture_rect_region`, `draw_msdf_texture_rect_region`,
  `draw_lcd_texture_rect_region`, `draw_style_box`, `draw_primitive`, `draw_polygon`,
  `draw_colored_polygon`, `draw_string`, `draw_multiline_string`, `draw_string_outline`,
  `draw_multiline_string_outline`, `draw_char`, `draw_char_outline`, `draw_mesh`,
  `draw_multimesh`, `draw_set_transform`, `draw_set_transform_matrix`,
  `draw_animation_slice`, `draw_end_animation` **[M]** (with an `ImageTexture` and
  `ThemeDB.fallback_font`; `draw_mesh`/`draw_multimesh`/font drawing are all accepted by
  the dummy server).
- `get_canvas_item().is_valid() == true` headless (`rid=1`) **[M]**.
- **`draw_set_transform` / `draw_set_transform_matrix` do not mutate the node
  transform** (`xform_same=1`, `matrix_same=1`) — the draw transform is separate state
  and is not readable back **[M]**.
- **Notification order inside one draw:** `NOTIFICATION_DRAW` handler → `draw` signal →
  `_draw` (`order=nsd`) **[M]**. (Discovery logged the same order; it is the reverse of
  the commonly assumed `_draw`-first order.)

### 3.4 Draw refusal (`draw_refusal`) — [M], expected ERROR

```
PASS canvas_lattice draw_refusal outside_refused=1 proc_refused=1 sig_ok=1 notif_ok=1 draws=1
```
stderr (exact, allowlisted):
```
ERROR: Drawing is only allowed inside this node's `_draw()`, functions connected to its `draw` signal, or when it receives NOTIFICATION_DRAW.
   at: draw_rect (scene/main/canvas_item.cpp:919)
```
- Drawing from a deferred arm body (`outside_refused=1`) and from `_process`
  (`proc_refused=1`) is **refused with that fixed ERROR** — and the drawing still does
  not happen **[M]**.
- Drawing from a `draw`-signal handler (`sig_ok=1`) and from a `NOTIFICATION_DRAW`
  handler (`notif_ok=1`) is **legal** — the error text names both contexts and the
  measurement confirms them **[M]**.
- This is the row that carries the `EXPECTED_ERRORS` allowlist; two identical ERROR
  lines per run.

### 3.5 Visibility chain (`vis_chain`) — [M]

```
PASS canvas_lattice vis_chain hide_in_tree=0 hide_prop=1 hide_notif=1 hide_sig=1
  hide_hidden_sig=1 hidden_queue_n=0 restore_in_tree=1 restore_n=1 child_hide_in_tree=0
  hide_noop=0 show_in_tree=1 show_notif=1 show_sig=1 draws_total=5
```

- Hiding an ancestor makes the child's `is_visible_in_tree()` false while the child's own
  `visible` property stays **true** (`hide_in_tree=0 hide_prop=1`) **[M]**.
- Each **effective** toggle emits exactly one `NOTIFICATION_VISIBILITY_CHANGED`
  (`hide_notif=1`, `show_notif=1`), one `visibility_changed` (`hide_sig=1`, `show_sig=1`)
  and one `hidden` signal on the hide edge (`hide_hidden_sig=1`) **[M]**.
- A redundant `hide()`/`show()` on an already-hidden/visible item is a **no-op**
  (`hide_noop=0`) **[M]**.
- Queueing while an ancestor is hidden draws nothing (`hidden_queue_n=0`); restoring
  visibility draws once (`restore_n=1`) **[M]**.
- `draws_total=5` is the sum over the frozen ladder (parent + child) and is stable ×6.

### 3.6 `clip_children` (`clip`) — [M], expected ERROR

```
PASS canvas_lattice clip default=0 only=1 and_draw=2 refused_stays=1 neg_cast=4294967293
  vis_layer=3 bit0=1 bit1=1 bit2=0 light=1 oversample=0
```
stderr (exact, allowlisted):
```
ERROR: Condition "p_clip_mode >= CLIP_CHILDREN_MAX" is true.
   at: set_clip_children_mode (scene/main/canvas_item.cpp:1862)
```
- Enum readbacks: `DISABLED=0`, `ONLY=1`, `AND_DRAW=2` **[M]**.
- **An out-of-range mode is REFUSED, not clamped**: setting `99` from `ONLY` leaves the
  value at `1` and emits the ERROR (`refused_stays=1`) **[M]**.
- **A negative mode is accepted and stored as its uint32 cast**: `-3` reads back
  `4294967293` with no ERROR (`neg_cast=4294967293`) **[M]** — the `>= MAX` guard is an
  int comparison, so negatives slip through into the stored enum.
- `set_visibility_layer(3)` reads back `3` with bits 0/1 set and bit 2 clear
  (`vis_layer=3 bit0=1 bit1=1 bit2=0`); `light_mask` default `1`; `oversampling_with_scale`
  default `0` **[M]**.

### 3.7 Z-order observables (`zorder`) — [M]

```
PASS canvas_lattice zorder first=ABC z_read=-5,0,5 zrel=1 parent_isolated=1
  parent_flag_isolated=1 ysort=1,0 behind=0 front_index=2 requeue=CBA
```

- Three siblings added `A(z=-5) B(z=0) C(z=5)` draw in **creation order `ABC`**, not z
  order; requeueing them in reverse draws in **queue order `CBA`** **[M]**. The headless
  draw-callback order is the message-queue order — the z/y sort lives in the renderer
  (r85 pinned the same fact one level up for CanvasLayers).
- `z_index` is a **local** readback: a parent `z_index=10` does not change the child's
  readback (`parent_isolated=1`), and setting `z_as_relative=false` on the parent does
  not change the child's flag (`parent_flag_isolated=1`) **[M]**.
- `y_sort_enabled` is **not inherited** by children (`ysort=1,0`) **[M]**;
  `show_behind_parent` default `0` **[M]**.
- `move_to_front()` moves the node to the last child index (`front_index=2`) and does
  **not** itself queue a redraw (only the explicit queue did) **[M]**.
- **No API exposes the effective z or the sorted order** (§3.1) — the sort is not
  observable headless; pin the readbacks and the notification-order law, never a visual
  order.

### 3.8 Modulation (`modulate`) — [M]

```
PASS canvas_lattice modulate defaults=1.0000,1.0000,1.0000,1.0000|1.0000,1.0000,1.0000,1.0000
  p_modulate=0.5000,1.0000,2.0000,0.2500 c_after_parent=1.0000,1.0000,1.0000,1.0000
  c_self_after_parent=1.0000,1.0000,1.0000,1.0000 c_self=0.0000,0.0000,3.0000,1.0000
  raw_neg=4.0000,-1.0000,0.5000,4.0000 hidden_same=4.0000,-1.0000,0.5000,4.0000
  getter=0 upm=0 material_null=1
```

- `modulate` and `self_modulate` are **independent local properties**: writing the
  parent's `modulate`/`self_modulate` does not change either child readback
  (`c_after_parent`, `c_self_after_parent`) **[M]**.
- **Values are not clamped or sanitised**: `Color(4,-1,0.5,4)` reads back verbatim
  (`raw_neg`), including a negative channel **[M]**.
- **The effective (composed) modulate is not readable headless** (`getter=0`); the
  documented `modulate × self_modulate` inheritance chain cannot be asserted by a
  headless row — only the local properties can (§8).
- `use_parent_material` default `0`; `material` default `null` **[M]**.

### 3.9 Transform/skew convention (`xform_skew`) — [M]

```
PASS canvas_lattice xform_skew m45=(1.0000,0.0000;-0.7071,0.7071;0.0000,0.0000)
  m90=(-0.0000,1.0000;-0.7071,-0.7071;0.0000,0.0000)
  ms=(2.0000,0.0000;-1.4383,2.6327;0.0000,0.0000) prop=0.5000 ctor=1 rks=1
```

- The local transform is **`R(rotation) · K(skew) · S(scale) · T(position)`**, with the
  skew matrix mapping the y basis to `(-sin k, cos k)` (`m45` at `k=π/4`: y =
  `(-0.7071, 0.7071)`; `m90` applies the same skew *after* a 90° rotation:
  y = `(-0.7071,-0.7071)`) **[M]**.
- `Node2D.get_transform() == Transform2D(rotation, scale, skew, position)` — the 4-arg
  constructor is the exact composition (`ctor=1`), and the explicit `R·K·S` product
  matches (`rks=1`) **[M]**.
- `skew` is stored in **radians** (`prop=0.5000` for `skew=0.5`); the inspector's degree
  hint is presentation only **[M]**.
- Note the `-0.0000` in `m90.x.x`: a signed float32 zero, deterministic on this build —
  pin it as measured or cut before it if a future build changes the sign of zero.

### 3.10 Mirror / non-uniform parent / zero scale (`xform_mirror`) — [M]

```
PASS canvas_lattice xform_mirror mx_grot=-2.0416 mx_gscale=(2.0000,-2.0000) mx_gskew=0.0000
  my_grot=1.1000 my_gscale=(2.0000,-2.0000) nu_gskew=1.3410 nu_grot_deg=42.1249
  zero_gscale=(0.000020,0.000020) zero_grot=1.1000 zero_gskew=0.0000
```

- Child local `rotation=0.4` under parent `rotation=0.7`, uniform scale 2, child
  `scale=(-1,1)`: `global_rotation = -2.0416 = 1.1 − π`, `global_scale = (2,-2)` **[M]**.
- Mirroring the other axis (`scale=(1,-1)`) leaves `global_rotation = 1.1000` exactly
  (parent+child) **[M]** — so the sign of the mirror decides the π offset.
- **A non-uniform parent scale creates shear in the child readback**:
  parent `scale=(3,0.25)` → child `global_skew = 1.3410` (child local skew is 0!) and
  `global_rotation_degrees = 42.1249` instead of the 22.92° naive sum **[M]**. Any code
  that reads back `global_rotation` under a non-uniform parent is reading a shear
  decomposition, not the angle it set.
- **A zero scale reads back as an epsilon, not 0**: child `scale=(0,0)` →
  `global_scale = (0.000020, 0.000020)` with `global_rotation` and `global_skew`
  unchanged **[M]**. `is_zero_approx()`-style guards are required; `x == 0` tests on a
  global scale are wrong.

### 3.11 Global setters + local space (`xform_global`) — [M]

```
PASS canvas_lattice xform_global gp_local=(7.0453,0.6031) grot_local_deg=11.4592
  gscale_local=(1.0000,1.0000) translate=(1.0000,0.0000) apply_scale=(2.0000,2.0000)
  norm=-1.5832 deg45=0.7854 top=(1.4142,1.4142;-1.4142,1.4142;0.0000,0.0000) top_is=1
  rel=(0.9211,0.3894;-0.3894,0.9211;0.0000,0.0000) edit_pivot=(0.0000,0.0000)
```

- Under parent `rotation=0.7 scale=(2,2)`: `global_position=(10,10)` inverse-composes to
  local `(7.0453,0.6031)`; `global_rotation=0.9` → local `11.4592°` (= 0.9−0.7);
  `global_scale=(2,2)` → local `(1,1)` **[M]**.
- **`translate(Vector2(1,0))` adds to `position` in PARENT space**, even with the node
  rotated 90° (`translate=(1.0000,0.0000)`) — it is not a rotated-local move
  (`move_local_x/y` are) **[M]**.
- `apply_scale(Vector2(2,2))` multiplies the local scale (`apply_scale=(2.0000,2.0000)`)**[M]**.
- **Local `rotation` is stored raw** (`rotation=4.0` reads back 4.0) while
  **`global_rotation` is normalised** into `[-π, π]` (`norm=-1.5832 = 4.0 − 2π + 1.1`);
  `rotation_degrees=45` stores `0.7854 rad` **[M]**.
- `top_level=true` makes global == local (`top_is=1`, matrix origin `(0,0)` with the
  frozen scale/rotation); `get_relative_transform_to_parent()` returns the parent-frame
  transform (`rel`) **[M]**.
- `_edit_get_pivot() = (0,0)` (editor helper; there is no runtime pivot on `Node2D`) **[M]**.

### 3.12 Transform notifications + canvas re-entry (`notify`) — [M]

```
PASS canvas_lattice notify defaults=0,0 move_default=[] move_default_c=[] move_p=[35,2000]
  move_c=[2000] cmove_p=[] cmove_c=[35]
  reparent=[10,11,18,19,27,30,31,32,33,2000,2010] cl_node=1
  reparent_back=[10,11,18,19,27,30,31,32,33,2000,2010] cl_node_back=0
```

- **Transform notifications are opt-in and silent by default**: with defaults, moving a
  node emits nothing (`move_default=[] move_default_c=[]`) **[M]**.
- With `set_notify_transform(true)` + `set_notify_local_transform(true)` on both:
  moving the parent emits `LOCAL_TRANSFORM_CHANGED(35)` + `TRANSFORM_CHANGED(2000)` on
  itself and **`TRANSFORM_CHANGED(2000)` on the child** (the child's global transform
  changed) — but **not** `35` on the child (`move_p=[35,2000] move_c=[2000]`) **[M]**.
- Moving the child emits `35` on the child only (`cmove_c=[35]`, `cmove_p=[]`) **[M]**.
- **Reparenting root→CanvasLayer emits the full re-entry set** (both directions):
  `ENTER_TREE(10), EXIT_TREE(11), PARENTED(18), UNPARENTED(19), POST_ENTER_TREE(27),
  DRAW(30), VISIBILITY_CHANGED(31), ENTER_CANVAS(32), EXIT_CANVAS(33),
  TRANSFORM_CHANGED(2000), TRANSLATION_CHANGED(2010)` — one each **[M]**. The
  `EXIT_CANVAS`+`ENTER_CANVAS` pair is the canvas migration; `get_canvas_layer_node()`
  is non-null inside the layer and null at the root (`cl_node=1 cl_node_back=0`) **[M]**.

### 3.13 Draw state vs node transform + canvas spaces (`draw_state`) — [M]

```
PASS canvas_lattice draw_state same=1 matrix_same=1
  canvas=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000)
  wc=(0.9689,0.2474;-0.2474,0.9689;7.0000,8.0000) screen_eq=1 vp=(64.0000,64.0000)
  mcl=(3.4015,1.1956) mouse=(-8.7616,-6.0195)
```

- With no camera, `get_canvas_transform()` is the identity; `get_global_transform_with_canvas()`
  equals the node's global transform (`wc`); `get_screen_transform()` equals it too
  (`screen_eq=1`) **[M]**.
- `make_canvas_position_local((10,10)) = (3.4015,1.1956)` — the item's global transform
  inverted; `get_local_mouse_position() = (-8.7616,-6.0195)` for the headless mouse at
  `(0,0)` (consistent with the same inverse) **[M]**.
- The `--script` root viewport is **64×64** (`vp`), matching the r85 scratch viewport
  note — a battery-context fact, not a project setting.

### 3.14 Redraw triggers — clean context (`redraw_triggers`) and counterexample (`redraw_context`) — [M]

```
PASS canvas_lattice redraw_triggers table=idle=0,pos=0,rot=0,scale=0,skew=0,modulate=0,
  self_modulate=0,material=0,z=0,zrel=0,ysort=0,behind=0,vislayer=0,lightmask=0,clip=0,
  upm=0,shader=0,texfilter=1,texrepeat=1,oversample=1,toplevel=1,rename=0,visbit=0,hide=0,show=1

PASS canvas_lattice redraw_context trigger_n=1 control_n=0 nontransform_n=0
```

- On a fresh node, only **five** writes queue a redraw: `texture_filter`,
  `texture_repeat`, `oversampling_with_scale`, `top_level`, and the visibility
  transition (`show`); **transform writes (position/rotation/scale/skew), modulate,
  material, z_index, z_as_relative, y_sort, show_behind_parent, visibility_layer,
  light_mask, clip_children, use_parent_material, instance shader parameters, renaming
  and visibility-layer-bit writes do not** **[M]**.
- **Counterexample (falsification F12):** in a frozen context — oversampling change →
  (3 frames) → `scale` write → (3 frames) → **the next transform write queues a
  redraw** (`trigger_n=1`), while the same sequence without the oversampling change
  (`control_n=0`) or with a non-transform write (`nontransform_n=0`) does not **[M]**.
  The clean-context table above is therefore valid **only for its own frozen sequence**;
  the reliable author rule is "call `queue_redraw()` explicitly after any change that
  affects drawing" (§5 H6).

---

## 4. Laws (each pinned by ≥3 canonical reps + loadtest)

**L1 — `queue_redraw()` is an end-of-frame coalescing flush.** A queue issued anywhere in
process frame N (deferred body, `_process`, `_physics_process`) draws at frame N, at most
once, unless the item is hidden or outside the tree; a self-queue from inside `_draw()` is
swallowed; `show()`/re-add redraw. *(§3.2)*

**L2 — There are exactly three legal draw contexts.** `_draw()`, a `NOTIFICATION_DRAW`
handler, and a `draw`-signal handler may call `draw_*`; anything else is refused with a
fixed ERROR naming those contexts. Inside one draw the order is
`NOTIFICATION_DRAW → draw signal → _draw`. *(§3.3, §3.4)*

**L3 — The local transform is `R·K·S·T`.** `Node2D.get_transform()` equals
`Transform2D(rotation, scale, skew, position)`; skew (radians) maps the y basis to
`(-sin k, cos k)`; skewing a draw transform requires the matrix variant. *(§3.9)*

**L4 — Global readbacks are decompositions, not the values you set.** Mirroring flips
`global_rotation` by π; a non-uniform parent scale produces a non-zero `global_skew` and a
`global_rotation` that is not the sum of the parts; a zero scale reads back as a ~2e-5
epsilon. *(§3.10)*

**L5 — Global setters inverse-compose; `translate` is parent-space; normalisation
differs.** `global_position/rotation/scale` writes compose through the parent;
`translate()` adds to `position` in parent space; local `rotation` is stored raw while
`global_rotation` is normalised to `[-π,π]`; `top_level` makes global == local. *(§3.11)*

**L6 — Z-order is not observable headless.** `z_index`/`z_as_relative`/`y_sort_enabled`/
`show_behind_parent` are local readbacks (parents do not change child readbacks; y-sort is
not inherited); the headless draw-callback order is queue/creation order and never
z-sorted; no API exposes effective z or the sorted order. *(§3.1, §3.7)*

**L7 — Modulation is local-only observable.** `modulate`/`self_modulate` are independent
per-item readbacks, values are not clamped, and there is no effective-modulate getter —
the composition chain is not assertable headless. *(§3.8)*

**L8 — Visibility is inherited and edge-notified.** A hidden ancestor makes
`is_visible_in_tree()` false while the child's `visible` stays true; each effective toggle
emits one `NOTIFICATION_VISIBILITY_CHANGED` + one `visibility_changed` (+ `hidden` on the
hide edge); redundant toggles are no-ops; hidden items do not draw. *(§3.5)*

**L9 — `clip_children` refuses out-of-range and casts negatives.** `>= CLIP_CHILDREN_MAX`
is refused with an ERROR and keeps the previous value; a negative value is stored as its
uint32 cast. *(§3.6)*

**L10 — Transform notifications are opt-in; canvas re-entry is loud.** By default transform
writes are silent; with both notify flags, a parent move notifies the child's
`TRANSFORM_CHANGED`; reparenting into a `CanvasLayer` emits the full re-entry set
including `ENTER_CANVAS`+`EXIT_CANVAS`. *(§3.12)*

**L11 — Redraw triggers are context-dependent.** Only five writes redraw on a fresh node
(§3.14), but a frozen counterexample shows a transform write redrawing after an
oversampling+scale history — so the only portable rule is an explicit `queue_redraw()`.
*(§3.14)*

---

## 5. Hazards recorded (for the author and the boundary seat)

1. **`queue_redraw()` from inside `_draw()` is a silent no-op** (§3.2) — a self-rescheduling
   draw loop does not loop. Use `call_deferred` or a process hook.
2. **Hidden items silently drop queued redraws** (§3.2) — if you queue before hiding, the
   pending draw never happens; showing later redraws once.
3. **Draw calls outside the three legal contexts are refused with an ERROR** (§3.4) —
   an author who draws from `_process`/a timer callback gets an engine error and no
   drawing; the error text itself is the API documentation.
4. **`_draw` is not the first thing in a draw** (§3.3): `NOTIFICATION_DRAW` handlers and
   `draw`-signal handlers run first; a handler that appends to a shared buffer sees a
   different order than expected.
5. **The headless draw order is not the visual order** (§3.7) — never write a row or a
   game test that asserts draw order from `_draw` notifications under a z_index/y_sort
   expectation; the sort is renderer-side.
6. **Transform writes may or may not redraw** (§3.14) — the clean-context table is
   sequence-dependent; always queue explicitly.
7. **`global_rotation` under a non-uniform parent is a shear decomposition** (§3.10) —
   `global_skew` becomes non-zero and the angle is not the naive sum.
8. **A zero `global_scale` is a ~2e-5 epsilon** (§3.10) — use `is_zero_approx`, never `==`.
9. **`translate()` is parent-space, not rotated-local** (§3.11) — use `move_local_x/y`
   for a local move.
10. **Local `rotation` is un-normalised, `global_rotation` is normalised** (§3.11) — a
    round-trip through `global_rotation` changes the value you set.
11. **`clip_children` out-of-range is refused, not clamped** (§3.6) — a failed set leaves
    the old mode and prints an ERROR; the negative uint32 cast is accepted silently.
12. **Effective modulate and effective z are not readable headless** (§3.1, §3.8) — do not
    build a headless assertion on either; only the local properties and the notification
    order are evidence.
13. **`draw_set_transform` state is not readable** (§3.3) — the row can only pin that the
    calls are legal and do not mutate the node transform; the resulting draw transform is
    renderer state.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (15, exec-checked)

`corpus/live/r98-scout/author-rows.py.txt` holds the two 5-tuple sets and the
`EXPECTED_ERRORS` dict; `python3 verify_rows.py` classifies every row against **every**
canonical + loadtest receipt with the production `classify_process` (AST-extracted from
`corpus/fixtures/run_battery.py`, segment sha256 `749fa060…` — the same segment
r89/r90/r91/r95 pinned):

- **`ROWS` (full-line): 129/129 receipts accepted, `rejected=[]`.**
- **`ROWS_PREFIX` (gating): 129/129 accepted, `rejected=[]`** — identical except that the
  `queue` cell is cut immediately before its first `events_tail=` (the raw frame-number
  tail; the prefix keeps every gating boolean).
- `EXPECTED_ERRORS`: exactly two entries —
  `r98_canvas_draw_refusal` → the `Drawing is only allowed inside…` line, and
  `r98_canvas_clip` → the `Condition "p_clip_mode >= CLIP_CHILDREN_MAX" is true.` line.
  Every other cell is ERROR-clean with 0 B stderr.

```
r98_canvas_census          PASS canvas_lattice census consts=… local_notify_default=0
r98_canvas_modulate        PASS canvas_lattice modulate defaults=… material_null=1
r98_canvas_queue           PASS canvas_lattice queue add_same=1 … outadd_n=1 [events_tail=…]
r98_canvas_draw_surface    PASS canvas_lattice draw_surface ok_n=33 rid=1 xform_same=1 matrix_same=1 order=nsd
r98_canvas_draw_refusal    PASS canvas_lattice draw_refusal outside_refused=1 proc_refused=1 sig_ok=1 notif_ok=1 draws=1
r98_canvas_vis_chain       PASS canvas_lattice vis_chain hide_in_tree=0 … draws_total=5
r98_canvas_clip            PASS canvas_lattice clip default=0 … oversample=0
r98_canvas_zorder          PASS canvas_lattice zorder first=ABC … requeue=CBA
r98_canvas_xform_skew      PASS canvas_lattice xform_skew m45=… ctor=1 rks=1
r98_canvas_xform_mirror    PASS canvas_lattice xform_mirror mx_grot=-2.0416 … zero_gskew=0.0000
r98_canvas_xform_global    PASS canvas_lattice xform_global gp_local=(7.0453,0.6031) … edit_pivot=(0.0000,0.0000)
r98_canvas_notify          PASS canvas_lattice notify defaults=0,0 … cl_node_back=0
r98_canvas_draw_state      PASS canvas_lattice draw_state same=1 matrix_same=1 … mouse=(-8.7616,-6.0195)
r98_canvas_redraw_triggers PASS canvas_lattice redraw_triggers table=idle=0,…,show=1
r98_canvas_redraw_context  PASS canvas_lattice redraw_context trigger_n=1 control_n=0 nontransform_n=0
```
(Exact strings in `author-rows.py.txt`; the `queue` prefix form cuts at ` events_tail=`.)

Probe file lands at `corpus/fixtures/canvas_lattice.gd` (sha256
`866480a1aaa0a385ad5a0e56a3066af4e5341db2e4ab5a5963366aef949394f0`, self-contained
`SceneTree` script, battery `--arm=` convention, no resources beyond
`ImageTexture`/`ThemeDB.fallback_font` created inside the probe). Insert the rows ahead of
the crash/descendant tail like prior blocks; **two `expected_errors` entries are
required** (draw_refusal, clip) — both exact-match lines verified live on all 129
receipts.

### 6.2 What to pin and what not to pin

1. **Pin the `PASS canvas_lattice …` line** — it carries the arm name, so the r88
   silent-fallback failure cannot recur.
2. **Prefer the prefix form for `queue`** — the raw `events_tail` frame numbers are
   deterministic today but are process-frame plumbing; the prefix booleans are the law.
3. **Do not pin anything that the renderer owns**: effective z order, effective modulate,
   sorted draw order, the draw transform state. None of them have a readback (§3.1).
4. **Pin the predicates, not just the numbers**: `order=nsd`, `refused_stays=1`,
   `neg_cast=4294967293`, `zero_gscale=(0.000020,0.000020)`, `nu_gskew=1.3410` are the
   laws; the matrices are the measurements.
5. **Keep the two refusal cells' `EXPECTED_ERRORS` entries** — they are the only
   allowlisted errors; removing them would flip both rows to FAIL.
6. **No envelope is needed for any cell** — 15/15 single-valued across canonical +
   loadtest (129/129).

---

## 7. Falsification list

| id | hypothesis (must-differ input) | result |
|---|---|---|
| F1 | Draw calls are only legal inside `_draw()` | **REFUTED [A]** — `NOTIFICATION_DRAW` handlers and `draw`-signal handlers are legal (`sig_ok=1 notif_ok=1`); the refusal ERROR names all three |
| F2 | `_draw()` runs first inside a draw | **REFUTED [A]** — order is `NOTIFICATION_DRAW → draw signal → _draw` (`order=nsd`) |
| F3 | `queue_redraw()` from `_draw()` reschedules the next frame | **REFUTED [A]** — swallowed (`from_draw_n=1`; `qtime3` silence over 3 frames) |
| F4 | `queue_redraw()` takes effect next frame | **REFUTED [A]** — same-frame flush from `_process` (`proc_same=1`, `q@pf0`→`d@pf0`) |
| F5 | Multiple `queue_redraw()` calls in a frame cause multiple draws | **REFUTED [A]** — coalesced to one (`coalesce_n=1`) |
| F6 | A hidden item still receives its pending draw | **REFUTED [A]** — `hidden_n=0`, `hide_before_flush_n=0` |
| F7 | `z_index` determines the draw-callback order | **REFUTED [A]** — creation order `ABC` with z `-5,0,5`; queue order `CBA` on reverse requeue |
| F8 | `z_index`/`z_as_relative`/`y_sort_enabled` propagate to children | **REFUTED [A]** — local readbacks only (`parent_isolated=1`, `parent_flag_isolated=1`, `ysort=1,0`) |
| F9 | Parent `modulate` writes change the child's readback | **REFUTED [A]** — child readbacks unchanged; values are not clamped (`raw_neg=4,-1,0.5,4`) |
| F10 | An invalid `clip_children` value clamps to the max | **REFUTED [A]** — refused, previous value kept + ERROR (`refused_stays=1`) |
| F11 | A negative `clip_children` value is rejected | **REFUTED [A]** — stored as uint32 `4294967293`, no ERROR |
| F12 | Transform writes never queue a redraw | **REFUTED [A]** — after oversampling+scale history the next transform write redraws (`trigger_n=1`); ablated: without oversampling 0, without scale 0, non-transform write 0 |
| F13 | `translate()` moves along the node's rotated local axis | **REFUTED [A]** — adds to `position` in parent space (`translate=(1,0)` at 90° rotation) |
| F14 | `global_rotation` under a non-uniform parent is parent+child rotation | **REFUTED [A]** — shear appears (`nu_gskew=1.3410`, `nu_grot_deg=42.1249` vs the naive 22.92°) |
| F15 | A zero scale reads back as exactly zero | **REFUTED [A]** — `zero_gscale=(0.000020,0.000020)` |
| F16 | `global_rotation` round-trips the local rotation | **REFUTED [A]** — local raw `4.0`, global normalised `-1.5832` |
| F17 | Transform notifications are on by default | **REFUTED [A]** — silent by default (`move_default=[]`); opt-in flags required |
| F18 | `clip_children`/`modulate`/effective-z have headless readbacks beyond the local property | **REFUTED [A]** — `has_global_modulate=0`, `has_global_z=0`, `rs_getters=3` (shader params only) |

---

## 8. Remaining unknowns / not measured

- **Rendered output**: `RendererDummy` means no pixels, no draw-command inspection, no
  texture readback; every `draw_*` claim here is "callable/refused", never "rendered".
- **Effective modulate composition** (parent×child×self) — no readback exists (§3.1).
- **Effective z / y-sorted order / `show_behind_parent` effect** — renderer-side; only
  the notification order was measured (§3.7).
- **The full state space of the context-dependent redraw** (§3.14): one trigger sequence
  was isolated and ablated; which engine state latches is **[I]**, and other histories
  may exist.
- **`draw_set_transform` state** (the composed draw transform, its persistence across
  commands, and `draw_animation_slice` semantics) — not readable headless.
- **`draw_*` argument refusals**: discovery saw `draw_arc(point_count=0)` →
  `Condition "p_points.size() < 2"` and `draw_polygon(<3 points)` →
  `Condition "pointcount < 3"`; these were **not** frozen into rows (they would need
  their own `EXPECTED_ERRORS`) and the exact boundary for every primitive is unmeasured.
- **Font/texture edge cases**: null font, null texture, zero-size regions — unmeasured.
- **`NOTIFICATION_PROCESS`/`PHYSICS_PROCESS`-driven redraw loops** under fixed-fps:
  process frames run uncapped headless, so physics-frame-coupled timing was avoided.
- **`CanvasItem` materials/shaders**: `material`, `use_parent_material` and instance
  shader parameters were only checked for readback/redraw, not for rendering effect.
- **`Control`-side pivot math** (`pivot_offset`, `rotation`/`scale` around a pivot) is a
  different class and a different surface — not measured.
- **Portability**: every value is this host/build/`--headless`/`RendererDummy`/64×64
  `--script` viewport.

---

## 9. Independent probe (frozen `probeParent` dispatch) — COMPLETED

The frozen probeParent dispatched exactly one read-only `ufo-labrat` seat with a bounded
receipt audit (no writes, no engine launches). Its report, on the receipts that existed
mid-run:

- **PASS stability**: every audited arm (`census`, `modulate`, `queue`, `draw_surface`,
  `draw_refusal`, `vis_chain` at that moment) had byte-identical final PASS lines across
  all its reps; no differing lines.
- **Source↔PASS key traceability**: every PASS key maps to an `_it(...)` call in the
  corresponding arm, in order — no fabricated or missing keys in any audited arm.
- **Law attacked (L1)**: SUPPORTED by the `queue` receipts — `coalesce_n=1`,
  `from_draw_n=1`, `hidden_n=0`, `hide_before_flush_n=0`, `out_n=0`, `show_n=1`,
  `readd_n=1`, `outadd_n=1`, and `q@pf0`→`d@pf0` same-frame evidence, quoted.
- **ERROR lines**: the two `draw_refusal` ERRORs per rep are the arm's deliberate,
  expected refusals; all other canonical `.err` files clean; discovery ERRORs are
  exploratory.

The seat's own conclusion: the hypothesis survived on the audited subset, with the only
limitation being incompleteness at audit time. The final full-population run (§1) closes
that limitation: **129/129 receipts, 0 rejections**.

---

## 10. Host cleanup

- **160 retained receipts** (84 canonical + 45 loadtest + 15 discovery + 16 ladder), all
  `--headless`, all `timeout -s KILL`-bounded (30 s; none hit), no run left running
  (`pgrep -fa canvas_lattice` → none).
- Loadtest hogs: 8 own `yes` processes started and **only their own PIDs killed**
  (`own_hogs_killed=8`, `host_yes_remaining=32` — other lanes' hogs untouched; no
  `pkill`/`pgrep`-based foreign kills this round).
- No tracked file written: `git status --porcelain` shows `?? corpus/live/r98-scout/`
  plus this report only; the sole `M` line is the concurrent r90 lane's
  `corpus/fixtures/run_battery.py` (+74 lines, no r98 token). The probe was never copied
  into `corpus/fixtures/`.
- `manifest.sha256` (505 files) covers every artefact under `corpus/live/r98-scout/`
  except itself.

---

## 11. Evidence index

All under `corpus/live/r98-scout/`; `manifest.sha256` covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| **frozen primary probe, 15 cells** | `probes/canvas_lattice.gd` | `866480a1aaa0a385` |
| discovery micro-probe (15 arms) | `probes/discover.gd` | see manifest |
| focused ladders (redraw falsification) | `probes/{skewchk,showchk,trigchk,late,late2,ablate,minimal,bisect}.gd` | see manifest |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| canonical driver (15 cells, 84 runs) | `run_cells.sh` | see manifest |
| loadtest driver (45 runs, load avg 74–86) | `run_loadtest.sh` | see manifest |
| analyzer → json/text | `analyze_r98.py` → `runs/analyze_r98.{json,txt}` | see manifest |
| author rows + builder + verifier | `author-rows.py.txt`, `make_author_rows.py`, `verify_rows.py` | see manifest |
| per-cell receipts (84 × 3 files) | `runs/r98_canvas_*.{out,err,rc}` | `manifest.sha256` |
| loadtest receipts (45 × 3 files) | `runs/loadtest/` | `manifest.sha256` |
| discovery receipts | `runs/disc/` | `manifest.sha256` |
| focused-ladder receipts (8 × 2 reps) | `runs/ladder/` | `manifest.sha256` |

Reproduce: `bash run_cells.sh && bash run_loadtest.sh && python3 analyze_r98.py &&
python3 make_author_rows.py && python3 verify_rows.py` (expect `UNSTABLE=[]`,
`LOADTEST_UNSTABLE=[]`, `ROWS 129/129`, `ROWS_PREFIX 129/129`, `rejected=[]`).
