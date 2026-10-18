# r101 CRIT-4 — Cross-claim interference: export launches + swarm load vs C2/C3 timing margins

Seat CRIT-4 (LEAF) | lane game-dev-2d-shokunin r101 | host **devin** (this machine),
Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python 3.14.x, 32 cores.
Scratch: `/var/tmp/r101-CRIT4/` (NOT /tmp — see F0). Lane repo untouched except this
report + the three driver scripts under `reports/round-101/mutations/`.

Plan (5 lines) — COMPLETE:
1. Record load context ✔ (§1). 2. Read r100-critic §F2 + r95 offy context ✔.
3. Measure export-launch + godot wall times under load / storm ✔ (§2).
4. Quantify perturbation on C2 replay pins + C3 measurement ✔ (§2 F5/F6).
5. Per-claim envelopes/qualifiers ✔ (§3).

**Verdict.** C2's proposed full-replay pins are **safe to land** with pin-shape rules
(F5); C3's replacement measurement is **safe if tick-indexed** (F6); C1's
`export_prod` lattice carries **two hard qualifiers** — export determinism only
holds warm→warm (F1), and rc=0 can hide a corrupt PCK (F2) — plus path/output
qualifiers (F3, F4). All r87-class timing rows measured: only unpinned diagnostic
counters moved (F6, F7); every pinned PASS line was byte-stable across all arms.

## 1. Load context (measured; `uptime` at arm boundaries)

| time | loadavg (1/5/15) | arm |
|---|---|---|
| 16:21:24 | 41.05 / 21.42 / 13.72 | session start |
| 16:22:55 | 53.88 / 30.58 / 17.65 | scratch staged |
| 16:23:34 | 55.51 / 33.93 / 19.33 | export calibration |
| 16:26:00 → 16:26:40 | 52.12 → 59.45 | storm-1 arm (peak 59.45) |
| 16:28:15 → 16:28:27 | 47.08 → 41.49 | storm-2 arm |
| 16:29:38 | 30.78 / 40.38 / 28.02 | isolation arms |

Sibling lanes' godot processes + the g2d swarm were live throughout; nothing below
is an idle-host artifact. `/tmp` tmpfs: `16G total, 12G used, 3.2G avail, 80%`.

## 2. Findings

### F0 — `EDQUOT` on /tmp reproduced live (blanket qualifier)

First scratch write failed mid-copy:
`cp: error writing '/tmp/r101-CRIT4/proj/run_battery.py': Disk quota exceeded`
while `/tmp` showed 3.2G "available". This is the r100-critic caveat, live. Any
seat (C1's export scratch included) writing under `/tmp/r101-<key>/` can fail
mid-write; scratch moved to `/var/tmp/r101-CRIT4/` and all results are from there.
**Qualifier:** round-101 scratch goes to `/var/tmp/` or the orchestrator shows
`/tmp` healthy at integration.

### F1 — C1 export determinism holds ONLY warm→warm; cold copies diverge (hard qualifier)

Measured PCK sha256 (identical 4-file project, `--export-release "Linux/X11"`,
absolute out path):

| project state | pack | sha256 | boot |
|---|---|---|---|
| `storm` 1st-ever export (calib) | 1672 B | `30df6560…` | **CORRUPT** (F2) |
| `storm` warm, repeat (calib2/calib4) | 1848 B | `8aa316ce…` == `8aa316ce…` (diff runs 0) | valid |
| `sA` cold copy | 1848 B | `93fba298…` | (not booted)* |
| `sB` cold copy | 1848 B | `fa9b4c69…` | (not booted)* |
| `sC` 1st + 2nd export | 1848 B | `e6b2d41d…` == same | valid ×2 |
| `sE` abs + abs-repeat | 1848 B | `06734308…` == same | valid ×2 |
| `sF–sI` cold, 4-way concurrent, 1st-ever | 1848 B | 4 distinct shas | valid 4/4 |

`diffbytes.py` on sA vs sB: 20 differing bytes — 4 B at [827..830] inside the
exported scene (`node_ids\x00 \x00\x00\x00\x01\x00\x00\x00 ⟨u32⟩`) = the Main
node's **random scene-unique id**, plus its 16-B md5 in the pack index
([1476..1491]). String-set diff adds nothing else. So cross-copy sha equality is
architecturally impossible while node_ids are random; equality requires the same
imported state.

**Demand (C1):** the "determinism sha256 ×2" row must be defined as export #2 vs
#3 of the SAME project directory (warm), or pin the auditable subset
(magic/size/index paths). "Two fresh copies → sha equal" is FALSIFIED by the
measurements above.

*not booted — their shas/sizes match the valid 1848 B shape but were not
`--main-pack`-verified (honest scope).

### F2 — rc=0 hides a CORRUPT pack; boot receipt is the only check that catches it (hard qualifier)

Corrupt-shape signature (byte-level, reproduced): pack is 1672 B; its index has
**no `project.binary` entry** (string-set diff vs a valid pack: missing
`application/config/name`, `expstorm-…`, `application/run/main_scene`,
`res://main.tscn`, `application/config/features`); the corrupted entry points at
data whose header is `ECFG`-shifted. Boot of such a pack (`--headless --main-pack
<pck> --quit-after 10`) prints exactly:

```
ERROR: Corrupted header in binary project.binary (not ECFG).
   at: _load_settings_binary (core/config/project_settings.cpp:918)
ERROR: Couldn't load file 'res://project.binary', error code 16.
```

and the main scene never runs (no `STORM_MAIN ready`), while `rc=0` and the export
log still shows `[ DONE ] first_scan_filesystem` / `[ DONE ] savepack`.

Observed conditions (all with rc=0 unless noted):

1. calib — 1st-ever export of a fresh project, run *concurrently with my 35-run
   script matrix* (load 55): 1672 B, corrupt. 1 of 7 first-ever exports
   (calib, sC, sD, sF–sI) was corrupt.
2. storm1–storm4 after **12 rounds × 4-way concurrent FAILED export attempts**
   (relative-path failures, F3): the next 8 "successful" exports (2 rounds) were
   **8/8 corrupt**, sha-stable per project (e.g. `246cbed3…` twice), all size
   1672. Wiping `storm1/.godot` → re-export = 1848 B, boots `STORM_MAIN ready`.
3. Isolation negatives (all valid, boot-verified): one failed export then abs
   (sE); **12 sequential failed exports** then abs (sJ); cold 4-way concurrent
   successful exports (sF–sI, 4/4). So the trigger is neither failure-repeat nor
   concurrency alone — mechanism UNKNOWN; only the combination (1) and (2) is
   measured.

**Demand (C1):** every pack any row reads back must be `--main-pack`-boot-verified
(the lattice's launch-receipt row does this — extend it to the determinism and
census rows, or assert the boot line in every export scenario). rc==0, `[ DONE ]`
progress lines, magic, and nonzero size all PASS a corrupt pack; a warm-warm sha
comparison of two identically corrupt packs also PASSES (measured). Treat any
project that saw failed export attempts as requiring `.godot` hygiene before
determinism rows run.

### F3 — export output paths are project-dir-relative: `out/x.pck` fails even when cwd has `out/`

`godot --headless --path sE --export-release "Linux/X11" out/rel.pck` (cwd =
scratch root, which HAS `out/`) → rc=1:

```
ERROR: Prepare Template: The given export path doesn't exist.
ERROR: Project export for preset "Linux/X11" failed.
```

48/48 storm-1 attempts used relative paths and produced **no output file**; the
storm driver did not record rc, but the identical shape measured rc=1 in
calib2, calib3, sE and sJ. The battery's own export rows already `.resolve()`
their paths (`run_battery.py:1853-1855`, `4465-4466`) — absolute. **Demand:**
`export_prod` rows use absolute/resolved out paths (and pre-create parent dirs);
"rc=0" is not a success check (F2).

### F4 — concurrency probes for export launches

* Two concurrent exports of the same warmed project, distinct outputs (P1):
  both rc=0, both `93fba298…` (= sA's one prior sequential export, reproduced
  bit-for-bit under concurrency). Safe at this project size.
* Two concurrent exports to the SAME output path (P2, sA+sB): both rc=0, final
  file = `fa9b4c69…` (sB's warm sha) — silent last-writer-wins, no corruption
  observed, but the loser's bytes vanish while it reports DONE. **Demand:** never
  share an output path across arms; a determinism row reading a shared path can
  compare another arm's product.
* 4-way concurrent successful exports across projects (storm-2): all rc=0, each
  project's shas stable across 2 rounds (4 distinct warm-fixed shas).

### F5 — C2 `r100b_seq` replay: byte-stable under every arm; full-transcript pins feasible; pin-shape rules

Reps: `--clean=1` **12 runs** (6 ambient + 4 storm-1 + 2 storm-2) all sha
`2181f1ebcb5a516897f403eb8c56a9b544e1a0350904d83de213bb094736a079`;
`--clean=0` **7 runs** all sha `3d2429f2…`. The 4 divergences vs fresh pins
(cursor/touch/subvp/warp) are **deterministic contamination**, traceable in the
transcript: `cursor c0=(30.0,14.0)` is `localpos`'s earlier push at gpos (30,14);
`subvp cursor_root=(20.0,4.0)` / `warp w0 cursor=(20.0,4.0)` is the touch-emul
cell's event. Nothing in the transcript is wall-time or physics-step coupled.

Pin-shape rules for the critic's F2 fix (all verified on bytes):

1. The battery captures streams separately and concatenates **stdout first, then
   stderr** (`run_battery.py:1698-1701`); `run_process_streams` (1709-1717) keeps
   them separate. In `r100b_seq.gd` stdout = 17 lines (banner, blank, **14
   contiguous PASS lines**, `SEQ_DONE clean=N`); stderr = the 6-line `ERROR:
   Parameter "t" is null.` block. A `"\n".join` of the 14 PASS lines is a
   contiguous substring of the merged blob and **rejects** the F2 `m_seq` forgery
   (its forged print lands between two PASS lines, breaking contiguity).
2. Do NOT build a pin that interleaves the stderr ERROR block between PASS
   lines: the fd-level order I observed (`warp` → ERROR → `render`) is not what
   the battery's concatenated blob contains (ERROR block sits after `SEQ_DONE`).
3. Never include `env`-style diag lines (§F6) or wall-clock text in any new pin;
   the transcript contains none, keep it that way.

### F6 — C3 `r95b_order` celloff: pinned PASS line immune; only the unpinned `proc=` diag counter roams

16 celloff-family reps (off=0 ×10, `--offy=1000` ×4, off=1000 ×2) at load 41–59:
**5 distinct output shas for the off=0 family** (`36af4675`, `e497f8b0`,
`aa63fa26`, `b84fd9f0`, `f50608f9`). Byte diff in every pair: exactly one line —
the `R95B celloff env=…` diagnostic. `pf=65` constant in every observation;
`proc=` roamed **{149, 155, 156, 157, 158}**. All pinned values (ladder, vecs,
relpos, distinct_ticks, last_change_tick) are identical across all 5 shas; PASS
lines verified identical pairwise.

`--offy` retirement evidence on these bytes: `grep -c offy r95b_order.gd` = **0**
(no read site); `--offy=1000` output distributes in the *same* env-only variant
family as `--off=0` (zero behavioral delta), corroborating reviewer F1/simplifier
F1 independently of their receipts. **Demand (C3):** the replacement Y-translation
measurement must land on tick-indexed cells (the ladder/`t2_relpos` pattern);
never pin `proc`/wall time; a retirement census should cite the 0-read grep + the
measured zero-delta distribution, and must not be "fixed" by pinning env lines.

### F7 — r87 api_press class under this load: mode split is load-shaped; dual payloads are mandatory

`input_lattice --arm=api_press`, first payload = production (`ph1{…/1/1}`);
second = alt (`…/1/0`): ambient **3/10 alt**, storm-1 **6/8 alt**, storm-2 **2/4
alt** (pooled storm 8/12). The landed row already carries both payloads — that
design is load-necessary, and any new C2/C3 row that admits interposed-step
divergence must do the same. No rate/ratio is pinnable (r87's 27/30 "under load"
vs 70–75% here: sample- and load-dependent).

### F8 — wall-time envelope: 72× timeout headroom; export launches are the heavy neighbor

All **75 script reps** rc=0; wall time **0.76–2.08 s** (max: celloff off=1000 at
t=2.08 s; seq 1.4–1.8 s; api_press 0.76–1.27 s) against the battery's per-case
timeout budget (the export-launch precedent uses 60 s; my runs used 150 s) —
≥72×. A warm PCK export launch costs 2.3–3.3 s and is not measurably slowed by
4-way export concurrency (storm-2: 2.33–2.68 s each). The storm arms did **not**
inflate any script-run wall time beyond the ambient range: no timeout-margin
mechanism exists in the observed envelope; the interference that IS real lives in
the export bytes (F1–F2) and the unpinned counters (F6), not in the clock.

## 3. Per-claim envelope / qualifier demands (deliverable)

| claim | demand |
|---|---|
| C1 base PCK row | assert output file exists + `--main-pack` boot receipt; rc/magic/size/[DONE] all pass a corrupt pack (F2) |
| C1 determinism ×2 | define as warm→warm on the same project dir (measured equal); do NOT compare cold copies (measured 20 B apart); boot-verify at least one pack (two corrupt packs compare equal) |
| C1 `--main-pack`/`--quit-after` row | keep; make it the validity gate for every other export row's product |
| C1 any export row | absolute/resolved out paths; parent dir pre-created; never share an output path across arms; `.godot` hygiene after failed attempts |
| C2 full-replay pins | land the 14-PASS-line stdout transcript (+`SEQ_DONE`); no stderr mid-transcript; no env/proc/wall cells; stable ×19 replay reps under load 41–59 incl. two export-storm arms |
| C3 offy retirement / replacement | replacement must be tick-indexed (pf-indexed) like the ladder; cite 0-read grep + zero-delta distribution; never pin proc/env; keep both-mode tolerance if the new cell can interpose |
| C2/C3 any r87-class cell | carry both payloads; no rate pins; timeout budget ≥ 30× the 2.1 s max observed run |

## 4. Evidence index (commands + bytes)

* Drivers: `reports/round-101/mutations/r101-crit4_ambient.sh`,
  `r101-crit4_storm.sh`, `r101-crit4_storm2.sh`, `r101-crit4_race.sh`.
* Logs + per-rep outputs: `/var/tmp/r101-CRIT4/logs/` (matrix_ambient.log =
  40 reps; matrix_storm.log = 26 reps; storm2 = 9 reps; per-rep `.out` files
  carry full merged stdout+stderr, sha256 recorded per rep).
* PCK bytes: `/var/tmp/r101-CRIT4/out/` (calib*, sA/sB, sC*, sD, sE*, sF–sI,
  sJ_abs, ok_*, race*, sE_clean etc.) with `pckdump.py` / `diffbytes.py` outputs
  cited above; boot logs `logs/boot_*.out`, `logs/pack_*.out`.
* Harness line cites: merge shape `run_battery.py:1698-1701`,
  streams `1709-1717`, existing export `.resolve()` `1853-1855`, `4465-4466`,
  project-name stamp `1683-1687`.
* Engine: `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`.

## 5. Binding to the siblings' live artifacts (observed at report time)

Three r101 artifacts appeared in the workspace while this seat measured; the
qualifiers above bind to them directly:

* `corpus/fixtures/r101_seqfull.gd` (C2, 836 lines) — full-replay receipt
  (`SEQ_BEGIN … 14 contiguous cell lines … SEQ_END digest=`). F5's pin-shape
  rules apply: the pinned span must stay pure stdout (the render cell's ERROR
  block appears AFTER stdout, appended by `run_battery.py:1701`, not inside the
  span); the measured transcript stability (19/19 identical replay reps) covers
  the digest.
* `corpus/fixtures/r101_ytrans.gd` (C3, 332 lines) — consumes `--offy`, adds a
  `census` retirement arm and absolute-y reads. F6 applies: keep pinned cells
  tick-indexed (no proc/env); the census reproduces my 0-hit grep
  (`grep -c offy r95b_order.gd` = 0) and should also cite the zero-delta
  distribution measured here.
* `corpus/fixtures/export_prod.gd` (C1) — already runs `--main-pack … --quit-after 5`
  (line 509): the boot receipt F2 demands exists; ensure the determinism row is
  warm-warm (F1) and out paths absolute (F3).

## 6. Unknowns / not done

* Corruption trigger in F2 not isolated to a single variable (two arms corrupt,
  four isolation arms clean; mechanism UNKNOWN, byte signature known).
* sA/sB/calib3 packs were not boot-verified (noted inline); all shas/sizes cited
  are as-listed.
* Storm-1 export attempts' rc values were not recorded by the driver (failures
  evidenced by logs + missing outputs; rc=1 measured on the same shape elsewhere).
* Wall-clock: no measurement of the 3D lane's own interference contribution
  (hands-off); numbers are "under the observed host load", not a controlled
  load curve.
* No battery run (per rules); no repo file touched beyond this report + drivers.
