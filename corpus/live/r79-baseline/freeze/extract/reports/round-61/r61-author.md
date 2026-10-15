# Round 61 author report — tracked spontaneous-crash classification (host: devin)

Seat: author (role executor), lane `game-dev-2d`, declared axis-move: **coverage**
— land the tracked spontaneous-crash classification row identified at r60.

## Scoped move and source

r60 verified in scratch (author + named verifier, zero disagreements): a fixture
calling `OS.crash()` exits `-6` (SIGABRT) carrying its own `ERROR:` line and
classifies False unless that exact line is allowlisted; self-`OS.kill(pid)`
exits `-9` and classifies True unmodified when `-9` is expected. The identified
zero-runner-change path = the existing `expected_errors` allowlist field.

## Tracked files changed (this lane's only tracked writes this round)

1. `corpus/fixtures/spontaneous_crash_probe.gd` — NEW tracked fixture, promoted
   from the r60 scratch probe (`corpus/live/r60-verifier/scratch-probe/proj/
   spontaneous_crash_probe.gd`). Header comment updated to tracked status;
   `MARKER`, both flag names, and the `OS.crash("r60 spontaneous crash probe")`
   message byte-identical to the twice-verified artifact. Arms: (none) →
   `quit(1)`; `--spontaneous-crash` → `OS.crash` (−6); `--spontaneous-sigkill`
   → `OS.kill(own pid)` (−9). sha256 `8d4c5b43…`.
2. `corpus/fixtures/run_battery.py` — **42 insertions, 0 deletions**, three
   additive hunks:
   - CASES +2 rows appended at list end (prior row order untouched):
     `("crash_spontaneous_sigabrt", "spontaneous_crash_probe.gd",
     ["--spontaneous-crash"], -6, "SPONTANEOUS_CRASH_PROBE: expected signature")`
     and `("crash_self_sigkill", …, ["--spontaneous-sigkill"], -9, …)`.
   - `expected_errors` +1 entry: `"crash_spontaneous_sigabrt":
     ("ERROR: r60 spontaneous crash probe",)` — exact-match allowlist for the
     crash's own single `ERROR:` line. `crash_self_sigkill` needs none
     (its stderr carries no `ERROR:` line at all).
   - ONE new unconditional meta row `probe_spontaneous_crash_classification`
     after the `probe_save_independent_process` append: re-classifies the
     **already-captured** crash-row outputs under mismatched expectations
     (zero extra Godot invocations) and appends the discriminating arm the
     CASES table cannot express.

   Runner sha256 `42104d95…` (pre-edit, = r59/r60) → `3bb29044…` (post-edit).

## Why the meta row (why pure CASES could not carry the negative arm)

Every CASES row must classify True or the whole battery FAILs
(`all(r["verdict"] == "PASS")`), so a CASES tuple cannot encode "this
classification must reject." The r60-identified zero-runner-change path
covers the *positive* allowlist only; expressing the brief's "expected-exit
mismatch / missing ERROR marker still rejects" needs a rejection arm, which in
this runner lives at meta level (`probe_godot_error`'s fault arm is the
precedent). The added block is ~40 lines, no new flag, no new subprocess —
it re-classifies the crash rows' captured `output` through the same
`classify_process`, mirroring the unconditional `probe_save_independent_process`
pattern. Discriminations recorded in the row:

- `sigabrt_expected_-9_rejects` — same crash output, expected −9 → False
  (expected-exit mismatch still rejects even with marker + allowlist met).
- `sigabrt_missing_allowlist_rejects` — expected −6, allowlist `()` → False
  (the crash's own `ERROR:` is an unrelated error without the entry).
- `sigabrt_wrong_allowlist_rejects` — expected −6, allowlist
  `("ERROR: unrelated different diagnostic",)` → False (exact-match, not
  wildcard).
- `self_sigkill_expected_-6_rejects` — the −9 arm under expected −6 → False.

## Exact evidence

Causal scratch (pre-edit, driver `ast`-extracts `run_process`/`classify_process`
verbatim from the unmodified runner sha `42104d95…`, no transcription):
`python3 .shokunin/game-dev-2d/corpus/live/r61-author/scratch-probe/drive_probe.py`
→ `corpus/live/r61-author/scratch-probe/causal-scratch-verdicts.json` **PASS**
(sha `f908e7bd…`); exits −6/−9/1 and all nine classification checks equal the
expected map; per-arm raw `*.stdout` beside it.

Mandated battery (exact invocation):
`python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot
--runs .shokunin/game-dev-2d/corpus/live/r61-author/runs --probe-failing
--probe-unrelated-error --probe-export-launch --probe-godot-error
--probe-stream-attribution --probe-crash-exit --probe-timeout` → exit 0,
`runs/20261013T220433441751Z/verdicts.json` **PASS, 92/92 rows** (sha
`d36f27fc…`; stdout `corpus/live/r61-author/battery.stdout`). Of 92: 79 CASES +
2 mutants + 11 meta/probe rows; the two inner `FAIL` lines are the designed
`godot_error_unrelated`/`stream_reject` rejections, same as every prior run.

Prior-row stability: field-diff vs `corpus/lessons/r59-audio-non-author.json`
over `(script, flags, expected_exit, actual_exit, signature, verdict, error)` —
**89 common cases, 0 mismatches**.

New rows measured:
- `crash_spontaneous_sigabrt`: expected/actual `−6`, verdict PASS; captured
  output contains exactly one `ERROR:` line — `ERROR: r60 spontaneous crash
  probe` — plus `at: crash (core/core_bind.cpp:349)` and both backtraces.
- `crash_self_sigkill`: expected/actual `−9`, verdict PASS; output beyond
  banner+marker is empty.
- `probe_spontaneous_crash_classification`: verdict PASS; all four
  discriminations `true`; `sigabrt_exit −6`, `self_sigkill_exit −9`.

Separate leg: `--fault-injection` →
`fault-runs/20261013T220602482092Z/fault-verdicts.json` outer **PASS** (sha
`b1b06ef7…`), designed inner hang/unrelated FAILs — unchanged.

Prior classification behavior untouched (all still in this run): harness
SIGTERM probe arm still exits −15 and classifies False inside
`crash-exit-verdicts.json` PASS; timeout probe PASS; mutant detections PASS;
every expected-mismatch rejection above rejects.

## Per-axis claimed verdict (author claim; named non-author replay still due)

- **coverage — improved (candidate)**: 0 → 2 tracked spontaneous signal-death
  CASES rows + 1 discriminating meta row; 89 → 92 rows, all prior stable.
- **calibration — unchanged**: no classifier/logic edit; the allowlist and
  meta consume existing `classify_process` semantics only.
- **depth — unchanged**: no new mechanic surface.

## UNKNOWNs / retained caveats

- Signal *origin* unprovable from `returncode`: self-SIGKILL vs external
  SIGKILL indistinguishable; `OS.crash` attribution rests on its own
  `ERROR:`+backtrace output, not syscall evidence (retained from r60).
- Bounded to Linux x86_64 headless Godot 4.7.2; `OS.crash` internally raises
  SIGILL then dies SIGABRT — parent-visible `−6` held here (r60 ×3, r61 ×2);
  cross-host determinism unprobed. No core-capture, no exported-build crash,
  no process-tree timeout (still the next candidate), no production claim.
- The fixture's crash message keeps the verbatim r60 string
  ("r60 spontaneous crash probe") for byte-continuity with the double-verified
  evidence; the allowlist entry follows it exactly.
- `crash_self_sigkill` intentionally has **no** `expected_errors` entry: the
  arm emits no `ERROR:` line, so the row itself demonstrates the
  missing-ERROR-marker shape passing purely on exact −9 match.

No commit, no push/merge, no LOG/SCORECARD write; adjudication and named
non-author replay follow.
