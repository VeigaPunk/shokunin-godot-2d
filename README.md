# game-dev-2d-shokunin

Repo: `shokunin-godot-2d`.

**2D game production verified by executable headless fixtures** — loop,
input, physics, scenes, camera, UI, levels, juice, export readiness —
on Godot 4.7.2.

A **shokunin lane**: an expert agent for one domain, minted and trained
under the [shokunin skill](https://github.com/VeigaPunk/shokunin).
Rank: **shonen**. Promotion is a named non-author review of
[`SHONEN.md`](SHONEN.md), never self-attestation.

This lane answers: *does this 2D mechanic hold under Godot headless,
with a discriminating negative control — without pretending the
rendered frame was observed?*

## Domain

From [`PROVINCE.md`](PROVINCE.md): 2D production surfaces listed above,
on the Godot 4.7.2 headless runtime. Domain source trees are read-only.
This lane writes its own corpus and reports.

**Refuses:** engine/editor source mutation; publishing or store
submission; asset rights clearance; harness/evidence auditing as a
product (that's
[tameshi](https://github.com/VeigaPunk/tameshi-shokunin)'s method, and
this lane's own gates stay this lane's); narrative canon (→
[lore](https://github.com/VeigaPunk/shokunin-world-bible) — contested
scope is reported, not absorbed).

Headless PASS is not a screenshot, not a player, not a store build.
Rendered viewport / production UI remain explicitly unprobed until a
round holds them.

## What's here

| Path | Role |
|---|---|
| [`PROVINCE.md`](PROVINCE.md) | owned surfaces and refusals |
| [`corpus/README.md`](corpus/README.md) | coverage map: which mechanic is held, which is still unprobed |
| [`corpus/fixtures/`](corpus/fixtures/) | read-only Godot 4.7.2 seeds + `run_battery.py` |
| [`corpus/lessons/`](corpus/lessons/) | per-round decision boundaries and independent replays |
| [`corpus/live/`](corpus/live/) | disposable scratch and later-round batteries |
| [`reports/`](reports/) | verifier / adjudicator reports |
| [`SCORECARD.md`](SCORECARD.md) · [`LOG.md`](LOG.md) · [`SHONEN.md`](SHONEN.md) | axes, trail, promotion |

(`SKILL.md` is still in shonen seed form — see `corpus/`.)

## The battery

```sh
python3 corpus/fixtures/run_battery.py
```

`run_battery.py` copies the seeds to an ignored scratch project before
execution. The original fixtures stay read-only. Expected exit
signatures and PASS lines are declared in the runner; a case that
cannot discriminate a negative control is not a test.

Requires Godot 4.7.2 headless on PATH as used by the runner. Live
scratch under `corpus/live/runs/` is ignored and disposable.

## How a lane learns

Append-only corpus; every claim separates observation / inference /
unknown; rounds are non-author-verified. See the fleet
[README](https://github.com/VeigaPunk/shokunin#readme).
