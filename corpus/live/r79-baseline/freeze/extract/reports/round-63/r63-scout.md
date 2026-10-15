# Round 63 — scout: merged-stream signature-spoof boundary map + insertion points (host: devin)

Recon only; no tracked edits. Scope kept: this report +
`corpus/live/r63-scout/` (scratch). Runner under study:
`corpus/fixtures/run_battery.py`, worktree == committed r62 work, sha256
`0c4c9bee70569c8ec29f98dea89c437d78587fd5c3c7b3220b76140ac59520dd`, 1154 lines;
`git status` clean at probe time except untracked `corpus/live/r63-*` lanes
(r63-baseline battery was in-flight: `runs/20261014T003458637390Z/` had a
scratch dir, no `verdicts.json` yet — sibling surface, not used here).
Fixture under study: `corpus/fixtures/descendant_pipe_probe.gd`, sha256
`054f37c9174db6be3e4579ecbd84705d25328c252a277827d418bd01b03365d3`, 39 lines.

**Tooling note:** no `lsp` device is exposed to this seat — text search +
full-file read used (fallback per seat card). The whole 1154-line runner and
39-line fixture were read end-to-end, so the map below is direct source
evidence, not grep sampling.

**Bottom line:** the r62 critic's isolated measurement re-verifies on the
current tracked runner via verbatim `ast` extraction — a ppid-gated
post-parent-death signature write lands in the merged capture and
`classify_process` returns **True** on the signature axis (spoof_release
arm). The boundary is pinnable with **one additive fixture arm + one CASES
row (release shape) + one unconditional meta row (hold shape)**; all 94
prior rows stay field-stable because every hunk is an append. The only
fields that ever separate the forged record from a genuine one are the
timeout/child-death evidence (`timed_out`, `child_exit_at_timeout`) — and on
the release shape even those are absent, so the CASES record is genuinely
indistinguishable from a real signature row.

## 1. Signature-verification path (file:line, current worktree)

### Capture + merge — `run_process` (nested in `main`), :143–152

- :145 `subprocess.run(command, capture_output=True, text=True, timeout=…)`
  → `stdout=PIPE, stderr=PIPE` both inherited by the Godot child and by any
  `OS.create_process` descendant (r61/r62 proven).
- **:146 `return proc.stdout + proc.stderr, proc.returncode, None`** —
  stdout and stderr are concatenated into one string *before* any
  classification. This is the merge point.
- :147–150 timeout arm merges `exc.stdout + exc.stderr` the same way and
  returns `(partial_output, None, "TIMEOUT after {timeout_seconds} seconds")`.
  Descendant bytes already in the pipes ride the exception into `output`.
- :151–152 OSError → `(str(exc), None, "launch error: …")`.

### Signature check — `classify_process`, :154–171

**:170 `return (code == expected_exit and error is None and signature in
output …)`** — the expected-signature match is `signature in output`, a
substring check over the *merged* capture. Presence-based; zero
attribution. Companion clauses: no `ERROR:` line outside `allowed_errors`
(:168–169 via `allowed_error` :156–166); `SCRIPT ERROR:`/`Parse Error:`
veto :170–171 (also re-applied at :443–444).

### Other classifiers (not on the CASES path)

- `classify_streams` :173–202 — separate streams; signature must appear on
  **stdout** (:177); unexpected stderr lines reject (:183–201). Called only
  inside `--probe-stream-attribution` (:866–867 via `run_process_streams`
  :848–855). **It does not fix the spoof**: my forged descendant write on
  inherited fd1 lands on stdout → `classify_streams` → **True** (measured,
  §4) — stream separation attributes a line to a stream, not a line to a
  process.
- `classify_audio_process` :204–211 — wraps `classify_process` + leaked-
  ObjectDB warning regex; used only for `audio_playback` (classifier pick
  :440).

### CASES plumbing — `execute` :271–453

- Command build :291 (`godot --headless --path <scratch> --script
  res://<script> -- <flags>`); sentinels `__godot_export_*__` :272–284,
  `__save_process_*__` :285–289.
- Bound :292 — `60 if __godot_export* else 8` → **CASES rows get 8s**; a
  descendant that holds pipes <8s produces a normal clean record.
- `run_process` call :299 → record fields at :445–449: `case, script,
  flags, command, xdg_data_home, expected_exit, actual_exit, signature,
  verdict, error, output` — **no `elapsed_seconds`, no timeout metadata on
  CASES records**; the only provenance fields are `flags`/`command` and
  whatever the fixture printed into `output`.
- `expected_errors` allowlist map :394–439 (`.get(name, ())` :439) — the
  spoof arm needs no entry (no `ERROR:` lines).
- Battery gate :1147 — `all(r["verdict"] == "PASS")`.

## 2. What the r62 meta row already records (`probe_descendant_pipe_eof` :549–689)

Drives the `--spawn-hold` fixture arm under one bounded
`Popen`/`communicate(timeout=3.0)` (:574–605), not `run_process` — because
a CASES/TIMEOUT record can't be PASS. `pipe_hold` record literal :564–569:

| field | set at | source |
|---|---|---|
| `timed_out` | :583 | `except TimeoutExpired` entry |
| `child_exit_at_timeout` | :586 | `pipe_proc.poll()` inside the catch — reaps the already-dead child (`0`) |
| `actual_exit` | :581 | `returncode` on clean return |
| `error` | :592 | `f"TIMEOUT after {pipe_bound} seconds"` |
| `marker_observed` | :616 | `pipe_marker in pipe_text` (:559) |
| `post_exit_write_captured` | :617 | `pipe_post_exit in pipe_text` (:560 `DESCENDANT_PIPE_AFTER_EXIT_WRITE`) |
| `godot_pid`/`descendant_pid` | :618–621 | regex on `DESCENDANT_PIPE godot_pid=`/`spawned_pid=` output lines |
| `godot_alive_at_return`/`descendant_alive_at_return` | :636–637 | `pid_alive` helper :623–634 (`os.kill(pid,0)`) |
| `inner_classification` | :638–639 | `classify_process(actual_exit, error, pipe_text, 0, pipe_marker)` |
| `elapsed_seconds` | :615 | `time.monotonic` delta |

Seven discriminations :644–669 → `all()` gate :678; orphan-SIGKILL harness
hygiene :672–677; record append :679–688 (mode
`bounded_popen_plus_cases_control`, `bounded_claim` :688). The companion
CASES row is `descendant_pipe_detached_control` :98 (expected_exit 0,
signature `DESCENDANT_PIPE_PROBE: expected signature`).

Critic-measured (r62): `spoof` arm — child silent, descendant writes
`…expected signature` at +0.8s, releases ~1.4s → `exit=0, marker present,
classify_process=True` at 1.749s: a positive-path PASS on a signature the
child never emitted. Load-bearing discriminator: `child_exit_at_timeout`
(`poll()` at the catch) — `hold_silent` vs `hang_hold` are byte-identical
except `0` vs `None`. Critic's bounded slip: `hold_post_exit_write_captured`
is presence-only; the committed fixture already hardens the write with the
ppid-flip gate (`descendant_pipe_probe.gd` :32–33 — waits for
`/proc/self/stat` ppid to flip off the child's pid before echoing).
Verifier caveat (r62): post-exit-ness is enforced *by the fixture gate*,
not provable from the receipt alone — a stripped-gate forge yields an
identical record. Boundary (r62): V3 attributed variant measured
`classification_if_error_none=True` — the same captured bytes pass if
`error` is dropped; `/proc/*/fd` holder-scan exists as scratch technique;
no process-group kill in the runner at all.

## 3. Fixture map — `descendant_pipe_probe.gd` (39 lines)

- `MARKER`/`POST_EXIT_WRITE` consts :23–24.
- `print(MARKER)` **:28 — unconditional**; `godot_pid=` print :29.
- `elif` arm chain :31–36: `--spawn-hold` :31–33 (ppid-gated
  `echo POST_EXIT_WRITE; sleep 6`, inherits pipes), `--spawn-detach`
  :34–36 (all stdio → /dev/null). `spawned_pid=` print :37–38 fires for any
  `spawned > 0` — new arms get the provenance line free.
- For a spoof arm the signature in merged output must be
  **descendant-only** — either (a) guard `print(MARKER)` at :28 behind
  flag-absence (edits an existing line; existing arms still print because
  their flags differ), or (b) cleaner: add a dedicated forged-signature
  const the child never prints under any flag and make that the row's
  expected signature — pure `elif` append, :28 untouched. Option (b) is
  the strictly-additive choice.

## 4. Fresh r63-scout measurement (this report's scratch evidence)

`corpus/live/r63-scout/drive_spoof.py` `ast.get_source_segment`-extracts
`run_process` + `classify_process` **verbatim** from the tracked runner and
execs them (production code path). Extraction hashes:
`run_process` `88728b2303f64fc4`, `classify_process` `749fa0607e7707e6` —
**byte-identical to r62-scout's recorded hashes** (unchanged since r60);
`classify_streams` `a886968fd3acf4de`. Arms are `/usr/bin/sh` children —
the mechanism under test is POSIX fd-inheritance + the merged-string
signature check; the classifier only ever sees bytes + exit code.
Descendant writes are ppid-flip-gated (same gate as fixture :33), so each
forged line is provably post-child-death. Receipt
`corpus/live/r63-scout/spoof-verdicts.json` sha256
`6fd32ffead467faa31c5eb070926ae94282a740d202aa0fcb997246613738b0d`, raws
under `raw/`, bound 3.0s.

| arm | actual_exit | error | sig in merged | classify | child_exit_at_timeout | notes |
|---|---|---|---|---|---|---|
| genuine | 0 | None | True | **True** | — | control |
| spoof_release | 0 | None | True | **True** | n/a (no timeout) | elapsed 0.002s; child dead, desc wrote post-death, released pipes → record identical to genuine on every verdict field |
| spoof_hold | None | `TIMEOUT after 3.0 seconds` | True | **False** | n/a (subprocess.run path) | elapsed 3.002s; `classify_if_error_none` = **True**; desc orphaned alive at return |
| spoof_hold_popen | None | `TIMEOUT after 3.0 seconds` | True | **False** | **0** | meta-shape drive; `timed_out=True`; `classify_if_error_none` = **True**; desc orphaned alive |

- `spoof_release` is the strongest form of the boundary: `classify_process`
  returns **True** — a record carrying only a descendant-forged signature
  is fully PASS-shaped (`actual_exit=0, error=None, signature present`).
  Only the `DESC_PID=` provenance line and `command/flags` mark it — never
  the signature axis.
- `spoof_hold`/`spoof_hold_popen` match the declared claim verbatim: the
  forged signature sits in the captured output (`signature in output`
  True — **accepted on the signature axis**), the record rejects only
  through `actual_exit=None`/`error` — i.e. the `timed_out` +
  `child_exit_at_timeout=0` evidence fields are the *entire* separation
  from a genuine signature row. `classify_if_error_none=True` proves the
  rejection is timeout-field-only.
- `classify_streams` on the forged stdout write → **True** — a
  stream-separated port would still accept the spoof; attribution, not
  stream choice, is the boundary.
- Orphan leak reproduces in both hold arms (`descendant_alive_at_return
  True`); harness-side SIGKILL hygiene applied after recording; no stray
  sleeps remain (`ps` check clean).

## 5. Insertion map for the r63 move (all additive → 94 prior rows field-stable)

1. **Fixture arm** — `descendant_pipe_probe.gd`: new `elif` in the chain
   :31–36 reusing the ppid-flip gate shape of :32–33. Suggested pair:
   `--forge-signature-hold` (`…gate…; echo <FORGED_SIG>; sleep 6`) for the
   meta arm, `--forge-signature-release` (`…gate…; echo <FORGED_SIG>` then
   exit → pipe release ~immediately) for the CASES arm. Header comment
   update :3–22. Marker handling per §3 option (b).
2. **CASES row** — append after :98 (`descendant_pipe_detached_control`),
   before `]` :99:
   `("descendant_pipe_signature_spoof_release", "descendant_pipe_probe.gd",
   ["--forge-signature-release"], 0, "<forged-signature>")`. This is the
   *tracked known-accepting forgery row*: it PASSes on a signature the
   child provably never emitted — documented boundary, not a fix. (Hold
   shape **cannot** be a CASES row — error-set records always classify
   False; r62 simplifier/scout §4 proof. Release shape works because the
   descendant releases pipes ≪ the 8s bound :292.)
   `expected_errors` :394–439 needs no entry.
3. **Meta row** — new unconditional block after the r62 meta's print :689,
   before `if args.probe_failing:` :690 (r62 precedent; a *new* record —
   do not edit `probe_descendant_pipe_eof`'s shape). Drive `--forge-signature-hold`
   under the same bounded-Popen pattern :574–615; reuse in-scope
   `pid_alive` :623–634, `pipe_bound` :561, pid regexes :618–621, and the
   discriminate-then-SIGKILL-orphans pattern :672–677. Precedent for the
   synthetic reclassification discrimination: crash meta `reclassify_crash`
   :517–520 / boundary V3 `classification_if_error_none`. Alternate
   bounded-Popen field template: `probe_timeout`'s `bounded_run` :1063–1110.
4. Row arithmetic after the move: 94 + 1 CASES + 1 meta = **96 rows**
   under the canonical seven-flag command; every prior tuple untouched.

## 6. Fields a discriminator could key on

| field | where it lives | discriminating power |
|---|---|---|
| `timed_out` | meta `hold_arm` record only (:583) | True on hold-spoof, absent on genuine/release — separates hold-forgery from clean rows |
| `child_exit_at_timeout` | meta only (:586 `poll()` in `TimeoutExpired`) | `0` = bound fired with child already dead — the single field proving dead-child pipe-wait (critic's load-bearing discriminator) |
| `signature in output` / `marker_observed` | everywhere | **none by design** — presence-only, origin-blind (the pinned boundary) |
| `inner_classification` | meta (:638) | False on hold-spoof via `error`/`exit`, not via signature |
| `classify_if_error_none` (new, synthetic reclassify) | new meta | **True** = signature axis alone accepts the forgery — the acceptance witness |
| `post_exit_write_captured` | meta (:617) | presence-only; post-death ordering comes from the fixture ppid gate, not the receipt (verifier caveat) |
| `godot_pid`/`descendant_pid` + `spawned_pid=` output line | meta + any CASES record | a descendant existed — genuine no-descendant rows lack it, but genuine descendant rows (detached) also carry it |
| `godot_alive_at_return`/`descendant_alive_at_return` | meta (:636–637) | leak/orphan evidence; desc-alive is racy for fast-exiting release descendants — keep informational |
| `elapsed_seconds` | meta/fault/bounded_run records only (:615) | bound-exact ≈3.0s corroborates timeout; never on CASES records |
| `flags`/`command` | every CASES record (:445–447) | carries the `--forge-*` arm flag — the only CASES-level provenance |

## 7. UNKNOWNs / caveats

- My measurement arms use `sh` children, not Godot `OS.create_process` —
  the fd-inheritance + merged-capture mechanism is identical (the fixture's
  own arms prove the Godot spawn inherits fds), but the tracked arm will
  re-measure under real Godot in the battery run.
- Single host (Linux 7.2.3-arch1-3, Python 3.14.7); reparent target is the
  session subreaper (ppid 1573, `systemd --user`) — other hosts reparent
  elsewhere; survival/ppid-flip is mechanism-guaranteed.
- The ppid gate proves write-after-death at the *fixture* level; the
  verdict receipt alone can never prove ordering (r62 verifier's
  stripped-gate caveat) — the row documents a boundary, it doesn't
  enforce it.
- `spoof_release`'s descendant is provably dead by pipe-EOF at return, but
  an `os.kill(pid,0)` check can still see a zombie inside the repaper
  window — gate `release_descendant_dead` only if measured stable;
  informational is safer.
- A release-shaped CASES row adds ~0.5–1s and a hold-shaped meta arm ~3s
  to every battery invocation (r62 meta already pays 3s).
- `classify_streams` accepting the forged fd1 write (measured) means
  "signature on stdout" ≠ "signature from the child" — any future port to
  stream-separated CASES classification does not close this boundary.

## Artifact inventory (`.shokunin/game-dev-2d/corpus/live/r63-scout/`)

- `drive_spoof.py` sha256 `ac75adc5f9c10371efcaba550f046d2d3c00eaf211b47b7dcb536646a35b824b`
  (verbatim-extraction arm driver, 4 arms + classify_streams check).
- `spoof-verdicts.json` sha256 `6fd32ffe…`; raw captures `raw/spoof_release.stdout`,
  `raw/spoof_hold.stdout`, `raw/spoof_hold_popen.stdout`.

No commit, no tracked-fixture/runner/LOG/SCORECARD write, no subagent
dispatch. All spawned descendants self-exited or were SIGKILLed after
recording; no stray processes remain.
