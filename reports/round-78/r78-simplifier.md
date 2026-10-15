# game-dev-2d round 78 — simplifier (seat: simplifier; host: devin)

Lane `g2d`, round 78, wave `shokunin-train-20261101-w18`. Repo
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`, HEAD `1a03b7a` (*r78 work:
nested-update damage surface — 17 cells*) at seat start and at seat end.
Runtime **LOVE 11.5** (Mysterious Mysteries, `/usr/bin/love`), LuaJIT
2.1.1788460057, Python 3.14.7.

Audited revision = the committed r78 delta only (`git show 1a03b7a`):
`corpus/fixtures/love_battery.py` **+565/−5**, `corpus/fixtures/love_phys_probe/
main.lua` **+479/−0** (plus the author report). Fixture hashes at audit:

```
battery ea70c42c5e1c54444de56a10c680c547c9044dbb590dc2d17c700d0ce4573458
probe   75eb18d2ffce0ef39b8a52cfe365de6de3898d9a60c20ca88765c94ec03f9d96
```

**Leaf discipline.** No subagent, no git mutation, **no tracked-file edit**.
Writes = this report + `corpus/live/r78-simplifier/**`. The shared tree was
verified byte-identical before reporting: both fixture hashes above are
unchanged (`sha256sum`), and `git status` shows only the pre-existing dirty
`corpus/live/r72-simplifier/*.log` files plus untracked directories (predating
this seat). The fold is delivered as a **reviewable diff**, not applied.

**`lsp` disclosure (host state, re-verified at seat start).** No `lsp` device
is exposed in this session: `lua-language-server`, `lua-lsp`, `sumneko*`,
`pylsp`, `pyright`, `jedi-language-server`, `luacheck` are all ABSENT (only
`clangd` is installed, and the LOVE C++ tree is not in this repo). The only
MCP server (`rea`) is a Ghidra binary-analysis server — **no source-level
`references` tool**. Every dead-code / unreachable-arm claim below is therefore
an **AST + textual census with runtime replay and a differential harness**,
never presented as `references` proof; no cold-start empty result is recorded
as absence (no `lsp` call was made at all).

---

## Axes (this seat, this round)

- **A1 weight** — dead pins / dead params / duplicated accumulators /
  unreachable branches in the r78 delta.
- **A2 falsifiability** — every deleted pin's catch must survive in the class
  gate; every retained pin must keep its catch.
- **A3 contract** — receipt bytes, verdicts, prior-75 rows, insertion-only.
- **A4 replay reproducibility** — a third party re-derives every claim from the
  artifacts alone.

Admission rule: a deletion is *proposed* only when A3 is byte-for-byte unmoved
and A1 improves; A2 is never traded for A1. Anything that moves a prior-75
receipt byte is **rejected by the tasking**, and anything that moves any
receipt byte at all is reported separately as a candidate, never folded in
silently.

**Harness validation.** A scratch copy of the unmodified fixtures replays the
full battery **92/92 PASS** (`runs-control/love-20261014T211556516761Z`) and is
**147/153 files byte-identical** to the r78-author's final run
(`corpus/live/r78-author/runs/love-20261014T210544087564Z`); the 6 differing
files are `probe.stdout.txt`, the four `splice-*.stdout.txt` and
`verdicts.json` — and the author's own two consecutive runs differ in
**exactly the same 6 files** (`210544…` vs `210613…`: 147/153), so the residual
is the declared timing jitter, not harness drift. All 146 IW receipt files
(73 cells × stdout+stderr) are byte-identical to the author's reference.

## Result

| variant | files | change | Δ weight | IW receipts vs control | battery |
|---|---|---|---|---|---|
| `v0` baseline | — | none | 0 | 146/146 byte | 92/92 |
| **`vbat`** | battery | **P1** 33 redundant pins (11 rows) | **−11 lines / −954 B** | **146/146 byte** | **92/92** |
| **`vprobe`** | probe | **P2+P3+P4** dead params, unreachable arms, dead fallback | 0 lines / −227 B | **146/146 byte** | **92/92** |
| **`vfold`** | both | **P1+P2+P3+P4 (fold target)** | **−11 lines / −1181 B** | **146/146 byte** | **92/92** |
| `vobs` | probe | **P5** 7 dead observer fields (candidate) | 0 lines / −364 B | 132/146 byte (14 r78 rows move) | 92/92 |
| `vmutfull` | probe | complete `mut` fold (W1, withheld) | −7 lines / −496 B | 130/146 byte (16 token-only) | 92/92 |
| `vover` | battery | fold + 7 over-deletions (control) | — | — | fuzz: **354 divergences** |

`IW receipts` = the 146 deterministic IW files (stdout+stderr) byte-identical
to the control run. `vfold` = `corpus/live/r78-simplifier/vfold/`, reviewable as
`corpus/live/r78-simplifier/fold.diff` (257 lines).

**Falsifiability evidence (A2), four independent layers.**
1. **Differential equivalence fuzz** (`equiv_fuzz.py`, `evidence/fuzz_summary.json`):
   baseline vs folded battery over the measured receipts + a mutant corpus
   (every flat key × a systematic wrong-value set, **every key pair**,
   relation-group subsets, 2 000 random multi-key mutants per row, at the
   measured rc and at rc ∈ {−11, 0, 1}): **457 100 evaluations, 0 verdict
   divergences**.
2. **Over-deletion control** (`vover`, `evidence/fuzz_over.json`): the fold
   *plus* the 7 relation pins that look single-key-redundant (fire.step,
   final.steps, final.count) → **354 divergences** (e.g.
   `fire.step=5 + final.steps=201`, `built.bodies=5 + final.count=5`). The
   retained set is tight in the measured sense: those pins carry a catch that
   over-deletion loses.
3. **The author's own 51-op gate-ablation matrix re-run against the folded
   battery** (`ablate_variant.py`, `evidence/ablation_vfold.json`): **37
   caught, 0 not caught, 0 tag absent, 0 base mismatch** — identical to the
   baseline run. (The fold touches **no classifier byte** — every battery hunk
   is inside `IW_CELLS`, lines 904–1296, while `iw_classify` starts at 1347 —
   so the author's and the reviewer's gate matrices apply unchanged; the re-run
   is the guard.)
4. **Per-pin ablation** (`pin_ablate.py`): for every deleted pin, every wrong
   value of its flat key still FAILs the row under the folded battery
   (class → anomaly); `evidence/pin_ablation.json`. The census that selected
   the 33 pins, the retained-pin list, and the semantic class of each deletion
   are in `evidence/pin_semantics.txt`.

---

## P1 — 33 redundant pins whose predicate the class gate already owns (PROPOSE, byte-identical)

**Finding.** The 17 r78 rows carry 375 pins. **33 of them (11 rows) restate a
decisive conjunct of the very class gate that yields the row's declared
class** — the same predicate authored twice, on the same flat key. Two tiers:

- **29 literal restatements** — the gate contains `flat.get(k) == "<pinned
  value>"` with exactly the pinned value (e.g. `r78destroy.dead == "true"`,
  `r78zcap.where == "drain"`, the 8 corrupt-member witnesses in each of the
  two depth-2 rows).
- **4 relation restatements** — `livelock_all`'s `r78obs.drain_n`/`r78obs.aborts`
  are forced by the gate's `aborts == drain_n == rate` chain once the retained
  `fire.step=4` and `final.steps=200` pins fix `rate=197`.

Per row (deleted pins): `n_queue_inner_drain` 1, `n_destroy_contacting_wp` 1,
`n_destroy_ground_wp` 1, `n_destroy_fx_wp` 1, `n_depth2_fxdrain` 1,
`z_drain_use_after` 3, `z_touch_then_end` 3, `livelock_all` 4,
`n_destroy_contacting` 2, `n_depth2_drain` 8, `n_depth2_drain_wp` 8.

**Why deletion cannot flip a verdict.** A row fails if *either* the class
mismatches *or* a pin fails. For every deleted pin, class-match implies the gate
conjunct, which is at least as strong as the pin — so any receipt that would
have failed the pin still fails the row (via `class → anomaly`). This is
measured, not argued: the 457 100-evaluation fuzz found **0 verdict
divergences**, and the author's matrix still shows 37/37 row-fails.

**Preserved contract.** `vbat`/`vfold`: battery **92/92**; 146/146 IW receipts
byte-identical; `verdicts.json` identical modulo the observed-only jitter rows;
every retained pin keeps its exact value (`verify_variants.py`).

**Fold shape and rule.** After the fold the row layer matches its own declared
rule (`main.lua`-side comment: rows pin *"the decisive witnesses the class gate
does not already enforce"*) — **one authority per predicate**, the r77-P3
precedent applied to r78.

**Tradeoff, named.** Failure *attribution* changes for those 33 witnesses: a
mutated witness now reports `class anomaly` instead of `pin:<key>`, and the
inline witness list the reader sees shrinks. Verdict, class, rc and every
retained pin are unmoved.

## P2 — dead parameters in the r78 probe (PROPOSE, byte-identical)

- **`r78_drain_hook(contact, fa, fb, dyn)` → `(contact, dyn)`** (definition
  `main.lua:1075`, call `main.lua:805`). Census: `fa`/`fb` occur 0 times as
  variables in the hook body (only inside the `r78zcap … fa=%s fb=%s` format
  string, which names the *contact's* fixtures, not the parameters). Same line
  count. In-pattern with the r77-P4 fold of the same helper's parameter list.
- **The `cb` field is `"bc"` in all 17 rows** (`census.txt`): the field, its
  read (`R78S.cb`) and the per-row declaration are one dead parameterization.
  Fold: drop `cb = "bc",` from the 17 rows; `r78_cb` becomes one channel
  constant (`local r78_cb = "bc"`) and the arming path keeps its shape. A
  pre-r78 cell is unaffected (`R78S ~= nil` still short-circuits).
- **The `mut` field is `"b3"` in all 3 `nested_queue` rows** plus **three
  `or "b1"` fallbacks** at the act call sites (`main.lua:574,577,581`). Fold:
  drop the field, `r78_mut` becomes one queued-body constant, the fallbacks go.
- **`(R78S.act or "none")` → `R78S.act`** (`main.lua:767`): every r78 row
  declares `act`, so the fallback is unreachable (contrast: the r77 table has
  empty `ext_*` rows, where the same fallback is schema-justified).

## P3 — unreachable branches in `r78_body_of` (PROPOSE, byte-identical)

`main.lua:1009–1013` maps a label to a body across `b1/b2/g/b3`, but the only
call site passes `r78_mut`, which is `"b3"` by construction (P2). The `b1`,
`b2` and `g` arms are unreachable; folded to the single live arm + a comment
(same line count, so no line number moves). Census + call-site list:
`evidence/census.txt`.

## P4 — the registry comment (PROPOSE, byte-identical)

The block at `main.lua:214–219` documents the fields that P2 removes; rewritten
in place to document what remains (same 6 lines).

## P5 — dead observers: 7 fields with no reader (CANDIDATE, r78-row bytes move)

**Finding.** A mechanical census of every `r78obs.*` / `r78nextstep.*` reader
(pins + gates, whole repo) leaves **7 emitted fields with no reader at all**:
`r78obs.step`, `r78obs.locked`, `r78obs.b1pos`, `r78obs.depth`, `r78obs.in_cb`,
`r78nextstep.count`, `r78nextstep.aborts`. The only occurrences outside the
fixture are *quoted receipt text* in `reports/round-78/r78-critic.md` (prose
evidence, not a consumer). The other 8 r78obs fields and 4 r78nextstep fields
are live in 1–11 rows each.

**Falsification proof** (`field_census.py`, `evidence/field_census.txt`): for
each of the 7 fields, in every row whose receipt carries it, mutating the field
never fails the row (**0 catches**) — they carry no catch, so removing them
cannot reduce falsifiability. Control: mutating `r78obs.count` fails 9 rows.

**Measured cost (why this is a candidate, not the fold).** `vobs` is a
same-line-count edit (−364 B) and the battery replays **92/92**, but 14 r78
receipts change by exactly their `r78obs`/`r78nextstep` lines (132/146 strict).
**No prior-75 byte moves** — so under the tasking's literal bar (`REJECT
anything touching prior-75 receipt bytes`) it is admissible, and it is
fold-ready as `fold-vobs.diff`; it is kept out of the primary fold only because
it does not meet the stronger carrier I held everywhere else ("146/146 IW
receipts byte-identical"). The dead cells (`n_depth2_drain*`,
`n_destroy_contacting`) are untouched: they die before the observer lines.

---

## W1 — the complete `mut` fold (WITHHELD, prior-75 token drift measured)

`vmutfull` finishes the P2/P3 `mut` cluster: delete the constant line, inline
`local mb = b3`, drop `r78_body_of` and its forward declaration (**−7 lines**).
Battery: **92/92 PASS**. But the probe's line count moves, so receipt line
tokens move — measured: **131/153 byte-identical, 16 receipts token-only**
(the 11 prior rows the r78 author already declared token-unpinned —
`bc_cowrap_unp`, `bc_coyield`, `bc_draindefer`, `bc_newbody_unp`,
`bc_setpos_unp`, `bc_setpos_wp`, `bc_worlddestroy`, `cowrap_update_yield`,
`ext_worldrelease`, `wp_coyield`, `wp_drain_throw` — plus 5 r78 `srcline` rows:
`livelock_all/stop2/transient`, `n_destroy_contacting`, `z_abort_use_after`).
That is exactly the class the tasking rejects. Kept as provenance and as the
measured representative for W2 (`fold-vmutfull.diff`).

## W2 — duplicated emit blocks (WITHHELD by arithmetic)

The r78 delta authors the same emission 2–4× verbatim: `r78setpos ok=…` ×4
full blocks (`nested_probe`, `nested_inner_cb`, `nested_queue`, `nested_twice`),
`r78queue what=…` ×3 full blocks (+1 `api_missing` arm), `r78destroy what=…`
×3 full blocks (+1 `api_missing` arm), `r78npre lock=…` ×2,
`r78zstate tag=…` ×2 (`evidence/census.txt`). Merging them into helpers is the
obvious dedup — and it changes the probe's line count above the deepest token
site (`main.lua:1302`, `evidence/census.txt`), so it moves prior-75 receipt
bytes exactly as W1 measured. **Stop rule:** no probe-side net line deletion
above line 1302 is admissible while the prior-row token sites are live. No
separate run is needed (same class as W1, r77-W2 precedent).

## W3 — other dead branches behind line deletions (WITHHELD by arithmetic)

`r78_fxcount`'s `if b == nil` guard (`main.lua:993`), `r78_zprobe`'s
`r78_zh == nil` branch (`1045–1048`), and the two `api_missing=contact_fixture`
arms are defensive-unreachable for every r78 cell (the hook always has a live
contact and body). Deleting them needs line removal → token drift → rejected.
The `r78_body_of` arms are the one such branch that is foldable at zero line
cost (P3).

## Retained / rejected (measured, not taste)

- **R1 — `rc` / `done` pins**: they duplicate the classifier's branch-entry
  condition on every row, but they are present on all 73 rows (including the
  56 prior rows), are the row's launch contract, and no prior round ever
  touched them. Deleting them on r78 rows only would create a second
  convention → withheld (r77-R3 precedent). `done` shows up as the only
  "candidate" in 17 rows of the folded per-pin ablation for this reason.
- **R2 — near-miss pins that look redundant but are stronger than their gate**:
  `r78setpos.pos_after` (gate `startswith("1234.5,678.9")`, pin exact),
  `r78nest1.err` (gate substring, pin exact), `r78obs.count` (gate reads
  `final.count`, not this key), `final.count` (gate relation has an unpinned
  `built.bodies` operand), and the livelock relation keys (`fire.step`,
  `final.steps`, `final.count`). Each is *measured load-bearing*: the per-pin
  sweep leaks a wrong value (`evidence/pin_ablation.json`) and the
  over-deletion control diverges 354 times.
- **R3 — `or nil` suffixes on the r78 locals**: `x or nil` ≡ `x`, but the same
  idiom is used throughout the r77 block; folding it on r78 lines only is a
  second convention → not touched.
- **Observation (not a fold)**: the r78 `inner_drain` gate calls
  `int(flat.get("built.bodies", "0"))` unguarded (`love_battery.py:1564`); a
  non-numeric `built.bodies` mutant raises `ValueError` out of `iw_classify`
  instead of returning `anomaly`. The differential fuzz catches the raise and
  maps it to a row failure, so no verdict differs — but the classifier is not
  fail-closed *by return* on that key. Flagged for a future hardening round,
  out of a simplifier's remit.

---

## Preserved contract

- **Battery:** 92/92 PASS, `launch_ok=True`, `done_marker=True`, exit 0, for
  `vbat`, `vprobe`, `vfold`, `vobs`, `vmutfull` (and the control). Run dirs:
  `corpus/live/r78-simplifier/runs-{control,vbat,vprobe,vfold,vobs,vmutfull}/`.
- **Receipts:** for `vbat`/`vprobe`/`vfold`, 146/146 IW files byte-identical to
  the control run — including all 11 prior-row token-bearing receipts, i.e.
  **zero token drift** (the probe edits are within-line; the battery edits
  cannot affect receipts).
- **Prior-75:** untouched. 56 prior rows are pin-identical by mechanical check
  (`verify_variants.py`); insertion-only holds — the fold removes only r78
  additions and touches no prior code path or prior row.
- **Verdicts:** `verdicts.json` identical in totals/verdicts/pins; the 6–7
  differing rows are observed-only timing jitter (same class as the author's
  own run-to-run variation).
- **Pins/classes:** every retained pin keeps its exact value; every declared
  class unchanged (`verify_variants.py`: all invariants hold; 33 edited probe
  lines, all within-line).

## Evidence index

| artefact | content |
|---|---|
| `fold.diff` | the proposed fold (battery + probe) as a reviewable patch |
| `fold-vobs.diff`, `fold-vmutfull.diff`, `fold-vover.diff` | the P5 candidate and the two withheld/control probes |
| `vfold/`, `vbat/`, `vprobe/`, `vobs/`, `vmutfull/`, `vover/`, `scratch/` | built variants (fold target + measured probes) + verified fixture copy |
| `mkvariants.py` | variant builder; `verify_variants.py` | mechanical invariants (prior rows, retained pin values, line-count) |
| `equiv_fuzz.py`, `evidence/fuzz_summary.json`, `evidence/fuzz_over.json` | 457 100-evaluation differential equivalence (0 divergences) + over-deletion control (354) |
| `ablate_variant.py`, `evidence/ablation_vfold.json` | the r78-author's 51-op gate matrix re-run against the folded battery (37/37 caught) |
| `pin_ablate.py`, `evidence/pin_ablation.json`, `pin_semantics.py`, `evidence/pin_semantics.txt` | per-pin falsification sweep + the semantic class of each of the 33 deletions |
| `field_census.py`, `evidence/field_census.txt` | emitted-vs-read census and the dead-observer mutation probe |
| `census.py`, `evidence/census.txt` | registry field values, read sites, drain-hook params, duplicated emits, every token site (deepest = 1302) |
| `compare_runs.py`, `compare_tokens.py` | byte / token-only / numeric / structural receipt comparison |
| `evidence/compare-author-runs.txt` (see runs) | author-run-to-run jitter calibration (147/153) |
| `runs-control/`, `runs-*/` | replay runs (receipts + `verdicts.json`) |
| `seq_runs.sh`, `seq_runs*.log` | the sequential replay harness (parallel LOVE launches contended once and were re-run; the first parallel batch's failures were a missing `conf.lua` in the variant dirs — fixed and recorded) |

## Tradeoffs, limits, blockers

- **P1 changes failure attribution, not verdicts.** 33 witnesses now fail as
  `class anomaly` instead of `pin:<key>`; a future seat debugging a row reads
  the gate instead of the pin list for those keys. All measured.
- **P2's `cb`/`mut` folds trade registry expressiveness for weight.** A future
  r78-style cell that arms on another channel or queues another body would need
  a code change; today no such cell exists (census: 17×`"bc"`, 3×`"b3"`). The
  constants keep a single named authority, so no second convention is created.
- **P5 and W1/W2/W3 are byte-moving** and are therefore separated from the
  fold. P5 is admissible under the tasking's prior-75 bar; W1 is not (it moves
  11 prior-row receipts); W2/W3 are blocked by the same arithmetic.
- **Residual risk, named:** the fuzz's mutation pool is finite (~457 k receipts
  over 17 rows); the gate was treated as the authority by syntactic inspection
  of its equality conjuncts, not by a full symbolic proof. No `lsp`/`references`
  device exists on this host — census + replay + differential harness is the
  strongest available carrier, and it is labelled as such.
- **Blockers:** none.
