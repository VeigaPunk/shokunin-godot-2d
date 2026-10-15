# Round 8 contact independent verifier

## Verdict

**Conditional pass; coverage improved for runtime collision presence and polygon-removal sensitivity, but the cell-specific attribution claim is not yet robust.** No broad claim of full level playability follows. The author's battery and direct copied-project control replayed successfully. My scratch falsification below showed a same-layer different-cell collision can make the positive assertion fail despite collision with the intended-layer tile, so present logic is not merely vulnerable to false positive in that setup; nevertheless contact points are robustly mapped to the correct cell in the original case. More importantly, the test checks `contacted` against contact point cell and is valid for current authored scene. It does not verify expected *top boundary* / normal, and the contact-point mapping can be susceptible to adjacent cell if altered geometry. Distinguish this residual limitation from a failure of current evidence.

## Independent native run

Ran exactly `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` from the project root. Exit 0. Raw JSON: `.shokunin/game-dev-2d/corpus/live/runs/20261012T171621951421Z/verdicts.json` (absolute: `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/runs/20261012T171621951421Z/verdicts.json`). It contains 27/27 PASS, including all 25 prior cases and both prior mutants; no unexpected FAIL. Each contact result has `error: null`. Positive output: start `(40.0, 36.0)`, end `(40.0, 44.82812)`, `contacted=true`, `collider=Ground`, `collider_cell=(2, 3)`, exit 0. Negative: exit 2 (expected), polygon count checked by fixture as zero, `contacted=false`, collider null, ends `(40.0, 76.0)` beyond target, `crossed=true`; expected assertion signature matches. It contains intended `ERROR: CONTACT ASSERTION FAILED...` only for negative; no `SCRIPT ERROR`, `Parse Error`, `Invalid`, resource load, or setup diagnostics in case outputs. No unexpected `ERROR:` in any other case output.

The fixture JSON/run directory remains under ignored `corpus/live/runs/`; scratch and `missing-preset-scratch` are contained there. Hashes of all 36 tracked files under `corpus/fixtures` were identical before/after this run. Runner removes generated export products from its scratch output. It adds only ignored run evidence, no tracked fixture changes/artifact leakage.

## Direct and adversarial scratch replays

Copied fixture project to a fresh `/tmp/r8-direct-*` directory and ran `godot --headless --path <copy> --script res://contact_probe.gd -- --no-collision`: exit 2 with exact expected contact assertion, start/end `(40,36)` to `(40,76)`, no collider, crossed true. The positive case is independently represented in the author battery's `contact_runtime` raw record (exit 0).

Scratch falsification only (seed project untouched): added an additional collidable tile at `(2,2)` directly above target `(2,3)`, and moved body start upward from `(40,36)` to `(40,20)`, preserving the motion path through target. Positive run exited 2 with `collider=Ground` but `contacted=false`, stopped at y=`28.82812`; current logic did *not* mistake the other same-layer tile for the target. This supports cell mapping as an actual assertion, not just printed metadata. It is a fail-closed result rather than evidence for other tile scenarios.

## Limits / no-go

This is finite headless CharacterBody2D physics against the authored packed fixture, not rendered gameplay, production playability, varied shapes, or all map cells. The control proves the checked cell's atlas polygon removal in this scene produces unobstructed traversal. No authored scene, runner, engine/editor source was edited by me; no delegation, commit, or push. Only this report is my write.
