# Round 35 group-absence verifier — named non-author

## Verdict

**PASS, bounded headless-only evidence.** On Godot 4.7.2, the new ordinary control distinguishes the tracked ButtonGroup positive from a B-not-in-group treatment while keeping the focused B→A `ui_accept` sequence, signal wiring, setup, and labels. This is native `Button(toggle_mode=true)` behavior, **not RadioButton coverage**. No RadioButton claim is made.

## Reproduction and raw artifacts

Ran the default-path full battery from the tracked fixtures:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r35-group-absence-verifier/full
```

Exit 0, **59/59 PASS** = 48 ordinary +2 mutants +9 opt-ins. Raw exact bytes copied to `corpus/lessons/r35-group-absence-verifier.json` (SHA-256 `09a44a1004cbc52d3b8bd60b0bbe6902cdc7f6271d3c5f80f20eeec00b75a3ed`); it is byte-identical to the replay's `verdicts.json`. Prior r34 raw is `corpus/lessons/r34-button-group-verifier.json`.

Compared all 49 prior ordinary/mutant rows that carry `(verdict, actual_exit, signature)`: every triple is unchanged. All 9 top-level opt-in probe verdicts remain PASS, and nested classifications match r34 for Godot-error `[true,false]`, stream attribution `[true,false]`, crash-exit `[true,false]`, and timeout `[false,true,false]`; the export launch probe retains positive/negative assertions. The sole new row is `button_group_selection_ungroup_b`, expected and actual exit 2, classified PASS only for exact `BUTTON_GROUP ABSENCE ASSERTION FAILED after B→A: expected exclusive selection, got A=true B=true`.

Separate `--fault-injection` replay is in `corpus/lessons/r35-fault-verifier.json`. Its outer verdict is PASS; inner `fault_clean_expected_negative` PASS is intentionally distinct from `fault_unrelated_error` FAIL and `fault_hang` FAIL (timeout at 0.25s). Do not report this as all-inner-PASS.

## Independent direct Godot and sabotage checks

Own source-instrumented scratch replay is under `corpus/live/r35-group-absence-verifier/direct/` (script and grouped/ungrouped stdout+exit receipts). Before each action it records actual ButtonGroup membership and viewport focus owner:

- Grouped: before B `groupA=true groupB=true focusB=true`; after B A=false/B=true, receipts `[A:false,B:true]`, Label B. Before A `groupA=true groupB=true focusA=true`; after A A=true/B=false, receipts `[A:false,B:true,B:false,A:true]`, Label A; exit 0.
- Ungrouped: before B `groupA=true groupB=false focusB=true`; after B A=true/B=true, receipts `[B:true]`, Label B. Before A `groupA=true groupB=false focusA=true`; after A A=true/B=true, receipts `[B:true,A:true]`, Label A. It reaches both receipts, then exits 2 on the intended absence diagnostic; it does not stop during setup/after B.

Scratch-only sabotage preserved B's ButtonGroup membership while passing `--ungroup-b`. It failed exit 2 at the intended after-B state check (`expected A=true B=true`), not PASS. Sabotage project and raw output are under `corpus/live/r35-group-absence-verifier/direct/sabotage/`; tracked sources were not altered for this test.

## Early failures / classifier telemetry

Read executor report and runner history: earlier drafts stopped after B or had an unrecognized expected-error classification. Those are retained in executor scratch, not treated as evidence. Final runner rule classifies the precise later diagnostic; full battery proves final intended flow and exact signature. The negative completes B then A before exit, and classifier is specific to its diagnostic.

## Integrity, limits, and disposition

Tracked source hashes before/after verifier run are unchanged: `button_group_selection.gd` `bc9f4aadfcfb2ea4930985ca4acb4d440ad3fd3c99411c891ca434e748053957`; `run_battery.py` `78072024d092964c9e214be418df10933092caf3f73168cbc27ef189f43ebc87`. No tracked source edits, commit, push, or merge by verifier.

Scope is synthetic headless focused `root.push_input(ui_accept)` on this Godot runtime. No pointer/rendered UI, physical timing, accessibility, production guarantee, or general ButtonGroup guarantee. This supports the declared calibration move only; depth and coverage unchanged. Constants: ordinary 47→48; full 58→59. No axis harmed in the bounded replay.
