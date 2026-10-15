# Round 68 baseline report — frozen before-state replay (host: devin)

Seat: baseline. This report is the immutable before-state for the r68 wave:
no tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r68-baseline/` (scratch; `frozen/` gitignored by
`corpus/.gitignore: live/*/frozen/`) plus this report. The r68 declared
axis-move (midlineforge fabrication-window ladder over the 200ms signature
gap, plus `divergent_clause`/`sha256(raw_*)` receipt-shape upgrades on the
r67 stream-attribution meta) is **not yet landed** at the frozen HEAD — the
receipts below are the pre-move surface the wave's drift comparisons are made
against. The r67-landed `classify_streams` per-channel divergence arm
(`--probe-stream-attribution`) is present at HEAD and green.

## Frozen-tree provenance — archive only (r68 procedure change)

The r68 brief's freeze rule changed vs r67: `git archive HEAD` **output
only, no populated-tree extraction** ("Do NOT extract the archive either —
receipts/proofs only"). The archive itself is the freeze receipt; the replay
below executes the live worktree, which is byte-identical to the frozen HEAD
(pinned three ways: clean `git status` on tracked paths, fixture digests ==
HEAD blobs, deterministic re-archive digest match).

- Frozen source: `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
  archive HEAD -o corpus/live/r68-baseline/frozen/HEAD-1101cb37e8c44b084d6ce6f8f8209919a2f59bd5.tar`
- HEAD frozen: `1101cb37e8c44b084d6ce6f8f8209919a2f59bd5`
  (`r67 report-last: ADMIT — stream-classifier divergence map (4 families,
  12/27 arms) + verifier AGREE 5/5 + lesson/LOG/SCORECARD`); parent chain
  carries the r67 landed arm `d44ba86` + fixup `9e946c9`
  (`classify_streams`/`dual_classify`/`streamdiv_arm` + load-bearing
  `sd_sig_head`) and r66's `cb84d0a` rejection-clause surface map.
- Archive: **655,554,560 bytes (~625 MiB)**, sha256
  `c8a2e7d4533a6957cba817722f426f5a75b01d1b4408ced1a846959529588f49`.
  `git archive HEAD | sha256sum` re-run = **identical digest** — archive is
  deterministic for this commit (vs r67 raw tar 651,827,200 B: +3.7 MB from
  r67's committed reports/lessons/receipts).
- Tar members: 42,886 total = **39,307 file entries** (`grep -v '/$'`) +
  3,579 directory entries. File count == `git ls-files | wc -l` = 39,307
  exactly (r67 baseline: 38,504 — delta is r67's accretion).
- No tracked `frozen/`, `tree/`, or `node_modules` paths at HEAD
  (`git ls-tree -r HEAD --name-only | grep -cE 'frozen|/tree/|node_modules'`
  → 0; same grep over tar listing → 0) — **no nested prior frozen trees**.
- `git status` before and after both battery runs: only untracked
  `corpus/live/r68-*/` sibling+self scratch dirs; **zero tracked
  modifications** — the executed tree stayed byte-identical to the archived
  HEAD for the whole measurement window.
- `run_battery.py` sha256 `8d7e4d946e419c8f2fd4c8890cc2d3286f009b8434abc27392724d903c8a4634`,
  `descendant_pipe_probe.gd` `92a40d70e31daa5048a4c49864d4ece276fbfbac8cb93f2cc6751c6c798caa91`,
  `stream_attribution_probe.gd` `dc0b0d5c5f44a1b4404cbe62cada0e6e53e2b33be010ea32dc72cb3892aeb286`
  — each == its `HEAD:` blob digest AND == the digests the r67 verifier
  recorded on the committed tree.
- `verdicts.json["seed"]` records
  `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures` — the
  run provably executed committed-HEAD fixture bytes (digests above), the
  same receipt shape the r67 verifier produced. Contamination risk: sibling
  lanes could in principle edit `corpus/fixtures/` mid-run; pre/post
  `git status` shows no tracked mutation occurred.

## Exact invocations

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` (canonical lane
repo; `~/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d` symlinks here):

```
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r68-baseline/runs
  # flagless -> exit 0, runs/20261014T104854073132Z/verdicts.json
  #            PASS 88/88

python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r68-baseline/runs \
  --probe-stream-attribution
  # flagged  -> exit 0, runs/20261014T105014927352Z/verdicts.json
  #            PASS 89/89; stream-attribution-verdicts.json emitted
```

Both stderr captures 0 bytes. Environment: Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python 3.14, this
host's `systemd --user` subreaper — identical profile to the r67
baseline/verifier environment.

## Before-state receipt summary

Flagless `battery.stdout` tail (verbatim):

```
PASS descendant_pipe_detached_control: exit=0 signature='DESCENDANT_PIPE_PROBE: expected signature'
PASS descendant_pipe_forged_signature_release: exit=0 signature='DESCENDANT_PIPE_PROBE: expected signature'
PASS independent save process probe: …/r68-baseline/runs/20261014T104854073132Z/save-process-verdicts.json
PASS spontaneous crash classification meta
PASS descendant pipe-EOF meta
PASS descendant signature-spoof meta
PASS while-live signature-gate meta
PASS descendant error-spoof meta
PASS error-clause surface meta
PASS battery: …/r68-baseline/runs/20261014T104854073132Z/verdicts.json
```

- Flagless `verdicts.json`: **`"verdict": "PASS"`, 88 results, 88 PASS / 0
  FAIL** (81 CASES + 7 meta rows). sha256
  `ab10e77a0c9b8f1de11ed99f2657a61368f61261f033ab3c0aaab5349ed3ab50`.
  stdout: 89 `^PASS` lines, 0 `^FAIL`.
- Flagged `verdicts.json`: **`"verdict": "PASS"`, 89 results, 89 PASS / 0
  FAIL** — adds exactly `probe_stream_attribution`. sha256
  `88f22ac31db345695051789326ed02ece7807edab0084f1218ea69c23e6deb0f`.
- **`probe_error_clause_surface`: verdict PASS, 34 discriminations, all
  True in both runs** — the brief's "surface 34/34" confirmed.
- `probe_stream_attribution` row: verdict PASS, artifact pointer to
  `stream-attribution-verdicts.json` sha256
  `d44e057c6600744b03b5e318af892db7e185c8232c164df9a1c4175fa4666dd4`.
  Artifact: `divergence.discriminations` = **20 keys all True**;
  `divergence_table` = **9 rows** with `divergent` flags identical to the
  r67 verifier table (stream_accept F, stream_reject T, stdout_error T,
  stderr_error F-control, stderr_structured T, sig_on_stderr T,
  seam_error T, seam_script T, seam_sig T). The `FAIL stream_reject` stdout
  line is the probe arm's measured `classification=False` output, not a
  battery row — same shape as r67.
- **Stream-attribution artifact is content-identical to the r67 verifier's
  receipt** (`6db5015e…`): field-level recursive diff after stripping only
  volatile fields (`artifact`/`command`/`scratch`/`xdg_data_home`/
  `elapsed_seconds`) → **equal**. No `divergent_clause` keys, no
  `sha256(raw_*)` fields at this HEAD — those are the wave's declared
  upgrades, not yet landed.
- Opt-in artifact: `save-process-verdicts.json` present in the flagless run
  dir.

## Drift vs committed r67 receipts — ZERO

Field-diff over the established tuple `(script, flags, expected_exit,
actual_exit, signature, verdict, error)` indexed by `case`; meta rows
compared on `verdict` + `discriminations` bool-map equality:

| reference receipt | tracked? | ref rows | common | new-only | old-only | mismatches |
|---|---|---|---|---|---|---|
| `r67-verifier/runs/20261014T102359619107Z` (flagless) | no (cited in committed r67-verifier.md) | 88 | 88 | [] | [] | **0** |
| `r67-verifier/runs/20261014T102529598296Z` (flagged) | no (cited) | 89 | 89 | [] | [] | **0** |
| `r67-baseline/runs/20261014T094859374505Z` | no (cited in committed r67-baseline.md) | 88 | 88 | [] | [] | **0** |
| `r67-simplifier/runs-landed/20261014T100135501917Z` | **yes** | 88 | 88 | [] | [] | **0** |
| `r67-simplifier/runs-landed/20261014T100512403308Z` | **yes** | 89 | 89 | [] | [] | **0** |
| `r67-author/runs/20261014T095753034446Z` | no | 88 | 88 | [] | [] | **0** |
| `r67-author/runs/20261014T095910487678Z` (full-flag) | no | 99 | 89 | [] | 10 opt-in rows | **0** |
| `r67-author/pretree-runs/20261014T100102229717Z` (full-flag) | no | 99 | 89 | [] | 10 opt-in rows | **0** |
| `r67-boundary/runs/20261014T101324429639Z` | no | 88 | 88 | [] | [] | **0** |
| `r67-boundary/runs/20261014T101440531775Z` | no | 89 | 89 | [] | [] | **0** |
| `r67-reviewer/runs/20261014T095231662268Z` | no | 88 | 88 | [] | [] | **0** |
| `r67-scribe/runs/20261014T095312613881Z` | no | 88 | 88 | [] | [] | **0** |
| `r67-scribe/runs/20261014T095922857280Z` | no | 89 | 89 | [] | [] | **0** |

- The 99-row author receipts carry 10 flag-gated opt-in rows my briefed
  invocations don't emit (`mutant_*` ×2, `probe_crash_exit`,
  `probe_export_launch`, `probe_godot_error`, `probe_timeout`,
  `probe_unrelated_error_*` ×4) — expected shape, not drift.
- Discrimination bool-maps identical on every common meta row across all 13
  references (0 disc-map diffs).

## Pinned boundary rows — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release` (CASES row): `verdict PASS`,
  `expected_exit 0`, `actual_exit 0`, `error null`,
  `flags ["--spawn-forge-release"]`, signature `'DESCENDANT_PIPE_PROBE:
  expected signature'` — tuple-identical to r63–r67. Origin-blind
  signature acceptance reproduced as documented.
- `probe_error_clause_surface` meta: PASS, 34/34 True — merged-only surface
  map stable.
- `divergence_table` midlineforge-relevant rows (`streamdiv_seam_error`,
  `streamdiv_seam_script`, `streamdiv_seam_sig`): all `divergent=True`,
  matching r67 — the seam-fabrication surface the r68 window-ladder
  axis-move measures is green at HEAD.

## Artifact inventory (all under `corpus/live/r68-baseline/`)

- `frozen/HEAD-1101cb37e8c44b084d6ce6f8f8209919a2f59bd5.tar` — `git archive
  HEAD` output, 655,554,560 B, sha256 `c8a2e7d4…` (deterministic; re-run
  matches). Not extracted, per r68 rule. Gitignored by
  `corpus/.gitignore: live/*/frozen/`.
- `runs/20261014T104854073132Z/` — flagless run: `verdicts.json` sha256
  `ab10e77a…` + `scratch/`, `xdg-data/`, `missing-preset-scratch/`,
  `save-process-verdicts.json`.
- `runs/20261014T105014927352Z/` — flagged run: `verdicts.json` sha256
  `88f22ac3…`, `stream-attribution-verdicts.json` sha256 `d44e057c…`, +
  scratch siblings.
- `battery.stdout` — flagless stdout, sha256
  `4147a24aebad4c517d5f493abf14816907ab29fa3769d35cfd3fdc472778ad5e`;
  `battery.stderr` 0 B. `battery-flagged.stdout` sha256
  `130002ef930fb1b0205a343970fd19565fb4749a0c3398d784d2db3d7ebf2a7c`;
  `battery-flagged.stderr` 0 B.

## Process hygiene

Post-run `ps -eo pid,ppid,stat,etime,args | grep -E 'godot|sleep'`: **no
godot engine processes and no fixture `sleep` descendants attributable to
this lane's runs** — every `--headless` invocation under
`corpus/live/r68-baseline/runs/` exited. Remaining matches are sibling
lanes in flight on their own scratch: `game-dev-3d r77-baseline`
(different repo tree), `r68-critic` midline probe, `r68-simplifier` digest
poll — none leaked by this replay.

## Drift / archive / command / sha summary

| item | value |
|------|-------|
| frozen HEAD | `1101cb37e8c44b084d6ce6f8f8209919a2f59bd5` |
| archive | tar-only (no extraction), 655,554,560 B, sha256 `c8a2e7d4…`, deterministic re-run match |
| archive members | 39,307 files == `git ls-files`; 0 frozen/tree/node_modules |
| battery flagless | exit 0, stderr 0 B → `verdict PASS`, **88/88** |
| battery `--probe-stream-attribution` | exit 0, stderr 0 B → `verdict PASS`, **89/89** |
| surface meta | **34/34 discriminations True** (both runs) |
| stream-attribution artifact | 20/20 discriminations True, 9-row table == r67 verifier (stripped-equal) |
| tuple-diff vs r67 receipts | **0 mismatches on all 13 references** |
| flagless verdicts.json sha256 | `ab10e77a0c9b8f1de11ed99f2657a61368f61261f033ab3c0aaab5349ed3ab50` |
| flagged verdicts.json sha256 | `88f22ac31db345695051789326ed02ece7807edab0084f1218ea69c23e6deb0f` |
| stream-attribution artifact sha256 | `d44e057c6600744b03b5e318af892db7e185c8232c164df9a1c4175fa4666dd4` |
| fixture sha256 (runner/pipe/stream probes) | `8d7e4d94…` / `92a40d70…` / `dc0b0d5c…` == HEAD blobs == r67 records |

## UNKNOWNs / caveats

- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, receipt shas) differ from prior runs by construction;
  the compared scope is the 7-field verdict tuple + meta verdicts +
  discrimination bool-maps + full artifact field-diff, per r62–r67
  verifier precedent.
- The r68 freeze is archive-only: replay executed the live worktree rather
  than an extracted copy (r67 baseline's method). Provenance is pinned by
  clean pre/post `git status`, fixture digest == HEAD-blob equality, and
  `verdicts.json["seed"]`; a mid-run sibling fixture mutation would have
  been caught by the post-run status check and none occurred. This is the
  same execution surface the r67 verifier used.
- Single host, single pass of each invocation; no transient flake observed
  (exit 0 both runs, stderr logs empty).
- The r68 declared claim (strict measured midlineforge window [lo,hi)
  inside the 200ms signature gap; `divergent_clause` + `sha256(raw_*)`
  receipt upgrades) is **not measured here** — it is the wave's move, and
  this receipt is its before-state. What this run pins: the seam-divergence
  rows and the 34-clause surface map are green at HEAD, so the wave's move
  lands on a verified-stable base.
- Not re-measured here (carried from r61–r67): signal-origin
  indistinguishability of `returncode`; live-window forgery acceptance
  under the poll() gate; >1 descendant depth, >64KiB descendant writes,
  exported builds, non-POSIX unprobed.
