# Round 64 verifier report — while-live signature gate (non-author, host: devin)

Seat: verifier (LEAF). Verified the committed state at `a32920b` plus the
actual working tree in the canonical repo `~/Projects/shokunin/game-dev-2d-shokunin`
(reached via `~/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d` symlink).
No commits/push/merge/stash/checkout; wrote only this report +
`corpus/live/r64-verifier/`. No LSP server answers this Python fixture — the
checks below are direct execution + git object comparison, stronger than text
grep.

## HEADLINE FINDING (severity: HIGH — blocks the claim as worded)

**`a32920b` does NOT contain the proposed mutation.** The commit touches 858
files, **all** under `corpus/live/` and `reports/` —
`git show a32920b --name-only --format="" | grep -vc '^corpus/live/\|^reports/'`
→ **0**. `a32920b:corpus/fixtures/run_battery.py` sha256 =
`fb7cab2bb0364bef802cd3ed67892510377b8c45024daa378ca632129d96d7c2` —
byte-identical to its parent `a7e0cb1` (the r63 file; `git log --follow` last
modifies it at `de78edb`). The +228 gate code exists only as **uncommitted
working-tree state**: `git status` → ` M corpus/fixtures/run_battery.py`,
worktree sha256 `66a18a0056aedbd6c99ed8637ed30d03a3404556ab49d05826e8c63f4fe1f07d`.
The commit message asserts "run_battery.py +228/-0" but the tracked file was
never staged; the author's own report says "Commit/push left to operator" —
the sweep committed the evidence and reports, not the code.

Consequence, measured: `git show a32920b:corpus/fixtures/run_battery.py` was
materialized into `corpus/live/r64-verifier/pretree/fixtures/` (all sibling
fixtures copied) and the full mandated 7-flag battery run against it →
**exit 0, PASS, 96/96 rows, NO `probe_while_live_signature_gate` row**
(receipt `pretree-runs/20261014T021648730172Z/verdicts.json`). A clean
checkout of HEAD cannot produce 97/97.

## Per-claim verdicts

### Claim 1 — seven-flag battery → 97/97: DISAGREE as worded ("committed tree")

- As commanded (from repo root, which executes the **uncommitted** worktree
  file): `python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot
  --runs <abs>/corpus/live/r64-verifier/runs --probe-failing
  --probe-unrelated-error --probe-export-launch --probe-godot-error
  --probe-stream-attribution --probe-crash-exit --probe-timeout` →
  **exit 0**, `PASS battery`, receipt
  `runs/20261014T021400329665Z/verdicts.json` = **PASS, 97/97 rows**
  (sha256 available in dir). So the functional claim holds — on dirty code.
- On the **committed** file: exit 0, PASS, **96/96**, gate row absent. The
  "committed tree → 97/97" premise is falsified.
- Row arithmetic checked: CASES literal = 81 entries (regex count on the
  committed blob); 81 + 2 mutants + 4 unrelated-error + 10 meta/probe = 97.

### Claim 2 — gate row semantics: AGREE (against the uncommitted code)

My own receipt `runs/20261014T021400329665Z/verdicts.json`, row
`probe_while_live_signature_gate`: verdict PASS, **12/12 discriminations
True**. Arm-level fields independently reproduce the author's table:

| arm | exit | marker@ | dead@ | lead | alive@obs | gate | inner_cls | write_ppid |
|---|---|---|---|---|---|---|---|---|
| genuine_default_r0/r1/r2 | 0 | 0.311–0.340 | +0.066–0.069 after | +66–69ms | True×3 | ACCEPT×3 | True | — |
| genuine_detach | 0 | 0.362 | +0.071 after | +71ms | True | ACCEPT | True | — |
| forge_release_r0/r1/r2 | 0 | 0.438–0.473 | −0.0317..−0.032 | post-death | False×3 | REJECT×3 | **True×3** | 1573 |
| forge_hold | 0 (TIMEOUT 3.0s) | 0.446 | −0.0317 | post-death | False | REJECT | False | 1573 |

Hold-arm kernel corroboration in my run: `write_ppid=1573` ==
`descendant_kernel_ppid_at_return=1573` (`/proc` truth) ≠ `godot_pid=1533023`;
`descendant_alive_at_return=True`. Release arms reject a *present* marker the
un-gated classifier accepts (`inner_classification=True`) — the r63 boundary
in one record. Matches author (±ms noise) and critic's verbatim-gate replica.

### Claim 3 — prior-row stability: AGREE

7-field tuple diff `(script, flags, expected_exit, actual_exit, signature,
verdict, error)` of my 96 non-gate rows vs the committed receipt
`corpus/live/r63-verifier/runs/20261014T011438671964Z/verdicts.json`
(96 results, PASS): **96 common rows, 0 mismatches**; only-new =
`{probe_while_live_signature_gate}`; only-old = `[]`. The pinned r63
boundary row `descendant_pipe_forged_signature_release` stays
`PASS exit=0 signature=forged` on both sides — byte-stable, documented.

### Claim 4 — forge spot-checks from my own scratch: AGREE both legs

Driver `corpus/live/r64-verifier/forge/wlg_forge_checks.py` (same selector
loop shape, liveness primitive parameterized), project
`corpus/live/r64-verifier/proj/` (tracked `descendant_pipe_probe.gd` +
critic's committed `wlg_critic_probe.gd` mutant), 3 reps/arm:

- (a) `kill(pid,0)` gate on the real `--spawn-forge-release` arm: **3/3
  false-ACCEPT** — `alive_at_marker=True` while `/proc/<pid>/stat` state =
  **Z** (dead-but-unreaped zombie; `write_ppid=1573` post-orphan). Same arm
  under `poll()` control: **0/3 accepted**, `dead_poll_at` 30–46ms before
  `marker_at`. The zombie-window class is deterministic, not a race —
  reproduces the critic's 13/13 effect.
- (b) live-window forgery under the `poll()` gate:
  `--forge-during-life` **3/3 ACCEPT** (descendant writes +150ms while the
  child sits in `OS.delay_msec`, state `S` at observation,
  `write_ppid` = live child pid) and `--forge-early` **3/3 ACCEPT** (racy
  immediate write, state `R`/`S`). A descendant-authored marker observed
  pre-death is accepted indistinguishably → `bounded_claim` is load-bearing,
  as claimed.

Receipt: `corpus/live/r64-verifier/forge/forge-verdicts.json`.

### Claim 5 — mutation scope: DISAGREE

- "HEAD touched `corpus/fixtures/run_battery.py` additively": **false** —
  HEAD touched zero tracked files (see headline finding).
- The *uncommitted* diff IS additive, verified exactly: single hunk
  `@@ -876,6 +876,234 @@`, `numstat 228/0`; prefix (`HEAD` lines 1–878:
  CASES, `run_process`, `classify_process`, `classify_streams`, all existing
  meta rows) and suffix (from `if args.probe_failing:`) byte-identical to
  HEAD — so classifier/run_process/CASES byte-stability holds *for the diff*.
- Secondary provenance gap: author reports post-edit sha `15ecad36…`
  (+224/−0); worktree is `66a18a00…` (+228/−0) — the critic's two integration
  corrections (poll()-primitive comment :896-899; `dead <= marker` ordering
  :1049/:1063) landed post-report and are *also* uncommitted.
- Untracked leftovers in tree: `corpus/live/r64-baseline/frozen/` (≈1.4G
  full-tree snapshot) and `reports/round-64/r64-boundary.md` — outside the
  commit, so not a scope breach, but the sweep left a report behind.

## Residual risk / verification gaps

- The gate row's genuine leg is a measured read-vs-exit race: my margin
  +66–71ms agrees with author (+67ms) and critic (knee ~70–75ms under
  injected stall). On a loaded host a genuine post-death observation flips
  `genuine_never_observed_post_death` → loud row FAIL, never silent accept —
  declared and verified by construction, not re-stressed here.
- Gate authenticates observation-time, not authorship — live-window forgery
  acceptance proven above; `bounded_claim` text carries the scope.
- Single host: Linux, Godot 4.7.2 headless, Python 3.14; orphans reparent to
  pid 1573 (user subreaper) — consistent across all arms.
- If the operator commits the working-tree `run_battery.py` (sha `66a18a00`),
  claims 1–4 stand as measured here; until then the round's code artifact
  exists only in a dirty worktree and the "committed state" claim fails.

## Verdict

**Claims 2, 3, 4: AGREE. Claims 1 and 5: DISAGREE** — the mechanism works
exactly as reported but is **not committed at `a32920b`**; HEAD contains only
the round's evidence and reports. Recommendation: operator should stage
`corpus/fixtures/run_battery.py` (worktree sha `66a18a00…`, the corrected
+228 version) and re-commit before this round's diff is treated as landed.
