# Orphaned r101 companion fixtures (E3/E5/E6/E9)

These four scenario fixtures belong to seats E3/E5/E6/E9, which died on a
provider-side 400 (`reasoning_content` must be passed back) BEFORE writing
their shards or measured pins. State at retirement (this round, quiet host):

- export_prod_s03.gd — exit=2, no PASS line (incomplete determinism scenario)
- export_prod_s05.gd — exit=1, no PASS line (incomplete remap/UID census)
- export_prod_s06.gd — exit=2 with 4 partial PASS lines (filter scenario,
  arm-dependent)
- export_prod_s09.gd — exit=0, 1 PASS line (subdirectory census; the only
  one that runs clean)

Every one of their scenarios is covered by the landed `export_prod.gd` harness
rows (`export_prod_det_a/det_b`, `resource_remap_census`,
`include_exclude_filter`, `subdir_census`), so C1 breadth is unaffected.
They are kept here (out of `corpus/fixtures/`, which must stay runnable and
shard-backed) so a future round can adopt, complete, or discard them with
evidence. Do not register them in CASES without fresh measured pins.

## Design-superseded companions (E1/E2/E4/E7/E8/E10/E11)

`s01/s02/s04/s07/s08/s10/s11` COMPLETED their seats (shards + measured pins in
`reports/round-101/r101-E*.md`), but E0's landed `export_prod.gd` harness
consolidates all their scenarios into the 12 registered rows. Keeping runnable
but unregistered fixtures in `corpus/fixtures/` would recreate the census/hygiene
drift class (B2), so they retire here. A future round may register any of them
with the pins already in their shards — that is additive coverage, not repair.

## r104 disposition (2026-10-18)

Adopted with fresh measured pins (12 rows registered): s01, s02, s04, s09,
s10, s11 (all six moved back to corpus/fixtures/). The r101 README's
"provider-orphaned/broken" claims were WRONG for s03/s05/s09 — r104-S1
re-measured them healthy on HEAD; the true disposition per r104-S2 §5-6:
s03 RETIRE (quota-blind scratch probe + 15-30s nested export vs the 8s row
bound, unsatisfiable by design), s05/s07 RETIRE (S2 measured: not
gate-accountable on HEAD), s06 REPAIR-PENDING (GDScript typing defect at
:370 blocks classification; repair is a fixture edit, outside r104 seat
ownership). Retired fixtures stay here as evidence.
