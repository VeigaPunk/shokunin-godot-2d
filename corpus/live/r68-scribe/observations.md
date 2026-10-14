# r68-scribe observations (working notes)

Host: devin, Godot 4.7.2.stable.arch_linux.ed1daf0bf (/usr/bin/godot),
CPython 3.14.7, Linux x86_64.

## Independent midlineforge ladder (own driver, own scratch)

Probe: `proj/descendant_pipe_probe.gd` — untracked copy of tracked fixture
(pre-patch sha256 `92a40d70e31d…` = HEAD blob) + 3 scratch args:
`--midline-offset-ms` (was fixed 80), `--midline-gap-ms` (was 200),
`--midline-head-stagger-ms` (delays printraw head — explores below-window).

Driver `ladder.py`: Popen + selector-timestamped chunk reads on BOTH pipes
(reader-wall arrival times per byte chunk), verbatim extracted
`classify_process` (segment sha `749fa0607e77`, unchanged since r65) over
stdout+stderr concat — same drain shape as `run_process`/`surface_run`.

Outcomes:
- `midline_splice` (order H E E2 T): forged ERROR line fused into the head
  fragment → fabricated `...expected ERROR: DESCENDANT_PIPE_MIDLINE forged
  splice` line + signature substring destroyed. classify=False (dual-clause).
- `midline_splice_straddle_ppid` (H E T E2): ERROR inside, ppid echo lands
  PAST the tail — the "truncate" edge shape. Observed 1× at off=198.05.
- `post_tail` (H T E E2): write lands after tail → signature INTACT,
  standalone ERROR line → cls still False (error clause, not splice).
- `pre_head_standalone` (E E2 H T): only reachable via head-stagger →
  write before head → signature INTACT, standalone ERROR, cls False.

Measured (all runs): gap t_tail−t_head = 199.573–200.121ms (mean 200.088,
n≈220); write lands at offset + spawn_overhead where overhead =
exec+stat+printf ≈ 1.43–2.26ms (mean ~1.8).

Declared set {0,40,80,120,160,240} ×8 reps: splice at 0–160 (pos
1.4–164.0ms), post_tail at 240 (pos ~241.8). Hi-edge sweep: splice
through 198 (pos ≤199.99), transition band 198.05–198.35 (mixed: 15/16,
14/16, 12/16, 9/16, 3/16, 0/16 at .05/.1/.15/.25/.3/.35), ≥198.5 all
post_tail. Lo edge: non-negative offsets cannot miss below (min pos
~1.43 > 0); stagger≥2 produces pre_head (pos −0.26 to −8.7).

=> Fabrication window in write-position space = [t_head, t_tail),
   i.e. pos ∈ [0, ~200.09)ms — strict bound CONFIRMED. In declared-offset
   space ≈ [0, 198.2]ms on this host (window shifted by ~1.8ms spawn
   overhead). r66 fixed-80ms sits mid-window: holds exactly within.

KEY NUANCE: verdict is False on BOTH sides — the window controls WHICH
clause corrupts (fabricated splice + destroyed signature inside vs
standalone ERROR line + intact signature outside), not whether it
rejects. write_ppid==godot_pid in every record (pre-death provenance).

Files: declared-ladder-results.json (48), hi-edge-results.json (72),
straddle-dense-results.json (96), provenance-results.json (12),
prov-prehead-results.json (3) + stagger-{1,2,3,5,10}-results.json (25).

## Author landing status

Awaiting author tracked diff (run_battery.py + descendant_pipe_probe.gd).
Author spike `corpus/live/r68-author/spike/` uses CLOCK_REALTIME stamps
both sides (child head/tail on stderr, descendant date+%s%3N on stdout) —
same clock domain; complements my reader-side chunk timing.
When landed: re-run THEIR ladder via run_battery.py --runs <abs r68-scribe
path> and verify divergent_clause + raw-stream sha256 upgrades via
check_receipt_upgrades.py.
