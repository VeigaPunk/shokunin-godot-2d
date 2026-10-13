# Round 48 late-reconnect critic — adversarial review

## Verdict: HOLD / no independent engine verdict

Read-only review of the requested late-reconnect transition. I did not edit tracked fixtures or runner, and made no admission claim. Installed Godot reports `4.7.2.stable.arch_linux.ed1daf0bf`.

I created isolated scratch under `corpus/live/r48-late-reconnect-critic/`. The initial invocation was malformed: it attached a `SceneTree` script to a Node scene; Godot reported native type mismatch and shell termination (143). This is adverse telemetry only. One bounded retry in unique `retry/` scratch did not yield a verdict. The retry script itself had incorrect connection-state expectations and timed out (124) at assertions; therefore it is not evidence for or against the proposed Godot behavior. I stopped rather than infer a measurement from a defective harness. Raw scratch and logs remain in my unique area.

## Read-only transition critique

The intended checks must make the edge-7 sequence explicit: owner slider before `ui_left` press; while callback is still disconnected; after the frame assert numeric 4, receipts exactly `[6]`, Label exactly `Value 6`, and callback still disconnected; only then reconnect and assert connected. Edge 8 release must have slider owner, connected callback, numeric 4, receipts `[6]`, Label `Value 6`. The same owner-before and numeric/receipts/Label-after-frame checks are needed on all nine edges. Edge 0 must verify connected before action and value 6/receipt `[6]`/Label `Value 6` before disconnect; immediately verify disconnected. The explicit connection vector *before each edge* is `[true,false,false,false,false,false,false,false,true]`; after edge0 it becomes false, and after edge7 reconnect it becomes true. A unique terminal expected-negative marker/exit 2 must be emitted only after all nine checks; no early marker may be mistaken for the terminal classification.

Potential timing pitfall: reconnection must occur after the edge-7 post-frame state assertions, not before the press, before the frame, or merely after numeric change without asserting retained label/receipt state. A branch condition should require both `--repeat-right` and `--second-focus-restore`, with exact distinct flag `--reconnect-after-final-left`; retain r44–r47 cases/rows as additions only. Signal reconnection cannot replay the already missed edge-7 emission; the edge-8 release should not create a new receipt because numeric value does not change. This causal expectation is plausible but **not measured in my scratch**.

No tracked edits, battery run, commit, or scope beyond synthetic parsed events+frames. This does not establish behavior for OS repeat, physical input/timing, rendered/pointer UI, accessibility, production, or generic signal replay.
