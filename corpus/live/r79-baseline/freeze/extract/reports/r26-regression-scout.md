# Round 26 regression scout — export, stream, signal, and fault coverage

Role: read-only regression map. No fixture/runner changes or live executions; no engine/editor or seeded-control mutation. This report is limited to prior artifacts and source inspection.

## Export-relative targets

The prior r25 failure was not merely relative `--runs`: two distinct Godot export call sites received relative output targets. `r25-export-verifier.md` records the first named non-author replay at 49/50: export-readiness and missing-preset passed, while both positive and missing-startup launch exports failed with `Prepare Template` missing-path output. `r25-export-launch-adverse.json` preserves that adverse result.

The final runner now resolves both targets before passing them to Godot:

- readiness: `(out_dir / "fixture.x86_64").resolve()`
- launch: `(out_dir / "fixture-launch.x86_64").resolve()`

This is the narrow two-target correction documented by `r25-export-verifier2.md`. Its explicit-relative full replay reports 50/50 PASS, both launch exports generated the expected executable, positive startup was observed, and the missing-startup control did not emit its token; the missing-preset negative remained expected and fail-closed. The earlier 49/50 and historical r16/r24 adverse export records remain adverse; the later replay does not erase or generalize them. Export coverage remains synthetic fixture export/launch, not production/game export reliability or all path/environment failure modes.

## Prior diagnostic coverage boundaries

- **Stream attribution (r19):** paired same-script runs emitted the expected marker to stdout and both exited zero; only reject arm added the unrelated stderr line. The stream probe distinguishes that bounded stdout-marker/stderr-diagnostic pair. It does not classify arbitrary stream layouts, crash behavior, or timeout/process-tree cleanup. `r19-stream-verifier.md` separately records fault injection and its limitations.
- **Signal (r21):** `r21-signal-reviewer.md` observed a same-signature normal exit 7 versus a live direct Godot child terminated by SIGTERM, represented as POSIX return code -15 on this Linux host. This is host-specific signal/return-code evidence, not portable semantics, general crash detection, or descendant cleanup. The named crash verifier independently records the bounded SIGTERM arm.
- **Fault injection:** the recorded `--fault-injection` checks are Python runner-level synthetic faults. Prior verifier reports retain the expected inner adverse outcomes (hang timeout and unrelated error classified false; clean expected-negative classified true) under an aggregate meta PASS. They test detection paths, not a real engine crash, arbitrary hangs, or process-tree termination.

## Round 26 implication

These prior areas are regression context, not evidence for the new slow-positive timeout calibration. A fresh timeout verifier should preserve the existing ordinary/opt-in rows and expected negative outcomes, and independently confirm both export target call sites and the stream/signal/fault records remain unchanged or behave as before. No prior caveat supports claims beyond its stated fixture, host, and bounded probe.
