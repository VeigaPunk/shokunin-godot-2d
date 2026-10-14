# R71 adjudicator (Sol) — pygame 2.6.1 headless first contact

Round: 71. Wave: `shokunin-train-20261101-w11`. Work commit `a993cbe`.

## Declared move (coverage/new-runtime)

Third 2D runtime: pygame 2.6.1 + SDL 2.32.72 headless. Claim under
test: "stdout withholding is a language-layer window bounded by buffer
size" — the frontier's ~8KB bound as the falsifiable constant.

## Claim adjudication

- Form CONFIRMED: withholding is a LANGUAGE-layer (CPython stdio)
  window, not SDL/pygame — identical edge with and without pygame init.
- Constant FALSIFIED: bound = `io.DEFAULT_BUFFER_SIZE` = **131072** on
  CPython 3.14.7 (GH-118144 raised it from 8192; ≤3.13 carries 8192).
  The frontier's ~8KB was a stale-artifact assumption.
- Boundary refined the exact semantics: compound two-layer window —
  textio pending (8192) + BufferedWriter (131072); exactly-full buffer
  does NOT flush; compound window = 139263 B fully invisible, the
  139264th byte surfaces the buffered 131072; granularity-conditional.
- Critic's load-fragility caught: pins re-derived to relations
  (bufsize−1/bufsize/bufsize+1), fragile wall-clock bounds widened,
  `PYTHONUNBUFFERED` pinned per-child.
- Simplifier's rev-1/rev-2 catch: the pin was right, the metric rule
  wrong; post-fix pin re-tightened to (60000,135000) so the case still
  witnesses the artifact class it was built for.

## Also measured

tick(60) → 62.1–62.3Hz (`int(1000/fps)` floor undershoot, SDL_Delay ms
granularity — 60Hz never deliverable); knife-edge fps=1000 sleeps 1ms /
fps=1001 spins; uncapped ~7MHz; popen writer-bound byte-exact (LOVE
shape); pump-free headless; event queue cap exactly 65535.

## Seat accounting

7/8 seats landed pre-integration: scout built a validated prototype
(83/83 ×3 incl. under load), author landed 36-case battery, baseline
independent second implementation (54/54 + LOVE/Godot byte-stability
replays), boundary compound-window lattice, critic constant+load
falsifications, simplifier pin/metric audit, scribe watching. Reviewer
not yet landed; verifier dispatched for committed tree.

## Verdict

**ADMIT-with-correction** — bound constant corrected (8192 →
io.DEFAULT_BUFFER_SIZE=131072, host-provenance row); window form and
language-layer attribution confirmed. Byte-stability: additive sibling,
love_battery/godot untouched.
