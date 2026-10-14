# Round 63 — critic: adversarial falsification of the forged-signature boundary

## Scope and method

LEAF critic seat, scratch-only + this report. Wrote only
`.shokunin/game-dev-2d/corpus/live/r63-critic/` and this file; no tracked
fixture, runner, CASES row, lesson, LOG, or SCORECARD mutation; no subagent
dispatch; no git mutation.

Method: `corpus/live/r63-critic/drive_spoof_attacks.py` `ast.get_source_segment`-
extracts `run_process`, `classify_process`, and `classify_streams` **verbatim**
from the worktree `corpus/fixtures/run_battery.py` (the landed r63 diff,
uncommitted at probe time: `run_battery.py` +149/−0, `descendant_pipe_probe.gd`
+31/−1) and execs them — every classification below is the production code
path. Meta arms run through a verbatim replica of the landed
`probe_descendant_signature_spoof` bounded-Popen block (same field names:
`timed_out`, `child_exit_at_timeout`, `write_ppid`, `inner_classification`).
The author's eight landed discriminations are re-evaluated verbatim against
each mutant's measured record. Mutant fixture
`proj/sig_spoof_probe.gd` re-derives the author's reparenting gate
independently; `proj/descendant_pipe_probe.gd` is a scratch copy of the
tracked worktree fixture for author-arm reproduction.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Linux
`7.2.3-arch1-3 x86_64`, Python `3.14.7`, `/usr/bin/sh` → `bash`. Classifier
functions `run_process`/`classify_process`/`classify_streams`/
`classify_audio_process` are byte+AST identical HEAD↔worktree — the diff is
additive outside classifier code.

## Landed work under attack

- CASES row `descendant_pipe_forged_signature_release`
  (`--spawn-forge-release`, expected 0, signature
  `DESCENDANT_PIPE_PROBE: expected signature`): child withholds the marker,
  descendant writes it post-reparenting and releases — the tracked
  known-accepting forgery row.
- Meta `probe_descendant_signature_spoof`: drives `--spawn-forge-hold` under
  one bounded Popen (3.0s) + reads the forged CASES row; eight
  discriminations.
- Dispatched claim: the forged record is "distinguishable from a genuine
  child signature ONLY via the child-death/timeout evidence fields
  (child_exit_at_timeout, timed_out), never via signature presence alone".

## Attack (a) — is there a hidden liveness guard? FALSIFICATION FAILED

`run_process` is `subprocess.run(capture_output=True)` + the verbatim
classifier; no liveness check exists anywhere on the path. Measured:

| arm | exit | error | elapsed | marker | classify |
|---|---|---|---|---|---|
| auth_forge_release_b8 (author's arm, 8s bound) | 0 | None | 0.405s | True | **True** |
| auth_forge_release_b3 (same arm, 3.0s bound) | 0 | None | 0.456s | True | **True** |
| mut_forge_midhold_b8 (write post-death, hold 1.2s more) | 0 | None | 1.600s | True | **True** |
| auth_hold_as_cases_b8 (`--spawn-forge-hold` under the 8s CASES bound) | 0 | None | 6.435s | True | **True** |
| mut_forge_neg_exit_b8 (child quit(2); descendant forges an allowlisted `ERROR:` signature post-death) | 2 | None | 0.442s | True | **True** |

The release arm does classify True — the claim's core is **confirmed, not
falsified**. Two widenings beyond the claim's wording: the forgery works for
an arbitrary `(expected_exit, signature, allowed_errors)` tuple (a forged
allowlisted `ERROR:` signature passes an expected-exit-2 row), and the hold
arm itself forges a clean PASS under the 8s CASES bound (release ~6.44s;
~1.5s margin — bound-relative, not a fixed shape).

## Attack (b) — which stream does the forgery need? Merged; stream-agnostic

`classify_process` judges `proc.stdout + proc.stderr` concatenated. A mutant
whose descendant writes the forged signature to **stderr only**
(`mut_forge_release_stderr_b8`, `mut_stderr_hold`) is captured and classified
**identically** (True on release; marker_observed True inside the TIMEOUT
record) — the merged record is even byte-identical in line set, since stderr
is appended after all stdout anyway. Split-pipe recheck through the verbatim
`classify_streams`: `--forge-release-stderr` → `classify_process=True`,
`classify_streams=False`; `--forge-release` (stdout) → both True. So the
boundary is exactly the merged check: either captured stream satisfies it; a
stream-split signature check would reject a stderr forgery but still accept
a stdout one. No defect — but "merged" is doing real work in the claim and
the boundary is wider than one stream.

## Attack (c) — the post-death ordering and the provenance field

- **Record cannot order a write vs the death.** The ungated mutant
  `mut_forge_ungated_honest_b8` (marker written ~0.05s post-spawn, pre-death,
  honest `$pp`) produces marker at output index 5 — the *same* position as
  the gated post-death arms: the child's own prints flush before the
  descendant's early write lands, so line order does not expose a pre-death
  write. Only the `write_ppid` field carries post-death evidence.
- **Honest pre-death writes fail closed**: the ungated honest arm records
  `write_ppid=1131809 == godot_pid` → `release_write_post_orphan` = False →
  meta rejects. The gate + discrimination pair works against truthful
  mutants.
- **The provenance field is self-reported — SLIP**:
  `mut_forge_lying_ppid_b8` writes the marker *pre-death* and prints a
  fabricated `write_ppid=1`. Evaluated under the author's eight
  discriminations: **8/8 true** — a pre-death forgery presents as a post-death
  forgery in the record. `write_ppid` is a printed claim, not a kernel fact.
  For the hold arm the meta *could* check kernel-side — the descendant is
  alive at return and my driver reads `/proc/<pid>/stat` ppid at return
  (`descendant_ppid_at_return=1573 ≠ godot_pid`, recorded in
  `spoof-attack-verdicts.json`); for the release arm the descendant is
  already reaped, so its record cannot be kernel-verified at all — the
  "provably post-exit" property is fixture-asserted there.

## Attack (d) — are the named discriminating fields doing the claimed work? NO

`child_exit_at_timeout` is kernel-true and unforgeable by fixture output:
`mut_forge_livechild` (child hangs; ungated descendant forges + holds) →
`timed_out=True`, `child_exit_at_timeout=None` →
`hold_timed_out_with_child_dead` rejects. Good.

But the dispatched claim names `child_exit_at_timeout`/`timed_out` as the
fields that distinguish the forged signature from a genuine one. Measured:

| hold-arm mutant under the author's 8 discriminations | result |
|---|---|
| auth_forge_hold (landed arm) | 8/8 — accepts (intended) |
| **mut_genuine_hold** — child prints the marker itself; gated descendant writes only `write_ppid=$pp`, holds | **8/8 — SLIP** |
| **mut_double_forge_hold** — child prints marker AND gated descendant forges it | **8/8 — SLIP** |
| mut_stderr_hold — forged marker on stderr | 8/8 |
| mut_genuine_silent_hold (tracked `--spawn-hold`, silent holder) | 7/8 — rejected only by `write_ppid` *absence* |
| mut_forge_livechild (child alive at bound) | 6/8 — rejects |

Release-side mutants: `mut_forge_ungated_honest` → `release_write_post_orphan`
False (caught); **`mut_forge_lying_ppid` → 8/8 slip**; `mut_forge_release_stderr` → 8/8.

Two conclusions:

1. **`timed_out`/`child_exit_at_timeout` never distinguish forged from
   genuine.** `mut_genuine_hold` has a child-authored signature yet matches
   the forged arm on all eight discriminations — including
   `hold_forged_signature_captured` (which is really "signature captured",
   origin-blind like the check it measures) and even `hold_write_post_orphan`
   (a genuine arm whose descendant prints a ppid line satisfies it). The
   fields the claim names mark the *hold shape* (dead child + pipe wait);
   they are identical across forged/genuine authorship. What actually
   separates forged from genuine in the record is **output-content
   provenance**: the `child_signature=withheld` banner (present in forged,
   absent in genuine; marker sits at index 5 vs index 2) and `write_ppid`.
   Neither named field appears in the release CASES record at all — CASES
   verdicts carry no `timed_out`/`child_exit_at_timeout`.
2. **"Provably descendant-authored" is not record-provable.** No
   discrimination checks the withheld banner: `mut_double_forge_hold`
   (child *and* descendant both write the marker) scores 8/8 — the meta
   cannot tell whether the captured signature is the descendant's. The claim
   holds by fixture construction, evidenced by self-reported lines.

## Field stability (independent)

My full flagged run: `runs/20261014T005336693128Z/verdicts.json` **97/97
PASS** (extra row vs author's 96 is `probe_audio_warning_captured_r12` — I
passed `--probe-audio-warning`, author did not). **94/94 prior rows match
the r62-verifier receipt** (`corpus/live/r62-verifier/runs/20261014T001002305311Z/verdicts.json`)
on the 8-field tuple (case/script/flags/expected_exit/actual_exit/signature/
verdict/error), **0 mismatches**; 0 mismatches vs the author's run on all
shared rows. Detached-control output shape unchanged (marker at index 2,
5 lines). "All prior 94 rows field-stable" confirmed.

## Verdict per attack

- **(a) Falsification failed — claim core confirmed.** No liveness guard;
  the release arm genuinely forges a PASS (0.405s, exit 0, classify True).
  Boundary is *wider* than worded: any signature-bearing tuple, either
  captured stream, and the hold arm under the 8s bound all forge acceptance.
- **(b) Sound, refined.** Merged `classify_process` is the spoof surface;
  `classify_streams` would reject a stderr forgery but is unused here.
- **(c) One bounded slip.** Honest pre-death writes are caught
  (`write_ppid==godot_pid`); fabricated `write_ppid=1` pre-death writes slip
  8/8 — provenance is self-reported. Kernel-side ppid verification is
  available for the hold arm only.
- **(d) Claim's discriminator set falsified.** `timed_out`/
  `child_exit_at_timeout` are kernel-sound but shared identically by forged
  and genuine holds — the live distinguishing evidence is output provenance
  (withheld banner + `write_ppid`), which the discriminations do not check
  and a mutant can fabricate.

**These are fixable defects, not a reject-level tradeoff.** The tracked
boundary is real and the rows do demonstrate origin-blind acceptance; the
defects are claim precision and two unchecked provenance assumptions.

## Smallest safe correction (additive, no mechanism change)

1. Reword claim + meta `bounded_claim`: the forged-vs-genuine separation is
   **post-orphan output provenance** (`child_signature=withheld` present,
   `write_ppid != godot_pid`), not `timed_out`/`child_exit_at_timeout` —
   those mark the hold shape only. Also state the boundary covers any
   `(expected_exit, signature, allowed_errors)` tuple on either captured
   stream.
2. Add one discrimination, e.g. `release_withheld_banner_present`:
   `"child_signature=withheld" in forged_output` — currently a child that
   prints banner *and* marker (or just the marker) produces an identical
   accepting meta.
3. For the hold arm only, kernel-verify provenance: read
   `/proc/<descendant_pid>/stat` field 4 at return and require
   `descendant_ppid_at_return != godot_pid` (descendant is alive at return;
   r62 verifier already demonstrated this check). For the release arm,
   record honestly that `write_ppid` is fixture-asserted (descendant reaped
   before return) — or hold the release descendant a beat and snapshot
   `/proc` before it exits.

## Artifact inventory (`.shokunin/game-dev-2d/corpus/live/r63-critic/`)

- `drive_spoof_attacks.py` (verbatim-extraction driver: 6 CASES-path arms +
  3 author reproductions + 6 bounded-Popen meta arms + eight-discrimination
  verbatim evaluator); `proj/sig_spoof_probe.gd` (11-arm mutant fixture),
  `proj/descendant_pipe_probe.gd` (tracked worktree copy), `proj/project.godot`.
- `spoof-attack-verdicts.json` sha256 `d1444c1d194478e8…` — all arm records
  incl. per-arm discrimination evals, stream split (`marker_on_stdout/
  stderr`), kernel ppid-at-return samples; `raw/*` captures.
- `runs/20261014T005336693128Z/verdicts.json` sha256 `c945247c45580dcf…` —
  independent full flagged battery, 97/97 PASS, 94/94 prior rows
  0-mismatch vs r62-verifier receipt; `battery.stdout` `ce8c737e710f5fcc…`.

No commit, no tracked-file mutation, no LOG/SCORECARD write. All spawned
descendants self-exited or were SIGKILLed in the driver's hygiene pass;
no stray processes remain (one observed `sleep 290` belongs to the fleet
watcher, not this lane).
