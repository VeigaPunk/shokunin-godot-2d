# Round 72 baseline report — frozen HEAD replay, three runtimes (host: devin)

Seat: g2d baseline (LEAF). Immutable before-state for the r72 wave: no
tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r72-baseline/` (`frozen/` + `*extract*/`
gitignored by `corpus/.gitignore`) plus this report.

The r72 declared axis-move — the reorder arm on `pygame_probe.py` +
`pygame_battery.py` (xconnector X1: fd1-inheritance × block-buffering →
descendant bytes land *before* the parent's buffered head; buffered child
→ prefix/reorder topology, flushed/`-u` → midline splice) — **landed
mid-session**: HEAD advanced `44127af` → **`fee5563`** ("r72: reorder
fabrication arm", committed 2026-10-14 14:46:58Z) *after* this seat's
archive (14:37:5xZ) and during/just-after the replay window (runs
14:37:55Z–14:44:01Z). The frozen surface is therefore the move commit's
**direct parent** (`git rev-parse fee5563^` = `44127af`) — a provably
pre-move before-state. Post-commit, live `corpus/fixtures/pygame_probe.py`
= sha256 `7c0f9c73…` ≠ frozen-extract `4d426a3b…`; at frozen `44127af`
both pygame files contain **0** `reorder` tokens (`git show 44127af:… |
grep -c reorder` → 0, 0). The move itself: 174 changed lines across
the two files (`git diff 44127af fee5563 --stat`: probe 103, battery 71;
173 insertions / 1 deletion — insertion-only per its commit message;
landed battery shape 54 CASES + 1 RAW_CASES, plus an `env=CHILD_ENV`
popen_arm fix for the r71-verifier PYTHONUNBUFFERED-leak defect) —
this baseline is its verified-stable referent.

## Frozen-tree provenance — archive + extracted replay (r69 procedure)

- Frozen source: `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
  archive HEAD -o corpus/live/r72-baseline/frozen/HEAD-44127afed9b68a28bf671a195f85a4b4f37a2c57.tar`
- HEAD frozen: `44127afed9b68a28bf671a195f85a4b4f37a2c57`
  (`r71 report-last: adjudicator + LOG + SCORECARD + landed seat reports`);
  parent `a993cbe` (r71 pygame first contact, 36/36) → `d9ae207` wave-10
  report-last; chain carries r70 LOVE `16d003c` + r69 gapladder `9fb50aa`.
- Archive: **683,438,080 bytes**, sha256
  `3df791c5947cfd7124cb7e771c334c3a971a409de197457ee067763afc3219dd`.
  `git archive HEAD | sha256sum` re-run = **identical** — deterministic.
- Tar members: 48,680 total = **44,563 file entries** + 4,117 directory
  entries; file count == `git ls-files | wc -l` = 44,563 exactly
  (r69: 41,425 — delta is r70/r71 accretion incl. committed receipts).
- No tracked `frozen/`, `tree/`, or `node_modules` at HEAD (`git ls-tree -r
  HEAD --name-only | grep -cE 'frozen|/tree/|node_modules'` → 0; same grep
  over tar listing → 0) — **no nested prior frozen trees**.
- Extraction: `tar -xf` into `corpus/live/r72-baseline/frozen-extract/`
  (untracked, matches `live/*/*extract*/` ignore rule). Membership check —
  `comm -23` and `comm -13` over `find . -type f/-l | sort` vs
  `git ls-files | sort` both **EMPTY**: 44,529 files + 34 symlinks =
  44,563, exactly `git ls-files`.
- Fixture digests in the extract == `HEAD:` blob contents
  (`git show HEAD:$f | sha256sum` vs `sha256sum $X/$f`), all 7 checked:
  `run_battery.py` `f55c27d8…`, `pygame_battery.py` `0a579819…`,
  `pygame_probe.py` `4d426a3b…`, `love_battery.py` `25977ad9…`,
  `love_probe/main.lua` `a0afe6ca…`, `descendant_pipe_probe.gd`
  `c86bda84…`, `stream_attribution_probe.gd` `dc0b0d5c…`.
- Live-worktree fixture digests == `44127af` for all five battery files
  **at archive time** — the live tree measured the same bytes then; the
  post-move bytes arrived later via commit `fee5563` (14:46:58Z), making
  the freeze isolation load-bearing retroactively (r69 rule: replay from
  the extract, never the live tree).
- `verdicts.json["seed"]` on godot runs records
  `…/r72-baseline/frozen-extract/corpus/fixtures`; love records
  `probe_dir: …/frozen-extract/corpus/fixtures/love_probe`; pygame records
  `probe: …/frozen-extract/corpus/fixtures/pygame_probe.py` — all three
  replays provably executed frozen-HEAD fixture bytes.
- Post-run `find frozen-extract -newermt <run start>` → **0 entries**:
  the extract stayed read-only-pristine.

## Exact invocations

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`X=corpus/live/r72-baseline/frozen-extract`:

```
python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r72-baseline/runs
  # run1: exit 1, runs/20261014T143755616527Z verdicts.json FAIL 87/88
  #   (audio_bus_route flake — see caveats)
  # run2: exit 0, runs/20261014T143946074058Z verdicts.json PASS 88/88

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r72-baseline/runs --probe-stream-attribution
  # exit 0, runs/20261014T144122146924Z PASS 89/89
  #   + stream-attribution-verdicts.json

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r72-baseline/runs --probe-midlineforge-ladder
  # exit 0, runs/20261014T144234955551Z PASS 89/89
  #   + midlineforge-ladder-verdicts.json

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r72-baseline/runs --probe-midlineforge-gapladder
  # exit 0, runs/20261014T144401150151Z PASS 89/89
  #   + midlineforge-gapladder-verdicts.json

python3 $X/corpus/fixtures/love_battery.py \
  --runs corpus/live/r72-baseline/love-runs
  # exit 0, love-20261014T144103820852Z PASS 19/19

python3 $X/corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r72-baseline/pygame-runs
  # exit 0, pygame-20261014T144107924935Z PASS 36/36
```

All seven `.stderr` captures 0 bytes. Environment: Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), LOVE 11.5
(`/usr/bin/love`), Python 3.14.7 + pygame 2.6.1 / SDL 2.32.72 — same
profile as r70/r71.

## Before-state receipt summary

- Flagless godot `verdicts.json`: `"verdict": "PASS"`, **88/88**, sha256
  `205b8927…`; stdout 89 `^PASS` / 0 `^FAIL` (sha256 `c90ab34d…`).
- `--probe-stream-attribution`: **89/89** (adds exactly
  `probe_stream_attribution`), sha256 `009ad97a…`; stdout 91 `^PASS` +
  1 `^FAIL` — `FAIL stream_reject: exit=0 classification=False` is the
  probe arm's measured output, not a battery row (same shape as r67–r69).
- `--probe-midlineforge-ladder`: **89/89** (adds exactly
  `probe_midlineforge_ladder`), sha256 `0796bfb6…`; stdout 90/0.
- `--probe-midlineforge-gapladder`: **89/89** (adds exactly
  `probe_midlineforge_gapladder`), sha256 `3a17ee9a…`; stdout 90/0.
- LOVE `verdicts.json`: PASS **19/19**, sha256 `5db7329a…`
  (15 CASES + 4 splice cells; `launch_ok=True done_marker=True`).
- pygame `verdicts.json`: PASS **36/36**, sha256 `8bf0f0c2…` — the
  pre-move battery shape (36 CASES, zero `reorder_*`/`self_*` rows); the
  landed post-move battery is 54 CASES + 2 RAW_CASES, so these 36 are
  exactly the prior rows the move's insertion-only claim must preserve.
- `probe_error_clause_surface`: **34 discriminations, all True in all 4
  godot runs** — the "surface 34/34" envelope confirmed.
- Stream-attribution artifact (sha256 `ea65fbe0…`): 24 discriminations,
  9-row `divergence_table`, `raw_merged_sha256` fields **present**
  (the r69 receipt upgrade, landed).
- Ladder artifact (sha256 `d4c8f5fc…`): `measured_window` landed
  `[0,40,80,120,160]`, missed `[240]`, mixed `[]`, lo 0 / hi 240 /
  nominal_gap 200 — strict threshold bound reproduced; 8 discriminations
  True.
- Gapladder artifact (sha256 `0e599a2f…`): `landed_gaps_ms`
  `[100,200,400,800,400,800,800]`, missed `[50]`, 12 discriminations
  True incl. `crossed_cells_*` + `window_referent_is_gap_relative` —
  the gap-relative referent (r69 claim) holds at frozen HEAD.
- `reorder` arm rows: **absent everywhere on the frozen surface** —
  all replays predate/derive from `44127af` (0 `reorder` tokens); the
  move landed as `fee5563` after the archive, so these receipts are the
  pre-move referent, not a measurement of the landed arm.

## Drift vs committed r68–r71 receipts — ZERO on compared tuples

`diff_receipts.py` (output `diff-output.txt`): Godot rows on the 7-tuple
(script, flags, expected_exit, actual_exit, signature, verdict, error) +
meta discriminations; LOVE/pygame rows on (arm, key, pinned, verdict).

**Godot — 20 comparisons, 0 tuple mismatches:**

| reference receipt | rows | my runs compared | common | mismatches |
|---|---|---|---|---|
| `r71-baseline/godot-runs/…142633675793Z` [tracked] | 88 | all 4 | 88 | **0** |
| `r69-scribe/runs-landed-flagged/…121035766840Z` [tracked] | 91 | all 4 | 88/89 | **0** (see gapladder meta note) |
| `r69-simplifier/runs-landed/…121426485317Z` [tracked] | 91 | all 4 | 88/89 | **0** (same note) |
| `r69-simplifier/del-measure/runs-base/…124109211343Z` [tracked] | 89 | all 4 | 88/89 | **0** |
| `r68-boundary/runs2/…112024144893Z` [tracked] | 90 | all 4 | 88/89 | **0** |

- Row-set deltas are only the flag-gated probe rows — expected shape.
- Gapladder meta note: vs the two r69 91-row refs the
  `probe_midlineforge_gapladder` discrimination map has 2 extra True keys
  (`crossed_cells_elapsed_tracks_gap`, `crossed_cells_refute_absolute_edge`)
  — those refs predate the crossed-cells addition that landed later the
  same round (r69-simplifier `runs-base` @12:41 has the final shape and
  matches **exactly**, 0 mismatches). Intra-round evolution, not drift.
- Attribution artifact volatile-stripped deep-diff: **0 diffs** vs both
  r69 refs; 24 diffs vs the two r68 refs = the `raw_merged_sha256`
  fields the r69 upgrade added (refs predate it; my artifact matches the
  landed shape). Raw arm digests identical (`cb00e428…` on stream_accept).
- Ladder artifact: `measured_window`, per-cell (offset,outcome), and all
  discriminations **identical to all 4 refs** — no jitter-split.
- Gapladder artifact vs post-crossed-cells ref (r69-simplifier base):
  **0 structural diffs**; all 76 raw diffs are rep-level jitter
  (`output_lines` embedded pids, `descendant_alive_at_return` flips).

**LOVE — 8 references, 0 mismatches** on all common rows:
r71-baseline love19 [tracked] + r71-reviewer ×3 + r71-simplifier ×4.
(r71-simplifier del-vB carries 18 rows — predates the `pump|pump_needed`
row; common 18 all clean.)

**pygame — 19 references:**

- **0 mismatches** vs the post-metric-fix refs:
  `r71-reviewer pg-6` [tracked], `r71-simplifier del-pg-vB` [tracked].
  My `withhold_fill|early_bytes` observed **126007 — byte-identical** to
  both.
- vs the 16 other refs the sole delta is `withhold_fill|early_bytes`:
  pin evolution [65536,200000]→[60000,135000] (r71-adjudicator.md:26 —
  author's metric fix; my HEAD pin = [60000,135000]) and/or that row's
  recorded FAIL in pre-fix refs (observed 191543 = the documented
  exit-burst misattribution, r71-author.md:94-96). Not prior-row drift:
  my run reproduces the landed battery's pins and every row PASSes.
- vs `r71-critic scout-{idle,loaded64}` [tracked]: those are the critic's
  75-row scout battery (different case model); 19 common keys, pin-tuple
  deltas on 8–9 = battery-version divergence, recorded for completeness.

## Pinned boundary rows — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release`: PASS, expected/actual 0,
  error null, flags `["--spawn-forge-release"]` — origin-blind signature
  acceptance reproduced, tuple-identical to r63–r71.
- `divergence_table` seam rows (`streamdiv_seam_error`,
  `streamdiv_seam_script`, `streamdiv_seam_sig`): all `divergent=True`,
  matching r68/r69 — the spawn-seam surface the r72 reorder claim
  composes over is green at HEAD.
- `splice_*` LOVE cells (4/4): in-window 80/200 spliced, beyond 240/200
  clean, crossed 300/400 spliced, tight 80/50 clean — the midline-splice
  topology (write-through `io.write`) reproduced; it is the control
  column for the r72 buffered-vs-flushed topology fork.
- pygame `withhold_*` rows: `whs_bufsize` = `131072` exact — the
  CPython-3.14 buffer constant the reorder window is bounded by, pinned.

## Artifact inventory (`corpus/live/r72-baseline/`)

- `frozen/HEAD-44127af….tar` — `git archive HEAD`, 683,438,080 B, sha256
  `3df791c5…`, deterministic re-run match.
- `frozen-extract/` — populated frozen tree (44,529 files + 34 symlinks,
  comm-clean vs `git ls-files` both directions); replay surface.
- `runs/20261014T143755616527Z/` — flaky FAIL (87/88, provenance keep) ·
  `…143946074058Z/` flagless 88/88 · `…144122146924Z/` attribution 89/89 ·
  `…144234955551Z/` ladder 89/89 · `…144401150151Z/` gapladder 89/89.
- `love-runs/love-20261014T144103820852Z/` — 19/19 + 4 splice receipts.
- `pygame-runs/pygame-20261014T144107924935Z/` — 36/36.
- `battery{,-rerun,-attribution,-ladder,-gapladder}.stdout` + `love-` /
  `pygame-battery.stdout` + 7 zero-byte `.stderr` siblings.
- `diff_receipts.py` + `diff-output.txt` — comparison harness + full
  output; `extract-done.txt`, `run-start.txt` — provenance marks.

## Process hygiene

Post-run `ps`: **no godot, no love, no battery processes from this seat**.
Sibling wave-12 seats are in flight — r72-{author,boundary,critic,scout,
scribe,simplifier,verifier} scratch dirs and reports/round-72 sibling
reports appeared during the session; a simplifier del-measure run and
three sibling watch/snapshot loops were live during my runs (this is the
documented concurrent-load condition behind the flaky row below).
`git status` from this seat: zero tracked modifications introduced —
only the pre-existing `M corpus/live/r71-scribe/watch.log` (sibling
watcher) and untracked `r7*` scratch/report paths.

## UNKNOWNs / caveats

- **Flaky row, documented class:** first flagless run
  (`20261014T143755616527Z`) failed `audio_bus_route` (exit=2: the
  script's own `position_advanced` assertion raced — signature PASS,
  playback position not yet advanced) under concurrent sibling load —
  the same flake class r69 recorded for `audio_playback`/
  `audio_bus_route`/`transition`. All 87 other rows tuple-identical to
  refs; clean re-run PASS 88/88. Kept as provenance.
- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, `seed`, receipt shas, rep-level `output_lines`) are
  outside compared scope, per r62–r69 precedent.
- The r72 declared claim (buffered→prefix/reorder vs flushed→midline
  splice on a spawned descendant into inherited fd1) is **not measured
  here** — it landed mid-session as `fee5563` while this seat was
  replaying its parent; this receipt is its verified-stable
  before-state. What is pinned: at frozen `44127af` the Godot midlineforge
  surface reads the same strict gap-relative bound (ladder
  [0,40,80,120,160]/missed 240; gapladder landed {100,200,400,800}+crossed
  /missed 50), LOVE's write-through splice cells hold 4/4, and pygame's
  withholding bound is `io.DEFAULT_BUFFER_SIZE` = 131072 — the two
  mechanisms whose composition the reorder arm asserts are both green.
- Not re-measured here (carried from r61–r71): signal-origin
  indistinguishability of `returncode`; live-window forgery acceptance
  under the poll() gate; >1 descendant depth, >64KiB descendant writes,
  exported builds, non-POSIX unprobed; pygame mixer under
  AUDIODRIVER=dummy, event-queue overflow, pygame-ce divergence.
