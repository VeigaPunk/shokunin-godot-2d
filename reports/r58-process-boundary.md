# Round 58 — cross-run and project-identity boundary probe

## Scope and method

Read-only probe of the process-boundary save claim. I created only this report and `.shokunin/game-dev-2d/corpus/live/r58-process-boundary/`. No seeded fixture, runner, tracked project, or prior receipt was changed. Godot 4.7.2 headless writer and reader invocations used separate OS processes (recorded PIDs) and scratch-only project files. Every invocation set absolute `XDG_DATA_HOME` to a directory under this probe's scratch. Raw stdout/stderr, exits, PIDs, and project roots are in `corpus/live/r58-process-boundary/evidence.json`.

## Results

- Writer process PID 3206694 exited 0 after writing `user://boundary.json`; it reported `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r58-process-boundary/run1/xdg-data/godot/app_userdata/R58BoundaryProbe/boundary.json`.
- Independent reader PID 3206734, same project identity and same absolute run1 XDG root, exited 0 and read exactly `{"run":"writer"}`. Its positive path only opens/reads; it does not rewrite the save.
- Independent reader PID 3206774, same identity but a different absolute run2 XDG root, exited 2 with `READER_MISSING`, and named the run2-only expected path. This is intentional negative evidence that differing XDG roots isolate app data.
- Reader PID 3206812 used a second project with identity `R58WrongIdentity`, while retaining run1's XDG root; it exited 2 with `READER_MISSING` at `.../app_userdata/R58WrongIdentity/boundary.json`. Identity changes redirect `user://`; a reader pointed at the wrong project identity will not find the writer's save.
- Reader PID 3206864 used a distinct project directory but the same `R58BoundaryProbe` identity and run1 XDG root; it exited 0 and saw the writer's bytes. Thus app identity plus XDG root, not project directory, selects the user-data location: two projects sharing them can share saves.

## Boundary / implication

The independent-process reopen is supported for a deliberately shared project identity and run-local absolute XDG directory. Run isolation depends on preserving that exact identity and XDG root between writer and reader; a unique identity or fresh XDG root for the reader creates an expected missing-file failure. Conversely, reusing an identity and XDG root shares user data across separate project roots. The runner's per-run unique `config/name` and absolute run-local XDG root are important safety controls and must remain applied to both process invocations. Never run this probe against real user or production app data. This does not test machine restart durability, power-loss behavior, tamper detection, concurrent writers, or platform portability.

Evidence JSON SHA-256: `0058d01a49cfe24862257670be9eb0f33286d8d4c4119352a4ca7897f840866e`.
