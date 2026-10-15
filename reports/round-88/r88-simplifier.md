# game-dev-2d round 88 — simplifier (r88-simplifier): two proven deletions in `r88_surfaces.gd` (−4 lines, probe-only, zero pinned bytes touched); dead CASES rows, unused keys, and duplicate-boilerplate candidates audited and dispositioned

Seat `SIMPLIFIER` (LEAF) | lane `r88` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.7. Repo
`~/Projects/shokunin/game-dev-2d-shokunin`. Work commit **`3c47eee`** (probe
`r88_surfaces.gd` sha256 `78370a04…`, 422 lines; battery `run_battery.py`
`fde5913b…`; `r88_spawnable.tscn` `89b9ddbe…`). HEAD moved mid-session under
other seats (`f9e8a5b` author report → `6ce55dd` scribe custody → `9697494`
reviewer CHANGES-needed); at report time HEAD is `9697494` and the three r88
tracked files still carry the `3c47eee` bytes. **No tracked file written, no
commit, no git mutation by this seat.** Writes are this report and
`corpus/live/r88-simplifier/**` only. Batteries ran sequentially, never in
parallel (boundary directive 7 / reviewer F4 port rule).

**`lsp` disclosure.** No `lsp` device is exposed in this dispatch — the only
MCP server is `rea` (Ghidra/binary-analysis); no GDScript/Python language
server is installed (`gdscript-lsp`/`gdtoolkit`/`gdls` absent from PATH and
pip). `references`/`definition` queries were therefore **unavailable**; no cold
result is recorded as absence. Deletion-candidate caller proofs rest on
(a) complete textual enumeration of every reader of the suspect state (grep,
**literal fallback, never presented as semantic proof on its own**),
(b) fresh-process receipt equivalence of the folded tree against the unmodified
control and both canonical runs, and (c) an engine-default readback for the
one property-default claim.

---

## 1. Method and proof artefacts

Apply the diff in a scratch copy → full battery both sides → every row's
verdict tuple and normalized output compared against the unmodified control and
the author's two canonical 215-row runs; touched arms additionally repped
directly in the battery's exact launch shape.

| artefact | content |
|---|---|
| `corpus/live/r88-simplifier/r88-simplifier-fold.patch` | unified diff, **−4 lines net / +1 modified token**, all in `corpus/fixtures/r88_surfaces.gd` (422 → 418); `git apply --check` clean against HEAD; sha256 `538a5b2f…` |
| `fixtures-after/` | runnable folded project: full `corpus/fixtures/` copy (`__pycache__` omitted) with `run_battery.py` byte-identical (`fde5913b…`); one differing source file: `r88_surfaces.gd` sha `78370a04…` → **`4661cedb…`**, 418 lines |
| `runs-before/20261015T182943587885Z/` | battery on the **unmodified** tree → **215/215 PASS** (verdicts sha `1d47abd7…`) |
| `runs-after/20261015T183321965855Z/` | battery on `fixtures-after/` → **215/215 PASS** (verdicts sha `8525b706…`) |
| `compare-after.txt` | `corpus/live/r87-baseline/compare.py godot` (r79-baseline tool, reused unmodified) folded vs control vs `r88-author/runs1` vs `runs2` |
| `reps-before/`, `reps-after/` | direct arm reps, battery launch shape, touched arms ×4/side (mp_loopback, light_props, sprite_phys, vis_not); raw `.out` + normalized |
| `rep-analysis.txt` | normalized (uid + traceback-line) per-rep sha table; cross-side per-rep comparison |
| `gravity-default-check/` | fresh-process readback of `RigidBody2D.gravity_scale` default |
| `receipt-audit.txt` | the 8-arm ×4 receipt audit and the four battery runs' row/census/gate extract |
| end-to-end patch check | applied in a temp git repo to the `3c47eee` bytes → output sha `4661cedb…`, byte-equal to `fixtures-after/` |

## 2. Killed — the fold, two deletions (SP1–SP2), both **proven byte-identical**

One patch, `r88_surfaces.gd` only. No pinned signature, no `run_battery.py`
byte, no `.tscn` byte is touched — the fold is invisible to every pinned byte.

| # | site (was) | why dead | proof |
|---|---|---|---|
| SP1 | `MpLimb.uping` `:103–105` (−3) | **zero call sites** — an "unreliable" `@rpc` limb that no arm ever invokes; the arm's only rpc invocations name `"ping"` literally (`:136–138`), and no dynamic dispatch exists (the file's only `call_deferred` is the `_run` bootstrap) | (a) `uping` occurs exactly once in the file — the definition; (b) repo-wide text search finds **no call site anywhere**: every other hit is a definition inside a byte-copy of this same probe (author `proj/`+4 scratch copies, reviewer/verifier/critic copies, scout `r88_probe{,_fix}.gd`, boundary `b88_mp.gd`) or the substring in the word "grouping"; (c) `MpLimb` is a **file-local** class inside a standalone SceneTree script — `project.godot` has no autoloads/globals, so no other script can name it; (d) all 10 loopback receipts on record (scout ×3, author ×4, canonical battery ×2, this seat's control ×1) carry limb logs with **only** ping entries — an `uping` call would log `"u<N>"`; (e) folded vs control: `mp_loopback` tuple and normalized merged output byte-identical (4+4 reps, full battery) |
| SP2 | `_body`'s `gs` parameter `:41` + `b.gravity_scale = gs` `:49` (−1 net) | **unexercised generality**: all 3 call sites (`:270`, `:320`, `:397`) use the default; `gs` is therefore always `1.0`, which is also the engine default — the assignment is a no-op by construction | (a) textual enumeration: the only `_body(` occurrences are the definition and three 2-arg calls; (b) fresh-process readback `RigidBody2D.new().gravity_scale == 1.0000` (`gravity-default-check/`); (c) the three arms that call `_body` — `light_props`, `sprite_phys`, `vis_not` — are byte-identical folded vs control (4+4 reps + battery; `body_y=118.4614`, sprite `y=74.5675`, frozen `vis_not` payload unchanged) |

## 3. Retained behavior — the narrow existing check, both sides

- **Full battery**: control **215/215 PASS**, folded **215/215 PASS**, both
  `verdict=PASS`; `r88_surfaces_*` 8/8 PASS on both sides; census
  `dead_entry_count=0` and `r88_expected_errors_all_matched=true` on both.
- **Folded vs control** (`compare.py godot`): `common=215 new_only=0
  old_only=0` **tuple_mismatches=0** (seeded=0, meta=0); output-normalized
  205 identical / 3 differing / 7 meta not carried. The 3 differing rows are
  exactly the declared-volatile class: `input_lattice_pre_frame` and
  `input_lattice_release_edge` (mode-envelope rows sampling their other
  whitelisted payload) and `r88_surfaces_mp_loopback` line 4 (the raw peer id
  on the declared `R88S` diagnostic line — the reviewer's F5 normalizer gap,
  unchanged by the fold).
- **Folded vs canonical** `r88-author/runs1` and `runs2`: `common=215`, **0
  tuple mismatches** each; output diffs are the same 4–5 declared-volatile rows
  (`press_phys`/`ui_ns`/`pre_frame`/`release_edge` envelope sampling plus the
  `mp_loopback` uid token) — no fold-attributable diff.
- **Direct reps** (battery launch shape, 4/side): every touched arm's
  normalized merged output has **uniq=1 per side and is identical across
  sides**, per rep — `mp_loopback` `31c4e54f0149870a`, `light_props`
  `462aa74c0fb73f6f`, `sprite_phys` `82634054803b0c6b`, `vis_not`
  `2c5d9e6ae141244e`; PASS-line uniq=1/side and cross-side identical.
- **Parse/exec check**: `godot --headless --check-only` rc=0 on both sides.
- **Declared receipt delta**: the only raw-byte difference anywhere is the
  `sprite_phys` stderr backtrace line numbers, `res://r88_surfaces.gd:327` →
  `:323` and `:71` → `:70` (deletions above those lines); the ERROR text
  (whitelisted exact-shape) and the PASS payload are unchanged, and the
  established compare tool normalizes `.<ext>:<N>`. No pinned payload changes
  anywhere.

## 4. Task-item cross-checks

**(a) Dead CASES rows — none.** All 8 `r88_surfaces_*` rows are live: each arm
has 4/4 receipts in `corpus/live/r88-author/arms/` with PASS-payload uniq=1
(stderr empty except `sprite_phys` 260 B ×4), and each row PASSes in both
canonical battery runs, my control run and the folded run (215/215 each). No
arm lacks evidence; no row references an arm that does not exist (8 rows ↔ 8
arms, exact match).

**(b) Unused `expected_errors` / gate keys — none.** The one added allowlist
key (`r88_surfaces_sprite_phys`) is exercised: census `matched_lines=1`,
`dead_in_run=false`, `bare_classification_rejects=true`,
`allowlisted_classification_passes=true` in all four runs; the added
`r88_expected_errors_all_matched` discrimination is `true` in all four runs and
non-vacuous (reviewer V5: `census_covers_all_allowlisted_rows` forces the row
into the census). The r88 rows sit at CASES index 196–203, ahead of the whole
crash/descendant tail — no row lands inside the descendant `sleep 8` gap the
author's comment guards (reviewer V1).

**(c) "Unused ctx keys" — no such mechanism.** `ctx` does not occur in
`run_battery.py` or any fixture (grep, 0 hits); the harness has no context-key
dictionary. The diff's only dict additions are the two live keys above.

**(d) Duplicated boilerplate vs existing probes — rejected, it is the
convention.** 31 of the 36 fixture `.gd` files carry their own
`OS.get_cmdline_user_args()` + `--arm=` dispatch (r88's `_initialize` `:24–28`,
`_fail` `:30–32`, `_finish` `:34–36` are that idiom, ~11 lines total), 7 define
`_finish`, and only `causal_chain.gd` preloads anything. Probes are staged
**alone** into the scratch project and launched standalone, so the duplication
is deliberate self-containment; a shared helper would be a second convention
(used by r88 only, or a 31-file refactor) and would stale 31 probe shas and
their citations. Not a deletion.

## 5. Candidates rejected (evaluated, did not survive the bar)

| # | candidate (was) | verdict | reason |
|---|---|---|---|
| SP3 | `api_s.connected_to_server.connect(…)` `:129` | rejected | Unreachable by contract (server-side `connected_to_server` never emits — confirmed absent from all 9 loopback receipts), **but it is the canary that makes the 5-entry `order=` pin total over the 4 emission types**: if a future engine emitted it, the listener appends and the pin fails loudly; without it the same emission is silent. r87-SP15 precedent (delete changes failure shape). |
| SP4 | `s.texture_changed.connect(…)` `:293` | rejected | Never fires (texture assigned before connect, never changed) — but it is the **negative control** that makes `signals=["fc"]` a claim about `tc` non-emission; without it the pin says nothing about a spurious `tc`. |
| SP5 | `mp_offline` `R88S` print `:85–87` duplicating the pinned `pre` read `:90–92` | rejected | Evidence output (the declared `R88S` diagnostic line), not dead code; deleting changes every future `mp_offline` receipt against the author's captured 4. −3 lines not worth the receipt-shape change. |
| SP6 | `p.stop()` `:380` | rejected | Unobservable on this host, but teardown hygiene and host-robust (a real audio driver can leak a playing stream at exit); convention. |
| SP7 | set-to-default exercises: `poly.closed=true` `:247`, `pl.enabled=true` `:251`, `p.max_distance`/`attenuation` `:363–364`, `listener.position` `:358`, `target.set_process(false)` `:407` | rejected | Each exercises a setter that would fail loudly if the property vanished, or is the negative stimulus the pin reads back; weight ≈ 0 (r87-SP17 precedent). |
| SP8 | `sp_c.add_spawnable_scene(…)` `:175` | rejected | Scout-mandated registered-scene positive control (F6/directive 4–7) — provenance. |
| SP9 | `sync_c.replication_config` construction `:225–226` | rejected | Plausibly load-bearing (client-side property-index mapping for the replicated `:position`); unproven without a run, cost > weight. |
| SP10 | `_vis_pf` / `_vis_events` instrumentation `:386–396` | rejected | Write-only headless, but it is the activation path that would receipt a positive on a screened host; deleting changes failure shape. |
| SP11 | CASES rows / allowlist key / gate deletions | rejected | Nothing dead — §4(a)(b). |

## 6. Flagged, not folded (already owned by other seats)

- **`ray_through_occluder` vacuity** (`:270–281`): the ray is vertical at
  x=−50 while the occluder polygon (`[(0,0),(10,0),(10,10)]` at
  `occ.position=(0,−40)`) spans global x∈[0,10], y∈[−40,−30] — the ray can
  never intersect it, so the boolean is true regardless of physics. This is
  reviewer F2 / boundary directive 5, already receipted by those seats; **the
  fix changes the pinned evidence string and needs a run + CASES edit**, so it
  is outside a byte-preserving fold and this patch does not touch it. My fold
  leaves the row's stable evidence (`occ_is_co=false`, and `body_y` subject to
  reviewer F1) exactly as landed.
- **Reviewer F1 mode pins**: both my runs landed Case B (`74.5675` /
  `118.4614`), so the fold proof is apples-to-apples in this window. A
  side-effect readback of my own (`gravity-default-check/`, fresh project dir)
  landed the light-body shape at `y40=107.9190` — the boundary's Case A value,
  consistent with F1's mode sensitivity. Not fold-relevant; recommend applying
  this patch only bundled with the F1/F2 probe fixes.

## 7. Tradeoff (apply-cost, disclosed)

Applying the patch **stales recorded provenance** (new sha `4661cedb…`, 418
lines): `reports/round-88/r88-author.md:17` (sha + line count),
`reports/round-88/r88-scribe.md:66` (sha), `reports/round-88/r88-reviewer.md:47`
(sha identity vs working tree), and the reviewer's/author's line citations —
`r88-author.md:138` `:327`→`:323`, `r88-reviewer.md:82` `:155–160`→`:151–156`,
`:99` `:255`→`:251`, `:155` `:270–281`→`:266–277`. The author's custody copy
`corpus/live/r88-author/proj/r88_surfaces.gd` stays at `78370a04…` (the bytes
that were measured) and would then differ from the fixture — intentional
custody semantics. Runtime weight is zero (dead statements only), so the honest
recommendation is: **apply only as a bundle with the reviewer's F1/F2 fixes
(same probe, same pinned rows) and update the three citations in the same
landing; otherwise defer.** The patch is left unapplied and proven.

## 8. Result

- **Deletions made (scratch-proven, unapplied):** 2 sites / **−4 lines**,
  `r88_surfaces.gd` 422 → 418, sha `78370a04…` → `4661cedb…`; patch
  `corpus/live/r88-simplifier/r88-simplifier-fold.patch` (`git apply --check`
  clean; end-to-end apply reproduces the folded bytes exactly).
- **Proven:** folded tree **215/215 PASS**; **0 tuple mismatches** vs control
  and vs both canonical runs; touched arms byte-identical in 4+4 direct reps;
  parse rc=0 both sides; the only raw delta is the normalized traceback line
  numbers.
- **Preserved contract:** all 215 rows, all 8 r88 pins, the `expected_errors`
  exact-shape entry and both gates, the descendant ordering razor, the `.tscn`,
  and `run_battery.py` (untouched by this fold).
- **Cross-checks:** no dead CASES rows; no unused allowlist/gate/ctx keys; the
  cross-probe boilerplate duplication is the established self-contained-probe
  convention (rejected).
- **Tradeoff:** probe-sha/line citations stale on apply (three reports) for
  zero runtime gain — bundle or defer.
- **Custody notes:** the shared tree is byte-identical to session start for
  every tracked file this seat could have touched; the sole tracked-dirty entry
  is `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` (mtime 15:33:01,
  compiled from the current battery source), **not written by this seat** — no
  command of mine imports `run_battery` (all Python invocations are stdlib-only;
  the battery is exec'd as `__main__`) — consistent with a concurrent lane's
  audit import; left untouched. Cosmetic report nit: `r88-author.md:18` says the
  `.tscn` is "(5 lines)"; it is 4 lines / 89 B (scribe measured 4 as well).
- **Stop line:** the next candidates would harm an axis — SP3/SP4/SP10
  (failure-shape canaries and negative controls), SP5 (evidence output), SP6
  (teardown/host robustness), SP7 (setter-existence coverage), SP8/SP9
  (provenance / unproven necessity), and any pinned-byte or cited-receipt
  change. Stopped here.

Seat output complete.
