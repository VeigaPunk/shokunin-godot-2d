# r104-sent1 — X1 scope/identity sentinel (round-104, incl. worktree registry)

Plan (5 lines):
1. T0 baseline: HEAD, porcelain -uall, worktree registry, reflog, stash, refs/tags, protected-path mtimes.
2. Continuous re-sampler (porcelain+HEAD+diffs+registry per tick) -> /var/tmp/r104-X1/samples.log.
3. Classify every changed path: allowed = corpus/fixtures/res_uid*.gd + reports/round-104/**; all else flagged.
4. Worktree registry audit: named strays, dangling locked pins (wt-r98/r99/r100), prune --dry-run, /var/tmp/r104-* leftovers.
5. Identity pins (sha256) + final verdict + re-runnable close commands for the orchestrator.

Labels: [obs] observed / [inf] inferred / [unk] unknown. All times -03.

## T0 baseline (2026-10-18T22:29:52-03:00)

uptime [obs]: `22:29:52 up 1 day, 22:30, 1 user, load average 3.65 / 2.14 / 1.85`

- HEAD [obs] = `eff29d1dce70a7591603982ccf411af234430a9f` ("round-103 record: LOG + SCORECARD
  verdicts (work 752cdc32)"), branch `main`, commit date `2026-10-18 22:21:40 -0300`.
  Remote main per brief = `eff29d1d` — matches, so **round 104 starts from a pushed baseline**.
- Reflog top [obs] = `eff29d1d HEAD@{0}: rebase (finish): returning to refs/heads/main`;
  @{1}/{2} = the two r103 picks (afe5b636, d0aaeea5). No round-104 commit exists.
- Refs [obs]: `refs/heads/main eff29d1d`, `wt-r98 68bee6e7`, `wt-r99 fe1a996e`, `wt-r100 2d562282`;
  `git tag` = 0; `git stash list` = empty.
- `git diff --name-only` [obs] = 1 path (F1); `git diff --cached --name-only` = empty.
- porcelain `-uall` at T0 [obs] = **35 paths**: 34 × `?? reports/round-104/*.md` (allowed) + 1 flag (F1).
  The 39→50 path growth seen in the first sampler ticks is pure r104 shard landings.
- Protected-path mtimes at T0 [obs], all byte-identical to the round-103 close commit time
  (22:21:40) except SHONEN: `run_battery.py` 22:21:40.215, `SCORECARD.md`+`LOG.md` 22:21:40.244,
  `PROVINCE.md` 22:21:40.162, `SHONEN.md` 2026-10-13 16:40:45. `corpus/lessons` dir 22:21:40.
  `git status --porcelain -uall -- reports/round-101 reports/round-102 reports/round-103 corpus/lessons corpus/fixtures`
  = only F1. **No shared-file edit by any r104 seat so far** [obs].
- `git worktree prune --dry-run -v` [obs] = empty at T0.
- Deliverables at T0 [obs]: `corpus/fixtures/res_uid*` = none; `reports/round-104/mutations/` = empty dir.

## F1 — tracked pyc deletion in a protected tree (flag; already-committed artifact)

[obs] ` D reports/round-102/mutations/__pycache__/r102-S3-verify.cpython-314.pyc`
- The file **is tracked** (`git ls-files` lists it; `git cat-file -e HEAD:…` → IN_HEAD) — it was
  committed in `afe5b636` (the r103 work commit, `git log --diff-filter=A` names only that commit;
  `git show --stat afe5b636` shows `Bin 0 -> 22086 bytes`). r103-sent1 §F2 had recommended
  `rm -rf reports/round-102/mutations/__pycache__` at close; that was not done, instead the file
  entered history with the r103 commit.
- The worktree copy is now **absent**, so `git status` reports ` D` (unstaged deletion). Present in
  every sampler tick from 22:30:13 onward [obs]; `git diff` also reports it. Deletion is
  **uncommitted**, so HEAD still carries the 22086-byte blob.
- No r104 seat claims it; r104-ver8.md:13 independently notes it as "pre-existing, not mine" [obs].
- Orchestrator decision owed: `git rm --cached`/commit the deletion, or restore the file. Either
  way it is a **history-level** hygiene item, not a seat defect.

## F2 — NEW unignored pycache inside `reports/round-103/` (flag; created live during r104)

[obs] `?? reports/round-103/mutations/__pycache__/mut05_gate_evasion.cpython-314.pyc`
- First seen at sampler tick 22:30:43 (absent at tick 22:30:13). File mtime `22:30:39.533`,
  size 12612 B, sha256 `35ea900c6790e9fcab1b48cf3ecb15092abbf10b16dbf9d2e98f39c33fb7c01c`
  (dir mtime identical to the file's — single creation event).
- Bytecode of tracked `reports/round-103/mutations/mut05_gate_evasion.py`
  (sha256 `871556627f81803e66ea414a53a4de7ddf14b09f173e914942353756f11503aa`, 206 lines).
- Attribution [inf]: `reports/round-104/r104-mut4.md` is the **only** r104 shard citing
  `mut05_gate_evasion` (grep over `reports/round-104/*.md`), so the r104 mut4 seat imported/ran that
  r103 script and Python wrote the cache. (mut4's own shard does not mention pyc.)
- Hard-rule-2 class: `reports/round-101..103/` is a never-edit path; this is an **additive untracked**
  artifact inside it, not a modification of tracked content. `git check-ignore -v` → exit 1
  (NOT ignored) because `corpus/.gitignore`'s `**/__pycache__/` rule is scoped to `corpus/` only.
  [obs] `reports/round-103/mutations/__pycache__/` also exists from r103 (pre-existing, ignored? no —
  also unignored; it was simply not present in the T0 porcelain because `-uall` lists it only if it
  holds files; it is empty/new).
- **A second cache landed 22:31:08** [obs]: `r103-receipt-shape-gate.cpython-314.pyc`, 21627 B,
  sha256 `0aa357542938d1a0c00de66ef46cd4dc8ad411f0aa9f7f495f601a42ed379203`, from tracked
  `reports/round-103/mutations/r103-receipt-shape-gate.py` (sha256 `c713852b…`, 129 lines).
  The whole `reports/round-103/mutations/__pycache__/` dir was created 22:30:39 and grew to two
  entries by 22:31:08 — i.e. **r104 seats are importing r103 scripts into the r103 tree repeatedly**.
- **Third cache 22:32:43** [obs]: `r103-receipt-shape-adversary.cpython-314.pyc`, 8571 B, sha256
  `d806accb6f8f3991ba8ebbd33cdee9ce644939f6dd9d243773bb036e90b011a8`, from tracked
  `r103-receipt-shape-adversary.py` (sha256 `0200ae0f…`). Dir now holds **3** entries, all created
  during r104, all from r103 sources.
- Also [obs] `?? reports/round-104/mutations/__pycache__/mut05.cpython-314.pyc` (39564 B) — same class,
  inside the round's own mutations dir (less severe; still unignored).
- Disposition = orchestrator: `rm -rf reports/round-103/mutations/__pycache__ reports/round-104/mutations/__pycache__`
  at close; and/or add a repo-level `**/__pycache__/` ignore (currently only `corpus/.gitignore` has it,
  no root `.gitignore`). Note this is a **repeat of the r103 F2 class**, so the durable fix is the ignore rule.

## Worktree registry audit [obs]

Registry at T0 = 6 entries, at 22:31 = 6 entries:
| entry | target | state |
|---|---|---|
| main | `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` | branch `main` @eff29d1d |
| `game-dev-2d-shokunin-wt-r100` | `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r100` | **target dir MISSING**; locked "souji r5: pinned until game-dev-2d pushes wt branches or operator dispositions" |
| `game-dev-2d-shokunin-wt-r98` | `…-wt-r98` | **MISSING**; same lock text |
| `game-dev-2d-shokunin-wt-r99` | `…-wt-r99` | **MISSING**; same lock text |
| `repo` | `/var/tmp/r104-ver5/repo` | detached @eff29d1d, clean, live r104 ver5 seat |
| `wt` | `/var/tmp/r104-ver3/wt` | detached @eff29d1d, clean, live r104 ver3 seat |

- Dangling locked pins: the three `wt-r98/99/100` admin dirs carry `gitdir:` pointers to dirs that
  **do not exist** (verified per-entry); their branch refs do exist. `git worktree prune --dry-run -v`
  is **empty at every check** because prune refuses locked entries by design. Pre-existing from r103
  (r103-sent1 §4), **not created or changed by r104**. Disposition = operator/orchestrator
  (unlock+prune, or leave). Admin-dir mtimes are Oct 16 05:43–06:19 — untouched by r104 [obs].
- Only **2** r104 worktrees exist at T0 (ver3/ver5); both clean, both detached at the round baseline.
- `/var/tmp/r104-*` scratch: 46 dirs at 22:31, none of them holding a `.git` file other than the two
  registered above — i.e. **no unregistered worktree** among them [obs]. Two are large (ver3 995M,
  ver5 995M — full checkouts); all others ≤7 MB.
- **Churn is seat-managed [obs]:** sampler tick 22:32:14 shows `wt=5` — `/var/tmp/r104-ver3/wt` was
  removed by its own seat (dir gone, registry entry gone, prune still empty). At 22:32:45 `wt=6` again
  (a new seat added one). No X1 action; no stale registration left behind.
- No `git worktree repair`/`add` by X1; X1 created no worktree and holds no checkout (rule 5).

## F3 — tracked r103 file mtime rewritten, bytes unchanged (NOT a defect)

[obs] `reports/round-103/mutations/r103-receipt-shape-adversary.json` mtime = 22:31:08.799 (after round
start), yet `git status --porcelain -uall -- <path>` is **empty** and `sha256sum` == `git show HEAD:<path>`
== `b6c83306a7cce6e8e5e0d49641f67d1c9b38a4224bf0e23ef1cb4e49ecfccf59` (805 B both).
Interpretation [inf]: a seat opened the tracked JSON (read or truncate-then-rewrite identical bytes);
mtime alone would look like a protected-tree edit, so this is recorded to pre-empt a false positive.
Full mtime sweep `find reports/round-101 reports/round-102 reports/round-103 corpus/lessons corpus/fixtures
-newermt '2026-10-18 22:21:41' -type f` returns exactly 6 paths — 3 pycache entries (F2), this JSON (F3),
`corpus/fixtures/res_uid_w07.gd` (allowed, C1 deliverable), and `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`
(ignored; see F4). **No tracked protected file was content-modified.**

## F4 — pycache class is fixable by one ignore rule (positive control)

[obs] `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` (497431 B, 22:30:25) is the same
import-side effect as F2 but `git check-ignore -v` resolves it to `corpus/.gitignore:17:**/__pycache__/`,
so it never appears in `git status`. The F2/F5 leak exists **only** because no root `.gitignore` carries
that rule. [inf] One line in a repo-level `.gitignore` retires this whole defect class.

## F5 — round-104's own pycache (same class, lower severity)

[obs] `reports/round-104/mutations/__pycache__/` holds `mut01.cpython-314.pyc` (31997 B) and
`mut05.cpython-314.pyc` (41528 B). Python's embedded source records resolve the true origins:
`mut01` src_size 23824 / src_mtime 1792373549 (22:32:29) == `reports/round-104/mutations/mut01.py`;
`mut05` src_size 27467 / src_mtime 1792373568 (22:32:48) == `reports/round-104/mutations/mut05.py`.
So a naive basename search would mis-attribute them to r101 — the header check disambiguates [obs].
Inside the round's own tree, so allowed-adjacent; still unignored and worth the same one-line fix.

## C1 deliverable identity — `res_uid_w07.gd` (allowed path, moving target)

[obs] Sole fixture landed so far; **rewritten once during the audit**:
| time | size | sha256 |
|---|---|---|
| 22:30:59 | 9415 B | `0f620a3f5df189269cd975eb57088895d3d60acf666fd236d16191412cb8f38d` |
| 22:32:26 | 13258 B | `f1ec8f8ede3ad6752ecdf9a8e318811630c299d6c69aa237e4421d69e67d6174` |
Owner per its shard: KEY=W7, "Owns `corpus/fixtures/res_uid_w07.gd` ONLY". 21 scratch copies of
`res_uid*` exist across `/var/tmp/r104-*` (other seats' verification copies — expected). **Pin at
integration must use the final bytes**, not the 22:30 value any early seat may have quoted.
Ownership map from shard headers [obs]: E0→`res_uid.gd`, E1→`res_uid_s01.gd`, E2→`res_uid_s02.gd`,
E3→`res_uid_s03.gd`, E4→`res_uid_s04.gd`; those five are **still absent** from `corpus/fixtures/` at
22:33. Exactly one writer per fixture name; no name collisions observed.

## Rule-1 / rule-2 watch [obs]

- `ps -eo pid,etime,cmd | grep run_battery` = **none** at 22:31:00 and at every check.
- Live Godot processes at 22:31 all use scratch project paths:
  `--path /var/tmp/r104-E2/harness` (3), `/var/tmp/r104-M1/probe/proj` (4), `/var/tmp/r104-S2/scratch` (4),
  `/var/tmp/r104-S2/w07/proj_a` (2). No `--path` pointing into the lane repo.
- Sibling lane `game-dev-3d-shokunin` at `3ea02ff` (22:24:32, "r106 report-last…"); **X1 did not read,
  write, or touch it** beyond a single `git log -1` identity read. No fleet MANIFEST present.

## Contract amendment recorded [obs]

`/home/vgpnk/Projects/shokunin/.scratch/goal-20261018-game-dev-2d-training.md` §Amendments (lines 128-155)
matches the brief: p6/xai skipped → 12-position cycle, 36 total rounds numbered 101–136; p4 keeps
hyper with devin/deepseek-v4-1-flash-high fallback; p10 swap devin→hyper; p9 → openai-codex/gpt-6-luna-max.
r104 = amended p4; this seat runs on the devin fallback as directed.

## Re-runnable close commands (orchestrator)

```bash
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
git rev-parse HEAD; git log -1 --oneline
git status --porcelain -uall | grep -v 'reports/round-104/'
  # expect: ' D reports/round-102/mutations/__pycache__/r102-S3-verify.cpython-314.pyc'
  #         '?? reports/round-103/mutations/__pycache__/mut05_gate_evasion.cpython-314.pyc'  (+ any new)
git diff --name-only; git diff --cached --name-only; git stash list
git worktree list --porcelain; git worktree prune --dry-run -v      # prune must stay empty
git for-each-ref refs/heads refs/tags
ps -eo pid,cmd | grep run_battery | grep -v grep                   # must be empty
stat -c '%y %n' corpus/fixtures/run_battery.py SCORECARD.md LOG.md SHONEN.md PROVINCE.md
```

## C2a patch exclusivity — measured splice constraint (integration-critical)

Four gate patches were staged in `reports/round-104/mutations/`. Method: fresh scratch git repo
`/var/tmp/r104-X1/gr` holding a byte copy of the HEAD `run_battery.py`; each test = `git checkout -q --
corpus/fixtures/run_battery.py` then `git apply` in the stated order. No shared file touched.

| patch | bytes | sha256 (patch) | applies alone | post-apply sha16 of run_battery.py |
|---|---|---|---|---|
| `r104-V7-pass-prefix-tighten.patch` | 753 | `76f4dfaf…` | OK | `eb1b04864d88347a` |
| `r104-G1-tabpass.patch` | 1889 | `b7d014af…` | OK | `da1ef37fff98dba9` |
| `r104-crit2-passprefix-tighten.patch` | 1438 | `e82d620b…` | OK | `e760599e61ce6eb9` |
| `r104-R2-tabpass-census.patch` | 808 | `df9c0403…` | OK | `bc3423432e9e7a2e` |
| `r104-S0-evasion-probe.patch` | 11521 | `f92fb6cc…` | OK | (C3a, independent) |

- **All four C2a patches are pairwise mutually exclusive.** Measured pairs, every ordering fails on
  the second apply: V7+G1, G1+V7, V7+crit2, crit2+V7, G1+crit2, crit2+G1, R2+V7, R2+G1, R2+crit2.
  Cause [obs]: all four replace the same single source line
  `    pass_lines = [line for line in output if line.startswith("PASS ")]` at `run_battery.py:1904`
  (hunk `@@ -1901,7 +1901,± @@`); V7/G1 additionally insert into the regex block at `@@ -1854/1855` where G1 also collides.
- **`r104-S0-evasion-probe.patch` is orthogonal.** `S0+V7`, `S0+G1`, `S0+crit2`, `S0+R2` all apply;
  `ast.parse` OK on the result. S0 also applies after nothing else, and V7-then-S0 / S0-then-V7 both
  yield the identical post-sha `256f52e714df37bd` (order-independent) [obs].
- **Orchestrator must splice exactly one of the four C2a patches**, then S0. Picking two silently
  fails (`git apply` errors) rather than half-applying — verified by the reverse-order tests.
- Semantic differences to adjudicate (read from the patch bodies, [obs]):
  - V7 — census widened to `^\s*PASS\b`; no new flag reason (pure census).
  - G1 — census widened to `^[ \t]*PASS(?![A-Za-z0-9_-])` **plus** a new flag
    `pass_line_separator` for any non-canonical PASS line.
  - crit2 — flags `pass_prefix_noncanonical` but deliberately keeps the account/span/DIAG windows on
    canonical `PASS `.
  - R2 — census widened to `line.lstrip().startswith("PASS")` with no new flag reason.
- G1's shard (`r104-G1.md:91`) claims the post-apply sha `da1ef37fff98dba9…`; X1 independently
  reproduced exactly that value, so G1's verification receipt is honest [obs].

## F6 — r104 lessons files in a never-edit tree (orchestrator disposition)

[obs] **Three** new untracked files landed in `corpus/lessons/` during the round (all rewritten once
after first appearance — the first two were 11409 B / 15881 B at 22:34:56, final sizes below):
`r104-gate-boundary-tabpass.md` (12011 B, sha256 `4868594f0e3560d3ae4070e92a972f4ad52ba5574f8b400c4a582d8e50962e73`),
`r104-resource-loader-uid.md` (16493 B, sha256 `9518a30b5760c61b57929a98e330fbe2a0ad697dc43fb5864db01fa10e5e7a63`),
`r104-evasion-probe-and-disposition.md` (14577 B, sha256 `ca3e5e3ea20d83413ca87bd3e333a8d9731f4b5fc148544b18d32d2900cbffae`).
Same class as the three r103 lessons files (r103-sent1 §3): `corpus/lessons/*` is a hard-rule-2
never-edit path, but these are **additive and untracked** — `git diff --name-status HEAD` shows no
lesson modified, and the blob-identity sweep (`git hash-object` vs `git rev-parse HEAD:<path>`) returns
SAME for every tracked lesson. Orchestrator decides keep/relocate/remove; nothing is committed either way.

## C1 fixture inventory — final, at T_end (22:36)

| fixture | owner seat | size | sha256 (final) | earlier sha(s) observed |
|---|---|---|---|---|
| `corpus/fixtures/res_uid.gd` | E0 | — | `5d11b241becf864ce6ff890cc8439b4fc21ec31ea0adcd5893f75842f91ac374` | `469fdb12…` (15054 B @22:33) → `54fbff17…` (15253 B @22:34:59) |
| `corpus/fixtures/res_uid_s01.gd` | E1 | — | `d24bd3b21c53ce64caf17b9f3d59a140e25c123af30dad0630fc9b6488d0668b` | `e08ecdf9…` (12046 B @22:34:20) |
| `corpus/fixtures/res_uid_s02.gd` | E2 | — | `721c13fd532b294fbaf79d9c0920e133243f399ada46a29271a8a43165ae92da` | `ce863954…` (12624 B) → `d9cfd95a…` (13121 B @22:34:54) |
| `corpus/fixtures/res_uid_s03.gd` | E3 | — | `7d91a8e197acbce130eb22be92ce3240d33802263a513a7b9f35983e8516ca74` | none — first landed 22:35:44 |
| `corpus/fixtures/res_uid_s04.gd` | E4 | — | `803aa5acbba44da0b3d201da85a9f60811360e8c5bc33be3757aeda33f41ed52` | `f7b169e8…` (16770 B @22:33) → `803aa5ac…` (17445 B @22:34:40) |
| `corpus/fixtures/res_uid_w07.gd` | W7 | 13258 B | `f1ec8f8ede3ad6752ecdf9a8e318811630c299d6c69aa237e4421d69e67d6174` | `0f620a3f…` (9415 B @22:30:59) |

All six landed during the round (none at T0); every one is untracked, and each fixture name has exactly
one owner seat — no name collisions. **Five of the six were rewritten at least once** after first
appearance, so *every* sha a seat quoted before its last write is a stale pin: integration must hash
the files at the moment of the splice, not reuse a receipt. Sizes are deliberately omitted for the
five that kept changing; the sha is the identity of record. `run_battery.py` has **no** `res_uid`
CASES rows yet (`grep res_uid` = empty at 22:36), so the C1 rows are not registered — that
registration is the orchestrator's splice and must be re-hashed at that instant.

## FINAL VERDICT (as of 2026-10-18T22:35:20-03:00)

Host [obs]: `22:35:20 up 1 day, 22:35, 1 user, load average 12.18 / 7.90 / 4.35` (rise = 48-seat
swarm; X1 is passive). HEAD `eff29d1dce70a7591603982ccf411af234430a9f`, == `origin/main`
(remote `shokunin-godot-2d`), **zero commits during the round** — verified on all 11 sampler ticks
plus every manual check; reflog top still `eff29d1d HEAD@{0}: rebase (finish)`; tags 0; stash empty.

**Seat-scope verdict: PASS with 6 recorded items, none a seat defect.**
- **Zero shared-file edits by any seat** [obs]: `git diff --name-status HEAD` = exactly one entry
  (the r102 pyc deletion, F1); blob-identity sweep returns SAME for `run_battery.py`, `SCORECARD.md`,
  `LOG.md`, `SHONEN.md`, `PROVINCE.md` and **all** tracked files under `corpus/lessons/`.
- Every path created during the round is either inside the allowlist (`reports/round-104/**`,
  `corpus/fixtures/res_uid*.gd`) or one of the flagged classes F1/F2/F5 (pycache) and F6 (lessons).
- **Rule 1 held** [obs]: no `run_battery.py` process at any check; all observed Godot processes used
  `--path /var/tmp/r104-*` scratch projects only.
- **Rule 5 held** [obs]: registry went 6 → 5 → 6 as seats added/removed their own verification
  worktrees (`/var/tmp/r104-ver3/wt` removed by its owner at ~22:32, `/var/tmp/r104-ver5/repo` still
  live); `git worktree prune --dry-run -v` **empty at every check**; only 2 of 46 `/var/tmp/r104-*`
  dirs ever held a `.git` marker, both registered. X1 created no worktree, ran no battery, pinned no
  device-census token. X1's own scratch `/var/tmp/r104-X1/` (samples.log, chain/, gr/) is non-repo.
- Sibling lane `game-dev-3d-shokunin` untouched (single `git log -1` identity read only). No MANIFEST.

**Orchestrator action list (ordered):**
1. Pick **exactly one** of the four C2a patches (V7 / G1 / crit2 / R2 — mutually exclusive, table above),
   then apply `r104-S0-evasion-probe.patch`.
2. Register the C1 `res_uid_*` CASES rows (none present yet) and re-hash the fixtures at that instant —
   several were rewritten during the round.
3. `res_uid_s03.gd` (E3) is still absent; decide adopt-as-is or drop from the row set.
4. `rm -rf reports/round-103/mutations/__pycache__ reports/round-104/mutations/__pycache__`; add a
   root `.gitignore` with `**/__pycache__/` to retire the class (F4 shows the rule works).
5. Decide F1: commit the r102 pyc deletion (already staged as ` D`) or restore the file.
6. Decide F6: keep/relocate/remove the two untracked `corpus/lessons/r104-*.md`.
7. The three dangling **locked** worktree registrations `wt-r98/r99/r100` (target dirs missing, prune
   refuses locked) remain — unchanged since r103, operator disposition.

## Unknowns / limits

- Sampler window is bounded (40 × 30 s from 22:30:13); state between ticks and after the window is
  unobservable. `[unk]` for anything not directly checked.
- Writes outside the repo path (all `/var/tmp/r104-*` scratch) are invisible to `git status`; the
  worktree registry is the only cross-check and it is clean.
- F2's creator seat is inferred from shard citation, not from process evidence (the import ran
  ~22:30:39 and no `ps` snapshot covered that instant).
- The `/var/tmp` `EDQUOT` warning from the brief did **not** reproduce for X1: an 8 MiB write test and
  a 500-file test under `/var/tmp/r104-X1/` both succeeded; `df` shows 756 G free. Two `patch -p1`
  dry-runs failed with a spurious "Disk quota exceeded" while `git apply` in the same directory
  succeeded — recorded because a seat hitting that message may misread it as a real quota wall [obs].

## T_end re-pin (2026-10-18T22:36:11-03:00)

`uptime` = `22:36:11 up 1 day, 22:36, 1 user, load average 13.46 / 8.92 / 4.88`.
- HEAD = `eff29d1dce70a7591603982ccf411af234430a9f` (unchanged from T0); `git diff --name-status HEAD`
  = the single r102 pyc `D`; porcelain `-uall` = 170 paths; `git worktree prune --dry-run -v` empty;
  tags 0; stash empty.
- Protected-file sha256 (all unchanged since the r103 close commit, mtime 22:21:40):
  `run_battery.py` `2af2bc841ccb416e5fb0e1bbaadc08627e2d4768a8822f6956e867d905a3d0fe` (matches the
  sha every r104 seat quoted — so no seat worked from a drifted copy),
  `SCORECARD.md` `7b937146…`, `LOG.md` `44d4ab59…`, `SHONEN.md` `6a3d6216…`, `PROVINCE.md` `462f41fc…`.
- Untracked outside the allowlist at T_end, complete list: the r102 pyc `D`, three
  `corpus/lessons/r104-*.md`, three `reports/round-103/mutations/__pycache__/*.pyc`. Nothing else.
- Sampler: `/var/tmp/r104-X1/samples.log`, 11 ticks × 30 s (22:30:13–22:35:44) + manual checks.
  `HEAD=eff29d1d` on every tick; `wt` cycled 6→5→6→5→4 as seats added/removed their own worktrees;
  `FLAGS` grew only by the two classes above (pycache, lessons).
- X1 cleanup: no worktree was ever created by X1 (the `/var/tmp/r104-X1/gr` used for patch testing is a
  standalone `git init` copy, **not** registered — `git worktree list` never contained it, so there is
  nothing to `git worktree remove`). Scratch left in place under `/var/tmp/r104-X1/` as cited evidence.

## Addendum (22:36:28) — independent re-checks

- **Exclusivity re-verified from a pristine clone** (`/var/tmp/r104-X1/gr2`, fresh `git init` + commit
  of the HEAD `run_battery.py`): all **12 ordered pairs** of {V7, G1, crit2, R2} were tried; **zero**
  pairs applied. The four-way mutual exclusion is a property of the patches, not of leftover scratch
  state. [obs]
- **Self-cleaning observed**: `reports/round-103/mutations/__pycache__` fell 3 → 1 file and
  `reports/round-104/mutations/__pycache__` fell 6 → 3 between 22:35 and 22:36 — seats delete their own
  caches on completion. The class still warrants the root `.gitignore` rule (F4), since the residual
  entries are unignored.
- T_end untracked-outside-allowlist set = **6 paths**: the r102 pyc `D`, three `corpus/lessons/r104-*.md`,
  one `reports/round-103/mutations/__pycache__/*.pyc`. HEAD `eff29d1d`; `git diff --name-status HEAD`
  = the single `D`; prune dry-run empty; `uptime` load 13.42 / 9.14 / 5.02.

**Seat X1 closing state: PASS, no commits, no shared-file edits, no worktree left behind, no
`run_battery.py` execution, no device-census token pinned.**

Shard self-pin is **not** recorded inside this file (any edit to write it changes the hash — circular).
The authoritative close pin is carried in X1's final handoff message to the orchestrator; verify the
on-disk copy with `sha256sum reports/round-104/r104-sent1.md`.

## Post-close observation — integration apply (orchestrator, expected; NOT a seat defect)

The 40-tick sampler (completed 22:50:15) kept running past X1's close and captured the integration
phase. Recorded here because it is the direct adjudication of X1's C2a exclusivity finding.

- **22:49:16** [obs] — first tick showing ` M corpus/fixtures/run_battery.py`; the prior tick (22:48:46)
  was clean. HEAD stayed `eff29d1d` on all 40 ticks (no commit during the sampler window).
- **The orchestrator spliced `r104-G1-tabpass.patch`.** [obs] Signature grep on the landed file:
  `RECEIPT_PASS_LINE_RE` present (2 occurrences), while `_PASS_RE` (V7), `pass_prefix_noncanonical`
  (crit2) and `line.lstrip().startswith("PASS")` (R2) are all **0**. So **exactly one** of the four
  mutually-exclusive C2a patches was applied — the constraint in §"C2a patch exclusivity" was honored.
  The landed sha16 `0e62eeb7a60e74c5` differs from G1's solo post-apply `da1ef37fff98dba9` because the
  S0 probe and the CASES registration were spliced in the same batch [inf].
- **C1 registration done.** [obs] `CASES` now holds **581 entries, 581 unique** (was 552 at r103 close),
  of which **29 are `res_uid*`** — the E0/E1/E2/E3/E4/W7 fixture rows are registered. `r104_*` = 0.
  `git diff --stat -- corpus/fixtures/run_battery.py` = **+308/−2**.
- **S0 probe landed.** [obs] `probe_receipt_shape_gate` present at `:6049` and wired into
  `receipt_shape_audit(results)` at `:6048`; the replay-probe comment block at `:2116-2125` and the
  `receipt_shape_flag` call sites at `:2264`/`:2282` are in place.
- **Battery run 1 launched** [obs]: process `python corpus/fixtures/run_battery.py --probe-failing
  --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution
  --probe-crash-exit --probe-timeout`, stdout → `/var/tmp/r104-batt-r1.log`, run dir
  `corpus/live/runs/20261019T015020674559Z/`. This is **the orchestrator's** invocation (rule 1
  applies to seats; X1 ran none). Also observed at 22:49:46 a second in-place edit to `run_battery.py`
  via `py_compile` guard asserting `CASES: 581 (expect 581 = 552+29)`.
- Path count grew 188 → 189 as the modification landed; the untracked set stayed at the 6 flagged
  paths + 29-new-CASES effect. **No shared-file edit by any seat is implied by any of this** — these
  changes are the orchestrator's integration apply, matching the C1/C2/C3 claim set.

*Coverage note: the sampler window (22:30:13–22:50:15, 40 ticks) is the authoritative continuous
record for X1; the ticks after 22:36:11 fall outside X1's seat-scope close but are reported because
they directly satisfy X1's own deliverable check — that the exclusivity constraint held at splice time.*

### Fixture drift continued through integration (T_last 22:50, mtime order)

Five of six fixtures were rewritten **again** after X1's 22:36 table — confirming (not contradicting)
the stale-pin warning. Final on-disk state at T_last, with the 22:36 value for comparison:

| fixture | mtime | sha256 at T_last | X1's 22:36 value |
|---|---|---|---|
| `res_uid.gd` | 22:44 | `75da874740b5ee333e6749e34bfe44946b2ba2cd5aa4a2d489f4477f408d21de` | `5d11b241…` |
| `res_uid_s01.gd` | 22:37 | `fdef4f3cf945531a916be3c247e1f471ae69f4c32ac6abaeefe077e7124756bc` | `d24bd3b2…` |
| `res_uid_s02.gd` | 22:37 | `551ecb76f0b9397c6f2ead8ec7d3e1ec00db95971ec6aa757d0b8c2b1bac37f9` | `721c13fd…` |
| `res_uid_s03.gd` | 22:39 | `7a5d29d0c284ca484706d5886f7a996149004a61f907e0014006e44b4c30a14a` | `7d91a8e1…` |
| `res_uid_s04.gd` | 22:36 | `7e3c637fe2a47c1a58ac45cb2ac91530acd417ffdea56d5895fa082d25a5ad70` | `803aa5ac…` |
| `res_uid_w07.gd` | 22:32 | `f1ec8f8ede3ad6752ecdf9a8e318811630c299d6c69aa237e4421d69e67d6174` | unchanged |

`res_uid_w07.gd` (W7) is the **only** fixture that never changed after 22:32:26 — its pin is stable.
The other five each moved 2–3 times during the round. **A CASES row pinned against an early sha will
fail its span check at battery time** — this is exactly the `export_div` CASES-pin repair pattern seen
at r103. The orchestrator's own `py_compile` guard at 22:49:46 asserted only the CASE *count* (581),
not the fixture *bytes*, so a byte-level re-pin against these five is still owed.

### Battery run 1 at T_last (22:50:20)

`/var/tmp/r104-batt-r1.log` = 34 lines, 34 `^PASS`, **0 `^FAIL`**, still running; no `verdicts.json`
written yet under `corpus/live/runs/20261019T015020674559Z/`. Not adjudicated here — the orchestrator
owns the verdict.
