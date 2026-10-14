# r64 Sol adjudicator — game-dev-2d lane, wave `shokunin-train-20261013-w4`

Adjudicator: Sol (parent session), host devin, 2026-10-14. Scope: round 64 declared depth move — test whether a while-live marker read discriminates forged post-death signatures from genuine child signatures (XConnector wave-3 synthesis); additive meta arm only; 96 prior rows field-stable.

## Declared claim (verbatim)

"a while-live marker read discriminates forged post-death signatures from genuine child signatures … the forged release-arm signature lands post-death so the gated read rejects or never observes it … while a genuine child signature still passes; if the gate cannot distinguish … record the falsified outcome with measured timing. Additive only: a new meta probe row; the r63 pinned accepting-boundary row stays byte-stable."

## Measured result

**CONFIRMED — deterministic on this host, with the gate's soundness pinned to its primitive.**

`probe_while_live_signature_gate` (`run_battery.py`, +228/−0): a `selectors`/`os.read` loop over both pipes where the marker is accepted only when `process.poll() is None` at the marker-completing read. Measured: genuine+detach arms accepted (death +66–71ms post-marker); forged release×3 + hold observed **post-death** (~+32ms after `dead_observed_at`) and REJECTED — the gate rejects a *present* marker. 12 discriminations all true; **97/97** battery, prior 96 rows 0-mismatch.

**Primitive is load-bearing (measured, not stylistic):**
- `os.kill(pid,0)`/`pid_alive` false-accepts the forged signature through the zombie window — critic 13/13, scribe 29/29, verifier 3/3 (state `Z` at read instant), boundary 6/6 on a kill(0)-variant gate. `poll()` reaps via waitpid — dead never reads alive. Pinned in a code comment.
- Zombie window quantified (boundary): under `communicate()` a dead child satisfies `kill(0)` for the entire drain (2.35–2.42s hold arms, ~33ms release); under the poll-gate the window is 1–4ms and can never contain its own check.
- `<` relaxed to `<=` on death-vs-marker ordering (sub-tick forger defense — critic correction).
- **Load-bearing `bounded_claim`**: live-window forgery defeats the gate by construction — boundary 6/6, verifier 6/6 accepted. The gate detects post-death *origin*, not authorship.
- Genuine-side failure mode measured: reader stall ≥~0.65s post-spawn false-rejects a genuine signature (boundary knee); fails loudly, disclosed.

## Integration defect and fix

The initial work commit `a32920b` staged reports+receipts but **omitted the runner diff** — the +228 hunk stayed uncommitted; a clean checkout ran 96/96 with no gate row (verifier-measured). Follow-up commit `5417…` (this lane's r64 fix commit) landed the exact verified blob `66a18a00…`; `git show HEAD:run_battery.py` sha matches the measured worktree bytes. The verifier's claims 1+5 marked DISAGREE-as-worded pre-fix; post-fix the committed state carries the verified code.

## Seat-evidence audit

| seat | landed | key evidence |
|---|---|---|
| author | `r64-author.md` + tracked +228/−0 | 97/97, 12 discriminations, prior 96 0-mismatch, fault-injection outer PASS |
| scout | `r64-scout.md` | mechanism map; `kill(0)` false-accept measured 5/5; poll() identified as the only sound primitive; insertion point |
| critic | `r64-critic.md` | 203 runs; buffering attack falsified (post-death write never readable pre-death); zombie trap real; knee ~70–75ms; live-forge 29/29 bypass; two corrections applied |
| reviewer | `r64-reviewer.md` | r63 audit AGREE-all: 96/96 fresh, 10 discriminations, kernel ppid corroboration, 94 prior rows stable |
| baseline | `r64-baseline.md` | frozen `a7e0cb1` 96/96, 0 mismatches vs r63-verifier receipt (83 tuples + 13 meta) |
| simplifier | `r64-simplifier.md` | minimal-expression YES; 8 load-bearing + 4 implied clauses (wash); zombie window dead-by-construction under poll() |
| scribe | `r64-scribe.md` | 156 gated observations over six liveness primitives — convergent; lesson draft → `corpus/lessons/r64-while-live-gate.md` |
| boundary | `r64-boundary.md` | 69 runs; zombie-window widths quantified; stderr forge identical; 24-hog load 8/8 genuine accepted; stall knee ~0.65s; pre-death forge 6/6 defeats gate |
| verifier | `r64-verifier.md` | claims 2,3,4a,4b AGREE; claims 1+5 DISAGREE-as-worded (integration miss) — resolved by landing the verified blob |

## Disclosures recorded

- Verifier caught the uncommitted-code defect pre-adjudication — fixed by committing the byte-identical verified file (`66a18a00`).
- Gate authenticates observation order, not authorship (live-window forge accepted 6/6 by design).
- Genuine-arm margin ~+67ms vs stall knee ~0.65s — real but bounded; fails loudly.
- Subreaper ppid 1573 host-specific; single host + build.
- XSentinel flagged recursive baseline embedding (1.4G frozen tree — excluded from staging) and pre-existing commit-identity drift (this round's commits use the majority `game-dev-2d-shokunin` identity).

## Per-axis verdicts

- **depth: improved locally** — the forgery boundary now has a measured dual: the poll-gated read discriminates post-death forgeries, with the primitive dependence and the residual live-window attack both pinned.
- **coverage: improved locally** — 96→97 rows; three new measured edge families (zombie window, load/stall knee, pre-death forge).
- **calibration: unchanged** — the gate is an observation path, not a threshold; bound 3.0s inside established margins.

Verdict: **ADMIT** — no demonstrated scoped harm; four SHONEN boxes remain checked without promotion.

## Bounds retained

Linux headless Godot 4.7.2, CPython subprocess semantics, subreaper host layout; gate discriminates post-death origin only; timing margins host/load-bound; the r63 documented-accepting boundary is unchanged policy.
