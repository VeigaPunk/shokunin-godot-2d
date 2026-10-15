# R59 audio scribe — evidence checklist (not a verdict)

Scope: checklist for the single declared claim in `.shokunin/game-dev-2d/LOG.md` line 569: headless Godot 4.7.2 explicit non-Master `AudioStreamPlayer` bus route resolves while playback is active and advances, with a paired missing/invalid-bus control that causally distinguishes. This report is not a PASS attestation. I did not run Godot, edit fixtures or the battery, or verify any runtime behavior.

## Before execution

- [ ] Preserve the old 87 classifications exactly (76 ordinary + 11 existing opt-in records); capture their identities/results and the runner/fixture hashes before and after.
- [ ] Keep the existing seven opt-in flags and their prior meanings unchanged; run only the exact seven declared flags. Do not add `--probe-audio-warning` or other flags.
- [ ] Use a fresh, unique run-local scratch directory; record Godot version as 4.7.2, exact command, exit code, stdout/stderr, verdict JSON, and hashes. Scratch must not overwrite prior run evidence.
- [ ] Keep all edits within the declared executor exception: `corpus/fixtures/run_battery.py` and a new audio fixture only, after a separate causal scratch experiment. No engine/editor, project, asset, publishing, or unrelated file changes.

## Positive route evidence

- [ ] Construct an in-tree `AudioStreamPlayer` with a generated in-memory stream and set its `bus` explicitly to a real, non-Master bus that exists in the isolated project (e.g. a deliberately created uniquely named bus, if that is the least ambiguous setup).
- [ ] Establish the named bus exists and record `AudioServer.get_bus_index(player.bus)` (or equivalent direct runtime evidence) as nonnegative; also record the player's configured bus string. Avoid treating a default/empty property as proof of explicit routing.
- [ ] After bounded processing, assert the player remains active and playback position advances by the established threshold, while recording before/after values. Preserve the current in-tree and generated-stream setup if reused.
- [ ] Ensure the positive checks the configured bus's resolution, not merely that playback works. State that these are playback state and route-resolution observations, not audible output or mixer fidelity.

## Paired invalid-route control / causal distinction

- [ ] Use the same fixture and bounded observation with only the bus value varied to a missing/invalid name; preserve all other relevant inputs.
- [ ] Observe actual Godot 4.7.2 behavior rather than assuming invalid routes error: record configured property, resolved index, active playback, position movement, exit code, exact diagnostics, and any fallback behavior (including possible routing to Master).
- [ ] Require the control to fail the route assertion for the intended cause. A `-1` index alone is insufficient if the engine silently falls back and the tested assertion never checks resolution; conversely, an engine warning alone is not proof unless the production classifier/assertion turns it into the intended rejection.
- [ ] Demonstrate a causal positive/control difference: valid route accepted; invalid route rejected by the exact route-resolution criterion. If both route to Master or otherwise pass, report the claim as unsupported and do not add a nominal negative case.
- [ ] Keep the control assertion signature specific enough that unrelated errors or a no-play failure cannot masquerade as the missing-bus distinction.

## Battery and regression evidence

- [ ] Add only the minimal positive and paired-control records, preserving the old 87 labels, expected statuses, and case order/meaning. Document expected exit and narrow output signature for each new record.
- [ ] Run the complete battery with exactly the declared seven opt-in flags; show old records are byte/tuple-equivalent as defined by the prior receipt and the two new cases are independently replayed.
- [ ] Verify the current audio playback and no-play cases remain unchanged, and verify runner/fixture hashes for all tracked prior fixtures are stable except the explicitly authorized runner and new audio fixture.
- [ ] Inspect warnings and exit classification for both route cases; retain raw output and verdict JSON. Do not suppress diagnostics or broaden warning handling.
- [ ] Report adverse/failed runs, including any invalid bus fallback, warning, leaked-instance warning, cleanup issue, unexpected positive/control overlap, or old-case drift. Do not discard failed evidence.

## Boundary and disposition

- [ ] Limit any eventual admission to headless Godot 4.7.2 bus-name resolution plus in-memory playback-state evidence.
- [ ] Do not infer audible sound, correct mix/output-device routing, volume/pan/effects quality, production integration, asset rights, or other-platform behavior.
- [ ] Leave verdict axes and PASS/RELEASE language to the integrator after named non-author replay; this checklist itself does not attest success.

Scratch directory reserved for this scribe: `.shokunin/game-dev-2d/corpus/live/r59-audio-scribe/` (no runtime evidence collected).
