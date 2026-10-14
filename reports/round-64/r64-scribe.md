# Round 64 scribe — while-live signature-gate lesson entry + LOG draft (host: devin)

Report+scratch seat. No tracked edits, no commit/push/merge, no delegation.
Unlike r63 this seat **did run its own mechanism experiments** (the brief
requires an independent derivation): a scratch gated-read harness at
`corpus/live/r64-scribe/` — `drive_whilelive.py` (sha256 `08739b5d…`),
`proj/` (two-file fixture copy), `raw/` (156 per-run captures),
`whilelive-verdicts.json` (sha256 `5ca64425…`), `observations.md` (exact
commands + tables), `run-matrix.stdout`. Nothing outside
`corpus/live/r64-scribe/` and this report was written by me.

**Verdict on the declared claim — CONFIRMED, with two measured falsification
surfaces that bound it.** The falsifiable claim ("a while-live marker read
discriminates forged post-death signatures from genuine child signatures")
holds deterministically on this host **iff the liveness primitive sees
through zombies**: under `poll()`/`waitid-WNOWAIT`/`proc-state` (incl. a
forced-lag variant) the forged post-death write was observed while-live
**0/44** across my reps (author 0/4, scout 0/8 live-observed — convergent)
while genuine markers were accepted **47/47** unlagged (author 4/4; +3/3
under a 50 ms lag on the Godot arm). Falsified exactly where predicted as
the alternative failure class — not buffering, but the **zombie-blind
primitive**: `os.kill(pid,0)` + stale `proc.returncode is None` accepted
the forged marker **29/29** combined (scout independently: kill0 5/5). A
naive "child-alive check" that signals a zombie does not discriminate at
all — the claim is only as sound as the primitive.

**State at finalize** (`git status` re-read ~01:40Z): HEAD `a7e0cb1` (r63
adjudication). Author's tracked diff **landed uncommitted** —
`corpus/fixtures/run_battery.py` **+224/−0**: unconditional meta
`probe_while_live_signature_gate` (`poll_gated_bounded_popen_signature_read`,
3.0 s bound, 5 ms poll tick, 8 arms, 12 discriminations). Author post-diff
seven-flag receipt **97/97** (`corpus/live/r64-author/runs/
20261014T013826495191Z/verdicts.json`, `battery.stdout` ends `PASS
battery`). Settled sibling receipts: baseline frozen-archive seven-flag
**96/96** (`corpus/live/r64-baseline/runs/20261014T013523271164Z/
verdicts.json`), reviewer fresh seven-flag **96/96** on HEAD `a7e0cb1` plus
r63 meta re-audit AGREE (sha `2c8392ea…`), scout primitive measurements.
Settled reports: `r64-{baseline,reviewer,scout}.md`. Critic/simplifier/
boundary reports + the work commit are `[pending]`; this wave's roster
fields no dedicated verifier seat — 96-prior-row field-stability on the
post-diff tree is `[pending non-author replay]` (author's own stdout shows
all prior rows PASS; not a field diff).

## Baseline + mechanism read (measured by me, scratch)

- `corpus/fixtures/run_battery.py` sha256
  `fb7cab2bb0364bef802cd3ed67892510377b8c45024daa378ca632129d96d7c2` (HEAD
  copy, pre-r64-diff — matches scout/baseline). `run_process` (:149–158) is
  single-shot `subprocess.run(capture_output=True)`; `classify_process`
  (:160–177) signature clause is substring presence over merged
  `stdout+stderr` — origin-blind (the r63 pinned boundary). I extracted
  both verbatim via `ast.get_source_segment` into scratch; production code
  path, no transcription.
- Gate under test (mine, `drive_whilelive.py`): `Popen` + `selectors` +
  `os.read`; on the chunk that first completes
  `DESCENDANT_PIPE_PROBE: expected signature` in the arrival buffer,
  evaluate one of six liveness primitives (`poll`, `poll_delay50`,
  `waitid`, `procstat`, `kill0`, `returncode`); a daemon thread samples
  `/proc/<pid>/stat` ~1 ms to timestamp the real death WITHOUT reaping.
- Arms: synthetic `/usr/bin/sh` children with the fixture's own ppid-flip
  descendant gate (write provably post-exit; real marker string +
  `write_ppid=` echo) plus the **real fixture** on a two-file project copy:
  default, `--spawn-detach`, `--spawn-forge-release`, `--spawn-forge-hold`;
  `syn_pre_forge` = live-child forgery control (write_ppid == child pid);
  bound 3.0 s. 156 gated runs total.

### Measured discrimination matrix (condensed; full table in `observations.md`)

| arm | gate | n | gated accept | naive classify | obs−death ms (med) |
|---|---|---|---|---|---|
| syn_genuine_fast | poll | 30 | 30 | 30 | −0.69 |
| syn_genuine_fast | poll_delay50 | 10 | **0** | 10 | −0.55 (dead at eval) |
| syn_genuine_slow | poll | 10 | 10 | 10 | −401 |
| syn_release | poll / waitid / procstat | 15/5/5 | **0** | 15/5/5 | +0.05…+0.10 |
| syn_release | kill0 / returncode | 10/10 | **20** | 20 | +0.08/+0.18 |
| syn_release | poll_delay50 | 5 | **0** | 5 | +0.50 |
| syn_hold (3 s bound) | poll / kill0 | 3/2 | **0 / 2** | 0 (t/o) | +0.25/+0.51 |
| syn_pre_forge (live forgery) | poll | 10 | **10** | 10 | −1250 |
| godot_genuine | poll / kill0 / poll_delay50 | 5/3/3 | 11 | 11 | −67…−70 |
| godot_detach | poll | 2 | 2 | 2 | −69.5 |
| godot_release | poll / procstat / poll_delay50 | 5/2/2 | **0** | 9 | +31…+37 |
| godot_release | kill0 / returncode | 3/3 | **6** | 6 | +33 |
| godot_hold | poll / kill0 | 2/1 | **0 / 1** | 0 (t/o) | +33.8/+33.6 |

`classify_if_error_none` is True on **every** forged record incl. hold arms
— the signature clause still accepts the bytes; only the gate (and timeout
on hold) rejects.

### The three races, measured

1. **Buffering race — cannot falsify.** Pipe bytes cannot precede their
   write; the forged write is reparenting-gated post-death, so every forged
   observation is strictly post-death (measured +0.01…+37 ms, margin set by
   descendant spawn + first `/proc` poll, never a pre-death observation in
   73 forged reps; min `obs−death` +0.010 ms this run — the ±~1 ms monitor
   quantization bound). Reader-side buffering/lag only pushes observation
   later → strictly more rejection margin, never less (the 50 ms-lag arm
   kept rejecting forged 7/7).
2. **Zombie race — real, and it is the gate primitive, not the data.** An
   unreaped child satisfies `os.kill(pid,0)` and reads `proc.returncode is
   None` for its **entire** corpse window (measured linger: ~33 ms release
   / ~2.4–3.0 s hold / ~0.3 ms syn — always covering the forged-observation
   instant). `poll()`/`waitid(WNOWAIT)`/`/proc`-state see through it;
   `kill0`/`returncode` accept forged deterministically.
3. **Genuine-side margin race — the gate's fragile direction.** A marker
   written while-alive but *evaluated* post-death is false-rejected:
   `syn_genuine_fast` 30/30 accept unlagged → **0/10** under a forced 50 ms
   eval lag; the Godot default arm survives the same lag 3/3 because its
   post-print teardown margin is ~66–70 ms (sh `echo;exit` margin ~0.7 ms).
   Genuine acceptance is a timing margin, forgery rejection is a causality
   guarantee.

Blind side by construction: `syn_pre_forge` (descendant writes at +0.25 s
while child sleeps 1.5 s; `write_ppid` == child pid in-record) accepted
**10/10** — the gate detects *post-death origin*, not *descendant
authorship*. Consistent with the author's `bounded_claim` scope ("a
pre-death-scheduled or faster-racing forge is out of scope") — now measured.

### Converge/diverge vs sibling seats

- **Author** (`probe_while_live_signature_gate` receipt): genuine×3 +
  detach gated True (alive at obs AND after read); forge_release×3 gated
  False with `dead_observed_at` (0.478–0.522) < `marker_observed_at`
  (0.509–0.553) — the reader-side ordering field the r63 record lacked;
  forge_hold gated False + timeout; `write_ppid=1573` kernel-corroborated
  on hold; all 12 discriminations true → PASS. My margins agree (forged
  gap ≈32 ms, genuine margin ≈67 ms).
- **Scout**: same load-bearing primitive conclusion (poll sound; kill0
  5/5 false-accept; `/proc`-existence unsound; `/proc`-state redundant);
  measured pipe-buffered bytes surviving writer death; ~65 ms margin;
  ~22 ms ordering; notes `poll()` and the `/proc` truth sample are two
  syscalls (µs inter-death race on 5/20 fast-sh genuine reps — keep both
  fields). My `waitid`/`procstat`/`returncode`/`poll_delay50`/`pre_forge`
  columns converge and extend.
- No divergence on the claim's core. Extensions I add: the two unsound
  primitives quantified (29/29 forged accepts), the reader-lag
  false-rejection class (10/10 at 50 ms on fast children), the live-forgery
  blind side quantified (10/10 accepts), zombie-linger windows.

---

## Draft A — lesson entry (proposed slot `corpus/lessons/r64-while-live-gate.md`; final name/placement is parent's call)

````markdown
# R64 — while-live signature gate: observation-time child liveness discriminates post-death forged writes (Godot 4.7.2 headless)

Sources: `reports/round-64/r64-{scout,author,critic,reviewer,simplifier,
scribe,baseline,boundary}.md`; `run_battery.py` meta
`probe_while_live_signature_gate` (sha at commit `[pending]`); author
receipt `corpus/live/r64-author/runs/20261014T013826495191Z/verdicts.json`
(97/97); scribe independent measurement
`corpus/live/r64-scribe/whilelive-verdicts.json` (sha256 `5ca64425…`, 156
gated runs, driver sha `08739b5d…`); scout primitive measurements +
insertion map `reports/round-64/r64-scout.md`;
`corpus/lessons/r63-signature-spoof-boundary.md` (the boundary this gate
reads, not fixes).

verified-at: 2026-10-14, Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python
`3.14.7`, Linux `7.2.3-arch1-3`; scribe/scout arms are `/usr/bin/sh`
children under `ast.get_source_segment`-extracted
`run_process`/`classify_process` plus real headless Godot children on the
unmodified `descendant_pipe_probe.gd` arms; the tracked meta row drives the
real fixture on the battery's own scratch project.
recheck: (1) on any `run_process`/`classify_process` rewrite — the gate is
a parallel observation path, not a clause; (2) if the liveness primitive
changes — `kill(pid,0)`/stale `returncode` are measured unsound; (3) if
the fixture's post-print teardown margin shrinks below reader lag, the
genuine arm starts false-rejecting (~67 ms measured); (4) on Python/POSIX
semantics change (`poll`/`waitid`/`/proc` states); (5) off this host —
reparent target (subreaper pid 1573 here), margins, scheduling.

## What the while-live gate actually is

A bounded `Popen` + `selectors` + `os.read` loop: the expected marker is
accepted only if observed while the direct child is alive — liveness
evaluated at the instant the marker-completing bytes are read. It asserts
"these bytes were *observed* before the child's observed death" — never
"these bytes were *written* by the child". The tracked implementation
(`probe_while_live_signature_gate`) polls each select tick (5 ms), samples
`alive_before` pre-read and `child_alive_after_marker_read` post-read, and
records `dead_observed_at` — landing `first_dead < marker_read` ordering
evidence **in-record, reader-side**, which the r63 row could only
fixture-assert via `write_ppid`. It is additive: `run_process`/
`classify_process`/`classify_streams`/`classify_audio_process` untouched;
the r63 pinned `descendant_pipe_forged_signature_release` CASES row stays
byte-stable — the gate reads the same forgery under a new path, it does
not close the accepting boundary.

## Discrimination, measured

Across three independent harnesses (author meta 8 arms; scribe 156 gated
runs; scout ~20 primitive reps):

| arm | gate | n | gated accept | naive classify | obs−death |
|---|---|---|---|---|---|
| genuine (godot default) | poll | 3+5 | all True | True | marker ~67 ms BEFORE death |
| genuine detach | poll | 1+2 | all True | True | ~69 ms before |
| forge_release | poll/procstat/delayed-poll | 3+9 | **0** | True | marker ~+31…+37 ms AFTER death |
| forge_hold (3 s bound) | poll | 1+2 | **0** | False (timeout) | ~+33 ms after |
| forge_release/hold | kill0/returncode | 6+1 godot (+22 syn) | **all True — forged accepted** | — | zombie window |
| genuine fast sh | poll | 30 | 30 | 30 | ~0.7 ms before |
| genuine fast sh | poll + 50 ms lag | 10 | **0 — false reject** | 10 | dead by eval |
| live-child forge (no ppid gate) | poll | 10 | **all True — blind side** | 10 | ~1.25 s before |

Headline (all three seats convergent): under a reaping or kernel-state
liveness primitive the reparenting-gated forged write can never be
observed while-live — the marker-completing read happens strictly after a
death `poll()` already reports; genuine signatures pass inside the
fixture's post-print teardown margin. `inner_classification` True on every
forged release record: same captured bytes, classifier accepts, gate
rejects — the exact divergence the pinned r63 boundary predicts.

## Buffering and zombie findings

- **Buffering cannot falsify the forged side.** Pipe bytes cannot precede
  their write; the arm's ppid gate makes the write provably post-death, so
  no read can observe forged bytes while the child lives — the claim's
  "forged signature observable pre-death through pipe buffering" failure
  mode is impossible for these arms. Reader lag only delays observation.
- **The zombie race is real — in the liveness primitive, not the data.**
  An unreaped child satisfies `os.kill(pid,0)` and `proc.returncode is
  None` for its whole corpse window (measured ~33 ms release, ~2.4–3.0 s
  hold, always covering the forged-observation instant): zombie-blind
  gates accepted the forged marker 29/29 (scribe) + 5/5 (scout).
  `poll()`/`waitid(WEXITED|WNOHANG|WNOWAIT)`/`/proc/<pid>/stat` state
  (`Z`/`X` = dead) are sound; `poll()` additionally reaps and is
  pid-reuse-safe (scout).
- **Genuine-side margin race.** A marker written while-alive but evaluated
  post-death false-rejects: fast `echo;exit` children (write→death ~0.7 ms)
  flipped 30/30-accept to 0/10 under a forced 50 ms reader lag; the Godot
  fixture's ~67 ms margin survived the same lag 3/3. The gate trades a
  bounded genuine-rejection race for deterministic forgery rejection —
  genuine arms need post-marker lifetime ≥ reader lag; on this fixture the
  margin is a property of Godot's shutdown path, not the harness.
- **Ordering evidence is reader-generated.** `dead_observed_at <
  marker_observed_at` lands in-record (~22–33 ms on forged reps), narrowing
  the r63 critic's stripped-gate slip class: a mutant whose write lands
  after observed death is caught without trusting fixture semantics.

## Tracked surface (landed author diff, commit `[pending]`)

`run_battery.py` **+224/−0**: unconditional meta
`probe_while_live_signature_gate` after the r63 spoof meta — helper
`gated_signature_run(case, flags)` + 8 arms (genuine×3, detach, forge
release×3, forge hold×1) + 12 discriminations, all required and all
observed true in the author receipt (97/97 total, +1 meta row): genuine
accepted while-live, genuine never observed post-death, detach control,
forge release/hold marker captured strictly post-death, gate rejects what
the classifier accepts, withheld-banner + `write_ppid != godot_pid`
provenance, hold kernel corroboration + orphan reaping, headline
`gate_discriminates_forged_from_genuine`. `bounded_claim` scopes the row:
discriminates forged post-death writes from genuine writes **on this
fixture**; not authorship proof in general; Linux headless 4.7.2 POSIX
semantics only. Prior-96-row field-stability receipt `[pending non-author
replay]`.

## Boundary status after this round

The r63 forgery-accepting boundary is **unchanged and still accepting** —
signature presence over merged captured output remains origin-blind and
the pinned CASES row still PASSes on a descendant-authored signature.
What r64 adds is a **documented discriminating read**, not a closure: a
poll()-gated observation path rejects the same forged bytes while
accepting genuine ones on this fixture. Practical rule, sharpened: a
signature assertion on a child that may spawn pipe-inheriting descendants
can now be paired with a while-live read to reject post-death writes —
but only *post-death* writes; live-child forgery still needs per-writer
channels the runner does not have, and the gate is sound only under
zombie-aware primitives (`poll()`/`waitid`/`/proc`-state — never
`kill(pid,0)` or a cached `returncode`).

## Critic falsifications survived / absorbed `[pending r64-critic report]`

Attack surface named in the axis-move: forged signature observable
pre-death through pipe buffering (impossible for these arms — measured;
write is ppid-gated post-death), liveness-timing nondeterminism (bounded —
genuine margin ~67 ms godot / ~0.7 ms sh; reader-lag false-rejection class
measured at 50 ms), primitive unsoundness (kill0/returncode measured
29/29 forged accepts — recorded, not softened). `[pending]` — fill from
the settled critic report.

## Not established (retained UNKNOWNs — do not soften)

- **Write-time provenance is unobservable reader-side**: the gate sees
  observation-time liveness only; pipe-buffered bytes survive writer death
  (scout measured), so "written while alive" is never provable from the
  read side. A pre-death-scheduled or faster-racing forge is out of scope
  by construction (scribe `syn_pre_forge` 10/10 accepted — measured blind
  side).
- **Genuine margin is fixture-bound**: ~67 ms here (Godot teardown);
  fixtures with shorter post-marker lifetimes can false-reject under
  reader lag ≥ margin. The knee between 0.7 ms and 50 ms is unmeasured;
  behavior under concurrent battery load untested (all runs serial).
- **µs inter-syscall race**: `poll()` and the `/proc` truth sample are two
  syscalls — scout saw 5/20 fast-sh genuine reps where the gate read alive
  while the next sample read Z; scribe's ~1 ms monitor quantization gives
  occasional ±displayed-zero obs−death on sub-ms margins. Neither flips a
  verdict on this fixture; both bound the timing fields' precision.
- **Stripped/mutated ppid gate**: the post-death ordering evidence is
  reader-generated, but a mutant forging *while the child lives* is
  indistinguishable from genuine — same live-forgery scope limit.
- **Wider surfaces**: stderr-carried markers under the gate (all 156
  scribe markers observed on stdout; mechanism is stream-agnostic by
  construction, unmeasured), >64 KiB descendant writes, exported builds,
  non-POSIX platforms, per-stream (`classify_streams`) gated variants,
  primitives beyond the six measured (signalfd, subreaper configs),
  >1 descendant writers racing the same fd.
````

Draft-A cautions: the "Tracked surface" section describes the
landed-but-uncommitted author diff (+224/−0) and its 97/97 receipt — if the
parent corrects the diff at integration (r61 `crash_meta_ok` / r63
kernel-corroboration precedents) the row name and discrimination list must
be reconciled before the lesson commits. Critic/simplifier/boundary
results are pending.

---

## Draft B — LOG.md round-64 entry (draft; `[pending]` = fill from settled raw before commit)

```markdown
## Round 64 — devin host — depth: while-live signature-gate discrimination of post-death forged writes

- Declared (fleet brief): test the falsifiable claim that a marker read
  gated on child liveness discriminates the r63-pinned forged post-death
  signature from a genuine child signature — bounded-Popen meta arm driving
  the EXISTING `--spawn-forge-release`/`--spawn-forge-hold` fixture arms;
  predicted: forged lands post-death → gated read rejects/never observes,
  genuine default arm still passes. Additive only; r63 pinned row
  byte-stable; 96 prior rows field-stable.
- Wave `shokunin-train-20261013-w4`: 8-seat devin leaf set
  `reports/round-64/r64-{scout,author,critic,reviewer,simplifier,scribe,
  baseline,boundary}.md`, disjoint scratch `corpus/live/r64-*/`, sole
  tracked writer = author.
- Settlement: baseline frozen `git archive HEAD` seven-flag **96/96**
  (`corpus/live/r64-baseline/runs/20261014T013523271164Z/verdicts.json`);
  reviewer fresh seven-flag **96/96** on HEAD `a7e0cb1` + r63 meta re-audit
  AGREE. Author landed `run_battery.py` **+224/−0** — unconditional meta
  `probe_while_live_signature_gate` (poll-gated bounded read, 3.0 s bound,
  5 ms tick, 8 arms, 12 discriminations): genuine+detach observed
  while-live, forged release/hold markers captured strictly post-death
  (`dead_observed_at` < `marker_observed_at`), `inner_classification` True
  on forged release — classifier accepts what the gate rejects. Author
  seven-flag **97/97** (`corpus/live/r64-author/runs/
  20261014T013826495191Z/verdicts.json`); 96-prior-row field-stability
  `[pending non-author replay]` — no dedicated verifier seat this wave.
- Seat evidence: scout (insertion map — crash-exit selector loop pattern;
  primitive table: poll sound, kill0 5/5 false-accept zombie-blind, /proc
  state redundant; ~65 ms margin, ~22 ms ordering; write-time provenance
  unobservable). Scribe (independent 156-run gated matrix, six liveness
  primitives + ~1 ms non-reaping death monitor: 0/44 forged while-live and
  47/47 genuine while-live under unlagged sound gates; kill0+returncode 29/29 forged
  accepts; 50 ms reader lag false-rejects fast genuine children 10/10;
  live-child forgery accepted 10/10 — the gate detects post-death origin,
  not authorship; zombie-linger windows measured ~0.02 ms–3.0 s).
- Per-axis verdict: `[pending parent/adjudicator]` — declared target depth:
  post-death-forgery discrimination now a tracked, reader-side
  discrimination (gate + in-record death ordering), the r63 accepting
  boundary documented not closed; coverage improved locally (96→97 rows);
  calibration unchanged expected. Retained UNKNOWNs: live-child forgery
  blind side, genuine margin fixture-bound (~67 ms), stripped-gate mutants,
  stderr-carried markers, exported/non-POSIX. Work commit `[pending]` then
  report-last; no push/merge.
```

Draft-B cautions: settlement bullet states only observed receipts; the
field-stability claim is unevidenced this wave (no verifier seat) and stays
a `[pending]` the parent must fill or scope down.

---

## Scribe evidence checklist for the tracked move (status at report time)

- [x] Baseline read by me: runner sha `fb7cab2b…` (== committed `a7e0cb1`
  work `de78edb`), 96 rows at HEAD, env Godot 4.7.2 / Python 3.14.7 /
  Linux 7.2.3-arch1-3.
- [x] Own gated-read harness run: 156 runs, verdicts sha `5ca64425…`;
  0/44 forged while-live + 47/47 genuine while-live under unlagged sound gates;
  29/29 forged accepts under zombie-blind gates; per-run raw captures in
  `raw/`; zero leaked descendants (post-run `pgrep` clean of my children).
- [x] Real fixture arms driven unmodified (proj two-file copy): default,
  detach, forge-release, forge-hold — gate + naive verdicts on identical
  captured bytes (`classify_if_error_none` True on all forged records).
- [x] Landed author diff read (+224/−0): meta
  `probe_while_live_signature_gate`, 12 discriminations; author receipt
  97/97 with arm timings matching my margins (forged +~32 ms, genuine
  −~67 ms).
- [x] Sibling convergence re-read: scout primitive table + margin/ordering
  agree with mine; reviewer 96/96 + r63 audit AGREE; baseline frozen 96/96.
- [ ] Author work commit hash — uncommitted at report time.
- [ ] Prior-96-row field-stability vs a non-author post-diff replay — no
  verifier seat this wave.
- [ ] Critic falsification results (pre-death-observability, timing
  nondeterminism, primitive soundness — my three surfaces measured).
- [ ] Simplifier minimal-diff verdict; boundary depth/other-surface results.
- [ ] Parent integration corrections + final adjudication.

## Bounded scope of this report

Drafts + scratch measurements only — not a PASS, not a verdict, not an
admission. Every classification constant quoted is my own receipt (paths +
sha256 in `observations.md`), a sibling in-flight receipt, or committed
history; the lesson draft's "tracked surface" describes the
landed-but-uncommitted author diff and must be reconciled with whatever
actually commits. No commit, no tracked-file write, no sibling-file write.
