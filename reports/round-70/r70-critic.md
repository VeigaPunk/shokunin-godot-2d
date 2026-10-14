# game-dev-2d round 70 — critic (post-landing audit of `ceba654`)

Seat: critic | Lane: g2d | Host: devin | Target: HEAD `ceba654`
(LOVE 11.5 headless fixture + sibling battery; recorded verdict:
"engine-general fabrication window FALSIFIED at engine layer").

Scope: audit items 1–3 of the brief. All commands run at
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`; scratch under
`corpus/live/r70-critic/`; battery receipts in
`corpus/live/r70-critic/runs/love-*/verdicts.json`.

## Finding F1 — HIGH: the falsification targeted a non-analogous seam; the analogous seam fabricates

The recorded headline is wrong in both halves:

1. **The probed arm cannot express the phenomenon by construction.**
   The Godot midlineforge window (r68/r69 referent) is a *writer-side byte
   interleave*: `OS.create_process` spawns a descendant that inherits the
   child engine's fd1; the child emits `printraw(HEAD)` → `delay_msec(gap)`
   → `print(TAIL)`, and a descendant write inside the gap splices into the
   captured signature line (`descendant_pipe_probe.gd:163-188`). The landed
   LOVE arm uses `io.popen(cmd,"r")` (`love_probe/main.lua:41-54`): the
   child's fd1 is a *private capture pipe read by LOVE*, disjoint from
   LOVE's own stdout. There is no shared fd and nothing to splice into —
   "no fabrication window" there is near-tautological. It measures
   read-side visibility latency (a real measurement, honestly reported:
   `l2_wait ≈ 120.6–124.8ms` = the child's `sleep 0.12`, writer-bound),
   not the splice phenomenon.

2. **The "no equivalent midlineforge seam" scoping claim (author report
   :42-44) is falsified.** The seam exists and is trivial: `os.execute`
   (LuaJIT → libc `system()`) children inherit LOVE's fd1. My
   distinguishing cell (`corpus/live/r70-critic/splice_probe/`,
   `OFFSET_MS`/`GAP_MS` env-parameterized — the same ladder shape as the
   Godot fixture): backgrounded subshell writes
   `ERROR: LOVE_MIDLINE forged splice` into LOVE's captured stdout inside
   a head/tail gap.

   Measured (`love splice_probe | cat -A`, 3/3 unanimous per cell):

   | offset | gap | offset<gap | observed stdout |
   |---|---|---|---|
   | 80 | 200 | yes | `LOVE_SPLICE_PROBE: expected ERROR: LOVE_MIDLINE forged splice$` / `signature$` — **fabricated, byte-structure identical to Godot's splice** |
   | 240 | 200 | no | intact signature; ERROR lands after `LOVE_SPLICE_DONE` — missed |
   | 300 | 400 | yes | **fabricated** — crossed cell: offset > r68's ~198ms absolute edge, still lands ⇒ gap-relative referent reproduced |
   | 80 | 50 | no | missed |

   The r69 `gap_relative` signature reproduces cell-for-cell on LOVE. A
   second vector (`splice_probe_fd1/`): an `io.popen` descendant writing
   to `/proc/<love_pid>/fd/1` fabricates identically — the seam is not
   `os.execute`-specific; any spawn path that can reach fd1 suffices.

   **Corrected verdict**: the phenomenon is *spawn/fd-inheritance-general*
   (POSIX), which is stronger than the declared "engine-general" claim —
   and it was never engine-mediated on Godot either (`create_process` fd
   inheritance + harness capture is the same libc-level mechanism the
   author's own report :41-43 localizes to "the Godot-runner pipe
   plumbing"). The landed data is honest; the recorded FALSIFIED verdict
   and its "no equivalent seam" note are not. The author's own
   remaining-unknown ("whether LOVE has ANY descendant-stdout-capture
   seam") is answered: yes, in the `os.execute` arm they already ship —
   fd1 inheritance, unprobed.

   **Smallest safe correction** (fixable defect, not a tradeoff): add a
   `splice` arm to `love_probe/main.lua` (backgrounded `os.execute`
   descendant + `io.write` head / `love.timer.sleep(gap)` / tail, exact
   pins on the spliced line, offset/gap cells above) and re-record the
   verdict as: writer-bound read latency confirmed on `io.popen`;
   fabrication window **confirmed at the spawn layer** on both engines;
   "engine-general" correctly relocalized to "spawn-general". Report and
   lesson verdict lines need the same edit.

## Finding F2 — LOW: `ret_a=768` pin is environment-conditional, not a LOVE property

`ldd /usr/bin/love` → `libluajit-5.1.so.2`: this build ships **LuaJIT**
(Lua 5.1 API), where `os.execute` returns the raw `system()` result — on
POSIX the wait status, `exit 3` → `3<<8 = 768`, single value. Observed
`768` in 6/6 runs — **build-stable on this pinned host**. But it is
(OS × linked-Lua)-conditional: on Windows, `system()` returns the exit
code (`3`); a hypothetical PUC-Lua ≥5.2 LOVE build returns the
`(nil,"exit",3)` triple. The battery hardcodes `/usr/bin/love`, so the pin
is safe here — but the case is mislabeled as a LOVE behavior. Suggest
renaming/noting "POSIX + LuaJIT-5.1-shape wait status".

## Finding F3 — INFO: pin margins healthy, including under full-core load

`python3 corpus/fixtures/love_battery.py --runs corpus/live/r70-critic/runs`
→ **6/6 runs 15/15 PASS** (5 idle + 1 with busy loops on all cores).

| key | bound | idle range (5) | loaded | min margin |
|---|---|---|---|---|
| dt_mean_ms | (0.5,4.0) | 1.043–1.054 | 1.054 | ~0.54 |
| dt_min_ms | (0.0,0.1) | 0.002–0.004 | 0.004 | ~0.096 |
| dt_max_ms | (0.5,8.0) | 1.084–1.194 | 1.782 | ~6.2 |
| l1_wait_ms | (0.2,30) | 1.14–1.66 | 2.89 | ~0.94 |
| l2_wait_ms | (110,140) | 120.62–120.67 | 124.76 | ~14.8 |
| close_wait_ms | (0,5) | 0.09–0.11 | 0.0 | ~4.9 |
| total_ms | (115,170) | 122.0–122.6 | 128.0 | ~7.0 |

Load skews `l2_wait`/`total` ~4–6ms; margins remain ≥ ~12% of bound width.
No pin is fragile on this host.

## Finding F4 — INFO (positive): opt-in contract held

`git diff HEAD~1 HEAD -- corpus/fixtures/run_battery.py corpus/fixtures/descendant_pipe_probe.gd`
→ 0 lines; prior Godot rows byte-stable by construction, as claimed.
Operator-substitution provenance disclosed in-report. The `dtcadence`
arm's falsification of the "fixed-dt 60Hz" half of the declared claim is
correct and well-measured (uncapped ~960Hz, dt_mean ~1.04ms).

## Impacted axes

- **Verdict integrity / falsification correctness** (F1): headline
  recorded verdict wrong-sign — falsified on an inexpressive seam while
  the analogous seam fabricates.
- **Evidence sufficiency** (F1): the distinguishing cell was
  constructible in-repo and was never run.
- **Pin portability** (F2): env-conditional pin labeled as engine fact.

## Bottom line

Fixable defect: the measurements are sound, the conclusion is not.
Land the `splice` arm (cells above reproduce the Godot ladder's
gap-relative referent 1:1) and re-record the verdict — the fabrication
window exists on LOVE at the same layer it existed on Godot: spawned
descendants writing into the captured stdout fd. Reject is not required;
the correction is one arm plus verdict text.
