# Round 21 baseline scout

Read-only baseline at HEAD `8c9a20b17cf745381f9efde445e4545e87e8e8f0`. No fixture, runner, seeded corpus, or engine/editor files were changed.

- Runner AST contains 35 ordinary `CASES` entries (includes export readiness/missing-preset cases); Round 20 LOG records 35 ordinary emitted rows.
- HEAD Round 20 verifier artifact `corpus/lessons/r20-top-verifier.json`: 44 rows; Counter({'PASS': 44}). The LOG attributes these to 35 ordinary + 2 mutants + 7 opt-in probes, all PASS.
- Tracked hashes at HEAD:
  - `corpus/fixtures/run_battery.py`: `ff5015734c22604b3cf5778b7ae4fcb3b452ebeb70cb687c2e4e0747b21513d1`
  - `corpus/fixtures/camera_limit.gd`: `c3953ce103ed382ef288adb306b7783672181e7555457f62721f1b648bfefd79`
  - `corpus/fixtures/stream_attribution_probe.gd`: `97143ad367a66e5f625208947c4d479a48d1aa7ce519d0e2de13b4751d288ebe`
- HEAD is `8c9a20b17cf745381f9efde445e4545e87e8e8f0`. Working tree had parent LOG modification and untracked R20 scratch directories before this report; outside this scout's scope.

The 35 ordinary emitted-row baseline is consistent with the recorded Round 20 result. I did not run Godot or alter corpus controls.
