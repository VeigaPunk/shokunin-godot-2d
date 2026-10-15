extends SceneTree
# r89-boundary bisection probe — why does the r89-scout exact arm's `just_after_flush`
# flip to inex=false under load while a probe that reads is_action_just_pressed early
# does not? Variant selected by --var=v1|v3.
#   v1 = the r89-scout _arm_exact verbatim + one extra marker read at the end
#   v3 = v1 + early is_action_just_pressed reads at the four pre-step poll points
# Launch: godot --headless --path proj --script res://b89_input_v.gd -- --var=v1

var var_ := ""
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--var="):
			var_ = a.substr(6)
	_run.call_deferred()

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R89V %s %s=%s" % [var_, key, value])

func _pass() -> void:
	print("PASS b89_input_v %s %s" % [var_, " ".join(_items)])
	quit()

func _key(shift: bool, pressed: bool) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = KEY_W
	e.physical_keycode = KEY_W
	e.shift_pressed = shift
	e.pressed = pressed
	return e

func _eia(ev: InputEvent, action: String, exact: bool) -> String:
	return "1" if InputMap.event_is_action(ev, action, exact) else "0"

func _early() -> void:
	if var_ == "v3":
		print("R89V %s early_jp=%s,%s" % [var_,
			Input.is_action_just_pressed("r89_w", true),
			Input.is_action_just_pressed("r89_w", false)])

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
	_it("control", "wW_eia_ex=1_actual=%s sW_eia_ex=1_actual=%s" % [
		_eia(w, "r89_w", true), _eia(sw, "r89_sw", true)])
	_it("eia_wW", "ex=%s inex=%s" % [_eia(w, "r89_w", true), _eia(w, "r89_w", false)])
	_it("eia_sW_vs_wW", "ex=%s inex=%s" % [_eia(sw, "r89_w", true), _eia(sw, "r89_w", false)])
	_it("eia_wW_vs_sW", "ex=%s inex=%s" % [_eia(w, "r89_sw", true), _eia(w, "r89_sw", false)])
	_it("eia_sW", "ex=%s inex=%s" % [_eia(sw, "r89_sw", true), _eia(sw, "r89_sw", false)])
	_it("eia_both", "plainW[ex=%s inex=%s] shiftW[ex=%s inex=%s]" % [
		_eia(w, "r89_both", true), _eia(w, "r89_both", false),
		_eia(sw, "r89_both", true), _eia(sw, "r89_both", false)])
	_early()
	Input.parse_input_event(sw.duplicate())
	Input.flush_buffered_events()
	_it("poll_shiftW_on_plainW_binding", "w[ex=%s inex=%s] sw[ex=%s inex=%s]" % [
		Input.is_action_pressed("r89_w", true), Input.is_action_pressed("r89_w", false),
		Input.is_action_pressed("r89_sw", true), Input.is_action_pressed("r89_sw", false)])
	_early()
	Input.parse_input_event(swu.duplicate())
	Input.flush_buffered_events()
	_it("poll_after_shiftW_release", "w[ex=%s inex=%s] sw[ex=%s inex=%s]" % [
		Input.is_action_pressed("r89_w", true), Input.is_action_pressed("r89_w", false),
		Input.is_action_pressed("r89_sw", true), Input.is_action_pressed("r89_sw", false)])
	_early()
	Input.parse_input_event(w.duplicate())
	Input.flush_buffered_events()
	_it("poll_plainW", "w[ex=%s inex=%s] sw[ex=%s inex=%s] both[ex=%s inex=%s]" % [
		Input.is_action_pressed("r89_w", true), Input.is_action_pressed("r89_w", false),
		Input.is_action_pressed("r89_sw", true), Input.is_action_pressed("r89_sw", false),
		Input.is_action_pressed("r89_both", true), Input.is_action_pressed("r89_both", false)])
	_early()
	Input.parse_input_event(wu.duplicate())
	Input.flush_buffered_events()
	_it("poll_plainW_released", "w[ex=%s inex=%s] both[ex=%s inex=%s]" % [
		Input.is_action_pressed("r89_w", true), Input.is_action_pressed("r89_w", false),
		Input.is_action_pressed("r89_both", true), Input.is_action_pressed("r89_both", false)])
	_early()
	Input.parse_input_event(sw.duplicate())
	Input.flush_buffered_events()
	if var_ == "v2":
		print("R89V v2 counters pf=%d ph=%d jp_ex=%s jp_inex=%s pr_inex=%s" % [
			Engine.get_process_frames(), Engine.get_physics_frames(),
			Input.is_action_just_pressed("r89_w", true),
			Input.is_action_just_pressed("r89_w", false),
			Input.is_action_pressed("r89_w", false)])
	if var_ == "v4":
		print("R89V v4 tick pf=%d ph=%d" % [
			Engine.get_process_frames(), Engine.get_physics_frames()])
	_it("just_after_flush", "w_jp[ex=%s inex=%s]" % [
		Input.is_action_just_pressed("r89_w", true), Input.is_action_just_pressed("r89_w", false)])
	Input.parse_input_event(swu.duplicate())
	Input.flush_buffered_events()
	_pass()
