# Round 33 CheckBox edge executor report

## Result

Implemented the declared depth move in `corpus/fixtures/checkbox_toggle.gd`: for each of the two focused `ui_accept` press/release pairs, the fixture now checks state, toggled receipts, and Label after press-only, then checks the resulting state and signal/Label behavior after release. Connected expected edge states are `[false,true,true,false]`; `toggled(bool)` receipts progress `[true]`, then `[true,false]`; Label is `Ready` before first toggle and `On`/`Off` following releases. The disconnected control checks both unchanged press observations and both state-changing releases with empty receipts and `Ready`, then retains its expected final signal assertion failure (exit 2).

Runner changes are limited to the positive CheckBox signature, updated to include `edge_states=[false,true,true,false]`; disconnected signature and allowlist are unchanged. No other source, fixture, or signature was edited.

## Evidence and full replay

Godot 4.7.2 focused connected replay:

```text
godot --headless --path .shokunin/game-dev-2d/corpus/fixtures --script .shokunin/game-dev-2d/corpus/fixtures/checkbox_toggle.gd
```

Exit 0; raw output:

```text
CHECKBOX press=false release_state=true receipts=[true] label=On
CHECKBOX press=true release_state=false receipts=[true, false] label=Off
PASS checkbox_toggle edge_states=[false,true,true,false] toggled=[true,false] labels=[On,Off]
```

Focused disconnected replay with `-- --disconnect-signal` exited 2 only at the intended final missing-signal assertion. It emitted both release observations: `press=false release_state=true receipts=[] label=Ready`, then `press=true release_state=false receipts=[] label=Ready`.

Full author replay, including all requested opt-ins:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r33-checkbox-edge-executor
```

Exit 0, **56/56 PASS** (45 ordinary, 2 mutants, 9 opt-ins). Raw full verdict JSON: `corpus/live/r33-checkbox-edge-executor/20261013T051448250991Z/verdicts.json`. Both CheckBox rows PASS with expected exits/signatures; ordinary and opt-in expectations held. The diagnostic subprobes correctly recorded their intentional inner negative classifications (`godot_error_unrelated=False`, `stream_reject=False`) as part of passing paired probes.

## Release-omission falsification

Scratch-only copy at `corpus/live/r33-checkbox-edge-executor/release-omission/checkbox_toggle.gd` omitted the first release while leaving the release-state assertion. It exited 2 at `CHECKBOX release-only state assertion failed: expected checked=true got=false`; first press-only observation passed. Tracked source was not altered for this probe.

## Boundaries

Synthetic headless `root.push_input(ui_accept)` only. No pointer/hit test, rendered UI, physical timing, accessibility, or production-user claim. No engine/editor source, seeded control, corpus case count, or non-CheckBox runner signature changed. No commit/push/merge performed. Named non-author replay remains necessary for admission/verdict.
