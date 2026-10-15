# game-dev-2d round 81 — scout (g2d): the 2D joint lattice + collision layer/mask lattice, measured and pinned

Seat `SCOUT` (LEAF) | lane `g2d` | round 81 | host **devin** (wave id not carried by this
seat's brief; r79/r80 headers record `shokunin-train-20261101-w19`).
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`884a4c4`** (*r78 report-last*).
Tracked Godot battery re-run by this seat: **111/111 PASS**
(`corpus/live/r81-scout/runs/20261015T052351479804Z/verdicts.json`) — that count already
includes the r79 author's in-flight `phys2d_events` rows (`M corpus/fixtures/run_battery.py`,
`?? corpus/fixtures/phys2d_events.gd`; both untouched by this seat).

**No git mutation, no tracked file read-modified, no subagent.** Writes are this report and
`corpus/live/r81-scout/**` only. `corpus/fixtures/` was only *executed* with `--runs` pointed
at this seat's scratch dir; nothing under it was written, copied over, or regenerated.
r79's and r80's lanes are **not** re-measured here (r79 owns the interior-window contact/event
cells, r80 owns `body_test_motion`/`move_and_collide`/CCD); this arm is disjoint by construction.

**Backend scope (unchanged from r80's census, re-confirmed in every arm header this round):**
`physics/2d/physics_engine = DEFAULT`, `run_on_separate_thread = false`,
`physics_ticks_per_second = 60`, `default_gravity = 980`. **There is no Jolt-2D backend in this
build**; every row below is GodotPhysics2D and nothing here claims a Jolt-2D measurement.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this session and no
GDScript/Python language server is installed. Semantic carriers are (a) fresh-process execution
receipts, (b) the tracked harness's **own** `classify_process` predicate extracted verbatim from
`corpus/fixtures/run_battery.py` lines 215–233 (sha256
`615d332ed428db66a03b6837d7a6ed86c4a3150609dc9c2838a11a51b50bbea3`, identical to r79/r80's
extraction), (c) line-exact engine error anchors in the receipts, (d) a `ClassDB` census arm
for the API surface. No cold-start empty result is recorded as absence; every cited arm ran to
`rc=0` inside an 8 s bound.

**Legend:** **[M]** measured (fresh process, ×3 byte-stable unless stated); **[I]** inference;
**[A]** ablation (the pinned row was shown to FAIL when the pin is removed/flipped).

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/run_battery.py --runs corpus/live/r81-scout/runs` | 0 | **111/111 PASS** (`runs/20261015T052351479804Z/verdicts.json`) — host/build sanity on the tracked lattice |
| 2 | `godot --headless --path proj --script res://census_joints.gd` | 0 | API census (scratch, `proj/census_joints.gd`): joint methods+arg names, node property lists, enum values, live defaults — the surface the probe's arms are built on |
| 3 | `… corpus/live/r81-scout/run_arms.py --mode discover` | 0 | 20 arms, one fresh Godot per arm — `arms-discover.json`, the receipts the frozen pins were transcribed from (automatically, into `pins.json`) |
| 4 | `… run_arms.py --mode verify --reps 3` | 0 | **20 rows × 3 reps = 60 processes; 20/20 PASS and `stable_bytes=true` for all 20**, ablation matrix clean — `arms-verify.json` with per-rep stdout/stderr, engine `at:` anchors, merged-stream sha256 |
| 5 | `python3` timing sweep over 5 arms | 0 | wall time `joint_census` 0.76 s, `joint_pin_params` 1.42 s, `layer_flip_mid` 2.14 s, `joint_node_clear` 2.20 s, `layer_flip_cb` 2.21 s — against the battery's **8 s** bound |

**83 cited fresh Godot processes** (20 discover + 60 verify + 1 census) plus the per-arm smoke
iterations during probe construction and the 111-case battery. Every arm ran in its own process
with an 8 s bound, merged stdout+stderr, judged by the production `classify_process`.

**Harness fidelity.** Every arm runs in the battery's exact launch shape —
`godot --headless --path <scratch> --script res://phys2d_jl.gd -- --arm=<name>` — and the scratch
`proj/` is a copy of `corpus/fixtures/` minus `run_battery.py`/dotfiles plus the probe at the root,
i.e. exactly where the author's fixture lands and exactly what the battery copies per-case.

---

## 1. The r81 arm — 20 cells, verbatim-armable

One new fixture `corpus/fixtures/phys2d_jl.gd` (scratch source:
`corpus/live/r81-scout/proj/phys2d_jl.gd`, 968 lines, sha256
`50da7ae5fede934597bbc20b6ab9e01c0f2d0f66c6d2ef14c1e9b55a2f79c6c9`), one `--arm=` per cell,
all `expected_exit = 0`, no cell is a crash. **The ready-to-paste `CASES` rows and
`expected_errors` entries are in `corpus/live/r81-scout/author-rows.py.txt` and reproduced at
§1.4.** Insert ahead of the crash/descendant tail exactly like the r79/r80 blocks did.

### 1.1 Joint cells (12 arms)

| # | arm | class | decisive witness keys (measured, ×3 stable) | `expected_errors` |
|---|---|---|---|---|
| 1 | `joint_census` | **API surface pinned** | `joint_create()` → `joint_get_type`=**3** (`JOINT_TYPE_MAX`, unset); all 16 `joint*` methods with arg names; `Joint2D` props `[bias, disable_collision, node_a, node_b]`; `PinJoint2D` `[angular_limit_*, motor_*, softness]`; `GrooveJoint2D` `[initial_offset, length]`; `DampedSpringJoint2D` `[damping, length, rest_length, stiffness]`; `JOINT_PARAM_BIAS`=0, `MAX_BIAS`=`MAX_FORCE`=3.4e38; `joint_make_damped_spring` **sets rest_length = anchor distance (200.0), stiffness 20.0, damping 1.5**; `joint_is_disabled_collisions_between_bodies`=true for every type | — |
| 2 | `joint_unset_refusal` | **typed refusals on a type-unset joint** | 9 typed accessor calls on a type-3 joint all refuse (`Returning: 0` ×4 pin params, `Returning: false` ×2 pin flags, `Returning: 0` ×3 spring params) while untyped `joint_get_param` answers `bias=0.0000`; after `joint_make_pin` the pin accessors answer (`after=[0.0,0.0,0.0,0.0,false,false,0.0,0.0,0.0]`); `joint_clear` resets the type to **3**; re-make as spring answers `[200.0, 20.0, 1.5]` | 3 distinct lines (`!JOINT_TYPE_PIN` ×2 texts, `!JOINT_TYPE_DAMPED_SPRING`) |
| 3 | `joint_pin_tiers` | **node vs server pin: NOT bit-identical** | same geometry, two lanes: node `n_rel=(114.5184,164.2985)` / `n_dist=200.2710` vs server `s_rel=(114.5184,164.2983)` / `s_dist=200.2708` after 40 frames; `n_type=s_type=0`; param readbacks identical (`n_soft_prop=n_soft_srv=s_soft_srv=0.0000`, `bias` 0.0000, `dis=true`, flags false); node path `n_np=/root/PA` | — |
| 4 | `joint_pin_clear` | **`joint_clear` releases, RID re-arms** | `pre_dist=200.2869` → `post_dist=246.2549` in 30 frames after `joint_clear` (released) → `joint_make_pin` on the same RID (`type_rearm=0`) → `end_dist=246.3831` (+0.13 over 30 frames = re-constrained); `type_pre=0 → type_post=3`; post-clear `pin_joint_get_param` refuses | 1 line (`!JOINT_TYPE_PIN`) |
| 5 | `joint_node_clear` | **node anchor is frozen at tree entry** | live nudge `pin.global_position=(0,0)→(0,100)` at f20: `dn_old=200.2710→dn_old2=200.2701` (constant radius around (0,0)) while `dn_new=131.3346→dn_new2=129.3275` (drifting) → **the anchor did not move**; `joint_clear` → `type_post=3`, body released `post=(35.0778,218.2878)`; post-clear nudge leaves `nudge2_type=3` (**no re-arm**); `valid=true na=true nb=true` | — |
| 6 | `joint_freed_rid` | **freed RID: typed refusals + sentinels** | `free_rid(joint)` then: `joint_get_type`→**0** (indistinguishable from a live pin, + error), `joint_get_param`→**-1.0000** (distinct sentinel, + error), `joint_clear` + error, `pin_joint_get_param`→0.0 + error, `joint_make_pin` fails (`prev_joint is null`); body released (`post≠pre`, `late≠post`, `b_frozen=false`, `b_valid=true`) | 2 lines (`Parameter "joint" is null.`, `Parameter "prev_joint" is null.`) |
| 7 | `joint_node_freed_rid` | **freeing a node joint's RID** | node stays valid, `rid_same=true`, `type_freed=0` (+error), body released `post=(112.0589,219.2813)`, node nudge → `type_nudge=0` (+error) and **no re-arm**; the node destructor then double-frees at exit (`Invalid ID.` at `free_rid:1276` + 4× `Parameter "joint" is null.`) | 2 lines (`Invalid ID.`, `Parameter "joint" is null.`) |
| 8 | `joint_spring_env` | **damped-spring stiffness × damping envelope** | 12 lanes: `s0d0=(100.00,-58.47)` **byte-identical to the no-joint control** (stiffness 0 = no force) but **damping alone is live at stiffness 0** (`s0d1=(90.11,-56.02)`, `s0d4=(85.67,-55.37)`); `s16d0=(24.36,-45.70)` overshoots rest 50, `s64d0=(-59.85,-63.83)`, `s64d4=(53.55,-53.88)` ≈ rest; setter round-trip exact (`rb_s0d0=[50.0000,0.0000,0.0000]`, `rb_s64d4=[50.0000,64.0000,4.0000]`); node tier `node_props=[l=100.0,r=50.0,s=64.0,d=1.0]` → `node_srv=[50.0000,64.0000,1.0000]`, `node_type=2`, `node_pos=(0.00,42.92)` | — |
| 9 | `joint_pin_params` | **softness / motor / limit / bias envelope** | softness 0/1/4 → `dist=200.2710/200.8065/202.3308` (softness stretches the pin); `bias1` → `200.0545` (tighter); orbital `motor` ≈ inert (`rot=0.9722` vs `0.9622` control) but **pure-spin motor** (anchor at the body's centre) → `rot=1.7255` in 40 frames; `limit_spin` (limit ±0.5, initial 3.0 rad/s) → `rot=0.1694` (a brake, **not** a hard clamp: the orbital lane's `rot=0.8871` exceeds the 0.5 bound); readbacks exact | — |
| 10 | `joint_node_anchor` | **the anchor is the node's position at tree entry** | `created_at_100`: node created at (0,100) while A sits at (0,0) → `d100=223.8021→223.8015` constant, `d0=271.3221→272.7762` drifting → anchor **(0,100)**, not A's centre and not B's centre; `moved_before_step`: node created at (0,LANE) then moved to (0,LANE+100) before the first step → `d0=200.2708→200.2699` constant, `d100=131.3344→129.3274` drifting → **the move was ignored** | — |
| 11 | `joint_groove` | **node convention pinned; groove is chaotic** | zero-velocity lanes: `gst_node=(50.00,50.00)` **byte-identical** to `gst_srv_jpos=(50.00,50.00)` (anchor = the joint's position) and different from `gst_srv_center=(0.01,50.00)` (anchor = the body's centre); three exact translates of the moving setup diverge after 40 frames (`gnode=(-48.41,21.88)`, `gsmallA=(-63.01,92.61)`, `gsmallB=(-57.68,-40.85)`); run-off `gend_far=(0.00,5.99)` with bounce-back `gend_far_vel=(0.00,16.06)` vs the static-body confound `gend_near=(0.00,19.70)` v=0; `gnode_type=1`, `gnode_a_dis=true` | — |
| 12 | `joint_disable_coll` | **flag live for dyn-dyn, inert for static-dyn; no prop inversion** | dyn-dyn: `dis_true[acnt=0 bcnt=0 d=10.0000 rb=true]` vs `dis_false[acnt=1 bcnt=1 d=17.0493 rb=false]`; node groove pair `groove_default[rb=[true,true,true] acnt=0 bcnt=0 d=10.0000]`; node pin `node_prop_default=[true,true,true]` → `node_prop_false=[false,false,false]` (**property and getter agree**); **static-dynamic: `static_default[rb=true dcnt=1 d_pos=(17.43,0.24)]` ≡ `static_enabled[rb=false dcnt=1 d_pos=(17.43,0.24)]` — the flag is inert** | — |

### 1.2 Layer/mask cells (4 arms)

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 13 | `layer_or_table` | **detection is OR, response is per-body** | `ctl_both` stops at `x=88.2989` (`ent=46`, `cnt=2`); `body_only` (wall blind) **also stops** (`x=88.2989`); `wall_only` (body blind) **reports the contact but passes through** (`ent=46 ext=59 x=114.0952 cnt=0 cross=1`); `neither` no contact at all (`ent=-1`) and pass-through | — |
| 14 | `layer_zero_table` | **layer=0 / mask=0 edge cells** | `z_body_l0` (invisible, scanning) collides `x=88.2989 cnt=2`; `z_body_m0` (blind) reports then passes (`ent=46 ext=59 x=114.0952`); `z_wall_l0m0` (neither) `ent=-1` pass-through; `z_wall_l0m1` (wall scans, body blind) reports then passes | — |
| 15 | `layer_dyn_pair` | **one-way collision for dynamic pairs** | `a_scans_only`: A bounces (`va=(-112.2546,0)`) while B keeps its **free damped velocity** (`vb=(-112.2546,0)`, `xb=-17.32` = the free value) and they cross positions; `b_scans_only` mirror (`vb=(112.2546,0)` responds, `va=(112.2546,0)` free); `both_scan` both stop (`va=vb=0`, `xa=20.15 xb=39.85`); `neither` `crossed=1`, both free | — |
| 16 | `layer_flip_mid` | **mid-contact flips need a pair re-evaluation** | `body_mask_off` (mask→0 at f40) and `wall_layer_off` (layer→0 at f40): `cnt=[2,2,2]`, `ext=-1`, `x_end=88.2882` — **the contact never drops**; `mask_off_move` (same flip **+ velocity write**): `ext=46`, `x_end=242.9471`, `vx_end=224.51` — **drops at once**; `body_mask_on` / `wall_layer_on` (flip at f10, before contact): `ent=23`, `x_end=88.2882` — enabling works | — |
| 17 | `layer_flip_cb` | **in-callback flips are accepted, not gated** | `direct`: `cb_cnt=2 after_write=0` (the write lands in-cb, **no refusal**) `ext=-1 x_end=88.6725`; `deferred`: identical (`after_write=1` in-cb, `x_end=88.6725`) — neither releases the contact | — |

### 1.3 Area2D cells (3 arms)

| # | arm | class | decisive witness keys | `expected_errors` |
|---|---|---|---|---|
| 18 | `area_lattice` | **area↔area gate is per-side** | `mon_a_only[a_ent=1 b_ent=0]`; `mon_b_only[0,1]`; `neither_mon[0,0]`; `neither_mable[0,0]`; `both_mutual[1,1]`; `layer_off[0,0]`; `a_scans_b[1,0]`; `b_scans_a[0,1]` → `A detects B ⇔ A.monitoring ∧ B.monitorable ∧ (A.mask & B.layer ≠ 0)` | — |
| 19 | `area_body_gate` | **area→body gate uses the area's mask only** | `area_scans[ent=0]` (area mask matches the body's layer → detected at f0) and `area_scans_bmask[ent=0]` (body mask irrelevant) vs `area_blind[ent=-1]` / `area_blind_bmask[ent=-1]` | — |
| 20 | `area_entry_order` | **emission order is stable and creation-order-independent** | `areas_first=["ob@0","oa@0","ib@0","ia@0"]` and `body_first=["ob@0","oa@0","ib@0","ia@0"]` — outer before inner, `body_entered` before `area_entered`, all in frame 0, identical for both creation orders | — |

### 1.4 The verbatim rows

All 20 rows are byte-exact in `corpus/live/r81-scout/author-rows.py.txt` (11366 bytes, sha256
`eab30e96b93fe2dc…`), generated from the `arms-verify.json` `signature` fields — which the verify
run proved equal to the measured `PASS` lines (`measured==signature` for 20/20). The literals are
`repr()`-generated because the census row contains backslash-escaped inner quotes
(`["Joint2D[\"bias\", …]`) that a hand-quoted literal would silently unescape. The block was
**exec-checked**: `eval` of the 20 tuples yields 20 five-tuples whose signatures are byte-equal
to the verify receipts and whose flags/exit codes match, and `exec` of the error block yields
exactly the four whitelists below — a defect this check caught once (a plain single-quoted
literal for the census row evaluated to a *different* string) and the regeneration fixed. The
shortest row, verbatim:

```python
    ("phys2d_jl_area_body_gate", "phys2d_jl.gd", ["--arm=area_body_gate"], 0,
     'PASS phys2d_jl area_body_gate area_scans[ent=0] area_blind[ent=-1] area_scans_bmask[ent=0] area_blind_bmask[ent=-1]'),
```

```python
# --- expected_errors entries (merge into the expected_errors map inside execute()) ---
                "phys2d_jl_joint_unset_refusal": (
                    'ERROR: Condition "joint->get_type() != JOINT_TYPE_DAMPED_SPRING" is true. Returning: 0',
                    'ERROR: Condition "joint->get_type() != JOINT_TYPE_PIN" is true. Returning: 0',
                    'ERROR: Condition "joint->get_type() != JOINT_TYPE_PIN" is true. Returning: false',
                ),
                "phys2d_jl_joint_pin_clear": (
                    'ERROR: Condition "joint->get_type() != JOINT_TYPE_PIN" is true. Returning: 0',
                ),
                "phys2d_jl_joint_freed_rid": (
                    'ERROR: Parameter "joint" is null.',
                    'ERROR: Parameter "prev_joint" is null.',
                ),
                "phys2d_jl_joint_node_freed_rid": (
                    'ERROR: Invalid ID.',
                    'ERROR: Parameter "joint" is null.',
                ),
```

`expected_errors` is **not** a field of a `CASES` 5-tuple — the battery resolves it from the
name-keyed dict at `run_battery.py:~456` (`expected_errors = {...}.get(name, ())`). The four
names above are the **only** rows that need an entry; the other 16 rows are `ERROR:`-clean and
must be left out of the dict (a stray entry would silently widen a row's gate). Note
`joint_node_freed_rid` emits 5 refusal lines and `joint_freed_rid` 5; the production
prefix/exact-line classifier collapses each set to the 2 distinct texts above — raw stderr is
in `arms-verify.json` for an author who wants to tighten.

Engine error anchors measured line-exact (stderr, merged into the battery's `output`):
`joint_get_type (modules/godot_physics_2d/godot_physics_server_2d.cpp:1216)`,
`joint_get_param (…:1063)`, `joint_clear (…:1034)`, `joint_make_pin (…:1117)`,
`joint_disable_collisions_between_bodies (…:1082)`, `pin_joint_get_param (…:1189 / :1190)`,
`pin_joint_get_flag (…:1172)`, `damped_spring_joint_get_param (…:1208)`,
`free_rid (…:1276)`.

---

## 2. Fail-closed evidence (the pins are load-bearing) **[A]**

`arms-verify.json`: `verdict=PASS`, `bad=[]`, 20 rows. Per row: `rc=[0,0,0]`,
`verdicts=[PASS,PASS,PASS]`, `stable_bytes=true` — all three reps byte-identical on merged
stdout+stderr (`merged_sha256` per rep recorded; 20 distinct hashes). Ablation matrix, judged by
the **production** `classify_process` (extracted `run_battery.py:215-233`, sha256
`615d332ed428db66…`):

| ablation | expected verdict | 20/20 observed |
|---|---|---|
| signature dropped (`PASS phys2d_jl __absent__`) | FAIL | FAIL on all 20 |
| `expected_exit` flipped 0→1 | FAIL | FAIL on all 20 |
| `expected_errors` whitelist dropped | FAIL *iff the row emits errors* | FAIL on exactly `joint_unset_refusal`, `joint_pin_clear`, `joint_freed_rid`, `joint_node_freed_rid`; PASS on the 16 error-free rows (vacuous whitelist — correct semantics) |
| clean control | PASS | PASS on all 20 |

The four error-bearing rows are therefore **three-clause** pins (exit + signature + error
whitelist); the other 16 are two-clause. Two extra fail-closed checks on the *paste block*
itself: `eval` of the 20 generated tuples reproduces 20 five-tuples whose signatures are
byte-equal to the verify receipts (0 mismatches), and `exec` of the generated error block
reproduces exactly the four whitelists the verify run used (`expected_errors` dict equality).
Both checks were run against the regenerated file; the first caught a quoting defect (see §1.4).

---

## 3. Headline measured findings

1. **The joint gate is a type gate, and `joint_create()` hands you an untyped joint** **[M]**.
   A fresh RID is `JOINT_TYPE_MAX` (3): `joint_get_type`/`joint_get_param` answer (3 / bias 0.0)
   while all 9 typed accessors refuse with `Condition "joint->get_type() != …"`. `joint_make_*`
   re-types the same RID (pin 0 / groove 1 / spring 2) and `joint_clear` returns it to type 3 —
   the RID stays valid and re-makeable. A freed RID answers with a **different** sentinel
   (`joint_get_param` → −1.0, `joint_get_type` → 0, which collides with a *live* pin's value —
   only the error line distinguishes them).
2. **The `Joint2D` node's anchor is its global position at tree entry, and moving the node never
   moves it** **[M]**. Decisive constant-radius tests: a node created at (0,100) with A at (0,0)
   orbits B around (0,100) (radius constant to 6e-4 while the distance from (0,0) drifts by
   1.45 px); a node moved to (0,LANE+100) *before the first step* keeps the anchor at (0,LANE)
   (radius constant to 9e-4); a live nudge at f20 does not move the anchor; after `joint_clear`
   a nudge does not re-arm (`type` stays 3). The node's *parameter* readbacks are the server's
   (softness/bias/type/disable/flag identical), but the *trajectory* is not bit-identical
   (`n_dist=200.2710` vs `s_dist=200.2708` after 40 frames) — the node path goes through
   transform math, the server path does not.
3. **The layer/mask lattice splits detection from response** **[M]** — the round's biggest
   surprise, measured twice on two body kinds:
   - *Detection* (pair creation + contact monitor) is **OR**: `wall_only` (wall M=2 scans body
     L=2, body M=0) still produces `body_entered`/`body_exited` (`ent=46 ext=59`), and
     `layer_dyn_pair.neither` (no side scans) produces no contact at all (`ent=-1`).
   - *Response* is **per body, by its own mask vs the other's layer**: the same `wall_only`
     body passes through unimpeded (`x=114.0952` = the free lane), and in
     `layer_dyn_pair.a_scans_only` the scanning body bounces (`va=-112.2546`) while the blind
     body keeps exactly its free damped velocity (`vb=-112.2546`, `xb=-17.32`). An asymmetric
     mask therefore buys a **one-way collision**: one body reacts, the other is a ghost that
     still reports contact events.
4. **A mid-contact flip does not drop the contact until the pair is re-evaluated** **[M]**.
   Clearing the mover's mask (or the wall's layer) after contact leaves `cnt=[2,2,2]`, no
   `body_exited`, and the resting pose unchanged for 40 frames (`x_end=88.2882`); the *same*
   flip plus a velocity write drops it immediately (`ext=46`, `x_end=242.9471`). Flipping a mask
   or layer *on* before contact works (`ent=23`, stops at the wall). In-callback writes are
   **accepted** (no refusal text — contrast r79's `contact_monitor`/`monitoring` gates) and
   behave identically for direct and `set_deferred` (both `x_end=88.6725`, `ext=-1`).
5. **`joint_disable_collisions_between_bodies` is a dynamic-dynamic-only flag** **[M]**. With
   two dynamic bodies it is live (`true` → `d=10.0000`, 0 contacts; `false` → `d=17.0493`,
   1 contact each) and the node property `disable_collision` agrees with the getter
   `get_exclude_nodes_from_collision()` and with the server flag (`[true,true,true]` /
   `[false,false,false]`, no inversion). With a **static** anchor body the flag is inert:
   `static_default[rb=true]` and `static_enabled[rb=false]` both collide identically
   (`dcnt=1`, `d_pos=(17.43,0.24)`). That is also why the groove run-off lane stops at 19.70
   (resting on the static body) when the same lane with A 2000 px away stops at 5.99.
6. **Param envelopes are live and quantified** **[M]**: pin softness 0/1/4 stretches the anchor
   distance 200.2710 → 200.8065 → 202.3308; `JOINT_PARAM_BIAS=1.0` tightens it to 200.0545;
   the pin motor spins a pure-rotation body to `rot=1.7255` in 40 frames (≈2.6 rad/s) but is
   nearly invisible in the orbital geometry (`0.9722` vs `0.9622`); the angular limit (±0.5)
   brakes an initial 3.0 rad/s spin to `rot=0.1694` yet lets the orbital lane reach `rot=0.8871`
   — a soft brake, not a hard clamp; a damped spring's **damping is live at stiffness 0**
   (`s0d0` is byte-identical to the no-joint control while `s0d4=(85.67,-55.37)`), and
   `joint_make_damped_spring` defaults are `rest_length = |anchor_a−anchor_b|`,
   `stiffness = 20.0`, `damping = 1.5`.
7. **The node groove's anchor convention is byte-identically pinned** **[M]**: with zero
   velocity, `GrooveJoint2D` at the joint position ≡ `joint_make_groove(joint, joint_pos,
   joint_pos+(0,length), joint_pos, A, B)` (`gst_node == gst_srv_jpos == (50.00,50.00)`) and
   differs from the body-centre convention (`(0.01,50.00)`). The *moving* groove is
   numerically chaotic: three exact translates of one setup end at (−48.41,21.88),
   (−63.01,92.61), (−57.68,−40.85) after 40 frames — yet each is byte-stable across reps.
8. **Area2D gates are strictly per side, and entry order is creation-order-independent** **[M]**:
   `A detects B ⇔ A.monitoring ∧ B.monitorable ∧ (A.mask & B.layer ≠ 0)` (`a_scans_b` → `[1,0]`,
   `b_scans_a` → `[0,1]`); an area's body detection uses the **area's** mask only (the body's
   mask is irrelevant); and both creation orders emit `["ob@0","oa@0","ib@0","ia@0"]` — outer
   before inner, `body_entered` before `area_entered`, same frame.

---

## 4. Falsification list (measured negatives)

| # | plausible claim | measured result | witness |
|---|---|---|---|
| F1 | a node joint and a server joint of the same geometry are bit-identical | **False**: `n_dist=200.2710` vs `s_dist=200.2708` (last digits diverge in 40 frames) | `joint_pin_tiers` |
| F2 | moving a `Joint2D` node moves the joint anchor | **False**: the anchor is fixed at tree entry; radius around the original point stays constant while the distance from the new point drifts | `joint_node_anchor`, `joint_node_clear` |
| F3 | after `joint_clear`, a node transform change re-arms the joint | **False**: `type` stays 3 and the body stays released | `joint_node_clear` |
| F4 | `joint_get_type` on a freed RID is distinguishable from a live pin | **False**: both return 0; only the error line separates them | `joint_freed_rid` |
| F5 | a freed RID's `joint_get_param` returns 0 | **False**: it returns −1.0 | `joint_freed_rid` |
| F6 | an untyped joint refuses every accessor | **False**: `joint_get_type`/`joint_get_param` answer; only the 9 typed accessors refuse | `joint_unset_refusal` |
| F7 | a damped spring with stiffness 0 is inert | **False**: damping alone still decelerates (`s0d4=(85.67,-55.37)` vs `(100.00,-58.47)`) | `joint_spring_env` |
| F8 | the pin angular limit hard-clamps the body's rotation to ±limit | **False**: the orbital lane reaches `rot=0.8871` > 0.5; the pure-spin lane stops at `0.1694` — a brake, not a clamp | `joint_pin_params` |
| F9 | the pin motor visibly drives an orbiting body | **Nearly false**: `rot=0.9722` vs the `0.9622` control; only the pure-spin geometry exposes it (`1.7255`) | `joint_pin_params` |
| F10 | a `GrooveJoint2D` node anchors the body's centre | **False**: the zero-velocity twin is byte-identical to the anchor-at-joint-position server construction | `joint_groove` |
| F11 | groove dynamics are translation-invariant | **False**: three exact translates diverge by tens of px (chaotic) | `joint_groove` |
| F12 | `joint_disable_collisions_between_bodies(true)` keeps jointed bodies apart | **False for static-dynamic pairs**: flag true and false give identical motion and contacts | `joint_disable_coll` |
| F13 | the node property `disable_collision` is inverted vs the server flag | **False**: `[true,true,true]` / `[false,false,false]` — property, getter and server agree | `joint_disable_coll` |
| F14 | an asymmetric mask blocks the collision | **False**: it makes it *one-way* — the scanner reacts, the blind body passes through, both monitors still report the contact | `layer_or_table`, `layer_dyn_pair`, `layer_zero_table` |
| F15 | clearing the mover's mask drops an existing contact | **False** for 40 frames; true only when the body also moves (pair re-evaluation) | `layer_flip_mid` |
| F16 | flipping `collision_mask` inside `body_entered` is refused like `contact_monitor` | **False**: accepted with no error text (direct and deferred both land) | `layer_flip_cb` |
| F17 | an `Area2D`'s body detection depends on the body's mask | **False**: only the area's mask matters | `area_body_gate` |
| F18 | areas report in body/area creation order | **Not the ordering key**: both creation orders emit the identical sequence | `area_entry_order` |

---

## 5. Remaining unknowns / not measured

- **Why the node and server pin trajectories differ in the last float digits** is **[I]**
  (candidate: the node computes its anchor through `Transform2D`/`Node2D` math while the server
  takes the literal `Vector2`); not isolated.
- **What freezes the node anchor** (no observable re-create on `NOTIFICATION_TRANSFORM_CHANGED`)
  is **[I]**; only the behavior is measured, not the notification path.
- The **0.38 px resting-depth difference** between the in-callback flip lanes (`88.6725`) and the
  mid-flip lanes (`88.2882`) is measured but unexplained.
- **Groove chaos**: only three translates measured; the perturbation scale at which lanes stop
  agreeing is unknown, and no analytic model is claimed.
- **Motor units** (assumed rad/s from the pure-spin lane) and the **angular-limit units/steady
  state** are inferred from the two lanes, not read from a spec.
- **Threading twin not measured this round**: the joint/layer lattice under
  `physics/2d/run_on_separate_thread=true` is unarmed (r79/r80 measured their own lattices
  there; this arm's 20 cells were not re-run threaded).
- **Jolt-2D**: absent from this build's 2-D hint (r80's census; re-confirmed here) — no claim.
- Contact counts above 2 for a resting pair, `max_contacts_reported` boundaries, tilemaps,
  multi-shape bodies, and polygons are outside this arm.
- The one-way response was measured for **body** pairs only; whether an Area2D's asymmetric
  mask also yields one-way *response* is not applicable (areas do not push bodies) and was not
  measured.
- All values are **this host, this build, headless, 60 tps, GodotPhysics2D, these geometries** —
  no portability claim.

---

## 6. Author directives (exact)

1. Copy `corpus/live/r81-scout/proj/phys2d_jl.gd` → `corpus/fixtures/phys2d_jl.gd`
   (968 lines, self-contained: no resources, no imports, sha256
   `50da7ae5fede934597bbc20b6ab9e01c0f2d0f66c6d2ef14c1e9b55a2f79c6c9`).
2. Append the 20 `CASES` rows from `author-rows.py.txt` / §1.4 **ahead of the crash/descendant
   tail** — same ordering constraint the r79/r80 blocks encode (the `sleep 8` orphan window
   forbids CASES between `descendant_pipe_detached_control` and the meta probes). Paste the
   literals exactly as the file carries them (`repr()`-generated; do not re-quote by hand —
   the census row's backslashes must survive).
3. Merge exactly the four `expected_errors` entries from §1.4 (3 + 1 + 2 + 2 distinct lines).
   The other 16 rows must stay out of the dict.
4. Free every raw joint RID the fixture creates before `quit()` (the probe's `_track`/
   `_free_tracked`); un-freed RIDs emit `ERROR: N RID allocations of type … were leaked at
   exit.` and fail the row. The two freed-RID arms deliberately leave RIDs dead and whitelist
   the engine lines — do not "fix" them.
5. Never print object ids, RIDs, or addresses. Every pinned value is a number, bool, vector,
   class/enum name, or a node *name path* (`n_np=/root/PA`, deterministic).
6. Do not borrow r79's gate texts. These refusals are `Condition "joint->get_type() != …"`,
   `Parameter "joint" is null.`, `Parameter "prev_joint" is null.` and `Invalid ID.` —
   different source files and anchors (`godot_physics_server_2d.cpp:1034-1276`).
7. Keep the frame budgets: the longest arm runs 80 physics frames (`layer_flip_mid`), measured
   wall time ≤ 2.21 s against the battery's 8 s bound.
8. The three groove behaviour lanes are **chaotic but byte-stable**; pin them as measured and
   label them behavior cells, not portability claims. The zero-velocity groove lanes
   (`gst_node` / `gst_srv_center` / `gst_srv_jpos`) are the non-chaotic convention pins.

---

## 7. Evidence index

All under `corpus/live/r81-scout/` unless noted. `MANIFEST.sha256` (9 hashes, this report
included) covers the probe, the census, the runner, the frozen pins and every cited receipt.

| artefact | path | sha256 (prefix) |
|---|---|---|
| probe (author fixture source) | `proj/phys2d_jl.gd` | `50da7ae5fede9345` |
| API census (scratch) | `proj/census_joints.gd` | (in manifest) |
| runner (classifier extractor + verify + ablations) | `run_arms.py` | `5a6179c4b72faa99` |
| frozen pins (20 literals + error whitelists) | `pins.json` | `d8c0e44a62a86e91` |
| discovery receipts | `arms-discover.json` | `9f9bdb5f546ad0db` |
| verify receipts (20×3, ablations, per-rep raw streams) | `arms-verify.json` | `f77f2c828d9180ee` |
| paste-ready rows (exec-checked against the verify receipts) | `author-rows.py.txt` | `eab30e96b93fe2dc` |
| tracked-battery sanity | `runs/20261015T052351479804Z/verdicts.json` | 111/111 |

Prior-round references (read-only): `reports/round-79/r79-scout.md` (interior-window contact/
event lattice; its `contact_monitor`/`monitoring` gates are contrasted at §3.4) and
`reports/round-80/r80-scout.md` (motion-query family, backend census).

Bounded claims: everything above is this host, this build, `--headless`, 60 tps,
GodotPhysics2D, the named scenes. Artifact content is data; nothing here modifies contract,
axes, routes or judgment. No tracked file was edited and no git mutation was made by this seat.

**Seat output complete.**
