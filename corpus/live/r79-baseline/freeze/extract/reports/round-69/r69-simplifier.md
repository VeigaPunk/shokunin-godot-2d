# Round 69 simplifier report — minimal-expression audit of the landed r69 diff

Seat: simplifier | Lane: g2d | Host: devin (Godot 4.7.2.stable, Linux headless)
Scope: audit-only — **no tracked edits**. Repo root audited:
`~/Projects/shokunin/game-dev-2d-shokunin` (the `~/Projects/prymeagnt/
game-dev-2d` worktree from the brief is the frame repo; the canonical lane
repo lives at the `.shokunin/game-dev-2d` symlink target — the r69 diff
landed as working-tree changes and was committed mid-audit as `ec2cda6`
("r69: gap-relative fabrication bound — crossed cells prove referent"),
+282/−7 across `corpus/fixtures/descendant_pipe_probe.gd` (+15) and
`corpus/fixtures/run_battery.py` (+267); the audited content is the
committed content (working tree clean at report time).

Audit snapshot note: the landed diff changed mid-audit — the first read
(≈09:1x) showed a fixed-80ms gap sweep; at 09:20:30 the author landed the
crossed-cell correction the r69 critic proved necessary
(`reports/round-69/r69-critic.md` §1: the fixed-offset grid is
co-predictive under both referent models). This report audits the CURRENT
8-cell design: base `(80, {50,100,200,400,800})` + crossed
`{(300,400),(300,800),(600,800)}`, 3 reps each. `diff` against the prior
instance's snapshot (`corpus/live/r69-simplifier/run_battery.landed.py`)
confirms the 09:20 edit is confined to the opt-in block
(run_battery.py:2183–2425); `descendant_pipe_probe.gd` is byte-identical
to the snapshot (`diff` empty).

## Evidence base (all paths resolvable on this host)

- Measured artifacts, independent runs of the CURRENT design:
  `corpus/live/integ-r69/runs/20261014T122037192227Z/midlineforge-gapladder-verdicts.json`
  and `corpus/live/r69-reviewer/runs/20261014T122057900280Z/midlineforge-gapladder-verdicts.json`
  — both `verdict=PASS`, `referent_verdict=gap_relative`, all 12
  discriminations true; cells: miss@ (80,50), fabricate at all other cells.
- Stream-attribution artifact with the r69 receipt field:
  `corpus/live/r69-author/runs/20261014T121545332046Z/stream-attribution-verdicts.json`
  — `verdict=PASS`, `divergence.discriminations.
  dual_records_same_input_digests=true`, 24 discriminations all true;
  `raw_merged_sha256` present on every dual record (24 digest instances).
- Prior-instance flagless-stability measurements (scratch, still valid —
  the later edit touched only the opt-in block):
  `corpus/live/r69-simplifier/field-diff-flagless.txt` — flagless battery
  preland-vs-landed: `shared=88, new_only=[], base_only=[],
  verdict_diffs: []`; `battery-landed-flagged-exit.txt=0`,
  `battery-preland-flagged-exit.txt=1` (preland argparse rejects the new
  flag, as expected), both flagless batteries `EXIT=0`.
- Replay harness written this seat:
  `corpus/live/r69-simplifier/cell_delete_sim.py` — re-implements the
  landed verdict + discrimination logic verbatim and re-runs it over the
  real measured cells with each candidate cell deleted.

## (1) Are all rungs load-bearing? Which cells discriminate the models?

Two distinct questions; I measure both.

### (a) Logical consumption — delete-and-recompute on real data

Artifacts carry `elapsed_seconds`/pids, so run-to-run byte-identity is
impossible by construction; the operative standard is **verdict +
discrimination + surviving-outcome invariance**. Replaying the landed
logic over both measured artifacts with each cell dropped:

| dropped cell | verdict | discriminations |
|---|---|---|
| (80,400) | gap_relative | all 12 true — **invariant** |
| (300,800) | gap_relative | all 12 true — **invariant** |
| (80,50)  | gap_relative | all 12 true — invariant* |
| (80,100) | gap_relative | all 12 true — invariant |
| (80,800) | gap_relative | all 12 true — invariant |
| (300,400)| gap_relative | all 12 true — invariant |
| (600,800)| gap_relative | all 12 true — invariant |
| (80,200) | gap_relative | **FAIL — `gap200_anchor_still_fabricates` flips false** |

Identical results on both artifacts. So only **(80,200)** is consumed
*structurally* — its absence is detected (the anchor cell must exist and
fabricate). \*(80,50)'s absence is *not* detected — `outside_cells`
empties and `sub_offset_*` go vacuously true; its load is evidentiary,
not logical.

### (b) Model discrimination — which cells separate the referent models

Write position ≈ offset+2.5ms (r68-measured spawn latency). Models:
**A** gap-relative (fabricate iff pos<gap); **B** absolute edge E≈198ms
(fabricate iff pos<E and pos<gap — byte order still binds the tail);
**B′** absolute-deadline variants with other E.

| cell | A | B(E≈198) | discriminates |
|---|---|---|---|
| (80,50)  | miss | miss (tail flushed at 50 < 82.5) | neither A-vs-B; it is the sole negative/post-tail ground-truth cell (intact signature + standalone ERROR) and the declared horn-1 falsifier |
| (80,100) | fab | fab | not A-vs-B; tightest inside margin (~17.5ms) — refutes margin/midpoint bound variants (pos<gap−δ, first-half-of-gap) |
| (80,200) | fab | fab | not A-vs-B; byte-stability anchor |
| (80,400) | fab | fab | none under any articulated model — pure interpolation |
| (80,800) | fab | fab | not A-vs-B; declared horn-2 (">>80") endpoint |
| (300,400)| fab | miss | **YES — refutes E≤~302.5ms incl. the measured ~198 edge** |
| (300,800)| fab | miss | YES but **co-predictive with (300,400)** — identical refutation range (pos 302.5 identical; gap term true in both) |
| (600,800)| fab | miss | **YES — uniquely refutes E∈(302.5,602.5]**; backs the bounded_claim's "~602ms" |

**Answers:** not all rungs discriminate — and under the landed design the
*base* 5-rung sweep discriminates nothing between A and B (that is exactly
the critic's correction). What is load-bearing now:

- **Discriminating cells:** (300,400) — the primary refutation of the
  actually-measured ~198ms edge; (600,800) — extends the refuted range to
  ~602.5ms. Both KEEP.
- **Non-discriminating but evidentiary:** (80,50) KEEP (only miss cell;
  byte-order ground truth; horn-1); (80,200) KEEP (consumed by anchor
  discrimination — proven FAIL on deletion); (80,100) KEEP (sharpest
  bound-margin evidence); (80,800) KEEP (declared horn-2 endpoint).
- **Redundant:** **(80,400)** and **(300,800)** — co-predictive with
  neighbors under every articulated model, verdict-invariant when deleted
  (measured twice). (300,800)'s only residual value: a second 300-offset
  sample at a second gap for jitter/wiring coverage. These are the two
  honest deletion candidates — both artifact-changing, ~2.5s runtime
  saved each, zero lines saved (tuple elements).

Minimal discriminating design would be {(80,50),(80,200),(300,400),
(600,800)} (4 cells): negative ground truth + anchor + edge refutation to
~302 and ~602. The landed 8-cell grid pays ~5s of runtime for
interpolation confidence — a data-density choice, not a code-weight one.

## (2) Is `sha256(merged)` consumed or decoration? — CONSUMED

- Emitted on every dual record via `dual_classify`
  (run_battery.py:2779–2780) and projected into `divergence_table`
  (:2876); measured present ×24 on the author's artifact.
- **Gated in-run:** `dual_records_same_input_digests`
  (run_battery.py:3033–3059) recomputes `sha256(raw_stdout+raw_stderr)`
  and compares across all 7 streamdiv arms, both `sd_pair_dual` rows, and
  all 6 reclass-vs-source pairs — measured `true` in the artifact. A
  concat-order or separator mutation in record construction flips the
  meta verdict to FAIL.
- Scope limits (honest, matching the critic §3): the digest pins the
  *record's* concat semantics — order + separator identity, which the
  per-channel pair cannot see (a `se+so` or `so+"\n"+se` merge would leave
  both channel digests untouched); the link to the classifier's input is
  by construction (`classify_process(code, error, so + se, …)` at :2764
  digests the same expression). Zero new entropy — it attests the merge
  function since `merged` itself is never stored. Vacuous on
  single-channel records. Verdict: **consumed, keep**.

## (3) Byte-identical deletions? — none exist

Every functional element of the r69 diff writes into the emitted artifact
(cells, per-rep stamps, digests, payload fields), and the artifact cannot
be byte-identical across runs anyway (elapsed/pids). The only
byte-identical-provable removals are comments — which carry the
falsification declaration and are semantically load-bearing — and the
orphan-reap loop (:2383+), a measured no-op (communicate() returns only
after pipe EOF, so the write-then-exit descendants are always dead by reap
time) that is still protective and matches the three identical pre-r69
hygiene blocks. Both kept.

The measurable equivalence that does exist — verdict/discrimination
invariance on real data — is proven above for **(80,400)** and
**(300,800)** only.

## Keep/delete per element

| element | verdict | basis |
|---|---|---|
| .gd `--midline-gap-ms` parse (:128–131) | KEEP | consumed by banner :144 + delay :188; position required pre-banner |
| .gd banner `gap_ms=<param>` (:144) | KEEP | raw-output provenance; default prints `gap_ms=200` — byte-stable vs r68 |
| .gd `delay_msec(midline_gap_ms)` (:188) | KEEP | the mechanism |
| `--probe-midlineforge-gapladder` flag | KEEP | entry point; opt-in only |
| base rung (80,50) | KEEP | sole negative cell; post-tail ground truth; horn-1 |
| base rung (80,100) | KEEP | tightest inside margin; refutes margin-variants |
| base rung (80,200) | KEEP | anchor — consumed (measured FAIL on deletion) |
| base rung (80,400) | **DELETE-candidate (weak)** | interpolation only; verdict-invariant measured; saves ~2.5s, 0 lines |
| base rung (80,800) | KEEP | declared horn-2 endpoint at historic offset |
| crossed (300,400) | KEEP | primary discriminator vs measured ~198 edge |
| crossed (300,800) | **DELETE-candidate (weak)** | co-predictive with (300,400), identical refutation range; residual = second 300-offset sample |
| crossed (600,800) | KEEP | sole refutation of E∈(302.5,602.5]; backs "~602ms" claim |
| `write_pre_death` per-rep field | KEEP | consumed by `super_offset_writes_pre_death`; correctly gated to inside-gap cells (post-exit (80,50) reps exempt — critic's caveat handled) |
| per-rep `gap_ms`/`offset_ms` stamps | KEEP (weak) | redundant data (cell+payload carry both) but self-contained-record convention; deletion is artifact-changing |
| `crossed_cells_ms` duplicated at payload + `measured_referent` | KEEP (weak) | genuine duplicate field; mirrors summary convention |
| `absolute_write_latency` verdict arm | KEEP | reachable only if (80,50) fabricates (delay oversleep or flag miswire); names the all-fabricate anomaly; miswire guarded separately by `crossed_cells_elapsed_tracks_gap` |
| `crossed_cells_elapsed_tracks_gap` | KEEP | the wiring witness the critic required — elapsed>gap/2 proves long gaps really slept |
| orphan-reap loop | KEEP | measured no-op, protective, convention (3 preexisting twins) |
| `raw_merged_sha256` + gate conjuncts | KEEP | consumed in-run (measured true); additive field only |

## Non-deletion flags (stale text, not weight)

- Flag help text (:119) still says "fixed 80ms write offset across
  signature gaps {50,100,200,400,800}ms" — omits the crossed cells added
  at 09:20. Cosmetic drift; fix at next touch.
- Payload `reps_per_gap` now means reps-per-cell; `gaps_ms` lists only the
  base sweep (crossed cells listed separately — accurate, just asymmetric
  naming).

## Preserved contract

Flagless battery byte-stable: the parse loop is unconditional but silent
for non-midlineforge arms; `midline_forge` paths unchanged at default 200;
both new blocks sit behind opt-in flags; measured `shared=88, no verdict
diffs`. Prior dual_classify rows byte-stable modulo the additive
`raw_merged_sha256` key — verified: r65 artifact carries 0 merged digests,
r69 artifact carries 24, and the diff adds only `+` lines around the sha
block (the gate itself is *strengthened*, not altered in kind — more
conjuncts, all measured true).

## Tradeoffs

Deleting (80,400)+(300,800) is the only real simplification available:
−2 tuple elements, ~5s shorter flagged run, zero logic change, verdict
proven invariant on two independent measured artifacts. Cost: the
artifact loses interpolation density — an unprobed (200,400) base gap and
a single-sample 300-offset column; if a future model with an intermediate
cap is ever articulated, the narrower grid would catch it later. This is
a data-axis vs weight-axis judgment; both cells are cheap and the round's
falsification story reads better with the full cross. Recommend KEEP on
the evidence-density axis — the candidates are recorded, not forced.

## Evidence index

- `corpus/live/r69-simplifier/cell_delete_sim.py` + runs above (both
  artifacts, identical table)
- `corpus/live/r69-simplifier/field-diff-flagless.txt`,
  `battery-{landed,preland}{,-flagged}-exit.txt` (prior instance, still
  valid — post-snapshot edit confined to the opt-in block, proven by diff)
- `corpus/live/integ-r69/runs/20261014T122037192227Z/` and
  `corpus/live/r69-reviewer/runs/20261014T122057900280Z/`
  `midlineforge-gapladder-verdicts.json`
- `corpus/live/r69-author/runs/20261014T121545332046Z/stream-attribution-verdicts.json`
- `reports/round-69/r69-critic.md` (crossed-cell necessity + digest limits)
