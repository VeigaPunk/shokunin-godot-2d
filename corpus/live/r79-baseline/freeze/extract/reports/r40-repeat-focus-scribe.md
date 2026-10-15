# Round 40 repeat/focus-absence scribe — raw, verdict, and scope checklist

## First real-Godot scratch measurement

Independent scratch under `corpus/live/r40-repeat-focus-scribe/`, Godot `4.7.2.stable.arch_linux.ed1daf0bf` headless. Reused the r39 probe wiring: in-tree HSlider (0..10, step 1, initial 5), connected `value_changed` callback appending receipts and updating Label, and seven newly parsed `InputEventAction`s each followed by one `process_frame`. The only intended contrast was focus: positive called `grab_focus`; `--no-focus` did not.

Raw focused positive (`--repeat-right`), exit 0:
```
SETUP focus=true owner=@HSlider@2:<HSlider#26424116681> value=5.0
EDGE ui_right true value=6.0 receipts=[6.0] label=Value 6 focus_owner=@HSlider@2:<HSlider#26424116681>
EDGE ui_right true value=7.0 receipts=[6.0, 7.0] label=Value 7 focus_owner=@HSlider@2:<HSlider#26424116681>
EDGE ui_right false value=7.0 receipts=[6.0, 7.0] label=Value 7 focus_owner=@HSlider@2:<HSlider#26424116681>
EDGE ui_left true value=6.0 receipts=[6.0, 7.0, 6.0] label=Value 6 focus_owner=@HSlider@2:<HSlider#26424116681>
EDGE ui_left false value=6.0 receipts=[6.0, 7.0, 6.0] label=Value 6 focus_owner=@HSlider@2:<HSlider#26424116681>
EDGE ui_left true value=5.0 receipts=[6.0, 7.0, 6.0, 5.0] label=Value 5 focus_owner=@HSlider@2:<HSlider#26424116681>
EDGE ui_left false value=5.0 receipts=[6.0, 7.0, 6.0, 5.0] label=Value 5 focus_owner=@HSlider@2:<HSlider#26424116681>
```

Raw paired no-focus (`--repeat-right --no-focus`), exit 0 for this measurement probe:
```
SETUP focus=false owner=<Object#null> value=5.0
EDGE ui_right true value=5.0 receipts=[] label=Value 5 focus_owner=<Object#null>
EDGE ui_right true value=5.0 receipts=[] label=Value 5 focus_owner=<Object#null>
EDGE ui_right false value=5.0 receipts=[] label=Value 5 focus_owner=<Object#null>
EDGE ui_left true value=5.0 receipts=[] label=Value 5 focus_owner=<Object#null>
EDGE ui_left false value=5.0 receipts=[] label=Value 5 focus_owner=<Object#null>
EDGE ui_left true value=5.0 receipts=[] label=Value 5 focus_owner=<Object#null>
EDGE ui_left false value=5.0 receipts=[] label=Value 5 focus_owner=<Object#null>
```

The scratch measurement confirms the expected setup and all seven state observations. It is observational, not the fixture's expected-negative exit-2 contract; the scout report independently recorded the candidate fixture scratch exiting 2 only after complete checks. No tracked fixture/runner edits were made by this scribe. Their hashes at inspection remain `8cea925f464478943f4a67de0ad8db886c4002a65f3cdf5a0f1444811da28dc9` (`slider_adjust.gd`) and `8f3a03a88e6e2db7777f1e049aa89f476c1e0ec08bca0ba8c05b7f59d47e18a0` (`run_battery.py`).

## Read-only admission checklist

- [x] Real Godot scratch, not a seeded fixture or simulated control.
- [x] Focused positive uses same seven edges; observed values 6,7,7,6,6,5,5, receipts `[6,7,6,5]`, callback-driven Label.
- [x] Paired no-focus setup has owner other than slider before each edge; value 5, receipts `[]`, Label `Value 5` after each edge.
- [x] `value_changed` callback and Label consumer remain connected in both arms; no manual state/signal injection.
- [ ] Executor fixture diagnostic/exit 2 only after seven edge assertions; require exact-runner expected-negative classification.
- [ ] Named non-author verifier replays paired path, full battery, prior 64 tuple preservation, and focus sabotage that proves the negative cannot false-pass.
- [ ] Final source hashes/raw battery and report-last integration evidence recorded by parent.

## Candidate axis verdict and constants (conditional)

If verifier confirms the unchecked items, calibration **improved**: same-wiring focus absence is a measured negative control for the repeat positive's longer seven-edge history. Depth and coverage **unchanged as axes**; no axis harmed if prior battery rows/signatures remain stable. Candidate ordinary count 53→54 and full count 64→65. Prior 64 `(case, verdict, actual_exit, signature)` tuples must remain identical; the single new expected-negative no-focus case exits 2 only after all seven per-edge checks and exact terminal diagnostic. No ordinary slider bounds, step, or focused positive behavior changes are expected.

## Claim boundary

This evidence is limited to Godot 4.7.2 headless synthetic parsed action events separated by one process frame, with GUI focus owner checks, an in-tree HSlider and callback-driven Label. It does not claim OS auto-repeat, physical input or timing, rendered/pointer UI, accessibility, window focus behavior, production behavior, or a general slider guarantee. No engine/editor source, seeded control, or runner behavior was changed by this scribe; no commit, push, or merge.
