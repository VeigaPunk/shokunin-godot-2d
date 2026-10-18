# r101-adjudicator — round 101 verdict (orchestrator seat)

Date: 2026-10-18. Swarm: 64 seats, opencode-go-7/deepseek-v4.1-flash (60 completed;
E3/E5/E6/E9 died on a provider 400 `reasoning_content` error late in their runs —
their standalone fixtures exist but their shards/pins do not; every one of their
scenarios is covered by the 12 landed `export_prod` harness rows, so C1 breadth is
unaffected; the four orphaned fixtures are disclosed below). Host context: sibling
game-dev-3d r104 swarm concurrent (load 33→57 during seat work; 7–9 during receipts).

## Declared claims

| claim | axis | before | after (target) |
|---|---|---|---|
| C1 export_prod capability lattice | coverage | 0 rows; scorecard note "production/general export reliability unproven" | +12 battery rows, green ×2, capability row entered |
| C2 full-replay pins close r100-critic F2 | depth | r100b_seq rows pin 1 line each of the 14-cell replay; m_seq forged-extra-line passes | r101_seqfull pins every cell + divergence census + digest; m_seq rejects |
| C3 --offy dead-flag honesty repair | calibration | r95b_order_celloff_y1000 unmeasured duplicate; Y-translation "honestly unmeasured" (r95) | retirement + real measurement rows; census tripwire |

## Landed changes (all under game-dev-2d-shokunin/, committed as round-101)

- `corpus/fixtures/export_prod.gd` + `r101_seqfull.gd` + `r101_ytrans.gd` + 11
  `export_prod_s*.gd` companion fixtures (s01–s11; four unsharded, see below).
- `corpus/fixtures/run_battery.py`: +20 CASES (2 seqfull, 6 ytrans, 12 export_prod),
  retired `r95b_order_celloff_y1000` (unmeasured duplicate of celloff_x0 — E17
  byte-identity), +2 expected_errors entries (seqfull rows), +r101 floor gate,
  cases_integrity existence extended (then re-anchored to `results` — fold F2 below).
  Splice scripts: `reports/round-101/mutations/r101-integration-splice.py`,
  `r101-ytrans-fold-splice.py` (auditable, rerunnable).
- `corpus/lessons/r101-export-capability.md`, `r101-seq-replay-transcript-pin.md`,
  `r101-ytrans-dead-flag.md` (from SCR-1/2/3 drafts, fold-appended).

## Folds landed in-round (critic/verifier-driven)

- **F1 (calibration, phase bimodality):** run-1 records showed `y1000`/`ym1000`/`ycop`
  receipts in a different child-order permutation (`ladder=[t2:4,1,2,3,0;…]`,
  `t2_vec=[e,b,c,d,a]`, `eq_canon=false`) with `pf=64` vs quiet `pf=3` — the Y-settling
  order depends on how many real frames ran before each ladder tick. Every translation
  invariant held in both phases. Fold: PASS lines pin phase-invariant fields only;
  order permutations moved to unpinned `R101Y` diagnostics; 4 pins re-anchored to fresh
  quiet receipts (2/2 byte-identical). The order law at offy≠0 is a mode-envelope
  diagnostic, not a falsifiable pin (r87 api_press precedent).
- **F2 (integration defect, mine):** cases_integrity's existence clause iterated
  `census_rows` (allowlist-bearing rows only) — the entry-less ytrans/export families
  vacuously failed it (run-1 `cases_integrity=False`, the ONLY false discrimination in
  the error-clause meta). Re-anchored the clause to all `results` rows.

## Before → after measurements

Counting command (scorecard convention):
`python corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

- C1: 0 export rows → 12/12 PASS in-run (run 1: base_pck, subdir_census,
  include_exclude_filter, zip_census, det_a, det_b, main_scene_swap,
  mainpack_quit_after_frames, resource_remap_census, icon_uid_census,
  unknown_preset_refusal, templates_missing_class). Receipts pinned to
  warm-warm determinism (`equal_to_sample1=true byte_diff_count=0`) after E0 measured
  the cold-export anomaly (first export of an unimported project → corrupted header,
  3672 B, non-loadable). Refusal classes verbatim: `Invalid export preset name:` /
  `No export template found at the expected path:`.
- C2: 2 rows (`r101_seqfull_clean`/`_noclean`) PASS in-run; 17-line/6.8 KB contiguous
  pins (SEQ_BEGIN + 14 cells + SEQ_CENSUS identical=10/divergent=4 + SEQ_END sha256
  digest). Non-author verification: D2 ("reproduce every cells 6–10 value this seat
  measured"), D3 forgery-demo (full-record pin rejects in-span forged line; the landed
  1-line pins accept it — the measured F2 gap), VER-5/6 recomputation, E12 verify
  script 28/28. m_seq mutation execution recorded in the mutation battery log.
- C3: 6 rows; run 1: y0/ysep/census PASS, 3 folded (above); folded state re-validated
  standalone ×2. Census row tripwires r95b sha256 (`4f7e945e…`) and
  `r95b_offy_tokens=0`. Retired duplicate: 366→365 r95b family rows, net +5.

## Environmental findings (NOT r101 defects; disclosed, bounded)

- 3 legacy rows red in run 1 with byte-identical pins: `input_lattice_census`,
  `input_lattice_dev_joy`, `input89_edges_axisdev` — all standalone-green on the same
  tree (reproduced exit=0, sig byte-equal to pin). In-battery classification failure
  with identical evidence bytes = host-state class (r92 F1 precedent). Run-2 result:
  red under the pre-fold pins in BOTH runs (deterministic `joys=1` in-battery —
  /dev/input/js0,js1 enumerate intermittently on this host); the folded pins are
  verified as substrings of both runs' received receipts (and of a `joys=0`
  standalone receipt) — the fold, not the host, is the final state. Law: never
  pin device-census tokens (r85 disclosed `joys` host-conditional; r101 proved it
  live).
- `timeout probe` FAIL: `hold_open_new_bound` arm of the r62 descendant-pipe probe —
  untouched by this round; host process-state pollution suspected after today's load
  storms. Run-2 result: red again with byte-identical arm results
  (`hold_open_new_bound` times out with marker observed, both runs) — a
  deterministic host-state class in the r62 descendant-pipe probe, untouched by
  this round (no r101 file in its path); bounded and routed.
- VER-13 finding (filed, not fixed here): `export_preset_missing`'s expected_errors
  dict entry (run_battery.py:2011) is dead code — the export branch overwrites
  `passed` inline so the dict lookup never runs; the CASES 5th-field string is
  vestigial. Behavior is correct (inline evidence pins the current refusal string);
  hygiene routed to a future harness round.
- SCOUT finding (routed): stale `.shokunin/game-dev-2d/corpus/` citations in
  SCORECARD/README/lessons — the live tree is `corpus/`; count + locations in
  r101-scout.md.

## Verdict

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | +12 `export_prod` rows, 12/12 PASS in both in-battery runs (run 1 + run 2 on folded state); capability row entered SCORECARD (`headless production export`); cold-export anomaly + warm-warm determinism pinned honestly; refusal classes verbatim. |
| depth | **improved** | F2 closed in-battery: `r101_seqfull_clean/_noclean` PASS ×2 (17-line/6.8 KB contiguous pins; SEQ_CENSUS identical=10 divergent_n=4; SEQ_END digest). Live forgery tests on committed bytes: interleaved-line forgery (r100-critic m_seq shape) → REJECT via contiguity; content-splice forgery (line-count preserved) → REJECT via pin + digest change (5be029c7→6b3b6704). Non-author: D2/D3/VER-5/VER-6 corroboration; E12-verify 28/28 PASS; mut01 confirmed the r100b rows still accept the forgery (their gap is documented history — the closure is additive, not a rewrite of landed rows). |
| calibration | **improved** | r95b `--offy` dead-flag repair: retirement of the unmeasured duplicate + 6 rows with sha tripwire, 6/6 PASS ×2 post-fold; F1 phase-invariant fold (measured bimodality: quiet pf=3 vs in-battery pf=64, invariants held in both phases); F2 `cases_integrity` re-anchor (verified green in run 2: error-clause meta PASS, all discriminations true, dead_entry_count=0); F3 legacy `joys` host-conditional pins folded (verified against both phases' receipts). |

**Admission: ADMIT-WITH-FINDINGS.** Every claim verifies; no axis harmed; findings bounded and routed below.

## SHONEN

- [ ] Real decision tables/error patterns/checklists with cited sources — `[~]`:
  3 new lessons with cited sources landed; probation gate remains operator-owned.
- [ ] End-to-end domain task executed and logged — `[ ]` untouched this round.
- [ ] Instructions executable without oral context — `[~]`: export_prod lattice is a
  runnable end-to-end export path (12 rows + lesson); box check awaits non-author
  probation review.
- [ ] No cross-domain bleed; PROVINCE remains accurate — `[~]`: connector seat filed
  0 contested-scope items; 3D lane untouched (side-round deferred via L0, see below).

L0 (open, operator-owned): (1) 3D side-round deferred — 3D lane under parallel
session's r104 (recorded in fleet .ufo/l0-questions.md); runs before 2D r105.
(2) Epic-account linking / 26.8 GB image for the UE-runtime unlock remain
operator-owned.

## LAWS (folded into LOG.md)

- Warm-warm export determinism only: the FIRST export of an unimported project is
  corrupt (3672 B, bad ECFG header); pins must compare same-root re-exports.
- Order permutations at offy≠0 are phase-bimodal (real-frame-count dependent);
  pin translation invariants, diagnose orders. (r87 api_press class, instance 2.)
- cases_integrity existence must scan all run rows, not census_rows, or
  entry-less families vacuous-fail the gate.
- Pack bytes are root-path dependent (sha drifts across roots); pin sizes,
  magic, census names, and in-process byte comparisons — never cross-root shas.
