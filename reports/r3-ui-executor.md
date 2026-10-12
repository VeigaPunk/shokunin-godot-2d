# Round 3 UI executor result

Implemented one new fixture, `corpus/fixtures/ui_signal_hud.gd`, and added two cases to `corpus/fixtures/run_battery.py`.

The positive case creates a `CanvasLayer` with a child `Label`, waits one frame, checks the label is in-tree with `Score: 0`, records that the signal is connected, emits score 7, and asserts the in-tree label changes to `Score: 7`. The disconnected control uses the same fixture and same post-emission assertion; it omits only the connection. It exits 2 with the expected signature `UI assertion failed: expected in-tree HUD text=Score: 7`.

Replay: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` exited 0. All 19 listed cases passed (the original 17 plus 2 UI cases), and the existing broken-scene mutant was detected. Raw verdicts: `.shokunin/game-dev-2d/corpus/live/runs/20261012T162158951296Z/verdicts.json`.

Scope is limited: this checks headless CanvasLayer/Label lifecycle and signal-driven text state, not rendered pixels or visual layout. Only the new `ui_signal_hud.gd`, `run_battery.py`, and this report were written by this executor; no engine/source or seeded fixture was changed.
