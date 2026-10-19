# r103 SCOUT — Census shard

Plan (5 lines):
1. CASES count at HEAD via run_battery cases listing (grep, no execution) — expect 536.
2. Grep fixtures for arms that legitimately print MULTIPLE `^PASS ` lines per process (C2 allowlist).
3. Enumerate routed-but-unlanded items from r101/r102 adjudicators + r100 critic (pointers, verbatim).
4. Probe export_div surface census: existing export_div*.gd files, preset/PCK rows, user:// isolation (read-only recon).
5. Publish shard <=400 lines with verbatim evidence; label observation vs inference vs unknown.

Host (SCOUT seat): start `20:55:16 up 1 day, 20:55, 1 user, load average: 1.82, 1.76, 1.62`;
end `20:58:40 up 1 day, 20:58, 1 user, load average: 12.22, 6.62, 3.51` (spike = my own
mut02 export run, ~14 s of Godot import+export; sibling lanes unknown). No device-census
token is pinned anywhere below. Godot `/usr/bin/godot 4.7.2.stable.arch_linux.ed1daf0bf`.
Base: commit 6e3e87f7, `corpus/fixtures/run_battery.py` sha256
`40440356f0bf04481f518adc332d1ebb7ba79213878a9f3836421a512828a5c4`.
`run_battery.py` was NEVER executed by this seat; all probes were read-only reads,
targeted `godot --headless --check-only` on a scratch copy, or the landed mutation
scripts (which do not run the battery).

Status: COMPLETE. Labels: [O]=observation (verbatim measured), [I]=inference, [U]=unknown.

## S1 — CASES count at HEAD (claim: 536)  [O]

Method: `ast.parse` of run_battery.py, walk to the `CASES = [ ... ]` assignment, bind
`found = node.value` (AST List, `lineno 18`, `end_lineno 1719`).

- `CASES` element count = **536**; named entries = 536; non-tuple elements = `[]`;
  duplicate names = `[]` → 536 unique row names. (Expectation 536 confirmed.)
- results rows in the r102 receipt = 554, all unique; `CASES - results = []` (0 missing:
  the execution loop ran every registered row).
- `results - CASES` = 18 rows: the 16 `probe_*` meta arms (`script=None`, `output=None`)
  plus 2 probe-failing-only rows `mutant_broken_scene_route`,
  `mutant_level_collision_removed`. `export_readiness`/`export_preset_missing` ARE
  CASES rows with harness scripts `__godot_export__` / `__godot_export_missing__`.
- Row algebra for the receipt-shape gate: 554 = 536 CASES + 16 probes + 2 mutants.

## S2 — w4 multi-PASS allowlist completeness (independent recompute)  [O]

Independent parser (regex `^PASS(\b|$|[:=])`, my own code, not w4's script) over both
r102 receipts (`corpus/live/runs/20261018T212500022987Z/verdicts.json`,
`...T213443471189Z/verdicts.json`):

- recomputed multi-PASS set = **19 cases in each run**; sets identical to each other and
  to `reports/round-103/mutations/r103-w4-census.json` (`run1==census`, `run2==census`,
  set-diff both directions `[]`); per-case counts identical (no mismatches).
- per-script PASS-count identity run1 vs run2: **ALL IDENTICAL** across all 75 script
  keys → the allowlist is stable, not timing-dependent.
- Complete class inventory of the 538 output-carrying rows: **471 single-PASS**,
  **19 multi-PASS** (r100b_seq 2×14, r101_seqfull 2×14, export_prod 7 rows (2–3 lines),
  export_launch 8 rows (2–3 lines)), **48 zero-PASS**, plus 16 no-output probe rows.
- Static-vs-receipt check [O][I]: 69 fixture files carry static `print("PASS` sites
  (top: particles_lattice 20, r100_gui 14, r100b_seq 14, anim_lattice 12), yet only 4
  scripts produce multi-PASS rows. The rest are arm-dispatched (one PASS per process):
  e.g. r100_gui.gd has 14 print sites and 14 rows × 1 PASS. [I] A source-derived
  allowlist would be wrong in both directions; the receipt-derived one (w4) is correct.
- **Gate consequence** [O]: a multi-only allowlist is insufficient. Zero-PASS rows are
  not banner-only — all 48 carry non-banner content and `actual_exit == expected_exit`
  (48/48): expected-exit histogram `{2: 36, -6: 4, -9: 1, 1: 3, 0: 4}`; 41/48 carry
  `ERROR:` evidence lines. 7 have no `ERROR:` line (`export_readiness`,
  `geo2d_lattice_lineempty`, `nav_lattice_teardown_crash`, `r92_tilemap_nullts_crash`,
  `crash_self_sigkill`, `descendant_pipe_detached_control`,
  `descendant_pipe_forged_signature_release`) — evidence is exit code / marker lines
  instead. Informational non-PASS evidence lines exist in the reject arms
  (e.g. `OBSERVED camera_limit ...`, `HEALTH_GAUGE_NEGATIVE ...`, `BUTTON_FOCUS ...`,
  `SLIDER_* values=...`, `ei=-2 -> pressed=1`); [I] these are what r102 called the
  "by-design reject-arm print lines". Receipt-shape gate must carry all four classes
  (single/multi/zero/no-output) or be circumvented by a row changing class.

## S3 — w5 gate splice: checkpoint + 2 defects found by running it  [O]

- `python3 reports/round-103/mutations/w5_export_div_gate_splice.py --check` →
  `gate_key_count=0 count_key_count=0 tuple_patched=0 anchor_gate=1 anchor_tuple=1`,
  `PRE-SPLICE`, exit **2** (as designed; patch NOT applied).
- `git apply --check` on `w5_export_div.patch` → clean; same for the three S0 patches
  (`r103-S0-E1-r97-F6-scene_marker.patch`, `r103-S0-E2-r99-F2-r99b_modes.patch`,
  `r103-S0-E3-r100-SP2SP3-r100b_seq.patch`) → all `OK`, exit 0.
- **W5-D1 (defect): `--self-test` exits 1, cells L–R never run.** Cells A–K (11) PASS,
  then `NameError: name 'results' is not defined` at
  `w5_export_div_gate_splice.py:206 → eval_expr (:138)`, frame `File "<sf>", line 4142`
  (the `cases_integrity` expression). Reproduced verbatim by my instrumented rerun
  (`/var/tmp/r103c-scout/ci_recheck.py`, log `/var/tmp/r103c-scout/w5_selftest.log`:
  `TRUE_EXIT=1`, 11 PASS cells). Root cause [I, high confidence]: `eval_expr` evaluates
  `eval(code, {"__builtins__": ...}, ns)`; `cases_integrity` nests a genexpr
  (`any(... for r in results)`) inside another genexpr, and comprehension scopes resolve
  free names via the eval *globals* only — the `ns` locals mapping is invisible to the
  inner comprehension. (Cells C–K pass because their names are outermost iterables.)
  In situ the expression is fine: inside the battery's function body, `results`/`CASES`
  are enclosing locals captured by closure.
- **W5-D2 (defect): cell L's expectation is unsatisfiable.** `cases_integrity`'s
  existence check requires a row for every one of the 13 named prefixes; cell L supplies
  only an `export_div` row plus `r101_seqfull_clean` *as a CASES name*, no `r101_seqfull_*`
  row → `all(...)` is False, so `is True` cannot hold even with a fixed evaluator.
  [O] measured with a function-local evaluator: `L recheck = False (expected True)`.
- Independent corrected rerun (function-local scope, mirroring the battery; same
  expression text extracted from the spliced source): `M` fail-closed on zero export_div
  rows **PASS**, `N` duplicate-CASES-name **PASS**, `P` false on the real 554-row
  artifact (0 export_div rows) **PASS**, `P'` live (unspliced) gate true on the same
  artifact **PASS**, `Q` true after 2 synthetic export_div rows **PASS**. [I] The gate
  expressions behave as documented; the failures are harness-side.
- **Atomicity requirement** [O]: the w5 patch adds the gate texture only; `w5_export_div.patch`
  contains NO CASES rows. With zero registered `export_div_` rows the spliced battery would
  evaluate `r103_export_div_count_floor` = `(0 == 0)` and `(0 >= 1)` → **False**, and
  `cases_integrity` → **False** (cell-M semantics measured above) ⇒ next battery red.
  w5's own docstring says the same; independently confirmed. H1+H2 must land in the SAME
  splice as the C1 CASES rows, and `--min-rows N` should be frozen to the landed row count.

## S4 — mut02 (C1/s02 discrimination) — landed script, run by SCOUT  [O]

`nohup python3 reports/round-103/mutations/mut02.py` → exit 0, 13.7 s
(`/var/tmp/r103c-scout/mut02.log`, `out/mut02_verdicts.json`, artifact
`/var/tmp/r103-mut2/out/app.x86_64` 73 519 416 B, `app.pck` 5 204 B; host load 12.02
during the run). Key cells:

- genuine XDG arm: `PROBE_STYLE arm=genuine naive_pass=true anchored_pass=true`.
- spoof arm (override silently dropped + text-forged claim): `naive_pass=true`,
  **`anchored_pass=false`** → the anchored composite clause REJECTS the spoof while a
  naive clause accepts it. Discrimination is real, not tautological.
- XDG resolution laws measured (fold into C1 s02/s05 expectations): XDG empty string and
  XDG relative path are NOT honored (fall back to `$HOME/.local/share/godot/app_userdata`);
  XDG pointing at a *file* → child rc 0, no marker on disk, userdir string still reported
  under the file path; XDG unwritable dir → marker *path* reported but
  `disk_marker_under_xdg=false`.

## S5 — mut05 defect (C2/W2 evidence currently absent)  [O]

`python3 reports/round-103/mutations/mut05_gate_evasion.py --emit-only` → exit **1**:
`ValueError: not enough values to unpack (expected 3, got 2)` at `:140`, frame `:188
main → emit`. Cause: `build_evasions` (`:76-127`) appends ten **2-tuples**
(`ev.append(("s1a_banner_forged_seq", mutate(...)))`) and returns `ev, cases`, while
`emit` unpacks `(n, r, d)`. Consequence: `evasions.json` is never written — the evasion
battery has produced **zero** evidence. Same defect class as r102's mut01/mut06 staging
defects. Line-pair for the owner (not applied by this seat): either append
`(name, row, note)` triples or unpack two-tuples with a separate note map.

## S6 — export_div surface census (C1)  [O]

**The family was IN FLIGHT during this seat** (sibling E-seats writing while I censused):
s01/s02/s03 all changed bytes between 18:53 and 21:00 local. Point-in-time anchor below
is the set I validated at UTC 00:00:13–00:00:25 (in-repo bytes re-hashed after the runs
and unchanged — validated sha == repo sha for all three).

| fixture | bytes | sha256 (validated == repo, UTC 00:00:25) | `--check-only` |
|---|---|---|---|
| export_div_s01.gd | 23 677 | `f8af56d4100e4b3c9d89a300cc110755c3e119c28e780d8d83bd5c982049dba8` | rc **0**, 0 parse errors |
| export_div_s02.gd | 17 975 | `c08792c1c208d47a8af66c669e7296eb6a1d94fe3d20872aeb73d4d6620a4898` | rc **0**, 0 parse errors |
| export_div_s03.gd | 18 014 | `b27a7ab4235a350b6a34bc885fe3554b81afe8037aa34bdfc1593d2e5c219f40` | rc **0**, 0 parse errors |

- s02 changed **mid-seat** (`50b56438…` 17 588 B at 18:53 → `c08792c1…` 17 975 B at 20:57);
  my first validation (rc 0) was against the older bytes — the table re-validates current
  bytes. s01 (`87f101fc…` → `f8af56d4…`) and s03 (`6552b658…` → changed again) also moved;
  s03 at `6552b658…` **failed to parse** (rc 1, e.g. `Parse Error: Cannot infer the type
  of "sha_match" variable because the value doesn't have a set type` at `:478`, plus
  `a_match`/`b_match` at `:441`) and was repaired within ~2 min. [I] any evidence quoted
  for these fixtures must carry its sha — live shas are a moving target this round.
- Method (verbatim): fresh scratch project `/var/tmp/r103c-scout/proj4/project.godot`,
  `cp` of each fixture, `sha256sum` of the copy, then
  `timeout 60 godot --headless --path /var/tmp/r103c-scout/proj4 --check-only --script res://export_div_s0N.gd`;
  rc from `$?`, parse errors counted by `grep -c "Parse Error"`. No s04/s05 fixtures.
- Registration drift confirmed (unchanged by the in-flight writes):
  `grep -c "export_div" corpus/fixtures/run_battery.py` = **0**; run_battery.py sha still
  `40440356…`. No `export_div` reference anywhere in the lane outside `reports/round-103/`
  and the fixtures themselves → the family is unreachable by the battery; the w5 patch is
  the only in-tree registration vehicle (S3).
- Shape: s01 `VARIANT=div_s01`, presets `Embed` (embed_pck=true) / `Stock` (false) — the
  preset-vs-`--export-pack` divergence row family; s03 `VARIANT=div_s03`, presets `PckOnly`
  (embed_pck=false) / `Embed`, disjoint beacon include/exclude filters — multi-preset
  sequential; s02 arms `iso` → rows `export_div_s02_user_iso`, `xdg` →
  `export_div_s02_xdg_override`. All three emit column-0 `print("PASS export_div s0N ...")`
  (s01 :122, s02 :121, s03 :113) → matches the `^PASS(\b|$|[:=])` shape the census/gate
  uses; FAIL prints are column-0 as well. Harness launch shape per headers:
  `godot --headless --path <proj> --script res://export_div_s0N.gd -- --arm=<arm>`; scratch
  root override `$EXPORT_DIV_ROOT` (then `$EXPORT_LAUNCH_ROOT`, engine user-data,
  `$TMPDIR`, `/tmp`).
- **Final re-anchor (UTC 00:00:55)**: still moving — newest bytes s01
  `ae2f8af5e1a90fe4753742dd763ca6b8963061aecc4b12c15ad37fcb91248754` (23 601 B),
  s02 `c08792c1c208d47a8af66c669e7296eb6a1d94fe3d20872aeb73d4d6620a4898` (17 975 B),
  s03 `778613524a15c0959555cecbe263570375235cd45c4e59c8d60e1b701af6fa84` (18 014 B); all
  three `--check-only` rc **0**, 0 parse errors (same method, scratch `proj5`). [I] the
  family is being written by sibling E/S seats concurrently with this census; sha cite
  with every claim.
- Cross-reference [O]: a sibling landed `corpus/lessons/r103-simp-gaps-and-print-law.md`
  (untracked, 155 lines) whose law #2 — "a probe's per-arm `FAIL` line is informational,
  not a verdict; the round's counts come from the probe's meta record" — states the same
  principle this shard measured for the 48 zero-PASS rows (S2's rejects carry designed
  evidence, verdict is meta-carried).

## S7 — routed-item census (r101/r102 adjudicators), status at HEAD  [O]

| # | routed item (source) | status measured at HEAD |
|---|---|---|
| 1 | stale `.shokunin/game-dev-2d/corpus/` citations (r101-adjudicator:92, "SCORECARD/README/lessons") | SCORECARD **0**, README **0**, PROVINCE **0** (r102 repair holds) — but **LOG.md 44 lines** was never in the enumeration, and `corpus/lessons/` = **100 files / 732 matching lines** (r102 quoted only the 384-line old-absolute sub-family). LOG.md hits are inside historical round records (e.g. `:11-12`, `:23`, `:34` quoting the old runner invocation) → same preserve-vs-rewrite policy class as lessons; [O] counts, [I] classification as history, not live instructions. |
| 2 | r101 VER-13: `export_preset_missing` expected_errors entry is dead code | still present at HEAD (dict entry `run_battery.py:2078`); the export branch still sets `passed = classify_export(output)` inline (`:1948`). New: the shape is enumerated in the error-clause-surface gate's `allowlists_outside_expected_errors` (`:3813-3816`, verbatim `"export_preset_missing executes classify with (evidence,) inline"`). Open-but-visible; no behavior defect. |
| 3 | r101 timeout probe `hold_open_new_bound` red | r102 re-derived bound 0.75→1.25 with counterfactuals (r102 adjudicator). Not re-measured here (needs a battery run). [U] current in-battery state. |
| 4 | r101 3 legacy `joys` rows red (host-state class) | not re-measured by this seat; rule honored: no device-census token pinned anywhere in this shard. [U]. |
| 5 | r102 pre/post-span foreign-line residual (mut09 span attack) | still open; [I] the C2 receipt-shape meta-gate is its routed vehicle — S2's four-class inventory is the baseline it needs. |
| 6 | r102: "QUALITY.md note … no QUALITY.md exists in the lane repo … routed to scout-class census" | **census answer**: fleet convention is `<lane>/corpus/QUALITY.md` — present in 10 of 21 lane repos (`ls -d *-shokunin/` = 21 lanes; 7–36 lines each; e.g. `tsukuroi-shokunin/corpus/QUALITY.md` "Admission bar (probation draft)"). `game-dev-2d-shokunin` and `game-dev-3d-shokunin` lack it; no `QUALITY.md` under `templates/`; fleet root has none; this lane's `corpus/knowledge/` holds only `seed.md` + `2026-10-12-production-checklist.md`. [I] the scribe's target is most plausibly a lane-level `corpus/QUALITY.md` per sibling convention; the write decision stays operator/scribe-owned. |
| 7 | r102 mut01/mut06 script staging defects (disclosed) | r103 mut05 reproduces the class (S5, exit 1, zero artifacts). |
| 8 | stray worktrees (instructed: list, do not remove) | `git worktree list` → `/var/tmp/r103-S1/repo`, `/var/tmp/r103-S2/wt`, `/var/tmp/r103-S3`, `/var/tmp/r103-ver4/wt` all detached at `6e3e87f7`; `/var/tmp/r102-S1` detached at `1392ca21`. Lane worktrees `wt-r98/r99/r100` locked (untouched). |

Incidental [O], outside lane, no action from me: a directory literally named `bash: /`
exists in `/home/vgpnk/Projects/shokunin/` (provenance unknown).

## Handoff (blocking actions for the orchestrator)

1. **Apply w5 H1+H2 atomically with the `export_div_*` CASES rows** (S3 atomicity); freeze
   `--min-rows` to the landed row count. Gate-only or rows-only splices are red by
   construction.
2. **Do not cite "self-test cells M/P" from the landed w5 script** — cells L–R never ran
   (W5-D1) and cell L is wrong by construction (W5-D2). Use this shard's corrected rerun
   (M/N/P/P′/Q all as intended) as the substitute evidence.
3. **mut05 produces no artifacts** (S5): repair it or source W2's evasion evidence elsewhere.
4. **Fixtures churn**: s01/s02/s03 were rewritten during this seat (mtimes 20:57–21:00).
   The validated set is the S6 table (s01 `f8af56d4…`, s02 `c08792c1…`, s03 `b27a7ab4…`,
   all `--check-only` rc 0 at UTC 00:00:13–00:00:25). s03 was *unparseable* at
   `6552b658…` (three `:=` type-inference errors) before a sibling repaired it — re-run the
   parse check on whatever bytes finally land, and cite the sha with any evidence.
   Registration rows remain the only missing piece for the family; s04/s05 do not exist.
5. CASES at HEAD = 536 exactly; every CASES row appears in the r102 receipt (0 missing) —
   a re-anchor of the count after the C1 registration lands should read 536 + N_div.
6. `corpus/fixtures/export_div_s0*.gd` are untracked (`git status --short` → `??`), as is
   `reports/round-103/`; this seat created/modified only `reports/round-103/r103-scout.md`
   (no commit, no shared-file edit, no `run_battery.py` execution).
