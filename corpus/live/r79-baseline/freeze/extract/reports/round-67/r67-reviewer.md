# Round 67 reviewer report — non-author audit of round 66 committed state (host: devin)

Seat: reviewer (non-author). I authored none of the r66 content and none of
the in-flight r67 work. Every run below is a fresh execution by me into my
own scratch; no commit, no tracked fixture/runner edit, no LOG/SCORECARD
write, no verdict marking. Write scope: this report and
`corpus/live/r67-reviewer/` only.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
CPython `3.14.7`, Linux x86_64, `systemd --user` subreaper pid `1573` —
same host profile as the r66 receipts. Repo under audit:
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` (canonical; reached via
the `.shokunin/game-dev-2d` symlink from worktree
`~/Projects/prymeagnt/game-dev-2d`, whose own tree sits at the `fe4bbeaf`
extract commit and is clean).

**LSP device status: unavailable.** This seat's toolset exposes no `lsp`
device; the single MCP server (`rea`) is a Ghidra binary-analysis toolset,
not an LSP — same as every prior round on this Python fixture. All checks
are direct execution, verbatim `ast` function extraction, and git-object
comparison — stronger than text grep for the claims under test; grep output
is never presented here as semantic proof.

HEAD under test: `4a4def9` "r66 report-last". The r66 chain verified by
`git log`: `cb84d0a` (r66 work: 4 surface arms + `probe_error_clause_surface`
meta + reparent_gate extraction) → `4d938b2` (hygiene ignore) → `4a4def9`
(report-last: verifier AGREE 5/5 + scribe/boundary + lesson + LOG/SCORECARD).
`git status --porcelain`: the r67 author's tracked diff **landed in-flight
during this audit** — `M corpus/fixtures/run_battery.py` (+263/−2 at
observation, worktree sha `3d5b0721…`, may still be growing) and `M
corpus/fixtures/stream_attribution_probe.gd` (+56/−2, sha `dc0b0d5c…`),
consistent with the declared per-stream meta arm; plus untracked sibling
r67 scratch (`r67-author`, `r67-baseline`, `r67-boundary`, `r67-critic`,
`r67-scout`, `r67-scribe`, `r67-simplifier`, `corpus/fixtures/__pycache__/`,
`reports/round-67/`) and my own `r67-reviewer/`. **Every measurement in
this report was taken on the committed r66 blobs** — the battery's own
scratch copy sha-matches the committed fixture (`descendant_pipe_probe.gd`
`92a40d70`, `stream_attribution_probe.gd` `97143ad3` == `HEAD:` blobs,
inside `runs/20261014T095231662268Z/scratch/`); the runner was `76d37ace`
== HEAD at battery launch; the worktree's tracked mtime (06:57:38 local)
postdates my `verdicts.json` write (06:54:02 local) by ~3.5 min; and all
`git show HEAD:` extractions read committed bytes regardless of worktree
state. Review of the in-flight r67 diff itself belongs to the wave's
verifier; nothing here asserts on it.

## Tasked check 1 — committed battery on HEAD, ABSOLUTE `--runs` → 88/88 + 34/34 — AGREE

```
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r67-reviewer/runs
```

- Exit `0`; final line `PASS battery`. stdout tee'd to
  `corpus/live/r67-reviewer/battery.stdout`: **89 `^PASS` lines
  (88 rows + banner), 0 `^FAIL`** — identical stdout shape to the r66
  author's flagless receipt.
- Receipt
  `corpus/live/r67-reviewer/runs/20261014T095231662268Z/verdicts.json`:
  `"verdict": "PASS"`, **88 results, 88 PASS / 0 FAIL** (81 CASES + 7
  unconditional meta rows; bare invocation, no opt-in flags).
- `probe_error_clause_surface`: `verdict PASS`, mode
  `bounded_popen_surface_arms_plus_allowlist_census`,
  **34 discriminations, every value `True`** — incl. the preemptor triple
  (reject-bare / absorb-matching / reject-foreign), all 9 shape-matrix
  cells, splitforge evasion + contiguous-twin rejection, seamforge
  fabrication incl. `seamforge_line_in_neither_stream`, midlineforge
  dual-clause corruption + `counterfactual_defeated`, census integrity,
  and the within-run anchors (`detached_control_row_still_passes`,
  `prior_meta_rows_stable_29_discriminations`).
- Census data on my run: `rows_with_expected_errors=39`,
  `dead_entry_count=0`, `scan_clause_census` = 41 `ERROR:` per-line hits,
  0 `SCRIPT ERROR:`, 0 `Parse Error:`, 0 ObjectDB-leak — the (d) edge
  lands identically to the r66 receipts.

### Prior-row stability — 7-field tuple diff, 0 mismatches

Keyed on `case`, tuple `(script, flags, expected_exit, actual_exit,
signature, verdict, error)` vs the r66-author flagless receipt
`corpus/live/r66-author/runs/20261014T051140112142Z/verdicts.json`:
**88 common cases, 0 mismatches, identical case sets** (no added/missing
rows). The committed r66 surface is field-identical across independent
executions.

## Tasked check 2 — the 4 surface arms behave as declared — AGREE

From my fresh receipt's `probe_error_clause_surface.arms`:

| arm | exit | error | sig | write_ppid | inner cls | reading |
|---|---|---|---|---|---|---|
| `surface_allowforge` | 0 | None | True | `1573` ≠ godot `2561266` | False bare | post-death forged **allowlisted** line captured; rejects bare, absorbed under the matching entry, rejects under foreign (F/T/F per discriminations) |
| `surface_splitforge` | 0 | None | True | `1573` ≠ godot `2561807` | **True** | `error_lines == []` while `ERR`/`OR: DESCENDANT_PIPE_SPLITFORGE …` bytes are in the record — newline-split **evades** the line-local scan |
| `surface_seamforge` | 0 | None | True | `1573` ≠ godot `2562531` | False | merged `error_lines` carries `DESCENDANT_PIPE_SEAMFORGE tail ends in ERROR: SEAMFORGE phantom fabricated line` — a reject line present in neither stream |
| `surface_midlineforge` | 0 | None | **False** | `2563240` **== godot** | False | spliced line `DESCENDANT_PIPE_PROBE: expected ERROR: DESCENDANT_PIPE_MIDLINE forged splice`; signature substring destroyed; `write_ppid == godot_pid` proves the write was **pre-death** |

The paired split-PIPE run corroborates seam geometry:
`seam_split_run.raw_stdout_lines[-1]` == `DESCENDANT_PIPE_SEAMFORGE tail
ends in ERROR` (unterminated tail), `raw_stderr_lines[0]` ==
`: SEAMFORGE phantom fabricated line`, and the fabricated line is absent
from both stream line-sets yet present in the concat (`midline_spliced_line`
recorded verbatim). All four arms match the r66 author report's declared
table cell-for-cell.

## Tasked check 3 — `reparent_gate` extraction — VERIFIED byte-identical

Commit `cb84d0a` extracted the three inline reparenting-gate literals into
one `var reparent_gate` at `descendant_pipe_probe.gd:131-132` and routed
every gated arm through it. I evaluated both blob versions' argv
construction mechanically (GDScript string concat over literals,
`str(OS.get_process_id())`, `reparent_gate`, per-arm tail vars — driver
`corpus/live/r67-reviewer/reparent_gate_argv_check.py`, output
`reparent_gate_argv_check.out`):

- Pre-extraction (`cb84d0a^`) had 4 `OS.create_process` sites; HEAD has 8.
- Every pre-existing arm produces **byte-identical argv post-extraction**:
  `--spawn-hold`, `--spawn-forge-hold` (`tail="; sleep 6"`),
  `--spawn-forge-release` (`tail=""`), `--spawn-errforge-hold`
  (`err_tail="; sleep 6"`), `--spawn-errforge-release` (`err_tail=""`) —
  all 5 flag combos identical under both tail expansions; `--spawn-detach`
  unchanged literal. (The "x8" in the commit message counts the 8
  post-extraction `create_process` sites / 8 gated flag combos; byte
  identity is only falsifiable on the 5 pre-existing combos — all pass.)
- New gated arms `--spawn-allowforge` / `--spawn-splitforge` /
  `--spawn-seamforge` prepend the same `reparent_gate` string
  (post-death writes: gate holds the descendant's `sh` until its ppid
  leaves `godot_pid`, then it echoes `write_ppid=$pp`).
- `--spawn-midlineforge` deliberately does **not** use the gate — its argv
  is `sleep 0.08; read pp; printf MIDLINE_ERROR; echo write_ppid=$pp`, a
  fixed-offset **pre-death** write (`write_ppid == godot_pid` measured on
  my run), matching the documented design.
- The single `−1` fixture line `else: print(MARKER)` →
  `elif not midline_forge: print(MARKER)` is semantics-preserving for
  every pre-existing flag combo (midline arm did not exist pre-diff).

## Tasked check 4 — classifier-divergence documentation — VERIFIED accurate on committed code

The `classify_process`/`classify_streams` divergence is documented in
tracked r66 artifacts: `reports/round-66/r66-boundary.md` edge-4 table
(:171–193, both-direction cross: `streams∧¬merged` and `¬streams∧merged`
both realizable), streams-asymmetry note (:165–169, no structured branch),
divergences list (:263–289); `r66-scout.md` (:94, stderr-lines shape);
`r66-scribe.md` (dead allowlist machinery under sole caller
`allowed_stderr=()`); `SCORECARD.md:41` and `LOG.md:631–636`. The r67
brief's "documented but contract unmapped" is accurate: the divergence is
measured and written down, but no battery row pins per-stream verdicts —
the only `classify_streams` call site is the opt-in stream-attribution
probe (`:2219`).

I re-derived the documented divergence on **committed** code by
`ast.get_source_segment`-extracting `classify_process` (segment sha16
`749fa0607e77`) and `classify_streams` (`a886968fd3ac`) from
`git show HEAD:corpus/fixtures/run_battery.py` — both shas match the r66
lesson (`corpus/lessons/r66-rejection-clause-surface.md:19-21`) — and
exec'd them on synthetic streams (receipt
`corpus/live/r67-reviewer/divergence_check.json`):

| input shape | classify_streams | classify_process | matches doc |
|---|---|---|---|
| `ERROR:` line on **stdout** only, sig on stdout | **True** | **False** | yes — the asked asymmetry: stdout-carried errors are invisible to streams (the r67 claim's premise) |
| `ERROR:` line on stderr, sig on stdout | False | False | yes — stderr-carried rejects under both |
| signature on **stderr** only | **False** | **True** | yes — opposite direction: streams requires sig in stdout |
| non-`ERROR:` stderr chatter | **False** | **True** | yes — streams' any-stderr-line whitelist vetoes |
| `SCRIPT ERROR:` on stdout | False | False | yes — blob clauses scan both streams (:185–188) |
| allowlisted `ERROR:` on stderr | True | True | yes — per-call allowlist, exact entry |

The code at `:179–208` confirms the mechanism the docs describe: signature
must appear in **stdout** (`:183`); `SCRIPT ERROR:`/`Parse Error:` checked
in **both** streams (`:185–188`); the error scan iterates **stderr lines
only** (`:189–207`) with a per-line allowlist that has no structured
branch (`:192–198`) — stdout `ERROR:` content is never scanned, so a
stdout-carried `ERROR:` is PASS-shaped under `classify_streams` where the
merged `classify_process` rejects. Documentation is accurate and the r67
axis-move's declared divergence direction is confirmed on committed code.

## Corroborating checks

- **Committed blobs == worktree bytes at battery-launch time**:
  `sha256sum` worktree == `git show HEAD:` for both files at launch —
  runner `76d37ace4b0b…`, fixture `92a40d70e31d…` (matching the r66
  lesson's recorded shas); the battery's per-run scratch copy
  independently sha-matches HEAD blobs (see header caveat). The worktree
  `run_battery.py`/`stream_attribution_probe.gd` bytes *now* differ —
  that is the in-flight r67 author diff, not drift in the audited commit.
- **r66 LOG/SCORECARD committed state intact**: `LOG.md:628–636` carries
  the round-66 wave/author/verifier/ADMIT entries (work commit `cb84d0a`);
  `SCORECARD.md:40–44` carries the r66 coverage/depth verdicts and
  adjudication line — consistent with `4a4def9`'s diff.
- **Process hygiene**: post-run `pgrep` finds no leaked
  `descendant_pipe`/`ALLOWFORGE`/`SPLITFORGE`/`SEAMFORGE`/`MIDLINE`
  processes from my run (the meta's orphan reaper ran; arms self-exit).
  Headless godot processes on the host during the audit belonged to the
  sibling lane `game-dev-3d` r76 seats — data, not evidence.
- **Sibling r67 wave in flight**: `r67-baseline/{frozen,runs}` etc. are
  sibling seats' untracked scratch — not mine, not audited.

## Findings by severity

**No actionable defect found in scope.** Every tasked check agrees.

- *Observation (not a defect):* the "argv byte-identical x8 arms" phrasing
  in `cb84d0a`'s message counts post-extraction create_process sites;
  byte-identity is only falsifiable on the 5 pre-existing flag combos —
  all 5 verified byte-identical under every tail expansion.
- *Carried-forward (disclosed):* the midlineforge arm remains
  timing-shaped by design (fixed 80ms descendant offset into the child's
  200ms `printraw` gap); it landed correctly on this host this run —
  `write_ppid == godot_pid`, spliced line captured — and the meta carries
  the declared falsification surface should a >~120ms stall flip it.

## Disagreements

None on any tasked claim. The r66 committed state
(`cb84d0a` + `4d938b2` + `4a4def9`) survives fresh re-execution: 88/88
bare battery, `probe_error_clause_surface` 34/34 discriminations True,
four surface arms landing as declared, committed blobs byte-identical to
the r66-verified shas, the `reparent_gate` extraction argv-faithful, and
the `classify_process`/`classify_streams` divergence documentation
accurate — re-derived on committed code in both directions.

## Residual risk / verification gaps

- Single host, single battery pass by me; `write_ppid != godot_pid` is
  the host-agnostic clause and my run shows the same `1573` subreaper
  constant.
- Concurrent wave w7: sibling r67 seats ran on this host/repo during the
  audit; my receipt is 0-mismatch vs the r66-author receipt, so no
  interference is observable in the record. The r67 author's tracked diff
  **did land in-flight** (after my battery completed — mtimes above);
  it is outside this measured state and is the wave verifier's scope, not
  this audit's.
- Not re-run (out of tasked scope): the mandated seven-flag battery
  (99/99 in the r66 author receipt) and `--fault-injection` leg; my audit
  re-ran the tasked flagless 88-row battery only.
- My divergence check used verbatim-extracted functions on synthetic
  stream pairs (declared axis premise), not a real Godot pipe run — the
  real-pipe versions are already receipted in `r66-boundary.md` edge 4.

Recommendation (non-binding; adjudication belongs to the judge): the r66
ADMIT stands — every checkable claim survives fresh re-execution on
committed `4a4def9`, and the r67 declared axis-move's premise (stdout-carried
`ERROR:` absorbed by `classify_streams`, rejected by `classify_process`)
reproduces exactly on the committed classifiers.

No commit, no tracked-file write, no sibling-lane contact, no subagent
dispatch. Artifacts: `corpus/live/r67-reviewer/runs/20261014T095231662268Z/`
(committed-state battery receipt), `battery.stdout`, `battery.stderr`,
`divergence_check.json` (verbatim-function stream-divergence re-derivation),
`reparent_gate_argv_check.py` + `reparent_gate_argv_check.out` (argv byte-identity evaluation).
