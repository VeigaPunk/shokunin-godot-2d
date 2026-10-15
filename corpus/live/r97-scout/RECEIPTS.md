# r97-scout receipts — SceneTree groups / signal connect flags / call_deferred ladder

Host: `godot 4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), `--headless`, 60 tps
(`Engine.physics_ticks_per_second=60`), `SceneTree` root class `Window`. Every launch is
`timeout -s KILL`-bounded (30 s; none hit); no run was left running.

## Probe revisions (all under `probes/`)

| file | role |
|---|---|
| `probes/discover.gd` | discovery micro-probe (28 arms: group order/forms/flags/lifecycle/reorder/dup/setters, signal forms/flags/await, deferred ladder/nest/slots/order, scene file/packed/missing/node) — receipts under `runs/disc/` and the one-off scratch runs listed in the report |
| `probes/stree_lattice.gd` | **frozen primary probe** (11 arms; `group_order` also runs as a `--rev` variant = 12 cells) — canonical receipts under `runs/r97_*.{out,err,rc}` |

`probes/stree_lattice.gd` sha256 `4dd18e10e84f0da2…` (recorded verbatim in
`runs/probe.sha256`) — the revision used for **all 48 canonical + 36 loadtest receipts**.
The discovery probe is **not** battery-authorable as-is (it prints diagnostic keys, no
`PASS` line) and is kept only as provenance.

## Canonical cells (48 runs, all rc=0, all stderr 0 B)

| cell | arm | flags | reps | receipts |
|---|---|---|---|---|
| census | census | — | 3 | `runs/r97_census.rep{1..3}.*` |
| group_order | group_order | — | 3 | `runs/r97_group_order.rep{1..3}.*` |
| group_order_rev | group_order | `--rev` | 3 | `runs/r97_group_order_rev.rep{1..3}.*` |
| group_flags | group_flags | — | 3 | `runs/r97_group_flags.rep{1..3}.*` |
| group_lifecycle | group_lifecycle | — | 3 | `runs/r97_group_lifecycle.rep{1..3}.*` |
| group_setters | group_setters | — | 3 | `runs/r97_group_setters.rep{1..3}.*` |
| signal_order | signal_order | — | 3 | `runs/r97_signal_order.rep{1..3}.*` |
| signal_flags | signal_flags | — | 3 | `runs/r97_signal_flags.rep{1..3}.*` |
| defer_ladder | defer_ladder | — | 6 | `runs/r97_defer_ladder.rep{1..6}.*` |
| defer_slots | defer_slots | — | 6 | `runs/r97_defer_slots.rep{1..6}.*` |
| defer_order | defer_order | — | 6 | `runs/r97_defer_order.rep{1..6}.*` |
| scene_probe | scene_probe | — | 6 | `runs/r97_scene_probe.rep{1..6}.*` |

`runs/rc-summary.txt` records the driver's rc vectors + host line.
`runs/analyze_r97.json` is the per-cell stability report — **`UNSTABLE=[]`,
`CRASH_CELLS=[]`**, every cell `out_uniq=1 err_uniq=1 pass_uniq=1 rc=[0]` with 0 B stderr.

## Loadtest receipts (36 runs, load avg 110–138)

`runs/loadtest/<cell>.rep{1,2,3}.{out,err,rc}` + `runs/loadtest/hogs.txt` (per-cell load
avg, own hog PIDs, kill counts). Host baseline was already ~113 (other lanes); 10 own
`yes` hogs raised it to ~118–138. Only this seat's own hog PIDs were killed
(`own_hogs_killed=10`, `host_yes_remaining=80`). All 36 rc=0, stderr 0 B, and **all 12
cells byte-identical to their canonical rep1** (`grep -h '^PASS' | sort -u` = 1 per cell).

## Row verification

- `author-rows.py.txt` — 12 rows: `ROWS` (full-line) and `ROWS_PREFIX` (**recommended**;
  cut before the multi-element order vectors for the 4 vector-bearing cells) +
  `EXPECTED_ERRORS = {}`.
- `verify_rows.py` — extracts `classify_process` from `corpus/fixtures/run_battery.py` by
  AST (segment sha256 `749fa060…`, the same segment r89–r95 pinned) and classifies every
  row against every canonical **and** loadtest receipt (stdout+stderr merged as
  `run_process` does): **`ROWS` 84/84 accepted, `ROWS_PREFIX` 84/84 accepted,
  `rejected=[]`.**
- Discriminating-power checks (run in-session, receipts under `runs/`): every row's
  signature is a byte-exact line of its receipt (12/12); flipping the
  `cap_d_membership` token is rejected on 6/6 receipts; the `--rev` negative control does
  not cross-accept (0/6 both directions); dropping any single row leaves the other 11
  clean. Known harness-wide property (r79 C3, unchanged): `classify_process` matches by
  substring, so a *shortened* signature that is still a prefix-substring of the real line
  is accepted — the pinned rows are the full lines, and the discriminating checks above
  are the evidence that matters.

## Reproduce

```
bash run_cells.sh && bash run_loadtest.sh && python3 analyze_r97.py && \
  python3 make_author_rows.py && python3 verify_rows.py
```

## Scratch (discovery-only, not receipts)

`proj/` is the launch project (byte-copy of `corpus/fixtures/project.godot`,
`8de8b3af…`) plus the probe, `scene_marker.gd`, `scene_a.tscn`, `scene_b.tscn`. The
one-off falsification scripts used during discovery (`/tmp/uniq_probe.gd`,
`/tmp/uniq2.gd`, `/tmp/uniq3.gd`, `/tmp/uniq4.gd`, `/tmp/cap.gd`, `/tmp/cap2.gd`,
`/tmp/cap3.gd`) were scratch and were deleted from `proj/` after use; their findings are
recorded in the report §4.
