# Round 50 release-edge critic — adversarial review

## Verdict: bounded scratch supports the stated release-edge hypothesis; read-only

I read the standing brief, the r50 LOG declaration, and the tracked slider fixture and battery runner. I made no tracked edits and ran a unique scratch copy at `/tmp/r50-release-critic-20261013-unique/` using Godot `4.7.2.stable.arch_linux.ed1daf0bf`.

The scratch kept the r49 ten actions and inserted exactly one `ui_left` release immediately after the late-reconnect press (edge10). It asserted expected GUI focus owner and signal connection state before every edge; after each parsed event and frame it asserted numeric value, complete receipt array, and Label. The first scratch attempt exposed a faulty critic-only precondition (`callback connected` was incorrectly expected false before edge0); I corrected this scratch assertion to expect connected at edge0, disconnected edges1–7, and connected edges8–10, then reran. Corrected evidence: all eleven edges passed their state checks; terminal state was value3, receipts `[6,3]`, Label `Value 3`, callback connected. The distinctive `SLIDER_RELEASE_AFTER_LATE_RECONNECT_PRESS` marker appeared only after those checks, followed by the dedicated expected-negative `ERROR: ... expected no new receipt after eleven checks`, with exit code 2. Thus release emitted no additional receipt and did not change value/Label in this run.

## Adversarial checks / interpretation

- The release is a new parsed `InputEventAction` with `pressed=false`, not an omitted edge; it runs only after fresh edge9 press completes and its frame is awaited.
- Owner is checked before each action, including slider focus immediately before both final press and release. Callback is checked before each action, including connected state before edge9/10; transitions are checked after disconnect/reconnect.
- Per-edge full-state expectations include cumulative receipts `[6]` through edge8 and `[6,3]` after edge9 and edge10, with numeric values `...,4,3,3` and corresponding unchanged Label `Value 6`, then `Value 3`, `Value 3`.
- Preserve the r49 positive ten-edge path and r48 negative nine-edge path exactly. For the new runner row, recognize only the new diagnostic with exit2 after the eleven-check marker/state sequence; a truncation/assertion failure must not be accepted as expected-negative.
- My initial failed scratch run was solely a critic precondition bug at edge0 and did not show Godot divergence. The corrected scratch is the relevant result.

This is only synthetic parsed input plus frame evidence in a bounded scratch project. It says nothing about OS key repeat, physical timing/input, rendered or pointer interaction, accessibility, production behavior, or generic signal replay. No tracked fixture/runner edits, battery replay, commit, push, or merge were performed.
