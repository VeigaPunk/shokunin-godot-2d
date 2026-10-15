# r81 VERIFIER — independent battery replay + forge-kill

Seat `VERIFIER` (LEAF) | lane `g2d` | round 81 | host **devin**.
Runtime Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python
3.14.7. HEAD `27f465c` (*r80 LOG: ADMIT-corr*) + r81 dirty landing, verified
live: ` M corpus/fixtures/run_battery.py` sha256
`ba3badff4ce24ec04d6cdd18375a85e7a7ab24e70ad231e9dcfb2f19f67bb13f`,
`?? corpus/fixtures/phys2d_joints.gd` sha256
`a93bffb958e2a7bd0f0a35f2311e5ff3ddd15f6217eeab92d767281edb93b26b` —
byte-identical to the author-claimed digest.

`lsp` disclosure: no `lsp` device is exposed in this session; no language
server is installed. Verification carriers are fresh-process battery receipts
and the production `classify_process` verdicts inside them — not grep. No
symbol-aware work was required of this seat.

Scope per dispatch: (1) two fresh full-battery reps, (2) prior-139 semantic
stability rep-vs-rep and rep-vs-HEAD, (3) one forge-kill on a load-bearing
`phys2d_joints` mechanism, (4) byte-stability of the 20 new rows, (5)
`expected_errors` census honesty. All mutations and receipts under
`corpus/live/r81-verify/`; **zero tracked edits** (`git status` delta vs the
landing: only the untracked `corpus/live/r81-verify/**` scratch plus
concurrent-seat arrivals documented in §6).

| # | check | result |
|---|---|---|
| 1 | rep1 battery (`runs1/20261015T065056902997Z/verdicts.json` sha `aff9a7c3…`) | **159/159 PASS**, top verdict PASS, rc=0 |
| 1 | rep2 battery (`runs2/20261015T065956055907Z/verdicts.json`) | **159/159 PASS**, top verdict PASS, rc=0 |
| 2 | rep1↔rep2 tuple identity (all 159) | **0 diffs** — `godot-tuples-rep{1,2}.txt` identical |
| 2 | prior-139 vs my own HEAD run (`git archive` @`27f465c`, `head-runs/20261015T070133097571Z`, 139/139 PASS) | **138/139 tuple-identical + 1 explained structural delta** (§2); 0 unexplained semantic diffs |
| 2 | my HEAD run vs r81-baseline freeze | **139/139 tuple-identical** — baseline seat's freeze independently confirmed |
| 3 | forge-kill: `pin.node_b` removed from `joint_pin_tiers` | row **FAIL** (exit 0, signature absent, +3 un-allowlisted ERRORs); battery **FAIL**; 158 other rows PASS — surgical, fail-closed |
| 4 | 20 `phys2d_joints_*` rows rep1-vs-rep2 | **byte-identical** on all fields incl. raw `output` lists |
| 5 | `probe_error_clause_surface` census | `rows_with_expected_errors=49`, `dead_entry_count=0`, 49/49 `any_entry_matched=true`, 49/49 `bare_classification_rejects=true` |

---

## 1. Full battery ×2 on the dirty tree — **159/159 both reps**

`python3 corpus/fixtures/run_battery.py --runs <abs>` from repo root, dirty
tree as landed (default path, no opt-in probe flags — the same invocation the
author and baseline seats used). 152 `CASES` + 7 meta = 159 rows; all 20
`phys2d_joints_*` rows present and PASS in both reps. `rep1.stderr.log` and
`rep2.stderr.log` are 0 bytes; no `^FAIL` line in either stdout log; the
documented SDL `joypad_sdl.cpp` flake did not occur in any of this seat's
four runs. Receipts: `rep1.stdout.log`, `rep2.stdout.log`,
`runs1/…/verdicts.json`, `runs2/…/verdicts.json`,
`godot-tuples-rep{1,2}.txt` (tooling: `tuples.py`/`compare.py`, copied
unchanged from `corpus/live/r81-baseline/`).

## 2. Prior-139 stability — **0 unexplained semantic diffs**

Compared **by case name** on the stable verdict tuple `(case, script, flags,
expected_exit, actual_exit, signature, verdict, error, expected_errors)` for
seeded rows and volatile-normalized canonical JSON for meta rows — i.e. the
dispatch's five semantic fields plus the pinned-evidence fields, with
`command`/`elapsed`/pids/path keys excluded by construction.

First-hand HEAD reference: `git archive HEAD | tar -x` →
`head-src/` (worktree checkout was refused twice by the host — see §6 note;
archive extraction is index-free and yields identical committed bytes;
harness sha `d13797a8…` matches the baseline-documented digest). Ran the
139-row HEAD battery once: **139/139 PASS**, and the resulting tuple set is
**byte-identical to the r81-baseline seat's frozen rep1 set**
(`../r81-baseline/freeze/godot-tuples-rep1.txt`) — two independent runs,
same 139 tuples.

rep1 and rep2 each vs HEAD/freeze on the 139 shared cases: **138 identical +
one delta on `probe_error_clause_surface`** (verdict PASS on both sides).
Field-level diff of that meta row (rep1 vs baseline `runs1`) shows the delta
is the landing's own self-census footprint and nothing else:

- `census.rows_with_expected_errors`: 45 → 49 — the four new allowlisted
  `phys2d_joints_*` rows are now censused; **all 45 shared census rows
  byte-identical**, zero missing.
- `census.scan_clause_census["ERROR:_per_line_lines"]`: 61 → 86 — the +25
  ERROR lines are exactly those the four new rows emit (all allowlisted).
- `dead_entry_count`: 0 → 0.

Identical new tuple sha on rep1 and rep2 (`e3b583a9…`) — deterministic
structural delta of the same class the r80 verifier recorded. **No seeded
row's verdict/exit/signature/error fields moved.** `new_only` = exactly the
20 `phys2d_joints_*` cases; `old_only` = ∅.

## 3. Forge-kill — `joint_pin_tiers` node_b removal → **fail closed**

Mutation: in `forge/fixtures/phys2d_joints.gd` (verbatim copy of the landed
fixture), deleted the single line `pin.node_b = b1.get_path()` (was
`:284`) — removes the Node2D-tier joint's second body. Ran the **entire**
forged battery (`forge/runs/20261015T065942850557Z/verdicts.json`):

- Battery verdict: **FAIL**; exactly one row failed —
  `phys2d_joints_joint_pin_tiers` (`exit=0`, error `None`). The other 158
  rows all PASS, including all census/meta rows: the kill is surgical.
- Divergence evidence in the row's own output: `n_type=3`
  (JOINT_TYPE_MAX — joint never created) vs pinned `n_type=0`;
  `n_rel=(200.0000,193.3124)`, `n_dist=278.1541` vs pinned
  `n_rel=(114.5184,164.2985)`, `n_dist=200.2710` — the unconstrained body
  fell under gravity. The untouched server-tier twin still reads
  `s_type=0`, `s_dist=200.2708` — the forge isolated to the node tier.
- Double rejection path: signature absence AND three un-allowlisted engine
  lines (`ERROR: Condition "joint->get_type() != JOINT_TYPE_PIN" is true.`
  ×3, `phys2d_joints.gd:296` — `pin_joint_get_param`/`get_flag` calls on the
  unmade joint). Either clause alone rejects the row.
- Receipt: `forge.stdout.log` (line 131 is the FAIL row), `forge/runs/…/
  verdicts.json`. The forge fixture copy lives at
  `forge/fixtures/phys2d_joints.gd` for audit.

Conclusion: the `node_b` connection is load-bearing for the pinned
measurement; the classifier fails closed on its removal — no false-PASS.

## 4. Byte-stability of the 20 new rows — **identical across reps**

rep1-vs-rep2 comparison of every field of all 20 `phys2d_joints_*` rows —
`verdict`, `actual_exit`, `expected_exit`, `signature`, `error`,
`expected_errors`, `script`, `flags`, and the full raw `output` line lists:
**zero differences**. The measured lattice (16 pinned API strings, joint
envelope positions to 4 decimals, layer/mask truth tables, Area2D entry
orders) is deterministic on this host, not merely passing.

## 5. `expected_errors` census — **all 49 entries live and discriminating**

From rep1's `probe_error_clause_surface` meta row (rep2 identical): 49
census rows (45 prior + 4 new: `joint_unset_refusal`, `joint_pin_clear`,
`joint_freed_rid`, `joint_node_freed_rid`), `dead_entry_count=0`, every
entry `dead_in_run=false` with `matched_lines>=1`, every row
`any_entry_matched=true` and `bare_classification_rejects=true`. The four
new allowlists are honest floors: in the forge run (§3) the same census
still reported `dead_entry_count=0` — the new entries' declared ERRORs are
genuinely emitted, and a row that *stops* emitting them is caught by
signature/exit clauses, not silently absorbed.

## 6. Anomalies and caveats

- **Concurrent-seat mutation of the shared dirty tree (observed live).**
  `corpus/fixtures/camera_proc.gd` — an **r85** fixture ("CanvasLayer /
  Viewport / Camera2D transform lattice", 15+5 arms, `r85-scout §1.1-1.4`)
  — appeared at `2026-10-15T06:51:39Z`, *inside rep1's run window and before
  rep2's scratch copy*. My two reps therefore bracket a foreign landing:
  rep1's scratch predates it, rep2's includes it. Both PASS 159/159 and
  remain tuple-identical on all 159 rows, so the r81 verdict is unaffected —
  but a battery that copies the whole fixtures dir means **any concurrent
  seat's in-flight file enters later reps' scratch**. Receipts stand; the
  isolation gap is worth naming.
- **Export progress-line jitter (cosmetic, non-semantic).** The only
  normalized-`output` diffs anywhere are `export_readiness` /
  `export_preset_missing` line 11: `update_scripts_classes … (30 steps)`
  HEAD/freeze, `(31 steps)` rep1, `(32 steps)` rep2 — the engine's class-
  registration step count tracks how many `.gd` files the scratch project
  holds (30 → +1 `phys2d_joints.gd` → +1 concurrent `camera_proc.gd`). It
  sits outside the five semantic fields, both rows PASS on both sides, and
  the rep1↔rep2 instance (31 vs 32) proves it is run-boundary noise from
  the shared tree, not landing drift.
- `git worktree add --detach` failed twice on this host ("unable to write
  file reports/round-81/r81-scout.md" / index-reset refusal; /tmp at 72%
  tmpfs). `git archive HEAD` used instead — committed bytes are identical;
  the resulting 139-tuple set equals the baseline's worktree-produced
  freeze sha-for-sha, which cross-validates both methods.
- Other pre-existing tree dirt (` M SCORECARD.md`, `__pycache__/*.pyc`,
  and concurrently arriving `reports/round-7x/8x` dirs including
  `r81-scribe.md`) is outside the battery's read path; `run_battery.py`
  and `phys2d_joints.gd` were stable (sha-verified) at both rep starts.
- Scope note: byte-stability is shown on this single host/runtime
  (Godot 4.7.2, 2 reps, ~32 cores); no cross-platform or cross-version
  determinism is claimed by this seat.

## Verdict

**Confirm the author claim.** 159/159 PASS reproduced independently on two
fresh serial reps; prior-139 rows carry 0 unexplained semantic drift (the
sole delta is the battery's own census growing to cover the 4 new
allowlisted rows); the 20 new rows are byte-stable across reps; a one-line
mechanism kill fails the row and the battery with zero collateral; the
49-entry `expected_errors` census is fully live and self-discriminating.
Recommendation: **admit** (verifier recommendation, not admission).

## Receipts (`corpus/live/r81-verify/`)

| artifact | path |
|---|---|
| rep1 stdout/stderr | `rep1.stdout.log` / `rep1.stderr.log` (0 B) |
| rep1 verdicts + tuples | `runs1/20261015T065056902997Z/verdicts.json`, `godot-tuples-rep1.txt` |
| rep2 stdout/stderr | `rep2.stdout.log` / `rep2.stderr.log` (0 B) |
| rep2 verdicts + tuples | `runs2/20261015T065956055907Z/verdicts.json`, `godot-tuples-rep2.txt` |
| HEAD source + run | `head-src/` (git archive @27f465c), `head.stdout.log`, `head-runs/20261015T070133097571Z/verdicts.json`, `godot-tuples-head.txt` |
| forge-kill | `forge/fixtures/` (mutated copy), `forge.stdout.log`, `forge/runs/20261015T065942850557Z/verdicts.json` |
| compare tooling | `tuples.py`, `compare.py` (unchanged copies from `corpus/live/r81-baseline/`) |
