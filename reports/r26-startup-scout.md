# Round 26 startup scout

## Scope

LEAF scout; no delegation. Only this report and `corpus/live/r26-startup-scout/` were written. No engine/editor files or seeded controls were changed.

## Real-Godot controlled delay

Host: `/usr/bin/godot`, Godot `4.7.2.stable.arch_linux.ed1daf0bf`; Linux. Scratch script `corpus/live/r26-startup-scout/timeout_probe.gd` uses `SceneTree.create_timer(1.15)` before printing the exact `TIMEOUT_PROBE: expected signature` marker and exiting 0. Its optional `--hold-open` arm waits 30 seconds after printing that same marker.

Three normal delayed runs using `godot --headless --path <scratch> --script res://timeout_probe.gd` returned exit 0, included the marker, and took 1.623s, 1.558s, and 1.570s wall time. Thus the deliberately slow but clean startup is reliably beyond the old 0.75s bound. The same command wrapped with `timeout 0.75s` was terminated with status 124 and emitted no marker: the old bound rejects this valid arm. Wrapped with `timeout 2.5s`, the delayed arm completed normally (the battery's current opt-in acceptance arm has no timeout and had the same clean completion).

For the marker-before-hang negative control, `timeout 2.5s godot --headless --path <scratch> --script res://timeout_probe.gd -- --hold-open` printed the marker and was terminated with status 124. This supports choosing a measured 2.5s bound for this host/script: it admits observed ~1.56s delayed clean startups and still expires a process that remains open after its marker. A timeout is not a general hang/process-tree guarantee; the battery should continue checking direct-child cleanup and the expected marker/classification.

## Recommendation

The controlled contrast supports the declared calibration move. Keep the positive and hold-open arms on the same delayed scratch script and same marker; require the delayed positive to exit 0 before the new 2.5s bound, and require hold-open to time out *after* observing marker. This is bounded evidence on this Godot/platform only, not evidence for arbitrary delays or other hosts. No runner/fixture edits were made by this scout.
