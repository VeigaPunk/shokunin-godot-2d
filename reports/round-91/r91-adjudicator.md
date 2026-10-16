# r91 adjudication — Navigation2D lattice

**Verdict: ADMIT** — committed `77d2f7e`, 258 rows (251 CASES + 7 meta), 11 new `nav_lattice_*` rows.

## Dossier

| seat | verdict | commit |
|---|---|---|
| author | 258/258 ×2, all 6 boundary folds encoded | `77d2f7e` |
| boundary (pre-landed `93ce7c4` corrections) | sync ladder not constant; change-application falsified under ff; fin/reached query-order artifact; teardown crash | folded |
| critic | PASS-WR — F1 settle pins 60-tps-conditioned (loud under ff) | `645fd8e` |
| reviewer | PASS — 4 folds demonstrated, nav 11/11 ×2 + 55/55 loaded | `7330589` |
| simplifier | PASS — 2 YAGNI dels (−3, SETTLE + hits sinks), unapplied | `23c3b46` |
| verifier | VERIFIED-WR — rep5 258/258 tuple-identical, nav 55/55, 43/43 rederiv | `ed31211` |
| scribe | CUSTODY HOLDS — 398+1632+642 manifests verify | `e3fd799` |

## Laws admitted

Sync-gate law via `iteration_id`+reach (STALE+exit-2 on 48-frame exhaustion — no silent mis-PASS at any tps); `is_navigation_finished()` before `is_target_reached()` (query-order fix); bake routes; avoidance invariants (probe-side); teardown crash armed `rc=-6` bound to `double free or corruption` + clean arm; scheduler fields in diagnostic tails only — every pin is a clean prefix.

## Recorded-not-folded

- Verifier F1: avoidance-bound comment formula is `(d−r_a−r_b)/τ`, not `(r_a+r_b)/τ` — coincides on the committed rig (gap 20 = radii sum 20). Comment defect, rig-correct pin.
- Critic F1: 4-frame settle pins are 60-tps-conditioned (flip loudly under `--fixed-fps` — never silent).
- Simplifier patch (−3) + reviewer F3/F4 queued for next touch.
- Scribe A1: scout §3.7 range is frame-1-only.

## Bounds

Godot 4.7.2 headless 60-tps project; `--fixed-fps` explicitly out-of-row-scope (loud flips measured); host load 51–130 across seats.
