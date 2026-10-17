# shokunin-godot-2d

2D game production, verified by executable headless fixtures on Godot.

Loop, input, physics, scenes, camera, UI, levels, juice, export
readiness — each as a fixture that runs without a window and says exactly
what it observed. Rendered output, production-project launch, and other
platforms stay unprobed until a round measures them. The corpus says so
in the lesson that would have had to prove them.

Rank: **shonen**. `SHONEN.md` is still here. Registered in the fleet
`MANIFEST.json` as game-dev-2d-shokunin since 2026-10-11. There is no
`SKILL.md` in this checkout.

## Province

**Owns.** Those 2D surfaces, verified by the fixture battery. Sources are
read-only: the corpus fixtures (seeded from games-engine-mechanics r15,
provenance in `corpus/knowledge/seed.md`), `~/Projects/gamez/research/` as
demand context, and the Godot 4.7.2 headless runtime named by the
province.

**Hands off.** Engine and editor source. Publishing and store submission.
Asset-rights clearance. Harness auditing as an end in itself. Narrative
canon (lore). Contested scope is reported, not absorbed.

Writes stay on this lane's tree and its own reports.

## Start here

1. `PROVINCE.md` — the boundary, twelve lines.
2. `corpus/README.md` — the lesson index. Early rows name what is still
   unprobed (rendered viewport, production UI, runtime contact beyond the
   fixture).
3. `corpus/fixtures/run_battery.py` — the runner. It copies seeds into an
   ignored scratch run.
4. `corpus/lessons/` — one pair of notes per round: the claim, and the
   non-author replay.
5. `SCORECARD.md` — scores stay unassigned. Read the latest round's
   verdict table and the report it cites. The planned-line at the top of
   the card is a queue, not an admission.

## Run the battery

From the repository root, with the Godot binary the province names:

```sh
python3 corpus/fixtures/run_battery.py --godot godot
```

The runner's `--probe-*` flags opt into extra classifications (failing
mutants, export launch, stream attribution, crash exit, timeout, and
others). The argparse help is the list. A green battery is the seeded
cases on this host's Godot. It is not a production export certificate.
`corpus/README.md` records the early rounds' independent replay counts;
later counts live in `reports/` and `corpus/lessons/`.

## The tree

| Path | What it is |
|---|---|
| `corpus/fixtures/` | Godot 4 scenes, scripts, and `run_battery.py` |
| `corpus/knowledge/` | Seed provenance and the production checklist of unprobed surfaces |
| `corpus/lessons/` | Per-round claims and verifier receipts |
| `corpus/live/` | Preserved runs, including frozen baselines |
| `reports/` | Adjudicator and verifier reports |

## Fleet

Minted under [shokunin](https://github.com/VeigaPunk/shokunin).
The 3D sibling is
[shokunin-3d-engines](https://github.com/VeigaPunk/shokunin-3d-engines).
Shared fixture patterns may be inherited. 2D product surfaces are not
its province, and 3D product surfaces are not this one.
