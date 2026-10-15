# Round 2 — camera-center headless check

Reproduce: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` (Godot 4.7.2). The committed independent replay is `r2-camera-verifier.json`; named verifier: `r2-camera-verifier`, report `../../reports/r2-camera-verifier.md` (repository path `.shokunin/game-dev-2d/reports/r2-camera-verifier.md`).

| Observation | Classification | Boundary |
|---|---|---|
| Camera2D parented to target; target displaced from origin to (120, -53); after a frame, `get_screen_center_position()` moves >100 and matches target within 0.01 | headless camera-center follow PASS | `corpus/fixtures/camera_follow.gd`; API result, not rendered pixels |
| Same script with `--no-follow`, camera detached; same movement and assertion exits 2 with `camera follow assertion failed` | intended no-follow control detected | absent tracking relation, not engine crash |
| Removing `make_current()` in verifier scratch still prints PASS | limitation | `is_current()` does not establish rendered viewport selection in this setup; do not claim visual framing |
| Disabling camera before `make_current()` produces Godot setup ERROR | invalid control | not evidence of a clean tracking defect |

The runner's signature/exit check does not reject every unrelated `ERROR:` string, though this independent run's positive output has none and the no-follow output has only the intended assertion. Counts are case-detection measurements, not quality scores. This fixture does not establish smoothing, limits, zoom, viewport rendering, visual framing, or other Godot versions. Existing 30 tracked fixture files were hash-checked unchanged by the verifier.
