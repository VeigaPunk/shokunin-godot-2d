# Round 21: normal Godot exit versus direct-child SIGTERM

Sources: `corpus/fixtures/crash_exit_probe.gd`, opt-in `--probe-crash-exit` in `corpus/fixtures/run_battery.py`, named independent replay `corpus/lessons/r21-crash-verifier.json`, detailed paired raw `corpus/lessons/r21-crash-detail.json`, `reports/r21-crash-verifier.md`.

| Same script and emitted marker | Process state | Python return | Verdict |
|---|---|---:|---|
| Normal `quit(1)` | completed normally | 1 | Accept expected nonzero exit; `classify_process` true. |
| `--hold-open`, marker observed while live; parent sends SIGTERM | direct child signaled | -15 | Reject despite marker; `classify_process` false. |

The meta probe requires same script/marker/expected exit, live observation before sending SIGTERM, correct negative return code, no probe error, and bounds on marker wait (8 seconds) and cleanup (3 seconds). Verifier full default-path run was 45/45 PASS (35 ordinary + 2 mutants + 8 opt-in) and separate Python fault injection meta PASS. No separate sabotage of signal guard was run. This is a Linux Godot 4.7.2 direct-child signal contrast, not spontaneous crash, process-tree timeout, other platforms, or export reliability. Earlier explicit relative `--runs` export `StopIteration` remains adverse unresolved evidence.
