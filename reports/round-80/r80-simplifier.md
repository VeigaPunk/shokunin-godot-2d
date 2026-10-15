# game-dev-2d round 80 — simplifier (g2d): fifteen proven deletions in `phys2d_motion.gd` (−105 lines), battery block audited clean

Seat `SIMPLIFIER` (LEAF) | lane `g2d` | round 80 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python
3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD `d9320dd` (r79
report-last) + dirty r80 landing — **no commit by this seat, no tracked file
written, no git mutation**. Shared tree verified byte-identical before
reporting: `git status` still shows only the pre-existing dirty pair
(`SCORECARD.md` +30, `corpus/fixtures/run_battery.py` +70); the landed fixture
stays sha256 `f622b89e3093dd5da44dd10ed26b480a506fb04b139861056567d37788337047`,
the battery stays `66bfe3e25c931c7038d2692a47f1edfb54f05392f0070d92d9092f2e1c6e6d61`.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed and no
GDScript/Python language server is installed on this host. Deletion-candidate
proofs therefore rest on (a) complete textual enumeration of every
reader/writer of the suspect symbol inside the only file that binds it, and
(b) fresh-process receipt equivalence of the folded battery against a
same-session control — the narrow existing check, run verbatim. Text grep is
used as the literal fallback only; it is never presented as standalone semantic
proof — the battery receipts are the semantic carrier.

**Scope:** the r80 delta only — `corpus/fixtures/phys2d_motion.gd` (new,
879 lines) and the inserted `CASES`/`expected_errors` block in
`run_battery.py`. r79-and-earlier code untouched.

**Writes:** this report and `corpus/live/r80-simplifier/**` only.

---

## 1. Method

Per brief: hunt only what is **provably** removable — dead vars, tautological
asserts, unreachable arms, duplicated helper bodies, stale comments. Proof bar
per candidate: apply the fold in a scratch copy → the full battery still runs
139/139 → every row's verdict tuple identical, and all 28 `phys2d_motion` rows
emit byte-identical `PASS` lines.

Workspace (all under `corpus/live/r80-simplifier/`):

| artefact | content |
|---|---|
| `vfold/` | the fold as full file copies: `phys2d_motion.gd` (**774 lines**, sha `6fb77d72…`), `run_battery.py` (**byte-identical** to fixtures, sha `66bfe3e2…` — audited, nothing provably dead) |
| `fold.diff` | unified diff `corpus/fixtures` → `vfold`; **−208/+103 lines, all in `phys2d_motion.gd`** (inlined §4) |
| `vfold-fixtures/` | runnable folded project: full `corpus/fixtures/` copy with the vfold pair swapped in (`diff -qr` vs fixtures: exactly one differing file, `phys2d_motion.gd`) |
| `control-runs/20261015T061328965017Z/` | same-session battery on the **unmodified** tree → **139/139 PASS** |
| `fold-runs/20261015T061528687738Z/` | battery on `vfold-fixtures/` → **139/139 PASS** |
| `receipts/` | both batteries' stdout/stderr (stderr empty both), `fold-compare.txt`, `godot-tuples-{control,fold}.txt`, `phys2d-output-compare.txt`, `arm28-{control,fold}.txt` + `arm28-smoke.diff` |
| `MANIFEST.sha256` | covers the fold, diff, receipts, and both `verdicts.json` |

Batteries ran **sequentially** (never parallel) with absolute `--runs`, per the
author's observed constraints.

## 2. Killed — all in `phys2d_motion.gd`

### K1. Header arm census — was `:9–37` (−29)

A 29-line `# Arms` comment enumerating all 28 arms with per-arm semantics —
the identical pattern this seat deleted in r79 (K1). It is a **duplicate arm
index** subordinate to the `match arm:` dispatch, which is the sole index the
battery exercises; the r79 census had already drifted (20 listed / 23 real) and
this one drifts the same way the next time an arm lands. Currently accurate —
that is precisely the state r79 judged worth removing before it rots. Replaced
with one line keeping the accurate count and the scout pointer:
"`# The `match arm:` dispatch in _run is the sole arm index (28 arms);`" and
"`# per-arm measured classes live in r80-scout §1.1-1.3.`"

### K2. Dead teardown apparatus — `_raw_rids` / `_track` / `_free_tracked` / `_tracked_nodes` / `_finish` frees (−22)

`_track()` had **zero call sites** (sole occurrence: its own definition), so
`_raw_rids` was provably always empty and `_free_tracked()` a provable no-op.
`_tracked_nodes` was write-only: its sole reader was the `queue_free` loop in
`_finish`, which ran a deferred free immediately before `quit(0)` — vacuous,
since process exit frees the whole tree and nothing prints afterward. All
nine `.append` sites deleted with it. Confirmation, not just assertion: the
folded run emits **zero** `leaked`/`ObjectDB` lines on all 139 rows and both
batteries' stderr is empty.

### K3. Unread node names + `_mk_wall`'s `nm` param (−9 decls, −39 call args)

All 9 `.name =` writes (`"B"`, `"C"`, `"G%d"`, `"S%d"`, `"R"`, `"RH"`, `"IB"`,
`"F"`, `_mk_wall`'s `nm`) were dead stores: no `.name` read, `get_node`, or
name-print path exists anywhere in the file, and the pinned outputs carry class
names via `get_class()` only. `_mk_wall(pos, size, nm)` → `_mk_wall(pos, size)`;
all 39 call sites lose the literal name arg.

### K4. Inline `for i in N: await physics_frame; _frame_no += 1` ×4 → `await _frames(N)` (−8)

Literal re-implementations of the existing `_frames` helper at former
`:212, :267, :314, :356` (ccd_ladder 30, ccd_gap 30, ccd_spin 8, ccd_edge 30).
The conditional `while` waits in cont_*/bds_* and the counting loop in
cont_persist are different control flow and stay.

### K5. `keys` mirror arrays in ccd_gap/ccd_spin/ccd_edge (−6)

Each arm re-recorded the `["d","r","s"]` iteration order into a parallel `keys`
array read back as `keys[i]` — a second authority for a constant list. Replaced
with direct indexing `["d","r","s"][i]` at the read site.

### K6. `b.set_meta("lane", lane)` in ccd_ladder (−1)

`set_meta` is the only meta call in the file; `get_meta` has zero callers.
Dead store.

### K7. Always-default parameters (−3 params)

`_mk_bullet.r` (2/2 callers default → pinned `BULLET_R`), `_mk_char.r`
(20/20 callers default → 10.0), `_mk_faller.monitor` (3/3 callers `true`).
Dead generality, not extension points-in-waiting.

### K8. Four spellings of the CCD key→mode map → one `const CCD` (±0 net)

`modes` enum dict in ccd_ladder + `{"d": 0, "r": 1, "s": 2}` int dicts in
ccd_gap/ccd_spin/ccd_edge. Now `const CCD := {"d": CCD_MODE_DISABLED, "r":
CCD_MODE_CAST_RAY, "s": CCD_MODE_CAST_SHAPE}` beside the other consts — one
authority, and the `mode` local in ccd_edge inlines away entirely.

### K9. RigidBody2D construction duplicated ×4 → `_mk_rigid(pos, shape)` (−28 net)

`_mk_bullet` (circle r8), `ccd_gap` (16×16 box), `ccd_spin` (8×128 bar) and
`mac_rigid` (two r10 circles) each re-implemented new→shape→CollisionShape→
position→gravity_scale→add_child. `_mk_rigid` is the shared body; per-arm props
(`can_sleep`/`ccd`/`monitor`/`cap`/signal hookups) stay at the call site.
`mac_rigid`'s twin bodies now share one `CircleShape2D` resource (shape data is
read-only geometry — identical physics, 17 lines → 5). Setup-order delta: ccd/
monitor/cap/connect now land after `root.add_child` instead of before — all are
server-side props and signal hookups evaluated no earlier than the first
physics tick, which happens after all setup; the battery verifies byte-level.

### K10. `btm_embed` hand-unrolled r/p/h ×5 → spec loop (−7)

Five copy-paste test blocks folded into the `for spec in [...]` convention the
file already uses in `btm_from2`/`btm_recflag`; `collide_separation_ray` carried
as the 4th spec field. Printed row text identical (`rec_off[...] rec_on[...]
rec_on_sepray[...] away_off[...] away_on[...]`).

### K11. `_cb_reads` member → local in `bds_windows` (−1 member)

Member dict read by exactly one arm; `cont_windows` already uses the local-dict
captured-by-lambda pattern (`reads`). Narrowed to a local `cb_reads`.

### K12. Query-param object reuse (±0 net)

`dss_embed` built three identical `(circle, (96,0), (200,0))` params for
`collide_shape`/`intersect_shape`/`get_rest_info` — now all three reuse `pt`.
`dss_shapes` built two identical mover-pose params → `qm`, two identical
embedded params → `qz` (five fresh constructions → two). Proven safe by the
round's own `dss_purity` arm: params are byte-identical after queries, so
sharing cannot observe.

### K13. Dead setup walls in `mac_maxcol` + `dss_wrongarg` (2 dead setups, ±0 net)

Both arms' calls refuse **before any query executes** — `mac_maxcol` on arity
(5-arg `callv` → typed refusal), `dss_wrongarg` on param class/null. The walls
were geometric props no code path could reach; the arms' own expected_errors
still fire under the fold (see raw-output note §3). Walls whose scenario feeds
a real query were kept (`mac_miss`, `dss_purity`, `dss_motion`, …).

### K14. Redundant `pos1` snapshot in `mac_embed` (−1)

`b` is never moved after `c1` returns; `b.global_position` at print time is the
same value. (`mac_test_only`'s `pos1` is a *true* snapshot — taken before `c2`
moves the body — and stays.)

### K15. `ccd_spin` second-loop rotation recompute → `poses[i]` (±0)

The emit loop recomputed `snappedf(rad_to_deg(fposmod(b.rotation, TAU)),
0.01)` already stored in `poses[i]`; no physics frame intervenes.

## 3. The proof — receipt equivalence, not suspicion

`compare.py godot` (r80-baseline seat's differ, reused unmodified): stable
verdict tuple per row + normalized-output compare.

| ref | rows | tuple_mismatches | output-normalized |
|---|---|---|---|
| same-session control `…061328…Z` | 139 | **0** (seeded 0 / meta 0) | identical=132, differing=0, not-carried=7 |
| fold `…061528…Z` | 139 | — | verdict PASS |

- `receipts/godot-tuples-{control,fold}.txt`: the two 139-row tuple sets are
  **byte-identical** (`diff` empty).
- `receipts/arm28-{control,fold}.txt`: direct per-arm runs — all 28 arms'
  `rc`, ERROR-line counts, and full `PASS` lines **byte-identical**
  (`arm28-smoke.diff` empty).
- **Only raw-output delta in the corpus:** GDScript backtrace line numbers in
  `mac_maxcol` (`:566`→`:481`, `:136`→`:94`) and `dss_wrongarg` (`:735–741`→
  `:633–639`) — the error sites shifted because the file shrank. Line-number
  tokens are declared volatile by the differ's own `NORM_RULES`
  (`\.(gd|lua|py):\d+ → :<N>`); verdict tuples, signatures, and per-row ERROR
  counts are unchanged, and the `probe_error_clause_surface` census row passed
  identically (every `expected_errors` entry still absorbs a live error).
- Fixture parse: `godot --headless --check-only --path vfold-fixtures --script
  res://phys2d_motion.gd` → exit 0, no diagnostics.
- `run_battery.py` r80 block **audited, nothing provably dead**: all 28 CASES
  rows are reached by the fixture's `match`; both new `expected_errors` entries
  absorb real emissions (verified live in both runs); the ordering-constraint
  comment is accurate and load-bearing.

### Considered and **not** taken (stop line)

- `_kc_line`'s `if c == null` arm — kept: reachable in principle from the
  unguarded hit-path callers (`mac_hit`, `tm_hit`, `mac_nodecomp`, `mac_chain`,
  `mac_embed`); it is a guard on a shared formatter, not dead code.
- `var tag := lane` closure binds (gap/spin/edge) — kept: the per-lane `hits`
  keys depend on capture semantics; the fold does not need this risk.
- `mac_miss`/`dss_purity`/`dss_motion` walls — kept: their queries **execute**
  against a populated space; deleting would make the measured claims vacuous,
  unlike K13's never-executed calls.
- `_exits` → local, `_frames(2)` pre-registration awaits, `ptq.position` —
  kept: conversions cost lines or rest on unproven claims about registration
  timing.
- r79-or-earlier code — untouched per scope.

## 4. Verified `fold.diff` (applied in scratch; 879→774 lines, −208/+103)

```diff
--- corpus/fixtures/phys2d_motion.gd	2026-10-15 02:49:37.173468922 -0300
+++ corpus/live/r80-simplifier/vfold/phys2d_motion.gd	2026-10-15 03:11:33.774770842 -0300
@@ -4,51 +4,22 @@
 #   godot --headless --path <scratch> --script res://phys2d_motion.gd -- --arm=<name>
 # Prints R80 diagnostic lines and one final `PASS phys2d_motion <arm> ...` line.
 # No object ids / addresses / RIDs are printed (byte-stability).
-# The `match arm:` dispatch in _run is the sole arm index (28 arms).
-#
-# Arms (measured class per arm, r80-scout §1.1-1.3)
-#   ccd_ladder      lattice-phase tunneling: continuous_cd {off,ray,shape} x velocity ladder, thin wall
-#   ccd_gap         cast_ray >> cast_shape (counterintuitive): box16x16 vs 12px slot wall
-#   ccd_spin        absence + tolerated end-overlap (weak cell): bar spins past an offset short wall (90deg/step)
-#   ccd_edge        cast_shape misses a real edge clip: circle edge overlaps a wall the center ray misses
-#   btm_from        params.from honored literally: unset vs set
-#   btm_hit         clean hit field dump (travel/rem/pt/n/depth/sf/uf)
-#   btm_embed       recovery always reported; recovery_as_collision flag inert (off/on/sepray)
-#   btm_margin      margin inflates depth, not travel: margin ladder on the hit geometry
-#   btm_from2       unset-from resolves to Transform2D() origin, never the body pose (discriminator)
-#   btm_recflag     recovery_as_collision inert: embedded start x zero/tiny motion isolator
-#   mac_hit         move_and_collide = body_test_motion + position write: field dump + end position
-#   mac_miss        miss -> null + full travel
-#   tm_hit          test_move pure twin: bool + out-collision + no move
-#   mac_test_only   move_and_collide(test_only=true) side-effect-free on both tiers
-#   mac_nodecomp    no auto-decomposition/slide: end = start + travel only
-#   mac_chain       chaining is caller-managed: remainder.slide(normal) into an L corner
-#   mac_maxcol      arity = 4, no max_collisions: 5-arg callv -> typed refusal, rc=0
-#   mac_rigid       RigidBody2D honors move_and_collide; server adopts the resulting pose
-#   mac_embed       embedded recovery + margin arg-vs-property channels inert
-#   dss_motion      motion honored split: cast_motion/get_rest_info sweep vs collide/intersect pose
-#   dss_embed       cast_motion blind to initial overlap; pose probes still report it
-#   dss_shapes      return-shape census (dict keys, lv field, max_results counts contacts not points)
-#   dss_purity      query params are read-only: fields byte-identical after each call
-#   dss_wrongarg    null / wrong-class params -> typed empties + error lines, no crash
-#   cont_windows    contact materialization windows: get_contact_count vs get_colliding_bodies
-#   cont_cap        count = contact points, array = bodies; max_contacts_reported truncates
-#   bds_windows     body_get_direct_state at out-of-phase / in-phase / in-cb / _integrate_forces
-#   cont_persist    colliding array clears the frame after exit, no linger
+# The `match arm:` dispatch in _run is the sole arm index (28 arms);
+# per-arm measured classes live in r80-scout §1.1-1.3.
 
 const WALL_X := 100.0
 const WALL_HALF := 2.0
 const BULLET_R := 8.0
+const CCD := {"d": RigidBody2D.CCD_MODE_DISABLED,
+	"r": RigidBody2D.CCD_MODE_CAST_RAY,
+	"s": RigidBody2D.CCD_MODE_CAST_SHAPE}
 
 var arm := ""
 var _frame_no := 0
-var _raw_rids: Array = []
-var _tracked_nodes: Array = []
 
-# contact-monitor capture state
+# contact-monitor capture state (shared with the _mk_bullet callback)
 var _entries: Array = []
 var _exits: Array = []
-var _cb_reads: Dictionary = {}
 
 class IntegBody extends RigidBody2D:
 	var seen: Dictionary = {}
@@ -107,23 +78,10 @@
 	quit(1)
 
 func _finish(line: String) -> void:
-	for n in _tracked_nodes:
-		if is_instance_valid(n):
-			n.queue_free()
-	_tracked_nodes.clear()
-	_free_tracked()
+	# nodes/RIDs die with the process on quit(); no teardown bookkeeping.
 	print("PASS phys2d_motion " + line)
 	quit(0)
 
-func _track(rid: RID) -> RID:
-	_raw_rids.append(rid)
-	return rid
-
-func _free_tracked() -> void:
-	for i in range(_raw_rids.size() - 1, -1, -1):
-		PhysicsServer2D.free_rid(_raw_rids[i])
-	_raw_rids.clear()
-
 func _space() -> RID:
 	return root.world_2d.space
 
@@ -146,9 +104,8 @@
 	PhysicsServer2D.body_set_state(b.get_rid(), PhysicsServer2D.BODY_STATE_TRANSFORM,
 		Transform2D(0, to))
 
-func _mk_wall(pos: Vector2, size: Vector2, nm: String) -> StaticBody2D:
+func _mk_wall(pos: Vector2, size: Vector2) -> StaticBody2D:
 	var b := StaticBody2D.new()
-	b.name = nm
 	var cs := CollisionShape2D.new()
 	var rs := RectangleShape2D.new()
 	rs.size = size
@@ -156,40 +113,39 @@
 	b.add_child(cs)
 	b.position = pos
 	root.add_child(b)
-	_tracked_nodes.append(b)
 	return b
 
-func _mk_bullet(pos: Vector2, vel: Vector2, ccd: int, r: float = BULLET_R) -> RigidBody2D:
+func _mk_rigid(pos: Vector2, shape: Shape2D) -> RigidBody2D:
 	var b := RigidBody2D.new()
-	b.name = "B"
 	var cs := CollisionShape2D.new()
-	var sh := CircleShape2D.new()
-	sh.radius = r
-	cs.shape = sh
+	cs.shape = shape
 	b.add_child(cs)
 	b.position = pos
 	b.gravity_scale = 0.0
+	root.add_child(b)
+	return b
+
+func _mk_bullet(pos: Vector2, vel: Vector2, ccd: int) -> RigidBody2D:
+	var sh := CircleShape2D.new()
+	sh.radius = BULLET_R
+	var b := _mk_rigid(pos, sh)
 	b.can_sleep = false
 	b.continuous_cd = ccd
 	b.contact_monitor = true
 	b.max_contacts_reported = 4
 	b.body_entered.connect(func(_n: Node) -> void: _entries.append(1))
-	root.add_child(b)
 	b.linear_velocity = vel
-	_tracked_nodes.append(b)
 	return b
 
-func _mk_char(pos: Vector2, r: float = 10.0) -> CharacterBody2D:
+func _mk_char(pos: Vector2) -> CharacterBody2D:
 	var b := CharacterBody2D.new()
-	b.name = "C"
 	var cs := CollisionShape2D.new()
 	var sh := CircleShape2D.new()
-	sh.radius = r
+	sh.radius = 10.0
 	cs.shape = sh
 	b.add_child(cs)
 	b.position = pos
 	root.add_child(b)
-	_tracked_nodes.append(b)
 	return b
 
 # ---------------------------------------------------------------- Q1: CCD
@@ -198,20 +154,16 @@
 	# All 21 cells fly simultaneously in parallel y-lanes (600px apart): 30
 	# physics frames total instead of 630, same determinism.
 	var vels := [600.0, 1150.0, 1200.0, 2000.0, 2400.0, 3000.0, 3600.0]
-	var modes := {"d": RigidBody2D.CCD_MODE_DISABLED, "r": RigidBody2D.CCD_MODE_CAST_RAY, "s": RigidBody2D.CCD_MODE_CAST_SHAPE}
 	var bullets: Array = []
 	var lane := 0
 	for mk in ["d", "r", "s"]:
 		for v in vels:
 			lane += 1
 			var y := float(lane) * 600.0
-			_mk_wall(Vector2(WALL_X, y), Vector2(4, 400), "W%d" % lane)
-			var b := _mk_bullet(Vector2(0, y), Vector2(v, 0), modes[mk])
-			b.set_meta("lane", lane)
+			_mk_wall(Vector2(WALL_X, y), Vector2(4, 400))
+			var b := _mk_bullet(Vector2(0, y), Vector2(v, 0), CCD[mk])
 			bullets.append(b)
-	for i in 30:
-		await physics_frame
-		_frame_no += 1
+	await _frames(30)
 	var out: Array = []
 	var idx := 0
 	for mk in ["d", "r", "s"]:
@@ -236,39 +188,27 @@
 	var lane := 0
 	var hits := {}
 	var boxes: Array = []
-	var keys: Array = []
 	for mk in ["d", "r", "s"]:
-		var mode: int = {"d": 0, "r": 1, "s": 2}[mk]
+		var mode: int = CCD[mk]
 		lane += 1
 		var y := float(lane) * 800.0
-		_mk_wall(Vector2(WALL_X, y - 114.0), Vector2(4, 216), "Ga%d" % lane)
-		_mk_wall(Vector2(WALL_X, y + 114.0), Vector2(4, 216), "Gb%d" % lane)
-		var b := RigidBody2D.new()
-		b.name = "G%d" % lane
-		var cs := CollisionShape2D.new()
+		_mk_wall(Vector2(WALL_X, y - 114.0), Vector2(4, 216))
+		_mk_wall(Vector2(WALL_X, y + 114.0), Vector2(4, 216))
 		var rs := RectangleShape2D.new()
 		rs.size = Vector2(16, 16)
-		cs.shape = rs
-		b.add_child(cs)
-		b.position = Vector2(0, y)
-		b.gravity_scale = 0.0
+		var b := _mk_rigid(Vector2(0, y), rs)
 		b.can_sleep = false
 		b.continuous_cd = mode
 		b.contact_monitor = true
 		b.max_contacts_reported = 4
 		var tag := lane
 		b.body_entered.connect(func(_n: Node) -> void: hits[tag] = hits.get(tag, 0) + 1)
-		root.add_child(b)
 		b.linear_velocity = Vector2(2400, 0)
-		_tracked_nodes.append(b)
 		boxes.append(b)
-		keys.append(mk)
 		hits[tag] = 0
-	for i in 30:
-		await physics_frame
-		_frame_no += 1
+	await _frames(30)
 	for i in boxes.size():
-		var mk: String = keys[i]
+		var mk: String = ["d", "r", "s"][i]
 		var b: RigidBody2D = boxes[i]
 		out.append("%s_cross=%d %s_hit=%d %s_x=%s" % [mk, 1 if b.global_position.x > WALL_X + WALL_HALF else 0,
 			mk, hits.get(i + 1, 0), mk, snappedf(b.global_position.x, 0.001)])
@@ -284,36 +224,24 @@
 	var lane := 0
 	var hits := {}
 	var bars: Array = []
-	var keys: Array = []
 	for mk in ["d", "r", "s"]:
-		var mode: int = {"d": 0, "r": 1, "s": 2}[mk]
+		var mode: int = CCD[mk]
 		lane += 1
 		var y := float(lane) * 800.0
-		_mk_wall(Vector2(40, y + 40.0), Vector2(20, 4), "Sw%d" % lane)
-		var b := RigidBody2D.new()
-		b.name = "S%d" % lane
-		var cs := CollisionShape2D.new()
+		_mk_wall(Vector2(40, y + 40.0), Vector2(20, 4))
 		var rs := RectangleShape2D.new()
 		rs.size = Vector2(8, 128)
-		cs.shape = rs
-		b.add_child(cs)
-		b.position = Vector2(0, y)
-		b.gravity_scale = 0.0
+		var b := _mk_rigid(Vector2(0, y), rs)
 		b.can_sleep = false
 		b.continuous_cd = mode
 		b.contact_monitor = true
 		b.max_contacts_reported = 4
 		var tag := lane
 		b.body_entered.connect(func(_n: Node) -> void: hits[tag] = hits.get(tag, 0) + 1)
-		root.add_child(b)
 		b.angular_velocity = TAU * 15.0  # 90 deg per 1/60s step
-		_tracked_nodes.append(b)
 		bars.append(b)
-		keys.append(mk)
 		hits[tag] = 0
-	for i in 8:
-		await physics_frame
-		_frame_no += 1
+	await _frames(8)
 	# self-verifying: at every sampled pose, a motion=0 body_test_motion must be
 	# clean -> no discrete contact was available to catch.
 	var poses: Array = []
@@ -325,10 +253,10 @@
 		var rr := PhysicsTestMotionResult2D.new()
 		pose_hit.append(1 if PhysicsServer2D.body_test_motion(b.get_rid(), rp, rr) else 0)
 	for i in bars.size():
-		var mk: String = keys[i]
+		var mk: String = ["d", "r", "s"][i]
 		var b: RigidBody2D = bars[i]
 		out.append("%s_hit=%d %s_rot=%s %s_ccd=%d" % [mk, hits.get(i + 1, 0), mk,
-			snappedf(rad_to_deg(fposmod(b.rotation, TAU)), 0.01), mk,
+			poses[i], mk,
 			b.get_continuous_collision_detection_mode()])
 	_finish("ccd_spin w=90deg_per_step bar8x128 wall20x4@(40,+40) %s endposes=%s endpose_overlap=%s" % [
 		" ".join(out), poses, pose_hit])
@@ -341,23 +269,18 @@
 	var lane := 0
 	var hits := {}
 	var bodies: Array = []
-	var keys: Array = []
 	for mk in ["d", "r", "s"]:
-		var mode: int = {"d": 0, "r": 1, "s": 2}[mk]
 		lane += 1
 		var y := float(lane) * 800.0
-		_mk_wall(Vector2(WALL_X, y + 5.0), Vector2(4, 10), "Ew%d" % lane)
-		var b := _mk_bullet(Vector2(0, y + 14.0), Vector2(2400, 0), mode)
+		_mk_wall(Vector2(WALL_X, y + 5.0), Vector2(4, 10))
+		var b := _mk_bullet(Vector2(0, y + 14.0), Vector2(2400, 0), CCD[mk])
 		var tag := lane
 		b.body_entered.connect(func(_n: Node) -> void: hits[tag] = hits.get(tag, 0) + 1)
 		bodies.append(b)
-		keys.append(mk)
 		hits[tag] = 0
-	for i in 30:
-		await physics_frame
-		_frame_no += 1
+	await _frames(30)
 	for i in bodies.size():
-		var mk: String = keys[i]
+		var mk: String = ["d", "r", "s"][i]
 		var b: RigidBody2D = bodies[i]
 		out.append("%s_cross=%d %s_hit=%d %s_pos=%s" % [mk,
 			1 if b.global_position.x > WALL_X + WALL_HALF else 0, mk, hits.get(i + 1, 0), mk,
@@ -386,7 +309,7 @@
 		_fv(r.get_collider_velocity()), (coll as Object).get_class() if coll != null else "null"]
 
 func _arm_btm_from() -> void:
-	_mk_wall(Vector2(200, 0), Vector2(4, 400), "WF")
+	_mk_wall(Vector2(200, 0), Vector2(4, 400))
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	b.global_position = Vector2(0, 1000)  # kinematic node write: lands next step
@@ -401,7 +324,7 @@
 		_res_line(r1, h1), _res_line(r2, h2), _fv(b.global_position)])
 
 func _arm_btm_hit() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "WH")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	var r := PhysicsTestMotionResult2D.new()
@@ -410,32 +333,24 @@
 	_finish("btm_hit %s bodypos=%s" % [_res_line(r, h), _fv(b.global_position)])
 
 func _arm_btm_embed() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "WE")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	var b := _mk_char(Vector2(96, 0))  # circle r10: face 98 -> 8px embedded
 	await _frames(2)
-	var r1 := PhysicsTestMotionResult2D.new()
-	var p1 := _mk_test_params(Vector2(50, 0), 0.0, b.global_transform, false)
-	var h1: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p1, r1)
-	var r2 := PhysicsTestMotionResult2D.new()
-	var p2 := _mk_test_params(Vector2(50, 0), 0.0, b.global_transform, true)
-	var h2: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p2, r2)
-	var r3 := PhysicsTestMotionResult2D.new()
-	var p3 := _mk_test_params(Vector2(50, 0), 0.0, b.global_transform, true)
-	p3.collide_separation_ray = true
-	var h3: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p3, r3)
-	# away-motion: separates the recovery-report flag from the motion-hit flag
-	var r4 := PhysicsTestMotionResult2D.new()
-	var p4 := _mk_test_params(Vector2(-50, 0), 0.0, b.global_transform, false)
-	var h4: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p4, r4)
-	var r5 := PhysicsTestMotionResult2D.new()
-	var p5 := _mk_test_params(Vector2(-50, 0), 0.0, b.global_transform, true)
-	var h5: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p5, r5)
-	_finish("btm_embed rec_off[%s] rec_on[%s] rec_on_sepray[%s] away_off[%s] away_on[%s]" % [
-		_res_line(r1, h1), _res_line(r2, h2), _res_line(r3, h3),
-		_res_line(r4, h4), _res_line(r5, h5)])
+	# away-motion rows separate the recovery-report flag from the motion-hit flag
+	var out: Array = []
+	for spec in [["rec_off", 50.0, false, false], ["rec_on", 50.0, true, false],
+			["rec_on_sepray", 50.0, true, true],
+			["away_off", -50.0, false, false], ["away_on", -50.0, true, false]]:
+		var r := PhysicsTestMotionResult2D.new()
+		var p := _mk_test_params(Vector2(spec[1], 0), 0.0, b.global_transform, spec[2])
+		if spec[3]:
+			p.collide_separation_ray = true
+		var h: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p, r)
+		out.append("%s[%s]" % [spec[0], _res_line(r, h)])
+	_finish("btm_embed %s" % [" ".join(out)])
 
 func _arm_btm_margin() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "WM")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	var out: Array = []
@@ -452,9 +367,9 @@
 	# stale one-flush-behind pose, (c) Transform2D() identity. Walls at y=0 and
 	# y=3000; bodies at y=3000 (node init, no write), y=3600 (no wall) and a
 	# server-tier teleported body at y=4200 (wall C there).
-	_mk_wall(Vector2(200, 0), Vector2(4, 400), "FB")    # lane B: y in [-200,200]
-	_mk_wall(Vector2(200, 3000), Vector2(4, 400), "FA") # lane A: y in [2800,3200]
-	_mk_wall(Vector2(200, 4200), Vector2(4, 400), "FC") # lane C: y in [4000,4400]
+	_mk_wall(Vector2(200, 0), Vector2(4, 400))    # lane B: y in [-200,200]
+	_mk_wall(Vector2(200, 3000), Vector2(4, 400)) # lane A: y in [2800,3200]
+	_mk_wall(Vector2(200, 4200), Vector2(4, 400)) # lane C: y in [4000,4400]
 	var b1 := _mk_char(Vector2(0, 3000))  # node-init, no writes
 	var b2 := _mk_char(Vector2(0, 3600))  # node-init, empty lane
 	var b3 := _mk_char(Vector2(0, 0))
@@ -478,7 +393,7 @@
 	# embedded start + ZERO motion isolates the recovery report from any
 	# motion-phase hit. rec_off=hit would mean recovery is always reported;
 	# rec_on-only hit means the flag gates the recovery report.
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "RF")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	var b := _mk_char(Vector2(96, 0))  # embedded 8px in wall face 98
 	await _frames(2)
 	var out: Array = []
@@ -500,21 +415,21 @@
 		_fv(c.get_collider_velocity()), (coll as Object).get_class() if coll != null else "null"]
 
 func _arm_mac_hit() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "WMC")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	var c := b.move_and_collide(Vector2(200, 0))
 	_finish("mac_hit %s bodypos=%s" % [_kc_line(c), _fv(b.global_position)])
 
 func _arm_mac_miss() -> void:
-	_mk_wall(Vector2(WALL_X, 500), Vector2(4, 400), "WMM")
+	_mk_wall(Vector2(WALL_X, 500), Vector2(4, 400))
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	var c := b.move_and_collide(Vector2(60, 0))
 	_finish("mac_miss col=%s bodypos=%s" % ["null" if c == null else "nonnull", _fv(b.global_position)])
 
 func _arm_tm_hit() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "WTM")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	var c := KinematicCollision2D.new()
@@ -522,7 +437,7 @@
 	_finish("tm_hit ret=%s %s bodypos=%s" % [h, _kc_line(c), _fv(b.global_position)])
 
 func _arm_mac_test_only() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "WTO")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	var c := b.move_and_collide(Vector2(200, 0), true)
@@ -534,16 +449,16 @@
 		"null" if c2 == null else "hit", _fv(b.global_position)])
 
 func _arm_mac_nodecomp() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "WA")
-	_mk_wall(Vector2(50, -110), Vector2(400, 4), "WB")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
+	_mk_wall(Vector2(50, -110), Vector2(400, 4))
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	var c := b.move_and_collide(Vector2(200, -200))
 	_finish("mac_nodecomp %s bodypos=%s" % [_kc_line(c), _fv(b.global_position)])
 
 func _arm_mac_chain() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "CA")
-	_mk_wall(Vector2(50, -110), Vector2(400, 4), "CB")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
+	_mk_wall(Vector2(50, -110), Vector2(400, 4))
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	var motion := Vector2(200, -200)
@@ -558,7 +473,7 @@
 	_finish("mac_chain %s" % [" ".join(hops)])
 
 func _arm_mac_maxcol() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "W5")
+	# no wall: the 5-arg callv refuses on arity before any query runs.
 	var b := _mk_char(Vector2(0, 0))
 	await _frames(2)
 	# max_collisions 5th positional arg: absent from this build's ClassDB sig
@@ -571,30 +486,12 @@
 	# move_and_collide at all and does the write persist through the sync?
 	# Pair 2: hit lane (wall in the body's lane) — does it stop like the
 	# CharacterBody2D and does the server keep the stopped pose?
-	_mk_wall(Vector2(WALL_X, 500), Vector2(4, 400), "WR")
-	_mk_wall(Vector2(WALL_X, 900), Vector2(4, 400), "WRH")
-	var b := RigidBody2D.new()
-	b.name = "R"
-	var cs := CollisionShape2D.new()
+	_mk_wall(Vector2(WALL_X, 500), Vector2(4, 400))
+	_mk_wall(Vector2(WALL_X, 900), Vector2(4, 400))
 	var sh := CircleShape2D.new()
 	sh.radius = 10.0
-	cs.shape = sh
-	b.add_child(cs)
-	b.position = Vector2(0, 0)
-	b.gravity_scale = 0.0
-	root.add_child(b)
-	var h := RigidBody2D.new()
-	h.name = "RH"
-	var cs2 := CollisionShape2D.new()
-	var sh2 := CircleShape2D.new()
-	sh2.radius = 10.0
-	cs2.shape = sh2
-	h.add_child(cs2)
-	h.position = Vector2(0, 900)  # in WRH's lane: motion (200,0) reaches the wall
-	h.gravity_scale = 0.0
-	root.add_child(h)
-	_tracked_nodes.append(b)
-	_tracked_nodes.append(h)
+	var b := _mk_rigid(Vector2(0, 0), sh)
+	var h := _mk_rigid(Vector2(0, 900), sh)  # in the y900 wall lane: motion (200,0) reaches it
 	await _frames(2)
 	var c := b.move_and_collide(Vector2(60, 0))
 	var pos_now := b.global_position
@@ -610,20 +507,19 @@
 		"null" if ch == null else _kc_line(ch), _fv(hpos_now), _fv(hpos_late), _fv(hsrv.origin)])
 
 func _arm_mac_embed() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "WEM")
-	_mk_wall(Vector2(WALL_X, 600), Vector2(4, 400), "WEM2")
-	_mk_wall(Vector2(WALL_X, 1200), Vector2(4, 400), "WEM3")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
+	_mk_wall(Vector2(WALL_X, 600), Vector2(4, 400))
+	_mk_wall(Vector2(WALL_X, 1200), Vector2(4, 400))
 	var b := _mk_char(Vector2(96, 0))  # embedded 8px
 	var b2 := _mk_char(Vector2(96, 600))
 	var b3 := _mk_char(Vector2(96, 1200))
 	b3.safe_margin = 5.0  # body property vs the 0.08 arg default
 	await _frames(2)
 	var c1 := b.move_and_collide(Vector2(50, 0), false, 0.08, false)
-	var pos1 := b.global_position
 	var c2 := b2.move_and_collide(Vector2(50, 0), false, 0.08, true)
 	var c3 := b3.move_and_collide(Vector2(50, 0))  # arg default margin
 	_finish("mac_embed rec_off[%s pos=%s] rec_on[%s pos=%s] prop5_argdefault[%s pos=%s]" % [
-		_kc_line(c1), _fv(pos1), _kc_line(c2), _fv(b2.global_position),
+		_kc_line(c1), _fv(b.global_position), _kc_line(c2), _fv(b2.global_position),
 		_kc_line(c3), _fv(b3.global_position)])
 
 # ------------------------------------------- Q4: direct-space query family
@@ -649,7 +545,7 @@
 		(d.get("collider") as Object).get_class() if d.get("collider") != null else "null"]
 
 func _arm_dss_motion() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "DW")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	await _frames(2)
 	var dss := _dss()
 	var circle := CircleShape2D.new()
@@ -668,7 +564,7 @@
 		cm, cm2, cm3, cs.size(), is_.size(), _rest_line(ri), _rest_line(ri3)])
 
 func _arm_dss_embed() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "DE")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	await _frames(2)
 	var dss := _dss()
 	var circle := CircleShape2D.new()
@@ -677,14 +573,14 @@
 	var cm_t := dss.cast_motion(pt)
 	var pa := _mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2(-200, 0))
 	var cm_a := dss.cast_motion(pa)
-	var cs := dss.collide_shape(_mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2(200, 0)))
-	var is_ := dss.intersect_shape(_mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2(200, 0)))
-	var ri := dss.get_rest_info(_mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2(200, 0)))
+	var cs := dss.collide_shape(pt)
+	var is_ := dss.intersect_shape(pt)
+	var ri := dss.get_rest_info(pt)
 	_finish("dss_embed cm_toward=%s cm_away=%s cs_n=%d cs_pts=%s is_n=%d ri=%s" % [
 		cm_t, cm_a, cs.size(), cs, is_.size(), _rest_line(ri)])
 
 func _arm_dss_shapes() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "DS")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	var mover := _mk_bullet(Vector2(300, 0), Vector2(120, 0), 0)
 	mover.contact_monitor = false
 	await _frames(2)
@@ -699,10 +595,12 @@
 	var ray_miss := dss.intersect_ray(rq2)
 	var circle := CircleShape2D.new()
 	circle.radius = 8.0
-	var ri := dss.get_rest_info(_mk_shape_params(circle, Transform2D(0, mover.global_position), Vector2.ZERO))
-	var is_ := dss.intersect_shape(_mk_shape_params(circle, Transform2D(0, mover.global_position), Vector2.ZERO))
-	var cs_full := dss.collide_shape(_mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2.ZERO), 32)
-	var cs_cap1 := dss.collide_shape(_mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2.ZERO), 1)
+	var qm := _mk_shape_params(circle, Transform2D(0, mover.global_position), Vector2.ZERO)
+	var ri := dss.get_rest_info(qm)
+	var is_ := dss.intersect_shape(qm)
+	var qz := _mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2.ZERO)
+	var cs_full := dss.collide_shape(qz, 32)
+	var cs_cap1 := dss.collide_shape(qz, 1)
 	_finish("dss_shapes ray_hit={keys=%s cls=%s pos=%s n=%s} ray_miss=%s ri=%s is_n=%d is0={keys=%s cls=%s} cs_full=%d cs_cap1=%d" % [
 		_sorted_keys(ray_hit), (ray_hit["collider"] as Object).get_class(), _fv(ray_hit.get("position")), _fv(ray_hit.get("normal")),
 		"{}" if ray_miss.is_empty() else "nonempty", _rest_line(ri), is_.size(),
@@ -711,7 +609,7 @@
 		cs_full.size(), cs_cap1.size()])
 
 func _arm_dss_purity() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "DP")
+	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
 	await _frames(2)
 	var dss := _dss()
 	var circle := CircleShape2D.new()
@@ -727,7 +625,7 @@
 	_finish("dss_purity equal=%s before=%s after=%s" % [before == after, before, after])
 
 func _arm_dss_wrongarg() -> void:
-	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400), "DX")
+	# no wall: every call refuses on param class/null before any query runs.
 	await _frames(2)
 	var dss := _dss()
 	var ptq := PhysicsPointQueryParameters2D.new()
@@ -747,9 +645,8 @@
 
 # ------------------------------------------------- Q5: contact materialization
 
-func _mk_faller(pos: Vector2, monitor := true, cap := 4) -> RigidBody2D:
+func _mk_faller(pos: Vector2, cap := 4) -> RigidBody2D:
 	var b := RigidBody2D.new()
-	b.name = "F"
 	var cs := CollisionShape2D.new()
 	var rs := RectangleShape2D.new()
 	rs.size = Vector2(10, 10)
@@ -758,13 +655,12 @@
 	b.position = pos
 	b.gravity_scale = 4.0
 	root.add_child(b)
-	b.contact_monitor = monitor
+	b.contact_monitor = true
 	b.max_contacts_reported = cap
-	_tracked_nodes.append(b)
 	return b
 
 func _arm_cont_windows() -> void:
-	_mk_wall(Vector2(0, 20), Vector2(200, 20), "Fl")
+	_mk_wall(Vector2(0, 20), Vector2(200, 20))
 	var b := _mk_faller(Vector2(0, -4))
 	var reads := {}
 	b.body_entered.connect(func(_n: Node) -> void:
@@ -797,12 +693,12 @@
 func _arm_cont_cap() -> void:
 	# corner wedge, two identical fallers: A capped at 1, B uncapped (4).
 	# The delta between them is the truncation witness.
-	_mk_wall(Vector2(0, 20), Vector2(200, 20), "CF")
-	_mk_wall(Vector2(17, 0), Vector2(20, 200), "CW")
-	_mk_wall(Vector2(400, 20), Vector2(200, 20), "DF")
-	_mk_wall(Vector2(417, 0), Vector2(20, 200), "DW")
-	var a := _mk_faller(Vector2(4, -4), true, 1)
-	var b2 := _mk_faller(Vector2(404, -4), true, 4)
+	_mk_wall(Vector2(0, 20), Vector2(200, 20))
+	_mk_wall(Vector2(17, 0), Vector2(20, 200))
+	_mk_wall(Vector2(400, 20), Vector2(200, 20))
+	_mk_wall(Vector2(417, 0), Vector2(20, 200))
+	var a := _mk_faller(Vector2(4, -4), 1)
+	var b2 := _mk_faller(Vector2(404, -4), 4)
 	var entered := {"a": false, "b": false}
 	a.body_entered.connect(func(_n: Node) -> void: entered["a"] = true)
 	b2.body_entered.connect(func(_n: Node) -> void: entered["b"] = true)
@@ -820,9 +716,8 @@
 		(arr_b[1] as Object).get_class() if arr_b.size() > 1 else "none"])
 
 func _arm_bds_windows() -> void:
-	_mk_wall(Vector2(0, 20), Vector2(200, 20), "BF")
+	_mk_wall(Vector2(0, 20), Vector2(200, 20))
 	var b := IntegBody.new()
-	b.name = "IB"
 	var cs := CollisionShape2D.new()
 	var rs := RectangleShape2D.new()
 	rs.size = Vector2(10, 10)
@@ -833,11 +728,11 @@
 	b.contact_monitor = true
 	b.max_contacts_reported = 4
 	root.add_child(b)
-	_tracked_nodes.append(b)
+	var cb_reads := {}
 	b.body_entered.connect(func(_n: Node) -> void:
 		_entries.append(_frame_no)
 		var st: Variant = PhysicsServer2D.body_get_direct_state(b.get_rid())
-		_cb_reads["in_cb"] = {"obj": st != null,
+		cb_reads["in_cb"] = {"obj": st != null,
 			"count": (st as PhysicsDirectBodyState2D).get_contact_count() if st != null else -1})
 	var st0: Variant = PhysicsServer2D.body_get_direct_state(b.get_rid())
 	var out0 := "null" if st0 == null else "obj"
@@ -856,10 +751,10 @@
 	var integ: Variant = b.seen.get("step0", {})
 	var last_integ: Variant = b.seen.get("step%d" % b.stamp, {})
 	_finish("bds_windows oop=%s cnt=%d in_cb=%s in_phase=%s cnt=%d proc=%s cnt=%d integ_first=%s integ_last=%s" % [
-		out0, cnt0, _cb_reads.get("in_cb"), out1, cnt1, out2, cnt2, integ, last_integ])
+		out0, cnt0, cb_reads.get("in_cb"), out1, cnt1, out2, cnt2, integ, last_integ])
 
 func _arm_cont_persist() -> void:
-	_mk_wall(Vector2(0, 20), Vector2(200, 20), "PF")
+	_mk_wall(Vector2(0, 20), Vector2(200, 20))
 	var b := _mk_faller(Vector2(0, -4))
 	b.body_entered.connect(func(_n: Node) -> void: _entries.append(_frame_no))
 	b.body_exited.connect(func(_n: Node) -> void: _exits.append(_frame_no))
```

## 5. Tradeoffs

- **Backtrace line numbers** moved in the two dead-wall arms (K13) — declared
  volatile by the repo differ; all verdict-relevant fields identical.
- **`_finish` teardown removal (K2)** relies on process-exit freeing; valid for
  this fixture's one-arm-per-process shape, verified by zero leak/ObjectDB
  lines across 139 rows.
- **Node names (K3)** were debugging labels nothing reads; section comments and
  scout doc carry the documentation duty now.
- Net: 879→774 lines (−12%), one construction convention (`_mk_rigid`), one
  CCD-mode table (`const CCD`), one test-loop convention (`for spec in …`),
  zero verdict or PASS-line drift.
