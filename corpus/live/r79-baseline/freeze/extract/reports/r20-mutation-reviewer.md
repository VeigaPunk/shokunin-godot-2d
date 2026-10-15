# Round 20 mutation reviewer — top-edge Camera2D

Scope: disposable scratch replay and sensitivity check only. No tracked fixture or runner edits. Godot observed: `4.7.2.stable.arch_linux.ed1daf0bf`.

Copied the executor's in-progress `project.godot` and `camera_limit.gd` into `.shokunin/game-dev-2d/corpus/live/r20-mutation-reviewer-scratch/`. The scratch fixture was restored to byte-equal the shared tracked fixture after mutation. Scratch is reviewer-owned; no engine/editor or seeded controls were changed.

Commands against the unmutated scratch fixture:

- `godot --headless --path <scratch> --script <scratch>/camera_limit.gd -- --top-bound` → exit 0; `PASS ... center_at_viewport_adjusted_clamp=true ... top_test=true`.
- `godot --headless --path <scratch> --script <scratch>/camera_limit.gd -- --far-top-bound` → exit 2; observed center `(0,-2000)`, expected clamp `-968`, then `ERROR: camera limit assertion failed: expected active center within top boundary and distinct from target`. This is the intended assertion, not setup failure.

Mutation: in scratch only, changed authored `camera.limit_top = -1000` to `camera.limit_top = -100000`, preserving the positive `--top-bound` invocation. Replayed the positive command: exit 2, observed center `(0,-2000)` versus expected `-968`, and the same intended top-bound assertion diagnostic (not setup failure). Restored scratch file afterward and confirmed byte equality to the shared fixture.

This demonstrates positive-assertion sensitivity to removal of the authored top limit in this Godot headless configuration. It does not establish full battery regression, rendered pixels, production camera behavior, or other edges; no such claims made. The full battery and independent verifier remain outside this reviewer replay.
