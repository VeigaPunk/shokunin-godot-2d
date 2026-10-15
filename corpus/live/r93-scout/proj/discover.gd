extends SceneTree
# r93-scout discovery micro-probe — AnimationPlayer + Tween authorability lattice.
# Launch: godot --headless --path proj --script res://discover.gd -- --arm=<arm>
# Prints `DISC <arm> ...` lines only; not a battery fixture.

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _names(objs: Array) -> String:
	var out: Array[String] = []
	for o in objs:
		var nm := String(o["name"])
		out.append(nm)
	return "[" + ",".join(out) + "]"

func _consts(cls: String) -> String:
	var out: Array[String] = []
	for c in ClassDB.class_get_integer_constant_list(cls, true):
		out.append("%s=%d" % [c, ClassDB.class_get_integer_constant(cls, c)])
	return "[" + ",".join(out) + "]"

func _method_names(obj: Object, needle: String) -> String:
	var out: Array[String] = []
	for m in obj.get_method_list():
		var nm := String(m["name"])
		if nm.contains(needle):
			out.append(nm)
	return "[" + ",".join(out) + "]"

func _initialize() -> void:
	var arm := _arg("arm", "census")
	match arm:
		"census": _arm_census()
		"tweenval": _arm_tweenval()
		"expo": _arm_expo()
		"tweenstep": await _arm_tweenstep()
		"animadvance": await _arm_animadvance()
		"animmethod": await _arm_animmethod()
		"animsample": _arm_animsample()
		"animblend": await _arm_animblend()
		"animproc": await _arm_animproc()
		"clock": await _arm_clock()
		_: print("DISC unknown arm=", arm)
	quit(0)

func _arm_census() -> void:
	var ap := AnimationPlayer.new()
	var an := Animation.new()
	var tw := Tween.new()
	print("DISC census ap_is_mixer=", ap is AnimationMixer, " ap_is_node=", ap is Node,
		" tw_is_ref=", tw is RefCounted, " an_is_res=", an is Resource)
	print("DISC census Animation_consts=", _consts("Animation"))
	print("DISC census AnimationMixer_consts=", _consts("AnimationMixer"))
	print("DISC census AnimationPlayer_consts=", _consts("AnimationPlayer"))
	print("DISC census Tween_consts=", _consts("Tween"))
	print("DISC census ap_defaults proc=", ap.playback_process_mode, " cbm=", ap.callback_mode_method,
		" cbp=", ap.callback_mode_process, " cbd=", ap.callback_mode_discrete,
		" root=", ap.root_node, " active=", ap.active, " speed=", ap.speed_scale)
	print("DISC census an_defaults len=", an.length, " loop=", an.loop_mode, " step=", an.step, " tracks=", an.get_track_count())
	print("DISC census ap_signals=", _names(ap.get_signal_list()))
	print("DISC census tw_signals=", _names(tw.get_signal_list()))
	print("DISC census ap_m_cache=", _method_names(ap, "cache"))
	print("DISC census ap_m_blend=", _method_names(ap, "blend"))
	print("DISC census ap_m_count=", ap.get_method_list().size())
	print("DISC census ap_m_advance=", _method_names(ap, "advance"))
	print("DISC census ap_m_process=", _method_names(ap, "process"))
	print("DISC census ap_m_capture=", _method_names(ap, "capture"))
	print("DISC census am_m_cache=", _method_names(ap, "cache"))
	print("DISC census an_m_count=", an.get_method_list().size())
	print("DISC census an_has_track_interp=", an.has_method("track_interpolate"))
	print("DISC census an_m_interp=", _method_names(an, "interpolate"))
	print("DISC census tw_m_count=", tw.get_method_list().size())
	print("DISC census tw_m_step=", _method_names(tw, "step"))
	print("DISC census tw_m_loop=", _method_names(tw, "loop"))
	print("DISC census tw_m_parallel=", _method_names(tw, "parallel"))

func _arm_tweenval() -> void:
	var trans: Array = [Tween.TRANS_LINEAR, Tween.TRANS_SINE, Tween.TRANS_QUINT, Tween.TRANS_QUART,
		Tween.TRANS_QUAD, Tween.TRANS_EXPO, Tween.TRANS_ELASTIC, Tween.TRANS_CUBIC, Tween.TRANS_CIRC,
		Tween.TRANS_BOUNCE, Tween.TRANS_BACK, Tween.TRANS_SPRING]
	var tn: Array = ["lin", "sin", "qui", "qua", "qad", "expo", "ela", "cub", "cir", "bou", "bac", "spr"]
	var ease: Array = [Tween.EASE_IN, Tween.EASE_OUT, Tween.EASE_IN_OUT, Tween.EASE_OUT_IN]
	var en: Array = ["in", "out", "io", "oi"]
	for i in range(trans.size()):
		var row: Array[String] = []
		for j in range(ease.size()):
			var vals: Array[String] = []
			for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
				vals.append(str(Tween.interpolate_value(0.0, 10.0, t, 1.0, trans[i], ease[j])))
			row.append("%s=%s" % [en[j], ",".join(vals)])
		print("DISC tweenval %s %s" % [tn[i], " ".join(row)])
	print("DISC tweenval r91_exact=", str(Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_OUT)))
	print("DISC tweenval clamp_neg=", str(Tween.interpolate_value(0.0, 10.0, -0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),
		" clamp_over=", str(Tween.interpolate_value(0.0, 10.0, 1.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)))
	print("DISC tweenval vec_delta=", str(Tween.interpolate_value(Vector2(1, 2), Vector2(4, 8), 0.25, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),
		" color_delta=", str(Tween.interpolate_value(Color(0, 0, 0, 1), Color(1, 0.5, 0, 0), 0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)))
	print("DISC tweenval int_delta=", str(Tween.interpolate_value(0, 10, 0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)))

func _arm_expo() -> void:
	var tvals: Array = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
	for e in [Tween.EASE_IN, Tween.EASE_OUT, Tween.EASE_IN_OUT, Tween.EASE_OUT_IN]:
		var parts: Array[String] = []
		for t in tvals:
			parts.append("%s:%s" % [t, str(Tween.interpolate_value(0.0, 1.0, t, 1.0, Tween.TRANS_EXPO, e))])
		print("DISC expo ease=", e, " ", " ".join(parts))
	# candidate closed forms at t=0.5, delta=1
	var t := 0.5
	print("DISC expo cand 1-2^-10t=", 1.0 - pow(2.0, -10.0 * t),
		" 1-2^10(t-1)=", 1.0 - pow(2.0, 10.0 * (t - 1.0)),
		" 2^-10t=", pow(2.0, -10.0 * t),
		" 2^10(t-1)=", pow(2.0, 10.0 * (t - 1.0)))

func _arm_tweenstep() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var tw := create_tween()
	tw.tween_property(target, "position:x", 10.0, 1.0)
	print("DISC tweenstep created running=", tw.is_running(), " x=", target.position.x, " elapsed=", tw.get_total_elapsed_time())
	tw.custom_step(0.5)
	print("DISC tweenstep custom_half x=", target.position.x, " running=", tw.is_running(), " elapsed=", tw.get_total_elapsed_time())
	var fired: Array = []
	tw.finished.connect(func(): fired.append("fin"))
	tw.custom_step(0.5)
	print("DISC tweenstep custom_full x=", target.position.x, " running=", tw.is_running(), " elapsed=", tw.get_total_elapsed_time(), " fired_now=", fired.size())
	await process_frame
	print("DISC tweenstep after_frame x=", target.position.x, " running=", tw.is_running(), " fired=", fired.size())
	# paused tween + custom_step
	var t2 := create_tween()
	t2.tween_property(target, "position:y", 20.0, 1.0)
	t2.pause()
	t2.custom_step(0.5)
	print("DISC tweenstep paused_custom y=", target.position.y, " valid=", t2.is_valid(), " running=", t2.is_running())
	await process_frame
	print("DISC tweenstep paused_after_frame y=", target.position.y)
	# unprocessed tween: does awaiting a frame advance it at all?
	var t3 := create_tween()
	t3.tween_property(target, "position:x", 100.0, 1.0)
	await process_frame
	print("DISC tweenstep await1_x=", target.position.x, " running=", t3.is_running())

func _build_player(target: Node2D) -> AnimationPlayer:
	var player := AnimationPlayer.new()
	player.name = "AP"
	target.add_child(player)
	var anim := Animation.new()
	anim.length = 1.0
	var tr := anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(tr, NodePath(".:position:x"))
	anim.track_insert_key(tr, 0.0, 0.0)
	anim.track_insert_key(tr, 1.0, 100.0)
	var lib := AnimationLibrary.new()
	lib.add_animation("move", anim)
	player.add_animation_library("", lib)
	return player

func _arm_animadvance() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _build_player(target)
	await process_frame
	var fired: Array = []
	player.animation_finished.connect(func(n): fired.append(n))
	print("DISC animadvance default_proc=", player.playback_process_mode)
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.play("move")
	print("DISC animadvance after_play playing=", player.is_playing(), " pos=", player.current_animation_position,
		" len=", player.current_animation_length, " x=", target.position.x, " speed=", player.speed_scale)
	player.advance(0.25)
	print("DISC animadvance adv_025 pos=", player.current_animation_position, " x=", target.position.x)
	player.seek(0.75, true)
	print("DISC animadvance seek_075_up pos=", player.current_animation_position, " x=", target.position.x)
	player.seek(0.5, false)
	print("DISC animadvance seek_05_noup pos=", player.current_animation_position, " x=", target.position.x)
	player.advance(1.0)
	print("DISC animadvance adv_cross playing=", player.is_playing(), " pos=", player.current_animation_position,
		" x=", target.position.x, " fired_during=", fired.size())
	await process_frame
	print("DISC animadvance after_frame fired=", fired.size(), " x=", target.position.x)
	# stop resets?
	player.stop()
	print("DISC animadvance after_stop playing=", player.is_playing(), " x=", target.position.x)
	# paused player + advance
	player.play("move")
	player.pause()
	player.advance(0.5)
	print("DISC animadvance paused_adv playing=", player.is_playing(), " x=", target.position.x)
	# manual mode: do awaited frames advance anything?
	player.play("move")
	await process_frame
	await process_frame
	print("DISC animadvance manual_frames pos=", player.current_animation_position, " x=", target.position.x)

class MethodTarget extends Node2D:
	var calls: Array = []
	func notify(v: int) -> void:
		calls.append(v)

func _arm_animmethod() -> void:
	var target := MethodTarget.new()
	target.name = "MT"
	root.add_child(target)
	var player := AnimationPlayer.new()
	player.name = "AP"
	target.add_child(player)
	var anim := Animation.new()
	anim.length = 1.0
	var tr := anim.add_track(Animation.TYPE_METHOD)
	anim.track_set_path(tr, NodePath("."))
	anim.track_insert_key(tr, 0.2, {"method": "notify", "args": [7]})
	anim.track_insert_key(tr, 0.5, {"method": "notify", "args": [8]})
	var lib := AnimationLibrary.new()
	lib.add_animation("m", anim)
	player.add_animation_library("", lib)
	await process_frame
	print("DISC animmethod default_cbm=", player.callback_mode_method)
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.play("m")
	player.advance(1.0)
	print("DISC animmethod deferred_after_advance calls=", target.calls)
	await process_frame
	print("DISC animmethod deferred_after_frame calls=", target.calls)
	target.calls.clear()
	player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
	player.stop()
	player.play("m")
	player.advance(1.0)
	print("DISC animmethod immediate_after_advance calls=", target.calls)
	await process_frame
	print("DISC animmethod immediate_after_frame calls=", target.calls)
	# disabled track
	target.calls.clear()
	anim.track_set_enabled(tr, false)
	player.stop()
	player.play("m")
	player.advance(1.0)
	print("DISC animmethod disabled_track calls=", target.calls)

func _arm_animsample() -> void:
	var anim := Animation.new()
	anim.length = 1.0
	var tr := anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(tr, NodePath(".:position:x"))
	anim.track_insert_key(tr, 0.0, 0.0)
	anim.track_insert_key(tr, 1.0, 10.0)
	print("DISC animsample has_value_track_interp=", anim.has_method("value_track_interpolate"))
	for it in [Animation.INTERPOLATION_NEAREST, Animation.INTERPOLATION_LINEAR, Animation.INTERPOLATION_CUBIC]:
		anim.track_set_interpolation_type(tr, it)
		print("DISC animsample interp=", it, " t05=", anim.value_track_interpolate(tr, 0.5),
			" t09=", anim.value_track_interpolate(tr, 0.9), " t10=", anim.value_track_interpolate(tr, 1.0))
	anim.track_set_interpolation_type(tr, Animation.INTERPOLATION_LINEAR)
	print("DISC animsample keys=", anim.track_get_key_count(tr), " k0=", anim.track_get_key_value(tr, 0),
		" t0=", anim.track_get_key_time(tr, 0), " k1=", anim.track_get_key_value(tr, 1),
		" interp_type_default=", anim.track_get_interpolation_type(tr))

func _arm_animblend() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := AnimationPlayer.new()
	player.name = "AP"
	target.add_child(player)
	var a := Animation.new()
	a.length = 1.0
	var ta := a.add_track(Animation.TYPE_VALUE)
	a.track_set_path(ta, NodePath(".:position:x"))
	a.track_insert_key(ta, 0.0, 0.0)
	a.track_insert_key(ta, 1.0, 100.0)
	var b := Animation.new()
	b.length = 1.0
	var tb := b.add_track(Animation.TYPE_VALUE)
	b.track_set_path(tb, NodePath(".:position:x"))
	b.track_insert_key(tb, 0.0, 500.0)
	b.track_insert_key(tb, 1.0, 500.0)
	var lib := AnimationLibrary.new()
	lib.add_animation("a", a)
	lib.add_animation("b", b)
	player.add_animation_library("", lib)
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.play("a")
	player.advance(1.0)
	print("DISC animblend a_end x=", target.position.x, " playing=", player.is_playing(), " pos=", player.current_animation_position)
	player.set_blend_time("a", "b", 1.0)
	print("DISC animblend blend_times=", player.get_blend_time("a", "b"), " default=", player.playback_default_blend_time)
	player.play("b")
	for step in [0.125, 0.25, 0.5, 1.0]:
		player.advance(step)
		print("DISC animblend blend_adv_", step, " x=", target.position.x, " pos=", player.current_animation_position)
	# hard switch control
	player.stop()
	player.play("a")
	player.advance(1.0)
	player.play("b", 0.0)
	print("DISC animblend hard_switch_immediate x=", target.position.x, " pos=", player.current_animation_position)
	player.advance(0.25)
	print("DISC animblend hard_switch_adv x=", target.position.x, " pos=", player.current_animation_position)
	# stop semantics with a non-zero starting property
	player.stop()
	target.position.x = 7.0
	player.play("a")
	player.advance(0.5)
	print("DISC animblend before_stop x=", target.position.x)
	player.stop()
	print("DISC animblend after_stop x=", target.position.x)
	# capture api presence
	print("DISC animblend capture_methods=", _method_names(player, "capture"))
	player.set_auto_capture(true)
	player.play("a")
	player.advance(0.5)
	print("DISC animblend autocapture x=", target.position.x, " auto=", player.is_auto_capture())
	player.play_with_capture("b", 1.0)
	player.advance(0.5)
	print("DISC animblend play_with_capture_mid x=", target.position.x, " pos=", player.current_animation_position)
	player.advance(0.5)
	print("DISC animblend play_with_capture_end x=", target.position.x, " pos=", player.current_animation_position)
	print("DISC animblend default_blend_after=", player.playback_default_blend_time)

func _arm_animproc() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _build_player(target)
	await process_frame
	player.play("move")
	var proc0 := target.position.x
	for i in range(3):
		await process_frame
	var proc1 := target.position.x
	for i in range(3):
		await physics_frame
	var proc2 := target.position.x
	print("DISC animproc idle x0=", proc0, " after3proc=", proc1, " after3phys=", proc2,
		" pos=", player.current_animation_position, " playing=", player.is_playing())
	player.stop()
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_PHYSICS
	player.play("move")
	var ph0 := target.position.x
	for i in range(3):
		await process_frame
	var ph1 := target.position.x
	for i in range(3):
		await physics_frame
	var ph2 := target.position.x
	print("DISC animproc phys x0=", ph0, " after3proc=", ph1, " after3phys=", ph2,
		" pos=", player.current_animation_position, " playing=", player.is_playing())
	# finished signal timing in idle mode, short animation
	var quick := Animation.new()
	quick.length = 0.1
	var tq := quick.add_track(Animation.TYPE_VALUE)
	quick.track_set_path(tq, NodePath(".:position:y"))
	quick.track_insert_key(tq, 0.0, 0.0)
	quick.track_insert_key(tq, 0.1, 5.0)
	var lib := AnimationLibrary.new()
	lib.add_animation("q", quick)
	player.add_animation_library("", lib)
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE
	var fin_frame := -1
	var frames := 0
	player.animation_finished.connect(func(n): fin_frame = frames)
	player.play("q")
	while frames < 20:
		await process_frame
		frames += 1
	print("DISC animproc quick frames=", frames, " fin_frame=", fin_frame, " y=", target.position.y,
		" playing=", player.is_playing())

func _arm_clock() -> void:
	var t0 := Time.get_ticks_usec()
	var pn := 0
	for i in range(30):
		await process_frame
		pn += 1
	var t1 := Time.get_ticks_usec()
	var qn := 0
	for i in range(30):
		await physics_frame
		qn += 1
	var t2 := Time.get_ticks_usec()
	print("DISC clock proc30_us=", t1 - t0, " phys30_us=", t2 - t1,
		" proc_delta_us=", (t1 - t0) / float(pn), " phys_delta_us=", (t2 - t1) / float(qn),
		" engine_max_fps=", Engine.max_fps, " time_scale=", Engine.time_scale)
