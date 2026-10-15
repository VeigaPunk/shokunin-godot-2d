# Round 48 independent late-reconnect scratch review

Bounded independent scratch: `corpus/live/r48-late-reconnect-reviewer-scratch/`, copied from the r47 reconnect scratch. Only this private scratch was changed; no tracked fixture/runner, seeded corpus, engine/editor, or production source was edited.

Engine: `4.7.2.stable.arch_linux.ed1daf0bf`.
Command: `timeout 30s godot --headless --path . --script slider_adjust.gd -- --repeat-right --second-focus-restore --reconnect-after-final-left`
Result: exit 2, with the unique `R48_LATE_RECONNECT_EXPECTED_NEGATIVE` marker printed only after all nine owner-before and numeric/receipt/Label-after checks. The sole subsequent `push_error` is the planned expected-negative terminal; no earlier assertion failed.

Callback connected at initialization and confirmed connected before edge0 disconnect; disconnected immediately after edge0 and remained disconnected through edge7's value change. After verifying edge7 value 4 / receipts `[6]` / Label `Value 6`, the callback was reconnected and verified connected; it remained connected through edge8 release. No retroactive receipt or Label update occurred on reconnection.

| edge | action | focus owner before | numeric after | cumulative receipts | Label after | callback after |
|---:|---|---|---:|---|---|---|
| 0 | ui_right press | HSlider | 6 | [6] | Value 6 | disconnected after verified adjustment |
| 1 | ui_right press | Button | 6 | [6] | Value 6 | disconnected |
| 2 | ui_right release | Button | 6 | [6] | Value 6 | disconnected |
| 3 | ui_left press | HSlider | 5 | [6] | Value 6 | disconnected |
| 4 | ui_left release | HSlider | 5 | [6] | Value 6 | disconnected |
| 5 | ui_left press | Button | 5 | [6] | Value 6 | disconnected |
| 6 | ui_left release | Button | 5 | [6] | Value 6 | disconnected |
| 7 | ui_left press | HSlider | 4 | [6] | Value 6 | reconnected after checks |
| 8 | ui_left release | HSlider | 4 | [6] | Value 6 | connected |

Observed numeric sequence `6,6,6,5,5,5,5,4,4`; receipts `[6]` and Label `Value 6` throughout. This supports only the requested synthetic parsed-input/frame behavior in this bounded Godot 4.7.2 scratch; not OS repeat, physical input/timing, rendered/pointer UI, accessibility, production behavior, or general signal semantics.
