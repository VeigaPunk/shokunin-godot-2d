extends SceneTree
func _initialize() -> void:
	_run.call_deferred()
class RT:
	extends Node2D
	var draws := 0
	var ev: Array = []
	func _draw() -> void:
		draws += 1
		ev.append("d@pf%d" % Engine.get_process_frames())
func _run() -> void:
	var t := RT.new()
	root.add_child(t)
	for i in 3: await process_frame
	t.ev.clear()
	t.hide()
	await process_frame
	print("SHOWCHK after_hide ", t.ev, " draws=", t.draws)
	t.ev.clear()
	t.show()
	for i in 5:
		await process_frame
		print("SHOWCHK frame", i, " ev=", t.ev, " draws=", t.draws)
	t.ev.clear()
	t.visible = false
	await process_frame
	t.ev.clear()
	t.visible = true
	for i in 3:
		await process_frame
		print("SHOWCHK v2 frame", i, " ev=", t.ev, " draws=", t.draws)
	quit()
