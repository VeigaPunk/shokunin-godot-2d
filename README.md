# shokunin-godot-2d

2D game production, checked by executable headless fixtures on Godot
4.7.2: loop, input, physics, scenes, camera, UI, levels, juice, and
export readiness.

The lane id is `game-dev-2d`. Rank is shonen. There is no root `SKILL.md`.
The working expertise is `PROVINCE.md`, the fixture corpus, and the
round reports.

## The job

`PROVINCE.md` owns those production surfaces and names the sources: the
corpus fixtures (seeded from the games-engine-mechanics r15 suite, with
provenance in `corpus/knowledge/seed.md`), the read-only demand notes
under `~/Projects/gamez/research/`, and the Godot 4.7.2 headless runtime.

The lane refuses engine or editor source mutation, publishing and store
submission, asset-rights clearance, harness and evidence auditing as a
separate discipline, and narrative canon. Contested lore scope is
reported to the lore lane, not absorbed. Writes stay in this lane's
tree and its own reports.

`corpus/README.md` is the index of what each round actually proved, and
of what it deliberately left unprobed (rendered viewport, production UI,
app launch). Read that index before treating a green battery as a
finished game.

## Run the battery

`corpus/fixtures/run_battery.py` runs the read-only Godot fixtures
serially in an isolated scratch project. The corpus index describes the
contract: the runner copies seeds to an ignored scratch run before
execution.

```sh
python3 corpus/fixtures/run_battery.py
```

The script needs the Godot 4.7.2 headless binary named in the province.
Per-round lessons under `corpus/lessons/` record the decision boundaries
and the independent replays; the battery is the re-run, the lessons are
the interpretation.

## Read this first

1. [`PROVINCE.md`](PROVINCE.md) — the owned surfaces and the refusals.
2. [`corpus/README.md`](corpus/README.md) — round-by-round index, including what stayed unprobed.
3. [`corpus/knowledge/seed.md`](corpus/knowledge/seed.md) — where the fixtures came from.
4. [`SHONEN.md`](SHONEN.md) — the promotion checklist. Still present.

## On disk

| Path | Role |
|---|---|
| `PROVINCE.md` | Boundary. |
| `corpus/fixtures/` | Seeds plus `run_battery.py`. |
| `corpus/knowledge/`, `corpus/lessons/` | Provenance and per-round decision records. |
| `corpus/live/` | Preserved run evidence. |
| `reports/` | Verifier and adjudicator reports. |
| `SCORECARD.md`, `LOG.md` | Axis verdicts and the audit trail. |
| `SHONEN.md` | Promotion checklist. |

## Fleet

Protocol and roster: [shokunin](https://github.com/VeigaPunk/shokunin).
Roster id `game-dev-2d`, rank **shonen**.
The 3D sibling is [shokunin-3d-engines](https://github.com/VeigaPunk/shokunin-3d-engines).
