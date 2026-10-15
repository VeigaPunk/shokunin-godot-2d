extends SceneTree
# r88 BOUNDARY seat — VisibleOnScreenNotifier2D / Enabler2D on headless: does any positive
# ever fire? Base mirror + variants (huge rect, camera, SubViewport) + force_draw arm.
# Launch: godot --headless --path proj --script res://b88_vis.gd -- --arm=<arm>

var arm := ""
var _vis_events: Array = []
var _vis_pf := 0

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	if arm.is_empty():
		print("R88B ARM_MISSING")
		quit(1)
		return
	print("R88B arm=%s" % arm)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"base": _arm_base()
		"variants": _arm_variants()
		"forcedraw": _arm_forcedraw()
		_:
			print("R88B unknown_arm=%s" % arm)
			quit(2)

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _body(x: float, y: float) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	cs.shape = circle
	b.add_child(cs)
	b.position = Vector2(x, y)
	return b

func _diag() -> String:
	return "display=%s root_size=%s vis_rect=%s" % [
		DisplayServer.get_name(), root.size, root.get_visible_rect()]

# Exact mirror of the scout's _arm_vis_not + diagnostics.
func _arm_base() -> void:
	var vn := VisibleOnScreenNotifier2D.new()
	vn.rect = Rect2(-16, -16, 32, 32)
	vn.screen_entered.connect(func(): _vis_events.append("in@%d" % _vis_pf))
	vn.screen_exited.connect(func(): _vis_events.append("out@%d" % _vis_pf))
	var b := _body(0, 0)
	b.add_child(vn)
	b.freeze = true
	root.add_child(b)
	var en := VisibleOnScreenEnabler2D.new()
	en.rect = Rect2(-8, -8, 16, 16)
	var target := Node2D.new()
	en.enable_node_path = NodePath("../target")
	var holder := Node2D.new()
	holder.name = "h"
	holder.add_child(en)
	holder.add_child(target)
	target.name = "target"
	target.set_process(false)
	root.add_child(holder)
	print("R88B vis base on_screen0=%s en_onscreen=%s vn_visible_in_tree=%s vn_rect=%s vn_gpos=%s %s" % [
		vn.is_on_screen(), en.is_on_screen(), vn.is_visible_in_tree(),
		vn.rect, _v2(vn.global_position), _diag()])
	for i in 30:
		await physics_frame
		_vis_pf += 1
	b.global_position = Vector2(500, 0)
	for i in 10:
		await physics_frame
		_vis_pf += 1
	b.global_position = Vector2(0, 0)
	for i in 10:
		await physics_frame
		_vis_pf += 1
	print("R88B vis base events=%s on_screen_end=%s enabler_proc=%s en_end=%s" % [
		_vis_events, vn.is_on_screen(), target.is_processing(), en.is_on_screen()])
	quit()

# Positive-arm hunt: huge rect, camera, SubViewport host.
func _arm_variants() -> void:
	var vn1 := VisibleOnScreenNotifier2D.new()
	vn1.rect = Rect2(-100000, -100000, 200000, 200000)
	vn1.screen_entered.connect(func(): _vis_events.append("huge_in"))
	root.add_child(vn1)
	await process_frame
	var s1 := vn1.is_on_screen()
	var cam := Camera2D.new()
	cam.position = Vector2(0, 0)
	root.add_child(cam)
	cam.make_current()
	await process_frame
	var s2 := vn1.is_on_screen()
	var sv := SubViewport.new()
	sv.size = Vector2i(320, 240)
	root.add_child(sv)
	var vn3 := VisibleOnScreenNotifier2D.new()
	vn3.rect = Rect2(-16, -16, 32, 32)
	vn3.screen_entered.connect(func(): _vis_events.append("sv_in"))
	sv.add_child(vn3)
	await process_frame
	var s3 := vn3.is_on_screen()
	var en := VisibleOnScreenEnabler2D.new()
	en.rect = Rect2(-100000, -100000, 200000, 200000)
	var tgt := Node2D.new()
	tgt.name = "tgt"
	var holder := Node2D.new()
	holder.name = "hv"
	holder.add_child(en)
	holder.add_child(tgt)
	en.enable_node_path = NodePath("../tgt")
	tgt.set_process(false)
	root.add_child(holder)
	await process_frame
	var en_s := en.is_on_screen()
	for i in 30:
		await physics_frame
		_vis_pf += 1
	print("R88B vis variants s1_huge=%s s2_camera=%s s3_subviewport=%s en_onscreen=%s tgt_proc=%s events=%s %s" % [
		s1, s2, s3, en_s, tgt.is_processing(), _vis_events, _diag()])
	quit()

# Can a forced render frame ever emit visibility? Isolated arm (force_draw may block).
func _arm_forcedraw() -> void:
	var vn := VisibleOnScreenNotifier2D.new()
	vn.rect = Rect2(-16, -16, 32, 32)
	vn.screen_entered.connect(func(): _vis_events.append("fd_in"))
	root.add_child(vn)
	await process_frame
	print("R88B vis forcedraw pre=%s %s" % [vn.is_on_screen(), _diag()])
	RenderingServer.force_draw()
	print("R88B vis forcedraw post_force=%s events=%s" % [vn.is_on_screen(), _vis_events])
	await process_frame
	print("R88B vis forcedraw post_frame=%s events=%s" % [vn.is_on_screen(), _vis_events])
	quit()
