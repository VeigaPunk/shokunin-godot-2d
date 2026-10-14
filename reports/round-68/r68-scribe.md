# Round 68 scribe — midlineforge fabrication-window bound + receipt upgrades (host: devin)

Report+scratch seat. LEAF: no subagent dispatch, no tracked edits, no
commit/push/merge/rebase/stash/checkout. Write scope honored: this report +
`corpus/live/r68-scribe/` only. No prior r68-scribe scratch existed at
takeover (first pass created it); nothing partial to extend.

**Landing status:** the author's tracked diff landed mid-report —
`descendant_pipe_probe.gd` +21/−6 (`--midline-offset-ms=N` parameterization
of the fixed `sleep 0.08`, int-ms, default 80; worktree sha
`5c5c629ac187…`) and `run_battery.py` +304/−3 (`--probe-midlineforge-ladder`
flag + meta arm, `divergent_clause` + `raw_{stdout,stderr}_sha256` in
`dual_classify`; worktree sha `7c4214360970…`), both uncommitted at report
time (lane convention: sole tracked writer, work commit at integration).
HEAD at write: `1101cb37` (r67 report-last). I re-ran the landed arm
end-to-end under my own `--runs` (absolute path; /proc cmdline probes
below) and re-measured the window independently with my own probe+driver.

## Verdict on the declared claim — VERIFIED, and sharper than worded

Claim: "the fabrication window has a strict measured bound [lo,hi) inside
the signature gap, and the r66 seam fabrication holds exactly within it."

Independently measured on 256 real Godot runs of the arm (my own
parameterized copy of the tracked fixture + reader-side chunk-timestamped
pipe capture; verdicts through the verbatim extracted `classify_process`):

- **The bound is real and strict, and it is exactly the gap:** the
  fabrication lands iff the descendant's write reaches the captured stdout
  pipe between the `printraw(head)` flush and the `print(tail)` flush —
  write-position `pos ∈ [0, gap)` where the measured gap is
  **200.024–200.121ms** (mean 200.088, n=216 timed runs). Inside: the
  forged `ERROR:` line fuses into the head fragment (fabricated line) AND
  the signature substring is destroyed — the r66 dual-clause corruption.
  Outside (either side): the ERROR lands as its own line and the signature
  survives intact.
- **In nominal-offset space on this host the window is ≈ [0, 198.2]ms:**
  offsets 0–198 fabricate rep-perfectly (48/48 declared-set runs at
  {0,40,80,120,160}; +18/18 at {170,180,190,195,197,198}); the transition
  band is 198.05–198.35 (mixed: 15/16, 14/16, 12/16, 9/16, 3/16, 0/16 at
  .05/.10/.15/.25/.30/.35 — logistic midpoint ≈198.2); ≥198.5 never
  fabricates (116/116 post-tail). The nominal edge sits ~1.8ms under the
  200ms gap end because the write lands at `offset + spawn_overhead`,
  overhead = sh exec + `/proc/self/stat` read + printf ≈ **1.43–2.26ms**
  (mean ~1.8).
- **The below-window regime exists and is symmetric:** non-negative offsets
  cannot reach it (min observed pos ≈ 1.43ms — spawn latency exceeds the
  child's sub-ms head-emission path). Delaying the head
  (`--midline-head-stagger-ms`, my scratch knob) pushes the write
  pre-head: stagger 1 → pos 0.25–0.67 (still inside); stagger 2 → pos
  −0.26…−0.67 (**pre_head_standalone**); stagger 3/5/10 → pos −1.3…−8.7,
  all standalone. Same miss shape as post-tail: standalone ERROR line +
  intact signature.
- **A truncate/straddle edge shape exists:** at off=198.05 rep14 the
  ERROR write landed inside the gap but the `write_ppid=` echo landed past
  the tail — byte order H E T E2, `spliced_line` present, signature
  destroyed. The two descendant writes straddle the boundary within ~0.1ms
  of each other; the band is narrower than per-rep jitter (~0.4ms), so it
  only samples at the exact edge.
- **Verdict-level nuance the brief's wording misses:** `cls=False` on EVERY
  run in every regime — a missed write still rejects, via the standalone
  ERROR: line clause, not the splice. The window bound controls **which**
  corruption the record carries (fabricated-line + destroyed-signature vs
  standalone-error + intact-signature), never whether it rejects. The
  claim's "fabrication window" is about the splice, not the verdict —
  verified as such.
- **r66 holds exactly within it:** the fixed-80ms point sample sits
  mid-window (write pos ≈81.6–82.2 > 0, ≪200) and fabricates in 12/12 of
  my runs + 3/3 of the author's landed ladder.
- **write_ppid == godot_pid in every record in every regime** — pre-death
  provenance holds even for misses (the write is still pre-death, just
  outside the gap).

## Landed-arm replay (post-land, own scratch, absolute --runs)

```text
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --probe-midlineforge-ladder --probe-stream-attribution \
    --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r68-scribe/runs
    → exit 0
```

Receipt `runs/20261014T111859212661Z/` — `verdicts.json` sha256
`d42ae9382ac7…`: **90/90 PASS** (88 prior rows + `probe_error_clause_surface`
34/34 + `probe_stream_attribution` + `probe_midlineforge_ladder`). `/proc`
cmdline probe mid-run confirms the absolute runs path:
`/usr/bin/godot --headless --path …/r68-scribe/runs/20261014T111859212661Z/scratch --script res://slider_adjust.gd -- --repeat-right --focus-handoff`.

`midlineforge-ladder-verdicts.json` sha256 `a8a7a9f096e4…` — **8/8
discriminations true**: `ladder_all_reps_clean_exit0`,
`ladder_all_writes_pre_death`, `ladder_all_reps_reject`,
`point_sample_80ms_still_fabricates`, `over_gap_240ms_never_fabricates`,
`window_is_strict_threshold`, `fabrication_iff_signature_destroyed`,
`spliced_line_is_head_error_fusion`. Measured cells (3 reps each):
{0,40,80,120,160} → `fabricated` (spliced line present, signature
destroyed, `write_ppid==godot_pid`); 240 → `missed` (signature intact).
`measured_window = {landed:[0..160], missed:[240], lo_edge:0,
hi_edge:240}` — on the declared nominal set; my independent sweep refines
the true transition to ≈198.2ms (offset space) / the gap flush boundary
(write-position space). Their `bound_semantics` estimate "offset + ~2.5"
matches my measured +1.4–2.3ms.

**Flagless post-land run** (`runs-flagless/20261014T112326985567Z/
verdicts.json` sha256 `3dbb7f5383bd…`): **88/88 PASS**, no ladder or
stream-attribution artifacts written — the opt-in claim verified directly.

## Receipt-shape upgrades — verified on the landed artifact

`stream-attribution-verdicts.json` sha256 `dba0461e1234…`, verified by
`check_receipt_upgrades.py` (sha `252f0524680e…`):

- **`divergent_clause` present on all 9 divergence_table rows**, values
  exactly the gated map:
  `stream_accept ()`, `stream_reject (error_scan)`,
  `streamdiv_stdout_error (error_scan)`, `streamdiv_stderr_error ()`,
  `streamdiv_stderr_structured (allowlist_shape)`,
  `streamdiv_sig_on_stderr (signature)`, `streamdiv_seam_error
  (error_scan)`, `streamdiv_seam_script (blob, error_scan)` — correctly
  multi-clause: the seamed `SCRIPT ERR`+`OR:` line trips BOTH the blob
  token and the ERROR:-line scan — `streamdiv_seam_sig (signature)`.
  Beyond the table: `sig_on_stderr__bare` (reclass row) gets
  `(signature, error_scan)` — baring the allowlist un-exempts the
  stderr-carried signature line, so stderr strictness diverges too. The
  clause attribution is computed per-clause on the same captured streams
  (mirror matchers attribute; real classifiers decide — the r66
  `surface_allowed_error` precedent).
- **`raw_stdout_sha256` + `raw_stderr_sha256` on all 24 dual-shaped
  records** (7 arms + 2 pair + 6 reclass + 9 table rows). Independent
  recompute: all 7 arm records' digests match `sha256(raw_stdout)`/
  `sha256(raw_stderr)` over their carried streams; both pair rows match
  `results[]`'s captured streams; all 6 reclass rows digest-match their
  source arm's digests (same-input gate closes the chain — reclassified
  inputs are provably the same bytes).
- **Prior rows byte-stable:** vs the r67 artifact (`r67-scribe/runs/
  20261014T095922857280Z/`): divergence_table, pair_reclassifications,
  allowlist_reclassifications, mode, bounded_claim **identical** after
  subtracting the 3 additive fields; discriminations = 20 prior keys all
  present/true + 4 new additive keys; verdicts.json: 89 shared rows with
  identical key sets and verdicts, +1 additive row. Arm `command` arrays
  differ only in the scratch path (r67's was relative; mine absolute per
  brief).

## Converge/diverge vs sibling seats

- **Author spike** (`corpus/live/r68-author/spike/`): instrumented probe
  (CLOCK_REALTIME both sides) — splice at write_rel_head ∈ [2,162],
  miss at ≥202 — **converges** with my bound. ⚠ erratum:
  `run_spike_real.py`'s `re.sub(r"sleep [0-9.$A-Z_]+;", …, count=1)`
  patches the reparent_gate's `sleep 0.05` (fixture line 132, first match
  in file order), never the midline arm's `sleep 0.08` (line 159) — its
  `spike-real-results.json` "spliced at every offset incl. 240" rows are
  21 runs of the unmodified 80ms arm, not evidence about the window. The
  LANDED code is correctly parameterized (`--midline-offset-ms` parsed in
  `_initialize`, landed ladder reproduces my bound), so the erratum is
  scratch-only — flagged for the author report's evidence trail.
- **Critic** (`corpus/live/r68-critic/`): parameterized replica probe
  (`critic_midline_probe.gd`, `--midline-offset-ms`/`--gap-ms`/
  `--head-stagger-ms`) — same parameterization shape as mine,
  independently written. CONVERGE on design.
- **Scout** (`corpus/live/r68-scout/`): two series — `t_*` env-var arm
  (`sleep $MIDLINE_SLEEP`, CORRECT: t_0.24 shows signature intact +
  DESC_WRITE_MS 42ms post-tail → post_tail, convergent); `off*_r*.out`
  series shows spliced at 240 — consistent with the same first-match
  regex hazard as the author's spike-real (their `timing_probe.py`
  `count=1` sub), not with the real arm's behavior.
- **Reviewer/baseline**: reviewer audited r67 HEAD while the diff landed
  (its runs are pre-land by construction); baseline's frozen pre-move
  replay is the byte-stability anchor my flagless run reproduces (88/88).

## Errata / limits

- `corpus/fixtures/__pycache__/` appeared alongside the author's battery
  run (interpreter cache, untracked); noted, not mine to remove.
- My ladder's `--midline-offset-ms` accepts floats (finer edge resolution:
  the 198.05–198.35 transition band is unrepresentable in the landed int-ms
  arm — declared set is int anyway, no gap in their claim).
- The gap itself is `OS.delay_msec(200)` + one print flush ≈ 200.02–200.12ms
  measured; jitter budget ~0.1ms. The nominal-offset edge (~198.2) is
  `gap − spawn_overhead`; overhead is host-dependent (sh exec + stat read),
  so the *declared* bound [0,240) is host-portable wording while the tight
  edge is this-host.
- Bounds: Linux headless Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
  CPython 3.14.7 POSIX pipes; classifier-level verdicts only — no gameplay,
  exported-build, or Windows/macOS claim.

## Draft — `corpus/lessons/r68-midlineforge-fabrication-window.md`

```markdown
# R68 — midlineforge fabrication window measured as an offset ladder (Godot 4.7.2 headless)

Sources: `reports/round-68/r68-{author,critic,reviewer,scribe,...}.md`;
`corpus/fixtures/run_battery.py` `--probe-midlineforge-ladder` meta +
`divergent_clause`/`raw_*_sha256` upgrades in the r67
`--probe-stream-attribution` block (worktree shas: battery `7c421436`,
fixture `5c5c629a`; commit TBD at integration);
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
split); ≥198.5 misses always. The nominal edge = gap − spawn_overhead,
overhead = sh exec + /proc/self/stat read + printf ≈ 1.4–2.3ms. The
below-window regime (write before head) is unreachable by non-negative
offsets — min pos ≈1.43ms — but exists under a delayed head: same
standalone-ERROR + intact-signature miss shape.

Three regimes, one boundary each side:
- pre-head / post-tail: ERROR lands standalone, signature INTACT,
  verdict still FAIL (error-scan clause) — a MISS changes which clause
  corrupts, never the verdict.
- inside: head+ERROR fuse (fabricated line), signature substring
  DESTROYED, verdict FAIL (dual-clause).
- edge straddle (rare, ~0.1ms band): ERROR inside while write_ppid echo
  lands past the tail (order H E T E2).

write_ppid==godot_pid in every regime — pre-death provenance is a write
property, not a splice property.

## The receipt upgrades (r67 meta arm)

- `divergent_clause`: per divergence_table row, the exact classifier
  clauses that diverged, taxonomy {exit,signature,error_scan,blob,
  allowlist_shape} — measured attribution, not a relabel: computed by
  re-deriving each clause's verdict on the SAME captured streams through
  allowlist mirrors (mirrors attribute; real classifiers decide). Multi-
  clause rows exist: `streamdiv_seam_script` → (blob, error_scan);
  `sig_on_stderr__bare` → (signature, error_scan).
- `raw_stdout_sha256`/`raw_stderr_sha256` on every dual_classify record —
  the same-input gate: both verdicts provably consumed identical bytes;
  reclass rows digest-match their source arm (chain verified).
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
  both channels agree to ~1ms.
```

## Draft — LOG.md round entry

```markdown
## Round 68 — devin host — depth/calibration: midlineforge fabrication-window bound + stream-meta receipt upgrades

- Declared (author dispatch brief; retroactive record): pin the
  fabrication-window bound on midlineforge as a measured ladder — sweep
  descendant write offsets {0,40,80,120,160,240}ms into the 200ms
  signature gap; claimed strict bound [lo,hi) inside the gap with the r66
  fabrication holding exactly within. Plus two receipt upgrades on the
  r67 stream-attribution meta: `divergent_clause` per divergence_table row
  and sha256(raw_stdout)+sha256(raw_stderr) per dual_classify record.
  Opt-in only; prior rows + surface meta byte-stable.
- Wave `shokunin-train-20261014-w8`: leaf set
  `reports/round-68/r68-{author,baseline,boundary,critic,reviewer,scout,
  scribe,simplifier,verifier}.md`, disjoint scratch `corpus/live/r68-*/`.
- Author `reports/round-68/r68-author.md` (diff landed, uncommitted at
  write): `descendant_pipe_probe.gd` `--midline-offset-ms=N` (default 80,
  int-ms); `run_battery.py` +304 — `--probe-midlineforge-ladder` meta
  (6 offsets × 3 reps through surface_run, 8 discriminations, measured_
  window receipt) + `divergent_clause`/`raw_*_sha256` in dual_classify
  (+4 discriminations).
- Measured (scribe independent, ~256 real-pipe runs + landed replay):
  window = write-position ∈ [0, gap) exactly — gap 200.02–200.12ms;
  nominal-offset bound ≈[0, 198.2] (transition band 198.05–198.35,
  ≥198.5 never fabricates); below-window regime real (pre-head via
  head-stagger); straddle edge shape observed (E inside, E2 past tail);
  write_ppid==godot_pid in every regime. Landed ladder: 90/90 flagged,
  88/88 flagless, surface 34/34, meta PASS ×2. Receipt upgrades verified:
  9/9 rows carry clause (exact map incl. multi-clause seam_script), 24/24
  dual records digest-verified, r67 artifact rows byte-identical modulo
  additive fields.
- Erratum: author `run_spike_real.py` + scout `off*` regex-patched the
  reparent_gate `sleep 0.05` (first match), not the midline arm's
  `sleep 0.08` — their all-offsets-spliced rows are the unmodified 80ms
  arm; the landed flag + both instrumented probes measure the true bound.
- Non-author `reports/round-68/r68-verifier.md`: TBD.
- Per-axis verdicts (Sol `reports/round-68/r68-adjudicator.md`): TBD.
  Bounded: classifier-level verdicts only, Linux headless 4.7.2, CPython
  POSIX pipes, this host's ~1.4–2.3ms spawn overhead; nominal edge moves
  with host latency. Work commit TBD; report-last follows.
```

## Artifact inventory (all `corpus/live/r68-scribe/`)

- `ladder.py` sha256 `21071d5474a7…` — selector-timestamped dual-pipe
  driver + verbatim classifier verdicts
- `extract_classifiers.py` sha256 `58b8e1c1c4b1…` — ast-segment extraction
  (`88728b23`/`749fa060`/`a886968f`/`3a6bc0e8`, unchanged post-land)
- `check_receipt_upgrades.py` sha256 `252f0524680e…` — divergent_clause +
  digest verifier
- `proj/descendant_pipe_probe.gd` sha256 `3f7806b6eaba…` — tracked fixture
  `92a40d70e31d…` + `--midline-{offset,gap,head-stagger}-ms` patch
- `declared-ladder-results.json` (48 runs, {0,40,80,120,160,240}×8),
  `hi-edge-results.json` (72, {170…220}×6), `straddle-dense-results.json`
  (96, {198.05…198.35}×16), `provenance-results.json` (12, full streams),
  `prov-prehead-results.json` (3), `stagger-{1,2,3,5,10}-results.json` (25)
- `runs/20261014T111859212661Z/` — landed replay: `verdicts.json` sha
  `d42ae9382ac7…` (90/90), `midlineforge-ladder-verdicts.json` sha
  `a8a7a9f096e4…` (8/8), `stream-attribution-verdicts.json` sha
  `dba0461e1234…` (9 rows + 24 dual digests verified)
- `runs-flagless/20261014T112326985567Z/verdicts.json` sha `3dbb7f5383bd…`
  (88/88, no opt-in artifacts)
- `battery-r68-landed.stdout` sha `df8961254391…` / `battery-r68-flagless
  .stdout` sha `0dde48b795ae…`; `sha-manifest.txt`; `observations.md`;
  `smoke.out`/`.err`
