# Round 14 warning executor

## Change

`corpus/fixtures/run_battery.py` now routes only the `audio_playback` case through `classify_audio_process`, preserving the existing exit/signature/ERROR/SCRIPT ERROR/Parse Error checks and additionally rejecting the anchored ObjectDB leak warning grammar `WARNING: <positive integer> ObjectDB instances were leaked at exit`. It accepts Godot's observed optional parenthetical verbose-details suffix on that exact warning line. This is case-scoped; export verdicts still use the ordinary classifier, so the nested-project export warning is not blanket-rejected. No logging is suppressed.

`--probe-audio-warning` loads the two committed r12 captured `audio_playback` outputs and feeds them through that production classifier. It errors if either capture is missing/ambiguous or lacks output. The meta verdict requires the expected leak line in the initial HOLD capture and its absence in the clean capture, plus classifications FAIL/PASS respectively. This uses actual captured output, not a synthetic marker-only test.

## Evidence

Command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-audio-warning
```

Exit 0. Ordinary battery: 31/31 PASS (29 listed cases plus two existing scratch mutants). Separate meta probe: PASS. Raw run: `.shokunin/game-dev-2d/corpus/live/runs/20261012T182421868971Z/verdicts.json` (scratch/ignored).

Captured r12 initial-HOLD audio output, verbatim relevant lines:

```text
PASS audio_playback in_tree=true playing=true position_advanced=true position_before=0.00580498855561 position_after=0.09868481010199 generated_samples=44100
WARNING: 2 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)
```

This captured case has exit 0 and matching playback signature, but the production audio classifier returns FAIL. The r12 clean capture has the same exit/signature and PASS line, no warning, and returns PASS. The live clean `audio_playback` run also passes. Export readiness and missing-preset cases both pass; actual export output retains `WARNING: Detected another project.godot at res://controls. The folder will be ignored.` and is accepted by the unchanged generic classifier. Missing-preset output retains that warning and passes its intended-negative classification.

The first local replay exposed an incorrect suffix regex. After correction, I explicitly tested the compiled pattern against the raw r12 warning line (`re.fullmatch` true), then reran successfully. No initial failure hidden.

## Limits

No fresh Godot leak re-emission was attempted; positive evidence is actual output captured by the r12 verifier HOLD, compared with actual clean r12 verifier output. This detects this ObjectDB warning grammar only in `audio_playback`, not every warning, other leak form, or leaks in other cases. The optional probe has not yet been independently replayed. No seeded fixture files or source scripts were edited; only the runner and this report are in scope.
