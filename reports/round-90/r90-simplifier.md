# game-dev-2d round 90 — simplifier (r90-simplifier): no fold survives the bar — the r90 rb2d landing is audited clean (12 arms ↔ 12 rows, zero dead stores, zero dead keys, zero unpinned emissions, both folded boundary corrections re-verified on the landed bytes); the author's "30 tps" receipt mislabel is independently reproduced (corroborating the committed reviewer F2), and one provably-inert filter term is dispositioned keep

Seat `SIMPLIFIER` (LEAF) | lane `r90` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
Work commit **`ee20575`** (r90 author: `rb_lattice.gd` + `rb_watch.gd` +
`run_battery.py` + `reports/round-90/r90-author.md`, 247 rows). HEAD moved
mid-session under sibling wave-B seats (`ee20575` → **`03d0239`** r90 reviewer
at 19:18:15 local). **No tracked file written, no commit, no git mutation by
this seat.** Writes are this report and `corpus/live/r90-simplifier/**` only.
Batteries ran sequentially. Disclosed: the direct CLI-flag reps (19:15:36
local) and the mode-probe sweep (19:16:33) ran while the control battery was
live (19:12:25–19:17:34) — no port-bearing arm is involved in the r90 block.

**`lsp` disclosure.** No `lsp` device is exposed in this dispatch, and no
GDScript/Python language server is installed on this host
(`gdlint`/`gdformat`/`gdscript-lsp` absent from PATH; `gdtoolkit` absent from
pip — re-checked this session). `references`/`definition`/rename were therefore
**unavailable**; no cold result is recorded as absence. Caller/consumer proofs
rest on (a) complete textual enumeration of every occurrence of the suspect
state, (b) a mutator-aware write-only-store scan and a dict-key scan over both
new probes, (c) a pin↔emission token census over every r90 row, and (d)
fresh-process byte equality against the unmodified control and both canonical
green runs.

**Frozen probeParent.** Exactly **one** `ufo-labrat` was dispatched (bounded,
read-only, three falsifiable hypotheses: CLI-flag existence, receipt byte
identity, real-30-tps pairing-field invariance). The probe seat returned **no
receipts**: in this dispatch it exposed only read-only file tools — no shell,
so no `godot` launch, `diff`, `sha256sum` or receipt write was possible. Its
static read of `f_pair_30tps.rep1.out` independently flagged the 60-tps shape
("consistent with H2, unverified byte-identity"). Every empirical number below
is this seat's own fresh-process receipt, and each one is byte-level, so the
proof does not depend on the probe. No other descendant was spawned.

---

## 1. Method and proof artefacts

`corpus/live/r90-simplifier/` (`MANIFEST.sha256`, 42 files, sha
`8a6d091d…`; run/scratch dirs excluded):

| artefact | content |
|---|---|
| `committed-fixtures/` | byte-exact `git show ee20575:` snapshot of `run_battery.py` (`76c0b1f5…`), `rb_lattice.gd` (`10da2291…`), `rb_watch.gd` (`e349faa0…`) — every audit below was re-run against this snapshot (the working tree carries a foreign in-flight edit, §8) |
| `runs-control/20261015T221225674936Z/` | full battery on the committed tree: **247 rows**, r90 12/12 PASS; census + gate values (§4) |
| `committed-landing_integrity.txt` | per-row: PASS line **byte-identical** to the CASES signature, emitted token set == pinned token set, 0 unpinned emissions → `ALL_ROWS_INTEGRITY_OK=True` |
| `committed-key_and_pin_census.txt` | pin↔emission token census (12/12 rows) + dict-key scan (0 dead keys in either probe) |
| `deadstore-scan.txt` | mutator-aware write-only-store scan over every `var`/`const` in both probes → **no write-only store** |
| `committed-audit.txt` | arm↔row bijection (12/12, no orphan, no duplicate), helper call-site census, CLI-knob usage, allowlist/gate inventory |
| `author-claim-recheck.txt` | the landing's own stability claims re-derived from its 12×6 receipts with the production classifier (`verify_arms.py` reused unmodified) |
| `committed-classify_modeprobes.txt` | production classifier over **24 fresh tps30 + 24 fresh dummy** receipts on the landed probe (§5) |
| `committed-field_diff_modeprobes.txt` | field-level pin diff for every mode cell, with pairing-field attribution (§5, §6) |
| `fl_30flag.rep{1,2}.{out,err,rc}`, `fl_60plain.rep1.*` | CLI-flag byte-identity receipts (§6) |
| `filter-audit.txt` | engine-side unique-match census of the `_arm_props` method-filter terms (§3 SP1) |
| `control-vs-green.txt`, `r90-identity.txt` | `compare.py godot` (r79-baseline tool, reused unmodified) + explicit r90-row identity vs both canonical green runs |
| `workcommit-shas.txt` | HEAD + the four landing-file shas at session start |

## 2. Verdict and findings (ranked)

**Verdict: PASS — no fold survives the bar.** The r90 landing carries **zero
provably-removable weight**: no unused arm, no dead store, no dead dict key, no
dead allowlist entry, no dead gate key, no dead CLI knob, no unreachable
row-facing path, and **no unpinned emission** in any of the 12 rows. Both
folded boundary corrections are independently re-verified on the landed bytes
(real 30 tps → 12/12 rows FAIL; real Dummy → 12/12 rows FAIL). 0 blockers.

| # | finding | severity | evidence |
|---|---|---|---|
| F1 | **The author's "30 tps" receipt is a 60-tps run** (`r90-author.md` §"30-TPS deliberately not pinned" + `f_pair_30tps.rep{1,2}.out`): `--physics-ticks-per-second` **does not exist** on this build (absent from `godot --help`; passing it yields **byte-identical** output, 0 B stderr) and the receipt is **byte-identical to a plain 60-tps/60-frame run** (sha `a74e8295…`, 3/3 receipts). The drawn comparison (`ncb=60` vs pin `ncb=120`) is a **frames** comparison, not a tps comparison. **Independently reproduced; not new** — the committed reviewer report `reports/round-90/r90-reviewer.md` F2 (medium-low) already records it, with the same suggested action. My added precision: at a *real* 30 tps the pin's pairing fields (`ncb`/`pf_delta`/`tick_dh`/`cb0_rel`/`obs0_rel`) are **unchanged for 11/12 rows**, so the row's rate evidence is `tps=` (the project-setting echo) plus the pinned motion values — **not** `ncb`/`pf_delta` (contra `r90-author.md`'s "ncb/pf_delta are the effective-rate evidence") | medium-low (evidence label / mechanism narrative; no pin affected) | `fl_30flag.rep{1,2}.out` ≡ `fl_60plain.rep1.out` ≡ `corpus/live/r90-author/f_pair_30tps.rep1.out`; `committed-field_diff_modeprobes.txt` |
| F2 | **`_arm_props`'s `"constant"` method-filter term has zero unique matches on this build** (7 matches, all also matched by `force`/`torque`; the shipped `methods=[…]` list is **byte-identical** with the term removed). Dispositioned **keep**: it is the census's constant-force family clause (r89-SP5 future-coverage precedent), the fold buys 1 line and 0 battery bytes while staling the probe sha cited in two tracked files + three manifests | low (audited, kept) | `filter-audit.txt` (`TERM constant n=7 uniq=[]`, `IDENTICAL=true`) |
| F3 | **Landing integrity is exact**: each r90 PASS line is byte-identical to its CASES signature and every emitted field is pinned (no unfalsifiable emission; no pinned-but-unemitted field) | info | `committed-landing_integrity.txt` (`ALL_ROWS_INTEGRITY_OK=True`) |
| F4 | **Both folded boundary corrections hold on the landed bytes**: real 30-tps project boot → 12/12 rows FAIL (`tps: 60→30` first diff); real Dummy boot → 12/12 rows FAIL (`eng: PhysicsServer2D→PhysicsServer2DDummy` first diff); 2 fresh reps per cell | info (fold verification) | `committed-classify_modeprobes.txt`, `committed-field_diff_modeprobes.txt` |
| F5 | **Custody**: the r89-SP1 fold I verified as still-applicable at 19:11 was applied by the sibling `r89-fold` lane at 19:16 (out of this seat's scope; recorded only); a foreign in-flight working-tree edit appeared *after* my control battery's launch snapshot, which is byte-proven to hold the committed bytes (§8) | info | `workcommit-shas.txt`, `runs-control/*/scratch/geo2d_lattice.gd` = `9784716b…`/581 lines |

## 3. The fold question — candidates audited, nothing survives

Method: (a) mutator-aware **write-only-store** scan over every `var`/`const`
in `rb_lattice.gd`/`rb_watch.gd`; (b) **dict-key** scan (init/assign = write,
index/`.get` = read); (c) **arm↔row bijection** and **call-site census**;
(d) **pin↔emission token census** per row; (e) direct read of every statement
that writes node/engine state, asking "can this change any pinned byte?".

| # | candidate | verdict | proof / reason |
|---|---|---|---|
| SP1 | `_arm_props` method-filter term `or n2.contains("constant")` `:186` (−1 line) | **rejected (audited)** | Provably inert **today** (engine receipt: 0 unique matches; shipped list == trimmed list, `IDENTICAL=true`) — but it is the census's constant-force family clause and the fold stales the probe sha cited in `run_battery.py:480`, `r90-author.md:28` and the scout/author manifests for **zero** battery-byte gain (r89-SP5 future-coverage precedent). Net-negative trade, not a YAGNI deletion. |
| SP2 | `_arm_freezelock` f==1 write `bodies[3].linear_velocity = Vector2(0,-30)` `:661` (−1 line) | **rejected** | The lane is **not** a same-value duplicate: `bodies[3]` (`f_kin2`) has **no** setup velocity write (the setup block writes only `bodies[2]`), so this line is the lane's **sole** instrument for the scout's declared "velocity set *after one step*" case (`r90-scout.md` §3.9). Deleting it leaves the pin byte-identical but turns `f_kin2` into an unrotated-style duplicate of `f_kin` and unbacks a cited claim (r89-SP3 evidence-canary precedent). |
| SP3 | `_arm_comread` `d.rotation = PI / 2.0` `:225` (−1 line) | **rejected** | Same class: the rotation is the `rot_com` lane's independent variable; without it `rot_com=4.0000,0.0000` degenerates into a duplicate of `custom_com` and the "rotated body reads back unchanged" claim becomes false. |
| SP4 | `_arm_freezelock` `bodies[5].position.y = -40.0` / `bodies[6].position.y = -40.0` `:653–654` (−2) | **rejected** | Not provably inert: the spawn point changes the fall/impact dynamics (sleep timing inside the 120-frame window) even if the f120 readout may coincide; it is an experiment parameter, not dead weight. |
| SP5 | `rb_watch.gd`'s `if sink.is_valid():` guard `:8` (−1) | **rejected** | Defensive guard **and** verbatim-pinned (sha `e349faa0…` asserted in the scout manifest, `r90-author.md:29`, `run_battery.py:480`); all 12 `_watch` call sites pass a valid Callable, so it is unreachable *today* — exactly the r89-SP7 class (deleting a defensive default makes a future silent failure louder, not quieter). |
| SP6 | Defensive fallbacks: `_arm_fallback` `:162`, `_eng`'s `<nosuch>` `:71`, `_dh`'s `"short"` `:81`, `_pair`'s `ncb>0`/`tvals.size()>0` ternaries `:98–99`, `_pget`'s final `str(v)` `:67` | **rejected** | r89-SP7 precedent: each is the loud-failure shape of its helper (the Dummy-vacuity lesson is precisely why defaults must stay loud). `_pget`'s tail is unreachable for the 21+9+5 observed property types but is the function's generic contract. |
| SP7 | Hand-rolled pairing emission in `damp`/`impulse`/`impedge`/`lag` vs the `_pair` helper (duplicate boilerplate) | **rejected** | Not a deletion: those arms emit **per-lane** `ncb` strings (`default=60|rep0=60|…`) and lane-specific `cb0_rel` anchors, so `_pair` cannot reproduce their pinned bytes; deduplicating would be a probe-byte refactor with zero battery-byte gain (r88 duplicate-boilerplate precedent). |
| SP8 | Cross-arm duplicate values (`lag.a` ≡ `damp.rep0` f30 ≡ `write.wman` f30; `lag.b` ≡ `write.wman`; `lag.c` ≡ `gravity.g1` ≡ `damp.default`) | **rejected** | Deliberate cross-arm identity evidence: `lag` pins `dy = n·g·dt²` against the same lanes other rows pin absolutely; each row is arm-verified by its own PASS line (r89-SP8 precedent). |
| SP9 | Trimming derivable pin tokens (`nprops=88` vs the `props=[…]` list; `tick_dh=1:59` vs `pf_delta=60`; `tps=60` vs `ps_tps=60`; `exp=N=30` vs `acc=an=30`) | **rejected** | Each is a *different* measurement that can diverge: `props` list ≠ count source; `tick_dh` is the await↔step pairing histogram (a stall yields `1:57,2:1` while `pf_delta` stays 60); `tps`/`ps_tps` are two settings sources; `exp` carries its own N so the oracle cannot be confused with `--frames`. Trimming = removing pinned bytes (r87 over-long-signature precedent). |
| SP10 | Any r90 CASES row, allowlist entry or gate key | **rejected** | All 12 rows PASS 12/12 in my control run and are byte-identical to both canonical green runs; both allowlist entries are **live** (`matched_lines=1` / `1+2`, `dead_in_run=false`) and each row **bare-rejects 6/6** without them; the `r90_expected_errors_all_matched` floor is the only key covering the r90 prefix (non-redundant). |
| SP11 | `--frames=` knob (`:37–38`) | **rejected** | Live: `freezelock` (`--frames=120`) and `lag` (`--frames=30`) pass it; both pins depend on it. |

**Conclusion:** the r90 probes were written to the conventions the r89
simplifier already pruned; the landing has no write-only store, no dead key,
no unreachable row path, and every line that *could* be deleted byte-identically
turns out to be an evidence instrument (SP2–SP4, SP5) or a family/coverage
clause (SP1). The honest simplifier output for this landing is **no fold**.

## 4. Landing integrity — the narrow check, on the committed bytes

- **Control battery** (`corpus/fixtures/run_battery.py` at `ee20575` bytes):
  247 rows, verdict `FAIL` — `overlap`, `transition`, `negative_transition`
  (the documented pre-existing scene-readiness flakes) + the
  `probe_error_clause_surface` meta cascade. **r90: 12/12 PASS.**
- **Per-row byte identity**: every r90 PASS line is byte-identical to its CASES
  signature; emitted token count == pinned token count for all 12 rows
  (40/40, 14/14, 12/12, 9/9, 10/10, 54/54, 10/10, 8/8, 9/9, 9/9, 13/13, 17/17);
  **0 unpinned emissions, 0 pinned-but-unemitted fields**.
- **r90 row identity vs both canonical green runs** (`runs9/212551992799Z`,
  `runs12/220233737605Z`): `tuple_mismatches=0`, `output_diffs=0`, 12/12.
  Full-battery `compare.py`: `common=247 new_only=0 old_only=0`,
  `tuple_mismatches=4` (3 seeded flakes + the meta census payload), no r90 row
  in the output-diff list (diffs are the documented volatile classes:
  envelope modes, peer-id tokens, `frames=` jitter, `negative_route` frames).
- **Census / gates** (my run): `r90_expected_errors_all_matched=true`;
  `rows_with_expected_errors=57`; `census_allowlisted_reproduces_verdicts=true`;
  `dead_entry_count=2` — **both entries are `negative_transition`'s**
  (`matched_lines=0`, that row flaked); every r90 entry is
  `dead_in_run=false`. The canonical green run (`runs9`) reads
  `dead_entry_count=0` with all r89/r90/phys2d gates true, so the two dead
  entries are exactly the flake's, not the landing's.
  `census_bare_classifier_consistent=false` is the same flake cascade
  (documented by the author).
- **Allowlist liveness** (independent re-derivation of the author's claim):
  `comrefuse` entry matched ×1, `impedge` entries matched ×1 and ×2 (the
  `mass<=0` entry covers both the `mass=0` and `mass=-1` lanes); both rows
  `bare_classification_rejects=true` / `allowlisted_classification_passes=true`,
  6/6 reps.
- **Author stability claims re-derived** from the 12×6 receipts with the
  production classifier: 12/12 `out_uniq=1 err_uniq=1`, constant rc, signature
  hit 6/6, classified 6/6.
- **Mechanical census**: 12 rows ↔ 12 dispatched arms (no rowless arm, no
  armless row, no duplicate case name; 240 CASES tuples of which 12 are r90);
  all helpers have ≥1 call site (`_initialize` is the engine lifecycle entry);
  probe sha claims in `run_battery.py:480` and `r90-author.md:28–29` verify
  (`10da2291…` / `e349faa0…`, the latter byte-identical to the scout probe and
  to both scout project copies); `project.godot` untouched (`8de8b3af…`).

## 5. Folded boundary corrections re-verified (independent receipts)

Fresh scratch projects built from the **landed** probe bytes (`10da2291…`),
battery launch shape (`timeout -s KILL 25`, `--headless`, 2 reps/cell):

| cell | result |
|---|---|
| **real 30 tps** (`[physics] common/physics_ticks_per_second=30`, the boundary's route) | **12/12 rows FAIL ×2 reps**; first differing field = `tps: pin=60 got=30` in every row. Value evidence: `gravity f60 g1 482.2250→1868.1178`, `damp rep0 f30 126.5834→506.3334`, `write step 0.016667→0.033333`, `order cb0 st 0.016667→0.033333`, `lag d=dy 8.1667→32.6667`, `freezelock f_lock −128.0000→−156.0000` & `f_normal −7.6969→−7.7000`, `contacts cvel 16.3333→32.6667` |
| **real Dummy** (`2d/physics_engine="Dummy"`) | **12/12 rows FAIL ×2 reps**; first differing field = `eng: pin=PhysicsServer2D got=PhysicsServer2DDummy`; motion arms additionally show the silent-vacuity shape (`ncb=0`/`cb0_rel=−1`, `tld=−1.0000`, bodies frozen at spawn, `s_off/s_on y=−40.0000`, `count=−1`) — exactly what the precondition makes loud |

Both folds therefore hold on the committed bytes, and the *whole row set*
(not just the sampled arms) is protected — the pure rows (`props`, `comread`,
`comrefuse`) fail on `eng=`/`tps=` alone, which is the intended design.

## 6. F1 detail — the "30 tps" receipt (corroboration, with the row-level precision)

- `godot --help | grep -i tick` → **no match**; no physics-ticks option exists
  on `4.7.2.stable.arch_linux.ed1daf0bf`. A run with
  `--physics-ticks-per-second 30` (before *or* after `--`) is **byte-identical**
  to a plain run (sha `a74e8295…`, stderr 0 B, rc 0) **and byte-identical to
  `corpus/live/r90-author/f_pair_30tps.rep1.out`** → that receipt is a plain
  60-tps, 60-frame run. The `ncb=60` vs pin `ncb=120` comparison in
  `r90-author.md` is a **frames** difference (`--frames` was not passed),
  not a tps difference.
- At a **real** 30 tps the *pairing* fields are **identical to the pins** in
  11/12 rows (`freezelock` @30 tps/`--frames=120` emits
  `ncb=120 cb0_rel=1 obs0_rel=1 pf_delta=120 tick_dh=1:119` — byte-equal to the
  pin — while its values fail). Only `contacts` differs in a pairing field
  (`ncb 45→24`, because the sleep point moves). So the landing's tps
  qualification rests on `tps=` (the project-setting echo) and the pinned
  motion values; `r90-author.md`'s "`ncb`/`pf_delta` are the effective-rate
  evidence" is **wrong as stated** (they are step-count evidence). The
  *conclusion* the fold needs — no 60-tps pin can be satisfied by a real
  30-tps run — is true and is proven by the 24 receipts above.
- This is the **same finding** as the committed reviewer F2
  (`reports/round-90/r90-reviewer.md`, committed in `03d0239`), which also
  verified the claim the boundary way (V8). Two independent seats, same
  conclusion; the suggested action (replace the receipt/claim with a real
  30-tps project boot, or state that no CLI tps override exists) remains
  un-applied at HEAD `03d0239`. No pin, gate or row is affected.

## 7. Tradeoff and stop line

- **No patch is proposed**: the only provable byte-identical deletion (SP1)
  is net-negative (weakens the census family clause; stales a probe sha cited
  in two tracked files and three manifests for zero battery-byte gain).
- **Stop line**: the next candidates would harm an axis — SP2/SP3
  (evidence instruments behind cited claims), SP4 (experiment parameter),
  SP5/SP6 (defensive loudness), SP7 (refactor of pinned emissions),
  SP8/SP9 (deliberate cross-arm/derived evidence), SP10 (live rows, live
  allowlist, non-redundant floor gate), SP11 (live knob). Stopped here.

## 8. Custody notes, residual risks, blockers

- **No tracked file written, no commit, no git mutation by this seat.** No
  untracked artefact remains under `corpus/fixtures/` (the pre-existing
  `__pycache__` pyc is now covered by the sibling lane's
  `**/__pycache__/` ignore, §8 next).
- **HEAD moved mid-session**: `ee20575` → `03d0239` (r90 reviewer, 19:18:15
  local). Three of the four landing files still carry the `ee20575` bytes
  (`rb_lattice.gd` `10da2291…`, `rb_watch.gd` `e349faa0…`,
  `reports/round-90/r90-author.md` unmodified); `run_battery.py` is modified in
  the working tree by another lane (next bullet) — every receipt in this report
  was taken against the **committed `ee20575`** bytes.
- **Foreign in-flight edit (not this seat's write).** A sibling `r89-fold`
  lane modified the working tree at 19:16:20–19:17:32 local:
  `corpus/fixtures/run_battery.py` `76c0b1f5…` → `2679180a…` (+80/−11: a
  `required_stderr` mechanism, `run_process_streams`, r89-row comment/row
  updates), `corpus/fixtures/geo2d_lattice.gd` `9784716b…` → −51 lines (r89
  SP1 fold + critic-F5 `bridge_hole`/`bridge_hole2` deletion + the lineempty
  stderr pin), plus `corpus/.gitignore` (+4: `**/__pycache__/`, `**/.godot/`),
  `corpus/live/.gitignore` (+6), `corpus/live/r89-author/manifest.sha256` (−1).
  **My control battery launched at
  19:12:25 local and its launch snapshot is byte-proven to hold the committed
  bytes** (`runs-control/*/scratch/geo2d_lattice.gd` = `9784716b…`/581 lines,
  `input89_edges.gd` = `601c223e…`, `rb_lattice.gd` = `10da2291…`; the harness
  process read `run_battery.py` at import, before the 19:16:55 edit, and its
  `geo2d_lattice_lineempty` row is identical to the canonical green run's).
  All post-battery audits were additionally **re-run against a byte-exact
  `ee20575` fixture snapshot** and produced **5/5 byte-identical receipt files**
  (`committed-*.txt` == the working-tree-run receipts), i.e. the foreign edit
  did not touch the r90 block (r90 block sha `2c6721bc…` in both files).
- **Load**: 69 → 125 average on 32 cores throughout (none of it mine); my
  flakes are exactly the documented pre-existing classes. The r90 rows never
  flaked (12/12 in the control run, and identical to both green runs).
- **Residual risks**: (a) F1's narrative is still in the tracked author report
  (reviewer F2 remains open as an action item, not a blocker); (b) the
  `freezelock`/`contacts`/`gravity`/`damp` 4-dp pins ride float32 fixed points
  (author's own caveat class); (c) the r89 fold now in the working tree will
  re-shape `geo2d_lattice` provenance — this report's r90 scope is unaffected.
- **Blockers: none.** The simplifier move is complete: audited clean, no fold,
  boundary folds re-verified, findings ranked and (F1) already adjudicated by
  the committed reviewer report.

Seat output complete.
