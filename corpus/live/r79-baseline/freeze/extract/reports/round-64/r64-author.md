# Round 64 author report — while-live signature gate meta probe (host: devin)

Seat: author (ONLY tracked-file writer), lane `game-dev-2d`, declared
axis-move (verbatim brief): test the falsifiable claim that a while-live
marker read discriminates forged post-death signatures from genuine child
signatures (the XConnector wave-3 synthesis proposal; r63 adjudicator:
"a while-live marker-read gate (3d-style) would narrow the accepting
boundary to post-death forgeries only"). Bounded-Popen meta arm over the
EXISTING `--spawn-forge-release` / `--spawn-forge-hold` fixture arms plus
the unmodified default genuine arm; additive only — the r63 pinned
accepting-boundary row stays byte-stable; all 96 prior rows field-stable.

## Outcome — claim CONFIRMED on this fixture (measured, not assumed)

A `poll()`-gated read accepts the expected marker only when observed while
the direct child is alive (`process.poll() is None` at the
marker-completing read). On this fixture and host the gate **discriminates
deterministically**:

- **Genuine arms** (default `[]` ×3, `--spawn-detach` ×1): the child's own
  `MARKER` write was observed while-live in **4/4** reps —
  `dead_observed_at − marker_observed_at = +0.067..+0.069s` (child death
  first observed ~67ms AFTER the marker read; both `alive_at_obs` and
  `alive_after` True) → gate **ACCEPT**, `inner_classification` True.
- **Forged arms** (`--spawn-forge-release` ×3, `--spawn-forge-hold` ×1):
  the descendant's reparenting-gated signature write was captured in
  **4/4** reps but only AFTER child death was already observed —
  `dead_observed_at − marker_observed_at = −0.0315..−0.0320s` →
  `alive_at_obs` False → gate **REJECT a PRESENT marker**. On the release
  arm the same captured bytes still classify `inner_classification` **True**
  — the gate rejects exactly what the un-gated classifier accepts, the
  pinned r63 boundary made visible in one record.

No falsification observed: zero post-death observations across all genuine
reps; zero while-live observations across all forged reps. The
nondeterminism axes are recorded per rep (`marker_observed_at`,
`dead_observed_at`, `child_alive_at_marker_observation`,
`child_alive_after_marker_read`) — the genuine-side race margin measured
**+67ms±1ms** on this host (engine-teardown window vs ~5ms poll tick);
the forged-side lag measured **−32ms±0.5ms**, bounded below by the
fixture's `sleep 0.05` reparent-poll cadence.

Residual falsification surface (declared, not hidden): a genuine signature
observed post-death under heavier scheduler load would falsify the
discrimination — the +67ms margin is the measured bound, and
`genuine_never_observed_post_death` is the discrimination that turns it
into a FAIL rather than hiding it. A forge that writes *before* the
child's death (not reparenting-gated) defeats the gate by construction —
out of scope of this claim (observation-time liveness is not authorship
proof; stated in the row's `bounded_claim`).

## Pre-edit labrat-style spike (scratch, pre tracked edits)

`corpus/live/r64-author/spike/gated_spike.py` against a scratch project
(`spike/proj/`, `project.godot` renamed `MechanicOneShotTest-r64spike` +
tracked `descendant_pipe_probe.gd` copied byte-identical). Runs:
`spike/gated_spike_run1.txt` — genuine 6/6 ACCEPT while-live (incl. detach),
forged 4/4 REJECT post-death (lead −0.0317..−0.0320s); plus a 10-rep
genuine-default flake check: **10/10** accepted while-live, margins up to
+0.068s. Totals: 16/16 genuine ACCEPT, 4/4 forged REJECT pre-landing.

## Landed diff (additive only)

`corpus/fixtures/run_battery.py` — sha256
`fb7cab2bb0364bef802cd3ed67892510377b8c45024daa378ca632129d96d7c2` (HEAD
`a7e0cb1`) → `15ecad36aa996426ff3bff882fd6064ddf4540cbc87dd58713d7f8c432256b4f`.
`git diff --stat`: **+224/−0**, one hunk inserted between the r63
signature-spoof meta print and `if args.probe_failing:` — zero deletions,
`run_process`/`classify_process`/`classify_streams`/CASES/all existing meta
rows byte-stable. New row `probe_while_live_signature_gate`
(`run_battery.py:879-1105`):

- `gated_signature_run(case, extra_args)` — binary `selectors.DefaultSelector`
  read over BOTH captured pipes (`gate_poll_tick=0.005` idle tick also
  samples child death even with no data); on each chunk records liveness
  before and after the read; the marker-completing chunk pins
  `child_alive_at_marker_observation`. Drains to pipe EOF or `gate_bound=3.0`
  (`timed_out` + bounded kill/wait hygiene, same shape as r62/r63 arms).
- Per-arm record: marker presence/observation time, liveness at
  observation, `dead_observed_at` (None = loop ended on EOF before poll()
  saw the exit — itself while-live evidence), `withheld_banner`,
  `write_ppid`/`godot_pid`/`descendant_pid`, `descendant_alive_at_return`,
  `descendant_kernel_ppid_at_return` (`kernel_ppid` helper reused),
  `gated_signature_accepted`, `inner_classification` (same bytes through
  the UNCHANGED classifier), `output_lines`.
- 8 arm records: `genuine_default_r{0,1,2}`, `genuine_detach`,
  `forge_release_r{0,1,2}`, `forge_hold`.
- 12 discriminations, all true in the landed battery (row
  `verdicts.json` path below): `genuine_marker_accepted_while_live`,
  `genuine_never_observed_post_death`, `detach_marker_accepted_while_live`,
  `forge_release_marker_captured_post_death`,
  `forge_release_gate_rejects_what_classifier_accepts`,
  `forge_hold_marker_captured_post_death`, `forge_hold_gate_rejects`,
  `forge_withheld_banner_present`, `forge_write_post_orphan`,
  `forge_hold_write_ppid_kernel_corroborated` (/proc ppid `1573` ==
  self-reported `write_ppid` ≠ `godot_pid` on the still-alive hold
  descendant — closes the fabricated-write_ppid class, same as r63;
  release descendants exit before return, fixture-asserted only),
  `hold_descendant_orphaned_alive`,
  `gate_discriminates_forged_from_genuine`.
- Hygiene: SIGKILLs orphaned arm descendants after recording (detach +
  forge; bounded sleeps that self-exit anyway); never gated.

Landed per-arm measurements (`runs/20261014T013826495191Z/verdicts.json`):

| arm | exit | error | marker@ | dead@ | lead | alive_at_obs | gate | un-gated cls | write_ppid |
|---|---|---|---|---|---|---|---|---|---|
| genuine_default_r0 | 0 | — | 0.4845 | 0.5516 | +0.0671 | True | ACCEPT | True | — |
| genuine_default_r1 | 0 | — | 0.4211 | 0.4898 | +0.0686 | True | ACCEPT | True | — |
| genuine_default_r2 | 0 | — | 0.5160 | 0.5830 | +0.0670 | True | ACCEPT | True | — |
| genuine_detach | 0 | — | 0.3951 | 0.4632 | +0.0680 | True | ACCEPT | True | — |
| forge_release_r0 | 0 | — | 0.5399 | 0.5079 | −0.0320 | False | REJECT | **True** | 1573 |
| forge_release_r1 | 0 | — | 0.5089 | 0.4773 | −0.0317 | False | REJECT | **True** | 1573 |
| forge_release_r2 | 0 | — | 0.5532 | 0.5217 | −0.0315 | False | REJECT | **True** | 1573 |
| forge_hold | 0 | TIMEOUT 3.0s | 0.6003 | 0.5682 | −0.0320 | False | REJECT | False | 1573 |

## Exact evidence

Mandated seven-flag battery (exact invocation, canonical repo root):
`python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
corpus/live/r64-author/runs --probe-failing --probe-unrelated-error
--probe-export-launch --probe-godot-error --probe-stream-attribution
--probe-crash-exit --probe-timeout` → **exit 0**,
`runs/20261014T013826495191Z/verdicts.json` **PASS, 97/97 rows** (sha256
`c385f8f1ea78b109803a1841cce116fa3ca81c73ef7262728a6be1c5511936bd`);
stdout `corpus/live/r64-author/battery.stdout`. Row arithmetic: 81 CASES +
2 mutants + 4 unrelated-error + 10 meta/probe rows (5 unconditional:
save-process, crash, pipe-EOF, signature-spoof, **while-live-gate**; 5
opt-in). The two designed inner `FAIL` lines (`godot_error_unrelated`,
`stream_reject`) unchanged.

Prior-row stability — 7-field diff `(script, flags, expected_exit,
actual_exit, signature, verdict, error)`:
- vs **same-session pre-edit** run: HEAD file materialized read-only via
  `git show` into `corpus/live/r64-author/pretree/fixtures/` (sha256
  `fb7cab2b…` = pre-edit), run
  `pretree-runs/20261014T013655181850Z/verdicts.json` **PASS 96/96**
  (sha256 `b35516789b68d1520dcb733a967985c5936d0e2aa026432fb36a32552cf4a998`):
  **96 common rows, 0 mismatches**; new-only
  `{probe_while_live_signature_gate}`; baseline-not-in-new `[]`.
- vs r63 named author receipt
  `corpus/live/r63-author/runs/20261014T004113548836Z/verdicts.json`:
  **96 common rows, 0 mismatches**. The r63 pinned accepting-boundary row
  `descendant_pipe_forged_signature_release` stays `PASS exit=0
  signature=forged` — documented, not fixed (byte-stable row).

Separate leg: `--fault-injection` → exit 0,
`fault-runs/20261014T014002655852Z/fault-verdicts.json` outer **PASS**
(sha256 `cc50beaf84dfdc2010358eafda5dbb50e217ed6327d8e39fd7b3538cc612fd8f`),
designed inner `fault_hang`/`fault_unrelated_error` FAILs — unchanged
(fault path returns before CASES/meta by construction).

No LSP server answers this file (Python fixture, none configured) — text
edit was the only path; the change is an appended self-contained block, no
cross-file rename needed.

## Files written (inside brief scope only)

- tracked: `corpus/fixtures/run_battery.py` (+224/−0)
- report: `reports/round-64/r64-author.md` (this file)
- scratch: `corpus/live/r64-author/{spike/,pretree/,pretree-runs/,
  pretree-battery.stdout,runs/,battery.stdout,fault-runs/,fault.stdout}`

## Remaining risks / blockers

- Host-load flake axis on the genuine arm is real but bounded: measured
  margin +67ms vs 5ms poll tick; a genuine post-death observation flips
  `genuine_never_observed_post_death` → row FAIL (the declared falsified
  outcome, not a silent pass).
- The gate rejects *post-death-observed* markers only; it cannot see write
  time. A forged write racing into the pipe *before* child exit would be
  accepted — documented in `bounded_claim`; the fixture's forge is
  reparenting-gated so this class is unreachable in these arms.
- `descendant_alive_at_return` varied True/False across release reps
  (descendant mid-exit at check time — sub-ms race, ungated field);
  only `hold_descendant_orphaned_alive` is gated.
- No blockers. Commit/push left to operator per seat rules.
