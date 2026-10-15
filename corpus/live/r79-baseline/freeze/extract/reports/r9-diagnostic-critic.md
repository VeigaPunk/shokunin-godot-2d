# Round 9 diagnostic-spoofing adversarial critique

Read-only review of the working-tree `corpus/fixtures/run_battery.py` and the Round 9 claim/runner changes in `LOG.md`. I made no runner, fixture, engine/editor, Git, or other project changes. I did not execute the battery; this is source-level falsification, not a replay.

## What the classifier currently establishes

`classify_process` is the shared production verdict function for ordinary fixtures, export, and mutant detection. It requires the expected exit, no timeout/launch error, a signature substring, no unallowed output line containing `ERROR:`, and no `SCRIPT ERROR:` / `Parse Error:`. Exact allowed error lines (including the expected invalid-preset line) pass; an added second `ERROR:` on that same line fails because it is no longer an exact allowed line. The comma-prefix allowances are less strict: they accept any suffix on the matching line so long as it has exactly one `ERROR:`. The chain-incomplete exception also makes structural checks on its allowed line.

The new flag injects a trailing unrelated `ERROR:` into captured real export output and, for missing-preset export, also forms a same-line spoof; it reclassifies those outputs with the production function. Mutant injection is limited to the `--probe-failing` mutants. These are useful unit-style checks of classifier reuse, not simulations of a process that emitted the forged output.

## Adversarial findings / qualification

1. **Same-line test coverage is asymmetric.** The missing-preset branch's `spoof_output` appends an unrelated `ERROR:` to the expected diagnostic line, and should be rejected by exact matching. Positive export has no same-line injection, and neither mutant branch tests a forged same-line `ERROR:`. A regression or alternate branch-specific allowance there can therefore go untested. Add same-line probes to positive-export and each mutant result, and test both `expected diagnostic + ERROR: unrelated` and `ERROR: unrelated + expected diagnostic` forms; the current exact whitelist should reject both.

2. **Probe outputs are synthetic string edits, not captured Godot diagnostics.** They demonstrate classifier behavior given a modified string but not that the process wrapper captures stderr/stdout completely, preserves line boundaries, or that real Godot's expected error is stable. The raw output needs to show the actual 4.7.2 invalid-preset diagnostic (and exit code) before asserting only that line is allowed. Avoid describing this as an end-to-end engine fault injection.

3. **Missing-preset exit contract is fail-open.** The branch calls `classify_process(code, ..., expected_exit=code, ...)` after checking merely `code is not None and code != 0`. That makes any nonzero exit self-validating rather than asserting the observed expected Godot exit (likely 1; establish from actual output). A different failure exit with the expected text can pass. Use a declared/replayed expected exit and retain the no-artifact check.

4. **Positive export signature is weaker than the work it claims.** Its current `classify_export` signature is only `Godot Engine v4.`; that is a generic startup banner, not evidence export reached the export phase. Nonempty artifact guards some failure modes, but prefer requiring the observed export-specific marker (`Exporting PCK/ ZIP...`) along with nonempty artifact and shared error classification. This matters especially when appending an ERROR to otherwise-valid output: ensure the control is a genuine successful export, not just a banner plus artifact residue.

5. **The mutation test is not fully branch-faithful.** Mutant probe records compute injected verdict as `detected and classify_process(...)`, while clean verdict is the composite `detected` (including the `PASS ` exclusion and case-specific mutation assertions). It likely rejects the current appended diagnostic, but it does not rerun the complete decision expression against injected output. Factor a verdict helper over candidate output and use it for both clean and injected output; test the same-line spoofs there too. This would prove no branch bypasses classification rather than merely prove a standalone helper rejects a string.

6. **Scope of “all diagnostics” is narrow.** The classifier rejects `ERROR:` text and script/parse errors, not every possible Godot warning or other severity. State the claim as unexpected `ERROR:` rejection, not general diagnostic cleanliness. The allowed comma-prefix logic is also deliberately broader than exact matching; each such prefix should have a concrete real expected line and bounded field validation, or use exact forms.

## Assessment

The shared classifier and the exact-line behavior are directionally sound; an appended second `ERROR:` should not be blessed as the expected negative. The current source supports only a bounded, synthetic-output calibration result, with clear remaining gaps in same-line mutant/positive-export coverage, missing-preset exit validation, and branch-faithful injection. Do not claim universal Godot diagnostic spoof resistance or production/export robustness from this probe alone.
