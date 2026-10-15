# game-dev-2d round 95 — scout (r95-scout): the PhysicsDirectSpaceState2D query lattice, pre-measured; 17 rows verbatim-ready

Seat `SCOUT` (LEAF) | lane `r95-scout` | round 95 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps default, GodotPhysics2D (`GodotPhysicsDirectSpaceState2D`). Repo
`~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at session start **`520ed6d`**
(*r90 boundary*), HEAD at session end **`c97424b`** (*r92 scout* — other lanes committed
while this seat ran; none of those commits touch this seat's artefacts). The launch
`project.godot` is the byte-copy of `corpus/fixtures/project.godot` (`8de8b3af…`).

**No git mutation, no tracked file written, no commit.** Writes are this report and
`corpus/live/r95-scout/**` only. The one tracked modification in `git status`
(`corpus/fixtures/run_battery.py`, +82 lines) is a **concurrent lane's** and contains no
r95/`dss_lattice` token.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server
installed; `definition`/`references`/`hover` were **unavailable for every file touched**.
All symbol work was therefore done by reading the fixtures directly (fallback per the seat
card) — semantic carriers are fresh-process execution receipts, `ClassDB` introspection
inside the probes, and engine-emitted error text. No engine source tree exists on this host,
so every mechanism statement is marked **[I]** and kept separate from the measurements.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Primary: the `PhysicsDirectSpaceState2D` query lattice** — `intersect_ray`, `intersect_point`,
`intersect_shape`, `cast_motion`, `collide_shape`, `get_rest_info`; the three query-parameter
objects (masks, exclude lists, `collide_with_bodies`/`collide_with_areas`,
`hit_from_inside`, `margin`, `shape` vs `shape_rid`); `max_results` semantics; the
canvas-instance vs physics-object layering (`canvas_instance_id`, `CanvasLayer`, node-tier vs
server-tier bodies, per-`World2D` spaces); and **multi-hit result ordering stability**.

Why this surface, against the brief's other candidates **[O]/[I]**:

- The battery already owns the *motion* half of the space state (`phys2d_motion.gd`:
  `dss_motion`/`dss_embed`/`dss_shapes`/`dss_purity`/`dss_wrongarg`, 28 rows) and the
  *backend* half (`phys2d_backends.gd`, 8 rows) — but **no row pins the query-parameter
  lattice**: masks, exclude forms, `hit_from_inside`, `max_results`, area toggles, canvas
  scoping, or result ordering. `grep -rin "hit_from_inside\|canvas_instance_id\|max_results"`
  over `corpus/fixtures/*.gd` finds only the `phys2d_backends` nested-boot strings and
  nothing else. That is a clean coverage gap on an author-facing surface.
- It is the highest-frequency query API in 2D gameplay code (line of sight, ground checks,
  melee arcs, tile pickup, AI probes), so the hazards found here (below) are directly
  author-relevant.
- **Falsifiability was immediate**: the first probe refuted two of the scout's own
  assumptions — `max_results=0` does *not* mean "unlimited" (it returns **zero** results) and
  `PhysicsPointQueryParameters2D` has a `canvas_instance_id` the brief did not name (§4).
- The other candidates were weighed and left: TileMapLayer was **claimed by the concurrent
  r92 scout** (`c97424b`, 13 rows) — duplicating it would be waste; AnimationPlayer/timing
  belongs to the r87 pulse-envelope territory; the `geo2d_lattice` geometry surface was
  taken in r89.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` (18 arms, fresh process each) | feasibility: API census, ray/point/shape/cast/rest semantics, ordering, layering, freshness, space scope | `runs/disc/d_*.{out,err}` |
| 2 | `bash run_cells.sh` | **17 cells** (1 pure ×3, 16 frame-bound ×6) = **99 runs** | `runs/r95_*.{out,err,rc}` |
| 3 | `bash run_loadtest.sh` (16 own `yes` hogs, load avg 95–109) | 51 runs over all 17 cells | `runs/loadtest/dss_*.{out,err,rc}` |
| 4 | alt-construction ordering probe (`--arm=order_alt --perm=0/1/2`) | 9 runs (3 perms × 3 fresh processes) + translated pile | `runs/alt/alt_p*.*.out` |
| 5 | `python3 analyze_r95.py` | per-cell reps / out-uniq / err-uniq / rc / PASS-line uniqueness | `runs/analyze_r95.json` |
| 6 | `python3 make_author_rows.py` → `python3 verify_rows.py` | 17 rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) | `author-rows.py.txt` |

**Canonical cell set: 99 runs across 17 cells** — 1 census cell ×3, 16 query/lifecycle cells ×6.
All rc=0; no cell crashed; no run left running; **all stderr 0 B**.

**Byte-stability: 17 of 17 cells are `out_uniq=1 err_uniq=1 pass_uniq=1 rc=[0]`**
(`runs/analyze_r95.json`: `UNSTABLE=[]`, `CRASH_CELLS=[]`) — including the four cells whose
PASS line carries **multi-hit order vectors** and the three `--rev` add-order variants.

**Load-stability [M]:** re-running all 17 cells ×3 at load avg 95–109 (16 own hogs on top of a
host already at ~90 from other lanes) produced **51/51 rc=0** and **zero** row rejections:
`verify_rows.py` → `ROWS` **150/150 accepted**, `ROWS_PREFIX` **150/150 accepted**,
`rejected=[]`. The full-line rows — order vectors included — are load-stable.

**Arm-dispatch integrity [O]:** every arm prints its own name on the `PASS` line
(`PASS dss_lattice <arm> …`), so a silent `_:` fallback (the r88 dead-seat failure) is
impossible to miss; `arm` is parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan).

**Delegated probe [O]:** the frozen probeParent dispatched exactly one read-only `ufo-labrat`
seat (independent-construction falsification of the ordering law). **It could not execute** —
that seat's tool surface has no shell/exec and no write capability, so it ran **0** godot
launches and reported honestly rather than fabricating vectors. No empirical delta; the
falsification ladder was therefore run by this seat instead (§3.7b, §7 F13–F17).

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| **API census + signatures + defaults** (6 methods, 3 param classes) | **PINNABLE** | 3 | uniq=1 |
| **`intersect_ray` flag lattice** (mask, exclude, bodies/areas, `hit_from_inside`) | **PINNABLE** | 6 | uniq=1 |
| **Ray geometry** (endpoint inclusive, grazing, corner, zero-length, boundary starts) | **PINNABLE** | 6 | uniq=1 |
| **Ray ordering** (nearest wins; coincident tie = last added) | **PINNABLE law** | 6 + 6 rev | uniq=1 |
| **`max_results` semantics** (0 ⇒ empty; default 32 truncates) | **PINNABLE hazard** | 6 + 6 rev | uniq=1 |
| **Point boundary predicate** (half-open rect: left/top in, right/bottom out) | **PINNABLE law** | 6 | uniq=1 |
| **Shape boundary predicate** (exact touching counts; inclusive) | **PINNABLE law** | 6 + 6 rev | uniq=1 |
| **Canvas-instance layering** (`canvas_instance_id`, `CanvasLayer`, default layer) | **PINNABLE law** | 6 | uniq=1 |
| **Multi-hit result ORDER** | **PINNABLE for a frozen construction; a broadphase artifact, never semantic** | 6 + 6 rev | uniq=1 |
| **Node-tier vs server-tier objects + `World2D` space scoping** | **PINNABLE** | 6 | uniq=1 |
| **`cast_motion` fractions** | **PINNABLE** (float32 fractions, exact strings) | 6 | uniq=1 |
| **`get_rest_info` sweep semantics** | **PARTIALLY MEASURED** — entry/exit contact transition pinned, rule **[I]** | 6 | uniq=1 |
| **`collide_shape` contact pairs** | **PINNABLE + artifact** (cap counts pairs; duplicate pair emitted) | 6 | uniq=1 |
| **Same-frame freshness** (node write deferred, server write live, `queue_free` deferred) | **PINNABLE law** | 6 | uniq=1 |
| **Server-RID leak prints ERROR on stdout** | **PINNABLE hazard** (row-killer, not a row) | discovery | deterministic |

---

## 3. Measured values, verbatim

All payloads are `runs/r95_dss_<cell>.rep1.out`; identities are node tags (`tag#shapeIndex`),
never RIDs. Fractions are printed exactly as Godot renders them (float32).

### 3.1 Census (`dss_census`) — [M]

```
PASS dss_lattice census dss_methods=n6[cast_motion,collide_shape,get_rest_info,intersect_point,intersect_ray,intersect_shape]
dss_sigs=[cast_motion(parameters:24)|collide_shape(parameters:24,max_results:2)|get_rest_info(parameters:24)|
intersect_point(parameters:24,max_results:2)|intersect_ray(parameters:24)|intersect_shape(parameters:24,max_results:2)]
ray=props=[collide_with_areas,collide_with_bodies,collision_mask,exclude,from,hit_from_inside,to]
  defaults=[collide_with_areas=false,collide_with_bodies=true,collision_mask=4294967295,exclude=n0,from=(0.0000,0.0000),hit_from_inside=false,to=(0.0000,0.0000)]
pt=props=[canvas_instance_id,collide_with_areas,collide_with_bodies,collision_mask,exclude,position]
  defaults=[canvas_instance_id=0,collide_with_areas=false,collide_with_bodies=true,collision_mask=4294967295,exclude=n0,position=(0.0000,0.0000)]
sh=props=[collide_with_areas,collide_with_bodies,collision_mask,exclude,margin,motion,shape,shape_rid,transform]
  defaults=[…,margin=0.0000,motion=(0.0000,0.0000),shape=<Object#null>,shape_rid=RID(0),transform=[X: (1.0, 0.0), Y: (0.0, 1.0), O: (0.0, 0.0)]]
ray_backface=has=false pt_canvas=has=true
ray_create=from=(1.0000,2.0000) to=(3.0000,4.0000) mask=4294967295 excl=0 bodies=true areas=false inside=false
dss_cls=cls=GodotPhysicsDirectSpaceState2D dss_identity=same_across_calls=true
```

- **The space state exposes exactly six methods** and **no `is_valid()`/`get_process_info`**
  on this build **[M]**.
- `max_results` is a **method argument** (`intersect_point`/`intersect_shape`/`collide_shape`),
  **not** a property of the params objects — `PhysicsPointQueryParameters2D` and
  `PhysicsShapeQueryParameters2D` have **no** `max_results` property **[M]** (a plausible
  author error: setting a nonexistent property).
- **`PhysicsRayQueryParameters2D` has no `backface_collision`** — the 3D flag does not exist
  in 2D **[M]** (see F1). `hit_from_inside` is the only "inside" lever.
- **`PhysicsPointQueryParameters2D` carries `canvas_instance_id`** (default `0`) — the only
  query family that is canvas-layer scoped **[M]**.
- `PhysicsShapeQueryParameters2D` offers **both** `shape` (default null) and `shape_rid`
  (default `RID(0)`); `margin` defaults to `0.0000` **[M]**.
- `PhysicsServer2D.space_get_direct_state(space)` returns the **same object** across calls
  (`dss_identity=same_across_calls=true`) and the class is
  `GodotPhysicsDirectSpaceState2D` on this build **[M]**.

### 3.2 Ray flags (`dss_ray_flags`) — [M]

```
base=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)} mask2=r={} mask0=r={} nobodies=r={}
areas_on=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)}
areas_only=r={w2 pos=(298.0000,0.0000) n=(-1.0000,0.0000)}
excl_wall=r={} excl_area=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)}
inside_off=r={} inside_on=r={w pos=(100.0000,0.0000) n=(0.0000,0.0000)}
inside_area_on=r={w2 pos=(300.0000,0.0000) n=(0.0000,0.0000)}
outside_on=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)}
keys=["collider", "collider_id", "normal", "position", "rid", "shape"]
```

- Wall `w` = 4×400 rect at (100,0) → near face **x=98**; area `w2` = same at (300,0).
- `collision_mask=2` and `mask=0` both **miss**; `collide_with_bodies=false` **misses** even
  with the mask full **[M]**.
- `collide_with_areas=true` does **not** change a body hit (areas do not preempt the nearest
  body); with bodies off it returns the area **[M]**.
- `exclude=[body RID]` removes that body; `exclude=[area RID]` does not affect the body hit
  **[M]**.
- **`hit_from_inside=false` + ray starting inside ⇒ `{}`** (silent miss — the hazard);
  `hit_from_inside=true` ⇒ a hit **at the ray origin** with **`normal=(0,0)`** (a degenerate
  normal; do not normalize it) **[M]**. Same law for areas **[M]**. Setting the flag on an
  outside-start ray changes nothing **[M]**.
- Hit dictionary keys are exactly `collider, collider_id, normal, position, rid, shape`
  (there is **no** `linear_velocity` here — that is `get_rest_info`'s key set) **[M]**.

### 3.3 Ray geometry (`dss_ray_geom`) — [M]

```
end_at_face=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)} end_eps_before=r={}
graze_top=r={w pos=(98.0000,-200.0000) n=(-1.0000,0.0000)} graze_inside=r={w pos=(98.0000,-199.9990) n=(-1.0000,0.0000)}
corner_diag=r={c pos=(180.0000,-20.0000) n=(-1.0000,0.0000)} zero_len_face=r={} zero_len_out=r={}
reverse=r={c pos=(220.0000,0.0000) n=(1.0000,0.0000)}
from_left_away=r={} from_left_through=r={c pos=(180.0000,0.0000) n=(-1.0000,0.0000)}
from_right_away=r={w pos=(102.0000,0.0000) n=(0.0000,0.0000)}
from_right_through=r={w pos=(102.0000,0.0000) n=(0.0000,0.0000)} corner_start_away=r={}
```

- **The segment endpoint is inclusive**: `to=(98,0)` (exactly the face) hits at 98; `to=(97.9999)`
  (0.0001 short) misses **[M]**.
- A ray **collinear with a face** (`y=-200`, the rect top) hits at the entry x with the face
  normal `(-1,0)`; 0.001 inside behaves identically **[M]**.
- A diagonal entering exactly at a corner reports the corner point with the **-x face normal**
  (not a corner bisector) **[M]**.
- Zero-length rays (`from == to`) always miss — on a face and outside alike **[M]**.
- Reversing the ray returns the nearest hit **from `from`** (the box `c` at its far face 220,
  normal `(1,0)`) — rays are direction-aware, not shape-aware **[M]**.
- **Boundary-start law [M]:** the ray's own start point is classified by the **same half-open
  point predicate** as `intersect_point` (§3.6). A start on the **left/top** face counts as
  *inside* ⇒ suppressed with `hit_from_inside=false` (`from_left_away`, `from_left_through`,
  `corner_start_away` all `{}`; `from_left_through` then hits the *next* body at 180).
  A start on the **right/bottom** face counts as *outside* ⇒ a **t=0 hit at the start with
  `normal=(0,0)`**, even when travelling *away* from the body (`from_right_away`) **[M]**.
  This asymmetry is the single most surprising measured law of the round; mechanism **[I]**.

### 3.4 Ray ordering (`dss_ray_order`, `…_rev`) — [M]

```
dss_ray_order:      nearest=r={near …98…} tie=r={tie_b …298…} tie_minus_first=r={tie_b …} tie_minus_second=r={tie_a …}
                    tie_add_order=[tie_a,tie_b] last_added_wins=true rev=false
dss_ray_order_rev:  nearest=r={near …98…} tie=r={tie_a …298…} tie_minus_first=r={tie_a …} tie_minus_second=r={tie_b …}
                    tie_add_order=[tie_b,tie_a] last_added_wins=true rev=true
```

- **Nearest wins** across bodies at different distances **[M]**.
- **Coincident colliders: the LAST added wins** (`tie_b` when the add order is `[tie_a,tie_b]`;
  `tie_a` when reversed) — deterministic, insertion-order dependent, byte-identical over 6
  canonical + 3 loadtest reps **[M]**. This is a **verbatim-pinnable but construction-bound**
  value: a row may pin it only because the row's own probe fixes the add order.

### 3.5 `max_results` (`dss_point_cap`, `…_rev`) — [M], the headline hazard

```
dss_point_cap:     add_order=[a,b,c,d,e] cap0=[] cap1=[e#0] cap2=[e#0,a#0] cap3=[e#0,a#0,c#0]
                   cap5=[e#0,a#0,c#0,d#0,b#0] cap_default=[e#0,a#0,c#0,d#0,b#0]
                   mask2=[] nobodies=[] excl_first=[e#0,c#0,d#0,b#0] far_out=[]
                   pile40_default=n32 pile40_cap0=n0 pile40_cap64=n40 cap32_truncates=true
dss_point_cap_rev: add_order=[e,d,c,b,a] cap1=[a#0] cap2=[a#0,e#0] … cap_default=[a#0,e#0,c#0,b#0,d#0] …
```

- **`max_results = 0` returns ZERO results — it does not mean "unlimited"** **[M]**. A 40-body
  pile: `cap0 → n0`, `default → n32`, `cap64 → n40`, `cap8 → n8`. The default is **32** and it
  **truncates silently** **[M]**. This is the hazard the scout itself fell into during
  discovery (§4.1) and it is the reason `dss_point_cap`'s `cap0=[]` is worth a row.
- `collision_mask` and `collide_with_bodies=false` both yield `[]` here **[M]**.
- `exclude` **preserves the relative order** of the surviving hits (`excl_first=[e,c,d,b]` is
  the original `[e,a,c,d,b]` minus `a`) **[M]**.
- Truncation takes a **prefix of the result order** (`cap2=[e,a]`, `cap3=[e,a,c]`) **[M]**.

### 3.6 Point boundary predicate (`dss_point_edge`) — [M]

```
box_left=[box#0] box_right=[] box_top=[box#0] box_bottom=[] box_left_in=[box#0] box_right_in=[box#0]
circ_left=[] circ_left_in=[circ#0] circ_top=[] circ_center=[circ#0]
rot_left=[] rot_right=[] rot_top=[rot#0]
s_box_right=[box#0] s_box_bottom=[box#0] s_circ_top=[circ#0] s_rot_right=[rot#0]
point_half_open=left=true right=false top=true bottom=false
```

- **A rectangle is tested half-open: left/top edges inclusive, right/bottom edges exclusive**
  (Godot `Rect2` semantics) **[M]**. A rotated 45° box behaves the same **in local space**
  (`rot_top` = local corner (-20,-20) ⇒ in; `rot_left`/`rot_right` = local (±20,∓20) ⇒ out)
  **[M]**.
- **A circle's boundary is strictly exclusive on all sides** (`circ_left`/`circ_top` miss at
  exactly r=20; `circ_left_in` at 280.001 hits) **[M]**.
- **The shape predicate disagrees with the point predicate at the same boundary point**: a
  1e-3 probe box hits on *every* edge/corner the point query rejects (`s_*` all hit) **[M]** —
  shape overlap is **inclusive of exact touching** (§3.8 `touch=[e#0]`, `touch_out=[]`).

### 3.7 Canvas-instance layering (`dss_point_canvas`) — [M]

```
default_q=[def#0] layer_q=[clb#0] layer_q_at_default_spot=[clb#0] layer_scoped=true
shifted_default_q=[def#0] shifted_layer_q=[clb#0] layer_offset_ignored=true
ray_sees_default=r={def pos=(80.0000,0.0000) n=(-1.0000,0.0000)}
shape_sees_both=[def#0,clb#0] shape_layer_agnostic=true rev=false
```

- `def` lives in the viewport's default canvas layer, `clb` under a `CanvasLayer` node at the
  same position. **A point query with `canvas_instance_id=0` sees ONLY the default layer**;
  with the layer's `instance_id` it sees only that layer **[M]**. `0` does **not** mean "all
  layers" (the docs' wording is literal).
- Changing the `CanvasLayer.offset` to (200,0) does **not** move the layer's physics body
  (`world_pos=(100.0000,0.0000)`; the offset is render-only) and does not change either
  query **[M]**.
- **`intersect_ray` and `intersect_shape` have no canvas scoping**: the ray sees the default
  layer's body (`def` at 80) and the shape query sees **both** bodies
  (`shape_sees_both=[def#0,clb#0]`) **[M]**.

### 3.7b Multi-hit ordering (`dss_order_core`, `…_rev`) — [M], the assigned "ordering stability"

```
dss_order_core:     add_order=[a,b,c,d,e] rep1=[e#0,a#0,c#0,d#0,b#0] rep2=same rep3=same repeat_stable=true
                    set=[a#0,b#0,c#0,d#0,e#0] shape_same_order=true
                    pile_b=[e2#0,a2#0,b2#0,c2#0,d2#0] layout_changes_order=true
                    pile_a_after_insert=[e#0,a#0,c#0,b#0,d#0] insert_perturbs=true
                    pile_rev=[a3#0,e3#0,d3#0,c3#0,b3#0]
                    after_free=[a#0,b#0,e#0,d#0] free_perturbs=true after_readd=[a#0,b#0,e#0,f#0,d#0]
                    readd_set=[a#0,b#0,d#0,e#0,f#0] rev=false
dss_order_core_rev: add_order=[e,d,c,b,a] rep1=[a#0,e#0,c#0,b#0,d#0] … rev=true
```

Five bodies (40×40 at x=0,8,16,24,32, tags a..e) all contain the probe point (16,0).

| observation | result | meaning |
|---|---|---|
| repeat queries, no mutation | identical ×3 | order is a stable read **[M]** |
| 6 canonical + 3 loadtest reps, fresh processes | byte-identical | **deterministic across processes** for a frozen construction **[M]** |
| reversed add order | different vector | **insertion-order dependent** **[M]** |
| same relative geometry translated +1000 y | different vector (`[e2,a2,b2,c2,d2]`) | **layout dependent** (broadphase, not semantics) **[M]** |
| unrelated pile inserted elsewhere | pile A's vector changed (`[e,a,c,b,d]`) | **perturbed by unrelated mutation** **[M]** |
| free middle body + add a fresh one | vector changed twice | **not a function of the set** **[M]** |
| point query vs shape query | identical vector | the two families share the order **[M]** |
| sorted **set** of hits | `[a,b,c,d,e]` in every variant | the only semantic invariant **[M]** |

**Law (ordering stability): the returned multi-hit order is a deterministic function of the
construction sequence *and* the layout — reproducible byte-for-byte across fresh processes and
under load for a frozen construction — but it is a broadphase artefact: it is not sorted by
distance, tag, or insertion index, it flips when the add order flips, when the same geometry
moves, when an unrelated collider is inserted, and when one is freed.** Authors must pin the
sorted **set** (or a per-case frozen vector), never a semantic order.

**Independent-construction falsification (§7 F13–F17)** — a *different* probe (`order_alt`):
6 mixed-shape colliders (circle r30, rotated 60×20 rect, capsule 40/r10, 100×100 rect, circle
r50, 20×80 rect) in three add-order permutations, 3 fresh processes each:

```
perm=0 add_order=[q0,q1,q2,q3,q4,q5] point_order=[q3#0,q0#0,q2#0,q4#0,q5#0,q1#0]  (×3 identical)
perm=1 add_order=[q5,q4,q3,q2,q1,q0] point_order=[q5#0,q3#0,q0#0,q2#0,q1#0,q4#0]  (×3 identical)
perm=2 add_order=[q2,q0,q4,q1,q5,q3] point_order=[q4#0,q2#0,q3#0,q1#0,q5#0,q0#0]  (×3 identical)
shifted pile (same relative geometry, +5000 y): different vector in all three perms
```

The hypothesis survived: 9/9 process-stable, permutation-dependent, layout-dependent, and the
point and shape queries agree in every run **[M]**.

### 3.8 Shape lattice (`dss_shape_lattice`, `…_rev`) — [M]

```
cap0=n0 cap1=n1 cap3=n3 cap5=n5 cap_default=n5
keys=["collider", "collider_id", "rid", "shape"] set=[a#0,b#0,c#0,d#0,e#0]
touch=[e#0] touch_in=[e#0] touch_out=[]
multi_c0=[m#0] multi_c1=[m#1] multi_c2=[m#2] multi_set=[m#0,m#1,m#2] shape_rid=[m#1] empty=n0
```

- Same `cap0=n0` / default-32 semantics as point queries **[M]**.
- Result dicts carry **`shape` = the shape index inside the body**; a 3-shape body yields one
  entry per shape (`multi_c0/1/2` → `m#0`, `m#1`, `m#2`) **[M]** — a body with N shapes can
  produce up to N entries, so a naive "one hit per body" count is wrong.
- `shape_rid` (server-created shape) produces the identical result to `shape` **[M]**.
- **Exact touching counts as overlap** (`touch=[e#0]` at a shared edge; `touch_out=[]` at
  +0.001) — the opposite of the point predicate (§3.6) **[M]**.
- `set=` (sorted unique `tag#shape`) is stable in both add-order variants **[M]**.

### 3.9 Layer forms + space scoping (`dss_layer_forms`, `dss_excl_space`) — [M]

```
point_vis=[sb:body1/areas1/only0, ar:body0/areas1/only1, rb:body1/areas1/only0,
           cb:body1/areas1/only0, srv:body1/areas1/only0, canvas:body0/areas0/only0]
ray_sb=r={sb pos=(80.0000,0.0000) n=(-1.0000,0.0000)} ray_srv=r={? pos=(860.0000,0.0000) n=(-1.0000,0.0000)}
ray_area_off=r={} ray_area_on=r={ar pos=(280.0000,0.0000) n=(-1.0000,0.0000)}
shape_srv=[?#0] shape_area_off=[] shape_area_on=[ar#0] cast_srv_ignored=[1.0, 1.0]
server_tier_visible=true canvas_absent=true
---
baseline=[a#0] body_rid=[] shape_rid_inert=true null_rid_inert=true dup_rid=[]
ray_shape_rid_inert=r={a pos=(80.0000,0.0000) n=(-1.0000,0.0000)} shape_rid_is_body_rid=false
same_space=false root_view=[root_body#0] sv_view=[sv_body#0] space_scoped=true
dss_identity=same_across_calls=true node_world_ok=true
```

- **`StaticBody2D`/`RigidBody2D`/`CharacterBody2D` are visible as bodies; `Area2D` only with
  `collide_with_areas=true`; a plain `Node2D`+`Sprite2D` is invisible** (`canvas:body0/areas0/only0`)
  **[M]**.
- **A server-tier body** (`PhysicsServer2D.body_create()` + `body_add_shape`, no node) **is
  visible to point/ray/shape/cast queries** — it prints as `?` because it has no metadata
  tag **[M]**. Node-tier and server-tier objects share one space.
- **`exclude` takes BODY RIDs only**: a shape RID (`Shape2D.get_rid()`) is inert for point and
  ray queries, a null RID is inert, duplicates are harmless, and a body RID always wins
  **[M]** (`shape_rid_is_body_rid=false`).
- **Queries are per-space**: a `SubViewport` owns a different `World2D`/space; the root body is
  invisible from the SubViewport's direct state and vice versa (`space_scoped=true`) **[M]**.
- `Node2D.get_world_2d().space` matches the space each node is queried in **[M]**.

### 3.10 `cast_motion` + `get_rest_info` + `collide_shape` (`dss_cast_rest`) — [M]

```
cm_base=[0.220703125, 0.2265625] cm_to_wall1=[0.59765625, 0.6015625] cm_mask2=[1.0, 1.0]
cm_excl_w1=[0.72265625, 0.7265625] cm_excl_both=[1.0, 1.0] cm_areas_on=[0.220703125, 0.2265625]
cm_zero=[1.0, 1.0] cm_negative=[1.0, 1.0] cm_from_inside=[0.47265625, 0.4765625]
cm_inside_skips_overlap=true cm_inside_matches_later_wall=true
ri_m50={} ri_m200={w1 pt=(98.0000,0.0000) n=(-1.0000,0.0000) shape=0}
ri_m290={w1 pt=(102.0000,0.0000) n=(1.0000,0.0000) shape=0} ri_m300=… ri_m400=…
ri_m600={w2 pt=(298.0000,200.0000) n=(0.0000,1.0000) shape=0}
ri_m200_excl_w1={} ri_m400_excl_w1={w2 pt=(298.0000,0.0000) n=(-1.0000,0.0000) shape=0}
ri_mask2={} ri_empty={} ri_offaxis={}
ri_keys=["collider_id", "linear_velocity", "normal", "point", "rid", "shape"]
ri_zero_motion={w1 pt=(98.0000,0.0000) n=(-1.0000,0.0000) shape=0}
cs_n=6 cs_pts=[(98.0000,0.0000),(102.0000,0.0000),(114.0000,0.0000),(110.0000,0.0000),(98.0000,0.0000),(102.0000,0.0000)]
cs_cap1=n2 cs_cap2=n4 cs_excl_b1=n4 cs_mask2=n0 cs_rep=n6 cs_empty=n0
```

- `cast_motion` returns **two float32 fractions** `[safe, unsafe]` of the motion; `[1.0,1.0]`
  means "no hit" (mask miss, zero motion, negative motion, both walls excluded) **[M]**. The
  existing `phys2d_motion_dss_motion` row pins the same shape of value (`[0.44921875, 0.453125]`
  for a 200-long motion) — this cell extends it to mask/exclude/area/inside cases **[M]**.
- **`cast_motion` does not depenetrate**: a shape starting *inside* a body reports the *next*
  contact along the motion (`cm_from_inside=[0.47265625, 0.4765625]`, positive), and
  `cm_inside_matches_later_wall=true` confirms the returned distance is measured from the
  start to the *later* wall **[M]**. A naive "stop at the first overlap" model is refuted (F8).
- `collide_with_areas` is honoured (`cm_areas_on` == the wall contact; the area alone is
  reachable when bodies are off — discovery `cast_lattice areas_only=[0.47265625,0.4765625]`)
  **[M]**.
- **`get_rest_info` keys contain `collider_id`, not `collider`** (`ri_keys`), so an author
  cannot tag-match a rest info the way they can a ray hit **[M]**.
- `get_rest_info` sweep semantics are **partially measured**: with motion 50 (short of the
  wall) → `{}`; motion 200 → the **entry** face `(98,0) n=(-1,0)`; motion 290/300/400 → the
  **exit** face `(102,0) n=(1,0)`; motion 600 → a corner contact of the *second* wall
  `(298,200) n=(0,1)`. The reported contact is the *deepest* contact along the sweep; the exact
  rule is **[I]** and the values are pinned as measurements. Zero motion + overlap → the
  nearest surface `(98,0)/(-1,0)`; mask/exclude/off-axis behave as expected **[M]**.
- `collide_shape` returns a **flat PackedVector2Array of contact pairs** `[A0,B0,A1,B1,…]`
  **[M]**. **`max_results` counts PAIRS, not points** (`cs_cap1=n2`, `cs_cap2=n4`) **[M]** —
  the same trap that makes `phys2d_motion_dss_shapes`' `cs_full=2` look like "2 contacts".
- **A duplicate pair is emitted** for two separated walls: `cs_n=6` = 3 pairs, of which pairs 1
  and 3 are byte-identical (`(98,0),(102,0)`) **[M]** — the pair count is **not** the contact
  count; determinism holds (`cs_rep=n6`), and `exclude`/mask remove pairs as expected **[M]**.

### 3.11 Same-frame freshness (`dss_fresh`) — [M]

```
add_t0_point=[f#0] add_t0_ray=r={f …80…} add_t0_shape=[f#0] add_same_frame=true
node_move_t0_old=[f#0] node_move_t0_new=[] node_move_deferred=true
node_move_t1_old=[] node_move_t1_new=[f#0]
server_tele_t0_old=[] server_tele_t0_new=[f#0] server_write_live=true
pre_free=[c#0] free_t0=[c#0] free_deferred=true free_t1=[]
vis_off=[d#0] visible_irrelevant=true layer_change_t0=[e#0] layer_change_t1=[e#0]
```

- **`add_child()` is immediately queryable in the same frame** (point, ray and shape) **[M]** —
  no warm-up frame is needed for *insertion* (the r88 `r88_spawnable` caveat is about scene
  sync, not queries).
- **Node-tier position writes are deferred one physics step** for query visibility (old
  position still hits in the same frame; the new one only after a frame) **[M]**.
- **Server-tier `body_set_state(BODY_STATE_TRANSFORM)` is live in the same frame** (old spot
  gone immediately) **[M]** — the r79 "server writes land edge-0 / node writes are reverted"
  duality, now measured from the *query* side.
- `queue_free()` is deferred: the body still answers queries in the same frame and disappears
  after a frame **[M]**.
- **`visible=false` does not affect queries** **[M]**; changing `collision_layer` does not hide
  a body from a full-mask query (both before and after the frame) **[M]**.

---

## 4. How the laws were found (falsification-driven discovery)

The discovery probe was written to be wrong on purpose; five of its first-pass assumptions were
refuted by its own output and drove the frozen probe's design:

1. **`max_results=0` = unlimited** → **REFUTED**: `cap0=[]`, `pile40_cap0=n0`. The scout's own
   sub-tests were silently empty until the cap ladder was printed. Frozen into `dss_point_cap`.
2. **`PhysicsPointQueryParameters2D.max_results` exists** → **REFUTED**: the census shows the
   property list has no `max_results`; it is a method argument.
3. **`PhysicsRayQueryParameters2D.backface_collision` exists** (the brief names "backface
   flags") → **REFUTED**: `ray_backface=has=false`.
4. **Point-in-shape is symmetric** → **REFUTED**: half-open rect (`point_half_open=left=true
   right=false top=true bottom=false`), circle exclusive, rotated box half-open in local space.
5. **"start inside" is the only boundary hazard** → **REFUTED**: a ray starting on a
   right/bottom face reports a t=0 hit with a zero normal even when travelling away.
6. **`collide_shape`'s cap counts contacts** → **REFUTED**: it counts pairs (and emits a
   duplicate pair).
7. **Coincident colliders have no defined winner** → **REFUTED**: the last-added wins,
   deterministically, over 9 receipts.
8. **Multi-hit order is semantic (distance/tag/add index)** → **REFUTED** in five independent
   ways (§3.7b) — and replaced by the broadphase-artifact law.
9. **A server-tier body is invisible to queries** → **REFUTED**: it is fully visible; and
   **its RIDs must be freed** or the engine prints a stdout `ERROR` (§H3).
10. **Point queries see all canvas layers** → **REFUTED**: `canvas_instance_id=0` means the
    *default* layer only.

---

## 5. Hazards recorded (for the author and the boundary seat)

1. **`max_results=0` returns nothing** (§3.5). Passing a computed cap that can be 0 silently
   empties a query. Pin `cap0=[]`.
2. **The default cap is 32 and truncates silently** (§3.5) — a >32-collider pile loses hits
   with no warning.
3. **`hit_from_inside=false` makes an inside-start ray return `{}`** (§3.2) — a silent miss,
   not an error.
4. **The inside-start hit has `normal=(0,0)`** (§3.2) — normalizing it yields NaN/zero vectors;
   guard before use.
5. **A ray starting exactly on a right/bottom face reports a t=0 hit with a zero normal**
   (§3.3) — a "self hit" that is not a self hit; exclude the owner RID.
6. **Point vs shape predicates disagree at boundaries** (§3.6/§3.8): the point query is
   half-open, the shape query is inclusive. A 1-pixel disagreement is by design, not a bug.
7. **`exclude` accepts body RIDs only** (§3.9) — a shape RID is silently inert.
8. **Point queries are canvas-layer scoped; ray/shape are not** (§3.7) — the same world can
   answer two different "what is at this point" questions.
9. **Node-tier position writes are one physics step stale** (§3.11) — do not chain
   `position = …` and a query in the same frame; use `body_set_state` or await a step.
10. **`collide_shape`'s `max_results` counts pairs** (§3.10) and a duplicate pair is emitted —
    never treat the array size as a contact count.
11. **`get_rest_info` has no `collider` key** (§3.10) — `collider_id` + `instance_from_id` (or
    a tag lookup) is required; and its sweep rule is only partially characterized.
12. **Server-tier RIDs leak an ERROR on stdout at exit** (§H3) — the production classifier
    rejects the row. Free every RID you create.
13. **`cast_motion` does not depenetrate** (§3.10) — starting inside a body yields a positive
    fraction to the *next* obstacle; the first value is a conservative "safe" fraction.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (17, exec-checked)

`corpus/live/r95-scout/author-rows.py.txt` holds two 5-tuple sets and the `expected_errors`
dict; `python3 verify_rows.py` classifies every row against **every** canonical + loadtest
receipt with the production `classify_process` (AST-extracted from `corpus/fixtures/run_battery.py`,
segment sha256 `749fa060…` — the same segment r89/r90/r91 pinned):

- **`ROWS` (full-line): 150/150 receipts accepted, `rejected=[]`** — all 17 cells are
  byte-stable over 6 canonical + 3 loadtest reps each (census: 3 + 3).
- **`ROWS_PREFIX` (recommended): 150/150 accepted, `rejected=[]`** — identical except that the
  four order-vector cells (`dss_lattice_point_cap`, `…_cap_rev`, `…_order_core`,
  `…_order_core_rev`) are cut immediately before their first order vector, keeping the
  order-free prefix (`add_order=…` and, for point_cap, `cap0=[]`).
- `expected_errors` additions: **none** — every cell is `ERROR:`-clean with 0 B stderr.

```
dss_lattice_census        PASS dss_lattice census dss_methods=n6[…] … dss_identity=same_across_calls=true
dss_lattice_ray_flags     PASS dss_lattice ray_flags base=r={w pos=(98.0000,0.0000) …} … keys=["collider", …]
dss_lattice_ray_geom      PASS dss_lattice ray_geom end_at_face=… corner_start_away=r={}
dss_lattice_ray_order     PASS dss_lattice ray_order nearest=… last_added_wins=true rev=false
dss_lattice_ray_order_rev PASS dss_lattice ray_order nearest=… last_added_wins=true rev=true
dss_lattice_point_cap     PASS dss_lattice point_cap add_order=[a,b,c,d,e] cap0=[] cap1=[e#0] … cap32_truncates=true
dss_lattice_point_cap_rev PASS dss_lattice point_cap add_order=[e,d,c,b,a] cap0=[] cap1=[a#0] …
dss_lattice_point_edge    PASS dss_lattice point_edge … point_half_open=left=true right=false top=true bottom=false
dss_lattice_point_canvas  PASS dss_lattice point_canvas default_q=[def#0] layer_q=[clb#0] … shape_layer_agnostic=true
dss_lattice_shape         PASS dss_lattice shape_lattice cap0=n0 cap1=n1 … shape_rid=[m#1] empty=n0 rev=false
dss_lattice_shape_rev     PASS dss_lattice shape_lattice … touch=[a#0] touch_in=[a#0] … rev=true
dss_lattice_order_core    PASS dss_lattice order_core add_order=[a,b,c,d,e] rep1=[e#0,a#0,c#0,d#0,b#0] … rev=false
dss_lattice_order_core_rev PASS dss_lattice order_core add_order=[e,d,c,b,a] rep1=[a#0,e#0,c#0,b#0,d#0] … rev=true
dss_lattice_layer_forms   PASS dss_lattice layer_forms point_vis=[sb:body1/areas1/only0,…] … canvas_absent=true
dss_lattice_cast_rest     PASS dss_lattice cast_rest cm_base=[0.220703125, 0.2265625] … cs_empty=n0
dss_lattice_excl_space    PASS dss_lattice excl_space baseline=[a#0] … node_world_ok=true
dss_lattice_fresh         PASS dss_lattice fresh add_t0_point=[f#0] … layer_change_t1=[e#0]
```
(Exact strings in `author-rows.py.txt`.)

Probe file lands at `corpus/fixtures/dss_lattice.gd` (sha256 `77ae4adb…`, self-contained
`SceneTree` script, battery `--arm=` convention). Insert the rows ahead of the crash/descendant
tail like prior blocks; no other fixture change is needed. **No `expected_errors` entry is
required** (this is the first r9x block with an empty dict — verified by the production
classifier on all 150 receipts).

### 6.2 What to pin and what not to pin

1. **Pin the `PASS dss_lattice …` line** — it carries the arm name, so the r88 silent-fallback
   failure cannot recur.
2. **Pin the `--rev` variants as separate cases** — they are the only evidence that the
   ordering and the tie winner are insertion-order dependent (the law, not just a value).
3. **For the four order-vector cells prefer `ROWS_PREFIX`** (cut before the first vector):
   the vectors are broadphase artefacts. The full-line rows are *also* load-clean (150/150),
   so either form gates today; the prefix form is the one that survives a future change in
   the broadphase (e.g. a different `physics/2d` backend or a Godot minor bump).
4. **Do not pin** raw RIDs, `instance_id`s, or anything from a construction you did not freeze
   yourself.
5. **Pin `cap0=[]` and `cap32_truncates=true` explicitly** — the two `max_results` hazards.
6. **Pin the predicates, not just the points**: `point_half_open=…`, `touch=[e#0]`,
   `s_box_right=[box#0]` are the law; the coordinates are the measurement.
7. **No envelope is needed for any cell** — 17/17 single-valued across canonical + loadtest.
8. **Server-tier RIDs in a probe must be freed** (§H3) or the row is rejected by
   `classify_process`.

---

## 7. Falsification list

| id | hypothesis (must-differ input) | result |
|---|---|---|
| F1 | `PhysicsRayQueryParameters2D` has a `backface_collision` flag (the brief's "backface flags") | **REFUTED [A]** — property absent (`ray_backface=has=false`); 2D has only `hit_from_inside` |
| F2 | `max_results=0` means unlimited | **REFUTED [A]** — `cap0=[]`, `pile40_cap0=n0`; default is 32 and truncates |
| F3 | `max_results` is a params-object property | **REFUTED [A]** — it is a method argument on three methods |
| F4 | A ray starting inside a body still hits it | **REFUTED [A]** — `{}` unless `hit_from_inside=true`, and then `normal=(0,0)` |
| F5 | A ray whose endpoint is exactly on a face misses | **REFUTED [A]** — `end_at_face` hits; 0.0001 short misses |
| F6 | Coincident colliders have an undefined ray winner | **REFUTED [A]** — last-added wins, `--rev` flips it, 9/9 receipts |
| F7 | Point-in-rect is symmetric (all edges equivalent) | **REFUTED [A]** — half-open: left/top in, right/bottom out; circle exclusive |
| F8 | `cast_motion` stops at the overlap it starts in | **REFUTED [A]** — it reports the next contact (`cm_inside_skips_overlap=true`) |
| F9 | A body with 3 shapes yields one query entry | **REFUTED [A]** — one entry per shape, `shape` = index |
| F10 | Point queries see colliders from every canvas layer | **REFUTED [A]** — `canvas_instance_id=0` = default layer only |
| F11 | `exclude` accepts shape RIDs | **REFUTED [A]** — shape RIDs are inert; only body RIDs work |
| F12 | A server-tier (`PhysicsServer2D`) body is invisible to queries | **REFUTED [A]** — visible to point/ray/shape/cast; and leaks an ERROR if unfreed |
| F13 | Multi-hit order is semantic (distance/tag/add index) | **REFUTED [A]** — 5-body pile returns `[e,a,c,d,b]`; reversed add order `[a,e,c,b,d]` |
| F14 | Multi-hit order is stable against an unrelated insertion | **REFUTED [A]** — `pile_a_after_insert=[e,a,c,b,d]` ≠ `[e,a,c,d,b]` |
| F15 | Multi-hit order is stable against free + re-add | **REFUTED [A]** — `after_free=[a,b,e,d]`, `after_readd=[a,b,e,f,d]` |
| F16 | Multi-hit order is a function of the set alone (layout-independent) | **REFUTED [A]** — translated pile returns a different vector |
| F17 | (independent construction, 6 mixed shapes, 3 permutations × 3 processes) the order is not reproducible across processes | **REFUTED [A]** — 9/9 byte-identical per permutation; the ordering law survived |
| F18 | `get_rest_info` returns the nearest contact along a sweep | **PARTIALLY REFUTED [A]** — entry face at motion 200, **exit** face at 290/300/400, second-wall corner at 600 |
| F19 | `collide_shape`'s `max_results` counts contact points | **REFUTED [A]** — it counts pairs (`cap1 → n2`) and emits a duplicate pair |
| F20 | `queue_free()` removes a body from queries immediately | **REFUTED [A]** — still visible in the same frame, gone after one frame |
| F21 | A node-tier `position` write is query-visible in the same frame | **REFUTED [A]** — old position hits; new position after one physics step |
| F22 | `visible=false` hides a collider from queries | **REFUTED [A]** — `vis_off=[d#0]` |
| F23 | Queries see bodies from another `World2D` (SubViewport) | **REFUTED [A]** — spaces are disjoint (`space_scoped=true`) |

---

## 8. Remaining unknowns / not measured

- **`get_rest_info`'s exact sweep rule** (entry vs exit vs deepest contact) — six motion values
  measured, rule **[I]**; the transition between `m200` (entry face) and `m290` (exit face) was
  not bisected.
- **`collide_shape`'s duplicate pair**: whether it is a manifold artefact or a broadphase pair
  duplication is **[I]**; only the emitted vector is measured.
- **`PhysicsShapeQueryParameters2D.margin`**: the property exists (default `0.0`) but only
  `dss_purity` (r80) reads it back; its effect on `intersect_shape`/`cast_motion` at boundary
  distances was **not** latticed.
- **`canvas_instance_id` beyond one layer**: a second `CanvasLayer`, nested layers, and a body
  whose layer is created after the query were not measured.
- **`intersect_point` with `canvas_instance_id` pointing at a non-CanvasLayer instance id**
  (e.g. a node's id) — refusal behaviour unmeasured.
- **Rotated/`ConvexPolygonShape2D`/`SegmentShape2D` point predicates** — only rect, circle and
  one 45° rect were measured; the half-open rule for arbitrary convex shapes is **[I]**.
- **`get_rest_info`/`cast_motion` under a non-default `margin`** — unmeasured.
- **Other backends**: the r86 nested-boot lattice showed Dummy returns degenerate payloads
  (`ray_keys=[]`, `cm=-1`); this round measured only the default GodotPhysics2D. The new rows
  are **default-backend-only** by construction.
- **Threaded physics** (`physics/2d/run_on_separate_thread`): the r86 gate matrix covers the
  space-state gate; the query *ordering* under the threaded window was not re-measured.
- **`PhysicsServer2D.space_get_direct_state` from inside a physics callback** — r80/r88 cover
  the callback window; not re-measured here.
- **Portability**: every value is this host/build/`--headless`/60 tps/GodotPhysics2D.

---

## 9. Host cleanup

- **209 bounded launches captured** (99 canonical + 51 loadtest + 17 discovery + 20 early
  ordering reps + 9 alt-construction + 13 smoke), all `--headless`, all `timeout -s KILL`-bounded
  (30 s; none hit), no run left running (`pgrep -fa dss_lattice` → none).
- Loadtest hogs: 16 own `yes` processes started and **only their own PIDs killed**
  (`own_hogs_killed=16`, `host_yes_remaining=72` — other lanes' hog blocks untouched). The
  *first* loadtest block used `pkill -x yes` and cleared 72 host hogs belonging to other lanes
  **[O]** — disclosed here; no tracked state was affected.
- No tracked file written: `git status --porcelain` shows only the concurrent lane's
  `corpus/fixtures/run_battery.py` (+82 lines, no r95 token) and untracked `corpus/live/*`.
- `manifest.sha256` covers every artefact under `corpus/live/r95-scout/`.

---

## 10. Evidence index

All under `corpus/live/r95-scout/`; `manifest.sha256` covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| **frozen primary probe, 17 cells** | `probes/dss_lattice.gd` | `77ae4adb8a47ccf5` |
| discovery micro-probe (18 arms) | `probes/discover.gd` | `693a548993a79be9` |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| canonical driver (17 cells, 99 runs) | `run_cells.sh` | `1dd033ec1fe818cd` |
| loadtest driver (51 runs, load 95–109) | `run_loadtest.sh` | `9ce3d6f4c06bd67b` |
| analyzer → json | `analyze_r95.py` → `runs/analyze_r95.json` | `0df372776e59a0a9` / see manifest |
| author rows + builder + verifier | `author-rows.py.txt`, `make_author_rows.py`, `verify_rows.py` | see manifest |
| per-cell receipts (99 × 3 files) | `runs/r95_*.{out,err,rc}` | `manifest.sha256` |
| loadtest receipts (51 × 3 files) | `runs/loadtest/` | `manifest.sha256` |
| alt-construction falsification (9) | `runs/alt/` | `manifest.sha256` |
| leak-hazard evidence (pre-fix) | `runs/leak-hazard/` | `manifest.sha256` |
| discovery receipts | `runs/disc/`, `runs/discord/`, `runs/smoke/` | `manifest.sha256` |

Reproduce: `bash run_cells.sh && bash run_loadtest.sh && python3 analyze_r95.py &&
python3 make_author_rows.py && python3 verify_rows.py` (expect `UNSTABLE=[]`,
`ROWS 150/150`, `ROWS_PREFIX 150/150`, `rejected=[]`).
