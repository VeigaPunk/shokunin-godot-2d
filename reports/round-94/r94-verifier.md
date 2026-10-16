# r94 verifier — independent non-author verification of `c7228893`

Seat `VERIFIER` (g2d lane r94, independent non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, default
60 tps), Python 3.14.7, 32 cores. Target:
`c7228893434ad70674791eda52794e96369a6744` (*r94 author: 19 particles rows
(314 total) — folded scout probe (4-line diff: okb windows, floor); 314/314 x2*).
Receipts: `corpus/live/r94-verifier/` (index in `RECEIPTS.md`; `manifest.sha256`
432 entries, `sha256sum -c` rc=0, scratch families excluded per
`MANIFEST-SCOPE.txt`). Author report `reports/round-94/r94-author.md`; inputs
`reports/round-94/r94-scout.md`, `reports/round-94/r94-boundary.md`.

**`lsp` disclosure.** No `lsp` device and no GDScript language server is exposed
to this seat (unchanged lane state, r89–r93); every semantic check below is a
static/AST read of the committed bytes plus fresh-process execution — the
recorded fallback. The change is one new fixture plus an insertion-only harness
block (no renames, no symbol moves), so no symbol-aware operation was possible
or required.

**Frozen probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2, agent
`05c89fb7`) was dispatched with one bounded static hypothesis in four clauses
over the committed bytes: (A) the fixture-vs-frozen-probe non-comment diff is
exactly the four declared code lines; (B) all 19 committed signatures are
contiguous substrings of their arms' scout canonical receipts; (C) the fixture
`match arm:` block covers exactly the 19 CASES arms; (D) no tps/`--fixed-fps`
surface exists in the fixture and the launch project pins no tps. Results:
**A CONSISTENT** (4 code lines; all other diffs are comments), **B CONSISTENT
with one tooling caveat** (census signature is ~8.8 KB and exceeded the probe's
line reader; first ~2 KB + line lengths verified), **C CONSISTENT**,
**D CONSISTENT** (`physics_ticks_per_second` only in a comment; project.godot
3 lines). Its census caveat is closed below by this seat's byte-exact
classification (`signature in output` over the full 8.8 KB string in 33
receipts). No second dispatch; the labrat wrote nothing, spawned nothing.

**Concurrent-worktree disclosure.** The lane advanced under this seat: HEAD was
`c7228893` at freeze time and is now `72315b14` (`86ace53c` r94 reviewer →
`cd83d736` r94 scribe → `72315b14` r94 critic); `git diff --name-only c7228893
HEAD -- corpus/fixtures` is **empty** — the verified fixture bytes are unchanged
at HEAD. A foreign seat is editing the shared worktree's
`corpus/fixtures/run_battery.py` right now (`+163/−0`, an uncommitted **r95
block**, CASES 307 → 359); re-checked, all 19 committed r94 CASES tuples are
**byte-identical** in the worktree copy and the r94 floor gate is untouched, so
that edit is additive to this report's scope. Nothing in this report reads the
worktree copy of `corpus/fixtures`: all battery reps, fresh arms and probes ran
the **frozen extraction** (`git archive c7228893 corpus/fixtures`), whose 81
files match their git blob sha1s exactly (`freeze/blob-identity.txt`, 81/81,
0 mismatches).

**Tracked writes: zero net, one accidental write detected and reverted.** All
artefacts are untracked `corpus/live/r94-verifier/**` plus this report. One
incident: importing the *worktree* harness via `importlib` (a read-intent
comparison) caused CPython to regenerate the tracked
`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`; it was detected,
reverted with `git checkout HEAD --`, and the file now hashes to its committed
blob `c98dead1…` again (`git status` shows only the foreign `run_battery.py`
edit, which is not this seat's).

---

## 1. Method — frozen committed bytes

- **Whole-repo content check**: `git diff --quiet HEAD` → rc=0 at freeze
  (`git rev-parse HEAD` = `c7228893`); `git status --porcelain` carried no
  tracked modification at freeze time.
- **Fileset**: committed `corpus/fixtures` subtree = **81 entries** vs 81 files
  in the extraction — 0 diffs (`freeze/fileset-*.txt`). 81 entries include the
  pre-existing tracked `__pycache__/run_battery.cpython-314.pyc` (added r69).
- **Blob identity**: every extracted file hashed as a git blob sha1 against
  `git ls-tree -r c7228893` — **81/81 match, 0 mismatches**
  (`freeze/blob-identity.txt`).
- **Pins (frozen)**: `particles_lattice.gd`
  `0701e813e50cdb50e05f0df0194d0baf94c1240f361e941949414dd5c52c00a9`
  (763 lines — byte-equal to the author's declared pin); `run_battery.py`
  `2b1f4df5426a8da679c58c58057817b75f6fd879f9ffc8ab1045b03deae04238`
  (4427 lines); frozen scout probe `e6a2e0f55c6bbeaa…b930` (741 lines).
- **Commit scope**: `git show --stat c7228893` = 3 paths —
  `corpus/fixtures/particles_lattice.gd` (+763),
  `corpus/fixtures/run_battery.py` (+91), `reports/round-94/r94-author.md`
  (+201). No other fixture, no `project.godot`, **no receipts corpus** (unlike
  r93's 235-file author corpus — see F5).
- **Launch project**: `corpus/fixtures/project.godot` is 3 lines and pins no
  `physics_ticks_per_second`; the battery scratch edits only `config/name`
  (receipted: `freeze/launch-scratch-project.godot.txt`).

**Harness delta `94377598 → c7228893`** (`probes/audit-committed.txt`):

- `git diff --numstat` = **91 / 0** — two pure-insertion hunks:
  `@@ -795,6 +795,86 @@` (CASES block) and `@@ -3020,6 +3100,17 @@` (floor gate).
- CASES **288 → 307** tuples; the 19 `r94_*` rows sit at **CASES indices
  284–302** (observed at **result indices 284–302** of 314), immediately after
  `r93_anim_blend_interleaved` and immediately before
  `crash_spontaneous_sigabrt`. All 19 flags are exactly `--arm=<arm>`.
- `expected_errors` r94: **0 cases / 0 lines**; `required_stderr`: **0 cases**.
- The floor gate `r94_expected_errors_all_matched` (predicate
  `case.startswith("r94_")`) is present, same named-by-round shape as r87–r93
  (8 round gates in the harness).
- The production `classify_process` segment hashes to
  `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`
  (AST source segment) — **identical in the parent commit, in `4b75151`, in the
  worktree copy, and to the r89–r93 pin `749fa0607e7707e6…`**.
- **Scout-row provenance**: all 19 committed r94 tuples are **byte-identical to
  the scout's `ROWS_PREFIX`** entries (19/19), and every committed signature is
  a prefix of the scout's full-line `ROWS` entry for the same arm (19/19). The
  committed block is the gating-prefix form, not the ±1-tail full-line form.

**Fixture fold vs the frozen scout probe** (`diff`, re-derived here and by the
labrat): the non-comment diff is **exactly four code lines** — the three
`_okb(…, 4, 7)` → `_okb(…, 1, 7)` windows in `_arm_cpu_pause`
(`okvis`/`okvp`/`okpm`) and `int(round(0.5 / spec)) + 1` →
`int(floor(0.5 / spec)) + 1` in `_arm_cpu_request`. `okts` stays `[15,25]`;
every other differing line is a comment (header fold note, discipline/law
comments, `cpu_never`/`cpu_contam`/`amount_mid`/`request` comments).

---

## 2. Battery ×3 on the frozen committed harness

| rep | run dir | start loadavg (1m) | verdict | r94 rows | r94 gate |
|---|---|---|---|---|---|
| rep1 | `runs/20261016T063334001914Z/` | not stamped (host ≈83; overlapped a foreign 8-hog control battery) | FAIL 314 rows — 5 fails | **19/19 PASS** | True |
| rep2 | `runs/20261016T064310819140Z/` | 58.25 | **PASS 314/314** | **19/19 PASS** | True |
| rep3 | `runs/20261016T065158572001Z/` | 56.52 | FAIL 314 rows — 2 fails | **19/19 PASS** | True |
| author r1 | `../../runs/20261016T055703426158Z/` | — | PASS 314/314 | 19/19 PASS | True |
| author r2 | `../../runs/20261016T060430025246Z/` | — | PASS 314/314 | 19/19 PASS | True |

- **95/95 r94 row-instances PASS across the five committed-harness runs**; the
  `r94_expected_errors_all_matched` gate is `True` in all five; `dead_entry_count`
  is 0 in rep2 and 2 in reps 1 and 3 — the 2 dead entries are
  `negative_transition`'s, as below.
- **The failures are the documented pre-existing load class, not
  r94-attributable.** rep1: `overlap` (CASES 4), `transition` (5),
  `negative_transition` (12), `audio_bus_route` (37), knock-on
  `probe_error_clause_surface`. rep3: `negative_transition` +
  `probe_error_clause_surface`. All four are CASES indices ≪ 284 (they execute
  minutes before the r94 block) and have the same failure history elsewhere in
  the corpus: the identical five-row set failed together in
  `corpus/live/runs/20261015T200615022811Z` (an **r88-era** run: 235 rows, r87/r88
  blocks only), and
  `negative_transition`/`audio_bus_route_invalid_control` failed again in a
  concurrent foreign run (`20261016T065335715243Z`). The knock-on shape is
  exact: `negative_transition`'s two allowlist entries die with it
  (`dead_entry_count=2`), flipping `census_bare_classifier_consistent` and
  failing the meta row — the same class r93's verifier recorded in its reps
  3–4. The r94 rows carry no allowlist, so nothing in the r94 block is affected.
- **Per-row stability across the five runs**: every r94 row shows **exactly one
  distinct boolean block** (its pinned signature) across all five runs; 9 rows
  show 2–3 distinct *full lines*, and the differences are exclusively the
  unpinned ` | ` tails (`l025[delta=15→14]`, `ph=60→59`, `pre25[delta=14→15]`,
  `vis[4→5]`, `second_after=15→14`, `stop40[20→19]`, `flip_after`). No pinned
  byte varies.
- **Host conditions**: the lane is heavily loaded and multi-lane (3d r97
  verifier/critic batteries, 2d r94 reviewer/critic batteries ran
  concurrently); rep1 additionally overlapped the r94-simplifier's 8-hog
  control battery (06:34:07–06:36). Loadavg stamps per rep are in
  `battery{2,3}.load.{start,end}`. The boolean-window pins are the load-proof
  form (boundary: 0 rejections at 16 hogs) — confirmed here: the r94 block is
  19/19 in the two FAIL reps as well.

---

## 3. Fresh arms — 57/57 clean

19 arms × 3 reps in the battery's exact launch shape on the frozen fixtures
(`probes/fresh_arms.py` → `probes/fresh-arms.txt`; receipts
`arms/<case>.rep{1,2,3}.{out,err,rc}`):

- **57/57 launches rc=0, 0 B stderr**, every PASS line on stdout.
- **57/57 row classifications PASS** with the production `classify_process`
  (AST-extracted from the frozen harness).
- Slowest arm wall: `cpu_pause` 3.81 s max (harness per-case bound is 8 s) —
  ≈2× headroom; `gpu_headless` 2.96 s, `cpu_expl` 2.76 s.
- Full-line byte stability: 13 rows byte-identical across their 3 reps; the
  other 6 (`cpu_lifetime`, `cpu_expl`, `cpu_speed_pre`, `cpu_pause`,
  `cpu_restart`, `gpu_headless`) vary only in unpinned tail fields — all 57
  classifications PASS and every boolean block is stable (same shape as the
  battery runs).

---

## 4. Signature coverage, fallback forgery, stream hygiene

`probes/signature_coverage.py` → `probes/signature-coverage.txt`: every
receipt of an r94 row's own arm in the canonical corpora is re-classified with
the production classifier and must contain the signature byte-exactly.

- **618 canonical receipts** (scout 143, boundary 323, the five canonical
  battery runs 95, fresh 57) → **EXACT 90 / TAIL 525 / MISS 0 / REJECT 3**.
  The 3 rejections are exactly the boundary's **ff30 `cpu_pause` ×3** — the
  *pre-fold* receipts (`ok=false`) that motivated the fold; §5 re-derives that
  the committed windows admit their measured values.
- **Three foreign-seat battery runs** (control/mutant harness copies of other
  r94 seats) add 57 more r94 row-instances, **all PASS** — grand total 675
  row-instances, 0 r94 failures.
- **Fallback forgery**: 0 `unknown arm=` fallback lines exist in any corpus and
  no signature is a substring of the fallback text (19/19).
- **Stream hygiene**: 523 file receipts carry `.err`; total stderr bytes **0**
  (scout 143 + boundary 323 + fresh 57). The 95 battery row-instances carry no
  `ERROR`/`WARNING` line. The author's "ERROR:-clean, 0 B stderr" claim holds
  on every canonical corpus this seat can see.

---

## 5. The `cpu_pause` fold, verified three ways

The fold is the only behavioral change in the fixture, and its motivation was
the boundary's own measurement that the frozen windows reject 3/3 under
`--fixed-fps 30`. `probes/ff30_fold.py` → `probes/ff30-fold.txt`:

1. **Re-derivation on the boundary's own ff30 receipts** (no new launches):
   measured `vis=4, vis_parent=2, pm_disabled=2, ts0=18` in all 3 reps; the
   committed windows `[1,7]/[1,7]/[1,7]/[15,25]` admit all four → the committed
   row would PASS on the boundary's measured bytes.
2. **Live ff30 on the committed fixture**: `cpu_pause` 3/3 **PASS**
   (`ok=true vis_ok=true vis_parent_ok=true pm_disabled_ok=true ts0_ok=true`).
3. **Live ff30 on the frozen (pre-fold) scout probe**: 3/3 **REJECT**
   (`ok=false vis_parent_ok=false pm_disabled_ok=false`).

So the fold is exactly the fix the boundary demanded, it is load-bearing
(before: reject, after: pass on the same measured values), and it does not
touch the emitted signature text.

---

## 6. Discrimination — would a broken law actually fail the row?

`probes/discriminate.py` → `probes/discrimination.txt`: for every row, take a
fresh receipt that classifies PASS, mutate one pinned token, re-classify.

- **111/111 pinned-token mutations reject** (boolean flips, integer ±1,
  float-last-digit perturbations sampled across each signature, incl. the
  full 8.8 KB census line).
- **32/32 tail controls are admitted** — mutations of the ` | ` tail
  (`fin_after_show`, `delta`, `n_fin`, `ph`, `flip_after`, …) never change the
  verdict, confirming the tail is deliberately unpinned and the pins are the
  boolean blocks.
- **Global rejection axes, all 19 rows**: rc flip 19/19, injected unrelated
  `ERROR:` line 19/19, injected `SCRIPT ERROR:` 19/19.

**The one pin that is not load-bearing for its claim (F1).** For
`r94_particles_cpu_contam` the pinned tokens are structural counts: the fixture
computes `ok = str(out.size() == 2)` (line 396) and `n_never` is `out.size()` —
both true whenever the two labels were appended, regardless of whether either
never-emitter fired. `probes/contam-tautology.txt`: mutating the *unpinned* tail
to a world where neither node ever fired
(`never1[fin_delta=-1 n=0] never2[fin_delta=-1 n=0]`) still classifies **PASS**;
`n_never=2 → 0` **REJECTs**. The measured contamination tail
(`never1[fin_delta=0 n=1] never2[fin_delta=0 n=1]`) is present in **25/25**
scout+boundary receipts of the arm — the law is *evidenced* and stable, but the
shipped row cannot fail for it. (The r94 critic recorded the same defect as its
F1 with a seat-built falsifying mutant; this seat's mutation path is
independent and agrees.)

---

## 7. The `r94_expected_errors_all_matched` floor gate

- **Static**: present, keyed on `case.startswith("r94_")`, over `census_rows`
  entries with `dead_in_run`; **vacuous today** (0 r94 allowlist entries).
- **Live**: `True` in all five committed-harness runs.
- **Mutant run** (`probes/make_gate_mutant.py` → `probes/gate-mutant-build.txt`,
  diff in `probes/gate-mutant-diff.txt`): the frozen harness with **one dead
  r94 entry injected** (`r94_particles_cpu_never` ← a diagnostic that can never
  be emitted) reports `r94_expected_errors_all_matched=**False**`,
  `dead_entry_count=3`, while `r94_particles_cpu_never` itself still **PASSes**
  (its `expected_errors` now carries the injected entry) and every other round
  gate stays `True`. The gate is therefore **load-bearing** — a future dead r94
  allowlist entry cannot die silently.

---

## 8. The 60-tps-only window risk, measured

`probes/tps_windows.py` → `probes/tps-windows.txt`,
`tps-probe/tps-windows.json`: the frozen fixture launched under three project
variants (only `physics/common/physics_ticks_per_second` added), with a
reporter proving the effective tps (`TPS_REPORT physics_ticks_per_second=60/30/120`).

| regime | r94 rows FAIL | rows still PASS |
|---|---|---|
| default (60) | **0/19** | all 19 |
| tps 30 | **10/19** | census, ppm, convert, cpu_never, cpu_contam, cpu_oneshot_flag, cpu_request, gpu_headless |
| tps 120 | **11/19** (+ `cpu_amount_mid`) | census, ppm, convert, cpu_never, cpu_contam, cpu_oneshot_flag, cpu_request, gpu_headless |

This **confirms and quantifies** the author's declared "`_okb` windows are
60-tps-only" risk: the exposure is 10–11 rows (every tick-windowed row), not
the 3 the author's report names. It is **latent today** — the committed
`project.godot` pins no tps, the harness scratch edits only `config/name`, and
the battery never changes tps — but any future project override would reject
the tick-windowed block. (The r94 critic's F3 reports the same 10/11 sets from
its own mutants; this seat's measurement is independent, on the committed
fixture with only the tps key changed.)

---

## 9. Findings (ranked)

**F1 (MEDIUM — discrimination gap, 1 of 19 rows; independently confirms r94
critic F1).** `r94_particles_cpu_contam`'s pinned signature
(`ok=true n_never=2`) is satisfied by any run where the two labels were
appended, so the row cannot fail for the law it claims (add_pf≥1 never-emitters
fire `finished` on first update). Mutation evidence in §6 /
`probes/contam-tautology.txt`: a never-fires world is admitted, `n_never=2` is
load-bearing, and the measured tail is present 25/25. The law itself is not in
question (boundary §8 measured it 24/24; scout uniq=1). Cheap fix when the
block is next touched: fold the tail operands into `ok`, e.g.
`ok = out.size() == 2 and out[0].contains("fin_delta=0 n=1") and
out[1].contains("fin_delta=0 n=1")`. `cpu_never` (the negative side) is not
affected — its `ok` is computed from the measurement.

**F2 (LOW — row shape, declared; confirms r94 critic F2).** The
`round → floor` fold in `cpu_request` is inert in the shipped row: the pinned
steps `0.10/0.05` are integer ratios where `floor` and `round` emit identical
bytes (6/11), so the row binds the `+1` lattice but not the `floor`-vs-`round`
half. The decisive steps (`0.20 → 3`, `0.30 → 2`) live only in the boundary's
receipts. The fixture comment discloses this ("identical for the integer ratios
pinned here"); the falsification is real, the row just cannot exercise it.

**F3 (LOW — documentation; confirms r94 critic F3).** The author's risk note
names 3 rows; measured exposure is **10 rows at tps30 / 11 at tps120** (§8).
No landing defect — latent only.

**F4 (LOW — pre-freeze scout evidence; new).** The scout corpus carries three
non-empty `.err` receipts, one of them for an r94 arm:
`runs/smoke-cpu_pause.err` shows a pre-freeze `_free_node`/`remove_child`
engine ERROR (`Condition "p_child->data.parent != this" is true`) from a
revision before the freeze. **Not reproducible**: the frozen probe and the
committed fixture both run `cpu_pause` at 0 B stderr (3/3 fresh default, 3/3
ff30, plus 57 fresh arms and 95 battery instances). The scout marks its smoke
receipts as not-evidence; the boundary's 323 r94 receipts are all 0 B stderr.
This is the same pre-freeze-revision class the boundary disclosed in §2.

**F5 (LOW — custody; new).** The r94 commit carries **no receipts corpus**
(fixture + harness + report only). The author's smoke pass exists only as prose;
its durable evidence is the two untracked `corpus/live/runs/20261016T05*/`
`verdicts.json` runs, which this seat re-verified (PASS 314/314 ×2, r94 19/19,
gate True). `corpus/live/.gitignore` keeps `runs*/` out of the commit, so the
battery evidence for every round is worktree-only — a standing custody
property, not new to r94.

**F6 (INFO — wall-time margin).** `cpu_pause` is the slowest r94 row: 3.81 s
max fresh (8 s bound, ≈2× headroom) at default tps; at tps30 the critic
measured ~6 s — another reason the tps override is latent-only.

---

## 10. Remaining risks / not measured

- **Host is multi-lane and heavily loaded** (loadavg 53–83 throughout); all
  numbers are host-conditioned. The boolean-window pins held in every rep, and
  the 4 pre-existing row failures are the lane's documented load class.
- **Scout/boundary corpora are untracked worktree evidence** (`runs*/` is
  gitignored); the durable committed evidence is the fixture + harness + the
  author's report. This seat re-derived the load-bearing claims (provenance,
  fold, windows, gate) from the committed bytes rather than trusting the
  corpora.
- **GPU rows are headless-inert only** — `gpu_headless` pins the inertness
  (no `finished`, silent one-shot `emitting` clear, zero `capture_rect`); no
  rendered-path claim is made or verified.
- **Not measured here**: `seed`/particle positions/colors (no headless
  readback), continuous-emitter `amount` coupling (boundary [U], deliberately
  unauthored), `fixed_fps ≤ 5` (stall hazard, unauthored), and any behavior
  outside Godot 4.7.2 headless on this host.

---

## 11. Verdict

**VERIFIED-WR on `c7228893`** — the committed r94 landing is sound on the
frozen committed bytes:

- 19/19 r94 rows PASS in **95/95 row-instances** across five full-battery runs
  (2 author + 3 verifier) on the frozen committed harness; the
  `r94_expected_errors_all_matched` gate is True in all five; every row has one
  stable boolean block with only unpinned-tail variation.
- 57/57 fresh launches clean (rc=0, 0 B stderr); 618-receipt coverage with 0
  missing and only the explained pre-fold ff30 rejections; 111/111 pinned
  mutations reject and 32/32 tail controls are admitted; the floor gate is
  proven load-bearing; the `cpu_pause` fold is verified before/after on live
  ff30 runs; the harness delta is insertion-only (+91/−0) and the production
  classifier is byte-identical to the r89–r93 pin.
- Reservations: **F1** (one of 19 rows cannot fail for its own claim — fix when
  the block is next touched), F2–F6 (row-shape/documentation/custody items).
  None of them makes a row pass on bytes that falsify a *different* row's law,
  and none is a landing blocker.

Canonical judgment remains with the Rust runtime / adjudicator; this seat
implements and reports only. Nothing committed; the only tracked modification
in the worktree is a foreign r95 edit.
