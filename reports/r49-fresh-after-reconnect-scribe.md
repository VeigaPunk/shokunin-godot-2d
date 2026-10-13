# Round 49 fresh-after-reconnect scribe — evidence/admission checklist

## Independent bounded scratch (Godot 4.7.2)

Own scratch: `.shokunin/game-dev-2d/corpus/live/r49-fresh-after-reconnect-scribe/godot-scratch/` (`scratch.gd`, `run.log`, `run2.log`). Ran headless Godot 4.7.2 against a fresh in-tree HSlider (min 0, max 10, step 1, initial 5), Label callback, Button focus target, and synthetic parsed actions with one frame per edge. No tracked project, seeded corpus, engine, or editor files changed.

The sequence is r48's nine events plus one fresh `ui_left` press at edge9. The scratch asserts focus ownership before every event, then asserts numeric value, cumulative callback receipts, and Label after each frame. It checks callback connected before edge0; disconnects only after edge0's 6/[6]/Value6 checks and verifies disconnected through edge7; verifies edge7's 4/[6]/Value6 before reconnecting; verifies connection remains true across edge8 and edge9.

| Edge | Action | Focus owner before | Numeric | Receipts | Label | Connected after |
|---:|---|---|---:|---|---|---|
| 0 | ui_right press | slider | 6 | [6] | Value 6 | no (disconnect after assertions) |
| 1 | ui_right press | Button | 6 | [6] | Value 6 | no |
| 2 | ui_right release | Button | 6 | [6] | Value 6 | no |
| 3 | ui_left press | slider | 5 | [6] | Value 6 | no |
| 4 | ui_left release | slider | 5 | [6] | Value 6 | no |
| 5 | ui_left press | Button | 5 | [6] | Value 6 | no |
| 6 | ui_left release | Button | 5 | [6] | Value 6 | no |
| 7 | ui_left press | slider | 4 | [6] | Value 6 | yes (reconnect after assertions) |
| 8 | ui_left release | slider | 4 | [6] | Value 6 | yes |
| 9 | ui_left press | slider | 3 | [6, 3] | Value 3 | yes |

Corrected run ended `R49_SYNTHETIC_FRESH_AFTER_RECONNECT PASS`, exit 0, after all ten checks. First scratch iteration failed at edge9 because the inherited r48 generic check still expected Label `Value 6` after the newly connected callback fired; that was a scratch assertion defect, not a different Godot observation. Corrected the scratch-only edge9 assertion and reran; full output is retained. Do not count the first run as positive evidence.

## Admission checklist for executor/verifier

- [ ] Keep r48 nine-edge expected-negative mode and its row byte-exact; keep all r47–r44 branches and rows byte-exact. Add only a distinct positive `--press-after-late-reconnect` mode gated by `--repeat-right --second-focus-restore`.
- [ ] Reuse exactly r48's first nine action/focus/connection transitions and per-edge state checks; edge9 is one additional fresh `ui_left` press with slider focus and callback connected.
- [ ] Require values `6,6,6,5,5,5,5,4,4,3`; receipts `[6]` through edge8 then `[6,3]`; Label `Value 6` through edge8 then `Value 3` at edge9. Check owner before each event and all three outputs after each frame.
- [ ] Assert callback connected before edge0, false after edge0 and through edge7 action, true only after verified edge7 state and through edges8–9.
- [ ] Positive exit 0 only after ten checks. Preserve paired r48 expected-negative exit2 after nine checks and its unique diagnostic.
- [ ] Run ordinary/full baseline comparison; preserve all prior tuple-bearing rows and nine prior opt-in classifications; add exactly one positive tuple row if causal. Keep raw result and hashes.
- [ ] Named non-author verifier replays full default path and fault path, plus targeted sabotages; no broad error classifier. No publishing, commit, push, or merge by this scribe.

Measurement supports the proposed bounded synthetic parsed-event/frame hypothesis. It does not establish OS repeat, physical input/timing, rendered/pointer UI, accessibility, production, generic slider behavior, or internal consumer behavior on unchanged edges. HOLD if the tracked candidate or verifier differs from this scratch result.
