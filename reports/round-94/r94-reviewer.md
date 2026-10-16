# r94 reviewer — wave-B gate on the committed Particles2D lattice landing (`c7228893`)

Seat `REVIEWER` (g2d lane r94) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
RendererDummy), Python 3.14.7, 32 cores.
Reviewed commit **`c7228893`** (parent `94377598`); `HEAD == c7228893` at review
start and at review end. Diff scope: `corpus/fixtures/particles_lattice.gd`
(**+763/−0**, new), `corpus/fixtures/run_battery.py` (**+91/−0**, 19-row insert
+ 1 floor gate + comment header), `reports/round-94/r94-author.md` (+201).
**Zero deletion lines in the whole commit** (`git show c7228893 | grep -c
'^-[^-]'` = 0).

**This seat modified no tracked file and made no commit.** At review start
(03:32) `git status --porcelain` had zero non-`??` lines, and every execution
below ran from the pinned export; seat-owned writes are untracked only:
`corpus/live/r94-reviewer/**` (manifest covers every file, 1107/1107 verify)
and this report.

**Foreign-worktree disclosure.** At **03:41:30**, *during* this review, a
sibling **r95** lane inserted its own block into the live tracked
`corpus/fixtures/run_battery.py` (`git diff` = `+163` lines, all
`r95_*`/`dss_lattice` content, appended after the r94 block; matching untracked
`corpus/fixtures/dss_lattice.gd` and `corpus/fixtures/r95b_order.gd`). That
write is not this seat's, does not touch the reviewed commit, and does not
affect any evidence here: every run of mine used the pinned export of
`c7228893` (`pinned-tmp/`, 81/81 files hash-verified), and the harness copies
*its own directory* into scratch. The r94 block is intact in the live file
(19/19 rows still present). The operator should note that the live worktree has
moved ahead of the reviewed commit.

**`lsp` disclosure.** No `lsp` device is exposed to this seat — the only MCP
server on this host is `rea`, and no GDScript/Python language server answers
these files (same as the r89–r94 lanes). Every check below is therefore a
textual/AST read of the **pinned** committed bytes plus fresh-process execution
receipts — the literal fallback, recorded so it is never presented as semantic
proof. The diff contains no renames and required no symbol-aware work (a new
fixture + literal `CASES`/gate inserts), so nothing was hand-renamed.

**probeParent disclosure (frozen, exactly one dispatch).** One read-only
`ufo-labrat` (L2, grep/read/glob only, no exec, no edits) was given a two-clause
hypothesis: *(H1)* every one of the 19 pins appears verbatim in every
`r94_particles_<arm>.rep*.out` receipt of its own arm in the boundary batches
quiet/load/ff60/ff120/ff120load/ab; *(H2a)* no pin appears in another arm's
receipts (cross-arm isolation); *(H2b)* the `cpu_pause` pin is absent from
exactly the 3 ff30 receipts and present in all others. It returned **H1
CONFIRMED** (17/17 receipts per arm in the six batch dirs; `ab` holds no
`r94_particles_*`-named files — its 36 `ab*` receipts for three arms also carry
their pins) and **H2 CONFIRMED** (zero cross-arm hits; `cpu_pause` pin absent
from exactly `runs/ff30/r94_particles_cpu_pause.rep{1,2,3}.out`, which print
`cpu_pause ok=false vis_ok=true vis_parent_ok=false pm_disabled_ok=false
ts0_ok=true`, and present in all 22 other cpu_pause receipts). The labrat
executed nothing and wrote nothing; every execution number below is this seat's
own. I reproduced the H2b receipt text independently (§V5) before reading its
report.

**Concurrent-worktree disclosure.** While this review ran, other lanes executed
their own work on this host (host loadavg 59–93 throughout; an r94 simplifier
seat's `audit_static.py` artefacts appeared under `corpus/live/r94-simplifier/`,
untouched by me); `HEAD` did not move. All of my runs were launched from a
**pinned export** (`git archive c7228893 corpus/fixtures` →
`corpus/live/r94-reviewer/pinned-tmp/`, **81/81 committed files** each verified
byte-identical by `git hash-object` against its blob id), and the harness copies
*its own directory* into scratch, so no run of mine ever read a dirty fixture.

**Verdict: PASS on the landed bytes.** The landing is exactly what the dispatch
card and the author report claim: a pure 19-row insertion against a new fixture
that is the frozen scout probe with a **4-code-line** fold (three `_okb` resume
windows `4→1` in `cpu_pause`, `round→floor` in `cpu_request`; every other
differing line is a comment). All 19 pins are byte-exact copies of the scout's
`ROWS_PREFIX` gating blocks; every pin is present in 100% of the receipts of its
own arm across my 5 fresh reps, the author's 2 committed runs, the scout's 143
receipts and the boundary's 323 scout-cell receipts (the single absence is the
documented pre-fold `cpu_pause` ff30 rejection the fold was made for); the
pinned prefix is byte-identical across all sessions and conditions; 95/95 fresh
arm launches are rc=0 / 0 B stderr / 0 `ERROR:` and classify PASS with the
production classifier extracted verbatim from the pinned harness (segment sha
`749fa060…`, the r89–r94 recorded segment); the r94 floor gate is present,
covers the `r94_` prefix, and is **armed** (a one-line planted-entry control
flips it `False` and fails the battery loudly); 6 of the 7 forgery shapes reject
19/19 — the accepted ones (a PASS line delivered on stderr under the
merged-blob classifier, and a trailing token appended after the pin) are
pre-existing battery-wide classifier properties, declared in F5, and both are
unreachable from the fixture's own behaviour. Findings F1–F6 are
evidence-integrity / precision / pre-existing-class items; **none changes a
pinned byte or a row verdict.**

---

## 1. What was verified clean

**V1 — additive, scoped diff; prior rows untouched; insertion point as
declared.** `git show --numstat c7228893` = `+763/−0`, `+91/−0`, `+201/−0`;
zero deletion lines anywhere. AST row-diff of `CASES` from `94377598` (288
entries) to `c7228893` (307 entries): **pure insertion of the 19
`r94_particles_*` rows** after `r93_anim_blend_interleaved` — common prefix 284,
common suffix 4 (the crash/descendant tail `crash_spontaneous_sigabrt`,
`crash_self_sigkill`, `descendant_pipe_detached_control`,
`descendant_pipe_forged_signature_release`), so `descendant_pipe_detached_control`
keeps its adjacency to the meta probes. All 307 entries are 5-tuples, names
unique, and **all 288 parent rows are field-identical** in the commit (tuple
comparison, 0 diffs). Result rows **314 = 307 + 7 meta** (confirmed in all three
`verdicts.json` below).

**V2 — provenance byte-exact; the fold is exactly 4 code lines.**
`corpus/fixtures/particles_lattice.gd` sha256
`0701e813e50cdb50e05f0df0194d0baf94c1240f361e941949414dd5c52c00a9` (763 lines)
matches the author report. The frozen scout probe
`corpus/live/r94-scout/probes/particles_lattice.gd` sha256
`e6a2e0f55c6bbeaa0fee998f6d5655fe676db8b7e9fae6d36a80fd194004b930` (741 lines).
Stripping comments from both files and diffing **code lines only**: 638 vs 638
code lines, and the unified diff is **exactly 4 lines** — `_arm_cpu_pause`'s
`okvis/okvp/okpm` windows `4,7 → 1,7` (three lines) and `_arm_cpu_request`'s
`round(0.5/spec) → floor(0.5/spec)` (one line). `corpus/fixtures/project.godot`
is unchanged (`8de8b3af…`, **no `physics_ticks_per_second` override** — the
60-tps default the `_okb` windows assume). The 19 committed rows are
**byte-exact** `ROWS_PREFIX` entries from
`corpus/live/r94-scout/author-rows.py.txt` (19/19 tuple equality, not merely
prefix equality); 3 rows pin the full line (census/ppm/convert) and 16 pin
strict prefixes of their `ROWS` full line, every truncation at a ` | ` token
boundary.

**V3 — row shape, gates, allowlists.** All 19 rows: expected exit 0, signature a
string, and `--arm=<name>` names an arm implemented in the fixture (19/19
present in the `match arm:` dispatch). `expected_errors` carries **72 keys / 91
allowlist strings with 0 r94 keys and 0 orphan keys**; `required_stderr` carries
3 keys (geo2d/nav/r92 crash classes), **0 r94 keys**. The new meta gate
`r94_expected_errors_all_matched` filters `r["case"].startswith("r94_")` and
evaluates `not e["dead_in_run"]` — the same named-by-round / covers-round-prefix
shape as r87–r93. All nine `*_expected_errors_all_matched` gates are `True` in my
green run and the r94 one flips in the control (§V9).

**V4 — fresh independent execution (this seat).** 19 arms × 5 reps = **95
launches** in the battery's exact launch shape (`godot --headless --path <proj>
--script res://particles_lattice.gd -- --arm=<a>`, streams captured separately),
on the pinned export, host loadavg 87–93 with a foreign battery running
concurrently: **95/95 rc=0, 0 B stderr, 0 `ERROR:` lines, 19/19 rows PASS 5/5**,
pin present in every receipt. The classifier used is the production
`classify_process` extracted **verbatim** (AST source segment) from the pinned
harness: segment sha256
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` = the
segment recorded by r89–r94, so the r94 rows are judged by the same production
logic as their predecessors. Receipts:
`corpus/live/r94-reviewer/fresh/20261016T063411274867Z/` (`fresh.json` + 285
receipt files — 95 × `.out/.err/.rc` — plus the scratch `proj/` copy).

**V5 — cross-session and cross-condition pin presence.** Pin presence per
session/condition (all receipts of the arm, read directly):

| session | receipts | pin present | missing |
|---|---|---|---|
| this seat, folded fixture, 5 reps | 95 | 95 | — |
| author's 2 committed runs (folded) | 2 per row | 38/38 | — |
| scout canonical + loadtest (pre-fold) | 143 | 143 | — |
| boundary quiet / load / ff60 / ff120 | 57 each | 57 each | — |
| boundary ff120load | 38 | 38 | — |
| boundary ff30 | 57 | 54 | **3 — `r94_particles_cpu_pause.rep{1,2,3}.out`** |
| boundary ab (f30/f60/f120 × 3 arms) | 36 | 36 | — |

The only absence is exactly the pre-fold rejection the fold was made for: at
ff30 the pause receipt prints `cpu_pause ok=false vis_ok=true
vis_parent_ok=false pm_disabled_ok=false ts0_ok=true`. **Pinned-prefix
identity**: for every row the text before ` | ` is byte-identical across my 5
reps, the author's runs, the scout receipts and every boundary batch — the sole
exception being the ff30 `cpu_pause` line above. The three full-line pins
(census, ppm, convert) are **byte-stable** (1 distinct line in 5/5 my reps, in
the scout's 3 canonical reps, and 1 distinct prefix per batch in all six
boundary batches). Tool + data:
`corpus/live/r94-reviewer/tools/cross_session.py`,
`corpus/live/r94-reviewer/cross_session.json`.

**V6 — fold inertness on the pinned bytes.** For the arms re-run at 60 tps, my
fresh (folded) full lines differ from the boundary's pre-fold quiet receipts
**only in the unpinned measured tails** (±1–2 physics ticks: e.g. `cpu_lifetime`
`l01 delta=6 ph=6` fresh vs `delta=7 ph=7` quiet; `cpu_expl` `e1 delta=30` vs
`29`), while the pinned boolean prefix is identical — consistent with the
author's "signatures pin the law, not the tail" claim and with the ±1 mode
tolerance the `_okb` windows encode. No pinned byte changed between the frozen
probe and the folded fixture.

**V7 — full battery on the pinned committed bytes (this seat).**
`corpus/live/r94-reviewer/runs/20261016T063307552830Z/verdicts.json`: 314 rows,
verdict **FAIL** — the *only* failing row is the pre-existing, load-conditioned
`transition` (`ERROR: scene transition probe: initial current_scene
identity/marker mismatch`, exit 1), the same failure text the r93 reviewer
recorded; **19/19 r94 rows PASS**, all nine gates `True`, `dead_entry_count=0`.
The author's two green runs (worktree-only, see F1) re-read from disk:
`20261016T055703426158Z` and `20261016T060430025246Z`, both `verdict=PASS`,
314/314, 19/19 r94, `r94_expected_errors_all_matched=true`. **Row-level
comparison mine-vs-author**: 314 common cases, and the only field differences
are `transition`'s verdict/`actual_exit`; **all 19 r94 rows are field-identical**
(verdict, signature, expected_exit, actual_exit, script, flags, error,
required_stderr, expected_errors) — the insertion perturbs nothing.

**V8 — discrimination (forges reject).** Production classifier + committed pins
on my rep1 receipts (`corpus/live/r94-reviewer/tools/discrimination.py`,
`discrimination.json`): genuine **19/19 accept**; `pin_dropped` 19/19 reject;
`digit_flipped` 11/11 reject (8 pins contain no digit); `bool_flipped` 19/19;
`wrong_rc` 19/19; `foreign_error` 19/19; `truncated_mid_pin` 19/19. Two shapes
are accepted **by construction**, both pre-existing battery properties, not
defects of this landing (F5): `prefix_spoof` (a trailing token appended after
the pin on the same line — the production classifier is substring-anchored) and
`stderr_only` (the production classifier is merged-blob; a PASS line delivered
on stderr still classifies). Under the stricter stdout anchor the r93 seat's
harness imposed, `stderr_only` rejects 19/19.

**V9 — the floor gate is armed (control battery).** A one-line mutant of the
pinned harness (`corpus/live/r94-reviewer/ctl/run_battery.py`, `diff` = exactly
the planted line) adds
`"r94_particles_census": ("ERROR: ctlA planted dead r94 entry (never matches)",)`
to `expected_errors` and runs end-to-end:
`corpus/live/r94-reviewer/runs-ctl/20261016T063849666613Z/verdicts.json`.
`r94_particles_census` itself still PASSes (it is `ERROR:`-clean), but the
census records the planted entry with `dead_in_run: true`, the gate reports
`r94_expected_errors_all_matched=**False**`, `probe_error_clause_surface` FAILs
and the battery verdict is FAIL (`dead_entry_count=2`: the planted entry plus a
pre-existing `audio_bus_route_invalid_control` entry that went dead because that
load-conditioned row flaked in this run — it PASSed in my green run). So a
future r94 allowlist entry cannot die silently — the property the author claims
is demonstrated, not assumed.

**V10 — ERROR-cleanliness claim audited.** Every r94 receipt on disk has 0 B
stderr and no `ERROR:`/`SCRIPT ERROR:`/`Parse Error:` line: boundary
`r94_particles_*` 323/323 and `r94b_*` 375/375, scout `r94_particles_*` 143/143,
my fresh 95/95 — consistent with the `expected_errors`/`required_stderr` "+0
r94 entries" claim and with the boundary's `[scout_canonical] rejected=0`,
`[quiet] rejected=0`, `[load] rejected=0`, `[ff30] rejected=3`,
`[ff60/ff120/ff120load] rejected=0` headline (independently reproduced in
`cross_session.json`).

**V11 — prior-row identity / no perturbation.** The 19-row insertion leaves all
288 parent rows byte-identical in `CASES` (V1) and behaviourally identical in my
run vs the author's (V7): the crash/descendant tail rows
(`crash_spontaneous_sigabrt`, `crash_self_sigkill`,
`descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`)
all PASS in both runs, and no r94 row is touched by any allowlist.

---

## 2. Findings (ranked by severity)

**F1 (medium-low — evidence integrity; the commit carries only part of the
lane's evidence).** `git ls-files corpus/live/runs` = **0 files**: the two green
battery runs the commit message and the author report's evidence index point at
are **worktree-only**, excluded by `corpus/live/.gitignore` (`runs*/`). I
re-read both from disk (314/314, 19/19 r94, gate `True`) and reproduced the rows
independently, so no verdict changes. Same shape as the r92/r93 reviewer F1.
Suggested action: force-add the two runs' `verdicts.json` in the wave fold, or
scope the report's evidence index to tracked artefacts.

**F2 (low — the r94 gate is inert today; its "cannot die silently" property is
verified only by control).** With zero r94 allowlist entries the gate is
vacuously true in every genuine run (census covers only rows carrying
`expected_errors`: 68 rows in my run, none r94). It is genuinely load-bearing
only in the planted-entry direction, which the control battery demonstrates
(§V9). It also inherits the pre-existing executed-rows-only scope: a
*renamed/orphan* r94 key would produce no census entry and stay invisible.
Effect today: none (no r94 keys exist).

**F3 (low — precision; the `cpu_pause` fold weakens the row's 60-tps
assertion).** The three resume windows widen `[4,7] → [1,7]`. The fold is
mandatory (the frozen windows reject 3/3 at ff30 — V5) and is declared in the
fixture header, the harness comment and the author report, but it means the row
can no longer distinguish a 1–3-tick resume from the 4–5 ticks measured at
60 tps: a regression that shortened the freeze-then-resume latency to 1 tick
would still pass. The lower bound 1 is the physical floor (the signal cannot
precede the resume frame), so this is a precision loss, not a hole. Suggested
(if a future round wants it back): pin the measured `fin_after_*` tails in a
separate ff30-tolerant row, or window per condition.

**F4 (low — precision; the `cpu_request` fold is behaviourally inert on the
authored steps).** `round → floor` changes no emitted byte for the two steps the
arm exercises (`floor(0.5/0.10)=5→6`, `floor(0.5/0.05)=10→11`, identical under
`round`), so the boundary's falsification of `round` (steps 0.20/0.30) has **no
witness in the battery** — the fold is a robustness/comment correction whose
distinguishing case is deliberately not authored. Declared by the author
("emitted `expected=` values are unchanged"), so this is a scope note, not a
misrepresentation. A future round could add a `step020`/`step030` cell to make
the closed form falsifiable in-row.

**F5 (low — pre-existing classifier properties, not defects of this landing).**
Two forgery shapes are accepted by the production classifier for these rows:
*(a)* a trailing token appended after the pin on the same line
(`prefix_spoof`, 19/19 accepted) — the classifier is substring-anchored
battery-wide; *(b)* a PASS line delivered on **stderr** (`stderr_only`, 19/19
accepted) — the production path classifies the merged stdout+stderr blob and
only `required_stderr` rows are stream-anchored (the r89-fold critic F1 closed
that hole for those rows only). The r93 seat's discrimination harness imposed a
stricter stdout anchor, which is why its report shows `sig_to_stderr → FAIL`;
my numbers are production-faithful. The r94 rows are `ERROR:`-clean and
`required_stderr`-less by design, so neither shape is reachable from the
fixture's own behaviour. Effect today: none.

**F6 (low — evidence provenance; the scout's mixed-revision corpus).** The
scout's 143 r94 receipts are not all from the frozen probe revision (the
boundary's §2 records 135/143 predating it). The pins' cross-condition
stability does not rest on that corpus: it is confirmed on the boundary's own
323-check matrix (frozen revision), on the author's two folded-fixture runs and
on my 95 fresh receipts. Also worth recording precisely, because the author's
"60-tps-only" risk note is easy to over-read: `--fixed-fps 30` does **not**
reject the ladder rows — the boundary's `ab` receipts show `l01=7, l025=12,
l05=28, l1=58` at f30, all inside the authored `[4,8]/[12,18]/[27,33]/[57,63]`
windows (and the `ab` f30 receipts carry the pins verbatim, confirmed by the
labrat). The real exposure is a host `physics_ticks_per_second` override, which
no committed file sets.

---

## 3. Evidence index (seat-owned receipts)

All under `corpus/live/r94-reviewer/` (untracked; `manifest.sha256` covers every
file except itself):

| artefact | path | what it shows |
|---|---|---|
| pinned export | `pinned-tmp/` | `git archive c7228893 corpus/fixtures`; 81/81 files `git hash-object`-identical to their blobs |
| fresh arm receipts | `fresh/20261016T063411274867Z/` | 95 launches, 19/19 arms PASS 5/5, rc=0, 0 B stderr, classifier segment sha `749fa060…` |
| my battery run | `runs/20261016T063307552830Z/verdicts.json` | 314 rows, r94 19/19 PASS, 9/9 gates True; only `transition` (pre-existing) FAIL |
| control battery | `runs-ctl/20261016T063849666613Z/verdicts.json` | planted r94 dead entry ⇒ `r94_expected_errors_all_matched=False`, battery FAIL |
| control mutant | `ctl/run_battery.py` | pinned harness + exactly 1 planted line |
| discrimination | `discrimination.json` | 7 forgery shapes × 19 rows, production classifier |
| cross-session | `cross_session.json` | pin/prefix/line identity across 5 sessions × 6 conditions |
| tools | `tools/{run_arms,discrimination,cross_session}.py` | reproduction path |
| logs | `fresh-arms.log`, `battery-run1.log`, `battery-ctl.log` | raw run logs |

Reproduction: `python3 corpus/live/r94-reviewer/tools/run_arms.py --reps 5` →
`python3 .../discrimination.py --fresh <fresh dir>` →
`python3 .../cross_session.py --fresh <fresh dir>`; batteries via
`python3 corpus/live/r94-reviewer/{pinned-tmp,ctl}/run_battery.py --runs <dir>`.

---

## 4. Remaining risks / blockers

- **`_okb` windows are tps-alias-dependent** (author-declared, boundary §3): the
  ladder/stream windows assume `round(L·tps)` at the launch 60-tps default. No
  committed file overrides `physics_ticks_per_second`, so the rows are safe
  today; a future project override would reject them. `--fixed-fps` modes are
  absorbed (F6), so this is a host-tps exposure only.
- **F3's widened window** accepts a 1-tick resume at 60 tps; declared, bounded by
  the physical floor.
- **Host was never idle** (loadavg 59–93 throughout this review; a foreign
  battery lane ran concurrently) — all measured tails are host-conditioned. The
  pinned form is the boolean block, which was stable in 100% of receipts in all
  conditions tested, including the boundary's 16-hog load batches.
- **Blockers: none.** Nothing was committed by this seat; `HEAD` is still
  `c7228893`; sibling lanes' artefacts (the r95 block that landed in the live
  `corpus/fixtures/run_battery.py` at 03:41:30, untracked
  `corpus/live/r94-simplifier/` and `corpus/live/r93-*` files) are untouched by
  me. The operator should note the live worktree has moved ahead of the
  reviewed commit — re-read the committed tree, or my pinned export
  (`corpus/live/r94-reviewer/pinned-tmp/`), for the reviewed bytes. Shipping
  decisions remain the operator's.
