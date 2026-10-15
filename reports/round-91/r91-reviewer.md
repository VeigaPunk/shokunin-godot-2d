# r91 reviewer — wave-B gate on the committed nav_lattice landing (`77d2f7e`)

Seat `REVIEWER` (g2d lane r91) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.
Reviewed commit **`77d2f7e`** (HEAD at review time; parent `13828dd`). Diff scope:
`corpus/fixtures/nav_lattice.gd` (**+882/−0**, new), `corpus/fixtures/run_battery.py`
(**+88/−0**, 4 pure-insertion hunks), `reports/round-91/r91-author.md` (+223), and 99
committed fresh-arm receipts under `corpus/live/r91-author/fresh-reps/`.
**This seat modified no tracked file and made no commit.** Seat-owned untracked
scratch/receipts: `corpus/live/r91-reviewer/**` (99 fresh Godot launches + 2 full battery
runs + run/classify drivers, `manifest.sha256` 1026/1026 OK, no self-entry) and this report.

**`lsp` disclosure.** No `lsp` device and no GDScript/Python language server is exposed to
this seat. Every check below is a textual/AST read of the committed bytes plus
fresh-process execution receipts — the literal fallback, recorded so it is never presented
as semantic proof. The diff contains no renames (fixture landing + literal
`CASES`/allowlist/gate inserts), so no symbol-aware operation was possible or required.

**probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2) was dispatched, with one
bounded hypothesis: *every one of the 11 `nav_lattice_*` signatures is a contiguous prefix
of its arm's single print expansion, ending before the first scheduler-adjacent field, and
no signature contains a scheduler token; the `_stale()` and unknown-arm lines satisfy no
signature.* It had **no shell/exec tool** (read/grep/glob only) and executed nothing; it
returned a static reconstruction that **held for 11/11 rows** with one borderline flag
(`pre_iter=` textually contains the token `iter=`), plus a 13-print-site classification
(11 pinned + 1 loud-failure + 1 fallback) and a null result on runtime-value correctness
(declared as inference, not measured). It was not re-dispatched; all empirical evidence
below is this seat's own fresh execution.

**Concurrent-worktree disclosure.** While this review ran, an in-flight **r92 author** lane
appended +161 lines of `r92_tilemap_*` rows to the *worktree's*
`corpus/fixtures/run_battery.py` (mtime 20:25:53 local). That is not this seat's work, is
not in `77d2f7e`, and was left untouched. Every check below reads the **committed** bytes:
the fixture/harness were pulled with `git show 77d2f7e:…` (harness sha256
`f5725ca441565b8c…`, fixture sha256 `088843399ce3…` — both byte-equal to the review commit)
and my launch project is a copy of the committed `corpus/fixtures/`, so neither the battery
runs nor the arm runs touch the dirty worktree.

**Verdict: PASS on the landed bytes.** The four boundary folds the dispatch names are
implemented as claimed and are *demonstrated* (not merely asserted): the `iteration_id`+reach
gate turns every stall I could produce into `STALE …` + exit 2, scheduler fields live only
after the pins, the agent reads `is_navigation_finished()` before `is_target_reached()`, and
the teardown arm's `rc=-6` is bound to the glibc double-free fragment on stderr with the
signature anchored to stdout (5/5 forgery shapes reject). 11/11 nav rows PASS in both of my
independent battery runs and in 55/55 loaded fresh arm runs; every rep-to-rep byte
difference lies strictly after the pinned prefix. Findings F1–F8 are evidence-integrity /
precision / by-design items; **none changes a pinned byte or a row verdict**.

---

## 1. What was verified clean

**V1 — additive, scoped diff; prior rows untouched.**
`git show --numstat 77d2f7e`: `nav_lattice.gd` +882/−0, `run_battery.py` **+88/−0**
(4 hunks, `git show | grep -c '^-[^-]'` = 0 deletions), report +223, 99 fresh-rep receipts.
AST row-diff of `CASES` from the r90 landing (`ee20575`, 240 entries) to `77d2f7e`
(251 entries; `77d2f7e`'s parent is `13828dd`):
240 → 251 entries, **pure insertion of 11 rows at index 236**; `names[:236]` identical and
the 4-row crash/descendant tail (`crash_spontaneous_sigabrt`, `crash_self_sigkill`,
`descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`) keeps its
order, so the guarded `sleep 8` detached-control row stays adjacent to the meta probes.
All 251 entries are 5-tuples, names unique. Committed shas match the report exactly:
fixture `088843399ce37eb272dfb8cbf7e2a115f1b9af01a44859ea05610297875e3796` (882 lines),
harness `f5725ca441565b8c9903b5e98aeb1112ea5c56a11a1f422b6feb46f904953220`, scout probe
`efb496e5fe08e6679c19c5f2a7a1eef86098f97f4a6407edab10451859afe5f9` (verbatim provenance),
`project.godot` `8de8b3af…` unchanged.

**V2 — row shape and gate mechanics.** All 11 rows: script `nav_lattice.gd`, a single
`--arm=<arm>` flag matching the row suffix, expected exit 0 (crash row −6), signature a
plain string (no envelope). Result rows **258 = 251 CASES + 7 meta** (r90: 247 = 240 + 7).
The `expected_errors` entries are **exact-shape** and load-bearing: census (both my runs)
`nav_lattice_sync` `matched_lines=1`, `nav_lattice_bake` `matched_lines=1`, each
`dead_in_run=false`, `bare_classification_rejects=true`,
`allowlisted_classification_passes=true`; `rows_with_expected_errors` 57 → **59**,
`dead_entry_count=0`. The `required_stderr` pin is stream-anchored by the harness
(`fragment in proc_stderr` **and** `signature in proc_stdout`).

**V3 — classifier identity.** The `classify_process` segment extracted from the committed
harness is byte-identical (segment sha256 `749fa0607e7707e6…`) to the segment r89/r90
recorded — the r91 diff does not touch the classifier, so the r91 rows are judged by the
same production logic as their predecessors.

**V4 — fresh independent execution, loaded (this seat).** `corpus/live/r91-reviewer/tools/run_arms.py`
in the battery's exact launch shape (`godot --headless --path <proj> --script res://nav_lattice.gd -- --arm=<a>`),
11 arms × 5 reps, 4-way concurrent, host loadavg 50–65: **55/55 classify PASS** with the
production classifier + per-row allowlists; `out_uniq` per row 1–5, `err_uniq=1` everywhere,
no `STALE`, rc as declared (crash row `-6` in 5/5). Every emitted line's **pin is a byte
prefix** of the emitted line (`startswith` = True, 11/11 rows) and every arm prints exactly
one PASS line.

**V5 — scheduler fields are tails, measured.** Rep-to-rep variance over my 5 fresh reps is
confined to the declared tails in **all 11 rows**: first divergence char ≥ pin length
(agent 417≥271, avoid 320≥210, bake 685≥554, path 713≥604, query 716≥607, region 1131≥939,
sync 438≥249); `census`, `link`, `teardown_clean`, `teardown_crash` byte-identical across
5 reps. The committed 3 reps show the same (avoid 320≥210, region 1131≥939, others
identical). Concretely, only the tails moved: `agent first_reachable=5|6`,
`sync ladder=[…f2:1/1/0|1/0/0…]`, `path settle=5|9`, `bake settle_b=0|1|2`,
`query settle=5|6`. Static token scan of the 11 pins: no `settle=`, `iter_b=`,
`link_iter=`, `gate=`, `ladder=`, `first_reach`, `walk_steps=`, `reached_at=`, `dis_same=`,
`fwd_disabled_same=`, `chg_iter_*`, `seq_*`, `vel_*`, `sum_max=` token appears (the one
textual hit, `pre_iter=`, is F5).

**V6 — the sync gate is a loud failure surface, not a silent settle (the r91 fold's
headline).** Under the boundary's non-benign modes the folded fixture never prints a
PASS-shaped payload off an unsynced map. `--fixed-fps 120`, 11 arms × 2 = 22 runs:
**8 STALE + rc=2** (no PASS line at all), **3 in-pin divergences**, **11 pin-matches** —
`sync` rep1 emitted
`… chg_settled=false dis_settled=true …` where the pin says `true/false`, and `link`
emitted the *un-truncated* `fwd_disabled_settled` (4-point) / truncated `cost300`, i.e. the
levers had not applied. `--fixed-fps 30`, 11 arms × 2: **11 STALE + rc=2**, **2 in-pin
divergences** (`path` rep0 `gap20` un-bridged `gap20_reach=false`; `link` rep1 as above).
Everything else either matched the pin byte-for-byte (`agent` 2/2 ff120, `census`, both
teardown arms) or failed the pin. **No case exists in which the pin matched while the
underlying state was stale** — the two failure classes are exactly {STALE+2, pin-mismatch},
both of which the battery rejects (`expected_exit=0`). Receipts: `fps120/`, `fps30/`.

**V7 — the teardown negative control is armed and its stderr pin is load-bearing.**
**16 crash instances** — 11 from this seat's own runs (5 fresh-load + 2 ff120 + 2 ff30 +
2 battery rows), 3 committed fresh-rep receipts, 2 author-battery rows: **every one**
`rc=-6`, stdout marker
`NAV_LATTICE_TEARDOWN_CRASH armed=live_cb has_cb=true`, stderr
`double free or corruption (!prev)` — including both `--fixed-fps` modes, so the class is
mode-independent. Discrimination on a **real committed receipt**, re-classified with the
production clause + the committed `required_stderr`:

| cell | verdict |
|---|---|
| clean committed shape (−6, fragment on stderr, sig on stdout) | **PASS** |
| −6 but fragment removed from stderr | FAIL |
| −6 with the signature on stderr only | FAIL |
| fragment present but wrong signal class (rc=0) | FAIL |
| −6, fragment only on stdout (merged-blob spoof) | FAIL |
| −6 + fragment + a foreign `ERROR:` line | FAIL |

The two controls are also separated: `teardown_clean` (`clear + ≥1 frame + free`) is
`rc=0 survived=true has_cb=false` in every rep (committed + 5 fresh + 4 fps cells).

**V8 — full battery on the committed bytes, twice (this seat).**
`corpus/live/r91-reviewer/runs1/20261015T224809997808Z` → **257/258** (only `transition`,
a documented volatile class), nav **11/11 PASS**;
`runs2/20261015T232238495426Z` → **256/258** (`transition`, `input_lattice_pre_frame`, both
documented volatile), nav **11/11 PASS**. In both runs: `r91_expected_errors_all_matched`
**true**, `all(40 discriminations)` **true**, `dead_entry_count=0`. Host context: both runs
ran under foreign oversubscription (loadavg ≈50–65; a sibling r91-critic lane started 16
CPU hogs at 20:22, i.e. during rep2) — none of it this seat's, and none of the 11 nav rows
flaked in either window. The author's two green
runs re-read from disk are genuinely 258/258 with the same gate values, and the author's
99 committed fresh-rep files re-classify **33/33 PASS** (out/err/rc triples, one PASS line
each, `err_uniq=1`).

**V9 — prior-row identity.** My rep1 vs the r90 green reference
(`corpus/live/r90-author/runs9/20261015T212551992799Z`): 247 common rows, **0 signature
mismatches**, 0 old-only rows, 11 new-only rows (the nav block). The +88-line insertion
perturbs nothing upstream. My rep1↔rep2 verdict diff is 1 row
(`input_lattice_pre_frame`); raw-output diffs are 16 rows, all documented-volatile
diagnostics (pids/paths/ASLR/`frames=`/envelope rows) plus the two nav tail-only rows
(`region`, `avoid`) — signatures and verdicts identical.

**V10 — harness invariants.** Every landed `expected_errors` key names a real CASES row
(inspected; the harness itself does not enforce this — see F6); no envelope row carries
entries (no tuple-into-classifier path); the 4 hunks are pure
insertions; the 11 rows sit immediately before the crash/descendant tail; the fixture has
exactly 13 print sites (11 arm prints + `_stale` + unknown-arm fallback), each arm's
`_stale` branch `return`s before any print, and the fixture's own `at:` backtraces in the
committed receipts confirm the report's engine citations
(`nav_map_2d.cpp:165`, `godot_navigation_server_2d.cpp:115`, WARNING at
`navigation_polygon.cpp:316` with no `ERROR:` token).

---

## 2. Findings (ranked by severity)

**F1 (medium-low — evidence integrity; the commit carries only part of the lane's evidence).**
`git ls-files corpus/live/r91-author` → **100 files**: 99 `fresh-reps/*` + `manifest.sha256`.
The manifest itself lists **642** entries — 543 of them under `runs1/`+`runs2/`
(272 + 271), which are excluded by `corpus/live/.gitignore` (`runs*/`). So the commit's
manifest cannot verify from a checkout, and the two "258/258" battery runs the commit
message and the report's evidence index point at (`runs1/20261015T223815564642Z/verdicts.json`,
`runs2/20261015T224213073214Z/verdicts.json`) are **worktree-only**. (Contrast r90 F1:
that lane committed *nothing*; r91 commits the fresh-arm receipts — the load-bearing
per-row evidence — and omits the battery run trees.) I verified the manifest in the live
worktree (642/642 OK, no self-entry, no missing file) and reproduced the green claim myself
(V8), so no verdict changes. Suggested action: force-add the two run trees (or their
`verdicts.json`) in the wave fold, or scope the evidence index to tracked artefacts and
state the gitignore exclusion.

**F2 (medium-low — tolerance margin inside pins, by design and loud).** The pinned
4-frame-settled reads
sit 1 frame above the boundary's measured worst case (max 3 of 56 lever-runs at 60 tps):
`sync.chg_settled`/`dis_settled`, `path.gap20*`, `region.*` settled geometry, and
`link.fwd_disabled_settled` (the boundary's own weakest lever: link-disable 2 frames at
60 tps, never under fixed-fps). My fps cells show exactly what a 4-frame-miss does —
in-pin divergence, row FAIL, never a silent pass. This is the correct failure direction,
but it is the tightest tolerance class in the landing and the one most likely to flake
under a heavier host; `link` remains the weakest-evidenced row (author's own flag #2), now
with 5 fresh + 4 fps cells added by this seat.

**F3 (low — gate naming/coverage precision).** The new floor gate
`r91_expected_errors_all_matched` (harness line 2746) filters on
`case.startswith("nav_lattice_")` — **no row carries an `r91_` prefix**, so the author's
"same named-by-round / covers-round-prefixes shape as r87–r90" is inaccurate: coverage is
by *feature* prefix (precedented by r89's `geo2d_lattice_`/`input89_edges_` pair). Effect
today: none (both entry-bearing rows are `nav_lattice_*` and are covered; the gate is true
and non-dead in both my runs). Effect tomorrow: a hypothetical `r91_*` row with a dead
entry would not be caught. Suggested: rename to `nav_lattice_expected_errors_all_matched`
or add the `r91_` prefix to the tuple.

**F4 (low — dead code in the fixture).** `const SETTLE := 10` (`nav_lattice.gd:56`) is
never referenced anywhere in the 882 lines (`grep -n SETTLE` → declaration only); the
settle-pattern was replaced by `_await_sync`. Vestige for the r91 simplifier seat to
delete; no behavioral effect.

**F5 (low — one iteration-id-shaped token inside a pin; disposition: benign, but worth a
comment).** `nav_lattice_sync`'s pin contains `pre_iter=0`, which textually contains the
token `iter=` (my scan and the labrat's independent scan both flagged it). Disposition:
`pre_iter`/`pre_regions`/`pre_path`/`pre_closest` are **pre-sync** reads taken in
`_initialize` before the first physics frame — structurally 0/0/[]/(0,0), measured 0 in
61/61 boundary gate runs and in all 55 of my reps, and the accompanying pre-sync
`map_get_closest_point` ERROR is the whitelisted, exactly-once receipt. It is not a
scheduler field; the fixture comment just doesn't say so.

**F6 (low — allowlist orphan keys are invisible; pre-existing).** The census is built from
executed rows, so an `expected_errors` key naming a **non-existent** case is silently
ignored (no census entry ⇒ no dead-entry). The author's sentence "A dead r91 allowlist
entry fails `probe_error_clause_surface` loudly" is therefore true for entries attached to
executed rows (the two landed ones, `matched_lines=1`, both directions verified) but
over-general as written. Identical property in r87–r90; not an r91 regression.

**F7 (low — freed-RID read in the positive control; disclosed).** `teardown_clean` prints
`agent_has_avoidance_callback(a)` **after** `free_rid(a)` (`nav_lattice.gd:879` → `:882`);
silent on this build (`has_cb=false`, 0 B stderr, every rep). A future build that makes
freed-RID reads loud fails the row loudly; the fix is to query before `free_rid` (the value
is already captured). The negative control correctly reads `has_cb` *before* the free
(`:857` before `:859`).

**F8 (info — derived-value pins whose generator is a frame loop; loud on drift).**
`agent.dist=2.2741` / `final_pos=(178.3920,178.3920)` are the residue of a 28-iteration
self-paced walk (8 px/step), and `avoid.sum_bound_ok`/`dirs_ok` require exactly 5 paired
measured frames. Both are deterministic in every rep I ran (5 fresh + 2 ff120 + 2 ff30;
`walk_steps=28 reached_at=28` throughout, `n_a=n_b=21` throughout), and both fail **loudly**
on drift (one extra iteration moves `final_pos` by ~8 px; a missed callback makes
`sums.size()!=5`). Same class as the author's own labrat flag #3 — recorded, not a defect.

---

## 3. Residual risks

- **`--fixed-fps` is not a benign harness variation** (boundary attack 9). The landing is
  *correct* under it — STALE/exit 2 or pin-mismatch — but the battery never runs that mode,
  so a future harness change that adds `--fixed-fps` to the nav rows would turn them red
  loudly rather than silently. My 44 fps cells (22 × ff120, 22 × ff30) are the receipt set.
- **4-dp navmesh vertex pins** (`diag`, `gap20`, region/link/bake paths) ride the engine's
  vertex order/partition: stable on this build across 5 committed + 5 mine + 44 fps reps;
  a solver change moves last decimals (same caveat class as r89/r90 geometry pins).
- **Build/host tokens**: `srv_methods=199 poly_methods=134`, the enum arrays and the
  `*_defaults` blocks are version tokens that flip loudly on an engine bump (intended).
- **Toolchain-pinned stderr fragment** `double free or corruption` is the glibc malloc
  printer (same class as the Clipper2 tokens already pinned); `(!prev)` is deliberately
  unpinned. A different libc/allocator would fail the row loudly.
- **F1**: the lane's battery evidence lives only in the worktree; a worktree clean loses it
  (my V8 reproduction is the durable substitute until the wave folds the run trees).
- **Concurrent worktree churn** (header note): a sibling r92 lane is editing the same
  `run_battery.py`; any later commit folding those edits is a new artefact set whose r91
  rows would need a diff-scoped re-check (the nav rows themselves are untouched by that
  edit — verified: the insertion is appended after `nav_lattice_teardown_clean`).

## 4. Blockers

None. Shipping/admission decisions remain with the operator.

---

## 5. Evidence index / reproduction

| artefact | path |
|---|---|
| committed bytes under review (pulled with `git show 77d2f7e:…`) | `corpus/live/r91-reviewer/pinned/{run_battery.py,nav_lattice.gd,project.godot}` |
| classifier segment (verbatim, sha `749fa0607e7707e6…`) | `tools/classify_process.py` (AST-extracted from the committed harness) |
| receipt re-classifier (production clause + allowlists + stream anchors) | `tools/verify_receipts.py` |
| fresh arm runner (battery launch shape, `--fixed-fps` opt-in, parallel) | `tools/run_arms.py` |
| 55 loaded fresh arm receipts (11 arms × 5) | `fresh-load/**` (+ `fresh-load.log`) |
| 22 `--fixed-fps 120` receipts | `fps120/**` (+ `fps120.log`) |
| 22 `--fixed-fps 30` receipts | `fps30/**` |
| full battery run 1 (257/258, nav 11/11) | `runs1/20261015T224809997808Z/verdicts.json` |
| full battery run 2 (256/258, nav 11/11) | `runs2/20261015T232238495426Z/verdicts.json` |
| launch project (copy of committed `corpus/fixtures/`) | `proj/` |
| receipt manifest (this seat) | `manifest.sha256` — 1026/1026 OK, no self-entry |
| committed author receipts re-classified 33/33 | `../r91-author/fresh-reps/*.{out,err,rc}` |
| r90 green reference for prior-row identity | `../r90-author/runs9/20261015T212551992799Z/verdicts.json` |

Reproduction:

```
git archive 77d2f7e | tar -x -C <scratch>            # or: git show 77d2f7e:<path> for single files
python3 corpus/live/r91-reviewer/tools/run_arms.py --proj corpus/live/r91-reviewer/proj \
        --out <receipts> --reps 5 --par 4            # add --fps 30|120 for the stall cells
python3 corpus/live/r91-reviewer/tools/verify_receipts.py <receipts>
python3 corpus/live/r91-reviewer/pinned/run_battery.py --runs <runsdir>
```

Reviewed commit `77d2f7e`; this seat made no tracked modifications and no commits.
