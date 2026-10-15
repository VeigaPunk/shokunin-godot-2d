# Round 67 author report — classify_streams PER-CHANNEL divergence map (host: devin)

Seat: author (ONLY tracked-file writer), lane `game-dev-2d`, declared
axis-move (verbatim brief): map classify_streams' PER-CHANNEL divergence
from merged classify_process as a measured axis: r66 mapped the rejection
surface over merged stdout+stderr; classify_streams scans stderr-only for
errors — the divergence is documented but its contract is unmapped.
Declared falsifiable claim: classify_streams verdicts diverge from
classify_process on exactly the stream-attribution axis — a stdout-carried
ERROR: line is ABSORBED by classify_streams (PASS-shaped) where merged
classification rejects, while stderr-carried ERROR:/signature bytes behave
differently than stdout-carried. Land an additive meta arm (per-stream
records + divergent-verdict pins incl. per-stream seam positions and the
allowlist's per-stream match); battery 88/88 + surface 34/34 must stay
green.

## Outcome — claim CONFIRMED (measured) and REFINED (divergence is four mechanisms, attribution is the headline)

The declared direction measured exactly as claimed: a stdout-carried
`ERROR:` line is **absorbed** by `classify_streams` (stdout is never
error-scanned) where merged classification rejects; stderr-carried
`ERROR:`/signature bytes behave differently than stdout-carried. The
bounded labrat probe's refinement — confirmed live — is that the
divergence set is a strict superset of pure channel placement: four
mechanisms, all now pinned per-stream through BOTH classifiers on the
SAME captured streams:

- **(a) stdout `ERROR:` absorption (headline, merged-FAIL / streams-PASS):**
  `--stdout-error` emits the signature + `ERROR: STREAMDIV stdout-carried
  diagnostic` both on stdout, stderr empty. `classify_process` rejects
  (`unrelated_errors`); `classify_streams` passes — its error scan covers
  only `stderr.splitlines()`. Measured live: `merged=False streams=True`.
- **(b) stderr strictness is broader than merged's (merged-PASS /
  streams-FAIL):** the pre-existing `stream_reject` arm is itself
  divergent — `STREAM_STDERR: unrelated attribution diagnostic` carries
  no `ERROR:` substring, so merged accepts while streams rejects (every
  non-empty stderr line must be allowlisted — `run_battery.py:200-207`).
- **(c) the allowlist's per-stream match is shape-asymmetric
  (merged-PASS / streams-FAIL):** `--stderr-structured` emits a real
  chain-incomplete-shaped stderr line. Under the SAME entry
  `"ERROR: chain incomplete"`, merged's third `allowed_error` branch
  (`run_battery.py:168-171`) absorbs → PASS, while streams' `line_allowed`
  (`run_battery.py:192-198`, exact + `,`-prefix only) rejects → FAIL.
  Under the byte-exact line entry both absorb; under `()` both reject.
- **(d) signature channel (merged-PASS / streams-FAIL):**
  `--sig-on-stderr` puts the signature on stderr; merged finds it in the
  concat → PASS; streams rejects **solely on the signature axis** —
  pinned by running streams with `allowed_stderr=(signature,)`: stderr
  fully allowlisted, still FAIL.
- **(e) seam positions are merged-only artifacts (streams seam-immune):**
  - `--seam-error`: unterminated stdout tail `STREAMDIV seam tail ends in
    ERROR` + stderr head `: STREAMDIV seam phantom merged-only line` →
    merged concat carries `...ERROR: STREAMDIV seam phantom merged-only
    line` (the only merged `ERROR:` line), present in **neither** stream's
    line set (`stdout_tail_line`/`stderr_head_line` pinned). merged=FAIL;
    streams=PASS with the head allowlisted (streams-bare rejects on
    stderr strictness, not the phantom).
  - `--seam-script`: `...SCRIPT ERR` + `OR: ...` fabricates `SCRIPT ERROR:`
    only in merged (`script_error_in_merged=True`, in neither stream) —
    merged=FAIL, streams=PASS.
  - `--seam-sig`: signature split at the seam — merged contains the full
    signature contiguous → PASS; streams sees half on each channel →
    FAIL (signature axis).

Measured divergence table (`runs/20261014T095910487678Z/
stream-attribution-verdicts.json` → `divergence.divergence_table`):

| arm | merged | streams | divergent |
|---|---|---|---|
| stream_accept | True | True | no |
| stream_reject (non-ERROR: stderr) | True | False | **yes** |
| streamdiv_stdout_error | False | True | **yes** |
| streamdiv_stderr_error | False | False | no (control) |
| streamdiv_stderr_structured (under structured entry) | True | False | **yes** |
| streamdiv_sig_on_stderr (stderr allowlisted) | True | False | **yes** |
| streamdiv_seam_error (head allowlisted) | False | True | **yes** |
| streamdiv_seam_script (head allowlisted) | False | True | **yes** |
| streamdiv_seam_sig (head allowlisted) | True | False | **yes** |

Allowlist reclassifications on the same captured streams (no extra runs):
`stderr_error` exact→T/T, foreign→F/F; `stderr_structured` exact-line→T/T,
bare→F/F; `sig_on_stderr` bare→T/F; `seam_error` bare→F/F.

## Labrat spike (dispatched, bounded, read-only)

Exactly one `ufo-labrat` probe pre-landing (probeParent allowance; brief
"bounded labrat spike before tracked edits"). Its tool surface resolved
read-only; it returned the full 11-arm static verdict table against the
verbatim clauses — **11/11 arms matched** the design — plus the mechanism
refinement above (divergence = attribution + allowlist-shape + bidirectional
seam + stderr-coverage asymmetry, not attribution alone) and the
line-reference for streams' deliberate non-`ERROR:` stderr strictness
(comment at `run_battery.py:204-205`). My own corroborating spike
ast-extracted BOTH classifier bodies verbatim
(`corpus/live/r67-author/spike/clause_matrix.py` → `clause-matrix.json`,
sha256 `bd6c14d0…`) and exec'd 14 synthetic stream pairs on a real
interpreter: identical verdicts to the labrat table.

## Landed diff (additive — +321/−2 across two tracked files)

- `corpus/fixtures/stream_attribution_probe.gd` — sha256
  `97143ad367a66e5f625208947c4d479a48d1aa7ce519d0e2de13b4751d288ebe` →
  `dc0b0d5c5f44a1b4404cbe62cada0e6e53e2b33be010ea32dc72cb3892aeb286`,
  **+58/−1**: seven arm flags + constants + banner; the single changed
  line is `print(STDOUT_MARKER)` → if/elif/else emitting the marker via
  `print` (default/`--stderr-unrelated` unchanged), `printerr`
  (`--sig-on-stderr`), or `printraw` head + `printerr` tail (`--seam-sig`).
- `corpus/fixtures/run_battery.py` — sha256
  `76d37ace4b0bbc3c92b83baf431bf6046cdfe4fa88f4bf3cd833dee99269b1ed` →
  `3d5b0721d582a0b9f00b601b1ede5f6c313b700a0a5e9a15d8e09104c7370e7c`,
  **+263/−1**: one additive block inside `if args.probe_stream_attribution:`
  (between `meta_pass` and `probe_payload`) — `dual_classify`/`streamdiv_arm`
  helpers, 7 real-Godot arms, 6 same-capture allowlist reclassifications,
  the 9-row divergence table, **20 discriminations, all True**; the single
  changed line is the row verdict `meta_pass` → `meta_pass and sd_meta_ok`.
  The arm stays inside the opt-in flag: flagless battery row count
  unchanged, `probe_stream_attribution` remains ONE results row.

`classify_process`, `classify_streams`, `classify_audio_process`,
`allowed_error`/`line_allowed`, CASES, and every existing meta row
untouched. Row arithmetic: flagless **88/88** (arm absent — flag-gated),
full-flag **99/99** (same single probe row, extended payload),
`probe_error_clause_surface` **34/34 discriminations** untouched.

## Exact evidence

Flagless battery (canonical root `~/Projects/shokunin/game-dev-2d-shokunin`):
`python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
corpus/live/r67-author/runs` → **exit 0**,
`runs/20261014T095753034446Z/verdicts.json` **PASS 88/88** (sha256
`2726c7b27ba1b261c698d5a5a9d0049de540ce9d3983d4bde6c5690dd118aeed`),
surface meta 34/34; stdout `corpus/live/r67-author/battery.stdout`.

Mandated seven-flag battery (exact invocation):
`python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
corpus/live/r67-author/runs --probe-failing --probe-unrelated-error
--probe-export-launch --probe-godot-error --probe-stream-attribution
--probe-crash-exit --probe-timeout` → **exit 0**,
`runs/20261014T095910487678Z/verdicts.json` **PASS 99/99** (sha256
`5638cd0f272d315254e750e24abe953eb6c336af8d1afaed1a4764427d3cf960`);
stream artifact `stream-attribution-verdicts.json` (sha256 `d65608f9…`)
carries 7 per-stream arm records + 6 reclassifications + 20/20
discriminations; stdout `corpus/live/r67-author/battery-full.stdout`.
Designed inner FAIL lines (`godot_error_unrelated`, `stream_reject`,
mutants) unchanged.

Prior-row stability — 7-field diff `(script, flags, expected_exit,
actual_exit, signature, verdict, error)`:

- vs **same-session pretree** run: HEAD tracked tree materialized
  read-only via `git archive HEAD corpus/fixtures | tar -x` into
  `corpus/live/r67-author/pretree/` (runner sha `76d37ace…`, fixture sha
  `97143ad3…`, both == `git show HEAD:` digests), same 7 flags →
  `pretree-runs/20261014T100102229717Z/verdicts.json` **PASS 99/99**
  (sha256 `9f367eeb…`): **99 common rows, 0 mismatches**, `new-only []`,
  `old-only []` — divergence data is payload-level, not row-level.
- vs **r67 baseline receipt**
  `corpus/live/r67-baseline/runs/20261014T094859374505Z/verdicts.json`
  (frozen HEAD replay, flagless): **88 common rows, 0 mismatches**;
  `probe_error_clause_surface` discrimination key-set identical, all-True
  in both.

Separate leg: `--fault-injection` → **exit 0**,
`fault-runs/20261014T100114730473Z/fault-verdicts.json` outer **PASS**
(sha256 `cd49178d…`), designed inner `fault_hang`/`fault_unrelated_error`
FAILs unchanged.

Smoke (pre-battery): each new flag run directly against
`corpus/fixtures` produced the designed byte placement — unterminated
stdout tails and stderr heads verified byte-exact via `cat -A` capture.
No LSP server answers either file (only clangd installed; no Python or
GDScript language server configured) — text edit was the only path; the
change is additive blocks with no cross-file rename.

## Files written (inside brief scope only)

- tracked: `corpus/fixtures/stream_attribution_probe.gd` (+58/−1),
  `corpus/fixtures/run_battery.py` (+263/−1)
- report: `reports/round-67/r67-author.md` (this file)
- scratch: `corpus/live/r67-author/{labrat/probe-report.md,
  spike/{clause_matrix.py,clause-matrix.json},
  pretree/, pretree-runs/, pretree-battery.stdout/.stderr, runs/,
  battery.stdout/.stderr, battery-full.stdout/.stderr, fault-runs/,
  fault.stdout}`

## Remaining risks / blockers

- **Claim refinement is deliberate, not softening:** the brief's
  "exactly the stream-attribution axis" confirmed in direction; the map
  additionally pins the allowlist-shape and seam mechanisms as
  independent divergence causes (both classifiers' own clause sets, not
  just channel routing). Recorded as measured data, all 20 pins gated.
- **Stream-merge ordering:** seam fabrications rely on the runner's fixed
  `stdout + stderr` concat order (`run_battery.py:152`); a consumer
  concatenating `stderr + stdout` fabricates different phantoms — same
  caveat as r66.
- **Streams' coverage asymmetry is per-channel:** it is simultaneously
  looser (stdout `ERROR:` unpoliced) and stricter (any non-allowlisted
  stderr line, `ERROR:` or not) than merged — not a uniform tightening;
  a consumer must not assume `classify_streams` implies merged-PASS.
- **`printerr`/`printraw` semantics are Godot-4.7.2-headless-measured:**
  byte placement verified on this host only; other versions/platforms
  unmeasured (bounded_claim in payload says the same).
- No blockers. Commit/push left to operator per seat rules.
