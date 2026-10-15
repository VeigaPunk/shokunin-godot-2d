# Round 50 regression scout — release after late-reconnected press

Read-only review of the r50 claim and r44–r49 reports/fixtures. I did not edit tracked fixture or runner files, prior reports, seeded fixtures, or engine/editor source; no commit, push, or merge. The unique scratch project is `corpus/live/r50-regression-scout-20261013/`.

## Bounded scratch evidence

Godot is `4.7.2.stable.arch_linux.ed1daf0bf`. I copied `project.godot` and the current `slider_adjust.gd` into scratch and added a candidate-only `--release-after-late-reconnect-press` branch, preserving the r49 ten events and adding edge10 (`ui_left`, pressed=false). Each iteration checks expected GUI focus owner and callback connection before dispatch, then numeric value, full cumulative receipt list, and callback-driven Label after one process frame. The callback is initially connected; it is disconnected after edge0 checks and reconnected after edge7 checks. It is checked connected before edges8–10. The unique expected-negative marker and exit 2 occur only after all eleven checks.

Command:

```text
timeout 15s godot --headless --path .shokunin/game-dev-2d/corpus/live/r50-regression-scout-20261013 --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --release-after-late-reconnect-press
```

Observed exit **2** after the expected terminal marker:

```text
SLIDER_RELEASE_AFTER_LATE_RECONNECT_PRESS values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Label=Value 3 connected=true
ERROR: SLIDER RELEASE-AFTER-LATE-RECONNECT-PRESS ASSERTION FAILED: expected no new receipt after eleven checks
```

The observed history supports the hypothesis: edge9 press changed value 4→3 and appended receipt 3; edge10 release left value 3, receipts `[6,3]`, and Label `Value 3`. The owner was HSlider before each edge except Button-owned edges1–2 and 5–6. The same scratch code checks signal connection state before every dispatch: connected on edge0 and edges8–10, disconnected on edges1–7, with disconnect/reconnect transitions verified after edge0/edge7 checks.

One initial scratch run was invalid: while adding the eleventh event I initially failed to extend the expected-value vector, so it stopped at an edge8 assertion. I corrected the scratch-only vector; the successful result above then reached all eleven checks and terminal marker. Retain the initial failure as scratch-development telemetry, not evidence against Godot's hypothesis.

This is direct candidate scratch evidence only. No tracked integration or full battery was run by this scout. HOLD if the authorized executor's tracked implementation or independent verification differs.

## Read-only regression and caveats

- r44 connected nine-edge baseline: `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, Label ends `Value 4`; owner-before and value/receipts/Label-after checks.
- r45 start-disconnected arm: same numeric history, receipts `[]`, Label `Value 5`, expected-negative after all nine checks.
- r46 disconnect-after-edge0: same numeric history, receipts `[6]`, Label `Value 6`; expected-negative after nine checks.
- r47 reconnect-after-edge3: same nine-edge values, receipts `[6]` then `[6,4]` at final adjustment, Label ends `Value 4`.
- r48 late reconnect after edge7: same nine-edge values, receipts `[6]`, Label `Value 6`; expected-negative after nine checks.
- r49 fresh press after that reconnect: ten-edge history ending 3, receipts `[6,3]`, Label `Value 3`; positive exit 0 after ten checks. Preserve these branches and rows byte-exact; r50 is an additional distinct expected-negative arm.
- Prior fault-verifier caveat: an outer/meta PASS can include intentional inner hang/timeout and unrelated-error FAILs; only the clean expected-negative inner case is a PASS. Do not describe all inner fault cases as passed. Timeout evidence is bounded to the tested direct-child cleanup, not general descendant/process-tree cleanup.
- Export evidence is separate. Prior reports note export-readiness does not imply generic export launch reliability; a relative export path previously failed (`Prepare Template: The given export path doesn't exist.`). No export behavior was tested here.

Scope is headless Godot 4.7.2, synthetic parsed `InputEventAction` events and process-frame yields. No claim about OS repeat, physical timing/input, rendered/pointer behavior, accessibility, production, generic HSlider/signal behavior, or internal consumption of unchanged events. No engine/editor/seeded edits.
