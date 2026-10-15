# r89-verify receipts index

All artifacts untracked, produced by the r89 verifier seat against frozen
`8cea888` bytes. Host: devin (32-core, load ~75–150 during the window —
~48–80 foreign `yes`/`blender`/sibling-battery processes plus this seat's
16 `yes` hogs, all since killed).

| path | contents |
|---|---|
| `tree/` | `git archive 8cea888` extraction — 99,186-path fileset, 0 diffs vs `git ls-tree`; `git diff --quiet` rc=0 |
| `freeze/fileset-diff.txt` | 0 lines (empty = identical fileset incl. symlinks) |
| `freeze/fixture-shas.txt` | `geo2d_lattice.gd 9784716b…`, `input89_edges.gd 601c223e…`, `run_battery.py e49b488d…`, `project.godot 8de8b3af…` |
| `freeze/ast-census.txt` | AST census of frozen CASES: 228 tuples, 20 r89 rows, exact=2-tuple envelope, lineempty exit=-6, tail order, r89 gate |
| `battery/runs{1,2,3}/<stamp>/verdicts.json` | three full-battery verdicts under load (235 rows each; all 20 r89 rows PASS in all three) |
| `battery/rep{1,2,3}.{stdout,stderr}` | battery console logs |
| `arms/lineempty.rep{1,2,3}.{out,err,rc}` | standalone crash row: rc=134, signature line on stdout before abort, Clipper2 assert on stderr |
| `arms/exact_load*` `exact_quiet*` `exact_jitter` `exact_hunt*` `exact_burst` `exact_pin` `exact_scope*` | 1,750 standalone `input89_edges_exact` reps — Q×4 (rep15/23/36/94 of `exact_scope2`), L×1,746, other×0, nopass×0; every PASS line byte-matches a committed envelope payload |
| `arms/axisdev_load/rep{1..6}.*` | 6/6 byte-exact vs committed `input89_edges_axisdev` pin under load |
| `arms/geo_load/*_rep{1,2}.*` | bridge/ring/ring4/ringhits/joins/ops/census/pipedges ×2 under load — 16/16 byte-exact vs committed pins |
| `probes/v89_probe.gd` | verifier-written independent probe (own arms incl. non-pinned cross-check cells) |
| `probes/rederive.py` + `probes/rederive-out.txt` | 23 independent re-derivations, 23/23 PASS |
| `proj/`, `proj-crash/` | scratch launch projects (frozen `project.godot` copy + probe scripts) |
| `hog.pids` | the seat's 16 `yes` hog pids (all killed, verified 0 alive) |
| `env.txt` | host/build/window record |
