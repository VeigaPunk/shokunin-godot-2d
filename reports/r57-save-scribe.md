# Round 57 save/load scribe — evidence checklist and adverse telemetry

Scope: scribe/evidence checklist only. This is **not** a PASS attestation, independent execution, or verdict. No fixture, runner, engine, editor, or domain-source files were edited. Unique scratch assigned: `.shokunin/game-dev-2d/corpus/live/r57-save-scribe/` (created; no test artifacts produced).

## Inspection commands and results

All commands were run from repository root `/home/vgpnk/Projects/prymeagnt/game-dev-2d`.

- `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`). This records the available binary version, not a test run.
- Python read-only inspection of `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py`: `CASES` contains 70 entries; case-name/fixture search for `save` or `load` found no save/load case (the incidental matches were unrelated scene loading, export probe/savepack strings, and verifier code). The existing `CASES` list currently ends with `slider_adjust_repeat_right_second_focus_restore_disconnect_after_first`.
- `Path('.shokunin/game-dev-2d/corpus/fixtures').iterdir()` filtered for filenames containing `save` or `load` → `[]`.
- `git diff --stat -- .shokunin/game-dev-2d/corpus/fixtures/run_battery.py .shokunin/game-dev-2d/corpus/fixtures/slider_adjust.gd` and scoped `git status --short` → empty output at inspection time. This establishes no observed tracked changes to these two paths at that time, not their status after other workers act.
- Read-only runner inspection: runner copies fixture files into per-run scratch, launches Godot with `--headless --path <scratch> --script res://...`, and classifies by expected exit/signature/error filtering. The runner's existing default case count is 70; no baseline rerun was performed by this scribe.

## Evidence checklist for executor / non-author verifier

- [ ] Preserve all 70 pre-existing `CASES` entries and expected command arguments, exit codes, signatures, and order byte-for-byte; append only new cases. Document exact before/after ordinary and full counts. Prior-round baseline recorded in the declared log is 70 ordinary / 81 full; it is not a result for this round.
- [ ] Positive case must actually write a JSON document to an isolated `user://` location in the copied project/run scratch, close/reopen it through the intended file API, parse it as structured JSON, and compare meaningful nested values/types to the source input. A printed marker alone, parse success alone, or reading the in-memory source object is insufficient evidence of round-trip/reopen.
- [ ] Record the exact scratch location and evidence that save and reopen use the same intended isolated user-data location. Confirm no source fixture or shared user data was modified. Avoid claiming durability outside this headless scratch process.
- [ ] Negative control must begin from a copied scratch JSON artifact, change its bytes after positive creation (record distinct original/corrupted hashes or exact bytes), attempt the real load/parse path, reject it, and emit a distinct expected-negative signature with the expected nonzero exit. Ensure corrupted bytes are genuinely invalid for the parser/contract rather than merely valid JSON with altered but accepted values.
- [ ] Verify negative acceptance is not a false success: corrupted-copy path must not report loaded values/positive completion; classifier must distinguish its negative signature from the positive signature and reject unrelated errors, parse/compile failures, timeout, or missing artifact as evidence of correct rejection.
- [ ] Run isolated smoke first, then have the named non-author perform the declared full seven-flag replay and controlled corruption sabotage. Capture exact command lines, binary version, exit codes, signatures, output, and artifact paths. Do not infer verification from executor output alone.
- [ ] Compare all old classifications and counts against baseline; report any missing/changed rows, new warnings/errors, timeout, or cleanup anomaly as adverse telemetry. Confirm old case definitions remain identical, not merely that the total grew.
- [ ] Evaluate the bounded claim only: this harness exercises a JSON file round-trip and a corrupted-copy rejection under the tested Godot/headless environment. It cannot establish crash/power-loss durability, atomicity, security, migrations, cross-platform behavior, user-profile behavior, or production save-system correctness.

## Adverse telemetry / unresolved

- No positive or negative save/load fixture exists in the inspected fixture directory at this scribe's inspection point, so there is no causal evidence yet for either behavior.
- No smoke, ordinary battery, full replay, or corruption sabotage was run by this scribe. Post-change counts/classifications and non-author independence remain unknown. Do not mark any checklist item complete from this report.
- `run_battery.py` has separate existing export/fault/probe behavior; its internal uses of words such as `savepack` are not a save/load test. Avoid counting those as evidence.
- The repository has many pre-existing untracked artifacts; do not clean them or write outside this lane's report/scratch. The working tree also showed an unrelated modified `.shokunin/game-dev-2d/LOG.md` during initial status inspection; this lane did not edit it.

References: `.shokunin/game-dev-2d/LOG.md` Round 57 declaration; `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py`; `.shokunin/game-dev-2d/corpus/fixtures/`.
