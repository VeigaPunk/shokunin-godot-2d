# Round 29 named non-author focus verifier

## Verdict: PASS, bounded headless calibration claim; no discrepancy in final tracked run

Replayed the final tracked `button_activation.gd` and `run_battery.py` without editing either. The only tracked source changes versus HEAD are those two assigned fixture files (and LOG, which is outside fixture scope); I made no source edits. This report and two raw lesson JSON files are my artifacts. Full replay copied byte-for-byte from the produced raw output to `corpus/lessons/r29-focus-verifier.json`; fault replay likewise to `corpus/lessons/r29-fault-verifier.json`.

### Scope and full battery

Command:
`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r29-named-verifier/full`

Exit 0. Raw JSON says aggregate PASS, 53 records = 42 ordinary (including exactly one new `button_activation_unfocused`) + 2 mutants + 9 opt-ins. Compared against `corpus/lessons/r28-repeat-verifier.json`, all 52 prior case names have identical `(verdict, actual_exit, signature)`; no missing or changed prior case. New case: `button_activation_unfocused`, expected/actual exit 2, intended step1 `UI BUTTON ASSERTION FAILED...`, classified PASS. The probe-level adverse `FAIL`s (unrelated-error and stream-reject) are intentionally rejected controls enclosed by PASS probe classifications, not battery failures.

Raw JSON: `corpus/live/r29-named-verifier/full/20261013T043845183877Z/verdicts.json` SHA-256 593c2b25a16f1c40e1a49a04172da12639087bd24e3f742a8054dac0f179c9af. Lesson copy has the same SHA-256; bytes identical.

### Direct tracked fixture pair

Godot `4.7.2.stable.arch_linux.ed1daf0bf`:
- `godot --headless --path .shokunin/game-dev-2d/corpus/fixtures --script res://button_activation.gd`: exit 0. Before actions the fixture's focused precondition verifies target owner/has_focus. After each complete action it prints button-focused true; receipts `[1,2]`; labels `Activated 1`, `Activated 2`; final PASS.
- Same command with `-- --no-focus`, run twice independently: both exit 2 at the intended step1 assertion, not setup; owner/has_focus false, receipts0, label Ready. Exact stdout/stderr captures and exit files are in `corpus/live/r29-named-verifier/{focused,nofocus1,nofocus2}.{out,exit}`.

The tracked fixture connects its callback to `button.pressed`, dispatches `ui_accept` press/release through `root.push_input`, and has no manual `.emit()` invocation. Positive and negative arms share this route; the no-focus arm verifies null focus owner before action. This supports only focus dependence in this synthetic headless test.

### Preserved adverse baseline-child scratch claim

Reran the preserved baseline-child source at exact project path `.shokunin/game-dev-2d/corpus/live/r29-focus-test/project`, using the reported `godot --headless --path ... --script res://button_activation.gd -- --no-focus` command twice. Source SHA-256 29d963f6621d2eacca224a9d8793283956c51f32436002fb47861c59fdae271e. Both runs exited 2 at its intended step1 diagnostic with receipts0/Ready; no setup error. Output/exit artifacts: `corpus/live/r29-named-verifier/baseline-nofocus-{1,2}.{out,exit}`. Thus the earlier reported successful no-focus runs are **nonreproducible** on preserved source and exact path; I retain the adverse claim rather than erase it. Current tracked and named replay support the focus contrast.

### Separate fault-injection control

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection --runs .shokunin/game-dev-2d/corpus/live/r29-named-verifier/fault`; exit 0, outer mode PASS; raw `corpus/live/r29-named-verifier/fault/20261013T043845183786Z/fault-verdicts.json` SHA-256 68dbd098c882a2d09e688568201fbc335138d1553f5c8a909a6ff88e964d8620. This is separate from seeded battery. Inner `fault_hang` (timeout) and `fault_unrelated_error` are deliberate FAILs; `fault_clean_expected_negative` PASSes. Lesson copy has the same SHA-256; bytes identical.

### Integrity and limits

`button_activation.gd` and `run_battery.py` SHA-256 before and after replay unchanged: `d42ebb11bdc07a007d7a85eaf0399c594fc76ca8e0fdab0b4d145d36e82bae3` and `097058b23fb53f38dd8cbede34559d7ef6a2999c8568ea598d7a2c57d1b3ff38`. No edits to fixture/runner by verifier. No commits/push/merge.

**Limits:** evidence is headless Godot synthetic focus via `ui_accept` and `root.push_input`; not pointer activation, rendered UI, accessibility, or production scene behavior. No arbitrary mutation-proof claim.
