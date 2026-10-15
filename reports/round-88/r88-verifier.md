# r88 verifier — named non-author verification of `3c47eee`

Seat `VERIFIER` (g2d lane r88, named non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, headless, 60 tps), Python
3.14.7, 32-core. Target commit: `3c47eee46bc2b13138787e4dcb95590566057ec2`
(*r88 work: mp loopback + sprite/light/audio/vis surfaces — 8 rows (207->215),
spawner-refusal + uid-tail corrections folded*). Author report:
`reports/round-88/r88-author.md`; receipts under `corpus/live/r88-verifier/`.

No `lsp` device on this host (same state as every r88 seat); this seat made no
edits — verification only, so no symbol work was required. No commits; all
artifacts untracked scratch + this report.

## Method

```
git archive --format=tar 3c47eee | tar -x -C corpus/live/r88-verifier/tree
cd corpus/live/r88-verifier/tree
PYTHONDONTWRITEBYTECODE=1 timeout 1200 python3 -B corpus/fixtures/run_battery.py \
    --runs <abs>/corpus/live/r88-verifier/runs{1,2}   # serial, rep1 then rep2
```

Frozen-tree integrity, pinned twice (pre- and post-reps):
- **File-set**: `git ls-tree -r --name-only 3c47eee` vs extracted
  `find -type f -o -type l` = **93 462 = 93 462, 0 diffs**
  (`freeze/git-ls-tree-3c47eee.txt`, `tree-files.txt`, `tree-files-post.txt`).
- **Content**: `GIT_DIR=$PWD/.git GIT_WORK_TREE=…/tree git diff --quiet
  3c47eee` → **rc=0** both pre- and post-reps (reps write only under
  `--runs`, never into the tree).
- **Blobs**: frozen `run_battery.py` sha `fde5913b…` ==
  `git show 3c47eee:…`; `r88_surfaces.gd` sha `78370a04…` and
  `r88_spawnable.tscn` sha `89b9ddbe…` — **byte-equal to the author's
  published claims**.
- Archive determinism: `git archive 3c47eee | sha256sum` =
  `9a7bea47…` (recomputable).
- `ast.parse` on the frozen `run_battery.py`: clean, 3735 lines; AST census
  `CASES=208` (200 prior + 8 `r88_surfaces_*`) + 7 meta = **215**, matching the
  author's insertion-only claim (`git show --stat 3c47eee`: +468/−0 across
  exactly the 3 declared files; `git diff 3c47eee f9e8a5b -- corpus/fixtures/`
  is empty — the evidence-custody commit changed no fixture bytes).
- `offset_polyline` absent from `r88_surfaces.gd` and `run_battery.py`
  (grep rc=1) — hazard-3 clean.

## Battery reps on the frozen tree

| rep | window (UTC) | rows | verdict | rc | wall | stderr |
|---|---|---|---|---|---|---|
| rep1 | 18:29:02→18:32:25 | 215 | **FAIL — 214/215** | 1 | ~203 s | 0 B |
| rep2 | 18:35:52→18:39:03 | 215 | **PASS 215/215** | 0 | ~191 s | 0 B |

Receipts: rep1 `runs1/20261015T182903032573Z/verdicts.json` sha
`3aa2b9d2…`; rep2 `runs2/20261015T183553023488Z/verdicts.json` sha
`70bf54f2…` (`freeze/receipt-shas.txt`).

**rep2 is the clean-condition reproduction the dispatch asks for: 215/215
PASS, tuple byte-identical 215/215 vs author runs1 AND runs2 (0 mismatches).**
rep1's sole FAIL is a measured instance of the round's already-documented
same-port MP contention hazard — analyzed in §F below; it is an environment
interaction, not a property of the frozen bytes (identical tree, rep2 clean).

## Claim results

| # | claim (author report / dispatch) | verdict | evidence |
|---|---|---|---|
| C1 | frozen tree at `3c47eee`, file-set + content identity | **VERIFIED** | 93 462 entries, 0 diffs; `git diff --quiet` rc=0 pre+post; blob shas equal author claims |
| C2 | `run_battery.py` ast.parse clean; +42 insertion-only, CASES 207→215, `expected_errors`+1, new `r88_` floor gate | **VERIFIED** | ast.parse OK; CASES=208 seeded (+8 `r88_`) +7 meta; `r88_surfaces_sprite_phys` allowlist `ERROR: Index p_frame = 3 is out of bounds (vframes * hframes = 2).` (exact); `r88_expected_errors_all_matched` discrimination present and `true` in both my reps |
| C3 | battery rep → 215/215 PASS | **VERIFIED** (rep2; rep1 flaked, §F) | rep2: 215/215 PASS rc=0, stderr 0 B; stdout 216 lines = 215 rows + `PASS battery:` trailer |
| C4 | prior 207 byte-identical modulo envelopes/volatile + disclosed census delta; 8 new rows | **VERIFIED** | rep2 vs r88-baseline rep1 (`91b3708d…`, frozen 207-scope receipt): `common=207 new_only=8 old_only=0`, tuple-identical **206/207** — sole diff = `probe_error_clause_surface` census meta = the author's disclosed census delta; all 200 prior seeded + 6/7 meta byte-identical. rep2 vs author runs1: **215/215 tuple byte-identical** — prior-207 trivially reproduced |
| C5 | mp_loopback arm ×3 fresh → uid normalization yields stable pins | **VERIFIED** | 3 fresh launches (`arms/mp_loopback.v{1,2,3}`): rc=0, stderr 0 B, raw `uid_c` ∈ {1173883505, 183566364, 1661825720} — all distinct, all normalized to `<C>`; **uniq PASS payload = 1**, byte-equal to the CASES pin |
| C6 | sprite_phys → exactly 1 whitelisted ERROR | **VERIFIED** | `arms/sprite_phys.v1.err`: exactly **1** `ERROR:` line, byte-equal to the allowlist entry, + 4 inert backtrace lines (5 total); rc=0; PASS payload byte-equal to CASES pin |
| C7 | host census: no stray godot after | **VERIFIED** | post-run: 0 godot processes attributable to r88-verifier; exactly 1 foreign `r88-critic` godot in flight (not mine) |
| C8 | gates: `r88_expected_errors_all_matched`, `r87_…`, `phys2d_…` true; census `dead_entry_count=0` | **VERIFIED** | both reps: all three gates `true`, `dead_entry_count=0`, `rows_with_expected_errors=53` (52+1 new), sprite_phys entry `matched_lines=1 dead_in_run=false shape=exact` |

### Tuple-compare summary (tooling: `compare.py`/`tuples.py`/`r88_compare.py`
copied verbatim from `corpus/live/r88-baseline/`)

| mine → ref | common | tuple-identical | raw diffs | normalized diffs |
|---|---|---|---|---|
| rep2 → author runs1 | 215 | **215/215** | 10 (8 volatile + 1 envelope `ui_ns` + 1 `mp_loopback` uid) | 2 (envelope payload + uid token) |
| rep2 → author runs2 | 215 | **215/215** | 11 (8 volatile + 2 envelope + 1 uid) | 3 (same classes) |
| rep2 → baseline rep1 (207) | 207 | **206/207** (+8 new_only) | 12 (8 volatile + 2 envelope + 2 `export_*` steps) | 4 (2 envelope + 2 export steps 36→37) |
| rep2 → rep1 | 215 | 213/215 | 11 | 3 |
| rep1 → author runs1 | 215 | 213/215 | 10 | 2 |

Every raw/normalized diff resolves to a declared class: the 8 declared-volatile
rows (pids/ASLR/runpaths/tween floats), envelope cells sampling another
whitelisted mode (tuple stores all payloads — tuple-identical holds in every
comparison), `mp_loopback`'s disclosed volatile `uid_c`/`s_conn<uid>` on the
`R88S` diagnostic line, and `export_*` line 11 `(37 steps)` vs baseline
`(36 steps)` = +1 for the landed `r88_surfaces.gd` in the export class scan
(author disclosed +4 vs the r87 33-step refs — consistent).

## §F — rep1 flake: `r88_surfaces_mp_spawner` same-port contention (measured, classified, non-recurring)

**Receipt** (`runs1/…/verdicts.json`, row `r88_surfaces_mp_spawner`, verdict
FAIL, exit 0): stderr carries the unpinned pair
`ERROR: Couldn't create an ENet host. at: _create
(modules/enet/enet_connection.cpp:319)` (arm line 176 = `create_server(41778)`)
and `ERROR: Supplied MultiplayerPeer must be connecting or connected.`
(scene_multiplayer.cpp:193). Printed payload:
`neg[c_children=1 srv_children=4 bound_hit=68] pos[added=SpawnableOne
c_got=SpawnableOne c_pos=33.0000,44.0000] sync[pos=111.0000,222.0000]` —
the negative-control field flipped `0→1` because **my client cross-connected
to a foreign `mp_spawner` server holding UDP 41778** and received *its*
registered `SpawnableOne` twin + synchronizer stream (the positive fields
accidentally matched the pin — same arm, same values). The row failed loudly:
signature mismatch AND unallowlisted ERRORs, either alone sufficient. All 7
meta rows still PASSed — **no cascade** (unlike the sigabrt class).

**Classification.** Pre-documented this round by two other seats: r88-boundary
§3.5 "same-port contamination" and r88-critic **F1 [BLOCKER]** (hardcoded
41777/41778 cross-connect under concurrent seats; measured 2/4 + 6/6 losers in
`conc_lb4`/`conc_sp3*`/`sp2_r*`, instrumented `R88C` receipts showing the same
`c_children=1` + same ERROR pair + `conn=2` on the winner). Host contention was
real: load ~13–14, an r88-simplifier battery (`runs-before`
18:29:43→18:33:18Z), an r88-critic battery (`full1` from 18:33:07Z) and a 3d
r92-verifier battery all overlapped. The foreign mp_spawner server is
attributable only to a *battery row or unrecorded probe* — file-mtime
forensics over every seat's `runs/` found no standalone mp_spawner launch in
the ~18:31:1xZ window, and battery rows leave no per-row files. The
attribution is therefore to the class, not a named process — bounded honestly.

**Non-recurrence**: rep2 on the identical frozen tree PASSed the row
(`neg_wait=300 bound_hit=300` — the deterministic bound path), and 3 fresh
focused arms (`arms/mp_spawner.v{1,2,3}.out`, all sha `4b622d55…`) are
byte-identical to the pin. The frozen bytes carry no defect here; the **port
design** carries the hazard (author's own residual-risk note: "MP legs are
one-process loopback on 127.0.0.1 … ports 41777/41778").

**Census echo**: rep1's sole meta tuple delta vs author runs1 is
`census.scan_clause_census.ERROR:_per_line_lines` **100 vs 98 = +2** — exactly
the contamination's own two ERROR lines. Explained to the line; the meta row
itself still PASSed.

## Disclosures / residual risks

- **R1 — the verified artifact is the frozen tree**, not live HEAD (`f9e8a5b`
  = work commit + report/evidence custody; `corpus/fixtures/` diff is empty
  between them).
- **R2 — rep1 is not green**; only rep2 is. The dispatch's expectation
  (215/215 PASS) is met by rep2; rep1 records the contention instance. This is
  the same "canonical quiet condition" criterion r88-baseline applied.
- **R3 — the contention hazard is intrinsic to the landed pins** (hardcoded
  ports), documented as critic F1 BLOCKER *before* my run; the mp_loopback row
  would equally flake under a concurrent 41777 holder. Whether to port-
  randomize is the adjudicator's/author's call — out of verifier scope.
- **R4 — envelope cells** sampled whitelisted alternates across my reps
  (`ui_ns` mode[1], `press_phys` mode[1]); all tuple-identical, no
  out-of-whitelist payload observed.
- **R5 — `crash_spontaneous_sigabrt` did NOT flake** in either of my reps
  (PASS, `exit=-6`, full backtrace) — the documented flake did not appear.
- **R6 — census counts are run-dependent** (`ERROR:_per_line_lines` 98 clean /
  100 with the +2 contamination); the row's own discriminations don't gate on
  the count, so this is data drift, not verdict drift.
- **R7 — footprint**: `corpus/live/r88-verifier/tree/` is 1.6 GB untracked
  scratch (frozen `3c47eee`), prunable.

## Verdict

**VERIFIED with one recorded reservation.** Every author claim reproduces on
the frozen `3c47eee` tree: 215/215 PASS (rep2, rc=0, stderr 0 B), 215/215
tuple byte-identity vs the author's runs1 receipt, prior-207 identity
confirmed against the frozen baseline (206/207, sole diff = the disclosed
census delta), all 8 new rows present and pinned, both focused checks exact
(loopback uniq=1 pin with real uid churn; sprite_phys exactly 1 whitelisted
ERROR), gates true, zero stray processes, zero tree writes.

Reservation: rep1's `r88_surfaces_mp_spawner` FAIL is a measured instance of
the round's documented same-port MP contention hazard (boundary §3.5 / critic
F1 BLOCKER) — an environment interaction, loudly caught by the pin, not a
defect of the committed bytes, and non-recurring across rep2 + 3 fresh arms.
It is recorded, not excused: under concurrent seats this row class can flake,
and the critic's F1 notes a narrow silent-PASS window exists in the pin shape.
That design question belongs to the author/adjudicator lane.

Files (all untracked under `corpus/live/r88-verifier/` + this report):
`tree/` (frozen `3c47eee`), `runs1/`, `runs2/`,
`godot-battery-rep{1,2}.{stdout,stderr}`, `arms/` (10 focused-launch
receipts), `armx/` (arm scratch), `env.txt`,
`freeze/{git-ls-tree-3c47eee,tree-files,tree-files-post,fileset-diff,
godot-tuples-rep1,godot-tuples-rep2,compare-rep1-vs-author,compare-rep2,
receipt-shas}.txt`, `{compare,tuples,r88_compare,rowtable}.py` (verbatim
copies from r88-baseline).
