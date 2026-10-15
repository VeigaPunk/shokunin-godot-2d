# Round 37 focus-absence scribe report

## Measurement and raw evidence

Read the standing mission brief and Round 37 declaration in `LOG.md`. Independently ran Godot 4.7.2 headless in the scribe-owned scratch project `corpus/live/r37-focus-scribe/` with a fresh in-tree HSlider (min 0, max 10, step 1, value 5), connected `value_changed(float)` callback updating the same Label form (`Value 5`), and fresh parsed `InputEventAction` press/release pairs for `ui_right` then `ui_left`; no `grab_focus()` call or programmatic value/signal mutation. Raw direct output is recorded in this report; executable scratch source is `focus_absence.gd`.

Actual `gui_get_focus_owner()` was null and `slider.has_focus()` false at setup and before both actions. After each complete action pair plus frame waits, owner remained null; value remained 5, receipts `[]`, Label `Value 5`. The script made its intended negative assertion only after both actions and exited 2. This agrees with independent reviewer and regression-scout measurements. No contradictory focus/action behavior: **not HOLD**.

Focused positive reference is the r36 named verifier: values 6 then 5; receipts `[6,5]`; Label `Value 6` then `Value 5`; r36 raw artifact SHA-256 `ad79ea348031d2ce1048c3fbb105ff8a2b2b60cf966a5445394d30050b8ae2e1`. Its connected consumer wiring and parsed action route are the intended comparator. Existing disconnected r36 row is not the focus counterfactual.

## Read-only baseline and raw/verdict checks

- Declared pre-round baseline: r36 HEAD `e66314d93f498010ec6ca661d84a59a1178b0c18`, 50 ordinary / 61 full rows.
- Baseline tracked fixture SHA-256 from HEAD: `slider_adjust.gd` `1c0850ff6daf74696c19cbe0bd45e66dc1d21e074d4b6b588c59166351576e87`; `run_battery.py` `5e6bc978a5098ac2ef104b378d3641902c8d595ad9fba57058e82abdc31f4b2a`.
- Current fixture differs (working tree already contains a modification); I did not edit it. Runner still matches baseline hash. Do not treat current fixture as immutable r36 baseline; use HEAD or preserved r36 verifier scratch/raw.
- My raw confirms state, focus owner and intended exit location, but is only scratch measurement—not a named non-author battery verifier, full replay, sabotage, or admission verdict.

## Checklist / recommendation

- [x] Same slider range/step/initial value; connected callback and Label consumer.
- [x] Same parsed `ui_right` then `ui_left` press/release actions; no values/signals faked.
- [x] Asserted null focus owner before either action; observed value 5, receipts `[]`, Label `Value 5` after both.
- [x] Negative exit2 occurs after both actions at intended missing-adjustment assertion.
- [ ] Named non-author full replay, prior result-triple comparison, and focus sabotage remain outstanding; no axis verdict/admission claim from this scribe report.

Scope: synthetic headless Godot GUI focus routing only. Not rendered/pointer/physical keyboard, OS window focus, accessibility, production UI, or generic HSlider assurance. No tracked fixture/runner, engine/editor source, or seeded fixture changed by this scribe.
