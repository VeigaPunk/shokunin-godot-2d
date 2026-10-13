# Round 52 independent route scratch review — HOLD

- Role: read-only tracked-file review and independent headless scratch; no delegation or tracked fixture/runner edits. Runtime: Godot `4.7.2.stable.arch_linux.ed1daf0bf`.
- Read standing mission, round 52 declaration, round 51 LOG claim/adjudication, `reports/r51-provenance-verifier.md`, and `corpus/lessons/r51-hslider-parsed-release-observer.md`. Round 51 establishes a parsed release receipt plus global state transition; it does not establish that `SceneTree.root.push_input()` drives global action state.

## Paired scratch contrast

Copied the fixture tree to separate scratch projects under `corpus/live/r52-route-reviewer-{scratch,parsed}-scratch`. The parsed control ran the unchanged fixture with `--repeat-right --second-focus-restore --observe-parsed-release`. In the alternate scratch only, the edge10 call was replaced by constructing the same `InputEventAction` (same action and pressed fields) and calling `root.push_input(event)`; edges 0–9 and the eleven-edge sequence stayed as-is. This was one frame per edge, with existing focus-owner and callback-connected checks before each edge and numeric/full receipt/Label assertions after each frame. The edge10 branch also printed observer/state/full receipts/Label/owner/callback evidence.

Parsed control output:
```
SLIDER_PARSED_RELEASE_OBSERVER values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true
ERROR: SLIDER PARSED RELEASE OBSERVER ASSERTION FAILED: expected no new receipt after eleven checks
```
It reached the expected-negative terminal after all eleven checks. The branch's existing observer and pressed-state assertions imply edge10 observer 3→4 and pressed true→false; final numeric3, receipts `[6.0,3.0]`, `Value 3`, focus owner/callback true.

`root.push_input` alternate output:
```
R52_PUSH_INPUT edge10 observer=3->4 pressed=true value=3.0 receipts=[6.0, 3.0] label=Value 3 owner=true callback=true
ERROR: SLIDER input-state post-release assertion failed: ui_left remains pressed
```
Thus this route **does dispatch** the matching release to the in-tree observer (3→4), and preserves numeric3, full receipts `[6.0,3.0]`, Label `Value 3`, owner true, callback true, but **does not clear** `Input.is_action_pressed("ui_left")` (remains true). The script halts at the existing post-state guard, before its observer-specific guard and terminal marker. That is direct adverse evidence for the proposed combined terminal condition, not an observed clean expected-negative case. It validates the narrow separation in the hypothesis, but the current fixture cannot classify it as a distinct exact negative without additive fixture/runner work; per assignment, HOLD and do not edit tracked files absent proof of a bounded distinction that can be safely encoded.

Scratch commands were `godot --headless --path <scratch> --script slider_adjust.gd -- --repeat-right --second-focus-restore --observe-parsed-release`; same command for the paired parsed control. Scratch source and complete stdout are retained at the two paths named above. No engine/editor/seeded edits, constants, tracked edits, commits, push, or merge.

Conclusion: measured behavior supports only this synthetic Godot 4.7.2 route contrast. `root.push_input()` delivers to this observer without clearing the global action state in this setup. **HOLD**: no case/allowlist/battery change. No inference about HSlider internal consumption, OS/physical input/timing, rendering, pointer/accessibility, or production behavior.
