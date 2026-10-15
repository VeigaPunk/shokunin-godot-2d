# Round 13 — bounded Tween `modulate` excursion and return

Reproduce on Godot 4.7.2 with `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error`: named non-author verifier independently **37/37 PASS** (`r13-battery-verifier.json`); fault classification meta PASS (`r13-fault-regression.json`). Initial author replay at a 36-frame observation cap failed the positive before it could return to baseline; a 90-frame cap passed. Critic caught a separate exact expected-error mismatch with the detailed negative diagnostic; executor corrected only the case-owned comma-terminated allowed prefix, then reran 31/31. Reports `reports/r13-juice-*.md` retain these adverse steps.

| Headless runtime action | Godot observation | Scope |
|---|---|---|
| Attach actual `Node2D` to SceneTree, baseline `modulate=(0.7,0.8,0.9,1.0)`, Tween for two 0.2 s legs to `(1.0,0.2,0.1,1.0)` and back; sample `target.modulate` each process frame for at most 90 | exit 0; observed nonbaseline `(0.7041,0.7918,0.8891,1.0)`, then original baseline by frame 62; no warning | Actual sampled property excursion and return; no rendering or perceived flash. |
| Same script and sampling loop, `--no-tween` skips only Tween start | exit 2 at same transient-then-return assertion after 90 frames, `transient_seen=false`, `baseline_restored=false`, final baseline; no parse/setup/other error | Rejects missing Tween start; exact case-owned expected diagnostic only. |
| Verifier disables Tween start in disposable `/tmp` copy | positive fails, no-start negative still passes, other ordinary cases pass when all export config is copied | Counterfactual supports attribution; no source edit. |

This differs from r5's `AnimationPlayer` direct `advance(0.5)` on `position.x`: it tests SceneTree Tween scheduling, CanvasItem modulation and return to baseline across process frames. It does not establish image pixels, perceived brightness, visual quality, production game integration, or universal timing. New fixture is copied to ignored scratch, and verifier's runner/new-fixture hashes remained unchanged.
