# Round 5 independent animation verifier report

Verifier: named non-author verifier (LEAF; no delegation, no fixture/log edits, no commit). I independently inspected the Round 5 declaration, fixture, runner, and scout/executor/critic reports, then reran the battery and performed a scratch-only track-removal falsification.

## Battery replay

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`

Result: exit 0; **23/23** case verdicts PASS. Raw output: `.shokunin/game-dev-2d/corpus/live/runs/20261012T164000590607Z/verdicts.json` (Godot 4.7.2). The preceding 21 cases all remain PASS; the run adds the two animation cases and retains the two existing opt-in mutation probes.

- `animation_property`: exit 0; output includes `PASS animation_property_changed=true started=true x=60.0`.
- `animation_stuck` (`--stuck`): exit 2; same x=60 property assertion, actual x=0.0. It emits only the intended `ERROR: ANIMATION ASSERTION FAILED: expected animated property x=60 after bounded advance, got 0.0` and associated assertion backtrace; no script/parse error or unrelated engine diagnostic. Runner records both as PASS under their expected signatures.

The positive fixture creates an in-memory `TYPE_VALUE` track at `.:position:x`, keys it at 0 and 120 over one second, verifies the starting x=0, starts playback, then synchronously advances 0.5 seconds and observes x=60. The stuck mode preserves that setup and assertion, setting `speed_scale=0` before the same bounded advance.

## Scratch-only falsification

In the battery's scratch copy only, I removed both `track_insert_key` calls from `animation_property.gd` and ran the same positive script without flags. It exited 2 with the exact intended property assertion (`expected animated property x=60 ... got 0.0`), no parse/script error and no unrelated diagnostic. I restored the scratch copy afterward. This falsifies the possibility that the positive passes without a functioning value track. No fixture source was changed.

## Integrity and verdict

SHA-256 hashes of all **34 tracked fixture paths** were captured immediately before and after the battery run; **zero changed**. The scratch-only falsification also left those tracked paths unchanged.

Round 5 coverage claim is independently reproduced for two synthetic, headless in-memory animation-property cases. Coverage: **improved** (0 to 2 cases demonstrated); depth: **unchanged**; calibration: **unchanged**. No harmed axis observed. Scope is limited to deterministic in-memory property-track advancement and detection of a stuck/trackless case. It does not prove rendered animation, visible smoothness, perceived juice, audio, or production integration.
