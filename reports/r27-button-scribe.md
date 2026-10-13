# Round 27 scribe — evidence and report-last checklist

Status: **incomplete; no admission/verdict from this scribe**. This is a read-only evidence checklist, not a raw run or independent verification.

## Declared claim / before state

The Round 27 LOG claim targets one headless in-tree `Button` activation → `pressed` signal → in-tree `Label` update, paired with the same activation after disconnecting the receiver. It declares 39 ordinary cases and 50/50 full replay before, targeting 41 ordinary and 52/52 after. Scope explicitly excludes pointer hit-testing, rendered UI, focus/accessibility, and production scene behavior.

## Artifacts inspected (worktree, not yet independently validated)

- `corpus/fixtures/button_activation.gd` is present and creates a `CanvasLayer`, `Button`, and `Label`; awaits a process frame; checks both controls in-tree and initial `Ready`; connects `pressed` unless `--disconnect-signal`; sends `ui_accept` pressed/released through `SceneTree.root.push_input`; then checks one callback and `Activated` text.
- `corpus/fixtures/run_battery.py` currently appends `button_activation` and `button_activation_disconnected` rows to `CASES`, expected exits 0 and 2 respectively. Existing fixture source is not changed in this observed diff.
- Current worktree is not clean and includes many prior-round untracked scratch paths and an edited LOG. Do not attribute unrelated paths or broad worktree changes to this lane.
- `r27-regression-scout.md` is present and read-only. The scout recommends an engine button activation API and notes an emitted `pressed` signal does not establish physical input/hit-testing. Its prior-case preservation observations are not a replay.
- `corpus/live/r27-mutation-reviewer-scratch/` contains a separate exploratory draft using `button.press()` and a disconnected variant. It is not the assigned fixture, has no verdict JSON inspected, and does not establish that the committed-in-progress fixture's `push_input` path activates a focused Button in headless mode.

## Raw evidence / verdict status

No Round 27 `verdicts.json`, named non-author verifier report, or `corpus/lessons/r27-button-verifier.json` was found during this review. I did not execute Godot or the battery, edit fixtures, or infer PASS from the runner's `CASES` table. Thus activation, exactly-one callback, disconnected same-assertion failure, case count, prior-row preservation, hashes, and exit classification are **unverified** here.

## Report-last closure checklist

Before any admission, the parent should obtain the named verifier's raw full-replay JSON and report, then confirm:

1. The complete requested combined command exits 0 and records 52/52, including precisely the two new rows and the earlier 50 rows retained with expected statuses/signatures.
2. Positive raw stdout establishes both controls in-tree, initial `Ready`, one actual button activation through the tested Godot API, exactly one `pressed` callback, and final `Activated`; no setup/parse/error/warning noise undermines attribution.
3. Disconnected arm performs the same activation, then fails the same final label/callback assertion with the declared expected diagnostic (not setup failure).
4. A scratch-only disconnect/activation mutation is detected by the intended assertion if required by the verifier plan; preserve raw record and exact mutated file/hash.
5. Tracked seeded fixture hashes remain unchanged; report any environmental/export/timeout anomalies rather than discarding them.
6. Compare the prior 50 verdict rows, state limits, and issue axis verdicts only after evidence is complete. Coverage may be **improved** only on independent evidence with no harmed depth/calibration; otherwise HOLD.
7. Integrate raw lesson/report and append closure to LOG, then commit the report last per round protocol. Do not push or merge.

No constants changed by this scribe. No verdict or claim beyond artifact inspection is made.
