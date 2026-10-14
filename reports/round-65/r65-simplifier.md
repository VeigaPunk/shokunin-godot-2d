# Round 65 simplifier report — forged-REJECTION dual audit (host: devin)

Seat: simplifier (LEAF, audit-only this round — write scope is this report +
`corpus/live/r65-simplifier/`; tracked-file edits are author-owned).
Subject: the landed r65 diff — `corpus/fixtures/descendant_pipe_probe.gd`
(+35/−0) + `corpus/fixtures/run_battery.py` (+431/−0), additive-only block
`run_battery.py:1107-1537` + fixture arms at
`descendant_pipe_probe.gd:42-61,73-75,80-84,97-100`.

## Verdict: boundary is pinned; minimal-expression bar met with 2 wash
## discriminations and 3 micro-dup candidates flagged; 1 small missing add.

Deletions made: **none** (audit seat — no tracked edit scope; the shared tree
is byte-identical to the author's landing, sha256 `1acbc73d…`/`37cf5015…`
re-verified post-audit).

## Preserved contract — independently re-verified, not trust-relayed

- Own battery re-execution (prior partial work in this scratch, completed):
  `corpus/live/r65-simplifier/runs/20261014T023657880557Z/verdicts.json` →
  **PASS, 98 rows**; `battery-exit.txt` `EXIT=0`;
  `battery.stdout` line `PASS descendant error-spoof meta`.
- Byte-stability (own field-diff, full row dicts on
  `(case,script,flags,expected_exit,actual_exit,signature,verdict,error)`):
  vs `corpus/live/r65-baseline/runs/20261014T022523005280Z/verdicts.json`
  (PASS 97) → **shared=97, mismatches=0, new_only=[probe_descendant_error_spoof],
  base_only=[]** (`field-diff-vs-baseline.txt` — earlier keyed variant agreed:
  shared=96 mismatches=0 under its narrower keying).
- All **28 discriminations True** on my run's record (extracted verbatim to
  `meta-row-evidence.json.txt`): forged release `inner_classification=False` /
  `stripped_classification=True`; genuine control identical on all
  `cases_visible` fields; 3 gated reps all `dead_observed_at <
  error_observed_at` with `gated_signature_accepted=True`; split
  stdout/stderr stream split confirmed.

## Duplication audit — "shared helper vs three copies"

1. **Fixture reparent-gate shell literal — 3 byte-identical copies**
   (`descendant_pipe_probe.gd:89,96,100`; count verified: the literal
   `while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"" +
   str(OS.get_process_id()) + "\" ]; do sleep 0.05; done;` occurs exactly
   3×). The r65 arm added the third copy rather than extracting a shared
   `var reparent_gate := …` local. **Candidate (deferred-keep):** extracting
   the local is behavior-preserving by construction (identical argv, statically
   provable) and would delete ~2×130 chars; deferred because each arm's literal
   stays greppable in a flat fixture and the win is ~260 bytes. If a 4th
   reparent-gated arm ever lands, extract then — three copies is the trigger,
   this is the borderline case.

2. **`gated_errforge_run` (run_battery.py:1226-1346) is a 121-line fork of
   `gated_signature_run` (:901-1009, 109 lines)** — normalized similarity
   0.77 (difflib, field-name normalization; ~90 plumbing lines identical:
   Popen+selector loop, deadline, `dead_observed_at`, close/wait/kill, pid
   parses, liveness, acceptance, classification). The semantic delta is real:
   per-chunk liveness of a SECOND marker must be captured at read time and
   cannot be derived post-hoc from `gated_signature_run`'s record — so a plain
   reuse call could never produce `child_alive_at_error_observation`.
   **KEEP the fork.** The only alternative — a parameterized
   `gated_marker_capture(markers=[…])` shared by both — would rewrite the
   pinned, verifier-audited r64 function and its record-field set to save ~80
   lines; that trades the byte-stability/audit axis for weight. Stop rule hit:
   the next deletion (the fork) would harm an axis. Consolidation candidate
   only if a third marker-tracked runner lands.

3. **Marker literal — 4th named copy:** `"DESCENDANT_PIPE_PROBE: expected
   signature"` now at `run_battery.py:98,104` (CASES signature column,
   intrinsic) and `:565,:712,:893,:1133` (`pipe_marker`, `spoof_marker`,
   `gate_marker`, `errforge_signature`). `errforge_signature = gate_marker`
   is a free alias — micro-candidate, ~zero risk.

4. **`ERRFORGE_ERROR` duplicates `ERRFORGE_ERROR_BODY` text**
   (`descendant_pipe_probe.gd:66-67`): `const ERRFORGE_ERROR := "ERROR: " +
   ERRFORGE_ERROR_BODY` folds constant-expressible in GDScript — micro-candidate.

5. **Not duplication:** `errforge_run` is the FIRST factored bounded-Popen
   runner (r62/r63 used inline blocks at `:580-`,`:716-779`); reusing it for
   3 arms is good hygiene, and folding the r63 inline block into it would
   perturb pinned `probe_descendant_signature_spoof` record fields —
   correctly not attempted. `split_errforge_run` used 2×, gated fork 5×,
   `errforge_run` 3× — each helper earns its place.

## Wash discriminations vs real-family killers (28 total)

**Drop candidates (verdict-neutral, purely redundant):**

- `hold_descendant_orphaned_alive` — logically subsumed by
  `hold_write_ppid_kernel_corroborated`: `kernel_ppid() == write_ppid` requires
  a live `/proc` read at return; `pid_alive` (kill(0)) cannot falsify anything
  the kernel check doesn't already. If the /proc read fails the row fails on
  the corroboration clause anyway — this key never changes the verdict.
- `gate_error_axis_timing_split` — a pure conjunction of clauses already
  asserted inside `gate_release_forged_error_observed_post_death`
  (all release `child_alive_at_error_observation is False`) and
  `gate_genuine_error_observed_while_live` (all genuine True). Every
  falsifying family is a strict subset of the two siblings. Documentation
  sugar only.

**Borderline keep:** `gate_does_not_reject_forged_error_arm` is ~2/3
redundant (`gated_signature_accepted` ∈ #21, `error_observed` ∈ #22) but its
third clause — inner classification False while the gate accepts — is the
headline asymmetry expressed atomically. Keep; a slimmer
`all(r["inner_classification"] is False for r in ef_gate_release)` would carry
the same family.

**Real-family killers (keep, credited):** the four release premises;
`release_flips_to_fail` + `release_counterfactual_passes_without_error`
(claim + sole-cause isolation); the genuine trio including
`genuine_counterfactual_passes_without_error` (kills "push_error rejects via
extra diagnostics" — its backtrace/`at:` lines contain no `ERROR:`);
`error_marker_bytes_identical`, `forged_vs_genuine_cases_fields_identical`,
`forged_vs_genuine_differ_only_in_provenance` (the falsifiable-claim trio);
`detached_control_row_still_passes` (the only in-row guard that the shared
elif chain didn't regress a pinned CASES arm); the hold set minus the wash;
`gate_release_signature_accepted_while_live`,
`gate_release_forged_error_observed_post_death` (dead≤error ∧ alive=False —
the brief's feared missing post-death discrimination **is present**),
`gate_genuine_error_observed_while_live`; the stream-split trio.

## Missing adds

1. **`hold_timeout_alone_rejects`** — the one real gap. The row documents
   "double-axis rejection (error + timeout)" but `hold_rejects` alone cannot
   distinguish timeout-caused from error-caused rejection; the discriminating
   field `stripped_classification=False` IS captured in the record (verified:
   `hold_arm.stripped_classification == False` in my run) but **no
   discrimination asserts it**. One line —
   `"hold_timeout_alone_rejects": ef_hold["stripped_classification"] is False`
   — pins the second axis instead of leaving it narrative. Small, real.
2. Post-death proof — NOT missing: `release_error_write_post_orphan`
   (reparent ppid provenance) + gated `dead_observed_at ≤ error_observed_at`
   both present and True.
3. Multiset caveat checked and discharged: the provenance diff uses **set**
   symmetric difference (multiplicity-blind). On my measured records the
   multiset diff equals the set diff exactly (n=9, all provenance,
   `non_provenance multiset diff = []`) — theoretical gap only on this
   fixture's outputs.
4. Nit, non-issue: the orphan-hygiene loop covers all hold-class descendants
   plus every gated/ungated release descendant it records; the two split-run
   descendants are release-class (immediate self-exit, no fd hold) — no
   lingering orphan window beyond microseconds.

## Evidence paths (all host-resolvable)

- `corpus/live/r65-simplifier/{pre-diff-sha256.txt,pre-diff-status.txt,
  tracked-diff.patch,tracked-sha256.txt}` — pre/landed digests, additive-only
  patch (+466/−0).
- `corpus/live/r65-simplifier/runs/20261014T023657880557Z/verdicts.json`
  (PASS 98), `battery.stdout`, `battery-exit.txt` (EXIT=0),
  `field-diff-vs-baseline.txt`, `meta-row-evidence.json.txt`.
- `git diff --stat`: 2 files, 466 insertions(+), 0 deletions; working-tree
  sha256 `1acbc73d…`/`37cf5015…` == author report digests.
- Caller analysis: no `lsp` device exists in this seat's surface and no
  language server answers these fixtures (Python/GDScript, none configured —
  same finding as r65-author §Evidence); text-grep is the disclosed literal
  fallback: zero references to `errforge*`/`probe_descendant_error_spoof`/
  `spawn-errforge`/`emit-errforge` outside the two touched files (only
  reports cite the row name — provenance, not callers); all new helpers are
  block-local defs consumed in-block (call sites `:1382-1394,:1449`).

## Tradeoffs

- Accepted ~90 duplicated plumbing lines (`gated_errforge_run` fork) to keep
  r64's pinned runner and record shape untouched — correct for this round;
  consolidation is a third-variant trigger.
- Accepted a third copy of the fixture reparent-gate literal (small, literal,
  greppable) — the cheapest follow-up micro-edit if weight matters.
- The two wash discriminations cost nothing but inflate "28
  discriminations" to an effective 26 falsifying claims; dropping them loses
  no coverage.
- The `hold_timeout_alone_rejects` add is the only place where one more line
  converts a documented claim into an asserted one — recommend landing it if
  the diff is reopened for any reason.
