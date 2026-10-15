# Round 53 baseline reviewer — composite route probe

Role: read-only baseline reviewer / causal scratch probe. No delegation and no tracked edits.

## Baseline

Round 52's bounded distinction is established in its paired reports and raw lesson: on the same Godot 4.7.2 synthetic eleven-edge focused/reconnected HSlider history, parsed edge10 yields observer release count 3→4 and global `ui_left` pressed true→false, while `root.push_input` alone yields 3→4 and leaves pressed true. Numeric value remains 3, receipts `[6,3]`, Label `Value 3`, with focus and callback checks. The paired r51 parsed and r52 push branches are additive controls, with r52 named non-author full-path 77/77 and prior rows/opt-ins retained. r52's simplifier tracked-scope breach and failed/tainted runs remain adverse, not evidence.

## Round 53 composite scratch result — hypothesis holds

Copied tracked `slider_adjust.gd` into unique scratch `.shokunin/game-dev-2d/corpus/live/r53-baseline-reviewer-scratch/project/slider_adjust.gd`. Changed only the scratch parsed-observer edge10 dispatch: construct matching `InputEventAction(action="ui_left", pressed=false)`, call `root.push_input`, then `Input.action_release("ui_left")` in that same frame boundary; edges0–9 remain unchanged parsed actions. Retained owner/callback prechecks, parsed-release observer check, global state check, and per-edge numeric/full receipt/Label assertions. No tracked fixture or runner edit.

Godot `4.7.2.stable.arch_linux.ed1daf0bf`, direct command with `--repeat-right --second-focus-restore --observe-parsed-release`: `godot --headless --path <scratch>/project --script slider_adjust.gd -- --repeat-right --second-focus-restore --observe-parsed-release`. At edge10 output: `R53_COMPOSITE edge10 observer=3->4 pressed=false value=3.0 receipts=[6.0, 3.0] label=Value 3 focus=true callback=true`. All eleven checks completed; unique existing parsed-observer terminal marker printed and expected terminal assertion exited 2. This establishes that this explicit composite bypass satisfies both r51 observer+pressed-state checks and all listed slider-state observations in this one synthetic route, despite not using parsed-event delivery at edge10.

The result supports exactly the proposed dedicated composite expected-negative calibration control if the sole executor adds it additively and non-author verification confirms it. It does not itself verify a tracked case, battery, classifier, prior tuple stability, or full-path admission; those remain parent/executor/verifier work.

## Scope and integrity

This is synthetic Godot 4.7.2 route evidence only. It does not establish HSlider internal consumption, OS/physical input or timing, rendering, pointer/accessibility, production, or generic provenance. No engine/editor/seeded edits, tracked fixture/runner edits, commit, push, or merge. Current tracked hashes remain fixture `eeea197a8a566ecb3fb48c929985d63bd5723796bb54467d24a382c352a31010` and runner `168058fa168917a39a3c561deef2102b93ea10df983cf6c5e30081fb0ca10c4c`.
