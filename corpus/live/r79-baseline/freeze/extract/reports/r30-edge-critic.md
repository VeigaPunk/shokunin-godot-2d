# Round 30 edge-attribution critic (read-only)

## Verdict
The proposed edge split is falsifiable and locally reproduced in Godot 4.7.2: with a verified focused Button and connected `pressed` callback, an isolated `ui_accept` press followed by one `process_frame` leaves receipt/text unchanged; a release followed by one frame increments the receipt and changes the Label. Two actions reproduce the sequence `0/Ready -> press still 0/Ready -> release 1/Activated 1 -> press still 1/Activated 1 -> release 2/Activated 2`. This supports a bounded distinction for this synthetic headless path, not a claim that the engine signal itself is emitted at a precisely timed physical edge.

## Raw scratch evidence
Owned scratch: `.shokunin/game-dev-2d/corpus/live/r30-edge-critic/edge_probe.gd`; command `godot --headless --path .shokunin/game-dev-2d/corpus/live/r30-edge-critic --script res://edge_probe.gd`, exit 0, Godot 4.7.2. Output:

```text
EDGE setup focus=B:<Button#201242715342> has_focus=true receipts=0 text=Ready
PRESS_ONLY index=1 receipts_before=0 receipts_after=0 text=Ready
EDGE release_1 focus=B:<Button#201242715342> has_focus=true receipts=1 text=Activated 1
PRESS_ONLY index=2 receipts_before=1 receipts_after=1 text=Activated 1
EDGE release_2 focus=B:<Button#201242715342> has_focus=true receipts=2 text=Activated 2
PASS edge split
```

The probe checks the focus owner and `has_focus` through state observations and retains callback/Label receipt evidence. A second disposable scratch variant omits the first release and expects the release receipt; command with `edge_probe_missing_release.gd` exits 2 at `release assertion failed`, with focus still on B but receipts 0 and text Ready. This establishes a meaningful missing-release adverse case, not merely a missing setup/focus failure.

## Attribution limits and pitfalls
- Never insert **press then release before the first wait**, as r29/r28 did with `_send_action`: the pair-wise check only shows that the action completed; it cannot discriminate edge attribution. Await and assert after press before sending release, then await and assert after release. Repeat independently for action two.
- A frame wait is a scheduling boundary, not a proof of physical timing or a universal latency bound. Here the tested sequence and `root.push_input` are deterministic in this local headless run. Preserve focus-owner checks before/after, and report the observed boundary precisely. Do not call one process frame a general input-processing guarantee.
- The watched `Button.pressed` callback is a semantic activation receipt; prior r28 scout and this split both observe it on release. Alternative observations (`button_down`, `button_up`, `gui_input`, or `Input.is_action_just_pressed/released`) answer different questions and could corroborate event delivery, but must not be substituted silently for the pressed callback/Label behavior. A different callback wired to the same counter or a direct `pressed.emit()` can create receipts without routed input; verify this fixture's callback connection and actual focused `ui_accept` path, and do not attribute counters alone to engine edge handling.
- Explicitly re-check target focus at edge boundaries: focus could transfer or be absent. Existing disconnected and `--no-focus` controls remain useful but diagnose wiring/focus, not release attribution; their expected step1 failure must not be mistaken for an edge assertion. Do not alter their intended paths.
- Missing release should fail at the intended first release assertion while setup and press-only state pass. A second press without an intervening release, or release omission only after the first completed activation, may test a different held-action/repeat behavior and is not interchangeable with this check.

## Scope / integrity
Read-only critic: no tracked fixture, runner, seeded fixture, project or engine files changed. Current hashes: `button_activation.gd` `f0b4c61bdf1444e3116d298c44debc32a74e389a27437bba50525e447cb9fb62`; `run_battery.py` `097058b23fb53f38dd8cbede34559d7ef6a2999c8568ea598d7a2c57d1b3ff38`. No full battery or verifier claim is made by this critic. No pointer hit-test, rendered UI, real-user timing/debounce, arbitrary mutation resistance, or general production behavior claim.
