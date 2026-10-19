# r103-crit1 — C1 attack seat (export_div family): forgery/spoof/contamination/echo

Seat: **KEY=C1** — attack C1 receipts. Scope: (a) divergence-census forgery (CLI run faked via
cp of preset artifact), (b) user:// isolation spoof (XDG not actually overridden),
(c) multi-preset cross-contamination miss, (d) header census echo. Required discriminators.

Host (observation, one-shot at seat start): `18:50:22 up 1 day, 18:50, 1 user, load average:
3.06, 3.57, 4.21`; `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`; `/tmp` write probe
OK (64 KiB @ 2.4 GB/s, no EDQUOT this session); `unshare -m --map-root-user` tmpfs OK.
Scratch: `/var/tmp/r103-crit1/` (never /tmp). No git worktree created; no shared file edited;
`run_battery.py` never executed by this seat; all repo writes are my two files under
`reports/round-103/mutations/` plus this shard.

## Plan
1. Build an independent ground-truth rig (own project, own parser) so every C1 claim can be
   re-derived from bytes without trusting a fixture's printed census.
2. Measure the four attack surfaces headless: CLI-form divergence, XDG isolation, sequential
   multi-preset, PCK header census.
3. Mutate scratch copies of the landed `export_div_s0*.gd` (repo untouched) with one forgery per
   class + controls; record verbatim PASS/FAIL lines.
4. Emit required discriminators per class; verdicts per surface; label observation/inference.

## 1. Independent ground truth (my rig — observation)

Rig: `/var/tmp/r103-crit1/gt/proj`, presets `PEmbed` (`embed_pck=true`, include `marker_a.txt`) /
`PStock` (`embed_pck=false`, include `marker_b.txt`); exports run under
`unshare -m --map-root-user sh -c 'mount -t tmpfs -o size=64M tmpfs /tmp && godot --headless
--path <proj> <cli> <preset> <out>'` (private /tmp for the packer's fixed `tmpproject.binary`).

```
run A:  godot --headless --path … --export-release PEmbed …/out/embed.x86_64   rc=0
run B:  godot --headless --path … --export-pack    PEmbed …/out/embed_cli.pck  rc=0
run C:  godot --headless --path … --export-release PStock …/out/stock.x86_64   rc=0
run D:  godot --headless --path … --export-pack    PStock …/out/stock_cli.pck  rc=0
```

- **GT-1 (embed_pck=false): zero divergence between CLI forms.**
  `stock.pck` (release sidecar) vs `stock_cli.pck` (`--export-pack`):
  `identical=True size_delta=0 diff_bytes_in_common=0`, sha
  `19bf0218a17d0143567c91bb48d3cb9eff34504da734d01019ff6467efa68419` (state 1) and
  `d5da9e69665…` (state 2). Entry sets and md5s equal.
- **GT-2 (embed_pck=true): the appended pack is NOT the standalone pack.**
  `embed.x86_64` = 73,522,072 B = template 73,519,416 B + pack region + 12 B trailer
  (`<u64 size><u32 "GDPC">`). Region body parses as a valid PCK: `file_base=104 table_ofs=2120
  count=8 table_end=2644`; the standalone `embed_cli.pck` is 2,652 B with `file_base=112
  table_ofs=2128`. Same 8 entries, identical per-entry md5/size, ~2209 byte positions differ
  (8-byte header/layout shift). State-2 rerun reproduced the same class (104/112; 3452 vs 3456).
- **GT-3 (determinism):** given a frozen project state, exports are byte-reproducible — three
  independent runs `out2 == out3 == seq` (`embed.x86_64` sha `948a630b…`, `stock.pck` sha
  `d5da9e69…`). An apparent 21:21→21:23 drift was traced to my own rig edit (adding `seq.gd`):
  `ENTRIES` diff showed `uid_cache.bin` 29→53 B plus new `seq.gd.remap`/`seq.gdc` entries.
  Export bytes are **project-state-coupled**, not arrangement-coupled.
- **GT-4 (XDG):** exported binary honors `XDG_DATA_HOME`; `OS.get_user_data_dir()` =
  `<XDG_DATA_HOME>/godot/app_userdata/CritDiv`; with XDG unset it falls back to
  `$HOME/.local/share/godot/app_userdata/CritDiv`. Files landed only under the selected root
  (xdg1 / xdg2 / home2 runs; `logs/godot.log` is a second independent witness).
- **GT-5 (size trap):** `embed_cli.pck` and `stock_cli.pck` are **both 2,652 B** and share 2,634
  bytes; only the marker entry differs (md5/name). A size- or count-only comparison is blind to
  exactly the difference these rows exist to detect.

Parser used for all re-derivations: `reports/round-103/mutations/r103-crit1_pck.py`
(`DUMP|ENTRIES|DIFF`, struct-from-bytes, re-verified against freshly exported artifacts).

## 2. Attack runs (scratch copies of the repo fixtures; repo files never edited)

Driver: `reports/round-103/mutations/r103-crit1_mutants.py` (copies `corpus/fixtures` →
`/var/tmp/r103-crit1/fxc`, patches one anchor, runs
`godot --headless --path <fxc> --script res://export_div_sNN.gd -- --arm=<arm>` with
`EXPORT_DIV_ROOT=/var/tmp/r103-crit1/mutroot/…`, then restores the copy from the repo).

Command: `python3 reports/round-103/mutations/r103-crit1_mutants.py M1 M1b M2 M3 M4`

Fixture revisions attacked (sha256, read 21:32): s01 `e7b9fdd4baf1f2bba8b6d4c1389498fed06de7cfba0d5e0ae81bf01824add4db`,
s02 `c08792c1c208d47a8af66c669e7296eb6a1d94fe3d20872aeb73d4d6620a4898`,
s03 `ec242f02b1c120c1654aa36ff11e9a0680469d0ebd4052d1676fcb5256a80000`,
s04 `01d0eef79fe4ca26420e0c0686d3421ec5e84cc2fd057769e79b9ab6eee329bb`,
s05 `f0476e5e18f4238280f4b1f04b24c72cc8b38c43d7d4f61d3918f22db6d1dcc2`.
`s01` was edited by its seat at 21:29:55 — 44 s **after** my first M1 run (21:29:11) — so M1/M1b
were re-run against the current revision: same verdicts as tabulated (`e7b9fdd4` → M1 PASS,
M1b FAIL `export_failed`), and the forged line matches the registered CASES row
`export_div_s01_ident` field-for-field. M2–M4 ran against the revisions above (s02–s05 unchanged
since their seats' last edits).

| mutant | class | arm | observed line (verbatim, truncated) |
|---|---|---|---|
| M1 | CLI run faked via cp + forged log | s01 ident | **`PASS export_div s01 arm=ident sidecar_identity sha256_equal=true files=2 sidecar=1 cli_files=1 bin_gt_1m=true sidecar_bytes=1976 cli_bytes=1976`** (rc=0) |
| M1b | same cp, log has no engine banner (control) | s01 ident | `FAIL export_div s01 arm=ident reason=export_failed sidecar_identity sha256_equal=true …` (rc=1) |
| M2 | XDG_DATA_HOME dropped from child env | s02 xdg | `FAIL export_div s02 arm=xdg reason=run3_read_not_none:[banner] r3_exit=0 store_b=[banner,run3] store_b_under_xdg=false r3_userdir_under_xdg=false r4_read=none r4_exit=0 store_c=[run4] r4_userdir_under_home=true` (rc=1) |
| M3 | foreign preset beacon appended to pack A | s03 seq | `FAIL export_div s03 arm=seq reason=a_foreign_content_present … a_bytes=2015 a_beacon_bytes=true a_foreign_beacon=true … b_foreign_beacon=false` (rc=1) |
| M4 | artifact `flags` byte flipped post-export | s04 pck | `FAIL export_div s04 arm=pck reason=flags_not_2:3 bytes=1944 ver=4 triple=4.7.2 flags=3 file_base=112 law=112 table_ofs=1472 count=7 … tail=0 marks=GDSC,ECFG` (rc=1) |

M1 on-disk shape (observation): forged log
`mutroot/mut-M1-s01/div_s01/ident/logs/export_ident_cli.log` contains exactly
`[ DONE ] savepack` (18 B); `cli.pck` sha `b03cc0d70c…` == `stock.pck` sha `b03cc0d70c…`;
mtime of `cli.pck` is 288 ms **after** the sidecar (copy order preserved). A real export log
(baseline `fxroot-s01/div_s01/ident/logs/export_ident_cli.log`) carries the engine banner plus
9 `savepack` progress lines — the evidence my forgery did not have to reproduce.

**M1 accepted ⇒ residual (bounded, disclosed):** the `ident` row's CLI-run provenance reduces to
the string `[ DONE ]` in the nested log; every pinned field (`sha256_equal`, `files`, `sidecar`,
`cli_files`, `bin_gt_1m`) is satisfied by a byte-copy of the preset sidecar plus that one log
line. The row genuinely measures artifact identity, but it cannot distinguish "the CLI exported
this" from "the sidecar was copied here". Required discriminator (D1b below). M1b shows removing
the banner does flip the row to FAIL — the log is the single point of trust.

## 3. Independent re-derivation of sibling claims (observation)

| claim | my re-derivation (evidence) | verdict |
|---|---|---|
| s01 `ident`: sidecar == CLI pack | `sha256sum` both → `b48027dce03b116efb643faa946c9ff21e170017b5801f6dd2ca8092fbc030d6`; my `DIFF` `identical=True` | holds |
| s03 `seq`: own beacon only, per pack | `grep -c tag_pck_only a_pck.pck` → 1, `tag_embed_only` → 0; `b_emb.pck` → 0 / 1 | holds |
| s02 `iso`: store under XDG, default absent | `cat xdgA/godot/app_userdata/ExportDivS02/div_s02_state.txt` → `run1,run2`; `find` shows **no** `homeA` dir at all | holds |
| s04 `pck` census | my parser on `out/plain.pck` → `ver=4 version=4.7.2 flags=2 file_base=112 table_ofs=1472 count=7 table_end=1944 tail_bytes=0`, sha `8652a4ac76…` — byte-identical to the pinned literals | holds |
| s05 `heal`: store canary | on disk `cfgA/godot/editor_settings-4.7.tres` = 17,751 B = pinned `17728` + the 23 B crafted marker (E5 mutant line `[23,…]`), so the canary is arithmetic-consistent | holds |

## 4. Required discriminators (per attack class)

- **D1 divergence rows** — (a) content identity must be shown on retained artifacts and the
  digest fields kept unpinned where generation-variable: **landed** (rows pin
  `sha256_equal=true`, `ref_*_match`, `sha_match`, not pack shas; E3 LAW-4 and my GT-3 agree).
  (b) CLI-run provenance must bind the log to the artifact: **gap M1** — require at least one
  engine progress line whose stored-file count matches the directory entry count (or an
  artifact-mtime/process-start ordering assertion), not just the `[ DONE ]` substring.
- **D2 user:// isolation** — two-sided and control-sourced: child must receive a real
  `XDG_DATA_HOME` **and** the default `$HOME/.local` tree must be provably absent, with an
  unset-XDG fallback run as the control: **landed and measured** (M2 flips both predicates to
  false: `store_b_under_xdg=false r3_userdir_under_xdg=false`, `home_store_absent=true` in the
  green run, `run4_userdir_under_home=true` fallback).
- **D3 multi-preset cross-contamination** — content-level, not size-level (GT-5 shows 2,652 B
  packs can differ only by one entry): **landed and measured** — own beacon verified by absolute
  search + directory md5, foreign *name* by directory scan, foreign *bytes* by whole-file search;
  M3 (append foreign beacon) FAILs `a_foreign_content_present`. Residual: bytes placed **outside**
  the artifact file (sibling files, project cache) are outside the row's claim — disclosed.
- **D4 header census** — every pinned header field must be re-derived from artifact bytes and
  the artifact must be shown to be *the one exported* (no echo, no constant):
  **landed and measured** — M4 (flags 2→3 post-export) FAILs `flags_not_2:3`, and my
  out-of-engine parse reproduces all pinned literals (before mutation), plus E4's two-tool
  re-parse. Also verified: `file_base` law matches my independent standalone/embedded pair
  (112 / 104).

## 5. Battery integration state I checked (read-only)

- 16 `export_div_` CASES rows are registered (`run_battery.py:1717-1750`) with the W5
  no-dead-allowlist gate and the family count floor (`:4405-4412`); `cases_integrity` covers the
  `export_div_` prefix (`:4430`).
- **Floor gap (inference from source, exact line):** `r103_export_div_count_floor` is
  `sum(results) == sum(CASES) >= 1`; a synchronized drop (CASES+results shrunk together to ≥1)
  is invisible, and `--min-rows` does not exist in the file (`grep -n "min.rows"` → only the
  comment at `:4406`). E0's own spec §170-172 prescribes freezing the floor to the exact
  registered count. Open integration action, not a fixture defect.
- **s03 cross-row dependency (measured):** `--arm=order` requires the same root to already
  contain the `seq` artifacts. In `fxroot-s03` (seq ran first): `PASS … ref_a_match=true
  ref_b_match=true` with shas `c067122b…`/`d2c25575…`. In a fresh root:
  `FAIL export_div s03 arm=order reason=seq_reference_missing … ref_a_match=false ref_b_match=false`
  with different shas (`b8711546…`/`319d0bd4…`). The battery's CASES order (seq→order→repeat) is
  therefore load-bearing; an isolated/targeted verification run of `order` alone will go red by
  design (`seq_reference_missing`), and pack bytes are generation-state-coupled (GT-3), so any
  future reordering, retry, or parallelization of these rows is a flake source. Disclosed by E3
  (LAW-5); flagged here as measured integration hazard.
- E0's composite `corpus/fixtures/export_div.gd` is **absent** at 21:32 (`ls` → No such file;
  still absent at 21:33 after the M1 re-run);
  the landed `reports/round-103/r103-E0-spec.md` (21:00, 14,172 B) covers the `s01…s05` row
  sets only, and C1's five named surfaces are each covered by a landed sibling fixture. E0's
  shard is stale at the recon line — orchestrator action if the composite row is still wanted.

## 6. Verdicts

| C1 surface | seats | verdict |
|---|---|---|
| preset-vs-`--export-pack` divergence (s01) | E1 | **landed-with-residual** — divergence class reproduced independently (incl. the embedded framing shift); M1 forgery-indistinguishability disclosed with D1b |
| exported-project `user://` isolation (s02) | E2 | **landed** — two-sided, control-sourced; XDG-drop attack FAILs (M2) |
| multi-preset sequential (s03) | E3 | **landed** — contamination insertion FAILs (M3); cross-row `seq` dependency measured, must keep CASES ordering |
| PCK extended header census (s04) | E4 | **landed** — byte-derived (M4) and independently re-parsed (mine + E4's) |
| editor-settings override probes (s05) | E5 | **landed (not attacked in my 4 classes)** — canary arithmetic consistent; E5's own three mutants FAIL-properly |

No C1 receipt was found to be *forged as landed*; the single accepted attack (M1) is a
class-level residual, not a defect in the shipped code. Nothing above contradicts the executors'
own PASS lines; all four mandated attack classes produce the expected verdicts except the D1b
gap.

## 7. Evidence index / hygiene

- My files: `reports/round-103/r103-crit1.md` (this shard);
  `reports/round-103/mutations/r103-crit1_pck.py`;
  `reports/round-103/mutations/r103-crit1_mutants.py`.
- Scratch (retained): `/var/tmp/r103-crit1/{gt,fxc,base,mutroot,fxroot-*,mut-*.out}` — no git
  worktree, nothing to `git worktree remove`.
- No `run_battery.py` run; no shared file touched; joystick device-census tokens never used;
  sibling lanes untouched.
- Unknowns: E0 composite fixture status (absent, reason unknown); whether the count floor will be
  frozen this round; `js0/js1` intermittency not exercised by these rows.
