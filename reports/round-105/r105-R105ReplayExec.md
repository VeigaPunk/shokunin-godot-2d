# r105 seat report — R105ReplayExec (executor)

Verbatim final output of L2 `W2RoundGameDev2d.R105ReplayExec` (round 105, batched swarm; transcript `history://W2RoundGameDev2d.R105ReplayExec` is session-scoped and not evidence — this file is).

---

Done. K3 claim landed: measured, host-scoped, doc-honest.

## Files touched (exclusive write set)
- `corpus/fixtures/r105_phys_replay.gd` — new; `extends SceneTree`, 3 arms (`inproc`/`digest`/`perturb`), one `PASS r105_phys_replay <arm> …` line per run, `FAIL … quit(1)` on divergence, digests on separate `REPLAY` diagnostic lines so the pinned PASS line stays host-stable.
- `corpus/knowledge/2026-10-19-physics-replay-boundary.md` — new, contract shape (`source:`/`verified-at:`/`recheck:` headers, `## Claim/Evidence/Decision/Limits`, cites S009, S010, S025 tier-B-lead-only, S030).

## CASES tuples (for L1 — do not edit run_battery myself)
```python
("r105_phys_replay_digest", "r105_phys_replay.gd", ["--arm=digest"], 0,
 'PASS r105_phys_replay digest bodies=8 above=true max_speed_ok=true char_inrange=true'),
("r105_phys_replay_inproc", "r105_phys_replay.gd", ["--arm=inproc"], 0,
 'PASS r105_phys_replay inproc equal=true bodies=8 above=true max_speed_ok=true char_inrange=true'),
("r105_phys_replay_perturb", "r105_phys_replay.gd", ["--arm=perturb"], 0,
 'PASS r105_phys_replay perturb differs=true bodies=8 above=true max_speed_ok=true char_inrange=true'),
```
No `user://` writes → no XDG env needed. Wall: digest ~2.7 s, inproc ~4.6 s, perturb ~5.0 s (8 s battery cap).

## Measurements (serial, scratch `/var/tmp/gd2d-r105/R105ReplayExec/proj`, `godot 4.7.2.stable.arch_linux.ed1daf0bf`)
- Cross-process census: **20/20 runs → 1 distinct digest** without `--fixed-fps`; **20/20 → 1 distinct digest** with `--fixed-fps 60`; both sets identical value `85a25c98…70870d9`.
- In-process: 5/5 `inproc` runs `equal=true` (fresh worlds, identical digest).
- Perturb control: 4/4 runs `differs=true` — `dx=1e-4` → `5beeda4e…b7faef`. Digest discriminates.
- Invariants every run: `bodies=8 above=true max_speed_ok=true char_inrange=true`; zero `ERROR:`/`FAIL` lines, zero nonzero exits.

## Doc quotes (≤25 words, URL + section)
- S009 physics_introduction, **Warning**: "Physics in Godot, regardless of physics engine, is **not** deterministic … not guaranteed to run the same way for seemingly identical situations." Also §Physics process callback: "The physics engine runs at a fixed rate (a default of 60 iterations per second)."
- S010 physics_interpolation_introduction, §Physics ticks and rendered frames: "The physics proceeds at a fixed tick rate … which defaults to 60 ticks per second."
- S025 issue #112976 (opened 2025-11-20, milestone 4.7, closed via godot-docs#11803): reporter — identical inputs diverge with ≥3 moving bodies + scene reload from `_process`; maintainer AThousandShips: "the lack of determinism is not a bug." Kept as tier-B lead only.

## Commands + output tails
```
godot --headless --path <scratch> --script res://r105_phys_replay.gd -- --arm=inproc
REPLAY arm=inproc equal=true
PASS r105_phys_replay inproc equal=true bodies=8 above=true max_speed_ok=true char_inrange=true  rc=0

godot --headless [--fixed-fps 60] --path <scratch> --script res://r105_phys_replay.gd -- --arm=digest   ×20 each
REPLAY arm=digest digest=85a25c9879be89b7e4d636f63c1cf2a440e281d704b8a034c6d0be1e030870d9 … (all 40)
PASS r105_phys_replay digest bodies=8 above=true max_speed_ok=true char_inrange=true  rc=0

godot --headless --path <scratch> --script res://r105_phys_replay.gd -- --arm=perturb   ×4
REPLAY arm=perturb base=85a25c98… pert=5beeda4e… differs=true
PASS r105_phys_replay perturb differs=true bodies=8 above=true max_speed_ok=true char_inrange=true  rc=0
```

## Knowledge rule landed
On this host replay is bit-identical — recorded as host-scoped `[obs]`, explicitly *not* a guarantee (S009 Warning). Practitioner rule: assert invariants/tolerances, record digests, require a perturbation negative control, never retry-until-match, never pin a raw cross-process digest in a shared gate.

## Risks/limits
Pinning `equal=true` for `inproc` is honest on this host (45/45 equality observations) but is the least-doc-guaranteed pin of the three; if a future build flakes it, the PASS line is designed to fail loudly (that's the finding, not a bug to suppress). Untested: S025's `_process`-timed reload trigger, threaded physics, 3D/Jolt — all declared in `## Limits`.
