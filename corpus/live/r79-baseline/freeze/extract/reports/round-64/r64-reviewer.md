# Round 64 reviewer report — non-author audit of round 63 (host: devin)

Seat: reviewer (non-author). I authored none of the r63 content and none of
the in-flight r64 work. Every run below is a fresh execution by me into my own
scratch; no commit, no tracked fixture/runner edit, no LOG/SCORECARD write, no
verdict marking. Write scope: this report and
`.shokunin/game-dev-2d/corpus/live/r64-reviewer/` only.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Python `3.14.7`, same host. Repo under audit:
`~/Projects/shokunin/game-dev-2d-shokunin` (canonical; `.shokunin/game-dev-2d`
symlink from worktree `~/Projects/prymeagnt/game-dev-2d`). HEAD under test:
`a7e0cb11399ec52c1e0453db345af8c35a0a86f3` "game-dev-2d r63 adjudication:
ADMIT" (work `de78edb` is its direct parent — `git log` verified).
`git status` at audit time: clean except untracked sibling scratch
(`corpus/live/r64-{author,baseline,scout,scribe}/`, wave w4 in-flight, not
mine, untouched by me) and my own `corpus/live/r64-reviewer/`.

## Tasked check 1 — seven-flag battery, fresh runs dir — AGREE

```
python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs .shokunin/game-dev-2d/corpus/live/r64-reviewer/runs \
  --probe-failing --probe-unrelated-error --probe-export-launch \
  --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

- Exit `0`; final line `PASS battery`. Receipt:
  `corpus/live/r64-reviewer/runs/20261014T013316960352Z/verdicts.json` (sha256
  `2c8392ea7582d948b230b6c16db5de7a6364b64ebcfc2ef3ea9fb4697015968e`).
- `len(results) = 96`, top `verdict: PASS`, **96/96 rows PASS**,
  `probe_failing: true`. Row arithmetic reproduced: 81 CASES + 2 mutants
  (83 rows carrying `script`) + 13 meta/probe rows (4 unconditional:
  save-process, crash-classification, pipe-EOF, signature-spoof; 5 opt-in; 4
  unrelated-error).
- stdout `corpus/live/r64-reviewer/battery.stdout` (sha256
  `2c75bb1d58dbe007a11d1ca9d1becad26164840e642b927abc48c3ccfe8de90f`):
  95 `^PASS` lines + exactly 2 designed inner `^FAIL`
  (`godot_error_unrelated` exit=1, `stream_reject` exit=0) — same shape as
  the r62/r63 receipts.
- Separate `--fault-injection` leg: exit `0`,
  `fault-runs/20261014T013452419554Z/fault-verdicts.json` outer PASS with the
  designed inner `fault_hang`/`fault_unrelated_error` FAILs — unchanged.

## Tasked check 2 — `probe_descendant_signature_spoof` meta, 10 discriminations — AGREE

My run's meta row: `verdict=PASS`, `mode=bounded_popen_plus_cases_forgery_row`,
`bound_seconds=3.0`. Hold arm `descendant_pipe_forge_hold_arm`:

| field | value |
|---|---|
| `timed_out` | `true` |
| `child_exit_at_timeout` | `0` (poll() reaped the already-dead child) |
| `actual_exit` / `error` | `null` / `"TIMEOUT after 3.0 seconds"` |
| `marker_observed` | `true` — forged signature inside the TIMEOUT record |
| `write_ppid` | `1573` |
| `godot_pid` / `descendant_pid` | `1230720` / `1230760` |
| `godot_alive_at_return` / `descendant_alive_at_return` | `false` / `true` |
| `descendant_kernel_ppid_at_return` | **`1573`** — `/proc/1230760/stat` field 4 |
| `inner_classification` | `false` |
| `elapsed_seconds` | `3.003` |

All **10 discriminations `true`** under my execution:
`hold_timed_out_with_child_dead`, `hold_forged_signature_captured`,
`hold_write_post_orphan`, `hold_rejects_via_timeout_axis_only`,
`hold_descendant_orphaned_alive`, `release_row_passes_on_forged_signature`,
`release_write_post_orphan`, **`hold_write_ppid_kernel_corroborated`**
(self-reported `write_ppid=1573` == kernel `/proc` ppid `1573` ≠
`godot_pid=1230720` — the fabricated-ppid slip class stays closed),
`release_withheld_banner_present`, `release_shape_matches_genuine`.
`ps -p 1573` → `/usr/lib/systemd/systemd --user` — the subreaper constant the
r63 reports record.

r62/r61 metas still green under the r63 surface:
`probe_descendant_pipe_eof` PASS with all 7 discriminations true;
`probe_spontaneous_crash_classification` PASS with all 4 true.

## Tasked check 3 — forged release CASES row is exit-0 PASS-shaped — AGREE

`descendant_pipe_forged_signature_release` (results row with
`flags=["--spawn-forge-release"]`): `expected_exit=0`, **`actual_exit=0`**,
`error=null`, `verdict=PASS`, signature
`DESCENDANT_PIPE_PROBE: expected signature` present. Captured output lines:

```
DESCENDANT_PIPE_FORGE child_signature=withheld
DESCENDANT_PIPE godot_pid=1230225
DESCENDANT_PIPE spawned_pid=1230299
DESCENDANT_PIPE_PROBE: expected signature
DESCENDANT_PIPE_FORGE write_ppid=1573
```

The child withheld the signature by construction (banner present, MARKER
gated out in fixture source), so the observed signature is provably the
descendant's post-exit write (`write_ppid=1573` ≠ `godot_pid=1230225`) —
yet classifies PASS indistinguishably from genuine. The pinned
documented-accepting boundary reproduces exactly.

## Tasked check 4 — 94 prior rows field-stable — AGREE

Field-diff of my `verdicts.json` vs the r62 named non-author receipt
`corpus/live/r62-verifier/runs/20261014T001002305311Z/verdicts.json` on
`(script, flags, expected_exit, actual_exit, signature, verdict, error)`,
meta rows on verdict (lane precedent; tool
`corpus/live/r64-reviewer/field_diff.py`):

- `new_rows=96 base_rows=94 shared=94` → **0 mismatches**;
  `new_only=[descendant_pipe_forged_signature_release,
  probe_descendant_signature_spoof]`; `base_only=[]`.
- Cross-check vs the r63-verifier 96-row receipt
  (`corpus/live/r63-verifier/runs/20261014T011438671964Z/verdicts.json`):
  **96 shared, 0 mismatches** — the full r63 surface is field-identical
  across independent executions.

## Tasked check 5 — adjudicator's bounded-claims vs committed surface — AGREE

| r63 adjudicator claim | committed surface | re-executed? |
|---|---|---|
| `classify_process` signature clause presence-only, origin-blind | `run_battery.py:176` `signature in output` over merged stdout+stderr | yes — forged PASS |
| forged PASS distinguishable only via timeout/child-death fields | meta `bounded_claim` + `hold_rejects_via_timeout_axis_only` | yes — `inner_classification=false` rides `error`/`actual_exit` |
| 10 discriminations incl. kernel ppid corroboration | `spoof_discriminations` dict, 10 keys (`run_battery.py:803–858`) | yes — all true, kernel 1573 == self-report |
| withheld-banner provenance anchor | `release_withheld_banner_present` | yes — banner in row output |
| documented-accepting, not fixed | CASES comment `:99–103`, meta `bounded_claim` | consistent; row still PASSes by design |
| 94 prior rows field-stable | vs r62 receipt | yes — 0 mismatches |
| classifier internals unchanged | `git show de78edb` on `run_battery.py`: **+189/−0**, two hunks (`@@ -96,6 +96,12` CASES append; `@@ -687,6 +693,189` meta block), zero removed lines; `run_process`/`classify_process`/`classify_streams`/`classify_audio_process` at lines 149–217 sit outside both hunk ranges | yes |
| bounds: Linux headless Godot 4.7.2, Python 3.14.7, POSIX pipes, host subreaper | bounded_claim strings + `ps` | env matches; 1573 = `systemd --user` |
| probe sha pins | `run_battery.py` sha256 `fb7cab2b…96d7c2`, `descendant_pipe_probe.gd` sha256 `4fce0676…3fdb3a2` — both match r63-verifier's recorded post-integration hashes | yes |

No r63 claim failed re-execution. `de78edb` resolves and is the direct
parent of HEAD (`a7e0cb1`).

## Tasked check 6 — r64-author diff on classifier internals / prior rows — CLEAN (nothing to flag)

At audit close: `git diff` and `git diff --cached` on the canonical repo are
**empty**; `git status --porcelain corpus/fixtures/ reports/ LOG.md
SCORECARD.md` clean; HEAD unchanged at `a7e0cb1`. The in-flight w4 wave
(`r64-author/`, `r64-baseline/`, `r64-scout/`, `r64-scribe/`) has produced
untracked scratch dirs only — **no tracked-file mutation exists yet**, so no
r64-author diff touches classifier internals or mutates prior rows as of this
report. The r63 accepting-boundary row and all 96 rows remain byte-stable at
HEAD. If the author lands the declared while-live-gate meta arm after this
audit, the check needs re-running against that diff; the declared brief
bounds it to additive-only.

## Corroborating checks (beyond the tasked list)

- Fixture source re-read (`descendant_pipe_probe.gd` HEAD): forge arms print
  the withheld banner instead of MARKER; the descendant's ppid-flip gate
  (`/proc/self/stat` field 4 polled at 0.05s) writes the signature only after
  kernel reparenting — post-exit provenance is fixture-enforced, matching the
  r63 reviewer's source verification.
- Process hygiene: post-run `ps` shows **no `sleep 6`/`sleep 8` descendants
  and no godot processes attributable to this lane**; the meta's SIGKILL
  reaping ran. (The only godots visible are sibling lane `game-dev-3d` r73
  processes — not this lane, per r63-verifier precedent.)
- Elapsed sanity: hold arm `elapsed_seconds=3.003` is bound-exact, inside the
  r62 critic's 3.003–3.007 band.

## Findings by severity

**No actionable defect found in scope.**

- *Cosmetic (carried-forward, disclosed):* the `run_battery.py` comment at
  lines ~655–657 still reads "written ~1s after spawn" — stale from the
  pre-integration `sleep 1` fixture; the committed mechanism is the ppid-flip
  gate. Already named in the r63 adjudication disclosures ("runner comment
  ~L649 stale"). The discrimination it annotates is presence-shaped and
  correct as coded. Non-blocking.
- *Cosmetic (carried-forward):* SCORECARD coverage row's "85 ordinary+meta
  rows" phrasing follows the r62 convention (96 total minus 11
  fault/opt-in-sub rows); arithmetic is internally consistent — noted only
  for the record.

## Disagreements

None on any tasked claim. Every pivotal r63 claim reproduces under my own
execution on committed `a7e0cb1`: 96/96 battery fresh, the forged release
row's exit-0 PASS on a provably descendant-authored post-death signature, all
10 spoof discriminations true including live kernel `/proc` corroboration
(1573 == 1573 ≠ 1230720), 94 prior rows 0-mismatch vs the r62 non-author
receipt (and 96/96 0-mismatch vs the r63 non-author receipt), classifier
internals demonstrably untouched (+189/−0 additive diff), and every
bounded-claim string consistent with what the committed surface measures.

## Residual risk / verification gaps (carried forward, consistent with r63 disclosures)

- Single host, single battery pass by me; `systemd --user` subreaper
  (`ppid=1573`) is host-specific — `write_ppid != godot_pid` is the
  host-agnostic clause, the concrete value is not.
- `hold_descendant_orphaned_alive` and the kernel-ppid corroboration are
  run-return timing checks; a descendant exiting inside that window would
  flip them — `sleep 6` leaves ~3s margin (r63-verifier-noted, observed
  comfortable).
- Release-arm `write_ppid` stays fixture-asserted only — that descendant is
  dead before return so kernel corroboration is impossible there by design
  (disclosed); the hold arm's corroboration covers the shared mechanism.
- `post_exit_write_captured` remains receipt-level presence; post-exit
  semantics are fixture-gate-enforced (r62/r63 honesty shape, disclosed).
- Not probed (author UNKNOWNs, carried): forged writes on a single captured
  stream, descendant chains >1 deep, >64KiB descendant output,
  Windows/macOS, exported builds, substring-forgery variants.
- Concurrency boundary: my battery ran 01:33–01:35Z on committed `a7e0cb1`;
  sibling w4 scratch (`r64-*`) appeared during the audit and is recorded as
  data, not evidence — none of it is mine, none of it is tracked.
- The r64 declared axis-move (while-live marker-read gate) is the author's
  in-flight work; this report audits only the r63 committed state plus the
  absence of tracked r64 mutation at audit close.

Recommendation (non-binding; adjudication belongs to the judge): the r63
ADMIT stands — every checkable claim survives fresh re-execution and no r64
tracked-surface violation exists at audit time.

No commit, no tracked-file write, no sibling-lane contact, no subagent
dispatch. Artifacts: `corpus/live/r64-reviewer/runs/20261014T013316960352Z/`
(battery receipt + opt-in artifacts), `fault-runs/20261014T013452419554Z/`,
`battery.stdout`, `fault.stdout`, `field_diff.py`.
