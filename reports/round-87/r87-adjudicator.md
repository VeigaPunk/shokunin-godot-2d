# r87 ADJUDICATOR — input event/action lattice

Seat: ADJUDICATOR (orchestrator) | round 87 | work `ebcf2bb` + fold `7ef247c`

## Verdict: ADMIT-corr

Admitted with corrections folded in-session. Twelve seat reports on
record: scout, baseline, boundary (exec) + boundary-readonly, author,
critic, critic2, reviewer, simplifier, verifier, verifier2, scribe.

## What the round measured

`input_lattice.gd` (+ `r87_edge.gd`, `ei_bound.gd`) — the Input /
InputMap / InputEventAction lattice, 25 new CASES rows: input-map
action registration and event binding, key/joypad/joypad-motion/
mouse surfaces, `action_press`/`action_release`/`action_strength`/
`action_raw_strength`, `is_action_just_pressed`/`just_released`
pulse semantics, `exact_match` modifier/direction behavior, deadzone
ladder, device-bank splits, event_index bound (`>=32` typed refusal),
null/never-registered refusal surface. Battery 182 -> 207 rows.

## The boundary law

`just_*` pulses arm for exactly one physics step — the first step
beginning after the state change — and the flake selector is
`interposed-steps==0 <=> jp==1` (idle:physics interleave),
reproducible 300/300. `pre_frame` is genuinely bimodal (23/48 alt);
`press_phys`/`release_edge`/`ui_ns` are two-mode cells. Boundary
corrected the scout's "stable" calls; author authored mode envelopes
with all observed payloads. Read-only boundary's `runs/`-absent claim
was falsified (101/101 files verify).

## Record corrections applied in fold (`7ef247c`)

- Critic F1 (BLOCKER-class): `api_press` is bimodal — release->idle->
  press gap admits an interposed physics step that consumes the
  release pulse (`ph1{...jr=0}`); observed 27/30 under 16-CPU load.
  Folded to a 2-payload envelope per the critic's prescription.
  Verifier2 reproduced the alt mode 22/24 under the falsifying load,
  all PASS through the envelope; critic2 replayed 207/207
  byte-identical and confirmed pre-fold-pin-FAIL vs fold-envelope-PASS
  at the production classifier.
- Floor-gate gap (scribe F3 / reviewer F3 / critic F3, all
  independently): `phys2d_expected_errors_all_matched` was
  prefix-scoped; r87's three new whitelists escaped the dead-entry
  floor. Fold adds `r87_expected_errors_all_matched` covering
  `input_lattice_`/`r87_edge_`/`ei_bound`; verifier2 confirms
  `dead_entry_count=0`, all 36 discriminations green.
- Simplifier SP1–SP7: 21 dead lines in `input_lattice.gd` proven
  byte-identical across interleaved reps; folded (probe sha
  `2b68531d` -> `7624aa97`; comments updated).
- Claim-arithmetic corrections recorded: 25 rows landed
  (19 verbatim + 3 new envelopes + `pre_frame` re-cut in place +
  2 edge), not "26"; scribe F5 citation relabeled.

## Finding dispositions

| finding | disposition |
|---|---|
| critic F1 api_press bimodal | FIXED in fold, verified under load |
| floor-gate prefix gap (F3 x3 seats) | FIXED in fold, green live |
| simplifier SP1-SP7 | FOLDED (byte-identical proof) |
| reviewer F1 tuple-signature TypeError | DEFERRED r88+ — latent, unreachable today (tuple rows ∩ whitelists = ∅); normalize census call or assert isinstance(str) |
| reviewer F2 eng=/joys= engine-encoded pins | NOTED — 20/20 samples stable incl. 8 under load; pin the engine version or drop the tokens |
| scribe F1 author/baseline dirs unmanifested | NOTED — custody convention gap, receipts tracked by git |
| critic F5 press_phys saturated pair | NOTED — <=1-step tail unlisted; envelope admits only observed modes, third modes fail loudly (correct behavior) |
| author "26 cells" / commit msg | RECORD-corrected (25; pre_frame counted once) |
| read-only boundary F2 (`runs/` absent) | FALSIFIED by boundary + scribe — 20 files, 101/101 verify |

## Evidence status

- 207/207 PASS on admitted bytes `7ef247c` — verifier2 battery rep
  (`be5b0222` verdicts sha) + orchestrator fold-check rep + critic2
  independent replay (207/207 byte-identical tuples vs verifier2).
- Non-author verification chain: r87-verifier AGREE 4/4 on frozen
  `ebcf2bb` (207/207 x2); r87-verifier2 VERIFIED on folded `7ef247c`.
  Chain satisfies the non-author requirement on the admitted bytes;
  caveats recorded (single git identity fleet-wide; post-fold
  rep depth 1 seat + critic2 unofficial second).
- Residuals disclosed: envelope `any()` admits mode-flip between
  whitelisted payloads; no off-host/gamepad/non-headless rep;
  `pre_frame` >=2-tick mode unobserved in 53+ cumulative reps;
  shared-host contention windows recorded by baseline.

## Axis calls for SCORECARD

coverage + (25 new cells, Input/InputMap/InputEventAction surface —
largest unmeasured authorability surface on the census), depth +
(flake selector mechanism closed; `exact_match`, device bank,
event_index bound all pinned with refusal classes), calibration +
(floor-gate widened after triple-seat finding; one real falsification
folded; envelope pattern hardened).

## LOG entry

round 87 — input event/action lattice (ADMIT-corr); commits
`ebcf2bb` (work) + `7ef247c` (fold) + this record commit.
