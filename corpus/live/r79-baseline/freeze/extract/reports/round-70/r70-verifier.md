# r70 verifier — LOVE headless first-contact battery (lane g2d)

Post-landing verification of committed tree at `ceba654` ("r70: LOVE 11.5
headless first contact — uncapped cadence + writer-bound popen … 15-case
sibling battery"). Commit content confirmed via `git show --stat ceba654`:
only `love_battery.py`, `love_probe/{conf,main}.lua`, docs/report/scorecard/log
— **zero** `.gd` / `.tscn` / `run_battery.py` paths touched
(`git show --name-only ceba654 | grep -c 'run_battery\|\.gd\|\.tscn'` → 0).

Host surface: `love --version` → `LOVE 11.5 (Mysterious Mysteries)` at
`/usr/bin/love`; `godot` at `/usr/bin/godot`.

## Item 1 — `python3 corpus/fixtures/love_battery.py` → PASS (15/15)

Command run from repo root; exit 0. Output tail:

```
totals: cases=15 pass=15 fail=0 launch_ok=True done_marker=True exit=0
PASS battery: …/corpus/live/runs/love-20261014T140230913511Z/verdicts.json
```

Receipt: `corpus/live/runs/love-20261014T140230913511Z/verdicts.json`
(+ `probe.stdout.txt`, `probe.stderr.txt` in same dir). All 15 cases PASS.

## Item 2 — `python3 corpus/fixtures/run_battery.py` (Godot) → PASS

Exit 0; every row PASS including all expected-negative controls (exit=1/2
signatures), crash classification (-6/-9), export_readiness, and all meta
rows. Receipt: `corpus/live/runs/20261014T140233983332Z/verdicts.json`.
Prior rows untouched: the r70 commit adds no Godot-side files (name-only
grep → 0 matches), and the battery output row set matches the pre-existing
fixture inventory.

## Item 3 — Pin honesty, 3x rerun → PASS, no flake

Ran `love_battery.py` 3 additional times (4 fresh runs total; a 5th receipt
`love-20261014T135430468688Z` from the author run also present). All runs:
`pass=15 fail=0`, `launch_ok=True`, `done_marker=True`, exit 0.

Bound-pinned observed values across the 5 receipts:

| case | pinned bound | observed min–max | margin |
|---|---|---|---|
| dtcadence_mean_uncapped | 0.5–4.0 ms | 1.043–1.046 | ~2x from lo, ~4x from hi |
| dtcadence_min_subms | 0.0–0.1 ms | 0.002–0.003 | ~33x from hi |
| dtcadence_max_cheap | 0.5–8.0 ms | 1.080–1.155 | ~7x from hi |
| popen_l1_wait_fast | 0.2–30.0 ms | 1.00–1.63 | ~5x from lo, ~18x from hi |
| popen_l2_wait_writer | 110–140 ms | 120.60–120.97 | ~9x/~16x from edges |
| popen_close_fast | 0.0–5.0 ms | 0.10–0.14 | ~36x from hi |
| popen_total | 115–170 ms | 121.99–122.58 | ~7 ms/~47 ms from edges |

Exact pins (`n=120`, `l1`/`l2` markers, `rest_len=0`, `ret_a=768`,
`ret_b=nil`, `pump_needed=false`, `updates_without_pump=123`): identical on
every run — zero flake observed.

Assessment: bound pins hold with wide margins, not hugging edges.
`dt_max_ms` is the only bound that could plausibly flake on a heavily loaded
host (a >8 ms scheduling stall inside the 120-tick cadence window), but that
is an honest jitter bound, not a mis-pinned quantity. `l2_wait` tracks the
child's own `sleep 0.12` (120.60–120.97 ms), confirming the writer-bound
claim rather than a fixed engine constant.

## Item 4 — `updates_without_pump=123`: deterministic by structure → PASS

`main.lua` tick accounting (`corpus/fixtures/love_probe/main.lua`):

- `love.update` increments `ticks` unconditionally at entry (line 89),
  before phase dispatch.
- Phase machine: `"cadence"` emits at `ticks==120` and sets `"popen"`
  (lines 91–98); each subsequent arm runs inside exactly one update call:
  tick 121 → `popen_arm` (lines 99–100), tick 122 → `osx_arm`
  (lines 101–102), tick 123 → `pump_arm` emits `updates_without_pump=ticks`
  = 123, then `LOVE_PROBE_DONE` + `love.event.quit(0)` (lines 103–106).

So 123 = 120 cadence ticks + 3 single-tick arm phases. The count is pure
control flow — no timing input reaches `ticks`. Blocking io inside tick 121
cannot add ticks because the loop is single-threaded and suspended;
`probe.stdout.txt` confirms `popen|ticks_before=121` (counter held at 121
for the whole ~120 ms popen arm). Observed `123` on all 5 receipts.

Verdict: **deterministic by structure, not off-by-one-fragile** against
timing. The exact pin can only move if the phase machine is edited — which
is precisely the change-detection a pin is for.

## Overall

| item | verdict |
|---|---|
| 1. love_battery 15/15 | PASS |
| 2. run_battery (Godot) green, rows untouched | PASS |
| 3. Bound pins hold across reruns | PASS (no flake in 5 receipts) |
| 4. updates_without_pump=123 structural | PASS |

No defects found in the landed work.

## Receipts

- `corpus/live/runs/love-20261014T135430468688Z/verdicts.json` (author run)
- `corpus/live/runs/love-20261014T140230913511Z/verdicts.json`
- `corpus/live/runs/love-20261014T140344671782Z/verdicts.json`
- `corpus/live/runs/love-20261014T140345211276Z/verdicts.json`
- `corpus/live/runs/love-20261014T140345879110Z/verdicts.json`
- `corpus/live/runs/20261014T140233983332Z/verdicts.json` (Godot battery)

## Remaining risks

- `dtcadence_max_cheap` (bound hi=8.0 ms) is the only jitter-bound pin that
  could flake under host CPU contention; current margin ~7x.
- Battery pins the local LOVE 11.5 build's `os.execute` shape (raw 768);
  a LOVE build shipping a different Lua runtime would legitimately fail —
  that is intended pin behavior, not a defect.
