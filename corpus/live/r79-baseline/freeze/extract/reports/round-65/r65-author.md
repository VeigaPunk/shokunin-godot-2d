# Round 65 author report — forged-REJECTION dual (host: devin)

Seat: author (ONLY tracked-file writer), lane `game-dev-2d`, declared
axis-move (verbatim brief): pin the forged-REJECTION dual (XConnector
wave-4 Arm 1) — a reparenting-gated descendant that emits an
UN-ALLOWLISTED `ERROR:`-class marker post-parent-death converts a genuine
exit-0 + signature-present record into a FAIL; measure whether the
rejection axis is as origin-blind as the signature axis. Falsifiable
claim: the post-death injected error marker flips a CASES row from PASS
to FAIL with CASES-visible fields identical to a genuine child-emitted
error (no provenance except the r63-style withheld/ppid fields). Land
additive fixture arms + `probe_descendant_error_spoof` meta probe
discriminating release-with-error / hold-with-error / genuine-error
control; r64 while-live gate and all 97 prior rows byte-stable; document
whether the while-live gate also rejects the forged-error arm.

## Outcome — claim CONFIRMED on this fixture (measured, not assumed)

`classify_process`'s error clause is a presence scan over the merged
captured bytes: any line containing `ERROR:` outside the per-case
allowlist rejects, regardless of which process wrote it or when. The
rejection axis is measured **as origin-blind as the signature axis**:

- **Forged release arm** (`--spawn-errforge-release`, bounded Popen,
  child runs clean): exit 0, `error=None`, elapsed 0.679s — a clean
  exit-0 + signature-present record carrying the descendant's post-death
  `ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic` and
  `write_ppid=1573 ≠ godot_pid=1629804`. `inner_classification` **False**
  — the flip. `stripped_classification` (same captured bytes minus only
  `ERROR:` lines) **True** — the forged error line is the sole cause.
- **Genuine-error control** (`--emit-errforge`, child's own `push_error`
  pre-death, exit 0): `inner_classification` **False** on byte-identical
  `error_lines` (`[errforge_error]` in both). `cases_visible()` fields —
  `{actual_exit, error, signature_observed, error_lines,
  classification}` — are **identical** between forged and genuine
  records. The symmetric-difference of output lines is provenance only:
  banner text, `godot_pid=`/`spawned_pid=` values, `write_ppid=1573`, and
  push_error's `   at:`/backtrace context lines — no `ERROR:` line, no
  signature line (`forged_vs_genuine_differ_only_in_provenance` True,
  `provenance_only_line_diff` recorded verbatim in the row).
- **Hold arm** (`--spawn-errforge-hold`, 3.0s bound): TIMEOUT record with
  `child_exit_at_timeout=0` carrying the forged error — double-axis
  rejection (error + timeout), `inner_classification` False. Descendant
  still alive at return; `/proc/<pid>/stat` ppid `1573` ==
  self-reported `write_ppid` ≠ `godot_pid` — kernel-corroborated
  post-orphan write (closes the fabricated-write_ppid class, r63/r64
  pattern).
- **Stream split** (separate PIPEs): forged descendant echo lands on
  **stdout only**; genuine `push_error` lands on **stderr only**; both
  merged classifications **False** — the merge hides even stream origin.

**While-live gate interplay (the brief's open question):** the r64 gate
does **NOT** reject the forged-error arm — measured, not inferred. Its
criterion is the signature marker only; the signature here is genuinely
child-authored, so `gated_signature_accepted` is **True on all 3 reps**
while `inner_classification` is **False** on the same captured bytes. The
forged error is *gate-invisible as a verdict input* — yet NOT invisible
to the gated read: the dual-marker r65 runner records it arriving only
after observed child death in every rep (`dead_observed_at` 0.632/0.686/
0.678s < `error_observed_at` 0.663/0.718/0.710s; genuine-error reps show
the error while-live at signature+20µs). The timing split an error-axis
gate would need is captured; the built gate simply never evaluates it.
Asymmetry pinned: signature axis has a while-live gate, the rejection
axis has none — forged post-death errors are rejected only because the
un-gated merged scan is origin-blind, not despite it.

Arms are meta-driven bounded Popens, **not CASES tuples**: an
expected-FAIL record is inexpressible in the all-PASS battery (the r62
hold-arm precedent). The "CASES row flip" is measured on the record
shape the row would carry — verified two ways: `inner_classification`
over the real captured bytes, and the counterfactual strip.

## Labrat spike (dispatched, bounded, read-only)

One `ufo-labrat` probe dispatched pre-landing with the exact planned arm
code and measurements. Its tool surface resolved read-only (no exec), so
it could not run the probe itself; it instead audited the landed receipts
verbatim plus a sibling scribe lane's independent matrix
(`corpus/live/r65-scribe/`, different marker text, 162-run matrix —
arriving at the same observations). My own pre-battery smoke runs
(`corpus/live/r65-author/smoke/`, direct godot + bounded-Popen captures)
are the pre-landing empirical check: release arm exit 0 @0.546s with
sig+error+`write_ppid=1573` captured; hold arm TIMEOUT child_exit=0 with
the forged error inside the record.

## Landed diff (additive only — +466/−0)

- `corpus/fixtures/descendant_pipe_probe.gd` — sha256
  `4fce06765b091e9ffe649b06fca020115e07d2590b91200d57c4f319b3fdb3a2`
  (HEAD `61ec1c0`) → `37cf50156839502a1372746d31c3db6b8c835df734acf838025c1664f3262e59`,
  **+35/−0**: three constants, three flag parses, banner/`push_error`
  lines, one `elif` descendant arm reusing the r63 reparenting gate
  verbatim (`/proc/self/stat` ppid poll → post-death echo of
  `ERRFORGE_ERROR` + `write_ppid=$pp`, `; sleep 6` tail on -hold).
- `corpus/fixtures/run_battery.py` — sha256
  `66a18a0056aedbd6c99ed8637ed30d03a3404556ab49d05826e8c63f4fe1f07d`
  (HEAD) → `1acbc73d80fa69317600ee2813ec44a71fd02a2436471bf52cb8c15ae052b2a3`,
  **+431/−0**: single block (`run_battery.py:1107-1537`) between the r64
  gate meta print and `if args.probe_failing:`. New row
  `probe_descendant_error_spoof` carrying `errforge_run` (bounded Popen,
  CASES-record shape + counterfactual strip), `gated_errforge_run`
  (dual-marker selectors read: signature AND error liveness at each
  completing chunk), `split_errforge_run` (separate PIPEs), 3 un-gated
  arms + 5 gated reps + 2 split runs, **28 discriminations, all True**,
  SIGKILL orphan hygiene (ungated).

Zero deletions: `run_process`, `classify_process`, `classify_streams`,
`classify_audio_process`, `gated_signature_run`, CASES, `expected_errors`,
and every existing meta row untouched.

## Landed per-arm measurements

(`runs/20261014T023015140150Z/verdicts.json` → `results[97]`)

| arm | exit | error | sig | ERROR: line | wppid | inner cls | strip cls |
|---|---|---|---|---|---|---|---|
| errforge_release | 0 | None (0.679s) | yes | forged, post-death | 1573≠godot | **False** | True |
| errforge_hold | None | TIMEOUT 3.003s | yes | forged, in TIMEOUT rec | 1573=kppid≠godot | **False** | False (timeout) |
| errforge_genuine | 0 | None (0.671s) | yes | genuine push_error | none | **False** | True |

| gated rep | sig@ | alive | dead@ | err@ | alive | gate | inner |
|---|---|---|---|---|---|---|---|
| release_r0 | 0.5600 | True | 0.6315 | 0.6632 | **False** | ACCEPT | False |
| release_r1 | 0.6145 | True | 0.6862 | 0.7178 | **False** | ACCEPT | False |
| release_r2 | 0.6066 | True | 0.6783 | 0.7100 | **False** | ACCEPT | False |
| genuine_r0 | 0.5710 | True | 0.6370 | 0.5710 | True | ACCEPT | False |
| genuine_r1 | 0.5882 | True | 0.6556 | 0.5883 | True | ACCEPT | False |

Stream split: forged `error_on_stdout=True, error_on_stderr=False`;
genuine `error_on_stderr=True, error_on_stdout=False`; both merged
`inner_classification=False`.

## Exact evidence

Mandated seven-flag battery (exact invocation, canonical repo root
`~/Projects/shokunin/game-dev-2d-shokunin`):
`python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
corpus/live/r65-author/runs --probe-failing --probe-unrelated-error
--probe-export-launch --probe-godot-error --probe-stream-attribution
--probe-crash-exit --probe-timeout` → **exit 0**,
`runs/20261014T023015140150Z/verdicts.json` **PASS, 98/98 rows** (sha256
`3a4f7fafdb7d841e29d06c73dc339a1711fae0cb014c0771c25ec268a93f3eea`);
stdout `corpus/live/r65-author/battery.stdout` (line 87 `PASS descendant
error-spoof meta`). Row arithmetic: 81 CASES + 2 mutants + 4
unrelated-error + 11 meta/probe rows (6 unconditional: save-process,
crash, pipe-EOF, signature-spoof, while-live-gate, **error-spoof**; 5
opt-in). The two designed inner `FAIL` lines (`godot_error_unrelated`,
`stream_reject`) unchanged.

Prior-row stability — 7-field diff `(script, flags, expected_exit,
actual_exit, signature, verdict, error)`:

- vs **same-session pretree** run: HEAD tracked tree materialized
  read-only via `git archive HEAD corpus/fixtures | tar -x` into
  `corpus/live/r65-author/pretree/` (run_battery sha256 `66a18a00…`,
  fixture `4fce0676…`, both == `git show HEAD:` digests), run
  `pretree-runs/20261014T023013125961Z/verdicts.json` **PASS 97/97**
  (sha256 `e32357a5e11b55682f70cdc05733de99fe016c5f8367525d55b95aada5cdd2c4`):
  **97 common rows, 0 mismatches**; new-only
  `{probe_descendant_error_spoof}`; baseline-not-in-new `[]`.
- vs r65 **named baseline receipt**
  `corpus/live/r65-baseline/runs/20261014T022523005280Z/verdicts.json`:
  **97 common rows, 0 mismatches**. The r63 pinned accepting-boundary row
  `descendant_pipe_forged_signature_release` stays `PASS exit=0
  signature=forged`, and the r64 `probe_while_live_signature_gate` row
  stays `PASS` — byte-stable.

Separate leg: `--fault-injection` → **exit 0**,
`fault-runs/20261014T023315248815Z/fault-verdicts.json` outer **PASS**
(sha256 `68dbd098c882a2d09e688568201fbc335138d1553f5c8a909a6ff88e964d8620`),
designed inner `fault_hang`/`fault_unrelated_error` FAILs unchanged.

No LSP server answers either file (Python + GDScript fixtures, none
configured) — text edit was the only path; the change is two appended
self-contained blocks, no cross-file rename needed.

## Files written (inside brief scope only)

- tracked: `corpus/fixtures/descendant_pipe_probe.gd` (+35/−0),
  `corpus/fixtures/run_battery.py` (+431/−0)
- report: `reports/round-65/r65-author.md` (this file)
- scratch: `corpus/live/r65-author/{smoke/,pretree/,pretree-runs/,
  pretree-battery.stdout,runs/,battery.stdout,fault-runs/,fault.stdout}`

## Remaining risks / blockers

- **Genuine-arm race (bounded, declared):** the genuine-error gated rep
  measures the error ~20µs after the signature inside the live window;
  under extreme scheduler stall a genuine error chunk could in principle
  be observed post-death → `gate_genuine_error_observed_while_live`
  would flip the row FAIL (declared falsification surface, not hidden).
  Margin on this host: death first observed ~65ms after the writes.
- **Stream-merge ordering:** the naive `communicate` merge concatenates
  stdout+stderr (order can interleave non-deterministically relative to
  the tty); classification is order-free, so this affects only line
  ordering inside `output_lines`, never verdict.
- **Descendant echo is stdout-only** — a forged `>&2` variant is
  untested in-tree (the scribe lane's matrix independently ran it → same
  merged FAIL; not my receipt, noted as corroboration only). The
  error clause is stream-blind by construction post-merge.
- **Error-axis gate unbuilt** — the dual-marker run captures the timing
  split such a gate would need; its verdict is inference, deliberately
  not claimed as measurement (labrat honest-gap note).
- No blockers. Commit/push left to operator per seat rules.
