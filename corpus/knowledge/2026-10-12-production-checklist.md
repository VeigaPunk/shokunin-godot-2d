# 2D production checklist — initial (mint)

Each row becomes falsifiable when a fixture names its counting command.

| system | falsifiable probe sketch | status |
|---|---|---|
| game loop | headless N-frame run exits 0 within bound | inherited r10 |
| input | synthetic event → receipt; wrong-key rejected | inherited r11b/r13 |
| physics | overlap collects once; mask-zero negative | inherited r4/r10 |
| scene flow | transition replaces current_scene, old freed | inherited r5 |
| camera | follow target within delta after k frames | r2 headless Camera2D effective center positive + detached no-follow control; rendered viewport unprobed (`corpus/lessons/r2-camera-verifier.json`) |
| tilemap/level | load .tscn level, count solid cells | r4 packed TileMapLayer occupied cell and collision-polygon metadata, 21/21 (`corpus/lessons/r4-level-verifier.json`); runtime contact/rendering unprobed |
| UI/HUD | canvas item updates on signal | r3 synthetic CanvasLayer/Label signal update + disconnected control, 19/19 (`corpus/lessons/r3-ui-verifier.json`); production/rendered HUD unprobed |
| animation | state change at frame k, no stuck state | r5 deterministic AnimationPlayer property advance and zero-speed stuck control, 23/23 (`corpus/lessons/r5-animation-verifier.json`); rendered/production juice unprobed |
| audio | bus routing resolves, silent headless | r59 Godot4.7.2 named non-author 89/89: explicit non-Master FixtureBus getter/index resolves plus playback advancement; invalid name falls back to Master with separate expected diagnostic (`corpus/lessons/r59-audio-non-author.json`). No audible output/mixer signal flow claim |
| save/load | round-trip JSON stable | r58 headless Godot 4.7.2 distinct writer→read-only reader process with same run-local XDG/project identity, separate missing-file negative, named non-author 87/87 (`corpus/lessons/r58-process-non-author.json`, `r58-process-evidence-non-author.json`); r57 one-process malformed-syntax control remains; crash durability, atomicity, production persistence unprobed |
| export | headless export dry-run flags missing deps | r6 actual Linux/X11 scratch export + missing-preset negative, 25/25 (`corpus/lessons/r6-export-verifier.json`); generated artifacts deleted, app launch/production project unprobed |
