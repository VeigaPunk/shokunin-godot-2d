# Round 20: top Camera2D limit in headless Godot 4.7.2

Source: `corpus/fixtures/camera_limit.gd` and `run_battery.py`; named non-author replay `corpus/lessons/r20-top-verifier.json`, `reports/r20-top-verifier.md`.

| Setup | Observation | Decision |
|---|---|---|
| Current Camera2D, target `(0,-2000)`, `limit_top=-1000`, 64px viewport | active screen center y=-968 (`-1000 + 64/2`) | Accept top-clamp positive only if center reaches viewport-adjusted bound, moved, and differs from target. |
| Same target/assertion, `limit_top=-100000` | center y=-2000, exit 2 with intended top-bound assertion | Accept causal negative; reject setup failure as evidence. |
| Disposable scratch authored-limit sabotage `-1000 → -100000` | top positive fails the same assertion | Shows the positive detects a missing effective limit. |

Verifier default-path battery exited 0, 44/44 PASS (35 ordinary, 2 mutation, 7 opt-in), including pre-existing right-edge cases. This checks headless center state only. It does not show rendered pixels, production cameras, other edges, or export reliability. Parent's explicit relative `--runs` pre-change export diagnostic raised `StopIteration` searching for `savepack`; the default-path replays did not resolve that adverse case. Constants: authored top -1000, far top -100000, target y -2000, dynamic viewport half-height (observed 32), epsilon 0.01.
