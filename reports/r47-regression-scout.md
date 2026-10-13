# Round 47 regression scout — callback reconnect after first left press

Read-only regression scout. I read the standing brief and Round 47 declaration in `LOG.md`. I made no tracked fixture/runner edits and did not modify seeded fixtures, engine/editor files, commit, push, or merge. Scratch is isolated at `corpus/live/r47-regression-scout/scratch/`.

## Direct Godot 4.7.2 scratch result

Godot reports `4.7.2.stable.arch_linux.ed1daf0bf`. I copied the fixture project into scratch and added only the proposed candidate branch there. Exact candidate command:

```text
godot --headless --path .shokunin/game-dev-2d/corpus/live/r47-regression-scout/scratch --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --reconnect-after-first-left
```

Exit **0**, with a distinct positive marker only after all nine edge checks:

```text
SLIDER_RECONNECT_AFTER_FIRST_LEFT values=6,6,6,5,5,5,5,4,4 receipts=[6,4] Label=Value 4
PASS slider_adjust_repeat_second_focus_restore_reconnect_after_first_left
```

The scratch asserts focus ownership before each edge, then numeric value, cumulative receipts, and Label after each frame. It explicitly asserts the callback connected after edge 0, disconnected after edge 0, remains disconnected immediately before reconnect after edge 3, and connected after edge 3. Edge 3 (`ui_left` press) changes numeric value to 5 with receipts `[6]` / `Value 6`; callback is reconnected only after those checks, before edge 4. Edges 0–6 produce values `6,6,6,5,5,5,5`, receipts `[6]`, Label `Value 6`; edges 7–8 produce 4, receipts `[6,4]`, Label `Value 4`.

Paired commands using the same scratch project:

- r44 `--repeat-right --second-focus-restore`: exit 0; expected connected positive marker, values `6,6,6,5,5,5,5,4,4`, receipts `6,5,4`, Labels through `Value 4`.
- r45 additionally `--disconnect-signal`: exit 2 after nine checks; marker reports same numeric sequence, receipts `[]`, Label `Value 5`.
- r46 additionally `--disconnect-after-first`: exit 2 after nine checks; marker reports same numeric sequence, receipts `[6]`, Label `Value 6`.

One initial scratch run failed before executing because a GDScript conditional expression assigned an untyped array to `Array[float]`; I corrected the scratch-only construction and reran. It is not candidate evidence. The successful scratch run used explicit `is_connected` assertions; this is feasible in-tree as well.

## Regression notes / scope

This is evidence for the narrow synthetic sequence and callback wiring transition, not OS auto-repeat, physical timing/input, rendered/pointer UI, accessibility, production behavior, generic HSlider semantics, or internal consumption of unchanged events. The r44–r46 full battery rows and fixtures remain read-only comparator evidence; this scout did not replay the entire battery or recertify their prior verifier tuples.

Fault-injection caveat from prior r44–r46 artifacts: an outer/meta PASS is not evidence that every injected fault passed. In each raw fault record, the deliberate hang/timeout and unrelated-error cases are inner FAILs; only the clean expected-negative inner case is PASS. Timeouts bound the tested child invocation, not general cleanup/descendant behavior. Export caveat: prior export readiness/launch evidence is separate; r25 recorded `probe_export_launch` failure for a relative path (`Prepare Template: The given export path doesn't exist.`), so readiness does not establish generic export reliability. No timeout, fault, or export path was changed or retested here.
