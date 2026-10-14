# Round 35 group-absence reviewer — scratch evidence

## Result

The paired scratch probe supports the proposed causal distinction in Godot 4.7.2: both controls toggle independently when B is omitted from the shared `ButtonGroup`; the grouped pair remains exclusive. The unmodified grouped fixture's focused B→A action path and callback/Label assertions reproduce. The current stock fixture cannot serve as the ungrouped arm unchanged: its first post-B exclusivity assertion correctly exits 2 before reporting callbacks. I made only scratch copies and relaxed that assertion in the ungrouped copy to observe the complete two-action outcome.

## Method and raw evidence

Scratch directory: `.shokunin/game-dev-2d/corpus/live/r35-group-absence-reviewer-scratch/` (`grouped.gd`, `ungrouped.gd`, `project.godot`, and raw `grouped.out` / `ungrouped.out`). Both run under `/usr/bin/godot` 4.7.2 headless. Each starts with A selected and Label `A`, connects the same toggled handlers, then focuses B, sends `ui_accept`, focuses A, sends `ui_accept`. The only setup difference is omitting `b.button_group = group` from ungrouped. In ungrouped scratch I replaced only expected-exclusive-state/signal assertions with observational prints, preserving action/focus logic. Initial ungrouped run with the stock assertion returned 2 at after-B, as expected; final observational run exits 0.

Grouped raw observations:

```text
BUTTON_GROUP after_B A=false B=true receipts=["A:false", "B:true"] label=B
BUTTON_GROUP after_A A=true B=false receipts=["A:false", "B:true", "B:false", "A:true"] label=A
PASS button_group_selection exclusive=true toggled=[A:false,B:true,B:false,A:true] labels=[B,A]
```

Ungrouped raw observations:

```text
UNGROUPED after_B A=true B=true receipts=["B:true"] label=B focus=@Button@3:<Button#26508002767>
BUTTON_GROUP after_B A=true B=true receipts=["B:true"] label=B
UNGROUPED after_A A=true B=true receipts=["B:true", "A:true"] label=A focus=@Button@2:<Button#26457671116>
UNGROUPED final receipts=["B:true", "A:true"] label=A
BUTTON_GROUP after_A A=true B=true receipts=["B:true", "A:true"] label=A
```

Fixture explicitly verifies after each focus change that both `has_focus()` and viewport `gui_get_focus_owner()` identify the target before sending the action. Raw owner object IDs are runtime-specific; the target checks plus log objects establish focus owner B then A. The focus print occurs after each action and is not itself the pre-action focus proof.

## Assessment / caveats

- B→A sequences diverge only at group behavior: grouped `[A:false,B:true,B:false,A:true]`, states `(false,true)→(true,false)`; ungrouped `[B:true,A:true]`, states `(true,true)→(true,true)`. In both arms Label follows the last newly pressed button (`B`, then `A`).
- A is already selected in both setups. Therefore A's second action is a no-op grouped (B turns off and A on, both receipts), but emits `A:true` ungrouped because A remained selected throughout and focusing/accepting it? **Correction:** the raw output says `A:true`; it is not a no-op. A was unexpectedly toggled on the action path despite already `button_pressed=true` in ungrouped. This observed transition is exactly why the sequence must be measured, not guessed. It implies focus-accept produces the A toggled callback even with its state true, while final property remains true; preserve this raw behavior and avoid asserting conventional no-op assumptions.
- The stock ungrouped fixture exits 2 at the after-B state assertion before it can record callbacks. If used as the negative/control, give it a separately bounded expected-negative classification at the after-B assertion or change the fixture's mode-specific expected assertions; do not treat early exit alone as proof of the callback/Label sequence. The complete scratch observation proves the latter.
- No RadioButton type, rendered/pointer behavior, physical timing, accessibility, production behavior, or general ButtonGroup guarantee is assessed. No tracked fixture/runner files modified.
