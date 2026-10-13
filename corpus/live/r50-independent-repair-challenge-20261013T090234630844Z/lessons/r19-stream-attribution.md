# Round 19 — Godot 4.7.2 headless stdout/stderr stream attribution

Reproduce on Godot **4.7.2** (`/usr/bin/godot` → `4.7.2.stable.arch_linux.ed1daf0bf`):

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-stream-attribution --godot /usr/bin/godot
```

(Parent re-run used the same flag without an explicit `--godot` path; both meta-PASS.) Fixture: `res://stream_attribution_probe.gd` (SceneTree). Opt-in only; does not alter ordinary CASES, `classify_process`, or `classify_audio_process`. Runner keeps accept/reject **stdout and stderr separate** for this probe (`run_process_streams` / `classify_streams`); r11 still notes that ordinary `run_process` concatenates streams.

## Paired commands (same script, identical quit code 0)

| Case | Actual headless command | Exit | stdout (after engine banner) | stderr | Inner classification |
|---|---|---|---|---|---|
| **ACCEPT** `stream_accept` | `godot --headless --path <scratch> --script res://stream_attribution_probe.gd --` | **0** | `STREAM_STDOUT: expected attribution marker` | empty | **true** |
| **REJECT** `stream_reject` | same + user arg `--stderr-unrelated` | **0** | same `STREAM_STDOUT: expected attribution marker` | exactly `STREAM_STDERR: unrelated attribution diagnostic` | **false** |

Evidence artifact (executor): `.shokunin/game-dev-2d/corpus/live/runs/20261012T231841765607Z/stream-attribution-verdicts.json`. Parent re-run: `.../20261012T231855322812Z/stream-attribution-verdicts.json`. Both record `same_script=true`, both script paths `res://stream_attribution_probe.gd`, `accept_emitted_stdout_marker`, `reject_emitted_stdout_marker`, `accept_lacks_stderr_diagnostic`, `reject_emitted_stderr_diagnostic`, `same_exit_zero`, meta **`verdict: PASS`**. Fixture always `print`s the stdout marker; only the reject flag adds `printerr` of the stderr diagnostic. Rejection is therefore **stream attribution**, not exit-code difference.

Executor leaf: `reports/r19-stream-executor.md`. Console `FAIL stream_reject` is the expected **inner** classification print for the reject leg, not a battery failure. Parent: battery results **n=34 all PASS** (33 ordinary + `probe_stream_attribution`).

## What is proved

- On this Godot 4.7.2 headless pair, `print` lands on **stdout only**; `printerr` of an unrelated diagnostic lands on **stderr only**.
- Classifier accept when the expected print signature is on stdout, stderr has no case-owned error, exit is the script quit code.
- Classifier reject when the same stdout signature is present but an unrelated stderr diagnostic is present — with **identical exit 0** on both legs.
- Meta PASS requires accept true, reject false, both markers on the claimed streams, and both runs on `res://stream_attribution_probe.gd`.

## What is not proved

- Crash-exit classification
- Process-tree timeout
- Export reliability (r16/r17 export-path HOLD remains open)
- Rendered output / production project gameplay
- Ordinary `run_process` stream separation (still concatenated for non-probe paths unless separately changed)
- Every diagnostic API beyond this print/printerr pair (push_error/push_warning placement was scouted elsewhere, not this meta contract)

Bounded claim: **one** Godot 4.7.2 headless stream-attribution accept/reject pair. Prior 33 ordinary outcomes remain the verifier lane's full regression charge; this lesson does not weaken unrelated-error rejection.

Parent follow-up after the critic leaf: `classify_streams` now rejects every non-empty stderr line that is not in `allowed_stderr`, closing the prefix-only hole the critic named (a plain `printerr` without `ERROR:` or `STREAM_STDERR:` would previously inner-classify true). Parent re-ran the opt-in probe after that edit: meta PASS at `corpus/live/runs/20261012T232054666461Z/stream-attribution-verdicts.json`. That re-run is author evidence, not the non-author verifier.
