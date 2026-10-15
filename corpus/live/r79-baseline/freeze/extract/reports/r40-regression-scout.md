# Round 40 regression scout — prior HSlider and battery caveats

Read-only review of the r40 paired no-focus repeat proposal, prior r37/r39 reports, current slider fixture, and runner. No Godot run, fixture/runner edit, or seeded-control change. This report is the only write.

## Prior HSlider evidence and r40-specific checks

- r37 measured the shorter no-focus `ui_right`/`ui_left` parsed-action sequence in Godot 4.7.2. With the HSlider in-tree, signal connected, and no `grab_focus()`, GUI focus owner stayed null; each action left value 5, receipts `[]`, and Label `Value 5`. That evidence is for the earlier two-action sequence only; it does not establish r40's seven-edge history.
- r39 measured seven fresh synthetic `InputEventAction` edges with the focused connected slider: right press, right press, right release, left press, left release, left press, left release. Values were 6,7,7,6,6,5,5; receipts accumulated `[6,7,6,5]`; the callback-driven Label followed each numeric change. This is deliberate synthetic input plus frame yields, not OS auto-repeat or physical keyboard timing.
- Current fixture's `--repeat-right` path asserts focus before every edge, but does not itself assert focus-absence behavior. Existing `--no-focus` path is a separate shorter sequence. For the proposed combined mode, verify focus owner remains not the slider before every one of the seven events and value 5 / receipts `[]` / Label `Value 5` after every edge. Retain the connected callback and label consumer; only report the intended expected-negative exit 2 after all seven assertions, not early. If any event acquires slider focus or changes state, HOLD/correct the claim.
- The current fixture has no combined `--repeat-right --no-focus` arm and runner has no paired row yet; do not count the r37 row as proof of the new history. A focused positive repeat row already exists and should remain unchanged.

## Export, timeout, and fault-injection boundaries

- Export cases have their own 60-second timeout, distinct from the general fixture bound; export-launch startup is separately bounded at 5 seconds. Earlier evidence records that relative export-target paths failed in this environment while absolute paths passed, and an explicit-relative `--runs` path hit `StopIteration`. Do not generalize export readiness or portability from slider evidence.
- Timeout evidence is bounded to the runner's particular direct-child hold/timeout/kill/reap probes and constants; it does not establish descendant cleanup or generic timeout safety. No timeout behavior should be changed or inferred by this calibration move.
- Fault injection is separate from real fixture results. Its outer battery PASS can include deliberately failing inner timeout/unrelated-error cases, and those must not be described as clean inner runs. Keep expected-negative slider classification tied to the exact expected diagnostic plus exit code, not exit 2 alone.

## Bounded review

The r40 contrast is well-motivated by r37's shorter focus-absence evidence and r39's focused seven-edge evidence, but the combination is not yet measured by those records. Require the first real Godot scratch to exercise the exact seven-edge route with the callback/Label connected and no focus grab. This read-only review makes no axis verdict and does not endorse a change without that measurement and the parent-requested replay. Scope remains headless synthetic focus routing, not rendered/pointer behavior, OS/window focus, physical input timing, accessibility, production behavior, or general slider assurance.
