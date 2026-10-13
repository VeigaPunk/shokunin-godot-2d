# Round 43 baseline review — immutable r42 baseline

## Result

Reviewed the existing r42 verifier lesson and committed `HEAD` before any r43 tracked-fixture change. The immutable r42 named-verifier artifact is `.shokunin/game-dev-2d/corpus/lessons/r42-focus-restore-verifier.json`, SHA-256 `e483882c1f39963388a48791500cb78bf37c4216d5`. It records **67/67 PASS** = 56 ordinary cases + 2 mutants + 9 opt-in groups. The r42 report records 58 tuple-bearing case rows and nine opt-in classifications. This is the stated r43 before-state; r43 proposal is one additional expected-negative slider row (57 ordinary / 68 full), only if admitted.

Current committed source identity at baseline: branch `craft/game-dev-2d-r1`, `HEAD` `917feeb9306382663eafa2f05db9811c8ab0f7d0`. `slider_adjust.gd` SHA-256 `2fcc98b4c5363d121effdb0accaa63118a42fdb32f82ccd1d593581063f5ed21`; `run_battery.py` SHA-256 `948f6ca23abd8f2b8dd81424d7dd0d81061df18db75895fee39d40f56be6ed18`.

The r42 lesson is internally consistent with the baseline declaration: it contains 67 rows; all have outer verdict PASS, including seven slider rows before the proposed r43 case and the r42 positive `slider_adjust_repeat_right_focus_restore` (exit 0). It is a recorded replay, not evidence of the new r43 sequence. The working tree already contains historical uncommitted LOG changes and many untracked live scratch directories; I did not modify, clean, stage, or claim ownership of them.

## Scope

This is a baseline-only review, not a fresh full battery replay or an r43 independent paired review. No tracked fixture or runner files were changed. The r43 candidate must separately demonstrate the distinct expected-negative exit 2 after all seven assertions and preserve all prior tuple rows / opt-in classifications before any admission decision.
