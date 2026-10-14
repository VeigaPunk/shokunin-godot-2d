# Round 60 non-author verifier report — spontaneous-crash calibration probe (host: devin)

Independent replay of `r60-author.md`. I did not author round 60; all runs below
are fresh executions by me. No commit, no tracked fixture/runner edit, no
LOG/SCORECARD write, no verdict marking. All artifacts under
`corpus/live/r60-verifier/` (untracked scratch) plus this report.

## Environment (matches author exactly)

- Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Linux
  `7.2.3-arch1-3 x86_64` (plazir27), Python `3.14.7`, `RLIMIT_CORE` unlimited
  (`[-1,-1]`, same as author's recorded value).
- `corpus/fixtures/run_battery.py` sha256
  `42104d95af5fcb98d742c495ee4562ea0c579c49d9ca22d11755302f685c31fb` —
  byte-identical to the author's claimed runner hash (r59 verifier's too).
- Author artifact hashes verified against the report's claimed prefixes:
  `verdicts.json` `9905553c…`, `full.stdout` `1c68d6ab…`,
  `fault-verdicts.json` `57f2dca0…`, `spontaneous-crash-verdicts.json`
  `9694988b…`, `drive_probe.py` `689e004b…`, `spontaneous_crash_probe.gd`
  `16e31617…` — all match.

## Runs executed

1. **Seven-flag battery replay (fresh run dir `corpus/live/r60-verifier/battery`).**
   Exact invocation, only `--runs` differs:
   `python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot
   --runs .shokunin/game-dev-2d/corpus/live/r60-verifier/battery --probe-failing
   --probe-unrelated-error --probe-export-launch --probe-godot-error
   --probe-stream-attribution --probe-crash-exit --probe-timeout` →
   `battery/20261013T165543975131Z/verdicts.json` **PASS, 89/89 rows**
   (77 CASES + 2 mutants + 10 probe/meta rows = 89; author's "78 ordinary"
   lumping counts the save-process meta row with CASES — consistent).
   stdout saved `corpus/live/r60-verifier/battery.stdout`; sorted-diff vs
   author's `full.stdout` is identical modulo run-dir paths (88 `^PASS` lines,
   2 designed inner `^FAIL` lines `godot_error_unrelated`/`stream_reject`,
   final `PASS battery`).
2. **Fault-injection leg (fresh `--runs corpus/live/r60-verifier/fault`).**
   `fault/20261013T165549045604Z/fault-verdicts.json` → outer **PASS**;
   `fault_hang` FAIL `TIMEOUT after 0.25 seconds`, `fault_clean_expected_negative`
   PASS exit 2, `fault_unrelated_error` FAIL exit 2 — structurally identical to
   author's `57f2dca0…` (same verdicts/errors/outputs; elapsed 0.251 vs 0.252).
3. **Spontaneous-crash probe re-derived, not replayed.** Wrote my own driver
   `corpus/live/r60-verifier/scratch-probe/verify_probe.py` that independently
   `ast.get_source_segment`-extracts nested `run_process` + `classify_process`
   from `run_battery.py` (extraction succeeded → both defs exist verbatim at the
   claimed sha) and execs them — no transcription, no reuse of `drive_probe.py`.
   Ran all four arms against a scratch copy of the author's `proj/`
   (`spontaneous_crash_probe.gd` unmodified). Result JSON:
   `scratch-probe/verifier-spontaneous-crash-verdicts.json`, per-arm raw
   `verifier_*.stdout`.

## Measured results (mine vs author)

| arm | author exit | mine exit | author class(exp=1) | mine | stderr shape |
|---|---|---|---|---|---|
| accept (no flag) | 1 | 1 | True | **True** | none, marker on stdout |
| `OS.crash` a | -6 SIGABRT | **-6** | False | **False** | `ERROR: r60 spontaneous crash probe` + `at: crash (core/core_bind.cpp:349)` + GDScript bt `spontaneous_crash_probe.gd:15` + `handle_crash: Program crashed with signal 4` + C++ bt |
| `OS.crash` b | -6 SIGABRT | **-6** | False | **False** | same shape |
| `OS.kill(self)` | -9 SIGKILL | **-9** | False | **False** | empty stderr, marker on stdout |

Supplemental classifications (author claimed, I measured on my own captures):
- sigkill arm with `expected_exit=-9` → **True** unmodified (author: True).
- crash arm with `expected_exit=-6` → **False** (own `ERROR:` line is an
  unallowlisted unrelated error); → **True** with
  `allowed_errors=("ERROR: r60 spontaneous crash probe",)` (author: True).
  So zero runner changes needed for a SIGKILL-expected row; one allowlist entry
  for the `OS.crash` row. Confirmed.
- SIGILL-in-handler nuance confirmed: stderr says `signal 4`, parent-visible
  returncode is `-6` on both crash runs (deterministic ×2).
- No `core.*` artifact in either scratch dir despite `timeout` reporting
  "dumped core" — systemd coredump path; consistent with author's note
  (bash micro-measure `crash.*`/`sigkill.*` show 134/137 shapes; I read them,
  did not re-run — setup telemetry only).

## Per-row agreement

- My 89 rows vs author's `20261013T164941106461Z` on
  `(script, flags, expected_exit, actual_exit, signature, verdict, error)`:
  **89 common cases, 0 mismatches** (probe/meta rows carry only `verdict` among
  the tuple fields; both sides PASS).
- My 89 rows vs `corpus/lessons/r59-audio-non-author.json` same tuple:
  **0 mismatches** — the r59 baseline replays byte-exact on this host under a
  second independent runner execution.
- Opt-in artifact verdicts, mine vs author: `crash-exit-verdicts.json`,
  `timeout-verdicts.json`, `godot-error-verdicts.json`,
  `stream-attribution-verdicts.json`, `export-launch-verdicts.json`,
  `save-process-verdicts.json` — all **PASS** on both.

## Disagreements

**None.** Every numeric claim in `r60-author.md` reproduces: 89/89 PASS, 0
field deltas vs r59, fault-injection outer PASS with designed inner FAILs,
probe meta-PASS shape, exit codes -6/-9, classifier outcomes, and the
allowlist nuance.

## UNKNOWNs / retained caveats (verifier-added, consistent with author's)

- Signal *origin* remains unprovable from `returncode` alone — self-SIGKILL vs
  external SIGKILL is indistinguishable; `OS.crash` attribution rests on its
  own `ERROR:`+backtrace output, not syscall evidence.
- My probe ran the same 4 arms in the same order on the same host; cross-host
  determinism of `-6` (SIGILL→handler→SIGABRT) is untested by me.
- `command`, `scratch`, `xdg_data_home`, `artifact` paths, `pid`s,
  `elapsed_seconds`, and export `sha256`s differ between runs (fresh run dir,
  fresh processes, rebuilt export) — expected; the claimed byte-compare scope
  is the 7-field verdict tuple, which holds.
- Not measured here: process-tree/descendant timeout cleanup, startup margin,
  exported-build crash behavior, non-SIGABRT/SIGKILL signals, core capture.
- Read-only review only; author artifacts untouched (verified by hash prefix
  match above).
