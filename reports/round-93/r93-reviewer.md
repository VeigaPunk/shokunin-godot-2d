# r93 reviewer — wave-B gate on the committed Anim/Tween lattice landing (`4b75151`)

Seat `REVIEWER` (g2d lane r93) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7, 32 cores.
Reviewed commit **`4b75151`** (parent `d9edb72`); at review start `HEAD ==
4b75151` and `git diff HEAD -- corpus/fixtures` was **empty**, so the committed
bytes are the live worktree bytes. `HEAD` advanced by one sibling commit
during the review (`043708ba`, the r93 critic — `corpus/live/r93-critic/**`
only); `git diff --stat 4b75151 HEAD -- corpus/fixtures` is **empty**, so the
reviewed fixture/harness bytes are still the live ones. Diff scope:
`corpus/fixtures/anim_lattice.gd` (**+689/−0**,
new), `corpus/fixtures/r93b_anim.gd` (**+466/−0**, new),
`corpus/fixtures/run_battery.py` (**+111/−0**, 23-row insert + 1 floor gate),
`reports/round-93/r93-author.md` (+248), and 235 committed author artefacts
(`corpus/live/r93-author/`: 153 fresh-rep files + `manifest.sha256` + 3 battery
logs + `proj/` fixture copy). **Zero deletion lines anywhere**
(`git show 4b75151 | grep -c '^-[^-]'` = 0).

**This seat modified no tracked file and made no commit** — `git status
--porcelain` shows zero non-`??` lines, re-checked after every execution batch.
Seat-owned untracked artefacts: `corpus/live/r93-reviewer/**` (manifest
covers every file, `manifest.sha256` excepted) and this report.

**`lsp` disclosure.** No `lsp` device and no GDScript/Python language server is
exposed to this seat (same as the r89–r93 lanes). Every check below is a
textual/AST read of the **pinned** committed bytes plus fresh-process execution
receipts — the literal fallback, recorded so it is never presented as semantic
proof. The diff contains no renames and no symbol-aware work was required
(fixture landing + literal `CASES`/gate inserts), so nothing was hand-renamed.

**probeParent disclosure (frozen, exactly one dispatch).** One read-only
`ufo-labrat` (L2, grep/read/glob only, no exec, no edits) was given a 4-clause
hypothesis: *(H1)* every r93 pin appears verbatim in every committed author
fresh-rep of its own arm and in no other arm's receipts; *(H2)* zero `r93_`
`expected_errors`/`required_stderr` entries and the gate covers the `r93_`
prefix; *(H3)* every row's `--arm=` names an implemented arm; *(H4)* all 51
author receipts are rc=0 / 0 B stderr / no `ERROR:`. It returned **H2–H4
CONFIRMED** (with per-line counts) and **H1 CONFIRMED with one cross-arm hit**:
`r93_anim_phys_delta`'s `phys_delta=0.01666666666667` also appears in the
`r93b_anim --arm=clock` receipts (which are not a battery row). I reproduced
that collision independently (§V6/F5) — benign, same finding the author's own
labrat recorded as its clause-2 refutation. The labrat executed nothing; all
execution evidence below is this seat's own.

**Concurrent-worktree disclosure.** While this review ran, other lanes
executed their own batteries on this host (a g3d r96 verifier battery among
them; no hogs of mine beyond the batteries below); `HEAD` did not move. All of
my runs were launched from the **pinned
export** (`git archive 4b75151 corpus/fixtures` →
`corpus/live/r93-reviewer/pinned/`, **all 80 committed files** — including the
r69-era tracked `__pycache__/run_battery.cpython-314.pyc` — each verified
byte-identical by `git hash-object` against its blob id in
`4b75151:corpus/fixtures`), and the harness copies *its own
directory* into scratch, so no run of mine ever read a dirty fixture.

**Verdict: PASS on the landed bytes.** All five dispatch-named folds are
implemented as claimed and *demonstrated*, not asserted: (1) runtime overshoot
is real and pinned on both sides (BACK reads `0.10286344587803` **below** the
start value 1.0, SPRING reads `10.510157585144` **above** the end value 10.0;
the static `Tween.interpolate_value` reproduces the BACK points byte-for-byte
and the SPRING/ELASTIC points to 2.4e-7, i.e. float32 property rounding — no
clamp on either path); (2) the N−1 await law is pinned at its stable instance
(`x1=0.0`) and verified exactly at `--fixed-fps 120` (`pos10 = 9/120 = 0.075`,
`x2/x3/x5` = 1/2/4 applied steps, `mixer_applied_10=10`); (3) the crossfade
law `w_i=(i−1)/(N−1)` is re-derived numerically from the pinned lattice at
**three** granularities (N=10/20/5) plus the running-source formula, and the
await-immunity control holds at the default rate and at ff120; (4) DEFERRED
method callbacks flush on the next **process** frame and on a **physics** frame,
with the two-advance queue and IMMEDIATE-in-`advance()` routes pinned; (5) the
`r93_expected_errors_all_matched` floor gate is present, covers the `r93_`
prefix, and is **armed** — a planted dead r93 entry flips it `False` and fails
the battery loudly (control §V9). All 23 r93 rows PASS in **every** run of mine
(4 full batteries — 3 on the pinned bytes + 1 control — plus 85 fresh arm
receipts and 6 ff120 receipts) and in the author's
3 committed runs; the 8 full-line pins are byte-identical across sessions and
all 23 pins appear in 100% of the 258-receipt r93-boundary corpus of their arm
(14/14 or 16/16). Findings F1–F7 are evidence-integrity / precision /
host-class items; **none changes a pinned byte or a row verdict**.

---

## 1. What was verified clean

**V1 — additive, scoped diff; prior rows untouched; provenance byte-exact.**
`git show --numstat 4b75151` for the three fixtures: `+689/−0`, `+466/−0`,
`+111/−0`; zero deletion lines in the whole commit. AST row-diff of `CASES`
from `d9edb72` (265 entries) to `4b75151` (288 entries): **pure insertion of
23 rows** after `r92_tilemap_nullts_crash` — common prefix 261, common suffix 4
(the crash/descendant tail `crash_spontaneous_sigabrt`, `crash_self_sigkill`,
`descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`),
all 288 entries 5-tuples, names unique. Result rows **295 = 288 + 7 meta**
(confirmed in all four `verdicts.json`). Committed shas match the report:
`anim_lattice.gd 6a919ae04d4e7549…` (**byte-identical to the frozen r93-scout
probe** `corpus/live/r93-scout/probes/anim_lattice.gd`),
`r93b_anim.gd 3c8dd8f10d6888e1…` (**byte-identical to the frozen r93-boundary
probe** `corpus/live/r93-boundary/probes/r93b_anim.gd`),
`run_battery.py a79bfdd6f3f468d7…`, `project.godot 8de8b3af9cc737ed…`
unchanged. The committed `corpus/live/r93-author/proj/` fixture copies are
byte-identical to the fixtures (both sha256-compared). The 15 scout gating rows
in `corpus/live/r93-scout/author-rows.py.txt` (`ROWS`) are carried into the
harness **verbatim** (15/15 tuples byte-equal); the other 8 rows come from the
boundary probe.

**V2 — classifier identity.** The `classify_process` segment extracted (AST)
from the pinned harness is byte-identical (segment sha256
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`) to the
segment r89/r90/r91/r92 recorded — the r93 diff does not touch the classifier,
so the r93 rows are judged by the same production logic as their predecessors.

**V3 — row shape, gates, allowlists.** All 23 rows: one `--arm=<name>` flag
matching an arm implemented in the named fixture (no dead arms; the 16 used
arms all have `match arm:` dispatch entries), expected exit 0, signature a
string. `expected_errors` carries **0** r93 entries and `required_stderr`
**0** r93 entries (the author's `+= 0` claims) — verified by AST over the
committed dict literals; no orphan r93 keys exist. The meta gate
`r93_expected_errors_all_matched` (harness lines 3013–3022) filters
`r["case"].startswith("r93_")` and evaluates `not e["dead_in_run"]` — same
named-by-round shape as r87–r92. Both fixtures contain **zero**
`push_error`/`printerr` calls, consistent with the ERROR:-clean claim.

**V4 — fresh independent execution (this seat).** `tools/run_arms.py` in the
battery's exact launch shape (`godot --headless --path <proj> --script
res://<script> -- --arm=<a>`, `subprocess.run`, streams captured separately),
17 arms × 5 reps, 4-way concurrent, host loadavg 80–90 with foreign battery
lanes active: **85/85 rc=0, 0 B stderr on every receipt, 23/23 rows classify
PASS ×5** with the production classifier + committed pins
(`fresh-load/`). Rep-level byte stability: **12 of the 23 rows are whole-line
byte-stable (`out_uniq=1`)**; the 11 mode rows (`frame`-derived
`await_offbyone`, `physics_tick`, `phys_delta`; `deferred_flush`;
`manual_clock_*`; `process_stable`/`process_manual`; `blend_interleaved`;
`tween_phys_manual_step`) vary only in their declared unpinned tails while
**every pin is present in every rep** (`clause_sig_uniq=1` for all 23; prefix
tails recorded per rep in `claim/prefix_mine.json`).

**V5 — cross-session and cross-condition stability.** The 8 **full-line** pins
are byte-identical across my 5 reps and the author's 3 committed reps
(`cross_session.pass_lines_identical_across_sessions = true` for all 8; 15
further rows are prefix/substring pins whose pinned substrings are present in
every receipt of both sessions, tails = the declared mode tokens). All 23 pins
appear in **100% of the r93-boundary corpus receipts of their arm** across the
7 launch conditions: 14/14 for the ten scout-cell rows the boundary re-ran
(census, tweenval, tweenval_grid ×2, animtrack, tweenchain, animseek,
animmethod, animblend ×2) and 16/16 for the other thirteen (the boundary's own
6 arms plus the scout manual/mode cells it ran in all seven batches) — 258
`.out` files scanned (`tools/boundary_pin_presence.py`,
`claim/boundary_pin_presence.txt`).

**V6 — the four encoded claims, re-derived (not merely re-read).**
- **Runtime overshoot (BACK<start, SPRING>end).** From `purity` receipts
  (5/5 reps, tokens byte-stable): `overshoot=[back025=0.10286344587803,
  back050=5.5]`, `overshoot2=[spr050=10.510157585144,spr100=10.0,
  ela025=9.11611652374268]`. The tween is `scale:y` 1.0→10.0, so
  `back025 < 1.0` (**below the start**) and `spr050 > 10.0` (**above the
  end**); `spr100 == 10.0` exactly; `ela025 < 10.0`. My own static probe
  (`claim/r93r_static.gd`, engine-computed `Tween.interpolate_value`):
  `back_io_025_1to10 = 0.10286344587803` and `back_io_050_1to10 = 5.5` are
  **byte-identical** to the runtime tokens; `spr_out_050 = 10.5101573467255`
  and `ela_out_025 = 9.11611676216125` differ by **2.38e-7** (float32 property
  rounding) — so the runtime reproduces the same curve with **no clamp**, and
  the static path also extrapolates (`lin_neg_050=-5.0`, `lin_over_150=15.0`,
  pinned as `clamp=[neg=-5.0,over=15.0]`).
- **N−1 await law.** `frame` arm: `x1=0.0` in 5/5 fresh + 3/3 author + 16/16
  boundary receipts. My opt-in `--fixed-fps 120` cell (`fresh-ff120/`, 3 reps)
  makes the law exact: `x1=0.0, x2=0.83333337306976, x3=1.66666674613953,
  x5=3.33333349227905, x10=7.50000047683716`, `pos10=0.075 = 9/120`,
  `mixer_applied_10=10` — i.e. after N awaited process frames, N−1 applied
  steps, one `mixer_applied` per frame. The pinned physics-side lattice
  (`y1=0.0,y2=0.0,y3=1.66666674613953,y6=6.66666698455811`) and
  `phys_delta=0.01666666666667` are byte-identical at ff120 (launch-invariant).
- **Crossfade `w_i=(i−1)/(N−1)` at three granularities.** Numerically
  re-derived from the `animblend` lattice in all 5 reps: `finished_010`
  (N=10) `= 100+400·min(1,(i−1)/9)`, `finished_005` (N=20) with 1/19
  increments, `finished_020` (N=5) with 1/4 increments — all values within
  1e-3 of the law (float32 print precision). Granularity scope is encoded:
  the same wall-clock t=0.6 reads 322.222229003906 / 331.578948974609 /
  300.0 for dt=0.1/0.05/0.2. The running-source lattice follows
  `w_i·500 + (1−w_i)·a(t_i)` with `a(t)=100·min(t,1)` (source holds its last
  pose past its end), and the await-immune control
  (`interleaved == finished_010`, `interleaved_eq_plain=true`,
  `hard_after_frame=500.0`) holds at the default rate and at ff120.
- **DEFERRED → process + physics flush.** From `deferred` receipts (5/5 reps
  byte-stable): `manual_def=[after_adv=[],next_proc=[7,8],second_proc=[7,8]]`
  (a manual `advance()` runs the timeline, calls queue), the **new route**
  `manual_def_phys=[after_adv=[],after_phys=[7,8]]` (a physics frame flushes),
  `two_adv=[after=[],flush=[7,8]]` (queue is per-mixer, not per-advance) and
  `immediate=[after_adv=[7,8],after_frame=[7,8]]` (IMMEDIATE lands inside
  `advance()`).
- **Manual clock + negative controls.** `manual_inv`: `paused=[a=2.5,b=2.5,
  c=5.0,d=5.0,e=10.0]`, `manual=[f=25.0,g=25.0,h=50.0,k=50.0,m=100.0]`,
  `inv=[…all true…]`, `step_exact=[…all true…]`, `unpaused_moved=true` (the
  non-vacuity control proving the frame path is live). Negative controls are
  present and stable in all reps: `deferred_adv=[]`, `disabled_track=[]`,
  `manual_frames=[0.0,0.0]`, `at_play=[7.0,…]` (play() applies no pose),
  `kill=[before=[true,false],after=[false,false]]` vs
  `node_free…after_frame=[false,true]` (lazy invalidation),
  `deltas=[tiny=0.00000001,…,neg=0.0,neg_elapsed=-0.5]` (negative delta does
  not rewind), `accum1000=1.0`.

**V7 — discrimination (forges reject).** `tools/discrimination.py` on my rep1
receipts, production classifier: **23/23 rows** accept the genuine receipt and
reject all six forgery shapes — pin dropped, pin digit/boolean flipped,
signature present on stderr only, wrong rc, foreign `ERROR:` line appended,
stdout truncated mid-pin. The `_` fallback arm of both fixtures
(`PASS … unknown arm=`) matches no pin. One **declared observation**: appending
an extra token after a pin on the same line is accepted by every row — the
production classifier is substring-anchored (pre-existing property of the whole
battery, see F4), not a defect of this landing.

**V8 — full battery on the pinned committed bytes (this seat, 4 runs).**

| run | stamp | rows | r93 | `r93_expected_errors_all_matched` | verdict |
|---|---|---|---|---|---|
| runs1 | `20261016T010025049307Z` | 295 | 23/23 PASS | **True** | FAIL — `overlap`, `transition`, `audio_bus_route_invalid_control` + `probe_error_clause_surface` knock-on (loadavg 86→90) |
| runs2 | `20261016T010517828361Z` | 295 | 23/23 PASS | **True** | FAIL — `transition`, `audio_bus_route_invalid_control` + knock-on (loadavg 87→67) |
| runs3 | `20261016T054914451887Z` | 295 | 23/23 PASS | **True** | FAIL — `audio_playback`, `audio_bus_route` only (loadavg 52→55; no dead entry, `probe_error_clause_surface` PASSes) |
| ctl | `20261016T010517876014Z` | 295 | 23/23 PASS | **False** (planted) | FAIL — `transition`, `negative_transition` + planted-entry knock-on |
| (author) runs1/runs3 | `20261016T003655…` / `20261016T004609…` | 295 | 23/23 PASS | True | **PASS** — re-read from the worktree |
| (author) runs2 | `20261016T004127…` | 295 | 23/23 PASS | True | FAIL — `crash_spontaneous_sigabrt` timeout + knock-ons |

The only failures in any run are **pre-existing rows** (all present before
`4b75151`), all load-conditioned, and each run's failing set differs:
`transition` fails with `scene transition probe: initial current_scene
identity/marker mismatch`, `overlap` with `signal occurred before physics
overlap observation`, `audio_bus_route_invalid_control` with `invalid-route
playback observation unavailable … advanced=false`, `audio_playback` /
`audio_bus_route` with `expected in-tree player playback to advance …
advanced=false`, `negative_transition` with the null-scene refusal. Where a
failed row carries an allowlist entry, its dead entry knocks on to
`probe_error_clause_surface` (`dead_entry_count=1`, the exact consequence class
r92's reviewer recorded); in runs3 the two failing rows carry no allowlist
entry, the meta row PASSes, and the battery FAIL is purely the two audio rows.
**No r93 row flaked in any run (23/23 PASS ×4 here + 23/23 in all three author
runs).**

**V9 — the floor gate is armed (control battery).** A one-line mutant of the
pinned harness (`ctl/proj/run_battery.py`, diff = exactly the planted line)
adds `"r93_tween_census": ("ERROR: ctlB planted dead r93 entry (never
matches)",)` to `expected_errors` and runs end-to-end: `r93_tween_census`
itself still PASSes (it is ERROR:-clean), but the gate reports
`r93_expected_errors_all_matched=**False**` with the planted entry listed in
`dead_entries`, `dead_entry_count=3` (2 pre-existing `negative_transition`
flakes + the planted one), and the battery verdict is FAIL. So a future r93
allowlist entry cannot die silently — the property the author claims is
demonstrated, not assumed. (Today the gate is vacuously true with 0 entries;
the only way to exercise it is a planted-entry control, which is what this is.)

**V10 — prior-row identity / no perturbation.** `tools/verdict_diff.py`
(my runs1 vs the author's green runs1): 295 common rows, **0 mine-only, 0
ref-only**; the only differences are 4 verdicts and 2 `actual_exit` values on
the three volatile rows + the meta knock-on. **All 23 r93 rows are
field-identical** (verdict, signature, expected_exit, actual_exit, script,
flags, error, required_stderr, expected_errors) to the author's green run — the
same field-identity holds for my runs3 (0 r93 field diffs vs the author's
run1, checked directly on the `verdicts.json` records). The 23-row insertion
perturbs nothing.

**V11 — evidence integrity of the author's own corpus.** The committed
`manifest.sha256` (1086 entries) verifies **1086/1086** on the live worktree,
covers all 235 tracked files except itself, and lists no missing file. See F1
for the tracked/untracked split.

---

## 2. Findings (ranked by severity)

**F1 (medium-low — evidence integrity; the commit carries only part of the
lane's evidence).** `git ls-files corpus/live/r93-author` → **235 files**, but
the manifest lists **1086** entries: 852 are **untracked** because
`corpus/live/.gitignore` excludes `runs*/` and `**/__pycache__/`. The two green
runs the commit message and the report's evidence index point at
(`runs1/20261016T003655768134Z`, `runs3/20261016T004609760557Z`) are therefore
**worktree-only**, and the manifest cannot be fully verified from a checkout. I
verified it in the live worktree (1086/1086 OK, no self-entry, no missing file),
re-read both green runs from disk (295/295, r93 23/23, gate True), and
reproduced the r93 rows independently, so no verdict changes. Same shape as the
r92 reviewer F1. Suggested action: force-add the two run trees' `verdicts.json`
in the wave fold, or scope the report's evidence index to tracked artefacts and
state the gitignore exclusion.

**F2 (low — the r93 gate is inert today; its "cannot die silently" property is
verified only by control).** With zero r93 allowlist entries, the gate is
vacuously true in every genuine run (§V8). It is genuinely load-bearing only in
the planted-entry direction, which my ctl battery demonstrates (§V9). It also
inherits the pre-existing executed-rows-only scope: a *renamed/orphan* r93 key
would produce no census entry and stay invisible (r92 reviewer F5). Effect
today: none (no r93 keys exist). Suggested: compare the allowlist key set
against `CASES` names in the meta block.

**F3 (low — precision; the N−1 law is pinned at one instance, and the row's
physics lattice is a different counting shape).** `r93_anim_await_offbyone`
pins the prefix `idle=[x1=0.0`, i.e. only the first-await instance; the general
law (`pos10 = (N−1)·delta`) is a mode at ambient fps and is deliberately
unpinned — declared in the report and the harness comment (lines 712–715), and
I verified the general law exactly at ff120 (§V6). **Mechanism correction
(independent, agrees with the sibling r93 critic's F1):** the harness comment
line 713–714 says the first awaited frame "still reads the pre-play value" —
that is wrong as a mechanism. My own probe (`claim/r93r_preplay.gd`, node
placed at `x=5.0` pre-play, animation t=0 pose 0.0) reads `pre=5.0,
at_play=5.0, after1=0.0` (the later reads are frame-rate modes): the first
awaited frame applies the **animation's t=0 pose**, not the node's pre-play
value. The pin is unaffected (this fixture's node starts at 0.0 and the t=0
pose is 0.0, so both readings emit `x1=0.0`), but the comment prose is a
precision defect of the same class as the r91 comment-formula item. Suggested
one-line comment fix.
Note the *physics-side* lattice in the same arm reads N−2 applied ticks at the
pinned points (`y1=0,y2=0,y3=1,y6=4` ticks) — the pin is a launch-invariant
observation, not an instance of the N−1 law; the harness comment calls it the
"physics-side tick lattice", which is accurate.

**F4 (info — pins are substring-anchored; a token appended after a pin is
accepted).** All 23 rows accept an extra `EXTRA_TAIL=1` token appended to the
same PASS line (§V7). This is the production classifier's semantics
(`signature in output`), pre-existing across every round, and the tails are
deliberately unpinned mode tokens — but it means the pins are *prefix/clause*
assertions, not exact-line assertions. A future harness change that inserts a
token *inside* a pinned prefix fails loudly; one appended after it does not.

**F5 (info — cross-arm substring collisions; independently reproduced).**
`phys_delta=0.01666666666667` (row `r93_anim_phys_delta`, `--arm=frame`) also
appears in the `clock`-arm receipts; `finished_010=[100.0,144.444442749023…`
(inside `r93_anim_blend_interleaved`, `--arm=blend`) also appears in the
`animblend`-arm line. Both are harmless: the `clock` arm is not a battery row,
and `animblend`/`blend` are different scripts, so each pin can only ever be
observed inside its own row's launch (and the shared lattice is the same
measured law on two probes). Matches the author's labrat clause-2 refutation.

**F6 (info — the author report's last paragraph is pre-fold).**
`reports/round-93/r93-author.md` ends with "No commit. Worktree: `M
corpus/fixtures/run_battery.py` …" — true when written, superseded by the fold
commit `4b75151` (whose bytes I verified identical to the worktree). No action;
recorded so the paragraph is not read as a current statement. Same class as the
r92 reviewer F6.

**F7 (low — host class, not the landing; recorded so my run verdicts are not
misattributed).** Across my four full runs (loadavg 52–90, foreign lanes
active, no hogs of mine) the only failing rows are pre-existing ones, and the
failing set differs per run: `transition` (runs1/runs2/ctl — scene-readiness
race), `audio_bus_route_invalid_control` (runs1/runs2 — playback-advance
observation unavailable), `overlap` (runs1 — physics-overlap race),
`negative_transition` (ctl), `audio_playback` + `audio_bus_route` (runs3 —
`advanced=false` under load). Where the failed row carries an allowlist entry,
its dead entry knocks on to `probe_error_clause_surface`
(`census_bare_classifier_consistent=False`), which is what turns the battery
verdict FAIL in those runs. The author's two green runs were taken at
loadavg ≈50; mine at 52–90. **All 23 r93 rows PASS in every run** — the r93
landing is not implicated, and no green 295/295 run of my own was reproducible
in this window (the author's green runs1/runs3 are re-read and re-verified
row-by-row, §V10).

---

## 3. Residual risks

- **Build/host tokens**: the census row's enum orders, signal lists,
  `an_m_count=177`/`tw_m_count=94`/`ap_m_count=293` method counts,
  `ap_defaults`/`anim_defaults` and the float-precision literals are
  version tokens that flip loudly on an engine bump (intended, same class as
  the existing census pins).
- **Project-conditioned pins**: `phys_delta=0.01666666666667` and the physics
  lattice are 60-tps project values (a project change correctly fails the row;
  declared in the report and harness comment).
- **`--fixed-fps` cells remain opt-in**: the battery never passes
  `--fixed-fps`; my ff120 receipts (`fresh-ff120/`) are the only fixed-rate
  evidence in this seat's corpus, alongside the boundary's 34 runs per rate
  (f30/f60/f120/f120l).
- **Prefix-anchored pins (F4)** and the 15 rows' mode tails
  (`pos10`, `proc_delta`, `tween5`, `quick`, `idle_lag`, `unpaused=[…]`,
  `proc_frames_during_6phys`, `idle=[x2…]`, `phys` counters) — deliberately
  unpinned; a token added inside a pinned prefix fails, one appended after it
  does not.
- **Pre-existing volatile rows (F7)**: `transition`, `overlap`,
  `audio_bus_route_invalid_control`, `audio_playback`, `audio_bus_route`,
  `negative_transition`, `crash_spontaneous_sigabrt` (the author's interim
  run 2) are load-conditioned and can mask a green 295/295 (my failing set
  differed in each of the four runs); they are unrelated to the r93 block and
  their knock-on is documented.
- **The r93b `clock` arm is a pure launch fingerprint** (not a battery row);
  `--arm=clock` is intentionally un-authored.

---

## 4. Evidence index

All seat artefacts under `corpus/live/r93-reviewer/`; `manifest.sha256`
covers every file except itself (hash-verified after writing).

| artefact | path | notes |
|---|---|---|
| pinned committed fixtures/harness | `pinned/` | all 80 committed `corpus/fixtures` files, blob-verified against `4b75151` |
| full battery runs (this seat) | `runs1/20261016T010025049307Z`, `runs2/20261016T010517828361Z`, `runs3/20261016T054914451887Z` | `verdicts.json`, scratch; driver logs `battery{1,2,3}.log` + `battery3.driver.log` |
| floor-gate control (planted dead r93 entry) | `ctl/proj/run_battery.py`, `ctl/runs/20261016T010517876014Z`, `ctl/battery.log` | one-line mutant; gate False, battery FAIL |
| fresh arm receipts (17 arms × 5 reps) | `fresh-load/` + `fresh-load.log` | battery launch shape, all rc=0, 0 B stderr |
| ff120 opt-in cells (frame, blend × 3) | `fresh-ff120/` + `fresh-ff120.log` | exact N−1 law at 1/120 s |
| static-vs-runtime claim probe | `claim/r93r_static.gd`, `claim/static2.out` | engine-computed `Tween.interpolate_value` |
| N−1 mechanism probe | `claim/r93r_preplay.gd`, `claim/preplay.out` | pre-play 5.0 → first-await read 0.0 (t=0 pose, not pre-play value) |
| claim verification (production classifier) | `claim/claim_checks.{json,txt}` | C1–C6 + cross-session + static |
| prefix/tail audits | `claim/prefix_mine.json`, `claim/prefix_author.json` | all 23 rows, per rep |
| discrimination matrix | `claim/discrimination.json`, `claim/discrimination_author.json` | 23 rows × 7 cells, on my receipts and on the author's committed receipts |
| verdict identity vs author green run | `claim/verdict_diff_run1_vs_author1.json` | 295 common rows, r93 field-identical |
| tools | `tools/{ufo_r93.py,static_audit.py,run_arms.py,prefix_audit.py,claim_checks.py,discrimination.py,verdict_diff.py,boundary_pin_presence.py,battery_runs.sh,ctl_run.sh,make_manifest.py}` | classifier extracted AST-verbatim from the pinned harness |

Reproduction commands (from the repo root, all read-only):

```
python3 corpus/live/r93-reviewer/tools/static_audit.py
python3 corpus/live/r93-reviewer/tools/run_arms.py --proj corpus/live/r93-reviewer/fresh-proj \
    --out corpus/live/r93-reviewer/fresh-load --reps 5 --par 4
python3 corpus/live/r93-reviewer/tools/claim_checks.py --mine corpus/live/r93-reviewer/fresh-load \
    --reps 5 --author corpus/live/r93-author/fresh-reps --json corpus/live/r93-reviewer/claim/claim_checks.json
python3 corpus/live/r93-reviewer/tools/discrimination.py --dir corpus/live/r93-reviewer/fresh-load
python3 corpus/live/r93-reviewer/pinned/run_battery.py --runs corpus/live/r93-reviewer/runsN
bash corpus/live/r93-reviewer/tools/ctl_run.sh
```

**Bottom line.** The r93 landing is implemented as dispatched: additive,
byte-copy provenance, production classifier unchanged, the four named laws
pinned at their boundary-surviving instances and demonstrated by fresh
execution (85 + 6 receipts, 4 full batteries — 3 pinned + 1 control —,
258-receipt cross-condition pin scan), forges rejected 23/23 × 6 shapes, and
the round's floor gate armed and shown to fail loudly on a planted dead entry.
No pinned byte or row verdict is changed by any finding.
