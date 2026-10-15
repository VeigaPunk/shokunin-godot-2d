# R68 — midlineforge fabrication window measured as an offset ladder (Godot 4.7.2 headless)

Sources: `reports/round-68/r68-{author,critic,reviewer,scribe,...}.md`;
`corpus/fixtures/run_battery.py` `--probe-midlineforge-ladder` meta +
`divergent_clause`/`raw_*_sha256` upgrades in the r67
`--probe-stream-attribution` block (work commit `f754546`);
`corpus/fixtures/descendant_pipe_probe.gd` `--midline-offset-ms=N`;
author receipt `corpus/live/r68-author/runs/…/midlineforge-ladder-
verdicts.json`; scribe independent measurement `corpus/live/r68-scribe/
{declared-ladder,hi-edge,straddle-dense,provenance,prov-prehead}-results.json`
(~256 real-pipe runs, driver `ladder.py` sha `21071d54…`, scratch probe
sha `3f7806b6…` = fixture `92a40d70` + 3-arg patch).
Prior lessons extended: `r66-rejection-clause-surface.md` (the arm),
`r67-stream-classifier-divergence.md` (the receipt upgraded).

verified-at: 2026-10-14, Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
Python 3.14.7, Linux x86_64; classifier segments unchanged since r65
(`run_process 88728b23`, `classify_process 749fa060`, `classify_streams
a886968f`, `classify_audio_process 3a6bc0e8` — byte-identical across the
r68 diff: probes/meta only).

## The window, measured

The midlineforge fabrication lands iff the descendant's write reaches the
captured stdout pipe between the `printraw(head)` flush and the
`print(tail)` flush — write-position space `[0, gap)`, gap measured
200.024–200.121ms (delay_msec(200) + print overhead, ~0.1ms jitter).

In nominal `--midline-offset-ms` space on this host: offsets 0–198
fabricate rep-perfectly; the transition band is 198.05–198.35 (jitter
split, ~1ms wide); ≥198.5 misses always. The nominal edge = gap −
spawn_overhead, overhead = sh exec + /proc/self/stat read + printf ≈
1.4–2.5ms. The below-window regime (write before head) is unreachable by
non-negative offsets — min pos ≈1.43ms — but exists under a delayed
head: same standalone-ERROR + intact-signature miss shape. The nominal
lo_edge is a spawn-latency floor, not a window bound (boundary: negative
offsets all splice — downward-unbounded).

Three regimes, one boundary each side:
- pre-head / post-tail: ERROR lands standalone, signature INTACT,
  verdict still FAIL (error-scan clause) — a MISS changes which clause
  corrupts, never the verdict.
- inside: head+ERROR fuse (fabricated line), signature substring
  DESTROYED, verdict FAIL (dual-clause).
- edge straddle (rare, ~0.1ms band): ERROR inside while write_ppid echo
  lands past the tail (order H E T E2).

write_ppid==godot_pid in every regime — pre-death provenance is a write
property, not a splice property. Post-death crossover at ~250–260ms
(write_ppid→subreaper).

## Receipt upgrades (r67 stream-attribution meta)

- `divergent_clause`: per divergence_table row, the exact classifier
  clauses that diverged, taxonomy {exit,signature,error_scan,blob,
  allowlist_shape} — measured attribution, not a relabel: computed by
  re-deriving each clause's verdict on the SAME captured streams through
  allowlist mirrors (mirrors attribute; real classifiers decide). Multi-
  clause rows exist: `streamdiv_seam_script` → (blob, error_scan);
  `sig_on_stderr__bare` → (signature, error_scan). Boundary caveats:
  `error_scan` covers 3 distinct mechanisms; `allowlist_shape` masked
  when a non-absorbable line coexists; `exit` structurally dead; the
  label maps WHICH clause, not which mechanism.
- `raw_stdout_sha256`/`raw_stderr_sha256` on every dual_classify record —
  the same-input gate: both verdicts provably consumed identical bytes;
  reclass rows digest-match their source arm. Boundary caveats: hashes
  bind decoded text not raw pipe bytes (b"\xff"≡b"\xfe"→same sha);
  empty-vs-absent indistinguishable; strict-decode DoV class unchanged.
- TIMEOUT captures are nondeterministic (stderr tail spread; seam
  fabrication possible under timeout; truncation byte-granular mid-line)
  — drain scheduling is verdict-inert on content but not on truncation.
- Prior rows + verdicts byte-stable; both upgrades are opt-in
  (`--probe-stream-attribution`, `--probe-midlineforge-ladder`); flagless
  battery unchanged at 88/88.

## Method notes

- `sleep`-offset ladders: patch the ARM's sleep by anchored edit or a real
  flag, never `re.sub('sleep [0-9.]+;', count=1)` — the reparent_gate's
  `sleep 0.05` precedes the midline arm in the fixture; a first-match sub
  silently runs the unmodified arm (two sibling scratch series hit this).
- Reader-side chunk timestamps (selector reads) give gap-edge resolution
  without fixture instrumentation; author-side CLOCK_REALTIME stamps on
  the write give the ~1.4–2.5ms spawn-overhead constant.
