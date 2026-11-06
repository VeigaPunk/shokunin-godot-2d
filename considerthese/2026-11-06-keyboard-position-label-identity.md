# 2D: a key position is not its printed label

[Godot3.5](https://github.com/godotengine/godot/blob/3.5-stable/doc/classes/InputEventKey.xml) distinguishes layout-dependent scancode from physical_scancode. [Godot4.4](https://github.com/godotengine/godot/blob/4.4-stable/doc/classes/InputEventKey.xml) separately documents physical_keycode, Latin keycode and localized key_label. These tagged contracts expose different identities, not interchangeable spellings.

Position-based movement can preserve a hand arrangement across layouts; label-based shortcuts preserve a different intention. That is a design choice, not a universally superior binding. A displayed prompt should follow the chosen identity rather than assume a physical code is the player's visible label.

The newer reference also warns that key-repeat configuration varies, including being disabled. Repeated events are therefore not a portable gameplay clock. Unicode input remains distinct, with composition potentially requiring IME support.

Both complete class references read; no engine or keyboard tested. Repository MIT notices cover software and associated documentation with notice-retention conditions; generated manual licensing is not inferred. Original commentary only, no copied examples, training or assimilation.
