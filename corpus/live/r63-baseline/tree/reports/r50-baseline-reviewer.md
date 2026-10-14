# Round 50 baseline reviewer report

## Result: immutable r49 baseline verified; release hypothesis is causally plausible

I was read-only for tracked fixture/runner files. I copied the fixture project into my unique bounded scratch directory `/tmp/r50-baseline-reviewer-f7a85fb083` and used Godot `4.7.2.stable.arch_linux.ed1daf0bf`.

I checked the separate r49 author and non-author raws: `corpus/lessons/r49-fresh-after-reconnect-verifier.json` (author) and `corpus/lessons/r49-fresh-after-reconnect-non-author.json` (non-author). Each records PASS with 74 entries (63 ordinary, two mutants, nine opt-ins); their 65 tuple-bearing records are identical. Raw SHA-256: author `298a17bcee81020e6a7eb22bb917e65bc8c0d189fb59a3089e49e8d78555f12a`, non-author `45eace51453b307458cc441c85aa8ebe2e6a63c584f6187fbc2f043f578a2751`. These remain distinct evidence sources; the author raw is not independent verification.

For immutable baseline comparison, r48 non-author raw `corpus/lessons/r48-late-reconnect-verifier.json` has 73 entries and 64 tuple-bearing results. The r49 non-author raw has 65 tuple-bearing results: all 64 prior `(case, verdict, actual_exit, signature)` tuples match exactly, plus the single PASS exit0 r49 press-after-reconnect tuple. The r49 raw confirms the ten edges end `...,4,3`, receipts `[6,3]`, Labels `Value 6,Value 3`; its separate r48 negative still ends after nine checks with expected exit2.

I independently replayed both existing modes from my own scratch. R49 `--repeat-right --second-focus-restore --press-after-late-reconnect` returned 0 and printed `values=6,6,6,5,5,5,5,4,4,3 receipts=6,3 Labels=Value 6,Value 3`. R48 `--repeat-right --second-focus-restore --reconnect-after-final-left` returned 2 after nine checks, with values `6,6,6,5,5,5,5,4,4`, receipts `[6]`, Label `Value 6`, connected true, and its expected unique late-reconnect diagnostic.

This supports the precise proposed edge10 test: the edge9 press already has a matching release edge10 in the r49 action sequence? It does not: r49's final edge9 is a fresh `ui_left` press; adding a release immediately afterward while slider owns focus and callback remains connected should leave numeric3, receipts `[6,3]`, Label `Value 3`. This is a hypothesis from the event model and baseline, not an observed r50 scratch result. No r50 code or mode was added/run by me. The executor should test it in causal scratch before any tracked edits, then assert focus and callback state before every edge and numeric/full receipts/Label after every frame, as requested.

No r49 raw or branch should be replaced; use additive mode/row and preserve the r49 positive ten-edge and r48 negative nine-edge cases. My evidence is limited to headless Godot synthetic parsed actions and process frames. It says nothing about physical input, OS key repeat/timing, rendered/pointer UI, accessibility, production, or consumers of unchanged edges.
