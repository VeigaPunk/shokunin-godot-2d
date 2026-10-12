# Round 10 launch adversarial review (read-only)

## Verdict: HOLD pending implementation

The launch implementation was not present at review time. The working tree shows only an untracked scout report, an `--probe-export-launch` parser flag, and an unused `os` import in `run_battery.py`; there is no `export_launch*` fixture and no launch branch/helper yet. Thus none of the four launch-critical behaviors is demonstrated by code or replay. Do not count planned behavior or export readiness as launch coverage.

## Checks required before acceptance

1. **Invoke the exported artifact itself.** In `run_battery.py`, current export path only invokes `godot --headless --path ... --export-debug ...`; that proves packaging/export, not executable startup. Launch command must have the exact freshly exported `fixture.x86_64` path as argv[0] (direct `subprocess` invocation), with `--headless` as an argument if needed. Do not use `godot --headless --path ...` or `godot --headless --path ... --script ...` for this assertion: those run the editor/runtime binary, not the packaged executable. Capture launch stdout/stderr, code, and timeout separately from export output.

2. **Prove the startup scene is in the artifact.** Seed `project.godot` currently has no `application/run/main_scene`, and no scene is configured as startup. Add/configure the startup scene only in a fresh scratch project before export. Require the positive exported binary itself to emit a unique marker from that scene's runtime startup event; do not infer packaging from source presence, export success, an export-log marker, or an editor-run script. Ensure the marker is absent from export output and control inputs. A same-name source file outside the PCK is not sufficient.

3. **Use the same assertion for positive and control.** Define one launch predicate, e.g. direct executable exits 0 before deadline **and** exact startup token occurs exactly once. Run it unchanged against positive and a separately exported negative control whose startup event is absent. The overall probe should pass only when positive predicate is true and negative predicate is false. Record control's code/output; its expected no-main diagnostic is corroboration, not a different acceptance predicate. A control that merely fails to export is invalid; it must be exported and then launched.

4. **Bound and reap all processes.** Both export and direct-launch subprocesses need finite timeouts. `subprocess.run(..., timeout=...)` bounds the direct child and kills it on expiry; record `TIMEOUT` as launch failure. Do not spawn shell/background wrappers, use `Popen` without wait/kill cleanup, or allow exported game to persist. The successful fixture should self-quit after marker; still keep external timeout as guard. If using a process group, terminate/reap the group on timeout, not just the launcher.

## Other falsification points

- Preserve and hash the exact executable before cleanup; launch that path, not a stale artifact. Keep positive and control output directories disjoint and initially empty. Record executable SHA-256 and command for attribution.
- An exit code of zero alone is insufficient: an empty project/no-main process may exit successfully, or return before the desired scene/event is reached. Require exact runtime marker and reject `SCRIPT ERROR:`/parse errors.
- Verify the control's marker is absent from its PCK/runtime output, not merely absent from one GDScript source. Reusing a positive PCK or mutating the same output after export invalidates the counterfactual.
- No launch replay/result or named independent verifier evidence is available yet in reviewed files. After implementation, verify the normal pre-existing battery still passes and retain raw launch evidence; do not claim coverage until non-author replay verifies these checks.

Scope was read-only; no fixture, runner, project, or engine/editor files were changed by this reviewer.
