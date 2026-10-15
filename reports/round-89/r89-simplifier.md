# game-dev-2d round 89 — simplifier (r89-simplifier): one proven deletion in `geo2d_lattice.gd` (−2 lines, dead accumulator, zero pinned bytes touched); unused non-row arms, the crash-arm tail, the `--frames` knob and both r89 allowlist entries audited and dispositioned

Seat `SIMPLIFIER` (LEAF) | lane `r89` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
Work commit **`8cea888`** (r89 author; HEAD at session start; HEAD moved to
`7a45a60` mid-session — see §7 custody notes).
**No tracked file written, no commit, no git mutation by this seat.** Writes are
this report and `corpus/live/r89-simplifier/**` only. Batteries ran sequentially,
never in parallel (control → folded).

**`lsp` disclosure.** No `lsp` device is exposed in this dispatch — the only MCP
server is `rea` (Ghidra/binary analysis); no GDScript/Python language server is
installed (`gdscript-lsp`, `gdtoolkit`, `gdls`, `gd-language-server`,
`godot-lsp` all absent from PATH; no such pip package). `references`/`definition`/rename
were therefore **unavailable**, and no cold result is recorded as absence. Caller proofs rest on (a) complete textual
enumeration of every occurrence of the suspect state, (b) a mutator-aware
write-only-store scan over both new probes, and (c) fresh-process byte equality
of the folded tree against the unmodified control and both canonical runs.

---

## 1. Method and proof artefacts

Apply the patch in a scratch copy → direct arm reps both sides → full battery
both sides → every row's verdict tuple and normalized output compared against the
unmodified control and the author's two canonical green 235-row runs.

| artefact | content |
|---|---|
| `corpus/live/r89-simplifier/r89-simplifier-fold.patch` | unified diff, **−2 lines**, all in `corpus/fixtures/geo2d_lattice.gd` (581 → 579); `git apply --check` clean against HEAD; sha256 `8d467cb1…` |
| `fixtures-after/` | runnable folded project: full `corpus/fixtures/` copy (`__pycache__` omitted) with `run_battery.py` byte-identical (`e49b488d…`) and `project.godot` byte-identical (`8de8b3af…`); one differing source file: `geo2d_lattice.gd` `9784716b…` → **`608a322e…`**, 579 lines |
| end-to-end apply | patch applied in a temp git repo to the `8cea888` bytes → output sha `608a322e…`, byte-equal to `fixtures-after/geo2d_lattice.gd` |
| `runs-before/20261015T201037827701Z/` | battery on the **unmodified** tree (harness bytes at proof time `e49b488d…` = the `8cea888`/HEAD bytes, 235 rows) → 235 rows, rc=1 (flake rows below; 20/20 r89 rows PASS) |
| `runs-after/20261015T201604743173Z/` | battery on `fixtures-after/` (same harness bytes, copied verbatim) → 235 rows, rc=1 (flake rows below; 20/20 r89 rows PASS) |
| `reps-before/`, `reps-after/` | direct arm reps, battery launch shape: `ringhits` ×4/side, `atlasempty`/`polyendpoly`/`lineempty` ×1/side |
| `reps-analysis.txt` | per-rep sha table, cross-side comparison, before-reps vs all 6 author canonical receipts, declared stderr delta |
| `rowcheck.py`, `rowcheck-folded.txt`, `rowcheck-control.txt` | per-row check of all 20 r89 CASES rows: verdict tuple + normalized output, folded vs control vs author runs4/runs5; plus the r89 census rows and gate values |
| `compare-folded.txt` | `corpus/live/r87-baseline/compare.py godot` (r79-baseline tool, reused unmodified): folded vs control vs `r89-author/runs4` vs `runs5` |
| `static-proof.txt` | occurrence enumeration, write-only scan, arm↔row matrix, convention/provenance citations |
| `receipt-audit.txt` | both allowlist entries vs the emitted receipt lines, census extract, per-arm stderr sizes, per-row `expected_errors` |
| `parse-before/after.out\|err` | `godot --headless --check-only` rc=0 on both sides |
| `byte-identity.txt` | `run_battery.py` / `project.godot` sha equality across the two trees |

## 2. Killed — the fold, one deletion (SP1), **proven byte-identical**

One patch, `geo2d_lattice.gd` only. No pinned signature, no `run_battery.py`
byte, no `.tscn` byte is touched.

| # | site (was) | why dead | proof |
|---|---|---|---|
| SP1 | `_arm_ringhits`'s `names` accumulator `:550` + `:555` (−2) | **write-only store** — the variable is built but never read; the output loop reads `bd[0]` from `builds[]` (`:567`), not `names` | (a) `names` occurs exactly twice in the file — declaration `:550`, `names.append(String(bd[0]))` `:555`; no other occurrence anywhere in the file (grep) and no other fixture/harness references it; (b) a mutator-aware scan over every `var`/`const` in both new probes (assignment/index-assign/`.append()`-class calls count as writes, everything else as a consumption) flags **exactly one** never-consumed store — `names`; `input89_edges.gd`: none; (c) the value cannot escape: no read, no return, no aliasing (`builds[i][0]` is the string actually used), and `PackedStringArray.append` has no side effects; (d) folded vs control: `ringhits` tuple + normalized merged output byte-identical (4+4 reps, full battery — §3); (e) full battery: all 235 rows present, all 20 r89 rows PASS, r89 rows byte-identical to control (0 tuple mismatches / 0 output diffs) |

## 3. Retained behavior — the narrow existing check, both sides

- **Direct reps** (battery launch shape, `timeout -s KILL 25 godot --headless
  --path proj-<side> --script res://geo2d_lattice.gd -- --arm=…`): `ringhits`
  **4/4 per side, stdout sha `546eb612…`, stderr 0 B, rc=0 — cross-side
  identical per rep**, and each before-rep is byte-equal to **all six** author
  canonical receipts (`runs/geo_ringhits.rep1..6`). `atlasempty` 1/1 identical
  incl. stderr; `lineempty` 1/1 identical incl. stderr (rc=134 ≡ −6);
  `polyendpoly` stdout identical (the stderr delta is the declared
  backtrace-line-number shift `:577/:578` → `:575/:576`, normalized by the
  established compare tool's `.<ext>:<N>` rule — verdict-inert).
- **Full battery, folded**: 235 rows, **20/20 r89 rows PASS**,
  `r89_expected_errors_all_matched=true`, census r89 rows live
  (`atlasempty` matched=1, `polyendpoly` matched=2, `dead_in_run=false`,
  `bare_classification_rejects=true`, `allowlisted_classification_passes=true`).
- **Folded vs control**: `common=235 new_only=0 old_only=0`, tuple_mismatches=3
  (`audio_playback`, `input_lattice_press_phys`, meta cascade) — all documented
  pre-existing flake classes on rows r89 does not touch; **r89 rows:
  tuple_mismatches=0, output_diffs=0**.
- **Folded vs both canonical green runs** (`r89-author/runs4`, `runs5`):
  `common=235`, tuple_mismatches=5 (same flake classes: `audio_playback`,
  `negative_transition`, `overlap`, `transition`, meta), **r89 rows:
  tuple_mismatches=0, output_diffs=1** — the single diff is
  `input89_edges_exact` line 12, the **declared load-bimodal 2-payload envelope
  row** (mine emitted mode L `w_jp[ex=false inex=false]`, canonical emitted mode
  Q `…inex=true`); the control run shows the **identical single diff** vs
  canonical, so it is not fold-attributable.
- **Parse/exec check**: `godot --headless --check-only` rc=0 on both sides.
- **Declared receipt delta**: the only raw-byte difference anywhere is
  `polyendpoly`'s stderr GDScript backtrace line numbers (`res://geo2d_lattice.gd:577`
  → `:575`, `:578` → `:576`); the ERROR text (whitelisted exact-shape) and every
  stdout payload are unchanged, and the compare tool normalizes `.<ext>:<N>`.
  No pinned payload changes anywhere.
- **Flake accounting (recorded, not excused)**: both my runs flaked on the
  author's documented pre-existing classes under foreign load (load average
  **112–145** on 32 cores; the author saw load 25→127): control failed
  `overlap`, `transition`, `negative_transition`, `input_lattice_press_phys`
  (3rd envelope mode) + the meta cascade; folded failed `overlap`, `transition`,
  `negative_transition`, `audio_playback` + the meta cascade. **Every flake row
  is non-r89**; the 20 r89 rows are PASS in both runs and byte-identical to
  control. The `dead_entry_count=2` seen in both runs is entirely
  `negative_transition`'s two entries (its row died on the flake) — the r89
  entries stay live and `r89_expected_errors_all_matched` is `true` in both runs.

## 4. Task-item cross-checks

**(a) Unused probe arms — two exist, both dispositioned keep (§5 SP2).**
Parsed from `CASES` (ast.literal_eval): `geo2d_lattice.gd` has 20 declared arms,
18 referenced by rows; the two non-row arms are `bridge_hole` / `bridge_hole2`
(two functions = lines 383–428 = 46 lines, plus the two dispatch lines = 48
lines deletable). `input89_edges.gd` is 2/2. No row references a non-existent
arm on either probe. The two arms are **battery-unreachable**, but they are
deliberate receipt arms, not dead code: the scout's own row list says
**"Not rows (receipts only, do not author): … `geo_bridge_hole` /
`geo_bridge_hole2` (the falsified `merge`-hole hypothesis …)"**
(`r89-scout.md:436–438`), their 6-rep receipts exist
(`r89-scout/RECEIPTS.md:63–64`, 12 files), and non-row evidence arms are the
established convention: `camera_proc.gd` retains **5 inert `diag_*` arms that no
CASES row references** (`r85-author.md:34`, still present) and `r87_edge.gd`
retains `jmode` after the author declared it "not authored"
(`r87-author.md:17`). Deleting them would stale the verbatim-landed probe sha
chain for **zero** battery-byte gain (they are unreachable, so they cost no
pinned byte today).

**(b) Unreachable paths — the `lineempty` arm tail is unreachable, dispositioned
keep (§5 SP3).** `_arm_lineempty` (`:346–350`) SIGABRTs inside
`offset_polyline(empty,…)` (rc=134 ≡ −6 ×6 author + ×3 scout; stdout carries
only the pre-call `R89 lineempty call=…` line), so `_it("result", …)` + `_pass()`
never execute. They are the arm's natural post-call readback and the
failure-shape canary for a future engine that stops crashing; the probe
convention keeps post-crash tails (`spontaneous_crash_probe.gd` retains
`quit(1)` after `OS.crash()`).

**(c) Dead `expected_errors` entries — none; both r89 entries are live.**
Cross-checked against whitelist + receipts: `geo2d_lattice_atlasempty`'s entry is
byte-identical to the emitted line (`matched_lines=1`), `geo2d_lattice_polyendpoly`'s
entry is byte-identical and fires **twice** per run (`matched_lines=2`), both
`dead_in_run=false`, `bare_classification_rejects=true`,
`allowlisted_classification_passes=true`, in the canonical runs **and** in both
of my runs; `r89_expected_errors_all_matched=true`. All 18 other r89 rows carry
no entry and their arms emit **0 B stderr** (receipt-audited).

**(d) Gate keys — no dead key.** `r89_expected_errors_all_matched` is the only
floor covering the r89 prefixes (there is no global all-matched gate;
`dead_entry_count` is carried as data, not gated), so it is non-redundant and
non-vacuous for `geo2d_lattice_`. Its `input89_edges_` member is inert today
(that prefix carries no entries) but is the future-coverage clause for the round
prefix — the same shape as the r87 gate's entry-less cases and the author's
declared intent.

**(e) `--frames=` knob — not dead.** No CASES row passes it, but the scout's
round-2 receipt driver uses it (`run_cells2.sh:36`, `geo_bridge_tps120_f120`,
6 reps) — a live replay surface. Kept.

## 5. Candidates rejected (evaluated, did not survive the bar)

| # | candidate (was) | verdict | reason |
|---|---|---|---|
| SP2 | `_arm_bridge_hole` + `_arm_bridge_hole2` + dispatch lines `:383–428`, `:103–104` (−48) | rejected | Battery-unreachable (proven), but receipt-only by scout declaration ("Not rows … do not author") with 12 receipt files; non-row evidence arms are the retained convention (`camera_proc` 5 inert `diag_*` arms, `r87_edge` `jmode`); deletion stales the verbatim probe sha chain for zero battery-byte gain. r88-SP8 provenance precedent. |
| SP3 | `_arm_lineempty`'s `result` + `_pass()` `:349–350` (−2) | rejected | Unreachable today (SIGABRT), but it is the post-call readback / failure-shape canary for a non-crashing future engine; convention keeps post-crash tails (`spontaneous_crash_probe.gd`). r88-SP3/SP4/SP10 precedent (deleting changes failure shape). |
| SP4 | `--frames=` parse branch `:19–20` (−2) | rejected | Exercised by the scout's receipt driver (`run_cells2.sh:36`); live replay knob, not dead. |
| SP5 | `r89_expected_errors_all_matched` gate or its `input89_edges_` member | rejected | Non-redundant floor (§4d); the inert member is deliberate future coverage, r87-gate precedent. |
| SP6 | Either r89 allowlist entry | rejected | Both live and necessary — bare classification rejects each row without them (§4c); deleting would flip `geo2d_lattice_atlasempty`/`polyendpoly` to FAIL. |
| SP7 | `_: _arm_census()` / `_: _arm_exact()` dispatch fallbacks | rejected | Defensive default; the PASS line carries the arm name, so a row cannot silently fall through (scout §"silent fallback" claim); removing them turns an unknown arm into a silent no-op — worse. |
| SP8 | Cross-arm duplicate pins (`ops` vs `joins` offset pins; `ring`/`ring2`/`ring4` shared rest values) | rejected | Deliberate cross-arm evidence (join×end lattice vs boolean-ops; hole-collider discriminator), each row arm-verified by its own name in the PASS line. Not dead. |
| SP9 | CASES rows / allowlist keys / comments deletions | rejected | Nothing dead — all 20 rows PASS in 5/5 author reps and both of my runs; both entries live; comments are the declared provenance block. |

## 6. Tradeoff (apply-cost, disclosed)

Applying the patch **stales recorded provenance** (new sha `608a322e…`, 579
lines): the scout→author→boundary sha chain (`9784716b…` appears 2× in
`r89-scout/manifest.sha256`, 11× in `r89-author/manifest.sha256`, 1× in
`r89-boundary/manifest.sha256`), report citations
`reports/round-89/r89-author.md:21` (sha + 581 lines),
`r89-scout.md:431`, `r89-scout.md:523`, `r89-boundary.md:42`, `r89-boundary.md:322`,
and the tracked harness comment `corpus/fixtures/run_battery.py:419`; it also
shifts `polyendpoly`'s stderr backtrace lines `:577/:578` → `:575/:576`
(normalized by the compare tool, verdict-inert). Runtime weight is zero (one
unread local). Honest recommendation: **apply only as a bundle with the next
landing that touches the r89 block** (so the sha/line citations can be updated in
the same commit); otherwise defer. The patch is left unapplied and proven.

## 7. Result

- **Deletion made (scratch-proven, unapplied):** 1 site / **−2 lines**,
  `geo2d_lattice.gd` 581 → 579, sha `9784716b…` → `608a322e…`; patch
  `corpus/live/r89-simplifier/r89-simplifier-fold.patch` (`git apply --check`
  clean; end-to-end apply reproduces the folded bytes exactly).
- **Proven:** folded `ringhits` byte-identical in 4+4 direct reps (and equal to
  all 6 canonical receipts); all 20 r89 rows byte-identical folded vs control
  (0 tuple mismatches / 0 output diffs) and tuple-identical vs both canonical
  runs; parse rc=0 both sides; the only raw delta anywhere is the normalized
  traceback line numbers.
- **Preserved contract:** all 235 rows, all 20 r89 pins, the 2-payload
  `input89_edges_exact` envelope, both r89 allowlist entries, the r89 floor gate,
  the descendant ordering razor, and `run_battery.py` (untouched by this fold).
- **Cross-checks:** no dead r89 allowlist entries; no dead gate keys; the two
  non-row arms, the crash-arm tail and the `--frames` knob are deliberate
  evidence/replay surfaces (kept, with convention citations); the write-only
  scan found no other never-consumed store in either new probe.
- **Custody notes:** no tracked file written, no commit by this seat. At proof
  time `corpus/fixtures/run_battery.py` was the r89 bytes (`e49b488d…`, equal to
  `8cea888` and to the current HEAD `7a45a60`); **after** my runs a foreign r90
  author lane modified the shared working tree's harness (+74 lines, 12
  `r90_*` rows, now `76c0b1f5…`, mtime 17:22:39 −0300) — not this seat's write;
  both of my batteries loaded the r89-era bytes (235 rows, no `r90_*` rows), so
  the proof stands on the r89 block. HEAD also moved mid-session
  (`8cea888` → `7a45a60` r92 boundary at 20:21:31Z, sibling r92/r95/r93/r98/r100
  commits); none of the new commits touches `geo2d_lattice.gd`,
  `input89_edges.gd` or `run_battery.py` (verified), so the probe bytes this
  fold targets are still HEAD's bytes. Batteries ran sequentially (control
  20:10:37→20:16:04Z, folded 20:16:04→20:21:31Z); the direct arm reps and parse
  checks ran while the control battery was live — disclosed, and no port-bearing
  arm was involved. Foreign load 112–145/32 cores during the window; all flake
  rows are the documented non-r89 classes. Cosmetic scout nit:
  `r89-scout.md:523` labels the primary probe "17 arms" while the landed probe
  has 20 (17 was the round-1 cell count) — no fold.
- **Stop line:** the next candidates would harm an axis — SP2 (scout receipt
  provenance), SP3 (failure-shape canary), SP4 (receipt replay knob), SP5/SP6
  (gate floor / allowlist entries), SP7 (defensive fallback), and any
  pinned-byte or cited-receipt change. Stopped here.

Seat output complete.
