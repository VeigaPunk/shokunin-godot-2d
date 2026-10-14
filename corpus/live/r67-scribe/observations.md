# r67 scribe observations — stream-divergence independent measurement

Host: devin. Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Python 3.14.7.
All classifier verdicts driven through `ast.get_source_segment`-extracted
segments of `corpus/fixtures/run_battery.py` (worktree bytes), sha-pinned
against the `HEAD:` blob — never fed hand-built classifier copies, and
every arm runs a real subprocess on real OS pipes (never fed strings).

## State at measurement time

- First matrix pass: `run_battery.py` sha256 `76d37ace4b0b…` == HEAD blob
  == the r66-committed runner. The author diff landed mid-session:
  worktree sha → `3d5b0721d582a0b9…` (+265/−1; `stream_attribution_probe
  .gd` +58/−2). Re-ran the full matrix on the landed bytes: all four
  classifier segment shas UNCHANGED worktree↔HEAD —
  `run_process 88728b2303f6`, `classify_process 749fa0607e77`,
  `classify_streams a886968fd3ac`, `classify_audio_process 3a6bc0e831a7`
  — the diff is arm-only, classifier clauses untouched. 12/27 divergent,
  identical table both passes.
- Battery re-runs (own scratch):
  - bare (pre-land): `--runs corpus/live/r67-scribe/runs` → exit 0,
    88/88 PASS, surface 34/34. Receipt `runs/20261014T095312613881Z/`.
  - flagged (post-land): `--probe-stream-attribution --runs …` → exit 0,
    89/89 PASS (incl. `probe_stream_attribution` row), surface 34/34,
    `stream-attribution-verdicts.json` 20/20 discriminations, meta PASS.
    Receipt `runs/20261014T095922857280Z/`.

## Commands

```text
python3 corpus/live/r67-scribe/drive_streams.py        # 27 arms x 2 reps
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --runs corpus/live/r67-scribe/runs                  # 88 rows
```

## Divergence matrix (verbatim classifiers, real pipes, rep-stable 2/2)

Direction notation: M=classify_process over stdout+stderr concat,
S=classify_streams over the same captured streams. Expected exit 0,
signature `STREAM_STDOUT: expected attribution marker` unless noted.

| arm | M | S | divergent | direction |
|---|---|---|---|---|
| s_clean_sig_stdout | T | T | no | control |
| s_stdout_error | F | T | YES | absorb: stdout `ERROR:` unseen by S |
| s_stderr_error | F | F | no | both scan stderr `ERROR:` |
| s_stderr_error_allowed | T | T | no | same entry absorbs under both |
| s_stdout_error_allowed | T | T | no | agree, different clauses |
| s_stdout_error_foreign_allowed | F | T | YES | absorb even under foreign list |
| s_stderr_nonerror_noise | T | F | YES | strict: any non-allowlisted stderr line |
| s_stderr_blank | T | T | no | blank stderr skipped by S |
| s_sig_on_stderr | T | F | YES | strict: S requires sig in stdout |
| s_sig_seam_out_tail_err_head | T | F | YES | strict: sig fabricated only at merge seam |
| s_sig_seam_err_tail_out_head | F | F | no | reversed seam unforgeable in both |
| s_script_error_stdout | F | F | no | S scans both streams for blob tokens |
| s_script_error_stderr | F | F | no | |
| s_parse_error_stderr | F | F | no | |
| s_error_seam_out_err | F | F | no | both reject, different clauses |
| s_stderr_split_error_evasion | T | F | YES | `ERR\nOR:` evades M line-scan; S rejects any stderr line |
| s_stderr_prefix_allowed | T | T | no | `,`-prefix shape works in both |
| s_stdout_prefix_allowed | T | T | no | |
| s_wrong_exit | F | F | no | exit conjunct first in both |
| s_both_streams_error | F | F | no | |
| s_script_error_seam | F | F | no | blob token fabricated at seam; S rejects stderr line anyway |
| s_stderr_allowed_plus_noise | T | F | YES | allowed line + unallowlisted noise |
| s_stderr_structured_entry | T | F | YES | structured `chain incomplete` entry is merged-only |
| s_seam_error_head_allowlisted | F | T | YES | allowlisted stderr fragment completes phantom `ERROR:` seam line |
| s_seam_script_head_allowlisted | F | T | YES | same geometry, `SCRIPT ERROR:` blob token |
| s_sig_on_stderr_allowlisted | T | F | YES | exempting the stderr signature can't satisfy the stdout pin |
| g_stream_accept (real Godot) | T | T | no | stderr empty |
| g_stream_reject (real Godot) | T | F | YES | shipped reject arm diverges — `STREAM_STDERR:` line has no `ERROR:` token |

12/27 arms divergent (54 records, rep-stable). Three divergence families:
- S-absorbing (S=T where M=F): stdout `ERROR:` (streams never examines
  stdout beyond signature + 2 blob tokens); allowlisted stderr fragments
  that complete a phantom line ONLY in the merged concat.
- S-stricter (M=T where S=F): non-`ERROR:` stderr bytes, stderr-only
  signature (allowlisted or not), seam-fabricated signature, stderr
  noise beside an allowlisted line, in-stderr newline-split `ERROR:`,
  structured allowlist entries (no `chain incomplete` form in
  `line_allowed`).

## Mechanism (file:line, committed bytes)

- `run_process` :149–158 — single `capture_output=True` run; verdict input
  is the `stdout + stderr` concat; all stdout precedes all stderr.
- `classify_process` :160–177 — `signature in output` (whole-blob);
  per-line `ERROR:` scan w/ allowlist; blob `SCRIPT ERROR:`/`Parse Error:`.
- `classify_streams` :179–208 — `signature in stdout` (:183); blob tokens
  scanned in BOTH streams (:185–188); EVERY non-empty stderr line must
  satisfy `line_allowed` against `allowed_stderr` (:200–207); stdout
  content otherwise unexamined.
- Sole call site: `run_process_streams` :2200 + classify at :2219, inside
  the opt-in `--probe-stream-attribution` block (:2199–2288). The 88-row
  battery NEVER routes through `classify_streams` — divergence is latent
  for CASES; it lives only where a caller keeps streams separate.
- `allowed_stderr` exact/`,`-prefix matching (:191–198) is dead under the
  sole caller (`allowed_stderr=()`) — r66-scribe's census already named
  it; an r67 meta arm exercising `allowed_stderr` non-empty wakes it.

## Convergence

- r67-critic `matrix_results.json` + `e2e_results.json` (real Godot
  `critic_e2e_probe.gd`): same divergent classes — stdout_error absorb,
  stderr_warning strict, sig_on_stderr strict, push_error both-reject.
  Independent extraction, same verdicts.
- r66-scribe segment shas identical → classifier bytes unchanged since r65.
- **r67-author** — spike `corpus/live/r67-author/spike/clause-matrix.json`
  (string-fed, ast-extracted clauses): 14 arms all reproduced in my
  pipe-driven matrix. Landed arm replayed end-to-end
  (`runs/20261014T095922857280Z/`): their 9-row `divergence_table`
  matches my arms row-for-row — `streamdiv_{stdout_error,
  stderr_structured, sig_on_stderr, seam_sig}` T/F-or-F/T as predicted,
  `streamdiv_{seam_error,seam_script}` F/T (allowlisted stderr fragment
  completes phantom merged-only line), `streamdiv_stderr_error` F/F
  concordant, `stream_reject` T/F. CONVERGE — zero disagreement.
