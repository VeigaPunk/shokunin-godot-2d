# Round 26 baseline scout — immutable HEAD (read-only)

## Baseline identity

- HEAD: `1e4e9c27fd75a5fcf38200a45891fb9c3064bf8e` (`game-dev-2d r25: report export target calibration`), branch `craft/game-dev-2d-r1`.
- HEAD `run_battery.py` SHA-256: `ab0d0352445113b2ba7f742b57500f97e62b2196411f96fe7f8b594e69cdab41`.
- HEAD `timeout_probe.gd` SHA-256: `e100202690d0101f9df191ec8ed37843d56d6d0217103016abf0148bdb9f47dd`.
- Runner declares 40 CASES tuples at HEAD; timeout remains opt-in (`--probe-timeout`) and adds one meta result rather than an ordinary CASES row.

## Prior timeout evidence at HEAD

- Immutable `corpus/lessons/r22-timeout-detail.json` SHA-256: `79e645231d3ab2e8bbbe823ba416c948e12d1e2cf598e6e17cc10632a8d433ba`.
- Immutable full battery record `corpus/lessons/r22-timeout-verifier.json` SHA-256: `0b19a50f767b7ea4fa2a2b505dc4206cce41536f720e91d254f126afc3e0c675`; PASS, 46/46 then (35 ordinary + 2 mutants + 9 opt-in), with paired classifications `[true, false]`.
- Detail has a same-script normal accept (exit 0, marker observed, true classification) and `--hold-open` reject (marker observed, still running at timeout, timed out at **0.75 s**, `actual_exit=null`, false classification, direct child not alive after cleanup; cleanup SIGKILL exit `-9`). The 0.75 s bound applies to the reject's `communicate`; the clean accept is run through the ordinary bounded runner.
- The earlier critic measured clean startup at 0.394 s, leaving about **0.356 s** under the 0.75 s reject bound (0.75 − 0.394). No deliberate slow-positive existed in this baseline, so this margin was observed—not a demonstrated safe threshold for delayed startup.

This report is an immutable HEAD/hash/count check only; no Godot run or file beyond this report was changed. It does not assess the in-progress r26 edit or verifier result.
