# r91 critic — adversarial review of committed `77d2f7e` (11 `nav_lattice_*` rows, 258-row battery)

Seat `CRITIC` (g2d lane r91) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.
Reviewed commit **`77d2f7e`** (HEAD at session start; parent `13828dd`).
**No tracked write, no commit.** Seat-owned artifacts: `corpus/live/r91-critic/**` + this report.

**Worktree churn (not this seat's).** The worktree went dirty mid-session from a sibling lane
(r92 author: `corpus/fixtures/run_battery.py` `+155` insertion-only, plus untracked
`corpus/fixtures/tilemap_lattice.gd`). Every harness-derived check below is pinned to a **frozen
copy of the committed tree** extracted with `git archive 77d2f7e -- corpus/fixtures`:
`run_battery.committed-77d2f7e.py` sha256 `f5725ca4…`, `nav_lattice.committed-77d2f7e.gd` sha256
`08884339…`, `project.committed-77d2f7e.godot` sha256 `8de8b3af…` — all three byte-equal to
`git show 77d2f7e:<path>`. The seat never read the sibling's worktree edits as the reviewed bytes.

**probeParent disclosure.** Exactly one read-only `ufo-labrat` was dispatched (agent `61d38105`,
depth-2, licence now exhausted). Its substrate exposes **no shell/exec** capability, so it returned
a static read only (no writes, no descendants, repository untouched). It pre-registered H1 —
*"the `nav_lattice_avoid` pinned payload is map-synchronization-independent; the sync gate is the
only thing that rejects a stalled map for that row"* — and leaned **CONSISTENT** with one caveat
(verify the stall premise with the unmodified fixture first). This seat then executed the same
pre-registered comparison itself (§5): **CONSISTENT, measured**.

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host (same as every
prior r89/r90/r91 seat); every `file:line` below is engine-emitted `at:` text. The change under
review is one new fixture file plus an insertion-only harness block, so no symbol-aware rename was
required; hand analysis + fresh-process execution is the fallback in use.

**Load regime.** Host carried foreign `loadavg 51–118` for the whole session — three sibling
batteries (g3d, r91-scribe, r91-verifier) were running concurrently. This seat added **16 named
`r91c_hog*` spinners** for every batch (killed at end; no stray process; no `.godot/` cache
created in the seat `proj/`, no tracked file touched). Own batches record `loadavg` start/end in
`battery_run*.log` / `runs/`.

---

## 0. What I ran — 112 seat probe launches + 2 full 258-row batteries

| # | probe | receipts |
|---|---|---|
| 1 | all 11 arms ×3, 60 tps, +16 hogs (battery launch shape) | `runs/fresh.*` ×33 |
| 2 | all 11 arms ×2 under `--fixed-fps 30` (regime attack) | `runs/ff30.*` ×22 |
| 3 | all 11 arms ×2 under `--fixed-fps 120` (regime attack) | `runs/ff120.*` ×22 |
| 4 | gate short-circuited (M1) — avoid ×8 in 3 modes + sync ×2 | `runs/nogdiag_*` ×10 |
| 5 | gate short-circuited on the other 7 sync-dependent arms at ff120 | `runs/nogate_ff120.*` ×7 |
| 6 | foreign-abort forgery M2a (`assert(false)`) / M2b (`OS.crash`) | `runs/crashkill.*`, `runs/crashos.*` ×4 |
| 7 | same-RID double-free variant M2d (annotated) | `runs/dblfree*.teardown_crash.*` ×4 |
| 8 | query-order mutants M3 (final swap) / M3c (scout order in loop) | `runs/reachord.*` ×3, `runs/reachloop.*` ×3 |
| 9 | refusal-poke removal M4 (dead allowlist entry) | `runs/noorphan.bake.*` ×2 |
| 10 | invariant-threshold mutant M5 (`20.001`→`100.0`) | `runs/sumthresh.avoid.*` ×2 |
| 11 | full battery, frozen committed tree, +16 hogs (rep1, 258 rows) | `battery-runs/20261015T232521428327Z/` |
| 12 | full battery, same tree (rep2, 258 rows) | `battery-runs/20261015T233102656414Z/` |

Plus seat scripts (`scripts/static_audit.py`, `analyze.py`, `census.py`, `required_stderr_check.py`,
`author_crosscheck.py`) and a read-only cross-check of the author's untracked evidence (33 fresh
reps + both 258-row runs re-classified through the production classifier). Production classifier
segment `classify_process` sha256 `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`
— the same byte segment r89/r90 seats used.

---

## 1. Findings (ranked)

### F1 — MEDIUM-LOW · the "settled" state pins are 60-tps-conditioned; the report's "no scheduler field inside any pin" wording overstates

The fold is real for *frame counts*: no `settle=`/`iter=`/`ladder=`/`first_reach*`/`walk_steps=`/
`reached_at=`/`first_reachable=`/`iter_b=`/`link_iter=`/`gate=`/`chg_iter_*`/`dis_same=`/
`fwd_disabled_same=` token appears inside any pin (static token check over all 11 signatures,
plus runtime: every pin is an exact prefix of its printed line in 112 receipts). But several
pinned **values** are reads taken after a fixed `await _await_frames(4)` settle, and those are
mode-dependent — measured under `--fixed-fps` (seat-owned receipts, committed fixture):

| row | pinned token | ff30/ff120 observed |
|---|---|---|
| `nav_lattice_sync` | `chg_settled=true` | `chg_settled=false` (4/4 ff receipts, rc=0, **FAIL**) |
| `nav_lattice_path` | `gap20=[…(205,20),(250,20)]`, `gap20_reach=true` | bridge absent: `gap20=[…(200,20)]`, `gap20_reach=false` |
| `nav_lattice_region` | `bot_cost1=…`, `top_cost1=…`, `enter500=…`, `l1/l2/l3`, `dis_settled`, `reenabled`, `swapped`, `restored` | e.g. `bot_cost1` = top corridor (cost change not applied) |
| `nav_lattice_link` | `fwd_disabled_settled=[2 pts]`, `cost300=[4 pts]` | disable/cost not applied: 4-pt / 2-pt lines |

At the battery's 60 tps the boundary measured these settling in **≤3 frames** (56/56 lever-runs)
and this seat measured 3/3 fresh reps + 2 author reps + 2 full battery reps green — so the pins
are correct for the shipped mode with a **1-frame margin**. Under `--fixed-fps` they reject
loudly (never a false pass). The finding is evidentiary: the fold as *worded* covers frame-count
fields, not these 4-frame settle *state* reads, and the margin is thin enough that extreme 60-tps
load could turn one into a flake (a red battery with no regression). Cheap future hardening:
widen the settle await (4→6/8) in a later round, or state the 4-frame window explicitly in the
r91 block comment.

### F2 — LOW · `nav_lattice_avoid`'s pinned payload is map-sync-independent: the gate is the *only* rejection for a stalled map (labrat H1 CONFIRMED)

With `_await_sync` short-circuited (`mut/nogate_diag`, a tail field added recording the map
iteration at print time), the arm printed the **exact committed pin** in 8/8 runs across 60 tps,
ff30 and ff120 — including one rep whose own tail reads `iter_now=1 region_iter_now=0`, i.e. the
payload was emitted **off a never-synchronized map**. The committed gate (`iter>=2 AND reach`,
`SYNC_BOUND=48` → `STALE` + exit 2) is therefore the sole mechanism that rejects a stalled map for
this row. This is not a false pass of any claim the row makes (its claims are avoidance cadence
and the ORCA bound, all true on a stalled map — the boundary's own `b_avoid` runs at ff30/ff120
agree), but a reader must not read the avoid PASS line as evidence of sync, and the gate must be
treated as load-bearing for that row specifically. For every *other* sync-dependent row the pin
itself rejects stale output (7/7 FAIL at ff120 with the gate removed: empty geometry, or
`chg_settled=false`; only `agent` passed in the one rep where its own reach loop had synced).

### F3 — LOW · the avoid row's invariant tokens are self-asserted by the probe

`sum_bound_ok=true dirs_ok=true` are computed in-fixture; the battery pins the booleans, not the
measurement. `mut/sumthresh` (threshold `s > 20.001` → `s > 100.0`) prints the byte-identical
pin in 2/2 reps — the row cannot see a loosened invariant. The measured digits *are* emitted
(`sum_max=`, `seq_a/seq_b`, `vel_a/vel_b`) but sit in the unpinned tail, and they are genuinely
process-dependent (`sum_max ∈ {19.839…20.0000}` across the seat's avoid receipts), so an exact
token pin is not available; a future envelope row is the only way to pin the measurement itself.
The boundary's `≤ 20.0000` law is honoured in every receipt this seat produced: 16 avoid
receipts carry `sum_max`, **min 19.839 / max 20.0000 / zero violations**, plus the boundary's own
100 samples.

### F4 — INFO · the teardown-crash binding is class-level (glibc heap-corruption), not site-level

The row's binding is rc `-6` + stdout marker + `double free or corruption` **on stderr**
(`required_stderr`), with the signature additionally anchored to stdout. Verified two-directionally
on the real capture (`scripts/required_stderr_check.py`): fragment moved to stdout → **FAIL**;
marker moved to stderr → **FAIL**; wrong exit → FAIL; and two *real-process* forgeries —
`assert(false)` (`mut/crashkill`) and `OS.crash()` (`mut/crashos`) — both produce rc=-6 with the
marker present and are **rejected** (no glibc fragment; the foreign stderr text also trips the
unrelated-`ERROR:` clause). Attempted same-class forgery `mut/dblfree` (same RID freed twice,
annotated) still reproduced the *deferred* teardown crash (`DBLFREE_SURVIVED_INLINE` printed; the
abort lands at exit), i.e. the committed class is "deferred double-free at server teardown with a
live callback" — as the author's own comment states. Residual: a future fixture edit that crashed
at a different site with the same glibc printer would still satisfy the row; the row binds the
class, not the site.

### F5 — INFO · precision notes

- **Battery-level flake, not r91**: seat battery **rep2** (loadavg 86.7) went red on
  `audio_bus_route` (exit 2 vs 0) + `audio_bus_route_invalid_control`, cascading one dead census
  entry into `probe_error_clause_surface` — the documented volatile audio class named in the
  author's own report. All 11 nav rows PASSED in both seat batteries and both author batteries
  (4/4). The author's "zero flakes observed" is host luck, not a property of the landing; lane
  note only.
- **`warm_n_a=16 n_a=21 n_b=21`** are cadence pins (one avoidance callback per agent per frame).
  They are the one frame-count-shaped value inside a pin, but they *are* the claim (boundary §5.1:
  exactly 1 callback/agent/frame in all 37 avoid runs, incl. stalled maps), not a scheduler
  artifact; they held in every seat rep.
- **Exactly-once PASS line**: 13 print sites (11 arms + `unknown arm` fallback + `STALE`); every
  one of 112 receipts carries exactly one of them; the `STALE nav_lattice <arm>` line cannot
  satisfy any signature and exits 2 (10 STALE receipts, all rc=2). The `unknown arm` fallback is
  PASS-shaped but matches no pin (a typo'd arm fails loudly).
- **Query-order fold**: the *pin* is order-robust — the final read-order swap (M3) still prints
  `fin=true reached=true` 3/3 — while the scout order in the loop (M3c) reproduces the boundary's
  artifact exactly (`reached_at=-1`, tail only) 3/3. The fold's stated rationale ("the pin carries
  the order-independent final state only") is measured true.
- **Census gate granularity**: `r91_expected_errors_all_matched` requires ≥1 match per entry, not
  exact multiplicity; captured multiplicity is exactly 1 for both entries in 33 fresh + 2 author
  + 1 seat battery reps. Both entries are byte-equal to the captured stderr lines.
- **`census` row tokens** (`srv_methods=199 poly_methods=134`, enum arrays, defaults) are
  build-version constants — intended loud flips on an engine bump, same class as prior census pins.

---

## 2. What survived (positive verifications)

1. **Byte-stability under load.** 11/11 rows PASS ×3 (33 receipts, loadavg 54–76 + 16 hogs)
   through the production classifier; err streams unique-per-row and byte-stable; the only
   per-rep variance is token-index-confined to the declared tails (`region` idx 16 ≥ pin 15;
   `avoid` idx 15–20; `bake` idx 17–18; `link` idx 20 ≥ pin 19).
2. **Pins are exact line prefixes.** Every one of 112 receipts: `line.startswith(pin)` and no
   scheduler/race token inside the pin prefix (static + runtime).
3. **The gate works as a failure surface.** Under ff30/ff120 stalls the arms emit
   `STALE nav_lattice <arm> sync_bound_exhausted bound=48` + exit 2 (10 receipts) — no
   PASS-shaped payload off an unsynced map; the row FAILs loudly.
4. **No mis-PASS under fixed-fps.** 44 regime launches: rows either PASS with the pin intact
   (`census`, `teardown_*` always; `agent`/`avoid` at ff120; `query`/`bake` in some reps) or FAIL
   loudly (STALE or pin mismatch). Gate-removed ff120: 7/7 sync-derived rows FAIL on the pin.
5. **Crash row mode-independent.** rc=-6 + marker + glibc fragment in 3/3 fresh, 2/2 ff30, 2/2
   ff120; `teardown_clean` 0 B stderr in all conditions; forgeries rejected (§1 F4).
6. **Allowlist load-bearing.** `nav_lattice_sync`/`nav_lattice_bake` bare-reject (bare=True) and
   allowlist-pass in every receipt; captured ERROR lines byte-equal to the entries; dead-entry
   census 0; `r91_expected_errors_all_matched=True` (recomputed by seat `census.py`).
7. **Floor gate is real and wired.** `r91_expected_errors_all_matched` covers the
   `nav_lattice_` prefix, lives in `sf_discriminations`, the meta row verdict is
   `all(sf_discriminations.values())`, and the battery verdict requires all rows PASS. Mutant
   `noorphan` (refusal poke removed) drives it **False** (entry dead, 2/2 reps) — the gate catches
   a mechanism removal.
8. **Commit hygiene.** `77d2f7e`: 103 files, **0 deleted lines**; `run_battery.py` `+88/-0`;
   `nav_lattice.gd` new (882 lines); `project.godot` untouched (sha equal to committed). CASES
   251 tuples; the 11 nav rows are a contiguous block at CASES[236..246], immediately after
   `r90_lattice_lag` and ahead of the crash/descendant tail; 251 + 7 meta = 258 rows.
9. **Author cross-check (read-only).** Both author battery runs: 258 rows, verdict PASS, nav 11/11,
   r91 gate True, `teardown_crash actual_exit=-6`; all 33 author fresh-reps re-classify PASS
   through the production classifier.
10. **Seat battery runs (frozen committed tree, +16 hogs).** rep1: **258/258 PASS**, all 40
    discriminations True, `dead_entry_count=0`. rep2: nav 11/11 PASS + gate True; battery verdict
    FAIL solely on the audio volatile class (§1 F5). Both runs' nav census entries matched once.
11. **Fixture hygiene.** No file/`user://`/`DirAccess`/`ResourceSaver` use (only
    `OS.get_cmdline_user_args`); no descendants, no shared state, no locks; output byte-stable
    while three sibling batteries ran concurrently.
12. **`teardown_clean` freed-RID read stays silent** (0 B stderr ×3 fresh + 2 author + 2 battery),
    as the author disclosed; if a future build makes it loud the row fails loudly (unrelated-ERROR
    clause), not silently.

---

## 3. Questions the dispatch implies, answered

**False-positive shapes (a row that passes when it shouldn't).** None found in the committed
bytes. Six mutants attempted: gate removal (M1), refusal-poke removal (M4), invariant-threshold
loosening (M5), foreign aborts (M2a/M2b), query-order reversal (M3/M3c). The row-level blind
spots are the ones the design declares: M1 shows the avoid payload is sync-blind (F2 — the gate
is the guard), M5 shows the invariant booleans are probe-side (F3), M4 shows the refusal event is
enforced only at battery level (the census gate, verified to work), M2a/M2b are rejected.

**Scheduler/host-conditional pins the boundary missed.** The 4-frame settle-state pins (F1):
`chg_settled`, `dis_settled`, `gap20_reach`/`gap20`, the region steering/layer/swap set, and the
link disable/cost set. The boundary *measured* the underlying settle law at 60 tps (≤3 frames) and
the rows are green under load, but the row pins encode the 4-frame window, and the report's
"never inside the pin" wording should be read as frame-count fields only.

**Rows that pass only because a sibling process is alive.** None. All state is in-process; the
fixture touches no files; receipts were byte-stable while three sibling batteries ran.

**Envelope gaps.** None needed at 60 tps: 11/11 rows single-mode over 112 seat launches + 33 author
reps + 4 battery runs. Fixed-fps modes are *rejections*, not alternative modes, by construction.

**Allowlist/census correctness.** Independently recomputed: bare-reject True for both rows,
entries live (matched exactly once), `dead_entry_count=0`, gate True; `noorphan` flips the gate
False. The `at:`/backtrace lines that accompany the ERROR lines are not scanned (line-local
`"ERROR:"` clause), consistent with every prior round's allowlist shape.

**Insertion ordering / prior-row identity.** Verified: contiguous insertion at CASES[236..246],
preceded by `r90_lattice_lag`, followed by `crash_spontaneous_sigabrt` (the `sleep 8` gap to the
descendant meta probes preserved); the whole commit is deletion-free, so prior rows are
byte-unchanged by construction.

**Cross-seat consistency.** No r91 sibling report (verifier/reviewer/scribe/simplifier) had landed
at write time; the sibling lanes were observed running their own 258-row batteries concurrently.
This report's `noorphan` census result and the author's labrat caveats are the only cross-checks
available; nothing contradicts them.

---

## 4. Verdict

**PASS-WITH-RESERVATIONS on the committed bytes `77d2f7e`.** No blocking defect.

The four boundary folds are landed and measured: (1) the `iteration_id+reach` gate is encoded and
is a real failure surface (`STALE` + exit 2 under stalls; for the avoid row it is the *only*
rejection, proven); (2) every frame-count scheduler field sits in a diagnostic tail, pins are
exact line prefixes, and per-rep variance is token-confined to the tails; (3) the fin-before-
reached order is encoded and the pin is measured order-robust while the tail `reached_at` is not;
(4) the teardown-crash negative control is armed with a `required_stderr` fragment + stdout anchor
that rejects foreign aborts in both directions. The battery-level guards (allowlist load-bearing,
dead-entry census, floor gate, final `all()` verdict) are real and mutation-tested, and the commit
is insertion-only.

Reservations are robustness/evidentiary, not behavioural:
- **F1** settle-state pins carry a 1-frame margin at 60 tps and reject under fixed-fps — correct
  for the shipped mode, thin under extreme load, and the report wording overstates slightly.
- **F2** the avoid row's PASS line is sync-blind by construction; the gate is its only guard.
- **F3** the avoid invariants are probe-side booleans (digits unpinned, process-dependent).
- **F4** the crash binding is class-level (glibc double-free), not site-level.
- **F5** the battery's global verdict under load is hostage to the pre-existing audio volatile
  class (seat rep2 red on `audio_bus_route*` with all nav rows green) — a lane note.

**Blockers: none.** Nothing in this review requires a change before the landing is folded; F1's
prose/window and F3's envelope are the only cheap follow-ups worth queueing.

---

## 5. ProbeParent labrat + the pre-registered hypothesis it could not run

The single labrat licence was used (depth-2, read-only, `61d38105`). Its substrate had **no
shell/exec**: it returned **INCONCLUSIVE — static read only** (no files, no processes, repository
untouched) with a careful static analysis: every pinned avoid token is a constant, a locally
mirrored property, or an ORCA callback product; the open question was whether the avoidance tick
runs on a map whose `iteration_id` never reaches 2; its caveat was to verify the stall premise
first.

This seat executed the hypothesis unchanged:

1. **Stall premise** — the committed fixture does stall under `--fixed-fps` (`STALE … bound=48`,
   exit 2, 10 receipts; empty geometry in gate-removed runs).
2. **M1 short-circuit** (`_await_sync` returns 0, no poll) — avoid prints the exact committed pin
   in **8/8** runs (60 tps ×2, ff30 ×3, ff120 ×3), including one rep whose added diagnostic tail
   reads `iter_now=1 region_iter_now=0` → **the pinned payload is emitted off an unsynced map**.

**Result: CONSISTENT.** The labrat's static read was right, and its caveat was the correct one:
without the gate the row would PASS on a stalled map; with the gate it fails loudly.

---

## 6. Evidence index

`corpus/live/r91-critic/` — `manifest.sha256` covers all:

| artefact | path |
|---|---|
| frozen committed battery / fixture / project | `run_battery.committed-77d2f7e.py`, `nav_lattice.committed-77d2f7e.gd`, `project.committed-77d2f7e.godot` |
| committed-tree extract for the battery runs | `battery/corpus/fixtures/` |
| 112 probe receipts (out/err/rc) | `runs/` |
| full battery rep1 (258/258 PASS) | `battery-runs/20261015T232521428327Z/verdicts.json` |
| full battery rep2 (nav 11/11; audio-block FAIL) | `battery-runs/20261015T233102656414Z/verdicts.json` |
| seat analyzer / census / static audit / forgery check / author cross-check | `scripts/`, `analyze.*.json`, `census.*.json`, `static_audit.json`, `required_stderr_check.json`, `author_crosscheck.json` |
| mutants (M1–M5) | `mut/nogate/`, `mut/nogate_diag/`, `mut/crashkill/`, `mut/crashos/`, `mut/dblfree/`, `mut/reachord/`, `mut/reachloop/`, `mut/noorphan/`, `mut/sumthresh/` |
| load logs | `battery_run.log`, `battery_run2.log` |
