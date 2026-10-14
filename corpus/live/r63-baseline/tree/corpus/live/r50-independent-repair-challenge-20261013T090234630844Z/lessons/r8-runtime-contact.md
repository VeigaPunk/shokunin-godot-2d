# Round 8 — finite runtime tile contact

Reproduce on Godot 4.7.2 with `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`. Independent named non-author verifier `r8-contact-verifier`: committed `r8-contact-verifier.json`, 27/27 PASS (25 retained). Direct copied-project no-collision also exited 2 with expected assertion; scratch extra collidable tile at `(2,2)` caused a fail-closed contact attribution, not a false positive. Reports under `.shokunin/game-dev-2d/reports/r8-contact-*.md`.

| Finite action / observation | Decision | Limit |
|---|---|---|
| Instantiate authored `level_collision/level_scene.tscn` in ignored scratch; occupied `(2,3)` has polygon; CharacterBody2D 6×6 mask/layer 1 starts `(40,36)`, sweeps down 40px after physics frames | exit 0; collider `Ground`, contact point maps to `(2,3)`; stop `(40,44.82812)` before center `(40,56)` | headless 2D body motion at one cell; no rendering |
| Same body/motion; deep-copy TileSet in scratch and remove atlas polygon; occupied tile remains and polygon count=0 | exit 2 expected assertion; collision=null, end `(40,76)` crosses tile; no setup errors | same authored fixture, not an independent environment |
| Add a second collidable tile at `(2,2)` in disposable `/tmp` copy and start sweep above it | fails closed on other cell contact | not a general proof of all adjacent-tile geometry |

The normal and control paths use the same contact assertion, but the control is admitted only if collision is null and full traversal occurred; setup/polygon mismatch exits 3 instead of being misclassified as expected negative. Verifier hashed 36 tracked fixture files unchanged before/after. This upgrades r4's metadata-only evidence to one runtime contact; it does not test production project, visuals, varied shapes, normals, or all cells.
