# game-dev-2d round 71 — critic (pre-landing attack on the pygame MOVE)

Seat: critic | Lane: g2d | Round: 71 | Host: devin — CPython 3.14.7,
pygame 2.6.1 classic (SDL 2.32.72), 32 cores, compositor present
(Hyprland/Wayland — the frontier's T2 "no env" trap host).

Target: the round-71 MOVE (`g2d-critic.txt:11-13`) and the de-facto design
in flight. Audit start 2026-10-14T14:23Z: **no tracked artifact had landed** —
`reports/round-71/` did not exist and `corpus/fixtures/` contained no
`pygame_*` file (`ls corpus/fixtures | grep -i pygame` → no match); sibling
reports landed while this audit ran. The concrete design under attack is
therefore the scout prototype
`corpus/live/r71-scout/pygame_probe.py` + `pygame_battery.py` (75 cases),
the author's in-flight variants `corpus/live/r71-author/withhold_variants.py`,
and the frontier claim text (`reports/frontier/fa-pygame.md:76-84`).

All commands from the lane repo root. Scratch + receipts:
`corpus/live/r71-critic/`. No sibling artifact was modified; the scout
battery was executed read-only with `--runs` pointed at my scratch.

## Verdict summary

Landable with pin corrections. The brief's **"~8 KB" withholding bound is
falsified on this host**: the parent-visible flush edge is
`io.DEFAULT_BUFFER_SIZE = 131072 B` (128 KiB on CPython ≥3.14; 8192 B on
≤3.13), and 8192 is the *text layer's staging chunk*, which by itself
never makes a byte visible. The scout prototype already measures the
corrected lattice; its **pins are not yet load-robust** (2/75 FAIL at 2×
core oversubscription), and the briefed falsifier is inverted as worded.

## F1 — HIGH: the withholding edge is 128 KiB, not ~8 KiB; the constant is interpreter-version-dependent

**Counterexample to the briefed figure.** An unflushed piped write is
parent-invisible until the *binary* buffer fills, not at 8 KiB. Measured
lattice (my harness `withhold_probe.py`, 3 reps on the boundary cells,
exits 0; receipts `withhold_results.idle.json`, `.edge.json`,
`.boundary.json`):

| unflushed cell | first parent-visible | verdict |
|---|---|---|
| 7–100 B line, no flush | only at exit (~405 ms; child sleep 400 ms) | withheld |
| single write 4001 / 8192 / 8193 / 16001 / 130000 B | only at exit | withheld |
| single write **131072 B** (== `io.DEFAULT_BUFFER_SIZE`) | ~5.5 ms | **released** |
| single write 131073 / 132000 / 200000 B | ~5.5 ms | released |
| 64 B writes × 400 (26 000 B) | all at exit | withheld |
| 65 B writes × 4000 (260 000 B) | bytes surface as accumulated output crosses ~128 KiB; tail 12 350 B at exit | partial |
| withheld line + later 132 000 B write | line released **at the crossing write** (255.7 ms), not at exit | released early |
| `PYTHONUNBUFFERED=1` (same as `-u`) | ~5.5 ms | window collapsed |

The scout's independent receipt agrees cell-for-cell
(`corpus/live/r71-scout/withhold_probe.stdout.txt`): `edge_8192`,
`edge_65536`, `edge_128k_lo` (131071) all `first_vis_ms ≈ 608.9` (exit);
`edge_128k_eq` (131072) and `edge_128k_hi` (131073) at 9.0–9.4 ms;
`seg_64k_64k` (total exactly 131072) still withheld; `seg_70k_70k`
partial at the second write. The r71-reviewer matrix independently shows
k ∈ {8192 … 65536} all exit-batched
(`corpus/live/r71-reviewer/flush_edge_matrix.txt`). The r71-simplifier's
independent bisect agrees (`reports/round-71/r71-simplifier.md` §2,
`corpus/live/r71-simplifier/flush-edge-bisect.txt`): moving the declared
buffer size (`os.fdopen(1,"wb",buffering=…)`) moves the edge exactly, so
the *mechanism* ("bounded by buffer size") is confirmed while the 8 KB
figure is not.

**Mechanism (two-stage, both stages are CPython, neither is SDL/pygame).**
`Modules/_io/textio.c:1206` sets the text layer `chunk_size = 8192` and
`:1790` flushes *pending text into the binary buffer* at
`pending_bytes_count >= chunk_size` — this is staging, not visibility.
Visibility is the binary layer: `Modules/_io/bufferedio.c:2104` buffers a
write only `if (buffer->len <= avail && buffer->len < self->buffer_size)`,
so a single write ≥ buffer size is written through at once; and
`Modules/_io/_iomodule.h:81` is `#define DEFAULT_BUFFER_SIZE (8 * 1024)`
on the 3.13 branch vs `(128 * 1024)` on 3.14. Runtime check:
`python3 -c "import io; print(io.DEFAULT_BUFFER_SIZE)"` → `131072`.
Consequence: the frontier's "~8KB" (`fa-pygame.md:78-79`) was an unmeasured
assumption from the ≤3.13 constant; on this host it is wrong by 16×.

**Impacted axes:** coverage (the withholding-window edge family would be
recorded at the wrong scale), calibration (the referent constant),
verdict integrity (see F2).

**Smallest safe correction:** keep the scout prototype's shape — emit the
referent (`PYGAME-ARM stdio | default_buffer_size=…`,
`pygame_probe.py:181`) and pin the **relations** `edge_lo = bufsize-1`,
`edge_eq = bufsize`, `edge_hi = bufsize+1` (`pygame_battery.py:144-151`),
plus the exact `131072` as a *host-provenance row* (same class as LOVE's
`ret_a=768` pin). Do not hardcode an 8 KiB edge anywhere; record the
interpreter version in the battery payload (it currently records only the
interpreter path — `pygame_battery.py:286-288`).

## F2 — HIGH: the briefed falsifier is inverted; "a >8KB write surfaces early" is the confirmation cell at the true bound, not the falsifier

The claim is "withholding is bounded by buffer size". Measured: a >8 KiB
mid-run write does **not** surface early (16 KB, 26 KB, 130 KB all held
until exit); a write ≥ 131072 B does. So the honest falsifiers are
(a) a withheld line *not* released by a later ≥bufsize write, and
(b) first-visibility bytes not explainable by the buffer boundary. If the
author's landing records ">8KB write surfaced early ⇒ 8KB bound confirmed"
or, worse, records the measured non-early surfacing as *falsifying*
buffer-boundedness, the round lands a wrong-sign verdict — the r70-F1
defect class. The author's in-flight variants
(`r71-author/withhold_variants.py`: 9000 B single write, 100×100 B
cumulative) are both below the real edge and will be exit-batched on this
host; they cannot confirm an 8 KiB bound.

**Impacted axes:** verdict integrity, evidence sufficiency.

**Smallest safe correction:** re-word the claim to "bounded by the binary
layer buffer (`io.DEFAULT_BUFFER_SIZE`), with the text layer's `_CHUNK_SIZE`
as an internal staging threshold", and land the scout's cell set verbatim
(it already tests the correct side of the edge).

## F3 — HIGH: draft pins fail under measured load (2/75) and carry three thin margins

`python3 corpus/live/r71-scout/pygame_battery.py --runs corpus/live/r71-critic/scout-battery-idle`
→ **75/75 PASS, exit 0, probe elapsed 20.0 s**.
Under 64 × `yes > /dev/null` on 32 cores (2× oversubscription), same
command with `--runs …/scout-battery-loaded64` → **73/75, exit 1,
elapsed 21.5 s**:

| failing case | pin | observed (loaded) |
|---|---|---|
| `popen_close_fast` (`pygame_battery.py:85`) | `(0.0, 5.0)` ms | **5.12 ms** |
| `withhold_seg_over_partial` (`:133`) | `vis_mid_bytes = 70000` | **0** (mid sample at `MID_MS=300`; the child's `SEG_SLEEP1=250 ms` sleep overshot under load, so the second 70 000 B write landed after the sample) |

Thin margins from the same loaded run plus my independent runs:
- `withhold_seg_over_mid` pin `(150, 500)` (`:134`): loaded `first_vis_ms =
  456.8` — the sleep overshoot moved the overflow write by ~200 ms; 43 ms
  of margin. The same run's `edge_eq_fast` pin `(0, 300)` (`:118`) saw
  183.6 ms (idle 47.2) — 116 ms margin.
- `popen_l2_wait_writer (110, 140)` (`:84`): my 32-hog run measured
  `l2_wait_ms` 131.3–136.5 (`withhold_results.popen_loaded.json`) — 3.5 ms
  margin; the frontier probe's `popen_buf` `l1_wait` measured 136.3–139.0
  vs its `(110, 145)` pin (`:90`).
- `cadencebusy_tail_tight (15.5, 22.0)` (`:77`): my 64-hog cadence run
  measured `dt_max_ms = 23.181` (`cadence.loaded64.json`) — **over the
  cap**; the scout's own loaded run saw 19.2. One of two 2×-load runs
  fails this pin.

**Impacted axes:** calibration (bounds must be floor/band-shaped with
margin, not near the measured tail).

**Smallest safe correction (all are constant edits):**
`popen_close_fast → (0.0, 20.0)`; `popen_l2_wait_writer → (110.0, 160.0)`;
`popen_buf_withheld → (110.0, 175.0)`; `cadencebusy_tail_tight →
(15.5, 40.0)`; `edge_eq_fast`/`edge_hi_fast`/`big_fast`/`unbuf_fast →
(0.0, 500.0)`; and for `seg_over` replace the wall-clock mid sample with a
timing-independent pin: emit the **first chunk size** from the first read
event (the overflow flush is deterministically 70 000 B) and pin
`first_chunk_bytes == 70000` + `first_vis_ms (100, 1500)` + `total_bytes
== 140000` + `integrity == 1`. Keep `MID_MS=300` for the *withheld* cells
(their claim is `vis_mid_bytes == 0` at any load, since bytes are
buffered, not delayed) — or move it to 450 ms, which is also safe.

## F4 — MEDIUM: env provenance gap — the popen children inherit `PYTHONUNBUFFERED`

Measured: `PYTHONUNBUFFERED=1` collapses the window (7 B line visible at
5.5 ms vs 405 ms withheld; `withhold_results.idle.json` `exit_unbuffered`).
The draft strips the variable only for the withhold children
(`pygame_probe.py:112`); the `popen`/`popen_buf` children inherit the
probe's env (`pygame_probe.py:96-97, 233-236`), and the probe inherits the
battery's env (`pygame_battery.py:46-50, 156-161`). On a host exporting
`PYTHONUNBUFFERED` (common in CI images), `popen_buf`'s exit-batch shape
disappears (`l1_wait ≈ 5 ms`) and its `(110, 145)` pin fails for the
wrong reason — a false-provenance failure, not a runtime difference.
This host is clean (`PYTHONUNBUFFERED` unset, measured), so the landed
evidence stands; the trap is portability.

**Impacted axes:** evidence sufficiency (env conditionality of a pinned
claim).

**Smallest safe correction:** build one `CHILD_ENV` in the probe
(`os.environ` minus `PYTHONUNBUFFERED`, plus the three pinned SDL/pygame
vars) and pass it to *every* spawned child; assert the precondition in the
child (`line_buffering=False, isatty=False, unbuffered=False`) and record
it — my harness does this and the receipts carry the fields
(`withhold_results.*.json` → `child_stdio`).

## F5 — LOW: `withhold_arm` can emit `first_vis_ms=None` (break/drain race)

`pygame_probe.py:140-153`: the loop breaks on `proc.poll() is not None`
and the post-break drain appends bytes **without** setting `first_vis`.
If the child's exit-flush lands between a `select` timeout and the `poll`
check, exit-batched cells emit `first_vis_ms=None`, and `check()` fails
with "not numeric" (`pygame_battery.py:184-198`). Not observed in any
exit-batch sample I ran (my harness ×2 reps + both scout-battery runs),
but it is a sub-ms race that load widens.

**Smallest safe correction:** in the drain loop, set
`first_vis = first_vis or (time.perf_counter() - t0)` when data arrives.

## F6 — INFO (independent confirmations of the other arms)

- Writer-bound popen (c): idle `l1_wait 5.11–5.18 ms`, `l2_wait
  125.19–125.24 ms` (child's own 120 ms sleep + spawn), `close_wait
  1.3–1.6 ms`, `rest_len 0`, byte-exact — LOVE's shape confirmed
  (`withhold_results.popen_idle.json`). Under 32 hogs the same arm drifts
  to `l1 11.1–14.6`, `l2 131.3–136.5`, `close 0–4.3`.
- Pump-free headless (d): 400 frames without any event call → posted
  `USEREVENT` survives (`posted_survived=1`), 0 spontaneous events in a
  0.5 s pump poll, no QUIT, `flip_mean_ms=0.0` (`pump.idle.json`) — the
  frontier's (d) verdict confirmed on my harness.
- Cadence (a): idle `tick(60)` 62.3 Hz (mean 16.056, min 16.008, max
  16.072); 64-hog 62.2 Hz (mean 16.089, max 20.908); uncapped 6.0–9.7 MHz;
  `busy60` 62.5 Hz idle → 59.2 Hz under 2× oversubscription (so any
  `busy` rate pin must be a floor ≤ 55 Hz). Frontier probe re-run under
  64 hogs reproduces its report (`frontier_loaded.stdout.txt`).
- The scout probe's `stdio default_buffer_size=131072` arm is a valid
  referent: the withhold child is the same interpreter
  (`sys.executable` + `os.path.abspath(__file__)`).

## F7 — INFO (landing checklist for the tracked fixture/battery)

- `pygame_battery.py:227-229` carries a landing note: the `--runs` default
  must become `HERE.parent / "live" / "runs"` (love_battery convention) or
  the landed runner writes a stray `corpus/fixtures/runs/` tree.
- `PROBE = HERE / "pygame_probe.py"` (`:43`) is right, but the basename
  collides with `corpus/live/frontier-pygame/pygame_probe.py` and
  `corpus/live/r71-baseline/pygame_probe.py`; the payload records the path
  (`:289`) — consider a probe sha256 for first-contact provenance.
- Claim wording: the capped cadence is a *bare Python loop + Clock pacer*
  under `SDL_Delay` ms-granularity, and the withholding window is *CPython
  stdio*, not pygame/SDL (pygame contributes zero pipe plumbing). The
  battery docstring already says this; keep it out of any "engine
  cadence/engine seam" phrasing.
- Byte-stability of prior rows: new files only; `run_battery.py` selects
  fixtures from a static `CASES` list (`corpus/fixtures/run_battery.py:19+`)
  and `love_battery.py` is untouched — Godot/LOVE rows are stable by
  construction. (Pre-existing worktree dirt in
  `corpus/live/frontier-lovephysics/` was present before this round and is
  not a round-71 delta.)
- Cross-layer hazard (my `mixed_invert` cell): `print()` (pending) then
  `sys.stdout.buffer.write(b"B"*140000)` (≥bufsize, raw) makes the parent
  see the *later* bytes first and the earlier line at exit — order
  inverted. The fixture's writer must stay single-layer (`print(...,
  flush=True)`) and no battery may assert "no bytes before flush" without
  the bufsize relation.

## Reproduce

```
# my harness (scratch)
cd corpus/live/r71-critic
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 \
  python3 withhold_probe.py idle --reps 2          # exit 0
… withhold_probe.py edge --reps 1                  # exit 0
… withhold_probe.py boundary --reps 3 --modes single130k,single131072,single131073,single132k,bigwrite,bigwrite128k,exit,flushsmall
… python3 cadence_probe.py idle | loaded | loaded64        # exit 0 each
… python3 pump_probe.py idle                       # exit 0
python3 -c "import io; print(io.DEFAULT_BUFFER_SIZE)"      # 131072

# the in-flight design under attack (read-only; runs into my scratch)
python3 corpus/live/r71-scout/pygame_battery.py \
    --runs corpus/live/r71-critic/scout-battery-idle       # 75/75 PASS exit 0
# same with 64 x `yes > /dev/null` on 32 cores:
python3 corpus/live/r71-scout/pygame_battery.py \
    --runs corpus/live/r71-critic/scout-battery-loaded64   # 73/75 FAIL exit 1
```

Receipts: `withhold_results.{idle,edge,boundary,popen_idle,popen_loaded}.json`,
`cadence.{idle,loaded,loaded64}.json`, `pump.idle.json`,
`frontier_loaded.stdout.txt`, `scout-battery-{idle,loaded64}/pygame-*/{probe.stdout.txt,verdicts.json}`.

## Bottom line

Fixable defects, not a reject: the design shape (referent arm + relation
pins + exact host row) is right and the scout prototype already measures
the corrected 128 KiB lattice. Land it with (1) the edge stated as
`io.DEFAULT_BUFFER_SIZE` (131072 here; version-dependent — never "~8KB"),
(2) the F3 bound widenings + the timing-independent `seg_over` first-chunk
pin, and (3) one pinned child env for every spawn. The strongest
counterexample available on this host — a >8 KiB mid-run write surfacing
early — does not reproduce (16 KB/26 KB/130 KB held; 131072 B released);
the withholding window is real, bounded, and 16× larger than the brief
assumed.
