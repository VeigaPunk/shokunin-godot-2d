# Round 5 animation/juice adversarial review

## Finding

**Not verifiable from the current checkout.** The Round 5 declaration in `LOG.md` specifies a positive animation probe and a stuck-animation control, but no `animation_*` fixture exists under `corpus/fixtures/`, and no `r5-anim-scout.md`, `r5-anim-executor.md`, or `r5-anim-verifier.md` is present. The battery currently lists no animation cases. Therefore I cannot claim that the positive case is animation-driven, nor that its mutant detects the intended defect. Treat the round's proof claim as pending until the implementation and raw replay are available.

## Adversarial proof criteria

For the positive to prove animation-driven property update (rather than merely a value change):

1. Establish and record the target property's initial value before animation starts.
2. Start the actual `AnimationPlayer`/`Tween` and advance the engine deterministically for a bounded interval, with no test-script assignment to the asserted property after the baseline. The asserted value must be sampled only after that advance.
3. Demonstrate the property track/path targets that node and property; require the value to differ from baseline and match a nontrivial expected intermediate or endpoint value. A mere “finished/playing” flag does not prove a property changed.
4. Ensure no alternate callback, setup code, default property value, or direct assignment can satisfy the assertion. A useful adversarial edit is to remove/rename the property track (or prevent the player from starting) while retaining all test code: positive must fail the property assertion.

For the mutant/control:

- It must preserve the same setup, clock advance, target and assertion, and fail specifically because the property did not animate (e.g. expected-value assertion / explicit test failure), not because the mutant causes a parse/runtime error, timeout, missing resource, or engine warning.
- Prefer a same-script `--stuck` mode that disables playback or uses a deliberately empty/removed property track. Prove that the positive passes and this control fails at the same assertion. Verify runner classification requires the intended failure signature and excludes `SCRIPT ERROR`, parse errors, and warnings as sufficient “detection.”
- Falsify warning-as-proof by injecting an unrelated warning into a passing positive: it must remain a pass; then make the animation genuinely stuck without generating a warning: it must fail. Capture stdout and stderr separately or together in raw JSON so this is auditable.
- Try the direct-assignment mutant: replace the animated property write with a direct assignment to the expected value after the advance. A robust fixture's design/review must expose this bypass; if that mutant still passes, the fixture does not establish causality. Also try a constant/zero-duration track, wrong target path, and playback never started. State the bounded timing assumptions and avoid frame-count dependence where possible.

## Visual and scope limits

Even a sound headless property-track probe proves only that a runtime animation changes an in-memory property under its chosen deterministic advance. It cannot establish rendered pixels, visible frame sequence, smoothness/easing quality, perceived juice, timing under real display refresh, sprite/art quality, audio playback/mix, or production integration. A screenshot/video or render-capture check would be separate evidence; no visual claim should be inferred from headless property values.

## Disposition

No implementation or runner behavior was modified or executed. Re-review the positive and mutant against the criteria above once their fixture and replay artifacts are present; until then the Round 5 animation claim is **unproven**, not a demonstrated failure.
