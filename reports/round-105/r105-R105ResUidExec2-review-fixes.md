# r105 executor correction receipt — final reviewer findings

## Files changed

- `corpus/fixtures/run_battery.py`
- `corpus/fixtures/res_uid_s01.gd`
- `corpus/lessons/r105-res-uid-isolation.md`

The other UID fixtures and both sibling R105 fixtures remain unchanged.

## Fixes and evidence

- The shared probe now compares two phases: **all 8 re-admitted rows on one clean shared project** (all pass; no UID cache before or after), then the same rows on a separate project seeded by the actual `export_readiness` CASES row. The probe retains the clean and seeded rows’ outputs and verdicts, plus the writer’s case, script, verdict, output, and cache presence.
- Forward and reversed shared controls both passed. The seeded phase reproduced `Unrecognized UID` / cache-signature mismatches in `res_uid_path`, `res_uid_missing`, and `res_uid_s01_diag`; the corresponding isolated rows passed. The clean shared phase passed 8/8 in both orders, so **no UID-row-to-UID-row leakage was observed** in that cache-absent control.
- `append_result=False` now suppresses the export unrelated-error meta append. The control run with `--probe-unrelated-error` recorded 11 unique result names; the ordinary CASES export row still emitted its single meta row.
- `res_uid_s01_createid` now pins `cfp_paths_differ=true`. A scratch constant-return mutant produced `cfp_paths_differ=false` and was rejected by the runner.
- Counts remain **29 ResUID rows, 600 CASES**. `r104_res_uid_count_floor` remains; the requested diff scan found no removed CASES tuples.
- `python3 -m py_compile corpus/fixtures/run_battery.py` completed cleanly. No full battery was run; the L1 gate remains pending.

Forward and reversed targeted runs each passed all 29 ResUID and 7 R105 rows:

```text
Forward:  DEV_COUNTS res_uid=29 r105=7 total=36
          DEV_FAILURES []
          DEV_DUPLICATE_CASES []
          DEV_R105_MAX_SECONDS 4.502

Reversed: DEV_COUNTS res_uid=29 r105=7 total=36
          DEV_FAILURES []
          DEV_DUPLICATE_CASES []
          DEV_R105_MAX_SECONDS 4.493
```

All seven R105 rows were under 8 seconds, and `receipt_shape_flag` returned `[]` for each. The shared-control forward and reversed runs both had `clean_shared_all_pass=True`, a passing `export_readiness` cache writer, and no duplicate result names. The constant-return mutant check reported `DEV_CONSTANT_RETURN_MUTANT_REJECTED True`.

The corrected expected full receipt count is **621**: 600 CASES plus 21 unique meta rows. The previous 622 count included the duplicate export-meta row and is pre-fix evidence; the lesson records this correction.

## `source_blobs`

`verdicts.json` now carries a top-level `source_blobs` mapping, computed from the actual source bytes before staging. Changed source blob hashes:

```text
corpus/fixtures/run_battery.py  ee1b439791787128313549d428714192a6825ec2
corpus/fixtures/res_uid_s01.gd  a85f10f28abcd72d2b32c9c19bd5cb28d6ea1aac
```

The remaining source hashes and full retained evidence are in `corpus/lessons/r105-res-uid-isolation.md`. That lesson preserves the earlier receipts as history and appends the corrected control interpretation and post-review receipts.

## L1 full-battery commands

Run serially, first forward and then reversed:

```sh
timeout --signal=TERM --kill-after=2s 3500s python3 /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/game-dev-2d-shokunin/corpus/fixtures/run_battery.py --godot /usr/bin/godot --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --res-uid-order forward --probe-res-uid-shared

timeout --signal=TERM --kill-after=2s 3500s python3 /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/game-dev-2d-shokunin/corpus/fixtures/run_battery.py --godot /usr/bin/godot --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --res-uid-order reversed --probe-res-uid-shared
```

**Writes outside the lane worktree:** only `/var/tmp/gd2d-r105/R105ResUidExec2/` for temporary drivers, runner copies, cache, and targeted-run artifacts. No commits were made. LSP was unavailable in the exposed tool inventory.
