# Round 21 signal reviewer — independent POSIX semantics check

Status: feasible on this host; reviewer scratch only, no tracked edits.

- Host/tool: Linux, Godot 4.7.2.stable.arch_linux.ed1daf0bf, Python `subprocess.Popen`; scratch at `.shokunin/game-dev-2d/corpus/live/r21-signal-reviewer-scratch/`.
- Normal arm: a finite `SceneTree` script printed `SIGNAL_REVIEW_SIGNATURE`, then `quit(7)`. Python observed returncode **7**, signature in stdout, and no stderr. This is an ordinary expected nonzero exit.
- Signal arm: a separate script printed the identical signature, then stayed alive across frames. Reviewer waited until that signature was read and verified `poll() is None` before sending `SIGTERM` to the actual Godot PID. `communicate`/wait completed in 0.526s; Python observed returncode **-15** (negative signal number), hence termination by signal 15 (`SIGTERM`). The emitted signature was present before termination; no copied/synthetic output was involved.
- Implication: a probe can distinguish these arms by requiring the configured normal exit code (7 here) and no timeout/error. On POSIX Python, a direct signal termination is represented as negative `Popen.returncode` (and `subprocess.run` returncode); this Linux result is not a cross-platform guarantee. Keep `SIGTERM`, lifetime bound, and platform semantics explicit. Signal arm bounded by five-second wait with kill fallback; it settled far sooner.
- Limits: this establishes host-specific feasibility only. It does not test battery classifier behavior, production crash handling, process-tree termination, timeout handling, or non-POSIX semantics.
