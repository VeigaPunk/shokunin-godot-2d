# game-dev-2d round 94 — simplifier (r94-simplifier): the r94 Particles2D landing on committed `c7228893` is audited clean — **two provable YAGNI deletions** (−3 lines: the dead `T0` store and the dead `start3` store) proposed as a patch, **not applied** (zero tracked writes); the four-line fixture fold is re-verified on the landed bytes with fresh receipts, the `r94_expected_errors_all_matched` floor gate is proven **loud and non-redundant** under a dead-entry fold, and every r94 pin is bound by real emissions

Seat `SIMPLIFIER` (LEAF; frozen `probeParent` — one labrat dispatch, §0) | lane
`r94` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless, 60 tps,
RendererDummy), Python 3.14. Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
Work commit **`c7228893`** (r94 author: `corpus/fixtures/particles_lattice.gd`
763 lines `0701e813e50cdb50e05f0df0194d0baf94c1240f361e941949414dd5c52c00a9` +
`corpus/fixtures/run_battery.py` `+91/−0`
`2b1f4df5426a8da679c58c58057817b75f6fd879f9ffc8ab1045b03deae04238` (4427
lines) + author report, **314 rows**). HEAD advanced mid-session under the
sibling wave-B seats (`c7228893` → `86ace53c` reviewer → `cd83d736` scribe →
`72315b14` critic → `6f817d10` verifier → **`9cd47507`** r95 author); the
**landing bytes are unchanged at the moved HEAD** — `git show 9cd47507:corpus/fixtures/particles_lattice.gd`
re-hashes to `0701e813…`, and the 19 r94 `CASES` tuples at `9cd47507` are
**byte-identical** to the `c7228893` ones (AST-extracted and compared), while
the worktree fixtures were byte-clean at session start. **No tracked file
written, no commit, no git mutation by this seat.** Writes are this report and
`corpus/live/r94-simplifier/**` only (285 files, `MANIFEST.sha256`).

**`lsp` disclosure.** No `lsp` device is exposed in this dispatch and no
GDScript language server exists on this host (same finding as the r89–r93
seats). Symbol-aware `references`/`definition`/rename were therefore
**unavailable**; no cold result is recorded as absence. No rename was needed:
the landing adds one new fixture and literal `CASES`/gate inserts, and the only
deletion proposed is the removal of three never-read store lines (no symbol
consumers). Every caller/consumer claim below rests on (a) a scope-aware
write-only-store scan, (b) an arm↔row↔gate↔entry census, (c) a pin↔emission
census over 504 real receipts, and (d) fresh-process byte comparison.

**Foreign-worktree disclosure (not mine).** At **03:41:30**, *during* this
seat's control2 run, a sibling **r95** lane inserted its own block into the live
tracked `corpus/fixtures/run_battery.py` (`git diff` = `+163` lines, all
`r95_*`/`dss_lattice` content, appended after the r94 block; matching untracked
`corpus/fixtures/dss_lattice.gd`, `corpus/fixtures/r95b_order.gd`) — the same
write the r94 reviewer records; it has since been **committed as `9cd47507`**
(the r95 author commit). None of it is this seat's and none of it is analysed
here. Control1 (loaded 03:34:07) predates it; control2 (loaded 03:41:28.6) ran
the r94-era CASES (**314 rows, 0 `r95_` rows** in its `verdicts.json`); every
other run of mine executed a byte-copy of the `c7228893` snapshot
(`committed-fixtures/`, `proj/`, `fold-gate/`, `fold-candidates/` — all
re-hashed). The r94 landing is intact at `9cd47507` (fixture sha unchanged; 19
r94 CASES tuples byte-identical).

**Host is shared.** Foreign loadavg ran 56–107 on 32 cores for the whole
session (other lanes' batteries included). Every number below is
host-conditioned; the boolean gates are the load-proof form.

**Frozen probeParent.** Exactly **one** read-only `ufo-labrat` was dispatched
(agent `2eb02cdd`, bounded, three falsifiable clauses, static grep/read only, no
writes, no shell). It returned **H1 CONFIRMED** (exactly two write-only stores:
`T0` and `start3`; all 145 `var` declarations enumerated, no third site),
**H2 CONFIRMED** (the fixture-vs-frozen-probe non-comment diff is exactly the 4
declared lines; every other difference is a comment), **H3 CONFIRMED** (no
`r94_` allowlist entry anywhere; `r94_` is the only gate prefix that can match
an `r94_` case). Its findings agree with this seat's mechanical census,
independently computed. No other descendant was spawned.

---

## 0. Method and proof artefacts

`corpus/live/r94-simplifier/` (`MANIFEST.sha256`, **285 files**; per-run Godot
scratch trees excluded, verdicts/stdout logs included):

| artefact | content |
|---|---|
| `committed-fixtures/` | byte-exact `git show c7228893:` snapshot of `particles_lattice.gd` (`0701e813…`) and `run_battery.py` (`2b1f4df5…`); every audit below re-run against this snapshot |
| `runs-control1/20261016T063407683465Z/`, `control1-battery.stdout` | full battery on the committed bytes **under 8 seat `yes` hogs** (loadavg 77→83): 314 rows, verdict FAIL on `overlap`+`transition` only; r94 **19/19 PASS**; r94 gate true; `dead_entry_count=0` |
| `runs-control2/20261016T064128655871Z/`, `control2-battery.stdout` | second full battery, no seat hogs (loadavg 57–64): 314 rows, FAIL on `transition` only; r94 **19/19 PASS**; r94 gate true; `dead_entry_count=0` |
| `fold-gate/`, `fold-gate.diff`, `runs-fold-gate/20261016T064647728943Z/`, `fold-gate-battery.stdout` | the **dead-entry fold** (committed harness + 1 stale `r94_particles_cpu_never` entry) and its full battery: **all 314 case rows PASS** (the folded row included), `r94_expected_errors_all_matched=False`, `dead_entry_count=1` naming exactly the injected entry ⇒ `probe_error_clause_surface` FAIL ⇒ battery FAIL |
| `fold-runs/20261016T065610468541Z/fold-verification.json`, `fold-verification.json`, `fold-verification.log`, `verify_folds.py` | 19 rows × 3 reps fresh launches on the committed bytes in the battery's exact launch shape, classified by the **production** `classify_process` AST-extracted from the committed harness (segment sha `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`, the author/boundary convention) + the row's committed signature; plus `--fixed-fps 30` ×3 folded-vs-frozen pairs, the 7-step `request` ladder on a spec-list-only variant, the unknown-arm launch and the 19×19 cross-arm matrix |
| `fold-candidates/`, `fold-proposal.diff`, `fold-candidates-verification.json`, `fold-candidates-analysis.txt`, `fold_candidates.py`, `fold_candidates_analysis.py`, `fold-candidates.stdout` | the **−3-line YAGNI patch tree** (`T0` + `start3` deleted; folded fixture `afd2aa88…`) and its proof: 19 arms × 3 reps committed-vs-folded raw comparison + same-fixture run-to-run controls |
| `runs-fold-candidates/20261016T070931814017Z/`, `fold-candidates-battery.stdout` | full battery on the **folded bytes** (loadavg 95–107): 314 rows, r94 **19/19 PASS**, r94 gate **True**; failing rows are the pre-existing volatile class (`overlap`, `transition`, `negative_transition`, `audio_bus_route_invalid_control`) |
| `audit-static.txt`, `audit_static.py` | scope-aware write-only-store scan, function/print/arm/CLI census, harness r94 block census (row↔arm bijection, allowlists, gate prefixes, insertion shape, signature redundancy) |
| `pin-census.txt`, `pin_census.py` | pin↔emission census over **504 receipts** (466 file receipts = scout canonical 105 + scout loadtest 38 + boundary 323; plus the author's two battery runs × 19 r94 rows = 38 battery outputs) |
| `unpinned-census.txt`, `unpinned_census.py` | emitted-vs-pinned token census per row: the tails that are deliberately not pinned (mode envelopes) |
| `head-check.txt`, `head_check.py` | 307 unique case names; census signature == full emitted line; 19/19 signatures are unique contiguous heads of their scout `rep1` line |
| `flake-probe.txt`, `flake_probe.py` | `transition` pass rate on this host: **4/10** (the volatile row's own flake rate) |
| `landing-inventory.txt` | commit/sha/diff inventory (HEAD, shas, `+91/−0`, full fixture-vs-frozen diff) |
| `proj/` | launch project = byte-copy of the committed fixture set (no `run_battery.py`), `project.godot` `8de8b3af…` = `corpus/fixtures/project.godot` |

## 1. Verdict and findings (ranked)

**Verdict: PASS with a proposed patch — the landing is audited clean, two YAGNI
deletions are provable and byte-neutral (−3 lines, §4), the four-line fold is
re-verified on the landed bytes, and the r94 floor gate is loud and
non-redundant. 0 blockers.** Like r91 (and unlike r92/r93, where nothing was
provable), this landing carries a real, executed-verified wart: two never-read
stores inherited from the scout probe.

| # | finding | severity | evidence |
|---|---|---|---|
| F1 | **Two provable YAGNI deletions (−3 lines), byte-neutral.** `var T0 := 0` (`:53`) + `T0 = Time.get_ticks_usec()` (`:739`, the write) and `var start3: int = PH` (`_arm_gpu_headless:723`) are **write-only stores** — zero reads file-wide, confirmed by the labrat's independent enumeration of all 145 declarations. The patch tree (`fold-candidates/`, `fold-proposal.diff`) executes byte-neutral: 57 committed-vs-folded pairs, 11 tail-only mismatches, **every pair's pinned prefix byte-identical**; the same-fixture run-to-run controls mismatch **12/57** (committed) and **12/57** (folded) — the differences are host-timing ±1 modes, not the fold. The full battery on the folded bytes: 314 rows, r94 **19/19**, r94 gate **True** | low (clean-up; −3 lines) | `audit-static.txt`, `fold-proposal.diff`, `fold-candidates-analysis.txt`, `runs-fold-candidates/…/verdicts.json` |
| F2 | **The floor gate is loud, not decorative — and non-redundant.** Fold: `+1` stale entry (`ERROR: r94-simplifier dead-entry fold probe (never emitted)`) added to `r94_particles_cpu_never` in a copied harness. Full battery on the folded bytes: **all 314 case rows PASS** (including the folded row), all sibling gates stay true, **but** `dead_entry_count=1` names exactly the injected entry, `r94_expected_errors_all_matched=False` ⇒ `probe_error_clause_surface` FAIL ⇒ battery FAIL. No other gate's prefix tuple can match an `r94_` case (mechanical census + labrat H3) | info (gate live) | `fold-gate.diff`, `runs-fold-gate/…/verdicts.json`, `fold-gate-battery.stdout` |
| F3 | **The four-line fold re-verifies on the landed bytes.** (a) non-comment diff fixture-vs-frozen-probe = exactly 4 changed lines (3 `_okb` windows `4,7`→`1,7`; `round`→`floor`), 8 diff lines counting removals+additions, everything else comment; (b) `--fixed-fps 30` `cpu_pause`: **folded `ok=true` 3/3** vs **frozen `ok=false` 3/3** (`vis_parent=2`, `pm_disabled=2`, identical tails) — the fold's stated purpose; (c) `request` ladder on the committed bytes over 7 steps: **`floor(L/step)+1` fits 7/7**, `round` fails at 0.20 (predicts 4, measured 3) and 0.30 (predicts 3, measured 2); (d) the two pinned integer ratios emit `expected=6/11`, unchanged | info (folds verified) | `fold-verification.json`, `landing-inventory.txt` |
| F4 | **Pin↔emission census: every pin is bound by real emissions.** Over **504 receipts** (466 file receipts = scout canonical 105 + loadtest 38 + boundary 323; plus the author's two battery runs × 19 rows), each row's committed signature appears in **100 %** of its own arm's receipts except **3 misses** — all three `r94_particles_cpu_pause` at boundary `ff30` on the **frozen scout probe** (the pre-fold `ok=false`, exactly the defect the fixture fold fixes). **0 `ERROR:` lines, 0 non-empty stderr, 0 non-zero rc** anywhere in the r94 corpus | info (integrity) | `pin-census.txt` |
| F5 | **Landing integrity on the committed bytes.** `runs-control1` (8 seat hogs, loadavg 77→83): 314 rows, FAIL on `overlap`+`transition` only; `runs-control2` (no hogs, loadavg 57–64): 314 rows, FAIL on `transition` only; **r94 rows 19/19 PASS and the r94 gate `True` in both**; `dead_entry_count=0`, `rows_with_expected_errors=68` in both. The failures are the **pre-existing load-conditioned scene-install race class** (r92-scribe A7 / r93-reviewer's enumerated set): the `transition` row's own flake rate on this host measured **4/10** (`flake-probe.txt`). On the same bytes the author's two runs and the r94 scribe's `git archive HEAD` extract run are **green 314/314** (sibling receipts, read as data), and the r94 reviewer's run fails only on `transition` | info (integrity) | `runs-control1/…/verdicts.json`, `runs-control2/…/verdicts.json`, `flake-probe.txt`, `reports/round-94/r94-scribe.md` |
| F6 | **Signature census: no redundancy, no truncation, no forge.** 307 CASES rows, 307 unique names; **0 exact duplicate and 0 substring-subsumption pairs among the 19 r94 signatures**; no r94 signature is contained in a foreign row's signature; the `census` signature is **byte-equal to the full emitted 8785-char line**; all 19 signatures are unique contiguous heads of their scout `rep1` line; each arm's receipt satisfies **only its own** signature (19×19 matrix, 0 violations); the unknown-arm fallback matches **no** row | info (clean) | `audit-static.txt`, `head-check.txt`, `fold-verification.json` |
| F7 | **Arm↔row↔gate bijection complete; insertion shape exact.** 19 fixture arms ↔ 19 rows (no orphan arm, no phantom row, no duplicate arm, all `exit=0`); r94 block contiguous at CASES index **284..302**, predecessor `r93_anim_blend_interleaved`, successor `crash_spontaneous_sigabrt` (the author's stated position); `git numstat` = **+91/−0** (42-line comment header + 19 two-line rows + the 11-line gate); `expected_errors`/`required_stderr` carry **0 r94 entries** | info (clean) | `audit-static.txt`, `landing-inventory.txt` |
| F8 | **The unpinned surface is the measurement surface, deliberately.** Per-row tail census over the corpus: stable cells keep 1 distinct tail; the timing cells vary only in their measured tails (`cpu_lifetime` 12 tails, `cpu_pause` 5, `gpu_headless` 7 with `flip_after` ∈ [1,7] — the boundary's corrected range, live-confirmed). Nothing inside a pinned prefix varies anywhere. Cross-ref (sibling seat, read as data): the r94 critic's F1 observes that `cpu_contam`'s *pinned* tokens are structural counts while its claim sits in the tail — my census confirms that tail is byte-stable (1 distinct tail over 27 receipts), so the gap is closable by **extending** the pin; that is a coverage action, not a simplifier deletion | info (by design) | `unpinned-census.txt`, `reports/round-94/r94-critic.md` F1 |
| F9 | **`cpu_contam`'s `pre` emitter is an instrument, not dead weight.** The arm's never-nodes are added at `add_pf≥1`; the boundary §8 reframing ("the prior emitter is not the cause") is *carried by this very control*. Deleting `pre` (+`_wait_ph` rework) is byte-neutral but erases the historical positive control and stales the fixture sha — rejected (r91-SP3 class) | info (keep) | `audit-static.txt`, boundary §8 |
| F10 | **Carried risks, disclosed (not defects of this landing).** (a) the ladder/stream `_okb` windows are **60-tps-only** (boundary §3): safe only because the launch `project.godot` pins no `physics_ticks_per_second`; a future tps override rejects them (author-disclosed, probe header documents the alias). (b) **Scout evidence-integrity defect** (boundary §2): 135/143 scout receipts predate the frozen probe revision and `RECEIPTS.md` cites a different probe hash (`09dd7723…` vs `e6a2e0f5…`); the rows stand on the boundary's own 323-check matrix plus this seat's fresh receipts, not on the mixed-revision set. (c) the live worktree carried the r95 lane's `+163`-line write during this session (since committed as `9cd47507`) | info (risk) | boundary §2/§3/§10, `landing-inventory.txt` |

## 2. The fold question — candidates audited

Method: (a) scope-aware **write-only-store** scan over every declaration; (b)
**arm↔row↔gate↔entry** bijection census; (c) **pin↔emission** census on 504 real
receipts; (d) **signature redundancy** census (exact + substring, intra- and
inter-row); (e) direct reading of every statement that writes node/engine state;
(f) execution for every candidate that survives (a)–(e).

| # | candidate | verdict | proof / reason |
|---|---|---|---|
| SP1 | `var T0 := 0` `:53` + `T0 = Time.get_ticks_usec()` `:739` (−2 lines) | **FOLD PROPOSED** | Zero reads file-wide (labrat-confirmed over all 145 declarations); the RHS is a pure clock read. Executed byte-neutrality: 57-pair comparison, all cross mismatches tail-only with identical prefixes; same-fixture internal controls mismatch **more** (12 vs 11) — the fold is invisible. Folded-tree battery: r94 19/19, gate True |
| SP2 | `var start3: int = PH` `_arm_gpu_headless:723` (−1 line) | **FOLD PROPOSED** | Same class: sole occurrence, never read (the capture block reads `g3.capture_rect()` and `g3.emitting`, not `start3`); `PH` read has no side effect; the arm's receipt is raw-identical in the stable reps and tail-only in the timing reps |
| SP3 | the `pre` emitter + wait in `_arm_cpu_contam` (−~4 lines) | **rejected** | Byte-neutral but it *is* the scout-exact positive control the boundary §8 verdict is about ("the prior emitter only guarantees `add_pf≥1`"); deleting it erases the falsification's own instrument and stales the cited sha (r91-SP3 class) |
| SP4 | the 42-line r94 comment block (`run_battery.py:798–839`) | **rejected** | It **is** the fold encoding (windows, floor law, the `add_pf` rule, `fixed_fps` hazard, the not-authored list, insertion rationale); deleting it orphans every justification (r91-SP6/r93-SP5 class) |
| SP5 | the 11-line `r94_expected_errors_all_matched` gate | **rejected** | Proven **loud** (F2) and **non-redundant** (labrat H3; mechanical prefix census); inert today by design (0 entries), the only floor that can catch a future dead r94 entry |
| SP6 | fixture ↔ frozen-probe duplicate bytes (and the scout/boundary copies) | **rejected** | The frozen probe is the provenance of record (path + sha cited by the harness comment, the author report and the boundary report); seat receipts under `corpus/live/<seat>/` are the repo convention (r87–r93) |
| SP7 | the unknown-arm fallback `:762` | **rejected** | Defensive loudness class (r89-SP7/r91-SP5): a mistyped `--arm` prints `PASS particles_lattice unknown arm=…`, which satisfies **no** row signature (verified by launch: matched rows = []) — it cannot forge a PASS |
| SP8 | the emitted-but-unpinned tails (±1 deltas, `flip_after`, `fin_after_*`) | **rejected** | They are the discovery surface that produced the boundary's laws (mode envelopes, `flip_after` [1,7]); pinning them would import a mode (r91-F5/r93-SP2 class) |
| SP9 | the 60-tps-only `_okb` windows themselves | **rejected** | They encode the time law under the pinned launch project; the tps fragility is a **disclosed risk** (F10a), not a deletion — removing them would drop the only ladder coverage (boundary §10 explicitly keeps them) |
| SP10 | helper/duplication refactors with zero byte gain (e.g. sharing `_watch`/`_watch_gpu`) | **rejected** | 0 lines saved, 0 battery bytes, stales the fixture sha cited in tracked files (r90-SP7/r91-SP4 class) |
| SP11 | *the honest negative* | **no other fold** | Nothing else survives (a)–(f): the remaining weight is an instrument (SP3/SP8), the fold's own encoding (SP4), a proven-live coverage clause (SP5/SP9), a byte-copy of record (SP6), or defensive loudness (SP7) |

**Conclusion.** The r94 landing has exactly **one** provable fold class: the two
dead stores (SP1+SP2, −3 lines). Everything else that looks removable is an
instrument, an encoding, a coverage clause, or provenance. The r91 precedent
applies (a patch is proposed and measured, not applied).

## 3. The proposed fold (SP1+SP2) — patch, proof, cost

`fold-proposal.diff` / `fold-candidates/particles_lattice.gd` (folded sha
`afd2aa88876abc7a0923066b024c825aa111d3e471ee0e3a304a58f9e494a125`):

```
--- a/corpus/fixtures/particles_lattice.gd
+++ b/corpus/fixtures/particles_lattice.gd
@@ -53,1 +53,0 @@
-var T0 := 0
@@ _arm_gpu_headless
-	var start3: int = PH
@@ _initialize
-	T0 = Time.get_ticks_usec()
@@ fold-candidates/run_battery.py (sha citation follows the fixture)
-# Probe particles_lattice.gd sha256 0701e813…
+# Probe particles_lattice.gd sha256 afd2aa88…
```

**Proof of byte-neutrality (executed, not argued):**

- **57 committed-vs-folded pairs** (19 arms × 3 reps, battery launch shape, raw
  stdout+stderr+rc): 11 mismatching pairs, **all 11 with a byte-identical
  pinned prefix**; the differing tokens are exclusively the documented ±1
  measured tails (`l025[delta=15→14`, `ph=60→59`, `ts0[fin_after_restore=20→19`,
  `second_after=15→14`, `ss05[delta=59→60`, `stop40[fin_after=19→20`,
  `flip_after=2→3`). The **same-fixture** controls mismatch **12/57** (committed
  reps vs each other) and **12/57** (folded reps vs each other) — the cross
  difference rate is *lower* than the intrinsic run-to-run variance.
- **13 of 19 arms were raw-byte-identical 3/3** in the analysed run (12 in the
  earlier run; all pure cells + the stable timing cells: `cpu_never`,
  `cpu_contam`, `cpu_oneshot_off/flag`, `cpu_retrigger`, `cpu_lt_mid`,
  `cpu_speed_mid`, `cpu_amount_mid`, `cpu_request`); the timing arms differ only
  in their tails, per above.
- **Every arm's pinned prefix is byte-stable across all six receipts** of the
  comparison (`prefix_stable=True` for 19/19).
- **Full battery on the folded bytes**: 314 rows, **r94 rows 19/19 PASS**,
  `r94_expected_errors_all_matched=True` (the run's 3 dead entries all belong
  to the volatile non-r94 rows; none to the r94 block); the battery verdict is
  red only on the pre-existing volatile rows under loadavg 95–107 (`overlap`,
  `transition`, `negative_transition`, `audio_bus_route_invalid_control` — the
  r93-reviewer's exact list, none of which loads `particles_lattice.gd`).

**Cost (honest accounting).** −3 lines; the landed fixture sha `0701e813…`
becomes `afd2aa88…`, which stales the sha quoted in the harness comment
(updated by the patch itself), `reports/round-94/r94-author.md:36`, and every
receipt/manifest in `corpus/live/r94-{author,reviewer,simplifier}/` that cites
the landed sha (all **historical** records — nothing *live* consumes the
fixture sha except the harness comment). Applying it also means a new commit
and, per the r89/r91 precedent, a re-verification pass against the new sha.
**This seat does not apply it**: the assignment says zero tracked writes /
commit nothing, and the shipping decision belongs to the operator/integrator.
If the gate prefers "no churn on a verified sha" (the r90-SP1 trade), the
fallback disposition is *record-and-keep*; the finding is then a documented,
proven-clean wart rather than a defect.

## 4. Landing integrity and the narrow check, on the committed bytes

- **Control battery (load, 8 seat hogs)**: `runs-control1/20261016T063407683465Z`
  — 314 rows, FAIL on `overlap` + `transition` only; **r94 19/19 PASS**; r94
  gate `True`; `dead_entry_count=0`; `rows_with_expected_errors=68`; loadavg
  77→83.
- **Control battery (no seat hogs)**: `runs-control2/20261016T064128655871Z`
  — 314 rows, FAIL on `transition` only; **r94 19/19 PASS**; r94 gate `True`;
  `dead_entry_count=0`; loadavg 57–64.
- **Volatile-class evidence**: the `transition` row's own pass rate on this host
  is **4/10** (`flake-probe.txt`, same failure text as the r93/r94 reviewers
  recorded); the author's two runs on the identical bytes are **green 314/314**
  and the r94 reviewer's run fails only on `transition`.
- **Fold-gate battery** (folded bytes, §1 F2): 314 case rows all PASS; only
  `probe_error_clause_surface` FAIL (the injected dead entry) ⇒ battery FAIL.
- **Narrow behavioral check (isolated)**: `verify_folds.py` — 19 rows × 3 reps
  in the battery's exact launch shape, production `classify_process`
  (segment sha `749fa060…`): **57/57 PASS, 57/57 signature-present, 0 B stderr
  in 57/57**; plus the ff30 pair, the 7-step ladder, the unknown-arm launch and
  the cross-arm matrix (§1 F3/F6).

## 5. Tradeoff and stop line

- **Patch proposed, not applied** (SP1+SP2, −3 lines, §3). Everything else that
  could be deleted is an instrument (SP3), the fold encoding (SP4), a live
  coverage clause (SP5/SP9), provenance (SP6), or defensive loudness (SP7).
- **Stop line**: the next candidates would harm an axis — SP3 backs a cited
  falsification, SP4 is the fold's own justification, SP5/SP9 are the only
  guards on the r94 block, SP8 is the measurement surface, SP10 is zero-gain
  churn that stales a cited sha.
- **Nothing else was touched**: no other lane's files, no `corpus/fixtures/`
  tracked file, no commit, no `.godot/` cache created in the launch projects.

## 6. Remaining risks / blockers

- **60-tps-only `_okb` windows** (F10a): the ladder/stream/pause rows are safe
  only while the launch project pins 60 tps; a future `physics_ticks_per_second`
  override rejects them regardless of the boolean gate. Disclosed by the author;
  not a defect of this landing, but the top residual risk for the rows.
- **Scout evidence-integrity defect** (F10b): 135/143 scout receipts predate the
  frozen probe revision; `RECEIPTS.md` and `manifest.sha256` disagree on the
  frozen probe hash. The landed rows do not depend on that mixed set (boundary
  323-check matrix + this seat's 504-receipt census + 57 fresh reps), but the
  scout directory still carries the contradiction.
- **Volatile battery rows are load-conditioned** (F5): `transition` failed in
  both of this seat's runs (and the reviewer's) under load; a green full-battery
  run of my own was not obtained. The r94 block itself is load-proof (19/19 in
  every run at loadavg 57–107) and the author's green runs are on the same
  bytes.
- **The live worktree moved ahead** of `c7228893` during the session (r95 lane
  write at 03:41:30, since committed as `9cd47507`; the sibling r94 wave-B seats
  also committed their reports: `86ace53c` reviewer, `cd83d736` scribe,
  `72315b14` critic, `6f817d10` verifier). The r94 landing is intact at
  `9cd47507` (fixture sha unchanged, 19 r94 CASES tuples byte-identical) —
  recorded so the operator does not mistake the later commits for r94 churn.
- **Blockers: none.** Zero tracked writes; the report and receipts are the only
  outputs.
