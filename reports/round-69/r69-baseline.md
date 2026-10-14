# Round 69 baseline report — frozen HEAD replay (host: devin)

Seat: baseline. Immutable before-state for the r69 wave: no tracked
fixture/runner edit, no commit, no LOG/SCORECARD write. All artifacts under
`corpus/live/r69-baseline/` (scratch; `frozen/` and `*extract*/` gitignored
by `corpus/.gitignore`) plus this report. The r69 declared axis-move —
pin the fabrication-window bound's referent (gap-relative `offset<gap` vs
absolute write-latency) via a crossed `gap_ms` ladder
{50,100,200,400,800}ms at fixed `midline_offset_ms=80`, plus the
`sha256(merged)` dual_classify receipt upgrade — is **not yet landed** at
the frozen HEAD: sibling in-flight edits to `run_battery.py` (+271) and
`descendant_pipe_probe.gd` (+18) sit uncommitted in the live worktree, and
the frozen replay below measures the pre-move r68-landed surface exactly.

## Frozen-tree provenance — archive + extracted replay (r69 procedure)

The r69 brief keeps archive-only freeze but permits extraction when the
replay needs a populated tree. This round it is **load-bearing**: the live
worktree carries the sibling wave's uncommitted edits to both harness
files, so a live-tree replay would measure the wrong referent. The replay
therefore executes a byte-verified extraction of the frozen archive.

- Frozen source: `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
  archive HEAD -o corpus/live/r69-baseline/frozen/HEAD-aa94cb712ea74d84e5c22bcbec3f484adca04946.tar`
- HEAD frozen: `aa94cb712ea74d84e5c22bcbec3f484adca04946`
  (`corpus ignore: cover *tree* dirs at any depth under live/`); parent
  `5d66b4d` (xsentinel w8-F4 ignore fix) → `4d8a525` r68 report-last; the
  chain carries the r68 landed arm `f754546` (midlineforge offset ladder +
  `divergent_clause`/`sha256(raw_*)` upgrades) + hygiene `e8d4fb7`.
- Archive: **666,542,080 bytes**, sha256
  `92e761baf6c19365e8af5d7bd2b7d5dc4b6a444d480538907786d7a7837cdb5d`.
  `git archive HEAD | sha256sum` re-run = **identical** — deterministic.
- Tar members: 45,201 total = **41,425 file entries** + 3,776 directory
  entries; file count == `git ls-files | wc -l` = 41,425 exactly
  (r68: 39,307 — delta is r68's accretion incl. committed r68 receipts).
- No tracked `frozen/`, `tree/`, or `node_modules` at HEAD (`git ls-tree -r
  HEAD --name-only | grep -cE 'frozen|/tree/|node_modules'` → 0; same grep
  over tar listing → 0) — **no nested prior frozen trees**.
- Superseded artifact note: `frozen/` also holds
  `HEAD-5d66b4d14e499f24ea05fcba314f3a3ada51d62d.tar` (666,542,080 B) from
  a dead prior instance — `5d66b4d` was HEAD then; `aa94cb7` adds only
  `.gitignore` +2 lines (`git diff 5d66b4d..HEAD --stat`). The `aa94cb7`
  archive is the round's authoritative freeze.
- Extraction: `tar -xf` into `corpus/live/r69-baseline/frozen-extract/`
  (untracked, matches `live/*/*extract*/` ignore rule). Membership check —
  `comm -23 <(find . -type f/-l | sort) <(git ls-files | sort)` = **EMPTY**
  and `comm -13` = **EMPTY**: 41,391 files + 34 symlinks = 41,425, exactly
  `git ls-files` — no untracked members, nothing missing.
- Fixture digests in the extract == `HEAD:` blob digests:
  `run_battery.py` `55314bb55b409e59830fc23ea21c49d25006be6de114e31438a83c3d548ba5e6`,
  `descendant_pipe_probe.gd` `5c5c629ac187b11832c825c3f510baeab98e81517e01b65491426840f4a39d1f`,
  `stream_attribution_probe.gd` `dc0b0d5c5f44a1b4404cbe62cada0e6e53e2b33be010ea32dc72cb3892aeb286`
  (== r67/r68 verifier records). Live-worktree digests for the first two
  differ (`56adf7cb…`, `c86bda84…`) — the sibling r69 edits — confirming
  the extract was the only correct replay surface.
- `verdicts.json["seed"]` on all three runs records
  `…/r69-baseline/frozen-extract/corpus/fixtures` — the run provably
  executed frozen-HEAD fixture bytes.
- Post-run `find frozen-extract -newermt <run start>` → **0 entries**:
  the battery wrote only into `runs/<ts>/` scratch; the extract stayed
  read-only-pristine.

## Exact invocations

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`X=corpus/live/r69-baseline/frozen-extract`:

```
python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r69-baseline/runs
  # flagless -> exit 0, runs/20261014T122503087808Z/verdicts.json PASS 88/88

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r69-baseline/runs --probe-stream-attribution
  # -> exit 0, runs/20261014T122618530700Z/verdicts.json PASS 89/89
  #    + stream-attribution-verdicts.json

python3 $X/corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs corpus/live/r69-baseline/runs --probe-midlineforge-ladder
  # -> exit 0, runs/20261014T122741902523Z/verdicts.json PASS 89/89
  #    + midlineforge-ladder-verdicts.json + ladder meta row
```

All three stderr captures 0 bytes. Environment: Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python 3.14.7 —
same profile as r67/r68.

## Before-state receipt summary

- Flagless `verdicts.json`: `"verdict": "PASS"`, **88/88** (81 CASES + 7
  meta rows), sha256 `2e4d940697fc9d792eec07edcf9720c8e0fea99cfda696c158163e2115ebd30b`;
  stdout 89 `^PASS` / 0 `^FAIL` (sha256 `7ded0db7…`).
- `--probe-stream-attribution`: **89/89** (adds exactly
  `probe_stream_attribution`), sha256 `044d03d7d5222e5d56dea073b5d258673c5c9b32d82de58f8162a297af2672cc`;
  stdout 91 `^PASS` + 1 `^FAIL` — the `FAIL stream_reject` line is the
  probe arm's measured `classification=False` output, not a battery row
  (same shape as r67/r68).
- `--probe-midlineforge-ladder`: **89/89** (adds exactly
  `probe_midlineforge_ladder`), sha256 `8c0f84188003371d63bd469815a9eb1ea84d02aa09160edf5823d89debb43354`;
  stdout 90 `^PASS` / 0 `^FAIL`.
- `probe_error_clause_surface`: verdict PASS, **34 discriminations, all
  True in all three runs** — the "surface 34/34" envelope confirmed.
- Stream-attribution artifact (`eff198a071cc9b309d512c37ebe8f264d3f077d23582b56b79e0cad826e6c640`):
  24 discriminations (post-r68 20→24 shape), 9-row `divergence_table`;
  raw arm digests byte-identical to committed r68 refs
  (e.g. `raw_stdout_sha256 cb00e428…` on stream_accept).
- Midlineforge-ladder artifact (`19357a0a9cd9a02ccbd2107d3b4034e672481b379a37b2fb61db175e6604a9da`):
  `measured_window` landed `[0,40,80,120,160]`, missed `[240]`, mixed `[]`,
  lo_edge 0, hi_edge 240, nominal_gap 200 — the strict threshold bound
  reproduced; all 8 discriminations True.
- `sha256(merged)` on dual_classify records: **absent** in both artifacts
  — the r69 receipt upgrade is the wave's move, correctly not yet landed.

## Drift vs committed r68 receipts — ZERO

Field-diff over `(script, flags, expected_exit, actual_exit, signature,
verdict, error)` per `case`; meta rows on `verdict` + discriminations
bool-map (`diff_receipts.py`, output `diff-output.txt`):

| reference receipt | tracked? | ref rows | my run | common | mismatches |
|---|---|---|---|---|---|
| `r68-scribe/runs-flagless/20261014T112326985567Z` | yes | 88 | flagless | 88 | **0** |
| `r68-simplifier/runs-landed/20261014T112132992259Z` | yes | 88 | flagless | 88 | **0** |
| `r68-verifier/runs/20261014T113409881703Z` | cited in committed r68-verifier.md | 88 | flagless | 88 | **0** |
| `r68-verifier/runs/20261014T113649697385Z` | cited | 89 | attribution | 89 | **0** |
| `r68-verifier/runs/20261014T113804001922Z` | cited | 89 | ladder | 89 | **0** |
| `r68-boundary/runs2/20261014T112024144893Z` | yes | 90 | all 3 | 88/89/89 | **0** |
| `r68-simplifier/runs-landed/20261014T112415928385Z` | yes | 90 | all 3 | 88/89/89 | **0** |
| `r68-simplifier/del-measure/v{A,B,C}-runs/*` | yes | 90 ×3 | all 3 | 88/89/89 each | **0** |
| `integ-r68/runs/20261014T114450090576Z` | no (on-disk) | 90 | all 3 | 88/89/89 | **0** |

- 33/33 comparisons clean; row-set deltas are only the flag-gated probe
  rows (`probe_stream_attribution`, `probe_midlineforge_ladder`) —
  expected shape, not drift.
- Stream-attribution artifact recursive field-diff (stripping volatile
  `command`/`scratch`/`xdg_data_home`/`artifact`/`elapsed_seconds`/pids):
  **0 diffs** vs all 4 references (2 tracked + 1 cited + 1 on-disk).
- Ladder artifact: `measured_window` + per-cell `(offset,outcome)` +
  discriminations **identical to all 5 references** — no jitter-split on
  this pass (mixed `[]` everywhere).

## Pinned boundary rows — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release`: verdict PASS, expected/actual
  exit 0, error null, flags `["--spawn-forge-release"]` — origin-blind
  signature acceptance reproduced, tuple-identical to r63–r68.
- `probe_error_clause_surface`: 34/34 True ×3 runs.
- `divergence_table` seam rows (`streamdiv_seam_error`,
  `streamdiv_seam_script`, `streamdiv_seam_sig`): all `divergent=True`,
  matching r68 — the seam-fabrication surface the r69 crossed-ladder
  measures is green at HEAD.

## Artifact inventory (`corpus/live/r69-baseline/`)

- `frozen/HEAD-aa94cb7…tar` — `git archive HEAD`, 666,542,080 B, sha256
  `92e761ba…`, deterministic re-run match. Plus superseded
  `HEAD-5d66b4d…tar` (dead instance; kept for provenance).
- `frozen-extract/` — populated frozen tree (41,391 files + 34 symlinks,
  comm-clean vs `git ls-files` both directions); replay surface.
- `runs/20261014T122503087808Z/` flagless · `…122618530700Z/` attribution ·
  `…122741902523Z/` ladder — verdicts + artifacts + scratch/xdg-data.
- `battery{,-attribution,-ladder}.stdout` (sha256 `7ded0db7…`,
  `31facd93…`, `9fa2db3a…`) + 0-byte `.stderr` siblings.
- `diff_receipts.py` + `diff-output.txt` — the comparison harness and its
  full output.
- `runs/20261014T1203*`–`…1215*` — six leftover run dirs from the two
  dead prior instances (see caveats).

## Process hygiene

Post-run `ps -eo pid,ppid,stat,etime,args | grep -E 'godot|sleep'`: **no
godot processes**; only sibling-lane `sleep` descendants (r69 other seats'
probes). Zero tracked modifications introduced by this lane — `git status`
shows only the pre-existing sibling `M` marks on `run_battery.py` /
`descendant_pipe_probe.gd` and untracked `r69-*` scratch dirs.

## UNKNOWNs / caveats

- Dead-instance leftovers: runs `120354`/`120625` flagless FAIL (flaky
  `audio_playback`/`audio_bus_route`/`transition` exits and
  `census_bare_classifier_consistent` under concurrent sibling load),
  `121316` ladder FAIL on `ladder_all_writes_pre_death` (a descendant write
  raced parent death — scheduling jitter, not the window claim: its
  measured_window was the same [0..160]/240 shape); `121007`, `121147`,
  `121508` PASS. Kept untouched as provenance of the earlier attempts; my
  three runs above are this seat's clean pass.
- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, receipt shas) differ by construction; compared scope
  is the 7-field tuple + meta verdicts + discrimination bool-maps +
  stripped artifact field-diff, per r62–r68 precedent.
- The r69 declared claim (window referent gap-relative vs absolute via the
  crossed `gap_ms` ladder; `sha256(merged)` upgrade) is **not measured
  here** — it is the wave's move; this receipt is its verified-stable
  before-state. What is pinned: at frozen `aa94cb7` the r68 ladder still
  reads a strict nominal bound [0,240) over the fixed 200 ms gap, so the
  crossed ladder's falsification surface is intact.
- Not re-measured here (carried from r61–r68): signal-origin
  indistinguishability of `returncode`; live-window forgery acceptance
  under the poll() gate; >1 descendant depth, >64KiB descendant writes,
  exported builds, non-POSIX unprobed.
