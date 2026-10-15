# Round 37 focus-absence scout

## Measurement

Ran a paired scratch probe with `/usr/bin/godot` **4.7.2.stable.arch_linux.ed1daf0bf** using the r36 scene/setup and identical `value_changed(float)` → receipt/Label wiring. Each arm began in its own headless Godot invocation with a fresh slider at 5 (range 0..10, step 1), and received fresh parsed `InputEventAction` ui_right pressed/released then ui_left pressed/released, each separated by process frames. The focused arm alone called `grab_focus()`. Focus owner was printed before both actions. Raw outputs: `corpus/live/r37-focus-scout/focused.stdout.txt` and `unfocused.stdout.txt`; probe: `focus_pair.gd`.

- Focused: before right and left owner was the HSlider (`has_focus=true`). After right: value 6, receipts `[6.0]`, Label `Value 6`; after left: value 5, receipts `[6.0, 5.0]`, Label `Value 5`.
- No `grab_focus`: before either action owner was `<Object#null>` and `has_focus=false`. After right and after left: value 5, receipts `[]`, Label `Value 5`.

## Conclusion

Observed behavior supports the proposed focus-absence control on Godot 4.7.2: focus absence prevented both action-driven slider adjustments, while same wiring positively observed the focused adjustment. The scratch establishes feasibility and the claimed control distinction; fixture integration and the intended post-two-actions exit-2 assertion remain for executor/verifier. No tracked fixture or runner edited.
