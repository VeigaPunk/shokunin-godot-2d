# game-dev-2d round 76 — scribe report (seat: scribe, host: devin)

Declared lane axis (dispatch brief
`.ufo/waves/shokunin-train-20261101-w16/tasks/g2d-scribe.md`, verbatim):

> r76 SCRIBE (g2d) — evidence audit + receipt provenance
>
> Read SHARED.md. Audit the lane's evidence integrity for r75->r76:
> - verify the landed r75 receipts: re-parse every r75 iw-*.stdout.txt in
>   the author/verifier/reviewer run dirs; confirm the pinned values are
>   byte-derivable; flag any receipt whose pin can't be re-derived
>   (provenance hole).
> - verify the r75 fold delta claims: the only receipt diffs should be
>   mode=unp on the two twins + unpinned traceback line drift on the two
>   fatal rows + srcline on wp. Anything else is a discrepancy — report it.
> - witness-gap followup: per-cell rc is now persisted in verdicts.json
>   (r75 fold) — confirm the field exists and discriminates fatal/died.
> - enumerate uncommitted-vs-committed scratch provenance: which cited
>   receipts exist on disk, which are committed, which are claimed but
>   absent.
> Report -> reports/round-76/r76-scribe.md.

Scope of this seat: **read-only** over the lane repo (landed receipts, tracked
fixtures, git object store, reports). Writes = this report +
`corpus/live/r76-scribe/` only. No git mutation, no subagent dispatch, **no
battery run and no `love`/`pygame`/`godot` process launched by this seat** —
the only code executed is this seat's own read-only audit scripts plus the two
battery revisions' *parser/classifier* functions imported in-process
(`sys.dont_write_bytecode=True`). Reports, receipts and commit messages are
data; nothing here modifies contract, axes, routes or judgment — the canonical
Rust judge is the only adjudicator.

## 0. State at write time (18:20–18:26Z, wave `shokunin-train-20261101-w16`)

- **HEAD `ddd455b49f0594610a065b360b8a3211fa510c09`** (r75 report-last);
  `origin/main = 1275746cedfa…`; **`main` is ahead 7** (`ae6cb16`, `35dcbf7`,
  `b2b20f2`, `2a2c337`, `2e3ae8e`, `be79ad1`, `ddd455b`). No remote claim.
- r75 chain under audit: work `2e3ae8e` → fold `be79ad1` → report-last
  `ddd455b`; wave-16 registry `dispatched: 2026-10-14T18:14Z` (g2d r76
  author/scout/boundary/baseline/scribe + g3d r85).
- Host/toolchain: `Linux 7.2.3-arch1-3 x86_64`, `LOVE 11.5 (Mysterious
  Mysteries)`, Python 3.14.7.
- Fixture ledger, **disk == `be79ad1` == `ddd455b`** (re-hashed, no drift):
  `corpus/fixtures/love_battery.py` `2f993578f93478ce…` (33,467 B),
  `corpus/fixtures/love_phys_probe/main.lua` `9c375230d2f9f55b…` (15,155 B).
  Pre-fold copies (`2e3ae8e`) `24a30a31c52ed65c…` (31,515 B) /
  `c80e2ba319d32ef0…` (14,833 B) — both extracted to this seat's scratch for
  the two-revision pin audit.
- r76 lanes are in flight: `corpus/live/r76-baseline/` (freeze phase landed),
  `corpus/live/r76-scout/` (empty at read); no r76 author commit yet.
  `reports/round-76/r76-baseline.md` landed at 15:25 local while this seat was
  writing — recorded as landed-at-read, **not** audited here. Nothing
  in-flight is audited as evidence.

## 1. Method

| item | instrument | object |
|---|---|---|
| 1 | `corpus/live/r76-scribe/audit_r76.py` (§C) | every `iw-*.stdout.txt` in the 7 author/verifier/reviewer run dirs (175 receipts), re-parsed with the **shipped** parser of the matching revision **and** an independently written parser (`iparse`); every table pin re-derived from raw bytes |
| 2 | same script (§E) + `git show be79ad1` | canonical pre-fold dir vs the post-fold `integrator-r75-fold` run: every file, every differing line, categorised; pin-space cross-check (HEAD pins × pre-fold bytes) |
| 3 | same script (§F) | `rc` presence in `verdicts.json` rows, whole-tree scan of every `verdicts.json` carrying `rc`, in-process fatal/died discrimination on a real fatal receipt |
| 4 | same script (§G) + `git ls-files`/`show`/`check-ignore`, `ps` | 22 r75-family run dirs, 10 r75 reports, 100 cited path tokens, 2 explicit "receipt in dir" claims, tracked-receipt dirt, orphan writers |

No cell was re-run; no battery was launched. 543 receipts were re-parsed
(175 pre-fold + 25 post-fold + 343 across the other 14 r75-family dirs), 4,715
pin values re-derived, 0 mismatches. Digest: `corpus/live/r76-scribe/audit_r76.txt`.

## 2. Item 1 — the landed r75 receipts re-parse; pins are byte-derivable

**Per-dir result (7 author/verifier/reviewer dirs × 25 cells):**

| dir | stdout-derivable pins OK | missing | mismatched | parser disagreement | class re-derived == recorded |
|---|---|---|---|---|---|
| `r75-author/runs/…T173642593012Z` | 201 | 0 | 0 | 0 | 25/25 |
| `r75-author/runs/…T173738748447Z` | 201 | 0 | 0 | 0 | 25/25 |
| `r75-author/runs/…T173748952061Z` | 201 | 0 | 0 | 0 | 25/25 |
| `r75-author/runs/…T173810495744Z` | 201 | 0 | 0 | 0 | 25/25 |
| `r75-verifier/runs/…T174224339664Z` | 201 | 0 | 0 | 0 | 25/25 |
| `r75-verifier/runs/…T174316002388Z` | 201 | 0 | 0 | 0 | 25/25 |
| `r75-reviewer/runs/…T174123645784Z` | 201 | 0 | 0 | 0 | 25/25 |

- **Every one of the 1,407 pre-fold pin values** (201 × 7, `rc` excluded — see
  below) is present in the raw bytes **and equal** to the pin. No mismatch
  anywhere. The `assert_txt` / `err_on` / `esc_fn` pins are not printed
  verbatim but are re-derived from the raw stdout by the battery's own
  `iw_flat_extras()` — all three re-derive for both fatal rows
  (`assert_txt=m_world_islocked` / `islocked`, `err_on=stdout`,
  `esc_fn=setPosition` / `newBody`).
- **Parser cross-check**: my independent `iparse()` (written from the receipt
  grammar, not copied) produces a flat map **identical** to the shipped
  `parse_iw()` on all 543 receipts — 0 disagreements.
- **Class cross-check**: the shipped HEAD classifier and my independent 11-rule
  classifier both re-derive the recorded class on 25/25 cells in every dir
  (including `refused_abort`, `ignored`, `deferred`, `applied`, `fatal`).

**Provenance hole found (pre-fold receipts only): per-cell `rc`.** The `rc` pin
exists on all 25 rows in the pre-fold table too, but **`rc` is persisted in 0
of the 7 audited run dirs' `verdicts.json`** (0/25 rows each) and appears in no
receipt file. So the `fatal`/`died` split is *not* byte-derivable from those
dirs: the class only re-derives if `rc` is **inferred** (no `CELL_DONE` +
`Box2D assertion` on stdout ⇒ rc≠0). With that inference, both classifiers
re-derive `fatal` for `iw_bc_setpos_unp` / `iw_bc_newbody_unp` and `rc=0`-class
values for the other 23 — i.e. the hole is a persistence gap, not a data
contradiction. This is exactly the r75 scribe §2 gap; §4 below confirms it is
closed for the post-fold run only.

**Corroborating provenance (pre-landing scratch, not re-run):** the author's
`corpus/live/r75-author/cells/*.r{1,2,3}.stdout.txt` scratch receipts are
byte-identical to the landed pre-fold receipts for 6 of the 7 new cells, and
`bc_setpos_wp` differs in **exactly one** field (`srcline=146` scratch →
`srcline=155` landed; srcline-normalised → identical). All scratch rep groups
are internally byte-stable (distinct-sha = 1). Pins therefore cannot have been
back-fitted to the landed code: the values were measured first, in a different
probe copy.

## 3. Item 2 — the r75 fold delta is exactly as declared (nothing extra)

Declaration under audit (`be79ad1` message, verbatim): *"Expected receipt
deltas: mode=unp on the two twin rows; unpinned traceback line numbers on the
two fatal rows + wp srcline (raw Error: lines, declared unpinned)."*

**Measured, canonical pre-fold dir vs post-fold dir (`integrator-r75-fold/runs/
love-20261014T180035355368Z`): 20 of 25 `iw-*.stdout.txt` are byte-identical;
5 receipts differ, in 9 differing lines total:**

| receipt | differing lines | category | pre → post |
|---|---|---|---|
| `iw-bc_destroy_unp.stdout.txt` | L7 | `mode=unp` addition | `cb_destroy ok=true err=nil alive_in_cb=…` → `… err=nil mode=unp alive_in_cb=…` |
| `iw-bc_setvel_unp.stdout.txt` | L7 | `mode=unp` addition | `cb_setvel ok=true err=nil vel_after=55,-7` → `… err=nil mode=unp vel_after=55,-7` |
| `iw-bc_setpos_unp.stdout.txt` | L12, L13, L15 | raw traceback line numbers | `main.lua:237/242/294` → `242/247/299` |
| `iw-bc_newbody_unp.stdout.txt` | L12, L13, L15 | raw traceback line numbers | `main.lua:237/242/294` → `242/247/299` |
| `iw-bc_setpos_wp.stdout.txt` | L7 | `srcline` drift | `srcline=155` → `srcline=160` |

- **0 uncategorised differing lines.** Every `IW | cell=… |` payload line in
  those receipts is otherwise byte-identical; the drifted lines are the raw
  `Error:`/traceback lines and the unpinned `srcline=` field.
- **All 25 `iw-*.stderr.txt` are 0 bytes on both sides.**
- **Pin-space cross-check (the decisive form):** the pre-fold receipt bytes
  satisfy **226 of HEAD's 228** stdout-derivable pins; the 2 unsatisfied are
  exactly `cb_destroy.mode` and `cb_setvel.mode` on every pre-fold-content dir
  (13 dirs × 2). The fold's *other* new pins — `fire.kind` (21 rows),
  `after_update.b1vel` on `iw_bc_setvel`, and the wp row's `fire.pos` /
  `wpext.err` / `wpext.pos_after` — are **already satisfied by the pre-fold
  bytes**, so no further receipt regeneration was needed. Post-fold, all
  **228/228** pins re-derive from the post-fold bytes.
- **Source anchors (why exactly these lines drift):** the fold's probe change
  is +8/−3 in `main.lua` in three hunks — a line-count-neutral comment swap at
  the file header (the "`*_unp` last of all" → "fatal cells last" wording,
  lines 14-17), then, inside `do_mutation`, a 5-line comment block and the two
  `mode=unp` EM sites (HEAD `main.lua:151` and `:156`). The net +5 line shift
  begins at that block, so `srcline` (the throwing `body:setPosition` at HEAD
  `main.lua:160`, pre-fold `:155`) and the three *later* traceback frames
  (`on_event` call site `:242`, its frame `:247`, `world:update(FIXED)` `:299`)
  move; the escape lines themselves (`setpos_unp` `main.lua:104`,
  `newbody_unp` `main.lua:108`) are **above** the insertion and do not move —
  which is why each fatal receipt drifts in 3 lines, not 5. Every drifted
  line re-anchors to a real source line in the folded file (verified by
  `grep -n` on both revisions).
- **Non-`iw` files (full-dir delta, 57 files):** 46 identical, 11 differ —
  the 5 `iw-*` above plus `probe.stdout.txt` + the 4 `splice-*.stdout.txt`
  (3 jitter lines each: `dt_max_ms`/`dt_mean_ms`/`dt_min_ms`, `l1_wait_ms`/
  `l2_wait_ms`/`close_wait_ms`/`total_ms`, `osx.ms`/`popen.open_ms` — the
  bound-pinned jitter keys plus the two keys that carry no CASES row) and
  `verdicts.json` (250 differing lines = `rc` additions + the same jitter
  observations). **No class, verdict or `reasons` string changed**: both runs
  are `cases=44 pass=44 fail=0 PASS`, and the only `observed` diffs are the
  six jitter-valued rows (`dtcadence_*`, `popen_*`).
- **Byte-uniformity of the pre-fold set:** across the 7 audited dirs all 25
  cells have exactly **1 distinct sha** — the pre-fold receipt set is a single
  canonical value per cell (concat sha `74db3f10…9004`). That same concat sha
  holds for **16 run dirs** in total (adds `integrator-r75-verify`,
  `r75-baseline/love-runs-postland`, `r75-critic`, `r75-simplifier/{control,
  c0,c2×2,c3,c5}`), so the r75 reports' "4 author dirs + mine" is an
  understated floor, not a contradiction. Post-fold concat sha is
  `9df61fde…8e8d`; the two deliberate simplifier variants
  (`c1_setpos_wp_dead_em` `0a6b9e3a…`, `c4_joint_pre_guard` `c3915f…`) sit
  outside both groups as expected, and the pre-land 18-receipt anchor is
  `58af4e7e…c754`.
- **Ordering evidence:** folded fixture mtimes are 15:00:05 local, the
  post-fold receipts were written 15:00:43, the fold commit is 15:01:52 — the
  post-fold run was made from the folded bytes (and those bytes are today's
  `be79ad1`/`ddd455b` bytes).

**Discrepancy report: none.** The only wording gap is a count, not a
contradiction: the declaration says "traceback line numbers" without saying
how many; the measured drift is 3 lines per fatal row (5 would require the
escape line and its own frame to move, which the insertion point forbids).

## 4. Item 3 — `rc` is persisted, and it discriminates `fatal` from `died`

- **Field exists**: `integrator-r75-fold/runs/love-20261014T180035355368Z/
  verdicts.json` carries `"rc"` on **25/25** `arm=="iw"` rows (0/25 in every
  pre-fold dir, including all 7 audited ones).
- **It discriminates, on landed values**: the two fatal rows are `rc=1`
  (`iw_bc_setpos_unp`, `iw_bc_newbody_unp`, both `observed=fatal`, PASS); the
  other 23 iw rows are `rc=0`. Whole-tree scan of every `verdicts.json`: the
  `rc` key exists **only** in this one run dir (25 rows), so r75's own landed
  receipt set is where the gap closes.
- **The classifier branch is rc-keyed** (`love_battery.py:508-511`): with a
  fire line present, no `CELL_DONE` and `rc ∉ {0,None}` → `fatal` if `Box2D
  assertion` is on stdout, else `died`.
- **Discrimination demonstrated in-process on real bytes** (no process
  launched): the real `iw-bc_setpos_unp` bytes + `rc=1` → `("fatal", "rc=1,
  assert text on stdout")`; the same bytes with the assert text replaced
  (synthetic) + `rc=1` → `("died", "rc=1 without assert text")`; the real
  bytes + `rc=0` → `("anomaly", "rc=0 done=False fire=True")`.
- **Limit (stated, not upgraded):** no `died` cell has ever landed in this
  tree, so the `died` branch is witnessed by that synthetic edit on real bytes
  plus the source branch — **not** by an observed `died` receipt. The r75
  fold closes the *re-derivability* gap for the run it verified; it does not
  retro-fit `rc` into the pre-fold dirs, which remain inferable-only.

## 5. Item 4 — provenance: on disk / committed / claimed-but-absent

**On disk, not committed (the whole r75 receipt set).** All 22 r75-family run
dirs exist on disk; **0 files in any of them are tracked by git** — every
r75 receipt citation is working-tree-only. `corpus/live/.gitignore:1` (`runs/`)
is why the `…/runs/…` subdirs are invisible to `git status` by design; the rest
is merely untracked. Measured: 47,500 untracked entries under `corpus/live`
(plus 2 modified tracked files, below); the newest tracked receipt slice is
r70–r72 (773 files); **0 tracked files for r73/r74/r75/r76**.

**Committed.** The 10 `reports/round-75/*.md` are byte-identical to HEAD
(`git show HEAD:<path>` == disk) — `r75-adjudicator 72ff1714…`,
`author dbacaa9f…`, `baseline c2dfb16b…`, `boundary d27e5b7c…`,
`critic c7f64b77…`, `reviewer ec2b53cf…`, `scout e4305179…`,
`scribe 2288476a…`, `simplifier 4470a9bb…`, `verifier 80c3ddd0…`; `LOG.md` and
`SCORECARD.md` also clean vs HEAD. So *the claims* are committed while *the
receipts they cite* are not — a fresh clone reproduces the sentences, not the
evidence.

**Claimed but absent.** 1 real case, 3 resolved artefacts:

- `r75-author.md` ("API surface verified first: `corpus/live/r75-author/
  api_probe/` … (receipt in dir)") — that dir holds only `conf.lua` +
  `main.lua` (the probe sources); **no captured receipt is in it**. The actual
  capture exists only as this seat's sibling's untracked
  `corpus/live/r75-verifier/api_probe.stdout.txt` (+ `.stderr.txt`). The r75
  verifier already scored the claim "AGREE substance / DISAGREE wording";
  independently confirmed here. Provenance hole: the author's own
  "verified first" evidence is not in the cited location.
- 3 `ABSENT` tokens among 100 cited paths: `corpus/live/r72-` and
  `corpus/live/runs/love-` (both in `r75-scribe.md`, line-wrapped/truncated
  tokens — the same class the r75 scribe flagged), and
  `corpus/live/r84-author/` (`r75-baseline.md`) — a **cross-lane** path that
  does resolve, in the sibling lane repo
  (`~/Projects/shokunin/game-dev-3d-shokunin/corpus/live/r84-author`), so it is
  not dangling.
- Citation status across the 10 r75 reports: 44 dir tokens, 37 untracked-file
  tokens, 13 glob/brace tokens, 3 tracked-file tokens, 3 absent (above).

**Dirty tracked receipts cited as evidence (carry-forward, still unfixed).**

| file | HEAD | disk | cited by |
|---|---|---|---|
| `corpus/live/r72-simplifier/watch.log` | 5,538 B | 6,054 B (+516) | `r75-boundary.md`, `r75-scribe.md` |
| `corpus/live/r72-simplifier/snapshots/log.txt` | 179 B | 1,074 B (+895) | `r75-boundary.md`, `r75-scribe.md` |

Both are tracked, append-only-grown in the working tree, so those citations do
not reproduce against a clean checkout (r75 scribe §3.4; unchanged mtimes
11:57:29 and 12:35:26 local — no further growth during r76).

**Orphan live writer from a closed wave.** `pid 1463255 bash
corpus/live/r74-scribe/author_land_poll.sh` is **still alive** (etime 1:54:50
at read) and appends `COMMIT …` lines into `corpus/live/r74-scribe/
landings.log` on every HEAD change — a closed round's receipt file remains
mutable during r76 (it already absorbed the r75 commits). Reported, not
touched. It is also an **independent witness of the fixture hash chain** (a
different writer, untracked file, 17 lines): its r75 rows record
`fixture_love_battery=24a30a31c52ed65c` at `2e3ae8e` and
`2f993578f93478ce` at `be79ad1`/`ddd455b` — matching this seat's re-hash of
`git show <rev>:corpus/fixtures/love_battery.py` exactly. (Its
`fixture_main_lua=a0afe6ca224efddf` field tracks `love_probe/main.lua`, which
the fold did not touch — not the phys probe's `9c375230…`.)

## 6. Findings and conflicts, verbatim, for the canonical judge

None of these upgrades an unobserved claim; each is a wording, referent or
scope mismatch between a landed sentence and the re-derived bytes. Listed for
the judge, not resolved here.

1. **r75-author.md "(receipt in dir)"** for `corpus/live/r75-author/api_probe/`
   — no receipt is in that dir (§5). The substance (5 named API functions
   present) is real, but the cited artefact is not where the sentence puts it.
2. **Fold-delta count**: `be79ad1` says "traceback line numbers on the two
   fatal rows"; measured = **3 lines per fatal row** (L12, L13, L15), because
   the escape line itself does not move. Consistent, under-specified.
3. **Pre-fold `rc` remains unpersisted** in all 7 author/verifier/reviewer dirs
   (0/25 rows) — the r75 fold's `rc` persistence reaches the post-fold run
   only. Any r76 sentence that reads "rc is re-derivable from the r75 receipts"
   must be scoped to `integrator-r75-fold` (and later runs).
4. **r75 receipts are untracked, not committed** (0 tracked files across 22
   r75-family dirs) while the reports citing them are committed — "landed
   receipt" should read "host-local working-tree receipt" for r73+.
5. **Two tracked receipts cited by r75 reports are dirty vs HEAD**
   (`r72-simplifier/watch.log`, `snapshots/log.txt`); those citations do not
   reproduce from a clean checkout.
6. **Orphan r74 poller still writing** (`pid 1463255`) — a closed round's
   `landings.log` is not frozen.
7. **Witness-set floor**: the pre-fold canonical concat sha
   `74db3f10…9004` is shared by **16** run dirs, not the 4–5 the r75
   verifier/reviewer scoped. Understatement only.
8. **`died` has never landed**: the `fatal`/`died` discriminator is verified
   by the persisted `rc` field plus an in-process synthetic-edit probe on real
   bytes, not by an observed `died` receipt.

## 7. Gates, out-of-scope, limits

- **Gates run**: none of the repo's battery gates — this seat deliberately
  launched **no** LOVE/pygame/Godot process and ran **no** cell. The audit is
  a re-derivation from bytes + the git object store. Nothing here is execution
  evidence for a new cell.
- **Not touched**: no product code, no fixture, no tracked file, no git state
  (no commit/push/branch), no sibling seat's scratch, no wave registry.
- **Out of scope / not audited**: the r76 in-flight lanes' outputs (baseline
  freeze, scout); the r75 audio lane and the g3d r84 lane (sibling repos);
  r76 author/scout/boundary briefs' frontier claims. Sibling scratch trees
  under `r75-critic`/`r75-boundary`/`r75-baseline`/`r75-simplifier` were read
  only as receipt dirs (their private battery copies were not used as a pin
  source).
- **Limits**: all claims are bounded to this host, this repo, these versions
  (LOVE 11.5 / Python 3.14.7 / LuaJIT 2.1.1788460057), and to the audit window
  18:20–18:26Z 2026-10-14. "Byte-derivable" means *the landed raw bytes
  reproduce the landed parsed view and every table pin*, not that a fresh
  process would reproduce the same bytes — the latter is witnessed only by the
  sibling replay dirs this seat re-read, not re-ran. The pre-fold `fatal`/`died`
  boundary stays inferable-only (§2); the `died` branch is synthetic-witnessed
  (§4).

## 8. Artifacts and reproduce

- `corpus/live/r76-scribe/audit_r76.py` → `audit_r76.json` (inventory,
  per-dir/per-cell pin re-derivation, fold delta with line-level diffs,
  pin-space cross-check, rc witness, provenance)
  `python3 corpus/live/r76-scribe/audit_r76.py`
- `corpus/live/r76-scribe/summarize_r76.py` → `audit_r76.txt` (human digest)
- `corpus/live/r76-scribe/pre_fold_love_battery.py`,
  `pre_fold_main.lua` (`git show 2e3ae8e:…`), `head_love_battery.py`,
  `head_main.lua` (working-tree copies) — the two revisions the pin audit
  compares.
- Read-only commands used: `git show|log|rev-parse|rev-list|ls-files|
  check-ignore|status -uall`, `sha256sum`-equivalent hashing in-process,
  `cmp`-equivalent byte comparison in-process, `stat`, `ps`, `python3` (this
  seat's scripts + the two battery modules imported in-process). No
  `love`/`pygame`/`godot` invocation.
