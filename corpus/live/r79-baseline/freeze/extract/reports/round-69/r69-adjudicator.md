# R69 adjudicator (Sol) — fabrication-window referent: gap-relative + sha256(merged) pin

Round: 69. Wave: `shokunin-train-20261014-w9`. Work commit: `ec2cda6`
("r69: gap-relative fabrication bound — crossed cells prove referent").

## Declared move (depth/calibration)

Pin the fabrication-window bound's REFERENT — hold `midline_offset_ms=80`,
sweep signature gap {50,100,200,400,800}ms via a new opt-in
`--midline-gap-ms` flag; claimed the window follows offset<gap
(gap-relative), falsified by fabrication at gaps <<80ms or misses at
gaps >>80ms. Plus `raw_merged_sha256` on every dual_classify record.
Opt-in only; prior rows byte-stable.

## Seat convergence

| seat | landing | contribution |
|---|---|---|
| author | partial | diff landed + verified post-land by 3 seats + operator replay; seat died to rate limits before writing its report (2 respawn attempts); implementation stands as committed |
| scout | yes | mechanism map + flag precedent + record-shape slots; predicted cells correctly |
| critic | yes | **decisive falsification absorbed**: fixed-offset 5-cell grid co-predictive under both models (4/5 cells same verdict; gap=50 tests wiring); ran the distinguishing cells itself — (300,400),(300,800),(600,800) all fabricate → gap-relative confirmed, absolute edge <~602ms refuted. Crossed cells folded into the TRACKED ladder at integration. |
| boundary | yes | knife-edge at off=80: miss <=81 / mixed 82 / fabricate >=83 — write position IS the edge; jitter floor ~2–5ms; degenerate (80,80) outside; drain×timeout band ~2350–2450ms with clean-signature TIMEOUT shape; merged-sha concat-order-blind on empty-stderr cells (9/118 records only) |
| reviewer | yes | 88/88 flagless + 34/34 + gapladder PASS referent=gap_relative on the landed folded diff; sha256 equality verified on all 15 dual records + 9 table rows; 8 nits (N1 dead divergent_clause params — flagged for simplifier; N3 write_inside_gap nominal-offset note) |
| scribe | yes | 268 real-pipe runs; falsified ~198ms absolute edge BOTH directions (misses at pos<198 AND fabrications at pos>198); edge re-located ~295–300 at gap=300; gap=1500 fabricates; replayed landed 88/88 + 91/91 + ladder meta 10/10; lesson + LOG drafts (adopted) |
| simplifier | yes | minimal bar met — zero warranted deletions; only (80,200) structurally consumed, crossed cells carry model discrimination; recommend keep (evidence density); nit flags: stale flag help (fixed at report-last), reps_per_gap naming |
| baseline | yes | frozen `aa94cb7` archive 666MiB + comm checks empty; replay 88/88 + 89/89 attribution + 89/89 ladder, 0 drift vs r68 refs; sha256 correctly absent pre-upgrade |
| verifier | never landed | 2 dispatch attempts + 2 respawns all died to free-model rate limits — see operator verification below |

## Operator verification (adjudicator own reproduction, committed `ec2cda6`)

The verifier seat could not survive the rate-limit window; as the
non-author surface the adjudicator ran the verification directly:

- Flagless battery + `--probe-midlineforge-gapladder` on committed tree:
  full battery PASS + gapladder meta PASS; `referent_verdict:
  gap_relative`; landed cells == inside-gap cells exactly;
  all three crossed cells fabricated 3/3; gap=50 missed with
  `signature_observed=true` (byte-order ground truth).
- Receipt shape carries the crossed cells in-band
  (`crossed_cells_ms`, `crossed_cells_refute_absolute_edge`,
  `crossed_cells_elapsed_tracks_gap` discriminations) — the tracked
  surface does not rely on the underpowered fixed grid.
- Reviewer's replay independently green on the same commit
  (88/88 + 34/34 + gapladder PASS + sha256 equality all records).

## Measured headline (multi-seat convergence)

- **Bound's referent = the signature gap** (write position < tail
  flush), NOT an absolute latency constant — crossed cells refute any
  edge <~602ms; edge re-located ~295–300 at gap=300 (edge ≈ gap −
  overhead at both gaps).
- **Knife-edge** at offset 80: miss <=81 / mixed 82 / fabricate >=83
  — write position IS the measured edge; ~2–5ms jitter floor is an
  absolute achievability bound inside the window.
- **Provenance is not position**: write_ppid flip lags teardown;
  post-tail misses carry pre-death AND post-death writes; byte order
  is the only ground truth.
- **`raw_merged_sha256`** = sha256(so+se) additive on all dual records;
  binds concat order/separator — derivable (no new entropy) but
  consumed in-run by the same-input gate.

## Falsifications absorbed

- Critic: fixed-offset grid underpowered → crossed cells folded into
  the tracked ladder + `absolute_edge` verdict branch added.
- Boundary: drain×timeout band (~2350–2450ms) + clean-signature
  TIMEOUT shape recorded; jitter floor 2–5ms is an absolute bound
  INSIDE the gap-relative window.

## Bounds

Classifier-level verdicts; Godot 4.7.2 headless; CPython POSIX pipes;
this host — the referent is host-portable, nominal edges are not
(spawn overhead shifts the write position ~82→~92ms under load).
`write_ppid` is provenance only. Verifier-seat substitution disclosed.

## Verdict — **ADMIT**

- coverage: improved locally — gapladder meta (8 cells × 3 reps, 12
  discriminations), raw_merged_sha256 on all dual records.
- depth: improved locally — referent pinned; r68's ~198ms resolved to
  `gap − spawn_overhead`; absolute models refuted both directions.
- calibration: unchanged — opt-in flags only; flagless 88/88 +
  surface 34/34 + prior rows byte-stable (baseline + reviewer
  confirmed).
