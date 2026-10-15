# r93-scout receipts — AnimationPlayer + Tween authorability lattice

Host **devin**; Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), `--headless`.
Lane `corpus/live/r93-scout/`; report `reports/round-93/r93-scout.md`.

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` (10 arms) | API/behaviour feasibility: census, interpolate_value grid, expo reverse-engineering, custom_step, MANUAL advance/seek, method tracks, track sampler, blend, process modes, frame clock | `runs/disc-*.{out,err,rc}` |
| 2 | `probes/discover2.gd` (7 arms) | loose ends: same-name replay, Tween.stop, node-free, blend step lattice, delay/from/relative, pingpong, infinite loops | `runs/disc2-*.{out,err,rc}` |
| 3 | `bash run_cells.sh` | **11 cells = 54 runs** (4 pure ×3, 7 runtime ×6) | `runs/r93_*.{out,err,rc}` |
| 4 | `bash run_loadtest.sh` (16 `yes` hogs) | 8 cells ×3 = **24 runs** at load avg 104–118 | `runs/loadtest/` |
| 5 | `python3 analyze_r93.py` | per-cell reps / out-uniq / err-uniq / rc vectors + varying-token census | `runs/analyze_r93.json` |
| 6 | `python3 make_author_rows.py` → `python3 verify_rows.py` | 15 gating + 2 informational rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) | `author-rows.py.txt` |
| 7 | `python3 audit_claims.py` | recomputes every headline numeric law from the raw receipts (r91 receipt, expo closed forms, crossfade weight law, running-source formula, stable clauses, byte-identity) — **AUDIT PASS, 0 mismatches** | stdout |

**Canonical cell set: 54 runs, 11 cells** — `census`/`tweenval`/`tweenval_grid`/`animtrack` ×3 (pure),
`tweenstep`/`tweenchain`/`tweenproc`/`animseek`/`animmethod`/`animblend`/`animproc` ×6 (runtime).
All rc=0; canonical stderr 0 B in every rep (54/54); no run left running.

**Byte-stability (canonical):** 9 of 11 cells `out_uniq=1` (full stdout byte-identical over reps):
census, tweenval, tweenval_grid, animtrack, tweenstep, tweenchain, animseek, animmethod, animblend.
Mode cells: `tweenproc` (out_uniq=5; `auto`/`paused` frame-coupled), `animproc`
(out_uniq=6; `idle`/`phys`/`quick`/`mixer_applied` frame-coupled) — both carry a trailing
`stable=[…]` boolean clause that is byte-identical in 9/9 canonical+loadtest reps.

**Loadtest:** all 8 cells rc=0, stderr 0 B; the six manual-clock cells
(tweenstep, tweenchain, animseek, animmethod, animblend, tweenval) are **byte-identical
under load avg 104–118**; only the two frame-coupled mode cells vary.

**Author rows:** `author-rows.py.txt`; `python3 verify_rows.py` → GATING set
**15 rows, 108 receipt checks, rejected=[]**; informational full-line mode rows reject 16/18
(the load-fragile counters), retained as the mode boundary demonstration.

**r91 receipt reproduction:** `Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, TRANS_EXPO, EASE_OUT)`
= `9.69718754291534` in 3/3 canonical and 3/3 loadtest reps — byte-identical to the r91 scout's
discovery receipt (`runs/disc-tweenval.out` of `corpus/live/r91-scout/`).
