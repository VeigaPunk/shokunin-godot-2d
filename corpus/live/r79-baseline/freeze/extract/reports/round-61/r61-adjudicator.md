# R61 Sol independent per-axis adjudication — tracked spontaneous-crash classification

**Verdict: ADMIT the bounded R61 coverage move.** Coverage **improved locally**; depth **unchanged**; calibration **unchanged**. No scoped axis is harmed. This verdict accepts tracked classification of the *exit-shape* of a spontaneous crash (−6 SIGABRT + own `ERROR:` marker → PASS under a scoped allowlist; −9 SIGKILL → PASS unmodified) plus in-band reclassification discriminations — **not** crash-origin detection, signal provenance, or production crash handling.

Pinned work adjudicated: `b95d180` (clean-before `3ee05ff`). Worktree clean otherwise.

## The declared claim (as briefed)

One **coverage** move: land the r60-identified zero-runner-change path as a tracked surface — spontaneous `OS.crash` (−6 + `ERROR:` marker) and self-`OS.kill` (−9) rows classifying True, with discrimination arms proving expected-mismatch and missing/wrong allowlist still reject, while all prior classification behavior stays untouched.

## Landed work

- `corpus/fixtures/spontaneous_crash_probe.gd` (new; executable content byte-identical to the twice-measured r60 scratch probe, sha `8d4c5b43…`; header comment is the only delta).
- `run_battery.py` **+43/−0** additive: 2 CASES rows (`crash_spontaneous_sigabrt` −6, `crash_self_sigkill` −9), one `expected_errors` exact-match entry `("ERROR: r60 spontaneous crash probe",)` scoped to the sigabrt case, one unconditional meta row `probe_spontaneous_crash_classification` re-classifying already-captured outputs under four mismatched expectations — zero extra Godot invocations.
- **Critic-driven integration correction** (applied by parent before the work commit, verified in-run): `crash_meta_ok` additionally requires the crash `ERROR:` marker be present in captured output — the `expected_errors` allowlist *forgives* unallowlisted lines but never *requires* the marker, so a markerless external-signal −6 would otherwise pass the meta's intent.

## Evidence audited (this adjudicator's own runs)

- Own seven-flag battery: `corpus/live/r61-integration/runs/20261013T221715829028Z/verdicts.json` → **PASS 92/92**; `crash_spontaneous_sigabrt` −6 PASS, `crash_self_sigkill` −9 PASS, `probe_spontaneous_crash_classification` PASS with all four `discriminations` true and the marker clause engaged (marker present in the captured output).
- Diff audit: `git diff HEAD~2 HEAD -- corpus/fixtures/run_battery.py | grep -c '^-[^-]'` → 0 removed lines; `classify_process`/`run_process`/`classify_streams`/`classify_audio_process` byte-identical (sha `749fa0607e…` preserved), runner sha `42104d95…`→`3bb29044…`.
- Frozen baseline `r61-baseline`: `git archive HEAD` standalone replay → **89/89 PASS**, runner byte-identical, 0 field mismatches vs `corpus/lessons/r59-audio-non-author.json` on the 7-field tuple — before-state exact.
- Non-author verifier `r61-verifier.md`: independent seven-flag replay → **92/92 PASS**; 0 mismatches on all 89 prior rows vs the r59 lesson JSON; forgery spot-checks — ast-extracted `classify_process` on captured sigabrt output + expected −6 + empty allowlist → False; markerless −6 forged record → committed `crash_meta_ok` → False (the correction works); signature-missing → False. Fixture executable content byte-identical to the r60 scratch original. Secrets scan clean.
- Critic `r61-critic.md`: demonstrated concrete forgeries (external `kill -4/-6/-11` → −6 classify True even with empty allowlist; forged-marker + external −6 passes) — establishing the claim boundary: the surface classifies **−6/+marker exit-shape**, not "detects spontaneous crashes"; signal origin remains unprovable from `returncode` (r60-retained UNKNOWN, now demonstrated). All designed rejects confirmed (extra unrelated ERROR, prefix-extended forged ERROR, crash-without-marker, SIGTERM −15, −9-under−6, `quit(134)`, `assert(false)`→TIMEOUT, stack overflow→exit 1). Exact-match (not comma-prefix) allowlist confirmed by measurement.
- Boundary `r61-boundary.md`: probed the r62+ surfaces — `run_process` is plain `subprocess.run`, **no process group**: a pipe-inheriting descendant makes timeout a pipe-EOF wait misattributed to child liveness; SIGKILL hits the direct child only (descendant orphans to user systemd); startup-margin knee at delay ∈(7.5,7.6] under bound 8. Recorded as next-round candidates, not this round's scope.
- Simplifier: diff is minimal — measured that the CASES signature field cannot carry the crash class (`unrelated_errors` rejection is orthogonal to signature); named dead-weight `expected_errors` empties (pre-existing, left alone); `__pycache__` stray cleaned at integration.
- Reviewer: full r60 audit — zero disagreements on every measurement; all cited hashes resolve (canonical-repo lineage note: worktree-repo SHAs from pre-extraction don't resolve canonically, same class of pointer defect as audio's r61 — content verified faithful).

## Discrepancies and evidence-quality notes

- Work commit sweep includes seat scratch under `corpus/live/r61-*` (lane convention); `r61-baseline/tree` (679M frozen checkout) deliberately left untracked — regenerable, and `runs/` receipts are gitignored by design.
- The meta row re-classifies *captured* outputs by design; the marker-presence clause + exit/verdict pinning is the mitigation (verified by the non-author spot-check). `-6` provenance rests on output evidence per the row's own `bounded_claim`.
- Verifier noted HEAD~1 is an unrelated housekeeping revert between r60 and r61 — the coverage diff is strictly additive regardless.

## Per-axis judgment

| Axis | Judgment | Basis and limit |
|---|---|---|
| Coverage | **Improved locally** | 89→92 tracked rows; a previously-scratch-only behavior class (spontaneous −6/+marker, self−9, and four mismatch-rejection arms) is now a durable battery surface with zero prior-row drift (89/89 fields identical). |
| Depth | **Unchanged** | No mechanism claim advanced; boundary's tree-timeout/startup findings are next-round candidates. |
| Calibration | **Unchanged** | Classifier untouched byte-for-byte; the new surface calibrates *what the runner accepts*, not the classifier itself. |

## Learning trends

- **Expansion**: improved — a new tracked behavior class where only probes existed.
- **Quality**: improved — critic-found forgery gap was corrected at integration and re-verified; baseline frozen-replay is byte-exact.
- **Discernment**: improved — admitted (92/92 incl. marker clause) and rejected (empty-allowlist/markerless/wrong-allowlist forgeries) both externally spot-checked.

## Bounded limits

Linux headless Godot 4.7.2 only; exit-shape classification, never signal-origin proof; single-host crash captures ×2; the `−6` arm's SIGILL→handler→SIGABRT internal path is observed on this build only; no core-capture, process-tree, production-crash-handling, or other-platform claim.

## Reopen conditions

Reopen if: the seven-flag battery stops producing 92/92; any of the 89 prior rows drifts on the 7-field tuple; the meta discriminations regress; a markerless −6 construction passes the meta row; or `classify_process`/`run_process` bytes differ from the pinned hashes.

This adjudicator made no git mutations and no writes other than this report; its evidence run is committed as `corpus/live/r61-integration/`.
