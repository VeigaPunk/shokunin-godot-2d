# Round 58 process scout

## Scope and tracked architecture

Read-only inspection of `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py`, `save_roundtrip.gd`, and Round 58's declared claim in `LOG.md`. No tracked files were changed. The existing battery stages a project copy in a timestamped `run_dir/scratch`, changes `project.godot` to a run-unique `config/name`, and creates `run_dir/xdg-data` as an absolute path. For `save_roundtrip.gd`, its `execute()` supplies a copied environment with `XDG_DATA_HOME` set to that path, and invokes Godot through `run_process()` (`subprocess.run`, capture output, timeout). It passes that same `env` to one Godot invocation per save case. The present save fixture writes and reopens `user://r57-save.json` in that same process. Thus the current runner establishes run-local storage and a copied project identity, but does **not** itself establish writer/reader process independence.

## Independent-process scout probe

Used only `.shokunin/game-dev-2d/corpus/live/r58-process-scout/independent-process-probe/` as a scratch project, a unique project name `MechanicOneShotTest-r58-scout`, and absolute `XDG_DATA_HOME` at `.../r58-process-scout/independent-process-probe/xdg-data`. Godot reported version `4.7.2.stable.arch_linux.ed1daf0bf`.

1. Launched the existing `save_roundtrip.gd` positive writer as a standalone Godot process. It exited 0 and printed `PASS save_roundtrip structured=true reopened=true values_match=true`; its reported absolute file was inside the scratch XDG directory at `godot/app_userdata/MechanicOneShotTest-r58-scout/r57-save.json`.
2. Separately launched a scratch-only reader script in a new Godot process, with the same copied project and `XDG_DATA_HOME`. The writer and reader process IDs were 3207208 and 3206286 respectively. The reader opened the existing save read-only, parsed it, compared the nested dictionary/array/bool values, and exited 0 with `PASS independent_reader structured=true`. The reader code contained no positive-path write operation.
3. Launched that scratch reader separately with `--missing`, targeting an absent `user://r58-absent.json`; it exited 2 with exact `ERROR: EXPECTED NEGATIVE: reader rejected missing save`. This exercises the missing-file branch, not wrong-value rejection.

Commands used Godot `--headless --path <absolute scratch> --script res://... --`; the standalone launches inherited the same run-local absolute XDG setting. The reader code and logs are in the named scratch directory. This is exploratory evidence for the process/storage arrangement, **not** a battery fixture or named non-author replay.

## Recommendation and limits

The simplest runner implementation is two sequential Godot invocations against the same scratch path/project identity and same absolute XDG environment: writer then reader-only mode/script. Keep any absent-file sabotage in a separate scratch copy (or run it before the positive writer); otherwise the positive save would exist and invalidate the missing-file control. The named replay should retain all prior 83 classifications and explicitly record both child invocations' commands, exits, output, and the globalized `user://` path. A reader that opens and validates the saved file without writing is the necessary independence check. Do not infer power-loss durability, flush guarantees, atomicity, broad corruption/tamper rejection, production persistence, or platform portability from these probes.
