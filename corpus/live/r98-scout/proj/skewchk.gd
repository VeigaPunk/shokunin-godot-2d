extends SceneTree
var arm := ""
func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()
class RT:
	extends Node2D
	var draws := 0
	func _draw() -> void:
		draws += 1
func _run() -> void:
	var t := RT.new()
	root.add_child(t)
	for i in 3: await process_frame
	var out: Array = []
	var step := func(label: String, f: Callable) -> void:
		var d0 := t.draws
		f.call()
		for i in 3: await process_frame
		out.append("%s=%d" % [label, t.draws - d0])
	await step.call("skew_first", func(): t.skew = 0.2)
	await step.call("rot", func(): t.rotation = 0.5)
	await step.call("scale", func(): t.scale = Vector2(2, 2))
	await step.call("skew_again", func(): t.skew = 0.3)
	await step.call("pos", func(): t.position = Vector2(1, 1))
	await step.call("skew_third", func(): t.skew = 0.4)
	await step.call("texfilter", func(): t.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST)
	await step.call("skew_fourth", func(): t.skew = 0.5)
	print("SKEWCHK " + ",".join(out))
	quit()
