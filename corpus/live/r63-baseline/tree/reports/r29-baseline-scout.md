# Round 29 immutable baseline scout report

Read-only baseline at HEAD `0c8423b2d8ab3607cee1897fb2fb18c12bc1f9e3` (`game-dev-2d r28: report repeated Button depth`). This is the committed r28 state, independent of the current worktree, which has a modified `button_activation.gd`.

## Button fixture in HEAD

`corpus/fixtures/button_activation.gd` SHA-256: `9373e361e4adaf20d6ef012c883799522f700846e672889f589596ad91983c22`.

The committed fixture explicitly calls `button.grab_focus()` before each of two `ui_accept` press/release pairs routed through `root.push_input`. The connected positive checks each step for one `pressed` receipt and label text `Activated 1`, then `Activated 2`. Its `--disconnect-signal` control keeps the action path but fails the first assertion with zero receipts and `Ready`.

`corpus/fixtures/run_battery.py` SHA-256: `c178aea2cfdfd16f31f3c4c0d192ab82988bfd31faba96dc2f053b4ca8d60260`. Its committed `CASES` include 41 ordinary records: `button_activation` and `button_activation_disconnected` are the last two entries. The full r28 verifier raw record is `corpus/lessons/r28-repeat-verifier.json`, SHA-256 `62737006cefb018cba78fa8987ef5a584b26ddfcf55cb1ca5a0568aac4bf27b6`; it records 52/52 PASS (41 ordinary plus 2 mutants plus 9 opt-in probes).

No uncommitted worktree content was used as baseline. This report does not assess the current executor diff or claim focus dependence; it only records immutable HEAD state and artifact hashes.
