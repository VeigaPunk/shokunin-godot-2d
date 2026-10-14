# Round 75 baseline report — frozen HEAD replay + drift-diff (host: devin)

Seat: g2d baseline (LEAF). Immutable before-state for the r75 wave: no
tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r75-baseline/` (`frozen/` gitignored by
`corpus/.gitignore:4 live/*/frozen/`, `frozen-extract/` by
`live/*/*extract*/`, `runs/` by `corpus/live/.gitignore:1 runs/`) plus
this report.

Timeline: HEAD frozen at `2a2c337` ("r71 late-filed seat reports",
committed 2026-10-14 14:25:08Z) — archive + extract 17:30:2x–17:30:38Z,
all seven family replays 17:31:11Z–17:39:05Z (incl. the gapladder
rerun after one crash-probe flake). The r75 declared
axis-move — `love_battery.py` + `love_phys_probe/` deferred
interior-write cells (critic C1 additive twins `bc_destroy_unp` /
`bc_setvel_unp`, C3 containment-level pcall partition, `esc_fn` pins,
joint stretch surface; per `tasks/g2d-author.md`) — **landed
mid-session** as `2e3ae8e` (committed 2026-10-14 14:40:05 -0300;
author worktree divergence first observed 17:36:00Z). The frozen
surface `2a2c337` is the move commit's **direct parent** — a provably
pre-move before-state, and this baseline its verified-stable
referent. It carries the r74 move `ae6cb16` + r74 folds `35dcbf7` +
report-last `b2b20f2` already committed, and none of the r75 arm's
tokens exist in the frozen fixtures.

## Frozen-tree provenance — archive + extracted replay (r69–r74 procedure)

- Frozen source: `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
  archive HEAD -o corpus/live/r75-baseline/frozen/HEAD-2a2c337ef92a4fdf5543db14eebf1518e79184c4.tar`.
- HEAD frozen: `2a2c337ef92a4fdf5543db14eebf1518e79184c4`; parent
  `b2b20f2` (r74 report-last) → `35dcbf7` r74 folds → `ae6cb16` r74
  IW-lattice move → `1275746` r73 report-last.
- Archive: **687,564,800 bytes**, sha256
  `395e7e06e9446f0f9e5cf8d4c7d5a22b6a1ca1354379e2d422ffb1d004876af0`.
  `git archive HEAD | sha256sum` re-run = **identical** — the frozen
  tar is byte-for-byte a deterministic archive of current HEAD.
- Tar members: **44,888 non-dir entries** == `git ls-files | wc -l`
  = 44,888 exactly (r74: 44,873 — delta +15 is r74-round committed
  receipts/reports). `comm -23` (missing) = **0**, `comm -13` (extra)
  = **0**.
- No tracked nested snapshot dirs at HEAD (`git ls-tree -r HEAD
  --name-only | grep -cE '^corpus/live/[^/]+/(frozen|head|snapshot|base)/
  |^corpus/live/[^/]+/tree/'` → **0**). Broader grep
  (`frozen|/tree/|node_modules|extract`) = 209 tracked paths, all
  incidental filenames (same class as r73/r74).
- Extraction: `tar -xf` into `corpus/live/r75-baseline/frozen-extract/`.
  `find . -type f` = 44,854 files + **34 symlinks** = 44,888 ==
  `git ls-files` exactly.
- Fixture digests extract == `HEAD:` blob == live tree (pre-move) for
  all 10 checked: `run_battery.py` `f55c27d8…`, `pygame_battery.py`
  `6d3fbf5f…`, `pygame_probe.py` `8e15e0d2…`, `love_battery.py`
  `b448c727…` (the post-`35dcbf7` fold byte), `love_probe/main.lua`
  `a0afe6ca…`, `love_probe/conf.lua` `0b45ef73…`,
  `love_phys_probe/main.lua` `2c0ac378…`, `love_phys_probe/conf.lua`
  `85aa6232…`, `descendant_pipe_probe.gd` `c86bda84…`,
  `stream_attribution_probe.gd` `dc0b0d5c…`.
- `verdicts.json["seed"]` on all 5 godot runs records
  `…/r75-baseline/frozen-extract/corpus/fixtures`; LOVE `probe_dir` and
  pygame `probe` fields record the frozen-extract fixture paths —
  replays provably executed frozen-HEAD bytes.
- Post-replay pristine check: `find frozen-extract -newer
  extract-done.txt` → **0 entries**.
- Pre-move token referents in frozen fixtures (the r75 move's claimed
  surface): `bc_destroy_unp|bc_setvel_unp|esc_fn|containment|joint|
  setFilterData|step_abort` = **0 occurrences** in `love_battery.py`
  and **0** in `love_phys_probe/main.lua` — the deferred-cell arm is
  entirely absent pre-move. (`_unp` hits = the r74 `bc_setpos_unp`/
  `bc_newbody_unp` cells; `pcall`/`deferred` hits = r74-arm internals.)

## Exact invocations (this generation, all receipts first-hand)

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`X=corpus/live/r75-baseline/frozen-extract`:

```
python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r75-baseline/runs
  # runs/20261014T173111477265Z verdicts.json PASS 88/88

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r75-baseline/runs --probe-stream-attribution
  # runs/20261014T173223691637Z PASS 89/89 + stream-attribution-verdicts.json

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r75-baseline/runs --probe-midlineforge-ladder
  # runs/20261014T173347454358Z PASS 89/89 + midlineforge-ladder-verdicts.json

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r75-baseline/runs --probe-midlineforge-gapladder
  # runs/20261014T173513597535Z FAIL 86/89 — see crash-flake section
  # runs/20261014T173715335871Z PASS 89/89 (rerun, clean referent)

python3 $X/corpus/fixtures/love_battery.py \
  --runs corpus/live/r75-baseline/love-runs
  # love-runs/love-20261014T173111472447Z PASS 37/37

python3 $X/corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r75-baseline/pygame-runs
  # pygame-runs/pygame-20261014T173111480699Z PASS 80/80
```

All seven `.stderr` captures **0 bytes**. Environment (`env.txt`):
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), LOVE 11.5
"Mysterious Mysteries" (`/usr/bin/love`), Python 3.14.7 + pygame 2.6.1
/ SDL 2.32.72, `io.DEFAULT_BUFFER_SIZE` = **131072** (THIS build's
constant — carried guard), node v24.21.0 — same profile as r70–r74.

## Before-state receipt summary (frozen `2a2c337`, pre-move)

- Flagless godot `verdicts.json`: `"verdict": "PASS"`, **88/88**,
  sha256 `5c96684d6161f1dc…`; `battery.stdout` tail `PASS battery: …`.
- `--probe-stream-attribution`: **89/89** (adds exactly
  `probe_stream_attribution`), sha256 `1bb9b62fb989a16f…`; artifact
  sha256 `be5e38858720c4c5…`.
- `--probe-midlineforge-ladder`: **89/89** (adds exactly
  `probe_midlineforge_ladder`), sha256 `ea1f3bcd6ccad0e2…`; artifact
  sha256 `2d4ea2d6cbbd26e3…`.
- `--probe-midlineforge-gapladder` (rerun): **89/89** (adds exactly
  `probe_midlineforge_gapladder`), sha256 `f2f9e8fa7476c844…`; artifact
  sha256 `527fb787c734e8f1…`.
- LOVE `verdicts.json`: PASS **37/37**, sha256 `5b1c930963fd3526…`
  (15 CASES + 4 splice + **18 `iw|cell=*` rows** — the post-r74-move
  shape; `done_marker=True`, probe_exit 0).
- pygame `verdicts.json`: PASS **80/80**, sha256 `3c8d5f539ca58b2a…`
  (73 CASES + 7 RAW_CASES); these 80 are exactly the prior rows the
  r75 move's insertion-only claim must preserve.
- `probe_error_clause_surface`: 34 discriminations all True on the 3
  clean godot runs — the "surface 34/34" envelope again.
- Stream-attribution artifact: 24 discriminations, 9-row
  `divergence_table`, `raw_merged_sha256` fields present.
- Ladder artifact: `measured_window` landed `[0,40,80,120,160]`,
  missed `[240]`, mixed `[]`, lo 0 / hi 240 / nominal_gap 200;
  8 discriminations all True — identical to all 5 refs.
- Gapladder artifact (rerun): `landed_gaps_ms` `[100,200,400,800,
  400,800,800]` (trailing three = crossed cells), missed `[50]`,
  `crossed_cells_ms` `[[300,400],[300,800],[600,800]]`, 12
  discriminations True.
- pygame reorder lattice at frozen HEAD: `infix|bufsize` = **131072**
  exact; `node_census` `node_present=True` `v24.21.0`; the r72/r73
  pins (`infix|injected_rel` 126011, `fd2mrg` prefix_reorder, `detach`
  eof_hold, `node_big` infix inj@65541 wire 200019) all reproduced.

## crash_spontaneous_sigabrt flake — first gapladder run (documented, rerun clean)

The first gapladder replay `…173513597535Z` returned FAIL 86/89:

- `crash_spontaneous_sigabrt`: `expected_exit=-6` (SIGABRT),
  `actual_exit=-9` (SIGKILL). The probe DID emit its signature line
  `SPONTANEOUS_CRASH_PROBE: expected signature` and the allowlisted
  `ERROR: r60 spontaneous crash probe` — output complete, then the
  process died to an external SIGKILL rather than its own abort.
- Cascade: `probe_spontaneous_crash_classification` meta FAIL
  (`sigabrt_exit=-9` → `sigabrt_expected_-9_rejects` discrimination
  False) and `probe_error_clause_surface` meta FAIL (census row
  flipped) — both pure consequences of the same `-9`.
- Attribution analysis: memory pressure is excluded (`free -m` at
  rerun: 21.4 GB available, swap 31 GB free); `dmesg` unreadable on
  this host. Concurrent sibling seats WERE live: g2d r75-boundary
  running `timeout -k 2 3 love …` cells and audio r76-boundary
  `timeout -s KILL` probes — a cross-seat signal/timeout sweep is
  consistent with an external `-9`, though no direct killer is
  provable from returncode (the receipt's own bounded_claim says
  exactly this: "signal origin unprovable from returncode").
- The same flake did NOT recur: the identical-command rerun
  `…173715335871Z` passed 89/89 with `crash_spontaneous_sigabrt`
  `actual_exit=-6`. Both receipts retained. The clean rerun is the
  drift-diff referent; the flake is rep-level nondeterminism in the
  harness environment, not a fixture/HEAD property (frozen bytes
  identical across both runs).

## Drift vs committed r68–r74 receipts — ZERO on compared tuples

`diff_receipts.py` (output `diff-output.txt`, 374 lines): Godot rows on
the 7-tuple (script, flags, expected_exit, actual_exit, signature,
verdict, error) + meta discriminations; LOVE/pygame rows on (arm, key,
pinned, verdict).

**Godot — 52 comparisons across 13 refs, 0 tuple mismatches** on all
common rows (flagless/attrib/ladder/gapladder × {r74-baseline ×5,
r74-reviewer pre-godot, r73-baseline ×2, r71-baseline, r69-scribe,
r69-simplifier ×2, r68-boundary}):

- Row-set deltas are only the flag-gated probe rows — expected shape.
- Meta note (documented class, unchanged since r72): vs the two r69
  91-row refs the `probe_midlineforge_gapladder` discrimination map
  carries 2 extra True keys (`crossed_cells_elapsed_tracks_gap`,
  `crossed_cells_refute_absolute_edge`) — those refs predate the
  crossed-cells addition. The post-crossed-cells refs and all
  r73/r74 refs match **exactly**.
- Attribution artifact volatile-stripped deep-diff: **0 diffs** vs
  r74-baseline, r73-baseline and both r69 refs; 24 diffs vs
  r68-boundary = the `raw_merged_sha256` fields the r69 upgrade added
  (ref predates it; `stream_accept` arm digest identical).
- Ladder artifact: `measured_window`, per-cell (offset,outcome), and
  all discriminations **identical to all 5 refs**.
- Gapladder artifact (rerun referent) vs r74-baseline: 83 raw diffs,
  vs r73-baseline 82 — all rep-level jitter (output_lines embedded
  pids, `descendant_alive_at_return` flips,
  `descendant_kernel_ppid_at_return` presence; same class r73=78 /
  r74=78). vs r69-scribe/simplifier landed: 8 diffs = crossed-cells
  addition (refs predate). vs r69-simplifier base: 80 diffs, same
  jitter class; discriminations identical.

**LOVE — 38 references:**

- **0 mismatches vs all 13 post-r74 (37-row) refs**: r74-baseline
  postland, integrator-r74-fold, r74-author ×2, r74-critic replay,
  r74-reviewer ×2, r74-simplifier baseline + A + B + L, r74-verifier ×2.
- **0 mismatches on all common rows vs all 25 pre-r74 (19-row) refs**:
  `new_only` = exactly the 18 IW keys on every ref (r71-simplifier
  del-vB carries 18 rows — predates `pump|pump_needed`; common 18
  clean, `new_only` = 18 IW + that row).
- One scenario ref (not drift): r74-reviewer `crash-runs` —
  15 verdict-only diffs (`pinned` identical on every row; the ref is
  a deliberate early-crash arm: `probe_exit=3`, `done_marker=False`).

**pygame — 51 references:**

- **0 mismatches** vs all clean 80-row refs (r74-baseline ×2,
  r74-reviewer pre-pg, integrator-r74-fold, r73-baseline postland,
  r73-author ×2, r73-critic replay + rep0a + rep2b + detach-55,
  r73-reviewer pg-r{1,2,3} + envsweep + loaded, r73-simplifier landed
  + del-control + vA/vB/vD/vE/vF/vG (vC: 78 rows, documented
  del-measure drop of the `pump` pair — common clean), r73-verifier
  run{3,5}).
- Ref-side intentional variance (scenario refs, identical pinned):
  nodeabsent refs (r73-critic, r73-reviewer, r73-verifier) 15
  `node_*` FAILs each; stuck-detach refs (r73-critic, r73-reviewer)
  `detach|wire_topology` FAIL; unbuf/uwrap refs (r73-critic,
  r73-reviewer, r72-reviewer) `wire_topology`-class FAILs;
  r73-reviewer `infmissing` 4 `infix_*` FAILs; r73-verifier `run1`
  pre-land draft key-rename (`injected_at`/`tail_at` vs landed
  `injected_rel`/`tail_rel`).
- vs all 8 post-r72 (55-row) refs: **0 mismatches on all 55 common
  rows**; `new_only` = exactly the 25 r73-added keys.
- vs all 6 pre-r72 (36-row) refs: **0 mismatches on all 36 common
  rows**; `new_only` = exactly 44 keys = 19 r72 + 25 r73 rows.

## Post-commit re-verification — `2e3ae8e` landed 17:40:30Z

The r75 move commit landed mid-session ("r75: deferred interior-write
cells — 2 predictions confirmed, 2 new classes discovered"; **422
insertions / 11 deletions**: `love_battery.py` +161, `love_phys_probe/
main.lua` +103, `reports/round-75/r75-author.md` +169). Watcher
provenance (`poll.log`): author worktree divergence first observed
**17:36:00Z** (`love_phys_probe/main.lua` `2c0ac378`→`c80e2ba3`,
mid-edit), commit **17:40:30Z** (committer timestamp 14:40:05 -0300).
The frozen surface `2a2c337` is the move commit's **direct parent**
(`git rev-parse 2e3ae8e^` = `2a2c337`) — a provably pre-move
before-state, and this baseline its verified-stable referent.

- **Prior-row bytes**: `CASES` and `SPLICE_CELLS` blocks in
  `love_battery.py` **byte-identical** `2a2c337`→`2e3ae8e`
  (`preland-*.txt` extraction equality); pygame `CASES`/`RAW_CASES`
  byte-identical. `IW_CELLS` is byte-identical **except two prior
  rows**: `iw_bc_setpos_unp` and `iw_bc_newbody_unp` each gained a
  pinned `"esc_fn"` key (`"setPosition"` / `"newBody"` — the brief's
  declared "esc_fn pin on unp rows"), a pinned-dict tightening on 2
  of 37 prior rows, not a byte-identical hold. The +74 lines inside
  the block are the 7 new cells, appended inside the block
  (`119,192d118` pure insertion): `iw_bc_destroy_unp`,
  `iw_bc_joint_destroy`, `iw_bc_joint_new`, `iw_bc_setfilter`,
  `iw_bc_setpos_wp`, `iw_bc_setvel_unp`, `iw_pre_retfalse`.
- **Other deletions** (8 in love_battery.py): 6 header-comment lines
  (expected_class docstring rewritten for esc_fn/new keys) + the 2
  err_on lines replaced by the esc_fn versions — no executable or
  pinned-value removal. `love_phys_probe/main.lua` carries 3 line
  deletions inside existing function bodies (`c_pre` local +
  `world:update(FIXED)` + a `fired` guard line) — the containment
  arm restructures the update call site.
- **Sibling batteries untouched** (blob-equality `2a2c337`→`2e3ae8e`):
  `run_battery.py`, `pygame_battery.py`, `pygame_probe.py`,
  `love_probe/main.lua`, `love_probe/conf.lua`,
  `love_phys_probe/conf.lua`, `descendant_pipe_probe.gd`,
  `stream_attribution_probe.gd` — all STABLE.
- **Post-commit battery re-runs on live `2e3ae8e`** (scratch
  `*-postland/`, live fixture path):
  - love: **44/44 PASS** (`love-…174348368669Z`, sha `7ec38ee1…`) —
    15 CASES + 4 splice + 18 prior IW + **7 new cells**; `new_only` =
    exactly those 7 keys; **0 pinned/verdict diffs on all 37 prior
    rows** vs my frozen receipt (the esc_fn addition lives inside the
    row's expected-dict, outside the compared (arm,key,pinned,
    verdict) tuple — receipt-level zero drift).
  - pygame: **80/80 PASS** (`pygame-…174348378371Z`, sha `6997d658…`)
    — 0 mismatches on all 80 rows vs frozen receipt.
  - godot flagless: **88/88 PASS** (`…174358491722Z`, sha
    `c2343bc7…`) — 0 tuple mismatches on all 88 rows vs frozen
    receipt.
- Landed new-cell classes (postland receipt, LOVE 11.5 this host):
  `bc_destroy_unp`→**deferred** (predicted deferred-drain —
  confirmed), `bc_setvel_unp`→**applied** (predicted — confirmed),
  `bc_setpos_wp`→**refused_abort** (C3 containment level: pcall
  around `world:update` converts the same write's outcome —
  refused write + aborted step + transient lock + next-step
  recovery), `bc_joint_new`→**refused**, `bc_joint_destroy`→
  **deferred**, `bc_setfilter`→**applied**, `pre_retfalse`→
  **ignored**. Consistent with the commit's "2 predictions
  confirmed, 2 new classes discovered" (refused_abort + ignored
  extend the r74 four-class partition to six).

## Pinned boundary rows — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release`: PASS, flags
  `["--spawn-forge-release"]` — origin-blind signature acceptance
  reproduced, tuple-identical to r63–r74.
- `divergence_table` seam rows: 9-row table, same divergent pattern
  as r68–r74.
- `splice_*` LOVE cells (4/4): inwindow 80/200 spliced, beyond 240/200
  clean, crossed 300/400 spliced, tight 80/50 clean.
- pygame bufsize pins = **131072** exact on `whs`/`rord`/`self`/
  `infix` rows; `fd1_isatty` = False on `reorder_self`/`infix`/
  `fd2mrg`/`detach`.
- IW lattice at frozen HEAD (the r74 arm inside this HEAD): 18/18
  `iw|cell=*` PASS — the {refused|deferred|fatal|applied} partition
  holds on the pre-move surface; the r75 `bc_destroy_unp`/`bc_setvel_unp`
  twins and containment cells will land as `new_only` additions.

## Artifact inventory (`corpus/live/r75-baseline/`)

- `frozen/HEAD-2a2c337….tar` — `git archive HEAD`, 687,564,800 B,
  sha256 `395e7e06…`, deterministic re-run match (gitignored).
- `frozen-extract/` — populated frozen tree (44,854 files + 34
  symlinks, comm-clean vs `git ls-files`); replay surface (gitignored).
- `runs/20261014T173111477265Z/` flagless 88/88 · `…173223691637Z/`
  attribution 89/89 · `…173347454358Z/` ladder 89/89 ·
  `…173513597535Z/` gapladder FAIL 86/89 (crash flake, retained) ·
  `…173715335871Z/` gapladder rerun 89/89 (diff referent).
- `love-runs/love-20261014T173111472447Z/` — 37/37.
- `pygame-runs/pygame-20261014T173111480699Z/` — 80/80.
- `runs-postland/…174358491722Z/` flagless 88/88 ·
  `love-runs-postland/love-…174348368669Z/` 44/44 ·
  `pygame-runs-postland/pygame-…174348378371Z/` 80/80 — post-commit
  re-verify receipts on live `2e3ae8e`.
- `battery{,-attribution,-ladder,-gapladder,-gapladder-rerun}.stdout`
  + `love-`/`pygame-battery.stdout` + `*-postland.stdout` + all-zero
  `.stderr` siblings;
  `diff_receipts.py` + `diff-output.txt`;
  `preland-{love,pygame}_battery-{CASES,SPLICE_CELLS,IW_CELLS,RAW_CASES}.txt`
  frozen tuple-byte references for the post-land insertion-only check;
  `run-start.txt`, `extract-done.txt`, `preland-head.txt` provenance
  marks; `env.txt`; `poll-commit.sh` + `poll.log` watcher.

## Process hygiene

Post-replay `ps` (after all 7 frozen + 3 postland runs): **no godot,
no love, no battery processes from this seat**; the only live
fixtures belong to the sibling g3d r84-author seat
(`run_battery.py`/`godot` under
`corpus/live/r84-author/`). Sibling wave-15 seats observed in flight
during the session: r75-author (worktree divergence 17:36:00Z →
commit `2e3ae8e` 17:40:30Z), r75-boundary (`timeout -k 2 3 love
cells`), audio r76-boundary (`timeout -s KILL` probes).
`git status` from this seat: zero tracked modifications introduced —
only the pre-existing `M corpus/live/r72-simplifier/{snapshots/
log.txt,watch.log}` (sibling residue) and untracked
`r7*/integrator-r74-fold` scratch paths plus my own `r75-baseline/`
+ `reports/round-75/`.

## UNKNOWNs / caveats

- The `crash_spontaneous_sigabrt -9` is unattributed beyond
  "external SIGKILL" — signal origin unprovable from returncode on
  this host (dmesg restricted); sibling timeout/kill sweeps are the
  consistent hypothesis, not proven. One occurrence in 7 replays;
  the clean rerun is the referent.
- Naturally varying fields (`command`, `scratch`, `xdg_data_home`,
  pids, `elapsed_seconds`, `seed`, receipt shas, rep-level
  `output_lines`, `descendant_alive_at_return`,
  `descendant_kernel_ppid_at_return`, bound-pinned `observed`) are
  outside compared scope, per r62–r74 precedent.
- The r75 declared claims (deferred-drain class of unprotected
  destroys, containment-level pcall partition, esc_fn pins, joint
  surface) are **not adjudicated here** — this receipt is the
  verified-stable before-state plus a receipt-level post-land
  re-verification. The landed new-cell classes are reported as
  observed on this host; their adjudication belongs to the wave's
  verifier/critic seats.
- The two `*_unp` IW rows' gained `esc_fn` pins mean `IW_CELLS` is
  not a byte-identical hold — documented exactly (2 pinned-dict
  keys on 2 of 37 prior rows; tuple-level receipts unchanged).
