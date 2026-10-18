# r101 SIMP-1 — queued simplifications, patch shards only (no in-repo fixture edits)

## Plan header (written first, before any measurement)
1. Harvest the queued-deletion queues from r98 (−19, minus dropped F5), r99 (−2), r100 (−2), r91 (−3) — critic/simplifier sections of `reports/round-{91,98,99,100}/`.
2. Scope: first half of `corpus/fixtures/` alphabetically (=< `project.godot`); candidates outside scope are recorded as out-of-scope hand-off, not deleted.
3. For each candidate: copy the repo tree to a scratch project, apply the deletion, run the single targeted fixture headless, compare stdout bytes + exit code against the unmodified baseline.
4. Emit ready-to-apply unified diffs (`diff -u` against untouched copies) plus before/after evidence lines in this shard.
5. Never run `corpus/fixtures/run_battery.py`; never edit shared registry files. All work in scratch.

## Verdict

**5 candidate folds PROVEN byte/verdict-neutral, ready to apply — −22 lines total.**
`nav_lattice.gd` −3 (r91), `canvas_lattice.gd` −10 + `r98b_attack.gd` −4 + `r98b_rksenum.gd` −3 (r98 F1–F4/F6, F5 dropped as instructed), `audio_lattice.gd` −2 (r99 F1).
**60 affected rows × committed/folded trees = 669 headless launches**: 0 rc diffs, **0 verdict flips** (60/60 PASS on every tree), 0 pinned-field violations, 0 `SCRIPT ERROR`/`Parse Error`. Patches in `reports/round-101/mutations/r101-simp1-*.patch`; all pass `git apply --check` at lane HEAD and the combined patch reproduces the folded bytes exactly.
No tracked fixture was modified by this seat; **nothing committed**.

## Host / space context (once)

```
$ uptime
 16:21:19 up 1 day, 16:21,  1 user,  load average: 40.10, 20.91, 13.51
```
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python 3.14.7. A sibling lane (game-dev-3d r104) is swarm-loading the host; launch times stayed ~0.9–2 s and no launch hit the harness's 8 s bound (0 timeouts in 669).
**`/tmp` is usrquota-exhausted for this user** (`echo test > /tmp/r101-simp1/t.txt` → `bash: write error: Disk quota exceeded`; 3.2 G "avail" is not usable). All scratch therefore lives in **`/var/tmp/r101-simp1/`** (root fs, 772 G free) — the same disclosed fallback r98/r99/r100 simplifiers used. The seat card named `/tmp`; the physical impossibility is recorded here rather than silently substituted.

## Queue harvest — every queued item, dispositioned

| queue entry | source | scope | disposition |
|---|---|---|---|
| r91 −3: `SETTLE` const + 2 `hits` sinks in `nav_lattice.gd` | `reports/round-91/r91-simplifier.md` §F1/§6 + `corpus/live/r91-simplifier/fold-proposal.diff` | **in half** | **PATCHED**; my reconstruction is hunk-body-identical to the in-repo patch and the folded sha `b23887e5…` matches r91's recorded folded sha exactly. **Two-seat convergence:** the sibling seat SIMP-3 independently emitted `reports/round-101/mutations/r101-simp3-nav-fold.patch`, which is `diff`-identical to `r101-simp1-r91-nav_lattice.patch` (same bytes); the orchestrator should keep one copy |
| r98 −19: F1 `canvas_lattice.gd` `methods`, F2 `_notif_keys()`, F3 `owner_ref`, F4 `pfs`, F6 `_items` (F5 dropped) | `reports/round-98/r98-simplifier.md` §2 | **in half** (all 3 files) | **PATCHED** (measured −17, see delta note) |
| r98 F5: `--arm=env` arm in `r98b_attack.gd` (−21) | same §4 | in half | **NOT PATCHED** — the r98 report itself says "drop F5 if provenance outweighs −19"; the seat card says "minus dropped F5" |
| r99 −2: F1 `prev_t` (`audio_lattice.gd`) + F2 `pairs` (`r99b_modes.gd`) | `reports/round-99/r99-simplifier.md` §2 | F1 **in half**, F2 out | F1 **PATCHED**; F2 handed off |
| r99 F3 (28 × `stream = null`) / F4 (harness comment) | same §2 | F3 in half, F4 shared file | **NOT PATCHED** — the queue counts −2 (two folds), and F3 is the report's own "observational, not semantic" caveat; F4 is a `run_battery.py` edit (shared file, orchestrator-serialized) |
| r100 −2: SP2 `--arm` parse + SP3 `arm` carrier in `r100b_seq.gd` | `reports/round-100/r100-simplifier.md` §3 | **out of half** | **HANDED OFF** |
| r100 SP1: duplicate crash CASES rows | same §3 | `run_battery.py` (shared) | **out of remit**; already deduped upstream at `9ede7c50` |

## Candidates and the exact proof of deadness

| # | file | site | proof of deadness (text census, file-global) | execution proof |
|---|---|---|---|---|
| A | `nav_lattice.gd` | `const SETTLE := 10` (56) | only occurrence of `SETTLE` in the file | all 11 nav rows |
| A | `nav_lattice.gd` | `var hits` + `hits.append(v)` in `_arm_teardown_crash` / `_arm_teardown_clean` (851/855, 871/875) | the two arrays are append-only; every read of a `hits*` name in the file is the *avoid* arm's separate `hits_a`/`hits_b` (604–674) | `nav_lattice_teardown_crash` byte-identical **including** stderr `double free or corruption` and `rc=-6`; `teardown_clean` byte-identical `rc=0` |
| B | `canvas_lattice.gd` | `_notif_keys(d)` (103–110) | **zero call sites** (`grep -n "_notif_keys"` → declaration only) | all 15 canvas rows |
| B | `canvas_lattice.gd` | `var methods` (126) + `methods.append(nm)` (130) | 2 occurrences total, no read | `r98_canvas_census` byte-identical (the arm reports `draw_n` from `drawm`) |
| C | `r98b_attack.gd` | `var owner_ref` (119) + `t.owner_ref = self` (173) | declaration + one dotted write, no read | `r98b_qflush_*`/`qorder_*` rows |
| C | `r98b_attack.gd` | `var pfs` (144) + `pfs.append(...)` (147) | declaration + one append, no read; `QH` is instantiated at 229 and consumed as `h.draws` | same rows |
| D | `r98b_rksenum.gd` | `var _items` (6) + `_items.append(...)` (12) | declaration + one append; the PASS line is printed directly | `r98b_rksenum` byte-identical |
| E | `audio_lattice.gd` | `var prev_t` (161) + `prev_t = now` (176) in `_arm_mixblock` | declaration + one store, no read (r99 LSP measured 2 references: decl + own write) | `r99_audio_mixblock` byte-identical both reps |

## Measurement method (what "byte-identical" was tested against)

- **Staging replica of the harness**: every `corpus/fixtures` entry except `run_battery.py`, project-name munge (`config/name`), `controls/pickup.tscn` copied to root, and the harness's scratch-only `causal_chain.gd` readiness fix — the exact staging block of `run_battery.py:1675–1695`, read but never executed as a battery.
- **Launch shape**: `godot --headless --path <scratch> --script res://<fixture> -- <flags>`, 8 s bound (harness non-export bound), fresh process per row.
- **Production classifier**: `classify_process` extracted **verbatim by AST** from the committed `run_battery.py` and applied with the row's `expected_exit`, signature and allowlist. The per-case allowlists are declared as `{...}.get(name, ())`; an extractor that only accepts `ast.Dict` silently yields an **empty** allowlist and produces 10 false FAILs — that trap is recorded here because it fired in this seat's first pass (§"Extractor caveat").
- **Trees**: `base` (committed bytes, sha-pinned), one tree per candidate fold (`f_nav`, `f_canvas`, `f_attack`, `f_rksenum`, `f_audio`), `f_r98all` (three r98 files), `f_all` (all five).
- **Null-control rule**: a field counts as a fold effect **only if** it is single-valued on the committed side and differs on the folded side. Keys that vary on committed reps are declared load noise.

## Results (receipts: `/var/tmp/r101-simp1/receipts/`)

| check | result |
|---|---|
| rows in scope | **60** (nav 11, canvas 15, r98b_attack 15, r98b_rksenum 1, audio 18) |
| launches | **669** = 387 (main sweep) + 126 (audio sweep) + 36 + 60 + 60 (three focused null-control sweeps) |
| verdicts, base (2 reps) | **60/60 PASS, 60/60 PASS** |
| verdicts, per-candidate fold (2 reps) | **60/60 PASS each** |
| verdicts, `f_r98all` / `f_all` | **60/60 PASS** on both combined trees |
| exit codes base vs folded | **identical on all 60 rows × 2 reps** (incl. `nav_lattice_teardown_crash` `-6` and `r98b_clipmatrix` allowlisted errors) |
| stdout byte-identical (rep1 / rep2) | **49/60 / 49/60**; the 11 differing rows are all declared load-noise tail fields (§null control) |
| stderr classification (120 row-side pairs) | **108 identical, 12 backtrace-line-number-only, 0 other** |
| pinned-field census (every `key=value` in every row signature, every tree/rep) | **0 missing/divergent values** |
| `SCRIPT ERROR:` / `Parse Error:` | **0** |
| timeouts | **0** |

Representative before/after (stdout sha256, prefix-16; rc identical):

| row | exercises | base rep1 | folded rep1 |
|---|---|---|---|
| `nav_lattice_census` | — | `c951e9b92fca5921` | `c951e9b92fca5921` |
| `nav_lattice_teardown_crash` | folded arms A | `b438db5862e33ed7` rc −6 | `b438db5862e33ed7` rc −6 |
| `nav_lattice_teardown_clean` | folded arms A | `e0bdb47c4cf1130d` rc 0 | `e0bdb47c4cf1130d` rc 0 |
| `r98_canvas_census` | fold B (`methods`) | `7756af95dcdaaea6` | `7756af95dcdaaea6` |
| `r98b_rksenum` | fold D | `23f7184276c044e4` | `23f7184276c044e4` |
| `r99_audio_mixblock` | fold E | `ea235e8ada307573` | `ea235e8ada307573` |
| `r99_audio_census` | — | `b752a8d99f2435e0` | `b752a8d99f2435e0` |

### Null control for the 11 non-identical rows (focused, interleaved, serial)

| row | base alone varies? | keys | verdict |
|---|---|---|---|
| `nav_lattice_sync` | yes 2/6 reps | `ladder`, `first_reach` | not a fold effect |
| `r98b_qflush_same_frame` | yes 3/6 reps | `coalesce_draws`, `frames_with_tick`, `ticks_window`, `distinct_draw_pf`, `hide_span_pf` | not a fold effect |
| `r98b_qorder_tree` | yes 5/6 reps | `stagger`, `stagger_off` | not a fold effect |
| `r99_audio_finish` | yes 6/6 reps | `fin_us`, `transition_f`, `fin_frame`, `frames`, `fin_same_frame` | not a fold effect |
| `r99_audio_poly` | yes 2/6 reps | `p1` | not a fold effect |
| `r99_audio_advance` | yes 2/10 reps | `after` (base value set = folded value set) | not a fold effect |
| `r99_audio_gen` | 0/10 but value sets equal on both sides | `skips_dry` | not a fold effect |
| `r99_audio_loop_pts` | 0/10 but value sets equal on both sides | `frames` | not a fold effect |
| `nav_lattice_query`, `_region`, `_agent`, `_avoid`, `_bake`, `_link`, `r98b_qflush_suppress`, `r98b_qorder_flat`, `r98b_epssweep` | yes (rep-to-rep) | declared tail fields | not a fold effect |

The 12 backtrace-only stderr diffs are the declared class: deleting lines shifts `res://<fixture>.gd:<line>` in the GDScript backtrace (`canvas_lattice.gd:436→426`, `nav_lattice.gd:234→233`, `:142→141`). No row pins a line number; the allowlisted `ERROR:` **line itself is byte-identical**, and the allowlist matched on both sides (`dead_entry_count`-equivalent = 0 by construction: classifier green).

### Extractor caveat (recorded so a future seat does not repeat it)

First pass used `ast.literal_eval` on a Dict-valued `Assign`. The harness's real shape is `expected_errors = {...}.get(name, ())` — an `ast.Call` — so the first pass silently got an **empty allowlist** and reported 10 spurious FAILs (`r98_canvas_clip`, `r98_canvas_draw_refusal`, `r98b_clipmatrix`, `nav_lattice_sync`, `nav_lattice_bake`, …). Corrected extractor unwraps `.get(...)`; all verdicts above are recomputed with 82 allowlist entries and 3 `required_stderr` entries, from the same on-disk receipts.

## Line deltas (measured)

| file | base | folded | delta |
|---|---|---|---|
| `nav_lattice.gd` | 882 | 879 | **−3** |
| `canvas_lattice.gd` | 791 | 781 | **−10** |
| `r98b_attack.gd` | 822 | 818 | **−4** |
| `r98b_rksenum.gd` | 68 | 65 | **−3** |
| `audio_lattice.gd` | 773 | 771 | **−2** |
| **total** | | | **−22** |

**Delta arithmetic note (calibration):** the r98 report states "F1–F4/F6 (−19 lines)", but its own per-file numbers are canvas −10 + attack (F3+F4) −4 + rksenum −3 = **−17** (attack −25 includes F5 −21; 10 + 4 + 3 = 17). The queued "−19" is a 2-line slip in that report, not a missing fold: every cited site was applied and the file deltas match the report's per-file counts exactly (`canvas −10`, `rksenum −3`, `attack −25−F5`). The r99 queue entry "−2" counts **folds** (F1 −2 lines + F2 −1 line), not lines.

## Ready-to-apply diffs (also on disk under `reports/round-101/mutations/`)

`git apply --check <file>` succeeds for every patch at lane HEAD; the combined
`r101-simp1-all.patch` applied to a scratch copy reproduces the folded trees byte-for-byte
(`b23887e5…`, `8bfddb74…`, `7021e53c…`, `5d7e3aab…`, `91161bf5…`).

### 1. `r101-simp1-r91-nav_lattice.patch` — −3 (hunk bodies identical to r91's in-repo proposal)
```diff
--- a/corpus/fixtures/nav_lattice.gd
+++ b/corpus/fixtures/nav_lattice.gd
@@ -53,7 +53,6 @@
 #    navmesh silently.
 #  - map_get_random_point() is random per call (not pinnable).
 
-const SETTLE := 10
 const SYNC_BOUND := 48
 
 var _exit_code := 0
@@ -848,11 +847,10 @@
 func _arm_teardown_crash() -> void:
 	var map := _new_map()
 	var a := NavigationServer2D.agent_create()
-	var hits: Array[Vector2] = []
 	NavigationServer2D.agent_set_map(a, map)
 	NavigationServer2D.agent_set_avoidance_enabled(a, true)
-	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
-		hits.append(v))
+	NavigationServer2D.agent_set_avoidance_callback(a, func(_v: Vector2) -> void:
+		pass)
 	await _await_frames(3)
 	print("NAV_LATTICE_TEARDOWN_CRASH armed=live_cb has_cb=",
 		NavigationServer2D.agent_has_avoidance_callback(a))
@@ -868,11 +866,10 @@
 func _arm_teardown_clean() -> void:
 	var map := _new_map()
 	var a := NavigationServer2D.agent_create()
-	var hits: Array[Vector2] = []
 	NavigationServer2D.agent_set_map(a, map)
 	NavigationServer2D.agent_set_avoidance_enabled(a, true)
-	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
-		hits.append(v))
+	NavigationServer2D.agent_set_avoidance_callback(a, func(_v: Vector2) -> void:
+		pass)
 	await _await_frames(3)
 	NavigationServer2D.agent_set_avoidance_callback(a, Callable())
 	await _await_frames(1)
```

### 2. `r101-simp1-r98-canvas_lattice.patch` — −10 (F2 helper, F1 accumulator)
```diff
--- a/corpus/fixtures/canvas_lattice.gd
+++ b/corpus/fixtures/canvas_lattice.gd
@@ -100,14 +100,6 @@
 func _col(c: Color) -> String:
 	return "%.4f,%.4f,%.4f,%.4f" % [c.r, c.g, c.b, c.a]
 
-func _notif_keys(d: Dictionary) -> String:
-	var keys: Array = []
-	for k in d.keys():
-		if int(d[k]) != 0:
-			keys.append(int(k))
-	keys.sort()
-	return "[%s]" % ",".join(keys)
-
 # --------------------------------------------------------------- census
 
 func _arm_census() -> void:
@@ -123,11 +115,9 @@
 	for p in ClassDB.class_get_property_list("CanvasItem", true):
 		props.append(str(p.get("name")))
 	_it("props", ",".join(props))
-	var methods: Array = []
 	var drawm: Array = []
 	for m in ClassDB.class_get_method_list("CanvasItem", true):
 		var nm := str(m.get("name"))
-		methods.append(nm)
 		if nm.begins_with("draw_"):
 			drawm.append(nm)
 	_it("draw_n", str(drawm.size()))
```

### 3. `r101-simp1-r98-r98b_attack.patch` — −4 (F3, F4)
```diff
--- a/corpus/fixtures/r98b_attack.gd
+++ b/corpus/fixtures/r98b_attack.gd
@@ -116,7 +116,6 @@
 
 class QF:
 	extends Node2D
-	var owner_ref
 	var q_pending := false
 	var q_every := false
 	var queue_from_draw := false
@@ -141,10 +140,8 @@
 class QH:
 	extends Node2D
 	var draws := 0
-	var pfs: Array = []
 	func _draw() -> void:
 		draws += 1
-		pfs.append(Engine.get_process_frames())
 
 class QHC:
 	extends Node2D
@@ -170,7 +167,6 @@
 
 func _arm_qflush() -> void:
 	var t := QF.new()
-	t.owner_ref = self
 	t.set_physics_process(true)
 	root.add_child(t)
 	await _frames(1)
```

### 4. `r101-simp1-r98-r98b_rksenum.patch` — −3 (F6 + its vacated blank line)
```diff
--- a/corpus/fixtures/r98b_rksenum.gd
+++ b/corpus/fixtures/r98b_rksenum.gd
@@ -3,13 +3,10 @@
 # claimed R*K*S product differs from the engine's Transform2D(r, s, k, p).
 # Not part of the batch matrix; receipts land in runs/rksenum/.
 
-var _items: PackedStringArray = []
-
 func _initialize() -> void:
 	_run.call_deferred()
 
 func _it(key: String, value: String) -> void:
-	_items.append("%s=%s" % [key, value])
 	print("R98BRKS %s=%s" % [key, value])
 
 func _tm(t: Transform2D) -> String:
```

### 5. `r101-simp1-r99-audio_lattice.patch` — −2 (F1)
```diff
--- a/corpus/fixtures/audio_lattice.gd
+++ b/corpus/fixtures/audio_lattice.gd
@@ -158,7 +158,6 @@
 	var jumps: Array[float] = []
 	var wall: Array[float] = []
 	var prev := -1.0
-	var prev_t := Time.get_ticks_usec()
 	var last_jump_t := Time.get_ticks_usec()
 	var frames := 0
 	while Time.get_ticks_usec() - t0 < 700000 and frames < 900:
@@ -173,7 +172,6 @@
 			wall.append(float(now - last_jump_t) / 1000000.0)
 			last_jump_t = now
 		prev = pos
-		prev_t = now
 	var period := AudioServer.get_time_since_last_mix() + AudioServer.get_time_to_next_mix()
 	var block := 4096.0 / 44100.0
 	var jmax := 0.0
```

## Landing follow-ups (in-repo text that becomes stale — orchestrator owns `run_battery.py`)

1. `run_battery.py:1283` cites `canvas_lattice.gd` sha256 `866480a1…` → becomes `8bfddb74…`.
2. `run_battery.py:1284` cites `r98b_attack.gd` sha256 `2e71c715…` → becomes `7021e53c…`; the r98 block header's "BYTE-COPY" wording becomes "byte-copy minus the declared folds".
3. `run_battery.py:1408–1410` cites `audio_lattice.gd` sha `165571c4…` (→ `91161bf5…`) and says "It is deliberately NOT folded" — false after this patch; rewrite per the r95/r99 precedent.
4. `r98b_rksenum.gd` has no sha citation in the harness (only "the one-off"), nothing to restate.
5. `nav_lattice.gd`: `run_battery.py:542` cites the **scout probe** sha `efb496e5…`, not the landed fixture sha → unchanged. `reports/round-91/r91-author.md:19` and `corpus/live/r91-author/manifest.sha256` cite `088843399…` (historical receipts; the r91 simplifier already recorded this cost).

## Out of this half's scope — hand-off

| item | file | delta | why handed off |
|---|---|---|---|
| r99 F2 `pairs` in `_arm_splitcycle` | `r99b_modes.gd` | −1 | second alphabetical half |
| r100 SP2 `--arm` parse + SP3 `arm` carrier | `r100b_seq.gd` | −5 | second alphabetical half |
| r100 SP1 duplicate crash rows | `run_battery.py` | −1 line / −2 rows | shared registry file; already deduped upstream at `9ede7c50` |
| r99 F3 (28 × `stream = null`) | `audio_lattice.gd` | −28 | not in the queued count (−2 = F1+F2); r99's own scope caveat (observational, not semantic) — operator call |
| r98 F5 `--arm=env` arm | `r98b_attack.gd` | −21 | explicitly dropped from the queue for the byte-copy chain |

## Rejected / not folded (with reason)

- **r98 F5 arm removal** — the r98 report's own tradeoff paragraph names it as the fold to drop; observed `--arm=env` is unauthored (no CASES row), so removal would be behaviour-neutral, but it breaks the frozen-probe launch-mode receipt chain.
- **Decorating the folded lines with "folded" comments** — a new convention; the patches are deletions only, restating provenance belongs in the harness comment (follow-up 1–3).
- **r91 SP2 alternative (`pass` vs. empty lambda)** — kept the r91 patch's exact shape (`func(_v) -> void: pass`) so the landed bytes equal r91's proven folded sha.
- **r99 SP1/SP2/SP3, r100 SP5–SP10** — already refuted by their own rounds (instruments/provenance); no weight to reclaim here.
- **Anything outside `corpus/fixtures/` first half** — out of seat scope by construction.

## Residual risks / honest limits

- The null control is **statistical** for `r99_audio_gen`/`loop_pts`: 10 interleaved reps produced equal single values on both sides after an earlier one-sided sample; no fold effect is visible, but a rarer scheduling mode cannot be excluded at this sample size.
- All proof is at the **battery launch shape** (headless, Dummy renderer/audio, 60 tps) under loadavg ≈40. The audio fields are wall-clock; the verdicts that pin them are predicates (`skips_dry_gt0=true`, `pos_after_gt_before=true`), which stayed green on every launch.
- The added `_v` parameter rename (`v`→`_v`) is a GDScript unused-parameter convention; it is part of r91's proven patch, not a new convention.
- `git status` shows other seats' untracked round-101 files (`export_prod_s0*.gd`, `r101_seqfull.gd`, `r101_ytrans.gd`, `corpus/live/r101-*`); this seat wrote none of them and read none of them.
- This seat did **not** run `corpus/fixtures/run_battery.py` (hard rule). The battery-level claim is therefore an aggregate of per-row production-classifier verdicts, not a full-battery run; integration must run it once.

## Receipts (`/var/tmp/r101-simp1/`)

`simp1.py` (staging + folds + AST extraction), `run.py` (main + audio sweeps), `focused.py`/`focused2.py`/`focused3.py` (null-control sweeps), `analyze2.py` (verdicts + masks + pinned-field census), `mkpatch.py` (diff generator), `trees/` (7 staged trees), `receipts/` (all stdout/stderr/rc files), `results*.json`, `analysis2.json`, `focused*.json`. Patches in-repo at `reports/round-101/mutations/r101-simp1-{r91-nav_lattice,r98-canvas_lattice,r98-r98b_attack,r98-r98b_rksenum,r99-audio_lattice,all}.patch`.

— r101 SIMP-1, seat output; the canonical runtime judges.
