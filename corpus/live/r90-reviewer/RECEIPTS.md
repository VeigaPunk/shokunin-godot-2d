# r90-reviewer receipts — what each artefact is and how to reproduce it

Seat `REVIEWER` (g2d r90), host devin, Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
`/usr/bin/godot`, headless, 60 tps (unless a cell says otherwise), Python 3.14.7.
Reviewed commit `ee20575`. **No tracked file written, no commit.** Everything here is
seat-owned untracked scratch.

Launch shape (identical to the battery's, `run_battery.py` `execute()`):

```
timeout -s KILL 25 godot --headless --path <proj> --script res://rb_lattice.gd -- --arm=<arm> [--frames=N]
```

| dir | contents | how produced |
|---|---|---|
| `proj/` | committed `rb_lattice.gd` (sha `10da2291…`), `rb_watch.gd` (`e349faa0…`), `project.godot` (`8de8b3af…`), extracted with `git show ee20575:<path>` | — |
| `runs/` | 12 arms × 3 reps sequential (`<arm>.rep{1..3}.{out,err,rc}`) + `tpsA/tpsB` CLI-flag A/B | `N=3 ./run_arms.sh`; A/B: same arm with/without `--physics-ticks-per-second 30` before `--` |
| `runs_par/` | 12 arms × 1 rep, 8 launched concurrently (background `&` + `wait`) | `for a in …; do ( … ) & done; wait` |
| `runs_dummy/` | 3 arms under `proj_dummy` (`physics/2d/physics_engine="Dummy"`) | same launch shape, `--path proj_dummy` |
| `runs_tps30/` | 4 arms under `proj_tps30` (`physics/common/physics_ticks_per_second=30`) | same launch shape, `--path proj_tps30` |
| `verify_fresh.py` | extracts the committed `CASES` r90 rows + `classify_process` (AST, segment sha `749fa0607e7707e6…`) and classifies a receipt dir against the pins | `python3 verify_fresh.py [receipt_dir]` |
| `manifest.sha256` | covers every file in this tree except itself | `find . -type f ! -name manifest.sha256 \| sort \| xargs sha256sum > manifest.sha256` |

Key results: 48/48 fresh runs classify PASS; every PASS line byte-equal to its pin
(whole line); Dummy and 30-tps cells all reject; `tpsA`/`tpsB` byte-identical (the
`--physics-ticks-per-second` flag is a no-op on this build — see report F2).
