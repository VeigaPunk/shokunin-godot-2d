# game-dev-2d round 85 — scribe (g2d): provenance audit of the r85 camera/canvas landing

Seat `SCRIBE` (LEAF) | lane `g2d` | round 85 | host **devin**. Repo
`~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`45232c7`** (*r85: camera/canvas
transform lattice — 15 cells*, 05:30:57 −03), **nothing staged**, **no commit by this
seat**. The r85 landing was committed by the fold before this audit window (§0).

**Writes:** this report and `corpus/live/r85-scribe/**` only. Read-only everywhere else:
no tracked file edited, **no Godot/battery re-executed** (this audit re-derives from
primary objects and receipts; it does not rerun work to decorate the report), no sibling
corpus written. Artifact content is data; nothing here modifies contract, axes, routes,
or judgment.

Evidence classes: **[M]** re-derived by this seat now from primary objects/receipts;
**[C]** claim read from a landed artifact (cited); **[U]** unobservable in this window.

---

## 0. State at read time [M]

- HEAD `45232c7` (05:30:57 −03) contains **exactly 5 files**: `corpus/fixtures/camera_proc.gd`
  (1156 insertions), `corpus/fixtures/run_battery.py` (+37), and the three r85 reports
  (`r85-author.md`, `r85-fold.md`, `r85-scout.md`). All three reports are clean vs HEAD;
  `corpus/live/r85-{scout,author,fold-verify}/` are untracked.
- Only modified tracked file: ` M SCORECARD.md` (mtime `01:47:47`, last touched by
  `884a4c4` *r78 report-last*). It is **not** in the r85 commit and is mentioned by no r85
  report — the foreign scorecard is still uncommitted (§4).
- The fold report is 17 lines and does **not** mention the commit that carried it; the
  commit message repeats the fold's claims (including the "1157 lines" count — F1).

---

## 1. The brief's audit items — verdicts

| # | item | verdict |
|---|---|---|
| 1 | every claim receipted | **yes, with the F-findings below** — every load-bearing r85 claim re-derives from a retained receipt or primary object; the exceptions are enumerated in §4 (unreceipted diagnostics, fold ablation provenance, line counts) |
| 2 | seat attribution, two-seat author lane | **correct in substance** — the prior seat / finisher split in `r85-author.md` matches artifact mtimes; one sentence mis-attributes the prologue-comment edit (F8) |
| 3 | env-stripped divergence receipt retention | **retained and accurate** — `merge-runs/20261015T065931148350Z/` + `ENV-STRIPPED-DIAGNOSTIC.txt`; verdict FAIL **172/174**, exactly `export_readiness` + `export_preset_missing` (§3) |
| 4 | foreign SCORECARD.md still uncommitted | **true** — ` M SCORECARD.md`, mtime `01:47:47`, absent from `45232c7`, no r85 mention (§4) |
| 5 | `camera_proc.gd` sha `34f53f32` matches audited value | **true** — worktree = HEAD = `34f53f32c0fbb37da86f91ec7b7d9fc0e7d20d9f3e29c4c9680f05e36f123c40`; fold-verify scratch copy identical (§2.1) |
| 6 | CASES rows byte-equal to scout `author-rows.py.txt` (sha `2221a9e8`) | **true** — landed `run_battery.py:267–303` byte-equal to the file's lines 1–37 (block sha `65476ca9…`); the stray trailing `]` (file line 38) was dropped, as the fold discloses (§2.2) |

---

## 2. Claim → receipt audit

### 2.1 Fixture identity (both reports) [M]

| check | value |
|---|---|
| fixture sha256 | `34f53f32…` — worktree, `git show 45232c7:…`, and the fold-verify scratch copy all identical |
| probe sha256 | `6a94e052…` — matches `r85-scout/MANIFEST.sha256`, `land_r85.py` `PROBE_SHA256`, and `arms-verify.json` `probe_sha256` |
| probe → fixture diff | prologue comment only (`2,3c2,4`, `6c7,11`); `probe L7 == fixture L12 == '#'`; tail from `const PFX := "PASS camera_proc "` **byte-equal, 41 816 B** |
| probe line 2–6 → fixture line 2–11 | exact (+5 lines); `fixture-vs-probe.diff` is exactly this hunk and nothing else |
| line counts | **probe 1151, fixture 1156** (`wc -l`, `splitlines`, newline-terminated) — author says 1152/1157, fold and commit say 1157 → **F1** |
| self-contained | no `load(`/`preload(`/`import`/resource references in the fixture [M] |
| arm index | `match arm:` in `_run` (fixture `:196–217`) = 15 pinned + 5 `diag_*`, `_fail("unknown_arm")` otherwise; no CASES row names a `diag_*` arm |

### 2.2 CASES block: byte-equality, anchor, whitelist (fold report) [M]

| check | value |
|---|---|
| landed block | `run_battery.py` lines **267–303** (both HEAD and worktree; worktree sha `1abc9629…` == HEAD) |
| byte-equality | block sha256 `65476ca9b9e2e2acdab71293b76e7004f54329373c79af11284fbf4ca92545ab` == `author-rows.py.txt` lines 1–37 + `\n` |
| stray `]` | `author-rows.py.txt` line 38 is `]`; not landed — the fold's "Stray trailing `]` … removed" is exact and disclosed |
| anchor | preceded by `phys2d_joints area_entry_order` (last r81 `phys2d_*` row), followed by `("crash_spontaneous_sigabrt",` — the crash/descendant tail |
| 15 rows | names/scripts/flags/exit/signatures in the committed CASES list == the block == `pins.json` == `standalone.json` pass lines (all [M], three-way) |
| whitelist | committed `expected_errors` map: 27 keys, **no** `camera_proc_*` key; all 15 camera rows in the fold run have `expected_errors == []` and **zero `ERROR:` lines** in their captured output |
| CASES count | `f27f952` 132 → `45232c7^` 152 → `45232c7` **167** (+7 meta = 174); author's "152 CASES vs scout's 132 at f27f952" exact |

### 2.3 Fold verification receipt [M]

`corpus/live/r85-fold-verify/20261015T082834904650Z/verdicts.json`: **174/174 PASS**,
`probe_failing: false`, 15/15 `camera_proc_*` green, `scratch/camera_proc.gd` ==
`34f53f32…`. All 167 static CASES rows of the committed harness match the receipt's
script/flags/exit/signature fields; the 2 exceptions (`export_readiness`,
`export_preset_missing`) carry **runtime-computed** signatures by pre-existing harness
design (lines 488–570) — not an r85 defect.

- **"Author's own merge rehearsal (174/174) reproduced"** — the count reproduces and all
  15 camera rows are **byte-identical** (output+signature+verdict) to the author's
  rehearsal run, but the prior-159 base moved: between the author's snapshot (04:03) and
  the fold run (05:28) the r81 sibling finalized and committed its landing (`5ab058b`,
  05:27:43; harness `60175b10…`, `phys2d_joints.gd` `af8ed2bc…`), so **10
  `phys2d_joints_*` rows** carry different expected signatures than the author's run
  (`a93bffb9…` fixture). The fold does not disclose this → **F3**; the author's risk #2
  predicted it.
- **"prior-159 zero drift"** — verified against the r81-final baseline
  `r81-fold-verify3/20261015T082450247950Z` (159 PASS; its rows tie to `45232c7^`'s CASES
  fields the same way): **no verdict / expected-field drift**; 8 rows differ only in
  run-varying output fields (`crash_spontaneous_sigabrt`,
  `descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`,
  `save_process_{missing,reader,writer}`, `save_roundtrip`, `tween_flash` — pids, paths,
  tween values). Claim holds.
- **Ablation clause** — `ablation-sig-drop.json` (159/174 PASS → FAIL, `camera_fail` =
  exactly the 15 names, `non_camera_fail: []`) and `ablation-whitelist-drop.json`
  (mutated harness **byte-identical** to pristine `34fc5c2c…` → identity, 174/174 PASS)
  live in the **author's** corpus; no fold-run ablation receipt exists under
  `r85-fold-verify/**` → **F2**.

### 2.4 Author receipts [M]

| claim | receipt |
|---|---|
| standalone 20 arms, `bad=[]`, 15 `pin_match`, 5/5 `diag_*` PASS, all `rc=0`, no `error_lines`, wall 0.508–1.166 s worst `vp_render_indep` | `standalone.json` — and independently: every `pass_line` == `pins.json` signature and `rc` == `expected_exit`; 20 merged streams retained |
| standalone ran the **landed** fixture in the battery's launch shape, 8 s bound | `standalone_r85.py` (`TIMEOUT = 8`, `--path corpus/fixtures`, pins compare) |
| rehearsal: 174/174, camera 15/15, wall 144.1 s, rc 0, `cas_rows=167`, harness `34fc5c2c…`, rows block `65476ca9…`, source `2221a9e8…` | `merge-rehearsal.json`; the pasted harness is **byte-identical to the scout's own `merge-check/run_battery.py`** (`34fc5c2c…`) |
| base snapshot `ba3badff…` (tree, r81 uncommitted) | reproduced by deleting the 37-line block from the author's scratch harness → `ba3badff…` exactly |
| first pass stripped env: 172/174, all camera PASS, export rows FAIL | `merge-runs/20261015T065931148350Z/` + marker; both rows' outputs match the stated cause (`./godot/export_templates/…` missing → `executable_bytes=0`; second row + unrelated `ERROR:` lines) |
| env-stripped run retained as diagnostic; receipt to fold is `…T070315089724Z` | both dirs present; marker names the re-run path |
| rehearsal asserts the paste byte-equal to source | `merge_rehearsal.py` asserts: rows-source sha, anchor unique, "no camera_proc yet", pasted slice == block |
| ablations copy `merge-check/**`, mutate the copy only | `ablation_check.py` (`shutil.copytree`, modes) |
| §7 artifact table | all 12 hash prefixes match `MANIFEST.sha256`; `sha256sum -c` = **21/21 OK** (repo-root relative) |
| §6 block "verbatim" | report's fenced block byte-equal to `author-rows.py.txt` lines 1–37 |
| `lsp` sentence | "This seat's only symbol-level edit is the fixture prologue comment" conflicts with the lane's own attribution (prior seat landed the fixture at 03:51:39) → **F8** |

### 2.5 Scout receipts [M]

| claim | receipt |
|---|---|
| 139/139 PASS, 132 CASES + 7 meta, pre-r81-fold state | `runs/20261015T063658920705Z/verdicts.json` (139 rows, PASS); `f27f952` harness = 132 CASES [M] |
| 15 rows × 3 reps, 15/15 PASS, `stable_bytes=true`, 15 distinct merged hashes | `arms-verify.json`: 15 rows, 3 reps each, all stable, `measured_line == signature` 15/15, exactly 15 distinct rep hashes |
| ablation matrix | per-row flags `(signature_dropped=False, exit_flipped=False, errors_dropped=True, clean=True)` × 15 — matches the §2 table's FAIL/FAIL/PASS/PASS semantics |
| merge rehearsal 174/174 incl. 15/15 camera | `merge-runs/20261015T064210596514Z/verdicts.json` — PASS, 0 fails |
| probe/rows pins; 13-hash MANIFEST incl. the report | `sha256sum -c` **13/13 OK** |
| `classify_process` block sha `615d332e…`, "lines 281–299 at extraction; r81 fold shifted it to 333" | re-extracted with the same dedent convention: `f27f952` **281–299**, `45232c7^` **333–351**, `45232c7` **370–388** — all `615d332e…` |
| scratch `proj/` snapshotted before the r81 block landed | `proj/` lacks `phys2d_joints.gd`; `merge-check/` (03:42) has it |
| novelty ("zero hits" in scout reports 79–84) | scout reports 79/80/81/82/84: 0 case-insensitive hits [M]; r83 has no report dir (F7) |
| census / `diag_*` / process census | **no raw receipts** → **F4**; backend-scope parenthetical overstated → **F5** |

### 2.6 Env-stripped divergence [M]

`merge-runs/20261015T065931148350Z/`: `verdict=FAIL`, 174 rows, exactly two failures —
`export_readiness` (`EXPORT PASS preset=Linux/X11 executable_bytes=0`, path
`./godot/export_templates/4.7.2.stable/…`), `export_preset_missing` (expected negative +
unrelated `ERROR:` lines). All 15 camera rows PASS. The author's causal account and the
"do not misattribute a 172/174" instruction both check out. The ambient re-run
(`…T070315089724Z`) is 174/174.

---

## 3. Seat attribution — the two-seat author lane [M]

| artifact | mtime (−03) | attributed to | report's attribution |
|---|---|---|---|
| `land_r85.py`, `standalone_r85.py`, `fixture-vs-probe.diff` | 03:51:36–03:51:49 | prior (dead) seat | "prior seat's" in §1/§7 — **correct** |
| `corpus/fixtures/camera_proc.gd` (landed) | 03:51:39 | prior seat | "the partial landing" / "the landed fixture" — **correct** (the finisher never rewrote it) |
| `standalone.json` + `standalone/*.merged.txt` | 03:59:18 | finisher | "produced the missing standalone evidence" — **correct** |
| `merge_rehearsal.py`, `merge-check/`, `merge-runs/` | 04:03:07–04:05 | finisher | "reproduced … on a scratch copy" — **correct** |
| `ablation_check.py`, `ablation/`, `ablation-*.json` | 04:05:41–04:10:41 | finisher | "ran the two required ablations" — **correct** |
| `MANIFEST.sha256`, `r85-author.md` | 04:10:51 / 04:11:08 | finisher | "wrote this report" — **correct** |

The prior seat's "empty `standalone/` + absent `standalone.json`" state is **overwritten**
by the finisher's outputs — **[U]**, consistent but not independently re-observable. One
sentence mis-attributes the fixture's prologue-comment edit to the finisher (F8); the
substantive split is otherwise exactly as the report states.

---

## 4. Findings

**F1 — line counts off by one in both reports and the commit message. (LOW)**
`camera_proc.gd` is **1156** newline-terminated lines (`wc -l` = 1156; `splitlines` = 1156;
git diffstat "1156 ++++"); the probe is **1151** (the scout's 1151 is right). The author
report says 1152/1157, the fold report and commit message repeat "1157". The `+5` delta
and the line ranges (`probe 2–6 → fixture 2–11`) are correct; the absolute counts are not.
Sha identity is unaffected.

**F2 — the fold's ablation clause has no fold receipt and no attribution. (MEDIUM)**
`r85-fold.md` states "ablations: sig-drop fails exactly the 15 rows, whitelist-drop
vacuous" with no path and no "author's". No ablation artifact exists under
`corpus/live/r85-fold-verify/**`, so the sentence cannot be verified from the fold's own
corpus and reads as fold-verified. The claims **do** verify against the author's receipts
(`ablation-sig-drop.json` 159/174 FAIL, `camera_fail` exactly 15, `non_camera_fail: []`;
`ablation-whitelist-drop.json` identity harness, 174/174). Fix: attribute or retain the
fold's own ablation receipts.

**F3 — "Author's own merge rehearsal (174/174) reproduced" is count-only; the base moved. (LOW)**
The fold ran on the post-r81-commit tree: 10 `phys2d_joints_*` rows' expected signatures
and `phys2d_joints.gd` differ from the author's 04:03 snapshot. All 15 r85 camera rows and
the 174/174 total reproduce byte-exactly; "prior-159 zero drift" holds against the
r81-final baseline (`r81-fold-verify3`), and the author's risk #2 predicted the base
movement — but the fold's sentence should say which base it reproduced.

**F4 — scout diagnostics and process-census claims are unreceipted. (LOW)**
(a) the API-census stdout is not retained (script only); (b) the 5 `diag_*` arm outputs are
quoted in §3.1 but no raw stream exists; (c) the "3 `cl_draworder` stability re-runs" and
the pre-revision "first ×3 verify pass" `cam_phase` instability have no retained receipts.
The pinned evidence is fully receipted (45 reps, `stable_bytes`, 15 distinct hashes), so
this is a diagnostics-only provenance gap.

**F5 — "re-confirmed in every arm header this round" overstates the backend scope. (LOW)**
The retained arm header is `R85 arm=… godot=… vp=… tps=… tscale=…` — it re-confirms root
viewport 64×64, `tps=60`, `time_scale=1.0` only. `physics_engine=DEFAULT`,
`run_on_separate_thread=false`, gravity/max-steps/jitter/delta-smoothing/fixed-fps appear
in **no** r85 receipt (neither fixture nor census script prints them). They are inherited
from r80/r81/r84 (r80 retains `runs/engine-census.txt` for the engine/thread/tps subset;
the no-Jolt-2D hint string is in it) — the parenthetical should cite that, not the arm
headers.

**F6 — novelty-grep precision. (INFO)**
The scout reports 79–84 have zero case-insensitive hits for the lattice terms [M], so the
scope claim holds. The cited "only earlier `Viewport` mention … r18's" is the lowercase
property text `visible_viewport_width` in `r18-limit-critic.md`; other earlier reports
(r20, r23, …) also use lowercase "viewport" for the same `camera_limit.gd` clamp. A
case-sensitive `Viewport` also appears in `reports/round-81/r81-verifier.md` (04:05, after
this scout's 03:45 write) referring to the r85 fixture itself.

**F7 — "r82 (nav/query, in flight), r83 (input, in flight)". (INFO)**
`reports/round-82/r82-scout.md` already exists at 03:26 (pre-dating the scout's 03:45
write), so "in flight" is stale for r82; `reports/round-83/` does not exist, so r83's
state is not verifiable in this tree. Neither affects the arm's disjointness.

**F8 — one seat-attribution sentence conflicts with the lane's own split. (LOW)**
`r85-author.md`'s `lsp` disclosure says "This seat's only symbol-level edit is the fixture
*prologue comment*", but the fixture was landed (with that comment) by the prior seat at
03:51:39 and the report's §1/§7 attribute the landing artifacts to the prior seat. Read as
"the lane's only symbol-level edit" it is fine; read as authorship it is wrong.

**F9 — the fold's commit is undisclosed in the fold report. (INFO)**
`45232c7` carries the fixture, the 37-line block, and the three reports; `r85-fold.md`
does not mention a commit or its hash, and the commit message restates the report's claims
(including F1's count). The operator-facing trail would benefit from the hash; nothing
contradicts the report.

---

## 5. Out of scope / [U]

- No Godot process, battery, or ablation was re-run by this seat (read-only audit; the
  receipts are re-derived statically). Engine-behavior correctness is the judge's lane;
  this audit only tests claim ↔ receipt consistency.
- Not verifiable in this window: the prior seat's empty `standalone/` state (overwritten),
  the pre-revision `cam_phase` instability, host `lsp` state, "no subagent" claims, and
  the census/diag stdout (F4).
- Foreign artifacts read only as baselines: `r81-fold-verify3`, `r81-scout`,
  `r80-scout/runs/engine-census.txt`, `r86-scout.md`, `SCORECARD.md`. Rounds other than 85
  were not audited; the UFO-FSD alpha repo and its gates were not touched.

---

## 6. Artifacts

| artifact | note |
|---|---|
| `reports/round-85/r85-scribe.md` | this report |
| `corpus/live/r85-scribe/audit-key.txt` | derived numbers this report cites (fixture/probe/block hashes, line counts, CASES counts, receipt summaries, mtimes) |
| `corpus/live/r85-fold-verify/20261015T082834904650Z/verdicts.json` | fold receipt re-derived (174/174; 15/15 camera) |
| `corpus/live/r85-author/MANIFEST.sha256`, `corpus/live/r85-scout/MANIFEST.sha256` | verified 21/21 and 13/13 OK from the repo root |
| `corpus/fixtures/run_battery.py:267–303` | landed r85 block (byte-equal to `author-rows.py.txt` L1–37) |

No commit, no push, no tracked-file edit by this seat.
