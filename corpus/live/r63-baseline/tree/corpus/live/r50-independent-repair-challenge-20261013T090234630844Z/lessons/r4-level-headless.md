# Round 4 — authored level tile collision metadata

Reproduce: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` on Godot 4.7.2. Named final non-author verifier `r4-level-verifier-final`, report `.shokunin/game-dev-2d/reports/r4-level-verifier-final.md`, committed 21/21 raw replay `r4-level-verifier.json`. Earlier `r4-level-verifier` initially held a verdict due to RID/resource leaks; adding level to tree and freeing after a frame cleared the positive output; its later replay report also confirms 21/21.

| Observation | Classification | Limit |
|---|---|---|
| PackedScene `level_collision/level_scene.tscn` has cell `(2,3)` with source 0 and physics-layer-0 four-vertex collision polygon; probe loads and asserts TileData metadata | authored collision metadata PASS | no CharacterBody2D contact/blocking physics shown |
| Same probe `--no-collision` duplicates TileSet and removes only the tile's polygon, preserving occupied cell; exits 2 at same assertion | isolated missing-polygon control detected | no rendered tiles or production level design |
| Initial positive case leaked RID/resources because level was never in tree/freed; corrected probe adds to tree and frees after frame, final independent output clean | lifecycle correction | runner does not reject every unrelated `ERROR` string; inspect raw record |

The final verifier hashed all 32 existing tracked fixture paths unchanged. Collision metadata is not physical solidity: runtime body contact remains unprobed.
