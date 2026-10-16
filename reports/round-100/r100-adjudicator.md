# r100 adjudication — GUI/Viewport input-routing capstone lattice

Landing: 2dcbb6f6; repairs 9ede7c50 + 619ad7e0; harness fix b970a6d1. Verdict: **ADMIT-with-findings**.

## Gate tally
- critic: PASS-wf — F1 SYSTEMIC: no gate could see dup/dropped/renamed CASES rows (25-tuple drop-mutant still PASSed 491/491, vacuous gate). FIXED: cases_integrity gate landed b970a6d1. F2 seq rows pin 1-of-14 replay cells (first-divergence scope).
- reviewer: rows PASS (two 519/519 on committed bytes; artifact findings F1-F3 = landing splices, all repaired)
- scribe: BROKEN at receipt->commit link (evidence-rebase class); committed-bytes green re-derived 519/519
- simplifier: PROVEN (-6 net; strongest fold superseded by 9ede7c50)
- verifier: VERIFIED-WR — 519/519 x2 pinned, 576+441+22 mutations reject, dead-entry battery discriminates

## Findings carried forward
- CF1 systemic evidence-rebase class recorded across r98/r99/r100 (branch numbers vs landed: 509 CASES/516 rows final)
- CF2 seq-row pins cover first-divergence only (F2) — multi-line transcript pin queued
- CF3 stale .pyc churn pattern closed at 619ad7e0
- CF4 cases_integrity gate now hardens the entire union-landing defect class (b970a6d1)

## Lane note
g2d round-100 capstone closes a four-round integration stack; all defects found by wave-B were integration-process defects (union splices, evidence rebase), repaired at 9ede7c50/619ad7e0/b970a6d1. Author-side evidence intact in every round.
