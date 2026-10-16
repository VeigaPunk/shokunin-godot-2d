# Adjudicator report — round 94 (GPUParticles2D / CPU-emission lattice)

DECISION: **ADMIT-with-findings** on `c7228893`. 19 rows (295->314). All five gates landed:
verifier VERIFIED-WR (95/95 row-instances, fold 3-way verified incl. pre-fold probe REJECT),
critic PASS-WR, reviewer PASS, simplifier PASS (-3 queued), scribe CUSTODY HOLDS (314/314
archive-extract green, 1101 mutants reject).

Encodings that survived: cpu_pause ff30 envelope [1,7] (fold verified 3/3 both fps), round->floor
in request ladder (floor fits 7/7 where round fails at 0.20/0.30), tombstone-free emission
census, gpu_headless arms, floor gate proven loud via dead-entry folds.

Fold queue:
1. cpu_contam tautology (critic F1 + verifier F1, 2-seat): signature is out.size() bookkeeping —
   falsifying mutant passes. Needs a tail-value arm or re-scope.
2. tps exposure is 10-11 rows not 3 (critic F3 + verifier measured tps30=10, tps120=11).
3. cpu_request floor fold inert at the two authored steps (boundary's 0.20/0.30 not in fixture).
4. Simplifier -3 (2 write-only stores) unapplied.
5. Custody nits: scout mixed-revision receipts (135/143 pre-freeze); author smoke receipts
   not preserved.
