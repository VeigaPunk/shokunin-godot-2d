# r81 fold — critic C1–C11 + boundary B1–B11 + simplifier vfold

## What landed
- `phys2d_joints.gd`: simplifier vfold applied (973→919 base, +41 witness lines → 960): factory `nm`-param cleanup, `_probe_joint_getters`/`_run_wall_table` dedup, dead keys/locals, doc fold. Proven 20/20 byte-exact pre-witness.
- Critic witness corrections (10 rows repinned):
  - **C1** `joint_pin_tiers`: same-position control `pin2` at (2000, LANE) — `n2_dist=200.2708 ≡ s_dist` kills the "node vs server" claim; divergence is the 2000 px y-translation (boundary B11 corroborates the y-gradient). Claim corrected: node and server pins are bit-identical at equal position.
  - **C2** `_run_wall_table`: `[wl= wm= bl= bm=]` now emitted from `w.collision_*`/`b.collision_*` readbacks, not spec echoes (values unchanged → pins unchanged, but layer forges now fail).
  - **C3** `joint_node_clear`: `nudge_pos=(0.0000,100.0000)` readback — nudge deletion now diverges.
  - **C4** `joint_node_anchor`: `p2_pos=(0.0000,2100.0000)` readback — pre-step move witnessed.
  - **C5** `area_entry_order`: `created1=["o","i","b"]`/`created2=["b","o","i"]` tokens — creation-order collapse now diverges.
  - **C6** `layer_flip_mid`: `m_pre`/`wl_pre` per lane — pre-flip state witnessed.
  - **C7** `joint_groove`: `j3_type=1` — never-connected gst_srv_jpos forge now reads type 3.
  - **C8** `joint_freed_rid`/`joint_node_freed_rid`: `bias_remade=-1.0000` + `type_again=0` — caught that the freed-RID re-make is silently REFUSED (type reads 0 colliding with JOINT_TYPE_PIN, param ops still return the -1.0 sentinel). The pin now records the measured fact, not the assumed re-make.
  - **C9** `area_lattice`/`area_body_gate`: `am/amab/bm/bmab` monitoring+monitorable readbacks — creation-time monitoring writes witnessed.
- **C10** (boundary): self-report clauses bounded in the report records, not rows.
- **C11**: confirmed caught (typed setter refusal) — no change.

## Boundary classes folded into the record (report-level, future-arm material)
B1 NULLB-ABORT (joint_make_pin body_b=RID() → SIGSEGV first step; no landed cell affected), B2 AREA-CB-GATE (Area2D.monitoring IS refused in-callback — layer_flip_cb's "not gated" is surface-specific), B3–B7 nonfinite/denorm classes, B8 self-joint inert, B9 freed joint RID never recycled in 64 allocs (strengthens freed pins), B10 warn-anchor interleave flake class, B11 y-gradient corroborates C1.

## Verification
- Full battery on folded bytes: **159/159 PASS** (`corpus/live/r81-fold-verify3/20261015T082450247950Z/verdicts.json`).
- Prior-139 rows: untouched (fold is inside the r81 block only).
- Forge-kill: n2 control makes the tier forge impossible; layer readbacks make spec-echo forges fail; monitoring readbacks kill deferred-mon forges.
- Scribe F3 recorded: unattributed stash-family op at 06:50Z (identical bytes, rate-limit window) — benign, recorded.
