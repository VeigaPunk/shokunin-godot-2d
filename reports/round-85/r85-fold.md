# r85 fold — camera/canvas transform lattice (corrections applied)

Fold of `45232c7` + wave-B corrections. Final battery: **174/174 PASS**
(`corpus/live/r85-foldc-final2/20261015T085238195177Z/verdicts.json`).

## Critic corrections (all landed, additive)

| # | arm | fix |
|---|-----|-----|
| C1 | `cl_draworder` | `DrawTag.queued` + `queue_tag()`; rows emit `hidden[in=1 vis=0 queued=3]` — orphaned-layer and never-requeued forges now both fail |
| C2 | `vp_render_indep` | readbacks `v2cam[pos zoom]` + `cloff` — camera/CanvasLayer writes can no longer be dropped silently |
| C3 | `cl_stack`, `cl_follow` | `in=%d` (`is_inside_tree()`) per row — membership pinned |
| C4 | `par_2d` | finish emits `rep/fv/so/ign` readbacks — writes can't be dropped |
| C5 | `par_layer` | in-row `mm=`/`mo=` on mirror100/moff10/pbgmirror/pbgmoff (finish's post-reset values are 0,0 — in-row witnesses required) |
| C6 | `cam_comp` | `n4`/`comp4` under the FIXED_TOP_LEFT (s4) transform — composition law now proven under two live configs, kills the "tautological identity" class |
| C7 | `cam_zoom_center` | `sub_dev=%.9f` (measured `0.000006104`) — replaces the 4dp "-0.025 exact" laundering |

## Boundary corrections (claim-scope)

- F5: "camera writes are cached" narrowed — **transform writes
  (position/rotation) are deferred**; `zoom`/`offset`/`anchor_mode`/`limit*`
  update synchronously via `_update_scroll()`. Author table row corrected.
- Remaining 13 named classes (smoothing divergence, inverted-limit midpoint
  clamp, `is_zero_approx` zoom floor, drag statefulness, parallax
  zoom/parentage splits, physics-interp timing) recorded for LOG — all
  claim-scope, no pinned value falsified.

## Verifier / scribe

- Verifier: ADMIT recommended on the pre-correction build (two fresh
  174/174, exact 15-row pin equality, prior-159 stable, forge-kill live);
  corrections above are the fold's own response to the critic.
- Scribe F2 (medium): noted — see adjudicator.

## Re-pin mechanics

8 of 15 rows re-pinned (new witness tokens only; all prior substrings
byte-identical). Pins captured **under battery context** — the scratch
project runs 64×64 vs the 720×450 direct-`--script` default; a first
capture at the wrong viewport produced 7 viewport-coupled FAILs, resolved
by re-capturing via `--path <scratch>`. Not a semantic drift; recorded so
future re-pins use the battery context.
