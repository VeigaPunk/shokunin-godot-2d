# R63 — signature spoof: post-death descendant writes satisfy the merged-capture signature check (Godot 4.7.2 headless)

Sources: `reports/round-63/r63-{scout,author,critic,reviewer,simplifier,
scribe,baseline,boundary}.md`; `corpus/fixtures/descendant_pipe_probe.gd`
forge arms + `run_battery.py` CASES row `descendant_pipe_forged_signature_release`
and meta `probe_descendant_signature_spoof` (sha at commit `de78edb`);
scout verbatim-extraction measurement
`corpus/live/r63-scout/spoof-verdicts.json` (sha256 `6fd32ffe…`); boundary
depth-2/3 extension `corpus/live/r63-boundary/depth-verdicts.json` (sha256
`e85d1918…`); r62 origin measurement `reports/round-62/r62-critic.md`
(spoof arm: child silent of signature, descendant wrote
`PIPE_CRITIC: expected signature` at +0.8s, released ~1.4s →
`exit=0, marker=True, classify_process=True` at 1.749s);
`corpus/lessons/r62-pipe-eof-timeout.md`.

verified-at: 2026-10-14, Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python
`3.14.7`, Linux `7.2.3-arch1-3`; scout arms are `/usr/bin/sh` children under
`ast.get_source_segment`-extracted `run_process`/`classify_process`
(mechanism is POSIX pipe inheritance, not Godot); boundary arms are real
headless Godot children under the same verbatim `run_process`; the tracked
meta row drives the real `descendant_pipe_probe.gd` fixture.
recheck: (1) on any `run_process`/`classify_process` rewrite — the whole
entry is implementation-bound (merged capture, substring presence); (2) if
capture becomes per-stream or per-writer (e.g. `classify_streams`
everywhere, pipes → sockets+forwarder) the forgery surface changes shape;
(3) on Python version change — timeout path is CPython-POSIX semantics;
(4) off this host — reparent target and timing margins vary.

## What the signature check actually is

`run_process` returns `(proc.stdout + proc.stderr, proc.returncode, None)`
— one merged string. `classify_process(code, error, output, expected_exit,
signature, ...)` returns `code == expected_exit and error is None and
signature in output and not unrelated_errors and "SCRIPT ERROR:" not in
output and "Parse Error:" not in output`. The signature term is a
**substring presence test over merged captured bytes**: it asserts "the
expected bytes appeared in captured output before pipe EOF" — never "the
direct child emitted them". Any process that inherits either captured fd
can satisfy it, at any time before that fd's last holder releases —
including after the direct child's death. There is no writer tag: the
kernel does not label pipe bytes with provenance, and the runner keeps no
per-writer channel.

## Post-death signature acceptance (measured)

Two shapes, both measured (scout verbatim extraction, bound 3.0s; `/usr/bin/sh`
children printing `SPOOF_CHILD_PID`/`SPOOF_DESC_PID` but never the signature;
descendant ppid-gated so the signature write is provably post-exit):

| arm | child | descendant | record | classify |
|---|---|---|---|---|
| genuine | prints signature, exits 0 | none | exit0, sig present | **True** |
| spoof_release | exits 0, signature withheld | writes signature post-death, then **releases pipes before the bound** | exit0, error None, sig present, elapsed 0.002s | **True — forged clean PASS** |
| spoof_hold | exits 0, signature withheld | writes signature post-death, holds pipes past bound | TIMEOUT 3.002s, exit None, sig present | False, **`classify_if_error_none`=True** |
| spoof_hold_popen | same under Popen+communicate replica | same | timed_out=True, `child_exit_at_timeout=0`, sig present, elapsed 3.004s | inner False, `classify_if_error_none`=True |

`classify_if_error_none` is the load-bearing datum on the hold arms:
evaluating the *same captured bytes* with `error` cleared classifies True —
the signature clause accepted the forged line; the rejection rides entirely
on the timeout/error axis. Depth generalization (boundary, real Godot
children): `d2_spoof` — a depth-2 grandchild writes the signature post-death
while the godot child suppresses it → exit0, classify **True** at 1.524s;
`d2_spoof_hold` → TIMEOUT 3.003s with forged signature captured, False.

## Which record fields carry attribution

On a **CASES verdict record** (`case, script, flags, command,
xdg_data_home, expected_exit, actual_exit, signature, verdict, error,
output`) — **none**. `signature` echoes the expected string, not its
origin; `output` is arrival-ordered merged lines. A forged release-record
and the genuine `descendant_pipe_detached_control` record are equal on
every classification-visible field (meta discrimination
`release_shape_matches_genuine`).

Attribution exists **only at the meta layer**, and it is exactly the
child-death/timeout evidence the r62 row introduced plus the r63 in-band
provenance line: `timed_out` and `child_exit_at_timeout` (`poll()` inside
the `TimeoutExpired` catch — 0 = bound fired on pipe EOF with the child
already dead by exit; None = child alive at bound, dead by kill),
`write_ppid` (`DESCENDANT_PIPE_FORGE write_ppid=<ppid>` — the descendant's
post-reparent ppid; `!= godot_pid` is in-record post-orphan provenance),
`godot_pid`/`descendant_pid`, `godot_alive_at_return`/
`descendant_alive_at_return`, `marker_observed`, `inner_classification`,
`elapsed_seconds`. Discrimination summary: hold shape — the record is
distinguishable from a genuine signature PASS **only** via `timed_out` +
`child_exit_at_timeout` (signature presence itself accepts); release shape
— **no** verdict-record field distinguishes it; only meta provenance
(child's `child_signature=withheld` banner, `write_ppid`, spawned-pid
identity) exposes the forgery.

## Tracked surface (landed author diff, commit `[pending]`)

- Fixture `descendant_pipe_probe.gd` +31/−1: arms `--spawn-forge-hold` /
  `--spawn-forge-release`. On either the child prints
  `DESCENDANT_PIPE_FORGE child_signature=withheld` instead of MARKER, so
  any captured `DESCENDANT_PIPE_PROBE: expected signature` is provably
  descendant-authored. The descendant reuses the `/proc/self/stat`
  ppid-flip gate (provably post-exit write), then echoes the expected
  signature + `write_ppid=<ppid>`; `-hold` appends `sleep 6` (holds both
  pipes ~6s), `-release` exits at once.
- CASES row `descendant_pipe_forged_signature_release`
  (`--spawn-forge-release`, expected exit 0, signature MARKER): **the
  tracked known-accepting forgery row** — a PASS whose signature is
  provably the descendant's post-death write. Author receipt
  (`runs/20261014T004113548836Z/verdicts.json`): `verdict PASS,
  actual_exit 0, error null`, captured output shows
  `child_signature=withheld`, `godot_pid=1071156`, `spawned_pid=1071195`,
  the forged signature, `write_ppid=1573`.
- Unconditional meta `probe_descendant_signature_spoof` (+155-line additive
  block, mode `bounded_popen_plus_cases_forgery_row`): drives the
  `--spawn-forge-hold` arm under one bounded `Popen`/`communicate
  (timeout=3.0)`. Eight discriminations, all required and all observed true
  in the author receipt: `hold_timed_out_with_child_dead`
  (`child_exit_at_timeout==0` — the pinned child-death attribution),
  `hold_forged_signature_captured`, `hold_write_post_orphan`,
  `hold_rejects_via_timeout_axis_only`, `hold_descendant_orphaned_alive`,
  `release_row_passes_on_forged_signature`, `release_write_post_orphan`,
  `release_shape_matches_genuine`. Orphaned descendants SIGKILLed as
  ungated harness hygiene. `run_process`/`classify_process`/
  `classify_streams`/`classify_audio_process` untouched.
- 94/94 → 96/96 under seven flags (+1 CASES, +1 meta); prior-row
  field-stability receipt `[pending non-author replay]`.

## The documented forgery-accepting boundary

This round **pins, not fixes**: the forged-PASS row is admitted to the
tracked corpus as a *known-accepting* row — `bounded_claim`: "signature
presence over merged captured output is origin-blind ... documented
forgery-accepting boundary, not a fix; Linux headless Godot 4.7.2 POSIX
pipe semantics only". Fixing is a runner redesign, not a clause change:
merged pipes are fd-inherited, the kernel does not tag writer origin, and
any presence check over merged output is origin-blind by construction —
even `classify_streams` (signature-on-stdout) would be forged by a
descendant holding stdout alone. Practical rule for future rows: **never
let a signature assertion rest on output from a child that may spawn
pipe-inheriting descendants**; if it must, the row needs meta-layer
child-death/timeout evidence to distinguish, and a release-before-bound
shape remains unverifiable on the verdict record alone.

## Critic falsifications survived / absorbed `[pending r63-critic report]`

Attack surface named in the critic brief: (a) the release arm somehow
guarded (child-liveness pre-check — none exists in `run_process`), (b)
stdout-vs-stderr stream placement (merged string — either stream
satisfies), (c) pipe-buffering ordering making the write land pre-death in
the record (ppid gate + `write_ppid` address ordering at fixture level;
the bytes themselves cannot show it), (d) `child_exit_at_timeout`
forgeability. `[pending]` — fill from the settled report.

## Not established (retained UNKNOWNs — do not soften)

- **Write ordering in bytes:** merged output is arrival-ordered; a
  pre-death vs post-death write is indistinguishable from the record
  alone. Post-exit-ness is carried by the fixture's ppid gate +
  `write_ppid`, i.e. fixture-side semantics — a stripped-gate mutant
  produces an identical-looking receipt (the r62 verifier documented this
  for `post_exit_write_captured`; it applies identically to `write_ppid`).
- **Stream origin:** which of stdout/stderr carried the forged line is
  unobservable in `classify_process` records (scout wrote to stdout; a
  stderr-only write would merge identically).
- **Bound-relative distinguishability:** the same `--spawn-forge-hold` arm
  under the 8s CASES bound releases at ~7s and forges a clean PASS
  (fixture comment); the TIMEOUT distinguishing shape is an artifact of
  the 3.0s meta bound, not of the arm.
- **`child_exit_at_timeout` precision:** it cannot date the death (exit at
  0.4s vs 2.99s read identically); sub-ms `poll()` race at the deadline.
- **Killed-child variant:** child alive at bound + descendant signature
  write (spoof+hang composite) untested — expected same outer record as
  `hang_hold` plus signature present.
- **Depth ≥2:** scratch-measured only (`d2_spoof` True, `d2_spoof_hold`
  False, `d3_hold` blocks EOF) — untracked.
- **Wider surfaces:** >64KiB descendant writes (blocking-write vs drain),
  `OS.execute` blocking paths, exported builds, non-POSIX platforms,
  `classify_streams` stdout-only spoof arm (origin-blindness holds
  per-stream by construction, unmeasured), startup-margin knee ∈(7.5,7.6]s
  under the 8s bound (boundary probed it this round in scratch — retained
  unless landed).
