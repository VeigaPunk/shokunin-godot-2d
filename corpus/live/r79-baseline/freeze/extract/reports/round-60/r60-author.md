# Round 60 author report — spontaneous-crash calibration probe (host: devin)

## Scoped move and source

SCORECARD `planned` names calibration gaps: "direct-child Linux SIGTERM and one
real Godot timeout are probed; **spontaneous crashes**, process-tree timeout,
startup-margin robustness, and other diagnostic shapes remain unprobed." r21
probed a *harness-sent* SIGTERM (`crash_exit_probe.gd`, return -15); r22/r26
probed one real timeout (direct child only). The first listed unprobed shape —
a process that dies by a signal **it** raised, not one the harness sent — is
the round-60 move. Author is scratch-only: no tracked fixture/runner edit
(integration belongs to a later executor + named non-author replay).

## What ran (exact invocations)

1. Devin-host seven-flag baseline replay (author raw, not non-author):
   `python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot
   --runs .shokunin/game-dev-2d/corpus/live/runs/round-60/battery
   --probe-failing --probe-unrelated-error --probe-export-launch
   --probe-godot-error --probe-stream-attribution --probe-crash-exit
   --probe-timeout` →
   `battery/20261013T164941106461Z/verdicts.json` **PASS 89/89**
   (78 ordinary + 2 mutants + 9 opt-in), verbatim stdout `full.stdout`.
   Field-diff vs `corpus/lessons/r59-audio-non-author.json` over
   `(script, flags, expected_exit, actual_exit, signature, verdict, error)`:
   **0 mismatches across all 89 rows** — battery replays byte-exact on this host.
2. Separate `--fault-injection` →
   `fault-injection/20261013T165157218085Z/fault-verdicts.json` outer **PASS**
   (inner hang/unrelated-error FAIL as designed), stdout `fault.stdout`.
3. Scratch spontaneous-crash probe: `scratch-probe/proj/spontaneous_crash_probe.gd`
   (marker `SPONTANEOUS_CRASH_PROBE: expected signature`, flags
   `--spontaneous-crash` / `--spontaneous-sigkill`) driven by
   `scratch-probe/drive_probe.py`, which `ast`-extracts `run_process` +
   `classify_process` **verbatim** from `run_battery.py` (sha256
   `42104d95af5fcb98d742c495ee4562ea0c579c49d9ca22d11755302f685c31fb` — same as
   r59 verifier) and execs them; no transcription. Raw merged outputs saved
   per arm (`*.stdout`); structured result
   `scratch-probe/spontaneous-crash-verdicts.json` → meta **PASS**.

## Byte-exact measured constants (Godot 4.7.2.stable.arch_linux.ed1daf0bf, Linux 7.2.3-arch1-3 x86_64, Python 3.14.7, RLIMIT_CORE unlimited)

| arm | actual_exit | error | marker | classifier | stderr shape | elapsed |
|---|---|---|---|---|---|---|
| accept (no flag) | 1 | None | yes | **True** | none | 0.617 s |
| `OS.crash("r60 spontaneous crash probe")` ×2 | **-6 (SIGABRT)** | None | yes | **False** | `ERROR: r60 spontaneous crash probe` + `at: crash (core/core_bind.cpp:349)` + GDScript backtrace at `spontaneous_crash_probe.gd:15` + `handle_crash: Program crashed with signal 4` + C++ backtrace | 2.035 s / 1.430 s |
| `OS.kill(OS.get_process_id())` | **-9 (SIGKILL)** | None | yes | **False** | empty | 0.581 s |

Measured nuance: `OS.crash` internally raises **SIGILL (signal 4)** — the engine
crash handler reports "signal 4", dumps both backtraces, then the process dies
by **SIGABRT**; the parent-visible returncode is -6 on both runs (deterministic).
The marker is captured on stdout in every arm (Godot `print` flushes pre-crash).
No `core.*` file landed in scratch (systemd coredump path; RLIMIT_CORE recorded
in the JSON).

Supplemental classifier measurements (same extracted `classify_process`, same
captured outputs — no rerun): expected `-9` on the SIGKILL arm → **True**;
expected `-6` on the crash arm → **False** (the crash's own `ERROR:` line is an
unallowlisted unrelated error) → **True** once that exact line is allowlisted.
So a tracked integration needs **zero runner changes** for a SIGKILL-expected
row, and only an `expected_errors` allowlist entry for the `OS.crash` row.

## Per-axis claimed verdict (author claim; named non-author replay still due)

- **calibration — improved-in-evidence (candidate)**: a real Godot 4.7.2
  spontaneous-abnormal-exit contrast exists and the production classifier
  cleanly rejects both signal exits despite the emitted marker — a distinct
  third outcome vs clean nonzero exit (code>0) and vs timeout (error set,
  code=None). UNKNOWN until a tracked fixture/case + named non-author replay
  admits it; claim here is scratch evidence only, author run not non-author.
- **coverage — unchanged**: 89 tracked rows, 0 new cases authored.
- **depth — unchanged**: no new mechanic surface.
- Host-migration evidence: devin host replays the r59 non-author battery
  byte-exact (89/89, 0 field deltas) — baseline is portable, so any later
  verifier divergence is attributable to the change, not the host.

## UNKNOWNs / adverse retained

- Python `returncode` carries signal number, **not origin**: a self-SIGKILL and
  a harness/OM killer SIGKILL are indistinguishable to this classifier. The
  `OS.crash` arm carries intrinsic attribution only via its own `ERROR:` line +
  GDScript backtrace pointing at the script line — output evidence, not
  syscall evidence. A tracked row asserting `-9`/`-6` proves the *exit shape*,
  not who sent it.
- No core-dump artifact capture, no signal beyond SIGABRT/SIGKILL measured,
  no exported-build crash behavior, no process-tree/descendant cleanup
  (still the natural next-round candidate), no startup-margin claim, Linux
  x86_64 headless only, not production crash handling.
- `timeout`-wrapped micro-measure files `crash.{stdout,stderr}`,
  `sigkill.{stdout,stderr}` retained as setup telemetry (bash reported 134/137);
  canonical captures are the driver `*.stdout` under `subprocess.run`.

## Artifact inventory (all under `corpus/live/runs/round-60/`, gitignored)

- `battery/20261013T164941106461Z/verdicts.json` (sha256 `9905553c…`) + `full.stdout` (sha256 `1c68d6ab…`)
- `fault-injection/20261013T165157218085Z/fault-verdicts.json` (sha256 `57f2dca0…`) + `fault.stdout`
- `scratch-probe/spontaneous-crash-verdicts.json` (sha256 `9694988b…`), `drive_probe.py` (`689e004b…`), `proj/spontaneous_crash_probe.gd` (`16e31617…`), per-arm raw `*.stdout`, micro-measure `crash.*`/`sigkill.*`

No commit, no tracked-fixture mutation, no LOG/SCORECARD write; verdict
adjudication and any tracked integration are non-author and follow.
