# Round 74 baseline report — frozen HEAD replay + drift-diff (host: devin)

Seat: g2d baseline (LEAF). Immutable before-state for the r74 wave: no
tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r74-baseline/` (`frozen/` gitignored by
`corpus/.gitignore:4 live/*/frozen/`, `frozen-extract/` by
`live/*/*extract*/`, `runs/` by `corpus/live/.gitignore:1 runs/`) plus
this report.

Timeline: HEAD frozen at `1275746` (`r73 report-last + simplifier-fold`,
committed 2026-10-14) — archive written 16:02:2xZ, extract done
16:02:41Z, all six family replays 16:03:27Z–16:09:43Z. **RECOVERY:**
the prior baseline generation died ~16:10Z, mid-way between the last
replay and the drift-diff phase. This generation re-verified the
inherited scratch before trusting it: `preland-head.txt` and the
frozen tar name both carry `1275746cedfa…` == live `git rev-parse
HEAD`, archive bytes re-derived deterministically (below), every
receipt re-read and the extract proven pristine — all reused, none
re-run. The drift-diff (`diff_receipts.py` + `diff-output.txt`) is new
work from this generation.

The r74 declared axis-move — `love_battery.py` + NEW `love_phys_probe`
interior-write lattice (writes inside Box2D callbacks
beginContact/preSolve/postSolve; gating partition
{refused|deferred|fatal|applied}; per `tasks/g2d-author.md`) — **landed
mid-session** as `ae6cb16` (committed 2026-10-14 16:41:00Z; author
worktree divergence first observed 16:37:30Z). The frozen surface
`1275746` is the move commit's **direct parent** — a provably pre-move
before-state, and this baseline its verified-stable referent. It
contains the r73 move `43bef2d` already committed (pygame battery
80-row shape), and none of the r74 arm's tokens exist in the frozen
LOVE fixtures.

## Frozen-tree provenance — archive + extracted replay (r69–r73 procedure)

- Frozen source: `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
  archive HEAD -o corpus/live/r74-baseline/frozen/HEAD-1275746cedfa314246755a81b4ab60e57075df98.tar`
  (run by prior generation 16:02:2xZ; re-verified this generation).
- HEAD frozen: `1275746cedfa314246755a81b4ab60e57075df98`; parent
  `43bef2d` (r73 topology-depth move) → `2dd108b` r72 report-last →
  `fee5563` r72 reorder arm → `44127af` r71 report-last.
- Archive: **687,329,280 bytes**, sha256
  `5175734c1f0ddf7fe921097f18dbddda8690df8643b84030e76805d64e183d87`.
  `git archive HEAD | sha256sum` re-run (this generation) =
  **identical** — the frozen tar is byte-for-byte a deterministic
  archive of current HEAD, not a stale or partial artifact.
- Tar members: **44,873 non-dir entries** == `git ls-files | wc -l`
  = 44,873 exactly (r73: 44,863 — delta +10 is r73-round committed
  receipts). `comm -23` (missing from tar) = **0**, `comm -13`
  (extra in tar) = **0**.
- No tracked nested snapshot dirs at HEAD (`git ls-tree -r HEAD
  --name-only | grep -cE '^corpus/live/[^/]+/(frozen|head|snapshot|base)/
  |^corpus/live/[^/]+/tree/'` → **0**). Broader grep
  (`frozen|/tree/|node_modules|extract`) = 209 tracked paths, all
  incidental filenames (same class as r73's 209: `extract_classifiers.py`
  copies, r66-simplifier extracted specimen, prior `extract-done.txt`
  marks, frozen-tar *names* inside reports).
- Extraction (prior gen): `tar -xf` into `corpus/live/r74-baseline/
  frozen-extract/`. Membership re-verified this gen: `find . -type f`
  = 44,829 files + **34 symlinks** = 44,873 == `git ls-files` exactly.
- Fixture digests extract == `HEAD:` blob == live tree (pre-move) for
  all 9 checked: `run_battery.py` `f55c27d8…`, `pygame_battery.py`
  `6d3fbf5f…` (the post-`43bef2d` byte), `pygame_probe.py` `8e15e0d2…`,
  `love_battery.py` `25977ad9…`, `love_probe/main.lua` `a0afe6ca…`,
  `love_probe/conf.lua` `0b45ef73…`, `descendant_pipe_probe.gd`
  `c86bda84…`, `stream_attribution_probe.gd` `dc0b0d5c…`.
- `verdicts.json["seed"]` on all 4 godot runs records
  `…/r74-baseline/frozen-extract/corpus/fixtures` — replays provably
  executed frozen-HEAD fixture bytes.
- Post-replay pristine check (this gen): `find frozen-extract -newer
  extract-done.txt` → **0 entries**.
- Pre-move token referents in frozen fixtures (the r74 move's claimed
  surface): `beginContact|preSolve|postSolve|setPosition|newBody|
  destroy|physics` = **0 occurrences** in `love_battery.py` and **0**
  in `love_probe/main.lua` — the Box2D interior-write arm is entirely
  absent pre-move. (`interior` hits in pygame_battery/pygame_probe are
  r73 infix-arm comments, not physics.)

## Exact invocations (prior generation, receipts verified this generation)

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`X=corpus/live/r74-baseline/frozen-extract`:

```
python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r74-baseline/runs
  # runs/20261014T160327707475Z verdicts.json PASS 88/88

python3 $X/corpus/fixtures/love_battery.py \
  --runs corpus/live/r74-baseline/love-runs
  # love-runs/love-20261014T160938436041Z PASS 19/19

python3 $X/corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r74-baseline/pygame-runs
  # pygame-runs/pygame-20261014T160943220687Z PASS 80/80

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r74-baseline/runs --probe-stream-attribution
  # runs/20261014T160446750837Z PASS 89/89 + stream-attribution-verdicts.json

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r74-baseline/runs --probe-midlineforge-ladder
  # runs/20261014T160615371269Z PASS 89/89 + midlineforge-ladder-verdicts.json

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r74-baseline/runs --probe-midlineforge-gapladder
  # runs/20261014T160749745644Z PASS 89/89 + midlineforge-gapladder-verdicts.json
```

All six `.stderr` captures **0 bytes**. Environment (`env.txt`):
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), LOVE 11.5
"Mysterious Mysteries" (`/usr/bin/love`), Python 3.14.7 + pygame 2.6.1
/ SDL 2.32.72, `io.DEFAULT_BUFFER_SIZE` = **131072** (THIS build's
constant — carried guard), node v24.21.0 — same profile as r70–r73.

## Before-state receipt summary (frozen `1275746`, pre-move)

- Flagless godot `verdicts.json`: `"verdict": "PASS"`, **88/88**,
  sha256 `275446588d14…`; `battery.stdout` tail `PASS battery: …`.
- `--probe-stream-attribution`: **89/89** (adds exactly
  `probe_stream_attribution`), sha256 `5dcfd2a1ae…`; artifact sha256
  `6e34d5aa1e…`.
- `--probe-midlineforge-ladder`: **89/89** (adds exactly
  `probe_midlineforge_ladder`), sha256 `355340bbcc…`; artifact sha256
  `9d389fa2bd…`.
- `--probe-midlineforge-gapladder`: **89/89** (adds exactly
  `probe_midlineforge_gapladder`), sha256 `7c0fdf2b2a…`; artifact
  sha256 `2d4a9b1033…`.
- LOVE `verdicts.json`: PASS **19/19**, sha256 `d8fa741844ec…`
  (15 CASES + 4 splice cells; `launch_ok=True done_marker=True`).
- pygame `verdicts.json`: PASS **80/80**, sha256 `f736bebb8725…` —
  the post-r73-move battery shape (73 CASES + 7 RAW_CASES, incl. the
  r73 `infix_*`/`fd2m_*`/`det_*`/`node_*`/`nsm_*`/`nbig_*`/`nsy_*`
  rows); these 80 are exactly the prior rows the r74 move's
  insertion-only claim must preserve.
- `probe_error_clause_surface`: **34 discriminations, all meta rows
  PASS in all 4 godot runs** — the "surface 34/34" envelope again.
- Stream-attribution artifact: 24 discriminations, 9-row
  `divergence_table`, `raw_merged_sha256` fields present.
- Ladder artifact: `measured_window` landed `[0,40,80,120,160]`,
  missed `[240]`, mixed `[]`, lo 0 / hi 240 / nominal_gap 200;
  8 discriminations all True.
- Gapladder artifact: `landed_gaps_ms` `[100,200,400,800,400,800,800]`
  (trailing three = crossed cells), missed `[50]`, `crossed_cells_ms`
  `[[300,400],[300,800],[600,800]]`, 12 discriminations True incl.
  `crossed_cells_elapsed_tracks_gap`, `crossed_cells_refute_absolute_edge`,
  `window_referent_is_gap_relative`.
- pygame reorder lattice at frozen HEAD (the r73 arm inside this HEAD):
  `reorder_buf` = `prefix_reorder` inj@0 head@8 wire 19B ret 0;
  `reorder_unbuf`/`_flush`/`_env` = `midline_splice` head@0;
  `reorder_late` = `append` tail@6; `reorder_self|wire_topology` =
  `prefix_reorder` (raw RAW_CASES row PASS); `whs`/`rord`/`self`
  bufsize = **131072** exact; r73 cells: `infix|injected_rel` observed
  **126011** (byte-identical to r73's pin), `fd2mrg` =
  `prefix_reorder`, `detach` = `eof_hold`, `node_census` =
  present + `v24.21.0`, `node_small`/`node_sync` = `midline_splice`,
  `node_big` = `infix` inj@65541 wire 200019.

## Drift vs committed r68–r73 receipts — ZERO on compared tuples

`diff_receipts.py` (output `diff-output.txt`, 275 lines): Godot rows on
the 7-tuple (script, flags, expected_exit, actual_exit, signature,
verdict, error) + meta discriminations; LOVE/pygame rows on (arm, key,
pinned, verdict).

**Godot — 40 comparisons, 0 tuple mismatches:**

| reference receipt | rows | my runs compared | common | mismatches |
|---|---|---|---|---|
| `r73-baseline/runs/…152239075708Z` flagless [on-disk] | 88 | all 4 | 88 | **0** |
| `r73-baseline/runs/…152414017636Z` attrib [on-disk] | 89 | all 4 | 88/89 | **0** |
| `r73-baseline/runs/…152533525776Z` ladder [on-disk] | 89 | all 4 | 88/89 | **0** |
| `r73-baseline/runs/…152659883512Z` gapladder [on-disk] | 89 | all 4 | 88/89 | **0** |
| `r73-baseline/runs-postland/…154631521198Z` flagless [on-disk] | 88 | all 4 | 88 | **0** |
| `r71-baseline/godot-runs/…142633675793Z` [tracked] | 88 | all 4 | 88 | **0** |
| `r69-scribe/runs-landed-flagged/…121035766840Z` [tracked] | 91 | all 4 | 88/89 | **0** (meta note) |
| `r69-simplifier/runs-landed/…121426485317Z` [tracked] | 91 | all 4 | 88/89 | **0** (same note) |
| `r69-simplifier/del-measure/runs-base/…124109211343Z` [tracked] | 89 | all 4 | 88/89 | **0** |
| `r68-boundary/runs2/…112024144893Z` [tracked] | 90 | all 4 | 88/89 | **0** |

- Row-set deltas are only the flag-gated probe rows — expected shape.
- Meta note (documented class, unchanged since r72): vs the two r69
  91-row refs the `probe_midlineforge_gapladder` discrimination map
  carries 2 extra True keys (`crossed_cells_elapsed_tracks_gap`,
  `crossed_cells_refute_absolute_edge`) — those refs predate the
  crossed-cells addition that landed later the same round; the
  post-crossed-cells ref (r69-simplifier `runs-base`) and all r73 refs
  match **exactly**.
- Attribution artifact volatile-stripped deep-diff: **0 diffs** vs
  r73-baseline and both r69 refs; 24 diffs vs r68-boundary = the
  `raw_merged_sha256` fields the r69 upgrade added (ref predates it;
  `stream_accept` arm digest `cb00e428…` identical).
- Ladder artifact: `measured_window`, per-cell (offset,outcome), and
  all discriminations **identical to all 4 refs**.
- Gapladder artifact vs r73-baseline: 78 raw diffs, all rep-level
  jitter (`output_lines` embedded pids, `descendant_alive_at_return`
  flips, `descendant_kernel_ppid_at_return` presence) — same class
  r73 reported (78 diffs). vs r69-scribe/simplifier landed: 8 diffs =
  crossed-cells addition (refs predate). vs r69-simplifier base:
  76 diffs, same rep-level jitter class; discriminations identical.

**LOVE — 17 references, 0 mismatches** on all common rows:
r73-baseline love19 + postland, r73-reviewer ×2, r73-simplifier,
r73-verifier, r72-baseline + r72-reviewer + r72-simplifier,
r71-baseline + r71-reviewer ×3 + r71-simplifier ×4. (r71-simplifier
del-vB carries 18 rows — predates `pump|pump_needed`; common 18
clean, `new_only` = exactly that row.)

**pygame — 46 references:**

- **0 mismatches** vs 21 of 25 post-r73-move (80-row) refs:
  r73-baseline postland, r73-author ×2, r73-critic replay ×4 +
  detach-battery (55-row early-draft ref: common 55 clean, new_only =
  the 25 r73 keys), r73-reviewer pg-r{1,2,3} + envsweep + loaded,
  r73-simplifier landed + del-control + vA/vB/vD/vE/vF/vG (vC: 78
  rows, documented del-measure drop of the `pump` pair — common
  clean), r73-verifier run{3,5}.
- Ref-side intentional variance (scenario refs, not drift; pinned
  values identical to mine, only verdicts differ where the scenario
  gates the row):
  - nodeabsent refs (r73-critic, r73-reviewer, r73-verifier): 15
    `node_*` FAILs each — node removed from PATH by construction.
  - stuck-detach refs (r73-critic, r73-reviewer):
    `detach|wire_topology` FAIL — the stuck-detach wound arm.
  - unbuf/uwrap refs (r73-critic unbuf, r73-reviewer uwrap): 3 FAILs
    each (`fd2mrg|wire_topology`, `infix|injected_rel`,
    `reorder_self|wire_topology` class) — the `-u` collapse the
    r72/r73 arms pin.
  - r73-reviewer `infmissing`: 4 `infix_*` FAILs — the infix-missing
    scenario arm; pinned bounds identical to mine.
  - r73-verifier `run1` (pre-land draft): key-rename delta —
    ref carries `infix|injected_at`/`tail_at` where landed shape has
    `injected_rel`/`tail_rel` (new_only/old_only pairs exactly), plus
    `infix|head_at` FAIL on the draft bound — intra-round draft
    evolution, documented.
- vs all 8 post-r72 (55-row) refs (r73-baseline frozen55, r73-reviewer
  pg-pre, r73-simplifier preland, r72-scribe landed{1,4},
  r72-simplifier landed, r72-reviewer pg-r1, r72-reviewer uwrap):
  **0 mismatches on all 55 common rows**; `new_only` = exactly the 25
  r73-added keys. (uwrap additionally carries its documented
  `reorder_self|wire_topology` FAIL.)
- vs all 6 pre-r72 (36-row) refs (r72-baseline, r72-scribe pre1,
  r72-reviewer pg-pre, r72-simplifier preland, r71-reviewer pg-6,
  r71-simplifier del-pg-vB): **0 mismatches on all 36 common rows**;
  `new_only` = exactly 44 keys = 19 r72 reorder rows + 25 r73 rows —
  the r72 and r73 moves both preserved prior rows, re-confirmed.

## Post-commit re-verification — `ae6cb16` landed 16:41:00Z

The r74 move commit landed mid-session (operator `ci`; **714
insertions / 0 deletions**: `love_battery.py` +292, NEW fixture
`love_phys_probe/` `conf.lua` +20 + `main.lua` +234,
`reports/round-74/r74-author.md` +168). Watcher provenance
(`poll.log`): author worktree divergence first observed **16:37:30Z**
(`love_battery.py` `25977ad9`→`0e11b6b3`, mid-edit), commit
**16:41:00Z**. The frozen surface `1275746` is the move commit's
**direct parent** (`git rev-parse ae6cb16^` = `1275746`) — a provably
pre-move before-state, and this baseline its verified-stable referent.

- **Prior-row bytes stable**: `love_battery.py` `CASES` and
  `SPLICE_CELLS` blocks **byte-identical** `1275746`→`ae6cb16`
  (extraction equality check); the +292 lines are the `IW_CELLS`
  lattice (18 tuple rows, spawned **last** per `love_battery.py:448`
  comment — the fatal-cell ordering guard from the author brief),
  `IW_LINE`/`IW_KV` parsers, and the per-cell `love love_phys_probe`
  spawn loop. `IW_CELLS` row count = **18** matching the commit claim.
- **Sibling batteries untouched** (byte-stability `1275746`→`ae6cb16`):
  `run_battery.py` `f55c27d8`→same, `pygame_battery.py` `6d3fbf5f`→
  same, `pygame_probe.py` `8e15e0d2`→same, `love_probe/main.lua`
  `a0afe6ca`→same, `conf.lua` `0b45ef73`→same,
  `descendant_pipe_probe.gd`/`stream_attribution_probe.gd` same — all
  STABLE. Godot CASES still 81 (+7 meta = 88-row flagless); pygame
  still 73 CASES + 7 RAW (80).
- **Post-commit battery re-runs on live `ae6cb16`** (scratch
  `*-postland/`, live fixture path):
  - love: **37/37 PASS** (`love-…164150119591Z`, sha `1bd2db02…`) —
    15 CASES + 4 splice + **18 new `iw|cell=*` rows**; all 19 prior
    rows pinned/verdict-identical vs my frozen receipt (0 mismatches);
    `new_only` = exactly the 18 IW keys.
  - pygame: **80/80 PASS** (`pygame-…164158853158Z`, sha `899bbbf3…`)
    — control family green on the moved tree; 0 pinned/verdict
    mismatches vs frozen receipt on all 80 rows.
  - godot flagless: **88/88 PASS** first-pass clean
    (`…164208871680Z`, sha `9b0d4ef3…`); 0 tuple mismatches on all
    88 rows vs frozen receipt.
- Net: the move is byte-conservative on prior rows (pure insertion —
  0 deletions anywhere), sibling counts unchanged (godot 88 flagless,
  pygame 80), love count grew 19→37 exactly by the declared 18 IW
  cells, all landed-PASS on this host (LOVE 11.5, loveAssert
  unconditional per the commit message).

## Pinned boundary rows — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release`: PASS, flags
  `["--spawn-forge-release"]` — origin-blind signature acceptance
  reproduced, tuple-identical to r63–r73.
- `divergence_table` seam rows: 9-row table, same divergent pattern
  as r68–r73.
- `splice_*` LOVE cells (4/4): inwindow 80/200 spliced, beyond 240/200
  clean, crossed 300/400 spliced, tight 80/50 clean — the
  write-through `io.write` midline-splice control column holds.
- pygame bufsize pins = **131072** exact on `whs`/`rord`/`self`/
  `infix` rows; `fd1_isatty` = False on `reorder_self`/`infix`/
  `fd2mrg`/`detach` — the harness pipe topology re-confirmed.

## Artifact inventory (`corpus/live/r74-baseline/`)

- `frozen/HEAD-1275746….tar` — `git archive HEAD`, 687,329,280 B,
  sha256 `5175734c…`, deterministic re-run match (gitignored).
- `frozen-extract/` — populated frozen tree (44,829 files + 34
  symlinks, comm-clean vs `git ls-files`); replay surface (gitignored).
- `runs/20261014T160327707475Z/` flagless 88/88 · `…160446750837Z/`
  attribution 89/89 · `…160615371269Z/` ladder 89/89 ·
  `…160749745644Z/` gapladder 89/89.
- `love-runs/love-20261014T160938436041Z/` — 19/19 + 4 splice receipts.
- `pygame-runs/pygame-20261014T160943220687Z/` — 80/80.
- `runs-postland/…164208871680Z/` flagless 88/88 ·
  `love-runs-postland/love-…164150119591Z/` 37/37 ·
  `pygame-runs-postland/pygame-…164158853158Z/` 80/80 — post-commit
  re-verify receipts on live `ae6cb16`.
- `battery{,-attribution,-ladder,-gapladder}.stdout` + `love-`/
  `pygame-battery.stdout` + all-zero `.stderr` siblings;
  `diff_receipts.py` + `diff-output.txt` (this generation);
  `preland-{love,pygame}_battery-{CASES,RAW_CASES}.txt` frozen CASES
  tuple-byte references for the post-land insertion-only check;
  `run-start.txt`, `extract-done.txt`, `preland-head.txt` provenance
  marks; `env.txt`; `poll-commit.sh` + `poll.log` watcher.

## Process hygiene

Post-recovery `ps`: **no godot, no love, no battery processes from
this seat** (the dead generation left none). Sibling wave-14 seats in
flight: r74-author (`scratch_iw` sketch), r74-boundary (love cells +
fifo-open SIGTERM-immunity arms — the carried guard), r74-scout/
r74-scribe reports already landed, g3d r83-author godot probes on the
sibling lane. `git status` from this seat: zero tracked modifications
introduced — only the pre-existing sibling `M corpus/live/r72-
simplifier/{snapshots/log.txt,watch.log}` and untracked `r7*`/`r83*`
scratch paths.

## UNKNOWNs / caveats

- **Recovery boundary:** the six frozen-surface replays were executed
  by the prior generation; this generation's claim there is bounded
  to receipt-level verification (verdicts.json PASS + row counts +
  seed provenance + zero-byte stderrs + frozen-tree identity
  re-derived deterministically). No replay was re-run — the frozen
  extract is pristine and the receipts internally consistent. The
  post-commit re-verify (this generation, all three families on live
  `ae6cb16`) is first-hand.
- Naturally varying fields (`command`, `scratch`, `xdg_data_home`,
  pids, `elapsed_seconds`, `seed`, receipt shas, rep-level
  `output_lines`, `descendant_alive_at_return`,
  `descendant_kernel_ppid_at_return`, bound-pinned `observed`) are
  outside compared scope, per r62–r73 precedent.
- The r74 declared claims (interior-write gating partition
  {refused|deferred|fatal} inside Box2D callbacks, per-callback
  channel-split, partial-capture FAIL semantics) are **not
  adjudicated here** — this receipt is the verified-stable
  before-state. What is pinned: at frozen `1275746` the Godot
  gap-relative fabrication bound, LOVE splice control column, the
  full r72 reorder lattice and the r73 infix/detach/fd2mrg/node-census
  cells reproduce cell-for-cell (80/80), and the LOVE fixture pair
  carries zero physics-callback bytes pre-move.
- Not re-measured here (carried from r61–r73): signal-origin
  indistinguishability of `returncode`; live-window forgery under the
  poll() gate; >1 descendant depth, >64KiB descendant writes, exported
  builds, non-POSIX unprobed; pygame mixer under AUDIODRIVER=dummy,
  event-queue overflow, pygame-ce divergence; love2d release-vs-debug
  Box2D assert behavior is build-dependent (this host's love is
  `LOVE 11.5` system build — assert class to be recorded by the
  author seat).
