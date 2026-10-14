# Round 64 — boundary recon: while-live gate edge probes

## Scope and method

LEAF boundary/revenger seat, scratch-only and report-only. I wrote only this
report and `.shokunin/game-dev-2d/corpus/live/r64-boundary/`. No tracked
fixture, runner, CASES row, lesson, LOG, or SCORECARD entry was touched; no
subagent dispatch; no git mutation.

Assignment (lane brief): probe the edges of the r64 author's landed while-live
signature gate — (1) zombie-window race quantified under the runner's
`communicate()` pattern + whether the gate's liveness check lands inside it;
(2) stderr-channel forgery under the gate; (3) the gate under system load
(genuine-arm false-negative risk); (4) a descendant writing the signature
BEFORE parent death while holding pipes (pre-death forge — defeats the gate
by construction; is the fixture able to produce it?).

**Provenance note — mid-flight sibling diff (fourth consecutive round).** At
probe start the working tree already carried the r64 author's landing:
`corpus/fixtures/run_battery.py` sha256 `15ecad36…` (+224 lines, meta row
`probe_while_live_signature_gate` with nested `gated_signature_run`, appended
after the r63 spoof-meta print). During my driver run the author amended it
to `66a18a00…` — verified **comment-only**: the executable shape of
`gated_signature_run` is identical between the two revisions (diffed
non-comment/non-blank lines; the amendment adds the "Load-bearing primitive:
process.poll() (waitpid) — it REAPS the child" comment). Every number below
characterizes the landed gate as now present. Tracked
`descendant_pipe_probe.gd` is byte-stable at `4fce0676…` (HEAD `a7e0cb1`,
r63 admitted). The author's full battery after landing: `PASS` overall incl.
`PASS while-live signature-gate meta`
(`corpus/live/r64-author/runs/20261014T013826495191Z/verdicts.json`); its arm
timings cross-check mine (~65–70ms genuine margin, ~30ms forged-post-death
margin).

Method: `ast.get_source_segment`-extract `run_process`, `classify_process`,
`classify_streams`, `pid_alive`, `kernel_ppid`, and **the landed
`gated_signature_run` itself** from the working-tree runner and exec them —
the verdict rows tagged `vg_*` are the production gate code, not a
transcription. `gated_replica` replicates that loop line-for-line (selectors
over both pipes, 5ms tick, heartbeat `poll()`, per-event `alive_before =
poll() is None` before `os.read`) and adds: a 1ms `/proc/<pid>/stat` +
`os.kill(pid,0)` transition monitor on the direct child, per-stream capture,
`mode="kill0"` (liveness via `os.kill` — never reaps in-loop), and an
injectable pre-loop reader stall. `communicate_replica` mirrors `run_process`
's `subprocess.run(capture_output=True, timeout=…)` consumer (Popen +
`communicate(timeout)`; `TimeoutExpired` → `kill()`+`wait()` per
`subprocess.run`'s POSIX path). All Godot runs sequential. Fixture copies:
`proj_stock/` byte-identical; `proj_edge/` adds scratch-only forge arms
(disclosed; sha `7d778ce0…` vs tracked `4fce0676…`).

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Linux 7.2.3-arch1-3
x86_64, Python `3.14.7` (`/usr/lib/python3.14/subprocess.py` read for the
consumer semantics), 32 CPUs, loadavg ~2.0–2.5, subreaper pid 1573
(`systemd --user`).

Key library evidence (this host's `subprocess.py`): `_communicate`'s select
loop (:2143–2177) drains pipes until dual-EOF and **never calls
`wait()`/`poll()` inside the loop** — the only reap is the post-loop
`self.wait(timeout=remaining)` (:2179) or, on timeout, `subprocess.run`'s
`kill()`+`wait()` handler. `Popen.poll()` → `_internal_poll` →
`waitpid(WNOHANG)` reaps a zombie immediately. `os.kill(pid,0)` succeeds on
an unreaped zombie. These three facts decide probe 1.

## Probe 1 — the zombie window, quantified per consumer

A dead-but-unreaped child satisfies `kill(pid,0)` for as long as the reader
refrains from `waitpid`. The window is entirely determined by WHICH consumer
pattern runs:

| consumer / arm | death→reap (kill0-satisfying zombie window) | evidence |
|---|---|---|
| `communicate()`, `--spawn-forge-hold` ×3 | **2349 / 2416 / 2425 ms** — godot dies ~0.58–0.65s, reaped only at the 3.0s timeout handler | `comm_forge_hold#*`, `edge-timeline.json` |
| `communicate()`, `--spawn-hold` | **2298 ms** (same hold shape, genuine marker) | `comm_spawn_hold` |
| `communicate()`, `--spawn-forge-release` ×3 | **32.7 / 32.9 ms** (+1 monitor-truncated rep) — reap follows the descendant's release→EOF→wait | `comm_forge_release#*` |
| `communicate()`, default arm ×2 | **no Z transition observed** (< ~1ms — EOF and reap are near-atomic when no fd survives) | `comm_default#*` |
| landed poll-gate, all forged/predeath arms | **1.06 – 4.24 ms** (median ~2.1 ms; n=21 observed windows) — the heartbeat `poll()` reaps within ~1–2 ms of death, inside one 5 ms tick | `gp_*`, `stderr_*`, `predeath_*`, `halfhalf_*` |
| kill0-variant gate, `--spawn-forge-release` ×4 | **30.9 – 34.0 ms** — nothing reaps until post-loop `wait()`; the forged marker is read INSIDE the window every rep | `k0_*` |

So the r62/r63 "≥1.1–2 s zombie persistence" observation (descendants under
live godot) has a sharper sibling here: **under the runner's own
`communicate()` path a dead direct child satisfies `kill(pid,0)` for the
entire pipe-drain** — ~2.4 s on hold arms, bounded by `death →
min(bound, last-pipe-close)`. That is the zombie-window answer to the brief:
a hypothetical kill(0)-liveness check inside a drain would call the dead
godot "alive" for seconds.

**Does the gate's check land inside the window?** Never — by construction the
landed check *is* the reap. `process.poll() is None` performs `waitpid
(WNOHANG)`: evaluated at the marker-completing read it can only return alive
for a child the kernel has not finished killing. The forged marker landed
**+29.6 … +34.3 ms after `dead_observed_at`** on every forged rep (n=13:
stdout release/hold, stderr release/hold, load reps) — ~15× the largest
poll-gate zombie window. The only theoretical leak is a `poll()` issued while
the child is mid-`do_exit` (post-reparent, pre-zombie) — a µs-scale window
the fixture's ~50 ms reparent-detect granularity cannot reach.

**The discrimination is primitive-bound, demonstrated on real Godot:** the
same `--spawn-forge-release` bytes under a `kill(pid,0)`-gated read are
**accepted 4/4** (`k0_forge_release#*`: `alive_at_obs=True` with
`state_at_marker_observation="Z"` — the marker was literally read while godot
was an unreaped zombie). Marker read ~33 ms post-death sits inside the ~34 ms
window. Transfers the r64-scout sh-replica finding to the real fixture.

## Probe 2 — stderr-channel forgery under the gate

The gate merges both pipes into `captured` (`captured += chunk` per event), so
a forged `expected signature` on **stderr** enters the identical check. Edge
arm `--spawn-forge-stderr-release`/`-hold` (reparent-gated post-death writes
to fd 2; `marker_stream="stderr"` recorded):

- `stderr_release` ×3, `stderr_hold` ×1 under the landed gate: **all
  rejected**, marker observed post-death at margins +31.5…+31.7 ms —
  indistinguishable from the stdout forge's +31.5…+32.0 ms. **Same
  discrimination, no timing difference**: which pipe carried the forged bytes
  is invisible to the ordering check, and there is no per-stream race to win
  (the completing bytes are post-death either way).
- Triple-axis record per rep: gate False, merged `classify_process` **True**
  (presence still origin- and stream-blind — the r63 boundary preserved),
  `classify_streams` **False** — the stream-aware classifier independently
  rejects a stderr-carried signature regardless of liveness.
- `k0_stderr_release` ×2: the kill0-variant false-accepts on stderr too —
  the failure is at the liveness primitive, channel-independent.

## Probe 3 — the gate under load, and the real falsification knee

**Contention run:** reader (this driver, gate loop included) pinned to cpu0
via `sched_setaffinity`, **24 spinning `sh` hogs pinned to the same cpu0**;
the godot child unpinned (`preexec_fn` reset to all 32 CPUs) — maximal
reader starvation while the child runs free.

- `load_default` ×8: **8/8 accepted while-live**; margins −66.2 … −68.3 ms —
  statistically identical to idle margins (−65 … −68.5 ms). Even at 24:1
  single-core contention the reader's wake latency stayed ≪ the
  marker→exit window; CFS wakeup preemption keeps select-wake latency at ms
  scale.
- `load_forge_release` ×4: 4/4 still rejected (+29.6 … +32.3 ms).
- **No false-negative produced by scheduler contention** on this host.

**Deterministic falsification knee (stall sweep):** injecting a pre-loop
reader stall shows where the genuine arm breaks — the marker is already
sitting buffered in the pipe when godot dies:

| stall | observed | margin |
|---|---|---|
| 0.20 / 0.35 / 0.50 s | accepted while-live | ~−67 ms |
| **0.65 s** | **rejected — post-death** | marker@0.6502 = dead@0.6502 |
| **0.90 s** | **rejected — post-death** | marker@0.9003 = dead@0.9003 |

Measured falsification condition: **reader stall ≥ ~0.6 s post-spawn lands
the first read after godot's exit** (godot's absolute write→exit span here:
marker ~0.33–0.63 s, death ~0.60–0.70 s under current load; the marker's
while-live observability window is the [write, exit] interval ≈ 65–70 ms
wide but it sits ~0.4–0.6 s into the run). This is the falsified genuine rep
the claim admits — produced deterministically, with timing recorded.

## Probe 4 — pre-death forged write (defeats the gate by construction)

**Fixture producibility:** the tracked fixture **cannot** produce a pre-death
forge — both forge arms gate the write on the kernel reparent flip
(`while … ppid == godot_pid; sleep 0.05`), i.e. post-death only. My scratch
edge variant produces it by replacing the reparent gate with a fixed offset
sleep; `write_ppid` read at write time lands as **in-record pre-death
provenance** (`write_ppid == godot_pid`).

**Acceptance knee** (offset sweep under the landed gate semantics):

| offset | write_ppid | gate | margin (marker−death) |
|---|---|---|---|
| 0 / 0.02 / 0.05 ×2 | **= godot_pid (pre-death)** | **accepted 6/6** | −65 … −16 ms |
| 0.07 ×2 | 1573 (post-death) | rejected | **+0.74 / +1.09 ms** |
| ≥0.09 ×2/pt | 1573 | rejected | +21 … +186 ms |

So godot's post-`OS.create_process` live window is ≈ **50–70 ms** on this
host: a descendant forged write landing inside it is accepted
indistinguishably (`gated_signature_accepted=True` AND
`inner_classification=True` — a complete forged PASS), and the flip sits
inside a ~20 ms band around 60 ms. `predeath_hold_0.02` shows the same forged
acceptance inside a `timed_out=True` record (orthogonal error axis
unaffected); `predeath_stderr_0.02` accepts on the stderr channel.
`halfhalf_0.02` ×2 — first half of the marker bytes written pre-death
(`FORGE_HALF1 pp=godot_pid`), reparent gate, then the completing bytes —
**rejected**, margins +0.022 / +4.98 ms: "observed" is the **completing-read
instant**, not first-byte arrival.

## Divergences / refined invariants

- The r64 gate's discrimination is **correct for post-death writes and exact
  about what it measures**: observation-time liveness. The forged-marker
  margin (~+31 ms observed-death→read) is bounded below by the fixture's
  reparent-detect granularity, not by the gate's 5 ms tick — the poll check
  reaps ~1–2 ms after death.
- Zombie-window rule of thumb for this host's `subprocess`: `kill(0)`-visible
  death window ≈ `death → next waitpid-by-anyone`. Under `communicate()` that
  is the whole drain (≤ the timeout bound); under the poll-gate ~1–4 ms.
- The genuine arm's safety margin is a **~65–70 ms** write→exit window on
  this host; the false-negative condition is reader-stall ≳ 0.6 s post-spawn
  (demonstrated), far beyond what 24:1 single-core contention produced.
- The gate is **blind to same-lifetime fd-inherited writes** — a descendant
  writing inside godot's ~50–70 ms post-spawn window forges an accepted
  signature while `write_ppid == godot_pid` proves it pre-death. The tracked
  fixture can't produce it; the edge variant does on demand. This matches —
  and now measures — the author's declared `bounded_claim` exclusion.
- `classify_streams` (stdout-pinning) is an independent rejection axis for
  stderr-carried forgery on both pre- and post-death shapes.

## Recommended next-round candidate surfaces (report-only)

1. **Pre-death forge tracked meta row**: promote a `--spawn-forge-predeath`
  arm (fixed-offset write, `write_ppid==godot_pid` in-record) into the
  fixture + a meta discrimination asserting `gated_signature_accepted=True` —
  pins the gate's *declared* boundary in tracked space rather than leaving it
  a prose caveat.
2. **Stall/margin receipt hardening**: per-arm `marker→death` margin fields
  already exist (`dead_observed_at`, `marker_observed_at`); a meta
  discrimination on `margin > guard` would catch the falsified-genuine shape
  if a slow host ever produces it.
3. **Counter-example meta row**: the kill0-variant gate on
  `--spawn-forge-release` (one-line primitive swap, ~2 extra bounded runs)
  pins *why* poll() is load-bearing — prevents a future refactor to
  `pid_alive`-style checks silently voiding the row.
4. **Mid-exit µs race**: a no-gate forge racing death itself (write between
  reparent and zombie-reapability) is the only residual accept-window for a
  post-death-intent write — unreachable through the fixture's 50 ms gate;
  would need a custom spawner. Note, don't chase.

## UNKNOWNs / retained caveats

- Single host (godot 4.7.2 headless, CPython 3.14.7, 32 CPU, load ~2–2.5):
  the ~50–70 ms post-spawn window, ~65–70 ms genuine margin, and ~31 ms
  forged-write latency all slide with build/load; the *ordering* results do
  not.
- Monitor granularity 1 ms — sub-ms zombie windows (default arm) report as
  "never Z"; consistent with near-atomic reap, not a proof of zero.
- `comm_forge_release#0`: monitor captured Z but missed the final reap
  transition (benign sampling artifact; the sibling reps bound the window).
- Replicas (`gated_replica`, `communicate_replica`, monitor, load/stall
  harness) are corroborating evidence; verdict-path evidence comes from the
  verbatim-extracted production gate (`vg_*` rows) and the author's own
  battery receipt. The kill0 variant's difference is disclosed in-record
  (`gate_mode` field).
- Pre-death offsets are wall-clock sleeps in the descendant's shell — the
  "pre-death" claim rests on `write_ppid == godot_pid` at write time, which
  the record carries.
- `pidfd`, non-POSIX, exported-build and `OS.execute`-path behavior unprobed
  (carried from r61–r63).

## Artifact inventory (`.shokunin/game-dev-2d/corpus/live/r64-boundary/`)

- `drive_edges.py` sha256 `9d86c6cf…` — verbatim-extraction + replica edge
  driver (69 bounded runs across 7 phases).
- `edge-verdicts.json` sha256 `c7ecc824…` — per-run records (all fields
  incl. per-stream classifications, margins, zombie windows).
- `edge-timeline.json` sha256 `4f305092…` — `/proc`+kill0 transition
  timelines per monitored run.
- `proj_stock/` — byte-identical `project.godot` `8de8b3af…` +
  `descendant_pipe_probe.gd` `4fce0676…`.
- `proj_edge/descendant_pipe_probe.gd` sha256 `7d778ce0…` — scratch-only edge
  fixture (stderr / predeath / halfhalf forge arms); tracked file untouched.
- `raw/*.stdout` — merged captured bytes per run.
- `drive.stdout` — driver transcript.

No commit, no tracked mutation, no LOG/SCORECARD write; descendants
SIGKILLed where still alive; `ps` post-check clean; hog pinned set released.
