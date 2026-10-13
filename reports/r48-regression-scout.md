# Round 48 regression scout — reconnect after final left adjustment

Read-only scout for r48, with an isolated scratch-only candidate probe. I read the standing brief, r44–r47 regression reports and verifier caveats, r47 full-battery report, and r44/r47 fault-verifier records. No tracked fixture/runner, seeded fixture, engine/editor, or existing report was modified; no commit, push, or merge was made. The unique scratch is `corpus/live/r48-regression-scout/scratch/`, with only copied `project.godot` and a scratch `slider_adjust.gd` candidate.

## Direct bounded Godot evidence

Godot is `4.7.2.stable.arch_linux.ed1daf0bf`. I ran:

```text
timeout 15s godot --headless --path .shokunin/game-dev-2d/corpus/live/r48-regression-scout/scratch --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --reconnect-after-final-left
```

It exited **2** in about one second. After its nine per-edge assertions it printed the unique terminal marker:

```text
SLIDER_RECONNECT_AFTER_FINAL_LEFT values=6,6,6,5,5,5,5,4,4 receipts=[6] Label=Value 6
ERROR: SLIDER LATE-RECONNECT ASSERTION FAILED: expected-negative after nine verified edges
```

Scratch probe builds an in-tree HSlider (0–10, step 1, initial 5), a focusable Button, and callback-driven Label. For every parsed event it checks expected GUI focus owner before dispatch, awaits one process frame, and checks numeric value, cumulative receipts and Label. It confirms callback is connected before edge0 disconnect; after disconnect it confirms false, stays false through edge7's value4 check with `[6]`/`Value 6`, then reconnects and confirms true after that check. Edge8 release confirms connection remains true and state remains value4 / `[6]` / `Value 6`. Observed numeric sequence is `6,6,6,5,5,5,5,4,4`; only receipt `[6]` is retained, with Label `Value 6` throughout after edge0. The r48 narrowly stated hypothesis is supported by this direct scratch run.

This is candidate scratch evidence only, not battery integration or independent verifier certification. The copied probe has no runner classifier. Its expected-negative marker and exit 2 were emitted after all nine owner/state checks. HOLD if tracked implementation or full replay diverges.

## Read-only regression evidence and caveats

- r44 connected control: nine edges yielded `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, Label `Value 4`; owner before each edge, state after. Its direct evidence was Godot 4.7.2 synthetic parsed actions plus frame yields.
- r45 disconnect-at-start: same numeric values, no receipts, Label `Value 5`; negative terminal must follow all checks. Preserve this arm and row.
- r46 disconnect-after-edge0: same numeric history, receipts `[6]`, Label `Value 6`; callback stays disconnected. Preserve this arm and row.
- r47 reconnect after edge3: same numeric history; callback history `[6]` through edge6, then `[6,4]` at edges7–8, with Label changing to `Value 4`. r47 report documents a prior adverse replacement of the r46 branch/row, restored before replay; all r44–r47 branches/rows must remain exact and r48 must be additive. Its named verifier recorded full 72/72, prior tuple stability, and nine opt-in class stability; this scout does not recertify them.
- Fault-injection artifacts can show an outer/meta PASS while deliberate hang/timeout and unrelated-error inner cases are FAIL; only the clean expected-negative inner case is PASS. Timeout evidence covers tested direct-child behavior only, not general descendant cleanup. Do not imply injected faults passed from meta PASS.
- Export readiness/launch is separate from this UI claim. Prior evidence includes a relative export target launch failure (`Prepare Template: The given export path doesn't exist.`); no export, timeout, or fault path was executed or changed here.

Scope is headless Godot 4.7.2 with synthetic parsed events and process-frame waits only. No OS key-repeat, physical timing/input, rendered/pointer UI, accessibility, production/generic slider behavior, arbitrary signal semantics, or internal consumption of unchanged edges is claimed. No engine/editor/seeded edits; no commit/push/merge.
