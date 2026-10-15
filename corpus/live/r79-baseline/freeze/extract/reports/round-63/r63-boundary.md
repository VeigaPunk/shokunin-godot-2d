# Round 63 — boundary recon: startup-margin knee pinning + multi-depth descendant pipe-EOF

## Scope and method

LEAF boundary/revenger seat, scratch-only and report-only. I wrote only this
report and `.shokunin/game-dev-2d/corpus/live/r63-boundary/`. No tracked
fixture, runner, CASES row, lesson, LOG, or SCORECARD entry was touched; no
subagent dispatch; no git mutation.

Assignment (lane brief): recon for the NEXT surface — (A) the startup-margin
knee retained from r61 (delay ∈ (7.5, 7.6]s under the CASES 8s bound): pin to
±0.05s and determine cross-run stability/variance; (B) multiple descendant
depths (grandchild-of-descendant holding the captured pipes): does the EOF
wait extend transitively?

Method (same discipline as r61/r62): both drivers
`ast.get_source_segment`-extract `run_process` and `classify_process`
**verbatim** from the tracked `corpus/fixtures/run_battery.py` and `exec`
them — the production code path, not a reimplementation. The depth driver
adds a second evidence layer: a `Popen`+`communicate` replica of the POSIX
timeout shape with a 20ms monitor thread (transitive `/proc` children
discovery, per-pid ppid/state transition log, and pipe-inode holder scans —
which pids hold OUR captured pipes regardless of genealogy). Knee runs are
**sequential** on purpose: elapsed is the measurement; concurrent godot
startups would contaminate it.

**Provenance note — mid-flight sibling diff (third consecutive round).**
At depth-probe time the tracked runner sha256 was
`0c4c9bee70569c8ec29f98dea89c437d78587fd5c3c7b3220b76140ac59520dd` (r62
commit `edbd945`). During this wave the r63 author landed the lane's declared
move in the working tree — runner now `b6f3d5c23804…`, fixture
`descendant_pipe_probe.gd` also modified (+185/−1: CASES row
`descendant_pipe_forged_signature_release`, meta row
`probe_descendant_signature_spoof`, fixture arms `--spawn-forge-hold` /
`--spawn-forge-release` — the tracked known-accepting forgery boundary at
depth 1). I verified via the same `ast` extraction that `run_process`,
`classify_process`, `classify_streams`, and `classify_audio_process` are
**byte-identical** HEAD↔worktree — additive-only outside those functions,
so every number below characterizes both revisions. The sibling's landed
rows pin the forgery at depth 1; my probe B measures that the same forgery
class extends to depth ≥2 unchanged.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Linux `7.2.3-arch1-3 x86_64`, Python `3.14.7`, `/usr/bin/sh` → bash,
loadavg ~2.0 during the knee phase (busier than prior rounds), subreaper =
pid 1573 (`systemd --user`) as in r61/r62.

## Probe A — startup-margin knee: it is a BAND, not a point

Fixture `proj/margin_probe.gd` (byte-identical r61 copy, `fefc7860…`) prints
`MARGIN_PROBE: expected signature` after `create_timer(--delay)`, exits 0.
Sequential runs through verbatim `run_process`. Receipts:
`knee-sweep-verdicts.json` (sha256 `01c5e213…`).

### Bound 8.0 sweep (n=4/point in the knee zone)

| delay | pass/n | marker-in-partial | elapsed s | overhead s (passes) |
|---|---|---|---|---|
| 0.0 ×8 | 8/8 | 8/8 | 0.358–0.575 | 0.358–0.575 |
| 7.30 ×2 | 2/2 | 2/2 | 7.709–7.818 | 0.409–0.518 |
| 7.45 ×4 | 4/4 | 4/4 | 7.808–7.931 | 0.358–0.481 |
| 7.50 ×4 | 4/4 | 4/4 | 7.887–7.970 | 0.387–0.470 |
| **7.55 ×4** | **1/4** | 2/4 | 7.926–8.011 | 0.376 (one pass) |
| **7.60 ×4** | **1/4** | 2/4 | 7.985–8.011 | 0.385 (one pass) |
| **7.65 ×4** | **1/4** | 2/4 | 7.986–8.011 | 0.336 (one pass) |
| 7.70 ×4 | 0/4 | 1/4 | 8.003–8.011 | — |
| 7.75 ×4 | 0/4 | 0/4 | 8.003–8.012 | — |
| 7.90, 8.20 | 0/4 | 0/4 | 8.005–8.011 | — |

Overhead pool (all accepting runs, n=21): min **0.336**, mean **0.421**,
max **0.575**, stdev **0.060**. TIMEOUT arms bound-exact: 8.003–8.012s.

**Pinned characterization**: the accept/reject knee is not a ±0.05s point —
it is a stochastic band ≈ `bound − overhead` where overhead draws from a
~0.24s-wide distribution on this host/load. Model check: predicted flip band
= 8.0 − [0.336, 0.575] = **[7.425, 7.664]**; the observed mixed zone
[7.55, 7.65] sits inside it; pass/fail inside the band is literally a draw
of the startup overhead (the 7.65 pass drew overhead 0.336 — the minimum
observed). Deterministic edges measured: **all-pass ≤ 7.50** (10/10 incl.
7.30/7.45), **all-fail ≥ 7.70** (12/12 incl. 7.75/7.9/8.2). The r61 bracket
(7.5, 7.6] is the left half of this band — consistent, but the honest pin is
distributional: last-always-accept 7.50, first-always-reject 7.70.

**Marker knee is wider than the classify knee.** Signature presence in the
partial output persists stochastically into the reject zone: 2/4 marked at
7.55, 7.60, 7.65 and still 1/4 at 7.70; zero marker ≥7.75. So between
~7.6–7.7 the record shape "signature present AND TIMEOUT" is common — the
exact shape the r61 7.6 run showed once. Marker presence says nothing about
verdict — the error field alone carries the reject.

**Bound-3.0 replication** (the tracked `--probe-timeout` margin): overhead
pool n=7 [0.325, 0.489] mean 0.393 — the same startup budget, confirming the
knee is `bound − overhead`, bound-independent. All-pass ≤2.55 (6/6), all-fail
2.60 (3/3), and — underlining the band — one stray pass at 2.65 (overhead
0.346). Bound-exact TIMEOUTs 3.005–3.006s.

**Variance answer**: not stable as a point. Baseline spread this host
0.358–0.575 (0.217) vs r61's 0.357–0.403 (0.046) — the jitter is
load-sensitive (loadavg ~2.0 here). Fixture-margin guidance sized to the
max, not the mean: under bound 8 a True-row wants delay ≤ ~7.4 (bound −
overhead_max − small guard); a False-row that also suppresses the marker
wants delay ≥ ~7.75 (bound − overhead_min + guard). The r61 candidate pair
(7.0 True / 8.5 False) remains comfortably outside the band at this load.

## Probe B — multi-depth descendants: the EOF wait is fully transitive, and so is the forgery

Fixture `proj/depth_probe.gd` (`2669f3ad…`) spawns ONE intermediate
`OS.create_process` executing a driver-written level file under `arms/`;
each level file decides whether a further level is spawned and whether it
holds the inherited pipes. Reparenting-gate idiom (same pattern as the
tracked fixture) makes gc/ggc writes provably post-ancestor-death. All arms
at bound 3.0; receipts `depth-verdicts.json` (`55f82850…`) +
`depth-timeline.json` (`cadb92f4…`); executed level files are receipts under
`arms/`.

| arm | shape | exit | error | elapsed | sig | classify | at return |
|---|---|---|---|---|---|---|---|
| d2_hold | godot exits ~0.5s; intermediate exits +0.6s; **gc holds pipes ~4s** | None | TIMEOUT | 3.002s | True | **False** | gc alive, ppid **1573**; holders = {gc, its `sleep`} |
| d2_release | same but gc releases ~+1.6s | 0 | None | **2.124s** | True | True | nobody holds; return ≈ gc release |
| d2_spoof | godot withholds signature; **gc writes it post-both-deaths**, releases ~1.4s | 0 | None | 1.451s | **True** | **True** | **depth-2 forged PASS** |
| d2_spoof_hold | forged sig then gc holds past bound | None | TIMEOUT | 3.003s | True | False | forged sig inside TIMEOUT record |
| d2_hang | godot `--hang`; gc holds | None | TIMEOUT | 3.006s | True | False | godot killed; gc orphaned |
| d2_detach | intermediate exits +0.3s; gc fully fd-detached, sleeps 6 | 0 | None | 0.707s | True | True | **gc leaked invisibly at depth 2** |
| d2_mixed | intermediate holds to +1.5s; gc detached | 0 | None | 1.834s | True | True | return gated by depth-1 holder; gc leaked |
| d2_reparent | intermediate exits +0.15s while godot `--linger` lives | None | TIMEOUT | 3.004s | True | False | see reparent finding below |
| d3_hold | intermediate→gc→ggc; only **ggc** holds ~4s | None | TIMEOUT | 3.003s | True | False | ggc alive, ppid 1573 — **depth 3 blocks** |

Timeline records (`depth-timeline.json`, per-pid transitions + pipe-inode
holder scans at 20ms):

- **Transitive hold, proven at inode level.** At the bound, the holder set
  for d2_hold was `{gc shell pid, its own sleep 4.0 child}` — a depth-2 shell
  AND a depth-3 transient — both on **both** captured streams, gc already
  orphaned to 1573 (transitions: `ppid intermediate → 1573` at 1.191s,
  godot reaped 0.511s). Same shape for d3_hold: blocking holder = the
  great-grandchild (depth 3) alone, orphaned at 0.858s.
- **EOF release tracks the last holder at ANY depth.** d2_release returned
  exit 0 at ~2.0–2.2s — over a second after the intermediate's death — the
  residual wait is attributable solely to the depth-2 holder. Holder samples
  show the set draining level by level (intermediate+gc+their sleeps → gc
  alone → empty → return).
- **The holder set quietly includes each level's own children.** Every
  `sleep`/`read`-loop child forked by a holding shell also inherits the
  pipes (visible in holder_samples); EOF releases only when the LAST
  fd-carrier of any generation dies. Depth is never the variable — fd
  carriage is.
- **Depth-2 signature forgery accepted.** d2_spoof: godot emitted no
  signature; the merged stream contains the intermediate's
  `INTERMEDIATE_EXIT`, then `GC_ORPHANED pid=… ppid_now=1573`, then
  `DEPTH_PROBE: expected signature`, then `GC_RELEASED` — the ONLY signature
  was written by a doubly-orphaned grandchild after BOTH ancestors' deaths
  (godot reaped 0.592s, gc's ppid flip at 1.099s, signature after).
  `classify_process` → **True**, exit 0, 1.451s — identical verdict shape to
  a genuine PASS. The just-landed tracked forgery rows (depth 1) pin a
  boundary that is, measured, **depth-agnostic**.
- **Orphans go to the session subreaper — never to a live ancestor.** My
  d2_reparent arm was designed to show re-adoption: intermediate exited at
  ~0.6s while godot (`--linger 1.2`) lived until 1.768s. Measured
  falsification of that hypothesis: gc's ppid went `intermediate → 1573`
  directly at 0.636s — the kernel reparents to the nearest subreaper
  (`systemd --user`), and a still-living grandparent process gets nothing.
  Corollary: the fixture's ppid-gate idiom stays valid at every depth —
  the flip target is always the subreaper, never a (possibly dead) ancestor.
- **Zombie datum (partially fills an r62 UNKNOWN).** A dead intermediate
  persists as **zombie under the live godot**: d2_reparent shows
  `state=Z, ppid=godot_pid` from 0.636s until godot's exit at ~1.77s
  (≥1.1s window); d2_hang the same from 1.048s to the 3.0s kill (~2s).
  Godot does not promptly `wait()` `OS.create_process` children; the
  zombie is reaped by the subreaper only when godot dies.
- **Kill reach unchanged.** d2_hang: `communicate` bound fired with godot
  alive (`child_reaped_at_s=None`), `kill()` SIGKILLed godot only; the gc
  was already orphaned and stayed alive — nothing at depth ≥1 is ever
  signaled.
- TIMEOUT arms bound-exact 3.002–3.006s; all descendants self-terminating;
  `hygiene_killed` = the d3 ggc + its sleep (bounded holds still pending at
  driver end), nothing else remains.

## Divergences / refined invariants

- `return ≈ min(bound, max(child_exit, last_holder_release))` — refined from
  r62's `last_fd_EOF`: the holder set is every live process carrying the
  captured pipe inodes, **at arbitrary depth and regardless of genealogy**
  (including transient children of holders). Measured transitively at depth
  3; nothing in the mechanism suggests a depth limit.
- Signature presence over the merged stream is forgeable **from any depth** —
  the r62 critic's depth-1 measurement and the r63 author's landed depth-1
  forgery rows bound a class that is, as measured, depth-agnostic.
  Distinguishing evidence is never signature presence: only
  child-exit/timeout fields (`error`, `actual_exit`, meta-side
  `child_exit_at_timeout`) plus fixture-carried provenance (reparent gates,
  `write_ppid=` lines).
- The startup-margin knee is a **load-sensitive stochastic band**, not a
  point: `bound − U[overhead]`, overhead ∈ ~[0.34, 0.58]s this host at
  loadavg ~2. Prior point-brackets ((7.5,7.6]) are band-left-edges; margin
  guarantees must be sized to overhead-max/min, not to a knee point.
- Reparenting is **subreaper-directed, not ancestor-directed** — falsified
  my own designed hypothesis; orphans never reattach to living
  non-subreaper ancestors.
- Godot children may linger as zombies under live godot (≥~2s observed) —
  a `run_process` record cannot see this; only `/proc` state does.

## Recommended next-round candidate surfaces (report-only)

1. Depth-2 forgery tracked arm: the `depth_probe.gd` level-file pattern
   ports directly — a CASES row where a doubly-orphaned gc emits the
   signature post-both-deaths would pin the depth-agnostic forgery class in
   tracked space (cheap additive; mirrors the landed depth-1 rows).
2. Startup-margin tracked pair (r61's candidate, re-sized by this
   measurement): True-row delay ≤ 7.4, False-row delay ≥ 7.9 under bound 8
   (7.9 also suppresses the marker — a second distinguishable shape). Keep
   margins vs overhead-extremes, not the band center.
3. Zombie/reap surface: a `--linger` arm asserting intermediate zombie-ness
   under live godot would pin Godot's `OS.create_process` reap discipline —
   the remaining piece of r62's zombie UNKNOWN is whether godot EVER reaps
   (longer linger) vs. only at exit.

## UNKNOWNs / retained caveats

- Single host, loadavg ~2.0 during the knee phase; the band edges (7.50 /
  7.70) will slide with host load — the *distributional* characterization
  is portable, the numbers are not. n=4/point; tails beyond observed
  overhead extremes unmeasured.
- Depth 3 confirmed; deeper depths unprobed (mechanism says unbounded).
- `OS.create_process` reap discipline bounded only at ~2s zombie windows;
  whether godot reaps at all during a long lifetime unprobed.
- Holder identity is fd-based; a descendant that closes a stream then
  re-dups it elsewhere, `pidfd` semantics, non-POSIX, exported builds —
  unprobed (carried from r61/r62).
- The timeline replica replicates the POSIX timeout shape; verdict records
  come from the verbatim extracted `run_process`. Replica timings are
  corroborating, not production-path numbers.
- LSP unavailable on this host for `references`/`implementation`; the
  `ast`-verbatim extraction + executed output is the evidence chain; text
  grep used only to locate, not to prove.
- r62 retained surfaces unchanged: >64KiB descendant writes, `OS.execute`
  blocking paths, signal origin, exported builds.

## Artifact inventory (`.shokunin/game-dev-2d/corpus/live/r63-boundary/`)

- Drivers: `drive_knee.py` `3c660cbc…`, `drive_depth.py` `047bc41b…`.
- Fixtures: `proj/margin_probe.gd` `fefc7860…` (r61 verbatim),
  `proj/depth_probe.gd` `2669f3ad…`, `proj/project.godot` `8de8b3af…`
  (fixture verbatim).
- Receipts: `knee-sweep-verdicts.json` `01c5e213…` (54 runs: 8 baseline +
  2 wing + 28 fine sweep + 4 tail + 12 bound-3.0),
  `depth-verdicts.json` `55f82850…`, `depth-timeline.json` `cadb92f4…`.
- Executed level files (receipts): `arms/{d2_hold,d2_release,d2_spoof,
  d2_spoof_hold,d2_hang,d2_detach,d2_mixed,d2_reparent,d3_hold}.sh` + gc/ggc
  helpers; `arms/*.gc-outlived` / `*.ggc-outlived` = deferred writes landed
  by orphaned descendants.
- Raw captures: `raw/{arm}.stdout` (verdict path) + `raw/{arm}.timeline.stdout`
  (replica path) for all 9 depth arms; `raw/margin-*.stdout` for all knee runs.

No commit, no tracked-fixture mutation, no LOG/SCORECARD write; integration
of any recommended row belongs to a later executor + named non-author replay.
