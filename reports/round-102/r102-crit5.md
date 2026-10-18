# r102-C5 — Exposure/wording audit: tps-conditioned pins, host-version receipts, template-path conditionals, load context

Plan (5 lines):
1. Recon: locate export_launch rows + tps-conditioned pins; inventory host receipts (godot version, template install dirs, load) — read r101 adjudicator/scout routing.
2. Probe template-path conditionals on scratch copies under /var/tmp/r102-c5/: does export_launch behavior (refusal class vs run) depend on installed templates? — DONE.
3. Audit wording/pins: enumerate claims that silently depend on host state; produce tightened line-pairs/diffs as shard content (no shared-file edits) — DONE for landed fixtures.
4. Evidence discipline: exact command + verbatim output bytes; label observation / inference / unknown; never pin joystick census tokens.
5. Deliverable: shard + optional mutation script under reports/round-102/mutations/; orchestrator applies/commits.

Host: seat opened 17:41:18 up 1d17h, load 6.06/8.09/9.02; batches at load 7.5→26.5 (sibling
lanes + swarm). `godot --version` = `4.7.2.stable.arch_linux.ed1daf0bf` (all runs 17:41–17:50).
Scratch: `/var/tmp/r102-c5/` (rootfs, 764G avail). `/tmp` = 16G tmpfs 80% used/3.1G avail
(r101 EDQUOT class live, dormant). `unshare -m --map-root-user` works [obs].

## §0 Host receipts (observed bytes)

| receipt | value |
|---|---|
| engine | `4.7.2.stable.arch_linux.ed1daf0bf`; editor banner carries `(2026-08-17 01:18:38 UTC)` |
| editor binary | `/usr/bin/godot` sha256 `3a72f85d53b84d7656ad8a633b06b019a11ad170a5718ff50bacc1c83cd4e72b` |
| templates dir | `~/.local/share/godot/export_templates/4.7.2.stable/` (only 4.7.x dir present) |
| version.txt | `4.7.2.stable\n` (13 B; xxd `342e 372e 322e 7374 6162 6c65 0a`) |
| linux_debug.x86_64 | 73,703,800 B sha256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e` |
| linux_release.x86_64 | 73,519,416 B sha256 `d9f79ab89b5ae369aeed11c6052d402e8218cd503bf85b4a235f9c30c46a7c63` |

## §1 tps-conditioned pins — measured law + census

Probe p1 (`/var/tmp/r102-c5/p1`, script prints process/physics frame counts), one `godot --headless
--path p1 --quit-after 60` per row; load 8.2–7.5:

| shape | rc | wall ms | process frames | last phys frames |
|---|---|---|---|---|
| default r1 | 0 | 1204 | 60 | **23** |
| default r2 | 0 | 1258 | 60 | **23** |
| `--fixed-fps 60` | 0 | 789 | 60 | 60 |
| `--fixed-fps 30` | 0 | 866 | 60 | 119 |

Laws (all [obs] on this host/version):
- L1 `--quit-after N` = exactly N **main-loop** frames; count invariant to load/tps. Process-frame
  vector pins (`frames=[1..5]`, `extra=false`) are exact — r101 export_prod row, r102 s01/s02/E0 all
  rest on this and reproduced.
- L2 physics progression inside those N frames is **wall-clock conditioned** (23 vs 60 vs 119) —
  never derive an expected physics count from `--quit-after` without `--fixed-fps`; note ff30 gives
  119 not 120 (last accumulator not flushed at quit).
- L3 exported template binary inherits L1/L2 (my embedded p2 binary: `--quit-after 5` → frames 1..5, rc 0, 743 ms).

Census (regex over `'PASS ...'` literals, `python3` re on `corpus/fixtures/run_battery.py`):
388 PASS literals; **18 contain `tps=`**, all `tps=60` (geo2d_lattice 5, r90_lattice 12,
r99_audio 1). `corpus/fixtures/project.godot` sets **no** `physics_ticks_per_second`/`max_fps`
[obs] ⇒ those tokens are engine-**default**-conditioned (version-conditioned), not load-conditioned
[inf]. 8 literals contain `frames=`; the C1 one (`export_prod quitframes frames=[1,2,3,4,5]`) is a
process-frame pin ⇒ exact by L1. One real-time boolean pin found outside C1:
`PASS r99_audio pause … frozen_400ms=true` — duration-conditioned; load sensitivity [unknown], flagged only.
No landed export_launch PASS line carries any tps/frames/wall token except process-frame vectors [obs §5].

## §2 Host-version receipts (banner classes, refusal bytes, template identity)

Exported-binary vs editor banner (byte-exact, observed):
- editor: `Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org`
- exported stock/embedded template binary: `Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org`
  (no timestamp; `.official`, not `.arch_linux` — r101-crit5 F7 restated and re-measured).

`--main-pack` refusal on the exported binary (embed and sidecar both, rc=1, 13–17 ms) — byte-exact:
```
ERROR: `--main-pack` was specified on the command line, but this Godot binary was compiled without support for path overrides. Aborting.
To be able to use it, use the `disable_path_overrides=no` SCons option when compiling Godot.
```
(the r101-crit5 quote omitted the backticks; substring pins like s03's `class=path_overrides_disabled`
+ `disable_path_overrides=no` are unaffected, but quoted excerpts should use the byte-exact text.)

Template identity (r101-crit5 F4 requirement — size/magic pins must cite it): `version.txt`
`4.7.2.stable` + template sha256s in §0. Measured byte-copy property: `--export-debug` sidecar binary
sha256 == `linux_debug` template sha (`1a291d3d…`); `linux_release` used by s01/s02/s05
(73,519,416 B; s02 `bin_eq_template=true`, s01 `template_bytes=73519416` in their PASS lines).

Wording census (17:47:29Z, 61 shards in reports/round-102/): 31 cite `4.7.2`, 53 cite
`uptime`/`load average`. Landing requirement stands (r101-crit5: every row's evidence chain carries
engine hash + batch load + scratch filesystem).

## §3 Template-path conditionals (pin the dependency)

- **Present** (`XDG_DATA_HOME` unset): `--export-debug/--export-release/--export-pack` rc=0 `[ DONE ]`;
  artifacts land; sidecar binary is the template byte-copy; debug export pck 1944 B (minimal project).
- **Absent** (`XDG_DATA_HOME=/var/tmp/r102-c5/xdg`, empty): export rc=1, verbatim stderr:
```
ERROR: Cannot export project with preset "Linux/X11" due to configuration errors:
No export template found at the expected path:
/var/tmp/r102-c5/xdg/godot/export_templates/4.7.2.stable/linux_debug.x86_64
No export template found at the expected path:
/var/tmp/r102-c5/xdg/godot/export_templates/4.7.2.stable/linux_release.x86_64

   at: _fs_changed (editor/editor_node.cpp:1401)
ERROR: Project export for preset "Linux/X11" failed.
   at: _fs_changed (editor/editor_node.cpp:1417)
```
- **Wrong version**: XDG dir containing only `4.7.1.stable/` (version.txt `4.7.1.stable`, binaries
  symlinked from the 4.7.2 install) → same refusal class, expected path cited as
  `…/export_templates/4.7.2.stable/…` ⇒ resolution is keyed to the **exact engine version string**
  [obs]. s02's `_template_path()` implements this keying (`Engine.get_version_info()` + version.txt
  match) [obs file]; s01 checks `HOME/.local/share/.../<ver>/` candidates likewise.
- Class string `No export template found at the expected path:` is stable; the path inside it is
  root-dependent (XDG or absolute scratch) ⇒ **never pin the path**, pin class + presence.
- Dependency-pin demands: each C1 row must either (a) carry template identity evidence (version.txt +
  sha256) in its shard/receipt, or (b) fail closed on absence. Landed status: s01 `template_not_found`
  FAIL; s02 `template_binary_not_found` FAIL; s03 `no_stock_template_binary` FAIL; s04 rejects
  `pbin_zero`; s05 reads templates directly — all fail-closed [obs file]. Supply (a) in the round
  record (this section is that receipt).
- **Packer /tmp conditional**: today no-unshare export rc=0, pck byte-identical to the unshare run
  (sha `4664c4ae5e4313891b17ea13922b4ed3d5dc978f22370921728182d9ec603378`), boots rc=0 ⇒ EDQUOT
  class dormant; under EDQUOT the export still exits 0 with a broken pack (r101 E0), so rows must
  assert boot/`pbin_size`/`pbin_ecfg`, never export rc alone. Landed fixtures do [obs §5].

## §4 Load context / bound class

Independent arm runs of the landed fixtures (scratch copies of `corpus/fixtures/{project.godot,
export_presets.cfg,<fixture>}`, roots under /var/tmp; command shape
`EXPORT_LAUNCH*_ROOT=<root> godot --headless --path <proj> --script res://<fixture> -- <arm>`):

| fixture arm | rc | wall ms | load |
|---|---|---|---|
| export_launch.gd embed | 0 | 3836 | ~18 |
| export_launch.gd stock | 0 | 3613 | ~18 |
| export_launch.gd probe | 0 | **5853** | ~18 |
| s01 embed (`--arm=embed`, sha 9b3d5a92) | 0 | 6559–6791 | ~25 |
| s01 neg self-export (`--arm=neg`) | 0 | **8475** | ~25 |
| s02 embed | 0 | 3932 | ~18 |
| s02 contrast | 0 | **5960** | ~19 |
| s03 all (sha 738bf2a6, FAIL) | 1 | 6004 | ~24 |
| s04 both (2 roots) | 0 | 6264 / 6168 | ~25 |
| s05 tmpl / tags | 0 | 914 / 4076 | ~25 |

Bound facts: `run_battery.py:1913` `timeout_seconds = 60 if script.startswith("__godot_export") else 8`
(unique anchor, grep -c = 1). Planner S4 trigger condition ("any E receipt wall > ~5 s") is **met**:
4 arms ≥5.85 s, one (s01 neg first-run leg) 8.475 s > 8 s. Margin at load 18–26 is 1.2–1.4×; r101
s10 precedent 6.7 s; r92-F1 inflation class (2.4–11.6×) crosses it. Proposed orchestrator line-pair
(run_battery.py:1913, shared-file edit is orchestrator's):
`-        timeout_seconds = 60 if script.startswith("__godot_export") else 8`
`+        timeout_seconds = 60 if script.startswith(("__godot_export", "export_launch")) else 8`
No PASS line found in any landed fixture carries a wall/ms token [obs grep + run outputs]; keep it so.

## §5 Landed-fixture audit (current bytes at read time; E-seats still editing — shas matter)

Fixtures present 17:50: `export_launch.gd` `a3567335…`, `export_launch_s01.gd` `9b3d5a92…`,
`s02` `3909882f…`, `s03` `738bf2a6…` (varies minute-to-minute), `s04` `6b11f1fa…`, `s05`, `s06` landed.

**F-C5-1 HIGH — s01 `_parse_binary` reads the wrong trailer field (currently in-tree, reproduced ×2).**
`s01.gd:294-301` seeks `binary_bytes - 16` then reads a u32 from the first 4 of those 16 bytes; the
real trailer is `[u64 pack_size][u32 GDPC]` in the **last 12** bytes. Result: `pck_bytes=0`,
`accounting_exact=false` in its own PASS line, and its stated structural proof (head comment lines
8–14) is falsified by its own receipt. Byte proof on its produced binary
(`/var/tmp/r102-c5/s01root/s01/iso/embed.x86_64`, 73,521,480 B): last16
`00000000040800000000000047445043`; u32@[-16:-12]=0 (what s01 computes) vs u64@[-12:-4]=2052 (true);
`73519416+2052+12 == 73521480` → accounting **true** if read right; PCK head at template boundary =
`GDPC` [obs]. Minimal fix line-pair (fixture owner/orchestrator): seek `binary_bytes - 12`, read 12 B,
`pck_bytes = int(tail.decode_u64(0))`, `trailer_magic = tail.slice(8,12) == "GDPC"`. Until fixed, a
row pin must NOT include `accounting_exact`/`pck_bytes` (pin through `trailer_magic=true`).

**F-C5-2 HIGH — s03 `_parse_pack` ECFG check omits `file_base`; `--arm=all` FAILs reproducibly.**
Entry offsets in a v4 pack are relative to `file_base` (`decode_u64(0x18)`; 112 here). s03 reads
`bytes.slice(offset, offset+4)` at the relative offset: measured `b[1184:1188]='xpor'` vs correct
`b[1296:1300]='ECFG'` in its own produced pack `/var/tmp/r102-c5/s03root2/out/s03.pck` (2056 B, 7
entries; the pack itself is valid — I re-parsed it and booted it with the editor: `S03_MARKER`,
frames 1–3, rc=0 [obs]). Consequence: every fresh export is judged `pbin_ecfg=false` →
`FAIL export_launch_s03 all reason=export_pack_unusable rc=0 pbin_size=-1` (the `-1` is the empty
`_pack` default — the message is misleading; print the last parsed info instead). Two runs on sha
`d1d64b70` and `738bf2a6`, fresh roots, rc=1, walls 5754/6004 ms [obs]. Fix: add
`var base := int(bytes.decode_u64(0x18))` and read ECFG at `base + offset` (export_prod.gd's parser
already does `base + foff`).

**F-C5-3 MEDIUM — arm/flag contract vs planner's placeholder registration.** Planner §2.2 shows
`flags []` for all rows. Measured: `export_launch.gd` and `export_launch_s01.gd` have **no default
arm** → running with `flags []` yields `FAIL export_launch  reason=unknown_arm` rc=1 (measured for
both, 860 ms / 0.9 s) — i.e. row registration must carry per-row arms: E0 `--arm=embed|stock|probe`;
s01 `--arm=embed` and `--arm=neg` (optionally `--reuse` when the neg row follows the embed row in the
same root — the reuse target is variant `s01neg`, so a first run self-exports, see §4 timings);
s02 `[]` (defaults to embed) + `--arm=contrast`; s03 `--arm=all|refuse|contrast|sibling`;
s04 `[]` (defaults to both); s05 `--arm=tmpl|tags|tagsdbg|custctl|arch|tex_on|tex_off`.

**F-C5-4 — s02 pin hygiene.** Its embed PASS line ends with `… exit=0 bin_bytes=73521464
template_bytes=73519416 pack_bytes=2036 proj=/var/tmp/r102-c5/s02root/embed/proj` — an absolute host
path inside the PASS line. Row signature must stop at `exit=0` (or the fixture must move `proj` to
DIAG); `bin_bytes/template_bytes/pack_bytes` are host-template conditioned → cite template identity
(§0) rather than making them the discriminator. s04's two-root counterfactual: PASS lines byte-identical
across roots `/var/tmp/r102-c5/s04root_a` vs `…/s04root_bbbb` incl. `bytes=2624/2200` and
`names_sha256` [obs diff → IDENTICAL], so its size pins look root-stable for this shape (still leave
trailing per r101 law).

**Positive receipts:** s05 tmpl emits in-band host receipts (`version=4.7.2.stable
tmpl_dir=4.7.2.stable`) and its feature-vector digests reproduced exactly on my independent runs
(`edit_sha256=95d8fa49…`, `vec_sha256=1adac65f…` — same values its head comment quotes). s02
`trailer_gdpc/trailer_size_consistent/pack_magic_at_start` = correct trailer semantics (contrast with
F-C5-1). s03's staging cross-checks the staged binary sha against the template sha (hardlink-or-copy)
[obs file]. No joystick/device tokens in any C1 PASS line.

## §6 Demands for the orchestrator (hold-lines)

1. s01 fix (F-C5-1) before pinning its line — or pin `… trailer_magic=true` prefix only; never pin
   `accounting_exact=false pck_bytes=0`.
2. s03 fix (F-C5-2, add `file_base`) before registration — otherwise the row is red by construction;
   also fix its FAIL message to print the parsed info, not the empty-`_pack` default.
3. Registration flags per F-C5-3; do not use blanket `[]`.
4. Bound: land the run_battery.py:1913 line-pair (§4) or publish the envelope; s01 neg's user-visible
   first-run leg is 8.475 s at load 25 (already over the 8 s bound).
5. s02 row signatures end at `exit=0` (F-C5-4); never pin `proj=`.
6. Shard/round-record evidence chain: engine hash + load + scratch fs (census §2) — 31/61/53 today.
7. Template dependency: cite version.txt + template sha (§0/§3) in the E0 spec / round record.
8. Byte-exact refusal quoting (backticks) in E3's shard/pins; substring class tokens unaffected.

## §7 Wave 2 (17:51–17:52) — status deltas; supersedes §4/§5/§6 status where conflicting

- **F-C5-1 CLOSED by author**: s01 current sha `2caa159b…` prints `accounting_exact=true pck_bytes=2052`
  — exactly the value my byte analysis computed (`73519416+2052+12==73521480`); wall 4544 ms @ load 20.7
  [obs `out/rc1_s01.log`]. Its structural chain may now be pinned in full.
- **F-C5-2 STILL OPEN**: s03 current sha `ef9cb857…` still FAILs `export_pack_unusable` (5346 ms).
  Its own new diagnostic closes the mechanism: `S03_DIAG all pack_probe=pass=1 … bytes=2056 magic=GDPC
  dir_off=1584 entries=7 pbin_size=273 pbin_ecfg=false` and byte-identical `pass=2` line — entry found,
  ECFG false. Line 389 still `bytes.slice(offset, offset + 4)`; grep finds no `decode_u64(0x18)`
  anywhere in the file [obs]. Demand 2 stands; the `pbin_size=-1` in the FAIL line is the empty-`_pack`
  default and should be replaced by the parsed info.
- **s06 audited** (sha `336768ae…`): `--arm=refusals` rc=0 **7919 ms** — 4 PASS lines, verbatim classes
  `could_not_load_patch_pack` (missing + nonpack), `missing_patches_list`, `invalid_export_preset_name`
  + `patch_load_reached=false`. `--arm=base` rc=0 **8116 ms** (> 8 s bound) — 3 PASS lines:
  `s06_base magic=GDPC count=8 flags=2 pbin_size=265 payload_size=11 names_sha256=3ffe3cd9… bytes=2100`;
  `s06_base_det equal=true diff=0 samples=2 bytes=2100`; `s06_fallback exit=0 count=8
  equal_to_base=true bytes=2100`. No tps/wall tokens; s06 root-stability of `bytes=`/digests [unknown].
  s06 also has an `unknown_arm` branch (line 106) ⇒ F-C5-3 applies to it: explicit `--arm=` per row.
- **Bound ledger (load 19–26)**: over 8 s — s01 neg 8475, s06 base 8116. ≥5.8 s — s06 refusals 7919,
  s04 6264/6168, s03 6004, s02 contrast 5960, E0 probe 5853. Demand 4 upgraded: the
  `run_battery.py:1913` line-pair is required for a green first run, not optional.
- Evidence adds: `out/{rc1_s01.log,rc1_s03.log,s06_refusals.log,s06_base.log}`.

## §8 Wave 3 (17:52–17:53) — spec reconciliation + final fixture states

- **E0-spec pins verified against current fixture `a3567335…`**: fresh runs emit `tail_magic=47445043`
  (embed) and `pck_magic=47445043` (stock) — hex, matching `r102-E0-spec.md` §1 pins. (An intermediate
  revision observed at 17:45 emitted ASCII `tail_magic=GDPC`; superseded — do not pin ASCII.)
  E0 rows carry explicit `--arm=` in-spec, agreeing with F-C5-3.
- **E2-spec rows are pin-hygienic already**: embed signature stops at `exit=0` (before
  `bin_bytes…proj=`), contrast at `without_pck_killed=true` — F-C5-4 resolved in-spec; the orchestrator
  must splice those strings verbatim (both rows explicit `--arm=`).
- **E4-spec**: pins stop before `bytes=`; its timeout note independently recommends the family-bound
  extension or the `--arm=lower|upper_excl` fallback (2.5–3.4 s) — consistent with §4/§7.
- **s01 fix holds on a second revision**: `cedd9b35…` embed PASS `accounting_exact=true pck_bytes=2052`
  (4194 ms @ load 17.9) [obs `out/rc3_s01.log`].
- **s03 at 17:53 = sha `e488da21…`, mid-edit and currently unloadable**: `SCRIPT ERROR: Parse Error:
  Function "_pack_gate()" not found in base self` at 415/431 → `Failed to load script`, rc=1, 851 ms
  [obs `out/rc2_s03.log`]. Do NOT register s03 until its shard is DONE and a fresh `--arm=all` run
  passes; the F-C5-2 base-offset fix must land with it.

## §9 Status + evidence index

Audit complete: E0 + s01–s06 probed at their live revisions; two defects found (s01 fixed by author,
re-verified ×2; s03 open — base-offset + currently mid-edit parse break), spec/pin hygiene checked
against E0/E2/E4 registration specs, bound ledger with two over-8 s arms delivered. No shared file
edited; `run_battery.py` never run; no commits.
Evidence: `/var/tmp/r102-c5/out/` (`p1_*.log`, `p2_*.out|err`, `embed_plain/embed_mainpack/sidecar_*`,
`s01_*.log`, `s02_*.log`, `s04_*.log`, `el_*.log`, `el3_*.log`, `x_*.log`, `rc1_*.log`, `rc2_s03.log`,
`rc3_s01.log`, `s06_*.log`), binaries/packs/roots under
`/var/tmp/r102-c5/{p1,p2,p2b,p2c,el3,s01root,s03root2,rc1root_*,rc2root,rc3root,s06root}/`.
