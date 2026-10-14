# Round 61 scout report — CASES map + spontaneous-crash row insertion point (host: devin)

Recon only; no tracked edits. Scope kept: this report + `corpus/live/r61-scout/`.

**Bottom line:** the r60-identified zero-runner-change path is confirmed live on the
current classifier, and a sibling (r61 author/executor) has *already staged* the
tracked insertion in the worktree between my baseline sha check and report time —
uncommitted (`git status`: ` M corpus/fixtures/run_battery.py`,
`?? corpus/fixtures/spontaneous_crash_probe.gd`), and already measured 92/92 PASS
in `corpus/live/r61-author/runs/20261013T220433441751Z/verdicts.json`. Map and
insertion-point spec below match what was staged.

## 1. CASES structure — `corpus/fixtures/run_battery.py`

- `CASES = [` at **line 18**; rows are **5-tuples**
  `(name, script, flags, expected_exit, signature)`; list closes `]` (HEAD line 96;
  worktree line 98 after sibling insert). 77 rows at HEAD; 79 in worktree.
- Special `script` sentinels handled inside `execute` (`def execute` HEAD **268** /
  worktree **270**): `__godot_export__`, `__godot_export_missing__`,
  `__save_process_*__` (HEAD **269–285**). Any plain `.gd` filename resolves as
  `"res://" + script` against the run-scratch copy (HEAD **288**); every file in
  `corpus/fixtures/` is copied into `run_dir/scratch` at **117–123**, so a new
  tracked fixture needs *no* extra wiring.
- Per-case timeout `8s` for non-export scripts (HEAD **289**) — crash arm measured
  1.3–2.0 s, fits.
- Iteration site (only one): `for case in CASES: execute(*case)` — HEAD **451–452**,
  worktree **454–455**. Mutants are separate named calls under `--probe-failing`
  (worktree **~547+**, `mutate=True`), not CASES-driven; additive rows don't
  interact.
- Record written per row (HEAD **441–448**): `case/script/flags/command/
  xdg_data_home/expected_exit/actual_exit/signature/verdict/error/output`.

## 2. Classification path (unchanged — proven by hash)

- `run_process` (HEAD **140–149**): `subprocess.run(..., capture_output=True,
  text=True)` → returns `(stdout+stderr, returncode, None)`; POSIX signal exits
  surface as negative `returncode` (-6 SIGABRT, -9 SIGKILL), `error=None`.
  `TimeoutExpired` → `(output, None, "TIMEOUT after …")`.
- `classify_process` (HEAD **151–167**, worktree **153–169**):
  `code == expected_exit and error is None and signature in output
  and not unrelated_errors and "SCRIPT ERROR:" not in output
  and "Parse Error:" not in output`.
  `unrelated_errors` = every merged-output line containing `ERROR:` not matched by
  `allowed_error` (inner fn HEAD **153–162**): exact equality, or
  trailing-`,`-means-prefix match (prefix arm also requires the line contain
  exactly one `ERROR:`), plus a special `chain incomplete` shape.
- `expected_errors` allowlist: plain dict keyed by **case name**, HEAD **391–435**
  (worktree **393–438**), `}.get(name, ())` → default `()`. Selected classifier:
  `classify_audio_process` only for `audio_playback`, else `classify_process`
  (HEAD **436–437**). `SCRIPT ERROR:`/`Parse Error:` veto again at HEAD
  **439–440**.
- **Byte-identity proof the classifier is untouched by the sibling insert:**
  `ast`-extracted `classify_process` from the *current worktree* file hashes
  `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` — identical to
  the r60 verifier's recorded extraction hash (`r60-verifier.md`, runner sha
  `42104d95…`). HEAD runner sha `42104d95af5f…`; worktree sha `3bb29044…`.

## 3. `corpus/fixtures/crash_exit_probe.gd` (r21 SIGTERM pair fixture, sha `ef8bccb7`)

10 lines total. Arms: default → `print("CRASH_EXIT_PROBE: expected signature")`
then `quit(1)`; `--hold-open` → `await create_timer(30.0)` (harness-SIGTERM
target). **No spontaneous arms.** Consumed only by the `--probe-crash-exit`
block (HEAD **753–869**): accept arm `classify_process` True on exit 1; reject arm
`Popen` + `send_signal(SIGTERM)` → returncode −15 classified False; meta requires
accept-True ∧ reject-False ∧ `actual_exit == -SIGTERM`; artifact
`crash-exit-verdicts.json`. `--probe-timeout` (HEAD **870+**) uses the separate
`timeout_probe.gd` (`--delay-clean`/`--hold-open`). Both untouched by the insert.

## 4. r60 evidence establishing OS.crash→-6-with-ERROR-marker

- `reports/round-60/r60-author.md` (author, scratch-only): measurement table —
  `OS.crash("r60 spontaneous crash probe")` → **-6 SIGABRT** ×2 with own
  `ERROR: r60 spontaneous crash probe` line, classify **False** (unallowlisted
  unrelated error); self-`OS.kill` → **-9**, classify **False**; expected **-9**
  → **True** unmodified; expected **-6** → **True** only with the ERROR line
  allowlisted. Zero-runner-change path stated.
- `reports/round-60/r60-verifier.md`: independent re-derivation (`ast` extract of
  `run_process`+`classify_process`), all four arms reproduced, 0 disagreements.
- `reports/round-60/r60-adjudicator.md`: calibration improved-bounded; names
  "natural r61: integrate the tracked crash row".
- Author artifacts were under `corpus/live/runs/round-60/` — **now absent**
  (`corpus/live/.gitignore` lists `runs/`). Persisting copies:
  `corpus/live/r60-verifier/scratch-probe/proj/spontaneous_crash_probe.gd`
  (MARKER line 9; `--spontaneous-crash` arm lines 14–15 `OS.crash(...)`;
  `--spontaneous-sigkill` lines 16–17 `OS.kill(OS.get_process_id())`) and
  `verifier-spontaneous-crash-verdicts.json` (full matrix + `raw_output_lines`;
  crash stderr contains exactly **one** `ERROR:`-bearing line, the rest is
  `at: crash (core/core_bind.cpp:349)`, GDScript bt, `handle_crash: Program
  crashed with signal 4`, C++ bt — none contain `ERROR:`).

## 5. Fresh r61-scout re-derivation (this report's scratch evidence)

`corpus/live/r61-scout/reclassify_r61.py` ast-extracts `run_process`+
`classify_process` verbatim from the tracked runner (extracted sha recorded in
JSON; runner was pre-sibling-edit `42104d95…` at run time — classifier bytes
identical to current, proven above) and ran all three arms fresh via real
subprocesses against a copied probe project (`corpus/live/r61-scout/proj/`).
Result `corpus/live/r61-scout/r61-spontaneous-crash-recheck.json`, raw captures
`r61_{accept_clean_exit1,os_crash,self_sigkill}.stdout`:

| arm | actual_exit | expected 1 | expected -6 | -6 + allowlist | expected -9 | wrong sig | wrong allowlist |
|---|---|---|---|---|---|---|---|
| accept (no flag) | 1 | **True** | False | False | False | False | False |
| `--spontaneous-crash` | **-6** | False | False | **True** | False | False | False |
| `--spontaneous-sigkill` | **-9** | False | False | False | **True** | False | False |

Elapsed 0.60/1.32/0.48 s; marker on stdout in every arm; fresh crash capture
`r61_os_crash.stdout` line 4 is byte-exact `ERROR: r60 spontaneous crash probe`
(`cat -A` verified, no `SCRIPT ERROR:`/`Parse Error:` anywhere). Reproduces r60
exactly: expected-mismatch, missing-allowlist, wrong-signature, and
wrong-allowlist all still reject → the allowlist path is the **only** change of
outcome, and it is per-case-name scoped.

## 6. Exact insertion point (spec) — and observed staged state

Spec for the tracked row(s), all inside `run_battery.py` + one fixture file:

1. **Fixture** — least-disruption precedent (r58 `save_process.gd`, r59
   `audio_bus_route.gd`) is a *new additive* `.gd`, not editing
   `crash_exit_probe.gd`. Promote the r60 scratch probe to
   `corpus/fixtures/spontaneous_crash_probe.gd` (its "NOT a tracked fixture"
   comment must be rewritten). Auto-staged into run scratch by the 117–123 copy.
   ✅ *Observed:* sibling created exactly this file (sha `8d4c5b43…`), comment
   updated to "Round-61 tracked … promoted from the round-60 scratch probe",
   `OS.crash` message kept byte-exact `r60 spontaneous crash probe`.
2. **CASES rows** — append before `]` (HEAD line 96), after the
   `save_process_missing` row (HEAD 95): two 5-tuples with `expected_exit` −6
   and −9 and `signature` `SPONTANEOUS_CRASH_PROBE: expected signature`.
   ✅ *Observed:* worktree lines **96–97**
   `("crash_spontaneous_sigabrt", …, ["--spontaneous-crash"], -6, …)` and
   `("crash_self_sigkill", …, ["--spontaneous-sigkill"], -9, …)`.
3. **Allowlist entry** — inside `expected_errors` dict before `}.get(name, ())`
   (HEAD line 435; worktree 438): `"crash_spontaneous_sigabrt":
   ("ERROR: r60 spontaneous crash probe",)` — exact-match semantics; must equal
   `ERROR: ` + the `OS.crash` argument byte-for-byte. Sigkill row needs no entry
   (stderr is empty; default `()` suffices).
   ✅ *Observed:* worktree line **437**.
4. **Bonus discrimination meta (sibling-added, beyond spec):** worktree
   **~508–545**, `probe_spontaneous_crash_classification` re-classifies the
   already-captured crash-row outputs under mismatched expectations (sigabrt as
   -9 / no-allowlist / wrong-allowlist; sigkill as -6) — all four must reject.
   Zero extra Godot invocations.
5. **Classifier/runner logic: zero changes** — `git diff` shows only three hunks:
   CASES +2, `expected_errors` +1, meta block +~39. `run_process`,
   `classify_process`, `execute` core, `--probe-crash-exit`, `--probe-timeout`
   all untouched (classify sha proof in §2).

## 7. Measured outcome of the staged insert (sibling author run, read-only observation)

`corpus/live/r61-baseline/runs/20261013T220006012870Z/verdicts.json`: **89/89**
on pre-edit tree. `corpus/live/r61-author/runs/20261013T220433441751Z/
verdicts.json`: **92/92** (79 CASES + 2 mutants + 11 probe/meta) —
`crash_spontaneous_sigabrt` actual_exit **-6** PASS, `crash_self_sigkill`
**-9** PASS, `probe_spontaneous_crash_classification` PASS with all four
discriminations True, `probe_crash_exit` (SIGTERM −15 pair) still PASS, fault
run outer PASS at `r61-author/fault-runs/…/fault-verdicts.json`. Sibling critic
sabotage battery exists at `corpus/live/r61-critic/` (forged-marker, extra-ERROR,
SIGSEGV/SIGILL/SIGTERM externals, crash-before-marker etc.) — critic's own
report territory.

## Confidence & remaining unknowns

- **High confidence:** insertion-point spec above is exact and is what is staged;
  both row shapes classify correctly on the untouched production classifier
  (hash-verified) on this host.
- **UNKNOWNs carried forward (per r60, still true):** signal *origin* unprovable
  from `returncode` — self vs external SIGKILL indistinguishable; the -6 row
  asserts exit *shape* + own-`ERROR:`-marker co-occurrence, not sender. The
  `OS.crash` message literally reads `r60 …` inside the r61 tracked fixture —
  intentional byte-exact reuse of the measured line; cosmetic only.
- Not covered: process-tree/descendant timeout cleanup, startup margin,
  exported-build crashes, non-SIGABRT/SIGKILL signals, core capture, non-Linux.
- Timing caveat for verifiers: I observed the worktree mid-mutation
  (sha `42104d95` → `3bb29044` between two scout commands ~minutes apart) —
  siblings are live; re-read file hashes before trusting line numbers.
