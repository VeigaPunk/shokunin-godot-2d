# r102 C3-critic — simplifier queue: load-bearing deletions & per-hunk discrimination audit

Plan (5 lines, as written first):
1. Read r101-simp1/2/3 queues + r94 cpu_contam lesson + scout census to inventory every hunk proposed for landing.
2. Build a discrimination-loss taxonomy (deletion that gates a detector/discriminator vs pure noise) and screen all hunks.
3. For each suspect hunk, run targeted godot headless counterfactuals in /var/tmp/r102-crit3/ (never run_battery.py).
4. Verify stale `.shokunin/game-dev-2d/corpus/` citation repair claims (scout census) without editing shared files.
5. Emit per-hunk verdict table (land / land-with-guard / reject); fix nothing in shared files.

Host / context (once): `17:40:57 up 1 day, 17:41, 1 user, load average: 6.55, 8.32, 9.12`; sweep end `17:52:50 ... load 18.14, 18.96, 14.45`. Repo HEAD `1392ca21` (round-101 close). Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`). Scratch `/var/tmp/r102-crit3/` (`/tmp` EDQUOT, per r101 precedent). Sibling seats' Godot processes visible (c5/mut7/E2) — load shared.

## Verdict

**All 10 fold sets LAND-CLEAN under an independent battery-shape sweep + per-hunk discrimination audit. No hunk rejects; one application guard (simp1-nav or simp3-nav — the two are `diff`-identical; apply exactly one). One real discrimination delta found (stree type-guard strip, dev-time only, no row impact) and one required evidence gap found and closed (r95b `_arm_procwait` — touched by the fold, no registered row).**

The r101 SIMP evidence was output-identity on registered rows. The r94 `cpu_contam` lesson (pinned tokens were structural counts; a discrimination-killing mutant kept the pinned PASS byte-identical) demands more: show the deleted line is not a *source of a pinned token*, not a *claim instrument*, and that every touched code path (incl. unregistered arms) was exercised. That evidence is supplied per hunk below.

## Provenance link verified (patch == verified fold)

- `git apply --check` at 1392ca21: all 12 patch files apply clean (0 fuzz), including the comment-only `r101-simp3-r95-harness-comment.patch`. Applied to a committed-bytes scratch tree (`rsync corpus/fixtures` minus `run_battery.py`, name-munged `config/name`), the folded shas reproduce every recorded folded sha (prefix-16): nav `b23887e5b05d8306`, canvas `8bfddb748d1be3d2`, attack `7021e53c0fcc3d7f`, rksenum `5d7e3aab8d44e426`, audio `91161bf5a6ff9ea5`, stree `4c457f887d933760…`, scene_io `18bc06da6c4d5ca6…`, particles `afd2aa88876abc7a`, dss `c128e9ccf3b3f512`, r95b `b367559e831e5e9f`. So the queued patches are byte-identical to the folds the SIMP seats verified — no drift between their proof and the landing artifact.

Command: `for p in reports/round-101/mutations/r101-simp*; do git apply --check $p; done` → every file APPLIES. Fold reproduction: `patch -p3` into `/var/tmp/r102-crit3/folded` (receipt: `sha256sum` above).

## Independent sweep (the base measurement)

- Runner: `reports/round-102/mutations/r102-crit3-probe.py` — extracts CASES/expected_errors by AST from `run_battery.py` (never executes it), launches every row of the 10 folded fixtures on BOTH trees in the battery's shape: `godot --headless --path <tree> --script res://<fixture> -- <flags>`, merged = stdout+stderr (battery's `run_process` convention), 30 s bound (battery's is 8 s), production `classify_process` ported (allowlist shapes: exact / comma-prefix / structured; rc + signature + no unrelated ERROR + no SCRIPT/Parse Error).
- **155 rows × 2 trees = 310 launches (197 s wall, two trees in parallel). Result: 155/155 PASS on base AND folded; 0 rc discordances; 0 signature discordances; 0 verdict discordances.** Per fixture: nav 11/11, canvas 15/15, r98b_attack 15/15, rksenum 1/1, audio 18/18, stree 12/12, scene_io 13/13, dss 17/17, r95b 34/34, particles 19/19 (both trees).
- Raw merged-output identical 117/155; masked-identical (backtrace `res://*.gd:<line>` masked) 124/155. The 38 raw-diff rows split 7 backtrace-only (declared class: nav sync/bake, scene_io refuse, canvas clip/draw_refusal, r98b clipmatrix, audio gen) + 31 in declared-unstable tails (`env=` counters, tick-phase staggers, wall-clock audio fields, particles frame counters, nav boundary tails).
- **Pinned-span check**: for every raw-diff row, the CASES evidence substring is present in both trees; for the 10 rows where the PASS-line text itself differs, the first differing byte lies **outside the pinned evidence span** (e.g. `r98b_qflush_suppress`: pin = `hide_ticksep_n=1 hidden_across_tick_n=0 show_after_tick_n=1`, identical; the difference is `hide_span_pf=2 vs 3`, which SIMP-1's null control measured varying 3/6 within base). Focused interleaved null control (`r102-crit3-focused.py`, 12 rows × 2 reps × 2 trees = 48 launches): both trees show within-tree variance on these fields; no verdict moves. Limitation: n=2/tree is size-of-sample evidence, not envelope equality (see Unknowns).

## Per-hunk audit

Legend: "zero-reader" = scope-aware census at HEAD by exact line, zero value reads after the deleted construct (my greps, lines cited). "Covered" = every arm containing the touched lines has ≥1 registered row (coverage table from `r102-crit3-coverage.py`: patch hunk base-lines → enclosing func → `match arm:` dispatch → registered `--arm` values).

| # | hunk (file, origin) | deleted / rewritten | covering rows | independent result | discrimination view | verdict |
|---|---|---|---|---|---|---|
| 1 | `nav_lattice.gd` −3 (r91 SP1/SP2) | `const SETTLE` (zero-read: only occurrence L56); 2× `var hits` + lambda body `hits.append(v)` → `pass` | all 11 nav rows; teardown_crash/teardown_clean covered by name | 11/11 PASS both trees; `teardown_crash` rc=−6 + `double free or corruption (!prev)` + marker `armed=live_cb has_cb=true` byte-identical both trees; `teardown_clean` rc=0 `survived=true` | crash/clean discrimination (**the row's teeth**) intact: crash present in both. Residual (both r91+SIMP-3 flagged): the fold narrows the pinned mechanism to *registration-bound* abort; a future engine whose abort depends on the callback body would red the folded row, original might not. The sink was executed (2 hits/arm, r91-F2 probe) but its value had zero readers even before — nothing observable is dropped. | **LAND** |
| 2 | `canvas_lattice.gd` −10 (r98 F1/F2) | `_notif_keys()` helper (0 call sites; only L103); `var methods` + append (never read; `draw_n` from sibling `drawm`) | all 15 canvas rows; `_arm_census` covered | 15/15 PASS; census row raw-identical | deleted helper is not a claim instrument: no call site, no dynamic dispatch (`call(`/`has_method` census clean); `methods` feeds no pinned token | **LAND** |
| 3 | `r98b_attack.gd` −4 (r98 F3/F4) | `var owner_ref`+write (decl+write only, L119/173); `var pfs`+append in `QH._draw` (L144/147) | all 15 rows; `_arm_qflush` covered | 15/15 PASS; qflush PASS lines identical; only `hide_span_pf` tail varies (unpinned) | **r94-trap analog checked**: `pfs` is per-frame draw bookkeeping, but every pinned qflush token traces to intact fields (`QF.draw_pf_counts` L126/137/212-219, `QHC.pf_*` L159-169/248-249) — the deleted accumulator feeds neither pins nor unpinned diagnostics (zero readers). `owner_ref` keep-alive-shaped — but `t` is tree-held (`root.add_child`) and `self` is the SceneTree; no lifetime change | **LAND** |
| 4 | `r98b_rksenum.gd` −3 (r98 F6) | `var _items` + append in `_it` | the 1 row | 1/1 PASS; `R98BRKS` line byte-identical | PASS line built directly; `_items` never flushed/read | **LAND** |
| 5 | `audio_lattice.gd` −2 (r99 F1) | `var prev_t := Time.get_ticks_usec()` + per-iteration store (L161/176) | all 18 audio rows; `_arm_mixblock` covered | 18/18 PASS; mixblock pinned predicates identical | decl + own-write only (L161/176); jitter math reads `prev`/`last_jump_t` (kept). Wall-clock tails vary in both trees | **LAND** |
| 6 | `stree_lattice.gd` −17 (r97 F1-F5) | `_tree_names()` (0 callers); `it_valid`→`_it` (51 sites, pure alias, String-typed both sides); `it_connected`→`_it(k,_v(v))` (6 sites); `it_paused`→`_it("paused_seen",str(n))` (3 sites); one comment restatement | all 12 rows; all touched arms covered (defer_ladder/defer_order/defer_slots/group_flags/group_setters/scene_probe/signal_flags) | 12/12 PASS both trees | aliases were pure (`func it_valid(k,v): _it(k,v)`); **one measured delta**: the typed wrappers rejected String args at load; the folded form accepts them (see §Type-guard). Numerics were coerced before (float/int → `true`). No registered row passes a non-bool; r97-critic itself recommended removing these misleading "validation" names | **LAND** (note) |
| 7 | `scene_io_lattice.gd` −12 (r96 fold) | 2 binding→bare-call (side-effecting calls KEPT: `_mk_child`, `ResourceSaver.save`); 12 terminal `= null` after last read | all 13 rows; every touched arm covered | 13/13 PASS; `refuse` raw diff is backtrace-only (masked-identical); rest raw-identical | deleted stores are **inert by position**: every pinned print precedes them; no read can observe them. The r96 liveness trap is respected — `var loaded = ResourceLoader.load(p)` (L763, refuse) is KEPT; only its terminal `= null` (L778) goes. Free timing moves to function end; no destructor output in any receipt | **LAND** |
| 8 | `particles_lattice.gd` −3 (r94 F1) | file-scope `var T0` + init store; `var start3 := PH` | all 19 rows; `_arm_gpu_headless` covered; `_initialize` runs for every row | 19/19 PASS both trees | r94-simplifier proven class (57-pair + full battery); my sweep re-verifies. Tail frame counters vary within both trees | **LAND** |
| 9 | `dss_lattice.gd`+`r95b_order.gd` −5 (r95 F2) | 15 dead stores/18 edits; side-effecting calls retained (`_mk_body`, `_pile`, `_sh`); `_pile(…, made2/made3)` → `_pile(…, [])`; 2× `var dss := _dss()` removed entirely | dss 17/17 rows; r95b 34/34 rows; `_arm_free/readd/layers/celloff/twopiles` covered | dss 17/17, r95b 34/34 PASS both trees; dss tokens re-censused at exact lines (each deleted name occurs only at its decl/append site in-scope) | `_mk_body` does `root.add_child(b)` (dss L141, r95b L245) — created bodies are tree-held, so dropped `made`-arrays are not keepers. `_dss()` is a pure getter (`return PhysicsServer2D.space_get_direct_state(root.world_2d.space)`, r95b L105-106) — removing the call removes nothing. **Evidence gap found + closed**: `_arm_procwait` is touched but deliberately unregistered (run_battery comment L911); targeted runs `--arm=procwait` base vs folded: **byte-identical, rc 0, 3 reps each** (both trees emit payloads from the same set) | **LAND** |
| 10 | nav duplicate | `r101-simp1-r91-nav_lattice.patch` and `r101-simp3-nav-fold.patch` are `diff`-identical (two independent reproductions) | — | — | — | **apply ONE** |

## The one measured discrimination delta — stree type-guard strip

Commands (scratch project `/var/tmp/r102-crit3/guard/`, exact stree wrapper signatures):
- committed shape `func it_connected(key: String, v: bool)` + `it_connected("probe_str", "x")` → `SCRIPT ERROR: Parse Error: Invalid argument for "it_connected()" function: argument 2 should be "bool" but is "String".` rc=1 (loud rejection).
- folded shape `_it("probe_str", _v("x"))` (with `_v(v: Variant)`) → `GUARD probe_str=x`, rc=0 (silently accepted).
- numeric args: committed coerces (`1.5`→`true`, `1`→`true`, rc=0); folded prints raw. Difference only for ill-typed call sites — none exist; no row impact; dev-time-only. Severity LOW/INFO; the fix direction r97-critic already endorsed (the names implied validation that never existed).

## r94 cpu_contam-class near-misses evaluated

- `r98b_attack.pfs` — the only hunk in the queue shaped exactly like `cpu_contam` (per-frame bookkeeping in a draw-frequency arm). Cleared: pinned tokens trace to intact sources; the accumulator has zero readers (see #3).
- `nav hits` — sink executed 2×/arm but write-only; the crash discrimination is intact (#1). Residual mechanism-narrowing documented, not closable without an engine change.
- `particles T0/start3` — r94's own simplifier fold, with 57-pair + battery evidence; re-verified here (#8).

## What output-identity cannot prove (explicit residual register)

1. **Engine-future behavior**: these folds are proven neutral for Godot 4.7.2 as observed. A future engine that makes the nav abort body-dependent, or that emits destructor side effects for the freed sub-resources, is outside the evidence (#1/#7). Falsifiable by rerunning the flagged arms on the next engine.
2. **Wall-clock tails**: my null control (n=2/tree interleaved) shows within-tree variance in both trees; envelope equality is not proven for `bus_peak pos_live`, `audio_finish` frames, particles counters. These fields are unpinned; no verdict depends on them (verified: all pins are predicates/substrings).
3. **Unregistered arms**: `r95b env`, `r98b_attack env` are unregistered; the folds do not touch either arm (targets verified by the hunk→func map). `procwait` was the only touched unregistered arm and is closed with byte-identical targeted runs.

## C3 second half — stale citation census (verified, no edits)

Scout census re-run by me at 1392ca21 (command: `grep -o '\.shokunin/game-dev-2d/corpus/' FILE | wc -l`): `SCORECARD.md` **3 occ / lines 8–10** (live depth/coverage/calibration command rows); `corpus/lessons/` **100 files / 736 occ**; `PROVINCE.md` **1 occ** (line 6); `LOG.md` **46 occ** (scout measured 45 at 16:21 — delta = r101-close LOG additions; historical log); `corpus/fixtures/` **0 occ**. Scout's numbers verified except the LOG delta, which is explained, not unexplained. The live form `corpus/fixtures/run_battery.py` exists (527,798 B); I did not run it (hard rule). Repair = text fix, orchestrator-serialized.

## Orchestrator notes (bounded)

- Land all 10 fold sets; **nav: exactly one** of simp1/simp3 (byte-identical).
- r95 fold: land together with `r101-simp3-r95-harness-comment.patch` (stale shas in the harness comment), else the comment lies.
- SIMP-1 §"Landing follow-ups" (sha citations; at current HEAD: canvas/attack at `run_battery.py:1281/1282`, audio at `:1406`; the r95 fixture shas at `:882/885` are covered by the simp3 comment patch) remain orchestrator work; my census adds no new ones.
- After landing, expected battery delta: zero (my 155-row sweep green both trees; SIMP full-battery runs green on folded bytes). The integration battery run remains the orchestrator's, not run here (rule 1).

## Files / receipts

- This shard. Scripts (mine): `reports/round-102/mutations/r102-crit3-{probe,analyze,coverage,focused}.py`.
- Receipts: `/var/tmp/r102-crit3/{receipts-sweep.json (310 launches), focused.json (48), coverage.json, procwait-*.out, pw-{base,folded}-{1,2,3}.out, guard/, sweep.log}`.
- No shared file edited; `run_battery.py` never executed; nothing committed.

## Unknowns / honest limits

- Null-control sample size 2 reps/tree for tails (see residual 2).
- Dynamic (reflective) references guarded only by `call(`/`has_method`/verbatim-token greps; GDScript has no further reflective member access here.
- The stree guard delta is demonstrated on synthetic call sites with the exact wrapper signatures; no in-fixture call site passes a non-bool today.
- All numbers above are observations at the stated load on this host; the pinned-span analysis is mechanical (literal substring positions), not inferred.

— r102 C3-critic, seat output.
