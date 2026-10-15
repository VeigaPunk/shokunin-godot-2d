# game-dev-2d round 79 — scribe report (seat: scribe, host: devin)

Task (dispatch brief, verbatim): "r79 SCRIBE (g2d) — closeout audit of
round 78 … Re-derive and cross-check: arithmetic vs `git --numstat`; fold
diff size vs claimed −1181 B; committed fold == verified vfold + semantic
fixes; adjudicator claims → receipts; prior-row stability 45/56 + 11;
ledger LOG/SCORECARD r78 entries; seat attribution on receipt dirs;
uncommitted/stray state. Write reports/round-79/r79-scribe.md. Do NOT
commit."

Scope: **read-only audit**. Writes = this report only. No LOVE/pygame/Godot
process launched, no cell re-run, no tracked file edited, no git mutation.
Battery claims are verified against committed receipts and landed JSON, not
re-executed. A prior draft of this report existed at this path (mtime
2026-10-14 20:56 -0300); this file supersedes it — every claim re-derived
independently, plus post-20:56 state it could not see.

Evidence classes: **[M]** measured by this seat now; **[C]** claim read
from a landed artifact (cited); **[U]** unobservable in this window.

## 0. State at read time

- HEAD **`884a4c4`** "r78 report-last: adjudicator ADMIT-corr + ledger"
  (2026-10-14 20:42:34 -0300). Chain resolves as dispatched: work
  `1a03b7a` (18:11:00) → fold `1fde57d` (19:55:17) → report-last `884a4c4`
  (20:42:34), all ancestors of HEAD **[M]**.
- Working tree is **not** clean: two tracked files carry uncommitted
  modifications (`SCORECARD.md` +29/−1, `corpus/fixtures/run_battery.py`
  +67/−0), plus 78 `git status` rows of untracked seat/receipt trees
  (§6) **[M]**.
- r79 and r80 work in flight concurrently with this audit: r79 author arm
  on disk (§6), `corpus/live/r80-scout/` (~900 K proj tree) exists **[M]**.

## 1. Commit arithmetic vs `git --numstat`

| commit | declared | measured (`git show --numstat`) | verdict |
|---|---|---|---|
| `1a03b7a` work | battery "+560/−5" (author tbl); probe +479/−0; report +381 | `love_battery.py` **560/5**, `main.lua` **479/0**, `r78-author.md` **381/0** | exact **[M]** |
| `1fde57d` fold | simplifier P1–P4 + drain-EC provenance + gate fixes | both fixtures **51/34 each** (+102/−68) | only the two fixtures touched **[M]** |
| `884a4c4` report-last | adjudicator + ledger | `LOG.md` +23, `SCORECARD.md` +11, `r78-adjudicator.md` +89 | exact **[M]** |

Minor phrasing note: the simplifier's audit line writes the battery delta
as "+565/−5" — that is changed-lines total (560+5), not insertions; the
author's "+560/−5" is the numstat-exact form. Byte deltas **[M]**:

- `1fde57d` committed: battery 114 018→114 909 B (**+891**), probe
  68 465→69 137 B (**+672**) → net **+1563 B**.
- Simplifier's `vfold/` vs `1a03b7a` blobs: battery 2 027→2 016 lines
  (**−11**), 114 018→113 064 B (**−954**); probe 1 367→1 367 lines (0),
  68 465→68 238 B (**−227**) → **−11 lines / −1181 B, exactly as claimed**.
- Consequence: the "−1181 B" in the fold message/adjudicator/LOG scopes
  to the vfold *variant*; the landed fold commit *nets +1563 B* because
  C1–C3 + own/own_n pins + comments sit on top of the deletions.
  Attributed correctly ("Simplifier vfold …"); misreadable as the
  commit's delta (F3 below).

## 2. Committed fold == vfold + semantic fixes — verified by residual diff

`diff` of `corpus/live/r78-simplifier/vfold/` against `git show
1fde57d` blobs leaves **exactly** the declared semantic layer and nothing
else **[M]**:

- Probe (5 hunks, all provenance): `r78_pending`/`r78_own_n` declarations
  + comment (`main.lua:266–272`); `r78_pending` set in `nested_queue`
  (:586), `queue_body` (:638–640), `queue_fixture` (:655–657); the drain
  hook's `own`/`own_n` emission (:1091–1098,
  `r78drainec … own=%s own_n=%d`).
- Battery (16 hunks): `r78drainec.own`/`own_n` pins added to **13 rows**
  (own=true on queue/drain members incl. `own_n=197` on `livelock_all`,
  `own_n=2` on the corrupt twins; own=false on the four
  immediate-destroy members); the `n_destroy_ground_wp` comment reword
  ("two immediate-destroy EndContacts"); the **C3** `drain_converge` gate
  (`r78drainact.kind ∈ {throw,throwall,noop}` + `r78wpcall.err` starts
  `R78-DRAIN-` + `aborts ≥ 1` + `drain_n ≥ 1` + prior numerics,
  `love_battery.py:1673–1685`); the **C1** `corrupt` re-key
  (`r78drainact.kind=="nested_update"` + `depth_before ∈ {"0","1"}` +
  `r78drainec.own_n != "0"`, `depth==2` retained as member-shape pins,
  verdict string "…from a body-drain EC", :1818–1839).
- **`r78_dead()` string-truthiness fix present**: `r78_dead` returns
  `res_str` strings (:1000–1004); all three consumption sites use
  `== "false"` (:586, :638, :655). The defective `not r78_dead(x)` form
  never landed — caught mid-fold as the adjudicator records **[M]**.

## 3. Adjudicator claims → receipts (claim-by-claim)

| claim (r78-adjudicator.md / LOG r78 block) | receipt status |
|---|---|
| "92/92 folded battery" | **Strong, two carriers** **[M]**: (a) `corpus/live/runs/love-20261014T215836641142Z` = 92/92 PASS on fold-content bytes (pre-commit 18:58 -0300; its drainec lines already discriminate `own=true/1` vs `own=false/0`); (b) `corpus/live/r79-baseline/freeze/love-runs{,2}/love-20261014T23{5210,5416}*Z` = **92/92 PASS ×2 on a byte-exact `git archive` of committed HEAD `884a4c4`** — post-commit execution evidence on the committed bytes themselves. |
| author "92/92 ×4 + 37/37 ablations" | `r78-author/runs/love-…T21{0544,0613,0635,0943}*Z` all 92/92; disclosed `…T205937122136Z` = 91/92 provenance run present; `ablation.json` = 51 rows, 37 mutated → all caught, 14 base rows clean **[M]** |
| "37/37 re-run against folded battery" (simplifier) | `r78-simplifier/evidence/ablation_vfold.json` = same 51-op matrix, all rows caught, vs `runs-control/love-20261014T211556516761Z` **[M]** |
| "457×100 fuzz 0-div" | `evidence/fuzz_summary.json`: `evaluations: 457100, divergences: 0` **[M]** |
| "146/146 receipts byte-identical" (vfold) | `evidence/compare-author-runs.txt` + the runs-* trees; control-vs-author jitter = same 6 files both directions **[M]** |
| C1 basis (crash at depth 1, not only depth 2) | `r78-boundary.md` §3.1 with cell receipts under `r78-boundary/cells/` (`drainact … depth_before=0`, rc=−11); committed gate re-keyed on `depth_before ∈ {0,1}` + `own_n ≠ 0` **[M]** |
| C2 basis (forgeable drain-EC) | `r78-critic/cells/x1.*`, `x2.*` receipts + §3 demonstration; fix landed (own/own_n everywhere) **[M]** |
| C3 basis (drain_converge without drain) | `r78-critic.md` §4 (H2) + committed conjuncts **[M]** |
| C4 "(verifier re-ran the mutations against the folded gates)" | **No located receipt** — see F4 below **[M]** |
| "67 redundant pins" | **Wrong numeral** — the fold deleted **33** pins (receipt-verified: fold.diff nets 49−16 = 33; the 17 r78 rows carry exactly 375 pins at `1a03b7a`, matching the simplifier's census). No natural count yields 67 **[M]** |
| "the three dispatch_escape rows now pin it" (fold msg) | **Undercount** — **four** rows pin `own=false/own_n=0`: the three contained `*_wp` members plus the uncontained `n_destroy_contacting` (:1213), itself classed `dispatch_escape` **[M]** |
| "45/56 byte-identical + 11 line-token-only" | `r78-author/drift_audit.json`: 112 files, 101 byte-identical, 11 line-token-only (all `.stdout.txt`), 0 semantic, 34 new → cell level 45+11. `r78-baseline.md` independently names the **identical 11 cells** (11/11 match incl. `bc_setpos_wp`) **[M]** |
| adjudicator's own 11-name enumeration | **Defective**: lists 11 tokens but only **10 distinct** — `bc_setpos_unp` appears twice, `bc_setpos_wp` is dropped (count and class still correct) **[M]** |
| "verifier (labrat, swe-2) confirmed falsifications" | `r78-verifier.md` + `r78-verifier/{runs,cells,ablation.json}` exist — two own-process 92/92 runs, 17-cell ×2 re-derivation, 51-row ablation — **all on `1a03b7a`** (pre-fold) **[M]** |
| "stray windowed love run surfaced the risk" | Narrated only in the adjudicator; **no dedicated artifact** under `corpus/live/r78-*` or reports. Recorded in LOG as an r79 proposal (`love.errorhandler` windowed-surface guard). Absence-of-artifact flag, not a contradiction **[M]** |
| siblings 80/80 + 88/88 | author `pygame-…T210706706131Z` (80/80), Godot `…T210716859565Z` (88/88); r78-baseline postland replays LOVE 92/92 ×2 + pygame 80/80 ×2 at 21:11Z **[M]** |
| wave tag | seat reports cite `w18`; adjudicator header cites `w19`; r79 baseline cites `w20`. Label drift across phases, not a content error **[M]** |

## 4. Ledger vs reality

- `LOG.md` r78 block (committed): verdict ADMIT-corr; commits `1a03b7a +
  1fde57d`; C1/C2/C3 folds; the mid-fold `r78_dead` string-truthiness
  fix; scribe's r77-D2-inert record correction; bounded items (C4
  classifier-level fail-open routes, one-point linearity, errorhandler
  windowed surface → r79); seat list complete. **All verified above —
  entry reads true** **[M]**.
- `SCORECARD.md` (committed `HEAD:` version): `| r78 | game-dev-2d |
  nested world:update damage surface | ADMIT-corr | 1a03b7a + 1fde57d |`
  plus depth/calibration "improved" rows consistent with the folds
  **[M]**. (The working-tree SCORECARD additionally carries an
  uncommitted fleet round-1 rewrite — §6.)
- Seat attribution on receipt dirs: all nine `corpus/live/r78-*` trees
  exist and match the nine reporting seats (author, baseline, boundary,
  critic, reviewer, scout, scribe, simplifier, verifier) **[M]**.

## 5. Findings for the canonical judge

- **F1 — adjudicator drift-set enumeration is name-defective.** 11
  tokens, 10 distinct: `bc_setpos_unp` twice, `bc_setpos_wp` dropped.
  Count (11) and class (line-token-only) correct; both underlying
  receipts (author `drift_audit.json`, baseline §raw) name the correct
  11-set **[M]**.
- **F2 — "67 redundant pins" is wrong; 33 is receipt-verified** (fold.msg,
  simplifier census, fold.diff net count, 375-pin total all agree) **[M]**.
- **F3 — "−1181 B" scopes to vfold, not the commit** (+1563 B landed).
  Correctly attributed but misreadable **[M]**.
- **F4 — C4's parenthetical has no durable artifact.** The verifier's
  tree is bounded at 18:47:01 -0300 and its report scopes itself to
  `1a03b7a`; no `corpus/live/r78-*` file postdates the fold commit
  (19:55). The only post-fold-content mutation re-run on record is the
  simplifier's `ablation_vfold.json` — against the **pre-C1–C3** vfold
  variant. Verdict-level fail-closed is supported pre-fold (verifier)
  and on committed bytes (r79-baseline frozen replays), but the specific
  claim "verifier re-ran the mutations against the folded gates" is
  unattributed/unevidenced **[M]**.
- **F5 — "three dispatch_escape rows" undercounts by one** (four rows
  pin `own=false`, incl. uncontained `n_destroy_contacting`) **[M]**.
- **F6 — unrecorded tracked modifications** (§6): `SCORECARD.md` fleet
  round-1 rewrite and the r79 `run_battery.py` arm (+67/−0,
  `phys2d_events.gd` 526 lines) are in the tree uncommitted — expected
  for an in-flight round, but worth a ledger note **[M]**.
- **F7 — wave-tag drift** w18 (seats) / w19 (adjudicator) / w20 (r79)
  **[M]**.

## 6. Uncommitted / stray state at audit

- **Seven r78 seat reports exist only untracked**: `r78-{baseline,
  boundary, critic, reviewer, scribe, simplifier, verifier}.md`. The
  committed set is author (in `1a03b7a`), scout (bundled early inside
  the r77 fold `d48e0fd` — cross-round bundling), adjudicator
  (`884a4c4`). The adjudicator's Files section cites all nine **[M]**.
- **Receipt trees untracked**: `corpus/live/r73-*` … `r78-*` — the
  established pattern since r73 (r72 was the last committed receipt
  round) **[M]**.
- **NEW tracked modifications since the earlier draft**: `SCORECARD.md`
  rewritten (+29/−1, a "Round 1 — current evidence-readiness baseline"
  fleet-calibration block prepended, `reports/fleet-round-1-calibration/`
  also untracked); `corpus/fixtures/run_battery.py` +67/−0 (r79
  `phys2d_events` arm — the r79 baseline's poll caught this first
  tracked write at 23:55:35Z and confirms all four frozen replays
  predate it); new fixture `corpus/fixtures/phys2d_events.gd` (526
  lines) untracked **[M]**.
- **Other in-flight trees**: `corpus/live/{r79-author,r79-baseline,
  r79-scout,gd-scout,r80-scout,integrator-r74-fold,integrator-r75-*}`;
  `reports/round-79/` (scout + baseline + this report); `__pycache__`
  noise **[M]**.
- **Ambient appends**: tracked `corpus/live/r72-simplifier/{snapshots/
  log.txt,watch.log}` carry 7 append-only watcher lines (14:57–15:35
  telemetry + 4 new snapshot dirs) — daemon noise, no semantic content
  **[M]**.
- LOVE error-window investigation: no artifact found in `corpus/live` —
  the stray windowed run is adjudicator-narrated only (§3) **[M]**.

## 7. Gates, out of scope, limits

- Gates: none run by this seat; landed gates and receipts audited.
- Out of scope: no battery/cell re-execution (read-only); no judgment —
  ADMIT-corr stands as the adjudicator's; F1–F7 are record-level items
  for the canonical judge.
- Limits: F4 is an absence claim bounded by `find -newermt` over
  `corpus/live/r78-*` and the verifier's self-scoped report; a re-run
  persisted elsewhere would be invisible. The pre-commit fold-content
  run (21:58Z) cannot prove byte-identity of the battery it ran — the
  gap is closed by the r79-baseline frozen-HEAD replays, not by that
  run. Commit-message numerals checked against object-store diffs and
  landed JSON.

## 8. Artifacts

- This report: `reports/round-79/r79-scribe.md` (supersedes the
  20:56 -0300 draft at the same path).
- Audited: commits `1a03b7a`, `1fde57d`, `884a4c4`;
  `reports/round-78/r78-*.md` (10 files); `LOG.md`/`SCORECARD.md` r78
  blocks; `corpus/live/r78-*` (9 seat trees);
  `corpus/live/runs/love-20261014T215836641142Z`;
  `corpus/live/r79-baseline/freeze/love-runs{,2}/` (frozen-HEAD 92/92
  ×2); `corpus/fixtures/{love_battery.py,love_phys_probe/main.lua}` at
  HEAD vs `corpus/live/r78-simplifier/vfold/`.
