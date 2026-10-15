# Round 30 edge scout — press-only vs release

## Result
Godot 4.7.2 scratch probe confirms the focused Button does not invoke `pressed` after `ui_accept` press-only; each receipt and Label update occurs only after the matching release and a frame. Both actions preserve Button focus. This supports assertions at both boundaries in the tracked fixture. Scout made no tracked fixture or runner edits.

- Runtime: `godot --headless`, `4.7.2.stable.arch_linux.ed1daf0bf`.
- Scratch: `.shokunin/game-dev-2d/corpus/live/r30-edge-scout/project/edge.gd`; SHA-256 `892f3ec6e293297430d830dd93cdcdcaac545d563280747f7f511452f0e85e15`.
- Raw stdout: `.shokunin/game-dev-2d/corpus/live/r30-edge-scout/godot-4.7.2-edge-raw.txt`; exit 0; SHA-256 `1eb489d89df61d35648ef567503aa97db31e506ff7bb59c79a40181e019fd77c`.
- Observed sequence: setup focus=true owner_button=true receipts=0/Ready; action 1 press-only remains 0/Ready; release changes to 1/Activated 1; action 2 press-only remains 1/Activated 1; release changes to 2/Activated 2. Focus and owner_button are true at each observation.
- Probe sends each event separately via `root.push_input`, awaits `process_frame` after each edge, and records owner, focus, receipt count, and text. It uses one connected `Button.pressed` handler. The output directly observes both boundaries; no missed/intermediate events inferred.
- This is scratch-only synthetic headless `ui_accept` Button behavior, not pointer timing, debounce, rendered UI, or production focus behavior. No engine/editor source, seeded controls, tracked fixtures or runner were changed.
