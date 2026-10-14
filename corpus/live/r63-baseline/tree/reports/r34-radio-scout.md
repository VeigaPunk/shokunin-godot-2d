# Round 34 radio/group scout (scratch only)

## Scope and environment
Godot 4.7.2.stable.arch_linux.ed1daf0bf, headless standalone script in `corpus/live/r34-radio-scout/`. No tracked files edited. Initial literal `RadioButton` attempt failed because Godot 4.7.2 has no `RadioButton` class; parser failure and subsequent non-exiting `ClassDB.instantiate` attempt are preserved in `literal-radio-failure.log`; parent terminated the process. My first ButtonGroup attempt also produced an adverse second-target result and is retained in `adverse-first-attempt.log` as telemetry, not valid evidence.

## Corrected probe
Used the reviewer-equivalent minimal native setup: two `Button`s with `toggle_mode=true`, shared `ButtonGroup` (default `allow_unpress=false`), A initially pressed, connected `toggled` callbacks, and Label initially Ready. Each target is explicitly focused before both `ui_accept` edges; after awaiting a frame, both `target.has_focus()` and viewport focus owner equality were true before each press. B then A. Commands were bounded by `timeout 20s`; connected and disconnected both exited normally. Raw outputs: `connected.log`, `disconnected.log`; script copied from reviewer variant with a focus-owner diagnostic and disconnect arg matching this scratch.

## Observed
Initial state A=true/B=false. B focus: press-only unchanged; release selects B/unselects A, emitting in order `A:false`, `B:true`. A focus: press-only unchanged; release selects A/unselects B, emitting `B:false`, `A:true`. Final connected state A=true/B=false; exact callback sequence `[A:false,B:true,B:false,A:true]`; callback-driven label ends A (A's handler changes label only when true; B likewise).

Disconnected run has the same property transitions A=true/B=false → A=false/B=true → A=true/B=false; receipts remain empty throughout and label stays Ready. This is scratch evidence for the actual Godot primitive (toggle Buttons + ButtonGroup), not a nonexistent `RadioButton` class. Scope is synthetic headless focused actions, not general ButtonGroup behavior, pointer/rendering, physical timing, accessibility, or production behavior.
