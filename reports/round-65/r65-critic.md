# Round 65 critic report — forged-REJECTION dual (host: devin)

Seat: critic, lane `game-dev-2d`. Target: the author's uncommitted +466/−0
diff in `~/Projects/shokunin/game-dev-2d-shokunin`
(`corpus/fixtures/descendant_pipe_probe.gd` +35,
`corpus/fixtures/run_battery.py` +431, both additive). Attacked the landed
diff directly; all commands below resolve on this host.

## Verdict on the declared claim — CONFIRMED as measured, but the falsifiable
## wording is falsified at its literal boundary (fixable defect)

The declared claim — "the post-death injected error marker flips a CASES
row from PASS to FAIL" — is measured TRUE for pipe-inheriting descendants
(author's 28/28 discriminations, independently reproduced below). The
operative precondition, however, is **capture-before-pipe-EOF, not
death-ordering**: I produced a post-death, post-orphan error emission —
the same reparenting gate, byte-identical marker, `write_ppid=1573`
provenance — whose record stays a clean **PASS** because the descendant
detached the pipe fds before emitting. The author's own `bounded_claim`
hedges with "lands in the merged capture"; the declared axis-move and the
report's headline do not state that precondition. This is a claim-precision
defect, not a mechanism failure — smallest safe correction below.

## Independent reproduction (not trusted from author's receipt)

- Full seven-flag battery re-run:
  `python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
  corpus/live/r65-critic/runs --probe-failing --probe-unrelated-error
  --probe-export-launch --probe-godot-error --probe-stream-attribution
  --probe-crash-exit --probe-timeout` → **exit 0**, PASS battery,
  `corpus/live/r65-critic/runs/20261014T041531981734Z/verdicts.json`
  (sha256 `fe0bdffc710a6451f7fb05979d40386d24d9795e3be12b599c47898972d1371d`),
  98 rows, `probe_descendant_error_spoof` PASS, **28/28 discriminations
  True** — independently re-measured (my release arm: exit 0 @0.44s,
  `write_ppid=1573 ≠ godot_pid=1801996`, inner cls False, strip cls True).
- **97 prior rows byte-stable**: 7-field tuple
  (script/flags/expected_exit/actual_exit/signature/verdict/error) diff of
  my run vs r65-baseline receipt `r65-baseline/runs/20261014T022523005280Z/
  verdicts.json` → **97 common rows, 0 mismatches**; new-only
  `{probe_descendant_error_spoof}`; vs author's run → 98 common, 0
  mismatches. r63 accepting-forgery row stays `PASS exit=0`; r64
  `probe_while_live_signature_gate` stays PASS.
- Gate interplay (brief's open question) verified on my run's gated reps:
  signature accepted while-live 3/3 (`child_alive_at_signature_observation`
  True), forged error observed strictly post-death 3/3
  (`dead_observed_at` 0.476–0.498 < `error_observed_at` 0.507–0.529,
  `child_alive_at_error_observation` False) — the built gate does **not**
  reject the forged-error arm; rejection stays in the un-gated merged
  classifier. Matches author's claim.

## Counterexample CE-1 — post-death emission ≠ capture (the strongest
## counterexample available: refines the flip's true boundary)

Scratch probe `corpus/live/r65-critic/proj/critic_errforge_probe.gd` +
`critic_probe.py` (extracts `classify_process` **verbatim** from
run_battery.py by regex+exec — no re-implementation drift). Arms reuse the
author's reparenting gate verbatim.

- `--detach-errforge`: descendant exec-redirects all stdio to /dev/null
  **before** gating, then emits `ERROR: DESCENDANT_PIPE_ERRFORGE unrelated
  injected diagnostic` + `write_ppid=$pp` into
  `probes/emitted_post_death.txt`. Record: exit 0, sig present, no error
  captured → `inner_classification` **True (PASS)**. The file exists and
  reads `ERROR: ...` + `write_ppid=1573` (1573 = reparented ppid ≠
  godot_pid 1799478) — the emission provably happened post-death and
  post-orphan, yet flips nothing. A post-death injected error marker does
  **not** convert the record: only one that lands in the captured pipe
  before EOF does.
- `--detach-errforge-late` (+1.5s delay after gate): emission lands ~1.5s
  after `communicate()` returned (elapsed 0.513s; file
  `emitted_post_return.txt` present) → PASS. The brief's race question
  answered concretely: a descendant error write **can** land after
  communicate() returns — but only post-EOF; while any write-fd is held,
  EOF ordering makes pre-return loss impossible.

**Impact:** the literal falsifiable claim omits the capture precondition;
the measured result stands but the axis statement should carry it. This
mirrors r62's detached-fd control exactly — the same boundary, now on the
rejection axis.

## Counterexample CE-2 — the merged concat FABRICATES reject-triggering
## lines (existence-blindness, beyond origin-blindness)

`run_process`/`errforge_run` merge is `stdout + stderr` with **no newline
guard**, then the error clause scans `text.splitlines()`. Real-pipe
measurement (`splice_real.py`): child prints signature then
`ending in ERROR` (no `\n`) to stdout and `: PHANTOM real-pipe splice` to
stderr → merged contains `ending in ERROR: PHANTOM real-pipe splice` —
**stdout_ERROR_lines=[], stderr_ERROR_lines=[], merged_ERROR_lines=[1
phantom]** → `classify_process` **False**. With a `\n` guard → True.

A two-process collusion (or one process split-writing across streams)
produces a FAIL whose `error_lines` — a CASES-visible field, the very
field `forged_vs_genuine_cases_fields_identical` compares — contains a
line **no process ever wrote as a line**. Symmetrically, `signature in
output` is a blob scan that splice-matches across the same seam, so both
axes share the merge artifact — the claim "as origin-blind as the
signature axis" survives; what is newly pinned is that the merged
line-set ≠ the union of stream line-sets, i.e. `error_lines` is not
line-faithful even ignoring provenance. Inverse measured: `ERROR\n:`
split across a newline **escapes** the per-line scan
(`newline_split` rejects=False in the matrix) — line-granularity cuts
both ways.

## Attack (5) — allowlist/marker boundary matrix (verbatim classifier)

`critic-probe-results.json → _allowlist_matrix`:

| mutation | rejects? |
|---|---|
| `ERROR: DESCENDANT_PIPE_ERRFORGE …` (verbatim) | **True** |
| mid-line `prefix text ERROR: …` | True (substring, not anchored) |
| bare suffix `ERROR:` | True |
| `SCRIPT ERROR:` / `Parse Error:` forged post-death | **True** — two additional reject clauses the fixture does not exercise |
| `error:` / `Error:` / `ERROR` (no colon) / `ERROR :` / `WARNING:` | False — wide escape space |
| `ERROR\n:` (newline-split) | False |
| forged echo of a per-case **allowlisted** error (save_corrupt_negative's string) | **accepted** when allowlisted (`accepts_when_allowlisted: True`) — the acceptance axis is equally origin-blind |
| allowlisted line + appended second `ERROR:` | rejects — the `count("ERROR:")==1` guard lets a tail-forge defeat the allowlist |

The asymmetry vs the signature axis is precise: the error path checks
*content class* (substring `ERROR:` + per-case allowlist + two extra blob
clauses) where the signature path checks one byte-substring — but neither
checks origin, timing, stream, or line-existence. Origin-blindness
confirmed; the axes are differently-shaped holes, not differently-deep.

## Attack (3) — stderr forge: same flip (first-party evidence)

`--stderr-errforge` (descendant `echo … >&2` post-death): exit 0, sig
present, `write_ppid=1573` → `inner_classification` **False**. The author
declared this variant untested in-tree (relied on the scribe lane); now
measured first-party — stdout and stderr forge identically post-merge.

## Attack (4) — double-write: count is invisible

`--double-errforge` (child `push_error` pre-death + descendant echo
post-death, byte-identical): merged output carries the marker **twice**
plus both provenance trails (`   at:`/`GDScript backtrace`/`[0]
_initialize` AND `write_ppid=1573`), yet `error_lines` — a sorted **set**
— dedupes to one entry → `cases_visible` equals a single-emission record.
The rejection axis is multiplicity-blind; consistent with (and
strengthening) origin-blindness, but worth noting the evidence field
cannot count emissions.

## Attack (2) — hold-arm race window measured

5 reps of the gated read on the stderr-forge arm (`splice-and-race.json`):
post-death write lag **31.7–32.0 ms**, forged error at ~0.41–0.45s →
margin to the 3.0s bound **≈2.55s**. `hold_forged_error_captured` flakes
only if godot's death lands in the final ~50ms before the bound (godot
dies ~0.4s in on this host — ~50× margin; the window is structural, not
latent here). Release arm has no race at all (EOF ordering).

## Minor observations (non-blocking)

- `provenance_only_line_diff` in my run carries push_error's full 3-line
  backtrace (`at:`/`GDScript backtrace`/`[0] _initialize`) — classified as
  "provenance" by the `ef_diff_is_provenance_only` test; consistent with
  the report wording.
- `error_lines`/`cases_visible` are set-based — the identical-fields proof
  would survive even a double-emission forged arm (CE-4); the comparison
  proves line-set equality, not emission equality.
- Mixed flags (`--spawn-forge-release --spawn-errforge-release`) produce
  an incoherent arm (withheld banner + forge descendant): undocumented
  combination, unused by any row — same exposure as prior rounds' arms.
- `gated_genuine` reps = 2 vs release = 3 — cosmetic asymmetry.
- Reparent target `write_ppid=1573` is this host's subreaper, identical
  across author and critic runs — stable, kernel-corroborated.

## Fixable defect vs tradeoff

All 28 discriminations reproduce; the mechanism is sound. The defect is
claim precision, not measurement: the declared falsifiable claim and the
headline say "post-death injected error marker flips", omitting the
capture precondition CE-1 demonstrates is load-bearing (the author's own
`bounded_claim` already hedges correctly). CE-2's phantom-line surface is
an inherited property of the `out+err` merge (pre-r65), newly documented
on the error axis — a documented-boundary matter, not a regression.

**Smallest safe correction:** amend the falsifiable-claim / bounded_claim
wording to "a post-death error marker **captured before pipe-EOF** flips a
clean exit-0 + signature-present record to FAIL"; optionally add one
discrimination asserting the detach-arm negative control (emission
provable, capture absent) and a comment noting `error_lines` is a deduped
merged-line set (phantom-splice/multiplicity caveat). No mechanism change
required; nothing here is a judge-reject.

## Files written (inside brief scope only)

- report: `reports/round-65/r65-critic.md` (this file)
- scratch: `corpus/live/r65-critic/{proj/{project.godot,
  critic_errforge_probe.gd}, critic_probe.py, splice_real.py,
  critic-probe-results.json, splice-and-race.json,
  probes/{emitted_post_death.txt,emitted_post_return.txt},
  runs/20261014T041531981734Z/, battery.stdout}`
