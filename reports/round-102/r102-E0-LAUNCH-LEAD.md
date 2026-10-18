# r102-E0-LAUNCH-LEAD — export_launch.gd (C1 launch matrix)

Seat: **E0-LAUNCH-LEAD**. Owned file: `corpus/fixtures/export_launch.gd` only.
Shard artifacts: this file, `reports/round-102/r102-E0-spec.md` (row intents),
`reports/round-102/mutations/r102-E0-m{1,2,3}_*.sh`. `run_battery.py` never run.

Plan (5 lines):
1. Scratch-prove both launch mechanics on /var/tmp/r102-E0 with a two-preset project (embed_pck=true vs stock template), export both, run both ways, capture verbatim rc/output. ✅
2. Author `corpus/fixtures/export_launch.gd` in lane fixture style, arms mirroring the proven runs. ✅
3. Validate the fixture standalone (targeted godot only; never run_battery.py), receipts ×2 where possible. ✅
4. Record row intents (names + pinned expected substrings) in `reports/round-102/r102-E0-spec.md`. ✅
5. Mutants for discrimination evidence if cheap; keep shard < 400 lines. ✅

`uptime` at start: 17:40:40 up 1 day 17:40, load 7.13/8.55/9.21.

## Deliverables

| file | role |
|---|---|
| `corpus/fixtures/export_launch.gd` | lead harness, arms `embed` / `stock` / `probe`, 8 candidate rows |
| `reports/round-102/r102-E0-spec.md` | CASES tuples + discriminators + env notes (r101 spec style) |
| `reports/round-102/mutations/r102-E0-m1_embed_off.sh` | flip embed preset → census row FAILs, boot row survives |
| `reports/round-102/mutations/r102-E0-m2_stock_embed_on.sh` | flip stock preset → census row FAILs, boot row survives |
| `reports/round-102/mutations/r102-E0-m3_refuse_with_editor.sh` | refusal probe with editor binary → refusal row FAILs |

## 1. Scratch mechanics proof (before authoring the fixture)

Project `/var/tmp/r102-E0/proj`: `project.godot` + `export_presets.cfg` with two
Linux/X11 presets (`EmbedPck` embed_pck=true, `Stock` embed_pck=false) + a
`main.gd/_tscn` printing `EXPORT_LAUNCH_MAIN` + `EXPORT_LAUNCH_FRAME n`.
Exports run inside `unshare -m --map-root-user sh -c 'mount -t tmpfs -o size=64M tmpfs /tmp; …'`
(private /tmp for the packer's fixed tmpproject.binary path). Both exports rc=0,
`[ DONE ] savepack` in logs (4.0 s for both, load ~7).

Artifact census (observed `ls -la`):
* `warm_embed.x86_64` 73,521,480 B — single file.
* `warm_stock.x86_64` 73,519,416 B + `warm_stock.pck` 2,056 B.
* delta embed−stock = 2,064 = pck 2,056 + 8; embedded GDPC header sits at
  offset 73,519,416 (= the stock binary's size), trailer last 8 B
  `00000000 47445043`; standalone pck head = `47445043 04000000 …`.

Launch runs (exact commands under `/var/tmp/r102-E0`; `rc` + stdout/stderr):

* `out/warm_embed.x86_64 --headless --quit-after 3` (cwd neutral; then again
  from a dir holding only the copied binary) → **rc=0, stderr 0 B**, stdout:
  `EXPORT_LAUNCH_MAIN boot scene=main` + `EXPORT_LAUNCH_FRAME 1..3`.
* `cd out && ./warm_stock.x86_64 --headless --quit-after 3` (sidecar adjacent)
  → **rc=0**, same 3 frame lines.
* `cd out && ./warm_stock.x86_64 --headless --main-pack warm_stock.pck --quit-after 3`
  → **rc=1, 11 ms**, stdout empty, 265 B stderr (verbatim in spec §4):
  `ERROR: `--main-pack` was specified on the command line, but this Godot binary was compiled without support for path overrides. Aborting.`
  + `use the `disable_path_overrides=no` SCons option` + `at: setup (main/main.cpp:1892)`.
* Same refusal from the **embedded** binary (rc=1, same 265 B) and from the
  stock binary with a **nonexistent** `--main-pack` path — the refusal is at
  arg parse, the file need not exist.
* `godot --headless --main-pack out/warm_stock.pck --quit-after 3` (editor
  build, cwd `/`) → **rc=0**, marker + frames — the pack itself is loadable.
* Stock binary copied **without** its pck, run under `timeout 1` →
  **rc=124**, stdout empty, 275 B stderr:
  `Error: Couldn't load project data at path "...". Is the .pck file missing?`
  + rename-the-exe hint + `at: setup (main/main.cpp:2130)` (process idles).

## 2. Fixture receipts (validated bytes, `corpus/fixtures/export_launch.gd`)

Command shape (identical to battery):
`godot --headless --path corpus/fixtures --script res://export_launch.gd -- --arm=<arm>`

Round A + round B with `EXPORT_LAUNCH_ROOT=/var/tmp/r102-E0/fx`
(2026-10-18, load 7–9): all 6 runs rc=0, stderr **0 bytes**, per-arm wall
3,835/3,943 ms (embed), 3,854/4,321 (stock), 5,566/6,009 (probe);
**PASS lines byte-identical A vs B** (`diff` clean per arm):

```
PASS export_launch embed_boot boot=true frames=[1,2,3] extra=false exit=0 cwd=isolated
PASS export_launch embed_census artifacts=1 sidecar_pck=0 tail_magic=47445043 binary_bytes=73521480
PASS export_launch embed_refusal rc=1 class=path_overrides_disabled hint=disable_path_overrides_no log_bytes=265
PASS export_launch stock_boot boot=true frames=[1,2,3] extra=false exit=0 sidecar=cwd
PASS export_launch stock_census artifacts=2 pck_exists=true pck_magic=47445043 pck_bytes=2056 bin_bytes=73519416
PASS export_launch refusal rc=1 class=path_overrides_disabled hint=disable_path_overrides_no log_bytes=265
PASS export_launch editor_boot boot=true frames=[1,2,3] extra=false exit=0
PASS export_launch hole rc=124 class=project_data_missing pck_hint=true stdout_bytes=0 stderr_bytes=283
```

Battery-shape run, **no env override** (default root resolved to
`/home/vgpnk/.local/share/godot/app_userdata/MechanicOneShotTest/export_launch`):
embed + probe rc=0, stderr 0 B, 4,182/6,121 ms; every pinned prefix
byte-identical; only trailing `stderr_bytes` drifted 283→341 (path length).
`--check-only --script res://export_launch.gd` rc=0.

## 3. Mutation counterfactuals (executed, scripts in mutations/)

| mutant | arm | observed | verdict |
|---|---|---|---|
| m1 embed preset `embed_pck=true→false` | embed | `artifacts=2 sidecar_pck=1 tail_magic=00000000`; boot still passes via sidecar | census row FAILs, boot row survives ⇒ embed/stock split is discriminated |
| m2 stock preset `embed_pck=false→true` | stock | `artifacts=1 pck_exists=false pck_magic=missing pck_bytes=-1`; boot still passes (embedded pack) | census row FAILs |
| m3 refusal probe runs editor binary | probe | `refusal rc=0 class=other hint=missing log_bytes=202`; editor_boot + hole unchanged | refusal row FAILs ⇒ pin discriminates template vs editor build |

## 4. Row intents

8 candidate rows (`export_launch_*`, exact CASES tuples in
`r102-E0-spec.md` §1). No ordering constraints; no `expected_errors` needed
(fixture stderr measured 0 B). Cost: all 8 ≈ 42 s battery time; minimal 4-row
subset (embed_boot, embed_self_contained, stock_sidecar_census,
stock_mainpack_refusal) ≈ 19 s.

## 5. Observation / inference / unknown

* [obs] Every command above; refusal text verbatim; artifact sizes; rc values.
* [inf] The embedded binary is the same template build (same refusal text,
  same `main/main.cpp:1892`); self-containment is the appended pack, not a
  build difference. The editor contrast makes the pack-loadability explicit.
* [unk] Behavior under a different Godot build with `disable_path_overrides=no`
  (not testable on this host); cross-version trailer offsets.
* Residual: `hole` rc=124 needs coreutils `timeout`; sizes/magic pinned are
  engine-version conditional and documented as such in the spec.
