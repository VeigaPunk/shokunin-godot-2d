# r92-critic receipts — replay and inventory

Seat `CRITIC`, round 92, commit reviewed **`5900431`** (parent `045d925`).
All artefacts below are seat-owned; nothing tracked was written and nothing was committed.
Manifest: `manifest.sha256` (covers every file under this lane directory).

## Replay

```bash
cd ~/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r92-critic
ulimit -c 0                                   # the crash row must not write cores

# 0. frozen committed tree (already extracted here)
git -C ../.. archive 5900431 -- corpus/fixtures | tar -x -C frozen
sha256sum -c manifest.sha256                  # 2470/2470

# 1. static audit: commit shape, CASES/census tables, envelope diff, gate wiring
python3 scripts/audit.py                      # -> audit.json

# 2. fresh 14 arms x3 (battery launch shape) + production classifier
python3 scripts/probe.py run  --proj proj --outdir runs --tag fresh \
  --arms census,atlas,cells,custom,terrain,pattern,encoding,fixinvalid,srcids,physics,timing,quadrant,nav,nullts --reps 3
python3 scripts/probe.py classify --dir runs --tag fresh

# 3. envelope reachability: nav at --fixed-fps 120 / 150 / 240 / 600
for ff in 120 150 240 600; do
  python3 scripts/probe.py run --proj proj --outdir runs --tag ff$ff --arms nav --reps 3 --fixed-fps $ff
  python3 scripts/probe.py classify --dir runs --tag ff$ff
done

# 4. load batch (+16 seat hogs, killed by trap)
bash scripts/load_batch.sh                    # -> runs/load.log

# 5. mutants (12 fixture mutants, each in its own scratch project + harness mutants)
python3 scripts/mutants.py                    # -> mutants.json, mutants/receipts/

# 6. crash-row wall time + phase split
bash scripts/wall_batch.sh                    # -> runs/wall_batch.log
python3 scripts/phase_probe.py 5              # -> runs/phase_nullts.log

# 7. full batteries on the frozen committed tree (rep1, rep2)
python3 frozen/corpus/fixtures/run_battery.py --runs battery-runs

# 8. mutant-fixture battery (floor-gate mechanism removal + crash-site line shift)
python3 frozen-mut/corpus/fixtures/run_battery.py --runs battery-mut-runs
```

## Inventory

| path | content |
|---|---|
| `frozen/` | committed tree, `git archive 5900431 -- corpus/fixtures` |
| `frozen-mut/` | same tree with the atlas duplicate-`create_tile` poke removed (one line) |
| `proj/` | scratch project used for every arm launch (fixture sha `a699138945ec7c1c…`) |
| `runs/` | fresh 42, regime 12, load 28, qnull 10, wall 16, phase 5 receipts + rc sidecars, `props.out` |
| `audit.json` | commit shape, CASES tables, envelope token diff, census, gate expression |
| `mutants.json` | 12 fixture mutants + 9 harness mutants with expectations and observations |
| `mutants/` | mutant projects + receipts |
| `battery-runs/<stamp>/` | seat battery rep1 / rep2 (272 rows each) |
| `battery-mut-runs/<stamp>/` | mutant-fixture battery (272 rows) |
| `battery-rep1.log`, `battery-rep2.log`, `battery-mut.log` | battery stdout + loadavg + wall time |
| `runs/load.log`, `runs/wall_batch.log`, `runs/phase_nullts.log` | load accounting, crash-row wall times, phase split |
| `probes/props.gd` | engine instrument for the `layer_props=n16[…]` census token |

## Headline numbers

- 126 seat Godot launches (incl. the `props.gd` instrument); 3 full 272-row batteries.
- fresh 42/42 PASS · regime 12/12 PASS · load 28/28 PASS (loadavg 64.6 → 72.6).
- battery rep1: 272 rows, 4 FAIL — all documented volatile classes (audio, spontaneous-crash
  timeout) + their meta knock-ons; **r92 14/14 PASS**, gate True.
- battery rep2: 272 rows, 3 FAIL — `negative_transition`, **`r92_tilemap_nullts_crash`
  TIMEOUT after 8 s** (host contention, see report F1), meta knock-on.
- mutant battery: gate `r92_expected_errors_all_matched` **False** (1 dead entry, atlas row
  still PASS); the same run incidentally shows the crash-site token is line-bound (`:926`).
- nullts wall: 1.07–1.21 s nominal (startup 0.45 / crash path 0.47 / post-dump 0.05);
  2.16–11.65 s under sibling-lane contention (3/18 over the battery's 8 s bound).
