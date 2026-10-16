# r97 reviewer — wave-B gate on the committed SceneTree groups / signal-flags / `call_deferred` lattice (`f67094bb`)

Seat `REVIEWER` (g2d lane r97) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps),
Python 3.14.7.

Reviewed commit **`f67094bb`** (r97 author; parent `d5c05ff8` — r96 adjudicate).
`HEAD` at review start `2dcbb6f6` (r100 author): **the worktree moved under the
review**, so nothing below is graded from it — every executed claim comes from
a **pinned export of `f67094bb`** (`corpus/live/r97-reviewer/pinned/`,
`git archive f67094bb`) whose identity against the commit's own tree I verified
blob-by-blob: **125,147 regular blobs + 68 symlinks, 0 missing, 0 mismatch**
(`git ls-tree -r f67094bb` vs the export; symlink targets compared to the blob
content). `corpus/fixtures/` in that export is **all real files, 0 symlinks**
(the r67-era symlink trees live elsewhere and are irrelevant here).

Diff scope re-derived (`git diff d5c05ff8..f67094bb --numstat`, all six rows
`N\t0`): 6 files, **+1199/−0** — `stree_lattice.gd` (+941, new),
`r97_scene_{a,b}.tscn` (+7/+7, new), `r97_scene_marker.gd` (+7, new),
`run_battery.py` (**+65/−0**), this report's sibling `r97-author.md` (+172).
`project.godot` untouched. **Zero deletion lines in the whole commit.**

**This seat modified no tracked file and made no commit.** The only seat-owned
writes are `corpus/live/r97-reviewer/**` (untracked; `manifest.sha256` covers
the 21 receipt files, `runs/` and `pinned/` excluded as regenerable — `runs*/`
is covered by the tracked `corpus/live/.gitignore`) and this report
(`git ls-files reports/round-97/r97-reviewer.md` is empty). Note: the
dispatch's "corpus/live gitignored" is **only partially true** on this tree —
`corpus/live/.gitignore` ignores `runs/`, `runs*/`, `**/__pycache__/`,
`**/.godot/`, but the seat directories themselves are untracked-and-visible.

**Dirty-worktree guard (the tree moved under the review).** At review end the
only non-`??` `git status` entry is
`M corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` (mtime 06:34:12,
size 457028→456798) — a **foreign** sibling-lane artifact, not this seat's:
every Python invocation of this seat was `ast.parse`/`json`/`hashlib` reads,
and both of my batteries executed the **pinned** copy with cwd inside the
pinned export (which still carries the commit's own pyc, mtime 06:17:38,
untouched). Concurrent r97/r98/r100 lanes were running their own batteries and
import-time compiles throughout. Nothing was graded from the live worktree, and
this seat neither repaired nor reverted the foreign entry.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript/Python
language server on this host (the same null-lsp class r89–r97 recorded;
`definition`/`references`/`diagnostics` were **unavailable for every file**).
Every symbol-level statement below is a textual/AST read of the **pinned**
committed bytes plus fresh-process execution receipts — the literal fallback,
recorded so it is never presented as semantic proof.

**Verdict: PASS on the landed bytes (recommendation).** The landing is what the
dispatch describes: 12 new `stree_lattice_*` rows, pure insertion, a folded
scout probe whose delta is **comment-only plus two declared scene-path
renames**, byte-identical emitted output to the frozen probe's canonical
receipts, zero allowlist entries, and an r97 floor gate wired into a real row
verdict. Two independent full batteries on the pinned commit are green
**438/438** with all 12 r97 rows byte-identical to the scout's canonical `rep1`
receipts, plus a 12/12 independent manual arm re-derivation in a scratch
project I built myself. Findings F1–F3 are **report/claim-accuracy** items and
F4–F5 are informational; **none changes a pinned byte, a row verdict, or the
gate**.

## 1. What was verified clean

- **V1 — commit shape.** `d5c05ff8..f67094bb`: 6 files, every numstat row
  `N\t0`; `run_battery.py` **+65/−0** in exactly **two** insert regions —
  CASES block (new lines 1228–1281: comment header + 12 tuples) and the gate
  (new lines 3574–3584). No `EXPECTED_ERRORS` hunk at all. `project.godot`
  absent from the commit. The r97 block sits after `r96b_seed_seedcheck`
  (line 1226) and **before** the crash/descendant tail
  (`crash_spontaneous_sigabrt` line 1282, `descendant_pipe_detached_control`
  line 1284) — i.e. it does **not** sit between
  `descendant_pipe_detached_control` and the meta probes, honouring the
  harness's sleep-8 adjacency rule stated in the file's own comments.
- **V2 — fixture identity.** All four landed fixture hashes equal the report's
  table (`stree_lattice.gd` `61954f87…`, `r97_scene_a.tscn` `c86d5674…`,
  `r97_scene_b.tscn` `7c153f7f…`, `r97_scene_marker.gd` `39763310…`), and
  `r97_scene_marker.gd` is **byte-identical to the scout's**
  `corpus/live/r97-scout/proj/scene_marker.gd` (`39763310…`) while the
  mint-era `corpus/fixtures/scene_marker.gd` is a different file (`fa72c254…`)
  — the namespacing claim holds.
- **V3 — the 12 rows reproduce.** Two independent full batteries on the pinned
  export (`python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot
  --runs …/r97-reviewer/runs`, `timeout -s KILL 1800`):
  `20261016T092302758669Z` and `20261016T093441519684Z`, both **PASS,
  438/438 rows (431 CASES + 7 meta), 0 failures**, all 12 r97 rows PASS with
  `out_uniq=1` across my two runs. Independently of the battery harness, I
  built my own scratch project (`corpus/live/r97-reviewer/manual/`: committed
  `project.godot` + `stree_lattice.gd` + the three `r97_scene_*` resources) and
  ran **all 12 arms by hand**: **12/12 PASS, rc=0, 0 B stderr, committed
  signature present**, each in <1 s.
- **V4 — signature provenance (the pinned laws are the scout's own bytes).**
  For each of the 12 rows the committed signature is **byte-equal to the full
  `PASS` line** of its canonical scout receipt — **48/48** canonical reps
  (`r97-scout/runs/r97_*.rep{1..6}.out`), **36/36** loadtest reps, **216/216**
  boundary-mode reps (`r97-boundary/runs/{quiet,load,ff30,ff60,ff120,ff1}/
  scout_*.rep{1,2,3}.out`) — and all 12 of the author's own final-run row
  outputs are **byte-identical to the frozen scout `rep1` receipts**; my two
  runs reproduce the same bytes. This is the strongest available form of the
  fold's "zero emitted-byte change" claim: the committed fixture emits the
  frozen probe's bytes on three independently driven harnesses (scout driver,
  author battery, my battery + my manual scratch).
- **V5 — the fold is comment-only apart from the declared rename.** A
  line-classified diff of the frozen probe (`896` lines, sha `4dd18e10…`) vs
  the committed fixture yields exactly **77 comment lines + 2 code lines**
  (4 diff lines counting both sides): `change_scene_to_file("res://scene_a.tscn")`
  → `"res://r97_scene_a.tscn"` and `load("res://scene_b.tscn")` →
  `"res://r97_scene_b.tscn"`. **Zero other code changes** — no behaviour,
  no arm logic, no new/removed statements.
- **V6 — the rename is behaviour-neutral and was necessary.** The arm's only
  scene readback is `_csname()` = `"%s tag=%s" % [current_scene.name,
  current_scene.get("tag")]` (line 263) — the path never reaches output, so
  the byte-equality in V4 is expected, not lucky. The incompatibility claim is
  real: mint-era `corpus/fixtures/scene_a.tscn` is `type="Node"` + `marker =
  "A"` and `controls/scene_transition_probe.gd` reads
  `old.get("marker") != "A"` (line 28), while the r97 arm reads `tag=` on a
  `Node2D` root — so the namespaced copies are required, not cosmetic.
- **V7 — the `--arm=` column correction was load-bearing.** The scout's
  `author-rows.py.txt` carries **zero** `arm=` tokens (every row's flags field
  is `[]`), and the probe's dispatch ends `_: _fail("unknown_arm")` (line 138).
  I ran the committed fixture with no user args: `FAIL stree_lattice
  reason=unknown_arm`, rc=1. The author's added `--arm=` flags are therefore a
  correctness fix to the scout's row list, correctly declared in the report and
  in the CASES comment header.
- **V8 — zero allowlist entries, and the floor gate is real.** Every r97 row's
  `expected_errors` is `[]` in the committed CASES block and in my run records,
  so `classify_process` requires **no** `ERROR:` line at all (strictly stronger
  than an allowlist). `r97_expected_errors_all_matched` is the 46th key of
  `sf_discriminations` (dict spans lines 3366–3585), which feeds
  `sf_meta_ok = all(sf_discriminations.values())` → the
  `probe_error_clause_surface` row verdict: a future dead r97 entry flips a row
  to FAIL, exactly as the report claims. Today the generator is empty
  (`census_rows` skips entry-less rows), so the gate is **vacuously True** —
  which the author states honestly ("`expected_errors` += 0 entries").
- **V9 — the rows discriminate.** Across my 12 manual arm outputs: **no**
  row signature is contained in any other arm's output (0 cross-acceptances);
  the `--rev` negative control does not cross-accept in either direction; and
  a one-token mutation of each signature is rejected by its own output
  (12/12 rejects). Combined with V4, the pinned rows are the scout's own
  stability evidence rather than a weakened form.
- **V10 — the flake accounting is exact.** The author's seven `verdicts.json`
  receipts read `PASS, PASS, FAIL, PASS, FAIL, PASS, PASS` with failures
  `['negative_transition', 'probe_error_clause_surface']` (run
  `084014089634Z`) and `['nav_lattice_region']` (run `085730720181Z`) — verbatim
  what the report records. All 12 r97 rows PASS in **all seven** runs
  (**84/84 row-instances**), `out_uniq=1` per row across the seven runs. The
  cascade claim is exact: of the 46 `probe_error_clause_surface`
  discriminations, **only** `census_bare_classifier_consistent` differs between
  the failing and passing runs (False vs True) — a pure cascade, as stated.
  Neither flake touches an r97 row.
- **V11 — boundary-driven comment corrections match the cited measurements.**
  The corrected L10 ordering is the boundary's own decisive keys, which I
  re-read in **all six modes × 3 reps**: `dproc_before_sig=true`,
  `dproc_after_sig=false`, `resume_after_sig=true` in every receipt; and the
  header clause "a call queued FROM a process_frame listener … is served
  before the next frame's `_process` pass" is **measured**, not inferred: in
  every frame group of every `defer_phase` receipt the `D_sig(qN)` entry
  precedes the `nodeproc` entry (**108/108 groups checked**, 6 modes × 3 reps ×
  6 groups). The two rewritten arm comments (`_arm_defer_ladder`,
  `_arm_defer_order`, lines 720/864) now state only what those arms pin and
  point at the corrected header law; the old text was the sentence
  `r97-boundary` §2.3 quotes and refutes.

## 2. Findings (by severity)

- **F1 — (low, report metadata) the landed fixture's line count is wrong in
  the report.** `reports/round-97/r97-author.md` says `stree_lattice.gd` is
  `937 lines` and the fold is `+41 lines`; the committed blob is **941 lines**
  (`git show f67094bb:corpus/fixtures/stree_lattice.gd | wc -l` = 941, and the
  numstat is `941\t0`), i.e. **+45** over the 896-line frozen probe. The
  recorded sha256 does match the committed bytes, so this is a stale count, not
  a different artifact. No payload or row is affected.
- **F2 — (low, report + commit-message arithmetic) CASES counts are off by
  one.** Report §"run_battery.py changes" and the commit message both say
  "CASES 420 → 432 tuples". AST extraction of the committed file
  (`ast.literal_eval` over the `CASES` list; all entries 5-tuples) gives
  **431** rows (12 `stree_lattice_*`), and the parent `d5c05ff8` gives **419**
  — so the delta is `+12` as claimed but the absolutes are `419 → 431`. The
  sibling claim "results rows 426 → 438 incl. meta" is **correct**: my runs
  report 438 rows = 431 CASES + 7 meta (`probe_save_independent_process`,
  `probe_spontaneous_crash_classification`, `probe_descendant_pipe_eof`,
  `probe_descendant_signature_spoof`, `probe_while_live_signature_gate`,
  `probe_descendant_error_spoof`, `probe_error_clause_surface`), and the
  parent's 426 = 419 + 7 follows (parent row count not re-executed by this
  seat; the 426 figure is the r96 reviewer's independently counted total).
- **F3 — (low, evidence-strength wording) "three consecutive" is not what the
  receipts show.** The report's "**Green ×2 on the final bytes — three
  consecutive at the end**" and the commit message's "438/438 **x3
  consecutive** on final bytes" overstate the run sequence. Re-derived from the
  seven `verdicts.json`: `P P F P F P P` — on the final (post-comment-fix)
  bytes the runs are `F P F P P`, so the tail is **two** consecutive greens
  (`090413067379Z`, `091032696916Z`) and **three** greens total
  (`084924888991Z` included, non-consecutive). The report body's own table and
  flake section are honest about this; only the headline phrase and the commit
  subject are wrong. No flake is hidden and no pin was weakened.
- **F4 — (informational) the r97 floor gate is vacuous today.** As declared:
  no `stree_lattice_*` row carries an allowlist entry, and `census_rows` skips
  entry-less rows, so `all(...)` over an empty generator is True. The
  mechanism itself is sound (V8) — the note exists so the next reader does not
  mistake "gate True in 7 runs" for evidence that an r97 allowlist entry was
  exercised.
- **F5 — (informational) the corrected header L10 keeps one inherited
  inference.** `await <signal>` "resumes AT EMIT TIME (same frame, **inside the
  emitting stack**)" replaces the refuted "before the deferred flush" clause;
  the boundary only pins `resume_after_sig` / `frame1=[pf_sig,resume]` ("at or
  after the signal"), so "inside the emitting stack" is engine-truth but not
  itself receipt-pinned. The refuted universal is gone from both the header and
  the two arm comments — which is the round's actual defect fix — so this is a
  documentation-precision note, not a defect in the landed payload.

## 3. Residual risk and verification gaps

- **Shared machinery.** My re-derivation shares the engine (`4.7.2.…ed1daf0bf`)
  and the battery harness (itself part of this commit) with the author. The
  mitigation is the *scout's* separately driven receipts (different driver,
  same engine) plus my own manual arm runs outside the harness; a harness-level
  classifier defect would still be shared by all three.
- **Pre-fix bytes are unrecoverable.** The "comment-only fix, zero emitted-byte
  change" claim cannot be re-run against the pre-fix fold state (it was never
  committed). It is verified transitively and more strongly: the committed
  fixture's emitted bytes equal the **frozen probe's** canonical receipts
  (V4), and the probe→fixture diff contains no non-comment change except the
  two declared path renames (V5).
- **Full-line order vectors are deliberately stricter than the measured
  equivalent.** The boundary measured `ROWS_PREFIX` equivalent to full-line
  rows; the author shipped full lines. A future engine bump will therefore fail
  loudly on vector cells — intended, but it means an engine upgrade must
  re-verify before relaxing, exactly as the author's blocker (b) states.
- **Host sharing and flake classes.** The two recorded flakes are outside this
  round's rows; the `nav_lattice_region` first-query path divergence
  (`[(20,60),(80,60),(90,50)]` missing the origin waypoint while the arm's own
  sync gate passed) remains an open observation on an r91 fixture — the
  author's blocker (a), unchanged by this review and not re-exercised here.
- **`await physics_frame` idle index** stays a distribution except at a 1:1
  idle:physics ratio; no r97 row pins it (by design) — the header says so.
- **Parent-side counts.** The parent's 419 CASES is AST-derived from
  `d5c05ff8`; the parent's 426-row battery total is not re-executed by this
  seat (arithmetic + r96's independent count only).

## 4. Reproduce

```bash
# pinned export of the reviewed commit (identity-verified against the tree)
git archive f67094bb | tar -x -C corpus/live/r97-reviewer/pinned
# two independent full batteries (green ×2, 438/438 each, 12/12 r97 rows)
cd corpus/live/r97-reviewer/pinned && \
  timeout -s KILL 1800 python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --runs ../runs                        # run dirs 092302758669Z, 093441519684Z
# 12/12 independent manual arm re-derivation (own scratch, no battery harness)
#   scratch = committed project.godot + stree_lattice.gd + r97_scene_{a,b}.tscn + r97_scene_marker.gd
for a in census group_order group_flags group_lifecycle group_setters signal_order \
         signal_flags defer_ladder defer_slots defer_order scene_probe; do
  timeout -s KILL 8 /usr/bin/godot --headless --path corpus/live/r97-reviewer/manual \
    --script res://stree_lattice.gd -- --arm=$a
done
# + 'group_order --rev' for the 12th row; receipts in corpus/live/r97-reviewer/manual_*.{out,err}
```

Receipts: `corpus/live/r97-reviewer/{manifest.sha256, probe_vs_fixture.diff,
committed_run_battery.py, parent_run_battery.py, committed_stree_lattice.gd,
runs/20261016T092302758669Z/, runs/20261016T093441519684Z/, manual_*.out|err,
pinned/}`.

**Return:** report `reports/round-97/r97-reviewer.md`; **verdict PASS
(recommendation)** on `f67094bb`; findings F1–F3 (report/claim accuracy, no
payload impact), F4–F5 informational; **blockers: none** for the landing.
