# r85 adjudicator — camera/canvas transform lattice

**Verdict: ADMIT-corr** (corrections applied in fold; all verified live).

## Inputs

- Scout: camera/canvas transform lattice — 15 arms author-ready, clean
  merge rehearsal (174/174, 15/15 camera_proc).
- Author (finisher): `camera_proc.gd` 20/20 standalone, 174/174
  rehearsal, ablations clean; CASES rows embedded for fold.
- Verifier (pre-correction build): two fresh 174/174, exact 15-row pin
  equality, prior-159 zero drift, forge-kill live → ADMIT recommended.
- Critic: 7 counterexamples — all resolvable by additive witnesses
  (C1–C7, table in r85-fold.md). No claim-refuting finding.
- Boundary: 14 named classes, none falsified a pinned value; F5 narrowed
  the "camera writes cached" headline (zoom/offset/anchor/limit writes
  are live; only transform writes defer).
- Simplifier: none dispatched this round (fixture was new-file; nothing
  to fold out).
- Scribe: F2 (medium) — record-level, no semantic defect; resolved via
  the author-table wording correction under F5.

## Decisions

- **ADMIT** the 15-row lattice. Fixture classes: composition law, zoom-center
  anchoring, write-timing visibility ladder, subpixel step, four transform
  spaces, CanvasLayer stack/follow/draw-order, SubViewport world isolation
  and render-independence, ParallaxLayer/Parallax2D/ParallaxBackground
  splits, parallax phase timing.
- **CORRECTIONS (fold)**: C1–C7 additive witnesses landed; 8 rows
  re-pinned under battery context; F5/F2 wording narrowed.
- **BOUNDED (recorded, not corrected)**: boundary's 13 remaining
  edge classes (smoothing `speed*delta` divergence/NaN, empty/inverted
  limit → midpoint clamp, zoom `is_zero_approx` floor with INF/NAN
  degenerate transforms, stateful drag, parallax zoom/parentage
  variance, physics-interp timing). Host: Godot 4.7.2.stable
  arch_linux headless, scratch project viewport 64×64.
- **HELD-OUT**: SCORECARD.md foreign edit remains uncommitted (fleet
  artifact, not this lane's round work).

## Evidence

- `corpus/live/r85-foldc-final2/20261015T085238195177Z/verdicts.json`
  — 174/174 on final folded bytes.
- `corpus/live/r85-foldc-arms/` + standalone arm captures — witness
  tokens verified before re-pin.
- All seat reports: `reports/round-85/`.
