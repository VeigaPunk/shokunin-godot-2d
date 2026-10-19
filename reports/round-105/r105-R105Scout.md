# r105 seat report — R105Scout (scout)

Verbatim final output of L2 `W2RoundGameDev2d.R105Scout` (round 105, batched swarm; transcript `history://W2RoundGameDev2d.R105Scout` is session-scoped and not evidence — this file is).

---

**[OBS]** The CASES AST census has 585 unique rows in 64 prefix buckets. The domain assignments below are **[INF]**—based on row names, fixture behavior and round notes—not a claim that every behavior is covered. **[UNK]** LSP is not mounted here, and I did not run fixtures. No files were changed.

```markdown
## Coverage map

Fixtures are relative to `corpus/fixtures/`; lesson paths are relative to `corpus/`.

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

`negative_` and `r88_surfaces_` are umbrella prefixes split by arm target; each row is assigned once.
```

```markdown
## Frontier

- **Rendered output / visual canary** — open: `r100_gui_render` reports `img_null=1`, `rd_null=1`, `screens=0`; the PNG writes found by the sweep create synthetic assets, not a rendered-image assertion. Sweep: `S1`.
- **Renderer performance** — open: FPS/fixed-FPS context fields exist, but no renderer time, GPU cost, draw-call benchmark or performance budget is asserted. Sweep: `S2`.
- **Clean-checkout import → export → launch** — open: registered export/launch rows exercise generated scratch projects; no clean checkout of the lane project is staged. Sweep: `S3`.
- **GUT/gdUnit4 runner contracts** — open: no GUT/gdUnit4 plugin or runner integration appears in fixture sources; the registered runner is custom. Sweep: `S4`.
- **Physics replay determinism** — open: `r95b_order_rigid` fingerprints one fixed-run trajectory, not a reusable record/replay harness or cross-run state replay. Sweep: `S5`.
- **TileMapLayer body-RID attribution** — open: r92 probes a manually created, untracked RID (`has_body_rid=0`; origin coords), not a contact RID mapped back to the TileMapLayer cell. Sweep: `S6`.
- **Engine-version upgrade matrix** — open: lane history and export receipts are pinned to Godot 4.7.2; no cross-version matrix or upgrade replay is registered. Sweep: `S7`.
- **Deterministic input replay** — open: `r100b_seq`/`r101_seqfull` pin authored GUI sequences, but no reusable input recorder/replayer or gameplay-session replay is covered. Sweep: `S8`.
- **Localization** — open: no locale switch or translated-string behavior is exercised; API-name inventory is not localization coverage. Sweep: `S9`.
- **Shaders/materials** — open: CanvasItem material/shader setters are touched, but no compiled shader/material output is validated. Sweep: `S10`.
- **Multiplayer (partial, not absent)** — r88 has three offline/ENet loopback/spawner rows; multi-host topologies, reconnect/failure behavior and broader network gameplay remain open. Sweep: `S11`.
```

```markdown
## Province split proposal

### Core — game-dev-2d
Own the 2D runtime contract: loop, input, 2D physics, scenes, camera, UI, levels/TileMapLayer, animation, audio, navigation, particles, resources/UID, save/load, and 2D export/launch. Scope current claims to the registered Godot 4.7.2 fixtures and their headless assertions.

### Frontier — game-dev-2d backlog, with explicit cross-lane handoffs
Prioritize TileMapLayer body-RID attribution, physics/input replay, clean-checkout import→export→launch, engine-version matrix, renderer output/performance, shader/material execution, and broader multiplayer. Record partial r88 ENet coverage rather than calling multiplayer wholly absent.

### Adjacent — owned by other lanes
- **3D lane:** 3D rendering, physics and gameplay contracts.
- **lore:** narrative/text content and localization catalogs; runtime locale wiring remains an explicit technical frontier if requested.
- **art-east-asian-design:** visual direction, asset/style review, rendered canary criteria, and shader/material appearance.
- **harness-integrity:** GUT/gdUnit4 runner contracts and shared harness/receipt integrity. game-dev-2d supplies feature-specific fixtures; it does not own the generic runner contract.
```

```text
Commands / sweeps used (all source searches were read-only).

AST census, run from the lane root:
python3 -c 'import ast,re; t=ast.parse(open("corpus/fixtures/run_battery.py").read()); n=next(x.value for x in t.body if isinstance(x,ast.Assign) and any(getattr(y,"id",None)=="CASES" for y in x.targets)); a=[e.elts[0].value for e in n.elts if isinstance(e,ast.Tuple) and len(e.elts)==5]; p=lambda s:(m.group(1) if (m:=re.match(r"(r\d+[a-z]?_[a-z0-9]+_|[a-z][a-z0-9]*_)",s)) else s); print("rows={}, unique_names={}, prefix_buckets={}".format(len(a),len(set(a)),len({p(s) for s in a})))'
Output: rows=585, unique_names=585, prefix_buckets=64.

First-landing history: functions.grep over LOG.md for Round headings and r57/r58/r61/r62/r79–r104 entries; table cites the resulting LOG.md line anchors.
S1 functions.grep(path=corpus/fixtures, pattern='screenshot|Image\\.save|save_png|capture_screen|get_image\\(')
S2 functions.grep(path=corpus/fixtures, pattern='frame_time|frametime|draw_calls|render_time|gpu_time|throughput|benchmark|fps=')
S3 functions.grep(path=corpus/fixtures, pattern='git clone|git worktree|clone_checkout|clean_checkout|fresh_checkout')
S4 functions.grep(path=corpus/fixtures, pattern='GUT|gdUnit4|gdunit4|addons/gut|addons/gdUnit|GutRunner')
S5 functions.grep(path=phys2d_events.gd;phys2d_motion.gd;phys2d_joints.gd;phys2d_backends.gd;dss_lattice.gd;rb_lattice.gd;r95b_order.gd, pattern='replay.*physics|physics.*replay|record.*input|input.*record|transcript.*replay')
S6 functions.grep(path=tilemap_lattice.gd;run_battery.py, pattern='get_collider_rid|body_rid|collider_rid')
S7 functions.grep(path=corpus/fixtures;LOG.md, pattern='version_matrix|upgrade_matrix|engine.{0,20}matrix|matrix.{0,20}engine|Godot 4\\.[0-9]+.*(matrix|upgrade)')
S8 functions.grep(path=corpus/fixtures, pattern='record_input|input_record|serialize_input|deserialize_input|input_replay|replay_input|InputEvent.*to_bytes|InputEvent.*serialize')
S9 functions.grep(path=corpus/fixtures, pattern='TranslationServer|Translation|locale|gettext|(^|[^A-Za-z_])tr\\(')
S10 functions.grep(path=corpus/fixtures, pattern='shader_type|ShaderMaterial|VisualShader|set_instance_shader_parameter|material.*shader|shader.*material')
S11 functions.grep(path=r88_surfaces.gd;run_battery.py, pattern='ENet|Multiplayer|multiplayer_peer|create_server|create_client|RPC|rpc\\(')

LSP check: `read xd://lsp` returned “No such tool”; the mounted-device list has no LSP route. Surface assignments are therefore [INFERENCE] from literal CASES names, fixtures and LOG comments; no semantic LSP proof was available. No files were touched.
```
