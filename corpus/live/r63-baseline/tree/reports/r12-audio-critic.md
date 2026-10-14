# Round 12 audio fixture — adversarial review

Review scope: read-only review of the Round 12 audio fixture design/evolving code. No implementation files or seeded fixtures were edited. At review time, `.shokunin/game-dev-2d/LOG.md` contains the declared claim, but there are no `audio_*` fixture files, no Round 12 audio reports, and no audio lesson artifact in the workspace. Therefore this is a provisional review of the declared assertion, not a code-level verification; do not treat absent evidence as a pass.

## Evidence required for the claim

The claim is specifically that a headless `AudioStreamPlayer` starts playback and advances playback position for generated in-memory audio, and that a no-play control fails the same bounded assertion. Output text, a successful `play()` call, `stream` metadata, stream length, or an arbitrary printed marker do not prove either runtime fact. Capture the player’s live `playing` state and `get_playback_position()` from the running Godot process, and require position to increase over a bounded interval after starting playback. Preserve raw observations and process exit/error data in the lesson artifact.

## Main falsification risks

- **Setup failure masquerading as a valid negative:** If the negative case has a missing/invalid stream, bad scene, parse/runtime error, or player not in-tree, then the same playback assertion will fail for the wrong reason. Both variants must first establish the same successful fixture setup (valid generated stream, player attached/in-tree, no script/parse/setup errors); only the negative should omit the playback-start action. Require clean completion and explicit setup evidence in both cases. A negative meta-probe should pass only when positive reaches the assertion and negative fails that exact assertion, not when either process fails to initialize.
- **Wrong evidence source:** Stream length/metadata is static and may be positive without a playback voice. A printed `playing=true` supplied by fixture code is not enough unless it is obtained from the actual player at runtime; preferably record structured samples directly from `player.playing` and `player.get_playback_position()` before/after the wait. Require the positive sample to show `playing` and a strictly advancing position, not merely a single nonzero position.
- **Negative assertion drift:** Reuse one assertion/check function and same timeout/sampling logic for both variants. Demonstrate that removing only `play()` makes that assertion fail while setup and process remain otherwise valid. Avoid a negative that exits early or has a different expected exit/signature path.
- **Headless audio backend:** Godot headless may use a dummy/null audio driver or lack a physical device. That can still permit software playback state/position advancement, but backend behavior is environment/version dependent. Record Godot version, audio driver/device configuration, and relevant runtime output. If the position does not advance under the selected backend, report HOLD/unsupported in this environment; do not substitute metadata or a print marker as proof.

## Claim boundary

Even a sound positive result demonstrates only Godot playback state/position advancement in this headless fixture. It does **not** establish audible output, speaker/device delivery, audio quality/mixing, user perception, production game integration, or asset rights. No audible-output claim is supportable from a headless state probe.

## Verdict

**Not yet adjudicable from available artifacts.** The declared test is a reasonable coverage target only if it proves live playback state and increasing position, with a setup-valid no-play control failing the identical assertion. Re-review the implementation and raw lesson after they appear; any output-only/metadata-only proof or setup-failure negative should be rejected.
