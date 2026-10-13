# Round 44 baseline reviewer — immutable r43 and direct scratch

## Baseline
- Confirmed `/usr/bin/godot --version`: `4.7.2.stable.arch_linux.ed1daf0bf`.
- Replayed the unchanged default battery with `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py` against r43 HEAD `c34b271` (no opt-in flags). Exit 0; the battery reports PASS for all rows, including expected-negative cases. It records 68/68 including two mutants, matching the stated r43 baseline. Existing slider focus-restore remains exit 0 and second-focus-loss remains expected exit 2; neither was modified.

## Independent scratch probe
- Copied the fixture project and slider script to `corpus/live/r44-second-restore-direct/`; added an isolated `--r44-second-restore` branch only in that scratch copy.
- Real Godot 4.7.2, connected in-tree HSlider min0/max10/step1 initial5; nine fresh parsed action edges, one frame each. Before every edge, asserted focus owner. After every edge asserted value, cumulative value_changed receipts, and Label.
- First seven actions preserve r43 sequence/expected values `6,6,6,5,5,5,5`, with Button ownership edges 1,2,5,6 and slider ownership edges 0,3,4. Slider is restored before edge7, then left press/release.
- Observed hypothesis exactly: values `6,6,6,5,5,5,5,4,4`; receipts `[6,5,4]`; final Label `Value 4`. Positive exit 0 after all nine checks.

## Review conclusion
Scratch evidence supports the proposed second-restoration claim. This is synthetic parsed actions plus frames only; it does not establish OS auto-repeat, physical timing, rendering/pointer behavior, accessibility, production behavior, or internal consumption of no-change edges. No tracked fixture, battery, engine/editor source, or seeded fixture was edited. No commit/push/merge.
