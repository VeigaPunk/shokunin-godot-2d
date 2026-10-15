# Round 61 critic report — falsification of the spontaneous-crash rows (host: devin)

Seat: critic, lane `game-dev-2d`. Scope: attack the landed r61 diff —
`corpus/fixtures/spontaneous_crash_probe.gd` (new) + `run_battery.py` hunks
(2 CASES rows, 1 `expected_errors` entry, 1 `probe_spontaneous_crash_classification`
meta). All scratch under `corpus/live/r61-critic/`; no tracked writes, no commits.

## Method

`corpus/live/r61-critic/drive_mutants.py` `ast`-extracts `run_process` +
`classify_process` **verbatim** from the tracked runner and execs them (same
method as r60 author/verifier — no transcription). Runner sha at extraction
`3bb2904497dfeb774d8d4a9b8c5f8b39ddf1e0ba66bde53599e17eafe3bcec5d` (post-edit);
extracted `classify_process` sha `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`,
`run_process` sha `88728b2303f64fc48b094d358f0a217ae7b07aaf85b446b014e35c31d76207c5`.
Mutant fixture `proj/r61_critic_probe.gd` (sha `f1d5f7bf…`) in scratch project
`proj/`. Every arm: `godot --headless --path <proj> --script res://r61_critic_probe.gd -- <flag>`,
12 s timeout, per-arm raw stdout saved `critic_<case>.stdout`, structured result
`r61-critic-sabotage-verdicts.json` (sha `d0992e65…`).

## Landed-diff check (independent re-run of the promoted fixture)

Copied the landed `spontaneous_crash_probe.gd` into my scratch project and ran
its three arms through the extracted classifier (`landed-row-verification.json`,
sha `b4ff46be…`):

| arm | exit | cls under landed row | verdict |
|---|---|---|---|
| `--spontaneous-crash` | −6 SIGABRT, one `ERROR: r60 spontaneous crash probe` | (−6, allowlist) → **True**; (−9) → False; (−6, no allowlist) → False; (−6, wrong allowlist) → False | positive arm + all 4 meta discriminations hold |
| `--spontaneous-sigkill` | −9 SIGKILL, zero ERROR lines | (−9) → **True**; (−6) → False | holds |
| clean | 1 | False under −6 and −9 | holds |

The diff is internally consistent: the meta row's four discriminations
(`-9` mismatch, missing allowlist, wrong allowlist, `−6` on the −9 arm) all
reject. The `expected_errors` entry uses the **exact-match** spelling
`("ERROR: r60 spontaneous crash probe",)` — correct choice; my forge test
(below) shows the comma-prefix spelling would fail the genuine arm itself.

## Counterexamples — what SLIPS THROUGH (admitted under the landed row semantics)

| arm (scratch fixture + flag) | mechanism | observed exit | marker | `cls` under landed (−6/−9) shape |
|---|---|---|---|---|
| `ext_abrt_no_error` | child `OS.create_process("/usr/bin/kill", ["-6", pid])`, then await | **−6 SIGABRT** | yes | **True** — even with `allowed_errors=()` |
| `ext_ill` | child `kill -4` (SIGILL — the very signal `OS.crash` raises internally) | **−6 SIGABRT** (handler banner "signal 4" then abort) | yes | **True** under every allowlist incl. none |
| `ext_segv` | child `kill -11` (SIGSEGV → crash handler → abort) | **−6 SIGABRT** | yes | **True** under every allowlist incl. none |
| `ext_abrt_forged_marker` | `printerr("ERROR: r61 critic abort")` (exact allowlisted text) + child `kill -6` | **−6 SIGABRT** | yes | **True** under exact-match allowlist |
| `ext_kill9` | child `kill -9` | **−9 SIGKILL** | yes | **True** under the `crash_self_sigkill` (−9) row |

Key structural fact measured, not assumed: **the allowlist *forgives* the
crash's `ERROR:` line — it never requires it.** `ext_abrt_no_error`, `ext_ill`,
`ext_segv` emit zero `ERROR:` lines, carry the signature, die −6, and classify
True even with an empty allowlist. The −6 admission surface is "exit-shape −6 +
marker + no unallowlisted ERROR lines," so three distinct non-`OS.crash`
delivery routes forge it. `ext_abrt_forged_marker` shows the ERROR text itself
is forgeable by `printerr`. `ext_kill9` proves the same origin-blindness on
the −9 row: an external SIGKILL is indistinguishable from `OS.kill(self)`.
Exit-code forgery is NOT reachable: `quit(134)` produced exit 1, not 134 or −6
(Godot normalizes the code); a real signal is required, but any fixture can
deliver one via `OS.create_process`.

This is r60's retained UNKNOWN ("signal origin unprovable from returncode")
made concrete. The author's bounded_claim discloses it; I file it as a
**demonstrated slip-through**, not a hidden defect — see correction below.

## What REJECTS as designed

| arm | observed | result |
|---|---|---|
| `ext_abrt_extra_error` (`printerr` extra `ERROR: unrelated injected diagnostic` + external −6) | −6 | **False** — the exact-match allowlist does NOT blanket-bless; the extra ERROR line stays unrelated |
| `forge_prefix_line` (`printerr("ERROR: r61 critic abort, EXTRA_UNRELATED_CONTENT")` + real `OS.crash`) | −6 | **False** under landed exact-match; also proves comma-prefix spelling `("ERROR: r61 critic abort,",)` would fail the genuine arm (`os_crash_baseline` under prefix → False) — exact-match is the only working spelling, and the executor used it |
| `crash_before_marker` (`OS.crash` before `print(MARKER)`) | −6, marker absent | **False** — crash without signature rejects |
| `crash_diff_msg` (`OS.crash("a different spontaneous abort")`) | −6 + unallowlisted ERROR | **False** — a genuine spontaneous abort with different text is still unrecognized: the row is exemplar-specific (one canned crash message), not "spontaneous crashes" generally |
| `ext_term` (external `kill -15`, r21 harness-SIGTERM shape) | −15 | **False** under −6 (True under −15) — prior SIGTERM classification untouched |
| `self_kill_sigkill` under −6 | −9 | **False** — expected-mismatch still rejects |
| `exit_134` (`quit(134)`) | exit **1** | **False** — cannot reach −6 without a signal |
| `assert_fail` (`assert(false)`) | **TIMEOUT** (12 s), `SCRIPT ERROR: Assertion failed.` | **False** — headless assert hangs and sets `error`; assert cannot produce −6 |
| `stack_overflow` (infinite `_recurse`) | exit **1**, `SCRIPT ERROR: Stack overflow…` + `ERROR: Stack underflow! (Engine Bug)` spam | **False** — another non-crash path confirmed unable to reach −6 |
| `printerr_clean_exit0` (`printerr` allowlisted line + `quit(0)`) | exit **1** (error state perturbs script-mode exit code) | **False** — code mismatch + ERROR unallowlisted |
| `accept_clean_exit1` | 1 | **False** under −6 and −9 |

## Per-attack-axis verdicts

- **(a) signal-origin indistinguishability — CONFIRMED slip.** Three external
  signal routes (−6, −4→−6, −11→−6) and a forged-marker variant admit under the
  −6 row; external `kill -9` admits under the −9 row. Two of the −6 forgeries
  need no ERROR content at all, so the allowlist is not the admission gate —
  exit-shape + marker is. Row name `crash_spontaneous_sigabrt` asserts a
  spontaneity the measurement cannot verify; the meta `bounded_claim`
  ("signal origin unprovable from returncode") discloses exactly this.
- **(b) unrelated-ERROR blessing — clean under the landed spelling.** Extra or
  prefix-extended ERROR lines still reject; `expected_errors` is per-case keyed
  so no cross-case blessing exists. The one trap — comma-suffix form — was
  avoided; measured that it would have broken the genuine arm.
- **(c) mutants — reject correctly.** Crash-without-marker and
  crash-with-different-message both reject; the latter bounds coverage to the
  single exemplar, consistent with the declared claim. Prior classifications
  (SIGTERM −15, timeout/error-set, expected-mismatch) untouched: zero
  regression observed.

## Impacted axes

- **coverage**: the claimed +2 rows / +1 meta is real (92 rows) — but the −6
  row's demonstrated admission surface is wider than "spontaneous crash":
  any marker-carrying −6 death, spontaneous or externally delivered. Fixable
  boundary wording, not a false measurement of the fixture it names.
- **calibration**: unchanged claim holds — no classifier edit; discriminations
  exercise existing semantics only.
- **harm**: none measured; 4/4 rejections + prior-row stability consistent
  with the author's 0-mismatch diff vs `r59-audio-non-author.json`.

## Smallest safe correction (for the canonical judge to weigh)

1. The meta already discloses origin-blindness. To shrink the forged-admission
   surface by one clause: require the crash's own ERROR line to be *present*
   rather than merely forgiven — e.g. add to `crash_meta_ok`:
   `"ERROR: r60 spontaneous crash probe" in "\n".join(sigabrt["output"])`.
   That rejects the `ext_abrt_no_error`/`ext_ill`/`ext_segv` forgeries (all
   emit zero ERROR lines). It cannot reject `ext_abrt_forged_marker` — origin
   remains unprovable — so it tightens but does not close the hole.
2. Keep the verdict wording at "exit-shape + marker classification"; the row
   names already imply more than is measured.

Tradeoff vs defect: the slip-through is a **disclosed tradeoff** (bounded_claim
says it plainly), not a hidden regression — provided the parent/verifier keeps
the claim at exit-shape granularity and does not upgrade "spontaneous" to a
provenance assertion. A verdict that claims the row *detects spontaneous
crashes* would be falsified by `ext_abrt_no_error` et al.; a verdict claiming
the row *classifies the −6/+marker exit shape* is not.

## Artifacts (all under `corpus/live/r61-critic/`)

- `drive_mutants.py` (sha `dc6bb716…`), `r61-critic-sabotage-verdicts.json`
  (sha `d0992e65…`), `landed-row-verification.json` (sha `b4ff46be…`),
  `proj/r61_critic_probe.gd` (sha `f1d5f7bf…`, copy of landed
  `spontaneous_crash_probe.gd` beside it), per-arm raw `critic_*.stdout`
  (20 captures), `proj/project.godot`.
- Runner sha `3bb29044…` (post-edit); extracted `classify_process` sha
  `749fa060…` identical before/after the edit — results apply to landed code.

No commit, no tracked-file write, no sibling-lane contact.
