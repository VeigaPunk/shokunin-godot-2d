# r98 simplifier — committed-tree audit of the r98 canvas/draw-flush block

**VERDICT: PROVEN-FOLD — 6 folds / 12 deleted constructs / 9 hunks / −38 lines, zero pinned-signature
change.** Every fold was executed head-to-head against committed bytes and the
result is **green on both sides at the lane's committed HEAD**: committed
**516/516 PASS** and folded **516/516 PASS**, identical result sets, **zero
verdict flips**, the `r98_expected_errors_all_matched` floor gate `True` on both,
and all **32 r98 rows classify PASS on both sides under the production
classifier** (`classify_process` extracted verbatim by AST, segment sha256
`3a306a7a4747128b…`, lines 1724–1741). Nothing was landed: this seat reports
candidates only — **zero tracked writes, commit nothing**.

Seat `SIMPLIFIER` (g2d lane r98) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 20 s
per-launch bound), Python 3.14.

**Commit sha verified: `619ad7e069b457a96c09b2fcda937f3fc6025ab2`** (lane HEAD at
report time). The r98 block landed at **`9d421fb2`** and is **byte-identical at
HEAD** — `git diff --stat 9d421fb2 HEAD -- corpus/fixtures/{canvas_lattice,r98b_attack,r98b_rksenum,r98c_flush}.gd`
is empty, and every fixture sha256 still equals the author's landing values
(§1). The lane HEAD **moved twice mid-session** (`2dcbb6f6` → `9ede7c50`,
the integrator's crash-sentinel dedupe, 06:34; → `619ad7e0`, a tracked-pyc
refresh, later); the r98 fixtures and `run_battery.py` were re-verified
byte-identical across both moves, and the final paired batteries were run on
`9ede7c50` bytes, which for every file this fold touches are the `619ad7e0`
bytes as well (`9ede7c50..619ad7e0` changes only the compiled cache).

## 0. Method, and the two honest disclosures

**`lsp` disclosure (upgraded from the lane's standing claim).** There is no
`lsp` device in this session (the only MCP server is a Ghidra/RE server), and no
standalone GDScript/Python language server binary is installed — but the prior
lanes' wording *"no GDScript language server on this host"* is **not accurate**:
Godot's own editor ships one and it **binds the port** here
(`godot --headless --editor --lsp-port 6012 --path <proj>` → `LISTEN
127.0.0.1:6012`). This seat drove it two ways — a hand-written RFC6455 client
(`lsp_client.py`) and Godot's own `WebSocketPeer` (`lsp_probe.gd`) — and
**neither completed the WebSocket upgrade** (raw handshake: no bytes in 30 s;
`WebSocketPeer`: `STATE_CLOSED` after 1200 polls; no server-side log line).
The server therefore **does not answer the file in headless editor mode**, and
call-site absence below is shown by **text-grep as the recorded literal
fallback — never presented as semantic proof**. Every load-bearing claim is
instead proven by fresh-process Godot execution. (Recorded as a lane finding in
§5: a future seat with a display server, or a `lsp` device, can upgrade these
grep claims to `references` proof.)

**Host/space caveats.** Load average 10–16 on 32 cores throughout; six sibling
lane batteries were running concurrently (`r97-verifier`, `r97-simplifier`,
`r97-reviewer`, `r100-verifier`, `r100-simplifier`, `g3d r100-*`). The mandated
`/tmp` archive checkout **could not be used**: `/tmp` is a 16 GiB tmpfs whose
per-user quota was exhausted by sibling lanes (`tar: Cannot write: Disk quota
exceeded` at 218 MiB; even `sort` failed). Archive-tree work therefore ran from
**fresh `git archive <sha> corpus/fixtures corpus/lessons` checkouts under
`/var/tmp/r98sim/`** — same tracked-bytes-only discipline, different filesystem,
disclosed here rather than silently. No sibling lane's file was touched or
deleted.

## 1. Audit scope and committed-byte verification

| file | committed sha256 (HEAD) | = landing `9d421fb2`? |
|---|---|---|
| `canvas_lattice.gd` (791 L) | `866480a1aaa0a385ad5a0e56a3066af4e5341db2e4ab5a5963366aef949394f0` | yes |
| `r98b_attack.gd` (822 L) | `2e71c7158c4f53dbaf5497798cef5cea7769c5799b443ffa5b3a2b289e95a2f8` | yes |
| `r98b_rksenum.gd` (68 L) | `7bb519025cba6bb2102fcc96eaf72938955fa180d4b52871f76b12742174f76a` | yes |
| `r98c_flush.gd` (272 L) | `c038f748a8572e4164fc0f6586199805b60f90929bdbed742bfcb7be28e1932e` | yes |
| `run_battery.py` | `35233c8b2edbd45c…` (HEAD) | +3/−2 integrator dedupe only |

The **byte-copy provenance claim is true at HEAD**: `cmp` is clean for all four
fixtures against the author's frozen upstream probes
(`…-wt-r98/corpus/live/r98-author/probes/*.gd`), and each sha256 equals the
upstream manifest entry. Block shape at HEAD: **32 r98 rows** (15
`r98_canvas_*` + 16 `r98b_*` + 1 `r98c_flush`) on **30 distinct launches**
(2 duplicate-launch pairs, §5), **3 allowlist entries / 3 strings / 2 distinct**,
**1 floor gate**, **59-line comment header**.

## 2. The folds (proven, executed, diff-reviewable)

Applied by `apply_fold.py` (exact-text replacements, each asserted to fire once;
9 hunks / 12 deleted constructs, deletions only — no additions, no renames, no new
conventions):

| # | file | site | committed lines | why it is dead weight | proof |
|---|---|---|---|---|---|
| **F1** | `canvas_lattice.gd` | `var methods: Array = []` + `methods.append(nm)` in `_arm_census` | 126, 130 | append-only accumulator, **never read** file-wide; the arm reports `draw_n` from the sibling `drawm` array | file-global scan + `r98_canvas_census` byte-identical |
| **F2** | `canvas_lattice.gd` | `_notif_keys()` helper | 103–110 (8 lines) | **zero call sites** in committed bytes | grep fallback (LSP unavailable, §0) + full battery |
| **F3** | `r98b_attack.gd` | `var owner_ref` in `class QF` + `t.owner_ref = self` | 119, 173 | declared, dotted-assigned, **never read** anywhere | file-global scan + `r98b_qflush_*` full-line identity |
| **F4** | `r98b_attack.gd` | `var pfs: Array = []` in `class QH` + `pfs.append(...)` in `_draw` | 144, 147 | append-only, never read; `QH` is consumed only as `h.draws` | file-global scan + `r98b_qflush_*` full-line identity |
| **F5** | `r98b_attack.gd` | `_arm_env()` arm + its `match` branch + its header line + its section banner | 33, 57, 804–822 | **unreachable adapter**: no CASES row launches `--arm=env` (the author declared `r98b_env` *"deliberately NOT authored … pins no law"*) | arm-vs-row census + `--arm=env` cell run on both sides (§3.3) |
| **F6** | `r98b_rksenum.gd` | `var _items: PackedStringArray = []` + `_items.append(...)` in `_it` | 6, 12 | write-only accumulator, **never flushed or read** (the PASS line is built directly) | file-global scan + `r98b_rksenum` byte-identical |

**Net line delta: −38** (`canvas_lattice.gd` −10, `r98b_attack.gd` −25,
`r98b_rksenum.gd` −3, `r98c_flush.gd` 0; `run_battery.py` 0). 791→781,
822→797, 68→65.

Dead-store detection was a **file-global** occurrence scan (r95/r96
`deadstore_scan.py` method, hardened: inner-class member *reads* written as
`obj.member` count as reads, dotted writes count as writes). The naive
scope-labelled scan reports **82** "dead stores" across the four files
(29 + 32 + 1 + 20) — almost all of them inner-class members that the arm body
reads as `obj.member` and that a scope-labelled walk cannot see; the hardened
file-global scan collapses that to **4** (1 + 2 + 1 + 0) (plus the zero-call-site helper and the
unreachable arm found by separate censuses). **All four stores survive a
deliberate attempt to call them live** — the h2h emits byte-identical full PASS
lines for the cells that exercise them (§3.1), so this is the r96
"grep-clean ≠ dead" trap tested rather than reasoned: `owner_ref` in particular
is a *keep-alive-shaped* binding (a node holding `self`) and was folded only
after execution showed the full `qflush` line unchanged, including its unpinned
keys.

## 3. Verification

### 3.1 Narrow check — head-to-head cell runs, both trees at HEAD

`cell_harness.py` stages each side exactly as `run_battery.py` stages its own
scratch (every `corpus/fixtures` entry except the battery, project-name munge,
`controls/pickup.tscn` at root) and launches
`godot --headless --path <scratch> --script res://<fixture> -- <flags>`
**interleaved** (committed, folded, committed, folded) so load drift hits both
sides equally: **33 cells × 2 reps × 2 sides = 132 launches**, `timeout -s KILL
20`, 0 timeouts, 0 non-zero rc except the declared `env` case.

| result | count |
|---|---|
| full stdout byte-identical, both reps | **62 / 66 pairs** |
| full-record (stdout+stderr+rc) differences | **10**, every one in a declared class (§3.2): 6 stderr-only backtrace line-number pairs, 2 `qorder` tick-phase pairs, 2 the declared `env` removal |
| non-zero rc | 2 — **both the declared `env` case**; 0 timeouts, 0 slow (>5 s) launches |
| `Parse Error` / `SCRIPT ERROR` anywhere | **0** |
| rows PASS under the production classifier | **32 / 32 on both sides, both reps** |

### 3.2 Every byte difference, classified (none is semantic)

| class | cells | what differs | why non-semantic |
|---|---|---|---|
| **A — backtrace line numbers** | `r98_canvas_clip`, `r98_canvas_draw_refusal`, `r98b_clipmatrix` | only `res://…gd:NNN` inside the engine's GDScript backtrace (e.g. `_arm_clip …gd:436` → `:426`, `_frames …gd:77` → `:75`) — exactly the deleted-line count above each arm | the allowlisted ERROR line itself is byte-identical; the census re-confirms `bare_classification_rejects=True` and matched lines **1 / 2 / 6** on both sides. Same declared class as r96's `res://*.gd:\d+` mask |
| **B — declared tick-phase keys** | `r98b_qorder_tree` (rep1) and `r98b_qorder_flat` (rep2) — `stagger`, `stagger_off`; in the full battery also `r98b_qflush_same_frame` (`hide_span_pf=2`→`3`) | keys the author **explicitly excluded** from the pinned signatures ("tick-phase dependent within a batch and across batches … pinning them would pin the host's scheduling") | the same keys differ **between two committed-side reps with no fold involved** (`r98b_qorder_flat` committed rep1 ≠ rep2 in both h2h runs), and the pinned prefix/substring is present on both sides in every rep (rows PASS) |
| **C — the removed unauthored arm** | `r98b_env_REMOVED_ARM` | committed `PASS r98b env …`, folded `FAIL r98b env reason=unknown_arm`, rc 0→1 | **no CASES row launches `--arm=env`**; this is the fold's only intentional behaviour change and is stated as the tradeoff in §4 |

### 3.3 Full battery, both sides on the same commit

`python3 corpus/fixtures/run_battery.py`, fresh `git archive 9ede7c50`
checkouts, run in parallel:

| | committed `head-committed` | folded `head-folded` |
|---|---|---|
| results | **516** | **516** |
| verdict census | **516 PASS / 0 FAIL** | **516 PASS / 0 FAIL** |
| payload `verdict` | `PASS` | `PASS` |
| r98 rows | **32/32 PASS** | **32/32 PASS** |
| `probe_error_clause_surface` row | PASS | PASS |
| gates | **49 / 49 true** | **49 / 49 true** |
| `r98_expected_errors_all_matched` | **True** | **True** |
| r98 allowlist census | 3 entries — clip **1**, draw_refusal **2**, clipmatrix **6** matched lines; `dead_in_run=false`, `bare_classification_rejects=true` | **identical** |
| `dead_entries` | `[]` | `[]` |
| row-set diff | — | `[]` (no row only on one side) |
| verdict flips | — | **`[]`** |

A second committed-tree green was taken at the pre-move HEAD (`2dcbb6f6`,
lane-repo root as the task mandates): **519/519 PASS**, r98 32/32, gate `True`,
same census — i.e. the block is green on both sides of the integrator's dedupe
as well.

## 4. Preserved contract and the one tradeoff

**Preserved:** every pinned signature of all 32 rows (verified by the production
classifier on both sides); every emitted byte of every *pinned* PASS line; all
three allowlist entries with their matched-line counts and their
`bare_classification_rejects` property; the `r98_expected_errors_all_matched`
floor gate; all provenance/history comments; every side-effecting call in the
retained arms. No rename, no new convention, no second authority.

**Tradeoff — the byte-copy chain (must be re-stated if the fold lands).** F1–F6
edit three fixtures that are *byte-copies* of the frozen scout/boundary probes.
Landing them means:

1. `canvas_lattice.gd`, `r98b_attack.gd`, `r98b_rksenum.gd` are no longer
   byte-identical to `corpus/live/r98-scout/probes/…` /
   `corpus/live/r98-boundary/probes/…`, so the in-code provenance
   (`run_battery.py` r98 header: `BYTE-COPY sha256 866480a1aaa0a385…` /
   `2e71c7158c4f53db…`) becomes **stale** and must be restated as "byte-copy
   minus the folded sites" (3 text edits, **0-line** change) — a stale-sha
   comment left in place would be exactly the stale-name defect this seat
   removes.
2. The boundary's `--arm=env` launch-mode fingerprint can no longer be re-run
   from the landed fixture (F5). Its receipts stay frozen at
   `corpus/live/r98-author/runs/*/r98b_env.rep*.out`; the claim it supports
   ("not authorable — pins no law") is unaffected.
3. `r98c_flush.gd` is untouched, so the author's own new probe remains a
   byte-copy.

If a reviewer judges the byte-copy chain load-bearing, **F5 is the one fold to
drop** (it is also the largest single site, −19 lines): F1–F4/F6 (−19 lines)
leave all four arms reachable and keep the three byte-copy files as
"byte-copy-minus-dead-stores", which is a smaller provenance edit than removing
an arm.

## 5. Rejected candidates (deliberately NOT folded) and report-only findings

Rejected — each would harm an axis:

- **The two duplicate launches** (`r98b_qflush_same_frame`/`_suppress` share
  `--arm=qflush`; `r98b_qorder_tree`/`_flat` share `--arm=qorder`): 2 extra
  engine launches (~1.4 s of a ~9 min battery). They are **not** redundant
  assertions — each row pins a *disjoint slice* of the same PASS line (the
  prefix ends before the excluded keys, the other row's substring begins after
  them), and the harness's only multi-payload form is ANY-of, not AND-of. The
  fold that would remove the launch also removes a claim. Report-only.
- **The 59-line r98 comment header** in `run_battery.py`: duplicates the author
  report's boundary-decision table, but it is *in-harness provenance* in the
  established r87–r97 shape — deleting it is prohibited by the seat card
  ("never delete provenance explicitly marked historical").
- **The three `expected_errors` strings** (the clip string appears twice, once
  per case): the allowlist is keyed by case name; sharing them needs a new
  module-level constant, i.e. a second convention for one line.
- **`r98c_flush.gd::_arm_flush` vs `r98b_attack.gd::_arm_qflush`**: structurally
  similar, but a rewrite (different classes, sequencing and key sets), not a
  deletion; folding them would mean a shared helper — a new convention.
- **The 78 scanner false positives** (82 scope-labelled "dead stores" − the 4
  real ones): inner-class members read as `obj.member` from the arm body, e.g.
  `QT.events`, `NT.counts`, `SUBJ.draw_pf_counts` — all live; recorded so a
  future seat does not re-derive them as dead.
- **`--arm=` dispatch uniformity**: `r98c_flush.gd`'s 3-line `match` for a
  single arm could collapse to a direct call, but that would make one fixture a
  different convention from the other three. Kept.

Report-only findings (no line delta, or outside this seat's remit):

- **`r98b_rksenum`'s count duplicates `r98b_skewgrid`'s**: `nz_fail_n=60`
  (rksenum) and `rks_fail_nz=60` (skewgrid) pin the *same* law twice; the
  rksenum row's unique content is `sign_pairs=++=24,-+=12,+-=12,--=12`. Not a
  duplicate authority (each row still carries a unique claim), but the block
  measures the 60 once more than it needs to.
- **`r98b_visphase` re-pins 8 keys that `r98_canvas_vis_chain` already pins**
  (`hide_in_tree`/`hide_notif`/`hide_sig`/`hide_hidden_sig`/`hidden_queue_n`/
  `restore_in_tree`/`restore_n`/`hide_noop`); its unique content is the five
  `tick_*` keys. The duplication *is* the scheduler-invariance claim, so it is
  evidence, not weight — but it is the block's one cross-fixture re-assertion.
- **Signature-form heterogeneity**: 27 rows pin a full `PASS …` line, 3 pin a
  declared gating prefix, and **2 pin a bare substring with no case anchor**
  (`r98b_qflush_suppress` = `hide_ticksep_n=1 hidden_across_tick_n=0
  show_after_tick_n=1`; `r98b_qorder_flat` = `flat=CBACBA`). Those two rows
  would admit a reordered foreign line containing the same contiguous run. A
  hardening candidate for the author, not a simplification.
- **Entry splice still glued** (same defect class the integrator fixed for the
  two crash rows at `9ede7c50`): the r98 block's banner comment
  (`# --- r98 block: …`) is still glued onto the *tail of the previous tuple's
  line* (`'PASS stree_lattice scene_probe …'),    # --- r98 block: …`).
  Semantically inert; splitting it costs **+1** line, so it is a formatting fix,
  not a fold.
- **Author-report arithmetic**: `r98-author.md` §`run_battery.py changes` says
  "`expected_errors` += 3 entries / **4 strings**"; the committed dict has
  **3 entries / 3 strings / 2 distinct**. The in-code comment ("two refusal
  cells") is correct; the report line is stale. Reports are provenance and were
  not edited.
- **Tracked `__pycache__` artifact**: `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`
  is a *tracked* file that any lane running the battery from the repo root
  regenerates (457 028 → 456 798 B here — exactly the 456 798 B that HEAD
  `619ad7e0` commits). It is an artifact of the mandated full-battery check, not
  of the fold; at report time it is byte-identical to HEAD (§7).

## 6. Evidence index

Lane-repo scratch (untracked, `corpus/live/r98-simplifier/`):
`apply_fold.py` (the fold, reproducible), `deadstore_scan.py` +
`deadstore-scan.txt`, `global_scan.py` + `global-scan{,2,3}.txt` (the hardened
file-global scan), `cell_harness.py` + `h2h.stdout`, `h2h-head.stdout`,
`classify_rows.py` + `classify-rows.txt`, `classify-rows-head.txt`,
`lsp_client.py`, `lsp_probe.gd`.

Archive-tree evidence (`/var/tmp/r98sim/`, fresh `git archive 9ede7c50`):
`head-committed/`, `head-folded/` (folded trees), `head-committed-battery.log`
+ `head-folded-battery.log`, the two `verdicts.json`
(`head-committed/…/20261016T093732006405Z/` sha256 `dc09a33166c250ee…`,
`head-folded/…/20261016T093734002929Z/` sha256 `acb2e97e62f9b342…`),
`battery-compare.txt`, `row-emission-diff.txt`, `h2h-head/` (132 receipts),
`h2h/` + `h2h-tmpfs-run1/` (the earlier `/tmp` replication),
`lsp-server.log`. Pre-move committed green:
`…/game-dev-2d-shokunin/corpus/live/runs/20261016T092554544775Z/verdicts.json`
(519/519).

## 7. Shared-tree state at report time

- `git rev-parse HEAD` = **`619ad7e069b457a96c09b2fcda937f3fc6025ab2`**
  (`9ede7c50` + a tracked-pyc refresh; the r98 fixtures and `run_battery.py` are
  unchanged across it).
- All four r98 fixtures + `run_battery.py`: **byte-identical to HEAD**
  (re-verified sha256 at report time).
- This seat's writes: `corpus/live/r98-simplifier/**` (untracked scratch) and
  `reports/round-98/r98-simplifier.md` (this report). The tracked
  `run_battery.cpython-314.pyc` that the mandated lane-root battery run
  regenerates was restored with `git checkout --` (a no-op at report time: it
  was already byte-identical to HEAD), leaving `git status --porcelain` with
  **zero modified tracked files** and only pre-existing/own untracked
  `corpus/live/*` entries. **Zero commits, zero staging.**
- Sibling-lane files: read-only (the author's `wt-r98` receipts and probes were
  read via `cmp`/`sha256sum`; nothing under `wt-r98` was written).

## 8. Blockers

**None for the fold** — both sides are green at the same commit with identical
censuses. The two residual conditions a reviewer should weigh: (a) the
byte-copy-chain tradeoff in §4 (drop F5 if provenance outweighs −19 lines), and
(b) the `lsp` device is still unavailable to this seat, so F2's "zero call
sites" and F1/F3/F4/F6's "never read" rest on the hardened file-global scan plus
full-battery execution, not on a semantic `references` answer.

— r98 simplifier, seat output; the canonical Rust runtime judges.
