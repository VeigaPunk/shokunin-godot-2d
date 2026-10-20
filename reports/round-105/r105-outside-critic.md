# Outside W3 critic — preserved closure evidence

Original: orchestrator artifact kaika-w3-game-dev-2d-critic.md. Scanner vault-URI scheme literals are redacted in this copy to honor the corpus no-reference rule; findings and verdict text unchanged. Parent disposition is REJECT/HONEST STOP despite reviewer ADMIT recommendation.

# kaika W3 critic — game-dev-2d round 105

**Boundary and verification.** Read-only review; no lane, fleet, or sibling writes. I did not rerun either expensive full battery. I reran the round count and source-census commands:

```sh
sh reports/round-105/r105-count.sh e89905162
sh reports/round-105/r105-count.sh ff32e252
sh reports/round-105/r105-count.sh b0d2c4990
sh reports/round-105/r105-sources-census.sh
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
  /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/game-dev-2d-shokunin \
  --today 2026-10-19 --verbose
```

Those outputs reproduce baseline `UID 21 / total CASES 585`, implementation/final `UID 29 / total CASES 600`, `QUALITY 0→23`, mistakes `0→32`, mapped rows `0→32`, knowledge `2→5`, complete-header entries `0→3`, and `SOURCES 0→31` (all measured by the three `r105-count.sh` invocations above). The frozen census command reports `31` rows, `0` malformed, tiers `A=30/B=1`, statuses `mined=10/queued=19/rejected=2`, and no duplicate/enum/tier/dead-used-by output; the invoked canonical validator returns `game-dev-2d-shokunin ok`.

I independently reopened S002, S026, S031, S001, and S009. S002's official 4.7 TileMapLayer page says “To get the exact cell coordinates, you need to set physics_quadrant_size to 1” (Property Descriptions → `physics_quadrant_size`); S026's official ResourceUID page says “Returns whether the given UID value is known to the cache” (Method Descriptions → `has_id`). The 4.4 TileMapLayer property table has no `physics_quadrant_size`; S001's support timeline marks 4.4 unsupported. S009's physics warning says physics is “not deterministic.” The opened quotes and locations in the Gate agree with these pages; no tier inflation appeared in the checked rows.

Focused runtime reruns, all on `/usr/bin/godot 4.7.2.stable.arch_linux.ed1daf0bf`, in a copied fixture project under the assigned `/tmp` scratch and removed afterward:

- `timeout --signal=TERM --kill-after=2s 60s env XDG_DATA_HOME=/tmp/kaika-verify/game-dev-2d-critic/godot-qqwSqT/xdg-createid RES_UID_ROOT=/tmp/kaika-verify/game-dev-2d-critic/godot-qqwSqT/resuid-createid /usr/bin/godot --headless --path /tmp/kaika-verify/game-dev-2d-critic/godot-qqwSqT/fixture --script res://res_uid_s01.gd -- --arm=createid` → `PASS`; both path domains were stable, round-tripped, unregistered, and distinct.
- `timeout --signal=TERM --kill-after=2s 90s env XDG_DATA_HOME=/tmp/kaika-verify/game-dev-2d-critic/godot-qqwSqT/xdg-persist RES_UID_ROOT=/tmp/kaika-verify/game-dev-2d-critic/godot-qqwSqT/resuid-persist /usr/bin/godot --headless --path /tmp/kaika-verify/game-dev-2d-critic/godot-qqwSqT/fixture --script res://res_uid_s04.gd -- --arm=persist` → `PASS`; editor-created cache had one consistent record; cache-present reader resolved `res://alpha.gd`, while the sidecar-only/cache-removed reader had `has_id=false`.
- `/usr/bin/godot --headless --path /tmp/kaika-verify/game-dev-2d-critic/godot-qqwSqT/fixture --script res://descendant_pipe_probe.gd -- --spawn-detach` → exit `0`, `0.680s`, marker present and detached child alive at parent return; I terminated that child. This exercises the finite-life premise, not the complete meta gate.

The runner exposes ordering and shared-UID flags but no individual CASES selector (`run_battery.py:2514-2519`), so I did not run the whole suite for a narrow check. For broader claims I read the stored final receipts and raw results. The author’s full-battery command is the report’s `timeout … python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --probe-failing … --res-uid-order "$ORDER" --probe-res-uid-shared`; its recorded outputs are not new reruns. Compact receipt reconstruction is documented as:

```sh
python3 reports/round-105/r105-receipts.py \
 corpus/live/runs/20261019T233501498056Z/verdicts.json \
 corpus/live/runs/20261019T234607282166Z/verdicts.json
```

The saved records show both final runs PASS, every CASES identity once, no duplicate result names, shared-probe clean baseline passing with no UID cache before/after, the actual export writer passing and creating the seeded cache, and the three named seeded mismatch rows. Raw full-run order places the shared UID probe before the detached control and its following meta; all recorded descendant discriminations are true. The receipt’s script-blob hashes match `git rev-parse ff32e252:<path>` for each listed runner/UID/R105 script. I did not rerun the full forward/reversed batteries, shared writer→reader chain, or full descendant meta.

## C1 — coverage: ResourceUID isolation and re-admissions

- **Counterexample / strongest bound:** The final clean-shared arm passes with no cache before or after, so it does not support a claim that shared project use or UID row order alone causes failures. The report and `r105-res-uid-isolation.md` correctly narrow the result: neither clean-shared order shows within-family leakage; the separate export-writer intervention reproduces a cache-regime mismatch. The first committed scheduling attempt is preserved as adverse history (`7d9d9741`, `r105-scheduling-failure.json`, `LOG.md` round-105); it harmed the finite-life meta check and was not retried unchanged.
- **Evidence:** The count command above establishes `21→29` UID CASES and `585→600` total. The final saved receipts and source-blob comparison support the bounded replay claim; the focused actual-Godot `createid` and `persist` arms independently exercised the revised UID invariants and cache/sidecar boundary. The direct detached-child run confirms why moving work out of the liveness window matters; source ordering and stored raw results show the corrected probe precedes the detached tail. No full suite was rerun.
- **Impacted axes:** Coverage improved on the measured fixture surface. No current C1 behavioral regression found; calibration benefits from preserving the failed iteration and limiting the causal claim.
- **Smallest safe correction:** Keep the existing explicit cache-regime wording and no-row-order-leak caveat. Do not generalize to other Godot builds, all shared-project use, or a universal UID-cache rule.

## C2 — calibration: mistake-to-QUALITY bar

- **Counterexample:** Q1–Q3 are active QUALITY criteria whose “why” cells cite `CORPUS.md`/`PROTOCOL.md`, not a lesson. `LEARNING.md:57-60` requires that every criterion cite the lesson that produced it; `QUALITY.md:3-6` likewise says the bar grew only from lessons. A search for `\bQ(?:1|2|3)\b` in `corpus/lessons/round-105.md` returned no matches. The C2 count’s `awk` predicate (`r105-count.sh:10`) accepts Q-shaped strings; it does not join each `captured-by` ID against existing QUALITY rows or prove that the criterion was learned from the cited mistake. This is a fixable bar/provenance defect, not evidence that the other mappings are false.
- **Evidence:** The count command above reproduces `32` mistake rows, `23` criteria, and `32` syntactically mapped rows. The actual table does capture the scheduling failure as M32→Q23 and records the failed iteration rather than hiding it; saved final receipts show the corrected liveness guards. Discernment remains correctly marked pending outside review.
- **Impacted axes:** Calibration directly; depth also, because C3’s knowledge admissions rely on this bar.
- **Smallest safe correction:** Preserve history. Append an evidence-backed correction/lesson and replacement criteria superseding Q1–Q3 (or establish their real lesson provenance); do not rewrite the existing rows. Tighten the count check to verify every mapped Q ID exists, separately from whether the criterion is substantively grounded.

## C3 — depth: SOURCES capability and three knowledge admissions

- **Counterexample:** The SOURCES capability itself is demonstrated and the sampled source records are accurate, but the declared claim combines that capability with knowledge admissions that require C2’s newly created QUALITY bar. The round prompt says “Creating it comes first” and forbids admission without the bar (`game-dev-2d-round-105.md:150-154`); the baseline count command above shows no QUALITY criteria at `e89905162`. The report’s assertion that QUALITY is “shared admission infrastructure” (`LOG.md:1334-1336`) confirms, rather than removes, the dependency. Thus C3 cannot be verified as declared without C2 having landed; the pair is not causally separable under `AXES.md:25-36`.
- **Evidence:** The count commands above reproduce the SOURCES/knowledge/header deltas. The canonical validator is clean; reopened S002 and S026 support admitted entries, S031’s 4.4-page absence plus S001’s release table support the retained rejection, and S009 supports K3’s bounded non-determinism caveat. The checked sample showed no quote mismatch or tier inflation; it does not independently prove all author-opened rows.
- **Impacted axes:** Depth, and calibration through the shared admission bar. The source-registry capability is a real, independently runnable result; the knowledge-admission part is the coupled portion.
- **Smallest safe correction:** Do not claim post-hoc independence by assertion. For a conforming claim set, separate the QUALITY-bar move from knowledge admission into distinct rounds, or explicitly narrow C3 to the SOURCES capability and leave the entries as dependent adjunct work in an append-only correction. Do not delete the knowledge. Separately, the scorecard remains honestly unscored; evidence age is a useful work-selection heuristic, not proof that depth is the lowest-scoring axis, so leave that obligation unresolved for the operator rather than inventing a scalar.

## Recommendation

**Recommendation only, not canonical adjudication:** reject round 105 as declared because C2/C3 violate the explicit causal-separability rule. This is a fixable claim/ledger-conformance defect, not a finding that the UID, source, or physics observations are false and not a reason to erase knowledge. C1 is supported within its stated bounds; the SOURCES capability and sampled citations are credible; C2 needs the append-only provenance correction above. No numerical score or promotion is supported or recommended.
