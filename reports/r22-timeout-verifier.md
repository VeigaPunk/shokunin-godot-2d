# Round 22 timeout verifier — independent replay

## Result

The named non-author replay completed on Linux with Godot `4.7.2.stable.arch_linux.ed1daf0bf`. The full default-path command was:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit code 0; **46/46 PASS** (35 ordinary, 2 mutants, 9 opt-in records). All **45 prior records** remain present and PASS; the only added record is `probe_timeout`. The source overall verdict JSON was copied byte-for-byte to `corpus/lessons/r22-timeout-verifier.json`; the detailed probe JSON is `corpus/lessons/r22-timeout-detail.json`.

## Timeout contrast

Both arms use `res://timeout_probe.gd` and marker `TIMEOUT_PROBE: expected signature`.

- Accept: marker observed, exit 0, no error, classifier `true`.
- Reject: same marker observed while the direct child was live; timeout at 0.75s; `actual_exit: null`; error exactly `TIMEOUT after 0.75 seconds`; classifier `false`. Cleanup reported `cleanup_exit_code: -9` and `direct_child_alive_after_cleanup: false`.

The critic's independent scratch timing measured a positive startup of 0.394s, leaving approximately **0.356s (about 0.35s) positive startup margin** under the 0.75s timeout. As noted in that review, load may cause a false negative/replay instability, not a false PASS. Claim remains limited to this direct child and this fixture; no descendant/process-tree or general freeze claim.

Separate `--fault-injection` run exited 0 and its raw JSON was preserved at `corpus/lessons/r22-fault-verifier.json` with top-level verdict PASS. Its expected adverse subcases are recorded honestly: `fault_hang` and `fault_unrelated_error` each have per-case FAIL, while the expected-negative diagnostic case is PASS; these do not get relabeled as individual PASS.

## Integrity

SHA256 hashes of all 254 tracked files were identical before and after both runs. No source or seeded control was edited. Only the three assigned lesson JSON files and this verifier report were written by this lane. No commit, push, or merge.
