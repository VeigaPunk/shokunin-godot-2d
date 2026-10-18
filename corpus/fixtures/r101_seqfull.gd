extends SceneTree
# r101-E12 scratch probe — FULL-REPLAY receipt for the 14-cell sequence
# (closes reports/round-100/r100-critic.md F2: the r100b_seq rows pinned one
#  line of a 14-cell replay, so a forged extra output line inside the replay
#  left both rows PASS and 3 of the 4 divergences were unconstrained).
#
#   godot --headless --path <scratch> --script res://r101_seqfull.gd -- --clean=<0|1>
#
# Cell bodies are the r100b_seq.gd bodies unchanged (byte-diff shows only the
# `print(` -> `_emit(` rename plus the receipt assembly). Each cell's
# `PASS r100_gui <cell> ...` line is printed in run order and appended to the
# transcript, so the whole stdout span
#
#   SEQ_BEGIN ... <14 cell lines, contiguous> SEQ_CENSUS ... SEQ_END digest=<sha256>
#
# is one contiguous multi-line unit: a forged extra stdout line anywhere inside
# the replay breaks the adjacency the row signature pins. SEQ_CENSUS recomputes
# the divergence census against FRESH_PINS (the 14 `r100_gui_*` harness pins
# embedded BY VALUE), SEQ_END digest binds the 14 cell lines by content.
# No object ids / RIDs / timestamps.

var arm := ""
var _nodes: Array = []

var _transcript: Array = []

# The 14 fresh-process `r100_gui_*` CASES pins, by value.
const FRESH_PINS := {
    "census": "PASS r100_gui census dv=headless vpsize=(64.0, 64.0) final=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000) mf_ctrl=0 mf_label=2 mf_button=0 mf_panel=0 mf_container=1 focus_mode_ctrl=0 vpmethods=[push_input=1|push_unhandled_input=1|gui_get_focus_owner=1|gui_get_hovered_control=1|gui_is_dragging=1|gui_get_drag_data=1|gui_release_focus=1|set_input_as_handled=1|is_input_handled=1|get_mouse_position=1|warp_mouse=1|get_final_transform=1] ctrlmethods=[force_drag=1|accept_event=1|grab_focus=1|has_focus=1|release_focus=1|get_local_mouse_position=1|set_drag_preview=1] inputmethods=[warp_mouse=1|get_mouse_position=0|set_emulate_mouse_from_touch=1|is_emulating_mouse_from_touch=1|set_emulate_touch_from_mouse=1|is_emulating_touch_from_mouse=1|get_last_mouse_velocity=1|get_last_mouse_screen_velocity=1|parse_input_event=1|flush_buffered_events=1|is_mouse_button_pressed=1] emul_mouse=1 emul_touch=0 mbprops=[alt_pressed|button_index|button_mask|canceled|ctrl_pressed|device|double_click|factor|global_position|meta_pressed|position|pressed|resource_local_to_scene|resource_name|script|shift_pressed|window_id] mmprops=[alt_pressed|button_mask|ctrl_pressed|device|global_position|meta_pressed|pen_inverted|position|pressure|relative|resource_local_to_scene|resource_name|screen_relative|screen_velocity|script|shift_pressed|tilt|velocity|window_id] stprops=[canceled|device|double_tap|index|position|pressed|resource_local_to_scene|resource_name|script|window_id] sdprops=[device|index|pen_inverted|position|pressure|relative|resource_local_to_scene|resource_name|screen_relative|screen_velocity|script|tilt|velocity|window_id]",
    "routing": "PASS r100_gui routing s1_cc[[C:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|C:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]]- s2_ci[-][P:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|P:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] s3_cp[[C:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|C:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]][P:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|P:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] s4_ch[[C:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|C:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]]- s5_ci_pp[-][P:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|P:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] s6_ii[-]- s7_inparent[-][P:mb(b=1,p=1,dc=0,bm=0,pos=24.0,24.0,gpos=24.0,24.0)|P:mb(b=1,p=0,dc=0,bm=0,pos=24.0,24.0,gpos=24.0,24.0)] s8_out[-]- s9_rb[-][P:mb(b=2,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] s10_input_state held_push=0 cursor=(0.0, 0.0)",
    "hover": "PASS r100_gui hover h0=null h1=A ev=[A_in] h2=A ev=[A_in] h3=B ev=[A_in|A_out|B_in] h4=null ev=[A_in|A_out|B_in|B_out] h5=C ev=[A_in|A_out|B_in|B_out] h6_press=A ev=[A_in|A_out|B_in|B_out|A_in] h7_after_release=A",
    "motion": "PASS r100_gui motion m1[[S:mm(bm=0,pos=10.0,10.0,gpos=10.0,10.0,rel=5.0,7.0,vel=0.0,0.0)]] m2[[S:mm(bm=0,pos=20.0,30.0,gpos=20.0,30.0,rel=10.0,20.0,vel=0.0,0.0)]] m3_dc[[S:mb(b=1,p=1,dc=1,bm=0,pos=10.0,10.0,gpos=10.0,10.0)|S:mb(b=1,p=0,dc=0,bm=0,pos=10.0,10.0,gpos=10.0,10.0)]] m4_push_input_state held=0 cursor=(0.0, 0.0) vel=(0.0, 0.0)",
    "localpos": "PASS r100_gui localpos lp_push_p[-] c[[C:mb(b=1,p=1,dc=0,bm=0,pos=6.0,2.0,gpos=30.0,14.0)]] loc_c=-24.0,-12.0 lp_push_local_p[-] c[[C:mb(b=1,p=1,dc=0,bm=0,pos=6.0,2.0,gpos=30.0,14.0)]] lp_parse_p[-] c[[C:mb(b=1,p=1,dc=0,bm=0,pos=6.0,2.0,gpos=30.0,14.0)]] loc_c=6.0,2.0 gloc_c=30.0,14.0",
    "cursor": "PASS r100_gui cursor c0=(0.0, 0.0) c1_push_mm=(0.0, 0.0) c2_push_mb=(0.0, 0.0) c3_parse_mb=(24.0, 24.0) c4_parse_mm=(30.0, 30.0) c5_gpos_drives=(60.0, 60.0) c6_parse_st=(44.0, 44.0) c7_push_mm2=(44.0, 44.0) c8 ds=(0, 0)",
    "clip": "PASS r100_gui clip cp0_vis=[P: (0.0, 0.0), S: (64.0, 64.0)] cp_hover(62.0, 4.0)=ED cp_press(62.0, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=2.0,4.0,gpos=62.0,4.0)] fa=- cp_hover(63.9, 4.0)=ED cp_press(63.9, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=3.9,4.0,gpos=63.9,4.0)] fa=- cp_hover(64.0, 4.0)=null cp_press(64.0, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=4.0,4.0,gpos=64.0,4.0)] fa=- cp_hover(64.1, 4.0)=null cp_press(64.1, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=4.1,4.0,gpos=64.1,4.0)] fa=- cp_hover(70.0, 4.0)=null cp_press(70.0, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=10.0,4.0,gpos=70.0,4.0)] fa=- cp_hover(90.0, 4.0)=null cp_press(90.0, 4.0) in=- ed=- fa=[FA:mb(b=1,p=1,dc=0,bm=0,pos=10.0,4.0,gpos=90.0,4.0)] cp_hover200=null",
    "drag": "PASS r100_gui drag d1_at_threshold drag=0 calls=0 d2_over_threshold drag=1 calls=1 data=fromA at=[(8.0,8.0)] d3_over_b drag=1 a_drop=[can(fromA)] b_drop=[can(fromA)] b_get=0 d4_over_b2 b_drop=[can(fromA)|can(fromA)] d5_release drag=0 b_drop=[can(fromA)|can(fromA)|can(fromA)|drop(fromA)] d6_unmasked_motion drag=0 calls=1 d7_accum[1:0 2:1 3:1 ] calls=2 d8_no_target drag=0 a_drop=[can(fromA)|can(fromA)|can(fromA)|can(fromA)|drop(fromA)|can(fromA)|can(fromA)|drop(fromA)] b_drop=[can(fromA)|can(fromA)|can(fromA)|drop(fromA)] d9_force drag=1 data=forced calls=0 d10_force_over_d d_drop=[can(forced)] d11_force_drop drag=0 d_drop=[can(forced)|can(forced)|drop(forced)] d12_nodrop drag=0 d_drop=[can(forced)|can(forced)|drop(forced)|can(no)]",
    "touch": "PASS r100_gui touch t1_push_a=- b=[B:st(i=0,p=1,dt=1,pos=4.0,4.0)] t2_pushdrag_a=- b=[B:sd(i=0,pos=-12.0,4.0,rel=-16.0,0.0)] t3_emul_touch held=1 a=[A:mb(b=1,p=1,dc=0,bm=1,pos=8.0,8.0,gpos=8.0,8.0)|A:st(i=0,p=1,dt=0,pos=8.0,8.0)] b=- emul=1 t4_emul_mouse a_gui=- a_in=[A:st(i=0,p=1,dt=0,pos=20.0,4.0)|A:mb(b=1,p=1,dc=0,bm=0,pos=20.0,4.0,gpos=20.0,4.0)] emul_t=1",
    "subvp": "PASS r100_gui subvp v0_local=1 size=(64, 64) cursor=(0.0, 0.0) v1_sub[[S:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]] root=- v2_hovered=S cursor_sub=(8.0, 8.0) cursor_root=(0.0, 0.0) v3_root_push_sub[-] root=[R:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] v4_cursors sub=(8.0, 8.0) root=(0.0, 0.0) v5_local_false local=0 s2=[[S2:mb(b=1,p=1,dc=0,bm=0,pos=12.0,12.0,gpos=12.0,12.0)]] cursor=(12.0, 12.0)",
    "warp": "PASS r100_gui warp w0 dv=headless cursor=(0.0, 0.0) ds_mouse=(0, 0) w1 after_push cursor=(0.0, 0.0) ds_mouse=(0, 0) w2 after_input_warp cursor=(0.0, 0.0) ds_mouse=(0, 0) w3 after_vp_warp cursor=(0.0, 0.0) ds_mouse=(0, 0) w4 mode=0",
    "focus": "PASS r100_gui focus f0 owner=F f_focus=1 g_focus=0 f1_key gui_f=[F:key(k=65,p=1)] gui_g=- in_f=[F:key(k=65,p=1)] f2_handled gui_f=[F:key(k=65,p=1)] gui_g=- f3_regrab gui_f=- gui_g=[G:key(k=65,p=1)] owner=G f4_released gui_f=- gui_g=- owner=null",
    "render": "PASS r100_gui render r0 tex_cls=ViewportTexture size=(64.0, 64.0) r1 img_null=1 r2 adapter= rd_null=1 r3 method=forward_plus screens=0 ssize=(0, 0) win_size=(64, 64) r4 light sh=0 filt=0 smooth=0.0 blend=0 r5 gpu_capture=[P: (0.0, 0.0), S: (0.0, 0.0)]",
    "osmeta": "PASS r100_gui osmeta Thread[e=1,m=7] Mutex[e=1,m=3] Semaphore[e=1,m=3] WorkerThreadPool[e=1,m=9] Time[e=1,m=21] os=Linux procs_gt0=1 wtp_has_thread_count=0",
}

class Sink extends Control:
	var tag := ""
	var log: Array = []
	var in_log: Array = []
	var handled := false
	var drag_data: Variant = null
	var drag_calls := 0
	var drag_at: Array = []
	var drop_log: Array = []
	var can_drop := true

	func _gui_input(event: InputEvent) -> void:
		log.append("%s:%s" % [tag, _ev(event)])
		if handled:
			get_viewport().set_input_as_handled()

	func _input(event: InputEvent) -> void:
		if in_log.size() < 24:
			in_log.append("%s:%s" % [tag, _ev(event)])

	func _ev(event: InputEvent) -> String:
		if event is InputEventMouseButton:
			var e := event as InputEventMouseButton
			return "mb(b=%d,p=%d,dc=%d,bm=%d,pos=%.1f,%.1f,gpos=%.1f,%.1f)" % [
				e.button_index, int(e.pressed), int(e.double_click), e.button_mask,
				e.position.x, e.position.y, e.global_position.x, e.global_position.y]
		if event is InputEventMouseMotion:
			var e := event as InputEventMouseMotion
			return "mm(bm=%d,pos=%.1f,%.1f,gpos=%.1f,%.1f,rel=%.1f,%.1f,vel=%.1f,%.1f)" % [
				e.button_mask, e.position.x, e.position.y, e.global_position.x, e.global_position.y,
				e.relative.x, e.relative.y, e.velocity.x, e.velocity.y]
		if event is InputEventKey:
			var e := event as InputEventKey
			return "key(k=%d,p=%d)" % [e.keycode, int(e.pressed)]
		if event is InputEventScreenTouch:
			var e := event as InputEventScreenTouch
			return "st(i=%d,p=%d,dt=%d,pos=%.1f,%.1f)" % [
				e.index, int(e.pressed), int(e.double_tap), e.position.x, e.position.y]
		if event is InputEventScreenDrag:
			var e := event as InputEventScreenDrag
			return "sd(i=%d,pos=%.1f,%.1f,rel=%.1f,%.1f)" % [
				e.index, e.position.x, e.position.y, e.relative.x, e.relative.y]
		return event.get_class()

	func _get_drag_data(at_position: Vector2) -> Variant:
		drag_calls += 1
		drag_at.append("(%.1f,%.1f)" % [at_position.x, at_position.y])
		return drag_data

	func _can_drop_data(_at_position: Vector2, data: Variant) -> bool:
		drop_log.append("can(%s)" % _dtag(data))
		return can_drop

	func _drop_data(_at_position: Vector2, data: Variant) -> void:
		drop_log.append("drop(%s)" % _dtag(data))

	func _dtag(data: Variant) -> String:
		if data == null:
			return "null"
		if data is Dictionary and data.has("tag"):
			return str(data["tag"])
		return "<data>"


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _run() -> void:
	var seq_arms := ['census', 'routing', 'hover', 'motion', 'localpos', 'cursor', 'clip', 'drag', 'touch', 'subvp', 'warp', 'focus', 'render', 'osmeta']
	var do_clean := 0
	for a in OS.get_cmdline_user_args():
		if a == "--clean=1":
			do_clean = 1
	print("SEQ_BEGIN cells=%d clean=%d pins=%d" % [seq_arms.size(), do_clean, FRESH_PINS.size()])
	for a in seq_arms:
		arm = a
		match arm:
			"census":
				await _cell_census()
			"routing":
				await _cell_routing()
			"hover":
				await _cell_hover()
			"motion":
				await _cell_motion()
			"localpos":
				await _cell_localpos()
			"cursor":
				await _cell_cursor()
			"clip":
				await _cell_clip()
			"drag":
				await _cell_drag()
			"touch":
				await _cell_touch()
			"subvp":
				await _cell_subvp()
			"warp":
				await _cell_warp()
			"focus":
				await _cell_focus()
			"render":
				await _cell_render()
			"osmeta":
				await _cell_osmeta()
			_:
				pass
		if do_clean == 1:
			await _cleanup()
	var divergent: Array = []
	for i in range(seq_arms.size()):
		if _transcript[i] != FRESH_PINS[seq_arms[i]]:
			divergent.append(seq_arms[i])
	print("SEQ_CENSUS identical=%d divergent_n=%d divergent=[%s]" % [
		seq_arms.size() - divergent.size(), divergent.size(), "|".join(divergent)])
	print("SEQ_END digest=%s" % "\n".join(_transcript).sha256_text())
	await _cleanup()
	quit(0)


func _emit(line: String) -> void:
	_transcript.append(line)
	print(line)


func _cleanup() -> void:
	for c in root.get_children():
		c.free()
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()
	await process_frame


func _mk_sink(tag: String, pos: Vector2, size: Vector2, filt: int) -> Sink:
	var s := Sink.new()
	_nodes.append(s)
	s.tag = tag
	s.name = tag
	s.position = pos
	s.size = size
	s.mouse_filter = filt
	return s


func _mb(pos: Vector2, pressed: bool, mask := 0, dc := false) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = pressed
	e.button_mask = mask
	e.double_click = dc
	e.position = pos
	e.global_position = pos
	return e


func _mm(pos: Vector2, rel: Vector2, mask := 0) -> InputEventMouseMotion:
	var e := InputEventMouseMotion.new()
	e.position = pos
	e.global_position = pos
	e.relative = rel
	e.button_mask = mask
	return e


func _click(pos: Vector2) -> void:
	root.push_input(_mb(pos, true))
	root.push_input(_mb(pos, false))


func _fmt(arr: Array) -> String:
	return "-" if arr.is_empty() else "[%s]" % "|".join(arr)


func _clr(sinks: Array) -> void:
	for s in sinks:
		(s as Sink).log.clear()


func _tag_of(c: Control) -> String:
	if c == null:
		return "null"
	if c.name != "":
		return str(c.name)
	return c.get_class()


func _method_map(o: Object, names: Array) -> String:
	var out: Array = []
	for m in names:
		out.append("%s=%d" % [m, int(o.has_method(m))])
	return "|".join(out)


func _own_props(o: Object) -> Array:
	var out: Array = []
	for p in o.get_property_list():
		if int(p.get("usage", 0)) & PROPERTY_USAGE_STORAGE:
			out.append(str(p["name"]))
	out.sort()
	return out


func _xform(x: Transform2D) -> String:
	return "(%.4f,%.4f;%.4f,%.4f;%.4f,%.4f)" % [x.x.x, x.y.x, x.x.y, x.y.y, x.origin.x, x.origin.y]


# ---------------------------------------------------------------- census
func _cell_census() -> void:
	var ctrl := Control.new()
	var label := Label.new()
	var button := Button.new()
	var panel := Panel.new()
	var ccontainer := Container.new()
	_nodes.append_array([ctrl, label, button, panel, ccontainer])
	var facts: Array = []
	facts.append("dv=%s" % DisplayServer.get_name())
	facts.append("vpsize=%s" % str(root.get_visible_rect().size))
	facts.append("final=%s" % _xform(root.get_final_transform()))
	facts.append("mf_ctrl=%d mf_label=%d mf_button=%d mf_panel=%d mf_container=%d" % [
		ctrl.mouse_filter, label.mouse_filter, button.mouse_filter, panel.mouse_filter,
		ccontainer.mouse_filter])
	facts.append("focus_mode_ctrl=%d" % ctrl.focus_mode)
	facts.append("vpmethods=[%s]" % _method_map(root, [
		"push_input", "push_unhandled_input", "gui_get_focus_owner",
		"gui_get_hovered_control", "gui_is_dragging", "gui_get_drag_data",
		"gui_release_focus", "set_input_as_handled", "is_input_handled",
		"get_mouse_position", "warp_mouse", "get_final_transform"]))
	facts.append("ctrlmethods=[%s]" % _method_map(ctrl, [
		"force_drag", "accept_event", "grab_focus", "has_focus",
		"release_focus", "get_local_mouse_position", "set_drag_preview"]))
	facts.append("inputmethods=[%s]" % _method_map(Input, [
		"warp_mouse", "get_mouse_position", "set_emulate_mouse_from_touch",
		"is_emulating_mouse_from_touch", "set_emulate_touch_from_mouse",
		"is_emulating_touch_from_mouse", "get_last_mouse_velocity",
		"get_last_mouse_screen_velocity", "parse_input_event",
		"flush_buffered_events", "is_mouse_button_pressed"]))
	facts.append("emul_mouse=%d emul_touch=%d" % [
		int(Input.is_emulating_mouse_from_touch()), int(Input.is_emulating_touch_from_mouse())])
	var mb := InputEventMouseButton.new()
	facts.append("mbprops=[%s]" % "|".join(_own_props(mb)))
	var mm := InputEventMouseMotion.new()
	facts.append("mmprops=[%s]" % "|".join(_own_props(mm)))
	var st := InputEventScreenTouch.new()
	facts.append("stprops=[%s]" % "|".join(_own_props(st)))
	var sd := InputEventScreenDrag.new()
	facts.append("sdprops=[%s]" % "|".join(_own_props(sd)))
	_emit("PASS r100_gui census %s" % " ".join(facts))


# ---------------------------------------------------------------- routing
func _cell_routing() -> void:
	var parent := _mk_sink("P", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var child := _mk_sink("C", Vector2.ZERO, Vector2(16, 16), Control.MOUSE_FILTER_STOP)
	parent.add_child(child)
	root.add_child(parent)
	await process_frame
	var out: Array = []
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s1_cc[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	child.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s2_ci[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	child.mouse_filter = Control.MOUSE_FILTER_PASS
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s3_cp[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	child.handled = true
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s4_ch[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	child.handled = false
	child.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.mouse_filter = Control.MOUSE_FILTER_PASS
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s5_ci_pp[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	parent.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s6_ii[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	parent.mouse_filter = Control.MOUSE_FILTER_STOP
	_clr([parent, child])
	_click(Vector2(24, 24))
	await process_frame
	out.append("s7_inparent[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	_clr([parent, child])
	_click(Vector2(60, 60))
	await process_frame
	out.append("s8_out[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	var rb := InputEventMouseButton.new()
	rb.button_index = MOUSE_BUTTON_RIGHT
	rb.pressed = true
	rb.position = Vector2(8, 8)
	rb.global_position = Vector2(8, 8)
	_clr([parent, child])
	root.push_input(rb)
	await process_frame
	out.append("s9_rb[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	_clr([parent, child])
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	var held_push := int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT))
	root.push_input(_mb(Vector2(8, 8), false))
	await process_frame
	out.append("s10_input_state held_push=%d cursor=%s" % [
		held_push, str(root.get_mouse_position())])
	_emit("PASS r100_gui routing %s" % " ".join(out))


# ---------------------------------------------------------------- hover
func _cell_hover() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var b := _mk_sink("B", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var ign := _mk_sink("I", Vector2.ZERO, Vector2(8, 8), Control.MOUSE_FILTER_IGNORE)
	a.add_child(ign)
	var ev: Array = []
	a.mouse_entered.connect(func() -> void: ev.append("A_in"))
	a.mouse_exited.connect(func() -> void: ev.append("A_out"))
	b.mouse_entered.connect(func() -> void: ev.append("B_in"))
	b.mouse_exited.connect(func() -> void: ev.append("B_out"))
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	out.append("h0=%s" % _tag_of(root.gui_get_hovered_control()))
	root.push_input(_mm(Vector2(8, 8), Vector2(8, 8)))
	await process_frame
	out.append("h1=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(4, 4), Vector2(-4, -4)))
	await process_frame
	out.append("h2=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(40, 8), Vector2(36, 4)))
	await process_frame
	out.append("h3=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(60, 60), Vector2(20, 52)))
	await process_frame
	out.append("h4=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	var c := _mk_sink("C", Vector2.ZERO, Vector2(8, 8), Control.MOUSE_FILTER_STOP)
	ign.add_child(c)
	await process_frame
	root.push_input(_mm(Vector2(2, 2), Vector2(-58, -58)))
	await process_frame
	out.append("h5=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(60, 60), Vector2(58, 58)))
	await process_frame
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("h6_press=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mb(Vector2(8, 8), false))
	await process_frame
	out.append("h7_after_release=%s" % _tag_of(root.gui_get_hovered_control()))
	_emit("PASS r100_gui hover %s" % " ".join(out))


# ---------------------------------------------------------------- motion
func _cell_motion() -> void:
	var s := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(s)
	await process_frame
	var out: Array = []
	_clr([s])
	root.push_input(_mm(Vector2(10, 10), Vector2(5, 7)))
	await process_frame
	out.append("m1[%s]" % _fmt(s.log))
	_clr([s])
	root.push_input(_mm(Vector2(20, 30), Vector2(10, 20)))
	await process_frame
	out.append("m2[%s]" % _fmt(s.log))
	_clr([s])
	root.push_input(_mb(Vector2(10, 10), true, 0, true))
	root.push_input(_mb(Vector2(10, 10), false))
	await process_frame
	out.append("m3_dc[%s]" % _fmt(s.log))
	out.append("m4_push_input_state held=%d cursor=%s vel=%s" % [
		int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)), str(root.get_mouse_position()),
		str(Input.get_last_mouse_velocity())])
	_emit("PASS r100_gui motion %s" % " ".join(out))


# ---------------------------------------------------------------- localpos
func _cell_localpos() -> void:
	var parent := _mk_sink("P", Vector2(20, 10), Vector2(40, 40), Control.MOUSE_FILTER_STOP)
	var child := _mk_sink("C", Vector2(4, 2), Vector2(10, 10), Control.MOUSE_FILTER_STOP)
	parent.add_child(child)
	root.add_child(parent)
	await process_frame
	var out: Array = []
	root.push_input(_mb(Vector2(30, 14), true))
	await process_frame
	out.append("lp_push_p[%s] c[%s] loc_c=%.1f,%.1f" % [
		_fmt(parent.log), _fmt(child.log),
		child.get_local_mouse_position().x, child.get_local_mouse_position().y])
	parent.log.clear()
	child.log.clear()
	root.push_input(_mb(Vector2(30, 14), true), true)
	await process_frame
	out.append("lp_push_local_p[%s] c[%s]" % [_fmt(parent.log), _fmt(child.log)])
	parent.log.clear()
	child.log.clear()
	Input.parse_input_event(_mb(Vector2(30, 14), true))
	await process_frame
	out.append("lp_parse_p[%s] c[%s] loc_c=%.1f,%.1f gloc_c=%.1f,%.1f" % [
		_fmt(parent.log), _fmt(child.log),
		child.get_local_mouse_position().x, child.get_local_mouse_position().y,
		child.get_global_mouse_position().x, child.get_global_mouse_position().y])
	_emit("PASS r100_gui localpos %s" % " ".join(out))


# ---------------------------------------------------------------- cursor
func _cell_cursor() -> void:
	var s := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(s)
	await process_frame
	var out: Array = []
	out.append("c0=%s" % str(root.get_mouse_position()))
	root.push_input(_mm(Vector2(20, 20), Vector2(20, 20)))
	await process_frame
	out.append("c1_push_mm=%s" % str(root.get_mouse_position()))
	root.push_input(_mb(Vector2(22, 22), true))
	await process_frame
	out.append("c2_push_mb=%s" % str(root.get_mouse_position()))
	Input.parse_input_event(_mb(Vector2(24, 24), false))
	await process_frame
	out.append("c3_parse_mb=%s" % str(root.get_mouse_position()))
	Input.parse_input_event(_mm(Vector2(30, 30), Vector2(6, 6)))
	await process_frame
	out.append("c4_parse_mm=%s" % str(root.get_mouse_position()))
	var mm2 := _mm(Vector2(70, 70), Vector2(10, 10))
	mm2.global_position = Vector2(60, 60)
	Input.parse_input_event(mm2)
	await process_frame
	out.append("c5_gpos_drives=%s" % str(root.get_mouse_position()))
	var st := InputEventScreenTouch.new()
	st.index = 0
	st.pressed = true
	st.position = Vector2(44, 44)
	Input.parse_input_event(st)
	await process_frame
	out.append("c6_parse_st=%s" % str(root.get_mouse_position()))
	root.push_input(_mm(Vector2(50, 50), Vector2(50, 50)))
	await process_frame
	out.append("c7_push_mm2=%s" % str(root.get_mouse_position()))
	out.append("c8 ds=%s" % str(DisplayServer.mouse_get_position()))
	_emit("PASS r100_gui cursor %s" % " ".join(out))


# ---------------------------------------------------------------- clip (motion picking vs button picking)
func _cell_clip() -> void:
	var inb := _mk_sink("IN", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var ed := _mk_sink("ED", Vector2(60, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var fa := _mk_sink("FA", Vector2(80, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(inb)
	root.add_child(ed)
	root.add_child(fa)
	await process_frame
	var out: Array = []
	out.append("cp0_vis=%s" % str(root.get_visible_rect()))
	for p in [Vector2(62, 4), Vector2(63.9, 4), Vector2(64, 4), Vector2(64.1, 4), Vector2(70, 4), Vector2(90, 4)]:
		root.push_input(_mm(p, p))
		await process_frame
		out.append("cp_hover%s=%s" % [str(p), _tag_of(root.gui_get_hovered_control())])
		_clr([inb, ed, fa])
		root.push_input(_mb(p, true))
		await process_frame
		out.append("cp_press%s in=%s ed=%s fa=%s" % [
			str(p), _fmt(inb.log), _fmt(ed.log), _fmt(fa.log)])
		root.push_input(_mb(p, false))
		await process_frame
	root.push_input(_mm(Vector2(200, 200), Vector2(200, 200)))
	await process_frame
	out.append("cp_hover200=%s" % _tag_of(root.gui_get_hovered_control()))
	_emit("PASS r100_gui clip %s" % " ".join(out))


# ---------------------------------------------------------------- drag
func _cell_drag() -> void:
	var LM := MOUSE_BUTTON_MASK_LEFT
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	a.drag_data = {"tag": "fromA"}
	var b := _mk_sink("B", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	b.drag_data = {"tag": "fromB"}
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	# d1: motion relative length exactly 10 -> below threshold
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(18, 8), Vector2(10, 0), LM))
	await process_frame
	out.append("d1_at_threshold drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(18, 8), false))
	await process_frame
	# d2: 10.5 -> drag starts; source = press-focus A, at_position = press-local
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(18.5, 8), Vector2(10.5, 0), LM))
	await process_frame
	out.append("d2_over_threshold drag=%d calls=%d data=%s at=%s" % [
		int(root.gui_is_dragging()), a.drag_calls, _dtag(root.gui_get_drag_data()), _fmt(a.drag_at)])
	# d3: motion over B (in-viewport) -> can_drop on B
	root.push_input(_mm(Vector2(40, 8), Vector2(21.5, 0), LM))
	await process_frame
	out.append("d3_over_b drag=%d a_drop=%s b_drop=%s b_get=%d" % [
		int(root.gui_is_dragging()), _fmt(a.drop_log), _fmt(b.drop_log), b.drag_calls])
	# d4: second motion over B -> can_drop again
	root.push_input(_mm(Vector2(44, 4), Vector2(4, -4), LM))
	await process_frame
	out.append("d4_over_b2 b_drop=%s" % _fmt(b.drop_log))
	# d5: release over B -> drop
	root.push_input(_mb(Vector2(44, 4), false))
	await process_frame
	out.append("d5_release drag=%d b_drop=%s" % [int(root.gui_is_dragging()), _fmt(b.drop_log)])
	# d6: masked press + unmasked motion (rel 30) -> no drag
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(38, 8), Vector2(30, 0), 0))
	await process_frame
	out.append("d6_unmasked_motion drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(38, 8), false))
	await process_frame
	# d7: accumulation 3 x (4,4): 5.66 / 11.31 / 16.97
	root.push_input(_mb(Vector2(4, 4), true, LM))
	var acc := ""
	for i in range(3):
		root.push_input(_mm(Vector2(8 + i * 4, 8 + i * 4), Vector2(4, 4), LM))
		await process_frame
		acc += "%d:%d " % [i + 1, int(root.gui_is_dragging())]
	out.append("d7_accum[%s] calls=%d" % [acc, a.drag_calls])
	root.push_input(_mb(Vector2(16, 16), false))
	await process_frame
	# d8: release over the source with no valid target -> cancel, no drop
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(8, 28), Vector2(0, 20), LM))
	await process_frame
	root.push_input(_mb(Vector2(8, 28), false))
	await process_frame
	out.append("d8_no_target drag=%d a_drop=%s b_drop=%s" % [
		int(root.gui_is_dragging()), _fmt(a.drop_log), _fmt(b.drop_log)])
	# d9: force_drag (no threshold, no mask needed)
	var c := _mk_sink("C", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var d := _mk_sink("D", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(c)
	root.add_child(d)
	await process_frame
	c.force_drag({"tag": "forced"}, null)
	await process_frame
	out.append("d9_force drag=%d data=%s calls=%d" % [
		int(root.gui_is_dragging()), _dtag(root.gui_get_drag_data()), c.drag_calls])
	root.push_input(_mm(Vector2(40, 8), Vector2(40, 8)))
	await process_frame
	out.append("d10_force_over_d d_drop=%s" % _fmt(d.drop_log))
	root.push_input(_mb(Vector2(40, 8), false))
	await process_frame
	out.append("d11_force_drop drag=%d d_drop=%s" % [int(root.gui_is_dragging()), _fmt(d.drop_log)])
	# d12: can_drop=false -> can called, drop not
	d.can_drop = false
	c.force_drag({"tag": "no"}, null)
	root.push_input(_mm(Vector2(41, 9), Vector2(1, 1)))
	await process_frame
	root.push_input(_mb(Vector2(41, 9), false))
	await process_frame
	out.append("d12_nodrop drag=%d d_drop=%s" % [int(root.gui_is_dragging()), _fmt(d.drop_log)])
	_emit("PASS r100_gui drag %s" % " ".join(out))


func _dtag(data: Variant) -> String:
	if data is Dictionary and data.has("tag"):
		return str(data["tag"])
	return "null" if data == null else "<data>"


# ---------------------------------------------------------------- touch
func _cell_touch() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(16, 16), Control.MOUSE_FILTER_STOP)
	var b := _mk_sink("B", Vector2(16, 0), Vector2(16, 16), Control.MOUSE_FILTER_STOP)
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	var st := InputEventScreenTouch.new()
	st.index = 0
	st.pressed = true
	st.double_tap = true
	st.position = Vector2(20, 4)
	root.push_input(st)
	await process_frame
	out.append("t1_push_a=%s b=%s" % [_fmt(a.log), _fmt(b.log)])
	a.log.clear()
	b.log.clear()
	var sd := InputEventScreenDrag.new()
	sd.index = 0
	sd.position = Vector2(4, 4)
	sd.relative = Vector2(-16, 0)
	root.push_input(sd)
	await process_frame
	out.append("t2_pushdrag_a=%s b=%s" % [_fmt(a.log), _fmt(b.log)])
	var up := InputEventScreenTouch.new()
	up.index = 0
	up.pressed = false
	up.position = Vector2(4, 4)
	root.push_input(up)
	await process_frame
	# emulation: touch -> mouse (Input.parse_input_event)
	a.log.clear()
	b.log.clear()
	var st2 := InputEventScreenTouch.new()
	st2.index = 0
	st2.pressed = true
	st2.position = Vector2(8, 8)
	Input.parse_input_event(st2)
	await process_frame
	out.append("t3_emul_touch held=%d a=%s b=%s emul=%d" % [
		int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)), _fmt(a.log), _fmt(b.log),
		int(Input.is_emulating_mouse_from_touch())])
	var up2 := InputEventScreenTouch.new()
	up2.index = 0
	up2.pressed = false
	up2.position = Vector2(8, 8)
	Input.parse_input_event(up2)
	await process_frame
	# emulation: mouse -> touch
	Input.set_emulate_touch_from_mouse(true)
	a.log.clear()
	b.log.clear()
	a.in_log.clear()
	Input.parse_input_event(_mb(Vector2(20, 4), true))
	await process_frame
	out.append("t4_emul_mouse a_gui=%s a_in=%s emul_t=%d" % [
		_fmt(a.log), _fmt(a.in_log), int(Input.is_emulating_touch_from_mouse())])
	Input.parse_input_event(_mb(Vector2(20, 4), false))
	await process_frame
	Input.set_emulate_touch_from_mouse(false)
	_emit("PASS r100_gui touch %s" % " ".join(out))


# ---------------------------------------------------------------- subvp
func _cell_subvp() -> void:
	var rnode := _mk_sink("R", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(rnode)
	var sv := SubViewport.new()
	_nodes.append(sv)
	sv.size = Vector2i(64, 64)
	var snode := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	sv.add_child(snode)
	root.add_child(sv)
	await process_frame
	var out: Array = []
	out.append("v0_local=%d size=%s cursor=%s" % [
		int(sv.handle_input_locally), str(sv.size), str(sv.get_mouse_position())])
	sv.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("v1_sub[%s] root=%s" % [_fmt(snode.log), _fmt(rnode.log)])
	out.append("v2_hovered=%s cursor_sub=%s cursor_root=%s" % [
		_tag_of(sv.gui_get_hovered_control()), str(sv.get_mouse_position()),
		str(root.get_mouse_position())])
	_clr([rnode, snode])
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("v3_root_push_sub[%s] root=%s" % [_fmt(snode.log), _fmt(rnode.log)])
	out.append("v4_cursors sub=%s root=%s" % [
		str(sv.get_mouse_position()), str(root.get_mouse_position())])
	var sv2 := SubViewport.new()
	_nodes.append(sv2)
	sv2.size = Vector2i(64, 64)
	sv2.handle_input_locally = false
	var s2 := _mk_sink("S2", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	sv2.add_child(s2)
	root.add_child(sv2)
	await process_frame
	sv2.push_input(_mb(Vector2(12, 12), true))
	await process_frame
	out.append("v5_local_false local=%d s2=[%s] cursor=%s" % [
		int(sv2.handle_input_locally), _fmt(s2.log), str(sv2.get_mouse_position())])
	_emit("PASS r100_gui subvp %s" % " ".join(out))


# ---------------------------------------------------------------- warp
func _cell_warp() -> void:
	var out: Array = []
	out.append("w0 dv=%s cursor=%s ds_mouse=%s" % [
		DisplayServer.get_name(), str(root.get_mouse_position()),
		str(DisplayServer.mouse_get_position())])
	root.push_input(_mm(Vector2(20, 20), Vector2(20, 20)))
	await process_frame
	out.append("w1 after_push cursor=%s ds_mouse=%s" % [
		str(root.get_mouse_position()), str(DisplayServer.mouse_get_position())])
	Input.warp_mouse(Vector2(30, 30))
	await process_frame
	out.append("w2 after_input_warp cursor=%s ds_mouse=%s" % [
		str(root.get_mouse_position()), str(DisplayServer.mouse_get_position())])
	root.warp_mouse(Vector2(40, 40))
	await process_frame
	out.append("w3 after_vp_warp cursor=%s ds_mouse=%s" % [
		str(root.get_mouse_position()), str(DisplayServer.mouse_get_position())])
	out.append("w4 mode=%d" % Input.get_mouse_mode())
	_emit("PASS r100_gui warp %s" % " ".join(out))


# ---------------------------------------------------------------- focus
func _cell_focus() -> void:
	var f := _mk_sink("F", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	f.focus_mode = Control.FOCUS_ALL
	var g := _mk_sink("G", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	g.focus_mode = Control.FOCUS_ALL
	root.add_child(f)
	root.add_child(g)
	await process_frame
	var out: Array = []
	f.grab_focus()
	await process_frame
	out.append("f0 owner=%s f_focus=%d g_focus=%d" % [
		_tag_of(root.gui_get_focus_owner()), int(f.has_focus()), int(g.has_focus())])
	var k := InputEventKey.new()
	k.keycode = KEY_A
	k.pressed = true
	_clr([f, g])
	root.push_input(k)
	await process_frame
	out.append("f1_key gui_f=%s gui_g=%s in_f=%s" % [_fmt(f.log), _fmt(g.log), _fmt(f.in_log)])
	f.handled = true
	_clr([f, g])
	root.push_input(k)
	await process_frame
	out.append("f2_handled gui_f=%s gui_g=%s" % [_fmt(f.log), _fmt(g.log)])
	f.handled = false
	g.grab_focus()
	await process_frame
	_clr([f, g])
	root.push_input(k)
	await process_frame
	out.append("f3_regrab gui_f=%s gui_g=%s owner=%s" % [
		_fmt(f.log), _fmt(g.log), _tag_of(root.gui_get_focus_owner())])
	root.gui_release_focus()
	await process_frame
	_clr([f, g])
	root.push_input(k)
	await process_frame
	out.append("f4_released gui_f=%s gui_g=%s owner=%s" % [
		_fmt(f.log), _fmt(g.log), _tag_of(root.gui_get_focus_owner())])
	_emit("PASS r100_gui focus %s" % " ".join(out))


# ---------------------------------------------------------------- render residue (vacuous-surface evidence)
func _cell_render() -> void:
	var out: Array = []
	var tex := root.get_texture()
	out.append("r0 tex_cls=%s size=%s" % [
		"-" if tex == null else tex.get_class(),
		"-" if tex == null else str(tex.get_size())])
	var img: Image = null
	if tex != null:
		img = tex.get_image()
	out.append("r1 img_null=%d" % int(img == null))
	out.append("r2 adapter=%s rd_null=%d" % [
		RenderingServer.get_video_adapter_name(), int(RenderingServer.get_rendering_device() == null)])
	out.append("r3 method=%s screens=%d ssize=%s win_size=%s" % [
		ProjectSettings.get_setting("rendering/renderer/rendering_method"),
		DisplayServer.get_screen_count(), str(DisplayServer.screen_get_size()), str(root.size)])
	var pl := PointLight2D.new()
	_nodes.append(pl)
	out.append("r4 light sh=%d filt=%d smooth=%.1f blend=%d" % [
		int(pl.shadow_enabled), pl.shadow_filter, pl.shadow_filter_smooth, pl.blend_mode])
	var gp := GPUParticles2D.new()
	_nodes.append(gp)
	out.append("r5 gpu_capture=%s" % str(gp.capture_rect()))
	_emit("PASS r100_gui render %s" % " ".join(out))


# ---------------------------------------------------------------- os/threading meta (deterministic subset)
func _cell_osmeta() -> void:
	var out: Array = []
	for cls in ["Thread", "Mutex", "Semaphore", "WorkerThreadPool", "Time"]:
		var exists := int(ClassDB.class_exists(cls))
		var nm := -1
		if exists == 1:
			nm = ClassDB.class_get_method_list(cls, true).size()
		out.append("%s[e=%d,m=%d]" % [cls, exists, nm])
	out.append("os=%s procs_gt0=%d" % [OS.get_name(), int(OS.get_processor_count() > 0)])
	out.append("wtp_has_thread_count=%d" % int(ClassDB.class_has_method("WorkerThreadPool", "get_thread_count")))
	_emit("PASS r100_gui osmeta %s" % " ".join(out))
