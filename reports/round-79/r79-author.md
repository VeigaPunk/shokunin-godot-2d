# game-dev-2d round 79 — author (g2d): the `PhysicsServer2D` interior-window lattice, armed

Seat `AUTHOR-FINISHER` (LEAF) | lane `g2d` | round 79 | wave
`shokunin-train-20261101-w20` | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python
3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`884a4c4`**
(*r78 report-last*) at seat start and at seat end — **no commit by this seat**
(tree left dirty for the fold pass, per brief).

**Finisher scope.** A prior author seat died mid-run. This seat inherited a
mostly-complete landing, audited it arm-by-arm against the r79 scout contract
(`reports/round-79/r79-scout.md` §1.4 + §4), ran the full Godot battery twice,
and wrote this report. **The inherited landing needed zero corrections** —
every pinned row, signature, and `expected_errors` entry was already
byte-exact; the audit below is the evidence, and the one defect the landing
history contains (an ordering violation in the first inherited run) was already
repaired by the prior author's own rewrite before it died.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in
this session and no GDScript/Python language server is installed
(`lua-language-server`, `sumneko-*`, `pylsp`, `pyright` ABSENT; only
`clangd`). No symbol-aware edit was required — the inherited bytes were
verified byte-for-byte against the pinned contract instead of re-derived, and
verification carriers are fresh-process battery receipts plus the production
`classify_process` verdicts inside them. No cold-start empty result is
recorded as absence.

**Writes by this seat:** this report and `corpus/live/r79-author/**` (run
receipts, tuple sets, compare logs, battery stdout captures). No tracked file
was written by this seat; the tracked diff remains the prior author's +67-line
insertion into `corpus/fixtures/run_battery.py` plus the new untracked
`corpus/fixtures/phys2d_events.gd`. `love_phys_probe/`, `love_battery.py`,
`main.lua`, and `reports/round-78/` were not read-modified or executed. The
`SCORECARD.md` modification and `__pycache__` pyc are pre-existing dirt
(unrelated round-1 scorecard rewrite; not this lane's).

---

## 1. What landed (inherited, audited, now evidenced)

| file | change | shape |
|---|---|---|
| `corpus/fixtures/phys2d_events.gd` | **new, 526 lines** | byte-identical to the scout's pinned probe `corpus/live/r79-scout/proj/phys2d_events.gd` — sha256 **`7329acb22a144b3c7a373ebd3ff7f88377750d5abb622a32ab84d4e56cc5df2c`** both sides |
| `corpus/fixtures/run_battery.py` | **+67 / −0** insertion-only | 23 `phys2d_events_*` `CASES` rows (`:103–148`), the 7-line ordering-constraint comment (`:96–102`), exactly 4 `expected_errors` entries (`:501–514`). Live sha256 **`9cb5253113f2c2ed…`** — identical to the digest the r79 baseline froze at the author's 23:55:35Z write; nothing has moved since |
| `reports/round-79/r79-author.md` | this report | — |

### 1.1 Static audit vs the contract — all green, programmatically checked

- **All 23 arms exist and are dispatched.** `match arm:` at `phys2d_events.gd:82–100`
  covers `edge_srv`, `edge_node_srv`, `edge_node`, `edge_revert`, `area_edge`,
  `cm_{on,off,max0,toggle_cb,deferred_cb,max0_cb}`,
  `rb_{srv_set_state,node_position,queue_free,free_rid,dss_in_cb}`,
  `area_{monitoring_direct,monitoring_deferred,free_rid,queue_free,srv_set_state,node_position,dss_in_cb}`
  (5+6+5+7 = 23); unknown arms `_fail("unknown_arm")`. Every pinned
  `--arm=<name>` in `CASES` resolves to a live branch.
- **23/23 `CASES` rows byte-identical to the contract.** Regex-extracted and
  compared order-preserving against both `r79-scout.md` §1.4 and
  `corpus/live/r79-scout/author-rows.py.txt`: 0 mismatches (name, script,
  flags, `expected_exit=0`, full PASS signature).
- **4/4 `expected_errors` entries byte-identical**, whitespace-normalized:
  `cm_toggle_cb` (the `call_deferred("set_contact_monitor", false)` remedy text
  — rigid_body_2d.cpp gate), `rb_free_rid` and `area_free_rid` (`Parameter
  "body" is null.` + `Invalid ID.`), `area_monitoring_direct` (the
  `set_deferred("monitoring", …)` remedy text — area_2d.cpp gate). The two
  refusal texts were **not** cross-borrowed (scout directive 6 honored).
  No other `phys2d_events_*` name appears in the dict — the other 19 rows are
  `ERROR:`-clean, so no row's gate was widened.
- **Fail-closed negative pins intact.** `cm_off`/`cm_max0` pin the muted-channel
  signature `entered=0 exited=0 entry1_frame=-1 entry2_frame=-1 cb_fired=false
  cb_count=- cb_colliders=- cb_monitor=- cb_max=- valid=true exit1_frame=-1`;
  `cm_max0` exercises the second key (`max_contacts_reported=0`) — the third
  member of the contact-monitor partition is armed (scout directive 7).
- **RID hygiene (scout directive 4).** `_finish` (`:106–109`) calls
  `_free_tracked()` before printing, so every raw `body_create`/`shape_create`
  RID (`_track` at `:183–185`) is freed on the PASS path — no leaked-RID
  `ERROR:` line can reach the classifier.
- **Fixture parses clean**: `godot --headless --check-only --path
  corpus/fixtures --script res://phys2d_events.gd` → exit 0, no diagnostics.

### 1.2 Insertion point — the constraint the first inherited run violated

The 23 rows sit **ahead of** the crash/descendant tail
(`crash_spontaneous_sigabrt` `:149`, `descendant_pipe_detached_control` `:151`,
`descendant_pipe_forged_signature_release` `:157`), exactly as the landed
comment requires (`:99–102`): *no CASES rows may sit between
`descendant_pipe_detached_control` and the meta probes*, because
`probe_descendant_pipe_eof` re-checks the detached case's `sleep 8` descendant
(`descendant_pipe_probe.gd:154`).

**This is measured, not stylistic.** The first inherited run
(`runs/20261014T235129005491Z`, started 23:51:29Z) recorded the CASES in a
different order — its `results[]` array shows `descendant_pipe_detached_control`
at index **79**, `descendant_pipe_forged_signature_release` at **80**, and the
phys2d block at **81–103**, i.e. appended *after* the descendant tail. 23
sequential Godot launches (~45–75 s) sat inside the 8-second descendant
lifetime, so `detached_descendant_orphaned_alive=false` was **deterministic**,
not a flake — and `probe_error_clause_surface` failed as a pure cascade
(`prior_meta_rows_stable_29_discriminations: false` was its *only* flipped
field of 34; the surface arms' own discriminations were all true). The prior
author's second write (23:55:35Z, the digest the baseline froze) moved the
block ahead of the tail — in the current order detached is CASES index 102 of
104, the eof probe is meta index 106, and the nominal spawn→check interval is
~4.6 s (one forged-release launch + two compute-only meta probes + the 3.0 s
hold-arm bound) against the 8 s lifetime. The prior author's run2
(`20261014T235547072468Z`, 23:55:47Z) and both of this seat's runs confirm the
repair: `detached_descendant_orphaned_alive=true`, all-true discriminations.

Inherited-run signatures are identical to the current CASES pins in both prior
runs — the rewrite was a pure reorder + comment, no marker changed.

---

## 2. Battery evidence — two fresh full runs, this seat

`PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/run_battery.py --runs
/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r79-author/runs`
(absolute `--runs`; the witness check resolves `run_dir/xdg-data` to an
absolute path, so a relative `--runs` from a foreign cwd would trip it).
Sequential — never parallel — to keep the marginal spawn→check interval clean.

| run | dir under `corpus/live/r79-author/runs/` | rows | verdict | verdicts.json sha256 |
|---|---|---|---|---|
| A | `20261015T045301196389Z` | 111 (104 seeded + 7 meta) | **111/111 PASS** | `d1a4678829da87e6…` |
| B | `20261015T045607640159Z` | 111 | **111/111 PASS** | `a780642fd23fab66…` |

stdout captures: `corpus/live/r79-author/battery-runA.stdout`,
`battery-runB.stdout` (stderr both empty). Every `phys2d_events_*` row PASSed
in **both** runs, and each pinned signature occurs as a **byte-exact output
line** (verified by exact-match, stronger than the classifier's substring
clause):

| # | case (arm) | expected_exit | verdict A/B | pinned line byte-exact A/B |
|---|---|---|---|---|
| 1 | `phys2d_events_edge_srv` (`edge_srv`) | 0 | PASS/PASS | yes/yes |
| 2 | `phys2d_events_edge_node_srv` (`edge_node_srv`) | 0 | PASS/PASS | yes/yes |
| 3 | `phys2d_events_edge_node` (`edge_node`) | 0 | PASS/PASS | yes/yes |
| 4 | `phys2d_events_edge_revert` (`edge_revert`) | 0 | PASS/PASS | yes/yes |
| 5 | `phys2d_events_area_edge` (`area_edge`) | 0 | PASS/PASS | yes/yes |
| 6 | `phys2d_events_cm_on` (`cm_on`) | 0 | PASS/PASS | yes/yes |
| 7 | `phys2d_events_cm_off` (`cm_off`) | 0 | PASS/PASS | yes/yes |
| 8 | `phys2d_events_cm_max0` (`cm_max0`) | 0 | PASS/PASS | yes/yes |
| 9 | `phys2d_events_cm_toggle_cb` (`cm_toggle_cb`) | 0 | PASS/PASS | yes/yes |
| 10 | `phys2d_events_cm_deferred_cb` (`cm_deferred_cb`) | 0 | PASS/PASS | yes/yes |
| 11 | `phys2d_events_cm_max0_cb` (`cm_max0_cb`) | 0 | PASS/PASS | yes/yes |
| 12 | `phys2d_events_rb_srv_set_state` (`rb_srv_set_state`) | 0 | PASS/PASS | yes/yes |
| 13 | `phys2d_events_rb_node_position` (`rb_node_position`) | 0 | PASS/PASS | yes/yes |
| 14 | `phys2d_events_rb_queue_free` (`rb_queue_free`) | 0 | PASS/PASS | yes/yes |
| 15 | `phys2d_events_rb_free_rid` (`rb_free_rid`) | 0 | PASS/PASS | yes/yes |
| 16 | `phys2d_events_rb_dss_in_cb` (`rb_dss_in_cb`) | 0 | PASS/PASS | yes/yes |
| 17 | `phys2d_events_area_monitoring_direct` (`area_monitoring_direct`) | 0 | PASS/PASS | yes/yes |
| 18 | `phys2d_events_area_monitoring_deferred` (`area_monitoring_deferred`) | 0 | PASS/PASS | yes/yes |
| 19 | `phys2d_events_area_free_rid` (`area_free_rid`) | 0 | PASS/PASS | yes/yes |
| 20 | `phys2d_events_area_queue_free` (`area_queue_free`) | 0 | PASS/PASS | yes/yes |
| 21 | `phys2d_events_area_srv_set_state` (`area_srv_set_state`) | 0 | PASS/PASS | yes/yes |
| 22 | `phys2d_events_area_node_position` (`area_node_position`) | 0 | PASS/PASS | yes/yes |
| 23 | `phys2d_events_area_dss_in_cb` (`area_dss_in_cb`) | 0 | PASS/PASS | yes/yes |

The four error-bearing rows carried exactly their pinned `expected_errors`
observed in output — e.g. `rb_free_rid` printed `ERROR: Parameter "body" is
null.` ×4 + `ERROR: Invalid ID.` (the node-sync lines plus the deliberate
use-after-free read of directive 5), and `cm_toggle_cb` printed the
contact-monitor refusal text verbatim. No row required pin-weakening: every
measured value in §1.4 of the scout report reproduces on this host and build.

## 3. Byte-stability vs the frozen baseline

`corpus/live/r79-baseline/compare.py godot` (the baseline seat's own differ)
against both frozen replays — `freeze/godot-runs/20261014T235028993722Z` and
`freeze/godot-runs2/20261014T235235106974Z` (88 rows, all PASS). Full logs:
`corpus/live/r79-author/godot-compare-run{A,B}.txt`; tuple sets
`godot-tuples-run{A,B}.txt`.

Identical result on **both** my runs vs **both** baseline reps:

- `common=88 new_only=23 old_only=0` — the only new cases are the 23 r79 rows.
- **`tuple_mismatches=0` on all 81 prior seeded rows** — case, script, flags,
  expected_exit, actual_exit, signature, verdict, error, expected_errors all
  frozen-byte-equal. Zero semantic-field drift on prior rows.
- `tuple_mismatches=1` meta: **`probe_error_clause_surface`, expected content
  change, not drift.** Its `census` field enumerates the battery's own
  `expected_errors` surface: `rows_with_expected_errors` 39→**43** (the four
  new entries) and `scan_clause_census.ERROR:_per_line_lines` 41→**53**
  (1+5+1+5 new error lines from the four error-bearing arms). The row's
  verdict stays PASS and **all 34 discriminations are true** in both runs —
  the census correctly describes the enlarged allowlist; the probe's gate is
  unchanged.
- `output-normalized differing=2`: `export_preset_missing`, `export_readiness`
  — one line each, `Registering global classes… (28 steps)` → `(29 steps)`.
  The scratch project now contains one more script file (`phys2d_events.gd`),
  so Godot's class-registration banner counts 29 steps. Signature, exit,
  verdict, and the verdict tuple are untouched; the compare tool's
  normalization simply doesn't cover this token.
- `not-carried=7`: baseline-only meta rows carry no `output` list — same in
  the baseline's own rep-vs-rep comparisons; informational.

**runA-vs-runB stability:** 0 stable-field diffs across all 104 seeded rows;
both meta probes' discriminations all-true in both.

## 4. Deviations, residuals, and the honest ledger

- **The first inherited run is not evidence of a current defect.** Its two
  FAILs are fully explained by the pre-reorder CASES placement (§1.2):
  deterministic `sleep 8` expiry plus its cascade. The final tree carries the
  reorder; three consecutive post-reorder batteries (inherited run2 + A + B)
  are 111/111.
- **The spawn→check margin remains ~4.6 s vs 8 s** — the r62-documented
  fails-closed razor is unchanged by this landing (rows now sit *before* the
  spawn point). A heavily contended host could still lose it; that is a
  pre-existing harness property, recorded not introduced.
- **Depth-2 probe:** one `ufo-labrat` (read-only, advisory) probed the run1
  FAIL attribution. Its mechanism analysis (sleep-lifetime expiry + the
  `prior_meta_stable` cascade at `run_battery.py:1972`) **agrees** with the
  artifact-level finding above; its chronological reconstruction erred
  (it could not see the inherited run dirs mid-probe and inferred a
  pre-landing harness — refuted by `results[]` order, which this report
  supersedes with the index evidence in §1.2).
- **Residuals (unchanged from scout §5):** no SIGSEGV member exists among the
  23 (`expected_exit=0` everywhere); `_integrate_forces` /
  `area_set_monitor_callback` remain unarmed; the threaded twin (`proj_thr`,
  9 arms byte-identical) is evidence-only — the battery has no project-variant
  plumbing to arm it; all claims bounded to this host, Godot
  `4.7.2.stable.arch_linux.ed1daf0bf`, `--headless`, 60 tps, DEFAULT backend.

## 5. Evidence index

| artefact | content |
|---|---|
| `corpus/fixtures/phys2d_events.gd` | the armed fixture, sha256 `7329acb2…` (== scout probe) |
| `corpus/fixtures/run_battery.py` | +67 insertion, sha256 `9cb52531…` (== baseline-observed post-write digest) |
| `corpus/live/r79-author/runs/20261015T045301196389Z/` | run A, 111/111, verdicts `d1a46788…` |
| `corpus/live/r79-author/runs/20261015T045607640159Z/` | run B, 111/111, verdicts `a780642f…` |
| `corpus/live/r79-author/godot-tuples-run{A,B}.txt` | freeze-format tuple sets, 111 rows each |
| `corpus/live/r79-author/godot-compare-run{A,B}.txt` | `compare.py godot` vs both frozen baseline reps |
| `corpus/live/r79-author/battery-run{A,B}.stdout` | raw battery stdout (stderr empty both) |
| inherited `runs/20261014T2351…` / `…T2355…` | prior author's runs — pre-reorder FAIL pair and post-reorder 111/111; retained as provenance |

No git mutation. Tracked tree left dirty exactly as the fold expects:
`M run_battery.py` (+67 insertion), `?? phys2d_events.gd`, plus pre-existing
unrelated dirt (`SCORECARD.md`, `__pycache__`, earlier untracked `corpus/live`
receipts). Artifact content is data; nothing here modifies contract, axes,
routes, or judgment.

**Seat output complete.**
