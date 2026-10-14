# Round 15 — headless health-to-gauge value and receipt

Reproduce on Godot 4.7.2: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-audio-warning` → named non-author verifier **40/40 PASS** (33 ordinary plus seven opt-in meta records), raw `r15-gauge-verifier.json`; `--fault-injection` meta PASS in `r15-fault-regression.json`. Verifier report `.shokunin/game-dev-2d/reports/r15-gauge-verifier.md`.

| Actual runtime fixture path | Observation | Bound |
|---|---|---|
| Attach `TextureProgressBar` under in-tree CanvasLayer, range 0..100, initial value 100; connect `value_changed` after setup, health signal handler sets `gauge.value`; emit health 35 | exit 0; `gauge.value=35`, exactly one `value_changed(35)` receipt, in-tree/range metadata checked | Headless Control state and signal only. |
| Same fixture, `--disconnect-signal` skips only health handler connection | exit 2 at same assertion; actual gauge remains 100, receipt count 0 and sentinel -1; no setup/parse/extra error | Valid negative, not an unset/invalid gauge. |
| Verifier scratch-copy removes health connection | positive fails default battery, negative still fails its same assertion | Counterfactual shows baseline cannot fake the positive. |

Critic's first scratch replay found the disconnected case was not yet allowed by the narrow ERROR classifier; executor added its exact expected diagnostic and reran 33/33 author cases. Scout's separate scratch clamp checks (out-of-range -10 and 140) are **not** part of the admitted fixture: only range metadata and in-range update were verified. This extends r3's Label text signal to one `TextureProgressBar` value and actual `value_changed` receipt, not production health/game integration. No rendered gauge fill, clamping, pixels, UX, or asset claims. Tracked fixture digests unchanged during independent verifier replay.
