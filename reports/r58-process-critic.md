# Round 58 process-independence critic

## Scope and method

Read-only review of the round-57 save fixture/runner and the declared r58 claim. I made scratch-only scripts and ran Godot 4.7.2 directly; no tracked source was changed. Scratch is `corpus/live/r58-process-critic/`.

## Independent-process check

The scratch writer and reader are separate `godot --headless --path <same copied project> --script ...` invocations, with the same absolute `XDG_DATA_HOME` (`.../r58-process-critic/xdg-data`) and same `config/name=MechanicOneShotTest`. Writer exits 0 and reports PID 3205860; reader exits 0 and reports PID 3205911. Both report the exact same globalized `user://r58.json` path under this scratch XDG tree. Reader script contains only `FileAccess.READ`, JSON parse, and equality assertion; it has no write path. Writer closes the file before exiting. Thus this direct reproduction does not depend on in-process state and does not contaminate pre-existing user data.

The persisted bytes were `{"enabled":true,"inventory":["key","map"],"profile":{"level":7.0,"name":"Ada"}}` (79 bytes; SHA-256 `00dc69a766693c198e0849b5fe4045524e97f9f91c13aaf52ee7cb69c4a9022e`). The reader verified the nested dictionary/array/string/float/bool structure.

## Negative

A distinct fresh reader invocation with `--missing` attempts only `user://missing.json`; it exits 2 with exact `ERROR: R58 REJECT missing=user://missing.json`. It cannot pass by observing the positive file. This supports a causal missing-file rejection. It does not test wrong-but-valid JSON values or corrupted content; the existing r57 malformed-JSON negative is a separate same-process test and must not be represented as a two-process negative.

## Critic findings / boundaries

- Direct scratch evidence supports separate OS process invocations and an independent reader for the positive file, plus an independent missing-file rejection.
- For the integrated battery, inspect the actual runner path: the two launches must each be separate subprocess calls; share the same *absolute* run-local XDG directory and copied project identity; and ensure the reader is passed no writer-mode/positive-fixture branch. Distinct command invocations alone are insufficient if the reader silently rewrites/reconstructs the expected file.
- A missing-file negative is adequate for the stated “wrong/missing” disjunction, but do not claim wrong-value validation unless that is separately measured. Retain both processes’ commands, PIDs, exits, stdout/stderr, and reader path in raw evidence. Verify user data is under the run scratch, not the default home directory.
- This demonstrates only reopen and structure verification after orderly writer exit. It says nothing about power-loss durability, fsync/atomicity, arbitrary corruption detection, production persistence, or other platforms.

## Scratch artifacts

`writer.json`, `reader.json`, `negative-missing.json` preserve raw command/output/exit records. Scratch fixture scripts and isolated project are under `project/`; all generated user data is under `xdg-data/`.
