# Round 7 fault-injection scout (read-only)

## Finding
`corpus/fixtures/run_battery.py` already has bounded per-case `subprocess.run` calls (8 seconds for scripts, 60 seconds for exports), but the present runner has no fault-injection replay. Its normal-case pass check is only expected exit + expected signature; unlike export checks, it does not reject `ERROR:` output. Thus a negative control can pass with its expected signature and an unrelated engine `ERROR:` in the same output. A real 8-second hang test would be needlessly slow.

## Minimal deterministic proposal
Add opt-in `--fault-injection` (or a tiny separate test harness importing a factored command/classification helper). Keep this isolated from `CASES` and the fixture-copy/mutation path; do not edit seeds. Exercise the exact production subprocess timeout and pass-classification helpers, not a duplicate test-only classifier. Emit a separate fault summary and make CLI exit nonzero if either detector assertion fails.

1. **Timeout fault:** run `[sys.executable, "-c", "import time; time.sleep(2)"]` with a test timeout of `0.15` seconds. Require the helper to return timeout classification (`error` begins `TIMEOUT after`, `actual_exit is None`), then require the injected case's verdict to be `FAIL` (not a battery PASS). `subprocess.run(timeout=...)` kills/waits for the child. This is deterministic, bounded, and does not depend on Godot scheduling.
2. **Unrelated ERROR fault:** synthetic completed subprocess prints both the exact expected negative signature (e.g. `No export preset 'Missing preset' found`) and `ERROR: injected unrelated engine error`, exits with the negative case's expected nonzero code. Require ordinary negative-case classification to reject it. Add a shared output rule: reject any `ERROR:` line not explicitly allowed by that case's expected signature; test that the injected unrelated line is rejected even while the expected signature is present. Do not blanket-reject expected negative diagnostics or alter their expected signatures.

Use a temporary directory if artifacts are required; otherwise stdout-only subprocesses need no scratch files. In fault mode, report proof assertions as `PASS` only when the inner injected cases were correctly classified as `FAIL`; distinguish this meta-test result from ordinary fixture verdicts so it cannot make a fault look like a passing game fixture. Keep the regular battery invocation unchanged.

## Exact assertions / runtime
- Timeout subprocess elapsed < 1.5 s; timeout classification present; injected-case verdict is `FAIL`.
- ERROR subprocess exit matches expected negative exit and contains both signatures; unrelated-ERROR predicate is true; injected-case verdict is `FAIL`.
- Fault-mode overall status is success only when both assertions hold; otherwise nonzero. Record timeout, exit, diagnostics, and detector outcomes in JSON.
- Expected finite runtime: about 0.15 s plus process startup (comfortably < 2 s); ERROR check is immediate. No Godot invocation or seed modification is needed.

I did not modify the runner, fixtures, or engine/editor files. This is a design recommendation only; actual detector implementation and independent replay remain necessary to establish Round 7 calibration improvement.
