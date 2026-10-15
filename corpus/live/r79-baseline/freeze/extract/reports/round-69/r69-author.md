# Round 69 author report — fabrication-window REFERENT (gap-relative vs absolute) + sha256(merged) receipt

Seat: author | Lane: g2d | Host: devin | Godot 4.7.2.stable.arch_linux.ed1daf0bf (`/usr/bin/godot`)
Respawn note: this is author instance #2. Instance #1 landed the
implementation and died mid-verification (rate limit). I verified the landed
diff, ran my own battery + reference runs, and report my measured results.
The operator committed the work as `ec2cda6` while my verification ran; the
committed files are sha256-identical to the files every run below measured
(`56adf7cb…` run_battery.py, `c86bda84…` descendant_pipe_probe.gd), so all
evidence applies to the landed state.

## Declared move (verbatim contract)

Pin the fabrication-window bound's REFERENT — gap-relative vs absolute —
via a crossed ladder the offset ladder cannot express: hold
`midline_offset_ms=80` fixed, sweep the signature gap {50,100,200,400,800}ms.
Declared falsifiable claim: the window follows `offset<gap` — falsified if
fabrication persists at gaps ≪80ms or fails at gaps ≫80ms (which would make
the bound an absolute write-latency constant). Plus `sha256(merged)` on every
dual_classify record (concat-order drift gate, r66 stderr+stdout caveat).
Opt-in flags only; flagless 88/88 + surface 34/34 + prior dual_classify rows
byte-stable modulo the additive field.

## Landed implementation (verified, not rewritten)

`corpus/fixtures/descendant_pipe_probe.gd` +18/−4 (`git show ec2cda6 --stat`):
- `--midline-gap-ms=N`, parsed in `_initialize` alongside the r66
  `--midline-offset-ms` flag (:128-131), default **200** — the r66/r68 arm is
  byte-stable.
- Feeds BOTH the `gap_ms=` banner field (:144) and `OS.delay_msec` (:188);
  comment block updated (:96-99, :183-186).

`corpus/fixtures/run_battery.py` +269/−2:
- `--probe-midlineforge-gapladder` argparse row (:119).
- Gap-ladder meta (:2183-2427): `gapladder_cells` = the declared fixed-offset
  sweep `(80, {50,100,200,400,800})` **plus the r69 critic's crossed cells**
  `(300,400),(300,800),(600,800)` — 8 cells × 3 reps through `surface_run`.
  The critic proved the declared grid alone cannot separate gap-relative from
  an absolute ~198ms edge (4/5 cells non-distinguishing, (80,50) confounded
  with flag wiring); the operator folded the crossed cells in — offsets >198
  inside the gap fabricate ONLY under gap-relative. This is the round's
  substantive augmentation over the literal brief text.
- `referent_verdict` (:2276-2288): `gap_relative` iff fabricated cells ==
  inside-gap cells AND all crossed cells fabricate; `absolute_edge` iff all
  crossed cells miss while base inside cells fabricate;
  `absolute_write_latency` iff every cell fabricates; else `unclassified`.
- 12 discriminations (:2307-2364) incl. `write_ppid` carried as **data only** —
  byte order (spliced_line / signature_observed) is ground truth because the
  ppid flip lags process teardown; `crossed_cells_elapsed_tracks_gap` is the
  wiring witness (elapsed > gap/2).
- `raw_merged_sha256 = sha256(so+se)` added to `dual_classify` (:2778-2779),
  propagated into `divergence_table` rows (:2876) and into
  `dual_records_same_input_digests` (:3033-3058) as a re-verified gate —
  catches stderr-before-stdout concat-order drift invisible to the per-channel
  digests.

## Measured results — declared claim CONFIRMED: referent = `gap_relative`

Canonical root `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`.
Flagged combo run (exact command):

```text
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --probe-midlineforge-gapladder --probe-midlineforge-ladder \
    --probe-stream-attribution \
    --runs corpus/live/r69-author/runs        → exit 0
stdout: corpus/live/r69-author/battery2-flagged.stdout (stderr empty)
```

`runs/20261014T123945501757Z/verdicts.json`: **91/91 PASS** (88 base +
midlineforge-ladder + midlineforge-gapladder + stream-attribution).

`runs/20261014T123945501757Z/midlineforge-gapladder-verdicts.json`: **PASS,
12/12 discriminations True**, `referent_verdict = "gap_relative"`. Measured
cell matrix (24 reps, all clean exit-0):

| offset | gap | inside | outcome | reps_landed | median elapsed | write_pre_death |
|---|---|---|---|---|---|---|
| 80  | 50  | false | missed     | 0/3 | 0.743s | false,false,false |
| 80  | 100 | true  | fabricated | 3/3 | 0.787s | true ×3 |
| 80  | 200 | true  | fabricated | 3/3 | 0.914s | true ×3 |
| 80  | 400 | true  | fabricated | 3/3 | 1.109s | true ×3 |
| 80  | 800 | true  | fabricated | 3/3 | 1.573s | true ×3 |
| 300 | 400 | true  | fabricated | 3/3 | 0.866s | true ×3 |
| 300 | 800 | true  | fabricated | 3/3 | 1.296s | true ×3 |
| 600 | 800 | true  | fabricated | 3/3 | 1.370s | true ×3 |

- Fabrication landed exactly on cells with `offset < gap` — the declared
  `offset<gap` claim confirmed; referent is the gap, not an absolute
  write-latency constant.
- Horn 1 (≪): the (80,50) cell missed 0/3 — every rep observed the intact
  signature (`signature_observed=True`, `spliced_line=None`), the ERROR landed
  on its own line, and `write_ppid=1573 ≠ godot_pid` (child reparented) —
  byte-order proof the write landed post-tail.
- Horn 2 (≫): all super-offset cells fabricate 3/3; every inside-cell write
  sampled `write_ppid == godot_pid` (pre-death — reliable in this direction:
  the child is still inside `delay_msec`).
- Crossed cells (300,400),(300,800),(600,800) ALL fabricated — refuting any
  absolute edge below ~602ms; the fixed-offset grid alone could not have
  shown this (the critic's distinguishing region).
- Wiring witness: median elapsed scales with gap (0.74s@50 → 1.57s@800;
  every crossed-cell rep > gap/2).
- The (80,200) anchor reproduces the r66/r68 arm byte-for-byte
  (`gap200_anchor_still_fabricates`).

r68 offset-ladder arm unchanged: `midlineforge-ladder-verdicts.json` PASS,
8/8 discriminations, measured window `[0,240]ms` nominal (landed
{0,40,80,120,160}, missed {240}) identical to r68.

## Byte-stability / opt-in contract

Flagless (exact command): `python3 corpus/fixtures/run_battery.py --godot
/usr/bin/godot --runs corpus/live/r69-author/runs` → exit 0,
`runs/20261014T122943272408Z/verdicts.json` **88/88 PASS**, surface
`probe_error_clause_surface` **34/34 all-True**; stdout
`corpus/live/r69-author/battery2.stdout`, stderr empty.

HEAD reference: pretree fixtures (`corpus/live/r69-author/pretree/`,
byte-verified = `git show HEAD:corpus/fixtures/*` for both files) run as
`python3 corpus/live/r69-author/pretree/corpus/fixtures/run_battery.py
--godot /usr/bin/godot --runs corpus/live/r69-author/pretree-runs` → exit 0,
`pretree-runs/20261014T122954497622Z/verdicts.json` **88/88 PASS**.

Row-level diff landed-vs-HEAD over
{script, flags, expected_exit, actual_exit, signature, verdict, error}:
**88 common rows, 0 mismatches**; surface discrimination key-sets identical.

dual_classify byte-stability: HEAD stream-attribution run
(`pretree-runs/20261014T123950534566Z/stream-attribution-verdicts.json`,
89/89 PASS) vs landed
(`runs/20261014T123945501757Z/stream-attribution-verdicts.json`, 24/24
discriminations True): the 9-row `divergence_table` differs ONLY by the
additive `raw_merged_sha256` key — 0 non-additive field diffs (digests are
deterministic across runs for these pid-free streams). In-run gate
`dual_records_same_input_digests=True` re-verifies the merged digest against
the canonical stdout+stderr concat. Note: rows with empty stderr
(e.g. `stream_accept`) trivially get merged==stdout digest; `stream_reject`
has both channels non-empty and its merged digest differs from each
channel's — the order-binding is live where it matters.

Default-gap byte-stability (direct godot, scratch projects under
`corpus/live/r69-author/scratch-direct/`):
- HEAD fixture vs landed fixture, `--spawn-midlineforge --midline-offset-ms=80`
  (no gap flag): outputs byte-identical modulo pid values — both banner
  `gap_ms=200`, both fabricate (`DESCENDANT_PIPE_PROBE: expected ERROR:
  DESCENDANT_PIPE_MIDLINE forged splice`).
- Landed + `--midline-gap-ms=800`: banner `gap_ms=800`, wall 1.357s vs 0.664s
  at default — the flag demonstrably reaches `delay_msec`.

## Provenance / caveats

- Instance #1's earlier runs remain in `corpus/live/r69-author/runs/`
  (120912 flagless, 121043 gapladder, 121231 stream-attr, 121402 ladder,
  121545 full-101) and `pretree-runs/121551` — its 121545 run was the FULL
  eight-probe battery (101/101 PASS incl. export-launch) but predates the
  crossed-cell fold (its gapladder artifact is the 5-cell shape). The fold
  touches only the gapladder block; my re-run covers every changed line.
- The operator committed `ec2cda6` mid-verification; it also picked up a
  `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` blob (bytecode
  artifact — cosmetic hygiene note, not mine to revert).
- The r69-simplifier lane was concurrently running its own
  `--probe-midlineforge-gapladder` in its own scratch while I measured —
  separate `--runs` dir, no interference; my artifact carries 12/12
  discriminations incl. the timing-margin checks.
- No commits/pushes performed by this seat; report + scratch only.

## Verdict

Declared claim CONFIRMED under measurement: the midlineforge
fabrication-window bound is **gap-relative** — the splice lands iff the
descendant write reaches the captured stdout pipe before the signature tail
flush (`write position < gap`), on Linux headless Godot 4.7.2 POSIX pipe
semantics only. The crossed-cell augmentation is what makes the claim
falsifiable-as-measured; the additive `raw_merged_sha256` receipt field is
live and gated. Opt-in contract held: flagless 88/88 + surface 34/34 + prior
dual rows byte-stable modulo the additive field.
