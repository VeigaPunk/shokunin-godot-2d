# R66 adjudicator (Sol) — rejection-clause surface map

Round: 66. Wave: `shokunin-train-20261014-w6`. Work commit: `cb84d0a`
("r66: rejection-clause surface map — allowlist preemptor, evasion,
fabrication").

## Declared move (coverage)

Map the rejection clause's behavior over merged captured output:
allowlist-as-preemptor, `count("ERROR:")==1` conjunct, newline-split
evasion, seam fabrication — the critic/boundary edges measured in r65 but
never tracked.

## Seat convergence

| seat | landing | contribution |
|---|---|---|
| author | yes | +565/−1: 4 fixture arms (allowforge/splitforge/seamforge/midlineforge) + ~500-line `probe_error_clause_surface` meta; 88/88 PASS, surface meta 34/34 |
| scout | yes | claim confirmed by measurement; `classify_streams` stderr-only divergence re-confirmed as latent finding |
| critic | yes | literal-wording falsification reproduced: `SCRIPT ERROR:`/`Parse Error:` blob conjuncts preempt the allowlist and reject with zero `ERROR:` lines — corrected clause order adopted |
| boundary | yes | newline-split evasion measured across the full `splitlines` boundary set + `\x1f` non-split; allowlist admittance edges; reader-drain surfaces |
| simplifier | yes | minimal except `reparent_gate` extraction (6 byte-identical copies → warranted, applied at integration, argv-byte-identical proven); `export_preset_missing` dead-entry delete evaluated and **rejected** (coverage-unsafe) |
| reviewer | yes | committed-state audit clean; surface meta 34/34 verified |
| scribe | yes | verified the dead prior instance's full 123-run matrix (sha-convergent); lesson draft adopted; found a **third direction** — post-death `\xff` → `UnicodeDecodeError` denial-of-verdict; verbatim errata on own scratch line refs |
| baseline | yes | frozen replay green; **archive shrink confirmed by measurement: 614MiB vs 1.4G** (~56% — the `tree/` untrack worked) |
| verifier | pending at adjudication write | respawned after rate-limit kill |

## Adjudicator own reproduction (committed tree `cb84d0a`)

- `--spawn-seamforge` run directly: descendant leaves unterminated stdout
  tail `…ends in ERROR` + stderr head `: SEAMFORGE phantom…` → merged
  capture fabricates `…tail ends in ERROR: SEAMFORGE phantom fabricated
  line` — a reject-triggering line present in neither stream; exit 0,
  genuine signature present. Matches the claim.
- Full-battery replay running at write time; verifier lands the
  byte-level comparison.

## Corrections absorbed this round

- "Pure line-presence function" falsified — `SCRIPT ERROR:`/`Parse
  Error:` are whole-blob clauses that preempt the allowlist itself;
  allowlist preempts the line scan ONLY (critic falsification → adopted).
- `reparent_gate` extraction applied at integration (simplifier,
  byte-identical argv proven) — battery re-run 88/88, surface 34/34.
- Dead-entry census: `export_preset_missing` entry flagged as deletion
  *candidate* by simplifier — retained (coverage implications unsafe).
- Third direction beyond the declared claim: denial-of-verdict via
  post-death `\xff` (`UnicodeDecodeError` escapes the verdict path) —
  scribe-measured, recorded as known-adjacent.

## Per-axis verdict — **ADMIT**

- **coverage: improved locally** — the rejection clause's full surface is
  now mapped at receipt level: clause inventory (line-scan + 2 blob
  conjuncts), allowlist preemptor bound, evasion boundary set, fabrication
  seam geometry, dead-entry census (0/40 in-run dead; 6 static dead
  surfaces named).
- **depth: improved locally** — forgery works in all three directions
  (evasion, fabrication, denial-of-verdict); composite single-writer
  split+phantom measured; `classify_process`/`classify_streams`
  divergence documented.
- **calibration: unchanged** — additive meta probe; no verdict logic
  edited.

Bounds: Godot 4.7.2 headless on this host; `systemd --user` subreaper
pid 1573 environment; census "reachable" bounded to shipped fixtures;
denial-of-verdict is decode-bound (`text=True` policy).

Work commit `cb84d0a`; report-last commit lands verifier + lesson +
LOG/SCORECARD.
