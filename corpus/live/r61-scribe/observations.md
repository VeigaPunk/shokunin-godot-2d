# r61-scribe observation receipt (read-only; no runners executed by this seat)

All commands run from worktree `~/Projects/prymeagnt/game-dev-2d`, paths under
`.shokunin/game-dev-2d/` → `~/Projects/shokunin/game-dev-2d-shokunin`.
Host: devin. Observed 2026-10-13.

## Commands and observed output

- `git -C ~/Projects/shokunin/game-dev-2d-shokunin status --short` → only
  untracked `corpus/live/r61-baseline/`, `corpus/live/r61-reviewer/`
  (`r61-simplifier/` appeared on a later listing). No tracked modifications.
  HEAD `3ee05ff` (r60 work commit `8aca02e` "game-dev-2d r60: spontaneous-crash
  classification verified (devin host)" in history).
- `ast` parse of `corpus/fixtures/run_battery.py` → **77 CASES rows**, 5-tuples
  `(name, script, flags, expected_exit, signature)`; last row
  `('save_process_missing', ..., 2, 'ERROR: SAVE PROCESS EXPECTED NEGATIVE: ...')`.
- `sha256 corpus/fixtures/run_battery.py` =
  `42104d95af5fcb98d742c495ee4562ea0c579c49d9ca22d11755302f685c31fb`
  — identical to r60 author/verifier claim (unchanged at draft time).
- `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`;
  `python3 --version` → `3.14.7`; `uname -r` → `7.2.3-arch1-3`. Same as r60.
- `corpus/live/runs/` does NOT exist: r60 author's scratch
  `corpus/live/runs/round-60/` is gone (live scratch disposable). Surviving
  copies of the probe fixture: `corpus/live/r60-verifier/scratch-probe/proj/
  spontaneous_crash_probe.gd` and `corpus/live/r61-reviewer/scratch-probe/proj/
  spontaneous_crash_probe.gd` (byte content quoted in report).
- `find corpus/live/r61-*` → sibling scratch present: r61-baseline (tree
  snapshot + `runs/20261013T220006012870Z/` battery + `battery.stdout`),
  r61-reviewer (`runs/battery/20261013T220005698057Z/`, own
  `scratch-probe/r61-reviewer-spontaneous-crash-verdicts.json`), r61-simplifier
  (`runs/` created). No `reports/round-61/` existed before this seat created it.
- r61-reviewer verdicts JSON (sibling scratch, untrusted-data read):
  accept exit1 classify(1)=True; `OS.crash`×2 → actual_exit **-6** SIGABRT,
  stderr `ERROR: r60 spontaneous crash probe` + `at: crash
  (core/core_bind.cpp:349)` + GDScript bt `spontaneous_crash_probe.gd:15` +
  `handle_crash: Program crashed with signal 4` + C++ bt;
  classify(-6)=**False**, classify(-6, allowed=("ERROR: r60 spontaneous crash
  probe",))=**True**; self-sigkill → **-9**, empty stderr,
  classify(-9)=**True** unmodified. Third independent reproduction of r60
  (author + non-author verifier + this reviewer).

## Classifier facts read from `run_battery.py` (lines cited in report)

- `run_process` (L140–149): merged stdout+stderr; returncode, or `(None,
  "TIMEOUT …")`/`(output, None, "launch error: …")`.
- `classify_process` (L151–168): `code == expected_exit and error is None and
  signature in output and not unrelated_errors and no "SCRIPT ERROR:"/"Parse
  Error:"`. `unrelated_errors` = any output line containing `ERROR:` not
  matched by an `allowed_errors` entry; allowlist match = exact stripped
  equality, or trailing-comma prefix with `stripped.count("ERROR:") == 1`
  (plus the hardcoded `ERROR: chain incomplete` special case).
- `expected_errors` dict (L391–435): per-case-name allowlist, `.get(name, ())`.
  Adding a key is data-only; classifier code untouched ("zero-runner-change"
  path identified at r60 — precisely: zero *classifier/harness-logic* change;
  the runner file gains CASES row(s) + one dict entry).
- CASES `execute(*case)` (L451–452): 5-tuples only; allowlist bound by name.
- `--probe-crash-exit` (L753–868): r21 harness-SIGTERM meta probe —
  `crash_exit_accept` (quit(1), -, classify True) vs
  `crash_exit_signal_reject` (parent `send_signal(SIGTERM)`, -15, classify
  False); meta requires marker observed while live, `actual_exit == -15`.
- `classify_streams` (L170–199) exists for stream-attribution probes only;
  CASES path uses merged-output `classify_process`.
