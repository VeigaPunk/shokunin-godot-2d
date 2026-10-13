# Round 61 scribe — crash-classification knowledge entry + LOG draft (host: devin)

Report-only seat. No tracked edits, no Godot runs by this seat, no
commit/push/merge, no delegation. This report carries two drafts for parent
admission: (A) the corpus knowledge entry on crash-classification semantics,
(B) the LOG.md round-61 entry. My scratch receipt:
`corpus/live/r61-scribe/observations.md` (exact commands + observed output).
Sibling wave state: untracked `corpus/live/r61-baseline/`, `r61-reviewer/`,
`r61-simplifier/` scratch dirs; sibling reports `r61-baseline.md`,
`r61-reviewer.md` appeared in `reports/round-61/` during this draft.

**State transition observed mid-draft** (two `git status` reads): at first read
the tree was clean apart from sibling scratch; at finalize time the executor's
tracked edit had landed — `corpus/fixtures/run_battery.py` modified (sha
`42104d95…31fb` → `3bb2904497dfeb774d8d4a9b8c5f8b39ddf1e0ba66bde53599e17eafe3bcec5d`)
and new untracked fixture `corpus/fixtures/spontaneous_crash_probe.gd` (sha
`8d4c5b43939f48ce1f099286cb0002415e53373177e4e81aae1922b01ca81ba5`), plus an
untracked `corpus/fixtures/__pycache__/` (import byproduct, not mine — I ran
`ast.parse`, which writes no bytecode). The diff is described exactly in
"Observed executor diff" below; a landed diff is not a PASS — the named
non-author replay is still owed.

## Baseline read (measured by me, read-only — pre-edit state)

- `corpus/fixtures/run_battery.py` pre-edit sha256
  `42104d95af5fcb98d742c495ee4562ea0c579c49d9ca22d11755302f685c31fb`
  (`ast` hash of file bytes) — identical to r60 author/verifier claims.
- `ast` parse pre-edit: **77 CASES rows**, each a 5-tuple
  `(name, script, flags, expected_exit, signature)`; `expected_errors` is a
  per-name allowlist dict (run_battery.py L391–435, `.get(name, ())`).
- Env: Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python `3.14.7`, Linux
  `7.2.3-arch1-3` — identical to r60 author/verifier environment.
- Provenance note: r60 author's scratch `corpus/live/runs/round-60/` no longer
  exists (`live/` is disposable). Surviving probe-fixture copies:
  `corpus/live/r60-verifier/scratch-probe/proj/spontaneous_crash_probe.gd` and
  `corpus/live/r61-reviewer/scratch-probe/proj/spontaneous_crash_probe.gd`.

## Observed executor diff (git diff, read-only — landed during this draft, UNVERIFIED)

- `CASES` += two rows: `("crash_spontaneous_sigabrt",
  "spontaneous_crash_probe.gd", ["--spontaneous-crash"], -6,
  "SPONTANEOUS_CRASH_PROBE: expected signature")` and `("crash_self_sigkill",
  "spontaneous_crash_probe.gd", ["--spontaneous-sigkill"], -9,
  "SPONTANEOUS_CRASH_PROBE: expected signature")` → 77 → **79 CASES** by
  inspection.
- `expected_errors` += one entry: `"crash_spontaneous_sigabrt": ("ERROR: r60
  spontaneous crash probe",)` — exact-match allowlist of the crash's own
  ERROR line. `crash_self_sigkill` gets none (its stderr is empty), matching
  the r60 zero-entry prediction for the -9 arm.
- New unconditional meta row `probe_spontaneous_crash_classification` appended
  after the save-process block: re-classifies the already-captured row outputs
  (zero extra Godot invocations) and requires both rows PASS with actual exits
  -6/-9 plus four discriminating rejections — sigabrt under expected -9,
  sigabrt -6 with empty allowlist, sigabrt -6 with a wrong allowlist,
  self-sigkill under expected -6. Projected full denominator 89 → **92**
  (79 CASES + 2 mutants + 11 probe/meta) by inspection; measured count
  pending the executor/verifier run.
- `run_process`/`classify_process`/`classify_streams` and every prior CASES
  row and `expected_errors` entry: byte-unchanged per the diff hunks — prior
  classification behavior preserved by construction (replay still required
  for evidence).
- New fixture `spontaneous_crash_probe.gd`: same marker and arms as the r60
  scratch probe, crash message kept verbatim `"r60 spontaneous crash probe"`
  (which is what the allowlist entry matches); comment updated to say
  tracked, promoted from r60.

---

## Draft A — knowledge entry (proposed slot `corpus/lessons/r61-spontaneous-crash.md`; corpus `knowledge/` placement is parent's call)

```markdown
# Spontaneous-crash classification semantics (Godot 4.7.2 headless, Linux x86_64)

source: `reports/round-60/r60-author.md`, `reports/round-60/r60-verifier.md`
(zero disagreements), `reports/round-60/r60-adjudicator.md`;
`corpus/lessons/r21-signal-exit.md` (harness-SIGTERM contrast);
`corpus/fixtures/run_battery.py` `run_process`/`classify_process`;
`corpus/live/r60-verifier/scratch-probe/` and
`corpus/live/r61-reviewer/scratch-probe/` (surviving probe fixture + raw
stdout; r60 author's own scratch under `live/runs/round-60/` is disposable and
no longer present).

verified-at: three independent derivations of every constant — r60 author
`20261013T1649–1652Z`, r60 non-author verifier `20261013T1655Z` (own
`ast`-extracted classifier, own captures), r61 reviewer `20261013T2200Z` (own
extraction, own captures). Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python
`3.14.7`, Linux `7.2.3-arch1-3`. All three measurements ran under runner
sha256 `42104d95…31fb` (pre-edit); the tracked rows land in
`3bb29044…` — `classify_process`/`run_process` byte-unchanged between them.

recheck: (1) at the named non-author r61 replay — the tracked row must reach
the same classifications in fresh scratch; (2) on any Godot version change —
the crash-handler stderr shape (`at: crash (core/core_bind.cpp:349)`,
`handle_crash: Program crashed with signal 4`, backtraces) is engine-owned
text and can drift; (3) if the fixture's `OS.crash` message changes, the
allowlist entry must change with it; (4) off this host — the SIGILL→handler→
SIGABRT `-6` determinism is verified on this host only.

## Returncode shape the classifier sees

`run_process` returns merged stdout+stderr plus `(returncode, error)`:
positive `code` = normal exit code; negative `-N` = process killed by signal
N; `code=None` with `error` set = harness timeout (`TIMEOUT after …`) or
launch error. `classify_process` passes iff `code == expected_exit`,
`error is None`, `signature in output`, no non-allowlisted `ERROR:` line, and
no `SCRIPT ERROR:`/`Parse Error:`. A negative expected exit is therefore
expressible with zero classifier change.

## Signal-vs-harness-kill decision table (same marker emitted in every arm)

| arm | parent-visible exit | stderr shape | classify expected 1 | classify expected -6 | classify expected -6 + allowlist | classify expected -9 |
|---|---|---|---|---|---|---|
| clean `quit(1)` | 1 | none | **True** | False | False | False |
| harness SIGTERM to live marker-observed child (r21 `--probe-crash-exit`) | -15 | none | **False** | — | — | — |
| `OS.crash("r60 spontaneous crash probe")` ×2 runs | **-6 (SIGABRT)** | own `ERROR: r60 spontaneous crash probe` + `at:` + GDScript bt + `handle_crash: Program crashed with signal 4` + C++ bt | **False** | **False** | **True** | False |
| `OS.kill(OS.get_process_id())` | **-9 (SIGKILL)** | empty | **False** | False | False | **True** |

Measured nuance: `OS.crash` raises SIGILL internally (handler prints
`signal 4`), dumps both backtraces, then the process dies by SIGABRT; the
parent-visible returncode is **-6 on every run measured** (2 author + 2
verifier + 2 reviewer). The stdout marker is captured in every arm because
`print` flushes pre-crash.

## The -6+ERROR allowlist rule

A spontaneous SIGABRT crash row needs exactly one `expected_errors` entry —
the crash's own `ERROR: <message>` line verbatim — because that line is an
unallowlisted unrelated error to `classify_process`. All other crash stderr
lines (`at:`, backtraces, `handle_crash:`, C++ bt) contain no `ERROR:`
substring and never reject. If the crash message is a fixed literal use an
exact allowlist string; if it embeds anything variable use the
trailing-comma prefix form (`allowed.endswith(",")` → `startswith` plus
`stripped.count("ERROR:") == 1`). A self-SIGKILL row needs no entry at all
(-9 arm has empty stderr and classifies True unmodified). This is the
zero-runner-logic-change path: CASES row(s) plus one dict entry; `run_process`
/`classify_process` untouched, so harness-SIGTERM -15 rejection, timeout
rejection, and every expected-mismatch rejection are preserved by
construction — and still must be shown preserved by the named replay.

## Retained UNKNOWNs (do not soften)

- **Signal-origin indistinguishability**: `returncode` carries the signal
  number, not its origin. A self-raised SIGKILL and an external/OOM-killer
  SIGKILL are the same -9 to this classifier. `OS.crash` provenance rests on
  its own `ERROR:` line + backtrace pointing at the script line — output
  evidence, not syscall evidence. A tracked -9/-6 row proves the exit shape,
  not who sent the signal.
- Cross-host determinism of -6 untested; no signals beyond SIGABRT/SIGKILL
  measured; no core-dump capture (systemd path, no `core.*` in scratch);
  exported-build crash behavior, process-tree timeout, startup margin remain
  unprobed; Linux x86_64 headless only; not production crash handling.
```

---

## Draft B — LOG.md round-61 entry (draft; `[pending]` = fill from settled raw before commit)

```markdown
## Round 61 — 2026-10-13 — coverage (devin host; declared before dispatch)
- ONE claim to test: land the tracked spontaneous-crash classification row
  identified at r60 — a tracked fixture whose spontaneous `OS.crash` SIGABRT
  (parent-visible -6) carrying its own `ERROR:` marker line classifies True
  once that exact line is allowlisted, while prior classification behavior
  (harness SIGTERM -15 reject, timeout reject, expected-mismatch reject) is
  untouched. Before r60 work/report [pending: parent fill commit hashes], 77
  CASES / 89 full; classifier boundary scratch-verified at r60 and
  independently re-measured this round. Zero classifier-logic change:
  additive CASES row(s) + one `expected_errors` allowlist entry only. If the
  measured result falsifies the claim, report actuals, never force it.
- Wave (LEAF, no delegation; disjoint own report under
  `.shokunin/game-dev-2d/reports/round-61/` and scratch under
  `.shokunin/game-dev-2d/corpus/live/r61-<name>/`): [pending: parent fill
  settled roster — observed sibling scratch at draft time: r61-baseline,
  r61-reviewer, r61-simplifier; r61-scribe draft]. Parent integrates and
  commits only after settlement; named non-author replay then decides
  admission. No leaf commit/push/merge.
- Settlement: [pending — expected evidence: executor tracked edit observed
  landed (two CASES rows `crash_spontaneous_sigabrt` -6 / `crash_self_sigkill`
  -9, one `expected_errors` entry, `probe_spontaneous_crash_classification`
  meta with four mismatch discriminations; `run_process`/`classify_process`
  byte-unchanged); seven-flag battery [pending] NN/NN PASS with all 89 prior
  records stable on (script, flags, expected_exit, actual_exit, signature,
  verdict, error); separate fault-injection outer PASS; named non-author raw
  copied byte-identically once to `corpus/lessons/r61-<slug>-non-author.json`;
  scratch sabotage of the new arm rejects pre-terminal.]
- Per-axis verdict: [pending parent] — declared target coverage **improved**
  (CASES 77→79, full 89→92 by diff inspection; measured counts pending the
  named replay: first tracked spontaneous-signal classification rows vs 0
  before); depth unchanged; calibration unchanged (r60's bounded improvement
  already recorded; this round lands its tracked row). Retained UNKNOWN:
  signal origin unprovable from returncode — the rows prove exit shape, not
  sender. No push/merge.
```

Draft-B cautions: the wave-roster and settlement bullets are templates, not
observations — the parent must replace every `[pending]` with settled
numbers/commit hashes or omit the bullet. Structural facts I observed (row
names, diff shape, 77→79 CASES, projected 92) are marked "by inspection";
only the executor/verifier's measured runs make them evidence. I measured
77 CASES / sha `42104d95…` pre-change and the diff to `3bb29044…` post-change.

---

## Scribe evidence checklist for the tracked move (status at report time)

- [x] Baseline hashes + CASES count read (`observations.md`): runner
  `42104d95…31fb`, 77 CASES, env matches r60.
- [x] r60 claim chain confirmed in-repo: author + zero-disagreement verifier +
  adjudicator; third independent re-measurement observed in
  `r61-reviewer` scratch (same -6/-9/allowlist outcomes).
- [x] Executor tracked edit observed landed (read-only `git diff`): additive
  fixture + two CASES rows + one `expected_errors` entry + discrimination
  meta; `run_process`/`classify_process` byte-unchanged. Landing observed,
  passing NOT observed.
- [ ] Named non-author seven-flag replay: all prior 89 classifications stable
  plus the 3 new rows (projected 92/92); raw copied once to
  `corpus/lessons/`; fault-injection outer PASS.
- [ ] Sabotage: a crash arm whose `ERROR:` line is *not* the allowlisted one
  must still classify False (the landed meta self-checks this as
  `sigabrt_wrong_allowlist_rejects`; independent scratch sabotage still owed);
  SIGTERM -15 and timeout rejects unchanged.

## Bounded scope of this report

Drafts only — not a PASS, not a verdict, not an admission. I ran no runner and
no Godot; all classifier constants quoted are from the three named prior
measurements plus my read of `run_battery.py`. Signal-origin
indistinguishability, cross-host `-6` determinism, process-tree timeout, and
startup margin stay UNKNOWN as recorded. No commit, no tracked-file write, no
sibling-file write.
