# r90-verifier receipts index

Target: `ee205757c7302992013bfd13085c449ef2504355` (r90 author: 12 rb_lattice
rows, 247 total). Host devin, Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
load ~100–130 foreign throughout (sibling `r90c_hog` ×N, `bash while` loops,
r94-critic node) — no verifier-spawned hogs needed.

| artefact | path | note |
|---|---|---|
| frozen tree | `tree/` | `git archive ee20575`; fileset 99,503 / 0 diff; `git diff --quiet` rc=0 |
| fileset lists | `freeze/{ls-tree,extracted}.txt`, `fileset-diff.txt` (empty) | |
| fixture shas | `freeze/fixture-shas.txt` | rb_lattice `10da2291…`, rb_watch `e349faa0…`, run_battery `76c0b1f5…`, project `8de8b3af…` |
| AST pins | `pins.json` | 12 r90 case tuples literal-evaled from frozen run_battery.py |
| arm runner | `run_arms.sh` | battery launch shape, `timeout -s KILL 25` |
| arm receipts | `arms/<arm>.rep{1..4}.{out,err,rc}` | 12 arms ×4: 48/48 PASS byte-exact, rc=0, err_uniq=1 |
| arm summary | `arms/summary.json` | |
| Dummy vacuity | `arms/dummy_gravity.{out,err}` | `eng=PhysicsServer2DDummy ncb=0`; == author receipt |
| real 30 tps | `arms/t30_lag.out` | proj_tps30 override: `tps=30 step=0.033333 dy=32.6667` |
| no-op flag | `arms/t30_freezelock.out`, `arms/t30flag_lag.out`, `arms/bogus_lag.out` | `--physics-ticks-per-second 30` / `--bogus-flag-xyz` silently ignored — byte-identical to 60-tps pins |
| frames=60 control | `arms/f60_freezelock.out` | **byte-identical to author's `f_pair_30tps.rep{1,2}`** (mislabeled evidence — report F1) |
| concurrency | `arms_par/` | order/lag/damp ×8-way under load ~127: 1 unique payload each |
| own probe | `probes/v90_probe.gd`, `probes/v90_*.out` | census/rest/imp/damp/lag on own rigs |
| analytic | `probes/rederive.py` | 55/55 checks agree with pins |
| comparator | `compare.py` | verdict-tuple diff |
| battery rep1 | `battery/rep1.{stdout,stderr}` + `battery/runs1/20261015T221709358848Z/verdicts.json` | FAIL on non-r90 flake classes; r90 12/12 |
| battery rep2 | `battery/rep2.{stdout,stderr}` + `battery/runs2/20261015T222444014470Z/verdicts.json` | **PASS 247/247**, tuple+signature-identical to author green rep9 |
| launch projects | `proj/` (committed bytes), `proj_dummy/` (Dummy override), `proj_tps30/` (30-tps override) | |
| manifest | `manifest.sha256` | covers all files outside `tree/` |

Classifier: `classify_process` AST-extracted from frozen run_battery.py,
segment sha256 `749fa0607e77…` (same as author/scout claim).
