# Round 73 simplifier report — landed topology-depth + node-census diff: weight audit + demonstrated deletion candidates

Seat: simplifier (LEAF, **audit-only** — write scope is this report +
`corpus/live/r73-simplifier/`; no tracked-file edits, no git mutations).
Lane: g2d | Round: 73 | Host: devin (CPython 3.14.7, pygame 2.6.1 / SDL
2.32.72, node **v24.21.0**, `io.DEFAULT_BUFFER_SIZE` = 131072 **on this
build**).

**Audited revision:** commit `43bef2d` ("r73: topology depth — infix pin
(paced flush, byte-exact inj@126011) + detach EOF-hold + fd2-merge
inversion + Node.js owner census…"). Probe sha256 `9a7456a3…d0d7f`,
battery `6d3fbf5f…fe79`; `git status` clean under `corpus/fixtures/` at
report time (re-checked after every run below). Pre-land baseline
`2dd108b` (probe `7c0f9c73…`, battery `077af0b5…`).

## Verdict

- **Deletions made: none** (no tracked edit scope; every candidate below
  is demonstrated in a scratch copy and reported, not applied).
- **Deletion candidates found: 3**
  - **new:** `node_major` (probe `:466-480`) — a derived duplicate of the
    pinned `node_version`, zero readers anywhere (§3.1). **Recommended.**
  - **adjacent (pre-existing, unchanged by this diff):**
    `pump_not_needed` + `pump_updates_counted` (battery `:130-131`) —
    assertion-carried rows; re-demonstrated silent on the landed revision
    (§3.2). **Recommended for the hygiene fold** (r72 report's standing
    recommendation; prior-row byte-stability means it belongs in a later
    commit, never a retro-edit of `43bef2d`).
- **Demonstrated-silent but retained (axis-bound), 5 edits:** the r73
  receipt-provenance keys (`chunks_pre/post`, `merge`, detach
  `mode/hold_ms/kill_bound_s`) and the two defensive hygiene lines (fd2
  restore, detach `stdin=DEVNULL`) — each provably silent under the narrow
  check, each retained because the deletion would remove a receipt
  referent or a channel/process-integrity guard (§3.3-3.4).
- **False-positive gates found: none.** Both new mechanism gates were
  falsified by mutation: a stuck detach FAILs `det_wire_eof`
  (`markers_missing`, wall 13.1 s — bounded, not a hang); a write-through
  `node_big` FAILs `nbig_topo` + `nbig_tail` + `nbig_bytes` in one run
  (§5).
- **Landed-diff weight audit:** probe **165+/0−** (insertion-only);
  battery **129+/17−** where all 17 deletions are the raw-wire block
  generalization — **zero CASES/RAW_CASES rows removed**, all 54+1 prior
  rows byte-identical (§2). Zero dead bindings, zero never-emitted pins,
  zero duplicate `(arm,key)` rows, zero unreachable *code* (only
  diagnostic/viability carriers), no verbatim helper duplication.
- **Preserved contract:** landed battery **80/80 ×3** (clean ×2 +
  `PYTHONUNBUFFERED=1` ambient), LOVE sibling **19/19**, prior rows
  byte-identical, `love_battery.py`/`run_battery.py` untouched (§6).
- **`lsp` disclosure:** no `lsp` device in this seat's tool surface and no
  language server on the host (§7) — every call-graph/dead-code claim here
  is an **AST/textual census, not `references` proof**.

## (1) Landing timeline and revision pinning

| time (UTC) | event | evidence |
|---|---|---|
| 15:18:56 | this seat's snapper armed; `HEAD=2dd108b`; fixtures at pre-land hashes | `snapshots/log.txt`, `baseline-hashes.txt` |
| 15:34:17 | probe rev1 `9a983e2b…` detected | `snapshots/log.txt` |
| 15:34:37 | probe rev2 `92ff4963…` | idem |
| 15:34:57 | probe rev3 `9a7456a3…` (final) | idem |
| 15:35:07 | battery rev1 `6e908e6f…` | idem |
| 15:35:27 / :47 | battery rev2 `fb2c400a…`, rev3 `aba0104b…` | idem |
| 15:36:47 | battery rev4 `6d3fbf5f…` (final) | idem |
| 15:43:58 | author commit `43bef2d` | `git log` poll; `git show --numstat` |

The pair moved 7 times while this seat watched; the audit below is on the
committed pair (`landed-sha256.txt`; snapshots frozen in
`snapshots/landed/`).

## (2) Landed-diff weight census (AST/textual, no language server)

Tools (scratch, runnable): `unused_locals.py`, `literal_rows.py`,
`arm_coverage.py`, `weight_census.py`, `case_keyed_diff.py`,
`build_variants.py` (all in `corpus/live/r73-simplifier/`).

- **Shape.** Probe 343 → 508 lines, battery 283 → 395 lines. Emitted
  surface 15 → **22 arms**, 107 → **138 keys**; case surface 55 → **80
  = 73 CASES + 7 raw-wire rows** (4 RAW_CASES entries; the infix entry
  expands to topo + 3 offset rows, `pygame_battery.py:193-211,303-369`).
- **Prior rows byte-identical.** AST row extraction at `2dd108b` vs
  `43bef2d`: all **54 CASES rows** and the r72 RAW_CASES row
  (`self_wire_reorders`) are byte-identical prefixes; 19 + 3 rows
  appended. Siblings untouched (`git diff` empty for
  `love_battery.py`/`run_battery.py`; love sha256 unchanged `25977ad9…`).
- **Dead bindings: zero.** Both files: 0 non-underscore bound-but-never-read
  names (only conventional `_` throwaways); no
  `locals()/globals()/exec/eval/getattr` escape hatches → the census is
  exhaustive for these files. Every top-level def has references outside
  its own body (`weight_census.py`: `node_arm` 3, all others ≥1).
- **Assertion-carried rows: no new ones.** AST emit-literal census
  (`literal_rows.py`) finds exactly 6 literal-valued emitted `(arm,key)`
  pairs; only 2 are pinned, both **pre-existing**: `pump|pump_needed`,
  `pump|frames_nopump` (§3.2). All new `infix|*`, `fd2mrg|*`, `detach|*`,
  `node_*|*` pinned values are computed/measured.
- **No never-emitted pins, no duplicate pins.** `arm_coverage.py`:
  "pinned but NEVER EMITTED: none". Duplicate check over CASES +
  raw-derived case names: none (80/80 unique).
- **Unpinned emitted surface (new, r73):** `infix|chunks_pre/chunks_post`
  (`:446`), `fd2mrg|merge` (`:464`), `detach|mode/hold_ms/kill_bound_s`
  (`:496-497`), `node_census|node_major` (`:477,:480`), `node_big|ret`,
  `node_small|injected_at/tail_at`, `node_sync|injected_at/tail_at`.
  §3 rules each: referent echoes keep, derived duplicate deletes, pin gaps
  are the verifier's row-addition (not a deletion).
- **No verbatim duplication introduced.** Normalized-token ratios (my
  measure): `node_arm` vs `reorder_arm` **0.413** (same spawn/classify
  skeleton, different owners: `node -e` vs caller argv, plus the infix
  class); battery `raw_topo3` vs probe `node_arm` **0.49** (same 5-way
  shape on *different wires* — the battery cannot import probe code);
  `node_arm` vs `withhold_arm` 0.082. In-convention (r72 precedent:
  0.319-class cross-file classifiers accepted; unifying would rewrite r72
  code and create a shared authority, §4).
- **Unreachable branches are diagnostic/viability carriers, not dead
  code.** `markers_missing`/`degenerate`/`premature` and the
  `NODE_EXE is None` / `TIMEOUT_EXE is None` / `except` paths
  (`pygame_probe.py:292-295,306-318,467-476,492-494`) — the same class
  r71/r72 ruled "not a deletion"; the blocked paths are explicitly
  required by the r73 brief ("viability-conditional … never fabricated").

## (3) Deletion candidates — demonstrated with byte-identity proofs

Method: control = verbatim landed pair; each variant = landed pair minus
one edit, run with the narrow existing check (`pygame_battery.py`), then
`case_keyed_diff.py` vs control. "Byte-identity" = the deterministic
receipt table (case/arm/key/pinned/verdict/reasons) matches; only
wall-clock `observed` timing keys differ between runs. Receipts:
`del-measure/r73/{control,v*}/runs/…/verdicts.json`,
`del-measure/r73/diff-v*.txt`; builder `build_variants.py`.

| variant | edit on landed bytes | battery | case-keyed diff vs control |
|---|---|---|---|
| control | verbatim landed copies | **80/80 PASS** | — |
| vA `node_major` | probe `:466-480` drop derivation + emit key (508→506 lines, −157 B) | **80/80 PASS** | cases only in A/B: none; changed non-observed: none |
| vB `chunks_keys` | probe `:446` drop `chunks_pre`/`chunks_post` (−1 line, −41 B) | **80/80 PASS** | none |
| vC `pump_rows` | battery `:130-131` drop the 2 assertion-carried rows (−2 lines, −138 B) | **78/78 PASS** | only A: the 2 rows; totals 80→78 |
| vD `fd2_restore` | probe `:456-463` drop dup/restore scaffolding (−5 lines, −118 B) | **80/80 PASS** | none |
| vE `merge_key` | probe `:464` drop `merge` key (−25 B) | **80/80 PASS** | none |
| vF `detach_keys` | probe `:496-497` drop `mode/hold_ms/kill_bound_s` (−1 line, −70 B) | **80/80 PASS** | none |
| vG `detach_stdin` | probe `:500` drop `stdin=subprocess.DEVNULL` (−1 line, −51 B) | **80/80 PASS** | none |

### 3.1 `node_major` — RECOMMEND (derived duplicate of a pinned key)

- **What it is:** `node_major` is computed from `node_ver`
  (`:477-478`), emitted (`:480`), and **never read**: zero references in
  `pygame_battery.py`; the only other mention in the repo is narrative
  prose in `reports/round-73/r73-author.md` (literal fallback census —
  no language server, §7). The authority for the version is
  `node_census|node_version` (pinned exact `v24.21.0`, battery `:163`);
  `node_major` is a derived view of that pinned value, not a referent of
  any measurement.
- **Proof:** vA — 80/80 PASS, case-keyed diff: no case set change, no
  changed non-observed field. The probe's own docstring/emitted keys are
  unaffected (no pin names it).
- **Why recommended:** deleting removes weight (1 derivation statement +
  1 key + its `absent/error` fallback branches) and a second
  representation of a fact that already has a pinned carrier; it creates
  no second convention (nothing else consumes it). This is the
  "duplicate authority / dead output" class the seat exists for.

### 3.2 `pump_not_needed` + `pump_updates_counted` — RECOMMEND (hygiene fold)

Pre-existing r71-era rows (battery `:130-131`) that pin the probe's own
literals (`pump_needed="false"`, `frames_nopump=400`,
`pygame_probe.py:402`) — they cannot fail for a mechanism reason, only if
the probe's literal changes. vC: 78/78 PASS; the only diff is exactly
those two rows (totals 80→78); everything else byte-identical. Same
finding and same recommendation as the r72 simplifier (§3 there); the r73
diff correctly left them untouched (prior-row byte-stability). Fold in a
hygiene commit with these receipts, not in `43bef2d`.

### 3.3 Receipt-provenance keys — demonstrated silent, RETAINED (vB/vE/vF)

`chunks_pre/chunks_post`, `merge`, `mode/hold_ms/kill_bound_s` are
unpinned literal echoes of the construction/write path/harness bound.
All three deletions are provably silent. **Retained** under the
receipt-referent rule (r72 §4.1 + xconnector pin-honesty; r72-boundary F8
explicitly asked the fd2 cell to name the write path): the receipts
should let a downstream reader interpret the pinned numbers without
re-opening the probe. The stop condition applies: deleting would trade a
few bytes for a weaker receipt, i.e. harm the verdict-integrity axis.

### 3.4 Defensive hygiene lines — demonstrated silent, RETAINED (vD/vG)

- **vD (fd2 restore, `:456-463`):** the battery cannot witness the
  difference — counterfactual capture diff: `probe.stderr.txt` byte-identical
  (334 B, same pygame avx2 warning) and `probe.stdout.txt` differs only in
  wall-clock digits (len 202708 vs 202712). "Silent" here means
  **unobservable by the narrow check, not proven effectless**: without the
  restore, fd2 stays aliased to the fd1 capture for every later arm and
  the process's stderr channel is gone. Deleting a channel-restore line
  whose effect the check cannot see is exactly where this seat stops.
- **vG (`stdin=DEVNULL`, `:500`):** same class — the detached child must
  not inherit the runner's stdin (a detached writer holding an inherited
  stdin is a hang vector for interactive callers; invisible to
  `subprocess.run` here). Retained.

## (4) Considered and rejected — the stop condition

- **4.1 Classifier unification (`node_arm` ↔ `reorder_arm`, ratio 0.413;
  probe ↔ battery `raw_topo3`, 0.49).** *Rejected:* merging rewrites the
  r72 function (this diff is insertion-only by contract), creates a
  shared authority where two independently measured classifiers exist
  today, and the battery cannot import probe code by construction. The
  duplication is the lane's cross-wire convention, not dead weight.
- **4.2 Trim the infix payload (140+60 chunks).** *Rejected:* changing
  the construction re-pins the landed RAW_CASES bounds
  (`injected_rel`, `tail_rel`) — that is a re-pin, not a deletion, and
  the author's measured bounds are load-bearing evidence.
- **4.3 `node_big|ret` (emitted, unpinned).** Not a deletion: `node_arm`
  emits `ret` for all three cells and two rows pin it (`nsm_ret`,
  `nsy_ret`); the big-cell gap is a *pin* gap → a verifier row-addition
  candidate, recorded in §8, not weight.
- **4.4 Absolute `head_at` bound on the infix row (1500, 2600).**
  *Rejected:* measured 2004-2009 across 6 runs (timing-digit jitter ±3 B
  on the preceding wire); the bound is honest and the rel-pins carry the
  mechanism. One row per key is the case-model convention (r72 §4.2).
- **4.5 Blocked/except/`degenerate`/`premature` branches.** Diagnostic
  and viability carriers (r71/r72 precedent); the blocked paths are
  explicitly briefed. Not dead code.
- **4.6 `INFIX_GAP_MIN=64` vs the battery's hardcoded `64`.** Two files,
  two processes; the battery cannot import the probe. In-convention
  (same ruling as 4.1).
- **Stop condition reached:** the next deletions (4.1-4.6 and §3.3-3.4)
  would harm the receipt-provenance, channel-integrity, or case-model
  axes rather than the weight axis. The landed insertion itself is lean:
  no dead code, no redundant branch reachable, no false-positive gate.

## (5) Gate-discrimination receipts (false-positive-gate audit)

A gate that cannot fail is a false-positive gate. Both new mechanism
gates were mutated and **failed as designed**:

| mutant | edit | result | wall |
|---|---|---|---|
| vH `detach_stuck` | `sleep 0.9; printf DETACH-LATE` → `sleep 300` | **FAIL `det_wire_eof`** `'markers_missing' != 'eof_hold' (idx anchor=202678 late=-1)`; rc=1 | 13.1 s (bounded: +4 s kill + EOF) |
| vI `node_big_writethru` | `process.stdout.write('A'*200000)` → `fs.writeSync` | **FAIL ×3**: `nbig_topo 'midline_splice' != 'infix'`, `nbig_tail '65550' outside (199000,200100)`, `nbig_bytes '65555' != '200019'`; rc=1 | 10.0 s |

Receipts: `del-measure/r73/{vH_detach_stuck,vI_node_big_writethru}/…`,
diffs `diff-vH…txt`, `diff-vI…txt` (only the mutated cases' verdicts
change; 17-18 wall-clock keys differ). The infix bound's honesty was
checked independently (§8.6): `injected_rel = 126011` is **exactly stable
across all 6 post-landing runs** (bounds 125000-127500 = ±1 chunk+); a
naive 131011-style pin would have been wrong because the fill-flush
quantum on this build is 126000 B for 1000-B chunks, below the 131072
withholding bound.

## (6) Preserved contract (independently re-verified)

- Fixtures byte-identical to `43bef2d` (`landed-sha256.txt`; `git status`
  clean under `corpus/fixtures/` after every run); this seat wrote only
  inside `corpus/live/r73-simplifier/` + this report.
- Landed battery replay: `runs-landed/…154428826035Z` **80/80, exit 0**;
  second replay `runs-landed2/…154748670504Z` **80/80** (stability:
  case-keyed identical, 18 wall-clock keys differ).
- Env hygiene: `PYTHONUNBUFFERED=1` ambient → `runs-dirty/…154738570720Z`
  **80/80** (the r72 battery-side pop still covers the probe's own-wire
  cells; node/detach children get `CHILD_ENV`/no env dependence).
- Prior rows: all 54 pre-land CASES + the r72 RAW row present with
  unchanged `pinned`/`verdict`, all PASS (byte-prefix check, §2).
- Sibling untouched and green: `love_battery.py` replay
  `runs-love/love-20261014T154525825507Z` **19/19 PASS, exit 0**.
- Hazard evidence (the round's payload, landed run): raw capture reads
  `INFIX-INJ@128018` strictly between `INFIX-HEAD@2007` and
  `INFIX-TAIL@202027` (rel 126011/200020, owner payload both sides);
  `FD2-ERR@202119` before `FD2-HEAD@202127`; `DETACH-LATE@202699` after
  `PYGAME_PROBE_DONE@202681`; `REORDER-CHILD@1891` before
  `REORDER-HEAD@1905`.

## (7) Method and `lsp` disclosure

- **No `lsp` device exists in this seat's tool surface**, and no language
  server answers these files: MCP surface lists only `rea` (Ghidra/binary
  RE — no `references`); `command -v pyright pylsp jedi-language-server
  basedpyright ruff-lsp` → empty/exit 1 (only `lspci` matches "lsp" on
  PATH); `importlib.util.find_spec` for `pylsp/jedi/pyright/multilspy/
  python_lsp_server` → all None; no pipx; `uv tool list` → only unblob;
  npm -g → no language server (`lsp-disclosure.txt`). There is no server
  to start, so there is **no warmup/retry step and no cold-empty result
  recorded as absence** — every dead-code/call-graph claim here is an
  **AST/textual census, stated as such**.
- All demonstrations are scratch copies under
  `corpus/live/r73-simplifier/del-measure/r73/`; the shared tree was
  verified byte-identical before reporting (§6).

## (8) Cross-seat observations (out of scope, bounded, for owners)

1. **Author-report arithmetic drift:** `r73-author.md` says the battery
   diff is "+146/-17"; `git show --numstat 43bef2d` says **129+/17−**
   (146 = total churn). Probe "+165/-0" is exact. The same "+146/-17"
   churn-vs-insertions figure was copied into the in-flight scribe edits
   of `SCORECARD.md` (round-73 calibration row). Scratch/report-level
   only; the artifact is correct.
2. **`node_big` jitter vs bound:** my 4 landed-revision samples observed
   `injected_at=65541` (one pre-final draft sample 98309); the author
   measured 65536/69637/131072. Bound (40000,199000) is justified by the
   spread; `nbig_tail` (199000,200100) + `wire_bytes` exact form the
   second gate. No change recommended.
3. **`writeSync` control caveat (vI side-observation):** a >64 KB
   `fs.writeSync(1, …)` on the probe's nonblocking stdout pipe delivered
   only the 65536-B prefix (wire 65555 B; remainder silently dropped,
   process continued). The "writeSync = write-through control" claim
   holds for the small-write control cell only; worth a critic/verifier
   note if the sync path is ever promoted to a >64 KB cell.
4. **Node-absent host behavior:** the probe emits
   `status=blocked`/`topology=blocked_node_absent` (`:292-295`) but no row
   pins that path, so a node-less host yields battery FAILs with
   `blocked_node_absent` reasons (bounded, never fabricated) rather than
   a battery-level "blocked" verdict. The battery model has no blocked
   state; flagged for the reviewer/verifier as a design note, not a
   deletion.
5. **Stale r72 watcher:** the previous wave's `r72-simplifier`
   snapshot loop (still running until ~15:36 UTC) appended 7 lines to its
   *tracked* scratch logs (`corpus/live/r72-simplifier/{snapshots/log.txt,
   watch.log}` — committed in `2dd108b`) during the r73 landing. Not this
   seat's write; flagged so the wave's report-last commit can decide
   whether to include them.
6. **Infix mechanism (measured here, corroborates the pin):** an
   independent n-sweep (`chunk=1000`: delivered 0 for n≤133, exactly
   126000 at n=140..255, 252000 at 378+, 378000 at 400; chunk=500 →
   0 at n=200; chunk=2000 → 130000 quanta) shows the fill-flush quantum
   on this build is a **textio-layer 126000 B** for 1000-B chunks — below
   the 131072 `io.DEFAULT_BUFFER_SIZE` (two-layer edge, r71/r72 F4
   corroborated). Hence `injected_rel = 11 + 126000 = 126011`, stable
   ×6 runs; the docstring's "126011 = 11 + 126x1000" is exact.
7. **LOG.md round-73 formula is inconsistent with its own number (for the
   scribe/adjudicator):** the in-flight `LOG.md` entry states
   "inj_rel=126011 x4 at the flush-epoch (H + B*floor((131072-H)/B))".
   For the actual construction (H=11, B=1000) that formula evaluates to
   **131011**, not 126011. Measured contrast backing the correction
   (scratch, this host): `sys.stdout.buffer.write` (binary layer,
   same pattern) delivers 131000-quanta (n=400 → 393000), while
   `sys.stdout.write` (textio path, the probe's path) delivers
   126000-quanta (n=400 → 378000) — the single-layer buffer-full formula
   describes the binary layer, not the observed two-layer epoch. The
   *number* 126011 is right (my ×6 + author ×4); the parenthetical
   formula should be corrected or its referent renamed.

## (9) Tradeoffs / stop condition

- The one *new* deletion recommended (`node_major`) is small (−2 lines,
  −157 B in the candidate block) but it is the only genuine dead output
  in the insertion: a derived second representation of a pinned fact.
  Applying it requires author/scribe edit scope (this seat has none);
  receipts are ready (`vA`).
- The two adjacent rows (§3.2) are the r72 standing candidates, still
  correctly untouched by this diff; fold them in a hygiene commit, not in
  `43bef2d`.
- Everything else that is deletable-silent is retained because the
  deletion would weaken a receipt referent or a hygiene guard — i.e. it
  would harm an axis, not the weight axis.
- **Stop condition reached.** No further deletion is proposed; the landed
  insertion passes the weight audit clean (no dead code, no redundant
  reachable branch, no false-positive gate).

## Evidence index (all host-resolvable, this repo)

- Revision/contract: `corpus/live/r73-simplifier/baseline-hashes.txt`,
  `landed-sha256.txt`, `snapshots/log.txt`, `snapshots/landed/`;
  `git show --numstat 43bef2d`.
- Runs: `runs-preland/` (55/55, pre-land control),
  `runs-landed/…154428826035Z` (80/80), `runs-landed2/…154748670504Z`
  (80/80), `runs-dirty/…154738570720Z` (80/80, env sweep),
  `runs-love/love-20261014T154525825507Z` (19/19).
- Censuses: `preland-census-*.txt`, `landed-census-*.txt`,
  `landed-literal-rows.txt`, `landed-coverage.txt`,
  `lsp-disclosure.txt`.
- Deletion proofs: `del-measure/r73/{control,vA_node_major,
  vB_chunks_keys,vC_pump_rows,vD_fd2_restore,vE_merge_key,
  vF_detach_keys,vG_detach_stdin}/runs/…/verdicts.json` +
  `diff-v*.txt`; builder `build_variants.py`.
- Gate mutants: `del-measure/r73/{vH_detach_stuck,
  vI_node_big_writethru}/…` + `diff-vH…txt`, `diff-vI…txt`.
- Tools: `unused_locals.py`, `literal_rows.py`, `arm_coverage.py`,
  `weight_census.py`, `case_keyed_diff.py`, `make_variant.py`,
  `build_variants.py`, `snapshot_loop.sh`.
