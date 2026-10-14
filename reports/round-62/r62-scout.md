# Round 62 scout report — run_battery.py process/timeout machinery + descendant-pipe row insertion map (host: devin)

Recon only; no tracked edits. Scope kept: this report + `corpus/live/r62-scout/`
(scratch). Runner under study: `corpus/fixtures/run_battery.py`, worktree ==
HEAD `08d80dc` == r61 work commit `b95d180` blob, sha256
`d705bca719fcdf24009f2302866ecf8066d49baa2adbc81dbd044c77b3bc5019`, 1012 lines.
(`git status`: only `?? corpus/live/r62-baseline/` — a live sibling; tracked
tree clean.) The r61 boundary's `3bb29044…` was a *mid-flight pre-correction*
hash — the committed blob differs because `crash_meta_ok` gained the
marker-presence clause during integration; verifier-facing extraction hashes
below are on the committed bytes.

**Bottom line:** the pipe-EOF misattribution mechanism is exactly where the r61
boundary report placed it, reproduced fresh on the current runner (§3). The
pinning move needs **one new fixture, 2–3 CASES rows, and one unconditional meta
row**; a sentinel-classified CASES row (Design A) or a meta-spawned arm (Design
B) both keep the prior 92 rows field-stable. A *plain* CASES row for the
pipe-hold arm is impossible — proof in §4.

**Provenance note — mid-flight sibling diff.** Between my hash check and report
time the r62 author seat landed the move: worktree runner is now sha
`0c4c9bee70569c8ec29f98dea89c437d78587fd5c3c7b3220b76140ac59520dd` (1154 lines,
`git diff` = **+142/−0**: 1 CASES row + ~141-line meta block), plus new fixture
`corpus/fixtures/descendant_pipe_probe.gd` (sha256
`795cb67dcd2010a02c4b7bfeb8ff06faade84ef84410341131e3020a25968049`,
untracked), measured **94/94 PASS** at
`corpus/live/r62-author/runs/20261013T234730112013Z/verdicts.json` (sha256
`f4f65b1a…`). All §1/§5
line numbers below are on the **pre-edit** runner `d705bca7…` (1012 lines) —
the map describes what was staged. ast-extraction on the post-edit file:
`run_process` `88728b23…` and `classify_process` `749fa060…` are **byte-identical**
— additive-only outside those functions, so §1–§4 characterize both revisions.
Observed-vs-spec detail in §8.

## 1. Mechanism map — `corpus/fixtures/run_battery.py`

### run_process (the whole timeout path) — lines 142–151

```
142  def run_process(command, timeout_seconds, env=None):
143      try:
144          proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, env=env)
145          return proc.stdout + proc.stderr, proc.returncode, None
146      except subprocess.TimeoutExpired as exc:
147          output = (exc.stdout or b"").decode(...) if isinstance(exc.stdout, bytes) else (exc.stdout or "")
148          output += (exc.stderr or b"").decode(...) if isinstance(exc.stderr, bytes) else (exc.stderr or "")
149          return output, None, f"TIMEOUT after {timeout_seconds} seconds"
150      except OSError as exc:
151          return str(exc), None, f"launch error: {exc}"
```

- **Capture**: `capture_output=True, text=True` (line 144) → `Popen` gets
  `stdout=PIPE, stderr=PIPE`; both pipe fds are inherited by the Godot child as
  fds 1/2 and by any `OS.create_process` descendant forked from it (proven §3).
- **Where the bound is enforced**: inside CPython, not this file.
  `subprocess.run` → `Popen.communicate(timeout=…)`; on POSIX 3.14.7
  `communicate` returns only when the child exits **and** both capture pipes
  reach EOF (descendant-held write ends keep EOF pending past the child's
  death — the deadline is shared). Verified via `inspect.getsource(subprocess.run)`
  on this host this session: on `TimeoutExpired` it runs `process.kill()` then
  `process.wait()` (POSIX arm — *no* second `communicate` drain) and re-raises.
  `Popen.kill()` → `send_signal(SIGKILL)` → `os.kill(self.pid, SIGKILL)`:
  **direct child pid only**.
- **Timeout classification written into verdicts**: handler :146–149 returns
  `(partial_output, None, "TIMEOUT after {timeout_seconds} seconds")` — the
  partial output (including any descendant bytes already in the pipe) rides the
  `TimeoutExpired` exception; `code=None`, `error` set.
- **No process-group machinery anywhere**: grep over the whole file finds no
  `start_new_session`, `process_group`, `os.killpg`, `setsid`, `terminate()`.
  The only kill calls are `Popen.kill()` at :858/:871/:881 (crash-exit probe)
  and :947/:954 (timeout probe) plus the implicit one inside `subprocess.run` —
  all direct-child-only. Descendants orphan under `systemd --user` (ppid 1573
  on this host, confirmed fresh §3).

### classify_process — lines 153–170

`code == expected_exit and error is None and signature in output and not
unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in
output`. `unrelated_errors` (:167–168) = any merged-output line containing
`ERROR:` not matched by `allowed_error` (:155–165: exact match, trailing-`,`
prefix match requiring exactly one `ERROR:` in the line, special
`chain incomplete` shape). A `code=None`+`error="TIMEOUT…"` result **always**
classifies False under every `expected_exit` — the misattribution is recorded
as `actual_exit: null`, `error: "TIMEOUT after N seconds"`, verdict FAIL.

### execute() — command assembly, bounds, classification — lines 270–452

- Script sentinels: `__godot_export__`/`__godot_export_missing__` build export
  commands at :271–283; `__save_process_*__` builds a godot `--script
  res://save_process.gd` command with per-mode flags at :284–288; everything
  else falls to the default `godot --headless --path <scratch> --script
  res://<script> -- <flags>` at :289–290.
- **Per-case bound**: `timeout_seconds = 60 if script.startswith("__godot_export") else 8`
  at :291 — CASES rows get **8s**; a sentinel name can fold a custom bound into
  this same expression (additive) or the branch can set it before :298.
- env: `XDG_DATA_HOME` run-local redirect at :292–297 (save cases only).
- `run_process` call: :298.
- `passed` computation: export branches set `passed` directly at :300–340
  (`__godot_export__` :300–334, `__godot_export_missing__` :335–340),
  `else: passed = None` :356–357 → falls into the `if passed is None` block
  (:392–440): `expected_errors` dict :393–437, `}.get(name, ())` :438,
  classifier pick :439, `passed = detected if mutate else classifier(...)` :440.
  SCRIPT/Parse veto :442–443. Record :444–448 (`case, script, flags, command,
  xdg_data_home, expected_exit, actual_exit, signature, verdict, error, output`
  — **no `elapsed_seconds` on CASES rows**; fault rows :228–231 and
  `bounded_run` rows :924–963 do carry it). append :451, print :452.

### Iteration, meta blocks, verdict gate

- Only CASES iteration site: `for case in CASES: execute(*case)` :454–455.
- Unconditional meta rows (inspect `results` records, zero extra Godot runs):
  `probe_save_independent_process` :456–507 (append :505–506);
  `probe_spontaneous_crash_classification` :508–547 (comment :508–510, records
  gather :513–514, `reclassify_crash` :516–519, four discriminations :521–532,
  `crash_meta_ok` :533–538, append :539–546, print :547). **Insertion point for
  a new unconditional meta row: after line 547, before `if
  args.probe_failing:` at :548.**
- Opt-in blocks: `--probe-failing` mutants :548–555; `--probe-export-launch`
  :556–647 (own `subprocess.run` :598 with inline TimeoutExpired :600–603);
  `--probe-godot-error` :649–703; `--probe-stream-attribution` :705–794
  (`run_process_streams` :706–715); `--probe-crash-exit` :796–911 (`Popen` +
  `send_signal(SIGTERM)` :823–889); `--probe-timeout` :913–1001 (`bounded_run`
  :921–968: `Popen` :932, `communicate(timeout=bound)` :935, TimeoutExpired
  :938, `process.kill()` :947, second `communicate` :948 — same
  direct-child-only shape).
- New opt-in argparse flag would go at :103–111 (rejected — see §6).
- Fixture auto-staging: :119–125 copies every non-dotfile item of
  `corpus/fixtures/` except `run_battery.py` into `run_dir/scratch` — a new
  `.gd` fixture needs **zero wiring**.
- Battery verdict gate: `"PASS" if all(r["verdict"] == "PASS" for r in results)`
  :1005 — one FAIL record fails the whole battery.

## 2. Current row accounting (field-stability surface)

Canonical seven-flag command → **92 rows**: 79 CASES (lines 19–97), 2 mutants,
11 probe/meta (4 `probe_unrelated_error_*` :318/:347/:381×2,
`probe_save_independent_process` :505, `probe_spontaneous_crash_classification`
:539, `probe_export_launch` :643, `probe_godot_error` :700,
`probe_stream_attribution` :788, `probe_crash_exit` :908, `probe_timeout`
:998). Sibling r62-baseline replayed the frozen HEAD archive on this host:
**92/92 PASS**, 0 mismatches vs `corpus/lessons/r61-crash-non-author.json` on
the 7-field tuple (`script, flags, expected_exit, actual_exit, signature,
verdict, error`) — `reports/round-62/r62-baseline.md`, receipt
`corpus/live/r62-baseline/runs/20261013T233453788036Z/verdicts.json`.

## 3. Fresh r62-scout re-derivation (this report's scratch evidence)

`corpus/live/r62-scout/drive_r62.py` `ast.get_source_segment`-extracts
`run_process` + `classify_process` **verbatim** from the tracked runner and
execs them (production code path, not a reimplementation). Extraction hashes on
the committed runner: `run_process` `88728b2303f64fc48b094d358f0a217ae7b07aaf85b446b014e35c31d76207c5`;
`classify_process` `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`
— the latter **byte-identical** to the r60-verifier/r61-scout recorded
extraction, i.e. the classifier is unchanged since r60.

Fixture `corpus/live/r62-scout/proj/tree_timeout_probe.gd`: prints
`TREE_TIMEOUT_PROBE: expected signature` + `godot_pid=` + `spawned_pid=`;
`--spawn-hold` spawns `sh -c 'sleep 1; echo TREE_DESC_AFTER_PARENT_WRITE; sleep 4'`
(inherits pipes, holds ~5s); `--spawn-detach` spawns `sh -c 'exec sh -c "sleep 4"
</dev/null >/dev/null 2>&1'` (fds detached, still outlives); default arm = no
descendant. Bound 3.0s (matches the tracked `--probe-timeout` bound).

Receipt `r62-scout-tree-verdicts.json` (sha256 `8d81586b…`), raw captures
`raw/tree-{clean,hold,detach}.stdout`:

| arm | elapsed | actual_exit | error | classify(expected 0) | desc line | godot alive at return | desc alive at return (ppid) |
|---|---|---|---|---|---|---|---|
| clean | 0.662s | 0 | None | **True** | — | False | — |
| hold | **3.002s** | **None** | `TIMEOUT after 3.0 seconds` | **False** | **`TREE_DESC_AFTER_PARENT_WRITE` present** | **False** | **True** (1573 = systemd) |
| detach | 0.550s | 0 | None | **True** | — | False | **True** (1573) |

- hold arm: `raw/tree-hold.stdout` contains
  `TREE_TIMEOUT_PROBE godot_pid=795243` / `spawned_pid=795493` /
  `TREE_DESC_AFTER_PARENT_WRITE` — a line the descendant (795493) wrote ~1s
  after the direct child (795243) was already dead (`godot_alive_at_return=false`,
  `os.kill(pid,0)`), into the *child's captured stdout*. `run_process` still
  reported `TIMEOUT` at 3.002s — pipe-EOF wait misattributed to child liveness,
  reproduced verbatim on the current runner. No `ERROR:` lines in the capture.
- detach arm: identical outliving descendant (alive at return, same orphan
  ppid 1573) yet clean True in 0.550s — the classification hinges purely on
  pipe-fd inheritance, not descendant lifetime. Same silent leak, opposite
  verdict (r61 boundary's consequence (b) confirmed again).
- Note on `exc.stdout`/`exc.stderr`: subprocess.run's TimeoutExpired carries
  both pipes' partial output; the descendant line lands in the merged
  `output` of the record — the in-band witness the meta row can pin.

## 4. Why a plain CASES row cannot pin the hold arm

Battery verdict requires every record `verdict == "PASS"` (:1005). Under
`classify_process` (:153–170) a pipe-hold run returns `code=None` and
`error="TIMEOUT after …"` — `code == expected_exit` fails for any int and
`error is None` fails — so a CASES row holding pipes past the bound can only
ever record FAIL. The tracked pin therefore needs **either** a custom
classification on the row (sentinel + `passed` override — precedent:
`__godot_export__`/`__godot_export_missing__` set `passed` directly at
:300–340, bypassing `classify_process`) **or** the hold arm spawned by the meta
block itself (subprocesses inside the runner outside CASES: fault block
:215–233, opt-in probes; meta blocks so far only *inspect* — an unconditional
meta spawning one Godot run is novel but additive).

## 5. Insertion map (spec)

**Fixture — new file** `corpus/fixtures/tree_timeout_probe.gd` (name free).
Auto-staged into run scratch by the :119–125 copy loop; resolves as
`res://tree_timeout_probe.gd` at :290; flags arrive via `-- <flags>` at :290
and read via `OS.get_cmdline_user_args()`. Minimal arm set: `--spawn-hold`,
`--spawn-detach`, default clean. Required in-band witnesses: signature marker
line, `godot_pid=`/`spawned_pid=` lines, and a descendant
`TREE_DESC_AFTER_PARENT_WRITE`-style line written *after* the child's exit
(this is the only in-band proof the EOF wait came from an inherited fd — a
descendant line alone doesn't order vs. parent death, so keep a ≥ ~1s delay
after spawn before the write, with the child exiting at ~0.4–0.7s). Precedent:
r61 `spontaneous_crash_probe.gd` promoted from scratch; my scratch fixture
`corpus/live/r62-scout/proj/tree_timeout_probe.gd` is directly promotable —
it's the r61 boundary fixture stripped of out-dir file writes (not needed for
the in-band pin).

**CASES rows — append between line 97 (`crash_self_sigkill`) and `]` at :98.**

- `("tree_timeout_detach", "tree_timeout_probe.gd", ["--spawn-detach"], 0, "TREE_TIMEOUT_PROBE: expected signature")` — clean PASS row (measured 0.550s); discriminating control: real descendant spawned (`spawned_pid=` in output), outlives child, yet child-exit-bound classification because it released the pipes.
- `("tree_timeout_clean", "tree_timeout_probe.gd", [], 0, "TREE_TIMEOUT_PROBE: expected signature")` — optional no-descendant same-fixture control.
- The hold arm as a CASES row needs the sentinel treatment (Design A) — below.

**expected_errors (:393–438)** — no entry needed: hold/detach/clean outputs
carry no `ERROR:` lines (verified in raw captures); `.get(name, ())` :438
defaults to `()`.

**Design A — sentinel row** (mirrors `__save_process_*__` at :284–288 and the
export `passed` overrides at :300–340):

1. CASES row `("tree_timeout_hold", "__tree_timeout_hold__", [], <expected>, <signature>)`.
   `expected_exit` carries the child's true exit (0) for documentation while
   `actual_exit` records `null`; or `None` — tuples are untyped, executor's call.
2. `elif script == "__tree_timeout_hold__":` beside :284–288 building the godot
   command with `--spawn-hold`.
3. Bound: :291 gives 8s → fixture's descendant must hold pipes **> 8s** (every
   battery run pays ~8s). A custom bound is a one-line additive tweak at :291
   (e.g. `3.0`, matching the proven `--probe-timeout` bound; descendant then
   needs > ~3s). Zero-runner-change path = keep 8s and hold ~12s.
4. `elif script == "__tree_timeout_hold__":` before `else: passed = None`
   :356–357 setting `passed = (code is None and isinstance(error, str) and
   error.startswith("TIMEOUT after") and signature in output and
   "TREE_DESC_AFTER_PARENT_WRITE" in output)` — the row PASSes exactly when the
   misattribution shape is observed.

**Design B — meta-spawned hold arm** (most literal "CASES/meta rows",
smallest diff): CASES rows are only the detach (+clean) controls; the
unconditional meta block itself runs `run_process(<hold command>, 3.0)` (the
nested helper is in scope) and records the TIMEOUT shape in its own payload.
Costs +1 Godot spawn and ~bound-seconds per battery run; the misattribution is
then not a CASES record. Precedent for runner-side subprocesses outside CASES
exists (fault block :215–233) though unconditional meta blocks haven't spawned
before.

**Meta row — append after :547, before `if args.probe_failing:` :548** (both
designs), e.g. `probe_tree_timeout_pipe_eof`:

- Gather records by case name (precedent :456–468 and :513–514).
- Assert hold evidence: `actual_exit is None`, `error` == `f"TIMEOUT after
  {bound} seconds"`, marker + descendant line in `output` — all present in my
  fresh capture.
- Assert controls: detach (and clean) records `verdict == "PASS"`,
  `actual_exit == 0`, `spawned_pid=(\d+)` present (precedent `pid=` regex :460)
  — pins "descendant existed yet classification was child-exit-bound".
- Zero-cost re-classification discriminations via `classify_process` on the
  captured outputs (crash-meta precedent :516–532): hold output under
  `expected=0` → must be False (the misattribution itself);
  `classify_process(0, None, hold_output, 0, MARKER)` → **True** (proves the
  FAIL came solely from `code=None`+`error`, not output content); detach
  output under a wrong `expected_exit` → False.
- `bounded_claim` should state: exit-shape/pipe-EOF classification only;
  orphan leak exists in both arms and is **not detected** by the battery;
  descendant liveness at meta-eval time is racy — keep any `os.kill(pid,0)`
  evidence informational, never gated.

**Design C — opt-in flag (rejected)**: new argparse flag :103–111 + block
mirroring :913–1001 changes the canonical seven-flag command (and every
downstream replay), contradicting "CASES/meta rows".

## 6. Field-stability constraints for the executor

- All edits additive: CASES appends before :98, optional `elif`s at :284–291 /
  :356, meta block before :548, new fixture file. `run_process`,
  `classify_process`, `execute` core, all 92 prior rows untouched → the
  verifier's `ast`-extraction-hash technique applies directly (baseline hashes
  in §3).
- Descendant hold duration must exceed the effective bound (8s CASES default
  at :291 vs ~5s under a 3.0s bound) or the pipe hits EOF before the deadline
  and the arm classifies clean — the r61 boundary hold arm (7s hold vs 3.0s
  bound) and mine (5s vs 3.0s) both satisfy it; a >8s hold under the CASES
  default is unverified but mechanism-identical.
- CASES records carry no `elapsed_seconds` (:444–448) — pin the bound via the
  exact `error` string (`"TIMEOUT after 8 seconds"` int vs `"TIMEOUT after 3.0
  seconds"` float — the f-string at :149 renders the bound literally).
- Meta rows run unconditionally: any Godot spawn inside one adds to *every*
  battery invocation (~0.5s + hold-bound). Design A's hold-as-CASES-row also
  adds its bound (8s default, or the custom bound) to every run — export rows
  already cost more.

## 7. UNKNOWNs / caveats

- Single host (Linux 7.2.3-arch1-3, Godot 4.7.2, Python 3.14.7);
  `OS.create_process` fd-inheritance and orphan reparenting (ppid 1573 =
  `systemd --user`, `/proc/1573/comm` = `systemd`) are this-host proven;
  reparent target differs on other hosts but survival is mechanism-guaranteed.
- In-band evidence cannot order the descendant write strictly after parent
  death (the ~1s sleep vs ~0.4–0.7s child exit makes it near-certain; the
  r61-boundary /proc evidence chain proves the ordering). The tracked row pins
  the classification *shape*; child-death proof stays in boundary receipts.
- Post-return descendant output is buffered kernel-side and discarded at
  harness exit (`run()` does no post-timeout drain) — a descendant write >64KiB
  post-return could block the descendant, not the harness. Not exercised.
- Not covered: multiple descendants, deeper trees, exported-build children,
  `OS.execute` blocking paths, Windows/macOS semantics, `SIGTERM`-vs-`SIGKILL`
  (harness only ever sends SIGKILL), process-group hardening (r61 boundary
  recommendation #4 — a larger move for the planner, not this round).
- Runner-hash provenance caveat: sibling lanes mutate the worktree mid-wave;
  re-read `sha256(run_battery.py)` before trusting any line number above (all
  pointers are on `d705bca7…`, 1012 lines).

## 8. Observed staged state (sibling author, post-edit worktree `0c4c9bee…`)

The r62 author implemented **Design B** verbatim, uncommitted, while this report
was in flight (same mid-flight pattern as r61):

- **Fixture** `corpus/fixtures/descendant_pipe_probe.gd` (36 lines): marker
  `DESCENDANT_PIPE_PROBE: expected signature`, `godot_pid=`/`spawned_pid=`
  prints, arms `(none)`/`--spawn-hold`/`--spawn-detach`. Hold arm spawns
  `sh -c 'sleep 1; echo DESCENDANT_PIPE_AFTER_EXIT_WRITE; sleep 6'` (post-exit
  write ~1s > ~0.4s child exit; pipes held ~7s > bound 3.0s ✓ per §6);
  detach arm `exec sh -c 'sleep 5' </dev/null >/dev/null 2>&1`. Comment cites
  r61-boundary provenance + r62-author scratch re-measurement.
- **CASES row** at post-edit line 98 (pre-edit `]` at :98 → now :99):
  `("descendant_pipe_detached_control", "descendant_pipe_probe.gd",
  ["--spawn-detach"], 0, "DESCENDANT_PIPE_PROBE: expected signature")` — the
  discriminating control as a plain PASS row, exactly my §5 spec.
- **Meta row** `probe_descendant_pipe_eof` appended at post-edit :679–689,
  block :549–689 sitting where §5 prescribed (immediately after the r61 crash
  meta, before `if args.probe_failing:` which moved :548→:690). The hold arm is
  meta-driven under one bounded `Popen` at `pipe_bound = 3.0` (:561, :574).
- **Two refinements beyond my spec**, both strict improvements:
  (a) `pipe_hold["child_exit_at_timeout"] = pipe_proc.poll()` inside the
  `TimeoutExpired` handler — `poll()` reaps the already-dead direct child and
  returns its real exit **0**, giving *in-band* proof the bound fired on pipe
  EOF with the child dead (stronger than my proposed ordering inference; the
  `hold_timed_out_with_child_dead` discrimination gates on `== 0`);
  (b) post-timeout the harness `stream.close()`s both pipes then
  `wait(timeout=3)` (bounded), and afterwards SIGKILLs both orphaned
  descendants via a local `pid_alive`/`os.kill` helper — harness hygiene that
  keeps the wave host clean, never gated in the verdict.
- **Seven discriminations, all True** in the author's receipt
  (`corpus/live/r62-author/runs/20261013T234730112013Z/verdicts.json`):
  `hold_timed_out_with_child_dead`, `hold_post_exit_write_captured`,
  `hold_misattributed_rejects` (`classify_process(None, "TIMEOUT…", output, 0,
  marker) → False` — the pinned misattribution), `hold_descendant_orphaned_alive`,
  `detached_case_passes_clean`, `detached_lacks_post_exit_write`,
  `detached_descendant_orphaned_alive` (the control's own descendant leaks too
  — the battery has no leak detection, pinned *as* a discrimination).
- Battery outcome: **94/94 PASS** (80 CASES + 2 mutants + 12 probe/meta).
  `expected_errors` untouched (no `ERROR:` lines in either arm — matches §5);
  no new opt-in flag; canonical seven-flag command unchanged.
- Boundary claim wording: "completion+pipe-drain bound, timeout kill is
  direct-child-only, descendants orphan; not a Windows/macOS or exported-build
  claim" — consistent with §7's UNKNOWNs.

Residual check for the verifier: `detached_descendant_orphaned_alive` gates on
`pid_alive(pid) is True` evaluated ~immediately after the CASES row returns
(adjacent rows; descendant sleeps 5s) — the race window is the inter-row gap
only, so it is stable on this fixture, but it is still a *timing*-gated check
(the only one among the seven); a <5s-lived detached descendant or a slow
interleaved CASES schedule could flake it. Worth one line in the verifier
report, not a defect.


## Artifact inventory (`.shokunin/game-dev-2d/corpus/live/r62-scout/`)

- `drive_r62.py` sha256 `a6abff5b21aca9c08e1475d6f20748f68b9b106bd0a02c9de9805d3a49cf1eb7`
- `proj/tree_timeout_probe.gd` sha256 `b6b9d41461870dc5a298a6ee6005e90252a93ca365da80818950a1b43a47276a`
- `proj/project.godot` sha256 `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` (verbatim copy of fixture)
- `r62-scout-tree-verdicts.json` sha256 `8d81586b5fdc11fa785aaf0ef59deada9dfe32802c949881a1d0fbaebf45daeb`
- `raw/tree-{clean,detach,hold}.stdout` sha256 `286c8710…`/`ba7656d9…`/`9649be98…`
- `driver.stdout` sha256 `91f6141676ce531e8351261be38515e5ad16b75f77f76ad20320ff5730d2feea`

No commit, no tracked-fixture/runner mutation, no LOG/SCORECARD write;
integration belongs to the r62 executor + named non-author replay.
