# Round 76 baseline report — freeze + post-commit zero-drift (host: devin)

Seat: g2d baseline (LEAF). Immutable before-state for the r76 wave: no
tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r76-baseline/` (untracked scratch; the
`freeze/` layout mirrors the r69–r75 `frozen/`+`frozen-extract/`
procedure — `live/*/*extract*/` covers `freeze/extract/`, `runs/`
covers the run dirs) plus this report.

Battery scope per brief: LOVE battery (`love_battery.py`, 44 rows this
HEAD) + pygame battery (`pygame_battery.py`, 80 rows). The r76
declared axis-move touches `love_battery.py` + `love_phys_probe/`
only (`tasks/g2d-author.md`: drain-deferral hazard cell, in-callback +
double `world:destroy()` edges, SayGoodbye/drain observer stretch,
per-contact preSolve-return-false stretch; insertion-only, all 44
prior cases byte-identical, fatal cells last).

## Phase 1 — PRE-COMMIT freeze of the r75-closed tree

Timeline: HEAD frozen at `ddd455b49f0594610a065b360b8a3211fa510c09`
("r75 report-last: 9 seat reports + adjudicator + LOG/SCORECARD",
committed 2026-10-14 15:03:16 -0300) — archive 18:23:11Z + extract
done 18:23:17Z, both frozen battery replays launched 18:23:40Z,
complete 18:23:50Z (both PASS). The r76 author commit `6ca715d`
landed mid-session 18:32:13Z; post-commit replays
18:35:35Z–18:35:46Z (both PASS).

### Frozen-tree provenance — archive + extracted replay

- Frozen source: `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
  archive HEAD -o corpus/live/r76-baseline/freeze/HEAD-ddd455b49f0594610a065b360b8a3211fa510c09.tar`.
- HEAD frozen: `ddd455b49f0594610a065b360b8a3211fa510c09`; parent
  `be79ad1` (r75 critic/reviewer folds) → `2e3ae8e` (r75 IW deferred-cell
  move) → `2a2c337` → `b2b20f2` (r74 report-last).
- Archive: **687,759,360 bytes**, sha256
  `ab303b1d54f14704278c87e3dcd19de8fff4c32ee30c8c51e4ba0a59f4970a78`.
  `git archive HEAD | sha256sum` re-run = **identical** — byte-for-byte
  deterministic archive of HEAD.
- Tar members: **44,898 non-dir entries** == `git ls-files | wc -l`
  = 44,898 exactly (r75: 44,888 — delta +10 is the r75 report-last
  payload). `comm -23` (missing) = **0**, `comm -13` (extra) = **0**.
- No tracked nested snapshot dirs at HEAD (`git ls-tree -r HEAD
  --name-only | grep -cE '^corpus/live/[^/]+/(frozen|head|snapshot|base|freeze)/
  |^corpus/live/[^/]+/tree/'` → **0**).
- Extraction: `tar -xf` into `freeze/extract/`: **44,864 files +
  34 symlinks** = 44,898 == `git ls-files` exactly.
- Fixture digests extract == `HEAD:` blob == live tree for all 10
  checked: `run_battery.py` `f55c27d8…`, `pygame_battery.py`
  `6d3fbf5f…`, `pygame_probe.py` `8e15e0d2…`, `love_battery.py`
  `2f993578…` (post-`be79ad1` fold byte), `love_probe/main.lua`
  `a0afe6ca…`, `love_probe/conf.lua` `0b45ef73…`,
  `love_phys_probe/main.lua` `9c375230…`, `love_phys_probe/conf.lua`
  `85aa6232…`, `descendant_pipe_probe.gd` `c86bda84…`,
  `stream_attribution_probe.gd` `dc0b0d5c…`.
- `verdicts.json["probe_dir"]`/`["probe"]` on both runs record
  `…/r76-baseline/freeze/extract/corpus/fixtures` — replays provably
  executed frozen-HEAD bytes.
- Post-replay pristine check: `find freeze/extract -newer
  extract-done.txt` → **0 entries**.
- Pre-move surface counts: love_battery CASES=15, SPLICE_CELLS=4,
  IW_CELLS=25 (44 total — the post-r75 shape); pygame CASES=73,
  RAW_CASES=7 (80 total). Block bodies snapshotted to
  `preland-*-{CASES,SPLICE_CELLS,IW_CELLS,RAW_CASES}.txt` (block sha256s:
  love CASES `9d41a0cca7a2bd44`, SPLICE `da60e2121be90e66`,
  IW_CELLS `3f0c6846e4b62b95`; pygame CASES `d4c63ef21b59c96f`,
  RAW `8fb996ee3b84f3ab`).

### Exact invocations (this generation, all receipts first-hand)

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`X=corpus/live/r76-baseline/freeze/extract`:

```
python3 $X/corpus/fixtures/love_battery.py \
  --runs corpus/live/r76-baseline/freeze/love-runs
  # love-runs/love-20261014T182340536201Z PASS 44/44, stderr 0 bytes

python3 $X/corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r76-baseline/freeze/pygame-runs
  # pygame-runs/pygame-20261014T182340543528Z PASS 80/80, stderr 0 bytes
```

Environment (`env.txt`): LOVE 11.5 "Mysterious Mysteries"
(`/usr/bin/love`), Godot 4.7.2.stable (`/usr/bin/godot`, unused this
round), Python 3.14.7 + pygame 2.6.1 / SDL 2.32.72,
`io.DEFAULT_BUFFER_SIZE` = **131072**, node v24.21.0 — same profile
as r70–r75.

### Before-state receipt summary (frozen `ddd455b`, pre-move)

- LOVE `verdicts.json`: `"verdict": "PASS"`, **44/44** (15 CASES +
  4 splice + **25 `iw|cell=*` rows** — 18 r74 IW + 7 r75 cells),
  `done_marker=True`, probe_exit 0, sha256
  `8bc095c458d2fdfcb936679cab8e2d38d351a7beebac5840695d7cc2520a1ab4`.
- pygame `verdicts.json`: PASS **80/80** (73 CASES + 7 RAW_CASES),
  sha256 `4e596347a7774c8d6aeb2e4cb46781a72d85f017d3e76ba62ba50882371cfe3f`.
- Per-cell receipt shas: `freeze/receipt-shas.txt` (124 rows:
  verdicts.json sha + canonical-JSON sha256 per (arm|key) row).

### Drift vs committed r73–r75 receipts — ZERO on compared tuples

`diff_receipts.py` (output `diff-output.txt`): rows compared on
(arm, key, pinned, verdict).

**LOVE — 14 references:**

- **0 mismatches vs all 10 post-r75 (44-row) refs**: r75-baseline
  postland, integrator-r75-fold, integrator-r75-verify, r75-verifier ×2,
  r75-reviewer, r75-critic, r75-simplifier c0_control, r75-author r1+r4 —
  `common=44 new_only=0 old_only=0` on every one.
- **0 mismatches on all 37 common rows vs all 4 pre-r75 (37-row)
  refs** (r75-baseline frozen, r74-baseline postland, r74-verifier,
  r74-simplifier baseline); `new_only` = exactly the 7 r75-added IW
  keys on every ref (`bc_destroy_unp`, `bc_joint_destroy`,
  `bc_joint_new`, `bc_setfilter`, `bc_setpos_wp`, `bc_setvel_unp`,
  `pre_retfalse`).

**pygame — 7 references:**

- **0 mismatches vs all 7 80-row refs**: r75-baseline frozen +
  postland, integrator-r75-fold, r74-baseline frozen + postland,
  integrator-r74-fold, r73-baseline postland —
  `common=80 new_only=0 old_only=0` on every one.

The frozen `ddd455b` tree is a verified-stable pre-move surface.

## Phase 2 — POST-COMMIT watch + committed-tree re-verification

Watcher: `poll-commit.sh` (20 s cadence, `poll.log`) — fires on HEAD
leaving `ddd455b` and logs first worktree divergence of
`love_battery.py` / `love_phys_probe/{main,conf}.lua` /
`pygame_battery.py` (pre-move shas `2f993578`/`9c375230`/`85aa6232`/
`6d3fbf5f`).

**Author commit LANDED 18:32:13Z** (`poll.log`): worktree divergence
first observed **18:28:52Z** (`love_phys_probe/main.lua`
`9c375230`→`d8f45de6` mid-edit; `love_battery.py` followed), commit
`6ca715d3d0285929210d268ad8bcabc7d8ddf73f` "r76: drain-observer cells
+ destroy edges — deferred_abort class discovered" (committer
timestamp 2026-10-14 15:32:06 -0300). The frozen surface `ddd455b` is
the move commit's **direct parent** (`git rev-parse 6ca715d^` =
`ddd455b49f05…`) — a provably pre-move before-state.

### Commit shape (`git diff ddd455b 6ca715d`, fixture scope)

- `love_battery.py` **+174/-1**; `love_phys_probe/main.lua`
  **+131/-3**; `reports/round-76/r76-author.md` +223 (report, not
  fixture). Total fixture: **+305 insertions / -4 deletions**.
- **Prior-row bytes**: `CASES`, `SPLICE_CELLS` blocks **byte-identical**
  `ddd455b`→`6ca715d` (SequenceMatcher 0 non-equal ops; both also ==
  the frozen-extract snapshots). `IW_CELLS`: 0 delete/replace ops —
  two pure `insert` ops only (+97 and +19 lines). pygame
  `CASES`/`RAW_CASES` **byte-identical** (`byte-identical=True` both).
- **Insertion position (precise)**: the 5 new IW rows land as pure
  insertions preserving every prior row's bytes and relative order —
  `iw_bc_draindefer`, `iw_bc_destroy2`, `iw_bc_jwatch`,
  `iw_pre_retfalse1` inserted before the `*_unp` tail, and
  `iw_bc_worlddestroy` inserted between `iw_bc_setvel_unp` and
  `iw_bc_setpos_unp`. So: insertion-only holds exactly (prior-row
  subsequence preserved verbatim), but the new rows are **not** all at
  the literal block end — they sit ahead of / inside the fatal-cell
  tail, consistent with the fixture's "fatal cells last" ordering
  rule.
- **Deletions**: `love_battery.py` −1 = the `iw_classify` docstring
  line (`refused_abort|ignored|fatal|…` class list rewritten for
  `deferred_abort`/`died`). `main.lua` −3 = `local j_pre` decl,
  `if kind == "joint_destroy" then`, `if wp_mode then` — guard-arm
  restructures inside existing bodies (same class as r75's 3-line
  main.lua deletions). No executable row or pinned value removed.
- **Sibling batteries untouched** (blob-equality
  `ddd455b`→`6ca715d`): `run_battery.py`, `pygame_battery.py`,
  `pygame_probe.py`, `love_probe/main.lua`, `love_probe/conf.lua`,
  `love_phys_probe/conf.lua`, `descendant_pipe_probe.gd`,
  `stream_attribution_probe.gd` — all STABLE.

### Post-commit battery re-runs on live `6ca715d`

cwd = live repo (fixtures at `corpus/fixtures/` — `probe_dir`/`probe`
fields record the live path), runs → `corpus/live/r76-baseline/postland/`:

```
python3 corpus/fixtures/love_battery.py \
  --runs corpus/live/r76-baseline/postland/love-runs
  # love-20261014T183535619051Z PASS 49/49, stderr 0 bytes
python3 corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r76-baseline/postland/pygame-runs
  # pygame-20261014T183535632478Z PASS 80/80, stderr 0 bytes
```

- **LOVE 49/49 PASS**, verdicts.json sha256
  `c871067b2a8be332c311f3e48e71f46dfadb50f488c53cbee4675be2fcca136c`:
  `common=44` vs my frozen receipt, `new_only` = **exactly the 5 r76
  cells** (`iw|cell=bc_draindefer`, `bc_destroy2`, `bc_jwatch`,
  `bc_worlddestroy`, `pre_retfalse1`), `old_only=0`,
  **0 pinned/verdict mismatches on all 44 prior rows** —
  receipt-level zero drift vs the freeze.
- **pygame 80/80 PASS**, verdicts.json sha256
  `5f9cd769f7bf263c48c7bd4c5e238b5f343f8b6f95e7c2125e08e609404a5f0e`:
  `common=80 new_only=0 old_only=0`, **0 mismatches** vs frozen —
  byte-stable on the compared tuple.
- **Whole-row byte-compare** (canonical-JSON sha256 per row,
  frozen↔postland): LOVE **39/44 prior rows byte-identical**; the 5
  differing rows differ in the `observed` field ONLY (bound-pinned
  jitter, by construction). pygame **64/80 byte-identical**; 16
  differ in `observed` ONLY. Zero diffs in `arm`/`key`/`pinned`/
  `verdict`/any other field on any prior row — the strongest form of
  the prior-rows-stable claim this tuple space supports.
- Postland receipts vs all committed refs: every 44-row LOVE ref
  shows `common=44 new_only=5` (the same 5 keys) / `mismatches=0`;
  every 80-row pygame ref `common=80`/`mismatches=0`
  (`diff-output.txt` postland section).
- Landed new-cell classes (postland receipt, LOVE 11.5 this host):
  `bc_draindefer`→**deferred_abort** (queued destroy + uncontained
  throw in one callback: epilogue drain skipped, queue drains one
  update late at locked=false — the declared new class),
  `bc_destroy2`→**deferred** (second post-drain destroy refused by
  lifetime guard, per commit body), `bc_jwatch`→**deferred** (joint
  drain point bounded-measured jwlive@73→jwdrop@74; SayGoodbye
  confirmed absent), `pre_retfalse1`→**ignored** (per-contact
  return-false discrimination proven), `bc_worlddestroy`→**died**
  (deferred via destructWorld, dies on next access).

## Artifact inventory (`corpus/live/r76-baseline/`)

- `freeze/HEAD-ddd455b….tar` — `git archive HEAD`, 687,759,360 B,
  sha256 `ab303b1d…`, deterministic re-run match.
- `freeze/extract/` — populated frozen tree (44,864 files + 34
  symlinks, comm-clean vs `git ls-files`); replay surface.
- `freeze/love-runs/love-20261014T182340536201Z/` — 44/44 ·
  `freeze/pygame-runs/pygame-20261014T182340543528Z/` — 80/80.
- `postland/love-runs/love-20261014T183535619051Z/` — 49/49 ·
  `postland/pygame-runs/pygame-20261014T183535632478Z/` — 80/80
  (committed-tree re-verify on live `6ca715d`).
- `freeze/receipt-shas.txt` — per-cell receipt sha table.
- `love-battery.stdout` / `pygame-battery.stdout` /
  `love-postland.stdout` / `pygame-postland.stdout` + 0-byte `.stderr`
  siblings; `diff_receipts.py` + `diff-output.txt`;
  `preland-{love,pygame}_battery-{CASES,SPLICE_CELLS,IW_CELLS,RAW_CASES}.txt`
  frozen tuple-byte references for the post-land insertion-only check;
  `freeze-head.txt`, `run-start.txt`, `extract-done.txt` provenance
  marks; `env.txt`; `poll-commit.sh` + `poll.log` watcher.

## Process hygiene

Post-replay `ps` (after both frozen + both postland runs): **no
love/pygame/battery processes from this seat**; the only live battery
observed is sibling g2d r76-simplifier's mutated-variant replay loop
(`corpus/live/r76-simplifier/runs-v{5,6}`), and g3d r85 seats run in a
separate repo. The commit watcher `poll-commit.sh` self-exited on
commit detection.
`git status` from this seat: zero tracked modifications introduced —
pre-existing sibling residue only (`M corpus/live/r72-simplifier/*`,
untracked `r7*/integrator-r7*` scratch) plus my own
`r76-baseline/` + `reports/round-76/`.

## UNKNOWNs / caveats

- Naturally varying fields (`command`, `scratch`, `xdg_data_home`,
  pids, `elapsed_seconds`, `seed`, receipt shas, rep-level
  `output_lines`, bound-pinned `observed`) are excluded from tuple
  comparison by construction; volatile-embedded rep jitter is a known
  class since r68.
- The insertion-only hold is sequence-exact (all 44 prior rows
  byte-identical, order preserved) but position-exact only under the
  "fatal cells last" ordering rule: `iw_bc_worlddestroy` sits between
  two `*_unp` fatal rows rather than after all of them. Receipt-level
  this is immaterial (`new_only` = exactly the 5 new keys; prior-row
  tuple drift = 0), but a byte-diff reviewer should read "appended at
  end" as "appended ahead of the fatal tail," not literal EOF.
- `died` is a newly-pinned verdict class at this HEAD
  (`bc_worlddestroy`); it lives inside the extended `iw_classify`
  docstring that replaced the −1 line — the pinned tuple still
  compares clean.
- No flake/fail events this round: all 4 battery replays passed on
  first attempt, all stderr captures 0 bytes.
