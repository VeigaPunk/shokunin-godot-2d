# Round 16 clamp scout

## Constants
- Runtime: `/usr/bin/godot`, Godot 4.7.2.stable.arch_linux.ed1daf0bf.
- Scratch probe: `TextureProgressBar`, `min_value=0.0`, `max_value=100.0`, initial `value=100.0`, default `step=1.0`; one `health_changed(float)` handler assigns `value`; observer records `value_changed(float)`. One `process_frame` before emissions.
- Emission sequence: `35.0, -10.0, 140.0, 140.0`.

## Actual raw result
Positive scratch run exited 0, no stderr. stdout observations: `SETUP min=0.0 max=100.0 value=100.0 step=1.0`; input `35.0` → actual `35.0`, one receipt, `[35.0]`; input `-10.0` → actual `0.0`, one receipt, `[35.0, 0.0]`; input `140.0` → actual `100.0`, one receipt, `[35.0, 0.0, 100.0]`; repeated `140.0` → actual `100.0`, zero receipts, `[35.0, 0.0, 100.0]`. Thus the requested sequence is supported.

Existing fixture negative check: ran `health_gauge.gd -- --disconnect-signal`; exit 2. Raw stdout: `HEALTH_GAUGE_NEGATIVE actual_value=100.0 value_changed_count=0 receipt=-1.0`. stderr contained the existing initial assertion: `ERROR: Health gauge assertion failed: expected in-tree TextureProgressBar value=35 value_changed=1 receipt=35`, with backtrace at `health_gauge.gd:28`.

## Limits
This is headless Godot 4.7.2 runtime property/signal evidence from a disposable scratch probe and existing fixture negative. It does not establish rendered gauge behavior, pixels, UX, or production health integration.
