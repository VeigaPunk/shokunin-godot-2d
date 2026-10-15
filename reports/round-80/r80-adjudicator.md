# R80 adjudicator — Godot-4 2D motion/query lattice (phys2d_motion)

Round: 80. Wave: `shokunin-train-20261101-w21/w22` mixed swe-2 / Sol /
ds-flash / zfl seats. Landing commits: this commit (author +
fold co-committed; the work commit carried +70 insertion-only CASES
rows and the new 879-line `corpus/fixtures/phys2d_motion.gd`, folded to
774 lines by the proven simplifier pass).

## Declared move

28-row `phys2d_motion` battery: CCD ladder/edge/gap/spin,
`body_test_motion`/`move_and_collide`/`test_move`/`move_and_collide`
family (from-default, embed, recovery_as_collision, chain, decomposed),
`PhysicsDirectSpaceState2D`/`body state` read arms (motion honoring,
embed, shapes, purity, wrongarg, windows), contact-window/persist/cap
cells. Insertion-only after the phys2d_events block; two
`expected_errors` entries (`mac_maxcol`, `dss_wrongarg`).

## Claim adjudication

- **Author evidence CONFIRMED** — 139/139 ×2 consecutive; verifier
  independent 139/139 ×2 with rep1↔rep2 tuple-identical on all 139
  rows. rep-1's single FAIL was the named SDL gamepad ERROR flake on a
  prior row (`cm_max0`), correctly rejected by the unrelated-error
  clause; baseline reproduced the same flake class on a different row.
- **Prior-row identity CONFIRMED** — 110/111 byte-identical tuples;
  the single delta is `probe_error_clause_surface`'s own census
  (43→45 rows, 53→61 ERROR lines = the landing's footprint).
- **Forges killed** — verifier: flipped signature detected, deleted
  row isolated (138/138 clean), neutered arm detected; critic:
  `dss_wrongarg` dead-entry forge demonstrated live pre-fold
  (`dead_entry_count=1` sailed through the phys2d_events_-scoped
  floor gate) → **C1 folded** (`startswith("phys2d_")`, census
  covers motion rows now); `ccd_edge` dead-wall forge → **C2
  folded** (`w[...]` `body_test_motion` witness into the wall face,
  `hit=true pt=(98,805) cls=StaticBody2D` pinned).
- **C3 advisory recorded** — `ccd_spin` remains a declared weak cell
  (blind to its own witness channel); boundary spec'd
  `bx_spin_clean`/`bx_cs_geom`/`bx_from_rec`/`bx_rec_edge` exec-ready
  arms for the next round.
- **Simplifier vfold LANDED** — 879→774 (−208/+103): dead teardown
  apparatus, `.name` writes, `_mk_rigid` unification, `_frames`
  consolidation, CCD-map const, spec-loop `btm_embed`, dead setup
  walls in refused-call arms; 139/139 both sides, 0 tuple diffs.
- **Boundary receipts audited** — scout `arms-verify.json` clean
  (28×3 byte-stable), threaded twin divergence named
  (`bds_windows` proc-gate), verifier cross-checks corroborated.
- **Scribe audit CLEAN** — CASES 28/28 byte-exact vs scout table,
  expected_errors truthful, conventions hold; F1–F7 record-level
  corrections absorbed into this record.

## Record notes

- `ccd_edge`/`ccd_spin` keep measured PASSES; `ccd_spin`'s label
  (weak cell) is honest, boundary arms queued to strengthen or kill.
- `cast_shape`≡`disabled` and `recovery_as_collision` inertness are
  this-geometry measurements — boundary specs exist to bound them.
- The floor gate now prefixes `phys2d_` — future phys2d_* batteries
  inherit dead-entry rejection automatically.

## Verdict

**ADMIT-corr** — the motion/query lattice is armed with
content-verified pins, a positive-witness edge cell, and a
floor-verified error allowlist. Seats: scout, author (swe-2),
baseline (ds-flash), boundary (audit, zfl), critic (Sol), verifier
(swe-2), simplifier (ds-flash), scribe (zfl); fold + adjudicator
swe-2.
