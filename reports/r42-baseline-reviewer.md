# Round 42 baseline review — immutable r41 baseline

## Result

Reviewed committed `HEAD` on `craft/game-dev-2d-r1` before any r42 fixture or runner change. The immutable r41 named-verifier lesson is `.shokunin/game-dev-2d/corpus/lessons/r41-focus-handoff-verifier.json`, SHA-256 `e4e3e6ffd2e78ece273c0b69a27d0fee6e52ab85294cb149afdd41b68a09045a`. It records **66/66 PASS** = 55 ordinary + 2 mutants + 9 opt-in groups. The 57 ordinary/mutant `(case, verdict, actual_exit, signature)` rows include the r41 handoff expected-negative row; the nine opt-ins are separately recorded. This is the r42 before-state.

The r40 lesson has 56 such tuple rows. Filtering the r41 result by tuple-bearing rows other than the new r41 `slider_adjust_repeat_right_focus_handoff` yields exactly those 56 r40 tuples, in order and byte-valued fields unchanged. The r41 row is PASS / exit 2 / `SLIDER REPEAT FOCUS-HANDOFF ASSERTION FAILED: expected post-handoff adjustment after seven checks`. This confirms the stated increment from 56 to 57 tuple rows without conflating opt-ins.

Committed source hashes: `slider_adjust.gd` `fe26f65b9cdb0e3edb0b102d49a46d676cccff82381b80a336ec066493469b5f`; `run_battery.py` `0a503c09c2d18a482d1ba195b776cc40adb1a5750e085da2d5ada8db5552a8a5`. No changes were made by this baseline review. Local uncommitted state already contained unrelated historical working changes/untracked artifacts; I did not edit, clean, stage, or claim ownership of those.

## Scope

This verifies the recorded r41 baseline artifact and committed source identity only. It is not a fresh full battery replay and does not establish r42 behavior; candidate scratch and named non-author verification remain separate.
