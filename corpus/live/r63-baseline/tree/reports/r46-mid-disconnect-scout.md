# Round 46 mid-disconnect scout — direct Godot scratch

**Result: hypothesis confirmed in Godot 4.7.2; scratch only.** The callback was connected during setup and through edge 0; immediately after edge 0's parsed action and one `process_frame`, the scratch disconnected `_on_value_changed`. It kept the exact nine parsed action edges and Button/slider focus transfers from the r44 second-focus-restore case. Before each edge it asserted the focus owner; after each edge it asserted slider numeric value, cumulative receipts, and label.

Command (in isolated scratch project):

```text
godot --headless --path .shokunin/game-dev-2d/corpus/live/r46-mid-disconnect-scout/scratch --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --disconnect-after-first
```

Exit 0, after all nine checks: `SCOUT_MID_DISCONNECT values=6,6,6,5,5,5,5,4,4 receipts=[6] Label=Value 6`. Thus edge 0 recorded numeric 6, receipt `[6]`, label `Value 6`; each later edge preserved cumulative receipt `[6]` and label `Value 6`, including numeric transitions to 5 and 4.

Controls in the same scratch: connected r44 flags exited 0 with the same numeric sequence and receipts `[6,5,4]` / labels through Value 4; disconnect-at-start r45 flags exited 2 with numeric sequence unchanged but receipts `[]` / Label `Value 5`. These support a within-run callback-disconnect contrast. Scope is synthetic `Input.parse_input_event` plus frames only; no OS repeat, physical input/timing, rendered/pointer UI, accessibility, production, or claim about consumers of unchanged edges.

Scratch script is isolated at `corpus/live/r46-mid-disconnect-scout/scratch/slider_adjust.gd`; no tracked fixture or runner edits. Independent scout only; executor must implement any battery row and verifier must replay it.
