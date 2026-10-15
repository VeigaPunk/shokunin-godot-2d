# Round 64 — critic: adversarial attack on the while-live signature gate

Seat: critic (LEAF). I wrote only this report and
`.shokunin/game-dev-2d/corpus/live/r64-critic/` (symlink target:
canonical repo `corpus/live/r64-critic/`). No tracked file, CASES row,
lesson, LOG, or SCORECARD touched; no subagent dispatch; no git mutation.

## Arm under attack

The author's `probe_while_live_signature_gate` landed mid-flight:
`corpus/fixtures/run_battery.py` +224/−0 (`gated_signature_run` +
12 discriminations; row verdict PASS, battery 97/97 at
`corpus/live/r64-author/runs/20261014T013826495191Z/verdicts.json`). Gate
semantics: `selectors` read over both pipes at ≤5ms tick; on each readable
fd `alive_before = process.poll() is None` is sampled **before**
`os.read`; the marker-completing chunk's `alive_before` decides
`gated_signature_accepted`. Verified additive-only via ast:
CASES literal **byte-identical** HEAD↔worktree; changed functions =
`main` only; new function = `gated_signature_run`; zero deletions.

## Method

`drive_wlg.py` runs real headless Godot 4.7.2 children
(`proj/descendant_pipe_probe.gd` copied byte-identical; `proj/wlg_critic_probe.gd`
is my forgery mutant) under six gate variants: `poll` (author's
semantics), `kill0` (liveness = `os.kill(pid,0)` — the repo's own
`pid_alive()` shape, run_battery.py:629), `stale` (liveness snapshotted
before each `select`, reused for that iteration's reads), `delayed`
(poll gate + injected post-wake stall), `batch` (communicate-then-check),
`fine` (poll gate + `pidfd` death edge + 0.5ms tick for true timing).
Death-edge timestamps are reported separately from `alive_at_marker`,
which is frozen at observation. `verbatim_gate.py` ast-extracts the
landed `gated_signature_run` and runs it **unmodified** on the tracked
arms. 203 runs total; `wlg-verdicts.json`, `wlg-verdicts-extra.json`,
`verbatim-gate.json`.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python `3.14.7`,
Linux `7.2.3-arch1-3`, `/usr/bin/sh` → bash.

## Headline result — claim CONFIRMED within its stated scope, and implementation-bound

The landed gate discriminates exactly as predicted on the tracked arms:
independent replica — genuine 12/12 (fine) + 12/12 (poll) ACCEPT,
detach 8/8 ACCEPT, forge_release 0/25 REJECT, forge_hold 0/5 REJECT;
verbatim production `gated_signature_run` agrees on every arm (genuine
+detach ACCEPT at +67ms lead; release×3 + hold REJECT at −32ms lead,
`inner_classification=True` on release — the r63 divergence in one
record). No falsification of the row as worded. The interesting findings
are the three measured ways the result is bound to its implementation,
plus one already-disclaimed boundary proven live.

## Attack (1) — PIPE BUFFERING: falsified as posed; bites in the reverse direction

Could the forged signature sit in the kernel pipe buffer *before* the
child's death and fool an alive-at-observation check? **No, and
provably so**: the fixture's forge is reparenting-gated, so the bytes do
not exist before death, and data cannot be readable before it is
written. Across 25 `fine`/`poll` reps the forged marker became readable
**26.7–34.8ms AFTER the pidfd death edge** (`t_dead_pidfd − t_marker`,
every rep strictly negative). Kernel buffering can only delay
observation of a *pre-death* write past the death edge — the
false-negative direction, measured under attack (3). Buffering does not
create the hole; the liveness primitive does (attack 2).

## Attack (2) — RACE WINDOW: the zombie trap is real and deterministic; the landed arm dodges it by choice of primitive

- **`kill0` gate (the `pid_alive()` shape): 13/13 forged signatures
  ACCEPTED** — `forge_release` 10/10, `forge_hold` 3/3. Every
  forged-observation shows `/proc` state **`Z`**: the child is a dead,
  unreaped zombie, and `os.kill(pid,0)` reports it alive because a zombie
  still exists until `waitpid`. The forged write lands ~32ms post-death;
  nothing in the read loop reaps in between, so the trap is not a race —
  it is deterministic. This is the exact trap the brief predicted; the
  claim survives only because the author liveness-checks with
  `process.poll()` (waitpid semantics: reaps, returns exit code). A
  future "simplify to `pid_alive()`" refactor silently flips the row to
  forge-accepting — **the primitive choice is load-bearing** and is
  currently carried only by the bounded_claim prose ("poll()-gated"),
  not by any code comment.
- **`stale` ordering: defeats only sub-tick forgeries.** The tracked
  arms' ~32ms forged lag ≫ 5ms snapshot staleness → 10/10 REJECT. My
  `--forge-fastpost` mutant (busy `read /proc/self/stat` ppid loop, no
  `sleep 0.05`) lands the forged write **~22µs post-death**
  (fine-measured margin −2.2e-05s) — inside one snapshot window →
  **12/12 ACCEPT** under stale ordering (death edge and forged chunk
  coalesce in one tick). Under `poll`-per-event ordering (the author's):
  **6/6 REJECT**, and `fine` **6/6 REJECT** at −22µs. A gate that
  checks liveness once per select iteration *before* blocking is
  defeated by any forger faster than its own tick; the landed
  post-wake-per-event check is the correct ordering and survives
  µs-close writes.
- Minor note on `dead_observed_at < marker_observed_at` (strict `<`):
  for the tracked arms robust (32ms lag ≫ tick), but a fastpost-class
  write lands both timestamps equal (`dead@ == marker@` observed on my
  fastpost reps) → the ordering clause fails → meta FAIL despite the
  gate rejecting correctly. Fails loudly, never slips;
  `child_alive_at_marker_observation is False` is the load-bearing
  clause — `<=` or dropping the ordering comparison would harden it.

## Attack (3) — FALSE NEGATIVE on the genuine arm: measured knee at ~70–75ms reader stall

Genuine-arm margin (t_death_edge − t_marker_readable): **+65.0..+70.9ms**
across 15 `fine` reps (author: +67..69ms — agreement). The marker is
flushed promptly mid-teardown (state `R`/`S` at observation), not
buffered to exit. Injected reader-stall sweep on the genuine arm:

| injected stall | accepted | outcome |
|---|---|---|
| 5/10/20/50ms | 24/24 | ACCEPT — stall < margin |
| 70ms | 4/6 | knee: 2 post-death observations → REJECT |
| 80ms | 1/6 | mostly REJECT |
| ≥100ms | 0/12 | deterministic REJECT of a GENUINE signature |

So the genuine leg survives up to ~65–70ms of reader-loop latency and
flips deterministically past ~75–100ms — ~14× the 5ms poll tick, a real
but bounded flake surface on a contended host (the author already
declares it; my number is the measured knee, not a guess). Direction
fails loudly via `genuine_never_observed_post_death` → row FAIL on a
healthy mechanism, never a silent accept. Separately: **`batch`
(communicate-then-check) rejects the genuine arm 3/3** — the claim is
only expressible under streaming per-event liveness; any batched
interpretation of "observed while alive" rejects every signature.

## Attack (4) — BYPASS: live-window forgery defeats the gate (the disclaimed boundary, proven)

`liveness-of-child ≠ authorship-of-write`. Mutant `wlg_critic_probe.gd`
arms — child prints the same `child_signature=withheld` banner and
`godot_pid`/`spawned_pid` provenance lines, but a descendant writes the
expected marker *inside* the child's live window:

| arm | forged write timing | gate verdict |
|---|---|---|
| `--forge-during-life` (child `OS.delay_msec(1200)` foreground wait; descendant writes +150ms) | margin **+1.125s pre-death** | **16/16 ACCEPT** (poll 8/8, fine 5/5, kill0 3/3) |
| `--forge-early` (ungated descendant echo, child exits ASAP) | lands inside the ~66ms live window | **10/10 ACCEPT** |
| `--forge-during-hold` (live-window write + 5s pipe hold) | live-window | **3/3 ACCEPT + TIMEOUT** |

A forged (provably descendant-authored, withheld-banner) signature is
accepted indistinguishably from a genuine one whenever the write lands
pre-death — and `--forge-early` shows even an immediate racy forger wins
every rep; the pre-death class is not exotic. The gate discriminates
*write timing*, never *provenance*. The author's `bounded_claim`
already disclaims exactly this class ("not a claim that
observation-time liveness proves authorship in general (a
pre-death-scheduled or faster-racing forge is out of scope)") — these
mutants prove the disclaimer is load-bearing, not hypothetical. If the
row's claim text ever shrinks to "discriminates forged from genuine",
it becomes false by measurement.

## Verdict

- **Not falsified within scope.** The literal claim — a `poll()`-gated
  read discriminates the tracked post-death forge arms from genuine arms
  — holds deterministically (0/38 forged accepts under waitpid ordering;
  48/48 genuine accepts at ≤50ms stall), independently reproduced on
  replica *and* verbatim production code.
- **Fragility notes worth carrying (fixable, small):**
  1. The gate is correct *because* the primitive is waitpid-shaped; the
     repo's `pid_alive()` (kill0) accepts the forgery 13/13 — a one-line
     comment in `gated_signature_run` pinning "poll()/waitpid, never
     kill(pid,0)" is the smallest safe correction.
  2. `dead_observed_at < marker_observed_at` strict `<` can collide on a
     sub-tick forger → loud FAIL despite correct rejection; `<=` or
     reliance on `alive_at_marker_observation` alone hardens it.
- **Bounded tradeoff the judge may weigh:** the genuine-leg flake knee
  (~70–75ms reader stall) is a measured retry surface on loaded hosts;
  it fails loudly. Not a defect.
- **Boundary proven, already disclaimed:** pre-death forgery is accepted
  29/29 — the claim's scope words are load-bearing; keep them.
- **Field stability:** CASES literal byte-identical; `main` is the only
  changed function; +224/−0; author's battery 97/97; 96 common rows 0
  field-mismatches vs pretree (author's own diff — I verified the
  code-level half, not their receipt diff).

## Artifact inventory (`corpus/live/r64-critic/`)

- `drive_wlg.py` (sha256 `ef5b857d…`) — six gate variants, arms matrix,
  injected-stall sweep; `verbatim_gate.py` (sha256 `aa75ae80…`) —
  ast-extracted production `gated_signature_run`.
- `wlg-verdicts.json` (`44ddb63c…`, 149 runs), `wlg-verdicts-extra.json`
  (`493de60a…`, 48 runs: fastpost + stall knee), `verbatim-gate.json`
  (`95d03d8a…`, 6 runs production code).
- `proj/descendant_pipe_probe.gd` byte-identical to fixture;
  `proj/wlg_critic_probe.gd` (`ebaf9195…`) mutant with
  `--forge-during-life`/`--forge-early`/`--forge-during-hold`/
  `--forge-fastpost`.

All spawned descendants were bounded `sleep`s or self-exited; orphan
reaping per-run; no stray processes remain.
