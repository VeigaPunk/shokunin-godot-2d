# r88 critic — adversarial review of the 8 new r88 arms (ports, startup mode, vacuous evidence, negative-pin vacuity)

Seat `CRITIC` (r88, g2d lane) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`; reviewed bytes = commit
**`3c47eee`** (`r88_surfaces.gd` 422 L, `r88_spawnable.tscn`, `run_battery.py`
+42/−0 → 8 rows, 207→215) with report commit `f9e8a5b` on top. Working tree:
no tracked modification by this seat. **No commit. No tracked file written.**

**Disclosures.** No `lsp` device / no GDScript server on this host (same as
scout/boundary); every claim below is fresh-process execution with receipts.
One transient tracked-file touch: an inline `python3` import of
`corpus/fixtures/run_battery.py` rewrote the tracked
`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`; it was restored with
`git checkout --` (tracked tree byte-clean at seat exit, `git status` verified).
All godot launches `timeout -s KILL`-bounded; hog batches bounded and reaped
(0 stray `yes`/`godot` at exit). All scratch is seat-owned
`corpus/live/r88-critic/**` (`RECEIPTS.md` there). A concurrent
`r88-simplifier` battery ran in this repo during the review (disclosed in §0);
its MP rows completed before my full battery started.

**Verdict recommendation (one line).** The 8-arm *measurement core* is
reproducible (my independent full battery: **215/215 PASS, 0 tuple
mismatches** vs the author's runs1; floor gate verified by mutation), but the
fold should **not** be admitted as landed: **F1 (BLOCKER)** — the hardcoded MP
ports cross-connect under concurrent seats (demonstrated) and one row class can
silently pass cross-connected; **F2/F3/F4 (HIGH)** — two pins are
file-startup-mode artifacts, one pinned boolean is vacuous evidence, and one
negative pin false-positives when the surface is removed; **F5 (HIGH)** — the
pre-existing `phys_peer` single-mode pin is now *confirmed* to flake under
oversubscription with a 5-value alt ladder. Each finding has a verified
smallest-safe correction below.

---

## 0. What I ran

| protocol | scope | receipts |
|---|---|---|
| fresh arms, battery launch shape | **8 arms × 6, `--load 20`** (48 runs) | `runs/load6/` |
| mode controls | author file ×8 (probe arm) + ×3 real; exact-arm-code strip files ×6/×4; minimal ×6; minimal+600 unused funcs ×4; minimal under 31 hogs ×6 | `runs/mode_quiet, quiet_real, strip_quiet, striplight, min_quiet, minbig_quiet, min_load31` |
| MP concurrency | 4-way `mp_loopback`; 3-way `mp_spawner` ×2 (one instrumented); 2-way ×4 | `runs/conc_lb4, conc_sp3, conc_sp3b, sp2_r1..r4` |
| negative-pin vacuity | `p.play()` removed; post-play ack + 20-frame timeline under `--load 24` | `runs/audio_vac, audio_ack` |
| pre-existing flake hunt | `phys_peer`: 50 runs quiet/load/concurrent; **60 runs 12-way under `--load 32`**; `overlap` 22 targeted runs | `runs/phys_*, runs/phys_x*, arms/overlap.*` |
| full batteries (bounded `timeout -s KILL 900`) | committed tree: **215/215 PASS**; mutated copy (gate falsification): **FAIL** | `full1/…/verdicts.json`, `gate/runs-mut/…/verdicts.json` |
| historical scan | 4868 `verdicts.json` receipts for `input_lattice_phys_peer` / `overlap` | scripted, quoted below |

Host load: 2.9–16 in the battery windows; ~40 in the oversubscription window.
`full1` ran while another seat's battery and 3d-lane godots were live.

---

## 1. Findings

| # | sev | finding | impacted axis |
|---|---|---|---|
| F1 | **BLOCKER** | hardcoded MP ports (41777/41778): concurrent batteries cross-connect; loser rows fail loudly (measured 2/4 + 6/6 losers) and a silent false-PASS window is 4–5 frames away; fixture prints `PASS` on contaminated runs | determinism / battery stability / provenance |
| F2 | **HIGH** | `sprite_phys` `y=74.5675` and `light_props` `body_y=118.4614` are **Case-B startup-mode artifacts of the probe file's size**, not arm invariants (author's exact arm code → 66.5952 / 107.9190 in a small file; +600 unused funcs flips a minimal file back to B) | measurement validity / determinism |
| F3 | **HIGH** | `ray_through_occluder=true` is pinned but **vacuous** (ray at x=−50 never crosses the occluder at x∈[0,10]; boundary FALSIFIED it; author kept it) | evidence provenance |
| F4 | **HIGH** | `audio_pos` negative pin is **vacuity-blind**: with `p.play()` deleted the exact pinned payload still matches (2/2) | measurement validity (false-positive) |
| F5 | **HIGH** | pre-existing `input_lattice_phys_peer` single-mode pin: **confirmed** load flake with alt ladder `ev_step_delta∈{1,2,3,4}` (46/60 under oversubscription) — fold decision required | battery stability (pre-existing row) |
| F6 | INFO | `overlap` recurrence (known r69 class) once under the extreme window; 22/22 targeted reps pass | battery stability (pre-existing) |
| F7 | INFO | uid normalization is correct for the 4–5 digit tail (exact-value replace, digit-count agnostic); `uid_after_dyn=true` is a constant-true tripwire; raw uid on the diagnostic line is by design | — (verified, no defect) |
| F8 | INFO | `mp_spawner` 8 s budget claim verified (2.60–2.75 s even under `--load 31`) | — (verified, no defect) |

---

## 2. Details

### F1 [BLOCKER] — hardcoded ports: cross-connection is real and one class can pass silently

**Counterexample (measured, fresh processes).** 4-way concurrent
`mp_loopback` (`runs/conc_lb4`):

```
conc0  rc=[0,0]  … pinned payload (clean)
conc1  rc=[0,0]  … pinned payload (clean)
conc2  rc=[20,0] order=[] limb_s=[] limb_c=[]                      stderr: ERROR: Couldn't create an ENet host.
conc3  rc=[20,0] order=["c_on_srv", "c_conn1"] limb_s=[] limb_c=["ping5:call_local_c"]   stderr: same ERROR
```

All four processes printed `PASS r88_surfaces mp_loopback …` (the fixture's
`_finish` is unconditional). The battery row fails only via signature mismatch;
the *fixture* labels a cross-connected run PASS. 3-way `mp_spawner` and four
2-way rounds (`conc_sp3`, `conc_sp3b`, `sp2_r1..r4`): **every** port-race loser
(a) carried the unallowlisted `ERROR: Couldn't create an ENet host.` on stderr
and (b) received the **other process's** `SpawnableOne` into its client:

```
loser:  R88C neg_child name=SpawnableOne sfp=res://r88_spawnable.tscn path=/root/cli/cont/SpawnableOne
        R88C neg_exit children=1 wait=291..297        # winner's positive add: t=2661, loser receipt t=2666
winner: R88C neg_exit children=0 wait=300  (clean)
```

**Why the silent window matters.** The loser's contamination time is
`winner_start + ~300 frames`; its negative-window end is
`loser_start + 300 frames`. The loser *always* starts later (it lost the bind
race), so the margin equals the start delta — measured **4–5 frames**
(`bound_hit=295/296` in `sp2_r*`; 291–297 in `conc_sp3*`). If two batteries hit
this row with a near-zero start delta (or the winner's frame cadence is
faster), the child lands **after** `bound_hit=300`, and the loser's pinned
payload becomes byte-identical to a clean run (`c_children=0 srv_children=4
bound_hit=300 pos[SpawnableOne 33,44] sync[111,222]` — both processes produce
the same values) → **silent false PASS on a cross-connected peer**. Not
observed in 6 rounds; structurally reachable by the measured phase geometry.

**Impacted axes.** Battery PASS under concurrent seats (the norm on this host:
a sibling battery was live during this review); evidence provenance (fixture
PASS label); potentially a silent wrong answer.

**Smallest safe correction.** Give each process its own port —
`var port := 40000 + OS.get_process_id() % 20000` in both MP arms (port is not
in any pin, so payloads are unchanged), and `_fail("server_rc=%d")` on
`rc_s != 0` in both arms (and print `rc_s/rc_c` in `mp_spawner`'s payload if a
re-pin is acceptable) so a cross-connected loser dies loudly instead of
printing PASS.

### F2 [HIGH] — the two position pins measure the probe file, not the arm

**Counterexample (controlled, fresh processes).** The boundary proved the
startup step-count race (Case A = 29 integrations, Case B = 30) and directed:
*“Do not pin the fall-distance values as written”* + the verified
`v ≠ 0` sync recipe (§2 there). The author pinned Case-B values and never
mentions the race. I reproduced the mode flip **for the author's exact arm
code**:

| file under test | mode | value |
|---|---|---|
| author's `r88_surfaces.gd` (17.7 KB) — `sprite_phys` ×6 loaded + ×3 quiet + 1 in `full1` (and `light_props` likewise) | B | `74.5675` / `118.4614` |
| author's **verbatim** `_arm_sprite_phys` in a 2.9 KB file (`r88_strip.gd`) ×6 quiet | **A** | **`66.5952`** |
| author's **verbatim** `_arm_light_props` in a 2.6 KB file (`r88_strip_light.gd`) ×4 | **A** | **`107.9190`** |
| minimal arm shape (0.8 KB) ×6 quiet | A | `66.5952` |
| same minimal file **+600 unused functions** (21.7 KB) ×4 | **B** | `74.5675` |
| minimal arm shape under 31 hogs ×6 | **bimodal 3 A / 3 B** | both |

So the pinned number is a function of the enclosing file's code volume/startup
profile (the +600-unused-functions mutation flips it with zero behavioral
change). A simplifier pass, a smaller host-startup profile, or a different
cache state moves the row to the other mode and the pin flips — loudly (row
FAIL), but it is a flake trap, and the *value* is not evidence of the physics
being claimed. **Impacted axes:** determinism, measurement validity.

**Smallest safe correction.** Apply the boundary §2 recipe in both arms
(`await physics_frame`; `while b.linear_velocity == Vector2.ZERO: await
physics_frame`; then `N−1` awaits), re-measure ×N, re-pin. (Boundary verified
the recipe reproduces the Case-B values in both modes; if the synced
`sprite_phys` value is again 74.5675 / `light_props` 118.4614, the pin text is
unchanged and only the fixture becomes mode-invariant.) Alternative if the
sync is unwanted: pin only the mode-invariant shape (four bodies equal-y;
`scaled_neg` visible only in `spr_rel`).

### F3 [HIGH] — `ray_through_occluder=true` is vacuous evidence (boundary FALSIFIED; kept)

**Counterexample.** `r88_surfaces.gd:276` casts
`PhysicsRayQueryParameters2D.create((-50,-80), (-50,60))` — a vertical ray at
**x=−50** — while the occluder polygon is `[(0,0),(10,0),(10,10)]` at
`occ.position=(0,-40)`, i.e. global `x∈[0,10]`, `y∈[−40,−30]`. The ray never
crosses the polygon, so `hit.is_empty()` is true regardless of the occluder
(boundary §4.3 measured the same; its sharp ray `(-50,-35)→(50,-35)` *is*
empty in the occluder arm and *hits* in the `StaticBody2D` control). The row's
noncollision claim is carried by `body_y` (falls through), not by this boolean.
The scout's directive 6 blessed the ray; the boundary (committed `d3e16fb`,
available to the author) falsified it and asked for the sharp ray.

**Impacted axes.** Evidence provenance (a pin that cannot fail for the reason
it claims). **Smallest safe correction.** Change the ray endpoints to the
crossing segment (`(-50,-35)→(50,-35)`); the pinned payload text is unchanged
(`ray_through_occluder=true`) and the boolean becomes falsifiable. Optionally
add the collision control as a second arm (out of r88 scope).

### F4 [HIGH] — the `audio_pos` negative pin false-positives when the surface is removed

**Counterexample.** `runs/audio_vac`: a copy of the landed fixture with
`p.play()` **deleted** still emits the exact pinned payload —
`playing=false pos=0.000 peaks_near/far=[-200.00×4] listener_current=true` —
and matches the CASES signature 2/2. The pin cannot distinguish “positional
audio started then went headless-null” from “the player was never started”, so
the row does not cover its stated surface. Same class for `vis_not` (a deleted
arm body would pass; there is no liveness signal for the notifier/enabler).
**Impacted axes.** Measurement validity / false-positive.

**Smallest safe correction (verified safe).** Add a fixture-side liveness
guard immediately after `p.play()`:
`if not p.playing: _fail("play_not_accepted")` — my `runs/audio_ack`
(post-play ack + per-frame timeline, `--load 24`) measured `ack=true` **6/6**,
flip at f7/f8, `f20=false` **6/6** (boundary 14/14), so the guard cannot flake
on this host and the existing f20 pin stays. For `vis_not`, add an unpinned
`R88S` line naming the notifier rect / enabler target so receipts carry node
liveness.

### F5 [HIGH] — `input_lattice_phys_peer` flake is CONFIRMED and its alt space is a ladder

**Counterexample.** 60 fresh runs of the arm at 12-way concurrency under 32
`yes` hogs (the mutated battery was also live in that window;
`runs/phys_x1..x5`, all rc=0, no ports involved):

```
ev_step_delta=0 : 29     ev_step_delta=1 : 15     ev_step_delta=2 : 8
ev_step_delta=3 :  6     ev_step_delta=4 :  2
```

Each alt mode is the press receipt landing 1–4 steps after the pinned parse
step (e.g. delta=1 → the `px=1` cell appears at `d+2` instead of `d+1`;
delta=4 → no `px=1` cell inside the recorded `d−1..d+4` window at all). 50
lighter runs (quiet, `--load 24` sequential, 8-way, under battery load) were
all `delta=0` — the trigger is oversubscription (load ≈40, the same condition
the r88-baseline rep3 hit at load 42.74). Historical scan: 41 receipts carry
the row (incl. frozen copies), 2 non-PASS — both the same rep3 event.

**Impacted axes.** Battery stability (pre-existing row, not an r88 row). **Fold
recommendation:** this must be handled in the r88 fold or explicitly deferred
with a tracked note — it will flake future batteries (confirmed, not
hypothetical). Caveat for the fold shape: the r87 `api_press` precedent was a
2-payload envelope; this row’s alt space is a 5+-value ladder, so a 2-payload
envelope is insufficient — prefer a structural re-pin (e.g. delta as a bounded
range / masked cells) or an arm fix that makes the receipt step-synchronous,
then re-measure. (Not fixed by this seat; critic only.)

### F6 [INFO] — `overlap` recurrence is a known class

One `overlap` FAIL in the mutated battery’s extreme-load window: exit 1,
`ERROR: overlap probe: signal occurred before physics overlap observation` —
byte-identical in kind to the r69-flagged class (24 non-PASS receipts in the
4868-receipt scan, all that message). 22/22 targeted re-runs (6 sequential +
16 concurrent under 24 hogs) PASSed. No r88 action; noted because it belongs to
the same load-sensitivity envelope as F5.

### F7 [INFO] — uid normalization and the `uid_after_dyn` tripwire (verified, no defect)

The boundary’s 4–5 digit tail (`<1e5`: 21/600 000 draws) breaks blanket
`\d{6,}` normalizers; the author instead replaces the **exact uid value**
(`String(e).replace(str(auth_uid), "<C>")`), which is digit-count agnostic and
collision-free (the only other digit in the event strings is the server’s
`c_conn1`; a collision needs `auth_uid == 1`, which the pin’s own
`uid_after_dyn=true` would turn into a loud mismatch, and which was never
drawn). The raw uid lives only on the `R88S` diagnostic line (unpinned) — the
pinned payload is uid-free. No correction.

### F8 [INFO] — `mp_spawner` 8 s budget (verified, no defect)

6 fresh runs under `--load 31`: wall **2.60–2.75 s**, pinned payload identical
6/6 (`frames=0 neg_wait=300 pos_wait=1 sync_wait=2`). The 300-frame negative
bound is a loop constant; the `neg_wait=300` pin correctly distinguishes
“bound held” from contamination (`<300`). No correction.

---

## 3. Author’s claims vs measurement

| claim | verdict |
|---|---|
| 8 rows inserted ahead of the crash/descendant tail, 207→215 | **verified** (`full1` rows=215; descendant metas PASS) |
| all 8 arms uniq PASS payload = 1 across reps; stderr empty except `sprite_phys` | **verified** 6/6 per arm under `--load 20`; sprite_phys stderr 260 B = 1 exact whitelisted ERROR line ×6 |
| `expected_errors` += 1 exact-shape entry; r88 floor gate gates it | **verified by mutation**: with the ERROR removed, the row itself PASSes, the census entry is `dead_in_run=true matched_lines=0`, and `r88_expected_errors_all_matched=false` is the **sole** false discrimination → battery FAIL |
| `<C>` normalization handles the 4–5 digit uid tail | **verified** (exact-value replace; see F7) |
| all pins byte-stable, 0 envelopes, “every payload measured ×4” | **conditional**: stable for the landed file in my windows (48 loaded + 6 quiet + full1), but two pins are mode artifacts (F2) |
| `light_props` height fix + occluder noncollision evidence | height fix verified; `ray_through_occluder` vacuous (F3) |
| audio/vis negative-only; f20 sample stable | sample point verified stable (6/6 + 6/6 + boundary 14/14); pin is vacuity-blind (F4) |
| MP arms loopback-only, `uid_after_dyn` honest | loopback verified; concurrency safety false as landed (F1) |
| “0.5–1.4 s/arm; mp_spawner ~2.6 s; inside the 8 s bound” | **verified** (2.60–2.75 s under `--load 31`) |
| prior-207-row identity preserved | **verified**: `full1` vs author runs1 = 215 common, 0 tuple mismatches |

**Independent full-battery evidence (my bytes).** `full1`: **215/215 PASS**,
`r88_*` gate true, `r87_*` true, `phys2d_*` true, `dead_entry_count=0`, and
**0/215 tuple mismatches** against `corpus/live/r88-author/runs1/…`. So the
landing is *reproducible in the current host window*; the findings above are
about what it will do under concurrency, after edits, and about what its pins
actually prove.

---

## 4. Verdict recommendation

- **F1 must be fixed before the fold** (BLOCKER): port ownership + rc guard.
  The demonstrated failure is not hypothetical — two batteries overlapping on
  this host flake the row, and a 4–5 frame phase margin separates that from a
  silent cross-connected PASS.
- **F2, F3, F4 should be fixed in the same fold** (HIGH, each a small verified
  correction; F3/F4 fixes keep the pinned payload text unchanged, F2 needs a
  re-measure after the sync recipe).
- **F5 is a fold decision for the canonical judge** (HIGH): confirmed
  load-flake with a 5-value alt ladder; envelope-or-defer, but a 2-payload
  envelope does not cover it.
- F6–F8 informational; no r88 action.
- No judging/admission by this seat; the canonical Rust runtime is the sole
  Pareto judge.

## 5. Evidence index

All under `corpus/live/r88-critic/` (`RECEIPTS.md` there; probe sha256s in
`logs/probe-shas.txt`). Key artifacts: `runs/load6` (48 fresh runs),
`runs/conc_lb4`, `runs/conc_sp3`, `runs/conc_sp3b`, `runs/sp2_r1..r4`,
`runs/mode_quiet`, `runs/quiet_real`, `runs/strip_quiet`, `runs/striplight`,
`runs/min_quiet`, `runs/minbig_quiet`, `runs/min_load31`, `runs/audio_vac`,
`runs/audio_ack`, `runs/phys_quiet|load|c1..c3`, `runs/phys_x1..x5`,
`runs/sp_load31`, `arms/overlap.*`, `arms/ovl_c*`, `full1/20261015T183307178445Z/verdicts.json`,
`gate/runs-mut/20261015T183954796247Z/verdicts.json`, `gate/mutfix/`.
Report: `reports/round-88/r88-critic.md` (this file, untracked; no commit).
