# Round 10 — scratch exported executable startup

Reproduce on this host (Godot 4.7.2 Linux/X11): `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch` → independent 32/32 PASS in `r10-battery-verifier.json`, paired export/launch details in `r10-launch-verifier.json`. Named non-author verifier: `.shokunin/game-dev-2d/reports/r10-launch-verifier.md`. `--fault-injection` remains meta PASS in `r10-fault-regression.json`.

| Scratch-only action / observation | Decision | Limit |
|---|---|---|
| Scratch scene `_ready()` prints `EXPORT_LAUNCH_READY scene=fixture`, then quits; exported Linux/X11 PCK 28,020 B; direct `<out>/fixture-launch.x86_64 --headless` with cwd in products-only `out/`, bounded 5s, exit 0 and exactly one event line | same launch assertion true | synthetic headless event, not gameplay or GUI |
| Same configured main scene/script and export path in separate scratch project; remove only event print, retain self-quit; PCK 27,956 B with distinct digest; direct launch exits 0 cleanly without event | same assertion false, control valid | not a negative for missing main scene (early invalid draft removed) |
| Verifier removes positive event print in disposable `/tmp` copy, then reruns | both assertion false, meta FAIL / exit 1 | scratch-only falsification |

Both exports returned 0 with `[ DONE ]`/`savepack`, produced separate `.x86_64`/`.pck`/`.sh`, then deleted all products after recording bytes and SHA-256. The executable is the same host template (same hash) but PCK hashes differ. Launch cwd contains no project.godot or source scene/script; the token is absent from export logs and control source. Verifier hashed 37 tracked fixture/runner files unchanged before/after. An early draft with missing main scene hit a timeout bytes/string TypeError and yielded no valid decision; it was corrected and disposable scratch removed. This is not a production game build, rendering, cross-platform test, shipping authorization, or rights clearance.
