# Round 25: export target path form in Godot 4.7.2 headless fixture battery

Source: `corpus/fixtures/run_battery.py`, `reports/r25-pair-reviewer.md`, `reports/r25-export-scout.md`, `reports/r25-export-verifier.md`, `reports/r25-export-verifier2.md`. Pre-fix alternating raw copies `corpus/lessons/r25-pair-before-{1,2,3,4}.json`; direct target isolation `corpus/lessons/r25-direct-target-pair.json`; initial partial-fix adverse `r25-export-verifier.json` and `r25-export-launch-adverse.json`; final raw `r25-export-verifier2.json`, `r25-export-launch-verifier2.json`.

| Controlled target form | Pre-fix result | Inference |
|---|---|---|
| Relative export target, same cwd/seed/preset, alternating full runner trials 1 and 4 | exit 1, 0 bytes, exact `Prepare Template: The given export path doesn't exist.` | Fail closed; do not retry into success. |
| Absolute export target, alternating trials 2 and 3 | exit 0, 73,703,800-byte executable, same SHA256 | This form succeeds in tested host/fixture. |
| Relative project root + absolute target versus absolute project root + relative target | first succeeds, second fails; see direct target pair | Isolates target spelling rather than project-root spelling in this test. |
| First fix: only readiness target `.resolve()` | independent explicit-relative full run 49/50; launch exports still relative and FAIL | Both export call sites require same target normalization. |
| Final fix: readiness and launch target `.resolve()` | fresh non-author explicit-relative full run 50/50; missing preset still expected exit 1 / outer PASS | Bounded calibration gain, not general/production export reliability. |

A baseline-scout child failed to supply its assigned report and identified itself as executor, so authorship of first line is uncertain. Admission uses inspected diff and independent replay, not child self-attribution. Both historical adverse and first partial-fix 49/50 are retained. No classifier/CASE list/seeded control or export success predicate changes.
