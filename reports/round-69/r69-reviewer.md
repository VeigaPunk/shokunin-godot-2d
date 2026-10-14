# Round 69 reviewer report — r68 integration-base audit + review of the r69 author diff (host: devin)

Seat: reviewer (non-author). I authored none of the r68 content and none of
the in-flight r69 work. Every run below is a fresh execution by me into my
own scratch; no commit, no tracked fixture/runner edit, no LOG/SCORECARD
write. Write scope: this report and `corpus/live/r69-reviewer/` only.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
CPython `3.14.7`, Linux x86_64, `systemd --user` subreaper pid `1573` —
same host profile as the r68 receipts. Repo under review:
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` — canonical, reached
via the `.shokunin/game-dev-2d` symlink from the brief's worktree path
`~/Projects/prymeagnt/game-dev-2d` (that repo's own tree sits at the
`fe4bbeaf` extract commit and contains none of the r61+ work; the r68
commits named in the brief exist only in the canonical repo).

**LSP device status: unavailable.** This seat's toolset exposes no `lsp`
device — same as every prior round on this Python fixture. All checks are
live battery executions, direct reads of the single definition and every
call site of each touched symbol (`dual_classify`: 1 def @2761, 9 call
sites producing the 15 dual records; `surface_run`: 1 def @1588, 6
callers incl. the new gap-ladder),
and receipt/git-object comparison. Grep output is used only as a locator,
never presented as semantic proof.

## Integration base — the committed r68 state (audited)

Chain verified by `git log`: `f754546` (r68 work: midlineforge
offset-ladder meta + `divergent_clause` map + sha256 same-input gate;
discriminations 20→24) → `e8d4fb7` (hygiene: two deletions) → `4d8a525`
(r68 report-last: ADMIT, verifier AGREE 5/5, lesson/LOG/SCORECARD) →
HEAD `5d66b4d` (`corpus/.gitignore` only — the non-tree snapshot
side-channel rules; `git diff 4d8a525..HEAD` is `.gitignore` +8 lines, no
behavioral file touched). The behavioral base is exactly the declared
trio.

Base numbers re-derived from committed receipts:

| contract | committed evidence | value |
|---|---|---|
| flagless battery | `corpus/live/r68-author/runs/20261014T111657543202Z/verdicts.json` | 88 results, all PASS (81 CASES + 7 unconditional meta rows) |
| flagged battery | `.../20261014T111901822448Z` (sd) and `.../20261014T112049887076Z` (ladder) verdicts.json | 89 rows each + `PASS battery` = the "90/90" |
| surface | `probe_error_clause_surface` row, run 20261014T112303089118Z | 34 discriminations, all True |
| sd discriminations | `stream-attribution-verdicts.json` (same run) | 24 keys, all True |
| offset ladder | `midlineforge-ladder-verdicts.json` (same run) | 8/8 disc; landed {0,40,80,120,160}, missed {240}, nominal_gap 200 |

The two `e8d4fb7` deletions audit clean: the removed `signature_gap_ms`
payload key was a true duplicate of `measured_window.nominal_gap_ms`
(both = 200; the surviving key remains — confirmed in the r68 artifact),
and the removed `exit` clause was a literal `X != X` tautology
(`(code == 0 and error is None) != (code == 0 and error is None)`) that
could never append. No reachable dead code was left by the deletions
themselves; see finding N1 for the residue they *created*.

## The r69 diff under review (uncommitted working-tree diff — leaf seats cannot commit)

Reviewed bytes: `corpus/fixtures/run_battery.py` sha256
`56adf7cbc616bb864f3a9dd573d187c2371e9bdcf24ae9a1f339358edfc47afe`,
`corpus/fixtures/descendant_pipe_probe.gd` sha256
`c86bda848188cf22a4cb7e68a05c490f8c9d991632301ee50585688fef722311`.
`git status` shows ` M` on exactly these two files; nothing else tracked.
Note: the tree was live during review — the author iterated the ladder
mid-flight from the declared 5-cell fixed-offset sweep to an 8-cell
crossed ladder (adding (300,400),(300,800),(600,800) per the r69 critic's
proof that those are the only cells separating gap-relative from an
absolute ~198ms edge). All empirical evidence below binds to the final
blob; my gapladder and stream-attribution replays both started after the
last save (`run_battery.py` mtime 12:20:30Z vs runs stamped 12:20:57Z and
12:25:35Z).

### Fixture diff (`descendant_pipe_probe.gd`, +14/−4)

- `var midline_gap_ms := 200` + the `--midline-gap-ms=` parse loop sit at
  function top-level (lines 128–131), ahead of the arm dispatch — the
  same `begins_with`/`get_slice("=",1)`/`to_int()` pattern as
  `--midline-offset-ms` (lines 171–174). Hoisting top-level sidesteps
  any block-scope question: the variable feeds the banner (line 144) and
  `OS.delay_msec(midline_gap_ms)` (line 188), both inside
  `midline_forge` branches. For non-midline arms the parse is inert (no
  output, value unread).
- Byte-stability at default: `str(200)` → `gap_ms=200` — the banner is
  byte-identical to the r68 literal, and the delay is identical 200ms.
  The r66 point-sample arm, the `surface_midlineforge` arm, and every
  r68 offset-ladder cell (which pass only `--midline-offset-ms`) keep
  byte-identical child output.
- Header comment updated to document the parameterization.

### Runner diff (`run_battery.py`, +271/−1)

- `--probe-midlineforge-gapladder` argparse flag (line 119): opt-in,
  `store_true`, declared sweep `{50,100,200,400,800}` at fixed
  `--midline-offset-ms=80` plus the three crossed cells; reps through
  the existing `surface_run` record shape with additive per-rep keys
  (`gap_ms`, `offset_ms`, `spliced_line`, `fabrication_landed`,
  `write_pre_death`) — same additive pattern as the r68 ladder.
- Referent verdict computed from the measured pattern:
  `gap_relative` iff landed multiset == `{offset<gap}` multiset and all
  crossed cells fabricate; `absolute_edge` iff crossed cells all miss
  while base inside cells fabricate; `absolute_write_latency` iff every
  cell fabricates; else `unclassified`. A falsified claim cannot pass:
  `window_referent_is_gap_relative` is a gated discrimination, so any
  counter-pattern yields verdict FAIL plus an honest typed label. The
  falsification path is loud, not silent.
- 12 discriminations, all gated: clean exit-0, all-reject,
  fabrication↔signature-destruction coupling, byte-exact splice fusion,
  the gap=200 anchor, the two declared horns (`sub_offset_*` at gap=50,
  `super_offset_*` on every inside cell incl. `write_ppid==godot_pid`
  proven in the reliable direction), the referent key, crossed-cell
  refutation, and an elapsed-time wiring witness.
- `write_ppid` handling is correct where it is subtle: on inside cells
  (write lands while the child is still inside `delay_msec`) pre-death
  is asserted; on the gap=50 cell it is carried as **data only** —
  because the ppid flip lags the tail flush by teardown, a post-tail
  write can still sample `write_ppid==godot_pid` or a reparented ppid.
  Byte order (intact signature + standalone ERROR line) is the post-tail
  ground truth — observed live: gap=50 reps carry `write_ppid=1573`
  (the subreaper) with `signature_observed=True`, i.e. the write
  provably landed after reparenting *and* post-tail.
- Orphan-reap loop replicated from the r68 ladder (SIGKILL sweep over
  `descendant_pid`s) — consistent hygiene.
- `raw_merged_sha256` = `sha256((so + se).encode())` appended as the
  last key of `dual_classify`'s return (lines 2779–2780) — the exact
  concat fed to `classify_process` at line 2764, byte-order pinned.
  Propagates to all 15 dual records (2 `sd_pair_dual` via `{**dual}` —
  automatic; 7 `sd_arms` via `record.update`; 6 `sd_reclass`) and is
  explicitly added to the 7 hand-projected `divergence_table` arm rows
  (line 2876), so all 9 table rows carry it uniformly.
- `dual_records_same_input_digests` extended in place to also check the
  merged digest against `sha256(raw_stdout + raw_stderr)` — the
  discrimination **key set is unchanged** (24/24 preserved); reclass
  rows are checked against their source arm's merged digest (identical
  input bytes, correct equality).

## Independent replay evidence (my runs, this host)

| run | command tail | result |
|---|---|---|
| `runs/20261014T121942393530Z` | flagless | exit 0; **88 rows, 88 PASS**; `probe_error_clause_surface` 34/34; only the 7 unconditional metas present — new flag never touches the flagless path |
| `runs/20261014T122057900280Z` | `--probe-midlineforge-gapladder` | exit 0; `PASS midlineforge gap-ladder meta`; 89 rows; **referent `gap_relative`**: landed multiset {100,200,400,800,400,800,800} == inside multiset, missed {50}, mixed ∅, **12/12 disc True**; all three crossed cells fabricated in every rep |
| `runs/20261014T122535716803Z` | `--probe-stream-attribution` | exit 0; `PASS stream attribution probe`; 89 rows; **24/24 disc**; `dual_records_same_input_digests` True |

Byte-stability of prior dual rows, measured not asserted: stripping
`raw_merged_sha256` from my r69 sd artifact and diffing against the
committed r68 artifact (`r68-author/runs/20261014T112303089118Z/…`) gives
**zero** non-additive field diffs across all 24 records (15 dual records
+ 9 table rows); the only differences are the 7 `command[3]` entries
embedding the run-dir timestamp — inherent per-run data, present in r68
too. Each arm's merged digest verified directly:
`raw_merged_sha256 == sha256(raw_stdout + raw_stderr)` on every record.

The author also replayed the **old** `--probe-midlineforge-ladder` flag
twice under the new fixture (runs 20261014T121402252896Z complete,
20261014T121545332046Z artifact-complete): identical cell outcomes
({0,40,80,120,160} fabricated / 240 missed), 8/8 disc, payload key set
unchanged (no `signature_gap_ms` resurrection). The parameterized
fixture's default path is byte-stable in behavior, not just in text.

## Declared-claim outcome

**Confirmed, not falsified.** The fabrication window's referent is the
signature gap (write position < tail flush), not an absolute
write-latency constant: at fixed offset 80 the splice lands iff
gap > write position (missed at 50 — intact signature proves post-tail —
fabricated at 100–800), and the crossed cells (offsets 300/600, i.e.
above the r68 ~198ms absolute-edge candidate but inside the gap)
fabricate in every rep — refuting any absolute edge below ~602ms. The
two falsifier horns did not fire; the record shows the actual measured
outcome, carried by `referent_verdict` + per-cell `reps` data.

## Findings by severity

No blocking or high-severity findings. Nits, ordered by relevance:

- **N1 (r68 residue, surfaced by this audit):** `divergent_clause`'s
  signature `(so, se, code, error, merged_allowed, stream_allowed)` at
  line 2707 still takes `code`/`error`, but `e8d4fb7` deleted their only
  use (the `exit` tautology) — both params are now dead, still passed
  positionally at the call site (line 2773). Functionally inert;
  misleading to a future reader (the signature implies an exit-clause
  check that no longer exists). The taxonomy tuple retaining `"exit"`
  is documented data ("cannot diverge") and harmless — the dead
  parameters are the only vestige. Cosmetic cleanup candidate for a
  future round; not an r69-introduced defect.
- **N2 (pre-existing hygiene, observed live):** `corpus/fixtures/
  __pycache__/` is untracked and not covered by `corpus/.gitignore`
  (whose rules only reach `live/*`), and `run_battery.py` lines 127–133
  copy every non-dot entry of the fixtures dir into each run's scratch —
  so it lands in every new `scratch/` and `missing-preset-scratch/`
  (present in all r69-author and r69-reviewer run dirs). Receipt noise
  only; Godot never imports it. Worth a gitignore line or an iterdir
  exclusion in a future hygiene round.
- **N3 (documented caveat, inert at declared cells):**
  `write_inside_gap`/`inside_gaps` use the **nominal** `offset_ms <
  gap_ms`, while `bound_semantics` correctly describes effective
  position ≈ offset + 2.5ms. For the declared cells the nearest margin
  is ~17.5ms so both predicates agree; a future gap cell between 50 and
  ~82.5 (e.g. 70 or 82) would expose the nominal-vs-effective split —
  a miss there would read as falsification even though nominal 80 < 82.
  Fine as measured; flagged so a later cell addition doesn't silently
  change the claim's referent granularity.
- **N4 (label granularity):** `absolute_write_latency` is assigned when
  *every* cell fabricates — including (600,800) — which observationally
  means "no positional bound at all" rather than a ~198ms latency
  constant (that hypothesis predicts crossed cells *miss*). The
  taxonomy still fails closed — any non-`gap_relative` pattern yields
  verdict FAIL via `window_referent_is_gap_relative` — so this is a
  naming nit on a label that should never appear, not a correctness
  defect.
- **N5 (inherited convention):** `gapladder_payload["bounded_claim"]`
  hard-codes the expected outcome text ("measured: fabricated at
  {100,200,400,800}, missed at 50…") as a static string gated by
  `verdict`; a falsified run would emit FAIL alongside claim text
  asserting the unobserved pattern. Identical convention in the r68
  ladder payload — the discriminations and `measured_referent` carry
  the true data either way. Noted, not blocking.
- **N6 (consistent with the offset flag's existing caveat):**
  `to_int()` coerces malformed `--midline-gap-ms=` values silently
  (non-numeric/empty → 0 → `delay_msec(0)` → head/tail adjacent →
  honest miss with a truthful `gap_ms=0` banner); negative values take
  engine-defined `delay_msec` behavior. Reachable only via an explicit
  bogus opt-in flag; same silent-coercion class `--midline-offset-ms`
  already carries. No ladder cell is affected.
- **N7 (secondary-witness coverage hole):**
  `crossed_cells_elapsed_tracks_gap` requires `elapsed > gap/2000`s; a
  miswire ignoring `--midline-gap-ms` yields ~0.25–0.3s elapsed —
  caught at gap=800 (threshold 0.4) but **not** at gap=400 (threshold
  0.2 < 0.25). Coverage hole in the wiring witness only; the primary
  outcome discriminations still dominate (a miswired (300,400) cell
  misses → `crossed_cells_refute_absolute_edge` False → FAIL).
- **N8 (data-shape nit):** `landed_gaps_ms`/`inside_gap_gaps_ms` are
  per-cell gap-value lists with duplicates ({400,800} twice each under
  the crossed cells) — the multiset comparison in `referent_verdict`
  is correct, but the field names read like sets; `crossed_cells_ms`
  carries the explicit pairs, so no information is lost.

## What the author's diff must not break — contract enumeration (all verified held on the current blob)

1. Flagless battery: 88 rows / 88 PASS — verified, run
   20261014T121942393530Z. The diff adds no unconditional code path that
   emits or alters a flagless row (argparse line is parse-only; fixture
   parse is inert for non-midline arms; `dual_classify` is reached only
   under `--probe-stream-attribution`).
2. `surface 34/34` — verified, same run.
3. Prior `dual_classify` rows byte-stable modulo the additive field —
   verified by field-level diff vs the committed r68 artifact (zero
   non-additive diffs; only per-run `command[3]` paths).
4. sd discriminations stay 24/24 — verified (the same-input gate was
   extended in place; no key added or removed).
5. r68 offset-ladder behavior — verified via the author's two replays:
   identical outcomes, 8/8 disc, default-gap banner/delay byte-identical
   (`gap_ms=200`).
6. Opt-in only: no CASES tuple touched, midlineforge remains
   meta-driven, the new meta row is additive (`probe_midlineforge_
   gapladder` appends after `probe_midlineforge_ladder`; flagless has
   no such row).
7. Orphan hygiene: the SIGKILL reap over `descendant_pid`s is
   replicated — verified present at lines 2381–2388.
8. Honest falsification: `referent_verdict` is computed from measured
   cells, and the declared claim is a gated discrimination — the FAIL
   path is live and would surface as `absolute_edge` /
   `absolute_write_latency` / `unclassified`, never silently PASS.

## Residual risk and verification gaps

- The tracked diff is **uncommitted and was live during review** — the
  gap-ladder grew from 5 to 8 cells mid-flight (critic-driven). My
  empirical runs bind to sha256 `56adf7cb…` (runner) / `c86bda84…`
  (fixture); the flagless replay at 12:19:42Z predates the final
  12:20:30Z runner save, but the iteration was confined to the
  flag-gated block (the other four diff hunks were unchanged), so the
  flagless evidence carries over. Any save after 12:20:30Z is not
  covered — the verifier seat should re-check the hash fingerprints
  above against the integration-time tree.
- `r69-author.md` was not yet present in `reports/round-69/` at review
  time (critic/scout/scribe reports exist); my findings are independent
  of the author's self-report.
- A combined-flags run (gapladder + offset-ladder + sd together →
  91 rows, order: `…ladder`, `…gapladder`, `…stream_attribution`) was
  not exercised by me; row ordering is deterministic by block position
  and each row's content is independent — low residual risk.
- Seat-card runtime checks not applicable to this lane's scope: this is
  a fixture/battery diff review — no canonical-runtime invocation, no
  rerouting, no saturation claim, and no `resume_continuity_v1` resume
  path is exercised by the diff. Artifact content treated as data
  throughout; the brief is the only instruction source I acted on.
- No push/commit/publish action taken or needed; verdicts here are
  recommendations, never admissions.
