# Round 3 UI scouting — model signal to HUD Label

Read-only proposal and runtime probe (Godot 4.7.2 headless). No corpus fixture, runner, engine/source, or tracked file was edited. A temporary project under `/tmp` was used solely to test the API pattern.

## Proposed fixture

Use a standalone `SceneTree` script with a tiny model node declaring `signal score_changed(value: int)` and a setter that updates its model value then emits it. Create a `CanvasLayer` and child `Label` (`Score: 0`), add both to `root`, add the model, connect `score_changed` to a same-script handler that writes `label.text = "Score: " + str(value)`, then set score to 7. Assert exact text `Score: 7`; print a stable PASS signature and quit 0. This tests the observable HUD control state after a real signal callback, not pixels or visible rendering.

For the negative control, accept `--disconnected` and skip the model-to-handler `connect()` while keeping the same model update and assertion. The unchanged assertion should fail (distinct exit 2) with expected/actual text in its diagnostic. The only intended difference is signal connectivity. Keep both cases in the same script and avoid an `await process_frame`: synchronous signal emission and callback are immediate, so no timing condition is needed.

## Runtime evidence

Executed the proposed pattern from an isolated temporary project with `godot --headless --path <tmp> --script res://ui_signal.gd` on Godot `4.7.2.stable.arch_linux.ed1daf0bf`.

- Connected: exit 0, `PASS ui_hud signal_connected=true label_text=Score: 7`.
- `--disconnected`: exit 2, assertion observed `expected Score: 7, got Score: 0`.
- Neither run emitted `SCRIPT ERROR:` or `Parse Error:`. The disconnected run's `ERROR` is the intentional `push_error` assertion diagnostic.

## Scope cautions

A `Label` under `CanvasLayer` establishes HUD-like scene ownership and a state update in headless mode; it does not establish font rendering, viewport visibility, layout, theme, input behavior, or pixel correctness. The control isolates the missing connection but does not exercise disconnect-after-connect, duplicate connections, or asynchronous signal ordering. A fixture should reject parse/script errors as the battery already does and verify the positive and negative signatures plus exact exit codes.
