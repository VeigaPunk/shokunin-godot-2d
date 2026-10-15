# r19 stream-executor leaf

role: executor  
axis slice: calibration (stream attribution pair)  
branch: craft/game-dev-2d-r1 @ fa31bef (not committed)

## Files written / edited

- NEW `.shokunin/game-dev-2d/corpus/fixtures/stream_attribution_probe.gd`
- EDIT `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py` only:
  - `--probe-stream-attribution` (default off)
  - `classify_streams(...)` helper (does **not** change `classify_process` / `classify_audio_process` / ordinary CASES)
  - paired accept/reject headless Godot runs; separate stdout/stderr capture; `stream-attribution-verdicts.json`
  - results record `case=probe_stream_attribution`
- NEW `.shokunin/game-dev-2d/reports/r19-stream-executor.md` (this file)

## Refused to change

- MANIFEST.json, sibling books, seeded fixtures, `classify_process`, `classify_audio_process`, existing probe flags, ordinary case list
- no commit / no push / no subagents

## Fixture design

- SceneTree; always `print("STREAM_STDOUT: expected attribution marker")`
- if `--stderr-unrelated` in user args: `printerr("STREAM_STDERR: unrelated attribution diagnostic")`
- `quit(0)` both paths (exit does not distinguish)

## Observed probe run

Command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-stream-attribution --godot /usr/bin/godot
```

- overall battery exit: 0
- stream_accept: classification=True, exit=0
- stream_reject: classification=False, exit=0
- meta stream attribution verdict: **PASS**
- artifact: `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/runs/20261012T231841765607Z/stream-attribution-verdicts.json`
- same_script=True script_paths=['res://stream_attribution_probe.gd', 'res://stream_attribution_probe.gd']
- accept_emitted_stdout_marker=True
- reject_emitted_stdout_marker=True
- accept_lacks_stderr_diagnostic=True
- reject_emitted_stderr_diagnostic=True
- same_exit_zero=True
- inner_classifications=[True, False]

Bounded claim: one Godot 4.7.2 headless stream-attribution pair; not crash classification, not process-tree timeout, not export reliability, not rendered output.

Note: default runner still executes the ordinary 33 cases before the optional probe; ordinary outcomes all PASS on this run. Full 33-case re-verify is for the verifier lane.


## Parent re-run confirmation

Parent re-ran `--probe-stream-attribution` on the uncommitted runner:
- Meta verdict PASS
- stream_accept inner True exit 0; stdout marker present; stderr empty
- stream_reject inner False exit 0; same stdout marker; stderr exactly `STREAM_STDERR: unrelated attribution diagnostic`
- Battery results n=34 all PASS (33 ordinary + probe_stream_attribution)
- Console line `FAIL stream_reject` is the expected inner classification print, not a battery failure

Executor status: leaf complete; no commit.
