# Frontier pre-measurement: LOVE physics (box2d) world-step timing

Seat: g2d-frontier-b (wave-10, LEAF). Lane-repo: `~/Projects/shokunin/game-dev-2d-shokunin`.
Candidate under test: wave-11 "LOVE physics" — `love.physics` (Box2D) stepping, headless.

Runtime: `LOVE 11.5 (Mysterious Mysteries)` (`love --version`, `/usr/bin/love`), LuaJIT present (`jit=true`).
Host: this machine, headless profile from r70 (`t.window=false`, graphics/image/audio off).

> Naming note: the brief says `world:step` — the actual LÖVE 11.5 method is **`World:update(dt)`**
> (`world:step(...)` is nil; first strict probe pcall failed on it). Box2D internals call it
> `b2World::Step`. All measurements below use `world:update(FIXED)`.

Probe source: `corpus/live/frontier-lovephysics/phys_probe/{conf.lua,main.lua}` (phase machine:
viability → contact lattice → determinism → accumulator → scripted-jitter accumulator).
Variants: `phys_strict/` (all modules off except physics+timer+event), `phys_off/` (physics=false).
Raw output: `corpus/live/frontier-lovephysics/out/run-{1..7}.txt` (exit 0 every run, empty stderr).

## (a) Headless viability — POSITIVE

- `love.physics.newWorld(0, 9.81*64, true)` + `newBody`/`newCircleShape`/`newRectangleShape`/
  `newPolygonShape`/`newFixture` + `world:update` all work with `t.window=false` and
  graphics/image/audio modules off (`PHYS-VIABILITY | ... physics=true window=false graphics=false`).
- **Conf requirements**: `t.modules.physics` must be true (it defaults true; the r70 conf never
  touched it and it worked). With `t.modules.physics=false` → `love.physics == nil` exactly.
- Strict conf (everything off except physics+timer+event; data/math/system/thread/font/sound/
  video/inputs all false): world built and stepped fine — `phys_strict` printed
  `STRICT | stepped y=9.592001`, `pcall=true`. **No hidden module dependencies**; physics is
  standalone. (`love.data` only needed if you want `love.data.hash` for in-Lua digests.)
- Step cost on this host (PERF, 600-step 5-body scene): mean ≈ **0.0011–0.0014 ms/step**,
  min 0.0004, max 0.008 — trivially inside any wave-11 budget.

## (b) Determinism — byte-identical

Scene: ground + 4 dynamic bodies (2 stacked boxes, bouncing circle w/ initial velocity, polygon;
mixed restitution 0.1–0.85, friction 0.3–0.8), 600 × `world:update(1/60)`, full transform+velocity
dump of every body every 30 steps as `%.17g` (exact double round-trip).

- In-Lua digest identical all runs: `sha256=f96c129d503a6c136f3bcdc0122eb88f2ba3171d7149e39ac87089ca47ec5d24` (×7 runs).
- External check over the whole deterministic block (100 `PHYS-DET` + 83 `PHYS-EVT` + `PHYS-STEP`
  window + `PHYS-COUNTS` + `PHYS-DETERM`, 192 lines incl. all contact-event transforms):
  `grep -a '^PHYS-\(DET\|EVT\|STEP\|COUNTS\|DETERM\)' out/run-N.txt | sha256sum`
  → `e003c41715767e9012f965ddbe30919b64fb9bed9871642b57dc922859be3206` for N=1..7. **Byte-identical.**
- Event stream is also deterministic: `PHYS-COUNTS | steps=300 BC=12 EC=10 PRE=73 POST=73` every run.

## (c) Contact callback lattice — measured inside `world:update`

`world:setCallbacks(beginContact, endContact, preSolve, postSolve)`; each callback captured the
contacting body's `(y, vy)` plus a global `in_step` flag set only around the `world:update` call.

**Dispatch: every callback ran with `in_step=true` — fully synchronous inside `world:update`,
none pre- or post-call.** Per-contact order is always `BC → PRE → POST` within one update;
`EC` fires on a later update. `postSolve` arity on 11.5: `(fixtureA, fixtureB, contact,
normalimpulse, tangentimpulse)` — measured `nargs=2 types=number,number`.

Observable body state at dispatch time (the sync-edge analogue — what a callback *sees*):

| callback | dispatch point | observed transform |
|---|---|---|
| `beginContact`, `preSolve` (narrowphase path) | start of update (Collide, pre-integration) | **exactly `y_pre`/`vy_pre`** — b3 i=4: cb `y=519.94647216796875 vy=31.392002105712891` == `y_pre`/`vy_pre` |
| `beginContact`, `preSolve` (TOI/substep path — fast first touch) | mid-update, body advanced to just-touching pose | **neither pre nor post** — b1 i=73: cb `y=520.1500244140625` vs `y_pre=518.3232421875`, `y_post=511.13113403320312`; `vy=763.87` = `vy_pre + g·dt` (post-gravity, pre-impulse) |
| `postSolve` | end of update (impulse Report) | **exactly `y_post`/`vy_post`** — all 73 POST events match post-step state bit-for-bit |
| `endContact` | start of a *later* update | settled state (= prev post == current pre); b1 separated during step 73, `EC` dispatched at i=74 reading `y=511.1311` = `y_pre(74)` |

Other measured facts:
- `preSolve`/`postSolve` fire **every update while a contact persists** (b3 resting: PRE+POST
  each of 25+ consecutive steps; b2 resting i=248–300 same).
- `endContact` lags physical separation by up to one step (touching evaluated at next Collide).
- Speculative margin: `beginContact` can fire while shapes are still geometrically separated —
  b3's first BC at `y=519.9465` with the touch plane at 520.0 (~0.05px gap).
- New-contact delivery latency differs by path: slow contacts report at next-update Collide
  (pre-step state); fast penetrating contacts report mid-update at the TOI-advanced pose with
  the pre-impulse velocity — i.e., **a callback cannot assume `getPosition()` returns either
  the pre-step or post-step transform**. For the wave-11 sync lattice: sample positions in
  `postSolve`/after `world:update`, not in `beginContact`, if post-state is needed.

## (d) Fixed-dt accumulator drift — bounded sawtooth, bursty steps

Real headless `love.update` dt is uncapped (this host: 1.008–1.917 ms in trace window, ~1.05 mean
— consistent with r70's ~1.044 ms). Feeding real dt into `acc += dt; while acc ≥ 1/60: update(1/60)`:

- 1500 ticks: `wall_s=1.5777–1.5804`, `steps=94` (≈59.5 Hz effective), `sim_s=1.566667`,
  `n0=1406 n1=94 n2p=0 maxs=1` — steps fire singly every ~16 ticks (rem climbs ~1.05 ms/tick,
  wraps at ≥16.667 ms).
- **Drift == accumulator remainder**, 10.998–13.735 ms across runs, always `< FIXED` (16.667 ms).
  No cumulative drift — sim_time tracks wall_time within one fixed step.
- Scripted-jitter arm (30×1.1 ms, 50 ms stall, 30×1.1 ms, 33 ms stall, 30×8.3 ms): stall of
  50 ms → `stepped=3` in one tick; 33 ms → `stepped=2`; `ACC2SUM drift_ms=14.667 rem=14.667`
  still < FIXED. So a stall is repaid as a **burst of `world:update` calls in one tick**
  (spiral-of-death exposure is real under larger stalls — no cap measured, none implemented).

## Viability verdict for wave-11 dispatch

**Runnable headless today.** `love` 11.5 present at `/usr/bin/love`; physics module is standalone
and deterministic byte-for-byte; the callback lattice is synchronous-in-step with the
pre/post-state split above; `world:update` costs ~1.2 µs/step in this scene. The only conf line a
fixture needs is `t.modules.physics` (default on) plus the r70 headless profile.

## Commands (reproduce)

```sh
cd ~/Projects/shokunin/game-dev-2d-shokunin/corpus/live/frontier-lovephysics
love phys_strict          # -> STRICT | stepped y=9.592001 / pcall=true   (exit 0)
love phys_off             # -> OFF | love.physics=nil                     (exit 0)
love phys_probe > out/run-N.txt   # exit 0, ~1.6 s wall
# determinism check:
grep -a '^PHYS-\(DET\|EVT\|STEP\|COUNTS\|DETERM\)' out/run-*.txt | sort | uniq -c | head
for i in 1 2 3 4 5 6 7; do grep -a '^PHYS-\(DET\|EVT\|STEP\|COUNTS\|DETERM\)' out/run-$i.txt | sha256sum; done
```

## Observed facts vs inference vs gaps

- **Observed**: everything above is printed from runs on this host (paths under
  `corpus/live/frontier-lovephysics/out/`).
- **Inference (not directly proven)**: the mid-step BC/PRE state for fast contacts is consistent
  with Box2D 2.4's continuous-collision TOI pass (advance-to-touch → `contact->Update` → residual
  solve); LÖVE source wasn't opened — treat the *observed* dispatch states as the contract, not
  the mechanism name.
- **Gaps**: multi-body simultaneous-contact event ordering across pairs not enumerated;
  `contact:getPositions()`/`isTouching()` not sampled inside callbacks; sensor/bullet flags
  unexplored; determinism shown only same-host/same-build (no cross-host or FFI-off comparison);
  jitter under real engine stalls was synthesized (headless dt never exceeded ~1.9 ms here).
