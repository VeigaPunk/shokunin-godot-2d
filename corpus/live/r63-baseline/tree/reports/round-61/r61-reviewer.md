# Round 61 reviewer report — non-author audit of round 60 (host: devin)

Seat: reviewer (non-author). I did not author round 60. Every run below is a
fresh execution by me into my own scratch; no commit, no tracked fixture/runner
edit, no LOG/SCORECARD write, no verdict marking. Write scope: this report and
`.shokunin/game-dev-2d/corpus/live/r61-reviewer/` only.

Environment matches both r60 reports: Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`), Python `3.14.7`, `RLIMIT_CORE` `[-1,-1]` (recorded in my
probe JSON).

## What I re-ran (r60 reports' exact recipes)

1. **Seven-flag battery, fresh runs dir** (`corpus/live/r61-reviewer/runs/battery`):
   ```
   python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot \
     --runs .shokunin/game-dev-2d/corpus/live/r61-reviewer/runs/battery \
     --probe-failing --probe-unrelated-error --probe-export-launch \
     --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
   ```
   → `runs/battery/20261013T220005698057Z/verdicts.json` (sha256 `e2391406…`)
   **PASS, 89/89 rows** (79 script-bearing + 10 probe/meta rows; verbatim stdout
   `corpus/live/r61-reviewer/battery.stdout` sha256 `74300e49…`, final line
   `PASS battery`).
2. **Fault-injection leg**, same recipe, `--runs corpus/live/r61-reviewer/runs/fault`
   → `runs/fault/20261013T220100775388Z/fault-verdicts.json` (sha256 `cc50beaf…`)
   outer **PASS**; `fault_hang` FAIL `TIMEOUT after 0.25 seconds`,
   `fault_clean_expected_negative` PASS exit 2, `fault_unrelated_error` FAIL
   exit 2 — identical designed shape to both r60 reports.
3. **Spontaneous-crash probe, third independent derivation.** Wrote my own
   driver `scratch-probe/r61_reviewer_probe.py` (sha256 `95627c5c…`) that
   `ast.get_source_segment`-extracts nested `run_process` + `classify_process`
   verbatim from the tracked runner and execs them — no transcription, no reuse
   of author's `drive_probe.py` (absent from disk) or verifier's
   `verify_probe.py`. My own probe project `scratch-probe/proj/`; the
   `spontaneous_crash_probe.gd` I wrote is sha256 `16e31617585406291f32e654c9d0899d6d2c28135d22c97a26d18d58b46edc69`
   — byte-identical to the author's claimed `16e31617…` (verified via the
   verifier's committed copy). Result JSON
   `scratch-probe/r61-reviewer-spontaneous-crash-verdicts.json` (sha256
   `227585de…`), per-arm raw `r61_*.stdout`.

## Measured results (mine vs both r60 reports)

| arm | r60 claim | my exit | classify e=1 | e=-9 | e=-6 | e=-6+allowlist |
|---|---|---|---|---|---|---|
| accept (no flag) | exit1 True | 1 | **True** | False | False | False |
| `OS.crash` a | -6 SIGABRT False | **-6** | **False** | False | False | **True** |
| `OS.crash` b | -6 SIGABRT False | **-6** | **False** | False | False | **True** |
| `OS.kill(self)` | -9 SIGKILL False | **-9** | **False** | **True** | False | False |

- stderr shapes confirmed on my captures: crash arms carry
  `ERROR: r60 spontaneous crash probe` + `at: crash (core/core_bind.cpp:349)` +
  GDScript backtrace `spontaneous_crash_probe.gd:15` +
  `handle_crash: Program crashed with signal 4` + C++ backtrace (SIGILL-in-
  handler nuance confirmed); accept and sigkill arms have no `ERROR:`/
  `handle_crash` lines; marker on stdout in all four arms.
- Extracted-source sha256s match the verifier's recorded values exactly:
  `run_process` `88728b23…`, `classify_process` `749fa060…`; runner sha256
  `42104d95af5fcb98d742c495ee4562ea0c579c49d9ca22d11755302f685c31fb`.

## Hash / committed-state verification

- Canonical repo `~/Projects/shokunin/game-dev-2d-shokunin` HEAD = `3ee05ff5`.
  `git merge-base --is-ancestor 8aca02e HEAD` → **`8aca02e` IS an ancestor**;
  `8aca02e` = the r60 commit ("game-dev-2d r60: spontaneous-crash
  classification verified (devin host)"). Its tracked delta is reports +
  `corpus/live/r60-verifier/` scratch + the historical live-scratch import; the
  runner's last touching commit is `587561c` (r59) — `git show
  HEAD:corpus/fixtures/run_battery.py | sha256sum` = `42104d95…` (committed
  state = what I executed).
- Post-r60 commits `8776736` (README), `3cc9e1a` + `3ee05ff5` (HOURS.md add +
  revert) touch no fixture/corpus logic. `git status`: only untracked
  `corpus/live/r61-*/` and `reports/round-61/`; `git diff HEAD` empty.
- Row-count arithmetic confirmed directly: `CASES` list = **77 entries**
  (run_battery.py lines 19–95); 77 + 2 mutants + 10 probe/meta = 89 —
  verifier's decomposition is exact; author's "78 ordinary" is the
  save-process-meta lumping convention (consistent, not an error).
- Field-level diff of my 89 rows vs verifier's
  `corpus/live/r60-verifier/battery/20261013T165543975131Z/verdicts.json` and vs
  `corpus/lessons/r59-audio-non-author.json` on
  `(script, flags, expected_exit, actual_exit, signature, verdict, error)`:
  **0 mismatches against both** (positional compare, 89/89 rows each).
- Zero-runner-logic-change integration path confirmed in source: CASES rows
  are 5-tuples; `expected_errors` (lines 391–435) is a per-case-name dict fed
  to `classify_process(..., allowed_errors)`; `allowed_error` exact-matches
  `ERROR: r60 spontaneous crash probe`, so a tracked SIGABRT row needs one
  CASES tuple + one dict entry (still inside run_battery.py — "zero runner
  changes" means zero logic changes) plus the tracked .gd fixture; a SIGKILL
  row needs only a CASES tuple.

## Disagreements

**None on any measurement.** All pivotal claims reproduce: -6/False, -9/False,
expected -9 True unmodified, expected -6 True only with the exact crash-`ERROR:`
allowlist, 89/89 on committed state, 0 field deltas vs r60-verifier and r59
baselines, fault-injection outer PASS.

## Verification gaps / provenance notes (not falsifications)

- **Author artifacts are gone**: `corpus/live/runs/round-60/` does not exist;
  `corpus/live/.gitignore` line 1 (`runs/`) explains it — gitignored scratch,
  never committed, since cleaned. I could not re-verify the author's claimed
  artifact shas (`verdicts.json 9905553c…`, `full.stdout 1c68d6ab…`,
  `fault-verdicts.json 57f2dca0…`, `spontaneous-crash-verdicts.json 9694988b…`,
  `drive_probe.py 689e004b…`); the r60-verifier hash-verified them
  contemporaneously, and this audit's fresh replay supersedes the artifacts.
- **Two-repo hash split**: `8aca02e` resolves only in the canonical repo
  (`~/Projects/shokunin/game-dev-2d-shokunin/.git`), not in the worktree repo
  (`~/Projects/prymeagnt/game-dev-2d`, where the r60 commit is `a0a9c4bc`,
  also verified ancestor of its HEAD `fe4bbeaf`). Conversely SCORECARD's cited
  full SHAs (`ca7cd3ac…`, `22b37bb7…`, `0c2ce964…`, `6eb4df76…`) resolve in the
  worktree repo but **not** in the canonical repo (history rewritten at the
  `fe4bbeaf` extraction; canonical equivalents `c47ab5d`/`587561c`/`00a41f6`
  carry the same subjects). Citations resolve in whichever repo minted them;
  future reports should name the repo.
- Cosmetic: the probe `.gd` header comment says it "lives only under
  `corpus/live/runs/round-60/`" — that path never existed in git; a tracked
  copy now lives under `corpus/live/r60-verifier/scratch-probe/proj/`
  (committed at `8aca02e`).
- **Timeline note**: during this audit (after my battery verdicts mtime
  2026-10-13T19:01-03:00 and probe run ~18:58-03:00) a sibling lane's
  in-flight edit to `corpus/fixtures/run_battery.py` and a new untracked
  `corpus/fixtures/spontaneous_crash_probe.gd` appeared (mtime 19:04-03:00):
  two CASES rows (`crash_spontaneous_sigabrt` exp -6, `crash_self_sigkill`
  exp -9) plus the `expected_errors` allowlist entry — exactly the path this
  audit confirms. All my measurements and every runner sha cited above pin
  the pre-edit committed blob `42104d95…`; I did not re-run against the
  working-tree edit (that is the r61 verifier's seat).

## Retained UNKNOWNs (consistent with both reports)

- Signal **origin** is unprovable from `returncode`: self-SIGKILL vs external
  SIGKILL is indistinguishable; `OS.crash` attribution rests on its own
  `ERROR:` + backtrace, not syscall evidence.
- I ran the same 4 arms on the same host; cross-host determinism of the
  SIGILL→handler→SIGABRT `-6` is untested by me.
- Not measured: process-tree/descendant timeout, startup margin,
  exported-build crash, non-SIGABRT/SIGKILL signals, core capture.
- My battery/fault receipts sit under `corpus/live/r61-reviewer/runs/` which
  the `runs/` gitignore pattern also covers — same gitignored-scratch
  convention as the author's; sha256s recorded above.

## Reviewer position on the r61 move

The r60 boundary claims are sound and the allowlist path is real and narrow
(exact-line match, per-case key — cannot bleed into SIGTERM -15, timeout, or
expected-mismatch rows). The falsification risk the executor must respect:
`expected_errors` falls back to `()` per unknown case name, so a tracked crash
case *without* its dict entry fails — that is the designed gate, and the
negative row should be exercised to prove it still rejects.
