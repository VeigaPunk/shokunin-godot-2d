# Round 63 simplifier report — minimal-design critique of the signature-spoof boundary pin (host: devin)

Seat: simplifier (report-only). Lane axis: **depth** — pin the merged-stream
signature-spoofing boundary the r62 critic measured in isolation as a tracked
known-accepting forgery row. I polled
`git -C ~/Projects/shokunin/game-dev-2d-shokunin diff` until the author's
tracked diff existed, judged it against the production classifier, and ran my
own measurements (pre-diff candidate arm + post-diff seven-flag battery) into
my own `--runs` scope. No tracked edit, no commit, no sibling-scope write.
Scratch under `corpus/live/r63-simplifier/`; this report is my only
tracked-path write.

## Poll evidence

- `git status`/`git diff` empty of tracked changes through ~00:34Z (only
  untracked `corpus/live/r63-*` sibling scratch).
- ~00:47Z: tracked hunks landed together —
  `M corpus/fixtures/descendant_pipe_probe.gd` **+31/−1** and
  `M corpus/fixtures/run_battery.py` **+155/−0**. Diff stable at snapshot;
  `corpus/live/r63-simplifier/tracked-diff.patch` (re-polled: identical).
- Worktree shas at review (`tracked-sha256.txt`): fixture
  `4fce06765b091e9f…` (committed r62 fixture `054f37c9174db6be…`), runner
  `b6f3d5c238047d0f…` (committed `0c4c9bee70569c8e…`).

## The diff as landed (verbatim inventory)

1. **Fixture** `descendant_pipe_probe.gd` (+31/−1, folds into the existing
   arm chain — no new file):
   - `print(MARKER)` :28 becomes conditional: `forge_hold`/`forge_release`
     flag vars computed once; under either forge flag the child prints
     `DESCENDANT_PIPE_FORGE child_signature=withheld` **instead of** MARKER —
     so any MARKER occurrence in captured output is descendant-authored.
     Existing arms (`none`/`--spawn-hold`/`--spawn-detach`) still print
     MARKER; their runtime behavior is byte-identical.
   - New const `FORGE_PPID_WRITE := "DESCENDANT_PIPE_FORGE write_ppid="`.
   - One new `elif` (shared by both forge flags): descendant reuses the r62
     reparenting gate (`/proc/self/stat` ppid-flip off the child's pid), then
     `echo MARKER; echo write_ppid=$pp` (the *reparented* ppid — in-record
     post-orphan provenance), then `; sleep 6` iff `-hold`
     (`tail` ternary). `spawned_pid=` print reused free.
   - Header comment documents both arms accurately — including the verified
     parenthetical that `-hold` under the 8s CASES bound also forges a PASS
     (measured below: exit 0 at 6.38s, classify True).
2. **CASES row** (1 tuple + 4-line comment): `("descendant_pipe_forged_signature_release",
   "descendant_pipe_probe.gd", ["--spawn-forge-release"], 0,
   "DESCENDANT_PIPE_PROBE: expected signature")` — asserts the **same**
   signature string as `descendant_pipe_detached_control`: the forgery
   collides with a genuine row's exact tuple.
3. **Unconditional meta** `probe_descendant_signature_spoof` (~148 lines after
   the r62 meta, before `if args.probe_failing:`): one bounded
   `Popen`/`communicate(timeout=3.0)` drive of `--spawn-forge-hold` reusing
   in-scope `pid_alive` (:623), `pipe_bound` shape, pid regexes, `detached` /
   `detached_output` r62 locals, and the discriminate-then-SIGKILL-orphans
   hygiene pattern; 8 discriminations → `all()` gate; `bounded_claim` names
   the boundary "documented forgery-accepting, not a fix". No
   `expected_errors` entry (no `ERROR:` lines), no CASES tuple-field change,
   no `--probe-*` flag, no classifier edit.

## Independence evidence (my own measurements)

Pre-diff, I built the candidate-minimal arm myself
(`proj/spoof_min_probe.gd` + verbatim-`ast`-extracted `run_process`/
`classify_process` from the tracked runner — production code path;
`drive_spoof_min.py` → `spoof-min-verdicts.json`):

- `forge_release` (child silent, ppid-gated descendant writes MARKER then
  exits): `exit=0, error=None, marker present ×1, classify_process=True`,
  elapsed 0.434s. **Verdict-field diff vs both genuine_child and the
  detached control: `{}` — empty.** On every classification-visible field
  the forged record is the genuine record.
- `forge_hold` (same write + 6s hold, bounded Popen at 3.0):
  `timed_out=True, child_exit_at_timeout=0, actual_exit=None,
  inner_classification=False, classify_if_error_none=True` — the declared
  claim's shape reproduced before the author landed.

Post-diff, landed-worktree battery:
`python3 corpus/fixtures/run_battery.py --probe-failing
--probe-unrelated-error --probe-export-launch --probe-godot-error
--probe-stream-attribution --probe-crash-exit --probe-timeout --runs
corpus/live/r63-simplifier/runs` →
`runs/20261014T004715285705Z/verdicts.json` **96/96 PASS**
(81 CASES + 2 mutants + 13 meta-side rows; console `battery.stdout`).

- New meta `probe_descendant_signature_spoof` observed:
  `timed_out=true, child_exit_at_timeout=0, marker_observed=true,
  write_ppid=1573 ≠ godot_pid=1108217, inner_classification=False,
  descendant_alive_at_return=true, elapsed=3.002s` — **all 8 discriminations
  true**.
- New CASES row `descendant_pipe_forged_signature_release`: `PASS exit=0
  error=None`, output = banner + `child_signature=withheld` + `godot_pid=` +
  `spawned_pid=` + MARKER + `write_ppid=1573` — a forged signature the child
  provably never emitted, accepted.
- Prior-row stability vs `corpus/live/r62-verifier/runs/
  20261014T001002305311Z/verdicts.json` on the 8-field tuple
  (case/script/flags/expected_exit/signature/actual_exit/verdict/error):
  **0 mismatches, 0 missing** across all 94 prior rows; exactly +2 rows.
- `ast`-extraction: `run_process`, `classify_process`, `classify_streams`,
  `classify_audio_process`, `execute`, `pid_alive` **byte-identical**
  HEAD↔worktree; only `main` (+CASES tuple context, +meta block) differs.
- `forge_hold_8s.json`: landed fixture `--spawn-forge-hold` under verbatim
  `run_process` at bound 8 → `exit=0, error=None, classify=True` at 6.38s,
  `write_ppid=1573` — the header comment's CASES-bound parenthetical is
  accurate.

## Verdict: minimal expression — YES; the floor is 1 CASES + 1 meta

### Could the arm fold into `descendant_pipe_probe.gd`? — it did; correct call

The single-authority choice won: the forge arms reuse the file's MARKER
const, the r62 reparenting gate, and the `spawned_pid=` provenance line. A
second fixture would have duplicated all three — a second convention over
one mechanism (the seat card's core target). Cost paid: one edited line
(`print(MARKER)` → flag-conditional). That edit is required by construction,
not avoidable — the claim is only meaningful if the signature in merged
output is descendant-only, and :28 was unconditional. The withheld-banner
substitute print keeps the record self-documenting. Existing arms' output is
unchanged (flag absent → `else` branch → MARKER). **Admissible and
preferred.** The alternative marker design — a dedicated forged-signature
const the child never prints (scout's option b) — would have kept :28
untouched but weakens the pin: the forged row's signature wouldn't collide
with the genuine control's tuple. The author's choice (forge the *same*
`DESCENDANT_PIPE_PROBE: expected signature`) is the sharper boundary: same
signature field, same verdict fields, opposite provenance.

### Are the CASES/meta rows the fewest needed? — yes, 1+1 is the floor

- The **release CASES row** is the cheapest possible carrier of the declared
  "tracked known-accepting forgery row": one tuple line, runs at the
  standard 8s bound (~0.5s wall), permanently in the suite. No meta drive
  could beat one line, and dropping it would leave the acceptance witnessed
  only synthetically (`classify_if_error_none`-style) inside a meta payload
  rather than as a real green row.
- The **hold meta** is required, not optional: the distinguishing-fields
  half of the claim (`timed_out`, `child_exit_at_timeout`) exists only on a
  bounded-Popen record — r62 proved a CASES tuple can't carry an error-set
  record (always False), and an 8s-bound CASES hold row would pass-and-pin
  nothing (measured again: `--spawn-forge-hold` at bound 8 → clean True at
  6.38s). `child_exit_at_timeout` needs `poll()` inside the `TimeoutExpired`
  catch, which `subprocess.run` cannot expose — the raw-Popen block earns its
  lines exactly as the r62 one did.
- A single meta driving both shapes is conceivable (~2 Popens, −1 row) but
  heavier per-line and loses the tracked-row embodiment; a CASES-only pin is
  impossible. **2 rows is the minimal honest encoding.**

### Is the meta minimal? — each clause bites; two named trims

- `hold_timed_out_with_child_dead` + `hold_forged_signature_captured` +
  `hold_rejects_via_timeout_axis_only` are the claim verbatim: the forged
  signature sits inside a record that rejects only via the timeout axis.
- `hold_write_post_orphan` / `release_write_post_orphan` are the **new
  capability this diff adds**: `write_ppid != godot_pid` is *receipt-carried*
  post-death provenance — it closes the r62 verifier's caveat ("post-exit-ness
  carried by the fixture gate, not provable from the receipt") for this arm.
  Two clauses that convert the weakest r62 evidence class into the strongest
  r63 evidence; keep.
- `release_row_passes_on_forged_signature` binds the meta to the CASES row
  (the cross-row link); `release_shape_matches_genuine` is the
  indistinguishability pin, honestly scoped to classification-visible fields
  (verdict/exit/error/marker-presence — the forged record's extra provenance
  lines are not classification fields). Both required.
- **Deletable candidate (wash):** `hold_descendant_orphaned_alive` — leak
  symmetry already pinned by two r62 clauses; here it corroborates the
  post-death writer's survival but the receipt now proves ordering via
  `write_ppid`. Margin ~3.4s (6s hold vs 3.0s bound + meta latency) — not a
  flake surface. Keep-or-delete; keeping is r62-consistent.
- **Informational fields** `godot_alive_at_return` /
  `descendant_alive_at_return` / `elapsed_seconds` — recorded, ungated,
  r62-consistent. Keep.
- **Orphan-reap loop** — non-gating hygiene, prevents descendant
  accumulation across runs. Keep.

### Anything else deletable / absent non-minimalisms

Confirmed absent (keep it that way): no new fixture file, no new
`expected_errors` entry, no CASES tuple schema change, no per-case bound
plumbing, no `--probe-*` flag expansion, no runner/classifier edit — the diff
pins the boundary instead of fixing it, which is the declared move.

**Optional 1-line hardening, not required** — a suppression witness. None of
the 8 clauses keys on marker *count* or the withheld banner: if the child's
suppression ever regressed (e.g. MARKER printed unconditionally again while
the descendant still wrote), every clause still passes while the row's
documented claim "a signature the direct child never emitted" silently
becomes false. `spoof_text.count(spoof_marker) == 1` (or
`child_signature=withheld in spoof_text`, mirrored for `forged_output`)
closes it for one line. Same evidence-integrity class as r62's `early_write`
presence-slip — bounded, not mechanism-breaking: `write_post_orphan` still
proves a post-death descendant write exists, so the boundary pin itself
survives a suppression regression.

**Convention note (non-required alternative):** the meta duplicates ~90% of
the r62 bounded-Popen block rather than extracting a shared helper. That is
the established convention (r61 crash meta, r62 pipe meta — each claim
self-contained with its own discriminations + `bounded_claim`), and it
leaves the hash-cited r62 block byte-untouched; a `_bounded_popen` helper
would shave ~35 lines at the cost of churning reviewed code. Convention-
consistent, not line-minimal — admissible, same trade r62 itself made.

Minor naming sprawl across the triple `--spawn-forge-*` /
`descendant_pipe_forged_signature_release` / `probe_descendant_signature_spoof`
(forge/forged/spoof for one concept) — cosmetic, consistent with the lane's
existing mixed naming.

## Bounded correctness notes

- `write_ppid` provenance assumes reparenting changes the ppid — host-
  specific target (1573 = `systemd --user` here) but mechanism-guaranteed;
  a non-differing ppid fails *closed* (`write_ppid is not None and !=
  godot_pid`).
- Gate-exit on failed `read` yields empty `$pp` → `write_ppid` unparseable →
  discrimination False — fails closed, correct.
- POSIX-only (`/usr/bin/sh`, `/proc/self/stat`, `os.kill`, `SIGKILL`);
  `bounded_claim` scopes it honestly.
- Same optional hardening carried forward from r62: fixture has no
  `spawned <= 0` guard; today it fails loud via meta cross-checks.

## Artifact inventory (my scope)

- `corpus/live/r63-simplifier/tracked-diff.patch` — reviewed diff snapshot
  (+31/−1 fixture, +155/−0 runner); `tracked-sha256.txt`.
- `corpus/live/r63-simplifier/proj/` — scratch project: `spoof_min_probe.gd`
  (candidate-minimal forge arms) + copy of the landed fixture.
- `corpus/live/r63-simplifier/drive_spoof_min.py` → `spoof-min-verdicts.json`
  — verbatim-classifier drive: forged release True with **empty**
  verdict-field diff vs both genuine controls; forged hold =
  timed_out+child_dead+`classify_if_error_none` True.
- `corpus/live/r63-simplifier/forge_hold_8s.json` — landed `-hold` arm at the
  CASES 8s bound: clean exit 0, classify True at 6.38s.
- `corpus/live/r63-simplifier/runs/20261014T004715285705Z/verdicts.json` —
  independent seven-flag battery **96/96 PASS**; all 8 new discriminations
  true; prior 94 rows field-stable vs the r62 verifier receipt (0
  mismatches). `battery.stdout` — console stream.
- This report. No commit, no tracked-fixture mutation, no LOG/SCORECARD
  write.

Tooling note: no `lsp` device is exposed to this seat — the deletion
candidate (`hold_descendant_orphaned_alive`) is a dict key produced and
consumed inside the same meta hunk (`all(spoof_discriminations.values())`);
its absence of external callers was established by full-file read of the
1154-line runner, not grep sampling. Text fallback per seat card.

**Bottom line**: the landed diff is the minimal honest expression of the
declared depth move — one fixture `elif` (shared hold/release via a `tail`
ternary) folded into the single marker/gate authority rather than a second
fixture; one CASES tuple as the cheapest possible tracked known-accepting
forgery row; one unconditional meta carrying what CASES provably cannot
(bounded-Popen timeout evidence fields — the *only* axis that separates the
forged record from a genuine signature). The `write_ppid` echo is the
standout small choice: it upgrades post-death ordering from fixture-gate
inference to receipt-carried proof for two discrimination clauses, closing
r62's thinnest caveat at ~zero marginal lines. Nothing is dead on arrival;
the only trims worth naming are `hold_descendant_orphaned_alive` (wash —
leak symmetry already r62-pinned) and the optional `marker_occurrences == 1`
suppression witness that would catch a child-suppression regression the
current eight clauses cannot see.
