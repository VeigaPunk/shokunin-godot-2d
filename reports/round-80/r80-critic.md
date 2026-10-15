# game-dev-2d round 80 — critic (g2d): adversarial audit of the `phys2d_motion` landing

Seat `CRITIC` (LEAF) | lane `g2d` | round 80 | wave `shokunin-train-20261101-w19` | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`d9320dd`** + the dirty landing
(`M corpus/fixtures/run_battery.py`, `?? corpus/fixtures/phys2d_motion.gd`). **No git
mutation, no tracked edits.** Scratches under `corpus/live/r80-critic/` only.

**Verdict line:** the landing is insertion-clean, mechanism-faithful, and drift-free — my own
tracked-battery rep is **139/139** with **zero** per-row drift vs author rep 2 — but the
landing **re-opens the r79 C2 hole for the new `phys2d_motion_*` prefix**: the dead-entry
gate `phys2d_expected_errors_all_matched` is scoped `startswith("phys2d_events_")` and never
covers the two new whitelist entries (**C1, demonstrated live: 139/139 with a dead entry**).
Separately, **`ccd_edge` is a claim-bearing absence cell that never witnesses its own
premise** — byte-identical output with a fully inert wall (**C2, demonstrated live**).
`ccd_spin`'s declared weakness is quantified (C3, demonstrated, advisory). The strongest
vacuity candidate (`btm_from2` `srv_tele`) was tested and **killed** — the cell is real.

---

## 1. Counterexamples

### C1 — dead-entry floor gate does not cover `phys2d_motion_*` *(fixable defect, demonstrated)*

`run_battery.py:2161-2165`:

```python
"phys2d_expected_errors_all_matched": all(
    not e["dead_in_run"]
    for r in census_rows
    if r["case"].startswith("phys2d_events_")   # <-- new prefix falls outside
    for e in r["entries"]),
```

The r79 C2 fix gates *dead allowlist entries* — but only for `phys2d_events_*` rows. The two
new `phys2d_motion_*` `expected_errors` entries are **censused (dead_in_run recorded as data)
and never gated**. Nothing else gates them either: `census_bare_classifier_consistent` and
`census_allowlisted_reproduces_verdicts` are consistency conjuncts that stay true with a dead
entry present.

**Live forge** (`corpus/live/r80-critic/forge/` = fixtures copy + patched `phys2d_motion.gd`
+ copied `run_battery.py`, full tracked battery run `runs-forge/20261015T061606758179Z`):
`dss_wrongarg` was patched to pass a *valid* far-away `PhysicsPointQueryParameters2D` to
`intersect_point` — modeling an engine regression where the null-param typed refusal is
silently tolerated. Result:

- Row output byte-identical to the pin (`pt_null=0`, signature satisfied); **6** ERROR lines
  emitted instead of 7 — `rp_point_query` never emitted → whitelist entry dead.
- `phys2d_motion_dss_wrongarg` → **PASS**; `phys2d_motion_ccd_spin` (separately forged, §C3)
  → **PASS**; **battery 139/139, all 7 meta rows PASS**.
- Census correctly records `dead_entry_count=1`, `dead_entries=[phys2d_motion_dss_wrongarg:
  "ERROR: Required object \"rp_point_query\" is null."]` — as **data** — while
  `phys2d_expected_errors_all_matched: true` and `probe_error_clause_surface` → **PASS**.

An error-removal regression inside `dss_wrongarg` (or `mac_maxcol`, whose signature
`callv5=null bodypos=(0,0)` is equally satisfiable by a silently-swallowing `callv`) launders
through every gate. The r79 C2 defect is re-opened under a new prefix.

**Smallest safe correction:** `run_battery.py:2165` widen `startswith("phys2d_events_")` →
`startswith("phys2d_")` (covers both families, preserves the r79 gate shape). Stronger,
equally safe on today's census (0 dead entries): gate `dead_entry_count == 0` over the whole
census — but that newly binds all 45 rows, so the prefix extension is the minimal-diff move.

### C2 — `ccd_edge` never witnesses that the wall can collide *(fixable defect, demonstrated)*

`_arm_ccd_edge` pins `d/r/s_cross=1` + `d/r/s_hit=0` + positions — a pure **absence**
signature. Unlike `ccd_gap` (`r_hit=2` is a positive wall-contact witness) or even the
weak-labeled `ccd_spin` (`endpose_overlap=[1,1,1]` proves via motion-0 `body_test_motion`
that the rest pose genuinely overlaps the wall), `ccd_edge` contains **no cell proving the
wall obstructs anything**. The claim text says "misses a **real** edge clip" — the premise is
asserted by geometry reasoning, never exercised.

**Live forge** (`proj/phys2d_motion.gd`, `ccd_edge` walls patched `collision_layer=0` /
`collision_mask=0`; receipt `ccd_edge-inertwall.txt`): output is **byte-identical** to the
pinned signature — `d_cross=1 d_hit=0 d_pos=(1169.4938,814.0000) … s_pos=(…,2414.0000)`.
A build where the wall is inert, miscollided, or never spawned passes this row verbatim.
Wrong-mechanism equivalence: the row cannot distinguish "cast_shape missed a real swept clip"
from "no collision was possible".

**Smallest safe correction:** add one positive witness inside the arm and pin it — e.g. a
fourth low-speed lane the wall stops (`d`-mode `hit=1`), or a `body_test_motion` overlap
assertion at a mid-path pose (the same trick `ccd_spin` uses for `endpose_overlap`).
One lane or one query; the pin then carries the premise.

### C3 — `ccd_spin` is blind to its own witness channel *(declared weak; quantified)*

Forge: `body_entered` connect commented out in `_arm_ccd_spin` only. Output **byte-identical**
(`d_hit=0 … endposes=[308.05,308.05,308.05] endpose_overlap=[1,1,1]`); in the forged battery
the row PASSes. The absence signature cannot distinguish "no contact detected" from "nothing
was listening". This is the *declared* weakness — the label is earned. Coverage analysis:
contact-reporting regressions are still caught elsewhere (`ccd_gap r_hit=2`,
`ccd_ladder entries=17`, `cont_windows/cap/persist`, `bds_windows in_cb`), and
`endpose_overlap` does witness the wall premise — so the cell's premise-witness is actually
stronger than `ccd_edge`'s. Residual, for the record: **no row anywhere carries a positive
rotational-contact witness** — a regression that selectively kills entry reporting for
rotating bodies is invisible to the whole battery. Advisory only; consistent with the
scout's own §7 disclosure.

## 2. Counterexamples killed / verified clean

- **`btm_from2` `srv_tele` is NOT vacuous** — `tele_probe.gd` (receipt `tele-probe.txt`):
  `body_set_state(BODY_STATE_TRANSFORM)` on a CharacterBody2D is *buffered* (immediate
  read-back still old) but **lands next physics frame and persists** (`srv=(0,4200)` at T+1f
  and T+5f) while the node never follows (`node=(0,0)` forever — kinematic node↔server
  split). At query time the server pose was genuinely (0,4200); the unset-`from` query still
  hit `pt=(198,0)`. The leg discriminates. `b3pos=(0,0)` documents the split, not a failure.
- **`expected_errors` ceiling byte-exact**: author's rep-2 output shows `dss_wrongarg` emits
  exactly 7 ERROR lines (5×`rp_shape_query`, 1×`rp_ray_query`, 1×`rp_point_query`) and
  `mac_maxcol` exactly 1 — each byte-matching its whitelist entry (exact-match form, no `,`
  prefix). My clean rep reproduces the same error-line sets. No line uncovered, no entry
  over-broad. Scout's "4× rp_shape_query" is loose wording — actual is 5 (the
  `intersect_shape` site fires twice: wrong-typed `:735` and null `:739`, same anchor
  `physics_server_2d.cpp:388`); harmless doc imprecision.
- **Insertion-only + no prior-111 drift** — `git diff` = +66/−0 (`:149–214`) + +4 (`:581–584`).
  Row order: `phys2d_events` ends idx 99, motion rows idx 100–127, crash/descendant tail
  128–131 — the `sleep 8` descendant window has nothing inserted inside it; my run's
  `probe_descendant_pipe_eof` discriminations all true. **139/139 on my own rep**
  (`runs/20261015T061856932497Z`), and vs author rep 2: verdict/exit/signature identical on
  **all** rows, error-line sets identical, **28/28 motion outputs byte-identical**.
  `rows_with_expected_errors` 43→45 is the declared content growth; `dead_entry_count=0` in
  the clean run.
- **Signature tokens are all live readbacks** — every pinned token in all 28 arms is a `%s`
  substitution of measured state (mode readbacks `*_ccd`, hit counters, positions, server
  transforms via `body_get_state`, dict-key censuses). No canned constants. Unknown arm →
  `_fail` exit 1 + no signature. `--arm=` absent → same. 8 s bound per row; `cont_*` while
  loops bounded at 200 frames and their `-1` fallbacks break the pins, not satisfy them.
- **Fixture code is byte-identical to the scout's measured probe** — comment-stripped diff is
  empty; the 3 diff hunks are all inside the header comment block (`:2–37`), including the
  added per-arm class labels and the two previously-omitted arms (`btm_from2`, `btm_recflag`).
- **Mechanism witnesses that DO work**: `ccd_ladder` `r_ccd=1/s_ccd=2` readbacks + distinct
  stop positions (`r_x=90.16` vs `d_x=90.3`) would catch a cast_ray→disabled silent fallback;
  `ccd_gap r_hit=2` catches a severed monitor or inert wall; `btm_from`/`btm_from2` pin both
  the origin-query hit and the empty-lane miss (`with_from`, `with_from3600`);
  `mac_test_only` reads the server tier; `mac_rigid` reads server pose ×3 frames;
  `dss_purity` prints param contents, so a by-reference `exclude` mutation would still show.
- **Minor note (not a defect)**: the `R80 arm=… engine2d=DEFAULT separate_thread=…` header is
  printed but not pinned — a backend flip producing identical pins is invisible to the rows.
  Harmless today (no Jolt-2D in this build's 2-D hint); a future probe could fold the header
  into the signature substring.

## 3. Evidence index

| artifact | content |
|---|---|
| `corpus/live/r80-critic/runs/20261015T061856932497Z/verdicts.json` | my clean tracked-battery rep: **139/139**, zero drift vs author rep 2 |
| `corpus/live/r80-critic/runs-forge/20261015T061606758179Z/verdicts.json` | forged battery: **139/139** incl. meta — `dead_entry_count=1`, `phys2d_expected_errors_all_matched=true` with the dead `rp_point_query` entry recorded |
| `corpus/live/r80-critic/forge/` | patched `phys2d_motion.gd` + copied `run_battery.py` + fixtures copy (untracked scratch; tracked files untouched) |
| `corpus/live/r80-critic/dss_wrongarg-forge.txt` | forged arm output — byte-identical PASS line, only 6 errors |
| `corpus/live/r80-critic/ccd_spin-nomonitor.txt` | no-connect forge — byte-identical PASS line |
| `corpus/live/r80-critic/ccd_edge-inertwall.txt` | `collision_layer=0` wall forge — byte-identical PASS line |
| `corpus/live/r80-critic/tele-probe.txt` | `body_set_state` transform landing/persistence probe (kills the srv_tele vacuity hypothesis) |
| `corpus/live/r80-critic/{forge,clean}-run.log` | full battery stdout for both reps |

## 4. Summary for the judge

| finding | class | evidence | smallest safe correction |
|---|---|---|---|
| **C1** dead-entry gate misses `phys2d_motion_*` | fixable defect — same hole r79 C2 closed, re-opened by prefix scope | forged battery 139/139 + meta PASS with `dead_entry_count=1` | `:2165` `startswith("phys2d_events_")` → `startswith("phys2d_")` |
| **C2** `ccd_edge` premise unwitnessed | fixable defect — claim-bearing row whose wall-collidability is unprovable from its pins | inert-wall forge emits byte-identical pin | add one positive witness (slow lane stopped, or mid-path `body_test_motion` overlap) and pin it |
| **C3** `ccd_spin` monitor severing invisible | declared weakness, quantified — family redundancy covers the shared channel; rotational-positive witness absent everywhere | no-connect forge emits byte-identical pin | none required; keep the weak label |

Prior-111 drift: none measured. Mechanism-faithfulness of the other 27 arms: verified by code
read + live receipts. Both demonstrated forgeries run in `corpus/live/r80-critic/` scratch
copies only; the tracked landing is byte-for-byte what the author claims.

**Seat output complete.**
