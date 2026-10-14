# Round 49 fresh-after-late-reconnect simplifier

## Result
Independent bounded Godot 4.7.2 scratch supports the requested causal hypothesis. I did not edit tracked fixtures or runner.

Scratch: `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r49-fresh-after-reconnect-simplifier/scratch-40c3df4bf7` (fresh unique directory; copied only fixture `project.godot` and `slider_adjust.gd`, modifying the latter only in scratch). Engine: `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`.

## Minimal additive branch design
Preserve the existing r48 `--reconnect-after-final-left` branch byte-for-byte. Add a new higher-priority sibling gated by all three flags `--repeat-right`, `--second-focus-restore`, `--press-after-late-reconnect`. It reuses the nine r48 edges verbatim and appends only edge9 `ui_left` pressed. Keep expected values `[6,6,6,5,5,5,5,4,4,3]`; keep connection history connected before edge0, disconnected after edge0 through edge7, reconnect after asserting edge7 numeric4/receipts[6]/Label Value6, connected at edge8 and edge9. Assert expected focus owner before each edge (other button edges1,2,5,6; slider all others); assert numeric value, cumulative receipts, and label after each frame. At edge9 require numeric3, receipts `[6,3]`, `Value 3`, connected. Emit unique PASS and exit0 only after ten assertions. No shared helper refactor needed; leave r48 branch unchanged.

## Measurements
Candidate scratch command:
`godot --headless --path "/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r49-fresh-after-reconnect-simplifier/scratch-40c3df4bf7" --script slider_adjust.gd -- --repeat-right --second-focus-restore --press-after-late-reconnect`
Exit 0; output `PASS SLIDER_FRESH_AFTER_LATE_RECONNECT values=6,6,6,5,5,5,5,4,4,3 receipts=[6,3] Label=Value 3 connected=true`.

Paired unchanged r48 command in a separate fresh scratch, with `--reconnect-after-final-left`, exited 2 after nine checks and printed `SLIDER_LATE_RECONNECT values=6,6,6,5,5,5,5,4,4 receipts=[6] Label=Value 6 connected=true`, followed by its expected-negative assertion. No divergence; no HOLD.

## Scope
Synthetic parsed `InputEventAction` events plus process frames only. This does not test OS key repeat, physical input/timing, rendering/pointer UI, accessibility, production behavior, generic signal replay, or internal consumers of unchanged edges. No engine/editor/seeded fixture edits. No tracked fixture/runner changes, commit, push, or merge by this read-only simplifier lane.
