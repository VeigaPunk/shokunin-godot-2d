# Round 57 named non-author verifier — save roundtrip

## Verdict: HOLD (do not claim expected 83/83 or 81 prior tuples)

I am a non-author verifier. I did not edit tracked runner/fixture files, LOG, scorecard, or prior reports. All scratch mutations are below `.shokunin/game-dev-2d/corpus/live/r57-save-verifier/`.

### Inputs and integrity
- Declaration: `.shokunin/game-dev-2d/LOG.md` Round 57 specifies a named non-author seven-flag replay, separate fault-injection, scratch-only sabotage, and tuple/opt-in comparisons.
- Seeded fixture: `.shokunin/game-dev-2d/corpus/fixtures`; runner: `corpus/fixtures/run_battery.py`; Godot reported `4.7.2.stable.arch_linux.ed1daf0bf`.
- Read prior raw evidence `.shokunin/game-dev-2d/corpus/lessons/r56-pushframe-non-author.json` (its `verdict` is PASS; 81 total results, 72 case/script rows and 9 opt-in rows).
- SHA-256 before and after both full invocations: `run_battery.py` `b3d721f923feda6b04b9cc9b78278f5b41c1e7a9df4e3215eb13e73505f982a8` unchanged; `save_roundtrip.gd` `ba66befa6d41d6eeb99001183e67e88422288bebc8b0d0295117ea2cb909dfea` unchanged. Seeded fixture source was only read/copied, never written. No commit/push/merge.

### Full seven-flag battery
Exact command (exit 0):
```sh
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --probe-audio-warning --runs '.shokunin/game-dev-2d/corpus/live/r57-save-verifier/seven-flag-runs'
```
Raw verdicts: `.shokunin/game-dev-2d/corpus/live/r57-save-verifier/seven-flag-runs/20261013T130745718555Z/verdicts.json`. The runner's overall verdict is PASS, but it contains **84** result rows, not the declared/expected 83: 74 case/script rows plus 10 opt-in/probe rows (including two mutants and nine named opt-ins plus the extra audio-warning row). I do not normalize this discrepancy away.

- Save positive: exit 0, `PASS save_roundtrip structured=true reopened=true values_match=true`; the reported absolute file exists at `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r57-save-verifier/seven-flag-runs/20261013T130745718555Z/xdg-data/godot/app_userdata/MechanicOneShotTest-20261013T130745718555Z/r57-save.json`. It is a child of this run's `xdg-data` directory, unique to this run's stamped project identity.
- Save negative: expected and actual exit 2; exact expected signature `ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR` appears. The control copied the valid saved JSON bytes into a separate `user://` file, replaced the copy with `{`, confirmed changed bytes, parsed the copy as invalid JSON, checked the original source bytes were preserved, then emitted the intended error. This demonstrates malformed-copy rejection, not merely a success print.
- For the 72 case/script tuples present in r56, **72/72 match** on script, flags, expected/actual exit, signature, verdict, and error. The two new rows are positive and negative save cases. r56 had 81 total result rows; current result rows = 84. Therefore the stated **81 old case tuples unchanged is not satisfied as a count** by this raw baseline: only 72 prior case/script tuples are represented in r56, and all 72 match. No unsupported 81/81 claim.
- The nine prior opt-in classifications are stable: 9/9 exact verdict and inner-classification matches. Current run also adds the audio-warning probe. Godot diagnostic/stream inner negative controls correctly classify false. The runner prints `FAIL` for intentionally rejected inner cases; outer probe verdicts are PASS.

### Separate fault injection
Exact command (exit 0):
```sh
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection --runs '.shokunin/game-dev-2d/corpus/live/r57-save-verifier/fault-runs'
```
Raw: `.shokunin/game-dev-2d/corpus/live/r57-save-verifier/fault-runs/20261013T130501674471Z/fault-verdicts.json`. Outer fault-probe verdict PASS is truthful: bounded hang is classified FAIL after the 0.25s timeout; clean expected-negative exits 2 and is PASS; unrelated-error case is FAIL. This fault mode is separate from the seeded battery and does not replace it.

### Scratch-only classifier sabotage
These are direct Godot 4.7.2 runs against fixture copies, with unique absolute XDG data paths. The first attempts accidentally used relative `XDG_DATA_HOME`; Godot warned and fell back to account data. Those attempts are adverse setup telemetry, not evidence. Corrected runs below use absolute paths and remain inside this verifier's scratch.

1. **Negative-control corruption sabotaged:** copy of fixture at `sabotage/negative/fixtures`; replaced the malformed `{` bytes with the valid original saved bytes. Command:
```sh
XDG_DATA_HOME='/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r57-save-verifier/sabotage/negative/xdg-data' godot --headless --path '/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r57-save-verifier/sabotage/negative/fixtures' --script save_roundtrip.gd -- --corrupt-negative
```
Exit 2, `ERROR: SAVE ASSERTION FAILED: corrupted bytes unchanged` (line 44); it rejected the sabotage before the expected malformed-JSON terminal. Thus classifier/evidence does not merely accept successful printing; the source runner's expected terminal is absent.
2. **Positive load sabotaged:** copied fixture at `sabotage/positive/fixtures`; changed expected dictionary after writing the saved value (`expected["level"] = 8.0`) before reopen comparison. Command:
```sh
XDG_DATA_HOME='/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r57-save-verifier/sabotage/positive/xdg-data' godot --headless --path '/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r57-save-verifier/sabotage/positive/fixtures' --script save_roundtrip.gd
```
Exit 2, `ERROR: SAVE ASSERTION FAILED: structured roundtrip` (line 26). Positive success terminal absent; classifier would reject this output because expected signature is absent and error is unrelated. Neither sabotage touched source fixture or runner.

### Scope / caveats
The raw run is an independent successful execution of all tests and probes, but **HOLD** for acceptance because expected total is 83 while raw is 84, and the named request says 81 old tuples although supplied r56 evidence has 72 script/case tuples. Evidence supports 72/72 prior tuple stability and 9/9 opt-in stability only. Report discrepancy to parent for reconciliation; do not infer expected counts or silently change the comparison baseline. The earlier simplifier shell exit 127 / parse failure is not used as evidence.


## Correction addendum — exact declared seven-flag replay (2026-10-13)

The parent clarified that the prior 84-row run was my own extra-flag run: it included `--probe-audio-warning`, which is not part of the seven flags in the Round 57 declaration. **That prior run and its HOLD remain preserved as adverse/mis-scoped evidence; this addendum does not rewrite it.** The claimed 81 prior “records” means 72 script/case tuples plus 9 opt-in records, not 81 script/case tuples.

I then performed a fresh run with exactly the seven declared options, omitting `--probe-audio-warning`:

```sh
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs '.shokunin/game-dev-2d/corpus/live/r57-save-verifier/corrected-seven-flag-runs'
```

Process exit: 0. Raw: `.shokunin/game-dev-2d/corpus/live/r57-save-verifier/corrected-seven-flag-runs/20261013T131017016504Z/verdicts.json`. The raw runner verdict is PASS with **83/83 results** (74 case/script rows plus nine opt-in rows; the 74 comprise the 72 prior script/case rows (including the two existing mutants) and the two new save cases). Godot version remains 4.7.2.stable.arch_linux.ed1daf0bf.

- Compared prior raw r56’s 81 result records by case/key: **72/72 prior script/case tuples match** on script, flags, expected/actual exit, signature, verdict and error. The two new case rows are `save_roundtrip` and `save_corrupt_negative`.
- **9/9 prior opt-in records match** by case, verdict and inner classifications. No prior record is missing; no mismatch found.
- Positive save is exit 0 and the absolute `user_path` exists under this run’s unique `xdg-data`: `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r57-save-verifier/corrected-seven-flag-runs/20261013T131017016504Z/xdg-data/godot/app_userdata/MechanicOneShotTest-20261013T131017016504Z/r57-save.json`.
- Negative malformed-copy test exits 2 with exact signature `ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR`.
- The separate fault-injection run and the two scratch-only sabotage runs documented above remain the applicable same-session evidence. Corrected seven-flag run did not mutate tracked fixture or runner; their hashes remain `run_battery.py` `b3d721f923feda6b04b9cc9b78278f5b41c1e7a9df4e3215eb13e73505f982a8` and `save_roundtrip.gd` `ba66befa6d41d6eeb99001183e67e88422288bebc8b0d0295117ea2cb909dfea`.

**Corrected seven-flag result: PASS for the requested count/comparison and save checks.** This supersedes the 84-row count concern only for the correct seven-flag replay. The earlier 84-row run remains documented, not erased. No tracked edits, commit, push, or merge.
