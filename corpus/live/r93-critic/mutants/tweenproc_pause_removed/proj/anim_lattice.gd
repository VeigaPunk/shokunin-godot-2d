extends SceneTree
# r93-scout frozen primary probe — AnimationPlayer + Tween authorability lattice.
# Launch: godot --headless --path <proj> --script res://anim_lattice.gd -- --arm=<arm>
# Every arm prints exactly one `PASS anim_lattice <arm> ...` line (battery signature).
#
# Discovery receipts (runs/disc-*): the authoring recipes this probe pins —
#  - Tween.interpolate_value is a pure function; time is NOT clamped (extrapolates).
#  - Tween: pause() + custom_step(delta) is a fully manual, exact stepper; an unpaused
#    tween also auto-processes per process frame; paused custom_step still steps.
#  - AnimationPlayer: playback_process_mode=MANUAL + advance(delta)/seek() is exact;
#    awaited frames do NOT advance a MANUAL player. IDLE advances on process frames,
#    PHYSICS on physics ticks.
#  - AnimationPlayer callback_mode_method DEFERRED queues method-track calls to the
#    end of the next frame; IMMEDIATE calls them synchronously inside advance().
#  - Animation.value_track_interpolate is a pure sampler (NEAREST/LINEAR/CUBIC).
#  - stop() resets the animated property to the animation's t=0 value (not the
#    pre-play value).

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _names(objs: Array) -> String:
	var out: Array[String] = []
	for o in objs:
		out.append(String(o["name"]))
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

func _ps(arr: Array) -> String:
	var parts: Array[String] = []
	for v in arr:
		parts.append(str(v))
	return "[" + ",".join(parts) + "]"

func _lib(anims: Dictionary) -> AnimationLibrary:
	var lib := AnimationLibrary.new()
	for name in anims:
		lib.add_animation(name, anims[name])
	return lib

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

func _player_for(target: Node2D, anims: Dictionary) -> AnimationPlayer:
	var player := AnimationPlayer.new()
	player.name = "AP"
	target.add_child(player)
	player.add_animation_library("", _lib(anims))
	return player

func _initialize() -> void:
	var arm := _arg("arm", "census")
	match arm:
		"census": _arm_census()
		"tweenval": _arm_tweenval()
		"tweenval_grid": _arm_tweenval_grid()
		"tweenstep": _arm_tweenstep()
		"tweenchain": await _arm_tweenchain()
		"tweenproc": await _arm_tweenproc()
		"animseek": await _arm_animseek()
		"animmethod": await _arm_animmethod()
		"animtrack": _arm_animtrack()
		"animblend": await _arm_animblend()
		"animproc": await _arm_animproc()
		_: print("PASS anim_lattice unknown arm=", arm)
	quit(0)

# ------------------------------------------------------------------ census (pure)
func _arm_census() -> void:
	var ap := AnimationPlayer.new()
	var an := Animation.new()
	var tw := create_tween()
	print("PASS anim_lattice census ",
		"ap_is_mixer=", ap is AnimationMixer, " ap_is_node=", ap is Node,
		" tw_is_ref=", tw is RefCounted, " anim_is_res=", an is Resource,
		" anim_consts=", _consts("Animation"),
		" mixer_consts=", _consts("AnimationMixer"),
		" player_consts=", _consts("AnimationPlayer"),
		" tween_consts=", _consts("Tween"),
		" ap_defaults=[proc=", ap.playback_process_mode, ",cbm=", ap.callback_mode_method,
		",cbp=", ap.callback_mode_process, ",cbd=", ap.callback_mode_discrete,
		",root=", ap.root_node, ",active=", ap.active, ",speed=", ap.speed_scale,
		",default_blend=", ap.playback_default_blend_time, ",auto_capture=", ap.is_auto_capture(), "]",
		" anim_defaults=[len=", an.length, ",loop=", an.loop_mode, ",step=", an.step, ",tracks=", an.get_track_count(), "]",
		" ap_signals=", _names(ap.get_signal_list()),
		" tw_signals=", _names(tw.get_signal_list()),
		" an_m_count=", an.get_method_list().size(),
		" tw_m_count=", tw.get_method_list().size(),
		" ap_m_count=", ap.get_method_list().size(),
		" cache_methods=", _method_names(ap, "cache"),
		" capture_methods=", _method_names(ap, "capture"),
		" blend_methods=", _method_names(ap, "blend"),
		" an_sample_methods=", _method_names(an, "interpolate"),
		" tw_step_methods=", _method_names(tw, "step"))
	tw.kill()
	ap.free()

# ------------------------------------------------------------------ tweenval (pure)
func _arm_tweenval() -> void:
	print("PASS anim_lattice tweenval r91_exact=", str(Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_OUT)),
		" expo_in_05=", str(Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_IN)),
		" expo_in_10=", str(Tween.interpolate_value(0.0, 10.0, 1.0, 1.0, Tween.TRANS_EXPO, Tween.EASE_IN)),
		" expo_out_05=", str(Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_OUT)),
		" expo_out_10=", str(Tween.interpolate_value(0.0, 10.0, 1.0, 1.0, Tween.TRANS_EXPO, Tween.EASE_OUT)),
		" clamp_neg=", str(Tween.interpolate_value(0.0, 10.0, -0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),
		" clamp_over=", str(Tween.interpolate_value(0.0, 10.0, 1.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),
		" int_025=", str(Tween.interpolate_value(0, 10, 0.25, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),
		" int_050=", str(Tween.interpolate_value(0, 10, 0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),
		" int_075=", str(Tween.interpolate_value(0, 10, 0.75, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),
		" vec_025=", str(Tween.interpolate_value(Vector2(1, 2), Vector2(4, 8), 0.25, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),
		" color_050=", str(Tween.interpolate_value(Color(0, 0, 0, 1), Color(1, 0.5, 0, 0), 0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),
		" form_in_err=", absf(Tween.interpolate_value(0.0, 1.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_IN) - (pow(2.0, 10.0 * (0.5 - 1.0)) - 0.001)),
		" form_out_err=", absf(Tween.interpolate_value(0.0, 1.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_OUT) - 1.001 * (1.0 - pow(2.0, -10.0 * 0.5))))

func _arm_tweenval_grid() -> void:
	var trans: Array = [Tween.TRANS_LINEAR, Tween.TRANS_SINE, Tween.TRANS_QUINT, Tween.TRANS_QUART,
		Tween.TRANS_QUAD, Tween.TRANS_EXPO, Tween.TRANS_ELASTIC, Tween.TRANS_CUBIC, Tween.TRANS_CIRC,
		Tween.TRANS_BOUNCE, Tween.TRANS_BACK, Tween.TRANS_SPRING]
	var tn: Array = ["lin", "sin", "qui", "qua", "qad", "expo", "ela", "cub", "cir", "bou", "bac", "spr"]
	var ease: Array = [Tween.EASE_IN, Tween.EASE_OUT, Tween.EASE_IN_OUT, Tween.EASE_OUT_IN]
	var en: Array = ["in", "out", "io", "oi"]
	var rows: Array[String] = []
	for i in range(trans.size()):
		var cells: Array[String] = []
		for j in range(ease.size()):
			var vals: Array[String] = []
			for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
				vals.append(str(Tween.interpolate_value(0.0, 10.0, t, 1.0, trans[i], ease[j])))
			cells.append("%s=%s" % [en[j], ",".join(vals)])
		rows.append("%s %s" % [tn[i], " ".join(cells)])
	print("PASS anim_lattice tweenval_grid ", " ".join(rows))

# ------------------------------------------------------------------ tweenstep (manual stepper)
func _arm_tweenstep() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var tw := create_tween()
	tw.tween_property(target, "position:x", 10.0, 1.0)
	var fin := [0]
	var stepfin := [0]
	tw.finished.connect(func(): fin[0] += 1)
	tw.step_finished.connect(func(_i): stepfin[0] += 1)
	var created := [tw.is_running(), tw.is_valid(), target.position.x, tw.get_total_elapsed_time()]
	tw.custom_step(0.5)
	var step05 := [target.position.x, tw.is_running(), tw.get_total_elapsed_time(), fin[0], stepfin[0]]
	tw.custom_step(0.5)
	var step10 := [target.position.x, tw.is_running(), tw.get_total_elapsed_time(), fin[0], stepfin[0]]
	tw.custom_step(0.5)
	var step_again := [target.position.x, tw.is_running(), tw.get_total_elapsed_time(), fin[0], stepfin[0]]
	# paused stepper: no auto processing, custom_step still exact
	var t2 := create_tween()
	t2.tween_property(target, "position:y", 20.0, 1.0)
	t2.pause()
	var pfin := [0]
	t2.finished.connect(func(): pfin[0] += 1)
	t2.custom_step(0.25)
	var paused := [target.position.y, t2.is_running(), t2.is_valid(), t2.get_total_elapsed_time(), pfin[0]]
	t2.custom_step(0.75)
	var paused_done := [target.position.y, t2.is_running(), t2.get_total_elapsed_time(), pfin[0]]
	# loops: 2 loops of a 0.5 s leg
	var t3 := create_tween()
	t3.set_loops(2)
	t3.tween_property(target, "scale:x", 2.0, 0.5)
	var lfin := [0]
	var loopfin := [0]
	t3.finished.connect(func(): lfin[0] += 1)
	t3.loop_finished.connect(func(_c): loopfin[0] += 1)
	t3.pause()
	t3.custom_step(0.5)
	var loop1 := [target.scale.x, t3.get_loops_left(), lfin[0], loopfin[0]]
	t3.custom_step(0.5)
	var loop2 := [target.scale.x, t3.get_loops_left(), lfin[0], loopfin[0]]
	print("PASS anim_lattice tweenstep ",
		"created=", _ps(created), " step05=", _ps(step05), " step10=", _ps(step10),
		" step_again=", _ps(step_again), " paused=", _ps(paused), " paused_done=", _ps(paused_done),
		" loop1=", _ps(loop1), " loop2=", _ps(loop2))

# ------------------------------------------------------------------ tweenchain (parallel/interval/callback/method/kill)
func _arm_tweenchain() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	# sequential legs (default)
	var t1 := create_tween()
	t1.tween_property(target, "position:x", 20.0, 0.5)
	t1.tween_property(target, "position:x", 40.0, 0.5)
	t1.pause()
	t1.custom_step(0.5)
	var seq1 := target.position.x
	t1.custom_step(0.25)
	var seq2 := target.position.x
	t1.custom_step(0.25)
	var seq3 := target.position.x
	# parallel
	var t2 := create_tween()
	t2.set_parallel(true)
	t2.tween_property(target, "position:y", 60.0, 1.0)
	t2.tween_property(target, "scale:x", 3.0, 1.0)
	t2.pause()
	t2.custom_step(0.5)
	var par := [target.position.y, target.scale.x]
	# interval + callback + method
	var cb := [0]
	var mvals: Array = []
	var t3 := create_tween()
	t3.tween_interval(0.5)
	t3.tween_callback(func(): cb[0] += 1)
	t3.tween_method(func(v): mvals.append(v), 0.0, 10.0, 1.0)
	t3.pause()
	t3.custom_step(0.5)
	var int_cb: int = cb[0]
	var int_m := mvals.duplicate()
	t3.custom_step(0.5)
	var post_cb: int = cb[0]
	var post_m := mvals.duplicate()
	t3.custom_step(0.1)
	var extra_cb: int = cb[0]
	# node-bound tween killed with the node
	var n := Node2D.new()
	n.name = "N"
	root.add_child(n)
	var tn := n.create_tween()
	tn.tween_property(n, "position:x", 50.0, 1.0)
	await process_frame
	tn.custom_step(0.25)
	var node_before := [tn.is_valid(), tn.is_running()]
	n.free()
	var node_right_after := [tn.is_valid(), tn.is_running()]
	tn.custom_step(0.25)
	var node_stepped_after_free := [tn.is_valid(), tn.is_running()]
	await process_frame
	var node_after_frame := [tn.is_valid(), tn.is_running()]
	# explicit kill
	var t4 := create_tween()
	t4.tween_property(target, "z_index", 9, 1.0)
	t4.pause()
	t4.custom_step(0.25)
	var killed_before := [t4.is_valid(), t4.is_running()]
	t4.kill()
	var killed_after := [t4.is_valid(), t4.is_running()]
	print("PASS anim_lattice tweenchain ",
		"seq=", _ps([seq1, seq2, seq3]),
		" par=", _ps(par),
		" interval=[cb_at_050=", int_cb, ",mvals_at_050=", _ps(int_m), ",cb_at_100=", post_cb,
		",mvals_at_100=", _ps(post_m), ",cb_after_extra=", extra_cb, "]",
		" node_free=[before=", _ps(node_before), ",right_after=", _ps(node_right_after),
		",stepped_after_free=", _ps(node_stepped_after_free), ",after_frame=", _ps(node_after_frame), "]",
		" kill=[before=", _ps(killed_before), ",after=", _ps(killed_after), "]")

# ------------------------------------------------------------------ tweenproc (process-mode coupling)
func _arm_tweenproc() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	# default process mode is IDLE: an unpaused tween auto-advances on process frames
	var t1 := create_tween()
	t1.tween_property(target, "position:y", 60.0, 1.0)
	var y0 := target.position.y
	for i in range(3):
		await process_frame
	var y1 := target.position.y
	var y_paused := target.position.y
	for i in range(3):
		await process_frame
	var y_paused_after := target.position.y
	# PHYSICS process mode
	var t2 := create_tween()
	t2.set_process_mode(Tween.TWEEN_PROCESS_PHYSICS)
	t2.tween_property(target, "position:x", 1000.0, 1.0)
	var x0 := target.position.x
	for i in range(3):
		await process_frame
	var x1 := target.position.x
	for i in range(3):
		await physics_frame
	var x2 := target.position.x
	# manual stepper is exact regardless of process mode
	t2.kill()
	var t3 := create_tween()
	t3.set_process_mode(Tween.TWEEN_PROCESS_PHYSICS)
	t3.tween_property(target, "scale:y", 5.0, 1.0)
	t3.pause()
	var manual_before := target.scale.y
	t3.custom_step(0.25)
	var manual_after := target.scale.y
	var auto_advanced := y1 > y0
	var paused_frozen := y_paused_after == y_paused
	var phys_advanced := x2 > x1
	var manual_exact := is_equal_approx(manual_after, 2.0)
	print("PASS anim_lattice tweenproc ",
		"auto=[y0=", y0, ",after3proc=", y1, "]",
		" paused=[at_pause=", y_paused, ",after3frames=", y_paused_after, ",running=", t1.is_running(), "]",
		" phys=[x0=", x0, ",after3proc=", x1, ",after3phys=", x2, "]",
		" phys_manual=[before=", manual_before, ",after_step025=", manual_after, "]",
		" stable=[auto_advanced=", auto_advanced, ",paused_frozen=", paused_frozen,
		",phys_advanced=", phys_advanced, ",manual_exact=", manual_exact, "]")
	t1.kill()
	t3.kill()

# ------------------------------------------------------------------ animseek (MANUAL advance/seek)
func _arm_animseek() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _player_for(target, {
		"move": _value_anim([[0.0, 0.0], [1.0, 100.0]]),
		"loop": _value_anim([[0.0, 0.0], [0.5, 50.0]], 0.5, Animation.LOOP_LINEAR),
	})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	var fin: Array = []
	player.animation_finished.connect(func(n): fin.append(n))
	# play() does not apply the pose; advance() does
	target.position.x = 7.0
	player.play("move")
	var at_play := [target.position.x, player.is_playing(), player.current_animation_position, player.current_animation]
	player.advance(0.25)
	var at_025 := [target.position.x, player.current_animation_position]
	player.seek(0.75, true)
	var at_seek_up := [target.position.x, player.current_animation_position]
	player.seek(0.5, false)
	var at_seek_noup := [target.position.x, player.current_animation_position]
	player.advance(1.0)
	var at_cross := [target.position.x, player.current_animation_position, player.is_playing(), fin.size()]
	await process_frame
	var after_frame := [target.position.x, fin.size()]
	# stop resets to the animation's t=0 value
	target.position.x = 7.0
	player.play("move")
	player.advance(0.5)
	var before_stop := target.position.x
	player.stop()
	var after_stop := [target.position.x, player.is_playing(), player.current_animation, player.assigned_animation]
	# speed_scale
	player.play("move")
	player.speed_scale = 2.0
	player.advance(0.25)
	var speed2 := [target.position.x, player.current_animation_position]
	player.speed_scale = 0.0
	player.advance(0.25)
	var speed0 := [target.position.x, player.current_animation_position]
	player.speed_scale = 1.0
	# replay of the SAME animation name does not restart; a different one does
	player.stop()
	player.play("move")
	player.advance(0.5)
	var replay_before := [target.position.x, player.current_animation_position]
	player.play("move")
	var replay_same := [target.position.x, player.current_animation_position]
	player.play("loop")
	var play_other := [target.position.x, player.current_animation_position, player.assigned_animation]
	player.play("move")
	var back_other := [target.position.x, player.current_animation_position]
	# clean paused advance (stop first so the timeline starts at 0)
	player.stop()
	player.play("move")
	player.pause()
	player.advance(0.5)
	var paused_adv := [target.position.x, player.is_playing()]
	# loop mode
	player.stop()
	var fin_before_loop := fin.size()
	player.play("loop")
	player.advance(0.75)
	var looped := [target.position.x, player.current_animation_position, fin.size() - fin_before_loop]
	# seek beyond length clamps, keeps playing
	player.stop()
	player.play("move")
	player.seek(2.0, true)
	var seek_over := [target.position.x, player.current_animation_position, player.is_playing()]
	# MANUAL mode: awaited frames do not advance
	player.stop()
	player.play("move")
	await process_frame
	await process_frame
	var manual_frames := [target.position.x, player.current_animation_position]
	print("PASS anim_lattice animseek ",
		"at_play=", _ps(at_play), " adv025=", _ps(at_025),
		" seek_up=", _ps(at_seek_up), " seek_noup=", _ps(at_seek_noup),
		" cross=", _ps(at_cross), " after_frame=", _ps(after_frame),
		" before_stop=", before_stop, " after_stop=", _ps(after_stop),
		" speed2=", _ps(speed2), " speed0=", _ps(speed0),
		" replay_before=", _ps(replay_before), " replay_same=", _ps(replay_same),
		" play_other=", _ps(play_other), " back_other=", _ps(back_other),
		" paused_adv=", _ps(paused_adv), " looped=", _ps(looped),
		" seek_over=", _ps(seek_over),
		" manual_frames=", _ps(manual_frames))

# ------------------------------------------------------------------ animmethod (callback modes)
func _arm_animmethod() -> void:
	var target := MethodTarget.new()
	target.name = "MT"
	root.add_child(target)
	var anim := Animation.new()
	anim.length = 1.0
	var tr := anim.add_track(Animation.TYPE_METHOD)
	anim.track_set_path(tr, NodePath("."))
	anim.track_insert_key(tr, 0.2, {"method": "notify", "args": [7]})
	anim.track_insert_key(tr, 0.5, {"method": "notify", "args": [8]})
	var player := _player_for(target, {"m": anim})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	var started: Array = []
	var changed: Array = []
	var cur_changed: Array = []
	player.animation_started.connect(func(n): started.append(n))
	player.animation_changed.connect(func(o, n): changed.append([o, n]))
	player.current_animation_changed.connect(func(n): cur_changed.append(n))
	player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_DEFERRED
	player.play("m")
	var sig_at_play := [started.size(), changed.size(), cur_changed.size()]
	player.advance(1.0)
	var deferred_adv := target.calls.duplicate()
	await process_frame
	var deferred_frame := target.calls.duplicate()
	var sig_after_frame := [started.size(), changed.size(), cur_changed.size()]
	target.calls.clear()
	player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
	player.stop()
	player.play("m")
	player.advance(1.0)
	var immediate_adv := target.calls.duplicate()
	await process_frame
	var immediate_frame := target.calls.duplicate()
	target.calls.clear()
	anim.track_set_enabled(tr, false)
	player.stop()
	player.play("m")
	player.advance(1.0)
	var disabled := target.calls.duplicate()
	print("PASS anim_lattice animmethod ",
		"sig_at_play=", _ps(sig_at_play), " deferred_adv=", _ps(deferred_adv),
		" deferred_frame=", _ps(deferred_frame), " sig_after_frame=", _ps(sig_after_frame),
		" immediate_adv=", _ps(immediate_adv), " immediate_frame=", _ps(immediate_frame),
		" disabled_track=", _ps(disabled),
		" started_names=", _ps(started), " changed=", _ps(changed), " cur_changed=", _ps(cur_changed))

class MethodTarget extends Node2D:
	var calls: Array = []
	func notify(v: int) -> void:
		calls.append(v)

# ------------------------------------------------------------------ animtrack (pure sampler)
func _arm_animtrack() -> void:
	var two := Animation.new()
	two.length = 1.0
	var t2 := two.add_track(Animation.TYPE_VALUE)
	two.track_set_path(t2, NodePath(".:position:x"))
	two.track_insert_key(t2, 0.0, 0.0)
	two.track_insert_key(t2, 1.0, 10.0)
	var two_vals: Array[String] = []
	var two_default := two.track_get_interpolation_type(t2)
	for it in [Animation.INTERPOLATION_NEAREST, Animation.INTERPOLATION_LINEAR, Animation.INTERPOLATION_CUBIC]:
		two.track_set_interpolation_type(t2, it)
		two_vals.append("it%d=[t05=%s,t09=%s,t10=%s]" % [it, two.value_track_interpolate(t2, 0.5),
			two.value_track_interpolate(t2, 0.9), two.value_track_interpolate(t2, 1.0)])
	var three := Animation.new()
	three.length = 1.0
	var t3 := three.add_track(Animation.TYPE_VALUE)
	three.track_set_path(t3, NodePath(".:position:x"))
	three.track_insert_key(t3, 0.0, 0.0)
	three.track_insert_key(t3, 0.5, 10.0)
	three.track_insert_key(t3, 1.0, 0.0)
	var three_vals: Array[String] = []
	for it in [Animation.INTERPOLATION_NEAREST, Animation.INTERPOLATION_LINEAR, Animation.INTERPOLATION_CUBIC]:
		three.track_set_interpolation_type(t3, it)
		three_vals.append("it%d=[t025=%s,t075=%s]" % [it, three.value_track_interpolate(t3, 0.25),
			three.value_track_interpolate(t3, 0.75)])
	var bez := Animation.new()
	bez.length = 1.0
	var tb := bez.add_track(Animation.TYPE_BEZIER)
	bez.track_set_path(tb, NodePath(".:position:x"))
	bez.bezier_track_insert_key(tb, 0.0, 0.0, Vector2(0, 0), Vector2(0.5, 0))
	bez.bezier_track_insert_key(tb, 1.0, 10.0, Vector2(-0.5, 0), Vector2(0, 0))
	var bez_vals := [bez.bezier_track_interpolate(tb, 0.25), bez.bezier_track_interpolate(tb, 0.5), bez.bezier_track_interpolate(tb, 0.75)]
	print("PASS anim_lattice animtrack ",
		"two_key=", _ps(two_vals), " three_key=", _ps(three_vals),
		" two_default_interp=", two_default,
		" three_key_count=", three.track_get_key_count(t3),
		" k0=", three.track_get_key_value(t3, 0), " kt1=", three.track_get_key_time(t3, 1), " k1=", three.track_get_key_value(t3, 1),
		" bezier=", _ps(bez_vals), " bezier_key_count=", bez.track_get_key_count(tb),
		" track_enabled=", three.track_is_enabled(t3), " track_type=", three.track_get_type(t3),
		" track_path=", three.track_get_path(t3))

# ------------------------------------------------------------------ animblend (blend lattice + capture)
func _blend_from_finished(player: AnimationPlayer, target: Node2D, steps: int, dt: float) -> Array:
	player.stop()
	player.play("a")
	player.advance(1.0)
	player.play("b")
	var out: Array[String] = []
	for i in range(steps):
		player.advance(dt)
		out.append(str(target.position.x))
	return out

func _arm_animblend() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _player_for(target, {
		"a": _value_anim([[0.0, 0.0], [1.0, 100.0]]),
		"b": _const_anim(500.0),
	})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	# crossfade from a finished animation — step-granularity lattice
	player.set_blend_time("a", "b", 1.0)
	var blend_get := player.get_blend_time("a", "b")
	var finished_010 := _blend_from_finished(player, target, 10, 0.1)
	var finished_005 := _blend_from_finished(player, target, 20, 0.05)
	var finished_020 := _blend_from_finished(player, target, 5, 0.2)
	# crossfade from a running animation (uniform 0.1 steps)
	player.stop()
	player.play("a")
	player.advance(0.5)
	var from_running: Array[String] = []
	player.play("b")
	for i in range(10):
		player.advance(0.1)
		from_running.append(str(target.position.x))
	# hard switch
	player.stop()
	player.play("a")
	player.advance(1.0)
	player.play("b", 0.0)
	var hard_at_play := target.position.x
	player.advance(0.25)
	var hard_after := target.position.x
	# default blend time
	player.stop()
	player.play("a")
	player.advance(1.0)
	player.set_default_blend_time(1.0)
	player.play("b")
	player.advance(0.5)
	var default_blend_mid := target.position.x
	player.set_default_blend_time(0.0)
	# capture route
	player.stop()
	player.play("a")
	player.advance(0.5)
	var before_capture := target.position.x
	player.play_with_capture("b", 1.0)
	var cap_seq: Array[String] = []
	for i in range(10):
		player.advance(0.1)
		cap_seq.append(str(target.position.x))
	print("PASS anim_lattice animblend ",
		"blend_get=", blend_get,
		" finished_010=[", ",".join(finished_010), "]",
		" finished_005=[", ",".join(finished_005), "]",
		" finished_020=[", ",".join(finished_020), "]",
		" running_from_50=[", ",".join(from_running), "]",
		" hard=[at_play=", hard_at_play, ",after_025=", hard_after, "]",
		" default_blend_mid=", default_blend_mid,
		" capture=[before=", before_capture, ",seq=", ",".join(cap_seq), "]")

# ------------------------------------------------------------------ animproc (process modes, signals, caches)
func _arm_animproc() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _player_for(target, {
		"move": _value_anim([[0.0, 0.0], [1.0, 100.0]]),
		"quick": _value_anim([[0.0, 0.0], [0.1, 5.0]], 0.1),
	})
	await process_frame
	var caches := [0]
	var mixer_upd := [0]
	var mixer_app := [0]
	player.caches_cleared.connect(func(): caches[0] += 1)
	player.mixer_updated.connect(func(): mixer_upd[0] += 1)
	player.mixer_applied.connect(func(): mixer_app[0] += 1)
	# IDLE coupling
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE
	player.play("move")
	var idle0 := target.position.x
	for i in range(3):
		await process_frame
	var idle1 := target.position.x
	for i in range(3):
		await physics_frame
	var idle2 := target.position.x
	# PHYSICS coupling
	player.stop()
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_PHYSICS
	player.play("move")
	var phys0 := target.position.x
	for i in range(3):
		await process_frame
	var phys1 := target.position.x
	for i in range(3):
		await physics_frame
	var phys2 := target.position.x
	# MANUAL: no frame advance
	player.stop()
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.play("move")
	player.advance(0.25)
	var man0 := target.position.x
	for i in range(3):
		await process_frame
	var man1 := target.position.x
	# speed_scale=0 freeze and active=false
	player.stop()
	player.speed_scale = 0.0
	player.play("move")
	player.advance(1.0)
	var frozen := [target.position.x, player.is_playing(), player.current_animation_position]
	player.speed_scale = 1.0
	player.stop()
	player.play("move")
	player.active = false
	player.advance(0.5)
	var inactive := [target.position.x, player.is_playing()]
	player.active = true
	# quick animation finished timing (IDLE)
	player.stop()
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE
	var fin_frame := [-1]
	var frames := [0]
	player.animation_finished.connect(func(n): fin_frame[0] = frames[0])
	player.play("quick")
	while frames[0] < 30:
		await process_frame
		frames[0] += 1
		if fin_frame[0] >= 0:
			break
	# cache/signal counters
	var caches_before: int = caches[0]
	player.clear_caches()
	var caches_after: int = caches[0]
	var stable := {
		"manual_frame_frozen": man1 == man0,
		"manual_exact": is_equal_approx(man0, 25.0),
		"speed0_frozen": frozen[0] == 0.0 and frozen[2] == 0.0,
		"inactive_advance": inactive[0] == 50.0,
		"fin_fired": fin_frame[0] >= 0,
		"caches_once": (caches_after - caches_before) == 1,
		"mixer_updated_zero": mixer_upd[0] == 0,
	}
	print("PASS anim_lattice animproc ",
		"idle=[x0=", idle0, ",after3proc=", idle1, ",after3phys=", idle2, ",pos=", player.current_animation_position, "]",
		" phys=[x0=", phys0, ",after3proc=", phys1, ",after3phys=", phys2, "]",
		" manual=[x=", man0, ",after3frames=", man1, "]",
		" frozen=", _ps(frozen), " inactive=", _ps(inactive),
		" quick=[frames_to_finish=", frames[0], ",fin_frame=", fin_frame[0], ",x=", target.position.x, "]",
		" caches_delta=", caches_after - caches_before, " caches_total=", caches_after,
		" mixer_updated=", mixer_upd[0], " mixer_applied=", mixer_app[0],
		" is_playing=", player.is_playing(),
		" stable=[manual_frame_frozen=", stable["manual_frame_frozen"], ",manual_exact=", stable["manual_exact"],
		",speed0_frozen=", stable["speed0_frozen"], ",inactive_advance=", stable["inactive_advance"],
		",fin_fired=", stable["fin_fired"], ",caches_once=", stable["caches_once"],
		",mixer_updated_zero=", stable["mixer_updated_zero"], "]")
