# Round 5 — deterministic animation-property advance

Reproduce: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` on Godot 4.7.2. Named non-author verifier `r5-anim-verifier`, report `.shokunin/game-dev-2d/reports/r5-anim-verifier.md`, committed independent 23/23 raw result `r5-animation-verifier.json`.

| Observation | Classification | Limit |
|---|---|---|
| AnimationPlayer TYPE_VALUE `.:position:x` track, keys x=0 at t=0 and x=120 at t=1, starts at x=0; synchronous `advance(0.5)` yields x=60 | headless property animation PASS | no rendered frames, smoothness or production juice |
| Same script `--stuck` still calls play but sets speed_scale=0; x stays 0 and same x=60 assertion exits 2 | stalled animation detected | one in-memory track, no visual animation quality |
| Verifier removed both track keys in scratch only; positive exits 2 at same assertion | track dependence demonstrated | not proof of production scene wiring |

Verifier SHA-256-checked 34 tracked fixture files unchanged. Engine error/timeout is never evidence of animation progress; current positive output is clean, stuck error is the intended assertion.
