# r101-crit5 — CRIT-5 exposure/wording audit (C1–C3)

Plan (5 lines):
1. Capture load + host-version receipts (uptime, godot --version) as audit baseline.
2. Audit wording discipline: tps-conditioned pins, host-version receipts, load-conditioned receipts across C1/C2/C3 artifacts.
3. Re-derive r92 F1 timeout-flake class and r87 probe-sha transition precedent; apply as audit criteria.
4. Run targeted headless godot probes on scratch projects under /var/tmp/r101-crit5/ to test any exposure claims that are cheaply falsifiable.
5. Write findings (observation vs inference vs unknown), each with exact command + observed bytes.

## 0. Baseline receipts (observed)

```
$ uptime  (16:21:27)
 16:21:27 up 1 day, 16:21, 1 user,  load average: 41.13, 21.77, 13.87
$ godot --version
4.7.2.stable.arch_linux.ed1daf0bf        (/usr/bin/godot)
$ cat ~/.local/share/godot/export_templates/4.7.2.stable/version.txt
4.7.2.stable
$ ls .../4.7.2.stable/linux_release.x86_64  -> present (73519416 bytes)
```

Pre-transition fixture/harness hashes (16:21:53, load 37.32):

| artifact | sha256 |
|---|---|
| corpus/fixtures/run_battery.py | `c4db615394934140e7fee285ac83528ceb8fdedb975212c0d685b00f28b40076` |
| corpus/fixtures/r100b_seq.gd | `4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd` |
| corpus/fixtures/r100b_phase.gd | `49298e6cc18c4e0de627105b9d95ff28ed2ccfa52bb1cc2da364b76d5430d4b7` |
| corpus/fixtures/dss_lattice.gd | `77ae4adb8a47ccf50b5da345720247c035418e31872a117d17cd98913f479627` |
| corpus/fixtures/r95b_order.gd | `4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490` |
| corpus/fixtures/export_presets.cfg | `0b321c1c866e5d61e5e4fe8842fe8552f8d6cac3c9b7659f285f2c15b59ba694` |

Harness facts (observed in bytes): launch shape `godot --headless --path <scratch> --script res://<fixture> -- <flags>`
(`run_battery.py:1862`); bound `timeout_seconds = 60 if script.startswith("__godot_export") else 8`
(`run_battery.py:1863`); seq rows at `run_battery.py:1640-1643` pin ONE line each
(`... cursor c0=(30.0, 14.0) ...` / `... hover h0=P ...`), substring-classified.

## 1. Findings

### F1 — MEDIUM (host class, measured) · `/tmp` is quota-cramped right now; receipts written there are corrupted or lost

`df -h /tmp` = 16G tmpfs, **80% used, 3.1G avail**. My first replay batch (load 52–55) wrote to
`/tmp/r101-crit5/out`: of 6 batch line-captures, 2 `echo` appends failed with **`Disk quota exceeded`**;
one transcript logged `rc=0` with **0 lines** and another with **8 lines**; one 23-line transcript
suffered a mid-line cut and merge (5 content lines lost). The same commands re-run on `/var/tmp`
(root fs, 771G avail) were **11/11 byte-identical** (F2). ⇒ verdict: those artifacts are the
**filesystem class**, not engine flakiness — do not file them as pin defects.
Wording consequence: any r101 seat whose scratch/exports live under `/tmp/r101-<key>/` must
(a) probe with `df` + a write test first, (b) move to `/var/tmp/` when >~75% or on any EDQUOT,
(c) record which fs the receipt lives on. `r100-critic` set this precedent; E-seats' export
output (~75MB per binary) must NOT land on `/tmp` at 80% full.

### F2 — INFO (positive) · the 14-cell replay transcript is stable and tps-invariant

`/var/tmp/r101-crit5`: `godot --headless --path proj --script res://r100b_seq.gd -- --clean=1`
×8 reps + `--fixed-fps 30` + `--fixed-fps 120` ×2 (load 56.7→58.0): **11/11 transcripts byte-identical**,
sha256 `2181f1ebcb5a516897f403eb8c56a9b544e1a0350904d83de213bb094736a079`, 23 lines, wall
1541–1725 ms (default) / 865–935 ms (fixed-fps). ⇒ the C2 full-replay pin content has **no
tps-conditioned token** (default-60tps vs ff30/ff120 identical), and the row wall is ~4.7× under
the 8 s bound at load ~57. The wording criterion stands anyway: a pin may only claim stability
for launch shapes it measured; the battery's own shape is default (no `--fixed-fps`).

### F3 — MEDIUM (C1 exposure, measured) · a nested export inside one 8 s-bounded fixture row has only ~2× headroom

Production shape proxy `exp_probe.gd` (SceneTree fixture calling `OS.execute(godot, [... "--export-release" "Linux/X11" <abs>.x86_64])`),
3 reps at load 58.6→57.5: outer wall **3864 / 3803 / 3900 ms** (inner export 3120/3110/3174 ms), rc=0.
Direct exports (`--export-release`, absolute path, load 58→63): **4002 / 5803 / 3137 ms**; `--export-debug` 3154 ms.
⇒ one nested export ≈ 3.8–3.9 s today vs the 8 s fixture bound — margin ≈ 2×; a single 2.1× load
inflation of the inner export (r92 F1 measured 2.4–11.6× for a different heavy path) crosses it.
Recommendation for C1: rows that nest an export must either be named with the `__godot_export` prefix /
carry an explicit 60 s-class bound at integration, or the shard must publish this margin envelope as a
known red mode. Also: relative export paths FAIL (`export path doesn't exist`, rc=1 — measured);
the harness shape resolves the path (`run_battery.py:1853 .resolve()`) — copy that.

### F4 — INFO (positive + criterion) · exported binary receipts

`--export-release` output is the template byte-copy plus side files: `x.x86_64` 73519416 bytes =
template size; sha256(x.x86_64) vs sha256(linux_release.x86_64 template) recorded in receipts
(see evidence). `x.pck` 1420 bytes + `x.sh` 121 bytes also written. `--main-pack` run receipt:
(see section 2). Wording criterion: any export-lattice pin that asserts size/magic must cite the
**template identity** (version.txt `4.7.2.stable` + template sha) — size alone transfers across hosts.

### F5 — INFO · host-version / load receipt census across r101 shards (as of 16:22)

Of 60 `reports/round-101/*.md`: **12 cite `4.7.2`**, **31 cite `uptime`/`load average`**, 8 cite neither.
Landing requirement (wording discipline): every row's evidence chain in the round report should
inherit (a) `godot --version` = `4.7.2.stable.arch_linux.ed1daf0bf`, (b) the load figure for the batch,
(c) which scratch filesystem held the receipt (F1). In-progress shards are exempt until their
findings exist; the census is a prompt, not a defect list.

### F6 — INFO · probe-sha transition discipline (r87 precedent applied)

Baseline shas in §0. r87 precedent (`r87-critic.md` F1 correction: "it changes the probe sha and
invalidates that citation"; `r87-simplifier.md:178` same). Criterion for C2/C3 landings:
if any seat edits a fixture file (`r100b_seq.gd`, `dss_lattice.gd`, …), the landing must (1) print
old→new sha256 for that file, (2) name every CASES comment/evidence string and receipt that cited the
old sha and is now invalid, (3) re-run the affected receipts. If the fix is harness-side only
(new evidence strings, same fixture bytes), the fixture shas above stay valid — state that explicitly.

## 2. Evidence index (all under /var/tmp/r101-crit5/, /var/tmp/r101-crit5-exp/)

| receipt | path |
|---|---|
| replay v2 times + 11 sha-identical transcripts | `out/t1v2.times`, `out/replay_v2_*.log` |
| `/tmp` EDQUOT-corrupted batch (class evidence) | `/tmp/r101-crit5/out/replay_default_5.log` (18 lines, mid-line cut), `replay_default_9.log` (0 lines, rc=0), `out/t1b.times` (2 lost appends) |
| export times (direct + debug) | `out/t2v2.times`, `out/exp2_rel_*.log` |
| nested-export proxy | `out/t3.times`, `out/nested_*.log`, `/var/tmp/r101-crit5/proj/exp_probe.gd` |
| crash-row timing | `out/t4.times`, `out/crash_*.log` |
| exported binary + template + pck runs | `out/run_nopack.log`, `out/run_mainpack.log` (fill below) |

## 3. Findings — second wave (inside the live landing artifacts)

### F7 — HIGH (C1 feasibility, measured) · `--main-pack` works on the **editor** binary only; the exported template binary aborts

Four launch forms measured (load 51.8) with the same PCK from a real `--export-release`:

| form | command | result |
|---|---|---|
| editor + `--main-pack` | `godot --headless --main-pack <abs>/s.pck --quit-after 5` | rc=0, 1022 ms, prints banner `4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC)` + `MAIN_SCENE_READY marker=r101crit5 scene=main` |
| **exported binary + `--main-pack`** | `proj/out/s.x86_64 --headless --main-pack <abs>/s.pck --quit-after 5` | **rc=1, 52 ms**: `ERROR: --main-pack was specified on the command line, but this Godot binary was compiled without support for path overrides. Aborting.` (+ `disable_path_overrides=no` hint, `at: setup (main/main.cpp:1892)`) |
| exported binary, sidecar PCK | `proj/out/s.x86_64 --headless --quit-after 5` (s.pck adjacent) | rc=0, 744 ms, `MAIN_SCENE_READY` (auto-loaded) |
| exported binary, embedded PCK | preset `binary_format/embed_pck=true` → `e.x86_64` 73521280 B = template+1864 | rc=0, 800 ms, `MAIN_SCENE_READY` |

Exported-binary banner says **`4.7.2.stable.official.ed1daf0bf`** (editor says `.arch_linux`) — any pin capturing the exported binary's banner must pin `.official`, and it transfers only across official-template hosts.
Receipts: `sha256(linux_release.x86_64 template) = sha256(x.x86_64) = d9f79ab89b5ae369…` (executable is a byte-copy of the template when the PCK is separate); `x.pck` = 1420 B sha `af1586794bf38ad6…`.
Wording requirement for E4/E5/E9/E11-style rows: state **which binary** carries `--main-pack` (editor via `OS.get_executable_path()` under `godot --script` — that is what E1's `export_prod_s01.gd:413` does, feasible; mut02 uses `args.godot`, feasible). A row that launches the *exported* binary with `--main-pack` is unsatisfiable on this host — deterministic rc=1, not a flake.

### F8 — HIGH (C1 exposure, measured) · s10-shaped export rows take ~6.7 s against the 8 s fixture bound

`export_prod_s10.gd` run from a scratch copy at load 50.9 (`SCRATCH_ROOT` redirected to `/var/tmp` in the copy only; repo file untouched): `rc=0`, **WALL_MS=6719**, 56 lines, final line `PASS export_prod_s10 icon_pack_entries=3 … forgeries_rejected=4/4`. Margin to the 8 s bound = **1.19×**; any ≥20 % inflation crosses it (r92 F1 measured 2.4–11.6× inflation for a heavy row under sibling load; the same class applies to two nested exports + pack census). Direct exports in the same window: release 3137/4002/5803 ms, debug 3154 ms; nested-export-in-fixture proxy 3803–3900 ms.
Requirement: export-bearing rows need the 60 s class at registration (only `script.startswith("__godot_export")` gets it today, `run_battery.py:1863`), or a publishable margin envelope naming this red mode. E10's default scratch (`/tmp/r101-E10`) sits on the EDQUOT-prone fs (F1) and the arm performs two exports — double exposure. Same for s02 (`/var/tmp` default — safer) and any s01 row that exports executables.

### F9 — INFO (positive audit of the C2 artifact) · `r101_seqfull.gd` transcript shape is sound

`godot --headless --path proj --script res://r101_seqfull.gd -- --clean=1` ×2 (load 54.2 / 51.2): rc=0, **1513–1579 ms**; stdout 19 lines = banner + blank + `SEQ_BEGIN cells=14 clean=1 pins=14` + **14 contiguous `PASS r100_gui …` lines** + `SEQ_CENSUS identical=10 divergent_n=4 divergent=[cursor|touch|subvp|warp]` + `SEQ_END digest=5be029c7d129bf6d…`; stderr = the 6-line `ERROR: Parameter "t" is null.` block (`_cell_render (res://r101_seqfull.gd:808)`). stdout sha256 identical across reps: `2fa3673312f1eeca…`. The 14 cell lines are **byte-identical to the r100b_seq replay** (extracted-PASS-line diff → identical), and `identical=10 / divergent 4` matches r100-critic §F2 cell-for-cell.
Capture-mode nuance (wording): the harness classifies the **concatenated** blob (`output = proc_stdout + proc_stderr`, `run_battery.py` execute), where `SEQ_BEGIN…SEQ_END` is contiguous; a shell `>f 2>&1` instead interleaves the ERROR block after the `focus` line. Pin/validator authors must derive pins from the concat shape (mut01.py exposes a `transcript_shape` probe). Row wall ≈ 1.5 s → 5.3× margin, no timeout risk.

### F10 — INFO · probe-sha transition discipline, applied and re-verified (16:27, load 49.5)

Current shas: `run_battery.py c4db6153…` (unchanged), `r100b_seq.gd 4718a19e…` (**unchanged** — so the CASES comment citation at `run_battery.py:1543` stays valid), new fixtures `r101_seqfull.gd 426075c8…`, `r101_ytrans.gd 0d5093d6…`, `export_prod_s10.gd 55ac8760…` (all untracked new files; adding a new fixture invalidates nothing, but each new row's evidence must carry its fixture sha).
Exemplary in-fixture pattern: `r101_ytrans.gd --arm=census` pins `r95b_offy_tokens=0 r95b_lines=778 r95b_sha256=4f7e945e…` — measured from the committed bytes (matches my baseline), so any later edit to `r95b_order.gd` flips the row loudly (r87 transition law enforced by construction). Criterion for the C1 fixtures: their census rows should pin source sha the same way instead of a bare size/magic.

### F11 — INFO/medium (wording) · tps- and timing-token census on the live C1/C3 artifacts; hold these lines at integration

* **No PASS line carries a wall-clock token today** (s10: `PASS export_prod_s10 icon_pack_entries=… forgeries_rejected=4/4`; s02: `PASS export_prod_s02 entries=… payload_hashes=…`) — but both fixtures print timing diagnostics on stdout (`export_prod_s01.gd:193` `ROW R0b export_child_rc=0 wall_ms=%d …`, `export_prod_s02.gd:506` `EXPORT_PROD_S02 total_seconds=%.3f`). Any row that pins those lines inherits the load-flake class by construction: they must stay outside authorable signatures as the fixtures themselves say for `_diag`-style lines.
* **`--quit-after N` receipts** (E4/E11 shape): N is an engine **frame count**, not seconds — tps-invariant and load-invariant; keep it that way (never pair it with an elapsed-seconds token).
* **tps-conditioning**: replay transcript is identical at default/ff30/ff120 (F2). `r101_ytrans.gd` ladder values are physics-frame indices `t2…t64` — tps-invariant by construction — but its only tps readout (`env tps=%d pf=%d proc=%d`, `r101_ytrans.gd:81-84`) is `_diag`-only, so a launch under a non-60-tps project would be invisible to the row. Today the fixtures project sets no `physics_ticks_per_second` override and the battery never passes `--fixed-fps`, so the exposure is theoretical; record it as a stated limit, not a measured guarantee.

### Wording census, second pass (16:28, 64 shards)

37/64 shards cite `4.7.2` (was 12/60 at 16:22), 52/64 cite load. Landing requirement: the round report's per-row evidence should carry (a) `4.7.2.stable.arch_linux.ed1daf0bf`, (b) batch load, (c) scratch filesystem. `--main-pack` is named in E4/E5/E9/E11 + ver1/2/4/14/15 shards — F7 binds all of them.

## 4. Status

All planned batches complete (T1–T7 + launch-form matrix + F7 matrix). Criteria (F1–F10) are ready to apply to the integration delta. Nothing edited outside this shard; no battery run; no shared file touched.

## 5. Evidence index — additions

| receipt | path |
|---|---|
| ytrans arms (timed) | `out/t5.times`, `out/yt_*.log` |
| seqfull (2× stdout/stderr/concat + interleave) | `out/t6.times`, `out/sf_stdout_*.log`, `out/sf_concat_*.log`, `out/sf_interleave_*.log` |
| s10 real row | `out/t7.times`, `out/s10_run.log` |
| F7 launch matrix | `proj/out/s.x86_64`, `e.x86_64`, `s.pck`; `out/a_run_sidecar.log`, `out/b_run_embed.log`, `out/c_editor_mainpack.log`, `out/d_bin_mainpack.log`; export_presets edits only in `/var/tmp/r101-crit5-exp/proj/` |
