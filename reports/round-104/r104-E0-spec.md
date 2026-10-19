# r104-E0-spec — C1 ResourceLoader / UID-cache lattice ROW TUPLES (seat KEY=E0-RES-LEAD)

Owner: this seat owns **`corpus/fixtures/res_uid.gd` ONLY**. This file + `r104-E0.md` are the
only repo writes. `run_battery.py` was **never executed**; no shared file edited; no worktree.

Host `uptime` = `22:29:30 up 1 day, 22:29, 1 user, load average: 3.46, 2.00, 1.80`.
Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Scratch `/var/tmp/r104-E0/` (never /tmp — EDQUOT).
Fixture sha256 **`75da874740b5ee333e6749e34bfe44946b2ba2cd5aa4a2d489f4477f408d21de`** (411 lines).
**Re-hash before splicing** — the hash above is the frozen revision the row tuples were taken from.

## Plan (5 lines)
1. Recon battery staging + `scene_io_lattice.gd:438` / `r96b_cache.gd` for the uncovered slice.
2. Scratch probes p1/p2/p3 + micro-tests n2/n3/n4/n5/n6/h9/z9: API signatures, text grammar, cache identity, `.import` remap, cross-process persistence.
3. Land `corpus/fixtures/res_uid.gd`, one arm per axis, one `PASS res_uid <arm> <k=v>…` line each.
4. Measure each arm on /var/tmp/r104-E0 (3 rounds, byte-compare); quote exact command + bytes.
5. Emit FINAL row tuples + `expected_errors` census here; fold into `r104-E0.md`.

## Battery launch shape (reproduced verbatim from `run_battery.py:2228`)

```
godot --headless --path <scratch> --script res://res_uid.gd -- --arm=<arm>
```
8 s per-row bound (`run_battery.py:1930`); the scratch project is `corpus/fixtures` minus
`run_battery.py` and dot-entries (`:2043-2049`), with `config/name` rewritten to
`MechanicOneShotTest-<stamp>` (`:2052`).

## Measured wall time (3 rounds, host load ~3.5)

| arm | r1 ms | r2 ms | r3 ms | vs 8 s bound |
|---|---|---|---|---|
| text | 792 | 843 | 772 | 9× headroom |
| path | 650 | 931 | 813 | 9× |
| collide | 789 | 864 | 859 | 9× |
| cache | 799 | 757 | 794 | 9× |
| modes | 827 | 782 | 799 | 9× |
| **import** | **3840** | **3635** | **3773** | **2.1× (tightest)** |
| persist | 1650 | 1649 | 1797 | 4.4× |
| missing | 897 | 788 | 747 | 9× |

`import` is the family's tightest row (two child spawns, one an editor `--import`). Its
`import_tries`/`reader_tries` are diagnostics on a `R104 …` line, **never pinned**.

## FINAL row tuples (measured — pins are exact substrings of the frozen receipts)

All eight arms are byte-stable across 3 rounds (`diff` of the `PASS` lines: STABLE ×8).

```python
    # r104 — C1: ResourceLoader / ResourceUID UID-cache lattice
    # (reports/round-104/r104-E0.md). One row per arm; each pin is the arm's
    # whole `PASS res_uid …` line, so a dropped/mutated field flips it.
    ('res_uid_text_grammar', 'res_uid.gd', ['--arm=text'], 0,
     'PASS res_uid text decode=uid://a=0,uid://9=34,uid://z=25,uid://0=25,uid://bqk3m5n7qar1=103876737118377468,uid://b=1,uid://=0,uid://aaaa=0 alias_empty_eq_aaaa=true alias_0_eq_z=true a0=0 z25=25 roundtrip_int63max=true first_bad=none pow2_63_overflows=true pow2_63_val=-9223372036854775808 int64_max=9223372036854775807 minted_positive=true minted_le_int64max=true minted_text_shape=uid minted_roundtrip=true invalid_text_id=-1 invalid_text_back=uid://<invalid> empty_text_id=-1 invalid_const=-1'),
    ('res_uid_path_api', 'res_uid.gd', ['--arm=path'], 0,
     'PASS res_uid path save=OK after_save_shape=path ensure_shape=path after_ensure_shape=path after_ensure_same=true echo_proj_is_path=true echo_missing_is_path=true ghost_back_empty=true bad_back_empty=true empty_back_empty=true unknown_uid_to_path_empty=true ghost_text_shape=uid create_for_path_deterministic=true registered=false id_path_empty=true'),
    ('res_uid_collision_classes', 'res_uid.gd', ['--arm=collide'], 0,
     'PASS res_uid collide two_ids_one_path fwd_ia_kept=true fwd_ib_kept=true rev_shape=uid rev_is_ib=true rev_is_ia=false one_id_two_paths fwd_keeps_first=true set_id_unregistered_registers=false set_id_registered_retargets=true remove_id_registered_clears=true'),
    ('res_uid_load_cache_identity', 'res_uid.gd', ['--arm=cache'], 0,
     'PASS res_uid cache same_path=true same_uid=true loaders_same=true uid_load_path_is_p=true uid_load_path_shape=path has_cached path=true uid=true exists_path=true exists_uid=true get_resource_uid_is_custom=true get_resource_uid_uidarg_is_custom=true missing_load_null=true missing_has_cached=false missing_exists=false unregistered_tres path_to_uid_echo=true get_resource_uid=-1 load_ok=true'),
    ('res_uid_cache_mode_bust', 'res_uid.gd', ['--arm=modes'], 0,
     'PASS res_uid modes modes_same_as_l0=reuse:s1/u1,replace:s1/u1,ignore:s0/u1,repl_deep:s1/u1,ign_deep:s0/u1 stale_reuse_same=true stale_reuse_col=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] replace_same_obj=true replace_col=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] uid_after_replace_same=true uid_path_kept=true'),
    ('res_uid_import_remap', 'res_uid.gd', ['--arm=import'], 0,
     'PASS res_uid import import_code=0 cache_written=true import_file_written=true reader_code=0 uid_is_uid=true same_by_uid=true exists_uid=true cls=CompressedTexture2D'),
    ('res_uid_persist_xprocess', 'res_uid.gd', ['--arm=persist'], 0,
     'PASS res_uid persist cache_bytes=32 reader_code=0 uid_is_uid=true back_is_target=true has_id=true id_path_is_target=true'),
    ('res_uid_missing_uid_class', 'res_uid.gd', ['--arm=missing'], 0,
     'PASS res_uid missing ghost_has_id=false ghost_path_empty=true ghost_uid_to_path_empty=true bogus_in_range=true bogus_has_id=false bogus_path_empty=true absent_path_echo_is_path=true unknown_uid_load_null=true unknown_uid_exists=false id_zero_encodes=uid://a id_zero_has_id=false'),
```

**No instance ids, RIDs, addresses, absolute paths or process-random tokens are pinned.** The
one process-random uid the arms touch (`collide`'s collision id) is deliberately never printed.

## `expected_errors` — REQUIRED for 4 of 8 rows

The battery concatenates stdout+stderr (`:2228` region) and `classify_process`
(`run_battery.py:2107-2110`) rejects any line containing `ERROR:` that no allowlist entry
matches. Every row's stdout has **0** `ERROR:` lines, but the engine writes diagnostics to
stderr for the error-class arms. Matcher rules (`:2096-2105`): an entry matches only if
`line.strip() == entry`, **or** the entry ends with `,` and is a prefix of the stripped line.
Hence entries are pinned as the `ERROR: …` line **with a trailing comma**.

```python
    # r104 — C1 expected_errors: the ResourceUID/loader error-class arms echo engine
    # diagnostics on stderr (verified line-exact below). Each entry is a prefix with a
    # trailing comma; every entry is live (matched) in its row, so the
    # r104_expected_errors_all_matched census stays green.
    'res_uid_path_api': ("ERROR: Invalid UID.,",),
    'res_uid_collision_classes': ('ERROR: Condition "unique_ids.has(p_id)" is true.,',
                                  'ERROR: Condition "!unique_ids.has(p_id)" is true.,'),
    'res_uid_load_cache_identity': ("ERROR: Cannot open file 'user://r104e0/absent_zzz.tres'.,",
                                    "ERROR: Failed loading resource: user://r104e0/absent_zzz.tres.,",
                                    "ERROR: Error loading resource: 'user://r104e0/absent_zzz.tres'.,"),
    'res_uid_missing_uid_class': ('ERROR: Condition "local_path.is_empty()" is true. Returning: Ref<ResourceLoader::LoadToken>(),',
                                  "ERROR: Error loading resource: 'uid://bqk3m5n7qar1'.,"),
```

`text`, `modes`, `import`, `persist` need **no** entry (stderr 0 `ERROR:` lines, measured).

Exact stderr bytes (round 3, `/var/tmp/r104-E0/logs/r3_<arm>.err`), continuation lines
(`   at: …`, `   GDScript backtrace …`) contain no `ERROR:` so they pass the matcher untouched:

```
path    ERROR: Invalid UID.                                             x2  (resource_uid.cpp:196)
collide ERROR: Condition "unique_ids.has(p_id)" is true.                    (resource_uid.cpp:164)
        ERROR: Condition "!unique_ids.has(p_id)" is true.               x2  (resource_uid.cpp:178/232)
cache   ERROR: Cannot open file 'user://r104e0/absent_zzz.tres'.            (resource_format_text.cpp:1442)
        ERROR: Failed loading resource: user://r104e0/absent_zzz.tres.      (resource_loader.cpp:317)
        ERROR: Error loading resource: 'user://r104e0/absent_zzz.tres'.     (core_bind.cpp:82)
missing ERROR: Condition "local_path.is_empty()" is true. Returning: …     (resource_loader.cpp:752)
        ERROR: Error loading resource: 'uid://bqk3m5n7qar1'.                (core_bind.cpp:82)
```

### Hazard avoided (worth recording)

An earlier revision of the `collide` arm called `get_id_path()` on an id whose `set_id()` had
been refused, which makes the engine print
`ERROR: Unrecognized UID: "uid://<random>".` — **a per-process random string that no
allowlist entry can match** (prefix entries need a trailing comma; the tail is variable).
The arm was restructured (rr.gd probe: set_id/remove_id are silent no-ops on an unregistered
id) so the line is never produced. A future edit must not reintroduce a `get_id_path` on a
possibly-unregistered id.

## Insertion / ordering constraints (for the orchestrator)

1. `res_uid.gd` is a **new** file — no existing CASES row references it. Insert the 8 rows
   **ahead of the crash/descendant tail** (before `("crash_spontaneous_sigabrt", …, :1711)`),
   i.e. in the same region as the r103 export_div family. The r79/r88/r101/r102 rule stands:
   no CASES row may sit between `descendant_pipe_detached_control` and the meta probes.
2. The rows are **order-independent** of each other: every arm wipes `user://r104e0` at start
   (`_wipe()`) and again at exit, and each uses its own subdirectory. Safe to run sequentially
   in any order; the battery is sequential today.
3. **No shared mutable state with any other fixture** — everything lives under `user://r104e0`
   in the per-run `app_userdata` directory (the battery rewrites `config/name` per run, so the
   base is run-private).
4. The `import`/`persist` arms spawn a **nested Godot child** via `OS.execute`. This is the
   same mechanism `export_launch`/`save_process` already use; the child inherits the battery's
   env. `import` needs an editor-capable build (it already runs `--import`), same precondition
   as the `__godot_export__` rows.
5. `import` is the only row with material runtime (≈3.8 s vs the 8 s bound). Do not raise its
   per-row bound unless the host is heavily oversubscribed.

## Residual risk / unknowns

- **Spawn flake (mitigated, not eliminated).** Under load this host intermittently launches a
  headless child with a null `getcwd`
  (`ERROR: Parameter "getcwd(real_current_dir_name, 2048)" is null.` at
  `drivers/unix/dir_access_unix.cpp:739` → `Invalid project path … aborting`). Measured 0/8
  failures in a quiet loop (z9 probe) but it appeared during a loaded sweep; the `import` and
  `persist` arms carry bounded retries (≤4) plus a project-dir guard, and `tries` is
  diagnostic-only. **Unknown:** whether a saturated 48-seat host could exhaust 4 attempts.
- **Unknown:** whether the loader's `.import` remap honours a `uid=` whose `.uid`/cache entry
  disagrees (the import arm writes the real cache, so the two agree).
- `create_id()` magnitude is pinned only as `minted_positive` / `minted_le_int64max` because
  `2 ** 63` overflows GDScript's int64 (measured: `2**63 == -9223372036854775808`), making any
  `>= 2 ** 63` comparison trivially true. An earlier draft of this shard asserted the
  stronger claim; it was a false positive and is retracted.
- The `path` arm's `ensure_shape=path` records that `ensure_path()` returns the path on this
  build; whether it returns a uid on a build with a populated cache is **unknown** (it is
  called before any uid exists for that path).
