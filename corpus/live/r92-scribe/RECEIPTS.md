# r92-scribe receipts — wave-B gate on committed `5900431` (TileMapLayer lattice)

Seat `SCRIBE` (LEAF, frozen `probeParent`) | lane `g2d-r92-scribe` | round 92 | host **devin**
(`plazir27`, 32 cores, loadavg 59–65 throughout, 48 foreign `yes` hogs, ppid 1537).

**Zero tracked writes.** `git status --porcelain -uno` was empty at audit start
(2026-10-16T00:15:46Z) and empty at every re-check (last: after both battery runs). The only
files this seat created are this lane's receipts (untracked) and the untracked report
`reports/round-92/r92-scribe.md`. No commit, no push, no runtime config touched.

## Run inventory

| artefact | stamp / path | what it is |
|---|---|---|
| battery run 1 (worktree = committed bytes) | `battery-runs/20261016T001546769898Z/` | 272 rows, **verdict PASS 272/272**, log `battery-rep1.log` |
| battery run 2 (`git archive HEAD` extract) | `battery-committed/20261016T001825616636Z/` | 272 rows, verdict FAIL (271/272: `overlap`), log `battery-rep2b.log` |
| fresh single-arm receipts | `fresh/{nav,nullts,encoding,census}.rep1.{out,err,rc}` | battery launch shape, Python subprocess (rc=-6 for nullts) |
| `--fixed-fps` envelope probe (landed fixture) | `fixedfps/nav_{default,ff120,ff150,ff180,ff600}.{out,err,rc}` | payload[0] at ratio ≤ 2, payload[1] at ≥ 2.5 |
| launch projects (untracked scratch) | `fresh-proj/`, `fixedfps-proj/` | byte-copies of `corpus/fixtures/` used by the two probes above |

## Audit scripts (all re-derive from HEAD's harness + on-disk receipts)

| script | output | what it proves |
|---|---|---|
| `audit/static_folds.py` | `audit/static_folds.json` | landing identity, CASES 265/14 rows, expected_errors 9 cases/18 lines, required_stderr pair, gate key, manifest completeness, tombstone decode |
| `audit/nav_envelope.py` | `audit/nav_envelope.json` | 144 committed nav receipts → payload0/payload1/neither, field single-valuedness |
| `audit/forge_nullts.py` | `audit/forge_nullts.json` | nullts row binding: 9 single-half mutations × 10 receipts + 2 cross-receipt foreign crashes |
| `audit/forge_rows_landed.py` | `audit/forge_rows_landed.json` | signature-forge re-run on the landed rows (396 mutants, 0 accepted) |
| `audit/recompute_claims.py` | `audit/recompute_claims.json` | author runs1–5, author fresh-reps ×42, boundary 416-receipt matrix (envelope vs payload0-only), scout 51 canonical |
| `audit/fixedfps_probe.py` | `audit/fixedfps_probe.json` | payload[1] reachability from the **landed** fixture |
| `audit/compare_runs.py` | `audit/compare_runs.json` | row-by-row rep1 vs rep2b (217 identical / 11 tail-only / 0 pin-diff / 44 no-pinned-line) |
| `audit/summarize_runs.py` | `audit/run_summary.json` | per-run verdict, gate, census, the 14 emitted r92 lines |
| `audit/run_fresh.py` | `fresh/` | the single-arm launcher (battery launch shape) |

## Replay

```bash
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin        # HEAD 5900431, clean tracked tree
python3 corpus/live/r92-scribe/audit/static_folds.py
python3 corpus/live/r92-scribe/audit/nav_envelope.py
python3 corpus/live/r92-scribe/audit/forge_nullts.py
python3 corpus/live/r92-scribe/audit/recompute_claims.py
python3 corpus/live/r92-scribe/audit/fixedfps_probe.py        # launches godot (5 runs)
python3 corpus/live/r92-scribe/audit/compare_runs.py
# battery runs (≈25 min each under load):
python3 corpus/fixtures/run_battery.py --runs corpus/live/r92-scribe/battery-runs
mkdir -p /home/vgpnk/r92-committed-extract && git archive HEAD | tar -x -C /home/vgpnk/r92-committed-extract
cd /home/vgpnk/r92-committed-extract && python3 corpus/fixtures/run_battery.py \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r92-scribe/battery-committed
```

## Headline numbers

| claim | recomputed |
|---|---|
| landing files worktree == `HEAD` | `tilemap_lattice.gd a6991389…`, `run_battery.py 5e518281…`, `project.godot 8de8b3af…` — all SAME |
| fixture is a byte-copy of the scout probe | `a6991389…` == `r92-scout/probes/tilemap_lattice.gd` == `r92-boundary/probes/scout_tilemap_lattice.gd`, 929 lines |
| manifests | scout **295/295**, boundary **2471/2471**, author **1510/1510** OK; each covers every file in its dir except itself |
| CASES | 265 = 251 + 14, contiguous after `nav_lattice_teardown_clean` (idx 246), crash/descendant tail intact |
| rows | 272 = 258 + 14 in all 7 retained committed-byte runs (author ×5, mine ×2) |
| `expected_errors` | 9 r92 cases / 18 lines; `rows_with_expected_errors` 59 → **68** |
| floor gate | `r92_expected_errors_all_matched` = **true** in all 7 runs; `dead_entry_count=0` in the 4 green ones |
| nav envelope | 144 committed nav receipts: payload0 98 / payload1 46 / **neither 0**; only `regions_f1` is multi-valued |
| envelope on the landed fixture | `fixedfps/nav_ff150|ff180|ff600` = payload1 byte-for-byte; payload0-only check rejects them |
| boundary matrix | 416 receipts: envelope **0 rejected**; payload0-only **2 rejected** (`f600_nav.rep{1,2}`) |
| nullts binding | genuine `rc=-6` + stdout anchor + both stderr fragments; every half-removal variant (rc=134, rc=0, stdout-only, stderr-only, wrong site, wrong handler) **rejected** |
| signature forge on the landed rows | **396/396** mutants rejected (nav 46/46) — the envelope admits two real lines, not arbitrary ones |
| tombstone law | 2-byte header + 12-byte records decoded from the pin: erase/clear write `-1` into source/atlas/alt at unchanged length |
| r92 row stability | **all 14 lines byte-identical** across rep1 and rep2b |
