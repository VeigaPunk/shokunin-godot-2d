# Round 61 — boundary probe: process-tree timeout and startup-margin robustness

## Scope and method

LEAF boundary/revenger seat, scratch-only and report-only. I wrote only this
report and `.shokunin/game-dev-2d/corpus/live/r61-boundary/`. No tracked
fixture, runner, CASES row, lesson, LOG, or SCORECARD entry was touched; no
subagent dispatch; no git mutation.

Method (same discipline as r60): `corpus/live/r61-boundary/drive_probes.py`
`ast.get_source_segment`-extracts `run_process` and `classify_process`
**verbatim** from the tracked `corpus/fixtures/run_battery.py` and `exec`s
them, so classification numbers below are the production code path, not a
reimplementation. Runner sha256 at probe time:
`3bb2904497dfeb774d8d4a9b8c5f8b39ddf1e0ba66bde53599e17eafe3bcec5d`.

**Provenance note — mid-flight sibling diff.** At round start the runner was
`42104d95af5f…` (the r60-verified hash); during this wave the r61 coverage
executor landed the tracked spontaneous-crash move, leaving the working-tree
runner at `3bb29044…` (`git diff`: +2 CASES rows `crash_spontaneous_sigabrt`
exp −6 / `crash_self_sigkill` exp −9, one `expected_errors` allowlist entry
`("ERROR: r60 spontaneous crash probe",)`, one additive meta row
`probe_spontaneous_crash_classification`; also new fixture
`corpus/fixtures/spontaneous_crash_probe.gd`). I verified via the same `ast`
extraction that `run_process`, `classify_process`, `classify_streams`, and
`classify_audio_process` are **byte-identical** between `HEAD:` and the
working tree — the diff is additive-only outside those functions, so my probe
numbers characterize both runner revisions.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Linux `7.2.3-arch1-3 x86_64`, Python `3.14.7`, `RLIMIT_CORE` `[-1,-1]`.

Mechanism read of `run_process` (run_battery.py:140-149): plain
`subprocess.run(command, capture_output=True, text=True, timeout=…)`. No
`start_new_session`/`process_group`, so the Godot child runs in the harness's
own process group; on `TimeoutExpired`, CPython 3.14 POSIX does
`process.kill()` (SIGKILL to the **direct child pid only**) then
`process.wait()` and re-raises — never a process-group signal, never a second
`communicate` drain. `communicate(timeout)` returns only when the child exits
**and** both capture pipes hit EOF.

## Probe A — process-tree timeout (does the harness reap/kill the tree or wait?)

Fixture `proj/tree_probe.gd` prints `TREE_PROBE: expected signature` +
`godot_pid=`, optionally spawns an OS descendant via `OS.create_process`, then
exits 0 or hangs 30s. Driver bound = 3.0s. Tree phase executed twice with
identical arm outcomes; JSON is the second execution (pids from run 2).

| arm | child behavior | descendant | result | elapsed | classify |
|---|---|---|---|---|---|
| clean | exits 0 | none | `exit=0 error=None` | 0.400s | **True** |
| hold | exits 0 (see note) | `sh` inherits pipes; writes pipe line at +1s, file at +7s | **`exit=None error=TIMEOUT after 3.0 seconds`** | 3.003s | **False** |
| detach | exits 0 | `sh` execs `sleep 5; touch file` with stdio→/dev/null | `exit=0 error=None` | 0.396s | **True** |
| hang | hangs 30s | `sh` inherits pipes, file at +5s | `exit=None error=TIMEOUT after 3.0 seconds` | 3.006s | **False** |

Receipts (`tree-probe-verdicts.json`, sha256 `cf328d66…`; raw captures under
`raw/`):

- **hold arm**: the direct child (godot pid 467792) had exited before return —
  proven by `godot_alive_at_return=false` and the descendant's orphaned
  ppid=1573; the ~0.4s exit point is inference from the clean/detach arms'
  elapsed — yet `run_process` returned `TIMEOUT` at
  3.003s — `communicate` was still draining the **descendant-held** pipes.
  Proof: the captured output (`raw/tree-hold.stdout`) contains
  `TREE_DESC_AFTER_PARENT_WRITE`, a line the descendant wrote ~1s *after* its
  parent died. The run reports a timeout for a child that had already exited
  cleanly — a pipe-EOF wait misreported as child-liveness timeout.
- **hang arm**: bound fired while godot (pid 468697) was alive;
  `process.kill()` SIGKILLed the direct child
  (`godot_alive_at_return=false`). Descendant `sh` pid 468735 was
  **alive at return, state `S`, reparented to ppid
  `1573` = `/usr/lib/systemd/systemd --user`** — orphaned, not killed. Its
  file landed 2.501s *after* `run_process` returned. The timeout kill is
  direct-child-only; there is no tree reap or group kill.
- **detach arm**: same outliving descendant, fds detached at exec → pipe EOF
  arrives with the child's exit → clean `True` in 0.396s while the descendant
  was still alive (`alive_at_return=true`, ppid 1573, file landed +5.003s
  after return). Same leak, opposite verdict — the classification hinges
  purely on pipe-fd inheritance, not on descendant lifetime.
- All three descendants survived the full `run_process` call and completed
  their deferred writes (`hold`/`detach`/`hang.descendant-outlived` files
  present; verified `descendant_file_landed=true` with
  `…_delay_after_return_s` 4.503 / 5.003 / 2.501).

**Answer**: the harness neither reaps nor kills the tree — it kills only the
direct child on timeout, and on *any* arm a spawned descendant outlives the
run as an orphan under `systemd --user`. Two consequences for future rows:
(a) a fixture spawning a pipe-inheriting descendant that exits cleanly is
**falsely classified** as timeout (error set, `actual_exit=None`); (b) a
fixture spawning an fd-detached descendant passes cleanly while silently
leaking a process — the battery has no leak detection.

## Probe B — startup-margin robustness (slow start approaching the bound)

Fixture `proj/margin_probe.gd` prints a `start` line, waits
`--delay=<s>` via `create_timer`, prints `MARGIN_PROBE: expected signature`,
exits 0. `run_process` bounds: 8.0s (the CASES default) and 3.0s (the tracked
`--probe-timeout` bound). Full per-run table in
`margin-probe-verdicts.json` (sha256 `f2c677b0…`).

Baseline jitter (delay 0, n=8, bound 8): elapsed **0.357–0.403s**, spread
0.046s — an immediate-exit script uses ~5% of the 8s bound; observed
start-to-exit overhead beyond the delay is ~0.36–0.41s consistently.

Bound-8.0 sweep (elapsed / marker / classify):

| delay | runs | elapsed s | verdict |
|---|---|---|---|
| 5.0 | 1 | 5.385 | True |
| 6.5 | 1 | 6.912 | True |
| 7.0 | 1 | 7.390 | True |
| 7.2 | 3 | 7.556–7.624 | True ×3 |
| 7.3 | 2 | 7.755–7.764 | True ×2 |
| 7.4 | 3 | 7.806–7.900 | True ×3 |
| 7.5 | 2 | 7.907–7.913 | True ×2 |
| **7.6** | 1 | 8.003 | **False — TIMEOUT, marker=True** |
| 8.5 | 1 | 8.012 | **False — TIMEOUT, marker=False** |

Accept/reject knee on this host: delay ∈ (7.5, 7.6]; the last still-accepting
runs sat ~0.09s under the bound. Nuance at 7.6: the signature marker **was**
emitted and captured in the partial output, but teardown ran past the bound →
still `error=TIMEOUT`, `code=None`, classify False. Marker presence does not
rescue a bound-crossing teardown.

Bound-3.0 sweep (the tracked probe's own margin): delay 2.0 → 2.372/2.415s,
2.3 → 2.682/2.725s, 2.45 → 2.797/2.819s, 2.55 → 2.845/2.904s — all True. The
seeded `--delay-clean` arm waits 1.5s (timeout_probe.gd:9) → ~1.9s elapsed by
this host's ~0.4s overhead, leaving ~1.1s headroom under the 3.0 bound; a
hypothetical case completing ~2.9s would sit ~0.1s from rejection — as thin
as the 7.5-delay edge at bound 8.

## Divergences / refined invariants

- Consistent with every prior timeout record (r22/r26: timeout produces
  `error` set + `code=None` → classify False). **Refinement**: on POSIX the
  "timeout" is really a *completion + pipe-drain deadline* — a descendant
  holding inherited stdout/stderr can trigger it with the child already dead.
- Extends the r60 signal-origin caveat: not only is `returncode` origin-blind,
  the *elapsed* is origin-blind too — `TIMEOUT` cannot distinguish
  child-alive-vs-killed from child-dead-but-pipe-held.
- No disagreement with tracked behavior found; nothing probed here requires a
  runner change to *keep* current classifications.

## Recommended next-round candidate rows (report-only, unintegrated)

1. `tree_hang_descendant` meta-row: `--spawn-hang`-style fixture, expected
   `TIMEOUT` + `code=None` + assert direct child dead and descendant **alive**
   — calibrates the documented direct-child-only kill (cheap, zero runner
   change: meta row like the existing probe rows).
2. `tree_clean_hold_descendant` row: clean exit + pipe-holding descendant,
   expected **False/TIMEOUT** — pins the pipe-EOF misattribution as intended
   behavior, or (alternative) flags it as a defect warranting a
   `start_new_session`+group-kill runner change. Intent decision needed;
   either direction is honest.
3. `startup_margin` pair: `--delay=7.0` expected True vs `--delay=8.5`
   expected False/no-marker under the production 8s bound — a tracked
   quantification of the accept band. Optionally a headroom guard assertion
   (edge runs leave ≤0.15s spare; brittle across hosts).
4. Optional runner hardening (larger move, flag for planner): run cases under
   a dedicated process group + `os.killpg`, and/or assert "no surviving
   descendant" as a case-level check — converts the silent leak from (b) into
   detectable signal.

## UNKNOWNs / retained caveats

- Single host, single bound per phase (3.0 tree / 8.0+3.0 margin), n≤3 per
  knee point — knee location is host-timing-specific; expect it to shift a
  few tenths of a second across hosts.
- Orphan reparent target (pid 1573, `systemd --user`) is this session's
  subreaper; other hosts may reparent to pid 1. Survival itself is
  mechanism-guaranteed (no group kill exists in the runner).
- Descendant write at ~7s could block if it exceeded the 64KiB pipe buffer —
  not exercised; post-return pipe output is buffered in the harness process
  and silently discarded at driver exit.
- Not probed: SIGTERM-vs-SIGKILL tree semantics (harness only ever sends
  SIGKILL), exported-build descendants, Windows/macOS semantics, `OS.execute`
  blocking paths, >1 descendant depth.
- First driver execution's `driver.stdout` was overwritten by the tree-only
  re-run (tee); canonical records are the two verdicts JSONs.
- LSP unavailable on this host for `references`/`implementation`; the
  `ast`-verbatim extraction + executed output is the evidence chain, and text
  grep was used only to locate — not to prove — the mechanism.

## Artifact inventory (`.shokunin/game-dev-2d/corpus/live/r61-boundary/`)

- `drive_probes.py` sha256 `773c8c1a…`; `proj/tree_probe.gd` `ceec716e…`;
  `proj/margin_probe.gd` `fefc7860…`; `proj/project.godot` (verbatim copy of
  fixture).
- `tree-probe-verdicts.json` `cf328d66…`; `margin-probe-verdicts.json`
  `f2c677b0…`; raw captures `raw/tree-{clean,hold,detach,hang}.stdout`
  (`7cb99a32…`/`03233ccd…`/`bebed666…`/`878e9392…`); `driver.stdout`
  `600f642a…`; `hold|detach|hang.descendant-outlived` (landed files).

No commit, no tracked-fixture mutation, no LOG/SCORECARD write; integration
of any recommended row belongs to a later executor + named non-author replay.
