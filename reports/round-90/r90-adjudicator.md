# r90 adjudication — RigidBody2D dynamics lattice

**Verdict: ADMIT** — committed `ee20575` (+ r89-fold neighbor `53a0be7` carrying `required_stderr`), 247 rows, 12 new `r90_lattice_*` rows.

## Dossier

| seat | verdict | commit |
|---|---|---|
| author | 247/247 ×2, all 3 folds applied | `ee20575` |
| boundary (pre-landed) | ordering law confirmed 60/120; `dy=n·g·dt²`; Dummy vacuity; typed refusals | `520ed6d` |
| critic | PASS-WITH-RESERVATIONS — F1 30-tps receipt mislabel (text only), F2 refusal state-blindness | `fe353ed` |
| reviewer | PASS — 48/48 fresh classify, pins byte-equal, folds verified | `03d0239` |
| simplifier | PASS — zero removable weight, 12 dispositions proven | `48b9bcc` |
| verifier | VERIFIED-WITH-RESERVATIONS — rep2 247/247 byte-identical, 55/55 re-derivations | `3254f54` |
| scribe | CUSTODY HOLDS — manifests 4015/4015, archive rep 247/247 | `8a8488d` |

## Laws admitted

COM read/refuse (typed refusal ladder), gravity lattice, damp semantics (float32 recurrence `v←v(1−d·dt)+g·dt` reproduces every pin exactly), built-in order stream, write-lag, impulse closed forms, freeze/lock/sleep lattice, contact monitor, `dy=n·g·dt²` oracle — all qualified to `eng=PhysicsServer2D` precondition and `tps=60`.

## Recorded-not-folded / lane notes

- **F1 (3-seat-confirmed):** `--physics-ticks-per-second` does not exist on Godot 4.7.2 and is silently ignored — the author's "30-tps" receipts are 60-tps runs. The fold's *conclusion* is true (real 30-tps fails loudly via project override — 3 independent verifications) but the evidence text is wrong. Lane note: never cite that flag.
- Critic F2: refusal rows are state-identity-blind (dead-entry census is the sole guard) — filed as standing caveat.
- Reviewer F6/by-design: floor gate checks ≥1 match only (r87–r89 precedent).

## Bounds

Godot 4.7.2 stable headless 60-tps project, `eng=` precondition armed on all 12 rows; load ~70–130 throughout; late-body pairing confirmed live at 60 tps (verifier F2 — the pairing fields are load-bearing).
