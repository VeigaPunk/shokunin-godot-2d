# Round 47 independent direct reconnect scratch — scout

**Result: HOLD / no production admission recommendation from this lane.** Godot 4.7.2 produced the predicted nine edge values, cumulative receipts, label, and focus ownership when run in a newly created, isolated scratch project. I did not edit `slider_adjust.gd` in the tracked battery or `run_battery.py`; only this report and `corpus/live/r47-reconnect-scout-scratch/` are mine.

## Setup and command

- Engine: `/usr/bin/godot`, `4.7.2.stable.arch_linux.ed1daf0bf`.
- Scratch: `corpus/live/r47-reconnect-scout-scratch/` (own minimal project, `HSlider` initialized in-tree at 5, callback connected before first edge; `Button` receives focus at edges 1–2 and 5–6).
- Run: `godot --headless --path . --script slider_adjust.gd` from that scratch directory. The script injects the same nine parsed events as r44/r46, checks GUI focus owner before each edge and numeric/signal receipts/label after it. After edge0 assertions, it disconnects and checks `is_connected == false`; after edge3 assertions, reconnects and checks `is_connected == true`.

## Evidence

Fresh scratch run exit **0**, output:

`PASS R47_RECONNECT values=6,6,6,5,5,5,5,4,4 receipts=[6] edges0-6,[6,4] edges7-8 Label=Value 4`

The runner asserts values `6,6,6,5,5,5,5,4,4`; cumulative receipts `[6]` through edge6, then `[6,4]` at edges7–8; label `Value 6` through edge6, then `Value 4`. The code explicitly asserts connection state after both changes. Per-edge focus owner schedule is slider, Button, Button, slider, slider, Button, Button, slider, slider. It asserted owner before every event and slider numeric/receipts/label after every frame. This was a new direct minimal reproduction, not a reuse of production battery behavior.

As a control, unmodified r46 scratch ran always-connected `--repeat-right --second-focus-restore` on Godot 4.7.2 and exited 0 with `values=6,6,6,5,5,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4`.

## Scratch iteration note / scope

My first scratch assertion used integer literal arrays against typed `Array[float]`, so it failed despite observed edge0 state being `6.0`, `[6.0]`, `Value 6`, and connected=true. I corrected the scratch expectations to floats and reran; the complete nine-edge scratch then passed. This was a test assertion typing mistake, not an engine mismatch. The positive run supports the specific synthetic parsed-event/frame history only; it does not establish OS repeat, physical timing/input, rendered/pointer UI, accessibility, production behavior, or internal consumers of unchanged events. No tracked files or seeded fixtures changed.
