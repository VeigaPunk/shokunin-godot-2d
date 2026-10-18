# R101 — a dead flag's row is not coverage, and the Y axis is invariant (Godot 4.7.2 headless)

Sources: `corpus/fixtures/run_battery.py` (the `r95b_order_celloff_y1000` row,
RETIRED at r101 — see `reports/round-101/r101-adjudicator.md`); `corpus/fixtures/r95b_order.gd`
(md5 `b9156c885ff26be4ce369407eb64f852`); `corpus/fixtures/r101_ytrans.gd`
(sha256 `0d5093d6…`, the repair); `reports/round-95/r95-simplifier.md` F1,
`r95-reviewer.md` §F1, `r95-adjudicator.md`; `reports/round-101/r101-E17.md`;
`reports/round-101/r101-scr3.md` (this round's measurements).
verified-at: 2026-10-18, Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Linux x86_64.

## Symptom
A CASES row passed `--offy=1000` to a fixture that never read the flag. The row
PASSed, its sibling PASSed, and the two PASS lines were byte-identical
(md5 `e06cb7f3753fb61fa288116aae4a8ca4`). The row's *name* claimed Y-axis
translation coverage; its *signature* was a duplicate. Nothing in the harness
compares sibling signatures, so the defect survived four rounds of green runs.

## Root cause, two layers
1. **Name vs signature.** Coverage is recorded by the row name + argv and
   measured only by the fixture's printed signature. A flag with no read site
   produces a signature identical to its control. PASS is evidence of a
   construction, never of a name.
2. **Geometry.** The dss query point is hardcoded in Y (`(16.0 + ox, 0.0)`), so
   the naive repair — translate the pile, leave the query — measures *absence*
   (`n_t2=0`, empty ladder), not invariance.

## The law, measured
With pile and query translated together, `offy=+1000` reproduces both the
`offy=0` and the `offx=+1000` readings: same ladder (`t2:4,0,2,3,1`), same hit
count (5), same offset-subtracted relative positions, byte-identical across
18/20 (probe) and 39/40 (repaired fixture) fresh processes — the exceptions are
the phase mode of pitfall 1. Y translation is invariant in the relative
frame — *and therefore ordering alone can never distinguish a y cell from an x
cell.* The row must pin the offset echo plus an absolute-y or out-of-reach read.

## Closure pattern — three pins in conjunction
| pin | correct | frozen fixture | body-only | echo-only |
|---|---|---|---|---|
| `offy=<v>` echo | ✓ | ✗ (token absent) | ✓ | ✓ |
| hit count / non-empty (`n_at_y=5`, `n_at_0=0`) | ✓ | ✓ | ✗ (0) | ✓ |
| offset-subtracted relpos (y column) | `0.0000` | `0.0000` | `[]` | `-1000.0000` ✗ |

Each pin alone is satisfiable by a broken variant; only the conjunction closes
the class. A fourth, strongest pin is relational: in one replay, the y cell's
transcript must equal the x cell's (same construction, different offset).

## Pitfalls
1. **Phase bimodality.** 4/40 fresh processes of the scratch probe (10 %) and
   1/40 of the repaired fixture itself emitted a one-tick-shifted ladder under
   host load 37–58; the shifted transcript is identical for the y and x cells
   (a process-level sampling phase, not geometry). Pin hit counts, sorted
   relative sets, absolute-y reads, offset echoes and in-replay relations; do not
   pin a tick-labelled ladder, the raw hit order, or `*_eq_canon` booleans —
   those are 2–10 % flaky under load.
2. **Half-extent floor.** A body-only repair is indistinguishable from the
   correct one while |offy| ≤ half the collider height (measured: 5 hits at 20,
   0 hits at 21 for a 40×40 body). Choose |offy| ≫ half-extent.
3. **Never patch the frozen fixture.** `r95b_order.gd` is a frozen byte-copy of
   record; the old row's byte-identity *is* the defect evidence. Land a new
   fixture + rows.
4. **Echo is not measurement.** An echo-only arm passes the echo and hit-count
   pins; only the offset-subtracted relative column catches it.
5. **stdout ≠ PASS line.** The env diag's `proc=` counter changes per run; pin
   the PASS line, not the whole stdout.

## Verification recipe
1. Census: for the fixture, compare `--flags` passed by CASES rows against
   `opt`/`_opt_*` reads ∪ dedicated `begins_with("--X=")` branches. Expect
   exactly one unread flag before the repair (`offy`) and none after.
2. Reproduce the duplicate: run both argv variants on the frozen fixture and
   diff the PASS lines (expected: identical md5 `e06cb7f3…`).
3. Run the repaired fixture: assert the offset echo, `n_at_y=5`, `n_at_0=0`, and
   the offset-subtracted relpos set `{0,8,16,24,32}×0.0`.
4. Run the two mutants (body-only; echo-only) and assert each is rejected by the
   pin named in the matrix above.
5. Repeat ≥ 20 fresh processes and assert the *pins* hold in every run (the
   phase mode may differ; the pins must not).

## Integration fold (2026-10-18, run 1 → run 2)

Run 1 caught the phase hazard this lesson predicts, in a stronger form: at
`offy=±1000` the ladder/order receipts flipped to a completely different
permutation (`ladder=[t2:4,1,2,3,0;…]`, `t2_vec=[e,b,c,d,a]`, `eq_canon=false`)
because the arm observed 64 real physics frames in-battery vs 3 standalone —
while every translation invariant (`dy_resid=0.0000`, `n_at_y=5 n_at_0=0`,
`t2/t64_absy=[1000…]`, `distinct_ticks=7`, `last_change_tick=64`) held in both
phases. Fold: the PASS lines pin phase-invariant fields only; `ladder`,
`*_vec`, `*_relpos`, `eq_canon`, `t64_relpos` are `R101Y` diagnostics. The
order law at offy≠0 is a mode-envelope diagnostic, not a row pin (r87
`api_press` precedent). Falsification lives in `dy_resid` (a skipped
translation is nonzero), the count fields, and the ysep gap cell.

## r102 dated correction (append-only)

The census row's tripwire sha changed by design at r102: r95b_order.gd was
folded (r101-simp3 queue, 10 folds) — lines 778→776, sha256
4f7e945e…→b367559e831e5e9f9ab9e386591dd0035e24fb4e5ea2efc2c533e11aec2bdcf7.
The `r101_ytrans_census` CASES pin was re-anchored in the same commit; the
`r95b_offy_tokens=0` clause is unchanged (folds removed no offy-relevant
code). The defect class this lesson teaches (a pinned sha is a receipt of the
file at a point in time, not a constant) is exactly why the row exists.
