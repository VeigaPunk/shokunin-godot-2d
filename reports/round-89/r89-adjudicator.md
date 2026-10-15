# r89 adjudication — geometry/edges lattice

**Verdict: ADMIT-corr** — authored `8cea888`, folded `53a0be7`, verified on folded bytes.

## Dossier

| seat | verdict | commit |
|---|---|---|
| author | 20 rows (215→235), 235/235 ×2 | `8cea888` |
| boundary | 7 SIGABRT + 1 NaN-hang vectors; `input89_edges_exact` load-bimodal → envelope | `5be63e9` |
| critic | PASS-WR — F1 lineempty crash-cause-blind (folded) | `68756af` |
| reviewer | PASS — envelope load-bearing (each mode the other's only-correct-answer) | `61355e2` |
| simplifier | PASS — `names` accumulator −2 proven (folded) | `f535ddb` |
| verifier | VERIFIED-WR — 60/60 under load ×3, 1750 envelope reps all in-tuple | `23947df` |
| scribe | custody HOLDS — arithmetic reconciles | (report) |
| fold | SP1+F5 −51 lines, `required_stderr` pin, gitignore hygiene; 247/247 run2 | `53a0be7` |
| verifier-r2 | VERIFIED — 247/247 ×2, forge discrimination PASS | `1a23de5` |

## Laws admitted

Geometry lattice (20 rows): atlas/ring/contour/poly-join/ops cells, the `input89_edges_exact` load-bimodal envelope (payload[0]=quiet / payload[1]=loaded — proven load-bearing both directions), typed SIGABRT rows pinned to `Clipper2Lib::Point<double>` assert via `required_stderr`.

## Folds applied and verified

- Critic F1 crash-cause-blindness → `required_stderr` pin + `run_process_streams` (forges flip FAIL live).
- Simplifier SP1 `names` −2 + critic F5 dead arms `bridge_hole{,2}` + falsified comment → −51 net, byte-identical outputs.
- Reviewer custody items: `runs*/`, `__pycache__/`, `.godot/` gitignore hygiene; manifest self-entry dropped.

## Bounds

Godot 4.7.2 headless 60-tps, load 51–153 across seats. Envelope Q mode rare under saturation (~0.2%) but byte-exact when observed (4 receipts). `lineempty` pin toolchain-pinned — intended loud-fail on Clipper2 bump.
