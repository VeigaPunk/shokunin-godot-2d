# r69-scout evidence scratch (read-only mapping; no fixture runs)

Repo: ~/Projects/shokunin/game-dev-2d-shokunin @ HEAD aa94cb7 (author in flight:
`git status --porcelain` shows `M corpus/fixtures/descendant_pipe_probe.gd`,
`M corpus/fixtures/run_battery.py`, `?? corpus/live/r69-author/`).

Commands run (all read-only):

- `find . -iname "*descendant*"` → canonical fixture
  `corpus/fixtures/descendant_pipe_probe.gd` (182 lines).
- `git show HEAD{,~1,~3,~5}:corpus/fixtures/descendant_pipe_probe.gd | grep -n
  delay_msec\|gap_ms=` → HEAD anchors: banner `gap_ms=200` :136, offset parse
  :165-168, `OS.delay_msec(200)` :180; HEAD~5 banner sat at :129 (brief's stale ref).
- r68 instrumented spike `corpus/live/r68-author/spike/spike-results.json`:
  write_rel_head = offset+2..3ms (off 0/40/80/120/160 → 2-3/42-43/82-83/122-123/162);
  gap 200-201ms; jitter ≤1ms.
- r68 ladder artifact `corpus/live/r68-author/runs/20261014T112303089118Z/
  midlineforge-ladder-verdicts.json`: 6 offsets × 3 reps, {0..160} fabricated,
  240 missed; ALL 18 reps write_ppid==godot_pid (incl. offset=240 → child exit
  latency post-tail >42ms); elapsed 0.717-0.804s.
- `grep -n` on `corpus/fixtures/run_battery.py` (3067 lines):
  `def dual_classify` :2515, return dict :2522-2532 (per-channel digests
  :2529-2532); callers :2564 (record.update), :2573-2578 (pair),
  :2595-2614 (reclass); divergence_table :2617-2627;
  `dual_records_same_input_digests` :2775-2799; ladder block :2043-2181;
  surface_run :1588-1661 (merged `sf_out+sf_err` :1612); pid_alive :633.
- CASES count: `re.findall(r'^\s*\("', CASES)` = 81; unconditional meta rows
  at :515,:549,:688,:871,:1101,:1530,:2031 → 88 flagless.
- `sf_discriminations` key census = 34 (matches "surface 34/34").
- Fixture shas at HEAD: probe `5c5c629ac187b11832c825c3f510baeab98e81517e01b65491426840f4a39d1f`,
  battery `55314bb55b409e59830fc23ea21c49d25006be6de114e31438a83c3d548ba5e6`.
- r66 concat-order caveat: `reports/round-66/r66-author.md:215-216`.

Observed (not reviewed) author working-tree diff: fixture gains
`--midline-gap-ms=N` (default 200; parse + banner + `OS.delay_msec(midline_gap_ms)`);
battery gains `--probe-midlineforge-gapladder` with `gapladder_gaps=(50,100,200,400,800)`,
`gapladder_offset_ms=80`, reps=3, per-cell `gap_ms`/`offset_ms`/`write_pre_death`.
