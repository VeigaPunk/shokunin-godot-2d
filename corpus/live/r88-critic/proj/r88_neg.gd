extends SceneTree
# r88-author battery probe — the r88 census's remaining measured surfaces,
# armed per lane convention (one arm per process):
#   godot --headless --path <scratch> --script res://r88_surfaces.gd -- --arm=<name>
# Prints `R88S` diagnostic lines (volatile counters kept out of the pin) and
# one final `PASS r88_surfaces <arm> ...` line. No object ids/RIDs/pointers.
#
# Provenance: arms adapted from the r88 dead-seat probe
# (corpus/live/r88-scout/proj/r88_probe.gd sha256 3584d229…) as measured x3 by
# r88-scout, with three deliberate changes:
#   1. Arm dispatch uses OS.get_cmdline_user_args() + `--arm=` prefix scan —
#      the dead probe's get_cmdline_args()/two-token form could never fire
#      under the battery's post-`--` launch shape (scout §0, hazard 1).
#   2. light_props carries the documented `range_height`->`height` fix
#      (scout §3.14 — the verbatim leg aborts mid-arm and hangs, rc=124).
#   3. mp_loopback normalizes the random client peer id to `<C>` before
#      printing (scout §3.10 — uid_c is the only unstable field), and
#      mp_spawner adds the registered-scene spawn() positive control the
#      scout left unrun (F6 / directive 4).
# geo_* arms are r89's lane; rb_* arms are r90's lane — neither is here.

var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _fail(reason: String) -> void:
	print("FAIL r88_surfaces %s reason=%s" % [arm, reason])
	quit(1)

func _finish(line: String) -> void:
	print("PASS r88_surfaces " + line)
	quit(0)

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _body(x: float, y: float, gs := 1.0) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	cs.shape = circle
	b.add_child(cs)
	b.position = Vector2(x, y)
	b.gravity_scale = gs
	return b

func _run() -> void:
	# arm= is the first printed line: a silent census-fallback is visible in
	# receipts, and an empty arm is a hard failure (scout directive 9).
	print("arm=%s" % arm)
	if arm == "":
		_fail("empty_arm")
		return
	match arm:
		"mp_offline":
			await _arm_mp_offline()
		"mp_loopback":
			await _arm_mp_loopback()
		"mp_spawner":
			await _arm_mp_spawner()
		"light_props":
			await _arm_light_props()
		"sprite_meta":
			await _arm_sprite_meta()
		"sprite_phys":
			await _arm_sprite_phys()
		"audio_pos":
			await _arm_audio_pos()
		"vis_not":
			await _arm_vis_not()
		_:
			_fail("unknown_arm")

# ---------- multiplayer ----------

func _arm_mp_offline() -> void:
	var off := OfflineMultiplayerPeer.new()
	var api := SceneMultiplayer.new()
	api.multiplayer_peer = off
	print("R88S mp_offline status=%d uid=%d mode=%d chan=%d" % [
		off.get_connection_status(), api.get_unique_id(),
		off.get_transfer_mode(), off.get_transfer_channel()])
	root.get_multiplayer().multiplayer_peer = OfflineMultiplayerPeer.new()
	await process_frame
	var pre := "status=%d uid=%d mode=%d chan=%d" % [
		off.get_connection_status(), api.get_unique_id(),
		off.get_transfer_mode(), off.get_transfer_channel()]
	_finish("mp_offline %s tree_uid=%d is_server=%s tree_status=%d" % [
		pre, root.get_multiplayer().get_unique_id(),
		root.get_multiplayer().is_server(),
		root.get_multiplayer().multiplayer_peer.get_connection_status()])

class MpLimb extends Node:
	var rpc_log: Array = []
	@rpc("any_peer", "call_local", "reliable")
	func ping(n: int, tag: String) -> void:
		rpc_log.append("ping%d:%s" % [n, tag])
	@rpc("any_peer", "call_local", "unreliable")
	func uping(n: int) -> void:
		rpc_log.append("u%d" % n)

func _arm_mp_loopback() -> void:
	var srv_branch := Node.new(); srv_branch.name = "srv"
	var cli_branch := Node.new(); cli_branch.name = "cli"
	root.add_child(srv_branch); root.add_child(cli_branch)
	var limb_s := MpLimb.new(); limb_s.name = "limb"; srv_branch.add_child(limb_s)
	var limb_c := MpLimb.new(); limb_c.name = "limb"; cli_branch.add_child(limb_c)
	var server := ENetMultiplayerPeer.new()
	var rc_s := server.create_server(41777, 4)
	var api_s := SceneMultiplayer.new()
	api_s.multiplayer_peer = server
	set_multiplayer(api_s, "/root/srv")
	var client := ENetMultiplayerPeer.new()
	var rc_c := client.create_client("127.0.0.1", 41777)
	var api_c := SceneMultiplayer.new()
	api_c.multiplayer_peer = client
	set_multiplayer(api_c, "/root/cli")
	var uid_c := api_c.get_unique_id()
	print("R88S mp_lb rc=[%d,%d] uid_s=%d uid_c=%d" % [rc_s, rc_c, api_s.get_unique_id(), uid_c])
	var conn_order: Array = []
	api_s.peer_connected.connect(func(id): conn_order.append("s_conn%d" % id))
	api_c.peer_connected.connect(func(id): conn_order.append("c_conn%d" % id))
	api_c.connected_to_server.connect(func(): conn_order.append("c_on_srv"))
	api_s.connected_to_server.connect(func(): conn_order.append("s_on_srv"))
	var frames := 0
	while api_c.get_unique_id() == 0 and frames < 300:
		await process_frame; frames += 1
	while conn_order.size() < 3 and frames < 600:
		await process_frame; frames += 1
	var auth_uid := api_c.get_unique_id()
	limb_c.rpc_id(1, "ping", 7, "c2s")
	limb_s.rpc_id(auth_uid, "ping", 9, "s2c")
	limb_c.rpc("ping", 5, "call_local_c")
	var wait := 0
	while (limb_s.rpc_log.size() < 2 or limb_c.rpc_log.size() < 2) and wait < 600:
		await process_frame; wait += 1
	api_s.peer_disconnected.connect(func(id): conn_order.append("s_disc%d" % id))
	api_c.server_disconnected.connect(func(): conn_order.append("c_srvdisc"))
	server.disconnect_peer(api_c.get_unique_id())
	wait = 0
	while conn_order.size() < 5 and wait < 600:
		await process_frame; wait += 1
	# Volatile diagnostics: the raw client uid and the scheduling counters are
	# mode candidates, not pins (scout hazard 6) — diagnostic line only.
	print("R88S mp_lb raw_order=%s raw_uid=%d frames=%d wait=%d" % [
		conn_order, auth_uid, frames, wait])
	# Pinned payload: peer-id-normalized ordering + rpc logs (scout §3.10).
	# NB: get_unique_id() errors once the peer is inactive — auth_uid was
	# captured while connected and is the only safe post-disconnect value.
	var norm_order: Array = []
	for e in conn_order:
		norm_order.append(String(e).replace(str(auth_uid), "<C>"))
	_finish("mp_loopback rc=[%d,%d] uid_s=%d uid_after_dyn=%s order=%s limb_s=%s limb_c=%s" % [
		rc_s, rc_c, api_s.get_unique_id(), str(auth_uid > 1),
		str(norm_order), str(limb_s.rpc_log), str(limb_c.rpc_log)])

func _arm_mp_spawner() -> void:
	var srv := Node.new(); srv.name = "srv"
	var cli := Node.new(); cli.name = "cli"
	var cont_s := Node.new(); cont_s.name = "cont"; srv.add_child(cont_s)
	var cont_c := Node.new(); cont_c.name = "cont"; cli.add_child(cont_c)
	var sp_s := MultiplayerSpawner.new(); sp_s.name = "sp"; srv.add_child(sp_s)
	var sp_c := MultiplayerSpawner.new(); sp_c.name = "sp"; cli.add_child(sp_c)
	root.add_child(srv); root.add_child(cli)
	sp_s.spawn_path = cont_s.get_path()
	sp_c.spawn_path = cont_c.get_path()
	# Registered-scene positive control (scout F6): both peers register the
	# same spawnable scene before spawn() is invoked.
	sp_s.add_spawnable_scene("res://r88_spawnable.tscn")
	sp_c.add_spawnable_scene("res://r88_spawnable.tscn")
	var server := ENetMultiplayerPeer.new(); server.create_server(41778, 4)
	var api_s := SceneMultiplayer.new(); api_s.multiplayer_peer = server
	set_multiplayer(api_s, "/root/srv")
	var client := ENetMultiplayerPeer.new(); client.create_client("127.0.0.1", 41778)
	var api_c := SceneMultiplayer.new(); api_c.multiplayer_peer = client
	set_multiplayer(api_c, "/root/cli")
	var frames := 0
	while api_c.get_unique_id() == 0 and frames < 300:
		await process_frame; frames += 1
	# Negative control: an unregistered add_child under spawn_path silently
	# never replicates (scout §3.11 / hazard 5). bound_hit is the loop's own
	# constant bound — deterministic by construction, unlike the wait counts.
	var neg := Node2D.new(); neg.name = "spawned_one"; neg.position = Vector2(33, 44)
	cont_s.add_child(neg)
	# Bound 300 idle frames (~2.3s here): generous vs the measured replication
	# latency (~4 frames) while keeping the arm well inside the battery's 8s
	# per-case bound even when a replication leg is broken.
	var neg_wait := 0
	while cont_c.get_child_count() == 0 and neg_wait < 300:
		await process_frame; neg_wait += 1
	var neg_c_children := cont_c.get_child_count()
	# Positive control: a scene-instantiated add_child under spawn_path
	# auto-tracks when its scene_file_path is registered — measured: client
	# receives a SpawnableOne twin at the baked-in (33,44). NB: in 4.7.2
	# MultiplayerSpawner.spawn() itself refuses without a spawn_function
	# (ERROR at multiplayer_spawner.cpp:325) — the registered-scene path is
	# the add_child auto-track, exercised here.
	var spawned: Node = load("res://r88_spawnable.tscn").instantiate()
	cont_s.add_child(spawned)
	var pos_wait := 0
	while cont_c.get_child_count() == 0 and pos_wait < 300:
		await process_frame; pos_wait += 1
	var c_got := ""
	var c_pos := ""
	if cont_c.get_child_count() > 0:
		var c = cont_c.get_child(0)
		c_got = String(c.name)
		c_pos = _v2(c.position) if c is Node2D else "nonnode2d"
	# Synchronizer replication without spawner involvement (scout §3.11).
	var sync_s := MultiplayerSynchronizer.new(); sync_s.name = "sync"
	var sync_c := MultiplayerSynchronizer.new(); sync_c.name = "sync"
	var prop_s := Node2D.new(); prop_s.name = "prop"; prop_s.position = Vector2(1, 2)
	var prop_c := Node2D.new(); prop_c.name = "prop"
	cont_s.add_child(prop_s); cont_c.add_child(prop_c)
	sync_s.root_path = prop_s.get_path(); sync_c.root_path = prop_c.get_path()
	cont_s.add_child(sync_s); cont_c.add_child(sync_c)
	var rcfg := SceneReplicationConfig.new()
	rcfg.add_property(NodePath(":position"))
	sync_s.replication_config = rcfg
	sync_c.replication_config = SceneReplicationConfig.new()
	(sync_c.replication_config as SceneReplicationConfig).add_property(NodePath(":position"))
	prop_s.position = Vector2(111, 222)
	var sync_wait := 0
	while prop_c.position != Vector2(111, 222) and sync_wait < 300:
		await process_frame; sync_wait += 1
	print("R88S mp_spawner frames=%d neg_wait=%d pos_wait=%d sync_wait=%d srv_children=%d spawned_srv=%s" % [
		frames, neg_wait, pos_wait, sync_wait, cont_s.get_child_count(),
		String(spawned.name) if is_instance_valid(spawned) else "<null>"])
	_finish("mp_spawner neg[c_children=%d srv_children=%d bound_hit=%d] pos[added=%s c_got=%s c_pos=%s] sync[pos=%s]" % [
		neg_c_children, cont_s.get_child_count(), neg_wait,
		String(spawned.name) if is_instance_valid(spawned) else "<null>",
		c_got, c_pos, _v2(prop_c.position)])

# ---------- 2D lights / occluder vs physics (height fix applied) ----------

func _arm_light_props() -> void:
	var pl := PointLight2D.new()
	var dl := DirectionalLight2D.new()
	var occ := LightOccluder2D.new()
	var poly := OccluderPolygon2D.new()
	poly.polygon = PackedVector2Array([Vector2(0, 0), Vector2(10, 0), Vector2(10, 10)])
	poly.closed = true
	occ.occluder = poly
	var cm := CanvasModulate.new()
	root.add_child(pl); root.add_child(dl); root.add_child(occ); root.add_child(cm)
	pl.enabled = true
	pl.shadow_enabled = true
	pl.energy = 2.5
	pl.texture_scale = 1.5
	pl.height = 42.0  # the verbatim leg's `range_height` is not a 4.7.2 property
	pl.color = Color(0.5, 0.25, 0.125)
	pl.range_item_cull_mask = 4
	dl.energy = 0.75
	occ.occluder_light_mask = 2
	occ.sdf_collision = true
	cm.color = Color(0.2, 0.2, 0.4)
	var pl_str := "pl=[en=%s sh=%s en2=%.3f ts=%.3f h=%.3f col=%s mask=%d mo=%s]" % [
		pl.enabled, pl.shadow_enabled, pl.energy, pl.texture_scale, pl.height,
		pl.color, pl.range_item_cull_mask, pl.shadow_item_cull_mask]
	var dl_str := "dl=[en=%.3f mask=%d]" % [dl.energy, dl.range_item_cull_mask]
	var occ_str := "occ=[closed=%s cull=%d mask=%d sdf=%s n=%d]" % [
		poly.closed, poly.cull_mode, occ.occluder_light_mask, occ.sdf_collision, poly.polygon.size()]
	var cm_str := "cm=[col=%s]" % cm.color
	print("R88S light_props %s %s %s %s" % [pl_str, dl_str, occ_str, cm_str])
	var b := _body(0, -100)
	occ.position = Vector2(0, -40)
	root.add_child(b)
	for i in 40:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q := PhysicsRayQueryParameters2D.create(Vector2(-50, -80), Vector2(-50, 60))
	var hit := dss.intersect_ray(q)
	_finish("light_props %s %s %s %s body_y=%.4f ray_through_occluder=%s occ_cls=%s occ_is_co=%s" % [
		pl_str, dl_str, occ_str, cm_str,
		b.global_position.y, hit.is_empty(), occ.get_class(),
		is_instance_of(occ, CollisionObject2D)])

# ---------- sprite metadata vs physics ----------

func _arm_sprite_meta() -> void:
	var img := Image.create(32, 16, false, Image.FORMAT_RGBA8)
	var tex := ImageTexture.create_from_image(img)
	var s := Sprite2D.new()
	s.texture = tex
	root.add_child(s)
	var fired: Array = []
	s.frame_changed.connect(func(): fired.append("fc"))
	s.texture_changed.connect(func(): fired.append("tc"))
	s.region_enabled = true
	s.region_rect = Rect2(4, 4, 8, 8)
	s.hframes = 4
	s.vframes = 2
	s.frame = 5
	s.flip_h = true
	s.flip_v = true
	s.offset = Vector2(3, -2)
	s.centered = false
	var rb := "readback=[re=%s rr=%s hf=%d vf=%d f=%d fc=%s fh=%s fv=%s off=%s cen=%s]" % [
		s.region_enabled, s.region_rect, s.hframes, s.vframes, s.frame, s.frame_coords,
		s.flip_h, s.flip_v, s.offset, s.centered]
	var s2 := Sprite2D.new()
	s2.texture = tex
	root.add_child(s2)
	s2.scale = Vector2(-1, 1)
	_finish("sprite_meta %s xf=%s signals=%s sneg_xf=%s get_rect=%s s2_rect=%s" % [
		rb, s.global_transform, str(fired), s2.global_transform, s.get_rect(), s2.get_rect()])

func _arm_sprite_phys() -> void:
	# Body + sprite child; sprite metadata varied across four variants of the
	# same drop. The `regioned` variant sets frame=3 with hframes*vframes=2 —
	# the engine refuses loudly (expected_errors whitelists the one ERROR;
	# scout §3.13 / directive 7).
	var results: PackedStringArray = []
	for variant in ["plain", "flipped", "regioned", "scaled_neg"]:
		var b := _body(variant.length() * 50, -50)
		var spr := Sprite2D.new()
		var img := Image.create(16, 16, false, Image.FORMAT_RGBA8)
		spr.texture = ImageTexture.create_from_image(img)
		b.add_child(spr)
		match variant:
			"flipped": spr.flip_h = true; spr.flip_v = true
			"regioned": spr.region_enabled = true; spr.region_rect = Rect2(2, 2, 4, 4); spr.hframes = 2; spr.frame = 3
			"scaled_neg": spr.scale = Vector2(-1, -1)
		root.add_child(b)
	for i in 30:
		await physics_frame
	for b in root.get_children():
		if b is RigidBody2D:
			var spr: Sprite2D = null
			for c in b.get_children():
				if c is Sprite2D: spr = c
			results.append("pos=%.4f,%.4f spr_gt=%s spr_rel=%s" % [
				b.global_position.x, b.global_position.y, spr.global_transform, spr.transform])
	_finish("sprite_phys [%s]" % "|".join(results))

# ---------- positional audio (negative-only pins — Dummy driver) ----------

func _arm_audio_pos() -> void:
	# Headless-null surface (scout §3.15): under the Dummy driver no buffer
	# advances — playing clears and every peak is -200 dB. Only negative pins
	# are authorable on this host; never author a positive row (directive 5).
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_8_BITS
	wav.mix_rate = 44100
	wav.stereo = false
	var data := PackedByteArray()
	for i in 44100 / 10:  # 0.1 s sine
		data.append(int(127 + 100 * sin(i * 440.0 * TAU / 44100.0)))
	wav.data = data
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	var listener := AudioListener2D.new()
	root.add_child(listener)
	listener.position = Vector2(0, 0)
	listener.make_current()
	var p := AudioStreamPlayer2D.new()
	p.stream = wav
	p.position = Vector2(0, 0)
	p.max_distance = 2000.0
	p.attenuation = 1.0
	root.add_child(p)
	# r88-critic vacuity control: p.play() deliberately removed
	var peaks: Array = []
	for i in 20:
		await process_frame
		if i % 5 == 4:
			peaks.append("%.2f" % AudioServer.get_bus_peak_volume_left_db(0, 0))
	var near := "playing=%s pos=%.3f peaks_near=[%s]" % [
		p.playing, p.get_playback_position(), ",".join(peaks)]
	p.position = Vector2(1800, 0)
	peaks.clear()
	for i in 20:
		await process_frame
		if i % 5 == 4:
			peaks.append("%.2f" % AudioServer.get_bus_peak_volume_left_db(0, 0))
	p.stop()
	_finish("audio_pos %s peaks_far=[%s] listen_pos=%s listener_current=%s" % [
		near, ",".join(peaks), _v2(listener.global_position), listener.is_current()])

# ---------- visibility notifier/enabler (negative-only pins — no screen) ----------

var _vis_events: Array = []
var _vis_pf := 0

func _arm_vis_not() -> void:
	# Headless-null surface (scout §3.16): no screen exists — is_on_screen()
	# is always false, the enabler never fires. Only negative pins are
	# authorable on this host; never author a positive row (directive 5).
	var vn := VisibleOnScreenNotifier2D.new()
	vn.rect = Rect2(-16, -16, 32, 32)
	vn.screen_entered.connect(func(): _vis_events.append("in@%d" % _vis_pf))
	vn.screen_exited.connect(func(): _vis_events.append("out@%d" % _vis_pf))
	var b := _body(0, 0)
	b.add_child(vn)
	b.freeze = true
	root.add_child(b)
	var en := VisibleOnScreenEnabler2D.new()
	en.rect = Rect2(-8, -8, 16, 16)
	var target := Node2D.new()
	en.enable_node_path = NodePath("../target")
	var holder := Node2D.new(); holder.name = "h"
	holder.add_child(en); holder.add_child(target); target.name = "target"
	target.set_process(false)
	root.add_child(holder)
	var on0 := "on_screen0=%s en_onscreen=%s" % [vn.is_on_screen(), en.is_on_screen()]
	for i in 30:
		await physics_frame
		_vis_pf += 1
	b.global_position = Vector2(500, 0)
	for i in 10:
		await physics_frame
		_vis_pf += 1
	b.global_position = Vector2(0, 0)
	for i in 10:
		await physics_frame
		_vis_pf += 1
	_finish("vis_not %s events=%s on_screen_end=%s enabler_proc=%s" % [
		on0, str(_vis_events), vn.is_on_screen(), target.is_processing()])
