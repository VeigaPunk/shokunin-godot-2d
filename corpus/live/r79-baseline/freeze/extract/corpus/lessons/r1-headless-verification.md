# Round 1 — serial headless verification for 2D scene flow

## Decision table

| Evidence observed | Classification | Next action |
|---|---|---|
| exit 0 and matching `PASS` signature for a positive | PASS | retain full stdout/stderr and scratch path in verdict JSON |
| exit 1 and matching negative-control signature | PASS as a *negative control*, not a positive result | verify the named absent event or wrong input, never exit code alone |
| exit 2 and `chain incomplete` only for the deliberately broken scene-B marker | detected mutant | require the unmutated causal fixture to pass in the same run |
| timeout, wrong exit, absent signature, `SCRIPT ERROR:` / `Parse Error:` | FAIL | inspect `error` and `output`, then repair only scratch preparation or record a seeded defect |

Sources: `corpus/fixtures/controls/input_route_negative.gd:25-36` (disabled receiver exits 1 after zero receipts), `corpus/fixtures/causal_chain.gd:211-220` (scene-B marker check and `chain incomplete`), `corpus/fixtures/run_battery.py` (`CASES`, `execute`). Godot run evidence: `corpus/lessons/r1-initial.json` and `r1-passing.json` (`results[]`).

## Error-pattern table from the first real run

| Pattern / observed fixture | Cause | Response, proven by second run |
|---|---|---|
| `Cannot open file 'res://pickup.tscn'` on scene-signal controls | seed stores `controls/pickup.tscn` but control loads it from project root | copy scene into scratch root; do not change seed (`controls/test_scene_signal.gd:6`, `controls/pickup.tscn:3`) |
| `Cannot call method 'get_instance_id' on a null value` at `causal_chain.gd:44` | `current_scene` not ready after one process frame on this host | add one frame wait in scratch copy only; seed remains unchanged (`causal_chain.gd:37-43`) |
| `chain incomplete collections=1 scene=SceneB` with exit 2 in mutant | marker was replaced from B to BROKEN in scratch `scene_b.tscn` | classify as detected *only* when positive baseline passes and exact diagnostic appears (`scene_b.tscn:7`, `causal_chain.gd:211-220`) |

The first run failed 7/15 cases; the repaired scratch preparation passed 15/15, including the injected failure, under Godot 4.7.2. Counts: `python -c 'import json; from pathlib import Path; p=Path(".shokunin/game-dev-2d/corpus/lessons"); print(*[(f.name, sum(r["verdict"]=="PASS" for r in json.loads(f.read_text())["results"]), len(json.loads(f.read_text())["results"])) for f in [p/"r1-initial.json",p/"r1-passing.json"]])'`. The count is case detection, not a product-quality score.

## Agent checklist

1. Keep all 29 seeded files read-only. Run `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` from repo root (Godot 4.7.2 on PATH).
2. Open the emitted `verdicts.json`; check the overall verdict, each case's exit code and exact signature, and the mutant's `chain incomplete` diagnostic. Exit code 1 on a negative control is intentional.
3. On FAIL, inspect `output` before treating any exit code as success. A `SCRIPT ERROR:` is never a pass. Check missing resource paths and scene readiness using the table above.
4. Do not claim camera, UI, tilemap, juice, or export coverage: no round-1 fixture measures them (`corpus/knowledge/2026-10-12-production-checklist.md`).
