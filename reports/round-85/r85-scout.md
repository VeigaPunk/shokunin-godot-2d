# game-dev-2d round 85 — scout (g2d): the CanvasLayer / Viewport / Camera2D transform lattice, measured and pinned

Seat `SCOUT` (LEAF) | lane `g2d` | round 85 | host **devin** (this seat's brief carries
no wave id; r79/r80 headers record `shokunin-train-20261101-w19`).
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`f27f952`** (*r80: phys2d_motion lattice*).
Tracked Godot battery re-run by this seat: **139/139 PASS** — 132 `CASES` rows + 7 meta probes
(`corpus/live/r85-scout/runs/20261015T063658920705Z/verdicts.json`, `verdict=PASS`,
`probe_failing=false`) — that count already includes the r79 `phys2d_events` and r80
`phys2d_motion` rows (tracked at HEAD; neither touched here).

**No git mutation, no tracked file read-modified, no subagent.** Writes are this report and
`corpus/live/r85-scout/**` only. `corpus/fixtures/` was only *executed* with `--runs` pointed
at this seat's scratch dir; nothing under it was written, copied over, or regenerated.
r79 (interior-window contact/event), r80 (`body_test_motion`/`move_and_collide`/CCD), r81
(joints + layers), r82 (nav/query, in flight), r83 (input, in flight) and r84 (SceneTree
process-mode + timer/tween timing) are **not** re-measured; this arm is disjoint by
construction — before this round, none of the neighbouring scout reports (`reports/round-79`
… `reports/round-84`) mentions `CanvasLayer`, `canvas_transform`, `Viewport` or `Parallax`
(grep: zero hits); the only earlier `Viewport` mention anywhere in `reports/` is r18's
camera-limit discussion (`limit_right − visible_viewport_width/2`), which is the tracked
`camera_limit.gd` clamp, not this lattice.

**Backend scope (unchanged from r80/r81/r84's census, re-confirmed in every arm header this
round):** `physics/2d/physics_engine = DEFAULT`, `run_on_separate_thread = false`,
`physics_ticks_per_second = 60`, `default_gravity = 980`,
`physics/common/max_physics_steps_per_frame = 8`, `physics/common/physics_jitter_fix = 0.5`,
`application/run/delta_smoothing = true`, `application/run/fixed_fps = null`. **There is no
Jolt-2D backend in this build**; every row below is GodotPhysics2D.

**New environment fact this round pins the stage:** in `--headless` the **root viewport is
64×64** (`root.get_visible_rect().size == (64,64)`; `DisplayServer.get_name() == "headless"`),
so every camera-centred value below is measured against a 64×64 root with its centre at
`(32,32)`. A `SubViewport` sized 320×180 has its own `(160,90)` centre (`vp_subcam`).

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this session and no
GDScript/Python language server is installed. Semantic carriers are (a) fresh-process execution
receipts, (b) the tracked harness's **own** `classify_process` predicate extracted verbatim from
`corpus/fixtures/run_battery.py` lines 281–299 at the moment of extraction — sha256
`615d332ed428db66a03b6837d7a6ed86c4a3150609dc9c2838a11a51b50bbea3`, identical to the
r79/r80/r81/r84 extraction; the r81 fold has since shifted the function to line 333 in the
tree, the sha is the stable identifier), (c) line-exact engine error anchors in the receipts, (d) a
`ClassDB`/property census arm for the API surface. No cold-start empty result is recorded as
absence; every cited arm ran to `rc=0` inside the battery's own 8 s bound (worst measured arm
this round: **1.267 s**, `vp_worlds`).

**Legend:** **[M]** measured (fresh process, ×3 byte-stable unless stated); **[I]** inference;
**[A]** ablation (the pinned row was shown to FAIL when the pin is removed/flipped).

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/run_battery.py --runs corpus/live/r85-scout/runs` | 0 | **139/139 PASS** (`runs/20261015T063658920705Z/verdicts.json`) — host/build sanity on the tracked lattice |
| 2 | `godot --headless --path proj --script res://census_camera.gd` | 0 | API census (scratch): root viewport size/transforms, `Camera2D`/`CanvasLayer`/`Viewport`/`Parallax2D`/`ParallaxLayer`/`ParallaxBackground` property surfaces, live defaults, world-sharing booleans, `_draw`-headless probe |
| 3 | `… corpus/live/r85-scout/run_arms.py --mode discover` | 0 | 15 arms, one fresh Godot per arm — `arms-discover.json`, the receipts the frozen pins were transcribed from (automatically, into `pins.json`) |
| 4 | `… run_arms.py --mode verify --reps 3` | 0 | **15 rows × 3 reps = 45 processes; 15/15 PASS and `stable_bytes=true` for all 15** (15 distinct merged hashes across the 45 reps, i.e. one per arm), ablation matrix clean — `arms-verify.json` |
| 5 | `godot … --arm=diag_delta / diag_world_step / diag_draw / diag_cam_internal / diag_stretch` | 0 | the phase/model diagnostics the pins are read against (§3.1; non-pinned arms) |
| 6 | **merge rehearsal** (scratch copy only): insert the 15 rows verbatim into `corpus/live/r85-scout/merge-check/run_battery.py` and run the production battery | 0 | **174/174 PASS including 15/15 `camera_proc_*`** (`merge-runs/20261015T064210596514Z/verdicts.json`) — the paste block is proven armable through the real harness, not merely well-formed |

**Cited fresh Godot processes:** 15 discover + 45 verify + 5 diagnostics + 3 `cl_draworder`
stability re-runs + 1 census + the 139-case battery + the 174-case merge rehearsal, plus
per-arm smoke iterations during probe construction. Every arm ran in its own process with the
battery's 8 s bound, merged
stdout+stderr, judged by the production `classify_process`.

**Harness fidelity.** Every arm runs in the battery's exact launch shape —
`godot --headless --path <scratch> --script res://camera_proc.gd -- --arm=<name>` — and the
scratch `proj/` is a copy of `corpus/fixtures/` minus `run_battery.py`/dotfiles plus the probe
at the root, i.e. exactly where the author's fixture lands and exactly what the battery copies
per-case. One probe revision was forced by measurement: the first ×3 verify pass showed
`cam_phase` unstable in **exactly one token class** — the idle-phase write cell, whose
write/observe interleaving depended on how many idle iterations the host ran per physics frame
(rep2 differed from rep0 only in the `D.*` row). That cell was redesigned to be **armed once per
physics frame**, making the sequence 1:1 with physics frames; the final probe is stable ×3.
Every pinned token below is therefore either a physics-frame-indexed value or a boolean.

**Concurrent tree movement (not this seat's).** While this seat was running its verify pass,
another lane folded the r81 joints/layers block into the tracked harness: `corpus/fixtures/
phys2d_joints.gd` appeared (untracked) and 20 `phys2d_joints_*` `CASES` rows landed in
`corpus/fixtures/run_battery.py` (68 insertions; file mtime 06:40:57 UTC, **after** this seat's
139/139 battery receipt at 06:36:58 UTC, which therefore describes the r79/r80-folded state —
152 `CASES` rows are present in the tree as this report is written). Nothing in this seat's arm
reads, copies or depends on that block: the scratch `proj/` was snapshotted before it landed and
`camera_proc.gd` is self-contained (no imports, no scene resources). This seat wrote neither
file; the §6 paste anchor accounts for the moved tail.

---

## 1. The r85 arm — 15 cells, verbatim-armable

One new fixture `corpus/fixtures/camera_proc.gd` (scratch source:
`corpus/live/r85-scout/proj/camera_proc.gd`, 1151 lines, sha256
`6a94e052760e9a10019ff05b43983c9f4958ea859fc48f618ea6de70e20cbe29`), one `--arm=` per cell,
all `expected_exit = 0`, no cell is a crash. **The ready-to-paste `CASES` rows are in
`corpus/live/r85-scout/author-rows.py.txt` (10952 bytes, sha256 `2221a9e815d8deec…`) and
reproduced at §1.5.** Insert **immediately after the r80 `phys2d_motion_*` block and before
`("crash_spontaneous_sigabrt", …)`** — same ordering constraint the r79/r80 blocks encode
(`probe_descendant_pipe_eof` needs `detached_descendant_orphaned_alive` inside the descendant's
`sleep 8`, so no `CASES` rows may sit between `descendant_pipe_detached_control` and the meta
probes). The probe also carries five `diag_*` arms that no `CASES` row references (they print
`PASS camera_proc diag_*` lines of their own); they are inert for the battery and exist so the
model in §3.1 stays reproducible.

### 1.1 Camera composition + timing (5 arms)

| # | arm | class | decisive witness keys (measured, ×3 stable) | `expected_errors` |
|---|---|---|---|---|
| 1 | `cam_comp` | **the canvas-transform composition law, pinned as transforms** | `vp2=(64,64)`; no camera → `nocam` = identity; cam (0,0) → `s0` O=(32,32) = viewport/2; cam (100,50) → `s1` O=(-68,-18); zoom (2,2) → `s2` O=(-168,-68); + offset (10,20) → `s3` O=(-188,-108); `anchor_mode=FIXED_TOP_LEFT` → `s4` O=(-220,-140) (**no viewport/2 term**); restore → `s5` = `s0`; `n3 = canvas_transform * global_transform` **bit-exact** (`comp == n3`, `comp=1`); `get_canvas_transform() == viewport.canvas_transform` (`cam_vp=1`); `get_screen_transform() == get_global_transform_with_canvas()` (`screen=1`); `affine_inverse` round-trip (`inv=1`); `get_target_position()` **ignores** offset (`t3=(100,50)` vs `c3=(110,70)`), under the top-left anchor `c4=(126,86)` = pos+offset+viewport/2 | — |
| 2 | `cam_zoom_center` | **which world point sits at the screen centre under fractional zoom** | cam (10.5,-3.25) zoom 1.5 → `ct=(1.5,-0;-0,1.5;16.25,36.875)`; screen map `screens=[16.25,36.875\|32,32\|166.25,186.875\|5.375,42.5]`; the inverse-mapped screen centre is exactly the camera position (`center_world=10.5,-3.25 anchor_ok=1`); `dx=(1.5,0) dy=(0,1.5)`; a **1/60 camera move shifts the screen position by exactly -1.5/60 = -0.025** (`sub60=-0.0250 sub_ok=1`); `ct2` origin `16.225` | — |
| 3 | `cam_phase` | **camera writes are cached, not live: the exact visibility ladder** | `A` (pc=IDLE, write in `_physics_process`): `w1[32,32>32,32]` (invisible in the writing callback), `i1[22,32]` (visible at the **first idle observation of the same iteration**), `w2[22,32>22,32]`, …, `next[2,32]`; `B` (`force_update_scroll()` right after the write): `w1[32,32>12,32]` — **immediately visible in the same callback**; `C` (`process_callback=PHYSICS`): identical to `A` (`w1[32>32] i1[2,32] w2[2>2]`); `D` (write from the **idle** callback): `p1[32,32] w1[after=32,32] i1[-8,32] p2[-8,32] w2[after=-8,32] i2[-48,32] …` — invisible in the writing callback, visible at the next idle observation **and** at the next physics callback; `E` (observer lane at `process_priority=100`, i.e. runs after the writer in the same physics pass): `w1[after=32,32] o1[sees=32,32] i1[-18,32] …` — **not even a later-priority physics callback of the same frame sees the write** | — |
| 4 | `cam_subpixel` | **1/60 fixed-tps moves are sub-pixel exact** | 12 successive `+1/60` (x) / `+1/120` (y) moves → `n=12 distinct=12` origins `[32,32 \| 31.9833,31.9917 \| … \| 31.8167,31.9083]`; every sample is **byte-equal to the closed form** `32 − k/60` (`eq_exact=111111111111` and `eq_close=111111111111`); fractional zoom exact at 1.5 (`zoom15=31.7,31.85 want15=31.7,31.85 z15_ok=1`) and 0.5 (`zoom05=31.9,31.95 z05_ok=1`) | — |
| 5 | `cam_space` | **the four transform spaces, and the stretch transform's seat** | `vpr=[P:(0,0), S:(64,64)]`; `g0 == g1` (**global_transform is camera-independent**, `g_indep=1`); `wc == ct * global` (`wc_eq=1`); `sc == wc` in **every** configuration (`screen_eq=1`); `vx == ct` for a root item (`vp_eq=1`); a CanvasLayer child: `final`=identity, `lwc=(300,200)` camera-independent (`l_indep=1`), `lsc == lwc`, `lvx` = the layer transform (identity, **not** the camera transform); stretch phase `content_scale_factor=2` (mode DISABLED): `f2_final=Scale(2)`, `f2_ct` O=(-184,-84) — the camera's viewport half-size term becomes `half=(16,16)` instead of (32,32) — `f2_wc=(416,316)`, `f2_sc == f2_wc` (`sc_wc=1`), `f2_vx = final * canvas_transform` (`vx_final_ct=1`), the layer child stays `(300,200)` (`layer_unscaled=1`), and the restore is exact (`restored=1`) | — |

### 1.2 CanvasLayer (4 arms)

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 6 | `cl_stack` | **layer value is render metadata only; the transform is one decomposed value** | camera at (50,0): the root-level child tracks the camera (`root_wc=82,32` = 32+100−50) while **all three layers read the same** `wc=100,0` regardless of `layer = -1 / 0 / 7` (camera-independent); each layer child's `vx` = the layer's final transform (identity), not the camera canvas; `transform=Transform2D(0.5,(10,20))` → readbacks `off=10,20 rot=0.5 scale=1,1`; then `offset=(5,5)` → `xf` origin (5,5) with rotation preserved; then `scale=(2,2)` → basis doubled (`(1.7552,0.9589;-0.9589,1.7552)`), origin and rotation preserved; `wc7 == layer.get_final_transform() * child.global_transform` **bit-exact** (`comp7=1`); a CanvasLayer nested inside a layer child is **isolated** from the outer layer's transform (`nested[wc=100,0 isolated=1]`) | — |
| 7 | `cl_follow` | **`follow_viewport_*` is a transform source with a basis-only scale** | camera (100,50) zoom 2 → `ct=(2,-0;-0,2;-168,-68)`; `F0` (follow=false) `wc=100,0 fin=identity`; `F1` (follow=true, scale 1) `wc=32,-68 fin == ct` exactly; `F2` (scale 0.5) `fin=(1,0;0,1;-168,-68)` — **basis halved, origin unchanged**; `F3` (scale 2.0) `fin=(4,0;0,4;-168,-68)`; with a layer transform, `fin = follow_base * layer_transform` (`f2b fin=(-148,-28) = ct * Translate(10,20)`); after moving the camera the layer tracks (`moved[ct O=-568,32 wc=-348,72 fin=(-548,72)]`) | — |
| 8 | `cl_phase` | **a CanvasLayer write is live — same callback — and never touches the viewport transform** | `A` (offset write in `_physics_process`): `w1[cl=100,0 vp=32,32>cl=110,0 vp=32,32]` — visible **inside the writing callback**; `i1[cl=110,0]`, `w2[cl=110>120]`, … ; the viewport canvas transform stays `vp=32,32` throughout (the layer write does not touch it); `B` (whole-`transform` write) identical shape (`w1[100>105]`); `inv[wc=100,0 vp=32,32]` after `visible=false` → `true` (transforms keep computing) | — |
| 9 | `cl_draworder` | **the headless redraw-order witness: creation order, not layer order** | three layers created in the anti-sorted order `7, -1, 0` (plus a root-level tag `LR`, plus a `visible=false` layer tag `LH`), each child `queue_redraw()`ed every physics frame: `seq=L7@pf1\|L-1@pf1\|L0@pf1\|LR@pf1\|LR@pf2\|L7@pf2\|L-1@pf2\|L0@pf2\|…\|LR@pf4\|L7@pf4\|L-1@pf4\|L0@pf4`; `counts={L7:4, L-1:4, L0:4, LR:4}`; `first=[L7,L-1,L0,LR]` → `creation_order=1`; `layer_sorted=0` (never `L-1,L0,L7`); **`hidden_draws=0`** — a `CanvasLayer.visible=false` child never `_draw`s at all | — |

### 1.3 Viewport / World2D (3 arms)

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 10 | `vp_worlds` | **world sharing must be explicit; every world steps its own physics** | `share[d_own=1 d_shares=0 s_shares=1 o_shares=0]` — a `SubViewport` added to the tree **auto-creates its own World2D** (so `find_world_2d() != root`), an explicit `world_2d = root.find_world_2d()` **shares** (`s_shares=1`), an explicit `World2D.new()` does not; physics after 40 frames: `pos[br=0.0007,76.3 bs=40.0007,76.3 bo=0,207.919 bd=0.0007,76.3]` — the shared-world body lands on the **root** world's floor (`shared_floor=1`), the own-world body **falls through** (`own_fall=1`), and the root-world and sub-world bodies rest at the **same** height (`same_rest=1`); `contacts=[0,0,0,0]` (resting bodies report 0 in this build — positions are the witness, §5) | — |
| 11 | `vp_render_indep` | **physics is byte-independent of canvas/camera state — the requested pin** | four identical floor+body lanes: `V0` no camera, `V1` static camera (100,50) zoom 2, `V2` camera **moving and zooming every physics frame**, `ROOT` root world with a moving camera **and** a `CanvasLayer.offset` written every frame: after 30 physics frames `pos=[0.0007,76.3003 \| 0.0007,76.3003 \| 0.0007,76.3003 \| 0.0007,76.3003]` with `eq_exact=1` and `eq_4dp=1` — **all four byte-identical**; `root_ct=30.8158,32` (the canvas really was moving) | — |
| 12 | `vp_subcam` | **cameras are per-viewport; canvas transforms do not leak** | root `(64,64)` vs sub `(320,180)`; `r0=(32,32)`, `s0=(120,90)` = the sub's own centre minus its camera (40,0); moving the **root** camera → `r1=(-68,32)`, `s1 == s0` (sub untouched); moving the **sub** camera → `s2=(80,70)` = 160−80, 90−20, `r2 == r1`; `cams[sv=1 root=1]`; `iso[sub_only=1 root_only=1]` | — |

### 1.4 Parallax (3 arms)

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 13 | `par_layer` | **`ParallaxLayer` is inert without a `ParallaxBackground`; under one, the scroll law is exact** | root-level layer through camera 0/64/128/150 with `motion_scale=0.5`, `motion_mirroring`, `motion_offset`: the layer's position stays `lp=0,0` in **every** row and the child simply follows the camera (`cam64 wc=-32,32`, `cam150mirror wc=-118,32`) — the three motion properties do nothing there; under `ParallaxBackground` (whose `follow_viewport_enabled` defaults to **0**): `pbg0 lp=16,16`, `pbg64 lp=-16,16`, `pbg128 lp=-48,16` = `canvas_transform.origin * motion_scale`; `pbgmoff lp=-38,16` (+10 for `motion_offset=(10,0)`); `pbgms1 lp=-96,32` (scale 1 ⇒ world-locked); `pbgms0 lp=0,0` (screen-fixed); zoom 2 ⇒ `pbgz2 ct=-224,32 lp=-112,16` (= −224 × 0.5, `ign=0`); **`pbgmirror` leaves `lp` unchanged** (mirroring is render-level); a plain `CanvasLayer(follow_viewport_enabled=true)` does **not** drive the layer (`cl_follow lp=0,0`), nor does `follow=false` (`cl_nofollow wc=0,0`) | — |
| 14 | `par_2d` | **`Parallax2D` needs no parent and obeys `position = ct.origin * (scroll_scale − 1)`** | `scroll_scale=0.5`: `d0 wc=16,16` (ct O = 32,32), `cam64 wc=-16,16` (ct O = −32,32), `cam150rep wc=-59,16` (ct O = −118,32 ⇒ ×0.5) — i.e. `with_canvas = canvas_transform.origin * scroll_scale`; `ignore_camera_scroll=true` freezes it (`ignore wc=-16,16` at cam 64); `repeat_size=(100,0)`+`repeat_times=3`, `follow_viewport=true` and `screen_offset=(7,3)` leave the node transform **unchanged** (`rep100x3`, `follow`, `screen_off` rows); `scroll_offset` stays a setter readback `0,0` | — |
| 15 | `par_phase` | **parallax lands in the camera's frame, not one later** | camera written in `_physics_process` frame k; observation points `w{k}` (in the writing callback), `i{k}` (first idle observation of that iteration), `next` (next physics callback): `PL.w1[cam=32,32 pl=32,32 p2=16,16 pbl=16,16 pbc=16,16>…]` (all old), then `PL.i1[cam=-32,32 pl=-32,32 p2=-16,16 pbl=-16,16 pbc=-16,16]` — **`Parallax2D` and the `ParallaxBackground`-driven layer both sync in the same iteration's idle phase as the camera canvas transform** — `PL.w2[…=-32,32…]`, `PL.i2[cam=-96,32 … p2=-48,16 pbl=-48,16]`, `PL.next` | — |

### 1.5 The verbatim rows

All 15 rows are byte-exact in `corpus/live/r85-scout/author-rows.py.txt` (10952 bytes, sha256
`2221a9e815d8deecfbe3d2e243d2760eec76e5a530d9195f3970373c67c8d97b`), generated from the
`arms-verify.json` `signature` fields — which the verify run proved equal to the measured
`PASS` lines (`measured==signature` for 15/15). The literals are `repr()`-generated because
several arms carry quote-heavy payloads (dict/list renderings such as
`counts={ "L7": 4, "L-1": 4, … }` and `vpr=[P: (0.0, 0.0), S: (64.0, 64.0)]`) that a
hand-quoted literal would silently corrupt. The block was **exec-checked**: `ast.literal_eval`
of the 15 tuples reproduces 15 five-tuples whose signatures are byte-equal to the verify
receipts and whose flags/exit codes match, and `exec` of the generated error block reproduces
exactly the (empty) whitelist the verify run used. The row with the shortest signature
(162 bytes), verbatim:

```python
    ('camera_proc_vp_render_indep', 'camera_proc.gd', ['--arm=vp_render_indep'], 0,
     'PASS camera_proc vp_render_indep names=V0|V1|V2|ROOT pos=[0.0007,76.3003|0.0007,76.3003|0.0007,76.3003|0.0007,76.3003] eq_exact=1 eq_4dp=1 root_ct=30.8158,32.0000'),
```

```python
# --- expected_errors entries (merge into the expected_errors map inside execute()) ---
                # (no row in this block needs a whitelist)
```

`expected_errors` is **not** a field of a `CASES` 5-tuple — the battery resolves it from the
name-keyed dict inside `execute()` (`expected_errors = {...}.get(name, ())`; line 574 in the
tree as this report is written — the anchor text, not the line number, is the stable handle
because sibling folds move it). **No row in
this block needs an entry**: all 15 discover/verify receipts are `ERROR:`-clean (no deliberate
refusal is exercised by this lattice), so a stray entry would only widen a row's gate.

---

## 2. Fail-closed evidence (the pins are load-bearing) **[A]**

`arms-verify.json`: `verdict=PASS`, `bad=[]`, 15 rows. Per row: `rc=[0,0,0]`,
`verdicts=[PASS,PASS,PASS]`, `stable_bytes=true` — all three reps byte-identical on merged
stdout+stderr (`merged_sha256` per rep recorded; 15 distinct hashes for 45 reps, i.e. exactly
one per arm). Ablation matrix, judged by the **production** `classify_process`:

| ablation | expected verdict | 15/15 observed |
|---|---|---|
| signature dropped (`PASS camera_proc __absent__`) | FAIL | FAIL on all 15 |
| `expected_exit` flipped 0→1 | FAIL | FAIL on all 15 |
| `expected_errors` whitelist dropped | FAIL *iff the row emits errors* | PASS on all 15 (vacuous whitelist — correct semantics, no row emits `ERROR:`) |
| clean control | PASS | PASS on all 15 |

Every row is therefore a **two-clause** pin (exit + signature). One extra fail-closed check on
the *paste block* itself: `literal_eval` of the 15 generated tuples reproduces signatures
byte-equal to the verify receipts (0 mismatches) and `exec` of the generated error block
reproduces the exact (empty) whitelist dict. And one end-to-end rehearsal (§0 row 6): the 15
rows were inserted verbatim into a **scratch copy** of the tracked harness (which already
carried the r79/r80/r81 blocks at that moment) and the production battery re-run — **174/174
PASS, including all 15 `camera_proc_*` rows**, with the block's position in the paste order
verified by the run itself. The tracked `corpus/fixtures/run_battery.py` was never written by
this seat.

---

## 3. Headline measured findings

1. **The camera's canvas transform is a cached value; a CanvasLayer's is live** **[M]**. A
   `Camera2D.position` write inside a `_physics_process` callback is invisible in that callback
   **and to any other physics callback of the same frame**, even one that runs later by
   `process_priority` (`E.o1[sees=32,32]`), but is visible at the **first idle observation of
   the same iteration** (`A.i1[22,32]` for a write to x=10). `force_update_scroll()` collapses
   that latency to zero (`B.w1[32,32>12,32]` — visible in the writing callback).
   `process_callback = PHYSICS` is indistinguishable from IDLE at this granularity (`C` ≡ `A`).
   A write made in the *idle* phase is visible at the next idle observation and at the next
   physics callback (`D.p1[32] w1[after=32] i1[-8] p2[-8] …`). Contrast: `CanvasLayer.offset` /
   `CanvasLayer.transform` writes are visible **inside the writing callback** (`cl_phase
   A.w1[cl=100,0>cl=110,0]`) and never touch `Viewport.canvas_transform` — the layer transform
   is computed on read, the viewport canvas transform is camera-owned state.
2. **The composition law is `canvas_transform = Translate(viewport/2) ∘ Scale(zoom) ∘
   Translate(−(position + offset))` for the default `ANCHOR_MODE_DRAG_CENTER`, and
   `−(position + offset) · zoom` for `FIXED_TOP_LEFT`** **[M]** — pinned as exact transforms in
   `cam_comp` (5 states) and as a world→screen map in `cam_zoom_center`. `get_target_position()`
   **excludes** `offset`; `get_screen_center_position()` includes it (and under the top-left
   anchor is `pos + offset + viewport/2`). `get_canvas_transform() == viewport.canvas_transform`
   and `get_global_transform_with_canvas() == canvas_transform * global_transform` are
   **bit-exact**.
3. **Fixed-tps camera motion is sub-pixel exact and byte-reproducible** **[M]**: 12 successive
   1/60 moves give 12 distinct origins, each **byte-equal** to the closed form (`eq_exact`
   all-ones, both axes), including under fractional zoom 1.5/0.5; a 1/60 move at zoom 1.5
   shifts screen space by exactly −0.025.
4. **`global_transform` is camera-independent; the spaces do not overlap** **[M]**: `g0 == g1`
   across camera states; `screen_transform == with_canvas` in every configuration measured
   (including under a content-scale factor); `viewport_transform` = the camera canvas transform
   for root items, the **layer's** final transform for layer children, and
   `final_transform * canvas_transform` under stretch.
5. **The stretch transform sits above the canvas transform and does not reach canvas-layer
   children** **[M]**: `content_scale_factor = 2` makes `get_final_transform() = Scale(2)`,
   **halves the camera's viewport half-size term** (the camera's ct origin becomes −184,−84 for
   cam (100,50) zoom 2, i.e. `(16,16) − 2·(100,50)`), leaves `with_canvas` = `ct * global`, makes
   `viewport_transform = final * canvas_transform`, and leaves a CanvasLayer child's
   `with_canvas` at (300,200) — layer children do not inherit the stretch scale.
6. **`CanvasLayer.layer` is render-order metadata, and the only headless ordering witness is
   creation order** **[M]**. Layers −1/0/7 give identical transforms; nested layers are
   transform-isolated; `transform`/`offset`/`rotation`/`scale` are one decomposed value
   (write one, the others re-derive). In headless, `_draw` **does** run: redraw order follows
   **creation order** (first frame `L7,L-1,L0,LR`; later frames root-first `LR,L7,L-1,L0`),
   never the layer value, and a `CanvasLayer.visible=false` layer's child gets **zero** `_draw`
   calls while its transforms still compute.
7. **`follow_viewport_enabled` substitutes the camera canvas transform for the layer's own, and
   `follow_viewport_scale` scales its basis only** **[M]**: scale 1 → `final == ct`; 0.5 → basis
   halved with the origin unchanged; 2.0 → basis doubled; the layer's own transform composes
   *inside* (`final = follow_base * layer_transform`); the layer tracks camera motion.
8. **A `SubViewport` does not share the parent's World2D by default — it auto-creates one** **[M]**,
   and **every world steps its own physics**: a body under an explicitly shared world lands on
   the root world's floor; a body in an own world falls through; two bodies in different own
   worlds rest at byte-equal heights. Cameras are per-viewport (`vp_subcam`), and neither
   camera's canvas transform leaks into the other.
9. **Physics is byte-independent of canvas/camera state** **[M]** — the round's requested pin:
   four lanes (no camera / static camera / camera moving+zooming every frame / root world with a
   moving camera **and** a per-frame CanvasLayer offset write) produce **byte-identical** body
   positions after 30 frames (`eq_exact=1`, `eq_4dp=1`, `0.0007,76.3003` in all four).
10. **`ParallaxLayer` is inert unless parented to a `ParallaxBackground`; `Parallax2D` is
    self-sufficient** **[M]**. Root-level, the layer's position never changes and
    `motion_scale`/`motion_mirroring`/`motion_offset` are unobservable; under a
    `ParallaxBackground` (whose `follow_viewport_enabled` defaults to **false**) the background
    drives it to `layer.position = canvas_transform.origin * motion_scale + motion_offset`,
    verified at camera 0/64/128, at scale 0/0.5/1.0 and at zoom 2; `motion_mirroring` never
    changes the node transform (it is a render-level repeat). `Parallax2D` obeys
    `with_canvas = canvas_transform.origin * scroll_scale`; `ignore_camera_scroll` freezes it;
    `repeat_size`/`repeat_times`/`follow_viewport`/`screen_offset` leave the node transform
    unchanged here.
11. **Parallax has no extra frame of latency** **[M]**: with a physics-phase camera write,
    `Parallax2D` and the `ParallaxBackground`-driven layer position both land in the **same
    iteration's idle phase** as the camera canvas transform (`PL.i1[cam=-32,32 p2=-16,16
    pbl=-16,16]`), never one frame later.

### 3.1 The phase model the pins are read against **[M]**

From the non-pinned diagnostic arms (one fresh process each; all values this host/build):

- **Headless frame shape.** `diag_delta`: `_physics_process` deltas are **exactly**
  `0.016666667` on every frame (`same=1`), while idle deltas vary per iteration
  (`0.0167/0.0106/0.000004/0.00695/0.0069`) — so every pinned number in this round is indexed by
  **physics frames**, never by idle iterations. Headless runs **2–3 idle iterations per physics
  frame** (visible as the process-frame counter gaps), which is exactly why the one unstable
  first-pass cell (the idle-write row) was redesigned to be armed once per physics frame.
- **Draw timing.** `diag_draw`: `queue_redraw()` from a physics callback produces one `_draw`
  per frame in the *same* physics frame (`draws=4`, `seq=TD@pf1|TD@pf2|TD@pf3|TD@pf4`), so the
  redraw-order witness in `cl_draworder` is frame-indexed and reproducible.
- **Where the camera syncs.** `diag_cam_internal`: a writer lane (`process_priority=0`) and an
  observer lane (`process_priority=100`, so it runs after the writer) in the same physics pass
  both see the **old** value; the new value appears at the first idle observation of that
  iteration. The sync therefore happens **between the end of the physics callback pass and the
  first idle observation** of the same iteration (whether it is the tail of the physics phase or
  the head of the idle phase is not discriminated — §5).
- **World stepping.** `diag_world_step`: a body created inside a `SubViewport`'s own world falls
  (`start=0,0 → after10=0,12.1957`), i.e. sub-viewport worlds are stepped by the same physics
  loop.
- **Stretch.** `diag_stretch` is the source of the `cam_space` stretch phase: `final` picks up
  `Scale(2)`, the camera's half-size term becomes (16,16), and the layer child is unaffected.

---

## 4. Falsification list (measured negatives)

| # | plausible claim | measured result | witness |
|---|---|---|---|
| F1 | a camera write is visible later in the same physics phase | **False**: not visible in the writing callback, and not to a lane with `process_priority=100` in the same pass | `cam_phase` A/E |
| F2 | a camera write needs no special call to be visible in the same callback | **False** for the same callback (only the first idle observation sees it); `force_update_scroll()` is what makes it immediate | `cam_phase` A/B |
| F3 | `process_callback = PHYSICS` makes a physics-phase camera write same-callback | **False**: `C` is byte-identical to `A` | `cam_phase` C |
| F4 | an idle-phase camera write is visible in the same idle callback | **False**: `D.w1[after=32,32]`, visible at the next idle observation (`D.i1[-8,32]`) | `cam_phase` D |
| F5 | `Camera2D.offset` moves `get_target_position()` | **False**: target stays (100,50), screen centre becomes (110,70) | `cam_comp` |
| F6 | `get_screen_transform()` adds the viewport stretch transform | **False** here: it equals `get_global_transform_with_canvas()` under `content_scale_factor=2` | `cam_space` |
| F7 | a CanvasLayer child inherits the viewport's stretch scale | **False**: layer child stays (300,200) at factor 2 | `cam_space` |
| F8 | a `CanvasLayer.offset`/`transform` write lands next frame | **False**: visible inside the writing callback | `cl_phase` |
| F9 | a CanvasLayer write moves `Viewport.canvas_transform` | **False**: `vp=32,32` in every observation | `cl_phase` |
| F10 | `CanvasLayer.layer` changes transforms | **False**: layers −1/0/7 read identical `wc`/`vx` | `cl_stack` |
| F11 | a nested CanvasLayer composes with the outer layer's transform | **False**: inner child reads (100,0) with the outer transform (10,20,rot 0.5) applied | `cl_stack` |
| F12 | `visible=false` only suppresses rendering, children still redraw | **False**: `hidden_draws=0` (transforms still compute) | `cl_draworder` |
| F13 | headless redraw order follows `CanvasLayer.layer` | **False**: creation order (`layer_sorted=0`) | `cl_draworder` |
| F14 | `follow_viewport_scale` scales the layer's origin | **False**: origin unchanged at 0.5 and 2.0, basis scales | `cl_follow` |
| F15 | a `SubViewport` shares its parent's World2D by default | **False**: it auto-creates its own (`d_own=1 d_shares=0`) | `vp_worlds` |
| F16 | a sub-viewport's world is not stepped by the physics loop | **False**: its bodies fall and land | `vp_worlds`, `diag_world_step` |
| F17 | a physics result depends on camera/canvas position | **False**: four lanes, byte-identical positions | `vp_render_indep` |
| F18 | a sub-viewport camera moves the root canvas transform (or vice versa) | **False**: `iso[sub_only=1 root_only=1]` | `vp_subcam` |
| F19 | a root-level `ParallaxLayer` scrolls | **False**: `lp=0,0` for every camera state; the child only follows the canvas transform | `par_layer` |
| F20 | `motion_mirroring` moves the layer | **False**: `pbgmirror lp == pbg128 lp` | `par_layer` |
| F21 | a plain `CanvasLayer(follow_viewport_enabled=true)` drives `ParallaxLayer` motion | **False**: `lp=0,0` | `par_layer` |
| F22 | `ParallaxBackground` defaults to `follow_viewport_enabled=true` | **False**: `follow=0` measured | `par_layer` |
| F23 | `Parallax2D` needs a CanvasLayer/parent to scroll | **False**: root-level it obeys `ct.origin * scroll_scale` | `par_2d` |
| F24 | parallax offsets land one frame after the camera | **False**: same iteration's idle phase | `par_phase` |
| F25 | `Parallax2D.repeat_size`/`repeat_times`/`screen_offset`/`follow_viewport` move the node transform | **False** in this arm: the node transform is unchanged in all four rows | `par_2d` |

---

## 5. Remaining unknowns / not measured

- **The stretch-mode derivation is unexplained [I]**: `content_scale_mode = CANVAS_ITEMS` or
  `VIEWPORT` with `content_scale_factor = 2` yields `final = (0.1111,0;0,0.1111;0,14)` and a
  camera ct origin of `(88,62)` — numbers that depend on the default `content_scale_size`
  (1152×648, unset in `project.godot`) against the 64×64 headless window. Only the
  **DISABLED-mode factor-2** case is pinned (`cam_space`); the CANVAS_ITEMS/VIEWPORT cases are
  observed, deterministic on this host, and left out of the pin deliberately.
- **The camera sync's exact seat is not discriminated [I]**: the transition is bounded by "end of
  the physics callback pass" and "first idle observation of the same iteration"; `diag_cam_internal`
  rules out *any* physics callback (even later-priority) but cannot separate a physics-phase tail
  pass from a pre-idle head pass.
- `ParallaxBackground.scroll_offset` / `scroll_base_scale` / `limit_begin/end` /
  `scroll_ignore_camera_zoom` (only its default `0` readback is pinned) and `Parallax2D.autoscroll`
  (idle-delta driven, deliberately not armed) are outside this arm; the `repeat_*` **copies** are
  render-level and were not observable (only the node transform was measured).
- `Camera2D` smoothing, drag margins and limits are the tracked battery's `camera_follow.gd` /
  `camera_limit.gd` territory and are **not** re-measured here.
- Resting rigid bodies report `get_contact_count() == 0` in `vp_worlds` (the positions are the
  pinned witness); whether that is sleep-related was not investigated.
- `Viewport.get_mouse_position()` / screen→world input mapping is unmeasurable headless (no
  input device) and was not attempted.
- No threaded twin (`physics/2d/run_on_separate_thread=true`) was armed for these 15 cells.
- **Jolt-2D**: absent from this build (r80 census, re-confirmed) — no claim.
- All values are **this host, this build, headless, 64×64 root viewport, 60 tps, GodotPhysics2D,
  these scenes** — no portability claim. The idle/physics iteration ratio (2–3 idle iterations
  per physics frame) is a host-timing shape and is deliberately absent from every pinned token.

---

## 6. Author directives (exact)

1. Copy `corpus/live/r85-scout/proj/camera_proc.gd` → `corpus/fixtures/camera_proc.gd`
   (1151 lines, self-contained: no resources, no imports, sha256
   `6a94e052760e9a10019ff05b43983c9f4958ea859fc48f618ea6de70e20cbe29`).
2. Append the 15 `CASES` rows from `author-rows.py.txt` / §1.5 **ahead of the crash/descendant
   tail** — immediately after the last `phys2d_*` block already inserted there (the r80
   `phys2d_motion_*` block at HEAD; the r81 `phys2d_joints_*` block if it has landed) and before
   `("crash_spontaneous_sigabrt", …)`. Same ordering constraint the r79/r80/r81 blocks encode
   (the `sleep 8` orphan window forbids `CASES` between `descendant_pipe_detached_control` and
   the meta probes). Paste the literals exactly as the file carries them (`repr()`-generated;
   do not re-quote by hand).
3. **Merge no `expected_errors` entry**: all 15 rows are `ERROR:`-clean and the block's error
   section is the empty comment line. A stray entry would silently widen a row's gate.
4. Free every node the fixture creates before `quit()` (the probe's `_nodes` list, freed in
   `_finish`); `World2D.new()` instances are owned by their `SubViewport`s and are freed with
   them, so no `RID allocations were leaked` line is expected — the 15 discover/verify receipts
   carry zero `ERROR:` lines.
5. Never print object ids, RIDs, or addresses. Every pinned value is a number, bool, vector,
   transform, class name, or a node *name*; `get_canvas_transform()`/`get_final_transform()`
   comparisons are pinned as **booleans**, never as identity or addresses.
6. Do not borrow r79's/r80's/r81's/r84's gate texts. **This block introduces no new engine error
   text at all** (no deliberate refusal is exercised).
7. Keep the frame budgets: the longest arm runs 40 physics frames (`vp_worlds`, measured wall
   1.267 s max across 3 reps) against the battery's 8 s bound.
8. The five `diag_*` arms are non-pinned diagnostics (they print `PASS camera_proc diag_*` lines
   of their own). They are inert for the battery; keep them if the model in §3.1 should stay
   reproducible, or drop them — either way **no `CASES` row may reference them**.
9. `vp_worlds`' `contacts=[0,0,0,0]` field is pinned **because** resting bodies report zero
   contacts here while the positions prove the landings — do not "fix" it to look like a
   contact witness.
10. The fixture name `camera_proc.gd` deliberately does not collide with the tracked
    `camera_follow.gd` / `camera_limit.gd` rows; do not merge them.

---

## 7. Evidence index

All under `corpus/live/r85-scout/` unless noted. `MANIFEST.sha256` (13 hashes, this report
included) covers the probe, the census, the runner, the frozen pins, the row generator, both
battery receipts, the merge rehearsal copy and every cited receipt.

| artefact | path | sha256 (prefix) |
|---|---|---|
| probe (author fixture source) | `proj/camera_proc.gd` | `6a94e052760e9a10` |
| API census (scratch) | `proj/census_camera.gd` | `4cbf8ef1bfaee7d5` |
| runner (classifier extractor + verify + ablations) | `run_arms.py` | `b9a50582c12c0496` |
| frozen pins (15 literals, 0 whitelists) | `pins.json` | `c1073f0fcad37c83` |
| discovery receipts | `arms-discover.json` | `937b76b6ce3443cd` |
| verify receipts (15×3, ablations, per-rep raw streams) | `arms-verify.json` | `fb2ffa6321d1b674` |
| paste-ready rows (exec-checked) | `author-rows.py.txt` | `2221a9e815d8deec` |
| row generator | `make_author_rows.py` | (see `MANIFEST.sha256`) |
| battery receipt (139/139, host sanity, pre-r81-fold state) | `runs/20261015T063658920705Z/verdicts.json` | `9333c9a022f207dc` |
| merge rehearsal receipt (174/174 incl. 15/15 r85 rows) | `merge-runs/20261015T064210596514Z/verdicts.json` | (see `MANIFEST.sha256`) |
| merge rehearsal copy of the harness (scratch, 15 rows pasted) | `merge-check/run_battery.py` + `merge-check/camera_proc.gd` | (see `MANIFEST.sha256`) |
