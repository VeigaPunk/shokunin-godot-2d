# r74 BOUNDARY (g2d) — LOVE 11.5 Box2D interior-write lattice: edge cells, negative controls, crash + kill semantics

Seat: **boundary** (LEAF) | Lane: **g2d** = `~/Projects/shokunin/game-dev-2d-shokunin` |
Round 74 | Wave `shokunin-train-20261101-w14` | Theme: physics-server interiors (g2d LOVE)

**Recovery note.** The prior generation of this seat died ~16:10Z and left scratch in
`corpus/live/r74-boundary/` (38-cell lattice, `absent.json`, `kill.json`). I verified that
scratch by re-running it (results in §7: 32/38 receipts reproduce byte-identically; the other
6 differ *only* in an embedded `main.lua:<line>` number because the probe source grew), then
extended it to 54 cells. No tracked file was touched, no git mutation, no subagent, no
sibling-lane edit. Write scope used: `corpus/live/r74-boundary/**` + this report.

**Host/build (bounded claim — this host, this build only):**

| key | value |
|---|---|
| host / kernel | `plazir27` / `7.2.3-arch1-3` |
| LOVE | **11.5 (Mysterious Mysteries)**, Arch pkg `love 11.5-3` |
| `/usr/bin/love` | sha256 `bd427c2fc581c4286da2e8da0bdb11cdd537a849cb86a5d6b66c11eb1150cdcb` |
| `/usr/lib/liblove-11.5.so` | sha256 `92cb23a7972fdfd079fe32b2e83864d5bd68334524732e965d063b283f75df92` |
| LuaJIT | `2.1.1788460057` | python | `3.14.7` | git HEAD | `1275746` |
| vendored Box2D | **2.3.2** (`b2Version b2_version = {2,3,2}`, `b2Settings.cpp:26`) |
| probe / driver sha256 | `cells/main.lua 9bcc8fc9…`, `cells/conf.lua 678014cc…`, `boundary_cells.py 7090e8fa…` |
| LOVE 11.5 source tree used for anchors | tarball `6f55c265…` (codeload, tag `11.5`); `b2StackAllocator.cpp c909015b…` |

**`lsp` disclosure (literal-fallback recorded).** No `lsp` device is in this seat's toolset and
no server exists on PATH for Lua/C++ (`lua-language-server`, `clangd`, `ccls` absent). Every
claim below is either a **process-level measurement** (command + exit + receipt path) or a
`file:line` citation from the LOVE 11.5 source tree, whose identity is pinned by tarball sha256
and by `strings -a /usr/lib/liblove-11.5.so` containing the very assert strings cited
(`Box2D assertion failed: %s`, `m_entryCount > 0`, `p == entry->data`). Grep is the literal
fallback, recorded here, and is never presented as semantic proof.

---

## 1. Headline — the interior-write partition, 54 cells

Lattice: **54 cells**, one fresh `love` process per cell, `timeout -s KILL 12` inside plus a
process-group kill in the driver, `EDGE_DONE <cell>` marker required for a complete receipt.
Every cell was run **≥2 times**; every cell's stdout is **byte-identical across reps**
(§6). Result: **52 clean, 2 hard-abort**.

Classes below are the *measured* gating, per callback class. `refused` = catchable Lua error
`Box2D assertion failed: m_world->IsLocked() == false`, state unchanged, step continues.
`deferred` = accepted, effect drained after `world:update` returns. `applied` = takes effect
inside the step. `fatal(lua)` = error escapes the step. `fatal(abort)` = **SIGABRT, no receipt.**

| mutation | beginContact | preSolve | postSolve | endContact | exterior (control) |
|---|---|---|---|---|---|
| `body:setPosition` | refused | refused | refused | **refused** (new) | applied |
| `love.physics.newBody` | refused | — | — | **refused** (new) | applied |
| `body:destroy` (self/other) | deferred | deferred | deferred | **deferred** (new) | immediate |
| `body:setActive(false)` | refused | — | — | — | applied |
| `body:setAwake(false)` | **applied** | **applied** | — | — | applied |
| `contact:setEnabled(false)` | applied (1-step mask) | **applied** | **applied** (new) | **applied** (new) | n/a |
| `world:destroy()` | deferred | deferred | deferred | deferred | deferred |
| `fixture:setSensor` solid→sensor | applied | n/a¹ | n/a¹ | applied | applied |
| `fixture:setSensor` sensor→solid | **fatal(abort)** | applied² | applied² | applied | applied |
| `world:update` (re-entrant) | **applied** | — | — | — | n/a |

¹ pure-sensor scenes never dispatch `preSolve`/`postSolve` (`sensor_trace`: `bc=1 ec=0 pre=0 post=0`
for 8 consecutive steps) — the callback simply never runs, so a "no abort" reading there is
*not exercised*, not evidence. Cell ² (`mixed_morph_sensor_*`) supplies a scene where pre/post
do fire and a live sensor contact exists.
² morphing a *different* live sensor contact from pre/post ⇒ applied, no abort
(`mixed_morph_sensor_pre`: `pre1 touch=true fa=false fb=false` → `mut … ok=true err=nil`).

**The two fatal(abort) cells are the round's sharpest edge:**

```
morph_sensor_solid_bc        rc=-6  done=False  5 stdout lines
mixed_morph_sensor_bc_own    rc=-6  done=False  35 stdout lines
stderr (both, byte-identical across reps):
  terminate called after throwing an instance of 'love::Exception'
    what():  Box2D assertion failed: p == entry->data
  timeout: the monitored command dumped core
```

Both are the *same shape*: **sensor→solid morph of the fixture whose own `beginContact` is
currently being dispatched** (one in a pure sensor world, one in a world that also holds a
live solid contact). Same morph issued from `preSolve`/`postSolve` of another contact, from
`endContact`, from outside any callback, or after the contact is disabled first ⇒ **clean**.
`solid→sensor` in its own `beginContact` ⇒ **clean**. So the abort is not "any interior morph"
and not "any contact-type flip": it is narrowed to the own-BC sensor→solid case, cross-scene
confirmed (2 scenes × 2 reps, byte-identical).

---

## 2. Crash semantics — partial capture, and why pcall cannot contain it

The driver wraps every step in `pcall(function() world:update(FIXED) end)`. Under that exact
containment boundary:

- **lock-class asserts are containable**: `uncaught_setpos_bc` → `step=1 update_ok=false
  err=main.lua:605: Box2D assertion failed: m_world->IsLocked() == false`, and the *next* step
  runs clean (`step=2 update_ok=true`). Same for a plain Lua error (`uncaught_error_bc`:
  `err=main.lua:…: BOOM-from-callback`).
- **the stack-allocator assert is not**: `morph_sensor_solid_bc` aborts *through* that pcall.

**Partial-capture pin (what the author must require):** the abort leaves a *truncated but
usable* receipt — the mutation line is present, the step line is absent, `EDGE_DONE` is absent,
rc = −6. Detection rule: `done_marker == 0 AND rc ∉ {0}` ⇒ measured FAIL, never a pass.
`stdout_lines=5` (BC scene) vs `35` (mixed scene) shows the truncation point is *where the
process died*, so line counts are evidence, not noise.

**Assert-surface anchor (source, not inference):** the aborting assert is
`b2Assert(p == entry->data)` in **`src/libraries/Box2D/Common/b2StackAllocator.cpp:65`**
(`b2StackAllocator::Free`, LIFO check), and the installed `.so` carries the string
(`strings -a /usr/lib/liblove-11.5.so` line 14479). LOVE's fork replaces `b2Assert` with
`loveAssert`, which **throws** `love::Exception` (`b2Settings.cpp:48-52`, `b2Settings.h:29-30`),
so an assert is only catchable where a `luax_catchexcept` boundary is still on the stack.
The only `Free` call sites are `b2World.cpp:548` and the **destructors**
`b2Island::~b2Island` (`b2Island.cpp:176-180`) and `b2ContactSolver::~b2ContactSolver`
(`b2ContactSolver.cpp:135-136`); a throw from a destructor is `noexcept` ⇒ `std::terminate`,
which is exactly the observed `terminate called after throwing an instance of 'love::Exception'`.
**Inference (moderate):** the throw therefore originates in one of those destructors, i.e. the
interior morph leaves the world's stack allocator (`b2World::m_stackAllocator`, `b2World.h:234`)
unbalanced and the failure surfaces while the island/solver is torn down. *The allocation
imbalance itself was not traced* — that is an open gap (§8), and the observed partition, not
the mechanism, is the contract.

**Build question in the author brief ("Box2D debug-vs-release assert behavior is
build-dependent — record which this build is") — answered:** this build is **asserts-on and
non-aborting by default**: LOVE *unconditionally* patches `b2Assert` (the `assert()` define is
commented out), so there is no NDEBUG dependence at all; asserts surface as Lua errors at the
nearest catch boundary. The abort above is **not** an NDEBUG artifact — it is the throw
crossing a `noexcept` destructor frame. Two assert surfaces exist on this build and they are
distinguishable in a receipt by `rc` alone: `0` + Lua error text = catchable; `−6` +
`terminate called after throwing` = fatal.

---

## 3. Edge members beyond `beginContact` (new in this seat's pass)

- **`endContact` is inside the lock too.** `ec_setpos` → refused
  (`err=… m_world->IsLocked() == false`), `ec_newbody` → refused (`IsLocked() == false`);
  `ec_destroy_self` → accepted (deferred). This closes the "all four callbacks run
  `locked=true`" claim for the *write* classes, not just for `world:isLocked()` (r74-scout).
- **Contact mask is a per-class, single-step lever.** `pre_contact_disable` and
  `post_contact_disable` and `ec_contact_disable` all `ok=true`; in the `preSolve` case the
  same step's `postSolve` for that contact is skipped (`counts step=1 … pre=1 post=0`), then
  `pre/post` resume from step 2 (`pre=3 post=2`) — i.e. `b2Contact::Update` re-enables the
  contact each update, matching r74-scout's beginContact measurement, now generalized.
- **Availability edges on a destroyed handle are total.** `avail_destroyed_body`: after
  `dyn:destroy()`, *every* read and write raises `Attempt to use destroyed body.` —
  `getPosition`, `getX`, `isActive`, `isAwake`, `getType`, `getMass`, `getFixtures`,
  `getContacts`, `getWorld`, `setLinearVelocity` (10/10). There is **no stale-read window**:
  a destroyed proxy is unusable, so "read the handle after destroy" is never a valid witness.
- **`world:destroy()` inside any callback is accepted and deferred by exactly one step.**
  `wdestroy_bc/pre/post`: the step in which the callback ran still returns
  `update_ok=true` and still counts contacts; the **next** `world:update` raises
  `Attempt to use destroyed world.` (`wdestroy_ec` identical: EC at step 2, step 2 completes,
  step 3 fails). After that every body read also raises.
- **Re-entrancy defeats the lock guard (highest-value edge).**
  `nested_update_bc`: a nested `world:update` inside `beginContact` is **accepted**
  (`mut=nested:world:update ok=true err=nil`) and runs a full step (pre/post counted inside the
  callback). Consequence, measured in `nested_update_then_pos_bc`:
  `mut=nested:world:update ok=true` then **`mut=post_nested:body:setPosition ok=true`** and the
  position *actually changes* (`x0=0 → x1=1`). The nested Step clears `m_locked` on exit and the
  outer step never restores it, so **a `setPosition` that is `refused` in an ordinary callback
  becomes `applied` after one nested `world:update`**. Any author cell that classifies a write
  must pin whether a nested step preceded it.
- **Sensor vs solid channel split is total** (`sensor_trace`, `sensor_lattice`,
  `mixed_lattice`): sensor contacts produce `beginContact`/`endContact` only; solid contacts
  produce `begin`+`pre`+`post`. This is what makes the pre/post morph cells above possible.

---

## 4. Negative controls and blockage rows (nothing here fabricates a lattice row)

| row | receipt | measurement |
|---|---|---|
| missing binary | `absent2.json:absent_binary` | rc `null`, `launch error: [Errno 2] No such file or directory: '/nonexistent/love'`, stdout empty |
| missing PATH | `absent2.json:absent_path` | rc `null`, same shape for `love` with `PATH=/nonexistent` |
| broken shim | `absent2.json:broken_shim` | rc **127**, stdout empty (no partial lattice) |
| physics module off | `absent2.json:physics_off` | rc 0, `love_physics_nil=true`, `newWorld_ok=false err=… attempt to index field 'physics' (a nil value)`, `EDGE_DONE physics_off` — a bounded blocked verdict, no fabricated rows |
| **video backend absent** | `backend3.json:video_absent` | rc **1**, `Error: Could not initialize SDL video subsystem (No available video device)` (+ `XDG_RUNTIME_DIR is invalid or not set`) |
| **video backend forced dummy** | `backend3.json:video_dummy` | rc **1**, `Could not set window mode` + stderr `Unable to create OpenGL window … requires … OpenGL 2.1` ⇒ even with `SDL_VIDEODRIVER=dummy`, **`t.window=true` is unrunnable on this host**; the physics interior is reachable only in the headless profile (window/graphics/image/audio off) |
| unwritable identity dir | `backend3.json:identity_unwritable` | rc **0**, full lattice + `EDGE_DONE` under `HOME=/nonexistent` ⇒ the probe has no `$HOME`/save-dir dependency (negative control for the probe itself) |
| exterior-write controls | `pos_ext`, `newbody_ext`, `destroy_other_ext`, `sleep_setactive_ext`, `morph_sensor_solid_ext_live` | same mutation outside a callback ⇒ `ok=true` and the state actually changes — the contrast that makes the interior rows meaningful |
| solid-lattice control | `solid_lattice`, `mixed_lattice` | baseline contact multiplicities for the scenes above |

The `video_dummy` row was re-run after a conf bug in the first attempt
(`t.window = true` then `t.window.width` — LOVE requires a table); the corrected probe is
`window_probe/conf.lua` with `t.window = {…}`. `backend2.json` (buggy conf) is kept on disk;
**cite `backend3.json`.** The earlier `video_absent` reading is unchanged by the fix.

---

## 5. Kill-escalation classes, and the carried FIFO guard — falsified here

`kill2.json` (driver rows) plus a first-hand matrix run by hand (`/tmp/y*.out`, reproduced by
the commands in §9). `hang_loop` = `while true do end` inside `love.update`;
`fifo_open` = blocking `io.open(FIFO,"r")` with no writer, in `love.load`;
`fifo_open_update` = same, inside `love.update`.

| cell | signal / wrapper | rc | wall | `EDGE_DONE` | reading |
|---|---|---|---|---|---|
| `hang_loop` | SIGTERM (driver) | survived, killed at +2.503 s by the driver's SIGKILL | | no | **TERM-immune** |
| `hang_loop` | SIGINT (driver) | survived, +2.503 s | | no | **INT-immune** |
| `hang_loop` | SIGKILL | dead | 1 ms | no | kill works |
| `hang_loop` | `timeout -k 2 3` (TERM@3 s, KILL@5 s) | **137** | **5001 ms** | no | TERM ignored, **KILL required** |
| `hang_loop` | `timeout -s KILL 3` | **137** | **3001 ms** | no | the carried guard's form: 3 s, deterministic |
| `fifo_open` | SIGTERM (driver) | **0** | 1 ms | **yes** | open returns `Interrupted system call` |
| `fifo_open` | SIGKILL (driver) | −9 | 1 ms | no | receipt truncated at the blocking line |
| `fifo_open_update` | SIGTERM / SIGKILL | 0 / −9 | 3 ms / 0 ms | yes / no | same, from inside `love.update` |
| `fifo_open` | `timeout -k 2 3` | **124** | **3002 ms** | **yes** | TERM alone ended it; `EDGE_DONE` intact |
| `fifo_open` | `timeout -s KILL 3` | **137** | 3001 ms | **no** | KILL also ends it, but **destroys the receipt** |

Verbatim TERM row (`kill2.json`): `fifo_returned=false err=…/fifo/block.fifo: Interrupted system call`
then `EDGE_DONE fifo_open`, rc 0.

**Carried guard status.** "fifo-open blocks are SIGTERM-immune → `timeout -s KILL`" **does not
transfer to LÖVE 11.5 on this host**: the blocked `open(2)` returns `EINTR` on SIGTERM, the Lua
`io.open` returns `nil, "Interrupted system call"`, and the cell exits cleanly with its DONE
marker (`rc=124` under `timeout`). The guard *does* hold for a **busy Lua spin**, which ignores
TERM/INT and needs the KILL (137 at 5.001 s). **Inference (not traced):** the EINTR shape is
consistent with a SIGTERM handler installed without `SA_RESTART`; SDL's handler was not read.
Mechanism name is not the contract — the measured pair (spin: KILL required; FIFO block: TERM
suffices) is.

**"rc alone is never a verdict" — demonstrated three ways in this matrix:** the same fifo cell
reports `rc=0` (direct TERM), `rc=124` (under `timeout`), and `rc=137` (under `-s KILL`), and
only the last one *loses* its `EDGE_DONE` marker. The verdict carrier is
`EDGE_DONE ∧ rc` together, never `rc`.

---

## 6. Determinism, load replay, and verification of the recovered scratch

- **Reps.** `edge-verify1.json` (51 cells, 16:30:44Z) vs `edge-verify2.json` (51, 16:31:03Z):
  **0 cells with differing stdout sha256**; same for `edge-final.json` (54 cells, all 51 shared
  cells identical). The two late cells: `edge-mixed1/2.json` (2/2 identical) and
  `edge-bcown1/2.json` (2/2 identical, including the abort). Total: **54 cells × ≥2 reps,
  every cell byte-identical.**
- **Load replay.** `edge-load2.json` — the full lattice re-run with **8 CPU burners** pinned in
  the driver: **0 differing cells** vs the baseline (51/51 byte-identical), the two abort cells
  still abort with the same stderr. Interior-write gating is not timing-sensitive here.
- **Gen-1 scratch verification.** All 38 gen-1 cells re-ran; **32/38 byte-identical** to the
  gen-1 receipts. The 6 that differ (`wdestroy_bc`, `wdestroy_bc_uncaught`, `wdestroy_pre`,
  `wdestroy_post`, `wdestroy_ec`, `wdestroy_ext`) differ **only** in one embedded line number:
  gen-1 `step=2 update_ok=false err=main.lua:593: Attempt to use destroyed world.` → now
  `main.lua:605`, because the step-loop pcall moved when gen-2 cells were appended to
  `love.update`; every other line reference is unchanged (`main.lua:131`, `main.lua:516`).
  Class, rc, line counts and all other fields match.
- **Correction to the recovered scratch.** The gen-1 `edge-run2.json` is *not* a second
  independent baseline rep: its `lattice` rows are byte-identical to `edge-load.json`
  (`edge-run2.json` 30399 B ≡ `edge-load.json` 30399 B, 35 cells, and both **lack**
  `morph_sensor_solid_ext`, `uncaught_setpos_bc`, `uncaught_error_bc` that `edge.json` has).
  Treat it as a copy/duplicate; the independent reps are the ones recorded in §6 bullet 1.
  Also note the gen-1 `run2.log` is empty (0 B) — its lattice output was never captured.
- One untracked stray exists outside this seat's scope and is **not** mine to remove:
  `corpus/fixtures/__pycache__/love_battery.cpython-314.pyc` (driver imports
  `corpus/fixtures/love_battery.py` with `sys.dont_write_bytecode = True`, so no new bytecode
  was written by this pass).

---

## 7. Observed vs inference vs unresolved

**Observed (process-level, receipts cited):** §1–§6, in particular (a) the 2 fatal cells and
their byte-identical stderr, (b) `endContact` lock refusal, (c) total unusability of destroyed
handles, (d) one-step-deferred `world:destroy()`, (e) nested-update lock defeat, (f) the
mask's single-step semantics in all four callback classes, (g) the fifo/spin/timeout matrix,
(h) the backend blockages, (i) byte-identical determinism ×2 and under load.

**Inference (marked):** the abort's throw originates in `b2Island`/`b2ContactSolver`
destructors and is therefore `noexcept`-fatal (source-anchored call sites + the
`terminate … after throwing` message); the FIFO EINTR shape implies a non-`SA_RESTART` SIGTERM
handler; the sensor→solid own-BC case is what unbalances the world stack allocator.

**Unresolved gaps (do not read these as absence):**
1. **Why** own-BC sensor→solid unbalances `b2World::m_stackAllocator` is not traced; no
   allocation site inside the callback path was identified (`b2Fixture::SetSensor` only calls
   `SetAwake(true)`, `b2Fixture.cpp:220-227`). The partition is measured; the mechanism is not.
2. `world:destroy()` **inside a callback** was measured for all four classes, but
   `World::~World`-time reentrancy and double-`destroy()` in one step are untested.
3. `contact:setEnabled` was measured in all four classes, but never with `preSolve` returning
   `false` (the platform pattern) — the return-value contract is untouched.
4. Joints (`Joint:destroy`, joint callbacks) and `Fixture:setFilterData` (contact-mask *filter*
   edges, as opposed to `setEnabled`) are untested; `contact:setEnabled` is a mask, not a filter.
5. No cross-host / cross-build comparison: every claim is this host + LOVE 11.5 +
   liblove `92cb23a7…`; a build whose `b2Assert` aborts (or a different Box2D version) can move
   the `refused` rows to `fatal`.
6. `g3d`/audio rows in `SHARED.md` are sibling-seat scope and were not measured here.

---

## 8. Reproduce

```sh
cd ~/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r74-boundary

# full lattice (54 cells) + absent/kill/backend sections
python3 boundary_cells.py --section lattice --json edge-final.json      # 54 cells, 52 clean
python3 boundary_cells.py --section lattice --load 8 --json edge-load2.json   # 0 diffs
python3 boundary_cells.py --section absent  --json absent2.json
python3 boundary_cells.py --section kill    --json kill2.json
python3 boundary_cells.py --section backend --json backend3.json       # corrected window probe
python3 boundary_cells.py --section lattice --only morph_sensor_solid_bc,mixed_morph_sensor_bc_own

# the kill/timeout matrix by hand (mkfifo is created and removed by the driver too)
mkfifo -m 600 /tmp/r74.fifo
CELL=hang_loop /usr/bin/timeout -k 2 3  /usr/bin/love ./cells   # rc=137 @5001ms  (TERM ignored)
CELL=hang_loop /usr/bin/timeout -s KILL 3 /usr/bin/love ./cells # rc=137 @3001ms
CELL=fifo_open FIFO_PATH=/tmp/r74.fifo /usr/bin/timeout -k 2 3  /usr/bin/love ./cells # rc=124 + EDGE_DONE
CELL=fifo_open FIFO_PATH=/tmp/r74.fifo /usr/bin/timeout -s KILL 3 /usr/bin/love ./cells # rc=137, no DONE
rm -f /tmp/r74.fifo

# source anchor for the aborting assert
curl -sSL -o /tmp/love115.tar.gz https://codeload.github.com/love2d/love/tar.gz/refs/tags/11.5
tar xzf /tmp/love115.tar.gz -C /tmp && sed -n '60,70p' /tmp/love-11.5/src/libraries/Box2D/Common/b2StackAllocator.cpp
strings -a /usr/lib/liblove-11.5.so | grep -n 'p == entry->data\|m_entryCount > 0'
```

**Receipts:** `edge-final.json`, `edge-verify1.json`, `edge-verify2.json`, `edge-load2.json`,
`edge-mixed1/2.json`, `edge-bcown1/2.json`, `absent2.json`, `kill2.json`, `backend3.json`,
`backend2.json` (buggy-conf first attempt, kept), `edge.json`/`kill.json`/`absent.json` (gen-1,
verified), per-cell stdout/stderr in `out/`, `out-final/`, `out-verify1/`, `out-verify2/`,
`out-mixed1/`, `out-bcown1/`, plus `state2.txt` (all hashes above).

**Carried guards from `SHARED.md`, this lane:** reorder-topology/fd1 buffering, `bpy`
`PYTHONUNBUFFERED`, `io.DEFAULT_BUFFER_SIZE`, lavf wound partition, consumer-fork locality —
**not applicable** (no pipe/ffmpeg/bpy in this lane; python 3.14.7 named in §0). The
`fifo-open ⇒ SIGTERM-immune` guard is **falsified for LÖVE 11.5** (§5) and must not be carried
into the author's kill policy as a universal; the busy-spin half of it holds.
