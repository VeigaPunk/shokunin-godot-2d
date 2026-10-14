# Round 65 scribe — forged-REJECTION dual lesson entry + LOG draft (host: devin)

Report+scratch seat. No tracked edits, no commit/push/merge, no delegation.
Like r64 this seat **ran its own mechanism experiments** (the brief requires
an independent derivation): scratch harness at `corpus/live/r65-scribe/` —
`drive_errforge.py` (sha256 `5a673765…`), `proj/` (two-file fixture copy +
five scribe-owned arms), `raw/` (160 per-run captures),
`errforge-verdicts.json` (sha256 `89037950…`), `observations.md` (exact
commands + tables), `run-matrix.stdout`. Nothing outside
`corpus/live/r65-scribe/` and this report was written by me.

**Verdict on the declared claim — CONFIRMED, and sharpened in two places the
claim itself left open.** The falsifiable claim ("a reparenting-gated
descendant emitting an un-allowlisted `ERROR:`-class marker post-parent-death
converts a genuine exit-0 + signature-present record into a FAIL — the
rejection axis is as origin-blind as the signature axis; CASES-visible fields
identical to a genuine child-emitted error modulo r63-style provenance")
holds deterministically on this host: **every** forged-error arm flipped the
clean record to FAIL (syn release 15/15, quiet 10/10, stderr 5/5, hold 3/3,
withhold 5/5, script 5/5; godot release 8/8, quiet 3/3, stderr 3/3, hold
2/2, withhold 3/3, script 3/3 — 65/65 forged rejects, zero escapes) with
record fields identical to the genuine-error control. Two sharpenings
measured: (1) the "except withheld/ppid fields" concession is itself
removable — the `--errforge-quiet` arm drops every self-report line and
produces output **line-shape-identical** to the genuine-error control (pid
values normalized): zero in-record provenance, not just r63-style fields;
(2) one descendant write can forge **both axes at once** — the
`--errforge-withhold` arm lands forged signature + forged error in a single
post-death batch: `classify` False while the signature-only sibling
(`godot_sigforge_release`) still passes — the error axis overrides the
signature axis in verdict composition.

**While-live gate question, answered by measurement: the r64 signature gate
does NOT reject the forged-error arm — the post-death error write is
capture-visible yet verdict-invisible.** On `godot_errforge_release` gated
reps 5/5: the genuine signature was observed while-live (mark@~323–458 ms,
`alive_at_marker_obs=True`, inside the ~67 ms teardown margin) →
`gated_signature_accepted=True`, while the same captured bytes classify
**False** — the mirror-image divergence of r64 (gate accepts what the
classifier rejects). The forged error bytes ARE observed by the gate's read
loop — `err_obs@~427–561 ms, alive_at_error_obs=False, err−death ≈
+33–35 ms` — but its verdict predicate is signature-scoped and ignores
them. The measured asymmetry: on the accept axis the gate's remedy rejects
post-death writes; on the reject axis the analogous remedy would EXCLUDE
post-death bytes from the error scan — an error-liveness-aware read does
carry the discriminating datum (forged +33–35 ms post-death vs genuine
self-error −67 ms while-live) but the built gate never evaluates it. The
live-window blind side is symmetric (`syn_pre_error` 5/5: error observed
while-live → indistinguishable from genuine even observationally).

**State at finalize** (`git status` re-read ~02:50Z): HEAD `61ec1c0` (r64
adjudication). Author's tracked diff **landed uncommitted** —
`descendant_pipe_probe.gd` **+35** + `run_battery.py` **+431/−0**:
`--spawn-errforge-release`/`--spawn-errforge-hold`/`--emit-errforge` arms +
meta `probe_descendant_error_spoof` (bounded-Popen records + dual-marker
gated read + split-stream capture + `stripped_classification`
counterfactual, ~22 discriminations). The four extracted functions'
segment sha256 are HEAD↔worktree identical (`run_process 88728b23`,
`classify_process 749fa060`, `classify_streams a886968f`,
`classify_audio_process 3a6bc0e8` — additive only, classifiers untouched).
Settled sibling receipts: reviewer fresh seven-flag **97/97**
(`corpus/live/r65-reviewer/runs/20261014T022426865258Z/verdicts.json`),
baseline frozen-archive seven-flag **97/97**
(`corpus/live/r65-baseline/runs/20261014T022523005280Z/verdicts.json`).
Settled reports: `r65-{baseline,reviewer}.md`. Author post-diff battery IN
PROGRESS (run dir `corpus/live/r65-author/runs/20261014T023015140150Z`, no
verdicts.json at finalize) — author receipt, discrimination truth values,
scout/critic/boundary/simplifier reports all `[pending]`; post-diff
prior-row field-stability is `[pending non-author replay]`.

## Baseline + mechanism read (measured by me, scratch)

- `corpus/fixtures/run_battery.py` extraction sha256
  `66a18a0056aedbd6c99ed8637ed30d03a3404556ab49d05826e8c63f4fe1f07d` (pre-
  landing worktree file — byte-identical to the r64-verified blob; the
  author's +431 diff changed no extracted byte). `run_process` (:149–158)
  single-shot `subprocess.run(capture_output=True)`; `classify_process`
  (:160–177) — its reject clauses are `unrelated_errors` (any line
  containing `ERROR:` outside the per-case allowlist), `"SCRIPT ERROR:" in
  output`, `"Parse Error:" in output`: **presence scans over merged
  captured bytes, origin-blind exactly like the signature clause the r63
  row pinned on the accept side.** Extracted verbatim via
  `ast.get_source_segment` into scratch; production code path.
- My gate replica: r64's `gated_signature_run` shape (Popen + selectors +
  `os.read`, `poll()` liveness at the marker-completing read, 3.0 s bound,
  ~1 ms `/proc` death monitor) extended with a second watcher timestamping
  the first `ERROR:`/`SCRIPT ERROR:`-completing read and the child
  liveness at that instant.
- Arms: synthetic `/usr/bin/sh` children (fast; ppid-gated descendants using
  the fixture's own gate) + real headless Godot children on the scribe
  `proj/` copy. Error marker `ERROR: INJECTED_DIAGNOSTIC classification
  tripwire` — allowlisted nowhere.

### The flip, measured (naive = exact CASES verdict path)

| arm | n | record fields | verdict |
|---|---|---|---|
| godot/syn genuine, detach | 10 | exit0 · error=None · sig ✓ · 0 unrel | **True** — the shape flipped FROM |
| godot/syn self_error | 8 | exit0 · error=None · sig ✓ · 1 unrel | **False** — genuine error control |
| godot/syn errforge_release | 23 | exit0 · error=None · sig ✓ · 1 unrel | **False** ×23 — forged post-death error |
| godot/syn errforge_quiet | 13 | same, NO provenance lines | **False** ×13 — zero in-record tell |
| godot/syn errforge_hold | 5 | TIMEOUT · exit None · sig ✓ · 1 unrel | False; `classify_if_error_none` **False** |
| godot/syn errforge_stderr | 8 | exit0 · error on >&2 | **False** ×8 — stream-blind merge |
| godot/syn errforge_withhold | 8 | exit0 · forged sig + forged error | **False** — double-axis forgery |
| godot/syn script_errforge | 8 | `SCRIPT ERROR:`-class forged line | **False** — 2nd reject clause blind |
| godot/syn sigforge_release | 8 | exit0 · forged sig · 0 unrel | **True** — r63 forged-PASS stands |
| syn_pre_error | 5 | exit0 · live-window descendant error | False — blind side (write_ppid==child) |

`classify_if_error_none` is the sharp dual datum: on the r63 forged-
signature hold arm it was **True** (the forged signature needed the timeout
axis to reject); on every forged-error hold rep it is **False** — the
forged error rejects on its own axis even with the runner-error field
cleared. Provenance: `write_ppid=1573` (subreaper) ≠ godot_pid on every
gated forged write; hold arms kernel-corroborated alive-at-return
(`kernel_ppid == write_ppid`).

### CASES-field identity

`godot_errforge_release` ≡ `godot_self_error` on every field
`classify_process` reads (exit, error, signature presence, unrelated-error
line set, SCRIPT/Parse absence, verdict). Output differs only in
`spawned_pid=`/`write_ppid=` echo lines — the conceded r63-style fields.
`godot_errforge_quiet` removes even those: `output_shape` (pids normalized)
is line-for-line identical to `self_error` — `[banner, '', MARKER,
godot_pid=N, ERROR line]` — a forged FAIL with **zero** in-record
provenance.

### While-live interplay, measured

| arm | n | gated accept | alive@error-obs | err−death ms | inner classify |
|---|---|---|---|---|---|
| godot_errforge_release | 5 | **True ×5** | False ×5 | +33.4…+35.3 | False |
| godot_errforge_quiet | 3 | True ×3 | False | +34.0…+34.9 | False |
| godot_errforge_hold | 2 | True ×2 | False | +32.5…+34.3 | False |
| godot_errforge_withhold | 3 | **False** (forged sig gated) | False | +34.3…+35.0 | False |
| godot_self_error | 3 | True | **True** | ≈−67 | False |
| syn_errforge_release | 10 | True ×10 | False | +0.02…+0.39 | False |
| syn_pre_error | 5 | True | **True** | ≈−1250 | False |

The signature gate accepts the forged-error arm in every rep — the declared
"post-death write should be gate-invisible" is confirmed as
verdict-invisible (capture-visible: `dead_observed_at` precedes
`error_observed_at` on all forged reps).

### Converge/diverge vs sibling seats

- **Author** (landed diff, receipt `[pending]`): same mechanism, independent
  implementation — `--spawn-errforge-*` (child clean, descendant writes
  `ERROR: DESCENDANT_PIPE_ERRFORGE…` post-death) + `--emit-errforge`
  genuine control via `push_error` (engine stderr path — complementary to
  my stdout `print` control and `>&2` forged arm). Their meta adds what I
  did not: `stripped_classification` counterfactual (remove only `ERROR:`
  lines → classification restored — sole-cause isolation), split-stream
  record, `forged_vs_genuine_cases_fields_identical`, and dual-marker gated
  arms with `dead_observed_at <= error_observed_at` ordering. My extras:
  quiet zero-provenance shape, withhold double-forgery, `SCRIPT ERROR:`
  clause arm, live-window `pre_error` blind side, sub-ms syn timing,
  `classify_if_error_none` dual datum vs r63. No divergence expected on the
  claim's core; their receipt truth values `[pending]`.
- **Reviewer/baseline**: 97/97 + 97/97 pre-move receipts settled; baseline
  notes the move not yet landed at frozen HEAD — consistent.
- Scout/critic/boundary/simplifier: `[pending]`.

---

## Draft A — lesson entry (proposed slot `corpus/lessons/r65-forged-rejection.md`; final name/placement is parent's call)

````markdown
# R65 — forged-REJECTION dual: post-death descendant error writes trip the merged-capture error scan (Godot 4.7.2 headless)

Sources: `reports/round-65/r65-{scout,author,critic,reviewer,simplifier,
scribe,baseline,boundary}.md`; `corpus/fixtures/descendant_pipe_probe.gd`
errforge arms + `run_battery.py` meta `probe_descendant_error_spoof` (sha at
commit `[pending]`); author receipt `[pending]`; scribe independent
measurement `corpus/live/r65-scribe/errforge-verdicts.json` (sha256
`89037950…`, 160 runs, driver sha `5a673765…`, fixture sha `95ec2bb8…`);
`corpus/lessons/r63-signature-spoof-boundary.md` (the accept-axis boundary
this duals) and `corpus/lessons/r64-while-live-gate.md` (the gate whose
interplay this round documents).

verified-at: 2026-10-14, Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python
`3.14.7`, Linux `7.2.3-arch1-3`; scribe arms are `/usr/bin/sh` children plus
real headless Godot children on a scratch fixture copy, under
`ast.get_source_segment`-extracted `run_process`/`classify_process` (runner
sha `66a18a00…` = r64-verified blob); the tracked meta row drives the real
fixture arms on the battery's own scratch project.
recheck: (1) on any `run_process`/`classify_process` rewrite — merged
capture + presence scans are the whole mechanism; (2) if capture becomes
per-writer or the error scan gains provenance; (3) if the ppid gate is
stripped — post-death-ness is fixture-asserted except where kernel-corroborated;
(4) on Python/POSIX semantics change (`communicate` drain, reparenting,
`poll()` zombie behavior); (5) off this host — reparent target (subreaper
pid 1573 here), timing margins, scheduling.

## What the error clause actually is

`classify_process` rejects on three presence tests over the SAME merged
string the signature clause reads: `unrelated_errors` (any line containing
`ERROR:` not matching the per-case allowlist), `"SCRIPT ERROR:" in output`,
`"Parse Error:" in output`. Like the signature clause they assert "these
bytes appeared in captured output before pipe EOF" — never "the direct
child emitted them". The kernel does not label pipe bytes with provenance;
any process inheriting either captured fd can satisfy or trip every clause
at any time before the last holder releases it — including after the direct
child's death.

## Accept-axis vs reject-axis symmetry (the dual, measured)

| | accept axis (r63 pinned) | reject axis (r65 pinned) |
|---|---|---|
| clause | `signature in output` | `"ERROR:" in line` (unallowlisted), `"SCRIPT ERROR:"`, `"Parse Error:"` |
| origin-blind forgery | descendant writes signature post-death → **forged PASS** | descendant writes error post-death → **forged FAIL** |
| release shape | exit0 + sig → True | exit0 + sig + error → False |
| hold shape | TIMEOUT + sig → False via error axis only; `classify_if_error_none` **True** | TIMEOUT + sig + error → False via error AND timeout axes; `classify_if_error_none` **False** |
| record-level tell | none except withheld/ppid echoes | none except spawned/write_ppid echoes — **removable entirely (quiet arm: zero)** |
| blind side | live-window forge (r64 `pre_forge` 10/10) | live-window error forge (`pre_error` 5/5) |
| while-live gate | rejects forged sig, accepts genuine | **accepts the forged-error arm** — signature-scoped verdict never reads the error |

The verdict composition is AND-ed clauses: a post-death batch carrying
BOTH markers forges both axes in one write (`withhold` arm: forged sig +
forged error → False; the signature-only sibling → True). The error axis
dominates the signature axis — a single un-allowlisted `ERROR:` line
vetoes a present signature regardless of either line's origin.

## Flip mechanics, measured

- **release** (child clean: genuine signature while alive, exit 0;
  descendant ppid-gated echo post-death, pipes released): clean exit-0 +
  signature-present record FAILing only on the descendant's line —
  syn 15/15, quiet 10/10, godot 8/8. Sole-cause isolation convergent:
  author's `stripped_classification` (drop only `ERROR:` lines → PASS
  restored) `[pending author receipt]`; scribe's `classify_if_error_none`
  False.
- **hold** (same write, pipes held ~6 s): error lands inside the TIMEOUT
  record — rejects via BOTH axes; descendant alive at return,
  `kernel_ppid == write_ppid` corroborated.
- **quiet**: suppress `spawned_pid`/`write_ppid` echoes → output
  line-shape-identical to the genuine-error control — zero in-record
  provenance (sharper than the claim's conceded ppid fields).
- **stderr**: forged error on `>&2` flips identically — merge is
  stream-blind.
- **withhold**: forged signature + forged error in one post-death batch →
  False; gate rejects the forged signature while the classifier rejects on
  the error — each observation path sees only its own axis.
- **SCRIPT ERROR:**-class forged marker trips the second clause — the
  blindness is not `ERROR:`-prefix-specific.
- **pre_error** (no gate — descendant writes while child lives): False,
  `write_ppid == godot_pid` — in-record "genuine-looking" provenance on a
  descendant-authored line; live-window forgery is the blind side on this
  axis too.

## Which fields discriminate forged from genuine errors

On a CASES verdict record: **none** — forged and genuine error records
agree on `actual_exit`, `error`, `signature_observed`, the `ERROR:` line
set, verdict; and (quiet arm) can agree line-for-line on `output` modulo
pid values. Attribution lives only at the meta/observation layer:
`write_ppid != godot_pid` + kernel `/proc` corroboration (hold arms),
the child's self-declared banner, `timed_out`/`child_exit_at_timeout`,
`spawned_pid`, and — reader-generated — `dead_observed_at <=
error_observed_at` / `child_alive_at_error_observation` (+33–35 ms forged
vs −67 ms genuine on this fixture; ~+0.02–0.4 ms sh arms, ±~1 ms monitor
quantization).

## While-live interplay — measured answer

The r64 signature gate **accepts** the forged-error arm in every measured
rep (godot release 5/5 + quiet 3/3 + hold 2/2, syn release 10/10 + quiet
5/5 + hold 2/2): the genuine signature is observed while-live inside the
~67 ms Godot teardown margin, so `gated_signature_accepted=True` while the
same bytes classify False — the mirror-image divergence of r64. The forged
error IS captured by the gate's read (observed post-death, `alive_at_error_
obs=False`) but is verdict-invisible: the gate's predicate evaluates only
signature-marker liveness. An error-axis-aware read carries the split an
error gate would need (forged errors only post-death; genuine errors only
while-live — author's `gate_error_axis_timing_split` convergent
`[pending]`) — but the REMEDY DIRECTION INVERTS: signature gating rejects
post-death writes; error-axis protection would need to EXCLUDE post-death
bytes from the error scan (or weight them differently), since rejecting
them only restates the origin-blind verdict. Neither direction addresses
live-window forgery on either axis.

## Tracked surface (landed author diff, commit `[pending]`)

`descendant_pipe_probe.gd` +35: `--spawn-errforge-release` /
`--spawn-errforge-hold` (child runs clean — genuine signature + exit 0;
ppid-gated descendant echoes `ERROR: DESCENDANT_PIPE_ERRFORGE unrelated
injected diagnostic` + `write_ppid=` post-exit) + `--emit-errforge`
genuine control (child `push_error`s byte-identical marker pre-death —
engine stderr path). `run_battery.py` +431/−0: unconditional meta
`probe_descendant_error_spoof` — `errforge_run` bounded-Popen records
(release/hold/genuine), `gated_errforge_run` dual-marker reps (release×3,
genuine×2), `split_errforge_run` stream attribution, ~22 discriminations
incl. `release_flips_to_fail`, `release_counterfactual_passes_without_
error`, `forged_vs_genuine_cases_fields_identical`, `gate_does_not_
reject_forged_error_arm`, `gate_error_axis_timing_split`,
`hold_write_ppid_kernel_corroborated`. The arms are meta-driven, not CASES
tuples — an expected-FAIL record is inexpressible in the all-PASS battery
(r62 hold-arm precedent). `run_process`/`classify_process`/
`classify_streams`/`classify_audio_process` byte-identical; all 97 prior
rows byte-stable `[pending non-author replay]`.

## Boundary status after this round

The forgery surface is now symmetric and pinned on BOTH verdict axes:
post-death descendant bytes can manufacture a PASS (r63) or a FAIL (r65)
with equal ease, and the same pipe-inheritance mechanism carries both.
Reject-axis blindness is arguably the sharper operational hazard — a
forged PASS overstates health, a forged FAIL manufactures false negatives
that no signature check can clear. The r64 gate remains a signature-scoped
tool: it narrows the accept axis only. The documented stance stays "pin,
not fix": merged capture without per-writer channels makes every presence
clause origin-blind by construction. Practical rule, extended: a row whose
verdict could be swung by a stray `ERROR:` byte must not run a child that
may spawn pipe-inheriting descendants — the threat is now bidirectional.

## Critic falsifications survived / absorbed `[pending r65-critic report]`

Named surface: origin-blindness of the error path vs allowlist scoping;
post-`communicate()`-return write races; stderr-vs-stdout parity (measured
identical — scribe 8/8 stderr arms); double-write (genuine+forged error
interleave); allowlist boundary mutations; >64 KiB post-death writes.
`[pending]` — fill from the settled report.

## Not established (retained UNKNOWNs — do not soften)

- **Write-time provenance unobservable**: post-death-ness rides on the
  fixture's ppid gate + courtesy `write_ppid` echo — a stripped-gate or
  quiet mutant leaves nothing (measured: zero-provenance forged FAIL).
  The genuine-error control relies on `push_error` being child-authored —
  engine-side, same caveat as any fixture claim.
- **Stream origin**: merged capture cannot say which fd carried the error
  (author's split record documents stdout-descendant vs stderr-push_error;
  the verdict cannot see either).
- **Live-window forgery**: a descendant writing while the child lives is
  indistinguishable on BOTH axes (`pre_error` 5/5 False with
  `write_ppid==godot_pid`; mirrors r64's `pre_forge` blind side).
- **Ordering vs interleaving**: error bytes interleaved mid-signature-line,
  partial writes, >64 KiB descendant floods, multiple racing writers —
  boundary's axis, unmeasured here.
- **Timeout-arm composition**: error + forged signature + held pipes —
  which clause fires first is record-invisible (all reject; order of
  evaluation is `and`-short-circuit, exit code first — untested as a
  sequencing claim).
- **CASES-row framing**: the flip is proven at the record/classification
  level (exact `run_process`+`classify_process` path, author's bounded-
  Popen meta records); no literal CASES tuple carries the shape since the
  battery is all-PASS — same expressibility limit as r62's hold arm.
- **Wider surfaces**: `classify_streams` per-stream variant (signature-on-
  stdout + stderr error scan — would it still flip? the error scan there
  is per-stream; untested), `classify_audio_process` variant, exported
  builds, non-POSIX platforms, OS.execute paths, concurrent battery load.
````

Draft-A cautions: the "Tracked surface" section describes the
landed-but-uncommitted author diff (+466/−0) whose battery receipt and
discrimination truth values were still in progress at finalize — if the
parent corrects the diff at integration (r61/r63/r64 precedents incl. the
r64 verifier-caught runner omission) names and counts must be reconciled
before the lesson commits. Author/scout/critic/boundary/simplifier receipts
are `[pending]`.

---

## Draft B — LOG.md round-65 entry (draft; `[pending]` = fill from settled raw before commit)

```markdown
## Round 65 — devin host — depth: forged-REJECTION dual — post-death descendant error flips PASS→FAIL

- Declared (fleet brief): pin the forged-rejection dual (XConnector wave-4
  Arm 1) — a reparenting-gated descendant emitting an un-allowlisted
  `ERROR:`-class marker post-parent-death converts a genuine exit-0 +
  signature-present record into a FAIL; measure whether the rejection axis
  is as origin-blind as the signature axis; additive fixture arms + meta
  `probe_descendant_error_spoof`; r64 gate + 97 prior rows byte-stable;
  document while-live-gate interplay.
- Wave `shokunin-train-20261013-w5`: 8-seat devin leaf set
  `reports/round-65/r65-{scout,author,critic,reviewer,simplifier,scribe,
  baseline,boundary}.md`, disjoint scratch `corpus/live/r65-*/`, sole
  tracked writer = author.
- Settlement: baseline frozen `git archive HEAD` seven-flag **97/97**
  (`corpus/live/r65-baseline/runs/20261014T022523005280Z/verdicts.json`);
  reviewer fresh seven-flag **97/97** on HEAD `61ec1c0` +
  r64-committed-state audit `[pending detail]`. Author landed
  `descendant_pipe_probe.gd` +35 + `run_battery.py` **+431/−0** — meta
  `probe_descendant_error_spoof` + arms `[pending receipt: author
  seven-flag N/N + M discriminations]`.
- Measured (scribe, independent derivation): 160 runs — forged post-death
  `ERROR:` flips clean records 65/65 forged-arm reps (release/hold/quiet/
  stderr/withhold/script-class × sh+Godot); forged≡genuine on every
  classification-visible field; quiet arm zero-provenance; hold arms
  `classify_if_error_none`=False (dual of r63's True); withhold arm forges
  both axes in one batch; while-live signature gate ACCEPTS the
  forged-error arm every rep (capture-visible, verdict-invisible;
  +33–35 ms post-death vs −67 ms genuine margin).
- Non-author verifier `[pending]`; adjudication `[pending]`.
```

## Seat notes

- Commands/evidence: `corpus/live/r65-scribe/observations.md` (exact
  invocations), `run-matrix.stdout` (all 160 per-rep lines),
  `errforge-verdicts.json` (machine records incl. output lines, timing
  fields, kernel ppid corroboration), `raw/` per-run captures.
- Orphan hygiene: all parsed `spawned_pid` descendants SIGKILLed at return
  (bounded `sleep 6` self-exits otherwise); quiet arms spawn no lingering
  descendant by construction. Zero leaked descendants observed.
- The author's diff landed DURING my measurement; my extraction predates it
  on disk (sha `66a18a00` recorded in the verdicts payload) and the landed
  blob shares identical extracted-function bytes — the measurement is
  unaffected. Convergence checked against the diff itself, not their
  (still-running) receipt.
