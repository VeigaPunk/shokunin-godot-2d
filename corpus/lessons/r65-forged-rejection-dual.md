
# R65 — forged-REJECTION dual: post-death descendant error writes trip the merged-capture error scan (Godot 4.7.2 headless)

Sources: `reports/round-65/r65-{scout,author,critic,reviewer,simplifier,
scribe,baseline,boundary}.md`; `corpus/fixtures/descendant_pipe_probe.gd`
errforge arms + `run_battery.py` meta `probe_descendant_error_spoof` (sha at
commit `414eb8e`); author receipt `20261014T023015140150Z`; scribe independent
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
  restored) (author receipt); scribe's `classify_if_error_none`
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
while-live — author's `gate_error_axis_timing_split` convergent) — but the REMEDY DIRECTION INVERTS: signature gating rejects
post-death writes; error-axis protection would need to EXCLUDE post-death
bytes from the error scan (or weight them differently), since rejecting
them only restates the origin-blind verdict. Neither direction addresses
live-window forgery on either axis.

## Tracked surface (landed author diff, commit `414eb8e`)

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
rows byte-stable (non-author replay 87/87, 0 mismatches — r65-verifier).

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

## Critic falsifications survived / absorbed

All 28→29 discriminations independently reproduced. Absorbed bounds:
- **CE-1**: the operative precondition is capture-before-pipe-EOF, not
  death ordering — a detached (unheld-pipe) errforge emits the identical
  post-orphan marker yet the record stays clean PASS.
- **CE-2**: the merged stdout+stderr concat is not line-faithful —
  a splice can fabricate a reject-triggering ERROR: line present in
  neither stream; a newline-split marker escapes.
- stderr forge flips identically; double-write dedupes; allowlisted echo
  accepts post-death; escape set + extra reject clauses mapped; race
  margin ≈2.55 s to the 3.0 s bound.

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
