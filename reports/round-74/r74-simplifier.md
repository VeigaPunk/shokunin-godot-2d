# Round 74 simplifier report — landed LOVE interior-write lattice (`ae6cb16`): weight audit + demonstrated deletion candidates

Seat: simplifier (LEAF, **audit-only** — write scope is this report +
`corpus/live/r74-simplifier/`; no tracked-file edits, no git mutations).
Lane: g2d | Round: 74 | Host: devin (CPython 3.14.7, LOVE 11.5
"Mysterious Mysteries" / LuaJIT 2.1.1788460057, `/usr/bin/love`).

**Audited revision:** commit `ae6cb16` ("r74: LOVE physics interior-write
lattice — {refused|deferred|fatal|applied} partition; 18 IW cells +
love_phys_probe fixture…"), `HEAD` at audit.
Fixture sha256: battery `281f57c8…1f4b4`, phys `main.lua` `2c0ac378…495b5`,
phys `conf.lua` `d2b9e62b…3c808`.
**Committed-run reference:** the r74-author ×4 run dirs
(`corpus/live/r74-author/runs/love-*`) — concatenated `iw-*.stdout.txt`
sha256 = `58af4e7e…801f86`, identical in all four; my scratch baseline run
reproduces that hash byte-for-byte.

## Verdict

- **Deletions made: none** (no tracked edit scope; every candidate below is
  built and measured in scratch copies and listed here for the integrator
  fold).
- **Deletion candidates found: 3** — all in `corpus/fixtures/love_battery.py`,
  all proven **byte-identical at both battery-stdout and raw-receipt level**:
  - **D1** `iw_classify`'s `evpins` parameter + `parse_iw`'s `evpins` return
    (`love_battery.py:288,285`) — dead parameter surface feeding a dead
    return value. **Recommended.**
  - **D2** `iw_flat_extras`'s `return flat` (`:348`) — call site is an
    expression statement that discards it. **Recommended.**
  - **D3** the `evpins` list itself (`:259,277,280-283`) — exists only to
    feed D1; evpin synthesis can be done inline at parse time.
    **Recommended** as the deeper cut (D1+D2+D3 = variant B).
- **Demonstrated-silent but retained (axis-bound), 1 Lua candidate + 2
  defensive branches:** the two `*_unp` witness `EM` lines
  (`love_phys_probe/main.lua:92,96`) and the two defensive classification
  branches (`iw_classify:322`, `iw_flat_extras:338-339`) — §3.2/§4.
- **Preserved contract:** landed battery **37/37 ×4 scratch runs** (baseline,
  variant A, variant B, variant L), exit 0; all prior CASES/SPLICE rows
  untouched; Python variants' 18 `iw-*` receipts byte-identical to the
  committed run.
- **`lsp` disclosure:** no language server answers on this host (pyright /
  pylsp / jedi / lua-language-server / lua-lsp all MISSING; no `luacheck`),
  and the only MCP server (`rea`, Ghidra binary RE) has no source-level
  `references` tool — every call-graph/dead-code claim here is an
  **AST/textual census, not `references` proof** (§7).

## (1) Landed-diff weight census

- `git show ae6cb16 --numstat`: battery **+292/−0**, `love_phys_probe`
  `conf.lua` +20, `main.lua` +234, author report +168. `git diff ae6cb16^
  ae6cb16 -- corpus/fixtures/love_battery.py | grep -c '^-[^-]'` → **0
  removed content lines**: insertion-only, prior rows byte-identical.
- Landed battery 502 lines; new surface: `IW_PROBE_DIR` (:55), `IW_CELLS`
  18 rows (:118-245), `IW_LINE`/`IW_KV` (:247-248), `parse_iw` (:251),
  `iw_classify` (:288), `iw_flat_extras` (:332), IW loop in `main`
  (:448-475).
- **Dead bindings: 0** (`unused_locals.py`: 0 non-underscore
  bound-but-never-read). **Dynamic-access escape hatches: none** (no
  `locals/globals/exec/eval/getattr`), so the census is exhaustive for this
  file.
- **Lua side:** 16 defs, every one has outside mentions except
  `love.load`/`love.update` — engine-dispatched callbacks, a **textual-census
  false positive**, not dead code. All top-level locals are read; no bare
  global assignment. The census's `load(`/`require` "escape hatch" hits are
  `love.load` and a header-comment word.
- **No verbatim helper duplication introduced:** `pos`/`vel`, `pcall_str`/
  `res_str` are single-purpose; `parse_iw` shares no grammar with
  `parse_arms` (different wire format).

## (2) Python deletion candidates — demonstrated with byte-identity proofs

Census basis (`landed_ast_census.py`, textual fallback — no LSP on host):
`iw_classify` `unread_params: ['evpins']`; `parse_iw` returns arity 2,
consumed at `:457` by an unpack whose second target feeds only that dead
parameter; `iw_flat_extras` returns arity 1 and its only call site (`:458`)
is an `Expr` statement (`DISCARDED`). Repo-wide textual census: those
symbols appear only in the landed file and in scratch **copies** of it — no
external importers of `love_battery.py`.

Proof protocol: scratch copy of the committed fixture (sha verified
`281f57c8…`) → build variant → run the full battery → compare against both
(a) a scratch baseline run of the unmodified bytes and (b) the committed
r74-author receipts.

| variant | edit | lines | battery stdout (normalized) sha256 | case-table sha256 | 18 `iw-*` receipts concat |
|---|---|---|---|---|---|
| baseline | — | 502 | `a5ada1ee…` | `2f02419a…` | `58af4e7e…` (= committed) |
| **A** = D1+D2 | `evpins` return+param dropped; `return flat` dropped | 500 | `a5ada1ee…` | `2f02419a…` | `58af4e7e…` |
| **B** = D1+D2+D3 | + evpin synthesis inlined; `evpins` list deleted | 498 | `a5ada1ee…` | `2f02419a…` | `58af4e7e…` |

- A: `python3 variantA/love_battery.py --runs …/runs-A` → exit 0,
  `totals: cases=37 pass=37 fail=0 launch_ok=True done_marker=True exit=0`
  (`runs-A/love-20261014T164427789945Z`). File sha
  `7cb44092…39d0e6a`.
- B: same, `runs-B/love-20261014T164435175657Z`, file sha
  `70cb1cc3…3f95e3a`.
- Both variants' full battery stdout is **byte-identical to the baseline
  run's** modulo the timestamped run-dir token (normalized sha equal); the
  case table is byte-identical outright; the 18 per-cell receipts are
  **byte-identical to the committed run's** (`58af4e7e…`). Verdicts differ
  from baseline only in `{started_utc, probe_dir, probe_elapsed_s}` plus the
  pre-existing *jittered* timing observeds (`dt_max_ms`, `popen_*`) that the
  battery deliberately carries as bounds — no class/pin row changes.
- Why D3 is safe: `flat` is keyed-lookup only (the sole tag scan iterates a
  literal tuple, not `flat`), so evpin insertion order is inert; last-wins
  semantics are preserved for duplicate `evpin` lines.
- Fold target for the integrator: variant B (`corpus/live/r74-simplifier/
  variantB/love_battery.py`, sha `70cb1cc3…`); variant A is the conservative
  subset. Neither creates a second convention: same flat-key grammar, same
  `check()` pins, same classifier.

## (3) Lua-side candidates

### 3.1 `*_unp` witness `EM` lines (`main.lua:92,96`) — demonstrated silent, retained

The two lines after the uncontained calls (`body:setPosition` :91,
`love.physics.newBody` :95) are **unreachable on this build**: the
`loveAssert` Lua error escapes before they run — `grep -c
"cb_setpos_unp pos_after\|cb_newbody_unp nb_pos"` over all 18 committed
receipts → **zero matches**. Variant L deletes them (and folds the dead
`local nb` binding into a bare call; 234 → 232 lines, sha
`18a6ad25…15d3ed`, `luajit -bl` parses):
`python3 variantL/love_battery.py --runs …/runs-L` → exit 0, 37/37 PASS,
battery stdout normalized sha `a5ada1ee…` (identical), case table
`2f02419a…`.

**But the deletion is not receipt-byte-identical:** the crash tracebacks
embed the probe's own source line numbers, and deleting lines above the
crash frames shifts them — `main.lua:95`→`94` (newBody frame), `174`→`172`
(`on_event`), `179`→`177`, `220`→`218`; 16/18 receipts identical, the 2
`*_unp` receipts differ exactly in those traceback lines.
**Retained** (axis-bound): (i) the lines are the probe's own trace of the
*alternate* class — on a build where `b2Assert` is a no-op the write would
apply and the receipt would carry `pos_after`, instead of showing a
completed cell with no mutation trace (the "silent hole" the brief warns
about); (ii) deleting them changes receipt bytes, so the committed
`58af4e7e…` reference would need re-baselining. This is the stop boundary:
the next deletion here trades a diagnostic witness + receipt stability for
2 lines.

### 3.2 Neighbour-deletion falsification (L2 mutant)

Deleting the uncontained **call** instead (variant L2, sha `2f6e040e…`)
flips the cell: `IW_CELL=bc_setpos_unp … love variantL2/love_phys_probe` →
`rc=0`, `CELL_DONE` present, classified `'anomaly' ≠ 'fatal'` → battery
FAIL. So the branch body is load-bearing; only the witness line is silent —
the two are not the same deletion.

## (4) Examined and retained (axis-bound, per r71-r73 convention)

- `flat.setdefault("done", "false")` (`:284`) — **load-bearing**, not
  redundant: without it the `*_unp` cells' `done=false` pin resolves to
  `key missing` → FAIL (demonstrated in-process against the committed
  receipt: landed → `done='false'`, pin reason `None`; minus the line →
  `done=None`, reason `key missing`).
- `iw_classify`'s `unhandled ok=` fallback (`:322`) and `iw_flat_extras`'s
  `assert_txt="other"` branch (`:338-339`) — unreachable under the probe's
  measured grammar, but they are classification-completeness carriers: a
  foreign `ok=` value or a third assertion wording lands as a *named*
  anomaly rather than a crash or a wrong class. Same class r73 ruled
  "diagnostic carriers, not dead code".
- `contact.setEnabled` API-availability branch (`main.lua:120-121`) and
  `pcall_str`/`res_str` — viability/`false`-as-value carriers, reachable on
  other builds; retained.
- The r74 docstring paragraph (`love_battery.py:23-41`) is the measured
  lattice + build record — **provenance explicitly marked historical**;
  never a deletion candidate.
- Pins/classes double-check (class gate + exact pins) is intentional
  belt-and-suspenders, not duplicate authority: they assert at different
  granularities from the same capture.

## (5) Coverage census (verifier row-adds, not deletions)

`landed_coverage.py` over the landed pair: 18 rows, **no duplicate case
names**, **no pinned-but-never-emitted tags** (`final`'s first hit was a
regex artifact; the multi-line `EM` is emitted). Unpinned emitted surface:
`postfire` (post-mutation count/b1pos), `cb_setpos_unp`/`cb_newbody_unp`
(the never-run witnesses), `evpin` (whose keys are synthesized into the
pinned `evpin_<cb>_*`). These are **row-addition candidates for the
verifier**, not deletions — deleting them would remove measurement surface.

## (6) Preserved contract + evidence

- Narrow existing check: the battery itself, run on scratch copies:
  baseline `runs-baseline/love-20261014T164250680780Z`, A
  `runs-A/love-20261014T164427789945Z`, B
  `runs-B/love-20261014T164435175657Z`, L
  `runs-L/love-20261014T164458024884Z` — each `cases=37 pass=37 fail=0
  launch_ok=True done_marker=True exit=0` (`verdicts.json` per dir).
- Committed-run identity: my baseline receipts concat ==
  `58af4e7e1bc6c754de7e3ad8dd55d75b1d1a05f1fbf831968092aeb116801f86`
  (== r74-author ×4). Partition intact: 1 captured + 5 applied + 7 refused
  + 3 deferred + 2 fatal = 18.
- Full command/exit/hash log: `corpus/live/r74-simplifier/proofs.txt`;
  tools: `landed_ast_census.py`, `landed_variant.py`,
  `landed_lua_variant.py`, `landed_coverage.py` (+ reused
  `unused_locals.py`, `lua_census.py` from this dir's earlier, pre-land
  scratch).
- No `git` mutation: `git rev-parse HEAD` unchanged `ae6cb16…`;
  `git ls-files corpus/live/r74-simplifier` empty (all audit artifacts are
  untracked scratch).

## (7) Tracked-tree byte-identity + `lsp` disclosure + scratch provenance

- Post-audit `git status`: `corpus/fixtures/` shows **only** the untracked,
  pre-existing `__pycache__/love_battery.cpython-314.pyc`; the only
  non-untracked entries repo-wide are the two `corpus/live/r72-simplifier/
  {snapshots/log.txt,watch.log}` files that were already modified **before**
  this seat started (present in the session's first `git status`). Fixture
  sha256s above equal `HEAD`'s blobs; the shared tree is byte-identical.
- **`lsp`:** `which pyright pylsp python-lsp-server lua-language-server
  lua-lsp jedi-language-server basedpyright` → all MISSING (exit 7); no
  `luacheck`. MCP servers: only `rea` (Ghidra/binary RE — 173 tools whose
  reference-shaped entries, `procedure_references`/`procedure_callers`/
  `get_call_graph`, are address-scoped native-binary tools, not source
  servers). **No server answers these files**; the textual fallback is
  recorded here and every dead-code claim is AST/textual, never presented
  as `references` proof. Repo-wide grep for the IW symbols finds only the
  landed file and scratch copies — no semantic callers.
- **Provenance note:** this directory's older files (`baseline-hashes.txt`,
  `lsp-disclosure.txt`, `preland-*.txt`, `snapshots/`, `runs-preland/`,
  `del-measure/`) are from the dead pre-land generation (16:0xZ) and audit
  the **pre-land** battery `25977ad9…`; they are superseded by the
  `*_landed*`/`variant*`/`runs-*` artifacts of this report and were not
  overwritten.

## (8) Tradeoffs / remaining unknowns

- D1-D3 are weight-only cuts (502→498 lines, one container, one dead
  parameter, one dead return): zero axis cost here, proven at stdout **and**
  receipt level. They do not change the probe, so the committed
  `58af4e7e…` receipt reference survives the fold.
- L1 is the boundary case: battery-stdout-identical, but receipt bytes
  shift (traceback line numbers) and the alternate-class witness is lost —
  reported, not recommended.
- Unpinned `postfire`/`*_unp` surface stays open as verifier row-adds.
- Same-host scope: all claims are for this LOVE 11.5/LuaJIT build; the
  partition's class pins are the build-independent part, the pose/step pins
  are this-host measurements (author's own caveat).
