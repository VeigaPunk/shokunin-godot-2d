# r101-scout — SCOUT seat (round 101)

Task: census `corpus/fixtures/`; stale dead-path census; r101 name-collision check;
extract battery receipt conventions from READING `corpus/fixtures/run_battery.py`.
Method: read-only greps + AST parse of `run_battery.py` (never executed). No patrol
of files outside ownership; no shared-file edits; no `run_battery.py` runs (rule 1).

## 0. Host / load context (recorded once)

- Base commit: `05a72899 gitignore: stop re-tracking round-local freeze/scratch materializations`
  (`git log --oneline -1`); branch main; `git status --porcelain corpus/fixtures` → empty
  (no untracked fixture files from concurrent seats at census time).
- `uptime` at 16:21:08 → `load average: 33.42, 19.05, 12.84`; at 16:22:58 → `54.69, 31.13, 17.90`; 32 cores (`nproc`).
  Expected: sibling 3D lane swarm running heavy.
- `/tmp` HAZARD (observed, all seats should read): mount is `tmpfs (rw,nosuid,nodev,nr_inodes=1048576,inode64,huge=advise,usrquota)`,
  16G size, 13G used, 3.1G avail (`df -h /tmp`), 63% inodes used. Two transient
  `EDQUOT` failures observed at 16:22 (a 11-byte `printf > /tmp/r101-scout/...` left a
  0-byte file; an `awk` redirect aborted with `print to "standard output" failed: Disk quota exceeded`).
  Seconds later `dd bs=1024 count=1` + `printf` to `/tmp/r101-scout/` both succeeded.
  Observation: intermittent EDQUOT bursts under the concurrent swarm. Inference (unverified):
  `usrquota` near its limit; free-block count alone is not the binding constraint.
  Guidance: retry scratch writes on EDQUOT; do not treat one failure as fatal.
- Toolchain: `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`.
  `~/.local/share/godot/export_templates/4.7.2.stable/linux_release.x86_64` present,
  73,519,416 bytes, mode 755 (`ls -la`). Relevant to C1.

## 1. Corpus census — `corpus/fixtures/`

- Total: **103 tracked files** (`find corpus/fixtures -type f | wc -l` = 103;
  `git ls-files corpus/fixtures | wc -l` = 103 — no untracked additions).
  The briefing's "82 files" does not match today's tree; closest near-miss is the
  .gd count (81). Report as stale briefing figure, not a defect.
- TIMED ADDENDUM (16:23): sibling seat E17-YTRANS (C3) landed
  `corpus/fixtures/r101_ytrans.gd` at 16:22 (11,464 B, untracked; `git status
  --porcelain corpus/fixtures` → `?? corpus/fixtures/r101_ytrans.gd`). On-disk
  total is now 104 (103 tracked + 1 untracked). `run_battery.py` itself is
  UNMODIFIED (`git diff --stat` empty) — that fixture has no registered CASES row
  yet; integration must register it per §4.2 routing.
- Extensions: 81 `.gd`, 11 `.tscn`, 4 `.py`, 4 `.lua`, 2 `.godot`, 1 `.cfg`.
- Layout: 78 top-level files + 4 subdirs / 25 files:
  - `controls/` 19 files (input-route, overlap, transition, signal, pickup testbed)
  - `level_collision/` 2, `love_probe/` 2, `love_phys_probe/` 2
- Notable: `run_battery.py` (508,301 B, 5,341 lines), `export_presets.cfg`,
  `project.godot`, `love_battery.py` (114,909 B), `pygame_battery.py`, `pygame_probe.py`,
  round fixtures `r87_edge.gd … r100b_seq.gd`, `r97_scene_a/b.tscn`, `r88_spawnable.tscn`.

## 2. Stale dead-path citations — routed defect

Dead path searched verbatim: `.shokunin/game-dev-2d/corpus/`.
Counts (per-file `grep -rc`; occurrence totals `grep -rho | wc -l`):

| Scope | Matching files | Occurrences | Lines |
|---|---|---|---|
| `SCORECARD.md` | 1 | **3** | lines 8, 9, 10 |
| `README.md` | 0 | 0 | — |
| `corpus/lessons/` | **100** | **736** | many |
| `corpus/fixtures/` (all types incl. .gd headers, .py, .lua, .tscn) | 0 | 0 | — |

- SCORECARD.md lines 8–10 are the LIVE depth/coverage/calibration command rows; each
  cites `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing ...`
  (copied by a reader this command fails). Fix belongs to the orchestrator
  (SCORECARD.md is serialized, hard rule 2) — correct form in this repo is
  `python corpus/fixtures/run_battery.py ...`.
- `corpus/lessons/` occurrence histogram by filename role: verifier 50, author 15,
  headless 5, detail 3, adverse 3, verifier2 2, warning/verification/retry/regression 1 each
  (files=100, occurrences=736). These are historical receipts; rewriting history is a
  policy call for the orchestrator (flag, do not silently rewrite).
- Adjacent, outside the four named scopes (report only, no fix assumed):
  `PROVINCE.md` line 6 — 1 occurrence, false present-tense claim
  "corpus fixtures under .shokunin/game-dev-2d/corpus/"; `LOG.md` 45 occurrences
  (historical log, arguably correct as history); `SHONEN.md` 0; `corpus/README.md` 0.
- Also zero: any `\.shokunin/game-dev-2d` reference (without `/corpus/`) inside
  `corpus/fixtures/` (`grep -rl` → NONE).

## 3. r101 name-collision check (assigned: `export_prod*.gd`, `r101_*.gd`)

- At census time 16:21: `find . -name 'r101_*' -o -name 'export_prod*'` (excluding .git)
  → **NONE**; `ls corpus/fixtures/ | grep -E 'export_prod|r101_'` → CLEAN.
- CASES case-name scan (AST): 0 rows whose name starts with `r101` or `export_prod`.
- Recheck at 16:23: exactly ONE r101-pattern file now exists —
  `corpus/fixtures/r101_ytrans.gd`, created at 16:22 by sibling seat E17-YTRANS (C3),
  not by this seat and not colliding with any other observed claim. No `export_prod*`
  file exists. No duplicate basenames observed. So the C1/C2 seats' assigned names
  (`export_prod*.gd` and the remaining `r101_*.gd` names) were free at both checks;
  seats must still pick distinct basenames among themselves and re-verify at write time.
- `run_battery.py` unmodified at 16:23 — no r101 CASES row is registered yet; the new
  fixture will auto-stage (§4.6) once a row is registered.
- `reports/round-101/` exists untracked with ~53 sibling shards; `reports/round-101/mutations/`
  contains other seats' `mut01.py`, `mut05.py`, `crit6_floor_gate_coverage.py` + `__pycache__`.
  My only owned output is this shard. Assigned r101 names are free — no collision.

## 4. Battery receipt conventions (from READING `run_battery.py` source)

### 4.1 CASES row shape and registration
- `CASES = [` at line 18, closing `]` at line 1652. **509 rows, 509 unique names, 0 duplicates**
  (verified by AST parse of the module — parse only, never executed). No separate registry file:
  rows ARE the registration; files auto-stage (see 4.6).
- Row = 5-tuple `(name:str, script:str, flags:list[str], expected_exit:int, evidence)`
  - `script` is relative to scratch: `"r100b_phase.gd"`, `"controls/mechanic_test.gd"`.
  - `evidence`: a `str` = exact PASS-line substring; a `tuple/list` = mode-envelope, PASS iff
    ANY whitelisted payload appears (lines 2270-2276).
  - Special markers handled inside `execute()`: `__godot_export__`, `__godot_export_missing__`,
    `__save_process_writer__/reader__/missing__` (lines 1843-1860).
  - Signal deaths use negative exits: `-6` SIGABRT, `-9` SIGKILL, `-11` (crash rows lines 1644-1645).
- **Insertion position convention (binding)**: new rows go BEFORE the crash/descendant tail —
  i.e. ahead of `("crash_spontaneous_sigabrt"` (line 1644) — because
  `descendant_pipe_detached_control` (line 1645) must remain adjacent to the meta probes inside
  its `sleep 8` lifetime. Evidence: comments at lines 99-102, 157, 225, 270, 399, 443; the r79 and
  r100 blocks were inserted exactly there (lines 1594-1643 end just before 1644).

### 4.2 expected_errors (allowlist) — semantics
- Separate dict `{case_name: (error_substring, ...)}.get(name, ())` at lines ~1971-2231.
  NOT part of the CASES tuple. Applied only when the row reaches the classifier path
  (`passed is None`, i.e. non-`__` scripts).
- Match rule per entry (`allowed_error`, lines 1727-1737): exact stripped-line equality; OR
  entry ends with `,` → line startswith entry and line has exactly one `ERROR:`; OR the
  structured `"ERROR: chain incomplete"` shape (startswith + `scene=SceneB:<Node#` +
  `old_alive=false` + exactly one `ERROR:`).
- `classify_process` (lines 1725-1742): PASS iff `code == expected_exit AND error is None
  AND signature in output AND no unrelated ERROR: line AND "SCRIPT ERROR:" not in output
  AND "Parse Error:" not in output`. ANY ERROR: line not matched by an allowlist entry → FAIL.
- `required_stderr` dict (lines ~2244-2268): fragments that must each appear on stderr alone,
  plus row signature anchored to stdout alone (merged-blob blindness pair).
- Floor gates (lines 3859-4027): per-round `rN_expected_errors_all_matched` =
  `all(not e["dead_in_run"] for r in census_rows if r["case"].startswith(prefixes))`;
  the dead-entry census (lines 3663-3745) records per entry: shape
  (`exact`/`comma_prefix`/`structured`), `matched_lines`, `first_match`, `dead_in_run`.
- `cases_integrity` (lines 4022-4027): `len({c[0] for c in CASES}) == len(CASES)` AND per-prefix
  non-empty existence over `("stree_lattice_", "r98_canvas_", "r98b_", "r98c_",
  "r99_audio_", "r99b_", "r100_gui_", "r100b_")`.
- **r101 routing**: if r101 rows land, the orchestrator must (a) insert rows before line 1644,
  (b) add the r101 prefix(es) to the `cases_integrity` tuple, (c) add an
  `r101_expected_errors_all_matched` clause iff r101 rows carry allowlist entries,
  (d) put allowlists in the named dict — never in the CASES tuple.

### 4.3 Receipt row (record) shape — what a row lands in `verdicts.json`
`{"case", "script", "flags", "command", "xdg_data_home", "expected_exit", "actual_exit",
"signature", "verdict", "error", "output" (list[str], merged stdout+stderr), "expected_errors",
"required_stderr", ["export_artifact" for export rows]}` (lines 2291-2299).
Export worksheets: `export_artifact = {artifact_bytes, artifact_sha256, products_created,
artifacts_deleted}` (line 1903); export evidence is OVERRIDDEN at runtime to
`EXPORT PASS preset=Linux/X11 executable_bytes={size}` (line 1876) even though the CASES row at
line 58 reads `...executable=nonempty`.
Top-level payload: `{godot, seed, scratch, probe_failing, results, verdict}` written to
`<runs>/<UTCstamp>/verdicts.json`; exit 0 iff all verdicts PASS (`--runs` default
`corpus/live/runs`). Console line per row: `{verdict} {name}: exit={code} signature={evidence!r}`.

### 4.4 Launch shape / timings / streams
- Normal row: `[godot, "--headless", "--path", scratch, "--script", "res://"+script, "--", *flags]`;
  timeout **8s**; streams captured SEPARATELY (`run_process_streams`, lines 1709-1723) then
  concatenated for merged classify; `error` field = TIMEOUT/launch-error string.
- Export rows: `[godot, "--headless", "--path", project, "--export-debug", "Linux/X11", "<out>/fixture.x86_64"]`;
  timeout **60s**; `out/` must start EMPTY (assert) and is asserted empty again after the missing-preset
  row; products are sha256'd + size-recorded then deleted.

### 4.5 Static preset/context a fixture may rely on
`export_presets.cfg`: `preset.0` name `Linux/X11`, platform `Linux/X11`, `runnable=true`,
`export_filter="all_resources"`, `include_filter=""`, `exclude_filter=""`,
`binary_format/architecture="x86_64"`. C1's include/exclude-filter rows need their own
modified preset in scratch (current one has empty filters). `project.godot` name
`MechanicOneShotTest`, features `PackedStringArray("4.7")`; the runner renames config/name with
a UTC stamp for user:// isolation.

### 4.6 Scratch staging
`main()` copies every top-level item of `corpus/fixtures/` except `run_battery.py` and dotfiles
into `<runs>/<stamp>/scratch/` (`.godot` state rebuilt per run); copies
`controls/pickup.tscn` to scratch root; `save_roundtrip`/`__save_process_*` rows get
`XDG_DATA_HOME=<runs>/<stamp>/xdg-data`. Consequence: **new fixture files auto-stage — only
CASES rows need registering**.

### 4.7 Naming conventions observed (for r101 row authors)
Round-prefixed names by round: `rNN` / `rNNb_` / `rNNc_` with per-arm suffixes
(`r100b_phase_<arm>`). Prefix histogram top: phys2d 79, r96b 47, r95b 35, camera 25,
input 24, r93 23, slider 22, r94 19, geo2d 18, r99 18, dss 17, r98b 16.
Fixture header style (e.g. `r100b_seq.gd` lines 1-6): `extends SceneTree`, one comment block
with the exact launch command, PASS-line shape, and the no-ids/timestamps rule
("No object ids / RIDs / timestamps").

## 5. Unresolved / for orchestrator
- SCORECARD.md lines 8-10 stale commands (fix is orchestrator-serialized).
- corpus/lessons/ 736 citations: history-rewrite policy decision.
- PROVINCE.md line 6 false present-tense claim (1×).
- /tmp transient EDQUOT hazard — seats retry; flagged here per load-context duty.
- All facts above are observations from exact commands at 16:21-16:23 on 2026-10-18 unless
  labeled inference.
