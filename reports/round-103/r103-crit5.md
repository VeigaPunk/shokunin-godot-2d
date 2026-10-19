# r103-crit5 — C5 Exposure/wording audit (tps/load conditioning, host-version pins, template-path conditionals, XDG/env dependence of E2)

Plan (5 lines):
1. Locate E2 fixture arm + run_battery invocations; extract every env/tps/host-version/template-path conditional.
2. Test XDG override behavior of E2 under scratch runs (HOME vs XDG_DATA_HOME/XDG_CONFIG_HOME divergence), tps/load conditioning claims.
3. Audit wording: claims in fixtures/reports that assert host-specific behavior vs observed bytes.
4. Cite exact command + observed output bytes per measurement; label observation/inference/unknown.
5. Keep <400 lines; shard-only output (no shared-file edits).

Host at seat start (C5 completion attempt 3): `2026-10-18 20:55:36 up 1 day, 20:55, 1 user, load average: 1.94, 1.79, 1.64`.
Base commit 6e3e87f7 (r102 close). Scratch root: `/var/tmp/r103c-C5/` (never `/tmp` — EDQUOT).
Sibling-lane note: a concurrent lane may run; load re-recorded per measurement below.

Audit axes for this seat (exposure = what a reader/verifier outside the run can see):
1. Host-version pins + template-path branches (`export_div_s02.gd:_template_exists`) vs on-disk reality.
2. XDG/env dependence of the E2 fixture: which env vars are pinned, which are inherited-but-unmeasured.
3. Wording: every load/timing/tps claim in r103 shards + landed artifacts vs measured bytes.
4. Exposure: absolute host paths / device-census tokens leaking into pinned PASS text or into committed artifacts.
5. Probe-granularity vs artifact-size claims (scratch root fallbacks, `/tmp` EDQUOT class).

**Status: COMPLETE.** Load series during the seat: `1.94 → 13.66 → 12.40 → 11.66 → 10.23 → 9.97`
(a sibling lane and other seats were active; every timing datum below carries its load).
All engine work was targeted `godot --headless` on scratch under `/var/tmp/r103c-C5/` (36 evidence files:
`s02` receipts pre/post-fix, env census ×3, child leak probe, five-fixture `--check-only` out/err pairs);
`corpus/fixtures/run_battery.py` was never executed (read-only `grep`/`sed -n` only). No shared file edited,
no commit.

---

## §1 Host-version + template-path receipts

| receipt | measured value | command |
|---|---|---|
| engine | `4.7.2.stable.arch_linux.ed1daf0bf` | `godot --version` |
| editor path | `/usr/bin/godot` (single hit) | `which -a godot` |
| templates dir | `~/.local/share/godot/export_templates/4.7.2.stable/` (only 4.7.x dir) | `ls` |
| version.txt | 13 B `4.7.2.stable` | `ls -la` |
| `linux_release.x86_64` | 73,519,416 B sha256 `d9f79ab89b5ae369aeed11c6052d402e8218cd503bf85b4a235f9c30c46a7c63` | `stat`, `sha256sum` |

The r102-crit5 §0 template sha claim is **re-verified byte-identical** this round [obs].

**F4 (template-path branches; wording precision).** `_template_exists()` probes, in order:
`$XDG_DATA_HOME/godot/export_templates/<ver>`, `$HOME/.local/share/godot/export_templates/<ver>`,
`/usr/local/share/godot/export_templates/<ver>`, `/usr/share/godot/export_templates/<ver>`.
Reality on this host: `/usr/local/share/godot/export_templates` and `/usr/share/godot/export_templates`
→ `No such file or directory` (both). And the inherited env carries `XDG_DATA_HOME=/home/vgpnk/.local/share`
(§2), so the **XDG branch is the live branch**, not the HOME branch — the two happen to name the same
directory here [obs]. The last two branches are dead code on this host [obs]; if `HOME` and
`XDG_DATA_HOME` were both unset, the fixture would correctly refuse via
`FAIL export_div s02 arm=… reason=template_binary_not_found` (fail-closed, not a false PASS) [inf].

**Version-token split (r102-crit5 §2 restated, re-measured).** Exported template binary banner
`Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org` vs editor banner
`Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org`
[obs]. Any wording that names "the engine version" without saying **which binary printed it** is
ambiguous; the divergence is `.official` vs `.arch_linux` plus the timestamp.

## §2 Environment dependence of E2 — measured, not assumed

Probe `env_census.gd` (scratch, printed `OS.get_user_data_dir()`, `OS.get_config_dir()`,
`OS.get_cache_dir()`, and the five env vars), 3 variants, one `godot --headless --path` each:

| variant | `XDG_DATA_HOME` | `HOME` | `USERDIR` printed | `CONFIGDIR` / `CACHEDIR` |
|---|---|---|---|---|
| inherited host env | `/home/vgpnk/.local/share` | `/home/vgpnk` | `/home/vgpnk/.local/share/godot/app_userdata/C5Probe` | `/home/vgpnk/.config` / `/home/vgpnk/.cache` |
| `XDG_DATA_HOME=xdgprobe HOME=homeprobe` | `…/r103c-C5/xdgprobe` | `…/homeprobe` | `/var/tmp/r103c-C5/xdgprobe/godot/app_userdata/C5Probe` | `/home/vgpnk/.config` / `/home/vgpnk/.cache` |
| `env -u XDG_DATA_HOME HOME=homeprobe` | *(empty)* | `…/homeprobe` | `/var/tmp/r103c-C5/homeprobe/.local/share/godot/app_userdata/C5Probe` | `/home/vgpnk/.config` / `/home/vgpnk/.cache` |

Observations: (a) this host **already exports `XDG_DATA_HOME`**; (b) `user://` follows `XDG_DATA_HOME`
when set and `$HOME/.local/share` otherwise — the law the fixture header asserts, reproduced
engine-side; (c) **`XDG_CONFIG_HOME` / `XDG_CACHE_HOME` are NOT overridden** by the fixture's child
`env` prefixes, so a child still resolves config/cache into the real user home.

**Leak test (does that un-overridden pair actually leak writes?).** Ran the *exported* child with all
four roots redirected at once:
`env XDG_DATA_HOME=$R/xdgd XDG_CONFIG_HOME=$R/xdgcfg XDG_CACHE_HOME=$R/xdgcache HOME=$R/homeE <bin> --headless --quit-after 3 -- --tag=xdgleak`
→ rc=0; `find` under each root:
- `xdgd/`: `godot/app_userdata/ExportDivS02/{logs/godot.log, div_s02_state.txt}`
- `xdgcfg/`: **empty** · `xdgcache/`: **empty** · `homeE/`: **empty**
- child receipt: `DIV_S02_USERDIR /var/tmp/r103c-C5/xdgd/godot/app_userdata/ExportDivS02/`, `DIV_S02_READ prior=<none>`, `DIV_S02_WRITE ok=true`

⇒ The un-overridden `XDG_CONFIG_HOME`/`XDG_CACHE_HOME` are a **bounded, measured non-issue** for this
fixture on this version: the exported game process writes nothing outside `XDG_DATA_HOME`. Scope of the
isolation claim is therefore exact [obs]; whether a *different* game binary or the editor would write
there is not measured [unknown].

## §3 s02 fixture validation — hash-attributed (the fixture changed mid-audit)

The landed file was **edited by its owning E-seat while this audit ran** [obs]:

| snapshot | sha256 | mtime |
|---|---|---|
| pre-fix (my 20:56 copy) | `50b564383638733ca7ff362f44d8cd9a9d3673d6eca34e72c7d595c15ed4392c` | 20:56:33 |
| post-fix (current HEAD-attached file) | `c08792c1c208d47a8af66c669e7296eb6a1d94fe3d20872aeb73d4d6620a4898` | 20:57:06 |

Diff of the two copies is exactly the `_wipe_dir` hunks documented in `r103-E2.md` §4
(static `get_directories_at`/`get_files_at` → instance listing with `include_hidden = true`), plus its
comment block. Same target hash named in `r103-E2.md` §4 ⇒ no unreported drift [obs]. Consequence for
this seat: all evidence below names its hash; the fixture is a **moving target within the round**.

**Pre-fix validation (hash `50b56438…`).** `env EXPORT_DIV_ROOT=/var/tmp/r103c-C5/root TMPDIR=…/tmp godot --headless --path $R/proj --script res://export_div_s02.gd -- --arm=<iso|xdg>`
- arm=iso ×2 → rc=0 both; stdout 1101 B, sha256 `95f72fc1d098b81b8890322815a30b48c345af5e484e01d2bedfdacdf3e8b883` **identical across both runs** (byte-identical receipts).
- arm=xdg (fresh root, first invocation) → rc=0; stdout 929 B sha256 `7fe32a6fea1c4cc874ae9e9f95534e5fa101a54f49f66f614a3661ceab1bff81`.
- Verbatim iso PASS line (one of them):
  `PASS export_div s02 arm=iso r1_read=none r1_exit=0 r2_read=run1 r2_exit=0 store=[run1,run2] store_under_xdg=true userdir_under_xdg=true home_store_absent=true proj=/var/tmp/r103c-C5/root/div_s02/proj`

**Pre-fix repeatability defect — independently reproduced on a different root.** Second/third `arm=xdg`
invocations against the same warm root → **rc=1 both**:
- rep1: `FAIL export_div s02 arm=xdg reason=run4_read_not_none:[run4] … store_c=[run4,run4] …` (sha256 `59a38b29…`)
- rep2: `FAIL export_div s02 arm=xdg reason=run4_read_not_none:[run4,run4] … store_c=[run4,run4,run4] …` (sha256 `14f72d3c…`)

This reproduces the `run4_read_not_none` class E2 reported (their receipt: `…:[run4]`, sha256 `73fefdc4…15b`) on the *same pre-fix hash* but a **different root** (`r103c-C5/root` vs `r103c-E2v/root`) ⇒ independent replication, not a rerun of their bytes [obs].

**Independent replication of the API claim that justifies the fix.** My own probe dir (`.hid/inner/f.txt`, `.hf`, `vis/v.txt`) printed, verbatim:
`A_dirs_at_default=["vis"]` · `A_files_at_default=[]` · `B_dirs_instance_default=["vis"]` · `B_files_instance_default=[]` · `C_dirs_include_hidden=[".hid", "vis"]` · `C_files_include_hidden=[".hf"]`
— byte-identical to the string `r103-E2.md` §4 quotes as Observation A [obs]. Static `*_at` helpers and the default instance listing both skip dot-entries; `include_hidden = true` restores them. `.local` is a directory, so the directory half is the load-bearing half.

**Post-fix validation (hash `c08792c1…`).** Deliberately **poisoned warm root** first: pre-state
`cat root/div_s02/homeC/.local/share/godot/app_userdata/ExportDivS02/div_s02_state.txt` → `run4,run4,run4`.
- arm=xdg ×2 → rc=0 both, stdout sha256 `7fe32a6fea1c4cc8` **identical across both**, `r4_read=none`, `store_c=[run4]`. `diff` → `POSTFIX_XDG_REPEAT=BYTE-IDENTICAL`.
- arm=iso ×2 → rc=0 both, stdout sha256 `95f72fc1d098b81b` identical, and the iso PASS prefix is **byte-identical to the pre-fix iso prefix** ⇒ the fix is receipt-neutral for passing runs and does not regress the iso arm.
⇒ Fix **confirmed effective** on a state that previously failed; `r103-E2.md` §2's "restores repeatability only" claim holds [obs].

**F2 (exposure: pinned-prefix safety — proven).** Same-arm runs at **different** scratch roots
(`root`, `root2`) differ on the PASS line in exactly one token: the trailing `proj=` field. `diff` of the
two receipts shows only `proj=/var/tmp/r103c-C5/root/…` vs `…/root2/…` on the PASS line (all other
differing lines are `EXPORT_DIV_DIAG`, which is unpinned by design). Measured pinned prefixes:

| arm | prefix bytes | sha256(prefix) |
|---|---|---|
| iso | 158 | `50ff6050927090842beeb5554455bf96a941f2176d3189f0cbf70ea77f9e8de3` |
| xdg | 203 | `765d0525e9c1ec72ae3c7017e0eeb0ed17655a6aac4c6b9fc7a68856930a7e67` |

Cross-seat: `r103-E2.md` (root `/var/tmp/r103c-E2v`) and `r103-sent2.md` (root `/var/tmp/r103c-x2`) quote
PASS lines whose prefixes hash **identically** to mine for both arms (content-anchored match, not
line-number — see F6). Three independent roots, one pinned prefix ⇒ the row signatures for s02 should pin
the prefix and treat ` proj=<path>` as the trailing unpinned field. A whole-line pin would embed a host
path and rot on any root change.

## §4 Exposure findings with exact evidence

**F1 (highest impact — the harness gives registered rows NO scratch root).**
`grep -n "EXPORT_LAUNCH_ROOT\|EXPORT_DIV_ROOT\|TMPDIR" corpus/fixtures/run_battery.py` → **zero hits**;
`run_battery.py:1931` sets `env = None` for every row except the `save_roundtrip`/`__save_process_`
family (`:1932-1936` is the only env injection in the harness). So under the battery the fixture's
`_pick_root()` sees no `EXPORT_DIV_ROOT`/`EXPORT_LAUNCH_ROOT` and selects its third candidate,
`OS.get_user_data_dir()/export_div_s02` = `$XDG_DATA_HOME/godot/app_userdata/MechanicOneShotTest-<stamp>/export_div_s02`
— i.e. the **real user home**, not the run dir. Measured consequence class, already on disk:
`du -sh ~/.local/share/godot/app_userdata` → **982 MB**; per-dir top: `MechanicOneShotTest` 352 MB,
`MechanicOneShotTest-20261018T212500022987Z` **281 MB**, `MechanicOneShotTest-20261018T213443471189Z` **281 MB**
— the last two are *exactly* the census `run1`/`run2` stamps recorded in
`reports/round-103/mutations/r103-w4-census.json.file`. Registering `export_div_s02` as-is adds another
~73.5 MB per battery run (§5) to that uncollected residue, and the fixture has no teardown by design.
Recommended line-pair (shard content only — orchestrator applies), following the existing precedent:

```
         env = None
-        if script == "save_roundtrip.gd" or script.startswith("__save_process_"):
+        if script.startswith("export_div_"):
+            # r103 C5: give the export_div_ family the scratch root the fixture
+            # documents as its first candidate; without this their 73.5 MB
+            # exports land under the real user-data dir (uncollected residue).
+            env = os.environ.copy()
+            env["EXPORT_DIV_ROOT"] = str((run_dir / "export-div-scratch").resolve())
+            (run_dir / "export-div-scratch").mkdir(exist_ok=True)
+        elif script == "save_roundtrip.gd" or script.startswith("__save_process_"):
             user_data = (run_dir / "xdg-data").resolve()
```
This is *registration-side*, so it does not touch the fixture; the two `export_div_` rows in
`w5_export_div.patch` stay as they are. Without it the rows still PASS (the home dir is writable, and
arm=iso wipes its own `<root>/div_s02` at start) — the defect is resource exposure, not verdicts.

**F3 (bound claim verified, with measured headroom).** The fixture header claims an "8 s fixture bound".
`run_battery.py:1930`: `timeout_seconds = 60 if script.startswith("__godot_export") else 8` ⇒ a
`.gd`-script row gets **8 s**; the 60 s class is only the legacy `__godot_export__` pseudo-script [obs].
Measured whole-arm walls: iso 5.0 s (first, cold — load 1.94), 4.667 s (load 12.33), 4.786 s (load 12.97),
~4.5 s (post-fix pair); xdg ~2.0–2.4 s (binary reused). Tightest observed margin ≈ **3.2 s (1.67×)**,
and the cold-cache read of the 73 MB template cost more than a 6.5× load increase did [inf, n=4].
Internal child bound `RUN_BOUND = 5` s per `timeout -k 1 5`; measured child boot 798 ms (load 11.66)
⇒ ~6× headroom. No tps token appears in any s02 PASS line [obs]; consistent with r102-crit5 §1 L1
(`--quit-after N` = N main-loop frames, load-invariant).

**F5 (header numeric claims vs bytes).** `~73 MB artifact could exceed the 64 MB mount`: template
73,519,416 B; embedded export artifact measured **73,522,200 B** sha256
`b55db3d04b640988ab3dd07256d22d7cd366f919bf888b802d0cc7eda69ada2e` (delta 2,784 B = the embedded PCK).
70.1 MiB > 64 MiB mount ⇒ claim TRUE in the safe direction [obs]. `Export ~1.9 s, child boot ~0.9 s`
(claimed at load 3.3): re-measured 2,105 ms / 798 ms at load 11.66 ⇒ within ~10% under 3.5× the load
[obs] — these are the only timing numbers in the round and they are not knife-edge.
**Probe-granularity caveat [inf]**: `_probe_writable` writes 4,096 B, but the export needs 73.5 MB; a
scratch root with <73.5 MB free passes the probe and then fails as `export_failed:<code>`. Fail-closed,
but the failure class is misleading (root-selection vs export). Not triggered this seat.

**F6 (citation hygiene, live).** While this audit ran, `reports/round-103/r103-sent2.md` and `r103-E2.md`
were being written by their seats; a line-number-anchored extraction of `r103-sent2.md:194` produced a
different line on a re-read 30 s later (content-anchored re-extraction then matched). Shard hashes at
close: `r103-sent2.md` md5 `422fa469ae1d450dcfda20e5819606a4` (15,860 B), `r103-E2.md` md5
`d55eb7a14a14fa90a5eabf669675a3f7` (11,392 B) — both still moving targets. Every cross-shard citation
in §3 is therefore content-anchored (hash of the pinned prefix), per the r102-connector RI-7/Ri-8 laws.

**F7 (claim-vs-reality sweep — moved twice inside this audit; two snapshots recorded).** Mechanical sweep
of every r103 shard's cited repo paths (`python3` regex over `reports/round-103/r103-*.md`,
`os.path.exists`), **snapshot A** 20:59 and **snapshot B** 21:02:40–21:03:09:

| artifact | snapshot A (20:59) | snapshot B (21:03) | sha256 (B, first 16) |
|---|---|---|---|
| `export_div_s01.gd` | absent (E1 cites it) | present, 23,967 B, 678 lines | `ae2f8af5e1a90fe4` |
| `export_div_s02.gd` | present | present, 17,975 B, 468 lines | `c08792c1c208d47a` |
| `export_div_s03.gd` | absent (E3 cites it) | present, 18,658 B, 517 lines | `8c32602faf454af5` |
| `export_div_s04.gd` | absent (E4 cites it) | present, 25,637 B, 642 lines | `37ca8eddb8a427c3` |
| `export_div_s05.gd` | absent (E5 cites it) | present, 23,455 B, 604 lines | `746c6b1a503eb374` |
| `export_div.gd` | absent (E0 cites it as its own) | **still absent** | — |
| mutations | — | `mut01…mut09_replay.py`, `mut05_gate.py` (186 KB), `mut05_gate_proto.py` present | — |

So the C1 fixture set went **1/5 → 5/5 within ~4 minutes**, all with mtimes 20:57–21:02 [obs]; my own
shard written at 21:00 therefore carried a claim that was true at write time and stale by 21:03 — an
exposure lesson, not a defect in the fixtures (the authors landed them as designed). Still absent and cited
at snapshot B: `corpus/fixtures/export_div.gd` (E0's stated ownership), `corpus/fixtures/README.md`,
`corpus/fixtures/three/README.md`, `reports/round-101/mutations/gen.py`,
`reports/round-103/game-dev-2d.md`, `reports/round-103/mutations/{mut06_foldreg.py, mut08.gd,
r103-crit2_meta_gate.py, r103-ver7-reject-arm-prints.patch}` — note `mut08.py` exists while `mut08.gd`
does not, and `r103-ver7-reject-arm-prints.patch` is the C3/S4 fix, so that claim is currently unfunded.
Sweep caveats: prose citations produced false-positive "missing" entries (`corpus/fixtures/export_div_s0`,
`run_battery.py...`, `r103-w4-census.json.file`), so this table is media-anchored, not a verdict on any seat.
E0/E1/E3/E4/E5 shards self-label "in progress"/"PENDING" ⇒ **stale skeletons at snapshot A, funded at
snapshot B** [inf].

**F8 (census label ambiguity, verified consistent).** `r103-w4-census.json` reports `rows=554`,
`rows_with_output=538`, `rows_zero_pass=48`, `multi_count=19`, `shape_first_tokens={"PASS":566}` against
`corpus/live/runs/20261018T212500022987Z/verdicts.json` / `…T213443471189Z/` (both 1,407,9xx B, present).
Independent recompute reproduces **554 / 538 / 19 / 566** exactly, and resolves the zero-PASS label:
64 rows have no PASS line under the strict reading, of which 16 have no output record at all
(`probe_unrelated_error_export_readiness`, `probe_save_independent_process`, …) ⇒ 64 − 16 = **48** =
the census's reading ("zero PASS among rows that have output"). The number is **correct for that
definition**, but the field name reads as "48 rows produced no PASS anywhere". Suggest renaming to
`rows_with_output_zero_pass` (or adding the 16-16 split as a field) when the census is regenerated [inf].
Also `python3` confirms **zero `export_div_` rows** in the live verdict files ⇒ registration not landed at
these stamps, consistent with F7 and with `w5_export_div.patch` being unapplied.

**F9 (a landed fixture emits a Unicode NUL notice — measured benign, with one residual).**
`godot --headless --path $R/proj --script res://export_div_sNN.gd --check-only` over all five landed
fixtures (rc=0 each, stdout 101 B = banner only):

| fixture | stderr | `Unicode parsing error … Unexpected NUL character` lines | literal `\u0000` escapes in source | on-disk NUL bytes / invalid UTF-8 |
|---|---|---|---|---|
| s01 | 291 B | 3 | 1 (`export_div_s01.gd:364`) | 0 / 0 |
| s02 | 0 B | 0 | 0 | 0 / 0 |
| s03 | 0 B | 0 | 0 | 0 / 0 |
| s04 | 291 B | 3 | 1 | 0 / 0 |
| s05 | 0 B | 0 | 0 | 0 / 0 |

Root cause: the source literal `raw.get_string_from_utf8().split("\u0000")[0]` (used to strip NUL-padded
PCK path entries) makes the lexer emit the notice 3× per occurrence. It is **not** file corruption — the
byte scans above show zero NUL bytes and zero invalid UTF-8 in all five files [obs]; the counts correlate
exactly with the escape's presence (1 escape ⇔ 291 B stderr ⇔ 3 warnings). Classification impact: none —
`run_battery.py:1806-1809` flags `unrelated_errors` by the literal `"ERROR:"` token and `"Parse Error:"`;
the warning text carries neither (`grep -c "ERROR:" ck_01.err → 0`) [obs]. Residual risk [inf]: the notice
goes to **stderr**, and the harness concatenates streams (`run_battery.py:1938`), so any future gate that
asserts *empty stderr* or counts lowercase "error" substrings would fire on s01 and s04 specifically.

**F10 (F1's blast radius = all five fixtures, so one env line fixes the whole family).** All five share the
same `_pick_root()` candidate order — `$EXPORT_DIV_ROOT` (3 refs each), `$EXPORT_LAUNCH_ROOT` (3 refs),
`<engine user-data dir>` (1 ref), `$TMPDIR`, `/tmp` (probe = 4096 B write+readback) — so F1's missing
harness-side scratch root applies to the entire C1 set, not just s02, and the single `env` line proposed
in F1 covers all five at registration time. Header claims audited against `run_battery.py:1930`: s01
("every arm stays under the 8 s battery bound"), s02, s03 ("pack-only export ~1.5-2 s"), s05 all claim the
**8 s** bound ⇒ **consistent** with the measured `else 8` branch [obs]; s04's header makes no bound claim
[obs]. All five prefer user-data over `/tmp` and all five keep nested engine output in
`<root>/div_sNN/logs/*.log` [obs] — i.e. the same evidence rule and the same F1 exposure class.

## §5 w5 gate semantics — the patch's own claims, proven

`reports/round-103/mutations/r103-crit5_gate_probe.py` (new, this seat) evaluates the two expressions the
w5 patch adds, **verbatim**, over synthetic row sets — no harness import/execution. Result: **7/7
scenarios behave as the patch comment claims**:
- A registered(2)==ran(2) → `count_floor=True`; B full-family drop (0 both sides) → **False (fires)**;
  C partial drop with CASES and results shrunk together → **True (the hole the comment declares)**;
  D registered(2) but the execution loop produced 1 result → **False (fires)**;
  E an `export_div_` allowlist entry with `dead_in_run=True` → `expected_errors_all_matched=False (fires)`;
  F zero census rows for the prefix → **True (the "vacuous-but-honest" empty-generator property, same
  shape as r100-critic GD-1)**; G a dropped *sibling-family* row does not move the family floor.
⇒ Both w5 comments are accurate as written; the declared ceiling (C) is a real ceiling and is disclosed.
The `export_div_` prefix also remains absent from the family-coverage tuple's list until the patch is
applied (`git apply --check` on all four landed patches → `APPLY-CHECK=PASS` for each, including
`r103-S0-E1/E2/E3` and `w5_export_div.patch`) [obs].

## §6 Boundaries and non-actions (C5 seat)

- `corpus/fixtures/run_battery.py` never executed (only `grep`/`sed -n` reads); no shared file edited
  (`SCORECARD.md`, `LOG.md`, `SHONEN.md`, `PROVINCE.md`, `corpus/lessons/*`, `reports/round-10{1,2}/`
  untouched); no `git` mutation. New files: this shard + `mutations/r103-crit5_gate_probe.py`.
- Device-census tokens: no r103 shard pins `js0`/`js1` state (grep hits are the r103-connector hazard
  disclosure and this shard's own axis text); no device state is asserted anywhere in this audit [obs].
- Stray worktrees listed only, per instruction, not removed: `/var/tmp/r103-S2/wt` (r103-S2),
  `/var/tmp/r103-S3` (r103-S3), `/var/tmp/r103-ver4/wt` (r103-ver4), plus `/var/tmp/r103-S1/repo`,
  `/var/tmp/r102-S1`, and the three locked lane worktrees.
- Scratch `/var/tmp/r103c-C5/` (plain dir, **not** a git worktree ⇒ nothing to `git worktree remove`)
  is retained as the evidence store: `logs/` (36 files — s02 receipts pre/post-fix, env census ×3, child
  leak probe, five-fixture `--check-only` out/err pairs), `root/`, `root2/`, `proj/`, `hid{,2}/` (141 MB).
- Tooling exposure noted for future timing claims: `/usr/bin/time` and `bc` **do not exist** on this
  host (`No such file or directory` / `command not found`); timing must use shell `date +%s%N`
  integer arithmetic. `/usr/bin/timeout` exists and is used by the fixture.
- `/tmp` class corroborated: `mount` → `tmpfs on /tmp type tmpfs (…,usrquota)`; `df -h /tmp` → 16 G
  size, 13 G used, 3.1 G avail (80%). `usrquota` ⇒ EDQUOT is a per-user quota, not exhaustion of the
  mount. `/var/tmp` is on `/dev/mapper/root` (930 G, 19% used) ⇒ correct scratch choice [obs].
- One slip, disclosed: an early command's fallback branch wrote a ~1.1 KB `/tmp/.c5a` scratch file
  before I switched to `/var/tmp`; removed (`rm -f /tmp/.c5a`) in the same session [obs].

## §7 Labels

**Observation:** every command output quoted above (version strings, sha256s, byte counts, load series,
mount flags, template sizes, receipts, probe prints, residue sizes, census recompute, claim-vs-reality
snapshot tables, `--check-only` stderr byte counts and NUL/UTF-8 byte scans, gate-probe results).
**Inference (labeled):** F1's residue mechanism (env is `None` + `_pick_root` ordering ⇒ home root);
F3's cold-cache-dominates-load reading (n=4); F5's probe-granularity caveat; F7's "stale skeleton, not
fabrication" reading; F8's field-rename suggestion; F9's residual empty-stderr-gate risk; F10's
"one env line covers the family" generalization; §1's fail-closed branch if HOME/XDG were unset.
**Unknown:** whether other fixtures (`export_launch*.gd`, `r96b_*`) also depend on wiping dot-entries
(E2 §6 flags this; not measured here); battery-level idempotence (rows unregistered, and
`run_battery.py` is out of bounds for this seat); whether a non-game Godot binary writes to
`XDG_CONFIG_HOME` (the exported child provably does not); the editor's own config/cache write pattern
under redirected roots; the runtime cost of the newly landed s01/s03/s04/s05 arms (headers claim 8 s and
~1.5–2 s pack exports; only s02's arms were timed by this seat).

## §8 Files touched

- `reports/round-103/r103-crit5.md` (this shard) — extended in place; original plan retained.
- `reports/round-103/mutations/r103-crit5_gate_probe.py` (new, 7/7 synthetic gate scenarios).
- Scratch only: `/var/tmp/r103c-C5/**` (evidence store), `/tmp/.c5a` created and removed.
- No other repo path created or modified; no commits.
