# Round 45 double-restore disconnect scribe — read-only admission checklist

## Declared claim and baseline

The append-only LOG declares one calibration claim: compare r44's nine-edge, double-focus-restoration sequence with only the `value_changed.connect(_on_value_changed)` callback disconnected via `--disconnect-signal`. Baseline is 58 ordinary / 69 full. Prediction: the same numeric history `6,6,6,5,5,5,5,4,4`, while receipts remain `[]` and Label remains `Value 5` after all nine edges; expected-negative exit 2 only after all nine checks. Connected r44 prediction is unchanged, final receipts `[6,5,4]`, Label `Value 4`.

## Real-engine scratch result — hypothesis confirmed; battery admission pending

Used an isolated copy of the in-tree fixture and project settings at `corpus/live/r45-double-restore-disconnect-scribe/`, Godot `4.7.2.stable.arch_linux.ed1daf0bf`. No tracked fixture/runner files were edited. First, the connected nine-edge path (`--repeat-right --second-focus-restore`) exited 0 with values `6,6,6,5,5,5,5,4,4`, receipts `6,5,4`, and expected labels, consistent with r44.

The existing disconnected branch was then run with `--disconnect-signal`. It exited 0 with a positive PASS line, but inspection showed its assertions were inadequate: it still checked connected numeric values and did not have a distinct expected-negative terminal. I initially tested the wrong scratch expectation (5.0 at disconnected edge 0); that failed with actual 6.0. This was an incorrect test expectation, **not** a falsification of LOG's stated same-numeric-history hypothesis.

Corrected only the isolated scratch copy: disconnected `edge_value` now remains `expected_values[i]`; after all nine per-edge owner/value/receipts/Label checks, it emits a distinct disconnected diagnostic and exits 2. Re-run observed exactly `6,6,6,5,5,5,5,4,4`, receipts `[]`, Label `Value 5`, and expected exit 2 after nine checks. This confirms the claimed control behavior in scratch. The earlier fixture's positive terminal was a real assertion/classifier gap; this scribe is read-only and did not repair tracked code. Executor/battery row integration and independent full verification remain pending; do not admit until those are reviewed.

Scratch commands:

```text
timeout 30s godot --headless --path .shokunin/game-dev-2d/corpus/live/r45-double-restore-disconnect-scribe --script res://slider_adjust.gd -- --repeat-right --second-focus-restore
exit 0; PASS ... values=6,6,6,5,5,5,5,4,4 receipts=6,5,4 ...

timeout 30s godot --headless --path .shokunin/game-dev-2d/corpus/live/r45-double-restore-disconnect-scribe --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --disconnect-signal
exit 2 after nine checks; SLIDER_REPEAT_SECOND_FOCUS_RESTORE_DISCONNECTED values=6,6,6,5,5,5,5,4,4 receipts=[] Label=Value 5
```

## Admission checklist — not met

- [x] Read LOG claim and the r44 connected verifier/scribe evidence.
- [x] Real Godot 4.7.2 isolated scratch; connected paired control succeeds.
- [x] Corrected disconnected scratch asserts the same numeric history, receipts/Label after every edge, and distinct expected-negative only after nine checks; observed predicted result. The old branch had inadequate terminal/positive assertion behavior.
- [x] Disconnected values match `6,6,6,5,5,5,5,4,4`, with empty receipts and Value 5; observed in corrected scratch.
- [x] Nine disconnected per-edge checks, then distinct expected terminal exit 2; observed.
- [ ] Causal basis to edit `slider_adjust.gd` / `run_battery.py`, add one row, or claim calibration improvement; absent. No tracked edits made.
- [ ] Named non-author full verifier, prior-row comparison, or admission; not applicable before causal scratch succeeds.

Verdict: **Scratch supports the declared calibration hypothesis; HOLD admission pending tracked executor integration and named independent full replay.** This observation is limited to Godot's synthetic parsed action events and frames in the fixture. It says nothing about OS repeat, physical keyboard/timing, rendered/pointer UI, accessibility, production, or generic HSlider behavior. No engine/editor or seeded corpus changes; no commit/push/merge.
