# shokunin-godot-2d — game-dev-2d-shokunin

**2D game production, verified by executable headless fixtures** —
loop, input, physics, scenes, camera, UI, levels, juice, export
readiness — on Godot 4.7.2.

This is a [shokunin](https://github.com/VeigaPunk/shokunin) lane. Rank:
shonen. Canonical lane name: `game-dev-2d-shokunin`. The runtime is
Godot 4.7.2 headless. Corpus fixtures were seeded from
games-engine-mechanics r15; provenance is in `corpus/knowledge/seed.md`.

A passing fixture proves the named mechanic in an isolated scratch
project. It does not prove a shipping title, a store page, or a canon
decision.

## Province

**Owns:** 2D game production verified by executable headless fixtures
on the surfaces above.

**Refuses:** engine / editor source mutation; publishing or store
submission; asset rights clearance; harness / evidence auditing;
narrative canon (→ lore — contested scope is reported, not absorbed).

Only writes this repository and its own reports. Domain source trees
(`~/Projects/gamez/research/` and others named in `PROVINCE.md`) are
read-only. 3D production is
[game-dev-3d](https://github.com/VeigaPunk/shokunin-3d-engines);
shared fixture patterns may be inherited, 3D product surfaces are not.
Full boundary: [`PROVINCE.md`](PROVINCE.md).

## Start here

1. [`PROVINCE.md`](PROVINCE.md) — owned surfaces and refusals.
2. [`corpus/fixtures/run_battery.py`](corpus/fixtures/run_battery.py) — serial headless runner.
3. [`SHONEN.md`](SHONEN.md) — promotion checklist.
4. [`corpus/README.md`](corpus/README.md) — coverage map, when present.

This lane is still in shonen seed form: distilled `SKILL.md` lives in
the corpus until promotion.

## The battery

```
python3 corpus/fixtures/run_battery.py
```

The runner copies fixtures into an isolated scratch project and
executes them serially under Godot headless. Cases are declared in
`CASES` inside the runner (mechanic, scene signal, camera, UI, …).
Sibling probes (`love_battery.py`, `pygame_battery.py`,
`pygame_probe.py`) are additional runtimes, not a claim that Godot is
absent.

A `PASS` line is the named assertion on that case. It is not export
readiness for a store and it is not juice as a subjective aesthetic.

## What's in the repo

```
shokunin-godot-2d/
├── PROVINCE.md       domain boundary
├── SHONEN.md         promotion checklist
├── LOG.md            append-only audit trail
├── SCORECARD.md      axis verdicts
├── reports/          verifier / adjudicator reports
└── corpus/
    ├── fixtures/     run_battery.py + .gd / .tscn cases
    ├── knowledge/    including seed.md
    └── lessons/
```

Protocol: append-only corpus; every claim separates observation /
inference / unknown; rounds are non-author-verified. See the fleet
[README](https://github.com/VeigaPunk/shokunin#readme) for how a lane
learns.
