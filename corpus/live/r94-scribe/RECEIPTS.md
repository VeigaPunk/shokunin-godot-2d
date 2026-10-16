# r94-scribe receipts — custody + claim audit on committed `c7228893`

Seat `g2d-r94-scribe` | lane `game-dev-2d-shokunin` | host **devin** (32 cores,
loadavg 74–95 for the whole session; ~10 concurrent batteries from sibling lanes,
60–68 foreign `yes` hogs). Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`**
(`/usr/bin/godot`), `--headless`, default 60 tps.

Read-only audit of the r94 Particles2D landing: **no tracked file written, no
commit, no runtime config mutated.** Writes are `reports/round-94/r94-scribe.md`
(new) and `corpus/live/r94-scribe/**` only. Every number in the report was
recomputed from `git show HEAD:` bytes, on-disk receipts, or fresh launches on
the committed bytes.

## What is here

| artefact | path | notes |
|---|---|---|
| battery run 1 (worktree = committed bytes) | `battery-runs/<stamp>/verdicts.json`, `battery-rep1.log` | 314 rows; r94 19/19; gate true |
| battery run 2 (`git archive HEAD` extract) | `battery-committed/<stamp>/verdicts.json`, `battery-rep2.log` | 314 rows; r94 19/19; gate true |
| fresh single-arm receipts (19 arms × 3, default 60 tps) | `fresh/particles_lattice.<arm>.default.rep<N>.{out,err,rc}` | 57 receipts, rc=0, 0 B stderr |
| fresh fold-mode receipts (cpu_pause/lifetime/request × 3) | `fresh-ff30/…`, `fresh-ff60/…` | 18 receipts; ff30 cpu_pause `ok=true` (the fold) |
| static custody audit | `audit/static_audit.py` → `static_audit.json` | identity, CASES/rows, allowlists, gate, manifests, provenance, author runs |
| receipts census | `audit/receipts_census.py` → `receipts_census.json` | 1009 receipts collected; 634 own-arm checks; 631 hit / 3 miss; 0 collisions |
| law re-derivation | `audit/laws_recompute.py` → `laws.json` | ladder/expl/request/pause/contam/gpu values from raw receipts |
| landed-row mutants + dossier recompute | `audit/recompute.py` → `recompute.json` | 579/579 signature + 522/522 output mutants rejected |
| floor-gate loudness | `audit/floor_gate.py` → `floor_gate.json` | extracted gate expression: live→True, dead→False, non-r94 dead→True |
| classifier properties | `audit/classifier_properties.py` → `classifier_properties.json` | trailing-token 19/19, stderr-only 19/19, control 19/19 reject |
| cross-run comparison | `audit/compare_runs.py` → `compare_runs.json` | run1 vs run2 per-row classes |
| scout verifier re-run | `audit/scout_verify_rows.txt` | `ROWS_PREFIX rejected=[]` over 143; `ROWS` 30 rejections |
| fresh-arm driver | `audit/fresh_arms.py` | replay script |
| manifest | `manifest.sha256` | covers every artefact in this directory except itself |

## Replay

```sh
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
python3 corpus/live/r94-scribe/audit/static_audit.py
python3 corpus/live/r94-scribe/audit/fresh_arms.py
python3 corpus/fixtures/run_battery.py --godot godot --runs corpus/live/r94-scribe/battery-runs
git archive HEAD | tar -x -C /home/vgpnk/r94-committed-extract   # then
python3 /home/vgpnk/r94-committed-extract/corpus/fixtures/run_battery.py \
        --godot /usr/bin/godot --runs corpus/live/r94-scribe/battery-committed
python3 corpus/live/r94-scribe/audit/receipts_census.py
python3 corpus/live/r94-scribe/audit/laws_recompute.py
python3 corpus/live/r94-scribe/audit/recompute.py
python3 corpus/live/r94-scribe/audit/floor_gate.py
python3 corpus/live/r94-scribe/audit/classifier_properties.py
python3 corpus/live/r94-scribe/audit/compare_runs.py
```

The author's two green runs live at `corpus/live/runs/20261016T055703426158Z/`
and `corpus/live/runs/20261016T060430025246Z/` (worktree-only, untracked).

**Late-window note (foreign write).** At 03:41:30 a concurrent r95-author lane inserted
its block into the worktree `corpus/fixtures/run_battery.py` (+163 lines, 52 rows,
CASES 307 → 359). It is not this seat's write and was left untouched. Both scribe battery
runs used committed bytes (run 1 copied the fixtures before the foreign write; run 2 ran
from the `git archive HEAD` extract), and the 19 r94 tuples plus the r94 floor-gate
comprehension are byte-identical between `HEAD` and the dirty worktree — see
`audit/static_audit.json → foreign_worktree_modification`.
