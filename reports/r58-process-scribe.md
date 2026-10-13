# Round 58 process-boundary evidence checklist — scribe

Role: checklist only. This report makes **no PASS or round verdict claim** and does not modify the fixture or runner.

## Claim under review

A writer Godot process exits after saving; a distinct reader Godot process reopens and structurally verifies that save. Both invocations must use the same copied project identity and the same run-local absolute `XDG_DATA_HOME`. A paired negative must reject an absent or wrong saved file. Preserve the prior 83 classifications. No durability, atomicity, arbitrary corruption detection, production persistence, or cross-platform inference.

## Existing baseline to protect

- The current fixture `corpus/fixtures/save_roundtrip.gd` writes and reads `user://r57-save.json` in the **same** Godot process. Its `--corrupt-negative` path tests a malformed copy in that process; neither establishes a process boundary.
- `corpus/fixtures/run_battery.py` registers `save_roundtrip` and `save_corrupt_negative`; the save case sets absolute run-local `XDG_DATA_HOME` at `run_dir/xdg-data` and uses a timestamp-suffixed copied project name.
- The Round 57 seven-flag non-author receipt and old 83 classifications are identified in `LOG.md`; compare exact old case/script/flags/expected-exit/evidence records, not just a total count. Round 58 additions must not silently relabel or replace them.

## Evidence required before any positive claim

- [ ] Writer and reader are separate child processes/invocations (record command, PID or equivalent process identity, exit status, stdout/stderr, and invocation order); writer has exited before reader starts.
- [ ] The writer alone creates the positive save. Reader source/flags do not write, repair, initialize, or substitute the target file before opening it.
- [ ] Both processes receive the same **absolute** run-local `XDG_DATA_HOME`; record it and show it lies below this run's scratch/run directory, not account-level user data. Both use the same copied project path and project identity.
- [ ] Reader opens the exact writer-produced `user://` path, checks parse success and expected structure/values, and emits a distinctive positive signature only after those assertions.
- [ ] Preserve raw per-process stdout/stderr, exit codes, commands/environment evidence, and the final runner verdict JSON in unique `corpus/live/r58-process-*/` scratch. Confirm no writes outside the assigned scratch/report.

## Causal negative evidence

- [ ] Use a separate controlled invocation/run for missing-file or wrong-value condition; establish that the target is absent/wrong before reader starts, and prove the reader rejects it with the specific expected assertion/diagnostic and expected nonzero exit.
- [ ] Show the negative is not a writer/setup failure, timeout, launch error, or unrelated Godot `ERROR:` line. Retain raw output and file-state evidence.
- [ ] Prefer missing-file or wrong-value as scoped by the declared claim; malformed JSON alone is not equivalent evidence that the independent reader rejects missing/wrong saved data.

## Regression and isolation gate

- [ ] A named non-author runs the declared seven flags in fresh unique scratch and produces raw evidence plus verdict JSON.
- [ ] Exactly 83 prior classifications remain present and unchanged (the prior 72 ordinary + 2 mutants + 9 opt-ins); account for the two new process cases separately, giving 85 total only if the runner registers two additional rows.
- [ ] Verify old 83 tuple-by-tuple against the prior receipt, including flag sets, expected code/signature and classification; report any mismatch as adverse, not a pass.
- [ ] Verify run-local absolute XDG path for both new process invocations and confirm prior cases' classifications did not shift due to shared state.
- [ ] Any sabotage/fault tests are separately labeled, scratch-only, and not substituted for the seeded battery or counted as ordinary coverage.

## Boundaries / reporting

A successful finite replay supports only the bounded headless Godot 4.7.2 two-process JSON roundtrip and the specific negative tested. It does not establish power-loss/flush durability, atomic saves, arbitrary tamper/corruption detection, production persistence, or platform guarantees. Keep depth and calibration classifications unchanged unless separate evidence justifies a change. Do not call this claim passed until all listed evidence is inspected; this scribe report is not that evidence.
