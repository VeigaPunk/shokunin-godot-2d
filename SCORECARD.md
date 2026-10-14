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
