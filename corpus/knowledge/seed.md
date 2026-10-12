# game-dev-2d seed knowledge

Inherited from the games-engine-mechanics research direction (15 verified
rounds, 2026-10-11/12). Upstream reference corpus:
https://github.com/VeigaPunk/prymeagnt-games-engine-mechanics (branch main,
corpus/ + round reports). Local copy: corpus/fixtures/ (29 files, from
research/games-engine-mechanics r15-toggle, commit c32adb1).

## Standing fixture discipline (proven across r1–r15)
- Godot 4.7.2 headless only; every run bounded: `timeout --signal=TERM --kill-after=2s 8s`.
- Negative controls use `quit(1)`, NEVER `assert(false)` (an early assert hung).
- Every negative must be discriminating: a mutant that should fail must fail
  with a targeted diagnostic, and a broken baseline must not false-PASS (r14).
- Serial execution only after r13/r15 exposed parallel-launch frame
  flakiness; PASS evidence is serial-only.
- Report-last commit ordering; canonical git identity on every commit
  (violation = round not admitted, per games r11).
- Failed rounds stay in the ledger as negative results (r6/r7/r9).

## Verified capability ladder (extends upward from here)
script runtime (r1) → scene+signal (r2) → Input.parse_input_event dispatch
(r3) → Area2D physics overlap (r4) → scene transitions (r5) → causal chain
input→intent→movement→overlap→transition (r10) → wrong-key filter (r11b) →
key release semantics (r12) → unrelated-key-up (r13) → receiver repair (r14) →
process-mode toggle (r15).

## Production axes not yet covered (candidate round claims)
camera follow, tilemap levels, UI/HUD, animation state, audio hooks,
save/load, export template check, autotest bundling.
