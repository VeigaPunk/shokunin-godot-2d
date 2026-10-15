# r90 verifier — independent non-author verification of `ee20575`

Seat `VERIFIER` (g2d lane r90, independent non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7, 32 cores. Target:
`ee205757c7302992013bfd13085c449ef2504355` (*r90 author: 12 rb_lattice rows
(247 total) — tps-qualified pins, eng=Dummy precondition gate, typed refusals,
dy=n*g*dt^2 oracle*). Receipts: `corpus/live/r90-verifier/` (index in
`RECEIPTS.md` there). Author report: `r90-author.md`.

No `lsp` device / no GDScript server on this host (unchanged lane state);
verification is fresh-process execution + AST/byte analysis only. **No tracked
writes, no commits.** All artifacts are untracked `corpus/live/r90-verifier/`
scratch + this report. **Frozen probeParent: zero subagents dispatched** —
the assignment is execution-bound (battery + probe launches), which a
read-only `labrat` cannot run; recorded rather than silently omitted.

## Method — frozen tree

```
git archive --format=tar ee20575 | tar -x -C corpus/live/r90-verifier/tree
```

- **Fileset**: `git ls-tree -r --name-only ee20575` (99,503) vs extracted
  `find -type f -o -type l` (99,503) — **0 diffs** (`freeze/fileset-diff.txt`
  empty).
- **Content**: `GIT_DIR=… GIT_WORK_TREE=tree git diff --quiet ee20575` →
  **rc=0**.
- **Fixture shas (frozen tree)**: `rb_lattice.gd` = `10da2291…`,
  `rb_watch.gd` = `e349faa0…`, `run_battery.py` = `76c0b1f5…`,
  `project.godot` = `8de8b3af…` — all match the author's declared pins;
  `rb_watch.gd` is sha-identical to the scout copy (`e349faa0…`), and
  `rb_lattice.gd` differs from scout `4f201e85…` exactly by the declared fold
  (header comment, `_guard()` eng=/tps= emitter, `_dh()`/`_pair()` pairing
  helpers, `impedge`/`lag` arms, `PASS rb_lattice` → `PASS r90_lattice`
  rename) — nothing else.
- **AST census of frozen `run_battery.py`**: CASES = **240 tuples** (228+12);
  all 12 r90 rows present verbatim (`rb_lattice.gd`, exit 0, correct
  `--frames=` on freezelock=120/lag=30); `expected_errors` += exactly the 2
  cases / 3 entries claimed (`comrefuse` → `:376` text; `impedge` →
  `p_inertia<0` + `p_mass<=0`); `r90_expected_errors_all_matched` gate present
  over `case.startswith("r90_")`; r90 block sits at idx 224–235 with
  `crash_spontaneous_sigabrt` adjacent at 236 — the descendant/crash tail
  preserved. The commit's own run_battery.py diff is **insertion-only**
  (0 `-` lines). 240 CASES + 7 meta rows = 247 result rows, matching the
  author's count.

## Results per dispatch item

### 1. Battery ×2 under load — rep1 FAIL on non-r90 flakes, rep2 full green; **r90 12/12 PASS in both**

| rep | verdict | r90 rows | r90 gate | non-r90 fails |
|---|---|---|---|---|
| runs1 `20261015T221709358848Z` | FAIL | 12/12 PASS | `r90_expected_errors_all_matched=true` | `overlap`, `transition`, `negative_transition` (scene-readiness class) + `probe_error_clause_surface` (census cascade: `census_bare_classifier_consistent=false`, dead=2 — both `negative_transition` entries of the flaked row) |
| runs2 `20261015T222444014470Z` | **PASS** | 12/12 PASS | `=true` | none — 247/247, all gates true, dead=0 |

Load throughout: ~100–130 runnable on 32 cores — **entirely foreign**
(sibling lane's `r90c_hog` ×N, `bash while` loops, an r94-critic node
process); no verifier-spawned hogs were needed.

**rep2 is byte-identical to the author's green rep9**: tuple compare
`common=247 new_only=0 old_only=0 tuple_mismatches=0`, and a signature-level
diff on all 247 rows yields **zero diffs** — the committed bytes reproduce a
full green under heavier load than the author's. rep1's only diffs vs rep9
are the 4 documented flake rows; `rows_with_expected_errors=57` in both my
reps (author's claimed 55→57). `probe_error_clause_surface` failures are
pure cascades — every `*_expected_errors_all_matched` gate (r87–r90 +
phys2d) stayed true in both reps.

### 2. Fresh arms on committed bytes — **48/48 byte-exact**

Each of the 12 arms ×4 fresh reps in the battery's launch shape
(`timeout -s KILL 25 godot --headless --path proj --script res://rb_lattice.gd
-- --arm=<a>`) on the frozen fixture bytes: **rc=0 all, PASS line byte-exact
to the committed signature all 48, `err_uniq=1` per arm**. The two
error-carrying arms emit exactly the whitelisted refusals each rep:
`comrefuse` 1× `ERROR: Condition "center_of_mass_mode !=
CENTER_OF_MASS_MODE_CUSTOM" is true.` (`rigid_body_2d.cpp:376`);
`impedge` 1× `"p_inertia < 0"` (`:334`) + 2× `"p_mass <= 0"` (`:324`).

Production `classify_process` AST-extracted from the frozen harness (segment
sha256 `749fa0607e77…` — same as author/scout): **48/48 classified PASS**;
with the allowlist stripped both error arms **bare-reject 8/8** and
allowlist-pass 8/8 — the whitelist entries are load-bearing, not dead.

### 3. Boundary folds — all three land and discriminate

- **eng= precondition**: Dummy-physics boot (`physics/2d/physics_engine="Dummy"`
  project override, `arms/dummy_gravity.out`) emits `eng=PhysicsServer2DDummy
  tps=60 … ncb=0 cb0_rel=-1`, all bodies frozen at spawn, rc=0, **0-byte
  stderr** — the silent-vacuity shape; the emitted line mismatches the pin
  (`eng` differs) so the row cannot pass vacuously. Byte-identical to the
  author's `dummy_gravity.out` receipt — that receipt is genuine.
- **tps qualification (real 30-tps run)**: with a project.godot override
  `physics/common/physics_ticks_per_second=30`, `lag` emits `tps=30
  step=0.033333 dy=32.6667 a_y=506.3334` — mismatches the pin on `tps`,
  `step`, and every physics value; the 60-tps pin cannot be satisfied by a
  30-tps run. **Verified true.**
- **Oracle-collapse boundary**: every pinned impulse lane reads
  `iI ∈ {0.031250, 0.024000}` — all ≥0.024, far inside the resolvable band;
  `impedge`'s post-state `w=15.0000 iI=0.031250` proves the refusals leave
  physics untouched; `lag` derives `exp=N=30` from the observed callback
  count (`acc["an"]`), never from `--frames` (source line confirmed).
- **Pairing keys**: every motion row carries `ncb`/`cb0_rel`/`obs0_rel`/
  `pf_delta`/`tick_dh` (lag carries the count as `an=30,bn=30`/`exp=N=30`);
  `order` additionally carries `cbpf_dh`. AST-verified across all 12 pins.

### 4. Independent re-derivations — **55/55 analytic + 5 own-probe live cells**

`probes/rederive.py` (pure-Python closed forms vs AST-extracted pins):

| id | re-derivation | basis |
|---|---|---|
| R1 | lag oracle `dy=n·g·dt²=8.1667`; `a_y=g·dt²·n(n+1)/2=126.5834`; `b_y=n(n−1)/2=118.4167`; `bpre/bpost=(n−1)·g·dt / n·g·dt` | closed form |
| R2 | impulse: `iI=1/I` for circle r8 (`0.03125`) and rect 20×10 (`0.024`); `w=T·iI` (15.0/11.52); `w=cross(r,J)·iI` (−15.0/−11.52); `v=J·im=−60` | rigid-body impulse law |
| R3 | order arm cb0–cb4/cblast/f1–f60 — **discrete damped-fall law** `v_{k+1}=v_k(1−d·dt)+g·dt`, `y=dt·Σv` reproduces all 16 values | float64 sim vs 4dp pins |
| R4 | damp arm f60: default (tld 0.1) `482.2250`, rep0 `498.1666`, rep05 `425.5192`, comb05 (tld 0.6) `412.9205` | same law, 4 damp values |
| R5 | gravity arm: g05/g2/gm1 linearity, `zv` damped drift from vy0=−30, `zv0` const −15.0000, `cf`=g1 | linearity + damp law |
| R6 | freezelock `f_lock` −128.0000 = −100 −60·(28·dt) — impulse applied at await-1 lands 28 steps | write-lag accounting |
| R7 | write `wman` f60 `481.8333` = `g·dt²·60·59/2` (manual-integrator one-step lag) | closed form |

`probes/v90_probe.gd` (verifier-owned; own parse, own rigs/parameters) on the
frozen project bytes:

- **census**: `nprops=88`, `u6count=57`, all 9 enum values — byte-agree with
  the props pin's claims.
- **rest margin**: own rig r=10 (author used 8) rests at `y=-9.7000` — the
  0.3px solver-margin law reproduces on a different radius.
- **impulse**: own r=5/m=2 body `iI=0.040000`, torque-200 → `w=8.0000`
  exactly; own m=4 body offset-impulse → `w=-5.0000` (cross sign law), and
  its `vy=12.4584` independently confirms the damp recurrence
  (`12.5·(1−1/600)²` — my rig left linear damp at default COMBINE 0.1).
- **lag**: own manual-integrator rig ran a **late pairing** (`n=39` for 40
  awaits) — `dy=10.6167` still equals `n·g·dt²` exactly: the oracle holds
  when `n` comes from callbacks, which is precisely why the pin derives
  `exp=N=` from `an`, not `--frames`.
- **damp**: own REPLACE-0.3 cell measured `44` effective steps for 45 awaits
  (`y=251.1597` = closed form at n=44 — another late pairing, my probe calls
  `_run` directly rather than `call_deferred`). See F2.

### 5. Prior-row identity

Author-level: `r89-author` green rep5 (235 rows) vs `r90-author` green rep9
(247): `common=235 new_only=12 old_only=0 tuple_mismatches=0` — exactly the
r90 block added, zero shared-row drift. My own green rep2 vs rep9:
`common=247 … tuple_mismatches=0` and zero signature diffs (§1).

## Census / hygiene

- Every launch `timeout -s KILL`-bounded; **0 stray godot of mine at exit**;
  no verifier hogs spawned (foreign load ~100–130 sufficed). Foreign
  processes untouched.
- Footprint: `corpus/live/r90-verifier/` (untracked; `tree/` extraction
  dominates ~1.7G, prunable) + this report. `manifest.sha256` covers all
  files outside `tree/` (744 entries).
- `git status` shows **zero tracked modifications**; nothing committed.

## Findings (ranked)

- **F1 (MEDIUM — author-report evidence mislabeled; landed rows unaffected).**
  The author's "30-TPS" receipts `corpus/live/r90-author/f_pair_30tps.rep{1,2}.out`
  are **byte-identical to an ordinary 60-tps `--frames=60` run** (my
  `arms/f60_freezelock.out` diff = identical on both). The stated mechanism
  `--physics-ticks-per-second 30` is **not a valid CLI flag on this build** —
  it is silently ignored exactly like a nonsense flag (`--bogus-flag-xyz`
  produces the same rc=0/0-byte-stderr/byte-identical PASS). The author's
  `ncb=60 pf_delta=60` reads as "half-rate physics" but is simply the
  default `--frames=60` window (and a real 30-tps run could not print
  `pf_delta=60` under `--frames=120`; the receipt's `s_on` rest `-7.7000`
  is also the 60-tps value). **The conclusion the receipt was offered for is
  nevertheless independently TRUE**: my real 30-tps run (project-setting
  override) emits `tps=30 step=0.033333 dy=32.6667` — a loud mismatch on
  `tps`, `step`, and every motion value, so no 60-tps pin can be satisfied
  cross-tps. Impact is confined to report accuracy: one evidence caption
  ("under `--physics-ticks-per-second 30` …") describes a run that did not
  happen. Recommend a lane note correcting the mechanism (project override
  or `Engine.physics_ticks_per_second`, not a CLI flag).
- **F2 (LOW — pairing variance observed at 60 tps under load).** My own
  probe (direct `_run` call instead of the author's `call_deferred` entry)
  hit the late-body pairing twice under load ~100–130: `n=39/40` callbacks
  on the lag rig and `44/45` effective steps on the damp rig — at **60 tps**,
  not only at 30. The author's arms all sync0-paired (`cb0_rel=1`) in 48/48
  standalone + 8-way-concurrent + 24 in-battery observations, so this is not
  a landed defect; it confirms the pairing fields (`ncb`/`cb0_rel`/`pf_delta`)
  are load-bearing: a slip on a pinned arm fails loudly rather than passing.
- **F3 (LOW — rep-level flake residue, pre-existing).** rep1 FAILed at top
  level on `overlap`/`transition`/`negative_transition` +
  `probe_error_clause_surface` census cascade — the documented
  scene-readiness class on rows r90 does not touch; rep2 was fully green
  byte-identical to the author's green. Zero diffs attributable to r90
  bytes on any shared row in either rep.

## Residual risks / disclosures

- **R1** — rep1 was not green: under ~100–130 foreign load the documented
  flake classes fired on non-r90 rows (loudly caught, non-cascading into
  r90; all five `*_expected_errors_all_matched` gates stayed true). rep2
  supplied the quiet green the dispatch prefers — and it was
  signature-identical to the author's.
- **R2** — `nprops=88`, the `props=[…]`/`methods=[…]` lists, `Thread Group`
  header, and `d_*` defaults are build-version tokens (author's own caveat);
  they flip loudly on an engine bump — intended.
- **R3** — the 4-dp physics pins ride float32 fixed points on this build
  (author's caveat); a solver change moves the last decimal.
- **R4** — F1 means one sentence in the author report describes evidence
  that was never produced; everything else in the report I checked
  (Dummy receipt, rep table, census payload, arm-stability claims) is
  accurate.

## Verdict

**VERIFIED-WITH-RESERVATIONS.** The committed `ee20575` bytes are exactly
what the author claims: frozen tree byte-identical (fileset 99,503/0-diff,
content rc=0, all four fixture shas match, `rb_watch.gd` scout-verbatim,
the `rb_lattice.gd` fold exactly as declared), harness delta insertion-only
(240 CASES, 12 r90 rows verbatim, 2-case/3-entry `expected_errors`, r90
floor gate, descendant adjacency preserved), all 12 rows PASS in both
loaded battery reps (24/24 row-instances; rep2 a full 247/247 green
byte-identical to the author's green run), 48/48 fresh-arm payloads
byte-exact with the production classifier accepting all and the two
allowlists proven load-bearing (8/8 bare-rejects), all three boundary folds
live-verified (Dummy vacuity loud via `eng=`, real 30-tps mismatch via
`tps=`/`step=`/physics values, impulse lanes inside the resolvable iI band
with `exp=N=` callback-derived), and 55/55 analytic re-derivations plus 5
verifier-owned probe cells all agree with the pins — including the
`dy=n·g·dt²` oracle holding through a late pairing on my own rig.

Reservations: (a) **F1** — the author's cited 30-tps receipts are mislabeled
60-tps `--frames=60` runs produced under a nonexistent CLI flag; the
conclusion they supported is independently verified true, so this is a
report-accuracy defect, not a landing defect; (b) rep1's top-level FAIL on
documented pre-existing non-r90 flake classes under ~100–130 foreign load —
rep2's identical-byte green covers it; (c) F2 — 60-tps pairing variance is
real (observed on a differently-timed entry), which is why the `ncb=`/
`cb0_rel=`/`pf_delta=` fields the author pinned are load-bearing rather
than decorative.
