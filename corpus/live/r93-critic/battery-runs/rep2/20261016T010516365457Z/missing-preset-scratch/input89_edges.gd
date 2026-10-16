extends SceneTree
# r89 scout probe — r87 remaining input unknowns (bounded secondary split):
#   `exact`   — InputMap exact_match granularity (mixed exact+inexact bindings)
#   `axisdev` — joypad analog-axis device filter (joys=0 headless, synthetic events)
# Battery launch shape: godot --headless --path <scratch> --script res://input89_edges.gd -- --arm=<name>
# All delivery is synchronous (Input.parse_input_event + Input.flush_buffered_events);
# no await separates a parse from its poll, so no idle/physics interposition can flake a value.
# Prints `R89I <arm> <key>=<value>` diagnostics and one final
# `PASS input89_edges <arm> <key>=<value> ...` line (the authorable signature).

var arm := ""
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R89I %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS input89_edges %s %s" % [arm, " ".join(_items)])
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

func _run() -> void:
	match arm:
		"exact": _arm_exact()
		"axisdev": _arm_axisdev()
		_: _arm_exact()

func _arm_exact() -> void:
	# Bindings: wW = plain W; sW = shift+W; both = both events on one action.
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
	# Control: the binding shape itself must match (else every 0 below is uninformative).
	_it("control", "wW_eia_ex=1_actual=%s sW_eia_ex=1_actual=%s" % [
		_eia(w, "r89_w", true), _eia(sw, "r89_sw", true)])
	_it("eia_wW", "ex=%s inex=%s" % [_eia(w, "r89_w", true), _eia(w, "r89_w", false)])
	_it("eia_sW_vs_wW", "ex=%s inex=%s" % [_eia(sw, "r89_w", true), _eia(sw, "r89_w", false)])
	_it("eia_wW_vs_sW", "ex=%s inex=%s" % [_eia(w, "r89_sw", true), _eia(w, "r89_sw", false)])
	_it("eia_sW", "ex=%s inex=%s" % [_eia(sw, "r89_sw", true), _eia(sw, "r89_sw", false)])
	_it("eia_both", "plainW[ex=%s inex=%s] shiftW[ex=%s inex=%s]" % [
		_eia(w, "r89_both", true), _eia(w, "r89_both", false),
		_eia(sw, "r89_both", true), _eia(sw, "r89_both", false)])
	# Polled read: does exactness change a polled answer, or only the parse-time match?
	Input.parse_input_event(sw.duplicate())
	Input.flush_buffered_events()
	_it("poll_shiftW_on_plainW_binding", "w[ex=%s inex=%s] sw[ex=%s inex=%s]" % [
		Input.is_action_pressed("r89_w", true), Input.is_action_pressed("r89_w", false),
		Input.is_action_pressed("r89_sw", true), Input.is_action_pressed("r89_sw", false)])
	Input.parse_input_event(swu.duplicate())
	Input.flush_buffered_events()
	_it("poll_after_shiftW_release", "w[ex=%s inex=%s] sw[ex=%s inex=%s]" % [
		Input.is_action_pressed("r89_w", true), Input.is_action_pressed("r89_w", false),
		Input.is_action_pressed("r89_sw", true), Input.is_action_pressed("r89_sw", false)])
	Input.parse_input_event(w.duplicate())
	Input.flush_buffered_events()
	_it("poll_plainW", "w[ex=%s inex=%s] sw[ex=%s inex=%s] both[ex=%s inex=%s]" % [
		Input.is_action_pressed("r89_w", true), Input.is_action_pressed("r89_w", false),
		Input.is_action_pressed("r89_sw", true), Input.is_action_pressed("r89_sw", false),
		Input.is_action_pressed("r89_both", true), Input.is_action_pressed("r89_both", false)])
	Input.parse_input_event(wu.duplicate())
	Input.flush_buffered_events()
	_it("poll_plainW_released", "w[ex=%s inex=%s] both[ex=%s inex=%s]" % [
		Input.is_action_pressed("r89_w", true), Input.is_action_pressed("r89_w", false),
		Input.is_action_pressed("r89_both", true), Input.is_action_pressed("r89_both", false)])
	# Just-pressed reads are frame-scoped; sample them inside the same flush window.
	Input.parse_input_event(sw.duplicate())
	Input.flush_buffered_events()
	_it("just_after_flush", "w_jp[ex=%s inex=%s]" % [
		Input.is_action_just_pressed("r89_w", true), Input.is_action_just_pressed("r89_w", false)])
	Input.parse_input_event(swu.duplicate())
	Input.flush_buffered_events()
	_pass()

func _joymotion(device: int, value: float) -> InputEventJoypadMotion:
	var e := InputEventJoypadMotion.new()
	e.device = device
	e.axis = 0
	e.axis_value = value
	return e

func _arm_axisdev() -> void:
	InputMap.add_action("r89_ax0")
	InputMap.add_action("r89_axany")
	InputMap.action_add_event("r89_ax0", _joymotion(0, 1.0))
	InputMap.action_add_event("r89_axany", _joymotion(-1, 1.0))
	_it("census", "joys=%d eia_avail=%s dz_ax0=%.4f dz_ui_accept=%.4f" % [Input.get_connected_joypads().size(), InputMap.has_method("event_is_action"), InputMap.action_get_deadzone("r89_ax0"), InputMap.action_get_deadzone("ui_accept")])
	for dev in [0, 5, -1]:
		var e := _joymotion(dev, 1.0)
		_it("eia_dev%d" % dev, "ax0[ex=%s inex=%s] axany[ex=%s inex=%s]" % [
			_eia(e, "r89_ax0", true), _eia(e, "r89_ax0", false),
			_eia(e, "r89_axany", true), _eia(e, "r89_axany", false)])
	Input.parse_input_event(_joymotion(5, 1.0))
	Input.flush_buffered_events()
	_it("poll_dev5", "ax0=%s axany=%s axis5=%.4f axis0=%.4f strength0=%.4f" % [
		Input.is_action_pressed("r89_ax0"), Input.is_action_pressed("r89_axany"),
		Input.get_joy_axis(5, 0), Input.get_joy_axis(0, 0), Input.get_action_strength("r89_ax0")])
	Input.parse_input_event(_joymotion(0, 1.0))
	Input.flush_buffered_events()
	_it("poll_dev0", "ax0=%s axany=%s axis0=%.4f strength0=%.4f raw0=%.4f" % [
		Input.is_action_pressed("r89_ax0"), Input.is_action_pressed("r89_axany"),
		Input.get_joy_axis(0, 0), Input.get_action_strength("r89_ax0"), Input.get_action_raw_strength("r89_ax0")])
	Input.parse_input_event(_joymotion(0, 0.6))
	Input.flush_buffered_events()
	_it("poll_dev0_06", "ax0=%s axis0=%.4f strength0=%.4f raw0=%.4f" % [
		Input.is_action_pressed("r89_ax0"), Input.get_joy_axis(0, 0),
		Input.get_action_strength("r89_ax0"), Input.get_action_raw_strength("r89_ax0")])
	Input.parse_input_event(_joymotion(0, -1.0))
	Input.flush_buffered_events()
	_it("poll_dev0_neg", "ax0=%s axany=%s axis0=%.4f" % [
		Input.is_action_pressed("r89_ax0"), Input.is_action_pressed("r89_axany"), Input.get_joy_axis(0, 0)])
	Input.parse_input_event(_joymotion(0, 0.0))
	Input.flush_buffered_events()
	_it("poll_release", "ax0=%s axany=%s axis0=%.4f" % [
		Input.is_action_pressed("r89_ax0"), Input.is_action_pressed("r89_axany"), Input.get_joy_axis(0, 0)])
	_pass()
