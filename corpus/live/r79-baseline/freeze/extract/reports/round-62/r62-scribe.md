# Round 62 scribe — pipe-EOF timeout knowledge entry + LOG draft (host: devin)

Report-only seat. No tracked edits, no Godot runs, no runner execution by this
seat, no commit/push/merge, no delegation. This report carries two drafts for
parent admission: (A) the corpus lesson entry on pipe-EOF timeout semantics —
descendant-held pipes vs child liveness, the no-process-group-kill boundary,
retained UNKNOWNs — and (B) the LOG.md round-62 entry. Scratch receipt:
`corpus/live/r62-scribe/observations.md` (exact commands + observed output).

**State at finalize time** (three `git status` reads): HEAD
`08d80dc0e7a74a6a26c7ed4d50f9fcc5341b95fd`; tracked tree clean apart from
untracked sibling scratch `corpus/live/r62-{author,baseline,boundary,critic,
reviewer,scribe,simplifier}/` (dirs appeared progressively during this draft).
Sibling reports settled: `reports/round-62/r62-baseline.md` — frozen
`git archive HEAD` seven-flag replay **92/92 PASS**, 0 mismatches vs
`corpus/lessons/r61-crash-non-author.json` on the 7-field tuple; and
`reports/round-62/r62-reviewer.md` — fresh 92/92 on committed `08d80dc`
(`corpus/live/r62-reviewer/runs/20261013T233616336304Z/verdicts.json` sha
`053f90bb…`), zero disagreements, plus a provenance nit: `3bb29044…` (the
r61-boundary probe-time runner) = pre-correction working tree; committed
`d705bca7…` = that plus the one-line `crash_meta_ok` marker-presence clause.
The author's tracked CASES/meta edit had **not** landed at observation time —
row names, fixture name, and verdict raw below are `[pending]` slots, and
every settled number quoted is r61-boundary/r62-baseline/r62-reviewer
evidence, not this round's move.

## Baseline read (measured by me, read-only)

- `corpus/fixtures/run_battery.py` sha256
  `d705bca719fcdf24009f2302866ecf8066d49baa2adbc81dbd044c77b3bc5019` — identical
  at HEAD and work commit `b95d180`; 79 CASES rows by `ast`.
- Provenance bridge: `run_process`/`classify_process`/`classify_streams`/
  `classify_audio_process` source segments are byte-identical between the
  r60 runner (`42104d95…`, commit `8aca02e`) and HEAD (`d705bca7…`) — verified
  by me via `ast.get_source_segment` hashing (segment shas
  `88728b23…`/`749fa060…`/`a886968f…`/`3a6bc0e8…` both revisions; my
  `classify_process` prefix `749fa0607e7707e6` matches the r62-reviewer's
  independently extracted full sha
  `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`). The
  r61-boundary probe measured `3bb29044…` — the pre-correction working tree,
  one `crash_meta_ok` line short of committed `d705bca7…` (r62-reviewer
  proved the delta) — with the same classification functions byte-identical
  to `42104d95…` (its own check, `r61-boundary.md` L22-28), so its numbers
  characterize the HEAD runner transitively.
- Env: Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python `3.14.7`, Linux
  `7.2.3-arch1-3` — unchanged across r60/r61/r62-baseline.
- Tracked timeout surface today: `--probe-timeout` three arms only
  (`run_battery.py:913-1001`), all on the direct child; every arm records
  `direct_child_alive_after_cleanup: false`, `bounded_claim` ends "direct
  child cleanup only". No tracked row spawns a pipe-inheriting descendant
  (r62-baseline before-state confirms).

---

## Draft A — lesson entry (proposed slot `corpus/lessons/r62-pipe-eof-timeout.md`; final name/placement is parent's call)

````markdown
# R62 — pipe-EOF timeout: descendant-held pipes vs child liveness (Godot 4.7.2 headless)

Sources: `reports/round-61/r61-boundary.md` + raw
`corpus/live/r61-boundary/tree-probe-verdicts.json` (sha256 `cf328d66…`,
driver = verbatim `ast`-extracted `run_process`/`classify_process`, runner
`3bb29044…` — functions byte-identical to `42104d95…`/`d705bca7…`);
`corpus/live/r61-boundary/raw/tree-{clean,hold,detach,hang}.stdout`;
`corpus/fixtures/run_battery.py` `run_process` (L142-151) /
`classify_process` (L153-170) / `--probe-timeout` (L913-1001);
`corpus/lessons/r22-real-timeout.md`, `r26-timeout-margin.md`,
`r21-signal-exit.md`; tracked-row receipts `[pending: r62 verdicts.json /
non-author raw paths]`.

verified-at: r61 boundary probe `2026-10-13T22:11:58Z`, Godot
`4.7.2.stable.arch_linux.ed1daf0bf`, Python `3.14.7`, Linux `7.2.3-arch1-3`;
mechanism re-verified in source at r62 (`run_process` unchanged since r60).
recheck: (1) at the named r62 non-author replay — tracked rows must reproduce
these classifications in fresh scratch; (2) on any `run_process` rewrite
(`start_new_session`/`os.killpg`, `subprocess.run` → `Popen`, drain policy)
every row in this table must be re-measured — the whole entry is
implementation-bound; (3) on Python version change — the timeout path is
CPython-`subprocess.run` semantics (POSIX: `kill()` direct pid + `wait()`,
no second pipe drain); (4) off this host — reparent target and timing margins
vary.

## What "TIMEOUT" actually is

`run_process` runs `subprocess.run(command, capture_output=True, text=True,
timeout=N)`. `communicate(timeout)` returns only when the child exits **and**
both captured pipes hit EOF. On `TimeoutExpired` CPython POSIX kills the
**direct child pid only** (`process.kill()` → SIGKILL) then `wait()` — never
a process-group signal (`start_new_session` is absent, `os.killpg` is never
called), never a second drain. The runner maps it to
`(partial_output, None, "TIMEOUT after N seconds")`; `classify_process`
rejects because `error` is set and `code is None` — **regardless of marker
presence and regardless of whether the child was alive at the bound**.

So TIMEOUT is a *completion + pipe-drain deadline*, not a child-liveness
verdict. Two consequences, both measured:

1. **False timeout (pipe-EOF misattribution):** a descendant that inherits
   the captured stdout/stderr holds them open past the direct child's death;
   the run still reports `TIMEOUT` + `actual_exit=None` for a child that had
   already exited cleanly.
2. **Silent leak:** an fd-detached descendant produces pipe EOF at the child's
   exit → clean `exit 0` True while the descendant lives on as an orphan.
   The battery has no leak detection; classification hinges purely on pipe-fd
   inheritance, never on descendant lifetime.

## Decision table (four arms, same scratch fixture `tree_probe.gd`, bound 3.0s)

| arm | child behavior | descendant | result | elapsed | classify |
|---|---|---|---|---|---|
| clean | prints marker, exits 0 | none | `exit=0 error=None` | 0.400s | **True** |
| hold (`--spawn-hold`) | prints marker, exits 0 | `sh` inherits pipes; writes pipe line at +1s (after the parent's ~0.4s exit), file at +7s | `exit=None error=TIMEOUT after 3.0 seconds` | 3.003s | **False** |
| detach (`--spawn-detach`) | prints marker, exits 0 | `sh` execs `sleep 5; touch file`, stdio→/dev/null | `exit=0 error=None` | 0.396s | **True** |
| hang (`--spawn-hang`) | hangs 30s | `sh` inherits pipes, file at +5s | `exit=None error=TIMEOUT after 3.0 seconds` | 3.006s | **False** |

Proof the hold-arm timeout is pipe-EOF, not liveness: the direct child (godot
pid 467792) was dead at return (`godot_alive_at_return=false`; its ~0.4s exit
point is inferred from the clean/detach arms' elapsed) — yet the captured
stdout (`raw/tree-hold.stdout`, sha `03233ccd…`) contains
`TREE_DESC_AFTER_PARENT_WRITE`, a line the descendant emitted ~1s after spawn
— after the direct child's ~0.4s exit (exit point inferred from the
clean/detach arms' elapsed). Proof there is no tree reap: in the hang arm the
bound fired with the child alive, `kill()` reached only the direct pid, and
descendant `sh` pid 468735 was alive at return orphaned to ppid 1573
(`systemd --user` — this session's subreaper); all three descendants'
deferred files landed +4.503/+5.003/+2.501s after `run_process` returned.

## The tracked surface this pins `[pending exact row names]`

- Descendant-held-pipe arm under the timeout bound: `actual_exit=None`,
  `error="TIMEOUT after N seconds"`, signature marker present in the *partial*
  captured output, the post-parent-death descendant line captured →
  `classify_process` False.
- Discriminating control on the same fixture: descendant detaches stdio
  (or no descendant) → `actual_exit=0`, `error=None`, classify True —
  child-exit-bound classification returns only when the pipes close.
- Meta discriminations (the class is defined by what must still reject):
  hold-arm captured output reclassified under expected 0 stays False (the
  `error` field rejects independently of signature); a markerless descendant
  arm stays False; control under a wrong expected exit stays False.
- CASES rows cannot express "expected timeout" (a 5-tuple has no expected-
  error field and `classify_process` requires `error is None`), so the
  held-pipe arm belongs to the meta/probe layer; only the accept controls can
  be CASES rows. `[pending: author lands rows; expected shape — additive
  fixture + control CASES row(s) + one meta row]`

## Boundary: no process-group kill exists

Timeout cleanup is direct-child-only SIGKILL. Any fixture spawning a
descendant — pipe-holding **or** detached — leaves that descendant orphaned
(reparented here to `systemd --user` pid 1573; pid 1 on hosts without a
subreaper). Whether the runner *should* run cases under a dedicated process
group + `os.killpg`, or assert "no surviving descendant", is a runner-
hardening policy call flagged for the planner — this entry pins observed
semantics, not preferred ones. A tracked control whose descendant outlives
the run also leaks a real process per battery execution; keep such
descendants short-lived.

## Not established (retained UNKNOWNs — do not soften)

- **Signal origin:** `returncode`/`error` cannot say which signal a descendant
  did or didn't receive, or who sent it; orphan survival is mechanism-guaranteed
  (no group kill exists), not observed per-descendant beyond these arms.
- **Reaping:** descendant reparent target is host-specific (1573 =
  `systemd --user` here); zombie/reap timing after harness exit unprobed.
- Single host, bound 3.0s on these arms (CASES bound is 8s); >1 descendant
  depth, >64KiB descendant pipe writes (blocking write vs drain), `OS.execute`
  blocking paths, exported-build descendants, non-POSIX platforms unprobed.
- Marker presence does not rescue a bound-crossing teardown (r61 boundary
  margin probe: marker emitted at delay 7.6 under bound 8 → still
  `TIMEOUT`/False — startup-knee remains a separate unprobed surface).
````

Draft-A cautions: the "tracked surface" section is a requirements statement,
not a receipt — the author's landed rows and the named non-author replay fill
the `[pending]` slots or this draft is wrong about the outcome and must be
corrected before commit. All measured constants are r61-boundary receipts
transitively valid on HEAD (function-level byte identity verified by me).

---

## Draft B — LOG.md round-62 entry (draft; `[pending]` = fill from settled raw before commit)

```markdown
## Round 62 — 2026-10-13 — coverage (devin host; declared before dispatch)
- Declared move (fleet brief): formalize the r61-boundary tree-timeout
  pipe-EOF misattribution as a tracked classification surface — when a Godot
  child spawns a descendant that inherits and holds the captured stdout/stderr
  pipes, `run_process` waits for pipe EOF until the bound even after the
  direct child exits (timeout misattributed to liveness), and no
  process-group kill exists so descendants orphan. Minimal additive rows only:
  fixture child + pipe-holding descendant, its observed classification under
  the bound, and a discriminating control (detached stdio or no descendant →
  child-exit-bound True). All prior 92 rows field-stable.
- Wave1 (LEAF, no delegation; disjoint reports under `reports/round-62/` and
  scratch under `corpus/live/r62-<seat>/`, sole tracked writer = author):
  eight seats — author, baseline, boundary, critic, reviewer, scout, scribe,
  simplifier. [pending: parent records settled roster and per-seat outcomes]
- Settlement: [pending — baseline receipt already settled: frozen
  `git archive HEAD` (`08d80dc`) seven-flag replay 92/92 PASS at
  `corpus/live/r62-baseline/runs/20261013T233453788036Z/verdicts.json`, 0
  mismatches vs `corpus/lessons/r61-crash-non-author.json`. Expected:
  author's additive fixture + CASES/meta rows (run_battery.py
  `run_process`/`classify_process` byte-unchanged), author's seven-flag run
  NN/NN with all 92 prior rows stable, critic/boundary falsifications
  recorded, named non-author replay + raw copied once to
  `corpus/lessons/r62-<slug>-non-author.json`, fault-injection outer PASS.]
- Per-axis verdict: [pending parent] — declared target coverage; expected
  bounded claim: pipe-EOF-vs-liveness misattribution pinned as observed
  runner semantics (exit-shape/elapsed-shape classification, not liveness or
  tree-reaping detection); depth unchanged; calibration unchanged. Retained
  UNKNOWNs: signal origin, descendant reaping/reparent host-specifics, >1
  depth, 64KiB pipe-buffer blocking, non-POSIX, exported builds. Work commit
  then report-last; no push/merge.
```

Draft-B cautions: wave-roster and settlement bullets are templates — parent
replaces every `[pending]` with settled numbers/commit hashes or omits the
bullet. The only settled r62 fact inside the draft is the baseline 92/92
frozen replay; row counts and verdicts are projections, not observations.

---

## Scribe evidence checklist for the tracked move (status at report time)

- [x] Baseline read by me: runner sha `d705bca7…` (== `b95d180` == HEAD
  `08d80dc`), 79 CASES rows, env identical to r61.
- [x] Function-level byte identity `run_process`/`classify_process`/
  `classify_streams`/`classify_audio_process` across `42104d95…` → `d705bca7…`
  (ast segment-hash match) — r61-boundary probe numbers characterize HEAD.
- [x] r61-boundary raw receipts re-read from `corpus/live/r61-boundary/`
  (verdicts JSON sha `cf328d66…`; hold-arm raw stdout sha `03233ccd…`
  contains `TREE_DESC_AFTER_PARENT_WRITE` post-parent-death line).
- [x] r62-baseline frozen replay receipt: 92/92 PASS, 0 field mismatches vs
  r61 non-author raw; `timeout-verdicts.json` arms all
  `direct_child_alive_after_cleanup: false` ("direct child cleanup only").
- [x] Structural reason recorded for meta-layer placement: CASES 5-tuples
  cannot express an expected-timeout row (`classify_process` requires
  `error is None` + integer `code == expected_exit`).
- [ ] Author's tracked rows landed (`run_battery.py` + new fixture) —
  NOT landed at report time.
- [ ] Author seven-flag run: all 92 prior rows field-stable + new rows PASS.
- [ ] Named non-author replay in fresh scratch + raw copied once to
  `corpus/lessons/`; fault-injection outer PASS.
- [ ] Critic/boundary falsifications recorded (e.g., markerless arm, wrong-
  expected-exit arm, descendant-dead-before-bound arm all still reject).

## Bounded scope of this report

Drafts only — not a PASS, not a verdict, not an admission. I ran no runner and
no Godot; all classification constants are r61-boundary measured receipts plus
my read-only inspection of `run_battery.py`. The lesson draft's semantics stand
on landed runner code paths; its "tracked surface" section is a requirement
statement the parent must reconcile with what actually lands. No commit, no
tracked-file write, no sibling-file write.
