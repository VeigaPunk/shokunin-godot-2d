# r95 author — PhysicsDirectSpaceState2D query lattice landed (52 rows: 17 `dss_lattice_*` + 35 `r95b_order_*`)

Seat `AUTHOR` (g2d lane r95) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, headless, 60 tps,
RendererDummy). HEAD at session start `c7228893` (r94 author, custody free
per dispatch: "Custody free (r94 landed c7228893)").
Work is worktree-only — **nothing committed**. No `lsp` device / no GDScript
server on this host (same as r89–r94); all semantic validation is
fresh-process execution. The battery's own `classify_process` semantics are
the judge for every signature below (`signature in output` substring, no
unallowlisted `ERROR:` line, `error is None`, `code == expected_exit`).

Scope per dispatch: read `reports/round-95/r95-scout.md` +
`corpus/live/r95-scout/` + `reports/round-95/r95-boundary.md`; **encode only
boundary-surviving claims** (boundary's falsifications pre-decided);
insertion-only `run_battery.py`; land probe(s) into `corpus/fixtures/`
(byte-copy or minimal declared diff); battery green twice; this report.

## Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/dss_lattice.gd` | `77ae4adb8a47ccf50b5da345720247c035418e31872a117d17cd98913f479627` (743 lines) | **byte-copy** of the frozen r95-scout probe `corpus/live/r95-scout/probes/dss_lattice.gd` — zero diff |
| `corpus/fixtures/r95b_order.gd` | `4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490` (777 lines) | **byte-copy** of the frozen r95-boundary probe `corpus/live/r95-boundary/probes/r95b_order.gd` — zero diff |
| `corpus/fixtures/run_battery.py` | tracked, `+163 / −0` | insertion-only: r95 comment header + 52 CASES tuples + `r95_expected_errors_all_matched` floor gate |

`project.godot` untouched. Byte-identity of both probes confirmed by
`sha256sum` and by the labrat's independent line-for-line comparison (H1
below).

## Boundary-driven encoding decisions (the falsifications applied)

The scout's `author-rows.py.txt` offered two verified sets: `ROWS`
(full-line, 150/150) and `ROWS_PREFIX` (recommended, 150/150). The
boundary's verdicts make the choice for the four order-vector cells:

| scout claim | boundary verdict | encoding consequence |
|---|---|---|
| order is a stable read / deterministic for a frozen construction | TRUE in-frame; the vector drifts **every physics tick** through a **k(k−1)-phase cycle** (§2) | the t=2 vectors are the wrong thing to pin — pin the cycle law instead (`r95b_order_*` rows) |
| `--rev` proves insertion-order dependence | conclusion true, **evidence refuted**: `--rev` relabels tags on index-positioned bodies — same construction (§3) | `order_core_rev`/`point_cap_rev` kept only as head-prefix arm-dispatch rows; the real evidence is `perm0..7` (fixed tag→position map, permuted creation — 8/8 distinct ladders) |
| "layout dependent" (translated pile → different vector) | **REFUTED** — 14/14 isolated translations identical; the effect is co-presence (§4) | the key `layout_changes_order=true` is never signed (prefix cut); the correction is pinned positively by `celloff` (invariance) + `twopiles`/`warm_keep8` (co-presence) |
| point and shape queries share the order | **conditional** — true single-layer, false with a CanvasLayer collider (§7) | `layers_k0`/`layers_k1` pin both branches; `dss_lattice_point_canvas` keeps `shape_layer_agnostic=true` (a canvas-scoping statement, not the refuted order-sharing one) |
| sorted set is the only invariant | **refuted above the cap** — 3 creation orders → 3 different 32-subsets; `set32_distinct=5` (§6) | `cap40_p0..p2` pin `n32=32 n64=40 n0=0` + `set32_distinct=5` + the three distinct `set32_t2` subsets |
| 17 rows load-stable | **CONFIRMED, strengthened** — byte-identical under 16-hog load, `--fixed-fps` 1/30/120, threaded physics, 32-body allocation-history perturbation (§8) | full-line signatures kept for the 13 non-vector cells |

So the landed `dss_lattice_*` set is the scout's `ROWS_PREFIX` **verbatim**
(17/17, labrat-verified element-wise): 13 full-line rows + 4 head-only rows
(`point_cap` ×2 → `add_order=… cap0=[]`; `order_core` ×2 → `add_order=…`).
Every claim the boundary refuted (`layout_changes_order`, cross-frame
stability, label-only `--rev` evidence, unconditional order-sharing,
above-cap set invariance) sits outside the signed region or is positively
re-pinned by an `r95b_order_*` row.

## run_battery.py changes (insertion-only, `git diff` = 163 `+` / 0 `−`)

1. **CASES 307 → 359 tuples** (results rows 314 → **366** incl. 7 meta):
   the r95 block (48-line comment header + 52 tuples) is inserted after
   `r94_particles_gpu_headless`, ahead of the crash/descendant tail —
   `descendant_pipe_detached_control`'s sleep-8 gap stays adjacent to the
   meta probes (the final four CASES tuples are untouched).
2. **Signature form**: the `dss_lattice_*` 17 are `ROWS_PREFIX` verbatim;
   the `r95b_order_*` 35 are the canonical `PASS r95b_order <arm> …`
   lines from the boundary receipts (per-cell `pass_uniq=1` across all
   batches they appear in — verified by this seat's hash scan over all
   261 receipts before authoring).
3. **`expected_errors` += 0, `required_stderr` += 0** — all 52 arms are
   `ERROR:`-clean with 0 B stderr (scout's 150 classified receipts,
   boundary's 261 receipts, this seat's 52-arm smoke pass, both green
   battery runs).
4. **Floor gate extended**: `r95_expected_errors_all_matched` covering
   `case.startswith(("dss_lattice_", "r95b_order_"))` — same
   named-by-round / covers-round-prefixes shape as r87–r94; inert today
   (no entries) so a future r95 allowlist entry cannot die silently.
   `True` in all three runs.

## New-cell inventory (52 rows)

### `dss_lattice.gd` — query lattice (17)

| case | arm | pin shape | law pinned |
|---|---|---|---|
| `dss_lattice_census` | `census` | full line | exactly 6 dss methods; `max_results` is a method arg, not a property; no `backface_collision` in 2D; `canvas_instance_id` exists on point params; `shape` vs `shape_rid`; dss object identity stable across calls; `GodotPhysicsDirectSpaceState2D` class |
| `dss_lattice_ray_flags` | `ray_flags` | full line | mask/body/area toggles; exclude by RID; `hit_from_inside=false` ⇒ silent miss inside, `=true` ⇒ origin hit with `normal=(0,0)`; exact hit-dict key set |
| `dss_lattice_ray_geom` | `ray_geom` | full line | inclusive endpoint; collinear-graze hits with face normal; corner = face normal not bisector; zero-length always misses; direction-aware; **boundary-start half-open asymmetry** (left/top-start suppressed, right/bottom-start = t=0 hit even pointing away) |
| `dss_lattice_ray_order` (+`_rev`) | `ray_order` | full line | nearest wins; coincident tie = last added (deterministic) |
| `dss_lattice_point_cap` (+`_rev`) | `point_cap` | **head prefix** | `max_results=0` ⇒ `[]` (the cap-0 hazard) — construction echo only; vectors/counts covered by `cap40_p*` |
| `dss_lattice_point_edge` | `point_edge` | full line | half-open rect (left/top in, right/bottom out), circle exclusive, rotated box half-open in local space; shape predicate disagrees by design |
| `dss_lattice_point_canvas` | `point_canvas` | full line | `canvas_instance_id=0` = default layer only; `CanvasLayer.offset` is render-only; ray/shape have no canvas scoping |
| `dss_lattice_shape` (+`_rev`) | `shape_lattice` | full line | same cap semantics; one entry per shape index (`m#0..m#2`); `shape_rid` ≡ `shape`; exact touching counts as overlap |
| `dss_lattice_order_core` (+`_rev`) | `order_core` | **head prefix** | arm dispatch + frozen `[a,b,c,d,e]`/`[e,d,c,b,a]` construction only — every order/mutation claim is carried by `r95b_order_*` |
| `dss_lattice_layer_forms` | `layer_forms` | full line | StaticBody/RigidBody/CharacterBody visible, Area2D only with `collide_with_areas`, plain Node2D invisible; server-tier body fully queryable (`?` tag) |
| `dss_lattice_cast_rest` | `cast_rest` | full line | `cast_motion` float32 `[safe,unsafe]` fractions; `[1,1]` no-hit; **no depenetration** (inside-start reports next contact); `get_rest_info` has `collider_id`, no `collider`; `collide_shape` counts PAIRS not points; duplicate pair emitted |
| `dss_lattice_excl_space` | `excl_space` | full line | exclude takes body RIDs only (shape/null RIDs inert); queries are per-`World2D`-space (SubViewport isolation); `Node2D.get_world_2d().space` agreement |
| `dss_lattice_fresh` | `fresh` | full line | `add_child` queryable same frame; node-tier position write deferred 1 step; `body_set_state` live same frame; `queue_free` deferred; `visible`/`collision_layer` irrelevant to queries |

### `r95b_order.gd` — the ordering law, phase-resolved (35)

| case(s) | claim pinned |
|---|---|
| `r95b_order_canon` | dense 20-phase ladder `t0=0,1,2,3,4 … t20==t0 … t64`, `distinct_ticks=20`, `cycle_len_dense=20`; `t2_vec` is the scout's old row, one phase of 20; `pt_stable_interleaved=true` (in-frame reads stable) |
| `r95b_order_periodx_k{2,3,4,5,5s8,6,7,8,10}` | **`cycle_len = k(k−1)`** for k = 2,3,4,5,5@spacing8,6,7,8,10 (`expected_kk1` echoed in-line); spacing-independence at k=5 |
| `r95b_order_period_k5` | k=5 cycle=20 — the cell that also ran under load/ff1/ff30/ff120/threaded in the boundary matrix |
| `r95b_order_perm{0..7}` | creation order permuted under a **fixed** tag→position map: 8/8 distinct ladders and t2 position vectors — the real insertion-order-dependence evidence |
| `r95b_order_scoutrev` | `t2_vec_matches_scout_row=true` + `t2_relpos_equals_canon=true` — the label-permutation falsification pinned positively |
| `r95b_order_celloff_{x0,x1000,y1000}` | identical 8-tick ladder at off 0, +1000 x, +1000 y — translation invariance (the corrected "layout" claim) |
| `r95b_order_twopiles` | A-at-t4 **with** B present `[e,a,c,b,d]` ≠ A alone `[e,a,b,c,d]` — co-presence, the true attribution of the scout's pile_b |
| `r95b_order_warm_k32` | 32 far bodies created **and freed** before the pile → ladder identical to canon (allocation history inert) |
| `r95b_order_warm_keep8` | 8 far bodies kept **live** → different vector `[a,e,b,c,d]`, `distinct_ticks=4` — the frozen-scene scope limit, pinned as data |
| `r95b_order_free_{ab,ba}` | same final set {c,d,e}, different free order → ladders differ at every sampled tick; post-free 3-body cycle still k(k−1)=6 (`t2==t8`) |
| `r95b_order_readd_a` | fresh body at a freed body's position inherits its cycle slot; 5-body cycle resumes |
| `r95b_order_cap40_p{0,1,2}` | `n0=0 n32=32 n64=40` (cap-0 empty, default-32 truncates, cap-64 full) + `set32_distinct=5` + three distinct `set32_t2` subsets — the set is NOT invariant above the cap |
| `r95b_order_layers_{k0,k1}` | `pt_eq_sh=true`/`sh_len=5` single-layer vs `pt_eq_sh=false`/`sh_len=6` with a CanvasLayer body — order agreement is layer-conditional; the invisible collider still perturbs (`cycle 30`) |
| `r95b_order_rigid` | rigid solver positions byte-deterministic (`t10_relpos=[15.9999,14.8732]`, `distinct_ticks=1`) |

## Deliberately NOT authored (boundary-verdict exclusions)

- **`procwait`** — the one genuinely unstable cell (boundary §9 [U]): an
  `await process_frame` harness lands on a different tick phase per rep;
  8 distinct payloads across its 16 receipts (quiet/load/ff1/ff30/ff120).
  No row.
- **`env`** — frame counters; 2 distinct payloads across its 4 receipts.
- **Every full-line multi-hit order vector** in the `dss_lattice` suite
  (t=2 phases of a k(k−1) cycle — phase-locked, construction-bound).
- **`layout_changes_order` / `shape_same_order` / `repeat_stable` as
  signed keys** — the first is refuted, the latter two are
  scope-conditional; the r95b rows pin the honest versions.
- **`warm_k{0..13}` (freed), `warm_keep64`, `free` single/`ac`/`ca`,
  `readd_c`, `celloff` other offsets, `period_k{2,3,4,6,8}`, `perm`
  beyond 8** — redundant cells of the same pinned laws (`keep64`'s
  `distinct_ticks=1` collapse is noted in the boundary, same claim class
  as `keep8`).
- **instance ids / raw RIDs** — `warm_k1` proves ids vary while ladders
  hold; never semantic (the `shape_rid=RID(0)`/`canvas_instance_id` hits
  in `dss_lattice_census` are deterministic null-RID default-property
  tokens, not instance values — labrat H5 caveat noted).

## Evidence

- **Smoke (pre-battery)**: all 52 arms run fresh-process
  `godot --headless --path <scratch-copy-of-fixtures> --script res://<p>
  -- <flags>` under an 8 s bound (the battery's own launch shape and
  timeout) — **52/52 rc=0, 0 B stderr, every signature substring-matched
  its fresh output**. The scratch replicated the battery's copy +
  `pickup.tscn` staging + app-name munging + `causal_chain` readiness fix.
- **Per-cell receipt stability (pre-check)**: `pass_uniq=1` for all 35
  authored `r95b_order` cells across every batch they appear in
  (hash-scan over `corpus/live/r95-boundary/runs/**`); only `env`
  (`pass_uniq=2`) and `procwait` (`pass_uniq=8`) vary — neither authored.
- **Battery run 1** `corpus/live/runs/20261016T064148780406Z/verdicts.json`:
  **365/366 PASS, 1 FAIL** — `input_lattice_pre_frame` (pre-existing r87
  mode-envelope row) emitted a third tick-window payload outside its two
  whitelisted modes: the documented "one-tick" flake class (r87 critic2
  "Unobserved third modes: pre_frame ≥2-tick window"; r89 reviewer
  counted it among the flake rows; dispatch's documented flake classes).
  **All 52 new rows PASS**, `r95_expected_errors_all_matched=True`.
- **Battery run 2** `corpus/live/runs/20261016T064742446822Z/verdicts.json`:
  **PASS, 366/366** — all 52 new rows PASS; `pre_frame` green;
  `r95_expected_errors_all_matched=True`.
- **Battery run 3** `corpus/live/runs/20261016T065335715243Z/verdicts.json`:
  **363/366 PASS, 3 FAIL** — `negative_transition` ("probe exceeded 120
  frames": transition one-tick flake), `audio_bus_route_invalid_control`
  (`advanced=fals`: audio wall-clock row), and `probe_error_clause_surface`'s
  `census_bare_classifier_consistent` (a downstream consistency
  discrimination that the two row flakes break — not an independent
  failure). All are the dispatch's documented flake classes; **all 52 new
  rows PASS again**, `r95_expected_errors_all_matched=True`.
- **Battery run 4** `corpus/live/runs/20261016T065922894811Z/verdicts.json`:
  **PASS, 366/366** — the second green on identical bytes.
- **Insertion-only proof**: `git diff corpus/fixtures/run_battery.py` →
  163 insertions, 0 deletions (152-line r95 CASES block = 48 comment
  lines + 104 tuple lines for the 52 tuples; 11-line floor gate).
- **Row arithmetic**: CASES 307 → 359 (+52); results 314 → 366 (+52,
  meta rows unchanged at 7).
- **Independent probe (frozen `probeParent` dispatch, exactly one)**:
  `ufo-labrat` agent `4310edb9`, read-only, five hypotheses — **all
  CONFIRMED**: H1 both probes byte-identical to frozen sources with the
  claimed sha256s; H2 17/17 `dss_lattice_` tuples equal `ROWS_PREFIX`
  element-wise (the four vector cells carry the cut signatures, no
  full-line leak); H3 35/35 `r95b_order_` signatures are exact whole
  `^PASS` lines of their matching receipts (incl. the three ~2.3 KB
  cap40 lines, verified head+tail+length); H4 insertion-only, +163,
  crash tail untouched; H5 no `procwait`/`env`/`layout_changes_order`
  anywhere in the block (the census `RID(0)`/`canvas_instance_id`
  literals are deterministic defaults, not instance values). Advisory
  only — no second dispatch; it wrote nothing.

## Files changed

- `corpus/fixtures/dss_lattice.gd` — **new**, 743 lines, sha256
  `77ae4adb8a47ccf50b5da345720247c035418e31872a117d17cd98913f479627`
  (byte-copy, zero diff vs frozen scout probe).
- `corpus/fixtures/r95b_order.gd` — **new**, 777 lines, sha256
  `4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490`
  (byte-copy, zero diff vs frozen boundary probe).
- `corpus/fixtures/run_battery.py` — `+163/−0` (r95 comment header,
  52 CASES tuples, `r95_expected_errors_all_matched` floor gate).
- `reports/round-95/r95-author.md` — this report (new, untracked).
- `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` — regenerated
  as a side effect of importing the battery (tracked build artifact);
  restored to HEAD after the final run.

## Remaining risks / blockers

- **The `dss_lattice` prefix rows are thin by design** —
  `order_core[_rev]` pins only `add_order=[…]` (arm dispatch + frozen
  construction); every ordering claim lives in the `r95b_order_*` rows.
  If a future engine bump perturbs the broadphase, it is the ladder rows
  that reject — the law, not a phase.
- **k(k−1) was measured for point queries over static rectangles**
  (boundary §11): `intersect_shape`/`intersect_ray` cycles are only
  spot-checked (`*_pt_eq_sh` keys); non-rect/rotated/server-tier and
  multi-shape-body periods are unmeasured. The pinned cells are exactly
  the measured set.
- **`warm_keep8` documents a scope limit, not a bug**: pinned vectors are
  valid only for their frozen scene composition; live unrelated
  colliders perturb the returned order deterministically.
- **`input_lattice_pre_frame` remains a live flake row** (pre-existing;
  a ≥2-tick envelope mode outside its whitelist) — run 1's sole FAIL;
  nothing in this block interacts with it.
- **Host was never idle** (loadavg ~70–150 through both lanes' sessions
  and these runs); all rows are the load-proof forms (boundary: 0
  rejections at 16 hogs, ff/thr-identical for tick-awaiting harnesses).
- **Blockers: none.** Nothing committed; unrelated lanes' untracked
  `corpus/live/` artifacts untouched.
