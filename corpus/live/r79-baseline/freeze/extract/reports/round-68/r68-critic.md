# Round 68 critic report — midlineforge fabrication-window "bound" + r67
# receipt-shape upgrades

Seat: critic, lane `game-dev-2d`. Repo `~/Projects/shokunin/game-dev-2d-shokunin`
(reached via `~/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d` symlink).
All commands resolve on this host; harness + receipts under
`corpus/live/r68-critic/`.

## Landed-state caveat (provenance, blocking the literal brief)

At review time **no r68 author diff has landed**: `git status --porcelain`
shows a clean tracked tree at HEAD `1101cb3` (r67 report-last);
`corpus/live/` holds sibling-seat scratch only (`r68-baseline`,
`r68-boundary`, `r68-reviewer`, `r68-scout`, `r68-scribe`,
`r68-simplifier`, mine); `reports/round-68/` holds `r68-baseline.md` only.
No `corpus/live/r68-author/` and no `r68-author.md`. Per r66/r67 critic
convention I attacked the declared claim directly against committed code —
a byte-faithful parameterized replica of the tracked midlineforge arm plus
VERBATIM AST-extracted classifiers (no re-implementation).

Measured against tracked `corpus/fixtures/run_battery.py`
sha256:`8d7e4d946e419c8f2fd4c8890cc2d3286f009b8434abc27392724d903c8a4634`
(182,056 B); `descendant_pipe_probe.gd`
sha256:`92a40d70e31daa5048a4c49864d4ece276fbfbac8cb93f2cc6751c6c798caa91`;
`stream_attribution_probe.gd`
sha256:`dc0b0d5c5f44a1b4404cbe62cada0e6e53e2b33be010ea32dc72cb3892aeb286`.
Extracted function digests (unchanged since r67):
`classify_process` sha256:`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`,
`classify_streams` sha256:`a886968fd3acf4dec4192e8141de44f0da7dddec9aacfceb5f5d3cafab68c6d7`.

## Verdict on the declared claim — the window is REAL, the "strict measured
## bound [lo,hi)" is FALSIFIED three ways

**What is true:** the fabrication window is a real temporal interval —
the interval between the child's two atomic `write()` syscalls on the
stdout pipe. strace evidence (`strace-timing.json`): `printraw(head)` is
one `write(1,"DESCENDANT_PIPE_PROBE: expected ",32)`, `print(tail)` one
`write(1,"signature\n",10)`, and `OS.delay_msec(200)` yields a pipe gap of
**200.126–200.162ms** (n=12, σ≈0.01ms). The descendant's
`write(1,"ERROR:…\n",45)` + `write(1,"…write_ppid=…",43)` pair (~0.02ms
apart) lands inside iff ordered between them. Kernel FIFO ordering by
`write()` call order — no read-loop granularity is involved anywhere
(see attack 2).

**What is false about "strict measured bound":**

- **(a) The hi edge is stochastic, ~1ms wide — not strict.** Nominal-offset
  reps at the true edge produce MIXED outcomes at the SAME offset
  (`edge-mixed-results.json`): offset 198.2 → 12/15 `midline_splice` +
  3/15 `post_tail`; 198.5 → 2/15 splice + 13/15 post; 198.8 → 15/15 post.
  The measured nominal hi on this host is ≈198.3–198.5ms, **not 200** —
  and the transition zone means no nominal offset is a clean separator.
  Jitter widens it further under perturbation: the same nominal 197 run
  under `strace -f` (ptrace adds ~1–2ms to the descendant exec path)
  flipped 1/3 reps to post_tail (`strace-grid.json`), and the whole
  unstraced edge sits ~1.7ms earlier than the straced one.
- **(b) The lo edge is unmeasurable by this arm — and below it is a
  categorically different record.** In nominal-offset units the lo edge is
  ≈ **−1.7ms** (negative): at nominal 0 the descendant write still lands
  ~+2.8ms AFTER the head write because `sh`+`/usr/bin/sleep` exec overhead
  (~1.7–2.9ms) dwarfs the child's `spawned_pid`→`printraw` lead (~0.03ms).
  `sleep` cannot go negative, so a nominal-offset ladder CANNOT reach the
  lower edge — a "splice at offset 0" reading measures the domain floor,
  not a bound. It is not scheduling-flippable either: `taskset -c 0`
  single-CPU contention still spliced 12/12 at offset 0
  (`lo-contended-results.json`) — the asymmetry is ~2 orders of magnitude.
  Below the temporal edge the outcome is NOT "fabricated line lands
  inside": it is `pre_head_standalone` — order E-E2-H-T, the ERROR line
  standalone and **the signature fully intact** (8/8 deterministic via a
  20ms head-stagger, `below-window-results.json`) — a different corruption
  profile (error-scan-only FAIL, no signature destruction, no midline
  splice). The claim's "below gap → fabricated line lands inside" is
  literally false for the sub-lo regime the ladder cannot see.
- **(c) The declared grid resolves hi to at best (160,240] — 40% of the
  window.** On this host {0,40,80,120,160} splice 10/10 each, 240 goes
  `post_tail` 10/10 (`declared-grid-results.json`). My denser sweep puts
  the true nominal edge inside (198,198.8). A "strict bound" claim from
  that grid overstates resolution by ~80×.

**The "misses or truncates" half-claim is also imprecise.** The descendant
write never misses the CAPTURE at any tested offset: the descendant holds
the stdout write-fd, `communicate()` drains until pipe EOF, so the error
line always lands — at/over-gap it lands AFTER an intact signature
(`post_tail`, `sig=True`, cls still False via error-scan). Nothing
"truncates": writes are atomic (≤PIPE_BUF), the tail is one 10-byte
`write()`. The ladder predicate is positional (lands midline vs not), not
existential. Additionally a third ordering `H<E<T<E2` exists structurally —
the ppid echo (~20–45µs behind E, `strace-timing.json` `err_to_ppid`) can
straddle the tail write — which the binary "lands/misses" grid cannot
express (unobserved at my ~1ms edge resolution; structural, reported for
completeness).

**What the ladder CAN honestly claim:** on an unloaded host the nominal
window is ~(0,198.4) — an affine-shifted image of the true temporal window
(0,~200.13), shifted by descendant-exec overhead (~1.7ms) that is itself
jittered. The temporal bound is real; the nominal bound is an artifact of
the measurement vehicle.

## Answers to the four assigned attacks

### (1) Real bound or point sample dressed as one?

The WINDOW is real; the BOUND as measurable via nominal offsets is mostly
dressed-up. The r66 80ms point sample generalizes honestly only to
nominal offsets ∈ [0,~196] on this host — the rep-stable interior. At the
edges the outcome is Bernoulli (198.2: 80% splice; 198.5: 13%); the lo
edge is unreachable (~80:1 latency asymmetry, unflippable even under
taskset contention). A claim of "strict [lo,hi)" is falsified; a claim of
"interior rep-stable, edge ~1ms stochastic, nominal hi ≈ gap −
descendant-overhead" is what the data supports. Rep-variance does not
collapse the INTERIOR edges — it erases the strictness claim at the
boundaries.

### (2) Signature gap or read-loop tick?

The signature gap — unambiguously, and I can prove there is no read-loop
to confound it. `surface_run` (run_battery.py:1606-1611) and my ladder
both use `communicate(timeout)`: the kernel buffers both pipes FIFO and
the capture yields whole strings post-hoc; "merged" is literal
`stdout+stderr` concat (l.152/1611). Ordering is fixed at `write()`-call
time; Godot emits head/tail as single atomic writes with no stdio
buffering delay (strace `write()` evidence above). The pipe-measured gap
is ~200.13ms ≈ delay primitive, NOT a sampling tick. What DOES confound
the ladder is the WRITE side: the descendant's effective offset = nominal
+ exec overhead (~1.7–3ms, jittered) relative to a head-write that lands
only ~30µs after the `spawned_pid` print — the nominal→temporal map is an
affine shift with ~±0.5ms noise, which is exactly why the edge reads
~198.4 nominal instead of 200.

### (3) `divergent_clause` — distinguish or rename?

Mostly rename, with one enum hole — measured on verbatim classifiers
(`clause-sig-results.json`):

- **Coverage gap (F1):** the pre-existing `stream_reject` divergence — a
  plain non-`ERROR:` stderr line — has NO honest member in
  `{exit,signature,error_scan,blob,allowlist_shape}`: merged=True /
  streams=False via the whole-stderr sweep (l.200-207). F1b: the same row
  under the SAME entry on both sides → concordant, so it is not an
  entry-shape asymmetry; the clause does not exist in merged at all. The
  enum needs a sixth member (`stderr_sweep`) or `stream_reject` gets a
  lying label.
- **Collisions (F2):** two mechanically distinct divergences map to one
  label — real sig-on-stderr bytes vs concat-FABRICATED signature both →
  "signature" (F2a/F2b both merged=True/streams=False); real stdout
  `ERROR:` vs seam-fabricated `ERROR:` both → "error_scan" (F2c/F2d). The
  signature cannot distinguish exist-in-wrong-channel from
  exists-in-no-stream.
- **Masked clauses (F3):** sig-on-stderr + unallowlisted stderr line →
  streams exits at l.183 before the l.200 sweep; a first-fail signature
  reports {signature} while {signature,stderr_sweep} is honest — the
  clause signature is order-semantics-dependent, spec doesn't fix which.
- **Dead member (F4):** `exit`/`error` gates are logically identical in
  both classifiers (l.181-182 vs l.176) — a divergent verdict requires
  identical gate outcomes, so `exit` can never be a divergent clause;
  1/5 of the enum is unreachable.
- **F5:** concordant-FAIL rows with different clause paths (merged fails
  on ERROR-scan, streams on sweep) are invisible — the signature
  conflates verdict agreement with mechanism agreement.

### (4) sha256 same-input gate — gameable?

Yes on the declared axis, and vacuous as implemented
(`hash-gate-results.json`):

- **G1 delivery-order blindness (the real gap):** two REAL subprocess
  captures with opposite emission order (stderr-first vs stderr-last,
  50ms apart) yield byte-identical (stdout,stderr) → **identical
  sha256 pairs**. The hash binds bytes, never delivery timing — the exact
  provenance question the seam arms exist for. Same-hash/different-
  timing is the norm, not an edge case.
- **G2 tautology:** `dual_classify` feeds the SAME string objects to both
  classifiers (l.2284-2287) — hash equality is guaranteed by call
  construction; the gate witnesses a fact already certain, and can only
  ever catch post-hoc field mutation, not input sameness.
- **G3 partial input:** the verdict depends on ≥5 inputs; hashes cover 2.
  Same byte-hashes across `bare`/`entry_both`/`entry_merged_only`
  allowlists give verdict pairs (False,False), (True,False), (True,False)
  — "same input" certifies bytes while an unhashed input flips verdicts.

## Impacted axes

- **measured-axis coverage**: the fabrication-window ladder as declared
  (6 nominal offsets) measures a ~40ms-resolution bracket on a ~1ms-wide
  stochastic edge; "strict bound" is falsified — interior-stable,
  edge-Bernoulli is the measured truth.
- **verdict correctness / hidden regression**: if the arm reports
  `lands=True` keyed on `midline_spliced`-equivalence it is correct at
  interior offsets but silent about the three-way outcome taxonomy —
  `pre_head_standalone` and `post_tail` both keep the signature intact
  yet are opposite mechanisms; a binary lands/misses column erases the
  distinction that makes the window a window.
- **receipt-shape quality**: `divergent_clause` as a 5-member enum
  under-covers (stream_reject unlabelable) and over-collapses
  (exist-vs-fabricate); `sha256(raw_*)` certifies storage bytes, not
  classified input timing, and not the allowlist inputs.
- **provenance**: nominal-offset edges are exec-overhead-shifted images
  of the true write()-time edges (~1.7–3ms on this host, ptrace-sensitive
  — a verifier re-running under different load sees a shifted edge);
  reporting them as THE bound without the shift constant is
  misprovenanced measurement.

## Smallest safe corrections

1. Report the window in **temporal** terms with the measured shift: e.g.
   "nominal-offset window (lo_n,hi_n) ≈ (−1.7,198.4)ms maps to pipe-write
   window (0,200.13±0.02)ms; nominal hi = gap − descendant-exec-overhead
   (~1.7ms, jittered)". Include rep-counts at edge offsets (198.x mixed
   outcomes) instead of a single verdict per offset.
2. Widen the outcome column to the 3-way taxonomy
   {pre_head_standalone, midline_splice, post_tail} (+ straddle slot) —
   or rename the axis to "splice window"; do not call pre/post "misses".
3. `divergent_clause`: add `stderr_sweep` member (or relabel enum to the
   actual clause DAG); split exist-vs-fabricate (e.g.
   `error_scan` vs `seam_fabricated_error`, `signature` vs
   `seam_fabricated_signature` — the *_in_stdout/_in_stderr/_in_merged
   fields already discriminate this); declare first-fail vs all-clauses
   semantics; drop or justify dead `exit`.
4. sha256 gate: keep it (cheap self-consistency witness) but rename to
   what it certifies — `captured_bytes_sha256`; if input-timing
   provenance is wanted it needs per-write timestamps, which the capture
   shape cannot provide — say so in the record.

## Evidence index

- `corpus/live/r68-critic/verbatim_classifiers.py` — AST-verbatim
  extraction (digests above); `extract_classifiers.py`
- `corpus/live/r68-critic/proj/{project.godot,critic_midline_probe.gd}` —
  byte-faithful parameterized midlineforge replica
- `corpus/live/r68-critic/midline_ladder.py` → `declared-grid-results.json`
  (declared grid ×10 reps), `edge-hi-results.json` (170–210 ×15),
  `edge-mixed-results.json` (**mixed outcomes at single offsets**),
  `below-window-results.json` (8/8 pre_head_standalone via head-stagger),
  `lo-contended-results.json` (12/12 splice under taskset -c 0),
  `straddle-hunt-results.json`, `smoke-results.json`
- `corpus/live/r68-critic/strace_window.py` → `strace-timing.json`
  (write() µs timestamps: gap_on_pipe 200.126–200.162ms, eff_offset =
  nominal+~2.8–3.5ms, err→ppid 0.013–0.045ms, spawned→head ~0.03ms),
  `strace-grid.json`, `strace-smoke.json`
- `corpus/live/r68-critic/clause_sig_probe.py` → `clause-sig-results.json`
  (F1–F5 verdicts through verbatim classifiers)
- `corpus/live/r68-critic/hash_gate_probe.py` → `hash-gate-results.json`
  (G1 identical hashes on opposite delivery order — real subprocess
  captures; G3 same-hash different-verdict allowlist table)
- Clause refs: `corpus/fixtures/run_battery.py` l.152/1611 (concat),
  l.160-177 (`classify_process` exit/error gate + ERROR-scan + blob
  conjuncts), l.179-208 (`classify_streams` stdout-bound sig l.183, blob
  l.185-188, stderr sweep l.200-207), l.2281-2292 (`dual_classify` same-
  object construction), l.1585-1660 (`surface_run` bounded Popen);
  `corpus/fixtures/descendant_pipe_probe.gd` l.157-168 (tracked
  midlineforge arm — fixed `sleep 0.08`, 200ms gap, `printraw`/`print`
  halves)
- Baseline cross-check: `corpus/live/r68-baseline/` freeze receipt at
  HEAD `1101cb3` (clean tree == attack target)

Stop. No verdict on admissibility — that is the canonical judge's call.
