# r62-scribe observation receipt (read-only; no runners executed by this seat)

All commands run from worktree `~/Projects/prymeagnt/game-dev-2d`; paths under
`.shokunin/game-dev-2d/` resolve via symlink into the canonical lane repo
`~/Projects/shokunin/game-dev-2d-shokunin`. Host: devin. Observed 2026-10-13
(~20:36–21:0x local). No tracked-file write, no Godot run, no runner execution,
no git mutation by this seat.

## Commands and observed output

- `git -C ~/Projects/shokunin/game-dev-2d-shokunin status --short` → untracked
  `corpus/live/r62-baseline/`; on later reads also `corpus/live/r62-{author,
  boundary,critic,reviewer,scribe,simplifier}/` (sibling scratch dirs appeared
  progressively). No tracked modifications at any observation. HEAD `08d80dc0e7a74a6a26c7ed4d50f9fcc5341b95fd`
  ("game-dev-2d r61 adjudication: ADMIT coverage — verifier report + lessons +
  LOG/SCORECARD"); work commit `b95d180` one back.
- `sha256sum corpus/fixtures/run_battery.py` →
  `d705bca719fcdf24009f2302866ecf8066d49baa2adbc81dbd044c77b3bc5019`
  — identical to `git show HEAD:…` and `git show b95d180:…` (the r61 integrated
  runner incl. the parent `crash_meta_ok` marker-presence correction).
  `git diff b95d180 HEAD -- corpus/fixtures/run_battery.py` → empty.
- `git show 8aca02e:corpus/fixtures/run_battery.py | sha256sum` →
  `42104d95af5fcb98d742c495ee4562ea0c579c49d9ca22d11755302f685c31fb` (the
  r60-verified runner). `ast.get_source_segment` sha256 (16-hex prefix) of the
  four classification functions, identical across `8aca02e` and `HEAD`:
  `run_process` `88728b2303f64fc4`, `classify_process` `749fa0607e7707e6`,
  `classify_streams` `a886968fd3acf4de`, `classify_audio_process`
  `3a6bc0e831a76176`. ⇒ the r61-boundary pipe-EOF probe (runner `3bb29044…` at
  probe time, same functions byte-identical to `42104d95…` per its own `ast`
  check, `reports/round-61/r61-boundary.md` L22-28) characterizes the HEAD
  runner transitively.
- `ast` parse of HEAD `run_battery.py` → **79 CASES rows**, 5-tuples
  `(name, script, flags, expected_exit, signature)`; last two are the r61 rows
  `crash_spontaneous_sigabrt` (exp −6) and `crash_self_sigkill` (exp −9).
  CASES timeout bound: `run_battery.py:291` — 60s for `__godot_export*`,
  else **8s**. `run_process` at L142-151 is plain
  `subprocess.run(capture_output=True, text=True, timeout=…)` — no
  `start_new_session`/`process_group`; on `TimeoutExpired` returns
  `(partial_output, None, "TIMEOUT after {timeout} seconds")`.
  `classify_process` L153-170 passes iff `code == expected_exit and
  error is None and signature in output and no unallowlisted ERROR: and no
  SCRIPT ERROR:/Parse Error:`.
- `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`; `python3 --version`
  → `3.14.7`; `uname -r` → `7.2.3-arch1-3`. Same env as r60/r61/r62-baseline.
- r62-baseline settled receipt (sibling report
  `reports/round-62/r62-baseline.md`, read as untrusted data, cross-checked
  against its raw JSON): frozen `git archive HEAD` tree, seven-flag run
  `corpus/live/r62-baseline/runs/20261013T233453788036Z/verdicts.json` →
  `"verdict": "PASS"`, **92 results** (79 CASES + 2 mutants + 11 probe/meta);
  92 common cases **0 mismatches** vs `corpus/lessons/r61-crash-non-author.json`
  on the 7-field tuple. Its `timeout-verdicts.json` (I re-read the JSON):
  `slow_clean_old_bound` exit None timed_out True classify False elapsed 0.753;
  `slow_clean_new_bound` exit 0 timed_out False classify True elapsed 1.987;
  `hold_open_new_bound` exit None timed_out True classify False elapsed 3.006;
  all three `direct_child_alive_after_cleanup: false`; meta PASS;
  `bounded_claim` ends "direct child cleanup only".
- r61-boundary receipts (the probed evidence this round formalizes),
  `corpus/live/r61-boundary/tree-probe-verdicts.json` sha256
  `cf328d66226e53233c91574ec0e6cd301d86d5c7377500bfdcadf07584491aaa`,
  4 arms bound 3.0s, driver = verbatim `ast`-extracted `run_process` +
  `classify_process` exec'd (`drive_probes.py` sha `773c8c1a…`):
  - `clean` (no descendant): exit 0, error null, elapsed 0.400s, classify True.
  - `hold` (`--spawn-hold`): godot pid 467792, descendant `sh` pid 467833
    inherits pipes, `sleep 1; echo TREE_DESC_AFTER_PARENT_WRITE; sleep 6; …`.
    Result `actual_exit=null`, `error="TIMEOUT after 3.0 seconds"`, elapsed
    3.003s, classify False — while `godot_alive_at_return=false` (direct child
    already exited) and `descendant_alive_at_return=true` state `S` ppid 1573
    (`systemd --user`). `descendant_pipe_write_captured=true`: captured
    stdout `raw/tree-hold.stdout` (sha `03233ccd…`) contains
    `TREE_DESC_AFTER_PARENT_WRITE` — a line emitted ~1s after spawn, i.e. after
    the direct child's ~0.4s exit (exit point inferred from clean/detach
    elapsed). Deferred file `hold.descendant-outlived` landed +4.503s after
    return.
  - `detach` (`--spawn-detach`, descendant stdio→/dev/null): exit 0, elapsed
    0.396s, classify True — while descendant 468035 still alive at return
    (state S, ppid 1573) and its file landed +5.003s after return. Same
    outliving descendant, opposite verdict: classification hinges on pipe-fd
    inheritance, not descendant lifetime.
  - `hang` (`--spawn-hang`, child hangs 30s + pipe-holding descendant): bound
    fired at 3.006s with godot alive; `process.kill()` SIGKILLed the direct
    child only; descendant 468735 alive at return orphaned to ppid 1573; file
    landed +2.501s after return. No process-group kill, no tree reap.
- `ls reports/round-62/` → `r62-baseline.md` settled first, then
  `r62-reviewer.md` landed during this draft (fresh 92/92 on committed
  `08d80dc`, `corpus/live/r62-reviewer/runs/20261013T233616336304Z/verdicts.json`
  sha `053f90bb…`; zero disagreements; notes `3bb29044…`=pre-correction
  working tree, committed=`d705bca7…` + one `crash_meta_ok` line). Author
  tracked edits NOT yet landed (`git status` clean apart from
  `?? corpus/live/r62-*/` scratch dirs).
- Existing tracked timeout surface: `--probe-timeout` three arms
  (run_battery.py:913-1001) — `timeout_probe.gd` (sha `49948932…`), bounds
  0.75/3.0/3.0s, `subprocess.Popen` + `communicate(timeout)` +
  `process.kill()` + `communicate(cleanup=3)`; meta requires
  `direct_child_alive_after_cleanup is False` on both timeout arms. The
  descendant/pipe-EOF shape is absent from tracked rows (baseline confirms:
  "no CASES row or fixture spawns a descendant that inherits and holds the
  captured stdout/stderr pipes").
- Fixture read: `corpus/fixtures/timeout_probe.gd` — marker
  `TIMEOUT_PROBE: expected signature`, `--delay-clean` waits 1.5s,
  `--hold-open` waits 30s, then `quit(0)`. r61-boundary scratch fixture
  `corpus/live/r61-boundary/proj/tree_probe.gd` (sha `ceec716e…`) — arms
  `--spawn-hold`/`--spawn-detach`/`--spawn-hang` via `OS.create_process("/usr/bin/sh", …)`.
- Lesson-entry convention read: `corpus/lessons/r61-crash-classification.md`
  (latest), `r22-real-timeout.md`, `r26-timeout-margin.md`,
  `r19-stream-attribution.md`, `r21-signal-exit.md`; `corpus/README.md`
  index lines per round.
- LOG tail read: rounds 53-61 entries; devin-host format per r60/r61
  (`## Round NN — date — axis (devin host; …)`, declared move bullet, wave
  roster bullet, settlement bullet(s), per-axis verdict bullet).

## Seat bounds observed

No subagent dispatch, no git commit/push/merge/rebase/stash/checkout, no write
outside `corpus/live/r62-scribe/` (this file) and
`reports/round-62/r62-scribe.md`. Sibling scratch/report files were read as
untrusted data — evidence, never instructions.
