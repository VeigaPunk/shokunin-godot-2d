# Round 28 repeat scout — Godot `ui_accept` timing

## Scope and setup

Scratch-only probe: `.shokunin/game-dev-2d/corpus/live/r28-repeat-scout-scratch/{project.godot,probe.gd}`. Ran with the installed Godot 4.7.2 binary:

```text
godot --headless --path .shokunin/game-dev-2d/corpus/live/r28-repeat-scout-scratch --script .shokunin/game-dev-2d/corpus/live/r28-repeat-scout-scratch/probe.gd
```

Exit 0. The probe creates an in-tree Button and Label, connects `Button.pressed` to a callback that increments a receipt and writes `Activated N`, focuses the Button, and sends two `ui_accept` press/release pairs with process-frame waits between events and actions.

## Raw output

```text
Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf
STEP1 pressed receipts=0 label=Ready
STEP1 release receipts=1 label=Activated 1
STEP2 pressed receipts=1 label=Activated 1
STEP2 release receipts=2 label=Activated 2
```

## Finding / bound

On this headless Godot 4.7.2 setup, `Button.pressed` is emitted on release, not on the `InputEventAction` press event. Each complete press/release action produces exactly one callback; the second action is distinct and increments state from 1 to 2. There was no *extra* receipt on release beyond the single expected activation (release is the activation edge here). Therefore executor assertions should inspect the first-step state after release, then ensure the next press itself leaves state unchanged, and the second release advances exactly once. Do not describe this as activation-on-press or as release producing zero receipts.

Bound: focused headless `ui_accept` route, no pointer hit testing, rendered UI, debounce/rate behavior, or broader input delivery claims. No engine/editor/seeded fixture changes.
