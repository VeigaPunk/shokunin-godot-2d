# r104-E2 battery registration (mutation content — orchestrator applies)

Seat KEY=E2. Target: `corpus/fixtures/run_battery.py` (this seat MUST NOT edit it).
Fixture: `corpus/fixtures/res_uid_s02.gd` (9 arms). All 9 arms validated `rc=0`, one `PASS`
line each, byte-identical across two fresh runs — see `reports/round-104/r104-E2.md` §3.

## 1. CASES rows — append before the closing `]` at line 1759

Tuple shape is `(name, script, flags, expected_exit, signature)` (line 18 comment). Signature
is the arm's full PASS line, which is process-independent by construction.

```python
    # r104-E2: ResourceLoader load-cache identity / cache_mode busting / post-mutation
    # reload classes.  Every arm prints exactly one PASS line; the only engine ERROR
    # output is the deleted arm's 3-line block (allowlisted below).
    ('res_uid_s02_reuse', 'res_uid_s02.gd', ["--arm=reuse"], 0,
     'PASS res_uid_s02 reuse cached=true has_cached=true reuse_same=true explicit_reuse_same=true ref_same=true iid_stable=true path=true'),
    ('res_uid_s02_ignore', 'res_uid_s02.gd', ["--arm=ignore"], 0,
     'PASS res_uid_s02 ignore distinct=true cache_kept=true ref_kept=true two_distinct=true path_kept=true reuse_after_is_orig=true has_cached=true content=v2'),
    ('res_uid_s02_replace', 'res_uid_s02.gd', ["--arm=replace"], 0,
     'PASS res_uid_s02 replace same=true refreshed=v2 alias_refreshed=v2 reuse_after_same=true cached_now=v2'),
    ('res_uid_s02_deep', 'res_uid_s02.gd', ["--arm=deep"], 0,
     'PASS res_uid_s02 deep igd_distinct=true igd_cache_kept=true igd_ref_is_orig=true rpd_same=true reuse_is_rpd=true'),
    ('res_uid_s02_bust', 'res_uid_s02.gd', ["--arm=bust"], 0,
     'PASS res_uid_s02 bust stale_reuse=v1 stale_same=true repl=v2 repl_same=true alias_after_repl=v2 after_reuse=v2 ign_fresh=v2'),
    ('res_uid_s02_deleted', 'res_uid_s02.gd', ["--arm=deleted"], 0,
     'PASS res_uid_s02 deleted removed=true reuse_stale=v3 reuse_same=true repl_stale=v3 repl_same=true repl_evicted=false ign_null=true cached_deleted_exists=true never_exists=false has_cached=true'),
    ('res_uid_s02_resdir', 'res_uid_s02.gd', ["--arm=resdir"], 0,
     'PASS res_uid_s02 resdir wrote=true reuse_same=true ign_distinct=true ign_path_kept=true repl_same=true repl_refreshed=v2 alias_refreshed=v2'),
    ('res_uid_s02_xproc_seed', 'res_uid_s02.gd', ["--arm=xproc_seed"], 0,
     'PASS res_uid_s02 xproc_seed wrote=v1 loaded=v1 cached=true'),
    ('res_uid_s02_xproc_read', 'res_uid_s02.gd', ["--arm=xproc_read"], 0,
     'PASS res_uid_s02 xproc_read fresh_first=v1 same_in_process=true rewrite_reuse=v1 repl=v2'),
```

`xproc_seed` must be ordered **before** `xproc_read` and both must share the default
`user://` (the battery does not set `XDG_DATA_HOME` for this script, so both inherit the
scratch project's app_userdata — same directory, same order). If a future edit ever assigns
this script a per-case `XDG_DATA_HOME`, the pair breaks: keep them on the default env.

## 2. `expected_errors` entries — extend the dict starting at line 2336

`expected_errors` starts as `()` and is reassigned from the `{...}.get(name, ())` dict. Add
these 9 keys. The `deleted` entries are **exact-line** (no trailing comma): the shipped
prefix clause is `stripped.startswith(allowed) and stripped.count("ERROR:") == 1` and each
line already ends in `.`, so a comma-suffixed entry can never match.

```python
                "res_uid_s02_reuse": (),
                "res_uid_s02_ignore": (),
                "res_uid_s02_replace": (),
                "res_uid_s02_deep": (),
                "res_uid_s02_bust": (),
                "res_uid_s02_deleted": (
                    "ERROR: Cannot open file 'user://res_uid_s02/v1.tres'.",
                    "ERROR: Failed loading resource: user://res_uid_s02/v1.tres.",
                    "ERROR: Error loading resource: 'user://res_uid_s02/v1.tres'.",
                ),
                "res_uid_s02_resdir": (),
                "res_uid_s02_xproc_seed": (),
                "res_uid_s02_xproc_read": (),
```

## 3. r103 receipt-shape gate tables (lines 1775+)

The gate is floor-not-ceiling: new rows must be **declared** or they fail closed.

- `RECEIPT_ANCHOR_MULTIPLICITY` — add `res_uid_s02_<arm>: 1` for all 9 arms. Each arm prints
  its PASS line exactly once and the anchor substring occurs exactly once in the merged
  output (the engine ERROR block does not contain the anchor).
- `RECEIPT_MULTI_PASS_GRAMMAR` — **no entry** for any of the 9 (single PASS line per arm).
- `RECEIPT_SHAPE_DERIVED_EVIDENCE` — not applicable (no derived/export rows).

## 4. Allowlist proof (why these entries are safe)

Replicated the shipped `classify_process` (lines 2093–2110) and drove it with the captured
merged output of the `deleted` arm (`/var/tmp/r104-E2/merged_deleted.out`):

```
ALLOWLISTED (must be True) = True
  no_allowlist             verdict = False
  foreign_error            verdict = False
  dup_allowlisted          verdict = True
  same_line_prefix_spoof   verdict = False
  wrong_value              verdict = True
  extra_pass_line          verdict = True
  wrong_exit               verdict = False
```

The allowlist admits the real arm while still rejecting a foreign ERROR line and a same-line
prefix spoof. **Three negatives survive at the verdict layer** — `dup_allowlisted`,
`wrong_value`, `extra_pass_line` — and are routed to C2/G0/G2 (they are `receipt_shape_flag`
/ anchor-multiplicity / multi-pass-grammar shapes, not allowlist shapes).

## 5. Follow-ups for the orchestrator

- A hard-coded CASES count, if one exists anywhere (battery or docs), must grow by 9. No
  literal `552` was found in `run_battery.py`; `len({c[0] for c in CASES}) == len(CASES)`
  (line 4443) is a uniqueness check and passes automatically.
- The fixture writes `res://r104_s02_root.tres` during the `resdir` arm and removes it again;
  the `resdir` receipt's `wrote=true` token is the only witness that the write succeeded.
  Verified: no leftover file in the harness root after any arm.
