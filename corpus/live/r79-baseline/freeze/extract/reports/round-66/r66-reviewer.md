# Round 66 reviewer report — non-author audit of round 65 committed state (host: devin)

Seat: reviewer (non-author). I authored none of the r65 content and none of
the in-flight r66 work. Every run below is a fresh execution by me into my
own scratch; no commit, no tracked fixture/runner edit, no LOG/SCORECARD
write, no verdict marking. Write scope: this report and
`corpus/live/r66-reviewer/` only.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
CPython `3.14.7`, Linux x86_64, `systemd --user` subreaper pid `1573` — same
host profile as the r65 receipts. Repo under audit:
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` (canonical; reached via
the `.shokunin/game-dev-2d` symlink from worktree
`~/Projects/prymeagnt/game-dev-2d`, whose own tree is clean at `fe4bbeaf`).

**LSP device status: unavailable.** This seat's toolset exposes no `lsp`
device; the single MCP server (`rea`) is a Ghidra binary-analysis toolset,
not an LSP — same as every prior round on this Python fixture. All checks are
direct execution, verbatim function extraction, and git-object comparison —
stronger than text grep for the claims under test; grep output is never
presented here as semantic proof.

HEAD under test: `2efaae2` "hygiene: untrack r63-baseline/tree". The r65
chain verified by `git log`: `414eb8e` (r65 work) → `44b6d2b` (r65
report-last: adjudication + lesson + verifier) → `b8a5a04` (r65 boundary
receipts) → `2efaae2` (hygiene). `git status` at audit close: **two tracked
modifications** — `M corpus/fixtures/descendant_pipe_probe.gd` (+65/−1) and
`M corpus/fixtures/run_battery.py` (+500/−0), the r66 author's diff which
**landed in-flight during this audit and was reviewed by direct execution**
(check 5 below); untracked = my `r66-reviewer/`, sibling r66 scratch
(`r66-author`, `r66-baseline`, `r66-scout`, `r66-boundary`,
`r66-simplifier`, and `reports/round-66/r66-baseline.md` — wave w6
in-flight, not mine), and the disclosed 117M
`r65-boundary/edge-verdicts.json` leftover.

## Tasked check 1 — fresh battery, ABSOLUTE `--runs` → 87/87 + 29 discriminations True — AGREE

```
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r66-reviewer/runs
```

- Exit `0`; final line `PASS battery`. stdout tee'd to
  `corpus/live/r66-reviewer/battery.stdout`: **88 `^PASS` lines, 0 `^FAIL`
  lines** — identical stdout shape to the r65 verifier's receipt.
- Receipt `corpus/live/r66-reviewer/runs/20261014T050233678898Z/verdicts.json`:
  `"verdict": "PASS"`, **87 results, 87 PASS / 0 FAIL** (81 CASES + 6 meta
  rows; bare invocation, no opt-in flags).
- `probe_descendant_error_spoof`: `verdict PASS`, mode
  `bounded_popen_dual_marker_gate_and_stream_split`, bound 3.0s,
  **29 discriminations, every value `True`** — including
  `hold_timeout_alone_rejects` (the simplifier-added 29th key) and the
  gate/stream-split keys (`gate_release_signature_accepted_while_live`,
  `gate_does_not_reject_forged_error_arm`, `forged_error_lands_on_stdout`,
  `genuine_error_lands_on_stderr`, `merged_classification_stream_blind`).

## Tasked check 2 — committed runner blob is the verified one — AGREE

- `git show HEAD:corpus/fixtures/run_battery.py | sha256sum` =
  `cd4824cc1a0199c2886ee8c5815ed5065757f50f6f59420ef79d56b4fd302d58`.
- `sha256sum corpus/fixtures/run_battery.py` (worktree) = **same value** —
  committed blob == worktree bytes == the `cd4824cc` blob the r65 verifier
  recorded on `414eb8e` (`r65-verifier.md` L13–15).
- `corpus/fixtures/descendant_pipe_probe.gd`: worktree sha256
  `37cf50156839502a1372746d31c3db6b8c835df734acf838025c1664f3262e59` ==
  `HEAD:` blob — the r65-committed fixture.
- The sibling r66-baseline frozen replay independently confirms the same
  shas on the `git archive HEAD` extraction (`reports/round-66/r66-baseline.md`,
  in-flight untracked).

## Tasked check 3 — r65 boundary edges reproduce — AGREE (3/3)

Driver `corpus/live/r66-reviewer/edge_repro.py`: `ast.get_source_segment`-
extracts `run_process` / `classify_process` / `classify_streams` **verbatim
from the committed runner** (segment sha16: `88728b23…` / `749fa060…` /
`a886968f…`) and execs them — production clauses under test, not a retype.
Fixture: byte-faithful copy of the committed r65-boundary edge fixture
(sha256 `dded5056b6c96e436c5a1d8f225c9c6b7355f7af2ee24ca8b92c81c5b78c510b`
== tracked `corpus/live/r65-boundary/proj_edge/`), run from my scratch so
`.godot/` writes stay in scope. Full receipt:
`corpus/live/r66-reviewer/edge-repro.json`; summary
`ALL_EDGES_REPRODUCED`, all six sub-checks true.

**(a) Newline-split evasion — reproduced.** `--spawn-errforge-newlinesplit`:
godot exit 0, error None, MARKER present, **classification `True`** while the
forged bytes are provably in the merged capture — output lines end `…, "ERR",
"OR: FORGED_DESCENDANT_ERROR newline-split diagnostic",
"DESCENDANT_PIPE_ERRFORGE write_ppid=1573"`; `error_lines == []`: the token
splits across a newline so no captured line contains `ERROR:` — the
line-local scan (`run_battery.py:174–176`) is blind to it. Controls detect:
`--spawn-errforge-split` (same token, no newline → reassembles contiguously)
→ `False`; stock `--spawn-errforge-release` → `False`.

**(b) Allowlist admittance — reproduced.** `--spawn-errforge-allowlisted`:
the descendant echoes `ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected
signature=JSON_PARSE_ERROR` post-death (`write_ppid=1573` ≠ `godot_pid`).
The **same captured record**: `allowed_errors=()` → `False` (rejects);
`allowed_errors=(save_corrupt_negative's entry,)` → `True` (admitted). The
verdict flips purely on string equality — the allowlist checks neither
origin nor timing, exactly the "preemptor row" the r66 axis-move names.

**(c) Reader-drain surface — reproduced.** Three measurements on
`--spawn-errforge-pipefull[-hold]` (post-death `yes`-pump):

- *Bounded pump drains fully under communicate*: `--pump-kb=512` through
  verbatim `run_process` → **all 524,542 bytes captured** (> 8× the 64KiB
  pipe capacity), 10,281 error lines, elapsed 0.536s, cls `False`. A >64K
  post-death write never blocks the draining reader.
- *Stalled reader → writer blocks*: Popen + 1.2s post-exit stall → the
  orphaned family is caught blocked in `/proc`: `sh` pid 1955821 `state=S
  wchan=do_wait ppid=1573`, `yes` pid 1955825 `state=S
  wchan=pipe_wait_writable`. On `communicate()` the full 524,542 bytes land
  and the family exits (`post_drain_family == []`). Nobody drains but the
  reader. (Enumeration is by the `FORGED_DESCENDANT_ERROR` cmdline token —
  `sh`+`yes` matched; the pipeline's `head` lacks the token and isn't in the
  sample, same filter shape as the r65 seat.)
- *Stall then close → SIGPIPE kills the writer*: the **unbounded**
  `--spawn-errforge-pipefull-hold` pump (`exec yes`) stalls blocked in
  `pipe_wait_writable` (`yes` pid 1956222, `ppid=1573`); closing both read
  ends without draining → family gone within 0.7s
  (`family_after_close == []`). Closing the pipes is the kill mechanism.

## Tasked check 4 — baseline-tree untrack lost no tracked receipts — AGREE

- `git show --name-status 2efaae2`: **34,520 deletions, every one under
  `corpus/live/r63-baseline/tree/`** — zero deletions outside that prefix
  (verified by `grep -v "r63-baseline/tree/"` → 0). Non-delete entries: adds
  `corpus/.gitignore` (`live/*/tree/`, `live/*/frozen/` now ignored),
  `r65-verifier/hold.out`, `r65-verifier/proj/*`; two rename detections fold
  tree paths into `r65-verifier/` receipts.
- Tracked count: `2efaae2^` 71,428 → HEAD **36,912** (net −33,694 vs the
  `61ec1c0` r65-baseline HEAD's 70,606 once the boundary/report-last adds
  are counted) — consistent with the sibling baseline's measurement.
- Pre-hygiene, `r63-baseline` tracked exactly `battery.stdout` + `tree/**`;
  at HEAD it tracks `battery.stdout` and `reports/round-63/r63-baseline.md` —
  **both receipts survive; only the regenerable extracted snapshot went
  away** (`git archive` at the pinned SHA reproduces it).
- **Zero `tree/`, `frozen/`, or `node_modules` paths remain tracked at HEAD**
  (`git ls-tree -r HEAD --name-only | grep -cE …` → 0), so a fresh
  `git archive HEAD` embeds no nested snapshot.
- Every `r*-baseline` dir still tracks its receipts (spot-verified:
  r30/r57/r58/r59 verdicts.json sets, r61–r65 `battery.stdout`; no file
  named `manifest`/`ledger` exists anywhere in the repo — those receipt
  files are the manifests/ledgers the brief refers to).

## Tasked check 5 — r66-author diff on classifier/run_process internals / prior rows — REVIEWED, CLEAN (measured on the diff)

The r66 author's tracked diff **landed in-flight during this audit** and I
reviewed the actual changed behavior, not just the stat. Worktree state at
report write (`git status --porcelain`, re-verified repeatedly):

- `M corpus/fixtures/descendant_pipe_probe.gd` — **+65/−1, additive
  arms**: `--spawn-allowforge` (post-death echo of `save_corrupt_negative`'s
  byte-exact allowlisted line — the preemptor-row arm), `--spawn-splitforge`
  (`ERR\n` + `OR:` newline-split evasion), `--spawn-seamforge` (unterminated
  `… ends in ERROR` stdout tail + `: SEAMFORGE phantom…` stderr head —
  concat fabrication), `--spawn-midlineforge` (pre-death fixed-offset splice
  into the signature's two `printraw` halves — dual-clause corruption).
  Post-death arms are reparenting-gated (`write_ppid=$pp`); `midline_forge`
  is deliberately pre-death (`write_ppid==godot_pid`). The single `−1` —
  `else: print(MARKER)` → `elif not midline_forge: print(MARKER)` — is
  semantic-preserving for every pre-existing arm.
- `M corpus/fixtures/run_battery.py` — **+500/−0 across three hunks, all
  additive**: `@@ -396` `expected_errors = ()` default; `@@ -453`
  `record["expected_errors"] = list(expected_errors)` (per-row allowlist
  annotation — verdict-inert; `passed` still derives from the unchanged
  `classify_process`; changes emitted row *shape* by +1 key on CASES rows,
  not any of the 7 verdict-bearing fields); `@@ -1539` **+498** =
  `probe_error_clause_surface` meta inserted after the error-spoof append
  and before the opt-in probe sections — pure insertion between existing
  statements.
- **`run_process` (:149), `classify_process` (:160–177), `classify_streams`,
  `run_process_streams`, `CASES` (:18–104), and all prior meta rows are
  byte-identical to the verified `cd4824cc` blob** — the hunk ranges do not
  intersect any of them (verified by hunk positions and by sha-diffing the
  function bodies I extracted and executed).
- **No prior-row mutation**: CASES tuples untouched; existing flags' behavior
  unchanged; the meta's census *reads* `results` rows (never mutates them)
  and appends exactly one new row.

### Measured on the diff (not just read)

- **Independent arm execution** (`author_arms_probe.py`, verbatim-extracted
  `run_process`/`classify_process` from the modified worktree runner —
  mid-edit sha `e419e7c5` per `author-arms.json`, function bodies identical
  to both `cd4824cc` and `76d37ace`): all six arm checks behave as
  declared —
  `AUTHOR_ARMS_BEHAVE_AS_DECLARED`. allowforge: `False` under `()`, `True`
  under the save entry; splitforge: `True` with `error_lines == []` while
  `ERR`/`OR:` lines sit in capture; **seamforge: `False` via the merged line
  `DESCENDANT_PIPE_SEAMFORGE tail ends in ERROR: SEAMFORGE phantom
  fabricated line` — a reject line present in neither stream** (the
  fabrication direction of the declared claim, now measured); midlineforge:
  `False`, `marker_whole_present=False`, spliced line
  `DESCENDANT_PIPE_PROBE: expected ERROR: DESCENDANT_PIPE_MIDLINE forged
  splice`, `write_ppid == godot_pid` (pre-death).
- **Full battery on the diff** (ABSOLUTE `--runs`, runner sha `76d37ace`,
  fixture `9ff5a9ae` — scratch copy inside the run dir sha-matches the
  worktree bytes): **88/88 PASS, 0 FAIL**
  (`runs-postdiff/20261014T051216915162Z/verdicts.json`), stdout 89 `^PASS`/
  0 `^FAIL`. New meta `probe_error_clause_surface`: **PASS, 34
  discriminations, all True** — preemptor row (reject-bare/absorb-matching/
  reject-foreign/counterfactual), 9/9 shape-matrix cells (exact/,-prefix/
  structured incl. tail-forge count==2 defeats and unanchored-prefix),
  newline-split evasion + contiguous-twin rejection, seam fabrication
  incl. `seamforge_line_in_neither_stream` and the split-stream control,
  midline dual-clause corruption + `counterfactual_defeated`, headline
  merged-line-presence, census integrity, and the within-run anchors
  (`detached_control_row_still_passes`,
  `prior_meta_rows_stable_29_discriminations`).
- **Prior-row stability on the diff**: 7-field tuple diff of the post-diff
  receipt vs my committed-state receipt — **87 common cases, 0 mismatches**;
  the only added row is `probe_error_clause_surface` (87→88, the declared
  additive shape).
- **Census data**: `rows_with_expected_errors=39`, `dead_entry_count=0`,
  `scan_clause_census` = 41 per-line `ERROR:` hits, 0 `SCRIPT ERROR:`, 0
  `Parse Error:`, 0 ObjectDB-leak lines — the (d) edge lands as carried
  data, gated only on coverage/consistency.
- **Fidelity check**: the meta's local `surface_allowed_error` is a
  clause-for-clause faithful retype of the production nested `allowed_error`
  (verified line-by-line); all load-bearing verdicts are re-derived through
  the real `classify_process`. `surface_run` reproduces the production
  consumer's record shape (bounded `communicate`, `stdout + stderr` merge
  order identical to `run_process`); `surface_split_run` correctly records
  stream-level non-existence the merged clause cannot see.

**Caveat — the diff is uncommitted and was still growing during this
audit** (fixture +65/−1 landed first, runner +2 → +500 across ~10 minutes).
If the author lands further tracked hunks after `76d37ace`/`9ff5a9ae`, this
check covers only the diff state I measured; my post-diff receipt
fingerprints exactly that state.

## Corroborating checks (beyond the tasked list)

- **0-mismatch tuple diffs vs all three r65 receipts** (7-field tuple
  `(script, flags, expected_exit, actual_exit, signature, verdict, error)`,
  keyed on `case`, meta rows on verdict): vs r65-baseline frozen receipt —
  86 common, **0 mismatches** (my only extra = `probe_descendant_error_spoof`;
  the 11 baseline-only rows are flag-gated opt-ins); vs r65-author full-flag
  receipt — 87 common, **0 mismatches**; vs r65-verifier receipt
  (`corpus/live/runs/20261014T043948860752Z/`, the shared gitignored
  `runs/` per `corpus/live/.gitignore`) — **87 common, 0 mismatches,
  identical case sets**. The committed surface is field-identical across
  four independent executions.
- **Sibling r66-baseline cross-check**: the in-flight frozen replay records
  the identical 87/87, 29/29-True, same runner/fixture shas — my live-tree
  numbers agree on every compared field.
- **Process hygiene**: post-run `pgrep` finds no leaked `descendant_pipe` /
  `FORGED_DESCENDANT`/`SEAMFORGE`/`SPLITFORGE`/`ALLOWFORGE`/`MIDLINE`
  processes from my runs (my C3 close killed the unbounded `yes` via
  SIGPIPE; bounded arms self-exited; the meta's orphan reaper ran). Stray
  headless godot on the host during the audit belonged to sibling seats —
  game-dev-3d `r75-simplifier` and this lane's own `r66-boundary`
  (`proj_r66`, running the same stock fixture) — per lane precedent, data
  not evidence.
- **r65 LOG/SCORECARD committed state intact**: `LOG.md:621–626` carries the
  wave/seat/author/verifier/ADMIT entries; `SCORECARD.md:34` the verifier
  AGREE 6/6 + ADMIT summary — consistent with `44b6d2b`'s diff.

## Findings by severity

**No actionable defect found in scope.** Every tasked check agrees.

- *Cosmetic (carried-forward, disclosed):* `corpus/live/r65-boundary/
  edge-verdicts.json` (117M) remains as untracked scratch — deliberately
  excluded from `b8a5a04` as oversized, disclosed in that commit message and
  the r65 boundary report. Untracked, so outside tracked state.
- *Observation (not a defect):* the unbounded-pump `MemoryError` leg of the
  r65 edge-5 surface (uncapped `captured` bytearray in `gated_signature_run`,
  ~21 GB/s pump under `RLIMIT_AS=5 GiB`) was not re-run — it is a deliberately
  memory-hostile measurement the r65 seat already pinned with receipts; my
  reproduction covers the writer-blocks / drain-completes / close-SIGPIPE
  mechanics of the same surface.

## Disagreements

None on any tasked claim. The r65 committed state
(`414eb8e` + `44b6d2b` + `b8a5a04` + `2efaae2`) survives fresh re-execution:
87/87 bare battery, 29/29 discriminations True, committed runner
byte-identical to the `cd4824cc` verified blob, all three boundary edges
reproduced against verbatim production code, and the hygiene untrack
confined to the regenerable tree with every receipt retained. The r66
tracked diff observed during this audit was reviewed by direct execution:
additive fixture arms +65/−1 and a +500/−0 runner insertion (record
annotation + `probe_error_clause_surface`) leave `run_process`,
`classify_process`, CASES and prior meta rows byte-identical; my own
battery on the diff runs 88/88 with the new meta 34/34-True and the prior
87 rows 0-mismatch — the declared additive shape, measured not just read.

## Residual risk / verification gaps

- Single host, single battery pass by me; `ppid=1573` is this host's
  `systemd --user` subreaper — `write_ppid != godot_pid` is the
  host-agnostic clause, and my edge run shows the same subreaper constant.
- Edge enumeration is cmdline-token filtered: the pipeline `head` process in
  C2 isn't in the blocked-family sample (its cmdline lacks
  `FORGED_DESCENDANT_ERROR`); the `sh`/`yes` blocked evidence is unaffected.
- The unbounded-pump OOM leg is carried from the r65 boundary receipts
  rather than re-measured (see observation above).
- Concurrent wave w6: sibling r66 seats (baseline/scout/boundary/simplifier)
  and a game-dev-3d r75 seat ran on this host/repo during the audit; my
  receipt is nevertheless 0-mismatch vs three r65 receipts, so no
  interference is observable in the record.
- Not re-probed (carried UNKNOWNs): stdout-under-`classify_streams`
  evasion, descendant chains >1 deep, exported builds, non-POSIX.
- **The r66 author diff is uncommitted and was still growing during the
  audit** (fixture +65/−1 first, then runner +2, then +500). My check-5
  measurement fingerprints runner `76d37ace` + fixture `9ff5a9ae`; any
  hunk landing after those bytes is outside this review's measured state.
  The diff is also reviewed here as *uncommitted* work — committed-state
  verification belongs to the wave's verifier once the author commits.
- The r66 declared falsifiable claim is **consistent with everything I
  measured**: on committed code I reproduced evasion + admittance + drain
  mechanics (edge repro), and on the author's diff I independently
  measured the *fabrication* direction (seam line in neither stream yet
  reject-bearing post-merge) plus all four arms behaving as declared and
  88/88 + 34/34 on a full battery. I did not audit the discriminations'
  long-run flakiness (single pass) nor re-derive the census table cell by
  cell beyond the checks stated.

Recommendation (non-binding; adjudication belongs to the judge): the r65
ADMIT stands — every checkable claim survives fresh re-execution on
committed `2efaae2`. The in-flight r66 diff matches the declared
axis-move's additive shape and shows no classifier/internal mutation or
prior-row change on the bytes I measured; nothing to flag, with the
uncommitted-diff caveat above.

No commit, no tracked-file write, no sibling-lane contact, no subagent
dispatch. Artifacts: `corpus/live/r66-reviewer/runs/20261014T050233678898Z/`
(committed-state battery receipt), `runs-postdiff/20261014T051216915162Z/`
(battery on the r66 author diff), `battery.stdout`, `battery.stderr`,
`battery-postdiff.stdout`, `battery-postdiff.stderr`, `edge_repro.py`,
`edge-repro.json`, `author_arms_probe.py`, `author-arms.json`,
`proj_edge/`, `proj_stock/`, `proj_author_diff/` (scratch copies).
