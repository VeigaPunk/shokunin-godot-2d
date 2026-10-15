# r87 verifier — named non-author verification of `ebcf2bb`

Seat `VERIFIER` (g2d lane r87, named non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf`, Python 3.14.7, 32-core. Target commit:
`ebcf2bbad6f0ee7ae02ac1c17babed2e0a8ee94e` (*r87: input event/action lattice —
20 verbatim arms + 4 mode-envelope cells + jpbe/ei_bound edge cells, 207/207 x2*).

## Method

```
git archive ebcf2bb | tar -x -C corpus/live/r87-verifier/tree
cd corpus/live/r87-verifier/tree
PYTHONDONTWRITEBYTECODE=1 timeout 900 python3 -B corpus/fixtures/run_battery.py \
    --runs $LIVE/corpus/live/r87-verifier/runs{1,2}   # serial, rep1 then rep2
```

Frozen-tree integrity: `diff -r` vs a second fresh `git archive ebcf2bb`
extraction = **IDENTICAL** (post-restore; see pyc note below). Harness
`run_battery.py` sha256 `325ab0206c8c5b22…` = committed blob, unchanged
pre/post both reps (`rep-timing.txt`). Fixture shas match author claims:
`input_lattice.gd 2b68531d…`, `r87_edge.gd 7cd80727…`, `ei_bound.gd 0493a257…`.

Compare tooling reused verbatim from `corpus/live/r87-baseline/`
(`tuples.py`, `compare.py`, `r87_compare.py` copied into my scratch); reference
receipt = baseline seat's rep1 `runs1/20261015T170136085777Z/verdicts.json`
(sha `56bfa601…`) and its frozen tuple set `freeze/godot-tuples-rep1.txt`.

## Results

| rep | rows | verdict | rc | wall | stderr |
|---|---|---|---|---|---|
| rep1 | 207 | **PASS** | 0 | 191.355 s | 0 B |
| rep2 | 207 | **PASS** | 0 | 210.004 s | 0 B |

Receipts: `runs1/20261015T173115194844Z/verdicts.json` (sha `d7a27969…`),
`runs2/20261015T173437720767Z/verdicts.json` (sha `ab13757c…`);
stdout/stderr + tuple sets + compares under `corpus/live/r87-verifier/`
(`freeze/receipt-shas.txt`).

### Claim verdicts

| # | claim | verdict | evidence |
|---|---|---|---|
| 1 | all 207 rows PASS, both reps | **AGREE** | `non-PASS=[]` both reps; 208-line stdout = 207 rows + `PASS battery:` trailer |
| 2 | 182 pre-r87 rows byte-identical to baseline rep1 tuples | **AGREE (as disclosed)** | `common=182 new_only=25 old_only=0`; **181/182** tuple lines byte-identical both reps; sole diff = `probe_error_clause_surface` meta census — the author's disclosed expected diff |
| 3 | envelope cells emit only whitelisted payloads | **AGREE** | 4 tuple-signature rows × 2 reps; each row's output matched exactly one whitelisted payload (indices below); zero out-of-whitelist payloads |
| 4 | author's "prior rows byte-identical" reproduces | **AGREE** | identical compare shape to author's: `tuple_mismatches=1 (seeded=0, meta=1)`; `output NORMALIZED differing=2` = `export_readiness`/`export_preset_missing` line 11 `(36 steps)` vs baseline `(33 steps)` (+3 landed `.gd` files) |

### Claim 2 detail — the one tuple diff is exactly the disclosed census

`probe_error_clause_surface` normalized stable-object diff isolates to key
`census` only (`arms` is in `META_ARM_RECORD_KEYS`, dropped by `norm_obj`):
- `census.rows` new-only entries: exactly `ei_bound_refusal`,
  `input_lattice_null_edge`, `r87_edge_jpbe` — the 3 new `expected_errors` rows;
  **0 changed pre-existing entries, 0 missing**.
- `rows_with_expected_errors` 52 vs 49 (+3); `scan_clause_census`
  `ERROR:_per_line_lines` 97 vs 88 (+9 = 4 null_edge + 1 jpbe + 4 ei_bound).

Counting command (either rep):
`python3 corpus/live/r87-verifier/r87_compare.py <mine-verdicts.json>
baseline-rep1=<r87-baseline rep1 verdicts>` → `tuple byte-identical=181/182`.
All **175/175 prior seeded rows** byte-identical; meta 6/7 identical with the
one diff disclosed above.

### Claim 3 detail — envelope whitelist audit

| row | rep1 hit | rep2 hit |
|---|---|---|
| `input_lattice_pre_frame` | payload[0] (`post_ph=[ph+0{…}]`) | payload[0] |
| `input_lattice_press_phys` | payload[1] (2-entry `post_ph`) | payload[1] |
| `input_lattice_release_edge` | payload[0] (`re=…/1/1` just-released variant) | payload[0] |
| `input_lattice_ui_ns` | payload[1] (`@ph+1` release receipts) | payload[1] |

Whitelisted ERROR lines: `input_lattice_null_edge` 4/4 declared,
`r87_edge_jpbe` 1/1, `ei_bound_refusal` 4 lines all matching the single
declared pattern — both reps. Global scan: one pre-existing undeclared ERROR
(`export_preset_missing`: `ERROR: Invalid export preset name`) — present
identically in the baseline receipt (row tuple byte-identical), not an r87
regression.

### Internal consistency

rep1 × rep2: `tuple byte-identical=207/207`, `output NORMALIZED
identical=200/207 differing=0` (7 meta rows carry no `output`). RAW diffs are
the declared-volatile set only (pids, runpaths, ASLR load address, tween
floats).

## Disclosures

- **HEAD moved during verification.** `live_head` was `adc2eaa8` pre-rep1 and
  `da41d543` pre-rep2 (r87 reviewer/critic seats committed on top). Irrelevant
  to the pin: the verified artifact is the `git archive ebcf2bb` frozen tree,
  proven byte-identical to a fresh extraction (`diff -r` IDENTICAL, harness
  sha pinned pre/post each rep).
- **pyc refresh (benign, restored).** My whitelist-extraction heredoc
  (`importlib exec_module`) rewrote the *committed, tracked* stale-mtime
  `tree/corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` during rep1.
  Python `-B` mains never read `__pycache__` and the battery executes sources
  only — zero behavioral surface. Restored to the committed blob
  (`13319b13…`); final `diff -r` vs fresh archive = IDENTICAL.
- **Residual risk (inherited, not a finding).** r87-critic F1 documents
  `input_lattice_api_press` as ~5% bimodal under load against a single-string
  pin; my 2 reps observed only the pinned payload (PASS both). The 4 envelope
  rows' whitelists cover observed modes only — an unobserved mode flakes loudly
  by design (author's own disclosed residual for `pre_frame` ≥2-tick window).

## Verdict

**AGREE 4/4.** Commit `ebcf2bb` reproduces: 207/207 PASS ×2 reps, 175/175 prior
seeded rows byte-identical to the baseline rep1 receipt, the sole meta census
diff disclosed and explained exactly, envelope cells whitelisted-clean.

Files (all untracked scratch under `corpus/live/r87-verifier/` + this report):
`tree/` (frozen `ebcf2bb`), `runs1/`, `runs2/`, `godot-battery-rep{1,2}.{stdout,stderr}`,
`freeze/{godot-tuples-rep1,godot-tuples-rep2,compare-rep1-vs-baseline,compare-rep2,envelope-audit-rep1,envelope-audit-rep2,receipt-shas}.txt`,
`envelope-whitelist.txt`, `env.txt`, `rep-timing.txt`, `freeze-head.txt`,
`{compare,tuples,r87_compare}.py` (verbatim copies from r87-baseline).
