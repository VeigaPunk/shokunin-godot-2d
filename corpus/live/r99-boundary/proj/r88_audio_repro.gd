extends SceneTree
# r88 scout probe — discovery arms for the r88 candidate surfaces.
# Launch: godot --headless --path proj --script res://r88_probe.gd -- --arm=<name>
# Prints `R88 <arm> ...` lines. No object ids/RIDs/pointers (byte-stability).

var arm := ""
var _err_count := 0

func _initialize() -> void:
	var idx := OS.get_cmdline_args().find("--arm")
	if idx >= 0 and idx + 1 < OS.get_cmdline_args().size():
		arm = OS.get_cmdline_args()[idx + 1]
	_run.call_deferred()

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _poly2str(arr: Array) -> String:
	# arr: Array of PackedVector2Array -> "n=3|verts=(x,y;...)|..."
	var parts: PackedStringArray = []
	for poly in arr:
		var verts: PackedStringArray = []
		for v in poly:
			verts.append(_v2(v))
		parts.append("n%d[%s]" % [poly.size(), ";".join(verts)])
	return "k=%d{%s}" % [arr.size(), "|".join(parts)]

func _pva2str(poly: PackedVector2Array) -> String:
	var verts: PackedStringArray = []
	for v in poly:
		verts.append(_v2(v))
	return "n%d[%s]" % [poly.size(), ";".join(verts)]

func _pva2str_area(poly: PackedVector2Array) -> String:
	# signed shoelace area appended
	var a := 0.0
	for i in poly.size():
		var p := poly[i]
		var q := poly[(i + 1) % poly.size()]
		a += p.x * q.y - q.x * p.y
	return "%s area=%.4f" % [_pva2str(poly), a / 2.0]

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
	match arm:
		"geo_ops": _arm_geo_ops()
		"geo_edge": _arm_geo_edge()
		"geo_trig": _arm_geo_trig()
		"geo_pred": _arm_geo_pred()
		"geo_phys": _arm_geo_phys()
		"rb_gravity": _arm_rb_gravity()
		"rb_com": _arm_rb_com()
		"rb_integrator": _arm_rb_integrator()
		"mp_offline": _arm_mp_offline()
		"mp_loopback": _arm_mp_loopback()
		"mp_spawner": _arm_mp_spawner()
		"sprite_meta": _arm_sprite_meta()
		"sprite_phys": _arm_sprite_phys()
		"light_props": _arm_light_props()
		"audio_pos": _arm_audio_pos()
		"vis_not": _arm_vis_not()
		"census": _arm_census()
		_: _arm_census()

# ---------- geometry ----------

func _sq(cx: float, cy: float, r: float) -> PackedVector2Array:
	return PackedVector2Array([Vector2(cx - r, cy - r), Vector2(cx + r, cy - r),
		Vector2(cx + r, cy + r), Vector2(cx - r, cy + r)])

func _arm_geo_ops() -> void:
	var a := _sq(0, 0, 10)
	var b := _sq(8, 0, 10)
	print("R88 geo_ops clip=", _poly2str(Geometry2D.clip_polygons(a, b)))
	print("R88 geo_ops merge=", _poly2str(Geometry2D.merge_polygons(a, b)))
	print("R88 geo_ops inter=", _poly2str(Geometry2D.intersect_polygons(a, b)))
	print("R88 geo_ops excl=", _poly2str(Geometry2D.exclude_polygons(a, b)))
	var tri := Geometry2D.triangulate_polygon(a)
	print("R88 geo_ops triang_idx=", tri)
	print("R88 geo_ops offset2=", _poly2str(Geometry2D.offset_polygon(a, 2.0)))
	print("R88 geo_ops offsetneg=", _poly2str(Geometry2D.offset_polygon(a, -2.0)))
	quit()

func _arm_geo_edge() -> void:
	var empty := PackedVector2Array()
	var degen := PackedVector2Array([Vector2(0, 0), Vector2(1, 0), Vector2(2, 0)])
	var bowtie := PackedVector2Array([Vector2(0, 0), Vector2(10, 10), Vector2(10, 0), Vector2(0, 10)])
	var sq := _sq(0, 0, 10)
	print("R88 geo_edge clip_empty=", _poly2str(Geometry2D.clip_polygons(sq, empty)))
	print("R88 geo_edge merge_empty=", _poly2str(Geometry2D.merge_polygons(sq, empty)))
	print("R88 geo_edge tri_degen=", Geometry2D.triangulate_polygon(degen))
	print("R88 geo_edge tri_bowtie=", Geometry2D.triangulate_polygon(bowtie))
	print("R88 geo_edge clip_bowtie=", _poly2str(Geometry2D.clip_polygons(bowtie, sq)))
	print("R88 geo_edge pip_bowtie=", Geometry2D.is_point_in_polygon(Vector2(5, 5), bowtie),
		" pip_degen=", Geometry2D.is_point_in_polygon(Vector2(1, 0), degen))
	print("R88 geo_edge cw_sq=", Geometry2D.is_polygon_clockwise(sq))
	var sqcw := PackedVector2Array([sq[0], sq[3], sq[2], sq[1]])
	print("R88 geo_edge cw_rev=", Geometry2D.is_polygon_clockwise(sqcw),
		" clip_rev=", _poly2str(Geometry2D.clip_polygons(sqcw, _sq(8, 0, 10))))
	quit()

func _arm_geo_trig() -> void:
	var concave := PackedVector2Array([Vector2(0, 0), Vector2(20, 0), Vector2(20, 20),
		Vector2(10, 8), Vector2(0, 20)])
	print("R88 geo_trig hull=", _pva2str(Geometry2D.convex_hull(concave)))
	print("R88 geo_trig decomp=", _poly2str(Geometry2D.decompose_polygon_in_convex(concave)))
	print("R88 geo_trig tri=", Geometry2D.triangulate_polygon(concave))
	var pts := PackedVector2Array([Vector2(0, 0), Vector2(30, 0), Vector2(15, 26),
		Vector2(8, 8), Vector2(22, 8)])
	print("R88 geo_trig delaunay=", Geometry2D.triangulate_delaunay(pts))
	print("R88 geo_trig atlas=", Geometry2D.make_atlas(
		[_sq(0, 0, 10), _sq(50, 0, 5), PackedVector2Array([Vector2(0, 0), Vector2(9, 3), Vector2(2, 7)])]))
	quit()

func _arm_geo_pred() -> void:
	var sq := _sq(0, 0, 10)
	print("R88 geo_pred pip_in=", Geometry2D.is_point_in_polygon(Vector2(5, 5), sq),
		" pip_out=", Geometry2D.is_point_in_polygon(Vector2(15, 5), sq),
		" pip_edge=", Geometry2D.is_point_in_polygon(Vector2(10, 5), sq),
		" pip_corner=", Geometry2D.is_point_in_polygon(Vector2(10, 10), sq))
	print("R88 geo_pred pic=", Geometry2D.is_point_in_circle(Vector2(3, 4), Vector2(0, 0), 5.0),
		" pic_out=", Geometry2D.is_point_in_circle(Vector2(6, 0), Vector2(0, 0), 5.0))
	var li = Geometry2D.line_intersects_line(Vector2(0, 0), Vector2(1, 0), Vector2(2, -1), Vector2(0, 1))
	var si = Geometry2D.segment_intersects_segment(Vector2(0, 0), Vector2(4, 0), Vector2(2, -1), Vector2(2, 1))
	var smi = Geometry2D.segment_intersects_segment(Vector2(0, 0), Vector2(1, 0), Vector2(2, -1), Vector2(2, 1))
	print("R88 geo_pred line_isect=", li, " seg_isect=", si, " seg_miss=", smi)
	print("R88 geo_pred closest_seg=", Geometry2D.get_closest_point_to_segment(Vector2(3, 4), Vector2(0, 0), Vector2(10, 0)),
		" uncapped=", Geometry2D.get_closest_point_to_segment_uncapped(Vector2(13, 4), Vector2(0, 0), Vector2(10, 0)),
		" segseg=", Geometry2D.get_closest_points_between_segments(Vector2(0, 0), Vector2(10, 0), Vector2(5, -2), Vector2(5, 2)))
	print("R88 geo_pred tri_inside=", Geometry2D.point_is_inside_triangle(Vector2(1, 1), Vector2(0, 0), Vector2(4, 0), Vector2(0, 4)),
		" tri_out=", Geometry2D.point_is_inside_triangle(Vector2(4, 4), Vector2(0, 0), Vector2(4, 0), Vector2(0, 4)))
	print("R88 geo_pred bresenham=", Geometry2D.bresenham_line(Vector2(0, 0), Vector2(5, 3)))
	print("R88 geo_pred sic=", Geometry2D.segment_intersects_circle(Vector2(-10, 0), Vector2(10, 0), Vector2(0, 0), 5.0),
		" sic_miss=", Geometry2D.segment_intersects_circle(Vector2(-10, 10), Vector2(10, 10), Vector2(0, 0), 5.0))
	quit()

func _arm_geo_phys() -> void:
	# Build static walls from clip_polygons output; drop a body; measure rest/contact.
	var wall_shape = Geometry2D.clip_polygons(_sq(0, 0, 60), _sq(0, -30, 60))
	var st := StaticBody2D.new()
	var pol := CollisionPolygon2D.new()
	if wall_shape.size() > 0:
		pol.polygon = wall_shape[0]
	st.add_child(pol)
	st.position = Vector2(0, 60)
	root.add_child(st)
	var b := _body(0, -100)
	root.add_child(b)
	for i in 60:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q := PhysicsPointQueryParameters2D.new()
	q.position = b.global_position
	var hits := dss.intersect_point(q)
	print("R88 geo_phys rest_y=%.4f" % b.global_position.y,
		" vel=%.4f,%.4f" % [b.linear_velocity.x, b.linear_velocity.y],
		" clip_result=%s" % _poly2str(wall_shape),
		" self_hit=", hits.size())
	quit()

# ---------- rigid body gravity / com / integrator ----------

func _arm_rb_gravity() -> void:
	var bodies := []
	var scales := [0.0, 1.0, 2.0, -1.0]
	for i in scales.size():
		var b := _body(-300 + i * 60, 0, scales[i])
		bodies.append(b)
		root.add_child(b)
	for i in 30:
		await physics_frame
	var pos: PackedStringArray = []
	for b in bodies:
		pos.append("%.4f,%.4f" % [b.global_position.x, b.global_position.y])
	print("R88 rb_gravity pos30=[%s]" % "|".join(pos))
	for i in 30:
		await physics_frame
	pos.clear()
	for b in bodies:
		pos.append("%.4f,%.4f" % [b.global_position.x, b.global_position.y])
	print("R88 rb_gravity pos60=[%s]" % "|".join(pos))
	quit()

var _integ_state := {}

func _arm_rb_com() -> void:
	# AUTO vs CUSTOM center_of_mass: read back state.center_of_mass_local;
	# offset com + off-center impulse -> angular velocity change.
	var auto := _body(0, 0)
	auto.sleeping = false
	root.add_child(auto)
	var cust := _body(200, 0)
	cust.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
	cust.center_of_mass = Vector2(4, 0)
	root.add_child(cust)
	var third := _body(400, 0)
	third.center_of_mass_mode = RigidBody2D.CENTER_OF_MASS_MODE_CUSTOM
	third.center_of_mass = Vector2(0, 0)
	third.mass = 4.0
	root.add_child(third)
	for i in 3:
		await physics_frame
	# impulses at offset point: central vs offset
	auto.apply_impulse(Vector2(0, -60), Vector2(8, 0))
	cust.apply_impulse(Vector2(0, -60), Vector2(8, 0))  # com at (4,0): lever arm 4
	third.apply_impulse(Vector2(0, -60), Vector2(8, 0))
	for i in 10:
		await physics_frame
	print("R88 rb_com angvel[auto=%.4f cust=%.4f cust0=%.4f]" % [
		auto.angular_velocity, cust.angular_velocity, third.angular_velocity],
		" com_prop=[auto=%s cust=%s]" % [_v2(auto.center_of_mass), _v2(cust.center_of_mass)],
		" inertia=[auto=%.4f cust=%.4f m4=%.4f]" % [auto.inertia, cust.inertia, third.inertia])
	quit()

class IntegBody extends RigidBody2D:
	var seen := {}
	var manual := false
	func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
		seen["step"] = state.step
		seen["tg"] = state.total_gravity
		seen["lv"] = state.linear_velocity
		seen["coml"] = state.center_of_mass_local
		seen["calls"] = int(seen.get("calls", 0)) + 1
		if manual:
			state.linear_velocity += state.total_gravity * state.step

func _arm_rb_integrator() -> void:
	var a := IntegBody.new()  # custom integrator OFF
	var cs := CollisionShape2D.new(); cs.shape = CircleShape2D.new(); (cs.shape as CircleShape2D).radius = 8.0
	a.add_child(cs); a.position = Vector2(0, 0)
	root.add_child(a)
	var b := IntegBody.new()  # custom integrator ON, no manual -> gravity skipped?
	var cs2 := CollisionShape2D.new(); cs2.shape = CircleShape2D.new(); (cs2.shape as CircleShape2D).radius = 8.0
	b.add_child(cs2); b.position = Vector2(200, 0)
	b.custom_integrator = true
	root.add_child(b)
	var c := IntegBody.new()  # custom ON + manual gravity
	var cs3 := CollisionShape2D.new(); cs3.shape = CircleShape2D.new(); (cs3.shape as CircleShape2D).radius = 8.0
	c.add_child(cs3); c.position = Vector2(400, 0)
	c.custom_integrator = true
	c.manual = true
	root.add_child(c)
	for i in 30:
		await physics_frame
	print("R88 rb_integrator a[y=%.4f v=%s calls=%d step=%.6f tg=%s coml=%s]" % [
		a.global_position.y, _v2(a.seen.get("lv", Vector2.ZERO)), int(a.seen.get("calls", -1)),
		float(a.seen.get("step", -1)), _v2(a.seen.get("tg", Vector2.ZERO)),
		_v2(a.seen.get("coml", Vector2.ZERO))])
	print("R88 rb_integrator b[y=%.4f v=%s calls=%d]" % [
		b.global_position.y, _v2(b.seen.get("lv", Vector2.ZERO)), int(b.seen.get("calls", -1))])
	print("R88 rb_integrator c[y=%.4f v=%s calls=%d]" % [
		c.global_position.y, _v2(c.seen.get("lv", Vector2.ZERO)), int(c.seen.get("calls", -1))])
	quit()

# ---------- multiplayer ----------

func _arm_mp_offline() -> void:
	var off := OfflineMultiplayerPeer.new()
	var api := SceneMultiplayer.new()
	api.multiplayer_peer = off
	print("R88 mp_offline status=", off.get_connection_status(),
		" uid=", api.get_unique_id(),
		" mode=", off.get_transfer_mode(),
		" chan=", off.get_transfer_channel())
	root.get_multiplayer().multiplayer_peer = OfflineMultiplayerPeer.new()
	await process_frame
	print("R88 mp_offline tree_uid=", root.get_multiplayer().get_unique_id(),
		" is_server=", root.get_multiplayer().is_server(),
		" status=", root.get_multiplayer().multiplayer_peer.get_connection_status())
	quit()

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
	print("R88 mp_lb rc=[%d,%d] uid_s=%d uid_c=%d" % [rc_s, rc_c, api_s.get_unique_id(), api_c.get_unique_id()])
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
	# rpc client->server and server->client
	limb_c.rpc_id(1, "ping", 7, "c2s")
	limb_s.rpc_id(auth_uid, "ping", 9, "s2c")
	limb_c.rpc("ping", 5, "call_local_c")
	var wait := 0
	while (limb_s.rpc_log.size() < 2 or limb_c.rpc_log.size() < 2) and wait < 600:
		await process_frame; wait += 1
	print("R88 mp_lb order=", conn_order,
		" uid_after=%d" % auth_uid,
		" limb_s=", limb_s.rpc_log, " limb_c=", limb_c.rpc_log,
		" frames=%d wait=%d" % [frames, wait])
	api_s.peer_disconnected.connect(func(id): conn_order.append("s_disc%d" % id))
	api_c.server_disconnected.connect(func(): conn_order.append("c_srvdisc"))
	server.disconnect_peer(api_c.get_unique_id())
	wait = 0
	while conn_order.size() < 5 and wait < 600:
		await process_frame; wait += 1
	print("R88 mp_lb disconn=", conn_order)
	quit()

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
	var server := ENetMultiplayerPeer.new(); server.create_server(41778, 4)
	var api_s := SceneMultiplayer.new(); api_s.multiplayer_peer = server
	set_multiplayer(api_s, "/root/srv")
	var client := ENetMultiplayerPeer.new(); client.create_client("127.0.0.1", 41778)
	var api_c := SceneMultiplayer.new(); api_c.multiplayer_peer = client
	set_multiplayer(api_c, "/root/cli")
	var frames := 0
	while api_c.get_unique_id() == 0 and frames < 300:
		await process_frame; frames += 1
	# spawn on server: a named node
	var spawn := Node2D.new(); spawn.name = "spawned_one"; spawn.position = Vector2(33, 44)
	cont_s.add_child(spawn)
	var wait := 0
	while cont_c.get_child_count() == 0 and wait < 600:
		await process_frame; wait += 1
	var got := ""
	var got_pos := ""
	if cont_c.get_child_count() > 0:
		var c = cont_c.get_child(0)
		got = c.name
		got_pos = _v2(c.position) if c is Node2D else "nonnode2d"
	print("R88 mp_spawner spawned_name=%s pos=%s frames=%d wait=%d srv_children=%d" % [
		got, got_pos, frames, wait, cont_s.get_child_count()])
	# synchronizer replication
	var sync_s := MultiplayerSynchronizer.new(); sync_s.name = "sync"
	var sync_c := MultiplayerSynchronizer.new(); sync_c.name = "sync"
	var prop_s := Node2D.new(); prop_s.name = "prop"; prop_s.position = Vector2(1, 2)
	var prop_c := Node2D.new(); prop_c.name = "prop"
	cont_s.add_child(prop_s); cont_c.add_child(prop_c)
	sync_s.root_path = prop_s.get_path(); sync_c.root_path = prop_c.get_path()
	cont_s.add_child(sync_s); cont_c.add_child(sync_c)
	var rcfg := SceneReplicationConfig.new()
	rcfg.add_property(prop_s.get_path_to(prop_s) if false else NodePath(":position"))
	sync_s.replication_config = rcfg
	sync_c.replication_config = SceneReplicationConfig.new()
	(sync_c.replication_config as SceneReplicationConfig).add_property(NodePath(":position"))
	prop_s.position = Vector2(111, 222)
	wait = 0
	while prop_c.position != Vector2(111, 222) and wait < 600:
		await process_frame; wait += 1
	print("R88 mp_spawner sync_pos=%s wait=%d" % [_v2(prop_c.position), wait])
	quit()

# ---------- sprite vs physics ----------

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
	print("R88 sprite_meta readback=[re=%s rr=%s hf=%d vf=%d f=%d fc=%s fh=%s fv=%s off=%s cen=%s]" % [
		s.region_enabled, s.region_rect, s.hframes, s.vframes, s.frame, s.frame_coords,
		s.flip_h, s.flip_v, s.offset, s.centered],
		" xf=", s.global_transform,
		" signals=", fired)
	var s2 := Sprite2D.new()
	s2.texture = tex
	root.add_child(s2)
	s2.scale = Vector2(-1, 1)
	print("R88 sprite_meta scale_neg1_xf=", s2.global_transform,
		" get_rect=", s.get_rect(), " s2_rect=", s2.get_rect())
	quit()

func _arm_sprite_phys() -> void:
	# Body + sprite child; sprite metadata varied across two runs of same motion.
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
	print("R88 sprite_phys [%s]" % "|".join(results))
	quit()

# ---------- light / occluder / canvas ----------

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
	pl.range_height = 42.0
	pl.color = Color(0.5, 0.25, 0.125)
	pl.range_item_cull_mask = 4
	dl.energy = 0.75
	occ.occluder_light_mask = 2
	occ.sdf_collision = true
	cm.color = Color(0.2, 0.2, 0.4)
	print("R88 light_props pl=[en=%s sh=%s en2=%.3f ts=%.3f h=%.3f col=%s mask=%d mo=%s]" % [
		pl.enabled, pl.shadow_enabled, pl.energy, pl.texture_scale, pl.range_height,
		pl.color, pl.range_item_cull_mask, pl.shadow_item_cull_mask],
		" dl=[en=%.3f mask=%d]" % [dl.energy, dl.range_item_cull_mask],
		" occ=[closed=%s cull=%d mask=%d sdf=%s n=%d]" % [
			poly.closed, poly.cull_mode, occ.occluder_light_mask, occ.sdf_collision, poly.polygon.size()],
		" cm=[col=%s]" % cm.color)
	# occluder vs physics: body must pass through occluder geometry (no collision)
	var b := _body(0, -100)
	occ.position = Vector2(0, -40)
	root.add_child(b)
	for i in 40:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q := PhysicsRayQueryParameters2D.create(Vector2(-50, -80), Vector2(-50, 60))
	var hit := dss.intersect_ray(q)
	print("R88 light_props body_y=%.4f ray_through_occluder=%s occ_cls=%s occ_is_co=%s" % [
		b.global_position.y, hit.is_empty(), occ.get_class(), is_instance_of(occ, CollisionObject2D)])
	quit()

# ---------- audio ----------

func _arm_audio_pos() -> void:
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_8_BITS
	wav.mix_rate = 44100
	wav.stereo = false
	var data := PackedByteArray()
	for i in 44100 / 10:  # 0.1 s sine
		data.append(int(127 + 100 * sin(i * 440.0 * TAU / 44100.0)))
	wav.data = data
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	if "--fix-loop" in OS.get_cmdline_user_args():
		wav.loop_end = 4410
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
	p.play()
	var frames := 0
	var peaks: Array = []
	for i in 20:
		await process_frame
		frames += 1
		if i % 5 == 4:
			peaks.append("%.2f" % AudioServer.get_bus_peak_volume_left_db(0, 0))
	print("R88 audio_pos playing=%s pos=%.3f peaks_near=[%s]" % [p.playing, p.get_playback_position(), ",".join(peaks)])
	# move far away
	p.position = Vector2(1800, 0)
	peaks.clear()
	for i in 20:
		await process_frame
		if i % 5 == 4:
			peaks.append("%.2f" % AudioServer.get_bus_peak_volume_left_db(0, 0))
	p.stop()
	print("R88 audio_pos peaks_far=[%s] listen_pos=%s listener_current=%s" % [
		",".join(peaks), _v2(listener.global_position), listener.is_current()])
	quit()

# ---------- visibility notifier vs physics ----------

var _vis_events: Array = []
var _vis_pf := 0

func _arm_vis_not() -> void:
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
	en.enable_node_path = en.get_path_to(target) if false else NodePath("../target")
	var holder := Node2D.new(); holder.name = "h"
	holder.add_child(en); holder.add_child(target); target.name = "target"
	target.set_process(false)
	root.add_child(holder)
	print("R88 vis_not on_screen0=%s en_onscreen=%s" % [
		vn.is_on_screen(), en.is_on_screen()])
	for i in 30:
		await physics_frame
		_vis_pf += 1
	# teleport body far away, then back
	b.global_position = Vector2(500, 0)
	for i in 10:
		await physics_frame
		_vis_pf += 1
	b.global_position = Vector2(0, 0)
	for i in 10:
		await physics_frame
		_vis_pf += 1
	print("R88 vis_not events=", _vis_events,
		" on_screen_end=%s" % vn.is_on_screen(),
		" enabler_proc=%s" % target.is_processing())
	quit()

# ---------- census ----------

func _own_methods(cls: String) -> PackedStringArray:
	var out: PackedStringArray = []
	for m in ClassDB.class_get_method_list(cls, true):
		out.append(String(m.get("name", "")))
	return out

func _own_props(cls: String) -> PackedStringArray:
	var out: PackedStringArray = []
	for p in ClassDB.class_get_property_list(cls, true):
		var n := String(p.get("name", ""))
		if not n.begins_with("resource_") and not n.begins_with("script"):
			out.append(n)
	return out

func _own_signals(cls: String) -> PackedStringArray:
	var out: PackedStringArray = []
	for s in ClassDB.class_get_signal_list(cls, true):
		out.append(String(s.get("name", "")))
	return out

func _arm_census() -> void:
	print("R88 display=", DisplayServer.get_name(),
		" render=", RenderingServer.get_current_rendering_driver_name(),
		" render_method=", RenderingServer.get_current_rendering_method(),
		" audio_driver=", AudioServer.get_driver_name(),
		" audio_mix_rate=", AudioServer.get_mix_rate(),
		" audio_bus_count=", AudioServer.bus_count,
		" tps=", Engine.physics_ticks_per_second)
	var classes := [
		"MultiplayerAPI", "SceneMultiplayer", "MultiplayerPeer", "ENetMultiplayerPeer",
		"WebSocketMultiplayerPeer", "WebRTCMultiplayerPeer", "OfflineMultiplayerPeer",
		"MultiplayerSpawner", "MultiplayerSynchronizer", "MultiplayerPeerExtension",
		"Sprite2D", "AnimatedSprite2D", "PointLight2D", "DirectionalLight2D",
		"LightOccluder2D", "OccluderPolygon2D", "CanvasModulate",
		"AudioStreamPlayer2D", "AudioListener2D", "AudioStreamPlaybackPolyphonic",
		"VisibleOnScreenNotifier2D", "VisibleOnScreenEnabler2D",
		"Geometry2D", "ConvexPolygonShape2D", "ConcavePolygonShape2D",
		"RigidBody2D", "PhysicsDirectBodyState2D", "Line2D", "Polygon2D",
		"Bone2D", "Path2D", "TouchScreenCamera2D",
	]
	for c in classes:
		print("R88C class=", c, " exists=", ClassDB.class_exists(c),
			" can_instance=", ClassDB.can_instantiate(c) if ClassDB.class_exists(c) else false)
	for c in ["ENetMultiplayerPeer", "OfflineMultiplayerPeer", "MultiplayerSpawner",
			"MultiplayerSynchronizer", "SceneMultiplayer"]:
		if ClassDB.class_exists(c):
			print("R88C methods_", c, "=", ",".join(_own_methods(c)))
			print("R88C props_", c, "=", ",".join(_own_props(c)))
	if ClassDB.class_exists("Geometry2D"):
		print("R88C methods_Geometry2D=", ",".join(_own_methods("Geometry2D")))
	for c in ["VisibleOnScreenNotifier2D", "VisibleOnScreenEnabler2D", "PointLight2D",
			"LightOccluder2D", "OccluderPolygon2D", "CanvasModulate", "AudioStreamPlayer2D",
			"AudioListener2D", "Sprite2D", "RigidBody2D", "PhysicsDirectBodyState2D"]:
		if ClassDB.class_exists(c):
			print("R88C props_", c, "=", ",".join(_own_props(c)))
			print("R88C signals_", c, "=", ",".join(_own_signals(c)))
	print("R88C audio_has_peak=", AudioServer.has_method("get_bus_peak_volume_left_db"),
		" sample_exists=", ClassDB.class_exists("AudioStreamWAV"))
	print("R88C tree_multiplayer=", root.get_multiplayer().get_class(),
		" has_set_multiplayer=", has_method("set_multiplayer"),
		" unique_id=", root.get_multiplayer().get_unique_id())
	print("R88C rendering_devices=", RenderingServer.get_video_adapter_name() if RenderingServer.has_method("get_video_adapter_name") else "?")
	quit()
