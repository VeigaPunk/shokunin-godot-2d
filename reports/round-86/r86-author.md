# r86 author — 2D backend-select lattice (phys2d_backends)

8 cells in `corpus/fixtures/phys2d_backends.gd`, +8 battery rows → 182.

**Seat completion note:** the dispatched author (ds) landed the fixture and a
3-rep standalone pin set (`corpus/live/r86-author/standalone.json`, all
uniq_pass=1, rc=0, parent_error_lines=0) then died in the 09:0x rate-limit
sweep before CASES rows/report. The parent finished the merge: rows pasted
from the standalone pins, battery-verified **182/182** under battery context
(`corpus/live/r86-author-battery/20261015T130812159398Z/verdicts.json`) —
no re-pin needed (nested-boot arms are viewport-independent).

## Architecture

Boot-selected state (`physics/2d/physics_engine`, `run_on_separate_thread`)
is fixed before script statements run, so each boot-variant measurement
launches a **child Godot process** into a generated minimal project under
`user://r86bt/` and reads split stdout/stderr capture files. The parent
prints digests only — engine ERROR frames stay inside child captures, so
every row carries `expected_errors=()` despite arms that deliberately arm
refusals inside children. `dummy_timeout` is a self-bounded negative arm
(parent `timeout(3)` wrapper → `rc=124` is the *expected* class).

## Cells (scout §1–§5 armed)

| cell | law |
|---|---|
| `census` | 2D engine enum = `DEFAULT,GodotPhysics2D,Dummy` (3, no Jolt); 3D enum = 4 incl. `Jolt Physics`; `physics/jolt_physics_2d/**` = 0 props vs 32 for 3D; both managers bind exactly `[register_server, set_default_server]` — no enumeration surface |
| `lattice` | boot-fallback is **silent**: `Jolt Physics`/`garbage_xyz`/`""` all store verbatim, rc=0, resolve GodotPhysicsDirectSpaceState2D, bodies move; `Dummy` resolves `PhysicsDirectSpaceState2DDummy` with `valid=false`, `moved=0` |
| `jolt3d_live` | same-process control: `3d/physics_engine="Jolt Physics"` boots a **live** `JoltPhysicsDirectSpaceState3D` — the name is real, just 3D-only |
| `xcheck` | `set_default_server` refusal is typed and located: 2D refuses Jolt/garbage/empty (`errs2d=[0,0,1,1,1]`) at `physics_server_2d.cpp:959`; 3D accepts Jolt (`errs3d=[0,0,0,1]`) at `physics_server_3d.cpp:1193` |
| `gate_matrix` | `run_on_separate_thread=true` arms a **space-state gate**: `direct_space_state` null at positions A,B,C,F,G; ok only at D (post-4-physics) and E (first `_physics_process`); `space_get_direct_state` loud path errors ×5 at `godot_physics_server_2d.cpp:281` |
| `gate_duality` | the gate bites identically via property or API path (`prop`/`api` both B=null, errs=1, same source site) — refines r77's pinned split (boundary-falsified: paths emit byte-identical errors) |
| `dummy_degenerate` | Dummy server: `space_valid=false`, ray `intersect_ray` returns `[]`, `is_n=0`/`cm_n=0` vs control `ray_pos=(98,0)` |
| `dummy_timeout` | Dummy + `dss_shapes` never returns: parent `timeout 3` → `rc=124`, `hang_begin=1` — the only row whose PASS signature contains a 124 |

## Known bounds

- Boot variants mutate only `physics/2d/*`; `physics/3d/*` untouched except
  `jolt3d_live`'s deliberate 3D engine set.
- `moved=17.867` is a 12-physics-frame drop distance under default gravity —
  engine-version-coupled.
- `dummy_timeout`'s rc=124 is a *harness* class (outer timeout kills the
  child), not an engine verdict.
- The gate positions A–G are this fixture's naming (init / deferred-run /
  post-idle / post-4-phys / `_physics_process` / `_process` / deferred
  continuation); the 5/7 null split is the measured class on this build.

Bounded: Godot 4.7.2.stable.arch_linux.ed1daf0bf headless; PipeWire-free
lane. Wave-B (critic/verifier/boundary/simplifier/scribe) pending — seats
dispatch when routes recover.
