# r86 ADJUDICATOR — engine/backend-select lattice

Seat: ADJUDICATOR (orchestrator) | round 86 | work `7ae7083` + fold

## Verdict: ADMIT-corr

Admitted with corrections folded in-session. All eight seat reports on
record (author, baseline, scout, verifier, critic, simplifier, boundary,
scribe).

## What the round measured

`phys2d_backends.gd` — nested-boot engine/backend selection lattice,
8 arms: class/property census, stored-value→resolved-backend lattice
(6 cells incl. silent verbatim-store fallback on garbage/empty),
Jolt-is-3D-only positive control, manager refusal cross-check (2D/3D
split on identical name lists), threaded space-state gate matrix
(7 positions + fetch-free baseline), property-vs-explicit gate duality
(correcting r77's falsified law), Dummy degenerate-query payloads,
Dummy collider-access hang (external-bound timeout class).

## Record corrections applied in fold

- Critic forges: 16/18 PASS → `dur_ge` timing pin, backtrace-frame
  provenance (`tf`/`df`/`pf`/`af`), `cm0/cm1` fraction pins,
  child-side `offered` lists + `errs_total`, `errB` symmetry, `thr`
  stimulus pin, `_boot` stale-capture purge + exec-failure class,
  `enum%d` real count, `stored_has` presence flag.
- New latent bimodality discovered during rep runs and enveloped:
  gate deferred-fetch can land inside the threaded physics window
  (`dual_ok`/`thr_ok` mode envelopes); `moved` frame-count coupling →
  `mv=pos|zero` class; `dur_ms` jitter → `dur_ge` threshold. Same
  envelope pattern as g3d r90 — the fix is honest mode admission, not
  a deterministic re-pin.
- Boundary: no pin falsified; B4 new class (gate is a GodotPhysics-server
  property — vacuous under Dummy) recorded; armed-unrun harness filed.
- Scribe: claim chain clean, F1–F6 non-blocking.
- Simplifier: vfold −4L applied, 16/16 byte-identical pairs.

## Evidence status

- Battery 182/182 PASS on folded bytes (`20261015T160405358447Z`),
  verifier 182/182 ×2 pre-fold, 24-rep stability pre-fold, 8 arms ×3
  stable post-fold, forge-kill re-armed (f09/f14-class now requires
  real paths).
- Boundary B8–B14 armed-unrun filed for a future exec-capable seat.
- `SCORECARD.md` foreign-fleet rubric edit remains held out, uncommitted.
