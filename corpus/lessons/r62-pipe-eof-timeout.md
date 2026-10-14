# R62 — pipe-EOF timeout: descendant-held pipes vs child liveness (Godot 4.7.2 headless)

Sources: `reports/round-62/r62-{author,scout,critic,reviewer,simplifier,scribe,baseline,boundary,verifier}.md`;
`corpus/fixtures/descendant_pipe_probe.gd` (sha at commit `81a100c`);
`run_battery.py` `run_process` (subprocess.run capture_output+timeout) /
`classify_process` / meta row `probe_descendant_pipe_eof`; named non-author
replay `corpus/live/r62-verifier/runs/20261014T001002305311Z/verdicts.json`
(94/94 PASS) + `corpus/live/r62-verifier/scratch/verifier-drive-verdicts.json`
(kernel-side ppid-flip gate trace).

verified-at: 2026-10-14, Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python
`3.14.7`, Linux `7.2.3-arch1-3`; mechanism re-verified in source at r62
(`run_process` unchanged since r60 — ast-identical `d705bca7…`→`0c4c9bee…`
`main`-only diff).
recheck: (1) on any `run_process` rewrite (`start_new_session`/`os.killpg`,
`subprocess.run`→`Popen`, drain policy) every row here must be re-measured —
the whole entry is implementation-bound; (2) on Python version change —
timeout path is CPython-POSIX semantics (`kill()` direct pid + `wait()`, no
second drain); (3) off this host — reparent target and timing margins vary.

## What "TIMEOUT" actually is

`run_process` runs `subprocess.run(command, capture_output=True, text=True,
timeout=N)`. `communicate(timeout)` returns only when the child exits **and**
both captured pipes hit EOF. On `TimeoutExpired` CPython POSIX kills the
**direct child pid only** (`process.kill()` → SIGKILL) then `wait()` — never
a process-group signal, never a second drain. The runner maps it to
`(partial_output, None, "TIMEOUT after N seconds")`; `classify_process`
rejects because `error` is set and `code is None` — regardless of marker
presence or whether the child was alive at the bound.

TIMEOUT is a *completion + pipe-drain deadline*, not a child-liveness verdict:
`return ≈ min(bound, max(child_exit, last_fd_EOF))` (critic's timeline probe:
child reaped at 0.533s, communicate returned at 3.003s — 2.47s of pure
pipe-EOF wait). Two consequences, both measured:

1. **False timeout (pipe-EOF misattribution):** a descendant that inherits the
   captured pipes holds them open past the direct child's death; the run
   reports `TIMEOUT` + `actual_exit=None` for a child already exited cleanly.
   Holding *either single* captured stream blocks; EOF waits for the *last*
   holder; up to 9,000 post-parent-death lines can land in the TIMEOUT record.
2. **Silent leak:** an fd-detached descendant produces pipe EOF at child exit
   → clean `exit 0` True while the descendant lives on as an orphan.
   Classification hinges on pipe-fd inheritance, never on descendant lifetime.

## Tracked surface (committed `81a100c`)

- Fixture `descendant_pipe_probe.gd`: prints `DESCENDANT_PIPE_PROBE: expected
  signature` + `godot_pid`/`spawned_pid`; arms:
  - `--spawn-hold`: `sh` descendant inherits both captured pipes, writes
    `DESCENDANT_PIPE_AFTER_EXIT_WRITE` only **after its own ppid flips off the
    godot pid** (`/proc/self/stat` field 4 — kernel reparenting is immediate,
    no reap dependency), then holds the pipes ~6s. Provably post-exit write:
    the r62 critic showed a presence-only write at +0.05s is forgeable, and
    the r62 verifier traced `first_pp==godot_pid → release_pp=1573` with the
    gate genuinely waiting 2 iterations in real timing.
  - `--spawn-detach`: descendant execs nested `sh -c 'sleep 8'` with stdio
    →/dev/null — fds detach at exec; sleep 8 sized to keep the orphan-alive
    check's margin (~1.5s at the simplifier's measured knee → ~4.6s after).
- CASES row `descendant_pipe_detached_control` (`--spawn-detach`, expected
  exit 0): the child-exit-bound discriminating control — clean PASS while its
  own descendant silently outlives the run.
- Unconditional meta `probe_descendant_pipe_eof` (+142-line additive block):
  drives the hold arm under one bounded `Popen`/`communicate(timeout=3.0)`
  (a CASES 5-tuple provably cannot carry the arm — `error` set always
  classifies False, and at the CASES 8s bound a naive row would pass-and-delay
  while pinning nothing; 3.0s sits inside the misattribution window:
  child-exit ~0.4s, authored hold ~7s). Seven discriminations, all required:
  `hold_timed_out_with_child_dead` (`poll()` at TimeoutExpired returns 0 —
  load-bearing attribution), `hold_post_exit_write_captured`,
  `hold_misattributed_rejects` (inner classification False),
  `hold_descendant_orphaned_alive`, `detached_case_passes_clean`,
  `detached_lacks_post_exit_write`, `detached_descendant_orphaned_alive`.
  `run_process`/`classify_process`/`classify_streams`/`classify_audio_process`
  byte- and ast-identical to r61.

## Critic falsifications survived / absorbed

- 9 sabotage mutants: 8 reject; the pre-fix slip (early post-exit write,
  ~0.6s ordering margin) was closed at integration by the reparenting gate.
- Bound-exact: TIMEOUT arms 3.003–3.007s; hold knee ∈(2.6,2.7]s at bound 3.0;
  authored ~7s hold has ~4.3s margin (robust).
- Merged-stream signature spoofing works in principle (descendant can emit the
  signature post-death → `classify_process` True in isolation) — the landed
  design avoids it by construction (control descendant detached; hold arm's
  marker ungated). Recorded as a boundary class, not a gate.

## Not established (retained UNKNOWNs)

- **Signal origin:** exit code/`error` cannot say which signal a descendant
  did or didn't receive, or who sent it; orphan survival is mechanism-
  guaranteed (no group kill exists), not per-descendant verified.
- **receipt-level semantics:** `post_exit_write_captured` is a presence check —
  post-exit-ness is carried by the fixture's ppid gate, not provable from the
  receipt alone (verifier documented the stripped-gate forgery yielding an
  identical receipt).
- **reaping/host:** reparent target host-specific (1573 = `systemd --user`
  here); zombie/reap timing after harness exit unprobed; >1 descendant depth,
  >64KiB descendant writes, `OS.execute` blocking paths, exported builds,
  non-POSIX unprobed.
- Startup-margin knee ∈(7.5,7.6]s under CASES bound 8 remains a separate
  unprobed surface (r61 boundary measured; not pinned this round).
- The 3d→2d process-tree port sketch lives at
  `.ufo/waves/shokunin-train-20261013-w2/x-connector.md` — boundary measured
  `killpg` cannot reach `OS.create_process` descendants (each is its own
  session/group leader), so a naive port would not reap this surface;
  `start_new_session`-less killpg would kill the harness's own group.
  Port remains a runner-hardening policy call for a future round.
