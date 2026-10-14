# Round 67 baseline report — frozen before-state replay (host: devin)

Seat: baseline. This report is the immutable before-state for the r67 wave:
no tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r67-baseline/` (scratch; `frozen/` gitignored by
`corpus/.gitignore: live/*/frozen/`) plus this report. The r67 declared
axis-move (per-channel divergence of `classify_streams` vs merged
`classify_process` — stdout-carried `ERROR:` absorbed PASS-shaped where merged
rejects; stderr-carried bytes under a stricter every-nonblank-line rule) is
**not yet landed** at the frozen HEAD — the 88-row list below is the pre-move
surface the wave's drift comparisons are made against. The r66-landed
rejection-clause surface map (`probe_error_clause_surface`, merged-stream
axes only) is present at HEAD and green.

## Frozen-tree provenance

- Frozen source:
  `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin archive HEAD | tar -x -C corpus/live/r67-baseline/frozen`
  — tracked files only, no `.git`, no extraction-then-re-archive.
- HEAD frozen: `4a4def9a9bc8dbbf7f9689b59b28211677095c9f`
  (`r66 report-last: verifier AGREE 5/5 + scribe/boundary reports +
  rejection-clause-surface lesson + LOG/SCORECARD`); parent chain carries the
  r66 landed arm `cb84d0a` (allowlist preemptor / splitforge / seamforge /
  midlineforge + `probe_error_clause_surface` meta row).
- Extracted **38,504 files** — exactly `git ls-files | wc -l` at HEAD (r66
  baseline: 36,912; the delta is r66's committed reports/lessons/receipts).
- No tracked `frozen/`, `tree/`, or `node_modules` paths exist at HEAD
  (`git ls-tree -r HEAD --name-only | grep -cE 'frozen|baseline/tree|node_modules'` → 0),
  so the archive contains **no nested prior frozen trees**.
- **Archive size: raw tar `git archive HEAD | wc -c` = 651,827,200 bytes
  (~622 MiB); extracted tree `du -sb` = 617,691,135 bytes (`du -sh` 711M
  block-allocated)** vs r66-baseline's 644,106,240 raw / 611,373,544 extracted
  — +7.7 MB raw growth from the r66 landed arm, its committed receipts, and
  the round-66 report set. Consistent with the post-`tree/`-untrack ~614 MiB
  norm plus one round of accretion.
- Frozen `corpus/fixtures/run_battery.py` sha256
  `76d37ace4b0bbc3c92b83baf431bf6046cdfe4fa88f4bf3cd833dee99269b1ed` —
  byte-identical to the live worktree copy and the `HEAD:` blob, and
  identical to the digest the r66 verifier recorded on committed `cb84d0a`
  bytes.
- Frozen `corpus/fixtures/descendant_pipe_probe.gd` sha256
  `92a40d70e31daa5048a4c49864d4ece276fbfbac8cb93f2cc6751c6c798caa91` —
  byte-identical to live worktree and `HEAD:` blob (the r66-committed fixture
  carrying allowforge/splitforge/seamforge/midlineforge + reparent_gate).
- `verdicts.json["seed"]` records
  `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r67-baseline/frozen/corpus/fixtures`
  → the run provably executed the **frozen copy**, not the live tree.
  Contamination risk: none; concurrent sibling-lane/seat edits cannot reach
  the archive.

## Exact invocation

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` (canonical lane
repo; `~/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d` symlinks here):

```
python3 corpus/live/r67-baseline/frozen/corpus/fixtures/run_battery.py \
  --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r67-baseline/runs
```

Bare invocation — no opt-in probe flags — to reproduce the r66-verifier
comparison surface (81 CASES + 7 meta = 88 rows). stdout tee'd to
`corpus/live/r67-baseline/battery.stdout`; pipeline exit 0; stderr capture
`battery.stderr` is **0 bytes**.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Python 3.14, this host's `systemd --user` subreaper — identical profile to
the r66 baseline/verifier environment.

## Before-state receipt summary (verbatim tail of `battery.stdout`)

```
PASS descendant_pipe_detached_control: exit=0 signature='DESCENDANT_PIPE_PROBE: expected signature'
PASS descendant_pipe_forged_signature_release: exit=0 signature='DESCENDANT_PIPE_PROBE: expected signature'
PASS independent save process probe: /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r67-baseline/runs/20261014T094859374505Z/save-process-verdicts.json
PASS spontaneous crash classification meta
PASS descendant pipe-EOF meta
PASS descendant signature-spoof meta
PASS while-live signature-gate meta
PASS descendant error-spoof meta
PASS error-clause surface meta
PASS battery: /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r67-baseline/runs/20261014T094859374505Z/verdicts.json
```

- `verdicts.json`: **`"verdict": "PASS"`, 88 results, 88 PASS / 0 FAIL**
  (81 CASES + 7 meta rows). sha256
  `cf4f79ae87bfc4b734a8c3cfcdab70d921dea0487f8153a3e1e81a35fa676a9e`.
- stdout: 89 `^PASS` lines (81 case lines + 7 meta lines + closing
  `PASS battery`), **0 `^FAIL` lines** — same shape as the r66-verifier
  bare run.
- Meta rows (7): `probe_save_independent_process`,
  `probe_spontaneous_crash_classification`, `probe_descendant_pipe_eof`,
  `probe_descendant_signature_spoof`, `probe_while_live_signature_gate`,
  `probe_descendant_error_spoof`, `probe_error_clause_surface`.
- **`probe_error_clause_surface`: verdict PASS, 34 discriminations, all
  True** — the brief's "surface 34/34" confirmed on the frozen tree.
- Opt-in artifact: `save-process-verdicts.json` present; no flag-gated
  artifacts — bare run by design.

## Drift vs committed r66 receipts — ZERO

Field-diff of my `verdicts.json` vs r66 receipts over the established tuple
`(script, flags, expected_exit, actual_exit, signature, verdict, error)`
indexed by `case`; meta rows compared on `verdict` + `discriminations`
bool-map equality:

| reference receipt | tracked? | common | new-only | old-only | mismatches |
|---|---|---|---|---|---|
| `r66-verifier/runs/20261014T092653605430Z` | no (cited in committed r66-verifier.md) | 88 | [] | [] | **0** |
| `runs/20261014T053603255626Z` (prior verifier) | no (cited in committed r66-verifier.md) | 88 | [] | [] | **0** |
| `r66-reviewer/runs-postdiff/20261014T051216915162Z` | **yes** | 88 | [] | [] | **0** |
| `r66-simplifier/runs-author/20261014T051322328700Z` | **yes** | 88 | [] | [] | **0** |
| `r66-simplifier/runs-extracted/20261014T050739566712Z` | **yes** | 87 | `[probe_error_clause_surface]` | [] | **0** |
| `r66-author/pretree-runs/20261014T051443586564Z` | **yes** | 87 | `[probe_error_clause_surface]` | 11 opt-in probe rows | **0** |

- The `runs-extracted` and `pretree` references predate the r66 arm (87-row
  surface) or carry flag-gated opt-in rows (`mutant_*`, `probe_crash_exit`,
  `probe_export_launch`, `probe_godot_error`,
  `probe_stream_attribution`, `probe_timeout`,
  `probe_unrelated_error_*` ×4) — both deltas are expected shape, not drift.
- Meta discriminations stable: `probe_descendant_error_spoof` **29/29 True**,
  `probe_while_live_signature_gate` **12/12**,
  `probe_descendant_signature_spoof` **10/10**,
  `probe_error_clause_surface` **34/34** — identical key sets and bool-maps
  to the r66-verifier receipt (0 discrimination-map diffs across all refs
  that carry the row).

## Pinned boundary rows — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release` (CASES row): `verdict PASS`,
  `expected_exit 0`, `actual_exit 0`, `error null`,
  `flags ["--spawn-forge-release"]`,
  `signature 'DESCENDANT_PIPE_PROBE: expected signature'` — tuple-identical
  to r63–r66. Origin-blind signature acceptance reproduced as documented.
- `probe_error_clause_surface` meta row (the r66-landed arm): `verdict PASS`,
  all **34 discriminations true**, including the r67-relevant anchors
  `merged_classification_stream_blind`-family entries — the merged-only
  surface map this wave's per-channel axis-move extends.

## Artifact inventory (all under `corpus/live/r67-baseline/`)

- `frozen/` — `git archive HEAD` extraction (38,504 files, 617,691,135
  bytes; raw tar 651,827,200 bytes). Gitignored by `corpus/.gitignore:
  live/*/frozen/`.
- `runs/20261014T094859374505Z/verdicts.json` — sha256 `cf4f79ae…` above;
  siblings `scratch/`, `xdg-data/`, `missing-preset-scratch/`,
  `save-process-verdicts.json`.
- `battery.stdout` — verbatim runner stdout, sha256
  `d8f506b4547d52d11f99699f88d0ec634f6542c7e7bad94d85c4c6cc76d95ec8`.
- `battery.stderr` — 0 bytes.

## Process hygiene

Post-run `ps -eo pid,ppid,stat,etime,args | grep -E 'godot|sleep'`: **no
godot engine processes and no fixture `sleep` descendants attributable to
this run** — every `--headless` invocation under my runs path exited.
Remaining matches are unrelated: host `godot-mcp` node services and a
**sibling lane's** in-flight `game-dev-3d r76-baseline` full-flag run
(different repo tree, pid 2487585 + its godot child) — none this lane, none
leaked by this replay.

## Drift / archive-size / command / sha summary

| item | value |
|------|-------|
| frozen HEAD | `4a4def9a9bc8dbbf7f9689b59b28211677095c9f` |
| archive raw tar | 651,827,200 B (~622 MiB) vs r66 644,106,240 (+7.7 MB) |
| extracted tree | 38,504 files / 617,691,135 B (`du -sb`; `du -sh` 711M) |
| battery | bare, exit 0, stderr empty → `verdict PASS`, **88/88** |
| surface meta | **34/34 discriminations True** |
| tuple-diff vs r66 receipts | **0 mismatches** on all six references (88/88 on the four same-surface refs) |
| discriminations | error_spoof 29/29, while_live_gate 12/12, sig_spoof 10/10, surface 34/34 — all True |
| verdicts.json sha256 | `cf4f79ae87bfc4b734a8c3cfcdab70d921dea0487f8153a3e1e81a35fa676a9e` |
| frozen runner/probe sha256 | `76d37ace…` / `92a40d70…` == HEAD blobs == live copies |

## UNKNOWNs / caveats

- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, receipt shas) differ from prior runs by construction;
  the compared scope is the 7-field verdict tuple + meta verdicts +
  discrimination bool-maps, per r62–r66 verifier precedent.
- Single host, single clean run; no transient flake observed. A sibling
  lane (`game-dev-3d r76-baseline`) was in flight during this run on a
  different repo tree; it cannot reach this receipt — the frozen copy is the
  committed `4a4def9` blobs (verified above) and `verdicts.json["seed"]`
  proves execution from `frozen/`.
- The brief's "88/88 + surface 34/34" is the bare-invocation surface
  (matching the r66-verifier receipt shape). The 11 flag-gated opt-in rows
  of full-flag runs are not emitted by a bare run — not removed rows.
- The r67 declared claim (stdout-carried `ERROR:` absorbed by
  `classify_streams`; stderr-only stricter scan) is **not measured here** —
  it is the wave's move, and this receipt is its before-state. What this run
  does pin: the merged-classifier surface map (34/34) is green at HEAD, so
  any r67 divergence arm lands on a verified-stable base.
- Not re-measured here (carried from r61–r66): signal-origin
  indistinguishability of `returncode`; live-window forgery acceptance
  under the poll() gate; >1 descendant depth, >64KiB descendant writes,
  exported builds, non-POSIX unprobed.
