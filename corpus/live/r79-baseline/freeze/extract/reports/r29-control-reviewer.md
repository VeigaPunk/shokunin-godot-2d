# Round 29 independent focus-control review

## Scope and method

Independent paired scratch-only replay. No tracked files were edited. Scratch project and modified probe are under `corpus/live/r29-control-reviewer/`; it derives from tracked `corpus/fixtures/project.godot` and `button_activation.gd`. The same fixture script and input route were used in each arm; the only arm variable was whether `button.grab_focus()` ran before input. I replaced the unsupported `root.get_focus_owner()` with `get_root().gui_get_focus_owner()` in scratch, asserted focus state before actions, and printed focus owner and label/receipt after each action. Godot: `4.7.2.stable.arch_linux.ed1daf0bf`.

Commands, from repo root:

- `godot --headless --path .shokunin/game-dev-2d/corpus/live/r29-control-reviewer --script res://button_activation.gd`
- `godot --headless --path .shokunin/game-dev-2d/corpus/live/r29-control-reviewer --script res://button_activation.gd -- --no-focus`

## Raw results

Focused arm exit 0:

```text
RECEIPT step=1 count=1 text=Activated 1 focus=true owner_is_button=true owner=ActivateButton:<Button#26440893899>
RECEIPT step=2 count=2 text=Activated 2 focus=true owner_is_button=true owner=ActivateButton:<Button#26440893899>
PASS button_activation mode=focused focus=true owner_is_button=true step_texts=[Activated 1,Activated 2] receipts=[1,2]
```

Unfocused arm exit 2 (the intended first-step assertion, not setup):

```text
RECEIPT step=1 count=0 text=Ready focus=false owner_is_button=false owner=<Object#null>
ERROR: UI BUTTON ASSERTION FAILED: expected step1 text=Activated 1 receipts=1, got receipts=0 text=Ready
```

The no-focus setup assertion passed: button was in-tree, `has_focus()==false`, and `gui_get_focus_owner()` was null immediately before action. It remained unfocused after first action. Thus no auto-focus occurred and `ui_accept` did not activate the button without focus in this headless test; the focused arm received one signal per complete action pair, with owner remaining the button after each.

## Verdict

The paired control shows a real focus-dependent contrast under this exact headless Godot setup. This supports the declared calibration hypothesis, conditional on the tracked implementation and independent verifier replay. Scope is limited to programmatically routed `ui_accept` against a dynamically created headless Button. It says nothing about pointer activation, rendered UI, general GUI focus/accessibility behavior, or production scenes. The tracked fixture/runner were not modified by this reviewer. Scratch probe SHA-256: `d58a22b278b87897885ca96afaaf76f4a1e3b5bb7de935dcecda4ed4df780054`.
