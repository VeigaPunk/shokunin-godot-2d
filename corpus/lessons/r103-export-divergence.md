# Round 103 — export CLI divergence + pack-shape census (Godot 4.7.2.stable)

First-hand receipts for the round-103 `export_div` surface: how the export CLI's two verbs
(`--export-release <preset> <target>` vs `--export-pack <preset> <target>`) diverge on the same
project and preset, the two PCK "shapes" sidecar vs embedded exports produce, and the validated
`user://` isolation fixture `corpus/fixtures/export_div_s02.gd` (sha256
`c08792c1c208d47a8af66c669e7296eb6a1d94fe3d20872aeb73d4d6620a4898`, file mtime 2026-10-18 20:57:06 -03;
its owner seat may revise it later — the hash names the revision this lesson validated). All runs on
godot `4.7.2.stable.arch_linux.ed1daf0bf`, headless, scratch under `/var/tmp/r103c-R1/` (never `/tmp`,
EDQUOT); `run_battery.py` was never executed. Verbatim stdout/logs are in `/var/tmp/r103c-R1/s01/` and
`/var/tmp/r103c-R1/e2v2/`; every figure is [obs] unless labelled.

## 1. Same preset, two verbs: pack bytes are byte-identical

Commands (project `/var/tmp/r103c-R1/s01/proj`, presets `linux_a` (none) / `linux_embed` (`embed_pck=true`)):

| exact command | rc | result |
|---|---|---|
| `godot --headless --path <proj> --export-release linux_a <abs>/preset_bin.x86_64` | 0 | `preset_bin.x86_64` 73,519,416 B sha `d9f79ab8…`; sidecar `preset_bin.pck` 2,504 B sha `79695842…` |
| `godot --headless --path <proj> --export-pack linux_a <abs>/cli.pck` | 0 | 2,504 B sha `79695842…`; `cmp` sidecar == `cli.pck` → **identical** |
| `godot --headless --path <proj> --export-pack linux_embed <abs>/embed_cli.pck` | 0 | 2,504 B sha `79695842…` — the embed flag does **not** change the standalone pack |
| `(cd <proj> && godot --headless --path . --export-pack linux_a rel.pck)` | 0 | bare relative target lands project-relative: `<proj>/rel.pck` 2,504 B |
| `(cd <proj> && godot --headless --path . --export-pack linux_a out/sub.pck)` | **1** | `ERROR: Save PCK: Can't open file for writing at path "out/sub.pck".` + `ERROR: Project export for preset "linux_a" failed.` (no parent dir created; corroborates the r101 lesson) |

- `preset_bin.x86_64` sha256 == installed template `linux_release.x86_64` (`d9f79ab8…`, 73,519,416 B):
  an executable export is template bytes when `embed_pck=false`.
- Reproducibility: 13 `--export-pack`-shaped artifacts in one session window share sha `79695842…`
  (fresh `cli.pck`, `embed_cli.pck`, `rel.pck`, sidecar `preset_bin.pck`, earlier `pack_a1`–`pack_a7`,
  `pack_ctl`, `linux_a/game.pck`; `/var/tmp/r103-R1/out/packs/`).
- Cross-project (E1 scratch, shard plan-only — bytes on disk only): `stock.pck == cli.pck == t1/t2/t3/time_seq.pck`
  (6 × 1,976 B, sha `dcb489a5…`).
- Boot receipt: `timeout 5 preset_bin.x86_64 --headless --quit-after 3 -- --tag=boot1` → rc 0,
  `[r103R1] ready name=r103div` … (artifact runs; exit-code-only would also pass on a silent no-run, cf. r101).

## 2. Target-path contract divergences

- **`--export-release` ignores the target extension**: `--export-release linux_embed <abs>/shape.pck` → rc 0,
  writes **73,521,928 executable bytes** into a `.pck`-named file (sha `9b31dd28…`; same bytes as
  `out/linux_embed/game.x86_64`). E1's scratch shows the same class: four 73,521,400-byte executables
  byte-identical (sha `f71d7ca8…`), one of them named `relpack.pck` [obs; producing command not recorded
  in E1's shard → the per-file command is unknown there].
- **Pack-route extension refusal** (E3 scratch log, provenance E3 shard plan-only):
  `ERROR: Export path "/var/tmp/r103-E3/recon/out_multi_ba/b.x86_64" doesn't end with a supported extension.`
  + `ERROR: Project export for preset "PckOnly" failed.` — a pack-targeted export refuses a non-pack
  extension, the mirror image of the row above.
- **Relative-target split**: bare `rel.pck` succeeds project-relative; a relative path with a missing
  parent directory (`out/sub.pck`) fails rc 1 with `Can't open file for writing`. Use absolute targets
  (the harness's `.resolve()` shape, `run_battery.py:1853`).

## 3. PCK shape census (v4 headers; s04 material)

Header, byte-verified by a self-checking parse (dir block ends exactly at the expected boundary on 10 packs,
`end==sz` / `end==region-4`): `GDPC | u32 fmt=4 | u32 4.7.2 | u32 flags | u64 file_base | u64 dir_offset`;
directory block at `dir_offset`: `u32 count` + entries `[u32 pathlen][path][u64 offset — file_base-relative]
[u64 size][md5 16][u32 flags=0]`.

- **Sidecar shape**: `file_base=112`, dir block flush with EOF. `pack_a1.pck` 2,504 B: fmt 4, eng 4.7.2,
  flags 0x2, dir_off 2,032, count 7 — entries `.godot/exported/…-main.scn` 667 B, `main.gdc` 873 B, `main.gd.remap`,
  `main.tscn.remap`, `global_script_class_cache.cfg`, `uid_cache.bin`, `project.binary` 164 B.
- **Embed shape**: `file_base=104`, dir block + a 4-byte zero tail. Three exported exes carry their pack at
  offset 73,519,416 (= template size) with region sizes 2,500 / 1,940 / 2,188 B, followed by a 12-byte footer
  `[u64 region_size][GDPC]` (footer u64 == region size, measured 2,500 / 1,940 / 2,188).
- E1 scratch `embedded.pck` (1,972 B, embed shape) is **byte-identical** to the in-exe region of E1's
  `preset.x86_64` (`reg == open(embedded.pck)` True) [obs; producer command unrecorded].
- **Include filters map 1:1 to entries**: `linux_filt` pack is 2,592 B / 8 entries — the only delta vs
  `linux_a` is `res/sub/note.txt` (19 B); E3 tag presets: `tag_pck_only.txt` (33 B) only in the PckOnly
  pack, `tag_embed_only.txt` (35 B) only in the Embed pack; a multi-sequence pack is byte-identical to the
  standalone one (`out/a.pck == out_multi_ab/a.pck`, sha `447346ab…`).
- **Encryption flag without a key is cosmetic** [obs]: preset with `encrypt_pck=true` + `encrypt_directory=true`
  and empty encryption filters exports a pack byte-identical to the plain one **except the flags byte**
  (`cmp -l`: 1 differing byte, 0x02→0x03); the export log contains no encrypt/key line. Whether the engine
  refuses such a flags=0x3 pack at load time was not tested [unknown].

## 4. user:// isolation (s02) — validated live

Command shape (`<harness>` = copy of the fixture dir; fresh root): `EXPORT_DIV_ROOT=<root> TMPDIR=<root>/tmp
godot --headless --path <harness> --script res://export_div_s02.gd -- --arm=<iso|xdg>`, ×2 reps per arm.

- **4/4 rc=0 PASS**; each arm's PASS lines are byte-identical across reps (PASS-line sha256:
  iso `fa2a7655…`, xdg `623c442b…`; whole stdout files identical too: `243b19e1…` / `22574729…`; walls
  4.6/4.8 s iso, 2.4/2.4 s xdg).
- Iso PASS (verbatim): `PASS export_div s02 arm=iso r1_read=none r1_exit=0 r2_read=run1 r2_exit=0
  store=[run1,run2] store_under_xdg=true userdir_under_xdg=true home_store_absent=true proj=…` — store
  resolves under the overridden `XDG_DATA_HOME`, run 2 sees run 1 (persistence), nothing under `HOME`.
- Xdg PASS: fresh store under `xdgB` (`store_b=[run3]`), then `env -u XDG_DATA_HOME HOME=homeC` resolves
  `user://` under `homeC/.local/share/godot/app_userdata/ExportDivS02/` (`r4_userdir_under_home=true`).
- **Repeat-run law** [obs→inf]: the xdg arm wipes `homeC` every run, but a wipe that lists with the default
  `DirAccess` semantics **skips dot-entries**; the payload lives under `homeC/.local/…`, so the pre-fix
  second run read `prior=run4` and FAILed `run4_read_not_none:[run4]` (`store_c=[run4,run4]`; E2v receipts
  `/var/tmp/r103c-E2v/xdg2.out`, 20:56:01). The fixture's wipe now sets `include_hidden=true` (source comment
  cites exactly this), and the fresh ×2 xdg runs above PASS.
- Cross-check: the pre-fix E2v iso PASS line equals my fresh iso PASS line modulo the scratch `proj=` path —
  pinned fields are root-independent.

## 5. Registration + limits

- `export_div` rows are **not registered at HEAD**: `cases_integrity` (`run_battery.py:4119`) has no
  `export_div_` prefix entry; `reports/round-103/mutations/w5_export_div.patch` (apply-check OK at 6e3e87f7)
  adds `r103_expected_errors_all_matched` + `r103_export_div_count_floor` + `"export_div_"` to the
  per-round prefix tuple. Fixtures `export_div_s01..s05.gd` were authored during the round (untracked at
  write time: s02 20:57:06 — the only one validated here, sha `c08792c1…` — s01 21:00:49, s05 21:02:44,
  s04 21:04:24, s03 21:05:00; each seat's shard carries its own run receipts).
- s05 (editor-settings override): measured by its fixture author, not re-measured here — the s05 fixture
  header records the hand probes (a bare headless `--export-pack` creates
  `$XDG_CONFIG_HOME/godot/editor_settings-<major>.<minor>.tres`, 17,728 B on this host, plus
  `feature_profiles/`, `script_templates/`, `text_editor_themes/`; editor-settings contents do not reach
  the pack) [obs at fixture-header level; end-to-end fixture receipts live in the s05 seat's shard].
- Not claimed: Windows/macOS platforms; encryption at load time; that the 2,504 B byte-identity holds across
  cold caches (the r101 A/B pack variance applies to whole-file pins — prefer header+entry pins, with the
  byte-compare as the within-session discriminator); sibling scratch provenance (E1/E3 shards plan-only) is
  labelled per item.
- Consequences for pin design: (1) an export row must parse the container (`GDPC` + self-checking dir walk),
  not just check `size>0`/exit 0; (2) preset-vs-pack rows should byte-compare the two artifacts and record
  the shared sha; (3) assert extension semantics explicitly — both verbs exit 0 on `.pck` targets, so the
  discriminator is the artifact *shape* (GDPC magic vs 73 MB executable), and refusals are `rc!=0` + quoted
  `ERROR:` text; (4) user:// rows must assert the resolved store path under the overridden root, HOME
  absence, and cross-run persistence, and any HOME-dir wipe must use `include_hidden=true`.

Evidence pointers: shard `reports/round-103/r103-scr1.md`; receipts `/var/tmp/r103c-R1/s01/`
(`a.log`…`e.log`, `boot.log`, `out/`), `/var/tmp/r103c-R1/e2v2/` (`*.out`, `run.txt`); mutation scripts
`reports/round-103/mutations/{mut02.py,mut05_gate_evasion.py,mut07.py}`; PCK census sources
`/var/tmp/r103-R1/out/`, `/var/tmp/r103c-E1/m1/out/`, `/var/tmp/r103-E3/recon/`, `/var/tmp/r103c-E4/root/out/`.
