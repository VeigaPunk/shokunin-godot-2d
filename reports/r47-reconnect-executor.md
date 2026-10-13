# Round 47 reconnect executor — fresh ordinary battery

The causal Godot 4.7.2 scratch was run first in `corpus/live/r47-reconnect-executor/scratch` before tracked edits. It passed with state history `6,6,6,5,5,5,5,4,4`, receipts `[6,4]`, Labels `Value 6` through edge 6 then `Value 4`, and explicit signal connection-state checks after disconnect (edge 0) and after reconnect (edge 3).

After restoring the exact r46 `--disconnect-after-first` branch and row and adding r47 as separate entries, I ran a fresh ordinary default-path battery:

- Command: `python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --runs .shokunin/game-dev-2d/corpus/live/r47-reconnect-executor/battery-runs`
- Result: `PASS`, 61/61 cases PASS.
- Raw verdict: `.shokunin/game-dev-2d/corpus/live/r47-reconnect-executor/battery-runs/20261013T080520437508Z/verdicts.json`
- All 60 baseline cases in HEAD remain byte-for-byte identical runner tuples and appeared in this run; the one added case is `slider_adjust_repeat_right_second_focus_restore_reconnect_after_first_left`.
- r46 control remains independently present: `--disconnect-after-first`, expected exit 2 with `SLIDER MID-DISCONNECT ASSERTION FAILED...` after its nine-edge assertions.
- No full/fault verdict, commit, push, or merge is claimed.

## Adverse telemetry
A temporary edit initially replaced rather than added the r46 branch and runner row. During that temporary state I ran one battery invocation; it reported `battery 1/1` and displayed 61 cases, but r46's case was absent and the output is **not a valid baseline or PASS**. I immediately restored the exact r46 branch/row and added r47 separately. This temporary overwrite and tainted run are retained here as adverse telemetry, not erased or counted as evidence.
