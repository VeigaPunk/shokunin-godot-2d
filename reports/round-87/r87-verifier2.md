# r87 verifier-2 — re-verification of the FOLDED tree `7ef247c`

Seat `VERIFIER-r2` (g2d lane r87, named non-author, post-fold) | host **devin** |
Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python 3.14.7, Linux 7.2.3-arch1-3,
32-core. Target commit: `7ef247c34584657d57ade0df22a8eb6a6134c637` (*r87 fold:
critic F1 api_press→2-payload envelope; F3 floor-gate extended to r87 whitelist
cases; simplifier SP1-7 dead-code removal*). HEAD did not move during this
verification — the frozen tree is the live commit.

## Method

```
git archive HEAD | tar -x -C corpus/live/r87-verifier2/tree   # freeze-head.txt
cd corpus/live/r87-verifier2/tree
PYTHONDONTWRITEBYTECODE=1 timeout 900 python3 -B corpus/fixtures/run_battery.py \
    --runs $REPO/corpus/live/r87-verifier2/runs1
```

Frozen-tree integrity: every fixture blob sha256 == `git show HEAD:` blob
(`env-shas.txt`): `run_battery.py 69512316…` (fold's new blob; was
`325ab020…` at ebcf2bb — unchanged pre/post rep), `input_lattice.gd
7624aa97…` (the simplifier's claimed post-SP1-7 sha — confirmed),
`r87_edge.gd 7cd80727…`, `ei_bound.gd 0493a257…` (unchanged since ebcf2bb).

Compare tooling reused verbatim from `corpus/live/r87-verifier/`
(`compare.py`, `tuples.py`, `r87_compare.py` copied into my lane); reference
receipt = verifier-1's own runs1 verdicts on ebcf2bb
(`corpus/live/r87-verifier/runs1/20261015T173115194844Z/verdicts.json`, sha
`d7a27969…` — matches that seat's `receipt-shas.txt`).

## Results

| rep | rows | verdict | rc | wall | stderr |
|---|---|---|---|---|---|
| rep1 | 207 | **PASS** | 0 | ≈174.3 s | 0 B |

Receipts: `runs1/20261015T174757647842Z/verdicts.json` (sha `be5b0222…`),
stdout `f3df55f7…`, stderr empty (`e3b0c442…`); `freeze/receipt-shas.txt`.

### Per-claim verdicts

| # | claim | verdict | evidence |
|---|---|---|---|
| 1 | `run_battery.py` parses | **PASS** | `ast.parse` OK on the frozen copy (sha `69512316…` = HEAD blob) |
| 2 | one full rep = 207/207 PASS, all meta gates PASS incl. `r87_expected_errors_all_matched` | **PASS** | `non-PASS=[]`; `PASS battery:` trailer (208 lines = 207 rows + trailer); `probe_error_clause_surface` verdict=PASS, 36/36 discriminations true, **`r87_expected_errors_all_matched: true`**, `phys2d_expected_errors_all_matched: true`; census `rows_with_expected_errors=52`, `dead_entry_count=0`; the 3 r87 whitelist rows censused: `input_lattice_null_edge` 4/4 entries matched, `r87_edge_jpbe` 1/1, `ei_bound_refusal` 1/1 (4 lines) |
| 3 | api_press envelope admits both modes, neither FAILs | **PASS** | 24 fresh-process reps under 16 CPU hogs, battery launch shape (`run_apipress.py`, receipt `apipress-load16.json`): payload[0] (`ph1{ap=1/0.70/1/1}`) ×2, payload[1] (`ph1{ap=1/0.70/1/0}`) ×22, neither 0; **both modes observed**; all 24 rc=0, zero `ERROR:`/`SCRIPT ERROR:`/`Parse Error:` lines, production-rule PASS 24/24. Alt rate 22/24 corroborates critic F1's 27/30 under load |
| 4 | prior rows byte-identical vs verifier-1 runs1 | **PASS (as disclosed)** | `common=207 new_only=0 old_only=0`; **tuple byte-identical 205/207** — the only 2 mismatches are exactly the fold: `input_lattice_api_press` (`signature` str→2-payload tuple) and `probe_error_clause_surface` (`discriminations` +1 key = the new gate; other differing fields are declared-volatile `arms`/`seam_split_run`/`command`). No other tuple drift |
| 5 | simplifier deletions didn't change probe output | **PASS** | all 25 r87-prefix rows (`input_lattice_*`, `r87_edge_jpbe`, `ei_bound_refusal`) verdict=PASS against unchanged pinned signatures; `input_lattice.gd` sha = `7624aa97…` as claimed |

### Envelope whitelist audit (in-battery rep1)

| row | rep1 hit |
|---|---|
| `input_lattice_api_press` | payload[0] (pin `ph1 …/1/1`) |
| `input_lattice_pre_frame` | payload[1] (`post_ph=[]` alt) |
| `input_lattice_press_phys` | payload[0] (3-entry `post_ph`) |
| `input_lattice_release_edge` | payload[1] (alt) |
| `input_lattice_ui_ns` | payload[0] |

Zero out-of-whitelist PASS lines in any envelope row. Normalized-output diff
vs verifier-1 rep1 = exactly these 4 pre-existing envelope rows landing the
complementary mode (v1: `[0],[1],[0],[1]` for the same four) — whitelisted
bimodality, not drift. The rep1 battery row for `api_press` hit payload[0];
the alt mode is proven PASS-admissible by the focused load batch (22/24).

### Remaining diffs are the declared-volatile set only

Raw (unnormalized) output diffs vs verifier-1 rep1 = 13 rows: pids
(`descendant_pipe_*` ×2, `save_process_*` ×3), runpaths (`save_roundtrip`),
ASLR `Load address` (`crash_spontaneous_sigabrt`), tween floats
(`tween_flash`), the 4 envelope-mode rows above, and **one new raw diff**:
`input_lattice_null_edge` backtrace token `res://input_lattice.gd:760` →
`:743` — the expected consequence of the 21-line SP1-7 removal. That token
class (`\.gd:\d+`) is declared-unpinned in the compare rules and normalizes
equal (`.<N>`); the whitelisted `ERROR:` lines themselves are unchanged and
all 4 entries still match in-run (census `dead=0`). Not a defect.

## Disclosures

- **HEAD did not move** during verification (still `7ef247c` post-run); the
  frozen tree and the live commit are one artifact.
- **Focused reps ran concurrently with the in-flight battery** (16 CPU hogs
  during the battery's mid-run). This is doubly useful: it exercised the
  folded envelope under exactly the conditions that falsified the old pin,
  and the battery still went 207/207. The in-battery `api_press` happened to
  land pin-mode; had it landed alt-mode the envelope would still PASS it —
  as demonstrated 22× out-of-band.
- One rep, per assignment (verifier-1's two-rep precedent on ebcf2bb stands;
  this seat verifies the fold delta). A second rep was judged unnecessary:
  the only changed rows are deterministic or envelope-covered.

## Verdict

**VERIFIED.** The `7ef247c` fold is correct: `ast.parse` clean; 207/207 PASS
in a full rep with every meta gate true including the new
`r87_expected_errors_all_matched` (dead-entry floor now covers the r87
whitelist cases); the `api_press` 2-payload envelope admits both observed
modes — alt-mode dominant under load (22/24), zero FAILs; all prior rows
byte-identical to verifier-1's ebcf2bb receipt modulo exactly the two
disclosed deltas (api_press signature shape, surface discriminations +1
key); simplifier SP1-7 leaves all 25 r87 rows PASS (sha `7624aa97…`
confirmed, sole raw delta a declared-unpinned `.gd:N` token).

Files (all untracked under `corpus/live/r87-verifier2/` + this report):
`tree/` (frozen `7ef247c`), `runs1/20261015T174757647842Z/`,
`godot-battery-rep1.{stdout,stderr}`, `proj/` (scratch fixture copy),
`run_apipress.py`, `apipress-load16.json`, `xdg-data/`,
`freeze/{godot-tuples-rep1,compare-rep1-vs-verifier1,receipt-shas}.txt`,
`env-shas.txt`, `env.txt`, `rep-timing.txt`, `freeze-head.txt`,
`{compare,tuples,r87_compare}.py` (verbatim copies from r87-verifier).
