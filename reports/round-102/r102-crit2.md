# r102-crit2 — C2 timeout-probe fix audit: tautology check + counterfactual pack

Seat: C2 critic (timeout probe). Date 2026-10-18. Host uptime: `17:41:01 up 1 day, 17:41, 1 user, load average: 6.34, 8.25, 9.09` (per-run load in §2/§5). Godot `4.7.2.stable.arch_linux.ed1daf0bf`; kernel `7.2.3-arch1-3`.
Constraints honored: never ran `corpus/fixtures/run_battery.py`; only direct `godot --headless` on `/var/tmp/r102-crit2/` scratch + my replication `cf_harness.py`; no shared file edited; shard-only output.
Labels: [obs] observed bytes/commands, [inf] inference, [unk] unknown.

## TL;DR

- The r101 `probe_timeout` red is **not** the `hold_open_new_bound` arm. Clause-by-clause recompute of `meta_pass` on both tracked records: `hold_rejects=true`, `new_accepts=true`; the sole red clause is `old_rejects` ← `slow_clean_old_bound.marker_observed=false` [obs, §1].
- Mechanism: boot-to-marker latency on this host is now 0.64–0.85 s (measured), so at 0.75 s the old-bound kill lands **pre-marker** deterministically; at r26 (same binary, same kernel) the same 0.75 s kill landed **post-marker** (marker=true in the r26 record) [obs, §2]. Max observed marker 0.848 > bound 0.75 by 98 ms — the bound sits inside the boot-noise band.
- Fix-space verdict: **deleting `marker_observed` from `old_rejects` is a tautology.** Applied to the two tracked FAIL records it yields PASS with zero observed change; live, it also accepts a fixture that provably kills pre-marker (delayed-marker variant G) [obs, §4].
- Bound-bump 0.75→1.5 s is a genuine repair **only with attached margin + sabotage evidence** — I ran that pack: accept-set §5 (B/C/D), reject-set §5 (E/F/G), margins §5–6 [obs].

## 1. The actual red clause

Command (read-only, on the tracked artifacts):
`python3 -c` clause mirror of `corpus/fixtures/run_battery.py:5375-5387` over both `timeout-verdicts.json` [obs]:

| record | old_rejects | new_accepts | hold_rejects | meta |
|---|---|---|---|---|
| 20261018T200239625248Z | **False** (marker=False) | True | True | FAIL |
| 20261018T202131127599Z | **False** (marker=False) | True | True | FAIL |

- `old_rejects` requires `timed_out ∧ marker_observed ∧ ¬inner_classification ∧ ¬child_alive` (run_battery.py:5375-5377). The old arm satisfies all but `marker_observed`: `timed_out=true`, marker **false**, inner=false, child dead [obs].
- `hold_rejects` (run_battery.py:5381-5383) is fully satisfied in both runs: `timed_out=true, marker=true, inner=false, child_alive=false`. The hold arm is healthy [obs].
- Misrouting in `reports/round-101/r101-adjudicator.md:81-86`: it names the red as "`hold_open_new_bound` times out with marker observed" and a "deterministic host-state class in the r62 descendant-pipe probe". Both wrong: the arm it names is the expected hold behavior, and the true r62 probe (`probe_descendant_pipe_eof`) is **PASS** in both runs' `verdicts.json` while `probe_timeout` is FAIL [obs]. The red belongs to the r22/r26 `--probe-timeout` three-arm meta (run_battery.py:5314-5402).
- Consequence for this round: `reports/round-102/r102-D3.md` (read 17:45:52) targets "`hold_open_new_bound` original intent + 3.0 s bound drift". Per this section that arm and its bound are healthy; the repair belongs at old bound 0.75 + its marker clause [obs].

## 2. Mechanism measurement

Direct timing of the exact battery child command (`/var/tmp/r102-crit2/timing.py`; timestamps are parent-side line arrivals) [obs]:

```
CMD godot --headless --path /var/tmp/r102-crit2/scratch --script res://timeout_probe.gd -- --delay-clean
run0: banner=0.016 marker=0.711 exit=0 total=2.252
run1: banner=0.016 marker=0.751 exit=0 total=2.307
run2: banner=0.015 marker=0.848 exit=0 total=2.398
run3: banner=0.015 marker=0.766 exit=0 total=2.319
run4: banner=0.016 marker=0.731 exit=0 total=2.286   (warmup run: marker=0.750)
CMD ... -- --hold-open (killed 0.3 s after marker)
run0: marker=0.703 ; run1: marker=0.705
```
- Marker arrival ∈ [0.711, 0.848] (N=5+1+2); exit ∈ [2.202, 2.398] (incl. the minimal-scratch control). Bound 0.75 therefore sits **inside** the marker distribution; at battery-time load the kill (elapsed exactly 0.753 in every red record) lands pre-marker → `marker_observed=false` [obs+inf].
- History, same binary+host: r26 record (`corpus/lessons/r26-timeout-detail.json`) old arm at 0.75 s elapsed 0.753 **marker=true**, new arm total 1.972 s → boot-to-marker ≈0.42 s [obs]; r101 runs new arm 2.294/2.346 s → ≈0.75–0.85 s [inf from elapsed arithmetic]. r22 lesson already flagged the margin: "0.394s normal startup, leaving only ~0.356s margin … a slow start can false-fail; no stability claim" [obs quote].
- Not scratch census: a 3-file minimal scratch (project.godot + fixture + .uid) gave marker 0.638/0.713/0.787 — same band as the ~200-file scratch [obs].
- Classification: host-conditioned latency drift consumed the margin; not "process-state pollution" (the adjudicator's guess), not expectation rot — the r26 lesson itself says a delayed-before-marker no-marker observation "is NOT evidence for the stronger claim", i.e. the expectation correctly demands marker-before-kill and the current state genuinely fails it [obs+inf]. Cause split between persistent drift vs current load regime: [unk]; kernel (7.2.3-arch1-3) and Godot hash unchanged since r26/r62 [obs].

## 3. Instrument fidelity (validates §5)

`/var/tmp/r102-crit2/cf_harness.py` replicates `bounded_run`/`classify_process`/meta semantics (run_battery.py:5322-5396, 1775-1792) on a scratch project. Genuine fixture @ (old 0.75, new 3.0, hold 3.0), run twice [obs]:
`old: timed_out=True marker=False elapsed=0.753`; `new: exit=0 marker=True elapsed=2.368/2.307 inner=True`; `hold: timed_out=True marker=True elapsed=3.006/3.006 inner=False`; META `old_rejects=false, new_accepts=true, hold_rejects=true` — same shape/classes as both tracked records, elapsed within 0.001–0.07 s. Raw: `out/A1-genuine-0.75.json`, `out/A2-genuine-0.75.json`.

## 4. Tautology test (the demanded attack)

Clause-deletion simulation — the same records, `marker_observed` removed from `old_rejects` only, computed on the **tracked** JSONs [obs]:

| record | tracked clauses | marker clause deleted |
|---|---|---|
| …T200239625248Z | FAIL | **PASS** |
| …T202131127599Z | FAIL | **PASS** |

Zero observed bytes change; the red disappears. So an "expectation repair" of this kind is an expectation rewrite by construction — REJECT unless it can be shown that no broken variant is newly accepted. Live counterexample (fixture G, §5): `timeout_probe_delayed_marker.gd` prints the marker only after a 1.0 s pre-delay, so the 1.5 s-bounded old arm provably kills pre-marker (marker=false at kill, elapsed 1.504). Under tracked clauses G is red; under clause-deleted clauses G passes (`meta_no_marker_clause_pass=true` in `out/G-delayedmarker-1.5.json`). That is the discriminating power the deletion silently drops [obs].

## 5. Counterfactual matrix (all runs: scratch, cf_harness; JSONs in `/var/tmp/r102-crit2/out/`)

| variant (fixture, old/new/hold bounds) | old arm | key other arms | meta(tracked clauses) | meta(marker clause deleted) |
|---|---|---|---|---|
| A1/A2 genuine @0.75/3.0/3.0 | marker=False, kill 0.753 | new ok, hold ok | FAIL | PASS |
| B genuine @1.25/3.0/3.0 | **marker=True**, kill 1.254 | new 2.224, hold 3.007 | **PASS** | PASS |
| C genuine @1.5/3.0/3.0 | **marker=True**, kill 1.506 | new 2.309, hold 3.006 | **PASS** | PASS |
| D genuine @2.0/3.0/3.0 | marker=True, kill 2.011 | new 2.221 (margin 0.21 s!) | PASS | PASS |
| E fast-exit sabotage @1.5 | timed_out=False exit 0 @0.762 | hold also exits @0.769 | **FAIL** (old+hold) | FAIL |
| F no-hold sabotage @1.5 | marker=True kill 1.507 | hold exits @0.746 | **FAIL** (hold only) | FAIL |
| G delayed-marker @1.5 | marker=False kill 1.504 | new 1.85 ok, hold ok | **FAIL** (old) | **PASS** (tautology demo) |

Margins from measured distributions (marker max 0.848; exit min 2.202) [obs+inf]:
- old=0.75: left margin **−0.098 s** (structurally broken); old=1.25: left +0.402, right +0.952; **old=1.5: left +0.652, right +0.702**; old=2.0: left +1.152, right **+0.202** (fragile; D passed only by ~0.2 s — reject).
- 1.5 s ≈ geometric mid of [max marker, min exit] → recommended minimal bump. Residual envelope: a future boot-to-marker > 1.5 s re-reds the arm; adaptive bounds (calibrate `T_marker` per run, set bounds relative to it) are the structurally robust alternative [inf].

## 6. Acceptance contract for D3 / orchestrator (minimum evidence the fix must carry)

1. **Counterfactual REJECT**: under the fixed constants, E/F (and a pre-marker-kill variant like G) must be red, with the clause that fires named — else the fix accepts still-broken state.
2. **Counterfactual ACCEPT**: full three-arm meta green on the genuine fixture with exact constants + raw records; old arm must show `marker_observed=true` and kill-in-delay (exit would have been ≈2.2–2.4 s).
3. **Two-sided measured margins**: N≥5 marker-arrival distribution, chosen bound, left margin (bound − max marker) and right margin (min exit − bound); publish residual envelope. Single-run calibration is insufficient (marker straddles 0.75; §2).
4. **Clause discipline**: any deletion/weakening of `marker_observed` (or of any meta clause whose falsity is the observed anomaly) must come with a demonstration of which broken variant the clause discriminated and that the new expectation still rejects it. Per §4, deleting the old-arm marker clause without such a demonstration = tautology; reject.
5. **Text reconciliation**: if the fix is the bound bump, `bounded_claim`/lesson wording "rejected by old bound" now means the calibrated 1.5 s bound; the r26 constant story (0.75/1.5/3.0) must be updated or annotated, and a recheck trigger added for boot-latency drift.
6. **Provenance**: D3's plan (r102-D3.md) currently aims at hold_open/3.0 s, which §1 shows healthy; the fix text must not silently leave the actual red clause unaddressed or claim the r62 probe as the carrier.

## 7. Answer to the assignment

- "Is the fix a tautology?" — **Clause deletion: yes, proven twice (tracked-record inspection + live G).** **Bound bump: no — provided it ships with this counterfactual pack** (accept on genuine 1.25/1.5; reject on fast/no-hold/delayed-marker; margins; residual envelope). If D3 proposes an envelope that passes while the old arm still kills pre-marker, treat it as the same tautology in different clothing and reject per §6.4.
- Recommended minimal repair: `old_timeout_seconds 0.75 → 1.5` (new/hold/cleanup constants unchanged), plus ±margin numbers and the E/F/G counterfactual evidence in the lesson/shard; adaptive-bounds noted as the durable alternative.

## 8. Artifacts (all scratch-side; nothing committed)

- This shard: `reports/round-102/r102-crit2.md`.
- `/var/tmp/r102-crit2/timing.py`, `/var/tmp/r102-crit2/cf_harness.py` (replications; sources cited in §3).
- Scratch: `/var/tmp/r102-crit2/scratch/` (copy of run scratch + `timeout_probe_delayed_marker.gd`, `timeout_probe_fast.gd`, `timeout_probe_nohold.gd`), `/var/tmp/r102-crit2/scratch-min/`.
- Records: `/var/tmp/r102-crit2/out/{A1,A2,B,C,D,E,F,G}-*.json`.
- Read-only sources cited: `corpus/live/runs/20261018T200239625248Z/timeout-verdicts.json`, `corpus/live/runs/20261018T202131127599Z/{timeout-verdicts,verdicts}.json`, `corpus/fixtures/run_battery.py:5314-5402,5375-5387,1775-1792`, `corpus/fixtures/timeout_probe.gd`, `corpus/lessons/r26-timeout-detail.json`, `corpus/lessons/r26-timeout-margin.md`, `corpus/lessons/r22-real-timeout.md`, `corpus/lessons/r62-pipe-eof-timeout.md`, `reports/round-101/r101-adjudicator.md:81-86`, `reports/round-102/r102-D3.md`.
- Not done by this seat: no shared-file edits, no CASES registration, no commit (orchestrator-serialized); D3 fix not yet landed → contract in §6 is the handoff.
