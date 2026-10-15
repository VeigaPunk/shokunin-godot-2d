# r90-scribe receipts — wave-B custody + claim audit on committed `ee20575`

Seat `SCRIBE` (LEAF) | lane `g2d-r90-scribe` | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf`, Python 3.14.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`ee20575`** at audit time.

**No tracked file written, no commit, no runtime config mutated.** This
directory and `reports/round-90/r90-scribe.md` are the only new files
(untracked). All probe launches were `timeout -s KILL 25`-bounded; the battery
runs use the harness's own bounds.

## Layout

| artefact | role |
|---|---|
| `audit/manifest_completeness.py` → `.txt` | per-dir manifest entry set vs `os.walk` file set (scout/boundary/author) |
| `audit/scout_recompute.py` → `.txt` | independent 12-cell stability recompute from `r90-scout/runs/` |
| `audit/boundary_recompute.py` → `.txt` | receipt census, per-cell pass/rc uniqueness, md5 PASS-hash literals, sv-tier byte-identity, cross-seat scout equality, 30-tps pairing census |
| `audit/author_checks.py` → `.txt` | CASES/r90 inventory, emitted-vs-landed rows, 14-stamp verdict census, rep9 census/gate keys, fresh-arm reps, fold fields (env `R90_BATTERY` points it at the committed blob) |
| `audit/author_verify_arms_committed.txt` | `verify_arms.py` re-run against the **committed** battery (run from a `git archive ee20575` extract) |
| `audit/cross_dossier.txt` | 10/10 shared rows payload-identical to the scout rows (fold fields only) |
| `probe-tests/` | committed-probe runs resolving the `f_pair_30tps` provenance (see `SUMMARY.txt`) |
| `battery-runs/<stamp>/` | fresh **committed-tree** battery runs (247 rows each): rep1 `20261015T221426402427Z`, rep2b `20261015T222520528392Z` (fully green) |
| `battery-rep1.*`, `battery-rep2b.*` | battery driver output for the two committed runs |
| `noncommitted-rep2/` | a second-rep attempt that started **after** a concurrent lane's tracked edits; retained but **excluded** from committed-tree evidence |
| `battery-load-*.txt` | host load at run start/end |
| `manifest.sha256` | every artefact under this directory except itself |

## Commands (exact)

```bash
# custody
cd corpus/live/r90-scout    && sha256sum -c manifest.sha256
cd corpus/live/r90-boundary && sha256sum -c manifest.sha256
cd corpus/live/r90-author   && sha256sum -c manifest.sha256
python3 corpus/live/r90-scribe/audit/manifest_completeness.py corpus/live/r90-scout corpus/live/r90-boundary corpus/live/r90-author

# claim recomputes
python3 corpus/live/r90-scribe/audit/scout_recompute.py
python3 corpus/live/r90-scribe/audit/boundary_recompute.py
python3 corpus/live/r90-scribe/audit/author_checks.py
cd corpus/live/r90-scout  && python3 verify_rows.py
cd corpus/live/r90-author && python3 verify_arms.py
cd corpus/live/r90-author && python3 compare.py godot runs9/20261015T212551992799Z/verdicts.json rep12b=corpus/live/r90-author/runs12/20261015T220233737605Z/verdicts.json
cd corpus/live/r90-author && python3 compare.py godot runs4/20261015T203404756405Z/verdicts.json r89=corpus/live/r89-author/runs5/20261015T195521854184Z/verdicts.json

# committed-tree behavioural check (fresh battery under load)
python3 corpus/fixtures/run_battery.py --runs corpus/live/r90-scribe/battery-runs        # rep1
git archive ee20575 corpus/fixtures | tar -x -C /tmp/r90-committed                      # committed fixtures
python3 /tmp/r90-committed/corpus/fixtures/run_battery.py --runs corpus/live/r90-scribe/battery-runs  # rep2b (green)
# verify_arms against the committed battery:
mkdir -p /tmp/r90-committed/corpus/live/r90-author && cp corpus/live/r90-author/{verify_arms.py,author-rows.py.txt} /tmp/r90-committed/corpus/live/r90-author/
ln -sfn "$PWD/corpus/live/r90-author/runs" /tmp/r90-committed/corpus/live/r90-author/runs
python3 /tmp/r90-committed/corpus/live/r90-author/verify_arms.py
R90_BATTERY=/tmp/r90-committed/corpus/fixtures/run_battery.py python3 corpus/live/r90-scribe/audit/author_checks.py

# 30-tps provenance probe (committed probe; 60-tps and real-30-tps projects)
timeout -s KILL 25 godot --headless --path /tmp/r90-scribe-probe/proj60 --script res://rb_lattice.gd -- --arm=freezelock --frames=60
timeout -s KILL 25 godot --headless --physics-ticks-per-second 30 --path /tmp/r90-scribe-probe/proj60 --script res://rb_lattice.gd -- --arm=freezelock --frames=60
timeout -s KILL 25 godot --headless --path /tmp/r90-scribe-probe/proj30 --script res://rb_lattice.gd -- --arm=freezelock --frames=60
timeout -s KILL 25 godot --headless --path /tmp/r90-scribe-probe/proj30 --script res://rb_lattice.gd -- --arm=freezelock --frames=120
```

(`/tmp/r90-scribe-probe/proj60` = byte-copy of `corpus/live/r90-author/proj`;
`proj30` = same + `[physics] common/physics_ticks_per_second=30`.)

## Headline results

- manifests: **208/208 + 1143/1143 + 4015/4015 OK**, completeness exact.
- scout: 12/12 cells single-valued; `verify_rows.py` `rows=10 rejected=[]`.
- boundary: 281 receipts all rc=0; 82/82 cells single PASS; sv cells
  byte-identical across tiers; 9/9 cross-seat byte-equality; quoted hashes are
  md5(PASS+LF), 3/3 reproduced.
- author: 240 CASES / 247 rows; 12/12 fresh arms `sig_hit=6/6`; r90 12/12 in
  all 14 stamps after rep1; greens rep9 + rep12b; both `compare.py` runs
  reproduce the reported tuple results exactly.
- **fresh battery on committed bytes under load**: rep1 (`20261015T221426402427Z`,
  loaded the committed harness before a concurrent lane's tracked edit) 247 rows,
  r90 12/12, r90 gate true, fails = `transition`/`audio_bus_route*` + meta
  cascade; **rep2b (`20261015T222520528392Z`, from a `git archive ee20575`
  extract) 247/247 PASS**, r90 12/12, r90+r89 gates true,
  `census_bare_classifier_consistent=true`, `dead_entry_count=0`. A second-rep
  attempt that ran after the concurrent edits is kept under `noncommitted-rep2/`
  and excluded.
- **A1 (medium)**: `f_pair_30tps.rep{1,2}` are 60-tps `--frames=60` runs;
  `--physics-ticks-per-second` is not a Godot 4.7.2 option and is silently
  ignored; a real 30-tps project yields `tps=30`, `f_normal=-7.7000`,
  `f_lock=-156.0000` (pairing fields identical to 60 tps). The fold's
  conclusion still holds; no landed pin is affected.
