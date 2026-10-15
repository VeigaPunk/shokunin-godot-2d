# r88 verifier-r2 — independent non-author verification of folded bytes (`fd59c11`)

Seat `VERIFIER-R2` (g2d lane r88, independent non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7, 32-core. Target commit:
`fd59c11be1fc02c35a6b5e1759df5cd103e7ae3d` (*r88 fold: pid ports + rc guards,
v!=0 sync recipe, crossing ray, playing assert, phys_peer 6-payload envelope,
SP1/2*). Fold report: `reports/round-88/r88-fold.md`; prior verifier:
`r88-verifier.md` (pre-fold `3c47eee`). Receipts: `corpus/live/r88-verify2/`
(`RECEIPTS.md` there).

No `lsp` device on this host (same state as every r88 seat); this seat made no
edits to tracked files — verification only. No commits. All artifacts are
untracked scratch + this report.

## Method — frozen tree

```
git archive --format=tar fd59c11 | tar -x -C corpus/live/r88-verify2/tree
```

- **File-set**: `git ls-tree -r --name-only fd59c11` (97 727) vs extracted
  `find` (97 727) — **0 diffs** (`freeze/fileset-diff.txt` = 0 lines).
- **Content**: `GIT_DIR=$PWD/.git GIT_WORK_TREE=…/tree git diff --quiet
  fd59c11` → **rc=0**.
- **Blobs** (frozen tree): `r88_surfaces.gd` sha `9631961d…` == fold's
  declared final-byte sha; `run_battery.py` sha `c3ae36a6…`;
  `input_lattice.gd` `7624aa97…`; `r88_spawnable.tscn` `89b9ddbe…` ==
  prior-verifier's published sha. Battery scratch copies re-pinned to the
  same shas at run time — the battery exercised the committed bytes.
- `ast.parse` on frozen `run_battery.py`: clean; CASES census **208** + 7 meta
  rows = **215**; `input_lattice_phys_peer` evidence = **6-tuple** (deltas
  0–5 verbatim); `r88_surfaces_sprite_phys` allowlist = exactly the one
  `ERROR: Index p_frame = 3 is out of bounds (vframes * hframes = 2).` entry.
- Focused arms run from `corpus/live/r88-verify2/scratch/` (battery launch
  shape: `godot --headless --path scratch --script res://<script> --
  --arm=<arm>`), payloads byte-compared against the **committed** CASES
  signatures via AST extraction (`probes/check_pins.py`), not eyeballed.

## Per-item results

| # | fold item | verdict | evidence |
|---|---|---|---|
| F1 | MP ports `40000 + pid % 20000`, `rc_s`/`rc_c` guards | **VERIFIED** | static: both arms identical recipe, `rc_s` checked **before** client exists, `rc_c` after, no `41777/41778` anywhere; dynamic: **67 committed MP-arm reps** (29 loopback, 28 spawner, 10 offline) incl. **54 concurrent launches** under load ≤39 — **zero `Couldn't create an ENet host` on any stderr**, payload uniq=1 each, distinct `uid_c` per process. Negative control (`loaded/portguard`): pid-window UDP ports pre-bound → 3/3 bind losers die `FAIL … server_rc=20`, rc=1, ENet error on stderr, **no PASS line** — an ENet-create error cannot pass; unbound control rep PASSes |
| F2 | `sprite_phys`/`light_props` v!=0 sync | **VERIFIED** | both sync guards present (frozen lines 300/373) + `for i in N-1`. Mode census via seat twin (`MODE guard=%d` instrumentation on committed bytes): **guard=0** in default launch shape across quiet serial, 32-hog 12-way concurrency, `taskset -c 0-3`, injected `_initialize` delay 0–500 ms, `--frame-delay 30`, `--fixed-fps 30` (116 reps); **guard=1** under `--fixed-fps ≥240` (22 reps — process frames outpace steps, the Case-A-family shape). Committed bytes held the pins in **both** shapes: 52+52 reps (quiet 24, hogged 20, fixed-fps 8 each) **all byte-identical** — `74.5675` ×4 bodies / `118.4614` |
| F3 | `ray_through_occluder` crossing ray | **VERIFIED** | frozen line 311 casts `(-50,-35)→(50,-35)` — crosses the polygon's global band x∈[0,10], y∈[-40,-30] (x∈[5,10] slice). Seat probe (`probes/ray_probe.gd`): same triangle as `StaticBody2D`+`CollisionPolygon2D` → **new ray HITS** (`body_hit_new=false`, collider `StaticBody2D`), **old vacuous ray EMPTY** (`body_hit_old=true`); occluder-only → new ray EMPTY → `ray_through_occluder=true` is falsifiable and still true |
| F4 | `audio_pos` liveness assert | **VERIFIED** | `if not p.playing: _fail("play_not_accepted")` immediately after `p.play()` (frozen 416–418). Negative control (`r88v_noplay.gd` = committed bytes −`p.play()`): `FAIL r88_surfaces audio_pos reason=play_not_accepted`, rc=1 — the pinned payload can no longer be emitted with `play()` removed |
| F5 | `input_lattice_phys_peer` 6-payload envelope | **VERIFIED** | 140 reps: 20 quiet (all delta=0) + **120 under 32 hogs / 12-way launch concurrency** → `ev_step_delta` **{0:70, 1:30, 2:17, 3:8, 4:10, 5:5}** — all six modes reproduced including the fold's new delta=5; every unique payload **byte-matches an envelope entry** (AST-extracted); **no 7th mode** in 140 reps (would fail loudly — none appeared) |
| F6 | Full battery on final bytes under load | **VERIFIED** (rep2; rep1 recorded below) | rep2 `runs_load2`: **215/215 PASS**, rc=0, `r88_expected_errors_all_matched=true`, `dead_entry_count=0`, `census_bare_classifier_consistent=true`, all 37 discriminations true; phys_peer landed delta=0 in-battery. Verdict/exit/signature tuple-compare vs fold `runs3` (same final bytes): **0 diffs on 215 common rows** |
| SP1/SP2 | simplifier deletions | **VERIFIED** | `uping` grep count 0; `func _body` is 2-arg; `MpLimb` carries only `ping` |

## rep1 under extreme oversubscription (recorded, classified)

`runs_load` (32 `yes` hogs + 12-way concurrent arm launches overlapping the
battery; load ~35–40): **212/215**, 3 non-PASS:

- `audio_playback` (pre-existing, untouched): exit 2/0 — `AUDIO ASSERTION
  FAILED: expected in-tree player playback to advance … position did not
  advance` — Dummy-driver advance starved by oversubscription; the
  r59/r66-documented class.
- `audio_bus_route_invalid_control` (pre-existing, untouched): exit 2/2 with
  `advanced=false` — the fold's own documented 1/185 load flake; its
  comma-prefix allowlist entry went dead (`matched_lines=0`) →
- `probe_error_clause_surface` meta FAIL = consequential census
  inconsistency (`dead_entry_count=1`, `census_bare_classifier_consistent=
  false`) — same chain as fold runs1.

**All 9 fold-touched rows PASSed in this same rep** (8 `r88_surfaces_*` +
`input_lattice_phys_peer`), and `r88_expected_errors_all_matched` stayed
`true` even in the failing rep. Both are non-r88 rows on untouched bytes;
the class is load-induced, loudly caught, and non-recurring — rep2 on the
identical frozen tree at saner load (10 hogs, ~15–27) is 215/215.

## Census / hygiene

- All 32 of this seat's `yes` hogs killed at exit (`hog.pids` recorded then
  reaped); post-exit `ps`: **zero `r88-verify2` processes** — surviving
  `yes`/`godot` on the host are foreign seats (r92/r96/r97/r100 lanes,
  unrelated PPIDs).
- Zero stray godot attributable to this seat; every launch `timeout`-bounded.
- No tracked writes by this seat: `git status` shows no modification
  attributable to me; the only new tracked-path file is this report (seat
  deliverable per lane convention). **Foreign in-flight work observed
  during the session and left untouched**: HEAD advanced `fd59c11` →
  `520ed6d` (r90-boundary receipts, committed 16:22 by another seat —
  `fd59c11` remains an ancestor) and an uncommitted working-tree edit to
  `corpus/fixtures/run_battery.py` (r89-author `geo2d_lattice_*` CASES
  rows, mtime 16:29) appeared mid-session. None of it entered my
  verification: every claim here is against the `git archive fd59c11`
  frozen extraction (content-identical to the commit, rc=0).
- Footprint: `corpus/live/r88-verify2/` ≈ 1.7 GB untracked (`tree/` frozen
  extraction dominates), prunable.

## Residual risks / disclosures

- **R1** — rep1 is not green; only rep2 is. The dispatch's 215/215 is met by
  rep2 under load; rep1 records a measured instance of the pre-existing
  audio-load-flake class on rows the fold did not touch. Same "clean-condition
  reproduction" criterion the r88-verifier applied.
- **R2** — the guard=0/guard=1 mode census is measured on the instrumented
  twin (committed bytes + `MODE` line); the pinned reps themselves ran
  committed bytes. On this host the committed file is mono-modal (guard=0) in
  the default launch shape across quiet+hogged+affined+delayed startups —
  `--fixed-fps ≥240` is what opened the guard=1 window here. The sync recipe
  absorbed both (pin identical in 104 committed reps + 22 guard=1 twin reps).
- **R3** — the `while v == ZERO` sync has no internal bound: if the body never
  integrates the arm hangs — caught loudly by the battery's 8 s per-row
  timeout (a FAIL, not a wrong answer). Observed zero times in ~250 launches.
- **R4** — `pid % 20000` collisions remain theoretically reachable across
  processes; now proven to fail loudly (`server_rc=20` → `_fail`, no PASS,
  unallowlisted stderr) rather than cross-connect — the intended trade,
  exercised live.
- **R5** — delta≥6 phys_peer payload remains unobserved (my 140 + fold's 150 +
  critic's 60+ reps); the enumerated envelope admits only measured payloads —
  a 7th mode fails loudly.

## Verdict

**VERIFIED with one recorded reservation.** Every fold item reproduces on the
committed `fd59c11` bytes: F1 pid-ports + rc guards eliminate the
cross-connect class (zero ENet errors in 67 MP reps incl. 54 concurrent under
load, and a forced bind-loser provably cannot PASS); F2 pins are now
mode-invariant by construction and byte-held across both exercised startup
shapes; F3's ray provably crosses the occluder band (falsifiable); F4's
liveness guard fails loudly on the negative control; F5's 6-payload envelope
covers all six reproduced modes with no 7th observed; SP1/SP2 byte-clean;
full battery **215/215 PASS** on the frozen bytes under load with
`r88_expected_errors_all_matched` green and 0 tuple diffs vs the fold's own
receipt.

Reservation: battery rep1 under extreme oversubscription (load ~35–40) hit
the documented pre-existing audio load-flake class on two non-r88 rows —
loudly caught, non-cascading, non-recurring at saner load. Recorded, not
excused; the flake class predates this fold and is owned by no r88 item.

Files (all untracked under `corpus/live/r88-verify2/` + this report):
`tree/`, `scratch/`, `freeze/`, `arms/` (incl. mode/delay/ff240 twins),
`loaded/` (mp_conc1–3, portguard, race_hogged, pp_quiet, pp_hogged),
`battery/runs_load{,2}` + console logs, `probes/` (seat tooling),
`env.txt`, `RECEIPTS.md`.
