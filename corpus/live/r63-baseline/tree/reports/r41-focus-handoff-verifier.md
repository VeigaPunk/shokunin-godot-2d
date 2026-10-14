# Round 41 named non-author verifier — focus handoff

## Verdict: PASS; bounded calibration evidence reproduced

I was the named non-author verifier. Direct scratch runs by the scout and independent reviewer used Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Each created an in-tree HSlider (0..10, step 1, initial 5), connected `value_changed` receipt/Label, and separate in-tree focusable Button. The focused first fresh parsed `ui_right` press plus frame changed 5→6, receipts `[]`→`[6]`, Label to `Value 6`. Before the second right press, Button took focus; each of the six remaining original edges plus frame kept Button as owner, slider unfocused, value 6, receipts `[6]`, Label `Value 6`. Both report exit 2 only after the seven assertions. These are synthetic parsed events plus frames, not physical input or OS auto-repeat.

## Full battery and r40 comparison

Ran the requested full default-path command with my explicit runs directory:

`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r41-focus-handoff-verifier/runs`

Exit 0; **66/66 PASS** = 55 ordinary + 2 mutants + 9 opt-in groups. The 56 prior `(case, verdict, actual_exit, signature)` tuples from `r40-repeat-focus-verifier.json` are unchanged. Exactly one new tuple: `slider_adjust_repeat_right_focus_handoff`, PASS exit 2, signature `SLIDER REPEAT FOCUS-HANDOFF ASSERTION FAILED: expected post-handoff adjustment after seven checks`. All nine opt-in groups retain outer PASS and stable classifications/inner results; paths are run-specific. In particular unrelated-error and stream-reject inner checks are expected FAIL classifications, not lost telemetry. Timeout and typed-array/runtime failure observations from earlier scratch attempts also remain adverse telemetry in the executor report; they are not candidate PASS evidence.

Raw full run: `corpus/live/r41-focus-handoff-verifier/runs/20261013T065830983556Z/verdicts.json`, copied byte-identically to `corpus/lessons/r41-focus-handoff-verifier.json` (SHA-256 `e4e3e6ffd2e78ece273c0b69a27d0fee6e52ab85294cb149afdd41b68a09045a`). Separate `--fault-injection` outer PASS: deliberate inner hang FAIL (`TIMEOUT after 0.25 seconds`), unrelated-error FAIL, clean expected-negative PASS exit 2. Raw `corpus/live/r41-focus-handoff-verifier/runs/20261013T065940256882Z/fault-verdicts.json`, copied byte-identically to `corpus/lessons/r41-fault-verifier.json` (SHA-256 `cd49178d1f70d6a05dc89abffb6d9f756f22cb258b9f1854133597e4592849de`).

## Sabotage and integrity

In my own scratch, omitted the `other.grab_focus()` transfer; it failed at the pre-edge-1 owner assertion (`SLIDER focus-handoff owner assertion failed before edge 1`), not the terminal expected-negative. Separately omitted edge-0 dispatch; it failed immediately at the edge-0 value/receipt/Label assertion, not the terminal negative. The tracked `slider_adjust.gd` and `run_battery.py` hashes before and after verifier execution were unchanged: `fe26f65b9cdb0e3edb0b102d49a46d676cccff82381b80a336ec066493469b5f` and `0a503c09c2d18a482d1ba195b776cc40adb1a5750e085da2d5ada8db5552a8a5`. No tracked edits, commit, push, or merge by verifier.

## Axis verdict and scope

**Calibration improved**: a same-wiring, independently reproduced focus-handoff contrast isolates the effect after an observed focused adjustment. **Depth unchanged; coverage unchanged as axes; none harmed** in the finite replay. Constants: ordinary 54→55, full 65→66, one new expected exit-2 row. Scope is parsed synthetic actions plus process frames in headless Godot 4.7.2. Does not prove OS auto-repeat, physical keyboard/timing, rendered/pointer UI, accessibility, production, or generic slider behavior. Invariance after handoff does not independently prove each later action was consumed; the loop and per-edge checks are present, and omission of the first action is caught. No engine/editor/seeded-control mutation, publication, commit, push, or merge.
