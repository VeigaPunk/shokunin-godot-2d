# Round 67 verifier report — classify_streams per-channel divergence map (seat: verifier, NON-AUTHOR)

Verified on committed tree `HEAD = 9e946c9` (= `d44ba86` + fixup `9e946c9`).
Worktree clean for `corpus/fixtures/`; HEAD blob digests == worktree bytes:
`run_battery.py` sha256 `8d7e4d946e419c8f2fd4c8890cc2d3286f009b8434abc27392724d903c8a4634`,
`stream_attribution_probe.gd` sha256 `dc0b0d5c5f44a1b4404cbe62cada0e6e53e2b33be010ea32dc72cb3892aeb286`
(probe digest == the author's recorded post-change digest; the runner digest
differs from the author's `3d5b0721…` because the fixup postdates the author
report — expected, not drift).

Host: `/usr/bin/godot` = Godot `4.7.2.stable.arch_linux.ed1daf0bf` (same
version the author measured). No LSP server answers either file (no Python or
GDScript server configured — matches author's note); verification ran live
battery executions plus byte/exact-match receipt comparisons.

## Commands executed (all on committed tree, scratch `corpus/live/r67-verifier/`)

```
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r67-verifier/runs
  # flagless -> exit 0, runs/20261014T102359619107Z/verdicts.json sha256 b5b0af0f…
  #            PASS 88/88

python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r67-verifier/runs \
  --probe-stream-attribution
  # flagged  -> exit 0, runs/20261014T102529598296Z/verdicts.json sha256 3e69d339…
  #            PASS 89/89; stream-attribution-verdicts.json sha256 6db5015e…
```

Both battery stderr logs 0 bytes.

## Per-claim verdicts

### Claim 1 — 7 arm flags on `stream_attribution_probe.gd`; default arm byte-identical — AGREE

Static: `git show d44ba86 -- corpus/fixtures/stream_attribution_probe.gd` adds
exactly the 7 named flags — `--stdout-error`, `--stderr-error`,
`--stderr-structured`, `--sig-on-stderr`, `--seam-error`, `--seam-script`,
`--seam-sig` — plus the constants/banner. The single changed emission is
`print(STDOUT_MARKER)` becoming `if/elif/else` whose `else` branch is the
identical `print(STDOUT_MARKER)`; pre-existing `--stderr-unrelated` untouched.

Dynamic: my flagged run's `stream_accept` ([] flags) and `stream_reject`
(`--stderr-unrelated`) captured `raw_stdout`/`raw_stderr` are **byte-identical**
to both the author's r67 receipt AND the pre-r67 receipt
`corpus/live/r66-author/runs/20261014T051301624764Z/stream-attribution-verdicts.json`
(banner + `STREAM_STDOUT: expected attribution marker\n` on stdout; stderr
empty / `STREAM_STDERR: unrelated attribution diagnostic\n`; inner True/False
unchanged).

### Claim 2 — `dual_classify`/`streamdiv_arm` meta under `--probe-stream-attribution`; 20 discriminations all True; 9-row table — AGREE

The block sits inside `if args.probe_stream_attribution:` (run_battery.py
2262–2504): `dual_classify` runs `classify_process(so+se)` and
`classify_streams(so,se)` over the same capture; `streamdiv_arm` does one real
Godot run per flag and records raw bytes + line maps + the verdict pair. My
receipt: `divergence.discriminations` = 20 keys, **all True**;
`divergence_table` = 9 rows (2 pair rows + 7 arms); `allowlist_reclassifications`
= 6 same-capture reclassifications (no extra runs); `pair_reclassifications` = 2.
`sd_meta_ok` gates the row verdict (`meta_pass and sd_meta_ok`).

### Claim 3 — divergence is real and multi-mechanism — AGREE

All measured on MY run's captured bytes (`runs/20261014T102529598296Z`):

| row | merged | streams | divergent |
|---|---|---|---|
| stream_accept | True | True | no |
| stream_reject (non-`ERROR:` stderr line) | True | False | **yes** |
| streamdiv_stdout_error | False | True | **yes** |
| streamdiv_stderr_error | False | False | no (control) |
| streamdiv_stderr_structured (structured entry) | True | False | **yes** |
| streamdiv_sig_on_stderr (stderr allowlisted) | True | False | **yes** |
| streamdiv_seam_error (head allowlisted) | False | True | **yes** |
| streamdiv_seam_script (head allowlisted) | False | True | **yes** |
| streamdiv_seam_sig (tail allowlisted) | True | False | **yes** |

Mechanism evidence in the receipt: sd1 `stdout_error_lines` carries the
`ERROR:` line while `stderr_error_lines` is empty yet merged rejects → stdout
is never error-scanned by `classify_streams` but `classify_process` scans the
merged text origin-blind. sd5 `merged_error_lines` is exactly the fabricated
`STREAMDIV seam tail ends in ERROR: STREAMDIV seam phantom merged-only line`,
present in NEITHER stream's line set (`stdout_tail_line`/`stderr_head_line`
pin the halves). sd6 `script_error_in_merged=True` while both stream flags are
False. sd7 signature contiguous only in merged. `stream_reject` itself
diverges (streams' any-unallowlisted-stderr-line strictness).
Allowlist reclassifications corroborate: `stderr_error` exact→T/T,
foreign→F/F; `stderr_structured` exact-line→T/T, bare→F/F; `sig_on_stderr`
bare→T/F; `seam_error` bare→F/F — the `line_allowed` shape asymmetry (exact +
`,`-prefix only, no structured branch) is exercised live, not just read.

### Claim 4 — flagless 88/88 + surface 34/34; flagged adds the streamdiv row; prior rows 0 mismatches — AGREE

- Flagless verdicts.json: `verdict=PASS`, 88 rows, Counter PASS×88.
- `probe_error_clause_surface` row: `discriminations` = 34 keys, all True.
- Flagged run: 89 rows all PASS; `new-only = ['probe_stream_attribution']`,
  `missing = []`.
- Prior-row stability: 7-field tuple
  `(script, flags, expected_exit, actual_exit, signature, verdict, error)`
  diff over the 88 common rows → **0 mismatches**.
- The streamdiv row: `verdict=PASS`, `inner_classifications=[true,false]`,
  artifact pointer to `stream-attribution-verdicts.json`; its 9-row table and
  all 20 discrimination values equal the author's receipt key-for-key
  (mismatch set `{}`); author's artifact sha256 `d65608f9…` matches his report.
- Seed digests unchanged: `git diff cb84d0a..HEAD -- corpus/fixtures/` touches
  ONLY `run_battery.py` (+266/−1: the sole deleted line is the old verdict
  expression) and `stream_attribution_probe.gd` (+58/−1); every other fixture
  byte is untouched, and the scratch seed copy of the probe used by my run is
  sha256-identical (`dc0b0d5c…`) to the committed blob.

### Claim 5 — `sd_sig_head` load-bearing; `raw_stdout.endswith(sd_sig_head)` True in the real receipt — AGREE

`seam_sig_diverges_signature_seam` at HEAD (run_battery.py:2468–2474) conjoins
`sd7["raw_stdout"].endswith(sd_sig_head)`. In `d44ba86` (pre-fixup)
`sd_sig_head` was assigned at :2278 and never read — a dead binding; the fixup
genuinely makes it load-bearing. My receipt: sd7 `raw_stdout` ends
`…ine.org\n\nSTREAM_STDOUT: expected attribution ` (trailing space, unterminated
`printraw` tail) and `raw_stderr='marker\n'`; the conjunct evaluates **True**,
and the discrimination is True in the artifact.

## Residual risk / verification gaps

- My flagged invocation used only `--probe-stream-attribution` (per brief):
  89 rows. The author's own full-flag receipt (7 flags → 99/99) is
  corroborating evidence, not re-executed by me; the other 10 opt-in rows were
  not re-measured this round.
- Seam fabrications depend on the runner's fixed `stdout + stderr` concat
  order (run_battery.py:152) — same caveat the author recorded; unchanged.
- `printerr`/`printraw` byte placement verified on this host's Godot 4.7.2
  headless only; other versions/platforms unmeasured (bounded_claim says the
  same).
- `classify_streams`' asymmetry is bidirectional (looser on stdout `ERROR:`,
  stricter on any unallowlisted stderr line); the artifact records this — a
  consumer must not read streams-PASS as implying merged-PASS.
- Single-host, single-run reproduction; no flake observed (exit 0 both runs,
  stderr logs empty).

## Verdict

**AGREE 5/5.** All claims reproduce on the committed tree at `9e946c9` with
command-level evidence under `corpus/live/r67-verifier/runs/`.
