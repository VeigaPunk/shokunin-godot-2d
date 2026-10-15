# Round 62 author report — tracked descendant pipe-EOF misattribution surface (host: devin)

Seat: author (role executor), lane `game-dev-2d`, declared axis-move:
**coverage** — formalize the tree-timeout pipe-EOF misattribution the r61
boundary seat probed (`reports/round-61/r61-boundary.md`, recommendation 2) as
a tracked classification surface.

## Scoped move and source

Established at r61 (boundary, re-measured by me below): `run_process`'s
`subprocess.run(capture_output=True, timeout=…)` bound is a completion +
pipe-drain deadline, not a liveness bound. A clean-exiting Godot child whose
spawned OS descendant inherits and holds the captured stdout/stderr pipes is
still reported `TIMEOUT` — `code=None`, `error` set, classify False — and the
timeout kill targets the direct child only, so descendants orphan. r62 lands
that observation as tracked rows: one fixture, one CASES control row, one
meta row. Zero runner-internal change.

## Causal scratch (pre-edit, production code path)

Driver `.shokunin/game-dev-2d/corpus/live/r62-author/scratch-probe/drive_probe.py`
(sha256 `b21873c6…`) `ast.get_source_segment`-extracts `run_process` and
`classify_process` **verbatim** from the pre-edit tracked runner (sha256
`d705bca719fcdf24009f2302866ecf8066d49baa2adbc81dbd044c77b3bc5019`, = HEAD
`08d80dc`, also the r62-baseline frozen hash) — no transcription. Fixture
candidate `scratch-probe/proj/descendant_pipe_probe.gd` (sha `e703a40c…`),
`project.godot` verbatim copy. Receipt
`scratch-probe/descendant-probe-verdicts.json` (sha `c1a342f6…`), raws under
`scratch-probe/raw/`. Bound 3.0s everywhere.

| arm | driver | exit | error | elapsed | classify | key evidence |
|---|---|---|---|---|---|---|
| clean (no descendant) | `run_process` verbatim | 0 | None | 0.363s | True | child-exit bound |
| hold | `run_process` verbatim | None | `TIMEOUT after 3.0 seconds` | 3.002s | **False** | `godot_alive_at_return=false`, `post_exit_write_captured=true`, descendant alive, ppid 1573 (`systemd --user`) |
| hold | `Popen`+communicate | None | `TIMEOUT after 3.0 seconds` | 3.002s | **False** | **`child_exit_at_timeout=0`** — `poll()` at the `TimeoutExpired` catch reaps the already-dead child: the bound fired on pipe EOF with the child gone |
| detach | `run_process` verbatim | 0 | None | 0.382s | **True** | descendant alive at return (silent leak), no post-exit write |

Same mechanism numbers as r61 boundary (its hold arm: TIMEOUT 3.003s,
`godot_alive_at_return=false`, descendant orphaned ppid 1573) — reproduced
independently on the r62 candidate fixture.

## Tracked files changed (this lane's only tracked writes this round)

1. `corpus/fixtures/descendant_pipe_probe.gd` — NEW tracked fixture, sha256
   `795cb67dcd2010a02c4b7bfeb8ff06faade84ef84410341131e3020a25968049`.
   Header comment updated to tracked status; executable content is the
   twice-measured scratch artifact. Arms: (none) → clean `quit(0)`;
   `--spawn-hold` → `OS.create_process("/usr/bin/sh", -c "sleep 1; echo
   DESCENDANT_PIPE_AFTER_EXIT_WRITE; sleep 6")` inherits both pipes;
   `--spawn-detach` → `exec sh -c 'sleep 5' </dev/null >/dev/null 2>&1`
   drops them.
2. `corpus/fixtures/run_battery.py` — **+142/−0**, two additive hunks:
   - CASES +1 row appended at list end (order untouched):
     `("descendant_pipe_detached_control", "descendant_pipe_probe.gd",
     ["--spawn-detach"], 0, "DESCENDANT_PIPE_PROBE: expected signature")`.
   - ONE unconditional meta row `probe_descendant_pipe_eof` after the r61
     crash-meta append: drives the `--spawn-hold` arm under one bounded
     `Popen`/`communicate(timeout=3.0)` (the same pattern `probe_timeout`
     already uses), then asserts seven discriminations. No new flag, no
     CASES-table change, `run_process`/`classify_process` untouched.

   Runner sha256 `d705bca7…` → `0c4c9bee70569c8ec29f98dea89c437d78587fd5c3c7b3220b76140ac59520dd`.

## Why the meta row (why CASES cannot carry the hold arm)

Every CASES row must classify True (`all(r["verdict"] == "PASS")` gates the
battery), and `classify_process` requires `error is None` — a TIMEOUT record
can never be a passing CASES row for any `expected_exit`. The r62 simplifier
proved this independently on the committed runner (`corpus/live/
r62-simplifier/cases_cannot_carry_hold.json`: all error-set records classify
False, control exit-0 True). The `probe_timeout`/`probe_crash_exit`
bounded-Popen pattern is the established surface for arms that must observe
timeout — the meta row follows it.

The meta's seven discriminations (all measured `true` in the run below):

- `hold_timed_out_with_child_dead` — `timed_out=true` AND
  `child_exit_at_timeout=0`: the pinned misattribution.
- `hold_post_exit_write_captured` — `DESCENDANT_PIPE_AFTER_EXIT_WRITE`
  (written ~1s post-spawn, i.e. after the ~0.4s parent exit) appears in the
  captured output: the runner kept draining the descendant-held pipe.
- `hold_misattributed_rejects` — `classify_process(None, "TIMEOUT…", out, 0,
  marker)` → False: the observed classification a CASES row would record.
- `hold_descendant_orphaned_alive` — descendant still alive at return: no
  process-group kill exists.
- `detached_case_passes_clean` — CASES row PASS, exit 0, error None.
- `detached_lacks_post_exit_write` — control output has the marker but no
  post-exit write: only the fd route differs between arms.
- `detached_descendant_orphaned_alive` — the control's own `sleep 5`
  descendant is still alive when the meta runs (~0ms after the last CASES
  row): passes cleanly while silently leaking — the battery has no leak
  detection.

Hygiene: after recording, the meta SIGKILLs both orphaned descendants
(bounded `sleep`s that would self-exit in seconds anyway); harness-side
cleanup only, never a gated verdict.

## Exact evidence

Mandated seven-flag battery (exact invocation):
`python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot
/usr/bin/godot --runs .shokunin/game-dev-2d/corpus/live/r62-author/runs
--probe-failing --probe-unrelated-error --probe-export-launch
--probe-godot-error --probe-stream-attribution --probe-crash-exit
--probe-timeout` → exit 0,
`runs/20261013T234730112013Z/verdicts.json` **PASS, 94/94 rows** (sha256
`f4f65b1a6de91e86c2a4606ae7a5860684eae08aa34e2e80ec1caba6a11074a8`); stdout
`corpus/live/r62-author/battery.stdout` (sha `4048ed26…`): 93 `^PASS` +
exactly 2 designed inner `^FAIL` (`godot_error_unrelated`,
`stream_reject`) + `PASS battery`. Row arithmetic: 80 CASES + 2 mutants +
4 unrelated-error + 8 meta/probe rows (3 unconditional: save-process,
crash, pipe-EOF; 5 opt-in).

Prior-row stability — field-diff vs the r62-baseline frozen-HEAD replay
(`corpus/live/r62-baseline/runs/20261013T233453788036Z/verdicts.json`, same
host, same HEAD `08d80dc`) over `(script, flags, expected_exit, actual_exit,
signature, verdict, error)`: **92 common cases, 0 mismatches**; new-only
`{descendant_pipe_detached_control, probe_descendant_pipe_eof}`;
baseline-not-in-new `[]`.

New rows measured:
- `descendant_pipe_detached_control`: expected/actual `0`, verdict PASS,
  error None; output = banner + marker + `godot_pid=`/`spawned_pid=` — no
  post-exit write.
- `probe_descendant_pipe_eof`: verdict PASS; hold arm `elapsed_seconds
  3.002`, `child_exit_at_timeout 0`, `godot_alive_at_return false`,
  `descendant_alive_at_return true`, `post_exit_write_captured true`,
  `inner_classification false`; all seven discriminations `true`.

Separate leg: `--fault-injection` →
`fault-runs/20261013T234902265100Z/fault-verdicts.json` outer **PASS** (sha
`c4a526f2…`), designed inner hang/unrelated FAILs — unchanged (fault path
returns before CASES/meta by construction).

## Per-axis claimed verdict (author claim; named non-author replay still due)

- **coverage — improved (candidate)**: 0 → 1 tracked descendant-pipe CASES
  control + 1 tracked meta row pinning the pipe-EOF misattribution, the
  post-death pipe drain, and the orphan/no-group-kill surface with a
  discriminating control; 92 → 94 rows, all prior field-stable.
- **calibration — unchanged**: no classifier edit; the meta consumes
  `classify_process` verbatim; prior classifications untouched.
- **depth — unchanged**: no new mechanic surface.

## UNKNOWNs / retained caveats

- Bounded to Linux headless Godot 4.7.2 POSIX pipe semantics; the meta uses
  a 3.0s bound (same as `probe_timeout`) — the pinned mechanism is
  bound-agnostic; the CASES 8s bound would show the same TIMEOUT only if
  the descendant held pipes past 8s (this fixture's hold is ~7s).
- Timing margins: the post-exit write at +1s vs ~0.4s child exit leaves
  ~0.6s ordering margin (observed stable across r61 boundary + r62 scratch
  + battery, n=3 hosts runs each ~3.0s); `detached_descendant_orphaned_alive`
  relies on ~4.5s of descendant sleep remaining when the meta runs —
  generous on this host, noted as host-timing-dependent.
- Orphan reparent target (ppid 1573, `systemd --user`) is this session's
  subreaper; other hosts may reparent to pid 1 — survival itself is
  mechanism-guaranteed.
- Not probed here: SIGTERM-vs-SIGKILL tree semantics, exported-build
  descendants, Windows/macOS, >1 descendant depth, >64KiB pipe-buffer
  descendant writes; signal-origin caveat from r60/r61 retained.
- The pinned misattribution is classification-level only; the runner still
  lacks process-group kill / leak detection (boundary recommendations 2/4
  remain the honest follow-ups — a `start_new_session`+`killpg` hardening or
  a leak-detection check is a planner decision, not this round's scope).

No commit, no push/merge, no LOG/SCORECARD write; adjudication and named
non-author replay follow.
