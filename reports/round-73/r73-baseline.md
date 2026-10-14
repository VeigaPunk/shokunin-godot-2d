# Round 73 baseline report — frozen HEAD replay + post-commit re-verify (host: devin)

Seat: g2d baseline (LEAF). Immutable before-state for the r73 wave: no
tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r73-baseline/` (`frozen/` gitignored by
`corpus/.gitignore:4 live/*/frozen/`, `frozen-extract/` by
`live/*/*extract*/`, `runs/` by `corpus/live/.gitignore:1 runs/`) plus
this report.

Timeline: HEAD frozen at `2dd108b` (archive 15:21:1xZ, extract done
15:22:00Z, replays 15:22:39Z–15:27:00Z). The r73 declared axis-move —
`pygame_probe.py`+`pygame_battery.py` topology-depth + node-census arm
(xconnector X4/X1: INFIX paced-flush, DETACH EOF-hold, FD2-INVERSION,
Node.js fd1-owner census) — **landed mid-session** as `43bef2d`
(committed 2026-10-14 15:43:36Z; author worktree divergence first
observed 15:34:22Z, mid-edit). The frozen surface `2dd108b` is the
move commit's **direct parent** (`git rev-parse 43bef2d^` = `2dd108b`)
— a provably pre-move before-state, and this baseline its
verified-stable referent.

## Frozen-tree provenance — archive + extracted replay (r69/r72 procedure)

- Frozen source: `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
  archive HEAD -o corpus/live/r73-baseline/frozen/HEAD-2dd108b647231e8adecc31de3d7ab0f1dc947d92.tar`
- HEAD frozen: `2dd108b647231e8adecc31de3d7ab0f1dc947d92`
  (`r72 report-last: adjudicator ADMIT + LOG + SCORECARD + 10 seat
  reports`, committed 2026-10-14T11:57:29-03:00); parent `fee5563`
  (r72 reorder arm) → `44127af` r71 report-last; chain carries r71
  pygame first contact `a993cbe`, r70 LOVE `ceba654`/`16d003c`, r69
  gapladder `9fb50aa`.
- Archive: **687,124,480 bytes**, sha256
  `5552cac0bd75867dd016a38a769569fba39bce00f4669c524239780bdedd199c`.
  `git archive HEAD | sha256sum` re-run = **identical** — deterministic.
  (The ignored-tar convention absorbed the growth: r72's was
  683,438,080 B; delta is r72 receipt accretion.)
- Tar members: 49,069 total = **44,863 non-dir entries** + 4,206 dirs;
  non-dir count == `git ls-files | wc -l` = 44,863 exactly
  (r72: 44,563 — delta +300 is r72-round committed receipts).
- No tracked nested snapshot dirs at HEAD (`git ls-tree -r HEAD
  --name-only | grep -cE '^corpus/live/[^/]+/(frozen|head|snapshot|base)/
  |^corpus/live/[^/]+/tree/'` → **0**). A broader grep
  (`frozen|/tree/|node_modules|extract`) matches 209 tracked paths, all
  incidental filenames — `extract_classifiers.py` copies, r66-simplifier
  `battery-extracted.*`/`runs-extracted/` (the pre-ignore-rule specimen
  the gitignore comments name), r72-baseline `extract-done.txt`.
- Extraction: `tar -xf` into `corpus/live/r73-baseline/frozen-extract/`
  (758M). Membership: `find . -type f` = 44,829 files + **34 symlinks**
  = 44,863 == `git ls-files` exactly; `comm -23`/`-13` both empty;
  symlink list `diff` vs `git ls-files` complement = clean, none
  dangling.
- Fixture digests in extract == `HEAD:` blob contents == live tree
  (pre-move) for all 7 checked: `run_battery.py` `f55c27d8…`,
  `pygame_battery.py` `077af0b5…`, `pygame_probe.py` `7c0f9c73…`,
  `love_battery.py` `25977ad9…`, `love_probe/main.lua` `a0afe6ca…`,
  `descendant_pipe_probe.gd` `c86bda84…`,
  `stream_attribution_probe.gd` `dc0b0d5c…`. (r72 move already inside
  this HEAD: probe `7c0f9c73…` is the post-`fee5563` byte.)
- `verdicts.json["seed"]` on godot runs records
  `…/r73-baseline/frozen-extract/corpus/fixtures`; love records
  `probe_dir: …/frozen-extract/corpus/fixtures/love_probe`; pygame
  records `probe: …/frozen-extract/corpus/fixtures/pygame_probe.py` —
  all three replays provably executed frozen-HEAD fixture bytes.
- Post-run `find frozen-extract -newer extract-done.txt` → **0
  entries**: extract stayed read-only-pristine.
- Pre-move token referents in the frozen fixtures (the r73 move's
  claimed surface): `infix`, `detach`, `fd2`, `node_census`, `paced`,
  `eof_hold`, `writeSync` = **0 occurrences** in both
  `pygame_probe.py` and `pygame_battery.py`; `reorder` = 25 (probe) /
  29 (battery) — the r72 arm present.

## Exact invocations

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`X=corpus/live/r73-baseline/frozen-extract`:

```
python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r73-baseline/runs
  # exit 0, runs/20261014T152239075708Z verdicts.json PASS 88/88

python3 $X/corpus/fixtures/love_battery.py \
  --runs corpus/live/r73-baseline/love-runs
  # exit 0, love-20261014T152243714938Z PASS 19/19

python3 $X/corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r73-baseline/pygame-runs
  # exit 0, pygame-20261014T152252487786Z PASS 55/55

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r73-baseline/runs --probe-stream-attribution
  # exit 0, runs/20261014T152414017636Z PASS 89/89
  #   + stream-attribution-verdicts.json

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r73-baseline/runs --probe-midlineforge-ladder
  # exit 0, runs/20261014T152533525776Z PASS 89/89
  #   + midlineforge-ladder-verdicts.json

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r73-baseline/runs --probe-midlineforge-gapladder
  # exit 0, runs/20261014T152659883512Z PASS 89/89
  #   + midlineforge-gapladder-verdicts.json
```

All six `.stderr` captures 0 bytes. Environment: Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), LOVE 11.5
(`/usr/bin/love`), Python 3.14.7 + pygame 2.6.1 / SDL 2.32.72,
`io.DEFAULT_BUFFER_SIZE` = 131072 (THIS build's constant), node
v24.21.0 present (the ARM-B census runtime) — same profile as r70–r72.

## Before-state receipt summary (frozen `2dd108b`, pre-move)

- Flagless godot `verdicts.json`: `"verdict": "PASS"`, **88/88**,
  sha256 `883f68cd…`; stdout 89 `^PASS` / 0 `^FAIL`.
- `--probe-stream-attribution`: **89/89** (adds exactly
  `probe_stream_attribution`), sha256 `be92af70…`; stdout 91 `^PASS` +
  1 `^FAIL` — `FAIL stream_reject: exit=0 classification=False` is the
  probe arm's measured output, not a battery row (same shape as
  r67–r72).
- `--probe-midlineforge-ladder`: **89/89** (adds exactly
  `probe_midlineforge_ladder`), sha256 `44ba4b07…`; stdout 90/0.
- `--probe-midlineforge-gapladder`: **89/89** (adds exactly
  `probe_midlineforge_gapladder`), sha256 `4647777e…`; stdout 90/0.
- LOVE `verdicts.json`: PASS **19/19**, sha256 `a4ed4925…` (15 CASES +
  4 splice cells; `launch_ok=True done_marker=True`).
- pygame `verdicts.json`: PASS **55/55**, sha256 `9a7b13a7…` — the
  post-r72-move battery shape (54 CASES + 1 RAW_CASES, incl. the 18
  `rord_*`/`self_*` rows + `self_wire_reorders`); these 55 are exactly
  the prior rows the r73 move's insertion-only claim must preserve.
- `probe_error_clause_surface`: **34 discriminations, all True in all
  4 godot runs** — the "surface 34/34" envelope confirmed again.
- Stream-attribution artifact (sha256 `45501764…`): 24 discriminations,
  9-row `divergence_table`, `raw_merged_sha256` fields present.
- Ladder artifact (sha256 `9663bac4…`): `measured_window` landed
  `[0,40,80,120,160]`, missed `[240]`, mixed `[]`, lo 0 / hi 240 /
  nominal_gap 200; 8 discriminations all True — strict threshold bound
  reproduced.
- Gapladder artifact (sha256 `9b0472df…`): `landed_gaps_ms`
  `[100,200,400,800,400,800,800]` (trailing three = crossed cells),
  missed `[50]`, `crossed_cells_ms` `[[300,400],[300,800],[600,800]]`,
  12 discriminations True incl. `crossed_cells_elapsed_tracks_gap`,
  `crossed_cells_refute_absolute_edge`,
  `window_referent_is_gap_relative` — the gap-relative referent holds
  at frozen HEAD.
- pygame reorder lattice at frozen HEAD (the r73 claim's foundation):
  `reorder_buf` = `prefix_reorder` inj@0 head@8 wire 19B ret 0;
  `reorder_unbuf`/`_flush`/`_env` = `midline_splice` head@0;
  `reorder_late` = `append` tail@6; `reorder_self` wire =
  `prefix_reorder` (raw RAW_CASES row PASS); `whs_bufsize` =
  `rord_bufsize` = `self_bufsize` = **131072** exact;
  `whf_early_bytes` observed **126007** — byte-identical to r72's
  126007.

## Drift vs committed r68–r72 receipts — ZERO on compared tuples

`diff_receipts.py` (output `diff-output.txt`): Godot rows on the
7-tuple (script, flags, expected_exit, actual_exit, signature,
verdict, error) + meta discriminations; LOVE/pygame rows on
(arm, key, pinned, verdict).

**Godot — 36 comparisons, 0 tuple mismatches:**

| reference receipt | rows | my runs compared | common | mismatches |
|---|---|---|---|---|
| `r72-baseline/runs/…143946074058Z` flagless [on-disk] | 88 | all 4 | 88 | **0** |
| `r72-baseline/runs/…144122146924Z` attrib [on-disk] | 89 | all 4 | 88/89 | **0** |
| `r72-baseline/runs/…144234955551Z` ladder [on-disk] | 89 | all 4 | 88/89 | **0** |
| `r72-baseline/runs/…144401150151Z` gapladder [on-disk] | 89 | all 4 | 88/89 | **0** |
| `r71-baseline/godot-runs/…142633675793Z` [tracked] | 88 | all 4 | 88 | **0** |
| `r69-scribe/runs-landed-flagged/…121035766840Z` [tracked] | 91 | all 4 | 88/89 | **0** (see meta note) |
| `r69-simplifier/runs-landed/…121426485317Z` [tracked] | 91 | all 4 | 88/89 | **0** (same note) |
| `r69-simplifier/del-measure/runs-base/…124109211343Z` [tracked] | 89 | all 4 | 88/89 | **0** |
| `r68-boundary/runs2/…112024144893Z` [tracked] | 90 | all 4 | 88/89 | **0** |

- Row-set deltas are only the flag-gated probe rows — expected shape.
- Meta note (unchanged from r72, documented class): vs the two r69
  91-row refs the `probe_midlineforge_gapladder` discrimination map
  has 2 extra True keys (`crossed_cells_elapsed_tracks_gap`,
  `crossed_cells_refute_absolute_edge`) — those refs predate the
  crossed-cells addition that landed later the same round; the
  post-crossed-cells ref (r69-simplifier `runs-base`) matches
  **exactly**, 0 mismatches. Intra-round evolution, not drift.
- Attribution artifact volatile-stripped deep-diff: **0 diffs** vs
  r72-baseline and both r69 refs; 24 diffs vs r68-boundary = the
  `raw_merged_sha256` fields the r69 upgrade added (ref predates it;
  my artifact matches the landed shape; `stream_accept` arm digest
  `cb00e428…` identical).
- Ladder artifact: `measured_window`, per-cell (offset,outcome), and
  all discriminations **identical to all 4 refs**.
- Gapladder artifact vs r72-baseline: 78 raw diffs, all rep-level
  jitter (`output_lines` embedded pids, `descendant_alive_at_return`
  flips, `descendant_kernel_ppid_at_return` presence) — same class
  r72 reported (76 diffs). vs r69-scribe/simplifier landed: 8 diffs =
  crossed-cells addition (refs predate). vs r69-simplifier base
  (final r69 shape): 73 diffs, all the same rep-level jitter class;
  discriminations identical (12 True keys).

**LOVE — 11 references, 0 mismatches** on all common rows:
r72-baseline love19 + r72-reviewer + r72-simplifier runs-love +
r71-baseline + r71-reviewer ×3 + r71-simplifier ×4. (r71-simplifier
del-vB carries 18 rows — predates the `pump|pump_needed` row; common
18 all clean.)

**pygame — 29 references:**

- **0 mismatches** vs 20 of 22 post-move (55-row) refs: r72-scribe
  runs-landed{1,2,3,4}+env1, r72-simplifier runs-landed + del-control
  + vD-clean + vE-clean + runs-dirty, r72-reviewer pg-runs{1,2,3} +
  envsweep + loaded, and the del-measure variants vA/vB/vC (54/54/53
  rows — documented del-measure drops of `pump|pump_needed` and/or
  `pump|frames_nopump`; common rows all clean).
- Ref-side intentional variance (not drift): r72-reviewer `uwrap` +
  `uwrap2` recorded `reorder_self|wire_topology` FAIL — observed
  `midline_splice` under the reviewer's unbuffered-wrapper env sweep
  (idx h<c<t — the `-u` collapse the r72 arm pins). My standard-env
  PASS `prefix_reorder` matches all 20 other post-move refs.
- vs all 7 pre-move (36-row) refs (r72-baseline, r72-scribe
  runs-pre{1,2}, r72-reviewer pg-pre, r72-simplifier preland,
  r71-reviewer pg-6, r71-simplifier del-pg-vB): **0 mismatches** on
  the 36 common rows; `new_only` = exactly the 19 r72-added keys
  (18 `reorder_*` CASES keys + `reorder_self|wire_topology`) —
  the r72 move preserved prior rows byte-for-byte, re-confirmed.

## Post-commit re-verification — `43bef2d` landed 15:43:36Z

The r73 move commit landed mid-session (operator `ci`; 480 insertions
/ 17 deletions across `pygame_probe.py` +165, `pygame_battery.py`
+146/−17, `reports/round-73/r73-author.md` +186). Re-verify results:

- **Prior-row bytes stable**: CASES list 54→73 — the prior 54 tuple
  lines byte-identical (`git show` extraction equality check), all 19
  new rows appended (`infx_*`, `fd2m_*`, `det_*`, `node_present`/
  `node_ver`, `nsm_*`, `nbig_*`, `nsy_*`). RAW_CASES 1→7, prior
  `self_wire_reorders` row byte-identical. The 17 deleted lines are the
  raw-wire evaluation *block* restructure (generalized marker-scan for
  the new raw arms), not prior-row data bytes.
- **Sibling batteries untouched** (byte-stability `2dd108b→43bef2d`):
  `run_battery.py` `f55c27d8`→`f55c27d8`, `love_battery.py` `25977ad9`
  →`25977ad9`, `love_probe/main.lua` `a0afe6ca`→same, `conf.lua`
  `0b45ef73`→same, `descendant_pipe_probe.gd`/`stream_attribution_probe.gd`
  same — all STABLE. Godot CASES still 81 (+7 meta = 88-row flagless);
  love still 19.
- **Post-commit battery re-runs on live `43bef2d`** (scratch
  `*-postland/`):
  - pygame: **80/80 PASS** (`…154437867083Z`, sha `37493d38…`) —
    73 CASES + 7 RAW = 80; all 55 prior rows present with 0
    pinned/verdict mismatches vs my frozen receipt (`observed` deltas
    only on bound-pinned jittered fields — timing class, outside
    compared scope); all 25 new rows PASS.
  - love: **19/19 PASS** (`love-…154458828446Z`, sha `13e14e39…`) —
    control family green on the moved tree.
  - godot flagless: run1 FAIL 87/88 (`audio_playback` exit=2 with
    `signature='PASS … position_advanced=true'` — the documented
    concurrent-load assertion flake, same class as r72's
    `audio_bus_route`; kept as provenance `…154508068468Z`); clean
    re-run **PASS 88/88** (`…154631521198Z`, sha `8f1a765e…`). Tuple
    diff frozen-pre-land vs post-land re-run: **0 mismatches on all
    88 rows**.
- Net: the move is byte-conservative on prior rows (insertion-only at
  the data level), sibling counts unchanged (godot 88 flagless /
  89 flagged, love 19), pygame count grew 55→80 exactly by the
  declared new cells.

## Pinned boundary rows — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release`: PASS, expected/actual 0,
  error null, flags `["--spawn-forge-release"]` — origin-blind
  signature acceptance reproduced, tuple-identical to r63–r72.
- `divergence_table` seam rows: 9-row table, same divergent pattern
  (F,T,T,F,T,T,T,T,T) as r68–r72 — the spawn-seam surface the r72/r73
  reorder claims compose over is green.
- `splice_*` LOVE cells (4/4): inwindow 80/200 spliced, beyond 240/200
  clean, crossed 300/400 spliced, tight 80/50 clean — the
  write-through `io.write` midline-splice control column holds.
- pygame `whs_bufsize`/`rord_bufsize`/`self_bufsize` = `131072` exact
  — the buffer constant bounding every r72/r73 withholding window.

## Artifact inventory (`corpus/live/r73-baseline/`)

- `frozen/HEAD-2dd108b….tar` — `git archive HEAD`, 687,124,480 B,
  sha256 `5552cac0…`, deterministic re-run match (gitignored).
- `frozen-extract/` — populated frozen tree (44,829 files + 34
  symlinks, comm-clean both directions vs `git ls-files`); replay
  surface (gitignored).
- `runs/20261014T152239075708Z/` flagless 88/88 · `…152414017636Z/`
  attribution 89/89 · `…152533525776Z/` ladder 89/89 ·
  `…152659883512Z/` gapladder 89/89.
- `love-runs/love-20261014T152243714938Z/` — 19/19 + 4 splice receipts.
- `pygame-runs/pygame-20261014T152252487786Z/` — 55/55.
- `runs-postland/…154508068468Z/` flaky FAIL (87/88, provenance keep)
  + `…154631521198Z/` clean 88/88 · `love-runs-postland/` 19/19 ·
  `pygame-runs-postland/` 80/80 — post-commit re-verify receipts.
- `battery{,-attribution,-ladder,-gapladder,-postland,-postland-rerun}.stdout`
  + `love-`/`pygame-`{`-battery`,`-postland`}`.stdout` + all-zero
  `.stderr` siblings; `diff_receipts.py` + `diff-output.txt`;
  `run-start.txt`, `extract-done.txt`, `preland-head.txt` provenance
  marks.

## Process hygiene

Post-run `ps`: **no godot, no love, no battery processes from this
seat**. Sibling wave-13 seats in flight throughout: r73-{author,
boundary,critic,reviewer,scout,scribe,simplifier,verifier} scratch
dirs and reports/round-73 sibling reports (author, boundary, critic,
scout, scribe, verifier at write time) appeared during the session;
r72-simplifier + r73-simplifier snapshot loops, an r73-critic watch
loop, and g3d-lane watchers ran concurrently (documented load
condition behind the post-land `audio_playback` flake).
`git status` from this seat: zero tracked modifications introduced —
only the pre-existing `M corpus/live/r72-simplifier/watch.log`
(sibling watcher) and untracked `r7*`/`r73-*` scratch/report paths.

## UNKNOWNs / caveats

- **Flaky row, documented class:** post-land flagless run1
  (`20261014T154508068468Z`) failed `audio_playback` (exit=2, the
  script's own `position_advanced` assertion raced — signature PASS)
  under concurrent sibling load — same flake class r69/r72 recorded
  for `audio_playback`/`audio_bus_route`/`transition`. All 87 other
  rows tuple-identical; clean re-run PASS 88/88. Frozen-surface
  replays were flake-free (all six runs first-pass clean).
- Naturally varying fields (`command`, `scratch`, `xdg_data_home`,
  pids, `elapsed_seconds`, `seed`, receipt shas, rep-level
  `output_lines`, `descendant_alive_at_return`,
  `descendant_kernel_ppid_at_return`, bound-pinned `observed`) are
  outside compared scope, per r62–r72 precedent.
- The r73 declared claims (infix interior-offset pin, detach EOF-hold
  harness cell, fd2-merge inversion, node owner-census topology split)
  are **not adjudicated here** — this receipt is the verified-stable
  before-state plus the byte-stability/counts post-commit check. What
  is pinned: at frozen `2dd108b` the Godot gap-relative fabrication
  bound, LOVE splice control column, and the entire r72 reorder
  lattice (prefix_reorder/midline_splice/append incl. the raw-wire
  `self_wire_reorders` prefix cell) reproduce cell-for-cell, and the
  r73 commit preserves all prior rows byte-identically while adding
  19 CASES + 6 RAW rows (55→80) with siblings untouched.
- Not re-measured here (carried from r61–r72): signal-origin
  indistinguishability of `returncode`; live-window forgery acceptance
  under the poll() gate; >1 descendant depth, >64KiB descendant writes,
  exported builds, non-POSIX unprobed; pygame mixer under
  AUDIODRIVER=dummy, event-queue overflow, pygame-ce divergence;
  node census rows verified only as landed-PASS, not independently
  re-derived (verifier seat owns AGREE/DISAGREE).
