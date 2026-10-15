# r88 author — remaining measured surfaces armed (8 cells, 0 envelopes)

Seat `AUTHOR` (g2d lane r88) | host **devin** | Godot `4.7.2.stable.arch_linux`
(`/usr/bin/godot`, headless, 60 tps, GodotPhysics2D), Python 3.14.7.
HEAD `d15c54d` (uncommitted worktree changes only — **nothing committed**).
No `lsp` device exposed; no GDScript/Python server installed — same host state
as scout; all work was fixture-level file landing + harness inserts, verified
by fresh-process execution, not symbol operations.

Scope per dispatch: r88-scout §9 directives 4–7 only. `geo_*` is r89's lane,
`rb_*` is r90's lane — neither authored here.

## Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/r88_surfaces.gd` | `78370a04…` (422 lines) | new fixture adapting the dead seat's measured arms (`corpus/live/r88-scout/proj/r88_probe.gd` sha `3584d229…`) to battery convention — see below |
| `corpus/fixtures/r88_spawnable.tscn` | `89b9ddbe…` (5 lines) | minimal Node2D `SpawnableOne` @ (33,44) for the registered-scene spawn positive control |

`r88_surfaces.gd` vs the dead probe — three deliberate changes (all
scout-mandated):
1. **Arm dispatch** uses `OS.get_cmdline_user_args()` + `--arm=` prefix scan —
   the dead probe's `get_cmdline_args()` two-token form can never fire under
   the battery's post-`--` launch shape (scout §0, hazard 1; verbatim reuse
   would silently census on every arm).
2. **`light_props`** carries `range_height`→`height` (scout §3.14/directive 6;
   the verbatim leg aborts mid-arm → SceneTree idle → rc=124 hang).
3. **`mp_loopback`** normalizes the random client peer id to `<C>` before
   printing (directive 4 — uid was the only unstable field, uniq 3→1); volatile
   `frames`/`wait` counters moved to `R88S` diagnostic lines, kept out of the
   pinned PASS payload (scout hazard 6 — mode candidates, not pins).

Directive-9 guards: `arm=` is the first printed line; empty arm →
`_fail("empty_arm")` rc=1; unknown arm → `_fail("unknown_arm")` rc=1. No
`offset_polyline` anywhere (hazard 3 — process-killer).

## run_battery.py changes (insertion-only, +42/−0)

1. **CASES 207 → 215** inserted ahead of the crash/descendant tail (before
   `crash_spontaneous_sigabrt`), preserving the descendant `sleep 8` gap —
   8 rows, all `r88_surfaces_*` prefix, verbatim measured signatures.
2. **`expected_errors` += 1 entry** (directive 7): `r88_surfaces_sprite_phys`
   → `ERROR: Index p_frame = 3 is out of bounds (vframes * hframes = 2).`
   (exact-shape) — the arm deliberately sets `frame=3` on a 2-frame regioned
   sprite; the engine refuses loudly and deterministically (×4 identical
   stderr blocks).
3. **Floor gate extended deliberately**: new discrimination
   `r88_expected_errors_all_matched` (`r88_` prefix) alongside the r87 one —
   a dead r88 allowlist entry now fails loudly instead of passing silently.

## New-cell inventory (8 rows, all pinned-mode, no envelopes)

| case | surface | pin (measured ×4 byte-stable) |
|---|---|---|
| `r88_surfaces_mp_offline` | OfflineMultiplayerPeer authority-of-one | `status=2 uid=1 mode=2 chan=0 tree_uid=1 is_server=true tree_status=2` |
| `r88_surfaces_mp_loopback` | one-process ENet loopback, two-way reliable RPC + call_local + disconnect ordering | `rc=[0,0] uid_s=1 uid_after_dyn=true order=["c_on_srv","c_conn1","s_conn<C>","c_srvdisc","s_disc<C>"] limb_s=[ping7:c2s, ping5:call_local_c] limb_c=[ping5:call_local_c, ping9:s2c]` |
| `r88_surfaces_mp_spawner` | Spawner silent non-replication + registered-scene positive control + Synchronizer | `neg[c_children=0 srv_children=4 bound_hit=300] pos[added=SpawnableOne c_got=SpawnableOne c_pos=33.0000,44.0000] sync[pos=111.0000,222.0000]` |
| `r88_surfaces_light_props` | PointLight2D/DirectionalLight2D/LightOccluder2D/OccluderPolygon2D/CanvasModulate + occluder noncollision | full readback + `body_y=118.4614 ray_through_occluder=true occ_cls=LightOccluder2D occ_is_co=false` |
| `r88_surfaces_sprite_meta` | region/frame/flip/offset/centered readback + get_rect | `re=true rr=[P:(4,4) S:(8,8)] hf=4 vf=2 f=5 fc=(1,1) fh fv off=(3,-2) cen=false` + `signals=["fc"]` + rects |
| `r88_surfaces_sprite_phys` | sprite flags under falling body (4 variants) | all at `y=74.5675`; `scaled_neg` visible only in `spr_rel` — sprite metadata invisible to integrator |
| `r88_surfaces_audio_pos` | positional audio — **negative-only** (Dummy driver) | `playing=false pos=0.000 peaks_≈[-200.00×4] listener_current=true` |
| `r88_surfaces_vis_not` | visibility notifier/enabler — **negative-only** (no screen headless) | `on_screen0=false en_onscreen=false events=[] on_screen_end=false enabler_proc=false` |

## Fresh-arm evidence (pre-battery)

Each arm run fresh ×4 in the battery's exact launch shape
(`timeout 15 godot --headless --path <scratch> --script res://r88_surfaces.gd
-- --arm=<a>`; scratch = fixtures project.godot + probe + tscn):

- **All 8 arms: uniq PASS payload = 1 across 4 reps**; all stderr empty except
  `sprite_phys` (one deterministic 5-line ERROR+backtrace block, whitelisted).
- Wall times: 0.5–1.4 s/arm; `mp_spawner` ~2.6 s (negative bound cut 600→300
  idle frames vs scout's arm — comfortably inside the battery's 8 s bound even
  when a replication leg breaks; bound is a pin constant by construction).
- Receipts: `corpus/live/r88-author/arms/` (64 files), probe copy under
  `corpus/live/r88-author/proj/`.

**`spawn()` correction (new measurement, supersedes directive wording):**
in 4.7.2 `MultiplayerSpawner.spawn(data)` *refuses without a spawn_function*
(`ERROR: Custom spawn requires the 'spawn_function' property to be a valid
callable. at: spawn (multiplayer_spawner.cpp:325)`, `spawn(0)` and `spawn()`
alike — empirically verified). The registered-scene positive control is the
**auto-track**: `load(tscn).instantiate()` + `add_child` under `spawn_path`
replicates because `scene_file_path` matches `add_spawnable_scene` — client
received `SpawnableOne` twin at the baked-in (33,44) in ~4 frames, ×4 stable.

**`mp_loopback` post-disconnect fix:** `api_c.get_unique_id()` after
`server_disconnected` emits `ERROR: The multiplayer instance isn't currently
active` (unpinned ERROR would fail the row) — `auth_uid` is captured while
connected and is the only safe post-disconnect value.

## Full battery — before/after

| run | rows | verdict |
|---|---|---|
| r87-critic2 ref (admitted bytes) | 207 | PASS |
| r87-fold-check ref | 207 | PASS |
| author runs1 `…/r88-author/runs1/20261015T181519396144Z/verdicts.json` | 215 | **PASS** |
| author runs2 `…/r88-author/runs2/20261015T181910437115Z/verdicts.json` | 215 | **PASS** |

**Prior-207-row identity** (`corpus/live/r87-baseline/compare.py godot`, vs
r87-critic2 + r87-fold-check post-fold refs): `common=207 new_only=8
old_only=0`, **tuple_mismatches=1 (seeded=0, meta=1)** both runs — the single
meta diff is `probe_error_clause_surface`, whose census by design enumerates
every `expected_errors` row (now incl. `r88_surfaces_sprite_phys` + the new
`r88_` gate key). All 207 seeded tuples byte-identical.
runs1↔runs2: `tuple_mismatches=0` across all 215 rows.
`output-normalized` diffs: only envelope rows emitting their other whitelisted
payload (`input_lattice_{press_phys,release_edge,ui_ns,pre_frame}` line 3),
`r88_surfaces_mp_loopback` line 4 (`s_conn<uid>`/`raw_uid=` — the declared
volatile peer-id token on the diagnostic line, pin itself normalized), and
export progress-log `Registering global classes (37 steps)` vs `(33)` — +4 =
r87's 3 landed `.gd` + `r88_surfaces.gd` scanned at export; signature/verdict
unchanged (same attributable class r87 recorded).

**Gate evidence (runs1 verdicts.json):** `r88_expected_errors_all_matched=true`,
`r87_…=true`, `phys2d_…=true`, census `dead_entry_count=0`; the sprite_phys
census row shows entry matched_lines=1, `bare_classification_rejects=true`,
`allowlisted_classification_passes=true`.

## Bimodal cells / rep counts

- **Envelopes added: 0** — all 8 arms measured uniq=1 ×4 fresh + ×2 battery.
- `expected_errors` added: 1 (`r88_surfaces_sprite_phys`, exact shape).
- New-cell rep counts: 4/4 fresh PASS per arm + 2/2 battery PASS per row.
- Rows: 207 → 215 (+8).

## Host notes / remaining risks

- MP legs are one-process loopback on `127.0.0.1` (ENet, ports 41777/41778);
  `uid_c` normalization binds ordering, not the value — a host issuing uid 1
  to the client would flip `uid_after_dyn` (honest measurement, loud).
- `audio_pos`/`vis_not` are negative-only **by host constraint** (Dummy driver,
  no screen headless) — positive rows are structurally impossible here, never
  authored (directive 5).
- `bound_hit=300` pins the loop bound constant, not wall time; scheduling
  counters stay in `R88S` diagnostic lines only.
- The sprite_phys GDScript backtrace (`res://r88_surfaces.gd:327`) is inert
  (no `ERROR:` token) but shifts if the probe file is edited — cosmetic only.
- Unmeasured: `spawn_function` custom-spawn path, cross-process/multi-peer
  replication, WebSocket/WebRTC peers, `offset_polyline` payloads (banned —
  SIGABRT), `make_atlas` correct-signature arm (r89 scope).
- No commit. Worktree: `M corpus/fixtures/run_battery.py`,
  `?? corpus/fixtures/r88_surfaces.gd`, `?? corpus/fixtures/r88_spawnable.tscn`,
  receipts under `corpus/live/r88-author/`, this report.
