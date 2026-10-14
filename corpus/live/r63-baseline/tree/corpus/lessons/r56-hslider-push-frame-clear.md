# R56 — pushed release frame, then direct clear frame (Godot 4.7.2)

## Decision and evidence

| Edge10 substep after ten parsed history edges | `_input` observer releases | Global `ui_left` | numeric / callback receipts / Label | Meaning |
|---|---|---|---|---|
| Pre-edge | 3 | true | 3 / `[6,3]` / `Value 3` | Baseline. |
| Matching `root.push_input(ui_left,false)`, then **one awaited process frame** | 4 | true | 3 / `[6,3]` / `Value 3` | Push delivers observer receipt but retains global pressed state. |
| Direct `Input.action_release("ui_left")`, then **another awaited process frame** | 4 | false | 3 / `[6,3]` / `Value 3` | Direct clear changes global state without a second observer receipt. |

Owner/focus and callback connection remain true at both substeps. The dedicated `--push-frame-then-clear-release` control checks owner/callback before each edge, per-edge numeric/full receipts/Label, both edge10 substeps, and an exact expected-negative exit2 terminal after eleven checks. R55 clear-frame-then-push has the complementary intermediate observer3/action false and same final state. Neither control shows the extra frame is *necessary*: R55 omit-await reached terminal; R56 named replay did not run that sabotage. Omit-push in the exact new branch fails the first observer check; omit-clear fails final pressed-state check; both fail before terminal and classifier rejects.

Named non-author full opt-in `r56-pushframe-non-author.json`: 81/81, all 71 prior r55 tuple-bearing rows exact, nine opt-in classifications stable. Separate `r56-fault-non-author.json` outer PASS with intended inner failures. See `../../reports/r56-pushframe-verifier.md`. Initial executor missing-observer scratch/author timeout, critic wrong pressed guard and verifier scratch redirection/collision failures remain adverse, not PASS evidence. The verifier copied lesson raws once from its unique source runs and verified byte identity; do not overwrite them.

Only synthetic Godot 4.7.2 two-frame substep measurements are established. No HSlider internal consumption, OS/physical input or timing, rendering, pointer/accessibility, production behavior, or generic route provenance.
