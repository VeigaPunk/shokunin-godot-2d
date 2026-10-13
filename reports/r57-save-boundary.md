# Round 57 — user:// isolation and boundary

## Scope

Read-only map for the save/load fixture proposal. No fixture, runner, engine, editor, production project, or existing scratch artifact was edited. My only created paths are this report and `.shokunin/game-dev-2d/corpus/live/r57-save-boundary/` (probe below).

## Findings

- `run_battery.py` stages the fixture tree into a per-run directory under `corpus/live/runs/<UTC timestamp>/scratch` (runner lines 108–118), then invokes Godot with `--headless --path <scratch> --script res://<fixture>` (line 270). Source fixture edits are therefore not required for a save test to create or corrupt files: the fixture can make its writes in `user://`, while deliberately corrupted bytes should be a copied file in that namespace, never a `res://` fixture/source file.
- `user://` is **not** a directory inside the battery's scratch project. Its location is derived by Godot from the application/project identity and the OS user-data root. The seeded `project.godot` currently names the app `MechanicOneShotTest` and declares feature 4.7. Distinct timestamped scratch project roots with the same application name may consequently resolve to the same persistent user-data directory. This is an isolation caveat: a fixture should use unique per-case filenames and should not assume `user://` resets merely because the runner creates a new scratch tree. Avoid destructive cleanup of unrelated user files.
- The production/non-production boundary is operational, not guaranteed by the scheme: `user://` means app user data, not “test-only.” The runner's `--path` is the staged scratch project; use a fixture-specific test filename (and, if feasible, a dedicated test project identity) so test data is separate from an installed game's saves. Do not point this fixture at a real game identity or real user saves. `res://` is the staged project resource namespace, and should remain read-only for this case.
- For a negative control, corruption must be applied to a copied scratch save byte stream and the loader must reject it distinctly. Do not mutate the positive source fixture's expected values, project files, or any preexisting user save. A negative exit/log must be attributed to the expected parse/read error rather than an unrelated failure.

## Probe and exact evidence

Created `.shokunin/game-dev-2d/corpus/live/r57-save-boundary/probe/project.godot` with application name `R57BoundaryProbe`, and `probe.gd` printing `ProjectSettings.globalize_path("user://")`. Commands:

```text
godot --version
4.7.2.stable.arch_linux.ed1daf0bf

godot --headless --path /home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r57-save-boundary/probe --script res://probe.gd
exit 0
USERDIR=/home/vgpnk/.local/share/godot/app_userdata/R57BoundaryProbe/
```

This directly demonstrates that the probe's `user://` resolves outside its staged project tree, under the OS account's Godot app-data root. It does not establish the exact platform behavior elsewhere. `godot --help` lists `--path <directory>` and headless mode, but no user-data override option. A status check scoped to the fixture paths showed only my unique scratch directory as untracked; I did not touch the runner or fixture sources.

## Risks / limits

- Unique run scratch does not itself provide unique `user://` storage. Repeated runs may leave or reuse user data; unique filenames or a project identity isolated for test execution are needed for reliable runs.
- `user://` is writable and durable across launches, but this says nothing about atomicity, crash consistency, backup, security, migration, or durability guarantees for production saves.
- Probe used Godot 4.7.2 on this Linux account only. It is an API/path observation, not evidence of cross-platform paths or production behavior.
