# r88 fold — gate-approved corrections applied (F1–F5 + SP1/SP2)

Seat `FOLD` (r88, g2d lane) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`; base work commit `3c47eee`,
HEAD at fold time `0628932`. Sources: `r88-critic.md` (F1 BLOCKER + F2–F5),
`r88-reviewer.md` (F1/F2), `r88-boundary.md` (directives 1/3c/5, §2 sync
recipe), `r88-simplifier.md` (SP1/SP2 + proven patch).

**No `lsp` device** on this host (same disclosure as every r88 seat); all
edits are textual on two files, all claims are fresh-process receipts.
**No commit.** Tracked diff: `r88_surfaces.gd` +64/−12, `run_battery.py`
+17/−1. Receipts: `corpus/live/r88-fold/**` (`RECEIPTS.md` there).

---

## 1. Items applied

### SP1/SP2 — simplifier patch (applied FIRST, byte-clean)

`git apply corpus/live/r88-simplifier/r88-simplifier-fold.patch` applied
clean against the `78370a04…` bytes; result sha **`4661cedb…`, 418 lines** —
byte-equal to the simplifier's proven `fixtures-after/` output. Deletes
`MpLimb.uping` (zero call sites) and `_body`'s unexercised `gs` parameter.
Done before all other edits so the patch's pre-fix offsets held.

### F1 (BLOCKER) — MP ports now pid-derived + loud failure on bind loss

Both `mp_loopback` and `mp_spawner`: `41777`/`41778` →
`var port := 40000 + OS.get_process_id() % 20000` (per-process port; the
port number is in no pinned payload — verified by grep and by all post-fix
payloads). `rc_s` is checked **before the client is created** and `rc_c`
immediately after: `if rc != 0: _fail("<arm> server_rc|client_rc=%d"); return`.
A bind-race loser now exits 1 with `FAIL r88_surfaces <arm> reason=…` — it
can no longer cross-connect into another process's server (the critic's
silent-PASS window is closed by construction: the loser never opens a
client). The unallowlisted `ERROR: Couldn't create an ENet host.` on stderr
still rejects classification independently.

**Evidence.** 4/4 quiet reps + 10/10 loaded reps per MP arm: pinned payloads
byte-identical (`rc=[0,0]`, `bound_hit=300`, …), PASS uniq=1 each, zero
`Couldn't create an ENet host` on any stderr. Live cross-battery test: my
runs1 overlapped a concurrent `r89-baseline` battery whose tree still carries
the **old** fixture with hardcoded 41777/41778 — my MP rows never competed
for those ports and both rows PASSed in that window.

### F2 (HIGH) — startup-race pins made mode-invariant (boundary §2 recipe)

`sprite_phys` (was `for i in 30`) and `light_props` (was `for i in 40`) now:
`await physics_frame` → `while <body>.linear_velocity == Vector2.ZERO: await
physics_frame` → `for i in N-1`. sprite_phys tracks the four bodies in a
`bodies` array and syncs on `bodies[0]` (all four enter the tree in the same
flush and first-integrate on the same step).

**Re-measured post-sync:** `sprite_phys` `pos=…,74.5675` ×4 bodies in 7/7
quiet + 10/10 loaded reps; `light_props` `body_y=118.4614` in 4/4 quiet +
10/10 loaded reps — identical to the pinned Case-B values, now reachable
from both startup modes (the Case-A `66.5952`/`107.9190` realization is
absorbed by the guard loop). **CASES evidence strings unchanged** — the
re-measure confirmed the pins, per boundary's verified recipe.

### F3 (HIGH) — vacuous ray now crosses the occluder

`PhysicsRayQueryParameters2D.create((-50,-80),(-50,60))` →
`((-50,-35),(50,-35))`. The y=−35 segment crosses the occluder polygon's
x∈[5,10] band (boundary's geometry). Re-measured: `hit.is_empty()` still
true → `ray_through_occluder=true` pin text unchanged — but now falsifiable
(a `LightOccluder2D` is not a `CollisionObject2D`; the boundary's
`StaticBody2D` control on the same triangle hits this exact ray).

### F4 (HIGH) — audio liveness guard

Immediately after `p.play()`: `if not p.playing: _fail("play_not_accepted");
return`. Under the Dummy driver `play()` sets `playing=true` synchronously
(boundary 14/14, critic ack 6/6 under load) — a no-op `play()` can no longer
produce the pinned negative payload. Re-measured: pinned payload
byte-identical 4/4 quiet + 10/10 loaded.

### F5 (HIGH) — `input_lattice_phys_peer` → 6-payload mode envelope

CASES row converted from a single pin to a tuple envelope covering every
observed verbatim payload (evidence tuple → PASS iff ANY payload matches;
same mechanism as `api_press`/`press_phys`/`release_edge`/`ui_ns`).

**Measurement (fresh, this seat):** 150 hogged reps (16 `yes` hogs, ~10-way
launch concurrency, the critic's 12-way/32-hog class): `ev_step_delta`
**{0:98, 1:19, 2:6, 3:8, 4:4, 5:15}**. Combined with the critic's {0:29,
1:15, 2:8, 3:6, 4:2} the observed ladder is deltas 0–5. **delta=5 is a new
mode not in the critic's window** (same all-`px=0` cells as delta=4,
different digit) — the 5-payload envelope I first staged would still have
flaked; the envelope now covers delta=5 verbatim (all six payloads were
byte-verified against receipts via AST extraction).

**Mechanism (commented at the row):** under CPU oversubscription the press
receipt lands 1+ ph steps after the pinned parse step (interposed steps in
the same idle-frame burst), shifting the `px=1` cell right; delta≥4 pushes
it past the recorded `d-1..d+4` window. Residual: delta≥6 is theoretically
reachable (bounded by `max_physics_steps_per_frame`) but unobserved in 210
reps; it would fail **loudly** — a flake, never a silent wrong answer.

**Live battery evidence:** runs3's `phys_peer` row landed `ev_step_delta=1`
— the envelope's second payload matched inside a real battery run.

### Item 7 — wording check: not present, no change

The author's "207→215 CASES" phrasing does **not** appear in
`run_battery.py` (grep: the only `207`/`215` in the file is `207.9190` in
the unrelated `camera_proc` pin; the r88 comment block carries no CASES
count). Declined — nothing to fix. (Literal CASES is 200→208 entries;
verdict rows 207→215, as the reviewer documented.)

---

## 2. Verification

| check | result |
|---|---|
| `python3 ast.parse run_battery.py` | clean (also post-envelope-extension) |
| `godot --headless --path scratch --check-only --script res://r88_surfaces.gd` | rc=0 |
| direct arm reps (battery launch shape) | all 8 arms rc=0; touched arms ×4–7 reps, PASS-payload uniq=1 each; sprite_phys stderr = exactly 1 whitelisted `ERROR: Index p_frame = 3 is out of bounds (vframes * hframes = 2).` per rep |
| full battery runs1 | **FAIL** — `audio_bus_route_invalid_control` (pre-existing row, untouched): `advanced=false` under a 3-battery load window (1st non-PASS in 185 scanned receipts); consequential `probe_error_clause_surface` census-consistency FAIL. **All 9 touched rows PASS.** |
| full battery runs2 | **215/215 PASS** |
| full battery runs3 (final bytes, 6-payload envelope) | **215/215 PASS**, `r88_expected_errors_all_matched=true`, phys_peer landed delta=1 envelope mode |
| loaded verification (16 `yes` hogs) | mp_loopback/mp_spawner/sprite_phys/light_props/audio_pos ×10 each: PASS uniq=1, zero ENet errors; phys_peer ×150: all six modes whitelisted |
| hogs | all killed at exit (`pgrep -x yes` = 0 for mine; a later 12-hog set belongs to another seat, PPID 1612189) |

`runs3` scratch `r88_surfaces.gd` sha `9631961d…` == working tree — the
battery exercised the folded bytes.

## 3. Files changed

- `corpus/fixtures/r88_surfaces.gd` (+64/−12): SP1/SP2 deletions; pid-derived
  ports + `rc_s`/`rc_c` `_fail` guards in `mp_loopback`/`mp_spawner`; v≠0
  sync in `sprite_phys`/`light_props`; crossing ray in `light_props`; audio
  liveness guard in `audio_pos`.
- `corpus/fixtures/run_battery.py` (+17/−1): `input_lattice_phys_peer` →
  6-payload mode envelope + mechanism comment. No pinned string changed —
  F2 re-measure confirmed the existing `74.5675`/`118.4614` pins and
  `ray_through_occluder=true`.

## 4. Declined / deferred

- **Item 7 wording**: phrasing absent from the harness — no change made.
- **delta≥6 phys_peer payload**: unobserved (210 reps); enumerated
  envelopes admit only measured payloads — documented as a loud-fail
  residual in the row comment.
- **Critic's optional `rc_s`/`rc_c` re-pin in mp_spawner payload**: not
  taken — the `_fail` guards make the values unreachable-except-0, and the
  existing pins stay byte-stable.
- **runs1 `audio_bus_route_invalid_control` flake**: pre-existing row
  (untouched by this fold); a load flake outside the dispatch's documented
  flake list — noted here for the round record, not re-pinned.

## 5. Remaining risks

- Residual `pid % 20000` port collision across processes is still possible
  by construction; it now fails loudly (exit 1, `FAIL … reason=…`) instead
  of contaminating — the intended trade.
- `audio_bus_route_invalid_control` is a real (if rare) load flake — 1/185
  receipts; future batteries under multi-battery contention may hit it
  again. Owned by no r88 item.
- delta≥6 phys_peer mode (unobserved) would fail loudly — flake, not a
  wrong answer.

Seat output complete. Stop after the assigned implementation.
