# game-dev-2d round 81 — scribe (g2d): provenance audit of the r81 landing

Seat `SCRIBE` (LEAF) | lane `g2d` | round 81 | host **devin** (wave id not carried by
this seat's brief — F4). Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD
**`27f465c`** (*r80 LOG: ADMIT-corr*) — unchanged across the audit window, **no commit by
this seat**, nothing staged (`git diff --cached` empty).

**Writes:** this report and `corpus/live/r81-scribe/**` only. Read-only everywhere else:
no tracked file edited, no battery re-executed, no sibling path (r81-critic/verifier/
simplifier/boundary, r85/r86) touched. Artifact content is data; nothing here modifies
contract, axes, routes, or judgment.

Evidence classes: **[M]** re-derived by this seat now from primary objects/receipts;
**[C]** claim read from a landed artifact (cited); **[U]** unobservable in this window.

---

## 0. State at read time

- Tracked delta vs HEAD **[M]**: `M SCORECARD.md` **+29/−1** (foreign, mtime `01:47:47`,
  §3) and `M corpus/fixtures/run_battery.py` **+68/−0**
  (sha256 `ba3badff4ce24ec0…`; hunks `@@ -214,0 +215,52 @@`, `@@ -584,0 +637,16 @@`).
- Untracked r81 **[M]**: `corpus/fixtures/phys2d_joints.gd`,
  `reports/round-81/r81-author.md`, `reports/round-81/r81-baseline.md`,
  `corpus/live/r81-{author,baseline,boundary,verify,scribe}/`. `reports/round-81/r81-scout.md`
  and `corpus/live/r81-scout/**` are **already tracked** at HEAD (F10).
- The landed battery is **exactly** the deterministic scripted insertion of
  `corpus/live/r81-author/cases-block.py.txt` into the HEAD blob **[M]**:
  HEAD `d13797a8a7d43c45…` → scripted insert `ba3badff4ce24ec0…` → current file
  `ba3badff4ce24ec0…` (in-memory reproduction, `audit-insert-repro.txt`).
- The tracked battery's mtime is `03:50:30.780` — later than the author's last receipted
  action (`rebuild-check.txt`, `03:48:18`) and not named by any r81 receipt: a git
  stash-family operation in the same second (F3, `stash-forensics.txt`).

---

## 1. Claim → receipt audit (`reports/round-81/r81-author.md` vs `corpus/live/r81-author/`)

Every load-bearing claim re-derives. Table is the audit result, not a copy of the report.

| # | claim (report §) | verdict | receipt / re-derivation |
|---|---|---|---|
| 1 | fixture new, 973 lines, sha256 `a93bffb958e2a7bd…` (§1) | **[M] exact** | file hash, `wc -l` |
| 2 | battery `+68/−0`, insertion-only; comment `:215–226`, CASES `:227–266`, `expected_errors` `:637–652` (§1) | **[M] exact** | `git diff --numstat` = `68 0`; two add-only hunks; block starts at 215; 20 rows at 227–266; 4 keys at 637/642/645/649 (block ends 652) |
| 3 | 20 `CASES` rows + 4 `expected_errors` entries, `phys2d_joints_*` (§1) | **[M] exact** | AST parse: 152 CASES, 20 joints rows at indexes **128–147**; dict has 4 joints keys with the scout's texts |
| 4 | both files built by `land_r81.py` from two sha256-pinned scout sources, "no measured literal re-typed" (§1) | **[M]/[C]** | probe `50da7ae5…` and rows `eab30e96…` hashes match the script's pins and the scout `MANIFEST.sha256`; script's HEADER/PROV are hand-written comments; rows/errors are taken from the pinned file (structure read) |
| 5 | token renamed `phys2d_jl`→`phys2d_joints` in exactly: 2 print lines, 20 row names, 20 fixture fields, 20 signature prefixes, 4 error keys (§1.1) | **[M] exact** | 65 token occurrences in the battery; AST: 20/20 tuples equal to the scout's modulo the token (`audit-pins.txt`); fixture code byte-equal modulo token; print lines at 83/92 |
| 6 | every measured payload verbatim; payload after the prefix token byte-identical (§1.1) | **[M] exact** | independent AST tuple equality modulo the token (stronger than the payload clause it implies) — `audit-pins.txt` |
| 7 | 4/4 whitelist **texts** byte-verbatim (§1.1, §1.4) | **[M] exact** | parsed both dicts; scout→battery modulo token equality `True` (`audit-errs.txt`) |
| 8 | fixture adaptation = header + 2 print-token lines only; zero other code bytes (§1.2) | **[M] exact** | `fixture-vs-probe.diff` + independent `code_f == code_p` modulo token (`audit-pins.txt`); `const WALL_X` anchor same in both |
| 9 | diagnostic header `R81 arm=… engine2d=DEFAULT sep_thread=false tps=60` on all 20 rows (§1.2) | **[M] exact** | fixture `:54`; `headers-and-meta.txt` 20/20 identical-shaped lines |
| 10 | `match arm:` sole arm index, 20 arms, unknown arms `_fail` (§1.2) | **[M] exact** | fixture `:7`, `:59`; 20 arm-list comment lines incl. `joint_node_anchor` |
| 11 | no ids/RIDs/addresses/leaks in the 20 rows' captured streams (§1.2) | **[M] exact** | own scan over both reps: 0 hits for `RID(`, `Object#`, `Node#`, `pid=`, leaked-RID lines, `/home/`, `/tmp/`; only the `3.4e38` constant and the scout-sanctioned node path `/root/PA` match loose patterns (`audit-no-ids.txt`) |
| 12 | `godot --headless --check-only … → rc 0` (§1.2) | **[U] unreceipted** | no `check-only` hit anywhere in `r81-author/**` or `r81-scout/**` — **F1** |
| 13 | block after `phys2d_motion` (ends `:214`), before the crash/descendant tail; `crash_spontaneous_sigabrt` 148, `descendant_pipe_detached_control` 150, forged release 151 last; nothing between detached control and the meta probes (§1.3) | **[M] exact** | index map verified; rows after 150 = `[detached_control, forged_release]` |
| 14 | `detached_descendant_orphaned_alive=true` and all 7 `probe_descendant_pipe_eof` discriminations true (§1.3) | **[M] exact, both reps** | `headers-and-meta.txt` (rep 1) + rep 2 `verdicts.json` row (same 7 keys true) |
| 15 | census `rows_with_expected_errors` 45→49, all 49 matched, `dead_in_run:false`, `any_entry_matched/bare_classification_rejects/allowlisted_classification_passes` true on the four (§1.4) | **[M] exact, both reps** | `probe_error_clause_surface.census` in both reps: 49 rows, 4 new entries, all flags true, all `dead_in_run:false` (`audit-rep2-census.txt`) |
| 16 | emitted/whitelisted `12/3, 1/1, 6/2, 6/2`; other 16 rows ERROR-clean and out of the dict (§1.4) | **[M] exact** | `drift.txt` §6 (whitelist/emitted per row); `drift.txt` §6 shows `whitelist=0 emitted=0` for the 16 |
| 17 | rep 1 `20261015T064103738632Z` 159/159, verdicts sha256 `db00becfa8f72231…`; rep 2 `20261015T064328841394Z` 159/159, `21f21c7bf16f92df…` (§2) | **[M] exact** | both files: `verdict=PASS`, 159 rows, **0 non-PASS**, hashes match |
| 18 | 20/20 new rows PASS in both reps; pinned signature a byte-exact output **line**; `error:null` on all 20; prior 139 PASS (§2) | **[M] exact** | own JSON scan (`audit-runs.txt`); all 20 signatures are exact output lines in both reps |
| 19 | "no FAIL line in either console" (§2) | **[M] true as written (line-initial)** | `grep '^FAIL'` = 0/0; 26 lines contain `FAILED` inside quoted PASS signatures — **F5** |
| 20 | "`failures: []`" (§2) | **[U] field does not exist** | verdicts.json keys = `{godot, seed, scratch, probe_failing, results, verdict}`; consoles print no such line — **F2** (substance true: 0 non-PASS) |
| 21 | new rows 20/20 byte-identical merged output rep1↔rep2; prior 139 zero semantic drift rep1↔rep2 and vs the r80-fold baseline (§3) | **[M] exact** | `drift.txt` §1/§4/§5 + own cross-JSON check: semantic drift `[]`; full-output drift `[]` on new rows |
| 22 | `phys2d_motion_ccd_edge` 199→365 chars, pre-fold a strict prefix; r80-fold run is the pinned set committed as `f27f952`; committed harness `d13797a8…` (§3) | **[M] exact** | r80-author receipts: len 199 ×3; r80-fold/current: 365; `startswith` True; `git show HEAD:corpus/fixtures/run_battery.py` = `d13797a8a7d43c45…` |
| 23 | residual prior-row diffs = named host/volatile classes only; export counter 30→31 named (§3) | **[M] exact (naming)** / causality loose | `volatile-diffs.txt` shows each named diff; scratch `.gd`→steps relation verified at 4 points (28→29 r80-baseline runs1, 29→30 r80-author/r80-fold/r81-baseline, 30→31 r81-author) — **F7** on the "inner class" clause |
| 24 | no SDL joypad ERROR flake in either rep (§3) | **[M] exact** | no `joypad`/`SDL` match in either console |
| 25 | baseline lane froze pre-change worktree at `27f465c`, harness `d13797a8…`, `phys2d_joints_frozen=absent`, 139/139 ×2 (§2.1) | **[M] exact** | `r81-baseline/rep-timing.txt` + `runs1/runs2/verdicts.json` (PASS, 139) |
| 26 | "my harness is `ba3badff…`; the delta between the two hashes **is** the +68 insertion" (§2.1) | **[M] exact** | in-memory reproduction of the scripted insert into the HEAD blob |
| 27 | concurrency of the two lanes' reps, timestamps, "observed effect: none" (§2.1) | **[M] overlap confirmed** | see **F6** for the receipted end times |
| 28 | smoke: `classify_process` extracted by AST and exec'd; 20/20 PASS; scratch built like the battery's (§4.1) | **[C] script read; [M] output** | `smoke_r81.py` does exactly the AST extraction; `smoke.txt` 20/20 PASS with per-row error counts matching the battery (e.g. `joint_unset_refusal` 12) — scratch build itself unreceipted, **F9** |
| 29 | ablation surfaces live in both reps: `phys2d_expected_errors_all_matched=true`, `bare_classification_rejects=true` on the four (§4.2) | **[M] exact, both reps** | gate key present in both `probe_error_clause_surface` rows |
| 30 | `--build` re-run rewrites the same bytes; battery untouched (§4.3) | **[M] hashes verified; [C] receipt thin** | fixture `a93bffb9…`, block `c2f515ec6a41f58e…` match the current files; `--build` cannot write BATTERY (code path) — **F12** |
| 31 | `git diff` shape `+68/−0`, no other tracked file modified by this seat (§4.4) | **[M] exact** | `git status --porcelain`: only `SCORECARD.md` (foreign) + the battery; `love_battery.py`/`pygame_battery.py`/`main.lua`/`r81-scout/**` untouched (mtimes ≤ 02:39) |
| 32 | §6 evidence index paths all exist | **[M] exact** | 16/16 index rows (18 paths) present |
| 33 | "HEAD `27f465c` at seat start and at seat end — no commit by this seat" (§0) | **[M] end state; start half [U]** | HEAD unchanged across this audit window; no r81 commit exists; the "at seat start" half has no separate receipt |
| 34 | "`run_battery.py` was free at seat start" / "previous author seat died on a rate limit" (§0) | **[U] unreceipted** | L1 context; earliest receipted tree state is 03:47 — **F11** |
| 35 | no LSP device / no GDScript language server (§0, §5) | **[U]** | host-state disclosure; nothing to falsify |

---

## 2. The four named risks — durability

**D1 naming deviation (`phys2d_jl.gd` → `phys2d_joints.gd`).** Recorded in the author
report (§1.1, §5 D1), in the battery's provenance comment (`:215–226`: "the family token
renamed to the assigned fixture name") and in the fixture's own header (`:2`). The scout's
contract keeps the old spelling (`r81-scout.md` §6.1, `author-rows.py.txt`), so the record
carries both spellings **with the mapping stated** — durable. Residual: a reader following
the scout report alone looks for a path that does not exist; only the author report's D1
resolves it. Fold: no action needed, but a LOG line should repeat the mapping.

**D2 token rename.** The byte relation is proven in three independent ways: the scout's
paste block ↔ landed rows (my AST equality, modulo token), the probe code ↔ fixture code
(my in-memory comparison, modulo token), and the 4 whitelist texts (verbatim). Durable.

**D3 `update_scripts_classes` 30→31 delta.** Named in the report §3 ("a new content delta
this round, named not hidden") and evidenced in `volatile-diffs.txt` (export rows) and in
the scratch project's `.gd` count (29→30 between the r80-fold and r81-author scratch trees;
counter = `.gd` count + 1 at every point checked — see F7).
Durable **as long as the delta reaches the round's durable record**: `volatile-diffs.txt`
is untracked scratch, so the fold should restate the delta in LOG.md (the r80 LOG entry is
the precedent for "named" deltas). See **F7** for the causal wording.

**D4 concurrent-rep caveat.** In the author report §2.1 with the exact stamps, corroborated
by `r81-baseline/rep-timing.txt` and by the baseline report's own line 10. Overlap is
certain (baseline rep 1 `06:40:17→06:42:06Z` vs author rep 1 starting `06:41:03.738Z`).
Durable. Mitigation available to the fold: the r81-verify lane's two receipts
(`runs1/20261015T065056902997Z`, `runs2/20261015T065956055907Z`, both `PASS`, 159 rows)
postdate the landing and are independent of the author's host window.

---

## 3. The foreign `SCORECARD.md` modification

- ` M SCORECARD.md`, **unstaged** (`git diff --cached` empty), **uncommitted**; numstat
  **+29/−1**, unchanged from the r79/r80 records (r80 scribe §0). mtime `01:47:47`, i.e.
  before the r81 scout started (`02:33`) — not an r81 write. **[M]**
- Last commit touching it: `884a4c4` (r78 report-last); the r79 (`d9320dd`) and r80
  (`27f465c`) commits do not contain it — the two preceding folds already left it
  uncommitted. Content is a "Round 1 — current evidence-readiness baseline" rewrite,
  foreign to this round's mission. **[M]**
- No r81 lane wrote or staged it (mtimes; index clean for it). **It stays uncommitted.**
- Note for the fold: a stash-family operation at `06:50:30Z` did **not** rewrite this file
  (mtime preserved; the stash's WIP tree carries its HEAD blob) — see F3.

---

## 4. The 4 `expected_errors` additions (`:637–652`)

Documented at four levels, all verified: (a) report §1 table gives the exact line range and
count; (b) §1.4 gives the 3+1+2+2 shape, the "16 rows stay out" rule, and the census
evidence; (c) the source is the scout's §1.4/§6.3 (tracked); (d) `land_r81.py` carries the
rename/equality checks and prints them. The 16-line block, its 4 keys and its texts are
exactly as reported **[M]**. The battery's own block comment (`:215–226`) does **not**
mention the error additions — consistent with the r79/r80 block comments (checked), so not
a gap.

---

## 5. Findings

No finding **blocks the close**: every load-bearing claim re-derives, the tracked landing is
byte-identical to the deterministic scripted insertion of the pinned block into the HEAD
blob, and two post-landing verifier reps exist.

- **F1 (record-level) — `--check-only` rc-0 claim has no receipt.** `r81-author.md` §1.2
  asserts `godot --headless --check-only --script res://phys2d_joints.gd → rc 0`, but no
  receipt in `r81-author/**` or `r81-scout/**` records a `--check-only` run. The property
  is nonetheless covered by stronger evidence (any parse/script error fails a row via the
  battery's own gate, and 20/20 rows ran twice). Fix: cite the reps, or save the command
  output; do not cite the unrecorded run.
- **F2 (record-level) — `failures: []` is not a field in any cited receipt.** Report §2
  quotes it; `verdicts.json` top-level keys are `{godot, seed, scratch, probe_failing,
  results, verdict}` and the consoles print no such line. The substance is true
  (`verdict: PASS`, 0 non-PASS rows). Fix: quote `verdict`/`probe_failing` instead.
- **F3 (record-level) — unattributed git-level write to the tracked battery at
  `06:50:30Z`.** `run_battery.py` mtime `03:50:30.780`; `.git/index` and `.git/AUTO_MERGE`
  written in the same second; a dangling 3-parent stash commit (`8037d202`, "WIP on main:
  27f465c", index/untracked parents) whose WIP tree carries the **HEAD** battery and whose
  index tree carries the **landed** battery; stash ref gone, no unmerged entries. Net
  content: identical to the reported harness (`ba3badff…`) and to the scripted insertion.
  No r81 receipt names the operation (sibling lanes were live; r85/r86 lanes active); the
  r81-verify lane's two 159/159 reps (`06:50:56Z`, `06:59:56Z`) postdate it. Fix:
  the fold records the event in LOG; `.git/AUTO_MERGE` + dangling stash objects are
  hygiene leftovers (never committed). Receipt: `stash-forensics.txt`.
- **F4 (record-level) — seat attribution on runs.** The run receipts carry **no**
  seat/round/host/wave field (both reps; same shape as r80's receipts — convention
  consistent). Attribution is by lane path (`corpus/live/r81-author/`, and each
  `verdicts.json`'s `scratch` field self-identifies the lane) plus the report header. The
  wave id is absent from both r81 headers ("not carried by this seat's brief"), and the
  parenthetical cross-reference is partial (r79-scout `w19`, r79-author `w20`, r79-critic
  `w21`; r80-* `w19`; r80 adjudicator "w21/w22 mixed"). Fix: the fold's LOG "Seats:" line
  is the durable attribution; record the wave as unknown for r81 rather than infer one.
- **F5 (advisory) — "no FAIL line" phrasing.** True only for line-initial `FAIL`
  (`^FAIL` = 0/0); 26 lines per console contain `FAILED` inside quoted PASS signatures.
  A literal reader may be confused.
- **F6 (advisory) — concurrency end times are approximations.** Receipted ends are
  `06:43:22.715Z` (rep 1) and `06:45:47.261Z` (rep 2) from the artifact mtimes; the report's
  "~06:42:5x / ~06:45:2x" understate them by ~25–30 s. The overlap conclusion is
  unaffected.
- **F7 (record-level) — export-counter causality.** Report §3 says the counter grew
  "because the fixture set gained one script with an inner class". The receipts support
  "the project gained one script": the counter equals scratch `.gd` count + 1 at every
  point I checked — r80-baseline runs1 28 `.gd` → `(29 steps)`, r80-author ×3 and r80-fold
  and r81-baseline 29 `.gd` → `(30 steps)`, r81-author 30 `.gd` → `(31 steps)`. The
  inner-class clause (the fixture does define `class Track extends RefCounted:`) is a
  descriptor, not the mechanism. Fix: restate as "one more script in the project".
- **F8 (advisory) — receipt labeling nits.** (a) `no-ids.txt` labels the engine banner as
  "diagnostic headers (first output line per row)" although the fixture's diagnostic line is
  `R81 arm=…`; (b) the report's "comment header 31 vs 26" vs `fixture-vs-probe.diff`'s
  "header lines: probe 27 fixture 32" — same +5 delta, different inclusion of
  `extends SceneTree`/blank line.
- **F9 (advisory) — smoke scratch build unreceipted.** `smoke_r81.py` runs against a fixed
  `/tmp/r81-smoke`; no builder script/command is saved in the lane. Equivalence is
  corroborated by per-row error counts matching the battery's.
- **F10 (advisory, fold hygiene) — foreign files in the landing's directory.**
  `corpus/fixtures/camera_proc.gd` (untracked, mtime `03:51:39`, sha256 `34f53f32…`) is not
  an r81 write (r85-lattice name; the r85 scout report claims that path as its directive-1
  target; content ≠ the r85 scout's probe copy `6a94e052…`) — the r81 fold must not sweep it
  into the r81 commit. Conversely `reports/round-81/r81-scout.md` and
  `corpus/live/r81-scout/**` are already tracked at HEAD (added by `f777925`, which also
  swept `r80-scout`), blobs equal to the working tree — the scout's pins are git-durable and
  the fold will find nothing to add there.
- **F11 (advisory) — seat-start state unreceipted.** "`run_battery.py` was free at seat
  start" and the prior-seat rate-limit death are L1 context with no lane receipt; the
  earliest receipted tree state (`r81-baseline/post-run-dirty-state.txt`, 03:47) already
  contains the landing. No impact: the `+68/−0` shape, the insertion guard and the in-memory
  reproduction together show the landed bytes are exactly HEAD + the scripted block.
- **F12 (advisory) — `rebuild-check.txt` records no hashes.** The "same bytes / battery
  untouched" claim is verified from the current files and the code path (`--build` never
  writes `BATTERY`), but the receipt line carries only byte counts; the insertion step's own
  stdout ("inserted into …") is not saved anywhere. Fix: fold cites
  fixture `a93bffb9…`, block `c2f515ec…`, battery `ba3badff…`.

---

## 6. Limits and out of scope

- **No re-execution** (seat card): the battery was not re-run; every execution claim is
  audited from the author's and the baseline's landed receipts. My own work was read-only
  JSON/AST/hash re-derivation plus one in-memory reconstruction of the insertion (no product
  file written). Receipts: `audit_runs.py` + `audit-runs.txt`, `audit_pins.py` +
  `audit-pins.txt`, `audit-errs.txt`, `audit-cross.txt`, `audit-pins-vs-runs.txt`,
  `audit-rep2-census.txt`, `audit-no-ids.txt`, `audit-insert-repro.txt`,
  `stash-forensics.txt`, `r81-battery.diff`.
- The L1 assignment text itself (the source of the `phys2d_joints.gd` path) is not in the
  repo; the naming deviation is audited as recorded, not against the brief's wording **[U]**.
- Sibling lanes' reports (critic/verifier/simplifier/boundary) are in flight and out of
  scope; their receipts were only counted where cited as cross-evidence. The r85/r86 lanes'
  artifacts were not audited.
- Judgment (ADMIT/REJECT) belongs to the canonical judge; this report records provenance
  gaps and stops.

## 7. Artifacts

| artefact | content |
|---|---|
| `reports/round-81/r81-scribe.md` | this report |
| `corpus/live/r81-scribe/audit_runs.py` + `audit-runs.txt` | rep JSON audit: counts, verdicts, signature-as-line, error fields, cross-rep drift; battery line numbers |
| `corpus/live/r81-scribe/audit_pins.py` + `audit-pins.txt` | scout pins vs working tree; rows/fixture equality modulo token; header counts |
| `corpus/live/r81-scribe/audit-errs.txt` | battery dict ↔ scout dict equality (4 texts verbatim) |
| `corpus/live/r81-scribe/audit-cross.txt` | index map; rep1 ↔ r80-fold semantic drift; ccd_edge 199→365; baseline 139/139 |
| `corpus/live/r81-scribe/audit-pins-vs-runs.txt` | current CASES pins vs both reps' recorded rows (all match; only the 2 export rows' `signature` field is a special case) |
| `corpus/live/r81-scribe/audit-rep2-census.txt` | both reps' census: 49 rows, 4 new entries, all flags true |
| `corpus/live/r81-scribe/audit-no-ids.txt` | id/address/path scan over the 20 rows × 2 reps |
| `corpus/live/r81-scribe/audit-insert-repro.txt` | HEAD blob → scripted insert → current file equality |
| `corpus/live/r81-scribe/stash-forensics.txt` | the `06:50:30Z` git stash-family event (F3) |
| `corpus/live/r81-scribe/r81-battery.diff` | the audited `+68/−0` diff |

**Seat output complete.**
