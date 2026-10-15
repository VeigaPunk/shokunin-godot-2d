# Round 32 checkbox reviewer — independent scratch paired probe

Scope: independent connected/disconnected CheckBox comparison using focused `ui_accept` press/release pairs. No seeded fixture or runner edits. Scratch project and script: `.shokunin/game-dev-2d/corpus/live/r32-checkbox-reviewer/project/` (`project.godot`, `checkbox_probe.gd`). Godot: `4.7.2.stable.arch_linux.ed1daf0bf`.

## Exact commands and raw outcomes

Connected command (exit 0):
```sh
godot --headless --path /home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r32-checkbox-reviewer/project --script /home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r32-checkbox-reviewer/project/checkbox_probe.gd
```
Raw stdout:
```text
Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org

SETUP focus=true owner=true checked=false label=Ready receipts=[]
EDGE1_PRESS checked=false label=Ready receipts=[]
EDGE1_RELEASE checked=true label=On receipts=[true]
EDGE2_PRESS checked=true label=On receipts=[true]
EDGE2_RELEASE checked=false label=Off receipts=[true, false]
FINAL disconnected=false checked=false label=Off receipts=[true, false]
```

Disconnected command (exit 0; observation probe, not an asserting battery case):
```sh
godot --headless --path /home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r32-checkbox-reviewer/project --script /home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r32-checkbox-reviewer/project/checkbox_probe.gd -- --disconnected
```
Raw stdout:
```text
Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org

SETUP focus=true owner=true checked=false label=Ready receipts=[]
EDGE1_PRESS checked=false label=Ready receipts=[]
EDGE1_RELEASE checked=true label=Ready receipts=[]
EDGE2_PRESS checked=true label=Ready receipts=[]
EDGE2_RELEASE checked=false label=Ready receipts=[]
FINAL disconnected=true checked=false label=Ready receipts=[]
```
Both stderr streams were empty. The disconnected treatment still changes CheckBox state on each complete action (false→true→false) while no `toggled(bool)` callback receipt arrives and the Label remains `Ready`. Connected control gets exactly `[true,false]` and Label `On` then `Off`; changes occur on release, while press edges preserve state. Thus the paired contrast isolates signal delivery/consumer update from the control's own toggle state. This is distinct from the Button `pressed` receipt mechanism.

Reviewer limitation: this was a raw behavioral scratch probe, not a battery fixture with assertion/intentional-failure classification, nor a full regression run. The paired evidence supports the proposed control. No inference about pointer interaction, rendering, accessibility, user timing, or production behavior.
