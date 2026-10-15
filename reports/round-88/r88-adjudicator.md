# r88 adjudicator — multiplayer / headless-boundary surfaces (orchestrator seat)

## Verdict: **ADMIT-corr**

Round 88 adds eight `r88_surfaces_*` rows (207→215) covering ENet
multiplayer (offline/loopback/spawner loopback), 2D lighting +
occluder, sprite metadata/physics, headless-null audio position,
and visibility-notifier surfaces — plus a required correction fold.
The round carried the fleet's first **seat-level BLOCKER** (critic F1)
through to a verified resolution.

## Seat ledger (13 reports on record)

| seat | verdict | commit |
|---|---|---|
| scout (r88 census) | surfaces ranked | prior wave |
| author | 8 rows additive, 215 green ×2 | `3c47eee` + `f9e8a5b` |
| baseline | 207/207 frozen; 2 named flakes | `aba4d7a` |
| boundary | playing=false pin FALSIFIED; Case A/B race; MP same-port class | `d3e16fb` |
| critic | **BLOCKER** F1 hardcoded ports → cross-connect-PASS; F2–F5 | `df9dd62` |
| reviewer | CHANGES — F1 HIGH race-pinned positions confirmed (7/7 Case A) | `9697494` |
| simplifier | 2 proven deletions (uping, _body 2-arg) | `3908299` |
| verifier | VERIFIED w/ reservation — F1 fired live (foreign server on 41778) | `0628932` |
| scribe | custody clean; open item = bimodal pins | `6ce55dd` |
| fold | all 6 corrections; new delta=5 phys_peer mode | `fd59c11` |
| verifier-r2 | VERIFIED-WITH-RESERVATIONS on folded bytes | `6864919` |
| adjudicator | this report | this commit |

## Corrections admitted into the fold

1. **F1 (blocker)** — pid-derived ports `40000 + pid % 20000`,
   `rc_s`/`rc_c` fail-closed guards. Verifier-r2: 54 concurrent MP
   reps, zero `Couldn't create an ENet host`; negative control
   (pre-bound pid window) → `FAIL server_rc=20`, no PASS line —
   an ENet-create error can no longer silently pass.
2. **F2** — v≠0 startup sync in `sprite_phys`/`light_props`;
   re-measure landed the same pinned values, now mode-invariant
   (52+52 reps across both startup shapes).
3. **F3** — occluder ray rerouted to cross the polygon
   (`(-50,-35)→(50,-35)`); `ray_through_occluder=true` is falsifiable
   (StaticBody2D on the ray hits; occluder-only stays empty).
4. **F4** — `audio_pos` asserts `p.playing` post-`play()`;
   play()-removed twin → `FAIL reason=play_not_accepted` rc=1.
5. **F5** — `input_lattice_phys_peer` → 6-payload envelope
   `ev_step_delta ∈ {0..5}`; fold found a NEW delta=5 mode
   (15/150 hogged reps); verifier-r2 reproduced all six
   ({0:70,1:30,2:17,3:8,4:10,5:5}), no 7th in 140 reps.
6. **SP1/SP2** — proven dead-code deletions applied.

## Correction ledger (claim fixes on the record)

- Scout's `playing=false` negative pin was falsified by boundary
  (playing=true 14/14 immediately post-play; false only ≥f19);
  author's pin samples ≥f19 — kept, mechanism disclosed.
- Author predated the boundary commit and pinned Case-B position
  values of a proven bimodal race — resolved by F2 sync, same
  values re-derived post-sync.
- `audio_bus_route_invalid_control` `advanced=false` load flake
  (pre-existing, non-r88): observed once by fold runs1 and once by
  verifier-r2 rep1 — documented rare environment flake, fails loudly.

## Residual risks (declared, accepted)

- Residual `pid % 20000` port collision would fail loudly by design.
- `phys_peer` delta≥6 theoretically reachable (bounded by
  max_physics_steps_per_frame); unobserved in ~350 reps; a future
  mode fails loudly, never silently.
- Headless-null audio rows measure the *null driver* surface only;
  real-device playback is outside the battery's reach by design.
- Shared-host contention remains the dominant flake source; all
  r88 flakes were named, reproduced, or dispositioned.

## Admission basis

Non-author verification on the actual admitted bytes:
verifier-r2 on `fd59c11` — 215/215 under load, every fold item
independently exercised incl. negative controls. Work `3c47eee`,
fold `fd59c11`, record this commit.
