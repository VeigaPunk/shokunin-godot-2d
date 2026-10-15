# Round 68 author report — midlineforge fabrication-window LADDER + stream-attribution receipt upgrades (host: devin)

Seat: author (ONLY tracked-file writer), lane `game-dev-2d`, declared
axis-move (verbatim brief): pin the fabrication-window bound on
midlineforge as a measured ladder — the descendant write offset into the
200ms signature gap was a point sample (80ms); sweep {0,40,80,120,160,240}ms
to find the measured window edges (below gap → fabricated line lands
inside; at/over → misses or truncates). Declared falsifiable claim: the
fabrication window has a strict measured bound [lo,hi) inside the signature
gap, and the r66 seam fabrication holds exactly within it. Additionally two
receipt-shape upgrades on the r67 stream-attribution meta: a
`divergent_clause` signature per divergence_table row and
sha256(raw_stdout)+sha256(raw_stderr) per dual_classify record (same-input
gate). Opt-in probes only; every prior row + surface meta byte-stable.

## Outcome — claim CONFIRMED (strict bound measured) with one precision refinement

The fabrication window is a strict measured bound: every nominal offset
whose descendant write reaches the captured stdout pipe between the
signature head flush and the tail flush fabricates; offsets at/over the
edge miss. Measured on the real fixture, 3 reps per offset, 18/18 reps
unanimous (zero mixed cells):

| nominal offset | outcome | reps_landed | signature_observed | write_ppid==godot_pid | inner_classification |
|---|---|---|---|---|---|
| 0ms | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 40ms | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 80ms | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 120ms | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 160ms | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 240ms | missed | 0/3 | T,T,T | T,T,T | False ×3 |

`measured_window` in `midlineforge-ladder-verdicts.json`:
`landed_offsets_ms=[0,40,80,120,160]`, `missed_offsets_ms=[240]`,
`mixed=[]`, `lo_edge_ms=0`, `hi_edge_ms=240`, nominal gap 200ms.

**Precision refinement (the "misses" edge is BELOW the nominal gap end):**
an instrumented scratch copy
(`corpus/live/r68-author/spike/proj/midline_timing_probe.gd`, child reports
head/tail `print`-call timestamps on stderr, descendant reports
`date +%s%3N` at write — same CLOCK_REALTIME domain) measured:

- the gap itself is `tail_ms − head_ms` = **200–201ms** (delay_msec is
  accurate to ~1ms),
- the descendant write lands at **offset + ~2–3ms** relative to head
  (fork/exec + sh startup + sleep wake latency),
- nominal **200ms already misses**: `write_rel_head` = 202–203ms >
  gap 200–201ms — the write arrives ~2ms AFTER the tail bytes.

So the effective bound is `write_position < tail_flush`: nominal-offset
window **[0, ~197–198)ms**, strictly inside the 200ms gap — the bound is
real, strict, and monotone; the hi edge sits just under the gap end because
of constant ~2.5ms spawn latency, not jitter (jitter observed ≤1ms; 18/18
reps unanimous). Spike table:
`corpus/live/r68-author/spike/spike-results.json` (33 reps, offsets
{0..400}ms incl. 200/220/260/300: all ≥200 miss, all <200 splice).

### Scout-side caveat discovered during the spike (data integrity note)

The r68-scout `off_*` scratch runs showed fabrication at every offset
including 240ms — a probe artifact, not physics: the scout's
`re.sub(r'sleep [0-9.]+;', …)` matches `sleep 0.05;` inside
`reparent_gate` (descendant_pipe_probe.gd:132, file-order first) and never
touched the midlineforge `sleep 0.08` (:159). All `off_*` runs were the
same 80ms arm. My own first regex spike reproduced the artifact verbatim;
targeting the literal `"sleep 0.08; ` token
(`corpus/live/r68-author/spike/run_spike_real.py`) gives the true ladder
{0,40,80,120,160} land / {200,240} miss — agreeing with the instrumented
timing probe. Reported so the record is not silently contradicted by
`corpus/live/r68-scout/runs/off_*.out`.

## Landed diff (additive — +319/−6 across two tracked files)

- `corpus/fixtures/descendant_pipe_probe.gd` — sha256
  `92a40d70e31daa5048a4c49864d4ece276fbfbac8cb93f2cc6751c6c798caa91` →
  `5c5c629ac187b11832c825c3f510baeab98e81517e01b65491426840f4a39d1f`,
  **+17/−4**: `--spawn-midlineforge` descendant write delay parameterized
  as `--midline-offset-ms=N` (default 80 — the r66 point sample;
  `get_slice("=",1).to_int()` parse, `"%d.%03d"` formatting). Bare
  `--spawn-midlineforge` behaviour is unchanged (default 80 → the r66/r67
  surface arm is byte-identical in observable output).
- `corpus/fixtures/run_battery.py` — sha256
  `8d7e4d946e419c8f2fd4c8890cc2d3286f009b8434abc27392724d903c8a4634` →
  `7c4214360970860dff5d69b47f3e5aad3dc707e212652984b871186fd431c214`,
  **+302/−2**:
  - new opt-in flag `--probe-midlineforge-ladder` →
    `probe_midlineforge_ladder` meta row (one results row) +
    `midlineforge-ladder-verdicts.json` artifact. 6 offsets × 3 reps via
    the surface meta's `surface_run` bounded-Popen record; per rep pins
    `spliced_line`/`fabrication_landed`/`signature_observed`/`write_ppid`/
    `inner_classification`; 8 discriminations (all True): all reps clean
    exit-0 + pre-death writes + all reject; 80ms reproduces fabrication;
    240ms never fabricates; the landed set is a strict threshold
    (max landed < min missed, mixed cells must sit inside the band);
    fabrication ⇔ signature destroyed per rep; spliced line is byte-exact
    head+ERROR fusion.
  - `divergent_clause` inside `dual_classify` (hence every
    divergence_table row + every allowlist_reclassification + pair
    reclassification record): clause-signature list re-derived per clause
    on the same captured streams through `sd_merged_line_allowed` /
    `sd_stream_line_allowed` mirrors (attribution only — verdicts stay the
    real `classify_process`/`classify_streams`; the r66
    `surface_allowed_error` census precedent).
  - `raw_stdout_sha256`/`raw_stderr_sha256` inside every dual_classify
    record — the same-input gate: a dual record now proves both classifiers
    consumed byte-identical captured streams.
  - 4 new discriminations in `sd_discriminations` (20 → 24, all True):
    `divergent_clause_map_exact`, `divergent_clause_nonempty_iff_divergent`,
    `divergent_clause_taxonomy_bounded`, `dual_records_same_input_digests`
    (arm digests == sha256 of each arm's own raw streams; pair rows ==
    accept/reject raws; each reclassification == its source arm's digests).

Measured `divergent_clause` map (divergence_table, 9 rows):

| row | merged | streams | divergent_clause |
|---|---|---|---|
| stream_accept | T | T | [] |
| stream_reject | T | F | ["error_scan"] |
| streamdiv_stdout_error | F | T | ["error_scan"] |
| streamdiv_stderr_error | F | F | [] |
| streamdiv_stderr_structured | T | F | ["allowlist_shape"] |
| streamdiv_sig_on_stderr | T | F | ["signature"] |
| streamdiv_seam_error | F | T | ["error_scan"] |
| streamdiv_seam_script | F | T | ["blob","error_scan"] |
| streamdiv_seam_sig | T | F | ["signature"] |

`streamdiv_seam_script` legitimately carries two clauses — the fabricated
merged line trips the `SCRIPT ERROR:` blob clause AND contains `ERROR:` so
the per-line error scan rejects it too; the list signature records both
(this is the measured answer, not a relabel: the boundary seat's
"collision" probe can distinguish rows sharing a single clause only when
the mechanism is genuinely single).

## Exact evidence

Canonical root `~/Projects/shokunin/game-dev-2d-shokunin`
(`/usr/bin/godot` = 4.7.2.stable.arch_linux.ed1daf0bf):

- Flagless: `python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot
  --runs corpus/live/r68-author/runs` → exit 0,
  `runs/20261014T111657543202Z/verdicts.json` **PASS 88/88**; stdout
  `corpus/live/r68-author/battery.stdout`.
- `--probe-stream-attribution`: → exit 0,
  `runs/20261014T111901822448Z/verdicts.json` **PASS 89/89**;
  `stream-attribution-verdicts.json` carries 24/24 discriminations,
  per-row `divergent_clause` + sha256 fields.
- `--probe-midlineforge-ladder`: → exit 0,
  `runs/20261014T112049887076Z/verdicts.json` **PASS 89/89**;
  `midlineforge-ladder-verdicts.json` carries the 6×3 ladder +
  measured_window + 8/8 discriminations.
- Full eight-flag (r67's seven + `--probe-midlineforge-ladder`): → exit 0,
  `runs/20261014T112303089118Z/verdicts.json` **PASS 100/100**.
- `--fault-injection` leg: → exit 0,
  `fault-runs/20261014T112658041757Z/fault-verdicts.json` outer **PASS**,
  designed inner `fault_hang`/`fault_unrelated_error` FAILs unchanged.
- Prior-row byte-stability, 7-field diff
  (script, flags, expected_exit, actual_exit, signature, verdict, error):
  - vs r68-baseline flagless frozen-HEAD replay
    (`corpus/live/r68-baseline/runs/20261014T104854073132Z/verdicts.json`):
    **88 common rows, 0 mismatches**; `probe_error_clause_surface`
    discriminations key-set identical, all-True, 34/34; structural diff
    shows only volatile fields (pids, elapsed_seconds, run-dir paths).
  - vs pretree HEAD seven-flag run
    (`corpus/live/r68-author/pretree-runs/*/verdicts.json`, HEAD fixtures
    materialized via `git archive HEAD corpus/fixtures | tar -x` into
    `pretree/`; runner sha `8d7e4d94…`, fixture sha `92a40d70…`):
    **99 common rows, 0 mismatches**; new-only `["probe_midlineforge_ladder"]`.
- Spike evidence: `corpus/live/r68-author/spike/{run_spike.py,
  run_spike_real.py, spike-results.json, spike-real-results.json,
  proj/, proj2/}` — instrumented timing (head/tail/write ms, same clock)
  plus real-fixture sleep-patch runs.

## Files written (inside brief scope only)

- tracked: `corpus/fixtures/descendant_pipe_probe.gd` (+17/−4),
  `corpus/fixtures/run_battery.py` (+302/−2)
- report: `reports/round-68/r68-author.md` (this file)
- scratch: `corpus/live/r68-author/{spike/, smoke/, runs/, pretree/,
  pretree-runs/, fault-runs/, battery*.stdout/.stderr, fault.stdout,
  pretree-battery.stdout/.stderr}`

## Remaining risks / blockers

- **Bound granularity**: the declared ladder resolves the hi edge to
  (160,240]ms nominal; the instrumented spike tightens it to ≈197–198ms
  nominal (write_position < tail flush at the 200ms gap end minus ~2.5ms
  constant spawn latency). A nominal offset in (160,200) near the edge —
  e.g. 190–200 — is untested in the *tracked* ladder (my scratch probe
  covered it: nominal 200 misses, i.e. effective ~202.5 > 200). If a
  finer bound is wanted, that is a follow-up ladder, not a gap in this
  one — the brief's declared offsets all behaved per the claim.
- **Jitter**: ≤1ms observed on this host across 18 ladder + 33 spike
  reps; a loaded host could widen the fork/exec latency and split a
  boundary cell — the ladder carries `reps_landed`/`mixed` so jitter is
  recorded, not hidden (a mixed cell would still satisfy the strict-
  threshold gate only inside the landed/missed band).
- **The edge is the pipe-arrival boundary**, not the read loop: the
  merged record's line structure is decided by byte order in the captured
  pipe; `divergent_clause`/`surface` classification sees only the drained
  text. Timing provenance (pre-death) is `write_ppid==godot_pid`, as r66.
- No blockers. Commit/push left to operator per seat rules.
