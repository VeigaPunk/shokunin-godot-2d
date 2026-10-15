# game-dev-2d round 85 — critic (g2d): the camera/canvas transform lattice under mechanism-blind forges

Seat `CRITIC` (LEAF) | lane `g2d` | round 85 | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7. Repo
`~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`45232c7`** (*r85: camera/canvas transform
lattice — 15 cells*). **No git mutation, no commit, no tracked file read-modified** — writes are
this report and `corpus/live/r85-critic/**` only. The tracked fixture was never edited: every
forge is a copy in scratch (`corpus/live/r85-critic/forges/*.gd` + `.diff`).

**Attacked bytes (hash-bound).** Fixture `corpus/fixtures/camera_proc.gd` sha256
`34f53f32c0fbb37da86f91ec7b7d9fc0e7d20d9f3e29c4c9680f05e36f123c40` (1156 `wc -l` lines; the
author/fold “1157 lines” counts the trailing newline split); battery `corpus/fixtures/run_battery.py`
sha256 `1abc9629448f299bb222b200…`, r85 `CASES` rows `:274–:303`, `classify_process`
`:370–:387` (the signature clause is `signature in output`, `:386`). Both hashes equal the
author/fold report values where claimed. `lsp`: none exposed on this host (unchanged); every
carrier below is a fresh-process receipt.

**Method (mechanism-blind).** Each forge is a minimal edit of a *copy* of the landed fixture,
run in the battery's exact launch shape
(`godot --headless --path corpus/live/r85-critic/proj --script res://camera_proc.gd -- --arm=<name>`,
8 s bound, merged stdout+stderr) and judged by the **production** `classify_process` extracted
verbatim from the tracked battery (sha256 `615d332ed428db66a03b6837d7a6ed86c4a3150609dc9c2838a11a51b50bbea3`,
the same extraction r79–r84 used). Because the harness clause is a *substring* test, every
result below is additionally checked for **byte-equality of the emitted `PASS` line against the
pinned literal** — a strictly stronger test than the classifier's. Each forge was re-run to ×3
where it matters; the emitted line was byte-stable across every rep.

**Volume:** 29 forge variants + 15 pristine controls + 5 `diag_*` runs + **3 full forged
174-row batteries** (522 rows) ≈ **600 fresh Godot processes**, all sequential. All scratch
under `corpus/live/r85-critic/` (`runs/*/forge-results.json`, `battery-runs/*/*/verdicts.json`,
`checks/*/checks.json`, `summary.json`).

| result class | count | meaning |
|---|---|---|
| forge PASS, pinned line **byte-equal** | **13** | counterexamples: the pin survives deletion of the mechanism |
| recitation forge (harness bound) | 1 | `cl_draworder_recite` — accepted, documented tradeoff (C8) |
| diagnostic arm (`%.9f` receipt) | 1 | `cam_zoom_center_sub60_9dp` — C7's measured deviation |
| byte-equal but caught by the ERROR clause | 1 | `cl_stack_layers_orphan` (C3) |
| pinned line differs only by a signed zero / identity fallback, also ERROR-caught | 1 | `cam_space_orphan_layer` (C3) |
| forge FAIL, pin held | 12 | negative controls: the stimulus is load-bearing |
| pristine fixture, 15/15 arms | 15 | judge-fidelity anchor (all byte-equal) |
| **full tracked 174-row battery on a forged fixture** | **3 × 174/174 PASS** | end-to-end counterexamples: `cl_draworder_hidden_orphan`, `vp_render_indep_no_v2_no_cl`, `par_2d_no_repeat_follow` |

---

## C1 — `cl_draworder`: `hidden_draws=0` is non-injective in two independent ways  **[witness gap + claim bounding]**

**Claim attacked** (scout §1.2 row 9, `r85-scout.md:124`): “**`hidden_draws=0`** — a
`CanvasLayer.visible=false` child never `_draw`s at all.”

**Forge 1 — the hidden layer never enters the tree** (`camera_proc.gd:631`, `root.add_child(hidden)` dropped):

```diff
@@ -629,5 +629,4 @@
 	hidden.layer = 3
 	hidden.visible = false
-	root.add_child(hidden)
 	_nodes.append(hidden)
 	var htag := DrawTag.new()
```

Live: **PASS, emitted line byte-equal to the pin ×3**, and the forged fixture passes the
**entire tracked battery 174/174** (`battery-runs/cl_draworder_hidden_orphan/20261015T083703028256Z/verdicts.json`).
`seq`, `counts`, `first`, `later`, `hidden_draws=0`, `creation_order=1` are all identical: an
out-of-tree `DrawTag` never draws either.

**Forge 2 — the hidden tag is never re-queued** (`:640`, `htag` dropped from `tags_list`):

```diff
-	var tags_list: Array = [rtag, htag]
+	var tags_list: Array = [rtag]
```

Live: **PASS, byte-equal ×3**. The token cannot distinguish “asked to redraw 4 times and
suppressed by `visible=false`” from “never asked”.

**Killing pin (smallest safe correction).** Add a per-tag requeue counter and pin the hidden
tag's configuration in the same line: `hidden[in=1 vis=0 requeued=4 draws=0]`
(`in := int(hidden.is_inside_tree())`, `vis := int(hidden.visible)`, and increment a
`requeues` field in the arm's `phys_hook` where `d.queue_redraw()` is already called). Forge 1
breaks on `in=0`, forge 2 on `requeued=0`. **Axes:** depth (witness thinness), calibration
(“never `_draw`s at all” is stated as a mechanism claim the row does not carry).

---

## C2 — `vp_render_indep`: two of the four lanes' canvas variation is unobserved; `eq_exact=1` is satisfied by a halted world  **[witness gap]**

**Claim attacked** (scout §1.3 row 11, `r85-scout.md:131`; author §2 row 11): “physics is
byte-independent of canvas/camera state” — with `V2` = “camera **moving and zooming every
physics frame**”, `ROOT` = “moving camera **and** a `CanvasLayer.offset` written every frame”,
and the parenthetical “`root_ct=30.8158,32` (**the canvas really was moving**)”.

**Forge — V2's camera never moves and the ROOT CanvasLayer offset is never written**
(`camera_proc.gd:754–:760`, `:776`):

```diff
@@ -755,8 +755,4 @@
 			var c2 := _mk_cam(sv, Vector2.ZERO)
 			c2.make_current()
-			var lane := _mk_lane("mv")
-			lane.phys_hook = func(l: Lane, _d: float):
-				c2.position = Vector2(float(l.phys) / 60.0, float(l.phys) / 120.0)
-				c2.zoom = Vector2(1.0 + 0.05 * float(l.phys), 1.0 + 0.05 * float(l.phys))
@@ -774,5 +770,4 @@
 		cam_root.position = Vector2(float(l.phys) / 60.0, 0.0)
 		cam_root.zoom = Vector2(1.0 + 0.05 * float(l.phys), 1.0)
-		cl.offset = Vector2(float(l.phys), 0.0)
```

Live: **PASS, byte-equal ×3**, and the forged fixture passes the **full 174/174 battery**
(`battery-runs/vp_render_indep_no_v2_no_cl/20261015T083703028151Z/verdicts.json`). The
single-edit variants (`vp_render_indep_no_v2_motion`, `vp_render_indep_no_cl_offset`) are also
byte-equal ×3. The row's only canvas readback is `root_ct` (`:791`), which is a function of the
ROOT lane's camera alone; V0/V1/V2 print only tags and physics positions, so their canvas state
is never read. The scout's “the canvas really was moving” is true of exactly one lane.

**Controls (pin held).** `vp_render_indep_freeze` (all four bodies frozen) → **FAIL** on the
`pos=[…76.3003…]` tokens — a halted world satisfies `eq_exact=1 eq_4dp=1` but not the
positions, so the *physics-ran* leg is load-bearing. Dropping the ROOT lane's position write or
its zoom write each **FAIL** (`root_ct` is a function of both) — the ROOT lane is witnessed.

**Killing pin.** Pin the per-lane canvas state that the claim quantifies over, e.g.
`ct=[32.0000,32.0000|-168.0000,-68.0000|<V2 live>|30.8158,32.0000]` from each
`sv.canvas_transform.origin` after the 30 frames (V1's literal shown), plus `cloff=%s`
(`cl.offset` readback). Forge breaks on `ct[2]` (frozen) and on `cloff=0,0`. **Axes:** depth,
calibration.

---

## C3 — CanvasLayer membership: three rows are out-of-tree-indistinguishable; two survive only on engine error noise  **[witness gap, fragile]**

**Claims attacked** (scout §1.2 rows 6–7, §1.1 row 5; `r85-scout.md:121–122`, `:115`):
“all three layers read the same `wc=100,0` regardless of `layer = -1/0/7`
(**camera-independent**)”; `F0` (follow=false) baseline `wc=100,0 fin=identity`; “a CanvasLayer
child: `final`=identity, `lwc=(300,200)` camera-independent (`l_indep=1`), `lvx` = the layer
transform (identity, **not the camera transform**)”.

**(a) `cl_stack` — layers −1 and 0 orphaned** (`:482`):

```diff
-		root.add_child(cl)
+		if lv == 7:
+			root.add_child(cl)
```

Live: **the emitted `PASS` line is byte-equal to the pin ×3** (`t1/t2/t3`, `wc7`, `expect7`,
`comp7=1`, `nested[…]` all unchanged); the classifier FAILs **only** because the out-of-tree
children's `get_viewport_transform()` calls emit two `ERROR: Condition "!is_inside_tree()" is
true. Returning: Transform2D()` lines (`:494`), which the harness's error clause rejects. The
pinned row itself does not witness that layers −1/0 exist.

**(b) `cl_follow` — the F0 layer orphaned** (`:540`): clean **PASS, byte-equal ×3** with no
error lines (the F0 row reads only `get_global_transform_with_canvas()` and
`get_final_transform()`, neither of which `ERR_FAIL`s). A layer that is not in the tree prints
the pinned row exactly:
`F0[en=0 sc=1.0 wc=100.0000,0.0000 fin=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000)]`.

**(c) `cam_space` — the layer orphaned** (`:431`): the line differs **only** by a signed zero
(`lwc=(1.0000,0.0000;0.0000,1.0000;300.0000,200.0000)` in-tree vs
`lwc=(1.0000,0.0000;-0.0000,1.0000;300.0000,200.0000)` out-of-tree) and the `ERR_FAIL` identity
fallback in `lsc`; two `ERROR:` lines also reject it. The row survives by accident of float
sign, not by a designed membership token.

**Killing pin.** One `in=%d` (`is_inside_tree()`) token per row — `in=[1|1|1]` in `cl_stack`,
`in=1` in `cl_follow`'s F0 and `cam_space`'s `cl[…]` block (or, stronger, give each layer a
distinct non-identity `offset` before the readback so the value itself is layer-relative and
cannot be produced out of tree). **Axes:** depth; the `cl_stack` case is also calibration
(a pinned token is being protected by an unrelated engine error line — if that ERROR were ever
whitelisted, the forge passes).

---

## C4 — `par_2d`: the `repeat_size` / `repeat_times` / `follow_viewport` / `screen_offset` legs are unwitnessed  **[witness gap]**

**Claim attacked** (scout §1.4 row 14, `r85-scout.md:139`): “`repeat_size=(100,0)`+`repeat_times=3`,
`follow_viewport=true` and `screen_offset=(7,3)` leave the node transform **unchanged**
(`rep100x3`, `follow`, `screen_off` rows)”.

**Forge — the four writes never happen** (`camera_proc.gd:961–:962`, `:968`, `:971`):

```diff
 	p2.ignore_camera_scroll = false
-	p2.repeat_size = Vector2(100, 0)
-	p2.repeat_times = 3
 	await _settle()
@@
-	p2.follow_viewport = true
 	await _settle()
@@
-	p2.screen_offset = Vector2(7, 3)
 	await _settle()
```

Live: **PASS, byte-equal ×3**, and the forged fixture passes the **full 174/174 battery**
(`battery-runs/par_2d_no_repeat_follow/20261015T083703027993Z/verdicts.json`). The rows print
only `off=` (`scroll_offset`, a property that is *never written* — so its readback does witness
non-writing) and `wc=`; neither is a function of the four properties, so “leave the node
transform unchanged” is a claim about a configuration the row cannot distinguish from the
default.

**Control (pin held).** `par_2d_ignore_stuck` (never reset `ignore_camera_scroll`) → **FAIL**:
the `cam150rep`/`follow`/`screen_off` rows collapse to the frozen `-16,16`. The arm is not
uniformly blind.

**Killing pin.** Read the properties back in the row: `rep=%s,%d fv=%d so=%s` from
`p2.repeat_size/repeat_times/follow_viewport/screen_offset` (additive, no re-measure of the
`wc` values needed). **Axes:** depth, calibration.

---

## C5 — `par_layer`: the root-level “mirroring/offset do nothing” rows are unwitnessed  **[witness gap]**

**Claim attacked** (scout §1.4 row 13, `r85-scout.md:138`): “the three motion properties do
nothing there [without a `ParallaxBackground`]”.

**Forge — the root-level writes and their resets never happen** (`camera_proc.gd:847`, `:853`, `:856–:857`):

```diff
-	pl.motion_mirroring = Vector2(100, 0)
@@
-	pl.motion_offset = Vector2(10, 0)
@@
-	pl.motion_mirroring = Vector2.ZERO
-	pl.motion_offset = Vector2.ZERO
```

Live: **PASS, byte-equal ×3**. The `mirror100`/`moff10` rows print `lp=0.0000,0.0000` whether or
not the properties were set, and the closing readbacks (`mm=0.0000,0.0000 mo=0.0000,0.0000`)
are reset to zero on both paths — so the mirroring/offset leg of “inert” is invisible.
`motion_scale` *is* witnessed (`ms=0.5000,0.5000` readback + the `pbgms1`/`pbgms0` lp swing).

**Killing pin.** Read the properties back **inside** the `mirror100`/`moff10` rows
(`mm=%s mo=%s`), not only at the end. **Axes:** depth.

---

## C6 — `cam_comp`: `comp==n3` is an engine identity, `probe=` is an algebraic identity; both are literal-reproducible  **[calibration + witness]**

**Claim attacked** (scout §1.1 row 1, `r85-scout.md:111`; author §2 row 1): “`n3 = canvas_transform
* global_transform` **bit-exact** (`comp == n3`, `comp=1`)”, and the row's trailing
`probe=32.0000,32.0000`.

**Forge 1 — `n3` literalised** (`camera_proc.gd:240`): `var n3 := Transform2D(Vector2(2.0,0.0), Vector2(-0.0,2.0), Vector2(412.0,292.0))`.
**Forge 2 — `comp` literalised** (`:256`). **Forge 3 — `probe` literalised** (`:260`,
`var s3_cf := _v(s3.origin + Vector2(32, 32) - s3.origin)` → `"32.0000,32.0000"`).
Live: **all three PASS, byte-equal (×3/×3/×2)**.

Two structural facts follow. `comp == n3` is true by engine construction for any in-tree
root-level node (`get_global_transform_with_canvas()` *is* `viewport.canvas_transform *
global_transform`); its only failure mode is the node leaving the tree — confirmed by the
control `cam_comp_node_orphan` → **FAIL** (`comp=0`). And `probe=` is `(o + (32,32)) − o`, an
identity on the live origin that can never report anything but `32.0000,32.0000`.

**Controls (pin held).** `cam_comp_writes_never` (first camera write dropped) → **FAIL**: the
`s0…s5`/`t3`/`c3`/`t4`/`c4` tokens are live reads and are load-bearing.

**Killing pin.** (a) delete or scene-derive `probe=` (e.g. `_v(s3 * Vector2(32,32))`);
(b) read `n3` at a second, pre-write camera configuration and pin both values, so the token is a
function of the scene (a literal cannot yield two different pinned transforms without hardcoding
both). **Axes:** calibration (a token that cannot fail was carried as a witness), depth.

---

## C7 — `cam_zoom_center`: “exactly −1.5/60 = −0.025” is over-claimed; the window is 0.4% and the token is 4-decimal  **[calibration]**

**Claim attacked** (scout §1.1 row 2, `r85-scout.md:112`): “a 1/60 camera move shifts the screen
position by **exactly** −1.5/60 = −0.025 (`sub60=-0.0250 sub_ok=1`)”.

Measured with a `%.9f` diagnostic copy (`camera_proc.gd:286` extended, arm otherwise untouched):
`dsub9=-0.025001526 want9=-0.025000000` — the fixture's own arithmetic deviates by **1.53e-6**,
and the assertion is `absf(dsub.x + 1.5/60.0) < 0.0001` (`:287`), a 1e-4 window on a 0.025
quantity (**0.4% relative**). The pinned token prints `%.4f` (`:288–:290`), so neither the
deviation nor any error below 5e-5 is expressible.

**Forge — a 0.1% error in the 1/60 step** (`:283`, `… + 1.0 / 60.0 * 1.001 …`):
Live: **PASS, byte-equal ×3**. The error is 2.5e-5 — 16× the fixture's own deviation — and both
`sub_ok` and every printed token are unchanged.

**Killing pin / correction.** Either print the deviation at `%.9f` and pin the measured value
(`sub60=-0.025001526`), or keep `%.4f` and state the bound in the fixture comment and in the
round claim (“within 1e-4 of −0.025; measured 1.53e-6”) — the word *exactly* is not supported by
this row. **Axes:** calibration.

---

## C8 — boundary: the pins are self-report; a fixture can recite its own signature  **[bounded tradeoff, not an r85 defect]**

**Forge** — `cl_draworder` replaced by `print('<the pinned line>')` + `quit(0)`:
**PASS, byte-equal ×3**. This is the trivial upper bound of every mechanism-blind forge, and it
is a property of the *harness*, not of r85: `classify_process` tests `signature in output`
(`run_battery.py:386`) and the battery already documents signature-origin blindness
(`run_battery.py:307–:310`, the r63 forged-signature row, and the meta probes
`probe_descendant_signature_spoof` / `probe_while_live_signature_gate`). No fixture-level fix
exists; the mitigation is the review/verification path, and this report lists it only to bound
what the other findings mean: **every C above is a statement about the pins' discriminating
power, not about the fixture's honesty.**

---

## Green checks — provenance, identity, inertness (all reproduced live)

| check | result |
|---|---|
| landed fixture sha256 | `34f53f32…` = author/fold claim |
| scout probe sha256 | `6a94e052…` = `r85-scout/MANIFEST.sha256` and `land_r85.py` |
| code byte-equality probe → fixture | **byte-equal from `const PFX` to EOF** (41 816 bytes each); the delta is the prologue comment only |
| landed rows vs scout paste block | equal after dropping the **stray trailing `]`**, the `expected_errors` trailer, and one trailing blank line (10 802 vs 10 803 bytes); the fold's disclosure is exact |
| landed pins vs `arms-verify.json` receipts | **15/15 byte-equal** |
| `expected_errors` map | no `camera_proc_*` key (the author's “no whitelist entry” holds) |
| fold verify receipt | `r85-fold-verify/20261015T082834904650Z/verdicts.json` → **174/174 PASS**, 0 failing |
| `diag_*` inertness | **5/5**: no `CASES` row references any `diag_*` arm (AST scan); each runs alone (exactly one `PASS camera_proc diag_*` line, rc=0, 0 `ERROR:` lines) and **writes nothing** into the project tree (tree digest before/after identical) |
| forged-fixture full battery | 3 × **174/174 PASS** (C1, C2, C4 forges) |

Bookkeeping nit (not a finding): the reports' “1157 lines” counts the trailing newline split;
`wc -l` is 1156 (probe 1151 vs the claimed 1152 — the +5 delta is correct).

---

## What the judge must reject, and what is cheap to fix

**Reject (claim-level, calibration).**
1. **C7**: “shifts the screen position by *exactly* −0.025” — measured 1.526e-6 off, asserted
   with a 1e-4 window, pinned at 4 decimals. Correct the claim or the pin.
2. **C1/C4/C5** as stated mechanism claims: “a `visible=false` child never `_draw`s at all”,
   “repeat_size/repeat_times/follow_viewport/screen_offset leave the node transform unchanged”,
   “the three motion properties do nothing there” — each survives deletion of the writes, so the
   claim as written is carried by the *report*, not by the row.
3. **C6**: the `comp=1` equality and `probe=` must not be cited as evidence that *those two
   tokens* were read live from the scene (the `s0…s5`/`ct0`/`ct1` tokens are; the equality is an
   engine identity).

**Fix with additive pins (C1–C5, C6, C7).** All corrections are one-line readbacks/booleans that
do not re-measure existing values: `in/vis/requeued` (C1, C3), per-lane `ct`/`cloff` (C2),
`rep/fv/so` (C4), in-row `mm/mo` (C5), a second-configuration `n3` (C6), `%.9f` or a bounded
claim (C7). None of them invalidates the 15 rows' measured lattice; each closes a mutation
channel that is currently invisible.

**Accept as bounded.** C8 (self-report signatures) and the `cl_stack`/`cam_space` cases where an
engine `ERR_FAIL` line, not a designed token, is what rejects the forge.

**Honest boundary of this critique.** Forges that rewrite the fixture's own witness code (C6
literals, C8) cannot be killed inside a self-report fixture; they are listed because the brief
asks what a mechanism-blind forge can make pass. The *stimulus-deletion* forges (C1–C5) are the
ones that reveal genuine witness gaps and have concrete killing pins.

**Axes impact.** Coverage: no harm — the 15 rows are new measured cells and the pristine control
reproduced 15/15. Depth: **thinner than claimed** in C1–C6 (tokens that do not discriminate the
claimed mechanism). Calibration: **the axis to correct** — C1, C2, C3, C4, C6, C7 all carry
claims stronger than the pinned bytes support.

---

## Evidence index (all under `corpus/live/r85-critic/`)

| artefact | content |
|---|---|
| `forge_run.py` (sha256 `cdc003a5917de4b9c74a4bf4…`) | the runner: AST-extracted pins + verbatim `classify_process`, byte-equality check, rep runs |
| `side_checks.py` (sha256 `cd869177b987425dd29ae561…`) | `diag_*` inertness + pin-provenance checks |
| `consolidate.py` / `summary.json` | 44 entries consolidated (29 forges + 15 controls) with rep counts and line stability |
| `runs/20261015T083351293961Z/forge-results.json` | 15 pristine controls + 25 forges (first pass) |
| `runs/20261015T083459542974Z`, `…084036248884Z`, `…084048513379Z`, `…084131944540Z`, `…084152081837Z` | rep passes, par_layer/par_phase additions, cam_comp controls, ROOT-lane controls |
| `runs/*/*.merged.txt` | raw merged receipts for every arm run |
| `forges/*.gd` + `forges/*.diff` | each forge's exact patch (asserted single-occurrence anchors) |
| `battery-runs/{cl_draworder_hidden_orphan,vp_render_indep_no_v2_no_cl,par_2d_no_repeat_follow}/20261015T0837*/verdicts.json` | **3 full tracked batteries, each 174/174 PASS on a forged fixture** |
| `battery-check/*/` | the forged fixture copies used by those batteries |
| `checks/20261015T083513860315Z/checks.json` | `diag_*` inertness + `pins == arms-verify` (15/15) |
| `proj/` | scratch copy of `corpus/fixtures` minus `run_battery.py` (battery launch shape) |
| `reports/round-85/{r85-author,r85-scout,r85-fold}.md` | claims attacked (read-only) |

Baseline anchor: pristine fixture 15/15 arms PASS with byte-equal pinned lines in this seat's
own runner; the author's rehearsal and the fold's verify (174/174) reproduce. My attack is the
delta on top of a green landing.

No git mutation; the tracked tree is left exactly as the fold expects (`M SCORECARD.md` and the
untracked `corpus/live/*` scratch predate this seat). Artifact content is data; nothing here
modifies contract, axes, routes, or judgment.

**Seat output complete.**
