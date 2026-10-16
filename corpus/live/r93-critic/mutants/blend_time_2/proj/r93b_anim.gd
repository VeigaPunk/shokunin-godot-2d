extends SceneTree
# r93-boundary attack probe (r93b) — scheduler-sensitivity of the r93 scout's
# AnimationPlayer + Tween authorability claims under quiet / hog load / --fixed-fps.
#
# Launch (battery shape):
#   godot --headless [--fixed-fps N] --path proj --script res://r93b_anim.gd -- --arm=<arm>
# Every arm prints exactly one `PASS r93b_anim <arm> ...` line.
#
# Arms
#  clock      — launch fingerprint: process-delta distribution, physics interleave, engine knobs.
#  manual_inv — manual-clock invariance: paused-Tween custom_step and MANUAL advance with
#               awaited process/physics frames interleaved, plus an unpaused control.
#  frame      — frame-coupled lattice: IDLE per-process-frame advance, PHYSICS per-tick advance,
#               unpaused tween auto-advance, mixer_applied rate, quick-anim frames-to-finish.
#  deferred   — DEFERRED/IMMEDIATE method-callback flush timing across frame kinds + the
#               key-relative lag of a frame-coupled DEFERRED call.
#  purity     — pure functions + extreme/negative custom_step deltas + runtime overshoot clamp.
#  blend      — crossfade weight law under this launch mode + an await-interleaved control.

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
	var arm := _arg("arm", "clock")
	match arm:
		"clock": await _arm_clock()
		"manual_inv": await _arm_manual_inv()
		"frame": await _arm_frame()
		"deferred": await _arm_deferred()
		"purity": _arm_purity()
		"blend": await _arm_blend()
		_: print("PASS r93b_anim unknown arm=", arm)
	quit(0)

# ---------------------------------------------------------------- clock (launch fingerprint)
func _arm_clock() -> void:
	var deltas: Array = []
	var pf0 := Engine.get_process_frames()
	var ph0 := Engine.get_physics_frames()
	var t0 := Time.get_ticks_usec()
	for i in range(20):
		await process_frame
		deltas.append(root.get_process_delta_time())
	var t1 := Time.get_ticks_usec()
	var pf_span := Engine.get_process_frames() - pf0
	var ph_span := Engine.get_physics_frames() - ph0
	var dmin: float = 1e18
	var dmax: float = -1e18
	var dsum := 0.0
	for d in deltas:
		dmin = minf(dmin, d)
		dmax = maxf(dmax, d)
		dsum += d
	print("PASS r93b_anim clock",
		" max_fps=", Engine.max_fps, " phys_tps=", Engine.physics_ticks_per_second,
		" time_scale=", Engine.time_scale,
		" proc_delta=[first=", deltas[0], ",min=", dmin, ",max=", dmax, ",mean=", dsum / 20.0,
		",last=", deltas[19], "]",
		" deltas=", _ps(deltas),
		" wall_us_per_await=", float(t1 - t0) / 20.0,
		" fps_reported=", Engine.get_frames_per_second(),
		" proc_frames_20=", pf_span, " phys_frames_20=", ph_span,
		" phys_per_proc=", float(ph_span) / float(maxi(pf_span, 1)),
		" phys_delta=", root.get_physics_process_delta_time())

# ---------------------------------------------------------------- manual_inv (manual clock)
func _arm_manual_inv() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	await process_frame
	# paused tween: manual steps interleaved with awaited process/physics frames
	var t1 := create_tween()
	t1.tween_property(target, "position:x", 10.0, 1.0)
	t1.pause()
	t1.custom_step(0.25)
	var a := target.position.x
	for i in range(3):
		await process_frame
	var b := target.position.x
	t1.custom_step(0.25)
	var c := target.position.x
	for i in range(3):
		await physics_frame
	var d := target.position.x
	t1.custom_step(0.5)
	var e := target.position.x
	# MANUAL player: same treatment
	var player := _player_for(target, {"move": _value_anim([[0.0, 0.0], [1.0, 100.0]])})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.play("move")
	player.advance(0.25)
	var f := target.position.x
	for i in range(3):
		await process_frame
	var g := target.position.x
	player.advance(0.25)
	var h := target.position.x
	for i in range(3):
		await physics_frame
	var k := target.position.x
	player.advance(0.5)
	var m := target.position.x
	# control: an unpaused tween DOES move across awaited frames
	var t2 := create_tween()
	t2.tween_property(target, "position:y", 60.0, 1.0)
	t2.custom_step(0.25)
	var n := target.position.y
	for i in range(3):
		await process_frame
	var o := target.position.y
	t2.pause()
	print("PASS r93b_anim manual_inv",
		" paused=[a=", a, ",b=", b, ",c=", c, ",d=", d, ",e=", e, "]",
		" manual=[f=", f, ",g=", g, ",h=", h, ",k=", k, ",m=", m, "]",
		" unpaused=[n=", n, ",o=", o, "]",
		" inv=[paused_proc=", a == b, ",paused_phys=", c == d, ",manual_proc=", f == g,
		",manual_phys=", h == k, "]",
		" step_exact=[paused025=", is_equal_approx(a, 2.5), ",paused_done=", is_equal_approx(e, 10.0),
		",manual025=", is_equal_approx(f, 25.0), ",manual_done=", is_equal_approx(m, 100.0), "]",
		" unpaused_moved=", o > n,
		" proc_delta=", root.get_process_delta_time())

# ---------------------------------------------------------------- frame (frame-coupled lattice)
func _arm_frame() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _player_for(target, {
		"move": _value_anim([[0.0, 0.0], [1.0, 100.0]]),
		"quick": _value_anim([[0.0, 0.0], [0.1, 5.0]], 0.1),
	})
	await process_frame
	var applied := [0]
	player.mixer_applied.connect(func(): applied[0] += 1)
	# IDLE: per-process-frame advance
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE
	player.play("move")
	var xs: Array = []
	var ap0: int = applied[0]
	for i in range(10):
		await process_frame
		if i == 0 or i == 1 or i == 2 or i == 4 or i == 9:
			xs.append(target.position.x)
	var pos10 := player.current_animation_position
	var applied10: int = applied[0] - ap0
	player.stop()
	# PHYSICS: per-physics-tick advance
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_PHYSICS
	player.play("move")
	var ys: Array = []
	var pf0 := Engine.get_process_frames()
	for i in range(6):
		await physics_frame
		ys.append(target.position.x)
	var proc_during_6phys := Engine.get_process_frames() - pf0
	player.stop()
	# unpaused tween auto-advance
	var t := create_tween()
	t.tween_property(target, "position:y", 60.0, 1.0)
	var tvals: Array = []
	for i in range(5):
		await process_frame
		tvals.append(target.position.y)
	t.pause()
	# quick animation: frames-to-finish under IDLE
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE
	var frames := [0]
	var fin_frame := [-1]
	player.animation_finished.connect(func(n): fin_frame[0] = frames[0])
	player.play("quick")
	while frames[0] < 60:
		await process_frame
		frames[0] += 1
		if fin_frame[0] >= 0:
			break
	var quick_x := target.position.x
	var quick_pos := player.current_animation_position
	player.stop()
	print("PASS r93b_anim frame",
		" idle=[x1=", xs[0], ",x2=", xs[1], ",x3=", xs[2], ",x5=", xs[3], ",x10=", xs[4], "]",
		" idle_per_frame=", (float(xs[4]) - float(xs[3])) / 5.0,
		" pos10=", pos10, " mixer_applied_10=", applied10,
		" phys=[y1=", ys[0], ",y2=", ys[1], ",y3=", ys[2], ",y6=", ys[5], "]",
		" proc_frames_during_6phys=", proc_during_6phys,
		" tween5=", _ps(tvals),
		" quick=[frames=", frames[0], ",fin_frame=", fin_frame[0], ",x=", quick_x, ",pos=", quick_pos, "]",
		" proc_delta=", root.get_process_delta_time(),
		" phys_delta=", root.get_physics_process_delta_time())

class MethodTarget extends Node2D:
	var calls: Array = []
	func notify(v: int) -> void:
		calls.append(v)

# ---------------------------------------------------------------- deferred (callback flush timing)
func _arm_deferred() -> void:
	var target := MethodTarget.new()
	target.name = "MT"
	root.add_child(target)
	var anim := Animation.new()
	anim.length = 1.0
	var tr := anim.add_track(Animation.TYPE_METHOD)
	anim.track_set_path(tr, NodePath("."))
	anim.track_insert_key(tr, 0.2, {"method": "notify", "args": [7]})
	anim.track_insert_key(tr, 0.5, {"method": "notify", "args": [8]})
	var short := Animation.new()
	short.length = 0.2
	var trs := short.add_track(Animation.TYPE_METHOD)
	short.track_set_path(trs, NodePath("."))
	short.track_insert_key(trs, 0.04, {"method": "notify", "args": [1]})
	short.track_insert_key(trs, 0.1, {"method": "notify", "args": [2]})
	var player := _player_for(target, {"m": anim, "s": short})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_DEFERRED
	# (a) manual advance: no calls in-frame; flush on the next process frame
	player.play("m")
	player.advance(1.0)
	var a1 := target.calls.duplicate()
	await process_frame
	var a2 := target.calls.duplicate()
	await process_frame
	var a3 := target.calls.duplicate()
	target.calls.clear()
	# (b) flush on a physics frame instead
	player.stop()
	player.play("m")
	player.advance(1.0)
	var b1 := target.calls.duplicate()
	await physics_frame
	var b2 := target.calls.duplicate()
	target.calls.clear()
	# (c) two manual advances before any frame
	player.stop()
	player.play("m")
	player.advance(0.3)
	player.advance(0.8)
	var c1 := target.calls.duplicate()
	await process_frame
	var c2 := target.calls.duplicate()
	target.calls.clear()
	# (d) IMMEDIATE: calls inside advance
	player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
	player.stop()
	player.play("m")
	player.advance(1.0)
	var d1 := target.calls.duplicate()
	await process_frame
	var d2 := target.calls.duplicate()
	target.calls.clear()
	# (e) frame-coupled IDLE + DEFERRED: key-relative lag of the call
	player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_DEFERRED
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE
	player.stop()
	player.play("s")
	var n := 0
	var first_at := -1
	var first_pos := -1.0
	var second_at := -1
	var second_pos := -1.0
	while n < 200:
		await process_frame
		n += 1
		if target.calls.size() >= 1 and first_at < 0:
			first_at = n
			first_pos = player.current_animation_position
		if target.calls.size() >= 2 and second_at < 0:
			second_at = n
			second_pos = player.current_animation_position
		if player.current_animation_position >= short.length and second_at >= 0:
			break
	await process_frame
	var final_calls := target.calls.duplicate()
	player.stop()
	print("PASS r93b_anim deferred",
		" manual_def=[after_adv=", _ps(a1), ",next_proc=", _ps(a2), ",second_proc=", _ps(a3), "]",
		" manual_def_phys=[after_adv=", _ps(b1), ",after_phys=", _ps(b2), "]",
		" two_adv=[after=", _ps(c1), ",flush=", _ps(c2), "]",
		" immediate=[after_adv=", _ps(d1), ",after_frame=", _ps(d2), "]",
		" idle_lag=[frames=", n, ",first_at=", first_at, ",first_pos=", first_pos,
		",second_at=", second_at, ",second_pos=", second_pos, ",final=", _ps(final_calls), "]",
		" proc_delta=", root.get_process_delta_time())

# ---------------------------------------------------------------- purity (pure + extremes)
func _arm_purity() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var expo_out_05: float = Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_OUT)
	var expo_in_05: float = Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_IN)
	var expo_in_10: float = Tween.interpolate_value(0.0, 10.0, 1.0, 1.0, Tween.TRANS_EXPO, Tween.EASE_IN)
	var expo_out_10: float = Tween.interpolate_value(0.0, 10.0, 1.0, 1.0, Tween.TRANS_EXPO, Tween.EASE_OUT)
	var clamp_neg: float = Tween.interpolate_value(0.0, 10.0, -0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)
	var clamp_over: float = Tween.interpolate_value(0.0, 10.0, 1.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)
	var int_050: int = Tween.interpolate_value(0, 10, 0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)
	var vec_025: Vector2 = Tween.interpolate_value(Vector2(1, 2), Vector2(4, 8), 0.25, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)
	var col_050: Color = Tween.interpolate_value(Color(0, 0, 0, 1), Color(1, 0.5, 0, 0), 0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)
	# pure track sampler
	var anim := Animation.new()
	anim.length = 1.0
	var tr := anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(tr, NodePath(".:position:x"))
	anim.track_insert_key(tr, 0.0, 0.0)
	anim.track_insert_key(tr, 1.0, 10.0)
	var tracks: Array[String] = []
	for it in [Animation.INTERPOLATION_NEAREST, Animation.INTERPOLATION_LINEAR, Animation.INTERPOLATION_CUBIC]:
		anim.track_set_interpolation_type(tr, it)
		tracks.append("it%d=[t05=%s,t09=%s,t10=%s]" % [it, anim.value_track_interpolate(tr, 0.5),
			anim.value_track_interpolate(tr, 0.9), anim.value_track_interpolate(tr, 1.0)])
	# extreme manual deltas on a paused tween
	var t1 := create_tween()
	t1.tween_property(target, "position:x", 10.0, 1.0)
	t1.pause()
	t1.custom_step(0.000000001)
	var tiny := target.position.x
	t1.custom_step(0.25)
	var mid := target.position.x
	t1.custom_step(1000000.0)
	var huge := target.position.x
	var huge_running := t1.is_running()
	# negative delta
	var t2 := create_tween()
	t2.tween_property(target, "position:y", 10.0, 1.0)
	t2.pause()
	t2.custom_step(-0.5)
	var neg := target.position.y
	var neg_elapsed := t2.get_total_elapsed_time()
	# runtime overshoot: does a BACK tween leave [start,target] mid-flight?
	var t3 := create_tween()
	t3.tween_property(target, "scale:y", 10.0, 1.0).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN_OUT)
	t3.pause()
	t3.custom_step(0.25)
	var back025 := target.scale.y
	t3.custom_step(0.25)
	var back050 := target.scale.y
	# 1000 tiny steps: elapsed accumulation
	var t4 := create_tween()
	t4.tween_property(target, "rotation", 1.0, 1.0)
	t4.pause()
	for i in range(1000):
		t4.custom_step(0.001)
	var accum := target.rotation
	# upper overshoot on a fresh node: SPRING/EASE_OUT goes above the target mid-flight
	var t5_target := Node2D.new()
	t5_target.name = "T5"
	root.add_child(t5_target)
	var t5 := create_tween()
	t5.tween_property(t5_target, "position:y", 10.0, 1.0).set_trans(Tween.TRANS_SPRING).set_ease(Tween.EASE_OUT)
	t5.pause()
	t5.custom_step(0.5)
	var spr050 := t5_target.position.y
	t5.custom_step(0.5)
	var spr100 := t5_target.position.y
	# ELASTIC/EASE_OUT undershoot on another fresh node
	var t6_target := Node2D.new()
	t6_target.name = "T6"
	root.add_child(t6_target)
	var t6 := create_tween()
	t6.tween_property(t6_target, "position:y", 10.0, 1.0).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	t6.pause()
	t6.custom_step(0.25)
	var ela025 := t6_target.position.y
	print("PASS r93b_anim purity",
		" expo=[out05=", expo_out_05, ",in05=", expo_in_05, ",in10=", expo_in_10, ",out10=", expo_out_10, "]",
		" clamp=[neg=", clamp_neg, ",over=", clamp_over, "]",
		" int050=", int_050, " vec025=", vec_025, " col050=", col_050,
		" track=", _ps(tracks),
		" deltas=[tiny=", tiny, ",mid=", mid, ",huge=", huge, ",huge_running=", huge_running,
		",neg=", neg, ",neg_elapsed=", neg_elapsed, "]",
		" overshoot=[back025=", back025, ",back050=", back050, "]",
		" overshoot2=[spr050=", spr050, ",spr100=", spr100, ",ela025=", ela025, "]",
		" accum1000=", accum)

# ---------------------------------------------------------------- blend (weight law + awaits)
func _blend_from_finished(player: AnimationPlayer, target: Node2D, steps: int, dt: float) -> Array[String]:
	player.stop()
	player.play("a")
	player.advance(1.0)
	player.play("b")
	var out: Array[String] = []
	for i in range(steps):
		player.advance(dt)
		out.append(str(target.position.x))
	return out

func _arm_blend() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _player_for(target, {
		"a": _value_anim([[0.0, 0.0], [1.0, 100.0]]),
		"b": _const_anim(500.0),
	})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	player.set_blend_time("a", "b", 2.0)
	var finished_010 := _blend_from_finished(player, target, 10, 0.1)
	var finished_020 := _blend_from_finished(player, target, 5, 0.2)
	# the same 10x0.1 lattice with one awaited process frame between steps
	player.stop()
	player.play("a")
	player.advance(1.0)
	player.play("b")
	var inter: Array[String] = []
	for i in range(10):
		player.advance(0.1)
		await process_frame
		inter.append(str(target.position.x))
	# hard switch with an awaited frame after the switch
	player.stop()
	player.play("a")
	player.advance(1.0)
	player.play("b", 0.0)
	player.advance(0.25)
	await process_frame
	var hard_after_frame := target.position.x
	print("PASS r93b_anim blend",
		" finished_010=[", ",".join(finished_010), "]",
		" finished_020=[", ",".join(finished_020), "]",
		" interleaved=[", ",".join(inter), "]",
		" interleaved_eq_plain=", finished_010 == inter,
		" hard_after_frame=", hard_after_frame,
		" proc_delta=", root.get_process_delta_time())
