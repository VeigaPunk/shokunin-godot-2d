# R11 Godot error probe — independent verifier

## Verdict

**PASS, narrowly.** I independently ran the requested calibration and fault-injection commands. The full battery reports 33/33 cases PASS, including the real Godot diagnostic meta-case. The paired raw records show an actual expected `push_error` once in both processes and an actual unrelated `push_error` once only in the fault process. The production classifier accepts the former as the expected negative and rejects the latter. I made no source/fixture edits in the repository, delegation, commit, or push.

## Commands and evidence

Commands run from the repository root:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --fault-injection
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection
```

The requested combined invocation exited **0** (19.85 s). The full battery raw record is `.shokunin/game-dev-2d/corpus/live/runs/20261012T174938280678Z/verdicts.json`: `verdict=PASS`, 33 results, all PASS. The observed total matches the requested accounting: 27 prior battery results, four unrelated-error calibration results, one export-launch result, and one real Godot diagnostic meta-result (33 total). The JSON enumerates each result; the console output shows each status.

Paired raw process evidence: `.shokunin/game-dev-2d/corpus/live/runs/20261012T174938280678Z/godot-error-verdicts.json`. Godot was `4.7.2.stable.arch_linux.ed1daf0bf`. Both commands use the same scratch script `res://godot_error_probe.gd`, expected and actual exit **1**, expected signature `EXPECTED_NEGATIVE: deliberate assertion rejected`, and have `error: null` (no timeout/launch error):

- Clean command ends with `--script res://godot_error_probe.gd --`; classification is **true**. Raw combined output contains `ERROR: EXPECTED_NEGATIVE: deliberate assertion rejected` exactly once, then Godot's `at: push_error` location and GDScript backtrace (`_initialize`, line 8).
- Fault command is identical plus `--unrelated-error`; classification is **false**. Output contains that same expected diagnostic exactly once plus `ERROR: UNRELATED_FAULT: unrelated engine diagnostic` exactly once, each with Godot's `push_error` location and GDScript backtrace (lines 8 and 10).

These are actual headless Godot process outputs, not edited captured strings. The runner concatenates stdout and stderr before classifying, and the JSON preserves only the combined output; **stream attribution is not established**.

The requested fault-injection run also exited **0**. Raw artifact: `.shokunin/game-dev-2d/corpus/live/runs/20261012T175130565388Z/fault-verdicts.json`. Its expected injected outcomes are visible: hang and unrelated-error cases themselves classify FAIL, the clean expected-negative case PASS, and the aggregate `PASS fault injection` means the harness correctly detected those injected failures.

Export launch evidence: `.shokunin/game-dev-2d/corpus/live/runs/20261012T174938280678Z/export-launch-verdicts.json`. Both bounded launches had exit 0 and no launch error; positive startup signature was found, and the missing-startup-signature control was not. Both report no lingering process and `products_after_cleanup=[]`; no `.x86_64` export remains under the run's export-launch directory. The full battery's unrelated-error checks and export/preset cases also passed. No unexpected errors appeared in the paired diagnostic outputs; the unrelated line is the intentional fault.

## Scratch sabotage checks

I copied runner/fixture to temporary directories outside the repository and changed only those copies:

1. Disabled the classifier's unrelated-`ERROR:` rejection. Both inner classifications then became true, but the Godot diagnostic meta-case and overall battery correctly failed because the unrelated fault was accepted.
2. Suppressed the scratch fixture's unrelated `push_error`. Both inner classifications became true, but the meta-case and overall battery correctly failed because the required unrelated diagnostic was not emitted.

Scratch runs/artifacts were under `/tmp/r11-sabotage-umu8u6lp/` and `/tmp/r11-sabotage-suppress-vsbqdgij/`; neither touched repository inputs.

## Integrity and limitations

SHA-256 before and after all runs was unchanged:

- `corpus/fixtures/run_battery.py`: `e752e8e207b602bd247fead37186e6d5d3548b06894ecf4d564cdad6e82a1fac`
- `corpus/fixtures/godot_error_probe.gd`: `b89e2ef78f23dacb32766073c6a7719f01e969ceaaa9f8f634575e30ae8d8956`

The claim is limited to this fixture's two `push_error` calls, installed Godot version, and combined-output classifier path. It does not establish stdout versus stderr, every Godot diagnostic category/source, or gameplay/export crash behavior. The separate fault injection is a synthetic runner-level calibration, not a real engine crash test.
