# r101-sent1 — SENT-1 scope/identity sentinel

Plan (5 lines):
1. Capture baseline: HEAD sha, `git status --porcelain` (line/byte-exact), shared-file status, `uptime` load context.
2. Late-round passes: re-run `git status --porcelain -uall`, `git diff --name-only`, staged diff; diff against baseline; classify every changed path against the allowlist.
3. Shared-file audit: `run_battery.py`, `SCORECARD.md`, `LOG.md`, `SHONEN.md`, `PROVINCE.md` must appear in NO status/diff output.
4. Commit audit: zero commits beyond baseline HEAD on `main` (`git log <baseline>..HEAD --oneline` must be empty).
5. Report violations with exact paths; close with a timestamped census and the observation limits of a point-in-time snapshot.

Status: **complete**. Verdict: allowlist PASS with 1 flagged deviation class (78 untracked files under `corpus/live/r101-ver11/` + `corpus/live/r101-ver17/`, outside the stated allowlist — adjudicate before commit). Zero commits, zero tracked-file edits, zero shared-file touches, zero lane-local `run_battery.py` processes observed.

## Load context (baseline, verbatim)

```
16:22:01 up 1 day, 16:22,  1 user,  load average: 43.86, 24.27, 14.98
```

Load stayed 30–53 across all passes (3D-lane swarm). No 2D-lane Godot runs were killed or retried by this seat; this seat ran no Godot at all.

## Baseline

- HEAD `05a7289961bafad79b041309d74913dff577ef1c` (`05a72899 gitignore: stop re-tracking round-local freeze/scratch materializations`), branch `main`.
- Baseline `git status --porcelain` (aggregated form): 1 line / 22 bytes: `?? reports/round-101/` — round-local shards only, tree otherwise clean.
- Shared files clean at baseline (`git status --porcelain -- <shared>` → 0 bytes).

## Exact commands used (read-only)

```
git rev-parse HEAD
git log 05a7289961bafad79b041309d74913dff577ef1c..HEAD --oneline | wc -l
git status --porcelain -uall            # + --ignored=matching variant
git diff --name-only ; git diff --cached --name-only
git status --porcelain -uall -- corpus/fixtures/run_battery.py SCORECARD.md LOG.md SHONEN.md PROVINCE.md
git diff HEAD --name-only -- corpus/fixtures/run_battery.py SCORECARD.md LOG.md SHONEN.md PROVINCE.md
git reflog --date=iso -8 ; git stash list ; git branch --show-current
pgrep -f 'run_battery\.py'   # then readlink /proc/<pid>/cwd per pid
```

## Census (5 passes, all timestamps UTC)

| pass | when | status bytes | status lines | unstaged | staged | commits since base | fixtures new | r101 new | outside |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 16:22:01Z | 22 | 1 | 0 | 0 | 0 | 0 | (round dir) | 0 |
| 1 | 16:23:00Z | 2423 | 69 | 0 | 0 | 0 | 1 | 68 | 0 |
| 2 | 16:26:08Z | 8233 | 179 | 0 | 0 | 0 | 5 | 116 | 58 |
| 3 | 16:28:52Z | 11785 | 241 | 0 | 0 | 0 | 11 | 152 | 78 |
| 4 | 16:31:02Z | 11627 | 244 | 0 | 0 | 0 | 14 | 152 | 78 |
| 5 | 16:32:44Z | 14039 | 280 | 0 | 0 | 0 | 14 | 188 | 78 |

Line-count reconciliation (pass 5): 14 + 188 + 78 = 280 → every status line accounted for. Status line type at every pass: `??` only (untracked); no `M/A/D/R` tracked entries in any pass.

## Findings

### F1 — Commits: zero (PASS)
`git log 05a72899..HEAD --oneline | wc -l` → `0` at every pass (5/5). `git reflog --date=iso -8` top entry is `05a72899 HEAD@{2026-10-18 11:28:50 -0300}` (pre-round); no commit/rebase/reset op visible in-round. `git stash list` → 0. Branch `main`.

### F2 — Shared files: untouched (PASS)
`git status --porcelain -uall -- corpus/fixtures/run_battery.py SCORECARD.md LOG.md SHONEN.md PROVINCE.md` → empty (0 bytes) at every pass. `git diff HEAD --name-only -- <same set>` → 0 files (5/5). No new file named `run_battery.py` anywhere in status.

### F3 — Tracked modifications/deletions: none (PASS)
`git status --porcelain -uall | grep -vE '^(\?\?|!!)'` → `(none)` at every pass; `git diff --name-only` → 0 and `git diff --cached --name-only` → 0 (5/5). Every in-round change is an untracked new file.

### F4 — New files inside allowlist (PASS, path-scope)
`corpus/fixtures/` new (14 at pass 5): `export_prod.gd`, `export_prod_s01.gd` … `export_prod_s11.gd` (s01–s11), `r101_seqfull.gd`, `r101_ytrans.gd`.
`reports/round-101/` new: 64 top-level shards at pass 4 + `mutations/` subtree (88 files at pass 4; 188 total r101 files at pass 5). Transient scratch seen mid-round (`mutations/.scratch-crit3/`, `mutations/__pycache__/*.pyc` at pass 3) was gone by pass 4 — no residual flag.

### F5 — FLAG (deviation class): 78 untracked files outside allowlist
Present passes 2–5, under `corpus/live/` (not `corpus/live/runs/`, which is the README-sanctioned ignored scratch area). Likely verifier receipts/scratch, but per this seat's allowlist (`corpus/fixtures/` or `reports/round-101/` only) they are deviations; they will be swept by `git add -A` at round close unless cleaned or intentionally committed. Exact paths (pass-5 snapshot):

```
corpus/live/r101-ver11/armartifacts/empty.bin
corpus/live/r101-ver11/armartifacts/junk.bin
corpus/live/r101-ver11/armartifacts/not_a_pack.json
corpus/live/r101-ver11/armartifacts/prod_body_flip.pck
corpus/live/r101-ver11/armartifacts/prod_magic_tampered.pck
corpus/live/r101-ver11/exportmatrix.json
corpus/live/r101-ver11/killmatrix.json
corpus/live/r101-ver11/mut02run/empty_artifact.bin
corpus/live/r101-ver11/mut02run/junk_artifact.bin
corpus/live/r101-ver11/mut02run/proj/export_presets.cfg
corpus/live/r101-ver11/mut02run/proj/main.gd
corpus/live/r101-ver11/mut02run/proj/main.gd.uid
corpus/live/r101-ver11/mut02run/proj/main.tscn
corpus/live/r101-ver11/mut02run/proj/project.godot
corpus/live/r101-ver11/mut02run/proj_silent/export_presets.cfg
corpus/live/r101-ver11/mut02run/proj_silent/main.gd
corpus/live/r101-ver11/mut02run/proj_silent/main.tscn
corpus/live/r101-ver11/mut02run/proj_silent/project.godot
corpus/live/r101-ver11/pins.json
corpus/live/r101-ver11/receipts/exp_exe1.out
corpus/live/r101-ver11/receipts/exp_exe2.out
corpus/live/r101-ver11/receipts/exp_exe3.out
corpus/live/r101-ver11/receipts/exp_exe4.out
corpus/live/r101-ver11/receipts/exp_exe5.out
corpus/live/r101-ver11/receipts/exp_exe6.out
corpus/live/r101-ver11/receipts/exp_launch.out
corpus/live/r101-ver11/receipts/exp_pack1.out
corpus/live/r101-ver11/receipts/exp_pack2.out
corpus/live/r101-ver11/receipts/freshA_debug1.out
corpus/live/r101-ver11/receipts/freshA_debug2.out
corpus/live/r101-ver11/receipts/freshB_debug1.out
corpus/live/r101-ver11/receipts/freshC_rel1.out
corpus/live/r101-ver11/receipts/freshC_rel2.out
corpus/live/r101-ver11/receipts/manifest.txt
corpus/live/r101-ver11/receipts/manifest2.txt
corpus/live/r101-ver11/receipts/manifest3.txt
corpus/live/r101-ver11/receipts/manifest4.txt
corpus/live/r101-ver11/receipts/mut02_run.log
corpus/live/r101-ver11/receipts/offy_1000.err
corpus/live/r101-ver11/receipts/offy_1000.out
corpus/live/r101-ver11/receipts/offy_999999.err
corpus/live/r101-ver11/receipts/offy_999999.out
corpus/live/r101-ver11/receipts/offy_absent.err
corpus/live/r101-ver11/receipts/offy_absent.out
corpus/live/r101-ver11/receipts/offy_x1000.err
corpus/live/r101-ver11/receipts/offy_x1000.out
corpus/live/r101-ver11/receipts/seq_base_clean0.err
corpus/live/r101-ver11/receipts/seq_base_clean0.out
corpus/live/r101-ver11/receipts/seq_base_clean1.err
corpus/live/r101-ver11/receipts/seq_base_clean1.out
corpus/live/r101-ver11/receipts/seq_extra_pass_clean0.err
corpus/live/r101-ver11/receipts/seq_extra_pass_clean0.out
corpus/live/r101-ver11/receipts/seq_forged_clean0.err
corpus/live/r101-ver11/receipts/seq_forged_clean0.out
corpus/live/r101-ver11/receipts/seq_forged_clean1.err
corpus/live/r101-ver11/receipts/seq_forged_clean1.out
corpus/live/r101-ver11/receipts/seq_subst_clean1.err
corpus/live/r101-ver11/receipts/seq_subst_clean1.out
corpus/live/r101-ver17/receipts/ver17_chip_check.err
corpus/live/r101-ver17/receipts/ver17_chip_check.out
corpus/live/r101-ver17/receipts/ver17_cli_version.err
corpus/live/r101-ver17/receipts/ver17_cli_version.out
corpus/live/r101-ver17/receipts/ver17_date.out
corpus/live/r101-ver17/receipts/ver17_env_pins.json
corpus/live/r101-ver17/receipts/ver17_fnm_node.err
corpus/live/r101-ver17/receipts/ver17_fnm_node.out
corpus/live/r101-ver17/receipts/ver17_hostname.out
corpus/live/r101-ver17/receipts/ver17_node_version.err
corpus/live/r101-ver17/receipts/ver17_node_version.out
corpus/live/r101-ver17/receipts/ver17_probe.dummydriver.err
corpus/live/r101-ver17/receipts/ver17_probe.dummydriver.out
corpus/live/r101-ver17/receipts/ver17_probe.rep1.err
corpus/live/r101-ver17/receipts/ver17_probe.rep1.out
corpus/live/r101-ver17/receipts/ver17_probe.rep2.err
corpus/live/r101-ver17/receipts/ver17_probe.rep2.out
corpus/live/r101-ver17/receipts/ver17_python_version.err
corpus/live/r101-ver17/receipts/ver17_python_version.out
corpus/live/r101-ver17/receipts/ver17_uptime.out
```

Ignored (skipped by git add, no action needed): `corpus/live/r101-ver11/mut02run/proj/.godot/`, `corpus/live/r101-ver11/scratch/`, `corpus/live/r101-ver17/scratch/`, `corpus/live/runs/`. Note `corpus/live/.gitignore` covers only `runs*/`, `**/__pycache__/`, `**/.godot/` — so the F5 files above are **not** ignored.

### F6 — Lane-local `run_battery.py`: none observed (PASS, scan-limited)
At all 5 passes, `pgrep -f 'run_battery\.py'` hits were resolved via `/proc/<pid>/cwd`; count with cwd `…/game-dev-2d-shokunin` = 0. All hits were cwd `…/game-dev-3d-shokunin` (sibling lane, hands off; not inspected further).

### F7 — Observation: /tmp quota blip
At ~16:22:32Z a pass wrote `git status` output to `/tmp/r101-sent1/pass.status` and git printed verbatim: `fatal: write failure on standard output: Disk quota exceeded` (file left 0 bytes; the first pass counts were discarded, not reported as measurements). Subsequent streamed passes succeeded; `/tmp` tmpfs had 3.1–3.3G free / 63% inodes. Seats persisting evidence into `/tmp` should tolerate EDQUOT under 3D-lane load.

## Limits / inference labels

- Observation: all counts, timestamps, hashes above. Inference: F5 files are "likely verifier receipts" (naming only). Unknown: per-seat assignment catalogs (not available to this seat) — F4/F5 acceptance is strictly path-scope based.
- Point-in-time snapshots; last pass 16:32:44Z. Writers active after that are unobserved — the census may undercount late seats.
- This seat placed no files under `corpus/fixtures/`; own outputs: this shard only (plus scratch in `/tmp/r101-sent1/`, outside the repo).

## Re-run at round close (integration)

```
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
git rev-parse HEAD; git log 05a7289961bafad79b041309d74913dff577ef1c..HEAD --oneline
git status --porcelain -uall | grep -vE '^(\?\?|!!)'   # expect empty
git status --porcelain -uall -- corpus/fixtures/run_battery.py SCORECARD.md LOG.md SHONEN.md PROVINCE.md  # expect empty
```

## Addendum — pass 6 (post-write confirm), 2026-10-18T19:33:57Z

- HEAD `05a7289961bafad79b041309d74913dff577ef1c` unchanged; `git log <base>..HEAD --oneline` → 0; shared-file grep over status → empty; tracked-mod/deletion grep → `(none)`.
- `git status --porcelain -uall`: 13936 bytes / 283 lines = 14 `corpus/fixtures/` + 191 `reports/round-101/` (64 top-level + 105 `mutations/` + 22 `mutations/r101-simp3-evidence/`) + 78 F5 files.
- Delta vs pass 5: new allowlisted subtree `reports/round-101/mutations/r101-simp3-evidence/` (22 files); F5 set unchanged (58 `corpus/live/r101-ver11/` + 20 `corpus/live/r101-ver17/`).
- This shard is present as `?? reports/round-101/r101-sent1.md` (172 lines before this addendum); no other own files in repo.
