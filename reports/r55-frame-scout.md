# R55 frame scout — two-frame clear then push

## Result

Independent scratch in Godot `4.7.2.stable.arch_linux.ed1daf0bf` supports the bounded claim: separating the reverse r54 calls by one `process_frame` preserved the requested final measurements after the pushed release's frame. At edge10, `Input.action_release("ui_left")` followed by `await process_frame` left observer count at 3 (3→3), cleared global `ui_left`, and kept slider value 3, receipts `[6,3]`, Label `Value 3`, focus owner on slider, and callback connected. Then `root.push_input(matching InputEventAction(ui_left,false))` followed by another `await process_frame` advanced observer 3→4; final value/receipts/Label and focus/callback remained as expected, and action remained released. All eleven edge checks reached the existing exact-negative terminal (exit 2), rather than an early failure.

This matches the measured final state of r54 same-frame clear-then-push and the r53 same-frame push-then-clear controls, as well as the parsed r51 reference: observer 3→4, action false, numeric 3, receipts `[6,3]`, Label `Value 3`, owner/callback true. Thus an explicit synthetic frame gap does not change these final measured postconditions; this neither proves the substeps identical nor supports a physical-timing claim. No tracked fixture or runner changes were made.

## Method and evidence

Unique independent scratch: `corpus/live/r55-frame-scout-independent/scratch/project/`; controls: `corpus/live/r55-frame-scout-independent/controls/{r54,r53,parsed}/`. The scratch copied the seeded fixture and altered only its clear-then-push branch to insert a frame after direct release and check the complete requested intermediate state, then push the matching release and await another frame. Edges 0–9 remained parsed. The eleven-edge history retained focus transfers/restorations, disconnect/reconnect, owner and signal-connection checks before each edge, and numeric/full receipt/Label postchecks after each frame. The explicit new substep check also verifies observer count has not advanced yet and owner/callback remain true.

Two-frame run output:
```
R55_CLEAR_FRAME observer=3->3 pressed=false value=3.0 receipts=[6.0, 3.0] label=Value 3 owner=true callback=true
SLIDER_CLEAR_THEN_PUSH_RELEASE values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true
ERROR: SLIDER CLEAR THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks
```
The terminal is the branch's exact expected-negative marker after successful per-edge assertions (exit 2), not an ordinary PASS exit. Controls each reached their own exact expected-negative terminal (exit 2): r54 `--clear-then-push-release`, r53 `--composite-push-and-clear`, and r51 `--observe-parsed-release`. Their checked terminal histories matched the previously reported measurements; see committed r54/r53 reports and lessons for their named non-author tuple receipts. Control paths are distinct scratch copies. No battery was run, and this scout makes no admission/verifier claim.

## Scope

Only the synthetic Godot 4.7.2 action-routing history and the stated frame-separated sequence. No claim about HSlider internal consumption, OS/physical input or timing, rendering, pointer/accessibility behavior, or production. No engine/editor/seeded edits, tracked fixture/runner edits, commit, push, or merge.
