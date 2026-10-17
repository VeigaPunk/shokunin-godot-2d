# shokunin-godot-2d

2D game production, verified by executable headless fixtures on Godot
4.7.2.

Lane id: **game-dev-2d-shokunin**. Rank: **shonen**. [`SHONEN.md`](SHONEN.md)
boxes are open; each one waits on a named non-author verifier. There is
no root `SKILL.md`. Lessons under `corpus/lessons/` are the craft record.

Fleet: [shokunin](https://github.com/VeigaPunk/shokunin).

## The question

> Does this 2D mechanic hold in a headless Godot fixture — loop, input,
> physics, scene, camera, UI, level, juice, export — and does the
> negative control fail the way the case declares?

`corpus/README.md` is the round index. It lists inherited fixtures plus
later lessons (camera, UI, level collision, animation, export, fault
classification, runtime contact, and the rounds after those). Several
lessons say rendered viewport behavior is still unprobed. Headless pass
is the claim those rounds made. A picture on a monitor is a different
claim.

## Boundary

**Owns:** those 2D production surfaces, checked by fixtures in this
repository. Sources named in `PROVINCE.md`: the seeded corpus, the
read-only demand notes under `~/Projects/gamez/research/`, and the Godot
4.7.2 headless runtime.

**Hands off:** engine and editor source mutation, publishing and store
submission, asset-rights clearance, harness auditing, and narrative canon
(lore — contested scope is reported). Domain source trees are read-only.
3D production is
[shokunin-3d-engines](https://github.com/VeigaPunk/shokunin-3d-engines).

## Run

`corpus/fixtures/run_battery.py` runs the read-only Godot fixtures
serially in an isolated scratch project. Default `--godot` is the
`godot` on `PATH`. Scratch goes under `corpus/live/runs/` unless `--runs`
says otherwise.

```sh
python3 corpus/fixtures/run_battery.py
```

Probe flags are opt-in and named in the argparse block: `--probe-failing`,
`--fault-injection`, `--probe-export-launch`, `--probe-godot-error`,
`--probe-stream-attribution`, and others. A bare run is the seeded
battery. It is not every probe the file can launch.

Case expectations are the tuples at the top of `run_battery.py` (`PASS`
markers and expected exit codes). `corpus/README.md` records which round
an independent verifier replayed, and which surfaces that replay left
unprobed.

## Map

| Path | What it is |
|---|---|
| [`PROVINCE.md`](PROVINCE.md) | owned 2D surfaces |
| [`corpus/README.md`](corpus/README.md) | fixture and lesson index |
| [`corpus/fixtures/`](corpus/fixtures/) | seeds and `run_battery.py` |
| [`corpus/lessons/`](corpus/lessons/) | per-round decision notes and verifier JSON |
| [`corpus/knowledge/`](corpus/knowledge/) | seed provenance and the production checklist |
| [`reports/`](reports/) | round reports |
| [`SHONEN.md`](SHONEN.md), [`SCORECARD.md`](SCORECARD.md), [`LOG.md`](LOG.md) | probation, verdicts, audit trail |

Export artifacts from a probe are scratch. The lessons that deleted them
say so. A passing export is not a shipped build.
