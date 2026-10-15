# R79 adjudicator — Godot-4 2D contact/event battery (phys2d_events)

Round: 79. Wave: `shokunin-train-20261101-w20`. Work+fold commit
`f777925` (author landing + fold in one commit; the Sol author lane
rate-limited mid-run and a swe-2 finisher completed + audited it).

## Declared move

23 new CASES rows arming the r79 scout's Godot-4 2D physics-events
table on `phys2d_events.gd`: contact-monitor on/off/max0 lattice,
in-cb write/deferred-write/queue_free/free_rid/direct-dss surface,
Area2D twins, plus the shared-battery insertions (88 → 111 rows).

## Claim adjudication

- **CONFIRMED.** 111/111 ×3 (author runA/runB post-repair, folded run).
  Finisher audit: the Sol lane's inherited landing was byte-exact
  (fixture sha 7329acb2 = scout-pinned probe; 23/23 CASES rows +
  4/4 expected_errors identical to `author-rows.py.txt`). Its run-1
  FAILs were diagnostic self-infliction (results-order) — repaired by
  the same seat's rewrite, re-verified.
- **Zero-drift verified independently.** Baseline (frozen HEAD
  884a4c4): 0 tuple mismatches on all 88 prior rows ×2 reps; the only
  meta tuple-diff is `probe_error_clause_surface` legitimately
  enumerating the new allowlist (39→43 rows, 41→53 error lines) — all
  34 discriminations true. Verifier re-derived: 0/111 tuple mismatches
  vs author runA, 104/104 output-identical.
- **Mutation proofs.** Forged-signature mutant killed (cb_count 2→3 →
  rc=1, exactly that row FAILs); CASES-row deletion flips only that
  row; 8s detached-descendant razor held under 20-spinner load
  (+4.5s injected delay fails with the documented signature).

## Fold corrections

- **Simplifier (proven vfold cd103d0a, −23 net)**: stale arm census
  comment (20/23 arms listed), dead `_in_cb["cls"]` store (never read
  on the RB dict — the area twin IS read; asymmetry verified),
  redundant `_area.monitoring = true` init. run_battery.py needed
  nothing — all 23 rows reachable, all 4 allowlist entries
  load-bearing.
- **C1 (mechanism-blind muted pins — live-proven forge)**: `cm_off`
  and `cm_max0` both emitted all-`-` cb_* fields — a fixture carrying
  `contact_monitor=false` produced the byte-exact pinned `cm_max0`
  signature without exercising `max_contacts_reported`. Folded:
  `post_monitor`/`post_max` post-state reads appended to both muted
  lines; re-pinned (`off`: false/4, `max0`: true/0). Forge replay on
  the folded tree emits `post_monitor=false` → fails closed.
- **C2 (expected_errors ceiling-not-floor)**: the allowlist census
  carried dead-entry data but never gated it. Added
  `phys2d_expected_errors_all_matched` to sf_discriminations — every
  phys2d_events_* allowlist entry must match a real emitted line.
- **P5 (boundary-exec verified)**: `love.errorhandler` now overridden
  in `love_phys_probe/main.lua` — prints error + `debug.traceback`
  at level 2 and returns the quit function. Level 1 broke `esc_fn`
  (first quoted frame became `handler`); level 2 preserves every pin
  (rc=1, err_on=stdout, assert_txt, esc_fn=setPosition) at +2 output
  lines. No conf can now open a desktop window — the stray-invocation
  surface the operator hit mid-run is closed.

## Record corrections (boundary-exec + verifier + scribe)

- **P1 falsified (scout's reading)**: `cb1_colliders=1` under two
  overlapping floors is a dispatch-order snapshot, not a count
  invariant — `colliders_2=2` measured. Cell pins are value-stable
  either way; the interpretation note is corrected here.
- **P2 partial-falsification**: deferred writes are NOT window-scoped
  reverts — `set_deferred` lands durably and reaches the server (the
  engine's own escape); the in-window invisibility remains pinned but
  is reframed as same-frame visibility, not revert.
- **P3 new member**: immediate `free()` in-cb = refused member
  (`Object is locked and can't be freed.` + SCRIPT ERROR) — differs
  from queue_free's accepted deferral; queued for a future arm.
- **Verifier F2**: at 20:1 oversubscription the hold arm starves at
  its 3.0s bound before the 8s razor — razor remains the correct bound
  on this host's load envelope; noted, not folded.
- **Scribe**: results-order root cause named (phys2d block appended
  after detached-pipe control → cascade); record stands corrected.

## Bounded residuals

- C3 substring-not-line signature matching — judge tradeoff,
  harness-wide, not a fold blocker.
- `area_node_position`/`rb_dss_in_cb` coverage of foreign-space dss
  objects: B4 measured no world-state bypass (foreign space sees only
  itself) — recorded, not armed.
- Threaded-twin arm remains evidence-only (no variant plumbing).
- `SCORECARD.md` foreign-fleet overwrite left uncommitted (attribution
  pending; the file belongs to this lane's own ledger format).

## Seat record

scout (verbatim 23-cell table) → author (Sol lane, died on rate
limit mid-run) → finisher (swe-2, byte-exact audit + repair) →
baseline (flash, zero-drift) → boundary (zfl, audit) → boundary-exec
(five probes live) → critic (Sol, C1 live-proven + C2/C3) → verifier
(zfl/mutation, 10/10 PASS) → simplifier (flash, proven vfold) →
scribe. **ADMIT-corr.**
