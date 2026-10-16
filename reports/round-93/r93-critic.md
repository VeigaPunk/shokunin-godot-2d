# r93 critic — adversarial review of committed `4b75151` (23 `r93_*` anim/tween rows, 295-row battery)

Seat `CRITIC` (g2d lane r93) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7.
Reviewed commit **`4b75151`** (`r93 author: 23 anim/tween rows (295 total)`, parent
`d9edb72`). `HEAD == 4b75151` at session start **and** at report time — no sibling
commit moved the g2d lane during this session (sibling *reports* landed as untracked
files; see §3 cross-seat).
**No tracked write, no commit.** Seat-owned artifacts: `corpus/live/r93-critic/**`
+ this report.

**Committed tree only.** Every harness-derived check below is pinned to a **frozen copy
of the committed tree** extracted with `git archive 4b75151 -- corpus/fixtures`
(`frozen/corpus/fixtures/`), whose four load-bearing files hash
`run_battery.py` = `a79bfdd6f3f468d7cf904608a053b22bb4f3d6423d199e4e81bfa1605506df83`,
`anim_lattice.gd` = `6a919ae04d4e754953b9f8067c49b74c46cf5f3bdc1dce76d4e29597faa2cd4a` (689 L),
`r93b_anim.gd` = `3c8dd8f10d6888e120c2420a3dcfc8c0867372ad0907d99d88b1eb98f1efd966` (466 L),
`project.godot` = `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` —
all four byte-equal to `git show 4b75151:<path>` and (at extraction time) to the
worktree. The worktree stayed clean for `corpus/fixtures` and `reports/round-93`
throughout; this seat wrote nothing outside `corpus/live/r93-critic/**` and this report.

**`lsp` disclosure.** No `lsp` device and no GDScript language server on this host (same
as every prior r89–r93 seat). The change under review is two new fixture files plus an
insertion-only harness block; no symbol-aware rename was required, so hand analysis +
fresh-process execution is the fallback in use.

**probeParent disclosure.** Exactly **one** read-only `ufo-labrat` (agent `212d132c`,
depth-2, licence exhausted) was dispatched with one bounded hypothesis (see §5). Its
substrate exposes **no exec** (`read`/`grep`/glob only), so it returned a **static trace
only** — zero artifacts, zero mutations, zero descendants, repository untouched.
It answered **Clause 1 CONFIRMED / Clause 2 CONFIRMED with one flagged boundary row**,
and this seat then *measured* the flagged row (`r93_anim_phys_delta` flips on a
physics-rate mutant, §1 F2) rather than accepting the static judgement.

**Load regime.** Host carried foreign `loadavg 75–90` for the battery, fresh, load and
mutant batches (session-start `86.3`; rep1 ran at `86.3`, the fresh/load batch at
`75.6–80.4`; `55` at report time) with **48 foreign `yes` hogs** (ppid 1537) plus
concurrent sibling batteries observed in `ps`: four g3d-lane (`r96-critic`, `r96-scribe`,
`r96-verifier`, `r96-reviewer`) and, later, the g2d `r93-reviewer` / `r93-scribe` /
`r93-verifier` lanes. This seat added **16 named hogs for exactly one batch** (killed at
end; `ps` shows **0** orphaned `yes` with ppid 1; no stray Godot left; `ulimit -c 0`
throughout). Loadavg is recorded per batch in `load.log`, `battery-rep{1,2}.log`,
`fresh_load.log`.

---

## 0. What I ran — 161 archived seat Godot launches (+46 timing launches) + 2 full 295-row batteries + 2 trimmed-harness runs

| # | probe | receipts |
|---|---|---|
| 1 | all 23 rows ×1 timed, battery launch shape (2 passes) | `timing.json` |
| 2 | 16 r93 arms ×3 fresh (48 launches) | `runs/freshrep/`, `author_compare.json` |
| 3 | 16 r93 arms ×2 with **+16 seat hogs** (32 launches) | `runs/load/`, `fresh_load.json` |
| 4 | 16 r93 arms ×3 + ×2, in-memory stability | `runs/fresh/`, `runs/load/` |
| 5 | seat probe `preplay` (N−1 law + pre-play wording) | `runs/probe/` |
| 6 | seat probe `physflush` (battery shape) + `physflush2` (600 tps, decisive) | `runs/probe/` |
| 7 | seat probe `overshoot` (runtime vs static curve) | `runs/probe/` |
| 8 | committed fixture at `--fixed-fps 60` / `120` (N−1 exactness) | `runs/ff60_frame.out`, `runs/ff120_frame.out` |
| 9 | **26 fixture/project mutants**, each in its own scratch project | `mutants/<name>/`, `mutants{,2}.json` |
| 10 | **harness mutant** (trimmed CASES, synthetic dead r93 entry) ×2 | `harness-mut/`, `harness-mut.json` |
| 11 | full battery, frozen committed tree, rep1 (loadavg 80→90) | `battery-runs/rep1/20261016T010010124152Z/` |
| 12 | full battery, frozen committed tree, rep2 | `battery-runs/rep2/20261016T010516365457Z/` |
| 13 | independent signature census over 387 sibling receipts | `signature_census.json` |
| 14 | custody manifests of the sibling seats (read-only) | §2.10 |

Plus seat scripts (`scripts/{mutants,harness_mut,fresh_load,freshrep,signature_census}.py`)
and one engine instrument (`probes/r93c_probe.gd`, run in seat scratch projects only).
Production classifier segment `classify_process` sha256
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` (1068 chars, AST
`ast.get_source_segment`) — **the same byte segment r89–r92 pinned**, re-extracted from
the r93 harness (this closes the r92 critic's open reconciliation item: the committed
r93 harness still yields `749fa060…`, not the scribe's `13473e6d…`).

---

## 1. Findings (ranked)

### F1 — LOW-MEDIUM · the encoded "pre-play value" mechanism is **false**; the first awaited frame applies the animation's *t=0 pose*

The r93 comment block in `run_battery.py` states: *"`await N process_frame => N-1 applied
steps` … pinned as `idle=[x1=0.0` (**the first awaited frame still reads the pre-play
value**)"*. The boundary report §9 states the same mechanism. The **count** is right; the
**mechanism sentence is wrong**, and the committed fixture cannot tell the two apart
because its pre-play value (0.0) equals its track's `t=0` key (0.0).

Seat probe `preplay` (`probes/r93c_probe.gd`, own scratch project) makes the two readings
diverge by setting a **non-zero pre-play value** before `play()`:

```
PASS r93c_probe preplay at_play=5.0 after_play=5.0
  xs=[0.0,0.3436666727066,0.34476667642593,0.9003221988678,1.66666674613953,2.22222232818604]
  pos=[0.0,0.00343666666667,0.00344766666667,0.00900322222222,0.01666666666667,0.02222222222222]
  proc_frames=[1,2,3,4,5,6]  n1_x1_is_preplay=false  n1_x1_is_t0=true
```

(`runs/probe/preplay.out`; the per-frame deltas vary with host rate — the three seat reps
print different `xs[1..5]` — while `at_play=5.0`, `x1=0.0`, `n1_x1_is_preplay=false`,
`n1_x1_is_t0=true` are identical in **3/3** reps, `runs/probe/preplay.rep{2,3}.out`.)

- `play()` does not apply a pose (`after_play=5.0`) ✓ — but the **first awaited frame
  reads `0.0`, not the pre-play `5.0`**: the first process frame *does* apply the
  animation, at `t=0`. The N−1 law is therefore "N awaits ⇒ N−1 **advances**", with the
  first apply being the `t=0` pose — not "the first frame reads the pre-play value".
- The sibling corpus already contains the fact that makes this reading the only
  consistent one: the scout's **F8** established that the player writes the animation's
  `t=0` value rather than restoring the pre-play value (`stop()` → 7.0 → 50.0 → 0.0).
  The same `t=0` write is what the first awaited frame performs; the boundary's
  "pre-play" wording survives only because the committed fixture's pre-play value *is*
  the `t=0` key (both 0.0).
- The counting law itself is **confirmed exactly** on the *committed* fixture at fixed
  rates: `--fixed-fps 60` → `x2=1.66666674613953 (1δ), x3=3.333 (2δ), x5=6.667 (4δ),
  x10=15.0000009536743 (9δ), pos10=0.15 (9δ)`; `--fixed-fps 120` → `x2=0.8333 (1δ) …
  x10=7.5 (9δ), pos10=0.075 (9δ)`. Receipts `runs/ff60_frame.out`, `runs/ff120_frame.out`.

Impact is comment-level, but it is a **committed artifact** other seats read: a future
author who pins "pre-play" semantics for a node whose pre-play value differs from the
track's `t=0` key will write a row that fails for the wrong reason. Fix is one sentence.

### F2 — LOW · three rows pin a **single token** with no co-pinned sibling; the await row's token is also produced by a fully dead path

Both the labrat's clause-2 flag and this seat's mutant evidence point at the same shape.

- **Mutant `frame_idle_to_manual`** (IDLE player switched to `MANUAL`, so the IDLE pose
  path never advances) → `r93_anim_await_offbyone` **PASSes** on bytes that read
  `idle=[x1=0.0,x2=0.0,x3=0.0,x5=0.0,x10=0.0] idle_per_frame=0.0 pos10=0.0
  mixer_applied_10=0` (0 B stderr, rc=0; receipt
  `mutants/frame_idle_to_manual/r93_anim_await_offbyone/`). The pinned token is a
  **zero**, and a zero is what a dead path prints. The *sibling* row
  `r93_anim_physics_tick` (`mixer_applied_10=10 …`) **FAILs** on the very same bytes —
  so the arm is non-vacuous, the row is not.
- The row is nevertheless **not vacuous w.r.t. its claim**: mutant `await_extra_step`
  (`player.advance(0.1)` inserted before the IDLE loop) flips it to **FAIL** while
  `r93_anim_physics_tick` / `r93_anim_phys_delta` stay PASS — i.e. the pin does bind the
  "zero advances after one await" instance.
- Labrat flag, measured here: `r93_anim_phys_delta` also pins one token
  (`phys_delta=0.01666666666667`); the project mutant `project_phys_120`
  (`[physics] common/physics_ticks_per_second=120` in `project.godot`) flips it **FAIL**
  (and `r93_anim_physics_tick` with it), so its "project-conditioned by design" claim is
  measured, not assumed.

Cheap follow-up if the operator wants row-level self-containment: add a non-zero
pre-play token (or a `pos10` identity token at a fixed rate) to the await row.

### F3 — LOW · the "physics frame flushes the DEFERRED queue" route is **not discriminated** by the shipped `manual_def_phys` lattice — but it is **true**

The encoded comment says the boundary found a **new route**: *"DEFERRED method-track
callbacks flush on the next process frame **AND on a physics frame**"*, carried by
`manual_def_phys=[after_adv=[],after_phys=[7,8]]`.

- In the **battery launch shape** that lattice cannot separate the two routes: seat probe
  `physflush` shows the `await physics_frame` arm crosses **5 process frames**
  (`proc_frames_elapsed=5`, `phys_frames_elapsed=1`), so `after_phys=[7,8]` is equally
  explained by the next-process-frame flush. Receipt `runs/probe/physflush.*`.
- The route is nevertheless **real**, and this seat's decisive probe establishes it:
  raising `Engine.physics_ticks_per_second` to **600** (≥2 physics steps per main-loop
  iteration, `max_physics_steps_per_frame=8`) lets the coroutine resume at the *next
  physics step of the same iteration* — **zero** process frames elapsed — and the queue
  is already visible:
  `after_adv=[] after_phys=[7,8] proc_frames_elapsed=[0,0,0] phys_frames_elapsed=[1,2,3]
  no_process_frame_between=true` (`runs/probe/physflush2.*`).

So the boundary's claim survives scrutiny; what does **not** survive is the claim's
*evidence inside the shipped fixture*. Recommend recording the confound in the comment
(or adding the ≥2-steps-per-iteration control), so the next reader does not re-derive it.

### F4 — INFO · the r93 floor gate is **wired but vacuous** today (0 entries), and provably live when an entry exists

`r93_expected_errors_all_matched` is `all(not e["dead_in_run"] for r in census_rows if
r["case"].startswith("r93_") for e in r["entries"])` — with **zero** r93 allowlist
entries (`census r93 rows: []`; the committed `expected_errors` dict has no `r93_` key)
this is `all()` over an empty generator ⇒ `True`. Verified in both batteries.

Its liveness is proven by a **harness mutant** (the r92 `noorphan` analogue, but
harness-side because this round adds no allowlist mechanism to remove): a trimmed-CASES
copy of the committed harness with one synthetic r93 entry that can never match.

| variant | `r93_expected_errors_all_matched` | census row | `probe_error_clause_surface` |
|---|---|---|---|
| `base` (no r93 entries) | **True** (vacuous) | — | PASS |
| `dead` (1 dead `r93_tween_census` entry) | **False** | `matched_lines=0, dead_in_run=true, any_matched=false` | **FAIL** |

(`harness-mut.json`, `harness-mut/base.log`, `harness-mut/dead.log`.) So the gate is
live and r93-scoped; it simply protects nothing yet. That is exactly what the author
discloses ("inert today … so a future r93 allowlist entry cannot die silently").

### F5 — INFO · boolean-clause rows are probe-computed predicates (not the r91-F3 class), and they do flip on mechanism removal

`r93_tween_process_stable` and `r93_anim_process_stable` pin only `stable=[…]`
booleans, and `r93_anim_manual_clock_control` pins `inv=[…] step_exact=[…]
unpaused_moved=true`. The labrat traced each operand: every one is printed on the same
stdout line (`auto=`, `paused=`, `phys=`, `phys_manual=`, `manual=`, `frozen=`,
`inactive=`, `paused=`/`manual=`/`unpaused=`), so a reviewer can cross-check the
predicate against printed values — **class (b), not the r91-F3 class (c)**; it found
**zero** class-(c) tokens across the 23 rows. This seat confirmed the predicates are not
decorative: mutants `tweenproc_pause_removed` and `animproc_manual_advance` flip them to
FAIL (with pristine controls PASS) while the raw operands move with them.

### F6 — INFO (lane note) · rep1's two failures are pre-existing volatile classes; the r93 block adds **no** per-case-bound risk

- rep1 reddened on `overlap` (CASES[4], `exit=1`, `ERROR: overlap probe: signal occurred
  before physics overlap observation`) and `audio_playback` (CASES[37], `exit=2`,
  `position_before == position_after`). Both are **documented flake classes** in earlier
  seat logs (`r92-author/battery3.log`, `r92-reviewer/ctlA.log` + `ctlB.log`,
  `r92-scribe/battery-rep2b.log`, and the r90 author's 8-rep flake table). rep2 was
  **fully green 295/295**.
- The r93 block is CASES[261..283], i.e. **after** both failures; it passed 23/23 in both
  runs. No r93 row flaked in any of the 5 regimes run here (2 batteries ×295, 3 fresh,
  2 load).
- Timing (23 timed launches, loadavg ≈80; `timing.json`, two passes agreeing within
  0.02 s): wall **0.476–0.875 s**, mean **0.632 s** — the slowest r93 row uses **11 %**
  of the harness's 8 s per-case bound (`execute()`,
  `timeout_seconds = 60 if script.startswith("__godot_export") else 8`). The r92 F1
  (crash-row wall-time straddling the bound) has **no r93 analogue**; the block adds
  ≈15 s of battery wall time.

---

## 2. What survived (positive verifications)

1. **Commit hygiene.** `4b75151`: **239 files, +21230 / −0** (zero deletions anywhere);
   `run_battery.py` **+111/−0**; `project.godot` untouched (the two `project.godot` paths
   in the commit are `corpus/live/r93-author/proj/**`, i.e. seat receipts). CASES
   **265 → 288**; the 265 pre-existing tuples are byte-identical **in order** after
   removing the 23 r93 rows; the r93 block is contiguous at **CASES[261..283]**,
   immediately after `r92_tilemap_nullts_crash` and ahead of the unchanged
   crash/descendant tail `[284] crash_spontaneous_sigabrt`, `[285] crash_self_sigkill`,
   `[286] descendant_pipe_detached_control`,
   `[287] descendant_pipe_forged_signature_release` — the descendant `sleep 8` gap stays
   adjacent to the meta probes. 288 + 7 meta = 295.
2. **Fixture provenance.** Both committed fixtures are **byte-copies** of the frozen
   sibling probes: `anim_lattice.gd` == `corpus/live/r93-scout/probes/anim_lattice.gd`,
   `r93b_anim.gd` == `corpus/live/r93-boundary/probes/r93b_anim.gd` (sha256 equal on all
   four copies), and both hashes are the ones documented in the harness comment. No
   fixture folds — every boundary fold is row-side, as claimed.
3. **Fresh reproduction.** rep2 = **295/295 PASS**, `r93_expected_errors_all_matched=True`,
   **0 false discriminations**; rep1 = 293/295 with the two F6 classes, same gate value
   and 0 false discriminations. r93 **23/23 PASS in both**. The two author batteries
   re-read: 295 rows, r93 23/23, gate True.
4. **Signature presence across the sibling corpora (independent re-derivation).** All
   **23/23** signatures appear verbatim in **every** committed receipt of their own arm —
   387 receipts scanned (scout 54 canonical + 24 loadtest, boundary 258, author 51), with
   19–28 own-arm receipts per row and **0** misses (`signature_census.json`). This is
   strictly stronger than the author's "14–16/16" claim for the 9 byte-stable cells.
5. **Byte-stability.** 48 seat fresh reps (16 arms ×3): **10/16 arms `uniq_out=1`**; the 6
   multi-valued arms are exactly the **documented mode cells** (`animproc` 3,
   `tweenproc` 2–3, `blend` 2, `deferred` 3, `frame` 3, `manual_inv` 2–3). Against the
   committed author fresh-reps: **32/48 byte-equal, 16/48 differing, and every differing
   token is frame-rate-coupled** (`proc_delta`, `idle=x2…x10`, `pos10`,
   `idle_per_frame`, `mixer_applied`, `unpaused[o]`, `idle_lag`). **No pinned token
   differs**; all 23 rows PASS on all 48.
6. **Load invariance.** 16/16 arms (all 23 rows) PASS with **+16 named seat hogs**,
   2 reps each, `loadavg 80→90`; **0 B stderr** and rc=0 in every one of the 48 fresh +
   32 load receipts; 0 orphaned hogs (0 `yes` with ppid 1 after the batch).
7. **Encoded law 1 — runtime overshoot (not clamp).** Direction: `BACK/EASE_IN_OUT`
   t=0.25 → **0.10286344587803 < start 1.0**; `SPRING/EASE_OUT` t=0.5 →
   **10.510157585144 > end 10.0** (t=1.0 → exactly 10.0); `ELASTIC/EASE_OUT` t=0.25 →
   9.11611652374268 < end. Curve identity: the runtime fraction equals the **static**
   `Tween.interpolate_value` fraction from the *independently pinned* grid row —
   `−0.099681839346886` vs `−0.099681839346886` (rel 4.5e-15), SPRING rel 2.3e-8,
   ELASTIC rel 2.6e-8 (float32). The static grid extrapolates on **both** sides
   (`bac io` t=0.25 → −0.9968 below start; t=0.75 → 10.9968 above end). Seat probe
   `overshoot` reproduces all three runtime values byte-for-byte (`runs/probe/overshoot.*`,
   `law_check2.json`).
8. **Encoded law 2 — N−1 await law.** Exact at `--fixed-fps 60` and `120` on the
   committed fixture (§1 F1 receipts). The pinned token is stable in every seat receipt
   of the `frame` arm (7/7 archived `runs/freshrep/`, `runs/fresh/`, `runs/load/`,
   `runs/ff*_frame.out`; 0 misses) and in both batteries, and it appears in all 19
   committed sibling receipts of that arm (§2.4). The first-await instance binds the
   *t=0 pose*, not the pre-play value (F1).
9. **Encoded law 3 — crossfade `w_i=(i−1)/(N−1)` at 3 granularities.** Recomputed from
   the pinned literals alone: `finished_010` (N=10) max |err| **5.9e-8**, `finished_005`
   (N=20) **8.4e-8**, `finished_020` (N=5) **0.0**, with `w[0]=0` and `w[-1]=1` in all
   three (`law_check.json`). The **running-source** crossfade reproduces the same law
   with a source that keeps advancing: predicting the pinned `running_from_50` sequence
   as `a_i + (500−a_i)·(i−1)/9` with `a_i = 100·min(0.5+0.1i, 1)` matches to
   **2.4e-5** (float32 accumulation) — i.e. the pinned values encode "source advances,
   weight law holds" rather than a fitted curve. `interleaved_eq_plain=true` and
   `hard_after_frame=500.0` are pinned in the r93b blend row, and both flip under
   mutants (`blend_time_2`, `hard_switch_blend`, `animblend_time_2`,
   `animblend_steps_9`).
10. **Encoded law 4 — DEFERRED/IMMEDIATE split.** `after_adv=[]`, `next_proc=[7,8]`,
    `second_proc=[7,8]`, `two_adv=[after=[],flush=[7,8]]`, `immediate=[after_adv=[7,8],
    after_frame=[7,8]]` all reproduce; the physics route is true (F3) and the
    IMMEDIATE/DEFERRED distinction is measured (mutant `deferred_immediate_b` → FAIL;
    `deferred_no_queue` → FAIL).
11. **Pins are discriminating (rows not vacuous).** 26 mutants total, covering **22 of
    the 23 rows** (all but `r93_anim_blend_running`, which shares its arm and its
    `finished_010`/`finished_020`/`hard_after_frame` tokens with the three
    `r93_anim_blend_interleaved` mutants). **23 of 26 behaved exactly as predicted**
    (mutant FAIL, pristine control PASS); the 3 exceptions are all **mutant-design errors
    of this seat**, not row defects, and each was re-run correctly:
    `tweenproc_paused_advance` (the predicate stayed true because the mutant shifted the
    baseline → replaced by `tweenproc_pause_removed`, which flips), `census_autocapture`
    (replacing `is_auto_capture()` with `true` produced identical bytes because the
    engine value *is* true → the `…_false` variant flips the row), `frame_idle_stopped`
    (failed on an unrelated `ERROR:` line, not on the signature → `frame_idle_to_manual`
    is the clean absorb receipt of F2). The only row that PASSes on perturbed mechanism
    bytes is the F2 zero-token case, plus the author's **declared** mode cells.
12. **No pairwise signature containment** within any shared arm (checked all same-arm
    row pairs) — no row silently absorbs another row's evidence.
13. **Custody cross-check (read-only).** `corpus/live/r93-author/manifest.sha256` verifies
    **1086/1086**; `corpus/live/r93-boundary/manifest.sha256` verifies **1049/1049**.
    The author's comment counts also check out against the corpora: scout
    **54 canonical + 24 loadtest** `.out` receipts, boundary **258** canonical and
    **16** purity receipts — exactly the numbers the r93 harness comment cites.

---

## 3. Questions the dispatch implies, answered

**False-positive shapes (a row that passes when it shouldn't).** One, at row level:
`r93_anim_await_offbyone` on a dead IDLE path (F2), with the arm still protected by a
sibling row. Every other pinned measurement tested flips loudly when perturbed — including
the project-conditioned `phys_delta`, both grid rows, the census line, the manual clock,
the blend weights (3 mutants), the DEFERRED queue, and the physics-side lattice (2
mutants). No *block-level* false-positive shape was found.

**Scheduler-conditional pins the boundary missed.** None new. The two `stable=[…]` mode
cells, the frame arm's `idle=`/`pos10`/`proc_delta`, `idle_lag`, `tween5` and the
unpaused control are modes and are **not** pinned; every pinned clause held in 5 regimes
here (2 batteries, 3 fresh, 2 load) and in the sibling corpora (19–28 receipts per row).
`--fixed-fps` behaves as the boundary described: a **stabilizer** for the mode cells
(ff60/ff120 receipts are single-valued) and a **verifier** for the N−1 law (exact
multiples of δ). `phys_delta=0.01666666666667` is project-conditioned by design and
flips on a 120-tps project mutant.

**Rows that pass only because a sibling process is alive.** None. All r93 state is
in-process; no fixture touches files, spawns descendants, or takes locks (0 B stderr,
rc=0 in every receipt).

**Allowlist / census correctness.** The r93 block carries **0** entries in both
`expected_errors` and `required_stderr`; the census therefore contains **no** r93 row
(verified in both batteries), 68 entries total and **0 dead entries** across the
battery. `r93_expected_errors_all_matched` is vacuous today and live when an entry
exists (F4).

**Insertion ordering / prior-row identity.** Verified (§2.1): insertion-only, ordering
preserved, tail untouched.

**Cross-seat consistency.** Sibling r93 seats landed *reports* (untracked) during this
session; the g2d `HEAD` did not move. This seat's measurements do not contradict the
author's disclosed items: the author's labrat's two cross-arm collisions are **exactly**
the ones this seat's independent 387-receipt census found (`phys_delta` inside the
non-CASES `clock` arm; `finished_010`/`finished_020` shared between the two blend arms —
different scripts, so never cross-evaluated). The author's "no clamp / overshoot" claim
is confirmed and strengthened (static-vs-runtime curve identity, §2.7). The one place
this report sharpens the record is F1 (the pre-play wording) and F3 (the physics-route
evidence), neither of which any sibling report claims to have discriminated.

---

## 4. Verdict

**PASS-WITH-RESERVATIONS on the committed bytes `4b75151`.** No blocking defect.

The five encoded folds are landed and measured: (1) **runtime overshoot, not clamp** —
BACK below start, SPRING above end, ELASTIC below end, with the runtime curve proven
identical to the static pure function (rel ≤ 2.6e-8) and the static grid extrapolating on
both sides; (2) the **N−1 await law** — exact at ff60/ff120 on the committed fixture,
with the first-await instance correctly bound to a single stable token; (3) the
**crossfade weight law** `w_i=(i−1)/(N−1)` at three granularities, recomputed from the
pinned literals to ≤8.4e-8, plus await-immunity and hard-switch control; (4) the
**DEFERRED/IMMEDIATE split** with the physics-frame route (true; the shipped lattice is
not the proof — F3); (5) the **floor gate** — wired, r93-scoped, and demonstrably live,
though vacuous today (F4). The commit is insertion-only, both fixtures are byte-copies of
frozen sibling probes, and every signature is present in every committed receipt of its
own arm.

Reservations are evidentiary/robustness, not behavioural:

- **F1** the comment's "pre-play value" mechanism is false (the first awaited frame
  applies the `t=0` pose); one sentence to fix.
- **F2** `r93_anim_await_offbyone` (and, per the labrat, `r93_anim_phys_delta`) pin a
  single token; the await row's zero token is also printed by a dead path, with
  non-vacuity carried by a sibling row.
- **F3** the "physics frame flushes" route is not discriminated by the shipped
  `manual_def_phys` lattice (5 process frames elapse in the battery shape); it is true
  and this seat's 600-tps probe proves it.
- **F4/F5/F6** gate vacuity, boolean-predicate clauses with printed operands, and two
  pre-existing volatile classes reddening rep1 — all disclosed or pre-existing.

**Blockers: none.** The cheap follow-ups worth queueing: F1's one-sentence comment fix,
F3's confound note, and an optional non-zero pre-play token in the await row.

---

## 5. ProbeParent labrat + the pre-registered hypothesis

The single labrat licence was used (agent `212d132c`, depth-2, read-only). Its substrate
exposes **no exec** (`read`/`grep`/glob only) — same capability class as the r92 critic's
labrat — so it returned a **static trace only**: zero files, zero processes, zero
descendants, repository untouched.

Pre-registered hypothesis, two clauses: *(1) every pinned token in the 23 r93 signatures
is engine-returned, or a probe-computed predicate whose operands are printed on the same
line; no "r91-F3 class" token exists. (2) no pinned token can be produced by a dead code
path.*

**Clause 1: CONFIRMED** — it traced all 23 rows to the emitting `print()` in
`anim_lattice.gd` / `r93b_anim.gd` and found **zero** class-(c) tokens; the `stable=`,
`inv=`, `step_exact=`, `unpaused_moved`, `interleaved_eq_plain` predicates all have their
operands on the same line. **Clause 2: CONFIRMED with one flagged boundary row** —
`r93_anim_phys_delta` (and to a lesser degree `r93_anim_await_offbyone`) pin a single
token, so under a literal reading no second pinned token moves if the mechanism is
removed.

This seat re-ran the flagged item against the engine rather than accepting the static
judgement: the project mutant `project_phys_120` flips `r93_anim_phys_delta` to **FAIL**
(and `r93_anim_physics_tick` with it) — the flag is a row-shape observation, not a
vacuity defect. The await-row half of the flag is independently confirmed by mutant
`frame_idle_to_manual` (§1 F2).

---

## 6. Evidence index

`corpus/live/r93-critic/` — `manifest.sha256` covers every artefact under the lane.

| artefact | path |
|---|---|
| this report | `reports/round-93/r93-critic.md` |
| frozen committed tree (`git archive 4b75151`) | `frozen/corpus/fixtures/` |
| classifier segment pin | `scripts/classifier_pin.json`, `scripts/r93_rows.json` |
| full battery rep1 (295 rows, 2 documented flakes) | `battery-runs/rep1/20261016T010010124152Z/`, `battery-rep1.log` |
| full battery rep2 (**295/295 PASS**) | `battery-runs/rep2/20261016T010516365457Z/`, `battery-rep2.log` |
| fresh receipts (16 arms ×3) + load receipts (+16 hogs) | `runs/freshrep/`, `runs/load/`, `fresh_load.json` |
| byte-comparison vs committed author fresh-reps | `author_compare.json` |
| seat engine probes (preplay / physflush / physflush2 / overshoot) | `probes/r93c_probe.gd`, `runs/probe/` |
| fixed-fps N−1 receipts (ff60 / ff120) | `runs/ff60_frame.out`, `runs/ff120_frame.out` |
| law recomputation (crossfade, overshoot identity) | `law_check.json`, `law_check2.json` |
| fixture/project mutants (26) + results + design-error corrections | `mutants/`, `mutants.json`, `mutants2.json`, `mutants_corrections.json` |
| r93 row wall times vs the 8 s per-case bound | `timing.json` |
| harness mutant (floor-gate liveness) | `harness-mut/`, `harness-mut.json`, `harness-mut/{base,dead}.log` |
| independent signature census (387 receipts) | `signature_census.json`, `scripts/signature_census.py` |
| seat scripts | `scripts/{mutants,harness_mut,fresh_load,freshrep,signature_census}.py` |
| load/regime log | `load.log`, `fresh_load.log` |
