# R11 Godot error probe — adversarial review

## Verdict
**Narrowly supports the declared calibration claim.** The production `run_process` and `classify_process` path accepts one actual Godot `push_error` diagnostic as the expected negative, and rejects the paired invocation when a second actual `push_error` diagnostic is emitted. The paired runs have the same script, expected exit (0), and signature; this is not string editing of captured output.

## Independent replay
Ran `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-godot-error` at the current worktree. Exit 0; the existing 25 seeded cases all PASS, followed by probe meta PASS. Raw evidence is in `.shokunin/game-dev-2d/corpus/live/runs/20261012T174522175192Z/godot-error-verdicts.json`.

- Clean invocation: actual exit 0, `error: null`; real output contains `ERROR: EXPECTED_NEGATIVE: deliberate assertion rejected` exactly once, plus Godot's `push_error` callsite/backtrace. Shared classifier returns true.
- Fault invocation: same script and expected signature/exit, with `--unrelated-error`; raw output contains the same expected diagnostic and actual `ERROR: UNRELATED_FAULT: unrelated engine diagnostic` exactly once, plus its callsite/backtrace. Shared classifier returns false.
- `classify_process` checks actual exit equals expected, no process error, required signature present, and rejects every `ERROR:` line not exactly allowed; it also rejects `SCRIPT ERROR:` and `Parse Error:`. The allowance here is the exact expected `ERROR: EXPECTED_NEGATIVE: deliberate assertion rejected` line, not arbitrary engine errors. The added error is a separate real emitted line, not an edited output string.

## Adversarial limits / remaining qualification
- No false PASS path was found for an actual timeout, nonzero crash exit, or extra `ERROR:` in this classifier: timeout returns `code=None` and a non-null `error`; a crash/nonzero exit mismatches expected 0; an extra error line is unrelated and rejected. However, this R11 probe itself does not inject a crash or timeout; those conclusions are from the shared classifier's explicit conditions, with earlier R7 synthetic timeout evidence separate.
- The probe's PASS is an aggregate oracle over the two recorded raw outputs, diagnostics counts, same expected exit, and the inner classifications. It does not prove Godot's handling of every error category or capture route; `push_error` is the specific emission path exercised.
- These are two bounded headless script processes (8-second limit), not gameplay errors, export errors, or proof of stderr-only behavior: the runner concatenates captured stdout and stderr before classification.

No changes made to runner, fixtures, or engine/editor files. Only this review report is written.
