# r98 author — the CanvasItem draw/transform lattice landed: 32 rows (15 scout + 16 boundary + 1 author) on the boundary-surviving claims

Seat `AUTHOR` (lane `r98-author`) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, `RendererDummy`,
60 physics ticks/s, 64×64 `--script` root viewport). Worktree
`~/Projects/shokunin/game-dev-2d-shokunin-wt-r98`, branch `wt-r98` at **`89f85ed8`**
(*r96 author*) — **nothing committed, nothing staged**.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript/Python language server
on this host; `definition`/`references`/`hover` were **unavailable for every file touched**.
No symbol work was required: the battery edit is insertion-only (32 new CASES tuples, three
`expected_errors` entries, one floor gate) with no rename or definition change, so the
semantic checks are `ast.parse` plus the battery's own run.

## Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/canvas_lattice.gd` | `866480a1aaa0a385ad5a0e56a3066af4e5341db2e4ab5a5963366aef949394f0` (791 lines) | **byte-copy** of the frozen r98-scout probe `corpus/live/r98-scout/probes/canvas_lattice.gd` (`cmp` clean; hash = the scout's own manifest entry; the boundary re-ran these exact bytes in all 7 of its modes) |
| `corpus/fixtures/r98b_attack.gd` | `2e71c7158c4f53dbaf5497798cef5cea7769c5799b443ffa5b3a2b289e95a2f8` (822 lines) | **byte-copy** of the frozen r98-boundary attack probe (manifest entry + `cmp` clean) |
| `corpus/fixtures/r98b_rksenum.gd` | `7bb519025cba6bb2102fcc96eaf72938955fa180d4b52871f76b12742174f76a` (68 lines) | **byte-copy** of the boundary's one-off R·K·S enumeration probe (manifest entry + `cmp` clean) |
| `corpus/fixtures/r98c_flush.gd` | `c038f748a8572e4164fc0f6586199805b60f90929bdbed742bfcb7be28e1932e` (272 lines) | **new**, this seat — the boundary's corrected flush law reached in the battery's own launch shape (see below) |
| `corpus/fixtures/run_battery.py` | tracked, `git diff --numstat` = **`150 0`** | insertion-only: r98 comment header + 32 CASES tuples + 3 `expected_errors` entries + `r98_expected_errors_all_matched` |
| `reports/round-98/r98-author.md` | this report (new, untracked) | — |

`project.godot` untouched. `git status --porcelain` shows exactly the four new fixtures,
` M corpus/fixtures/run_battery.py`, `?? corpus/live/r98-author/` and this report; no other
tracked file was written and `corpus/fixtures/__pycache__` is unchanged.

## Boundary-driven encoding decisions (the falsifications applied)

| scout/boundary claim | boundary verdict | encoding consequence |
|---|---|---|
| L1 "`queue_redraw()` is an **end-of-frame** coalescing flush, at most once per frame" | **CONFIRMED for process-step queues; REFUTED-SCOPE for physics-step queues** — ff1: 359 draws / 359 ticks / 6 frames; `slow`: 37/37/6; the scout's ladder never separates a queue from a tick | the scout's `queue` row lands in its **declared prefix form** (cut before ` events_tail=`); the corrected law gets its own cell — `r98c_flush` blocks the process step with `OS.delay_msec(80)` (the in-process equivalent of the boundary's `--frame-delay 100`, since the battery launches rows with **no** engine pacing flags) and pins `multitick_frames_ge2=1 draws_eq_ticks=1 draws_gt_frames=1 max_draws_per_pf_ge2=1 d_phf_delta=0` |
| Hazard #2 "hidden items silently drop queued redraws" | **CONFIRMED for a synchronous queue+hide; scope widened** — a tick-separated hide in the *same* process frame still draws (`hide_ticksep_n=1`, `hide_span_pf=0`) | the frozen `hide_before_flush_n=0` stays in the scout row; `r98b_qflush_suppress` pins `hide_ticksep_n=1 hidden_across_tick_n=0 show_after_tick_n=1`; the qflush head row stops before `coalesce_draws=` |
| L4 "a zero scale reads back as a **~2e-5** epsilon" | **REFUTED as a constant; CONFIRMED as `1e-5 × parent scale`, per axis** | `r98b_epssweep` pins the whole `eps_exact` chain (ps 0.001→1e-8 … ps 100→1e-3) plus the per-axis degenerate cases and the angle survival |
| L3 "`get_transform() == Transform2D(r,s,k,p)`" / "the explicit `R·K·S` product matches" | **CONFIRMED for non-degenerate scales (125/125); REFUTED for degenerate scales (75/75 fail)**; the `rks=1` exact pin is float-fragile (60/125 non-degenerate combos differ, max component diff `4.77e-7`) | `r98b_skewgrid` pins `ctor_fail_n=75 ctor_fail_z=75 ctor_fail_nz=0 rks_fail_n=72 …` and the zero-scale matrices; `r98b_rksenum` pins the fragility count; the scout's `xform_skew` row is kept as a measurement (its own matrices are unchanged) |
| L5 "global setters inverse-compose" | **CONFIRMED matrix-level (global round-trip ≤1e-4); local readbacks under a non-uniform parent are shear decompositions, not naive inverses** | `r98b_gskew` pins `gs_local=0.0258`, `gr_local=1.1808 gr_local_skew=0.0258`, `gsc_local=(1.7184,0.7131)` vs the uniform-parent naive inverses |
| L9 "`>= MAX` refused with ERROR, previous value kept"; "negative stored as its uint32 cast" | **CONFIRMED + generalized** — every prior value survives, `== MAX` is refused, `INT_MIN→2147483648`, recovery works, repeated refusal holds | `r98b_clipmatrix` pins the full `stay99`/`neg`/`neg_prop`/`recover` vectors + `max_const=3`; one exact allowlist entry covers the 6 ERROR lines per run |
| L10 "reparenting emits the full re-entry set" | **CONFIRMED with a flag condition** — the set carries `35` only with `set_notify_local_transform(true)` | `r98b_notifyphase` pins `rep_tick`/`rep_frame`/`back_*` **with** `35`; the scout's `notify` row is landed unchanged (its node has the flag off, so its set legitimately lacks `35`) |
| F12/§3.14 the context-dependent redraw latch | **CONFIRMED; tick-phase-invariant and one-shot** (`t1`/`t3`/`imm` all trigger; a second transform write does not) | five `r98b_latch_*` rows (canon, t1, t3, imm, second) |
| (r95 lesson) anything claimed "stable" across ticks | **no r95-style cycle found** — 15/15 scout cells byte-identical across 7 modes; the only phase-varying observables are tick-driven grouping keys | `r98b_visphase` pins the visibility ladder under both schedulers; qflush/qorder pin **only** keys the boundary's 7-mode table shows invariant |

## `run_battery.py` changes (insertion-only, `git diff --numstat` = `150 0`)

1. **CASES 419 → 451 tuples** (results rows 426 → **458** incl. the 7 meta rows): the insert
   is exactly three hunks — **123 lines** at `CASES` (a 59-line comment header + 64 tuple
   lines) inserted **after `r96b_seed_seedcheck`, ahead of the crash/descendant tail**, then
   **17 lines** of `expected_errors` entries and **10 lines** of floor gate in `main()` —
   `descendant_pipe_detached_control`'s sleep-8 gap stays adjacent to the meta probes; the
   final four CASES tuples are untouched.
2. **Signature forms**: 27 full `PASS` lines, **3 declared gating prefixes**
   (`r98_canvas_queue` cut before ` events_tail=`, `r98b_qflush` cut before ` coalesce_draws=`,
   `r98b_qorder` cut before ` stagger=`), **2 declared contiguous substrings**
   (`hide_ticksep_n=1 hidden_across_tick_n=0 show_after_tick_n=1`; `flat=CBACBA`). Every
   signature is derived byte-exactly from `corpus/live/r98-author/runs/quiet/*.rep1.out` by
   `make_author_rows.py`, never transcribed.
3. **`expected_errors` += 3 entries / 4 strings** (after the r96 block):
   `r98_canvas_clip` ×1, `r98_canvas_draw_refusal` ×1, `r98b_clipmatrix` ×1 (the same clip
   string as `r98_canvas_clip`) — every string byte-equal to an observed engine line on this
   seat's own receipts, matched 2/1/6 lines respectively in both green runs.
4. **Floor gate extended**: `r98_expected_errors_all_matched` covering
   `case.startswith(("r98_canvas_", "r98b_", "r98c_"))` — same named-by-round /
   covers-round-prefixes shape as r87–r96, so a dead r98 allowlist entry cannot pass
   silently. `True` in both final-bytes runs.

## New-cell inventory (32 rows)

### `canvas_lattice.gd` — scout-surviving cells (15)

`r98_canvas_{census, modulate, queue, draw_surface, draw_refusal, vis_chain, clip, zorder,
xform_skew, xform_mirror, xform_global, notify, draw_state, redraw_triggers,
redraw_context}` — the scout's own gating set: the 32-method draw surface, the three legal
draw contexts and their refusal ERROR, the queue ladder (`add_same/proc_same/coalesce_n/
from_draw_n/hidden_n/hide_before_flush_n/show_n/readd_n/outadd_n`), the visibility chain, the
`clip_children` readbacks (`refused_stays=1 neg_cast=4294967293`), local z-order readbacks
with the queue-order draw order, the `R·K·S` matrix pins, mirror/non-uniform/zero-scale
decompositions, the global-setter round-trip, the notification sets, canvas-space readbacks,
the five-write redraw table and the F12 latch.

### `r98b_attack.gd` — boundary cells (16 rows on 15 arms)

| case | arm | law pinned |
|---|---|---|
| `r98b_qflush_same_frame` | `qflush` | `same_pf=1 d_pf_delta=0 d_n=1` — a physics-step queue flushes inside the same process frame (invariant in all 7 boundary modes) |
| `r98b_qflush_suppress` | `qflush` | `hide_ticksep_n=1 hidden_across_tick_n=0 show_after_tick_n=1` — the tick-separated hide does **not** drop the draw; hidden-across-tick does; `show()` redraws once |
| `r98b_qorder_tree` | `qorder` | `tree=ABC|…` / `rev=|CBA|…` — draw-callback order is queue/creation order, stable per frame |
| `r98b_qorder_flat` | `qorder` | `flat=CBACBA` — the 3-tick staggered queue's flattened order, identical in all 7 modes (no r95-style cycle) |
| `r98b_latch_canon` / `_t1` / `_t3` / `_imm` / `_second` | `latch` | the F12 latch is tick-offset invariant (`tick_wait=1` and `3` both trigger), immediate same-frame, and one-shot (`second_n=0`) |
| `r98b_gskew` | `gskew` | global setters round-trip globally; local readbacks under a non-uniform parent are shear decompositions |
| `r98b_skewgrid` | `skewgrid` | the ctor identity fails exactly on the 75 degenerate combos (`ctor_fail_z=75 ctor_fail_nz=0`); zero scales read `1e-5·I`; y-basis convention for negative/`>π` skew |
| `r98b_epssweep` | `epssweep` | the epsilon law `global_scale = 1e-5 × parent_scale` per axis (5 parent scales × 3 degenerate scales), angles survive the clamp |
| `r98b_clipmatrix` | `clipmatrix` | refusal keeps every prior value, `== MAX` refused, negatives cast to uint32, property path agrees, recovery works |
| `r98b_notifyphase` | `notifyphase` | notification sets are scheduler-independent (`move_tick`/`move_frame`, `rep_tick`/`rep_frame`, `back_*`) and carry `35` when local-transform notifications are on |
| `r98b_visphase` | `visphase` | the visibility ladder's counts under process-frame vs physics-frame waits (`draws_total=5` / `tick_draws_total=5`) |
| `r98b_rksenum` | one-off | the exact `R·K·S` pin is float-fragile: `nz_fail_n=60`, `sign_pairs=++=24,-+=12,+-=12,--=12` |

### `r98c_flush.gd` — the corrected flush law in the battery's own launch shape (1)

`r98c_flush` — 80 ms process-step block → ~5 physics ticks per process frame, then:
`multitick_frames_ge2=1 draws_eq_ticks=1 draws_gt_frames=1 max_draws_per_pf_ge2=1 same_pf=1
d_pf_delta=0 d_phf_delta=0 selfq_draws=1 sync_coalesce_n=1 hide_sync_n=0 hide_ticksep_n=1
hide_ticksep_same_frame=1 hidden_across_tick_n=0 show_after_tick_n=1 bounded=1`.
The two discriminating keys are `draws_eq_ticks` (the per-physics-step hypothesis) against
`draws_gt_frames` (the per-frame hypothesis refuted), and `d_phf_delta=0` (the draw lands in
the *same physics frame* as the queueing tick — a per-frame flush would read a later tick
counter). `sync_coalesce_n=1` re-pins the scout's coalescing **inside** the multi-tick regime:
three synchronous queues in a process step still produce one draw.

## Deliberately NOT authored

- **`r98b_env`** — a launch-mode fingerprint by construction (`ph5` measured 2…298 across the
  boundary's 7 modes); it pins no law.
- **qflush's `coalesce_draws` / `coalesce_eq` / `frames_with_tick` / `ticks_window` /
  `distinct_draw_pf` / `max_draws_per_pf` / `hide_span_pf` / `hide_same_frame`** and
  **qorder's `stagger` / `stagger_off` / `stag_groups` / `stagoff_groups`** — tick-phase
  dependent *within* a batch and *across* batches (both classes re-measured rep-to-rep in
  this seat's own 186 receipts); pinning them would pin the host's scheduling.
- **the scout's full-line `queue` tail** (`events_tail=…`) — frame-number plumbing; the
  gating prefix is the law (the full line was verified stable, but the boundary's own §6
  recommends the prefix).
- **any effective/composed observable** — effective z order, effective modulate, sorted draw
  order, draw-transform state: none has a headless readback.
- **the scout's and boundary's scope notes as replacements** — the boundary's §6 says
  explicitly "nothing here changes the scout's 15 rows"; the corrections are additive rows
  plus comment scope.

## Evidence

- **Cell matrix (the narrow behavioral check)**: 31 cells × 2 reps × 3 batches
  (`quiet` default launch / `load` +16 own hogs / `munged` with the battery's project-name
  munge) = **186 runs, 0 × rc≠0, 0 timeouts, 0 stray probes**; every run bounded
  `timeout -s KILL 20`; wall times 0.5–0.7 s per scout/attack cell, 2.6 s for `r98c_flush`
  (battery bound: 8 s). Receipts: `corpus/live/r98-author/runs/{quiet,load,munged}/`.
- **Row verification**: `python3 analyze_r98author.py` classifies **every** row against
  **every** receipt of its cell with the **production** `classify_process` extracted verbatim
  (AST) from `run_battery.py` (segment sha256 `749fa0607e7707e6…`, the same segment
  r89/r90/r91/r95/r96 pinned) → **`ROWS=32`, every signature 6/6 receipts, `REJECTED=[]`**.
  The analyzer also reports the six rep-unstable keys (the exclusion set) and
  `NONZERO_RC=[]`.
- **`r98c_flush` pre-landing stability**: 3 quiet reps + 8 reps under 16 own hogs on a host at
  loadavg 54–67 → **11/11 byte-identical PASS lines**, 0 B stderr, 2.6–2.7 s wall.
- **Battery run A** (`corpus/live/r98-author/battery/20261016T085050725365Z/verdicts.json`,
  final bytes): **458/458 PASS, 0 FAIL**; all **32 r98 rows PASS**; payload `verdict: PASS`;
  gate `r98_expected_errors_all_matched=true`; allowlist census: the three r98 entries
  `dead_in_run=false` with `matched_lines` 2 / 1 / 6 and `bare_classification_rejects=true`
  (the rows genuinely need their allowlist).
- **Battery run B** (`corpus/live/r98-author/battery/20261016T090007095328Z/verdicts.json`,
  identical bytes — sha of `run_battery.py` and all four fixtures re-checked between runs):
  **458/458 PASS, 0 FAIL**; all **32 r98 rows PASS**; payload `verdict: PASS`; gate
  `r98_expected_errors_all_matched=true`; `dead_entry_count=0`; the three r98 entries again
  matched 2 / 1 / 6 lines with `dead_in_run=false` — second green on the same bytes.
- **Mutation check (does the new row actually detect its mechanism?)**: on a scratch copy,
  the one-line mutation `pace.delay_ms = 80` → `= 0` flips the payload to
  `multitick_frames_ge2=0 draws_gt_frames=0 max_draws_per_pf_ge2=0
  hide_ticksep_same_frame=0`; the landed row signature does **not** match that output and the
  production `classify_process` **rejects** the mutant while accepting the clean receipt
  (`corpus/live/r98-author/mutants/`). The multi-tick regime is therefore caused by the
  process-step block, not incidental.
- **Insertion-only proof**: `git diff --numstat corpus/fixtures/run_battery.py` → `150 0`;
  `git diff -U0 … | grep -c '^-[^-]'` → `0`; `ast.parse` clean; CASES 451 tuples with zero
  duplicate case names (checked by executing the CASES assignment).
- **Byte-copy proof**: `cmp` of all three byte-copy fixtures against the upstream probes is
  clean and their sha256 values equal the upstream manifest entries
  (`corpus/live/r98-scout/manifest.sha256`, `corpus/live/r98-boundary/manifest.sha256`).
- **Independent probe (frozen `probeParent` dispatch, exactly one)**: one read-only
  `ufo-labrat` seat audited this seat's final state — see §"Independent probe" below.

## Independent probe (frozen `probeParent` dispatch) — exactly one

Dispatched **once**, read-only, no writes and no engine launches, with one bounded
falsifiable hypothesis: *the landed block is exactly the 32 rows the receipts and this report
claim, insertion-only, with no dead allowlist entry, and every claimed byte-copy really is
byte-identical to its upstream probe.* Its verdict on the final state: **7/7 checks
CONFIRMED, no counterexamples**, with two self-declared bounded caveats —

1. **insertion-only: CONFIRMED as a contiguous additive block** — the r98 CASES block sits at
   `run_battery.py:1228–1350`, spliced between `r96b_seed_seedcheck` and
   `crash_spontaneous_sigabrt`; the allowlist keys and the floor gate are additive shapes at
   their declared sites. *Caveat (its seat had no exec):* the literal `-0` was not runnable
   there — this seat measures it directly (`150 0`, `grep -c '^-[^-]'` = 0).
2. **row census: CONFIRMED** — 32 r98-prefixed tuples (15 `r98_canvas_*` + 16 `r98b_*` +
   1 `r98c_flush`), identical to `author-rows.py.txt`, zero duplicate names; CASES=451
   corroborated by run A's 451 case `PASS` lines.
3. **signature traceability: CONFIRMED, measured** — each signature greps to exactly its own
   cell's 6 receipts (32/32 rows, zero misses, zero foreign-cell hits), corroborated by
   `analysis.txt` (`cells=31 receipts=186`, `hits=6/6`, `REJECTED=[]`).
4. **byte-copy chain: CONFIRMED at manifest level, bounded at file level** — all three fixture
   hashes equal the upstream manifest entries, and bounded file comparisons found no
   divergence (`r98b_rksenum.gd` byte-identical over all 68 lines; the two larger pairs
   identical in head/tail with equal total line counts). *Caveat (no exec):* literal sha256
   equality was not runnable there — this seat measures it with `sha256sum`/`cmp` (clean).
5. **allowlist floor: CONFIRMED** — the three r98 census rows matched 2 / 1 / 6 lines,
   `dead_in_run=false`, `dead_entry_count=0`, gate `true`.
6. **battery verdict: CONFIRMED** — run A's verdicts.json has no non-PASS verdict anywhere,
   all 32 r98 results PASS, payload `PASS`, log `EXIT=0`.
7. **adversarial: no counterexample found** — the two substring signatures do not bleed into
   any other cell (`qflush_suppress`'s fragment does not match `r98c_flush`, whose line
   interposes `hide_ticksep_same_frame=1`; `flat=CBACBA` matches only `r98b_qorder`), and the
   shared latch key triple is disambiguated by the row prefixes. Its one residual caution:
   a *reordered* output containing the same contiguous run would still satisfy a substring
   row — no such receipt observed.

Advisory only; it wrote nothing. Both caveats are covered by this seat's own direct
measurements quoted above.

## Files changed

- `corpus/fixtures/canvas_lattice.gd` — **new**, byte-copy of the frozen r98-scout probe
  (sha `866480a1aaa0a385…`).
- `corpus/fixtures/r98b_attack.gd`, `corpus/fixtures/r98b_rksenum.gd` — **new**, byte-copies
  of the frozen r98-boundary probes (shas above).
- `corpus/fixtures/r98c_flush.gd` — **new**, this seat's probe (sha `c038f748a8572e41…`).
- `corpus/fixtures/run_battery.py` — `+150/−0` (r98 comment header, 32 CASES tuples,
  3 `expected_errors` entries, `r98_expected_errors_all_matched`).
- `corpus/live/r98-author/**` — driver, probes, 186 cell receipts, analyzer, builder,
  splice script, RECEIPTS.md, manifest.
- `reports/round-98/r98-author.md` — this report.

## Remaining risks / blockers

- **`r98c_flush` depends on the in-process delay producing multi-tick frames.** At 60 tps an
  80 ms process-step block yields ≈5 ticks/frame — a >4× margin over the ≥2 the row needs,
  and the tick rate is fixed by the engine, not by host speed (a slower host only adds
  ticks). Measured 11/11 identical pre-landing plus both battery runs; `bounded=1` fails the
  row loudly if a wait loop ever hits its cap.
- **`r98b_rksenum` pins a float32-derived count** (`nz_fail_n=60`, `sign_pairs=++=24,…`,
  max component diff `4.77e-7`): engine-version/CPU-pinned in the same class as the corpus's
  other float pins, and it is *about* the fragility of the scout's exact `rks=1` pin, so a
  future rounding change is a real signal rather than noise.
- **qflush/qorder rows are declared substrings/prefixes by construction** — they gate the law
  keys and deliberately leave the mode-varying keys ungated (documented in the block header);
  a future engine change to the tick/frame coupling would move those keys without failing
  these rows, which is why `r98c_flush` carries the discriminating booleans.
- **Upstream receipt provenance**: the r98-scout and r98-boundary `runs/` directories are
  **absent from this worktree** (their manifests list 471 / 1057 run artifacts, but only the
  non-`runs` artifacts still verify). This seat therefore re-derived every row from its own
  186 fresh receipts + two full battery runs, and relied on the upstream *probe bytes*
  (hash-verified) and the upstream `analysis.txt` / `author-rows.py.txt` payload dumps
  (hash-verified) rather than on the missing raw receipts. The same retention risk applies to
  `corpus/live/r98-author/runs/`; every payload is additionally quoted in this report and in
  `author-rows.py.txt`, both of which survive on their own.
- **Blockers: none.** Nothing committed; unrelated lanes' untracked `corpus/live/` artifacts
  untouched.
