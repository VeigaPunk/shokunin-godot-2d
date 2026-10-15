# Round 33 CheckBox edge scout report

## Scope
Scratch-only Godot 4.7.2 headless probe, connected and signal-disconnected cases, using two focused `ui_accept` press/release pairs. Raw scripts/logs are in `.shokunin/game-dev-2d/corpus/live/r33-checkbox-edge-scout/`. No tracked fixture/runner edits.

## Raw observations
- `connected.log` (exit 0): after press1, checked=false, receipts=[], Label=Ready; release1 checked=true, receipts=[true], Label=On. After press2, checked=true, receipts=[true], Label=On; release2 checked=false, receipts=[true,false], Label=Off. Focus is set and checked before the pairs.
- `disconnected.log` (exit 2): same two-pair state behavior: press1 false, release1 true, press2 true, release2 false. Receipts stay [] and Label stays Ready at all four edges. It exits only after both pairs with the intended missing-signal diagnostic.
- Both commands completed under `timeout 12` (about 0.4 seconds); no timeout or setup diagnostic.

## Conclusion
On this Godot 4.7.2 synthetic headless input path, the observed CheckBox state transitions occur on release, not press; the connected signal/Label reaction likewise occurs on release. The disconnected arm distinguishes property state change from callback receipts and Label effects while completing both pairs. This supports press-only prior-state and release-only next-state assertions. It is scratch evidence, not fixture integration or independent verification. No pointer/rendered UI, real-user timing, accessibility, or production behavior claim.
