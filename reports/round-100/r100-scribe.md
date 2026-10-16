# r100 scribe — custody audit of the r100 landing `2dcbb6f6`

Seat `SCRIBE` (g2d lane r100, custody gate) | host **devin** | lane repo
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` | **audited commit
`2dcbb6f6ed491e51aa76237b96f80c0b38fe607f`** (the r100 landing named in the
dispatch; `main` HEAD and tracked-clean when this audit opened) | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`) | Python
3.14.7 | audit window 2026-10-16T09:2x–09:5xZ.

> **HEAD advanced during the audit.** `2dcbb6f6` was HEAD when this audit
> opened (09:26:27Z) **and still HEAD when the archive checkout was cut**
> (09:39:4xZ — proven by that checkout's battery hash `86a1aef8…`). By 09:48Z
> HEAD had moved to `619ad7e0` via `9ede7c50` "r97-r100 integration fix: dedupe
> crash sentinel CASES rows (509/509 unique)" (committer date 09:34:32Z) and
> `619ad7e0` "pyc refresh: src_size 507480 matches deduped source (r100-reviewer
> F4)" (committer date 09:46:26Z); the battery at current HEAD is
> `35233c8b2edbd45c5a6f37fb3293613017657b8ab4a96ff94bb4967bf081c35c`
> (509 tuples / 509 unique / 0 dups). **All runs and hashes below measure the
> audited commit's bytes** (`corpus/fixtures/run_battery.py` =
> `86a1aef86b36f70758a47bacd323879e9f76aa5a101bdb4b60e0a176fdeadc90`), which
> both runs had already loaded before the successors appeared. The successor
> commits are **not** covered by this audit; `9ede7c50` independently
> corroborates and repairs F2 (§3).

**Verdict: `BROKEN`** — the landing's *custody chain from receipt to committed
bytes* is broken (F1–F3): the commit message and the author report carry a
green that was measured on a **different battery file** (`43ce922e…`, 444
CASES) than the one committed (`86a1aef8…`, 512 CASES), and the landing diff
is not insertion-only. Everything the author *actually measured* is internally
consistent and hash-verified (C1–C8): fixtures, row content, receipts,
census, isolated re-runs. The findings are custody/landing defects, not
fabrication.

**Behavior on the committed bytes is green** — measured here, not inherited:
my rep2 run (§4.2) executes the committed battery end-to-end and returns
`verdict=PASS`, 519/519 rows, `rc=0`, with all 25 r100 rows and all 50
`probe_error_clause_surface` discriminations (including
`r100_expected_errors_all_matched`) true. So the custody gap is *evidence
coverage*, not a behavioral regression: the landed bytes had never been
measured as landed until this audit.

**`lsp` disclosure.** No `lsp` device in this session; no symbol work was
required (audit + one report write).

**The host is shared and heavily loaded** (§6): ≥8 sibling battery runs were
live during this audit; loadavg 9.8–12.7 on 32 cores; 43 `godot` processes at
peak; 30 G RAM with 16 G/34 G swap in use. "Quiet" never applies below.

---

## 1. What was audited, and how

| # | check | command (lane repo root unless noted) |
|---|---|---|
| 1 | landing identity | `git log --oneline -5`, `git rev-parse HEAD`, `git status --porcelain --untracked-files=no` |
| 2 | landing diff | `git diff --numstat 254e79dd 2dcbb6f6`, `git diff -U0 … -- corpus/fixtures/run_battery.py` |
| 3 | fixture hashes | `git show 2dcbb6f6:corpus/fixtures/r100*.gd \| sha256sum` vs report/manifest/live probes |
| 4 | CASES inventory | `ast.parse` of `corpus/fixtures/run_battery.py` at `2dcbb6f6`, `254e79dd`, `89f85ed8`, and the author worktree file |
| 5 | row-set diff | name→(script, flags, exit, signature) dicts, committed vs worktree |
| 6 | receipts | `corpus/live/r100-author/{rows.json,manifest.sha256,runs/**}` (author worktree), `sha256sum -c` |
| 7 | classifier identity | `ast.unparse(classify_process)` — `make_rows.py` vs `run_battery.py` |
| 8 | my battery run rep1 | `python3 corpus/fixtures/run_battery.py --runs corpus/live/r100-scribe/runs` on the committed HEAD |
| 9 | my battery run rep2 | `git archive HEAD corpus/fixtures \| tar -x -C /tmp/r100-scribe-archive` then the same battery from that checkout |

Tools I wrote for the audit (read-only, untracked): `corpus/live/r100-scribe/
audit_receipts.py`, `corpus/live/r100-scribe/analyze_run.py`.

## 2. Confirmed (INTACT) — claims that hold

- **C1 — fixtures are exact byte-copies of the frozen probes.** All four
  committed fixtures hash to the report's §1 table, the receipts manifest, and
  the frozen live probes:
  `r100_gui.gd dd826f6e…` (= `corpus/live/r100-scout/proj/r100_gui.gd`),
  `r100b_phase.gd 49298e6c…`, `r100b_emul.gd 31087e78…`, `r100b_seq.gd
  4718a19e…` (= `corpus/live/r100-boundary/probes/…`); line counts 780/520/37/790.
- **C2 — the 25 r100 rows survive the landing byte-identically.** Committed and
  measured files agree on all 25 `(script, flags, expected_exit, signature)`
  tuples, and the 58-line r100 comment header is identical.
- **C3 — allowlist + floor gate are present and live.** Committed file carries
  the 3 `expected_errors` entries (lines 2222–2228) and
  `r100_expected_errors_all_matched` (line 4010); the receipts' census shows
  `matched_lines=[1]`, `dead_in_run=False`, `bare_classification_rejects=True`
  for all three cases in all three runs.
- **C4 — receipts are internally consistent and match the report.** `rep1`
  451/451 PASS, `rep2` 449/451 (`negative_transition` +
  `probe_error_clause_surface`, `dead_entry_count=2` = that row's own two
  entries, only `census_bare_classifier_consistent` false), `rep3` 451/451
  PASS; **r100 25/25 PASS in all three**; every r100 signature equals the pin
  and equals the other two runs and the smoke receipt for the same case (0
  mismatches).
- **C5 — smoke harness is what it claims.** `rows.json` = 25 rows, every row
  `uniq_sha=1`, `stable=true`, 3 accepts; `runs/smoke/` = 225 files = 25 arms
  × 3 reps × {out, err, rc}.
- **C6 — manifest verifies.** `sha256sum -c` on the 6 recorded artifacts: 6 OK.
- **C7 — isolated re-run of the pre-existing flake row.** 3/3 carry
  `PASS invalid_destination_rejected=true current_scene_preserved=true
  old_scene_alive=true frames=3` at `rc=1` (stderr carries the row's two
  allowlisted diagnostics — see F7).
- **C8 — report bytes are stable.** Committed `reports/round-100/r100-author.md`
  == worktree file == manifest hash `9f617b46…`.

## 3. Findings

### F1 — `BROKEN` (high): the measured battery is not the committed battery

| file | sha256 | CASES tuples | distinct names |
|---|---|---|---|
| committed `2dcbb6f6:corpus/fixtures/run_battery.py` | `86a1aef86b36f70758a47bacd323879e9f76aa5a101bdb4b60e0a176fdeadc90` | **512** (block lines 18–1651) | 509 |
| measured (worktree `wt-r100` = `2d562282`, manifest, receipts) | `43ce922e2e26419e5ee6f35223e11ba10e86e95a46223c342f87d27dc09732fb` | **444** (18–1345) | 444 |

The author's three `verdicts.json` runs contain **451 rows = 444 CASES + 7
meta probes** — i.e. the reported `green 451/451 x2` is the 444-tuple file.
The committed file runs **512 CASES + 7 = 519** rows. 65 case names exist only
in the committed file: `stree_lattice_*` ×12 (r97), `r98_*` ×15, `r98b_*` ×16,
`r98c_*` ×1, `r99_*` ×18, `r99b_*` ×3. The measured file is a strict subset:
every shared name has identical tuple content.

Consequence: **no receipt in `corpus/live/r100-author/` measures the committed
bytes.** The commit subject `(25 rows, +132/-0), green 451/451 x2` and the
report's §5 evidence describe `43ce922e…`; the landing commit is `86a1aef8…`.
My rep1/rep2 runs (§4) are the measurement of the committed bytes.

### F2 — `BROKEN` (high): the landing diff is not insertion-only; it duplicates two CASES rows

`git diff --numstat 254e79dd 2dcbb6f6 -- corpus/fixtures/run_battery.py` →
`134 2` (**134 insertions, 2 deletions**), against the report's §1/§4 and the
commit subject's `+132/-0`.

The r100 block was spliced *into* the pre-existing mashed crash-tail line, so
the two tuples were re-emitted on either side of it (committed lines 1535 and
1643–1644):

- `crash_spontaneous_sigabrt` ×**3** (parent `254e79dd`: ×2)
- `crash_self_sigkill` ×**2** (parent: ×1)

so the committed battery executes 512 case rows instead of 510 (observed in my
rep1: `crash_spontaneous_sigabrt:` 3×, `crash_self_sigkill:` 2×). The author's
own file has neither duplicate (`apply_insert.py`'s byte-restore post-condition
does hold on its base — recomputed: worktree vs `89f85ed8` = **+132/−0**), so
this is a landing defect. No gate keys on row multiplicity and the crash meta
is a name-keyed dict (last wins), so nothing failed because of it — it is a
real, unmetered deviation from the report's "final four CASES tuples are
untouched / insertion-only" statement.

**Independently corroborated and repaired while this audit ran.** Successor
commit `9ede7c50` (09:34:32Z, subject "r97-r100 integration fix: dedupe crash
sentinel CASES rows (509/509 unique)", body: *"Union-merge splice artifact
flagged by r98-critic F1: crash_spontaneous_sigabrt appeared x3 and
crash_self_sigkill x2 after serial union landings. Semantically inert (same row
run twice) but broke CASES uniqueness and row-count arithmetic."*) removes
exactly these two glued tuples: `git diff 2dcbb6f6 9ede7c50` = 3 insertions /
2 deletions on the battery, and the file at `619ad7e0` is 509 tuples / 509
unique / 0 dups (verified by AST). My runs measured the pre-repair bytes; the
deduped file `35233c8b…` was **not** run by me.

### F3 — report numbers describe the worktree base, not the landing base (medium)

- §1/§4 `+132 / −0` and "Insertion-only proof … 132 insertions(+), 0 deletions":
  true against `89f85ed8` (recomputed +132/−0), **false against the landing
  parent `254e79dd`** (+134/−2).
- §4 "CASES 419 → 444": true (r96 `89f85ed8` = 419, all distinct); the landing
  parent `254e79dd` = 485 (484 distinct).
- §1/§4 "444 CASES names, 444 distinct": true for the measured file; the
  committed file has **509 distinct of 512**.
- The report nowhere states which base its `git diff` numbers are relative to.

### F4 — report custody header is stale at audit time (medium, conflict reported verbatim)

Report header: *"Worktree `~/Projects/shokunin/game-dev-2d-shokunin-wt-r100`,
branch `wt-r100`, HEAD `89f85ed8` (r96 author merge) — **nothing committed,
nothing staged**."*
Observed: `wt-r100` HEAD = **`2d562282`** "r100 author: GUI/input lattice 25
rows (+132/-0), green 451/451 x2" (parent `89f85ed8`), tree clean apart from
untracked `corpus/live/r100-author/`; that commit contains exactly the report's
6 files. Whether the commit postdates the report is not resolvable from this
seat — reported for the judge. Related: §6 lists receipts as
`corpus/live/r100-author/**`, which exist **only in the worktree** (the lane
repo has no `r100-author` directory; its `corpus/live/` carries scout/boundary
and older seats).

### F5 — tracked `.pyc` provenance claim does not describe the landing (minor)

§8: the `.pyc` "is restored to HEAD bytes after the final run". True for the
worktree commit (`2d562282:…pyc` == `89f85ed8:…pyc`, sha `13319b13…`). The
landing commit carries a **new** pyc (`43b1a6de…`, 457028 B) whose embedded
source size is **507894** = the committed battery's byte length (parent pyc:
489915 = parent source length). The landed artifact is self-consistent, but it
is a fresh compile, not the byte-restore the report describes.

### F6 — citation line number is wrong (minor)

§5.1 "the production clause copied verbatim from `run_battery.py:1310`":
`def classify_process` is at **1418** in the measured file and **1725** in the
committed file (line 1310 is a row in both). The substantive claim is
**verified**: `make_rows.py:77 classify_process` is AST-identical
(`ast.unparse` equality) to the battery's.

### F7 — §5.3 "0 `ERROR:` lines" is true only of stdout (minor, wording)

`runs/isolated-negative_transition/rep{1,2,3}.out` carry 0 `ERROR:` lines, but
each `.err` carries the row's **two allowlisted diagnostics** (`ERROR: Can't
change to a null scene…`, `ERROR: negative control: deliberately invalid scene
destination rejected`) — the lines that keep that row's allowlist live. The
load-sensitivity conclusion holds; the wording invites a false reading.

## 4. Gates: my own battery runs on the committed bytes

Both runs use the committed `run_battery.py` (`86a1aef8…`), Godot
`4.7.2.stable.arch_linux.ed1daf0bf`, `--headless`, serial (one Godot child at
a time), run dirs under `corpus/live/r100-scribe/`.

### 4.1 rep1 — lane repo HEAD (`2dcbb6f6`), launched 09:26:27Z

Command: `python3 corpus/fixtures/run_battery.py --runs
corpus/live/r100-scribe/runs`.

- **512/512 CASES rows PASS, 0 FAIL** — including **25/25 r100 rows** (14
  `r100_gui_*` + 11 `r100b_*`), every signature equal to its committed pin
  (0 mismatches), **65/65** r97/r98/r99 rows, and the duplicated crash rows
  (3× / 2×).
- **3/7 meta probes PASS** (independent save-process probe, spontaneous crash
  classification meta, descendant pipe-EOF meta).
- The process was **gone at 09:34:32Z** (last output byte), during the 4th meta
  probe (`descendant signature-spoof`). `battery-committed-rep1.err` is 0 bytes,
  **no `verdicts.json` was written**, and no final `PASS/FAIL battery:` line
  exists. Cause undetermined from this seat (no OOM line visible via `dmesg`;
  the host was running ≥8 sibling batteries — §6).
- **This is not a battery verdict.** The last four metas (descendant
  signature-spoof, while-live signature-gate, descendant error-spoof,
  error-clause surface) measured **nothing** in rep1 and are not claimed.

### 4.2 rep2 — fresh `git archive` checkout under /tmp, launched 09:39:45Z

Command: `git archive HEAD corpus/fixtures | tar -x -C /tmp/r100-scribe-archive`
(cut while HEAD was still `2dcbb6f6`) then `python3
corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
/tmp/r100-scribe-archive/corpus/live/runs` from that checkout; archive battery
sha256 = `86a1aef8…` (identical to committed).

> **Archive scope caveat.** A whole-tree `git archive HEAD` was attempted first
> and aborted on the 16 G `/tmp` tmpfs quota: the archive carries tracked
> `corpus/live` evidence history (53 G of the 55 G working tree). The checkout
> used is therefore `corpus/fixtures/` at HEAD only (2.4 M) — which is exactly
> what the battery stages (`HERE.iterdir()`), plus an explicit `--runs`.

**Result: `verdict=PASS` — 519/519 rows, `rc=0`, completed 09:48:40Z.**

| field | value |
|---|---|
| run dir | `/tmp/r100-scribe-archive/corpus/live/runs/20261016T093944931255Z` |
| rows | **519** = 512 CASES + 7 meta probes (plus the final `PASS battery:` line) |
| fails | **0** |
| final verdict | `PASS` (`verdicts.json.verdict`) |
| rc | `0` (`battery-archive-rep2.rc`) |
| r100 rows | **25/25 PASS**, every signature == committed pin == worktree pin == all three author runs (0 mismatches) |
| duplicate rows executed | `crash_spontaneous_sigabrt` 3×, `crash_self_sigkill` 2× (F2) |
| meta probes | 7/7 PASS |
| census | `rows_with_expected_errors=80`, `dead_entry_count=0`, all three r100 allowlist entries `matched_lines=[1]`, `dead_in_run=False` |
| discriminations | all 50 true, incl. `r100_expected_errors_all_matched: true`, `census_covers_all_allowlisted_rows: true`, `prior_meta_rows_stable_29_discriminations: true` |

`rows_with_expected_errors` is 80 here vs 74 in the author's 444-row file — the
+6 are the r97/r98/r99 rows the author's file never contained (F1).

Cross-run stability of the 25 r100 signatures now spans **four independent
batteries** (author rep1/rep2/rep3 on `43ce922e…` + my rep2 on `86a1aef8…`),
two files, and two checkout trees: 0 mismatches.

## 5. Conflicts reported verbatim (for the canonical judge)

1. Commit subject `2dcbb6f6`: `"r100 author: GUI/input routing lattice (25 rows, +132/-0), green 451/451 x2"` vs `git diff --numstat 254e79dd 2dcbb6f6 -- corpus/fixtures/run_battery.py` → `134 2`, and receipts measuring a 444-tuple file (`43ce922e…`) while the commit carries 512 tuples (`86a1aef8…`).
2. Report §1 table: ``corpus/fixtures/run_battery.py | tracked, `+132 / −0` `` vs the landing diff `+134/−2`.
3. Report §4: "**Insertion-only proof:** `git diff --stat corpus/fixtures/run_battery.py` → `132 insertions(+)`, `0 deletions`" vs `134 insertions(+), 2 deletions(-)` against the landing parent (the 132/0 figure reproduces only against `89f85ed8`).
4. Report header: "HEAD `89f85ed8` … **nothing committed, nothing staged**" vs `wt-r100` HEAD `2d562282` (a commit containing the report's 6 files) at audit time.
5. Report §8: `.pyc` "restored to HEAD bytes after the final run" vs the landed pyc `43b1a6de…` compiled from the committed 512-tuple source (worktree pyc `13319b13…` == `89f85ed8` pyc).
6. Report §5.1: "`run_battery.py:1310`" vs `def classify_process` at 1418 (measured) / 1725 (committed).
7. Report §5.3: "0 `ERROR:` lines" vs the isolated `.err` files carrying the row's two allowlisted ERROR lines.

## 6. Load / host caveats (honest measurement conditions)

- Shared host `plazir27`, 32 cores; loadavg **9.76** at rep1 start, **11.9–12.7** during it, **10.7–12.5** during rep2; 30 G RAM with **16 G/34 G swap used**.
- ≥8 concurrent sibling battery runs observed during the audit (`r100-simplifier`, `r97-reviewer`, `r99-simplifier`, `r100-critic`, `/var/tmp/r100-verify`, `/var/tmp/r98sim/{head,tree}-folded`, g3d `r100-author` `full_run4`), 43 `godot` processes at peak.
- Rows measured here are **contended** measurements. rep1's mid-meta termination is consistent with host pressure but its cause is not proven; rep2's completion state is reported as measured.
- **Timestamp note, explicitly unproven:** rep1's last output byte and the successor commit `9ede7c50`'s *committer date* are both 09:34:32Z, yet HEAD was still `2dcbb6f6` when the archive was cut minutes later — so the commit date is not evidence of when the ref moved. No mechanism is claimed from this seat; rep1's stderr is empty and no `verdicts.json` was written.
- No row is called green that measured nothing: rep1's 4 unmeasured metas are listed as unmeasured.

## 7. Not verified by this seat (scope limits)

- **The labrat dispatch** (§7, "agent `374d001d`", "5/6 hypotheses CONFIRMED,
  H2 NOT-VISIBLE"): no access to that transcript from this seat — contract-only
  evidence, reported as such, not upgraded.
- **Mechanism/physics claims** (boundary verdicts: flush-gated cursor write,
  `|Σ relative| > 10` drag law, single-cell-per-process): re-read only as text
  against `reports/round-100/r100-boundary.md` (rows 3/6/18 of its verdict
  table) — consistent with §2's encoding. Not re-adjudicated, not re-measured
  except through the pinned rows themselves.
- **The author's smoke scratch internals** beyond the receipts
  (`make_rows.py`'s staging): only the classifier identity (F6/C-checks) and
  the receipt set were verified; the scratch replicas were not re-run.
- **r97/r98/r99 rows** are reported only as "all PASS in my rep1" — their
  custody is not this round's subject.

## 8. Artifact paths

- Report (this file, **untracked, not committed**):
  `reports/round-100/r100-scribe.md`
  (self-hash intentionally omitted: any later edit invalidates it — hash at
  commit time; the orchestrator commits)
- My receipts (untracked, gitignored space):
  - `corpus/live/r100-scribe/battery-committed-rep1.{out,err}` — 515 row lines, 0 FAIL
  - `corpus/live/r100-scribe/runs/20261016T092627437631Z/` — scratch + `save-process-verdicts.json` (**no** `verdicts.json`; run terminated mid-meta)
  - `corpus/live/r100-scribe/battery-archive-rep2.{out,err,rc}` — 520 row lines, `rc=0`
  - `corpus/live/r100-scribe/archive-rep2-verdicts.json`, `archive-rep2-save-process-verdicts.json` — durable copies of rep2's verdicts (originals in `/tmp/r100-scribe-archive/corpus/live/runs/20261016T093944931255Z/`)
  - `corpus/live/r100-scribe/audit_receipts.py`, `analyze_run.py` — audit tools
- Author receipts audited (worktree, untracked): `game-dev-2d-shokunin-wt-r100/corpus/live/r100-author/**`
- Author landing commit: `2d562282` on branch `wt-r100` (parent `89f85ed8`)
- Lane landing commit (audited): `2dcbb6f6ed491e51aa76237b96f80c0b38fe607f` (parent `254e79dd`)
- Successor commits landed during the audit (not covered by these runs): `9ede7c50` (dedupe, 3/2 on the battery), `619ad7e0` (pyc refresh) — current HEAD, battery `35233c8b…`
