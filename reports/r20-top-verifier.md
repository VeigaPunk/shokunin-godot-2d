# Round 20 — named non-author top-limit verifier

Independent replay from tracked raw fixtures/runner; no authoring edits made. Command:

```sh
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution
```

It used the runner default absolute runs path and exited 0 in 27.99s. Run: `.shokunin/game-dev-2d/corpus/live/runs/20261013T005523747164Z/`. Raw battery verdict JSON is preserved byte-for-byte at `corpus/lessons/r20-top-verifier.json`; associated opt-in raw files are `export-launch-verdicts.json`, `godot-error-verdicts.json`, and `stream-attribution-verdicts.json` in that run directory.

**Result: 44/44 PASS** — 35 ordinary records (33 baseline + 2 top-bound records), 2 mutation records, 7 opt-in records. The JSON top-level verdict is PASS and every record verdict is PASS. Expected negative arms print `FAIL`/`ERROR` labels as inner test data; those are not outer battery failures.

The new positive `camera_top_limit` exits 0. An independent scratch-only instrumented copy reports active center `(0.00,-968.00)` and target `(0.00,-2000.00)` for authored top `-1000`, matching `top + viewport half-height` for 64px viewport. The far-top control exits 2 with observed center and target both `(0.00,-2000.00)`, then the intended `camera limit assertion failed: expected active center within top boundary and distinct from target`; no setup-error signature. Control evidence is in the raw JSON.

Top-limit sensitivity: disposable scratch copy changed only `camera.limit_top = -1000` to `-100000`; invocation `godot --headless --path <run>/scratch --script res://camera_limit_sabotage.gd -- --top-bound` exited 2 with center `-2000`, expected clamp `-968`, and the same intended assertion. This was not a seeded or tracked fixture edit.

Both previous right cases (`camera_limit`, `camera_far_bound`) remain PASS, with expected positive and intentional assertion failure respectively. All first 33 ordinary rows PASS. Export readiness and export-launch positive/control both succeeded (both launches exit 0; control intentionally lacks expected startup event). Godot diagnostic expected-negative classifies true and unrelated diagnostic false; stream accept true and unrelated-stderr reject false, both stream arms exit 0. These inner false classifications are expected; there are no outer verifier failures.

Tracked fixture integrity: `camera_limit.gd` SHA-256 `c3953ce103ed382ef288adb306b7783672181e7555457f62721f1b648bfefd79`; `run_battery.py` SHA-256 `ff5015734c22604b3cf5778b7ae4fcb3b452ebeb70cb687c2e4e0747b21513d1`, unchanged before/after replay. Seed fixtures are runner-copied into scratch. The disposable sabotage and measurement scripts were placed only in that run's scratch directory. No source/editor mutation, tracked fixture/runner/LOG/scorecard change, commit, or push.

Verifier assessment: evidence supports the round's stated top-bound coverage claim and no regression observed in this finite battery. It does not establish rendered-pixel behavior, production camera coverage, other edges, or export reliability beyond these specific passes.
