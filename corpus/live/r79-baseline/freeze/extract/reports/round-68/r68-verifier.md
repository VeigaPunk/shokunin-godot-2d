# Round 68 verifier report — independent non-author replay of f754546

Seat: verifier (named, independent, NON-AUTHOR). Verified the committed tree,
not the author's claims. Host: `/usr/bin/godot` 4.7.2.stable.arch_linux.ed1daf0bf,
python 3.14.7, Linux x86_64. Commit under test: `f754546`. Committed file
identity re-pinned before any run: `run_battery.py` sha256
`7c4214360970860dff5d69b47f3e5aad3dc707e212652984b871186fd431c214`,
`descendant_pipe_probe.gd` `5c5c629ac187b11832c825c3f510baeab98e81517e01b65491426840f4a39d1f`
— both byte-equal to the author's declared post-diff hashes.

## Replay evidence (my own --runs under corpus/live/r68-verifier/runs)

| run dir | flags | verdict | artifact |
|---|---|---|---|
| 20261014T113409881703Z | (none) | PASS 88/88 | — |
| 20261014T113649697385Z | --probe-stream-attribution | PASS 89/89 | stream-attribution-verdicts.json |
| 20261014T113804001922Z | --probe-midlineforge-ladder | PASS 89/89 | midlineforge-ladder-verdicts.json |

Row-vs-row comparison against `r68-author` and `r68-baseline` verdicts on the
author's 7-field criterion (script, flags, expected_exit, actual_exit,
signature, verdict, error): **0 mismatches in all five comparisons**
(flagless↔author 88 common, flagless↔baseline 88, sd↔author 89, sd↔baseline 89,
ladder↔author 89). Full-row diffs after scrubbing are exclusively volatile:
pids, elapsed/`signature_observed_at`/`marker_observed_at` timings, run-dir
paths, ASLR load/backtrace addresses, stdout↔stderr merged-concat interleave
order, a 4th-decimal `transient_modulate` sample wobble, and (vs baseline only)
the expected `descendant_pipe_probe.gd:125`→`:132` push_error line reference —
the r68 fixture edit moved the call site; the receipt records this in a field
literally named `provenance_only_line_diff`.

## Per-claim verdicts

### Claim 1 (ladder bound) — AGREE

My ladder replay, verbatim outcome grid:

| offset | my outcome | reps_landed | signature_observed | write_ppid==godot_pid | inner_classification |
|---|---|---|---|---|---|
| 0 | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 40 | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 80 | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 120 | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 160 | fabricated | 3/3 | F,F,F | T,T,T | False ×3 |
| 240 | missed | 0/3 | T,T,T | T,T,T | False ×3 |

18/18 unanimous, zero mixed; `measured_window` =
landed{0,40,80,120,160} missed{240} lo=0 hi=240. All 8 discriminations True on
my artifact, including `window_is_strict_threshold`,
`fabrication_iff_signature_destroyed`, `over_gap_240ms_never_fabricates`.
Landed splice is byte-exact and unique across reps:
`DESCENDANT_PIPE_PROBE: expected ERROR: DESCENDANT_PIPE_MIDLINE forged splice`
(one distinct line; starts with head prefix, carries the forged ERROR). The
240ms record shows signature intact on its own line + standalone ERROR line +
pre-death provenance (`write_ppid==godot_pid`) — reject via error clause, not
fabrication.

### Claim 2 (bound semantics) — AGREE, with my own numbers

I wrote my own instrumented probe
(`corpus/live/r68-verifier/spike/proj/v_timing_probe.gd` + `run_timing.py`,
independent of the author's spike): child reports head/tail print timestamps
on stderr via `Time.get_unix_time_from_system`, descendant reports
`date +%s%3N` immediately at its write — same CLOCK_REALTIME domain. 33 runs,
offsets {0,40,80,120,160,190,195,198,200,205,240} × 3:

- measured gap `tail−head` = **200–201ms** (mean 200.12) — `delay_msec(200)`
  accurate to ~1ms, matches author.
- descendant first write lands at `offset + {2,3}ms` relative to head flush
  (mean +2.09ms; author measured ~2.5ms — same order, mine marginally lower).
- signature corrupted (write inside gap): offsets 0–195 all reps; **nominal
  198 = the race edge (1/3 corrupted, write_rel_head = 200 = gap end)**;
  ≥200 all reps intact. My measured effective nominal bound ≈ **[0, ~198)**,
  strictly inside the 200ms gap — consistent with the author's ~197–198 and
  the critic's ~198.4 (whose edge-Bernoulli observation my 198 cell
  independently reproduces).

Instrumentation caveat (declared, not a disagreement): my probe's descendant
writes `date` output *before* the forged line, so the timestamp write splices
first and the ERROR lands standalone — I measured *first-write arrival*, which
is the bound-relevant quantity. The real fixture's first stdout write IS the
forged line (`sleep`+`read` emit nothing), so the ladder's head+ERROR fusion is
unaffected. The author's spike shares this instrumentation shape.

### Claim 3 (receipt upgrades) — AGREE

Every divergence_table row carries `divergent_clause` from the declared
taxonomy; my table is identical to the author's map (all 9 rows, including
`streamdiv_seam_script → ("blob","error_scan")` and `stream_reject →
("error_scan",)`). I recomputed the clause signature **from spec** — my own
reimplementation of both classifiers' clause logic
(`corpus/live/r68-verifier/recompute_clauses.py`, not run_battery's mirrors) —
over the raw captured streams in both the author's and my own artifacts:
9/9 rows agree on both. Row-level semantics verified, not just recomputed:
- `seam_script` two-clause attribution is real: merged concat fabricates
  `SCRIPT ERR`+`OR:` → `SCRIPT ERROR:` token (blob diverges) on a line that
  also carries `ERROR:` (scan diverges); per-stream checks see neither.
- `stderr_structured → allowlist_shape`: merged's structured-entry matcher
  absorbs the chain-incomplete line that `line_allowed` (exact/comma only)
  rejects — shape asymmetry, correctly distinguished from scan coverage.
- `stream_reject → error_scan`: the non-`ERROR:` stderr line is stderr-strictness
  reject under streams while merged never scans it — filed under error_scan
  per the taxonomy's own definition (stderr-line strictness), consistent.
sha256 gate: recomputed `sha256(raw_stdout)`/`sha256(raw_stderr)` from captured
bytes for all 15 dual records (9 table rows + 6 allowlist_reclassifications)
in my artifact and the author's — all match; each reclassification's digests
equal its source arm's. Discriminations: 24/24 True on my run (r67-era
artifacts confirmed at 20 → the 20→24 count is exact), incl.
`divergent_clause_map_exact`.

### Claim 4 (prior stability) — AGREE

Flagless 88/88 PASS; `--probe-stream-attribution` 89/89;
`--probe-midlineforge-ladder` 89/89 (each flagged run adds exactly its one meta
row). Surface meta `probe_error_clause_surface` discriminations 34/34 all True
on both my flagless and ladder runs. Bare midlineforge arm byte-stable in
observable output: flagless `surface_midlineforge` record carries flags
`["--spawn-midlineforge"]` only, produces the identical spliced line and
`signature_observed=False`, `inner_classification=False`.

### Claim 5 (diff shape) — AGREE

`git show f754546` confirms `descendant_pipe_probe.gd` +17/−4 (param parse
inside the `elif midline_forge:` branch, default `midline_offset_ms := 80`,
`"sleep %d.%03d"` formatting) and `run_battery.py` +302/−2. The entire ladder
block sits inside `if args.probe_midlineforge_ladder:` (run_battery.py:2043);
`--midline-offset-ms` is parsed only inside the midline_forge branch, so it is
inert without `--spawn-midlineforge`. Precision note: the spawned shell string
for the default arm is `sleep 0.080` vs the old literal `sleep 0.08` —
byte-different command text, semantically identical delay, invisible in every
observable field (0 verdict mismatches above).

## Opt-in proof + seed immutability

- Flagless run dir contains NO `midlineforge-ladder-verdicts.json`, NO
  `probe_midlineforge_ladder` row, and grep of flagless stdout/run commands
  finds zero `midline-offset` references. Ladder spawns only under the flag.
- `git status corpus/fixtures/` empty before AND after all three replays; the
  battery copies fixtures into `runs/<stamp>/scratch` (run_battery.py:124–141)
  and writes only there. `corpus/knowledge/seed.md` untouched.

## Bounds of this verification

- Edge granularity: my declared-grid replay agrees {160 land, 240 miss}; my
  instrumented edge ≈198 nominal races ~1ms wide (consistent with the critic's
  ~198.4 stochastic edge and the author's ~197–198). "Strict threshold" holds
  as a shape claim; the hi edge is jitter-bounded, not jitter-free — the
  ladder's `mixed` field records rather than hides that.
- Timing constant measured at +2–3ms on this host under verifier load; a
  busier host shifts the nominal edge (critic's ptrace observation), which is
  exactly why the bound is stated as nominal-minus-spawn-latency.
- No commits, no tracked-file writes, no subagents. Scratch only under
  `corpus/live/r68-verifier/`.

## Verdict

**AGREE 5/5** — all five claims verified by independent replay on the committed
tree: ladder grid identical (18/18, zero mixed, 8/8 discriminations), bound
semantics independently measured (write = nominal + ~2ms, gap 200–201ms,
effective nominal bound ≈[0,~198)), clause map + sha256 gate recomputed from
raw bytes (9/9 + 15/15), prior stability holds (88/88, 89/89, 89/89, 34/34
surface), diff additive and opt-in as claimed. 0 non-volatile mismatches.
