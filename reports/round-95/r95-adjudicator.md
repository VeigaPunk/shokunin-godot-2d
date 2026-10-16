# Adjudicator report — round 95 (DirectSpaceState2D query + order lattice)

DECISION: **ADMIT-with-findings** on `9cd47507`. 52 rows (314->366). All five gates landed:
verifier VERIFIED-WR (468/468 instances, rep3 366/366, floor gate load-bearing), critic
PASS-WR, reviewer PASS, simplifier PASS (-5 queued), scribe CUSTODY HOLDS (4780 mutants reject).

Encodings that survived: k(k-1) cycle ladder k=2..10 (window-doubling probe confirms, no
window artifact), perm0-7 creation permutations, cap40 set32_distinct=5, co-presence
attribution (layout_changes_order falsification folded), warm/readd/layers/rigid laws.

Fold queue:
1. celloff_y1000 never reads --offy (reviewer F1 + simplifier F1, 2-seat): byte-dup of
   celloff_x0; Y-translation unmeasured not falsified. Fix --offy or drop the row.
2. order_core rows unfalsifiable (critic F1): pinned signature is the probe's own echo —
   mutants deleting the queries emit identical PASS. Bind a measured vector.
3. rigid is 60-tps-only (critic F2): tps120 relpos FAIL, tps30 distinct_ticks FAIL —
   1 of 52 rows; cheap fix on the t<=5 ladder prefix.
4. Simplifier -5 lines (15 dead stores / 18 sites, proven + green battery on folded tree).
