# r97 scribe — CUSTODY HOLDS on f67094bb (12 rows: `stree_lattice_*`)

Seat `SCRIBE` (g2d lane r97, wave-B gate) | host **devin** |
contract `.ufo/waves/shokunin-train-20261016-w23/tasks/g2d-r97-scribe.md`
(lane repo `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`). Audited commit
`f67094bb9cbf665242f85499c59e8b2f59cd5531` ("r97 author: SceneTree
groups/signal-flags/call_deferred lattice"), parent
`d5c05ff8eea42e25f985e8780a55db8b8441c88b` (r96 adjudication), HEAD
`2dcbb6f6ed491e51aa76237b96f80c0b38fe607f` at audit time
(2026-10-16T09:22Z, `git merge-base --is-ancestor f67094bb HEAD` → true,
`git branch -a --contains f67094bb` → `main`). **COMMITTED tree audited;
zero tracked writes; nothing committed, staged, or re-executed.** No battery
run was performed by this seat — re-execution is the verifier's duty, not the
scribe's.

## Custody verdict: HOLDS

Every checkable claim in `reports/round-97/r97-author.md` resolves against the
committed bytes + the live receipt trees (probe/manifest scaffolding is tracked;
`runs*/` receipt trees are ignore-ruled under `corpus/live/.gitignore`), with four prose-precision
findings (F1–F4, all custody-neutral) and two informational notes (F5–F6).
No unclaimed tracked write exists inside the landing commit; the tracked
working tree was clean at audit time.

## Checks performed (all PASS unless marked)

| check | method | result |
|---|---|---|
| Claimed commit exists / ancestry | `git cat-file -t`, `merge-base --is-ancestor f67094bb HEAD`, `branch --contains` | commit resolves; **ancestor of HEAD**, on `main`; parent is exactly `d5c05ff8` |
| Byte-pins on landed files | `git show f67094bb:<f> \| sha256sum` vs report table | **4/4 fixture pins + report pin match**: `stree_lattice.gd` `61954f87…`, `r97_scene_a.tscn` `c86d5674…`, `r97_scene_b.tscn` `7c153f7f…`, `r97_scene_marker.gd` `39763310…`, `r97-author.md` `a1a1b5ae…` |
| Committed bytes ≡ disk | `sha256sum` on disk vs committed blob | **5/5 identical** — landing bytes are live bytes, nothing drifted after the commit |
| Landing commit file set | `git show --numstat --format=` | exactly **6 files, insertion-only** (`+1199/−0`): the 4 fixtures + `run_battery.py` (+65/−0) + the report (+172/−0). No unclaimed path; `project.godot` untouched |
| No unclaimed tracked writes | `git status --porcelain=v1 \| grep -v '^??'` | **empty** at audit time (the report's "pyc restored to HEAD" claim holds: `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` is tracked and clean) |
| Frozen-probe provenance | `sha256sum corpus/live/r97-scout/probes/stree_lattice.gd` | `4dd18e10…`, **896 lines — exactly the report's claimed provenance sha**; scout/boundary `manifest.sha256` + `RECEIPTS.md` present |
| Fold = scout probe + comments + rename | `difflib` on non-comment code lines, scout probe vs committed fixture | **non-comment code differs in exactly 2 lines** — the declared `res://scene_a.tscn`→`res://r97_scene_a.tscn` and `scene_b` renames. 676 code lines both sides; +45 comment lines, +0 code lines. The two arm-body comments the report says it corrected contain **no** restatement of the refuted L10 universal (sentence absent from the landed bytes) |
| Scene fixtures | committed vs `corpus/live/r97-scout/proj/*` | `r97_scene_marker.gd` **byte-identical** to the scout's copy; `r97_scene_a/b.tscn` differ from the scout originals in exactly the one declared `ext_resource` script-path line. Mint-era `scene_a/b.tscn` + `scene_marker.gd` still tracked and untouched by the landing |
| `run_battery.py` arithmetic | AST over `git show f67094bb:…` and parent | insertion-only ✓; **12 `stree_lattice_*` CASES tuples** (11 arms; `group_order` twice, second with `--rev`), every row carries its `--arm=` token; CASES **419 → 431** (see F2); results rows **426 → 438**; receipt row set = CASES(f67094bb) **+ exactly the 7 `probe_*` meta rows** |
| Receipts bind to the landed revision | receipt case names vs CASES at f67094bb / HEAD | receipt == CASES(f67094bb)+7 meta **exactly**; **zero** post-r97 names leaked in (HEAD carries 512 CASES tuples / 509 distinct names, 78 names post-r97; none appear) — the green evidence is on the r97 battery revision, not a later one |
| `expected_errors` += 0 entries | per-row field + run census | every `stree_lattice_*` row carries `expected_errors == []`; census `rows_with_expected_errors = 71` in **all 7** runs with **no** `stree_lattice_*` row in the census → nothing to live-match, and nothing silently allowlisted |
| Floor gate | gate source in committed bytes + per-run receipt value | `"r97_expected_errors_all_matched": all(not e["dead_in_run"] for r in census_rows if r["case"].startswith("stree_lattice_") for e in r["entries"])` — keyed on the round prefix exactly as claimed; **`true` in all 7 runs**; all 12 round gates (`phys2d`+`r87`–`r97`) `true` in all 7 runs |
| Signature live-match (positive control) | committed signature vs frozen scout `runs/r97_<arm>.rep1.out` | **12/12 `in` and 12/12 full-line equality** — the "full-line `^PASS`, byte-equal to the canonical rep1 PASS lines" claim is exact |
| Author receipts resolve | `corpus/live/r97-author/runs/*/verdicts.json` | **7/7 runs present**, each 438 rows; FAIL sets exactly as reported (see table); all 12 r97 rows PASS in all 7 runs → **84/84 row-instances** |
| Comment-only edit, emitted bytes | per-row `output` sha256 across the 7 runs | **`out_uniq = 1` for all 12 rows** — the 12 outputs are byte-identical across the 2 pre-fix and 5 post-fix runs; the census row's output is also **line-for-line identical** to the frozen scout rep1 receipt |
| Cascade attribution | run `084014` vs `090413` on `probe_error_clause_surface` | only **one** discrimination flips: `census_bare_classifier_consistent` false→true; `negative_transition`'s 2 allowlist entries are `matched_lines: 0 / dead_in_run: true` in the failing run and `1/1, dead_in_run: false` in the green one → the second FAIL is a cascade, as the report states |
| Receipt-family census | `rglob('*.out' / '*.err')` | scout **48** top-level `r97_*.rep*` + **36** loadtest = 84 ✓ report's "48 scout + 36 loadtest"; boundary lattice arms **216** (36/mode × 6 modes: quiet/ff1/ff30/ff60/ff120/load) ✓ report's "216 boundary receipts"; **all 426 `.err` files are 0 bytes** and **no `ERROR:` line appears in any of the 426 `.out` receipts** → "ERROR:-clean with 0 B stderr" holds for the lattice arms |
| Green-run arithmetic | verdict sequence | 5 green / 7 runs; 3 greens on final bytes; **longest consecutive green streak = 2** (see F3) |

### Author run table (measured from receipts, not copied)

| run dir | claimed | measured |
|---|---|---|
| `…T082702326496Z` | PASS 438/438 | PASS, 438 rows, 0 FAIL |
| `…T083244672622Z` | PASS 438/438 | PASS, 438 rows, 0 FAIL |
| `…T084014089634Z` | FAIL 437/438 `negative_transition` | FAIL, 438 rows, 2 FAIL (`negative_transition`, `probe_error_clause_surface` cascade) — see F4 |
| `…T084924888991Z` | PASS 438/438 | PASS, 438 rows, 0 FAIL |
| `…T085730720181Z` | FAIL 437/438 `nav_lattice_region` | FAIL, 438 rows, 1 FAIL (`nav_lattice_region`) |
| `…T090413067379Z` | PASS 438/438 | PASS, 438 rows, 0 FAIL |
| `…T091032696916Z` | PASS 438/438 | PASS, 438 rows, 0 FAIL |

No r97 row failed in any run; no pin was weakened to force green; the two FAIL
rows are pre-r97 rows this round does not touch (verified: neither is a
`stree_lattice_*` row; `nav_lattice_region` is cited as an r91 fixture and
`negative_transition` as the r89-documented scene-readiness class in the
author report's flake accounting, which I did not re-derive).

## Working-tree / chain custody

- Landing was replayed on top of `d5c05ff8` (r96 adjudication, 05:53), not on
  the report's stated base `89f85ed8` (r96 author, 05:04). That is consistent:
  the report says "nothing committed" and names HEAD as of author-finish time.
  `git diff --numstat 89f85ed8 d5c05ff8` = `LOG.md` + `reports/round-96/*` only
  — **zero fixture/battery bytes** — so the author's green evidence transfers to
  the landed tree unchanged.
- The landing's parent chain is `89f85ed8 → d5c05ff8 → f67094bb → 9d421fb2 →
  254e79dd → 2dcbb6f6` (HEAD). Later rounds (r98–r100) rewrote
  `run_battery.py` but **not** any r97 file: the r97 fixture blobs at HEAD are
  byte-identical to the landing blobs.
- Nothing in this audit wrote to a tracked path; all scratch is under
  `corpus/live/r97-scribe/`. Precise ignore state (checked with
  `git check-ignore -v`): `corpus/live/.gitignore` rules `runs*/`,
  `**/__pycache__/`, `**/.godot/` — the author's 7 run dirs are ignore-ruled,
  my audit dir is **not** ignore-ruled and therefore shows as untracked (`??`).
  Zero tracked writes, zero staged paths, nothing committed; the 30 tracked
  files under `corpus/live/r97-*` are scout/boundary scaffolding committed by
  earlier rounds, none of them touched by the landing commit or by this seat.

## Findings

- **F1 (prose precision — line counts stale, hash correct).**
  `r97-author.md`'s landed-files table annotates `stree_lattice.gd` as
  "`61954f87…` (**937 lines**)" and the fold as "**+41 lines**". The landed
  bytes are **941 lines = +45** over the 896-line frozen probe (676 code lines
  both sides; +45 comment lines; the 2 renamed path lines). The **sha256 pin is
  the load-bearing figure and it matches the landed bytes**; the count appears
  to be the pre-fix draft that the seat's own 4-line arm-comment fix outdated
  (the hash was refreshed, the count was not). Custody unaffected.
- **F2 (prose precision — CASES count off by one on both sides).**
  The report (and the landing commit message) say "CASES 420 → 432 tuples". AST
  over the committed file: **419 → 431** (delta +12 ✓). A count of
  `^    (`-indented lines in the same file gives 432 — one of them being the
  unrelated `(run_dir / "verdicts.json")…` write at line 4892 — the likely
  origin of the figure; the load-bearing delta (+12) and the results-row
  arithmetic the claim is attached to (**426 → 438 incl. 7 meta**) are exact.
  The parent figure also contradicts `r96-author.md`'s own landed "CASES 359 → 419".
- **F3 (commit-message overstatement; the report's table is honest but its
  closing phrase is loose).** The landing commit message claims "438/438 x3
  consecutive on final bytes". Measured sequence: PASS, PASS, FAIL, PASS, FAIL,
  PASS, PASS → 3 greens on final bytes, **longest consecutive green streak = 2**
  (5 green / 7 total). The report's own table lists both FAIL runs correctly,
  but its sentence "three consecutive at the end (`090413…`, `091032…`;
  `084924…` is a third green on the same bytes)" is internally loose:
  `084924` is separated from the last two by the `085730` FAIL. Not a custody
  defect — an arithmetic/disclosure precision defect on the commit message that
  the orchestrator authored.
- **F4 (tally convention, disclosed).** The report's table records run
  `084014` as "437/438"; the receipt's literal tally is **436 PASS / 2 FAIL /
  438 rows**. The second FAIL is disclosed in the same paragraph as the
  `probe_error_clause_surface` cascade, and the cascade is verified (F-table
  row above: one discrimination flips; the affected allowlist entries are
  dead-in-run). So "437/438" is a disclosed-tally that counts the cascade as
  green — accurate as intent, imprecise as arithmetic. No r97 gate was affected
  (`r97_expected_errors_all_matched` and all round gates `true` in that run).
- **F5 (informational — wave-B siblings outstanding).** At audit time
  (2026-10-16T09:22Z) `corpus/live/r97-{verifier,reviewer,simplifier,critic}`
  directories existed (concurrent lanes in flight) but `reports/round-97/`
  held only `r97-author.md`, `r97-scout.md`, `r97-boundary.md`. **No r97
  verifier / critic / reviewer / simplifier verdict is filed**, so this scribe
  report is the first wave-B artifact for r97 and the landing is not yet gated
  by the other four seats. Not a defect of the landing; a disclosure of what
  "wave-B gate" does and does not yet cover.
- **F6 (informational — inherited, not r97).** `nav_lattice_region`'s
  first-query path divergence is a newly observed class recorded only in the
  author report; the row is an r91 fixture, untouched by this landing, and it
  passed byte-exact in both later runs. Left standing as a hazard note for a
  future boundary/mutation look.

## Not verified by this seat (scope, stated explicitly)

- **No re-execution**: no Godot run, no battery run, no mutation/forgery
  sensitivity on the signature gate — those are the r97 verifier's and critic's
  duties, and I did not rerun work to decorate this report.
- **No re-derivation of the 12 law payloads** beyond matching the shipped
  signatures to the frozen scout receipts and the author's own run outputs.
- **The boundary verdicts themselves** (L10 refutation, ordered snapshot,
  frame-epoch UNIQUE key, priority-inertness) are taken as the r97-boundary
  report's claims; I verified only that the cited sections exist (§2.3 refutation
  headline, §3.2 priority modes, §4 `callmut` block, §6.2 epoch sharpening) and
  that the landed fixture's comments encode them.
- **Sibling wave-B receipts** were observed as present/absent only; their
  contents were not read or graded.

## Blockers

None. Custody holds; the landing is byte-pinned, insertion-only, receipt-backed,
and unclaimed-write-free. Open (not blockers): the four outstanding r97 wave-B
verdicts (F5), and the three prose/commit-message precision items (F1–F3) that
the orchestrator may correct in the adjudication note — none of them touch
landed bytes or gates.

## Artifacts

- Report: `reports/round-97/r97-scribe.md` (this file; untracked, not committed)
- Evidence: `corpus/live/r97-scribe/audit/r97_audit.py` (read-only auditor),
  `corpus/live/r97-scribe/audit/r97_audit.json` (machine record of every check
  above, incl. per-run FAIL sets, gate values, receipt census, byte pins)
