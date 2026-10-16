# r95 reviewer — wave-B gate on the committed PhysicsDirectSpaceState2D query lattice (`9cd47507`)

Seat `REVIEWER` (g2d lane r95) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7, 32 cores.
Reviewed commit **`9cd47507`** (parent `6f817d10`); `HEAD == 9cd47507` at review
start. Diff scope: `corpus/fixtures/dss_lattice.gd`
(**+743/−0**, new), `corpus/fixtures/r95b_order.gd` (**+777/−0**, new),
`corpus/fixtures/run_battery.py` (**+163/−0**: 152-line CASES block + 11-line
gate), `reports/round-95/r95-author.md` (+224). **Zero deletion lines in the
whole commit** (`git show 9cd47507 | grep -c '^-[^-]'` = 0).

**This seat modified no tracked file and made no commit.** `git status
--porcelain` had zero non-`??` lines at review start and at review end; the
author's report file and both fixtures are committed, the two probes are
byte-identical to the frozen lane artefacts, and every run below used the
**pinned export** of `9cd47507` (`corpus/live/r95-reviewer/pinned-tmp/`,
**83/83 files `git hash-object`-identical** to their blobs). Seat-owned writes
are untracked only: `corpus/live/r95-reviewer/**` (manifest covers every file)
and this report.

**`lsp` disclosure.** No `lsp` device is exposed to this seat — the only MCP
server on this host is `rea`, and no GDScript/Python language server answers
these files (same as r89–r94). Every symbol-level statement below is a
textual/AST read of the **pinned** committed bytes plus fresh-process execution
receipts — the literal fallback, recorded so it is never presented as semantic
proof. The diff contains no renames and required no symbol-aware work (two new
fixtures + literal `CASES`/gate inserts), so nothing was hand-renamed.

**probeParent disclosure (frozen, exactly one dispatch).** One read-only
`ufo-labrat` (L2; read/grep/glob only, no shell, no writes) was given four
bounded hypotheses: *(H1)* in the author's four worktree `verdicts.json` files,
all 208 (52×4) r95 rows are `verdict=PASS`, their `signature` field equals the
committed CASES signature, and the signature string appears verbatim in the
row's `output`; *(H2)* in the boundary receipts, each of the 35 authored cells'
committed signature is a whole line in 100% of that cell's receipts (176);
*(H3)* in the scout receipts (99 canonical + 51 loadtest), each of the 17 dss
signatures is present in 100% of its cell's receipts; *(H4)* the tokens
`procwait`/`env`/`layout_changes_order`/`repeat_stable`/`pile_b=`/`pile_rev=`
appear in none of the 52 signatures, `expected_errors` carries 0 r95 keys, and
the r95 gate filters both prefixes. It returned **H1 CONFIRMED** (208/208),
**H2 CONFIRMED with a stated bound** (176 receipts enumerated; `canon` 24/24 and
`periodx_k2` 2/2 byte-verified whole-line, the rest anchored-head; no
counter-example), **H4 CONFIRMED** (all zero; gate text verified), and
**H3 NOT EXECUTED** — it hit its token bound before probing the scout receipts
and reported that honestly. No second dispatch; it wrote nothing. Every
execution number below is this seat's own (my own H3-equivalent is §V5, run
independently of the labrat).

**Concurrent-worktree disclosure.** While this review ran, a sibling **r95
critic** seat executed its own mutants/batteries under
`corpus/live/r95-critic/**` (untracked; first artefacts 04:06), and foreign
lanes kept ~48–112 `yes` blocks on the host (loadavg 84 → 105 throughout). That
work is not mine, does not touch the reviewed commit, and does not affect any
evidence here: every run of mine was launched from the pinned export and the
harness copies *its own directory* into scratch.

**Foreign-worktree disclosure (the tree moved after the reviewed commit).** At
**04:32–04:38**, *during* this review, three wave-B sibling commits landed on
top of `9cd47507`: `5d3a947c` (r95 scribe), `6128778b` (r95 verifier) and
`5097014f` (r95 critic) — all **pure additions** (0 deletions), all under
`corpus/live/r95-{scribe,verifier,critic}/**` and `reports/round-95/**`, and
`git diff 9cd47507 HEAD -- corpus/fixtures/` is **empty**, so the reviewed
bytes are unchanged at HEAD (`5097014f` at review end). Separately, a
concurrent **r96 author** lane began writing a +233-line r96 block
(`scene_io_lattice.gd` + 60 rows) into the live tracked
`corpus/fixtures/run_battery.py`; that write is not this seat's, does not touch
the reviewed commit, and cannot affect any evidence here (every run of mine
used the pinned export of `9cd47507`, whose r95 block is intact and identical
to the reviewed bytes). The operator should note that the live worktree has
moved ahead of the reviewed commit.

**Verdict: PASS on the landed bytes.** The landing is exactly what the dispatch
card and the author report claim: a pure 52-row insertion against two new
fixtures that are **byte-copies of the frozen lane probes** (zero diff), with
all 17 `dss_lattice_*` signatures equal to the scout's `ROWS_PREFIX` set
element-wise (13 full-line + the four order-vector cells cut to order-free
head prefixes) and all 35 `r95b_order_*` signatures equal to whole `PASS` lines
in the boundary receipts. All 52 pins are present in 100% of the receipts of
their own arm across my 364 fresh launches (5 load reps + ff30 + ff120 per
arm), the author's four runs, the scout's 150 and the boundary's 176 receipts;
364/364 fresh launches are rc=0 / 0 B stderr / 0 `ERROR:` and classify PASS
with the production classifier extracted verbatim from the pinned harness
(segment sha `749fa060…`, the r89–r94 recorded segment); the r95 floor gate is
present, covers both round prefixes, and is **armed** (a one-line planted-entry
control flips it `False` and fails the battery loudly); 6 of the 9 forgery
shapes reject 52/52 — the accepted ones are pre-existing battery-wide
classifier properties, declared in F5, and unreachable from the fixtures' own
behaviour. Two independent full-battery runs on the pinned bytes (one under 16
seat hogs, one without) put the block at 52/52 r95 rows and 10/10 gates in
both. Findings F1–F7 are precision / evidence-integrity / pre-existing-
class items; **none changes a pinned byte or a row verdict** (F1 is the one
substantive coverage gap: one r95b row does not exercise its named
construction — see §2).

---

## 1. What was verified clean

**V1 — additive, scoped diff; prior rows untouched; insertion point as
declared.** `git show --numstat 9cd47507` = `+743/−0`, `+777/−0`, `+163/−0`,
`+224/−0`; zero deletion lines anywhere. Two hunks in `run_battery.py`:
152 added lines (48 comment + 52 tuple-head + 52 signature lines = the 52
tuples) and 11 added lines (the gate) = 163. AST row-diff of `CASES` from
`6f817d10` (307 entries) to `9cd47507` (359 entries): **pure insertion of the
52 `r95_*`/`dss_lattice_*` rows** after `r94_particles_gpu_headless` and
before `crash_spontaneous_sigabrt` (common prefix 303, common suffix 4 — the
crash/descendant tail keeps its adjacency to the meta probes). All 307 parent
rows are **field-identical** in the commit (tuple comparison, 0 diffs); all
359 entries are 5-tuples (`case, script, flags, expected_exit, signature`),
names unique, all 52 r95 rows `expected_exit=0`, every signature a `str`, every
`--arm=` implemented in its landed fixture (52/52). Result rows **366 = 359 +
7 meta** (confirmed in my run and the author's runs).

**V2 — provenance byte-exact; no hidden diff.** `corpus/fixtures/dss_lattice.gd`
sha256 `77ae4adb8a47ccf50b5da345720247c035418e31872a117d17cd98913f479627`
(743 lines) is **byte-identical** to the frozen scout probe
`corpus/live/r95-scout/probes/dss_lattice.gd`;
`corpus/fixtures/r95b_order.gd` sha256
`4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490`
(777 lines) is **byte-identical** to the frozen boundary probe
`corpus/live/r95-boundary/probes/r95b_order.gd`. `corpus/fixtures/project.godot`
is unchanged vs the parent (`8de8b3af…`; **no `physics_ticks_per_second`
override** — the 60-tps default the tick-awaiting harnesses assume). The pinned
export of the whole `corpus/fixtures` tree is 83/83 blob-identical.

**V3 — row shape, arms, allowlists, gate.** All 17 `dss_lattice_*` signatures
are **element-wise equal** to the scout's `ROWS_PREFIX` entries (case, script,
flags, exit, signature); the 13 non-vector cells are additionally equal to the
scout's full-line `ROWS`, and the four order-vector cells
(`point_cap[_rev]`, `order_core[_rev]`) are strict prefixes of their full lines,
cut at a ` | `-equivalent token boundary (`cap0=[]` / `add_order=[…]`) — no
order vector is signed anywhere. All 35 `r95b_order_*` signatures are exact
whole `PASS` lines and appear as whole lines in **176/176** boundary receipts
of their own cell across the quiet/load/ff1/ff30/ff120/thr/label/extra batches
(per-cell payload uniq = 1). `expected_errors` carries **72 keys / 0 r95 keys /
0 orphan keys**; `required_stderr` carries 3 keys / 0 r95 keys. The new meta
gate `r95_expected_errors_all_matched` filters
`case.startswith(("dss_lattice_", "r95b_order_"))` — the same
named-by-round / covers-round-prefixes shape as r87–r94 (10 gates total).

**V4 — fresh independent execution (this seat).** 52 arms × (5 load reps +
1 `--fixed-fps 30` + 1 `--fixed-fps 120`) = **364 launches** in the battery's
exact launch shape (`godot --headless --path <pinned-scratch-copy>
--script res://<fixture> -- <flags>`, streams captured separately), on the
pinned export, host loadavg 75–105 with 16 seat hogs plus foreign lanes:
**364/364 rc=0, 0 B stderr, 0 `ERROR:` lines, 52/52 rows PASS in every
condition**, signature present on **stdout** in every receipt. The classifier
used is the production `classify_process` extracted **verbatim** (AST source
segment) from the pinned harness: segment sha256
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` = the
segment recorded by r89–r94, so the r95 rows are judged by the same production
logic as their predecessors. Receipts:
`corpus/live/r95-reviewer/fresh/20261016T071531110784Z/` (1092 receipt files +
`fresh.json`).

**V5 — cross-session and cross-condition pin identity.** For every one of the
52 rows, the printed `PASS` line is **byte-identical (1 distinct line)** across
my 5 load reps, the author's two green runs, and the lane receipts — the scout's
99 canonical + 51 loadtest receipts for the 17 dss cells and the boundary's 176
receipts for the 35 r95b cells. The four prefix rows print exactly one
continuation tail in all 60-tps sources (the unpinned vector text is
condition-stable today — the prefix cut is future-proofing, and the full-line
forms would also gate today, as the scout declared). No row has >1 distinct
pinned prefix anywhere. Tool + data:
`corpus/live/r95-reviewer/tools/cross_session.py`,
`corpus/live/r95-reviewer/cross_session.json`.

**V6 — full battery on the pinned committed bytes (this seat, two runs).**
Run 1 `corpus/live/r95-reviewer/runs/20261016T070817247206Z/verdicts.json`
(16 seat hogs + foreign lanes, loadavg 84→105): 366 rows, verdict **FAIL** —
failing rows are `overlap` ("signal occurred before physics overlap
observation"), `transition` ("initial current_scene identity/marker
mismatch"), `negative_transition` ("probe exceeded 120 frames") and the
downstream `probe_error_clause_surface` (its only false discrimination is
`census_bare_classifier_consistent`, broken by the flaked `negative_transition`
allowlist entries; `dead_entry_count=2`, both `negative_transition`'s own).
Run 2 `…/runs/20261016T072931769603Z/verdicts.json` (seat hogs stopped, host
loadavg 56→75 from foreign lanes): **verdict PASS, 366/366**. In both runs
**52/52 r95 rows PASS, all 10/10 gates `True`, r95 `dead_entry_count=0`.** The
run-1 failures are the documented transition/overlap one-tick flake classes
(r91 reviewer, r94 reviewer, the author's runs 1/3) — they flake under
contention and are green in run 2.

**V7 — row-level mine-vs-author; no perturbation.** 366 common cases vs the
author's green run `20261016T064742446822Z`: the only field differences are the
four flake rows' `verdict`/`actual_exit`; **all 52 r95 rows are
field-identical** (verdict, signature, expected_exit, actual_exit, script,
flags, error, required_stderr, expected_errors). 25 r95 rows have an *output*
difference and it is only the `proc=` process-frame counter in the
`R95B … env=…` diagnostic line (e.g. `canon proc=156` vs `152`; `pf=` and every
payload line identical) — the physics-tick discipline the fixtures pin, not a
perturbation.

**V8 — discrimination (forges reject).** Production classifier + committed pins
on my load rep1 receipts (`tools/discrimination.py`): genuine **52/52 accept**;
`pin_dropped` 52/52 reject; `digit_flipped` 50/50 reject (the 2 rows without
digits are the thin `order_core[_rev]` prefixes); `bool_flipped` 52/52;
`wrong_rc` 52/52; `foreign_error` 52/52; `truncated_mid_pin` 52/52. Three
shapes are accepted **by construction**, all pre-existing battery properties,
not defects of this landing (F5): `prefix_spoof` (trailing token after the pin
— the production classifier is substring-anchored), `stderr_only` (the
production path classifies the merged stdout+stderr blob) and
`cross_case_signature` (any other r95 signature in the output satisfies the
clause — origin-blind presence, the r63 meta's pinned forgery class). Under the
strict stdout anchor (`classify_streams`), `stderr_only` rejects 52/52. The
four prefix rows additionally show `tail_mutation_inert` 4/4 — mutating the
unpinned vector text leaves the row PASS, which is the designed behaviour.

**V9 — the floor gate is armed (control battery).**
`corpus/live/r95-reviewer/ctl/fixtures/run_battery.py` differs from the pinned
harness by **exactly one inserted line** (a planted
`"dss_lattice_census": ("ERROR: ctlB planted dead r95 entry (never matches)",)`
allowlist entry); the end-to-end run
`corpus/live/r95-reviewer/runs-ctl/20261016T072221535240Z/verdicts.json`
(366 rows, verdict **FAIL**) reports
`r95_expected_errors_all_matched=**False**` — the only gate that flips — with
`dead_entry_count=1` = exactly the planted entry
(`dss_lattice_census` entry `dead_in_run: true, matched_lines: 0`), while the
`dss_lattice_census` row itself still PASSes (it is `ERROR:`-clean) and
`probe_error_clause_surface` FAILs. The other failing row is the pre-existing
`input_lattice_pre_frame` envelope flake. So a future r95 allowlist entry
cannot die silently — the property the author claims is demonstrated, not
assumed.

**V10 — boundary-falsification folding audited.** No refuted key is signed
anywhere: `layout_changes_order`/`repeat_stable`/`pile_b=`/`pile_rev=`
occurrences in the 52 signatures = 0; `procwait`/`env` = 0 (the two `[U]`
cells are not authored); every instance-id/RID-shaped token in a signature is a
deterministic default-property echo (`canvas_instance_id=0`, `shape_rid=RID(0)`
in the census defaults), never a live id. The boundary's five verdicts are
carried the way the author declares: the phase ladder (`r95b_order_canon`
t0…t64, `t20==t0`, `distinct_ticks=20`), the k(k−1) law (`periodx` k=2,3,4,5,
5@spacing8, 6,7,8,10 with `expected_kk1` echoed in-line), creation-order
permutations under a fixed tag→position map (`perm0..7`), the label-mirror
counter-pin (`scoutrev`), translation invariance (`celloff_x0/x1000`), the
co-presence attribution (`twopiles`, `warm_keep8`, `warm_k32`), free-order
(`free_ab/ba`, `readd_a`), the above-cap set (`cap40_p{0,1,2}`:
`n0=0 n32=32 n64=40 set32_distinct=5`), the layer-conditional order agreement
(`layers_k0/k1`) and the rigid solver echo (`rigid`). The two demoted `--rev`
cells pin only their construction echo, as declared.

**V11 — the author's committed-run evidence re-read (worktree-only).**
`tools/author_runs.py` re-read all four runs from disk: `…064148780406Z` FAIL
(only `input_lattice_pre_frame`, the documented r87 envelope flake; 52/52 r95,
gate True), `…064742446822Z` PASS 366/366, `…065335715243Z` FAIL
(`negative_transition` + `audio_bus_route_invalid_control` +
`probe_error_clause_surface`; 52/52 r95, gate True), `…065922894811Z` PASS
366/366. Every r95 row carries its signature in its output in all four runs
(208/208, labrat-confirmed independently). `git ls-files corpus/live/runs` = 0
(F3).

**V12 — ERROR-cleanliness claim audited.** Every r95 receipt on disk has 0 B
stderr and no `ERROR:`/`SCRIPT ERROR:`/`Parse Error:` line: scout
`r95_dss_*` 150/150, boundary authored cells 176/176, my fresh 364/364, the
author's four runs 208/208 — consistent with the `expected_errors`/
`required_stderr` "+0 r95 entries" claim (V3) and with the r95 gate's
`True` in every genuine run.

---

## 2. Findings (ranked by severity)

**F1 (medium-low — coverage: one r95b row does not exercise its named
construction; it is a byte-identical duplicate of another row).**
`r95b_order_celloff_y1000` is launched with `--off=0 --offy=1000`, but the
landed probe **never reads `--offy`** (0 occurrences in
`corpus/fixtures/r95b_order.gd`; the option parser stores it in `opt` and
nothing consumes it) and `_arm_celloff` hard-codes y=0.0
(`_pile(["a","b","c","d","e"], off, 0.0)`). Consequently the row's committed
signature is **byte-identical to `r95b_order_celloff_x0`'s** (the only
duplicate-signature pair in the block; `tools/audit_static.py` §S9 records the
pair, the zero `offy` occurrences and the `_arm_celloff` source), and the only
difference between the x0 and y1000 receipts is the
`proc=` diagnostic counter. So the row cannot measure the y+1000 translation
that the author's report table (`celloff_{x0,x1000,y1000} … +1000 y`) and the
boundary §4 ("14/14 isolated translations … y +1000") attribute to it; the
y-axis is unmeasured, and the genuine translation evidence is the 13-value x
ladder (`off=±0.25…±1000`, all identical ladders). Effect on verdicts: none —
the row still exercises arm dispatch and the ladder law, and every other row is
unaffected. Suggested action (future round, author-owned): either drop the row
or make `_arm_celloff` consume `--offy` (then the y-ladder prints, and the row
becomes a real test); the boundary report's y+1000 claim should be treated as
not reproducible from the landed artifact.

**F2 (low — precision: `dss_lattice_shape_rev` is a label permutation behind a
full-line pin).** The author demotes `order_core_rev` and
`point_cap_rev` to head-prefix rows and declares why, but `dss_lattice_shape_rev`
keeps a full-line pin and is built the same index-positioned way
(`for i in order.size(): _mk_body(order[i], Vector2(i*8, 0), …)` with `--rev`
reversing the tag list), so its pinned `touch=[a#0]` (vs `[e#0]`) is a **label
echo**, not insertion-order evidence — exactly the class the boundary §3
refuted for the `--rev` rows. (`dss_lattice_ray_order_rev` is different and
genuine: its tie bodies are created in reversed *tag* order at the same
position, so the add order really flips and `last_added_wins=true` is a second
test.) The row's stated claim (shape predicate/cap semantics) is unaffected.
Effect today: none; a reader could over-read the `rev=true` tail. (The sibling
r95 critic's commit `5097014f`, landed during this review, reports the same
class more strongly for `order_core[_rev]` — a mutant that deletes the query
calls still PASSes — which is consistent with this report's V3/V10 scope note
that those two rows are construction echoes.)

**F3 (low — evidence integrity; the commit carries none of the lane's run
evidence).** `git ls-files corpus/live/runs` = **0**: the four battery runs the
commit message and the author report point at are worktree-only, excluded by
`corpus/live/.gitignore` (`runs*/`). I re-read all four from disk (V11),
reproduced the 52 rows independently (V4/V6) and the labrat re-verified the
208 row/signature/output triples, so no verdict changes. Same shape as the
r92/r93/r94 reviewer F1. Suggested action: force-add the two green runs'
`verdicts.json` in the wave fold, or scope the report's evidence index to
tracked artefacts.

**F4 (low — evidence attribution: the dss rows' ff/threaded invariance was
cited from evidence that measured the r95b cells).** The author's table answers
"17 rows load-stable" with "byte-identical under 16-hog load, `--fixed-fps`
1/30/120, threaded physics … (§8)". The boundary §8 measured the *r95b*
ordering cells; the scout's 150 dss receipts cover load only, and no ff/thr
receipt exists for the `dss_lattice` fixture in either lane. My own ff30/ff120
reps (52/52 PASS, one distinct printed line per row) close the gap for the dss
rows on this host; the cited pointer is imprecise, not the conclusion.

**F5 (low — pre-existing classifier properties, not defects of this landing).**
Three forgery shapes are accepted by the production classifier for these rows
(§V8): a trailing token after the pin (`prefix_spoof`), a PASS line delivered
on stderr (`stderr_only`, merged-blob classification), and another r95 row's
signature present anywhere in the output (`cross_case_signature`). All three
are battery-wide, documented (r63 meta, r89-fold critic F1, r94 reviewer F5),
and unreachable from the fixtures' own behaviour (every arm is `ERROR:`-clean,
`required_stderr`-less and prints its own `PASS <fixture> <arm>` line first);
the strict stdout anchor rejects `stderr_only` 52/52. Note the F1 pair makes
`cross_case_signature` concrete for one row pair (x0/y1000 accept each other's
output) — harmless because the constructions are identical.

**F6 (low — the r95 gate is inert today; its "cannot die silently" property is
verified only by control).** With zero r95 allowlist entries the gate is
vacuously true in every genuine run; it is load-bearing only in the
planted-entry direction, which the control battery demonstrates (§V9). It also
inherits the pre-existing executed-rows-only census scope: a *renamed/orphan*
r95 key would produce no census entry and stay invisible. Same class as r94 F2.

**F7 (informational — the census row's RID/id tokens are defaults).** The only
id-shaped tokens in any r95 signature are in `dss_lattice_census`'s
`defaults=[…]` echo (`canvas_instance_id=0`, `shape_rid=RID(0)`) and
`dss_identity=same_across_calls=true` (a within-process object identity, not a
value pin) — deterministic default-property tokens, author-declared, and the
only rows that would be perturbed by an id change are the `warm_*` cells, which
are not authored. No instance id is ever signed.

---

## 3. Evidence index (seat-owned receipts)

All under `corpus/live/r95-reviewer/` (untracked; `manifest.sha256` covers
every file except itself):

| artefact | path | what it shows |
|---|---|---|
| pinned export | `pinned-tmp/` | `git archive 9cd47507 corpus/fixtures`; 83/83 files `git hash-object`-identical to their blobs |
| static audit | `tools/audit_static.py` → `audit_static.json` | S1 diff/insertion shape; S2 arms; S3 scout-row equality; S4 176/176 boundary whole-line; S4b 99+51 scout presence; S5 allowlists; S6 gate; S7 provenance; S8 excluded tokens; S9 duplicate-signature + `--offy` audit (F1) |
| author runs re-read | `tools/author_runs.py` → `author_runs.json` | four runs: 2×366/366 green; 52/52 r95 and gate True in all four; 0 tracked run files |
| fresh arm receipts | `fresh/20261016T071531110784Z/` (+ `fresh.json`) | 364 launches (5 load + ff30 + ff120 × 52 arms), 364/364 PASS, 0 B stderr, classifier segment sha `749fa060…` |
| my battery runs | `runs/20261016T070817247206Z/verdicts.json`, `runs/20261016T072931769603Z/verdicts.json` | run 1 (load) 366 rows / 4 documented flake rows; run 2 (no seat hogs) **366/366 PASS**; r95 52/52 and 10/10 gates True in both |
| control battery | `ctl/fixtures/run_battery.py`, `runs-ctl/…/verdicts.json` | one-line planted dead r95 entry ⇒ `r95_expected_errors_all_matched=False`, battery FAIL |
| cross-session identity | `tools/cross_session.py` → `cross_session.json` | 1 distinct printed line per row across 5 sources; prefix rows single-tail |
| discrimination | `tools/discrimination.py` → `discrimination.json` | 6 shapes reject 52/52; 3 pre-existing accepts; strict-stream reject 52/52 |
| hogs | `hogs/start.sh`, `hogs/stop.sh`, `hogs/pids.txt` | 16 seat `yes` hogs, PID-tracked and killed by PID (never `pkill`) |

Reproduce the headline checks:
`python3 corpus/live/r95-reviewer/tools/audit_static.py && python3 corpus/live/r95-reviewer/tools/author_runs.py && python3 corpus/live/r95-reviewer/tools/cross_session.py && python3 corpus/live/r95-reviewer/tools/discrimination.py`
(expect: S1 insertion 52 / 0 deletions; 176/176 and 99+51 presence; 364/364
fresh; 1 distinct line per row; 6 forgery shapes rejecting 52/52).

**Remaining risks / blockers.**

- The pinned `k(k−1)` cycle and the ladder vectors are **tick-phase-locked**:
  the rows are reproducible because their probes await exactly 2 physics frames
  (boundary §10); the 13 non-vector dss cells are the broad coverage. My
  ff30/ff120 reps and the boundary's 8-batch matrix found no phase break for
  tick-awaiting harnesses, but a future probe edit that changes the await count
  would change every vector row.
- The `dss_lattice` full-line rows are broadphase-conditioned for a frozen
  scene composition (`warm_keep8` documents the scope limit); a live unrelated
  collider perturbs the returned order deterministically.
- Host was never idle (loadavg 75–105; a sibling critic seat ran concurrently);
  "load" is seat-relative. All invariance results are the point, not the
  absolute values.
- The live tree has moved ahead of the reviewed commit (two wave-B evidence
  commits at HEAD, `6128778b`; a concurrent r96 author's +233-line block in the
  live `run_battery.py`) — see the foreign-worktree disclosure. The reviewed
  bytes are unchanged at HEAD (`git diff 9cd47507 HEAD -- corpus/fixtures/` is
  empty), so this gate stands on `9cd47507` as dispatched.
- Blockers: none. Nothing committed; unrelated lanes' untracked `corpus/live/`
  artefacts untouched.
