# Round 26: controlled slow-clean versus marker-then-hold timeout

Sources: `corpus/fixtures/timeout_probe.gd`, `--probe-timeout` in `corpus/fixtures/run_battery.py`, named non-author raw `corpus/lessons/r26-timeout-verifier.json` and `r26-timeout-detail.json`, `reports/r26-timeout-verifier.md`.

| Same script/marker before delay | Timeout bound | Actual outcome | Classify |
|---|---:|---|---|
| `--delay-clean` prints marker, then waits 1.5s, exits 0 | old 0.75s | marker observed but timeout, actual_exit null, direct child reaped | false: old bound rejects valid delayed run |
| same `--delay-clean` | new 3.0s | marker observed, clean exit 0 in 1.972s | true: admits measured slow clean |
| `--hold-open` prints marker then waits 30s | new 3.0s | timeout, actual_exit null, direct child reaped | false: longer bound still rejects this hang |

Full named non-author replay 50/50 PASS (39 ordinary + 2 mutants + 9 opt-in), separate Python fault meta PASS with deliberate failing inner cases. Scratch reviewer variant delayed before marker, so its old-bound no-marker observation is NOT evidence for the stronger claim; only final tracked fixture raw shows marker present at old bound. A 3-second limit is justified by measured ~1.9s valid delay on this host; no universal or production startup reliability, arbitrary-freeze or process-tree cleanup claim. Constants: old 0.75s, new 3.0s, postmarker delay 1.5s, cleanup 3s.
