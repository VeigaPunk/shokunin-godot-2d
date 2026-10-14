# Round 53 composite-route scribe — read-only causal scratch

## Scope and baseline reviewed

Read `/tmp/mission-game-dev-2d-standing.md`, r53 declaration/wave plan in `.shokunin/game-dev-2d/LOG.md`, r51/r52 raw and lesson evidence, including `corpus/lessons/r51-provenance-non-author.json`, `r52-route-non-author.json`, `r52-fault-non-author.json`, `corpus/lessons/r51-hslider-parsed-release-observer.md`, and `r52-hslider-push-input-route.md`, plus the r51/r52 scribe and r52 named verifier reports. Baseline r52 source hashes remain fixture `eeea197a8a566ecb3fb48c929985d63bd5723796bb54467d24a382c352a31010` and runner `168058fa168917a39a3c561deef2102b93ea10df983cf6c5e30081fb0ca10c4c`; I made no tracked edits.

## Scratch and result

Unique scratch project: `.shokunin/game-dev-2d/corpus/live/r53-composite-scribe/project`; logs `composite.log` and `composite-rerun.log`. The only scratch mutation was edge10 in a copy of the existing push-input branch: after `root.push_input(pushed)` for matching `InputEventAction(action="ui_left", pressed=false)`, call `Input.action_release("ui_left")` in the same frame boundary. Edges 0–9, focus transfers, owner/callback assertions, one-frame waits, numeric/full receipt/Label checks, and the eleven-edge expected-negative terminal were retained. The scratch assertion was adjusted to expect action state cleared, so observed measurements are not inferred from a stale push-only expectation.

Godot 4.7.2 result, exit 2 at existing terminal after all eleven checks:

`SLIDER_PUSH_INPUT_RELEASE values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 observer_delta=1 pressed=false callback_connected=true`

The terminal error was `SLIDER PUSH INPUT RELEASE ASSERTION FAILED: expected no new receipt after eleven checks`. The matching parsed edge10 route in r51 also measured observer 3→4, pressed true→false, numeric3, receipts `[6,3]`, Label `Value 3`, owner/callback valid, and reaches its own expected-negative terminal. Thus this explicit composite route reproduces the measured r51 observer-plus-global-state result in this synthetic sequence despite not using `Input.parse_input_event` at edge10. The causal hypothesis is supported for this bounded composite.

## Recommendation and limits

Scratch supports a dedicated `--composite-push-and-clear` exact expected-negative case as a calibration control, if its branch asserts edge10 observer delta 1 and action state true→false, all existing per-edge receipts/Label/value and owner/callback checks, and reaches a unique terminal only after eleven checks. Runner addition should be exactly one case/allowlist, additive; do not modify paired r51/r52 cases. Named non-author full default/fault battery and exact classification/regression evidence remain necessary before admission. This report is not a battery run or axis verdict.

Scope is only explicit synthetic `root.push_input(matching release)` plus `Input.action_release("ui_left")` in this fixture/frame sequence. It does not establish HSlider internal consumption, OS/physical input or timing, rendering/pointer/accessibility, production behavior, or general input-route provenance. No constants changed; no engine/editor/seeded files changed; no commit/push/merge.
