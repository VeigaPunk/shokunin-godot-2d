# Round 6 export scout — read-only findings

## Environment and fixture

- `godot --help` identifies this executable as an editor build, Godot `4.7.2.stable.arch_linux.ed1daf0bf` (4.7.2.stable, 2026-08-17). `--export-debug <preset> <path>` / `--export-release` are editor-only; help says preset must be in `export_presets.cfg`, output must include a binary filename, and target directory must already exist. `--headless` is available, but does not make the export option available on a non-editor build.
- Installed templates are under `~/.local/share/godot/export_templates/4.7.2.stable/`; `version.txt` matches `4.7.2.stable`. Linux x86_64 debug and release templates are present (`linux_debug.x86_64`, `linux_release.x86_64`), along with other platform templates. This is an inventory check, not proof every platform template works.
- Existing fixture `corpus/fixtures/project.godot` is a minimal Godot 4.7 project. `corpus/fixtures/export_presets.cfg` defines preset `Linux/X11` (`platform="Linux/X11"`, all resources, x86_64); both custom template overrides are empty, so the preset uses installed default templates. Its `export_path` is empty. Do not assume production project/preset parity from this synthetic fixture.

## Safe probe recommendation (not run)

Use an isolated copy of the fixture under `corpus/live/<unique-run>/project/`; do not run the export against the seeded fixture. Ensure output directory exists inside that same scratch run. Invoke the editor build headlessly, using explicit project and output paths, for example:

```text
godot --headless --path <scratch>/project --export-debug "Linux/X11" <scratch>/out/fixture.x86_64
```

A positive readiness observation is exit 0 plus the expected nonempty file at the exact scratch output path and no export error in captured diagnostics. Record Godot version, preset name, template inventory/version, exit code, output existence/size, and diagnostic tail. Delete scratch output after measurement. This performs an actual export and creates an executable artifact; call it scratch export, not a no-output dry run, and never write to the repository's normal build/release locations.

## Negative controls

- Missing preset: in a separate scratch project copy, invoke the same export command with a deliberately nonexistent preset name and an output path under its pre-created scratch `out/`. Expected: nonzero exit and a missing/unknown preset diagnostic; verify no output artifact appeared. Do not alter the fixture preset for the positive case.
- Missing template: another independent scratch copy can keep `Linux/X11` but set `custom_template/debug` in its scratch-only preset to a deliberately nonexistent absolute path (or otherwise select a platform whose required template is absent). Run the command with output confined to that copy's scratch `out/`. Expected: nonzero exit with a missing template diagnostic, no output artifact. Explicit custom template avoids depending on whether this host's default template happens to exist. Keep mutation and logs in scratch.

Use separate scratch runs for each branch, capture stdout/stderr and exit status, assert that any created files remain beneath the run's `out/`, then remove scratch. Avoid running `--export-*` in the repository fixture: export commands generate distributable artifacts, and help provides no validation-only/no-output export switch. Headless mode alone does not prevent writes.

## Scope / limitations

No command that performs an export was run. This scout only inspected help, installed template files/version, and fixture configuration. Recommended tests measure local Godot export readiness for this fixture and host only; they do not prove a production build, cross-platform readiness, successful launch, or shipping readiness. The round target requires positive and negative replay plus retained battery tests; this scout provides a safe design, not those results.
