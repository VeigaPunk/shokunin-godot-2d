# Round 2 camera coverage — adversarial review

## Scope and current evidence

Read the standing brief and round-2 declaration in `LOG.md`, then inspected the current `corpus/fixtures/run_battery.py` and the existing scene-transition probe. At review time the runner had 14 unconditional cases plus the opt-in broken-scene mutation, and contained no camera case or camera-specific assertions. This review is adversarial guidance, not a verifier rerun: camera additions were not yet present in the inspected tree. Do not treat a future `PASS` label or the count of two camera cases as evidence until the checks below have been replayed against the final artifact.

The useful target contract is behavioral: after a controlled target displacement and enough frames for the declared camera policy, a positive camera must track the target; a no-follow mutant must fail the *same positional assertion*. Scene parsing, Camera2D node existence, `enabled`, and a printed success line alone do not establish tracking.

## False-positive risks (defect accepted)

1. **Load-only or node-presence assertion.** A script can load a scene and find a Camera2D while its camera never becomes current or never moves. Require a before/after measurement and a tracking relation (for example, `camera.global_position` follows the target, or the target's screen-space position stays within a declared tolerance after movement). Include an explicit target displacement large enough to exceed tolerance.
2. **Self-fulfilling output signature.** If runner accepts only `exit == 0` plus an expected substring, a script that prints `PASS camera_follow=true` without executing the assertion passes. A hand-written output spoof check is helpful, but the stronger test is the no-follow mutant: remove/disable follow behavior in scratch and prove that the runner rejects it. Make sure no assertion is conditional on a test flag that the mutant accidentally omits.
3. **Mutant does not actually mutate the behavior under test.** Check the scratch diff and mutation precondition. The mutant should change only the follow mechanism (e.g. disable the relevant camera or replace/disable its follow script), preserve the same target-motion scenario, and produce a failing tracking assertion. A scene-load error or parse error is not proof that camera tracking was detected.
4. **Wrong camera / wrong coordinate.** A camera node can follow while another current camera renders; checking only the node under test may pass. Assert it is `is_current()`/current for the active viewport where applicable, or derive target screen coordinates from the viewport transform. Compare consistent spaces: do not compare a local target position with a global camera position. For a centered camera, global-position equality can be valid, but state the expected policy.
5. **Weak or vacuous movement.** A zero displacement, movement before the camera is enabled, or a check performed before the target moves can pass an inert implementation. Assert initial and final target positions differ by a material amount and that the measured camera/screen response changes accordingly.
6. **False negative masked by substring.** Unrelated output can contain the success substring even when the assertion path failed. Require expected status *and* the behavioral result; reject `SCRIPT ERROR:`, `Parse Error:`, and unexpected errors, including in expected-failure cases. Keep machine verdict tied to structured result fields, not a line that merely says `PASS`.

## False-negative risks (working implementation rejected)

1. **Camera smoothing / limits / offset / zoom.** Exact target-camera equality may be wrong for a deliberately smoothed camera or camera with offset/limits. Declare a deterministic policy and use a bounded tolerance after a sufficient, bounded number of frames. If checking screen-space centering, account for viewport center and zoom. Avoid silently increasing a global timeout to hide a too-short camera settle window.
2. **Frame-order assumptions.** Camera transforms may update on a subsequent frame after target movement or `make_current()`. Sample only after the documented frame/update boundary; if necessary await a bounded number of `process_frame`s and report the measured frame count. Avoid testing an intermediate state as final.
3. **Startup/current-scene readiness.** Existing runner already documents a Godot 4.7.2 current-scene frame-order issue and patches only the scratch copy for the older causal probe. A camera test that samples immediately after scene change may fail spuriously. Add readiness to the camera test itself rather than broadening an unrelated patch.
4. **Floating-point and platform variation.** Exact float equality and brittle output formatting can reject valid results. Use an explicit epsilon and print numeric measurements in structured JSON (or stable, parseable fields); distinguish tolerance from expected motion threshold.
5. **Unintended project/scratch dependency.** Camera fixture resources must be copied into scratch and resolve using the scratch project root. A test that works only from the repository cwd can fail in isolated invocation. Exercise through the battery, not just `godot --path` in the fixture directory.
6. **Mutant failure classification.** If mutant case merely expects any nonzero exit, a timeout, missing executable, parse error, or crash may look like successful defect detection. Require the intended assertion-failure signature and expected exit; record timeout/launch error separately and fail the battery for these.

## Reproducible adversarial checks

Run from repository root with Godot available on `PATH`; choose a fresh run directory to preserve raw artifacts. These are recommended checks after the executor's camera case and opt-in mutant land (adjust only the documented mutant flag if its name differs):

```sh
set -o pipefail
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py \
  --runs .shokunin/game-dev-2d/corpus/live/critic-camera-positive
```

Require all prior cases and the camera-follow positive case to pass, then inspect the emitted `verdicts.json` and scratch copy. Next run the no-follow mutant mode and require the mutation case to be rejected specifically by the tracking assertion while the positive is still passing:

```sh
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py \
  --runs .shokunin/game-dev-2d/corpus/live/critic-camera-mutant \
```

At review time the runner did not yet expose a camera-mutant flag; the executor must add/document it before the mutation replay can be run. Inspect `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --help` after that change, then pass that exact option. Do not report mutant coverage if no such mode exists.

Inspect the JSON's per-case `actual_exit`, `error`, and captured output. Confirm that mutation is scratch-only and the source fixture is byte-identical to the pre-run version (`the hash checks below).

The following exact shell checks guard seeded inputs and expose the mutant's scope; run before and after each invocation, substituting the actual scene/script paths if the final implementation uses other names:

```sh
git status --short
sha256sum .shokunin/game-dev-2d/corpus/fixtures/controls/camera*           .shokunin/game-dev-2d/corpus/fixtures/camera*
find .shokunin/game-dev-2d/corpus/live/critic-camera-mutant -type f -maxdepth 5 -print
```

These commands use the repository path as written. Compare the two checksum outputs: seeded fixture hashes must not change. In each run's scratch project, diff the positive and mutant copy to verify only the documented follow behavior changed. Also check for source/runtime errors explicitly:

```sh
python - <<'PY'
import json, pathlib, sys
p = pathlib.Path('.shokunin/game-dev-2d/corpus/live/critic-camera-mutant')
files = list(p.rglob('verdicts.json'))
assert len(files) == 1, files
j = json.loads(files[0].read_text())
for r in j['results']:
    assert r['error'] is None, (r['case'], r['error'])
    out = '\n'.join(r['output'])
    assert 'SCRIPT ERROR:' not in out and 'Parse Error:' not in out, r['case']
print(j['verdict'], len(j['results']), files[0])
PY
```

That last generic check should be applied to the *positive* run as well. For mutant detection, additionally assert the mutant's `actual_exit` equals the intended assertion exit and its output contains the assertion-specific failure marker, while lacking the positive success marker. A baseline positive battery that passes is not mutation evidence by itself.

## Recommendation

Count camera coverage only when raw measurements prove movement and a paired, behavior-only no-follow mutant is rejected for the intended reason. The existing runner's current signature model is vulnerable to success-substring spoofing and expected-exit acceptance for negatives; camera additions should explicitly reject unrelated errors and should not classify timeout/launch failure as a successful mutant. I did not edit runner, fixtures, or seeded files.

## Review of camera files observed after the initial inspection

The executor's camera additions appeared while this report was being written. Current diff shows two independent scripts (`camera_follow.gd` and `camera_no_follow.gd`) and two unconditional cases in `CASES`; this supersedes the earlier snapshot statement that no camera additions existed. The scripts construct bare `Node2D`/`Camera2D` nodes at runtime. In the positive, the camera is a child of target; in the negative, it is a sibling. These are not a paired behavioral mutant: they alter the scene graph and compare separate setups. More importantly, the positive assertion compares `Camera2D.global_position` with the target's global position. Since the camera is parented to the target, ordinary transform inheritance makes that comparison pass even if the camera is not current and the viewport never tracks the target. Thus it is a false positive for the declared camera-follow behavior. The negative's `camera.global_position` remains unchanged because it is a sibling, so its expected error proves only the constructed hierarchy differs, not that disabling camera-follow in the positive scenario is detected.

Also, the no-follow expected signature includes `camera follow assertion failed...` and exit 2. This is stronger than accepting any nonzero exit, but the current runner still treats exact exit + substring as enough, and the negative is not produced by mutating a known-good setup. Recommend replace the two ad hoc scripts with one shared probe parameterized by a scratch-only follow-disable mechanism (or produce the mutant from the exact positive setup); measure target screen position through the viewport/canvas transform after moving target, assert the active viewport camera is current, and require a material displacement. Then the pair can demonstrate that the same screen-space contract passes/fails, not merely that scene-parent coordinates differ.

Concrete check to falsify current positive: run its exact `godot --headless --path <scratch> --script res://camera_follow.gd` command but make the camera non-current (or disable it) without changing its parent-child relationship. If the script still prints PASS (likely, because global transform inheritance remains), the runner's positive contract has a false positive. The stronger replacement check is to alter only `current`/enabled state in the scratch copy and confirm the same screen-space assertion fails for the intended reason. Do not count the current no-follow case as a mutation control until it uses the identical probe/setup and validates this.
