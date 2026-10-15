# game-dev-2d round 74 — scout: love.physics callback-interior pre-measurement

Seat: scout (LEAF) | Lane: g2d | Round: 74 | Wave
`shokunin-train-20261101-w14`.

Host: devin. Runtime **LOVE 11.5** (Arch package `love 11.5-3`;
`/usr/bin/love` launcher sha256 `bd427c2f…` → `/usr/lib/liblove-11.5.so`
sha256 `92cb23a7…`; system LuaJIT `2.1.1788460057+24c20c9-1`).
Repo `~/Projects/shokunin/game-dev-2d-shokunin` at HEAD `1275746`;
**no tracked file touched, no git mutation** — scratch
`corpus/live/r74-scout/` + this report only. No `$HOME` side effect
(no `~/.local/share/love/` created).

**`lsp` disclosure.** No `lsp` device in this seat's toolset and none on
PATH (`lsp`, `pyright`, `basedpyright`, `pylsp`, `jedi-language-server`,
`ruff-lsp`, `lua-language-server` all absent). Every claim below is a
process-level measurement or a `file:line` citation from LOVE 11.5
sources fetched at tag `11.5` (per-file sha256 in
`corpus/live/r74-scout/love_src_excerpts.txt`) — literal fallback,
recorded; not presented as semantic proof.

**Concurrency.** Sibling r74 seats were active (r74-author/… dirs
present); all keys below were stable across reps and no timing key is
used as a pin.

## Headline — the {refused | deferred | fatal} gating, measured

22 cells × 2 reps, one `love` process per cell, bounded 20 s, SIGKILL on
overrun; every cell prints a `CELL_DONE` marker (stdout flushed per
line), so a mid-cell death is a measured FAIL, never a silent truncated
pass. **All 22 cells 2/2 stable; surviving-cell stdout byte-identical
across reps** (the one diag cell differs only in heap addresses).

| write inside callback | beginContact | preSolve | postSolve | class |
|---|---|---|---|---|
| `body:setPosition(x,y)` | refused | refused | refused | **refused** — catchable Lua error `Box2D assertion failed: m_world->IsLocked() == false`; state unchanged; step continues when contained |
| `love.physics.newBody(world,…)` | refused | refused | refused | **refused** — `Box2D assertion failed: IsLocked() == false`; no body created (count 4→4) |
| `body:destroy()` | deferred | deferred | deferred | **deferred** — alive through the rest of the step, drained after `world:update` returns (count 4→3); synthesized `endContact` at drain time with `locked=false` |
| `body:setLinearVelocity(x,y)` (contrast) | applied | applied | applied | **applied** — `(55,-7)` persists into integration; trajectory changes |
| `body:setActive(false)` (edge) | refused | — | — | refused (assert); `isActive` stays true; world identical to baseline |
| `contact:setEnabled(false)` (edge, preSolve) | — | applied | — | **applied, single-step mask** (details below) |

**Fatal is the shape of the same assertion when *not* contained.** The
uncontained variants (`bc_setpos_unp`, `bc_newbody_unp`) die mid-cell:
**rc=1 at ~82 ms, `Error: … Box2D assertion failed: …` + traceback on
stdout, empty stderr, no `CELL_DONE`** — 2/2 reps, byte-identical. This
is the partial-capture pin the r74 author needs: uncontained interior
writes kill the whole run (Lua error escapes the callback through
`world:update` to boot's `xpcall`), they are not catchable by anything
upstream of a `pcall` around the write itself.

**Build determination (the brief's open question).** LOVE 11.5's vendored
Box2D is **2.3.2** (`b2Version b2_version = {2, 3, 2}`,
`b2Settings.cpp:26`) and LOVE **unconditionally patches the assert**:
`b2Settings.h:29-30` comments out `#define b2Assert(A) assert(A)` and
defines `#define b2Assert(A) loveAssert((A), #A)`; `loveAssert` **throws
`love::Exception("Box2D assertion failed: %s", …)`** (`b2Settings.cpp:
48-52`). So on this build asserts are **active but non-aborting** — they
surface as Lua errors at the nearest `luax_catchexcept` boundary. This is
a source-level property of LOVE's Box2D fork, not an NDEBUG accident;
`liblove-11.5.so` contains the strings `Box2D assertion failed: %s` and
`m_world->IsLocked() == false`.

## Method

- Scratch probe `corpus/live/r74-scout/probe/` extends the r70/frontier
  `phys_probe` shape: same headless conf profile, same ground/b1/b2/b3
  contact scene, `world:update(1/60)` stepping, EM lines. Cells selected
  by `R74_CELL`; grammar `<when>_<kind>` (`bc|pre|post|ext` ×
  `setpos|setvel|newbody|destroy|setactive|contactmask[_diag|_b3]`,
  plus `*_unp` uncontained variants).
- One cell per process ⇒ a fatal cell cannot truncate other receipts;
  interior cells run after all controls, uncontained cells last.
- `run_cells.py`: bounded `Popen`, timeout+SIGKILL, rc/signal, wall ms,
  per-rep stdout sha256, mechanical classification from evidence keys;
  receipts `cells/<cell>.r{1,2}.{stdout,stderr}.txt` + `.json`,
  `summary.json`, `summary.md`, `state.txt`.
- Trigger: first event of the target callback type for body `b1` (fast
  TOI contact, step 73) or `b3` (resting narrowphase contact, step 4).
  `world:isLocked()` is read inside every callback: **all four callbacks
  dispatch with `locked=true`** (baseline, 2/2) — the frontier's
  `in_step` pin, now the real API.

## Evidence per class (verbatim receipt lines, `cells/*.r1.stdout.txt`)

`bc_setpos` (refused; pre/post identical, err string differs only in the
guarded expression):
```
fire cb=bc kind=setpos step=73 locked=true count=4 pos=400,520.1500244140625 vel=0,763.8724365234375
cb_setpos ok=false err=Box2D assertion failed: m_world->IsLocked() == false pos_after=400,520.1500244140625
after_update step=73 count=4 b1pos=400,511.13113403320312 b1vel=0,-611.09796142578125
final steps=200 count=4 b1pos=400,445.10910034179688 … counts bc=5 ec=4 pre=36 post=36
```
(`pos_after` unchanged; post-update physics == baseline. `pre_setpos`/
`post_setpos` receipts differ only in the fire line pose — postSolve fires
at the post-step pose `400,511.13/-611.10`, consistent with the frontier
channel split.)

`bc_newbody` (refused, no allocation):
```
cb_newbody ok=false err=Box2D assertion failed: IsLocked() == false count_before=4 count_after=4
```

`bc_destroy` (deferred; identical shape for `pre_destroy`/`post_destroy`):
```
cb_destroy ok=true err=nil alive_in_cb=400,520.1500244140625 count_after=4
evpin cb=ec locked=false step=73
after_update step=73 count=3 b1pos=ERR:Attempt to use destroyed body. b1vel=ERR:Attempt to use destroyed body.
```
The destroyed body stays live and readable for the rest of the step
(its same-step preSolve/postSolve still fire: trace `step=73 bc=1 ec=1
pre=1 post=1`), then the post-Step drain destroys it; the drain
synthesizes an `endContact` **with `locked=false`** (Box2D destroys the
touching contact during `DestroyBody`). `world:getBodyCount()` inside the
callback still counts it (4); after `world:update` returns, 3. Reading
the destroyed body afterwards raises `Attempt to use destroyed body.`
(`wrap_Body.cpp:31-37`). World survives to step 200 (`final … count=3`,
b2 resting normally).

`bc_setvel` (contrast — gating is class-specific, not "callbacks are
read-only"):
```
cb_setvel ok=true err=nil vel_after=55,-7
after_update step=73 count=4 b1pos=400.78515625,519.7547607421875 b1vel=55,-7
```

`bc_setactive` (edge):
```
cb_setactive ok=false err=Box2D assertion failed: m_world->IsLocked() == false isActive_after=true count_after=4
```
`final … counts bc=5 ec=4 pre=36 post=36` — byte-identical to baseline
(no effect). Source: `b2Body.cpp:454-458` has an assert-only guard with
no release-path early return; here the assert throws *before* any
mutation. On a build whose `b2Assert` aborts, this same cell would be
fatal — carry the build key.

`bc_setpos_unp` (uncontained; fatal shape):
```
fire cb=bc kind=setpos_unp step=73 locked=true count=4 …
Error: main.lua:88: Box2D assertion failed: m_world->IsLocked() == false
stack traceback: … [C]: in function 'setPosition' … [C]: in function 'xpcall'
```
rc=1, stderr empty, no `CELL_DONE`; `bc_newbody_unp` identical shape via
`[C]: in function 'newBody'`.

Exterior controls (`ext_*`, outside callbacks): all three mutations
apply — `ext_setpos` pos becomes `1234.5,678.9`; `ext_newbody` count
4→5; `ext_destroy` **immediate** (dead right after the call: count 4→3,
`b1pos_after=ERR:Attempt to use destroyed body.`). The
immediate-vs-deferred contrast is the cleanest discriminator for the
author's control rows.

## Edge: `contact:setEnabled(false)` in preSolve — single-step mask

`pre_contactmask` / `_diag` / `_b3` (mask on the resting b3 contact
instead) — all applied, 2/2:
```
cb_contactmask ok=true err=nil isEnabled_after=false isTouching=true
```
- Same step: the contact is excluded from the island solve — **postSolve
  for that contact is skipped** (`trace step=73 bc=1 ec=0 pre=1 post=0`;
  baseline `post=1`), the body keeps its velocity and sinks
  (`after_update … b1pos=400,531.054443359375 b1vel=0,763.8724365234375`;
  baseline `400,511.13 / -611.10`).
- The flag does **not persist**: `b2Contact::Update` re-enables every
  contact each update (`b2Contact.cpp:165-166` — "Re-enable this
  contact"), so this is the documented one-way-platform pattern's
  single-step semantics.
- Resume step: the same contact id reports **pre×2 + post×2** (`trace
  step=74 bc=0 ec=0 pre=2 post=2`), with the second solve restarting
  from the pre-step pose (diag positions: `pre 531.05 → post 520.30 →
  pre 531.05 → post 509.53`). Static anchor: the same `b2World::Step`
  TOI pass re-`Update`s and re-solves a candidate contact
  (`b2World.cpp:604-612` candidate loop, `:735` second
  `minContact->Update`, `:739-743` solidity re-check); the island builder
  had skipped the disabled contact (`b2World.cpp:468-473`). **Inference
  (not directly traced):** the second pair is that TOI-path solve — the
  observed pose sequence matches, but the exact TOI-selection criterion
  was not resolved.
- Net deltas vs baseline: `pre 36→38`, `post 36→37`, `endContact`
  74→75, b1 final y `445.11→461.55`. Reproduces identically on the
  b3-resting witness (`trace step=4 pre=1 post=0; step=5 pre=2 post=2;
  step=6 pre=1 post=1`), so it is generic to mask-then-resume, not a
  TOI-contact artifact.

## Observed vs inference vs gaps

- **Observed:** all of the above — receipts under
  `corpus/live/r74-scout/cells/` (+ `summary.md`), run 2×, byte-identical
  per cell (diag cell: only `cid=` heap addresses differ, ASLR).
- **Inference (moderate):** TOI-pass attribution of the resume-step
  double solve (source-anchored, pose-consistent; not traced).
- **Gaps / not measured:** `world:destroy()` inside a callback (LOVE
  defers it via `destructWorld`, `World.cpp:575-584` — untested);
  double-`destroy()` in one step; `contact:setEnabled` in
  beginContact/postSolve; sensor/bullet; a build whose `b2Assert`
  aborts (none on host). The wave scout brief's audio viability gates
  (paplay/aplay/ffplay) and the g3d `PhysicsServer3D`/Jolt inventory are
  **sibling-seat scope and are not measured here**.

## Notes for the r74 author (pins)

1. Gating pins per class: refused (`setPosition`, `newBody`) =
   `ok=false` + `err=Box2D assertion failed: …` + no state change;
   deferred (`destroy`) = alive-in-callback + count−1 after
   `world:update` + `getPosition` error after; contrast (`setLinearVelocity`,
   `contact:setEnabled`) = applied inside the callback.
2. Partial-capture detection (the brief's requirement): require a
   per-cell done marker; uncontained interior writes produce **rc=1 +
   assertion text on stdout + no marker at ~82 ms** — a measured FAIL,
   not a truncated pass. Keep interior cells last and one-per-process;
   pcall containment flips a fatal-shaped cell to a refused row.
3. Determinism: surviving cells byte-identical 2/2 (frontier lattice was
   ×7); fatal cells also byte-identical 2/2.
4. The box2d layer runs `locked=true` in all four callbacks — pin
   `world:isLocked()` as the in-callback state key.

## Reproduce

```
cd corpus/live/r74-scout && sh reproduce.sh     # 22 cells × 2 reps, ~25 s
# exits: every control/refused/deferred cell rc=0; the two *_unp cells rc=1 BY DESIGN
```
Receipts: `cells/` (66 files), `summary.{json,md}`, `state.txt`
(probe/driver sha256 + git HEAD), `love_src_excerpts.txt` + `src_cache/`
(11 fetched sources with per-file sha256).
