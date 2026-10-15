# Round 67 critic report — per-channel divergence of classify_streams vs classify_process

Seat: critic, lane `game-dev-2d`. Repo `~/Projects/shokunin/game-dev-2d-shokunin`
(reached via `~/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d` symlink).
All commands resolve on this host; harness + receipts under
`corpus/live/r67-critic/`.

## Landed-state caveat (provenance, blocking the literal brief)

At review time **no r67 author diff has landed**: `git status --porcelain` shows a
clean tracked tree at HEAD `4a4def9` (r66 report-last); `corpus/live/` holds
`r67-baseline/` + sibling seat scratch only; `reports/round-67/` holds
`r67-baseline.md` only. There is no `corpus/live/r67-author/` and no
`reports/round-67/r67-author.md`. I therefore attacked the declared claim
directly against the committed classifiers — the strongest counterexample
available from local evidence — exactly per r66 critic convention: my probe
execs `classify_process` + `classify_streams` **verbatim** (AST
`get_source_segment` + dedent, `extract_classifiers.py`), never re-implements.

Measured against tracked `corpus/fixtures/run_battery.py`
sha256:`76d37ace4b0bbc3c92b83baf431bf6046cdfe4fa88f4bf3cd833dee99269b1ed`
(166591 B). Extracted function digests:
`classify_process` sha256:`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`,
`classify_streams` sha256:`a886968fd3acf4dec4192e8141de44f0da7dddec9aacfceb5f5d3cafab68c6d7`.

## Verdict on the declared claim — core mechanism CONFIRMED on real bytes;
## "exactly the stream-attribution axis" FALSIFIED (4 unmapped mechanisms)

The claim has two halves. Half 1 — "a stdout-carried `ERROR:` line is ABSORBED
by classify_streams (PASS-shaped) where merged classification rejects" — is
confirmed at both levels:

- **Synthetic, verbatim classifiers** (`matrix_probe.py` row
  `A_stdout_error_absorbed`): stdout=`"SIG: expected marker\nERROR: injected
  diagnostic\n"`, stderr empty → merged `False`, streams `True`.
- **End-to-end, real `godot --headless` 4.7.2** (`e2e_probe.py` case
  `stdout_error`, receipt `e2e_results.json`): probe emits sig + `ERROR:
  stdout carried diagnostic` via `print()` on stdout → merged `False`,
  streams `True`. `classify_streams` never line-scans stdout (l.183-189 check
  signature + `SCRIPT ERROR:`/`Parse Error:` substrings only).

Half 2 — "diverge on **exactly** the stream-attribution axis" — is falsified.
My 23-row matrix (`matrix_results.json`) measures **12 divergent rows in 4+
distinct clause-level mechanisms**, and at least three of them involve zero
`ERROR:`/signature placement:

| mechanism | example row | merged | streams | clause responsible |
|---|---|---|---|---|
| stdout `ERROR:` invisibility (claimed) | A, R, U | FAIL | PASS | streams scans stderr only |
| signature must be stdout-bound | E | PASS | FAIL | l.183 `signature not in stdout` |
| **every stderr line must be allowlisted** | K, L | PASS | FAIL | l.200-207 sweep — fires on `WARNING:`/plain text with **no error markers at all** |
| **allowlist-matcher asymmetry** | N | PASS | FAIL | `"ERROR: chain incomplete"` structured matcher exists only in merged `allowed_error` (l.168-171); `line_allowed` (l.192-198) drops it |
| seam-concatenation fabrication | G, H, J | both dirs | both dirs | `proc.stdout + proc.stderr` literal concat (l.152) |
| allowlist scoping | P, Q | both dirs | both dirs | `allowed_errors` vs `allowed_stderr` are separate tuples |

So the divergence surface is **strictly larger** than the declared axis. Rows
K/L are not "ERROR:/signature bytes behave differently by stream" — they are a
third rejection clause (whole-stderr sweep) firing on benign bytes. Row N is a
matcher-parity defect, not stream placement. An arm that pins only
ERROR:/signature placement and calls the surface "mapped" leaves these
undiscriminated — that is the counterexample the arm must answer.

## Answers to the five assigned attacks

**(1) stdout-ERROR absorption real?** Yes — verbatim + real-Godot evidence
above. Additionally the absorption is *unconditional*: no `allowed_stderr`
value can make streams see a stdout `ERROR:`, and a signature that itself
contains `ERROR:` (row U) is a streams-only PASS because merged line-scans its
own signature line.

**(2) signature scanned on stdout in both directions?** `classify_streams`
requires the signature on **stdout** (l.183); merged accepts it anywhere in
`stdout+stderr`. Both directions measured: sig-on-stderr-only → merged PASS /
streams FAIL (real bytes: `e2e_results.json` case `sig_on_stderr`);
sig-on-stdout → both PASS (modulo other clauses).

**(3) per-stream allowlist matching.** Measured answer to "does an
allowlisted stderr error absorb where merged would reject a stdout twin?": the
asymmetry is inverted from the natural guess — a *stdout* twin absorbs under
streams unconditionally while merged needs the entry; a *stderr* error absorbs
under streams only if in `allowed_stderr` (and under merged only if in
`allowed_errors`). Discriminating rows P/Q require **asymmetric** allowlists;
if the arm passes the same tuple to both classifiers, P/Q collapse to agree
and the only observable allowlist divergences are N and the real-`push_error`
case below. Separately: **`allowed_stderr` can never admit a real Godot
`push_error`** — measured on real bytes: allowlisting `ERROR: stderr pushed
error` in both classifiers gives merged PASS / streams FAIL, because the
engine's `   at: push_error (core/variant/variant_utility.cpp:1023)` +
`GDScript backtrace` + `[0] _initialize (res://…)` context lines are
unallowlistable dynamic stderr text (`e2e_results.json`; direct reclassification
printed `merged=True streams=False`).

**(4) divergence the arm does not discriminate** — the strongest set:
- **Seam-forged `ERROR:`** (`seam_capture_probe.py`, `seam_results.json`):
  real `subprocess.run` capture, stdout `…marker\nERR` (no trailing newline) +
  stderr `OR: allowlisted tail\n` → merged text contains `ERROR: allowlisted
  tail`, a line that exists in **neither** stream → merged FAIL, streams PASS.
  A streams-only PASS caused by a line the process never emitted — pure
  capture artifact.
- **Seam-forged signature**: sig split `CRITIC_E2E` | `: expected marker`
  across the same seam → `sig_in_merged=True`, in neither stream → merged
  PASS, streams FAIL.
- **Seam-forged `SCRIPT ERROR:`** (matrix row J): `SCRIPT ERR`|`OR: benign`
  (allowlisted) → merged FAIL via the l.177 blob conjunct, streams PASS.
- **Benign stderr strictness** (K, L; real bytes `stderr_warning` case):
  `WARNING: benign stderr chatter` → merged PASS / streams FAIL.
- **Structured-entry drop** (N): `"ERROR: chain incomplete collections=1
  scene=SceneB:<Node#7> old_alive=false"` on stderr under entry `"ERROR: chain
  incomplete"` in *both* allowlists → merged PASS (l.168-171 matcher), streams
  FAIL. `classify_streams`' allowlist is not a faithful port.
- **ObjectDB trap** (latent, not in matrix): `classify_audio_process`'s
  leaked-ObjectDB clause (l.210-217) has no counterpart in `classify_streams`;
  routing audio captures through streams silently drops that clause.

**(5) timing/provenance confound** — the seam is *not* drain-order dependent;
it is worse: `subprocess.run(capture_output=True)` → `communicate()` drains
both pipes but yields each as one block, and `run_process` merges by literal
`proc.stdout + proc.stderr` (l.152). The seam position is deterministically
`len(stdout)`; what the concat destroys is *all* interleave provenance — a
stderr line emitted before every stdout byte still lands at the end of
"merged". A "per-stream seam position" pin therefore records a byte offset in
a Frankenstein buffer, not an emission-time fact; and the *content* at the
seam depends on whether stdout is newline-terminated, which the fixture (not
the pipe scheduler) controls. Fixture-side, GDScript `print()`/`printerr()`
always newline-terminate, so a real seam-split arm needs a raw-writing child
(descendant pattern) — my `FileAccess('/dev/stdout')` attempt inside the probe
did not land (`e2e_results.json`, `stdout_no_newline`), so I demonstrated the
seam through a real `subprocess.run` capture of a non-newline-terminated
writer instead.

## Impacted axes

- **measured-axis coverage**: "exactly the stream-attribution axis" overclaims;
  ≥4 clause-level mechanisms diverge, two of them not ERROR:/signature-shaped.
- **verdict correctness / hidden regression**: any future routing of CASES
  rows through `classify_streams` inherits the stderr sweep (engine `at:`/
  backtrace lines make real `push_error`s unallowlistable) and loses the
  structured allowlist entry + audio ObjectDB clause.
- **provenance**: seam-position pins are capture-concat offsets, not timing
  evidence; an arm presenting them as emission order would be false provenance.
- **identity/provenance of the diff itself**: at review time there is nothing
  to diff — verdicts on the *arm's pins* are necessarily deferred to verifier.

## Smallest safe corrections

1. Reword the claim to enumerate mechanisms, not one axis: stdout-`ERROR:`
  invisibility; signature stdout-binding; whole-stderr sweep; allowlist-matcher
  parity (`"ERROR: chain incomplete"` dropped); seam concat artifacts. Drop
  "exactly" or scope it to "these enumerated clauses".
2. If the arm pins "per-stream allowlist match", include (a) the structured
   entry on stderr — streams rejects where merged absorbs; (b) one real
   `push_error` row — provably unallowlistable under streams on this host —
   or document `allowed_stderr` as exact-text-only by contract.
3. Mark seam rows as capture artifacts: pin `seam_offset == len(stdout)`,
   state merged-order is not temporal, and generate split bytes with a
   non-newline-terminated writer (child/descendant raw write), since in-probe
   `/dev/stdout` FileAccess did not land.
4. Keep `classify_streams` out of `audio_playback`'s path, or port the
   leaked-ObjectDB clause — a silent swap regresses a green clause.
5. Either pass deliberately asymmetric allowlists in the arm (to expose P/Q)
   or pin the single-tuple contract explicitly — same-tuple arms cannot see
   the scoped-allowlist divergence.

## Evidence index

- `corpus/live/r67-critic/extract_classifiers.py`, `verbatim_classifiers.py`
  (AST-verbatim extraction, sha256s above)
- `corpus/live/r67-critic/matrix_probe.py` → `matrix_results.json`
  (23 rows, 12 divergent; command `python3 matrix_probe.py`, exit 0)
- `corpus/live/r67-critic/critic_e2e_probe.gd`, `e2e_probe.py` →
  `e2e_results.json` (`godot 4.7.2.stable`, `/usr/bin/godot`, exit 0;
  `stdout_error`/`stderr_warning`/`sig_on_stderr` divergent on real bytes)
- `corpus/live/r67-critic/seam_capture_probe.py` → `seam_results.json`
  (real `subprocess.run` capture; forged `ERROR:` and forged signature
  confirmed, exit 0)
- Clause refs: `corpus/fixtures/run_battery.py` l.152 (merged concat),
  l.160-177 (`classify_process` + structured entry l.168-171 + blob conjuncts
  l.177), l.179-208 (`classify_streams`: stdout-bound sig l.183, substring
  clauses l.185-187, stderr sweep l.200-207), l.210-217 (audio ObjectDB),
  l.2200-2219 (only existing `classify_streams` call site)
- Baseline cross-check: `corpus/live/r67-baseline/runs/20261014T094859374505Z/
  verdicts.json` — 88/88 PASS on the pre-r67 tree.

Stop. No verdict on admissibility — that is the canonical judge's call.
