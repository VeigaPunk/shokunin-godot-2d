# r79 VERIFIER — live falsification probes (mutation-tester, exec-capable)

Seat `VERIFIER`/`mutation-tester` (LEAF) | lane `g2d` | round 79 | host **devin**.
Runtime Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), LÖVE 11.5,
Python 3.14.7, 32 cores, Linux. HEAD `884a4c4` + r79 dirty landing
(` M corpus/fixtures/run_battery.py` sha256 `9cb52531…`,
`?? corpus/fixtures/phys2d_events.gd` sha256 `7329acb2…` — both match the
author/baseline-pinned digests; verified before and after all probes).

Scope: the five NOT-RUN probes of `r79-boundary.md` **plus** the dispatch's
minimum harness set (a)–(e). All mutations applied to **scratch copies** under
`corpus/live/r79-verify/`; the tracked tree was never modified (restoration
evidence §4). Nothing here judges; findings are coverage data for the L1.

| probe | mutant / challenge | verdict |
|---|---|---|
| (a) 88-row byte-stability, second run | none — pristine detector re-run | **PASS** |
| (b) forged signature fails closed | `cb_count=2`→`cb_count=3` in `phys2d_events_cm_on` CASES pin | **PASS (killed)** |
| (c) detached-descendant 8s razor under load | 4/12/20 CPU-pinned spinners + injected +4.5 s check delay | **PASS (fails closed; load finding F2)** |
| (d) expected_errors on refusing cells | none — direct arm runs, split streams | **PASS** |
| (e) CASES-row removal locality | delete `phys2d_events_cm_on` row | **PASS** |
| B1 cb_count/cb_colliders falsification | second overlapping static body in `cm_on` | **PASS — pin falsified (load-bearing)** |
| B2 deferred-write reorder | `set_deferred("global_position", (700,700))` inside `rb_node_position` cb | **PASS + finding F1** |
| B3 rb_queue_free stability / free() split | `queue_free()`→`free()` | **PASS — split confirmed** |
| B4 foreign-space DSS bypass | `space_create()` + foreign `intersect_point` inside cb | **PASS — available, sees own space only** |
| B5 love.errorhandler fatal cell | none — direct `bc_setpos_unp` run | **PASS** |

---

## (a) prior-88-row byte stability on a second identical run — **PASS**

Detector: `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/run_battery.py
--runs corpus/live/r79-verify/runs-clean` → rc=0, **111/111 PASS**
(`runs-clean/20261015T050805946857Z/verdicts.json`, sha `4f8fbddb…`, stderr 0 B).
Compared with the baseline seat's own `compare.py godot`:

- vs frozen rep1 `…T235028993722Z` and rep2 `…T235235106974Z` (88 rows each):
  `common=88 new_only=23 old_only=0`, **tuple_mismatches=0 on all 81 prior
  seeded rows**; `new_only` is exactly the 23 `phys2d_events_*` rows.
- Single meta tuple diff: `probe_error_clause_surface` — the *declared* census
  change (`rows_with_expected_errors` 39→43, `ERROR:_per_line_lines` 41→53);
  verdict PASS, all 34 discriminations true.
- `output-normalized differing=2`: `export_preset_missing`/`export_readiness`
  `(28 steps)`→`(29 steps)` — the +1 script file banner; declared volatile.
- vs author run A (`…T045301196389Z`, 111 rows): **tuple_mismatches=0 and
  output-normalized identical 104/104** — a third-seat run reproduces the
  author's byte-for-byte.

Receipts: `battery-clean.stdout/.stderr/.rc`, `probe-a-compare.txt`,
`godot-tuples-clean.txt`, `runs-clean/20261015T050805946857Z/`.

## (b) deliberately forged signature line fails a pinned row closed — **PASS (mutant killed)**

Mutant: scratch copy `fix-forge/run_battery.py` (sha `e0a49060…`), one token —
`phys2d_events_cm_on` pinned signature `cb_count=2` → `cb_count=3` (a
signature the fixture never emits).

- Command: `python3 -B fix-forge/run_battery.py --runs …/runs-forge` → **rc=1**.
- Output head: `FAIL phys2d_events_cm_on: exit=0 signature='…cb_count=3…'`;
  110 `PASS` lines; final `FAIL battery: …/verdicts.json` (sha `3e8bff2f…`).
- `fails=['phys2d_events_cm_on']` — exactly the forged row; `actual_exit=0`,
  `error=None`: the run itself was clean, the **signature clause alone** killed
  it. All 7 meta probes still PASS → zero cascade.

The pin is load-bearing in the fail direction: a wrong expected signature
cannot PASS. (The dual — signature presence is origin-blind — remains the
tracked `descendant_pipe_forged_signature_release` row + spoof/while-live meta
verdicts, PASS in the clean run.)

Receipts: `battery-forge.stdout/.stderr/.rc`, `runs-forge/…/verdicts.json`,
`fix-forge/run_battery.py`.

## (c) detached-descendant 8 s razor under load — **PASS, fails closed (margin measured)**

Mechanism: `descendant_pipe_detached_control` spawns `exec sh -c 'sleep 8'`;
`probe_descendant_pipe_eof` samples `pid_alive()` after the forged-release row
+ two compute metas + the 3.0 s hold-arm bound. Detector: `fix-razor/` —
trimmed CASES = the exact razor segment (`save_process×3`, `crash×2`,
`detached`, `forged_release`) with `ROW_TS`/`RAZOR_TS` monotonic stamps. The
trim removes only rows that sit *before* the spawn; the spawn→check pipeline is
byte-identical to the full battery's. Trimmed idle run: 14/14 PASS.

| run | row_done→check Δ | est. spawn→check | `orphaned_alive` | eof verdict |
|---|---|---|---|---|
| idle | 3.912 s | ≈4.4–4.8 s | true | PASS (≈ author's ~4.6 s) |
| 4 spinners, cpu31 | 4.514 s | ≈5.2–6.0 s | true | PASS |
| 12 spinners, cpu31 | 5.347 s | ≈6.0–7.5 s | true | PASS |
| 20 spinners, cpu31 | 6.785 s | ≈7.1–7.7 s | **true** | **FAIL** (see F2) |
| injected `sleep(4.5)` | 8.358 s | ≈8.9–9.2 s | **false** | **FAIL** |

- **Razor trip, isolated**: `fix-razor2` adds one `time.sleep(4.5)` before the
  liveness sample → `detached_descendant_orphaned_alive=false`, eof **FAIL**;
  every *other* discrimination stayed true. Cascade: `probe_error_clause_surface`
  FAIL — the same two-row failure signature as the inherited pre-reorder run1.
  RC=1: a timing violation is surfaced as FAIL, never silently absorbed —
  the razor is real and fails closed.
- **Under real load on this host the razor was NOT tripped** up to 12:1 core
  oversubscription; the fixed 3.0 s hold bound is load-immune and the spawn
  itself shifts late under contention. The author's "a heavily contended host
  could still lose it" stands, but the observed margin is larger than implied.
- **F2 (coverage finding)**: at 20 spinners the battery fails *before* the
  razor clause matters — the hold arm's Godot child is still alive at the 3.0 s
  bound (`child_exit_at_timeout=None`, `elapsed=3.427`), flipping
  `hold_timed_out_with_child_dead`/`hold_post_exit_write_captured` and
  cascading into signature-spoof/while-live/error-spoof/surface FAILs while
  `detached_descendant_orphaned_alive` stays **true**. Load degradation order:
  hold-arm starvation first, razor second.

Receipts: `razor-{idle,load,load12,load20,delay}.stdout/.stderr`,
`timing-summary.txt`, `runs-razor-*/…/verdicts.json`, `fix-razor{,2}/run_battery.py`
(shas `d88515f7…`, `ecce89d2…`).

## (d) expected_errors prefixes appear in stderr on the refusing cells — **PASS**

Each of the 4 r79 `expected_errors` keys run standalone, streams split:

| arm | rc | stderr content (stripped lines) | pinned entries found |
|---|---|---|---|
| `cm_toggle_cb` | 0 | `Can't disable contact monitoring during in/out callback…` ×1 + backtrace | exact ×1 |
| `rb_free_rid` | 0 | `Parameter "body" is null.` ×4, `Invalid ID.` ×1 | exact, claimed multiplicities |
| `area_monitoring_direct` | 0 | `Function blocked during in/out signal…` ×1 + backtrace | exact ×1 |
| `area_free_rid` | 0 | `Parameter "body" is null.` ×4, `Invalid ID.` ×1 | exact |

`probe-d-check.txt`: `ALL_ENTRIES_FOUND_ON_STDERR: True` under the classifier's
own exact-strip semantics. The refusal texts are not cross-borrowed, and the
entries sit on **stderr** (engine error path), reaching the classifier only via
the merged-output scan — the allowlist is exercised, not decorative.

Receipts: `arm-*.stdout/.stderr`, `probe-d-check.txt`.

## (e) removing one CASES row flips only that row's verdict — **PASS**

Mutant: `fix-drop/run_battery.py` (sha `c836c563…`), the 2-line
`phys2d_events_cm_on` tuple deleted.

- `python3 -B fix-drop/run_battery.py --runs …/runs-drop` → rc=0, **110 rows,
  verdict PASS** (sha `c68aceec…`).
- vs the clean run: `missing=['phys2d_events_cm_on']`, `added=[]`, **0 tuple
  diffs on all 110 common rows** — every other row byte-stable, all 7 meta
  probes unchanged (the removed row carried no `expected_errors`, so the
  surface census is untouched; it sits before the detached tail, so the razor
  segment is untouched).

Receipts: `battery-drop.stdout/.stderr/.rc`, `probe-e-diff.txt`,
`runs-drop/…/verdicts.json`, `fix-drop/run_battery.py`.

---

## Boundary-report probes 1–5 (the original NOT-RUN five)

### B1 — cb_count/cb_colliders falsification — **PASS: pin is load-bearing**

Mutant `mut/phys2d_events_b1.gd` (`c3add2d5…`): one extra `StaticBody2D`
(40×40) overlapping `FloorA`'s spot — the faller is born contacting two
colliders.

- Pristine (restored bytes, sha-verified): `entered=2 … entry2_frame=20
  cb_count=2 cb_colliders=1 …` — byte-exact to the CASES pin.
- Mutant, 3/3 deterministic: `entered=2 exited=1 entry1_frame=1
  **entry2_frame=0** … **cb_count=4** cb_colliders=1 …`.
- `cb_count` is the manifold contact-point count (2→4 with the second
  collider); entry frames **do** shift (20→0 — the second body is overlapped
  from spawn, so `_wait_for` sees the second entry immediately; the pinned
  `entry2_frame=20` was the *FloorB* landing after the floor teleports).
  `cb_colliders=1` holds because `_in_cb` is captured on the first contact
  before the second collider registers. Under the battery this output FAILs
  the pinned signature — falsification succeeds by construction, as the
  boundary note predicted.

### B2 — deferred-write reorder — **PASS + finding F1**

Mutant `mut/phys2d_events_b2.gd` (`1cb6a30f…`): keeps the in-cb immediate
write `(600,600)` and adds `set_deferred("global_position", Vector2(700,700))`
inside `rb_node_position`'s callback.

- 3/3 deterministic: `cb_node_read=(600.0, 600.0)` (in-cb immediate write still
  reads back) but `next_node=(700.0001, 701.0889)`,
  `next_srv=(700.0001, 701.0889)`, `late_node=(700.0006, 716.2971)` — the
  deferred write **lands durably**: applied at frame end *after* the locked
  window, it propagates node→server (the body itself teleports to 700) and the
  body keeps falling from there.
- **F1 (coverage finding)**: the pinned "reverted" class is window-scoped.
  An immediate node write inside `body_entered` is reverted (the pin holds);
  the same write via `set_deferred` escapes the revert window entirely and
  behaves like an ordinary out-of-window node write. This is not a reorder of
  the *in-cb* write — it is the engine-prescribed remedy doing exactly what
  the refusal texts tell you to do. No pin moves; the escape hatch is real.

### B3 — rb_queue_free 20-rep + immediate-free split — **PASS**

- Pristine, 20 fresh processes (`b3-queuefree-20rep.txt`): **20/20
  byte-identical** `…next_node=<dead> … valid_after=false cb_queued=true`,
  zero ERROR lines.
- Mutant `mut/phys2d_events_b3.gd` (`f48b151d…`): `_faller.free()` —
  3/3 deterministic: `ERROR: Object is locked and can't be freed.`
  (`object.cpp:787`) + `SCRIPT ERROR: Attempted to free a locked object
  (calling or emitting).`; the body **survives**
  (`valid_after=true`, keeps falling `(0.000128,-4.672004)→-4.699955`),
  `cb_queued=-` (the post-free assignment never runs — the script error aborts
  the callback body). Immediate free inside the window is **refused with a
  SCRIPT ERROR**, a different class from queue_free's deferred destroy — the
  split is real, and under the classifier it fails on three clauses at once
  (signature, unallowlisted ERROR, SCRIPT ERROR).

### B4 — foreign-space DSS bypass inside the cb window — **PASS**

Mutant `mut/phys2d_events_b4.gd` (`556f7dd6…`): inside `rb_dss_in_cb`'s
`body_entered`, `space_create()` a second space, activate it, fetch its DSS,
run the same point query.

- 2/2 deterministic, no ERROR/SCRIPT lines: `cb_foreign_dss_null=false
  cb_foreign_q_hits=0` alongside the pinned `cb_dss_null=false cb_q_hits=1`.
- A foreign space's direct state **is** obtainable and queryable inside the
  locked window — no gate on the query path itself — but it sees only its own
  (empty) membership. There is no bypass to the world space's contents; the
  boundary is space membership, not DSS availability. The pinned
  `cb_q_hits=1` stands for the world space.

### B5 — `love.errorhandler` on the fatal cell — **PASS (live)**

The fixture uses the **default** handler (no `love.errorhandler` in
`love_phys_probe/main.lua`). Direct run in the battery's exact shape:

- Command: `IW_CELL=bc_setpos_unp timeout 30 love proj/love_phys_probe` →
  **rc=1**, stderr **0 bytes**.
- stdout tail: `Error: main.lua:321: Box2D assertion failed:
  m_world->IsLocked() == false` + `stack traceback:` containing
  `[C]: in function 'setPosition'`, `main.lua:321: in function 'do_mutation'`,
  `… in function 'update'`, `[C]: in function 'xpcall'`.
- All three audit conditions measured live: (a) handler prints to **stdout**
  (`err_on=stdout` pin ✓), (b) traceback contains `in function 'setPosition'`
  (`esc_fn` ✓), (c) process exits **1** ✓. The pre-death `evpin`/`fire`
  receipts (`fire cb=bc kind=setpos_unp step=73 … locked=true`) precede the
  traceback on the same stream.

Receipts: `b5-setpos.stdout/.stderr`.

---

## 4. Restoration / hygiene evidence

- Tracked tree never modified by this seat: `git status --porcelain --
  corpus/fixtures/` shows only the inherited r79 dirt (` M run_battery.py`,
  `?? phys2d_events.gd`, `?? __pycache__/*.pyc` — pre-existing).
- Digests re-verified after all mutations: `run_battery.py` `9cb52531…`,
  `phys2d_events.gd` `7329acb2…` (both = pre-probe), `descendant_pipe_probe.gd`
  `c86bda84…`. Arm-probe scratch `proj/phys2d_events.gd` restored to
  `7329acb2…` after every mutant (sha-checked after B1–B4).
- Mutants lived only in `corpus/live/r79-verify/{mut,fix-forge,fix-drop,
  fix-razor,fix-razor2}/` (before/after shas recorded per probe).
- No stray `sleep 8`/`sh` descendants left (harness reaps; `pgrep` clean);
  load spinners SIGKILLed after each razor run.
- All runs wrote only inside `corpus/live/r79-verify/` (each battery run gets
  its own stamped `run_dir` + private `xdg-data`).

## 5. Findings (coverage data, not contract changes)

- **F1** — the `reverted` class for in-cb node writes is window-scoped: a
  `set_deferred` node write lands durably and crosses node→server. Consistent
  with the refusal texts' prescribed remedy; worth one sentence in the
  lattice doc if a future round touches it.
- **F2** — under 20:1 single-core oversubscription the descendant meta stack
  fails on **hold-arm starvation** (child alive at the 3.0 s bound) before the
  8 s `orphaned_alive` razor can trip; the razor clause itself stayed true up
  to ≈7.7 s measured. Ordering claim "razor is the weak link" is inverted on
  this host: the 3 s hold bound is the weaker link.

## 6. Honest ledger

- Probe (c)'s razor trip is demonstrated by an *injected* check delay plus
  real-load margin measurement, not by real load alone — 20 spinners starved
  the hold arm first (that is itself the honest load result).
- B4's "bypass" answers only what the fixture could express: foreign-space
  queries work in-cb but see foreign membership only.
- Razor timing instrumentation (`ROW_TS`/`RAZOR_TS` prints) is additive-only
  in the scratch copy; razor logic untouched.
- Claims bounded to this host, Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
  LÖVE 11.5, `--headless`, DEFAULT 2D backend.

**All five dispatch probes and all five boundary probes executed with
receipts. No pin refuted; two coverage findings recorded. Seat output
complete.**
