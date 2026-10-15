# Round 27: headless Button action to Label signal

Sources: `corpus/fixtures/button_activation.gd`, `corpus/fixtures/run_battery.py`, named non-author replay `corpus/lessons/r27-button-verifier.json`, `reports/r27-button-verifier.md`, critic `reports/r27-button-critic.md`.

| Mode | Action and observed state | Decision |
|---|---|---|
| Connected | Button and Label in tree, initial `Ready`; Button focused, `ui_accept` pressed+released through `root.push_input`; one `pressed` callback; final `Activated` | Accept exit 0. |
| `--disconnect-signal` | Same routed `ui_accept`; callback receipts 0, text remains `Ready`; exit 2 intended final assertion | Accept causal negative, not setup error. |
| Critic scratch injected direct callback into disconnected arm | Text `Activated`, receipts 1 despite no signal; spoof passes | Do **not** claim arbitrary edited-fixture resistance. No direct callback exists in tracked source. |

Named full default-path battery 52/52 PASS (41 ordinary, 2 mutants, 9 opt-in), separate fault meta top-level PASS with deliberate inner failures. Four wave-1 leaves were unreachable without reports; their scratch did not support admission. This is headless UI action/signal wiring, not physical/pointer hit testing, rendered pixels, accessibility or production UI.
