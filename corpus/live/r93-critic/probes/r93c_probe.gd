extends SceneTree
# r93-critic seat probe — discriminating tests for the r93 encoded claims.
# NOT a fixture: lives in corpus/live/r93-critic/, never copied into corpus/fixtures.
# Launch: godot --headless --path <scratch> --script res://r93c_probe.gd -- --arm=<arm>
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

func _value_anim(keys: Array, length: float = 1.0) -> Animation:
	var anim := Animation.new()
	anim.length = length
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
	var arm := _arg("arm", "preplay")
	match arm:
		"preplay": await _arm_preplay()
		"physflush": await _arm_physflush()
		"physflush2": await _arm_physflush2()
		"overshoot": _arm_overshoot()
		_: print("PASS r93c_probe unknown arm=", arm)
	quit(0)

# ---------------------------------------------------------------- preplay
# Falsifiable question: after play(), does the FIRST awaited process frame read the
# PRE-PLAY value (claim wording) or the animation's t=0 pose? With a NON-ZERO
# pre-play value the two readings differ: pre-play => x1 == 5.0; t=0 pose => x1 == 0.0.
# Also: does the N-1 counting law survive a non-zero pre-play value?
func _arm_preplay() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var player := _player_for(target, {"move": _value_anim([[0.0, 0.0], [1.0, 100.0]])})
	await process_frame
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE
	target.position.x = 5.0
	var at_play := target.position.x
	player.play("move")
	var after_play := target.position.x
	var xs: Array = []
	var pos: Array = []
	var pfs: Array = []
	var pf0 := Engine.get_process_frames()
	for i in range(6):
		await process_frame
		xs.append(target.position.x)
		pos.append(player.current_animation_position)
		pfs.append(Engine.get_process_frames() - pf0)
	print("PASS r93c_probe preplay at_play=", at_play, " after_play=", after_play,
		" xs=", _ps(xs), " pos=", _ps(pos), " proc_frames=", _ps(pfs),
		" proc_delta=", root.get_process_delta_time(),
		" n1_x1_is_preplay=", is_equal_approx(xs[0], 5.0),
		" n1_x1_is_t0=", is_equal_approx(xs[0], 0.0),
		" x2_eq_one_step=", is_equal_approx(xs[1], root.get_process_delta_time() * 100.0))

# ---------------------------------------------------------------- physflush
# Falsifiable question: does a DEFERRED method-call queue flush on a PHYSICS frame
# with NO intervening process frame? Count process frames across the await.
func _arm_physflush() -> void:
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
	player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_DEFERRED
	player.play("m")
	player.advance(1.0)
	var pf_before := Engine.get_process_frames()
	var ph_before := Engine.get_physics_frames()
	var a1 := target.calls.duplicate()
	await physics_frame
	var pf_after := Engine.get_process_frames()
	var ph_after := Engine.get_physics_frames()
	var b1 := target.calls.duplicate()
	print("PASS r93c_probe physflush after_adv=", _ps(a1), " after_phys=", _ps(b1),
		" proc_frames_elapsed=", pf_after - pf_before,
		" phys_frames_elapsed=", ph_after - ph_before,
		" no_process_frame_between=", (pf_after - pf_before) == 0)

class MethodTarget extends Node2D:
	var calls: Array = []
	func notify(v: int) -> void:
		calls.append(v)

# ---------------------------------------------------------------- overshoot
# Cross-check the runtime tween value against the static pure function on the SAME
# curve (the two independently pinned rows) + a direction report.
func _arm_overshoot() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	var t3 := create_tween()
	t3.tween_property(target, "scale:y", 10.0, 1.0).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN_OUT)
	t3.pause()
	t3.custom_step(0.25)
	var back025 := target.scale.y
	t3.custom_step(0.25)
	var back050 := target.scale.y
	var t5t := Node2D.new()
	t5t.name = "T5"
	root.add_child(t5t)
	var t5 := create_tween()
	t5.tween_property(t5t, "position:y", 10.0, 1.0).set_trans(Tween.TRANS_SPRING).set_ease(Tween.EASE_OUT)
	t5.pause()
	t5.custom_step(0.5)
	var spr050 := t5t.position.y
	var t6t := Node2D.new()
	t6t.name = "T6"
	root.add_child(t6t)
	var t6 := create_tween()
	t6.tween_property(t6t, "position:y", 10.0, 1.0).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	t6.pause()
	t6.custom_step(0.25)
	var ela025 := t6t.position.y
	# static pure function, 0 -> 10, same curves
	var s_back_io_025: float = Tween.interpolate_value(0.0, 10.0, 0.25, 1.0, Tween.TRANS_BACK, Tween.EASE_IN_OUT)
	var s_spr_out_050: float = Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_SPRING, Tween.EASE_OUT)
	var s_ela_out_025: float = Tween.interpolate_value(0.0, 10.0, 0.25, 1.0, Tween.TRANS_ELASTIC, Tween.EASE_OUT)
	print("PASS r93c_probe overshoot",
		" runtime_back025=", back025, " runtime_back050=", back050,
		" runtime_spr050=", spr050, " runtime_ela025=", ela025,
		" static_back_io_025=", s_back_io_025,
		" static_spr_out_050=", s_spr_out_050,
		" static_ela_out_025=", s_ela_out_025,
		" back_below_start=", back025 < 1.0,
		" back_is_fractional_delta=", back025,
		" spr_above_end=", spr050 > 10.0,
		" ela_below_end=", ela025 < 10.0,
		" frac_runtime_back=", (back025 - 1.0) / 9.0,
		" frac_static_back=", s_back_io_025 / 10.0,
		" frac_runtime_spr=", spr050 / 10.0,
		" frac_static_spr=", s_spr_out_050 / 10.0,
		" frac_runtime_ela=", ela025 / 10.0,
		" frac_static_ela=", s_ela_out_025 / 10.0)

# ---------------------------------------------------------------- physflush2 (decisive)
# Raise the physics rate so >=2 physics steps run per main-loop iteration. Then a
# physics-frame await resumes at the NEXT physics step of the SAME iteration, with
# ZERO intervening process frames. If the deferred queue is visible at that resume,
# the flush provably happened inside the physics phase (message-queue flush point),
# not on a process frame.
func _arm_physflush2() -> void:
	Engine.physics_ticks_per_second = 600
	Engine.max_physics_steps_per_frame = 8
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
	player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_DEFERRED
	player.play("m")
	# resume at a physics step, queue inside the physics phase, then await the NEXT
	# physics step: at 600 tps >=2 steps land in one iteration, so this stays inside
	# the same iteration => no process step can run in between.
	await physics_frame
	var pf_before := Engine.get_process_frames()
	var ph_before := Engine.get_physics_frames()
	player.advance(1.0)
	var a1 := target.calls.duplicate()
	var pfs: Array = []
	var phs: Array = []
	for i in range(3):
		await physics_frame
		pfs.append(Engine.get_process_frames() - pf_before)
		phs.append(Engine.get_physics_frames() - ph_before)
	var b1 := target.calls.duplicate()
	print("PASS r93c_probe physflush2 after_adv=", _ps(a1), " after_phys=", _ps(b1),
		" proc_frames_elapsed=", _ps(pfs), " phys_frames_elapsed=", _ps(phs),
		" no_process_frame_between=", pfs[0] == 0,
		" phys_tps=", Engine.physics_ticks_per_second,
		" max_phys_steps=", Engine.max_physics_steps_per_frame)
