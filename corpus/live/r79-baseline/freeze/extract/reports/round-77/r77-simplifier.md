# game-dev-2d round 77 — simplifier (seat: simplifier; host: devin)

Lane `g2d`, round 77. Repo `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
HEAD `62201e5` (r77 work). Runtime LOVE 11.5 (Mysterious Mysteries,
`/usr/bin/love`), LuaJIT 2.1.1788460057, Python 3.14.7.

Audited revision = the committed r77 delta only (`git show 62201e5`):
`corpus/fixtures/love_battery.py` +631/−0, `corpus/fixtures/love_phys_probe/
main.lua` +422/−0. Fixture hashes at audit: battery
`1e3e9f46e16ae9f1b3dc26734ac62f27d42113f4c41b5ff61041b9aa0fcafeb3`, probe
`3f130f418ff600c593181027cdda59f5931bbf0137d784700e1126f88f753d01`
(= the r77-author's declared post-change hashes).

**Leaf discipline.** No subagent, no git mutation, **no tracked-file edit**.
Writes = this report + `corpus/live/r77-simplifier/**`. The shared tree was
verified byte-identical before reporting: `sha256sum` of both fixtures equals
the hashes above, and `git status` shows only the two pre-existing dirty
`corpus/live/r72-simplifier/*.log` files (mtimes 11:57/12:35, predating this
seat) — untouched by this seat.

**`lsp` disclosure (host state, re-verified at seat start).** No `lsp` device
is exposed in this session: `lua-language-server`, `lua-lsp`, `sumneko*`,
`pylsp`, `pyright`, `jedi-language-server`, `luacheck` are all ABSENT (only
`clangd` is installed, and the LOVE C++ tree is not in this repo). The only
MCP server (`rea`) is a Ghidra binary-analysis server whose tools are
native-function annotation — **no source-level `references` tool**. Every
call-graph / dead-code claim below is therefore an **AST + textual census with
runtime replay**, never presented as `references` proof; no cold-start empty
result is recorded as absence (no `lsp` call was made at all).

---

## Axes (this seat, this round)

- **A1 weight** — duplicated predicates / emit blocks / dead state in the r77
  delta.
- **A2 falsifiability** — every armed witness, pin, and gate conjunct that
  carries a catch.
- **A3 contract** — receipt bytes, pinned keys, classifications, battery
  verdict, prior-row bytes.
- **A4 replay reproducibility** — third party can re-derive every claim from
  the artifacts alone.

Admission rule applied: a deletion is *proposed* only when A3 and A4 are
byte-for-byte unmoved and A1 improves. A2 is never traded for A1: a deletion
whose witness cannot be re-caught by any retained layer is **withheld and
reported as rejected with the measurement**.

**Harness validation.** A scratch copy of the unmodified fixtures replays the
full battery **75/75** and reproduces the r77-author's reference run
(`corpus/live/runs/love-20261014T194754676712Z`) **112/112 IW receipt files
byte-identical** (only the 7 declared timing-jitter verdict rows differ:
`dtcadence_*`, `popen_*`). Concatenated `iw-*.stdout.txt` sha256 =
`bebcdf6b70826ee76090b93006001cc6aa1a2bd80dad6e418d0c2ae8675f0168`.

## Result

| variant | files | change | Δ weight | iw strict | token-only | other | battery |
|---|---|---|---|---|---|---|---|
| `v0` baseline | — | none | 0 | 112/112 | 0 | 0 | 75/75 |
| **`vpins`** | battery | **P3** 67 redundant pins | −34 lines / −2164 B (1502→1468) | **112/112** | 0 | 0 | **75/75** |
| **`vprobe`** | probe | **P1+P2+P4** dead `ext` fields, dead disjunct, dead params | 0 lines / −130 B | **112/112** | 0 | 0 | **75/75** |
| **`vfold`** | both | **P1+P2+P3+P4** (fold target) | −34 lines / −2294 B | **112/112** | 0 | 0 | **75/75 ×2** |
| `vobs` | probe | **P6** dead observer fields | 0 lines / −155 B | 95/112 | 0 | 17 | **75/75** |
| `vdedup` | probe | **W1** merge duplicated fire/postfire blocks | −2 lines / −229 B | 104/112 | 4 | 4 | 75/75 |

`iw strict` = the 112 deterministic IW receipt files (`iw-*.stdout.txt` +
`iw-*.stderr.txt`, 56 cells) byte-identical to the r77-author reference run.
`token-only` = identical after normalizing only the unpinned `main.lua:<N>` /
`srcline=<N>` digits. `other` = anything else moved. `vfold` ran twice
(`runs-fold`, `runs-fold2`) and the two runs' receipts are identical to each
other and to the reference.

**Falsifiability evidence (A2), three independent layers.**
1. **Differential equivalence fuzz** (`corpus/live/r77-simplifier/
   equiv_fuzz.py`, `fuzz_summary.json`): the baseline and the folded battery
   are loaded side by side and every affected row is evaluated against the
   real receipt plus a mutation sweep over every flat key (systematic
   single-key values + 2 000 random multi-key mutants per row).
   **47 347 evaluations, 0 verdict divergences.**
2. **The r77-author's own 43-ablation matrix re-run against the folded
   classifier** (`ablate_variant.py`, their script pointed at `vfold`):
   **43/43 row-fails, 0 leaks** — every decisive line whose deletion used to
   fail the row still fails it.
3. **Per-pin ablation** (`pins_ablation.tsv`): for each of the 67 deleted
   pins, mutating that key in the real receipt still **FAILs** the row —
   **67/67 caught by the class gate**, 0 leaks.

---

## P1 — dead `ext` field in the R77 spec table (PROPOSE, byte-identical)

`main.lua:116,131`: `ext_fixture_destroy = { ext = "fixture_destroy" }` and
`ext_worldrelease = { ext = "worldrelease" }`. The `ext` field is **never
read**: the exhaustive `RS.<field>` census over the whole probe is
`act, cb, co, cowrap, drain, extra_fx, joint, scene, target, wp` — no `ext`
(`evidence/census.txt`). The exterior controls are dispatched by `run_ext()`
on the parsed cell `kind`, not on the table field; the entries' only live
role is making `RS ~= nil` (which the empty table preserves).

Fold shape: `ext_fixture_destroy = {},` / `ext_worldrelease = {},` — a
same-line-count edit (888 lines stay 888), so no traceback line token can
move. Measured: `vprobe` 75/75, **112/112 receipts byte-identical**.

Tradeoff: the field duplicated the cell name; deleting it removes a
cross-check that could catch a future mismatch between the table entry and
the cell name — but nothing consumed it, so no check existed.

## P2 — dead disjunct `or mkind == "update_yield"` (PROPOSE, byte-identical)

`main.lua:397`. `do_mutation` has exactly two call sites
(`main.lua:497` passes the cell-name `kind`; `main.lua:514` passes `RS.act`).
The only cells whose name parses to `kind == "update_yield"` are
`co_update_yield` and `cowrap_update_yield`, and for both `target_cb == nil`,
so the pre-r77 arming path (the only caller that passes the parsed `kind`) is
never entered for them; the r77 path passes `RS.act == "coyield"`. The
disjunct is unreachable, and even if reached it selects the identical body
(`"coyield"`). Census: `evidence/census.txt`.

Fold shape: `elseif mkind == "coyield" then` — same line count. Measured:
`vprobe` 75/75, 112/112 receipts byte-identical.

## P3 — 67 redundant pins whose predicate the class gate already owns (PROPOSE, byte-identical)

**Finding.** The r77 rows carry 461 pins across 26 rows. **67 of them (in 17
rows) restate a decisive conjunct of the very class gate that yields the
row's expected class** — the same predicate authored twice, on the same flat
key. Two tiers:

- **60 literal restatements** — the gate contains `flat.get(k) == "v"` with
  exactly the pinned value (e.g. `cb_meter.ok == "true"`,
  `drainact.fx_dead == "false"`, `wpext.ok == "true"`,
  `r77recover.b1dead == "true"`, `drainec.n == "1"`).
- **7 derived restatements** — the gate enforces a *relation* whose other
  operand is a retained pin: `drainact.count_after == drainec.count − 1`
  (with `drainec.count: "4"` retained), `r77obs.bc == cb_setcallbacks.
  swapped_n` (×3 rows, with `swapped_n` retained), `r77obs.pre` likewise, and
  `cb_fxdestroy.fcount_after == cb_fxdestroy.fcount_before` (×2, with
  `fcount_before` retained).

Per row (deleted pins): `iw_bc_setcallbacks` 2, `iw_pre_setcallbacks` 2,
`iw_multi_setcallbacks` 2, `iw_bc_setcallbacks_nil` 3, `iw_bc_setcallbacks_back`
3, `iw_bc_fixture_destroy` 7, `iw_bc_fixture_destroy2` 7,
`iw_ext_fixture_destroy` 3, `iw_drain_setpos_b2` 2, `iw_drain_queue_b2` 4,
`iw_wp_drain_throw` 11, `iw_drain_order_joint` 5, `iw_bc_cowrap_setpos` 1,
`iw_co_update_yield` 4, `iw_wp_coyield` 3, `iw_bc_meter` 4, `iw_pre_meter` 4.

**Why deletion cannot flip a verdict.** The row fails if *either* the class
mismatches *or* a pin fails. For every deleted pin, class-match implies the
gate conjunct, which is at least as strong as the pin — so any receipt that
would have failed the pin still fails the row (via `class → anomaly`). This
is not hand-waving: the fuzz evaluated 47 347 mutated receipts per-side and
found **0 verdict divergences**, and the author's 43-ablation matrix still
shows 43/43 row-fails.

**Preserved contract.** `vpins`/`vfold`: battery 75/75; 112/112 receipts
byte-identical; concat sha `bebcdf6b…`; `verdicts.json` identical modulo the
7 declared jitter rows.

**Fold shape and rule.** `fold.diff` (65 removed content lines, 31 added;
net −34 battery lines). After the fold the row-pin layer has a clean rule —
*pins carry exactly the values the gate does not decide* — which is the
r76-P1 precedent applied to r77 (one authority per predicate), not a second
convention.

**Tradeoff, named.** Failure *attribution* changes for those 67 witnesses:
a mutated witness now reports `class anomaly` instead of `pin:<key>`, and the
inline witness list the reader sees shrinks. The verdict, the class, the rc
and every retained pin are unmoved. Rows whose gate does **not** cover a key
keep their pins (see R2/R3), which is what makes the rule uniform.

## P4 — dead parameters in the r77 helpers (PROPOSE, byte-identical)

- `r77_drain_hook = function(contact, fa, fb, dyn)` → `function(fa, dyn)`:
  `contact` and `fb` are never referenced in the hook body (census:
  `evidence/census.txt`; `fa` is used only by the `order` branch, `dyn`
  everywhere); call site `main.lua:542` updated on the same line.
- `r77_cb2_bc(fa, fb, c)` → `(fa, fb)` (`c` unused);
  `r77_cb2_ec/pre/post(fa, fb, c)` → `()` (all three parameters unused).
  LOVE dispatches callbacks with positional extras that Lua ignores; the
  callback identity (and the label map that reads it) is unchanged.

Same line count, 112/112 receipts byte-identical, 75/75. In-pattern with the
r74 fold of the dead `evpins` parameter.

---

## P6 — dead observers: 6 `r77obs` fields never read by any cell (CANDIDATE, r77-row bytes move)

**Finding.** `r77_obs` emits 20 fields. A mechanical census of every
`r77obs.*` reader in the battery (pins + classifier) and of the whole repo
(`corpus/live/r77-author/**` tools, `reports/round-77/**`; the only other hit
is the author's scratch `cells/*.summary.json`, which is a mechanical dump of
the parsed flat map, not a reader) leaves **6 fields with no reader at all**:

`step`, `locked`, `b1pos`, `jcount`, `swap_step`, `drain_n`.

The other 14 (`count`, `b1pos`-siblings `b2pos`, `b1dead`, `b2dead`,
`fx_a_dead`, `fx_b_dead`, `bc/ec/pre/post`, `bc2/ec2/pre2/post2`) are live in
1–5 rows each.

**Falsification proof** (`deadfield_probe.py`): for each of the 6 fields, in
each of the 17 rows that emit `r77obs`, setting the field to `MUT` **never
fails the row** (17 rows × 6 fields, 0 catches) — they carry no catch at all,
so removing them cannot reduce falsifiability. The same probe shows the 14
retained fields do carry catches (mutation fails the row).

**Measured cost (why this is a candidate, not a fold).** Dropping the 6
fields is a same-line-count edit (888 lines stay 888, −155 B) and the battery
replays **75/75**, but 17 r77 receipts change by exactly their two `r77obs`
lines (95 strict / 17 other; concat sha `7d8eb496…`). No prior-row byte
moves and no pinned key is lost — but the strict bar this seat applied to
P1–P4 ("112/112 strict") is not met, so under that bar it is **withheld**;
it is fold-ready only if the L1 accepts a declared r77-only receipt delta.
The author's existing r77 run dirs remain on disk as provenance either way.

---

## W1 — duplicated fire/postfire emit blocks (WITHHELD, measured prior-row perturbation)

The r77 arming path (`main.lua:506–516`) duplicates the pre-r77
fire/postfire emission block (`main.lua:492–499`) verbatim except for the
`kind` string. Merging both into one `r77_fire(...)` helper is the obvious
dedup (−2 lines), and the battery still passes 75/75 — but the measured
receipt drift is a **prior-row perturbation**, which the tasking forbids:

- `iw-bc_setpos_unp` and `iw-bc_newbody_unp` (prior rows) change
  **structurally**: the traceback gains a `main.lua:460: in function
  'r77_fire'` frame and every subsequent frame line moves
  (`497→502`, `546→544`, `810→808`);
- `iw-bc_worlddestroy` (prior row) moves its error token `861→859`;
- 3 r77 rows move token-only; 4 r77 rows move structurally.

Root cause is arithmetic and general: the reference run's prior-row receipts
contain line tokens at `194, 198, 250, 299, 497, 546, 810, 861`
(`evidence/token_sites.txt`), so **any line-count-changing probe edit above
line 862 perturbs prior-row bytes**. W1 is kept as the measured
representative (`vdedup`, concat sha `fdf40de5…`) and is not proposed.

## W2 — other duplicated emit blocks (WITHHELD, same class)

Same arithmetic, no separate run needed: the `cb_destroy` pcall+EM pair is
authored 4× (`destroy`, `draindefer`, `destroy2`, and the r77 `queue_target`
branch), `r77abortq` 2× (resume container + update path), `r77recover` 2×
(different formats), and the `cb2bc/pre/post` traces share a shape. Every
merge changes the line count above 862 and therefore moves prior-row tokens
and/or traceback frames exactly as W1 measured. **Stop rule:** no probe-side
line deletion above line 862 is admissible while the prior-row token sites
are live.

## R1 — r77 gate conjunct `wp_setpos.ok == "false"` (REJECTED by ablation)

`love_battery.py:1140` (the `drain_abort` branch) checks
`flat.get("wp_setpos.ok") == "false"`, but the probe emits that line as a
**hardcoded echo** of the abort (`main.lua:821`: `EM("wp_setpos ok=false
err=%s …", stripped, …)` — there is no call, unlike `wpext`), so the conjunct
is structurally constant whenever the branch is reached. Deleting it looks
free — until the ablation probe: with the `wp_setpos …` witness line deleted
from the receipt, the baseline gate drops the row to `anomaly` (FAIL) while
the variant without the conjunct stays `drain_abort` (PASS)
(`evidence/p5_leak.txt`). **A catch is lost → rejected.** (The misleading
`wp_setpos` echo itself is pre-r77 code and out of this seat's remit.)

## R2 — `drainec.locked` pins outside gate coverage (WITHHELD)

`drainec.locked` is emitted only under the `not world:isLocked()` guard and
prints the same value (`main.lua:541–542,639`), so it is constant on every
reachable receipt. But in `drain_setpos_b2`, `drain_queue_b2`,
`drain_order_joint`, `drain_worldrelease` the class gate does **not** read
it, so the pin is the only catcher of a locked-drain receipt; deleting it
would leak exactly the mutation the pin exists for. Only the rows whose gate
already reads `drainec.locked` (`fixture_destroy`, `fixture_destroy2`,
`wp_drain_throw`) lose the pin in P3 — and there the 67/67 ablation sweep
proves the gate still catches the mutation.

## R3 — `rc` / `done` pins (WITHHELD for convention)

`rc`/`done` duplicate the classifier's branch-entry condition on every row
(`done and rc == 0`, `rc == -11`, …), but they are present on **all 56 rows**
including the 30 pre-r77 rows, are the row's launch contract, and the
precedent rounds never touched them. Deleting them only on r77 rows would
create an inconsistent row convention — withheld by the "no second
convention" rule.

## R4 — armed-but-unread "unreached" markers (RETAINED, axis-bound)

`cb_coyield after_unreached` (`:404`), `cb_cowrap_unp
inner/outer_after_unreached` (`:410,414`), `r77cowrap_after_unreached`
(`:715`) are never emitted and never read by any pin. They are the probe's
honesty markers ("if this line appears, the invariant broke") and no verdict
depends on them; the r74 seat retained exactly this class as axis-bound.
Deleting them is byte-identical but removes the absence witnesses — not
proposed.

## R5 — `pre_meter` as a channel twin (RETAINED, axis-bound)

`bc_meter` and `pre_meter` are byte-identical in shape by design (the
author's own "the channel is irrelevant" claim). Deleting one would remove a
measured channel-invariance row — a falsifiability reduction, not weight.
Retained.

---

## Preserved contract

- **Battery:** 75/75 in every accepted variant (`baseline`, `pins`, `probe`,
  `fold`, `fold2`), `launch_ok=True`, `done_marker=True`, exit 0. Run dirs:
  `corpus/live/r77-simplifier/runs-{baseline,pins,probe,fold,fold2}/`.
- **Receipts:** 112/112 IW files byte-identical to the author's reference run
  for the fold; concat sha256 `bebcdf6b70826ee76090b93006001cc6aa1a2bd80dad6e418d0c2ae8675f0168`
  (same number as the reference and the baseline). `vfold` ×2 reproduces it.
- **Prior rows:** untouched (P1–P4 are same-line-count edits; the fold's only
  line-count change is inside the battery, which cannot affect probe bytes).
- **Pins/classes:** every retained pin keeps its exact value (`verify()`
  asserts the pin-key diff equals the intended delete list and all retained
  values are unchanged, for all 56 rows).
- **Fold target for the integrator:** `corpus/live/r77-simplifier/vfold/`
  (`love_battery.py`, `love_phys_probe/main.lua`), reviewable as
  `corpus/live/r77-simplifier/fold.diff`. `vpins`/`vprobe` are the
  conservative subsets. No tracked file was edited by this seat.

## Evidence index

| artefact | content |
|---|---|
| `corpus/live/r77-simplifier/scratch/` | verified copy of the audited fixtures (hashes above) |
| `vfold/`, `vpins/`, `vprobe/`, `vobs/`, `vdedup/`, `vconj/` | built variants (fold target + measured withheld probes) |
| `mkvariants.py` | variant generator; `verify()` asserts pin diff == intended list for all 56 rows |
| `equiv_fuzz.py`, `fuzz_summary.json`, `pins_ablation.tsv` | 47 347-evaluation differential equivalence + 67/67 per-pin ablation |
| `ablate_variant.py` | the r77-author's 43-ablation matrix, re-run against `vfold` (43/43 fail, 0 leaks) |
| `deadfield_probe.py` | 6 dead `r77obs` fields × 17 rows, 0 catches; 14 retained fields carry catches |
| `evidence/census.txt` | `RS.*` census (no `ext`), `update_yield` tokens, `do_mutation` call sites, drain-hook params |
| `evidence/token_sites.txt` | every `main.lua:<N>`/`srcline` site in the reference run, prior vs r77 |
| `evidence/receipts_summary.txt` | strict/token-only/other + concat sha per variant |
| `evidence/p5_leak.txt` | the R1 leak measurement |
| `fold.diff` | the proposed fold as a reviewable patch |
| `runs-{baseline,pins,probe,fold,fold2,obs3,dedup}/` | replay runs (receipts + verdicts.json) |
| `runs-obs/`, `runs-obs2/` | **incidents, not measurements**: the first two P6 builds were invalid (an implicit-concatenation Lua syntax error; then a value-swallowing `%s` gap that ate the counter keys — the author's own key-name trap class). Kept as provenance; superseded by `runs-obs3` |

## Tradeoffs, limits, blockers

- **P3 changes failure attribution, not verdicts.** 67 witnesses now fail as
  `class anomaly` instead of `pin:<key>`; a future seat debugging a row will
  read the gate instead of the pin list for those keys. All measured.
- **P6 moves r77-row bytes.** It is the only candidate that touches emitted
  bytes; its proof is falsification-neutrality (no reader, no catch) plus
  prior-row and pin invariance. Withheld under the strict bar; fold-ready if
  the L1 accepts the declared 17-file delta.
- **W1/W2 are withheld by arithmetic, not by taste:** the reference prior-row
  receipts carry line tokens up to `861`, so any probe line deletion above
  that perturbs prior rows (W1 measured: 2 prior rows structurally changed).
- **Not measured / residual risk:** the fuzz's mutation pool is finite
  (~47 k receipts over 17 rows); the class gates were treated as the
  authority by syntactic inspection, not by a full symbolic equivalence
  proof. `rc`/`done` and the pre-r77 `abort_w` hoist were deliberately left
  untouched (pre-r77 lines / row convention). No `lsp`/`references` device
  exists on this host — census + replay is the strongest available carrier,
  and it is labelled as such.
- **Blockers:** none.
