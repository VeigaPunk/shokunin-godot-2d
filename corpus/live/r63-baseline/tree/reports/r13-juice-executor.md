# Round 13 juice executor report

## Implementation

Added `corpus/fixtures/tween_flash.gd` and added `tween_flash` / `tween_no_start` to `run_battery.py`'s ordinary cases. The fixture attaches a real `Node2D` to the headless `SceneTree`, records its initial `modulate` baseline, starts `target.create_tween()` unless `--no-tween`, and chains `CanvasItem.modulate` to a distinct flash color and back to baseline. It reads actual `target.modulate` snapshots each `process_frame`; success requires an observed non-baseline snapshot followed by a baseline snapshot. Prints snapshot values and observed frame count. No markers alone establish success.

- Baseline: `Color(0.7, 0.8, 0.9, 1.0)`; tween excursion: `Color(1.0, 0.2, 0.1, 1.0)`.
- Each tween leg: `0.2` seconds.
- Bounded observation: at most 90 `process_frame` yields; positive exits when baseline follows transient.
- Negative: `--no-tween` skips only the call that starts/configures the tween, retaining target construction, initialization, baseline read, frame loop, and exact same transient-then-return assertion. It reports transient/restored/frame/final property diagnostics in the expected failure.
- Negative classification expects exit 2 and the exact assertion prefix `ERROR: TWEEN ASSERTION FAILED: modulate did not show flash then return to baseline,` (comma-terminated allowance enables existing narrowly constrained prefix matching with exactly one `ERROR:` on that line); setup `SCRIPT ERROR:` and `Parse Error:` force failure via existing classifier. No broader `ERROR:` allowance was added.

## Raw author runs

- Initial `--probe-failing` run `corpus/live/runs/20261012T181339281989Z`: 30 existing/other cases passed, positive Tween reached exit 2 because 36 frames did not allow the transient-and-return to finish; no-tween correctly failed its assertion. This was an inadequate bound, not admitted evidence.
- Second run `corpus/live/runs/20261012T181420362576Z`: positive passed with larger bound; no-tween exited 2 at the intended assertion, but battery classifier did not accept the diagnostic due to its trailing diagnostic fields. This exposed a signature-matcher mismatch, not a fixture setup error.
- Final run command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → exit 0, `PASS battery`, 31/31. Raw verdicts: `corpus/live/runs/20261012T181549921811Z/verdicts.json` (latest replay; an earlier successful replay is `corpus/live/runs/20261012T181447567687Z/verdicts.json`).
  - Positive raw output: exit 0; `PASS tween_flash transient_modulate=(0.704, 0.7921, 0.8894, 1.0) baseline_modulate=(0.7, 0.8, 0.9, 1.0) frames_observed=62`.
  - No-tween raw output: exit 2; `ERROR: TWEEN ASSERTION FAILED: modulate did not show flash then return to baseline, transient_seen=false baseline_restored=false frames_observed=90 final_modulate=(0.7, 0.8, 0.9, 1.0)` followed only by Godot's expected `push_error` backtrace. No `SCRIPT ERROR`, `Parse Error`, setup error, or warning appeared. The expected negative doesn't rely on another print marker.
  - Existing controls and two `--probe-failing` mutants passed; all 31 records PASS.

A headless `CanvasItem.modulate` property excursion is state evidence only: this does not prove rendered brightness, visually perceived flash, or production integration. No setup-failure controls beyond existing parse/script-error exclusion were added. No delegation, commits, pushes, engine/editor or seeded edits.


## Critic follow-up

The critic correctly noted that a bare expected-error allowance would fail to match the state-appended assertion. The runner allowance is comma-terminated, so existing classifier logic matches only that prefix and requires exactly one `ERROR:` on the line. Replayed the complete command after this review: exit 0, 31/31 PASS. Latest no-start raw line has `transient_seen=false baseline_restored=false frames_observed=90 final_modulate=(0.7, 0.8, 0.9, 1.0)` and exits 2; this is accepted as the intended assertion, while setup parse/script errors remain excluded. Positive actual snapshot remains non-baseline then returns to baseline after 62 frames. No further edits were necessary.
