# Round 20 scribe — provenance checklist

Scope: closure checklist only; no fixture or runner edits. This records a live inspection, not verifier evidence or a verdict.

## Declaration and baseline

- [x] Round-20 declaration read in `.shokunin/game-dev-2d/LOG.md` and mission brief read at `/tmp/mission-game-dev-2d-standing.md`. Declared axis: coverage; intended change: add top-bound positive and far-top-bound control to existing headless `camera_limit.gd` battery. Declared before-state: 33 ordinary cases, with right-edge camera rows; target after-state: 35 ordinary cases.
- [x] At read time, `git rev-parse HEAD` was `3d19377a604df726377e53b8007b284a3607875d`. `git status --short` showed only ` M .shokunin/game-dev-2d/LOG.md`; no fixture/runner modifications were reported at that particular command.
- [x] Inspected baseline at HEAD from the declaration: runner CASES contains 33 entries, including `camera_limit` and `camera_far_bound`; no top-edge camera case. The committed fixture has right limit `1000`, far-right control `100000`, target `(2000,0)`.
- [ ] Closure must capture exact before and after CASE counts from the tested revision, not just the declaration. Confirm 33 -> 35 and identify the two newly added case names/flags. If counts differ, reconcile before verdict.
- [ ] Capture `git diff --stat` and hashes of the exact tested fixture/runner revision (or immutable commit) and state whether seeded controls/corpus were untouched. The earlier checked-out revision has no applicable after hash yet.

## Working-tree observation (not a stable result)

A later read of the shared worktree observed a top-edge fixture implementation in the working `camera_limit.gd` (it supports `--top-bound` and `--far-top-bound`) and the runner still listed 33 CASES, with no top rows visible in its CASES table. At that later point both fixture and runner differed from HEAD, while `git status` had only been sampled earlier. This is a transient shared-worktree observation, not a claim about the final patch: record the final diff and reconcile that the runner actually invokes both top arms. The working fixture's top test uses target `(0,-2000)`, boundary `-1000`, viewport half-height, expected center `boundary + viewport_half`, tolerance `0.01`, movement threshold `100`, and setup errors exit 2.

## Independent verifier evidence required

- [ ] Named non-author verifier is `r20-top-verifier`; record the verifier report and raw lesson path (expected `reports/r20-top-verifier.md` and `corpus/lessons/r20-top-verifier.json`). Do not substitute executor/parent reruns for independent verification.
- [ ] Record exact command(s), exit status, tested revision, and artifact paths. Confirm the raw seeded replay has 35/35 PASS (or explicitly explain any different total), including both new top rows PASS and all 33 prior outcomes unchanged.
- [ ] Check raw output demonstrates positive top clamp: active camera center y equals top boundary plus viewport half-height, remains within the top limit, advances from prior center, and is distinct from moved target.
- [ ] Check far-top-bound control is detected by the intended camera-limit assertion (expected case exit 2), with the specific assertion diagnostic; it must not be a setup failure, script error, or parse error. Record diagnostic and case classification from raw artifacts.
- [ ] Record disposable fault-injection command/artifact and result if performed. State clearly whether it is independent verifier evidence; do not infer mutation sensitivity from the top control alone.
- [ ] Check ordinary prior cases unchanged against baseline raw result set where available, and report any exceptions as adverse evidence.

## Verdict and limitations

- [ ] State each axis categorically: coverage / depth / calibration = improved, harmed, unchanged, or unprovable-but-better. Admit only if at least one improves and none are harmed, per mission.
- [ ] Bound the coverage claim to the tested headless Godot Camera2D top-limit fixture and observed assertions. Do not claim rendered-pixel behavior, production-camera coverage, other edges, zoom/rotation/offset behavior, or export readiness from this evidence.
- [ ] Record any unresolved export or unrelated adverse event; a passing camera replay does not settle export reliability.
- [ ] List introduced constants/thresholds if retained in final implementation (e.g., top bound, far bound, target displacement, viewport-derived expectation, tolerance, movement threshold).

## Attribution and report-last closure

- [ ] Attribute each edit and each evidence run to its author/role; identify the non-author verifier and distinguish author reruns from verifier replay. Include failed/missing lanes as telemetry, not as proof.
- [ ] Ensure own and all required lane reports are present before closure; LOG closure gives links/paths to raw verifier artifacts and reports the exact final tested commit/tree.
- [ ] Commit only after reports and LOG closure are complete (report-last); verify the final commit identity and clean status. No push/merge.

No final verdict is offered here: at inspection time the verifier evidence, final case count, and final attribution/commit were not yet observed.
