# Round 68 reviewer report — non-author audit of round 67 committed state (host: devin)

Seat: reviewer (non-author). I authored none of the r67 content and none of
the in-flight r68 work. Every run below is a fresh execution by me into my
own scratch; no commit, no tracked fixture/runner edit, no LOG/SCORECARD
write, no verdict marking. Write scope: this report and
`corpus/live/r68-reviewer/` only.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
CPython `3.14.7`, Linux x86_64, `systemd --user` subreaper pid `1573` —
same host profile as the r67 receipts. Repo under audit:
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` (canonical; reached via
the `.shokunin/game-dev-2d` symlink from worktree
`~/Projects/prymeagnt/game-dev-2d`, whose own tree sits at the `fe4bbeaf`
extract commit and is clean).

**LSP device status: unavailable.** This seat's toolset exposes no `lsp`
device — same as every prior round on this Python fixture. All checks are
live battery executions, verbatim `ast` function extraction from the
committed blob, and receipt/git-object comparison; grep output is never
presented here as semantic proof.

HEAD under test: `1101cb3` "r67 report-last". The r67 chain verified by
`git log`: `d44ba86` (r67 work: `classify_streams` per-channel divergence
map, 7 probe arms + dual-classify meta) → `9e946c9` (`sd_sig_head`
load-bearing pin) → `3a53258` (ignore hygiene, pre-dates report-last) →
`1101cb3` (report-last: ADMIT, verifier AGREE 5/5, lesson/LOG/SCORECARD).
`git status --porcelain` at audit time: **no tracked modification** — only
untracked sibling r68 scratch (`r68-baseline`, `r68-boundary`,
`r68-critic`, `r68-scout`, `r68-scribe`, `r68-simplifier`,
`reports/round-68/`) and my own `r68-reviewer/`. The r68 author's tracked
diff had **not landed** at any measurement below; worktree bytes ==
committed blobs throughout:

| file | worktree sha256 | `git show HEAD:` sha256 | r67-recorded digest |
|---|---|---|---|
| `corpus/fixtures/run_battery.py` | `8d7e4d946e41…` | identical | `8d7e4d94…` (r67-verifier post-fixup) |
| `corpus/fixtures/stream_attribution_probe.gd` | `dc0b0d5c5f44…` | identical | `dc0b0d5c…` (r67-author post-change) |
| `corpus/fixtures/descendant_pipe_probe.gd` | `92a40d70e31d…` | identical | `92a40d70…` (r66/r67 receipts) |

## Tasked check 1 — flagless committed battery on HEAD → 88/88 + surface 34/34 — AGREE

```
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r68-reviewer/runs
```

- Exit `0`; final line `PASS battery`. stdout tee'd to
  `corpus/live/r68-reviewer/battery.stdout`: **89 `^PASS` lines (88 rows +
  banner), 0 `^FAIL`**; stderr log 0 bytes.
- Receipt
  `corpus/live/r68-reviewer/runs/20261014T104813737103Z/verdicts.json`:
  `"verdict": "PASS"`, **88 results, 88 PASS / 0 FAIL** (81 CASES + 7
  unconditional meta rows; `probe_stream_attribution` correctly absent —
  flag-gated).
- `probe_error_clause_surface` row: `verdict PASS`, mode
  `bounded_popen_surface_arms_plus_allowlist_census`, **34 discriminations,
  every value True**; `census.rows_with_expected_errors=39`.
- The four surface arms land exactly as the r66/r67 declared table:

| arm | exit | sig | write_ppid vs godot_pid | inner cls | reading |
|---|---|---|---|---|---|
| `surface_allowforge` | 0 | True | `1573` ≠ `2893816` | False | post-death forged line captured, allowlist-scoped |
| `surface_splitforge` | 0 | True | `1573` ≠ `2893893` | **True** | `ERR`/`OR:` newline split **evades** merged line scan |
| `surface_seamforge` | 0 | True | `1573` ≠ `2894001` | False | phantom `…tail ends in ERROR: SEAMFORGE phantom fabricated line` merged-only |
| `surface_midlineforge` | 0 | **False** | `2894116` **== godot** | False | pre-death splice destroyed signature — the 80ms offset landed inside the 200ms gap on this host |

- `seam_split_run` corroborates seam geometry: `raw_stdout_lines[-1]` ==
  `DESCENDANT_PIPE_SEAMFORGE tail ends in ERROR` (unterminated),
  `raw_stderr_lines[0]` == `: SEAMFORGE phantom fabricated line`,
  `write_ppid=1573`, `merged_classification=false`.

### Prior-row stability — 7-field tuple diff, 0 mismatches

Keyed on `case`, tuple `(script, flags, expected_exit, actual_exit,
signature, verdict, error)`:

- vs r67-author flagless `corpus/live/r67-author/runs/20261014T095753034446Z/verdicts.json`: **88 common, 0 mismatches**, no added/missing rows.
- vs r67-verifier flagless `corpus/live/r67-verifier/runs/20261014T102359619107Z/verdicts.json`: **88 common, 0 mismatches**.
- vs r67-baseline frozen replay `corpus/live/r67-baseline/runs/20261014T094859374505Z/verdicts.json`: **88 common, 0 mismatches**.

## Tasked check 2 — `--probe-stream-attribution` → 89/89 + 20/20 + 9-row table — AGREE

```
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r68-reviewer/runs \
  --probe-stream-attribution
```

- Exit `0`. Receipt
  `corpus/live/r68-reviewer/runs/20261014T105018887735Z/verdicts.json`:
  **89 rows, 89 PASS / 0 FAIL**. (The one `^FAIL stream_reject:` stdout
  line at :90 is the probe's designed inner-classification diagnostic —
  its *expected* `classification=False` — not a battery row failure.)
- `probe_stream_attribution` row: `verdict PASS`,
  `inner_classifications=[True, False]`.
- Artifact `stream-attribution-verdicts.json`:
  `divergence.discriminations` = **20 keys, all True**;
  `divergence_table` = **9 rows** — **field-identical** to the r67-author
  receipt (`runs/20261014T095910487678Z`), including per-row
  `merged_allowlist`/`stream_allowlist`; `allowlist_reclassifications` = 6
  same-capture reclasses, all verdict-identical to the author's;
  `pair_reclassifications` = 2. Divergent rows: `stream_reject` T/F,
  `streamdiv_stdout_error` F/T, `streamdiv_stderr_structured` T/F,
  `streamdiv_sig_on_stderr` T/F, `streamdiv_seam_error` F/T,
  `streamdiv_seam_script` F/T, `streamdiv_seam_sig` T/F — 7 divergent of
  9, control rows (`stream_accept` T/T, `streamdiv_stderr_error` F/F)
  concordant.
- Prior-row stability vs r67-verifier flagged receipt
  (`runs/20261014T102529598296Z/verdicts.json`, same single flag): **89
  common rows, 0 mismatches**.
- Seam mechanics pinned on MY captured bytes: `streamdiv_seam_error`
  `merged_error_lines` = `['STREAMDIV seam tail ends in ERROR: STREAMDIV
  seam phantom merged-only line']` — present in NEITHER stream's line set
  (`stdout_tail_line`/`stderr_head_line` pin the halves);
  `streamdiv_seam_script` `script_error_in_merged=True` while both stream
  flags are False; `streamdiv_seam_sig` signature_in_merged only
  (`False/False/True`) and `raw_stdout.endswith(sd_sig_head)` evaluates
  **True** — the `9e946c9` load-bearing pin confirmed on real bytes
  (`run_battery.py:2468–2474`).
- Prior surface meta byte-stable: flagless run still 34/34, and the r67
  artifact carries **no** `divergent_clause` field and **no**
  `sha256(raw_*)` fields — clean baseline shape for the r68 declared
  additive upgrade.

## Tasked check 3 — r67 adjudication claims — VERIFIED on committed code

### (a) Four-family map, 12 divergent arms — AGREE (with a report-text nit)

I re-derived the map independently: `ast.get_source_segment`-extracted
`classify_process` and `classify_streams` from `git show
HEAD:corpus/fixtures/run_battery.py` (committed bytes, not worktree),
exec'd, and drove real subprocess pipes — driver
`corpus/live/r68-reviewer/drive_divergence.py`, receipt
`divergence-rederive.json` + `raw/`. Segment sha256s from the HEAD blob:
`classify_process` `749fa0607e77…`, `classify_streams` `a886968fd3ac…`,
`run_process` `88728b2303f6…` — **all three identical** to the r67-scribe's
recorded segment digests.

Same 28-arm enumeration (26 synthetic + 2 Godot) × 2 reps, rep-stable.
Divergent set reproduces **exactly** the r67 artifact's 12 arms:

- **ABSORB (merged=F / streams=T, 2):** `s_stdout_error`,
  `s_stdout_error_foreign_allowed` — stdout `ERROR:` invisible to streams.
- **STRICT (merged=T / streams=F, 8):** `s_stderr_nonerror_noise`,
  `s_sig_on_stderr`, `s_sig_on_stderr_allowlisted`,
  `s_sig_seam_out_tail_err_head`, `s_stderr_allowed_plus_noise`,
  `s_stderr_structured_entry`, `s_stderr_split_error_evasion`,
  `g_stream_reject`.
- **SEAM×ALLOWLIST (merged=F / streams=T, 2):**
  `s_seam_error_head_allowlisted`, `s_seam_script_head_allowlisted` —
  exempted stderr fragment completes a phantom line existing only in the
  concat.
- **AGREE:** the remaining 16 arms concordant (incl. `s_stderr_error` F/F,
  `s_wrong_exit` F/F, `g_stream_accept` T/T).

*Nit (documentation, not code):* the adjudicator, scribe report, and
`LOG.md:657` say "12/27 arms" / "54 real-pipe records"; the committed
artifact `corpus/live/r67-scribe/stream-verdicts.json` enumerates **28**
arms / 56 records (`arm_count: 28`, my re-run confirms 28 distinct arms).
The divergent numerator — 12 — is exactly confirmed; the most plausible
reading is that "27" excludes the exit-path control `s_wrong_exit` from
the classification arm census. No semantic impact; record-keeping nit.

### (b) Seam one-position (stdout-tail|stderr-head only) — VERIFIED

- Committed mechanism: `run_process` returns `proc.stdout + proc.stderr`
  (`run_battery.py:152`) — the merge has exactly one junction; fragments
  at stderr-tail|stdout-head sit at the merged blob's opposite ends and
  can never meet.
- Live: all three landed seam arms fabricate at stdout-tail|stderr-head
  only (above); boundary's direction-B de-fabrication reproduced by my two
  added arms: `r68_err_seam_err_tail_out_head` → `merged_error_lines=[]`
  (**no phantom**; merged=True, streams=False on stderr strictness alone),
  `r68_sig_seam_err_tail_out_head` → `signature_in_merged=False`, F/F.
  Direction B fabricates neither the error axis nor the signature axis.

### (c) Shipped-arm divergence (`stream_reject` T/F, latent since r19) — VERIFIED

- My flagged receipt: `stream_reject` merged=True / streams=False in both
  `divergence_table` row 2 and `pair_reclassifications`; discrimination
  `reject_arm_diverges_non_error_stderr=True` (`run_battery.py:2477–2481`).
- Mechanism confirmed on captured bytes: `STREAM_STDERR: unrelated
  attribution diagnostic` carries no `ERROR:` token — merged ignores it;
  streams' every-nonblank-stderr-line audit (`:200–207`) rejects.
- Provenance: `git log` shows the pair added by `2cd776c` "r19: calibrate
  headless stdout/stderr attribution" — divergent production behavior
  since r19, un-named until r67. Claim holds.
- Latency confirmed: `classify_streams` call sites at `:2219` and `:2286`
  are both inside the opt-in `probe_stream_attribution` block; default
  battery never invokes it (88-row flagless receipt has no streamdiv row).

## Corroborating checks

- **LOG/SCORECARD committed state intact:** `LOG.md:645–671` carries the
  round-67 wave/author/measured/integration/verifier/adjudicator entries;
  `SCORECARD.md:48–56` carries the r67 axis verdicts and ADMIT line —
  consistent with `1101cb3`'s diff.
- **Process hygiene:** post-run `pgrep` finds no leaked
  `descendant_pipe`/`STREAMDIV`/`*FORGE` processes from my runs (the meta's
  orphan reaper ran; arms self-exit). A `sha256sum`-watcher shell
  (pid 3093980) polling for `r68-author` scratch is a sibling lane's
  monitor, not a leaked probe; headless godot processes on the host during
  the audit belonged to the sibling `game-dev-3d` r77 lane — data, not
  evidence.
- **Sibling r68 wave in flight:** `r68-{baseline,boundary,critic,scout,
  scribe,simplifier}/` and `reports/round-68/` are sibling seats'
  untracked scratch — not mine, not audited. No `r68-author` dir or
  tracked diff existed at any measurement.

## Findings by severity

**No actionable defect found in scope.** Every tasked check agrees.

- *Observation (documentation nit, disclosed):* "12/27" in
  `r67-adjudicator.md:31`, `r67-scribe.md:28`, `LOG.md:657`, and
  `SCORECARD.md:50` vs the committed enumeration's 28 arms / 56 records
  (`stream-verdicts.json` `arm_count: 28`). Numerator 12 reproduces
  verbatim; denominator appears to count classification arms excluding
  the `s_wrong_exit` exit-path control. Not drift in any measured claim.
- *Carried-forward (disclosed):* the `surface_midlineforge` arm remains
  timing-shaped (fixed ~80ms descendant offset into the child's 200ms
  `printraw` gap); it landed `write_ppid == godot_pid` again on this host.
  The r68 declared ladder sweep ({0,40,80,120,160,240}ms) is exactly the
  right instrument for that residual — outside this audit's scope.

## Disagreements

None on any tasked claim. The r67 committed state (`d44ba86` + `9e946c9` +
`1101cb3`) survives fresh re-execution: 88/88 flagless with surface 34/34,
89/89 under `--probe-stream-attribution` with 20/20 discriminations and a
field-identical 9-row `divergence_table`; the adjudicated four-family map
reproduces arm-for-arm on verbatim extracted committed classifiers over
real pipes; the seam bound is one-position by construction and by
measurement; the shipped-arm divergence is real, live, and r19-provenanced.

## Residual risk / verification gaps

- Single host, single battery pass per leg by me; `write_ppid != godot_pid`
  is the host-agnostic clause and my runs show the same `1573` subreaper
  constant.
- Not re-run (out of tasked scope): the mandated seven-flag battery (99/99
  in the r67 author receipt) and `--fault-injection` leg; my audit re-ran
  the tasked flagless + `--probe-stream-attribution` legs only.
- My divergence re-derivation drives the committed classifiers over
  real pipes via my own capture harness (not `run_process` itself) — the
  shipped-path verdicts are already receipted in the flagged battery leg.

Recommendation (non-binding; adjudication belongs to the judge): the r67
ADMIT stands — every checkable claim survives fresh re-execution on
committed `1101cb3`, with one documentation nit on the arm-count
denominator.

No commit, no tracked-file write, no sibling-lane contact, no subagent
dispatch. Artifacts:
`corpus/live/r68-reviewer/runs/20261014T104813737103Z/` (flagless battery
receipt), `runs/20261014T105018887735Z/` (flagged receipt +
`stream-attribution-verdicts.json`), `battery.stdout`/`battery.stderr`,
`battery-flagged.stdout`/`battery-flagged.stderr`,
`drive_divergence.py` + `divergence-rederive.json` + `raw/` +
`proj/` (verbatim-classifier 30-arm × 2-rep real-pipe re-derivation).
