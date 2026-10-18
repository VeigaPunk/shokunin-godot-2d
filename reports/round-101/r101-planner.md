# r101 PLANNER shard — lattice map, saturation draft, integration-order spec

KEY=PLANNER | host `vgpnk` — Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`,
`--headless`), Python 3.14.7, 32 cores.
Load context (`uptime`, seat start 16:21:07): `load average: 33.42, 19.05, 12.84`;
at last probe (16:25:45): `load average: 57.01, 42.80, 24.56` (sibling 3D lane r104 live).

Plan (5 lines, as written before execution):
1. Gather: SCORECARD tail, LOG tail, reports/round-98..100, run_battery.py conventions.
2. Map C1/C2/C3 into a lattice: nodes, edges, ownership, integration risks.
3. Draft saturation line + stagnation window N from the r88–r100 axis history.
4. Write the integration-order spec: exact CASES row names + order + harness edits.
5. Keep <400 lines; cite exact command + observed bytes; label observation/inference/unknown.

Ownership: this seat wrote **only this shard**. All probes ran on scratch copies under
`/var/tmp/r101-PLANNER/` (see §2.0 for the `/tmp` deviation). No shared file touched, no commit,
`run_battery.py` never executed (rule 1).

---

## 1. Lattice map

Round 101 has three claims landing on three *disjoint* fixture sets. C1 is a **capability**
acquisition (new build-product surface), C2 is a **discrimination-breadth repair** (r100 critic
F2), C3 is a **retirement + replacement measurement** (r95 dead flag).

| node | claim | fixture(s) | row family | owner seat | verdict shape |
|---|---|---|---|---|---|
| C1 | `export_prod` lattice | `corpus/fixtures/export_prod_s01..s11.gd` (1 landed at 16:25: `export_prod_s10.gd`) | `export_prod_sNN` | E0 lead + E1..E11 | coverage: +11 rows, export/build-product surface; depth: cold/warm build-product semantics; calibration: legacy export predicate shown blind (mut5 F3) |
| C2 | full-replay pins for the 14-cell replay | `corpus/fixtures/r101_seqfull.gd` (37677 B, landed 16:24; sha `426075c8…` per ver6) | `r101_seqfull_clean` / `r101_seqfull_noclean` | E12 lead + D1/D2/D3 (non-author derivation) | depth: closes r100-critic F2 (1-line → full-transcript pin); calibration: forged-extra-line mutant must reject |
| C3 | `--offy` dead flag → live Y-translation measurement | `corpus/fixtures/r101_ytrans.gd` (11464 B, sha `0d5093d6…`, landed 16:22) | `r101_ytrans_{y0,y1000,ym1000,ysep,ycop,census}` | E17 | coverage: 6 rows; depth: Y-translation order-invariance law (was claimed-but-void in r95); calibration: 0-reachable-reads census + sha tripwire |

Edges (dependencies an integrator must respect):

* C1 rows depend on nothing in C2/C3, but C1's *run-receipt* rows depend on the engine behaviour
  in §2.3–§2.5 — a naive "export then `--main-pack`" row **fails** without the warm-up recipe.
* C2 rows depend on the r100 `r100b_seq_*` rows staying registered (the new rows extend, not
  replace, the 1-line pins; retiring them would lose the fresh-process contrast).
* C3's `census` arm reads `res://r95b_order.gd` from the scratch project — the harness copies it
  (`run_battery.py:1675-1681`), so the row is coupled to that file's bytes (E17 intends this: a
  deliberate sha256 tripwire).
* All three families share the tail-adjacency constraint (§5.1) and the `cases_integrity` prefix
  tuple (§5.3) — the only cross-family integration coupling.

## 2. Measurements made by this seat (all on scratch copies, observation unless labelled)

### 2.0 Scratch-path deviation (disclosure)
Rule 1 designates `/tmp/r101-<key>/`. `/tmp` is a 16 GB tmpfs at **80 %** with a live per-user
quota: `printf … > /tmp/r101-PLANNER/exp2/project.godot` →
`/bin/bash: line 1: printf: write error: Disk quota exceeded` (observed 16:24). Scratch moved to
`/var/tmp/r101-PLANNER/` (same root fs as `/home`, 772 G free) — the same deviation r100-critic
and E17 recorded independently. `run_battery.py`'s own run dirs live in-repo, so this affects
fixtures that hardcode `/tmp` (**risk R2**).

### 2.1 C1 — the `--main-pack` launch is **not** one command away
Probe project `/var/tmp/r101-PLANNER/exp2` (production-shaped: `run/main_scene`, icon, `sub/`
subdirectory, `export_presets.cfg` preset `Linux/X11`, `binary_format/architecture="x86_64"`).

| probe | command (shape) | observed |
|---|---|---|
| PCK export | `godot --headless --path P --export-pack "Linux/X11" out/pack.pck` | rc=0, 3672 B, head `47 44 50 43` = `GDPC` |
| ZIP export | `… --export-pack "Linux/X11" out/pack.zip` | rc=0, 3708 B, head `50 4B 03 04`; `unzip -l` = **14 files** (`main.gdc` 216, `main.gd.remap` 31, `main.tscn.remap` 97, `sub/prop.gdc` 185, `sub/prop.gd.remap` 35, `sub/prop.tscn.remap` 97, `.godot/exported/133200997/export-<hash>-{main,prop}.scn` 669/673, `.godot/imported/icon.svg-<hash>.ctex` 94, `icon.svg` 112, `icon.svg.import` 192, `.godot/uid_cache.bin` 84, `.godot/global_script_class_cache.cfg` 8, `project.binary` 324), all `1980-00-00` mtimes |
| cold `--main-pack` | `godot --headless --main-pack out/pack.pck --quit-after 5` | rc=0 but **no run marker**; stderr `ERROR: Corrupted header in binary project.binary (not ECFG).` + `ERROR: Couldn't load file 'res://project.binary', error code 16.` |
| release binary, non-embedded | `./fixture.x86_64 --headless --quit-after 5` | rc=1: `ERROR: Error: Couldn't load project data at path … Is the .pck file missing?` + `"fixture.pck" was found in the current working directory. To be able to load a project from the CWD, use the disable_path_overrides=no SCons option` |
| release binary + `--main-pack` | `./fixture.x86_64 --headless --main-pack fixture.pck` | rc=1: ``--main-pack` was specified … but this Godot binary was compiled without support for path overrides` |

### 2.2 C1 — the working run receipt (two independent shapes)
1. **Embedded pack**: preset option `binary_format/embed_pck=true` + `--export-release` →
   `./embedded.x86_64 --headless --quit-after 5` → **rc=0**, stdout
   `EXPORT_PROD: main ready name=Main` (binary 73 523 432 B).
2. **Warm `--main-pack`**: after the project has been imported, `godot --headless --main-pack
   out/pack.pck --quit-after 5` → **rc=0**, same marker. (= also works on a warm `.zip`.)

### 2.3 C1 — determinism is **conditional on the import cache** (this is the headline C1 finding)
Same project, no `--import` pre-pass, three consecutive `--export-pack` runs:

* run 1 (cold, project has no `.godot`): **3672 B**, sha `1519ddd2…`
* run 2: **4008 B**, sha `6001d1c8…`
* run 3: **4008 B**, sha `6001d1c8…` → `cmp` → **`WARM_PAIR_IDENTICAL`**
* zip pair (both warm): sha `13cee300…` twice → identical.
* the cold artifact is exactly the one that fails to load (§2.1); the warm ones load.

With a pre-pass (`godot --headless --path P --import`, rc=0, creates `.godot/`) then two exports:
both **4008 B**, identical sha `0384f0a8…`, and `--main-pack` on the first one → rc=0 + marker.
Header bytes: `GDPC`, then format 4 / 4.7.2, `flags=2`, `file_base=112`; the differing field sits
at offset `0x20` (u64 `0x0A90`=2704 cold vs `0x0BE0`=3040 warm) and the data section grows 336 B.
**Inference (not proven):** the cold export writes its pack before the import/uid-cache state is
settled. **Unknown:** whether `--export-release` (as opposed to `--export-pack`) shows the same
cold/warm split — the cold release export produced the same class of failure (§2.1 row 3), so the
split is at least not pack-format-specific.

### 2.4 C1 — filters and main-scene swap are cheap to pin, with exact censuses
* `exclude_filter="sub/*"` (on a warm project) → zip census drops from **14 to 10** files:
  `sub/prop.gdc`, both `sub/prop.*.remap`, and the `prop*.scn` entry disappear; remaining
  `main.gdc` 216, `main.gd.remap` 31, `main.tscn.remap` 97, `export-3070c538…-main.scn` 669,
  `uid_cache.bin` **55** (was 84), `ctex` 94, `icon.svg` 112, `icon.svg.import` 192,
  `global_script_class_cache.cfg` 8, `project.binary` 324; zip 2518 B.
* main-scene swap: `run/main_scene="res://main2.tscn"` + warm export + `--main-pack` →
  rc=0, stdout `EXPORT_PROD: SWAPPED main ready` (the receipt follows the swap).

### 2.5 C1 — the two error classes, verbatim
* unknown preset, `--export-pack "Nope" …`: **rc=1**, stderr tail
  `ERROR: Invalid export preset name: Nope.` / `The following presets were detected in this
  project's \`export_presets.cfg\`:` / `        "Linux/X11"` / `   at: _fs_changed (editor/editor_node.cpp:1417)`.
  Note the *legacy* CASES row (`run_battery.py:59`) pins `No export preset 'Missing preset' found`
  while `execute()`'s in-line evidence (`:1909`) pins `ERROR: Invalid export preset name: Missing preset.`
  — **only the latter is the string this engine emits** (observed). Integration risk R6.
* missing templates, `XDG_DATA_HOME=<empty> godot --headless --path P --export-release "Linux/X11" out/z.x86_64`:
  **rc=1**, `ERROR: Cannot export project with preset "Linux/X11" due to configuration errors:` /
  `No export template found at the expected path:` /
  `<xdg>/godot/export_templates/4.7.2.stable/linux_debug.x86_64` (and `linux_release.x86_64`) /
  `   at: _fs_changed (editor/editor_node.cpp:1401)` + `ERROR: Project export for preset
  "Linux/X11" failed.` — `--export-pack` needs **no** template (it succeeded with the hidden data
  home), so this row must use `--export-release`/`--export-debug`. A `HOME=` override alone did
  **not** hide the templates (rc=0) — use `XDG_DATA_HOME`.
* Present templates (observation): `~/.local/share/godot/export_templates/4.7.2.stable/` —
  `linux_release.x86_64` 73 519 416 B, `linux_debug.x86_64` 73 703 800 B, `version.txt` 13 B.

### 2.6 C2 — the full-transcript pin is expressible, and the forgery must break it
`classify_process` = `… and signature in output` (`run_battery.py:1741`) over
`stdout + stderr` concatenation (`:1701`); `execute()` needs **no** change for a multi-line
signature. My capture of the replay, exactly the harness launch shape
(`godot --headless --path /tmp/r101-PLANNER/proj --script res://r100b_seq.gd -- --clean=1`):
stdout = **17 lines / 6804 B**, sha256 `2fc9a28f0dc2a44f4301d346ef46a81bfab87a6514bf21b070a9334412b0372a`
— line 1 banner, line 2 blank, **lines 3–16 = the 14 `PASS r100_gui <cell> …` lines in the
replay order `[census, routing, hover, motion, localpos, cursor, clip, drag, touch, subvp, warp,
focus, render, osmeta]`**, line 17 `SEQ_DONE clean=1`; stderr 6 lines / 293 B.
A `"\n".join` of lines 3–17 is therefore a contiguous substring of the merged output, and the
critic's `m_seq` forgery (an extra `print` inside the replay) breaks contiguity → rejects.
Divergences I reproduced in the `--clean=1` transcript against the fresh-process pins (partial —
my line dump was cut at 200 chars, E12 owns the full census): `cursor c0=(30.0, 14.0)` (fresh
`(0.0, 0.0)`), `subvp cursor_root=(20.0, 4.0)` (fresh `(0.0, 0.0)`), `warp w0 cursor=(20.0, 4.0)`
(fresh `(0.0, 0.0)`), and `touch t3_emul_touch` list order. These match r100-critic §F2's four
divergence cells (`cursor`, `touch`, `subvp`, `warp`).

### 2.7 C3 — the flag is dead, and the retirement census has a runtime leg
* Static: `grep -c 'offy' corpus/fixtures/r95b_order.gd` → **0**; `r95b_order.gd:566` reads only
  `_opt_float("off")` and `:567` calls `_pile(…, off, 0.0)`; `grep -rn 'offy' corpus/` finds the
  token only in `run_battery.py:1004` (the row's flag) and in r95 live evidence trees.
* Runtime: 5 runs of the committed fixture (`--arm=celloff --off=0` ×3, with `--offy=1000` ×2):
  the **PASS line sha256 is identical in all five** (`grep '^PASS' | sha256sum` →
  `4eb7afed20b2d44c…` prefix); the only differing line is the non-authorable diagnostic
  `R95B celloff env=… proc=N …`, whose `proc` field varies **between identical-flag repetitions**
  (156, 156, 154, 155, 156) — i.e. run-nondeterministic, not flag-caused. One repetition (r3)
  also lost its first 4 stdout lines to a truncated capture under load (an environment artifact,
  not a flag effect) — both observations argue the R95B diagnostics are not pinnable and the
  PASS line is.
* ⇒ E17's replacement (real Y-translation measurement + `r95b_offy_tokens=0` census with a sha
  tripwire) is the correct closure; nothing in the flag can be "fixed" — it was never read.

## 3. Integration risks (ranked; each with its evidence)

* **R1 — 8 s row timeout vs nested export boots.** `run_battery.py:1863` gives every non-`__`
  row **8 s**. C1's fixtures run *nested* Godot exports from inside a Godot process (observed
  wall time: one cold export ≈3–5 s; a 3-export + import sequence ≈9.0 s; under loadavg 57 the
  margin is gone). **Action:** extend the sentinel to
  `60 if script.startswith(("__godot_export", "export_prod_")) else 8` (or give the r101 export
  rows the 60 s class) — orchestrator-owned, one line.
* **R2 — `/tmp` quota (live in the landed fixtures, not hypothetical).** Measured `EDQUOT` on
  `/tmp` at 16:24 (§2.0). Cross-check of the fixtures landed at 16:26–16:27:
  `export_prod_s01.gd:22 DEFAULT_WORK := "/tmp/r101-E1/export_prod_s01_work"` and
  `export_prod_s10.gd:13 SCRATCH_ROOT := "/tmp/r101-E10"` — both default into the quota-blocked
  tmpfs; `export_prod_s02.gd:23` uses `/var/tmp` (its header cites the same EDQUOT reason),
  `export_prod_s04.gd:33` uses `user://`. **Action:** the orchestrator must either pass each
  fixture a `--root=` on a disk-backed path (s02 already parameterises it) or force the defaults
  off `/tmp` before the battery run; otherwise s01/s10 can fail for an environmental reason
  unrelated to their claims. (Checked: no landed fixture writes into the battery's `<scratch>/out`
  — s01's `out/export_prod_s01.pck` is relative to its own `--path` project under `DEFAULT_WORK`
  (`:282-283`), and s10's `PROJ + "/out/…"` likewise (`:14`, `:154`) — so R7's legacy-row trap is
  not triggered by them today.)
* **R3 — cold-export artifacts are non-loadable.** Any row that asserts a `--main-pack`/
  direct-launch receipt from the *first* export of a fresh project will fail (§2.1 vs §2.2).
  Warm first: `--import` pre-pass, or export twice and pin the second/third artifact.
* **R4 — determinism rows must be conditioned.** "sha256 ×2" is only true warm-warm (§2.3).
  A row that exports twice from a cold project gets 3672 B vs 4008 B and fails.
* **R5 — the non-embedded template binary cannot be launched at all** (§2.1 rows 4–5). Row s04/s09/s11
  must either use `embed_pck=true` for the binary-launch arm or use `--main-pack` on a warm pack.
* **R6 — two string truths for the unknown-preset class** (§2.5). New s07 rows must pin the
  observed `Invalid export preset name:`, not the stale tuple string at `:59`.
* **R7 — cross-row scratch interference (new, not on any shard yet).**
  `run_battery.py:1843-1852`: `__godot_export__` uses `export_project = scratch` and
  `out_dir = scratch/"out"`, then `assert not any(out_dir.iterdir())`. The scratch dir is shared by
  **all** rows in one run. If any r101 fixture writes into `<scratch>/out/`, the legacy
  `export_readiness` row aborts the battery. Equally, fixtures must not leave files that other
  rows' censuses (uid/icon/`res://` walk) can see. **Action:** r101 fixtures write only under
  their own temp root and delete it; never `<scratch>/out`.
* **R8 — allowlist obligations.** Scenario rows that deliberately provoke nested ERROR text
  (s07 unknown preset, s08 missing templates) must have the *nested* output suppressed or their
  exact ERROR lines registered in the `expected_errors` dict — `classify_process` fails a row on
  any unmatched `ERROR:` line (`:1739-1742`). Same for C2's replay rows (they already carry the
  `ERROR: Parameter "t" is null.` entry through the render cell).
* **R9 — `cases_integrity` prefix coverage.** The tuple at `:4026-4027` lists r98–r100 prefixes
  only; r101 prefixes must be added or the F1 repair does not see the new blocks (§5.3).
* **R10 — the existing export rows are blind to PCK content** (mut5 F3, independent): the legacy
  predicate accepts a 1 MB partial ELF and never reads the `.pck`. C1's s01 must therefore pin
  magic/size/sha of the pack itself, and the lane should say so rather than claim the legacy row
  already covered it.

## 4. Saturation line + stagnation window N (draft for SCORECARD.md §Saturation)

**Draft text (paste-ready, one paragraph + one table line):**

> **Saturation line.** An axis is *saturated at round R* when R's verdict for that axis is
> `unchanged` — the round lands no new mechanism class, no new pinned cell, and no corrected pin
> on that axis. **Stagnation window N = 5**: five consecutive rounds with no `improved` verdict on
> any axis trigger the stagnation nudge. **Rationale (r88–r100, 13 rounds):** every round in the
> window returned `improved` on all three axes — r88 207→215 rows (mp/light/occluder/vis),
> r89 →235 (geo2d), r90 →247 (RigidBody2D), r91 →258 (Navigation2D), r92 →272 (TileMapLayer),
> r93 →295 (anim/tween), r94 →314 (particles), r95 →366 (dss/order), r96 →426 (scene_io),
> r97 CASES 419→431 (SceneTree), r98 →463 (canvas/draw-flush), r99 →485 (audio), r100 →509
> (GUI/Viewport capstone) — so the lane's stagnation count has been **0 across the whole window**
> and N is not calibrated from history; 5 is declared as a conservative fleet default, countable
> from the trailing run of SCORECARD verdict rows reading `unchanged`. The axis where saturation
> is *plausible* is coverage of the in-engine headless 2D API (recent rounds extend
> already-mapped surfaces); the export/build-product surface opened at r101 (C1) and the
> non-headless/platform surfaces remain open, which is why the lane is **not** saturated at r100.

**Capabilities table (draft row; per `SCORECARD.md:288-290` a capability enters only through a
round that demonstrates it running):**

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| headless production export | build a production-shaped Godot 4.7.2 project to PCK / ZIP / embedded release binary with the installed templates, census the pack, and run the product under `--main-pack` + `--quit-after`, with byte-stable warm builds | §2.1–§2.5 here + `reports/round-101/r101-E0-spec.md` (row receipts) | r101 (pending integration) |

## 5. Integration-order spec (what the orchestrator must register)

### 5.1 Insertion point (binding)
Insert all r101 rows **immediately before the current line 1644**
(`("crash_spontaneous_sigabrt", …)`, verified by `sed -n '1643,1646p'`), i.e. after the r100
block that ends at `:1643`. Reason: `descendant_pipe_detached_control` (`:1645`) sleeps 8 s and must
stay adjacent to the meta probes (r88 constraint; r79/r100 blocks were inserted exactly there).
E17's note "after the r95b block" is satisfied in *spirit* by this position (the r95b rows stay
where they are); appending mid-file is not required and would scatter the round's rows.

### 5.2 Row order (exact names, in order; groups sorted by fixture stem)
```
 1  r101_ytrans_y0        r101_ytrans.gd      ["--arm=ytrans","--offy=0"]
 2  r101_ytrans_y1000     r101_ytrans.gd      ["--arm=ytrans","--offy=1000"]
 3  r101_ytrans_ym1000    r101_ytrans.gd      ["--arm=ytrans","--offy=-1000"]
 4  r101_ytrans_ysep      r101_ytrans.gd      ["--arm=ysep","--offy=1000","--qoffy=0"]
 5  r101_ytrans_ycop      r101_ytrans.gd      ["--arm=ycop","--offy=1000"]
 6  r101_ytrans_census    r101_ytrans.gd      ["--arm=census"]
 7  r101_seqfull_clean    r101_seqfull.gd     ["--clean=1"]      # E12 owns final name/sig
 8  r101_seqfull_noclean  r101_seqfull.gd     ["--clean=0"]
 9  export_prod_s01       export_prod_s01.gd  (base PCK: magic/size/sha)
10  export_prod_s02       export_prod_s02.gd  (zip + central-directory census)
11  export_prod_s03       export_prod_s03.gd  (determinism: warm×2 + cold/warm envelope)
12  export_prod_s04       export_prod_s04.gd  (main-scene swap + run receipt)
13  export_prod_s05       export_prod_s05.gd  (remap/UID census)
14  export_prod_s06       export_prod_s06.gd  (include/exclude filter)
15  export_prod_s07       export_prod_s07.gd  (unknown-preset refusal)
16  export_prod_s08       export_prod_s08.gd  (templates-missing error class)
17  export_prod_s09       export_prod_s09.gd  (subdirectory census + run receipt)
18  export_prod_s10       export_prod_s10.gd  (icon + .uid census)
19  export_prod_s11       export_prod_s11.gd  (--main-pack launch + --quit-after receipt)
```
The C3 signatures are fixed in `reports/round-101/r101-E17.md` §"Spec rows" (6 exact tuples);
C2 and C1 signatures are owned by E12 and E0/E1..E11 — **the orchestrator should take them verbatim
from those shards, not rewrite them**. If E0's "12 scenario rows" count is authoritative, the extra
row inserts between s11 and the tail without disturbing the order above.

### 5.3 Harness edits the orchestrator must land with the rows (all in `run_battery.py`)
1. `:4026-4027` `cases_integrity` prefix tuple → append `"export_prod_"` and `"r101_"` (covers
   both r101 families).
2. Add `r101_expected_errors_all_matched` **iff** r101 rows carry allowlist entries; its prefix
   filter should be `("export_prod_", "r101_")`. Entries go in the named `expected_errors` dict,
   never in the CASES tuple.
3. `:1863` timeout sentinel → include the r101 export rows (R1).
4. Do **not** create any `<scratch>/out` artifact from r101 fixtures (R7).
5. Retire-or-keep `r95b_order_celloff_y1000`: keep → **528 CASES / 535 results**; retire (E17's
   recommendation, its signature is an unmeasured duplicate of `celloff_x0`) → **527 / 534**. The
   `r95b_` prefix keeps 34 other rows, so the r95 floor gate cannot go vacuous either way.

### 5.4 Verification order at integration (cheapest first, fail-fast)
1. AST census: 509 + 19 (or +18) rows, **all names unique** (the F1 gate must be non-vacuous over
   the new prefixes).
2. Targeted single-row replays of the 6 `r101_ytrans_*` rows (each ~1 s) — signatures are
   already byte-verified by E17 ×3.
3. `r101_seqfull_*` ×2 with the forged-extra-line mutant (E12/ver6/ver11 have the scripts).
4. The 11 `export_prod_*` rows **under load**, with the extended timeout — these are the only
   r101 rows whose runtime (nested boots, ~3–10 s each) can exceed the legacy 8 s budget.
5. One full battery run, then the fold/scrub pass. Expect `export_readiness` and
   `export_preset_missing` to stay green (they are untouched), and watch `probe_error_clause_surface`
   (the floor gate) for any dead entry introduced by the new allowlists.

## 6. Limits of this shard
* Observation: §2.1–§2.7 (all command + byte receipts above); risk R7 (source-verified),
  R1/R9/R10 (source-verified), R2 (reproduced, with the landed `file:line` defaults); the
  `export_prod_sNN` name convention (the landed fixtures print their own stems:
  `PASS export_prod_s01 …`, `PASS export_prod_s02 …`, `PASS export_prod_s04 …`,
  `PASS export_prod_s08 …` — `grep -oh "PASS export_prod[^\"]*" corpus/fixtures/export_prod_s*.gd`).
* Inference (not proven): the cold/warm cause in §2.3; that the s07/s08 fixtures will surface
  nested ERROR lines (depends on how E7/E8 print); that the s01/s10 `/tmp` defaults actually
  hit EDQUOT inside the battery (they are the measured failure mode of `/tmp`, but the battery's
  staging can change available space).
* Unknown: `--export-debug` (the legacy rows' mode) under the same cold/warm split; whether an
  *embedded* PCK with forged magic produces the same loader error class (mut5's open question);
  the exact final C1 row signatures until E0/E1..E11 land (6 of 11 fixtures landed at 16:27;
  s03/s05/s06/s07/s11 absent at that timestamp); the fleet's exact
  `AXES.md §The stagnation nudge` wording (fleet-root, outside this lane — not read).
* Left undone by this seat: no row registered, no shared file edited, no commit; the `/tmp`
  deviation is disclosed in §2.0.
