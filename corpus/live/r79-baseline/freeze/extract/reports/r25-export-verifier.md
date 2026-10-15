# Round 25 independent export verifier

## Scope and result

I independently inspected the working-tree runner diff and replayed the requested battery. The runner change is exactly one export-target normalization: `out_dir / "fixture.x86_64"` becomes `(out_dir / "fixture.x86_64").resolve()`. It does not change the case table, expected exit/signature, export pass predicate, artifact checks, or missing-preset path. Tracked fixture/runner tree hashes (45 files including the runner) were stable before and after the replays. I made no runner or fixture changes.

**Adverse overall result:** the explicit-relative full command exited 1, 49/50 outer cases PASS. `export_readiness` itself passed (exit 0; 73,703,800 bytes; SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`) and `export_preset_missing` passed its expected fail-closed classification (exit 1; `ERROR: Invalid export preset name: Missing preset.`). However `probe_export_launch` failed: that separate launch probe builds its own still-relative export target, yielding the original `Prepare Template: The given export path doesn't exist.` failure. I did not retry or reclassify this failure. The requested raw complete verdict JSON is byte-identical at `corpus/lessons/r25-export-verifier.json` (98,572 bytes; SHA-256 `a5a0d1db4225141f855cd9721c9fcd7ca75ad65b3f469021a726d2e688d6cf53`). Thus the targeted readiness case is fixed in this replay, but the requested 50/50 battery claim is not verified; the separate launch probe remains a counterexample to broad path handling.

A separate ordinary absolute-`--runs` replay exited 0 with 39/39 PASS. Its export output record gives the same 73,703,800-byte hash above and lists `.pck`, `.sh`, `.x86_64`; runner cleanup was recorded and the output directory was empty afterward. The missing-preset negative also passed. This is synthetic fixture evidence only, not production export reliability.

## Prior path evidence and attribution

The pre-fix relative-versus-absolute adverse evidence is consistent across `reports/r25-pair-reviewer.md`, `reports/r25-export-scout.md`, and `reports/r25-export-critic.md`: relative `--runs` battery cases failed with zero-byte/no product and the missing export-target diagnostic; absolute cases passed with matching size/hash. Pair-reviewer reports alternating matched full batteries (relative FAIL 2/2, absolute PASS 2/2); scout reports direct Godot target-path contrasts including mixed project/target forms; critic independently documents the battery contrast and target-isolation follow-up. My relative battery readiness row now passes while its additional, separately implemented export-launch probe fails on a relative target, which supports the narrow mechanism while demonstrating the fix is not global across all export call sites.

The requested baseline-scout report is absent. LOG telemetry says that child reported identity confusion (believed it was executor) and would not author the scout artifact; author attribution for the runner edit is uncertain. I therefore verify the observed diff and behavior, not authorship.

## Fault injection and artifacts

Separate `--fault-injection` command exited 0. Its raw JSON is preserved as `corpus/lessons/r25-fault-verifier.json` (1,153 bytes; SHA-256 `68dbd098c882a2d09e688568201fbc335138d1553f5c8a909a6ff88e964d8620`): timeout and unrelated-error injected cases were classified FAIL; clean expected-negative passed.

Compact exact commands, cwd, exits, signatures, artifact records, diff, and hash checks are in `corpus/lessons/r25-export-pair-verifier.json`. No binaries were copied. The full requested relative command included all listed flags and `--probe-failing`; its supplemental Godot-error unrelated and stream-reject probe rows are also FAIL as recorded in the raw JSON.

**Verifier assessment:** narrow export-readiness normalization and missing-preset behavior are independently reproduced; full 50/50 requested outer PASS is **not** reproduced. Do not claim general or production export reliability. No runner/fixture/LOG edit, commit, push, or merge.
