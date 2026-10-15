# Round 38 named edge verifier — independent replay

## Scope and method
Non-author replay of tracked `corpus/fixtures/slider_adjust.gd` on Godot 4.7.2.stable.arch_linux.ed1daf0bf. Reviewed r38 LOG and scout/critic/executor reports. Executed the tracked fixture in isolated verifier scratch copies for connected, focused disconnected-signal, and no-focus arms. Each edge uses `Input.parse_input_event(InputEventAction)` followed by exactly one `process_frame` before assertion. Focus was checked before both action pairs. This is not rendered/pointer input, physical timing, auto-repeat behavior, accessibility, or production UI validation.

## Independent Godot results
- Focused connected: ui_right press `6`, receipts `[6]`, Label `Value 6`; release remains `6/[6]/Value 6`; ui_left press `5/[6,5]/Value 5`; release remains `5/[6,5]/Value 5`. Exit 0.
- Focused disconnected: values `6,6,5,5`, receipts `[]`, Label `Value 5`; intended negative signal diagnostic occurs after all four edge assertions. Exit 2.
- No-focus: values `5,5,5,5`, receipts `[]`, Label `Value 5`; intended negative focus diagnostic occurs after all four edges. Exit 2.
- The critic's caveat stands: transition is observed only after the frame; an extra repeated `pressed=true` can advance 6→7. No repeat-immunity claim is supported.

## Full DEFAULT-PATH battery
Ran exactly:
`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

Outer battery exit 0, raw verdict PASS, 62 entries (51 ordinary +2 mutants +9 opt-in groups). Raw source: `corpus/live/runs/20261013T061438379322Z/verdicts.json`; copied byte-for-byte to `corpus/lessons/r38-edge-verifier.json` (SHA-256 `c1c81ed4d469ec4bde4e7525f50cd41a9ba73168664c07d7de91cf2125c56c83`). Compared all 62 r37 named-verifier `(case, verdict, actual_exit, signature)` tuples with r38: exact match, no changed tuple and no new row. The unrelated-error and stream-reject probes contain deliberate inner FAIL classifications; their enclosing probe groups PASS, as expected.

## Fault injection and sabotage
Separate command `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection --runs .shokunin/game-dev-2d/corpus/live/r38-edge-verifier/fault` exited 0 with outer PASS. Raw copied byte-for-byte to `corpus/lessons/r38-fault-verifier.json`: deliberate `fault_hang` FAIL (timeout), clean expected-negative inner PASS, unrelated-error inner FAIL. This is the intended distinction between inner fault outcomes and outer probe success.

In an isolated sabotage copy, omitted only the `ui_right` pressed event while retaining its release and the left pair. Godot exited 2 specifically at `SLIDER edge assertion failed: ui_right press`; no false PASS. Scratch only.

## Integrity / verdict
Tracked fixture SHA-256 before and after: `093ae11de4e854ffb954ce5158133be2c3d5f890c8fef738990190a9bcfcd036`; runner SHA-256 before and after: `69d94dd63f0a32769731d7942b831a3d7e7ad84a5ce571153df2abe231a1914f`. No tracked source edits, commit, push, or merge by verifier. Raw lesson/report and scratch outputs are verifier-owned artifacts.

Independent evidence supports the bounded r38 per-edge assertion claim. No HOLD condition observed. Claim is limited to one synthetic action event followed by one process frame per edge, not rendered/pointer/physical timing/auto-repeat/accessibility/production behavior.
