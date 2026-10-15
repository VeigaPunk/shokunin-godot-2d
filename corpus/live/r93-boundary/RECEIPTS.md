# r93-boundary receipts — batch table, replay commands, per-cell stability

Seat `BOUNDARY` (LEAF), lane `r93-boundary`, round 93, host **devin**.
Runtime `/usr/bin/godot` = `4.7.2.stable.arch_linux.ed1daf0bf`, `--headless`, 60 tps default,
GodotPhysics2D. Every run is `timeout -s KILL 25`-bounded; stdout/stderr split into
per-cell `.out`/`.err` sidecars plus `.rc` and `.wall`.

Probes: `probes/scout_anim_lattice.gd` (byte-copy of the r93 scout's frozen probe, sha256
`6a919ae04d4e7549…`, 11 arms) and `probes/r93b_anim.gd` (this seat, 6 arms: clock,
manual_inv, frame, deferred, purity, blend). Both are copied into `proj/` before launching
(the scout's own driver does the same; a missing copy is receipted in `runs/defect/`).

Replay:

```bash
cd corpus/live/r93-boundary
cp -f probes/scout_anim_lattice.gd proj/ && cp -f probes/r93b_anim.gd proj/
bash run_matrix.sh all        # 7 batches, 258 runs (both probes, all cells)
bash run_matrix.sh p          # extended-purity re-run, 16 runs (overwrites *_purity receipts)
python3 analyze_r93b.py       # -> runs/analyze_r93b.json + runs/analysis.txt
```

## Batch table

| batch | tag | conditions | runs | loadavg start→end |
|---|---|---|---|---|
| `q` | `q_` | no seat hogs (ambient only) | 51 | 57.33 → 56.41 |
| `l` | `l_` | **16 seat hogs** | 51 | 57.74 → 74.56 |
| `f30` | `f30_` | `--fixed-fps 30` | 34 | 74.56 → 72.45 |
| `f60` | `f60_` | `--fixed-fps 60` | 34 | 72.45 → 70.03 |
| `f120` | `f120_` | `--fixed-fps 120` | 34 | 70.03 → 69.34 |
| `f120l` | `f120l_` | `--fixed-fps 120` + 16 seat hogs | 34 | 69.34 → 75.30 |
| `l32` | `l32_` | **32 seat hogs** (32 cores), mode+attack subset | 20 | 75.30 → 80.82 |
| `p` | `q_/l_/f30_/f60_/f120_/f120l_/l32_ purity` | extended purity arm, all conditions | 16 | 147.47 → 149.02 |

**258 canonical runs, all rc=0, all stderr 0 B, 0 timeouts (0× rc=137), wall max 2.26 s.**
(The scout-cell half of the first `all` pass was voided by a harness defect — see below —
and re-run in a second pass; the receipt files were overwritten in place, so the 258 files
on disk are all valid.)

Per-cell reps: 3 per batch for `q`/`l`; 2 per batch for `f30`/`f60`/`f120`/`f120l`;
2 for `l32` (tweenstep/tweenproc/animseek/animproc + the 6 attack arms).

## Harness defect (recorded, not hidden)

The first `all` pass launched the scout cells without `probes/scout_anim_lattice.gd` copied
into `proj/`: **162 runs were vacuous** (rc=1, no `PASS` line, 3 `ERROR:` lines on stderr).
Evidence preserved in `runs/defect/noscript.{out,err,rc}` (deliberate single reproduction):

```
rc=1
ERROR: Attempt to open script 'res://scout_anim_lattice.gd' resulted in error 'File not found'.
   at: load_source_code (modules/gdscript/gdscript.cpp:1139)
ERROR: Failed loading resource: res://scout_anim_lattice.gd.
ERROR: Can't load script: res://scout_anim_lattice.gd
stdout: 101 B (engine banner only), PASS lines: 0
```

The battery convention (a `PASS <probe> <arm>` line) rejects this class loudly; a runner
that only checks "rc ≠ 137 / not a timeout" would misread it as a clean crash. A second
harness defect (editing `run_matrix.sh` while it was executing → bash re-read the file at a
shifted offset → `syntax error near unexpected token '}'`, exit 2) is recorded in
`runs/matrix-scout.log`; no receipt was affected (all batches had finished).

## Per-cell stability (from `runs/analyze_r93b.json`)

| cell | reps | payload_uniq per batch | verdict |
|---|---|---|---|
| census, tweenval, tweenval_grid, animtrack, animmethod, tweenchain, animblend | 14 | **1** in every batch | launch-invariant; byte-identical to the scout's canonical **and** loadtest receipts |
| tweenstep, animseek | 16 (incl. `l32`) | **1** in every batch | launch-invariant incl. 32 hogs; byte-identical to the scout's canonical + loadtest receipts |
| purity (seat) | 16 | **1** in every batch | launch-invariant (incl. the overshoot lanes) |
| tweenproc | 16 | q 3, l 3, l32 2, **ff 1 each** | mode cell; `stable` + `phys_manual` clauses constant 16/16 |
| animproc | 16 | q 3, l 3, l32 2, **ff 1 each** | mode cell; `stable` clause constant 16/16 |
| frame (seat) | 16 | q 3, l 3, l32 2, **ff 1 each** | mode cell; `phys` + `mixer_applied_10` constant 16/16 |
| manual_inv (seat) | 16 | q 3, l 3, l32 2, **ff 1 each** | manual tokens constant; only the unpaused control + `proc_delta` vary |
| blend (seat) | 16 | q 3, l 3, l32 2, **ff 1 each** | weight-law tokens constant; only the sampled `proc_delta` varies |
| deferred (seat) | 16 | q 3, l 3, l32 2, **ff 1 each** | flush-lattice constant; only `idle_lag` + `proc_delta` vary |
| clock (seat) | 16 | 16 | launch fingerprint by design |

`err` bytes: 0 for all 258 canonical runs. `rc`: 0 for all 258.

## Batch log / analysis artefacts

- `runs/rc-summary.txt` — every batch's loadavg start/end and hog census (all batches end
  `my_hogs_after_stop=0`; other lanes' hogs were never touched).
- `runs/matrix.log`, `runs/matrix-scout.log`, `runs/matrix-p.log` — full batch logs
  (including the stray-godot census of concurrent lanes).
- `runs/analyze_r93b.json`, `runs/analysis.txt` — machine + human summary
  (per-batch uniq, cross-batch payload sets, `matches_scout_ref` flags, varying-key census).
- `analyze_r93b.py` — analyzer (read-only over `../r93-scout/runs/`).
- `manifest.sha256` — every artefact under this lane.
