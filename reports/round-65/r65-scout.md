# Round 65 — scout: forged-REJECTION dual, landed-diff map (host: devin)

Recon only; no tracked edits. Scope kept: this report +
`corpus/live/r65-scout/` (scratch). The author's diff is **landed
uncommitted** in this lane root (`~/Projects/shokunin/game-dev-2d-shokunin`,
reached via `.shokunin/game-dev-2d` symlink from the worktree):

- `corpus/fixtures/run_battery.py` +431/−0 → sha256
  `1acbc73d80fa69317600ee2813ec44a71fd02a2436471bf52cb8c15ae052b2a3`,
  single block `:1107–1537`.
- `corpus/fixtures/descendant_pipe_probe.gd` +35/−0 → sha256
  `37cf50156839502a1372746d31c3db6b8c835df734acf838025c1664f3262e59`.
- `git status` shows only these two `M` under `corpus/fixtures/` (plus
  untracked `corpus/live/r65-*/` and `reports/round-65/`). HEAD `fe4bbeaf`.

**Tooling note:** no `lsp` device is exposed to this seat — text search +
targeted reads used (fallback per seat card). Both changed files and all
referenced helpers were read in full at the relevant regions; this map is
direct source evidence, not grep sampling.

**Bottom line:** the declared claim is **measured-confirmed in the author's
own battery run** (`corpus/live/r65-author/runs/20261014T023015140150Z/
verdicts.json`: 98 rows, verdict PASS, `probe_descendant_error_spoof` with
28/28 discriminations True) and independently reproduced by the prior
scout-pass measurement already in this scratch
(`corpus/live/r65-scout/errforge-verdicts.json`, verbatim-`ast`-extracted
`classify_process`, real Godot 4.7.2 + a Godot-free `sh` forge arm). The
rejection axis is exactly as origin-blind as the signature axis, and the
r64 while-live gate does **not** reject the forged-error arm — both as
the brief predicted.

## Q1 — how un-allowlisted error markers cause FAIL (`classify_process` error path)

`classify_process(code, error, output, expected_exit, signature,
allowed_errors=())` — `run_battery.py:160–177`. It takes a **merged**
`output` string (stdout+stderr concatenated upstream by `run_process`
`:149–158`, order unrecoverable). Reject conditions — any one suffices:

1. `code != expected_exit` or `error is not None` (`:176`) — the
   exit/timeout axis (TIMEOUT sets `error`, `code=None`).
2. `signature not in output` (`:176`) — the r63 origin-blind axis.
3. `unrelated_errors` non-empty (`:174–175`): **any line containing the
   substring `"ERROR:"`** (case-sensitive, position-free — mid-line and
   glued `XERROR:` both hit; measured in
   `errforge-verdicts.json → substring_probes`) not matched by
   `allowed_errors`. This is the rejection axis under test.
4. `"SCRIPT ERROR:" in output` — unconditional (`:177`). Un-allowlistable:
   the string itself contains `ERROR:`, and this check runs even if a
   matching allowlist entry absorbed the line in (3).
5. `"Parse Error:" in output` — unconditional (`:177`); distinct
   case-sensitive substring (does not contain `ERROR:`).

Allowlist mechanics (`allowed_error`, `:162–172`):
`stripped == allowed` exact-match, or `allowed.endswith(",")` prefix form
requiring `stripped.count("ERROR:") == 1` (a second `ERROR:` on the same
line defeats a matching prefix entry — measured:
`allowed_prefix_comma_second_error → False`), or the structured
`"ERROR: chain incomplete collections=…"` special-case. Per-case
allowlists live in the `expected_errors` map `:400–445`; the r61 crash
allowlist is the exact-match tuple `("ERROR: r60 spontaneous crash
probe",)` (`:444`, re-tested by `probe_spontaneous_crash_classification`
`:519–553`). `descendant_pipe_*` rows are absent from the map → `()` —
nothing absorbed.

The allowlist is itself origin-blind (scout-measured
`allowlist_absorption`: forged line allowlisted → `True`, empty →
`False`) — it keys on bytes, not authorship.

## Q2 — the rejection-triggering marker

Any un-allowlisted line containing `ERROR:` flips the row. The author
chose `ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic`
(fixture `:67`, `ERRFORGE_ERROR`) specifically because it is **byte-
identical to what the engine emits for the genuine arm's
`push_error(ERRFORGE_ERROR_BODY)`** (`:84`) — the cleanest possible dual:
the forged write and the genuine write differ only in *which process*
wrote them. Measured in the author run: `error_lines` is
`["ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"]` in
both records (the genuine arm's `   at: push_error
(core/variant/variant_utility.cpp:1023)` + GDScript backtrace context
lines carry no `ERROR:` substring → provenance only).

`SCRIPT ERROR:`/`Parse Error:` would also reject but are weaker choices
(redundant with (3)/(4) and not push_error-shaped); lowercase `Error:` /
`WARNING:` do **not** reject (case-sensitive — scout-measured).

## Q3 — CASES-row forged-rejection shape: confirmed carried

`errforge_run` (`:1137`) reproduces the CASES record shape exactly —
bounded `Popen` + `communicate(timeout)` mirroring `run_process`, then
`classify_process(actual_exit, error, text, 0, signature)` stored as
`inner_classification` (`:1214`). Author-run receipts:

| arm | flags | actual_exit | error | sig | forged ERROR: | inner cls | stripped cls |
|---|---|---|---|---|---|---|---|
| release | `--spawn-errforge-release` | 0 | None (0.679s) | yes | yes, post-death | **False** | True |
| hold | `--spawn-errforge-hold` | None | TIMEOUT 3.003s, child_exit_at_timeout=0 | yes | yes, inside TIMEOUT rec | **False** | False* |
| genuine | `--emit-errforge` | 0 | None (0.671s) | yes | yes, pre-death push_error | **False** | True |

\* hold's `stripped_classification` is False *by construction* — the
counterfactual strips only `ERROR:` lines; the `error="TIMEOUT"` field
persists, so the timeout axis still rejects. The counterfactual isolates
the error axis only on clean records — correct as designed.

- `cases_visible()` (`:1396`) = `{actual_exit, error, signature_observed,
  error_lines, classification}` — measured **identical** between forged
  and genuine (`forged_vs_genuine_cases_fields_identical` True). The
  output line sets differ only in provenance lines (banner /
  `godot_pid=` / `spawned_pid=` / `write_ppid=` / push_error `at:` +
  backtrace) — `forged_vs_genuine_differ_only_in_provenance` True with the
  verbatim symmetric diff pinned in `provenance_only_line_diff`.
- An actual CASES tuple is **inexpressible**: every row's verdict is the
  bare classify boolean and the battery requires all-PASS
  (`payload["verdict"]` `:1995`); an expected-FAIL row has no encoding —
  the r62 hold-arm precedent, meta-driven `bounded_popen` instead. The
  row *shape* is what's measured; a real tuple would FAIL the battery by
  design.
- Dual datum (scout scratch, `godot_errforge_hold`):
  `error_axis_only_classification` = `classify_process(0, None, text, …)`
  — clearing the timeout/exit axes entirely — is still **False**: the
  ERROR: line alone rejects. The r63 hold-arm equivalent with signature
  axis cleared classified **True**. Mirror confirmed.

## Q4 — does `probe_while_live_signature_gate`'s read see these bytes?

**It captures them; its criterion ignores them — verified two ways.**

- The r64 `gated_signature_run` (`:901–1010`) drains BOTH pipes via
  `selectors` until EOF (`captured` bytearray `:920,948`) — error bytes
  land in `output_lines`/the `inner_classification` text just like any
  bytes. But the acceptance decision is
  `gated_signature_accepted = marker_observed and
  child_alive_at_marker_observation` (`:1001–1003`) — the **signature
  marker only**; `ERROR:` content is never evaluated. The gate's
  inner_classification *would* reject the same bytes (it calls
  `classify_process` over the full capture `:1007`), but nothing in the
  gate verdict consults it.
- The r65 `gated_errforge_run` (`:1226`) is the dual-marker variant —
  tracks `error_observed` + per-read liveness alongside the signature.
  Author-run receipts on `--spawn-errforge-release` (3 reps): signature
  observed **while-live** (`child_alive_at_signature_observation` True,
  `gated_signature_accepted` True all 3); forged error observed
  **post-death** every rep — `dead_observed_at` 0.632/0.686/0.678s <
  `error_observed_at` 0.663/0.718/0.710s — yet `inner_classification`
  False on the same bytes. `--emit-errforge` reps (2): error observed
  while-live (err@0.571/0.588 < dead@0.637/0.656). So: gate-accepted and
  still FAIL — rejection stays in the un-gated classifier; the forged
  error is gate-invisible *as a verdict input*, though the gated read
  does pin it post-death. `gate_does_not_reject_forged_error_arm` True.

## Q5 — insertion map (as landed, +466/−0)

**Fixture** `descendant_pipe_probe.gd` (+35): doc header `:42–61`; consts
`ERRFORGE_PPID_WRITE`/`ERRFORGE_ERROR_BODY`/`ERRFORGE_ERROR` `:65–67`;
flag parses `:73–75`; banner / `push_error` emit branch `:80–84`; spawn
`elif` `:97–100` reusing the r63 reparenting gate **verbatim**
(`/proc/self/stat` field-4 ppid poll → post-death `echo ERRFORGE_ERROR;
echo write_ppid=$pp`, `; sleep 6` tail on `-hold`). New arms sit last in
the flag/elif chains; all pre-existing arms' control flow untouched.

**Runner** `run_battery.py` (+431), one block `:1107–1537` between the r64
gate print (`:1106`) and `if args.probe_failing:` (`:1538`):
`errforge_run` (`:1137`) bounded-Popen CASES-shape + counterfactual strip,
`gated_errforge_run` (`:1226`) dual-marker selector read,
`split_errforge_run` (`:1348`) separate PIPEs; invocations — 3 un-gated
arms + `ef_gate_release`×3 + `ef_gate_genuine`×2 + 2 split runs
(`:1382–1395`); `cases_visible` (`:1396`) + line-diff; 28-key
`ef_discriminations` (`:1409`); un-gated SIGKILL orphan hygiene
(`:1515`); `results.append({case: "probe_descendant_error_spoof", …,
bounded_claim})` `:1523–1536`. Reuses existing `pid_alive` (`:629`),
`kernel_ppid` (`:781`), `gate_poll_tick` (`:895`), `detached` (`:568`),
`classify_process`; **zero new imports, zero edits to any prior row or
helper.**

**Row accounting:** 81 CASES tuples + 17 meta/conditional rows = 98
(author run had `--probe-failing --probe-export-launch --probe-godot-error
--probe-stream-attribution --probe-crash-exit --probe-timeout
--probe-unrelated-error` all active, per row names in the payload).
Baseline `r65-baseline/runs/20261014T022523005280Z/verdicts.json`: 97 rows
— the author run adds exactly `probe_descendant_error_spoof`. Every shared
row compares equal on `verdict`/`actual_exit`/`error`/`signature`
(checked all 97 — no diffs); r64 gate discriminations all-True with
identical keys. "Byte-stable" holds at the tracked-file level
(+466/−0 diff) and at the row-field level.

## Adjacent measured datum (not in the author's claim scope)

`classify_streams` (`:179–208` — used **only** by
`probe_stream_attribution` `:1715`, never by `execute()`/CASES rows) is
**not** equally origin-blind: its per-line allowlist scan covers **stderr
only** (`:200–207`); stdout is checked only for `SCRIPT ERROR:`/`Parse
Error:`. Measured on verbatim-extracted code
(`corpus/live/r65-scout/classify_streams_probe.json`): the **forged**
shape (error on stdout — the descendant's `echo` inherits the child's
stdout pipe; `split_errforge_run` measured `error_on_stdout=True`) is
**accepted True**, while the **genuine** shape (`push_error` → stderr)
is **rejected False**. The stream-aware classifier inverts the spoof
outcome: a while-live+stdout-injected error would slip it entirely.
Latent surface only — no CASES row routes through it — but worth the
record if a future round proposes `classify_streams` as the fix for this
axis.

## Remaining unknowns / caveats

- `write_ppid=1573` is a fixture-asserted provenance claim on the release
  arm (descendant dead at return → no `/proc` check possible); kernel-
  corroborated only on the hold arm (`/proc/<pid>/stat` ppid == write_ppid
  == 1573 ≠ godot_pid, measured). Same disclosure carried from r63/r64.
  `1573` is this host's reparent target (subreaper), stable across
  r63–r65 receipts.
- Post-death ordering is proven by the fixture's `/proc/self/stat` ppid
  gate (the write cannot execute while the child lives) plus
  `dead_observed_at < error_observed_at` in every gated rep — two
  independent witnesses.
- `split_errforge_run`'s release-arm descendant isn't pid-recorded
  (`subprocess.run` doesn't expose it); it self-exits immediately (no
  `; sleep 6` tail) — the un-gated reap loop covers the other arms' pids.
- Gated-genuine reps = 2 vs release = 3 — matches the author's rep
  budget; both observed while-live.
- Claim scope is correctly bounded to Linux headless Godot 4.7.2 POSIX
  pipe semantics (per the row's `bounded_claim`).

Evidence paths: `corpus/live/r65-author/runs/20261014T023015140150Z/
verdicts.json` (row 97, 28/28), `corpus/live/r65-scout/errforge-
verdicts.json` + `raw/` + `classify_streams_probe.json`,
`corpus/live/r65-author/battery.stdout` ("PASS descendant error-spoof
meta").
