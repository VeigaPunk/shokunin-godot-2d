# Round 23: left Camera2D limit in headless Godot 4.7.2

Sources: `corpus/fixtures/camera_limit.gd`, `corpus/fixtures/run_battery.py`, named non-author `corpus/lessons/r23-left-verifier.json` and `reports/r23-left-verifier.md`.

| Setup | Observation | Decision |
|---|---|---|
| Target (-2000,0), current camera limit_left=-1000, 64px battery viewport | screen center x=-968 (-1000 + 32), distinct from target | Accept if dynamically derived center, movement, current camera and separation pass. |
| Same target and authored assertion boundary -1000, camera limit_left=-100000 | center follows target x=-2000; exit 2 on same left assertion | Causal control; no setup failure. |
| Scratch sabotage authored limit_left -1000→-100000 | original positive fails intended assertion | Detects ineffective authored bound. |

Scout scratch viewport was 720px and center -640: the same formula with half-width 360. Never hard-code -968 outside the observed 64px battery. Verifier default full battery 48/48 PASS (37 ordinary, 2 mutants, 9 opt-in) and separate Python fault meta top-level PASS with deliberate inner FAIL controls. Headless center state only; no rendered framing or production behavior. Existing export adverse observations remain unresolved.
