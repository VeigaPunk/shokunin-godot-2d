# r97 critic — adversarial review of committed `f67094bb` (12 `stree_lattice_*` rows, SceneTree groups / signal flags / `call_deferred`)

Seat `CRITIC` (g2d lane r97) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps),
Python 3.14. Reviewed commit **`f67094bb`** (`r97 author: SceneTree
groups/signal-flags/call_deferred lattice`, parent `d5c05ff8`). HEAD at session
start and report time **`2dcbb6f6`** (r100) — the reviewed bytes are *not* HEAD,
so every check below ran on `git archive f67094bb` extracted to
`corpus/live/r97-critic/frozen/` (seat receipt dir; the archive's own
`corpus/live` payload was pruned after extraction). The r97 fixture bytes are
unchanged from `f67094bb` to HEAD (sha256 equality re-verified for
`stree_lattice.gd` + the 3 scene fixtures; the 12 CASES tuples are
AST-byte-identical at HEAD), so the frozen tree is the landed artifact.

**Zero tracked writes, no commit.** `git status --porcelain
--untracked-files=no` is empty at report time; the tracked
`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` was not regenerated
(no harness import; all runs used `git archive` copies or AST parses). All seat
receipts are untracked files under `corpus/live/r97-critic/` — `corpus/live`
carries a nested `.gitignore` covering only `runs*/`, `**/__pycache__/` and
`**/.godot/`, so the seat dir is *visible as untracked*, exactly like every
prior `corpus/live/rNN-<seat>/`.

**`lsp` disclosure.** No `lsp` device / GDScript server on this host (same class
as r89–r96). Evidence is fresh-process execution + textual/AST diff.

---

## 0. What I ran

| # | batch | scope | result |
|---|---|---|---|
| 1 | **re-derivation** — 12 landed rows × 3 reps, fresh scratch staged from the frozen fixtures (`scripts/attack.py --mode baseline`) | 36 receipts | **12/12 PASS ×3**, PASS line **byte-equal** to the shipped signature, `out_uniq=1` per row, max wall **0.78 s** vs the 8 s harness bound (**10.2×**) |
| 2 | **fixture mutants** (`scripts/attack.py --mode all`, receipts `runs/mut-*`) | 9 mutant shapes | see §1 — `value-count-plus1`/`uniq-direct-reverse`/`no-arm-flag`/`arm-swap` **rejected**; `comment-only`/`forge-stub`/`phys-late-1..3`/`sample-next-sig` **accepted**; `phys-late-4` rejected |
| 3 | **floor-gate mutants** — frozen harness with CASES trimmed to the 12 r97 rows + the 3 hard-required `save_process_*` rows (`scripts/build_harness_mutants.py`, `harness-runs/`) | 3 runs | base: gate `True`, `dead_entry_count=0`; dead-on-`stree_lattice_census`: gate **False** (liveness ✓); dead-on-`r97b_gate_probe`: gate **True** while `dead_entry_count=1` (**silent**, §1 F2) |
| 4 | **provenance / static** (`scripts/provenance.py`, `weaken.py`) | fold diff, sha256s, receipt equality, signature-form sensitivity | §2 |
| 5 | **scratch-contamination probe** (`/tmp/uid-*`) | does any arm install `.godot/uid_cache.bin`? | **no** for `census`/`scene_probe`/`group_order` — refuted, §2.4 |

---

## 1. Findings (ranked)

### F1 — DEFECT (row semantics) · `phys_defer_same_frame=true` is a ≤4-signal **window** pin, not a same-frame pin

`stree_lattice_defer_ladder` emits `phys_defer_same_frame=true`, and the author
table + header L10 read it as *"a deferred call queued from its continuation
lands in that continuation's frame"*. The landed measurement cannot discriminate
that: `_phys_probe()` (fixture L780–801) samples `PHYSL`/`DFNODE.log` from a
`process_frame` listener inside `for i in 4: await process_frame`, never clears
either buffer inside the loop, and sets the flag on the first signal where
**both** markers are visible.

Counterexample (executable, landed bytes untouched): mutant `phys-late-N`
inserts N × `await process_frame` between the physics continuation's
`PHYSL.push_back("co_phys")` and its `DFNODE.call_deferred("cb", "after_phys")`
— i.e. the deferred call is queued **N frames after** the continuation:

| mutant | emitted | landed row verdict |
|---|---|---|
| `phys-late-1` | `phys_defer_same_frame=true phys_co_in_log=true` | **PASS** (byte-identical line) |
| `phys-late-2` | same | **PASS** |
| `phys-late-3` | same | **PASS** |
| `phys-late-4` | `phys_defer_same_frame=false phys_co_in_log=true` | FAIL |

⇒ the pin's real content is *"lands within the 4-signal sampling window that
opens at the physics continuation"*; a 1–3-frame-late queue is
indistinguishable from the same-frame law. Corroborating shape from the other
direction: `sample-next-sig` (observation shifted one signal later) also PASSes.

Consequence for the L10 correction: because the only sampling of a deferred
landing relative to a signal happens ≥1 signal later (this arm's 4-frame window;
`_arm_defer_order`'s `df`/`DLOG` are read at the *next* resume, after that
frame's `pf_sig`), the **refuted** ordering (*flush after `process_frame`*) and
the **corrected** one (*flush before it*) emit byte-identical output on all 12
rows. The boundary's headline correction is carried in comments only and is not
falsifiable by the landed block — the header's *"Measured laws this probe
encodes (all [M])"* list should not imply otherwise.

Smallest safe correction (additive, next insertion round): have `_phys_co`
capture `Engine.get_process_frames()` at queue time and at landing and emit
`phys_defer_frame_delta=<int>` (0 = same frame), keeping the existing key as the
window witness. Do **not** relax any signature to a prefix (see F5). No row
rewrite is needed to admit the counterexample as a *recorded reservation* — the
pinned value is true for the real engine; what is unproven is its discrimination.

### F2 — DEFECT (gate coverage) · the r97 floor gate filters on the *fixture* prefix, not the round prefix

`run_battery.py:3580–3584` (landed bytes) filters
`r["case"].startswith("stree_lattice_")` and its comment claims *"same
named-by-round / covers-round-prefixes shape as r87–r96"*. Measured with two
trimmed-harness mutants (identical synthetic dead entry
`ERROR: r97 critic synthetic dead entry never emitted by this probe`):

| mutant | dead entry on | `r97_expected_errors_all_matched` | `dead_entry_count` |
|---|---|---|---|
| `harness-base` | — | `True` | 0 |
| `harness-dead97` | `stree_lattice_census` | **`False`** | 1 |
| `harness-deadr97name` | **`r97b_gate_probe`** (renamed copy of the census row — the convention every other round uses: `r96_scene_io_`, `r96b_`, `r98_canvas_`, `r100_gui_`) | **`True`** | **1** |

⇒ the gate is load-bearing for `stree_lattice_*` rows (liveness proven) but
**silent** for any r97-era row named with the round convention. No global gate
exists — `dead_entry_count` is recorded as data, never asserted (only the
per-round prefix gates read `dead_in_run`).

Smallest safe correction: widen the filter to
`("stree_lattice_", "r97_", "r97b_", "r97c_")` (one line, insertion-only) and
state the naming convention in the r97 block comment. Today the gate is
vacuously `True` (the block carries zero `expected_errors` entries — re-verified
by AST: the landed dict at lines 1610–1830 holds **70** entries, none whose key
contains `stree` or `r97`).

### F3 — INFO (doc) · the landed row-count arithmetic is off by one

Commit message and `r97-author.md:80` state *"CASES 420 → 432 tuples (results
rows 426 → 438 incl. meta)"*. Measured on the committed bytes (AST literal
count): `89f85ed8` = **419**, `f67094bb` = **431**; the author's own
`runs/20261016T091032696916Z/verdicts.json` has **438** results = 431 + the 7
appended meta rows. The delta (+12) and the results-row count are right; the two
CASES absolutes are each 1 too high. Smallest safe correction: fix the two
numbers in the report (the commit message is immutable). No row impact.

### F4 — BOUND (recorded, not a defect) · the 12 rows admit a total forgery; the probe contains no internal assertion

A 25-line stub (`sha256 59ad78ac…`) that never creates a node and never touches
the group/signal API, printing the 12 shipped PASS lines verbatim
(`mutants/forge-stub/`), passes **12/12** rows (exit 0, no `ERROR:`). Same class
measured: `comment-only` mutant
passes 12/12 (no fixture-hash witness anywhere in the row). The landed probe
corroborates why nothing can catch it: `_fail` is reachable **only** from
`_: _fail("unknown_arm")`, `it_valid`/`it_connected` are pure `_it` aliases
(`func it_valid(key, value) -> void: _it(key, value)`), and there are **0**
`assert(` sites — no arm asserts anything about its own measurements. This bound
is documented by the harness itself (`probe_error_clause_surface` bounded claim:
the verdict is a pure function of merged-line presence), so it is a **bound to
state**, not a blocker. The one fixable half: the helper names `it_valid` /
`it_connected` claim a validation that does not exist in code — a reader can
mistake `it_valid("phys_defer_same_frame", …)` for a checked invariant. Smallest
safe correction: rename to `_it`/`_emit`, or make `it_valid(key, expected)`
compare and `_fail` on mismatch.

### F5 — RISK (evidence-backed) · nothing gates the signature *form* that bounds F1's slack

The author deliberately shipped full-line signatures and warned "never weaken to
`ROWS_PREFIX` silently". Measured sensitivity (`scripts/weaken.py`): with the
`defer_ladder` signature truncated at `phys_defer_same_frame=`, the `phys-late-4`
receipt is **accepted** (`full_line=False`, `prefix=True`) — a silent relaxation
of the shipped form would re-admit the F1 counterexample, and no gate in the
battery covers signature strictness (the r97 floor gate covers allowlist entries
only). Smallest safe correction: one gate asserting each `stree_lattice_*`
signature is a full `PASS stree_lattice <arm> … rev=<bool>` line (end-anchored),
or an explicit note in the block comment that strictness is intentional and
ungated.

---

## 2. Claims verified (no finding)

1. **Landing shape.** `git show --numstat f67094bb -- corpus/fixtures/run_battery.py`
   = **+65 / −0** insertion-only; the 6 touched files are the 4 fixtures + the
   harness block + the report; `project.godot` untouched; the 12 rows sit at
   lines 1258–1281, immediately ahead of the `crash_*`/`descendant_pipe_*` tail
   (rows 1282–1291) as claimed.
2. **Fixture provenance.** `stree_lattice.gd` `61954f87…` (937 L), `r97_scene_a.tscn`
   `c86d5674…`, `r97_scene_b.tscn` `7c153f7f…`, `r97_scene_marker.gd` `39763310…`
   — all four byte-equal to the author's table and to `f67094bb:corpus/fixtures/*`.
3. **"Zero emitted-byte change" fold.** Non-comment code diff vs the frozen scout
   probe (`corpus/live/r97-scout/probes/stree_lattice.gd`, `4dd18e10…`, 896 L) is
   **exactly two lines**: the `res://scene_a.tscn` → `res://r97_scene_a.tscn` and
   `res://scene_b.tscn` → `res://r97_scene_b.tscn` renames in `_arm_scene_probe`.
   Everything else is comment/header. All **12** shipped signatures are
   **byte-equal** to the scout's canonical `runs/r97_<cell>.rep1.out` PASS lines
   (12/12, including the `--rev` cell, whose receipt is
   `r97_group_order_rev.rep1.out`).
4. **The rename was necessary.** Mint-era `scene_marker.gd` is `extends Node` +
   `@export var marker := ""` (and its `.tscn`s are `Node` roots), while the r97
   marker is `Node2D` + `@export var tag` — sharing the flat scratch names would
   have collided with `controls/scene_transition_probe.gd`. The landed
   `r97_scene_marker.gd` is byte-identical to the scout's `proj/scene_marker.gd`.
5. **`--arm=` tokens are load-bearing.** Running a landed row with `[]` or with a
   swapped `--arm=` both FAIL (`_fail("unknown_arm")`, exit 1) — the scout's
   `author-rows.py.txt` really did drop the arm column (its `flags` are `[]` for
   all 12), so the landed fix is a genuine correction, not cosmetics.
6. **Row discrimination.** `value-count-plus1` (`get_node_count_in_group + 1`) and
   `uniq-direct-reverse` (an extra emitted key) both FAIL ⇒ the rows are not
   echo pins and the shipped form is byte-exact on the whole line.
7. **Byte-stability / hygiene.** 12 rows × 3 fresh-scratch reps: `out_uniq=1` per
   row; all 12 scout canonical `.rep1.err` receipts are **0 B**; no
   unallowlisted `ERROR:` in any receipt.
8. **No scratch contamination.** No arm creates `.godot/` or `uid_cache.bin` in a
   fresh project (tested `census`, `scene_probe`, `group_order`) ⇒ the r97 block
   cannot perturb the r96 `uid`-cache-dependent family, and the 12 rows are
   order-independent (they pass in a scratch the battery never touched).

---

## 3. Verdict

**PASS-WR (with reservations)** — the landed bytes re-derive green and nothing
they *emit* is false: 12/12 rows reproduce their shipped signatures byte-exactly
on the committed fixture in a fresh scratch, the fold is provably
comment-only-plus-two-path-renames, provenance is byte-exact against the scout
receipts, and the one gate the block carries is live (dead entry → `False`).
Two claims in the surrounding report are **not** supported by the landed bytes
and should be narrowed next round:

- **F1**: `phys_defer_same_frame=true` discriminates a ≤4-signal window, not the
  same frame (3-frame-late queue still reads `true`), and consequently the
  corrected L10 ordering is not falsifiable by the block.
- **F2**: the r97 floor gate covers the fixture prefix only — a dead entry on a
  round-convention-named row is silent (measured), so the "covers-round-prefixes
  shape as r87–r96" claim is inaccurate.

F3 is documentation arithmetic; F4 is the (documented) forgery bound plus two
misleading helper names; F5 is the ungated signature strictness that currently
bounds F1's slack.

Blockers: **none**. No row, signature, or gate needs to be withdrawn; the
corrections above are additive and insertion-only.
