# game-dev-2d round 100 — scout (r100-scout): capstone regression-residue sweep + the Viewport/Control GUI input-routing & pointer-gesture lattice, pre-measured; 14 rows verbatim-ready

Seat `SCOUT` (LEAF; frozen `probeParent` — one labrat dispatch, read-only, §9) | lane
`r100-scout` | round 100 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
`DisplayServer.get_name() == "headless"`, root viewport **64×64**, 60 tps, `RendererDummy`.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`. HEAD at session start **`2c4b1ff`**
(*r94 scout*); HEAD at session end **`61355e2`** (*r89 reviewer*) — the concurrent r89 lane
landed `8cea888` (r89 author, the 20-row battery merge) + `61355e2` (r89 reviewer) while this
seat ran. The battery bytes this seat ran (run dir `20261015T200615022811Z`, started
20:06:15Z) are the bytes committed as `8cea888`/`61355e2` (worktree == HEAD at sweep time,
verified 20:13Z). At report close a concurrent lane had begun merging the r90 RB2D rows into
`corpus/fixtures/run_battery.py` (74 insertions, mtime 20:14:42Z) — **not this seat's edit**
(this seat wrote only `corpus/live/r100-scout/**` and this report).

**No git mutation, no tracked file written, no commit.** Writes are this report and
`corpus/live/r100-scout/**` only. The launch `project.godot` is the byte-copy of
`corpus/fixtures/project.godot` (`8de8b3af…`).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on this
host; `definition`/`references`/`hover` were **unavailable for every file**. All symbol/API
knowledge comes from runtime `ClassDB`/instance introspection inside the probes and from the
engine's own error text. No engine source tree exists on this host; mechanism statements are
marked **[I]** and kept separate from measurements.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Capstone verdict — ranked residue surfaces

The brief's candidates, ranked by (a) 2D-authoring relevance, (b) headless measurability,
(c) residual coverage, (d) falsifiability, with the round's evidence:

| rank | surface | verdict | evidence |
|---|---|---|---|
| **1** | **Viewport/Control GUI input routing + pointer-gesture stream** (`push_input` → `_gui_input`, `mouse_filter`, hover, mouse-motion/`double_click`, drag-and-drop, ScreenTouch/ScreenDrag + emulation, SubViewport input isolation, focus/key routing, cursor null-ness) | **PINNED — worth the round** | Zero tracked rows for positional routing (§0.1); 14 cells measured byte-stable ×6 canonical + ×2 under 8 hogs, full-line rows verified 112/112 with the production classifier (§6.1). r87 left `SubViewport cursor` open — closed here (§3.6/§3.11). |
| 2 | **The unmerged r90–r95 frontier** (83 scout-verified rows: r90 RB2D extras 10, r91 nav 9, r92 TileMapLayer 13, r93 anim/tween 15, r94 particles 19, r95 dss queries 17) | **MEASURED, NOT TRACKED — land before new probes** | `grep` for `rb2d_`/`nav_lattice`/`tilemap_lattice`/`anim_tween`/`particles_lattice`/`dss_lattice` in `corpus/fixtures/run_battery.py` → **0 hits**; the six `corpus/live/r9x-scout/author-rows.py.txt` files carry 10/9/13/15/19/17 rows = **83**. The tracked battery carries 228 CASES tuples (208 r88-admitted + the 20-row r89 merge; the SCORECARD/commit "215→235" counts are verdict lines: 228 CASES + 7 meta probes = 235). |
| 3 | **light shadow / filter chain** | **VACUOUS headless (property readback only)** | `RendererDummy`: no adapter name, no rendering device, screens=0, `PointLight2D` shadow state readback-only (r88 already pinned `pl=[en=true sh=true …]` readbacks); behaviour (shadows, filters, blend modes) needs a renderer. |
| 4 | **backbuffer / copy-texture APIs** | **VACUOUS headless — measured as a deterministic ERROR** | `root.get_texture()` is a `ViewportTexture(64,64)` but `get_image()` → **null** + `ERROR: Parameter "t" is null.` at `./servers/rendering/dummy/storage/texture_storage.h:110`; `RenderingServer.get_rendering_device()` null (§3.14). One negative row is authorable with an `expected_errors` entry. |
| 5 | **GPUParticles2D beyond r94** | **VACUOUS headless** | r94: `finished` never fires, `request_particles_process` no-op; `capture_rect()` = `[P:(0,0), S:(0,0)]` (§3.14, corroborates r94 §3.5). Sub-emitters/trails/collision/turbulence are readback-only. |
| 6 | **OS/threading in-engine** | **MEASURABLE but off-axis** | `Thread`/`Mutex`/`Semaphore`/`WorkerThreadPool`/`Time` exist (methods 7/3/3/9/21, §3.15); r86 already owns the 2D-relevant `physics/2d/run_on_separate_thread` gate. Not a 2D-authoring surface; recommend only if the lane wants an engine-meta family. |
| 7 | **Viewport/world non-input residue** | **MOSTLY COVERED** | r85 (world isolation, canvas transform, CanvasLayer, parallax) + r95 §3.9 (space scoping); the render-side remainder is rank 3/4 above. |

**Residue inside the pinned surface** (measured here or explicitly bounded): multi-touch
`index>0`, drag preview content, `event_index 1..31` *meaning* (r87 pinned the refusal
boundary), `in_local_coords=true` under non-identity content scale, `Input.set_mouse_mode` /
`DisplayServer.warp_mouse`, and the battery's load-sensitivity envelope (§7).

### 0.1 Why this surface earned the round

- **Zero positional-routing coverage.** Every existing Control fixture drives activation with
  `InputEventAction` (`button_activation.gd:17`, `checkbox_toggle.gd:17`,
  `button_group_selection.gd:23,28`, `slider_adjust.gd:242,312,398,469,538`); the only mouse
  work is r87's `Input.parse_input_event` state probe (`input_lattice.gd:712-727`) which never
  touches `_gui_input`, hit-testing or `mouse_filter`. `grep -rin
  "mouse_filter|_gui_input|gui_get_hovered_control|mouse_entered|ScreenTouch|ScreenDrag|warp_mouse|_drop_data"`
  over `corpus/fixtures/` before this round → **0 hits** (labrat audit §9).
- **Falsifiable on first contact** (§5): the cursor is *not* moved by `push_input`, the drag
  threshold is *not* the press, the drop target is *not* the control under the mouse at release
  in the simple sense, and hover/button picking are clipped differently.
- **All of it is scene-tree logic** — no rendering server needed; byte-stable under load.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `bash run_cells.sh <cells> 6` | **14 cells × 6** = 84 canonical runs | `runs/r100_gui_*.rep{1..6}.{out,err,rc}` |
| 2 | `HOGS=8 REPS=2 bash run_loadtest.sh` | **14 cells × 2** = 28 runs under 8 own `yes` hogs | `runs/loadtest/` |
| 3 | `probes discover2..discover8.gd` | ~40 discovery arms (cursor laws, `event.position`, drag threshold/target, mask dependency, viewport clip, drag geometry grid) | `runs/d2_*` … `runs/d8_*` |
| 4 | `python3 analyze_r100.py` | per-cell reps/out_uniq/err_uniq/rc/pass_uniq | `runs/analyze_r100.json/.txt` |
| 5 | `python3 make_author_rows.py` → `verify_rows.py` | 14 rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) | `author-rows.py.txt` |
| 6 | `python3 corpus/fixtures/run_battery.py` | **capstone regression sweep** on the tracked battery (HEAD bytes) | `battery-r100-pre.{out,err}`; verdicts `corpus/live/runs/20261015T200615022811Z/verdicts.json` |

**Cell set (14):** `census routing hover motion localpos cursor clip drag touch subvp warp
focus render osmeta`.

**Byte-stability [M]:** all 14 cells `out_uniq=1 err_uniq=1 rc=[0] pass_uniq=1` across 6
canonical reps **and** 2 loadtest reps (`analyze_r100.txt`: `UNSTABLE=[]` in both sections);
the canonical and loadtest lines are byte-identical for all 14 cells. Only `render` carries
stderr (246 B — the deterministic dummy-texture ERROR + backtrace). Host load during the
canonical run: loadavg **60–80** from concurrent lanes; the loadtest added 8 own hogs.

**Battery sweep [M]:** 229 PASS lines / 5 row FAILs + 2 meta FAILs → `FAIL battery`. §7
dissects this: the failing family is pre-existing and load-sensitive, not r89-introduced.

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| API census + defaults + event property lists | **PINNABLE** | 6 | uniq=1 |
| `mouse_filter` STOP/PASS/IGNORE routing matrix + `set_input_as_handled` | **PINNABLE law** | 6 | uniq=1 |
| hover (`gui_get_hovered_control`, `mouse_entered/exited`, press-hover) | **PINNABLE law** | 6 | uniq=1 |
| mouse-motion passthrough (`relative`, `velocity`, `double_click`) | **PINNABLE** | 6 | uniq=1 |
| `event.position` local vs `get_local_mouse_position()` cursor-derived | **PINNABLE hazard** | 6 | uniq=1 |
| cursor update laws (`push_input` inert vs `Input.parse_input_event` global_position-driven) | **PINNABLE law** | 6 | uniq=1 |
| viewport-edge picking (hover clipped / buttons unclipped) | **PINNABLE hazard** | 6 | uniq=1 |
| drag-and-drop (threshold >10, motion-mask, press-focus source, drop target) | **PINNABLE law + hazard** | 6 | uniq=1 |
| `force_drag` path (`can_drop` / `drop` / `can_drop=false`) | **PINNABLE** | 6 | uniq=1 |
| ScreenTouch/ScreenDrag routing + both emulation directions | **PINNABLE law** | 6 | uniq=1 |
| SubViewport input isolation + private cursor | **PINNABLE law** | 6 | uniq=1 |
| `warp_mouse`/cursor null-ness (Input + Viewport + DisplayServer) | **PINNABLE inertness** | 6 | uniq=1 |
| focus/key routing (`grab_focus`, `gui_get_focus_owner`, `gui_release_focus`) | **PINNABLE law** | 6 | uniq=1 |
| backbuffer/light/GPU-particle render residue | **HEADLESS-NULL** (one allowlisted ERROR row) | 6 | uniq=1 (stderr 246 B) |
| OS/threading class census | **PINNABLE but off-axis** | 6 | uniq=1 |

---

## 3. Measured values, verbatim

All lines are `runs/r100_gui_<cell>.rep1.out`; full verbatim rows are in
`author-rows.py.txt`. Long lines are quoted by their key tokens.

### 3.1 Census (`census`) — [M], 6/6 identical

```
dv=headless vpsize=(64.0, 64.0) final=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000)
mf_ctrl=0 mf_label=2 mf_button=0 mf_panel=0 mf_container=1 focus_mode_ctrl=0
vpmethods=[push_input=1|push_unhandled_input=1|gui_get_focus_owner=1|gui_get_hovered_control=1|
  gui_is_dragging=1|gui_get_drag_data=1|gui_release_focus=1|set_input_as_handled=1|
  is_input_handled=1|get_mouse_position=1|warp_mouse=1|get_final_transform=1]
ctrlmethods=[force_drag=1|accept_event=1|grab_focus=1|has_focus=1|release_focus=1|
  get_local_mouse_position=1|set_drag_preview=1]
inputmethods=[…|get_mouse_position=0|…]            # Input has NO get_mouse_position in 4.7
emul_mouse=1 emul_touch=0                           # touch→mouse emulation is ON by default
mbprops=[alt_pressed|button_index|button_mask|canceled|ctrl_pressed|device|double_click|factor|
  global_position|meta_pressed|position|pressed|resource_local_to_scene|resource_name|script|
  shift_pressed|window_id]
mmprops=[alt_pressed|button_mask|ctrl_pressed|device|global_position|meta_pressed|pen_inverted|
  position|pressure|relative|resource_local_to_scene|resource_name|screen_relative|
  screen_velocity|script|shift_pressed|tilt|velocity|window_id]
stprops=[canceled|device|double_tap|index|position|pressed|resource_local_to_scene|
  resource_name|script|window_id]
sdprops=[device|index|pen_inverted|position|pressure|relative|resource_local_to_scene|
  resource_name|screen_relative|screen_velocity|script|tilt|velocity|window_id]
```

Default `mouse_filter`: `Control`=STOP(0), `Label`=IGNORE(2), `Button`=STOP, `Panel`=STOP,
`Container`=PASS(1); default `Control.focus_mode`=FOCUS_NONE(0).

### 3.2 Routing matrix (`routing`) — [M], the STOP/PASS/IGNORE table

`s1_cc` child STOP: `[C:mb(p=1)|C:mb(p=0)]` `-` — child only (STOP stops propagation).
`s2_ci` child IGNORE: `-` `[P:mb(p=1)|P:mb(p=0)]` — parent only (IGNORE is skipped by the pick).
`s3_cp` child PASS: child **then** parent receive both edges — PASS propagates *after* delivery.
`s4_ch` child PASS + `set_input_as_handled()`: child only — handled suppresses the parent.
`s5_ci_pp` child IGNORE + parent PASS: parent only. `s6_ii` both IGNORE: nobody.
`s7_inparent` (24,24): parent only. `s8_out` (60,60): nobody.
`s9_rb`: right button `b=2` reaches the parent.
`s10_input_state held_push=0 cursor=(0.0, 0.0)` — **`push_input` does not update
`Input.is_mouse_button_pressed` and does not move the cursor**.

### 3.3 Hover (`hover`) — [M]

```
h0=null h1=A ev=[A_in] h2=A ev=[A_in] h3=B ev=[A_in|A_out|B_in] h4=null ev=[…|B_out]
h5=C ev=[…] h6_press=A ev=[…|A_in] h7_after_release=A
```
Hover updates on **motion and on press**; `mouse_entered/exited` fire on transitions; leaving
all controls clears it; a STOP child inside an IGNORE parent is still hovered (`h5=C` — the
pick descends); press re-enters the control (`A_in` again); **release does not clear hover**.

### 3.4 Motion passthrough (`motion`) — [M]

```
m1[S:mm(bm=0,pos=10.0,10.0,gpos=10.0,10.0,rel=5.0,7.0,vel=0.0,0.0)]
m2[S:mm(…,rel=10.0,20.0,vel=0.0,0.0)]
m3_dc[S:mb(p=1,dc=1…)|S:mb(p=0,dc=0…)]      # double_click flag passes through
m4_push_input_state held=0 cursor=(0.0, 0.0) vel=(0.0, 0.0)
```
`relative` is delivered verbatim; `velocity` is **not** computed for pushed motions (0.0); the
`double_click` flag is delivered as set.

### 3.5 `event.position` vs cursor-derived helpers (`localpos`) — [M], the author trap

Parent P at (20,10), child C at (4,2) (global 24,12); push a press at (30,14):

```
lp_push_p[-] c[[C:mb(p=1,pos=6.0,2.0,gpos=30.0,14.0)]] loc_c=-24.0,-12.0
lp_push_local_p[-] c[[C:mb(p=1,pos=6.0,2.0,gpos=30.0,14.0)]]        # in_local_coords=true: same
lp_parse_p[-] c[[C:mb(p=1,pos=6.0,2.0,gpos=30.0,14.0)]] loc_c=6.0,2.0 gloc_c=30.0,14.0
```
Inside `_gui_input`, `event.position` is **local to the receiving control** (6,2) and
`event.global_position` is the pushed screen coordinate (30,14). `get_local_mouse_position()`
is **cursor-derived**: stale `(0,0)`-based `(-24,-12)` after `push_input`, correct `(6,2)` only
after `Input.parse_input_event` moved the cursor.

### 3.6 Cursor laws (`cursor`) — [M], closes the r87 `SubViewport cursor` unknown

```
c0=(0.0, 0.0) c1_push_mm=(0.0, 0.0) c2_push_mb=(0.0, 0.0) c3_parse_mb=(24.0, 24.0)
c4_parse_mm=(30.0, 30.0) c5_gpos_drives=(60.0, 60.0) c6_parse_st=(44.0, 44.0)
c7_push_mm2=(44.0, 44.0) c8 ds=(0, 0)
```
- `Viewport.push_input` **never** moves `Viewport.get_mouse_position()` (c1/c2/c7).
- `Input.parse_input_event` **does**, and the value comes from the event's
  **`global_position`**, not `position` (c5: position (70,70), global_position (60,60) → 60,60).
- Parsed `InputEventScreenTouch` also moves it (c6, via the default touch→mouse emulation).
- `DisplayServer.mouse_get_position()` stays `(0, 0)` — the OS cursor is inert headless.

### 3.7 Viewport-edge picking (`clip`) — [M], the asymmetry

Control `ED` at (60,0,32,32) extends past the 64×64 viewport; `FA` at (80,0,32,32) is fully outside:

```
cp0_vis=[P: (0.0, 0.0), S: (64.0, 64.0)]
cp_hover(62.0,4.0)=ED   cp_press(62.0,4.0) ed=[…pos=2.0,4.0…]
cp_hover(63.9,4.0)=ED   cp_press(63.9,4.0) ed=[…pos=3.9,4.0…]
cp_hover(64.0,4.0)=null cp_press(64.0,4.0) ed=[…pos=4.0,4.0…]     # half-open rect
cp_hover(64.1,4.0)=null cp_press(64.1,4.0) ed=[…pos=4.1,4.0…]
cp_hover(70.0,4.0)=null cp_press(70.0,4.0) ed=[…pos=10.0,4.0…]
cp_hover(90.0,4.0)=null cp_press(90.0,4.0) fa=[…pos=10.0,4.0…]
cp_hover200=null
```
**Motion-driven hover is clipped to the viewport's visible rect; button routing is not.** The
visible rect is half-open (63.9 in, 64.0 out). Because the drag drop-target follows hover, a
drag motion outside the viewport finds no target (§3.9 G5).

### 3.8 Drag: threshold + source + mask (`drag`) — [M]

```
d1_at_threshold drag=0 calls=0                       # |relative| = 10 -> no drag
d2_over_threshold drag=1 calls=1 data=fromA at=[(8.0,8.0)]   # 10.5 -> drag
d3_over_b drag=1 a_drop=[can(fromA)] b_drop=[can(fromA)] b_get=0
d4_over_b2 b_drop=[can(fromA)|can(fromA)]
d5_release drag=0 b_drop=[can|can|can|drop(fromA)]
d6_unmasked_motion drag=0 calls=1                    # masked press + unmasked motion -> no drag
d7_accum[1:0 2:1 3:1] calls=2                        # 5.66 / 11.31 / 16.97
d8_no_target drag=0 a_drop=[…|can(fromA)|can(fromA)|drop(fromA)]   # released over the source
d9_force drag=1 data=forced calls=0                  # force_drag: no threshold, no _get_drag_data
d10_force_over_d d_drop=[can(forced)]
d11_force_drop drag=0 d_drop=[can(forced)|can(forced)|drop(forced)]
d12_nodrop drag=0 d_drop=[…|can(no)]                 # can_drop=false: can called, no drop
```
Laws: threshold = accumulated `|relative|` **> 10**; the **motion event's own `button_mask`
must carry LEFT** (a masked press + unmasked motion never drags; an unmasked press + masked
motion does); `_get_drag_data` runs on the **press-focus** control with the **press-local**
`at_position` (offset case measured `(10.0,4.0)` in `runs/d7_grid` G1/G2); the drop target is
the hover-picked control (`_can_drop_data` per motion + again on release, then `_drop_data`);
releasing over the source calls the source's own drop callbacks; `force_drag(data, null)`
bypasses threshold/mask and never calls `_get_drag_data`.

### 3.9 Drag geometry grid (`runs/d7_grid.out`) — [M], why the first attempt failed

```
G1 drag=1 a=[can] b=[can]   rel=[can]/[can|can|drop]     # in-viewport geometry, both callbacks
G2 drag=1 a=[can] b=-       rel=[can]/-                  # same shape, second motion at (70,14)
G3 drag=1 a=[can] b=-       rel=[can]/-                  # G1 geometry, second motion (70,14)
G4 drag=1 a=[can|can] b=-   rel=[…|drop]/-               # stayed inside A -> source drop
G5 drag=1 a=- b=-           rel=-/-                      # single motion straight to (70,14)
G6 drag=1 a=[can] b=[can|can]                            # third motion (44,4) over B
```
The `(70,14)` cells fail **because of the §3.7 hover clip**, not because of geometry — a
control at x≥64 is reachable by buttons but never hovered, so it can never be a drop target.

### 3.10 Touch (`touch`) — [M]

```
t1_push_a=- b=[B:st(i=0,p=1,dt=1,pos=4.0,4.0)]          # position pick + double_tap passthrough
t2_pushdrag_a=- b=[B:sd(i=0,pos=-12.0,4.0,rel=-16.0,0.0)]  # local = prev local + relative
t3_emul_touch held=1 a=[A:mb(bm=1,p=1,pos=8.0,8.0)|A:st(i=0,p=1,pos=8.0,8.0)] b=- emul=1
t4_emul_mouse a_gui=- a_in=[A:st(i=0,p=1,pos=20.0,4.0)|A:mb(b=1,p=1,pos=20.0,4.0)] emul_t=1
```
`ScreenTouch` reaches both `_input` and `_gui_input` of the picked control; `ScreenDrag` is
delivered to the touch's tracked control with a **local position advanced by `relative`**
(the event's own `position` is ignored for delivery). Touch→mouse emulation is **on by
default** and produces an `InputEventMouseButton` with `button_mask=1` plus the original touch
event; `set_emulate_touch_from_mouse(true)` makes a parsed mouse press deliver an
`InputEventScreenTouch` (in `_input`) alongside the mouse event.

### 3.11 SubViewport isolation (`subvp`) — [M]

```
v0_local=1 size=(64, 64) cursor=(0.0, 0.0)
v1_sub[[S:mb(p=1,pos=8.0,8.0)]] root=-     v2_hovered=S cursor_sub=(8.0, 8.0) cursor_root=(0.0, 0.0)
v3_root_push_sub[-] root=[R:mb(p=1,pos=8.0,8.0)]
v4_cursors sub=(8.0, 8.0) root=(0.0, 0.0)
v5_local_false local=0 s2=[[S2:mb(p=1,pos=12.0,12.0)]] cursor=(12.0, 12.0)
```
`SubViewport.push_input` routes to its own Controls, maintains **its own hovered control and
its own cursor** (set from the pushed event), and leaves the root cursor untouched; root
`push_input` does not route into the SubViewport. `handle_input_locally=false` does **not** gate
direct `push_input`. (This closes r87's `SubViewport cursor` unknown: the cursor exists and is
per-viewport; the root cursor is inert because `push_input` never writes it.)

### 3.12 Warp / cursor null-ness (`warp`) — [M]

```
w0 dv=headless cursor=(0.0, 0.0) ds_mouse=(0, 0)
w1 after_push cursor=(0.0, 0.0) ds_mouse=(0, 0)
w2 after_input_warp cursor=(0.0, 0.0) ds_mouse=(0, 0)     # Input.warp_mouse: no-op
w3 after_vp_warp cursor=(0.0, 0.0) ds_mouse=(0, 0)        # Viewport.warp_mouse: no-op
w4 mode=0
```
Both warp APIs and the DisplayServer cursor are inert under the headless display server.

### 3.13 Focus / key routing (`focus`) — [M]

```
f0 owner=F f_focus=1 g_focus=0
f1_key gui_f=[F:key(k=65,p=1)] gui_g=- in_f=[F:key(k=65,p=1)]
f2_handled gui_f=[F:key(k=65,p=1)] gui_g=-
f3_regrab gui_f=- gui_g=[G:key(k=65,p=1)] owner=G
f4_released gui_f=- gui_g=- owner=null
```
Key events go to the focused control's `_gui_input` **and** `_input`; re-grab moves delivery;
`gui_release_focus()` leaves no owner and no delivery.

### 3.14 Render residue (`render`) — [M], the vacuity evidence (one allowlisted ERROR)

```
r0 tex_cls=ViewportTexture size=(64.0, 64.0) r1 img_null=1 r2 adapter= rd_null=1
r3 method=forward_plus screens=0 ssize=(0, 0) win_size=(64, 64)
r4 light sh=0 filt=0 smooth=0.0 blend=0 r5 gpu_capture=[P: (0.0, 0.0), S: (0.0, 0.0)]
```
stderr (246 B, deterministic): `ERROR: Parameter "t" is null.` at
`texture_2d_get (./servers/rendering/dummy/storage/texture_storage.h:110)`.

### 3.15 OS/threading census (`osmeta`) — [M], evidence for the rank-6 verdict

```
Thread[e=1,m=7] Mutex[e=1,m=3] Semaphore[e=1,m=3] WorkerThreadPool[e=1,m=9] Time[e=1,m=21]
os=Linux procs_gt0=1 wtp_has_thread_count=0
```

---

## 4. Laws (each pinned by 6 canonical reps + 2 loadtest reps, byte-identical)

1. **Routing matrix.** STOP delivers to the deepest control and stops; IGNORE is skipped by
   the pick; PASS delivers then propagates to ancestors; `set_input_as_handled()` in any
   receiver suppresses the rest of the chain (§3.2).
2. **`push_input` is a scene-tree injection, not a device.** It updates neither
   `Input.is_mouse_button_pressed` nor the viewport cursor; it *does* update hover (§3.2 s10,
   §3.3, §3.6).
3. **The cursor is written only by `Input.parse_input_event`, from `global_position`**, and
   only `Viewport.get_mouse_position()` observes it; `DisplayServer.mouse_get_position()` is
   inert (§3.6).
4. **`event.position` is control-local inside `_gui_input`; the `get_*_mouse_position()`
   helpers are cursor-derived** and are stale under `push_input` (§3.5).
5. **Hover is clipped to the viewport's half-open visible rect; button routing is not** (§3.7).
   Corollary: the drag drop-target (hover-based) is unreachable outside the viewport.
6. **Drag start = accumulated `|relative| > 10` on a motion whose own `button_mask` has LEFT**,
   evaluated on the press-focus control; `at_position` is the press-local point (§3.8).
7. **Drop target = hover-picked control**, `_can_drop_data` per motion + on release, then
   `_drop_data`; releasing over the source calls the source's callbacks; `can_drop=false` gets
   `can` but no `drop`; `force_drag` bypasses the threshold/mask and skips `_get_drag_data`
   (§3.8).
8. **Touch events are positional and tracked**: `ScreenTouch` picks by position and passes
   `double_tap`; `ScreenDrag` advances the tracked local position by `relative` (§3.10).
9. **Both emulation directions work headless** and touch→mouse is **on by default** (§3.10).
10. **SubViewports own their input state** (cursor + hovered control) and are isolated from
    root `push_input` (§3.11).
11. **Warp APIs and the OS cursor are inert** under `--headless` (§3.12).
12. **Focus owns key delivery**; `_gui_input` and `_input` both see the key; releasing focus
    ends delivery (§3.13).
13. **The render surface is headless-null**: `ViewportTexture.get_image()` nulls with a
    deterministic dummy-storage ERROR; no adapter/rendering device/screen; light shadow state
    is readback-only; GPU particle `capture_rect` is a zero rect (§3.14).

---

## 5. Falsification list (assumptions refuted during discovery)

| # | assumption | result | receipt |
|---|---|---|---|
| F1 | a pushed motion moves the viewport cursor | **REFUTED** — cursor unchanged through push motions/presses | §3.6 c1/c2/c7 |
| F2 | `Input.get_mouse_position()` exists in 4.7 | **REFUTED** — no such method | §3.1 `get_mouse_position=0` |
| F3 | the drag threshold is a small fixed distance | **REFUTED** — rel 10 → no drag, 10.5 → drag; accumulates across motions | §3.8 d1/d2/d7 |
| F4 | a masked press is sufficient to drag | **REFUTED** — the motion's own `button_mask` is required | §3.8 d6 |
| F5 | `_get_drag_data` is called on the control under the mouse | **REFUTED** — press-focus control, press-local `at_position` | §3.8 d3 (`b_get=0`) |
| F6 | hover and button picking share one (unclipped) space | **REFUTED** — hover clipped at the viewport edge, buttons not | §3.7 |
| F7 | `get_local_mouse_position()` inside `_gui_input` reflects the event | **REFUTED** — cursor-derived; stale under `push_input` | §3.5 |
| F8 | `ScreenDrag` delivery uses the event's `position` | **REFUTED** — tracked position + `relative` | §3.10 t2 |
| F9 | the tracked battery passes at HEAD | **REFUTED under load** — 5 row FAILs + 2 meta FAILs | §7 |

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (14, exec-checked)

`corpus/live/r100-scout/author-rows.py.txt` carries `ROWS` / `ROWS_PREFIX` as Python 5-tuples
for script **`r100_gui.gd`** (copy `proj/r100_gui.gd` → `corpus/fixtures/r100_gui.gd`; sha256
`dd826f6e7b74ba62fcfd175ab7a1cf0c40fd9712de4b33a18554930cf6dad073`):

| case | arm | signature head |
|---|---|---|
| `r100_gui_census` | `census` | `PASS r100_gui census dv=headless vpsize=(64.0, 64.0) …` |
| `r100_gui_routing` | `routing` | `PASS r100_gui routing s1_cc[[C:mb(b=1,p=1,…` |
| `r100_gui_hover` | `hover` | `PASS r100_gui hover h0=null h1=A ev=[A_in] …` |
| `r100_gui_motion` | `motion` | `PASS r100_gui motion m1[[S:mm(bm=0,pos=10.0,10.0,…` |
| `r100_gui_localpos` | `localpos` | `PASS r100_gui localpos lp_push_p[-] c[[C:mb(…pos=6.0,2.0…` |
| `r100_gui_cursor` | `cursor` | `PASS r100_gui cursor c0=(0.0, 0.0) … c8 ds=(0, 0)` |
| `r100_gui_clip` | `clip` | `PASS r100_gui clip cp0_vis=[P: (0.0, 0.0), S: (64.0, 64.0)] …` |
| `r100_gui_drag` | `drag` | `PASS r100_gui drag d1_at_threshold drag=0 calls=0 …` |
| `r100_gui_touch` | `touch` | `PASS r100_gui touch t1_push_a=- b=[B:st(i=0,p=1,dt=1,…` |
| `r100_gui_subvp` | `subvp` | `PASS r100_gui subvp v0_local=1 size=(64, 64) …` |
| `r100_gui_warp` | `warp` | `PASS r100_gui warp w0 dv=headless cursor=(0.0, 0.0) …` |
| `r100_gui_focus` | `focus` | `PASS r100_gui focus f0 owner=F f_focus=1 g_focus=0 …` |
| `r100_gui_render` | `render` | `PASS r100_gui render r0 tex_cls=ViewportTexture size=(64.0, 64.0) …` |
| `r100_gui_osmeta` | `osmeta` | `PASS r100_gui osmeta Thread[e=1,m=7] …` |

`EXPECTED_ERRORS = {'r100_gui_render': ('ERROR: Parameter "t" is null.',)}` — the dummy-storage
ERROR is the measured fact for the backbuffer-vacuity row.

`ROWS_PREFIX == ROWS`: every cell is byte-stable at **full-line** granularity (no ±1-tick
tails, no order vectors), so no load-robust cut is needed. `verify_rows.py` classified every
row against all 6 canonical + 2 loadtest receipts (112 classifications, merged
stdout+stderr exactly like `run_process`) → **0 rejections**, classifier segment sha
`749fa060…`.

### 6.2 What to pin and what not to pin

1. **Do not pin `Input.get_last_mouse_velocity()` after `Input.parse_input_event`** — it is
   time-based (`9.957696` observed in discovery) and will flake. Only the push-path zero
   (`vel=0.0`) is pinned.
2. **Do not pin object reprs.** `gui_get_hovered_control()` / `gui_get_focus_owner()` return
   `@Control@3:<Control#…>` — use `name`/tag (the probe names every control).
3. **Do not pin `OS.get_thread_caller_id()` / processor count / adapter names.** The `osmeta`
   row pins class existence + method counts only.
4. **Keep the drag cell in-viewport** (all coordinates < 64): targets at x≥64 are unreachable
   as drop targets because of the hover clip (the first draft of the drag cell failed exactly
   this way — §3.9).
5. **The `render` row needs its `expected_errors` entry**; without it the deterministic dummy
   ERROR rejects the row.
6. **No envelope/mode split is needed anywhere in this surface** — 14/14 cells single-valued
   ×6 + ×2 under load.

---

## 7. Capstone regression-residue: the tracked battery at HEAD is load-fragile

The sweep ran the tracked battery (HEAD bytes = r89 merge, `8cea888`/`61355e2`) once at host
loadavg **60–80** (concurrent lanes):

```
PASS lines: 229    FAIL lines: 7
FAIL overlap: exit=1 signature='PASS packed_scene=true'
FAIL transition: exit=1 signature='PASS valid_transition=true'
FAIL negative_transition: exit=1 signature='PASS invalid_destination_rejected=true'
FAIL audio_bus_route: exit=2 signature='PASS audio_bus_route in_tree=true … position_advanced=true'
FAIL audio_bus_route_invalid_control: exit=2 signature='AUDIO BUS CONTROL ASSERTION FAILED: requested invalid route silently fell back to Master'
FAIL error-clause surface meta
FAIL battery: corpus/live/runs/20261015T200615022811Z/verdicts.json
```

**Isolated re-runs in the same scratch (3 reps each):**

| row | isolated result | failure mode |
|---|---|---|
| `negative_transition` | **3/3 FAIL** | `SCRIPT ERROR: Cannot call method 'get_instance_id' on a null value.` at `controls/scene_transition_negative.gd:22` — `current_scene` still null one frame after `change_scene_to_packed`; the probe then times out at 120 frames |
| `overlap` | **3/3 FAIL** | `ERROR: overlap probe: signal occurred before physics overlap observation` |
| `transition` (positive) | 1/3 PASS | same `current_scene` readiness race |
| `audio_bus_route_invalid_control` | 3/3 PASS | flaked only in the battery run: `advanced=false` took the "observation unavailable" branch (different error text → signature miss) |
| `audio_bus_route` (positive) | 2/3 PASS | `advanced=false` (`position_advanced` needs 12 frames of audio advancement) |

**This is pre-existing, not r89-introduced [M]:** the r89 author's own five battery receipts
(`corpus/live/r89-author/battery-rep1..5.stdout`) show `FAIL transition` (rep1),
`FAIL negative_transition` (rep3), `FAIL audio_bus_route_invalid_control` (rep3),
`FAIL audio_playback` (rep1), `FAIL input_lattice_pre_frame` ×2, and `FAIL battery` on
reps1/3 — i.e. the same family flakes at lower load; reps2/4/5 are clean (the "235/235 ×2"
in the commit message).

**Root causes (measured, not inferred):**
1. **One-frame `current_scene` readiness.** `controls/scene_transition_probe.gd` /
   `scene_transition_negative.gd` (and `overlap_probe.gd`) read `current_scene` after a single
   `await process_frame`. The harness itself documents this class and applies a **scratch-only
   2-frame readiness patch to `causal_chain.gd`** (`run_battery.py:526`, comment: *"Godot
   4.7.2 may install current_scene one process frame after the change"*) — the same patch was
   never extended to the transition/overlap fixtures.
2. **Short audio observation window.** The audio fixtures require
   `get_playback_position()` to advance within 12 frames; under load `advanced=false` flips
   the invalid-route arm onto a different error branch (so the pinned signature misses) and
   fails the positive arm.
3. **Meta-gate coupling.** `probe_error_clause_surface`'s
   `census_bare_classifier_consistent` asserts
   `any_entry_matched == bare_classification_rejects` over all 55 censused rows. A flaked
   *negative* row emits none of its allowlisted lines (`any_entry_matched=False`) while still
   rejecting bare (`bare_classification_rejects=True`) → the gate flips and takes the whole
   battery with it. The gate was never exercised with a FAILing row before (r88 was 215/215
   PASS at low load), so this is a latent coupling: any load-induced row flake fails the
   battery twice.

**What this does not mean.** It is not evidence that the r89 rows are wrong (the r89 reviewer's
`PASS` on `61355e2` and the author's clean reps are on record); it is evidence that the battery
verdict is **load-conditional** on this host and that the sweep cannot certify HEAD as
green from a single run. Data for the operator, not a verdict: the fix candidates are the
harness's own 2-frame readiness pattern + a longer audio window, and the gate's assumption
needs a decision if FAIL rows are to be censused.

---

## 8. Remaining unknowns / not measured

- **Multi-touch** (`index>0`, two simultaneous touches) — only index 0 measured.
- **Drag preview** (`Control.set_drag_preview` content/positioning) — `force_drag(data, null)`
  used; previews were deliberately not instantiated.
- **`event_index` semantics 1..31** — r87 pinned the ≥32 refusal; the *meaning* of the field
  is still untested.
- **`in_local_coords=true` under a non-identity content scale** (stretch/scale modes) — the
  scratch viewport is identity (§3.1 `final=`), so the flag's transform path is unexercised.
- **SubViewport nesting** (SubViewport inside SubViewport), `CanvasLayer`-offset input mapping,
  and `gui_get_hovered_control` across nested viewports.
- **`Input.set_mouse_mode` / `DisplayServer.warp_mouse`** — only `Input.warp_mouse` and
  `Viewport.warp_mouse` measured.
- **Drag/drop under a real display server** (screen-edge targets, preview windows, external
  drops) — structurally unreachable headless.
- **The battery's load envelope** — flake rates sampled at loadavg 60–80 only; the exact
  threshold per row is unmeasured.
- **Portability**: every value is this host/build/`--headless`/64×64 root viewport/identity
  transform; no off-host claim.

---

## 9. Independent probe (frozen `probeParent` dispatch) — read-only audit

The frozen `probeParent` dispatched exactly one read-only `ufo-labrat` seat (coverage audit +
probe-hazard review). It reported **no exec/write tool** in its substrate and answered purely
from file reads (honest, no fabricated receipts): (1) confirmed the positional GUI-routing
surface has **zero** tracked coverage — existing fixtures use `InputEventAction`
(`button_activation.gd:14-17`, `checkbox_toggle.gd:17`, `button_group_selection.gd:23,28`,
`slider_adjust.gd:239-243,…`) and r87's mouse work is `Input.parse_input_event` state-only
(`input_lattice.gd:705-727`); (2) flagged the nondeterminism hazards this seat had already
measured and fixed (object reprs in `hover`/`focus`/`subvp`, `OS.get_thread_caller_id`, adapter
names, engine-computed velocity); (3) noted the drag arm might collapse if the engine needs a
real mouse state — falsified here (the drag path works; it needs the motion `button_mask` +
threshold, §3.8).

---

## 10. Host cleanup

- **Probe launches:** 84 canonical + 28 loadtest receipts retained (14 cells × 6 + × 2),
  plus ~60 discovery/smoke launches (`d2_*`…`d8_*` receipts plus superseded reps that were
  deleted after the probe was re-cut) — all `--headless`, all `timeout -s KILL`-bounded
  (30 s; none hit).
- **Sweep launches:** one full battery run (~250 harness Godot processes) + 15 isolated
  battery-row re-runs. No run left running; no tracked file touched.
- 8 `yes` hogs from `run_loadtest.sh` were killed at the end of the script (verified by the
  script's own kill loop).
- Writes: `reports/round-100/r100-scout.md`, `corpus/live/r100-scout/**`. No commit.

---

## 11. Evidence index

| path | content |
|---|---|
| `corpus/live/r100-scout/proj/r100_gui.gd` | the 14-cell probe (sha256 `dd826f6e…`) |
| `corpus/live/r100-scout/proj/discover2..8.gd` | discovery probes (cursor, localpos, drag mask/threshold/target, clip, grid) |
| `corpus/live/r100-scout/runs/r100_gui_<cell>.rep{1..6}.{out,err,rc}` | canonical receipts (84) |
| `corpus/live/r100-scout/runs/loadtest/` | 8-hog receipts (28) |
| `corpus/live/r100-scout/runs/d2_*`…`d8_*` | discovery receipts incl. `d7_grid.out` (G1–G6) and `d8_edge.out` |
| `corpus/live/r100-scout/runs/analyze_r100.{json,txt}` | per-cell census (`UNSTABLE=[]` both sections) |
| `corpus/live/r100-scout/author-rows.py.txt` | 14 verbatim rows + `EXPECTED_ERRORS` |
| `corpus/live/r100-scout/{make_author_rows,verify_rows,analyze_r100}.py` | row builder / production-classifier verifier / analyzer |
| `corpus/live/r100-scout/battery-r100-pre.{out,err}` | capstone battery sweep (229 PASS / 5 row FAIL / 2 meta FAIL) |
| `corpus/live/runs/20261015T200615022811Z/verdicts.json` | battery verdicts + `probe_error_clause_surface` census |
| `corpus/live/r89-author/battery-rep{1..5}.stdout` | the r89 author's own battery receipts (same flake family) |
| `corpus/fixtures/run_battery.py:526` | the harness's scratch-only 2-frame `current_scene` readiness patch for `causal_chain.gd` |
| `corpus/live/r100-scout/runs/probe.sha256` | probe hash |
