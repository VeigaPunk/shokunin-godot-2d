# r95-scribe receipts — wave-B custody + claim audit on committed `9cd47507`

Seat `g2d-r95-scribe` | lane `game-dev-2d-shokunin` | host **devin** (32 cores,
loadavg 75–98 for the whole session; 48 foreign `yes` hogs and ~10–16 concurrent
Godot processes from sibling lanes throughout). Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`, default
60 tps.

Read-only audit of the r95 `PhysicsDirectSpaceState2D` query-lattice + order-cycle
landing: **no tracked file written, no commit, no runtime config mutated.** The
only writes are `reports/round-95/r95-scribe.md` (new, untracked) and
`corpus/live/r95-scribe/**`. `git status --porcelain -uno` was empty at audit
start and at every check through both battery runs, the 160 fresh launches and
all recomputations.

**Late-window note.** A concurrent lane committed `35001d1d` (r94 simplifier)
while this audit ran. That commit touches only `LOG.md`, `SCORECARD.md`,
`corpus/live/r94-simplifier/**` and two `reports/round-94/` files; **every r95
artefact is byte-identical between the audited `9cd47507` and the current HEAD**
(blob-by-blob verified in `audit/static_audit.json → late_window`). All numbers
below are pinned to the audited commit `9cd47507`.

**Second late-window note.** At 07:26:40Z — after every launch in this audit — a
concurrent **r96-author** lane inserted its r96 block into the *worktree*
`corpus/fixtures/run_battery.py` (`+223/−0`, CASES 359 → 419). Foreign and
untouched by this seat; the 52 r95 CASES tuples and the r95 gate expression are
element-wise identical between `HEAD` and the dirty worktree, and both battery
runs here used committed bytes (run 1 on the then-clean worktree, run 2 from the
`git archive HEAD` extract).

## What is here

| artefact | path | notes |
|---|---|---|
| battery run 1 (worktree = committed bytes) | `battery-runs/20261016T070820061770Z/verdicts.json`, `battery-rep1.log` | 366 rows; 361 PASS; r95 52/52; gate true; dead 2 |
| battery run 2 (`git archive HEAD` extract) | `battery-committed/20261016T071623277563Z/verdicts.json`, `battery-rep2.log` | 366 rows; 364 PASS; r95 52/52; gate true; dead 2 |
| fresh single-arm receipts (52 arms × 2 default) | `fresh/<case>.default.rep{1,2}.{out,err,rc}` (104) | rc=0, 0 B stderr, signature present |
| fresh `--fixed-fps 30` receipts (all 35 r95b rows) | `fresh/<case>.ff30.rep1.*` (35) | rc=0, sig present |
| fresh `--fixed-fps 120` receipts (5 sentinels) | `fresh/<case>.ff120.rep1.*` (5) | rc=0, sig present |
| fresh threaded-physics receipts (10 dss + 6 r95b) | `fresh/<case>.threaded.rep1.*` (16) | `sep2d=true` echoed; rc=0, sig present |
| static custody audit | `audit/static_audit.py` → `static_audit.json` | identity, diff shape, CASES/allowlists/gate, manifests, scout rows, author runs |
| own-cell binding | `audit/own_cell_binding.json`, `audit/scout_own_cell_binding.json` | 35/35 r95b bound to own boundary cells (308 receipts); 17/17 dss bound to own scout cells (150 receipts) |
| receipts census | `audit/receipts_census.py` → `receipts_census.json` | 892 receipts; 472 row receipts; 472 hits / 0 misses; 0 `ERROR:` lines; 20 collisions (the x0/y1000 duplicate) |
| law re-derivation | `audit/laws_recompute.py` → `laws.json` | cycle k(k−1), perm, celloff, twopiles, free, cap40, layers, warm, rigid, procwait/env |
| mutant test + classifier properties | `audit/recompute.py` → `recompute.json`, `audit/floor_gate.py` → `floor_gate.json` | 52/52 baseline; 3288/3288 signature + 1492/1492 output mutants rejected; gate loudness table |
| cross-run comparison | `audit/compare_runs.py` → `compare_runs.json` | 307 identical / 59 differing (24 r95, all `proc=` only) / 3 flips |
| scout verifier re-run (read-only) | `audit/scout_verify_rows.txt` | `ROWS` 150/150, `ROWS_PREFIX` 150/150, `rejected=[]` |
| fresh-arm driver | `audit/fresh_arms.py` | replay script |
| manifest | `manifest.sha256` | 1091 entries = every file under this lane except itself and the two regenerable scratch project copies (`fresh-proj/`, `fresh-proj-threaded/`, verified byte-copies of `corpus/fixtures/`) |

## Replay

```sh
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
python3 corpus/live/r95-scribe/audit/static_audit.py
python3 corpus/fixtures/run_battery.py --godot godot --runs corpus/live/r95-scribe/battery-runs
git archive HEAD | tar -x -C /home/vgpnk/r95-committed-extract
python3 /home/vgpnk/r95-committed-extract/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
        --runs "$PWD/corpus/live/r95-scribe/battery-committed"
python3 corpus/live/r95-scribe/audit/fresh_arms.py --reps 2
python3 corpus/live/r95-scribe/audit/receipts_census.py
python3 corpus/live/r95-scribe/audit/laws_recompute.py
python3 corpus/live/r95-scribe/audit/recompute.py
python3 corpus/live/r95-scribe/audit/floor_gate.py
python3 corpus/live/r95-scribe/audit/compare_runs.py
python3 corpus/live/r95-scout/verify_rows.py   # read-only, reproduces 150/150
```

## Headline numbers

- HEAD `9cd47507` (parent `6f817d10`), 4 files / **1907 insertions / 0 deletions**;
  `run_battery.py` `+163/−0` in two blocks (152-line r95 CASES block at old line
  877, 11-line floor gate at old line 3113). CASES 307 → 359; results rows
  314 → 366 (7 meta); r95 rows contiguous at indices 303–354; crash/descendant
  tail (4 cases) intact.
- Fixtures are **byte-copies** of the frozen probes: `dss_lattice.gd`
  `77ae4adb8a47ccf5…479627` (743 lines, scout probe), `r95b_order.gd`
  `4f7e945e1b16f241…d9e2490` (777 lines, boundary probe); `project.godot`
  unchanged vs `HEAD~1` (`8de8b3af…`).
- Allowlists unchanged by r95: `expected_errors` 72 keys (69 non-empty),
  `required_stderr` 3 keys — **zero r95 keys in either**.
- Floor gate `r95_expected_errors_all_matched` at `run_battery.py:3272`, scoped to
  `("dss_lattice_", "r95b_order_")`, `dead_in_run`-fail-closed; `true` in all six
  366-row runs (author ×4 + scribe ×2) and in both of this seat's runs.
- Manifests verify completely: scout 565/566 (13 tracked), boundary 1062/1063
  (10 tracked) — 0 missing, 0 hash mismatch, 0 unlisted.
