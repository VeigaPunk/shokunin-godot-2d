# Round 63 author report — tracked merged-stream signature-spoof boundary (host: devin)

Seat: author (role executor), lane `game-dev-2d`, declared axis-move:
**depth** — pin the merged-stream signature-spoofing boundary the r62 critic
measured in isolation (`reports/round-62/r62-critic.md` attack (b), `spoof`
arm: child printed no signature, descendant wrote `PIPE_CRITIC: expected
signature` into the held pipe post-death, released ~1.4s → `classify_process`
True at 1.749s) as a **tracked known-accepting forgery row**.

## Scoped move

`classify_process`'s signature clause is `signature in output` over the merged
captured stdout+stderr — presence-based and **origin-blind**. A
`OS.create_process` descendant inherits the captured pipes; gated on kernel
reparenting (`/proc/self/stat` ppid flip, the r62-proven gate) it can write
the expected signature *provably after the direct child's exit*. Whether that
forged write is accepted depends only on pipe lifetime vs the bound:

- **release-before-bound** (descendant exits after writing) → runner returns
  `exit 0`, `error None`, signature present → `classify_process` **True** —
  a PASS on a signature the child never emitted.
- **hold-past-bound** → `TIMEOUT` record carrying the forged signature →
  classified False *only* via the error/timeout axis (`timed_out`,
  `child_exit_at_timeout`), never via signature presence.

r63 lands both arms as tracked rows: **+1 CASES row** (the forged PASS —
documented known-accepting forgery, *recorded not fixed*) and **+1
unconditional meta row** (the hold arm under bounded Popen + discriminations).
Zero runner-internal change.

## Causal scratch (pre-edit, production code path)

Driver `.shokunin/game-dev-2d/corpus/live/r63-author/scratch-probe/drive_probe.py`
`ast.get_source_segment`-extracts `run_process` + `classify_process`
**verbatim** from the pre-edit tracked runner (sha256
`0c4c9bee70569c8ec29f98dea89c437d78587fd5c3c7b3220b76140ac59520dd` = HEAD
`edbd945`) — no transcription. Fixture candidate
`scratch-probe/proj/descendant_pipe_probe.gd` is byte-identical (`cmp`
verified post-landing) to the promoted tracked file. Receipt
`scratch-probe/spoof-verdicts.json` sha256
`f24b10b92d685c19814793cdc27b9dee70692f4cf6252d70cc930f10674b3fcc`; raw merged
captures under `scratch-probe/raw/`.

| arm | driver | exit | error | sig present | write_ppid≠godot_pid | classify |
|---|---|---|---|---|---|---|
| clean (no descendant) | `run_process` verbatim | 0 | None | yes (child's own) | — | True |
| detach (`--spawn-detach`) | `run_process` verbatim | 0 | None | yes (child's own) | — | True |
| **forge_hold @3.0s** | bounded Popen (meta replica) | None | `TIMEOUT after 3.0 seconds` | **yes (forged, post-death)** | 1573≠1011361 | **False** |
| **forge_release @8s** | `run_process` verbatim | **0** | **None** | **yes (forged, post-death)** | 1573≠1013939 | **True** |
| forge_hold @8s | `run_process` verbatim | 0 | None | yes (forged) | 1573≠1014646 | **True** |
| forge_release @ wrong signature | reclassify same output | 0 | None | n/a | — | False |

`forge_hold` also records `child_exit_at_timeout=0` (`poll()` reaps the
already-dead child at the `TimeoutExpired` catch), `elapsed 3.003s`,
`godot_alive_at_return=false`, `descendant_alive_at_return=true` (orphaned to
subreaper ppid 1573 — this session's `systemd --user`, same as r62). The
`forge_hold @8s` arm pins bound-dependence: the *same* forged write releases
~6.5s < 8s → clean forged PASS; rejection is carried only by the
timeout/error fields, never by signature provenance. `shape_compare.
indistinguishable_on_signature_axis = true`: forged-release tuple
`(exit 0, error None, marker_observed, classify True)` ≡ genuine-detach
tuple — no classification-visible field separates them.

**Spoof-accepting boundary pinned**: `classify_process` returned True on a
signature written after the child's death by a process the child spawned.

## Tracked files changed (this lane's only tracked writes this round)

1. `corpus/fixtures/descendant_pipe_probe.gd` — sha256 `054f37c9…` →
   **`4fce06765b091e9ffe649b06fca020115e07d2590b91200d57c4f319b3fdb3a2`**,
   +31/−1. New `FORGE_PPID_WRITE` const; arms `--spawn-forge-hold` /
   `--spawn-forge-release`: child **withholds** the signature (prints
   `DESCENDANT_PIPE_FORGE child_signature=withheld` instead of MARKER — the
   −1 diff line is `print(MARKER)` moved under the non-forge gate, so any
   observed signature is provably descendant-authored); descendant reuses
   the ppid-flip reparenting gate, echoes the **expected signature** +
   `write_ppid=<reparented ppid>`, then holds ~6s (`-hold`) or exits at once
   (`-release`). Existing arms untouched and behavior-identical.
2. `corpus/fixtures/run_battery.py` — sha256 `0c4c9bee…` →
   **`b6f3d5c238047d0f8636d880cf73515197504aba29787a5cdc0ca8164ea660c4`**,
   **+155/−0**, two additive hunks:
   - CASES +1 appended at list end (order untouched):
     `("descendant_pipe_forged_signature_release", "descendant_pipe_probe.gd",
     ["--spawn-forge-release"], 0, "DESCENDANT_PIPE_PROBE: expected
     signature")` with an in-list KNOWN-ACCEPTING FORGERY comment.
   - ONE unconditional meta row `probe_descendant_signature_spoof` after the
     r62 pipe-EOF meta: drives `--spawn-forge-hold` under one bounded
     `Popen`/`communicate(timeout=3.0)` (the `probe_timeout`/r62-meta
     pattern), then asserts eight discriminations. `run_process`,
     `classify_process`, `classify_streams`, `classify_audio_process`
     **ast-identical HEAD↔worktree** (verified by extraction, same method as
     the r62 critic).

## Meta discriminations (all `true` in the landed run)

- `hold_timed_out_with_child_dead` — `timed_out` ∧ `child_exit_at_timeout==0`:
  bound fired on pipe EOF with the child dead.
- `hold_forged_signature_captured` — expected signature **inside** the
  TIMEOUT record; the child withheld it by construction.
- `hold_write_post_orphan` — `write_ppid` (1573, subreaper) ≠ `godot_pid`:
  in-record post-death provenance — the r62 critic's `ppid=$PPID` hardening
  suggestion, landed as the provenance carrier.
- `hold_rejects_via_timeout_axis_only` — `classify_process(None, TIMEOUT,
  out, 0, marker)` is False: rejection rides the error/timeout axis alone.
- `hold_descendant_orphaned_alive` — no process-group kill; descendant
  orphaned alive at return.
- `release_row_passes_on_forged_signature` — the CASES row: verdict PASS,
  exit 0, error None, signature in output.
- `release_write_post_orphan` — same post-orphan provenance inside the
  accepted record.
- `release_shape_matches_genuine` — forged-release `(verdict, actual_exit,
  error, signature-present)` tuple ≡ genuine `descendant_pipe_detached_control`
  tuple: signature presence cannot distinguish forged from genuine.

Hygiene: the meta SIGKILLs both orphaned descendants after recording
(bounded `sleep`s that self-exit anyway); never gated.

## Exact evidence

Mandated seven-flag battery (exact invocation):
`python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot
/usr/bin/godot --runs .shokunin/game-dev-2d/corpus/live/r63-author/runs
--probe-failing --probe-unrelated-error --probe-export-launch
--probe-godot-error --probe-stream-attribution --probe-crash-exit
--probe-timeout` → exit 0,
`runs/20261014T004113548836Z/verdicts.json` **PASS, 96/96 rows** (sha256
`d52a05ef0268496ce9e34662e3845c6b794f9318f275ea4bb0c00484e67ffdb5`); stdout
`corpus/live/r63-author/battery.stdout`. Row arithmetic: 81 CASES + 2
mutants + 4 unrelated-error + 9 meta/probe rows (4 unconditional:
save-process, crash, pipe-EOF, signature-spoof; 5 opt-in). The two designed
inner `FAIL` lines (`godot_error_unrelated`, `stream_reject`) unchanged.

Prior-row stability — 7-field diff `(script, flags, expected_exit,
actual_exit, signature, verdict, error)`:
- vs my **pre-edit** pristine-worktree run
  `runs/20261014T003829532517Z/verdicts.json` (PASS 94/94, sha256
  `b8aa384996596ea16028c5dc3340480377f61e7f653dc1896c3726189705d6c3`):
  **94 common rows, 0 mismatches**; new-only
  `{descendant_pipe_forged_signature_release, probe_descendant_signature_spoof}`;
  baseline-not-in-new `[]`.
- vs the r62 named non-author receipt
  `corpus/live/r62-verifier/runs/20261014T001002305311Z/verdicts.json`:
  **94 common rows, 0 mismatches**.

New rows measured in the landed battery:
- `descendant_pipe_forged_signature_release`: expected/actual `0`, verdict
  **PASS**, error None — the documented forgery accepted.
- `probe_descendant_signature_spoof`: verdict **PASS**; hold arm
  `timed_out=true`, `child_exit_at_timeout=0`, `marker_observed=true`,
  `write_ppid=1573 ≠ godot_pid=1071603`, `descendant_alive_at_return=true`,
  `inner_classification=false`, `elapsed 3.001s`; all eight discriminations
  `true`.

Separate leg: `--fault-injection` →
`fault-runs/20261014T004113558828Z/fault-verdicts.json` outer **PASS**
(sha256 `cd49178d1f70d6a05dc89abffb6d9f756f22cb258b9f1854133597e4592849de`),
designed inner hang/unrelated FAILs — unchanged (fault path returns before
CASES/meta by construction).

Labrat (single dispatched probe, agent `78f291d6`): hypothesis
**CONFIRMED** — read-only verification of the above receipts against the
verbatim production source (its seat lacked exec/write capability, so it
audited rather than re-executed; limitation disclosed). It also noted
`descendant_alive_at_return=true` on the release arm is an exit-race
artifact (pid probe ran while the descendant was mid-exit) — benign, and
`write_ppid=1573` is this host's subreaper constant.

## Per-axis claimed verdict (author claim; named non-author replay still due)

- **depth — improved (candidate)**: the merged-stream signature check is now
  pinned as origin-blind with a tracked, replayable forgery boundary —
  post-death descendant writes satisfy signature presence; the only
  separating evidence is `timed_out`/`child_exit_at_timeout`, which the
  release-before-bound arm never trips.
- **coverage — improved (candidate)**: 94 → 96 rows (+1 CASES
  forgery-accepting row, +1 eight-discrimination meta).
- **calibration — unchanged**: no classifier edit; all 94 prior rows
  field-identical on both diffs.

## UNKNOWNs / retained caveats

- The forgery row is a *documented* accepting boundary — it asserts runner
  semantics as observed, not a fix. Any future hardening (per-stream
  attribution, process-group kill, drain policy) must re-measure every row
  here; the surface is implementation-bound to `run_process`'s
  `subprocess.run(capture_output=True, timeout=N)` shape.
- Bounded to Linux headless Godot 4.7.2 + this host's POSIX semantics;
  reparent target (ppid 1573, `systemd --user`) is this session's
  subreaper — other hosts may show pid 1; the `write_ppid != godot_pid`
  discrimination is host-agnostic.
- Timing margins: forge write lands ~0.1–0.2s after child exit (gate polls
  at 0.05s); the release arm returns ~0.6s — ~7.4s margin to the 8s CASES
  bound; the hold arm's ~6.5s pipe release is ~3.5s past the 3.0s meta bound
  (knee at release ∈ (2.6, 2.7]s per r62 — my arms sit far outside it on
  both sides).
- `--spawn-forge-hold` under the 8s CASES bound also forges a PASS (release
  ~6.5s < 8s) — measured in scratch as bound-dependence evidence; the
  tracked meta uses 3.0s so the same arm lands as the TIMEOUT record. Both
  directions of the boundary are bound-relative, as claimed.
- The `descendant_alive_at_return=true` on the release arm is a pid-probe
  race with the descendant's own exit (labrat-noted); the CASES record
  carries no such field, so it gates nothing.
- Not probed: forged writes to only one captured stream, descendant chains
  >1 deep, >64KiB descendant output, Windows/macOS, exported builds,
  signature-substring (vs line) forgery variants.

No commit, no push/merge, no LOG/SCORECARD write; adjudication and named
non-author replay follow.
