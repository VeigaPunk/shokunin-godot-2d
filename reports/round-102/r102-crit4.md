# r102 C4 — cross-claim interference: ordering + re-pin census (crit4)

Seat: KEY=C4. Shard-only; mutation script `reports/round-102/mutations/r102-crit4-cite-census.py`.
Scratch `/var/tmp/r102-crit4/`. Base: lane HEAD `1392ca21` ("round-101 record…").
`run_battery.py` = 5413 lines, sha256 `bb8f79c92fbc6b7dc9b0c7d7adaffb4d103a51a368970a1b242a08f5915c1336`
(measured `sha256sum corpus/fixtures/run_battery.py`). Host (once, two reads):
`17:41:01 up 1 day, 17:41, load average: 6.55, 8.32, 9.12`;
`17:45:41 up 1 day, 17:45, load average: 18.01, 11.48, 9.95` (round seats ramping).
Rule 1 honored: `run_battery.py` was never executed; all Godot runs are targeted standalone.

## Verdict

| # | finding | class | evidence |
|---|---|---|---|
| 1 | **HARD RED**: C3's r95 fold invalidates the landed `r101_ytrans_census` pin (`run_battery.py:1666`); requires a same-splice re-pin | obs (measured counterfactual) | §1 |
| 2 | `run_battery.py` is a 3-claim collision file (C1 rows / C2 driver fix / C3 comments); one insertion at line ≤1694 moves C2's whole authoring region | obs + inference | §2 |
| 3 | Seat-brief attribution "hold_open_new_bound arm is red" is contradicted by the r101 record: the red conjunct is the **old-bound** arm's `marker_observed` | obs (recomputed; ver12 concurs) | §3 |
| 4 | r101 receipt citations of `run_battery.py:NNNN` are already stale vs HEAD (file changed mid-round); new citations must be `symbol@sha`, not bare line numbers | obs | §4 |
| 5 | S4's stale-path repair is line-neutral but 328/353 pairs rewrite **receipt JSONs** (execution history), not live instructions | obs | §5 |

## 1. HARD RED — r95 fold × `r101_ytrans_census` (measured)

Chain: `corpus/fixtures/r101_ytrans.gd:333-339` reads `res://r95b_order.gd` live and emits
`r95b_offy_tokens` / `r95b_lines` (`src.split("\n").size()`) / `r95b_sha256` (`sha256_text()`).
The landed CASES row `r101_ytrans_census` (`run_battery.py:1666`) pins the literal:

```
'PASS r101_ytrans census r95b_offy_tokens=0 r95b_lines=778 r95b_sha256=4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490 replacement_arm=ytrans'),
```

Counterfactual (scratch replica of the battery staging, minus `run_battery.py`):

```
$ (cd corpus/fixtures && tar --exclude='./run_battery.py' --exclude='./.*' -cf - .) | (cd /var/tmp/r102-crit4/base && tar -xf -)
$ cp corpus/fixtures/controls/pickup.tscn /var/tmp/r102-crit4/base/
$ cp -a /var/tmp/r102-crit4/base/. /var/tmp/r102-crit4/fold/
$ cd /var/tmp/r102-crit4/fold && patch -p3 -i <repo>/reports/round-101/mutations/r101-simp3-r95-fold.patch   # exit 0
$ godot --headless --path /var/tmp/r102-crit4/base --script res://r101_ytrans.gd -- --arm=census
$ godot --headless --path /var/tmp/r102-crit4/fold --script res://r101_ytrans.gd -- --arm=census
```

Observed (rc=0 both; each run ≈1.7 s total):

| tree | r95b_order.gd sha256[:16] | wc -l | fixture `r95b_lines` |
|---|---|---|---|
| base | `4f7e945e1b16f241` | 777 | **778** |
| fold | `b367559e831e5e9f` | 775 | **776** |

Classifier-shape check (battery semantics = `signature in output`, `run_battery.py:1775-1792`):

```
old pin  in base output : True
old pin  in fold output : False      ← row FAILs under the fold
new pin  in fold output : True       ← candidate re-pin
```

Full classifier preconditions also hold: rc=0 on both trees (row `expected_exit=0`) and
0 `ERROR:` / `SCRIPT ERROR:` / `Parse Error:` lines in both outputs (identical counts) —
the signature substring is the only gate that flips.

Required re-pin (same splice as the fold), full-line replacement at `run_battery.py:1666`:

```
'PASS r101_ytrans census r95b_offy_tokens=0 r95b_lines=776 r95b_sha256=b367559e831e5e9f9ab9e386591dd0035e24fb4e5ea2efc2c533e11aec2bdcf7 replacement_arm=ytrans'),
```

Arithmetic trap: the pin counts `split("\n").size()` (778 base → 776 fold), NOT `wc -l`
(777 → 775). The edit only touches `r95b_lines` / `r95b_sha256`; `r95b_offy_tokens=0` holds
in both trees (measured).

Corroboration: `r102-ver12.md:43-50` (independent find) and
`reports/round-102/mutations/r102-S3-verify.py:163` (includes this row in S3's target set).
SIMP-3's claim "No *live* gate reads a sha" (`r101-simp3.md:288`) is refuted by this row.
SIMP-3's own companion patch (`r101-simp3-r95-harness-comment.patch`) covers only comments
881-885, not row 1666. Also no other fixture reads a foreign fixture's bytes (verified:
`grep -n "get_file_as_string\|sha256" corpus/fixtures/*.gd` → only `r101_ytrans.gd` reads
`r95b_order.gd`; `export_prod*.gd` reads its own run logs; `r101_seqfull.gd` hashes its own
transcript). C1's new `export_launch.gd`/`export_launch_s02.gd` (untracked, created while this
seat ran; 429/460 lines) read only their own child logs — no cross-fixture coupling.

## 2. `run_battery.py` collision map (HEAD `bb8f79c9`, 5413 lines)

| region | current lines | C1 (launch rows) | C2 (timeout fix) | C3 (folds/comments) |
|---|---|---|---|---|
| CASES last non-crash rows (`export_prod_templates_missing_class`) | 1692-1693 | **insertion point: before 1694** | — | — |
| crash/descendant tail (`crash_spontaneous_sigabrt` … forged row) | 1694-1701 | shift target | — | — |
| `]` closing CASES / `def main()` | 1702 / 1705 | shift | — | — |
| `classify_process` | 1775-1792 | shift | — | — |
| `expected_errors` dict | 2021 (`= {`) – 2287 (`}.get`) | additions possible → 2nd shift segment | — | — |
| `required_stderr` dict | 2300-2324 | additions possible | — | — |
| r101 floor gate / `cases_integrity` | 4076 / 4094 | +`export_launch_` prefix (observed `w6_cases_integrity.patch`, hunk `@@ -4096,7 +4096,8 @@`) | — | — |
| `if args.probe_export_launch:` | 4510 | C1 evidence path | — | — |
| `if args.probe_timeout:` block | 5314-5400 (predicates 5375-5387) | — | **fix region** | — |
| comments citing fixture shas | 542, 799, 881-885, 1281-1282, 1406 | — | — | **re-pin targets (all <1694)** |
| `r101_ytrans_census` row | 1666 | — | — | **re-pin target (<1694)** |

Shift rule: a C1 insertion of Δ₁ lines before 1694 moves **every line ≥1694** by +Δ₁;
expected_errors additions (Δ₂, if any) move **every line ≥2287** by a further +Δ₂. C3's comment
targets and row 1666 sit above 1694 → insertion-invariant. C2's authoring region (5314-5400,
per `r102-w2.md:16`, `r102-mut4.md:16`, `r102-ver12.md:55`) is below → shifted by Δ₁(+Δ₂).
Δ₁ unknown until C1 publishes its row manifest (row-name material observed: `export_launch_positive`,
`export_launch_missing_startup_event`, `export_launch_mainpack_refusal`, `export_launch_s02…`).

## 3. C2 attribution correction + confinement demand

Recomputed from `corpus/live/runs/20261018T202131127599Z/timeout-verdicts.json` with the
driver predicates at 5375-5387 verbatim:

| clause | value | why |
|---|---|---|
| `old_rejects` | **False** | `slow_clean_old_bound`: `timed_out=T`, **`marker_observed=F`**, `inner_classification=F`, child dead=T |
| `new_accepts` | True | `slow_clean_new_bound`: exit 0, marker T, inner T |
| `hold_rejects` | True | all four conjuncts hold (`timed_out=T`, `marker=T`, `inner_classification=F`, child dead) |
| `meta_pass` | False | single failing conjunct = old arm's marker at 0.75 s |

So `hold_open_new_bound` is **green**; the red arm is the old bound (implied boot-to-script
0.794–0.846 s > 0.75 s; ver12 §3 same numbers). A fix that edits/holds only the hold arm
changes nothing. Fix region is the probe-timeout block; demand: diff confined to lines
5314-5400 (`if args.probe_timeout:`) and/or `timeout_probe.gd` (12 lines), no edits to
`run_process` (1748) / `classify_process` (1775) / `execute` (1892); record `run_battery.py`
sha before and after.

## 4. Citation census (what shifts, what is already stale)

Census command: `python3 reports/round-102/mutations/r102-crit4-cite-census.py .`
(at 17:43Z): r101 shards = **195 distinct `path:line` citations / 275 occurrences**;
`run_battery.py` is the most-cited file (63 distinct lines across two path spellings).
r102 shards (census-time) = 14 distinct. Selected integrity checks at HEAD:

| cited | cited by | content at that line now | class |
|---|---|---|---|
| `run_battery.py:1004` | r101-ver11, r101-scr3, r101-planner | `('r95b_order_twopiles', …)` (y1000 row retired in r101) | STALE/recycled |
| `run_battery.py:2011` | r101-adjudicator (dead dict entry) | `"same_line_suffix_classification": suffix_detected,` | STALE (target now 2061) |
| `run_battery.py:1543` | r101-E12/scr2/ver5/mut8 | `# no fixture folds; every boundary fold lands row-side here.` | STALE (sha comment now 1541) |
| `run_battery.py:1283/1284` | r101-simp1 follow-ups | `# + 1 r98-author cell…` / `#` | STALE (sha cites now 1281/1282) |
| `run_battery.py:1408` | r101-simp1 | `# probes/). It is deliberately NOT folded…` | VALID |
| `run_battery.py:542` | r101-simp1 | nav scout-sha comment | VALID |
| `run_battery.py:5375` | r102-crit2/w2/mut4 | `old_rejects = (…` | VALID |
| `run_battery.py:1666` | r102-ver12 | ytrans census row | VALID pre-fold, see §1 |

Precedent: r101's own file changed mid-round (r101-crit5 cited `c4db6153…`, HEAD is `bb8f79c9…`),
so receipts already cite transient bytes. Live harness line-number references (not receipts):
exactly one — `run_battery.py:2322` embeds `_nullts (res://tilemap_lattice.gd:927)` in an
`expected_errors` entries; `tilemap_lattice.gd` is NOT in any fold queue (r92 queue empty),
so no interference this round — but it is the class example ("do not fold tilemap_lattice").
Fixture-line citations in r101 receipts (r100b_seq.gd ×18, r95b_order.gd ×6, dss ×2,
canvas ×1, nav ×1, r98b_attack ×1, scene_io ×2, etc.) are frozen receipts; the only
declared consequence of folds is the GDScript backtrace-line shift (already measured by
SIMP-1/2/3; no live pin reads a fixture line number).

## 5. S4 stale-path repair — split and line-neutrality

`s4_cite_pairs.txt` (155 KB): **353 BEFORE/AFTER pairs; 0 AFTER lines left absolute**.

| class | pairs | route |
|---|---|---|
| `corpus/lessons/*.json` receipt files (r61/r58/… scratch + command records) | **328** | history rewrite — hold / operator policy (these record where runs actually ran) |
| `corpus/lessons/*.md` live instructions | 20 | apply as substitutions |
| `SCORECARD.md:8,9,10` | 3 | apply (orchestrator-serialized) |
| `PROVINCE.md:6,12` | 2 | apply; `:12` is also a **write-scope semantic change** ("Only writes `.shokunin/game-dev-2d/**`" → "this repository's tree") — route to operator |

Each pair is a single-line BEFORE/AFTER → line-neutral if applied per-line; acceptance check:
`git diff --numstat` shows added==deleted per file. mut06's 0-hit gate defaults to
`SCORECARD.md PROVINCE.md README.md` only — consistent with holding the JSON receipts.

## 6. Demands (ordering + re-pin)

1. **Same-splice re-pin**: if any r95 fold lands, edit `run_battery.py:1666` to the §1 string
   (values measured), plus comments 881-885 (SIMP-3 patch). If the fold is dropped, no edit.
   Acceptance receipt: the §1 census-arm command on the landed tree emits the new pin.
2. **r100 queue is unverifiable as-is**: `ls reports/round-101/mutations/ | grep -i r100b` →
   NONE. The r100 fold (`r100b_seq.gd` −5) has no patch and no per-hunk evidence; if landed,
   prove `r100b_seq_clean`/`_noclean` signatures byte-identical base/fold, update comment
   1646-1647/1541 (`4718a19e…`) in the same splice, else hold.
3. **Landing order for `run_battery.py`**: (a) C3 folds + comment/census re-pins, (b) C2
   probe-block fix, (c) C1 CASES insertion (+expected_errors, +cases_integrity) **last**.
   Reason: C1's splice is the only line-count-changing edit above C2's region; applying it last
   keeps C2/C3 authoring anchors valid. Every patch: `git apply --check` against the exact
   pre-image sha; re-check after each predecessor lands.
4. **Post-splice anchor map**: after C1 lands, publish symbol→line for CASES tail, dict close,
   gates, probe blocks, and record the new `run_battery.py` sha in the round record. No shard
   may cite pre-splice bare line numbers afterwards (§4 shows they rot within one round).
5. **C2 confinement** (§3): diff inside 5314-5400 only; sha before/after; standalone 3-arm
   rerun; counterfactual must reject a still-broken variant (mut4's inverse arm).
6. **Citation discipline**: new citations as `symbol@<sha>:<line>` or anchor text; bare `:NNN`
   only with the file sha.
7. **S4 application** (§5): apply the 23 markdown/scored pairs as line substitutions; hold the
   328 JSON receipt pairs; `git diff --numstat` added==deleted proof; PROVINCE:12 to operator.
8. **Temporal isolation**: C1's export receipts and C2/D stress seats (D2 interleaves ~20 rapid
   `godot` spawns; mut4 re-break runs) must not share measurement windows — r101-ver3.md:99
   measured 62.3 s cold for the s07 export under load vs the 60 s export bound. Record loadavg
   per receipt; warm-warm only (r101 law).

## 7. Limits / unknowns

- Did not run the battery (rule 1); acceptance is the orchestrator's full-battery run.
- Δ₁/Δ₂ exact values require C1's row manifest; the shift rule is segment-wise as stated.
- My scratch replica staged fixtures at 17:42Z; C1's `export_launch*.gd` files (untracked)
  appeared afterwards and do not affect this measurement.
- §4 staleness classes are content spot-checks at the cited lines, not a full re-derivation of
  every citation.
- The JSON-receipt history question is a policy call, not a defect I can settle.

## Receipts

- `reports/round-102/mutations/r102-crit4-cite-census.py` (this seat's census extractor).
- `/var/tmp/r102-crit4/`: `base/`, `fold/`, `census-base.out`, `census-fold.out`,
  `census-base.err`, `census-fold.err`, `cites.txt`, `s4files.txt`.
- Cross-checks: `r102-ver12.md` §2/§3, `r102-w3.md` §3 (fold sha table), `r102-S3-verify.py:163`,
  `reports/round-101/mutations/r101-simp3-r95-fold.patch`, `w6_cases_integrity.patch`.
