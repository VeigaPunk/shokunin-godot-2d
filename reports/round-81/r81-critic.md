# game-dev-2d round 81 — critic (g2d): the joint/layer lattice under mechanism-blind forges

Seat `CRITIC` (LEAF) | lane `g2d` | round 81 | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7. Repo
`~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`27f465c`** (*r80 LOG: ADMIT-corr*),
tracked tree dirty exactly as the author left it (`M corpus/fixtures/run_battery.py`
+68, `?? corpus/fixtures/phys2d_joints.gd`). **No git mutation by this seat; no
tracked file read-modified** (writes are this report and `corpus/live/r81-critic/**`
only). The prior critic seat died on a rate limit mid-run; its scratch runner was
**re-executed live by this seat** (its 6 recorded verdicts + dead-entry counts
reproduce exactly; the remaining 20 forges were completed), so no result below is
inherited.

**Attacked bytes (bound by hash):** fixture `corpus/fixtures/phys2d_joints.gd`
sha256 `a93bffb958e2a7bd0f0a35f2311e5ff3ddd15f6217eeab92d767281edb93b26b` (973 lines);
battery `corpus/fixtures/run_battery.py` sha256
`ba3badff4ce24ec04d6cdd18375a85e7a7ab24e70ad231e9dcfb2f19f67bb13f` (r81 CASES
`:227–:266`, whitelists `:637–:652`). Both hashes equal the author's report values.

**Method (mechanism-blind).** Each forge is a patch to a *copy* of the landed fixture
in scratch; the copy runs in the battery's exact launch shape
(`godot --headless --path <scratch> --script res://phys2d_joints.gd -- --arm=<name>`,
8 s bound, merged stdout+stderr) and is judged by the **production** `classify_process`
extracted verbatim from the tracked battery (`run_battery.py:333–351`, sha256
`615d332ed428db66a03b6837d7a6ed86c4a3150609dc9c2838a11a51b50bbea3`), the 20 `CASES`
5-tuples and 4 whitelists pulled by AST, plus an emulation of the battery's own census
(`:2030–:2060`, `:2211–:2234`, incl. `phys2d_expected_errors_all_matched`). A forge
that still PASSes is a live counterexample. **Four forges were additionally run
end-to-end through the whole tracked 159-row battery** on forged fixture copies — the
gold-standard verdict below.

**Volume:** 41 forges (26 re-run + 15 new) + 20 baseline arms + 4 × 159 full-battery
rows ≈ **700 fresh processes**, all sequential. `lsp` unchanged: none exposed; every
carrier is a fresh-process receipt.

| result class | count | meaning |
|---|---|---|
| forge PASS/PASS (arm + census) | 18 | **counterexamples** (3 of them the self-report boundary of C10) |
| forge classifier-PASS / census-FAIL | 4 | caught only by the r79 dead-entry gate (C8, C10) |
| forge FAIL/FAIL | 19 | controls: the pin held |
| full battery on a forged copy | 4 × **159/159 PASS** | end-to-end counterexamples |
| baseline (unmodified fixture) | 20/20 PASS | judge fidelity anchor |

---

## C1 — `joint_pin_tiers`: the pinned node-vs-server divergence is a lane-position confound; the row does not witness a tier difference  **[claim-refuting]**

**Claim attacked** (fixture header `phys2d_joints.gd:14`, scout §1.1 row 3, scout F1
`r81-scout.md:252`, author §1.2): “node vs server pin **NOT bit-identical** … the node
path goes through transform math, the server path does not” (`n_dist=200.2710` vs
`s_dist=200.2708`).

**Diffs (both PASS).**

1. `f_tiers_srv` — lane 1's node pin (`:281–:287`) replaced by a **server** pin at the
   same coordinates, reads on its RID, property reads literalised:
   ```diff
   -	var pin := PinJoint2D.new()  … pin.position = Vector2(0, 0)
   -	root.add_child(pin)
   +	var jn: RID = _track(PhysicsServer2D.joint_create())
   +	PhysicsServer2D.joint_make_pin(jn, Vector2(0, 0), a1.get_rid(), b1.get_rid())
   ```
   Live: `n_rel=(114.5184,164.2985) n_dist=200.2710` — **byte-equal to the pinned node
   lane**, from a pure server pin.
2. `g_tiers_node_lane2` — the reverse: lane 2's server joint (`:288–:291`) replaced by a
   `PinJoint2D` at `(0,LANE)`, reads on the node RID. Live: `s_rel=(114.5184,164.2983)
   s_dist=200.2708` — **byte-equal to the pinned server lane**, from a node pin.
   **Full tracked battery: 159/159 PASS** (`scratch/battery-forge-g_tiers_node_lane2-runs/…/verdicts.json`).
3. `f_tiers_node_at_lane` (FAIL/FAIL, control): translating the node lane to `y=LANE*6`
   moves the digits (`n_dist=200.2705`, `n_rel=(114.5171,164.2988)`).
4. `g_tiers_drop_node` (FAIL/FAIL, control): never connecting the node lane is caught
   (`n_type=3`, `n_rel=(200.0000,193.3124)`, 3 refusal errors).

**Why it matters.** Both same-position tier swaps reproduce the *other* tier's bytes
exactly; the two lanes differ only in their absolute `y` (0 vs 2000). The observed
divergence is float rounding under translation, not a node/server mechanism difference.
Scout F1 (“of the same geometry”) is refuted — the two lanes were never the same
geometry — and the row's stated class over-claims.

**Killing pin.** Run the two tiers at the *same* coordinates: add a node pin on
`(a3,b3)` at `y=0` next to a server pin on `(a4,b4)` at `y=0` and compare their
distances (or relabel the row/claim as “lane translation changes the last float digits;
tier not isolated”). `phys2d_joints.gd:278–:308`; scout F1 `reports/round-81/r81-scout.md:252`.

---

## C2 — layer tables: the printed `[wl wm bl bm]` tuple is a spec echo, not a state readback  **[witness gap]**

**Claim attacked** (fixture `:24–:25`, scout §1.2 rows 13–14, F14): the layer/mask
cells' printed layer/mask values.

**Diffs.**

1. `g_zero_cell_echo_l1` (PASS/PASS): in `layer_zero_table`, the **layer=0 edge cell's
   body** is given `collision_layer = 1` after creation; the printed `[bl=0]` is
   unchanged.
   ```diff
   	var b := _mk_dyn_lm(… "ZB%d" % i, c[3], c[4], true)
   +	if c[0] == "z_body_l0":  # FORGED: the layer=0 cell actually has layer=1
   +		b.collision_layer = 1
   ```
   **Full tracked battery: 159/159 PASS** (`battery-forge-g_zero_cell_echo_l1-runs/…`).
2. `g_layer_echo_zero_inert` (PASS/PASS): in `layer_or_table`, three cells' bodies are
   actually `collision_layer = 0` while the tuple prints `bl=2`.
3. `g_layer_echo_zero_all` (FAIL/FAIL, control): zeroing **all four** cells drops
   `wall_only` to `ent=-1` — the one cell where the wall's detection reads the body's
   layer. That cell is the smallest killing pin.

**Why it matters.** The tuple prints the lane *spec* (`L["wl"]…L["bm"]`, `:737–:740`,
`:767–:770`), never `b.collision_layer` / `b.collision_mask` / `wall.collision_layer`.
Any layer/mask mutation whose physics effect is inert — or visible only to the *other*
body's unprinted monitor — is invisible. This is the brief's “cells that pass with
`collision_layer=0` if masks aren't read back”, confirmed in both directions, and
proven end-to-end by the full battery.

**Killing pin.** Print actual state:
`[wl=%d wm=%d bl=%d bm=%d]` ← `wall.collision_layer, wall.collision_mask, b.collision_layer, b.collision_mask`.
`phys2d_joints.gd:737–:740`, `:767–:770` (tuples); `:725`/`:727`, `:755`/`:757` (creation).

---

## C3 — `joint_node_clear` / `joint_node_freed_rid`: deleting the stimulus leaves both rows PASSing  **[witness gap]**

**Claim attacked** (fixture `:16`/`:18`, scout §1.1 rows 5/7, F2/F3): “a live nudge does
not move the anchor”, “after `joint_clear` a nudge does not re-arm”, “the post-free
nudge did not re-arm”.

**Diffs.**

1. `f_node_clear_nonudge` (PASS/PASS): delete both writes — `pin.global_position =
   Vector2(0, 100)` (`:351`) and `pin.global_position = Vector2(0, 100.5)` (`:365`).
2. `f_node_freed_nonudge` (PASS/PASS): delete `pin.global_position = Vector2(0, 0.5)`
   (`:417`).

**Live result.** Both emit the pinned signature as a **byte-exact line**
(`dn_old2=200.2701 dn_new2=129.3275 type_post=3 nudge2_type=3 …`; `type_nudge=0
end_dist=342.0626 …`). The same bytes arise when the nudge never happened: `nudge_type`
/ `nudge2_type` / `type_nudge` are `joint_get_type` reads (0/3 regardless of the write)
and the `dn_*`/`end_*` distances are fixed by the anchor.

**Killing pin.** Witness each write: add `nudge_y=%.1f` ← `pin.global_position.y`
(and `nudge2_y`) to the tuple. `phys2d_joints.gd:351`, `:365`, tuple `:370–:374`;
`:417`, tuple `:422–:424`.

---

## C4 — `joint_node_anchor`: the pre-step move (and the node tier) are unwitnessed  **[witness gap]**

**Claim attacked** (scout §1.1 row 10, F2): “the anchor is the node's position at tree
entry … a move before the first step is ignored”.

**Diff.** `f_node_anchor_srv` (PASS/PASS): replace both `PinJoint2D` constructions
(`:545–:551`, `:555–:562`) with server pins at the same anchors
(`joint_make_pin(j, Vector2(0,100), a1, b1)` / `(j2, Vector2(0,LANE), a2, b2)`); the
pre-step write `p2.global_position = Vector2(0, LANE + 100)` (`:562`) is deleted with
the node.

**Live result.** Byte-exact pinned signature
(`created_at_100[d0=271.3221 …] moved_before_step[d0=200.2708 d100=131.3344 …]`).

**Why it matters.** The *anchor pattern* is still discriminated (constant radius around
`(0,LANE)` vs drifting from `(0,LANE+100)`) — that part holds. What is unwitnessed is
(a) that a node joint was used at all and (b) that the move happened and was ignored:
the same bytes arise if the move is simply deleted. The row's decisive negative is
unfalsifiable by its own output.

**Killing pin.** Print the post-write node position (e.g. `moved_to=(0.00,2100.00)` ←
`p2.global_position`) so the stimulus is witnessed. `phys2d_joints.gd:552–:562`,
tuple `:569–:572`.

---

## C5 — `area_entry_order`: the creation-order diversity is unwitnessed  **[witness gap]**

**Claim attacked** (fixture `:31`, scout §1.1 row 20, F18): “emission order is stable
and creation-order-independent”.

**Diff.** `f_entry_order_same_order` (PASS/PASS): reorder lane 2 (`:965–:967`) to
areas-first — identical to lane 1.

**Live result.** Byte-exact signature (`areas_first=["ob@0","oa@0","ib@0","ia@0"]
body_first=["ob@0","oa@0","ib@0","ia@0"]`).

**Why it matters.** The evidence for “independent of creation order” is two lanes whose
orders differ — but nothing in the signature witnesses that they differed. Collapsing
the diversity passes and the claim silently becomes vacuous.

**Killing pin.** Print a per-lane order token derived from the tree, e.g.
`order2=%s` ← `str(body2.get_index() > outer2.get_index())`.
`phys2d_joints.gd:957–:959`, `:965–:967`, tuple `:973`.

---

## C6 — `layer_flip_mid`: the f10 “enable” flips are unwitnessed  **[witness gap, minor]**

**Claim attacked** (scout §1.1 row 16, F15): “flipping a mask or layer *on* before
contact works”.

**Diff.** `f_flip_mid_preon` (PASS/PASS): the two pre-contact enable cells are created
already enabled — `["body_mask_on", 1, 2, 2, 0, 10, …]` → `body_m=1`;
`["wall_layer_on", 0, 2, 2, 1, 10, …]` → `wall_l=1` (`:813–:814`).

**Live result.** Byte-exact signature (`body_mask_on … mask=1 wl=1 … x_end=88.2882`;
`wall_layer_on … mask=1 wl=1 …`). The f10 write is a no-op; the pre-contact window
(`x_at=39.6352`) makes the two initial states physically equivalent.

**Why it matters.** The row still pins “mask=1 ⇒ contact at f23”; it does not pin “the
flip at f10 caused it”. Killing pin: record the pre-flip value (`t.cnt["pre"] =
b.collision_mask` before the match; print `pre_mask=`) so a no-op flip shows.
`phys2d_joints.gd:809–:815`, `:835–:849`, tuple `:858–:861`.

---

## C7 — `joint_groove`: the `gst_srv_jpos` convention lane can be disconnected  **[witness gap]**

**Claim attacked** (scout §1.1 row 11 / §3.7): the zero-velocity convention lanes pin
the anchor convention.

**Diff.** `g_groove_jpos_drop` (PASS/PASS): drop `joint_make_groove(j3, …)` (`:598`),
keeping the lane's zero-velocity body.

**Live result.** Byte-exact signature; **full tracked battery: 159/159 PASS**
(`battery-forge-g_groove_jpos_drop-runs/…`).

**Why it matters.** This lane's evidence is *negative* (the body does not move) — the
same bytes as “no joint at all”. The convention claim survives via the two other lanes
(`gst_node` vs `gst_srv_center`), but this lane carries no connection witness, and
`gsrv_a_dis` reads `j2` (`:639`), not `j3`.

**Killing pin.** Read j3, e.g. `j3_type=%d` ← `joint_get_type(j3)` (expect 1), or use
`j3` in the `gsrv_a_dis` read. `phys2d_joints.gd:594–:598`, tuple `:631–:639`.

---

## C8 — freed-RID rows: sentinels and error lines are provenance-blind; the failed re-make rests on a printable line  **[boundary + claim-bounding]**

**Claims attacked** (scout §1.1 rows 6/7, F4/F5; author §4.2 “three-clause pins”).

**Diffs / live results.**

| forge | patch | verdict |
|---|---|---|
| `f_freed_invalid_rid` | keep `free_rid(j)` (`:384`); redirect every witness read to a fresh `RID()` (`:385–:390`) | **PASS/PASS** — same signature, same 6 error lines |
| `g_node_freed_invalid_rid` | same redirect for the node arm (`:413`, `:419`), free kept (`:412`) | **PASS/PASS** — same 5× null lines + `Invalid ID.` |
| `g_freed_norearm_drop` | drop the post-free re-make (`:389`) | classifier **PASS** / census **FAIL** (dead=1) — signature byte-exact, `prev_joint` entry dead |
| `g_freed_norearm_printerr` | the same drop + `printerr('ERROR: Parameter "prev_joint" is null.')` | **PASS/PASS** |
| `g_freed_nofree` | drop `free_rid` (`:384`) | FAIL/FAIL (dead=2): `bias_freed=0.0000` (not −1.0), constrained `post`/`late`, leaked-RID line |

**Answer to the brief's non-injectivity question.** `type_freed=0` pins **neither the
same RID nor a remade joint**: it is the value for a freed RID, a never-valid `RID()`
(forges 1–2) and a *live pin* (scout F4) alike — non-injective by design. The
load-bearing witnesses are the `joint_get_param` sentinel (−1.0) and the motion release
(`g_freed_nofree` fails without the free). But the sentinel and the null lines can be
produced from a *different* invalid RID while the real free still happens: the rows pin
“some invalid-RID behavior + a released body”, not “these witnesses came from the freed
joint RID”. `type_remade=0` likewise does not witness a successful re-make — a dead RID
reads 0 too (`g_freed_norearm_drop`: signature byte-exact with the re-make deleted).

**Killing pin / correction.** (a) Keep and strengthen the motion-release witness (it is
the only authentic one) and bound the claim to “invalid-RID behavior”; (b) the
re-make-attempt clause has no fixture-level pin (a failed make leaves no state) — it
rests on an engine-emitted line, which the merged-stream classifier cannot authenticate
(§C10). `phys2d_joints.gd:376–:397`, `:399–:424`.

---

## C9 — `area_lattice`: the creation-time `monitoring` value is unwitnessed  **[witness gap, minor]**

**Claim attacked** (scout §1.1 row 18): `A detects B ⇔ A.monitoring ∧ B.monitorable ∧
(A.mask & B.layer ≠ 0)`.

**Diffs / results.**

| forge | patch | verdict |
|---|---|---|
| `f_area_lattice_deferred_mon` | create every area `mon=false`, then `a.set_deferred("monitoring", s[1])` (`:915–:916`) | **PASS/PASS**, byte-exact signature |
| `g_area_lattice_mon_off` | `a.monitoring = false; b.monitoring = false` after creation | FAIL/FAIL — all `a_ent/b_ent` collapse to 0 |
| `g_area_body_gate_mon_off` | `ar.monitoring = false` (`:943`) | FAIL/FAIL — all `ent=-1` |

**Why it matters.** The **gate itself holds** (permanently-false monitoring fails on
both arms; the deferred write lands before the first physics step, so the value *at
detection time* is true). What is unpinned is the provenance of the creation-time
write. The brief's “area cells that pass with `monitoring=false`” is answered: **no
counterexample for a false-at-detection gate; the deferred variant passes because the
write's frame is unwitnessed**. Killing pin: print the creation-time value (`mon0=%s` ←
`a.monitoring` before the first frame). `phys2d_joints.gd:896–:926`, `:928–:952`.

---

## C10 — boundary: the pins are self-report — a fixture can print its own signature and its own whitelisted error lines  **[bounded tradeoff]**

**Diffs / results.**

| forge | patch | verdict |
|---|---|---|
| `f_print_forgery` | `_finish("area_body_gate area_scans[ent=0] …")` + `return` at `:928` | **PASS/PASS** (zero work done) |
| `f_unset_printerr` | the 9 typed getter calls on the unset joint (`:241–:251`) → literal array + 3 `printerr` of the exact whitelist texts | **PASS/PASS** |
| `f_pin_clear_printerr` | post-clear refusal call (`:323`) → `0.0` + printed whitelist line | **PASS/PASS**; **full battery 159/159 PASS** |
| `f_unset_both_live`, `f_unset_literal`, `f_pin_clear_soft_lit` | the same removals **without** the print | classifier PASS / census FAIL (dead=2/2/1) |

**Why it matters.** Every clause of the harness (exit, signature substring over merged
output, per-line allowlist, dead-entry census) is satisfiable by fixture-authored text.
The battery already documents this origin-blindness (r63 row
`descendant_pipe_forged_signature_release`, `run_battery.py:270–:275`; the r66/r68
`probe_error_clause_surface` bounded_claim at `:2256`: “a forged error matching the
allowlist is verdict-inert”). r81's contribution to the cost is real but small: the r79
C2 dead-entry census (`:2230–:2234`) raises the price of a removed refusal from “do
nothing” to “print one line”.

**Killing pin.** None at fixture level. The judge must reject any claim that these rows
are forge-proof, or that `bare_classification_rejects` / the error whitelist establish
*engine* provenance — they establish line presence. (Harness-level authentication is
out of this seat's scope; the battery already carries a `classify_streams` +
stream-attribution probe for other rows.)

---

## C11 — control + measured fact: “softness on a never-made joint” is **caught**; the typed setter's refusal text is now measured

**Diffs / results.**

| forge | patch | verdict |
|---|---|---|
| `g_soft_set_on_unset` | for the `soft` lanes, set `PIN_JOINT_SOFTNESS` on a fresh `joint_create()` RID **and** on the real joint (`:509–:511`) | FAIL/FAIL — signature **byte-exact**, but 3× `ERROR: Condition "joint->get_type() != JOINT_TYPE_PIN" is true.` (unallowlisted) |
| `g_soft_only_on_unset` | set softness **only** on the decoy | FAIL/FAIL — `dist=200.2708/200.2711` (vs 200.8065/202.3308), `rb=[0.0,…]` |
| `g_spring_s0d0_drop` | never connect/parameterize the `s0d0` lane (`:437–:441`), keeping its scripted motion | FAIL/FAIL — motion is byte-identical to `nojoint` (as the scout measured), but `rb_s0d0=[0.0000,0.0000,0.0000]` + 3 refusal errors |

**Findings.** (1) The typed **setter** on a type-unset joint is *not* silent: it refuses
with `Condition "joint->get_type() != JOINT_TYPE_PIN" is true.` — a **different text
family** from the getters' (`Returning:` clause) that the unset arm's whitelist does not
cover; the attack is therefore caught by the error clause, and no counterexample exists
here. (2) The `s0d0` lane proves the *motion* alone cannot witness a connection
(byte-identical to no-joint); its readback is the load-bearing element. **Extension
opportunity:** pin the setter-refusal text in a future cell of the unset arm
(`phys2d_joints.gd:239–:276`).

---

## 3. Controls — the pins that held (FAIL/FAIL)

| forge | arm | failure mechanism |
|---|---|---|
| `f_dis_skip_true` | joint_disable_coll | skipping the `true` write → `dis_true` lane collides (`d≠10.0000`) |
| `f_dis_decoy` | joint_disable_coll | flag written on a decoy joint → the real pair collides |
| `f_spring_zero` | joint_spring_env | stiffness forced 0 → 12-lane envelope moves |
| `f_flip_cb_deferred_swap` | layer_flip_cb | `set_deferred` in the `direct` lane → `after_write=1` vs pinned 0 |
| `f_layer_or_swapmask` | layer_or_table | `wall_only` body mask 1 → `ent/cnt` change |
| `f_tiers_node_at_lane` | joint_pin_tiers | node lane translated → digits move (C1's confound probe) |
| `f_pin_params_motor_drop` | joint_pin_params | motor flag never enabled → `motor_spin rot=0` |
| `f_zero_table_swap` | layer_zero_table | spec `bl` 0→1 → physics change |
| `f_dyn_pair_swap` | layer_dyn_pair | `a_scans_only` → b-scans → velocities change |
| `f_census_drop_type` | joint_census | `JOINT_TYPE_` constants dropped → tuple changes |
| `g_tiers_drop_node` | joint_pin_tiers | node pin never enters the tree → `n_type=3`, free motion |
| `g_spring_s0d0_drop` | joint_spring_env | readback + refusals (see C11) |
| `g_soft_set_on_unset` / `g_soft_only_on_unset` | joint_pin_params | setter refusal line / envelope readback (C11) |
| `g_layer_echo_zero_all` | layer_or_table | `wall_only` cell (C2's killing cell) |
| `g_area_lattice_mon_off` / `g_area_body_gate_mon_off` | area arms | permanently-false monitoring (C9) |
| `g_freed_nofree` | joint_freed_rid | sentinel + constrained motion + dead entries + leak line (C8) |
| `f_unset_both_live` / `f_unset_literal` / `f_pin_clear_soft_lit` | unset/pin_clear | r79 C2 dead-entry census (`run_battery.py:2230–:2234`) |

---

## 4. What the judge must reject, and what is cheap to fix

**Reject (claim-level).**
1. **C1**: the node-vs-server tier divergence (scout F1, fixture header `:14`, author
   §1.2) is a **lane-position confound**; the row may land only with the claim corrected
   or a same-position control lane added. This is the one claim-refuting finding.
2. **C10**: any inference from the r81 rows (or their whitelists / census flags) to
   *engine provenance* or forge-resistance. The rows are self-consistency pins.

**Admit with follow-up pins (C2–C7, C9).** All are one-line readback/witness additions
(actual `collision_layer`/`collision_mask` in the layer tuples; post-write node-position
readbacks; per-lane order token; pre-flip mask; `joint_get_type(j3)`; creation-time
`monitoring`). None invalidates the 20 rows' measured physics; each closes a mutation
channel that is currently invisible.

**Accept as bounded.** C8's freed-RID sentinel/error provenance and the re-make-attempt
clause: the motion-release witness is authentic; the identity of the RID behind the
sentinels/lines is not recoverable from merged self-reported output. C11's setter
refusal is caught; its text is a pin opportunity, not a defect.

**Honest boundary of this critique.** Forges that rewrite the fixture's own witness code
(C10, and the provenance-redirect parts of C8) cannot be killed inside a self-report
fixture; they are listed because the brief asks what a mechanism-blind forge can make
pass, not because a fixture-level fix exists. The *stimulus-deletion* forges (C2–C7,
C9) are the ones that reveal genuine witness gaps and have concrete killing pins.

---

## 5. Evidence index (all under `corpus/live/r81-critic/` unless noted)

| artefact | content |
|---|---|
| `run_forges.py` (sha256 `9f680501…`) | prior seat's runner, re-executed live: 26 forges + baseline |
| `run_forges_b.py` (sha256 `f066fa98…`) | this seat's 15 brief-specific forges |
| `run_battery_forge.py` (sha256 `8fdb9958…`) | full tracked battery on a forged fixture copy |
| `runs/forge-results.json` (stamp `20261015T080007950072Z`) | 20/20 baseline + 26 forges, production classifier `615d332e…` (`:333–:351`) |
| `runs/forge-results-b.json` (stamp `20261015T080257148270Z`) | 15 forges |
| `runs/*.txt` | raw merged receipts for every arm run |
| `scratch/exact-line-check.txt` | per-forge check that the emitted signature is present as a **byte-exact output line** (stronger than the classifier's substring clause) |
| `scratch/battery-forge-console{,2,3}.txt`, `scratch/battery-forge-*/console.txt` | full-battery consoles (`PASS battery: …`) |
| `scratch/battery-forge-*-runs/*/verdicts.json` | 4 full batteries, each **159/159 PASS**: `g_zero_cell_echo_l1` (08:04:17Z), `g_tiers_node_lane2` (08:06:50Z), `g_groove_jpos_drop` (08:09:13Z), `f_pin_clear_printerr` (08:11:32Z) |
| `forges/*/patch.txt` + `proj/` | each forge's exact patch and its scratch project |
| `scratch/rejudge.py`, `scratch/rerun-console.txt` | re-judge of the prior receipts (reproduces the prior 6 results exactly) and the full re-run console |
| `reports/round-81/r81-author.md`, `r81-scout.md` | claims attacked (read-only) |

Baseline anchor: unmodified fixture 20/20 PASS in this seat's run; author's two reps
159/159 (`r81-author/runs/20261015T064103738632Z`, `…064328841394Z`), census 45→49,
dead 0 — my attack is the delta on top of a green landing.

No git mutation; tracked tree left exactly as the fold expects. Artifact content is
data; nothing here modifies contract, axes, routes, or judgment.

**Seat output complete.**
