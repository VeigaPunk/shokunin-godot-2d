# Round 105 — lessons

## Mistakes

| # | class | evidence pointer (path:line) | captured-by (QUALITY.md criterion id or none-before-r105) | fix |
|---|---|---|---|---|
| M1 | negative control contaminated by positive sidecars (r6 HOLD) | `LOG.md:57` | Q7 | runner empties the negative scratch before and after, proven by the runner not assumed |
| M2 | unresolved failure left with no causal fix and no next probe (r17 HOLD; r16 intermittent export retained) | `LOG.md:169-172` | Q5 | HOLD keeps the open hypothesis and names the next probing command as its recheck |
| M3 | verifier ran the pre-fix commit; runner diff uncommitted (r64) | `SCORECARD.md:24` | Q9 | verify the committed blob and record its SHA in the verdict |
| M4 | declared grid overstated its resolution (r68 ~80x claim falsified as written) | `SCORECARD.md:64` | Q17,Q21 | report grid resolution/edge uncertainty, and never let a claim exceed its evidence tier |
| M5 | hypothesis refuted at a wider scope (r70 fabrication window is runner plumbing, not engine-general) | `SCORECARD.md:81` | Q19 | recast to the narrower measured scope and keep the refutation in the ledger |
| M6 | pins falsified after landing (r79 P1 dispatch-order snapshot, P2 same-frame visibility, P3 new member) | `SCORECARD.md:158` | Q19 | every pin carries its mechanism and falsifier; correction names the falsified clause |
| M7 | PASS-while-broken harness: hardcoded ENet ports let concurrent batteries cross-connect (r88 BLOCKER) | `LOG.md:1108-1111` | Q8,Q11 | pid-derived ports, fail-closed rc guards, bind-loser negative, serial receipts |
| M8 | dead flag / unmeasured claim (`--offy` no-op, r95) | `SCORECARD.md:280`; `LOG.md:1251` | Q6,Q12 | retire the row with its token and keep a token-count tripwire |
| M9 | custody-broken-at-link, systemic r98-r100 (evidence no longer resolves at its cited path) | `LOG.md:1196`, `LOG.md:1206` | Q13 | cite resolve-at-HEAD paths; link check at close |
| M10 | provider failure orphaned 4 fixtures plus 7 design-superseded ones (r101) | `LOG.md:1254-1256` | Q15 | every orphan gets a disposition (adopt with fresh pins or reject) before close |
| M11 | row state leaks across rows: shared scratch-project uid cache retired 7 res_uid rows pre-close (r104) | `LOG.md:1319-1320` | Q10 | per-row scratch project plus a shared-cache negative control that reproduces the class |
| M12 | operator reboot precluded a re-run after post-run retirement (r104) | `LOG.md:1323-1324` | Q16 | fresh run or an explicit disclosed gap line |
| M13 | simplifier breached read-only scope and overlapped tracked edits (r52) | `LOG.md:520` | Q15 | touched-file list checked against `git status`; read-only seats stay read-only |
| M14 | broad `git add` swept 180 scratch files (r6 bookkeeping correction) | `LOG.md:60` | Q14 | extend ignore rules and verify with `git ls-files`, not assumption |
| M15 | probe passed the wrong argument and pinned the result as engine behaviour (r92 fed the mover's `get_rid()` to `get_coords_for_body_rid`, allowlisted `ERROR: Parameter "found" is null.` and pinned `(0,0)` + "unreachable from script"; confirmed r105 by `r105_tile_rid.gd --arm=wrongrid` and a separate critic probe) | `corpus/fixtures/tilemap_lattice.gd:727-741`; allowlist `corpus/fixtures/run_battery.py:2817-2819` at `e8990516` | Q22 | feed the API the argument its docs name (S002/S027), and never pin a return that rides an allowlisted ERROR as a state fact |
| M16 | promised curation artifact absent for tens of rounds; routed note dropped from the next queue (QUALITY.md, knowledge headers) | `LOG.md:1287`, `LOG.md:1307` | Q4 | land the artifact and close each routed note in the round that owns it |
| M17 | post-commit replay overwrote committed lesson receipts (r54) | `LOG.md:537` | Q9 | committed receipts are immutable; new runs write unique paths |
| M18 | non-additive edit under an "additive" claim; matching tuples masked the prior-row mutation (r55) | `LOG.md:543` | Q9 | diff must touch no prior expected string; tuple equality alone is not proof |
| M19 | harness ceiling: dropped or duplicated CASES rows invisible to the battery (r100) | `LOG.md:1204` | Q18 | CASES-count gate read from results, not mutable records |
| M20 | ledger misattribution corrected append-only (r101 blamed the hold arm; the old-bound arm was red) | `LOG.md:1266-1268` | Q20 | separate observation from causal attribution; append the correction, keep the original |
| M21 | seat identity confusion produced a missing report and an unowned diff (r25) | `LOG.md:248` | Q15 | missing report is lane-failure telemetry, never admission evidence |
| M22 | mechanism-blind pin: positive emitted all-muted fields and a disabled-mechanism negative reproduced the byte-exact pin (r79) | `SCORECARD.md:158` | Q7 | positive must emit a non-muted field; the negative must fail inside the mechanism, not beside it |
| M23 | constant latency bound invalidated by host drift (0.39 s to 0.8 s); margin must be pinned (r101/r102) | `LOG.md:1271-1278` | Q5,Q17 | re-derive the bound from the current margin and state both sides |
| M24 | row self-reported `matches_pinned=false` and was still counted green (`s01_createid`, r104) | `LOG.md:1321-1322` | Q16 | derive expectations from inputs; retire any self-contradicting row |
| M25 | non-existent CLI token cited as a measurement (`--physics-ticks-per-second` silently ignored on 4.7.2, r90) | `LOG.md:1127-1128` | Q12 | count the token in the fixture/engine surface before citing it |
| M26 | parallel Godot launches caused frame flakiness (r13/r15) | `corpus/knowledge/seed.md:14-15` | Q8 | serial-only PASS evidence |
| M27 | row count claimed from the seat patch, not the landed CASES list (r104 "23 res_uid rows"; landed AST count 21; the LOG's own "+33 net" = 21+12) | `LOG.md:1312-1313`; `reports/round-104/r104-adjudicator.md:42`; commit `5f924226` subject | Q18 | count rows with the AST CASES command at the measured commit, never from a patch or seat report |
| M28 | isolation claimed per-row while implemented per-run (r104 comment "per-row XDG isolation"; one `XDG_DATA_HOME` per battery run) | `corpus/fixtures/run_battery.py:2526-2533` at `e8990516` | Q10 | isolation claims name the unit (row/run) and ship the negative control that shows the unit is load-bearing |
| M29 | control confounded cache regime with within-UID row ordering (initial r105 shared project editor-seeded, isolated projects cache-less; first shared UID row already failed) | `reports/round-105/r105-R105FinalReviewer.md` F1 | Q10 | symmetric fresh templates, unseeded-shared baseline and explicit preceding export-writer intervention; claim writer→reader cache-regime interference, not measured within-UID order dependence |
| M30 | nested probe ignored `append_result=False`, duplicating a meta result name (initial r105 receipts: 600 CASES + 22 meta rows but only 21 distinct meta names) | `reports/round-105/r105-R105FinalReviewer.md` F2/F3 | Q18 | respect the result-append contract in nested export probes; compare CASES by identity/multiplicity and count unique meta rows separately |
| M31 | same-path repeatability/round-trip/nonregistration pins did not reject a constant-returning path-ID implementation | `reports/round-105/r105-R105FinalReviewer.md` F5 | Q7 | add distinct-path inequality and exercise a constant-returning scratch mutant |
| M32 | new shared-cache probe ran between the detached-control CASES tail and its finite-life meta check, expiring the `sleep 8` orphan and harming two prior meta verdicts in the first committed final replay | `reports/round-105/r105-scheduling-failure.json`, `reports/round-105/r105-pre-scheduling-fix-receipts.json` at `7d9d9741` | Q23 | schedule the probe before the crash/descendant tail; keep all original liveness bounds and pins unchanged; replay the full battery in both orders after the scheduling fix |

## Gate

### Sources (contract v1 rule 1) — 31 new rows, all opened 2026-10-19 by R105SourcesExec

Per row: URL — access date — ≤25-word quote + location grounding `teaches`. Status/recheck/used-by
changes: none (all rows new this round). Rejected: S015 (pre-release snapshot), S031 (4.4-era class
reference) — reasons and flips in the registry.

- S001 — https://docs.godotengine.org/en/stable/about/release_policy.html — 2026-10-19 —
  §"What are the criteria for compatibility across engine versions?": "Godot's physics
  engine is not deterministic, so physics bug fixes are not considered to break
  compatibility." [obs]
- S002 — https://docs.godotengine.org/en/4.7/classes/class_tilemaplayer.html — 2026-10-19 —
  Property Descriptions → physics_quadrant_size: "To get the exact cell coordinates, you
  need to set physics_quadrant_size to `1`, which disables physics chunking." [obs]
- S003 — https://docs.godotengine.org/en/4.7/classes/class_tilemap.html — 2026-10-19 —
  Class header banner: "Deprecated: Use multiple TileMapLayer nodes instead." [obs]
- S004 — https://docs.godotengine.org/en/4.5/tutorials/2d/using_tilemaps.html — 2026-10-19 —
  §Specifying the TileSet in the TileMapLayer: "The recommended way to reuse the same
  TileSet in several TileMapLayer nodes is to save the TileSet to an external resource."
  [obs]
- S005 — https://docs.godotengine.org/en/4.5/tutorials/migrating/upgrading_to_godot_4.5.html
  — 2026-10-19 — Behavior changes → TileMapLayer: "get_coords_for_body_rid() will return
  different values in 4.5 compared to 4.4, as TileMapLayer physics chunking is enabled by
  default." [obs]
- S006 — https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html —
  2026-10-19 — Command line reference note: "unknown command line arguments have no effect
  whatsoever."; Run options table: `--import` "Starts the editor, waits for any resources
  to be imported, and then quits." [obs]
- S007 — https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html —
  2026-10-19 — §Configuration files + §Exporting from the command line: "Exporting from
  the command line still requires an export preset to define the export parameters."
  [obs]
- S008 — https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/import_process.html
  — 2026-10-19 — §Files generated: "Make sure to commit these files to your version
  control system"; §Importing assets: access via FileAccess "will work in the editor, but
  it will break in the exported project". [obs]
- S009 — https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html
  — 2026-10-19 — Warning admonition: "Physics in Godot, regardless of physics engine, is
  **not** deterministic." [obs]
- S010 — https://docs.godotengine.org/en/4.7/tutorials/physics/interpolation/physics_interpolation_introduction.html
  — 2026-10-19 — §Physics ticks and rendered frames: "The physics proceeds at a fixed
  tick rate … which defaults to 60 ticks per second." [obs]
- S011 — https://docs.godotengine.org/en/4.7/tutorials/inputs/inputevent.html — 2026-10-19 —
  §How does it work? ordered list: "`Node._unhandled_input()` callback will be called if
  overridden … ideal for full-screen gameplay events". [obs]
- S012 — https://godotengine.org/releases/4.6/ — 2026-10-19 — §2D → Rotatable scene tiles:
  "when you place a scene instance on a grid cell in your tile map … you can rotate the
  scene tile in 90-degree increments". [obs]
- S013 — https://godotengine.org/article/maintenance-release-godot-4-6-1/ — 2026-10-19 —
  Byline + changes: "16 February 2026"; "Physics: Fix transform updates sometimes being
  discarded when using Jolt (GH-115364)." [obs]
- S014 — https://godotengine.org/article/maintenance-release-godot-4-5-2/ — 2026-10-19 —
  Changes list: "2D: Check for tiles outside texture on TileSet atlas settings changes
  (GH-112271)"; "Core: Improve determinism of UIDs (GH-111858)." [obs]
- S015 — https://godotengine.org/article/dev-snapshot-godot-4-5-dev-1/ — 2026-10-19 —
  Footer + header: "this release is built from commit 97241ffea"; "by definition a
  pre-release piece of software". Grounds REJECTED (pre-release snapshot, not current
  normative behavior). [obs]
- S016 — https://gut.readthedocs.io/en/v9.6.1/index.html — 2026-10-19 — Page title:
  "Gut 9.6.1 (Godot 4.6)"; body: "GUT 9 requires Godot 4." [obs]
- S017 — https://github.com/bitwes/Gut/tree/v9.6.0 — 2026-10-19 — README Features list:
  "Export results in standard JUnit XML format"; version table row "9.6.0 … 4.6". [obs]
- S018 — https://gut.readthedocs.io/en/v9.6.0/Command-Line.html — 2026-10-19 — §Command
  Line: "0 will be returned if all tests pass and 1 will be returned if any fail (pending
  doesn't affect the return value)." [obs]
- S019 — https://gut.readthedocs.io/en/v9.6.1/Export-Test-Results.html — 2026-10-19 —
  §Setting the export file: "You can export test results in the JUnit XML format";
  settings `-gjunit_xml_file`, `-gjunit_xml_timestamp`. [obs]
- S020 — https://godot-gdunit-labs.github.io/gdUnit4/latest/advanced_testing/cmd/ —
  2026-10-19 — §Return Codes: "0 = all tests success; 100 = ends with test failures; 101 =
  ends with test warnings." [obs]
- S021 — https://godot-gdunit-labs.github.io/gdUnit4/latest/advanced_testing/sceneRunner/ —
  2026-10-19 — §Definition: "simulate input events such as keyboard or mouse input and/or
  simulate scene processing over a certain number of frames." [obs]
- S022 — https://github.com/godot-gdunit-labs/gdUnit4-action — 2026-10-19 — README
  Configuration tables: inputs `godot-version`, `paths`, `timeout`, `version`,
  `warnings-as-errors`. [obs]
- S023 — https://raw.githubusercontent.com/godot-gdunit-labs/gdUnit4-action/master/.github/workflows/ci-pr.yml
  — 2026-10-19 — `compatibility-check` job, Verify step: "ERROR: Expected exit code 78
  for version incompatibility"; matrix jobs `unit-tests-v5x/v61/v62`. [obs]
- S024 — https://raw.githubusercontent.com/godotengine/godot/df623583/.github/actions/godot-project-export/action.yml
  — 2026-10-19 — Steps `Run project files from folder` / `Run exported project PCK/ZIP`:
  "xvfb-run ${{ inputs.bin }} --main-pack /tmp/test_project.pck … --write-movie"; md5sum
  output checks. [obs]
- S025 — https://github.com/godotengine/godot/issues/112976 — 2026-10-19 — Issue body:
  "nondeterminism even within the same game instance running on the same computer";
  maintainer AThousandShips: "The physics engine is not deterministic … the lack of
  determinism is not a bug". Closed via godot-docs#11803. [obs]
- S026 — https://docs.godotengine.org/en/4.7/classes/class_resourceuid.html — 2026-10-19 —
  Method Descriptions: "has_id(id: int) — Returns whether the given UID value is known to
  the cache."; "id_to_text … Converts the given UID to a `uid://` string value." [obs]
- S027 — https://docs.godotengine.org/en/4.7/classes/class_kinematiccollision2d.html —
  2026-10-19 — Method Descriptions: "get_collider_rid() — Returns the colliding body's RID
  used by the PhysicsServer2D." [obs]
- S028 — corpus/lessons/r104-resource-loader-uid.md — 2026-10-19 — §1 Law: "res://.godot/uid_cache.bin
  is the runtime authority for uid:// resolution. <name>.*.uid is the editor's durable
  input; a plain --script process never reads it." [obs]
- S029 — corpus/fixtures/tilemap_lattice.gd — 2026-10-19 — `_physics`/`_timing`/`_quadrant`
  arms (~L700–860): "the collision body is the layer node itself"; "update_internals IS
  the synchronous apply lever". [obs]
- S030 — corpus/fixtures/r105_tile_rid.gd + corpus/fixtures/r105_phys_replay.gd —
  2026-10-19 — Executed this session: `PASS r105_tile_rid exact … c5_coords=5,0
  c21_coords=21,0`; `PASS r105_tile_rid wrongrid … own_has=0 own_coords=0,0`;
  `PASS r105_phys_replay perturb differs=true …`. [obs]
- S031 — https://docs.godotengine.org/en/4.4/classes/class_tilemaplayer.html — 2026-10-19 —
  Properties table lists `rendering_quadrant_size` but **no** `physics_quadrant_size`
  (pre-chunking API); grounds REJECTED for current-behavior scope. [obs]

### Knowledge admissions (bar: `corpus/QUALITY.md`)

| candidate | verdict | reason |
|---|---|---|
| `knowledge/2026-10-19-tilemaplayer-body-rid-attribution.md` (ART C1) | **admitted** | Q4 headers; fixture `r105_tile_rid.gd` 4 arms, positive + `wrongrid` negative + 2 scratch mutants FAIL (Q7); independent critic probe reproduced exact/quadrant coords (R105Critic); Q22 refusal receipt labelled |
| `knowledge/2026-10-19-res-uid-runtime-authority.md` (STATE cand. 1–2) | **admitted** | Q4; curation of r104 lesson §1/§3/§4 (S028) + S026; rows `res_uid_s04_persist` (sidecar-only negative `nocache_has=false`), `res_uid_text`, `res_uid_s04_collision` re-run this round |
| `knowledge/2026-10-19-physics-replay-boundary.md` (ART C2) | **admitted** | Q4; eight-body-plus-character fixture invariants + perturb discrimination; no cross-process digest pin (S009). R105Critic's six-body 1-digest/20-run probe is different-scenario corroboration only, not independent reproduction of K3 |
| ART C3 clean-checkout import→export→launch | **rejected (this round)** | no executed fixture; Q6/Q7 unmet — routed to r106 planned |
| ART C4 GUT/gdUnit4 exit/pending contracts | **rejected (this round)** | documentation only, no runner installed or executed — Q6 unmet; rows S016–S023 stay `queued` |
| ART C5 renderer-pinned visual canary | **rejected (this round)** | headless host only, no graphical baseline — Q7 unmet |

### Draft corrections before first landing

S015/S031 `recheck` draft values `—`→`180d`; S028/S029 revision anchors bound to
`e8990516`, S030 to its exact Git blobs. All rows are first-working this round,
not edits to previously committed registry rows. Final reviewer/critic findings
and corrected controls are preserved in the seat reports; fresh full receipts
supersede the initial two runs' duplicate-meta / missing-run-byte provenance.

### Outside spot-check

**Pending orchestrator non-author verification:** ≥1 admit and ≥1 reject,
≥3 registry rows re-opened, every counting command re-run. R105FinalReviewer
and R105FinalCritic are still this lane; their source re-opens and disagreement
lessons improve the bar but do not certify outside discernment. SHONEN stays
unchecked/self-asserted, never `[x]`.

## Append-only metadata corrections

### QUALITY provenance

Parent-approved correction to the blanket opening statement in `corpus/QUALITY.md`: Q1–Q3 are mandatory inherited baseline criteria, not new lesson-derived criteria. Their provenance is the canonical mint template `.tower/worktrees/kaika/kimi-shokunin-canon/templates/mint/corpus/QUALITY.md:20-22`, with `CORPUS.md:24-26` and `PROTOCOL.md:469-471` as the original cited sources. Q4–Q23 are 20 lesson-derived criteria; the unchanged total is 23. No new Q rows or retroactive lessons are asserted.

### SOURCES named-set reconciliation

The appended correction in `corpus/SOURCES.md` separates the counts: Sweep 1 S001–S025 identified 25 / included 24 / rejected 1; corrected Sweep 2 S026–S030 identified 5 / included 5 / excluded 0; Sweep 3 S031 identified 1 / included 0 / rejected 1. S025's negative-claim note is a re-screen of its existing row, not a new unique identification. The disjoint sets total 31 unique IDs, matching the registry's 29 non-rejected and 2 rejected rows.

### Outside spot-check and disposition

The persistent outside review `reports/round-105/r105-outside-review.md` agrees with admitting K1/K2 and rejecting ART C4/C5/S031. The critic `reports/round-105/r105-outside-critic.md` agrees with the sampled source checks but finds the frozen C2/C3 dependency: C2 QUALITY criteria created the admission prerequisite for C3 knowledge entries, so the declared claims are not causally separable. Parent disposition is REJECT/HONEST STOP for round 105 as declared. No promotion and no post-hoc claim narrowing are made; preserved runtime observations and receipts are not erased or reinterpreted by this metadata correction.
