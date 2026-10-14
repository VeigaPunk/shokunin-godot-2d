# R69 — midlineforge fabrication bound's referent: gap-relative, not absolute (Godot 4.7.2 headless)

Sources: `reports/round-69/r69-{baseline,boundary,critic,reviewer,
scout,scribe,simplifier}.md`; `corpus/fixtures/descendant_pipe_probe.gd`
`--midline-gap-ms=N` (default 200 — the r66/r68 arm is byte-stable);
`run_battery.py` `--probe-midlineforge-gapladder` meta +
`raw_merged_sha256` on every dual_classify record; operator receipt
`corpus/live/integ-r69/runs/20261014T122037192227Z/
midlineforge-gapladder-verdicts.json`; scribe independent measurement
`corpus/live/r69-scribe/{declared-gaps,gap-transition,gap-edge-fine,
gap-band-quiet,crossed,offset-sweep-gap300,extremes}-results.json`
(268 real-pipe runs, driver `gap_ladder.py` sha `32ce2099…`, scratch
probe sha `afd2dd0c…` = fixture `5c5c629a` + gap flag); critic
`corpus/live/r69-critic/gap-sweep-results.json`; boundary knife-edge
`gap=81 miss / 82 mixed / >=83 fabricate` at offset 80.
Prior lessons extended: `r68-midlineforge-fabrication-window.md`
(the offset ladder), `r66-rejection-clause-surface.md` (the arm),
`r67-stream-classifier-divergence.md` (the receipt upgraded again).

verified-at: 2026-10-14, Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
Python 3.14.7, Linux x86_64; classifier segments unchanged since r65
(`run_process 88728b23`, `classify_process 749fa060`,
`classify_streams a886968f`, `classify_audio_process 3a6bc0e8` —
byte-identical across the r69 diff: probes/meta only).

## The referent, measured

The fabrication bound's referent is the GAP: the splice lands iff the
descendant's write reaches the captured stdout pipe strictly between
the `printraw(head)` flush and the `print(tail)` flush — write
position `pos ∈ [0, gap)`, measured per run. The r68 nominal ~198ms
edge was `200ms gap − spawn_overhead`, never an absolute constant.

- Declared grid (offset=80 fixed): gaps {100,200,400,800} fabricate,
  50 misses (write ~82ms lands post-tail; signature INTACT).
- Absolute-write-latency falsified BOTH directions by crossed cells —
  tracked in the ladder as (300,400)/(300,800)/(600,800): all
  fabricate 3/3 though pos>198; any absolute edge < ~602ms refuted.
  Scribe's wider scratch net adds (120,50)+(150,100) miss with
  pos<198; (250,800)+(500,800) fabricate; (350,200) misses.
- The nominal edge IS the write's landing position and moves with it:
  ~82ms quiescent, ~86–92 under load; nominal gap cells near the write
  position flip accordingly (boundary: miss <=81, mixed at 82,
  fabricate >=83 — the write position IS the edge).
- Second edge re-located: offset sweep at gap=300 puts the transition
  at ~295–300 (295 mixed) — edge ≈ gap − overhead at both gaps.
- No ceiling: gap=1500 fabricates; jitter floor ~2–5ms (no write wins
  at gap<=2ms at any offset — an absolute achievability bound INSIDE
  the gap-relative window, boundary).
- Per-rep invariant `splice ⟺ pos < measured_gap` held on 268 runs
  (1 same-chunk tie resolved by byte order — the r68 straddle shape).
- write_ppid is provenance, not the bound: post-tail misses carry
  pre-death writes (child in teardown — ppid flip lags) AND post-death
  writes; the splice correlates with position, never death state.
  Ground truth is byte order (spliced line / intact signature).
- Verdict nuance persists: every run rejects (misses via the
  standalone ERROR: clause) — the window selects the corruption shape,
  not the verdict.

## Receipt upgrade

- `raw_merged_sha256 = sha256(raw_stdout + raw_stderr)` on every
  dual_classify record (+ divergence_table rows + same-input gate):
  binds concat ORDER/separator — `sha(so+se) ≠ sha(se+so) ≠
  sha(so+"\n"+se)` over identical channel bytes (the r66 stderr+stdout
  caveat). Derivable from the pinned channels (attests the merge
  function, zero new entropy); vacuous on single-channel records.
  Boundary measured the digest concat-order-blind on only 9/118
  records — discriminating power lives on two-stream arms.
- Prior rows byte-stable modulo the additive field: the whole
  stream-attribution payload is byte-identical to r68's after
  volatile-field scrub; verdicts +1 additive row (`probe_midlineforge_
  gapladder`); flagless 88/88 + surface 34/34 unchanged; classifier
  segments byte-identical.

## Method notes

- The fixed-offset gap sweep alone cannot pin the referent: at
  offset=80 the absolute model diverges only where gap < write
  position (one cell), and that cell also falsifies a wiring defect —
  consume `elapsed_seconds` (∝ wired gap) and the `gap_ms=` banner as
  wiring witnesses. The reverse horn needs offset > ~198 with gap >
  offset: crossed (offset,gap) cells are the minimal complete design —
  now tracked in the ladder itself, not left in scratch.
- Gate pre-death only on inside cells: the ppid flip lags process
  teardown, so post-tail writes can sample write_ppid==godot_pid; byte
  order — never the ppid — is the post-tail ground truth.
- `negative_transition` readiness is load-sensitive: one observed
  flake where `current_scene` was still null a frame after
  `change_scene_to_packed` (SCRIPT ERROR at fixture :22 + 120-frame
  watchdog) under concurrent-lane load — environmental, not logic.
- drain×timeout interaction band ≈ gap 2350–2450ms (boundary): three
  nondeterministic record shapes race the deadline, plus a
  clean-signature TIMEOUT when the pending descendant holds the pipe —
  verdict-stable, content-unstable; a wave-10+ arm candidate.
