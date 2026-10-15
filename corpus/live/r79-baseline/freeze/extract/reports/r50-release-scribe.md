# Round 50 release scribe — evidence/admission checklist

## Independent bounded scratch (Godot 4.7.2)

Own scratch: `.shokunin/game-dev-2d/corpus/live/r50-release-scribe/godot-scratch/` (`scratch.gd`, `run.log`, `run2.log`). Used a fresh in-tree HSlider (min 0, max 10, step 1, initial 5), Label callback, Button focus target, and synthetic parsed actions with one frame per edge. No tracked project, seeded corpus, engine, or editor files changed.

The sequence extends r49's ten edges with edge10 `ui_left` release, retaining slider focus and callback connection. Owner and callback state are checked before each edge; numeric value, full callback receipt list, and Label are checked after every frame.

| Edge | Action | Owner before | Numeric | Receipts | Label | Callback connected after |
|---:|---|---|---:|---|---|---|
| 0 | ui_right press | slider | 6 | [6] | Value 6 | no (disconnect after checks) |
| 1 | ui_right press | Button | 6 | [6] | Value 6 | no |
| 2 | ui_right release | Button | 6 | [6] | Value 6 | no |
| 3 | ui_left press | slider | 5 | [6] | Value 6 | no |
| 4 | ui_left release | slider | 5 | [6] | Value 6 | no |
| 5 | ui_left press | Button | 5 | [6] | Value 6 | no |
| 6 | ui_left release | Button | 5 | [6] | Value 6 | no |
| 7 | ui_left press | slider | 4 | [6] | Value 6 | yes (reconnect after checks) |
| 8 | ui_left release | slider | 4 | [6] | Value 6 | yes |
| 9 | ui_left press | slider | 3 | [6,3] | Value 3 | yes |
| 10 | ui_left release | slider | 3 | [6,3] | Value 3 | yes |

Two independent direct Godot 4.7.2 runs passed all eleven checks and printed `R50_SYNTHETIC_RELEASE_AFTER_FRESH_RECONNECT PASS`, exit 0. Expected calibration observation: the release following edge9 adds no new receipt and changes neither value nor Label. Scratch output is retained in both logs.

## Admission checklist

- [ ] Preserve r49 positive ten-edge mode and r48 negative nine-edge mode byte-exact. Add only distinct `--release-after-late-reconnect-press`, gated by `--repeat-right --second-focus-restore`.
- [ ] Reuse r49 edges 0–9 unchanged; add only edge10 fresh `ui_left` release.
- [ ] Assert owner and callback connection before every edge. For edge10, require slider focused and callback connected.
- [ ] Assert numeric/full receipts/Label after each frame. Edge10 must remain `3`, `[6,3]`, `Value 3`; unique expected-negative exit2 only after eleven checks.
- [ ] Confirm r49 positive exit0 and r48 negative exit2 remain unchanged, all older branches/rows byte-exact, and one new negative row only.
- [ ] Named non-author verification compares 63 ordinary/74 full prior baseline, all prior tuple rows/classifications, fault path, and targeted sabotage; retain raw evidence and hashes.

Evidence supports the narrow hypothesis that the synthetic parsed `ui_left` release after the fresh press leaves value/receipts/Label unchanged in this exact history. It does not establish OS repeat, physical input/timing, rendering/pointer behavior, accessibility, production, generic slider behavior, or internal consumer behavior. HOLD if tracked candidate/verifier differs. No edits to tracked fixture or runner by this scribe.
