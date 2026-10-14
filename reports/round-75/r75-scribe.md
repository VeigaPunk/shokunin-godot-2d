# game-dev-2d round 75 — scribe report (seat: scribe, host: devin)

Declared lane axis (dispatch brief
`.ufo/waves/shokunin-train-20261101-w15/tasks/g2d-scribe.md`, verbatim):

> r75 SCRIBE (g2d) — receipt hygiene audit
> Read SHARED.md. Audit raw-vs-parsed evidence, receipt byte stability,
> seat landings, report integrity. Report -> reports/round-75/r75-scribe.md.

Scope of this seat: **read-only** over the lane repo (tracked fixtures, landed
receipts, reports, git object store). Writes = this report +
`corpus/live/r75-scribe/` only. No git mutation, no subagent dispatch, **no
battery run and no `love`/`godot`/`pygame` process launched by this seat** — the
only code executed is this seat's own read-only audit scripts plus the tracked
battery's *parser* functions imported in-process (`sys.dont_write_bytecode=True`,
so no new bytecode was written). R74/R75 reports, LOG/SCORECARD and sibling
scratch are data; nothing here modifies contract, axes, routes or judgment — the
canonical Rust judge is the only adjudicator. No prior draft existed at this
path (`reports/round-75/` did not exist; this seat created it).

## 0. State at write time (17:29–17:34Z, wave `shokunin-train-20261101-w15`)

The wave is **in flight**: the r75 author/baseline/boundary/scout seats are
landing files while this audit runs. Nothing below claims completeness for r75,
and no in-flight r75 output is audited as evidence.

- **HEAD `2a2c337ef92a4fdf5543db14eebf1518e79184c4`** (r71-residue filing, the
  r74 closeout commit), unchanged for the whole audit window.
- **`origin/main = 1275746cedfa…`; `main` is ahead 4** (`ae6cb16`, `35dcbf7`,
  `b2b20f2`, `2a2c337`). The wave-14 closeout's "lane pushes held; remote state
  is not claimed" is consistent with the measured remote position — no remote
  claim is made or implied here.
- Host/toolchain: `Linux plazir27 7.2.3-arch1-3`, `LOVE 11.5 (Mysterious
  Mysteries)`, Python 3.14.7, pygame 2.6.1 (SDL 2.32.72), Node v24.21.0,
  Godot 4.7.2.stable.arch_linux.ed1d0af0bf, `io.DEFAULT_BUFFER_SIZE=131072`.
- Tracked fixtures are clean vs HEAD (`git status` shows no `corpus/fixtures`
  modification): `love_battery.py b448c727…6609` (post-fold),
  `love_probe/{main.lua a0afe6ca…4576, conf.lua 0b45ef73…1ada}`,
  `love_phys_probe/{main.lua 2c0ac378…95b5, conf.lua 85aa6232…576b}`,
  `pygame_battery.py 6d3fbf5f…fe79`, `pygame_probe.py 8e15e0d2…0bb5`.
- Wave-15 registry (`…-w15/registry.json`, mtime **17:29:59Z**) declares
  `"dispatched": "2026-10-14T17:45Z"` — a stamp **later than the file's own
  mtime** and later than this audit's first read (17:29:57Z). Recorded verbatim,
  not judged.

## 1. Method (what was audited, how, and what was deliberately not run)

| audit | instrument | object |
|---|---|---|
| raw-vs-parsed | `corpus/live/r75-scribe/audit_love_receipts.py` | every landed LOVE receipt in the tree (`verdicts.json` + its raw `probe/splice/iw` files) |
| byte stability | same script (concat-sha grouping) + `boundary_claims.py` | `iw-*.stdout.txt` byte-identity; r74-boundary JSON determinism/load claims; raw↔JSON `stdout_sha256` |
| seat landings | `git ls-files` / `git hash-object` / `git rev-parse HEAD:<p>` / `stat` | all 10 r74 reports, 9 r74 scratch dirs, wave files, r75 in-flight dirs |
| report integrity | `corpus/live/r75-scribe/refs_check.py` + targeted greps | 10 r74 reports: path references, claim referents, cross-report numbers |

No cell was re-run. Every number below is re-derived from the bytes on disk or
from the git object store; where a claim's referent is ambiguous the ambiguity is
reported rather than resolved silently.

## 2. Raw-vs-parsed re-derivation

Two independent derivations per receipt, both from raw bytes:

- **A. shipped-parser consistency** — re-run the *tracked* `parse_arms`/`check`/
  `splice_verdict`/`parse_iw` on the raw files and compare against the run's own
  `verdicts.json`. Pin keys whose comparison needs the process `rc` (never
  persisted) are counted, not silently passed.
- **B. independent text derivation** — a from-scratch kv parser (incl. the
  documented `evpin_<cb>_lck/_step` synthesis) plus a 5-rule classifier, applied
  to the raw `iw-*.stdout.txt` text, compared to the class the receipt claims.

Result (`audit_love_receipts.json`, run 17:31Z):

| metric | result |
|---|---|
| LOVE run dirs discovered (r70→r75 whole tree) | **98** (95 PASS / 3 FAIL) |
| case rows re-derived from raw | **2,101** |
| arm drift | **0** |
| splice drift | **0** |
| iw parse drift (shipped parser, non-`rc` pins) | **0** |
| iw class drift (independent text rule) | **0** |
| iw cells (16 run dirs × 18) | **288** (288 pin-compared) |
| FAIL rows reproduced from raw | 17 = 13 arm rows recorded as the *same* FAIL shape + 4 splice rows re-derived as `missing` |
| non-empty `iw-*.stderr.txt` | 0 |

Per-round dir distribution (runs audited): r70-critic 6, r71 {baseline 1,
reviewer 3, simplifier 4, verifier 1}, r72 {baseline 9, reviewer 1, simplifier 1},
r73 {baseline 13, reviewer 2, simplifier 1, verifier 1}, r74 {author 4, baseline
13, critic 3, reviewer 4, simplifier 7, verifier 2}, r75-baseline 12,
`corpus/live/runs` 9, integrator-r74-fold 1.

**Convergence with the r74 scribe's own audit** (different instrument, narrower
scope — r70→r74 pre-land, 41 run dirs / 734 cases / 601 arm cases / 0 drift):
same zero-drift conclusion, extended here to 98 run dirs / 2,101 rows including
the r75-baseline replay.

**Witness gap found (not a defect in the landed data, a limit of the receipt
set):** the process `rc` is *not persisted anywhere* per cell — `verdicts.json`
carries `observed`/`pinned`/`reasons` only, and no `iw-*.stderr.txt` carries it.
The shipped `iw_classify` reads `rc` to split `fatal` (rc≠0 + assert text) from
`died` (rc≠0, no assert text). Therefore class re-derivation from landed bytes
cannot use the shipped rule verbatim; the rule set above substitutes "no
CELL_DONE + `Box2D assertion` on stdout" and reproduces all 18 landed classes,
but the `fatal`/`died` boundary itself is not re-derivable from the receipts.
16 run dirs carry `rc`-dependent pins. A future round that lands a `died` cell
should persist the exit status (or the classifier's verdict string) alongside the
raw capture.

## 3. Receipt byte stability

### 3.1 `iw-*.stdout.txt` concat-sha invariance (extended)

`cat iw-*.stdout.txt | sha256sum` per run dir (shell glob order), over all 16
dirs that carry the 18 IW receipts:

| sha256 (full) | dirs |
|---|---|
| `58af4e7e1bc6c754de7e3ad8dd55b75b1d1a05f1fbf831968092aeb116801f86` | **15** — 4×r74-author, r74-baseline postland, r74-critic replay, 2×r74-reviewer, 3×r74-simplifier (A/B/baseline), 2×r74-verifier, integrator-r74-fold, **and r75-baseline's fresh 17:31:11Z replay** |
| `7faf9409e73983eebfa43821099f9d06d20b02e3bf1b8103207c9157d6b7753c` | 1 — `r74-simplifier/runs-L` (the **documented** variant-L run) |

- The r75-baseline replay (37/37 PASS, wave-15 seat, 3.7 h after the r74 land)
  falls in the same group: byte-stability holds **across the wave boundary**, not
  only inside r74.
- The single outlier is verified as the variant-L divergence the simplifier
  report itself declares: per-cell `cmp` over the 18 receipts shows **exactly 2
  differ** (`iw-bc_setpos_unp`, `iw-bc_newbody_unp`) and **only in embedded
  traceback line numbers** (`main.lua:94→95`, `172→174`, `177→179`, `218→220`).
  Sibling claim verified from raw bytes.

### 3.2 Fixture ledger (convergent, no silent movement)

| file | now | parent `1275746` | sibling pre-land ledgers |
|---|---|---|---|
| `love_battery.py` | `b448c727…6609` | `25977ad9…3647` | r74-verifier `sha256-preland.txt` and r74-simplifier `baseline-hashes.txt` **both** = `25977ad9…3647` |
| `love_probe/main.lua`, `conf.lua`, `pygame_battery.py`, `pygame_probe.py` | unchanged vs pre-land (controls intact) | same | same |

`git show 1275746:…love_battery.py` re-hashes to the recorded pre-land value, so
the pre-land ledger is the parent commit's bytes, not a scratch artifact. Table
sizes (AST count of the tracked file): `1275746` = CASES 15 / SPLICE 4 (19 love
cases); `ae6cb16`/`35dcbf7`/HEAD = 15 / 4 / **18** (37) — matching the reports'
"19→37 by exactly the declared 18 IW".

### 3.3 r74-boundary determinism, load and raw↔JSON claims (`boundary_claims.txt`)

| claim (r74-boundary.md §6) | re-derived | verdict |
|---|---|---|
| `edge-verify1` (51) vs `edge-verify2` (51): 0 differing `stdout_sha256` | 51 shared, **0 differing** | holds |
| `edge-final` (54): 51 shared cells identical | 54 cells, 51 shared, **0 differing**; the 3 extras are the `mixed_morph_sensor_*` cells | holds |
| `edge-mixed1/2` 2/2 identical | 2 shared, 0 differing | holds |
| `edge-bcown1/2` identical incl. the abort | 1 cell × 2 reps, sha `5420cd2e1b74…`, `rc=-6`, class `sig_SIGABRT`, identical | holds (2 **reps**, not 2 cells) |
| load replay "0 differing cells vs the baseline (51/51)" | **vs the 51-cell verify pair: 0/51 differing**; vs `edge-load.json` (a **35**-cell gen-1 file): 12/35 differ | holds **only** under the verify-pair referent (§6.2) |
| `edge-run2` lattice rows byte-identical to `edge-load` | 35 shared rows, **0 row inequalities** | holds at row level |
| raw ↔ JSON `stdout_sha256` | `out-verify1` 51/51, `out-verify2` 51/51, `out-final` 54/54, `out-mixed1` 2/2, `out-bcown1` 1/1 | holds; note the bcown raw lives at `out-bcown1/out/<cell>.stdout.txt` (nested), the other reps put raws at the rep-dir top level |

### 3.4 Receipt classes: committed vs ignored vs merely untracked

- **Committed**: all 10 `reports/round-74/*.md` — `git hash-object` ==
  `git rev-parse HEAD:<path>` for **10/10** (report bytes *are* committed bytes);
  `LOG.md`/`SCORECARD.md`; and the receipts through r72 — 44,048 tracked files
  under `corpus/live` in total, of which the newest tracked slice (r70–r72) is
  773 files and **0 files are tracked for r73, r74 or r75**.
- **Deliberately ignored** (`corpus/.gitignore`): `live/*/frozen/`,
  `live/*/*extract*/`, `live/*/tree|head|snapshot|base/`, `live/**/*tree*/`;
  `corpus/live/.gitignore`: `runs/`. This is why the 687 MB baseline tars are
  invisible to `git status` by design.
- **Merely untracked (not ignored)**: `corpus/live/r73-*`, `r74-*`,
  `integrator-r74-fold/`, `r75-*` — **3,404 untracked files** (`git status
  -uall`). The r74 seat-receipt trees are host-local: author 174, boundary 780,
  critic 183, reviewer 518, scout 86, scribe 28, simplifier 258, verifier 91,
  integrator-fold 46 files. A fresh clone (or the remote) has **none** of them,
  while the reports that cite them are committed. Every "landed receipt" citation
  for r73+ is therefore working-tree-only and must be read that way.
- **Dirty tracked receipts** (working tree ≠ HEAD, append-only growth):

  | file | HEAD bytes | disk bytes | delta | mtime |
  |---|---|---|---|---|
  | `corpus/live/r72-simplifier/watch.log` | 5,538 | 6,054 | +2 lines | 14:57:29Z |
  | `corpus/live/r72-simplifier/snapshots/log.txt` | 179 | 1,074 | +5 lines | 15:35:26Z |

  Both are cited as evidence by 7 reports (r72-simplifier, r73-scribe,
  r73-simplifier, r73-baseline, r74-baseline, r74-critic, r74-simplifier), so
  those citations are only reproducible against the dirty tree, not against
  HEAD. Five further snapshot dirs under the same (tracked) `snapshots/` dir are
  untracked. The r74 adjudicator recorded this residue class already; this seat
  only quantifies it.

### 3.5 Orphan writer from a closed wave (live)

`pid 1463255  bash corpus/live/r74-scribe/author_land_poll.sh` — armed ~16:26Z,
**alive at 17:33Z (3,846 s)**, 10 s poll, appends `COMMIT …` lines into
`corpus/live/r74-scribe/landings.log` on every HEAD change. Current log
`sha256 e8f9272962523681…aa805f`, mtime 17:25:17Z (its last write = `2a2c337`);
the hash was **unchanged across this audit** only because HEAD did not move. It
will fire on the first r75 commit, so a *closed* round's receipt file is
mutable during r75. Its last recorded md5 (`147fa343fe388195`) does **not** match
the committed `r74-scribe.md` (`86f509a536825687`): the log's hash chain stops at
the gen-1 draft, i.e. it witnesses the pre-recovery draft only.

## 4. Seat landings

**r74 (9/9 + adjudicator, all verified):** `r74-adjudicator|author|baseline|
boundary|critic|reviewer|scout|scribe|simplifier|verifier.md` all present,
tracked, and byte-matching HEAD; author report landed in `ae6cb16`, the other
nine in `b2b20f2`; the wave-14 registry's `g2d-r74.seats: "9/9"` and
`outcomes.g2d-r74.commits = [ae6cb16, 35dcbf7, b2b20f2]` both check out against
`git log`. Scratch dirs exist for all nine seats + `integrator-r74-fold/`.

**r75 in flight (partial, no verdict):** `corpus/live/r75-author/` (32 files),
`r75-baseline/` (45,337 — incl. `preland-head.txt` = `2a2c337`, the frozen
`HEAD-2a2c337….tar`, a 37/37 PASS love replay at 17:31:11Z, `poll-commit.sh`),
`r75-boundary/` (114 — `cells/ apicheck/ out/`), `r75-scout/` (194 — `cells/`
includes `lvl1.bc_destroy_unp` and `lvl1.bc_setvel_unp`, i.e. the C1 twins, plus
`lvl1.*` containment-level cells for C3), `r75-scribe/` (this seat, 7 files).
`reports/round-75/` holds only this report. Sibling lanes: `audio r76`
`reports/round-76` absent; `g3d r84` dir exists, empty at read.

## 5. Report integrity

- **Dangling references** (`refs_check.txt`): 96 literal path tokens across the 10
  r74 reports, 89 present, **7 raw misses — 0 genuinely dangling**. Resolution of
  all 7: 2 line-wrapped/glob tokens (`corpus/live/r72-`, `corpus/live/r74-author/
  runs/love-`), 2 brace-range tokens (`frontier-lovephysics/out/run-{1..7}.txt`,
  `r74-author/scratch_iw/{main.lua`), 1 out-of-tree upstream source path
  (`src/libraries/Box2D/Common/b2StackAllocator.cpp` — LOVE's own tree, cited for
  the build claim), 1 microsecond-truncated dir name
  (`pre-love-runs/love-20261014T160210Z/` → actual
  `…T160210648000Z`), 1 brace token (`r74-verifier/runs{`). The only one a reader
  cannot resolve literally is the truncated run dir.
- **Freeze-count referent**: r74-baseline's "44,873 non-dir entries == `git
  ls-files | wc -l`" is **exact at the frozen rev** (`git ls-tree -r 1275746` =
  44,873). Today's `git ls-files | wc -l` = **44,888**; the +15 is fully accounted
  for by the 4 post-freeze commits (2 fixtures + 3 r71-residue reports + 10
  round-74 reports). Time-scoped claim, no drift.
- **Handoff to r75 verified**: the r75 author brief carries the deferred frontier
  the r74 critic declared — C1 twins (`bc_destroy_unp`, `bc_setvel_unp`), the C3
  containment-level cell (`pcall(world:update)` vs `pcall(interior write)`), the
  `esc_fn` pin (critic §4 rank 4) and the joints/`setFilterData` stretch — and
  the r75 scout is already sampling those cell names. **Critic §4 rank 5
  (`after_update.b1vel: "55,-7"` on `iw_bc_setvel`, to make "applied"
  effect-bearing rather than legality-only) appears nowhere in the wave-15
  material** (registry, SHARED, all 15 briefs). Recorded, not judged: it may be a
  deliberate scope call.
- **Row-level vs run-level verdicts**: the 3 FAIL receipts are not all
  row-FAILs. `r74-critic/battery_mutant/runs-fatal` has **19/19 rows PASS** with
  battery `verdict=FAIL` (`done_marker=false`, `probe_exit=1`) — the run-level
  verdict is *not* derivable from the rows; it needs the payload's
  `done_marker`/`probe_exit`, which are persisted. The other two FAILs
  (`r74-reviewer/crash-runs` 4/19, `corpus/live/runs/love-…141302410332Z` 17/19)
  reproduce row-for-row from raw.
- **Cross-report numbers** spot-checked and consistent: `58af4e7e…801f86`
  (adjudicator = LOG = SCORECARD = re-derived); "AGREE 13/13" (verifier §
  per-claim table has exactly 13 rows); "godot 88, love 19→37, pygame 80";
  "44,873" freeze; "9 seat reports folded" (`b2b20f2` stat = 9 reports + LOG +
  SCORECARD); insertion-only `+292/−0` (verified as `git show --stat ae6cb16`).

## 6. Conflicts / discrepancies, verbatim, for the canonical judge

None of these is an upgrade of an unobserved claim; each is a wording, referent
or scope mismatch between a landed sentence and the re-derived bytes. They are
listed for the judge, not resolved here.

1. **"6 independent runs"** (r74-adjudicator:19, LOG:870, SCORECARD:118) vs the
   measured **15 non-variant run dirs + 1 documented variant** carrying the 18 IW
   receipts. The r74-verifier's "all 6 run dirs" is explicitly scoped ("my 2
   replays + all 4 author dirs") and is accurate as scoped. The published figure
   is an understated floor, not a contradiction — but the landed witness set is
   larger and now includes a wave-15 replay.
2. **"0 differing cells vs the baseline (51/51 byte-identical)"**
   (r74-boundary.md §6, load replay) — "the baseline" is unnamed; the claim is
   exact against the 51-cell `edge-verify1/2` pair and false against
   `edge-load.json`, which is a 35-cell gen-1 file (12/35 `stdout_sha256` differ).
3. **"`edge-run2.json` 30399 B ≡ `edge-load.json` 30399 B"** (same §6) — true at
   **row** level (0/35 row inequalities) but not at file level: the file sha256s
   differ (`46e7d074…` vs `a8a6e08d…`); the shared byte size is coincidental.
4. **"`edge-bcown1/2.json` (2/2 identical, including the abort)"** — 2 *reps* of
   1 cell, not 2 cells (contrast `edge-mixed1/2` = 2 cells).
5. **`44,873 == git ls-files | wc -l`** (r74-baseline:47) — exact at the frozen
   rev `1275746`; today's count is **44,888** (4 later commits, +15 files).
6. **`r74-scribe/landings.log`** stops at the gen-1 draft (md5 `147fa343…` ≠
   committed report `86f509a5…`) and is **still being appended to** by an orphan
   poller (pid 1463255) from the closed wave.
7. **Two tracked receipts are dirty vs HEAD** (`r72-simplifier/watch.log` +2
   lines, `snapshots/log.txt` +5 lines) and are cited as evidence by 7 reports —
   those citations do not reproduce against a clean checkout.
8. **Wave-15 registry stamp** `dispatched: 2026-10-14T17:45Z` is later than the
   registry file's own mtime (17:29:59Z) and later than this audit's reads.
9. **r73+ seat receipts are untracked, not ignored** — 3,404 files
   (`r70–r72` receipts are tracked). Any wording that reads as "committed
   receipts" for r73/r74/r75 should be read as "host-local working-tree receipts".
10. **Receipt-set limit**: per-cell process `rc` is not persisted, so the
    `fatal`/`died` split (and any future abort-class cell) is not re-derivable
    from landed bytes (§2).

## 7. Artifacts and reproduce (this seat)

- `corpus/live/r75-scribe/audit_love_receipts.py` → `audit_love_receipts.json`
  (98 run dirs, 2,101 rows, per-run drift lists, concat-sha groups)
  `python3 corpus/live/r75-scribe/audit_love_receipts.py`
- `corpus/live/r75-scribe/boundary_claims.py` → `boundary_claims.txt`
- `corpus/live/r75-scribe/refs_check.py` → `refs_check.txt`
- `corpus/live/r75-scribe/state.txt` (environment + ledger snapshot)
- Evidence commands used, all read-only: `git ls-files|ls-tree|hash-object|
  rev-parse|show|status -uall`, `sha256sum`, `cmp`, `diff`, `stat`, `ps`,
  `python3` (this seat's scripts), `ls`. No `love`/`godot`/`pygame` invocation.

## 8. Limits (bounded claims)

All claims are bounded to **this host, this repo, these versions** (above), and to
the audit window **17:29–17:34Z 2026-10-14**. The r75 wave was mid-flight: r75
seat outputs are recorded as landed-at-read only and carry no verdict; r75's
author/boundary/scout/baseline claims are unaudited here. No battery cell was
re-executed, so "byte-stable" means *the landed raw bytes reproduce the landed
parsed view*, not that a fresh process would reproduce the same bytes — the
latter is witnessed only by the sibling replay receipts (16 dirs, incl. the
r75-baseline 17:31:11Z run) that this seat re-read, not re-ran. The
`fatal`/`died` boundary and any abort-class cell remain unverifiable from the
receipt set as landed.
