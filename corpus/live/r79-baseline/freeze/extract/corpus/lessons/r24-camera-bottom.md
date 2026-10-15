# Round 24: bottom Camera2D limit in headless Godot 4.7.2

Sources: `corpus/fixtures/camera_limit.gd`, `corpus/fixtures/run_battery.py`, named non-author `corpus/lessons/r24-bottom-verifier.json` and `reports/r24-bottom-verifier.md`.

| Setup | Observation | Decision |
|---|---|---|
| Target (0,2000), current camera limit_bottom=1000, battery viewport height 64px | center y=968 (`1000 - 32`), distinct from target | Accept dynamic viewport-adjusted bottom clamp, current camera and movement. |
| Same target and authored assertion boundary 1000, camera limit_bottom=100000 | center follows target y=2000, exit 2 intended bottom assertion | Causal far-bottom control, not setup failure. |
| Scratch sabotage authored limit_bottom 1000→100000 | original positive fails intended assertion | Detects missing effective authored bound. |

Scout scratch viewport height 450px produced center 775 (`1000 - 225`); always derive half-height at runtime. Named full default-path replay 50/50 PASS (39 ordinary, 2 mutants, 9 opt-in); separate fault meta top-level PASS with deliberately failing inner hang/unrelated cases. Author relative-`--runs` replay was 38/39 due to export readiness `Prepare Template: The given export path doesn't exist.` in committed `corpus/lessons/r24-export-adverse.json`; default-path export passing once does not resolve it. Headless center only; no rendered framing or export reliability claim.
