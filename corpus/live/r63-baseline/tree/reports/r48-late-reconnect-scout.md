# Round 48 late-reconnect scout

- Role: independent bounded scratch scout; no delegation and no tracked fixture/runner edits.
- Scratch: `.shokunin/game-dev-2d/corpus/live/r48-late-reconnect-scout-scratch/` (fresh isolated directory; copied project config and scratch actor derived from r47 executor actor).
- Command: `godot --headless --path . --script slider_adjust.gd -- --repeat-right --second-focus-restore --reconnect-after-final-left`
- Engine: Godot 4.7.2.stable.arch_linux.ed1daf0bf.
- Result: process exit 2 only after all nine edge assertions. Unique terminal: `SLIDER_LATE_RECONNECT_COMPLETE values=6,6,6,5,5,5,5,4,4 receipts=6 Labels=Value 6`; expected-negative diagnostic followed.
- Measured: nine edge numeric values were `6,6,6,5,5,5,5,4,4`; callback receipt history stayed `[6]`; Label stayed `Value 6`. Callback was initially connected, confirmed connected at edge0 before disconnect and disconnected after; edge7 asserted value4/[6]/Value6 while disconnected, then reconnect confirmed; edge8 release retained 4/[6]/Value6 and connection. Focus-owner checks before each edge and state checks after each frame passed.
- Conclusion: supports the stated narrow synthetic parsed-event/frame calibration claim. No generic/OS-repeat/physical/rendered-input claim.
- Files in scratch are probe-only; no engine/editor/seeded fixture or tracked file was changed.
