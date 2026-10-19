# r104-E3 mutations — `corpus/fixtures/res_uid_s03.gd`

Seat KEY=E3. Delivered fixture sha256
`7a5d29d0c284ca484706d5886f7a996149004a61f907e0014006e44b4c30a14a` (616 lines).
Staged and run only under `/var/tmp/r104-E3/mut*`; the repo fixture was never edited by a
mutant run. Each mutant is a single-token edit, applied to a scratch copy.

## Row tuples to register (orchestrator applies; exact)

Insertion point: after the other r104 `res_uid_*` rows, contiguous with the family.
`expected_errors` EMPTY for all five (the fixture prints no `ERROR:` line and 0 B stderr;
the nested child's engine noise is redirected to a scratch log, never echoed).

```python
    # r104 — C1: res_uid UID-cache lattice, seat E3 (.import remap resolution).
    ('res_uid_s03_import_remap_resolution', 'res_uid_s03.gd', ["--arm=resolve"], 0,
     'PASS res_uid_s03 resolve exists_source=true load_class=Resource load_name=s03_dest load_path=res://asset.png has_cached=true exists_import_file=false import_parse_err=0 import_dest=res://gen/dest.tres import_type=Resource import_uid=<none> dest_exists=true dest_class=Resource dest_name=s03_dest dest_path=res://gen/dest.tres dest_same_instance_as_source=false uid_source=-1 uid_dest=-1 typed_resource_class=Resource typed_textfile_class=Resource typed_exists_resource=true typed_exists_textfile=true'),
    ('res_uid_s03_import_remap_missing', 'res_uid_s03.gd', ["--arm=missing"], 0,
     'PASS res_uid_s03 missing m0_exists=true m0_load=Resource m0_errors=0 m1_exists=true m1_load=<null> m1_errors=3 m2_exists=true m2_load=<null> m2_errors=4 m3_exists=false m3_load=<null> m3_errors=2 m4_exists=true m4_load=<null> m4_errors=3 m5_exists=true m5_load=Resource m5_errors=0'),
    ('res_uid_s03_nonresource_refusal', 'res_uid_s03.gd', ["--arm=refuse"], 0,
     'PASS res_uid_s03 refuse e_plain=false l_plain=<null> e_dir=false l_dir=<null> e_root=false l_root=<null> e_absent=false l_absent=<null> e_import=false l_import=<null> e_user=false l_user=<null> e_subplain=false l_subplain=<null> e_noscheme=true l_noscheme=Resource uid_plain=-1 uid_absent=-1 uid_dir=-1 uid_root=-1 uid_import=-1'),
    ('res_uid_s03_remap_load_cache', 'res_uid_s03.gd', ["--arm=cache"], 0,
     'PASS res_uid_s03 cache reuse_default_identity=true reuse_explicit_identity=true replace_identity=true ignore_identity=false has_cached=true ignore_name=s03_dest ignore_path=res://asset.png cached_name=s03_dest retarget_load_name=s03_other cached_name_after_retarget=s03_dest'),
    ('res_uid_s03_uid_cache_authority', 'res_uid_s03.gd', ["--arm=uidcache"], 0,
     'PASS res_uid_s03 uidcache uid_source=1311768467294899695 uid_text=uid://sxovuchqei7p uid_expected=1311768467294899695 exists=true load_class=Resource load_name=s03_dest import_uid_field=<none>'),
```

`cases_integrity` / floor-gate prefix: `res_uid_s03_` (same shape as the sibling
`res_uid_s01/s02/s04` rows).

## Mutants (all must reject — measured, 6/6)

| id | single-token edit | arm | measured verdict |
|---|---|---|---|
| M1 | `GOOD_IMPORT` loses `path="res://gen/dest.tres"` | resolve | exit 1 `FAIL … assertion_load_class_want=Resource_got=<null>` |
| M2 | refuse arm's `"plain"` case -> `res://asset.png` | refuse | exit 1 `FAIL … assertion_e_plain_want=false_got=true` |
| M3 | `.godot/uid_cache.bin` staged as `.godot/uid_cache.bin.off` | uidcache | exit 1 `FAIL … assertion_uid_source_want=1311768467294899695_got=-1` |
| M4 | `"m1": ["true", "<null>", 3]` -> `…, 0]` (vacuity) | missing | exit 1 `FAIL … assertion_m1_errors_want=0_got=3` |
| M5 | child `RETARGET` path -> `res://gen/dest.tres` | cache | exit 1 `FAIL … assertion_retarget_load_name_want=s03_other_got=s03_dest` |
| M6 | child's terminal marker renamed (gate's own comparison kept) | resolve | exit 1 `FAIL … reason=child_incomplete_rc=0` |

M4 proves the per-variant `ERROR:` count column is genuinely bound rather than vacuous.
M6 proves the child-completeness gate (`CHILD <arm> done`) is real and independent of the
child's exit code. Exact commands:

```
RES_UID_ROOT=/var/tmp/r104-E3/mutroot/<id> godot --headless --path /var/tmp/r104-E3/mut/<id> \
  --script res://res_uid_s03.gd -- --arm=<arm>
```

## Notes for the verifier

- The fixture is **not** sensitive to `RES_UID_ROOT`: with the env var unset it falls back to
  `user://res_uid_s03` and reproduces all five receipts byte-identically (measured).
- All five PASS lines contain no host path, digest, RID or object id, so they may be pinned
  whole. If a verifier prefers an unpinned tail, `import_dest`/`ignore_path`/`load_path` are
  the only `res://`-bearing values and they are project-relative constants.
- Timing: 1.61–1.70 s per arm (one nested child each) at load 10.9 — well inside the 8 s bound.
- The `uidcache` arm hand-authors `.godot/uid_cache.bin`. If a future engine changes that
  internal format the arm fails closed on `assertion_uid_source…`, which is the intended
  detection, not a flake.
