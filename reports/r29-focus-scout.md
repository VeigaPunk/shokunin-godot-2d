# Round 29 focus-dependence scout

## Result: focus dependence observed in one-action paired probe

Scratch paired probe using the actual Godot 4.7.2 headless runtime shows a contrast. With identical `ui_accept` press/release delivery and signal wiring, the focused Button received one receipt (`Activated 1`), while the explicitly unfocused Button received no additional receipt (final count remained 1). The focused Button had the Button as GUI focus owner immediately before its action; after `release_focus()`, owner was absent and `has_focus=false` before the control action. This is causal paired evidence for focus-dependence of this one-action input under this fixture. It does not itself verify the tracked fixture's two-action `[1,2]` sequence. As scout, I made no fixture/runner edit; executor can decide whether this evidence warrants the declared calibration change.

- Runtime: `godot --headless`, version `4.7.2.stable.arch_linux.ed1daf0bf`.
- Scratch-only script: `.shokunin/game-dev-2d/corpus/live/r29-focus-scout/project/focus_pair.gd` (SHA-256 `f5cc341374c86f20a63311651d58e38c7902acd4484b05bcb913da435d4d8985`).
- Raw output: `.shokunin/game-dev-2d/corpus/live/r29-focus-scout/godot-4.7.2-paired-raw.txt`; exit 0.
- Raw line: `PAIR focused={"has_focus":true,"owner":"@Button@2"} focus_receipts=1 focus_text=Activated 1 unfocused={"has_focus":false,"owner":"<none>"} final_receipts=1 final_text=Activated 1`.
- At both action boundaries, focus state was explicitly observed: focused owner was the Button; after `release_focus()`, no owner and Button `has_focus=false`.
- Existing tracked fixture SHA-256 `9373e361e4adaf20d6ef012c883799522f700846e672889f589596ad91983c22`; runner SHA-256 `c178aea2cfdfd16f31f3c4c0d192ab82988bfd31faba96dc2f053b4ca8d60260`. Neither changed by this scout.
- No engine/editor source or seeded control was changed. This scratch probe was not an executor change; no runner/fixture edit is recommended. Evidence is only a one-action headless Button focus contrast, not pointer hit-testing or user-facing focus behavior.
