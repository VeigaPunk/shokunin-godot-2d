extends SceneTree
# r88 BOUNDARY seat — multiplayer loopback edges: uid pinning, connect/disconnect ordering,
# repeated cycles, generator range, offline peer.
# Launch: godot --headless --path proj --script res://b88_mp.gd -- --arm=<arm> [--port=<base>]
# Dispatch via OS.get_cmdline_user_args() (battery convention; never get_cmdline_args).

var arm := ""
var port_base := 41931

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--port="):
			port_base = int(a.substr(7))
	if arm.is_empty():
		print("R88B ARM_MISSING")
		quit(1)
		return
	print("R88B arm=%s port_base=%d" % [arm, port_base])
	_run.call_deferred()

func _run() -> void:
	match arm:
		"mp_lb": _arm_mp_lb()
		"mp_names": _arm_mp_names()
		"mp_cycles": _arm_mp_cycles()
		"mp_genid": _arm_mp_genid()
		"mp_offline": _arm_mp_offline()
		_:
			print("R88B unknown_arm=%s" % arm)
			quit(2)

class MpLimb extends Node:
	var rpc_log: Array = []
	@rpc("any_peer", "call_local", "reliable")
	func ping(n: int, tag: String) -> void:
		rpc_log.append("ping%d:%s" % [n, tag])
	@rpc("any_peer", "call_local", "unreliable")
	func uping(n: int) -> void:
		rpc_log.append("u%d" % n)

# One ENet loopback cycle. Mirrors r88_probe.gd _arm_mp_loopback, with srv/cli branch names
# and add order parameterized, plus extra uid readbacks.
func _pair_round_trip(srv_name: String, cli_name: String, port: int, add_cli_first: bool) -> Dictionary:
	var srv_branch := Node.new()
	srv_branch.name = srv_name
	var cli_branch := Node.new()
	cli_branch.name = cli_name
	if add_cli_first:
		root.add_child(cli_branch)
		root.add_child(srv_branch)
	else:
		root.add_child(srv_branch)
		root.add_child(cli_branch)
	var limb_s := MpLimb.new()
	limb_s.name = "limb"
	srv_branch.add_child(limb_s)
	var limb_c := MpLimb.new()
	limb_c.name = "limb"
	cli_branch.add_child(limb_c)
	var server := ENetMultiplayerPeer.new()
	var rc_s := server.create_server(port, 4)
	var api_s := SceneMultiplayer.new()
	api_s.multiplayer_peer = server
	set_multiplayer(api_s, srv_branch.get_path())
	var client := ENetMultiplayerPeer.new()
	var rc_c := client.create_client("127.0.0.1", port)
	var api_c := SceneMultiplayer.new()
	api_c.multiplayer_peer = client
	set_multiplayer(api_c, cli_branch.get_path())
	var out := {
		"rc_s": rc_s,
		"rc_c": rc_c,
		"uid_s_pre": api_s.get_unique_id(),
		"uid_c_pre": api_c.get_unique_id(),
		"is_server_s": api_s.is_server(),
		"is_server_c": api_c.is_server(),
		"enet_uid_s": server.get_unique_id(),
		"enet_uid_c": client.get_unique_id(),
	}
	var conn_order: Array = []
	api_s.peer_connected.connect(func(id): conn_order.append("s_conn%d" % id))
	api_c.peer_connected.connect(func(id): conn_order.append("c_conn%d" % id))
	api_c.connected_to_server.connect(func(): conn_order.append("c_on_srv"))
	api_s.connected_to_server.connect(func(): conn_order.append("s_on_srv"))
	var frames := 0
	while api_c.get_unique_id() == 0 and frames < 300:
		await process_frame
		frames += 1
	while conn_order.size() < 3 and frames < 600:
		await process_frame
		frames += 1
	var auth_uid := api_c.get_unique_id()
	limb_c.rpc_id(1, "ping", 7, "c2s")
	limb_s.rpc_id(auth_uid, "ping", 9, "s2c")
	limb_c.rpc("ping", 5, "call_local_c")
	var wait := 0
	while (limb_s.rpc_log.size() < 2 or limb_c.rpc_log.size() < 2) and wait < 600:
		await process_frame
		wait += 1
	out["order"] = conn_order.duplicate()
	out["uid_after"] = auth_uid
	out["uid_s_after"] = api_s.get_unique_id()
	out["limb_s"] = limb_s.rpc_log.duplicate()
	out["limb_c"] = limb_c.rpc_log.duplicate()
	out["frames"] = frames
	out["wait"] = wait
	api_s.peer_disconnected.connect(func(id): conn_order.append("s_disc%d" % id))
	api_c.server_disconnected.connect(func(): conn_order.append("c_srvdisc"))
	server.disconnect_peer(auth_uid)
	var disc_wait := 0
	while conn_order.size() < 5 and disc_wait < 600:
		await process_frame
		disc_wait += 1
	out["disconn"] = conn_order.duplicate()
	out["disc_wait"] = disc_wait
	await process_frame
	return out

func _arm_mp_lb() -> void:
	var o := await _pair_round_trip("srv", "cli", port_base, false)
	print("R88B mp_lb rc=[%d,%d] uid_s_pre=%d uid_c_pre=%d is_server_s=%s is_server_c=%s enet_uid_s=%d enet_uid_c=%d" % [
		o["rc_s"], o["rc_c"], o["uid_s_pre"], o["uid_c_pre"], o["is_server_s"],
		o["is_server_c"], o["enet_uid_s"], o["enet_uid_c"]])
	print("R88B mp_lb order=%s uid_after=%d uid_s_after=%d limb_s=%s limb_c=%s frames=%d wait=%d" % [
		o["order"], o["uid_after"], o["uid_s_after"], o["limb_s"], o["limb_c"],
		o["frames"], o["wait"]])
	print("R88B mp_lb disconn=%s disc_wait=%d" % [o["disconn"], o["disc_wait"]])
	quit()

# Name/order sensitivity of the connect+disconnect ordering pin.
func _arm_mp_names() -> void:
	var cases := [
		["scout_names", "srv", "cli", false],
		["swapped_names", "cli", "srv", false],
		["server_sorts_last", "zz_srv", "aa_cli", false],
		["reverse_add_order", "srv", "cli", true],
	]
	var i := 0
	for c in cases:
		var o := await _pair_round_trip(c[1], c[2], port_base + 1 + i, c[3])
		print("R88B mp_names case=%s srv=%s cli=%s add_cli_first=%s rc=[%d,%d] uid_s=%d uid_c=%d order=%s disconn=%s frames=%d wait=%d disc_wait=%d" % [
			c[0], c[1], c[2], c[3], o["rc_s"], o["rc_c"], o["uid_s_pre"], o["uid_after"],
			o["order"], o["disconn"], o["frames"], o["wait"], o["disc_wait"]])
		i += 1
	quit()

# 10 sequential loopback cycles in one process — reorder hunt without process-start effects.
func _arm_mp_cycles() -> void:
	for i in 10:
		var o := await _pair_round_trip("srv%d" % i, "cli%d" % i, port_base + 11 + i, false)
		print("R88B mp_cycles cycle=%d rc=[%d,%d] uid_s=%d uid_c=%d order=%s disconn=%s frames=%d wait=%d disc_wait=%d" % [
			i, o["rc_s"], o["rc_c"], o["uid_s_pre"], o["uid_after"], o["order"],
			o["disconn"], o["frames"], o["wait"], o["disc_wait"]])
	quit()

# Sample MultiplayerPeer.generate_unique_id() — the source of uid_c — to measure the
# digit-count tail that a \d{6,} normalizer would miss.
func _arm_mp_genid() -> void:
	var has := ClassDB.class_has_method("MultiplayerPeer", "generate_unique_id")
	var methods: Array = []
	for m in ClassDB.class_get_method_list("MultiplayerPeer", true):
		methods.append(String(m.get("name", "")))
	print("R88B mp_genid has_generate_unique_id=%s own_methods=%s" % [has, methods])
	if not has:
		quit()
		return
	var p := ENetMultiplayerPeer.new()
	var sample: Array = []
	for i in 3:
		sample.append(p.call("generate_unique_id"))
	print("R88B mp_genid sample=%s" % [sample])
	var n := 200000
	var mn := 1 << 30
	var mx := 0
	var below6 := 0
	var below7 := 0
	var eq0 := 0
	var eq1 := 0
	var hist := {}
	for i in n:
		var v: int = p.call("generate_unique_id")
		if v < mn:
			mn = v
		if v > mx:
			mx = v
		if v < 100000:
			below6 += 1
		if v < 1000000:
			below7 += 1
		if v == 0:
			eq0 += 1
		if v == 1:
			eq1 += 1
		var d: int = str(v).length()
		hist[d] = int(hist.get(d, 0)) + 1
	print("R88B mp_genid n=%d min=%d max=%d below_1e5=%d below_1e6=%d eq0=%d eq1=%d digits=%s" % [
		n, mn, mx, below6, below7, eq0, eq1, hist])
	quit()

func _arm_mp_offline() -> void:
	var off := OfflineMultiplayerPeer.new()
	var api := SceneMultiplayer.new()
	api.multiplayer_peer = off
	print("R88B mp_offline status=%d uid=%d mode=%d chan=%d is_server=%s" % [
		off.get_connection_status(), api.get_unique_id(), off.get_transfer_mode(),
		off.get_transfer_channel(), api.is_server()])
	root.get_multiplayer().multiplayer_peer = OfflineMultiplayerPeer.new()
	await process_frame
	print("R88B mp_offline tree_uid=%d is_server=%s status=%d" % [
		root.get_multiplayer().get_unique_id(), root.get_multiplayer().is_server(),
		root.get_multiplayer().multiplayer_peer.get_connection_status()])
	quit()
