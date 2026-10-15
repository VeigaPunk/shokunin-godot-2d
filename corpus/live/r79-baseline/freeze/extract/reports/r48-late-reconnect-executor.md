# Round 48 late-reconnect executor — scratch feasibility

Own scratch: `.shokunin/game-dev-2d/corpus/live/r48-late-reconnect-executor/scratch/` (Godot 4.7.2, copied project/fixture; disposable-only edit).

Ran `godot --headless --path . --script slider_adjust.gd -- --repeat-right --second-focus-restore --reconnect-after-final-left`. After nine parsed events and frames, the scratch assertions verified focus owner before every edge; connected before edge0; edge0 numeric6/receipts[6]/Value6 before disconnect; disconnection afterward and through edge7; edge7 numeric4/receipts[6]/Value6 before reconnect; connected again through edge8; edge8 remained 4/[6]/Value6. It emitted the unique terminal `SLIDER LATE-RECONNECT ASSERTION FAILED: expected no retroactive receipt after nine checks` and exited 2, as this is the intentionally expected-negative feasibility harness. Raw output: `r48-scratch.log`.

An initial prototype falsely required disconnected status at edge8 and correctly failed the scratch assertion (`remained-disconnected assertion failed edge=8`); fixed disposable scratch to require connected after edge7 and at edge8, reran successfully. No tracked source changed in this scratch step. This demonstrates the hypothesized bounded behavior; tracked implementation/replay remains pending.

## Tracked additive correction and fresh ordinary replay

Parent flagged the first tracked insertion as malformed: it had placed an `else` fragment rather than a complete standalone mode. That candidate is preserved as adverse development telemetry only; no run from it is admitted. I restored `slider_adjust.gd` byte-for-byte from HEAD, then inserted one complete `--reconnect-after-final-left` branch before the untouched r47 branch. The runner row is additive and its exact terminal diagnostic is allowlisted; all r47/r46/r45/r44 branches and row remain intact.

Direct tracked Godot 4.7.2 invocation exits 2 only on `SLIDER LATE-RECONNECT ASSERTION FAILED: expected no retroactive receipt after nine checks`, after the nine checks; raw `tracked-direct.log`. First fresh ordinary run before allowlisting correctly rejected the row despite matching expected exit/signature, because the terminal ERROR was not yet allowlisted (`ordinary.log`, verdict FAIL) — this was a runner-classification issue, not evidence. After adding exact error classification, fresh ordinary run passes **62/62** with new expected-negative row exit2 and all existing rows PASS; `fresh-ordinary.log` and `fresh-runs/*/verdicts.json`. This is author replay only, not named independent verification.
