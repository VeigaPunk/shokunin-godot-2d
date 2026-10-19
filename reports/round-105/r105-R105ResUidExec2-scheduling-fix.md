# r105 M32 correction — executor final output

## M32 fix

**Files changed:** `corpus/fixtures/run_battery.py` and the appended correction in `corpus/lessons/r105-res-uid-isolation.md`. No other code or pins changed; no commit was made.

The shared-probe helper now runs immediately after the last ResUID CASES row, before the R105 cases and descendant tail. This keeps its export writer/readers out of the interval between `descendant_pipe_detached_control` and the liveness meta probe.

## Targeted regression

The bounded selected run exercised the shared probe, save-process and crash controls, and the descendant tail in one runner path:

```text
DEV_COUNTS res_uid=8 r105=0 total=22
DEV_FAILURES []
DEV_DUPLICATE_CASES []
DEV_TAIL_GUARDS {
  'probe_save_independent_process': 'PASS',
  'probe_spontaneous_crash_classification': 'PASS',
  'probe_descendant_pipe_eof': 'PASS',
  'probe_descendant_signature_spoof': 'PASS',
  'probe_descendant_error_spoof': 'PASS',
  'probe_while_live_signature_gate': 'PASS'
}
DEV_PIPE_DETACHED_DESCENDANT_ALIVE True
```

`probe_descendant_pipe_eof` had all seven discriminations true, including `detached_descendant_orphaned_alive=true`. The shared probe also passed: all eight clean-shared rows passed with no UID cache before or after; the actual `export_readiness` writer created the cache, and the seeded phase reproduced the specific UID class in `res_uid_path`, `res_uid_missing`, and `res_uid_s01_diag`.

A broader **filtered** attempt that continued through `probe_error_clause_surface` reported `prior_meta_rows_stable_29_discriminations=true`; its overall result was red only for omitted-family count/integrity checks (`r103_export_div_count_floor`, `r104_export_prod_count_floor`, `r105_case_count_floor`, `cases_integrity`). The final targeted regression stops after the relevant tail guards; no production gate was weakened.

## Receipt and source binding

- `PYTHONPYCACHEPREFIX=/var/tmp/gd2d-r105/R105ResUidExec2/pycache python3 -m py_compile corpus/fixtures/run_battery.py` completed cleanly.
- `verdicts.json` now includes the top-level `source_blobs` key, with Git blob SHA-1s computed from the actual eight source files before staging.
- Current changed source blobs:
  - `corpus/fixtures/run_battery.py`: `bbc4e9f96915317047373f1b9fbc7f125793de26`
  - `corpus/fixtures/res_uid_s01.gd`: `a85f10f28abcd72d2b32c9c19bd5cb28d6ea1aac`
- The updated lesson records the full source-blob mapping and targeted run artifacts.

The corrected expected full receipt count is **621** (600 CASES plus 21 unique meta rows); the previous 622 count included the duplicate export-meta row. **No full battery was run**, per the parent’s instruction.

## L1 full-battery command

Run serially once with each order after integration:

```sh
timeout --signal=TERM --kill-after=2s 3500s python3 /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/game-dev-2d-shokunin/corpus/fixtures/run_battery.py --godot /usr/bin/godot --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --res-uid-order forward --probe-res-uid-shared

timeout --signal=TERM --kill-after=2s 3500s python3 /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/game-dev-2d-shokunin/corpus/fixtures/run_battery.py --godot /usr/bin/godot --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --res-uid-order reversed --probe-res-uid-shared
```

All out-of-worktree writes were under `/var/tmp/gd2d-r105/R105ResUidExec2/` for temporary drivers and run artifacts. LSP was unavailable in the exposed tool inventory.
