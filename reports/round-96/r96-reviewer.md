# r96 reviewer — wave-B gate on the committed PackedScene/ResourceSaver/ResourceLoader lattice (`89f85ed8`)

Seat `REVIEWER` (g2d lane r96) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
RendererDummy), Python 3.14.
Reviewed commit **`89f85ed8`** (parent `4a8bb124`); `HEAD == 89f85ed8` at
review end. Diff scope (`git show 89f85ed8 --stat`, re-derived): nine files,
**+2712/−0** — `corpus/fixtures/scene_io_lattice.gd` (+839, new),
`r96b_{cache,id,phase,seq,var,seed}.gd` (+209/+338/+121/+264/+388/+63, new),
`corpus/fixtures/run_battery.py` (**+243/−0**), this report's sibling
`reports/round-96/r96-author.md` (+247). **Zero deletion lines in the whole
commit** — verified by `git diff 4a8bb124..89f85ed8 --numstat` (every row
`N\t0`) and by a three-hunk AST/line audit: CASES block (+198) sits after
`r95b_order_rigid` ahead of the crash/descendant tail, expected_errors (+35)
sits after the r92 block, gate extension (+10) inside
`probe_error_clause_surface`.

**This seat modified no tracked file and made no commit.** Every execution
below ran against the **pinned export** of `89f85ed8`
(`corpus/live/r96-reviewer/pinned-tmp/`), verified byte-identical to
`git archive 89f85ed8 corpus/fixtures` by full-tree `diff -r` (only the
untracked `__pycache__` excluded — it is not in the archive). Seat-owned
writes are untracked only: `corpus/live/r96-reviewer/**` (`manifest.sha256`
covers 2212 files) and this report.

**Dirty-worktree guard (the tree moved under the review).** At review time
the live worktree carries foreign r97-lane state: `M
corpus/fixtures/run_battery.py`, `M
corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`, untracked
`r97_scene_{a,b}.tscn`, `r97_scene_marker.gd`, `stree_lattice.gd`, and many
sibling `corpus/live/*` dirs. None of that was graded: the reviewed bytes are
the commit's, taken exclusively through `pinned-tmp` and `/tmp` scratch
copies. `git status` non-`??` entries at review end are exactly those two
foreign `M` rows; none are mine.

**`lsp` disclosure.** No `lsp` device answers on this host and no
GDScript/Python server is available (same as r89–r95); every symbol-level
statement below is a textual/AST read of the **pinned** committed bytes plus
fresh-process execution receipts — the literal fallback, recorded so it is
never presented as semantic proof.

**Verdict: PASS on the landed bytes.** The landing is exactly what the
dispatch describes — 60 new rows (13 `r96_scene_io_*` + 47 `r96b_*`), pure
insertion, six fixtures byte-identical to frozen boundary probes, one folded
scout probe whose delta is fully declared and accounted, 16 allowlisted ERROR
strings all live-matched, and an extended `r96_expected_errors_all_matched`
floor gate that is proven to discriminate. An independent full battery on the
pinned seed is green 426/426, and my own 36-row fresh-process re-derivation
on committed bytes is 36/36 under the committed classifier. Findings N1–N4
are pre-existing-semantics / documented-context items; **none changes a
pinned byte or a row verdict.**

## 1. What was verified clean

- **V1 — commit shape.** `4a8bb124..89f85ed8`: 9 files, all `N\t0` numstat;
  `run_battery.py` +243/−0 in exactly three insert regions (CASES +198,
  expected_errors +35, gate +10); `project.godot` untouched. CASES
  re-extracted from the committed file by AST: **359 → 419 (+60)**, r96 rows
  = 60 (`scene_io_lattice.gd`×13, `r96b_id`×14, `r96b_cache`×10,
  `r96b_phase`×10, `r96b_var`×7, `r96b_seq`×5, `r96b_seed`×1), **zero
  duplicate case names**. `child_cases.json`/`parent_cases.json` differ from
  the AST extract only in tuple→list JSON shape — faithful.
- **V2 — pinned seed.** `diff -r` of `pinned-tmp/corpus/fixtures` against a
  fresh `git archive 89f85ed8` export: byte-identical across the whole tree.
- **V3 — fixture provenance.** All six `r96b_*` committed fixtures are
  byte-identical to `corpus/live/r96-boundary/probes/` (shas match the
  author's table: `f7d06de3…`, `53a63d65…`, `4bb89614…`, `69a6413f…`,
  `3cae3659…`, `71653a79…`). `scene_io_lattice.gd` =
  `8aeab1cb5492320e…` as claimed; its diff vs the frozen scout probe
  `2eded40b…` is **52 changed lines, every hunk accounted**: fold-header
  comment (+13), L4 law-comment correction, `size_in_190_200`→
  `size_in_176_194` (bound + token), `get_id_path(created)`→
  `get_id_path(sid)` + fold comment, and the extres same-path-resave block
  with the `id_stable_*`→`id_differs_*`/`id_stable_same_path`/
  `same_path_bytes_identical` key re-sign. Zero unexplained bytes.
- **V4 — independent battery on the pinned seed.**
  `runs/20261016T081447869987Z/verdicts.json`: `verdict=PASS`,
  **426/426 rows PASS**, `probe_failing=false`, seed = the pinned export.
  All 60 r96 rows PASS with `signature ∈ output`; census
  `dead_entry_count=0` and every one of the **16 r96 allowlist entries
  `matched_lines ≥ 1`**; `discriminations.r96_expected_errors_all_matched =
  True`; `save-process-verdicts.json` verdict PASS.
- **V5 — my own spot re-derivation on committed bytes**
  (`tools/spot_rederive.py` → `spot_rederive.json`). A fresh scratch was
  built from `pinned-tmp` replicating the battery staging byte-for-byte
  (per-item copy, `MechanicOneShotTest-r96spot` app-name munge, `pickup.tscn`
  stage, `causal_chain` second `await process_frame` fix,
  `.godot/uid_cache.bin` planted as `export_readiness` produces it).
  **36 rows** — all 13 scene_io arms plus 23 r96b rows spanning all six
  fixtures — were launched fresh-process
  (`godot --headless --path <scratch> --script res://<p> -- <flags>`,
  timeout 40 s) and classified by the **committed `classify_process`**
  extracted by AST: **36/36 PASS**, every signature substring-matched, and
  emitted `ERROR:` lines equal the committed allowlist **as exact sets in
  both directions** (ownership 2/2, uid 1/1 — `uid://bqk3m5n7qar1`, refuse
  13/13; no unallowlisted line, no dead entry).
- **V6 — discrimination on the committed classifier**
  (`tools/discrimination.py` → `discrimination.json`; uses the
  `fresh/20261016T080810794707Z` per-row receipts). `genuine` accept 60/60;
  `pin_dropped`, `digit_flipped`, `wrong_rc`, `foreign_error`,
  `truncated_mid_pin`, `cross_case_signature` each **reject 60/60**;
  `bool_flipped` rejects **38/38 where the pin carries a bool token** (the
  22 recorded "accepts" are pins with no `=true`/`=false` — the mutation is
  an identity, not an evasion); `same_arm_sibling_signature` accepts only
  the `idstat_breadth`/`idstat_u31_gate` pair (by design — they pin disjoint
  substrings of one printed line, so a regional flip still fails its own
  row). `prefix_spoof`/`stderr_only` accept 60/60 — see N1.
- **V7 — floor-gate discrimination (control).** `runs-ctl/
  20261016T080936246324Z` ran the battery on `ctl/fixtures` carrying **one
  planted dead r96 allowlist entry** (`"ctlB planted dead r96 entry (never
  matches)"`): `probe_error_clause_surface` → **FAIL**, the entry flagged
  `dead_in_run` by name. The gate a future dead r96 entry would trip is
  proven to fire, not merely to exist.
- **V8 — uid-diagnostic mechanism** (`uid-mechanism/`): the
  `Unrecognized UID` ERROR fires iff the project carries
  `.godot/uid_cache.bin` (silent in both pre-export phases, fires
  deterministically after export readiness with byte-identical
  `uid://bqk3m5n7qar1`). Corroborated negatively by history: the pre-fold
  worktree run `20261016T072821756317Z` shows `r96_scene_io_uid` FAILing on a
  process-random `uid://s3vo6pi07qle` — exactly the falsification that
  motivated the `_arm_uid` fold to the fixed `sid`.
- **V9 — author-run re-read + cross-session identity**
  (`tools/author_runs.py`, `tools/cross_session.py`). Every battery
  `verdicts.json` on disk re-scanned: final-bytes runs `0741` (60/60 r96
  PASS; sole FAIL is the pre-existing `audio_playback` wall-clock flake),
  `0748` and `0754` (**426/426 PASS**, all 16 entries live). Across 658 lane
  receipts + 4 battery runs + my fresh run, **every r96 row emits exactly
  one distinct printed line** — except `r96b_var_idstat_*` (7 variants; the
  `min=`/`max=` tokens are process-random and deliberately unpinned, matching
  the author's declared-substring design).
- **V10 — insertion-only + placement.** The r96 CASES block's neighbors are
  `r95b_order_rigid` before and `crash_spontaneous_sigabrt` after —
  `descendant_pipe_detached_control`'s sleep-8 gap stays adjacent to the meta
  tail as the author claims; the final four CASES tuples are untouched.

## 2. Findings (ranked by severity)

No defects found in the landed bytes. The items below are context /
pre-existing-semantics records, none blocking.

- **N1 (low — classifier semantics, pre-existing corpus-wide).**
  `classify_process` is merged-stream substring matching: in the harness
  forgery matrix, `prefix_spoof` (signature + trailing `extra=1`) and
  `stderr_only` (signature moved to stderr) accept 60/60. This is the
  documented corpus design since r63/r89 — declared-prefix signatures and
  merged streams are deliberate, `classify_streams` exists for rows that
  need a stdout anchor, and all pins still gate exit code, `SCRIPT
  ERROR:`/`Parse Error:`, and every `ERROR:`-carrying line. For the 3
  ERROR-emitting r96 rows (ownership, uid, refuse) a stricter stdout-anchor
  reading also trips on the multi-line GDScript backtrace continuations
  (`   at: …`, `GDScript backtrace`, `       [n] …`), which the production
  classifier treats as inert data — consistent, since only `ERROR:`-bearing
  lines are gated. No action; noted so the spoof surfaces are on record.
- **N2 (low — ordering dependency, author-documented).**
  `r96_scene_io_uid`'s single allowlist entry matches only when the scratch
  carries `.godot/uid_cache.bin`, which the earlier `export_readiness` row
  produces. If a future battery shape drops or reorders that row after the
  r96 block, the diagnostic goes silent, the entry goes dead, and
  `r96_expected_errors_all_matched` fails loudly — verified in V7 that the
  failure mode fires. Correct-by-design; flag is for whoever next edits
  battery ordering.
- **N3 (info — deliberate rare-flip surface).**
  `r96b_var_idstat_breadth` pins `n=200 distinct=200`; 200 minted ids from a
  <2^31 range collide at ~1e-5/run. A flip is a real generator-boundary
  event surfaced deliberately (author-documented), not noise.
- **N4 (info — pre-existing, out of scope).** `audio_playback` remains a
  live wall-clock flake row (run `0741`'s sole FAIL, position frozen
  mid-sample — the documented r69/r72/r73 class). Nothing in the r96 block
  interacts with it.

## 3. Evidence index (seat-owned receipts)

All under `corpus/live/r96-reviewer/` (untracked; `manifest.sha256` covers
every file except itself):

| artefact | path | what it shows |
|---|---|---|
| pinned export | `pinned-tmp/` | `git archive 89f85ed8 corpus/fixtures` equivalent — `diff -r` clean vs a fresh archive |
| static audit | `tools/audit_static.py` → `audit_static.json` | S1 diff shape (+243/−0, three insert regions, parentage), CASES 359→419 |
| author runs re-read | `tools/author_runs.py` → `author_runs.json` | every battery run on disk; final-bytes 0741/0748/0754: 60/60 r96, gate True, 16/16 entries live |
| fresh arm receipts | `fresh/20261016T080810794707Z/` (~540 files) | per-row `.out`/`.err`/`.rc` for all 60 rows, 3 reps |
| my battery run | `runs/20261016T081447869987Z/` | verdicts.json **426/426 PASS** on the pinned seed; `save-process-verdicts.json` PASS; scratch preserved |
| control battery | `ctl/fixtures/`, `runs-ctl/20261016T080936246324Z/` | one planted dead r96 entry ⇒ `probe_error_clause_surface` FAIL — gate discriminates |
| cross-session identity | `tools/cross_session.py` → `cross_session.json` | 1 distinct printed line per row over 658 receipts + 5 runs (2 declared idstat-substring exceptions) |
| discrimination | `tools/discrimination.py` → `discrimination.json` | 6 forgery shapes reject 60/60; committed-classifier sha `749fa060…` |
| uid mechanism | `uid-mechanism/`, `runs/…/missing-preset-scratch/` | ERROR iff `uid_cache.bin` present; deterministic `uid://bqk3m5n7qar1` |
| spot re-derivation | `tools/spot_rederive.py` → `tools/spot_rederive.json` | 36/36 fresh-process PASS on committed bytes; ERROR sets == allowlist both directions (my run, this session) |
| case extraction | `child_cases.json`, `parent_cases.json` | AST extracts (419 / 359); tuple→list-only diffs vs commit re-verified |

Reproduce the headline checks:
`diff -r <(git archive 89f85ed8 corpus/fixtures | tar -x) corpus/live/r96-reviewer/pinned-tmp/corpus/fixtures` — clean;
`python3 corpus/live/r96-reviewer/tools/spot_rederive.py` — 36/36 PASS;
`python3 corpus/live/r96-reviewer/tools/{audit_static,author_runs,cross_session,discrimination}.py`
— the table above.

## Remaining risks / blockers

- The committed pins (`1_vwxho`, `Gradient_xlqlr`, `uid://bqk3m5n7qar1`,
  raw `sha_raw` literals, `size_in_176_194`, …) are host/engine-version
  pinned tokens like the rest of the corpus — reproducible across processes
  at fixed paths on Godot 4.7.2; an engine upgrade would re-mint them. The
  boundary's `proj_alt` family covers project-name independence.
- My spot re-derivation samples 36/60 rows (every arm class and every
  fixture covered); the remaining 24 are covered by the pinned-seed battery
  (426/426) and the 3-rep fresh receipts already on disk — full coverage,
  no gap.
- The live worktree is mid-r97 (foreign `run_battery.py` modification);
  nothing here grades it, and the reviewed commit's bytes are unchanged at
  HEAD.
- **Blockers: none.** Nothing committed; unrelated lanes' untracked
  `corpus/live/` artefacts untouched.
