# Round 8 contact executor report

Implemented new `contact_probe.gd` and added `contact_runtime` / `contact_no_collision` to `run_battery.py`. The probe loads the existing `level_collision/level_scene.tscn` read-only in battery scratch, keeps cell `(2,3)` occupied, uses a `CharacterBody2D` with layer/mask `1`, and drives the same 40px motion through that tile in both cases. Positive contact checks the `Ground` collider and maps the reported contact point back to `(2,3)`. The negative duplicates the TileSet only in scratch and removes the cell's collision polygon; it verifies polygon count `0`, no contact, and that the body crossed the tile region. Both paths free body and level before exit.

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`

Result: exit 0, `PASS battery`, 27/27 cases. The contact positive reports start `(40,36)`, end `(40,44.82812)`, collider `Ground`, cell `(2,3)`; the negative reports start `(40,36)`, end `(40,76)`, `contacted=false`, `collider=null`, `crossed=true`, and is correctly recognized by the battery as its expected exit-2 assertion. Existing 25 cases (including both prior mutants) pass. No `SCRIPT ERROR`, parse error, or invalid physics-step warning in run output. Run verdict: `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/runs/20261012T171415351323Z/verdicts.json`.

Scope: only new `contact_probe.gd`, existing `run_battery.py`, and this report were written. Seeded level files unchanged; no delegation, commit, push, or engine/editor changes.
