# Round 22 timeout cleanup review

## Scope and setup
Read-only review of the Round 22 proposed real-Godot timeout contrast and Python subprocess cleanup. No engine/editor, fixture, runner, seed, or control files were changed. Godot available: `/usr/bin/godot`, version observed in output `4.7.2.stable.arch_linux.ed1daf0bf`.

## Findings

- `subprocess.run(command, capture_output=True, text=True, timeout=...)` raises `TimeoutExpired` and performs cleanup of the process it launched: Python's implementation kills and waits for that direct child before returning the exception. In an isolated Python test, a child printed `same marker` (flushed), slept, and timed out at 0.4s; `TimeoutExpired.stdout` contained the marker. This is adequate to establish the paired signal: marker emitted, then the launched process did not exit before the deadline. Marker alone is not success; require `error == TIMEOUT after ...`, `code is None`, marker observed, and false classification.
- A real scratch Godot 4.7.2 headless script also emitted `TIMEOUT_REVIEW_MARKER` and remained live beyond the 8s subprocess timeout. Python delivered `TimeoutExpired` with the marker in captured stdout. This confirms the engine/runtime can exercise the expected boundary; this exploratory run did not validate the production classifier or independently confirm PID termination.
- **Process-tree limitation is material:** Python `subprocess.run` controls only the direct process. A separate isolated test launched a Python child that spawned a 30s sleeper with stdio detached, emitted the same marker, then hung. After `subprocess.run(..., timeout=.4)` returned, the recorded grandchild PID was still alive. It was explicitly terminated by the test. Thus a direct-child timeout / no direct child remains claim must not be phrased as process-tree cleanup.
- Further limitation: if a grandchild inherits stdout/stderr pipes, it may keep those pipes open after the direct child is killed; timeout cleanup/pipe draining may be delayed. Not tested here. A process group/session strategy or platform-specific tree-kill mechanism would be needed for tree-level guarantees; outside this round's requested scope.

## Reviewer verdict
A paired marker-then-timeout test is a valid narrow calibration contrast when the outcome checks timeout error and `code=None`, and checks/reaps the direct Godot process. It cannot prove descendants are gone. Preserve the explicit exclusion of descendant/process-tree cleanup and avoid reporting this as arbitrary-freeze or cross-platform coverage. No production code recommendation beyond that bounded interpretation.

## Raw experimental facts

- Direct child controlled Python probe: `subprocess.run(..., timeout=0.4)`; elapsed 0.402s; exception carried `b'same marker\n'`.
- Detached-descendant probe: same timeout; grandchild PID remained signalable after timeout handling; test sent it SIGTERM.
- Godot exploratory script: headless 4.7.2, 8s timeout; elapsed ~8.01s; exception carried engine banner and `TIMEOUT_REVIEW_MARKER`; no production files touched.
