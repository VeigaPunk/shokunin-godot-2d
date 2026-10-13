# Round 49 baseline reviewer report

## Result: baseline reviewed; causal tenth-edge scratch confirms the declared behavior

I acted as a read-only baseline reviewer and made no tracked fixture/runner edits. I used a uniquely named bounded scratch copy at `/tmp/r49-baseline-reviewer-e924ea62d1`. Godot reported `4.7.2.stable.arch_linux.ed1daf0bf`.

First, I loaded the immutable r48 raw lesson at `corpus/lessons/r48-late-reconnect-verifier.json`: PASS, 73 result entries, 62 ordinary tuple-bearing rows plus two mutant rows and nine opt-in rows. The matching r47 lesson has 72 entries. Comparing tuple-bearing `(case, verdict, actual_exit, signature)` results from r47 against r48 yields 63 unchanged prior tuples and exactly one new tuple, the r48 late-reconnect expected-negative (`PASS`, actual exit 2, exact `SLIDER LATE-RECONNECT ASSERTION FAILED: expected no retroactive receipt after nine checks`). The source r48 lesson hash is `51b49a574eae48b346028b4998ed33986b82721c63527b126f53936b04b5b0fc`.

I ran the existing unchanged nine-edge mode from my scratch copy with `--repeat-right --second-focus-restore --reconnect-after-final-left`. It completed expected-negative exit 2 after checking all nine edges, with marker `SLIDER_LATE_RECONNECT values=6,6,6,5,5,5,5,4,4 receipts=[6] Label=Value 6 connected=true`. This supports preservation of the r48 branch as currently implemented, but does not test a tenth edge. Output is `/tmp/r49-baseline-godot.out`.

The causal scratch does support the proposed tenth edge: after the existing nine-edge flow and reconnect, the r49 probe should assert slider focus before edge9, inject a fresh parsed `ui_left` press, await a frame, and expect numeric3, receipts `[6,3]`, Label `Value 3`; a following release should not alter that. The baseline is safe for this additive depth claim. I did not edit or author the new branch or battery row.

Prior r44–r48 branches/rows are outside my modification scope and remain untouched by this reviewer. Scope is limited to synthetic parsed events and frames in headless Godot; no claim about OS repeat, physical input/timing, rendered or pointer UI, accessibility, production, generic signal replay, or internal consumers of unchanged edges.
