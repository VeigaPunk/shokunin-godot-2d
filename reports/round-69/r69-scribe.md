# Round 69 scribe — fabrication-window REFERENT pinned gap-relative + sha256(merged) receipt (host: devin)

Report+scratch seat. LEAF: no subagent dispatch, no tracked edits, no
commit/push/merge/rebase/checkout. Write scope honored: this report +
`corpus/live/r69-scribe/` only.

**Landing status:** the author's tracked diff landed mid-report and is
UNCOMMITTED at write time (lane convention: sole tracked writer, work
commit at integration). HEAD `5d66b4d` (r68 report-last). Diff:
`descendant_pipe_probe.gd` +13/−5 (`--midline-gap-ms=N`, default 200 —
byte-stable arm; feeds the `gap_ms=` banner AND `OS.delay_msec`) and
`run_battery.py` +228/−2 (`--probe-midlineforge-gapladder` flag + meta,
10 discriminations; `raw_merged_sha256 = sha256(so+se)` on every
dual_classify record + divergence_table rows + same-input gate). I
re-ran the landed arm end-to-end under my own `--runs` and measured the
referent independently with my own probe+driver BEFORE and AFTER the
land. Classifier segments byte-identical across the diff
(`run_process 88728b23`, `classify_process 749fa060`,
`classify_streams a886968f`, `classify_audio_process 3a6bc0e8` —
probes/meta only).

**Incident (verbatim):** while polling `git status` I mistakenly issued
`git stash -q`, which stashed the author's uncommitted worktree diff; I
immediately ran `git stash pop` and the diff returned with the identical
+230/+18 stat (`stash@{0}` dropped cleanly, no conflicts). The window
was seconds; no sibling lane reads the worktree diff. `git stash` is on
my forbidden-op list — recorded here unsoftened.

## Verdict on the declared claim — VERIFIED, and sharper than worded

Claim: the window follows `offset < gap` (gap-relative — fabrication iff
the write lands before the tail flush AT ANY gap size); falsified if
fabrication persists at gaps ≪80ms or fails at gaps ≫80ms.

Independently measured on **268 real Godot runs** of the arm (my own
`--midline-gap-ms`-patched copy of the HEAD fixture + reader-side
chunk-timestamped dual-pipe capture; verdicts through the verbatim
extracted `classify_process`; byte order = ground truth):

- **The declared grid reproduces exactly:** at offset=80, gaps
  {100,200,400,800} splice 8/8 each (fused `expected ERROR:` line,
  signature destroyed, `write_ppid==godot_pid`); gap=50 misses 8/8 —
  `post_tail` (write lands ~81.6–82.1ms, tail flushed ~50.1ms;
  signature INTACT, standalone ERROR line). Author's landed meta on my
  replay: `referent_verdict: gap_relative`, identical landed/missed
  sets, no mixed.
- **The nominal edge IS the write position:** transition at offset=80
  sits between gap=78 (all miss) and gap=82 (all splice), write position
  ~81.4–82.3ms quiescent. Under battery load the same write drifts to
  ~83–92ms and nominal gap {79,80,81,83} then MISSES (a straddle at 82)
  — the edge moved with the write, not with the nominal numbers. The
  bound is position-in-gap, measurable only in write-position space.
- **Absolute-write-latency (~198ms constant) falsified in BOTH
  directions** — the crossed cells the fixed-offset design cannot
  express:
  - absolute predicts FABRICATE, gap-relative predicts MISS:
    (120,50) → miss 6/6 (pos ~126ms < 198); (150,100) → miss 6/6
    (pos ~156ms < 198).
  - absolute predicts MISS, gap-relative predicts FABRICATE:
    (250,800) → splice 6/6 (pos ~257); (300,400) → splice 6/6
    (pos ~307); (500,800) → splice 6/6 (pos ~506). Control (350,200)
    → miss 6/6 (outside both models).
- **The edge re-locates at a second gap:** offset sweep at gap=300 —
  offsets ≤280 splice 4/4 each (pos 45–289), offset 295 MIXED (1
  splice/3 miss, pos 301–304 straddling gapM 300.1–303), offsets
  ≥310 miss 4/4 each. Edge ≈ gap − spawn_overhead at BOTH gaps
  (~198 at 200, ~298–300 at 300) — the offset ladder's ~198 edge was
  `200 − overhead`, never a constant.
- **No absolute ceiling:** gap=1500 splices 4/4 (write pos ~85–87
  inside a 1.5s window). Gap={20,30} miss 4/4 each.
- **Per-rep invariant** `splice ⟺ write_pos < measured_gap`: 268 runs,
  exactly ONE exception — gap=82 rep11, pos==gapM==85.997: ERROR and
  tail bytes arrived in the SAME reader chunk; byte order H<E<T
  resolves a true splice — the r68 edge-straddle resampled at chunk
  granularity (a resolution limit, recorded, not a violation).
  Byte-order check `splice ⟺ H<E<T`: 0/268 exceptions.
- **write_ppid is provenance, not the bound:** post-tail misses carry
  BOTH pre-death writes (child still in teardown — gap=79: 10/10
  pre_death yet missed) and post-death writes (gap=50: 7/8 post-death;
  (350,200): 0/6 pre_death). Position in the gap decides; death state
  does not. The author's meta encodes this exactly: `write_pre_death`
  is data-only, byte order is the ground truth, pre-death gated only on
  inside cells.
- **Verdict-level nuance (carried from r68):** `cls=False` on all 268
  runs — a miss still rejects via the standalone ERROR: clause. The
  referent decides WHICH corruption, never whether it rejects.
- **Wiring witness:** median elapsed ≈ gap + ~0.55s across the declared
  ladder (0.57s@50 → 1.39s@800) — the flag demonstrably reaches
  `delay_msec` (an unwired flag would hold ~0.75s at every gap).

## Landed-arm replay (post-land, own scratch, absolute --runs)

```text
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --runs .../corpus/live/r69-scribe/runs-landed-flagless     → exit 0
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --probe-midlineforge-gapladder --probe-midlineforge-ladder \
    --probe-stream-attribution \
    --runs .../corpus/live/r69-scribe/runs-landed-flagged      → exit 0
```

- **Flagless** `runs-landed-flagless/20261014T121013482915Z/verdicts.json`
  sha `40926fa9…`: **88/88 PASS, surface 34/34**, no opt-in artifacts —
  the opt-in contract verified on the landed diff.
- **Flagged** `runs-landed-flagged/20261014T121035766840Z/verdicts.json`
  sha `2c7de139…`: **91/91 PASS** — 88 prior + `probe_error_clause_
  surface` 34/34 + `probe_midlineforge_ladder` (8/8) +
  `probe_stream_attribution` + the additive row
  `probe_midlineforge_gapladder`.
- **`midlineforge-gapladder-verdicts.json`** sha `c8936a5f…`: **10/10
  discriminations true** (`gapladder_all_reps_clean_exit0`, `all_reps_
  reject`, `fabrication_iff_signature_destroyed`, `spliced_line_is_head_
  error_fusion`, `gap200_anchor_still_fabricates`, `sub_offset_gap_never_
  fabricates`, `sub_offset_signature_intact_post_tail`, `super_offset_
  gaps_always_fabricate`, `super_offset_writes_pre_death`,
  `window_referent_is_gap_relative`). Cells (3 reps each): {100,200,
  400,800} fabricated, 50 missed, none mixed; their gap=50 reps all
  post-death (mine mixed — teardown jitter, both shapes observed).
- **`midlineforge-ladder-verdicts.json`** sha `6ca50d5a…`: 8/8
  discriminations, cells {0,40,80,120,160} fabricated / 240 missed —
  identical to the r68 receipt (prior arm byte-stable under the new
  fixture: default gap 200 reproduces the historic arm byte-for-byte).

## Receipt upgrade — `sha256(merged)` verified on the landed artifact

`stream-attribution-verdicts.json` sha `6adc03f0…`, checked by
`compare_prior_rows.py` (sha `44e9c1b8…`) against the r68-scribe receipt
(`r68-scribe/runs/20261014T111859212661Z/`):

- **`raw_merged_sha256` present on all 24 dual-shaped records** (7 arms
  + 2 pair + 6 reclass + 9 table rows); the same-input gate recomputes
  `sha256(raw_stdout + raw_stderr)` per record — all self-consistent.
- **Prior rows byte-stable modulo the additive field:** after scrubbing
  volatile fields (command paths, pids, timing, the new digest) the
  ENTIRE payload — divergence_table, pair/allowlist reclassifications,
  discriminations (same 24 keys all true), bounded_claim — is
  byte-identical to the r68 artifact. verdicts.json: 90 shared rows,
  0 verdict mismatches, 0 key-set mismatches, +1 additive row.
  Ladder artifact: identical modulo embedded pid values + the already-
  adjudicated r68 `signature_gap_ms` hygiene deletion.
- The merged digest pins concat ORDER/separator (the r66 stderr+stdout
  caveat): `sha(so+se)`, `sha(se+so)`, `sha(so+"\n"+se)` are three
  distinct digests over identical channel contents — a merge-path drift
  invisible to the per-channel pair (critic's demonstration, §3 of
  `r69-critic.md`; consistent with my records: all 268 midline captures
  carry stderr_bytes=0, where the gate is trivially vacuous — its value
  lives on dual-channel rows like the streamdiv stderr arms).

## Pre-author replays (HEAD `5d66b4d`, before the diff landed)

- Flagless `runs-flagless/20261014T120222723303Z/verdicts.json` sha
  `206875e9…`: 88/88, surface 34/34.
- Flagged `runs-flagged/20261014T120636888767Z/verdicts.json` sha
  `8d788928…`: **1/90 FAIL** — `negative_transition` environmental
  flake: `SCRIPT ERROR: Cannot call method 'get_instance_id' on a null
  value` at `scene_transition_negative.gd:22` (`current_scene` still
  null one frame after `change_scene_to_packed` under concurrent-lane
  load; the fixture then hit its 120-frame watchdog, `ERROR: negative
  transition probe exceeded 120 frames`). Cascaded into surface
  discrimination `census_bare_classifier_consistent` (the row rejected
  on a NON-allowlist clause). The row passed in all three other runs —
  load-timing nondeterminism on PRE-author code, not diff-caused.
  (The `FAIL stream_reject` stdout line in both flagged runs is the
  expected per-arm classification print — the meta requires
  `inner_classification is False` for that arm; not a verdict.)

## Converge/diverge vs sibling seats

- **Author** (`corpus/live/r69-author/runs/20261014T121043188828Z/`):
  gapladder PASS, `gap_relative`, identical landed/missed sets; battery
  89/89 with the flag on. CONVERGE. Their probe diff is semantically
  identical to my scratch patch (same flag name, default 200, banner +
  delay wired); `write_pre_death` carried as data with byte order as
  ground truth — the same conclusion my ppid measurements forced.
- **Critic** (`corpus/live/r69-critic/gap-sweep-results.json`,
  `reports/round-69/r69-critic.md`): correct structural critique — the
  declared fixed-offset grid is underpowered alone (4/5 cells
  non-distinguishing; gap=50's miss also falsifies a wiring defect).
  Their added cells {(300,400),(300,800),(600,800) fab; (300,200)
  control miss; (80,50) miss} converge with my crossed cells and put
  the absolute-edge exclusion at write-time >~602ms; my (500,800) at
  pos ~506 and second-edge offset sweep at gap=300 are independent
  confirmations. Their wiring witness (elapsed_seconds ∝ wired gap)
  matches mine (≈ gap + 0.55s). Their `all_writes_pre_death` caveat
  lands: the author's meta gates pre-death only on inside cells —
  CONVERGE on verdict, cells, and caveats.
- **Boundary/baseline/simplifier:** scratch dirs present; no reports at
  write time.

## Errata / limits

- My `write_pos`/`gap_measured` are reader-side chunk timestamps
  (~50ms selector poll): fine for ms-scale edges, ties recorded when E
  and T share a chunk (1/268, resolved by byte order).
- Write position drifts with host load (~81.5 quiescent → ~86–92 under
  concurrent battery): nominal-cell outcomes near the edge are
  load-sensitive; the per-rep `pos < gap` predicate is not. The landed
  meta's fixed-offset cells sit ≥ ~17ms from the edge — robust by
  design.
- The declared grid's falsifier is one-directional: at offset=80 the
  absolute model only diverges from gap-relative where gap < write
  position — the reverse horn needs offset > ~198 with gap > offset
  (critic's §1); my crossed cells + gap=300 offset sweep supply it.
- `sha256(merged)` is derivable (a pure function of the already-pinned
  channels — it attests the merge function, adds no entropy) and
  vacuous on empty-channel records; consistent limits, honestly carried.
- Bounds: classifier-level verdicts only; Linux headless Godot
  `4.7.2.stable.arch_linux.ed1daf0bf`; CPython 3.14.7 POSIX pipes; this
  host's spawn overhead (~1.5–5ms quiescent→loaded); no gameplay,
  export, or non-Linux claim.
- One environmental flake observed (`negative_transition` null
  current_scene under load, PRE-author run): recorded for the ledger;
  fixture readiness, not verdict logic.

## Draft — `corpus/lessons/r69-fabrication-window-referent.md`

```markdown
# R69 — midlineforge fabrication bound's referent: gap-relative, not absolute (Godot 4.7.2 headless)

Sources: `reports/round-69/r69-{author,critic,scribe,...}.md`;
`corpus/fixtures/descendant_pipe_probe.gd` `--midline-gap-ms=N`
(default 200 — the r66/r68 arm is byte-stable); `run_battery.py`
`--probe-midlineforge-gapladder` meta + `raw_merged_sha256` on every
dual_classify record; author receipt `corpus/live/r69-author/runs/…/
midlineforge-gapladder-verdicts.json`; scribe independent measurement
`corpus/live/r69-scribe/{declared-gaps,gap-transition,gap-edge-fine,
gap-band-quiet,crossed,offset-sweep-gap300,extremes}-results.json`
(268 real-pipe runs, driver `gap_ladder.py` sha `32ce2099…`, scratch
probe sha `afd2dd0c…` = fixture `5c5c629a` + gap flag); critic
`corpus/live/r69-critic/gap-sweep-results.json`.
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
- Absolute-write-latency falsified BOTH directions by crossed cells:
  (120,50)+(150,100) miss though pos<198; (250,800)+(300,400)+
  (500,800) fabricate though pos>198; (350,200) misses (outside both).
- The nominal edge IS the write's landing position and moves with it:
  ~82ms quiescent, ~86–92 under load; nominal gap cells near the write
  position flip accordingly.
- Second edge re-located: offset sweep at gap=300 puts the transition
  at ~295–300 (295 mixed) — edge ≈ gap − overhead at both gaps.
- No ceiling: gap=1500 fabricates; no floor below the head flush.
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
  offset: crossed (offset,gap) cells are the minimal complete design.
- Gate pre-death only on inside cells: the ppid flip lags process
  teardown, so post-tail writes can sample write_ppid==godot_pid; byte
  order — never the ppid — is the post-tail ground truth.
- `negative_transition` readiness is load-sensitive: one observed
  flake where `current_scene` was still null a frame after
  `change_scene_to_packed` (SCRIPT ERROR at fixture :22 + 120-frame
  watchdog) under concurrent-lane load — environmental, not logic.
```

## Draft — LOG.md round entry

```markdown
## Round 69 — devin host — depth/calibration: fabrication-window referent (gap-relative vs absolute) + sha256(merged) receipt pin

- Declared (author dispatch brief; retroactive record): pin the
  fabrication-window bound's REFERENT — hold `midline_offset_ms=80`,
  sweep the signature gap {50,100,200,400,800}ms via a new
  `--midline-gap-ms` opt-in flag (same pattern as
  `--midline-offset-ms`); claimed the window follows offset<gap
  (gap-relative), falsified by fabrication at gaps ≪80ms or misses at
  gaps ≫80ms. Plus `sha256(merged)` on every dual_classify record (the
  merged-concat digest catches concat-order drift the per-channel
  digests can't see — r66 stderr+stdout caveat). Opt-in only; flagless
  88/88 + surface 34/34 + prior dual_classify rows byte-stable modulo
  the additive field.
- Wave `shokunin-train-20261014-w9`: leaf set
  `reports/round-69/r69-{author,baseline,boundary,critic,reviewer,
  scout,scribe,simplifier,verifier}.md`, disjoint scratch
  `corpus/live/r69-*/`.
- Author `reports/round-69/r69-author.md` (diff landed, uncommitted at
  write): `descendant_pipe_probe.gd` +13/−5 — `--midline-gap-ms=N`
  (default 200, byte-stable arm; feeds banner + delay_msec);
  `run_battery.py` +228/−2 — `--probe-midlineforge-gapladder` meta
  (5 gaps × 3 reps through surface_run, referent_verdict
  {gap_relative|absolute_write_latency|unclassified}, 10
  discriminations) + `raw_merged_sha256` in dual_classify +
  divergence_table + same-input gate.
- Measured (scribe independent, 268 real-pipe runs + landed replay):
  referent = gap — splice iff write position ∈ [0, gap), 0/268
  byte-order exceptions (1 same-chunk tie resolved to a straddle).
  Declared grid: {100,200,400,800} fab / 50 miss. Absolute ~198ms
  falsified BOTH horns: (120,50)+(150,100) miss with pos<198;
  (250,800)+(300,400)+(500,800) fabricate with pos>198; edge
  re-located ≈295–300 at gap=300 (offset sweep, 295 mixed); gap=1500
  fabricates; nominal edge = write position, drifts ~82→~89 under
  load; write_ppid provenance-only (pre-death misses + post-death
  misses both observed — position decides, not death). Landed replay:
  91/91 flagged, 88/88 flagless, 34/34 surface, gapladder meta PASS
  10/10, referent gap_relative. Byte-stability: stream-attribution
  payload identical to r68 modulo additive field + volatiles; ladder
  artifact identical modulo pids + adjudicated hygiene key.
- Critic correction absorbed (design-level): fixed-offset grid alone
  underpowered — added crossed cells supply both falsifier horns;
  `write_pre_death` carried as data (ppid flip lags teardown), byte
  order is ground truth; elapsed_seconds + banner as wiring witnesses.
- Flake observed (pre-author run, load): `negative_transition` null
  `current_scene` at fixture :22 → SCRIPT ERROR + watchdog; passed in
  3/4 runs — environmental readiness, recorded for the ledger.
- Non-author `reports/round-69/r69-verifier.md`: TBD.
- Per-axis verdicts (Sol `reports/round-69/r69-adjudicator.md`): TBD.
  Bounded: classifier-level verdicts only, Linux headless 4.7.2,
  CPython POSIX pipes, this host's load-dependent spawn overhead —
  the measured referent (write position vs tail flush) is
  host-portable, nominal edges are not. Work commit TBD; report-last
  follows.
```

## Artifact inventory (all `corpus/live/r69-scribe/`)

- `gap_ladder.py` sha `32ce2099…` — selector-timestamped dual-pipe
  driver, crossed (offset,gap) cells, verbatim-classifier verdicts
- `extract_classifiers.py` sha `64d3bb8c…` — ast-segment extraction
  (`88728b23`/`749fa060`/`a886968f`/`3a6bc0e8`, identical pre/post land)
- `compare_prior_rows.py` sha `44e9c1b8…` — byte-stability scrubber
- `proj/descendant_pipe_probe.gd` sha `afd2dd0c…` — HEAD fixture
  `5c5c629a…` + `--midline-gap-ms` patch (semantically identical to
  the landed diff)
- `declared-gaps-results.json` (40 runs, off80 × {50,100,200,400,800}
  ×8), `gap-transition-results.json` (66, gaps 55–95 ×6),
  `gap-edge-fine-results.json` (30, {79,80,81} ×10),
  `gap-band-quiet-results.json` (48, {81,82,83} ×16 under load),
  `crossed-results.json` (36, six discriminator cells ×6),
  `offset-sweep-gap300-results.json` (36, offsets 40–350 @ gap300),
  `extremes-results.json` (12, gaps {20,30,1500}), `smoke-results.json`
- `runs-landed-flagless/20261014T121013482915Z/verdicts.json` sha
  `40926fa9…` (88/88 + 34/34); `runs-landed-flagged/
  20261014T121035766840Z/` — verdicts sha `2c7de139…` (91/91),
  `midlineforge-gapladder-verdicts.json` sha `c8936a5f…` (10/10,
  gap_relative), `stream-attribution-verdicts.json` sha `6adc03f0…`
  (24 dual records + merged digests verified), `midlineforge-ladder-
  verdicts.json` sha `6ca50d5a…` (8/8, prior cells identical)
- `runs-flagless/…Z/verdicts.json` sha `206875e9…` (pre-author 88/88);
  `runs-flagged/…Z/verdicts.json` sha `8d788928…` (pre-author 89/90 —
  negative_transition flake)
- `battery-*.stdout` shas `ba9a45a5`/`4592f327`/`272c037d`/`260727d4…`;
  `sha-manifest.txt`; `observations.md`
