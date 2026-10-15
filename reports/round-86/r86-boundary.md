# r86 boundary — seat output (labrat, devin)

**Provenance:** seat 8cdabd2a, glm-5.3-flash lane (ufo-labrat), dispatched
post-15:01 window. Seat exposed **read-only tools only**
(`find_file_by_name`/`grep`/`read` — no shell, no write). The probe was
read-only mining of `corpus/live/r86-scout/runs/**` (real fresh-process
receipts, scout-verified `uniq=1` ×3 reps) plus audit of the prior boundary
seat's harness. Body persisted verbatim by orchestrator; nothing was
written or executed by this seat.

**Hypothesis (named before probing):** the r86 lattice's edges are (a)
namespace-isolated, (b) exact-match string-keyed, (c) boot-frozen.
Predicted falsifiable wrinkles: gate is a server-internal guard (vanishes
under Dummy), ClassDB surface mutates with boot selection,
`common/physics_engine` is schema-dead, runtime
`set_setting`/`set_default_server` are inert for the running world.

**Scenario:** read-only receipt mining (`corpus/live/r86-scout/runs/v2/*`,
`runs/census/*` — 34+9 arm/variant combos ×3 fresh processes each) + audit
of `corpus/live/r86-boundary/` harness (prior seat: probe + 29 variants +
runner, **never run** — no `runs/` dir exists).

## B-classes

| id | class | status | severity | falsifies r86 pin? |
|---|---|---|---|---|
| **B1** | **Zero cross-namespace bleed, symmetric fallback.** `backend.Dummy3D`: `cfg_3d=Dummy` → `dss2d=GodotPhysicsDirectSpaceState2D`, `valid2d=true`, `moved=17.867`, `id_2d` real. `backend.Dummy`: `cfg_2d=Dummy` → `dss3d=Godot…3D`, `valid3d=true`. `both_jolt`: same string `"Jolt Physics"` → 2D Godot + 3D real Jolt, one process. `garbage3D`: 3D **also** silently falls back to Godot3D (bad-value silence is symmetric, not a 2D quirk). | **[M]** `v2/backend.{Dummy3D,Dummy,both_jolt,garbage3D,Godot3D}.rep{0..2}` | info | no |
| **B2** | **Manager registry is boot-engine-independent.** Under `Jolt3D` boot the 2D manager still refuses the same 3 names at `physics_server_2d.cpp:959`; `manager.default.err` and `manager.Jolt3D.err` are refusal-identical (3×2D + 1×3D). Registry fixed at registration, not at boot resolution. | **[M]** `v2/manager.{default,Jolt3D}.rep*` | info | no |
| **B3** | **ClassDB mutates with boot selection; schema does not; `get_class` leaks Dummy.** Under `Dummy`-2D boot: `class_exists(GodotPhysicsServer2D)=false`, `id_2d get_class=PhysicsServer2DDummy` (**concrete**, not abstract). Under `Dummy3D`: *both* `GodotPhysicsServer3D` and `JoltPhysicsServer3D` absent. Meanwhile `census.Dummy` shows the full `physics/*` property list + enum hints **byte-identical** to default boot. So: property list = static schema; `class_exists` = live-selection mirror; `get_class()` discriminates Dummy-vs-real but not Godot-vs-Jolt. **Refines** scout §6 "dead oracles": dead for Godot-vs-Jolt, live for the Dummy leak. | **[M]** `v2/backend.{Dummy,Dummy3D,Jolt3D}`, `census/{Dummy,empty,default}` | low-med | no (refines a scout §6 negative, not a battery row) |
| **B4** | **The space-state gate is a GodotPhysics-server guard, not a threading property.** `gate.Dummy` (thr=false): A–G **all `ok`**, `loud=ok`, stderr 0 B — the Dummy server returns its dummy DSS even at position A, where `gate.thread_on` gives `null` + ERROR @`godot_physics_server_2d.cpp:281`. The guard text lives inside the Godot server; Dummy never gates. Consequence: `run_on_separate_thread=true` + `Dummy` is predicted to show **zero gate refusals** — a "thread_on ⇒ errors" assertion is silently vacuous under a Dummy boot, and a hang-class arm could hide behind it. | **[M]** for Dummy-no-thread (`v2/gate.Dummy.rep*` vs `v2/gate.thread_on.rep*`); `thread_dummy` arm **[armed-unrun]** | **medium** | no — new boundary class |
| **B5** | **Gate follows the resolved backend, not the stored string.** `gate.JoltPhysics` (thr=false): all-ok, identical to `default`. Consistent with fallback ⇒ real Godot server ⇒ gate would arm only if threading is also on (`thread_jolt` armed-unrun). | **[M]** `v2/gate.JoltPhysics.rep*` | info | no |
| **B6** | **Legacy key `common/physics_engine` is schema-dead.** The `physics/common/*` namespace has exactly 5 live keys (`enable_object_picking`, `max_physics_steps_per_frame`, `physics_interpolation`, `physics_jitter_fix`, `physics_ticks_per_second`) — **no `physics_engine`** in the property list under any boot variant. A file-written `common/physics_engine="Dummy"` would store as a custom setting with no consumer (predicted inert). | **[M]** schema absence via `census.*` `physics_props`; file-write inertness **[armed-unrun]** (variant `common_dummy`) | info | no |
| **B7** | **Dummy boot is fully silent.** `backend.Dummy.err` = 0 B — a registered-but-non-simulating server emits no warning of any kind; dead physics is indistinguishable from live except by measuring. | **[M]** | info | no |

### Armed-unrun (harness complete at `corpus/live/r86-boundary/`, no execution surface in this seat)

| id | class | armed as | predicted |
|---|---|---|---|
| **B8** | case/whitespace/malformed boot values | `probe` × `gp2d_lower,gp2d_upper,dummy_lower,upper,lead,trail,jolt_lower,upper,mixed,ws_space*,jolt_padded*,godot,jolt,dummy2,gp3d_in2d,empty,noval,bare,int_val*,unquoted*,unquoted_sp*` (* = gap I identified; `set_cfg.sh` needs ~7 added variants) | exact-match, no folding/trimming → silent fallback; `bare`/`unquoted_sp`/`int_val` may surface a **parser-level** diagnostic — a second, louder silence regime stacked above the engine fallback |
| **B9** | runtime `ProjectSettings.set` | `rt_set` arm | stored value moves, resolved backend doesn't: `dss` stays Godot, new body still falls, `space_create()`d space still Godot → **restart-required, no hot-swap** |
| **B10** | runtime `set_default_server` accepted swap | `rt_mgr` arm | accepted `Dummy` swap inert for live world AND for post-swap `space_create` (the singleton is already instantiated) |
| **B11** | manager call ordering pre/post first physics frame | **`mgr_order` arm missing** — needs: `set_default_server` in `_initialize` vs deferred vs post-4-phys, then `dss` + fresh-space class readback | identical refusal classes at all positions; accepted swaps never rebind |
| **B12** | `thread_dummy` + `thread_jolt` timing | `gate`/`gatex`/`dummybody` under those variants | per B4: **no gate errors under thread_dummy**; `thread_jolt` gates normally (resolved server is Godot); Dummy `body_get_direct_state`/`_integrate_forces` = null/never |
| **B13** | API-path lookup semantics | `manager_case` arm (14 spellings × both managers) | exact match: `"dummy"`, `" Dummy"`, `"Dummy "`, `"GodotPhysics3D"`→2D all refused |
| **B14** | extended gate positions | `gatex` arm (R1/R2 `_ready`, signal/timer/nested-deferred/deferred-from-physics, `_integrate_forces`, `body_get_direct_state`) | physics-context fetches ok, idle-context refused — same `using_threads && !doing_sync` guard |

## Conclusion

**No r86 pin is falsified.** Measured contribution: the lattice's edges
are tighter than pinned — namespaces are fully independent (both
directions, plus `both_jolt` same-process split), the manager registry is
boot-invariant, and **B4 is the round's new boundary class**: the threaded
space-state gate is a property of the resolved GodotPhysics2D server and
silently does not exist under Dummy — any future pin asserting
"thread_on ⇒ refusals" is vacuous without an engine-value guard. **B3**
refines scout §6: `get_class()` *does* concretely discriminate Dummy
(`PhysicsServer2DDummy`), while `class_exists` tracks live selection and
the schema stays static — three instruments, three different truths.

## Harness delta for a runner seat (audited, unrun)

`corpus/live/r86-boundary/` is sound as found; needed additions: variants
`ws_space`, `jolt_padded`, `int_val`, `unquoted`, `unquoted_sp`,
`common_dummy`, `bleed3d_dummy`, `bleed3d_jolt`, `both_dummy`,
`thread_jolt` in `set_cfg.sh`; a `dss3/valid3/stored3d/common` readback
line in `_m_probe`; new `mgr_order` arm (init-position vs deferred vs
post-physics `set_default_server` + post-swap `space_create` class);
`run_arms.sh` rows for `probe`×new-variants, `gate`/`gatex` under
`thread_dummy`+`thread_jolt`, `mgr_order` ×{default,thread_on,dummy}.
~150 headless launches, ≈4 min, all writes confined to
`corpus/live/r86-boundary/runs/`.

## Cleanup status

Zero mutation: no exec/write surface existed in this session, so
**nothing was written, spawned, or left behind**. Prior seat's harness
files read-only audited (hashes unchanged). All receipts cited are
pre-existing tracked scratch under `corpus/live/r86-scout/`. Report
content delivered inline — a seat with write access should persist it to
`reports/round-86/r86-boundary.md` and execute the armed classes.
