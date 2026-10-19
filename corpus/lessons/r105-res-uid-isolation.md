# Round 105 — ResourceUID row isolation

verified-at: 2026-10-19 (Godot 4.7.2.stable.arch_linux.ed1daf0bf, Linux x86-64)

## Mechanism

[obs] Before this change, `run_battery.py` staged one project at `run_dir/scratch`; each fixture process used that same project. ResUID processes received the same run-wide `run_dir/xdg-data`, not one XDG root per row. The R104 retirement comment identified shared `.godot/uid_cache.bin` state as the failure mechanism; its claim that the seats were isolated did not match the runner's actual XDG setup.

[obs] The runner now snapshots an immutable `res-uid-template` after the normal scratch staging and setup, before any CASES execute. Every `res_uid.gd` / `res_uid_s01..s04.gd` row gets a fresh `res-uid-isolated/<case>` copy of that template, a case-specific `XDG_DATA_HOME`, and a case-specific `RES_UID_ROOT`. This leaves the ordinary `scratch` path unchanged for non-ResUID rows. The shared-control probe has a separate project copy and shared XDG/root paths.

[obs] `probe_res_uid_shared` prepares its dedicated shared project with the runner's existing `__godot_export__` execution path so the project has an engine-generated `.godot/uid_cache.bin`, then runs the eight re-admitted rows serially against that same project and shared XDG/root. The probe is green only when all eight isolated twins pass, the cache exists, and at least one shared row fails in the specific `Unrecognized UID` or UID-mismatch class. A generic shared failure is not enough.

[obs] The existing `r96_scene_io_uid` expected-error entry and fixture pin were not changed. Its runner comment says the diagnostic is conditional on `.godot/uid_cache.bin`; it still executes against the ordinary shared scratch, not `res-uid-template`. The targeted runs below did not execute `r96_scene_io_uid`. [inf] In a full battery, its prior export/cache context can still activate that allowlist; the row's cache dependency remains visible rather than being silently erased by the ResUID isolation.

[obs] `res_uid_s01_createid` no longer prints or compares the seat constants `8476142776992359011` / `4163091229239537790`. It checks repeat-call stability, `text_to_id(id_to_text(id)) == id`, and `has_id()` registration independently for both `res://` and `user://` paths, plus the existing distinct/unregistered `create_id()` check.

## CASES before and after

The required AST count command:

```sh
python3 -c "import ast;t=ast.parse(open('corpus/fixtures/run_battery.py').read());print([sum(e.elts[0].value.startswith('res_uid_') for e in n.value.elts) for n in ast.walk(t) if isinstance(n,ast.Assign) and any(getattr(x,'id',None)=='CASES' for x in n.targets) and isinstance(n.value,ast.List)])"
```

- Before (R104-reviewed baseline): `21` ResUID rows; `585` total CASES.
- After (measured AST): `[29]` ResUID rows; `600` total CASES (`585 + 8` re-admitted/fixed ResUID rows `+ 7` R105 sibling rows).
- The seven retired cases and repaired createid case were added without changing any prior CASES signature. The new createid pin is derived from the independent in-process invariants above.

## Dev receipts

Fixture rows were serial and bounded by the runner's 8-second per-row timeout; the shared probe's export cache seed used the runner's existing 60-second export timeout. The outer driver used `timeout --signal=TERM --kill-after=2s 300s`. A throwaway driver under `/var/tmp/gd2d-r105/R105ResUidExec2/` imported a copied runner, selected only the 29 ResUID plus seven R105 rows for the forward/reversed runs, and returned after those fixture executions (before full-battery meta gates). Each selected row still used the runner's own `execute` path. The shared-control run selected only the eight re-admitted rows and enabled the runner's opt-in probe.

Forward command:

```sh
timeout --signal=TERM --kill-after=2s 300s python3 /var/tmp/gd2d-r105/R105ResUidExec2/dev_runner.py forward /var/tmp/gd2d-r105/R105ResUidExec2/runs-forward-final 0 all
```

Tail:

```text
DEV_COUNTS res_uid=29 r105=7 total=36
DEV_FAILURES []
DEV_R105_MAX_SECONDS 4.594
DEV_R105_RECEIPT_SHAPES {'r105_tile_rid_exact': [], 'r105_tile_rid_chunked': [], 'r105_tile_rid_kinematic': [], 'r105_tile_rid_wrongrid': [], 'r105_phys_replay_digest': [], 'r105_phys_replay_inproc': [], 'r105_phys_replay_perturb': []}
```

Reversed command:

```sh
timeout --signal=TERM --kill-after=2s 300s python3 /var/tmp/gd2d-r105/R105ResUidExec2/dev_runner.py reversed /var/tmp/gd2d-r105/R105ResUidExec2/runs-reversed-final 0 all
```

Tail:

```text
DEV_COUNTS res_uid=29 r105=7 total=36
DEV_FAILURES []
DEV_R105_MAX_SECONDS 4.849
DEV_R105_RECEIPT_SHAPES {'r105_tile_rid_exact': [], 'r105_tile_rid_chunked': [], 'r105_tile_rid_kinematic': [], 'r105_tile_rid_wrongrid': [], 'r105_phys_replay_digest': [], 'r105_phys_replay_inproc': [], 'r105_phys_replay_perturb': []}
```

The measured R105 row timings (seconds, forward / reversed) were:

| Row | Forward | Reversed |
| --- | ---: | ---: |
| `r105_tile_rid_exact` | 0.626 | 0.973 |
| `r105_tile_rid_chunked` | 0.591 | 0.984 |
| `r105_tile_rid_kinematic` | 0.629 | 0.950 |
| `r105_tile_rid_wrongrid` | 0.591 | 0.930 |
| `r105_phys_replay_digest` | 2.624 | 2.880 |
| `r105_phys_replay_inproc` | 4.469 | 4.849 |
| `r105_phys_replay_perturb` | 4.594 | 4.562 |

[obs] All seven are below 8 seconds in both runs. `receipt_shape_flag` returned `[]` for all seven; the extra `REPLAY ...` diagnostics on the physics rows were accepted without weakening the shape gate. `r105_tile_rid_wrongrid` emitted exactly one `ERROR: Parameter "found" is null.` line, followed by the engine backtrace, and passed under that allowlist.

Shared-control command:

```sh
timeout --signal=TERM --kill-after=2s 300s python3 /var/tmp/gd2d-r105/R105ResUidExec2/dev_runner.py forward /var/tmp/gd2d-r105/R105ResUidExec2/runs-shared-final 1 rejoined
```

Tail:

```text
PASS probe_res_uid_shared: reproduced_rows=['res_uid_path', 'res_uid_missing', 'res_uid_s01_diag']
DEV_COUNTS res_uid=8 r105=0 total=9
DEV_FAILURES []
```

[obs] All eight isolated twins passed; the export-seeded shared project had `uid_cache.bin`; the probe passed with three reproducing rows. Exact shared-run diagnostics were:

- `res_uid_path`:
  - `ERROR: Unrecognized UID: "uid://dg1qdmv0eb3ve".`
  - `ERROR: Unrecognized UID: "uid://dt730spfkuh22".`
  - `ERROR: Unrecognized UID: "uid://c37t0ym5hr456".`
- `res_uid_missing`:
  - `ERROR: Unrecognized UID: "uid://colb8ryp2m2t".` (twice)
  - `ERROR: Unrecognized UID: "uid://i6bg5pc0581p".`
  - `ERROR: Unrecognized UID: "uid://bqk3m5n7qar1".` (twice)
- `res_uid_s01_diag` printed `PASS res_uid_s01 diag ... has_cache=true`; its isolated pin is `has_cache=false`, so the shared row failed on that explicit cache-state signature mismatch.

[obs] `res_uid_s02_deleted` passed with the same pinned receipt in both isolated orders (`0.883s` forward, `0.888s` reversed). No flake was observed in these two isolated samples; this is not a broader flake-rate claim.

## Gate

### Candidates

- Re-admit `res_uid_path`, `res_uid_collide`, `res_uid_cache`, `res_uid_missing`, `res_uid_s01_collide`, `res_uid_s01_diag`, and `res_uid_s02_deleted` from the R104 W4 patch.
- Repair and re-admit `res_uid_s01_createid` without seat-specific ID constants.
- Register the four TileMapLayer body-RID arms and three physics replay arms supplied by the sibling seats.

### Admitted

- All 29 ResUID CASES rows, including the eight re-admitted/fixed rows, passed in forward and reversed order; `r104_res_uid_count_floor` remains in place.
- All seven R105 sibling rows passed in both order runs. The wrong-RID diagnostic has an exact expected-error entry and `r105_expected_errors_all_matched`; the R105 family also has a seven-row count floor.
- The shared control passed only after it reproduced the cache-dependent `Unrecognized UID` / explicit cache-state mismatch class while the same eight isolated rows passed.

### Rejected

- `res_uid_s02_bust` remains unregistered: the existing R104 comment records `FAIL reason=post_mutation_reload_class_mismatch`.
- `res_uid_s02_xproc_read` remains unregistered: the existing R104 comment records `FAIL reason=cross_process_or_l5_law_mismatch`.
- `res_uid_w07.gd` remains unregistered because six of its eleven arms emit two PASS lines, which the current receipt-shape gate rejects as `unaccounted_pass_lines`; its census/api2 coverage is superseded by `res_uid_s01`.

## Residual unknowns

[unk] Stability beyond the two isolated `res_uid_s02_deleted` order runs and portability beyond this Godot build/host were not measured.

[unk] The targeted dev driver intentionally stopped before full-battery meta gates and did not execute the ordinary battery's `r96_scene_io_uid` row. The L1 full-battery run remains required after integration.

## L1 full-battery replay (appended, 2026-10-19)

The dev-driver paths above are development history, **not closure evidence**.
Persistent closure evidence is `reports/round-105/r105-battery-receipts.json`,
extracted by `reports/round-105/r105-receipts.py`. The full command (run twice,
serial, `ORDER=forward` then `ORDER=reversed`, from the lane root):

```sh
timeout --signal=TERM --kill-after=2s 3500s python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --res-uid-order "$ORDER" --probe-res-uid-shared
```

[obs] Both runs: exit 0; verdicts JSON 622/622 PASS, 0 FAIL; 29/29 res_uid and
7/7 r105; every focus signature byte-matched output. Order lists are exact
reverses. Shared probe PASS in both, reproducing the mismatch in `res_uid_path`,
`res_uid_missing`, `res_uid_s01_diag`. Both meta gates pass (shape: 602 audited,
0 flags; evasion: 10 shapes, 6 flagged, 0 probe flags). Ordinary
`r96_scene_io_uid` also PASS; its prior expected string was not changed.
`s02_deleted` now has four green isolation samples (two dev + two full), not a
claim that all future host/builds are flake-free.

Blobs held unchanged across both full runs and subsequently committed:
runner `5ec364bf908e1da436a91cc752bc95e79e47eb99`;
createid fixture `4ed6440c605b9e9f4d55bed0e16fc2cb00a3aa83`;
tile-RID `b861d62208982f7998d1f7e0fdbe51441591a629`;
replay `e646d1264231d755a6ef3f4016a163d1d753f61c`.

## Reviewer correction and updated evidence (2026-10-19)

The earlier seeded-only control above is historical and superseded. Seeding the
project before the first ResUID row demonstrated a cache-regime flip, not
UID-row-to-UID-row leakage. The current probe makes the intervention explicit:

1. It runs all eight re-admitted rows serially in a clean shared project copied
   from the same pre-CASES template, with one shared XDG root and one shared
   `RES_UID_ROOT`. It records every row's output and verdict, and requires all
   eight to pass with no UID cache present at start.
2. It copies a separate fresh project, invokes the actual `export_readiness`
   CASES tuple (`case=export_readiness`, `script=__godot_export__`) as the cache
   writer with `append_result=false`, records its output/verdict/cache presence,
   then runs the same eight rows in order with separate shared XDG/root paths.
   The probe requires the writer to pass and create `uid_cache.bin`, isolated
   twins to pass, and at least one seeded reader to reproduce the specific
   `Unrecognized UID` / signature-mismatch class.

[obs] Forward and reversed shared-control runs both passed. In each, the clean
shared project had no `uid_cache.bin` before or after the eight rows; all clean
rows passed. The actual export writer passed and produced the cache in the
separate seeded project. Seeded rows `res_uid_path`, `res_uid_missing`, and
`res_uid_s01_diag` reproduced the class while their isolated twins passed.
The full raw rows, including output/verdicts, are retained in the
`probe_res_uid_shared` result record. This establishes the export-writer to
cache-present-reader regime difference; no within-ResUID-row leakage was
observed across these eight rows in the clean shared project.

[obs] The export-meta uniqueness control ran with `--probe-unrelated-error`:
the selected control had nine CASES rows (export writer + eight readers), one
`probe_unrelated_error_export_readiness`, and one `probe_res_uid_shared`, for
11 unique result names. The `append_result=false` writer seed added no duplicate
meta row; the ordinary CASES export writer still emitted its one meta probe.
With 600 CASES and the same 21 distinct meta names, the corrected full-battery
receipt count is **621**, not the pre-fix 622.

[obs] A scratch constant-return mutant replacing all four
`create_id_for_path` observations with `0` emitted
`cfp_paths_differ=false`; the runner verdict was `FAIL` against the admitted
`cfp_paths_differ=true` signature. The dev driver reported
`DEV_CONSTANT_RETURN_MUTANT_REJECTED True`.

The prior L1 replay block above describes pre-correction source blobs and
receipt count. It is retained as historical evidence, not post-fix closure.
Per the parent gate instruction, no full battery was run after these changes;
the L1 must rerun it to create the new source-bound receipt summary.

## Post-review dev receipts and source binding (appended, 2026-10-19)

Updated serial selected-case runs (29 ResUID + 7 R105):

```sh
timeout --signal=TERM --kill-after=2s 300s python3 /var/tmp/gd2d-r105/R105ResUidExec2/dev_runner.py forward /var/tmp/gd2d-r105/R105ResUidExec2/runs-forward-review 0 all
timeout --signal=TERM --kill-after=2s 300s python3 /var/tmp/gd2d-r105/R105ResUidExec2/dev_runner.py reversed /var/tmp/gd2d-r105/R105ResUidExec2/runs-reversed-review 0 all
```

Both tails: `DEV_COUNTS res_uid=29 r105=7 total=36`, `DEV_FAILURES []`,
`DEV_DUPLICATE_CASES []`; receipt-shape flags were empty for all seven R105
rows. R105 max row times were 4.502s forward and 4.493s reversed.

Two-phase shared control, run in both orders with the ordinary
`--probe-unrelated-error` option active:

```sh
timeout --signal=TERM --kill-after=2s 300s python3 /var/tmp/gd2d-r105/R105ResUidExec2/dev_runner.py forward /var/tmp/gd2d-r105/R105ResUidExec2/runs-shared-review 1 control
timeout --signal=TERM --kill-after=2s 300s python3 /var/tmp/gd2d-r105/R105ResUidExec2/dev_runner.py reversed /var/tmp/gd2d-r105/R105ResUidExec2/runs-shared-reversed-review 1 control
```

Both controls: clean shared phase PASS 8/8 with cache absent before and after;
the actual `export_readiness` writer PASSed and produced the seeded cache; the
seeded phase reproduced `res_uid_path`, `res_uid_missing`, and
`res_uid_s01_diag`; all isolated twins passed. Both had 11 unique result names
and `DEV_DUPLICATE_CASES []`; exactly one
`probe_unrelated_error_export_readiness` meta row remained (from the ordinary
CASES export row, not the `append_result=false` seed). Full row outputs and
verdicts are stored in each `probe_res_uid_shared` record.

Forward seeded lines included:

```text
ERROR: Unrecognized UID: "uid://8pvlcjun842l".
ERROR: Unrecognized UID: "uid://dfwar485vxw4n".
ERROR: Unrecognized UID: "uid://dfmqft1230v57".
ERROR: Unrecognized UID: "uid://d2cdjh634hvpd".
ERROR: Unrecognized UID: "uid://d2cdjh634hvpd".
ERROR: Unrecognized UID: "uid://i6bg5pc0581p".
ERROR: Unrecognized UID: "uid://bqk3m5n7qar1".
ERROR: Unrecognized UID: "uid://bqk3m5n7qar1".
```

Reversed seeded lines included:

```text
ERROR: Unrecognized UID: "uid://dloknbcge17uw".
ERROR: Unrecognized UID: "uid://biwgm84u2k5s0".
ERROR: Unrecognized UID: "uid://dmbbt0p2twdeo".
ERROR: Unrecognized UID: "uid://cgs2k156r5q54".
ERROR: Unrecognized UID: "uid://cgs2k156r5q54".
ERROR: Unrecognized UID: "uid://i6bg5pc0581p".
ERROR: Unrecognized UID: "uid://bqk3m5n7qar1".
ERROR: Unrecognized UID: "uid://bqk3m5n7qar1".
```

The `res_uid_s01_diag` seeded PASS line on both orders had `has_cache=true`
against its isolated `has_cache=false` signature.

The constant-return scratch mutant command:

```sh
timeout --signal=TERM --kill-after=2s 60s python3 /var/tmp/gd2d-r105/R105ResUidExec2/dev_runner.py forward /var/tmp/gd2d-r105/R105ResUidExec2/runs-createid-mutant 0 mutant
```

Tail: `DEV_FAILURES ['res_uid_s01_createid']` and
`DEV_CONSTANT_RETURN_MUTANT_REJECTED True`; the captured PASS line had
`cfp_paths_differ=false`, so it did not match the accepted pin.

The normal full-run `verdicts.json` now carries the top-level key
`source_blobs`, mapping the eight source paths below to Git blob SHA-1s computed
from their actual bytes before staging:

```text
corpus/fixtures/run_battery.py       ee1b439791787128313549d428714192a6825ec2
corpus/fixtures/res_uid.gd           4bb02839bb4622b61fc81e5ea5ea4f554921682b
corpus/fixtures/res_uid_s01.gd       a85f10f28abcd72d2b32c9c19bd5cb28d6ea1aac
corpus/fixtures/res_uid_s02.gd       295336fbb121f50616a76b5efa62d072bafb94fd
corpus/fixtures/res_uid_s03.gd       71bad141a52f8733163bd1c5ebb1148b68b479fd
corpus/fixtures/res_uid_s04.gd       d42d5839cbcfc904f6a4a3efd7ebeb8213aac346
corpus/fixtures/r105_tile_rid.gd     b861d62208982f7998d1f7e0fdbe51441591a629
corpus/fixtures/r105_phys_replay.gd  e646d1264231d755a6ef3f4016a163d1d753f61c
```

These are current source-byte identities, not evidence from a post-fix full
battery. With the duplicate export meta suppressed, the expected full receipt
count for the same 600 CASES and 21 distinct meta rows is 621. The L1 full
battery is still pending after this correction.

After tightening the clean-shared phase to require the UID cache remain absent
through all eight rows, both final control reruns passed:

```text
forward:  clean_shared_all_pass=True; cache_before=false; cache_after=false;
          cache_writer=PASS; seeded_cache=true; reproduced_rows=[res_uid_path,
          res_uid_missing, res_uid_s01_diag]; DEV_DUPLICATE_CASES []
reversed: clean_shared_all_pass=True; cache_before=false; cache_after=false;
          cache_writer=PASS; seeded_cache=true; reproduced_rows=[res_uid_s01_diag,
          res_uid_missing, res_uid_path]; DEV_DUPLICATE_CASES []
```

Artifacts: `/var/tmp/gd2d-r105/R105ResUidExec2/runs-shared-final-review/20261019T230949732056Z/selected-dev-results.json` and
`/var/tmp/gd2d-r105/R105ResUidExec2/runs-shared-reversed-final-review/20261019T231009822307Z/selected-dev-results.json`.
