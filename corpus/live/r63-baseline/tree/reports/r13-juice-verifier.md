# Round 13 juice verifier — independent LEAF

## Scope and independence

Named non-author verifier; no delegation, source edits, commit, or push. Read Round 13 mission in `.shokunin/game-dev-2d/LOG.md` and the r13 scout, executor, and critic reports. Independently ran the requested combined battery and separate fault-injection mode; inspected raw verdicts and the seeded Tween fixture. The combined run is `.shokunin/game-dev-2d/corpus/live/runs/20261012T181811533203Z/`; fault injection is `.../runs/20261012T181836047504Z/`.

## Replay and raw evidence

- `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error` → exit 0, **37/37 PASS**. This retains all 31 ordinary cases (the 29 pre-round cases plus the Tween pair), along with the opt-in diagnostic, export-launch, and Godot-error probes. Export-launch and Godot-error probe artifacts also say PASS.
- `tween_flash`: Godot 4.7.2, exit 0. Raw output reports `transient_modulate=(0.7041, 0.7918, 0.8891, 1.0)`, baseline `(0.7, 0.8, 0.9, 1.0)`, `frames_observed=62`. In the fixture, actual `target.modulate` snapshots are sampled after process-frame yields; a non-baseline snapshot is observed, then a later baseline snapshot, within `MAX_OBSERVATION_FRAMES := 90`.
- `tween_no_start`: exit 2, exactly the intended `TWEEN ASSERTION FAILED` line with `transient_seen=false`, `baseline_restored=false`, `frames_observed=90`, final modulate equal to baseline. It emits the expected push_error/backtrace only. No setup error, parse error, extra error, warning, or leak warning appeared in either Tween case's raw output.
- Separately, `--fault-injection` → exit 0, meta verdict PASS. Raw cases behave as intended: hang times out and fails its inner check; clean expected negative passes; appended unrelated error fails its inner check. These are fault-harness controls, not new game cases.

## Adversarial counterfactual

Copied fixtures to `/tmp/r13-verifier-mutant-y7pxb8l9`, changed only that scratch copy of `tween_flash.gd` to force `skip_start := true`, then ran its `--probe-failing` battery. Exit 1: positive `tween_flash` fails with exit 2 instead of expected exit 0/signature; paired `tween_no_start` still passes its expected negative assertion. Existing cases also show unrelated export failures in that first attempt because the copy omitted an export preset. Repeated after correcting the scratch copy to include all fixture files (including `export_presets.cfg`): same intended Tween positive failure, Tween negative expected pass, all other ordinary cases pass; total battery still fails because positive Tween failed. Scratch mutation/copy removed afterward. This demonstrates the paired assertion detects disabled Tween start, without modifying the actual fixture.

## Integrity and verdict

SHA-256 before and after replay of tracked fixture/runner inputs was unchanged:
- `corpus/fixtures/run_battery.py`: `ecbdf9b0d712490beb29ab1ea5411c964c4a644e7599dd16f744dd5bd37db9bc`
- `corpus/fixtures/tween_flash.gd`: `e37bd03dd8801ba2379a1275edd3b9cab0b2767cf310ebb8c92a31892ebbdd81`

- **Coverage: RELEASE, narrowly.** Distinct headless Tween-driven `CanvasItem.modulate` transient-and-return behavior and same-assertion no-start control are supported; prior 29 ordinary cases remain and total ordinary cases are 31.
- **Calibration: RELEASE, narrowly.** Intended no-start exit/signature and its sole expected assertion diagnostic are accepted, while parse/setup errors remain disallowed; raw paired outputs were clean. This is not universal diagnostic handling.
- **Depth: HOLD / unchanged.** No claim of additional causal depth or broad runtime integration.
- **No harmed axis observed.**

Limits: this proves sampled headless property state only—not rendered brightness, perceived flash, visual quality, production integration, or platform-wide timing. The 90-frame cap is specific to this fixture/runtime. No constants or seeded source files changed by verifier.
