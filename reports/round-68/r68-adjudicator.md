# R68 adjudicator (Sol) — midlineforge fabrication-window bound + receipt upgrades

Round: 68. Wave: `shokunin-train-20261014-w8`. Work commit: `f754546`
("r68: midlineforge fabrication-window ladder + receipt upgrades —
strict nominal bound [0,~198) measured; divergent_clause map + sha256
same-input gate; discriminations 20->24").

## Declared move (depth/calibration)

Pin the fabrication-window bound on midlineforge as a measured ladder —
sweep descendant-write offsets {0,40,80,120,160,240}ms into the 200ms
signature gap; claimed strict bound [lo,hi) inside the gap with the r66
fabrication holding exactly within. Plus: `divergent_clause` signature
per divergence_table row + sha256(raw_{stdout,stderr}) per dual_classify
record. Opt-in only; prior rows byte-stable.

## Seat convergence

| seat | landing | contribution |
|---|---|---|
| author | yes | `descendant_pipe_probe.gd` +17/−4 (`--midline-offset-ms=N`, default 80 — bare arm byte-stable); `run_battery.py` +302/−2 (ladder meta + divergent_clause machinery + sha256 fields); 100/100 full-flag battery; caught the scout's sed-corruption artifact independently (first-match `sleep` sub → unmodified 80ms arm) |
| scout | yes | mapped mechanism (file:line: `printraw`/`delay_msec(200)`/`print` at :166–168; `sleep 0.08` hardcode at :159); predicted bound correctly; flagged unconditional surface meta → opt-in flag landed; own `off_*` series sed-corrupted (disclosed honestly; corrected series converges) |
| critic | yes | three falsifications absorbed: (a) strict measured bound is on write-position not nominal offset — grid resolves hi to (160,240] only, ~80× overstated; edge stochastic ~198.3–198.5, NOT 200 (exec-overhead shift); lo unreachable (~−1.7ms, `pre_head_standalone` regime); (b) divergent_clause mostly renames mechanisms (error_scan covers 3; exit dead; allowlist masked); (c) sha256 binds decoded text + tautological on declared axis (allowlists unhashed) |
| boundary | yes | window downward-unbounded (negative offsets all splice — lo_edge is spawn-latency floor); mixed cell at nominal 198 (1/3); TIMEOUT nondeterminism confirmed (stderr tail spread 44..56, seam under timeout, mid-line truncation); divergent_clause collisions on landed data; sha256 decoded-text collision b"\xff"≡b"\xfe" |
| simplifier | yes | minimal bar MET — all 6 rungs + 12 new discriminations load-bearing (40/120 = contiguity witnesses; reps=3 required for mixed-cell semantics); mirror fidelity proven via AST truth table (0/132 mismatches); TWO byte-identical deletions applied as `e8d4fb7` (dead `exit` tautology :2480-2481, duplicate `signature_gap_ms` :2157); optional finder-idioom extraction declined (borderline under r67 bar); sharpest stability form: artifact == baseline modulo exactly the declared-upgrade fields |
| reviewer | yes | r67 committed state survives: 88/88 + 89/89 + 34/34 + 20/20 + 9/9 rows byte-identical; own re-derivation of the 4-family map on real pipes (12 divergent arms); "12/27" vs "12/28" denominator nit (committed artifact enumerates 28) |
| scribe | yes | VERIFIED sharper than worded (~256 own runs): bound {0–198} fabricate / 198.05–198.35 transition / ≥198.5 never; straddle H-E-T-E2; rejects both sides; ppid invariant; both receipt upgrades verified (9-row clause map, 24 sha records, digest chain closed); lesson+LOG drafts adopted |
| baseline | yes | frozen `1101cb3` archive-only (625MiB tar, deterministic digest); replay 88/88 + 89/89 + 34/34 + 20/20, 0 drift |
| verifier | yes | **AGREE 5/5** on `f754546` — 18/18 grid exact; own instrumented edge ≈198 (2.09ms mean latency); divergent_clause recomputed **from spec** (not mirrors) 9/9; sha256 verified on 15 records; 24/24 discriminations; prior 0-mismatch ×5 comparisons; opt-in proven |

## Measured headline (multi-seat convergence)

- **Fabrication window = write-position bound**: lands iff the
  descendant write reaches the captured pipe between head-flush and
  tail-flush (gap 200.02–200.16ms). Nominal-offset space: {0–198}
  fabricate rep-perfectly, 198.05–198.35 transition (jitter ~1ms),
  ≥198.5 never. Nominal edge = gap − spawn overhead (~1.4–2.5ms).
  Lo edge = floor (negative offsets splice — downward-unbounded).
- **Regimes**: miss = standalone ERROR + signature INTACT (verdict still
  FAIL — clause differs, verdict same); in-window = fused line +
  signature DESTROYED; rare straddle H-E-T-E2 (~0.1ms).
- **Receipt upgrades landed with measured limits**: divergent_clause
  exact 9-row map (verified from-spec, multi-clause seam_script→(blob,
  error_scan)); sha256 same-input gate on 24 records (digest chain
  reclass→arm closed). Both carry measured caveats, recorded in lesson.

## Adjudicator own reproduction

- Scribe + verifier independently reproduced the landed code's full
  battery (88/88 flagless, 89–90/90 flagged, 34/34 surface, 24/24
  discriminations) — the committed diff is triply-verified.
- The divergent_clause exact-map discrimination passes on committed
  state (verifier recomputed from spec, not the landed mirrors).

## Corrections absorbed this round

- Declared bound re-scoped: strict bound is on write-position
  (flush-to-flush), nominal offset is a latency-shifted proxy
  (~2–2.5ms); transition band ~1ms stochastic — the "strict [lo,hi)"
  wording falsified as written, corrected semantics landed.
- `exit` in the clause taxonomy is structurally dead — the dead
  conditional was proven unreachable and deleted (`e8d4fb7`); the
  taxonomy slot stays documented in the docstring.
- sha256 binds decoded text, not raw bytes — receipt semantics named
  accordingly.
- Scout's off_* series falsified by a scratch-tooling artifact
  (re.sub first-match) — two lanes hit it independently; method note
  in lesson.

## Bounds

Nominal-offset space on this host (edge ≈198.3–198.5ms, ~1ms
stochastic); write-position bound exact (gap 200.02–200.16ms measured);
receipt fields bind decoded text; TIMEOUT records nondeterministic;
Godot 4.7.2 headless, CPython POSIX pipes. Opt-in flags only.

## Verdict — **ADMIT**

- depth: **improved locally** — fabrication window bounded in both
  spaces; regime map (miss/in-window/straddle) + provenance crossover;
  clause-attribution mechanism measured with its limits named.
- coverage: **improved locally** — ladder meta + two receipt upgrades +
  24 discriminations; 9-row clause map exact.
- calibration: **unchanged** — opt-in only; flagless 88/88; classifiers
  byte-identical.

Work commit `f754546`; report-last commit follows (simplifier lands
there).
