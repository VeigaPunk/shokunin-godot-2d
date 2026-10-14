# Round 33 immutable r32 baseline review

## Baseline identity

I reviewed the immutable current `HEAD` `11ab08294c27dfdc7e9d18878f84c16f63c431e1` (`game-dev-2d r32: report CheckBox coverage`), whose parent is `af5e22f9c967738870b778d30b0f36d7437dfcab`. The round-32 full-path raw receipt is `.shokunin/game-dev-2d/corpus/lessons/r32-checkbox-verifier.json`, SHA-256 `7f12c3a1f69adab2098d92dd23825f3905239d7953206fbdc2cd4f49378cd245`. It contains 56 result records, all PASS: 45 ordinary rows, 2 mutants, and 9 opt-in/probe rows (45 + 2 + 9 = 56). This is the declared r33 before-state: **45 ordinary / 56 full**.

Committed HEAD source hashes (SHA-256):

- `.shokunin/game-dev-2d/corpus/fixtures/checkbox_toggle.gd`: `a6971f7e1089177e3e7ed8923e95aa8dd1021bf0ac8c1a4856a257d3665f79bb`
- `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py`: `f03ba367c7311c83e4621f835b5a41135a6f96b0ee7023d76b317c828d0d0250`

The fixture and runner in r32 `HEAD` hash to those exact values. No r33 candidate mutation was reviewed or executed; that is outside my baseline-only assignment. The working-tree `LOG.md` is modified by the parent, but the committed fixture and runner at `HEAD` are the immutable baseline.

## Existing CheckBox behavior in baseline

The r32 receipt includes these two CheckBox cases:

- `checkbox_toggle`: PASS, exit 0, signature `PASS checkbox_toggle states=[true,false] toggled=[true,false] labels=[On,Off]`.
- `checkbox_toggle_disconnected`: expected-negative PASS, actual exit 2, signature `ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got []`.

The connected fixture currently sends each focused `ui_accept` press/release pair and only then asserts the resulting state, signal receipt, and Label. The committed behavior does **not** assert the press-only intermediate state, receipt list, or Label. Thus r33's proposed press-edge observations are unmeasured relative to this baseline; whether they pass is for the assigned implementation and non-author replay to establish.

## Signature baseline comparison

Compared raw result tuples `(case, verdict, actual_exit, signature)` against the committed r31 verifier receipt, all 45 r31 signature-bearing result cases are unchanged in r32. The two additional signature-bearing records are exactly the connected and disconnected CheckBox cases listed above. This confirms r32's 47 signature-bearing records (45 predecessor + 2 additions); the remaining records are aggregate probe receipts without per-case exit/signature tuples. No candidate r33 outcome is claimed.

## Disposition

This is a baseline identification only, not a Godot replay or verification of r33 edge semantics. Baseline hashes and counts match the Round 33 LOG before-state. I wrote only this assigned report; no fixture/runner edit, engine/editor use, commit, push, or merge.
