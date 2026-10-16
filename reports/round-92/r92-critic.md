# r92 critic — adversarial review of committed `5900431` (14 `r92_tilemap_*` rows, 272-row battery)

Seat `CRITIC` (g2d lane r92) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7.
Reviewed commit **`5900431`** (HEAD at session start; parent `045d925`). **HEAD moved
mid-session** (sibling lanes landed `8a0da55` scribe, `c3c0d16` reviewer, `60b758b`
simplifier on top of it); the reviewed bytes are identified by sha, not by `HEAD`, and
the committed fixture bytes are unchanged at `HEAD` (`tilemap_lattice.gd` =
`a699138945ec7c1c…`, `run_battery.py` = `5e5182815e6e3c50…`, both verified with
`git show HEAD:<path>`).
**No tracked write, no commit.** Seat-owned artifacts: `corpus/live/r92-critic/**`
+ this report.

**Committed tree only.** Every harness-derived check below is pinned to a **frozen
copy of the committed tree** extracted with `git archive 5900431 -- corpus/fixtures`
(`frozen/corpus/fixtures/run_battery.py` sha256 `5e5182815e6e3c50…`,
`tilemap_lattice.gd` sha256 `a699138945ec7c1c…`, `project.godot` sha256
`8de8b3af9cc737ed…`) — all three byte-equal to `git show 5900431:<path>` and, at the
time of extraction, to the worktree files. The seat's scratch project `proj/` (used for
every arm launch) was copied from that frozen tree and still carries
`tilemap_lattice.gd` = `a699138945ec7c1c…` / `project.godot` = `8de8b3af…`; the two
batteries ran `frozen/corpus/fixtures/run_battery.py`, the mutant battery its
`frozen-mut/` copy.

**Worktree churn (not this seat's).** The worktree went dirty *mid-session* from a
sibling lane: `git status` now shows ` M corpus/fixtures/run_battery.py` — a **+111-line
r93 animation block inserted after the r92 rows** — plus untracked
`corpus/fixtures/anim_lattice.gd` and `corpus/fixtures/r93b_anim.gd`. Nothing in this
report reads those bytes: every check is pinned to the frozen `5900431` copy above, and
`git status --porcelain -- corpus/fixtures` was empty when the copy was taken. This seat
wrote nothing outside `corpus/live/r92-critic/**` and this report.

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host
(same as every prior r89–r92 seat); every `file:line` below is engine-emitted `at:`
text. The change under review is one new fixture file plus an insertion-only harness
block — no symbol-aware rename was required; hand analysis + fresh-process execution
is the fallback in use.

**probeParent disclosure.** Exactly **one** read-only `ufo-labrat` (agent `60261732`,
depth-2, licence now exhausted) was dispatched with one bounded hypothesis —
*"every measured-claim token pinned in the 14 signatures is engine-returned; the r91
F3 class (probe-side boolean pinned instead of the measurement) does not recur"*.
Its substrate exposes no shell/exec, so it returned a **static read only** (no writes,
no descendants, repository untouched): **H1 CONFIRMED**, with `census
layer_no_collision_priority` and the object-identity/null predicates as the only
class-(b) tokens and `layer_props=n16[…]` flagged as the one count-vs-authored-list
pair. This seat re-ran its rank-1 item against the engine (§1 F5) and reproduced the
rest by inspection.

**Load regime.** Host carried foreign `loadavg 51–72` for the whole session, including
**two sibling lanes running their own full batteries concurrently** (observed in `ps`:
`r92-simplifier` fold-gate and `r92-verifier` arms) and 48 foreign `yes` hogs. This
seat added **16 named hogs for exactly one batch** (killed at end; `ps` shows 0
orphaned `yes` with ppid≠1; no stray Godot process left; `ulimit -c 0` throughout, so
no core files). Loadavg is recorded per batch in `runs/load.log`,
`runs/wall_batch.log`, `battery-rep{1,2}.log`, `battery-mut.log`.

---

## 0. What I ran — 126 seat Godot launches + 3 full 272-row batteries

| # | probe | receipts |
|---|---|---|
| 1 | all 14 arms ×3, battery launch shape (production classifier) | `runs/fresh.*` ×42 |
| 2 | `nav` ×3 at `--fixed-fps` 120 / 150 / 240 / 600 (envelope reachability) | `runs/ff*.*` ×12 |
| 3 | all 14 arms ×2 with **+16 seat hogs** (loadavg 64.6 → 72.6) | `runs/load.*` ×28 |
| 4 | `nullts` ×10 (contended window, wall-time distribution) | `runs/qnull.*` ×10 |
| 5 | crash-row wall batch: `nullts` ×8, `spontaneous` ×5, `lineempty` ×3 | `runs/wall.*`, `runs/wall_batch.log` |
| 6 | crash-path phase split (`arm` → marker → `handle_crash` → dump end → reap) ×5 | `runs/phase_nullts.log` |
| 7 | 12 fixture mutants, each in its own scratch project | `mutants/<name>/`, `mutants/receipts/` |
| 8 | harness mutants (pin / allowlist / fragment / exit perturbed on real receipts) | `mutants.json` |
| 9 | full battery, frozen committed tree, rep1 (loadavg 62 → 72) | `battery-runs/20261016T001931085761Z/` |
| 10 | full battery, frozen committed tree, rep2 (loadavg 59.6 → 53.7) | `battery-runs/20261016T002404467950Z/` |
| 11 | full battery, **atlas-refusal-poke removed** fixture (floor-gate mechanism removal + crash-site line shift) | `battery-mut-runs/`, `battery-mut.log` |

Plus seat scripts (`scripts/audit.py`, `probe.py`, `mutants.py`, `crash_wall.py`,
`phase_probe.py`, `load_batch.sh`, `wall_batch.sh`) and one engine instrument
(`probes/props.gd`, run in the scratch project only). Production classifier segment
`classify_process` sha256
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` — the same byte
segment r89/r90/r91/r92 pinned.

---

## 1. Findings (ranked)

### F1 — LOW-MEDIUM · the crash row is the battery's slowest row, and its wall time straddles the battery's 8 s per-case bound under sibling-lane contention

The row's *claim* is fine and its bytes are fine; what is measured here is a **battery-verdict
risk** the landing adds one more instance of.

Nominal cost (seat receipts, quiet window): the 13 PASS arms run in **493–924 ms**
(mean 651 ms, 39 fresh receipts); `r92_tilemap_nullts_crash` is the slowest at
**1070–1213 ms**. Phase split
(5 runs, `runs/phase_nullts.log`): **startup 0.40–0.46 s → crash path 0.46–0.48 s →
post-dump 0.05 s → reap ≈ 0.96 s**. The crash path is the engine's crash handler, which
forks `sh -c "llvm-addr2line" <20 addresses>` and waits for it before printing the dump
and `abort()`ing (`ps` capture in `runs/` — the child inherits the parent's stdout/stderr
pipes). `llvm-addr2line` itself is cheap (**8–19 ms** for all 20 addresses, 3 seat runs);
the cost is the fork/exec + symbolization of a **182 MB** binary under page-cache
pressure.

Under sibling-lane contention the same row inflates **2.4–11.6×**:

```
wall_batch (loadavg 51, a foreign battery running):  nullts ms = 4549 5728 3453 11647 3368 2653 4880 8162   -> 2/8 over 8000
qnull      (loadavg ~54, foreign batteries running): nullts ms = 2157 2552 2378 4152 3393 8017 2998 7235 2256 3694 -> 1/10 over 8000
pre-existing spontaneous_crash_probe (10-frame dump): 5249 892 969 949 928                              -> 1/5 over 8000
pre-existing geo2d_lattice_lineempty (no Godot dump):  517 456 480                                     -> 0/3
```

The r92 dump is **20 C++ frames** vs the pre-existing spontaneous probe's 10 — the
deepest dump in the battery, hence the largest exposure. Consequence, measured on the
committed bytes: seat battery **rep2 went red on `r92_tilemap_nullts_crash` alone**
(`TIMEOUT after 8 seconds`, `actual_exit=None`) with a sibling battery running; rep1 was
green on that row, and every seat receipt produced for this report (42 fresh + 28 load +
12 regime + 10 qnull + 8 wall + 5 phase = 105 launches of which 28 are this row)
recorded the correct rc and signature. Of the 18 wall-timed standalone `nullts`
launches inside the contended window, **3 crossed 8 s** (2/8 in the wall batch, 1/10 in
the qnull batch) and none crossed the 20 s `timeout -s KILL` bound used there. The
author's 5 runs were green (their `verdicts.json` record **no** `error` field on any row
of any run).

Not a row defect and not a blocker — but the adjudication should know that a red
`r92_tilemap_nullts_crash` is *this* failure mode, and that the pre-existing
`crash_spontaneous_sigabrt` row failed the same way in seat rep1 (so the class is
host-wide, not r92-specific). Cheap future hardening: raise the per-case bound for
crash-handler rows (or retry once) in a later fold; the harness's 8 s is a single
global constant (`timeout_seconds = 60 if script.startswith("__godot_export") else 8`).

### F2 — LOW · the nav envelope is a mode-blind disjunction: a permanent production-mode regression still passes

The fold is landed exactly as directed (boundary §6 option 2) and is *closed*: the
`any()` disjunction admits only the two committed payloads, they differ in **exactly one
token** (`regions_f1=1` → `regions_f1=0`; 22 tokens each; `regions_f2=1` in both), and a
third value is rejected (mutant `nav_f1_third_value` → FAIL). Both payloads are
**reachable on the committed fixture** (seat receipts: `--fixed-fps 120` →
`regions_f1=1` ×3; 150/240/600 → `0` ×9; all 12 classify PASS).

What the envelope *loses* is measured: mutant `nav_f1_stuck_zero` — the fixture pinned
to the ratio≥2.5 mode forever — **PASSES**, and so does `nav_f1_stuck_one_ff`. Because
`any()` is order-insensitive, the comment's "payload[0] is the production/pinned mode"
is prose, not a gate: the harness cannot distinguish the production scheduler from a
`--fixed-fps ≥ 150` one. The claim that is now ungated is precisely the one-step
registration read; the settled law (`regions_f2=1`) and the
disable/re-enable/erase lever trio stay pinned in both payloads, and the author's
committed `fresh-reps` still *record* payload[0]. A future battery that wants the
production-mode read back would need a second nav row run in a pinned regime (or a
mode-discriminating receipt gate) — queue-worthy, not blocking. **The same fold is
cross-referenced by the r92 reviewer (F2) and simplifier (F8) from the opposite
direction** — payload[1] is unreachable in the battery's own launch shape — and by the
scribe (A2) as the absorb class; §3 reconciles the two views.

### F3 — INFO · the crash binding is a call-*origin* pin plus a literal stdout anchor

Three-directional, on the real capture (`mutants.json`):

| forgery | rc | `handle_crash: … signal 11` | `_nullts (…:927)` | arming marker | verdict |
|---|---|---|---|---|---|
| real committed run | **-6** | yes | yes | yes | **PASS** |
| `OS.crash()` at the same line (`nullts_foreign_abort`) | -6 | **signal 4** | yes | yes | **FAIL** |
| same null-deref, reached from `_run` (`nullts_foreign_cause`) | -6 | yes | **no** | yes | **FAIL** |
| same null-deref two frames deeper, reached *from* `_nullts:927` (`nullts_foreign_site`) | -6 | yes | yes (caller frame) | yes | **PASS** |
| no crash at all (`nullts_no_crash`) | 0 | — | — | yes | **FAIL** |
| crash one line lower (`nullts_site_line_shift`) | -6 | yes | **no** (`:928`) | yes | **FAIL** |
| raw `rc=-11` re-classification | -11 | — | — | — | **FAIL** |

So the row binds **"a signal-11 crash whose call originates at `_nullts:927` of this
fixture"** — a tighter binding than r91's teardown row (class-level glibc printer), and
the strongest available forgery (same rc, same site frame, same marker, wrong signal
class) is rejected by the header fragment. Two residuals, both benign but worth
recording: (a) the site fragment is a *caller*-frame token, so a crash **deeper** inside
the same engine call is admitted — that is the right semantics for a cause pin, but it
means the row does not require `_nullts` to be the innermost frame; (b) the pinned
stdout token `about_to_call_tile_data=1` is a **fixture literal**
(`_it("about_to_call_tile_data", "1")`), not a measurement — the measured precondition
`tileset_null=1` is emitted on stdout but *unpinned*, so the anchor proves only that the
probe reached the line before the call. The harness comment's claim that the row "is
bound to THIS null-deref, not merely to the -6 signal class" is therefore true for
*this fixture's* bytes and false as a general statement about the cause.

### F4 — INFO · harness comment says `rc=-11`; the row asserts `-6`

`run_battery.py` line 1237 (committed bytes): *"r92 null-TileSet SIGSEGV negative
control: binds the **rc=-11** to the engine's own signal-11 crash handler AND the
_nullts frame site…"*, while the CASES row is
`('r92_tilemap_nullts_crash', 'tilemap_lattice.gd', ['--arm=nullts'], **-6**, …)`. The
CASES-block comment is correct (`signal 11, and the engine crash handler's abort() exits
the process -6 (SIGABRT)`, and the measured scout-vs-battery `134` = 128+6 note). The
`required_stderr` comment contradicts the row it documents. Cosmetic, same class as the
r91 comment-formula defect; a one-line fix in a later fold. **Filed independently by the
r92 scribe as A1 — dedupe on fold.**

### F5 — INFO · `layer_props=n16[<13 authored names>]` pairs a measured count with an authored list of a different cardinality

Measured with a seat instrument (`probes/props.gd`, run in the scratch project):
`ClassDB.class_get_property_list("TileMapLayer", true).size() == 16`, and the returned
names are the **13 real properties** (`tile_map_data, enabled, tile_set,
occlusion_enabled, y_sort_origin, x_draw_order_reversed, rendering_quadrant_size,
collision_enabled, use_kinematic_bodies, collision_visibility_mode,
physics_quadrant_size, navigation_enabled, navigation_visibility_mode`) **plus 3 group
entries** (`Rendering, Physics, Navigation`). The fixture prints `n16[<the 13 names,
sorted>]` — so the token is internally coherent but the bracket list is **authored, not
read back**: a property *rename* with unchanged counts is invisible to the row (the
count flips loudly on add/remove, which is the discriminating part). The fixture does
read the instance list for `layer_no_collision_priority` (`get_property_list()` = 73
entries, `collision_priority` absent → `1`), so the name space is not entirely
unmeasured. This is the labrat's rank-1 exposure, verified; severity INFO (census row,
count-measured).

### F6 — INFO · WARNING-blindness is unchanged (author-disclosed)

The rejection clause is line-local on `"ERROR:"`; `nav`'s only stderr is the
`make_polygons_from_outlines()` deprecation WARNING (1 line, 0 `ERROR:`) and
`census`/`timing`/`quadrant` are clean (0 `ERROR:` / 0 `WARNING:`). Any number of
WARNING lines is verdict-inert for every row — pre-existing design, named by the scout
as hazard #11 and unchanged by this landing.

### F7 — INFO (lane note) · the battery's global verdict under contention is hostage to the pre-existing volatile classes

Seat rep1's non-r92 failures (`audio_bus_route_invalid_control` on a *different*
refusal line than its pinned one, `crash_spontaneous_sigabrt` TIMEOUT) cascaded into
`probe_error_clause_surface` via a dead audio entry and
`census_bare_classifier_consistent=False` — the same knock-on the author documents for
`negative_transition`. Rep2's `negative_transition` + the F1 timeout did the same. The
14 r92 rows were green in both runs except the F1 timeout. Lane note only.

---

## 2. What survived (positive verifications)

1. **Commit hygiene.** `5900431`: 136 files, **+5775 / -0**; `run_battery.py` **+161/-0**;
   `project.godot` untouched. CASES **251 → 265**; the 251 pre-existing tuples are
   byte-identical *in order* after removing the 14 r92 rows; the r92 block is contiguous
   at **CASES[247..260]**, immediately after `nav_lattice_teardown_clean` and ahead of
   `crash_spontaneous_sigabrt` (the descendant `sleep 8` gap preserved). 265 + 7 meta = 272.
2. **Fixture provenance.** `corpus/fixtures/tilemap_lattice.gd` is a byte-copy of the
   committed scout probe (both `a699138945ec7c1c…`, 929 lines); every boundary fold is
   row-side, as claimed.
3. **Fresh reproduction.** 42/42 receipts PASS through the production classifier
   (segment `749fa0607e7707e6`); the 9 allowlists are load-bearing on every receipt
   (`bare` classification rejects), the census finds **0 dead entries**, and the r92
   floor gate recomputes **True**.
4. **Byte-stability.** 126/126 seat receipts reproduce the committed author
   `fresh-reps` — 123 byte-equal, the 3 `nullts` stderr equal modulo ASLR addresses
   (identical 2122-byte length, identical 20-frame structure, identical tokens); stdout
   and stderr byte-stable across the 3 fresh reps for all 14 arms.
5. **Load invariance.** 28/28 PASS with +16 seat hogs (loadavg 64.6 → 72.6); fresh ↔
   load receipts byte-stable modulo ASLR; 0 orphaned hogs.
6. **Envelope.** Two payloads, one differing token, both reachable on the committed
   fixture (ff120 → `regions_f1=1`; ff150/240/600 → `0`; 12/12 PASS); a third value and
   a `regions_f2=0` mutant both FAIL; the payload diff cannot hide any other field
   because the rest of the 22-token line stays pinned.
7. **Tombstone encoding is measured, not asserted.** `enc_cell_moved` (a cell moved from
   `(7,-2)` to `(7,-3)`) and `enc_alt_field` (alternative id 1 → 0) both FAIL — the
   `two_bytes`/`alt_bytes`/`stride`/`tomb_*` pins are engine bytes.
8. **Crash row.** rc=-6 in 3/3 seat fresh reps, 3/3 author reps, seat battery rep1 and
   the mutant battery (where the row failed on the *moved site*, not the exit); both
   fragments on stderr **only** and the signature on stdout **only**; each direction
   rejects when moved (`nullts_stream_binding`: fragment-on-stdout-only → FAIL,
   signature-on-stderr-only → FAIL, either fragment deleted → FAIL); `rc=-11` → FAIL.
9. **Pins are discriminating (row not vacuous).** Perturbing any sampled pin token
   (`travel=…1.9531`, `stride=12`, `regions_f2=1`, `bad_src_readback=42`,
   `update_set_same_frame=hit`) makes the real receipt FAIL; dropping any single
   allowlist entry makes the real receipt FAIL.
10. **Floor gate is real and wired.** `r92_expected_errors_all_matched` is in
    `sf_discriminations`, `sf_meta_ok = all(sf_discriminations.values())`, and the prefix
    covers all 14 rows. Removing one refusal poke from the fixture leaves the row
    PASSing but kills its entry (`atlas_allowlist_dead`: PASS, 1 dead entry, gate
    **False**) — see §5 for the harness-evaluated confirmation.
11. **Author custody (read-only cross-check).** `corpus/live/r92-author/manifest.sha256`
    verifies **1510/1510**; `verify_author.py` re-run → 14 rows / 42 receipts / **0 fails**,
    same classifier segment.
12. **Both author batteries** (runs4/runs5) re-read: 272 rows, 0 fails, r92 14/14,
    gate True, `nullts actual_exit=-6` with both fragments.

---

## 3. Questions the dispatch implies, answered

**False-positive shapes (a row that passes when it shouldn't).** None found in the
committed bytes. Twelve fixture mutants and four harness-mutant classes (pin
perturbation, allowlist drop, stream-anchoring, exit-code) were attempted;
the only PASS-on-a-mutant cases are the two *declared* envelope modes (F2) and the
deeper-frame crash (F3, same cause). Every pinned measurement tested flips loudly when
perturbed.

**Scheduler-conditional pins the boundary missed.** None new: the boundary's ratio sweep
(13 conditions × 13 arms, 416 gated receipts) is reproduced at the ends here (ff120 =
payload[0], ff150/240/600 = payload[1]); the 12 non-nav rows are single-valued across all
70 seat launches and both batteries. The `_same_frame` lever tokens inside the pins are
the *claim* (one-physics-step law), not scheduler artifacts — measured invariant by the
boundary at ff1…ff900 and green in every seat receipt.

**Rows that pass only because a sibling process is alive.** None. All state is
in-process; the fixture touches no files (`OS.get_cmdline_user_args` only), no
descendants, no locks.

**Allowlist/census correctness.** Independently recomputed with the harness's own
`surface_allowed_error` semantics (verified identical to `classify_process`'s
`allowed_error` for the exact/comma shapes used): 9 rows / 18 exact entries, 0
comma-prefix entries, 0 dead in 42 receipts, every entry matched in every rep;
`cells` emits 4 identical `Method/function failed. Returning: p_coords` lines covered by
one entry (as disclosed). `census`/`timing`/`quadrant`/`nav` carry no entry and emit no
`ERROR:` line.

**Insertion ordering / prior-row identity.** Verified: contiguous insertion, ordering
preserved, commit deletion-free by construction.

**Cross-seat consistency.** Three r92 sibling reports landed *during* this session, on
top of the same commit — and the overlaps are convergent, not contradictory:

- **scribe A1 == this report's F4** (the `required_stderr` comment says `rc=-11` while the
  row pins `-6`), found independently.
- **reviewer F2 / simplifier F8 == this report's F2**, from the other direction: they
  measure that payload[1] is *unreachable in the battery's own launch shape* (no
  `--fixed-fps` flag) while this seat measures that payload[1] *is* reachable under
  `--fixed-fps ≥ 150` on the landed fixture (ff150/240/600 → payload[1], 9/9; ff120 →
  payload[0], 3/3). Together: the second payload is real (not dead code for the engine)
  and inert in the shipped harness (absorb-only there) — the fold's price either way.
- **scribe A10 (site token is line-bound) == the incidental result of this seat's mutant
  battery** (a one-line deletion above `_nullts` moved the site to `:926` and the row
  failed loudly with the correct rc).
- **scribe A5** ("42 receipts" vs 126 files) matches this seat's counts.
- The simplifier's SP2 ("payload[1] is required for the ff≥150 class") and this seat's
  `nav_f1_stuck_zero` mutant are the same measurement seen as keep-vs-cost.

One reconciliation item: the scribe reports its `classify_process` extraction as
`13473e6def6cd2da…`. On the reviewed commit — and on `HEAD` and on the current worktree
(r93 edit) — this seat, the author and the boundary all extract
**`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`** (1068 chars, AST
`ast.get_source_segment` on the `classify_process` FunctionDef). The two extractions
differ; whoever folds next should confirm the scribe hashed the same segment (this
seat's whole review is pinned to the 1068-char segment above, and it is byte-identical
in all four copies checked).

No sibling report contradicts anything measured here.

---

## 4. Verdict

**PASS-WITH-RESERVATIONS on the committed bytes `5900431`.** No blocking defect.

The four encoded folds are landed and measured: (1) the **nav 2-payload envelope** is a
closed, one-token-wide disjunction with both payloads reachable on the committed fixture
and a third value rejected; (2) the **nullts crash row** carries `rc=-6` + a two-fragment
`required_stderr` pin and a stdout anchor that together reject the strongest available
forgeries in three directions (foreign signal class, foreign call origin, no crash);
(3) the **tombstone encoding** is pinned verbatim and is measured, not self-asserted
(byte-level mutants flip it); (4) the **+9 `expected_errors` cases (18 lines) with the
floor gate** are load-bearing and wired, and the gate demonstrably flips when a mechanism
is removed. The commit is insertion-only, the fixture is a byte-copy of the frozen scout
probe, and the committed evidence verifies against its own manifest.

Reservations are robustness/evidentiary, not behavioural:

- **F1** the crash row is the battery's slowest row (nominal ≈1.0 s) and its wall time
  reaches 2.4–11.6× under sibling-lane contention, crossing the battery's 8 s per-case
  bound (3/18 wall-timed launches; the row alone reddened seat rep2). Host class — the
  pre-existing `crash_spontaneous_sigabrt` row failed the same way in seat rep1.
- **F2** the envelope is mode-blind: a permanent regression to the ratio≥2.5 read still
  passes; the production-mode read is now receipt-only.
- **F3** the crash binding is "signal-11 crash originating at `_nullts:927`", with a
  fixture-literal stdout anchor; a deeper same-cause crash is admitted.
- **F4/F5/F6** comment/exit-code contradiction, `layer_props` count-vs-authored-list,
  and WARNING-blindness — all cosmetic or pre-existing.

**Blockers: none.** Nothing here requires a change before the landing is folded; F1's
per-case bound, F2's second nav row, F4's comment and F5's measured name list are the
cheap follow-ups worth queueing.

---

## 5. ProbeParent labrat + the pre-registered hypothesis

The single labrat licence was used (agent `60261732`, depth-2, read-only). Its substrate
exposes **no shell/exec**, so it returned a **static read only** (no files, no processes,
repository untouched) and pre-registered H1: *every measured-claim token in the 14
signatures is engine-returned; no r91-F3-class probe-side boolean recurs.*

It answered **H1 CONFIRMED**, with a class-(b) table whose only non-trivial entry is
`census layer_no_collision_priority` (an existence predicate over the engine property
list) plus object-identity/null predicates whose underlying values are unprintable by
design (no RID/object printing policy), and it flagged
`layer_props=n16[13 names]` as a count-vs-authored-list pair. This seat re-ran that
rank-1 item against the engine (§1 F5: `DB_COUNT=16` = 13 properties + 3 group entries,
so the token is coherent but the list is authored) and confirmed the rest by inspection —
including that `two_arr_equals_bytes` is *not* blind (one operand's bytes are pinned
verbatim in the same line) and that the crash row's stdout token is a literal (§1 F3).

**Floor-gate mechanism removal, evaluated by the harness itself** (the r91 `noorphan`
analogue): the fixture with the atlas duplicate-`create_tile` poke removed was run
through the *unmodified committed harness* as a full battery (§0 row 11). Result:
`r92_tilemap_atlas` still **PASS**es, its `Cannot create tile…` entry is the **only**
dead entry (`dead_entry_count=1`), and the harness's own
`r92_expected_errors_all_matched` flips **False** — the single false discrimination in
the run, reddening `probe_error_clause_surface`. The gate is live, r92-scoped, and
catches a removed mechanism.

**Incidental confirmation of the site token's line-binding** (same run, unplanned): the
one-line deletion sits *above* `_nullts`, so the crash call moved to
`_nullts (res://tilemap_lattice.gd:926)`; the committed row then FAILed on the site
fragment with the *correct* rc (`actual_exit=-6`, `error=null`) — i.e. a fixture fold
that moves the crash site fails loudly rather than silently, exactly as the author
discloses. See `battery-mut.log` / `battery-mut-runs/`.

---

## 6. Evidence index

`corpus/live/r92-critic/` — `manifest.sha256` covers every artefact under the lane.

| artefact | path |
|---|---|
| this report | `reports/round-92/r92-critic.md` |
| frozen committed tree (git archive) | `frozen/corpus/fixtures/` |
| scratch project (battery launch shape) | `proj/` |
| fresh / regime / load / qnull / wall receipts | `runs/` |
| static audit JSON (commit shape, tables, census, gate) | `audit.json`, `scripts/audit.py` |
| mutant fixtures + receipts + harness mutants | `mutants/`, `mutants.json`, `scripts/mutants.py` |
| crash-path phase split / wall batch / load batch logs | `runs/phase_nullts.log`, `runs/wall_batch.log`, `runs/load.log` |
| full battery rep1 (272 rows) | `battery-runs/20261016T001931085761Z/`, `battery-rep1.log` |
| full battery rep2 (272 rows) | `battery-runs/20261016T002404467950Z/`, `battery-rep2.log` |
| mutant-fixture battery (floor-gate removal) | `battery-mut-runs/`, `battery-mut.log` |
| engine instrument for the census token | `probes/props.gd`, `runs/props.out` |
