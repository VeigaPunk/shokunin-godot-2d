# Round 3 — synthetic UI signal-to-Label check

Reproduce: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` with Godot 4.7.2. Named non-author verifier `r3-ui-verifier` independently replayed 19/19 in `r3-ui-verifier.json`; report `.shokunin/game-dev-2d/reports/r3-ui-verifier.md`.

| Observation | Classification | Limit |
|---|---|---|
| In-tree CanvasLayer/Label starts `Score: 0`, locally declared signal emits 7, callback sets `Label.text` to `Score: 7` | headless property update PASS | synthetic test wiring, not production HUD or pixels (`corpus/fixtures/ui_signal_hud.gd`) |
| Same script `--disconnect-signal` omits connect and fails the same post-emit assertion, exit 2 | missing connection detected | no asynchronous ordering or rendering evidence |
| Verifier's scratch-only wrong-callback mutation writes `Wrong: 7` and also fails same assertion | assertion sensitivity demonstrated | runner signatures alone can be spoofed; the current script actually asserts |

The first 17 prior cases retained PASS; verifier compared SHA-256 hashes for 31 tracked fixture paths before and after. No asset, rendered visibility, theme, layout, pixel, or real project scene conclusion follows from a headless `Label.text` check.
