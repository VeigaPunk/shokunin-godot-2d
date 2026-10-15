# game-dev-2d scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → 74/74 PASS; named non-author `corpus/lessons/r49-fresh-after-reconnect-non-author.json`: after late callback reconnection and edge8 release held4/[6]/Value6, fresh focused edge9 left press changes 4→3 with receipts `[6,3]`/Value3; 64 prior tuples unchanged, nine opt-ins stable comparable classifications; author raw separate; work commit cited r49 report | r49 |
| coverage | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → named non-author 96/96 PASS, 85 ordinary+meta rows; `corpus/lessons/r61-crash-non-author.json`: spontaneous SIGABRT −6 with own ERROR marker classifies True under scoped exact-match allowlist, self SIGKILL −9 True unmodified, meta row's four mismatch discriminations + marker-presence all reject. r62: `corpus/lessons/r62-pipe-eof-timeout.md` — descendant-held-pipe TIMEOUT misattribution pinned (hold arm `child_exit_at_timeout=0` + `post_exit_write_captured` reparenting-gated + 7 discriminations; detach control child-exit-bound). All 92 prior records stable on the 7-field tuple; verifier kernel-side ppid-flip trace. r63: `corpus/lessons/r63-signature-spoof-boundary.md` — merged-stream presence-only signature clause pinned as tracked known-accepting forgery boundary (release arm PASS on post-death descendant signature; hold arm rejects via error axis only; 10 discriminations incl. kernel-corroborated write_ppid + withheld-banner anchor; fabricated-ppid slip closed). All 94 prior records stable; verifier 6/6 forgery spot-checks, zero leaks. Work commit `de78edb`; no signal-origin/production claim | r63 |
| calibration | unscored | `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout` → named non-author 81/81 PASS; `corpus/lessons/r56-pushframe-non-author.json`: after push+frame observer3→4/action stays true; after direct clear+next frame observer remains4/action false, numeric3/[6,3]/Value3 and focus/callback stable. All 71 prior tuples and nine opt-ins unchanged; separate fault and two omissions reject early. R55 omit-await ineffective, so no frame-necessity claim. Initial nil-observer author failure, critic wrong guard and verifier setup failures retained adverse; no HSlider internal consumption, OS timing or general provenance claim; work commit cited r56 report | r56 |

planned: r64 (devin, ADMIT) — while-live signature gate tracked (poll()-gated read rejects forged post-death markers; primitive load-bearing; live-window forge defeated-by-construction). Next: forged-rejection dual (XConnector Arm 1 — post-death un-allowlisted ERROR: converts PASS→FAIL), stall-knee margins, kill(0)-trap lint. Prior: r63 (devin, ADMIT) — signature-spoof forgery boundary tracked (release forged PASS + hold forged-TIMEOUT; 10 discriminations; kernel ppid corroboration). Next: boundary-measured surfaces — transitive-depth forgery (depth-agnostic), startup-knee stochastic band (7.55–7.65@8s, size margins ≤7.4/≥7.9), while-live marker gate (XConnector proposal from 3d), zombie persistence; runner --runs relative-path trap (from 3d r72 verifier). Prior: r62 tracked pipe-EOF descendant-timeout surface (hold/detach arms + meta discriminations, reparenting-gated post-exit write); 94/94 non-author verified. Prior: r61 tracked spontaneous-crash classification: crash_spontaneous_sigabrt (−6 + exact ERROR-marker allowlist) + crash_self_sigkill (−9) CASES rows and meta probe_spontaneous_crash_classification (4 rejection discriminations + marker-presence clause, critic-driven); 92/92 verified non-author. Next: boundary-probed candidates — tree-timeout is a pipe-EOF wait misattributed to child liveness (no process-group kill, descendant orphans), startup-margin knee ∈(7.5,7.6]s under bound 8; port of 3d's tree-timeout mechanism is a proposed sibling import; other diagnostic shapes unprobed. Coverage: production-project launch, GUI/rendering, and other platforms remain unprobed. The relative-export-target failure is causally reproduced and both fixture export targets normalized at r25; historical r16/r20/r24 adverse and first r25 49/50 remain recorded, with production/general export reliability unproven.
retired: none.


## Round 64 verdict — 2026-10-14

| axis | Sol verdict | evidence |
|---|---|---|
| depth | **improved locally** | forgery boundary gains its measured dual: `probe_while_live_signature_gate` (selectors/os.read + poll() at marker-completing read) rejects forged post-death markers (release×3 + hold, ~32ms post-death) while accepting genuine/detach (+66–71ms margin); primitive load-bearing — kill(pid,0) false-accepts through zombie window (critic 13/13, scribe 29/29, boundary 6/6, verifier 3/3; window quantified 2.35–2.42s drain vs 1–4ms gate); death-ordering relaxed `<`→`<=` (sub-tick forgers); live-window forge defeats gate by construction (6/6 verifier, 29/29 critic) — post-death origin, not authorship; stall knee ~0.65s. |
| coverage | **improved locally** | 96→97 rows; new measured edge families: zombie-window widths, stderr-forge parity, 24-hog load resilience, pre-death forge. |
| calibration | **unchanged** | gate is an observation path; bound 3.0s inside established margins; thresholds untouched. |

Non-author `reports/round-64/r64-verifier.md`: claims 2/3/4a/4b AGREE; claims 1+5 DISAGREE-as-worded on pre-fix commit `a32920b` (runner diff left uncommitted — adjudicator's integration defect); resolved by follow-up commit landing the verified blob `66a18a00` byte-identical. Sol `r64-adjudicator.md` admits no demonstrated scoped harm post-fix. Bounded: Linux headless Godot 4.7.2, CPython subprocess semantics, subreaper host; observation-order not authorship; the r63 documented-accepting boundary is unchanged policy. Work commits `a32920b` + `5265da6`; report-last commit follows.

## Round 65 verdict — 2026-10-14

| axis | Sol verdict | evidence |
|---|---|---|
| depth | **improved locally** | forged-REJECTION dual of r63 pinned: reparent-gated descendant's post-death un-allowlisted `ERROR:` flips a clean exit-0/signature-present record to FAIL on classification-identical fields; counterfactual strip = sole cause; hold arm double-axis (`hold_timeout_alone_rejects`); kernel ppid corroborated; 29 discriminations all True. |
| coverage | **improved locally** | new measured shapes: quiet zero-provenance forged FAIL, stderr-forge parity, withhold dual-marker batch, gated dual-marker timing split (forged errors only post-death / genuine only while-live), stream-blindness of merged vs stderr-only classify_streams asymmetry. |
| calibration | **unchanged** | observation-path documentation only; classifiers untouched; same bounds. |

Non-author `reports/round-65/r65-verifier.md`: **AGREE 6/6** — 87/87 committed-state replay, 29/29 discriminations, 97 prior rows 0-mismatch on 7-field tuples, own `/proc` corroboration. Sol `r65-adjudicator.md` admits no demonstrated scoped harm. Critic bounds absorbed: capture-before-pipe-EOF is the operative precondition; merged concat is not line-faithful. Bounded: Godot 4.7.2 headless, CPython POSIX subprocess semantics, this host's subreaper/margins; origin not authorship; live-window error forge open. Work commit `414eb8e`; report-last commit follows.

## Round 66 verdict — 2026-10-14

| axis | Sol verdict | evidence |
|---|---|---|
| coverage | **improved locally** | Rejection-clause surface mapped at receipt level: clause inventory (line-scan + 2 allowlist-immune blob conjuncts), allowlist preemptor bound (F/T/F × 3 entry shapes), evasion boundary set (all splitlines boundaries + `\x1f`), seam-fabrication geometry, dead-entry census (0/40 in-run; 6 static dead surfaces with file:line). |
| depth | **improved locally** | Forgery works in three directions: evasion, fabrication (both clauses incl. signature dual — forged PASS no process emitted), denial-of-verdict (`\xff`→`UnicodeDecodeError`); composite single-writer split+phantom; `classify_process`/`classify_streams` divergence documented. |
| calibration | **unchanged** | additive meta probe + fixture arms; verdict logic untouched except warranted `reparent_gate` dedup (byte-identical argv proven). |

Sol `r66-adjudicator.md`: seamforge reproduced directly (fabricated `ERROR:` line from split-stream bytes, exit-0 + genuine signature); independent full-battery replay 88/88 PASS incl. `error-clause surface meta`. Non-author verifier pending at write (rate-limit respawn in flight). Bounded: Godot 4.7.2 headless this host; census "reachable" bounded to shipped fixtures; DoV is decode-bound (`text=True`). Work commit `cb84d0a`; report-last commit follows.

## Round 67 verdict — 2026-10-14

| axis | Sol verdict | evidence |
|---|---|---|
| depth | **improved locally** | `classify_streams`↔`classify_process` divergence mapped as enumerated four-family table (12/27 divergent, rep-stable): absorb / strict×4 / seam×allowlist / agree; shipped `--probe-stream-attribution` reject arm itself diverges (T/F — latent since r19); signature channel-pin + seam-position bound (stdout-tail\|stderr-head only) measured. |
| coverage | **improved locally** | `streamdiv_*` meta arm: 7 real-Godot + 6 allowlist reclass + pair dual = 20 discriminations all true; 9-row divergence_table; opt-in flag only, default path untouched. |
| calibration | **unchanged** | additive probe; classifiers byte-identical (three seats, AST + sha); prior 88 rows stable. |

Sol `r67-adjudicator.md`: adjudicator replay — flagless 88/88, flagged 89/89, discriminations 20/20, table 9/9. Non-author `r67-verifier.md`: **AGREE 5/5** on `9e946c9`. Bounded: classifier-level verdicts, Godot 4.7.2 headless, CPython POSIX pipes, this host; divergence latent in default battery. Work commits `d44ba86` + `9e946c9` (sd_sig_head load-bearing pin); report-last commit follows.

## Round 68 verdict — 2026-10-14

| axis | Sol verdict | evidence |
|---|---|---|
| depth | **improved locally** | Fabrication-window bound measured strictly: write-position space [0,gap), nominal offsets {0–198} fabricate / transition 198.05–198.35 / ≥198.5 never; three regimes pinned (miss = standalone ERROR + intact sig; in-window = fused line + destroyed sig; straddle H-E-T-E2); spawn-latency floor + ppid crossover ~250–260ms; TIMEOUT truncation nondeterminism + duplicate-write splice edges (boundary). |
| coverage | **improved locally** | `--probe-midlineforge-ladder` meta (6 offsets × 3 reps, 8 discriminations); `divergent_clause` per-row clause attribution (exact 9-row map incl. multi-clause seam_script); `raw_*_sha256` same-input gate on 24 dual records; discriminations 20→24 all True. |
| calibration | **unchanged** | opt-in flags only; flagless 88/88 unchanged; classifiers byte-identical since r65; bare midlineforge arm unchanged (default offset stays 80). |

Sol `r68-adjudicator.md`: declared-grid claim falsified as written (~80× resolution overstated — critic) and recorded honestly; the measured bound (write-lands-between-flushes; nominal edge = gap − spawn overhead) is what landed. Non-author `r68-verifier.md`: **AGREE 5/5** on `f754546` — 18/18 grid exact, from-spec clause recompute 9/9, 24/24 discriminations, prior 0-mismatch ×5. Bounded: nominal-offset space on this host (edge ≈198.3–198.5ms stochastic ~1ms); receipt fields bind decoded text; timeout records nondeterministic. Work commit `f754546`; report-last commit follows.

## Round 69 verdict — 2026-10-14

| axis | Sol verdict | evidence |
|---|---|---|
| depth | **improved locally** | Fabrication-window REFERENT pinned gap-relative: splice iff write pos in [0,gap) — r68's ~198ms edge shown to be `gap − spawn_overhead`, not a constant. Crossed cells (300,400)/(300,800)/(600,800) in the tracked ladder refute any absolute edge <~602ms; edge re-located ~295–300 at gap=300; jitter floor ~2–5ms; knife-edge miss<=81/mixed82/fab>=83 (boundary). |
| coverage | **improved locally** | `--probe-midlineforge-gapladder` meta (8 cells x 3 reps, 12 discriminations, referent_verdict 3-way); `raw_merged_sha256` on all dual_classify records + same-input gate (concat-order binding; additive-only, verifier-confirmed equal to sha(so+se) on every record). |
| calibration | **unchanged** | opt-in flag only; flagless 88/88 + surface 34/34 unchanged; classifiers byte-identical since r65; default arm (gap=200) byte-stable. |

Sol `r69-adjudicator.md`: declared claim CONFIRMED in measured semantics — the critic's grid-power falsification corrected the DESIGN (crossed cells folded into the tracked ladder), not the conclusion. Non-author: verifier seat lost to free-model rate limits; operator adjudicator replay on `ec2cda6` = 88/88 + gapladder PASS + referent gap_relative; reviewer + scribe + boundary independent replays all green. Bounded: classifier-level verdicts, Godot 4.7.2 headless, CPython POSIX pipes, this host — referent portable, nominal edges not. Work commit `ec2cda6`; report-last commit follows.

## Round 70 verdict — 2026-10-14

| axis | Sol verdict | evidence |
|---|---|---|
| coverage | **improved locally** | first non-Godot runtime in lane: LOVE 11.5 headless fixture + sibling battery, 15 pinned cases green |
| depth | **improved locally** | honest falsification landed: fabrication window is Godot-runner plumbing, NOT engine-general — narrows the r66-r69 model's scope correctly; +uncapped-cadence + os.execute-shape facts |
| calibration | **unchanged** | sibling runner only; run_battery.py untouched, prior rows byte-stable by construction |

Sol (provisional): ADMIT-with-falsification — claim refuted at the engine layer, recorded honestly. Author=operator-substituted (massacre). Verifier pending post-reset. Bounded: LOVE 11.5 headless, this host.

## Round 71 verdict — 2026-10-14

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | THIRD 2D runtime (pygame 2.6.1/SDL 2.32.72) headless — 36-case pinned battery; sibling runner convention extends cleanly to a non-engine runtime |
| depth | **improved** | withholding-window bound corrected to io.DEFAULT_BUFFER_SIZE=131072 (3.14) with compound 2-layer semantics; critic's stale-8KB falsification + load-fragility audit folded |
| calibration | **unchanged** | sibling runner only; Godot/LOVE batteries byte-stable by construction |
## Round 72 verdict — 2026-11-01

| axis | verdict | evidence |
|---|---|---|
| depth | **improved** | reorder fabrication CONFIRMED and correctly attributed: variable = fd1-OWNER's stdio mode (critic F1 referent correction — brief's "buffered child" was wrong); topology family {prefix,infix,midline,append}; window = buffer lifetime not wall-time; mechanism libc/CPython-general (byte-equal on bare python3 and in-pygame) |
| coverage | **improved locally** | `reorder_*` arm family (5 owner-mode cells) + `reorder_self` + `RAW_CASES` raw-wire predicate (new case class — parser-hazard pinned: REORDER-CHILD precedes REORDER-HEAD in captured stream); 55/55 |
| calibration | **unchanged** | insertion-only (+171/−0); prior 36 cases byte-stable; env hygiene hardened (PYTHONUNBUFFERED popped probe-side, env=CHILD_ENV on all children — folds r71 verifier defect) |

Sol `r72-adjudicator.md`: ADMIT — composition CONFIRMED with corrected referent; verifier AGREE 5/5 on `fee5563` (55/55 ×3 + PYTHONUNBUFFERED sweep + 7/7 independent); baseline zero-drift on freeze `44127af` across all 5 battery families. Bounded: CPython 3.14.7 block-buffering (131072), pipe capture regime (fd1_isatty recorded), this host. Work commit `fee5563`; report-last commit follows.

## Round 73 verdict — 2026-11-01

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | topology set closed: {prefix, infix, midline, append} all pinned + fd2-merge inversion; Node.js v24.21.0 joined as 4th owner runtime (3rd 2D-adjacent); node-absent honest-blocked gate |
| depth | **improved** | third withholding layer measured (libuv event-loop queue past libc/Python buffers); infix = flush-epoch constant not a band; detach-EOF harness-integrity cell pinned |
| calibration | **unchanged** | insertion-only (+165/-0 probe, +146/-17 battery removing only the r72 classifier block); 55 prior cases byte-stable; 80/80 x4 reps |

Sol `r73-adjudicator.md`: ADMIT — topology depth pinned, non-Python census confirms splice/infix predictions. Verifier AGREE 10/10 on `43bef2d`. Bounded: CPython 3.14.7, Node v24.21.0, this host.
## Round 74 verdict — 2026-10-14

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | interior-write lattice — love.physics callback mutation classes measured inside the tracked battery (18 IW cells + love_phys_probe fixture); Box2D callback surface now pinned {refused,deferred,fatal,applied} with endContact joined |
| depth | **improved** | fatal partitioned into fatal(lua) vs SIGABRT-died (critic C2 fold); re-entrancy defeats IsLocked (nested world:update applies a refused write); destroy drain located inside the update epilogue (reviewer D1); carried fifo-SIGTERM-immune guard falsified for LOVE (EINTR) — second wave running a guard needed narrowing |
| calibration | **unchanged** | insertion-only +292/-0; 19 prior rows byte-identical; concat iw receipts 58af4e7e across 6 independent runs; simplifier fold byte-proven |

Sol `r74-adjudicator.md`: ADMIT-corr — partition confirmed, class names scoped, two additive cells deferred to r75 frontier. Recovery wave (gen-1 seats died 16:10Z). Verifier AGREE 13/13 on `ae6cb16`; baseline zero-drift on freeze `1275746`. Bounded: LOVE 11.5-3/LuaJIT, this host. Work commit `ae6cb16` + folds `35dcbf7`; report-last commit follows.
## Round 75 verdict — 2026-10-14

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | 7 new cells: joints surface (newDistanceJoint refused / joint:destroy deferred), setfilter applied with refilter-tunneling witness, preSolve return (ignored class), update-level containment (refused_abort class), unp twins complete the C1 pair |
| depth | **improved** | 2 new classes admitted (refused_abort — step abort + transient lock + collateral exterior refusal; ignored — return value unconsumed, impulse measured landing); esc_fn which-call-threw witness pinned; containment axis proven byte-inert for non-throwing writes |
| calibration | **improved** | F2 gate defect corrected (presence -> value); arm identity pinned (fire.kind x21 + mode=unp); collateral witness pinned; per-cell rc persisted; insertion-only still (prior rows byte-identical modulo declared unpinned traceback lines + mode=unp) |

Sol `r75-adjudicator.md`: ADMIT-corr — deferred/uncontained partition confirmed at byte level, two new classes with full witness sets, F2 gate defect folded. Verifier AGREE 18/18 on `2e3ae8e`; baseline zero-drift. Bounded: LOVE 11.5-3/LuaJIT, this host. Work `2e3ae8e` + folds `be79ad1`.
## Round 76 verdict — 2026-10-14

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | 5 new cells: drain-deferral hazard (bc_draindefer), world-destroy + double-destroy edges (bc_worlddestroy/bc_destroy2), joint drain observer (bc_jwatch), per-contact retfalse (pre_retfalse1) |
| depth | **improved** | new class deferred_abort (accepted write + abort; drain catches up one step late — third abort-adjacent class); world:destroy deferral + next-access death measured; drain bounded inside step-73 epilogue (jwlive->jdrain); retfalse inertness proven at 3-granularity control |
| calibration | **improved** | abort_w single-sources the abort witness; latent fail-open closed (abortq.b1pos); stale enumeration replaced by authority pointer; drain-point overclaim scoped (window measured / line inferred) |

Sol `r76-adjudicator.md`: ADMIT-corr — deferred_abort admitted, destroy-edge lifecycle split, drain bound measured, retfalse refuted at every granularity. Verifier AGREE all claims on `6ca715d`; baseline zero-drift. Bounded: LOVE 11.5/LuaJIT, this host. Work `6ca715d` + folds `c8fa307`.

| r77 | game-dev-2d | release/callback-swap/drain-EC lattice | ADMIT-corr | 62201e5 + d48e0fd |
## Round 78 verdict — 2026-10-14

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | 17 new cells on the nested world:update surface: e_locked cleared by inner epilogue, inner-drain ownership, Memoizer dispatch escape, body-drain-EC nested SIGSEGV, zombie-contact silent UAF, livelock/drain_converge |
| depth | **improved** | drain provenance now required (own/own_n); corrupt gate keyed on drain-origin not depth; drain_converge requires real drain identity (R78-DRAIN- error + aborts>=1 + drain_n>=1) |
| calibration | **improved** | simplifier P1-P4 byte-identical (-1181 B); r78_dead string-truthiness defect corrected; r77 inert D2 conjunct recorded |

`swe-2/sol` `r78-adjudicator.md`: ADMIT-corr — nested-update surface admitted with fold corrections; verifier AGREE (labrat), baseline zero-drift. Bounded: LOVE 11.5/LuaJIT, this host. Work `1a03b7a` + folds `1fde57d`.

| r78 | game-dev-2d | nested world:update damage surface | ADMIT-corr | 1a03b7a + 1fde57d |

## Round 79 verdict — 2026-10-15

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | 23 new CASES rows arm the Godot-4 2D physics-events table on `phys2d_events.gd` (contact-monitor on/off/max0 lattice, in-cb write/deferred-write/queue_free/free_rid/direct-dss surface, Area2D twins); shared battery 88→111 rows, 111/111 ×3; zero-drift 0 tuple mismatches on all 88 prior rows ×2 baseline reps, only meta delta is `probe_error_clause_surface`'s own census (39→43 rows, 41→53 error lines, 34/34 discriminations true); fixture sha `7329acb2` = scout-pinned probe, 23/23 CASES rows + 4/4 expected_errors identical to `author-rows.py.txt`. |
| depth | **improved** | C1 live-proven mechanism-blind muted pins killed: `cm_off`/`cm_max0` emitted all-`-` cb_* fields and a `contact_monitor=false` fixture produced the byte-exact pinned `cm_max0` signature without exercising `max_contacts_reported`; fold appends `post_monitor`/`post_max` readbacks (off false/4, max0 true/0), forge replay fails closed. Record corrections: P1 falsified (`cb1_colliders=1` under two overlapping floors is a dispatch-order snapshot, not a count invariant; `colliders_2=2` measured), P2 partial-falsification (`set_deferred` lands durably and reaches the server — same-frame visibility, not a window-scoped revert), P3 new member (immediate `free()` in-cb = refused member). |
| calibration | **improved** | C2 `phys2d_expected_errors_all_matched` floor gate added to `sf_discriminations` (every allowlist entry must match a real emitted line); P5 `love.errorhandler` level-2 guard closes the stray-invocation window (no conf can open a desktop window); verifier F2 hold-arm starvation ordering noted, not folded; scribe results-order root cause named; results-order self-infliction repaired and re-verified. |

`r79-adjudicator.md` (swe-2 finisher lane; Sol author lane died on rate limit mid-run, landing byte-exact vs the scout-pinned probe): ADMIT-corr — 111/111 ×3, forged-signature mutant killed, CASES-row deletion flips only that row, 8s detached-descendant razor held under 20-spinner load. Non-author `reports/round-79/r79-verifier.md` (zfl/mutation): all five dispatch probes + five boundary probes executed with receipts, 10/10 PASS, no cell pin refuted; re-derived 0/111 tuple mismatches vs author runA, 104/104 output-identical. Bounded: C3 substring-not-line signature matching is a harness-wide judge tradeoff; foreign-space dss coverage measured (B4: sees own space only) but not armed; threaded-twin arm evidence-only; host Godot `4.7.2.stable.arch_linux.ed1daf0bf` headless, LÖVE 11.5, Python 3.14.7; SCORECARD.md foreign-fleet edit held out at close (since reconciled, `fad0b1e` restored the tracked ledger). Work+fold `f777925`; report-last `d9320dd`.

## Round 80 verdict — 2026-10-15

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | 28-row `phys2d_motion` battery (CCD ladder/edge/gap/spin; `body_test_motion`/`move_and_collide`/`test_move` family incl. from-default, embed, recovery_as_collision, chain, decomposed; `PhysicsDirectSpaceState2D`/body-state read arms incl. purity/wrongarg/windows; contact-window/persist/cap cells); battery 111→139 rows, author 139/139 ×2, verifier 139/139 ×2 tuple-identical; prior-row identity 110/111 byte-identical tuples, single delta = `probe_error_clause_surface` census (43→45 rows, 53→61 ERROR lines). |
| depth | **improved** | C2 positive wall witness folded: `ccd_edge` `w[...]` `body_test_motion` witness into the wall face pinned (`hit=true pt=(98,805) cls=StaticBody2D`), `collision_layer=0` dead-wall forge now fails; C3 advisory recorded (`ccd_spin` weak cell, blind to its own witness channel; `bx_spin_clean`/`bx_cs_geom`/`bx_from_rec`/`bx_rec_edge` spec'd exec-ready for the next round); `cast_shape`≡`disabled` and `recovery_as_collision` inertness are this-geometry measurements. |
| calibration | **improved** | C1 floor-gate scope: dead-entry forge demonstrated live pre-fold (`dead_entry_count=1` sailed through the `phys2d_events_`-scoped gate) → gate now `startswith("phys2d_")`, motion rows covered; simplifier vfold 879→774 (−208/+103), 139/139 both sides, 0 tuple diffs; scribe F1–F7 record corrections absorbed; forges killed (token flip, row deletion 138/138 clean, arm neuter). |

`r80-adjudicator.md` (swe-2): ADMIT-corr — motion/query lattice admitted with content-verified pins, a positive-witness edge cell, and a floor-verified error allowlist. Non-author `reports/round-80/r80-verifier.md` (swe-2): independent 139/139 ×2 with rep1↔rep2 tuple-identical on all 139 rows, prior-111 rows vs freeze 110 identical + 1 explained delta, forges killed, 2 new `expected_errors` floor-verified. Bounded: `ccd_spin` stays weak-labeled (boundary arms queued to strengthen or kill); threaded twin divergence named (`bds_windows` proc-gate); inertness/`cast_shape` claims scoped to this fixture geometry; host Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python 3.14.7; SCORECARD.md foreign edit held out at close (since reconciled, `fad0b1e`). Work+fold `f27f952`; LOG `27f465c`.

## Round 81 verdict — 2026-10-15

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | 20 `phys2d_joints` cells + 4 `expected_errors` (joint census/refusals, pin tiers/clear/freed-RID, spring envelope, groove conventions, disable_collisions, layer/mask OR-table + zero edges + dyn pair + mid-step flips, Area2D gates, entry order); insertion-only +68 → 159 rows; author 159/159 ×2 with zero prior-139 drift; verifier 159/159 ×2 independent, prior-139 stable (45→49 census explained); 20/20 new rows byte-stable across reps. |
| depth | **improved** | C1 claim-refuting correction: node vs server pins are bit-identical at equal position — the divergence is the 2000 px lane offset (y-gradient), n2 control pins it; C8: freed-RID `joint_make_pin` is silently refused (`type=0` collides with JOINT_TYPE_PIN; `bias_remade=-1.0` pins the measured fact); boundary B1 crash class (`joint_make_pin` body_b=RID() → SIGSEGV at first step, no cell affected), B9 (freed joint RID never recycled in 64 allocs); 10 witness emissions added in fold. |
| calibration | **improved** | Fold resolves critic C1–C11 (18 PASS-forges found, 4 end-to-end), 10 rows re-pinned; B2 wording bounded (`layer_flip_cb` "not gated" scoped to collision_mask writes — `Area2D.monitoring` IS refused in-callback); simplifier vfold 973→919, 20/20 byte-exact, negative controls N1/N2 recorded (registries stay); F7 restated (`update_scripts_classes` 30→31 = "one more script"); boundary 11 named classes, none falsified. |

`r81-adjudicator.md` (swe-2): ADMIT-corr — the joints + layer/mask lattice is admitted after the fold corrected one claim-refuting finding and added 10 witness emissions. Non-author `reports/round-81/r81-verifier.md` (zfl): CONFIRM — 159/159 ×2 independent, prior-139 stable, 20 new rows byte-stable, one-line mechanism kill fails the row and the battery with zero collateral, 49-entry `expected_errors` census fully live; recommendation admit. Bounded: B1 crash class recorded (no cell affected); SCORECARD.md foreign edit held out (since reconciled, `fad0b1e`); `camera_proc.gd`/r85-author artifacts held out (r85's, fold next); host Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python 3.14.7. Work+fold `5ab058b`; LOG `71405b2`.

## Round 85 verdict — 2026-10-15

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | 15-row camera/canvas transform lattice in `camera_proc.gd` (+5 non-pinned diag arms): composition law, zoom-center anchoring, write-timing visibility ladder, 1/60 subpixel steps, four transform spaces, CanvasLayer stack/follow/draw-order, SubViewport world isolation + render-independence, ParallaxLayer/Parallax2D/ParallaxBackground splits, parallax phase timing; +15 battery rows → 174; author 20/20 standalone + 174/174 rehearsal; verifier 174/174 ×2, prior-159 zero drift, forge-kill live; folded bytes 174/174 (`r85-foldc-final2`). |
| depth | **improved** | C1–C7 all additive and landed: draworder hidden-tag queued/in/vis witnesses, `vp_indep` camera+cl readbacks, cl in-tree pins, par_2d rep/fv/so/ign readbacks, par_layer in-row mm/mo, `cam_comp` second-config comp4 witness, `sub_dev` %.9f (deviation 6.104e-6 kills the "exact −0.025" 4dp launder); F5 narrows the "camera writes cached" headline — zoom/offset/anchor/limit writes are live via `_update_scroll()`, only transform writes defer to the visibility ladder. |
| calibration | **improved** | 8 rows re-pinned under battery context (scratch viewport 64×64 ≠ 720×450 direct); F5/F2 wording narrowed; critic 7 counterexamples all resolvable by additive witnesses (C1–C7, table in `r85-fold.md`), no claim-refuting finding; simplifier not dispatched (new-file fixture); 13 remaining edge classes bounded. |

`r85-adjudicator.md` (swe-2): ADMIT-corr — 15-row lattice admitted, C1–C7 corrections applied in fold and verified live, final folded bytes 174/174. Non-author `reports/round-85/r85-verifier.md` (zfl, pre-correction build): two fresh 174/174, exact 15-row pin equality, prior-159 zero drift, forge-kill live → ADMIT recommended. Bounded: boundary's 13 remaining edge classes (smoothing `speed*delta` divergence/NaN, empty/inverted limit → midpoint clamp, zoom `is_zero_approx` floor with INF/NAN degenerate transforms, stateful drag, parallax zoom/parentage variance, physics-interp timing); host Godot `4.7.2.stable` arch_linux headless, scratch project viewport 64×64; SCORECARD.md foreign edit held out at close (since reconciled, `fad0b1e`). Work `45232c7` + fold `76fa8d8`; LOG `71e3861`.

## Round 86 verdict — 2026-10-15

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | `phys2d_backends.gd` — nested-boot engine/backend-select lattice, 8 arms: class/property census, stored-value→resolved-backend lattice (6 cells incl. silent verbatim-store fallback on garbage/empty), Jolt-is-3D-only positive control, manager refusal cross-check (2D/3D split on identical name lists), threaded space-state gate matrix (7 positions + fetch-free baseline), property-vs-explicit gate duality, Dummy degenerate-query payloads, Dummy collider-access hang (external-bound timeout class); +8 battery rows → 182; 182/182 PASS on folded bytes (`20261015T160405358447Z`). |
| depth | **improved** | New latent bimodality discovered in-session and enveloped: gate deferred-fetch can land inside the threaded physics window (`dual_ok`/`thr_ok` mode envelopes); `moved` frame-count coupling → `mv=pos|zero` class; `dur_ms` jitter → `dur_ge` threshold — honest mode admission, not a deterministic re-pin; r77's falsified law corrected (property-vs-explicit gate duality); boundary B4 new class (gate is a GodotPhysics-server property — vacuous under Dummy). |
| calibration | **improved** | Critic 16/18 PASS-forges corrected: `dur_ge` timing pin, backtrace-frame provenance (`tf`/`df`/`pf`/`af`), `cm0/cm1` fraction pins, child-side `offered` lists + `errs_total`, `errB` symmetry, `thr` stimulus pin, `_boot` stale-capture purge + exec-failure class, `enum%d` real count, `stored_has` presence flag; 8 rows repinned ×3 stable; simplifier vfold −4L applied, 16/16 byte-identical pairs; forge-kill re-armed (f09/f14-class now requires real paths); scribe F1–F6 non-blocking. |

`r86-adjudicator.md` (swe-2): ADMIT-corr — all eight seat reports on record, corrections folded in-session. Non-author `reports/round-86/r86-verifier.md` (swe): ADMIT — 182/182 ×2 fresh own-process runs (author receipt not trusted), prior-174 rows 0 field mismatches, forge-kill PASS both directions, arm-level claims PASS; 24-rep stability pre-fold, 8 arms ×3 stable post-fold. Bounded: B4 vacuous-pin hazard recorded; B8–B14 armed-unrun filed for a future exec-capable seat; host Godot `4.7.2.stable.arch_linux.ed1daf0bf` headless, Python 3.14.7; SCORECARD.md foreign-fleet rubric edit held out at close (since reconciled, `fad0b1e`). Work `7ae7083` + fold `01dd32b`.

## Round 87 verdict — 2026-10-15

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | 25 new CASES rows arm the Input/InputMap/InputEventAction lattice (`input_lattice.gd` 854->833 lines post-simplifier + `r87_edge.gd` + `ei_bound.gd`): registration/binding, key/joypad/joypad-motion/mouse surfaces, action_press/release/strength/raw_strength, exact_match modifier+direction split, deadzone ladder, device-bank writes, event_index>=32 typed refusal, null/never-registered refusal surface; battery 182->207, 207/207 PASS on admitted bytes x3 independent seats. |
| depth | **improved** | just_* pulse mechanism closed: arms exactly one physics step, flake selector `inter==0 <=> jp==1` reproducible 300/300; pre_frame/press_phys/release_edge/ui_ns true-bimodal -> honest mode envelopes; api_press falsification found in-session (alt mode 27/30 under load) and enveloped; `InputEventAction` name-only matching + explicit-action-binding inertness measured; event_index bound + null-surface refusal classes pinned. |
| calibration | **improved** | Floor gate widened post-fold (`r87_expected_errors_all_matched`: dead-entry census now covers input_lattice_/r87_edge_/ei_bound — `dead_entry_count=0` live); read-only boundary's `runs/`-absent claim falsified (101/101 verify); author cell count corrected 26->25 on the record; probe sha transition 2b68531d->7624aa97 documented; simplifier SP1-7 byte-identical deletions folded. |

`r87-adjudicator.md` (orchestrator): ADMIT-corr — twelve seat reports on record; critic F1 folded (api_press 2-payload envelope), floor gate widened, simplifier deletions proven. Non-author verification: `r87-verifier.md` AGREE 4/4 on frozen `ebcf2bb` (207/207 x2); `r87-verifier2.md` VERIFIED on folded `7ef247c` (207/207, alt-mode 22/24 under load); `r87-critic2.md` independent replay 207/207 byte-identical. Deferred: reviewer F1 tuple-signature TypeError (latent, unreachable), F2 engine-encoded eng=/joys= pins. Bounded: envelope any() admits mode-flip between whitelisted payloads; no off-host/gamepad/non-headless rep; pre_frame >=2-tick mode unobserved; host Godot 4.7.2.stable.arch_linux headless, Python 3.14.7. Work `ebcf2bb` + fold `7ef247c`; record `337407e` + this commit.
| r88 | improved | improved | improved | mp offline/loopback/spawner rows + light/occluder/sprite/headless-null-audio/vis surfaces (8 rows, 207->215); BLOCKER folded: pid ports + rc guards, race-sync pins, crossing ray, play() assert, phys_peer 6-envelope incl. new delta=5 mode; VERIFIED-WITH-RESERVATIONS on folded bytes (verifier-r2, 215/215 under load) |
