# r101-E0-EXPORT-LEAD — export_prod CASES registration spec (C1)

Seat: **E0-EXPORT-LEAD** (owner of `corpus/fixtures/export_prod.gd` only).
Engine: `godot 4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), templates
present at `~/.local/share/godot/export_templates/4.7.2.stable/`.
Host: load average 33 → 9 during the session (sibling 3D lane r104 + r101 seats
running concurrently); all times below measured under that load; fixture bound
is **8 s** (`run_battery.py:1863` gives non-`__godot_export*` scripts 8 s).

All receipts below are **observed bytes** from targeted runs of the exact
command shape the battery uses:

```
godot --headless --path <proj> --script res://export_prod.gd -- --arm=<arm>
```

against a scratch copy of the fixture project (`project.godot` +
`export_presets.cfg` + `export_prod.gd`, i.e. `corpus/fixtures/` bytes) under
`/var/tmp/r101-E0/val/proj`, two full rounds, byte-identical receipts in both
rounds, stderr 0 bytes, exit 0. `run_battery.py` was never executed.

## 1. Rows to register (exact names, args, signatures)

Rows execute the arm process once each; `base`-arm rows (`1–3`) and `swap`-arm
rows (`7–8`) print several PASS lines per process, so each row re-runs the arm.

| # | CASES name | script | flags | exit | pinned signature (substring of merged output) |
|---|---|---|---|---|---|
| 1 | `export_prod_base_pck` | `export_prod.gd` | `--arm=base` | 0 | `PASS export_prod base magic=GDPC entry_count=16 names_sha256=d3a3d695534079a2e9d3a4f3d2e7e5bbf5b8e2a66110e94c09434611be7bd889 nested_size=15 keep_size=8 drop_in_pack=false uid_entries=0 remap_entries=3 ctex_entries=2 import_entries=2 project_binary=true pbin_size=324 census_match=true bytes=3968` |
| 2 | `export_prod_subdir_census` | `export_prod.gd` | `--arm=base` | 0 | `PASS export_prod subdir dirs=[data,data/deep,res,secret] nested_path=data/deep/nested.txt nested_size=15 file_count=16` |
| 3 | `export_prod_include_exclude_filter` | `export_prod.gd` | `--arm=base` | 0 | `PASS export_prod filter include=data/*,secret/keep* exclude=secret/drop* nested_in=true keep_in=true drop_in=false drop_on_disk=true` |
| 4 | `export_prod_zip_census` | `export_prod.gd` | `--arm=zip` | 0 | `PASS export_prod zip magic=PK0304 eocd=true entry_count=16 local_headers=16 names_sha256=d3a3d695534079a2e9d3a4f3d2e7e5bbf5b8e2a66110e94c09434611be7bd889 nested_size=15 drop_in_zip=false deflate_entries=16 pbin_size=324 census_match=true` |
| 5 | `export_prod_det_a` | `export_prod.gd` | `--arm=det_a` | 0 | `PASS export_prod det_a sample=1 bytes=3968` |
| 6 | `export_prod_det_b` | `export_prod.gd` | `--arm=det_b` | 0 | `PASS export_prod det_b sample=2 bytes=3968 equal_to_sample1=true byte_diff_count=0 samples=2` |
| 7 | `export_prod_main_scene_swap` | `export_prod.gd` | `--arm=swap` | 0 | `PASS export_prod swap pack_boot=main_a source_boot=main_b pbin_size=168 pack_exit=0 source_exit=0` |
| 8 | `export_prod_mainpack_quit_after_frames` | `export_prod.gd` | `--arm=swap` | 0 | `PASS export_prod quitframes quit_after=5 frames=[1,2,3,4,5] extra=false exit=0` |
| 9 | `export_prod_resource_remap_census` | `export_prod.gd` | `--arm=remap` | 0 | `PASS export_prod remap remap_gd=true remap_scn=true remap_tres=true raw_gd=false raw_png=false ctex_tex=true ctex_icon=true import_tex=true import_icon=true` |
| 10 | `export_prod_icon_uid_census` | `export_prod.gd` | `--arm=remap` | 0 | `PASS export_prod iconuid icon_svg=true icon_import=true icon_uid_in_pack=false uid_on_disk=true uid_in_pack=false` |
| 11 | `export_prod_unknown_preset_refusal` | `export_prod.gd` | `--arm=refusal` | 0 | `PASS export_prod refusal nested_exit=1 class=invalid_export_preset_name preset_listing=true artifacts=0` |
| 12 | `export_prod_templates_missing_class` | `export_prod.gd` | `--arm=notemplates` | 0 | `PASS export_prod notemplates nested_exit=1 class=no_export_template release_template_named=true artifacts=0` |

**Ordering constraint:** register rows 5 then 6 adjacent — `det_b` byte-compares
its sample against `det_a`'s `a.pck` in the shared out dir and FAILs
(`reason=det_a_artifact_missing`) if it is absent. No `expected_errors` entries
are needed: the fixture's own stdout/stderr never contains `ERROR:`/`SCRIPT
ERROR:`/`Parse Error:` (nested diagnostics are redirected to scratch logs).

**Trailing fields deliberately left unpinned** (they follow the pinned text, so
the rows above still classify them as diagnostics):

* row 4 `bytes=3982…3983` — zip size drifts with the scratch root path
  (the exported `.scn` embeds a path-dependent hash);
* rows 5/6 `sha256=…`, `sample1_sha256=…` — the pack sha is **root-path
  dependent** (same bytes inside one root; three roots gave `3e0df548…`,
  `ed1a2056…`, `d8b7d1cd…`). The determinism claim is pinned as
  `equal_to_sample1=true byte_diff_count=0 samples=2`, which is a byte-level
  comparison inside the process;
* rows 11/12 `log_bytes=…` — refusal 1219 (root-stable), templates-missing
  1545…1653 (the log embeds the absolute `XDG_DATA_HOME` path, so it drifts
  with the scratch root).

## 2. What each row measures (and its discriminator)

| row | measured mechanism (observed) | discriminator (measured) |
|---|---|---|
| 1 | `--export-pack` → real PCK: magic `GDPC`, u64 file-table offset at 0x20, 16 entries, 3968 bytes; `project.binary` 324 B | M1/M2 below flip `entry_count`, `census_match`, `names_sha256` |
| 2 | `data/deep/nested.txt` (15 B) present in the pack; dirs `[data, data/deep, res, secret]` | M2 → `dirs=[res]`, `file_count=14` |
| 3 | `include_filter="data/*,secret/keep*"`, `exclude_filter="secret/drop*"`: `keep.txt` in, `drop.txt` out (still on disk) | M1 → `keep_in=false`; M2 → `nested_in=false` |
| 4 | `--export-pack … .zip` takes the packer's `savezip` path: `PK\x03\x04`, EOCD, 16 central entries = 16 local headers, all DEFLATE(8), unzip-readable | delete `.zip` handling / corrupt EOCD → `zip_parse_failed` FAIL |
| 5–6 | two exports of the same project are **byte-identical** (size 3968, `byte_diff_count=0`); `det_b` requires `det_a`'s artifact | missing/renamed `a.pck` → `det_a_artifact_missing` FAIL |
| 7 | pack exported with `main_scene=res://main.tscn`, then the **source** `project.godot` is swapped to `main_b.tscn`; running the pack from `/` (neutral cwd) boots `main_a`, the swapped source boots `main_b` | M3 → `pack_boot=main_b` (pinned `main_a` row fails) |
| 8 | `godot --headless --main-pack <pck> --quit-after 5` → exit 0, exactly `FRAME 1…5`, no 6th | M3 leaves this row PASS (frames are engine-driven) — the two rows discriminate independently |
| 9 | exported pack carries `.remap` for script/scene/`.tres` (no raw `main.gd`, no raw `res/tex.png`) plus `.godot/imported/*.ctex` + `.import` sidecars | dropping import/config → `ctex_*`/`remap_*` false |
| 10 | `icon.svg` + `icon.svg.import` in the pack, **no** `.uid` entry (0 uid entries) while `main.gd.uid` exists on disk → editor-only UID stripped | a future engine that packs `.uid` → `uid_in_pack=true` |
| 11 | nested `--export-pack "No Such Preset"` → exit 1, `Invalid export preset name: No Such Preset.`, preset listing printed, 0 artifacts | a preset lookup regression → `nested_exit=0`/`artifacts=1` |
| 12 | nested `--export-release` under an empty `XDG_DATA_HOME` → exit 1, `No export template found at the expected path:` + `linux_release.x86_64`, 0 artifacts | templates present → `class=other` |

**Fixture-side mutants** (scripts in `reports/round-101/mutations/r101-E0-m*.sh`,
recorded outputs in §4):

* **M1** drops `secret/keep*` from `include_filter` → `filter keep_in=false`,
  `base entry_count=15 keep_size=-1 census_match=false`, `subdir file_count=15`
  ⇒ rows 1–3 all stop matching their pins.
* **M2** empties `include_filter` → `entry_count=14`, `nested_in=false`,
  `dirs=[res]`, `nested_size=-1` ⇒ rows 1–3 fail.
* **M3** points the swap project's initial `main_scene` at `main_b` ⇒
  `swap pack_boot=main_b` (row 7 fails) while row 8 still PASSes
  (`frames=[1,2,3,4,5]`).

## 3. Environment notes the integration must know

1. **/tmp EDQUOT hazard (measured, host-wide).** Godot 4.7.2's packer serializes
   `project.binary` through a fixed temp path `/tmp/tmpproject.binary-<rand>`
   (`strace`: `write(2) = -1 EDQUOT`; `$TMPDIR` is **not** honored). The packer
   ignores the error and stores a **0-byte `project.binary`**; the export still
   exits 0, but the pack/binary cannot load its own settings
   (`ERROR: Corrupted header in binary project.binary (not ECFG)`) and
   `--main-pack` boots nothing. This was reproduced on a pristine third-party
   project and on this lane's own `export_readiness` artifacts — every export
   row on this host is affected while the /tmp quota is exhausted, and
   `export_readiness` cannot see it (it only checks non-empty output + `[DONE]`).
2. **Mitigation inside the fixture.** Export calls run under
   `unshare -m --map-root-user sh -c 'mount -t tmpfs … /tmp; …'` (private /tmp)
   when user namespaces are available; `EXPORT_PROD_DIAG <arm>
   userns_tmp_isolation=true` records it. Without unshare the arms still run and
   `pbin_size=0` makes the failure visible instead of silent (rows 1/4/7 fail).
   `pbin_size` (324 prod / 168 swap) is the new tripwire for this class.
3. **Scratch root policy.** `EXPORT_PROD_ROOT` → `$TMPDIR/export_prod` →
   `<engine user data dir>/export_prod` → `/tmp/export_prod`, each candidate
   accepted only after a **4096-byte write+readback** probe. The user-data dir
   is preferred over `/tmp` because `/tmp` measurably rejected even the 4 KB
   pack output with EDQUOT during this session (a 5-byte probe had passed).
   With no env var set (the battery default) the fixture selected
   `…/app_userdata/MechanicOneShotTest/export_prod` and every pinned line above
   reproduced byte-identically. Host paths appear only in `EXPORT_PROD_DIAG`
   lines, never inside the pinned text.
4. **Cost** (measured, loaded host): base/subdir/filter/zip/det/remap ≈ 3.0–3.3 s,
   swap/quitframes ≈ 4.9–5.1 s, refusal/notemplates ≈ 3.0–3.2 s. All ≤ 5.1 s
   against the 8 s bound. Registering all 12 rows adds ≈ 40 s of battery wall
   time (each row re-executes its arm).
5. **Sibling artifacts.** `corpus/fixtures/export_prod_s01…s11.gd` exist in the
   tree but are owned by other seats; this spec only covers `export_prod.gd`
   and the `export_prod_*` row names above.

## 4. Verification receipts (commands + observed output)

Command shape for every line below (two rounds each, byte-identical receipts):

```
EXPORT_PROD_ROOT=/var/tmp/r101-E0/root godot --headless --path /var/tmp/r101-E0/val/proj \
  --script res://export_prod.gd -- --arm=<arm>
```

* round 1/2 exit codes: all `0`, stderr 0 bytes; per-arm wall time 2.9–3.3 s
  (base/zip/det/remap/refusal/notemplates) and 4.9–5.1 s (swap).
* **battery-condition run** (no `EXPORT_PROD_ROOT`; root selected =
  `…/app_userdata/MechanicOneShotTest/export_prod`): all 8 arms exit 0, stderr
  0 B, and the pinned substrings reproduce byte-identically. Only the trailing
  unpinned fields moved: zip `bytes=3983` (vs 3982), det sha
  `ed1a2056…` (vs `3e0df548…`), notemplates `log_bytes=1653` (vs 1545) — all
  after the pinned text, as designed in §1.
* M1/M2/M3 as quoted in §2 (`bash reports/round-101/mutations/r101-E0-m1_drop_keep_include.sh`
  etc.), mutants built by sed from `corpus/fixtures/export_prod.gd`.
* fixed-tmpfs proof: pristine project exported directly → `project.binary` 0 B,
  `--main-pack` run prints `Corrupted header in binary project.binary (not ECFG)`;
  same export under `unshare -m --map-root-user … mount -t tmpfs tmpfs /tmp` →
  `project.binary` 164 B (pbtest), 324 B/168 B (prod/swap arms), pack boots.
  `strace` evidence for the EDQUOT write:
  `openat("/tmp/tmpproject.binary-PMblp0", O_RDWR|O_CREAT|O_EXCL)` then
  `write(10, "ECFG…", 164) = -1 EDQUOT` followed by rename/read/unlink and a
  0-byte pack entry.

## 5. Left undone / residual risk

* Rows 5/6 pin *same-root* determinism only; cross-root byte equality is
  **false** by design (path-dependent exported scene) and is not claimed.
* If the integration host lacks user namespaces **and** the /tmp quota is full,
  rows 1/4/7 fail with `pbin_size=0` — that is the honest outcome, not a
  fixture defect (the engine genuinely produces broken packs there).
* The `swap`/`quitframes` rows spend ~5 s; if battery time is tight, dropping
  row 8 halves that (row 7's line already proves the launch).
