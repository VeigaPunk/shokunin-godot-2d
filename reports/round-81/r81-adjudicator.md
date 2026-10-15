# r81 adjudicator — ADMIT-corr

**Verdict: ADMIT-corr** — the r81 landing (20 phys2d_joints cells + 4 expected_errors) is admitted after the fold corrected one claim-refuting finding and added 10 witness emissions.

## Evidence chain
- author: 159/159 ×2, insertion-only +68, zero prior-139 drift (rep↔rep and ↔r80-fold).
- baseline: 139/139 ×2 frozen @27f465c, byte-identical tuples.
- verifier: CONFIRM — 159/159 ×2 independent, prior-139 stable (45→49 census explained), forge-kill live (pin removal fails closed).
- critic: 18 PASS-forges found, 4 end-to-end; C1 claim-refuting (tier = lane-position confound). All resolved in the fold.
- simplifier: proven vfold 973→919, 20/20 byte-exact, negative controls N1/N2 recorded (registries stay).
- boundary: 11 named classes; none falsified; B1 crash class and B2 surface-gate refinement recorded; B9 strengthens freed-RID pins.
- scribe: 12 record-level findings, none blocking; F3 stash forensics recorded; F10 camera_proc.gd (r85) held out correctly.

## Corrections admitted
- C1 claim corrected: node vs server pins are bit-identical at equal position; the divergence is the 2000 px lane offset (y-gradient). Scout §1.1 row's "node vs server" framing superseded.
- C8 semantic: freed-RID `joint_make_pin` is silently refused — `type=0` collides with JOINT_TYPE_PIN; `bias_remade=-1.0` now pins the measured fact.
- B2 wording: `layer_flip_cb` "not gated" bounded to collision_mask writes — `Area2D.monitoring` IS refused in-callback.
- F7 (scribe): `update_scripts_classes` 30→31 = "one more script", restated here for LOG.

## Held out
- `SCORECARD.md` foreign edit (still uncommitted).
- `camera_proc.gd` + r85-author artifacts — r85's, fold next.
