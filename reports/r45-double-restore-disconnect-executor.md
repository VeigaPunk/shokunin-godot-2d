# Round 45 executor — double-restore disconnected signal consumer

## Evidence and result

- Read the standing brief and round-45 claim in `LOG.md` before action. Used a private copy at `corpus/live/r45-double-restore-disconnect-executor/scratch/` first; no engine/editor or seeded files were edited.
- Godot `4.7.2.stable.arch_linux.ed1daf0bf`. The scratch negative with `--repeat-right --second-focus-restore --disconnect-signal` completed all nine owner-before-event and value/receipts/Label-after-event checks, then exited **2**. Actual output: `SLIDER_DOUBLE_RESTORE_DISCONNECTED values=6,6,6,5,5,5,5,4,4 receipts=[] Label=Value 5`, followed by the expected terminal assertion. The connected r44 pair exited **0**, values `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, Labels `Value 6,Value 5,Value 4`.
- After scratch established the causal result, added a dedicated disconnected branch to `slider_adjust.gd`: the r44 nine-edge event/focus sequence is unchanged; the branch explicitly requires those nine values, empty receipts, and unchanged `Value 5` label at each edge. Its terminal expected-negative assertion occurs only after the loop. Kept the connected r44 branch unchanged.
- Added one exact expected-negative row and exact diagnostic classification to `run_battery.py`. Default battery: **59/59 PASS** (58 old ordinary rows plus new row); new row classified expected exit 2 with its exact signature. All existing rows were retained. `verdicts.json`: `corpus/live/r45-double-restore-disconnect-executor/battery-runs/20261013T074042686698Z/verdicts.json`.
- Ran the paired connected/disconnected cases directly against the edited in-tree fixture: connected exit 0 with `[6,5,4]`, disconnected exit 2 with actual `[]` / `Value 5` evidence. Scratch-first direct outputs are in the REPL transcript; scratch copy is retained above.

## Reviewer telemetry / disposition

An independent reviewer reported the old r44 disconnected arm could pass per-edge checks and still reach a hard-coded success terminal. That is valid adverse telemetry. The dedicated branch fixes the hole: it cannot return success and asserts the disconnected consumer state at every edge before the terminal exit 2. HOLD if replay or additional review finds any discrepancy; this report does not claim a non-author full verifier replay.

Scope remains synthetic parsed actions and frames only; not OS repeat, physical timing, rendering/pointer input, accessibility, production, or internal consumption of unchanged edges. No commit, push, or merge.
