# r97 simplifier — fold audit of the r97 landing block (`f67094bb`)

**VERDICT: PROVEN-LEAN.** The r97 landing block carries a verified
**−21-line fold** (`stree_lattice.gd` 941→924, `r97_scene_marker.gd` 7→3,
60 call sites re-pointed) that was executed in a scratch copy and proven
inert end-to-end: **48 fresh headless launches** (12 battery rows × 2 reps ×
committed vs folded) with **0 byte diffs**, the folded bytes **byte-equal to
the frozen r97-scout `rep1` receipts on 12/12 rows**, and the **real battery
green on both sides** (committed 516/516, folded 516/516, all 12
`stree_lattice_*` rows PASS with byte-identical recorded outputs, every
`*_expected_errors_all_matched` gate `True`). Nothing was landed: this seat
reports candidates only; **zero tracked writes, commit nothing**.

Seat `SIMPLIFIER` (g2d lane r97) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 8 s per
launch — the harness's own per-case bound), Python 3.14. Audit target: commit
`f67094bb9cbf665242f85499c59e8b2f59cd5531` (*r97 author: SceneTree
groups/signal-flags/call_deferred lattice*, 6 files, +1199/−0). All scratch
work under `corpus/live/r97-simplifier/` (gitignored); committed bytes staged
from `git show f67094bb:…` and verified sha256-equal to the working tree
before any run.

## 1. Audit scope and byte verification

| file | sha256 (truncated) | state at report time |
|---|---|---|
| `stree_lattice.gd` | `61954f87…` | 941 lines; blob `58603345…` **identical at `f67094bb` and HEAD** |
| `r97_scene_a.tscn` | `c86d5674…` | identical to `f67094bb` |
| `r97_scene_b.tscn` | `7c153f7f…` | identical to `f67094bb` |
| `r97_scene_marker.gd` | `39763310…` | identical to `f67094bb` **and** to the scout's `corpus/live/r97-scout/proj/scene_marker.gd` (byte-identity claim independently re-verified) |
| `run_battery.py` r97 block | 55 lines (12 tuples + gate + provenance comment) | tuple data and the gate expression byte-identical at `f67094bb`, `2dcbb6f6` and HEAD `619ad7e0`; the only live difference is an r98-appended trailing comment on the `scene_probe` row line (see §6.3) |

The r97 block's provenance claims were checked against the tree, not taken on
trust: probe sha `4dd18e10…` (896 lines) matches, the fixture sha256 is the one
recorded in `reports/round-97/r97-author.md`, the mint-era
`scene_a.tscn`/`scene_b.tscn`/`scene_marker.gd` fixtures are indeed load-bearing
for `controls/scene_transition_probe.gd` (`marker=` on a `Node` root, verified
in that file), and the receipt census behind the harness comment checks out
(48 scout + 36 loadtest receipts present; the boundary's 216 = 36 receipts ×
6 modes, per r97-boundary §7/§10).

## 2. `lsp` disclosure — the lane's first semantic reference proof

The seat card requires semantic call-site proof through the `lsp` device
"whenever a server answers the file". Device inventory first: the only MCP
server on this host is `rea` (Ghidra/reverse-engineering; no LSP tool), and
r89–r96 recorded "no `lsp` device / no GDScript language server". **That
recording is now superseded: Godot's own editor binary hosts the GDScript
language server**, and it answers `textDocument/references` for these files.

Recipe (so sibling lanes can reuse it — recorded verbatim because the obvious
form silently does something else):

```
godot --headless --editor --lsp-port <1024-49151> --path <project>   # server
# then JSON-RPC over TCP, Content-Length framed:
#   initialize -> initialized -> textDocument/didOpen -> textDocument/references
```

`--lsp-port` **without** `--editor` makes the binary *run the project* instead
(it dies `Can't run project: no main scene defined`), so a port-watch loop
that only tries the bare flag records a false "no server". Client:
`corpus/live/r97-simplifier/lsp_refs.py`.

Measured answers (`lsp-refs.json`, `lsp-refs-marker.json`, `lsp-refs-xfile.json`):

| symbol | refs | composition |
|---|---|---|
| `_tree_names` (fixture) | **1** | **declaration only — zero callers** |
| `it_valid` | 52 | decl + 51 call sites |
| `it_connected` | 7 | decl + 6 |
| `it_paused` | 4 | decl + 3 |
| `_it` (control) | 103 | decl + 102 (== text-grep count) |
| `_snap` (control) | 41 | decl + 40 (== text-grep count) |
| `ready_ticks` (marker) | 2 | decl + its own `+= 1` — nothing reads it |
| `_ready` (marker, control) | 7 | name-matched across `camera_proc.gd`, `causal_pickup.gd`, `pickup.gd`, `input_lattice.gd` + this file |

Cold/warm discipline per the seat card: every probe was issued **twice**
(2 s after `didOpen`, then again after 8 s) and both passes returned identical
results — no cold-index empty is recorded as absence. Cross-file reach was
validated with a scratch-only two-file control (`lsp_xfile_a.gd` defines
`lsp_xfile_target`, `lsp_xfile_b.gd` calls it): references returned **both**
locations, so "1 ref" means "nowhere in the project", not "nowhere in this
file".

Honest bound, stated rather than glossed: Godot's reference matching is
name-based over parsed script text — it also returned a *comment* occurrence
(`tag` at `r97_scene_marker.gd:2:59`). It is therefore an **over-approximating
absence proof** (if a name appeared anywhere, it would be listed), from a
second, engine-side implementation, not a type-resolved call graph. Every
load-bearing claim below is additionally proven by fresh-process execution.

## 3. Proven fold (executed in scratch, verified)

`fold.py` builds the proposal from committed bytes by exact-string
replacement; `fold-proposal.diff` is the reviewable result (88 `−` / 67 `+`
diff lines, net **−21**). Nothing else changed.

**F1 — dead helper, −4 lines.** `_tree_names()` deleted. Semantic proof:
LSP refs = declaration only (§2); corroborated by text grep (1 occurrence) and
by 24 launches emitting identical bytes.

**F2 — duplicate emit convention, −4 lines, 51 sites.** `it_valid(key, value)`
was a pure forwarding alias of `_it`; every call site now calls `_it` and the
alias is gone. One name per operation instead of two.

**F3 — duplicate emit convention, −4 lines, 6 sites.** `it_connected(key, v)`
folded to the two primitives it wrapped: `_it(key, _v(v))` (the `_v` bool
conversion is preserved, not dropped).

**F4 — duplicate emit convention, −4 lines, 3 sites.** `it_paused(n)` folded to
`_it("paused_seen", str(n))` — same key, same `str()` conversion.

**F5 — duplicate authority for a law, −1 line.** `_arm_defer_ladder`'s comment
restated the *general* L10 law (the exact duplicate-authority shape that went
stale this round and needed the authorfinish fix). The fold keeps the
arm-local clause — what this arm does and does not pin (boundary §2.3) — and
points at the header laws block, which is the single authority. `_arm_defer_order`
already used that pointer form, so this removes an inconsistency rather than
introducing a convention.

**F6 — dead fixture field, −4 lines.** `r97_scene_marker.gd`: `ready_ticks`
(never read; LSP refs = decl + its own increment) and the `_ready()` that only
increments it. The marker's contract — `Node2D` root, `@export var tag`, node
name — is untouched.

## 4. Verification method and results

**Narrow check, row level** (`verify_folds.py`): both sides staged exactly as
`run_battery.py` stages its scratch project (fixture copy, project-name munge,
`controls/pickup.tscn` staging, causal-chain two-frame fix), then all **12 r97
rows × 2 reps × 2 sides** run at `--headless` with the harness's own 8 s bound:

```
committed: 24 launches   folded: 24 launches
row diffs: []            rows byte-identical: 12/12
signature present: 12/12 both sides      rc=0: 12/12 both sides
ERROR: lines: none on either side
folded == frozen scout rep1 receipts: 12/12
```

**Detector teeth** (the check must be able to fail): (a) a launch without
`--arm=` fails `FAIL stree_lattice  reason=unknown_arm`, rc=1, identically on
both sides — which also independently verifies the harness comment's claim
that the arm token is load-bearing; (b) a deliberate 1-token mutation
(`count`→`countx`) in the folded bytes is visibly caught by the signature
check.

**Narrow check, battery level**: the real `run_battery.py` was run on a copy of
the fixture directory with the folded bytes swapped in, and on an unmodified
copy, in the same host session — both against the **same harness bytes**
(`run_battery.py` sha256 `35233c8b…`, re-verified at report time as the blob
committed at the current HEAD `619ad7e0`), each ~8 minutes at
loadavg ~13–16:

```
                          committed (HEAD bytes)      folded (F1–F6)
verdict                   PASS                        PASS
rows                      516/516, 0 FAIL             516/516, 0 FAIL
row set                   identical (no delta)        identical (no delta)
r97 rows                  12/12 PASS                  12/12 PASS
r97 recorded outputs      byte-identical 12/12 (identical per-row sha256)
discriminations           49/49 True                  49/49 True
allowlist gates           15/15 True (r97 gate True)  15/15 True (r97 gate True)
```

(row counts are `verdicts.json` result rows; the log's extra `PASS battery:`
line is the summary print. HEAD's harness carries 516 rows because r98–r100
landed after this block.)

`paired-battery.json` holds the per-row comparison. A *first* folded run (see
§8) had been executed on the then-HEAD harness blob (`86a1aef8…`, committed at
`2dcbb6f6`, before the mid-session integration dedupe) and also came back green
with all 12 r97 rows PASS — corroboration that the fold is inert across the
harness revisions that landed during the session, not a substitute for the
HEAD-blob pair above.

## 5. Rejected candidates (kept deliberately)

- **`_v()`'s float/int/Array branches** — unreachable from today's 35 call
  sites (all bool or Vector2), i.e. a textbook dead alternate path. **Kept**:
  these branches are the formatter's declared `Variant` contract, and folding
  them would silently change a future float emission (`3.0` vs `3.0000`) —
  a contract change disguised as weight removal, not weight removal.
- **`r97_expected_errors_all_matched`** (vacuously true today) — **kept**: it
  is one of 15 identically shaped `*_expected_errors_all_matched` gates
  (r87–r100) that make a future dead allowlist entry fail loudly. Deleting it
  would create a one-off convention and remove a floor.
- **Provenance comment blocks** (fixture header, harness r97 block, author
  report) — explicitly historical provenance plus the measured laws; never
  deleted. F5 *points at* that authority instead of duplicating it.
- **Engine-called entry points** (`_initialize`, `_run`, `_ready`) — text
  occurrence counts of 1 are not evidence here; the engine calls them (the LSP
  control shows `_ready` implemented in four other fixtures).
- **The r97 harness block itself** — 12 tuples + 1 gate + provenance comment:
  no deletion candidate; every claim in the comment verified true (§1).

## 6. Report-only findings (not folded)

1. **Duplicate key tokens inside 5 of the 12 signatures** (4 if the
   `defer_order` frame-group repeats count as intentional grouping) — `first`
   twice (`group_order`, `group_order_rev`), `paused_seen` twice
   (`group_flags`), `tag` twice (`scene_probe`), and `df`/`ord` repeated per
   frame group (`defer_order`). Same class r96 §5 recorded:
   the first occurrence is dead output weight, but the row signature pins the
   whole line, so removal is not byte-neutral — flagged for the author, not
   folded.
2. **Stale line count in the author report** — `r97-author.md` records the
   fixture as `61954f87… (937 lines)` and "+41 lines" over the 896-line probe.
   The sha256 matches the landed bytes, but the landed file is **941 lines
   (+45)**. Report-only staleness (the count appears to predate the
   authorfinish comment edit).
3. **r98 smeared the r97 block boundary** — the live harness's `scene_probe`
   row line (1281) carries the r98 block banner appended to it by the r98
   landing. The r97 tuple data is unchanged; cosmetic, and outside this lane's
   remit to touch.
4. **The `it_*` wrapper layer is droppable independently** — F2/F3/F4 each
   stand alone; if a reviewer prefers the named wrappers for readability, the
   dead-helper and duplicate-law folds (F1/F5) still stand on their own.

## 7. Preserved contract

Every emitted byte of every `stree_lattice_*` PASS line and diagnostic, every
exit code, the 12 CASES signatures, the `r97_expected_errors_all_matched` gate
(0 r97 allowlist entries, still live), all provenance comments, the three scene
resources' semantics (`tag`, node names, `ext_resource` paths),
`project.godot`, and the harness code itself are preserved. The fold is
strictly weight removal: no renames of emitted keys, no new conventions, no
second authorities — and it removes three.

## 8. Shared-tree state at report time

- `git rev-parse HEAD` = `619ad7e069b457a96c09b2fcda937f3fc6025ab2`; **no tracked
  modifications** (`git status --porcelain` clean apart from untracked files).
- All four r97 fixture files: **byte-identical to HEAD** (sha256 re-verified at
  report time; §1 table). `stree_lattice.gd`'s blob (`58603345…`) is unchanged
  from `f67094bb` through the two mid-session commits.
- HEAD advanced during the session: `2dcbb6f6` (r100 author) → `9ede7c50`
  (r97–r100 integration: dedupe of duplicate `crash_*` sentinel CASES rows,
  a union-merge splice artifact) → `619ad7e0` (pyc refresh). The dedupe is
  **outside the r97 block**: the 12 r97 tuples and the
  `r97_expected_errors_all_matched` expression are byte-identical at
  `f67094bb`, `2dcbb6f6` and `619ad7e0` (re-verified), so the audit target and
  the §4 pair's predicates are unaffected by the landing.
- `corpus/fixtures/run_battery.py` at report time = `35233c8b…` = the blob both
  §4 batteries ran on. My *first* folded battery ran on the `2dcbb6f6` blob
  (`86a1aef8…`, which still carried the spliced duplicate crash rows) and was
  green with all 12 r97 rows PASS.
- Tracked `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`: clean at
  report time (refreshed by the integration commit). Foreign battery runs
  regenerate it transiently — **not this lane's write**: every run in this
  audit used copies under `corpus/live/r97-simplifier/`.
- This seat's writes: only under `corpus/live/r97-simplifier/` (gitignored) and
  this report. Zero tracked writes, zero staging, zero commits.

## 9. Evidence index (all under `corpus/live/r97-simplifier/`)

- `fold-proposal.diff`, `folded/`, `fold.py` — the proposed fold, reviewable.
- `fold-verification.json`, `fold-runs/` — 48-launch committed-vs-folded diff
  (0 diffs) + scout-receipt comparison.
- `lsp-refs.json`, `lsp-refs-marker.json`, `lsp-refs-xfile.json`,
  `lsp_refs.py` — semantic reference proof, controls, cross-file control.
- `battery-committed.log` + `battery-committed-runs/` (HEAD harness, committed
  bytes), `battery-folded2.log` + `battery-folded2-runs/` (HEAD harness, folded
  bytes), `battery-folded.log` + `battery-folded-runs/` (first run, foreign
  in-flight harness), `paired-battery.json` + `paired_battery.py` — the paired
  battery runs and their r97 row comparison.
- `battery-folded/`, `battery-folded2/`, `battery-committed/`,
  `proj-committed/`, `proj-folded/`, `proj-mutant/`, `proj-xfile/`, `stage.py`
  — staged scratch trees.
- `tree/` — committed r97 bytes, sha256-verified.

## 10. Blockers

**None.** Stated tradeoffs, for the integrator: F2–F4 trade three readable
wrapper names for a single emit convention across 60 sites (each fold is
independently droppable); F6 is the only fold with a documentation cost — its
landing turns `r97_scene_marker.gd`'s "byte-identical to the scout's
`scene_marker.gd`" provenance row into "folded from … (simplifier F6)", so drop
it if this round's convention is byte-identity to the scout resource. Landing
any part of the fold requires updating the fixture sha256 row and adding the
fold note in `reports/round-97/r97-author.md`; the harness bytes need no change.

— r97 simplifier, seat output; the canonical Rust runtime judges.
