# Round 41 immutable r40 baseline review

Read-only review of committed r40 HEAD `0956c50bed04d306802ba5ce4f0107b7e09a7603` (`game-dev-2d r40: report seven-edge focus calibration`). Current working tree includes the in-progress round-41 LOG entry and live scratch; I made no fixture/runner changes and ran no engine or battery.

The immutable r40 named-verifier corpus is `corpus/lessons/r40-repeat-focus-verifier.json`, SHA-256 `0de4471c784e5e69d5e3a384436f5a734fb7548e4824fe948d4822ffb8d51167`. Its verifier report is `reports/r40-repeat-focus-verifier.md` (SHA-256 `1554166a61b5a6d23ea9f45f9396d8ef5f1253a8947e468874e18e02c33ce96e`). It records PASS: 65 results (54 ordinary, 2 mutants, 9 opt-in groups), including focused seven-edge repeat-right and seven-edge no-focus controls. The no-focus arm holds value 5/receipts[]/Label Value5 and terminally exits 2 after its seven checks; its report scopes that evidence to synthetic parsed actions plus process frames.

Compared r39 `corpus/lessons/r39-repeat-verifier.json` (64 results) to r40 by `(case, verdict, actual_exit, signature)`: all 55 prior tuple-bearing rows are unchanged, and the sole added tuple row is `slider_adjust_repeat_right_no_focus` (PASS, exit 2). Nine opt-in group records retain their respective stable classifications; their run-specific artifacts are not tuple rows and should not be described as byte-identical. The proposed round-41 target is one further ordinary row, so a successful comparison should preserve all 56 r40 tuple rows and separately classify the nine opt-ins.

Committed r40 fixture/runner are the baseline; this review did not alter tracked files. No engine/editor or seeded fixture use, commit, push, or merge.
