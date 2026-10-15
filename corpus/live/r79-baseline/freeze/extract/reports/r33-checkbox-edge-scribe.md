# Round 33 — CheckBox edge scribe checklist

## Scope and baseline

Read-only evidence/verdict checklist for the declared r33 depth move. I did not run Godot or the battery and did not edit fixture/runner code. Prior baseline is r32 named-verifier raw receipt `corpus/lessons/r32-checkbox-verifier.json` (56 records; 45 ordinary + 2 mutants + 9 opt-in/probe), report `reports/r32-checkbox-verifier.md`, and tracked source hashes: CheckBox fixture `a6971f7e1089177e3e7ed8923e95aa8dd1021bf0ac8c1a4856a257d3665f79bb`; runner `f03ba367c7311c83e4621f835b5a41135a6f96b0ee7023d76b317c828d0d0250`. The r32 verifier records two focused `ui_accept` press/release pairs, but only post-pair assertions; it does not establish press-only CheckBox behavior. At review time no r33 raw verifier receipt was present, so no r33 runtime result or admission can be claimed from this scribe review.

## Focused evidence checklist

For each arm, establish setup succeeds: in-tree unchecked CheckBox, `Ready` Label, focus owner is the CheckBox. Check observations after an awaited frame at every edge, not just after the pair:

| Observation | Checked state | Connected signal receipts / Label | Disconnected receipts / Label |
|---|---|---|---|
| Before action 1 | false | `[]` / `Ready` | `[]` / `Ready` |
| Press 1 only | false | `[]` / `Ready` | `[]` / `Ready` |
| Release 1 | true | `[true]` / `On` | `[]` / `Ready` |
| Press 2 only | true | `[true]` / `On` | `[]` / `Ready` |
| Release 2 | false | `[true,false]` / `Off` | `[]` / `Ready` |

The connected row should exit 0 with its declared success signature. The disconnected row should complete both state transitions and then exit 2 specifically at the intended final missing-signal assertion; it must not fail setup or an earlier state checkpoint. Runner diagnostic matching should distinguish expected-negative diagnostic from any setup/runtime error. These synthetic focused `root.push_input(ui_accept)` observations do not establish physical-key, pointer, rendered, accessibility, or real-user behavior.

## Replay / raw comparison checklist

- Named non-author verifier records exact full default-path command and exit status, Godot version, raw output, scratch location, and source hashes before/after; copies raw receipt byte-identically to `corpus/lessons/r33-checkbox-edge-verifier.json` and documents equality/hash.
- Compare all r32 and r33 raw result maps by case: preserve every non-CheckBox `(verdict, actual_exit, signature)` tuple. Preserve row count (56 aggregate) and all 45 ordinary / 2 mutant / 9 opt-in classifications; permit only the two intended CheckBox signature changes. Do not equate expected-negative inner exit 2 with a battery failure.
- Record the separate fault-injection outer result and intentional inner classifications separately from the seeded battery; likewise isolate any scratch omission/sabotage result from tracked evidence.
- A useful scratch omission of release 1 must pass setup and press 1, then fail at the intended release-1 state assertion. It is corroborating sensitivity evidence only; the connected and disconnected tracked arms plus non-author replay establish the behavior.
- Confirm source hashes stable during verifier replay; report any adverse evidence rather than overriding it.

## Verdict boundary

Depth improves only if the non-author real-Godot replay confirms press-only prior state/receipt/Label and release-only next state/receipt/Label across both actions, disconnected control completes both state changes, scratch omission fails at the intended checkpoint, and all baseline tuples/counts remain stable. Coverage and calibration should remain unchanged; any regression is a hold/harm, not hidden by aggregate PASS. Current fixture (hash above) still checks only after full pairs, and no r33 raw exists at this review point; therefore this artifact itself supports no r33 axis verdict. No constants changed by this scribe. No engine/editor/seeded-control edits, commit, push, or merge.
