# Round 48 late-reconnect scribe — read-only evidence/admission checklist

## Scratch measurement (Godot 4.7.2)

Own bounded scratch: `.shokunin/game-dev-2d/corpus/live/r48-late-reconnect-scribe/godot-scratch/` (`scratch.gd`, `run2.log`, `exit2`). Command: `godot --headless --path <own-scratch> --script scratch.gd`; exit 0. Fresh in-tree HSlider min=0, max=10, step=1, initial=5; same Label/value_changed consumer; connected at initialization; Button focus target; nine fresh parsed `InputEventAction` edges, one process frame each. No fixture, runner, seeded, engine, or editor edits.

Observed edge receipt (numeric value / cumulative receipts / Label / callback connection after the edge):

| Edge | Action | Focus owner before | Value | Receipts | Label | Connected after |
|---:|---|---|---:|---|---|---|
| 0 | ui_right press | slider | 6 | [6] | Value 6 | no (disconnected after checks) |
| 1 | ui_right press | Button | 6 | [6] | Value 6 | no |
| 2 | ui_right release | Button | 6 | [6] | Value 6 | no |
| 3 | ui_left press | slider | 5 | [6] | Value 6 | no |
| 4 | ui_left release | slider | 5 | [6] | Value 6 | no |
| 5 | ui_left press | Button | 5 | [6] | Value 6 | no |
| 6 | ui_left release | Button | 5 | [6] | Value 6 | no |
| 7 | ui_left press | slider | 4 | [6] | Value 6 | yes (reconnected after checks) |
| 8 | ui_left release | slider | 4 | [6] | Value 6 | yes |

The connection state was checked true before edge0, false after disconnect and before/through edge7's numeric transition, true immediately after reconnect following edge7's numeric/receipt/Label checks, and true before/after edge8. Scratch asserts owner before every event and numeric/receipts/Label after every frame. This directly supports the declared timing and outcome: reconnecting does not replay the prior edge7 `value_changed`; edge8 release does not add a receipt or alter the Label. Scope is only these synthetic parsed events and frames in Godot 4.7.2.

## Baseline and admission checklist

Immutable candidate baseline is HEAD `411891efa015f1ba8bbde196ca723b5fae3206db` (r47); raw baseline `corpus/lessons/r47-reconnect-verifier.json` reports 72/72 PASS = 61 ordinary + 2 mutants + 9 opt-ins. The 63 tuple-bearing rows include the two mutants (61 ordinary + 2 mutants). Existing r47 slider branches include callback connected, disconnected at start, disconnect-after-edge0, and reconnect-after-edge3. Preserve each exact branch/row/signature. Round 48 should add **one** negative ordinary tuple row only, gated by `--repeat-right --second-focus-restore --reconnect-after-final-left`, with one unique terminal expected-negative diagnostic and expected exit 2 reached only after nine assertions. Do not overwrite r47 or earlier branches/rows. Proposed total if implementation and named verifier pass: 62 ordinary + 2 mutants + 9 opt-ins = 73 full results; prior 63 tuple-bearing result triples unchanged.

Before admission require:
- Candidate `--reconnect-after-final-left` is distinct and allowed only with both required flags.
- Same exact r44 nine events and focus owners: slider/Button/Button/slider/slider/Button/Button/slider/slider.
- Connected at initialization; assert true before edge0; disconnect only after edge0 verifies 6 / `[6]` / `Value 6`.
- Remains disconnected through edge7. After edge7 verify numeric4 / `[6]` / `Value 6`, then reconnect and assert connection true before edge8 release.
- After every edge assert numeric `6,6,6,5,5,5,5,4,4`, cumulative receipts `[6]` and Label `Value 6`; owner assertion precedes each action.
- Connected remains true after edge8; no retroactive receipt or Label update.
- Unique terminal negative diagnostic occurs after all nine edge checks, exit 2; runner classifier requires that exact intended terminal, not a broad substring or earlier observation marker.
- Preserve r44–r47 source branches/rows exactly; additive-only; no edits outside executor-authorized fixture/runner and own report/scratch.
- Named non-author full default-path replay and separate fault-injection replay; compare prior 63 tuple-bearing triples (61 ordinary + 2 mutants) and nine opt-in classifications; hash fixture/runner before and after verification; retain raw JSON and report.

## Evidence caveats / verdict proposal

The first scratch attempt had an incorrect scratch-only connection expectation on edge8 (it expected disconnected after the prescribed edge7 reconnect) and failed exit2 at setup before edge8. It is retained as adverse scratch telemetry; corrected scratch changed only that expectation and passed all nine assertions. Do not count the first attempt as candidate evidence. No tracked project file changed.

If implementation and required named replay corroborate this measurement: calibration improved; depth and coverage unchanged as axes; no harm observed in finite replay. Keep scope bounded: no physical keyboard/timing, OS auto-repeat, rendered/pointer UI, accessibility, production/generic-slider guarantee, arbitrary signal replay, or proof about internal consumption of no-change edges.
