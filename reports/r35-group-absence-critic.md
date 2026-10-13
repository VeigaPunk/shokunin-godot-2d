# Round 35 group-absence critic (read-only)

## Result
The causal contrast is supported on the current Godot 4.7.2 headless runtime. No tracked source edits were made by this critic. The actual tracked fixture/runner already contain concurrent working-tree edits from the executor; I inspected them but did not modify either.

## Independent scratch replay
Scratch corpus: `.shokunin/game-dev-2d/corpus/live/r35-group-absence-critic/` (project copy and independent probe scripts). Godot: `4.7.2.stable.arch_linux.ed1daf0bf`.

I independently replayed the current positive fixture:

- `godot --headless --path .shokunin/game-dev-2d/corpus/fixtures --script button_group_selection.gd` → exit 0. It observes A=false/B=true after focused B; receipts `[A:false,B:true]`, Label B. Then A=true/B=false after focused A; receipts `[A:false,B:true,B:false,A:true]`, Label A.
- A compact scratch-only paired probe uses the same A/B setup, native toggle-mode Buttons, signal handlers, focus steps, and `_send_accept()` press/release `ui_accept` pair, varying only whether B is assigned to `group`. Its entire output:

```
GROUPED setup A=true B=false receipts=[] label=A group_alive=true members=2
focusB=true
after_B A=false B=true receipts=["A:false", "B:true"] label=B
focusA=true
after_A A=true B=false receipts=["A:false", "B:true", "B:false", "A:true"] label=A

UNGROUPED setup A=true B=false receipts=[] label=A group_alive=true members=1
focusB=true
after_B A=true B=true receipts=["B:true"] label=B
focusA=true
after_A A=true B=true receipts=["B:true", "A:true"] label=A
```

These exact observations verify group object remains live, is shared by A/B in positive (two members) and only A in negative (one member), initial A-selected/B-unselected state is the same, both targets own focus, and both actions are executed in each arm. B's absent association is the only treatment difference. Ungrouped B naturally turns on without deselecting A and emits B:true; A is already on on the second action, so no A:false/B:false callbacks occur, while B signal updates the shared Label to B and then A's signal updates it to A. This is a state/receipt contrast, not an unobserved expected callback assumption.

I also ran the current `--ungroup-b` fixture directly. It emits `BUTTON_GROUP_UNGROUPED after_B A=true B=true receipts=["B:true"] label=B`, then exits 2 on the intended after-B exclusivity assertion. The selected arm's expected grouped positive remains exit 0. Current working tree already contains an ungroup-b branch in the fixture/runner, which encodes the candidate exact negative outcome, but this critic did not validate the complete battery admission/verifier.

## Falsification checks
- **B association:** Current grouped fixture assigns `a.button_group = group` and `b.button_group = group` before input. Scratch group reports two members. Removing only B assignment gives one member, same setup, and both remain selected after B.
- **Group lifetime:** The same `ButtonGroup` local remains referenced by A during each complete run; instance is valid after tree entry, and membership counts remain meaningful. No evidence of premature group destruction.
- **Focus/actions:** B and A each become `gui_get_focus_owner()` before their corresponding action. Both arms use identical focus calls and press/release construction; no extra B refocus or differing key/action sequence.
- **Initial A state:** Both arms start with A selected and B unselected, no setup toggled receipts, Label A. Setup assertion occurs before focus/action.
- **Signal wiring:** Both signal handlers are connected before first frame in both connected arms. In ungrouped run, B:true callback is observed; A has no callback when already selected. The paired fixture disconnected mode should expect no receipts/Label A after B and fail on the intended disconnected signal assertion (not an association issue).
- **Control type:** Native `Button` toggle_mode + ButtonGroup, not a `RadioButton` class.

## Recommendation
Read-only causal review supports the r35 treatment. Admit only if the executor/verifier confirms the registered battery classifies the bounded expected exit-2 negative by exact signature and prior r34 outcomes are preserved. Keep claim narrow: grouped vs ungrouped toggle-mode Button selection under this specific headless focused `ui_accept` sequence. No generic ButtonGroup guarantee or rendered/pointer/physical input claim.
