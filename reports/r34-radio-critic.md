# Round 34 RadioButton critic review

**Scope:** Read-only falsification of the proposed shared-ButtonGroup fixture. I wrote only this report and scratch corpus under `corpus/live/r34-radio-critic/`; no tracked fixture, runner, seeded fixture, engine/editor source, or battery state was changed. Scratch runtime used installed Godot 4.7.2 headless.

## Material type/API mismatch

The proposed target class name `RadioButton` does not exist in the installed Godot 4.7.2 GDScript API: a scratch script using `RadioButton.new()` fails to parse with `Identifier "RadioButton" not declared`. This is not an engine failure to excuse or a reason to silently rename the test. Godot's equivalent built-in control pattern here is `Button` with `toggle_mode = true` and a shared `ButtonGroup`; a scratch repro with those controls works. Thus any candidate using that pattern measures grouped toggle Buttons, not an actual `RadioButton` class. The distinction must be made explicit in scope/fixture naming or this round's stated RadioButton claim is unsupported. No runner/fixture exists yet in my inspected checkout, so I did not edit one.

## Scratch observation / adversarial checks

Scratch artifacts: `corpus/live/r34-radio-critic/radio_probe.gd`, `project.godot`. Two `Button`s were given one locally-held `ButtonGroup` (both button_group refs compare equal), set `toggle_mode=true`, A was initially pressed, then after insertion into the tree B and A separately acquired GUI focus. The probe sent ui_accept press and release with a process-frame wait after each edge. Godot reported the measured sequence:

- Initial: both in tree, same group, A=true/B=false, no focus owner.
- Focus B then full action: A=false/B=true; `toggled(bool)` callbacks in exact order `A:false`, `B:true`; Label ended `B`.
- Focus A then full action: A=true/B=false; callbacks appended `B:false`, `A:true`; Label ended `A`.

This falsifies neither group exclusivity nor input routing in that scratch configuration. It does falsify any expectation of only one toggled callback per selection; exact four-entry identity/value order is needed. The first exploratory run with only press and no release showed no transition; the complete action requires the release edge in this headless setup. Focus was absent immediately after insertion but was explicitly transferred and verified before each activation. The test should verify `gui_get_focus_owner() == intended_button`, not rely on group focus behavior.

The local `group` variable plus each control's `button_group` reference remained valid throughout the action sequence; the live identities printed identically and all transitions worked. Retain an explicit same-group identity check to guard accidental group mismatch. A scratch negative variant that deliberately omitted group assignment (not used as battery evidence) is the direct falsifier for a manual property-only implementation: manual state writes can mimic final values, but cannot show actual group-based mutual exclusion under routed focus input and its exact callbacks. The tracked fixture should assert both buttons' complementary states after both actions and must never assign `button_pressed` after setup or call `emit_signal`.

Important subtlety: initial A selection occurred before tree insertion in my probe and generated no recorded callback because connections were made after insertion; this does not measure every setup ordering. Put setup selection before connecting observers, then assert empty receipts, or explicitly test/declare any setup callback. Do not accept a generated expected sequence based on unmeasured order.

## Disconnected consumer and redundancy

I did not run a disconnected tracked consumer because the fixture is not present. For the required paired control, disconnect only callbacks; run both full press/release actions and assert A/B transitions after each, zero callback receipts, and unchanged initial Label. Place the intentional missing-signal failure only after the A action; if it fails after B, the test does not establish traversal of both transitions. The scout/simplifier guidance correctly calls out this requirement. Compare the disconnected control's property trace with connected's trace, not just its final state.

This is behavior distinct from the existing CheckBox fixture: CheckBox tests one independent boolean's edge changes, while a shared group imposes cross-control exclusivity and selecting one emits false for the previous choice and true for the next. It is worthwhile coverage only if implemented as actual grouped toggle controls and appropriately labeled; it is not evidence about a `RadioButton` class absent in this runtime.

## Assessment / hold conditions

No observed failure from manually forced state or a transient group reference makes the core grouped-control probe invalid, but the specific requested `RadioButton` premise is unsupported by the available Godot class API. HOLD a literal RadioButton claim unless executor establishes an actual supported class in the declared target/runtime or parent amends the claim to grouped `Button` controls and treats that as the assigned causal contrast. Also hold if either connected or disconnected variant exits before both complete actions, if focus is not checked for each target, if callback sequence differs from raw observation without explanation, or if direct property assignment/synthetic signal emission replaces input-driven transitions. This probe is finite headless synthetic UI evidence only, not pointer/rendered/accessibility/production evidence.

**Verdict:** The grouped Button behavior is a real causal contrast to CheckBox and scratch measured exact sequence `[(A,false),(B,true),(B,false),(A,true)]`; but the explicit RadioButton-class claim is not supported because `RadioButton` is not a declared Godot 4.7.2 class. No constants changed; no tracked changes made.
