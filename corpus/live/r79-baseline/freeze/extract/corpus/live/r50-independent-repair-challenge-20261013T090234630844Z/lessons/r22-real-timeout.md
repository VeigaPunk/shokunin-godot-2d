# Round 22: a real Godot timeout despite a success marker

Sources: `corpus/fixtures/timeout_probe.gd`, `--probe-timeout` in `corpus/fixtures/run_battery.py`, named non-author `corpus/lessons/r22-timeout-verifier.json` and `r22-timeout-detail.json`, `reports/r22-timeout-verifier.md`.

| Same script/marker | Outcome | Classification |
|---|---|---|
| Normal mode prints `TIMEOUT_PROBE: expected signature`, calls `quit(0)` | rc 0, no error | true (accept). |
| `--hold-open` prints marker, still running at 0.75s deadline | `actual_exit=null`, `TIMEOUT after 0.75 seconds`, direct child killed/reaped (-9), no child live | false (reject even with marker). |

Non-author full default-path replay: 46/46 PASS (35 ordinary, 2 mutants, 9 opt-in); separate Python fault meta PASS with its intentionally failing inner hang/unrelated subcases preserved. Critic measured a 0.394s normal startup, leaving only ~0.356s margin at this host/load: a slow start can false-fail; no stability claim. Controlled detached descendant survived timeout in cleanup reviewer scratch, so there is explicitly no process-tree cleanup claim. This is not a general freeze detector, cross-platform proof, or export-reliability result. Prior r16/r20 export adverse observations remain unresolved.
