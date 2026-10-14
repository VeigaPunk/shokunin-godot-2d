# Round 55 named non-author verifier — frame-separated clear then push

## Result: fresh replay PASS; bounded claim only

LEAF/no delegation. Candidate was rerun only after parent reported repair. Runtime: Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Prior pre-repair verifier run under `corpus/live/r55-frame-verifier/runs/20261013T103529894014Z/` is tainted/adverse because the tracked prior r54 branch print was changed; it is excluded from this result and no raw lessons were copied from that run. Earlier malformed quoted shell invocation (exit 127) ran no test. I also violated the no-delegation rule before this task; parent cancelled/deleted the child. Neither its activity nor output is evidence.

## Fresh battery and fault replay

Fresh seven-flag command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r55-frame-verifier/repaired/runs
```

Result PASS, **80/80** (69 ordinary + 2 mutants + 9 opt-in classifications). Raw was copied once byte-identically to `corpus/lessons/r55-frame-non-author.json`, SHA-256 `ecaa7807e1eb7d01914ac8b3e9837c349c1e80f4032978ac727a2e20037c3e51`. Compared against `corpus/lessons/r54-order-non-author.json`: all **70/70** previous tuple-bearing `(case, verdict, actual_exit, signature)` rows match exactly by case. The sole added tuple row is `slider_adjust_repeat_right_second_focus_restore_clear_frame_then_push_release` with expected-negative exit 2 and exact terminal signature. Nine opt-in classifications match r54 (export positive/negative assertions, Godot diagnostic, stream attribution, crash, timeout); intentional unrelated-error and stream-reject inner classifications remain false under outer probe PASS.

Separate `--fault-injection` run PASS outer classification, raw copied once to `corpus/lessons/r55-fault-non-author.json`, SHA-256 `2e11424fa1ed88086de6c92c4080eaa5aa508a6d5bc46127b64a7f5581d00e1c`. Expected inner results: hang times out/FAIL; clean expected negative PASS; unrelated error FAIL.

## Direct scratch and omission sabotages

Fresh direct scratch copied current fixture into `corpus/live/r55-frame-verifier/repaired/direct/project`. Godot reached the unique expected-negative exit 2 only after the candidate branch assertions and eleven edges; terminal reports values `6,6,6,5,5,5,5,4,4,3,3`, receipts `6,3`, labels `Value 6,Value 3`, callback connected. Candidate code checks the actual awaited intermediate substep: after `Input.action_release("ui_left")` and one `process_frame`, observer remains 3, action false, numeric 3, receipts `[6,3]`, Label `Value 3`, focus/callback true; after matching pushed release and next awaited frame, observer increments 3→4 and these other values remain stable. The earlier causal wave1 scratch reports are supporting setup evidence, not substitutes for this replay.

Two fresh unique scratch sabotages were applied only within the exact `--clear-frame-then-push-release` branch. Omitting clear fails early at intermediate assertion (`observer=3 pressed=true ... focus=true callback=true`), before unique terminal. Omitting push fails early at observer assertion (expected exactly one delivered release), before terminal. Both are expected-negative rejections. Earlier omit-intermediate-await sabotage reached the candidate terminal; it is **ineffective as a final-state rejection** and is recorded adverse, not evidence that the frame is necessary. The supported claim is limited to direct checks of the observed intermediate state after an actual await, not necessity of the await or a final-state difference from same-frame behavior.

Tracked fixture/runner were not modified by this verifier. Fixture SHA-256 after parent repair and throughout this verifier: `0b287ea2a687e48045359949cd83ef222c2255bfab3961574b6bc631d2f63dc1e`; runner: `d57b8f477c3507122dfb1d7d35040487c8d54598c75b6587a45484e710f3875`. No constants changed. No commit, push, or merge.

Scope is synthetic Godot 4.7.2 frame cadence and measured state only. No claim about HSlider internal consumption, physical timing, OS input, rendering, pointer/accessibility, production, or generic provenance. The new raw receipts are final; never overwrite them after parent commit. Any further replay requires a unique path.
