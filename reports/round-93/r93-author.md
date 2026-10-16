# r93 author — AnimationPlayer + Tween authorability lattice landed (23 rows)

Seat `AUTHOR` (g2d lane r93) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.
Work is worktree-only — **nothing committed**. No `lsp` device / no GDScript
server on this host (same as r89–r92 authors); all semantic validation is
fresh-process execution + runtime introspection + engine diagnostics.

Scope per dispatch: land the AnimationPlayer/Tween lattice with **only
boundary-surviving claims** — overshoot values, the N-1 await law, the
crossfade weight law with step-granularity scope, DEFERRED/IMMEDIATE callback
split, negative controls. `run_battery.py` touched **insertion-only**
(`+111, -0`).

## Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/anim_lattice.gd` | `6a919ae04d4e754953b9f8067c49b74c46cf5f3bdc1dce76d4e29597faa2cd4a` (689 lines) | **byte-copy** of the frozen r93-scout probe `corpus/live/r93-scout/probes/anim_lattice.gd` |
| `corpus/fixtures/r93b_anim.gd` | `3c8dd8f10d6888e120c2420a3dcfc8c0867372ad0907d99d88b1eb98f1efd966` (466 lines) | **byte-copy** of the frozen r93-boundary attack probe `corpus/live/r93-boundary/probes/r93b_anim.gd` — needed because the boundary's new measurements (runtime overshoot, N-1 await law, physics-frame DEFERRED flush, await-interleaved manual clock) live in *its* arms, not the scout probe's |

`project.godot` untouched. No fixture folds — every boundary fold lands
row-side in the signatures.

## Boundary folds applied (r93-boundary, all measured)

1. **Runtime tweens OVERSHOOT — encoded, not clamped.** Boundary §7 falsified
   the scout's "runtime tween clamps" parenthetical: `r93_anim_overshoot`
   (`r93b_anim.gd --arm=purity`, full-line pin, byte-identical in 16/16
   boundary reps + 3/3 fresh) pins `overshoot=[back025=0.10286344587803
   (BACK/EASE_IN_OUT, *below* the start value),back050=5.5]` and
   `overshoot2=[spr050=10.510157585144 (SPRING/EASE_OUT, *above* the end
   value),spr100=10.0,ela025=9.11611652374268]`. The same row pins the
   no-clamp static path (`clamp=[neg=-5.0,over=15.0]`), extreme/negative
   `custom_step` deltas (`tiny=1e-8 px`, `huge` completes,
   `neg=0.0,neg_elapsed=-0.5` — negative delta does not rewind), and
   `accum1000=1.0` (1000×0.001 steps land exactly).
2. **N-1 await law — pinned at the only stable instance.** Boundary §9:
   `await process_frame` N times ⇒ N−1 applied steps; `x1=0.0` in 258/258
   frame runs. `r93_anim_await_offbyone` pins `idle=[x1=0.0` (the first
   awaited frame still reads the pre-play value); `r93_anim_physics_tick`
   pins the launch-invariant physics-side lattice
   `mixer_applied_10=10 phys=[y1=0.0,y2=0.0,y3=1.66666674613953,y6=6.66666698455811]`
   and `r93_anim_phys_delta` pins `phys_delta=0.01666666666667` (the 60-tps
   tick is launch-invariant while every process-side counter is a mode).
   Reads past the first await (`x2…x10`, `pos10`, `tween5`, `quick`) are
   modes — deliberately **not** pinned.
3. **Crossfade weight law with step-granularity scope.** `w_i=(i−1)/(N−1)`
   is pinned at three Ns in `r93_anim_blend_finished`
   (`finished_010`/`finished_005`/`finished_020` — same 1 s blend, different
   mid-values, so the pin itself encodes that mid-blend values are
   granularity-scoped) and the await-immunity extension in
   `r93_anim_blend_interleaved` (`interleaved_eq_plain=true`,
   `hard_after_frame=500.0`).
4. **DEFERRED flush routes — extended.** `r93_anim_deferred_flush` pins the
   boundary's four-lattice block verbatim: DEFERRED queues to the next
   process frame (`manual_def`), **also flushes on a physics frame**
   (`manual_def_phys` — new route, not in the scout), two advances before a
   frame still queue (`two_adv`), IMMEDIATE fires inside `advance()`
   (`immediate`). The frame-coupled `idle_lag` tail is a mode — not pinned.
5. **Manual clock under interleaved awaits.** `r93_anim_manual_clock_interleaved`
   pins the paused-tween + MANUAL-player step lattice with awaited
   process/physics frames between steps; `r93_anim_manual_clock_control`
   pins `inv=[…all true…] step_exact=[…all true…] unpaused_moved=true` —
   `unpaused_moved` is the non-vacuity control (the frame path is live).
6. **Mode cells pinned only at stable clauses** (scout §6.2 rule 4,
   boundary attacks 3/5/13): `r93_tween_process_stable`,
   `r93_anim_process_stable`, `r93_tween_phys_manual_step`,
   `r93_anim_process_manual` pin the clauses byte-verified in **every**
   committed receipt (16/16 boundary tweenproc/animproc, 9/9 scout
   canonical+loadtest). The load-fragile frame counters
   (`auto`/`paused`/`phys`/`idle`/`quick`/`caches_total`/`mixer_applied`
   counts) are **not** pinned. `--fixed-fps` is a **stabilizer** for these
   cells (collapses each to one byte-stable value), not a destabilizer —
   no row needs an envelope this round.
7. **All 15 scout gating rows carried verbatim** from
   `corpus/live/r93-scout/author-rows.py.txt` (`ROWS`, `rejected=[]` over
   54 canonical + 24 loadtest receipts), re-verified here against the
   boundary corpus: the 9 byte-stable cells' rep1 PASS lines appear in
   **14–16/16** boundary receipts each and the two mode cells' clause
   signatures in **16/16**.
8. **Negative controls carried inside rows** (no dedicated crash row this
   surface): `clamp_neg=-5.0`/`clamp_over=15.0` (no clamp),
   `deferred_adv=[]`/`disabled_track=[]`/`two_adv=[after=[],…]` (absent
   callbacks), `manual_frames=[0.0,0.0]` (MANUAL never auto-advances),
   `idle=[x1=0.0` (zero applied steps after one await),
   `at_play=[7.0,…]` (`play()` does not apply a pose),
   `kill=[true,false]→[false,false]` vs `node_free` lazy invalidation,
   `unpaused_moved=true` non-vacuity control.

## run_battery.py changes (insertion-only, +111 lines)

1. **CASES 265 → 288 tuples** (result rows 272 → **295** incl. 7 meta):
   23 `r93_*` rows inserted after `r92_tilemap_nullts_crash`, ahead of the
   crash/descendant tail — `descendant_pipe_detached_control`'s sleep-8 gap
   stays adjacent to the meta probes. `git diff` shows **111 insertions,
   0 deletions**; the inserted block was generated from the scout's
   `author-rows.py.txt` + boundary receipts and diff-verified
   byte-identical to the generator output.
2. **`expected_errors` += 0 cases** — all 23 rows are `ERROR:`-clean with
   0 B stderr in every committed receipt (54/54 scout canonical, 24/24
   loadtest, 274/274 boundary) and in 51/51 fresh reps here.
3. **`required_stderr` += 0 cases** — no crash-class row this round.
4. **Floor gate extended**: `r93_expected_errors_all_matched` covering
   `case.startswith("r93_")` — same named-by-round /
   covers-round-prefixes shape as r87–r92; inert today (no entries) but a
   future r93 allowlist entry cannot die silently. Verified `True` in both
   green runs.

## New-cell inventory (23 rows)

| case | arm | pin shape |
|---|---|---|
| `r93_tween_census` | anim_lattice `census` | full line — class/enum/default census, signal lists, method counts, cache/capture surface |
| `r93_tween_interp_value` | `tweenval` | full line — r91 receipt + expo-quirk endpoints + clamps + int/vec/color + formula residuals |
| `r93_tween_interp_grid_a` | `tweenval_grid` | `lin/sin/qui/qua/qad` ×4 eases ×5 t |
| `r93_tween_interp_grid_b` | `tweenval_grid` | `expo/ela/cub/cir/bou/bac/spr` ×4 eases ×5 t — **encodes pure-function overshoot** (`bac io` −0.997, `spr out` 10.51) |
| `r93_anim_track_interp` | `animtrack` | full line — NEAREST/LINEAR/CUBIC two- and three-key, default LINEAR, bezier handles |
| `r93_tween_manual_step` | `tweenstep` | full line — `custom_step` exactness, synchronous completion signals, paused stepper, loops |
| `r93_tween_chain` | `tweenchain` | full line — sequential/parallel/interval/callback ordering, lazy owner-free invalidation, `kill()` immediate |
| `r93_tween_process_stable` | `tweenproc` | `stable=[…]` clause (the mode cell's only pinnable tokens) |
| `r93_tween_phys_manual_step` | `tweenproc` | `phys_manual=[before=1.0,after_step025=2.0]` — manual step on a paused physics-mode tween |
| `r93_anim_seek` | `animseek` | full line — play/advance/seek/pause/stop/speed/replay/loop/manual-frames |
| `r93_anim_method_callback` | `animmethod` | full line — DEFERRED vs IMMEDIATE, disabled track, started/current signals |
| `r93_anim_blend_finished` | `animblend` | `finished_010/005/020` — w_i law at three step granularities |
| `r93_anim_blend_running` | `animblend` | running-source crossfade, hard switch, default blend, `play_with_capture` |
| `r93_anim_process_manual` | `animproc` | `manual=[…] frozen=[…] inactive=[…]` clause |
| `r93_anim_process_stable` | `animproc` | `stable=[…]` septet clause |
| `r93_anim_overshoot` | r93b `purity` | full line — **runtime overshoot** BACK/SPRING/ELASTIC, extreme/negative deltas, accum1000 |
| `r93_anim_manual_clock_interleaved` | r93b `manual_inv` | paused-tween + MANUAL-player step lattice across awaited frames |
| `r93_anim_manual_clock_control` | r93b `manual_inv` | `inv`/`step_exact` invariants + `unpaused_moved=true` non-vacuity control |
| `r93_anim_deferred_flush` | r93b `deferred` | DEFERRED→process frame **and** physics frame; two-advance queue; IMMEDIATE inside advance |
| `r93_anim_await_offbyone` | r93b `frame` | `idle=[x1=0.0` — N awaits ⇒ N−1 applied steps (258/258 boundary runs) |
| `r93_anim_physics_tick` | r93b `frame` | `mixer_applied_10=10` + physics-side tick lattice (launch-invariant) |
| `r93_anim_phys_delta` | r93b `frame` | `phys_delta=0.01666666666667` — the 60-tps tick is not a mode |
| `r93_anim_blend_interleaved` | r93b `blend` | weight law + `interleaved_eq_plain=true` + `hard_after_frame=500.0` |

## Fresh-arm evidence (pre-battery)

All 17 arms (11 `anim_lattice` + 6 `r93b_anim`) ×3 fresh reps in the
battery's exact launch shape (`godot --headless --path <scratch-copy-of-
fixtures> --script res://<script> -- --arm=<a>` via `subprocess.run`, no
shell wrapper): `corpus/live/r93-author/fresh-reps/` — 51 receipts
(`out`/`err`/`rc`), all rc=0, all 0 B stderr.

- **All 23 rows classify PASS ×3 through the production
  `classify_process`** (AST-extracted from the edited battery, segment
  sha256 `749fa0607e7707e6` — the same segment r89–r92 pinned); every
  signature additionally verified on the **stdout** stream.
- Rep-level byte-stability: every full-line-pinned arm is `uniq=1`
  (census, tweenval, tweenval_grid, animtrack, tweenstep, tweenchain,
  animseek, animmethod, animblend, purity). The clause-pinned arms are the
  documented modes (tweenproc, animproc, manual_inv, deferred, frame,
  blend, clock) — their pinned substrings were byte-verified against every
  committed boundary receipt (16/16 each) before insertion.
- The six `r93b` arms' signatures were also re-checked against the
  boundary's own 258-run corpus: purity full-line 16/16; manual_inv
  prefix + clause 16/16; deferred block 16/16; frame `x1=0.0`,
  `mixer_applied_10=10 phys=[…]`, `phys_delta=` 16/16; blend prefix 16/16.

## Labrat advisory (agent `06a966cd`, read-only, no edits)

One bounded hypothesis dispatched (frozen-`probeParent` allowance): *every
authored signature appears verbatim in every committed receipt of its arm
across the r93-scout + r93-boundary corpora, and none collides with a
different arm's PASS line* — **Clause 1 CONFIRMED in full** (336 receipt
files checked; every signature hit exactly its own arm's receipts, incl.
the 2720-char census line in 17/17). **Clause 2 REFUTED as literally
stated** with two cross-arm substring hits — both benign in this battery
because each row's signature is only ever evaluated against that row's own
`--arm=` launch:

- `phys_delta=0.01666666666667` (`r93_anim_phys_delta`, `--arm=frame`) also
  appears in all 16 `clock`-arm receipts — but `clock` is not a CASES row,
  so the substring can only ever be observed inside a `frame` run, where
  it still binds exactly the 60-tps tick it pins. If a future fixture
  bumps `physics_ticks_per_second`, the `frame` arm emits
  `phys_delta=0.0083…` and the row fails as designed.
- `finished_010=[100.0,…,500.0]` (inside `r93_anim_blend_interleaved`,
  `--arm=blend`) is verbatim inside the `animblend` arm's line — the same
  measured crossfade lattice on two probes (a shared law, not corruption);
  an `--arm=blend` run of `r93b_anim.gd` can only emit the r93b line.

No signature is forgeable by its own arm's fallback path (`_:` prints
`unknown arm=`, matching none of the pins — the r88 dead-seat shape cannot
recur). `idle=[x1=0.0` and `mixer_applied_10=10` confirmed zero cross-arm
hits.

## Full battery — final bytes

| run | rows | verdict |
|---|---|---|
| `runs1/20261016T003655768134Z` | 295 | **PASS** — 295/295, `r93_expected_errors_all_matched=true`, r93 23/23 |
| `runs3/20261016T004609760557Z` | 295 | **PASS** — 295/295, `r93_expected_errors_all_matched=true`, r93 23/23 |

**Two green runs (295/295) on the final bytes.** Interim run
`runs2/20261016T004127802572Z` failed only on the **documented volatile
classes**: `crash_spontaneous_sigabrt` timed out at the 8 s bound — the
SIGABRT/signal-4 crash dump was still being written under foreign
oversubscription (loadavg 51–54, 48 foreign `yes` hogs — none mine); its
signature and `handle_crash: Program crashed with signal 4` were already
on the streams, so the flake is the dump-vs-timeout race, not a verdict
change. The two knock-ons (`probe_spontaneous_crash_classification`,
`probe_error_clause_surface` → `prior_meta_rows_stable_29_discriminations`)
are the same flake consequence pattern r92 recorded for
`negative_transition`. **No r93 row flaked in any of the 3 runs (23/23
PASS ×3).**

## Host notes / remaining risks

- Host ran under heavy foreign oversubscription throughout (loadavg ~50+,
  48 `yes` hogs — none mine). All 23 signatures are byte-stability-verified
  state/pure-function/manual-clock reads plus clause pins on the two mode
  cells; nothing frame-counted is pinned.
- Enum orders, signal lists, `an_m_count`/`ap_m_count`/`tw_m_count` method
  counts, and float-precision literals are **build-version tokens** — they
  flip loudly on an engine bump (intended, same class as existing census
  pins).
- `r93_anim_await_offbyone` pins `x1=0.0` — a prefix substring ending
  before `,x2=`; it binds the N−1 law's first-await instance. The general
  law (`pos10 = (N−1)·delta`) is a mode at the default ~160 fps rate and is
  deliberately unpinned; the comment records the scope.
- `r93_anim_phys_delta` (`phys_delta=0.01666666666667`) binds the 60-tps
  physics tick on the `frame` arm; under a non-60-tps project.godot this
  row would correctly fail — the pin is project-conditioned by design.
- `r93b_anim.gd`'s `clock` arm is a pure launch fingerprint (16/16 unique)
  — intentionally **not** authored.
- Deliberately un-authored: mid-blend values outside their step
  granularity, `tweenproc.phys`/`auto`/`paused` counters, `quick` frame
  counts, `idle_lag`, `caches_total`, `mixer_applied` totals, the
  `--fixed-fps` boot transient (a measured-but-mode boot artifact),
  `mixer_updated` (0 fires — dead for script observation on this build).
- No commit. Worktree: `M corpus/fixtures/run_battery.py` (+111,
  insertion-only), `?? corpus/fixtures/anim_lattice.gd`,
  `?? corpus/fixtures/r93b_anim.gd`, `?? corpus/live/r93-author/`, this
  report.

## Evidence index

`corpus/live/r93-author/` — `manifest.sha256` (1087 entries) covers all:

| artefact | path |
|---|---|
| fresh-arm receipts (17 arms × 3 reps, out/err/rc) | `fresh-reps/` |
| launch project (fixtures copy incl. both probes) | `proj/` |
| battery runs (1 green, 1 flake, 1 green) | `runs{1,3}/<stamp>/verdicts.json`, `runs2/…/verdicts.json`, `battery{1..3}.log` |
| source reports | `reports/round-93/r93-scout.md`, `reports/round-93/r93-boundary.md` |
