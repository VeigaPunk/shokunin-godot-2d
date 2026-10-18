# r102-connector — sibling scan / routed-import candidates

Plan (5 lines):
1. Fleet census via ../MANIFEST.json (last rounds per lane) — read-only.
2. 3D-lane quiet probe (read-only mtime/proc); read LOG.md tail only if quiet, else record skip.
3. Mine sibling timeout/descendant/envelope mechanisms relevant to C2 (r62-era `hold_open_new_bound`).
4. File routed-import candidates (mechanism, source evidence, expected 2D use) + contested scope.
5. Output only in this shard; no shared-file edits; keep <400 lines.

Host: 2026-10-18. `uptime` at seat start (20:40 UTC): `17:40:36 up 1 day, 17:40, 1 user, load average: 7.49, 8.64, 9.24`; during counterfactual measurement: `14.32 9.06 9.10`. Base commit `1392ca21`; `git status --porcelain` = `?? reports/round-102/` only.

Rules-of-engagement note: nothing outside the lane repo was written. Reads outside: fleet `MANIFEST.json` (seat-authorized), 3D-lane file *metadata* (mtime via `find -printf`) and `ps` process args (needed for the quiet check). No 3D-lane file content was read (lane not quiet → LOG.md tail skipped per seat instruction). Fleet `.ufo/*` contents not read (rule 5); metadata only.

## 1. Sibling lane scan

### 1.1 3D-lane quiet check → NOT QUIET (LOG.md tail SKIPPED)
Evidence (exact commands):
- `pgrep -fa 'game-dev-3d'` at 17:40:49 local → live r105 battery: PID 1447141 `python3 corpus/fixtures/run_battery.py > reports/round-105/n24/runs/node24-full-20261018T202944Z.stdout`; harness watchers 1614623/1617630/1890236/1986930/1989138; live Godot children: PID 1989353 `godot --headless --path .../corpus/live/runs/20261018T202944290389Z/scratch --script res://r99_animtree.gd -- --arm=sm_misc`, PIDs 1989429/1989430 `timeout -s KILL 14 godot ... --script res://r99b_sm.gd > child.log`.
- Newest 3D-lane file mtimes (excl. `.git`) all 2026-10-18 17:40 (child.log writes under `.../runs/20261018T202944290389Z/scratch/`).
- Consequence: LOG.md tail not read; recorded as a measured skip, not a defect. The sibling is mid-battery (r105, node24), so timing-sensitive comparisons against 3D-lane artifacts should not be attempted from this seat.

### 1.2 Fleet MANIFEST census (read-only jq over `../MANIFEST.json`, 233 round entries)
- `lane_rounds` key census: chousa 11, kagi 12, kake 10, kama 1, kasegi 5, kengaku 17, kotoba 13, kotodama 27, kumitate 16, lore 22, mori 11, protocol 11, aggregator 18, **game-dev-2d 1** (r101). **`game-dev-3d` has zero `lane_rounds` entries.**
- Last 3D-lane appearance in round notes: r70–r73 (2026-10-13/14), ADMITs with reports at `.ufo/reports/round-NN/game-dev-3d.md`; last recorded r73. Roster entry: `{"id":"game-dev-3d", "domain":"3D game production via headless fixtures across Godot/three.js/Unity/Unreal", "repo":"shokunin-3d-engines", "minted":"2026-10-11"}`.
- Route for orchestrator: r101 L0 recorded "3D side-round deferred; 3D lane under parallel r104" — the sibling is now running **r105** (see ps above) and still active, so the L0 gate (3D quiet) remains unmet; refresh the fleet L0 record. (Fleet `.ufo/l0-questions.md` metadata only: 38,356 B, mtime 2026-10-18 17:14 — content unread, rule 5.)

## 2. C2 routing correction — the red conjunct is the OLD-bound arm, not the hold arm

Method: recomputed the four meta conjuncts verbatim from `run_battery.py:5375-5387` over every `timeout-verdicts.json` in the lane (`glob corpus/live/**/timeout-verdicts.json` → **50 receipts**).

- **46 receipts** (r26→r66 era, 2026-10-13/14): `old_rejects=True, new_accepts=True, hold_rejects=True` → verdict PASS. The old arm historically passed with `elapsed=0.753–0.755` and `marker_observed=true`. (2 more receipts — `corpus/live/r25-verifier-relative/…`, `r25-verifier2-relative/…` — use an older two-arm schema (`timeout_accept`/`timeout_reject`) and do not contain these conjuncts; 50 files total = 46 + 2 FAIL + 2 older-format.)
- **Only two FAILs exist** — the two r101 runs:
  - `corpus/live/runs/20261018T200239625248Z/` (run 1): `old_rejects=False`, `new_accepts=True`, `hold_rejects=True`.
  - `corpus/live/runs/20261018T202131127599Z/` (run 2): same shape.
- Run-2 arm bytes (verbatim from the receipt):
  - `slow_clean_old_bound`: `timed_out=true, marker_observed=false, inner_classification=false, direct_child_alive_after_cleanup=false, elapsed=0.753`, raw_stdout ends at the Godot banner (no marker). → the sole failing conjunct is `old_positive["marker_observed"]` in `old_rejects`.
  - `slow_clean_new_bound`: exit 0, marker true, 2.294 s → `new_accepts=true`.
  - `hold_open_new_bound`: `timed_out=true, marker_observed=true, inner_classification=false, direct_child_alive_after_cleanup=false, elapsed=3.005` → **`hold_rejects=true` (green), exactly the designed shape.**
- Receipt row: `probe_timeout FAIL inner_classifications=[False, True, False]` — all three inner classifications are the designed ones (`False`=old rejects, `True`=new accepts, `False`=hold rejects). The meta fails only on the old-arm marker conjunct.
- In the same receipt **`probe_descendant_pipe_eof` PASS** (r62's own descendant-pipe probe is green).
- → The C2 brief ("the r62 timeout probe's `hold_open_new_bound` arm is red") conflates three distinct things: r62's descendant-pipe meta probe (green), the `hold_open_new_bound` arm (green), and the r26-lineage `slow_clean_old_bound` arm (red via its marker conjunct). Routing this correction back is the seat's main finding.

## 3. Mechanism — knife-edge bound vs boot-to-marker (measured this host)

Probe script (durable): `reports/round-102/mutations/r102-connector-probe.py`; scratch `/var/tmp/r102-connector/proj` = verbatim copies of `corpus/fixtures/project.godot` + `timeout_probe.gd`. Never `run_battery.py`; bounded_run semantics transcribed from `run_battery.py:5322-5369`. Raw run-2 output: `/var/tmp/r102-connector/probe-run2.json`.

- **Unbounded warm runs, marker arrival** (banner constant ~0.014 s): run-1 (load 4.30) `0.800 / 0.684 / 0.762`; run-2 (load 6.81) `0.843 / 0.775 / 0.778`. Six samples: min 0.684, median ≈ 0.777, max 0.843.
- **bounded 0.75 (bounded_run replica) ×4**: `marker_observed` false/false/**true**/false (1/4), `timed_out=true`, `elapsed=0.753–0.754` → reproduces the r101 receipt exactly on a scratch project.
- **bounded 3.0**: clean exit 0, 2.304 s, marker true.
- **Counterfactual — bound 1.2 s ×3 (load 14.32)**: `timed_out=true, marker_observed=true, elapsed=1.203–1.204` in all three → `old_rejects` restored with ≥0.36 s margin at measured load; clean total ≈2.3 s keeps the "old bound rejects the delayed clean exit" semantics intact (1.2 < 1.5 s post-marker delay).
- Inference (labeled): the 0.75 s bound sits *inside* today's marker-arrival distribution (0.68–0.84); the historical 46 passes cleared it by ≤ ~50 ms even then (`elapsed ≈0.753–0.755` with marker true). This is **bound/expectation rot at a knife edge** — no leaked process state is needed to explain it; both r101 runs' new-arm totals (2.346/2.294 s ⇒ boot ≈0.79–0.85 s) match my samples, i.e. the two "byte-identical" failures are two draws from the same narrow distribution, not a new host-state class.
- r26 lesson (`corpus/lessons/r26-timeout-margin.md`) designed this arm as "marker observed but timeout"; it explicitly states the no-marker observation is "NOT evidence for the stronger claim" → dropping the marker conjunct would weaken the claim; raising the old bound preserves it. Repair candidate for C2: old bound ∈ [1.0, 1.3] s, marker conjunct kept. Envelope machinery (`run_battery.py:2326-2340`, any-payload tuple evidence; r87 precedent at 321-325/433-434) is **not** recommended here — it would erase the marker-before-bound discrimination the arm exists to pin.

## 4. Routed-import candidates (2D lane)

- **RC-1 (timeout arms, primary)** — repair shape: old bound raise + counterfactual numbers (§3). Source: in-lane measurement. Route: C2 seat / orchestrator. Label: observation + labeled inference.
- **RC-2 (sibling capture discipline)** — 3D lane's live pattern (ps args only): shell `timeout -s KILL 14` + per-case scratch + `> child.log` file redirect; kills the direct child at kernel level, and file redirects remove pipe-drain semantics entirely. Import value: for *diagnosis harnesses* whose classification is polluted by pipe-drain timing. Explicitly NOT for `probe_timeout` itself (its subject is the runner's own subprocess-bound semantics) and NOT a blanket change (r62 lesson: pipe semantics are a tracked coverage surface). Source: ps observation 17:40 local; no 3D content read. Label: observation.
- **RC-3 (historical 3D→2D process-tree port)** — sketch path `.ufo/waves/shokunin-train-20261013-w2/x-connector.md`, cited at `corpus/lessons/r62-pipe-eof-timeout.md:103-108`: `killpg` cannot reach `OS.create_process` descendants (each is its own session/group leader) and a naive `start_new_session`-less port would kill the harness's own group. Status there: "runner-hardening policy call for a future round". Route: orchestrator (fleet file; unread by me under rule 5 — the lesson carries the boundary).
- **RC-4 (pipe-safety precedent, mori lane)** — MANIFEST r9 note: SIGPIPE/grep race eliminated by capture-then-grep (15/8000 rc=141 → 0/60000). Applicable if any harness ever greps live pipes; 2D already uses full `communicate` capture → no active need. Label: fleet-record observation.
- **Envelope-pattern inventory (in-lane)** — (a) evidence-tuple any-payload machinery `run_battery.py:2326-2340` + r87 mode-envelope precedent; (b) r101 F1 fold precedent (pin phase-invariant fields only; phase-variable fields to unpinned diagnostics) — the closest correct pattern if C2 ever needs to absorb a *legitimately bimodal* arm field rather than repair the bound.

## 5. Contested scope

- **No filesystem contention found**: `mount | grep -iE 'shokunin|game-dev'` → empty; `readlink -f corpus/live` = the in-repo path (real dir, not symlink); each lane keeps its own `corpus/live` tree; 2D run stamps are lane-local.
- **Cross-lane mechanism territory**: the process-tree reaping/killpg port decision (RC-3) is 2D-owned but has 3D history; if C2's repair changes capture/kill discipline in `run_battery.py`, coordinate with that open port.
- **Schedule gate**: r101 L0 item (1) — "3D side-round deferred; runs before 2D r105" — gate reflected "3D under r104"; sibling observed at **r105 and active** → gate still closed; orchestrator refresh needed.
- **Host-shared device census**: `/dev/input/js0,js1` intermittent enumeration affects input-census rows in this lane (r101 F3, r101-adjudicator); the same host serves both lanes → "never pin device-census tokens" (r85/r101 law) is a cross-lane host hazard, not a per-lane one.
- **Record note (low severity, non-accusatory)**: r101-adjudicator records "Receipts run2 540 PASS/7 FAIL". Both stored receipts measure differently (`546` results each): run 1 = 537 PASS / 9 FAIL, run 2 = 542 PASS / 4 FAIL (FAIL sets listed in §2/§-below). Counting convention for the adjudicator's figure is unknown — flag for orchestrator reconciliation, not a defect claim. Run-1 FAIL set: `input_lattice_census, input_lattice_dev_joy, input89_edges_axisdev, r101_ytrans_y1000, r101_ytrans_ym1000, r101_ytrans_ycop, probe_error_clause_surface, probe_export_launch, probe_timeout`. Run-2 FAIL set: `input_lattice_census, input_lattice_dev_joy, input89_edges_axisdev, probe_timeout`.

## 6. Unknowns / not measured

- Marker-arrival under swarm-time load (33–57, r101 run window) not measured; my samples are at load 4–14, max arrival 0.843 s.
- 3D-lane file contents unread (lane active); its r105 battery outcome/pass-rate unknown from this seat.
- Fleet `.ufo/l0-questions.md` and `.ufo/waves/.../x-connector.md` contents unread (rule 5) — metadata only.
- Whether `probe_timeout`'s old arm can be made load-robust without *any* bound change (e.g. waiting for marker with its own small sub-bound) was not prototyped — C2's call.

Exact commands used are cited inline; arm bytes quoted in §2 are verbatim from the receipts. Every claim above is observation unless labeled inference.
