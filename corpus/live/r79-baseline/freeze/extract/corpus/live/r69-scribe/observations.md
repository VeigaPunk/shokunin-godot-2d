# r69-scribe observations — fabrication-window REFERENT (gap-relative vs absolute)

Host: devin, Godot 4.7.2.stable.arch_linux.ed1daf0bf, CPython 3.14.7,
Linux x86_64 headless. All measurement under `corpus/live/r69-scribe/`.

## Independent crossed ladder (own harness, own probe patch)

Driver `gap_ladder.py` (sha `32ce2099…`): bounded Popen + selector-
timestamped dual-pipe reads; per run records exit, timeout, byte order
(H=head fragment, T=tail line, E=forged ERROR, E2=write_ppid echo),
spliced_line, signature_present, write_ppid vs godot_pid, chunk-arrival
times (t_head/t_err/t_tail -> write_pos_in_gap, gap_measured), per-channel
+ merged sha256, and verdict through the VERBATIM extracted
`classify_process` (segment shas `88728b23/749fa060/a886968f/3a6bc0e8` —
byte-identical pre- and post-author-diff; probes/meta only).

Scratch probe `proj/descendant_pipe_probe.gd` (sha `afd2dd0c…`) = HEAD
fixture `5c5c629a…` + `--midline-gap-ms=N` parse (default 200) feeding
both the `gap_ms=` banner and `OS.delay_msec` — the declared pattern,
semantically identical to the author's later-landed diff.

268 measured runs (declared grid + off-grid transition + crossed cells +
offset-sweep at gap=300 + extremes), byte-order ground truth 0 exceptions:

| cell (off,gap) | n | outcome | interpretation |
|---|---|---|---|
| (80,50) | 9 | post_tail 9/9 | write ~82ms lands past 50ms tail; sig INTACT |
| (80,{55..78}) | 36 | post_tail all | edge below write position |
| (80,{79,80,81}) | 30+16 | post_tail all (under load pos drifted 83–91) | |
| (80,82) | 6+16 | splice 6/6 quiet; 1 straddle + 15 miss loaded | band = write pos itself |
| (80,{84,86,90,95}) | 24 | splice all | |
| (80,{100,200,400,800}) | 32 | splice all | declared inside cells |
| (80,{20,30}) | 8 | post_tail all | far-below extreme |
| (80,1500) | 4 | splice all | no absolute ceiling |
| (120,50) | 6 | post_tail all | pos~126 < 198 yet missed — abs model falsified |
| (150,100) | 6 | post_tail all | pos~156 < 198 yet missed — falsified |
| (250,800) | 6 | splice all | pos~257 > 198 yet fabricated — falsified |
| (300,400) | 6 | splice all | pos~307 > 198 yet fabricated — falsified |
| (500,800) | 6 | splice all | pos~506 — deepest inside-write observed |
| (350,200) | 6 | post_tail all | control: outside both models |
| (40..280,300) | 20 | splice all | second edge located ~295–300 |
| (295,300) | 4 | mixed 1 splice/3 miss | jitter-split at the new edge |
| (310..350,300) | 8 | post_tail all | |

Per-rep invariant `splice ⟺ write_pos < measured_gap`: 268 runs, 1
exception — gap=82 rep11, pos==gapM==85.997 exactly: E and T arrived in
the SAME reader chunk; byte order H<E<T resolves it as a splice (the r68
edge-straddle resampled at chunk granularity). Not a violation — a
resolution limit, recorded as such.

- Edge in nominal-gap space == the write's own landing position:
  ~81.4–82.3ms quiescent, drifting to ~86–92 under battery load — the
  nominal edge MOVED with the write, proving position-in-gap is the
  referent, not any nominal constant.
- Second edge re-located at gap=300: offsets ≤280 splice, 295 mixed,
  ≥310 miss -> edge ≈ gap − spawn_overhead at BOTH 200 (~198) and 300
  (~298–300). An absolute-198 constant predicts misses at offsets
  200–280 gap=300 — 20/20 spliced instead.
- write_ppid: post-tail misses carry BOTH pre-death (write_ppid==
  godot_pid — child in teardown; e.g. gap=79 all 10 reps pre-death yet
  missed) and post-death writes (gap=50 7/8 post-death; (350,200) 0/6
  pre-death). Position in the gap decides; provenance does not. The
  author's landed meta encodes exactly this (write_pre_death data-only;
  byte order is ground truth).
- Wiring witness: median elapsed ≈ gap + ~0.55s across the declared
  ladder (0.57@50 .. 1.39@800) — the flag demonstrably reached
  delay_msec.
- cls=False on every run (both corruption shapes still reject — the
  window decides WHICH clause, never the verdict).

## Landed-diff replay (own --runs, absolute path)

Worktree carries the author's uncommitted diff (convention: sole tracked
writer; commit at integration). `descendant_pipe_probe.gd` +18
(`--midline-gap-ms`, banner+default 200 byte-stable), `run_battery.py`
+230 (`--probe-midlineforge-gapladder` meta + `raw_merged_sha256` on every
dual_classify record + same-input gate extended to sha256(so+se)).

- Flagless: `runs-landed-flagless/20261014T121013482915Z/verdicts.json`
  sha `40926fa9…` — **88/88 PASS, surface 34/34**, no opt-in artifacts.
- Flagged: `runs-landed-flagged/20261014T121035766840Z/` — **91/91 PASS**
  (`verdicts.json` sha `2c7de139…`): +1 additive row
  `probe_midlineforge_gapladder`. `midlineforge-gapladder-verdicts.json`
  sha `c8936a5f…` — **10/10 discriminations**, `referent_verdict:
  gap_relative`, landed {100,200,400,800} / missed {50} / no mixed.
  Their gap=50 reps all post-death (mine mixed — teardown jitter).
- Prior-row byte-stability (`compare_prior_rows.py` sha `44e9c1b8…`):
  stream-attribution payload byte-identical to the r68 receipt modulo
  volatile fields + `raw_merged_sha256` (24 dual records both sides,
  same 24 discriminations); ladder artifact identical modulo embedded
  pid values + the adjudicated r68 `signature_gap_ms` hygiene deletion;
  verdicts +1 additive row, 0 verdict/keyset mismatches.

## Pre-author replays (HEAD 5d66b4d, before the diff landed)

- Flagless `runs-flagless/20261014T120222723303Z/verdicts.json` — 88/88,
  surface 34/34.
- Flagged `runs-flagged/20261014T120636888767Z/verdicts.json` — FAIL
  1/90: `negative_transition` environmental flake (`SCRIPT ERROR:
  Cannot call method 'get_instance_id' on a null value` at
  scene_transition_negative.gd:22 — current_scene still null one frame
  after change_scene_to_packed under concurrent-lane load; fixture then
  hit the 120-frame watchdog). Cascaded into surface discrimination
  `census_bare_classifier_consistent` (row rejected for a non-allowlist
  reason). Passed in all three other runs — load-timing nondeterminism,
  not diff-caused. The `FAIL stream_reject` stdout line is the expected
  per-arm classification print (meta requires inner=False), not a verdict.

## Incident (reported verbatim)

While checking `git status` I mistakenly ran `git stash -q`, which
stashed the author's uncommitted worktree diff; I immediately ran
`git stash pop` — diff restored, identical +230/+18 stat, stash dropped.
Seconds-scale window; no sibling lane affected (their runs read the
committed tree / own copies). The stash command itself is on my
forbidden list; the accident and repair are recorded here unsoftened.

## Converge/diverge vs siblings

- Author (`corpus/live/r69-author/runs/…Z/midlineforge-gapladder-
  verdicts.json`): PASS, gap_relative, identical landed/missed sets.
  CONVERGE.
- Critic (`corpus/live/r69-critic/gap-sweep-results.json`, report
  `reports/round-69/r69-critic.md`): declared grid underpowered alone
  (4/5 cells non-distinguishing); their added cells (300,400),(300,800),
  (600,800) fab + (300,200) control miss + (80,50) miss — same verdict,
  E excluded > ~602ms. My crossed cells {(120,50),(150,100) miss;
  (250,800),(300,400),(500,800) fab} + second-edge offset sweep supply
  both horns independently. CONVERGE on verdict and on the needed cells.
- Boundary/baseline/simplifier: scratch present; not yet reported at
  write time.
