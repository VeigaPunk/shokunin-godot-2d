# r97 adjudication — SceneTree groups / signal-flags / call_deferred lattice

Landing: f67094bb. Verdict: **ADMIT-with-findings**.

## Gate tally
- scribe: HOLDS (custody clean; F1-F6 prose precision only)
- critic: PASS-WR (F1 frame-delta pin too weak; F2 gate filters fixture prefix not round prefix -> dead r97b entry passes silently)
- reviewer: PASS (438/438 x2 on pinned commit; 12/12 manual arms; 300/300 signature byte-equality)
- simplifier: PROVEN-LEAN (-21 verified fold, 516/516 both sides; queued not landed)
- verifier: VERIFIED (438/438 x2, 540/540 mutations, gate-mutant discriminates alone, 97/97 laws)

## Findings carried forward
- CF1 emit phys_defer_frame_delta (0=same frame) so the corrected ordering is falsifiable (critic F1)
- CF2 widen r97 gate tuple to ("stree_lattice_","r97_","r97b_","r97c_") (critic F2)
- CF3 queued fold -21 lines (simplifier; F6 provenance-row cost noted)
- CF4 prose/commit arithmetic: 419->431 not 420->432; fixture 941/+45 not 937/+41; "x3 consecutive" = x2 tail
