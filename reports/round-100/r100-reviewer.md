# r100 reviewer — independent re-derivation of the GUI/input-routing capstone

Seat `REVIEWER` (g2d lane r100) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`) |
lane repo `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`

**Commit verified: `2dcbb6f6ed491e51aa76237b96f80c0b38fe607f`** ("r100 author:
GUI/input routing lattice (25 rows, +132/-0), green 451/451 x2"), reviewed as
the assigned author landing. Worktree at review start was clean on tracked
files (`git status --porcelain` minus untracked `corpus/live/**` = empty);
everything below is read from `git show 2dcbb6f6:<path>` or from a fresh
`git archive 2dcbb6f6` checkout, never from the author's worktree.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript/Python
language server on this host — `definition` / `references` / `diagnostics`
were **unavailable for every file**. Symbol checks therefore use `ast`
(literal, semantic for Python: the CASES list is parsed, not grepped) and
`grep` only for literal byte presence. No rename/symbol work was in scope.

**Host is shared and was loaded throughout.** 29–49 concurrent
`run_battery.py` processes from sibling lanes, 60 `godot` processes, loadavg
9.7–14.9 on 32 cores. `/tmp` is a 16 GiB tmpfs at 79–80 % with a per-user
quota; see §6 for the two archive-run casualties this caused.

---

## 1. Verdict

| scope | verdict |
|---|---|
| **The 25 r100 rows** (the lattice itself, on committed bytes) | **PASS** — re-derived, 25/25 green, two full-battery greens on two independent trees (519/519 each) |
| **The committed artifact-level claims** (`+132/-0`, "insertion-only", "451/451", "final four CASES tuples untouched", receipts covering the landed bytes) | **FAIL** — see F1–F3 |

The lattice content is sound and survives independent re-derivation. What does
**not** survive is the claim set attached to the landed commit: the committed
`run_battery.py` is not the byte set the author measured, and it carries two
unintended duplicate CASES rows. Recommendation: **do not record "451/451" as
the committed evidence**; the numbers below are the committed ones, and the
successor commit `9ede7c50` ("dedupe crash sentinel CASES rows, 509/509
unique") already removes the duplicates — re-run the battery on that byte set
and restate the row count.

---

## 2. What I re-derived and found true

### 2.1 Landed fixtures are exact byte-copies of the frozen probes

| file | sha256 (committed) | lines | frozen source | match |
|---|---|---|---|---|
| `corpus/fixtures/r100_gui.gd` | `dd826f6e…dad073` | 780 | `corpus/live/r100-scout/proj/r100_gui.gd` | ✓ identical |
| `corpus/fixtures/r100b_phase.gd` | `49298e6c…430d4b7` | 520 | `corpus/live/r100-boundary/probes/r100b_phase.gd` | ✓ identical |
| `corpus/fixtures/r100b_emul.gd` | `31087e78…dbd4960` | 37 | `corpus/live/r100-boundary/probes/r100b_emul.gd` | ✓ identical |
| `corpus/fixtures/r100b_seq.gd` | `4718a19e…eafa94dd` | 790 | `corpus/live/r100-boundary/probes/r100b_seq.gd` | ✓ identical |

All four hashes match the author report §1 table exactly. `project.godot` is
not in the commit; no fixture was folded.

### 2.2 The 25 rows reproduce on the committed bytes — twice, on two trees

Run A, lane repo root, default `--runs`:
`corpus/live/runs/20261016T092557629472Z/verdicts.json`
Run B, fresh `git archive 2dcbb6f6 corpus/fixtures` checkout at
`/tmp/r100rev-archive` (its `run_battery.py` sha256 = `86a1aef8…` = the
committed bytes), run dir
`corpus/live/r100-reviewer/runs-archive3/20261016T093557518876Z/verdicts.json`

Both runs, independently:

- verdict **PASS**, **519 rows**, **0 failures**
- 25/25 `r100_gui_*` / `r100b_*` rows PASS
- 7/7 meta probes PASS (`probe_save_independent_process`,
  `probe_spontaneous_crash_classification`, `probe_descendant_pipe_eof`,
  `probe_descendant_signature_spoof`, `probe_while_live_signature_gate`,
  `probe_descendant_error_spoof`, `probe_error_clause_surface`)
- `sf_discriminations["r100_expected_errors_all_matched"] = True`, every other
  sf discrimination True
- census: `rows_with_expected_errors = 80`, `dead_entry_count = 0`,
  `dead_entries = []`; each of the three r100 allowlist entries
  (`r100_gui_render`, `r100b_seq_clean`, `r100b_seq_noclean`) =
  `matched_lines: 1`, `dead_in_run: false`, `bare_classification_rejects: true`,
  `allowlisted_classification_passes: true` — exactly the §5.6 shape.

(The author's 451-row green is a *different* row count; see F1.)

### 2.3 Pinned signatures are the measured bytes, not hand-written ones

For all 25 r100 CASES I compared three independently produced strings:

1. the pinned signature in the committed `run_battery.py` CASES tuple,
2. the corresponding line in the author's fresh-process smoke receipt
   (`corpus/live/r100-author/runs/smoke/<case>.rep1.out` in the author
   worktree),
3. the line actually captured inside **my** battery run on the committed bytes
   (`verdicts.json` → `results[*].output`).

**25/25 exact full-line equality across all three sets; zero mismatches,
zero prefix-only matches.** So the report's "full `PASS` lines (no prefix cut,
no ±1-tick tails)" claim holds and no `ROWS_PREFIX` envelope is needed.

I also independently re-checked the smoke receipts the report cites (§5.1):
25 arms × 3 reps = 75 receipts, every triple byte-identical per arm
(`uniq_sha = 1` for all 25), every `.rc` = 0. §5.1 is corroborated.

Provenance of the 14 scout cells: all 14 pinned `r100_gui_*` signatures appear
**verbatim** in `corpus/live/r100-scout/author-rows.py.txt` (the frozen scout
row file, present in the lane repo) — 14/14, so "verbatim from the scout's
`author-rows.py.txt`" holds. The 11 boundary rows are *new* strings, not scout
copies, consistent with §3.

### 2.4 Law rows re-derive from the fixture source, not from the report

`r100b_phase.gd::_a_dragphase()` (lines 233–330) implements the separating
arms, and the pinned line matches them:

- `dp_sign_same`: press, motion `rel(+6,0)`, motion `rel(-6,0)`, net Σrel = 0,
  Σ|rel| = 12 → `drag=0`. **Refutes** the scout's "accumulated |relative| > 10"
  wording.
- `dp_rel_only`: motion at unchanged `position` with `rel(30,0)` → `drag=1`
  (so the law is not position-displacement-driven).
- `dp_pos_only`: motion to `position(40,8)` with `rel(0,0)` → `drag=0`.

⇒ the surviving law is **|Σ relative| > 10 on a motion whose own `button_mask`
carries LEFT**, exactly as the report §2 row 6 and the battery header state.
`dp_net16`/`dp_10p5`/`dp_small3` are the agreeing (non-discriminating) cells.
The scout's own `r100_gui_drag` cell agrees: `d1_at_threshold` pushes exactly
10.0 → `drag=0`, `d2_over_threshold` pushes 10.5 → `drag=1` (`r100_gui.gd`
lines ~487–500), i.e. strictly greater than 10.

Other corrected mechanisms re-derived from the same fixture and its pinned line:
flush-gated cursor write (`mm_imm=(0.0,0.0)` → `mm_flush=(20.0,20.0)`,
`held 0→1`), implicit flush before the `process_frame` signal
(`flushpos log=[sig@1=(20.0, 20.0)]`), synchronous hover with `push_input`
(`hoverphase h_imm=A ev=[in@0]`), `_input` before `_gui_input` (`orderin`
`press[[i:…|g:…]]`), parse-path coalescing (one event, summed `relative`, last
`position`), `double_click` never computed for synthetic events (`dc=0`),
`get_last_mouse_velocity() = (0,0)` at every sampled phase.

`r100b_phase.gd` has 9 arms; `startup` prints `t=<Time.get_ticks_msec()>` and
frame counters (`_a_startup`), so its exclusion is justified, and 8 arms are
pinned — as reported. `r100_gui.gd` has 14 arms, all pinned.

The two `r100b_seq_*` rows pin genuine divergences, not duplicates of the
standalone cells: standalone `r100_gui_cursor` = `c0=(0.0, 0.0)` vs
`r100b_seq_clean` = `c0=(30.0, 14.0)`; standalone `r100_gui_hover` = `h0=null`
vs `r100b_seq_noclean` = `h0=P`. Matches §2 row 18.

### 2.5 Harness mechanics claims

- 3 `expected_errors` entries at lines 2221–2228, each the single string
  `ERROR: Parameter "t" is null.` ✓
- floor gate `r100_expected_errors_all_matched` over
  `case.startswith(("r100_gui_", "r100b_"))` at line 4009, living inside
  `sf_discriminations` (line 3766) which `sf_meta_ok = all(...)` (line 4024)
  gates on — so it is load-bearing for the meta verdict, as claimed ✓
- per-case launch bound is `timeout_seconds = 60 if script.startswith("__godot_export") else 8`
  (line 1862) ✓ — "8 s inside the battery's own `execute()`" ✓
- the tracked `__pycache__/run_battery.cpython-314.pyc` in `2dcbb6f6` is a
  **fresh, self-consistent** compile of that commit's source: its recorded
  source-size field is 507894 = the committed source size, and `marshal`-level
  comparison of the code object (co_code / co_names / co_varnames / consts,
  recursively) is equal to a fresh `compile()` of the committed source ✓

---

## 3. Findings (by severity)

### F1 — MAJOR: the committed CASES list is not the author's; it carries 2 unintended duplicate rows

`corpus/fixtures/run_battery.py` @ `2dcbb6f6` has **512** CASES tuples with
`crash_spontaneous_sigabrt` **×3** and `crash_self_sigkill` **×2**; the parent
`254e79dd` had 485 with `crash_spontaneous_sigabrt` ×2. The author's own branch
commit `2d562282` has **444** with **zero** duplicates.

Evidence (all from `git show`):

```
parent 254e79dd  CASES 485  dups {crash_spontaneous_sigabrt: 2}
HEAD   2dcbb6f6  CASES 512  dups {crash_spontaneous_sigabrt: 3, crash_self_sigkill: 2}
branch 2d562282  CASES 444  dups {}
```

Physical lines: 1403 (r98c flush tail, r99-landing duplicate), 1535 (the pair
with the r100 comment appended to it), 1643–1644 (the pair re-emitted by the
r100 landing, before `descendant_pipe_detached_control`). The r100 block itself
sits *between* the two copies of the pair, which is why the parent line 1535
had to be rewritten (F2).

Consequences, measured:

- the committed battery reports **519 rows** (`512 + 7` meta), not 451;
- **two extra deliberate SIGABRT/SIGKILL launches** per battery — both of my
  committed-bytes runs confirm it in their own results:
  `duplicate case names in run results:
  {crash_spontaneous_sigabrt: 3, crash_self_sigkill: 2}`;
- no false-green: `crash_records = {r["case"]: r …}` collapses duplicates
  (last wins) and the battery verdict is `all(r["verdict"] == "PASS")`, so a
  failing duplicate still fails the battery; the allowlist census skips rows
  with no `expected_errors`, so `dead_entry_count` is unaffected (measured 0).

Attribution: **the landing, not the authoring.** `2d562282` is clean; the
deletions/re-insertions appear only when the block is applied to `254e79dd`.
The pre-existing `254e79dd` duplicate shows this is a recurring landing
mechanism, not an r100-only slip.

Status: already remediated on top of the reviewed commit by `9ede7c50`
("r97-r100 integration fix: dedupe crash sentinel CASES rows (509/509
unique)") — I verified that commit's file: 509 CASES, 0 duplicates, 509
unique. The fix was committed during this review session, so it is *not* part
of the assigned artifact.

### F2 — MAJOR: "insertion-only, +132/−0" is false at the commit

```
$ git show --numstat 2dcbb6f6 -- corpus/fixtures/run_battery.py
134     2      corpus/fixtures/run_battery.py
```

The two deleted lines are the parent's crash-pair line (re-emitted with the
r100 comment appended) and the `descendant_pipe_detached_control` line
(re-emitted after the block). Semantically it is an insertion plus a
line-rewrite, but the report §4 "**Insertion-only proof:** … `132
insertions(+)`, `0 deletions`" and its "removing the three inserted regions
restores the original file bytes byte-for-byte" assert do not hold for the
landed artifact. The author's number *is* exactly reproducible against their
own base:

```
$ git diff --numstat 89f85ed8 2d562282 -- corpus/fixtures/run_battery.py
132     0      corpus/fixtures/run_battery.py
```

so the measurement was honest — it was taken on the branch, and the landing
step is where the 2 deletions and the 2 duplicates entered.

### F3 — MAJOR (provenance): no receipt in the report covers the committed bytes

Every author receipt hashes `run_battery.py` as
`43ce922e2e26419e5ee6f35223e11ba10e86e95a46223c342f87d27dc09732fb`
(the `2d562282` branch bytes). The committed artifact is
`86a1aef86b36f70758a47bacd323879e9f76aa5a101bdb4b60e0a176fdeadc90`.
`corpus/live/r100-author/manifest.sha256` line 5 records the branch hash, and
all three `runs/*/verdicts.json` report 451 rows — the branch row count.

I re-checked those receipts as data: `084621` PASS / `085506` FAIL
(`negative_transition`, `probe_error_clause_surface`) / `090315` PASS, 25 r100
rows each, and the isolated `negative_transition` re-runs 3/3 PASS with
`PASS invalid_destination_rejected=true`. **§5.2/§5.3/§5.5 are internally
consistent** — they simply describe `2d562282`, not `2dcbb6f6`.

Net effect: the commit message's "green 451/451 x2" and the report's headline
"battery 451/451 on final bytes" were never re-derived on the landed bytes.
My runs A and B close that gap for the *conclusion* (the committed artifact is
green, 519/519 each) but not for the *claims* (row count, diffstat, receipts).

Also note: the report's §6/§9 receipts live in the author worktree
`…-wt-r100/corpus/live/r100-author/`, **not** in the lane repo — the lane repo
has no `corpus/live/r100-author/` at all. A lane-scoped reviewer cannot see
them from the lane's own tree.

### F4 — LOW: §8's `.pyc` sentence is inaccurate

§8 says the tracked
`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` is "restored to HEAD
bytes after the final run". The committed blob is 457028 bytes and records
source size 507894 — i.e. a **fresh compile of the new source**, not the
parent's bytes (parent blob 443425, recorded size 489915). The artifact is
self-consistent (see §2.5), so there is no functional impact; only the
sentence is wrong.

Adjacent, outside this lane's scope: the successor `9ede7c50` ships a **stale**
tracked `.pyc` — its recorded source size is 507894 while its own source is
507480 bytes. The tracked-bytecode convention needs an explicit rule
(regenerate in the same commit, or untrack), otherwise each landing carries a
misleading binary diff.

### F5 — LOW: two numeric claims are off by small amounts

- "59-line comment header": the committed block has **58** comment lines
  (line 1535 tail + 1536–1592), and the branch block is likewise 58 lines
  (1228–1285). The 50 tuple lines are correct (25 × 2).
- "CASES 419 → 444 tuples (results rows 426 → 451)": true of the branch, false
  of the commit (485 → 512 tuples, 492 → 519 rows). Folded into F1/F3, listed
  here so the arithmetic is not mistaken for a rounding artifact.

### F6 — INFORMATIONAL: the landing mechanism is the systemic risk

The lineage shows the pattern, not a one-off:

```
r97 f67094bb  CASES 431  dups {}
r98 9d421fb2  CASES 463  dups {}
r99 254e79dd  CASES 485  dups {crash_spontaneous_sigabrt: 2}     <- +1 from the r99 landing
r100 2dcbb6f6 CASES 512  dups {crash_spontaneous_sigabrt: 3, crash_self_sigkill: 2}  <- +2 more
```

`254e79dd` already carried `crash_spontaneous_sigabrt` ×2, produced by the same
"append the new block onto the previous line" pattern that `2dcbb6f6` then
repeated twice. Any landing that inserts a round block adjacent to the
crash/descendant tail will keep re-emitting those sentinel tuples.
`9ede7c50` dedupes the current instance; the landing step still needs a
post-apply structural assert (e.g. "CASES names are distinct" and
"removing the inserted region restores the parent bytes"), run against the
*committed* tree rather than the author worktree.

---

## 4. Evidence index

| what | where |
|---|---|
| committed bytes under review | `git show 2dcbb6f6:corpus/fixtures/run_battery.py` (sha256 `86a1aef8…`) |
| full-battery run A (committed bytes, lane root) | `corpus/live/runs/20261016T092557629472Z/verdicts.json` → PASS, 519 rows |
| run A console | `corpus/live/r100-reviewer/lane-rep1.out` / `.err`, `lane-rep1.rundir` |
| archive tree (fresh `git archive 2dcbb6f6 corpus/fixtures`) | `/tmp/r100rev-archive` — `run_battery.py` sha256 `86a1aef8…`, all four r100 fixtures hash-equal to the lane's |
| archive full-battery run B | `corpus/live/r100-reviewer/runs-archive3/20261016T093557518876Z/verdicts.json` → PASS, 519 rows; console `archive-rep3.out` / `.err`, `archive-rep3.rundir` |
| archive attempt 1 (died, 38 rows) / attempt 2 (died, 336 rows) | `archive-rep1.out` (`/tmp` path, rc 120), `runs-archive/20261016T092909944110Z` |
| discarded non-committed run | `lane-rep2-DISCARDED-noncommitted-bytes.out` (started after a sibling lane rewrote the tracked `run_battery.py` at 06:34:12 local; 79 rows, killed) |
| author receipts (data, branch bytes) | `…-wt-r100/corpus/live/r100-author/{runs,rows.json,manifest.sha256}` |
| CASES/duplicate re-derivation | `ast.parse` + `ast.literal_eval` over `git show <rev>:corpus/fixtures/run_battery.py` |

---

## 5. Residual risk / verification gaps

1. **Mode portability is cited, not re-encoded.** The boundary's 7-launch-mode
   table (quiet, 16-hog, `--fixed-fps 30/60/120/1`, threaded 2D physics) is the
   stated reason no envelope row is needed, but this commit pins only the
   default headless mode. My re-derivation is therefore single-mode; the
   "no envelope needed" conclusion still rests on the boundary's evidence, and
   the harness's `execute()` cannot express a per-case `--fixed-fps`
   (user args land after `--`), so it cannot be closed row-side without a
   harness change. Not a defect — a bounded claim.
2. **Row-level verdicts are host/engine pinned**: Godot
   `4.7.2.stable.arch_linux.ed1daf0bf`, `--headless`, 64×64 root viewport,
   identity transform, this host. No off-host claim is made or tested.
3. **Load-conditional harness family.** `negative_transition` +
   `probe_error_clause_surface` (`census_bare_classifier_consistent`) is a
   pre-existing coupling the scout documented; it did not fire in my run A.
   Nothing in the r100 block touches `change_scene_to_*`. One green is one
   sample, not proof the coupling is gone.
4. **`r100b_seq_*` are contamination rows by design.** They pin first
   divergences of a single-process replay; a future engine that makes the cells
   composable will FAIL them loudly — correct, but it means these two rows are
   the most engine-version-sensitive of the 25.
5. **Environment hygiene.** The lane worktree's tracked `run_battery.py` was
   rewritten by a sibling lane mid-session (06:34:12 local, sha `35233c8b…`,
   509 CASES) and `HEAD` advanced to `9ede7c50` while this review ran. The
   tracked `.pyc` was already dirty at that point and is a regenerable build
   artifact; I issued no write to any tracked path and committed nothing, and I
   deliberately left the sibling lane's worktree state alone rather than
   restoring a file another lane is using. Run A predates the rewrite (started
   09:25:57Z; 519 rows = the committed count, not the fixed file's 516), so it
   is a committed-bytes run; run B runs from the `/tmp` archive tree and cannot
   be affected by worktree edits at all.

## 6. Host caveats (recorded honestly, per the lane contract)

- `/tmp` is a 16 GiB tmpfs at 79–80 % with a per-user quota. Archive attempt 1
  (outputs on `/tmp`) died at 38 rows with **rc 120** — CPython's exit status
  when it cannot flush stdio — with stdout truncated at exactly one 4096-byte
  block and empty stderr: an ENOSPC, not a test failure. Attempt 2 (same tree,
  outputs on `/home`) was reaped at 336 rows by the session harness (its shell
  exited `-1`) and is **not** counted as evidence. Attempt 3 runs detached
  (`setsid nohup … & disown`) and is the run B cited above. Partial outputs
  from attempts 1–2 showed no failures, but a partial run is not a green run
  and is not reported as one.
- Sibling-lane load (29–49 concurrent batteries, 60 Godot processes,
  loadavg ~10–15) is the reason both committed-bytes runs took ~8–12 min
  instead of the author's ~9 min.
