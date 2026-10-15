# game-dev-2d round 86 — scout (r86-scout): does Godot 4.7.2 ship godot-jolt as a **2D** physics engine option?

Seat `SCOUT` (LEAF) | lane `r86-scout` | round 86 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, pacman pkg
`godot 4.7.2-1`, 182 015 704 B), Python 3.14.7, 32 CPUs.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`27f465c`** (*r80 LOG: ADMIT-corr*).
`DisplayServer.get_name() == "headless"` for every receipt in this report.

**No git mutation, no tracked file written, no subagent, no commit.** Writes are this report
and `corpus/live/r86-scout/**` only. `git status --porcelain` shows exactly two modified
tracked files — `SCORECARD.md` (mtime 01:47:47) and `corpus/fixtures/run_battery.py`
(mtime 03:50:30) — **both pre-date this seat's session (started ≈04:14)** and are not mine;
the tracked fixtures were only *executed* (from byte-identical scratch copies, §6/F8).

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this session and no
GDScript/Python language server is installed, so `definition`/`references`/`hover`/
`type_definition`/`implementation` were **unavailable for every file touched here**. Semantic
carriers are therefore (a) fresh-process execution receipts, (b) `ClassDB`/`ProjectSettings`
runtime introspection, and (c) static census of the engine binary's own strings. Where this
report names a C++ symbol or file:line it is quoting **engine-emitted error text or binary
strings**, never a grep of engine source. No engine source tree is present on this host.

**Prior-seat scratch audit (`corpus/live/r86-scout/`, pre-existing).** A previous r86 scout died
on rate limit. Audited and dispositioned:

| artefact | verdict |
|---|---|
| `proj/r86_probe.gd` (`a8f829924a7a595e`) — census / ps2dmanager / thread_ids / engine_readback arms | **sound, reused**; its `engine_readback` arm supplied the first `space_valid` split (Dummy vs rest) |
| `set_cfg.sh` (`a81ae8845958f660`) | sound; extended (not overwritten) by `set_cfg2.sh`, which adds the 3D positive controls |
| `arms/slice_*.{default,JoltPhysics,thread_on}.rep{0,1,2}.log` — 54 logs | **sound and independently reproduced** (§4); all 18 (slice,variant) combos are `uniq=1` across 3 reps |
| `census` / `ps2dmanager` arms | **gap — no receipts existed** (died before running). Both run by this seat (§2) |
| `thread_ids` arm | **superseded.** It measures `OS.get_thread_caller_id()` inside callbacks and returns `body_integrate=1` for both settings — that is *not* the observable of this setting (§5). Reading it as "inert" would have been wrong |
| scratch slice variant set | **incomplete**: no `Dummy` column. Added here — and it exposed a timeout class (§4.3) |

Nothing in the scratch was found false; one *interpretation* was pre-empted.

---

## 0. What I ran

| protocol | scope | receipts |
|---|---|---|
| **v2 arms**, fresh process ×3 each | `backend` ×12 variants, `manager` ×3, `gate` ×4, `threads` ×2, `boot --nofetch` ×2 | `runs/v2/` (315 files) |
| **one-fetch-per-process** attribution, ×3 each | `gate_one` ×6 positions ×2 threading variants | `runs/v2/gate_one.*` |
| **prior-seat census + manager arms**, fresh process ×3 each | `census` ×7 variants, `ps2dmanager` ×2 | `runs/census/` (81 files) |
| **pinned-law slices**, fresh process ×3 each | 6 tracked laws × 4 variants | `runs/slices/` (288 files) |
| **4-axis compact slice**, fresh process ×3 each | ccd / joints / queries / damping × 4 variants | `runs/slice4.*` (36 files) |
| static census of the engine binary | Jolt/GodotPhysics symbol inventory | `runs/static_strings.txt` |

Runners: `run_v2.sh`, `run_slices.sh`, `set_cfg2.sh`. Analyzers: `analyze_v2.py`,
`analyze_slices.py`. Probes: `proj/r86_probe2.gd` (`7e4fd2a1edf26757`),
`proj/r86_slice4.gd` (`fc222938fdfcfb5e`), plus the audited prior-seat
`proj/r86_probe.gd` (`a8f829924a7a595e`) re-run for the census receipts.

**Byte-stability: 0 unstable (arm,variant) pairs.** All 34 combos in `runs/v2/` have
`out_uniq=1`, `err_uniq=1`, single `rc` across 3 fresh processes; all 9 census/manager combos in
`runs/census/` likewise; all 24 combos in `runs/slices/` are `uniq=1`; all 4 `slice4` variants
are `uniq=1`. `analyze_v2.py` prints `UNSTABLE_COUNT=0`.

---

## 1. Headline answer

**No — Godot 4.7.2 (Arch build) does not ship godot-jolt as a 2D physics engine option.**
Jolt is present in this build as a **3D-only** backend. The 2D engine enum has **three**
values; the 3D enum has **four**, and `Jolt Physics` appears only in the 3D one.

```
physics/2d/physics_engine  hint_string = DEFAULT,GodotPhysics2D,Dummy
physics/3d/physics_engine  hint_string = DEFAULT,Jolt Physics,GodotPhysics3D,Dummy
```

`physics/jolt_physics_3d/**` — **32** properties exist (`simulation/position_steps`,
`limits/max_bodies`, `motion_queries/recovery_iterations`, …). `physics/jolt_physics_2d/**` —
**zero**. Of the 67 `physics/*` settings this build exposes, **15** are `physics/2d/*` and
**32** are Jolt-3D; there is no 2D Jolt settings namespace, no 2D Jolt server class, and no 2D
Jolt symbol in the binary.

Because Jolt-2D does not exist, the question's first branch is unreachable. This seat instead
ran the nearest realizable experiment — **the literal string `"Jolt Physics" installed as the
2D engine value at boot** — plus the refusal-class and manager measurements the question asks
for on the absent branch.

**This confirms a fact r77's scout already recorded** (`reports/round-77/gd-scout.md` §3.1:
*"there is no `Jolt Physics` 2D backend on this build"*, and re-confirmed as a census side-note
by r80/r81/r84/r85). **What is new here** is everything that makes the absence *load-bearing*
rather than incidental: the refusal class (§3), the manager advertisement (§2.2), the
same-process same-name 3D control (§2.3), the live-backend-class discriminator (§2.4), and the
pinned-law divergence map (§4). No prior round set `"Jolt Physics"` in 2D and measured what
happens — `grep -rn 'Jolt Physics' --include=project.godot corpus/` returns **zero** hits
before this round.

---

## 2. The census — five independent instruments, all agreeing

### 2.1 `ProjectSettings.get_property_list()` **[M]**

```
R86 prop name=physics/2d/physics_engine type=4 hint=2 hint_string=DEFAULT,GodotPhysics2D,Dummy
R86 prop name=physics/3d/physics_engine type=4 hint=2 hint_string=DEFAULT,Jolt Physics,GodotPhysics3D,Dummy
R86 prop name=physics/2d/run_on_separate_thread type=1 hint=0 hint_string=
R86 prop name=physics/3d/run_on_separate_thread type=1 hint=0 hint_string=
```

`type=4` = `TYPE_STRING`, `hint=2` = `PROPERTY_HINT_ENUM`: the engine value is a **string
carrying an enum hint**, not an integer index. `DEFAULT` is the shipped value in every variant
that does not name an engine.

### 2.2 `PhysicsServer2DManager` — what it actually advertises **[M]**

```
R86B PhysicsServer2DManager_own_methods=register_server:inst,set_default_server:inst
R86B PhysicsServer3DManager_own_methods=register_server:inst,set_default_server:inst
R86B PhysicsServer2DManager_singleton=true
R86B PhysicsServer2DManager has_method_get_servers_count=false
R86B PhysicsServer2DManager has_method_get_server_count=false
R86B PhysicsServer2DManager has_method_get_server_name=false
R86B PhysicsServer2DManager has_method_find_server_id=false
R86B PhysicsServer2DManager has_method_has_server=false
```

- The manager is an Engine singleton and is `ClassDB.class_exists == true`, but it exposes
  **exactly two** script-bound methods. Both are bound as **instance** methods even though the
  C++ declarations are `static` (the probe tests `METHOD_FLAG_STATIC = 32`, the value from
  `core/object/object.h`, and the flag is clear on both).
- **The registered-server list is not enumerable from GDScript.** `get_servers_count`,
  `get_server_name`, `find_server_id` and `has_server` all report `has_method=false`; r77's
  `PS2DMGR methods=["register_server","set_default_server", …]` was an elided list, now
  closed: there is no third method. The **only** script-visible enumeration of 2D engines is
  the `ProjectSettings` enum hint in §2.1.
- The refusal itself is therefore the only dynamic oracle, and it is precise (§2.3).

### 2.3 The decisive controlled comparison — same name, same process, two managers **[M]**

`set_default_server(name, priority)` was called for each name on both managers with
`priority=100`, and the engine's own refusal was counted by source location:

| name offered | 2D manager | 3D manager |
|---|---|---|
| `GodotPhysics2D` | **accepted** (no error) | — |
| `Dummy` | **accepted** (no error) | **accepted** |
| `Jolt Physics` | **REFUSED** | **accepted** (no error) |
| `garbage_xyz` | **REFUSED** | **REFUSED** |
| `""` (empty) | **REFUSED** | — |
| `GodotPhysics3D` | — | **accepted** |

Refusal text, verbatim:

```
ERROR: Condition "id == -1" is true.
   at: set_default_server (servers/physics_2d/physics_server_2d.cpp:959)
ERROR: Condition "id == -1" is true.
   at: set_default_server (servers/physics_3d/physics_server_3d.cpp:1193)
```

Counts per run (3 fresh processes, `uniq=1`): **2D-manager refusals = 3**
(`Jolt Physics`, `garbage_xyz`, `""`), **3D-manager refusals = 1** (`garbage_xyz`).

**Therefore the 2D registered set is `{GodotPhysics2D, Dummy}` and the 3D registered set is
`{Jolt Physics, GodotPhysics3D, Dummy}`.** The identical string `"Jolt Physics"` is *accepted*
by the 3D manager and *refused* by the 2D manager inside the same process, through the same
call shape. This is the strongest available statement of the answer: the engine's own registry
has no Jolt 2D entry, and the same name is live one dimension over.

### 2.4 Which backend is actually live — with a working positive control **[M]**

The `PhysicsServer2D`/`PhysicsServer3D` singletons are useless for this: `get_class()` returns
the abstract bound name (`PhysicsServer2D`) and `is_class("GodotPhysicsServer2D")` is **false**
even when GodotPhysics2D is running. Likewise `ClassDB.class_exists` is *selection-dependent*:
`GodotPhysicsServer3D` exists=true under DEFAULT and flips to **false** under Jolt-3D, while
`JoltPhysicsServer3D` flips false→true. The one instrument that discriminates is the **live
`World2D.direct_space_state` concrete class**:

| 2D engine value | value read back | `dss2d_class` | `space2d_valid` | rc | stderr |
|---|---|---|---|---|---|
| `DEFAULT` | `DEFAULT` | `GodotPhysicsDirectSpaceState2D` | true | 0 | 0 B |
| **`Jolt Physics`** | **`Jolt Physics`** | **`GodotPhysicsDirectSpaceState2D`** | true | 0 | **0 B** |
| `Dummy` | `Dummy` | **`PhysicsDirectSpaceState2DDummy`** | **false** | 0 | 0 B |
| `garbage_xyz` | `garbage_xyz` | `GodotPhysicsDirectSpaceState2D` | true | 0 | 0 B |
| `""` | `` | `GodotPhysicsDirectSpaceState2D` | true | 0 | 0 B |
| `GodotPhysics2D` | `GodotPhysics2D` | `GodotPhysicsDirectSpaceState2D` | true | 0 | 0 B |

and the 3D twin, which is the **positive control**:

| 3D engine value | `dss3d_class` |
|---|---|
| `DEFAULT` / `GodotPhysics3D` / `garbage_xyz` | `GodotPhysicsDirectSpaceState3D` |
| `Dummy` | `PhysicsDirectSpaceState3DDummy` |
| **`Jolt Physics`** | **`JoltPhysicsDirectSpaceState3D`** |

The instrument is live: it names a Jolt backend the moment one is actually installed
(`Jolt3D`, and `both_jolt` where the 2D value is *also* `"Jolt Physics"`), and it names a
distinct class (`…2DDummy` / `…3DDummy`) the moment a *different* backend is installed in
either dimension. Under `"Jolt Physics"` in 2D it names the Godot class. This is a
within-process, single-variable comparison across twelve variants.

### 2.5 Static census of the engine binary **[M]**

```
Jolt*2D symbols : 0
Jolt*3D symbols : 43
JoltPhysicsServer3D            : present
JoltPhysicsServer2D            : ABSENT
GodotPhysicsServer2D           : present
_createGodotPhysics2DCallback  : present   (the 2D server factory)
_createGodotPhysics3DCallback  : present
modules/jolt_physics/*         : every source path ends in _3d
                                 (jolt_physics_server_3d.cpp, jolt_body_3d.cpp,
                                  jolt_pin_joint_3d.cpp, jolt_area_3d.cpp, …)
```

No `Jolt*2D` symbol of any kind exists in the binary; every Jolt symbol is 3D-suffixed. This is
consistent with upstream godot-jolt being a 3D-only module and closes the question at the
binary level as well as at the API level.

---

## 3. The refusal class, measured precisely

The question asks: **bad enum value → silent clamp vs error vs fallback?** The answer is that
the two entry paths *disagree*, and the boot path is the quiet one.

| stage | observation |
|---|---|
| **stored value** | **not clamped.** `ProjectSettings.get_setting("physics/2d/physics_engine")` returns the file's bytes verbatim: `Jolt Physics`, `garbage_xyz`, `` (empty). An empty string is preserved as empty, not normalised to `DEFAULT`. |
| **boot / file path** | **silent fallback.** For every one of `Jolt Physics`, `garbage_xyz`, `""`, `Dummy`, `GodotPhysics2D`, `DEFAULT`: **`stderr` = 0 bytes, rc = 0**, and a live GodotPhysics2D runs (`space2d_valid=true`, a dropped body falls `moved=17.867` — byte-identical across all six). No `ERROR`, no `WARNING`, no diagnostic of any kind. |
| **explicit API path** | **loud typed refusal.** `PhysicsServer2DManager.set_default_server("Jolt Physics", 100)` emits `Condition "id == -1" is true. at: set_default_server (servers/physics_2d/physics_server_2d.cpp:959)` and performs no swap. |

So: **silent fallback at boot, loud refusal through the manager API** — and the same bad value
takes a different branch depending on which door it enters. Note the consequence for anyone
auditing a project file: a `physics/2d/physics_engine` value that names nothing is
**indistinguishable from `DEFAULT` by any runtime signal** (rc, stderr, `space2d_valid`,
`dss2d_class`, and the simulated result are all identical to DEFAULT). The value is only
observable by *reading it back* and comparing against the enum hint.

The mechanism behind the split is **bounded, not proven** **[I]**: boot does not appear to route
through the guarded `set_default_server` (otherwise the `id == -1` error would print at boot,
and it does not), so boot either validates before calling or resolves by a different route.
This seat did not locate the boot call site — no engine source on host, and the `lsp` device is
unavailable (§7).

---

## 4. Divergence map — pinned 2D laws under the boot-time swap

### 4.1 Six tracked laws × 4 variants × 3 fresh processes **[M]**

Scratch copies are byte-identical to the tracked fixtures (F8), so these are the pinned laws.
Payload = the fixture's own `PASS`/`ERROR` lines (headers carrying `engine2d=`/`sep_thread=`
excluded, since those echo the config by construction).

| law | axis | `Jolt Physics` vs `DEFAULT` | `thread_on` vs `DEFAULT` | `Dummy` vs `DEFAULT` |
|---|---|---|---|---|
| `phys2d_motion ccd_ladder` | ccd | **byte-identical** | byte-identical | differs |
| `phys2d_motion btm_hit` | motion query | **byte-identical** | byte-identical | differs |
| `phys2d_motion dss_shapes` | queries | **byte-identical** | byte-identical | **differs + rc=124** (§4.3) |
| `phys2d_events cm_on` | contact monitor | **byte-identical** | byte-identical | differs |
| `phys2d_joints joint_groove` | joints | **byte-identical** | byte-identical | differs |
| `phys2d_joints joint_pin_clear` | joints | **byte-identical** | byte-identical | differs |

`Jolt Physics` as a 2D engine value is **observationally identical to `DEFAULT` on every pinned
law measured** — consistent with §2: the value is stored, ignored, and the Godot 2D server runs.
Note this is *not* evidence that the 2D setting is dead in general: `Dummy` moves every one of
these rows (§4.2).

### 4.2 Four-axis compact slice (ccd / joints / queries / damping) **[M]**

One process measures all four axes, so the backend swap is the only variable.

| axis | `DEFAULT` | `Jolt Physics` | `thread_on` | `Dummy` |
|---|---|---|---|---|
| **ccd** (3000 px/s vs 2 px wall, CAST_RAY) | `x=91.1600 crossed=false` | **identical** | identical | `x=0.0000` (never moves) |
| **joints** (pin, softness .5, gravity-loaded) | `sep=80.0000 a=(-40,8.6071)` | **identical** | identical | `a=(-40,-80)` (frozen) |
| **queries** (ray / shape / cast_motion) | `ray_hit=true ray_x=99.0000 n_shape=1 n_motion=2` | **identical** | identical | `ray_hit=false n_shape=0 n_motion=0` |
| **damping** (v₀=(200,0), ω₀=12, defaults 2.0/3.0) | `lin=74.8265 ang=2.7112` | **identical** | identical | `lin=200.0000 ang=12.0000` (no decay) |

`Jolt Physics` ≡ `DEFAULT` on all four axes, 3 fresh processes each, `uniq=1`.
`Dummy` differs on all four: it does not simulate at all (no gravity, no damping, no
collisions, empty query results) — which is the positive control proving the 2D engine setting
**is** functional for registered names, and therefore that the Jolt-2D null result is a fact
about the registry rather than about an inert setting.

**Incidental damping-axis pin** (backend-independent, identical in all four variants) **[M]**:
`RigidBody2D.linear_damp` / `angular_damp` **read back `0.0000`** while the effective damping is
the `ProjectSettings` default. With `physics/2d/default_linear_damp=2.0`,
`default_angular_damp=3.0` and `linear_damp_mode=0` (`DAMP_MODE_COMBINE`), the measured decay
matches `exp(-damp·t)`: `200·exp(-1.0)=73.58` measured `74.8265`; `12·exp(-1.5)=2.677` measured
`2.7112`. The node property is the *override*; `0.0` means "unset/combine", not "undamped".

### 4.3 New divergence class found under `Dummy` — the queries axis can time out **[M]**

Neither the r86 scratch (which had no `Dummy` column at all) nor any tracked battery row
exercises a `Dummy` 2D server on the query laws — the tracked harness always runs the default
`project.godot`. r77's scratch did probe `Dummy`, but only for the body-state path
(`body_get_state ⇒ <null>`), not `dss_shapes`. Under
`physics/2d/physics_engine="Dummy"`, `phys2d_motion --arm=dss_shapes` does **not** fail cleanly:

```
SCRIPT ERROR: Invalid access to property or key 'collider' on a base object of type 'Dictionary'.
   at: _arm_dss_shapes (res://phys2d_motion.gd:612)
```

`intersect_ray` under Dummy returns a hit `Dictionary` with **no `collider` key**, the fixture's
coroutine dies before `quit()`, and the SceneTree keeps running until the harness's timeout
kills it: **rc=124 at 180 s**, deterministic across 3 fresh processes (stderr byte-identical,
329 B). This matters for any future arm that swaps the 2D server: a registered-name swap can
convert a PASS row into a **180-second timeout** instead of a clean non-zero failure, which
costs the battery a bounded-run budget rather than producing a verdict.

---

## 5. `physics/2d/run_on_separate_thread` — measurable change, not inert

**Measurable behaviour change.** The setting arms a **space-state access gate**. Seven fetch
positions, one process each so every stderr line is attributable:

| position | threading `false` | threading `true` | ERROR lines (true) |
|---|---|---|---|
| A first statement of `_initialize` | `ok` | **`null`** | 2 |
| B first statement of deferred `_run` | `ok` | **`null`** | 2 |
| C after `await process_frame` | `ok` | **`null`** | 3 |
| D after 4 × `await physics_frame` | `ok` | `ok` | 2 |
| E inside `Node._physics_process` | `ok` | `ok` | — |
| F inside `Node._process` | `ok` | **`null`** | 3 |
| G deferred continuation after an idle frame | `ok` | **`null`** | 3 |

Refusal text, verbatim (identical for every refused position):

```
ERROR: Space state is inaccessible right now, wait for iteration or physics process notification.
   at: space_get_direct_state (modules/godot_physics_2d/godot_physics_server_2d.cpp:281)
```

**Attribution is exact.** A `--nofetch` baseline performs zero explicit fetches and produces
**0** such ERROR lines under both settings. Each `gate_one` run performs A, B and its target
position, so the expected refused count is A,B plus the target unless the target is legal:
observed `{A:2, B:2, C:3, D:2, F:3, G:3}` — **exactly** the predicted counts, with legal `D`
adding none. **One refused fetch ⇒ exactly one ERROR line**, at zero ambient noise.

Reproduces r77's `window` table (A,B,C,F,G refused; D,E legal) on a fresh process, independently.

**One correction to r77's record (§6/F9).** r77 §3.2 characterises this refusal as *"silent
through `World2D.direct_space_state` and loud through the explicit server call"*. **The property
path is equally loud.** This seat measured `get_root().get_world_2d().direct_space_state` and
`PhysicsServer2D.space_get_direct_space_state(w.space)` in separate processes and their error
signatures are **byte-identical** — same message, same `at:` line, sha256 of the `at:` line
`e18944622af0bc30f8a046a3316c25c163b494d7ffc053727246edaa0b412352` for both. r77's own receipt
agrees: in `corpus/live/gd-scout/probe2d/win.thr.stderr.txt`, ERROR frames attribute to
`w2.gd:53` (**3×**, the World2D property) and `w2.gd:24` (**1×**, the World2D property in
`_initialize`) alongside `w2.gd:54` (**3×**, the explicit call) — while
`win.default.stderr.txt` is **0 bytes**. The correct statement is: *the refusal returns `null`
and emits one identical ERROR through both paths.*

**Mechanism, bounded [I].** The binary carries `PhysicsServer2DWrapMT`,
`&PhysicsServer2DWrapMT::_thread_loop` and `CommandQueueMT<…PhysicsServer2DWrapMT…>` — i.e. the
threaded mode is a wrapper that marshals commands — together with two guard families:

```
Condition "(using_threads && !doing_sync)"                is true. Returning: nullptr
Condition "(using_threads && !doing_sync) || space->is_locked()"    is true. Returning: nullptr
Condition "(on_separate_thread && !doing_sync)"           is true. Returning: nullptr
Condition "(on_separate_thread && !doing_sync) || space->is_stepping()" is true. Returning: nullptr
Condition "space->is_stepping()" is true. Returning: Vector3()
```

The `is_stepping` family is **provably 3D** — one of its members returns `Vector3()`, which no
2D call can — so by elimination the `using_threads && !doing_sync` / `is_locked` family is the
**2D** guard, and it explains the gate exactly. Note the runtime error does **not** carry the
condition string (`ERR_FAIL_COND_V_MSG` prints only the message), so this pairing rests on the
`Vector3()` datum, not on the refusal text.

This does **not** explain thread creation: the per-thread name census
(`/proc/self/task/*/comm`) is **byte-identical** for both settings — 36 threads,
`WorkerThread 0..31` ×1 each plus `godot` ×4, at boot and after 40 physics frames with 40 live
bodies. No dedicated physics thread appears. Whether the step runs on a `WorkerThreadPool` task
rather than a dedicated thread was **not** determined (the solver's pool use is visible as
`WorkerThreadPool::GroupUserData<GodotStep2D…>` in the binary, but this seat did not prove the
step's dispatch path).

**A grep trap worth recording.** The binary also contains the bare strings
`physics/2d/run_on_thread` and `physics/2d/thread_model`. Neither is a live setting: the
`ProjectSettings.get_property_list()` census in §2.1 lists `physics/2d/run_on_separate_thread`
and does **not** list either of them, and `physics/3d/run_on_thread`/`thread_model` are absent
too. They are 3.x-era names retained for the settings-migration/rename table. A `strings`-only
inventory would have reported two extra 2D threading knobs that do not exist at runtime — which
is why §2.1's runtime property list, not the string census, is the authority for what the 2D
surface contains.

**Consequence for the pinned laws: none.** All six tracked laws and all four `slice4` axes are
byte-identical under `thread_on` vs `false` (§4). The setting's *only* measured effect is the
gate — which is a real, reproducible, loud behaviour change, not an inert knob.

---

## 6. Falsification list (measured negatives, all controls PASS)

Each control is an input that **must** move the instrument if the instrument is live.
`analyze_v2.py` prints the verdicts; all pass.

| id | falsification test (must-differ input) | result |
|---|---|---|
| **F1** | the backend discriminator must fire when a Jolt backend really is installed: `3d/physics_engine="Jolt Physics"` must move `dss3d_class` | **PASS** — `GodotPhysicsDirectSpaceState3D` → `JoltPhysicsDirectSpaceState3D` |
| **F2** | the 2D engine setting must be honoured for a *registered* name: `2d/physics_engine="Dummy"` must change the measured world | **PASS** — `space2d_valid` true→false; all four `slice4` axes move |
| **F3** | the enum hint must be read live, not fabricated: 2D must lack a Jolt token while 3D carries one | **PASS** — `hint_2d` has no `Jolt`; `hint_3d` has `Jolt Physics` |
| **F4** | the gate instrument must be live: `thread_on` must refuse ≥1 position and print ≥1 ERROR; `false` must print 0 | **PASS** — false: 0 refusals/0 ERROR; true: 5 refusals + ERROR |
| **F5** | the manager refusal probe must be name-specific, not blanket: the same name must be accepted by the 3D manager and refused by the 2D manager | **PASS** — 2D-manager refusals=3 (`Jolt`+`garbage`+`""`), 3D-manager refusals=1 (`garbage`) |
| **F6** | error counting must be attributable, not ambient: a fetch-free baseline under `thread_on` must be silent | **PASS** — baseline stderr 0 B for both settings |
| **F7** | one refused fetch must cost exactly one ERROR line; a legal fetch must cost none | **PASS** — per-position `{A:2,B:2,C:3,D:2,F:3,G:3}` == predicted exactly |
| **F8** | the slices must be the pinned laws, not drifted copies | **PASS** — `phys2d_motion.gd`/`phys2d_joints.gd`/`phys2d_events.gd` byte-identical to `corpus/fixtures/` |
| **F9** | r77's "silent through World2D" claim | **FALSIFIED** — property path and explicit call emit byte-identical ERROR (`at:` line sha256 equal); r77's own `win.thr.stderr.txt` attributes 4 ERROR frames to the property path (`w2.gd:53` ×3, `w2.gd:24` ×1) |

Additional measured negatives worth carrying forward:

- **`is_class` / `class_exists` are not backend oracles.** `is_class("GodotPhysicsServer2D")` is
  `false` while GodotPhysics2D runs (`get_class()` returns the abstract `PhysicsServer2D`), and
  `ClassDB.class_exists` is *selection-dependent* (`GodotPhysicsServer3D` flips true→false when
  Jolt-3D is selected). Only the live DSS class discriminates.
- **The manager's registry is not enumerable from script** — `has_method` is false for all five
  accessor spellings tried on both managers.
- **An out-of-enum 2D engine value is not clamp-detected at runtime**: `Jolt Physics`,
  `garbage_xyz`, `""`, `GodotPhysics2D` and `DEFAULT` all yield rc=0, 0 B stderr,
  `space2d_valid=true`, `dss2d_class=GodotPhysicsDirectSpaceState2D` and byte-identical simulated
  output. Only reading the value back distinguishes them.

---

## 7. Remaining unknowns / not measured

- **Boot-path validation mechanism** **[I, bounded]**: why the boot path is silent where the
  manager API is loud. The `id == -1` guard demonstrably exists and fires on the API path; it
  demonstrably does *not* fire at boot. Whether boot validates first, resolves by a different
  route, or the setting is consulted by a wrapper that ignores misses — **not determined** (no
  engine source on host, no `lsp` device).
- **Thread creation for `run_on_separate_thread`** **[I, bounded]**: the per-thread name census
  is byte-identical across the setting (36 threads, same names), yet the gate proves
  `using_threads == true` and `PhysicsServer2DWrapMT::_thread_loop` exists in the binary.
  Whether a dedicated thread is created and named, or the step is dispatched to the existing
  `WorkerThreadPool`, was not proven.
- **g3d rounds r83–r85 not re-measured** — out of lane. This seat did not verify the 3D
  "backend split" rows the r86 question refers to; the 3D measurements here exist only as the
  positive control for F1/F5.
- **No pinned law covers the damping axis.** `slice4`'s damping column is a scout probe, not a
  battery row; the incidental `linear_damp`-reads-0.0 pin in §4.2 is **not** tracked.
- **`Dummy` + `dss_shapes` timeout (§4.3)** was characterised only on this one arm; whether
  other query-family arms also degrade into timeouts under `Dummy` was not swept.
- **No 2D Jolt claim beyond absence.** Since no 2D Jolt backend exists here, this seat makes no
  statement about how godot-jolt *would* behave in 2D — the divergence map in §4 is the
  divergence map of the *literal string* `"Jolt Physics"` installed as a 2D engine value, which
  is a no-op, not a Jolt measurement.
- **Portability**: all values are this host, this build, `--headless`, 60 tps, GodotPhysics2D
  (except where a variant is named), these scenes. A Godot build with a 2D Jolt module compiled
  in would change §1, §2 and §4 wholesale.
- **`lsp` device absent** (host state, unchanged): no semantic navigation was possible; every
  C++ file:line in this report is engine-emitted text or a binary string, not a source read.

---

## 8. Author directives (exact)

1. **Do not author a Jolt-2D cell.** There is no 2D Jolt backend in this build; a row asserting
   one would be unfalsifiable here. If the fleet wants a pinned backend-identity row, pin
   `dss2d_class` — it is the only discriminating oracle (§2.4) — and gate it on the enum hint,
   **not** on `is_class`/`class_exists` (both are dead instruments, §6).
2. **If a `run_on_separate_thread` cell is authored**, pin the **gate** (A–G null/ok table, §5),
   not thread ids. The scratch's `thread_ids` arm returns `body_integrate=1` under both settings
   and cannot discriminate; it would produce a false "inert" verdict.
3. **Expect one ERROR line per refused fetch**, including through `World2D.direct_space_state`
   (§5, F7). Any `expected_errors` entry for a threaded row must budget **one line per refused
   fetch**, and the `at:` line is `space_get_direct_state
   (modules/godot_physics_2d/godot_physics_server_2d.cpp:281)`.
4. **`--nofetch`-style baselines are the right pattern** for any arm that counts engine errors:
   the fetch-free baseline is 0 B under both settings (F6), so error counts are attributable.
5. **If a `Dummy` column is ever added to the battery**, budget for §4.3: `dss_shapes` under
   `Dummy` converts to a **180 s timeout** (rc=124) via a GDScript error at
   `phys2d_motion.gd:612` (`'collider'` absent from the ray-hit Dictionary). Do not paste a
   `Dummy` variant into `CASES` without either fixing that access or bounding the run.
6. **Never pin the 2D engine value from a variant that names an unregistered engine** as if it
   proved the backend: `Jolt Physics`, `garbage_xyz`, `""` and `DEFAULT` are mutually
   indistinguishable at runtime (rc, stderr, `space2d_valid`, `dss2d_class`, simulated output).
   The value must be read back explicitly (§3).
7. **Keep the `slice4` damping column out of the battery** unless a real row is authored: it is a
   scout probe (§7). The `linear_damp`-reads-`0.0`-while-effective-damp-is-the-default finding
   (§4.2) is measured but **untracked**.
8. **Do not cite r77 §3.2's silent/loud split.** It is falsified (§6/F9); cite §5 of this report
   instead.
9. Never print object ids, RIDs or addresses. Every pinned value in §2–§5 is a number, bool,
   class name, enum hint, or a source-relative file:line.
10. No git mutation and no commit were performed by this seat; the two modified tracked files
    (`SCORECARD.md`, `corpus/fixtures/run_battery.py`) pre-date this session and belong to
    another lane.

---

## 9. Evidence index

All under `corpus/live/r86-scout/` unless noted. `MANIFEST.sha256` covers every artefact below.

| artefact | path | sha256 (prefix) |
|---|---|---|
| v2 probe (backend / manager / gate / gate_one / threads / boot) | `proj/r86_probe2.gd` | `7e4fd2a1edf26757` |
| 4-axis divergence slice (ccd/joints/queries/damping) | `proj/r86_slice4.gd` | `fc222938fdfcfb5e` |
| variant setter incl. 3D positive controls | `set_cfg2.sh` | `79247773e72e09a5` |
| v2 runner (fresh ×3, split streams, rc) | `run_v2.sh` | `89fad0d62b9b11d6` |
| pinned-law slice runner | `run_slices.sh` | `0b6be67d56ebb8cb` |
| stability + falsification analyzer (F1–F8) | `analyze_v2.py` | `d3ee7e44600017ed` |
| slice stability + divergence analyzer | `analyze_slices.py` | `8b75daf25e163192` |
| binary static census | `runs/static_strings.txt` | see `MANIFEST.sha256` |
| v2 receipts (34 arm/variant × 3 reps, split streams + rc) | `runs/v2/` | 315 files |
| census + manager receipts (9 arm/variant × 3 reps) | `runs/census/` | 81 files |
| pinned-law receipts (6 laws × 4 variants × 3 reps) | `runs/slices/` | 288 files |
| 4-axis slice receipts (4 variants × 3 reps) | `runs/slice4.*` | 36 files |
| per-receipt sha256 sidecars (every file above) | `MANIFEST.sha256` | 752 lines |
| prior-seat probe, audited and reused | `proj/r86_probe.gd` | `a8f829924a7a595e` |
| prior-seat variant setter, audited and extended | `set_cfg.sh` | `a81ae8845958f660` |
| r77 receipt falsifying its own §3.2 (read-only, tracked corpus) | `corpus/live/gd-scout/probe2d/win.thr.stderr.txt` | (tracked, unmodified) |
| tracked 2D laws under test (byte-identical to scratch copies) | `corpus/fixtures/phys2d_{motion,joints,events}.gd` | (tracked, unmodified) |

Reproduce: `bash run_v2.sh && bash run_slices.sh && python3 analyze_v2.py && python3 analyze_slices.py`.
