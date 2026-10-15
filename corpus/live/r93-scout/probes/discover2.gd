extends SceneTree
# r93-scout discovery #2 — loose ends for the frozen probe.

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _ps(arr: Array) -> String:
	var parts: Array[String] = []
	for v in arr:
		parts.append(str(v))
	return "[" + ",".join(parts) + "]"

func _value_anim(keys: Array, length: float = 1.0, loop_mode: int = Animation.LOOP_NONE) -> Animation:
	var anim := Animation.new()
	anim.length = length
	anim.loop_mode = loop_mode
	var tr := anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(tr, NodePath(".:position:x"))
	for k in keys:
		anim.track_insert_key(tr, k[0], k[1])
	return anim

func _const_anim(value: float, length: float = 1.0) -> Animation:
	var anim := Animation.new()
	anim.length = length
	var tr := anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(tr, NodePath(".:position:x"))
	anim.track_insert_key(tr, 0.0, value)
	anim.track_insert_key(tr, length, value)
	return anim

func _initialize() -> void:
	var arm := _arg("arm", "restart")
	match arm:
		"restart": await _arm_restart()
		"stopstep": _arm_stopstep()
		"nodefree": await _arm_nodefree()
		"blendsteps": await _arm_blendsteps()
		"delay": _arm_delay()
		"pingpong": await _arm_pingpong()
		"inf": _arm_inf()
		_: print("DISC2 unknown arm=", arm)
	quit(0)

func _mk_player(target: Node2D, anims: Dictionary) -> AnimationPlayer:
	var lib := AnimationLibrary.new()
	for name in anims:
		lib.add_animation(name, anims[name])
	var player := AnimationPlayer.new()
	player.name = "AP"
	target.add_child(player)
	player.add_animation_library("", lib)
	return player

func _arm_restart() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _mk_player(target, {
		"a": _value_anim([[0.0, 0.0], [1.0, 100.0]]),
		"b": _const_anim(500.0),
	})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.play("a")
	player.advance(0.5)
	var before := [player.current_animation_position, target.position.x]
	player.play("a")
	var replay_same := [player.current_animation_position, target.position.x]
	player.play("b")
	var play_other := [player.current_animation_position, target.position.x, player.assigned_animation]
	player.play("a")
	var back := [player.current_animation_position, target.position.x]
	player.seek(2.0, true)
	var seek_over := [player.current_animation_position, target.position.x, player.is_playing()]
	player.play("a", -1, 1.0, true)
	var from_end := [player.current_animation_position, target.position.x]
	print("DISC2 restart before=", _ps(before), " replay_same=", _ps(replay_same), " play_other=", _ps(play_other),
		" back=", _ps(back), " seek_over=", _ps(seek_over), " from_end=", _ps(from_end),
		" list=", _ps(player.get_animation_list()), " has=", player.has_animation("a"), " assigned=", player.assigned_animation)

func _arm_stopstep() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var tw := create_tween()
	tw.tween_property(target, "position:x", 10.0, 1.0)
	tw.pause()
	tw.custom_step(0.5)
	var mid := [target.position.x, tw.get_total_elapsed_time(), tw.is_running(), tw.is_valid()]
	tw.stop()
	var after_stop := [target.position.x, tw.get_total_elapsed_time(), tw.is_running(), tw.is_valid()]
	tw.custom_step(0.25)
	var after_stop_step := [target.position.x, tw.get_total_elapsed_time(), tw.is_running(), tw.is_valid()]
	print("DISC2 stopstep mid=", _ps(mid), " after_stop=", _ps(after_stop), " after_stop_step=", _ps(after_stop_step))

func _arm_nodefree() -> void:
	var n := Node2D.new()
	n.name = "N"
	root.add_child(n)
	var tn := n.create_tween()
	tn.tween_property(n, "position:x", 50.0, 1.0)
	await process_frame
	tn.custom_step(0.25)
	var stepped := [n.position.x, tn.is_valid(), tn.is_running()]
	n.free()
	var freed := [tn.is_valid(), tn.is_running()]
	tn.custom_step(0.25)
	var after := [tn.is_valid(), tn.is_running()]
	await process_frame
	var after_frame := [tn.is_valid(), tn.is_running()]
	print("DISC2 nodefree stepped=", _ps(stepped), " freed=", _ps(freed), " after_step=", _ps(after), " after_frame=", _ps(after_frame))

func _blend_run(player: AnimationPlayer, target: Node2D, steps: int, dt: float) -> Array:
	var out: Array = []
	player.play("a")
	player.advance(1.0)
	player.play("b")
	for i in range(steps):
		player.advance(dt)
		out.append(target.position.x)
	return out

func _arm_blendsteps() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _mk_player(target, {
		"a": _value_anim([[0.0, 0.0], [1.0, 100.0]]),
		"b": _const_anim(500.0),
	})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.set_blend_time("a", "b", 1.0)
	var s005 := _blend_run(player, target, 20, 0.05)
	var s010 := _blend_run(player, target, 10, 0.1)
	var s020 := _blend_run(player, target, 5, 0.2)
	var s025 := _blend_run(player, target, 4, 0.25)
	print("DISC2 blendsteps dt005=", _ps(s005))
	print("DISC2 blendsteps dt010=", _ps(s010))
	print("DISC2 blendsteps dt020=", _ps(s020))
	print("DISC2 blendsteps dt025=", _ps(s025))

func _arm_delay() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var tw := create_tween()
	tw.tween_property(target, "position:x", 10.0, 1.0).set_delay(0.5)
	tw.pause()
	tw.custom_step(0.25)
	var d1 := [target.position.x, tw.get_total_elapsed_time()]
	tw.custom_step(0.25)
	var d2 := [target.position.x, tw.get_total_elapsed_time()]
	tw.custom_step(0.5)
	var d3 := [target.position.x, tw.get_total_elapsed_time()]
	var t2 := create_tween()
	target.position.x = 7.0
	t2.tween_property(target, "position:x", 10.0, 1.0).from(0.0)
	t2.pause()
	t2.custom_step(0.5)
	var from_mid := [target.position.x, t2.get_total_elapsed_time()]
	var t3 := create_tween()
	target.position.x = 7.0
	t3.tween_property(target, "position:x", 10.0, 1.0).as_relative()
	t3.pause()
	t3.custom_step(0.5)
	var rel_mid := [target.position.x, t3.get_total_elapsed_time()]
	print("DISC2 delay delay=[", _ps(d1), _ps(d2), _ps(d3), "] from=", _ps(from_mid), " relative=", _ps(rel_mid))

func _arm_pingpong() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _mk_player(target, {
		"pp": _value_anim([[0.0, 0.0], [0.5, 50.0]], 0.5, Animation.LOOP_PINGPONG),
	})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.play("pp")
	var fin: Array = []
	player.animation_finished.connect(func(n): fin.append(n))
	player.advance(0.75)
	var p075 := [target.position.x, player.current_animation_position, fin.size(), player.is_playing()]
	player.advance(0.5)
	var p125 := [target.position.x, player.current_animation_position, fin.size()]
	player.advance(0.5)
	var p175 := [target.position.x, player.current_animation_position, fin.size()]
	print("DISC2 pingpong p075=", _ps(p075), " p125=", _ps(p125), " p175=", _ps(p175))

func _arm_inf() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var tw := create_tween()
	tw.set_loops(0)
	tw.tween_property(target, "position:x", 10.0, 0.5)
	tw.pause()
	tw.custom_step(0.5)
	var l1 := [target.position.x, tw.get_loops_left(), tw.is_running()]
	tw.custom_step(0.5)
	var l2 := [target.position.x, tw.get_loops_left(), tw.is_running()]
	tw.kill()
	print("DISC2 inf loop0=[", _ps(l1), _ps(l2), "]")
