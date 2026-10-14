# Round 77 baseline report — freeze + post-commit drift (host: devin)

Seat: g2d baseline (LEAF). Immutable before-state for the r77 wave: no
tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r77-baseline/` (untracked scratch; `freeze/`
mirrors the r69–r76 procedure — `live/*/*extract*/` covers
`freeze/extract/` and `interim/extract/`, `runs/` covers the run dirs)
plus this report.

Battery scope per brief: LOVE battery (`love_battery.py`, **49 rows** at
the frozen HEAD) + pygame battery (`pygame_battery.py`, **80 rows**). The
r77 declared axis-move touches `love_battery.py` +
`love_phys_probe/main.lua` only (`tasks/g2d-author.md`: release/SIGSEGV
cells, `setCallbacks` mid-dispatch, fixture-destroy witness branch,
drain-EC legality, coroutine ladder, `setMeter` ratio — all pre-measured
by `reports/round-77/r77-scout.md`).

**STATUS: COMPLETE.** Phase 1 froze `aa4d567` and replayed both batteries
on frozen bytes (49/49 + 80/80, zero tuple drift vs 37 committed refs).
Phase 2 watched the author worktree, absorbed one intervening closeout
commit, and replayed the landed arm commit `62201e5` (75/75 + 80/80):
**49 prior LOVE rows byte-identical modulo bound-pinned `observed`
jitter, 26 `new_only` cells, 0 tuple mismatches; pygame 80/80 with 0
mismatches; the only prior raw-text drift is the declared unpinned
`main.lua:NNN`/`srcline=NNN` line-number shift.**

## Phase 1 — PRE-COMMIT freeze of the r76-closed tree

Timeline: HEAD frozen at
`aa4d567c6863736f9812f6f6d34395e478798505` ("r76 report-last: 8 seat
reports + adjudicator + LOG/SCORECARD", committed 2026-10-14 16:20:06
-0300) — `run-start.txt` 19:39:33Z, archive 19:39:33Z, extract done
19:39:43Z (0.858 s), frozen LOVE replay 19:40:04→19:40:15Z, frozen
pygame replay 19:40:27→19:40:37Z (both PASS on first attempt). **First
author worktree divergence observed 19:42:51Z** (`love_phys_probe/main.lua`
`2a7c68a1`→`2483e3f8`, `poll.log`) — i.e. the whole freeze + both frozen
replays provably predate the author's first write.

### Frozen-tree provenance — archive + extracted replay

- Frozen source: `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
  archive HEAD -o corpus/live/r77-baseline/freeze/HEAD-aa4d567c6863736f9812f6f6d34395e478798505.tar`.
- HEAD frozen: `aa4d567c6863736f9812f6f6d34395e478798505`; parent
  `c8fa3076288dd2054ac67b98a4ed699aaca678ca` (r76 folds) →
  `6ca715d` (r76 move) → `ddd455b` (r75 report-last).
- Archive: **687,943,680 bytes**, sha256
  `680b53796e6fd543351ccba567bfc1223db5800274338a2cdf74d100aa085333`.
  `git archive HEAD | sha256sum` re-run = **identical** — byte-for-byte
  deterministic archive of HEAD.
- Tar members: **44,907 non-dir entries** == `git ls-files | wc -l` =
  44,907 exactly (r76: 44,898 — delta +9 is the r76 report-last payload).
  `comm -23` (missing) = **0**, `comm -13` (extra) = **0**.
- No tracked nested snapshot dirs at HEAD (`git ls-tree -r HEAD
  --name-only | grep -cE '^corpus/live/[^/]+/(frozen|head|snapshot|base|freeze)/
  |^corpus/live/[^/]+/tree/'` → **0**).
- Extraction: `tar -xf` into `freeze/extract/`: **44,873 files +
  34 symlinks** (+4,212 dirs) = 44,907 non-dir == `git ls-files` exactly.
- Fixture digests extract == `HEAD:` blob == live tree for all 10
  checked: `love_battery.py` `471e1a4d6779f9e29d4183c9adb05bceee57de17558385de3e862f285fcfaad0`,
  `love_phys_probe/main.lua` `2a7c68a16e7c2328255f0a6ebb32d725827ef6adb1f0f29bfde9b3a695f3617f`,
  `love_phys_probe/conf.lua` `85aa6232741ea3eaa86e73d3280701d4b0a870f416bfb071558e61cc9a73576b`,
  `pygame_battery.py` `6d3fbf5f364f5bc7c9124883bd98fcf1e9513930d88a8b0dd4bbf0c77fc6fe79`,
  `pygame_probe.py` `8e15e0d21af3b56501602039fffbcd639c1c49107d44a4598706df72728d0bb5`,
  `run_battery.py` `f55c27d8f300e0f3045729c1f35743c4b7082c8ff13341bc933309eb694ce650`,
  `love_probe/main.lua` `a0afe6ca224efddf100dc8db7766ffc58e73c384f9c805c75d4a8756cfbc4576`,
  `love_probe/conf.lua` `0b45ef7310127cd4a23d72e1d56e7c825290ede5357d1cee7ebcfa706cc91ada`,
  `descendant_pipe_probe.gd` `c86bda848188cf22a4cb7e68a05c490f8c9d991632301ee50585688fef722311`,
  `stream_attribution_probe.gd` `dc0b0d5c5f44a1b4404cbe62cada0e6e53e2b33be010ea32dc72cb3892aeb286`.
- `verdicts.json["probe_dir"]` (LOVE) / `["probe"]` (pygame) on both runs
  record `…/r77-baseline/freeze/extract/corpus/fixtures/…` — replays
  provably executed frozen-HEAD bytes.
- Post-replay pristine check: `find freeze/extract -newer
  extract-done.txt` → **0 entries**.
- Pre-move surface counts: love_battery CASES=15, SPLICE_CELLS=4,
  IW_CELLS=30 (49 total — the post-r76 shape); pygame CASES=73,
  RAW_CASES=7 (80 total). Block bodies snapshotted to
  `preland-*-{CASES,SPLICE_CELLS,IW_CELLS,RAW_CASES}.txt` with sha256s:
  love CASES `a03a4559b46e3f02…` (19 lines), SPLICE_CELLS
  `d37906235135aaea…` (11), IW_CELLS `08095d0f66643ee5…` (359);
  pygame CASES `ef6c8d529a07a343…` (101), RAW_CASES
  `e28f12acf1942d81…` (19).

### Exact invocations (this generation, all receipts first-hand)

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`X=corpus/live/r77-baseline/freeze/extract`:

```
python3 -B $X/corpus/fixtures/love_battery.py \
  --runs corpus/live/r77-baseline/freeze/love-runs
  # love-runs/love-20261014T194004954785Z PASS 49/49, stderr 0 bytes, exit 0

python3 -B $X/corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r77-baseline/freeze/pygame-runs
  # pygame-runs/pygame-20261014T194027699277Z PASS 80/80, stderr 0 bytes, exit 0
```

Environment (`env.txt`): LOVE 11.5 "Mysterious Mysteries"
(`/usr/bin/love`), Godot 4.7.2.stable (`/usr/bin/godot`, unused this
round), Python 3.14.7 + pygame 2.6.1 / SDL 2.32.72,
`io.DEFAULT_BUFFER_SIZE` = **131072**, node v24.21.0 — same profile as
r70–r76.

### Before-state receipt summary (frozen `aa4d567`, pre-move)

- LOVE `verdicts.json`: `"verdict": "PASS"`, **49/49** (15 CASES +
  4 splice + **30 `iw|cell=*` rows** — 18 r74 IW + 7 r75 cells + 5 r76
  cells), `done_marker=True`, probe_exit 0, probe_elapsed 0.860 s,
  sha256 `b92d8d401f9b41dec5a7493da2cf585ad6dc8d78d893c68939c86998d2bab3b0`.
- pygame `verdicts.json`: PASS **80/80** (73 CASES + 7 RAW_CASES),
  `done_marker=True`, probe_exit 0, probe_elapsed 9.965 s, sha256
  `24bf18bd770fe5d966811e3848698064771fcea045d4335c6a9f509d5588ac37`.
- Per-cell receipt shas: `freeze/receipt-shas.txt` (129 rows: 2
  verdicts.json shas + canonical-JSON sha256 per (arm|key) row).

### Drift vs committed r73–r76 receipts — ZERO on compared tuples

`diff_receipts.py` (output `diff-output.txt`): rows compared on
(arm, key, pinned, verdict).

**LOVE — 28 references (19 × 49 rows + 10 × 44 rows + 4 × 37 rows):**

- **0 mismatches vs all 19 post-r76 (49-row) refs**: r76-baseline
  postland, r76-author r1–r4, r76-critic r1–r4, r76-reviewer r1–r2,
  r76-simplifier v0/v0b/v1/v2/v4/v6, r76-verifier r1–r2 —
  `common=49 new_only=0 old_only=0` on every one.
- **0 mismatches on all 44 common rows vs all 10 pre-r76 (44-row)
  refs** (r76-baseline frozen, r75-baseline postland,
  integrator-r75-fold, integrator-r75-verify, r75-verifier ×2,
  r75-author r1–r4); `new_only` = exactly the 5 r76-added IW keys on
  every ref (`bc_destroy2`, `bc_draindefer`, `bc_jwatch`,
  `bc_worlddestroy`, `pre_retfalse1`).
- **0 mismatches on all 37 common rows vs the 4 pre-r75 (37-row) refs**
  (r75-baseline frozen, r74-baseline postland, r74-verifier,
  r74-simplifier baseline); `new_only` = exactly the 12 post-r74 keys
  (7 r75 + 5 r76).

**pygame — 9 references (all 80 rows):** r76-baseline postland,
r76-verifier, integrator-r75-fold, integrator-r74-fold, r75-baseline
frozen + postland, r74-baseline frozen + postland, r73-baseline
postland — `common=80 new_only=0 old_only=0 mismatches=0` on every one.

**Whole-row byte compare (canonical-JSON sha256 per row) — all diffs are
declared-unpinned fields only:**

| mine vs ref | rows byte-identical | differing rows — fields |
|---|---|---|
| LOVE vs r76-baseline postland49 | 45/49 | 4 — `observed` only |
| LOVE vs r76-baseline frozen44 | 39/44 | 5 — `observed` only |
| LOVE vs integrator-r75-fold44 | 37/44 | 7 — `observed` only |
| LOVE vs r75-baseline postland44 | 13/44 | 31 — `observed` (6) + `rc` (25) |
| pygame vs r76-baseline postland80 | 62/80 | 18 — `observed` only |
| pygame vs r75-baseline frozen80 | 62/80 | 18 — `observed` only |

`observed` is the bound-pinned jitter field (excluded by construction).
The 25 `rc` differences are a **schema delta, not drift**: the persisted
`rc` field on the 25 IW rows was introduced by the r75 folds commit
`be79ad1`, so pre-fold refs (`r75-baseline postland`, r74 refs) lack the
key while post-fold refs (integrator-r75-fold onward) carry `rc=0` — and
every post-fold ref shows 0 `rc` differences against this freeze. Zero
diffs in `pinned`/`verdict`/`case`/`reasons` on any prior row.

The frozen `aa4d567` tree is a verified-stable pre-move surface.

## Phase 2 — POST-COMMIT watch + landed-tree re-verification

Watcher `poll-commit.sh` (15 s cadence, `poll.log`), armed 19:39:33Z,
fires on HEAD leaving `aa4d567` and logs the first worktree divergence of
`love_battery.py` / `love_phys_probe/{main,conf}.lua` /
`pygame_battery.py` (pre-move shas
`471e1a4d`/`2a7c68a1`/`85aa6232`/`6d3fbf5f`).

### Timeline

| event | UTC |
|---|---|
| freeze + extract + both frozen replays | 19:39:33–19:40:37Z |
| first author worktree divergence (`main.lua` `2a7c68a1`→`2483e3f8`) | 19:42:51Z |
| **intervening commit** `94356ce` "r76 closeout corrections (r77-scribe audit)" | 19:45:36Z |
| interim control replay (94356ce extract) 49/49 + 80/80 | 19:46:05–19:46:26Z |
| worktree churn: `love_battery.py` 4bd71c36→1e3e9f46, `main.lua` 3f130f41 | 19:46:15–19:48:00Z |
| **author arm commit** `62201e5` | 19:53:30Z |
| postland LOVE replay 75/75 (rep 1) | 19:55:31–19:55:46Z |
| postland pygame replay 80/80 | 19:55:46–19:55:56Z |
| postland LOVE replay 75/75 (rep 2, rep-stability control) | 19:56:20–19:56:35Z |

### Intervening closeout commit `94356ce` — absorbed, behavior-neutral

`94356ce` (parent `aa4d567`) touches `LOG.md`,
`corpus/fixtures/love_battery.py` (+4/−2, **comment-only**:
`World.cpp:283-299` → `World.cpp:289-294 joint loop; 283-287 is the
fixture loop` inside the `bc_jwatch` comment block),
`reports/round-76/r76-boundary.md`, `reports/round-77/r77-scribe.md`.
Because it changed the fixture bytes between my freeze and the arm
commit, a **control replay** was taken from a `git archive 94356ce`
extract (`interim/`, tar sha256
`32efbc5e2365c4dd41b49e0f66d97094e489a1bafa6fb994bb6f424d3f2906cb`;
`love_battery.py` `4bd71c36…`, `main.lua` unchanged `2a7c68a1…`):

- interim LOVE 49/49 PASS (`interim/love-runs/love-20261014T194605733864Z`),
  pygame 80/80 PASS (`interim/pygame-runs/pygame-20261014T194616231406Z`),
  both stderr 0 bytes.
- vs frozen (`interim-diff.txt`): LOVE 45/49 byte-identical, **4 rows
  differ in `observed` only, 0 tuple mismatches**; pygame 63/80
  byte-identical, **17 rows `observed`-only, 0 tuple mismatches** — the
  closeout edit is behaviour-neutral, so any Phase-2 prior-row delta is
  attributable to the arm.

### Author arm commit `62201e5` — shape

- `62201e5 r77 work: release/swap/fixture/drain-EC/coroutine/meter lattice`,
  parent `94356ce4f40e6772a0df6fe0715da3f7160cd9d2`, committer
  2026-10-14 16:53:29 -0300.
- Fixture scope: `corpus/fixtures/love_battery.py` **+631 / −0**,
  `corpus/fixtures/love_phys_probe/main.lua` **+422 / −0**
  (`git diff --numstat 94356ce 62201e5`) — **pure insertion, zero
  deletions**. Also carries `reports/round-77/{gd-scout,r77-author,r77-boundary}.md`.
- Worktree fixture cleanliness at replay time (19:55:31Z): all four arm
  files CLEAN vs `HEAD:` blobs
  (`love_battery.py` `1e3e9f46…`, `main.lua` `3f130f41…`,
  `conf.lua` `85aa6232…`, `pygame_battery.py` `6d3fbf5f…`) — the postland
  replays provably executed the committed bytes.
- Line growth: `love_battery.py` 869→1502 lines, `main.lua` 466→888
  (this is what shifts the declared-unpinned line tokens below).
- Sibling fixtures byte-stable `aa4d567`→`62201e5`: `pygame_battery.py`,
  `pygame_probe.py`, `love_probe/{main,conf}.lua`,
  `love_phys_probe/conf.lua`, `run_battery.py` — all STABLE.

### Post-commit battery re-runs on live `62201e5`

cwd = live repo (fixtures at `corpus/fixtures/` — `probe_dir`/`probe`
fields record the live path), runs → `corpus/live/r77-baseline/postland/`:

```
python3 -B corpus/fixtures/love_battery.py \
  --runs corpus/live/r77-baseline/postland/love-runs
  # love-20261014T195531531710Z PASS 75/75, stderr 0 bytes, exit 0
python3 -B corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r77-baseline/postland/pygame-runs
  # pygame-20261014T195546545964Z PASS 80/80, stderr 0 bytes, exit 0
python3 -B corpus/fixtures/love_battery.py \
  --runs corpus/live/r77-baseline/postland/love-runs2   # rep-2 control
  # love-20261014T195620554096Z PASS 75/75, stderr 0 bytes, exit 0
```

- **LOVE 75/75 PASS** (49 prior + 26 new), verdicts.json sha256
  `28a88d608cd9ad50a3c30b7e527fe7ca826e9c88ea55e4e630b37b6ad22d897f`.
- **pygame 80/80 PASS**, verdicts.json sha256
  `2cf8f06093b0e73a31cb6ba1d87bba0a41afefab4478f930626fcdf57c5aeb5a`.

### Prior rows — byte-identity and drift attribution

- **Receipt tuples**: `postland-love vs MY FROZEN: common=49
  new_only=26 old_only=0 mismatches=0`; the same tuple result holds vs
  **all 19 committed 49-row refs** (r76-baseline postland, r76-author
  r1–r4, r76-critic r1–r4, r76-reviewer r1–r2, r76-simplifier
  v0/v0b/v1/v2/v4/v6, r76-verifier r1–r2) — `common=49 new_only=26
  mismatches=0` on every one. pygame: `common=80 new_only=0 old_only=0
  mismatches=0` vs my frozen and vs all 9 committed 80-row refs.
- **Prior-row order preserved**: the 49 prior `(arm, key)` rows appear in
  the postland receipt in exactly the frozen order (`True`), with the 26
  new rows occupying receipt indices 44–74.
- **Whole-row bytes** (`byte-drift.txt`): LOVE **43/49 byte-identical**;
  the 6 differing rows differ in **`observed` ONLY** (bound-pinned
  jitter: `dtcadence|dt_max_ms` 1.092↔1.090, `dtcadence|dt_mean_ms`,
  `popen|close_wait_ms`, `popen|l1_wait_ms`, `popen|l2_wait_ms`,
  `popen|total_ms`) — 0 rows with any other diff. pygame **62/80
  byte-identical**, 18 rows `observed`-only, 0 other diffs.
- **Raw per-cell captures** (`raw-drift.txt`; the verdicts rows carry only
  classified values, so this is where line-number text lives) — 35 prior
  cells compared:
  - 25 byte-identical,
  - **5 identical modulo declared-unpinned line tokens**
    (`iw-bc_draindefer` `srcline=230`→`299`; `iw-bc_setpos_wp`
    `srcline=181`→`250`; `iw-bc_worlddestroy` `main.lua:441`→`861`;
    `iw-bc_newbody_unp` `129/315/339/401`→`198/497/546/810`;
    `iw-bc_setpos_unp` `125/315/339/401`→`194/497/546/810`),
  - 5 numeric-jitter-only (`probe.stdout.txt` + the 4 `splice-*.stdout.txt`
    raw timing arms — `dt_*_ms`/`popen` numbers by construction),
  - **0 structural diffs**; 26 new-only cells, 0 old-only.
- **Block bytes** (`block-diff.txt`, SequenceMatcher on the preland
  snapshots): love `CASES` (19 lines) and `SPLICE_CELLS` (11) and pygame
  `CASES` (101) / `RAW_CASES` (19) are **byte-identical**; love
  `IW_CELLS` 359→770 lines shows **2 pure insert ops (409 lines)** plus
  **one 4-line replace — which is exactly the `94356ce` closeout comment
  correction, not the arm** (the arm's own file delta is +631/−0 and
  +422/−0). Prior-row subsequence survives; the insertion-only claim
  holds modulo the separately-committed comment fix.

### New cells — `new_only` = exactly the 26 arm cells, all PASS

Classes as landed (postland receipt, LOVE 11.5 this host; `rc` persisted
per the r76 schema):

| class | count | cells |
|---|---|---|
| `corrupt` (rc −11, SIGSEGV) | 5 | `bc_worldrelease`, `pre_worldrelease`, `post_worldrelease`, `ec_worldrelease`, `drain_worldrelease` |
| `died` (rc 1) | 3 | `bc_coyield`, `cowrap_update_yield`, `ext_worldrelease` |
| `fatal` (rc 1) | 1 | `bc_cowrap_unp` |
| `swapped` (rc 0) | 4 | `bc_setcallbacks`, `pre_setcallbacks`, `multi_setcallbacks`, `bc_setcallbacks_back` |
| `muted` (rc 0) | 1 | `bc_setcallbacks_nil` |
| `deferred` (rc 0) | 3 | `bc_fixture_destroy`, `bc_fixture_destroy2`, `drain_order_joint` |
| `applied` (rc 0) | 4 | `ext_fixture_destroy`, `drain_setpos_b2`, `bc_meter`, `pre_meter` |
| `immediate` (rc 0) | 1 | `drain_queue_b2` |
| `drain_abort` (rc 0) | 1 | `wp_drain_throw` |
| `refused` (rc 0) | 1 | `bc_cowrap_setpos` |
| `yield_abort` (rc 0) | 2 | `co_update_yield`, `wp_coyield` |

- `rc` distribution over the 26 new rows: 17× `0`, 4× `1`, 5× `-11`.
- **Fatal/corrupt tail respected**: the last 8 receipt rows are
  `cowrap_update_yield`(died), `ext_worldrelease`(died),
  `bc_cowrap_unp`(fatal), then the five `corrupt` rc=−11 rows last.
- Partial-capture shape confirmed for the corrupt rows: stdout ends with
  the in-callback witness and no `CELL_DONE`
  (`bc_worldrelease`: `rel_call ok=true err=true` → `rel_alive marker=1`
  → `rel_post marker=1`, then death; `drain_worldrelease`:
  `drainrel call_ok=true call_ret=true` → `drainrel alive=1`), stderr
  0 bytes on every new cell.

### Rep-stability control (rep 1 vs rep 2, `rep2-diff.txt`)

- Verdicts: 75 rows compared, **70 byte-identical, 5 `observed`-only, 0
  other diffs** → every one of the 26 new cells is byte-stable across
  reps, including the five rc=−11 corrupt rows.
- Raw captures: 61 cells, **56 byte-identical, 5 numeric-jitter-only, 0
  structural, 0 new/old-only** — the new cells' witness text is
  rep-stable verbatim.
- rep-2 vs frozen prior 49: 44/49 byte-identical, 5 `observed`-only, 0
  other — the prior-row claim is not a single-rep artifact.

## Artifact inventory (`corpus/live/r77-baseline/`)

- `freeze/HEAD-aa4d567….tar` — `git archive HEAD`, 687,943,680 B,
  sha256 `680b5379…`, deterministic re-run match.
- `freeze/extract/` — populated frozen tree (44,873 files + 34
  symlinks, comm-clean vs `git ls-files`); replay surface.
- `freeze/love-runs/love-20261014T194004954785Z/` — 49/49 ·
  `freeze/pygame-runs/pygame-20261014T194027699277Z/` — 80/80.
- `interim/HEAD-94356ce….tar` + `interim/extract/` +
  `interim/love-runs/love-20261014T194605733864Z/` (49/49) +
  `interim/pygame-runs/pygame-20261014T194616231406Z/` (80/80) — the
  closeout-commit control surface.
- `postland/love-runs/love-20261014T195531531710Z/` — 75/75 ·
  `postland/love-runs2/love-20261014T195620554096Z/` — 75/75 (rep 2) ·
  `postland/pygame-runs/pygame-20261014T195546545964Z/` — 80/80
  (committed-tree re-verify on live `62201e5`).
- `freeze/receipt-shas.txt` (129 rows: 49 + 80) and
  `postland/receipt-shas.txt` (155 rows: 75 + 80) — per-cell receipt sha
  tables.
- `diff_receipts.py` + `diff-output.txt` (frozen + postland sections vs
  37 refs); `postland_blocks.py` + `block-diff.txt`;
  `byte_drift.py` + `byte-drift.txt` + `rep2-diff.txt` +
  `interim-diff.txt`; `raw_receipts_drift.py` + `raw-drift.txt` +
  `raw-drift-rep2.txt`; `phase2.sh` + `phase2-provenance.txt`;
  `preland-*.txt` frozen block references.
- stdout/stderr pairs: `love-battery`, `pygame-battery`,
  `interim-love`, `interim-pygame`, `love-postland`, `pygame-postland`,
  `love-postland2` (all `.stderr` siblings 0 bytes).
- `freeze-head.txt`, `run-start.txt`, `extract-done.txt`,
  `extract-time.txt`, `interim/extract-done.txt`, `env.txt`;
  `poll-commit.sh` + `poll-commit2.sh` + `poll.log` watchers.

## Process hygiene

No tracked file edited by this seat; no commit, no push. `git status`
shows only pre-existing sibling residue (`M corpus/live/r72-simplifier/*`,
untracked `r7*/integrator-r7*` scratch, `corpus/live/gd-scout/`) plus this
seat's own untracked `corpus/live/r77-baseline/` and
`reports/round-77/r77-baseline.md`. All four batteries were launched from
either the frozen/interim extracts or the live tree with `--runs` inside
this scratch root; both watchers self-exited on commit detection; `pgrep`
after the runs shows no battery or watcher process left from this seat.
No `lsp` device is exposed on this host for `.py`/`.lua` (r77-scout §0
disclosure) — this seat performs no symbol-level edit, so no
language-server path applies. No subagent was dispatched: the baseline's
claims are hash- and receipt-verifiable first-hand, and an advisory probe
would add no independent axis.

## UNKNOWNs / caveats

- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, `seed`, receipt shas, bound-pinned `observed`) are
  excluded from tuple comparison by construction; volatile-embedded rep
  jitter is a known class since r68. The raw-text `splice-*`/`probe`
  timing arms jitter numerically every run by construction — that is why
  the raw comparator reports them in a separate numeric bucket.
- Byte-identity is a **this-host** property (LOVE 11.5, LuaJIT
  2.1.1788460057, Python 3.14.7 + pygame 2.6.1/SDL 2.32.72); no claim
  about other builds or the g3d arm.
- The declared-unpinned line-token drift is *positional, not semantic*:
  the 5 prior cells' raw captures differ only in `main.lua:NNN` /
  `srcline=NNN` values, and the arm grew `main.lua` by 422 lines. Nothing
  in this report asserts those line numbers are stable across future
  insertions — they are layout-coupled by construction and must stay
  unpinned.
- The intervening `94356ce` closeout commit means `62201e5`'s parent is
  not the frozen `aa4d567`; the frozen surface is still a provably
  pre-move referent (frozen 19:39–19:40Z, first author write 19:42:51Z,
  closeout 19:45:36Z), and the control replay isolates the closeout
  comment edit as behaviour-neutral.
- `new_only` classes are reported as the battery's own landed
  classifications (`iw_classify`), not as independent judgments; the
  class partition itself is the author/verifier surface, not this seat's
  call.
