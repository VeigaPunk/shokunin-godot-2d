# Outside W3 review — preserved closure evidence

Original: orchestrator artifact kaika-w3-game-dev-2d-review.md. Scanner vault-URI scheme literals are redacted in this copy to honor the corpus no-reference rule; findings and verdict text unchanged. Parent disposition is REJECT/HONEST STOP despite reviewer ADMIT recommendation.

# kaika W3 — independent non-author review: game-dev-2d round 105

Reviewer: W3ReviewGameDev2d (fresh orchestrator-dispatched task, non-author). Read-only.
Lane: `game-dev-2d`, steered round 105. Worktree:
`/home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/game-dev-2d-shokunin`.
Base `e89905162`; round head `b0d2c4990`; measured implementation `ff32e252`; rejected pre-fix iteration `7d9d9741`.
Report reviewed: `fleet-ledger/.ufo/reports/round-105/game-dev-2d.md`.
Scratch used only under `/tmp/kaika-verify/game-dev-2d-review/` (deleted after this review).
No repository was edited, staged, committed, or switched.

## 1. Provenance — PASS

Command:
`git -C <lane> log --format='%h %an <%ae> | %cn <%ce> | %s' e89905162..b0d2c4990`

```
b0d2c499 game-dev-2d-shokunin <game-dev-2d@shokunin.local> | game-dev-2d-shokunin <game-dev-2d@shokunin.local> | round-105: record 621-pass serial replays, source census and per-axis verdicts
ff32e252 game-dev-2d-shokunin <game-dev-2d@shokunin.local> | game-dev-2d-shokunin <game-dev-2d@shokunin.local> | round-105: preserve descendant liveness window and learn the scheduling failure
7d9d9741 game-dev-2d-shokunin <game-dev-2d@shokunin.local> | game-dev-2d-shokunin <game-dev-2d@shokunin.local> | round-105: restore UID rows, curate sources and turn mistakes into admission criteria
```

Every round commit has the lane identity as author and committer. Same-identity rerouting holds: no foreign-authored commit in range. Worktree status at review time: clean (`git status --porcelain` printed nothing).

## 2. Append-only — PASS (no prior-line edits in the protected set)

Command:
`git -C <lane> diff e89905162..b0d2c4990 -- LOG.md corpus/lessons corpus/QUALITY.md | grep -E '^-' | grep -vE '^---'`

Output: empty. `LOG.md` +142/−0; `corpus/lessons/round-105.md` new; `corpus/lessons/r105-res-uid-isolation.md` new; `corpus/QUALITY.md` new (+66/−0, Q23 appended at `ff32e252`). `corpus/SOURCES.md` did not exist at base (`git cat-file -e e89905162:corpus/SOURCES.md` → exit 128), so no in-place cell history exists; the registry is first-working this round.

Deletions in the range are confined to non-append-only files:
`git diff --numstat e89905162..b0d2c4990 | awk '$2>0'` →
`9 7 SHONEN.md`; `11 9 corpus/fixtures/res_uid_s01.gd`; `315 15 corpus/fixtures/run_battery.py`.
`corpus/README.md`, `PROVINCE.md`, `SCORECARD.md` are additions only. `SHONEN.md` is a canonical regeneration, not a seed rewrite: normalized against the PROTOCOL.md seed, marks/evidence lines removed, it is byte-equal modulo the repo name, and it contains four boxes only.

CASES pin integrity:
`git diff e89905162..b0d2c4990 -U0 -- corpus/fixtures/run_battery.py | grep -E "^-    \('"` → no output (no prior CASES tuple line removed). Between the rejected and fixed commits the full AST tuple list is identical: SHA-256 of the 600-tuple literal list is `88fb9fe1073a621cb8e60fa588976a08767579dffecf4f0790846742fe2f69c0` at both `7d9d9741` and `ff32e252`; 600 names, same order, 0 content diffs.

## 3. Declared claims — all VERIFIED

Counting command (committed): `sh reports/round-105/r105-count.sh <rev>` from the lane root.
Re-run by me at both revisions:

| rev | C1 res_uid / r105 / total CASES | C2 Q rows / M classes / M captured | C3 knowledge / full-header / SOURCES |
|---|---|---|---|
| `e89905162` | 21 / 0 / 585 | 0 / 0 / 0 | 2 / 0 / 0 |
| `b0d2c4990` | 29 / 7 / 600 | 23 / 32 / 32 | 5 / 3 / 31 |

Report before→after matches exactly: C1 21→29 and 585→600; C2 0→23 and 0→32/32; C3 2→5, 0→3, 0→31.

### C1 coverage — verified
- `res_uid` CASES 21→29; total CASES 585→600; r105 rows 0→7 (AST command above).
- Both final receipts: `res_uid_pass=29`, `res_uid_rows=29`, `r105_pass=7`, `r105_rows=7`.
- Forward and reversed UID lists are exact reverses: `list(reversed(forward)) == reversed` → True, 29 unique names each.
- Per-row isolation is real in code: `execute()` copies a pristine project per `res_uid_*` row and sets `XDG_DATA_HOME` and `RES_UID_ROOT` per row (`run_battery.py:2708-2732`); template is copied before CASES.
- Createid repair: fixture now emits `cfp_paths_differ=true` (`res_uid_s01.gd`), and a constant-return mutant was rejected per `reports/round-105/r105-R105ResUidExec2-review-fixes.md`.
- Shared control: clean shared arm 8/8, cache absent before/after; `export_readiness` writer PASS with cache created; seeded readers reproduce the class in `res_uid_path`, `res_uid_missing`, `res_uid_s01_diag` in both orders. Report correctly does **not** claim within-UID order leakage.
- Independent live check (below, §6): clean shared 3/3 pass with cache absent; export writer rc=0 and `uid_cache.bin` 3284 B; seeded `diag` prints `has_cache=true`; seeded `path`/`missing` emit `ERROR: Unrecognized UID:` lines. The no-cache isolated twin prints `has_cache=false`; class reproduced.

### C2 calibration — verified
- 23 Q rows, 32 M rows, 32/32 M rows carry a pure Q-id captured-by cell.
- Every referenced Q id exists; no M row has an empty fix cell. (`python3` parse of `QUALITY.md`/`round-105.md`.)
- Q23 cites M32 and the scheduling failure; M32 cites `r105-scheduling-failure.json`; both resolve.
- M27's correction is supported: base AST count is 21 `res_uid_` rows, while `reports/round-104/r104-adjudicator.md:42` says “23 res_uid rows remain green ×2”. The evidence path resolves in the lane.
- M15's base anchors resolve: `tilemap_lattice.gd:727-741` feeds `probe.get_rid()` and the allowlist at `run_battery.py:2817-2819 @e8990516` holds `ERROR: Parameter "found" is null.`.

### C3 depth + capability — verified
- Knowledge entries 2→5; entries with all three headers 0→3; SOURCES rows 0→31; statuses mined=10, queued=19, rejected=2; tiers A=30, B=1, C=0.
- Seven new fixture rows pass in both final receipts (7/7 each), with exact signatures.
- Capability row “curated source registry” exists in `SCORECARD.md` and is tied to the clean census, not pre-claimed.

## 4. SOURCES census — PASS

The assignment's path `/home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-census/scripts/sources-census.sh` does not exist; per the runtime boundary the canonical validator is `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`.

Command:
`bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate <lane> --today 2026-10-19 --verbose`

```
game-dev-2d-shokunin	ok	<lane>/corpus/SOURCES.md
census-exit=0
```

Lane's frozen census script `sh reports/round-105/r105-sources-census.sh`:

```
rows: 31
malformed: 0
tiers: A=30 B=1
statuses: mined=10 queued=19 rejected=2
duplicate ids (expect no lines):
enum/tier violations (expect no lines):
mined used-by missing (expect no lines):
exit=0
```

### Source rows re-opened (≥3; includes new tier-A and both rejects)

| Row | Tier/kind | Opened source and anchor | Gate quote / check | Verdict |
|---|---|---|---|---|
| S002 | A/docs | `docs.godotengine.org/en/4.7/classes/class_tilemaplayer.html`, `get_coords_for_body_rid` + `physics_quadrant_size` | “Such an RID can be retrieved from KinematicCollision2D.get_collider_rid(), when colliding with a tile.” (13 words) and “To get the exact cell coordinates, you need to set physics_quadrant_size to 1, which disables physics chunking.” (17 words) | quote and anchor exist |
| S005 | A/docs | `docs.godotengine.org/en/4.5/tutorials/migrating/upgrading_to_godot_4.5.html`, Behavior changes → TileMapLayer | “get_coords_for_body_rid() will return different values in 4.5 compared to 4.4, as TileMapLayer physics chunking is enabled by default.” (18 words) | quote and anchor exist |
| S009 | A/docs | `docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html`, Warning | “Physics in Godot, regardless of physics engine, is not deterministic” (10 words) and the same sentence continues “not guaranteed to run the same way for seemingly identical situations.” | quote and anchor exist |
| S026 | A/docs | `docs.godotengine.org/en/4.7/classes/class_resourceuid.html`, `has_id` | “Returns whether the given UID value is known to the cache.” (11 words) | quote and anchor exist |
| S027 | A/docs | `docs.godotengine.org/en/4.7/classes/class_kinematiccollision2d.html`, `get_collider_rid` | “Returns the colliding body's RID used by the PhysicsServer2D.” (9 words) | quote and anchor exist |
| S031 | A/docs, **rejected** | `docs.godotengine.org/en/4.4/classes/class_tilemaplayer.html`, Properties table | No match for `physics_quadrant_size`; `rendering_quadrant_size` present at line 49. Rejection reason/flip present. | reject correct |

S015's rejection/flip (“pre-release snapshot … flip: only a claim specifically about the dev1 build”) is explicit and retained. All 31 Gate bullets are present (`grep -cE '^- S[0-9]{3} '` → 31), each with URL, 2026-10-19 access date, and a grounded quote/location. Own-work rows S028/S029/S030 resolve; S030's two Git blobs match `git rev-parse b0d2c4990:<path>` (`b861d622…`, `e646d126…`).

## 5. Discernment spot-check — AGREE on all sampled decisions

| Candidate | Gate decision | Reviewer judgment | Reason |
|---|---|---|---|
| `knowledge/2026-10-19-tilemaplayer-body-rid-attribution.md` (K1) | admitted | **agree** | Docs S002/S027 name the collider RID as the argument; exact/chunked/wrongrid arms independently reproduced (`c5_coords=5,0`; `own_has=0 own_coords=0,0`); mutants reject; formula wording scoped to measured horizontal cells. |
| `knowledge/2026-10-19-res-uid-runtime-authority.md` (K2) | admitted | **agree** | `s04_persist` independently reproduced the cache/no-cache discriminator (`reader_has=true`, `nocache_has=false`); `text` aliases and `collision` survivor reproduced; text-vs-id rule is correctly stated. |
| ART C4 GUT/gdUnit4 exit/pending contracts | rejected this round | **agree** | Documentation-only rows S016–S023 stay `queued`; no runner installed/executed, so Q6/Q7 unmet. Rejection is taste, not lost work. |
| ART C5 rendered visual canary | rejected this round | **agree** | Headless host; no rendered baseline. Frontier still lists rendered output as open. |
| S031 (TileMapLayer 4.4) | rejected | **agree** | Page lacks `physics_quadrant_size` and 4.4 is EOL per S001; correct scope-limited rejection with flip. |

Recorded for the orchestrator to append to the round lesson (I am read-only): one admit and three rejects sampled, all `agree`. This supplies the outside spot-check the lane lesson marked pending.

## 6. Independent runtime exercise (real Godot; scoped, not full battery)

Runtime: `/usr/bin/godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`. Scratch project staged like the runner (fixtures copied, `.godot` absent, `project.godot` renamed, `pickup.tscn` staged, causal-chain readiness patch applied); per-run `XDG_DATA_HOME` and `RES_UID_ROOT`.

Rerun (all rc=0 unless noted):

| Scenario | Command shape | Observed |
|---|---|---|
| repaired createid | `godot --headless --path P --script res://res_uid_s01.gd -- --arm=createid` | `PASS res_uid_s01 createid … cfp_paths_differ=true create_id_distinct=true create_id_unregistered=true` |
| UID text aliases | `res_uid.gd --arm=text` | `alias_empty_eq_aaaa=true alias_0_eq_z=true roundtrip_int63max=true` |
| cache authority | `res_uid_s04.gd --arm=persist` | `cache_records=1 … reader_has=true … nocache_has=false uidfile_only_authority=false` |
| collision survivor | `res_uid_s04.gd --arm=collision` | `dup_warn=true records=1 dup_records=1 winner_in_pair=true` |
| tile exact | `r105_tile_rid.gd --arm=exact` | `c5_coords=5,0 c21_coords=21,0` |
| tile chunked | `r105_tile_rid.gd --arm=chunked` | `c5_coords=0,0 c15_coords=0,0 c21_coords=1,0` |
| tile wrong RID | `r105_tile_rid.gd --arm=wrongrid` | `own_has=0 own_coords=0,0` + one `ERROR: Parameter "found" is null.` |
| replay digest ×2 | `r105_phys_replay.gd --arm=digest` twice | both `digest=85a25c98…70870d9` |
| replay inproc | `r105_phys_replay.gd --arm=inproc` | `equal=true`, both run digests `85a25c98…` |
| replay perturb | `r105_phys_replay.gd --arm=perturb` | `differs=true`, `pert=5beeda4e…` |
| clean shared UID | same project, cache absent, `path`/`missing`/`s01_diag` | 3/3 PASS; `has_cache=false`; cache absent before/after |
| seeded writer | `godot --headless --path P --export-debug Linux/X11 out/fixture.x86_64` | rc=0, `[ DONE ]`, exe non-empty, `.godot/uid_cache.bin` 3284 B |
| seeded readers | same project, `diag`/`path`/`missing`/`createid` | `diag has_cache=true`; `path`/`missing` emit `ERROR: Unrecognized UID:` lines (battery would classify FAIL); `createid` PASS |
| finite-life detach | `descendant_pipe_probe.gd --spawn-detach` | spawned `sleep 8` alive at +0.0/+0.2/+1.0 s after Godot exit (ppid 1520), signature present, no `DESCENDANT_PIPE_AFTER_EXIT_WRITE`; orphan killed |

Scheduling check:
- CASES positions: `res_uid_*` occupy 548–576; tail `crash_*`/`descendant_*` occupy 596–599. `run_shared_res_uid_probe` executes at `case_index == last_res_uid_index` (576), before r105 rows and long before the tail. The rejected `7d9d9741` ran it after the CASES loop.
- `r105-scheduling-failure.json` at `7d9d9741`: `battery_verdict=FAIL`; failed guards `detached_descendant_orphaned_alive=false` and `prior_meta_rows_stable_29_discriminations=false`.
- Final receipts at `ff32e252`: both guards true, all seven pipe discriminations true.
- The scheduling delta is a pure move plus 13 new lines; 142 deleted lines are the moved block; the 600 CASES tuples are byte-identical between `7d9d9741` and `ff32e252` (hash above), and the `sleep 8` lifetime is unchanged.

Full-receipt provenance:
- Committed JSON reconstructs byte-identically from the two live `verdicts.json` files:
  `python3 reports/round-105/r105-receipts.py corpus/live/runs/2026…/verdicts.json …` → SHA-256 `e9c468b9…35bb27` for both reconstructed and committed `r105-battery-receipts.json`; `cmp` exit 0.
- Both runs: `pass=621 fail=0 rows=621 cases=600 cases_backed_rows=600 meta_rows=21`, `cases_bad_multiplicity={}`, `duplicate_result_names={}`, `res_uid 29/29`, `r105 7/7`, shape `audited_rows=602 flag_count=0`, evasion `shape_count=10 control_count=4 flags=0`.
- Eight startup source blobs in both receipts equal `git rev-parse b0d2c4990:corpus/fixtures/<file>`; `current_matches_source_blobs` all true.
- Initial 622-row receipts preserved byte-identically at `r105-initial-battery-receipts.json` (SHA-256 `34e0f9ee…b60511` equals the old `r105-battery-receipts.json` at `7d9d9741`). Failed pre-scheduling receipts preserved separately.

**Exactly what was not rerun:** the two full 621-row batteries, the three literal full-battery `recheck:` commands, and the full 4/4 / 20+20 / 5/5 multi-run censuses. Their committed receipts and seat reports were inspected and the receipt extraction reproduced byte-for-byte; scoped live runs above corroborate the changed UID boundary and the finite-life scheduling predicate. I do not present this as a full-battery re-execution.

## 7. New knowledge entries — PASS with one evidence note

| Entry | Header trio | Recheck target | Claim ↔ source | Independent check |
|---|---|---|---|---|
| K1 tile body-RID attribution | `source:`, `verified-at:`, `recheck:` present, 3/3 | battery `PASS r105_tile_rid_exact:` | S002/S005/S027/S029/S030; quote verified | exact/chunked/kinematic/wrongrid rerun; scoped claims match |
| K2 UID runtime authority | 3/3 | battery `PASS res_uid_s04_persist:` | S026/S028; quote verified | persist/text/collision rerun; matches |
| K3 physics replay boundary | 3/3 | battery `PASS r105_phys_replay_inproc:` | S009/S010/S025/S030; quote verified | digest ×2 identical, inproc equal, perturb differs |

All three carry a Q6 claim-to-CASES table naming fixture, arm, exit, exact PASS line, and both serial receipt references. K3 correctly pins invariants/in-process equality/perturb-differs, not the raw digest; the docs' no-determinism guarantee is quoted and the host-scope limits are stated. K2 correctly avoids the contested `cache_version=1` header claim.

Evidence note (residual, not a gate defect): K1's 4/4 and K3's 20+20 + 5/5 run censuses are summarized in committed seat reports (`r105-R105TileRidExec.md`, `r105-R105ReplayExec.md`) with raw output elided (“(all 40)”), while the committed final receipts contain one digest/inproc row per battery. The entries' rechecks assert the row prefix, not the multi-run census. My scoped 2/2 cross-process digest identity, inproc equality, perturb-differs, and four tile-arm runs corroborate but do not re-derive those counts.

## 8. Credentials — PASS

Command:
`git -C <lane> diff e89905162..b0d2c4990 | grep -qE '[vault-URI scan prefix redacted][A-Za-z0-9]|BEGIN [A-Z ]*PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9]'`
→ no match; sweep printed nothing.

## 9. Report conformance — PASS

- Required sections present in order: `## Work performed`, `## Landed changes`, `## Before → after measurements`, `## SHONEN`, `## Sources & frontier`, `## Mistakes`, `## Trend verdicts`, `## L0 questions`, `## Integrator notes`.
- No `[x]` anywhere in the report or `SHONEN.md`; the only `[x]` token in the report is inside backticks in prose (“without any `[x]`”). SHONEN has `[ ]` + three `[~]` with pointers.
- Cites the lane round commit `b0d2c499` and implementation `ff32e252`; both exist and are ancestors of the lane HEAD.
- Every declared claim carries a counting command and a measured before→after; the rejected iteration and initial receipts are retained as adverse history.
- Process-only claims not artifact-verifiable (10 L2 leaves in one batch, no model override, no push, no sibling writes) are stated without contradiction; no artifact in the lane contradicts them.

## 10. Recommended verdicts

### Per-axis (owned axes)
| Axis | Recommendation | Evidence |
|---|---|---|
| coverage | **improved** | UID CASES 21→29, total 585→600; 29/29 ×2; per-row project/XDG/root isolation; clean shared 8/8 vs seeded writer→reader class; createid repair with rejecting mutant. |
| calibration | **improved** | Q rows 0→23, M classes 0→32, 32/32 mapped; M27–M32 correct real errors; Q23 learned from the round's own scheduling failure; outside spot-check agrees on admit/reject sample. |
| depth | **improved** | knowledge 2→5, full-header 0→3, SOURCES 0→31; K1 corrects the r92 wrong-RID interpretation; K3 separates host-observed replay identity from engine guarantee; two frontier rows advanced. |
| freshness / operability / adjacency | unchanged / no claim | No axis move claimed. Sources opened 2026-10-19 with on-release rechecks; recheck commands resolve; connector report records no sibling mutation. No harm observed. |

### Trends
- **Expansion: improved.** Two net-new admitted entries on previously open coverage-map ground (TileMapLayer body-RID attribution; physics replay boundary), each `source:` citing mined rows. Not claimed from the 31-row registry alone.
- **Quality: improved.** Wrong-RID interpretation corrected; r92's allowlisted-ERROR-as-state-fact class captured as Q22; cache-regime control disentangled from row-order leakage; final receipts reconstruct byte-identically and both failed meta guards are true.
- **Discernment: improved via this outside spot-check.** LEARNING.md's improved condition — “the spot-check agrees with the gate on admits and rejects” — is met on one admit and three rejects. The lane's conservative “unchanged / pending” is superseded by this non-author agreement; if the orchestrator weighs the low findings below as material, `unchanged` is also defensible, but no sampled gate decision is wrong.

### Recommendation
**ADMIT.** All three declared claims verify against re-run counting commands; the runtime boundary change and scheduling fix are independently reproducible with real Godot; append-only, provenance, census, credential, and report-conformance checks pass. No axis harm observed. Recommended closure: record the outside spot-check in `corpus/lessons/round-105.md` and note the two low-severity documentation findings.

## 11. Defects by severity

No high or medium blocking defect found.

**Low-1 — SOURCES search log double-counts S031.**
`corpus/SOURCES.md` Search log Sweep 2 says “Identified 6 … included 5 (S026–S030), excluded 1 (S031, see next note)”; Sweep 3 says “Identified 1, screened 1, included 0, rejected 1 (S031)”. The same rejected source is counted in two sweeps, so the log's identified total is 32 while the registry has 31 rows. No claim or row is wrong; the log is internally inconsistent. Fix: count S031 once (keep it as the Sweep 3 rejection, or merge the sweeps).

**Low-2 — QUALITY header says every criterion cites a lesson; Q1–Q3 cite contracts.**
`corpus/QUALITY.md` opens “Grown only from lessons: every criterion cites the lesson that produced it,” but Q1 cites `CORPUS.md`, Q2 cites `CORPUS.md`, and Q3 cites `PROTOCOL.md`. The count of 23 is accurate and the 32 M classes map to Q4–Q23; the blanket wording is what overstates. Fix: either label Q1–Q3 as foundational contract rows or scope the “grounded in lessons” phrasing to the 20 lesson-derived criteria.

**Informational — multi-run census evidence is summary-level.**
See §7. K1's 4/4 and K3's 20+20 are commands-plus-summary in committed seat reports; the committed compact receipts carry one row per battery. Independent scoped runs corroborate the boundary, but the exact multi-run counts are not re-derivable from the persisted artifacts alone.

**Environmental, not a lane defect — census tool path.**
The assignment's `fleet-census/scripts/sources-census.sh` is absent; the canonical `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` validated clean, consistent with the runtime boundary.

## 12. Residual risk and verification gaps

- Full 621-row batteries were not re-executed. The committed receipt is self-consistent and reconstructs from the two live verdicts byte-identically; source blobs match HEAD. This is strong provenance but not a fresh full-battery replay.
- The shared-resource control proves cache-regime interference, not within-UID row-order ordering; the lane reports this limitation and both orders agree, so the disclosure is honest.
- The stale-artifact risk of `corpus/live/` (40,677 legacy tracked files) is inherited and correctly named as an integrator defect, not silently repaired.
- Process claims (L2 batch shape, model routing, no push, no sibling writes) are not artifact-verifiable from the lane repo; no contradicting evidence was found.
- Scratch is ephemeral; all commands above are rerunnable from the cited revisions and runner/fixture paths.

