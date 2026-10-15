# Round 7 — fault classification checks

Reproduce on Godot 4.7.2: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection` → meta PASS in independent `r7-fault-verifier.json`; and `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` → 25/25 in independent `r7-normal-verifier.json`. Named non-author verifier `r7-fault-verifier`, report `.shokunin/game-dev-2d/reports/r7-fault-verifier.md`.

| Injection / observation | Correct machine decision | Limit |
|---|---|---|
| Child prints start marker then sleeps 30s; shared subprocess helper times out at 0.25s, actual_exit null and TIMEOUT error | inner FAIL; meta check PASS in ~0.3s | proves this bounded fault only, not every descendant process |
| Expected negative diagnostic, exact exit 2, no extra ERROR | inner PASS | intended negative error is not over-rejected |
| Same negative signature and exit 2 plus unrelated `ERROR:` line | inner FAIL | case-owned expected error lines; cannot prove all forged diagnostics impossible |
| Verifier sabotages shared classifier to always true in disposable `/tmp` copy | meta FAIL / exit 1 | `/tmp` copy is not a committed evidence artifact; reproduce by changing a scratch copy of classifier only |

`run_process` and `classify_process` are shared by normal script cases and fault mode. Normal known negatives have explicit allowed diagnostics; script/parse errors and unrelated ERROR lines fail. The 25-case normal suite stays PASS with no seeded-file changes. This tests failure classification, not product behavior or full process-tree hang handling. No timeout was globally changed for normal cases: Godot scripts remain 8s, export 60s, fault-only 0.25s / 2s.
