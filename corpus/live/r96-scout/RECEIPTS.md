# r96-scout receipts — PackedScene / ResourceSaver / ResourceLoader round-trip lattice

Seat `g2d-r96-scout` (LEAF) | lane `corpus/live/r96-scout/` | round 96 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`, 60 tps.
No git mutation, no tracked file written, no commit.

## Launch shape

```
godot --headless --path proj --script res://scene_io_lattice.gd -- --arm=<arm>
godot --headless --path proj --script res://discover[2..8].gd -- --arm=<arm>
```

`proj/project.godot` is the byte-copy of `corpus/fixtures/project.godot`
(`8de8b3af…`); every artefact the probe writes lives under `user://r96/` and is
removed again by the probe's `_wipe()` (the battery's own scratch project gets a
unique `config/name` per run, so `user://` is isolated there too).

## Counts

| block | runs | receipts |
|---|---|---|
| canonical cells (1×3 + 12×6) | **75** | `runs/r96_<cell>.rep<N>.{out,err,rc}` |
| loadtest cells (13×3, load avg 94–148, 16 own hogs) | **39** | `runs/loadtest/<cell>.rep<N>.{out,err,rc}` |
| discovery probes (disc … disc9) | **41 files** | `runs/disc*/…` |
| battery-shaped smoke (scratch project, 8 s bound, production classifier) | **13** | `runs/smoke/<stamp>/` |
| **launches with retained receipts** | **155** + 13 smoke | all `rc=0`, no run left running |

Roughly **590 further launches** during probe development (superseded canonical/loadtest
passes and discovery iterations, receipts overwritten) are not counted.

## Commands

```bash
cd corpus/live/r96-scout
bash run_cells.sh          # 75 canonical runs
bash run_loadtest.sh       # 39 runs under 16 own hogs (own PIDs only are killed)
python3 analyze_r96.py     # → runs/analyze_r96.json + per-cell stability table
python3 make_author_rows.py # → author-rows.py.txt (13 rows, full + census-prefix)
python3 verify_rows.py     # production classify_process over all 114 receipts
python3 smoke_battery.py   # scratch project + battery timeout + classifier, 13/13
```

## Verification results (verbatim)

```
[ROWS(full-line)] rows=13 receipts_checked=114 rejected=[]
[ROWS_PREFIX(census-prefix)] rows=13 receipts_checked=114 rejected=[]
classify_process segment sha256=749fa0607e7707e6
full_line_rejections=0  prefix_rejections=0
```

```
smoke: 13/13 rows classified PASS
classify_process segment sha256=749fa0607e7707e6
```

Stability (`runs/analyze_r96.json`): **UNSTABLE=[]**, **CRASH_CELLS=[]** — every cell
is `out_uniq=1 err_uniq=1 pass_uniq=1 rc=[0]` over its canonical reps **and**
byte-identical on all three loadtest reps.

One scout-authored key was **load-bimodal and was removed before the rows were frozen**:
`ResourceUID.id_to_text(create_id()).length()` returned 17 in one loadtest rep (18/19 in
the other eight), so the cell now pins `create_id_text_prefix=true` instead. The
loadtest receipts of that superseded probe version are not part of the frozen set.

## ERROR allowlists (exact, measured)

`ownership` (2) and `refuse` (13) are the only cells that print engine `ERROR:` lines;
both sets are byte-stable across all 9 receipts each. The `author-rows.py.txt`
`EXPECTED_ERRORS` dict carries them verbatim.

## Artifact hashes (sha256, first 16)

| artefact | path | sha256 |
|---|---|---|
| frozen probe, 13 cells | `probes/scene_io_lattice.gd` | `2eded40b74971c4f` |
| discovery probes | `probes/discover[2..9].gd` | see `manifest.sha256` |
| canonical driver | `run_cells.sh` | `28e3098616a716d8` |
| loadtest driver | `run_loadtest.sh` | `e171090bc90e7b44` |
| analyzer | `analyze_r96.py` | `ec33169028854a96` |
| row builder / verifier | `make_author_rows.py` / `verify_rows.py` | `b41be47cdb6cf4d7` / `5cd44b05fc207a33` |
| battery-shaped smoke | `smoke_battery.py` | `b608046be882438e` |
| author rows | `author-rows.py.txt` | `84e5f7b3ad8294c1` |
| launch project | `proj/project.godot` | `8de8b3af9cc737ed` |

`manifest.sha256` covers all 649 artefacts under this directory (every receipt included).

## Delegated probe

The frozen `probeParent` dispatched exactly one read-only `ufo-labrat` seat
(independent falsification of the pinned-bundle determinism recipe). **It could not
execute**: that seat's tool surface has no shell/exec and no write capability, so it
ran **0** godot launches and reported honestly instead of fabricating shas. No
empirical delta; the falsification ladder was run by this seat instead.
