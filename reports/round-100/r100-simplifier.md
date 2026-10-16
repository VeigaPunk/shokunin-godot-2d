# r100 simplifier — the GUI/input lattice landing `2dcbb6f6` re-verifies **25/25 r100 rows** and the whole battery is **519/519 PASS on its own bytes**; exactly two provable weight deletions exist: the landing's own **2 duplicate crash-sentinel CASES rows** (already deduped upstream at `9ede7c50`, independently re-verified here) and a **5-line dead `--arm`/`arm` path** in `r100b_seq.gd`; every other deletion candidate is an instrument, a claim, or provenance

Seat `SIMPLIFIER` (LEAF) | lane `g2d-r100` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, `--headless`, 60 tps,
`RendererDummy`), Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
**Work commit audited: `2dcbb6f6`** (r100 author landing, parent `254e79dd`) —
lane HEAD was `2dcbb6f6` when the audit began and the tracked tree was clean.
**The shared tree moved repeatedly mid-session** (sibling lanes land
concurrently): `9ede7c50` *"r97-r100 integration fix: dedupe crash sentinel
CASES rows (509/509 unique)"* (06:4x), then `619ad7e0` (pyc refresh),
`2ac38451` (r97 adjudicate), `f02ee348` (r98 adjudicate) at report time.
**Every run of record below is pinned to an explicit commit in a private archive
checkout** (`git archive <sha> corpus/fixtures`), never the shared working tree;
the receipts name the exact tree sha per run.

**`lsp` disclosure.** No `lsp` device in this dispatch and no GDScript/Python
language server on this host — `references`/`definition`/`rename` were
**unavailable for every file**. No rename/symbol work was required. Every
deletion candidate below is a *textual* dead path, proved by (a) a complete
occurrence enumeration over the file, (b) fresh-process before/after runs in the
battery's exact launch shape, and (c) a full whole-battery run on each
byte-state.

**Host is shared and was hostile to long-lived background work.**
loadavg 10–16 for the session (≈10 sibling lane batteries running
concurrently). Three of this seat's own whole-battery attempts were **reaped by
the host ~3 min after launch** (both members of a pair dying at the same
wall-clock instant — ≈06:30 and ≈06:35 local, i.e. ≈09:30Z/09:35Z; log
truncated, no traceback). All runs of record were relaunched in the
tool-supported foreground-of-background-shell shape and completed. **`/tmp` is a
tmpfs with `usrquota` and is exhausted for this user** (a direct 800 MiB write
stops at 197 MiB with `EDQUOT`), so the contract's *fresh git archive checkout
under /tmp* is hosted at **`/var/tmp/r100-simplifier/<tree>/`** (same fresh
`git archive` extraction, root filesystem, 728 GB free). The lane repo root was
used for exactly one exploratory run (`R0`, before the tree-move was detected);
**every run of record is from a pinned private checkout**.

---

## 1. What is under audit

| item | value |
|---|---|
| landing | `2dcbb6f6` — `corpus/fixtures/r100_gui.gd` (780 L, `dd826f6e…`), `r100b_phase.gd` (520 L, `49298e6c…`), `r100b_emul.gd` (37 L, `31087e78…`), `r100b_seq.gd` (790 L, `4718a19e…`), `run_battery.py` (`+134/−2` per `git diff --numstat 254e79dd 2dcbb6f6`), `reports/round-100/r100-author.md` |
| claimed | commit msg `+132/−0`, *"green 451/451 x2"*; report *"CASES 419 → 444 tuples (results rows 426 → 451 incl. the 7 meta probes)"*, *"444 CASES names, 444 distinct"*, *"removing the three inserted regions restores the original file bytes byte-for-byte"* |
| landed (measured) | **CASES 512** (509 distinct: `crash_spontaneous_sigabrt` ×3, `crash_self_sigkill` ×2), **519 battery rows** (512 + 7 meta) on `2dcbb6f6`; the 25 r100 rows are byte-identical to the author's worktree rows (order-sensitive), and the landed file additionally carries r97/r98/r99's **65** rows |
| upstream fix | `9ede7c50` (`+3/−2`) dedupes **all three** duplicate crash rows (509/509 unique), keeping the tail copies — the same fold class found here, landed by the integration lane while this seat ran |

The claim/landing gap is mechanical, not mysterious: the author's worktree
(`game-dev-2d-shokunin-wt-r100`, branch `wt-r100` @ `2d562282`, parent
`89f85ed8`) really does hold **CASES 444 / 444 distinct / 451 rows** and its
receipts (`corpus/live/r100-author/`, 3 runs, 451 rows each) are receipts for
*that* file. The commit that landed on main was re-applied on top of `254e79dd`
(r99, CASES 485), and that re-application is what produced the two duplicate
tuples (`+27` tuples, not `+25`). The landed 512-CASE bytes were first run
whole by the **r100-reviewer lane** at 06:25 (`corpus/live/runs/20261016T0925*`,
519/519 PASS, 5 crash rows — independently re-measured by this seat's `R1` at
06:46, same result); the *author's* receipts remain worktree-only (§4).

## 2. Verdict and findings (ranked)

**Verdict: PASS on the audited landing's own bytes (519/519, `R1`), with two
provable weight deletions — one already landed upstream, one residual — and no
other fold.** 0 blockers. Nothing committed by this seat; the patches are
unapplied (`§5`).

| # | finding | severity | evidence |
|---|---|---|---|
| F1 | **The landing's hunk added 2 exact-duplicate CASES rows** — `crash_spontaneous_sigabrt` (indices 459/481/**508**) and `crash_self_sigkill` (482/**509**), byte-identical 5-tuples (tuple shas `b4799da3…`, `e5ccc504…`). `254e79dd → 2dcbb6f6` is `+134/−2` and adds **27** tuples: the 25 r100 rows **+ these 2 duplicates**. They are not claims: the same probe/exit/signature already runs, the crash meta consumes `crash_records` as a name-keyed dict (last wins) and the probe's stdout is one fixed marker line. Deleting the 2 landing-added copies: **−1 line, −2 rows, −2 Godot launches (~2.0 s measured)** — proven claim-neutral in §4 (`R1`↔`R3`: 0 claim-bearing diffs, 0 FAILs, crash-meta payload identical) | low (weight) | `fold-candidates.txt`, `census.py`, `compare-r1-vs-r3.txt` |
| F2 | **`r100b_seq.gd` carries a dead `--arm` alternate path and a dead `arm` carrier (−5 lines).** `_initialize` parses `--arm=` into the file-scope `arm`; `_run` then overwrites `arm` on every loop iteration before the `match` — the parsed value is **unobservable**. With it gone, `arm` is a loop-local carrier (`arm = a` then `match arm:`), so the declaration and assignment go too (`match a:`). No row ever passes `--arm` to this fixture (its only 2 consumers pass `--clean=0/1`); the fixture is a *generated* copy of the frozen scout probe (`make_seq.py`) and this is the generator's leftover | low (dead path) | §3, §5; `rows-base/`, `rows-folded/`, `rows-folded2/`, `compare-r4-vs-r3.txt` |
| F3 | **The r99 landing had already duplicated `crash_spontaneous_sigabrt`** (`254e79dd`: CASES 485, 484 distinct — its insertion also split the shared crash line). Same class as F1, one round earlier; the r99 lane owns it, and `9ede7c50` removed it upstream. Recorded, not claimed | info (cross-lane) | `fold-candidates.txt` census table |
| F4 | **Evidence provenance: the landing's count claims describe the author's worktree, not the landed bytes** (444/444/451/`+132−0`/byte-restore vs landed 512 CASES (509 distinct) / 519 rows / `+134−2`). The 25 r100 rows themselves are byte-identical between worktree and landing (order-sensitive), so the r100-row evidence transfers; the *whole-battery* claims do not. The landed bytes' own whole-battery receipts are the r100-reviewer's two 06:25 runs (`corpus/live/runs/20261016T0925*`, 519/519) and this seat's `R1` (§4). Flagged for critic/verifier/adjudicator — this seat neither judges nor fixes it | medium (claim accuracy) | §1, `census.py`, `r100-author/` receipts (worktree), `R1`, `corpus/live/runs/20261016T0925*` |
| F5 | **Integrity, all clean:** the 4 fixture shas cited in the harness comment match the committed bytes exactly; all 25 r100 rows' flags are read by their fixtures (no phantom row, no `--offy`-class unread flag); 25/25 r100 signatures appear in real scout/boundary receipts (24–50 hits each); no r100 row's signature is a duplicate or a substring of another row's; the 3 `expected_errors` entries are live in every run (`dead_entry_count=0`); the r100 floor gate is present, prefix-correct and exercised | info (integrity) | `fold-candidates.txt`, `pin-census.txt` |
| F6 | **The `.pyc` is a coherent derived artifact, not drift.** The committed `__pycache__/run_battery.cpython-314.pyc` at `2dcbb6f6` embeds the committed source's size (507894) — it was regenerated with the landing (the author report's *"restored to HEAD bytes"* wording is wrong, the artifact is right). The upstream dedupe then made it stale (source 507480) and the wave refreshed it (`619ad7e0`, r100-reviewer F4) — the refresh is the correct follow-up, not a fold | info | pyc header read (this seat), `git log` |

## 3. Fold candidates audited — PROVEN / REFUTED per fold

Method: (a) AST census of `CASES` across `89f85ed8 → 2dcbb6f6` (counts, exact
5-tuple duplicates, multiset diff, identical-launch groups, substring
relations); (b) occurrence-classified scans of the 4 new fixtures (dead stores,
unused helpers, unused parameters, unread flags); (c) pin↔emission census over
503 scout/boundary receipt files; (d) fresh-process execution for every
candidate that survives (a)–(c), in the battery's exact launch shape; (e) a full
whole-battery run on each byte-state.

| # | candidate | verdict | proof / reason |
|---|---|---|---|
| SP1 | **2 duplicate crash rows added by the landing's hunk** (F1) | **FOLD PROVEN — −1 line / −2 rows / −2 launches** (patch hunk 1) | Identical 5-tuples of rows already present (tuple shas `b4799da3…`/`e5ccc504…`); no distinct claim is removed (516 distinct cases before and after); `R1`(519) ↔ `R3`(517): **0 claim-bearing diffs, 0 FAILs**, crash-meta payload identical, census `rows_with_expected_errors` 80→79 (the duplicate's own allowlist entry) with `dead_entry_count=0` both. Already superseded upstream: `9ede7c50` removed all three duplicates (keeping the tail copies) and `R4` re-verifies that state green (516/516) |
| SP2 | **`--arm` parse in `r100b_seq.gd` `_initialize`** (3 lines) | **FOLD PROVEN — −3 lines** (patch hunk 2) | `_run` unconditionally assigns `arm` before every `match` (occurrence census: `arm` at decl / parse / loop-assign / match-subject only) → the parsed value is never observed; no row passes `--arm` to this fixture; 2 rows × 3 reps on base vs folded: **stdout byte-identical** (`2fc9a28f…` / `bb1e7676…`), rc identical |
| SP3 | **`var arm := ""` + `arm = a` carrier** (2 lines, F2b) | **FOLD PROVEN — −2 lines** (patch hunk 3) | After SP2 the name is a loop-local; `match a:` is the same dispatch. 2 rows × 3 reps base vs folded2: **stdout byte-identical**; full battery `R3` (folded) vs `R4` (unfolded, same fixture bytes): 0 claim-bearing diffs, 25/25 r100 rows PASS, 7/7 meta PASS |
| SP4 | **The r99 duplicate** (`crash_spontaneous_sigabrt` at `254e79dd`) | **FOLD REAL, not this lane's** (F3) | Same proof class as SP1; the r99 lane's landing introduced it and `9ede7c50` has already removed it. Not claimed here |
| SP5 | `r100b_phase.gd` 9th arm `startup` (no row uses it) | **REJECTED** | A receipted instrument of record, deliberately excluded from rows because it prints wall-clock `t=` (author §3, boundary §7); `corpus/live/r100-boundary/runs/probes/{quiet,load}/r100b_startup.rep{1,2,3}.out` exist. r95-SP11 precedent: an uncovered arm with receipts is not dead code |
| SP6 | `_:` fallbacks (`r100_gui.gd` → `_cell_census()`; `r100b_seq.gd` → `pass`; `r100b_phase.gd` → prints `unknown arm=`) | **REJECTED** | Unreachable adapters by construction, but they are the loudness/default class (r95-SP11): a typo'd arm cannot pass — the row's signature would not match its own launch. Deleting them changes behavior for a hypothetical bad arm and edits frozen fixtures for no weight win |
| SP7 | The 58-line r100 harness comment block | **REJECTED** | It *is* the fold encoding: boundary verdicts applied, the corrected drag law (`|Σ relative| > 10`), the excluded `startup` arm, receipt counts, insertion-position rationale. Deleting it orphans every justification (r91-SP6 / r92-SP9 / r95-SP7 class). One gap recorded: it does not itself name the excluded `startup` arm (the author report does) — a doc note, not a deletion |
| SP8 | The 3-entry allowlist + `r100_expected_errors_all_matched` gate | **REJECTED** | Both proven live/loud by `R1`/`R3`/`R4` (`dead_entry_count=0` in all three; the gate covers both r100 prefixes and is inside `sf_discriminations`, so it is load-bearing for the meta verdict). A single generic dead-entry gate replacing the r87–r100 family is a cross-round refactor that would change *other* rounds' failure surface — out of this lane's scope, and the per-round named gate is the repo's convention |
| SP9 | `r100b_seq.gd`'s stale header (`godot … r100_gui.gd -- --arm=<cell>`, *"One cell per process … prints one final PASS line"* — both false for a 14-cell sequential fixture) | **REJECTED as a fold; recorded as a doc defect** | It is the generator's inherited provenance (the fixture is a byte-copy of the frozen boundary probe, sha cited in the harness comment); the repo convention is to correct wrong wording *row-side / harness-side*, never by editing a frozen fixture (r100 author §1 did exactly that for the scout's drag wording) |
| SP10 | `r100b_seq.gd` as a whole (785 L, 714 non-blank lines shared with `r100_gui.gd`) | **REJECTED** | It is the only artifact that can produce the `seq_clean`/`seq_noclean` rows (single-process contamination chain, boundary §18); the duplication is the probe's construction, and the bytes are frozen provenance (r95-SP9 class) |
| SP11 | dead stores / unused helpers / unused params / unread flags in the 4 new fixtures | **NONE FOUND** | Two independent scans (scope-aware occurrence classification; low-occurrence enumeration) over 2127 fixture lines: 0 dead stores, 0 unused helpers (only engine callbacks `_initialize`/`_run`/`_input`/`_gui_input`/`_get_drag_data`/`_can_drop_data`/`_drop_data`, all engine-invoked), 0 unused parameters, 0 unread flags. Scanner limits noted: no cross-file call graph, no type-flow analysis |
| SP12 | *the honest negative* | **no other fold** | Nothing else survives (a)–(e): every remaining emitted field is either a pinned claim or the unpinned discovery surface that produced the pins |

**Conclusion.** The landing carries exactly two provable weight deletions (SP1,
SP2+SP3 = −6 lines, −2 rows) and one cross-lane duplicate (SP4, already
landed). Everything else that looks removable is an instrument (SP5/SP6),
provenance (SP7/SP9/SP10), or a gate that is the loudness surface (SP8). The
next deletion (any of SP5–SP10) would harm the coverage or provenance axis —
the seat stops here.

## 4. The narrow check — three pinned whole-battery runs

All three runs: `python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot`
from a **private archive checkout** of the named commit, `timeout 3600`, one
fresh process per row, 60 tps, headless; run dirs under
`/var/tmp/r100-simplifier/<tree>/runs/<stamp>/`.

| run | tree (pinned) | `run_battery.py` sha | CASES / distinct | rows | verdict | census rows / dead | r100 rows | crash rows |
|---|---|---|---|---|---|---|---|---|
| **R1** | **`2dcbb6f6`** (audited landing) | `86a1aef8…` | 512 / 509 | **519** | **PASS 519/519**, 0 FAIL | 80 / 0 | 25/25 | 3+2 |
| **R3** | `2dcbb6f6` + this seat's patch (SP1+SP2+SP3) | `dcec248e…` | 510 / 509 | **517** | **PASS 517/517**, 0 FAIL | 79 / 0 | 25/25 | 2+1 |
| **R4** | `9ede7c50` (current HEAD, integration dedupe) | `35233c8b…` | 509 / 509 | **516** | **PASS 516/516**, 0 FAIL | 78 / 0 | 25/25 | 1+1 |

Comparisons (`compare.py`, `results` verbatim from each `verdicts.json`):

- **R1 ↔ R3 (the fold proof):** 519 → 517 results; **cases only in one side: 0
  (the removed rows are exact name-duplicates of retained rows)**;
  **claim-bearing diffs on common cases: 0** (verdict, exit, signature, script,
  flags compared per case); 0 FAILs both sides; all 7 meta rows PASS both sides;
  `probe_spontaneous_crash_classification` **payload identical** (the meta's
  last-wins record is the same claim on either side); `probe_error_clause_surface`
  discriminations **unchanged**, census `80 → 79`, `dead_entry_count 0 → 0`.
- **R4 ↔ R3:** 516 vs 517 (the one extra row is the r99 duplicate that `R3`
  still carries and `R4` no longer does); **0 claim-bearing diffs**; all meta
  PASS; census `78 → 79`.
- **R1 re-measures the landed bytes green** (519/519,
  `dead_entry_count=0`, all `sf_discriminations` true, 25/25 r100 rows PASS) —
  the third independent whole-battery run of those bytes: the r100-reviewer lane
  ran them twice earlier (`corpus/live/runs/20261016T092554544775Z`,
  `…092557629472Z`: 519/519 PASS, 25/25 r100, 5 crash rows), and the author's
  own receipts are worktree-only. The author's documented load-flake classes
  (`negative_transition`, the `census_bare_classifier_consistent` coupling) did
  **not** fire in any of the three landed-bytes runs — loadavg 10–16 vs the
  author's 51–66; recorded, not claimed as a fix.

Row-level (fresh-process, battery launch shape, 3 reps each;
`rows.py` receipts):

| row | base stdout sha | folded stdout sha | rc | stderr |
|---|---|---|---|---|
| `r100b_seq_clean` | `2fc9a28f0dc2a44f…` | `2fc9a28f0dc2a44f…` | 0 = 0 | only GDScript backtrace line numbers (`_cell_render 762→757`, `_run 116→111`, `_cleanup 135→130`) |
| `r100b_seq_noclean` | `bb1e76767fcd3bf0…` | `bb1e76767fcd3bf0…` | 0 = 0 | same class |
| `crash_spontaneous_sigabrt` | `094b4251cac9b79d…` | `094b4251cac9b79d…` | −6 = −6 | identical |
| `crash_self_sigkill` | `094b4251cac9b79d…` | `094b4251cac9b79d…` | −9 = −9 | identical |

The stderr shift is the only non-byte-neutral consequence in the whole patch,
and it is verdict-inert by construction: no r100 row carries `required_stderr`
(the only three stderr-pinned rows are `geo2d_lattice_lineempty`,
`nav_lattice_teardown_crash`, `r92_tilemap_nullts_crash`), and
`classify_process` inspects only lines containing `ERROR:` (the allowlisted
`ERROR: Parameter "t" is null.` line is unchanged). Confirmed end-to-end by
`R3`/`R4` (0 claim-bearing diffs).

## 5. The fold proposal — patches (unapplied) and how they were proved

| patch | against | hunks | delta | applies |
|---|---|---|---|---|
| `corpus/live/r100-simplifier/r100-simplifier-fold-2dcbb6f6.patch` | the **audited landing** `2dcbb6f6` | 4 | `run_battery.py` −1 line / −2 rows; `r100b_seq.gd` −5 lines | `git apply --check` clean; result == the proven folded tree byte-for-byte |
| `corpus/live/r100-simplifier/r100-simplifier-fold-9ede7c50.patch` | **current HEAD** `9ede7c50` | 3 | `r100b_seq.gd` −5 lines (the F1 hunk is already satisfied upstream) | `git apply --check` clean |

Proof chain for the patch of record (SP1+SP2+SP3 on `2dcbb6f6`):

1. **Arm/row level** — 4 targeted rows × 3 reps on base and folded (the 2 seq
   rows additionally on folded2): stdout byte-identical, rc identical (§4 table).
2. **Whole battery, before** — `R1` on the untouched landing bytes: 519/519
   PASS.
3. **Whole battery, after** — `R3` on the patched bytes: 517/517 PASS, and
   **0 claim-bearing diffs** vs `R1`; meta payloads identical.
4. **Independent corroboration upstream** — `R4` on `9ede7c50` (the integration
   lane's stronger dedupe): 516/516 PASS, 0 claim-bearing diffs vs `R3`.
5. **Patch integrity** — applying the patch to a fresh archive of `2dcbb6f6`
   reproduces the folded tree byte-identically (`diff -r --brief` empty; the
   patch is generated from exactly those two trees).

**If the operator applies the residual (`9ede7c50`) patch, two harness-comment
lines should move with it** (they are inert otherwise): the
`r100b_seq.gd sha256 4718a19e…` citation becomes `e77dc55c…`, and the
parenthetical *"(… no fixture folds)"* becomes false once the fixture carries
the declared diff (r95 precedent: the sha lines were updated with the patch).
Nothing else in the comment references the fixture's bytes.

## 6. Remaining risks / blockers

- **The shared tree is moving under every seat.** HEAD advanced `2dcbb6f6 →
  9ede7c50 → 619ad7e0 → 2ac38451` during this session, and the working tree was
  briefly *not* HEAD (an integration edit was in flight). Any seat that runs
  the battery "from the lane repo root" is running whatever bytes happen to be
  there. All receipts here name a pinned commit and were produced from private
  checkouts.
- **F1 is landed upstream in a different shape than this seat's patch** (upstream
  kept the tail copies and removed all three duplicates; this seat's F1 hunk
  removes the two landing-added copies). Both are claim-neutral (proved), so the
  divergence is cosmetic — but the residual patch above is the only one that
  applies to HEAD.
- **F2/F2b stale the fixture↔frozen-probe byte identity** for `r100b_seq.gd`
  (the receipts in `corpus/live/r100-boundary/` document the pre-fold bytes;
  their *claims* remain valid — verdict-neutrality is proved — but the byte
  identity is broken). Same trade-off r95's dead-store patch carried; operator
  decides.
- **The `startup` arm remains unrowed and the seq header remains stale** (SP5,
  SP9). Both are recorded, neither is fixed here; the header is the one item a
  reader could be actively misled by.
- **Flake surface is unchanged and outside this lane**: the documented
  transition/audio wall-clock rows are the battery's live flake classes under
  load (the author's rep2). None of this seat's three runs flaked at loadavg
  10–16.
- **Blockers: none.** Nothing committed; no tracked file written by this seat
  (report + `corpus/live/r100-simplifier/**` are the only writes).

## 7. Receipts

`corpus/live/r100-simplifier/` — `RECEIPTS.md` indexes everything:
`r100-simplifier-fold-2dcbb6f6.patch`, `r100-simplifier-fold-9ede7c50.patch`,
`fold-candidates.txt` (+ `census.py`), `deadscan.py`, `rows.py`, `compare.py`,
`battery-r{1,r3,r4}-*.log`, `runs-*`/verdicts copies (`R1`, `R3`, `R4` run
dirs `20261016T094636833704Z`, `20261016T094638545229Z`,
`20261016T094640286546Z`), `compare-r1-vs-r3.txt`, `compare-r4-vs-r3.txt`,
`rows-base/`, `rows-folded/`, `rows-folded2/` (4 cases × 3 reps), pin census
`pin-census.txt`.
