# Round 44 second-restore scout

## Direct scratch probe

Created a fresh scratch project at `.shokunin/game-dev-2d/corpus/live/r44-second-restore-scout` from the fixture project settings and current `slider_adjust.gd`, with a scratch-only nine-edge branch. No tracked fixture or engine/editor files were edited. Ran real Godot `4.7.2.stable.arch_linux.ed1daf0bf`:

```text
timeout 30s godot --headless --path .shokunin/game-dev-2d/corpus/live/r44-second-restore-scout --script res://slider_adjust.gd -- --repeat-right --second-focus-loss
exit 0
PASS SLIDER_REPEAT_SECOND_RESTORE values=6,6,6,5,5,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4
```

The scratch branch started with connected in-tree HSlider min0/max10/step1/value5 and focus. It used nine fresh parsed `InputEventAction` press/release edges, awaiting one process frame per edge. Before every edge it asserted the focus owner: slider at 0,3,4,7,8; Button at 1,2,5,6. After every edge it asserted numeric value, cumulative `value_changed` receipt history, and Label. Focus was explicitly restored to the slider before edge 7.

Observed history: edge 0 `ui_right` press → 6 / `[6]` / Value 6; edges 1–2 while Button owns focus → 6 / `[6]` / Value 6; edges 3–4 after first restoration → 5 / `[6,5]` / Value 5; edges 5–6 after second Button handoff → 5 / `[6,5]` / Value 5; edges 7–8 after second restoration → 4 / `[6,5,4]` / Value 4. This agrees with the nine-edge hypothesis. The direct scratch evidence supports proceeding; it does not establish OS auto-repeat, physical timing, rendered/pointer UI, accessibility, production behavior, or internal consumption of unchanged edges.
