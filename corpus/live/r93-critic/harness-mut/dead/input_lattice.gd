extends SceneTree
# r83-scout scratch probe — input action + event lattice (headless Godot 4 2D).
# One arm per process, exactly the battery's launch shape:
#   godot --headless --path <scratch> --script res://input_lattice.gd -- --arm=<name>
# Prints one final `PASS input_lattice <arm> ...` line.
#
# Byte-stability discipline: proc_no counts process_frame emissions, phys_no
# counts physics_frame emissions. Absolute counters are wall-clock dependent
# headless, so every printed tick index is a DELTA from an arm-set mark
# (flags.ph0/pr0) — structural quantities only.

var arm := ""
var phys_no := 0
var proc_no := 0
var seq := 0
var inlog: Array = []          # event receipt dicts
var ticks: Array = []          # {k:"ph"|"pr"|"EV", d:int, tag:String, st:String}
var watch: Array = []          # actions polled in sink ticks + in-cb state
var ev_watch := false
var rec_ph := -1               # physics ticks to record (-1 = off)
var rec_pr := -1               # process ticks to record (-1 = off)
var flags := {}

class Sink extends Node:
	var hub
	var tag := "s0"
	func _ready() -> void:
		set_process_input(true)
		set_process_unhandled_input(true)
		set_process_unhandled_key_input(true)
		set_process_shortcut_input(true)
	func _input(e: InputEvent) -> void:
		hub._ev("in", tag, e)
	func _unhandled_input(e: InputEvent) -> void:
		hub._ev("uh", tag, e)
	func _unhandled_key_input(e: InputEvent) -> void:
		hub._ev("uk", tag, e)
	func _shortcut_input(e: InputEvent) -> void:
		hub._ev("sc", tag, e)
	func _physics_process(_d: float) -> void:
		hub._tick("ph", tag)
	func _process(_d: float) -> void:
		hub._tick("pr", tag)

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _fail(reason: String) -> void:
	print("FAIL input_lattice %s reason=%s" % [arm, reason])
	quit(1)

func _finish(line: String) -> void:
	print("PASS input_lattice " + line)
	quit(0)

func _mk_sink(tag: String) -> Sink:
	var s := Sink.new()
	s.hub = self
	s.tag = tag
	s.name = "Sink_" + tag
	root.add_child(s)
	return s

func _tick(w: String, tag: String) -> void:
	var d: int
	if w == "ph":
		d = phys_no - int(flags.get("ph0", 0))
		if flags.has("on_ph_step") and int(flags["ph_step"]) == phys_no:
			var cb: Callable = flags["on_ph_step"]
			flags.erase("on_ph_step")
			cb.call(tag)
	else:
		d = proc_no - int(flags.get("pr0", 0))
	if (w == "ph" and rec_ph > 0) or (w == "pr" and rec_pr > 0):
		if w == "ph":
			rec_ph -= 1
		else:
			rec_pr -= 1
		ticks.append({"k": w, "d": d, "tag": tag, "st": _states()})

func _states() -> String:
	var out: Array = []
	for a in watch:
		if not InputMap.has_action(a):
			out.append("%s=<gone>" % a)
			continue
		out.append("%s=%d/%.2f/%d/%d" % [a,
			int(Input.is_action_pressed(a)),
			Input.get_action_strength(a),
			int(Input.is_action_just_pressed(a)),
			int(Input.is_action_just_released(a))])
	return ";".join(out)

func _ev(via: String, tag: String, e: InputEvent) -> void:
	seq += 1
	var rec := {"seq": seq, "via": via, "tag": tag, "pr": proc_no, "ph": phys_no,
		"desc": _edesc(e)}
	if ev_watch:
		var m := {}
		var ist := {}
		for a in watch:
			if InputMap.has_action(a):
				m[str(a)] = "%d/%d" % [int(e.is_action_pressed(a)),
					int(e.is_action_released(a))]
				ist[str(a)] = "%d/%d/%d" % [int(Input.is_action_pressed(a)),
					int(Input.is_action_just_pressed(a)),
					int(Input.is_action_just_released(a))]
			else:
				m[str(a)] = "gone"
				ist[str(a)] = "gone"
		rec["m"] = m
		rec["ist"] = ist
		rec["echo"] = int(e.get("echo") == true)
	inlog.append(rec)
	ticks.append({"k": "EV", "seq": seq, "d": phys_no - int(flags.get("ph0", 0)),
		"prd": proc_no - int(flags.get("pr0", 0))})
	if flags.has("on_event"):
		flags["on_event"].call(e, via, tag)

func _edesc(e: InputEvent) -> String:
	if e is InputEventAction:
		return "A(%s,p=%d,s=%.2f,d=%d,ai=%s,ei=%s)" % [
			e.action, int(e.pressed), e.strength, e.device,
			str(e.get("action_index")), str(e.get("event_index"))]
	if e is InputEventKey:
		return "K(kc=%d,ph=%d,pr=%d,echo=%d,dev=%d,u=%d,sh=%d)" % [
			e.keycode, e.physical_keycode, int(e.pressed), int(e.echo), e.device,
			e.unicode, int(e.shift_pressed)]
	if e is InputEventJoypadMotion:
		return "JM(ax=%d,v=%.3f,dev=%d)" % [e.axis, e.axis_value, e.device]
	if e is InputEventJoypadButton:
		return "JB(b=%d,p=%d,dev=%d)" % [e.button_index, int(e.pressed), e.device]
	if e is InputEventMouseButton:
		return "MB(b=%d,p=%d,pos=(%.0f,%.0f))" % [e.button_index, int(e.pressed),
			e.position.x, e.position.y]
	if e is InputEventMouseMotion:
		return "MM(pos=(%.0f,%.0f),rel=(%.0f,%.0f))" % [e.position.x, e.position.y,
			e.relative.x, e.relative.y]
	return e.get_class()

# Receipt formatter: proc delta vs flags.base set right before the parse.
# Phys delta is printed only when structural (mask_ph for physics-window parses).
func _fmt_recv(mask_ph: bool = false) -> String:
	var b: Dictionary = flags.get("base", {"pr": 0, "ph": 0})
	var parts: Array = []
	for r in inlog:
		var s := "%d:%s%s@pr+%d" % [r.seq, r.via, r.tag, r.pr - int(b.pr)]
		s += ("/ph~" if mask_ph else "/ph+%d" % [r.ph - int(b.ph)])
		s += ":" + r.desc
		if r.has("m"):
			var mm: Array = []
			for a in r.m:
				mm.append("%s:%s|I%s" % [a, r.m[a], r.ist[a]])
			s += " m[%s] echo%d" % [",".join(mm), r.echo]
		parts.append(s)
	return "[" + " ".join(parts) + "]"

func _mark() -> void:
	flags["base"] = {"pr": proc_no, "ph": phys_no}
	flags["ph0"] = phys_no
	flags["pr0"] = proc_no

func _fmt_ticks_rel_ev() -> String:
	# ph/pr ticks renumbered by order AFTER the first EV marker; the last tick
	# before the EV is reported as pre{.}. Positions are structural.
	var ev_at := -1
	for i in ticks.size():
		if ticks[i].k == "EV":
			ev_at = i
			break
	if ev_at < 0:
		return "none"
	var pre := ""
	var post_ph: Array = []
	var post_pr: Array = []
	for i in range(ev_at + 1, ticks.size()):
		var t: Dictionary = ticks[i]
		if t.k == "EV":
			continue
		if t.k == "ph" and post_ph.size() < 3:
			post_ph.append("ph+%d{%s}" % [post_ph.size(), t.st])
		elif t.k == "pr" and post_pr.size() < 3:
			post_pr.append("pr+%d{%s}" % [post_pr.size(), t.st])
	for i in range(ev_at - 1, -1, -1):
		if ticks[i].k in ["ph", "pr"]:
			pre = "%s{%s}" % [ticks[i].k, ticks[i].st]
			break
	return "pre=%s post_ph=[%s] post_pr=[%s]" % [pre, " ".join(post_ph), " ".join(post_pr)]

func _act(name: StringName, pressed: bool, strength: float = 1.0, device: int = -1) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = name
	e.pressed = pressed
	e.strength = strength
	e.device = device
	return e

func _key(kc: int, pressed: bool = true, echo: bool = false, phys: int = 0, shift: bool = false) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = kc
	e.physical_keycode = phys
	e.pressed = pressed
	e.echo = echo
	e.shift_pressed = shift
	return e

func _bind(name: StringName, ev: InputEvent, deadzone: float = -1.0) -> void:
	if not InputMap.has_action(name):
		InputMap.add_action(name)
	if deadzone >= 0.0:
		InputMap.action_set_deadzone(name, deadzone)
	InputMap.action_add_event(name, ev)

func _pr_frames(n: int) -> void:
	for i in n:
		await process_frame

func _ph_frames(n: int) -> void:
	for i in n:
		await physics_frame

func _st(a: StringName) -> String:
	return "%d/%.2f/%d/%d" % [int(Input.is_action_pressed(a)), Input.get_action_strength(a),
		int(Input.is_action_just_pressed(a)), int(Input.is_action_just_released(a))]

# Pressed-action enumeration (Input.get_pressed_actions does not exist on 4.7).
func _pl() -> String:
	var names: Array = []
	for a in InputMap.get_actions():
		if Input.is_action_pressed(a):
			names.append(str(a))
	names.sort()
	return str(names)

func _run() -> void:
	physics_frame.connect(func() -> void: phys_no += 1)
	process_frame.connect(func() -> void: proc_no += 1)
	print("R83 arm=%s godot=%s acc=%s tps=%s" % [
		arm, Engine.get_version_info().string, Input.use_accumulated_input,
		ProjectSettings.get_setting("physics/common/physics_ticks_per_second")])
	match arm:
		"census": await _arm_census()
		"press_idle": await _arm_press_idle()
		"press_phys": await _arm_press_phys()
		"acc_off": await _arm_acc_off()
		"acc_flush": await _arm_acc_flush()
		"pre_frame": await _arm_pre_frame()
		"api_press": await _arm_api_press()
		"burst": await _arm_burst()
		"release_edge": await _arm_release_edge()
		"dz_ladder": await _arm_dz_ladder()
		"joy_axis": await _arm_joy_axis()
		"echo_edge": await _arm_echo_edge()
		"key_map": await _arm_key_map()
		"imap_erase": await _arm_imap_erase()
		"imap_mid_cb": await _arm_imap_mid_cb()
		"ui_ns": await _arm_ui_ns()
		"conflict": await _arm_conflict()
		"dev_joy": await _arm_dev_joy()
		"mouse_hdls": await _arm_mouse_hdls()
		"null_edge": await _arm_null_edge()
		"dispatch_order": await _arm_dispatch_order()
		"reentrant": await _arm_reentrant()
		"phys_peer": await _arm_phys_peer()
		_: _fail("unknown_arm")

# ------------------------------------------------------------------- arms ---

func _arm_census() -> void:
	var in_methods: Array = []
	for m in Input.get_method_list():
		in_methods.append(str(m.name))
	in_methods.sort()
	var pick_in: Array = in_methods.filter(func(n: String) -> bool: return n.contains("action") or n.contains("pressed") or n.contains("parse") or n.contains("flush") or n.contains("accumul") or n.contains("mouse") or n.contains("joy") or n.contains("key") or n.contains("event") or n.contains("echo") or n.contains("strength") or n.contains("any"))
	var im_methods: Array = []
	for m in InputMap.get_method_list():
		im_methods.append(str(m.name))
	im_methods.sort()
	var ea := InputEventAction.new()
	var ea_props: Array = []
	for p in ea.get_property_list():
		if p.name in ["device", "action", "pressed", "strength", "event_index",
				"action_index"]:
			ea_props.append(str(p.name))
	var ek := InputEventKey.new()
	var ek_props: Array = []
	for p in ek.get_property_list():
		if p.name in ["pressed", "keycode", "physical_keycode", "key_label",
				"unicode", "echo", "location", "device", "shift_pressed",
				"ctrl_pressed", "alt_pressed", "meta_pressed",
				"command_or_control_autoremap", "window_id"]:
			ek_props.append(str(p.name))
	var builtins: Array = []
	for a in InputMap.get_actions():
		var s := str(a)
		if s.begins_with("ui_"):
			builtins.append(s)
	builtins.sort()
	var ua_events: Array = []
	for ev in InputMap.action_get_events(&"ui_accept"):
		if ev is InputEventKey:
			ua_events.append("K%d" % ev.keycode)
		else:
			ua_events.append(ev.get_class())
	var ps_acc: Variant = ProjectSettings.get_setting("input_devices/buffering/use_accumulated_input", "<missing>")
	var ps_agile: Variant = ProjectSettings.get_setting("input_devices/buffering/agile_event_flushing", "<missing>")
	Input.use_accumulated_input = false
	var acc_write: Variant = Input.use_accumulated_input
	Input.use_accumulated_input = true
	var eng := "%d/%d" % [Engine.get_process_frames(), Engine.get_physics_frames()]
	var s := _mk_sink("s0")
	await _pr_frames(2)
	_finish("census imap=[%s] input=[%s] evact=[%s] evkey=[%s] ui_builtins=[%s] ui_accept_ev=[%s] dz_ui=%.2f ps_acc=%s ps_agile=%s acc_wback=%s eng=%s joys=%d sink=%s" % [
		",".join(im_methods), ",".join(pick_in), ",".join(ea_props),
		",".join(ek_props), ",".join(builtins), ",".join(ua_events),
		InputMap.action_get_deadzone(&"ui_accept"),
		str(ps_acc), str(ps_agile), str(acc_write), eng,
		Input.get_connected_joypads().size(), str(is_instance_valid(s))])

func _arm_press_idle() -> void:
	_mk_sink("s0")
	InputMap.add_action(&"pi")
	watch = [&"pi"]
	ev_watch = true
	await _pr_frames(2)
	_mark()
	Input.parse_input_event(_act(&"pi", true))
	var imm := _st(&"pi")
	var pl := _pl()
	rec_ph = 6
	rec_pr = 4
	await _ph_frames(4)
	_finish("press_idle imm[%s] pl=%s recv=%s ticks=%s" % [
		imm, pl, _fmt_recv(), _fmt_ticks_rel_ev()])

func _arm_press_phys() -> void:
	# Parse inside a physics_frame signal resume (physics phase). ph deltas in
	# receipts are timing-dependent there -> masked; only pr deltas are pinned.
	_mk_sink("s0")
	InputMap.add_action(&"pp")
	watch = [&"pp"]
	ev_watch = true
	await _ph_frames(1)
	_mark()
	Input.parse_input_event(_act(&"pp", true))
	var imm := _st(&"pp")
	rec_ph = 8
	rec_pr = 3
	await _pr_frames(10)
	_finish("press_phys imm[%s] recv=%s ticks=%s" % [
		imm, _fmt_recv(true), _fmt_ticks_rel_ev()])

func _arm_acc_off() -> void:
	var s := _mk_sink("s0")
	InputMap.add_action(&"ao")
	watch = [&"ao"]
	ev_watch = true
	await _pr_frames(2)
	Input.use_accumulated_input = false
	var rb := Input.use_accumulated_input
	_mark()
	Input.parse_input_event(_act(&"ao", true))
	var inline_len := inlog.size()
	var imm := _st(&"ao")
	rec_ph = 3
	rec_pr = 2
	await _ph_frames(3)
	s.queue_free()
	_finish("acc_off acc=%s inline_receipts=%d imm[%s] recv=%s ticks=%s" % [
		str(rb), inline_len, imm, _fmt_recv(), _fmt_ticks_rel_ev()])

func _arm_acc_flush() -> void:
	var s := _mk_sink("s0")
	InputMap.add_action(&"af")
	watch = [&"af"]
	ev_watch = true
	await _pr_frames(2)
	_mark()
	Input.parse_input_event(_act(&"af", true))
	var mid := _st(&"af")
	var mid_len := inlog.size()
	Input.flush_buffered_events()
	var post := _st(&"af")
	var post_len := inlog.size()
	await _pr_frames(2)
	s.queue_free()
	_finish("acc_flush mid[%s] mid_len=%d post[%s] post_len=%d recv=%s" % [
		mid, mid_len, post, post_len, _fmt_recv()])

func _arm_pre_frame() -> void:
	# Parse before the first frame await and before the sink exists.
	InputMap.add_action(&"pf0")
	_mark()
	Input.parse_input_event(_act(&"pf0", true))
	var imm0 := _st(&"pf0")
	_mk_sink("s0")
	watch = [&"pf0"]
	ev_watch = true
	rec_ph = 4
	rec_pr = 3
	await _pr_frames(3)
	_finish("pre_frame imm0[%s] recv=%s ticks=%s" % [
		imm0, _fmt_recv(true), _fmt_ticks_rel_ev()])

func _arm_api_press() -> void:
	# API presses apply state immediately and dispatch no event.  Windows are
	# bounded by matching awaits so every index is structural.
	_mk_sink("s0")
	InputMap.add_action(&"ap")
	watch = [&"ap"]
	ev_watch = true
	# process-window ladder
	await _pr_frames(2)
	_mark()
	Input.action_press(&"ap", 0.7)
	var imm := _st(&"ap")
	var raw := Input.get_action_raw_strength(&"ap")
	var pl := _pl()
	rec_pr = 3
	await _pr_frames(2)
	Input.action_release(&"ap")
	rec_pr = 2
	await _pr_frames(1)
	var pr_seq := str(ticks.filter(func(t): return t.k == "pr").map(func(t): return "pr%d{%s}" % [t.d, t.st]))
	ticks.clear()
	# physics-window ladder: press during process resume, step with physics
	flags["ph0"] = phys_no
	Input.action_press(&"ap", 0.7)
	rec_ph = 6
	await _ph_frames(2)
	Input.action_release(&"ap")
	await _ph_frames(2)
	var ph_seq := str(ticks.filter(func(t): return t.k == "ph").map(func(t): return "ph%d{%s}" % [t.d, t.st]))
	_finish("api_press imm[%s] raw=%.2f pl=%s recv=%s pr=%s ph=%s" % [
		imm, raw, pl, _fmt_recv(), pr_seq, ph_seq])

func _arm_burst() -> void:
	var s := _mk_sink("s0")
	InputMap.add_action(&"bu")
	watch = [&"bu"]
	ev_watch = true
	await _pr_frames(2)
	_mark()
	Input.parse_input_event(_act(&"bu", true))
	Input.parse_input_event(_act(&"bu", false))
	var imm := _st(&"bu")
	rec_ph = 4
	rec_pr = 3
	await _ph_frames(4)
	s.queue_free()
	_finish("burst imm[%s] recv=%s ticks=%s" % [
		imm, _fmt_recv(), _fmt_ticks_rel_ev()])

func _arm_release_edge() -> void:
	var s := _mk_sink("s0")
	InputMap.add_action(&"re")
	watch = [&"re"]
	ev_watch = true
	await _pr_frames(2)
	_mark()
	Input.parse_input_event(_act(&"re", true))
	await _pr_frames(2)
	ticks.clear()
	flags["ph0"] = phys_no
	flags["pr0"] = proc_no
	Input.parse_input_event(_act(&"re", false))
	var imm := _st(&"re")
	rec_ph = 4
	rec_pr = 3
	await _ph_frames(4)
	s.queue_free()
	_finish("release_edge imm[%s] recv=%s ticks=%s" % [
		imm, _fmt_recv(true), _fmt_ticks_rel_ev()])

func _arm_dz_ladder() -> void:
	_mk_sink("s0")
	_bind(&"dz50", _key(KEY_F1), 0.5)
	_bind(&"dz20", _key(KEY_F2), 0.2)
	var vals := [0.0, 0.3, 0.49, 0.5, 0.51, 0.7, 1.0]
	var rows: Array = []
	var rows20: Array = []
	for v in vals:
		Input.parse_input_event(_act(&"dz50", true, v))
		await _pr_frames(2)
		rows.append("s%.2f[%s]" % [v, _st(&"dz50")])
		Input.parse_input_event(_act(&"dz50", false))
		await _pr_frames(2)
	for v in vals:
		Input.parse_input_event(_act(&"dz20", true, v))
		await _pr_frames(2)
		rows20.append("s%.2f[%s]" % [v, _st(&"dz20")])
		Input.parse_input_event(_act(&"dz20", false))
		await _pr_frames(2)
	var api_rows: Array = []
	for v in vals:
		Input.action_press(&"dz50", v)
		api_rows.append("s%.2f[%s|raw %.2f]" % [v, _st(&"dz50"),
			Input.get_action_raw_strength(&"dz50")])
		Input.action_release(&"dz50")
		await _pr_frames(1)
	_finish("dz_ladder dz50=[%s] dz20=[%s] api50=[%s]" % [
		" ".join(rows), " ".join(rows20), " ".join(api_rows)])

func _arm_joy_axis() -> void:
	_mk_sink("s0")
	var jp := InputEventJoypadMotion.new()
	jp.axis = JOY_AXIS_LEFT_X
	jp.axis_value = 1.0
	_bind(&"jxp", jp, 0.5)
	var jn := InputEventJoypadMotion.new()
	jn.axis = JOY_AXIS_LEFT_X
	jn.axis_value = -1.0
	_bind(&"jxn", jn, 0.2)
	watch = [&"jxp", &"jxn"]
	var vals := [0.0, 0.2, 0.21, 0.49, 0.5, 0.51, 0.7, 1.0, -0.2, -0.21, -0.7]
	var rows: Array = []
	for v in vals:
		var e := InputEventJoypadMotion.new()
		e.axis = JOY_AXIS_LEFT_X
		e.axis_value = v
		e.device = 0
		Input.parse_input_event(e)
		await _pr_frames(2)
		rows.append("v%.2f[%s|%s|raw %.2f/%.2f]" % [v, _st(&"jxp"), _st(&"jxn"),
			Input.get_action_raw_strength(&"jxp"), Input.get_action_raw_strength(&"jxn")])
	_finish("joy_axis %s" % [" ".join(rows)])

func _arm_echo_edge() -> void:
	var s := _mk_sink("s0")
	_bind(&"ek", _key(KEY_E))
	watch = [&"ek"]
	ev_watch = true
	await _pr_frames(2)
	_mark()
	Input.parse_input_event(_key(KEY_E, true))
	await _pr_frames(2)
	Input.parse_input_event(_key(KEY_E, true, true))   # echo repeat
	await _pr_frames(2)
	var after_echo := _st(&"ek")
	Input.parse_input_event(_key(KEY_E, false))
	await _pr_frames(2)
	_bind(&"ek2", _key(KEY_R))
	Input.parse_input_event(_key(KEY_R, true, true))   # echo as FIRST event
	await _pr_frames(2)
	var first_echo := _st(&"ek2")
	s.queue_free()
	_finish("echo_edge after_echo[%s] first_echo[%s] recv=%s" % [
		after_echo, first_echo, _fmt_recv(true)])

func _arm_key_map() -> void:
	var s := _mk_sink("s0")
	_bind(&"ka", _key(KEY_Q))                          # keycode-Q binding
	_bind(&"kp", _key(0, true, false, KEY_W))          # physical-W binding
	watch = [&"ka", &"kp"]
	ev_watch = true
	await _pr_frames(2)
	_mark()
	Input.parse_input_event(_key(KEY_Q, true))
	await _pr_frames(2)
	var after_q := "%s|%s keyq=%d phq=%d phw=%d" % [_st(&"ka"), _st(&"kp"),
		int(Input.is_key_pressed(KEY_Q)), int(Input.is_physical_key_pressed(KEY_Q)),
		int(Input.is_physical_key_pressed(KEY_W))]
	# event carrying keycode=Q AND physical=W: which bindings fire?
	Input.parse_input_event(_key(KEY_Q, true, false, KEY_W))
	await _pr_frames(2)
	var after_qw := "%s|%s phw=%d" % [_st(&"ka"), _st(&"kp"),
		int(Input.is_physical_key_pressed(KEY_W))]
	Input.parse_input_event(_key(KEY_Q, false))
	var r2 := InputEventKey.new()
	r2.physical_keycode = KEY_W
	r2.pressed = false
	Input.parse_input_event(r2)
	await _pr_frames(2)
	var tail := "%s|%s" % [_st(&"ka"), _st(&"kp")]
	s.queue_free()
	_finish("key_map after_q[%s] after_qphysw[%s] tail[%s] recv=%s" % [
		after_q, after_qw, tail, _fmt_recv(true)])

func _arm_imap_erase() -> void:
	var s := _mk_sink("s0")
	_bind(&"er", _key(KEY_Z))
	await _pr_frames(2)
	Input.parse_input_event(_key(KEY_Z, true))
	await _pr_frames(2)
	var while_pressed := _st(&"er")
	var pl1 := _pl()
	InputMap.erase_action(&"er")
	var has_after := InputMap.has_action(&"er")
	var pl2 := _pl()
	InputMap.add_action(&"er")
	var readd := "%s" % InputMap.has_action(&"er")
	var pl3 := _pl()
	InputMap.action_add_event(&"er", _key(KEY_Z))
	var len_mid := inlog.size()
	Input.parse_input_event(_key(KEY_Z, true))
	InputMap.erase_action(&"er")
	await _pr_frames(2)
	var recv_after := inlog.size() - len_mid
	s.queue_free()
	_finish("imap_erase while[%s] pl1=%s has=%s pl2=%s readd=%s pl3=%s buf_erase_recv=%d recv=%s" % [
		while_pressed, pl1, str(has_after), pl2, readd, pl3, recv_after,
		str(inlog.map(func(r): return r.desc))])

func _arm_imap_mid_cb() -> void:
	_bind(&"cb_a", _key(KEY_F5))
	_bind(&"cb_b", _key(KEY_F6))
	_mk_sink("s0")
	# During delivery of the F5 event, erase cb_b — a real mid-dispatch
	# InputMap mutation; the already-buffered F6 event is flushed after it.
	flags["on_event"] = func(e: InputEvent, _via: String, _tag: String) -> void:
		if e is InputEventKey and e.keycode == KEY_F5 and e.pressed \
				and InputMap.has_action(&"cb_b"):
			InputMap.erase_action(&"cb_b")
			flags["erased_in_cb"] = true
	await _pr_frames(2)
	Input.parse_input_event(_key(KEY_F5, true))
	Input.parse_input_event(_key(KEY_F6, true))
	await _pr_frames(2)
	var b_has := InputMap.has_action(&"cb_b")
	var pl := _pl()
	if not InputMap.has_action(&"cb_b"):
		InputMap.add_action(&"cb_b")
	InputMap.action_add_event(&"cb_b", _key(KEY_F6))
	Input.parse_input_event(_key(KEY_F6, true))
	await _pr_frames(2)
	var b2 := "%s" % [_st(&"cb_b")]
	_finish("imap_mid_cb erased_in_cb=%s b_has=%s pl=%s b_rearmed[%s] recv=%s" % [
		str(flags.get("erased_in_cb", false)), str(b_has), pl, b2,
		str(inlog.map(func(r): return "%s%s:%s" % [r.via, r.tag, r.desc]))])

func _arm_ui_ns() -> void:
	_mk_sink("s0")
	watch = [&"ui_accept", &"cx"]
	ev_watch = true
	_bind(&"cx", _key(KEY_ENTER))
	var ua_n := InputMap.action_get_events(&"ui_accept").size()
	await _pr_frames(2)
	_mark()
	Input.parse_input_event(_key(KEY_ENTER, true))
	await _pr_frames(2)
	var during := "%s|%s" % [_st(&"ui_accept"), _st(&"cx")]
	var pl := _pl()
	InputMap.erase_action(&"ui_accept")
	var has_ua := InputMap.has_action(&"ui_accept")
	Input.parse_input_event(_key(KEY_ENTER, false))
	await _pr_frames(2)
	var after_erase := "%s" % [_st(&"cx")]
	_finish("ui_ns ua_ev=%d during[%s] pl=%s ua_has_after=%s cx_after[%s] recv=%s" % [
		ua_n, during, pl, str(has_ua), after_erase, _fmt_recv()])

func _arm_conflict() -> void:
	var s := _mk_sink("s0")
	_bind(&"ck_a", _key(KEY_Q))
	_bind(&"ck_b", _key(KEY_Q))
	_bind(&"ck_s", _key(KEY_W, true, false, 0, true))   # shift-W binding
	watch = [&"ck_a", &"ck_b", &"ck_s"]
	ev_watch = true
	await _pr_frames(2)
	_mark()
	Input.parse_input_event(_key(KEY_Q, true))
	await _pr_frames(2)
	var both := "%s|%s pl=%s" % [_st(&"ck_a"), _st(&"ck_b"), _pl()]
	Input.parse_input_event(_key(KEY_W, true, false, 0, true))
	await _pr_frames(2)
	var ex := "ck_s[%s] a_exact=%d a_plain=%d s_exact=%d" % [_st(&"ck_s"),
		int(Input.is_action_pressed(&"ck_a", true)), int(Input.is_action_pressed(&"ck_a", false)),
		int(Input.is_action_pressed(&"ck_s", true))]
	s.queue_free()
	_finish("conflict both[%s] exact[%s] recv=%s" % [
		both, ex, _fmt_recv(true)])

func _arm_dev_joy() -> void:
	var s := _mk_sink("s0")
	var jb := InputEventJoypadButton.new()
	jb.button_index = JOY_BUTTON_A
	_bind(&"jb", jb)
	watch = [&"jb"]
	ev_watch = true
	await _pr_frames(2)
	_mark()
	var cells: Array = []
	for dev in [0, 5, -1]:
		var e := InputEventJoypadButton.new()
		e.button_index = JOY_BUTTON_A
		e.pressed = true
		e.device = dev
		Input.parse_input_event(e)
		await _pr_frames(2)
		cells.append("d%d[%s] j0=%d j5=%d" % [dev, _st(&"jb"),
			int(Input.is_joy_button_pressed(0, JOY_BUTTON_A)),
			int(Input.is_joy_button_pressed(5, JOY_BUTTON_A))])
		var rel := InputEventJoypadButton.new()
		rel.button_index = JOY_BUTTON_A
		rel.pressed = false
		rel.device = dev
		Input.parse_input_event(rel)
		await _pr_frames(1)
	s.queue_free()
	_finish("dev_joy joys=%d %s recv=%s" % [
		Input.get_connected_joypads().size(), " ".join(cells), _fmt_recv(true)])

func _arm_mouse_hdls() -> void:
	var s := _mk_sink("s0")
	InputMap.add_action(&"mh")
	watch = [&"mh"]
	ev_watch = true
	await _pr_frames(2)
	_mark()
	var mb := InputEventMouseButton.new()
	mb.button_index = MOUSE_BUTTON_LEFT
	mb.pressed = true
	mb.position = Vector2(7, 9)
	Input.parse_input_event(mb)
	await _pr_frames(2)
	var st := "ml=%d pos=(%.0f,%.0f)" % [int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)),
		root.get_mouse_position().x, root.get_mouse_position().y]
	var mm := InputEventMouseMotion.new()
	mm.position = Vector2(30, 40)
	mm.relative = Vector2(23, 31)
	Input.parse_input_event(mm)
	await _pr_frames(2)
	var pos := "pos2=(%.0f,%.0f)" % [root.get_mouse_position().x, root.get_mouse_position().y]
	s.queue_free()
	_finish("mouse_hdls %s %s recv=%s" % [st, pos, _fmt_recv(true)])

func _arm_null_edge() -> void:
	var s := _mk_sink("s0")
	InputMap.add_action(&"ne")
	watch = [&"ne"]
	ev_watch = true
	await _pr_frames(2)
	Input.parse_input_event(_act(&"ne", false))          # release before press
	await _pr_frames(2)
	var rel_first := _st(&"ne")
	Input.parse_input_event(InputEventShortcut.new())   # concrete, non-action
	var ev_empty := _act(&"", true)
	Input.parse_input_event(ev_empty)             # empty action name
	await _pr_frames(1)
	var base_seen := inlog.size()
	Input.parse_input_event(null)                        # typed refusal
	var miss := Input.is_action_pressed(&"never_existed")
	var miss2 := Input.is_action_just_pressed(&"never_existed2")
	Input.action_press(&"never_existed3")
	await _pr_frames(1)
	s.queue_free()
	_finish("null_edge rel_first[%s] base_recv=%d miss_p=%s miss_jp=%s recv=%s" % [
		rel_first, base_seen, str(miss), str(miss2),
		str(inlog.map(func(r): return "%s%s:%s" % [r.via, r.tag, r.desc]))])

func _arm_dispatch_order() -> void:
	_mk_sink("s0")
	_mk_sink("s1")
	await _pr_frames(2)
	Input.parse_input_event(_key(KEY_F8, true))
	await _pr_frames(2)
	# handled gate: s0._input marks the event handled on the NEXT events
	flags["on_event"] = func(_e: InputEvent, via: String, tag: String) -> void:
		if via == "in" and tag == "s0" and flags.get("do_handle", false):
			root.set_input_as_handled()
	flags["do_handle"] = true
	Input.parse_input_event(_key(KEY_F8, false))
	Input.parse_input_event(_key(KEY_F8, true))
	await _pr_frames(2)
	_finish("dispatch_order recv=%s" % [
		str(inlog.map(func(r): return "%d:%s%s" % [r.seq, r.via, r.tag]))])

func _arm_reentrant() -> void:
	_mk_sink("s0")
	InputMap.add_action(&"ra")
	InputMap.add_action(&"rb")
	flags["on_event"] = func(e: InputEvent, via: String, _tag: String) -> void:
		if via != "in":
			return
		var depth: int = flags.get("depth", 0)
		if e is InputEventAction and e.action == &"ra" and e.pressed and depth < 1:
			flags["depth"] = depth + 1
			Input.parse_input_event(_act(&"rb", true))
	await _pr_frames(2)
	Input.parse_input_event(_act(&"ra", true))
	await _pr_frames(3)
	var acc_recv := str(inlog.map(func(r): return "%d:%s%s:%s" % [r.seq, r.via, r.tag, r.desc]))
	inlog.clear()
	Input.use_accumulated_input = false
	Input.parse_input_event(_act(&"ra", false))
	flags["depth"] = 0
	Input.parse_input_event(_act(&"ra", true))
	await _pr_frames(2)
	var off_recv := str(inlog.map(func(r): return "%d:%s%s:%s" % [r.seq, r.via, r.tag, r.desc]))
	_finish("reentrant acc=%s off=%s" % [acc_recv, off_recv])

func _arm_phys_peer() -> void:
	# The ph_step callback parses a press inside s0's _physics_process at a
	# pinned step offset; s1's same-step tick then answers "does a peer see it".
	_mk_sink("s0")
	_mk_sink("s1")
	InputMap.add_action(&"px")
	watch = [&"px"]
	await _ph_frames(1)
	var step0: int = phys_no
	flags["ph0"] = step0
	flags["pr0"] = proc_no
	flags["ph_step"] = step0 + 1
	flags["on_ph_step"] = func(_tag: String) -> void:
		Input.parse_input_event(_act(&"px", true))
		flags["same_tick_state"] = _st(&"px")
		flags["parse_step"] = phys_no
	rec_ph = 24
	rec_pr = 0
	await _pr_frames(30)
	# ticks for s1 (the peer, second in tree order), indexed by step-delta vs parse
	var pstep: int = flags.get("parse_step", 0)
	var s1_map := {}
	var s0_map := {}
	for t in ticks:
		if t.k == "ph":
			(s1_map if t.tag == "s1" else s0_map)[t.d] = t.st
	var ev_d := -999
	for t in ticks:
		if t.k == "EV":
			ev_d = t.d
			break
	var cells: Array = []
	for d in range(0, 6):
		var rel := d - (pstep - step0)
		cells.append("d%s{s1=%s,s0=%s}" % [
			"+" + str(rel) if rel >= 0 else str(rel),
			str(s1_map.get(d, "-")), str(s0_map.get(d, "-"))])
	_finish("phys_peer same_tick[%s] ev_step_delta=%s cells=%s" % [
		str(flags.get("same_tick_state", "-")), str(ev_d - (pstep - step0)),
		" ".join(cells)])
