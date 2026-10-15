# r89 author — Geometry2D lattice landed (20 rows, 1 envelope, 1 crash row)

Seat `AUTHOR` (g2d lane r89) | host **devin** | Godot `4.7.2.stable.arch_linux`
(`/usr/bin/godot`, headless, 60 tps, GodotPhysics2D), Python 3.14.7.
Work executed on the `fd59c11` (*r88 fold*) tree; HEAD is now `2c4b1ff`
(sibling r91–r95 scout/boundary commits landed meanwhile — none touch
`corpus/fixtures/run_battery.py`: CASES is identical, 208 tuples, at both
commits, verified by AST parse). My work is worktree-only — **nothing
committed**. No `lsp` device / no GDScript server on this host (same as
scout/boundary); work = fixture landing + harness inserts verified by
fresh-process execution.

Scope per dispatch: the r89-scout's 20 verbatim CASES rows + the r89-boundary's
mandatory folds. `geo2d_lattice` probes land verbatim (sha-pinned); the only
harness file touched is `corpus/fixtures/run_battery.py`.

## Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/geo2d_lattice.gd` | `9784716b5d6932fa…` (581 lines) | verbatim copy of `corpus/live/r89-scout/probes/geo2d_lattice.gd` — manifest sha matches scout/boundary pins |
| `corpus/fixtures/input89_edges.gd` | `601c223ed7a32d91…` (140 lines) | verbatim copy of `corpus/live/r89-scout/probes/input89_edges.gd` |

Both probes already use the battery convention (`OS.get_cmdline_user_args()`
+ `--arm=` prefix scan; every arm prints its own name on its PASS line — no
silent dispatch). `project.godot` untouched (`8de8b3af…`).

## run_battery.py changes (insertion-only, +82/−0)

1. **CASES 208 → 228 tuples** (results rows 215 → **235**): 20 rows inserted
   after `r88_surfaces_vis_not`, ahead of the crash/descendant tail —
   `descendant_pipe_detached_control`'s `sleep 8` gap is preserved (no CASES
   row sits between it and the meta probes).
2. **`input89_edges_exact` armed as a 2-payload tuple envelope** (boundary
   fold, mandatory): the `just_after_flush=w_jp[ex=false inex=…]` token is
   load-bimodal — quiet `inex=true` / loaded `inex=false`. Payload[0] = quiet
   (the scout's pin), payload[1] = the boundary's verbatim alt. **Both
   payloads re-verified live this session**: 6/6 quiet fresh reps emitted Q;
   12/12 reps under 16 `yes` hogs emitted L, byte-identical to the boundary's
   §2 mode-L text; battery reps1–3 emitted L (envelope absorbed), reps4–5
   emitted Q.
3. **`expected_errors` += 2 exact entries** (scout §6.3):
   `geo2d_lattice_atlasempty` → `ERROR: Condition "p_rects.is_empty()" is true.`;
   `geo2d_lattice_polyendpoly` → `ERROR: Attempt to offset a polyline like a
   polygon (use offset_polygon instead).` (fires ×2 per run — open + closed —
   one exact entry covers both lines).
4. **Floor gate extended deliberately**: new discrimination
   `r89_expected_errors_all_matched` covering prefixes
   `("geo2d_lattice_", "input89_edges_")` — the r87 named-by-round /
   covers-round-prefixes shape (`input89_edges_*` carries no entries today —
   inert but covered). A dead r89 allowlist entry now fails loudly.

## New-cell inventory (20 rows)

| case | surface | pin shape |
|---|---|---|
| `geo2d_lattice_census` | ClassDB method census + join/end/op enums + 2-arg default resolution | `nmethods=86 sig=[…] default_join=SQ match=[sq,] default_polyline match=[sq/square,]` |
| `geo2d_lattice_ops` | clip/merge/inter/excl on overlapping squares + tri + ±2 offsets ×3 joins | full vertex+area pins incl. SQUARE<ROUND<MITER ordering |
| `geo2d_lattice_contain` | containment/hole semantics | `merge` collapses (k=1 a=1600); `clip`/`excl` produce k=2 w/ negative-area hole; edge-contact ≠ intersection |
| `geo2d_lattice_joins` | join×end lattice | sign-sensitivity (polygon) vs sign-insensitivity (polyline), `END_JOINED` k=2 inner-corner hole |
| `geo2d_lattice_trig` | hull/triangulate/decompose/delaunay/atlas | `tri_area==poly_area==280.0000`, `dec_area==280.0000` conservation invariants |
| `geo2d_lattice_pred` | predicates + bresenham + sic | `sic` = entry-fraction parametric pins (fwd=rev=0.2500) |
| `geo2d_lattice_pipedges` | boundary-policy ladders | three policies pinned: polygon ε-band inclusive / triangle strictly interior / circle exact |
| `geo2d_lattice_edge` | degenerate/empty inputs (all-clean class) | rotated-passthrough, bowtie/collinear/1pt tables |
| `geo2d_lattice_offempty` | `offset_polygon(∅)` | clean k=0 — the NOT-crashing twin of `offset_polyline(∅)` |
| `geo2d_lattice_offdeg` | `offset_polygon` on collinear/2pt/1pt | all clean, pinned contours |
| `geo2d_lattice_atlasempty` | `make_atlas(∅)` | loud refusal (whitelisted ERROR) + `{points:[], size=(0,0)}` |
| `geo2d_lattice_polyendpoly` | `END_POLYGON` on open+closed polylines | refusal (whitelisted ERROR ×2) + closed END_JOINED/BUTT contours |
| `geo2d_lattice_bridge` | clip → CollisionPolygon2D → StaticBody2D + falling RigidBody2D | `rest=y=82.3000 vel=0,0 self_hit=1` — duration-pin at 60 tps × 60 frames (boundary §3: ≥14-step settle margin, race-immune at this sample point) |
| `geo2d_lattice_ring` / `ring2` / `ring4` | hole contours as colliders | all rest `y=-47.8043 hits=1`; ring4 = 4-slab positive control |
| `geo2d_lattice_ringhits` | point-query discriminator | `A_contour0[centre:1…] B_both[centre:2…] C_slabs[centre:0…]` — the "no subtractive shape" law |
| `input89_edges_exact` | r87 leftover: poll-time `exact_match` granularity | **2-payload envelope** (fold); modifier-widened match answer is stable in both modes |
| `input89_edges_axisdev` | r87 leftover: joypad analog-axis device filter | `joys=0` env token; dev-5 doesn't press dev-0 action but writes the state bank; `dz_ax0=0.2000` |
| `geo2d_lattice_lineempty` | `offset_polyline(∅)` | **dedicated crash row** `expected_exit=-6` — uncatchable Clipper2 assert; signature is the pre-call `R89` diagnostic line (PASS unreachable). Battery's 8 s bound covers it |

**Deliberately NOT authored** (boundary folds honored): bool clip ≥1e15, any
INF vertex, `make_atlas(1e6,1e6)` (all SIGABRT vectors), `bresenham` NaN
(hang), zero-rect atlas poison, tiny-geometry floors, silent sentinels —
boundary measured them as laws/crash classes; none sit inside any authored
payload or signature.

## Fresh-arm evidence (pre-battery)

Each arm ×6 fresh in the battery's exact launch shape
(`timeout -s KILL 25 godot --headless --path proj --script res://<probe> --
--arm=<a>`; proj = fixtures `project.godot` + the two probes):
`corpus/live/r89-author/runs/` (120 receipts) + `verify_arms.py` (production
`classify_process` AST-extracted verbatim, segment sha `749fa060…` — same as
the scout's extraction):

- **20/20 cells: `out_uniq=1 err_uniq=1`, constant rc, `sig_hit=6/6`,
  `classified=6/6`.** No envelope needed for any geo cell — matching the
  scout's "no bimodal cell exists in this surface".
- `lineempty`: rc=134 (shell) ≡ −6 (Python) ×6, SIGABRT reproducible.
- `exact`: quiet reps all mode Q; a separate 16-hog series gave **12/12 mode
  L** (`inex=false`), byte-verified vs the boundary's alt payload — the
  envelope's second arm is real, not speculative.

## Full battery — before/after

| run | rows | verdict |
|---|---|---|
| r89-baseline refs (frozen `0628932`) | 215 | PASS ×2 |
| author rep1 `runs1/20261015T192943134846Z` | 235 | FAIL — `transition`, `audio_playback`, `input_lattice_pre_frame` (mode C) |
| author rep2 `runs2/20261015T193511810128Z` | 235 | FAIL — `input_lattice_pre_frame` (mode C) only |
| author rep3 `runs3/20261015T194459977604Z` | 235 | FAIL — `negative_transition`, `audio_bus_route_invalid_control` (+meta cascade) |
| author rep4 `runs4/20261015T195122022920Z` | 235 | **PASS** |
| author rep5 `runs5/20261015T195521854184Z` | 235 | **PASS** |

**Two consecutive green runs (235/235) on the final bytes.** All 20 r89 rows
are PASS in **all five** reps (100/100 row-instances).

**Flake accounting (recorded, not excused — the r88-verifier2 pattern):**
reps1–3 ran under foreign oversubscription (load 25→127; up to 52 `yes` hogs
+ two sibling-lane batteries live — none of it mine; my own hog set was
killed after the mode-L series). All four observed failures are **documented
pre-existing classes** on rows this round does not touch: `pre_frame` emitted
the ≥2-tick mode the r87 author predicted verbatim ("if it ever appears the
row flakes — recut … rather than widening" — so the envelope was **not**
widened; 48 standalone reps incl. 24 under +24 hogs produced only the two
whitelisted modes — the battery's sequential context is what exposes it);
`audio_playback`/`audio_bus_route_invalid_control` are the audio-load-flake
class; `transition`/`negative_transition` are the scene-readiness class.
rep3's `probe_error_clause_surface` failure is a pure cascade of those two
rows (`census_bare_classifier_consistent` — their whitelisted entries went
unmatched because the rows died differently); every other discrimination,
incl. all four `*_expected_errors_all_matched` gates, was green.

**Prior-row identity** (`compare.py godot` vs baseline runs1+runs2):
`common=215 new_only=20 old_only=0`; `tuple_mismatches=2` — the seeded diff is
`input_lattice_phys_peer`'s signature (the frozen baseline predates `fd59c11`,
whose r88 fold widened the row from a single `ev_step_delta=0` payload to a
6-payload envelope covering delta 0–5 — verified: single string at 0628932,
tuple at fd59c11); the meta diff is `probe_error_clause_surface`
(census enumerates the 2 new expected_errors rows + the `r89_` gate key —
by design). rep4↔rep5: **tuple_mismatches=0** across all 235 rows; the only
output diffs are envelope rows emitting their other whitelisted modes
(`pre_frame`/`press_phys`/`ui_ns`/`release_edge`) and the declared-volatile
`mp_loopback` peer-id token.

**Gate evidence (rep5 verdicts.json):**
`r89_expected_errors_all_matched=true`, `r88_…=true`, `r87_…=true`,
`phys2d_…=true`, census `dead_entry_count=0`,
`rows_with_expected_errors=55` (was 53); r89 census rows show
atlasempty `matched=1`, polyendpoly `matched=2`, both
`bare_classification_rejects=true` / `allowlisted_classification_passes=true`.

## Host notes / remaining risks

- `input89_edges_exact` still emits per-load modes by design — PASS either
  way via the envelope; a THIRD payload (never observed: 20/20 scout +
  51 boundary loaded + 12 mine hogged + 5 battery reps → only Q/L) would fail
  loudly, which is the intended semantics of a mode cell.
- `nmethods=86`/`sig=[…]` (build), `joys=0` (host joypad count),
  `tps=60 frames=60` (project) are stable non-run tokens — each flips loudly
  on a build/host/config change (boundary §5), none authored away.
- Bridge/ring 4-dp pins ride float32 fixed points ~6–10 ULP from the rounding
  boundary (`82.300003`, `-47.804287`) — safe on this build; a solver/backend
  change can move the 4th decimal (boundary §3).
- `lineempty`'s stderr carries the host libstdc++ assert path
  (`/usr/include/c++/16/bits/stl_vector.h:1253`) — contains no `ERROR:`
  token, never whitelisted; a libstdc++ bump shifts that text but the row's
  verdict only reads rc + the pre-call `R89` stdout line.
- Boundary vectors deliberately left un-authored (documented above) remain
  available for a dedicated crash/hang battery if the orchestrator wants them.
- No commit. Worktree: `M corpus/fixtures/run_battery.py`,
  `?? corpus/fixtures/{geo2d_lattice.gd,input89_edges.gd}`,
  `?? corpus/live/r89-author/`, this report.

## Evidence index

`corpus/live/r89-author/` — `manifest.sha256` (1713 entries) covers all:

| artefact | path |
|---|---|
| arm driver | `run_arms.sh` |
| per-cell fresh reps (20 arms ×6 + 12 hogged `exact`; 396 files) | `runs/` |
| rep verifier (AST-extracted classifier) | `verify_arms.py` |
| battery rep summarizer | `check_rep.py` |
| launch project copies | `proj/` |
| 5 battery runs (rep4+rep5 green) | `runs{1..5}/<stamp>/verdicts.json` + `battery-rep{1..5}.{stdout,stderr}` |
</content>
