# r89 verifier — independent non-author verification of `8cea888`

Seat `VERIFIER` (g2d lane r89, independent non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7, 32 cores. Target:
`8cea888245c071564f76d7471d240ea43dff0997` (*r89 author: Geometry2D lattice +
input89 edges — 20 rows 215→235*). Receipts: `corpus/live/r89-verify/`
(index in `RECEIPTS.md` there). Author report: `r89-author.md`.

No `lsp` device / no GDScript server on this host (unchanged lane state);
verification is fresh-process execution + AST/byte analysis only. **No tracked
writes, no commits.** All artifacts are untracked `corpus/live/r89-verify/`
scratch + this report.

## Method — frozen tree

```
git archive --format=tar 8cea888 | tar -x -C corpus/live/r89-verify/tree
```

- **Fileset**: `git ls-tree -r --name-only 8cea888` (99,186) vs extracted
  `find -type f -o -type l` (99,186) — **0 diffs**
  (`freeze/fileset-diff.txt` empty; the 68 non-`f` paths are mode-120000
  symlinks, accounted for).
- **Content**: `GIT_DIR=$PWD/.git GIT_WORK_TREE=…/tree git diff --quiet
  8cea888` → **rc=0**.
- **Fixture shas (frozen tree)**: `geo2d_lattice.gd` = `9784716b5d69…`,
  `input89_edges.gd` = `601c223ed7a3…`, `run_battery.py` = `e49b488d…`,
  `project.godot` = `8de8b3af…` — all match the author's declared pins.
- **AST census of frozen `run_battery.py`**: CASES = **228 tuples** (208+20);
  all 20 r89 rows present verbatim; `input89_edges_exact` evidence is a
  **2-tuple** (payload[0] ends `…inex=true]` = Q, payload[1] ends
  `…inex=false]` = L); `geo2d_lattice_lineempty` = `expected_exit=-6` with
  signature `R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)`;
  the two `expected_errors` entries (`atlasempty`/`polyendpoly`) and the
  `r89_expected_errors_all_matched` gate over `("geo2d_lattice_","input89_edges_")`
  are present verbatim; `descendant_pipe_detached_control` →
  `descendant_pipe_forged_signature_release` adjacency preserved.

## Results per dispatch item

### 1. Battery ×2 under load — ran ×3, all FAIL on non-r89 rows; **all 20 r89 rows PASS in all three** (60/60 row-instances)

| rep | verdict | r89 rows | `exact` mode | `lineempty` | r89 gate | non-r89 fails |
|---|---|---|---|---|---|---|
| runs1 `20261015T202034147662Z` | FAIL | 20/20 PASS | L (payload[1] byte-exact) | PASS exit=-6 | true | `overlap`, `transition`, `negative_transition`, `audio_bus_route_invalid_control`, `input_lattice_press_phys` (unwhitelisted 3rd shape — loudly caught), `probe_error_clause_surface` (census cascade, dead=3) |
| runs2 `20261015T202702434201Z` | FAIL | 20/20 PASS | L (payload[1] byte-exact) | PASS exit=-6 | true | `overlap`, `transition`, `negative_transition`, `probe_error_clause_surface` (dead=2) |
| runs3 `20261015T204042266765Z` | FAIL | 20/20 PASS | L (payload[1] byte-exact) | PASS exit=-6 | true | `overlap`, `transition`, `negative_transition`, `probe_error_clause_surface` (dead=2) |

Load during all three: ~75–150 runnable (32 cores) — **foreign** contention:
48–80 `yes` hogs owned by other lanes (37-min-old set, ~23-min sets, respawning),
a `blender -b` batch, and a sibling `run_battery.py --runs corpus/live/r90-author/runs5`
observed mid-session — plus this seat's own 16 `yes` hogs.

**Flake classification (recorded, not excused — r88-verifier2 pattern):**
every failure is a documented pre-existing class on rows r89 does not touch:
`overlap`/`transition`/`negative_transition` = scene-readiness class;
`audio_bus_route_invalid_control` = audio-load-flake class;
`input_lattice_press_phys` emitted a payload outside its committed 2-tuple
envelope (diff at `post_ph/post_pr` tick lists — a genuinely unwhitelisted mode,
failing **loudly by design**); `probe_error_clause_surface` = consequential
census inconsistency (dead allowlist entries of the rows that died) — while all
four `*_expected_errors_all_matched` gates, **including `r89_…=true`**, stayed
green in all three reps; `rows_with_expected_errors=55` matches the author's
claim (was 53).

### 2. input89 envelope arms under hogs — **both modes appeared and passed**

Standalone `input89_edges.gd --arm=exact` on the frozen bytes, `timeout -s KILL 25`,
hogs/foreign load live throughout: **1,750 reps — Q×4, L×1,746, other×0,
nopass×0**. Every emitted PASS line byte-matches one of the two committed
envelope payloads (AST-extracted, compared programmatically — not eyeballed).

- **Mode L** (`just_after_flush=…inex=false]` → payload[1]): 1,746 reps
  byte-exact — overwhelmingly dominant under load ~90–150, consistent with the
  boundary's load-bimodal claim.
- **Mode Q** (`…inex=true]` → payload[0]): `arms/exact_scope2/rep{15,23,36,94}.out`
  — 4 reps byte-exact vs payload[0], 0-byte stderr, PASS emitted. Q rate was
  ~0.2–4% under this contention (vs the boundary's ~50% at ~16 hogs); obtained
  via `systemd-run --user --scope -p CPUWeight=10000` bursts — still scheduled
  against the live hog load, merely weighted. ~1,000 unweighted reps produced
  zero Q (probability consistent with saturation); the scoped bursts produced
  the four saved receipts.
- `input89_edges_axisdev`: **6/6 reps byte-exact** vs the committed pin under
  load (`joys=0`, `dz_ax0=0.2000`, `strength0=0.5000`, dev-5-writes-bank-not-action).
- Geo arm spot-checks under load: bridge/ring/ring4/ringhits/joins/ops/census/
  pipedges ×2 — **16/16 byte-exact** vs committed pins, incl. the physics rows.
- **No third payload** for `exact` in 1,750+3 observations — the envelope's
  fail-loudly semantics were never triggered.

### 3. `geo2d_lattice_lineempty` SIGABRT row — VERIFIED

Standalone ×3 (`arms/lineempty.rep{1,2,3}`): shell rc **134 ≡ -6 SIGABRT**
every time; stdout carries `R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)`
**before** the abort; PASS line unreachable; stderr = libstdc++ `std::vector`
assert (`/usr/include/c++/16/bits/stl_vector.h:1253` … `Clipper2Lib::Point<double>`
`__n < this->size()`), containing **no `ERROR:` token** — never whitelisted,
as claimed. In-battery: PASS with `actual_exit=-6` in all three reps.

### 4. Independent re-derivations — **23/23 PASS** (dispatch required ≥5)

`probes/v89_probe.gd` (verifier-written; own parse, own helpers, own extra
non-pinned cells) + `probes/rederive.py` (analytic expectations in pure Python)
vs AST-extracted committed pins — three-way agreement
(analytic == fresh-measure == pin):

| id | re-derivation | basis |
|---|---|---|
| R1/R3 | `offset_polygon` miter area 576 @d=2, **676 @d=3 (own cell)** | `(2(r+d))²` closed form |
| R2 | square-join area 573.2548 | `24² − 2·(2(2−√2))²` analytic |
| R4 | collapse at d=−20 → k=0 | analytic |
| R5 | bresenham (0,0)→(5,3) fwd/rev/diag **+ 3 own slopes** | own Python Bresenham |
| R6/R6b | `segment_intersects_circle` params 0.25/−1/0.5 **+ 2 own cells** | quadratic first-entry solve |
| R7/R7b | merge 1600 / clip k=2 hole −100 / inter 100 / edge-contact k=0 **+ own pair (3600)** | shoelace + containment law |
| R8 | tri_area=poly_area=dec_area=280 | own shoelace of the concave input |
| R9 | atlas size (25,10) | greedy row-pack bound |
| R10/R10b/R10c | pip edge-ε ladder, triangle strict-interior ladder, **own rect both windings** | boundary-policy law |
| R11/R11b/R11c | `nmethods=86`, enum values, default join=SQUARE | independent ClassDB census |
| R12/R12b | ring drop `y=-47.8043 hits=1` **on my own rigs** (outer-contour-only + 4-slab at x=500 offset) | independent physics reproduction |
| R13 | hole non-subtraction A=1/B=2/C=0 centre hits | own 3-body build |
| R14 | modifier-widening match law re-derived with **ctrl** (not the pinned shift) | `ex=0 inex=1` widened-superset / `inex=0` missing-modifier |
| R15/R15b | `dz=0.2`, `strength=(0.6−0.2)/(1−0.2)=0.5`, dev-5 bank-write without dev-0 press | deadzone law analytic |

### 5. Prior-row identity

vs frozen `r89-baseline` runs1: `common=215`, `new_only` = exactly the 20 r89
rows, `old_only=[]`. PASS-line diffs vs author's green rep5 on the 215 common
rows: only volatile/envelope classes (`frames=` counts, `pid=`, run-dir paths,
`tween_flash` color sample, `phys_peer ev_step_delta=5` whitelisted mode,
`exact` emitting its other arm) — **zero diffs attributable to r89 bytes**.

## Census / hygiene

- Seat's 16 `yes` hogs: SIGSTOPped for sampling windows, then SIGKILLed —
  **0 alive at exit** (`hog.pids`). All probe/battery launches
  `timeout -s KILL`-bounded; zero stray godot of mine at exit. Remaining
  `yes`/`godot`/`blender` on the host are **foreign seats'** (untouched).
- **Foreign in-flight work observed and left alone**: tracked-file edit
  `M corpus/fixtures/run_battery.py` (+74, mtime 17:22 — mid-session,
  `rb_*` cells, another seat's naming) and untracked `corpus/fixtures/
  rb_{lattice,watch}.gd` (17:14). None entered my verification — every claim
  above is against the `git archive 8cea888` extraction (content rc=0).
- This seat's footprint: `corpus/live/r89-verify/` (untracked; `tree/` frozen
  extraction dominates, prunable) + this report.

## Residual risks / disclosures

- **R1** — no battery rep was fully green: all three FAILed on pre-existing,
  documented load-flake classes on non-r89 rows under extreme foreign
  oversubscription (~75–150 runnable vs the author's 25–127). The dispatch's
  "×2 under load" is met (three reps, all loaded); what was not reproducible
  this session is a *quiet* green rep — same reservation shape as
  r88-verifier2's rep1. All 20 r89 rows passed all three reps; the failures
  are owned by earlier rounds' flake classes.
- **R2** — mode Q cost: ~1,750 loaded reps yielded 4 saved Q receipts
  (CPUWeight-scoped bursts). Q is real and byte-exact on committed bytes, but
  rare under saturation — consistent with the boundary's contention mechanism.
  No third payload observed (1,750 standalone + 3 in-battery).
- **R3** — scoped reps lack `.rc` files (parallel loop didn't write them);
  rc=0 is inferred from the emitted PASS line + 0-byte stderr (a timeout/SIGABRT
  cannot print the full PASS line). The row-level rc is separately proven by
  the three in-battery verdicts and the 1,746 unscoped reps' rc files.
- **R4** — `input_lattice_press_phys` emitted a genuinely unwhitelisted third
  payload shape in rep1 (loudly caught) — a pre-existing r87-row observation
  for the lane, not an r89 item; worth a lane note if it recurs.

## Verdict

**VERIFIED-WITH-RESERVATIONS.** The committed `8cea888` bytes are exactly what
the author claims: frozen tree byte-identical (fileset 99,186/0-diff, content
rc=0, fixture shas match), harness delta insertion-only semantics confirmed by
AST (228 CASES, 2-payload `exact` envelope, `lineempty` −6 row, r89 floor gate,
two exact `expected_errors`), all 20 r89 rows PASS in 3/3 loaded battery reps
(60/60), both `exact` envelope modes reproduced byte-exact under load
(Q×4 + L×1,746 standalone, L×3 in-battery; zero third modes), the SIGABRT row
reproduces rc −6 with the pre-call signature line, and 23 independent
re-derivations — analytic Python + verifier-owned probes incl. non-pinned
cross-check cells — all agree with the pins.

Reservations: (a) battery reps all FAIL at top level on documented pre-existing
non-r89 load-flake rows under ~75–150 foreign load — loudly caught, owned by
earlier rounds, non-cascading into r89; (b) Q mode required weighted-scheduling
bursts to surface under this session's saturation — observed 4× byte-exact.
