# R74 adjudicator (Sol) — LOVE physics interior-write lattice

Round: 74. Wave: `shokunin-train-20261101-w14` (**recovery dispatch** — the
first seat generation died with its dispatching session ~16:10Z; all landed
work below is the 16:20Z+ respawn generation, with dead-seat scratch
verify-reused where sound). Work commit `ae6cb16` + folds `35dcbf7`.

## Declared move

Fold the pre-measured `love.physics` frontier into the tracked battery:
writes inside Box2D callbacks (beginContact/preSolve/postSolve) gated per
class — `{refused | deferred | fatal | applied}` as the falsifiable
partition; interior cells ordered last; partial-capture is a measured FAIL.

## Claim adjudication

- **The four-class partition is CONFIRMED** — 37/37 on the landed tree,
  verifier AGREE 13/13, per-cell byte-identical receipts across 6
  independent runs (concat sha `58af4e7e…801f86`): refused ×7 (catchable
  `IsLocked()==false` loveAssert), deferred ×3 (destroy drains in the
  update epilogue, synthesized EndContact `locked=false`), applied ×5
  (setLinearVelocity, `contact:setEnabled` measurably suppressing the
  impulse `0,763.87` vs `-611.09`), fatal(lua) ×2, captured ×1.
- **Class names scoped by corrections** (folded `35dcbf7`): `fatal` as
  landed = fatal(lua); the boundary's uncontainable SIGABRT class
  (`m_abort` port: rc134, `p == entry->data`, 2/2 byte-identical)
  classifies `died` — distinct classes, correctly separated. Critic C1
  stands: `unp ⇒ fatal` is true only for assert-gated structural writes;
  docstring now says so. C3 (containment-level relativity — pcall around
  `world:update` produces a materially different refuse-with-step-abort
  state the classifier reads as `refused`) is **recorded, not folded**:
  closing it needs an additive cell (receipt-invalidating) → r75 frontier.
  C1's additive twins (`bc_destroy_unp`, `bc_setvel_unp`) same → r75.
- **Boundary lattice upheld** (54 cells, ≥2 reps byte-identical + 8× load
  replay): endContact joins the callback set; re-entrancy defeats the lock
  (nested `world:update` → subsequent setPosition *applied*);
  destroyed-handle total unusability (10/10); build answer recorded
  (asserts-on, loveAssert throw — `b2Settings.h:29-30`, anchored by
  tarball + `strings` on `liblove-11.5.so`).
- **Carried guard falsified (again)** — FIFO-open block is NOT
  SIGTERM-immune under LOVE 11.5 (`open` → EINTR, clean exit); the Lua
  busy-spin is. `timeout -s KILL` on the fifo cell forfeits the DONE
  marker: receipt completeness is the verdict carrier, not rc.
  Guard restated consumer/host-locally; this is the second consecutive
  wave a carried guard needed narrowing (w13 pw-cat/audio, w14 love).

## Seat accounting

9/9: author `ae6cb16` (+292/−0 battery, new `love_phys_probe/`, cells
ordered last, 4 author receipts); scout (prior gen, verified-reused);
boundary 54-cell extension incl. 2 hard-fatal cells + nested-update
re-entrancy; critic C1–C3 MED folded/scoped (C5 comment fix landed);
reviewer ACCEPT no HIGH/MED (D1 drain-wording folded); simplifier D1–D3
folded byte-identical (`evpins` dead param/return; battery stdout
`a5ada1ee…` + receipts `58af4e7e…` preserved — integrator re-verified on
`35dcbf7`); scribe superseded the dead draft, forge-accept + forged-line
findings recorded for the parser axis; baseline zero-drift on freeze
`1275746` (44,873 members; godot 88, love 19, pygame 80 pre/post);
verifier AGREE 13/13 on `ae6cb16` (6-run receipt identity).

## Recovery note

The r71-critic `wvtail.wv` orphan, r72-simplifier snapshot dirs, and the
round-71 late reports (`r71-{reviewer,scribe,verifier}.md`) remain
uncommitted working-tree residue from earlier waves — recorded, left for
the integrator's sweep decision; they are not r74 scope.

## Verdict

**ADMIT-corr** — partition confirmed with named-class scoping; two
additive critic cells + the containment-level cell deferred to r75 as the
declared frontier. Bounded: LOVE 11.5-3 (Arch), LuaJIT 2.1.1788460057,
Box2D via loveAssert-unconditional build, this host.
