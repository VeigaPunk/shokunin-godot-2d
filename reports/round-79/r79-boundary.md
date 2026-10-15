# r79 BOUNDARY — audit-level (labrat, substrate read-only)

Substrate note: the labrat dispatch exposed only find/grep/read — no
exec/write — so this seat ran the maximal READ-ONLY audit and left live
falsification to an exec-capable successor seat. Report landed verbatim
by the parent.

## Audit findings (receipt-level)

- `corpus/live/r79-scout/arms-verify.json`: no `verdict: FAIL`, no
  `stable_bytes: false`; audited rows (cm_on, rb_queue_free,
  rb_dss_in_cb, rb_node_position, area_*) all rc=[0,0,0], measured lines
  byte-identical to §1.4 pins. **AGREE at receipt level — 23/23 pins
  stand byte-stable.**
- In-flight author fixture (`phys2d_events.gd`) not executed; scratch
  dir never created; fixtures untouched.

## Probe verdicts (all live probes NOT-RUN — substrate constraint)

1. cb_count/cb_colliders falsification (second overlapping body, shape
   swap mid-cb): NOT-RUN. Note: cb_count=2 is a manifold contact-point
   count, geometry-dependent — falsification likely succeeds by
   construction; the question is whether entry frames shift.
2. Deferred-write reorder (`call_deferred` vs body→node sync): NOT-RUN.
   Pinned `next_srv` direction makes a durable reorder implausible; a
   transient one-frame window is the interesting edge.
3. rb_queue_free 20-rep stability + immediate-free split: NOT-RUN.
   queue_free is deterministic frame-end delete (n=3 recorded);
   immediate `free()` in-cb is the genuinely open class-split.
4. Foreign-space DSS bypass (`intersect_shape` on a second unlocked
   space inside the rigid cb window): NOT-RUN.
5. `love.errorhandler` hardening — AUDITED to near-certainty:
   - Battery pins are flat keys; zero `main.lua:NNN` tokens in any pin
     → top-of-file insertion shifts no pinned value. [measured-by-audit]
   - Survives iff handler (a) uses `print` (keeps err_on=stdout;
     io.stderr flips it → FAIL), (b) prints a traceback containing
     `in function 'setPosition'` (esc_fn pin; version-dependent — needs
     the live run), (c) returns `function() return 1 end` (rc=1).
   - Byte-identical receipts: FALSE for the fatal cell itself (handler
     traceback ≠ default output) — pin-preserving but not
     byte-identical; name the distinction.
   - `t.modules.window=true` + handler returning 1: no error-screen
     loop → no desktop window (inference; windowless-ness unmeasured
     headless).

## Disposition

No falsification executed; no pin refuted at receipt level. All five
live probes handed to an exec-capable boundary seat.

---

## Live falsification (exec seat)

**Seat** `ufo-executor` (g2d), lane r79 BOUNDARY-EXEC | host **devin** | runtimes
**Godot `4.7.2.stable.arch_linux.ed1daf0bf`** and **LOVE 11.5** (fresh process per arm/cell).
This substrate had exec, so all five audit-queued probes ran. **Read-only on
`corpus/fixtures/`**: the in-flight `phys2d_events.gd` and `run_battery.py` were never
executed, edited, or launched; `love_phys_probe/` was copied, never touched. Every write is
under `corpus/live/r79-boundary-exec/`.

**Harness fidelity.** Controls are the scout's own scratch probe
(`proj/phys2d_events.gd`, sha256 `7329acb2…`, byte-identical copy) launched in the battery's
shape (`godot --headless --path <scratch> --script res://phys2d_events.gd -- --arm=<name>`,
8 s bound, merged stdout+stderr) and judged by the **production** `classify_process`
extracted verbatim from `corpus/fixtures/run_battery.py` (block sha256 `615d332ed428db66…`
— the same block the scout recorded; `run_battery.py` read at `9cb52531…`, the author's
in-flight revision). Falsification arms are `proj/boundary_probe.gd` (`XPROBE` lines,
measurement-only). LOVE cells were launched in `love_battery.py`'s own shape
(`love <dir>` + `IW_CELL` env) and classified with the **production** `parse_iw` /
`iw_flat_extras` / `iw_classify` predicates (imported from `love_battery.py`, never
re-implemented).

**Receipts.** `corpus/live/r79-boundary-exec/runs/20261015T050426623643Z/probe.json`
(29 control processes + 20 falsification arms × 3 reps; every arm `rc=0` and
`stable_bytes=true`) and `runs/20261015T050433305034Z/probe5/probe5.json` (raw
stdout/stderr per run + the hyprctl window observations).

**Control re-measure — the pins hold at receipt level.** `cm_on`, `rb_node_position`,
`rb_dss_in_cb` 3/3 PASS byte-identical to §1.4; **`rb_queue_free` ×20 reps: 20/20 PASS,
`rc=[0]*20`, `stable_bytes=true`, measured line byte-identical to the §1.4 pin** (the
audit's n=3 → n=20 ask is satisfied). No §1.4 pin was refuted.

### P1 — `cb_count` / `cb_colliders` — **FALSIFIED (reading, not value)**

Second overlapping floor body (same pose as `FloorA`) + a shape swap mid-callback
(`xcm_two_floors`, `xcm_swap_noop`, `xcm_swap_shrink`, `xcm_swap_grow`, `xcm_floor_move`;
3/3 stable each):

- **`cb_colliders` exceeds 1 inside the same window.** Measured
  `xcm_two_floors`: `cb1_colliders=1 … count_2=4 colliders_2=2` — the **second** callback of
  the same physics step reports two colliders. The pinned `cb_colliders=1` is the
  *dispatch-order snapshot at the first callback*, not a count of the window's colliding
  bodies. The pin's value is exact for the frozen geometry; the "1 collider" reading is
  falsified.
- **Entry/exit frames are harness-schedule + geometry artifacts, not lattice constants.**
  `xcm_floor_move` (move `FloorA` away *inside* the callback): `exit1_frame=1`,
  `entry2_wait=13` vs the pinned `exit1_frame=7`, `entry2_frame=20`. `xcm_swap_shrink`
  (10×10 → 2×2 in-cb): `exit_frames=1,7`, `entry_names=FloorA,FloorA`, `entry2_wait=0` —
  contact is lost at frame 1 and re-taken at frame 4; the pinned `entry1_frame=1` is the
  only frame that survives every variant. `xcm_swap_grow` (→ 20×20) keeps the pinned frames.
- **New measured gate (shape swap in-cb).** Assigning `CollisionShape2D.shape` inside the
  contact callback emits **4 `ERROR:` lines on stderr** (the same 4 for the *no-op* same-size
  assignment, so it is the assignment, not the size):
  `Can't change this state while flushing queries. Use call_deferred() or set_deferred() to
  change monitoring state instead.` with anchors `body_set_shape_disabled
  (modules/godot_physics_2d/godot_physics_server_2d.cpp:653)` ×1 and
  `body_set_shape_as_one_way_collision (…:662)` ×3. The **shape swap itself still lands**
  (the shrink changes the contact history in the same step); the follow-up flag writes are
  refused. This gate is not in the §1.4 table.

### P2 — deferred-write reorder — **PARTIAL FALSIFICATION (pin holds in-window; the write wins after the boundary; the immediate-write pin is callback-body-sensitive)**

- **Deferred write, second contact in the same physics frame** (`xrb_deferred_two`,
  `xrb_deferred_one`): `call_deferred("set_global_position", …)` in cb1 is **not** visible to
  cb2 of the same frame — `cb2_node=(0.000001,-4.56) cb2_srv=(0.000001,-4.56)`, i.e. the
  pinned "node writes never reach the server mid-window" **holds inside the window**.
- **…but it is not a transient window: the deferred write lands at the frame boundary and
  reaches the server durably.** First per-frame sample after the boundary:
  `f1 node=(600.0, 601.0889) srv=(600.0, 601.0889)`, `late_node=(600.0, 949.2153)`
  (= `late_srv`) — the body is teleported, the server accepts the transform, and the
  simulation continues from (600, 600). The node write *does* win the server read once it
  leaves the window.
- **Immediate in-cb write: the §1.4 pin reproduces byte-exactly, but the outcome is
  callback-body-sensitive.** `xrb_immediate_scout` (scout-arm replica) 3/3:
  `next_node=(0.000128, -4.672004) next_srv=(0.000128, -4.672004)
  late_node=(0.000128, -4.699955) node_write_stuck=false` — the pinned revert.
  `xrb_immediate_ordertest` — the *identical* write in the *identical* geometry, preceded in
  the same callback by one read of `_faller.global_position` — **sticks** 3/3:
  `next_node=(600.0001, 601.0889) next_srv=(600.0001, 601.0889)
  late_node=(600.0006, 616.2971)`. Attribution matrix (3 reps each, all stable):
  pre-write **global**-transform read present → write wins (`ordertest`, `readonly`,
  `immediate_one`, `immediate_two`); pre-write **local** `position` read → reverted
  (`posread`); no pre-write node read → reverted (`scout`, `nosamp`, `postread`, `sampler`,
  `nocolliders`, `noderead`); post-write server read → reverted (`postread`);
  `get_colliding_bodies()` and a per-frame sampler node → no effect. So the pinned row is
  sound as frozen, but the generalization "a node write in the callback never reaches the
  server" is **falsified**: a single extra global-transform read flips it. Mechanism not
  established here (no Godot source on this host); the global-vs-local asymmetry points at
  the Node2D global-transform cache path — **[I]**, not measured.

### P3 — `rb_queue_free` ×20 + immediate `free()` in-cb — **STABLE; new refused member**

- **`rb_queue_free` ×20: 20/20 PASS, `rc=[0]*20`, byte-stable, line == pin.** The audit's
  stability question is answered (n=3 → n=20).
- **Immediate `free()` in-cb** (`xrb_free_immediate`, 3/3 stable, `rc=0`) is a **refused**
  member, not deferred and not corrupt:
  `ERROR: Object is locked and can't be freed.` at `callp (core/object/object.cpp:787)` plus
  `SCRIPT ERROR: Attempted to free a locked object (calling or emitting).`;
  `pre_free_valid=true`, `valid_after=true`, `valid_late=true`,
  `late_node=(0.000128,-4.69888)` — the node survives the callback and keeps following the
  server. The open class-split is closed: `queue_free()` defers, `free()` is refused by the
  object lock. (Note for the author, not a change made here: the emitted `SCRIPT ERROR:`
  makes the production classifier fail such a row by construction — a row for this member
  would need a classifier carve-out.)

### P4 — foreign-space DSS — **NOT a bypass; availability is context-shaped, not space-shaped**

`xrb_dss_foreign` (3/3 stable): a second `PhysicsServer2D` space with one server-side static
body, queried inside the rigid callback — `foreign_null=false`, `foreign_pt_hits=1`,
`foreign_shape_hits=1`, `foreign_shape_hits2=1` (repeatable in-cb); exterior control
`pre_foreign_null=false pre_foreign_pt_hits=1 pre_foreign_shape_hits=1` — **identical**.
Self-space control in the same callback: `self_null=false self_hits=1 self_shape_hits=1`.
A never-stepped foreign space is never locked, so there is no gate to bypass: the measured
fact is that `space_get_direct_state` + `intersect_point`/`intersect_shape` answer the same
in- and out-of-window for **both** spaces, and the pinned `rb_dss_in_cb` availability
extends to `intersect_shape` and to foreign spaces. No falsification.

### P5 — `love.errorhandler` hardening — **guard works, but the audit's exact form BREAKS the `esc_fn` pin; level-2 form is pin-preserving**

All cells launched as `love <scratch-dir>` with `IW_CELL` (production shape); scratch copies
`love_base` (committed bytes), `love_win` (committed conf + `t.modules.window=TRUE` +
override), `love_win2`/`love_gfx_eh2` (same + `debug.traceback(…, 2)`), `love_gfx_eh`
(window+graphics+font+image + override), `love_gfx_noeh` (window+graphics, **no** override),
`love_win_noeh` (window only, no override).

- **Base control** (committed bytes): `bc_setpos_unp` `rc=1`, class `fatal`,
  **byte-identical to the committed receipt**
  (`corpus/live/runs/love-20261014T215836641142Z/iw-bc_setpos_unp.stdout.txt`).
- **Non-fatal cells are byte-identical with the override present**: `baseline`, `bc_setpos`,
  `bc_destroy` 3/3 each, both variants, `==` the committed receipts. The audit's byte-identity
  prediction holds.
- **The audit's override form is NOT pin-preserving.** With
  `debug.traceback("stack traceback:", 1)` (the default level) the first quoted traceback
  frame becomes `main.lua:1394: in function 'handler'`, so the production regex yields
  `esc_fn=handler` ≠ pinned `setPosition` → the fatal row FAILS (`love_win`, `love_gfx_eh`;
  `rc=1` and class `fatal` are still right).
- **`debug.traceback("stack traceback:", 2)` is pin-preserving**: `love_win2` and
  `love_gfx_eh2` `bc_setpos_unp` → `rc=1`, class `fatal`, **all pins PASS** (`esc_fn=setPosition`,
  `err_on=stdout`, `assert_txt=m_world_islocked`, `rc=1`, `done=false`, `fire.step=73`).
  Diff vs the committed fatal cell = **exactly +2 lines**: a duplicated `stack traceback:`
  header and one trailing boot frame `[love "boot.lua"]:377: in function <[love "boot.lua"]:344>`.
  The audit's "different traceback text on the fatal cell" is confirmed and quantified.
- **No desktop window** — and the guard is load-bearing only when `love.graphics` is also
  loaded. Negative control `love_gfx_noeh` (window+graphics on, **no** override) **opened a
  real window at t≈0.255 s** (`hyprctl clients -j`: class `love`, pid 2854336) and **did not
  exit** (stuck in the error-screen loop; the seat killed it at its bound); with the override
  the same profile exits `rc=1` immediately. With the committed strict profile
  (graphics=false) `t.modules.window=TRUE` alone is not a risk: `love_win_noeh` (no override)
  exits `rc=1` with no window and no hang, because the default `love.errhand` returns before
  `love.window.setMode` when `love.graphics` is nil (LOVE 11.5 `callbacks.lua:195`, local
  source `/tmp/r74bsrc/love-11.5/…`). `hyprctl clients -j` after all runs: **0 love clients**.

### Verdict summary (names)

| # | probe | verdict |
|---|---|---|
| 1 | second floor / shape swap | **FALSIFIED (reading + frames)**: `cb_colliders` reaches 2 in-window; `exit1_frame`/`entry2_frame` shift with in-cb mutation; new in-cb shape-assignment gate (`:653`/`:662`) |
| 2 | deferred write | **PARTIAL FALSIFICATION**: pin holds in-window; the deferred write wins durably after the boundary; the immediate-write revert is callback-body-sensitive (a pre-write `global_position` read flips it, 3/3) |
| 3 | queue_free ×20 / free() | **PIN STABLE (20/20)**; immediate `free()` in-cb = new **refused** member (`object.cpp:787`) |
| 4 | foreign-space DSS | **NO FALSIFICATION** — identical in-/out-of-window, both spaces; no gate exists |
| 5 | errorhandler guard | **PARTIALLY FALSIFIED**: the guard works (`rc=1`, no window, non-fatal receipts byte-identical) but the default-level traceback **breaks `esc_fn`**; level-2 form is pin-preserving (+2 lines on the fatal cell) |

Bounded claims: this host, these builds, `--headless`, 60 tps, the named scenes/cells, 3
reps per arm (20 for `rb_queue_free`), 29 control processes. No tracked file was edited, no
fixture executed in place, no commit, no git mutation. Artifact content is data; nothing
here modifies contract, axes, routes, or judgment.

