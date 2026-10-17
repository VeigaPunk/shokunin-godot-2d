# shokunin-godot-2d — game-dev-2d

The question this lane answers is whether a 2D production surface holds under an executable headless fixture: loop, input, physics, scenes, camera, UI, levels, juice, and export readiness, on Godot 4.7.2 (`PROVINCE.md`).

**Rank:** `SHONEN.md` is titled probation. Every box is `[ ]`, and the file says a box may be checked only by a named non-author verifier. That is not a promotion.

## Owns / refuses

Owns that 2D fixture craft. Sources named in `PROVINCE.md`: the corpus fixtures (seeded from games-engine-mechanics r15, provenance in `corpus/knowledge/seed.md`), `~/Projects/gamez/research/` as read-only demand context, and the Godot 4.7.2 headless runtime.

Refuses engine or editor source mutation, publishing or store submission, asset-rights clearance, harness and evidence auditing, and narrative canon. Domain source trees are read-only. The write scope named in `PROVINCE.md` is `.shokunin/game-dev-2d/**` and this lane's reports.

There is no root `SKILL.md`. The decision table for the first battery is `corpus/lessons/r1-headless-verification.md`, indexed from `corpus/README.md`.

## Start here

`corpus/fixtures/run_battery.py` runs the read-only Godot fixtures serially in an isolated scratch project. It needs Godot. This page does not require a full battery run.

```sh
python3 corpus/fixtures/run_battery.py --help
```

The module docstring is the contract: seeds are not edited in place. Opt-in probes (`--probe-godot-error`, `--probe-stream-attribution`, `--probe-crash-exit`, `--probe-timeout`) are separate from the default battery (`corpus/fixtures/run_battery.py`).

## How to read the corpus

`corpus/README.md` is the round index: fixtures, then one bullet per lesson from r1 onward, including what each round left unprobed. It was not reflowed. `corpus/knowledge/seed.md` is provenance. `corpus/knowledge/2026-10-12-production-checklist.md` lists production surfaces still unprobed. `corpus/lessons/` holds the decision notes and verifier JSON. `corpus/live/` holds run receipts; `corpus/README.md` calls live scratch ignored and disposable.

## Map

| Path | What it is |
|---|---|
| `PROVINCE.md` | 2D boundary |
| `SHONEN.md` | Probation checklist, boxes unchecked |
| `LOG.md` | Append-only record |
| `SCORECARD.md` | Axis verdicts |
| `corpus/README.md` | Lesson index |
| `corpus/fixtures/run_battery.py` | Godot battery |
| `corpus/knowledge/` | Seed and production checklist |
| `corpus/lessons/` | Per-round notes |
| `reports/` | Verifier reports |

## Neighbors

lore owns narrative canon; contested scope is reported, not absorbed (`PROVINCE.md`). game-dev-3d owns 3D product surfaces. Audio, art rights, and harness auditing are outside this province.

Fleet protocol: [VeigaPunk/shokunin](https://github.com/VeigaPunk/shokunin).
