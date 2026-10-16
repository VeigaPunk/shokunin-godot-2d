# Adjudicator report — round 96 (scene_io + r96b lattices)

DECISION: **ADMIT-with-findings** on `89f85ed8`. 60 rows (366->426), +2712/-0
insertion-only across 9 files; CASES 359->419. All five gates landed:
verifier VERIFIED (426/426 on 125,204-file archived tree; 2124/2124
in-signature mutations reject; 57/57 laws re-derived; floor gate proven
load-bearing by gate-mutant battery); critic PASS (426/426 archived,
mutants decisive, uid context-dependence verified both directions);
reviewer PASS (426/426 + 36/36 fresh re-derivation, 6 forgery shapes
reject 60/60); scribe custody HOLDS (all byte-pins match, receipts
resolve, only declared files touched); simplifier PROVEN-LEAN (-55 lines
/ 33 sites across 6 fixtures proven by 264 fresh launches — queued, not
landed).

Encodings that survived: scene_io lattice (13 arms), r96b six-fixture
boundary lattice, 16-entry expected-error allowlist all live-matched,
uid_cache fold (deterministic iff .godot/uid_cache.bin exists —
context-dependence proven both directions by two seats).

Fold queue:
1. **Simplifier -55 fold** (six fixtures; 0 masked diffs over 264
   launches): scene_io -12, r96b_cache -21, r96b_id -4, r96b_var -12,
   r96b_seed -6, r96b_seq net 0 + run_battery comment fix. Apply in a
   dedicated fold round — never inside an author landing.
2. **Gate-comment drift** (critic F1, scribe F1 — two-seat consensus):
   comment says "two cases / 15 entries"; actual 3 cases / 16. Fold
   with the simplifier pass.
3. **REJECTED-fold lesson banked**: `_arm_refuse`'s
   `ResourceLoader.load(p)` is liveness-load-bearing — static scan
   called it dead; executing the fold flipped
   `set_path_collision_refused` true->false. Cache-adjacent folds need
   execution proof, not just static reachability.
4. Scribe F2 (disclosure): uid allowlist string never emitted on
   scout/boundary receipts — uid_cache-conditional diagnostic; custody
   unaffected, record stands.
5. Report-only candidates: duplicate `key=` tokens inside signature-
   pinned PASS lines (not byte-neutral — integrator review).

Pre-existing lane property carried forward (not an r96 defect):
`negative_transition` wall-clock flake under load; `audio_playback`
flake; merged-stream prefix-spoof surface (documented since r63/r89).

Adjudicated by the lane orchestrator after all five wave-B reports
landed (this commit). Author commit `89f85ed8`.
