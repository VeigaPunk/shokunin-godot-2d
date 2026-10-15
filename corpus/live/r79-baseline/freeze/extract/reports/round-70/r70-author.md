# game-dev-2d round 70 — author (seat: author; **operator-substituted**, host: devin)

> Provenance: the r70 author seat died to the free-model rate-limit
> massacre (reset 16:01 UTC). Operator authored this diff under disclosed
> substitution. Independent verification is left to post-reset seats —
> nothing here is self-certified beyond the recorded own-replay.

## Declared move (verbatim)

First-contact a NEW 2D runtime: LOVE 11.5 headless — "LOVE with
`t.window=false` runs a deterministic fixed-dt love.update loop headless,
and its child-process stdout surface (io.popen / os.execute) exhibits a
measurable write-visibility window analogous to Godot midlineforge's
gap-relative fabrication bound — i.e., the phenomenon is engine-general."

## Landed changes

- `corpus/fixtures/love_probe/conf.lua` (NEW): `t.window=false`,
  graphics/window/image/audio modules off — minimal headless profile.
- `corpus/fixtures/love_probe/main.lua` (NEW): arms dtcadence / popen /
  osx / pump, exact-stdout `LOVE-ARM <arm> | k=v` lines.
- `corpus/fixtures/love_battery.py` (NEW sibling runner): one `love <dir>`
  run, ARM parser, 15 pinned cases (exact bytes where deterministic,
  measured bounds where jittered), `verdicts.json` under ignored
  `corpus/live/runs/love-*`. `run_battery.py` untouched → all prior
  Godot rows byte-stable by construction.

## Measured result (battery `love-20261014T135430Z`: 15/15 PASS)

Verdict on the claim — **viability confirmed; "engine-general window"
FALSIFIED at the engine layer**:

- Headless viability: clean (`love --version` 11.5; probe exit 0).
- **Update cadence is uncapped headless**: dt_mean ≈ 1.044ms (~960Hz),
  dt_min 0.002ms — the "fixed-dt 60Hz" half of the claim is wrong on this
  build; vsync/fps-cap are windowed-mode phenomena.
- **No fabrication window at LOVE's layer**: io.popen write→readable
  latency tracks the writer — l2_wait_ms ≈ 120.7 for a child sleeping
  120ms (the wait IS the child's delay, not an engine-bound window);
  lines byte-exact; EOF wait <0.2ms. The Godot midlineforge bound was a
  property of the Godot-runner pipe plumbing, not engine-general child-
  stdout semantics. Boundary note: this scopes the claim — the Godot
  phenomenon lives in the harness/descendant-pipe layer, which LOVE
  does not implement the same way (no equivalent midlineforge seam).
- `os.execute` on this build returns Lua-5.1-shape raw status
  (exit 3 → 768), single value — NOT the 5.2+ (ok,"exit",code) triple.
- `love.event.pump` not required for the update loop headless.
- Blocking io.popen reads suspend the update loop entirely (ticks frozen
  during a blocked read — structural, no pump).

## Evidence

- `python3 corpus/fixtures/love_battery.py` → 15/15 PASS, exit 0,
  LOVE_PROBE_DONE, ~0.4s wall. 3 spot reps byte-consistent on
  deterministic keys (dt/timing keys within pinned bounds all 3 runs).
- Operator viability receipts: `corpus/live/runs/love-*/`.

## Remaining unknowns (handed to next-round seats)

- Whether LOVE has ANY descendant-stdout-capture seam where a
  fabrication-style window could exist (sockets? love.thread channels?);
- love.timer resolution floor (dt_min 0.002ms = jittered sub-ms reads);
- love.thread/love.filesystem sync edges — greenfield.
