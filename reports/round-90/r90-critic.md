# r90 critic — adversarial review of committed `ee20575` (12 `r90_lattice_*` rows, 247-row battery)

Seat `CRITIC` (g2d lane r90) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.7.
Reviewed commit **`ee20575`** (HEAD at session start; parent `a08a190`).
**No tracked write, no commit.** Seat-owned artifacts: `corpus/live/r90-critic/**` + this report.

**Worktree churn (not this seat's).** The worktree went dirty mid-session from a sibling
seat (r89-fold edits to `corpus/fixtures/run_battery.py`, `corpus/fixtures/geo2d_lattice.gd`,
`corpus/.gitignore`, `corpus/live/.gitignore`, `corpus/live/r89-author/manifest.sha256`).
Nothing of it was touched. Every harness-derived check below runs against a **frozen copy of
the committed blob** (`corpus/live/r90-critic/run_battery.committed-ee20575.py`,
sha256 `76c0b1f56b3d03acf011f5a3d71095c741903d47938ae2155e5d8a31a198bfe6`); I verified that the
sibling's worktree edits leave the r90 CASES block **and** the `classify_process` segment
**byte-identical** to the committed revision (so earlier worktree-based reads were also valid).

**probeParent disclosure.** Exactly one read-only `ufo-labrat` was dispatched (bounded depth-2);
the licence is now exhausted — no second dispatch. Its substrate exposed no shell/exec
capability, so the pre-registered regime probe returned **INCONCLUSIVE (not executed, zero
side effects, repository untouched)**. I then ran the identical pre-registered matrix myself as
seat-owned evidence (§5): hypothesis **FALSIFIED**, 8/8 byte-equal.

**`lsp` disclosure.** No `lsp` device / GDScript server on this host (same as every prior r89/r90
seat); all checks are fresh-process receipts plus the AST-extracted production classifier
(`classify_process` segment sha256 `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`,
the same segment r89 author/critic/reviewer used). No symbol-aware operation was required.

**Load regime.** Every launch `timeout -s KILL 15`, all in the battery's exact launch shape
(`godot --headless --path <proj> --script res://rb_lattice.gd -- <flags>`). Host carried
48 foreign `yes` hogs, 16→34 foreign spinning bash loops and sibling godot processes
throughout; this seat added 16 then 32 named `r90c_hog*` hogs. loadavg **76 → 126** across the
session. Own hogs killed at the end; no stray process; `proj/` gains no files (no `.godot`).

---

## 0. What I attacked and how — 123 seat-owned receipts (122 probe launches + 1 driver smoke)

| # | probe | receipts |
|---|---|---|
| 1 | all 12 arms ×3 under load (12 arms, `timeout`-bounded) | `runs/load.*` ×36 |
| 2 | all 12 arms ×2 under ~1.6× load (32 own hogs) | `runs/load2.*` ×24 |
| 3 | `contacts` ×8 under max load (sleep-onset pin) | `runs/heavy.contacts.rep{1..8}.*` |
| 4 | startup-race hunt: `order` ×6 single-CPU-pinned + 12 hogs on that CPU | `runs/starve.order.rep{1..6}.*` |
| 5 | concurrency: 6 simultaneous godot (gravity/order/freezelock/contacts/lag/impedge) | `runs/conc.*` |
| 6 | Dummy-physics boot, all 12 arms (engine precondition) | `runs/dummy.*` ×12 |
| 7 | true 30-tps **project** (`proj_tps30/`), 7 tps-sensitive arms | `runs/tps30.*` ×7 |
| 8 | bogus CLI flag `--physics-ticks-per-second 30` (claim test) | `runs/flag30.gravity.*` |
| 9 | pre-registered regime matrix: `--fixed-fps 60` ×3, `--frame-delay 200` ×3, both ×2, props control | `runs/ffps.*` ×9 |
| 10 | frame-flag binding: `freezelock`/`lag` without their `--frames` | `runs/noframes.*` ×2 |
| 11 | mutation battery (mechanism removed in seat-owned fixture copies) | `runs/mut_*` ×10 |
| 12 | re-derivation of the author's own 6-rep receipts through the production classifier | `runs/` of `corpus/live/r90-author` ×72 (read-only) |
| 13 | absence-token micro-probe (`center_of_mass_local`) | `runs/coml_check.*` |

Plus: the author's two green battery reps re-parsed (`runs9`, `runs12b` verdicts.json), and the
battery's floor-gate census recomputed from seat-owned receipts (`census.py`).

---

## 1. Findings (ranked)

### F1 — MEDIUM · the tps-qualification fold's stated evidence is void: `--physics-ticks-per-second` is not a Godot option and is silently ignored

The author report's mandatory-fold §1 (and the `run_battery.py` r90 block's "tps
qualification" bullet) justify the tps-qualification; the report's stated evidence is
`corpus/live/r90-author/f_pair_30tps.rep{1,2}.out` — "under
`--physics-ticks-per-second 30` … `ncb=60` … vs the 60-tps pin `ncb=120`". That flag does not
exist in this build:

- `godot --help | grep -i physics` → **no match**; `strings /usr/bin/godot | grep -i physics-ticks`
  → only the project setting / `Engine` methods, no CLI option string.
- Launching the committed fixture with `--physics-ticks-per-second 30` produces a **byte-identical
  60-tps PASS line** (classifier PASS, 0 B stderr): `runs/flag30.gravity.*`.
- The receipt itself proves it: `f_pair_30tps.rep{1,2}.out` show `tps=60`, `ncb=60`,
  `f30=f_normal[y=-7.6969]`, `f_lock[y=-128.0000]` — the 60-tps/`--frames=60` values. A **true**
  30-tps project (`proj_tps30/`, `physics/common/physics_ticks_per_second=30` — the method the
  boundary itself used, `corpus/live/r90-boundary/RECEIPTS.md:21`) gives
  `f_normal[y=-7.7000]`, `f_lock[y=-156.0000]` (`runs/tps30.freezelock.*`). The receipt cannot be
  a 30-tps run.

The second half of the claim is also wrong as a *mechanism*: **the pairing fields do not carry the
effective rate.** At a true 30-tps project with the same `--frames`, every motion row prints the
60-tps pin's pairing fields byte-for-byte — `freezelock --frames=120`: `ncb=120 cb0_rel=1
obs0_rel=1 pf_delta=120 tick_dh=1:119` (pin-identical); `gravity`/`order`: `ncb=60 … 1:59`;
`lag --frames=30`: `ncb=30 … 1:29`. They are step-count echoes (one `await` = one step) and are
tps-blind at fixed frame counts. The *rate* is carried by `tps=` (a project-setting echo) and the
**numeric motion values** (`tps30` token diff = `tps=` + motion only; `runs/tps30.*`).

**Consequence.** No false pass: all seven arms tested at a true 30-tps project classify **FAIL**
(props/impulse/impedge on the `tps=` token alone; the motion arms on `tps=` plus differing
values), the 30-tps `late_body` pairing is genuinely never pinned, and the rows are correctly
tps-discriminating — the fold is *landed* correctly. But the report's stated receipt and
mechanism are void, and the flag is a trap for the next seat: a "30-tps receipt" produced with it
is a 60-tps run. Correction needed in `reports/round-90/r90-author.md`
(§"30-TPS deliberately not pinned") and in the r90 block comment in `run_battery.py`; the bogus
flag must not be reused.

### F2 — MEDIUM-LOW · `comrefuse`/`impedge` payloads are state-identity-blind (demonstrated row-level false positive; the battery-level census is the only guard)

Every "post-refusal" value in these two rows equals the property default
(`inertia=0.0000` AUTO, `mass=1.0000`, `center_of_mass=0,0`), so the rows cannot distinguish
"write attempted and refused" from "write never attempted". Demonstrated on seat-owned fixture
copies (committed fixtures untouched):

| mutation (seat copy) | row verdict with the production classifier + committed allowlist |
|---|---|
| `proj_mut_comrefuse`: drop `a.center_of_mass = Vector2(4, 0)` (the refusal trigger) | **PASS** (identical PASS line, 0 B stderr) |
| `proj_mut_impedge`: drop `inertia = -5.0`, `mass = 0.0`, `mass = -1.0` (all three triggers) | **PASS** (identical `set=` payload, 0 B stderr) |

The refusal *event* is enforced only by the battery-level dead-entry floor
(`r90_expected_errors_all_matched`, a discrimination of the separate
`probe_error_clause_surface` row). That guard **does** work — recomputed on the mutated receipts:
entries dead → `r90_expected_errors_all_matched=False`; on the real fixture the same recomputation
gives `matched=1` (comrefuse) and `matched=1`+`2` (impedge, one entry covering the two `mass<=0`
lanes) with `dead_entry_count=0` → `True`, matching the author's rep9 census exactly. The
top-level verdict requires every row to PASS (`run_battery.py:3900` in the committed blob), so
the battery fails loudly end-to-end. Residuals: (a) a seat reading only the row's PASS line cannot see the refusal;
(b) the `at: …:376/:334/:324` **line** attribution is never matched by the harness (the census
matches only the message line), so the "typed refusal ladder" line claims rest on the boundary's
evidence plus the emitted stderr, not on a pin. Both cheaply closable (e.g. a distinct
post-refusal probe field, or a required-stderr pin like the r89-fold F1 shape).

### F3 — LOW · `props`'s `methods=[…]` is a keyword-filtered list, not a method census

The arm collects only method names containing `impulse|force|torque|state|gravity|damp|constant`
(`rb_lattice.gd:184-187`) and sorts them. The property list (`props=[…]`, `nprops=88`) **is** a
complete census; the method token is not. A method outside those keywords is invisible to the pin
(both added and removed). The row's PASS line labels it plainly as `methods=`, so this is a
precision note on the report's "property/method/enum census" wording, not a false pass.

### F4 — LOW · one-directional tokens (`<null>`/`-1` absence, `eng=` class-only)

- `coml_prop=<null>`, `d_center_of_mass_local=<null>`, `u_center_of_mass_local=-1`: verified
  accurate — this build exposes only `center_of_mass_mode|center_of_mass` on the instance and in
  ClassDB, and `get("center_of_mass_local")` returns null with 0 B stderr
  (`runs/coml_check.*`). They can only flip *if the property appears*; they verify no positive
  claim. (Loud in the one direction that matters.)
- `eng=` proves the **live server class**, not the configured engine. The boundary showed
  `"Jolt Physics"` and garbage strings silently fall back to GodotPhysics2D
  (`r90-boundary.md` §3), which still prints `eng=PhysicsServer2D` and passes. That is honest
  (the live engine really is GodotPhysics2D) but a reader should not read `eng=` as "the project
  asked for GodotPhysics2D".

### F5 — INFO · `tps=` is a project-setting echo (author-disclosed; recorded because F1 shows how it is misread)

`Engine.physics_ticks_per_second` reflects the project setting, so `tps=60` discriminates a
project-setting change (30-tps project → FAIL) but not an effective-rate change. On tps-invariant
rows (`impulse`, `impedge`) the payload is byte-equal at a 30-tps project **modulo the `tps=`
token** (`runs/tps30.impulse.*`, `runs/tps30.impedge.*`) — consistent with the author's
disclosure; the rate-sensitivity of the motion rows comes from the numeric values, not from
`tps=`/pairing fields (F1).

---

## 2. What survived (positive verifications)

1. **Byte-stability / no envelope needed.** 12/12 rows `out_uniq=1`, `err_uniq=1`, rc=0, PASS line
   byte-equal to the committed pin, in **every** seat-owned regime (36 + 24 + 8 + 6 + 6 + 12 + 9
   launches) **and** in all 72 of the author's own 6-rep receipts re-classified through the
   production classifier. The one 30-tps mode the boundary found is not reachable at 60 tps here.
2. **Dummy precondition works.** Under `physics/2d/physics_engine="Dummy"` all 12 arms fail
   loudly at the **first token** (`pin='eng=PhysicsServer2D' got='eng=PhysicsServer2DDummy'`,
   `runs/dummy.*`); no row can pass vacuously. This is exactly the fold the boundary demanded.
3. **Mechanism mutations are detected** (seat copies, 0 B stderr, classifier FAIL):
   `rb_watch.gd` forwarding suppressed → `order` `ncb=0`, `damp` `tld=-1.0000`;
   `contact_monitor=false` → `entered=0`; `can_sleep=false` → `ncb=60` (proves `ncb=45` **is** the
   step-count sleep-onset pin, stable 11/11 under load); `gravity_scale` write removed → all
   gravity lanes collapse; `lock_rotation` removed → `f_lock w=-9.3694`. Only the two refusal rows
   are state-identity-blind (F2).
4. **Frame-flag binding.** `freezelock` without `--frames=120` → `ncb=60` vs pin `120`;
   `lag` without `--frames=30` → `exp=N=60`, `a=y=498.1666` vs pin — both FAIL loudly
   (`runs/noframes.*`). The battery's per-row flags are load-bearing.
5. **Typed refusals are emitted as claimed.** Seat receipts show the exact messages and
   `at: set_center_of_mass (scene/2d/physics/rigid_body_2d.cpp:376)`,
   `set_inertia (…:334)`, `set_mass (…:324)` — matching the boundary §5/§6 and the author report.
6. **Floor gate is real and wired.** `r90_expected_errors_all_matched` covers the `r90_` prefix,
   lives in `sf_discriminations` (committed blob `run_battery.py:2589`), the meta row's verdict is
   `all(...)` (`:2604`), and the battery verdict requires all rows PASS (`:3900`). Recomputed
   `True` on the committed fixture; `False` on both mutated copies.
7. **Commit hygiene.** `ee20575` is **insertion-only** for `run_battery.py` (0 deleted lines;
   `+74`), and `rb_lattice.gd`/`rb_watch.gd` are new files (707/9 lines) — prior rows are
   byte-unchanged by construction. The 12 rows sit ahead of the crash/descendant tail
   (`r90_lattice_lag` at CASES line 527, `crash_spontaneous_sigabrt` 529,
   `descendant_pipe_detached_control` 531) so the `sleep 8` gap to the meta probes is preserved.
8. **Fixture identity.** `rb_lattice.gd` `10da2291…`, `rb_watch.gd` `e349faa0…`,
   `project.godot` `8de8b3af…` match the report/comment pins; no `user://`, no file/lock/shared
   state in the probes (verified by grep and by `proj/` being unchanged after every run).
9. **247-row claim.** 240 CASES + 7 default meta rows = 247; the author's `runs9`
   (`212551992799Z`) and `runs12b` (`220233737605Z`) verdicts.json are 247/247 PASS with all 39
   meta discriminations True and the r90 census entries live (`matched_lines` 1 and 1+2).
10. **30-tps bimodality independently reproduced.** My true-30-tps `order` ran the *sync0* mode
    (`cb0_rel=1`, `cb0≡f1`) while the boundary's t30 batch ran *late_body* 12/12 — the
    startup-window instability is real and is correctly never pinned. This also shows the failure
    at 30 tps is loud regardless of which mode the boot takes.

---

## 3. Questions the dispatch implies, answered

**False-positive shapes (a row that passes when it shouldn't).** F2 is the demonstrated one
(row-level, covered in-battery by the census gate). Everything else failed its mutation:
every one of the 8 mechanism-mutation runs (watch forwarding suppressed on two rows × two
variants, contact monitor off, sleep gating off, gravity-scale write off, lock-rotation off)
produced a classifier FAIL. There are no crash rows in the r90 block, so the r89-F1
"crash-cause-blind" class has no instance here. No vacuous token could be found in the
10 measured rows: their payloads are computed from live state, and removing the mechanism moves
the pinned string.

**Scheduler/host-conditional pins the boundary missed.** None found. `contacts ncb=45` is the
sleep-onset step count (proved by mutation), stable 11/11 including 8 runs at loadavg ~125. The
`cb0_rel=1 / ncb=frames / tick_dh=1:(frames-1)` pairing held in 6 single-CPU-starved runs, 6-way
concurrency, 60 loaded runs, 8 clock-regime runs and the author's 13 battery reps. The only
unstable mode anywhere is the 30-tps `late_body`, which no r90 pin touches.

**Rows that pass only because a sibling process is alive.** None. All state is in-process; the
probes touch no `user://`, no files, no locks. 6 simultaneous godot processes (including two
motion arms and the contact/freeze instruments) each emitted their pinned line byte-identically.

**Envelope gaps.** None at 60 tps: 12/12 rows are single-mode over 123 seat launches + 72 author
receipts + 35 boundary runs. The block deliberately ships no envelope; the claim "byte-stable on
this build" is the correct shape.

**Allowlist/census correctness.** Independently recomputed: `bare_rejects=True` for both
allowlist rows (entries are load-bearing, not decorative), `dead_entry_count=0`,
`r90_expected_errors_all_matched=True`, and the mutated copies drive the gate False (F2).

**Insertion ordering / prior-row identity.** Verified (item 7 above); the author's
`tuple_mismatches=5` compare claim is consistent with an insertion-only diff plus the documented
flake/meta classes — not re-derived row-by-row, but structurally guaranteed by the 0-deletion diff.

**Cross-seat consistency (the sibling `r90-reviewer` report landed while this seat ran).**
Agreement: its F2 == this report's F1 (the nonexistent `--physics-ticks-per-second` flag; the
"30 tps" receipt is a 60-tps run) — two independent seats, same measurement. Its F6 (the floor
gate enforces only ≥1 match, not per-run multiplicities) is the weaker form of this report's F2
(which additionally shows the refusal *event* is not row-level-pinned at all). Its F1 (no r90
evidence tree tracked in `ee20575`) is acknowledged; this seat's receipts are untracked by the
same seat convention — folding is the orchestrator's call, and the rows themselves gate on the
committed bytes. **One discrepancy to record:** the reviewer's residual-risk bullet says an
effective-rate change without a project-setting change "is caught only by
`ncb`/`pf_delta`/`tick_dh`" — measured **false** here: at a true 30-tps project those tokens are
byte-identical to the 60-tps pin (they are step-count echoes), and the catch is `tps=` plus the
numeric motion values (§1 F1 token diff). Readers should use this report's token-level
measurement.

---

## 4. Verdict

**PASS-WITH-RESERVATIONS on the committed bytes `ee20575`.** No blocking defect.

The 12 rows are byte-stable and correctly classified under every regime this seat could construct
(load to loadavg 126, single-CPU starvation, 6-way concurrency, Dummy engine, clock-regime flags,
30-tps project), the engine precondition genuinely kills the Dummy-vacuity class, the frame flags
and refusal allowlists are load-bearing, the floor gate is real and wired, and the commit is
insertion-only. The boundary's three folds are **landed** in the rows.

The reservations are evidentiary, not behavioral:

- **F1 (MEDIUM)** — the tps-qualification fold's *stated* evidence is void (nonexistent,
  silently-ignored CLI flag; the cited receipt is a 60-tps run) and the stated mechanism
  ("effective rate carried by the pairing fields") is measured false: at a true 30-tps project the
  pairing fields are pin-identical and only `tps=` + the numeric motion values move. The rows
  still fail loudly at 30 tps, so the fold's *effect* is correct; the report/comment text needs
  correction and the flag must not be reused.
- **F2 (MEDIUM-LOW)** — the two refusal rows cannot see the refusal event from their own payload;
  the battery-level census is the sole guard (verified to work). Worth one hardening field in a
  future round.
- **F3–F5** — precision/hygiene notes (keyword-filtered method list; one-directional absence and
  `eng=` tokens; `tps=` echo).

Neither reservation flips a verdict today; F1 is cheaply corrected in prose, F2 in one token.

---

## 5. ProbeParent labrat + pre-registered regime matrix

The single labrat licence was used (depth-2, read-only). Its substrate had **no shell/exec**
tooling: it returned **INCONCLUSIVE — probe not runnable**, with zero files/processes created and
the repository untouched (its own report is the receipt for that claim).

The pre-registered hypothesis it could not test — *"at 60 tps the committed `r90_lattice_order`
pairing can be flipped to a `late_body` shape by `--fixed-fps 60` and/or `--frame-delay <ms>`"* —
was then executed by this seat, unchanged: control (already covered), `--fixed-fps 60` ×3,
`--frame-delay 200` ×3, both ×2, plus a `props --fixed-fps 60` control.

**Result: FALSIFIED.** 8/8 `order` runs are **byte-equal to the committed pin**
(`ncb=60 cb0_rel=1 obs0_rel=1 pf_delta=60 tick_dh=1:59 cbpf_dh=1:59`), 0 B stderr, rc=0
(`runs/ffps.*`); the `props` control is byte-equal too. Frame pacing does not move the physics
callback pairing on this build — consistent with the boundary's `--delay` ladder (18 runs) and
this seat's starvation/concurrency runs. The 60-tps pairing pin is scope-closed for every regime
tested.

---

## 6. Evidence index (`corpus/live/r90-critic/`, `manifest.sha256`)

| artefact | path |
|---|---|
| frozen committed harness blob (all checks pinned to it) | `run_battery.committed-ee20575.py` (sha256 `76c0b1f5…`) |
| production-classifier replay of all tags | `analyze.py` (`classifier_sha 749fa060…`) |
| dead-entry census + floor-gate recomputation | `census.py` |
| single-receipt classifier check | `check_one.py` |
| author's 6-rep receipts re-classified | `verify_author_receipts.py` |
| 12-arm driver (battery launch shape, `timeout -s KILL 15`) | `run_arms.sh` |
| concurrency + single-CPU starvation driver | `stress.sh` |
| loaded replay ×3 / ×2 / contacts ×8 | `runs/load.*`, `runs/load2.*`, `runs/heavy.contacts.*` |
| startup-race hunt | `runs/starve.order.rep{1..6}.*` |
| 6-way concurrency | `runs/conc.*` |
| Dummy-boot engine precondition | `proj_dummy/`, `runs/dummy.*` |
| true 30-tps project + verdicts | `proj_tps30/`, `runs/tps30.*` |
| bogus-flag control | `runs/flag30.gravity.*` |
| pre-registered clock-regime matrix | `runs/ffps.*` |
| frame-flag binding | `runs/noframes.*` |
| mutation battery (8 mutated fixture copies, incl. the two F2 demonstrations) | `proj_mut_*/`, `runs/mut_*` |
| absence-token micro-probe | `probes/coml_check.gd`, `runs/coml_check.*` |
| launch project (committed fixture copy) | `proj/` (sha pins verified) |

**Reproduce:** `bash run_arms.sh proj load 3 -- props comread comrefuse gravity damp order write
impulse impedge freezelock contacts lag` → `python3 analyze.py load`; `python3 census.py load`;
`python3 check_one.py r90_lattice_gravity runs/flag30.gravity.out runs/flag30.gravity.err
runs/flag30.gravity.rc`; `python3 verify_author_receipts.py`; `bash stress.sh proj conc conc`.
All runs under ≥16 `yes` hogs; each launch `timeout -s KILL 15`.
