# r101-E0-EXPORT-LEAD shard (lane game-dev-2d-shokunin, round 101, claim C1)

Seat: **E0-EXPORT-LEAD** — owns `corpus/fixtures/export_prod.gd` only.
Engine: `godot 4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, headless).
Deliverables: `corpus/fixtures/export_prod.gd` (729 lines, new file; sha256
`872a9cf699b2cadf98b5201b3607e51dad754a15072b9d35ee22c8749a735f3e`),
`reports/round-101/r101-E0-spec.md` (registration spec, 12 rows),
`reports/round-101/mutations/r101-E0-m{1,2,3}*.sh` (discrimination mutants),
this shard. No shared file was edited; `run_battery.py` was never executed.

## Plan (as executed)

1. Recon: neighbor fixture idiom (`r95b_order.gd`, `r100b_phase.gd`,
   `descendant_pipe_probe.gd`), the harness contract
   (`execute()` at `run_battery.py:1842`, 8 s bound at `:1863`, classifier at
   `:1725`), existing export rows (`__godot_export__` at `:58`).
2. Mechanics on scratch projects (`/var/tmp/r101-E0/**`, never run_battery):
   PCK/ZIP export, `--main-pack`, unknown preset, templates-missing.
3. Author `export_prod.gd`: 8 arms, 12 registrable PASS lines, PCK/ZIP census
   parsers in-engine, nested Godot calls redirected to scratch logs.
4. Validate every arm ×2 on the exact battery launch shape; mutants for
   discrimination; battery-default root run.
5. Write `r101-E0-spec.md` with exact row names/signatures/discriminators.

## Load context (`uptime`)

```
16:21:09 up 1 day, 16:21, load average: 33.42, 19.05, 12.84   (session start)
16:53:39 up 1 day, 16:53, load average:  8.98,  9.19, 14.51   (final sweep)
```
Sibling lanes live on the host (3D r104 swarm, other r101 seats incl.
`export_prod_s01…s11.gd` owners, two hung E9 `godot` processes from another
seat — left untouched).

`/tmp` state during the session: 80 % full and intermittently **EDQUOT** for
this user (`printf` → `Disk quota exceeded` at 16:22; `df -h /tmp` 13 G/16 G);
`/var/tmp` (root fs, 769 G free) used for all seat scratch.

## Findings

### F1 (HIGH, host-wide, measured) — the 4.7.2 packer silently packs a 0-byte `project.binary` when /tmp writes hit EDQUOT

`strace` of a `--export-pack` (pristine third-party project, no fixture code):

```
openat(AT_FDCWD, "/tmp/tmpproject.binary-PMblp0", O_RDWR|O_CREAT|O_EXCL, 0600) = 10
write(10, "ECFG\3\0\0\0\27\0\0\0application/config/n"..., 164) = -1 EDQUOT (Disk quota exceeded)
rename("/tmp/tmpproject.binary-PMblp0", "/tmp/tmpproject.binary") = 0
openat(AT_FDCWD, "/tmp/tmpproject.binary", O_RDONLY) = 10
unlink("/tmp/tmpproject.binary") = 0
```

* the temp path is a **fixed `/tmp/…` name**; setting `TMPDIR` does not move
  it (verified by a second strace run);
* the write error is swallowed: the pack stores a **0-byte `project.binary`**
  and the export exits **0**; the artifact then fails to load its own settings
  (`ERROR: Corrupted header in binary project.binary (not ECFG)`), and
  `--main-pack` / an exported release binary boot nothing;
* reproduced on this lane's `--export-pack`, `--export-release` and on a
  pristine handmade project; it appeared system-wide around 16:39 (earlier
  exports produced 269/324/168-byte `project.binary`);
* the existing `export_readiness` CASES row cannot see it (non-empty ELF +
  `[DONE]` marker still hold), so the host-wide breakage is invisible to the
  battery as landed.

**Mitigation shipped in the fixture:** export calls run under
`unshare -m --map-root-user /usr/bin/sh -c 'mount -t tmpfs -o size=64M tmpfs /tmp; <export>'`
— private /tmp, so the packer's temp write always succeeds (verified: 164 B
pbtest / 324 B prod / 168 B swap `project.binary`, pack boots). The new
`pbin_size` receipt field pins this (rows 1/4/7). Unshare availability is
probed once per process and recorded as
`EXPORT_PROD_DIAG <arm> userns_tmp_isolation=true|false`; without it the arms
still run and `pbin_size=0` fails loudly instead of hiding the environment.

### F2 (MEDIUM, measured) — three receipt fields are scratch-root dependent

The exported `.scn` embeds a path-dependent hash (two roots differ in
`.godot/exported/133200997/export-…-main.scn`, all other entries equal), so:

* pack `sha256` differs per root (`3e0df548…`, `ed1a2056…`, `d8b7d1cd…`);
* zip `bytes` drifts (3982/3983);
* templates-missing `log_bytes` drifts (1545 vs 1653 — the log embeds
  `XDG_DATA_HOME`).

The 12 pinned signatures therefore stop **before** those fields (they trail the
pinned text); determinism is pinned structurally as
`equal_to_sample1=true byte_diff_count=0 samples=2` (same-root byte equality,
true ×2 rounds + battery-default root run).

### F3 (LOW, measured) — `/tmp` quota also breaks the 4 KB pack output

With no `EXPORT_PROD_ROOT` the first root policy (`/tmp/export_prod`, probed
with 5 bytes) accepted the dir, then `pack_export_exit:1` — the pack write
itself hit EDQUOT. Fixed by probing with a 4096-byte write+readback and by
preferring the engine user-data dir over `/tmp`
(`…/app_userdata/MechanicOneShotTest/export_prod`, same fs as the repo).

## Measured receipts (battery launch shape, ×2 rounds, stderr 0 B, exit 0)

```
EXPORT_PROD_ROOT=<scratch> godot --headless --path <proj> --script res://export_prod.gd -- --arm=<arm>
```

| arm | ms (r1/r2) | pinned line (prefix) |
|---|---|---|
| base | 3078/3194 | `PASS export_prod base magic=GDPC entry_count=16 names_sha256=d3a3d695… pbin_size=324 census_match=true bytes=3968` |
| base (subdir) | — | `PASS export_prod subdir dirs=[data,data/deep,res,secret] nested_size=15 file_count=16` |
| base (filter) | — | `PASS export_prod filter … nested_in=true keep_in=true drop_in=false drop_on_disk=true` |
| zip | 3220/3000 | `PASS export_prod zip magic=PK0304 … deflate_entries=16 pbin_size=324 census_match=true` |
| det_a | 3168/3284 | `PASS export_prod det_a sample=1 bytes=3968` |
| det_b | 3084/3147 | `PASS export_prod det_b sample=2 bytes=3968 equal_to_sample1=true byte_diff_count=0 samples=2` |
| swap | 5126/4902 | `PASS export_prod swap pack_boot=main_a source_boot=main_b pbin_size=168 pack_exit=0 source_exit=0` |
| quitframes | — | `PASS export_prod quitframes quit_after=5 frames=[1,2,3,4,5] extra=false exit=0` |
| remap | 3103/2948 | `PASS export_prod remap remap_gd=true remap_scn=true remap_tres=true raw_gd=false raw_png=false ctex_tex=true ctex_icon=true import_tex=true import_icon=true` |
| iconuid | — | `PASS export_prod iconuid icon_svg=true icon_import=true icon_uid_in_pack=false uid_on_disk=true uid_in_pack=false` |
| refusal | 3121/3162 | `PASS export_prod refusal nested_exit=1 class=invalid_export_preset_name preset_listing=true artifacts=0` |
| notemplates | 3191/3005 | `PASS export_prod notemplates nested_exit=1 class=no_export_template release_template_named=true artifacts=0` |

All ≤ 5.1 s against the harness's 8 s fixture bound; full 12-row registration
≈ 40 s of battery time. Battery-default run (no env var, root =
`…/app_userdata/MechanicOneShotTest/export_prod`): all 8 arms exit 0, pinned
texts byte-identical, only the F2 trailing fields moved.

## Discrimination (mutants, `reports/round-101/mutations/`)

* **M1** (drop `secret/keep*` from `include_filter`): `filter keep_in=false`,
  `base entry_count=15 keep_size=-1 census_match=false bytes=3896`,
  `subdir file_count=15` → rows 1–3 fail.
* **M2** (empty `include_filter`): `entry_count=14`, `nested_in=false`,
  `dirs=[res]` → rows 1–3 fail.
* **M3** (swap project boots `main_b` from the start): `swap pack_boot=main_b`
  → row 7 fails, row 8 (`frames=[1,2,3,4,5]`) still PASSes — the two swap-arm
  rows discriminate independently.

## What the orchestrator must do

1. Register the 12 rows exactly as in `reports/round-101/r101-E0-spec.md`
   (`--arm=base|zip|det_a|det_b|swap|remap|refusal|notemplates`, exit 0,
   signatures as quoted). Keep `det_a` immediately before `det_b`. No
   `expected_errors` entries are needed.
2. Consider reusing the TMP-namespace + `pbin_size` pattern for the existing
   `__godot_export__` row, which currently cannot see F1 (its artifact is
   silently broken while the row stays green).

## Residual risk / left undone

* Rows 5/6 claim same-root determinism only; cross-root equality is false and
  not claimed.
* If the integration host lacks user namespaces and `/tmp` is quota-full, rows
  1/4/7 fail with `pbin_size=0` — honest, not a fixture defect.
* My seat covered **C1 only**; C2 (`r100b_seq_*` full-replay pins) and C3
  (`--offy` retirement) are other seats' claims and were not touched here.
* Sibling `corpus/fixtures/export_prod_s01…s11.gd` files are other seats'
  artifacts; I did not read or modify them.
