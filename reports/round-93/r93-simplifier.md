# game-dev-2d round 93 — simplifier (r93-simplifier): the r93 Anim/Tween landing on committed `4b75151` is audited clean — **zero provable YAGNI deletions** (0 write-only stores across 272 declarations, 0 dead rows/arms/gates/knobs/entries, 0 duplicate or subsumed signatures), all four encoded folds re-verified on the landed bytes with fresh receipts, and the `r93_expected_errors_all_matched` floor gate proven **loud** under a dead-entry fold (+1 stale entry ⇒ row still PASSes, gate flips `False`, `dead_entry_count=1` names it ⇒ battery FAIL); **no patch proposed** (zero tracked writes)

Seat `SIMPLIFIER` (LEAF) | lane `r93` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14. Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
Work commit **`4b75151`** (r93 author: `corpus/fixtures/anim_lattice.gd` 689
lines `6a919ae04d4e754953b9f8067c49b74c46cf5f3bdc1dce76d4e29597faa2cd4a` +
`corpus/fixtures/r93b_anim.gd` 466 lines
`3c8dd8f10d6888e120c2420a3dcfc8c0867372ad0907d99d88b1eb98f1efd966` +
`corpus/fixtures/run_battery.py` +111/−0
`a79bfdd6f3f468d7cf904608a053b22bb4f3d6423d199e4e81bfa1605506df83` (4336
lines) + author receipts/report, 295 rows). **The landing bytes are unchanged
at the moved HEAD** — HEAD advanced under the sibling wave-B seats
(`043708ba` critic → `d2aac92b` reviewer → `6dd0a9f6` verifier, now at
`6dd0a9f6`); `git show HEAD:corpus/fixtures/{anim_lattice.gd,r93b_anim.gd,run_battery.py}`
are byte-identical to `4b75151` (all three shas re-verified). **No tracked file
written, no commit, no git mutation by this seat.** Writes are this report and
`corpus/live/r93-simplifier/**` only.

**Concurrent-lane disclosure (worktree, not mine).** While this seat ran, the
r94 author lane began landing in the shared worktree: `corpus/fixtures/particles_lattice.gd`
(new, 02:54:51) and an **uncommitted** `+91` insertion into the worktree
`corpus/fixtures/run_battery.py` (a 19-row particles block; worktree sha
`2b1f4df5…`, 307 CASES rows) at 02:56:54. None of it is this seat's, none of
it was analysed, and none of it is in any receipt below: all three of this
seat's full battery runs executed the **r93-era** harness (295 result rows,
zero `r94`/particles rows — see §4), and every static audit reads the pinned
`committed-fixtures/` snapshot (`git show 4b75151:`). Host ran under heavy
foreign oversubscription throughout (loadavg 55–87 on 32 cores, 48–60 foreign
`yes` hogs — none mine).

**`lsp` disclosure.** No `lsp` device is exposed in this dispatch and no
GDScript language server exists on this host (same finding as the r89–r93
seats). Symbol-aware `references`/`definition`/rename were therefore
**unavailable**; no cold result is recorded as absence. No rename was needed
(no deletion was proposed), so hand editing never arose. Every caller/consumer
claim below rests on (a) a complete scope-aware textual scan, (b) an
arm↔row↔gate↔entry census, (c) a pin↔emission census over real receipts, and
(d) fresh-process byte comparison.

**Frozen probeParent.** Exactly **one** read-only `ufo-labrat` was dispatched
(agent `d718f42a`, bounded, 3 falsifiable clauses, static scan only, no
writes). It returned **H1 CONFIRMED** (zero write-only stores in both fixtures;
its own full-file manual audit), **H2 CONFIRMED** (arm sets quoted exactly:
`anim_lattice.gd` 11/11 covered, `r93b_anim.gd` 5/6 with `clock` the sole
uncovered arm), **H3 CONFIRMED** (zero `r93_` allowlist/stderr keys; gate
vacuously true today; 7 sibling gates enumerated and **none** can match an
`r93_` case name). Substrate limitation it disclosed: **no shell executor** —
its audit was `grep`/`read` only, so it could not re-verify the sha256 values
(they are pinned as comments at `run_battery.py:698–700` and were re-verified
by this seat). Its H1/H2/H3 agree with this seat's mechanical census
independently computed. No other descendant was spawned.

---

## 1. Method and proof artefacts

`corpus/live/r93-simplifier/` (`MANIFEST.sha256`, **186 files**, sha
`212276fa6bd3eee98429ece8b9c01b65c43b6641e56cc69cca89f3866a3431a9`; per-run
Godot scratch trees and per-run launch-project copies excluded):

| artefact | content |
|---|---|
| `committed-fixtures/` | byte-exact `git show 4b75151:` snapshot of `anim_lattice.gd` (`6a919ae0…`), `r93b_anim.gd` (`3c8dd8f1…`) and `run_battery.py` (`a79bfdd6…`); every audit below re-run against this snapshot |
| `runs-control1/20261016T010013729412Z/`, `control1-battery.stdout` | full battery on the committed tree: 295 rows, verdict **FAIL on `overlap` only** (pre-existing scene-install race class, r92-scribe A7; not r93), r93 rows **23/23 PASS**, `dead_entry_count=0`, all round gates true |
| `runs-control2/20261016T055101886625Z/`, `control2-battery.stdout` | second full battery on the committed tree: **295/295 PASS**, verdict PASS, `dead_entry_count=0`, `rows_with_expected_errors=68`, r93 **23/23**, all gates true |
| `fold-gate/`, `fold-gate.diff`, `runs-fold-gate/20261016T010542302783Z/`, `fold-gate-battery.stdout` | the **dead-entry fold** (committed harness + 1 stale `r93_tween_census` entry, sha `548c1fef…`) and its full battery: the row still **PASSes**, `r93_expected_errors_all_matched=False`, `dead_entry_count=1` naming the injected entry ⇒ `probe_error_clause_surface` FAIL ⇒ battery FAIL |
| `fold-runs/<stamp>/fold-verification.json`, `fold-verification.json`, `fold-verification.log`, `verify_folds.py` | 96 fresh launches: 23 rows × 3 reps in the battery's exact launch shape, classified by the **production** `classify_process` AST-extracted from the committed harness (segment sha `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`, the author/boundary/r92 convention) + the row's own committed signature; plus `--fixed-fps 30/60/120` ×2 and default ×2 for the N−1 law, 16 foreign-arm launches + 2 unknown-arm fallbacks |
| `audit-static.txt`, `audit_static.py` | scope-aware write-only-store scan (inner-class aware), function/print/arm/CLI census for both fixtures, harness r93 block census (row↔arm bijection, allowlists, gate prefixes, insertion shape) |
| `static-pin-analysis.txt`, `static_pin_analysis.py` | signature redundancy census (exact dups + substring subsumption within shared arms), crossfade law arithmetic, overshoot pin internal check, harness-comment spot checks |
| `unpinned-census.txt`, `unpinned_census.py` | emitted-vs-pinned token census per arm + helper-parameter census |
| `pin-census.txt`, `pin_census.py` | pin↔emission census over **518 receipts** (author runs1/runs3 + fresh-reps, r93-scout canonical+loadtest, r93-boundary 258, this seat's controls + fold runs) |
| `proj/`, `fold-gate/` | launch projects (fixtures copy incl. both probes, byte-verified to the committed shas) |

## 2. Verdict and findings (ranked)

**Verdict: PASS — the landing is audited clean and no YAGNI deletion is
provable; the four encoded folds are re-verified on the landed bytes, and the
floor gate is loud.** Like r92, this landing carries **nothing to delete**: the
write-only-store axis is empty in both fixtures, every removable-looking line
turns out to be a claim, an instrument, or evidence. 0 blockers.

| # | finding | severity | evidence |
|---|---|---|---|
| F1 | **Zero provable YAGNI deletions.** Scope-aware store scan over **272 declarations** (160 `anim_lattice.gd` + 112 `r93b_anim.gd`; file + function + inner-class scope, assignment-target aware): **0 write-only stores**, 0 cross-scope anomalies. Neither fixture declares any `const`/`enum`/`signal` (the r91-SETTLE class cannot exist). 23/15 functions accounted for; the only zero-call-site functions are engine-invoked (`_initialize`, the inner-class `notify` invoked by the METHOD track). Arm↔row bijection complete (11/11 anim_lattice arms used; 5/6 r93b arms used, `clock` documented unauthored); the only CLI knob read anywhere is `--arm=`. No duplicate signature and **no substring subsumption** between the 23 rows (6 arms carry 2–3 rows each — all disjoint clauses) | info (clean) | `audit-static.txt`, `static-pin-analysis.txt` |
| F2 | **The four encoded folds re-verify on the landed bytes.** (1) runtime overshoot: BACK/EASE_IN_OUT 1.0→10.0 reads **0.10286344587803 < start** at t=0.25 and 5.5 at t=0.5; SPRING/EASE_OUT 0→10 reads **10.510157585144 > end** at t=0.5 and 10.0 at t=1.0; static `interpolate_value` extrapolates (neg=−5.0, over=15.0) — 3/3 reps byte-identical. (2) N−1 await law: `x1=0.0` 3/3 default + 6/6 fixed-fps reps; `pos10 = 9/N` exact (0.3/0.15/0.075) and `x2 = 100/N`, `x3/x5 = 2/4 steps` at ff60/ff120. (3) crossfade `w_i=(i−1)/(N−1)`: the pinned arrays satisfy the law to **max rel err 8.5e-8** at N=10/20/5, and `interleaved == finished_010` byte-for-byte (`interleaved_eq_plain=true`, `hard_after_frame=500.0`). (4) DEFERRED flush: all four lattices (`manual_def`, `manual_def_phys`, `two_adv`, `immediate`) byte-exact in 3/3 reps | info (folds verified) | `fold-verification.json`, `fold-runs/` |
| F3 | **The floor gate is loud, not decorative — and non-redundant.** Fold: `+1` stale entry (`ERROR: r93-simplifier dead-entry fold probe (never emitted)`) added to `r93_tween_census` in a copied harness. Full battery on the folded bytes: the row **still PASSes** and `census_bare_classifier_consistent` / `census_allowlisted_reproduces_verdicts` / all 7 sibling gates stay **true**, **but** `dead_entry_count=1` names exactly the injected entry, `r93_expected_errors_all_matched=False` ⇒ `probe_error_clause_surface` FAIL ⇒ battery FAIL. No other gate's prefix tuple can match an `r93_` case (verified mechanically and by the labrat), so the r93 gate is the only floor covering the block | info (gate live) | `fold-gate.diff`, `runs-fold-gate/…/verdicts.json`, `fold-gate-battery.stdout` |
| F4 | **Pin↔emission census: every pin is bound by real emissions.** Over **518 receipts** (author runs1/runs3 + fresh-reps, r93-scout 54 canonical + 24 loadtest, r93-boundary 258, this seat's controls + fold runs), each of the 23 rows' committed signature appears in **100 %** of its own arm's receipts (25–37 receipts per row); **0 `ERROR:` lines** in any r93 receipt (consistent with the zero-entry allowlist); 12 of the 17 arms are byte-stable (`distinct=1`), the 6 mode arms vary in their unpinned tokens while the pinned clauses hold everywhere | info (integrity) | `pin-census.txt` |
| F5 | **Landing integrity on the committed bytes.** `runs-control2`: **295/295 PASS**, verdict PASS, `dead_entry_count=0`, `rows_with_expected_errors=68`, all 11 floor/census gates true, **r93 rows 23/23** (all `actual_exit=0`). `runs-control1` (same bytes): 295 rows, the only failure is `overlap` (pre-existing scene-install race class, r92-scribe A7 — it PASSes in control2, in the fold-gate run, and in the author's runs1/runs3); **r93 rows 23/23** there too and the r93 gate true. `runs-fold-gate` (folded bytes): 295 rows, r93 23/23 PASS, only the meta gate row fails | info (integrity) | `runs-control2/…/verdicts.json`, `runs-control1/…/verdicts.json`, `runs-fold-gate/…/verdicts.json` |
| F6 | **Mechanism-blind pin, disclosed (cross-ref critic F1).** The harness comment (lines 712–715) says the first awaited frame "still reads the pre-play value"; the committed fixture cannot distinguish that from "applies the animation's t=0 pose", because the `frame` arm's target is a fresh `Node2D` (position.x = 0.0) and the track's t=0 key is 0.0 (`r93b_anim.gd:168–180`). The **pin** (`x1=0.0`) is correct and holds; only the prose mechanism is unfalsifiable here. Recorded, not edited (zero-gain edit class; the critic's `preplay` probe is the falsification record) | info (doc nit) | `r93b_anim.gd:168–180`, `run_battery.py:712–715`, committed `r93-critic.md` F1 |
| F7 | **Stale probe-header phrasing (doc nit).** `r93b_anim.gd:17` still says "runtime overshoot **clamp**" — the pre-falsification hypothesis wording. The arm measures the opposite (no clamp on either side) and the harness comment records the falsification; the file is a frozen byte-copy whose sha is cited by the harness comment (line 700) and the author report, so editing it is zero-gain and stales provenance (r92-F9 class). No action | info (doc nit) | `r93b_anim.gd:17`, `run_battery.py:716–719` |
| F8 | **The `clock` arm is unpinned by design, not dead weight.** 100 % of its tokens (`proc_delta`, `deltas`, `phys_per_proc`, `wall_us_per_await`, …) are referenced by no row, and the arm is 1 of 6 in `r93b_anim.gd` with no CASES row. It is the **launch fingerprint** that produced the boundary's fixed-fps boot-transient measurement and the harness comment's "`--fixed-fps` is a STABILIZER" law (cited by `reports/round-93/r93-boundary.md` §6 and its 16/16 receipts). Deleting it removes the evidence chain, changes nothing measurable and stales the cited sha — rejected (r92-SP1/SP9 class) | info (keep) | `unpinned-census.txt`, `audit-static.txt`, boundary §6 |
| F9 | **Helper defaults: exactly one is never overridden.** `_const_anim(value, length = 1.0)` — `length` is never passed at any call site in either fixture; `_value_anim`'s `length`/`loop_mode` **are** exercised positionally (2/1 passes in `anim_lattice.gd`; 2/0 in `r93b_anim.gd`). The dead default saves 0 lines, changes no byte, and would stale the cited probe shas — rejected (r92-SP7 class) | info (keep) | `unpinned-census.txt` |
| F10 | **Signature forge surface is closed.** 16 foreign-arm launches + the unknown-arm fallback (`--arm=__bogus__`) of both probes satisfy **no** r93 row signature; each row is only ever evaluated against its own `--arm=` launch. Corroborates the author's labrat clause 2: `phys_delta=0.01666666666667` also appears in the `clock` arm (harmless — `clock` is not a CASES row) | info (keep) | `fold-verification.json` §cross_arm |
| F11 | **Comment citations check out.** The harness comment's corpus counts are accurate on disk: r93-scout **54** canonical `.out` + **24** loadtest `.out`, r93-boundary **258** canonical `.out` + **16** purity runs; the fixtures are byte-copies of the frozen probes (`6a919ae0…` / `3c8dd8f1…` both re-verified against `corpus/live/r93-{scout,boundary}/probes/`) | info (custody) | `audit-static.txt`, sha256 re-verification |

## 3. The fold question — candidates audited

Method: (a) scope-aware **write-only-store** scan over every declaration; (b)
**arm↔row↔gate↔knob** bijection census; (c) **pin↔emission** census on 518 real
receipts; (d) **signature redundancy** census (exact + substring); (e) direct
reading of every statement that writes node/engine state, asking "can this
change any pinned byte?"; (f) execution for every candidate that survives
(a)–(e).

| # | candidate | verdict | proof / reason |
|---|---|---|---|
| SP1 | `clock` arm (≈30 lines, 0 pinned tokens) | **rejected** | It is the boundary's launch-fingerprint instrument; its delta vector is quoted in the boundary §6 and underwrites the harness's fixed-fps stabilizer claim; deletion is measurement-invisible but removes the evidence that produced the law and stales the sha cited in two tracked files (r92-SP1/SP9 class) |
| SP2 | The 31 emitted-but-unpinned token instances (24 distinct names) across 7 arms (`idle_per_frame`, `proc_delta`, `tween5`, `quick`, `frames`, `idle_lag`, `pos10`, `unpaused`, `n`, `blend_get`, `x0`, `y0`, `caches_*`, `mixer_*`, `at_pause`, `auto`, `paused`, `phys`, `is_playing`, `frames_to_finish`) | **rejected** | They are the discovery surface the boundary used to *derive* the mode law (r92-SP1 class) and the author's explicit "never pin frame counts / mid-blend values" scope decisions (`pos10` is the general N−1 law, deliberately unpinned); deleting them changes stdout bytes for zero gain and destroys the measurement surface for the next falsifier |
| SP3 | `_const_anim`'s never-overridden `length` default | **rejected** | 0 lines saved, 0 bytes changed, stales the cited probe sha (r92-SP7 class) |
| SP4 | `r93b_anim.gd:17` "runtime overshoot clamp" header phrasing | **rejected as an edit** | Documentation nit (F7); the file is a frozen byte-copy of record — any edit stales the sha cited by the harness comment + author report (r90-SP7 zero-gain class) |
| SP5 | The harness's ~55-line r93 comment block (lines 697–751) | **rejected** | It **is** the fold encoding (overshoot/no-clamp, N−1 law and its scope, crossfade granularity rule, DEFERRED routes, the negative-control list, the insertion-position rationale); deleting it orphans every justification (r91-SP6 / r92-SP9 class) |
| SP6 | Fixture ↔ frozen-probe duplicates (`anim_lattice.gd` ×2, `r93b_anim.gd` ×2, byte-identical) | **rejected** | The scout/boundary copies are the provenance of record (paths + shas cited by the author report and the harness comment); seat receipts under `corpus/live/<seat>/` are the repo convention (r87–r92) |
| SP7 | The 7-line `r93_expected_errors_all_matched` gate | **rejected** | Proven **loud** (F3) and **non-redundant** (no sibling prefix matches `r93_`); it is the only floor that can catch a future dead r93 entry |
| SP8 | `r93_anim_await_offbyone`'s truncated prefix signature (`…idle=[x1=0.0`) | **rejected** | It binds the N−1 law's only *stable* instance; the general law (`pos10 = 9·delta`) is a mode at the default rate (author-disclosed scope). Lengthening the pin would import a mode (r91-F5 class) |
| SP9 | Rows sharing an arm (6 groups: tweenproc ×2, tweenval_grid ×2, animblend ×2, animproc ×2, frame ×3, manual_inv ×2) | **rejected (nothing redundant)** | Mechanical check: 0 exact duplicates and 0 substring subsumption within any shared-arm group — each row pins a disjoint clause of the same line, so neither row can fail-when-the-other-passes |
| SP10 | `r93_anim_phys_delta` (`phys_delta=0.01666666666667`) | **rejected** | Project-conditioned by design: it binds the 60-tps physics tick of `corpus/fixtures/project.godot`; a `physics_ticks_per_second` change must fail loudly, and the row is the only guard on the physics clock's rate |
| SP11 | Helper/duplication refactors with zero byte gain (e.g. sharing the two probes' `_lib`/`_value_anim`/`_player_for` helpers) | **rejected** | 0 lines saved, 0 battery bytes, and both fixtures are byte-copies whose shas are cited in tracked files (r90-SP7 class) |
| SP12 | *the honest negative* | **no fold** | Nothing survives (a)–(f): the two probes are measurement instruments where every emitted field is either a pinned claim or the unpinned discovery surface that produced the pins, and the store axis is empty |

**Conclusion.** The r93 landing has **no provable YAGNI deletion**. The only
removable-looking weight is an instrument (SP1/SP2), a byte-copy of record
(SP6/SP11), a documentation nit (SP4), or a coverage clause (SP7/SP8/SP10).
Contrast r91, where two byte-neutral deletions were provable. The honest
simplifier output here is: **nothing to cut**, and the folds verified below.

## 4. Landing integrity — the narrow check, on the committed bytes

- **Control battery (green)**: `runs-control2/20261016T055101886625Z` —
  **295/295 PASS**, verdict PASS, `dead_entry_count=0`,
  `rows_with_expected_errors=68`, all gates true
  (`census_*` 3/3, `phys2d_`/`r87_`…`r93_expected_errors_all_matched`),
  r93 rows **23/23** (`actual_exit=0`).
- **Control battery (flake-only)**: `runs-control1/20261016T010013729412Z` —
  295 rows; the only failing row is `overlap` (exit=1, "signal occurred before
  physics overlap observation" — the pre-existing scene-install race class,
  r92-scribe A7; it PASSes in control2, in the fold-gate run and in the
  author's runs1/runs3); r93 rows 23/23 and the r93 gate true.
- **Fold-gate battery** (folded bytes, §5): 295 rows, r93 rows 23/23 PASS, only
  `probe_error_clause_surface` FAIL (the injected dead entry) ⇒ battery FAIL.
- **Narrow behavioral check (isolated)**: `verify_folds.py` — 23 rows × 3 reps
  in the battery's exact launch shape (`godot --headless --path <scratch>
  --script res://<script> -- <flags>` via `subprocess.run`, no shell),
  classified by the **production** `classify_process` (segment sha
  `749fa0607e7707e6…`) with each row's committed signature: **69/69 PASS**,
  rc=0, **0 B stderr** in every rep. 12 arms are byte-stable (`distinct=1`);
  the 11 mode arms vary in their unpinned tokens only.
- **Pin↔emission census** (518 receipts): each row's signature present in
  **100 %** of its arm's receipts (25–37 per row); 0 `ERROR:` lines anywhere;
  **0 varying pinned fields**.
- **Mechanical census**: 288 CASES rows (295 result rows incl. 7 meta); the 23
  `r93_*` rows are contiguous (indices 261–283) ahead of the crash/descendant
  tail, predecessor `r92_tilemap_nullts_crash`, successor
  `crash_spontaneous_sigabrt` — the sleep-8 adjacency rationale holds;
  insertion is **+111/−0**; `corpus/fixtures/project.godot` untouched by the
  commit (0 occurrences in `git show --name-only 4b75151 -- corpus/fixtures/project.godot`);
  the commit carries 239 files (fixtures + author receipts + author report).
- **Allowlist / gate liveness**: 0 r93 `expected_errors` entries and 0
  `required_stderr` entries (nothing dead); the r93 gate is the only floor
  covering `r93_`; the dead-entry fold flips it (F3).

## 5. The four encoded folds re-verified on the landed bytes

| fold | claim | receipt |
|---|---|---|
| 1 | **Runtime tweens overshoot — no clamp on either side.** BACK/EASE_IN_OUT 1.0→10.0: t=0.25 ⇒ **0.10286344587803** (*below* start), t=0.5 ⇒ 5.5. SPRING/EASE_OUT 0→10: t=0.5 ⇒ **10.510157585144** (*above* end), t=1.0 ⇒ 10.0. Static path also extrapolates (`clamp=[neg=-5.0,over=15.0]`). Byte-identical 3/3 reps; the `overshoot`/`overshoot2`/`clamp` tokens parse and satisfy every law clause | `fold-verification.json` folds.overshoot, `fold-runs/` |
| 2 | **`await process_frame` N times ⇒ N−1 applied steps.** `idle=[x1=0.0` in 3/3 default reps and 6/6 fixed-fps reps; at ff30/ff60/ff120 `pos10 = 9/N` exactly (0.3 / 0.15 / 0.075) and `x2 = 100/N` (3.3333 / 1.6667 / 0.8333); `x3/x5 = 2/4 steps` exact at ff60/ff120. The ff30 boot transient perturbs steps 2 and 4 (7.5 vs 6.667; 13.417 vs 13.333) yet **step 9 is exact again (30.0)** — the transient redistributes elapsed time, it does not lose it (boundary §6, re-derived here) | `fold-verification.json` law_runs |
| 3 | **Crossfade weight law `w_i=(i−1)/(N−1)` at three step granularities + await immunity.** The pinned `finished_010` (N=10), `finished_005` (N=20), `finished_020` (N=5) arrays satisfy `100 + 400·w_i` to **max rel err 8.5e-8** (float32 prints); `interleaved == finished_010` byte-for-byte with `interleaved_eq_plain=true` and `hard_after_frame=500.0`; 3/3 reps | `static-pin-analysis.txt`, `fold-verification.json` folds.blend |
| 4 | **DEFERRED flushes on the next process frame *and* on a physics frame.** `manual_def=[after_adv=[],next_proc=[7,8],second_proc=[7,8]]`, `manual_def_phys=[after_adv=[],after_phys=[7,8]]`, `two_adv=[after=[],flush=[7,8]]`, `immediate=[after_adv=[7,8],after_frame=[7,8]]` — all four lattices byte-exact in 3/3 reps | `fold-verification.json` folds.deferred |
| + | **The two mode cells' pinned clauses hold.** `tweenproc.stable=[auto_advanced=true,paused_frozen=true,phys_advanced=true,manual_exact=true]`, `phys_manual=[before=1.0,after_step025=2.0]`, `animproc.manual/frozen/inactive`, `stable=[…septet…]`, `manual_inv` invariants + `unpaused_moved=true` non-vacuity control: pinned in 3/3 reps each | `fold-verification.json` rows, `pin-census.txt` |
| + | **The floor gate is a live discrimination instrument.** `+1` stale entry on `r93_tween_census`: row PASS, all sibling/census gates true, `dead_entry_count=1` (named), `r93_expected_errors_all_matched=False` ⇒ battery FAIL | `fold-gate.diff`, `runs-fold-gate/…/verdicts.json` |

## 6. The proposed fold: **none**

No deletion survives the candidate audit (§3). This seat proposes **no patch** —
the landing is at its minimal provable weight on every axis this seat can
measure (store scan, row/arm/gate/knob bijection, entry liveness, signature
redundancy, pin↔emission). Every remaining removable-looking line is
load-bearing as instrument, evidence, or coverage. If the round is ever
re-opened, the only actionable items are *precision* notes others already
filed: critic F1 (the "pre-play value" prose mechanism — my F6), the probe
header's stale "clamp" phrasing (F7), and the reviewer/verifier observations
recorded in their committed reports.

## 7. Evidence index

`corpus/live/r93-simplifier/` — `MANIFEST.sha256` (186 files, sha
`212276fa6bd3eee98429ece8b9c01b65c43b6641e56cc69cca89f3866a3431a9`):

| artefact | path |
|---|---|
| committed snapshot (byte-exact) | `committed-fixtures/{anim_lattice.gd,r93b_anim.gd,run_battery.py}` |
| green battery (295/295) + flake-only battery | `runs-control2/20261016T055101886625Z/verdicts.json`, `control2-battery.stdout`, `runs-control1/20261016T010013729412Z/verdicts.json`, `control1-battery.stdout` |
| dead-entry fold + its battery | `fold-gate.diff`, `fold-gate/run_battery.py` (`548c1fef…`), `runs-fold-gate/20261016T010542302783Z/verdicts.json`, `fold-gate-battery.stdout` |
| fold verification (23 rows × 3 reps + fixed-fps laws + cross-arm) | `fold-verification.json`, `fold-verification.log`, `fold-runs/`, `verify_folds.py` |
| censuses | `audit-static.txt`, `static-pin-analysis.txt`, `unpinned-census.txt`, `pin-census.txt` + their scripts |
| launch projects | `proj/`, `fold-gate/` (probes byte-verified to the committed shas) |
| source reports | `reports/round-93/r93-{scout,boundary,author,critic,reviewer,verifier,scribe}.md` |
