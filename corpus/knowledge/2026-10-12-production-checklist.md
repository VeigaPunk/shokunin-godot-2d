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
| animation | state change at frame k, no stuck state | unprobed |
| audio | bus routing resolves, silent headless | unprobed |
| save/load | round-trip JSON stable | unprobed |
| export | headless export dry-run flags missing deps | unprobed |
