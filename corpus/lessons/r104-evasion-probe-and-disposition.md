# Round 104 — gate-evasion replay probe + orphaned-companion disposition (Godot 4.7.2.stable)

Two routed surfaces from r103, measured first-hand and landed together because they share one
instrument: the **receipt-shape meta-gate** `receipt_shape_flag` in `corpus/fixtures/run_battery.py`
(`run_battery.py:1877-2020`). (A) the pass-line census is `line.startswith("PASS ")` — a literal
space, so every other `PASS`-prefixed line is grammar-invisible; (B) the r103 adjudicator left six
evasion shapes "unflagged" without proving they are *harmless*; (C) the probe that would keep this
boundary honest was never built; (D) eleven r101 companion fixtures sit orphaned under
`reports/round-101/mutations/orphaned-fixtures/` with no adopt/retire decision.

**Instrument.** `run_battery.py` was **never executed** in this round. Every gate verdict below comes
from the *live* source, extracted by AST: the module is parsed, the `if __name__ == "__main__"` block
is dropped, and the remainder is `exec`'d in a scratch namespace
(`/var/tmp/r104-scr3/live_gate.py`, `load_live()`). Live source sha256 at land:
`2af2bc841ccb416e5fb0e1bbaadc08627e2d4768a8822f6956e867d905a3d0fe`. All runs are `godot
--headless`, scratch under `/var/tmp/r104-scr3/` (never `/tmp` — EDQUOT), engine
`4.7.2.stable.arch_linux.ed1daf0bf`. Every figure is [obs] unless labelled [inf]/[unknown].

## 1. The pass-line census and its widening (C2a)

The census is a single list comprehension; the widening is one predicate. Exact site
(`run_battery.py:1904`, the only `line.startswith("PASS ")` outside the SEQ/DIAG accept clauses at
1965/1970/1988):

```python
- pass_lines = [line for line in output if line.startswith("PASS ")]
+ pass_lines = [line for line in output if line.lstrip().startswith("PASS")]
```

`lstrip()` rather than a bare `"PASS"` prefix, so an indented or leading-whitespace forgery
(`\tPASS forged=true`, r103 mut05 s4a) is censused too; a bare prefix would still miss it.

**False-positive surface (the required analysis).** Over all 8 stored runs in `corpus/live/runs/`:

| measure | value |
|---|---|
| `^PASS` lines, all 8 runs (4484 rows) | **4548** |
| `^PASS ` (space) lines, same corpus | **4548** |
| separator census of the 4548 | `{' ': 4548}` — every one |
| rows audited, 4 green runs (live gate) | 2184, flags **0** |
| rows audited, 4 green runs (widened gate) | 2184, flags **0** |
| runs whose flag list differs live↔widened | **0** |

[obs] There is no `PASS`-prefixed line in the corpus that is not `PASS `-separated, so the widening
is **false-positive-free on the entire stored corpus** — zero rows change verdict. [obs] The
property is emitter-side too: of the `"PASS` string literals in `corpus/fixtures/*.gd`, **198/198**
carry a space as the 5th character (`grep -rhoE '"PASS.' … | cut -c5 | uniq -c` → `198 " "`).

**What the widening actually buys.** On the 16-shape replay (§3): **7 → 12** flagged. The five shapes
it closes are exactly the census-invisible ones — `\tPASS forged=true` (r103 mut05 s4a),
`PASS\tforged=true` (s4d), bare `PASS`, `PASSforged=true`, `PASS\u00a0forged=true`. Two flag forms
carry it: `unaccounted_pass_lines` (non-grammar rows, `observed 2 declared 1`) and
`pass_line_grammar_mismatch` (grammar rows, e.g. a `PASS\t` flood on `r100b_seq_clean` → `observed 15
declared 14`).

**Coupling caveat (measured, not assumed).** The naive text-substitution widening hits all four
`startswith("PASS ")` sites, including the DIAG-window accept clause at `:1988`. Replayed against
the DIAG family that substitution does **not** weaken the window (a `PASS\t` line is now accepted by
the census *and* by the window, so the row still flags as `unaccounted_pass_lines`) — but widening
the *accept* clause is the wrong direction for a gate. The landed patch is therefore **one site
only** (`reports/round-104/mutations/r104-scr3-tabpass-census.patch`, `git apply --check` clean,
1 file / 1 insertion / 1 deletion); the accept clauses stay space-strict, so a `PASS`-prefixed line
that the DIAG window would otherwise admit still fails the census.

The same one-site patch was derived independently by the C2a seat and documented in
`corpus/lessons/r104-gate-boundary-tabpass.md` — the two lessons agree on the site, the predicate and
the zero false-positive surface (the C2a seat reports 197 `"PASS` literals, this seat 198 with the
exact command in §1; both agree that 0 are non-canonical). The two patch files differ only in the
C2a seat's four-line explanatory comment: `diff` of the hunk bodies shows one added code line each,
`line.lstrip().startswith("PASS")`, at the same site. This lesson adds the *replay-probe* contract
and the *disposition* that the C2a lesson does not cover; the orchestrator should land the patch
**once** — prefer `r104-R2-tabpass-census.patch`, which carries the rationale comment.

## 2. Verdict-layer harmlessness of the six unflagged r103 shapes (C2b)

The r103 adjudicator recorded "6 unflagged = accounted classes (banner/diag) or verdict-layer-
harmless (tab-PASS)" as a *claim*. The verdict predicate is `signature in "\n".join(output)`
(prefix-substring pin), so harmlessness has a mechanical form: **a shape line can only flip a
FAIL→PASS if it, alone, satisfies some CASES signature.** Measured (`/var/tmp/r104-scr3/harm.py`):

| shape | line | sig-hits over 558 CASES signature strings |
|---|---|---|
| s1a banner-forged | `Godot Engine v9.9.9…` | 0 |
| s1b banner-duplicate | exact engine banner | 0 |
| s2a diag-other-family | `EXPORT_LAUNCH_DIAG embed forged=true` | 0 |
| s2b diag-forged-same-family | `EXPORT_LAUNCH_DIAG embed forged=1` | 0 |
| s4a tab-lead | `\tPASS forged=true` | 0 |
| s4d tab-after-pass | `PASS\tforged=true` | 0 |
| x1/x2/x3 (r104, §3) | `PASS`, `PASSforged=true`, `PASS\u00a0forged=true` | 0 each |

**MAX_SIG_HITS = 0.** Second, direct test: append each shape line to **every** FAIL row that carries a
CASES pin and re-check the pin — **2160 rows checked, 0 flips**. Third: delete a green row's pinned
anchor, insert the shape line, and ask the live gate — all 20 (case × shape) combinations FLAG (the
missing anchor trips `anchor_line_multiplicity`), i.e. the shape cannot substitute for a deleted pin
either.

[obs] The six r103 survivors are harmless **at the verdict layer** for a stronger reason than
"accounted by design": they cannot create a signature match at all. The banner/diag classes are
additionally *class*-harmless (they are the very vocabulary the DIAG account admits), and the
tab-PASS classes are *census*-invisible, which is the defect C2a closes.

## 3. In-battery gate-evasion replay probe (C3a)

**Contract.** The probe is a stored catalog of K ≥ 8 synthetic shapes; each run replays every shape
against the live `receipt_shape_flag` and the run is green **only if every shape flags as classified**
(a shape declared `must_flag` that comes back clean = red; a `must_clean` control that flags = red).
It is a *boundary regression*, not a classifier: it never runs a Godot process and never edits the
classifier.

**Catalog (K = 16, measured).** Bases are real green records from
`corpus/live/runs/20261018T213443471189Z/verdicts.json` (`input_route` 3 lines/1 PASS,
`export_launch_embed_boot` 11/3 DIAG, `export_prod_base_pck` 9/3 DIAG, `r100b_seq_clean` 23/14
grammar). `live` = landed gate; `wide` = §1 widening (the landed one-site `lstrip()` patch).

| # | shape (base) | class | live | wide |
|---|---|---|---|---|
| 1 | banner-forged, insert idx2 (seq) | must_flag | clean | clean |
| 2 | exact banner duplicate, idx4 (launch) | must_flag | clean | clean |
| 3 | foreign `EXPORT_LAUNCH_DIAG`, idx3 (simple) | must_flag | clean | clean |
| 4 | same-family forged DIAG, idx6 (launch) | must_flag | clean | clean |
| 5 | 5× PASS flood, append (simple) | must_flag | **FLAG** | **FLAG** |
| 6 | 1× PASS flood (seq grammar) | must_flag | **FLAG** | **FLAG** |
| 7 | leading-TAB `\tPASS forged=true` | must_flag | clean | **FLAG** |
| 8 | trailing-space duplicate | must_flag | **FLAG** | **FLAG** |
| 9 | trailing-NBSP `PASS forged=true\xa0` | must_flag | **FLAG** | **FLAG** |
| 10 | TAB-after-PASS `PASS\tforged=true` | must_flag | clean | **FLAG** |
| 11 | bare `PASS` | must_flag | clean | **FLAG** |
| 12 | `PASSforged=true` (no separator) | must_flag | clean | **FLAG** |
| 13 | `PASS\u00a0forged=true` (NBSP separator) | must_flag | clean | **FLAG** |
| 14 | double-space `PASS  forged=true` | must_flag | **FLAG** | **FLAG** |
| 15 | 1× PASS flood on seq | must_flag | **FLAG** | **FLAG** |
| 16 | 1× PASS flood on prod DIAG row | must_flag | **FLAG** | **FLAG** |

Counts: **live 7/16 flag; widened 12/16 flag.** Controls (unmutated rows 1-4 above as
`must_clean`) are silent under both — the probe's green predicate is therefore satisfiable, not
vacuous.

**Calibration — the nine `clean` cells are a *declared* boundary, not a pass.** Shapes 1-4 are the
banner/diag vocabulary the account admits; §2 proves they cannot reach the verdict layer. Shapes
7/10/11/12/13 are census-invisible under the landed gate and become flags under §1 — i.e. the probe
catalog itself is the *change detector* for the C2a patch: a probe run on the landed gate is RED by
design (5 census-class shapes), and turns green once the widening lands. That is the calibration
loop the round asked for.

**Cost.** Catalog build + 16 replays + the 2184-row corpus differential: **0.106 s** wall for both
gate variants loaded, 0.059 s to load and 0.039 s to audit all 8 stored runs (4343 rows). No Godot
process. The probe is affordable in-battery at ~0.1 s and ~600 B of new catalog data; the run-time
cost is dominated by JSON parsing, not by the shapes.

## 4. Orphaned-companion disposition (C3b)

The 11 companions were re-run **live** from a scratch project (`/var/tmp/r104-scr3/proj`, `TMPDIR`
redirected off EDQUOT `/tmp`), targeted `godot --headless … --script res://export_prod_sNN.gd`.
No battery, no CASES registration, shared files untouched.

| fixture | sha256 (head) | exit | stdout/stderr | class | disposition |
|---|---|---|---|---|---|
| `export_prod_s01.gd` | `d6a2868d` | 2 | 2414 B / 365 B | fixture-class: `pack did not load in engine rc=0 autoload_seen=false` | **retire** |
| `export_prod_s02.gd` | `d953f689` | 0 | 3001 B / 0 B | clean, PASS verbatim | **adopt** (pins in r101-E2) |
| `export_prod_s03.gd` | `d5e5314e` | 2 | 156 B / 0 B | fixture-class: `reason=export_rc_a detail=nonzero` | **retire** |
| `export_prod_s04.gd` | `763087b6` | 0 | 418 B / 0 B | clean, PASS verbatim | **adopt** (pins in r101-E4) |
| `export_prod_s05.gd` | `8f16f47e` | 1 | 101 B / 340 B | **parse error**: `_emit_pack() argument 2 should be "PackedByteArray" but is "Dictionary"` (s05:623) | **retire** |
| `export_prod_s06.gd` | `772fb51e` | 2 | 2428 B / 698 B | fixture-class: `entry_row_7 got=project.binary\|0\|e3b0c442… expected=\|114\|b07db252…` (empty sha) | **retire** |
| `export_prod_s07.gd` | `e159f37c` | 0 | 2140 B / 0 B | clean, PASS verbatim | **adopt** (pins in r101-E7) |
| `export_prod_s08.gd` | `e6c63361` | 0 | 1225 B / 0 B | clean, 4 PASS lines | **adopt** (pins in r101-E8) |
| `export_prod_s09.gd` | `79e723f1` | 2 | 602 B / 0 B | fixture-class: `census mismatch: entries=12` vs the pinned 9-entry shape | **retire** |
| `export_prod_s10.gd` | `55ac8760` | 1 | 3004 B / 593 B | **environment-class**: `const SCRATCH_ROOT := "/tmp/r101-E10"` is hardcoded — `/tmp` is EDQUOT on this host | **retire** (see below) |
| `export_prod_s11.gd` | `755207e9` | 2 | 172 B / 0 B | fixture-class: `pack reasons=pck_project_binary_bytes=0` | **retire** |

**Adopt, with fresh pins — 4 fixtures** (s02, s04, s07, s08). Each runs clean at HEAD *and* already
carries a measured CASES-row proposal in its own r101 shard (`r101-E2.md:179-183` two rows,
`r101-E4.md:38-42`, `r101-E7.md:167`, `r101-E8.md:122`). Evidence for adopt is therefore two-sided: a
live green run today, plus a recorded pin from the seat that built it. Registration remains the
orchestrator's act (shared `CASES`), and per r101 discipline the pins must be re-measured, not copied.

**Retire — 7 fixtures.** Five are broken at HEAD for fixture-class reasons (s01 boot probe, s03
export rc, s05 does not parse, s06 empty-hash census, s09 12-entry vs 9-entry, s11 zero
`project.binary`) and their scenarios are covered by the landed `export_prod.gd` rows — retire with
the run bytes above as the evidence. s10 is a different case: its failure is
**environment-class** (a hardcoded `/tmp` scratch root, EDQUOT on this host); a one-line
`SCRATCH_ROOT` repoint was tried and it then advanced to `FAIL zip:open = 1`, i.e. it is broken for a
second, fixture-class reason too. Retire, but do not record "s10 is broken" without the class split —
on a host with a writable `/tmp` it may still be adoptable.

**Overlap census.** Every companion's PASS verb is scenario-unique: of the 11 fixtures' verbs
(`export_prod_s01`…`export_prod_s11`), **0** collide with the 428 landed (verb, subverb) pairs in
`CASES`. So the orphans are additive coverage, never duplicate coverage — the retire decisions rest
on *brokenness*, not on redundancy.

## 5. Ceilings / residuals (do not over-trust)

- The census widening is measured on **one host, one engine version, 4 green runs**. A future fixture
  that emits a non-space `PASS` separator for a legitimate reason would false-flag; the corpus
  evidence says none exists today, and the fix in that case is a declared account entry, not a revert.
- The probe's `must_clean` control set is the 4 unmutated base rows; a richer control set (the 19
  multi-PASS grammar rows) would be stronger and is not built here.
- Harmlessness (§2) is proven for the *shape lines as catalogued*. A forger who also rewrites the
  pinned span is the r102-mut9 family and is out of scope — as r103 recorded, only whole-capture
  grammar equality plus an output-bytes binding closes that, not this gate.
- The orphan disposition rests on a single run per fixture on a load-3 host. s01/s06/s11 failures are
  consistent with the r101 shards' own notes (they were the "broken" class then too), but this lesson
  does not claim re-reproducibility.
- `git worktree` was not used: all verification ran in a scratch project directory
  (`/var/tmp/r104-scr3/proj`) with fixture copies; nothing to remove from the repo.

## 6. Reproduce

```bash
# live gate, no battery execution
python3 - <<'PY'
import ast
src="corpus/fixtures/run_battery.py"; raw=open(src).read(); t=ast.parse(raw)
kept=[n for n in t.body if not (isinstance(n,ast.If) and getattr(getattr(n.test,"left",None),"id","")=="__name__")]
m=ast.Module(body=kept,type_ignores=[]); ast.fix_missing_locations(m)
ns={"__name__":"live","__file__":src}; exec(compile(m,src,"exec"),ns)
import json; d=json.load(open("corpus/live/runs/20261018T213443471189Z/verdicts.json"))
print(ns["receipt_shape_audit"](d["results"]))   # -> {'audited': 538, 'flags': []}
PY

# widening differential + 16-shape replay
python3 /var/tmp/r104-scr3/replay.py          # -> 7/16 live, 11/16 bare-prefix, corpus diffs 0
python3 /var/tmp/r104-scr3/harm.py            # -> MAX_SIG_HITS=0, 2160 FAIL rows, 0 flips

# orphan re-run (one fixture shown; all 11 in the §4 table)
mkdir -p /var/tmp/r104-scr3/proj && cd /var/tmp/r104-scr3/proj
cp .../orphaned-fixtures/export_prod_s02.gd . ; printf 'config_version=5\n\n[application]\n\nconfig/name="host"\n' > project.godot
TMPDIR=/var/tmp/r104-scr3/tmp godot --headless --path . --script res://export_prod_s02.gd -- --root=/var/tmp/r104-scr3/s02
```
