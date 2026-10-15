# r64 scribe — while-live signature gate: observation log (host: devin)

Seat: scribe (leaf). Own while-live experiments only inside
`corpus/live/r64-scribe/`; no tracked-file writes, no sibling-file writes,
no git mutations. Everything below is verbatim command + observed output.

Env: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python
`3.14.7`, Linux `7.2.3-arch1-3`, `/usr/bin/sh -> bash`.

## Layout

- `drive_whilelive.py` — the gated-read harness (sha256
  `08739b5d2f6ede9d6656503f79e36817142f0787bd678cba51cf4206b0329fa2`).
  `ast.get_source_segment`-extracts `run_process`/`classify_process` verbatim
  from `corpus/fixtures/run_battery.py` (pre-r64 HEAD copy, sha256
  `fb7cab2bb0364bef802cd3ed67892510377b8c45024daa378ca632129d96d7c2` — same
  sha the r64 scout/baseline recorded). Gate: `Popen` + `selectors` +
  `os.read`; on the chunk that first completes
  `DESCENDANT_PIPE_PROBE: expected signature` in the arrival buffer, evaluate
  one of six liveness primitives — `poll` (`proc.poll() is None`, reaping),
  `poll_delay50` (50 ms reader lag before `poll()`), `waitid`
  (`os.waitid(WEXITED|WNOHANG|WNOWAIT) is None`, non-reaping), `procstat`
  (`/proc/<pid>/stat` state field not in `{Z,X}`, non-reaping), `kill0`
  (`os.kill(pid,0)`, zombie-blind), `returncode` (stale `proc.returncode is
  None`, never reaps). A daemon thread samples `/proc/<pid>/stat` every ~1 ms
  to timestamp the real death (first `Z`/`X`/gone) WITHOUT reaping, so
  death-vs-observation deltas are measured independently of the gate.
- `proj/` — two-file scratch Godot project (`project.godot` +
  `descendant_pipe_probe.gd`, byte-copies of the tracked fixture; the
  r62-author minimal-copy convention — the probe needs nothing else).
- `raw/` — per-run captured output (156 files, `<arm>-<gate>-<rep>.stdout`).
- `whilelive-verdicts.json` — full receipt, sha256
  `5ca644252e71b62319dbc2cbcf47b4fcbf9ae5d5d78cf252fb2bf951719803cb`.
- `run-matrix.stdout` — full per-run console log of the matrix run.

## Arms

Synthetic `/usr/bin/sh` children mirror the fixture shapes (`syn_release` /
`syn_hold` use the fixture's own ppid-flip gate — poll `/proc/self/stat`
until ppid != child pid, i.e. provably post-exit — then write the REAL
marker string + `write_ppid=`). `syn_pre_forge` is the blind-side control:
descendant writes at +0.25 s while the child sleeps to 1.5 s (no ppid gate;
`write_ppid` == child pid in-record). Godot arms run the tracked fixture on
`proj/` unmodified: `[]`, `--spawn-detach`, `--spawn-forge-release`,
`--spawn-forge-hold`. Bound 3.0 s everywhere.

## Exact invocations

```
mkdir -p corpus/live/r64-scribe/{proj,raw}
cp corpus/fixtures/project.godot corpus/fixtures/descendant_pipe_probe.gd \
   corpus/live/r64-scribe/proj/
cd corpus/live/r64-scribe
python3 drive_whilelive.py            # full matrix -> whilelive-verdicts.json
```

Smoke test first (3 runs inline) then the full matrix; console log at
`run-matrix.stdout`. Post-run `pgrep -af 'descendant_pipe|sleep 5|sleep 8'`
→ only an unrelated in-flight sibling-critic Godot process; zero leaked
descendants from this seat (all hold/forged descendants SIGKILLed in
harness hygiene, same convention as the tracked meta rows).

## Measured discrimination matrix (156 gated runs)

`gated` = marker observed AND child alive at observation (the while-live
accept); `naive` = verbatim `classify_process` on the same captured bytes;
`cfe` = `classify_if_error_none`; `obs−death` = marker-observation time
minus monitor death time (ms; + = observed after death; ±~1 ms monitor
quantization).

| arm | gate | n | gated accept | marker present | naive classify | cfe | t/o | obs−death ms (min/med/max) |
|---|---|---|---|---|---|---|---|---|
| syn_genuine_fast | poll | 30 | **30** | 30 | 30 | 30 | 0 | −0.743/−0.687/−0.535 |
| syn_genuine_fast | kill0 | 10 | 10 | 10 | 10 | 10 | 0 | −0.691/−0.649/−0.536 |
| syn_genuine_fast | poll_delay50 | 10 | **0** | 10 | 10 | 10 | 0 | −0.687/−0.546/−0.467 |
| syn_genuine_slow | poll | 10 | 10 | 10 | 10 | 10 | 0 | −401.5/−401.0/−400.6 |
| syn_release | poll | 15 | **0** | 15 | 15 | 15 | 0 | +0.032/+0.097/+0.251 |
| syn_release | waitid | 5 | **0** | 5 | 5 | 5 | 0 | +0.011/+0.046/+0.088 |
| syn_release | procstat | 5 | **0** | 5 | 5 | 5 | 0 | +0.010/+0.027/+0.336 |
| syn_release | kill0 | 10 | **10** | 10 | 10 | 10 | 0 | +0.027/+0.078/+0.264 |
| syn_release | returncode | 10 | **10** | 10 | 10 | 10 | 0 | +0.011/+0.176/+0.329 |
| syn_release | poll_delay50 | 5 | **0** | 5 | 5 | 5 | 0 | +0.329/+0.498/+0.616 |
| syn_hold | poll | 3 | **0** | 3 | 0 | 3 | 3 | +0.010/+0.250/+0.383 |
| syn_hold | kill0 | 2 | **2** | 2 | 0 | 2 | 2 | +0.198/+0.507/+0.507 |
| syn_pre_forge | poll | 10 | **10** | 10 | 10 | 10 | 0 | −1250.4/−1249.7/−1249.3 |
| godot_genuine | poll | 5 | 5 | 5 | 5 | 5 | 0 | −69.2/−68.1/−66.8 |
| godot_genuine | kill0 | 3 | 3 | 3 | 3 | 3 | 0 | −67.8/−67.5/−67.4 |
| godot_genuine | poll_delay50 | 3 | 3 | 3 | 3 | 3 | 0 | −68.8/−67.8/−66.7 |
| godot_detach | poll | 2 | 2 | 2 | 2 | 2 | 0 | −70.5/−69.5/−69.5 |
| godot_release | poll | 5 | **0** | 5 | 5 | 5 | 0 | +31.7/+32.6/+33.1 |
| godot_release | procstat | 2 | **0** | 2 | 2 | 2 | 0 | +31.3/+36.7/+36.7 |
| godot_release | kill0 | 3 | **3** | 3 | 3 | 3 | 0 | +32.2/+33.3/+33.9 |
| godot_release | returncode | 3 | **3** | 3 | 3 | 3 | 0 | +32.2/+33.1/+34.2 |
| godot_release | poll_delay50 | 2 | **0** | 2 | 2 | 2 | 0 | +32.4/+33.6/+33.6 |
| godot_hold | poll | 2 | **0** | 2 | 0 | 2 | 2 | +32.6/+33.8/+33.8 |
| godot_hold | kill0 | 1 | **1** | 1 | 0 | 1 | 1 | +33.6 |

Headline: under every sound primitive (poll, waitid-WNOWAIT, procstat,
delayed poll) **0/44 forged observations while-live** (all `obs−death`
strictly positive, min +0.010 ms) and **47/47 genuine observations
while-live** on unlagged gates — deterministic discrimination. Under
zombie-blind primitives (kill0, stale returncode) **29/29 forged markers
accepted** — deterministic NON-discrimination. `cfe` True on every forged
record incl. hold arms (the signature clause alone still accepts the forged
bytes; rejection rides on gate and/or timeout, never on presence).

## Key single records

- `godot_release`/poll rep0 (`raw/godot_release-poll-0.stdout`): marker
  observed 556.388 ms; death (Z) 523.256 ms; `poll()=0` → gated False;
  naive True; `write_ppid=1573` ≠ `godot_pid=1307213`; child_exit 0.
- `godot_release`/kill0 rep0: marker 591.475 ms, dead (Z) since 557.526 ms
  → `kill ok` → gated **True** (forged accepted inside a 34.05 ms zombie
  linger window).
- `godot_hold`/kill0 rep0: gated **True** AND `timed_out` at 3002.9 ms;
  child zombie-lingered ~2493 ms until post-bound reap — the naive
  classifier rejects on the timeout axis while the gate accepted the forged
  bytes.
- `syn_pre_forge`/poll rep0: marker 252.164 ms, `poll()=None`, death
  1502.153 ms → gated True; `write_ppid=1299036` == `WL_CHILD_PID` — a
  provably pre-death descendant write, accepted: the gate detects
  post-death origin, not authorship.
- `syn_genuine_fast`/poll_delay50 rep0: marker observed 0.779 ms (child
  alive then), liveness evaluated +50 ms later → `poll()=0` → gated
  **False** — a genuine signature false-rejected by reader lag ≥ the
  write→death margin (~0.7 ms here, ~67 ms on the Godot fixture).
- `godot_genuine`/poll rep0: marker 484.540 ms, death 551.714 ms
  (`obs−death` −67.174 ms — Godot's post-print teardown margin) → gated
  True.

Zombie-linger measurements (`zombie_linger_ms`): release arms ~0.02–0.4 ms
(syn) / ~31.6–34.9 ms (godot) — always covering the forged-observation
window; hold arms ~2.3–3.0 s (until post-timeout reap); a reap-at-end
reader leaves the child a zombie for the whole session.

## Cross-seat convergence

- Author's landed (uncommitted) meta `probe_while_live_signature_gate`
  (`run_battery.py` +224/−0, poll-gated selectors read, 5 ms tick, 3.0 s
  bound): receipt `corpus/live/r64-author/runs/20261014T013826495191Z/
  verdicts.json` 97/97; its arms — genuine×3 gated True (obs ~0.42–0.52 s,
  dead_obs ~0.49–0.58 s), detach True, forge_release×3 gated False with
  `dead_observed_at` 0.478–0.522 < `marker_observed_at` 0.509–0.553,
  forge_hold gated False + timeout, `write_ppid=1573` —
  `gate_discriminates_forged_from_genuine: true`, all 12 discriminations
  true. My margins agree: author forged gap ≈ 32 ms vs my +31.3…+36.7 ms;
  author genuine margin ≈ 67 ms vs my −66.7…−70.5 ms.
- Scout (`reports/round-64/r64-scout.md`): measured poll() sound (forged
  live-observed 0/5), `os.kill(pid,0)` false-accepts 5/5 (zombie), `/proc`
  bare-existence unsound, `/proc`-state sound-but-redundant; ~65 ms genuine
  margin; ~22 ms dead-before-marker ordering; "write-time provenance
  unobservable reader-side". My waitid/procstat/kill0/returncode columns
  converge; my poll_delay50 + syn_pre_forge arms extend it.
- Reviewer: fresh 96/96 on HEAD `a7e0cb1` + r63 meta re-audit AGREE.
- Baseline: frozen `git archive HEAD` replay 96/96.

## State at finalize (2026-10-14T01:4xZ)

HEAD `a7e0cb1` (r63 adjudication); worktree `M corpus/fixtures/
run_battery.py` (+224/−0 — author's uncommitted meta row); untracked
sibling dirs r64-{author,baseline,critic,reviewer,scout,scribe,simplifier}
and `reports/round-64/` (baseline, reviewer, scout, this scribe report).
Work commit: `[pending]`.
