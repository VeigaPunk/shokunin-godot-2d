# r105 seat report — R105ResUidExec2 (executor (re-dispatch; R105ResUidExec died resource_exhausted after 31m40s, no writes))

Verbatim final output of L2 `W2RoundGameDev2d.R105ResUidExec2` (round 105, batched swarm; transcript `history://W2RoundGameDev2d.R105ResUidExec2` is session-scoped and not evidence — this file is).

---

## Files changed

- `corpus/fixtures/run_battery.py`
- `corpus/fixtures/res_uid_s01.gd`
- `corpus/lessons/r105-res-uid-isolation.md`

The other listed UID fixtures and both sibling R105 fixtures were left unchanged.

## Changes and evidence

- ResUID rows now run from a fresh copy of a pre-CASES project template, with a distinct `XDG_DATA_HOME` and `RES_UID_ROOT` per row. The ordinary shared scratch remains the execution path for non-ResUID rows.
- Re-admitted the seven retired rows and repaired `res_uid_s01_createid` with repeatability, ID/text round-trip, and registration invariants—no seat-specific ID constants.
- Added forward/reversed ordering, a cache-seeded shared-project probe, exact expected-error entries and per-round gates, plus the seven R105 sibling rows.
- AST counts: **29 ResUID rows** and **600 total CASES**. The R104 count-floor predicate remains; the R105 family has its own error and count gates.
- Requested diff scan: **no removed CASES tuple lines** matched `^-    \('`.
- `python3 -m py_compile corpus/fixtures/run_battery.py` completed silently with exit 0. Bytecode was directed to scratch.

Forward and reversed runs each executed 29 ResUID + 7 R105 rows serially through the runner’s `execute` path:

```text
Forward:  DEV_COUNTS res_uid=29 r105=7 total=36
          DEV_FAILURES []
          DEV_R105_MAX_SECONDS 4.594

Reversed: DEV_COUNTS res_uid=29 r105=7 total=36
          DEV_FAILURES []
          DEV_R105_MAX_SECONDS 4.849
```

All seven R105 rows were under 8 seconds in both runs; `receipt_shape_flag` returned `[]` for each, including the physics rows’ extra `REPLAY` diagnostics. `r105_tile_rid_wrongrid` emitted exactly `ERROR: Parameter "found" is null.`

The shared control passed with all eight isolated twins passing and an engine-generated UID cache present. It reproduced the specific class in `res_uid_path`, `res_uid_missing`, and `res_uid_s01_diag`. Example exact diagnostic:

```text
ERROR: Unrecognized UID: "uid://dg1qdmv0eb3ve".
```

The `s01_diag` shared receipt reported `has_cache=true` against the isolated `has_cache=false` pin. `res_uid_s02_deleted` passed with the same pinned receipt in forward and reversed isolation runs (0.883s / 0.888s); no flake was observed in those two samples.

Exact per-row timings, all shared diagnostics, commands, and run artifact paths are recorded in `corpus/lessons/r105-res-uid-isolation.md`.

## L1 full-battery command

Run this **twice, serially** after integration:

```sh
timeout --signal=TERM --kill-after=2s 7200s python3 /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/game-dev-2d-shokunin/corpus/fixtures/run_battery.py --godot /usr/bin/godot --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --res-uid-order forward --probe-res-uid-shared
```

The targeted runs stopped before full-battery meta gates; those remain for the L1 gate. The existing cache-conditional `r96_scene_io_uid` entry was not changed. LSP was unavailable in the exposed tool inventory.

**Writes outside the lane worktree:** only `/var/tmp/gd2d-r105/R105ResUidExec2/` (temporary driver, copied runner, bytecode cache, and run artifacts). No other out-of-scope paths were written.
