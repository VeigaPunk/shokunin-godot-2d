# Round 15 gauge executor

Implemented `corpus/fixtures/health_gauge.gd` and added positive/disconnected cases plus the case-owned expected diagnostic in `corpus/fixtures/run_battery.py`.

The fixture creates an in-tree `TextureProgressBar` at range 0..100 and value 100, then connects `value_changed` after initialization. The health signal updates the gauge to 35; the positive assertion verifies actual value 35, exactly one `value_changed` receipt, receipt value 35, and in-tree/range setup. `--disconnect-signal` skips only the health signal connection. Its same value/receipt assertion fails after setup; it prints actual value/count/receipt (`100.0`, `0`, `-1.0`) and emits the exact expected assertion diagnostic. The runner recognizes only that exact `ERROR:` line for this case. Range metadata is checked; no clamping claim is made.

## Author replay

Command: `python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot --probe-failing --runs .shokunin/game-dev-2d/corpus/live/runs`

Final raw result: `.shokunin/game-dev-2d/corpus/live/runs/20261012T183327080551Z/verdicts.json` (PASS, 33/33; ordinary plus two existing mutation probes). Gauge positive exit 0, disconnected exit 2 classified PASS. Captured negative output:

```text
HEALTH_GAUGE_NEGATIVE actual_value=100.0 value_changed_count=0 receipt=-1.0
ERROR: Health gauge assertion failed: expected in-tree TextureProgressBar value=35 value_changed=1 receipt=35
```

The first replay before adding the case-owned diagnostic allowance had gauge negative classified FAIL despite expected exit 2; added the narrow allowance and reran. A subsequent full `--probe-failing` run passed all 33 cases. No unexpected warning, parse error, script error, or extra ERROR was present in the final gauge outputs. Godot: 4.7.2. No clamp behavior, rendering, UX, or production integration is established.
