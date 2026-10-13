# Round 30 edge mutation reviewer

## Scope and method
Leaf scratch-only review of the focused Button `ui_accept` edge assertions. I read the Round 30 claim in `.shokunin/game-dev-2d/LOG.md`, the tracked fixture, and the Round 30 scout raw observation. Copied the fixture project to `.shokunin/game-dev-2d/corpus/live/r30-edge-mutation-reviewer-scratch/project`; omitted the first `await _send_action_edge(false)` (release) in that copy only, leaving all assertions, especially the intended release1 assertion, intact. No delegation, tracked edits, runner changes, engine/editor/seeded controls, commits, or publishing.

## Evidence
- Tracked fixture SHA-256 before/after scratch probe: `f0b4c61bdf1444e3116d298c44debc32a74e389a27437bba50525e447cb9fb62` (unchanged; this reviewer did not edit it).
- Godot 4.7.2 headless scratch run: `godot --headless --path <scratch>/project --script res://button_activation.gd`; exit **2**.
- Raw output: `corpus/live/r30-edge-mutation-reviewer-scratch/omit-release.raw.txt`; exit record: `omit-release.exit`.
- Setup/focus passed (failure was not setup); after first press-only event the untouched receipt/text stayed 0/Ready. The run then failed exactly at the retained intended release1 assertion: `UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1, got receipts=0 text=Ready` (fixture line 64). Thus omitting release was detected at the corresponding release edge, not an unrelated later assertion.
- Scout's independent scratch-only normal path raw observation in `corpus/live/r30-edge-scout/godot-4.7.2-edge-raw.txt` records setup focused/owner true, press-only states `(0, Ready)` then `(1, Activated 1)`, and after-release states `(1, Activated 1)` then `(2, Activated 2)`. This is consistent with the asserted intended edge contrast; I did not rerun a second mutation variant.

## Assessment
The release-omission mutation is killed at the intended first release assertion with setup and press-only checks intact. This supports the Round 30 depth claim narrowly for this synthetic focused `root.push_input(ui_accept)` path. It does not establish delayed-release handling, pointer interaction, rendered UI, debounce/rate behavior, or production focus semantics. No change to ordinary case counts or runner signature was made by this reviewer.
