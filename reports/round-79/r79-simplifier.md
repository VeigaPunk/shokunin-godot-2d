# game-dev-2d round 79 — simplifier (g2d): three proven deletions in `phys2d_events.gd`, battery block survives audit clean

Seat `SIMPLIFIER` (LEAF) | lane `g2d` | round 79 | wave `shokunin-train-20261101` | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python
3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD `884a4c4` (r78
report-last) — **no commit by this seat, no tracked file written, no git
mutation**. The r79 landing stands untouched: `corpus/fixtures/phys2d_events.gd`
still sha256 `7329acb22a144b3c…` (scout pin) and `corpus/fixtures/run_battery.py`
still sha256 `9cb5253113f2c2ed…` (baseline-observed post-write digest).

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed and no
GDScript/Python language server is installed (`pylsp`, `pyright`, `clangd` for
these sources ABSENT). Deletion-candidate proofs therefore rest on (a) complete
textual enumeration of every reader of the suspect state, and (b) fresh-process
receipt equivalence of the *folded* battery against a same-session control and
the author/baseline freezes — the narrow existing check, run verbatim. No
cold-start empty result is recorded as absence; grep output is never presented
as semantic proof on its own — the battery receipts are the semantic carrier.

**Writes:** this report and `corpus/live/r79-simplifier/**` only.

---

## 1. Method

Per brief: hunt only what is **provably** removable — unreachable `CASES` rows,
emitted keys no battery reads, branches covered by a cheaper cell, comments
contradicting code. For each candidate the proof bar is: apply the diff in a
scratch copy → the full battery still runs 111/111 → every prior row's verdict
tuple is identical.

Workspace (all under `corpus/live/r79-simplifier/`):

| artefact | content |
|---|---|
| `vfold/` | the fold as full file copies: `phys2d_events.gd` (**503 lines**, sha `cd103d0a…`), `run_battery.py` (**byte-identical** to fixtures, sha `9cb52531…` — audited, nothing provably dead) |
| `fold.diff` | unified diff `corpus/fixtures` → `vfold`; **−24/+1 lines, all in `phys2d_events.gd`** |
| `vfold-fixtures/` | runnable folded project: full `corpus/fixtures/` copy with the vfold pair swapped in (`diff -qr` vs fixtures: exactly one differing file, `phys2d_events.gd`) |
| `control-runs/20261015T051454229720Z/` | same-session battery on the **unmodified** tree → **111/111 PASS** |
| `fold-runs/20261015T051725980038Z/` | battery on `vfold-fixtures/` → **111/111 PASS** |
| `receipts/` | both batteries' stdout/stderr (stderr empty both), `fold-compare.txt`, per-run tuple sets |
| `MANIFEST.sha256` | covers the fold, diff, receipts, and both `verdicts.json` |

Batteries ran **sequentially** (never parallel) with absolute `--runs`, per the
author's observed constraints.

## 2. Killed — three deletions, all in `phys2d_events.gd`

### K1. Stale arm census comment — header lines 7–28 (−21 net)

**What it was:** a `# Arms` block enumerating 20 arms with one-line semantics.
**Why dead:** it is a **second arm index that has already drifted** — it omits
`cm_max0_cb`, `area_node_position`, and `area_dss_in_cb`, three of the 23 arms
the `match arm:` dispatch (`:82–100`) actually reaches. Its grouping duplicates
the section banners (`---- tier arms` / `contact_monitor arms` / `RigidBody2D
interior window` / `Area2D interior window`). Every listed line is accurate, but
as a census it silently misstates the file (a reader counts 20; the battery
drives 23). Options were delete vs complete; completing perpetuates a duplicate
authority already proven to drift, so the census is deleted and replaced by one
line: `# The \`match arm:\` dispatch in _run is the sole arm index (23 arms).`
Per-arm semantics live in `r79-scout.md` §1.1 and the section banners.

**Proof:** comments are unreachable by any output path; receipt-level
confirmation below (all 111 rows' normalized outputs identical to control,
including byte-identical `PASS` lines on all 23 phys2d rows).

### K2. `_in_cb["cls"] = other.get_class()` — was `:320` (−1)

**What it was:** a store of the collider's class into the RigidBody2D-window
callback dict.
**Why dead:** every read of `_in_cb` goes through `in_cb.get(key, "-")` in
`_arm_cm` (`:385–392`) and `_arm_rb` (`:426–438`). Full enumeration of the
written keys — `cls, count, colliders, monitor, max, srv_read, node_unchanged,
srv_before, node_read, queued, freed, dss_null, q_hits, readback` — against the
read set shows **`cls` is the only key never read**. Asymmetry confirmed rather
than assumed: the area twin `_area_in_cb["cls"]` (`:447`) **is** read
(`cb_cls=%s`, `:515`) and is **kept**.

**Proof:** deleting the store removes one never-read key from a duplicated dict;
no `.get("cls")` exists on that dict. Receipt-equivalent — see §3.

### K3. `_area.monitoring = true` — was `:490` (−1)

**What it was:** explicit init of the probe `Area2D`'s `monitoring` property,
which defaults to `true` on `Area2D.new()`.
**Why dead:** pure redundant initialisation. Crucially it is **fail-closed**
dead weight: the arm pins `cb_monitoring=true` and `post_monitoring={true,false}`
verbatim, so if the engine default ever stopped holding the rows would FAIL, not
silently drift. The folded run measured `cb_monitoring=true` on all seven area
arms — the redundancy is confirmed by the pin itself, not just asserted.

**Proof:** receipt equivalence on the seven `area_*` rows (and no other row
touches `_area`).

## 3. The proof — receipt equivalence, not suspicion

`compare.py godot` (the r79-baseline seat's own differ, reused unmodified):
stable verdict tuple per row (case, script, flags, expected_exit, actual_exit,
signature, verdict, error, expected_errors) + normalized-output compare;

| ref | common | tuple_mismatches | output-normalized identical | differing |
|---|---|---|---|---|
| **same-session control** (unmodified tree) | 111 | **0** | **104** | **0** |
| author run A `045301…` | 111 | **0** | **104** | **0** |
| author run B `045607…` | 111 | **0** | **104** | **0** |
| baseline freeze rep1 (88-row era) | 88 | 1* | 79 | 2* |
| baseline freeze rep2 | 88 | 1* | 79 | 2* |

\* the only deltas vs the pre-r79 freeze are the r79 **landing's own** expected
changes, identical in folded and control runs: `new_only=23` (the new rows), the
`probe_error_clause_surface` census content (39→43 expected_errors rows,
41→53 ERROR: lines), and the `(28 steps)`→`(29 steps)` class-registration
banner on the two export rows. None are fold-introduced — the control run
exhibits the same three against the same freeze.

**Strongest single artifact:** `receipts/godot-tuples-{fold,control}.txt` —
the two 111-row tuple sets are **byte-identical** (`diff` empty). Every prior
row's tuple is preserved and all 23 phys2d rows produce byte-identical `PASS`
lines under the fold. Fixture parse: `godot --headless --check-only --path
vfold-fixtures --script res://phys2d_events.gd` → exit 0, no diagnostics.

## 4. Kept — audited candidates that did not survive proof bar

| candidate | verdict | reason |
|---|---|---|
| all 23 `phys2d_events_*` `CASES` rows | **keep** | every one reachable and PASSing in both fold and control runs; each pins a distinct cell (window × write-kind lattice, incl. the paired rb/area twins — same signature shape, different gate) |
| all 4 `expected_errors` entries | **keep** | scout's `errors_dropped` ablation FAILed exactly these 4 rows; the dict is load-bearing per entry |
| ordering comment `run_battery.py:96–102` | **keep** | accurate and load-bearing documentation of the measured `descendant_pipe_detached_control` ordering razor (author §1.2) |
| `run_battery.py` phys2d block wholesale | **keep, zero diff** | nothing in the +67 is provably dead — fold copy ships byte-identical so `vfold/` is a complete drop-in |
| `_:` unknown-arm match arm | **keep** | fail-closed dispatch guard; unreachable from CASES but is the fixture's negative path — removing changes the typo failure mode from `FAIL unknown_arm` to silent hang→timeout |
| `print("R79 arm=…")` header | **keep** | live diagnostic output every run (engine/backend/thread readout used by scout's threaded-twin evidence); not dead |
| `.duplicate()` on `in_cb` (×3) | **keep** | defensive snapshot of cb dict; removing saves zero lines and weakens the frozen-after-guard idiom — churn, not weight |
| `_entries/_exits.append(other.get_class())` | **keep** | only `.size()` is read, but the element documents the stored signal payload; rewriting to `append(1)` saves nothing and obscures |
| `var body := other as RigidBody2D` (`:449`) | **keep** | unused by 3 of 7 area kinds but is one shared line; sinking it into branches adds lines — net negative |
| `_mk_static`'s `nm`/`b.name` | **keep** | unused by output but retagging 5 call sites for −1 line is churn; names aid failure diagnosis |
| `_in_cb["monitor"]/["max"]` for rb kinds | **keep** | dead *for rb arms only* but the store is shared with cm arms which read both — conditionalising adds a branch to save nothing |
| `_floor_a.position = (10000,10000)` for off/max0 | **keep** | the bounded wait window IS the absence measurement (scout: `cm_off` burns both waits deliberately, 2.18 s pinned) |
| `cm_max0` vs `cm_off` identical signature | **keep both** | same observed output, different mutation (second key vs first key) — distinct cell, scout directive 7 |
| `rb_free_rid`/`area_free_rid`, `*_dss_in_cb`, `*_node_position` pairs | **keep both** | paired controls across the two interior windows — the pairing IS the evidence (scout §1.2) |

**Out of scope, recorded not touched:** `run_battery.py` carries pre-existing
`expected_errors` entries mapping names to `()` (`:479,481,485` — e.g.
`slider_adjust_repeat_right_focus_restore: ()`); these are semantically inert
versus the `.get(name, ())` default, but they pre-date the r79 landing and sit
outside this seat's hunt scope.

## 5. Result

- **Deletions made:** 3 (header arm census, dead `cls` store, redundant
  `monitoring=true`), all in `phys2d_events.gd`: 526 → **503 lines**.
- **Battery:** folded tree **111/111 PASS**, tuple sets **byte-identical** to
  same-session control; folded vs both author runs: 0 tuple mismatches,
  104/104 normalized outputs identical.
- **Preserved contract:** every `CASES` row, all 4 `expected_errors` gates, the
  ordering razor, the fail-closed `unknown_arm` path, RID hygiene, all pinned
  PASS lines byte-exact.
- **Tradeoff:** the header census's per-arm one-liners are gone; recovered
  authority is `match arm:` (sole index) + section banners + scout §1.1. The
  alternative (completing the stale list to 23 lines) was rejected — it keeps a
  duplicate index already shown to drift.
- **Stop line:** the next deletion candidates (header print, `.duplicate()`,
  per-kind `monitor`/`max` stores, `nm` param) would either remove diagnostics
  other seats cite, cost more lines than they save, or mutate live call sites
  for zero semantic gain — each would harm an axis. Stopped here.

Seat output complete.
