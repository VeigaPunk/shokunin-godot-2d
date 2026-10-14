# Round 49 independent direct scratch — fresh adjustment after late reconnect

Reviewer role: independent bounded Godot scratch; no tracked fixture/runner edits. Scratch: `.shokunin/game-dev-2d/corpus/live/r49-reviewer-unique-20261013/` (unique, copied r48 reviewer project, mode added locally only). Engine: `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`.

## Commands and observations

- `godot --headless --path .shokunin/game-dev-2d/corpus/live/r49-reviewer-unique-20261013 --script slider_adjust.gd -- --repeat-right --second-focus-restore --press-after-late-reconnect` exited **0**. It emitted ten per-edge checks. Focus owner before edges 0,3,4,7,8,9 was HSlider; before 1,2,5,6 Button. Edges 0–8 matched numeric `6,6,6,5,5,5,5,4,4`, callback receipts `[6]`, Label `Value 6`. Edge0 began connected, yielded 6/[6]/Value6, then disconnected; remained disconnected through edge7 numeric4, then reconnected after edge7 verification. Edge8 release held 4/[6]/Value6 and was connected. Fresh edge9 `ui_left` press with slider focus and callback connected yielded numeric3, receipts `[6,3]`, Label `Value 3`, connected. All ten edges asserted focus before and numeric/receipts/Label after; connection transitions were asserted; positive exit followed checks.
- Paired preserved r48 command `... --repeat-right --second-focus-restore --reconnect-after-final-left` exited **2** with its expected-negative marker after nine checks: values `6,6,6,5,5,5,5,4,4`, `[6]`, Value6.

## Finding

Direct evidence supports the r49 hypothesis on Godot 4.7.2 in headless synthetic parsed actions and process frames. This validates the proposed extra fresh press after reconnection; it does not cover physical input/OS repeat, rendered/pointer interaction, accessibility, production use, or general signal-replay semantics. No tracked implementation files were edited.
