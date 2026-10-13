# Round 34 baseline reviewer

## Immutable baseline

The requested baseline is HEAD `856ea34f1bf160dd9593576204dca60aa8129c45` (`game-dev-2d r33: report CheckBox edge depth`), unchanged on inspection. The committed fixture tree has 47 files. Its `run_battery.py` SHA-256 is `e584780f2b88c57947cfa723ba8f47dbce01b24d49ce1b0077555d6fff0f38f2`; `checkbox_toggle.gd` is `a9dea80b3b14e0643c4402b4d1a9c709ef836760b4439dcb20c5bb4b7614ec9b`. Committed r33 raw verifier/fault receipt hashes are `72a04ce3a6067b8b9110319284f7ac49399e7795ec11a5e4f2bd7bbe5e268b7f` and `b1b06ef74f44d6ee986f5a6e5e41ca480ff2da7344a5d3bb58bf5f243f3cadcc`, respectively.

## Independent baseline replay

I ran the full r33 default-path command from repo root:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

It exited 0: 56/56 PASS (45 ordinary, 2 mutants, 9 opt-in/probe rows). Radio work was not in that run. I compared every result record's `(verdict, actual_exit, signature)` by case to committed `corpus/lessons/r33-checkbox-edge-verifier.json`; all 56 cases matched exactly, including both CheckBox expected outcomes. New raw run: `.shokunin/game-dev-2d/corpus/live/runs/20261013T052121172062Z/verdicts.json`.

The raw replay also records the expected inner adverse classifications for opted-in probes (e.g. unrelated Godot diagnostic and stream-reject are FAIL classifications inside outer PASS probes); they are not seeded battery failures.

## Scope and disposition

At inspection start HEAD was the immutable r33 commit. During/after the replay, the working tree showed uncommitted `radio_group.gd` and edits to `run_battery.py` (+2 rows plus allowlist) belonging to the separate executor lane. I did not read, edit, stage, or claim those changes, and this report makes no radio behavior or causal-contrast finding. My baseline evidence supports the declared 45 ordinary / 56 full predecessor counts and exact r33 regression comparison only. No engine/editor or seeded fixture changes, commit, push, or merge by this reviewer.
