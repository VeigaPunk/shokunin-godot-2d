# game-dev-2d corpus

- `fixtures/`: 29 inherited, read-only Godot 4.7.2 fixtures plus `run_battery.py`, which copies the seeds to an ignored scratch run before execution.
- `knowledge/seed.md`: fixture provenance and inherited constraints; `knowledge/2026-10-12-production-checklist.md`: production surfaces still unprobed.
- `lessons/r1-headless-verification.md`: decision table, observed errors, reproduction checklist and source pointers.
- `lessons/r1-initial.json`, `lessons/r1-passing.json`: full per-case stdout/stderr and verdicts from the first failing run and corrected passing run.
- `lessons/r2-camera-headless.md`, `lessons/r2-camera-verifier.json`: camera-center decision boundaries and independent 17/17 replay; rendered viewport behavior remains unprobed.
- `lessons/r3-ui-headless.md`, `lessons/r3-ui-verifier.json`: synthetic UI signal-to-Label decision boundaries and independent 19/19 replay; production/rendered UI remains unprobed.
- `lessons/r4-level-headless.md`, `lessons/r4-level-verifier.json`: authored level tile collision metadata and independent 21/21 replay; runtime contact/rendering remain unprobed.
- `lessons/r5-animation-headless.md`, `lessons/r5-animation-verifier.json`: deterministic in-memory property animation and independent 23/23 replay; rendered motion remains unprobed.
- `lessons/r6-export-headless.md`, `lessons/r6-export-verifier.json`: actual scratch Linux/X11 export plus missing-preset control, independent 25/25; generated artifacts deleted, app launch and production project remain unprobed.
- `lessons/r7-fault-classification.md`, `lessons/r7-fault-verifier.json`, `lessons/r7-normal-verifier.json`: shared subprocess/classifier fault probes and independent 25/25 replay.
- `lessons/r8-runtime-contact.md`, `lessons/r8-contact-verifier.json`: finite CharacterBody2D contact at authored tile `(2,3)` and scratch polygon-removed pass-through; independent 27/27 replay.
- `lessons/r9-diagnostic-calibration.md`, `lessons/r9-diagnostic-verifier.json`, `lessons/r9-fault-regression.json`: captured-output export/mutant ERROR calibration, independent 27 + four probes and r7 fault regression.
- `lessons/r10-export-launch.md`, `lessons/r10-launch-verifier.json`, `lessons/r10-battery-verifier.json`, `lessons/r10-fault-regression.json`: direct scratch exported Linux/X11 executable startup event/control, independent 32/32 and fault regression.
- `lessons/r11-real-godot-diagnostics.md`, `lessons/r11-godot-error-verifier.json`, `lessons/r11-battery-verifier.json`, `lessons/r11-launch-regression.json`, `lessons/r11-fault-regression.json`: paired real Godot push_error classifier calibration, independent 33/33.
- `lessons/r12-headless-audio.md`, `lessons/r12-initial-hold.json`, `lessons/r12-cleanup-author.json`, `lessons/r12-battery-verifier.json`, `lessons/r12-fault-regression.json`: in-memory WAV player-state/position advancement and no-play assertion, initial leak-warning HOLD, bounded cleanup and independent 35/35 warning-free replay.
- `lessons/r13-headless-tween-flash.md`, `lessons/r13-battery-verifier.json`, `lessons/r13-fault-regression.json`: headless SceneTree Tween modulation excursion/return and no-start control, independent 37/37.
- `lessons/r14-audio-leak-warning.md`, `lessons/r14-warning-verifier.json`, `lessons/r14-fault-regression.json`: production audio-positive ObjectDB warning rejection against R12 real captured leak/clean output, independent 38/38.
- `lessons/r15-health-gauge.md`, `lessons/r15-gauge-verifier.json`, `lessons/r15-fault-regression.json`: headless TextureProgressBar value_changed receipt and disconnected control, independent 40/40.
- `lessons/r16-gauge-clamp.md`, `lessons/r16-export-adverse.json`, `lessons/r16-parent-retry.json`, `lessons/r16-clamp-verifier.json`, `lessons/r16-fault-regression.json`: clamp boundaries and same-current callback suppression, independent 40/40 with intermittent author export failure retained.
- `lessons/r17-export-path-hold.md`, `lessons/r17-battery-control.json`: unresolved r16 export-path failure, multiple fresh controls, no causal fix or code change; Round 17 HOLD. Live scratch under `live/runs/` is ignored and disposable.
- `lessons/r18-camera-limit.md`, `lessons/r18-limit-verifier.json`, `lessons/r18-fault-regression.json`, `lessons/r18-setup-fault-control.json`: headless Camera2D right-edge center clamp plus far-bound control, independent 42/42; rendered framing unprobed.
- `lessons/r19-stream-attribution.md`: paired Godot 4.7.2 headless print/printerr stream attribution (opt-in `--probe-stream-attribution`); crash-exit and process-tree timeout remain unprobed. Live scratch under `live/runs/` is ignored and disposable.

## Coverage map (r105 appended correction — the r19 bullets above are kept as history)

The bullets above stop at r19 and say "29 inherited" fixtures; at base `e8990516` the battery holds
585 CASES rows (AST count, `corpus/QUALITY.md` Q18 command). Rows grouped by name prefix into
surfaces — assignment is [inf] from row names, fixtures and LOG notes (R105Scout, r105). Fixtures are
relative to `corpus/fixtures/`, lesson paths to `corpus/`. Admitted knowledge lives in `knowledge/`,
its admission bar in `QUALITY.md`, its sources in `SOURCES.md`.

| Surface / CASES families | Rows | Fixture files | Lesson or report pointer | Since |
|---|---:|---|---|---|
| Loop — `mechanic`, `causal`, `stree_` | 14 | `controls/mechanic_test.gd`, `causal_chain.gd`, `stree_lattice.gd` | `lessons/r1-headless-verification.md`; `reports/round-97/` | r1 (LOG.md:9); SceneTree timing r97 (LOG.md:1177) |
| Input — `input_`, `input89_`, `r87_edge_`, `ei_`, `route_`, `keyup`, `release`, `wrong_`, `r100b_phase_`, `r100b_emul_`, `negative_route` | 42 | `controls/input_route*.gd`, `causal_chain.gd`, `input_lattice.gd`, `input89_edges.gd`, `r87_edge.gd`, `ei_bound.gd`, `r100b_phase.gd`, `r100b_emul.gd` | `lessons/r1-headless-verification.md`; `reports/round-87/`, `reports/round-100/` | r1 (LOG.md:9); lattices r87/r100 |
| Physics — `phys2d_`, `dss_`, `geo2d_`, `r90_lattice_`, `r95b_order_`, `r101_ytrans_`, `overlap`, `negative_overlap`, `r88` sprite-physics | 169 | `controls/overlap*.gd`, `phys2d_{events,motion,joints,backends}.gd`, `dss_lattice.gd`, `geo2d_lattice.gd`, `rb_lattice.gd`, `r95b_order.gd`, `r101_ytrans.gd`, `r88_surfaces.gd` | `lessons/r8-runtime-contact.md`; `reports/round-79/`–`round-81/`, `round-89/`–`round-90/`, `round-95/` | r1 (LOG.md:9); physics lattices r79–r95 |
| Scenes — `scene_`, `transition`, `negative_signal`, `negative_transition` | 4 | `controls/test_scene_signal*.gd`, `controls/scene_transition*.gd` | `lessons/r1-headless-verification.md` | r1 (LOG.md:9) |
| Camera — `camera_` | 25 | `camera_follow.gd`, `camera_limit.gd`, `camera_proc.gd` | `lessons/r2-camera-headless.md`; `reports/round-85/` | r2 (LOG.md:16) |
| UI — `button_`, `checkbox_`, `health_`, `slider_`, `ui_`, `r100_gui_` | 49 | `button_activation.gd`, `button_group_selection.gd`, `checkbox_toggle.gd`, `health_gauge.gd`, `slider_adjust.gd`, `ui_signal_hud.gd`, `r100_gui.gd` | `lessons/r3-ui-headless.md`, `r15-health-gauge.md`, `r50-hslider-release-after-reconnect.md`; `reports/round-100/` | r3 (LOG.md:27) |
| Levels/tilemap — `level_`, `contact_`, `r92_tilemap_` | 17 | `level_collision/level_probe.gd`, `contact_probe.gd`, `tilemap_lattice.gd` | `lessons/r4-level-headless.md`, `r8-runtime-contact.md`; `reports/round-92/` | r4 (LOG.md:37); TileMapLayer lattice r92 |
| Animation — `animation_`, `tween_`, `r93_anim_`, `r93_tween_` | 27 | `animation_property.gd`, `tween_flash.gd`, `anim_lattice.gd`, `r93b_anim.gd` | `lessons/r5-animation-headless.md`, `r13-headless-tween-flash.md`; `reports/round-93/` | r5 (LOG.md:45) |
| Audio — `audio_`, `r99_audio_`, `r99b_`, `r99b_finfree_`, `r88` audio-position | 26 | `audio_playback.gd`, `audio_bus_route.gd`, `audio_lattice.gd`, `r99b_modes.gd`, `r88_surfaces.gd` | `lessons/r12-headless-audio.md`, `r59-audio-non-author.json`; `reports/round-99/` | r12 (LOG.md:112); bus routing r59; lattice r99 |
| Navigation — `nav_` | 11 | `nav_lattice.gd` | `reports/round-91/` | r91 (LOG.md:1139) |
| Particles — `r94_particles_` | 19 | `particles_lattice.gd` | `reports/round-94/` | r94 (LOG.md:1159) |
| Resources/UID — `res_`, `r96b_{cache,id,phase,seed,seq,var}_` | 68 | `res_uid.gd`, `res_uid_s01.gd`–`res_uid_s04.gd`, `r96b_{cache,id,phase,seed,seq,var}.gd` | `lessons/r104-resource-loader-uid.md`; `reports/round-96/`, `round-104/` | r96 scene/resource IDs (LOG.md:1170); `ResourceUID` lattice r104 |
| Save/load — `save_`, `r96_scene_` | 18 | `save_roundtrip.gd`, `save_process.gd`, `scene_io_lattice.gd` | `lessons/r57-save-non-author.json`, `r58-process-non-author.json`; `reports/round-96/` | r57 (LOG.md:553); process boundary r58 |
| Export/launch — `export_` | 50 | `export_div_s01.gd`–`s05.gd`, registered `export_prod*.gd` variants, `export_launch.gd`, runner-generated export cases | `lessons/r6-export-headless.md`, `r10-export-launch.md`, `r101-export-capability.md`; `reports/round-102/`, `round-103/` | r6 export (LOG.md:54); r10 launch; r101–r102 production-shaped |
| Harness/meta — `crash_`, `descendant_`, `r100b_seq_`, `r101_seqfull_` | 8 | `spontaneous_crash_probe.gd`, `descendant_pipe_probe.gd`, `r100b_seq.gd`, `r101_seqfull.gd` | `lessons/r101-seq-replay-transcript-pin.md`, `r103-receipt-shape-gate.md`; `reports/round-103/`, `round-104/` | r61 crash CASES (LOG.md:584); descendant r62; sequence pins r100–r101 |
| Canvas/rendering — `r98_canvas_`, base `r98b_`, `r98b_{latch,qflush,qorder}_`, `r98c_`, selected `r88_surfaces_` arms | 35 | `canvas_lattice.gd`, `r98b_attack.gd`, `r98b_rksenum.gd`, `r98c_flush.gd`, `r88_surfaces.gd` | `reports/round-88/`, `round-98/` | r88 state properties (LOG.md:1103); CanvasItem flush lattice r98 |
| Multiplayer — `r88_surfaces_mp_*` | 3 | `r88_surfaces.gd` | `reports/round-88/` | r88 ENet (LOG.md:1103) |
| **Total** | **585** |  |  |  |

r105 additions (not in the 585 above): 8 `res_uid_` rows re-admitted under per-row isolation
(`lessons/r105-res-uid-isolation.md`), `r105_tile_rid_` ×4 (`tilemaplayer-body-rid-attribution`),
`r105_phys_replay_` ×3 (`physics-replay-boundary`).

## Frontier

Each line: surface — why it is open — the sweep that shows absence (run from the lane root).

- Rendered output / visual canary — headless runs only; `r100_gui_render` reports `img_null=1 rd_null=1 screens=0` — `grep -rlE 'get_image\(|save_png|capture_screen' corpus/fixtures/*.gd` hits 6 fixtures, all synthetic-asset writes or null-image reads [inf, R105Scout], none a rendered-image assertion
- Renderer performance — no frame/GPU time or draw-call budget asserted — `grep -rlE 'draw_calls|render_time|gpu_time|benchmark' corpus/fixtures/*.gd`
- Clean-checkout import → export → launch — export rows build generated scratch projects; no clean checkout staged (ART C3; `SOURCES.md` S006/S007/S024) — `grep -rlE 'git clone|clean_checkout' corpus/fixtures`
- GUT / gdUnit4 runner contracts — custom runner only (ART C4; S016–S023) — `grep -rliE 'gdunit|addons/gut' corpus/fixtures`
- Engine-version upgrade matrix — everything pinned to 4.7.2 (S001, S005) — `grep -rlE 'version_matrix|upgrade_matrix' corpus/fixtures`
- Input record/replay — `r100b_seq`/`r101_seqfull` pin authored GUI sequences, no recorder/replayer — `grep -rlE 'record_input|input_replay' corpus/fixtures`
- Localization — `grep -rlE 'TranslationServer|set_locale' corpus/fixtures/*.gd`
- Shaders/materials output — setters touched, no compiled output validated — `grep -rlE 'shader_type|VisualShader' corpus/fixtures/*.gd`
- Multiplayer beyond r88 loopback — 3 `r88_surfaces_mp_*` rows only — `grep -c "r88_surfaces_mp" corpus/fixtures/run_battery.py`
- **Advanced r105:** TileMapLayer body-RID attribution (was open: r92 probed the mover's RID) → `knowledge/2026-10-19-tilemaplayer-body-rid-attribution.md`; physics replay boundary (was open: one fixed trajectory fingerprint) → `knowledge/2026-10-19-physics-replay-boundary.md`.
