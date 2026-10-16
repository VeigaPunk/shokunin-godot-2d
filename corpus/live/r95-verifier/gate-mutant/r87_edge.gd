extends SceneTree
# r87-scout finisher edge probe — adjacent surface of input_lattice.gd.
#   godot --headless --path <scratch> --script res://r87_edge.gd -- --arm=<name>
# Arms:
#   jpbe   — is_action_just_{pressed,released}_by_event, InputMap.event_is_action
#            exact_match, InputEventAction.event_index population. Immediate-API
#            reads at parse time only (deterministic window).
#   jmode  — in-process mode census of the three instability shapes the
#            input_lattice verify flagged: ph-count, ph-delta, just_-flag.
#            Prints histograms, never a pinned sequence.

var arm := ""
var phys_no := 0
var proc_no := 0
var inlog: Array = []

class Sink extends Node:
	var hub
	func _input(e: InputEvent) -> void:
		hub.inlog.append({"pr": hub.proc_no, "ph": hub.phys_no,
			"cls": e.get_class(), "act": str(e.get("action"))})

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _mk_sink() -> Sink:
	var s := Sink.new()
	s.hub = self
	root.add_child(s)
	return s

func _key(kc: int, pressed: bool = true, phys: int = 0, shift: bool = false) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = kc
	e.physical_keycode = phys
	e.pressed = pressed
	e.shift_pressed = shift
	return e

func _act(name: StringName, pressed: bool, strength: float = 1.0) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = name
	e.pressed = pressed
	e.strength = strength
	return e

func _st(a: StringName) -> String:
	return "%d/%.2f/%d/%d" % [int(Input.is_action_pressed(a)),
		Input.get_action_strength(a),
		int(Input.is_action_just_pressed(a)),
		int(Input.is_action_just_released(a))]

func _run() -> void:
	physics_frame.connect(func() -> void: phys_no += 1)
	process_frame.connect(func() -> void: proc_no += 1)
	print("R87E arm=%s godot=%s acc=%s tps=%s" % [arm,
		Engine.get_version_info().string, Input.use_accumulated_input,
		ProjectSettings.get_setting("physics/common/physics_ticks_per_second")])
	match arm:
		"jpbe": await _arm_jpbe()
		"jmode": await _arm_jmode()
		_: print("FAIL r87_edge %s reason=unknown_arm" % arm); quit(1)

# -- jpbe: by_event + event_is_action + event_index ---------------------------
func _arm_jpbe() -> void:
	_mk_sink()
	InputMap.add_action(&"jx")
	InputMap.action_add_event(&"jx", _key(KEY_J))
	InputMap.add_action(&"jshift")
	InputMap.action_add_event(&"jshift", _key(0, true, KEY_W, true))  # shift+phys-W
	InputMap.add_action(&"jother")
	InputMap.action_add_event(&"jother", _key(KEY_K))
	await process_frame
	await process_frame
	# key press bound to jx — buffered under acc=true; state applies at flush
	var jdown := _key(KEY_J, true)
	Input.parse_input_event(jdown)
	var imm := _st(&"jx")                    # pre-flush: still 0
	await process_frame                      # flush happened inside this boundary
	var post := _st(&"jx")
	# by_event reads while just_pressed is live
	var j_k := Input.is_action_just_pressed_by_event(&"jx", jdown)
	var j_wrong := Input.is_action_just_pressed_by_event(&"jx", _key(KEY_K, true))
	var j_other_a := Input.is_action_just_pressed_by_event(&"jother", jdown)
	var j_rel := Input.is_action_just_released_by_event(&"jx", jdown)
	# InputMap.event_is_action matrix (event, action, exact_match)
	var eia_hit := int(InputMap.event_is_action(jdown, &"jx"))
	var eia_miss := int(InputMap.event_is_action(jdown, &"jother"))
	var eia_ex_hit := int(InputMap.event_is_action(jdown, &"jx", true))
	# shift-modified W event vs shift-bound action, exact vs not
	var wshift := _key(0, true, KEY_W, true)
	var wplain := _key(0, true, KEY_W, false)
	var se_exact := int(InputMap.event_is_action(wshift, &"jshift", true))
	var se_plain := int(InputMap.event_is_action(wshift, &"jshift", false))
	var pe_exact := int(InputMap.event_is_action(wplain, &"jshift", true))
	var pe_plain := int(InputMap.event_is_action(wplain, &"jshift", false))
	# by_event on the shift action with/without exact match
	var jp_ex := int(Input.is_action_just_pressed_by_event(&"jx", jdown, true))
	# InputEventAction path: valid (ei=-1) vs refused (ei=42) — see ei_bound law
	var act_ev := _act(&"jx2", true)
	InputMap.add_action(&"jx2")
	Input.parse_input_event(act_ev)
	var a_pre := _st(&"jx2")
	await process_frame
	var a_imm := _st(&"jx2")
	var a_jpbe := int(Input.is_action_just_pressed_by_event(&"jx2", act_ev))
	var a_eia := int(InputMap.event_is_action(act_ev, &"jx2"))
	var bad_ev := _act(&"jx3", true)
	bad_ev.event_index = 42
	InputMap.add_action(&"jx3")
	Input.parse_input_event(bad_ev)
	await process_frame
	var b_st := _st(&"jx3")
	var a_ei := act_ev.event_index          # readback: did parse populate?
	var a_ai := str(act_ev.get("action_index"))   # property does not exist in census
	# release edge for by_event — jup is the single releasing event
	var jup := _key(KEY_J, false)
	Input.parse_input_event(jup)
	await process_frame
	var r_st := _st(&"jx")
	var r_jrbe := int(Input.is_action_just_released_by_event(&"jx", jup))
	var r_jpbe := int(Input.is_action_just_pressed_by_event(&"jx", jup))
	await process_frame
	print("PASS r87_edge jpbe imm[%s] post[%s] jpbe[j=%d wrong=%d other=%d rel_on_press=%d ex=%d] "
		% [imm, post, int(j_k), int(j_wrong), int(j_other_a), int(j_rel), jp_ex]
		+ "eia[hit=%d miss=%d ex=%d] shift[s_ex=%d s_plain=%d p_ex=%d p_plain=%d] "
		% [eia_hit, eia_miss, eia_ex_hit, se_exact, se_plain, pe_exact, pe_plain]
		+ "act[pre=%s imm=%s jpbe=%d eia=%d ei=%d ai=%s bad_st=%s] "
		% [a_pre, a_imm, a_jpbe, a_eia, a_ei, a_ai, b_st]
		+ "rel[st=%s jrbe=%d jpbe=%d] recv_n=%d"
		% [r_st, r_jrbe, r_jpbe, inlog.size()])
	quit(0)

# -- jmode: in-process instability census -------------------------------------
func _arm_jmode() -> void:
	var s := _mk_sink()
	InputMap.add_action(&"jm")
	await process_frame
	await process_frame
	# shape A (press_phys): ph ticks elapsed during await process_frame x10
	var count_hist := {}
	for i in 16:
		var p0 := phys_no
		for k in 10:
			await process_frame
		var d: int = phys_no - p0
		count_hist[d] = int(count_hist.get(d, 0)) + 1
	# shape B (ui_ns): ph delta between parse call and buffered receipt delivery
	inlog.clear()
	var delta_hist := {}
	for i in 16:
		var p0 := phys_no
		Input.parse_input_event(_act(&"jm", true))
		var n0 := inlog.size()
		for k in 3:
			await process_frame
			if inlog.size() > n0:
				break
		var d: int = inlog[n0].ph - p0 if inlog.size() > n0 else -99
		delta_hist[d] = int(delta_hist.get(d, 0)) + 1
		Input.parse_input_event(_act(&"jm", false))
		await process_frame
	# shape C (release_edge): just_pressed at first ph tick after a
	# press -> 2 idle frames -> release sequence, plus whether a ph tick
	# interposed in the gap
	var flag_hist := {}
	var gap_hist := {}
	InputMap.add_action(&"jr")
	for i in 16:
		Input.parse_input_event(_act(&"jr", true))
		var g0 := phys_no
		await process_frame
		await process_frame
		var gap: int = phys_no - g0          # ph ticks inside the 2-pr window
		Input.parse_input_event(_act(&"jr", false))
		# sample at the first physics_frame AFTER the release parse
		# (array cell: lambdas capture locals by value, arrays by reference)
		var jp_at := [-1]
		var cb := func() -> void:
			if jp_at[0] < 0:
				jp_at[0] = int(Input.is_action_just_pressed(&"jr"))
		physics_frame.connect(cb)
		await physics_frame
		physics_frame.disconnect(cb)
		var key := "%d/jp%d" % [gap, jp_at[0]]
		flag_hist[key] = int(flag_hist.get(key, 0)) + 1
		gap_hist[gap] = int(gap_hist.get(gap, 0)) + 1
		await process_frame
	print("PASS r87_edge jmode ph_in_10pr=%s recv_ph_delta=%s flag[gap/jp]=%s gap=%s"
		% [str(count_hist), str(delta_hist), str(flag_hist), str(gap_hist)])
	s.queue_free()
	quit(0)
