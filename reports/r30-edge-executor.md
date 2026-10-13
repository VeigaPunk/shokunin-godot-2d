# Round 30 edge executor report

## Change
Split the focused `Button` `ui_accept` positive path into two action pairs with awaited edges. The fixture checks pre-existing receipt/text after each press and the new receipt/text after each release: `Ready/0` → `Activated 1/1` → `Activated 1/1` → `Activated 2/2`. It records focus owner after the first release and final pair; the positive assertion requires focus at the first release. Disconnected and no-focus modes remain paired controls, and they fail at the intended `release1` receipt/text assertion. No ordinary rows were added. The runner signatures and exact allowed diagnostic prefixes were updated for the intentional per-edge output/negative assertion change.

## Evidence
- Godot 4.7.2; ordinary run returned 0: 42/42 PASS (39 positive/other controls plus existing expected negatives; three Button rows all PASS as classified).
- Full named path `python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`: exit 0, 53/53 PASS. Raw artifact: `.shokunin/game-dev-2d/corpus/live/r30-edge-executor/full-runs/20261013T044643087749Z/verdicts.json`.
- Compared with r29 verifier artifact: all 50 non-Button named results retained same verdict, actual exit, and signature (45 standard non-Button rows plus 5 probe summary rows); the remaining four? [correction: three Button rows] retained PASS classification and actual exits, with expected signature changes to positive edge receipt output and negative `release1` diagnostic. There are 53 total results: 50 unchanged non-Button rows + 3 Button rows.
- Scratch-only release-suppression probe, based on final fixture: exit 2 at `expected release1 text=Activated 1 receipts=1`, while setup and press-edge focus/old-state checks passed. Raw terminal output was captured in session scratch `.shokunin/game-dev-2d/corpus/live/r30-edge-executor/edge-mutation` (source copy; command output observed directly).
- Disconnected/no-focus full-run outputs each exit 2 at `release1`; their expected negative classifications pass. The controls remain in the ordinary suite with unchanged row count.
- Final source SHA-256: fixture `edb777640fe19bdd62960ef18898f8fb181fcb28db57f20025f4430d1cbb68af`; runner `38a27c76ceb18a8b5e14b90504ca8010856b305929487ccef18252f96c6bc0eb`.

## Scope and caveats
Only `corpus/fixtures/button_activation.gd`, `corpus/fixtures/run_battery.py`, this assigned report, and own scratch under `corpus/live/r30-edge-executor/` were touched. No engine/editor source, seeded controls, push, merge, or commit. This is headless synthetic `root.push_input(ui_accept)` Button edge behavior, not rendered UI, pointer timing, debounce, accessibility, or production focus behavior. I did not author a separate r30 ordinary replay lesson; full raw JSON remains in the cited scratch run.
