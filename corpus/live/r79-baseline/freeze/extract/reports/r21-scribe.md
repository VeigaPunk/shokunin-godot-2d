# Round 21 scribe — raw-artifact, axis closure, report-last checklist

Scope: scribe only. This report is a checklist, not execution or admission evidence. No engine/editor or seeded-corpus changes made. The round-21 claim in `LOG.md` is a paired real-Godot probe: expected nonzero exit versus externally signaled termination, same short-lived script and emitted success signature. The current checkout has no `r21-*` reports/raw verifier artifact yet; do not infer a result from the declared claim.

## Raw artifact checklist

- [ ] Preserve the complete named verifier invocation, executable/version (`godot --version`), OS/platform, Python version, working directory, and relevant signal mechanism/number.
- [ ] Preserve unedited stdout and stderr separately for both arms, exact argv, expected and actual process return code, timeout/error fields, elapsed time, and the resulting JSON. Do not reduce evidence to a printed PASS line.
- [ ] Establish the reject process had actually started and was still running before signaling (record the handshake/marker and timing/observation); record the external signal sent and exact observed termination status. A copied signature alone is not evidence of signal termination.
- [ ] Demonstrate both arms invoke the same script and emit the same exact claimed signature; the accept arm ends normally at the declared expected nonzero status, while the reject arm is terminated externally and is rejected by classification. Record any other stdout/stderr differences; do not conflate shell status with Python `Popen.returncode` signal encoding.
- [ ] Show bounded wait/cleanup and no leaked process. State platform-specific signal semantics as observed; avoid generalizing across platforms.
- [ ] Store verifier raw replay under the assigned `corpus/lessons/r21-crash-verifier.json` and cite it from `reports/r21-crash-verifier.md`. Keep scratch/output under `corpus/live/`; no changes to seeded controls.
- [ ] Retain baseline and post-change fixture/runner hash comparison and complete ordinary + mutant + existing opt-in results. Preserve failures and diagnostics verbatim; do not retry a failed arm into a pass.

## Per-axis closure

- **Calibration (target):** improved only if an independent non-author verifier reproduces the paired causal contrast from raw artifacts: normal expected nonzero exit with signature classifies true; actual externally signaled termination with the same signature classifies false; process-running proof, signal status, bounded lifetime and cleanup all hold. If no safe reproducible contrast or status distinction exists, HOLD / unprovable-but-better only if a real evidence-backed limitation was learned; no invented improvement.
- **Coverage:** unchanged unless the round adds a distinct product behavior surface; this is a process-classification probe, not a product feature. Do not claim crash-proofing or broader platform coverage.
- **Depth:** unchanged unless evidence shows a new mechanic/probe class beyond the declared process exit classification. No scalar scores.
- **Harm/regression gate:** all prior ordinary outcomes, mutants, and existing opt-in probes must remain PASS in the same verified replay; any regression is harmed and blocks admission. Mention the prior relative-`--runs` export `StopIteration` as unresolved adverse telemetry, not as round-21 evidence or something this calibration probe repairs.
- Admit only with at least one improved axis and zero harmed axes. Otherwise record HOLD/no admission and why. Report exactly what the finite run proves; no production crash, process-tree timeout, or cross-platform guarantee.

## Report-last / closeout checklist

- [ ] Wave-one deviations/failures and non-author verifier identity/independence are reported accurately; no leaf delegation.
- [ ] Link every claim to raw JSON and leaf report paths; distinguish author feasibility checks from verifier evidence.
- [ ] State constants changed (or “none”), files changed, exact platform signal semantics, scope limits, and unresolved adverse observations.
- [ ] Ensure the round report is the final written artifact before any permitted commit; preserve append-only `LOG.md`; do not commit/push/merge from this scribe lane. Parent owns integration and final disposition.
