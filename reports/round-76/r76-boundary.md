# r76 boundary — static source trace (read-only seat)

**Provenance note (integrator reconstruction, 2026-10-15):** the r76
boundary seat ran under a read-only toolset (no exec, no writes —
`ufo-labrat` profile limitation discovered this round). Its output was
consumed live by the wave and relayed into the adjudicator record, but
the seat never wrote this report file itself; the r77 scribe flagged the
absence (its audit finding 1). This file reconstructs the seat's findings
from the in-conversation record so the ledger resolves. Live-probe
boundary work resumes in r77 on exec-capable seats; the predictions
below are exactly what the r77 author armed.

## Behavior

Static source trace against the pinned LOVE 11.5 source tree
(`/tmp/r74bsrc/love-11.5` per the r75 baseline extraction). No live
probes run — **all forward statements below were PREDICTIONS at seat
time**; the r77 scout measured them and the r77 cells pin the results.

## Confirmed source anchors (traced this seat)

- `World.cpp:272-297` — the update-73 epilogue containing the drain;
  the joint-drain bracket (`jwlive` last callback seeing the queued
  joint → `jdrain` after `world:update` returns) is consistent with
  the epilogue being the only code in that window.
- `Body.cpp:529` / `Fixture.cpp:339` / `Joint.cpp:167` — the
  `isLocked` destroy-guard sites; destroy-in-cb refusal mechanics
  confirmed at source.
- `World.cpp:98` — `lua_call(L, args, 0)`: `preSolve` return value
  unconsumed; `pre_retfalse` → `ignored` is source-exact, not inferred.
- `mode=unp` falsifiability cap confirmed by construction: for
  non-throwing writes the containment axis is unobservable — the label
  catches branch-misdirection only (a wrong-branch spawn emits no
  `mode` field). Inertness is measured twin-identity, not a defect.

## Predicted cells (all subsequently measured by r77-scout)

1. **drain-EC throw retry** — uncontained throw inside a drain-phase
   endContact → distinct signature vs callback-time throw (locked=false
   at drain; re-fire next step at locked=true). *Predicted.*
2. **drain-EC write legality** — writes at locked=false inside drain EC
   apply; destroy() there is IMMEDIATE not deferred. *Predicted.*
3. **destroyb3 isDestroyed ordering** — cheapest upgrade of the joint
   drain bracket from inferred to measured: `isDestroyed()` inside the
   drain EC observes the mid-drain state. *Predicted.*

## Honest limits

- No execution evidence was produced by this seat; every anchor above is
  a static trace. `corpus/live/r76-boundary/` does not exist.
- The r76 adjudicator's "9/9" seat count should read 8/9 executed
  reports + this reconstructed record.
