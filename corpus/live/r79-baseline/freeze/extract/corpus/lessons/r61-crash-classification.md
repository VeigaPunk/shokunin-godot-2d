# R61 — spontaneous-crash exit-shape classification (Godot 4.7.2 headless)

## Decision and evidence

| Fixture arm | exit | own `ERROR:` marker | classification | requirement |
|---|---|---|---|---|
| `--spontaneous-crash` (`OS.crash("r60 spontaneous crash probe")`) | −6 (SIGILL→handler→SIGABRT on this build) | `ERROR: r60 spontaneous crash probe` + `handle_crash:` banner | **True** | `expected_exit=-6` AND scoped `expected_errors` exact-match allowlist |
| `--spontaneous-sigkill` (self `OS.kill(-9)`) | −9 (SIGKILL) | none | **True** | `expected_exit=-9` only — zero allowance |
| sigabrt output reclassified under expected −9 | — | — | **False** (meta discrimination) | expected-exit mismatch rejects |
| sigabrt output under expected −6 with EMPTY allowlist | — | — | **False** (meta) | marker not forgiven → reject |
| sigabrt output under expected −6 with WRONG allowlist | — | — | **False** (meta) | unrelated allowed strings reject |
| sigabrt output under marker-presence clause with marker ABSENT | — | — | **False** (meta, r61 correction) | `crash_meta_ok` requires marker in captured output |
| self_sigkill output under expected −6 + crash allowlist | — | — | **False** (meta) | cross-arm mismatch rejects |

Meta row `probe_spontaneous_crash_classification` re-classifies *captured* outputs only — zero additional Godot invocations; the four discriminations plus marker-presence are evaluated on the same-run receipts.

Named non-author `corpus/lessons/r61-crash-non-author.json`: 92/92 PASS, all 89 prior rows field-identical on the 7-field tuple vs `r59-audio-non-author.json`; ast-extracted `classify_process` forgery checks all reject. See `../../reports/round-61/r61-verifier.md` and `r61-adjudicator.md`. Critic's concrete forgeries (external `kill -4/-6/-11` → −6 True under empty allowlist; forged-marker admitted) bound the claim: this is **−6/+marker exit-shape** classification, never signal-origin detection — `returncode` cannot prove which signal or source produced the death.

Runner internals (`run_process`/`classify_process`/`classify_streams`) byte-unchanged at sha `42104d95…`→`3bb29044…` (additive hunks only). The CASES signature field demonstrably cannot carry the crash class — `unrelated_errors` rejection is orthogonal (measured by simplifier).

## Not established

Signal origin/provenance from `returncode`; `-6` determinism across hosts (SIGILL→SIGABRT observed ×5 here only); markerless-crash rejection at the CASES level (by design — a CASES row has no marker-requirement field; the meta row carries the class definition); any crash-dump/core-capture or process-tree semantics; other platforms.
