# r91 verifier — receipts index

Seat `VERIFIER` (g2d lane r91), independent non-author, gate on committed
**`77d2f7e`** (`r91 author: 11 nav_lattice rows (258 total) …`). Host **devin**,
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot --headless`,
GodotPhysics2D, 60 tps), Python 3.14.7, 32 cores.

**No tracked write, no commit.** Every artefact below lives under
`corpus/live/r91-verifier/` (untracked) except the report
`reports/round-91/r91-verifier.md` (new, untracked at write time).

**Frozen probeParent.** Exactly one read-only `ufo-labrat` (agent `57f3a492`)
was dispatched with one bounded static hypothesis; it had no exec tool and
returned a static read (clause A FALSIFIED by three substring counterexamples —
`n_a`/`pre_iter`/`settled` — all resolved as bare-token false positives under
delimiter-aware re-check; clauses B/C/D CONSISTENT). No second dispatch.
**`lsp` disclosure:** no `lsp` device and no GDScript server is exposed to this
seat; every semantic check is an AST/static read of the committed bytes plus
fresh-process execution — the recorded fallback.

## Layout

| artefact | path | notes |
|---|---|---|
| frozen extraction of `77d2f7e` | `tree/` | 1.8 G, 100,530 entries; excluded from the manifest (prunable) |
| freeze evidence | `freeze/` | `fileset-diff.txt` (0 lines), `content-diff.err` (0 bytes, rc=0), `fixture-shas.txt`, `scout-to-committed.diff` (532 lines) |
| battery runs (5) | `runs/2026*/verdicts.json` | rep1–rep3 loaded, rep4, rep5 **green 258/258**; `rep{1..5}.{log,load}` |
| fresh-arm receipts (11 arms × 3) | `arms/*.rep*.{out,err,rc}` | battery launch shape, `timeout -s KILL 15` + Python bound |
| fresh-arm summary | `arms/fresh-arms.txt`, `arms/fresh-arms-check.txt` | 33/33 clean under the production stderr rule |
| verifier-owned probe (39 runs) | `arms/probe/*.{out,err,rc}` | `v91_probe.gd` — agent-order artifact, gate law, maxrad ladder, 5 ORCA-bound rigs, 4 teardown cells |
| fixed-fps stall cells (44 runs) | `arms/fixedfps/ff{30,120}.*` | committed fixture under `--fixed-fps`; STALE + exit 2 cells |
| launch project + probe | `arms/proj/` | copy of the frozen `corpus/fixtures/` + `v91_probe.gd` |
| audit script + output | `probes/audit_committed.py` → `probes/audit-committed.txt` | AST census, field-form leak check, tail print-site ordering |
| re-derivations | `probes/rederive.py` → `probes/rederive.txt` | 43/43 closed-form checks |
| custody check | `probes/custody_check.py` → `probes/custody-check.txt` | committed fresh-reps + author runs vs mine |
| tail-variance table | `probes/tail_variance.py` → `probes/tail-variance.txt` | pins constant / tails varying across 8 observations per row |
| production-classifier discrimination | `probes/classify_discriminate.py` → `probes/classify-discriminate.txt` | AST-extracted `classify_process`/`classify_streams` |
| receipt re-checker | `probes/check_arms.py` | fresh-arm receipts vs the production stderr rule |
| scratch | `tmp/` | `lstree-v.txt`, `extracted-v.txt`, `sort/` |

## Reproduction

```bash
# freeze
git ls-tree -r --name-only 77d2f7e | wc -l                      # 100530
GIT_DIR=$PWD/.git GIT_WORK_TREE=$PWD/corpus/live/r91-verifier/tree \
  git diff --quiet 77d2f7e                                      # rc=0
# battery (from the frozen tree)
python3 corpus/live/r91-verifier/tree/corpus/fixtures/run_battery.py \
        --runs corpus/live/r91-verifier/runs
# fresh arms / probe / stall cells
python3 corpus/live/r91-verifier/probes/fresh_arms.py 3
cd corpus/live/r91-verifier/arms/proj && \
  timeout -s KILL 20 godot --headless --path . --script res://v91_probe.gd -- --arm=agent_order
  timeout -s KILL 25 godot --headless --path . --fixed-fps 30 \
    --script res://nav_lattice.gd -- --arm=bake
```

## Key raw cells

- `runs/20261016T000657222526Z/verdicts.json` — the green rep (258/258; tuple-identical to both
  committed-worktree author runs).
- `arms/fixedfps/ff30.bake.rep1.out` — `STALE nav_lattice bake sync_bound_exhausted bound=48`
  (rc=2, no PASS line).
- `arms/probe/agent_order.rep1.out` — `r1=false fin=true r2=true` (query-order artifact).
- `arms/probe/avoid_bound_gap30.rep1.out` / `avoid_bound_tau2.rep1.out` — the ORCA-bound
  discrimination (`gap/τ`, not `(r_a+r_b)/τ`).
- `arms/teardown_crash.rep1.err` — `double free or corruption (!prev)` with rc=-6.
