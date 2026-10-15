# Round 78 baseline report — freeze + post-commit drift (host: devin)

Seat: g2d baseline (LEAF). Immutable before-state for the r78 wave: no tracked
fixture/runner edit, no commit, no LOG/SCORECARD write. All artifacts under
`corpus/live/r78-baseline/` (untracked scratch) plus this report.

Battery scope per brief: LOVE battery (`love_battery.py`, **75 rows** at the
frozen HEAD) + pygame battery (`pygame_battery.py`, **80 rows**). The r78
declared axis-move touches `love_battery.py` + `love_phys_probe/main.lua` only
(`tasks/g2d-r78-author.md`: nested lock-clear, inner-drain ownership, depth-2
drain-EC partition, contacting-destroy escape, zombie contact handles,
livelock/convergence — all pre-measured by `reports/round-78/r78-scout.md`).

**STATUS: COMPLETE.** Phase 1 froze `d4aaa958` at 20:52:59Z — *the r77
report-last commit; the r78 author's first worktree write was observed at
20:56:08Z, so the freeze and both frozen replays provably predate it* — and
replayed both batteries on frozen bytes (75/75 + 80/80, zero tuple drift vs
24 clean 75-row refs, 21 49-row refs, 14 pygame refs). Phase 2 fired on the
landed arm commit `1a03b7a` ("r78 work: nested-update damage surface — 17
cells", parent `d4aaa958`) and replayed both batteries on committed bytes
(**92/92 + 80/80**, both reps): **75 prior LOVE rows 0 tuple mismatches,
69/75 byte-identical (6 `observed`-only), 17 declared inserted rows, 0 other
deltas; pygame 80/80 with 0 mismatches.** One prior raw capture shows a
line-order permutation not covered by the author's declaration — diagnosed as
a nondeterministic stream-flush race (§Phase 2, "the one delta the author did
not declare").

## Phase 1 — PRE-COMMIT freeze at current HEAD

Timeline (all UTC): `run-start.txt` **20:52:59Z** → HEAD recorded
**20:52:59Z** → `git archive HEAD` 20:52:59–20:53:0x → extract done
**20:53:08Z** → frozen LOVE replay **20:53:30→20:53:48Z** → frozen pygame
replay **20:53:50→20:54:00Z** (both PASS first attempt) → **first author
worktree divergence 20:56:08Z** (`love_phys_probe/main.lua` `a186053b`→
`ca10824c`, `poll.log`) → arm commit `1a03b7a` 21:11:00Z (committer stamp).

Frozen HEAD: `d4aaa9588f75aee8259e397226433fb64fbaf48b`
("r77 report-last: adjudicator ADMIT-corr + ledger", committed
2026-10-14 17:09:44 -0300). Parent chain: `d48e0fd` (r77 folds) → `62201e5`
(r77 move) → `94356ce` → `aa4d567` (r76 report-last). **The r78 author was
landing concurrently; this is the HEAD at freeze time and the author had not
yet written to either arm file** (both matched their HEAD blobs at 20:52:59Z,
20:54:46Z, and until 20:56:08Z).

### Frozen-tree provenance — archive + extracted replay

- Frozen source: `git archive HEAD -o
  corpus/live/r78-baseline/freeze/HEAD-d4aaa958….tar`.
- Archive: **688,281,600 bytes**, sha256
  `342710aa4f2842fe74c6249374ba6fa7091b4bbf7b83596844a6394df988a952`.
  `git archive HEAD | sha256sum` re-run = **identical** — deterministic
  archive of HEAD.
- Tar members: **44,920 non-dir entries** == `git ls-files | wc -l` = 44,920
  exactly (r77: 44,907; delta +13 is the r77 report-last payload).
  `comm -23` (missing) = **0**, `comm -13` (extra) = **0**.
- No tracked nested snapshot dirs at HEAD (`git ls-tree -r HEAD --name-only |
  grep -cE '^corpus/live/[^/]+/(frozen|head|snapshot|base|freeze)/|^corpus/
  live/[^/]+/tree/'` → **0**).
- Extraction: `tar -xf` into `freeze/extract/`: **44,886 files + 34
  symlinks** = 44,920 non-dir == `git ls-files` exactly; `extract-done.txt`
  20:53:08Z.
- Fixture digests extract == `HEAD:` blob == live tree for all 10 checked:
  `love_battery.py` `82986759243fff639696095c61933eab135b8f325f8d46223e4fc86c8540221b`,
  `love_phys_probe/main.lua` `a186053b124dd9c3191381948dedf26138979f1d1901481057812cdfc4802925`,
  `love_phys_probe/conf.lua` `85aa6232741ea3eaa86e73d3280701d4b0a870f416bfb071558e61cc9a73576b`,
  `pygame_battery.py` `6d3fbf5f364f5bc7c9124883bd98fcf1e9513930d88a8b0dd4bbf0c77fc6fe79`,
  `pygame_probe.py` `8e15e0d21af3b56501602039fffbcd639c1c49107d44a4598706df72728d0bb5`,
  `run_battery.py` `f55c27d8f300e0f3045729c1f35743c4b7082c8ff13341bc933309eb694ce650`,
  `love_probe/main.lua` `a0afe6ca224efddf100dc8db7766ffc58e73c384f9c805c75d4a8756cfbc4576`,
  `love_probe/conf.lua` `0b45ef7310127cd4a23d72e1d56e7c825290ede5357d1cee7ebcfa706cc91ada`,
  `descendant_pipe_probe.gd` `c86bda848188cf22a4cb7e68a05c490f8c9d991632301ee50585688fef722311`,
  `stream_attribution_probe.gd` `dc0b0d5c5f44a1b4404cbe62cada0e6e53e2b33be010ea32dc72cb3892aeb286`.
- **Full fixture seed** ("hash-seed all fixtures"): 61-entry sha256 manifest
  of every file under `corpus/fixtures/` (excluding `__pycache__`) —
  `freeze/fixture-manifest-frozen.txt` vs `freeze/fixture-manifest-live.txt`
  → **byte-identical (61/61, `diff` empty)** at freeze time.
- `verdicts.json["probe_dir"]` (LOVE) / `["probe"]` (pygame) on both runs
  record `…/r78-baseline/freeze/extract/corpus/fixtures/…` — replays
  provably executed frozen-HEAD bytes.
- Post-replay pristine check: `find freeze/extract -newer extract-done.txt`
  → **0 entries**.
- Pre-move surface counts: love CASES=15, SPLICE_CELLS=4, IW_CELLS=56 (75
  total — the post-r77 shape); pygame CASES=73, RAW_CASES=7 (80 total).
  Block bodies snapshotted to `preland-*-{CASES,SPLICE_CELLS,IW_CELLS,
  RAW_CASES}.txt` (`preland-snapshot.log`): love CASES `a03a4559b46e3f02…`
  (19 lines), SPLICE_CELLS `d37906235135aaea…` (11), IW_CELLS
  `0f146fffa48535e4…` (736 lines); pygame CASES `ef6c8d529a07a343…` (101),
  RAW_CASES `e28f12acf1942d81…` (19).

### Exact invocations (this generation, all receipts first-hand)

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`X=corpus/live/r78-baseline/freeze/extract`:

```
python3 -B $X/corpus/fixtures/love_battery.py \
  --runs corpus/live/r78-baseline/freeze/love-runs
  # love-runs/love-20261014T205330614648Z PASS 75/75, stderr 0 bytes, exit 0

python3 -B $X/corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r78-baseline/freeze/pygame-runs
  # pygame-runs/pygame-20261014T205350160537Z PASS 80/80, stderr 0 bytes, exit 0
```

Environment (`env.txt`): LOVE 11.5 "Mysterious Mysteries" (`/usr/bin/love`),
Godot 4.7.2.stable (`/usr/bin/godot`, unused this round), Python 3.14.7 +
pygame 2.6.1 / SDL 2.32.72, `io.DEFAULT_BUFFER_SIZE` = **131072**,
node v24.21.0, Linux 7.2.3-arch1-3 — same profile as r70–r77.

### Before-state receipt summary (frozen `d4aaa958`, pre-move)

- LOVE `verdicts.json`: `"verdict": "PASS"`, **75/75** (15 CASES +
  4 splice + 56 `iw|cell=*` rows — 30 r74–r76 + 26 r77), `done_marker=True`,
  probe_exit 0, `probe_elapsed_s` 1.295, sha256
  `ed3829108487aba8fd16f35a626bdf60220b319564edb240112cd0fb75d0e4c1`.
- pygame `verdicts.json`: PASS **80/80** (73 CASES + 7 RAW_CASES),
  `done_marker=True`, probe_exit 0, `probe_elapsed_s` ~10.0, sha256
  `ae0fb185280903457151d06781af7e1e9c072af9db4a63be18bf032cc10e2025`.
- Per-cell receipt shas: `freeze/receipt-shas.txt` (155 rows: 2 verdicts.json
  shas + canonical-JSON sha256 per (arm|key) row) — the frozen reference set
  the brief asks for.

### Drift vs committed r73–r77 receipts — ZERO on compared tuples

`diff_receipts.py` (output `diff-output.txt`); rows compared on
(arm, key, pinned, verdict).

**LOVE — 24 clean 75-row refs + 21 pre-r77 refs:**

- **0 mismatches vs 24 of the 25 75-row refs**: r77-baseline postland rep1 +
  rep2, `runs/{194754,194819,194837,195013,195441,195456,195511,195526,
  195600,200810}`, r77-simplifier {baseline,dedup,fold a,fold b,fold2 a,
  fold2 b,obs3,pins a,pins b,probe}, r77-verifier r1 + r2 —
  `common=75 new_only=0 old_only=0` on every one.
  The 25th (`runs/love-20261014T194717707844Z`) is the **r77 author's
  pre-fix intermediate** — `common=75, mismatches=3` on rows the r77 wave
  itself declared FAIL at that revision (`bc_cowrap_setpos`,
  `bc_setcallbacks_back`, `drain_worldrelease`); it is flagged in the ref
  table as an incident, not a clean reference, and is not counted as drift.
- **0 mismatches on all 49 common rows vs all 21 pre-r77 (49-row) refs**
  (r77-baseline frozen + interim, r76-baseline postland, r76-author r1–r4,
  r76-critic r1–r4, r76-reviewer r1–r2, r76-simplifier v0/v0b/v1/v2/v4/v6,
  r76-verifier r1–r2); `new_only` = **exactly the 26 r77-added IW keys** on
  every ref.

**pygame — 14 refs (all 80 rows):** r77-baseline postland + interim + frozen,
r77-verifier, r76-verifier, r76-baseline postland + frozen,
integrator-r75-fold, integrator-r74-fold, r75-baseline frozen + postland,
r74-baseline frozen + postland, r73-baseline postland —
`common=80 new_only=0 old_only=0 mismatches=0` on every one.

**Whole-row byte compare (canonical-JSON sha256 per row) — all diffs are
declared-unpinned fields only:**

| mine vs ref | rows byte-identical | differing rows — fields |
|---|---|---|
| LOVE vs r77-baseline postland rep1 | 68/75 | 7 — `observed` only |
| LOVE vs r77-baseline frozen49 | 42/49 | 7 — `observed` only |
| pygame vs r77-baseline postland80 | 62/80 | 18 — `observed` only |

`observed` is the bound-pinned jitter field (excluded by construction).
Raw prior-cell captures (frozen vs r77-baseline postland, `raw-drift.txt`
Phase-1 section): 61 stdout cells → **56 byte-identical, 5 numeric-jitter-only,
0 structural**; 57 stderr cells → **57/57 byte-identical**.

The frozen `d4aaa958` tree is a verified-stable pre-move surface.

### Pre-existing dirty state at freeze — recorded, NOT cleaned

`pre-existing-dirty-state.txt` (captured 20:55:21Z, verbatim in the artifact):

- **2 modified tracked files, neither touched by this seat**:
  `corpus/live/r72-simplifier/snapshots/log.txt` (+5) and
  `corpus/live/r72-simplifier/watch.log` (+2) — `git diff --stat` = 2 files,
  7 insertions. Left exactly as found (brief: do NOT clean it yourself).
- **55 untracked entries**: `corpus/fixtures/__pycache__/love_battery.cpython-314.pyc`,
  prior-round scratch (`corpus/live/r7{2,3,4,5,6,7}-*/`,
  `integrator-r7{4,5}-*`, `corpus/live/gd-scout/`), the r78 scout/scribe/baseline
  scratch dirs, and 4 `corpus/live/r72-simplifier/snapshots/*` dirs.
- No tracked file was modified by this seat; `corpus/fixtures/` had **zero**
  tracked modifications at freeze time.

## Phase 2 — POST-COMMIT watch + landed-tree re-verification

Watchers: `poll-commit.sh` (15 s cadence, `poll.log`), armed 20:53:23Z, fires
on HEAD leaving `d4aaa958` and logs the first worktree divergence of the arm
files; `phase2-watch.sh` (15 s cadence, `phase2-watch.log`) fires only on a
commit that changes `corpus/fixtures/love_battery.py` **and** a worktree
CLEAN-vs-HEAD for two consecutive polls (so it cannot replay mid-write).

### Timeline

| event | UTC |
|---|---|
| freeze + extract + both frozen replays | 20:52:59–20:54:00Z |
| first author worktree divergence (`main.lua` `a186053b`→`ca10824c`) | 20:56:08Z |
| arm commit `1a03b7a` committer stamp | 21:11:00Z |
| watcher sees HEAD≠`d4aaa958`, worktree CLEAN ×2 | 21:11:10Z / 21:11:25Z |
| postland LOVE replay 92/92 (rep 1) | 21:11:25→21:11:45Z |
| postland pygame replay 80/80 (rep 1) | 21:11:45→21:11:56Z |
| postland LOVE replay 92/92 (rep 2, rep-stability control) | 21:11:56→21:12:15Z |
| postland pygame replay 80/80 (rep 2) | 21:12:15→21:12:25Z |
| phase2 analysis complete | 21:12:26Z |

### Landed commit `1a03b7a` — shape

- `1a03b7a61141337206c118f071777c71752d7f7c` "r78 work: nested-update damage
  surface — 17 cells", parent `d4aaa9588f75aee8259e397226433fb64fbaf48b`,
  committer 2026-10-14 18:11:00 -0300.
- Fixture scope: `corpus/fixtures/love_battery.py` **+560 / −5**,
  `corpus/fixtures/love_phys_probe/main.lua` **+479 / −0**
  (`git diff --numstat d4aaa958 1a03b7a -- corpus/fixtures/`); also carries
  `reports/round-78/r78-author.md`. Commit identity is `ci <ci@local>` for
  both author and committer (the integrator landed the author's worktree
  bytes; the author seat's own report records "no git mutation") — recorded
  as provenance, not judged here.
- Worktree fixture cleanliness at replay time (21:11:25Z): all four files
  CLEAN vs `HEAD:` blobs (`love_battery.py` `ea70c42c…`, `main.lua`
  `75eb18d2…`, `conf.lua` `85aa6232…`, `pygame_battery.py` `6d3fbf5f…`) —
  the postland replays provably executed the committed bytes.
- Sibling fixtures byte-stable `d4aaa958`→`1a03b7a`: `pygame_battery.py`,
  `pygame_probe.py`, `run_battery.py`, `love_probe/{main,conf}.lua`,
  `love_phys_probe/conf.lua` — all STABLE.
- Line growth: `love_battery.py` 1040-line IW_CELLS block (736→1040),
  `main.lua` +479 lines (this is what shifts the declared-unpinned line
  tokens below).

### Post-commit battery re-runs on live `1a03b7a`

cwd = live repo (fixtures at `corpus/fixtures/`), runs →
`corpus/live/r78-baseline/postland/`:

```
python3 -B corpus/fixtures/love_battery.py \
  --runs corpus/live/r78-baseline/postland/love-runs
  # love-20261014T211125990828Z PASS 92/92, stderr 0 bytes, exit 0
python3 -B corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r78-baseline/postland/pygame-runs
  # pygame-20261014T211145943377Z PASS 80/80, stderr 0 bytes, exit 0
python3 -B corpus/fixtures/love_battery.py \
  --runs corpus/live/r78-baseline/postland/love-runs2      # rep-2 control
  # love-20261014T211156070014Z PASS 92/92, stderr 0 bytes, exit 0
python3 -B corpus/fixtures/pygame_battery.py \
  --runs corpus/live/r78-baseline/postland/pygame-runs2    # rep-2 control
  # pygame-20261014T211215546763Z PASS 80/80, stderr 0 bytes, exit 0
```

- **LOVE 92/92 PASS** (75 prior + 17 new), rep1 verdicts.json sha256
  `2523eda873c85f8a84ea91b93978de618e9621c5308c240e5cc4a2e605e7d025`,
  rep2 `aeaa8bf7eb23599408972e3aac72bfeb5ab66dde0238f59bc704c26397ec7b46`.
- **pygame 80/80 PASS**, rep1 sha256
  `869c312ddd319250117c7ca2b657e8832653017aa8e35f1f89b34984832f469d`,
  rep2 `4ad3c19f394bc7fbd4ee1a4ebe6e3f8007ee01c7ba36a49ba73894975917d521`.
- `probe_dir`/`probe` fields on all four postland runs record the **live**
  `corpus/fixtures/…` path (committed bytes), `done_marker=True`,
  `probe_exit=0`.

### Prior rows — positions, tuples, bytes

`prior_row_diff.py` (outputs `prior-row-diff-love.txt`,
`prior-row-diff-pygame.txt`); brief requirement = "all 75 prior rows at
identical positions (stdout+stderr)".

**Positions.** All **75 prior `(arm,key)` rows are present, none removed, and
their relative order is preserved** (`subsequence=True` on both reps).
Prior rows at frozen indices **0–60 sit at identical postland indices**; the
14 process-death-tail rows (frozen 61–74: `bc_destroy_unp` … `drain_worldrelease`)
shift **+14** to postland indices 75–89. The 17 inserted rows occupy **three
contiguous runs: [61–74] (14 rows), [84] (1), [90–91] (2)** — i.e. the
declared shape "17 rows appended ahead of the process-death tail, the three
r78 death rows joining the tail" (`prior-row-diff-love.txt`,
`position-map.txt`).

**Tuples.** `rows compared: 75  tuple_mismatches=0` — **both reps** — vs the
frozen reference and vs every committed 75-row ref (`diff-output.txt`,
postland section: `common=75 new_only=17 old_only=0 mismatches=0` on all 24
clean refs).

**Whole-row bytes.** rep1: **69/75 byte-identical, 6 differing in `observed`
ONLY, 0 rows with any other diff**; rep2: identical counts (6 `observed`-only).
The 6 are the bound-pinned jitter fields
(`dtcadence|dt_max_ms`, `dtcadence|dt_mean_ms`, `popen|{close,l1,l2,total}_ms`).

**Raw prior-cell captures — stdout.** 61 prior cells compared (1 probe +
4 splice + 56 iw):
- **45 byte-identical**;
- **11 line-token-only** — and they are **exactly the 11 cells the author
  declared** (`r78-author.md` §4: `bc_cowrap_unp`, `bc_coyield`,
  `bc_draindefer`, `bc_newbody_unp`, `bc_setpos_unp`, `bc_setpos_wp`,
  `bc_worlddestroy`, `cowrap_update_yield`, `ext_worldrelease`, `wp_coyield`,
  `wp_drain_throw`) — `main.lua:NNN` / `srcline=NNN` tokens only, 11/11 name
  match, **no extra token-only cell**;
- **4 numeric-jitter-only** (`probe.stdout.txt` + 3 `splice-*.stdout.txt`
  raw timing arms — `dt_*_ms`/`popen` numbers by construction);
- **1 line-order-only** — `splice-80-50` (see below);
- **0 content-structural diffs**; 17 new-only cells; 0 old-only.

**Raw prior-cell captures — stderr.** 57 prior cells compared →
**57/57 byte-identical** (both reps); 17 new-only stderr cells; 0 old-only.

**The one delta the author did not declare.** `splice-80-50.stdout.txt` is
**the same 8 lines / the same 476 bytes in both trees**, but the trailing
`ERROR: LOVE_MIDLINE forged splice` line occupies a different position:
frozen has it **last** (`…expected signature / LOVE-ARM splice / LOVE_PROBE_DONE / ERROR`),
postland rep1 has it **third-from-last** (`…expected signature / ERROR / LOVE-ARM splice / LOVE_PROBE_DONE`).
Line-multiset equality confirmed (`line-order-check.txt`), so this is an
ordering permutation, not content drift — and it is **nondeterministic on this
host**: rep2 reproduces the frozen order, while the author's own four
final-revision runs split (run `…T210544087564Z` shows the permuted order; the
other three show the frozen order). It is a stream-flush race between the
probe's tail writes and the harness's ERROR annotation. The author's
`drift_audit.py` scope is "prior iw receipts" (112), so this splice-cell
ordering class sits **outside their declared set** — named here as a measured,
undeclared-by-scope delta, classified as ordering jitter with the rep-2 +
author-run counter-evidence, **not** semantic drift.

**Block bytes** (`block-diff.txt`, SequenceMatcher on the preland snapshots):
love `CASES` (19 lines) and `SPLICE_CELLS` (11) are **byte-identical**; pygame
`CASES` (101) / `RAW_CASES` (19) **byte-identical**; love `IW_CELLS` 736→1040
lines shows **4 equal ops (736 lines) + 3 pure insert ops (304 lines), zero
delete/replace** → `prior_rows_byte_identical(subsequence)=True`. The
insertion-only claim holds at the block level.

### New cells — `new_only` = exactly the 17 declared rows, all PASS

`new-rows.txt`, postland receipt (LOVE 11.5 this host; `rc` persisted):

| class (`pinned`) | count | rc | cells |
|---|---|---|---|
| `nested_lockclear` | 3 | 0 | `n_baseline`, `n_inner_cb`, `n_depth2_seq` |
| `inner_drain` | 1 | 0 | `n_queue_inner_drain` |
| `dispatch_escape` | 4 | 0×3, 1×1 | `n_destroy_contacting_wp`, `n_destroy_ground_wp`, `n_destroy_fx_wp`; `n_destroy_contacting` (rc=1) |
| `refused` | 1 | 0 | `n_depth2_fxdrain` |
| `contact_invalidated` | 2 | 0 | `z_drain_use_after`, `z_touch_then_end` |
| `contact_live_after_abort` | 1 | 0 | `z_abort_use_after` |
| `livelock` | 1 | 0 | `livelock_all` |
| `drain_converge` | 2 | 0 | `livelock_stop2`, `livelock_transient` |
| `corrupt` | 2 | −11 | `n_depth2_drain`, `n_depth2_drain_wp` |

- `rc` distribution over the 17 new rows: 14× `0`, 1× `1`, 2× `-11`.
- **Fatal/corrupt tail respected**: postland indices 80–91 read
  `bc_coyield`(died,rc=1), `cowrap_update_yield`(died), `ext_worldrelease`(died),
  `bc_cowrap_unp`(fatal), **`n_destroy_contacting`(dispatch_escape,rc=1)**,
  then the five r77 `corrupt` rc=−11 rows, then **`n_depth2_drain`,
  `n_depth2_drain_wp` (corrupt, rc=−11) last**.
- Partial-capture shape confirmed for the two new corrupt rows and the new
  rc=1 death row: no `CELL_DONE` in stdout, stderr **0 bytes on all 17 new
  cells** (`new-rows-stability.txt`).
- **Rep-stability control**: all **17/17 new rows byte-identical** between
  rep1 and rep2 (0 `observed`-only, 0 other diffs) — including the two rc=−11
  corrupt rows.

### Declared vs measured — reconciliation

| author declaration (`reports/round-78/r78-author.md`) | this seat's measurement |
|---|---|
| 17 new `IW_CELLS` rows; love_battery `+560/−5`, main.lua `+479/−0` | exactly **17** new rows, same key names; same numstat; `IW_CELLS` block 736→1040 with 0 delete/replace |
| "No `IW_CELLS` row was moved or edited" | prior 75 rows order-preserved, 0 tuple mismatches, block subsequence identical |
| prior 112 iw receipts: 101 byte-identical, **11** `main.lua:NNN`-only, **0 semantic** | 11 token-only cells — **exactly the 11 named cells**; 0 semantic; plus 4 numeric-jitter-only and the 1 undeclared splice ordering permutation |
| pygame 80/80 unaffected | 80/80 PASS, 80 prior rows at identical positions, 0 mismatches |
| "fatal/corrupt rows last" | held (2 new corrupt rows last; new rc=1 death row inside the tail) |

No undeclared prior-row semantic drift was found. The only measured delta
outside the author's declaration is the `splice-80-50` line-order permutation,
which is reproducible-in-both-orders on this host and therefore classified as
ordering jitter, not drift.

## Artifact inventory (`corpus/live/r78-baseline/`)

- `freeze/HEAD-d4aaa958….tar` — `git archive HEAD`, 688,281,600 B, sha256
  `342710aa…`, deterministic re-run match; `freeze/tar-members.txt`.
- `freeze/extract/` — populated frozen tree (44,886 files + 34 symlinks,
  comm-clean vs `git ls-files`); replay surface.
- `freeze/love-runs/love-20261014T205330614648Z/` — 75/75 ·
  `freeze/pygame-runs/pygame-20261014T205350160537Z/` — 80/80.
- `postland/love-runs/love-20261014T211125990828Z/` — 92/92 ·
  `postland/love-runs2/love-20261014T211156070014Z/` — 92/92 (rep 2) ·
  `postland/pygame-runs/pygame-20261014T211145943377Z/` — 80/80 ·
  `postland/pygame-runs2/pygame-20261014T211215546763Z/` — 80/80 (rep 2) —
  committed-tree (`1a03b7a`) re-verify.
- `freeze/receipt-shas.txt` (155 rows) and `postland/receipt-shas.txt`
  (174 rows: 92 + 80 + 2 verdicts shas) — per-cell receipt sha tables.
- `freeze/fixture-manifest-{frozen,live}.txt` (61-entry fixture sha seed).
- `preland-love_battery-{CASES,SPLICE_CELLS,IW_CELLS}.txt`,
  `preland-pygame_battery-{CASES,RAW_CASES}.txt`, `preland-snapshot.log`.
- `diff_receipts.py` + `diff-output.txt` — **101 ref comparisons, 0 skips**
  (frozen LOVE 25 × 75-row + 21 × 49-row refs; frozen pygame 14 × 80-row
  refs; postland LOVE + pygame vs their frozen replays and every clean
  committed ref); `prior_row_diff.py` + `prior-row-diff-{love,pygame}.txt`;
  `postland_blocks.py` + `block-diff.txt`; `byte_drift.py` + `byte-drift.txt`;
  `raw_receipts_drift.py` + `raw-drift.txt`; `receipt_shas.py`;
  `position-map.txt`, `line-order-check.txt`, `new-rows.txt`,
  `new-rows-stability.txt`.
- stdout/stderr pairs: `love-battery`, `pygame-battery`, `love-postland`,
  `pygame-postland`, `love-postland2`, `pygame-postland2` (all `.stderr`
  siblings **0 bytes**).
- `freeze-head.txt`, `run-start.txt`, `env.txt`, `extract-done.txt`,
  `extract-time.txt`, `phase1-provenance.txt`, `phase2-provenance.txt`,
  `pre-existing-dirty-state.txt`; `poll-commit.sh` + `poll.log` +
  `phase2-watch.sh` + `phase2-watch.log` + `phase2.sh` + `phase2-run.log`.

## Process hygiene

No tracked file edited by this seat; no commit, no push, no cleanup of the
pre-existing dirty state. `git status` shows only pre-existing sibling residue
(`M corpus/live/r72-simplifier/*`, untracked prior-round scratch,
`corpus/fixtures/__pycache__/`) plus this seat's own untracked
`corpus/live/r78-baseline/` and `reports/round-78/r78-baseline.md`. Both
watchers self-exited (poll on HEAD change, phase2-watch after its single
Phase-2 run); all six battery launches used `--runs` inside this scratch root.

## Known limits (explicit)

- **Phase-2 evidence is pinned to `1a03b7a`** (HEAD at 21:11:25Z, still HEAD
  at 21:15:19Z). A later closeout/report-last commit that re-touches
  `corpus/fixtures/` would need a re-run; none had landed when this report
  was written.
- Timing-quantity `observed` fields are bound-pinned by construction and
  excluded from the byte-identity claim (r67–r77 precedent); 6 LOVE and
  17–19 pygame prior rows differ in that field only.
- The LOVE `CASES` rows derive from a single probe capture; their prior-row
  identity is verified at the verdicts-row level.
- One of the 25 75-row LOVE refs is the r77 pre-fix intermediate
  (`runs/love-20261014T194717707844Z`, 3 rows FAIL); it is flagged and
  excluded from the clean-reference count. All other 24 show 0 mismatches.
- No `lsp` device is exposed on this host (unchanged from r77); nothing here
  depends on symbol-aware tooling.
