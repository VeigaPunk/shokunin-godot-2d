# Round 101 — production-shaped headless export capability (Godot 4.7.2.stable)

Godot's export path was exercised end-to-end on a scratch project (2 scenes, 2 scripts,
`icon.svg`, one non-resource `.txt`, 2 presets) with the installed
`~/.local/share/godot/export_templates/4.7.2.stable/` templates, headless, on the loaded
round-101 host. Every byte below is an observed run of this seat; the root finding is that
**exit 0 does not imply a usable artifact**, and that whole-pack `sha256` is not a stable pin.

| Observation (exact command) | Result | Limit |
|---|---|---|
| `godot --headless --path proj --export-pack "Linux/X11" <abs>/base.pck` | exit 0, `GDPC` magic, 3704 B or 4104 B, `project.binary` directory entry present | two byte-images exist — see below |
| same with a **relative** output path `out/base.pck` | exit 1: `ERROR: Save PCK: Can't open file for writing at path "out/base.pck".` + `ERROR: Project export for preset "Linux/X11" failed.` | pins a path contract, not a permission model |
| `… --export-pack "Linux/X11" <abs>/z2.zip` | exit 0, 3775 B, `PK\x03\x04`, 14 entries, sha `0074bbdd0fc0d362…`, 4/4 byte-identical | first zip of the session was a **0-byte file at exit 0** (`BadZipFile`) |
| `godot --headless --main-pack <A>.pck --quit-after 3` | exit 0, `ERROR: Corrupted header in binary project.binary (not ECFG).` + `ERROR: Couldn't load file 'res://project.binary', error code 16.`, **no scene output** | a silent no-run: exit code alone cannot see it |
| `godot --headless --main-pack <B>.pck --quit-after 3` | exit 0, `[scr1] main_scene=main ready`, `[scr1] frame=1..3` | `--quit-after N` = exactly N `_process` iterations |
| `<out>/game.x86_64 --headless --quit-after 3` (exported template + sibling `game.pck`) | exit 0, same frame receipt; binary 73,519,416 B | the production launch path; not a rendering test |
| `<out>/game.x86_64 --headless --main-pack <pck>` | exit 1: ```--main-pack` was specified on the command line, but this Godot binary was compiled without support for path overrides. Aborting.` | `--main-pack` is editor-build-only here; use `/usr/bin/godot` |
| `--export-release "NoSuchPreset" <abs>/nope.pck` | exit 1, `ERROR: Invalid export preset name: NoSuchPreset.` + list of detected presets, no artifact | matches `r6-export-headless.md:8` |
| templates hidden (`HOME`/`XDG_DATA_HOME` redirect) + `--export-release "Linux/X11" …` | exit 1, `ERROR: Cannot export project with preset "Linux/X11" due to configuration errors:` + `No export template found at the expected path:` (`…linux_debug.x86_64`, `…linux_release.x86_64`) + `ERROR: Project export for preset "Linux/X11" failed.` | the missing-template class is a *configuration* error, not a preset error |
| preset swap `run/main_scene="res://alt.tscn"` → `--export-release` → run | `[scr1] main_scene=alt ready` | proves the swap reached the shipped pack |
| preset `Filtered` (`include_filter="res/sub/*"`) | adds the non-resource `res://res/sub/note.txt` and omits `icon.svg.import` + the `.ctex` sidecar that `all_resources` stores | filter semantics observed on the store list only; matcher internals not read |

**Non-determinism (measured, load-bearing).** Twenty identical `--export-pack` invocations produced
two images: **A** = 3704 B with the `project.binary` entry at **size 0** (md5
`d41d8cd98f00b204e9800998ecf8427e` = empty), and **B** = 4104 B with `project.binary` at 392 B (md5
`a93fb0f1ad58ed5446d88d99482b604a`) carrying the `ECFG`-tagged project settings. Sequence:
`A B A A A B A B B B`, then 8×`B`; A appeared only in the session's early window. **A is not merely
different — it is unrunnable**: `--main-pack A.pck` exits 0 without running the game. A third variance
appears after `rm -rf proj/.godot`: the pack re-hashes (`eda5028ebb7294fb…`) although
`project.binary`'s md5 is unchanged — the differing entries are the converted scene blobs, which differ
by exactly one 4-byte field (offset 605: `8a7f3d28` vs `e5a7d707`; **inference**: a re-minted resource
UID — not proven from engine source).

**Relative output paths are project-relative, and no parent directory is created.** `--export-pack
"Linux/X11" out/base.pck` (no `proj/out/`) → exit 1, `ERROR: Save PCK: Can't open file for writing at
path "out/base.pck".`; the same command with a bare `rel.pck` → exit 0 and the artifact appears at
`proj/rel.pck`. The sibling string `Prepare Template: The given export path doesn't exist.` is a second
shape of the same refusal (`r17-export-path-hold.md:3`, `r101-crit5.md:72`). Use absolute paths, or
`.resolve()` as the harness does (`run_battery.py:1853`).

**Exported binary identity (cheap, strong pin).** `sha256(game.x86_64)` =
`d9f79ab89b5ae369aeed11c6052d402e8218cd503bf85b4a235f9c30c46a7c63` = `sha256(linux_release.x86_64)`
of the installed 4.7.2.stable template (73,519,416 B), `version.txt` = `4.7.2.stable`. Pinning size
*and* template sha ties the receipt to the engine build instead of the host
(cf. `r101-crit5.md:74-79`). Discrepancy left open: crit5 also saw a `x.sh` (121 B) side file in its
export; two `--export-release` runs here wrote **no** `.sh` (mechanism unknown — preset-option
difference suspected, not tested).

**Consequences for pin design.** (1) A "determinism" row that pins whole-file `sha256` twice is flaky
by construction — it passes or fails on cache state, not on behaviour; pin the header fields, the entry
census (paths/sizes) and the `project.binary` `ECFG` md5, and back the claim with a runtime receipt.
Sibling seats hit the same wall independently: `r101-mut2.md:67-72` ("two runs produced different
digests … the pack embeds per-run state, so this sha is a per-run receipt, not a stable pin") and a
*silent* rc-0 build with no receipt. (2) Any artifact row must assert `size > 0` **and** parse the
container before any census: exit 0 with a 0-byte zip, and exit 0 with an unrunnable pack, were both
observed live — the exact "size>0 vacuity" and "fake magic" attack classes `r101-crit1.md:6-7` names.
(3) A `--main-pack` row must name its launcher, because the exported template refuses `--main-pack`
outright while the editor binary accepts it. (4) A launch row must pin a **frame receipt**, never the
exit code alone — the shape `corpus/fixtures/export_prod_s04.gd:99-109` landed
(`pack_swapped=3 pack_default=0`).

**Independent corroboration (sibling seats, different scratch projects).** Missing-template class
reproduced with the same two-path error text at `r101-connector.md:141`; `--main-pack --quit-after 3`
frame receipts at `r101-crit5.md:79` and `r101-mut2.md:72-74`; PCK v4 header including an explicit
`dir_offset` documented at `corpus/fixtures/export_prod_s01.gd:15-17` (this seat parsed the trailing
directory rather than using that field).

Not claimed: shipping readiness, asset rights, other platforms, encryption, embedded-PCK, or that the
A/B flip is a bug rather than a cache-state effect. One host, one project shape, Linux/X11 only; the
20-run sequence and the 0-byte zip are single-window observations, and the UID interpretation is
inference. Sibling lattice fixtures had landed (`export_prod_s01/s02/s04/s08/s09/s10.gd`) but their
shards were still plan-only when this lesson was drafted, so no lattice row is validated here.
