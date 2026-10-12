# r19 stream-attribution scout (leaf)

**Role:** scout (read-only except this report)  
**Round axis (parent):** calibration  
**Lane axes:** depth, coverage, calibration  
**Godot:** `/usr/bin/godot` → `4.7.2.stable.arch_linux.ed1daf0bf` (exit 0 on `--version`)  
**Scratch (not corpus):** `/tmp/stream_attr_scout_yw_860f1`  
**Refused:** any edit to `run_battery.py`, fixtures, MANIFEST, sibling books, commits/pushes, subagent spawns.

## Axes named

| Axis | Scout contribution |
|------|--------------------|
| depth | Real separated stdout/stderr capture under headless Godot 4.7.2; quit-code and banner behavior |
| coverage | print / printerr / push_error / push_warning + paired accept/reject flag design |
| calibration | Claims bounded to one stream-attribution pair; not crash, timeout, export, or render |

## Method

Minimal `project.godot` + SceneTree scripts in `/tmp`. Each run:

```text
/usr/bin/godot --headless --path /tmp/stream_attr_scout_yw_860f1 --script res://<script.gd> [-- --flag]
```

`subprocess.run(..., capture_output=True, text=True)` kept **stdout and stderr separate** (unlike `run_battery.run_process`, which concatenates).

## 1. Stream placement (confirmed)

| API | Stream | quit code effect on placement |
|-----|--------|-------------------------------|
| `print(...)` | **stdout only** | none — same placement for quit(0) and quit(1) |
| `printerr(...)` | **stderr only** (raw text, no `ERROR:` prefix) | none |
| `push_error(...)` | **stderr** as `ERROR: <msg>` + `at:` + GDScript backtrace | none |
| `push_warning(...)` | **stderr** as `WARNING: <msg>` + `at:` + backtrace | none |

### Evidence: print only, quit(0)

- **cmd:** `/usr/bin/godot --headless --path /tmp/stream_attr_scout_yw_860f1 --script res://print_only_q0.gd`
- **exit:** `0`
- **stdout (exact):**
```text
Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org

STREAM_MARK_PRINT_ONLY
```
- **stderr (exact):** empty

### Evidence: print only, quit(1)

- **cmd:** `... --script res://print_only_q1.gd`
- **exit:** `1`
- **stdout:** same banner + `STREAM_MARK_PRINT_ONLY` (identical stream placement to quit(0))
- **stderr:** empty

### Evidence: printerr only, quit(0)

- **exit:** `0`
- **stdout:** banner only (no mark)
- **stderr (exact):**
```text
STREAM_MARK_PRINTERR
```

### Evidence: printerr only, quit(1)

- **exit:** `1`
- **stdout:** banner only
- **stderr (exact):** `STREAM_MARK_PRINTERR` (placement unchanged vs quit(0))

### Evidence: push_error, quit(0)

- **exit:** `0`
- **stdout:** banner only
- **stderr (exact lines):**
```text
ERROR: STREAM_MARK_PUSH_ERROR
   at: push_error (core/variant/variant_utility.cpp:1023)
   GDScript backtrace (most recent call first):
       [0] _initialize (res://push_error_q0.gd:3)
```

### Evidence: push_error, quit(1)

- **exit:** `1`
- **stderr:** same shape with `res://push_error_q1.gd:3` — still stderr-only

### Evidence: push_warning, quit(0)

- **exit:** `0`
- **stderr (exact):**
```text
WARNING: STREAM_MARK_PUSH_WARNING
     at: push_warning (core/variant/variant_utility.cpp:1033)
     GDScript backtrace (most recent call first):
         [0] _initialize (res://push_warning_q0.gd:3)
```

### Combined script (all four APIs)

- **stdout:** banner + `STREAM_MARK_PRINT` only  
- **stderr:** `STREAM_MARK_PRINTERR`, then `ERROR:`/`WARNING:` blocks  
- quit(0) vs quit(1): **identical stream split**; only process exit differs

**Conclusion (1–2):** Parent fact holds. `quit(0)` vs `quit(1)` does **not** move messages between streams. Exit code is orthogonal to stream attribution.

## 3. Engine banner vs signature-in-stdout

- Banner line (every successful headless start observed here):
```text
Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org
```
- Always on **stdout**, never on stderr in these runs.
- Followed by a blank line, then script `print` output.

**Would the banner break a signature-in-stdout check?**  
**No**, if the classifier uses substring / exact-line membership (`signature in stdout` or line equality), because the banner does not contain fixture markers.  
**Yes-risk** only if someone required `stdout == signature` or “stdout has exactly one non-empty line”. Production `classify_process` uses `signature in output` on the **concatenated** blob today, so banner noise is already tolerated there; a stream-aware check should still use containment/exact marker line, not whole-stream equality.

Banner does **not** put false `ERROR:` lines on stdout.

## 4. Accept / reject flag design (no collision)

### Existing flags to avoid (from `run_battery.py` + `godot_error_probe.gd`)

CLI on battery: `--probe-failing`, `--fault-injection`, `--probe-unrelated-error`, `--probe-export-launch`, `--probe-godot-error`, `--probe-audio-warning`.  
User args inside Godot fixtures: `--unrelated-error` (godot_error_probe), `--no-collision` (contact/level).

### Recommended fixture (implementer path only; scout did not write corpus)

**Path:** `.shokunin/game-dev-2d/corpus/fixtures/stream_attribution_probe.gd`  
**Battery flag:** `--probe-stream-attribution` (new only; do not repurpose existing probes)

**Script shape (verified under /tmp as `stream_attribution_probe.gd`):**

```gdscript
extends SceneTree

const ACCEPT_MARK := "STREAM_ATTR_ACCEPT: print signature on stdout"
const REJECT_DIAG := "STREAM_ATTR_REJECT_DIAG: unrelated printerr on stderr"

func _initialize() -> void:
    var user_args := OS.get_cmdline_user_args()
    print(ACCEPT_MARK)
    if "--emit-stderr-diag" in user_args:
        printerr(REJECT_DIAG)
    quit(0)
```

**Why this design**

| Choice | Rationale |
|--------|-----------|
| `print` accept marker | Lands on stdout only; exercises signature-on-stdout ACCEPT path |
| `printerr` reject diag (not `push_error`) | Raw stderr line **without** forcing `ERROR:` prefix; still fails unrelated-error style checks if classifier scans stderr (or concat) for case-owned faults. Distinct from `godot_error_probe` which uses `push_error` + quit(1) |
| Same `quit(0)` both arms | Exit codes identical → rejection is stream/content, not exit delta |
| User flag `--emit-stderr-diag` | Does not collide with `--unrelated-error` / `--no-collision` |
| Markers prefixed `STREAM_ATTR_*` | Do not collide with `EXPECTED_NEGATIVE` / `UNRELATED_FAULT` strings |

### Paired real runs (scout verification)

**ACCEPT**

- **cmd:** `godot --headless --path <scratch> --script res://stream_attribution_probe.gd`
- **exit:** `0`
- **stdout:** banner + blank + `STREAM_ATTR_ACCEPT: print signature on stdout`
- **stderr:** empty  
- Classifier intent: accept when accept mark ∈ **stdout**, stderr has no case-owned error/diag, exit == 0

**REJECT**

- **cmd:** same + `-- --emit-stderr-diag`
- **exit:** `0` (identical to accept)
- **stdout:** same accept mark (still on stdout)
- **stderr (exact):** `STREAM_ATTR_REJECT_DIAG: unrelated printerr on stderr`
- Classifier intent: reject because reject diag is on **stderr** and is not an allowed error

### Implementer notes (for parent / non-scout leaves; not done here)

- Extend `run_process` **only for this probe path** (or a sibling helper) to return `(stdout, stderr, code, error)` and record both streams in verdict JSON; do not change ordinary battery concat behavior if that would shift the prior 33 outcomes.
- Meta PASS: accept classifies true, reject classifies false, both markers on claimed streams, both `res://stream_attribution_probe.gd`, same exit.
- Do not weaken unrelated-error rejection; do not edit `classify_process` / ordinary case list / seeded fixtures per contract.
- Bounded claim: one Godot 4.7.2 headless stream-attribution pair — not crash classification, process-tree timeout, export reliability, or rendered output.

## Parent fact re-check

Parent stated: print → stdout; printerr / push_error / push_warning → stderr; `run_process` concatenates so stream attribution is unprobed. **Re-run confirms all of that on 4.7.2.**

## Files

| Path | Action |
|------|--------|
| `.shokunin/game-dev-2d/reports/r19-stream-scout.md` | **written** (this report) |
| corpus fixtures / `run_battery.py` | **not edited** (refused) |

## Full probe dump

`/tmp/stream_attr_scout_yw_860f1/probe_results.json`
