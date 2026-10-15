# Round 16 — health-gauge range decisions and receipt suppression

Reproduce on Godot 4.7.2 using `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-audio-warning`. Named non-author verifier independent fresh scratch replay **40/40 PASS** (31 base cases + two scratch mutations + seven opt-in probes) in `r16-clamp-verifier.json`; `--fault-injection` meta PASS in `r16-fault-regression.json`. This extends r15's same fixture, not a new game-feature case.

| Synchronous health emission after in-tree gauge range 0..100, start 100 | Actual `gauge.value` snapshot | Accumulated `value_changed` receipts |
|---|---:|---|
| 35 | 35 | `[35]` |
| -10 | 0 | `[35,0]` |
| 140 | 100 | `[35,0,100]` |
| repeat 140 | 100 | `[35,0,100]` (no fourth callback) |
| `--disconnect-signal` | 100 | `[]`; same original first assertion fails before clamp path |

The fixture samples after each emission and checks snapshots 0,100,100 plus the complete ordered receipt array before printing PASS. Non-author verifier changed the expected low bound 0→1 and independently shortened the receipt expectation in disposable scratch copies; both failed the actual clamp assertion while preserving the real observed values/receipts. Seeded fixture hashes unchanged.

**Adverse export event preserved:** executor `--probe-failing` raw `r16-export-adverse.json` failed only `export_readiness` with exit 1, `ERROR: Prepare Template: The given export path doesn't exist.` Parent fresh-scratch retry `r16-parent-retry.json` 33/33 PASS; verifier fresh combined export/readiness/launch PASS. Cause and long-term reliability remain unproved; do not convert two successful replays into an export reliability claim. Headless synchronous value/signal state only, not rendered gauge, production health system, asynchronous/re-entrant duplicate suppression, or all range semantics.
