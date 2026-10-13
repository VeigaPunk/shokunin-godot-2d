# Round 45 independent paired scratch review

## Result: HOLD — paired numeric history is supported, but disconnected-path classification fails

Ran real Godot 4.7.2.stable.arch_linux.ed1daf0bf in independent scratch `corpus/live/r45-double-restore-disconnect-reviewer/` using a copied in-tree `slider_adjust.gd` and fresh minimal Godot 4 project. No fixture, runner, engine/editor, or seeded-corpus files were edited.

Commands (both direct real-engine runs, not seeded battery):

- Connected: `godot --headless --path .shokunin/game-dev-2d/corpus/live/r45-double-restore-disconnect-reviewer --script slider_adjust.gd -- --repeat-right --second-focus-restore`
- Disconnected: same command with `--disconnect-signal` appended.

Both exited 0 and reported same numeric values `6,6,6,5,5,5,5,4,4`, receipts `6,5,4`, Labels `Value 6,Value 5,Value 4`. In the fixture's nine-edge branch, each iteration asserts expected focus owner before dispatch and then value, full receipt history, and Label after one frame. In disconnected mode, the expected history is empty and Label remains `Value 5` at every edge; completion output is misleadingly hard-coded as the connected PASS line.

This does **not** meet the declared disconnected-control contract: after the nine checks, `--second-focus-restore` unconditionally prints PASS and `quit(0)`. It never emits the expected-negative terminal exit 2 for disconnected mode. The independent run therefore falsifies the proposed battery row/classifier even though the nine per-edge state assertions passed. Correct terminal branching is required before admission; preserve the nine checks and connected r44 behavior, and only then re-run the causal scratch and battery. No battery result or calibration improvement is claimed here.

Scope is synthetic parsed actions plus frames, not OS repeat, physical keyboard/timing, rendered/pointer UI, accessibility, or production behavior.
