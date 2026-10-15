# Round 2 camera coverage — independent verifier (LEAF)

## Result

I independently ran, after the camera setup correction:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing
```

Exit 0. Raw verdicts: `.shokunin/game-dev-2d/corpus/live/runs/20261012T161706486809Z/verdicts.json`; overall `PASS`, **17/17**. The 14 round-1 cases are byte-for-byte the same case definitions as at `HEAD`, and all 14 pass in this run. The camera positive exits 0 with `PASS camera_follow moved=true current=true center_matches_target=true`; its output has no Godot `ERROR`, script/parse error, launch error, or timeout. The no-follow invocation runs the same script with `--no-follow`, exits 2, and emits only the expected assertion `ERROR: camera follow assertion failed: target moved but active center did not track`; no timeout or unrelated diagnostic. The opt-in broken-scene route mutant exits 2 with `chain incomplete`, as intended.

The fixture makes the target move from its initial origin to `(120, -53)` (>100 units), calls `make_current()` after adding the enabled camera to the tree, waits a frame, records the screen-center baseline, moves the target, waits another frame and forces scroll update. It then requires the target displacement, current camera, center within `0.01` of target, and center displacement >100. The control is the same probe and assertion, with the camera detached from the target; it fails with the intended tracked-center assertion. The runner and probe outputs agree with those conditions.

I calculated SHA-256 hashes for all **30 fixture paths tracked at `HEAD`** immediately before and after the battery; none changed. (The new camera probe is untracked at `HEAD`, so this check specifically certifies the preexisting seeded corpus.)

## Adversarial falsification / limitations

- Removing the `camera.make_current()` call from a temporary scratch copy still printed PASS. The probe's `camera.is_current()` and `get_screen_center_position()` are methods on the camera under test, and this headless test did not prove that a rendered viewport actually uses that camera. Treating this as screen-space/rendered tracking would overstate the evidence. The positive does prove Camera2D's effective screen-center API follows the moved target under this tree setup, but not visual framing or pixels.
- I also tried disabling the camera in the scratch copy while leaving `make_current()` in place. Godot emitted `Condition "!enabled || !is_inside_tree()" is true` at `make_current`, then the intended assertion failure. This is **not** a clean behavior-only falsification because the setup itself is invalid and emits an unrelated engine diagnostic; I restored the scratch copy afterward. A no-current variant likewise passed as above. The successful detached control remains useful evidence that the script's center assertion distinguishes this detached hierarchy, but it does not independently establish active viewport rendering.
- The runner's verdict logic is exit code plus output substring; for ordinary cases it only rejects `SCRIPT ERROR:` and `Parse Error:`. The no-follow case is not subject to the `mutate=True` path that recognizes only the broken-scene mutant. Current raw camera outputs are clean except the explicitly expected `push_error`, but the harness is not robust against a forged signature or every possible unrelated `ERROR:` line. The positive script's `0.01` tolerance and one-frame settle are validated on Godot 4.7.2 headless here, not across smoothing, limits, zoom, other engine versions, or rendered viewports.

## Verdict

Coverage evidence for the declared headless camera-center behavior is reproduced: **17/17**, with a positive target-follow observation and same-script detached no-follow control exiting 2 for the intended assertion. No preexisting tracked fixture changed. Limit the claim to headless `Camera2D.get_screen_center_position()` behavior; this run does not prove rendered viewport tracking, and the no-current falsification exposes that boundary.
