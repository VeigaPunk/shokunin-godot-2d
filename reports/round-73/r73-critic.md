# game-dev-2d round 73 — critic (pre-landing attack on the r73 claim + diff)

Seat: critic | Lane: g2d | Round: 73 | Wave `shokunin-train-20261101-w13`.
Host: devin — CPython **3.14.7** (`/usr/bin/python3`), pygame 2.6.1 (SDL
2.32.72), **node v24.21.0**
(`/run/user/1000/fnm_multishells/651042_1791991115990/bin/node`),
`F_GETPIPE_SZ = 65536`, `io.DEFAULT_BUFFER_SIZE = 131072`,
`PYTHONUNBUFFERED` unset, 32 cores.

**Audit snapshot 2026-10-14T15:23–15:35Z — no r73 tracked artifact landed.**
`git rev-parse HEAD` → `2dd108b` (r72 report-last); tracked fixtures at the
r72 hashes (probe `7c0f9c73…`, battery `077af0b5…`); `git status` shows no
`corpus/fixtures` delta; `reports/round-73/` holds the scout report only.
The concrete design under attack is therefore the brief
(`.ufo/waves/shokunin-train-20261101-w13/tasks/g2d-author.md:1-39`), the
r72 machinery it says to reuse (`corpus/fixtures/pygame_probe.py:193-217`
`reorder_arm`; `pygame_battery.py:54,147-164,237-256` — r72 revision; after
the landing the RAW_CASES list is at `:193-211` and the raw-wire block at
`:303-366`), and the xconnector
X4/X1 text (`.ufo/waves/shokunin-train-20261101-w12/xconnector.md:58-63`).
Sibling pre-measurement (`reports/round-73/r73-scout.md`) was read and is
cross-checked below.

**Author diff landed 15:34–15:36Z; replayed 15:36–15:39Z.** Replayed
revision: probe `9a7456a3…` (+165/-0, insertion-only), battery
`6d3fbf5f…` (+146/-17: the 17 removed lines are the r72 classifier block,
no CASES row removed); hashes unchanged through the replay. Replay
receipts under `corpus/live/r73-critic/replay/`. The pre-landing findings
F1–F5 below are kept with a **landed-diff status** line each; the replay
verdict is in §Replay.

**Scope.** Scratch-only + this report: wrote only
`corpus/live/r73-critic/` (probes, receipts, scratch *copies* of the
tracked probe/battery for the battery-level replay) and this file. No
tracked file touched, no git mutation, no subagent dispatch. Every probe
ran under `timeout -s KILL`; every stray process was reaped (receipts in
the JSONs; `detach_battery/grandchild.pid` self-terminated via its alarm).

**`lsp` disclosure.** No `lsp` device on this host (as prior g2d seats
recorded). All evidence below is process-level measurement + textual
`file:line` citations.

## Verdict summary

| # | finding | severity | impacted axes | pre-landing status | landed-diff status |
|---|---|---|---|---|---|
| F1 | DETACH cell through the reused `reorder_arm` fallback **hangs**; the battery-level symptom is a whole-battery FAIL with **all 55 cases PASS** and no case-level signal; the daemonized holder survives the runner's kill | **HIGH** | verdict integrity, harness integrity, evidence sufficiency | briefed guarantee falsified; correction measured | **avoided by design** (own-wire cell, `timeout -s KILL 4` self-bound); stuck path verified 79/80 + `det_wire_eof` FAIL in 13.1 s, no hang; latent unbounded drain remains in two helpers |
| F2 | Node `>64KB` offset is a **reader-race bimodal** {65536, 131072}, not the byte-exact 65536; the infix class is set by the **spawn API's loop-blocking**, not by node's stdio mode (`execSync` infix 10/10, `cp.spawn` splice 10/10) | **HIGH** | calibration (wrong variable), verdict integrity (flaky pin / wrong-sign port) | prediction confirmed for the execSync shape only; attribution corrected | **folded** (band `(40000,199000)` + measured modes in the code comment; 65541 ×4 reps); residual: no async-spawn control, no write-order key |
| F3 | `execSync` provenance trap: default `stdio:'pipe'` → child bytes never on the wire (scout N1); the **re-emission variant is byte-identical to a true small-write splice** → a naive implementation lands a PASS with false provenance | **HIGH** | false provenance, verdict integrity | measured; pin requirement stated | **avoided** (`stdio:'inherit'` in all three node cells); residual: the trap is not pinned as a negative-control row |
| F4 | INFIX: the offset is a **flush-epoch constant** (126005 / 252005 / 0), not a ±1-chunk jitter band; the class is a **race** — an owner stall flips the same cell to prefix 3/3; the implicit epochs are the textio/BufferedWriter law, not "paced" | **MED-HIGH** | calibration, verdict integrity (false FAIL / non-discriminating pin) | pin form falsified; witness-gated + explicit-flush correction measured | **superseded**: landed cell is positional (fill-flush, no sleeps) → 126011 ×4 reps; infix class added to the classifier; residual: absolute `head_at` band couples to upstream byte count |
| F5 | FD2-INVERSION: with one marker text the fd1-child and fd2-merged-child wires are **byte-identical** → the wire cannot attribute the cell; r72's `fd2mrg` shape is **capture-configuration-dependent** (`stderr=STDOUT` driver vs the battery's `capture_output`) | **MED** | duplicate authority, provenance | measured; metadata pin required | **folded**: probe-side `dup2(1,2)` + distinct `FD2-*` markers + `merge=fd2_dup2_to_fd1` receipt; a dropped dup fails loudly (`markers_missing`) |
| F6 | Replay of the landed diff: prior-row stability, hazard greps H1–H9, regime control, stuck-detach, node-absent gate | INFO | — | recipe armed | **executed** — see §Replay |

The scout's pre-measurement is corroborated on every overlapping cell
(infix flush law incl. INJ@126005; detach hold; node edge 65536/65537;
`execSync` stdio trap). F1/F2/F4/F5 are where the *pin form* the brief asks for does not survive
as worded; each carries the measured correction, and the landed diff
folds or supersedes all four.

## F1 — HIGH: the DETACH cell's "bounded timeout" does not bound anything

The brief says the detach cell must be "bounded timeout so a stuck detach
= measured FAIL not hang", and to route the arm through the r72 machinery.
The r72 vehicle is `pygame_probe.py:193-217`; its fallback is:

```
try:
    data, _ = proc.communicate(timeout=CHILD_TIMEOUT_S)
except subprocess.TimeoutExpired:
    proc.kill()
    data, _ = proc.communicate()          # pygame_probe.py:205-206 — UNBOUNDED
```

A double-forked descendant (`setsid`) survives `proc.kill()` (which signals
only the direct child), so the unbounded drain never reaches EOF. Measured
with a detaching child holding fd1 for 600 s (`hang_shape.py`, outer
`timeout -s KILL 8`):

| variant | result | elapsed | grandchild |
|---|---|---|---|
| `r72_shape` (bounded wait + unbounded drain) | **KILLED by outer bound, exit 137 — HANG** | >8 s | alive |
| `pgroup_kill` (`start_new_session` + `killpg`) | **KILLED, exit 137 — HANG** (the grandchild's own `setsid()` escapes the group) | >8 s | alive |
| `bounded_drain` (second bounded drain) | returned | 1.4 s | alive (needs explicit reap) |
| `self_bounded` (grandchild `signal.alarm`) | returned, empty drain, no stray | 1.01 s | dead |

Receipts: `hang_shape_r72_shape.json`, `hang_shape_pgroup_kill.json`,
`hang_shape_bounded_drain.json`, `hang_shape_self_bounded.json`.

**Battery-level replay on the tracked machinery** (scratch copies only:
`corpus/live/r73-critic/detach_battery/{pygame_probe.py,pygame_battery.py}`,
probe = tracked bytes + a 23-line insertion-only detach cell emitting
`PYGAME-ARM detach | hold_ms=35000 parent_rc=0`, HOLD=35 s):

```
python3 pygame_battery.py --runs runs-detach      # exit 1, 30.1 s
totals: cases=55 pass=55 fail=0 launch_ok=False done_marker=True exit=None
FAIL battery: runs-detach/pygame-20261014T152540747903Z/verdicts.json
```

`verdicts.json` fields: `probe_exit=None`,
`probe_error='TIMEOUT after 30 seconds'`, `probe_elapsed_s=30.02`,
`done_marker=True`, `totals={cases:55, pass:55, fail:0}`, `verdict='FAIL'`.
The probe's own stdout (`probe.stdout.txt:19-20`) contains
`PYGAME-ARM detach | hold_ms=35000 parent_rc=0` **followed by**
`PYGAME_PROBE_DONE`: the probe exited cleanly with every byte captured; the
battery FAILs only because `subprocess.run(timeout=30)`
(`pygame_battery.py:147-164`, `TIMEOUT_S=30` at `:54`) cannot see EOF, and
`launch_ok` (`:219`) / the final verdict (`:267`) never consult the detach
arm. The holder (pid recorded in `grandchild.pid`) was **still alive after
the battery returned**; it self-terminated only because my scratch cell
gave it `alarm(40)`. The battery's kill reaches neither the holder nor its
session.

**Smallest safe correction.** (1) Never wire a detach cell through
`reorder_arm`'s fallback: the drain after `kill()` must itself be bounded
(and the second `TimeoutExpired` recorded as the cell's receipt, not
raised). (2) The holder must **self-bound** (`signal.alarm(HOLD+slack)`) —
this is the only bound that survives `setsid` (process-group kill does
not). (3) The probe must record the holder's pid (pidfile/handshake) and
reap it at cell end. (4) The battery-side pin should be
`probe_elapsed_s >= hold_ms` + `probe_exit == 0` + `done_marker` (the
machinery already records `probe_elapsed_s` at `pygame_battery.py:214`);
a stuck-detach (>30 s) cell belongs in an opt-in scratch invocation, not in
the default battery run — otherwise one cell converts a 55/55 PASS battery
into a FAIL with no case-level diagnosis.

**Semantic note (over-strong wording).** "Battery EOF arrives late" is the
weaker half of the hazard. The measured stronger half: a late write by the
detached holder lands **after** the probe's done marker in the same capture
(`detach_eof.json` → `raw_hold1.5_late`: `HEAD  TAIL\nPYGAME_PROBE_DONE\nDETACHED-LATE\n`;
scout `setsid_late_marker` agrees). A consumer that treats
`PYGAME_PROBE_DONE` as "stream complete" sees post-exit injected bytes; the
pin should carry that cell, not only the EOF delay.

**Landed-diff status (replayed).** The landed detach cell is an *own-wire*
cell — the probe never drains its own stdout, so the F1 hang path is not
reachable from it: it spawns the holder as a direct child with
`start_new_session=True` and `timeout -s KILL 4` (`pygame_probe.py:485-502`),
emits `hold_ms=900 kill_bound_s=4`, and spawns it **last** so the 900 ms
sleep straddles the exit edge. Measured: default battery 80/80 PASS with
`probe_elapsed_s` 8.92 s (r72) → 9.85 s (r73, +0.93 s ≈ the hold; the
EOF-lateness is visible in the battery's own wall-clock key); the stuck
variant (holder `sleep 60`, scratch copy `replay/stuck_detach/`) → battery
returns in 13.1 s with **79/80 PASS, `det_wire_eof` FAIL (`markers_missing`),
no stray** — the docstring's "stuck detach … measured FAIL, never a hang"
is now **verified**, not asserted. Residual (LOW): the unbounded post-kill
drain still exists at `pygame_probe.py:234-237` (`reorder_arm`) and
`:299-302` (`node_arm`); any *future* cell that routes a pipe-holding
descendant through those helpers re-opens the hang. One-line guard: bound
the second drain too and treat a second `TimeoutExpired` as the receipt.

## F2 — HIGH: node's >64KB offset is a reader race, and the class belongs to the spawn API

Brief prediction: "node >64KB single write -> INFIX (partial fill +
event-loop queue remainder = third withholding layer beyond
libc/Python)"; scout §4 pins "INJ at **exactly 65536** (pipe capacity)".

Measured (`node_census.py`, `node_census_edges.py`; node as the fd1 owner,
`printf` child spawned with `stdio:['ignore','inherit','inherit']`,
`execSync`):

| cell | INJ offset, per rep | class |
|---|---|---|
| `big65536` (write == cap) | 65536, 65536, 65536 | splice (full payload before child) |
| `big65537` (+1 byte) | 65536, 65536, 65536 | infix (1-byte queued remainder, stable) |
| `big200k` ×10 | **131072 ×6, 65536 ×4** | infix 10/10 |
| `big200k` slow/fast reader | 131072, 65536, 131072 / 65536, 65536, 131072, 131072, 131072 | infix |
| `big200k_async` (`cp.spawn`, 5 reps) | **200000 ×5** | **splice** |
| `big200k_async_slowchild` (5 reps) | **200000 ×5** | **splice** |
| `writesync_small` / `writesync_200k` | 5 / 200000 ×3 | splice (write-through control) |

Mechanism (measured, not cited): a pipe is capacity-bounded
(`F_GETPIPE_SZ=65536`); libuv's write path loops while a syscall succeeds
and queues the remainder on `EAGAIN`. Whether the *next* 65536 goes out
before the child's write depends on whether the **reader drained the pipe
inside that loop** — my select-loop reader (65536-byte reads) wins that
race ~60% of the time; the scout's heavier per-round reader loses it. Both
readings are honest; the consequence is that `INJ at exactly 65536` is a
**reader-timing artifact**, and a future runner with a different read
pattern lands 131072 and fails an exact-offset pin. The *class* (infix) is
stable (10/10), and so is the mechanism.

The second, larger result: with `cp.spawn` instead of `execSync`, the same
owner/write/child yields **splice 10/10** — the queued remainder drains
while the child is forked/exec'd, before its `INJ`. So the "third
withholding layer" is **not** node's stdio mode (the r72 referent); it is
the composition *pipe capacity × libuv EAGAIN queue × a synchronous spawn
that blocks the event loop*. The brief's cell shape (`execSync`) is
load-bearing for the prediction; the async sibling is the control that
names the variable.

**Smallest safe correction.** Pin `topology=infix` **plus** the write-order
witness (`first delivery < C-WRITE < remainder delivery`); pin the offset
as a **set/band** `{pipe_capacity, 2×pipe_capacity}` (or `[65536, 131072]`)
with `pipe_capacity=65536` carried as a provenance key (same convention as
`bufsize`); add the `cp.spawn` control cell (expected splice) so a port
that keeps node but changes the spawn API lands a measured difference
rather than a silent wrong-sign. Do not pin a single exact offset.

**Landed-diff status (replayed).** Folded: the landed row is
`nbig_inj_bound (40000.0, 199000.0)` with the measured modes
(`65536/69637/131072`) named in the code comment — my two modes and the
scout's third all sit inside; observed 65541 ×4 reps, class `infix` ×4.
The viability gate is real and measured: a PATH-restricted run
(`PATH=/usr/bin:/bin`) emits `node_present=False`,
`topology=blocked_node_absent` on all three arms, no fabricated wire, 65/80
PASS with exactly the 15 node rows failing (honest). Residuals: (a) the
node receipt has no write-order key, so the *class* pin carries the claim
alone; (b) no `cp.spawn` control row, so the mechanism sentence ("blocked
by execSync", now in the docstring) is the only guard against a port
switching to an async spawn and getting an unexplained class FAIL;
(c) on a node-absent host the battery verdict is FAIL, not "blocked" — the
brief's "bounded blocked verdict" is met at the arm level, not the verdict
level.

## F3 — HIGH: the `execSync` trap has a byte-identical false-PASS variant

Scout N1 already measured the literal brief shape
(`execSync('printf INJECTED')` → default `stdio:'pipe'` → `INJ` absent from
the wire; my `node_census_edges`/`node_census` reproduce the class). The
stronger variant is the natural "fix" an author reaches for:
`const out = execSync(cmd); process.stdout.write(out)` — measured wire
`HEAD INJECTED TAIL\n` (`inj_at=5`, `wire_bytes=19`), **byte-identical to
the true inherited-fd1 small-write cell** (`small_w`, same order/length,
3/3 each; `node_census.json`). The seam (fd inheritance) is not exercised
at all: the bytes are node's own second write. A pin built on this shape
passes while attributing a same-process double-write to the spawn seam —
false provenance, and exactly the failure the r72 critic F1 fixed for the
owner-mode referent.

**Smallest safe correction.** `stdio:['ignore','inherit','inherit']` is
mandatory; the receipt must carry the witness (`C-WRITE` before/after the
owner's HEAD delivery) and a `child_stdio=inherit` provenance key; add the
`execSync`-default cell as a **negative control** whose expected verdict is
`markers_missing` (scout) so the trap is pinned, not just avoided.

**Landed-diff status (replayed).** Avoided: all three landed node cells
pass `{stdio:'inherit'}` (`pygame_probe.py:262-280`), and the re-emission
variant is not used. Residual (LOW): the trap is not pinned as a
negative-control row — the wave's own convention elsewhere is to pin the
hazard (r72 `self_wire_reorders`, r73 `det_wire_eof`); one extra cell
(`execsync` default → expect `markers_missing`) would make the trap
evidence rather than an implementation detail.

## F4 — MED-HIGH: the infix pin as briefed is the wrong instrument

Brief: "Pin bounded ranges (topology class + offset bounds ±1 chunk),
never exact offsets."

Measured (`paced_infix.py`, H=5, 300×1000 B chunks paced 1 ms, child
write-through at sleep s):

| cell | reps | class | INJ offset |
|---|---|---|---|
| `implicit_s150` | 6 | infix | **126005 ×6** |
| `implicit_s150_load` (32 spinners) | 4 | infix | 126005 ×4 |
| `implicit_s020` (child before flush1) | 2 | **prefix** | 0 |
| `implicit_s280` (child after flush2) | 2 | infix | **252005 ×2** |
| `implicit_s150_ownerstall` (SIGSTOP owner 0.25 s at chunk 30) | 3 | **prefix 3/3** | 0 |
| `explicit_flush` (flush() at chunk 100 and 200, child 0.15) | 3 | infix | **101005 ×3** |

Three facts follow.

1. **The offset is a flush-epoch constant, not a jitter band.** Within the
   (flush1, flush2) window it is byte-exact 126005 (matching the scout's
   law `H + B·floor((131072−H)/B)`, B=9000, and r72-boundary's `paced2`);
   across windows it takes the discrete values {0, 126005, 252005} — a
   swing of 126000 B = 126 chunks. A "±1 chunk" band around a nominal
   describes the *pacing* jitter, not the observable; it is only
   meaningful once the *epoch* is pinned (i.e. with the witness).
2. **The class is a race, not a shape.** The same declared cell flips to
   `prefix_reorder` when the owner stalls asymmetrically (3/3 measured):
   the byte-driven flush epoch slides past the child's fixed sleep, so the
   child's bytes hit an empty pipe first. A class pin without the
   write-order witness turns a host stall (GC pause, page fault, scheduler
   preemption of the owner) into a wrong-sign FAIL, and loosening the
   bound to accept it destroys the prefix/infix discrimination.
   (Symmetric load — 32 spinners — did *not* flip it: 4/4 infix, margin
   preserved ~13–16 ms; the asymmetric case is the real hazard.)
3. **"Paced-flush owner" misnames the mechanism.** The implicit epochs are
   the textio/BufferedWriter batch law (scout §1.1, source-read), not a
   paced flush; they depend on this build's 8192/131072 constants. The
   explicit-flush variant is deterministic (101005, 3/3) and **stable
   under 32-spinner load** (101005 ×3, epochs ~129/~235 ms, child ~182–186 ms;
   `infix_classifier.json`), removes the race dependence on the
   131072/8192 law, and is the portable form.

Also: the battery's raw classifier (`pygame_battery.py:237-248`) cannot
express infix — `h<i<t → midline_splice` (scout §1.4 measured
`classifier_demo`; my byte-exact wire
`HEAD `+`C`×300000+` TAIL\n` with `INJ@126005`, 300014 B, through the same
predicate → `midline_splice` while the witness
`flush1 150.7 < C-WRITE 164.7 < flush2 283.4` says infix;
`infix_classifier.json`). A raw pin that reuses this predicate labels a
measured infix wire `midline_splice`: a FAIL if the author pins `infix`,
or a wrong-name PASS if they pin `midline_splice`. The infix class must be
added with a delivery/write-order key, or pinned as an offset-epoch
constant *plus* the witness.

**Smallest safe correction.** Prefer the explicit-flush owner (epochs by
construction) and pin: `topology=infix` ∧ `flush1_ms < c_write_ms <
flush2_ms` ∧ `inj_at ∈ [flush_prefix−1 chunk, flush_prefix+1 chunk]`; when
the witness shows a missed window, record `window_missed` (with the
measured cause) rather than FAIL.

**Landed-diff status (replayed).** Superseded by a better design: the
landed cell is **positional, not timed** (`pygame_probe.py:432-448`:
`INFIX-HEAD\n` + 140×1000 B + `os.system(printf INFIX-INJ)` + 60×1000 B +
`INFIX-TAIL\n`, no sleeps) — the fill-flush epoch is a byte-count event,
so the infix shape cannot be lost to a stall (my F4 race is not reachable
for this cell). Measured `infx_wire_topo_injected_rel = 126011` ×4 reps
(1 replay + 3 stability) and `tail_rel = 200020`, both inside the pinned
bands; the classifier gained an `infix` class (`min(gap_pre, gap_post) >
64`, `pygame_battery.py:308` `raw_topo3`) with relative offsets — this folds
the scout's §1.4 wrong-sign finding (the r72 row still reports
`midline_splice` in the unbuffered regime, verified below). Residuals:
(a) the absolute `head_at ∈ (1500, 2600)` band is a *placement* pin over
the whole-run prefix — it shifts if any upstream arm's output length
changes (LOW; the two `*_rel` pins carry the evidence, the band could be
dropped or widened); (b) the >64 B gap heuristic is a shape test, fine for
this positional cell but not a write-order witness; (c) on a ≤3.13 build
(8192 buffer) the fill-flush prefix collapses to ~11 B and the row would
classify `midline_splice` — `infx_bufsize=131072` pins the build, same
convention as the other `bufsize` rows (SHARED guard applies).

## F5 — MED: the fd2-inversion cell is byte-indistinguishable from the fd1 cell

Brief: "descendant writes fd2 while fd2 merges into the same capture
(2>&1) — r72-boundary fd2mrg measured `ERR\nHEAD  TAIL\n`. Pin the merge
topology cell."

Measured (`fd2_merge.py`, `fd2_driver_config.json`):

| cell | fd1 wire | battery-shape stdout |
|---|---|---|
| `fd2_child_merged` (descendant `stderr=STDOUT`, writes fd2) | `CHILD-MARKER\nHEAD  TAIL\n` | `CHILD-MARKER\nHEAD  TAIL\n` |
| `fd1_child` (descendant writes fd1) | `CHILD-MARKER\nHEAD  TAIL\n` | `CHILD-MARKER\nHEAD  TAIL\n` |
| `fd2_child_unmerged` (descendant fd2 inherited separately) | `HEAD  TAIL\n` | `HEAD  TAIL\n` (marker on **stderr**) |

With one marker text the two cells are **byte-identical** — the wire
cannot attribute "fd2-inversion"; only the spawn dup + the child's write
path can. And the r72 shape itself is capture-configuration-dependent:
`ERR\nHEAD  TAIL\n` appears only with a **merged driver**
(`stderr=subprocess.STDOUT`); through the battery's exact path
(`capture_output=True`, `pygame_battery.py:155-157`) the same program
yields stdout `HEAD  TAIL\n` + stderr `ERR\n`. Since `RAW_CASES`
(`:140-142`, `:237-256`) judge `stdout` only, an fd2 cell wired without a
probe-side dup measures nothing — the same trap as F3, one layer down.

**Smallest safe correction.** The probe must spawn the descendant with
`stderr=subprocess.STDOUT` (the probe-side 2>&1), and the receipt must
carry `child_write_fd=2` / `merged=true` keys so the cell is attributable;
keep the fd1 sibling as the paired discriminator (same marker text, same
capture), otherwise the new cell is a duplicate authority over the r72
fd1 cell.

**Landed-diff status (replayed).** Folded, via the probe-level variant:
the probe `dup2(1, 2)`s its own fd2 onto the capture, runs the descendant,
then restores fd2 in a `finally` (`pygame_probe.py:449-465`), with distinct
`FD2-HEAD/FD2-ERR/FD2-TAIL` markers and a `merge=fd2_dup2_to_fd1` receipt
key; measured `prefix_reorder` ×4 reps. The failure mode is loud: if the
dup were dropped, `FD2-ERR` would land on the battery's stderr pipe and the
row would report `markers_missing` → FAIL. Residual (LOW): the cell is
regime-scoped (under an unbuffered probe the wire is `midline_splice`,
measured in the `-u` control) — the `fd2m_piped` row records the pipe
regime, matching the r72 `self_fd1_piped` convention; the claim text should
say so.

## Replay of the landed diff (2026-10-14T15:36–15:39Z)

Replayed revision: probe `9a7456a3…` (+165/-0), battery `6d3fbf5f…`
(+146/-17, classifier block only); hashes stable through the replay.
Receipts: `replay/audit.txt`, `replay/battery.txt`,
`replay/runs/pygame-20261014T153649901806Z/verdicts.json`,
`replay2.json`, `replay/runs-rep{0,1,2}/`, `replay/stuck_detach/`,
`replay/runs-nodeabsent/`, `replay/runs-unbuf/`.

| check | result |
|---|---|
| H1 diff shape | probe **insertion-only** (+165/-0); battery removes only the r72 classifier block (17 lines), **no CASES row removed**; `git diff -U0 \| grep '^-'` shows no prior-row line |
| H2 battery | **80/80 PASS, launch_ok=True, done_marker=True, exit=0** (`replay/battery.txt`); ×3 stability reps identical |
| H3 prior rows | all **55/55** prior cases present and PASS; only *timing* keys moved (c60_*, c0_*, popen_*, wh*_ within their pinned bounds); byte-order/structural keys byte-identical to the r72 receipt `corpus/live/runs/pygame-20261014T144544784421Z/verdicts.json` |
| H4 node cells | `node_present=True`, `node_version=v24.21.0`; `nsm/nsy` = midline_splice; `nbig` = infix with `injected_at` 65541 ×4 reps inside `(40000,199000)`; `stdio:'inherit'` present; PATH-restricted run → `blocked_node_absent` on all three arms, no fabricated wire |
| H5 infix cell | `infx_wire_topo=infix`, `injected_rel=126011` ×4, `tail_rel=200020`; classifier now has the infix class; `infx_bufsize=131072` pins the build constant |
| H6 fd2 cell | `fd2m_wire_topo=prefix_reorder` ×4; `merge=fd2_dup2_to_fd1` receipt; fd2 restored (later arms unaffected: 80/80) |
| H7 detach cell | `det_wire_eof=eof_hold` ×4; `probe_elapsed_s` +0.93 s ≈ `hold_ms`; **stuck variant** (holder sleep 60) → 13.1 s, 79/80, `det_wire_eof FAIL (markers_missing)`, no stray, no hang |
| H8 regime control | probe forced `-u` (`--python replay/pyu_wrapper.sh`) → **77/80**, failing exactly the three regime-scoped raw rows (`self_wire_reorders` midline_splice, `fd2m_wire_topo` midline_splice, `infx_wire_topo_injected_rel` outside its band) — no unexpected failure, and the r72 row's label is unchanged (`midline_splice`, same as the old classifier) |
| H9 hazard greps | `pygame_probe.py:234-237` and `:299-302` still hold the unbounded post-kill `communicate()` (latent, not reachable from the landed cells — F1 residual) |

**Replay verdict: no reject.** The landed diff resolves or folds F1–F5 at
the level of the *pinned evidence*; the remaining items are LOW residuals
(helper-drain guard, `head_at` placement band, node async-spawn control,
node-absent verdict class, fd2 regime note) and none of them falsifies a
landed claim. One pre-registered item remains open by construction: the
`head_at` band and the `nbig` class pin are *this-build/this-runner*
quantities (SHARED guard) — carry them as such.

## Residual actions for the author (smallest safe corrections, post-replay)

Ordered by value; none blocks the landing (all LOW):

1. **Bound the second drain** at `pygame_probe.py:234-237` / `:299-302`
   (treat a second `TimeoutExpired` as the receipt) — closes the F1 hang
   class for any future cell with a pipe-holding descendant.
2. **Pin the harness-integrity row**: `probe_elapsed_s >= hold_ms/1000`
   (+ slack) — the machinery already records `probe_elapsed_s`
   (`pygame_battery.py:283`, payload key `:384`); measured +0.93 s for `hold_ms=900`. This
   makes the detach cell's *observable* a pinned key instead of an
   incidental wall-time.
3. **`head_at` band** (`infx_wire_topo_head_at`) — drop or widen it; the
   two `*_rel` pins carry the evidence and the absolute offset is coupled
   to the whole-run prefix length.
4. **Node async-spawn control** (`cp.spawn` instead of `execSync`, expected
   `splice`, my 10/10) — names the loop-blocking variable so a port cannot
   silently change the mechanism.
5. **`execSync`-default negative control** (expected `markers_missing`) —
   pins the F3 trap as evidence.
6. **Claim-text scopes**: node's "third withholding layer" = pipe capacity
   × libuv EAGAIN queue × **execSync blocking the loop** (not "node
   buffers"); the infix/fd2 rows are pipe+block-buffered-regime scoped
   (like `self_fd1_piped`); the `head_at`/`nbig` class pins are
   this-build/this-runner quantities.

## Over-strong claim audit (wording scopes for the landed claim)

- "node ... third withholding layer **beyond libc/Python**" — true only for
  writes > pipe capacity (65536 here) **and** a synchronous loop-blocking
  spawn; with `cp.spawn` the layer is unobservable (splice 10/10). The
  landed docstring already names `execSync` — keep that word.
- "capture EOF arrives late" — the load-bearing hazard is the **late write
  landing in the same capture after the parent's done marker**
  (`DETACH-LATE` after `PYGAME_PROBE_DONE`, pinned as `det_wire_eof`);
  EOF delay alone is a harness-timing artifact (F1).
- "bounded timeout ... measured FAIL not hang" — true **for the landed
  design** (self-bound holder + no probe-side drain of its own stdout);
  verified by the stuck variant. It was false for the reused
  `reorder_arm` fallback (F1) — that guard stays.
- "paced-flush owner" — the landed cell is positional (fill-flush), not
  paced; the implicit epochs are the 8192/131072 batch law.
- The infix offset is a **flush-epoch constant** on this build
  (`H + B·floor((131072−H)/B)`, B = chunk·ceil(8192/chunk)); `8192`,
  `131072`, `65536` are this-host/this-build constants (SHARED guard).
- Byte order alone is not a fabrication witness (r72 F2); the landed cells
  each construct the write order (spawn mid-sequence) or carry the
  offset-epoch structure — keep the construction when porting.

## Reproduce

```
cd corpus/live/r73-critic
python3 node_census.py                     # 8 cells × 3 reps, exit 0 (~0.9 s)
python3 node_census_edges.py               # bimodality + async control, exit 0
python3 paced_infix.py                     # infix/prefix/epoch cells, exit 0 (~8 s)
python3 infix_classifier.py                # tracked predicate vs infix wire, exit 0
python3 detach_eof.py                      # raw + battery-shaped detach, exit 0 (~5 s)
python3 -c 'import detach_eof as d; import json; print(d.run_battery(35.0, timeout=30.0))'   # 30 s masking receipt
python3 fd2_merge.py                       # merge provenance, exit 0
for v in r72_shape bounded_drain pgroup_kill self_bounded; do timeout -s KILL 8 python3 hang_shape.py $v; echo "$v exit=$?"; done
cd detach_battery && timeout -s KILL 120 python3 pygame_battery.py --runs runs-detach; echo "battery exit=$?"   # pre-landing masking receipt
cd .. && ./replay.sh                       # landed diff: audit + 80/80 battery
python3 replay2.py                         # stability ×3 + stuck-detach + node-absent
timeout -s KILL 120 python3 corpus/fixtures/pygame_battery.py --python "$PWD/corpus/live/r73-critic/replay/pyu_wrapper.sh" --runs corpus/live/r73-critic/replay/runs-unbuf   # regime control (77/80)
```

## Artifact inventory (`corpus/live/r73-critic/`)

- `node_census.{py,json}` — node owner census, 8 cells × 3 reps.
- `node_census_edges.{py,json}` — bimodality (10 reps), slow/fast reader,
  async-spawn controls.
- `paced_infix.{py,json}` — implicit/explicit/epoch/stall cells (17 reps).
- `infix_classifier.{py,json}` — tracked predicate vs measured infix wire
  (wrong-sign) + explicit-flush under load.
- `detach_eof.{py,json}` — raw parent-exit vs EOF, late-write, battery-shape
  at T=0.5/5; `detach_battery_T30.json` — T=30/HOLD=35 receipt.
- `detach_battery/{pygame_probe.py,pygame_battery.py,runs-detach/}` —
  scratch copies; battery-level masking receipt (`verdicts.json`,
  `probe.stdout.txt`, `grandchild.pid`).
- `fd2_merge.{py,json}`, `fd2_driver_config.json` — merge provenance.
- `hang_shape.py` + `hang_shape_{r72_shape,pgroup_kill,bounded_drain,self_bounded}.json`.
- `replay.sh`, `replay/audit.txt`, `replay/battery.txt` — landed-diff audit
  (H1–H7 greps + 80/80 battery receipt).
- `replay2.py`, `replay2.json`, `replay/runs-rep{0,1,2}/`,
  `replay/stuck_detach/`, `replay/runs-nodeabsent/`,
  `replay/runs-unbuf/`, `replay/pyu_wrapper.sh` — stability ×3,
  stuck-detach, node-absent gate, regime control.
- `watch_author.sh`, `watch.log` — author-diff watch (landed 15:34Z).

No commit, no tracked mutation, no LOG/SCORECARD write.
