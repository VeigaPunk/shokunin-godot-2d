extends SceneTree
# r89-boundary diagnostic — why does input89_edges `just_after_flush` flip under CPU load?
# Replicates the r89-scout exact arm verbatim, then prints frame counters and the four
# just-pressed / pressed reads at the just_after_flush point. No writes, no state mutation.
# Launch: godot --headless --path proj --script res://b89_input_diag.gd -- --arm=diag

var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _d(key: String, value: String) -> void:
	print("R89D %s %s=%s" % [arm, key, value])

func _key(shift: bool, pressed: bool) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = KEY_W
	e.physical_keycode = KEY_W
	e.shift_pressed = shift
	e.pressed = pressed
	return e

func _probe(tag: String) -> void:
	var pf := Engine.get_process_frames()
	var ph := Engine.get_physics_frames()
	_d(tag, "pf=%d ph=%d jp_ex=%s jp_inex=%s pr_ex=%s pr_inex=%s" % [
		pf, ph,
		Input.is_action_just_pressed("r89_w", true), Input.is_action_just_pressed("r89_w", false),
		Input.is_action_pressed("r89_w", true), Input.is_action_pressed("r89_w", false)])

func _run() -> void:
	InputMap.add_action("r89_w")
	InputMap.add_action("r89_sw")
	InputMap.add_action("r89_both")
	var w := _key(false, true)
	var sw := _key(true, true)
	var wu := _key(false, false)
	var swu := _key(true, false)
	InputMap.action_add_event("r89_w", w)
	InputMap.action_add_event("r89_sw", sw)
	InputMap.action_add_event("r89_both", w)
	InputMap.action_add_event("r89_both", sw)
	_probe("boot")
	Input.parse_input_event(sw.duplicate())
	Input.flush_buffered_events()
	_probe("s1_shiftW")
	Input.parse_input_event(swu.duplicate())
	Input.flush_buffered_events()
	_probe("s2_release")
	Input.parse_input_event(w.duplicate())
	Input.flush_buffered_events()
	_probe("s3_plainW")
	Input.parse_input_event(wu.duplicate())
	Input.flush_buffered_events()
	_probe("s4_release")
	Input.parse_input_event(sw.duplicate())
	Input.flush_buffered_events()
	_probe("s5_shiftW_again")
	Input.parse_input_event(swu.duplicate())
	Input.flush_buffered_events()
	_probe("s6_release")
	print("PASS b89_input_diag %s done=1" % arm)
	quit()
