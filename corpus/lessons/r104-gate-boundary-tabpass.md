# Round 104 — gate boundary: the PASS-line census is canonical-form only (tab-PASS hole), and the six "unflagged" shapes are four different things

**Scope.** r103 landed the receipt-shape meta-gate (`receipt_shape_flag`, `corpus/fixtures/run_battery.py:1877`)
and measured its boundary against a 10-shape synthetic evasion catalog
(`reports/round-103/mutations/mut05_gate_evasion.py`): 4 flag, 6 unflagged, "accounted-by-design or
verdict-layer-harmless". r103's adjudicator routed the tab-PASS hardening forward. This round closes it and
re-classifies the six.

Engine/host: `4.7.2.stable.arch_linux.ed1daf0bf`, Linux, headless. All figures below are **[obs]** unless
labelled [inf]/[unknown]. `run_battery.py` was **never executed**; every measurement imports or AST-extracts
functions out of it, and stored receipts are read as data. Scratch `/var/tmp/r104-R2/`. Evidence shard:
`reports/round-104/r104-scr2.md`; harnesses: `reports/round-104/mutations/r104-R2-*.py`.

## 1. The hole, stated exactly

The census is `pass_lines = [line for line in output if line.startswith("PASS ")]` (line 1904). It feeds both
the `RECEIPT_MULTI_PASS_GRAMMAR` branch and the single-PASS branch (`len(pass_lines) > 1` →
`unaccounted_pass_lines`; `pass_line_unanchored` otherwise). The single-PASS branch's anchor test is
`any(anchor in line for anchor in anchors)` — a **substring** test. So a line that does not literally begin
`PASS ` (space) is:

- invisible to the census, and
- unable to satisfy the anchored-pin test (its anchor is `PASS …` and the forged line has no space there).

⇒ a forged `PASS\tforged=…` or `\tPASS forged=…` line is invisible to **both**, and appends to any
single-PASS row unflagged. Measured: `input_route` + `PASS\tforged=true` → live gate 0 flags
(`s4d_tab_after_pass_simple`); + `\tPASS forged=true` → 0 flags (`s4a_tab_lead_simple`).

The same predicate appears at three more sites — `:1965` and `:1970` (declared SEQ span membership) and
`:1988` (DIAG-window membership). **At those three sites the loose form is the stricter one**: `PASS`-prefixed
lines are exempted from the foreign-line check there, so replacing the predicate wholesale *loosens* those
censuses. The correct landing is therefore **site-specific** (census only), not a global textual replace.

## 2. Landing patch (site-specific; mutation content — orchestrator applies)

`reports/round-104/mutations/r104-R2-tabpass-census.patch` (808 B, sha256
`df9c0403aa7cfca2f1027364d7826c4d8d884d02a807377533783923d5b12492`), one hunk at `:1904`:

```diff
-    pass_lines = [line for line in output if line.startswith("PASS ")]
+    # r104-R2 (C2a): the census takes every PASS-prefixed line, not only the
+    # canonical "PASS " form. `PASS\tforged=…` and `\tPASS forged=…` are
+    # invisible to this census AND to the anchored-pin rules below, so a
+    # forged TAB-separated PASS line appends to any single-PASS row unflagged.
+    pass_lines = [line for line in output if line.lstrip().startswith("PASS")]
```

Verified on a fresh clone of HEAD (`/var/tmp/r104-R2/repo`): `git apply --check` OK, applied, `py_compile`
OK, post-state sha256 `bc3423432e9e7a2e47b328f74cbd4c67960f1305f153b1d70523571c6cd979ba`. With the patch
applied, replaying the full catalog gives s4a and s4d newly flagged (`unaccounted_pass_lines`) and **all
other shapes unchanged**; all four green controls stay silent.

`lstrip()` (not a `\t`-only strip) is deliberate: it also catches a leading space run and `\r`; it does **not**
touch `PASS`-only or `PASS`+trailing-space lines, which is what keeps the false-positive surface at zero.

## 3. False-positive analysis (the required part)

Two independent floors, both [obs]:

| floor | command | result |
|---|---|---|
| stored receipts | `r104-R2-gate-boundary.py --census-tighten` over 8 stored runs | **4548 PASS lines, 0 non-canonical**; old census 4548 = new census 4548, delta +0 |
| fixture print sites | `grep -rnoP '"PASS[^\"]*"' corpus/fixtures/*.gd \| grep -vP '"PASS '` | **0 hits** across all 197 `"PASS…` literals — every one begins `PASS ` |
| green silence (V0/V1/V2 × 8 runs) | `r104-R2-census-sites.py --green` | identical flag counts per run; totals V0=37 V1=37 V2=37 over 4352 rows |
| green controls ×4 under the applied patch | clone replay | 0 flags each |

⇒ tightening cannot create a false flag on any receipt the lane has ever stored, and cannot fire on any
fixture print site as it exists. The r103 meta-gate's "0 flags" green runs survive unchanged.

## 4. The six unflagged shapes are four different things (the C2b reclassification)

Each row below was replayed against the **live** gate from a scratch copy, and against `classify_process`
AST-extracted from the same source (sha256 `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`).
**Leg A (rescue).** Delete the row's own pin line, then re-grade with the forgery present:
`rescued=False` means the forgery cannot substitute for the pin. All six rows: `deleted=1 intact=True
depinned=False rescued=False` — a forged line cannot supply a row's pin.

| shape | gate | harmlessness verdict | evidence |
|---|---|---|---|
| `s1b_banner_dup_launch` | 0 | **harmless in the pinned region** | the duplicate banner sits at index 4, inside the row's own 11-line DIAG window; `foreign_in_diag_window` legitimately admits banner-shaped lines anywhere in that window (Leg B: same forged banner appended to `export_launch_embed_boot` → 0 flags, while a plain foreign line → 1). Duplicate banner byte-identical to index 0 [obs] |
| `s2a_diag_other_family_simple` | 0 | **verdict-layer harmless** | appended `EXPORT_LAUNCH_DIAG …` to `input_route`; `PASS` (7 chars) is not a substring of that line → pin containment unmoved; Leg A rescued=False |
| `s2b_diag_forged_launch` | 0 | **real gap** | appended `EXPORT_LAUNCH_DIAG embed forged=1`; class-matched by `^[A-Z][A-Z0-9_]*_DIAG\b` and payload-unchecked in the whole-receipt DIAG window |
| `s1a_banner_forged_seq` | 0 | **real gap** | the forged banner carries a *different* engine version (`v9.9.9`) and a different hash from index 0, at index 2 of a 23-line receipt — outside the declared span, so no span check reaches it |
| `s4a_tab_lead_simple` | 0→1 | **verdict-layer harmless; now flagged** | `\tPASS forged=true`; pin containment unmoved (no `PASS ` substring); Leg A rescued=False |
| `s4d_tab_after_pass_simple` | 0→1 | **verdict-layer harmless; now flagged** | `PASS\tforged=true`; same reasoning; Leg A rescued=False |

**Leg B (region move).** The same foreign line in different region classes. The stored receipt carries no
`SEQ_*`/`*_DIAG` line (those live in the row's **pin**, which is not part of the receipt), so a declared
window is synthesised explicitly; `banner_on_declared_span_ctl` is the uncontaminated control:

```
banner_in_span              case=r100b_seq_clean          flags=1 ['foreign_in_span']
banner_in_tail              case=r100b_seq_clean          flags=0 []
banner_on_declared_span_ctl case=r100b_seq_clean          flags=0 []   <- control, clean
banner_on_simple            case=input_route              flags=0 []
diag_on_simple              case=input_route              flags=0 []
diag_on_launch_row          case=export_launch_embed_boot flags=0 []
launch(diag) forged_banner  flags=0 []      launch(diag) plain_foreign flags=1 ['foreign_in_diag_window']
prod(diag)   forged_banner  flags=0 []      prod(diag)   plain_foreign flags=1 ['foreign_in_diag_window']
```

⇒ the same forged banner is **caught inside a declared span** (`foreign_in_span`) and **missed in the tail**,
in a DIAG window, and on every `no_census` row. The span-interior check has teeth; the tail check does not
reach a banner-shaped line (the tail loop treats `RECEIPT_BANNER_RE` matches as block resets, so a banner
there re-opens rather than closes the block).

**Leg C (class allowance).** Inside a DIAG window, `real_banner_dup`, `forged_banner`,
`forged_diag_same_family` and `forged_diag_other_family` all give **0 flags**; only a plain foreign line
gives 1. The class regex alone admits the line regardless of payload.

**Leg D (rescue at the verdict layer, the strongest harmlessness test available):** all 9 stored FAIL
receipts were injected with the union of the six shapes' forged lines (5 distinct lines) and re-graded with
their own signatures — **0 grade flips**. A forged line cannot flip a FAIL to PASS by being appended; it can
only ride along on an already-PASS row. That is what makes the six "verdict-layer harmless" *for grading*,
and it is simultaneously why the gate's own account matters: the receipt is supposed to be a faithful record
of what the fixture printed.

## 5. Region reach — why three of these shapes are not cosmetic

[obs] Over 4352 live PASS rows with output:

| region class | rows | non-PASS census in the landed gate |
|---|---|---|
| `no_census` (no `SEQ_*`, no `*_DIAG` line) | 4119 | **none** — only the PASS census runs |
| `seq_span` (declares `SEQ_BEGIN`/`SEQ_END`) | 16 | span-interior + post-span tail |
| `diag_window` (any `*_DIAG` line) | 208 | whole receipt (banner/blank/PASS/`*_DIAG`/progress/ANSI only) |

⇒ **94.8% of live receipts have no foreign-line census at all.** Any line that is not `PASS`-shaped and
whose banner/diag shape does not match a class regex is simply unexamined on those rows — the r102-mut9
"foreign line in span" residual is closed only for the 224 rows (5.2%) that declare a span or a DIAG verb.
The forged-banner shape `s1a` sits in the `no_census` class and is therefore unexamined **by construction**,
not by oversight: a receipt in that class has no declared window to audit.

## 6. Two defects found in the r103 record (hand to the round-104 adjudicator)

1. **The landed gate has no banner rule.** `r103-receipt-shape-gate.md` documents a `banner_shape` flag class
   ("engine banner not exactly once at line 0"). In the landed source the string `banner_shape` appears
   **0 times**; `RECEIPT_BANNER_RE` (`:1852`) is used only to *exempt* banner lines inside span/diag windows
   (`:1971`, `:1988`); the why-keys `receipt_shape_flag` can emit are exactly
   `anchor_line_multiplicity, derived_evidence_unbound, fail_closed_missing_signature, fail_closed_non_text_line,
   foreign_after_span, foreign_in_diag_window, foreign_in_span, pass_line_grammar_mismatch, pass_line_unanchored,
   seq_marker_shape, unaccounted_pass_lines`. r103's "0 flags ×2" therefore never exercised a banner rule, and
   s1a/s1b were never gate-catchable at the landed revision. **The r103 green result stands; the documented
   flag class does not exist.**
2. **The r103 green-silence figure is revision-scoped.** The landed gate is silent on the last 5 stored runs
   (0 flags / 2754 audited rows) but flags 37 rows across the 3 earlier ones: `dead_shape_allowlist_entry` ×8
   per run on the two r101-era runs (the 8 `export_launch_*` grammar entries are absent from those record
   sets — the intended floor), `pass_line_unanchored` + `anchor_line_multiplicity` on the two `r101_ytrans`
   rows (the r101 `--offy` dead-flag repair changed `distinct_ticks=8`→`7`, `last_change_tick=68`→`64`, and
   `r95b_lines=778`→`776`; the stored r101 receipts predate it), and `foreign_in_diag_window` ×15 in run
   `20261019T001435805887Z` only (three `Unicode parsing error … U+FFFD` lines per `export_div_s01` arm — the
   in-fixture s01 fix landed during r103). "0 flags" is true of the receipts measured after each fix, not of
   the corpus as a whole.

## 7. Ceilings (do not over-trust)

- The tightening closes the TAB/NBSP-prefixed PASS hole **at the census**. It does not add a banner rule, a
  version check, or a foreign-line census to the 4119 `no_census` rows; those remain open by design.
- `lstrip().startswith("PASS")` still does not catch `PASS` embedded mid-line (e.g. `X PASS …`), which is
  correct — such a line is not a receipt PASS line and stays a `foreign_line` candidate where a census exists.
- The engine-diag vocabulary and the `*_DIAG` class regex are version/platform bound (measured only on
  4.7.2.stable.arch_linux.ed1daf0bf).
- Leg D proves the six shapes cannot **flip a grade**; it does not prove a future shape cannot (e.g. a shape
  that supplies a *different* legitimate pin for a row whose own pin was dropped — that is the "stolen pin"
  class, untested here).
- Whether `RECEIPT_MULTI_PASS_GRAMMAR` should absorb a 15th `r100_gui` line, and whether the 208 DIAG-window
  rows should get a payload census, are open questions this round did not answer.
- **Count-method note.** PASS-line counts differ by one between harnesses (4548 from the raw-line walk in
  `r104-R2-gate-boundary.py --census-tighten`, 4539 from the region walk above, 4343 vs 4352 for the
  PASS-row denominator): the region walk skips rows whose `output` contains a non-`str` line, the raw walk
  does not. Both report **0 non-canonical**; cite the harness alongside the number.

## Reproduce

```text
python3 reports/round-104/mutations/r104-R2-gate-boundary.py --census-tighten   # 525 B
python3 reports/round-104/mutations/r104-R2-census-sites.py   --all            # 3111 B
python3 reports/round-104/mutations/r104-R2-region-teeth.py                    # 3097 B
python3 reports/round-104/mutations/r104-R2-harmless-legs.py                   # 1470 B
git apply --check reports/round-104/mutations/r104-R2-tabpass-census.patch     # OK at eff29d1d
```

Harness sha256: `r104-R2-gate-boundary.py` `0b571d1a…`, `r104-R2-census-sites.py` `adb826e4…`,
`r104-R2-region-teeth.py` `e5f6491b…`, `r104-R2-harmless-legs.py` `65c41ff9…`. Raw stdout retained at
`/var/tmp/r104-R2/out-{census,sites,region,legs}.txt`.
