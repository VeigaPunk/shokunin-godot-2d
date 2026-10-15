# R64 — while-live signature gate: observation-time child liveness discriminates post-death forged writes (Godot 4.7.2 headless)

Sources: `reports/round-64/r64-{scout,author,critic,reviewer,simplifier,
scribe,baseline,boundary}.md`; `run_battery.py` meta
`probe_while_live_signature_gate` (sha at commit `a32920b+5265da6`); author
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

## Tracked surface (landed author diff, commit `a32920b+5265da6`)

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
semantics only. Prior-96-row field-stability receipt `a32920b+5265da6`.

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

## Critic falsifications survived / absorbed `a32920b+5265da6`

Attack surface named in the axis-move: forged signature observable
pre-death through pipe buffering (impossible for these arms — measured;
write is ppid-gated post-death), liveness-timing nondeterminism (bounded —
genuine margin ~67 ms godot / ~0.7 ms sh; reader-lag false-rejection class
measured at 50 ms), primitive unsoundness (kill0/returncode measured
29/29 forged accepts — recorded, not softened). `a32920b+5265da6` — fill from
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
