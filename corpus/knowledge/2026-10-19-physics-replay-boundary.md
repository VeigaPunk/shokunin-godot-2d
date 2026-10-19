# Physics replay boundary — invariants over identical digests

source: S009 — https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html — Warning + §Physics process callback, Godot Engine 4.7 docs; S010 — https://docs.godotengine.org/en/4.7/tutorials/physics/interpolation/physics_interpolation_introduction.html — §Physics ticks and rendered frames, Godot Engine 4.7 docs; S025 — https://github.com/godotengine/godot/issues/112976 — maintainer comment thread (tier B lead only); S030 — corpus/fixtures/r105_phys_replay.gd round-105 fixture
verified-at: 2026-10-19 (godot 4.7.2.stable.arch_linux.ed1daf0bf; corpus/fixtures/r105_phys_replay.gd --arm=inproc)
recheck: on-release — from lane root: `timeout --signal=TERM --kill-after=2s 1800s python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --res-uid-order forward --probe-res-uid-shared` → expects `PASS r105_phys_replay_inproc:` (runner stages fresh scratch projects; full battery, not just this row)

## Claim

On this host and engine build (4.7.2.stable.arch_linux.ed1daf0bf, headless, x64),
an identical scripted 2D scenario — 8 RigidBody2D boxes dropped onto a
StaticBody2D floor between walls, plus a CharacterBody2D driven by a fixed
velocity stream — replays **bit-identically**: one sha256 state digest
(positions, rotations, linear and angular velocities, sleep flags at full float
precision) across 240 physics ticks. This is an observed host property, not an
engine guarantee; the docs explicitly disavow determinism.

## Evidence

- [obs] 20 serial `--arm=digest` runs **without** `--fixed-fps`: 1 distinct
  digest (`85a25c98…70870d9`). 20 serial runs **with** `--fixed-fps 60`: 1
  distinct digest, the same value. Fixed tick rate therefore dominates any
  render-cadence coupling for this scene on this host.
- [obs] 5 serial `--arm=inproc` runs: `equal=true` 5/5 — two fresh worlds
  (queue_freed and rebuilt inside one process) converged to the identical
  digest each time.
- [obs] Discriminating negative control: `--arm=perturb` nudges body 0's
  initial x by 1e-4 px → digest `5beeda4e…b7faef`, `differs=true` on 4/4 runs.
  A constant or insensitive digest would fail this arm, so the equality
  observations are not vacuous.
- [obs] Gameplay invariants held in every run: 8/8 bodies above the floor,
  max linear velocity < 1200 px/s, character inside its scripted corridor.
- [obs] S009, *Physics introduction → Warning*: "Physics in Godot, regardless
  of physics engine, is **not** deterministic … not guaranteed to run the same
  way for seemingly identical situations." Same page, *Physics process
  callback*: "The physics engine runs at a fixed rate (a default of 60
  iterations per second)."
- [obs] S010, *Physics ticks and rendered frames*: "The physics proceeds at a
  fixed tick rate … which defaults to 60 ticks per second." Interpolation
  smooths rendering between ticks; it says nothing about replay equality.
- [obs] S025 (tier B lead), godotengine/godot issue #112976 (opened 2025-11-20,
  milestone 4.7, closed via docs PR): a same-build reproduction where
  identical inputs gave different results, attributed to ≥3 moving bodies plus
  scene reload from `_process` (unsynced to physics ticks). Maintainer
  AThousandShips: "the lack of determinism is not a bug." Closed by
  godot-docs#11803 adding the S009 warning.
- [inf] My fixture avoids the S025 trigger shape: worlds are built and
  torn down at physics-tick boundaries, and no `_process`-timed reloads
  occur. [unk] Whether introducing S025's reload pattern reproduces
  divergence on this build — not measured.
- [inf] Bit-identical cross-process replay here plausibly follows from
  Godot Physics 2D's single-threaded solver, fixed tick rate, and identical
  build + host; the docs warning reserves timing-dependent factors (threaded
  physics, `_process`-synced inputs, different builds) that this scene does
  not exercise.

## Decision

Replay tests assert **invariants and tolerances** — body counts, boundary
containment, speed bounds, scripted-input reach — and record the digest as
evidence, never as a required equality. A replay harness compares digests
in-process or records them for a census; it must never retry-until-match and
must never pin a raw cross-process digest in a shared gate, because the docs
give no such guarantee and pinning it would encode an unguaranteed property.
Every digest-based fixture carries a perturbation negative control proving the
digest discriminates; a divergent digest paired with held invariants is a
recorded finding, not a failure.

## Limits

Single host, single build, headless, Godot Physics 2D (not Jolt/Godot
Physics 3D), non-threaded physics, 120 TPS, ≤10 rigid bodies, no scene
reload, no real input devices, 240-tick horizon (~2 s sim). Bit-identity
observed on this host does not transfer to other builds, OSes, CPU features,
threaded physics, `_process`-driven scene management, or longer horizons.
The PASS lines pin invariants, in-process equality, and perturb-differs —
deliberately not the digest value.

## Claim-to-CASES binding (Q6)

Exact five-field tuples and byte-exact PASS signatures:
`reports/round-105/r105-claim-tuples.json` keyed by case below. Two serial receipts:
`reports/round-105/r105-battery-receipts.json`, matching keys and
`signature_in_output=true`. `REPLAY` digest diagnostics are not the PASS pin.

| claim | exact tuple key | fixture / arm / expected exit |
|---|---|---|
| gameplay invariants | `r105_phys_replay_digest` | `r105_phys_replay.gd`, `--arm=digest`, 0 |
| host-observed in-process equality | `r105_phys_replay_inproc` | `r105_phys_replay.gd`, `--arm=inproc`, 0 |
| perturbation discrimination | `r105_phys_replay_perturb` | `r105_phys_replay.gd`, `--arm=perturb`, 0 |

### Invariant bounds and resolution (Q17)

Fixture constants and predicates (`r105_phys_replay.gd:28-35,154-175`):
8 rigid bodies; every box center `y < 480 px`; final maximum box speed
`< 1200 px/s`; character `170 < x < 600 px` and `y < 480 px`; 240 physics ticks
at 120 TPS; perturbation `dx = 1e-4 px`. [obs] PASS records those inequalities,
not numeric distances to each bound. [unk] Exact final speed/position margins
were not emitted and are not inferred from `true` booleans. The SHA-256 diagnostic
hashes binary double state bytes; no universal determinism tolerance is claimed.
