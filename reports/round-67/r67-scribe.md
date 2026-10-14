# Round 67 scribe — classify_streams ↔ classify_process divergence map (host: devin)

Report+scratch seat. LEAF: no subagent dispatch, no tracked edits, no
commit/push/merge/rebase/stash/checkout. Write scope honored: this report +
`corpus/live/r67-scribe/` only. No prior r67-scribe scratch existed at
takeover (first pass created it); nothing partial to extend.

**Landing status:** the author's tracked diff landed mid-report —
`run_battery.py` +265/−1 (worktree sha `3d5b0721d582a0b9…`),
`stream_attribution_probe.gd` +58/−2, both uncommitted at report time
(lane convention: sole tracked writer, work commit at integration). My
matrix ran twice — once on the pre-land blob (`76d37ace`), once on the
landed worktree — with all four classifier segment shas byte-identical
across both (`run_process 88728b2303f6`, `classify_process 749fa0607e77`,
`classify_streams a886968fd3ac`, `classify_audio_process 3a6bc0e831a7`):
the diff adds the meta arm only, classifiers untouched. I re-ran the
landed arm end-to-end below.

## Verdict on the declared claim — VERIFIED, and wider than worded

Claim: "classify_streams verdicts diverge from classify_process on exactly
the stream-attribution axis — a stdout-carried `ERROR:` line is ABSORBED
by classify_streams (PASS-shaped) where merged classification rejects,
while stderr-carried `ERROR:`/signature bytes behave differently than
stdout-carried."

Independently measured through the verbatim extracted classifiers on real
captured per-stream pipe bytes (27 arms × 2 reps, rep-stable; 12
divergent):

- **Absorption direction CONFIRMED:** `s_stdout_error` → merged **False** /
  streams **True**; identical result under a foreign allowlist
  (`s_stdout_error_foreign_allowed`). Critic's real-Godot `stdout_error`
  arm (`--stdout-error` → `print("ERROR: stdout carried diagnostic")`)
  reproduces the same divergence on engine bytes.
- **"Exactly the stream-attribution axis" CONFIRMED but the asymmetry is
  bidirectional:** 8 of my 12 divergent arms go the OTHER way — streams
  *stricter* than merged:
  - `s_stderr_nonerror_noise` (merged T / streams F): any non-empty
    stderr line that is not allowlisted rejects — merged only scans for
    `ERROR:`-bearing lines;
  - `s_sig_on_stderr` (T/F): signature on stderr satisfies merged's
    whole-blob `signature in output`; streams requires `signature in
    stdout`;
  - `s_sig_seam_out_tail_err_head` (T/F): signature fabricated only at
    the stdout-tail→stderr-head merge seam — present in NEITHER stream
    (`signature_in_stdout=False`, `signature_in_stderr=False`,
    `signature_in_merged=True`);
  - `s_stderr_allowed_plus_noise` (T/F): an allowlisted `ERROR:` line
    plus unallowlisted stderr noise absorbs under merged, rejects under
    streams;
  - `s_stderr_structured_entry` (T/F): the structured `"ERROR: chain
    incomplete"` allowlist form exists ONLY in `classify_process`'s
    `allowed_error` (:168–171) — `classify_streams`' `line_allowed`
    (:192–198) implements exact + `,`-prefix only, so the same entry
    absorbs under merged and rejects under streams;
  - `s_stderr_split_error_evasion` (T/F): `ERR\nOR:` inside stderr evades
    merged's per-line `ERROR:` scan (r66 evasion class) — moot under
    streams, which rejects any non-allowlisted stderr line;
  - `s_sig_on_stderr_allowlisted` (T/F): exempting the stderr-carried
    signature in `allowed_stderr` clears the stderr gate but cannot
    satisfy the signature's stdout pin — the allowlist cannot redirect
    the signature channel;
  - `g_stream_reject` (T/F): **the shipped production reject arm
    already diverges** — `STREAM_STDERR: unrelated attribution
    diagnostic` on stderr contains no `ERROR:` token, so merged
    classification PASSES where `classify_streams` FAILS. The existing
    `--probe-stream-attribution` pair has measured this divergence since
    r19 without naming it.
- **Third family, seam×allowlist interaction (F/T — merged rejects where
  streams accepts):** `s_seam_error_head_allowlisted` and
  `s_seam_script_head_allowlisted`: an allowlisted stderr fragment
  completes a phantom `ERROR:`/`SCRIPT ERROR:` line that exists ONLY in
  the merged concat — merged rejects the fabrication, streams sees an
  exempted stderr line and accepts. The allowlist + seam compose into a
  verdict split neither clause reaches alone.
- **stderr-carried `ERROR:` behaves identically, not differently, at the
  verdict level** (`s_stderr_error` F/F) — the difference is in which
  clause fires, and it diverges as soon as the stderr line is *not* an
  `ERROR:` line or the allowlist position differs.

Corrected formulation my data supports: the two classifiers disagree
wherever stream attribution changes which bytes a clause can see —
streams loses all stdout content except the signature substring and the
two blob tokens (absorption side); gains a strict every-nonblank-stderr-
line gate that merged never applies plus the signature's stdout-channel
pin (stricter side); and resolves the allowlist contract differently —
the structured `chain incomplete` entry shape is merged-only, while an
allowlisted stderr fragment can't see the phantom line it completes in
the concat (seam×allowlist side).

## Baseline + mechanism read (extraction verified this pass)

- `corpus/fixtures/run_battery.py` sha256 `76d37ace4b0b…` — identical
  bytes worktree ↔ `HEAD:` blob. Extracted-segment sha256, all
  worktree==HEAD: `run_process 88728b2303f6`,
  `classify_process 749fa0607e77`, `classify_streams a886968fd3ac`,
  `classify_audio_process 3a6bc0e831a7` — the same segment shas r66-scribe
  reported; classifier bytes unchanged since r65.
- `classify_process` (:160–177): conjuncts over ONE merged string —
  `code==expected_exit` ∧ `error is None` ∧ `signature in output` ∧
  no non-allowlisted `ERROR:` line ∧ no `SCRIPT ERROR:`/`Parse Error:`
  blob hits. `run_process` (:149–158) feeds it `stdout + stderr` concat
  (all stdout precedes all stderr).
- `classify_streams` (:179–208): `code`/`error` first; `signature not in
  stdout` → False (:183); `SCRIPT ERROR:`/`Parse Error:` scanned in BOTH
  streams (:185–188); then EVERY non-empty stderr line must satisfy
  `line_allowed` against `allowed_stderr` (:200–207). **Stdout content is
  otherwise never examined** — no `ERROR:` line scan on stdout at all.
- Allowlist contract asymmetry: merged `allowed_error` carries three
  shapes — exact / `,`-prefix+`count("ERROR:")==1` / the structured
  `"ERROR: chain incomplete"` special case (:168–171); streams
  `line_allowed` (:192–198) implements only exact + `,`-prefix — the
  structured form is merged-only (measured: `s_stderr_structured_entry`
  T/F).
- Sole call site: `classify_streams` at :2219 inside the opt-in
  `--probe-stream-attribution` block (:2199–2288) with
  `allowed_stderr=()`. The 88-row battery never routes through it — the
  divergence is **latent** for CASES; it only manifests where a caller
  keeps streams separate. `line_allowed`'s exact/`,`-prefix matching
  (:191–198) is dead under the sole caller (r66-scribe census already
  named this; a non-empty `allowed_stderr` arm wakes it).

## Measured (own driver, verbatim classifiers, real pipes — 54 records, 2/2 rep-stable)

Driver `corpus/live/r67-scribe/drive_streams.py` sha256 `b54e564a5e5d…`;
receipt `stream-verdicts.json` sha256 `c12f76e352cd…` (post-land run;
identical verdict table pre- and post-land); 54 raw per-stream captures
under `raw/`; Godot arms ran a scratch copy of the landed fixture
(`proj/stream_attribution_probe.gd` sha256 `dc0b0d5c5f44…`; pre-land
copy was `97143ad367a6…`).

| arm | merged | streams | finding |
|---|---|---|---|
| s_clean_sig_stdout | T | T | control |
| s_stdout_error | F | **T** | headline absorb: stdout `ERROR:` unseen by streams |
| s_stderr_error | F | F | both scan stderr `ERROR:` |
| s_stderr_error_allowed | T | T | same entry absorbs under both |
| s_stdout_error_allowed | T | T | agree — merged via allowlist, streams blind |
| s_stdout_error_foreign_allowed | F | **T** | absorb even under foreign entry |
| s_stderr_nonerror_noise | T | **F** | strict: `WARNING:` on stderr |
| s_stderr_blank | T | T | blank stderr skipped |
| s_sig_on_stderr | T | **F** | signature channel-pinned to stdout |
| s_sig_seam_out_tail_err_head | T | **F** | seam-fabricated signature |
| s_sig_seam_err_tail_out_head | F | F | reversed seam unforgeable in both |
| s_script_error_stdout / _stderr | F | F | blob tokens scanned in both streams |
| s_parse_error_stderr | F | F | |
| s_error_seam_out_err | F | F | both reject, different clauses |
| s_stderr_split_error_evasion | T | **F** | in-stderr `ERR\nOR:` evasion moot under streams |
| s_stderr_prefix_allowed | T | T | `,`-prefix shape works in both |
| s_stdout_prefix_allowed | T | T | |
| s_wrong_exit | F | F | exit conjunct first in both |
| s_both_streams_error | F | F | |
| s_script_error_seam | F | F | blob forged at seam; streams rejects stderr line anyway |
| s_stderr_allowed_plus_noise | T | **F** | allowed line + unallowlisted noise |
| s_stderr_structured_entry | T | **F** | structured `chain incomplete` entry is merged-only |
| s_seam_error_head_allowlisted | F | **T** | allowlisted stderr fragment completes phantom `ERROR:` line |
| s_seam_script_head_allowlisted | F | **T** | same, `SCRIPT ERROR:` blob token |
| s_sig_on_stderr_allowlisted | T | **F** | exemption clears gate, can't satisfy stdout pin |
| g_stream_accept (real Godot) | T | T | stderr empty |
| g_stream_reject (real Godot) | T | **F** | shipped reject arm diverges — `STREAM_STDERR:` has no `ERROR:` token |

12/27 divergent: 4 streams=T (2 stdout-`ERROR:` absorb + 2 seam×allowlist
phantom-accept), 8 streams=F (stricter direction). Seams: only
stdout-tail→stderr-head ordering fabricates in merged (stderr bytes
always land after all stdout in the concat); `signature_in_{stdout,
stderr,merged}` per record pins each arm's per-stream seam position.

## Landed-arm replay (post-land, own scratch)

The landed meta arm rides inside `--probe-stream-attribution`
(`run_battery.py` +265: `dual_classify`/`streamdiv_arm` helpers, 7 real
Godot `streamdiv_*` arms, 6 allowlist reclassifications, pair dual on the
shipped accept/reject runs, 20 discriminations, `divergence` block in the
probe payload). Fixture +58: `printraw`/`printerr` byte placement for
`--stdout-error` `--stderr-error` `--stderr-structured` `--sig-on-stderr`
`--seam-error` `--seam-script` `--seam-sig`.

```text
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --probe-stream-attribution \
    --runs corpus/live/r67-scribe/runs        → exit 0
```

Receipt `runs/20261014T095922857280Z/` — `verdicts.json` sha
`20fcd8cdd2bc…`: **89/89 PASS** (88 prior rows + `probe_stream_attribution`
row, all PASS); `probe_error_clause_surface` discriminations still
**34/34 true**; `stream-attribution-verdicts.json` sha `ea290a65d394…`:
**20/20 discriminations true**, meta verdict PASS. `battery-attr.stdout`
sha `2832cccb2962…`.

Their `divergence_table`, row-for-row vs my independent arms:

| landed row | M | S | my corresponding arm | match |
|---|---|---|---|---|
| stream_accept | T | T | g_stream_accept T/T | ✓ |
| stream_reject | T | **F** | g_stream_reject T/F | ✓ |
| streamdiv_stdout_error | F | **T** | s_stdout_error F/T | ✓ |
| streamdiv_stderr_error | F | F | s_stderr_error F/F | ✓ |
| streamdiv_stderr_structured | T | **F** | s_stderr_structured_entry T/F | ✓ |
| streamdiv_sig_on_stderr | T | **F** | s_sig_on_stderr(_allowlisted) T/F | ✓ |
| streamdiv_seam_error | F | **T** | s_seam_error_head_allowlisted F/T | ✓ |
| streamdiv_seam_script | F | **T** | s_seam_script_head_allowlisted F/T | ✓ |
| streamdiv_seam_sig | T | **F** | s_sig_seam_out_tail_err_head T/F | ✓ |

9/9 verdict pairs identical across independent drivers and independent
Godot invocations. Per-stream seam positions in their records
(`stdout_tail_line`/`stderr_head_line`) match my `signature_in_*`/
`error_token_in_*` pins — e.g. `streamdiv_seam_sig` tail
`STREAM_STDOUT: expected attribution ` + head `marker` = my
SIG[:SIG_H]/SIG[SIG_H:] split.

My adds beyond their table: in-stderr `ERR\nOR:` evasion-is-moot (T/F),
allowlisted-line+noise mix (T/F), comma-`,`-prefix stderr shape absorbed
(T/T), bare script-seam and reversed seam (F/F), stdout `ERROR:` under
foreign allowlist (F/T) — all consistent extensions, no disagreement.

## Battery receipts (own scratch re-runs)

```text
python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --runs corpus/live/r67-scribe/runs        → exit 0  (pre-land)
```

Receipt `runs/20261014T095312613881Z/verdicts.json` sha256
`7eb316015bd2…`: **88/88 PASS**; `probe_error_clause_surface`
discriminations **34/34 true**. `battery.stdout` sha256 `89c619a0957a…`.
Post-land flagged run above preserves both greens (89/89 incl. the new
meta row; bare-battery surface unchanged — the meta arm lives in the
opt-in flag, the bare count stays 88).

## Converge/diverge vs sibling seats

- **Critic** (`corpus/live/r67-critic/`): `matrix_results.json` +
  `e2e_results.json` — independent extraction AND real Godot
  `critic_e2e_probe.gd` arms. Same divergent classes: `stdout_error`
  absorb, `stderr_warning`/`sig_on_stderr` strict, `stderr_push_error`
  both-reject (engine `push_error` emits multi-line stderr incl.
  backtrace — rejects under both classifiers). CONVERGE.
- **Baseline** (`corpus/live/r67-baseline/` + `r67-baseline.md`):
  frozen pre-move replay 88/88; my battery run reproduces it
  field-for-field on the result rows. CONVERGE.
- **Author**: landed mid-report and replayed — spike
  `corpus/live/r67-author/spike/clause-matrix.json` (14 string-fed arms)
  plus the tracked meta arm re-run end-to-end at
  `runs/20261014T095922857280Z/` (89/89, 20/20 discriminations). Their
  9-row divergence table matches my independent matrix row-for-row; the
  spike surfaced three classes my first pass missed (structured entry,
  seam×allowlist, allowlisted-sig-on-stderr), all confirmed on real
  pipes. CONVERGE — zero disagreement.
- **r19 lesson**: documents the pair's origin — `classify_streams`'s
  every-nonblank-stderr gate was itself a r19 critic-driven fix of the
  prefix-only hole. The r67 divergence map is that gate's measured
  contract.

## Errata / limits

- Landing raced the report: the diff landed mid-write; both states were
  measured (pre-land blob `76d37ace`, post-land `3d5b0721`), classifier
  segments identical across them. The author's own report/verifier/
  adjudication were not yet on disk — convergence reported against their
  landed bytes + my replay, not their prose.
- Untracked `corpus/fixtures/__pycache__/` appeared alongside the author's
  battery run (interpreter cache, not a tracked edit); noted, not mine to
  remove.
- Bounds: Linux headless Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
  CPython 3.14.7 POSIX pipes; verdicts are classifier-level, no gameplay
  or exported-build claim; the `UnicodeDecodeError` escapes-verdict hole
  (r66) applies identically to `run_process_streams`'s text-mode capture.
- `s_sig_seam_err_tail_out_head` wording in earlier notes said "order
  broken in merged too" — precisely: the signature halves land
  non-adjacent in the concat, so no fabrication is possible; verdict F/F
  stands.

## Draft — `corpus/lessons/r67-stream-classifier-divergence.md`

```markdown
# R67 — classify_streams ↔ classify_process per-channel divergence map (Godot 4.7.2 headless)

Sources: `reports/round-67/r67-{author,critic,reviewer,scribe,...}.md`;
`corpus/fixtures/run_battery.py` classifiers :160–177 / :179–208,
`run_process` :149–158, `run_process_streams` :2200–2209, meta arm in the
`--probe-stream-attribution` block (worktree sha `3d5b0721d582…`,
commit TBD at integration); `corpus/fixtures/
stream_attribution_probe.gd` `streamdiv_*` byte-placement arms;
author receipt `corpus/live/r67-author/runs/…/stream-attribution-
verdicts.json`; scribe independent receipt `corpus/live/r67-scribe/
stream-verdicts.json` (sha256 `c12f76e352cd…`, 54 real-pipe records,
driver `b54e564a5e5d…`) + landed replay `runs/20261014T095922857280Z/`
(89/89, 20/20 discriminations); critic matrix + e2e receipts under
`corpus/live/r67-critic/`.
Prior lessons extended: `r19-stream-attribution.md` (the pair's origin),
`r66-rejection-clause-surface.md` (merged-clause surface map).

verified-at: 2026-10-14, Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
Python 3.14.7, Linux x86_64; classifier segments byte-identical
worktree↔HEAD (`classify_process 749fa060`, `classify_streams a886968f`);
verdicts driven through `ast.get_source_segment`-extracted production
functions on real captured pipe bytes — never fed strings.

## The asymmetry, precisely

`classify_process` sees one concat blob (`stdout` then `stderr`);
`classify_streams` sees the channels separately. Every divergence is a
clause whose byte-view differs:

- ABSORB side (streams=T, merged=F): stdout is examined ONLY for
  signature-presence and the `SCRIPT ERROR:`/`Parse Error:` blob tokens.
  A stdout `ERROR:` line is invisible — absorbed PASS-shaped, with or
  without a matching allowlist entry.
- STRICT side (merged=T, streams=F): (a) EVERY non-empty stderr line
  must match `allowed_stderr` — non-`ERROR:` chatter (`WARNING:`,
  `STREAM_STDERR:`, banner noise) is verdict-inert under merged but
  rejects under streams; (b) the signature is channel-pinned to stdout —
  a stderr-only signature satisfies merged's blob test, never streams',
  and exempting it in `allowed_stderr` cannot redirect the pin; (c) the
  merged concat's stdout-tail→stderr-head seam fabricates substrings
  (signatures, `ERROR:` lines, blob tokens) present in NEITHER stream —
  merged can be forged to a verdict either way, streams cannot see the
  seam; (d) the structured `chain incomplete` allowlist entry is
  merged-only — `line_allowed` has exact + `,`-prefix shapes only.
- SEAM×ALLOWLIST side (merged=F, streams=T): an allowlisted stderr
  fragment completes a phantom `ERROR:`/`SCRIPT ERROR:` line that exists
  only in the concat — merged rejects the fabrication; streams sees an
  exempted stderr line and accepts.
- AGREE shapes: stderr `ERROR:` rejects under both (same verdict,
  different clause); allowlist absorbs matching stderr lines under both;
  blob tokens reject under both in either stream; exit/error mismatches
  short-circuit first in both.

## Notable pins

- The shipped `--probe-stream-attribution` REJECT arm already diverges:
  `STREAM_STDERR: unrelated attribution diagnostic` has no `ERROR:`
  token → merged=True / streams=False. The divergence was production
  behavior since r19, un-named.
- `line_allowed`'s exact/`,`-prefix matcher (:191–198) is live only for
  `allowed_stderr` — sole caller passes `()`, so it is dead machinery
  until a non-empty allowlist arm exercises it (r66 census: same
  finding).
- Only stdout-tail→stderr-head seam order fabricates in merged; stderr
  bytes always land after all stdout, so the reversed seam cannot.
- Latency bound: the 88-row battery never calls `classify_streams` —
  divergence lives only where a caller captures streams separately.
```

## Draft — LOG.md round entry

```markdown
## Round 67 — devin host — depth/coverage: classify_streams ↔ merged per-channel divergence

- Declared (author dispatch brief; retroactive record): map
  `classify_streams`' per-channel divergence from merged
  `classify_process` as a measured axis — stdout-carried `ERROR:`
  absorbed PASS-shaped where merged rejects; per-stream records +
  divergent-verdict pins incl. per-stream seam positions and the
  allowlist's per-stream match; additive meta arm; 88/88 + surface 34/34
  stay green.
- Wave `shokunin-train-20261014-w7`: leaf set
  `reports/round-67/r67-{...}.md`, disjoint scratch `corpus/live/r67-*/`.
  Frozen baseline 88/88, surface 34/34 (`corpus/live/r67-baseline/`).
- Author `reports/round-67/r67-author.md` (diff landed, uncommitted at
  write): `run_battery.py` +265 — `streamdiv_*` meta arm inside
  `--probe-stream-attribution` (7 real Godot arms + 6 allowlist
  reclasses + pair dual, 20 discriminations);
  `stream_attribution_probe.gd` +58 per-channel byte placement
  (`printraw`/`printerr`, `--{stdout,stderr}-error`, `--stderr-
  structured`, `--sig-on-stderr`, `--seam-{error,script,sig}`).
  Flagged replay 89/89, surface 34/34, meta PASS.
- Measured (scribe independent, 54 real-pipe records + landed replay):
  12/27 arms divergent — absorption: stdout `ERROR:` invisible to
  streams (2); strict: non-`ERROR:` stderr, stderr-only signature
  (allowlisted or not), seam-fabricated signature, allowlist+noise mix,
  in-stderr `ERR\nOR:` evasion, merged-only structured entry (8);
  seam×allowlist: exempted stderr fragment completes phantom line
  merged-only (2). Landed 9-row divergence_table matches arm-for-arm.
  Shipped reject arm itself diverges (T/F). Critic e2e converges.
- Non-author `reports/round-67/r67-verifier.md`: TBD.
- Per-axis verdicts (Sol `reports/round-67/r67-adjudicator.md`): TBD.
  Bounded: classifier-level verdicts only, Linux headless 4.7.2, CPython
  POSIX pipes; divergence latent for CASES (sole call site is the
  opt-in stream-attribution probe). Work commit TBD; report-last follows.
```

## Artifact inventory (all `corpus/live/r67-scribe/`)

- `drive_streams.py` sha256 `b54e564a5e5d…` — extraction + 27-arm driver
- `stream-verdicts.json` sha256 `c12f76e352cd…` — 54 records, rep-stable
  (post-land run; classifier segments still `88728b23`/`749fa060`/
  `a886968f`/`3a6bc0e8`)
- `observations.md` sha256 `aa48696b9b8a…`
- `battery.stdout` sha256 `89c619a0957a…` + `battery.stderr` (pre-land,
  88/88)
- `battery-attr.stdout` sha256 `2832cccb2962…` + `battery-attr.stderr`
  (post-land, `--probe-stream-attribution`, 89/89)
- `runs/20261014T095312613881Z/verdicts.json` sha256 `7eb316015bd2…`
  (pre-land) and `runs/20261014T095922857280Z/{verdicts.json
  sha 20fcd8cdd2bc…, stream-attribution-verdicts.json sha ea290a65d394…}`
  (post-land)
- `raw/` — 54 raw per-stream captures (`<arm>.rep<N>.{stdout,stderr}`)
- `proj/` — scratch fixture copy for the Godot arms (post-land bytes)
