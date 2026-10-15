# Round 32 named non-author CheckBox verifier

## Scope and source integrity

I independently verified the assigned new `corpus/fixtures/checkbox_toggle.gd` and its two `run_battery.py` rows; I did not edit tracked source or runner code. The fixture creates an initially unchecked in-tree CheckBox and a `Ready` Label, connects `toggled(bool)` only in the connected arm, and delivers two focused `ui_accept` press/release pairs. I found no assignment or manual mutation of `checkbox.button_pressed`, no `set_pressed*`, and no `toggled.emit()`; state changes are driven by the input pairs. Source SHA-256 before and after replay was unchanged: fixture `a6971f7e1089177e3e7ed8923e95aa8dd1021bf0ac8c1a4856a257d3665f79bb`; runner `f03ba367c7311c83e4621f835b5a41135a6f96b0ee7023d76b317c828d0d0250`.

## Independent direct Godot results

Godot `4.7.2.stable.arch_linux.ed1daf0bf`, headless scratch project at the full-run scratch directory.

- Connected direct run exited 0. Output showed `state=true receipts=[true] label=On`, then `state=false receipts=[true, false] label=Off`, then the exact fixture PASS marker.
- Disconnected direct run (`-- --disconnect-signal`) exited 2 at the intended final missing-signal assertion, after both actions: `CHECKBOX_DISCONNECTED state=true receipts=[] label=Ready` and `CHECKBOX_DISCONNECTED state=false receipts=[] label=Ready`, then `CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got []`.

This independently verifies both toggles in the disconnected control, the connected boolean receipt order, and callback-driven Label updates. The positive fixture sends press/release pairs in its loop with frames after each edge; it checks completed action state and signal effects (not separate press-edge state). No manual checkbox state or signal fabrication is present.

## Full default-path replay and baseline comparison

Exact command:
```sh
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```
Exit 0; raw receipt copied byte-for-byte to `corpus/lessons/r32-checkbox-verifier.json` (SHA-256 `7f12c3a1f69adab2098d92dd23825f3905239d7953206fbdc2cd4f49378cd245`, equal to run raw). Result: 56/56 aggregate PASS, 45 ordinary +2 mutants +9 opt-in/probe records (matching the stated 45 ordinary /56 full count; battery has 56 result records). Compared result cases with actual exit/signature against `corpus/lessons/r31-focus-loss-verifier.json`: all 54 predecessor rows matched exactly in `(case, verdict, actual_exit, signature)`. Two rows were added:

- `checkbox_toggle`: PASS, exit 0, signature `PASS checkbox_toggle states=[true,false] toggled=[true,false] labels=[On,Off]`.
- `checkbox_toggle_disconnected`: PASS as an expected-negative battery case, actual exit 2, signature `ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got []`.

That intentional inner exit 2 is classified as a passing battery case, not a setup failure. The disconnected row's own output records both true and false CheckBox states and Ready/no receipts before the designated final assertion.

## Separate fault-injection replay

Exact command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection`, outer exit 0. Its distinct raw receipt was copied byte-for-byte to `corpus/lessons/r32-fault-verifier.json`. It reports `FAIL fault_hang` (timeout after 0.25s), `PASS fault_clean_expected_negative` (the intentional exit-2 diagnostic), and `FAIL fault_unrelated_error` (unrelated error rejected), followed by `PASS fault injection`. These inner FAIL classifications are deliberate fault probes; they are not the seeded battery result or an outer harness failure.

## Scratch sabotage and boundary

In isolated scratch only, I removed the signal connection while retaining the positive arm's normal assertions and both-action loop. This arm necessarily checks signal receipt after action one; it exited 2 at `CHECKBOX SIGNAL ASSERTION FAILED: expected toggled=true receipts=[] label=Ready`, before action two. Thus this sabotage proves an absent signal is detected at the intended assertion but does **not** itself prove two state changes. The tracked disconnected paired control/direct run above is the evidence that the same two actions still toggle state twice when the signal is disconnected. Scratch: `corpus/live/r32-checkbox-verifier-sabotage/`.

The scout's earlier failed scratch is also recorded in `reports/r32-checkbox-scout.md`: an initial typed-array scratch-script error left a Godot process alive until parent termination; it was not treated as evidence. Corrected scout probe and this verifier's bounded direct runs completed. No inference beyond bounded headless synthetic `ui_accept` behavior; no pointer, rendered UI, accessibility, real-user timing, or production claim.

## Verdict

**Coverage improved**: this independently replayed pair establishes a CheckBox's two state transitions and observed `toggled(bool)`→Label behavior, distinct from Button `pressed` receipts. **Depth unchanged. Calibration unchanged.** No harm observed in these finite comparisons. Counts advance from 43 ordinary/54 full to 45 ordinary/56 full. No constants changed. I wrote only this report, the two assigned raw JSON copies, and isolated scratch; no source edit, commit, push, or merge.
