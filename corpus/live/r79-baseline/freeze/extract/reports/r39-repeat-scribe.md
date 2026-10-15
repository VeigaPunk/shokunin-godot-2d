# Round 39 repeat-scribe report — baseline, raw evidence, and admission checklist

## Declared scope
Read the standing brief and Round 39 LOG declaration. The candidate is a second deliberate, fresh synthetic `ui_right` pressed=true event before release, then two `ui_left` press/release pairs on the same focused HSlider. Required connected history is values `6,7,7,6,5`, cumulative receipts `[6,7,6,5]`, with signal-driven Label states corresponding to each value; the disconnected pair must traverse the same numeric history with `receipts=[]` and Label `Value 5`. Its intended negative diagnostic must occur only after every edge assertion. This is a synthetic event sequence, not OS auto-repeat or a physical timing claim.

## Read-only baseline and raw corpus
- Current committed baseline observed: `992e2df5ae3d8beb74c64f9dfe97558e3b1b5bc1` (`game-dev-2d r38: report HSlider edge depth`). The working-tree LOG is already modified for the Round 39 declaration; it is not part of this committed baseline.
- Round 38 named-verifier raw: `corpus/lessons/r38-edge-verifier.json`, SHA-256 `c1c81ed4d469ec4bde4e7525f50cd41a9ba73168664c07d7de91cf2125c56c83`; 62 results, verdict PASS. R38 report records 51 ordinary + 2 mutation + 9 opt-in results and all 62 `(case, verdict, actual_exit, signature)` tuples match r37. Its raw shows existing connected `slider_adjust` signature `values=6,5 receipts=6,5 Labels=Value 6,Value 5`, plus existing disconnected and no-focus negatives; it contains no Round 39 repeated-press arm.
- R37 comparison corpus: `corpus/lessons/r37-focus-verifier.json`, SHA-256 `aa14fc53eadb717b3f66475a22c424961cceb0257b60cd0e6332dd421da09b05`.
- Tracked fixture and runner are not modified in the present working tree. R38 named-verifier report recorded fixture SHA-256 `093ae11de4e854ffb954ce5158133be2c3d5f890c8fef738990190a9bcfcd036` and runner SHA-256 `69d94dd63f0a32769731d7942b831a3d7e7ad84a5ce571153df2abe231a1914f`.
- This is read-only corpus/report inspection, not a new Godot measurement or battery replay. No engine/editor run, seeded control change, commit, push, or merge.

## Admission checklist — pending Round 39 evidence
- [ ] Fresh Godot scratch measurement confirms exact event order, focus, each post-frame value, receipts, and signal-driven Label state for connected arm.
- [ ] Paired disconnected arm confirms same numeric history, empty receipts, Label `Value 5`, and intended negative only after all edges.
- [ ] Release is measured to remain at 7; final left press/release pairs return to 5.
- [ ] Executor changes, if causal, stay limited to `slider_adjust.gd` and `run_battery.py`; no extra seed/corpus mutation.
- [ ] Named non-author verifier replays intended fixture modes and full default-path command; confirms prior 62 result tuples unchanged and expected two new rows (53 ordinary / 64 full), if the proposed row design is implemented.
- [ ] Raw verifier result and report are retained; any sabotage fails at the specific affected assertion rather than false-PASS.
- [ ] Scope wording says deliberate synthetic press events only, with no OS auto-repeat/physical-timing claim.

**Current status: NOT ADMITTED / HOLD pending the first real Godot measurement and verifier evidence.** The candidate is consistent with the prior critic's observation that an extra pressed=true can advance 6→7, but that earlier observation is not evidence for the complete Round 39 sequence, paired disconnected behavior, receipts, or Labels. If the fresh measurement contradicts any expectation, correct the claim or HOLD before implementation/admission. Provisional axis intent is depth improved; coverage and calibration unchanged; no final axis verdict until full evidence is independently replayed.
