# r102-scout — Round 101 close-state verification

Plan (executed read-only; run_battery.py never executed — hard rule 1):
1. `git log --oneline -3` + worktree status; confirm HEAD 1392ca21 (r101 close).
2. Count CASES rows in run_battery.py via AST (parse only) — expect 528.
3. Confirm the 3 registered r101 fixtures exist; locate the moved orphan companions.
4. Re-run stale `.shokunin/game-dev-2d/corpus/` citation census with file:line list (feeds C3).
5. Cross-check close receipts + label observation/inference/unknown.

Host: `uptime` at 17:40:39 (=2026-10-18 17:40 local, -0300) → `load average: 7.13, 8.55, 9.21`.
All commands run from repo root; scratch helper scripts written to `/var/tmp/r102-scout-*.py`
(never /tmp, never the repo). No file created except this shard.

## 1. Close state

```
$ git log --oneline -3
1392ca21 round-101 record: LOG + SCORECARD verdicts (work ac4eb8d4)
ac4eb8d4 round-101: export_prod capability lattice (12 rows), r101_seqfull full-replay pins closing r100-critic F2, r101_ytrans --offy dead-flag repair (6 rows), retired r95b_order_celloff_y1000; folds F1 phase-invariant pins, F2 cases_integrity re-anchor, F3 legacy joys-token pins; 64-seat swarm 60/64 (opencode-go-7); receipts 540 PASS/7 FAIL run 2
05a72899 gitignore: stop re-tracking round-local freeze/scratch materializations
$ git rev-parse HEAD
1392ca21276e8beb007c5b96fa24758d166e6bc9
$ git status --porcelain
?? reports/round-102/          (this shard only; tree otherwise clean)
```

- OBSERVED: HEAD == 1392ca21 as briefed; branch main; worktree clean except my shard.
- OBSERVED: `run_battery.py` at HEAD: 5,413 lines / 527,798 bytes (`wc -lc`).

### CASES count (AST, module parsed never executed)
Command: `python3 /var/tmp/r102-scout-cases.py` (ast.parse of `corpus/fixtures/run_battery.py`).
- OBSERVED: `CASES` assign at **line 18**, `List` with **528** elements, all 528
  `Tuple`-shaped rows. Names: **528 unique, 0 duplicates**. `tuple_elts=528`.
- Composition: `r101_*` = **8** (2 `r101_seqfull_*` + 6 `r101_ytrans_*`), `export_prod_*`
  = **12**; `r95b*` = 34; retired `r95b_order_celloff_y1000` → absent (`False`).
- Identity check vs r101 claims: r101-scout counted 509 rows at 05a72899; adjudicator
  claims +20 rows −1 retirement → 509+20−1 = **528** ✓.
- OBSERVED row tail: `... export_prod_templates_missing_class, crash_spontaneous_sigabrt,
  crash_self_sigkill, descendant_pipe_detached_control, descendant_pipe_forged_signature_release`
  — r101 rows landed before the crash tail per the insertion convention.
- OBSERVED gate wiring: `cases_integrity` existence prefix tuple (line 4098-4099) now
  includes `r101_seqfull_`, `r101_ytrans_`, `export_prod_`; r101 floor gate
  `r101_expected_errors_all_matched` at lines 4076-4079; seqfull allowlist entries at 2281-2284.

## 2. Registered r101 fixtures + orphaned companions

`$ ls -la corpus/fixtures/ | grep -Ei "r101|export_prod"` →
- `export_prod.gd` 27,657 B, `r101_seqfull.gd` 37,677 B, `r101_ytrans.gd` 12,384 B.
- sha256 (OBSERVED):
  `872a9cf699b2cadf98b5201b3607e51dad754a15072b9d35ee22c8749a735f3e  export_prod.gd`
  `426075c8993b1a93ff9dd8e2cd6a14145644b64587bbc30c89d929a0f674273d  r101_seqfull.gd`
  `bbd769521278faedb1fc51f8375cedad4afb878058ce97e8254afc335b6f6334  r101_ytrans.gd`
- Byte identity with what the battery actually ran: sha256 of each file equals its copy in
  `corpus/live/runs/20261018T202131127599Z/scratch/` (all three `equal True`).
- Counts: `git ls-files corpus/fixtures` = 106; on-disk non-pycache files = 106; no untracked
  (`git status --porcelain corpus/fixtures` → empty). 103 pre-r101 + 3 = 106 ✓.

### Companion fixtures — moved, and safe
- OBSERVED: `reports/round-101/mutations/orphaned-fixtures/` holds **11 `.gd` + README.md = 12
  tracked files** (all added by ac4eb8d4; `git ls-files` count = 12).
- Composition per its README (`cat reports/round-101/mutations/orphaned-fixtures/README.md`):
  - **7 design-superseded** (seats E1/E2/E4/E7/E8/E10/E11): `export_prod_s01, s02, s04, s07,
    s08, s10, s11` — completed seats, but E0's landed 12-row `export_prod.gd` harness
    consolidates their scenarios.
  - **4 provider-orphaned** (seats E3/E5/E6/E9 died on provider 400): `export_prod_s03, s05,
    s06, s09`.
  - Briefing's "7 orphaned companions" = the 7 design-superseded subset; total retired = 11.
- Move is non-breaking (OBSERVED, AST): every one of the 20 r101-era CASES rows uses
  `script ∈ {export_prod.gd, r101_seqfull.gd, r101_ytrans.gd}`. `grep -n "export_prod_s"
  corpus/fixtures/run_battery.py` → sole hit is the case-name string
  `('export_prod_subdir_census'` at line 1672 — no `.gd` file reference. Nothing stages or
  loads the companions; their copies inside run-1/run-2 scratch dirs are historical staging
  snapshots (runs started 17:14/17:21 before the ~17:23 retirement), not live dependencies.

## 3. Close receipts (observed from disk; one routed discrepancy)

All in-tree `verdicts.json` dated 2026-10-18 (only these two today):
Command: python3 walk of `corpus/live/runs/*/verdicts.json` printing (rows, PASS, FAIL, verdict).

| run dir | mtime | rows | PASS | FAIL | payload |
|---|---|---|---|---|---|
| `20261018T200239625248Z` | 17:14:58 | 546 | 537 | 9 | FAIL |
| `20261018T202131127599Z` | 17:33:18 | 546 | 542 | 4 | FAIL |

- OBSERVED run-2 FAIL set: `input_lattice_census, input_lattice_dev_joy,
  input89_edges_axisdev, probe_timeout` (3 legacy joys-host rows + r62 timeout probe — exactly
  the two environmental findings r101 disclosed).
- OBSERVED run-1 FAIL set: that + `r101_ytrans_y1000, r101_ytrans_ym1000, r101_ytrans_ycop,
  probe_error_clause_surface, probe_export_launch`. Run1→run2 delta = 5 rows, matching the
  F1 fold (3 ytrans) + F2 cases_integrity re-anchor (error-clause meta) + export-launch probe.
- OBSERVED: all 20 r101-era rows PASS in run 2 (none in FAIL set). All 528 CASES names present
  in run-2 `results` (`missing_from_results: []`); the 18 non-CASES rows are `probe_*` ×14,
  `mutant_*` ×2, `probe_unrelated_error_mutant_*` ×2 (measured breakdown).
- OBSERVED: verdict values are only PASS/FAIL; 0 PASS rows carry an error field or an
  expected/actual exit mismatch in either run.
- **DISCREPANCY (routed, unexplained):** LOG.md:1225 and the ac4eb8d4/1392ca21 message claim
  "run 1 535 PASS/12 FAIL, run 2 540/7". No in-tree receipt supports 535/12 or 540/7: both
  on-disk runs have 546 rows (claims imply 547), and claimed FAIL counts exceed observed by
  exactly 3 in *both* runs (observed: 537/9 and 542/4; claimed: 535/12, 540/7). The claimed
  run1→run2 delta (−5 FAIL) matches observed. UNKNOWN: counting convention vs. external
  `--runs` root. Not a row-level defect — the failure *sets* on disk are consistent with the
  adjudicator prose. Recommend orchestrator reconcile LOG.md:1225 (calibration hygiene).
- Courtesy pin for C2: both runs' `timeout-verdicts.json` verdict=FAIL; arm triples are
  **normalized-equal across the two runs** (all fields except `command`/`raw_*`/`elapsed_seconds`
  compare equal per arm — `normalized_equal=True` for all 3). States: `slow_clean_old_bound`
  timed_out=True (expected at old bound), `slow_clean_new_bound` exit 0 marker true,
  `hold_open_new_bound` timed_out=True marker_observed=True in BOTH runs — confirms the routed
  red arm premise (deterministic, round-unrelated; C2 owns the diagnosis).

## 4. Stale `.shokunin/game-dev-2d/corpus/` citation census (C3 fuel)

Command: `grep -rn '\.shokunin/game-dev-2d/corpus/' --include='*.md' --include='*.py'
--include='*.gd' --include='*.json' .` (+ per-file `grep -c`/`grep -o`).

Exact file:line list — LIVE surface (all victims; fix targets):
- `SCORECARD.md:8`, `SCORECARD.md:9`, `SCORECARD.md:10` — 3 occurrences, one per axis row
  (`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py ...`). Correct form in this
  repo: `python corpus/fixtures/run_battery.py ...`. Mechanical line-pair repair ×3:
  replace `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py` →
  `python corpus/fixtures/run_battery.py` (nothing else on the lines changes).
  SCORECARD.md is orchestrator-serialized (hard rule 2) — C3 supplies the line-pairs.
- `PROVINCE.md:6` — 1 occurrence, false present-tense claim:
  `- corpus fixtures under .shokunin/game-dev-2d/corpus/ (seeded from games-engine-mechanics r15, provenance in seed.md)`.
  Correction needs one word of judgment: `under corpus/`. PROVINCE.md is not in rule-2's list
  but is a lane doc — orchestrator decision.
- `README.md`: 0. `SHONEN.md`: 0. `corpus/README.md`: 0. `corpus/knowledge/`: 0.
  `corpus/fixtures/` (all types): 0. (re-verified today; matches r101-scout)

Historical surfaces (flag only — policy call, not silent rewrite):
- `LOG.md`: **44 matching lines / 46 occurrences**; lines:
  11,12,23,34,42,51,69,79,89,99,109,118,185,198,199,203,213,232,238,242,254,264,274,285,296,
  305,314,323,332,343,352,361,370,379,388,397,406,415,424,433,555,563,570,1250.
  Of the 46, 36 are `.../corpus/fixtures/run_battery` command citations (same class as
  SCORECARD); LOG also carries ~50 `.shokunin/game-dev-2d/reports/...` stale-root siblings.
  Append-only history — recommend a one-line forward correction, not edits.
- `corpus/lessons/`: **100 files / 736 occurrences** (82 `.json`, 18 `.md`). Per-file counts
  (top + representative): r59-audio-non-author.json 98, r58-process-non-author.json 96,
  r61-crash-non-author.json 88, r25-export-pair-verifier.json 13, r25-direct-target-pair.json 12,
  r58-process-evidence-non-author.json 10, r57-save-non-author.json 8,
  r25-export-launch-verifier2.json 8, r25-export-launch-adverse.json 8, r11-launch-regression.json 8,
  r10-launch-verifier.json 8, r56-pushframe-non-author.json 7, r55-frame-non-author.json 7,
  r54-order-non-author.json 7, r53-composite-non-author.json 7 … (remaining ~85 files carry 1-7
  each; full list reproducible with the command above). Many are inside JSON receipt payloads
  (historical scratch/seed paths), not prose.
- `reports/`: 287 files / 812 occurrences (round history; out of repair scope).

Observation vs inference: counts and line lists = OBSERVED (commands above). "Mechanical" repair
of the SCORECARD lines = OBSERVED shape (command token differs only by path prefix; no
interpolation); no fix applied by this seat (rule 2).

## 5. Routed / notes for the orchestrator

1. LOG.md:1225 receipt counts vs on-disk receipts (see §3) — reconcile or annotate.
2. C3 scope: live victims are exactly SCORECARD.md:8-10 (+ PROVINCE.md:6 decision); the 736
   lessons + 46 LOG occurrences are historical receipts needing a policy call.
3. r101 companions: 11 retired (not 7); all unreferenced by CASES; register only with fresh
   pins per the orphaned-fixtures README.
4. Nothing r101-leftover in `corpus/fixtures/` beyond the 3 registered files; no untracked
   fixture drift at r101-close census time (17:47).
5. Timed addendum: at 17:49 `git status --porcelain` shows NEW untracked
   `corpus/fixtures/export_launch.gd` + `corpus/fixtures/export_launch_s02.gd` — sibling C1
   seat artifacts (expected per rule 3), not scout-created and not r101 leftovers; orchestrator
   accounts for them at integration.

(All measurements 2026-10-18 ~17:40-17:49 local unless labeled otherwise; `run_battery.py`
was never executed by this seat — AST parse only.)
