# r89 critic — adversarial review of committed `8cea888` (20 rows: `geo2d_lattice_*` + `input89_edges_*`)

Seat `CRITIC` (g2d lane r89) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.7.
Reviewed commit `8cea888` (HEAD at session start; parent `2c4b1ff`).
**No tracked write, no commit.** Seat-owned untracked artifacts:
`corpus/live/r89-critic/**` + this report. Sibling r90-author lane's uncommitted
edits (`M corpus/fixtures/run_battery.py` +12 `r90_lattice_*` rows, `??
rb_lattice.gd/rb_watch.gd`) were in flight during the session — not this seat's,
not touched; committed-file checks were done against the `8cea888` blob where it
mattered (all r89 content identical between worktree and commit).

**probeParent disclosure:** zero descendants spawned (the one-labrat licence was
not needed — every hypothesis below was falsified/confirmed directly from fresh
execution receipts and the AST-extracted production classifier).

**`lsp` disclosure:** no `lsp` device / no GDScript server on this host (same as
all prior r89 seats); all checks are fresh-process receipts plus textual/AST
reads. No symbol-aware operation was required (review-only seat).

**Load regime (≥12 hogs requirement):** during every probe below, the host ran
**64–124 concurrent `yes` hogs** (loadavg **85–153**): 48–108 foreign hogs from
sibling lanes plus this seat's own 16. All my launches are `timeout -s KILL 25`
bounded or the battery's own `subprocess.run` shape; no stray process left.

---

## 0. What I attacked and how

| # | probe | receipts |
|---|---|---|
| 1 | all 20 arms ×3 fresh under 64–124 hogs (battery launch shape) | `runs/*.{out,err,rc}` ×180 |
| 2 | `input89_edges_exact` mode census: **77 loaded reps** (40-file + 24-sweep + 8-pipe-launcher + 3-first + 2-concurrent) | `runs/{bigload,sweep2,pipe,conc}*` |
| 3 | false-positive probes through the **production `classify_process`** (AST-extracted from the committed `run_battery.py`, segment sha `749fa060…` — same as author/reviewer) | `probes/fp_*.gd`, `runs/fp_battery_shape.json` |
| 4 | concurrency isolation: two `exact` + `axisdev` + an idle sibling godot, all overlapping | `runs/conc_*` |
| 5 | committed-envelope extraction + byte-diff vs live mode-L / scout mode-Q | `check_envelope.py` |
| 6 | volatile-token sweep (RID/uid/address/pid/`<Node#>` patterns) over all rep outputs | `runs/` |
| 7 | wall-time margin of physics arms vs the 8 s bound, under load | inline `date` timers |

**Result of the replay under extreme load:** 19/19 non-envelope rows classify
**PASS 3/3**, `out_uniq=1 err_uniq=1`, constant rc, signature on stdout —
byte-stable at loadavg ~150. `input89_edges_exact`: 3/3 PASS, all mode L.
`lineempty`: rc 134 ≡ −6 ×3, whitelists unused, stderr = libstdc++ assert only.

---

## 1. Findings (ranked)

### F1 — MEDIUM · `geo2d_lattice_lineempty` is crash-cause-blind and signature-stream-blind (demonstrated false-positive shape)

The reviewer's V5 calls this row "fail-safe in both directions"; **one direction
is not safe.** The committed evidence is `expected_exit=-6` +
`signature='R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)'`
— a *pre-call* diagnostic line, necessarily (the PASS line is unreachable).
Three gaps compose:

1. `run_process` merges `stdout + stderr` into one blob, so `signature in output`
   is **not stream-anchored** — a signature on stderr alone satisfies it.
2. `expected_exit=-6` binds only the signal class, never the call site.
3. The stderr assert text (`Assertion '__n < this->size()'`,
   `/usr/include/c++/16/bits/stl_vector.h:1253`) is **never examined** —
   crash rows have no expected-stderr mechanism (the `expected_errors`
   allowlist only ever *permits* `ERROR:` lines; it cannot require content).

Demonstrated through the production classifier on this build, battery launch
shape (`subprocess.run`, no `timeout` wrapper) — `runs/fp_battery_shape.json`:

| probe | stdout sig | stderr sig | rc | classify |
|---|---|---|---|---|
| `fp_wrongcause.gd` — prints the exact signature, then aborts via `clip_polygons` on an **INF-vertex polygon** (boundary §4.1 `bool_inf_clip`: bare abort, 0 B stderr) — `offset_polyline(∅)` is never called | ✓ | — | −6 | **PASS** |
| `fp_stderr_sig.gd` — emits the signature **only on stderr** (`printerr`), same wrong-cause abort | — | ✓ | −6 | **PASS** |
| real `lineempty` arm (control) | ✓ | — | −6 | PASS |

So the row proves only "the process died SIGABRT *after* the byte appeared in the
merged stream" — not "`offset_polyline(∅)` hits the Clipper2 assert". A build
where the empty path is fixed but the process aborts later in the same script
(teardown assert, or a second buggy call) still passes. The window is narrow
(nothing else runs between the print and `_pass()` in this arm) and the shape is
convention-shared with `crash_spontaneous_sigabrt`/`crash_self_sigkill`, but
this row *advertises a specific cause* in its diagnostic. Hardening note for the
author lane: a `required_stderr`-style pin (e.g. the `__n < this->size()`
fragment) would bind the crash to the Clipper2 assert class.

### F2 — MEDIUM-LOW · `input89_edges_exact` envelope is verdict-blind to which mode fired (disclosed design, residual quantified)

The 2-payload tuple is byte-verified: payload[0] == scout's quiet emission
(`corpus/live/r89-scout/runs/in_exact.rep1.out`), payload[1] == **my** live
mode-L emission (`runs/input89_edges.gd.exact.load.rep1.out`), and the payloads
differ in exactly one token (`just_after_flush=w_jp[… inex=true]` ↔ `inex=false]`;
neither is a substring of the other). Consequences measured/derived:

- **77/77 loaded reps emitted mode L** this session (loadavg 85–153), all
  byte-equal to payload[1] — the envelope absorbs correctly under load.
- A *permanent* drift to mode L (i.e., `is_action_just_pressed`'s
  modifier-widening never firing) is **verdict-invisible**: the emitted line
  goes into `output[]` for auditors, but no census records which payload
  matched and no gate notices a dead payload arm. This is the intended
  mode-cell semantics — the disclosure stands — but note the asymmetry vs
  `expected_errors`, which *does* have a dead-entry floor gate.
- **Mitigation already present:** the same widening law is pinned at the
  level-state API by `poll_shiftW_on_plainW_binding=w[ex=false inex=true]`
  — stable in **all** loaded reps — so the semantic claim survives even if the
  just_pressed variant rots. Only the `is_action_just_pressed` surface is
  softly unpinned.

### F3 — LOW · harness tolerates unexpected stderr `WARNING:` lines for every CASES row (pre-existing shape, confirmed for r89 rows)

`classify_process` rejects lines containing `ERROR:` (unwhitelisted),
`SCRIPT ERROR:`, `Parse Error:` — and **nothing else**. A `WARNING:` line on
stderr passes silently (contrast `classify_streams`, which rejects any
unexpected stderr line but is not the CASES path). The scout's §5.5 hazard —
the re-parse `WARNING` from `parse_input_event` — would sail through a green
row if it ever reappeared. Today every r89 row emits **0 B stderr** (verified ×3
under load; `atlasempty`/`polyendpoly` emit only their whitelisted ERROR + `at:`/
backtrace continuations, which carry no `ERROR:` token and are ignored).
Latent, not a current defect — worth one line because the input probe family is
exactly where this warning class lives.

### F4 — LOW · `geo2d_lattice_ring`'s `colliders=n=1 contour0_only` is an unconditional literal

`_arm_ring` emits the literal string `"n=1 contour0_only"` (geo2d_lattice.gd:456)
— it is **not computed**, unlike `_arm_ring2`'s `"n=%d all_contours" % n` (:474).
If the arm were ever refactored to attach both contours, the label would still
claim `n=1`. The discriminating evidence (`ring=k=2{…}` contour dump +
`drop_center=y=-47.8043 hits=1`) is computed and stable, so the token is
cosmetic — but it's an unverified claim sitting inside a pinned string.

### F5 — LOW · committed fixture ships dead arms with a falsified comment

`geo2d_lattice.gd` keeps `_arm_bridge_hole`/`_arm_bridge_hole2` (not in CASES —
receipts only per scout §6.1). `_arm_bridge_hole`'s comment asserts *"merge() of
a contained square yields TWO contours: outer + hole"* — **refuted by the
round's own measurement** (F2 in scout §4: `merge` collapses containment to
k=1; `clip`/`exclude` are the hole-producers). Harmless at runtime; misleading
to a future reader mining the fixture for laws.

### F6 — INFO · conditional pins inventory (all verified loud-fail; none missed by boundary that I could move)

| token | class | moved? |
|---|---|---|
| `joys=0` | host hardware (`get_connected_joypads`) | can't be faked by a sibling *process* — needs a real/uinput device |
| `nmethods=86`, `sig=[…]`, `eia_avail=true`, `dz_ax0=0.2000`, `dz_ui_accept=0.5000` | Godot build constants | flip loudly on a build bump |
| `tps=60 frames=60` (bridge/ring*/ringhits) | fixtures `project.godot` (no `[physics]` block) + literal loop bound | loud on a tracked project change; `--frames` honored by the probe but never passed by the battery (verified) |
| `82.3000` / `-47.8043` | solver fixed point (~6–10 float32 ULP from the 4-dp boundary — reviewer's V7 recomputation) | byte-stable ×3 under loadavg ~150 here |
| `ringhits` 2-frame settle | sim-deterministic | byte-stable under load |

No *new* conditional pin surfaced beyond the boundary's §5 list.

---

## 2. Questions the task asked, answered

**Is a 3rd `input89_edges` mode reachable?** **No — structurally bounded, not
just unobserved.** The only frame-scoped read in the signature is
`just_after_flush=w_jp[ex=X inex=Y]`: `ex=true` requires an exact modifier match
of a shift+W event against a plain-W binding — impossible on this engine's
matching rules — and `inex` is binary ⇒ the token space is exactly the two
whitelisted values. A "3rd mode" would need a *different* token to move; every
other token is a synchronous, non-frame-scoped read (`eia_*`, `poll_*` level
state, control). Empirically: **77/77 loaded reps this session emitted a line
byte-equal to one of the two committed payloads** (all L); zero lines matched
neither payload; zero `?` lines. Combined with scout 20 + boundary 51 + author 12
+ battery 5 → ~165 observations, only Q/L. If another token ever moves, the row
fails loudly — the envelope is two *exact* payloads, not a matcher. Envelope
complete modulo F2's blindness.

**Rows that pass only because a sibling process is alive:** **none found, and
the regime this report ran under is itself the counter-proof.** Every r89 pin is
computed from within-process state — pure math calls, a per-process `Input`/
`InputMap` singleton, an owned `World2D`, `ClassDB` introspection. Two
concurrently-launched `exact` processes + `axisdev` + an idle sibling godot all
emitted byte-identical lines (`runs/conc_*`). `joys=0` is a host-hardware count,
not a process property. No probe writes `user://`, touches a shared lock, or
needs `.godot` (verified: `proj/` gains no files across all runs).

**False-positive shapes (passing when they shouldn't):** F1 (demonstrated),
F4 (literal token). Every other row's signature is a *post-execution* PASS line
with computed tokens — a mid-arm GDScript error or crash means no PASS line and
a non-zero rc ⇒ fail-loud; `--arm=bogus_arm` and missing-arm runs echo the
invoked arm (`PASS geo2d_lattice bogus_arm …`, `PASS geo2d_lattice  …`), so the
`_:` fallback can't produce a matching signature (verified live).

**Scheduler/host-conditional pins the boundary missed:** none found (F6 table).
My boundary-extension attempts: pipe-vs-file launcher parity under load (8/8 L —
mode is launcher-independent, reproducing boundary's 2×2), concurrent-process
isolation, volatile-token sweep (no RID/uid/pid/address anywhere in 200+
receipts), and wall-margin measurement (worst physics arm ~1.9 s vs the 8 s
bound at loadavg ~150 — ~4× headroom; deeper oversubscription would fail-loud
as TIMEOUT, a flake-availability risk only, not a false pass).

**Allowlist/census correctness:** author's rep5 `verdicts.json` re-parsed —
`r89_expected_errors_all_matched=true`, `dead_entry_count=0`,
`rows_with_expected_errors=55`, atlasempty `matched=1`, polyendpoly `matched=2`
(two emitted occurrences, one entry — per-line matching covers both; the
*occurrence count* itself is data, not a gate — reviewer's F5, concur). Under
my load the ERROR lines emit byte-identically (246 B / 572 B stderr).

**Insertion ordering:** verified — the 20 rows sit ahead of
`crash_spontaneous_sigabrt`; `descendant_pipe_detached_control`'s `sleep 8` gap
to the meta probes is preserved.

---

## 3. Verdict

**PASS-WITH-RESERVATIONS on the landed bytes.** No blocking defect: all 20 rows
are byte-stable and correctly classified under loadavg ~150, the envelope is
byte-exact and (provably) exhaustive over its reachable token space, the
allowlist census is tight, and no cross-process confound exists.

The reservation is **F1**: the crash row verifies "SIGABRT after the diagnostic
byte" rather than "the Clipper2 empty-polyline assert" — a demonstrated
false-positive shape (wrong-cause abort and stderr-only signature both classify
PASS). Convention-shared, narrow in practice, but the only place in the block
where a pinned claim is structurally weaker than it reads. Secondary residual
**F2**: the exact row cannot see a permanent mode-L drift at the
`is_action_just_pressed` API (the law is still pinned at `is_action_pressed`,
so the semantic claim survives). F3–F5 are hygiene/precision nits.

Neither reservation flips a verdict today; both are cheaply closable
(stderr-fragment pin on crash rows; optional mode-census in the envelope
record) if a future seat wants the margin.

## 4. Evidence index (`corpus/live/r89-critic/`, `manifest.sha256` — 442 entries)

| artefact | path |
|---|---|
| 20-arm loaded replay (×3 each) | `runs/*.{out,err,rc}` |
| `exact` mode census ×77 loaded | `runs/{*.bigload.*,*.sweep2.*,pipe_exact.*,conc_exact_*}` |
| false-positive probes + battery-shape classification | `probes/fp_{wrongcause,stderr_sig}.gd`, `runs/fp_battery_shape.json`, `fp_battery_shape.py`, `check_fp.py` |
| production classifier extraction + per-row verdicts | `analyze.py` (sha `749fa060…` segment) |
| envelope byte-diff vs committed tuple | `check_envelope.py` |
| arm-fallback / no-arm probes | `runs/fp_{bogusarm,noarm}.{out,err}` |
| launch project (fixtures `project.godot` byte-copy `8de8b3af…`) | `proj/` |
| drivers | `run_arms.sh`, `run_all_loaded.sh`, `pipe_check.py`, `runs/concurrency.sh` |

Reproduce: `bash run_all_loaded.sh 3 load` then `python3 analyze.py load` under
≥12 `yes` hogs; `python3 check_envelope.py`; `python3 fp_battery_shape.py`.
