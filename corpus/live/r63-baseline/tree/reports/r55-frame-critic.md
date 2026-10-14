# Round 55 frame critic — explicit synthetic frame gap

- Role: LEAF critic; tracked fixture and runner were read-only. Read the standing mission, LOG round 55 declaration, and r53–r54 reports/lessons. Godot `4.7.2.stable.arch_linux.ed1daf0bf`.
- Unique scratch: `.shokunin/game-dev-2d/corpus/live/r55-frame-critic-scratch/project/`. It is a copy of the committed fixture. Instrumented only the copied `--clear-then-push-release` branch at edge10 to await and inspect immediately after `Input.action_release("ui_left")`, then push the matching `InputEventAction` release, await and inspect again. Edges 0–9, focus transfers, callback disconnect/reconnect, pre-edge owner/connection checks and post-edge numeric/receipt/Label checks were retained.

## Direct two-substep observation

Godot output at the explicit frame gap:

- After clear frame: observer **3**, `pressed=false`, numeric **3.0**, receipts `[6.0, 3.0]`, Label `Value 3`, slider focus owner **true**, value-changed callback connected **true**.
- After pushed-release frame: observer **4**, `pressed=false`, numeric **3.0**, receipts `[6.0, 3.0]`, Label `Value 3`, slider focus owner **true**, callback connected **true**.
- Both substeps retained the edge10 final state requested; crucially, observer advancement occurs only at the second substep. Run then reached the existing exact expected-negative terminal after eleven edge checks (exit 2); no fixture assertion failed.

The same scratch copy with the `--composite-push-and-clear` branch confirms the r53 same-frame push-then-clear path reaches its existing eleven-check terminal (exit 2). r54's committed clear-then-push branch is the matching same-frame control. Prior r54 independent reports directly measured observer 3→4 and the stated state for that control; r53 logs/reports give same-frame push-then-clear outcomes. This critic did not claim a new independent raw lesson receipt for either control. The explicit frame gap therefore exposes a bounded substep distinction from same-frame composites: after clear-only frame observer remains 3, while after matching push frame it becomes 4, although the final measured state matches. It is a directly measured synthetic frame-cadence distinction, not a claim about physical timing or internal HSlider consumption.

## Adversarial / scope notes

The temporary diagnostics are observations only, not new assertions; current branch's existing edge10 observer and final action-state assertions execute after the pushed event, so they cannot by themselves enforce the requested intermediate observer count. If the executor admits this observation, its dedicated case should explicitly assert observer still exactly 3, action false, value 3, receipts `[6,3]`, Label `Value 3`, focus owner slider and callback connected after the clear frame; then after the matching push frame assert observer exactly 4 and the same remaining invariants. Preserve all existing per-edge owner/connection-before-edge and numeric/full-receipt/Label-after-edge checks, and an exact unique expected-negative terminal after the full sequence. Any omitted await collapses the experiment to same-frame ordering; any wrong/mismatched event or assertion moved past final frame fails to test the intermediate claim. The two frame-separated operations are synthetic calls only.

I made no tracked, seeded, engine/editor changes; no constants changed; no commits, push or merge. No inference about HSlider internal consumption, physical timing/input, OS, rendering, pointer, accessibility, production behavior or general route provenance.
