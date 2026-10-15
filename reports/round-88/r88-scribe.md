# r88 scribe — custody + consistency audit (round 88)

Seat `SCRIBE` (LEAF) | lane `r88-scribe` | round 88 | host **devin**.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`f9e8a5b`**
(work `3c47eee` + report `f9e8a5b`; baseline `aba4d7a`; boundary `d3e16fb`;
pre-round `d15c54d`).

**No git mutation, no commit, no product-code edit, no runtime invocation.**
The only write is this report (`reports/round-88/r88-scribe.md`, new, untracked).
Every command below is read-only verification (`sha256sum -c`, `md5sum`, `grep`,
`find`/`ls`, `git show/status/ls-files/check-ignore`, and re-runs of the existing
read-only comparators `corpus/live/r87-baseline/compare.py` and
`corpus/live/r88-scout/analyze_r88.py`; both were checked for write calls —
none). No battery was re-executed; no claim here upgrades an unobserved claim.

**Scope.** Custody (1), dangling-path sweep (2), claim arithmetic (3), verbatim
conflict log (4), untracked census (5), LOG/SCORECARD state (6) — as dispatched.

---

## 1. Custody — `sha256sum -c` and receipt verification

### 1.1 Boundary lane — `corpus/live/r88-boundary/manifest.sha256`

`sha256sum -c corpus/live/r88-boundary/manifest.sha256` → **642/642 OK, rc=0**.
Manifest composition (642 entries): 6 `proj/` files (`b88_{mp,light,audio,vis,sprite}.gd`
+ `project.godot`), `run_boundary.py`, `analyze_boundary.py`,
`__pycache__/run_boundary.cpython-314.pyc`, `RECEIPTS.md`,
`reports/round-88/r88-boundary.md`, and **631 files under `runs/`**
(166 `.out`, 163 `.err`, 163 `.rc`, 138 `.wall`, 1 `analysis.txt`).
The report's own manifest entry `3193f3ea…c2e1` equals the current
`reports/round-88/r88-boundary.md` sha256 (re-checked directly: same digest).

Receipt integrity spot-verified against claims: rc vector 157×`0` + 6×`-9`
(the only non-zero runs are `b88_light.hang_min` ×3 and
`verbatim.light_props_hang` ×3, wall `25.001` s); uid-normalized MP uniq=1
recomputed with marker-anchored normalization (`b88_mp.mp_lb` 6→1,
`verbatim.mp_loopback` 6→1, `mp_names` 3→1, `mp_cycles` 3→1); uid tail
`below_1e5=8+9+4=21`, `below_1e6=81+96+97=274`, min `3621` (rep0), max
`2147481226` (rep2); same-port stress losers `rc=[20,0]`, `frames=600 wait=600`
(rep0/rep2), winner `rc=[0,0] frames=4 wait=1` (rep1).

**Manifest prose note (not a custody failure).** The report §7 says the manifest
covers "163 receipt sidecars"; the manifest actually covers 631 files under
`runs/`. 163 is exactly the `.err`/`.rc` sidecar class; the count in prose
undercounts the receipt tree. All 642 entries verify.

### 1.2 Scout lane — `corpus/live/r88-scout/MANIFEST.sha256`

`cd corpus/live/r88-scout && sha256sum -c MANIFEST.sha256` → **269/269 OK, rc=0**
(manifest excludes itself; 270 files on disk incl. `MANIFEST.sha256`).
Manifest composition: 262 `runs/` files + 4 `proj/` + 3 runner/analyzer scripts.
All sha prefixes quoted in the scout report verify from the manifest
(`r88_probe.gd 3584d229…`, `r88_probe_fix.gd d14ae0ad…`,
`r88_edge.gd 1fa389ac…`, `run_arms.sh fd6fac04…`, `run_edge.sh 4bcf4164…`,
`analyze_r88.py 69651dd4…`). Census reproduction verified: 16/16
`runs/disc/*.out` are 6463 B each with one md5, and
`runs/repro/eq_form.out` is sha256/md5-identical to `runs/disc/geo_ops.out`
(`78670882d625fc5c…` / `4498e228a550066b0a2373e63d4b5ef0`).

### 1.3 Author lane — no manifest; receipts measured directly

`corpus/live/r88-author/` has **no `manifest.sha256`/`RECEIPTS.md`**; custody is
the commit `f9e8a5b` (569 tracked files) plus measured digests:

- `corpus/fixtures/r88_surfaces.gd` = `78370a04…` (422 lines) and
  `corpus/fixtures/r88_spawnable.tscn` = `89b9ddbe…` (4 lines, 89 B) — both match
  the report's prefixes; the two `corpus/live/r88-author/proj/` copies are
  byte-identical to the fixtures.
- `arms/` = 64 files (32 `.out` + 32 `.err`); **PASS-payload uniq=1 across 4 reps
  for all 8 arms**; raw `.out` uniq=4 only for `mp_loopback` (uid confined to the
  `R88S` diagnostic line); stderr empty except `sprite_phys` (4 × 260 B
  deterministic ERROR+backtrace block).
- `runs1/…/verdicts.json` sha `f06fadfa…9aaf5`, **215/215 PASS**;
  `runs2/…/verdicts.json` sha `43b1a769…188f2`, **215/215 PASS**.
- Gate evidence present in both runs: `r88_expected_errors_all_matched=true`,
  `r87_expected_errors_all_matched=true`, `phys2d_expected_errors_all_matched=true`,
  census `dead_entry_count=0`; census entry `r88_surfaces_sprite_phys`
  `matched_lines=1`, `bare_classification_rejects=true`,
  `allowlisted_classification_passes=true`.

### 1.4 Baseline lane — no manifest; receipt shas measured vs claims

- rep1 `91b3708d…80e7` ✓, rep2 `c400cf2f…e076b` ✓, rep3 `3d1bfb40…f03c9` ✓;
  `freeze/godot-tuples-rep{1,2,3}.txt` = `1dbf9dea…`, `c5f374d9…`, `f0e29f45…` ✓;
  `freeze/row-names.txt` = 207 rows ✓.
- Frozen harness `69512316…1bf` equals `git show d15c54d:corpus/fixtures/run_battery.py` ✓.
- Frozen tree identity: `freeze/{tree-files,git-ls-files,tree-files-post}.z`
  each **92 691 NUL-terminated entries**; `find …/tree -type l | wc -l` = **68** ✓;
  `du -sh` = 1.6 G ✓.

---

## 2. Dangling-path sweep — `reports/round-88/*.md`

Extracted every `corpus/…` / `reports/…` token (including brace/glob forms) from
the four round-88 reports and resolved each against the repo. **All repo-relative
references resolve**; brace forms (`corpus/fixtures/r88_{surfaces.gd,spawnable.tscn}`,
`proj/b88_{mp,light,audio,vis,sprite}.gd`, `runs/*.rep*.{out,err,rc,wall}`) expand
to existing files. Relative references (`runs/analysis.txt`, `freeze/…`, `arms/`,
`proj/…`, `run-reps.sh`, `tuples.py`, `compare.py`, `r88_compare.py`, `env.txt`,
`rep-timing.txt`) resolve under their lane dirs.

**Only non-resolving reference:** scout §0's `/tmp/r88-argtest` probe
(`argprobe.gd`) — a `/tmp` scratch artifact, since removed; it is outside the
repo and outside the scout manifest by construction (the scout's own protocol
text is the reproduction recipe). Not a custody failure; recorded as
out-of-custody scratch.

---

## 3. Claim arithmetic (measured)

| claim | source | measured | verdict |
|---|---|---|---|
| `run_battery.py` insertion-only +42/−0 | author §"run_battery.py changes" | `git show 3c47eee --numstat` → `42 0`; commit = 468 insertions, 0 deletions | **CONFIRMED** |
| 207 → 215 | author §"Full battery" | AST `CASES` = **208** (200+8) + 7 meta = **215**; 8 `r88_surfaces_*` rows inserted immediately before `crash_spontaneous_sigabrt` (index 204) | **CONFIRMED** |
| `expected_errors` +1 (exact shape) | author §2 | run_battery.py whitelist entry present; census shape=`exact`, matched_lines=1 | **CONFIRMED** |
| floor gate `r88_expected_errors_all_matched` added | author §3 | present at `run_battery.py:2417`; `true` in runs1/runs2 | **CONFIRMED** |
| prior-207 identity, `tuple_mismatches=1 (seeded=0, meta=1)` | author §"Full battery" | re-ran cited comparator: runs1 vs r87-verifier2 → `common=207 new_only=8 old_only=0 tuple_mismatches=1 (seeded=0 meta=1)` = `probe_error_clause_surface`; runs2 vs r87-critic2 and r87-fold-check → identical result | **CONFIRMED** |
| runs1 ↔ runs2, 0 mismatches on 215 | author §"Full battery" | `common=215 … tuple_mismatches=0`; 2 normalized diffs (envelope payload text + `mp_loopback` raw-uid diagnostic line) | **CONFIRMED** |
| 8 arms × 4 reps, uniq=1 PASS payload | author §"Fresh-arm evidence" | measured: all 8 uniq=1; battery 2/2 PASS per row | **CONFIRMED** |
| `sprite_phys` = 1 deterministic ERROR block | author §2/§"Host notes" | stderr 4×260 B, identical; row `expected_errors` matches | **CONFIRMED** |
| export progress-log `(37) vs (33) — +4` | author §"Full battery" | receipts: r87-verifier2/critic2/fold-check all `(36 steps)`; runs1/runs2 `(37 steps)`; delta **+1**. `(33 steps)` appears only in `r87-verifier/freeze/compare-*.txt` text inside the frozen tree copy, in no cited verdict receipt | **DISCREPANCY** (§5.1) |
| `spawn()` refusal "empirically verified" | author §"`spawn()` correction" | no receipt in `corpus/live/r88-author/**` carries the quoted ERROR text (grep over all receipts: only the fixture's own source comment mentions `spawn_function`); the pinned arm exercises the `add_child` auto-track path only | **CLAIM WITHOUT RECEIPT** (§5.2) |
| scout census md5 `4498e228550066b0a2373e63d4b5ef0` | scout §0/§F1 | actual md5 `4498e228a550066b0a2373e63d4b5ef0` (32 hex; report string is 31) over 16/16 disc outs + repro | **TYPO** (§5.4) |
| scout file counts: arms 51 / fix 12 / edge 28 | scout §1/§10 | actual: arms **153** (51 per sidecar class), fix **9**, edge **63** | **DISCREPANCY** (§5.4) |
| boundary "163 receipt sidecars" | boundary §7 | actual manifest = 631 files under `runs/` (+11 others) | **DISCREPANCY** (§1.1) |
| author tscn "(5 lines)" | author §"Landed files" | actual 4 lines / 89 B (no trailing newline) | **TYPO** (§5.5) |

Boundary claim set also re-derived from receipts: audio flip band
(`b88_audio.timeline` first-false f9×5 / f10×1; stress f6,f7,f7,f8,f11,f11,f13,f13;
`f19=false` 14/14; `sync_after_play playing=true` 14/14), fall bimodality
(Case A 66.5952/107.9190 ×6; Case B 74.5675/118.4614 ×6; `stress_fall` 8/8 B;
`seq_fall` B,A,B), sprite OOB ERROR counts, hang rc/wall — **all match** the
boundary report.

---

## 4. Conflicts — logged verbatim for the canonical judge

### 4.1 Audio `playing=false`: scout early-window claim vs boundary falsification vs author pin — **CONSISTENT (sample-frame analysis)**

- Scout §3.15: *"after `play()` and 20 frames — **`playing=false`**, `pos=0.000`,
  peaks `[−200.00,−200.00,−200.00,−200.00]` dB near; identical far. Under the
  Dummy driver no buffer advances and `playing` clears; … Only negative pins are
  authorable headless (e.g. `playing==false` after `play()` under Dummy)."*
- Boundary claim 4a: *"audio: `playing=false` after `play()` under Dummy —
  **FALSIFIED as a blanket statement**; the 20-frame sample CONFIRMED —
  `sync_after_play playing=true` in **14/14**; `playing` flips to false between f6
  and f13 (battery f9×5/f10×1; concurrent f6..f13); `f19=false` in **14/14**."*
- Boundary directive 3: *"**Keep the scout's 20-frame audio sample point** for
  `playing=false`; never pin the flip frame (f6..f13) or the post-`play()` value
  (true)."*
- Author fixture `_arm_audio_pos`: `p.play()` then `for i in 20: await process_frame`
  (peaks every 5th), then reads `p.playing` → pin `playing=false pos=0.000 …`.

**Frame check:** the boundary's timeline labels f0..f19 over `for i in 20: await
process_frame`; its `f19` is the 20th await. The author reads `p.playing` after
exactly 20 awaits — the same sample point. Boundary receipts: `f19=false` in
14/14. The author's `playing=false` pin is therefore **at the boundary-validated
sample point, not in the falsified early window**; the two seats are consistent
(the scout's blanket framing is the falsified part). Author receipts: 4/4 arms
`playing=false`; runs1/runs2 PASS.

### 4.2 Structurally-impossible positives vs negative-only choice — **CONSISTENT**

- Scout §7.7: *"Headless-null surfaces: Dummy audio (`playing=false`, peaks −200 dB)
  and no screen (`is_on_screen()==false` always, enabler never fires). Authorable
  only as *negative* pins; any positive audio-position/visibility row is
  unfalsifiable on this host."*
- Scout directive 5: *"**Never author positive `audio_pos`/`vis_not` rows headless**
  — only negative pins (`playing=false`, `events=[]`) are falsifiable here (§7.7)."*
- Scout §8: *"**`vis_not`/`audio_pos` positive arms are structurally impossible
  headless** — not a coverage gap, a host constraint; a `--display-server`/Xvfb
  host could open them."*
- Boundary directive 4: *"**vis_not: negative pins only** (`is_on_screen()==false`,
  `events==[]`, `enabler_proc==false`); no positive is reachable headless on this
  host."*
- Author report §"Host notes": *"`audio_pos`/`vis_not` are negative-only **by host
  constraint** (Dummy driver, no screen headless) — positive rows are structurally
  impossible here, never authored (directive 5)."*

The author's negative-only choice matches both the scout directive and the
boundary refinement; no conflict. Both rows PASS in runs1/runs2.

### 4.3 Fall-distance pins vs boundary directive 1 — **OPEN (author work predates the boundary commit)**

- Boundary directive 1: *"**Do not pin the fall-distance values as written.**
  `74.5675`, `118.4614`, `124.5675`, `482.2250` are Case-B realizations; the same
  code yields `66.5952`, `107.9190`, `116.5952`, `466.6694` in Case A, and the mode
  flips run-to-run under load."*
- Author pinned exactly those Case-B values: `r88_surfaces_sprite_phys` payload
  `pos=…,74.5675` (4 bodies) and `r88_surfaces_light_props` payload
  `body_y=118.4614`, with **no v≠0 sync recipe** in the fixture (plain
  `for i in 30/40: await physics_frame` after body creation), and the author report
  does not mention the startup race.

Measured receipts: author arms ×4 = `74.5675` / `118.4614`; battery runs1+runs2
PASS (Case B in both). Boundary receipts for the same computation: `b88_sprite.phys`
×6 = `66.5952` and `b88_light.fixed` ×6 = `107.9190` (Case A), `verbatim.sprite_phys`
×6 = `74.5675` and `verbatim.light_props_fix` ×6 = `118.4614` (Case B),
`stress_fall` 8/8 B, `seq_fall` B,A,B. **Both payloads are live on this host for
the same code.**

Chronology (local, UTC−3): author fixture mtime 15:14:01, `run_battery.py` 15:15:14,
runs1 verdicts 15:19:06, runs2 verdicts 15:22:46, arms receipts collected 15:23:53,
author report 15:24:29; **boundary commit `d3e16fb` 15:19:37** (report written
~15:18–15:19), baseline `aba4d7a` 15:21:28, author work/report commits 15:25:29.
The author's rows and fixture therefore predate the boundary directive; this is a
**folding gap**, not a disagreement — the canonical judge decides whether the two
pins stand (they are stable in every author receipt) or must be re-pinned
(sync recipe / masked range) per directive 1.

### 4.4 `ray_through_occluder=true` — vacuous pin kept — **OPEN**

- Boundary claim 3c: *"`ray_through_occluder=true` pin — **FALSIFIED as evidence**
  (the pin itself is true but **vacuous**)"* — the scout's ray is vertical at
  `x=-50`, occluder polygon global `x∈[0,10]`; the ray never crosses it.
- Boundary directive 5: *"**`light_props`:** keep the `height` fix and the property
  readbacks; replace the vertical x=-50 ray with a ray that actually crosses the
  polygon (e.g. y=-35, x −50→50) if the ray is meant to be evidence; keep
  `occ_is_co=false` …"*
- Scout directive 6 (followed by the author): *"…the repaired leg pins
  occluder-noncollision (`occ_is_co=false`, `ray_through_occluder=true`, `body_y`
  falls through)."*
- Author fixture `_arm_light_props` keeps
  `PhysicsRayQueryParameters2D.create(Vector2(-50,-80), Vector2(-50,60))` and pins
  `ray_through_occluder=true`; the author report lists it as evidence without
  noting the vacuity.

The pin is true in every author receipt (×4 + ×2 battery), but by the boundary's
measurement it is non-discriminating; `occ_is_co=false` remains valid. The author
report's directive source (scout §9) predates the boundary's supersession — logged
for the judge.

### 4.5 Export progress-log arithmetic — **DISCREPANCY (measured +1, not +4)**

- Author report: *"export progress-log `Registering global classes (37 steps)` vs
  `(33)` — +4 = r87's 3 landed `.gd` + `r88_surfaces.gd` scanned at export;
  signature/verdict unchanged (same attributable class r87 recorded)."*
- Receipts: `export_preset_missing` / `export_readiness` show `(37 steps)` in
  runs1+runs2; `(36 steps)` in r87-verifier2, r87-critic2 **and** r87-fold-check
  (all three cited refs). Measured delta **+1**. The `(33 steps)` string occurs
  only inside `r87-verifier/freeze/compare-*.txt` (frozen-tree copy text), not in
  any cited verdict receipt.

---

## 5. Findings (non-blocking; for the record)

1. **Export-log arithmetic** — §4.5; the attribution class is unchanged, only the
   delta/counts are wrong.
2. **`spawn()` refusal claim has no receipt.** The quoted engine ERROR
   (`Custom spawn requires the 'spawn_function' property … multiplayer_spawner.cpp:325`)
   appears in no receipt file in any r88 lane (grep); only the fixture comment
   mentions `spawn_function`. The author's *pinned* spawner rows do not depend on
   it (they pin the `add_child` auto-track positive + silent non-replication
   negative), but the "empirically verified" wording is not carried by stored
   evidence. Reported, not upgraded.
3. **MP port ownership residual hazard.** The fixture hardcodes ENet ports
   41777/41778. The boundary's same-port contamination mode is *loud* in the
   author's pin (loser would produce `rc=[20,0]` and truncated
   `order`/`limb_s=[]`, failing the signature) — boundary directive 7's "assert
   it fails loudly" is satisfied — but the rows are not serialized against other
   lanes; a same-port collision with a foreign process would surface as a row
   FAIL, not silent pass.
4. **Scout prose counts/md5.** `runs/arms/` 51 → actual 153 files (51 `.out`);
   `runs/fix/` 12 → actual 9; `runs/edge/` 28 → actual 63; census md5 string is
   31 hex chars (`4498e228550066b0a2373e63d4b5ef0`) vs actual 32
   (`4498e228a550066b0a2373e63d4b5ef0`). The manifest covers all actual files and
   verifies 269/269; `/tmp/r88-argtest` is gone (scratch).
5. **Author prose nits.** tscn described as "5 lines" (actual 4 / 89 B); arm wall
   times ("0.5–1.4 s/arm; `mp_spawner` ~2.6 s") have no `.wall` sidecars in the
   author lane (battery verdicts carry no elapsed field) — unverifiable from
   stored receipts; "client received … in ~4 frames" while the author's own
   receipt shows `pos_wait=1` (diagnostic, not pinned).
6. **Boundary prose count.** §7 "163 receipt sidecars" vs 631 manifest-covered
   `runs/` files (§1.1). All 642 entries verify.
7. **Author report HEAD statement is stale at read time (expected).** The report
   says "HEAD `d15c54d` … nothing committed"; the work and report are now commits
   `3c47eee` + `f9e8a5b`. No content drift: the committed fixture bytes equal the
   measured shas; the working tree is clean (`git status` shows only untracked
   pre-existing `corpus/live/*` churn + this report).

---

## 6. Untracked census — round-88 dirs (HEAD `f9e8a5b`)

**Snapshot note.** The census below was taken in-session at ≈15:26–15:28 local
(UTC−3). During the audit the sibling lanes **`r88-critic` (7 untracked
non-ignored files + ignored `runs/`), `r88-reviewer` (27 + ignored `runs/`),
`r88-simplifier` (324), `r88-verifier` (257 + ignored `tree/`, 1.6 G, same
`live/**/*tree*/` rule)** landed at 15:27:31–15:30:20; they postdate the snapshot,
carry no manifests/reports at observation time, and are outside this audit's
scope. The table and the "no other artifact" statement are scoped to the
snapshot.

| path | state | notes |
|---|---|---|
| `corpus/live/r88-author/` | **569 tracked** (`f9e8a5b`) | arms 64 + runs1/runs2 503 + proj 2; no untracked/ignored leftovers |
| `corpus/live/r88-baseline/` | **756 tracked** (`aba4d7a`) | runs1–3, freeze, scripts, receipts; `tree/` **ignored** |
| `corpus/live/r88-baseline/tree/` | **ignored** (`corpus/.gitignore:14 live/**/*tree*/`) | 1.6 G, 92 691 entries + 68 symlinks; **deliberate** local-only exclusion (baseline C8: prunable, reproducible via `git archive d15c54d`) |
| `corpus/live/r88-boundary/` | **11 tracked** (`d3e16fb`) | manifest + 6 proj + 2 scripts + RECEIPTS + report; `runs/` ignored |
| `corpus/live/r88-boundary/runs/` | **ignored** (`corpus/live/.gitignore:1 runs/`) | 631 receipt files, covered by the tracked manifest (642/642 OK) |
| `corpus/live/r88-scout/` | **untracked** (8 non-ignored files) | `MANIFEST.sha256`, `analyze_r88.py`, 4 `proj/` files, `run_arms.sh`, `run_edge.sh`; `runs/` (262 files) ignored by `corpus/live/.gitignore:1`; report tracked separately (`fad0b1e`) |
| `reports/round-88/` | 4 reports tracked | `r88-{scout,author,baseline,boundary}.md`; **this report** `r88-scribe.md` new/untracked |
| `corpus/fixtures/__pycache__/love_battery.cpython-314.pyc` | untracked | pre-existing, not round-88 |

No round-88 artifact outside the above is untracked or ignored; nothing was
pruned or moved by this seat.

---

## 7. LOG.md / SCORECARD.md current state

- **LOG.md** — r87 section present and closed: `## round 87 — input event/action
  lattice (ADMIT-corr)` (line 1083), ending *"Seats: … ADMIT-corr. Commits
  ebcf2bb + 7ef247c + this."* Last commit touching `LOG.md` = `d15c54d`; file clean
  at HEAD. **No r88 section yet** (round in flight).
- **SCORECARD.md** — last verdict section is **Round 87** (2026-10-15,
  ADMIT-corr: 25 new CASES rows 182→207, just_* law, api_press envelope folded,
  floor gate widened). **No r88 verdict yet.** Last commit touching `SCORECARD.md`
  = `d15c54d`; file clean at HEAD.
- Neither file was read-modified-written by this seat.

---

## 8. Out of scope / not done

- No product/fixture edit, no judge action, no commit/push/publish/deploy, no
  Godot/runtime launch, no sibling-seat dispatch, no battery re-execution.
- Not verifiable retrospectively: boundary "0 stray children", author wall-time
  claims (no `.wall` sidecars), host-load history (quoted from the baseline report
  only), and any claim whose evidence lives outside the stored receipts.
- The canonical Rust runtime remains the sole judge; this report does not
  adjudicate §4.3/§4.4 — it records both sides verbatim with measured receipts.

---

## 9. Artifact paths

- **This report:** `reports/round-88/r88-scribe.md` (new, untracked; no commit).
- Custody evidence: `corpus/live/r88-boundary/manifest.sha256` (642/642 OK),
  `corpus/live/r88-scout/MANIFEST.sha256` (269/269 OK),
  `corpus/live/r88-author/{arms,runs1,runs2,proj}`,
  `corpus/live/r88-baseline/{runs1,runs2,runs3,freeze,run-reps.sh}`.
- Comparator re-run (read-only): `corpus/live/r87-baseline/compare.py godot …`
  vs `corpus/live/r87-verifier2/runs1/20261015T174757647842Z/verdicts.json`,
  `corpus/live/r87-critic2/runs1/20261015T175608856719Z/verdicts.json`,
  `corpus/live/r87-fold-check/runs1/20261015T174312754775Z/verdicts.json`.
- Scout analyzer re-run (read-only): `corpus/live/r88-scout/analyze_r88.py`
  (stdout captured to `/tmp/scribe-analyze-r88.txt`; `UNSTABLE_COUNT=1`).

Reproduce this audit: `sha256sum -c corpus/live/r88-boundary/manifest.sha256`;
`(cd corpus/live/r88-scout && sha256sum -c MANIFEST.sha256)`;
`python3 corpus/live/r87-baseline/compare.py godot corpus/live/r88-author/runs1/20261015T181519396144Z/verdicts.json r87verifier2=corpus/live/r87-verifier2/runs1/20261015T174757647842Z/verdicts.json`;
`git status --porcelain --ignored corpus/live/r88-*`.
