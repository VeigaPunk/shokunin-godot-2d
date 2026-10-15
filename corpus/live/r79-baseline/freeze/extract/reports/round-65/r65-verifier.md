# Round 65 verifier report — named non-author verifier (host: devin)

Seat: named non-author verifier, lane `game-dev-2d`, committed state under
test `414eb8e066eda414fa316c4b77b641e8e194496c` (`r65: forged-REJECTION
dual — post-death ERROR: flips genuine PASS->FAIL`). Independent replay of
the committed bytes only; no tracked modification, no commit, no dispatch.

## Committed-bytes provenance

- `git rev-parse HEAD` → `414eb8e066eda414fa316c4b77b641e8e194496c`;
  `git diff HEAD --stat` → empty (clean tracked tree).
- Executed runner == committed blob: worktree
  `corpus/fixtures/run_battery.py` sha256
  `cd4824cc1a0199c2886ee8c5815ed5065757f50f6f59420ef79d56b4fd302d58`
  == `git show HEAD:corpus/fixtures/run_battery.py` sha256 (identical);
  `corpus/fixtures/descendant_pipe_probe.gd` sha256
  `37cf50156839502a1372746d31c3db6b8c835df734acf838025c1664f3262e59`
  == HEAD blob. The bytes I executed ARE the committed bytes.
- Lane worktree `~/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d`
  is a symlink resolving to `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`.
- Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
  Python `3.14.7`, `systemd --user` subreaper ppid `1573` — same host
  profile as the r65 baseline/author receipts.

## Claim 1 — forged rejection flips a genuine-looking record to FAIL; all rows PASS, meta discriminations all True (29): **AGREE**

Command (verbatim, absolute `--runs` as required), cwd
`~/Projects/prymeagnt/game-dev-2d`:

```
python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/runs
```

Output: pipeline exit 0; stdout `88` `^PASS` lines, `0` `^FAIL` lines
(tee'd to `corpus/live/r65-verifier/battery.stdout`). New receipt
`corpus/live/runs/20261014T043948860752Z/verdicts.json`:
`"verdict": "PASS"`, **87 results, 87 PASS / 0 FAIL** (81 CASES + 6 meta
rows — bare invocation, no opt-in flags). Meta row
`probe_descendant_error_spoof`: `verdict PASS`, mode
`bounded_popen_dual_marker_gate_and_stream_split`, bound 3.0s,
**29 discriminations, every value `True`** (enumerated below verbatim
from my receipt):

```
release_clean_exit0_record                     True   hold_rejects                                True
release_genuine_signature_present              True   hold_timeout_alone_rejects                  True
release_forged_error_captured                  True   hold_write_ppid_kernel_corroborated         True
release_error_write_post_orphan                True   hold_descendant_orphaned_alive              True
release_flips_to_fail                          True   gate_release_signature_accepted_while_live  True
release_counterfactual_passes_without_error    True   gate_release_forged_error_observed_post_death True
genuine_clean_exit0_record                     True   gate_does_not_reject_forged_error_arm       True
genuine_error_captured                         True   gate_genuine_error_observed_while_live      True
genuine_error_rejects                          True   gate_error_axis_timing_split                True
genuine_counterfactual_passes_without_error    True   forged_error_lands_on_stdout                True
genuine_carries_no_descendant_provenance       True   genuine_error_lands_on_stderr               True
error_marker_bytes_identical                   True   merged_classification_stream_blind          True
forged_vs_genuine_cases_fields_identical       True   detached_control_row_still_passes           True
forged_vs_genuine_differ_only_in_provenance    True   hold_timed_out_with_child_dead              True
                                                   hold_forged_error_captured                    True
```

Release arm in my receipt: `actual_exit=0`, `error=None`,
`timed_out=False`, `signature_observed=True`,
`error_marker_captured=True`,
`error_lines=["ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected
diagnostic"]`, `inner_classification=False` — a genuine-looking
exit-0/signature-present record flipped to FAIL, exactly as claimed.
(`run_battery.py` L1137–1224 mechanism re-read: bounded `communicate`
merge → `classify_process`' un-allowlisted-`ERROR:` presence scan.)

## Claim 2 — sole cause: stripping only ERROR: lines restores True: **AGREE**

`release_arm.stripped_classification` is **`True`** in my receipt while
`inner_classification` is `False` on the same capture. The counterfactual
is constructed at `run_battery.py:1216–1222` — `stripped_text` drops only
lines containing `"ERROR:"` from the SAME captured bytes, then re-runs
the same `classify_process`; nothing else in the record changes. The
genuine control shows the symmetric shape (`inner=False`,
`stripped=True`). Independently consistent with the classifier's single
rejection input (`unrelated_errors` presence scan, L174–177). Sole cause
confirmed by replay, not prose.

## Claim 3 — classification-visible fields identical forged-vs-genuine; differ only in provenance: **AGREE**

Recomputed `cases_visible()` myself from my receipt's recorded fields
(`{actual_exit, error, signature_observed, error_lines, classification}`):

- forged release: `{0, None, True, ["ERROR: DESCENDANT_PIPE_ERRFORGE
  unrelated injected diagnostic"], False}`
- genuine control: identical dict, key-for-key.

Recomputed the output-line symmetric difference; it equals the recorded
`provenance_only_line_diff` verbatim — 9 lines, every one provenance:
banner text (`child=clean …` vs `child_error=genuine_pre_exit`),
`godot_pid=`/`spawned_pid=` values, `write_ppid=1573`, and the genuine
arm's `push_error` context lines (`   at: push_error …`,
`   GDScript backtrace …`, `       [0] _initialize …`). No `ERROR:` line,
no signature line in the diff — confirmed non-ERROR/non-signature by
direct scan.

## Claim 4 — kernel corroboration: hold write_ppid matches /proc and != godot_pid: **AGREE**

Two independent evidences, both mine:

1. My receipt's hold arm: `write_ppid=1573`,
   `descendant_kernel_ppid_at_return=1573`, `godot_pid=1845334`,
   `descendant_pid=1845372`, `descendant_alive_at_return=True` —
   kernel ppid == self-reported write_ppid ≠ godot_pid.
2. My own out-of-runner probe (scratch copy of the fixture in
   `corpus/live/r65-verifier/proj/`):
   `godot --headless --path proj --script res://descendant_pipe_probe.gd
   -- --spawn-errforge-hold` printed `godot_pid=1842946`,
   `spawned_pid=1842987`, `ERROR: DESCENDANT_PIPE_ERRFORGE unrelated
   injected diagnostic`, `DESCENDANT_PIPE_ERRFORGE write_ppid=1573`
   (all on stdout; stderr empty — incidentally confirming
   `forged_error_lands_on_stdout`). While the descendant `sleep 6`
   (pid 1842987) was still alive I read `/proc/1842987/stat` field 4
   directly: **ppid 1573** — kernel-side, independent of the runner's
   `kernel_ppid()` helper, equal to self-reported `write_ppid` and
   different from `godot_pid`.

Scope note (as claimed, not a defect): the release arm's descendant is
dead at return so its `write_ppid` is fixture-asserted only; kernel
corroboration applies to the hold arm — the claim says exactly that.

## Claim 5 — gate boundary: r64 while-live signature gate ACCEPTS the forged-error arm; rejection stays downstream: **AGREE**

My receipt's `gated_release_reps` (3 reps of `--spawn-errforge-release`
under the dual-marker gated read):

| rep | gated_signature_accepted | alive@signature | error_observed | alive@error | dead_observed_at | error_observed_at | inner_classification |
|-----|--------------------------|-----------------|----------------|-------------|------------------|-------------------|----------------------|
| r0  | True  | True | True | False | 0.365584 | 0.397537 | False |
| r1  | True  | True | True | False | 0.369665 | 0.401523 | False |
| r2  | True  | True | True | False | 0.382463 | 0.414294 | False |

The signature is genuinely child-authored and observed while-live → the
r64 criterion accepts all 3 reps; the forged error arrives only after
observed child death (`dead < error` each rep) yet the record still
classifies False — rejection lives in the un-gated merged classifier,
not the gate. Genuine reps show the complementary half of the timing
split (`error_observed` with `child_alive_at_error_observation=True`).
Stream split likewise reproduced: forged echo stdout-only, genuine
`push_error` stderr-only, both merged classifications False.

## Claim 6 — regression: every pre-r65 row present, verdicts unchanged: **AGREE**

7-field tuple diff (`script, flags, expected_exit, actual_exit,
signature, verdict, error`; meta rows compared on `verdict` per
r62–r64 precedent), indexed by `case`:

- My run (87) vs r65-baseline frozen receipt
  `corpus/live/r65-baseline/runs/20261014T022523005280Z/verdicts.json`
  (97, all PASS): **86 common cases, 0 mismatches**. My only extra row:
  `probe_descendant_error_spoof`. The 11 baseline-only rows
  (`mutant_*` ×2, `probe_unrelated_error_*` ×4, `probe_export_launch`,
  `probe_godot_error`, `probe_stream_attribution`, `probe_crash_exit`,
  `probe_timeout`) are flag-gated opt-ins never emitted by a bare
  invocation — not removed rows.
- Cross-check vs the author's committed full-flag receipt
  `corpus/live/r65-author/runs/20261014T023015140150Z/verdicts.json`
  (98, all PASS): my 87 rows common, **0 mismatches**; author vs
  baseline: **97 common, 0 mismatches**, author-only =
  `probe_descendant_error_spoof` — the +1 additive shape the commit
  claims ("prior 97 rows stable") holds on the full surface too.
- All three receipts are all-PASS.

## Process hygiene / repo cleanliness

- Post-run `ps`: no leaked `--headless` godot processes and no fixture
  `sleep 6` descendants (harness reaps errforge orphans; my manual hold
  probe's descendant self-exited within its bounded sleep).
- `git status`: my writes are `corpus/live/r65-verifier/` (assigned
  scratch), this report, and the gitignored
  `corpus/live/runs/20261014T043948860752Z/` receipt written by the
  mandated command (`corpus/live/.gitignore: runs/`). Pre-existing
  untracked dirs (`r64-baseline/frozen/`, `r65-baseline/frozen/`,
  `r65-boundary/`) untouched. **Zero tracked modifications.**

## Notes / honest gaps (none affecting the verdicts)

- The author's committed receipt recorded **28** discriminations; the
  committed source emits **29** — the simplifier-added
  `hold_timeout_alone_rejects` landed after that mid-flight run. My
  replay of committed bytes produces 29/29 True, matching the claim.
- `dead_observed_at` can be `None` on genuine arms by design (EOF before
  first post-death poll tick); not hit here — all forged reps recorded
  finite `dead < error` ordering.
- Single host, single clean replay; per author-declared surface the
  genuine-arm ~20µs error-observation race is a bounded falsification
  window, not observed (death-first-observed margin ~65ms in my reps).
- Descendant `>&2` forged-error variant remains untested in-tree (the
  merged classifier is stream-blind by construction; split arms show
  rejection on both stream origins anyway).

## Verdict summary

| # | claim | verdict |
|---|-------|---------|
| 1 | forged `ERROR:` flips exit-0/sig-present record to FAIL; all rows PASS; 29/29 discriminations True | **AGREE** |
| 2 | strip only `ERROR:` lines → `stripped_classification` True; sole cause | **AGREE** |
| 3 | classification-visible fields identical; diff provenance-only | **AGREE** |
| 4 | hold `write_ppid` == kernel `/proc` ppid (1573) ≠ `godot_pid` | **AGREE** (double-corroborated) |
| 5 | r64 while-live gate accepts forged-error arm; rejection downstream | **AGREE** |
| 6 | all pre-r65 rows present, 0 tuple mismatches vs baseline/author receipts | **AGREE** |

**6/6 AGREE.** Committed state `414eb8e` replays as claimed: the
un-allowlisted-`ERROR:` rejection axis is as origin-blind as the
signature axis, the flip is solely the forged post-death error line, and
the while-live gate's signature-only criterion does not see it.
