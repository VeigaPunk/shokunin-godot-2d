# game-dev-2d round 74 — author (seat: author; host: devin)

## Declared move (verbatim)

"ARM — fold the pre-measured love.physics frontier into the tracked
battery: writes inside Box2D callbacks (beginContact/preSolve/postSolve)
are gated per class — {refused | deferred | fatal} is the falsifiable
partition. Extend corpus/fixtures/love_battery.py (or the love probe
fixture, whichever carries the r70 splice cells):
- in-step mutation cells: setPosition/newBody/destroy inside
  beginContact — pin each class's actual gating (the frontier measured
  in_step=true + per-callback channel-split snapshots, byte-identical
  determinism x7)
- interior vs exterior write contrast cells (the same mutation outside
  the callback = control)
- contact-mask / active-body availability edges
Order interior-write cells LAST (a fatal crash kills the probe early —
frontier note); pin partial-capture detection so a crash mid-arm is a
measured FAIL not a silent truncated receipt.
Viability: love2d on host (r70 established). Box2D debug-vs-release
assert behavior is build-dependent — record which this build is.
pygame battery untouched = control. Report -> reports/round-74/r74-author.md."

Recovery context honored: wave-14 recovery dispatch; prior generation
died ~16:10Z. Sibling scratch verified and reused (see Evidence).

## Landed changes

- `corpus/fixtures/love_phys_probe/` — NEW fixture dir (2 files,
  purely additive): `conf.lua` (strict headless profile,
  physics+timer+event kept) + `main.lua` (~235 lines). One cell per
  process via `IW_CELL` env; emits `IW | cell=<c> | <tag> k=v` lines
  flushed per line + bare `CELL_DONE`. Scene = the r70 frontier
  phys_probe scene verbatim (static ground + b1/b2/b3 dynamic), so
  fire-step and pose pins inherit the frontier's byte-identical
  determinism. Mutations fire only on b1's first contact of the
  selected channel (bc/pre/post at step 73, TOI-dispatch pose;
  ext_* cells run in love.load = the unlocked exterior control).
  `*_unp` kinds skip pcall so the assert escapes the callback and
  world:update -> process death.
- `corpus/fixtures/love_battery.py` (+292/-0; `git diff` shows zero
  removed content lines — every prior CASES/SPLICE_CELLS row
  byte-identical):
  - docstring: r74 lattice paragraph appended (the {refused|deferred|
    fatal|applied} partition + ordering rule).
  - `IW_PROBE_DIR` constant; `IW_CELLS` table (18 rows:
    case, cell, expected_class, {flat_key: pinned}); `parse_iw`
    (space-tolerant kv parser — values run to the next `word=`
    boundary, so assert text and `ERR:` strings parse cleanly);
    `iw_classify` (capture shape -> class) + `iw_flat_extras`
    (synthesized `rc`/`done`/`err_on`/`assert_txt`/`evpin_*` keys).
  - `main()`: IW loop after the SPLICE loop — one `love` launch per
    cell, `iw-<cell>.{stdout,stderr}.txt` receipts, per-cell verdict =
    class match AND all pins via the existing `check()`.
  - Partial-capture detection is structural, not advisory: expected
    class "fatal" requires fire-line present + CELL_DONE absent +
    rc!=0 + assert text on stdout; any contained cell that dies ->
    cls "fatal"/"died"/"timeout" != expected -> measured FAIL with the
    detail in `reasons`. A crash mid-arm can never pass as a
    truncated receipt.
- `corpus/fixtures/love_probe/` and `pygame_battery.py`/`pygame_probe.py`
  UNTOUCHED (control; `git status` shows no modifications there).

## Measured result (37/37 PASS, 4 stable reps)

15 prior CASES + 4 splice cells + 18 new IW cells; every IW case PASS
in all four runs. Concatenated `iw-*.stdout.txt` sha256 identical
across all 4 run dirs:
`58af4e7e1bc6c754de7e3ad8dd55d75b1d1a05f1fbf831968092aeb116801f86`
— the interior-write lattice is byte-identical determinism, same
class as the r70/r73 pins.

The measured partition (this host, LOVE 11.5):

| cell | channel | observed | decisive pins |
|---|---|---|---|
| baseline | — | captured | evpin locked=true in all 4 cbs; bodies=4; bc=5 ec=4 pre=36 post=36 |
| ext_setpos | exterior | applied | ok=true pos_after=1234.5,678.9 (immediate) |
| ext_newbody | exterior | applied | count 4->5 in-line |
| ext_destroy | exterior | applied | count 4->3 + `ERR:Attempt to use destroyed body.` in-line (immediate, not deferred) |
| bc/pre/post_setpos | interior | refused | ok=false err="Box2D assertion failed: m_world->IsLocked() == false"; pos unchanged (bc/pre see pre-state 400,520.15; post sees post-state 400,511.13 — the frontier channel split pinned) |
| bc/pre/post_newbody | interior | refused | ok=false err="Box2D assertion failed: IsLocked() == false" (world-level fn drops the m_world-> prefix); count stays 4 |
| bc/pre/post_destroy | interior | deferred | ok=true, alive_in_cb pose readable, count_after=4 inside cb; after_update count=3 + b1pos=ERR; **drain evpin ec locked=false step=73** (destruction queue drains inside the update epilogue, unlocked, synthesized EndContact) |
| bc_setactive | interior-edge | refused | same m_world assert; isActive_after=true |
| pre_contactmask | interior-edge | applied | ok=true isEnabled_after=false isTouching=true; after_update b1vel=0,763.87 (NO impulse — mask suppressed the solve; contrast refused cells' -611.09) |
| bc_setvel | interior | applied | ok=true vel_after=55,-7 (non-structural write has no locked assert) |
| bc_setpos_unp | interior-uncontained | fatal | rc=1, CELL_DONE absent, "Error: ...m_world->IsLocked() == false" on STDOUT (stderr file 0 bytes) |
| bc_newbody_unp | interior-uncontained | fatal | rc=1, CELL_DONE absent, "Error: ...IsLocked() == false" on stdout |

**Build record (the brief's debug-vs-release question):** this build is
`LOVE 11.5 (Mysterious Mysteries)` / Arch `liblove-11.5.so`, LuaJIT
2.1.1788460057. The Box2D `b2Assert` surfaces through LÖVE's
`loveAssert` as a **catchable Lua error on every build mode** — r74-critic
F4 (strings+source) shows loveAssert is unconditional on this build, so
"refused" is not a debug-only behavior and the silent-refusal path is
dead code here. Uncontained, the same error kills the run via the LÖVE
error handler (rc=1, text on stdout) — the fatal class is a containment
fact, not a build fact. A build where b2Assert hard-aborts would flip
the refused cells to "died"/"fatal" — a measured FAIL, which is the
point of the partition.

**Design choice vs the dead generation:** the prior seat's scratch
(`corpus/live/r74-author/scratch_iw/main.lua`) was verified and its
env-per-cell + BEGIN/DONE architecture adopted, but its dispatch was
broken for uncontained cells (`CELL:match("_([a-z]+)$")` returns "unp"
as the channel, so `*_unp` cells could never fire — they would have
emitted unfired done-lines, a silent hole). The landed probe instead
ports the r74-scout probe verbatim (minus per-step trace spam and the
`counts` bare word that broke kv parsing) — its 22 cells x2 reps were
already byte-identical, so every pin in IW_CELLS is pre-verified twice
over plus my own x4 battery reps.

## Evidence

- `python3 corpus/fixtures/love_battery.py --runs corpus/live/r74-author/runs`
  -> `totals: cases=37 pass=37 fail=0 launch_ok=True done_marker=True
  exit=0`, battery exit 0, ~15 s wall, x4 reps:
  `love-20261014T163734563743Z`, `...T163751175528Z`,
  `...T163758511555Z`, `...T163805922987Z`.
  Per-run `verdicts.json` + `iw-<cell>.{stdout,stderr}.txt` receipts
  under each run dir.
- Standalone smoke before wiring: `IW_CELL=<c> timeout -s KILL 10 love
  corpus/fixtures/love_phys_probe` — all 18 cells; outputs identical to
  r74-scout `cells/*.stdout.txt` modulo the IW/R74 prefix and dropped
  trace lines (fire step=73, poses `400,520.1500244140625` /
  `400,511.13113403320312`, counts, err texts all match).
- Sibling corroboration (verified, not just trusted):
  `corpus/live/r74-scout/summary.json` (22 cells x2 byte-identical reps,
  same classes), `corpus/live/r74-critic/notes.md` F1/F2/F4/F6
  (containment-dependence, end-of-update drain at locked=false,
  loveAssert unconditional, error on stdout) and
  `battery_mutant/runs-fatal` (in-probe fatal = un-PASSable default run
  — why this arm uses one process per cell instead of arms inside the
  default launch).
- `git diff corpus/fixtures/love_battery.py`: +292 insertions, 0
  removed content lines. New dir `corpus/fixtures/love_phys_probe/`
  untracked-new. No other fixture touched. Nothing committed (leaf seat;
  integrator commits).
- `lsp` disclosure: no lsp/pyright/pylsp/python-lsp-server/jedi/
  lua-language-server on this PATH (`which` output in scratch; same
  host state r72/r73 recorded). All edits are additive insertions with
  no symbol renames, so no callsite risk; names verified by the four
  green battery runs.

## Remaining unknowns / risks

- `fire.step=73` and the pose pins are exact values of this scene on
  this build — deterministic x4 here (and x2 in scout), but they are
  physics-exact pins: a different Box2D/love build could legitimately
  shift the TOI pose while preserving every class. The class
  (`refused`/`deferred`/`fatal`) is the load-bearing assertion; exact
  poses document this host (same convention as `bufsize=131072`).
- `evpin_ec_*` for destroy cells pins the FIRST ec event = the drain
  ec. If another body's contact ended earlier in the scene the pin
  would catch it as FAIL (locked=true) — safe direction, but a scene
  edit must re-derive that pin.
- `assert_txt`/`err_on` synthesized keys scan raw stdout — a future
  LÖVE version printing the error to stderr flips `err_on` to "stderr"
  -> measured FAIL on the two unp cases (intended).
- `died` vs `fatal`: a signal death (negative rc, e.g. SIGSEGV instead
  of the Lua-error path) classifies "died" and FAILs unp pins `rc="1"`
  — deliberate: different death shape = different measurement.
- pygame battery untouched (control). No git mutations; commits remain
  operator-owned.

## Blockers

None.
