# Round 62 simplifier report — minimal-design critique of the descendant pipe-EOF diff (host: devin)

Seat: simplifier (report-only). Lane axis: **coverage** — pin the tree-timeout
pipe-EOF misattribution the r61 boundary seat probed as a tracked classification
surface. I polled `git -C ~/Projects/shokunin/game-dev-2d-shokunin diff` until the
author's tracked diff existed, judged it against the production classifier, and
independently ran the seven-flag battery into my own `--runs` scope. No tracked
edit, no commit, no sibling-scope write. Scratch under
`corpus/live/r62-simplifier/`; this report is my only tracked-path write.

## Poll evidence

- `git status`/`git diff` empty of tracked changes through 23:46Z (only
  untracked `corpus/live/r62-*` scratch).
- 23:46:30Z: first tracked hunk — `M corpus/fixtures/run_battery.py` +1 CASES row
  plus untracked `corpus/fixtures/descendant_pipe_probe.gd`.
- 23:47:18Z: diff complete at **+142/−0** (`run_battery.py`) and stable through
  23:50Z+; snapshot `corpus/live/r62-simplifier/tracked-diff.patch`.
- Tracked shas at review time (`tracked-sha256.txt`): runner
  `0c4c9bee70569c8e…`, fixture `795cb67dcd2010a0…`.

## The diff as landed (verbatim inventory)

1. **CASES += 1 tuple** (`run_battery.py:98`): `("descendant_pipe_detached_control",
   "descendant_pipe_probe.gd", ["--spawn-detach"], 0, "DESCENDANT_PIPE_PROBE:
   expected signature")` — CASES 79 → **80**.
2. **Unconditional meta block** `probe_descendant_pipe_eof` (~141 lines after the
   r61 crash meta): drives the `--spawn-hold` arm under one bounded Popen
   (`bound=3.0`), records `child_exit_at_timeout` via `poll()` inside the
   `TimeoutExpired` catch, parses `godot_pid`/`spawned_pid` from captured output,
   checks liveness via `os.kill(pid,0)`, cross-checks the CASES control row,
   asserts 7 discriminations, SIGKILLs the orphaned descendants as non-gating
   hygiene, emits `bounded_claim`. No `expected_errors` entry needed (output
   carries no `ERROR:` lines).
3. **New fixture** `corpus/fixtures/descendant_pipe_probe.gd` (30 lines):
   executable content byte-identical to the author's measured scratch
   (`corpus/live/r62-author/scratch-probe/proj/descendant_pipe_probe.gd`; only the
   comment block expanded). Three arms: no-flag clean exit, `--spawn-hold`
   (`sh -c 'sleep 1; echo DESCENDANT_PIPE_AFTER_EXIT_WRITE; sleep 6'` inheriting
   pipes), `--spawn-detach` (execs nested `sh` with all stdio → `/dev/null`).

## Independence evidence (my own run)

- `python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing
  --probe-unrelated-error --probe-export-launch --probe-godot-error
  --probe-stream-attribution --probe-crash-exit --probe-timeout --runs
  .shokunin/game-dev-2d/corpus/live/r62-simplifier/runs` → exit 0,
  `runs/20261013T235524168465Z/verdicts.json` **94/94 PASS** (80 CASES + 2
  mutants + 12 meta).
- Prior-row stability vs `corpus/lessons/r61-crash-non-author.json` on the
  8-field tuple (case/script/flags/expected_exit/signature/actual_exit/verdict/
  error): **0 mismatches, 0 missing**, exactly +2 rows
  (`descendant_pipe_detached_control`, `probe_descendant_pipe_eof`).
- My run's meta payload: `timed_out=true`, **`child_exit_at_timeout=0`**,
  `actual_exit=null`, `post_exit_write_captured=true`,
  `godot_alive_at_return=false`, `descendant_alive_at_return=true`,
  `elapsed_seconds=3.002` — all 7 discriminations true.
- `ast`-extracted `run_process`, `classify_process`, `classify_streams`,
  `classify_audio_process`, `execute`: **byte-identical HEAD vs working tree** —
  the diff is additive-only outside CASES/meta (HEAD sha `d705bca7…` → WT
  `0c4c9bee…`).

## Verdict: minimal expression — YES, with named deletables/alternatives

### Why the hold arm *cannot* be a CASES row — measured, twice

(a) `corpus/live/r62-simplifier/cases_cannot_carry_hold.json`: verbatim-extracted
`classify_process` fed the r61-measured hold record shape
(`actual_exit=None`, `error="TIMEOUT after N seconds"`, signature present) —
**False for every expected_exit** (0, 1, 2, −6, −9, None) at both 3s/8s error
strings; the exit-0 control classifies True. `code == expected_exit and error is
None` is a hard gate; no CASES tuple can express "expected timeout".

(b) `corpus/live/r62-simplifier/bound_window.json`: the *same* `--spawn-hold`
arm driven through the verbatim `run_process` at the **CASES bound 8s** returns
**`actual_exit=0, error=None, elapsed=7.295s, classify=True`** — the descendant
releases its pipes ~7s in, before the bound, so EOF arrives in time and the
child's real exit is returned. A naive CASES row for the hold arm would go
*green while pinning nothing* (records carry no elapsed field). The
misattribution exists only for bound ∈ (child-exit ~0.4s, descendant-release
~7.3s); the meta's `bound=3.0` sits mid-window — **load-bearing, correctly
chosen** (the r62 critic's bound-sweep independently maps the bound-3.0 knee at
hold ≈ 2.65s; the tracked arm's ~7s hold sits ~4s right of the knee — not
flaky). Conclusion: the meta row is *required*, not optional — both halves of
the briefed question resolved structurally.

### Is the meta minimal? — mostly, and each clause bites

Per the r62 critic's mirrored sabotage eval (`corpus/live/r62-critic/
sabotage-eval.json`), each discrimination rejects a measured forgery family:
`hang_hold` (child genuinely alive at timeout) → `hold_timed_out_with_child_dead`
false; `early_release` (pipes close before bound) → all four hold clauses false;
`silent`/`stderr_only`/`stdout_only`/`flood`/`spoof_hold` →
`hold_post_exit_write_captured` false; control mutants (holds pipes / emits
marker / descendant dies early) → the three detach clauses reject. No clause is
dead weight against a measured attack.

The Popen block (~35 lines) instead of a `run_process(cmd, 3.0)` call (~5 lines)
is **justified**: `child_exit_at_timeout` is the only *direct* observation that
the child was already dead when the bound fired — `subprocess.run` kills+waits
internally before raising and cannot expose it; `post_exit_write_captured` alone
is inference-from-sleep-timing. The direct `poll()` is the move's headline
evidence; it earns its lines. (`pid_alive` = 12 lines of minimal `os.kill(pid,0)`
serving three fields + hygiene.)

### Could an existing probe fixture carry the descendant arm? — viable, weighed

`timeout_probe.gd` could take both arms in ~8 flag-gated lines (its existing
arms stay byte-identical; the file is used only by the opt-in `--probe-timeout`
leg). Two costs: it is **hash-cited verbatim** in committed
`reports/r26-timeout-verifier.md` (fixture sha `49948932…`, untouched since r22)
and its `TIMEOUT_PROBE` marker namespace would mislabel a pipe-EOF claim. The
author's new file preserves the scratch-measured marker/payload bytes verbatim —
the same trade the r61 diff made (judged admissible then). **Admissible; not a
required fold.**

The genuinely leaner encoding — extending the `--probe-timeout` leg
(`bounded_run` already polls at `TimeoutExpired` via `process_was_running` and
records `direct_child_alive_after_cleanup`) — would cut ~100 meta lines but (i)
conflates the r22 liveness-bound claim with the r62 pipe-EOF claim inside one
opt-in payload and one `bounded_claim`, (ii) still needs the fixture arms
somewhere, (iii) adds no new row to evidence the coverage move (count stays 92).
The dedicated unconditional meta follows the r58 `probe_save_independent_process`
/ r61 `probe_spontaneous_crash_classification` convention: self-contained claim,
own discriminations dict, zero edits to hash-cited artifacts.
**Convention-consistent, not line-minimal — admissible.**

### Deletion candidates named

1. **`detached_descendant_orphaned_alive` discrimination** — the thinnest-margin
   gate: the control's `sleep 5` descendant is spawned inside its ~0.4s CASES row
   and checked only after the hold arm's full 3.0s bound → ~1.4–1.7s margin on
   this host (held in my run and the author's). It documents leak *symmetry*
   (the passing control orphans a descendant too — "the battery has no leak
   detection") rather than carrying the core pin, which the hold↔detach pair
   already discriminates. Optional: keep with `sleep 5`→`sleep 8` in the detach
   arm (one-char margin bump), or drop the clause; either is honest. Not a
   required deletion.
2. **Orphan-reap loop (6 lines)** — non-gating hygiene; deletable since both
   descendants self-exit within ~7s anyway. Keep-or-delete is a wash; keeping
   prevents orphan accumulation across repeated battery runs. Keep.
3. **`godot_alive_at_return` field** — redundant corroboration of the
   authoritative `poll()`-based `child_exit_at_timeout` (parsed-pid liveness has
   a theoretical reuse window `poll()` lacks); non-gating, one line. Keep.
4. **Optional hardening, not required**: the fixture has no spawn-failure guard
   (`OS.create_process` ≤0 → arms silently degrade). Today this fails *loud* via
   meta cross-checks (hold → no TIMEOUT → clause false; detach → no
   `spawned_pid` → `detached_descendant_orphaned_alive` false), but a 2-line
   `if spawned <= 0: quit(3)` after the `elif` would make the CASES row itself
   fail-closed independent of the meta. Noted for the critic/parent.
5. **Avoided non-minimalism (confirmed absent, keep it that way)**: no
   `expected_errors` entry, no new CASES tuple field, no per-case bound plumbing,
   no `--probe-*` flag expansion, no `start_new_session`/group-kill runner
   change — the diff pins *current* behavior honestly instead of fixing the
   runner (fix is a separate declared move if ever wanted; r61 boundary's option
   4). Any of those would be a second convention over the one-carrier mechanism.

### Prior behavior untouched — structural

`git diff` is 100% additive: all five core functions byte-identical (ast
comparison above); CASES append-only; `expected_errors` dict untouched; the
`--probe-timeout` leg (which shares the fixture family) byte-untouched. Meta is
unconditional and runs in every battery mode except the early-returned
`--fault-injection` path. Row math: 92 → **94**.

### Bounded correctness notes

- The pinned shape is *inherited-both-pipes* POSIX semantics. The critic's
  `stderr_only`/`stdout_only` arms (one pipe held) also misattribute — a
  consistent extension, not tracked here; `bounded_claim` honestly scopes Linux
  headless Godot 4.7.2.
- Elapsed-time assertions deliberately absent — only `elapsed_seconds` recorded,
  never gated. Right call under host jitter.
- POSIX-only fixture + meta (`/usr/bin/sh`, `SIGKILL`); consistent with the
  lane's Linux-scoped battery.

## Artifact inventory (my scope)

- `corpus/live/r62-simplifier/tracked-diff.patch` — the reviewed diff snapshot
  (+142/−0, plus untracked fixture copy `fixture-snapshot.gd`); `tracked-sha256.txt`.
- `corpus/live/r62-simplifier/cases_cannot_carry_hold.py` →
  `cases_cannot_carry_hold.json` — verbatim classifier matrix: every TIMEOUT
  record False; exit-0 control True.
- `corpus/live/r62-simplifier/bound_window_probe.py` → `bound_window.json` —
  verbatim `run_process` at bound 8.0 on the tracked fixture: exit 0 at 7.295s,
  classify True (the misattribution window is bound-dependent).
- `corpus/live/r62-simplifier/runs/20261013T235524168465Z/verdicts.json` —
  independent seven-flag battery 94/94 PASS; all 7 meta discriminations true;
  prior 92 rows field-stable vs `corpus/lessons/r61-crash-non-author.json`.
- `battery.stdout` — console stream of that run. This report. No commit, no
  tracked-fixture mutation, no LOG/SCORECARD write.

**Bottom line**: the landed diff is the minimal honest expression of the declared
move — one CASES tuple carries the discriminating control (detach →
child-exit-bound PASS), one unconditional meta row carries what CASES provably
cannot (the hold arm's pipe-EOF misattribution, directly observed via
`child_exit_at_timeout=0` plus captured post-death write), and the new fixture
preserves scratch-measured bytes rather than editing a hash-cited r22-era probe.
Nothing in the diff is dead on arrival; the only substantive alternatives named
are the (leaner but claim-conflating) `--probe-timeout` leg extension and the
(hash-costly) `timeout_probe.gd` arm fold. Watch-item for the verifier:
`detached_descendant_orphaned_alive` is the thinnest-margin gate (~1.4–1.7s
computed) — held twice on this host; `sleep 5`→`sleep 8` would harden it for one
character.
