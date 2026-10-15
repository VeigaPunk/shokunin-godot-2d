# game-dev-2d round 89 — scout (r89-scout): the Geometry2D authorability lattice, pre-measured; 20 rows verbatim-ready

Seat `SCOUT` (LEAF) | lane `r89-scout` | round 89 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps default (plus a generated 120 tps project variant), GodotPhysics2D.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD at session start **`fad0b1e`** (*late r78
wave-B reports + scouts r82/r84/r87/r88*); HEAD moved to **`96c0b13`** mid-session (a concurrent
lane's r87 boundary report commit, `reports/round-87/r87-boundary-readonly.md` only). All
measurements here are probe/API receipts independent of that commit; the launch
`project.godot` I copied is pinned in `manifest.sha256` (`8de8b3af…`).

**No git mutation, no tracked file written, no subagent, no commit.** Writes are this report and
`corpus/live/r89-scout/**` only. `git status --porcelain` shows no modified tracked file; the
untracked `corpus/fixtures/{ei_bound.gd,input_lattice.gd,r87_edge.gd}` and
`corpus/fixtures/__pycache__/` pre-date this session (r87 lane leftovers) and are untouched.

**`lsp` disclosure (unchanged host state).** No `lsp` device in this session and no GDScript
language server installed; `definition`/`references`/`hover` were **unavailable for every file
touched**. Semantic carriers: fresh-process execution receipts, `ClassDB` runtime introspection
inside the probe, and engine-emitted error text. Every `file:line` below is engine-emitted
`at:` backtrace text, never a source read.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and the one bounded split

**Primary: the Geometry2D authorability lattice** — the r88 census's top-ranked family
(§2 headline row 1, §9.1 "*Geometry2D pure-function arms are battery-ready as-is*", §9.2 the
geometry→collision bridge). The census carries **no numeric ranking**; its §2 order plus §9.1/§9.2
place Geometry2D first, and I take that as the pick **[I]**.

Two facts make it the right pick, both measured this session:

- **Zero existing coverage.** `grep -rin "geometry2d\|geo2d" corpus/fixtures/ --include=*.gd
  --include=*.py --include=*.tscn` → **0 hits** **[O]**. The 191-row battery has no Geometry2D row.
- **Zero flakiness surface.** Geometry2D is a pure static math class: no physics step, no idle
  window, no wall-clock. All 12 pure/boundary arms are `out_uniq=1 err_uniq=1` (§1), and 9 of
  them emit **0 B stderr**. This is the opposite of the r87 input lattice, where three arms are
  bimodal through physics-step interposition.

**Bounded secondary split (2 arms, 6 runs):** r87's remaining input unknowns
`is_action_pressed(a, exact_match)` **granularity** and the **joypad analog-axis device filter**.
Reason for taking exactly these two: both are *synchronous* queries
(`Input.parse_input_event` + `Input.flush_buffered_events`, no `await` between parse and poll), so
they close two named r87 unknowns with **no idle/physics window to flake**; the other two r87
unknowns (SubViewport cursor, `event_index` semantics for `1..31`) need a display server or
frame-sequenced probes and were **not** taken. `event_is_action`/modifier semantics were already
measured in r87 §4 (`jpbe`) and were not re-taken.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `bash run_cells.sh` | 17 cells (11 pure ×3, 3 lifecycle ×6, 1 tps-split ×6, 2 input ×3) = 63 runs | `runs/` |
| 2 | `bash run_cells2.sh` | 9 cells (bridge re-cut, tps time-match, ring ×3, pipedges, input re-runs) = 45 runs | `runs/` |
| 3 | inline loop (same launch shape) | `ringhits` ×6, `pipedges` (format fix) ×3 = 9 runs | `runs/geo_ringhits.*`, `runs/geo_pipedges.*` |
| 4 | inline loop | `census`/`joins` re-cut (ERROR-free) + new `polyendpoly` ×3 = 9 runs | `runs/geo_{census,joins,polyendpoly}.*` |
| 5 | `godot … res://discover.gd -- --arm={geoapi,joy}` | API-shape discovery (method args, enums, device filter) | `runs/disc-*.{out,err}` |
| 6 | `python3 analyze_r89.py` | per-cell reps / out-uniq / err-uniq / rc vectors | `analyze_r89.json` |
| 7 | `python3 make_author_rows.py` → `python3 verify_rows.py` | 20 verbatim CASES rows, classified with the production `classify_process` | `author-rows.py.txt` |

**Canonical cell set: 99 runs across 23 cells** — 15 cells × 3 reps (pure functions, boundary
isolations, input edges) and **9 cells × 6 reps** (every physics-await/lifecycle cell).
Plus 2 discovery runs, 3 superseded `pipedges` reps kept under `runs/fmtbug/`, and 18 round-1 runs
for 4 cells that were re-run after a probe revision (traces in `runs/rc-summary.txt`).

**Byte-stability: 23 of 23 cells are `out_uniq=1` `err_uniq=1` with a constant rc vector.**
`analyze_r89.py` prints `UNSTABLE=[]`. **No bimodal cell exists in this surface** — no envelope or
mode-distribution is needed for any row below. rc vectors: all `0` except `geo_lineempty`
`134,134,134` (SIGABRT, deterministic, byte-identical stderr 377 B).

**Arm-dispatch integrity [O]:** every arm prints its own name on its `PASS` line, so the 23
signatures are pairwise distinct and a silent `_:` fallback (the r88 dead-seat failure) is
impossible to miss. `arm` is parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan), not the inverted pair that killed r88.

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| Geometry2D **boolean ops** (clip/merge/inter/excl) | **PINNABLE**, exact vertex+area output | 3 | uniq=1 |
| Geometry2D **containment/hole** semantics | **PINNABLE**, and the census had no cell for it | 3 | uniq=1 |
| Geometry2D **offset join/end lattice** | **PINNABLE** incl. sign- and join-sensitivity | 3 | uniq=1 |
| Geometry2D **triangulation/hull/decompose/atlas** | **PINNABLE** + area-conservation invariants | 3 | uniq=1 |
| Geometry2D **predicates + boundary policy** | **PINNABLE**, three different boundary policies measured | 3 | uniq=1 |
| Geometry2D **degenerate/empty inputs** | **PINNABLE**; one SIGABRT vector (§5) | 3 | uniq=1 |
| **geometry → CollisionPolygon2D → body** bridge | **PINNABLE**; census `rest_y=82.3000` reproduced exactly | 6 | uniq=1 |
| **holes are not expressible** in one CollisionPolygon2D | **PINNABLE** point-query discriminator + positive control | 6 | uniq=1 |
| **tps split** of the bridge pin | measured: the pin is a *duration* pin, not a frame-count pin | 6 | uniq=1 |
| r87 `exact_match` granularity | **PINNABLE** — poll-time exactness *does* change an answer | 3 | uniq=1 |
| r87 joypad **analog-axis device filter** | **PINNABLE** — device filter blocks the action, not the device state | 3 | uniq=1 |

---

## 3. Measured values, verbatim

Helper shapes are the census's, pinned verbatim: `_poly2str(arr) = k=<n>{n<size>[x,y;…]|…}` and
`_poly2str_area` appends ` a=<signed shoelace/2>`. All coordinates `%.4f`.

### 3.1 API census (`census`) — [M]

```
PASS geo2d_lattice census sig=[clip_polygons(polygon_a,polygon_b)|convex_hull(points)|decompose_polygon_in_convex(polygon)|make_atlas(sizes)|merge_polygons(polygon_a,polygon_b)|offset_polygon(polygon,delta,join_type)|offset_polyline(polyline,delta,join_type,end_type)|triangulate_polygon(polygon)] join=SQ=0,RD=1,MT=2 end=POLY=0,JOINED=1,BUTT=2,SQUARE=3,ROUND=4 op=UNION=0,DIFF=1,INTER=2,XOR=3 nmethods=86 default_join_polygon=k=1{n8[12.0000,-10.8284;…]} match=[sq,] default_polyline=k=1{n7[22.0000,-0.8284;…]} match=[sq/square,]
```

- `offset_polygon(polygon, delta, join_type)`, `offset_polyline(polyline, delta, join_type, end_type)`,
  `make_atlas(sizes)` — arg names/types from `ClassDB.class_get_method_list` **[M]**.
- **The 2-arg default is `JOIN_SQUARE` for both entry points**, and `offset_polyline`'s 2-arg
  default end type is `END_SQUARE` (resolved by byte-comparing the default call against all
  12 join×end combinations) **[M]**. This is why the census's `offset(+2)` chamfered n8 and its
  `k=1 n7` polyline output reproduce here.
- `END_POLYGON` is **not** part of the default resolution: it refuses (§5.3).

### 3.2 Boolean ops, two overlapping 20×20 squares (`ops`) — [M], reproduces the census

```
clip  = k=1{n4[-2,-10;-2,10;-10,10;-10,-10]}
merge = k=1{n4[18,-10;18,10;-10,10;-10,-10]}
inter = k=1{n4[10,10;-2,10;-2,-10;10,-10]}
excl  = k=2{n4[left a=160.0000] | n4[right a=160.0000]}
tri_idx=[3, 0, 1, 1, 2, 3]  tri_area=400.0000 poly_area=400.0000
offset(+2, JOIN_SQUARE) = k=1{n8[…10.8284/12.0000…] a=573.2548}
offset(+2, JOIN_ROUND)  = k=1{n12[…11.0625/11.6944…] a=571.0277}
offset(+2, JOIN_MITER)  = k=1{n4[12,12;-12,12;-12,-12;12,-12] a=576.0000}
offset(−2, all three joins) = k=1{n4[8,-8;8,8;-8,8;-8,-8] a=256.0000}
```

Every value equals the census's §3.1/§3.2 output **[M]**; the areas are new. Note the exact
ordering `SQUARE < ROUND < MITER` by area for the outward offset (573.25 / 571.03 / 576.00), and
that `triangulate_polygon`'s triangle-area sum equals the polygon area exactly.

### 3.3 Containment and holes (`contain`) — [M], **no census cell**

```
merge(big,small) = k=1{n4[20,20;-20,20;-20,-20;20,-20] a=1600.0000}      # NO hole — containment collapses
merge(small,big) = k=1{ …same 1600… }                                   # order-independent
clip(big,small)  = k=2{n4[outer] a=1600.0000 | n4[-5,-5;-5,5;5,5;5,-5] a=-100.0000}   # HOLE, negative winding
clip(small,big)  = k=0{}
inter(big,small) = k=1{n4[5,5;-5,5;-5,-5;5,-5] a=100.0000}   (identical for (small,big))
exclude(big,small)= k=2{outer a=1600.0000 | hole a=-100.0000}  (identical for (small,big))
adjacent merge = k=1{n4[30,-10;30,10;-10,10;-10,-10] a=800.0000}   # edge-sharing squares merge
adjacent clip  = k=1{left a=400.0000}      # unchanged
adjacent inter = k=0{}                     # edge contact is NOT an intersection
overlap excl   = k=2{n6 a=204.0000 | n6 a=204.0000}   clip = k=1{n6 a=204.0000}   inter = k=1{n4 a=196.0000}
```

**`clip`/`exclude` are the hole-producing operations; `merge` never produces a hole [M].**
A hole contour is returned with **negative** signed area (CCW outer / CW inner), which is the only
in-band signal that a contour is a hole.

### 3.4 Join / end-type lattice (`joins`) — [M]

```
poly_p2_sq = n8 a=573.2548   poly_p2_rd = n12 a=571.0277   poly_p2_mt = n4 a=576.0000
poly_m2_sq = poly_m2_rd = poly_m2_mt = k=1{n4[8,-8;8,8;-8,8;-8,-8] a=256.0000}   # join_type is inert for delta<0
poly_zero  = k=1{n4[-10,-10;10,-10;10,10;-10,10] a=400.0000}   # delta=0 identity (same start vertex)
poly_collapse = k=0{}                                          # delta=-20 on a r=10 square: empty
line_rd_joined = k=2{n11[…a=347.4172] | n3[4.8284,2;18,15.1716;18,2] a=-86.7453}
line_sq_joined = k=2{n6[…a=350.5732]  | n3[same] a=-86.7453}
line_mt_joined = k=2{n5[…a=351.2595]  | n3[same] a=-86.7453}
line_rd_butt = k=1{n8 a=158.7569}  line_rd_square = k=1{n8 a=174.7569}  line_rd_round = k=1{n14 a=169.3603}
line_default = k=1{n7 a=175.3137}                      # == JOIN_SQUARE/END_SQUARE
line_m2_joined = BYTE-IDENTICAL to line_rd_joined      # offset_polyline is sign-insensitive
```

- **`offset_polyline` sign-insensitivity is general, not an artifact of the default args** — the
  census measured it for the 2-arg default; here `(+2, ROUND, END_JOINED)` and `(−2, ROUND,
  END_JOINED)` are byte-identical **[M]**.
- **`offset_polygon` sign-sensitivity**: `join_type` changes the result only for positive delta
  (all three joins agree at `−2`).
- **`offset_polyline` of an L-shaped open line returns `k=2`**, the second contour being the inner
  corner with **negative** area — an author expecting one contour is wrong for `END_JOINED`.
- `delta=0` on a polygon is a true identity (same start vertex, positive area) **[M]**.

### 3.5 Triangulation / hull / decomposition / atlas (`trig`) — [M]

```
hull(concave 5pt)      = k=1{n5[0,0;20,0;20,20;0,20;0,0]}     # closed ring, first vertex repeated
tri_idx(concave)       = [1, 2, 3, 3, 4, 0, 0, 1, 3]  tri_area=280.0000  poly_area=280.0000
decompose_in_convex    = k=3{n3|n3|n3}                dec_area=280.0000
delaunay(5 pts)        = [0, 1, 3, 0, 2, 3, 1, 2, 4, 2, 3, 4, 1, 3, 4]
make_atlas([(20,10),(5,5),(3,3)]) = points=[(0,0),(20,0),(20,5)] size=(25,10)   # census value reproduced
make_atlas([(4,4)])               = points=[(0,0)]               size=(4,4)
make_atlas([(7,3),(7,3)])         = points=[(0,0),(0,3)]         size=(7,6)     # equal sizes pack vertically
```

**Area-conservation invariants (new, authorable):** the triangle-area sum of `triangulate_polygon`
and the absolute-area sum of `decompose_polygon_in_convex` both equal the input polygon's area
**exactly** at 4 dp (280.0000 = 280.0000) **[M]**.

### 3.6 Predicates (`pred`) and their boundary policies (`pipedges`) — [M]

```
pip  in=true out=false edge=true corner=true
pic  on=true out=false center=true
isect line=(2.0, 0.0) seg=(2.0, 0.0) miss=<null>
closest cap=(3.0, 0.0) uncap=(13.0, 0.0) segseg=[(5.0, 0.0), (5.0, 0.0)] degenerate=(2.0, 2.0)
tri  in=true out=false edge=false vertex=false
bresenham fwd=[(0,0),(1,1),(2,1),(3,2),(4,2),(5,3)] rev=[exact reverse] diag=[(0,0),(1,1),(2,2),(3,3)]
sic  fwd=0.2500 rev=0.2500 miss=-1.0000 inside=-1.0000 startinside=0.5000 tangent=0.5000
```

**Three different boundary policies live in the same class [M]** — this is the authoring trap:

| predicate | boundary point | 1e-6 outside | 1e-4 outside | 1e-3 outside | 1e-2 outside |
|---|---|---|---|---|---|
| `is_point_in_polygon` | **true** | true | **true** | **false** | false |
| `point_is_inside_triangle` | **false** | true | true | true | true |
| `is_point_in_circle` (radius exact) | **true** | — | **false** (out) | — | — |

- `is_point_in_polygon` is boundary-**inclusive with an epsilon between 1e-4 and 1e-3**, and the
  policy is **winding-independent** (`pip_right_cw` = `[0:true,1e-4:true,1e-2:false,0.1:false]`).
- `point_is_inside_triangle` is **strictly interior** (edge=false, vertex=false, first true at
  1e-6 inside).
- `is_point_in_circle` is **exact** (on-circle true, +1e-4 out false).
- `segment_intersects_circle` returns the **fraction along the segment of the first boundary
  crossing**: `0.25` for a diameter segment **in both directions** (the entry point is 0.25 from
  the start either way), `0.5` when the start is inside (the *exit* fraction), `0.5` for a tangent,
  and `−1.0` when the segment lies entirely inside **[M]** — the census's "parametric t, not bool"
  is now fully parameterized.

### 3.7 Degenerate and empty inputs (`edge`, `offempty`, `offdeg`) — [M]

```
clip(sq,∅)=k=1{subject, start vertex rotated}   merge(sq,∅)=k=1{same}   inter(sq,∅)=k=0{}   excl(sq,∅)=k=1{same}
clip(∅,sq)=k=0{}   merge(∅,sq)=k=1{sq}   inter(∅,sq)=k=0{}
clip(sq,sq)=k=0{}   merge(sq,sq)=k=1{sq}   inter(sq,sq)=k=1{sq}   excl(sq,sq)=k=0{}
clip(1pt,sq)=k=0{}  clip(2pt,sq)=k=0{}
tri: 1pt=[]  2pt=[]  dup(4pt,2 duplicated)=[0, 3, 2, 2, 1, 0]  collinear=[0, 2, 1]  bowtie=[]  sq=[3, 0, 1, 1, 2, 3]
cw: sq=false  reversed=true  1pt=false  2pt=false  collinear=false  bowtie=false
pip: bowtie-centre=true  collinear-point=false  1pt=false
clip(bowtie,sq)=k=0{}     clip(reversed-winding sq, sq)=k=1{identical to the CCW result}
hull: 1pt=k=1{n1}   collinear-3pt=k=1{n3[0,0;2,0;0,0]}   sq=k=1{n5 closed ring}
offset_polygon(∅, 2.0, ROUND) = k=0{}          # CLEAN, rc=0 — no error, no crash
offset_polygon(collinear-3pt) = k=1{n10}   offset_polygon(2pt) = k=1{n10}   offset_polygon(1pt) = k=1{n7}
```

- **`clip_polygons(sq, ∅)` returns the subject with a rotated start vertex**, not byte-identical to
  the input — the census's "returned unchanged" is true up to start-vertex rotation and winding **[M]**.
- **New: `offset_polygon` accepts every degenerate input tried** (∅, 1-pt, 2-pt, collinear) without
  an error, while `offset_polyline(∅)` is a process-killer (§5.1) — the two entry points do **not**
  share the boundary behaviour **[M]**.
- `convex_hull` returns `n+1` (closed ring) for polygons but `n1` for a single point and `n3` for
  three collinear points — a vertex-count pin must special-case those.

### 3.8 The geometry→collision bridge (`bridge`) — [M], census `geo_phys` reproduced exactly

```
PASS geo2d_lattice bridge wall=k=1{n4[60.0000,60.0000;-60.0000,60.0000;-60.0000,30.0000;60.0000,30.0000]} tps=60 frames=60 rest=y=82.3000 vel=0.0000,0.0000 self_hit=1
```

`clip_polygons(sq(0,0,60), sq(0,−30,60))` → one quad assigned verbatim to `CollisionPolygon2D` on a
`StaticBody2D` at y=60; a radius-8 `RigidBody2D` dropped from y=−100 rests at **`y=82.3000`** with
zero velocity and `intersect_point` hits **1**. This is byte-equal to the census's §3.5
`rest_y=82.3000 self_hit=1` **[M]**, now in battery launch convention. (Ideal contact would be
y=82.0; the solver leaves a 0.3 px margin — pin the measured value, not the ideal.)

### 3.9 Runtime split: the bridge pin is a *duration* pin (`bridge` @120 tps) — [M]

| project | `physics_ticks_per_second` | frames awaited | rest |
|---|---|---|---|
| `proj` | 60 | 60 | **y=82.3000, vel 0,0, self_hit=1** |
| `proj_tps120` | 120 | 60 | **y=22.5250, vel 0,478.1458, self_hit=1** (still falling) |
| `proj_tps120` | 120 | **120** | **y=82.3000, vel 0,0, self_hit=1** (identical to 60 tps) |

The pin is invariant to tps **at equal simulated duration** and breaks at equal frame count **[M]**.
Any authoring of a frame-counted physics row must state the tps assumption; a tps-variant cell in
the battery would need the r86 nested-boot pattern (`phys2d_backends.gd`) because
`run_battery.py` has no per-case project variant.

### 3.10 Holes are not expressible in a `CollisionPolygon2D` (`ring`, `ring2`, `ring4`, `ringhits`) — [M]

The hole-producing op is `clip` (§3.3). Ring = `clip_polygons(sq(0,0,40), sq(0,0,10))`:

```
ring = k=2{n4[40,40;-40,40;-40,-40;40,-40] a=6400.0000 | n4[-10,-10;-10,10;10,10;10,-10] a=-400.0000}
hits = [A_contour0[centre:1,top:1,right:1,bottom:1,left:1]
      | B_both[centre:2,top:1,right:1,bottom:1,left:1]
      | C_slabs[centre:0,top:1,right:1,bottom:1,left:1]]
drop_center (body from y=-60, 60 frames): A y=-47.8043 vel 0,0 hits=1
                                          B y=-47.8043 vel 0,0 hits=1
                                          C y=-47.8043 vel 0,0 hits=1
```

- **A** (outer contour only): the hole centre reports **1** hit — the interior is solid.
- **B** (outer + hole contour as two `CollisionPolygon2D`s): the hole centre reports **2** hits —
  the second collider **adds solid material**; it never subtracts.
- **C** (the same ring authored as **four solid slabs**): the hole centre reports **0** hits —
  the hole is finally a hole. This is the positive control.
- The falling-body variant does **not** discriminate here (the ring has material *above* the hole,
  so all three builds rest at `y=−47.8043`); the point query is the discriminating instrument.

**Law: 2D physics has no subtractive shape. A Geometry2D hole contour cannot be assigned away —
author the hole as multiple solid pieces.** The `drop_center` cell is kept as a second
solid-square rest pin (`y=−47.8043`), not as hole evidence.

### 3.11 r87 `exact_match` granularity (`input89_edges:exact`) — [M], closes the r87 unknown

```
PASS input89_edges exact control=wW_eia_ex=1_actual=1 sW_eia_ex=1_actual=1 eia_wW=ex=1 inex=1
  eia_sW_vs_wW=ex=0 inex=1  eia_wW_vs_sW=ex=0 inex=0  eia_sW=ex=1 inex=1
  eia_both=plainW[ex=1 inex=1] shiftW[ex=1 inex=1]
  poll_shiftW_on_plainW_binding=w[ex=false inex=true] sw[ex=true inex=true]
  poll_after_shiftW_release=w[ex=false inex=false] sw[ex=false inex=false]
  poll_plainW=w[ex=true inex=true] sw[ex=false inex=false] both[ex=true inex=true]
  poll_plainW_released=w[ex=false inex=false] both[ex=false inex=false]
  just_after_flush=w_jp[ex=false inex=true]
```

- **Matching is asymmetric**: an **unmodified** binding matches a **modified** event under
  `exact_match=false` (`eia_sW_vs_wW: ex=0 inex=1`) but a **modified** binding never matches an
  **unmodified** event under either value (`eia_wW_vs_sW: ex=0 inex=0`) — r87's `jpbe` result
  confirmed from the other direction.
- **The poll-time flag is load-bearing [M]**: with only the plain-`W` binding present, a parsed
  `shift+W` press reads `is_action_pressed(w, exact=false)=true` **and**
  `is_action_pressed(w, exact=true)=false` — r87's open question "whether exactness ever changes a
  polled answer" is answered **yes**, and the mechanism is the modifier-widened match, not a
  modifier on the probe.
- The same divergence appears in `is_action_just_pressed` (`w_jp[ex=false inex=true]`).
- The release of the widened match clears both readings (`poll_after_shiftW_release` all false).
- A control line (`wW_eia_ex=1_actual=1 sW_eia_ex=1_actual=1`) proves the binding shape itself
  matches, so every `0` above is informative. stderr is **0 B** (parse events are `duplicate()`d;
  the naive same-instance re-parse emits a WARNING — see §5.4).

### 3.12 r87 joypad analog-axis device filter (`input89_edges:axisdev`) — [M], closes the r87 unknown

```
PASS input89_edges axisdev census=joys=0 eia_avail=true dz_ax0=0.2000 dz_ui_accept=0.5000
  eia_dev0=ax0[ex=1 inex=1] axany[ex=1 inex=1]
  eia_dev5=ax0[ex=0 inex=0] axany[ex=1 inex=1]
  eia_dev-1=ax0[ex=0 inex=0] axany[ex=1 inex=1]
  poll_dev5=ax0=false axany=true axis5=1.0000 axis0=0.0000 strength0=0.0000
  poll_dev0=ax0=true axany=true axis0=1.0000 strength0=1.0000 raw0=1.0000
  poll_dev0_06=ax0=true axis0=0.6000 strength0=0.5000 raw0=0.6000
  poll_dev0_neg=ax0=false axany=true axis0=-1.0000
  poll_release=ax0=false axany=true axis0=0.0000
```

- With `joys=0`, a **device-5** `InputEventJoypadMotion` does **not** press a device-0-bound action
  (`ax0=false`) — the analog-axis twin of r87's button result — **but its device state bank is
  written anyway** (`Input.get_joy_axis(5,0)=1.0000`, `axis0=0.0000`) **[M]**.
- `device=-1` in a binding means **any device** (`axany` matches dev 0/5/−1 under both exactness
  values) **[M]**.
- Sign selects direction: a `−1.0` event does not press an action bound with `axis_value=1.0`
  (`poll_dev0_neg: ax0=false, axis0=-1.0000`) **[M]**.
- **New bonus pin: the default deadzone of a freshly added action is 0.2**
  (`dz_ax0=0.2000`, `dz_ui_accept=0.5000`) — visible in `strength=0.5000` at `|v|=0.6` with
  `raw=0.6000` **[M]**. r87 pinned `dz_ui=0.50` for builtins; the custom-action default was not pinned.

---

## 4. Falsification list

| id | must-differ input | result |
|---|---|---|
| F1 | arm dispatch is real: 23 arms must give 23 distinct signatures, none the census fallback | **PASS** — every `PASS` line carries its arm name; no two cells share a signature |
| F2 | `merge` of a contained square produces a hole contour | **REFUTED [A]** — `merge(big,small)=k=1 a=1600`, no hole; my own hypothesis died here (§3.3) |
| F3 | `clip`/`exclude` of a contained square produce a hole | **PASS** — `k=2`, inner contour `a=−100.0000` (negative winding) |
| F4 | assigning the hole contour as a second `CollisionPolygon2D` subtracts material | **REFUTED [A]** — the hole centre goes `centre:1 → centre:2` (it *adds*); a 4-slab build gives `centre:0` |
| F5 | `offset_polygon(∅)` crashes like `offset_polyline(∅)` | **REFUTED [A]** — `offset_polygon(∅)=k=0{}` rc=0 clean; `offset_polyline(∅)` SIGABRT rc=134 ×3 |
| F6 | `join_type` changes a negative-delta polygon offset | **REFUTED [A]** — all three joins give byte-identical `n4 a=256.0000` |
| F7 | `END_POLYGON` is usable on a closed polyline | **REFUTED [A]** — open **and** closed both return `k=0{}` plus the refusal ERROR |
| F8 | the bridge pin is a frame-count pin (tps-independent) | **REFUTED [A]** — 120 tps/60 frames is mid-fall (`y=22.5250`, `vel 0,478.1458`); 120 tps/**120** frames reproduces `82.3000` |
| F9 | `is_point_in_polygon` and `point_is_inside_triangle` share a boundary policy | **REFUTED [A]** — polygon: edge true, 1e-4 outside true, 1e-3 false; triangle: edge false, first true at 1e-6 inside |
| F10 | `segment_intersects_circle`'s fraction is direction-dependent | **REFUTED [A]** — `0.2500` both directions (it is the *entry* fraction); `0.5` from inside = exit |
| F11 | poll-time `exact_match` never changes an answer (r87's open question) | **REFUTED [A]** — `w[ex=false inex=true]` on a modifier-widened press |
| F12 | a device-5 axis event presses a device-0-bound action (or is dropped entirely) | **REFUTED both ways [A]** — action not pressed, device state bank still written (`axis5=1.0000`) |
| F13 | `offset_polyline`'s sign-insensitivity is a default-args artifact | **REFUTED [A]** — `(+2,ROUND,END_JOINED)` and `(−2,ROUND,END_JOINED)` are byte-identical |
| F14 | `triangulate_polygon`/`decompose_polygon_in_convex` lose area | **REFUTED [A]** — triangle-sum and convex-piece-sum both equal the polygon area to 4 dp (280.0000) |
| F15 | the census's `geo_phys` bridge value reproduces under the battery's launch shape | **PASS** — `rest_y=82.3000 self_hit=1`, byte-equal to the census |

---

## 5. Hazards recorded (for the author and the boundary seat)

1. **`offset_polyline(∅, …)` is a SIGABRT vector [M]** — rc **134** ×3, stderr byte-identical
   (377 B): `std::vector<Clipper2Lib::Point<double>>::operator[] … Assertion '__n < this->size()'
   failed.` + `timeout: the monitored command dumped core`. Uncatchable from GDScript, no `ERROR`
   line, no rc-1. Reproduces the census's §5 exactly. **Never place it in an authorable row**
   (census §9.8); it is offered as an optional crash row in §6.2 only.
2. **`make_atlas(∅)` is a loud refusal [M]** — `ERROR: Condition "p_rects.is_empty()" is true.
   at: make_atlas (core/math/geometry_2d.cpp:148)` and `{points:[], size:(0,0)}`, rc=0. One
   `expected_errors` line (§6.3). (The census's wrong-signature error was the same file at `:150`.)
3. **`offset_polyline(…, END_POLYGON)` always refuses [M]** — open *and* closed input both give
   `k=0{}` plus `ERROR: Attempt to offset a polyline like a polygon (use offset_polygon instead).
   at: offset_polyline (./core/math/geometry_2d.h:336)` (2 occurrences in the isolated arm).
   One `expected_errors` line covers both.
4. **GDScript has no `%e` format specifier [O]** — `"%.0e" % [x]` emits
   `ERROR: String formatting error: unsupported format character.
   at: validated_evaluate (core/variant/variant_op.h:770)` and returns the format string
   unchanged (so the "value" printed is the literal format text). The three affected reps are
   preserved under `runs/fmtbug/`; the fixed cell uses literal labels.
5. **Re-parsing the same `InputEvent` instance in one frame is a WARNING, not an error [M]** —
   `WARNING: An input event object is being parsed more than once in the same frame, which is
   unsafe. … at: parse_input_event (core/input/input.cpp:1540)`. The main classifier tolerates it
   (no `ERROR:`), but `classify_streams` rejects any unexpected stderr line — so probe code that
   parses must use `duplicate()` (the emitted `input89_edges` probe does; stderr is 0 B).
6. **`clip_polygons`/`merge_polygons` may rotate the start vertex of a passthrough result [M]** —
   `clip(sq,∅)` is the same contour starting at a different vertex. A "byte-identical to input" pin
   is wrong; pin the returned string.
7. **Holes exist in the geometry and not in the collider [M]** — §3.10. Negative-area contours are
   the in-band hole signal.
8. **Frame-counted physics cells are duration cells [M]** — §3.9. State the tps in the cell.
9. **Predicate boundary policies differ three ways inside `Geometry2D` [M]** — §3.6. Do not
   assume "boundary-inclusive" for the whole class.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (20, exec-checked)

`corpus/live/r89-scout/author-rows.py.txt` holds the exact 5-tuples, and
`python3 verify_rows.py` classifies all 20 with the production `classify_process` extracted
verbatim from `corpus/fixtures/run_battery.py` (segment sha256 `749fa060…`) → **`rows=20 rejected=[]`**.

```
geo2d_lattice_{census,ops,contain,joins,trig,pred,pipedges,edge,offempty,offdeg,bridge,
               ring,ring2,ring4,ringhits} + input89_edges_{exact,axisdev}
```
plus `geo2d_lattice_atlasempty` and `geo2d_lattice_polyendpoly` (each needs one
`expected_errors` entry, §6.3).

Probe files land at `corpus/fixtures/geo2d_lattice.gd` (sha256 `9784716b…`) and
`corpus/fixtures/input89_edges.gd` (sha256 `601c223e…`). Insert the rows ahead of the
crash/descendant tail like prior blocks; no fixture change beyond the two probe files is needed
(both probes are self-contained `SceneTree` scripts and use the battery's `--arm=` convention).

**Not rows** (receipts only, do not author):
`geo_bridge_tps120` / `geo_bridge_tps120_f120` (need a 120 tps project — only reachable via the
r86 nested-boot pattern), `geo_bridge_hole` / `geo_bridge_hole2` (the falsified `merge`-hole
hypothesis; they are the second solid-square rest pin `y=−47.8043` and the "merge collapses
containment" receipt), `geo_lineempty` (crash vector, §6.2).

### 6.2 Optional crash row (boundary-seat decision)

`("geo2d_lattice_lineempty", "geo2d_lattice.gd", ["--arm=lineempty"], -6, "R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)")`
— verified as a `-6` row under the production classifier. It documents an uncatchable Clipper2
assert reachable from script; the census's §9.8 rule ("keep it out of any probe as a payload")
still holds — this is a *dedicated single-call* arm, not a payload.

### 6.3 `expected_errors` additions (dict in `run_battery.py`, keyed by case name)

```python
'geo2d_lattice_atlasempty': (
    'ERROR: Condition "p_rects.is_empty()" is true.',
),
'geo2d_lattice_polyendpoly': (
    'ERROR: Attempt to offset a polyline like a polygon (use offset_polygon instead).',
),
```
Every other row is `ERROR:`-clean with **0 B stderr** (measured).

### 6.4 What to pin and what not to pin

1. **Pin the full `PASS geo2d_lattice …` line as the row signature** — it carries the arm name, so
   the row is arm-verified and the r88 silent-fallback failure cannot recur.
2. **Pin `_poly2str`/`_poly2str_area` output verbatim** (census §9.1) — the shape is
   `k=<n>{n<size>[x,y;…] a=<signed area>|…}`; coordinates `%.4f`.
3. **Pin `tri_area == poly_area` and `dec_area == poly_area` as invariants**, not just indices —
   they are the only self-checking values in the trig arm.
4. **Pin the boundary-policy table** (§3.6) rather than a single "inside/outside" pair.
5. **Do not pin ideal contact geometry** in the bridge/ring cells — pin the measured `82.3000` /
   `−47.8043` (the solver's margin is part of the measurement).
6. **Do not pin `hull` vertex counts generically** — `n+1` for polygons, `n1` for a single point,
   `n3` for collinear input.
7. **No envelope/mode-distribution is needed anywhere in this surface** — 23/23 cells are
   single-valued. If a future cell pairs a physics await with a frame-indexed count, re-check
   against the r87 lesson before pinning.

---

## 7. Remaining unknowns / not measured

- **The census's other PINNABLE families were not touched this round** (RigidBody2D extras,
  offline/loopback multiplayer, spawner/synchronizer, sprite metadata, 2D lights, positional audio,
  visibility notifiers). They remain candidates for r90+; the census's §3 values are single-sample
  scout receipts, not battery rows.
- **`make_atlas` coercion mechanics** (`Array` → `PackedVector2Array`) still not dissected — only
  the flat-`PackedVector2Array` form was exercised.
- **Hole representation workarounds**: 4-slab decomposition is measured as *possible*; whether
  `CollisionPolygon2D.BUILD_SEGMENTS` or a `ConcavePolygonShape2D` gives a cheaper hole was **not**
  measured.
- **The solver margin** (82.3000 vs the ideal 82.0; −47.8043 vs −48.0) was not decomposed — it is
  deterministic here but its dependence on mass/radius/solver iteration count is unmeasured.
- **`offset_polyline` sign-insensitivity mechanism** — measured on three join/end combinations; the
  internal reason (absolute-value normalization in the Clipper2 wrapper) is **[I]**.
- **tps other than 60/120**, `physics/2d/solver/*` overrides, and `run_on_separate_thread` were not
  split for the bridge cell (the r86 lattice covers backend selection).
- **SubViewport cursor** and **`event_index` semantics for 1..31** (r87 unknowns) — not taken (need
  a display server / frame-sequenced probe).
- **Portability**: every value is this host/build/`--headless`/GodotPhysics2D; `DisplayServer` is
  headless in every receipt.
- **`lsp` absent**: all `file:line` citations are engine-emitted `at:` text.

---

## 8. Host cleanup

- 128 godot launches total = **99 canonical cell runs** + 2 discovery runs + 27 superseded runs
  (18 round-1 runs for 4 cells re-run after a probe revision, 6 round-1 `census`/`joins` runs
  re-cut to be ERROR-free, 3 `%e`-format-bug `pipedges` reps preserved under `runs/fmtbug/`),
  **all `--headless`, all `timeout`-bounded** (bound 15 s); no run hit the bound, no run was left
  running.
- `pgrep -fa godot` at report time lists only the concurrent **g3d** lane's
  `r92-baseline`/`r99-scout` processes — **none from this seat**.
- No tracked file written: `git status --porcelain` shows no modified tracked file and no
  `corpus/fixtures/` addition from this seat.

## 9. Evidence index

All under `corpus/live/r89-scout/`; `manifest.sha256` (330 lines) covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| primary probe, 17 arms | `probes/geo2d_lattice.gd` | `9784716b5d6932fa` |
| r87-split probe, 2 arms | `probes/input89_edges.gd` | `601c223ed7a32d91` |
| discovery micro-probe | `probes/discover.gd` | `d4feb378baabcd36` |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| 120 tps variant project | `proj_tps120/project.godot` | `1bcaeba7d52c27ee` |
| round-1 / round-2 drivers | `run_cells.sh`, `run_cells2.sh` | `f3e35d1ef9bb3bfc`, `7b49e47d2621e944` |
| analyzer | `analyze_r89.py` → `analyze_r89.json` | `2d9c18e49768b6cb`, `ce631cedb229591a` |
| author rows + verifier | `author-rows.py.txt`, `verify_rows.py` | `0dbb9dd5c97ba4cb`, `91b69859ae74335c` |
| per-cell receipts (99 runs × 3 files) | `runs/` | `manifest.sha256` |
| superseded `%e`-bug reps | `runs/fmtbug/` | `manifest.sha256` |
| discovery receipts | `runs/disc-*.{out,err}` | `manifest.sha256` |

Reproduce: `bash run_cells.sh && bash run_cells2.sh`, then `python3 analyze_r89.py &&
python3 make_author_rows.py && python3 verify_rows.py` (expect `UNSTABLE=[]`, `rows=20 rejected=[]`).
