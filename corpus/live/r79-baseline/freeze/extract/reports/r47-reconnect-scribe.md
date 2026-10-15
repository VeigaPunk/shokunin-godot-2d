# Round 47 reconnect scratch and read-only admission checklist

## Claim and boundary
Round 47 tests only the callback reconnection claim: initial callback connected; edge0 `ui_right` press changes HSlider 5→6 and records `[6]` / `Value 6`; disconnect after checking edge0; edge3 `ui_left` press changes 6→5 while disconnected, preserving `[6]` / `Value 6`; reconnect after checking edge3; edges7–8 change 5→4 and record `[6,4]` / `Value 4`. The candidate is restricted to `--repeat-right --second-focus-restore --reconnect-after-first-left`. This is Godot headless synthetic parsed events and frames only.

## Scratch evidence (scribe-authored, no tracked files edited)
Scratch: `corpus/live/r47-reconnect-scribe-scratch/` (`project.godot`, `slider_adjust.gd`). Engine: `4.7.2.stable.arch_linux.ed1daf0bf`.

Scratch explicitly asserts callback `is_connected` at setup, before/after disconnect on edge0, before and after reconnect following edge3; for each of nine events it checks expected focus owner before `_action`, then checks numeric value, cumulative receipts and label after one `process_frame`. Results:

- Candidate bounded command: `timeout 20s godot --headless --path <scratch> --script slider_adjust.gd -- --repeat-right --second-focus-restore --reconnect-after-first-left` → exit 0, `PASS SLIDER_RECONNECT_AFTER_FIRST_LEFT values=6,6,6,5,5,5,5,4,4 receipts=[6,4] Labels=Value 6,Value 4`.
- Paired connected r44 scratch mode → exit 0, expected values and `[6,5,4]`, labels Value 6/5/4.
- Paired disconnected-at-start r45 mode → exit 2 after nine checks, expected values, `receipts=[]`, `Label=Value 5`.
- Paired disconnect-after-edge0 r46 mode → exit 2 after nine checks, expected values, `receipts=[6]`, `Label=Value 6`.

Initial attempt at the candidate scratch had a GDScript typed-array assignment error (`Array` to `Array[float]`) and exited 143. This was a scratch construction error, not an observed behavior mismatch. Changed only scratch declarations to inferred arrays; bounded retry completed with the evidence above. Retain initial failed attempt as adverse scratch telemetry, not as a Godot behavior verdict.

## Read-only admission checklist / remaining evidence
- [x] Real Godot 4.7.2 scratch first; candidate observed as described.
- [x] Connected, start-disconnected, and after-first-disconnect paired controls observed in scratch.
- [x] Candidate distinct positive exit 0 only after all nine assertions.
- [x] Callback connection transitions explicitly asserted by `is_connected`.
- [ ] Executor integration of one opt-in battery row and candidate mode in tracked fixture/runner.
- [ ] Named independent non-author full replay; compare the 62 prior tuple-bearing rows and nine opt-in classifications; fault and sabotage evidence.
- [ ] Confirm ordinary/full counts advance from 60/71 to 61/72 only if admitted; confirm all unrelated working-tree changes remain untouched.
- [ ] Parent admission verdict, then report-last commit if admitted. No push or merge.

Recommendation from scratch evidence alone: candidate behavior is supported; do **not** claim round admission until independent full-battery verification and parent review. Preserve synthetic-only scope: no OS key repeat, physical input or timing, rendered/pointer UI, accessibility, production, generic HSlider, or internal-consumer claim.
