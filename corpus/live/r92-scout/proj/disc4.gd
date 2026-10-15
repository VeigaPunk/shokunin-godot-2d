extends SceneTree
var arm := ""
func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")
func _run() -> void:
	print("arm=%s" % arm)
	var layer := TileMapLayer.new()
	root.add_child(layer)
	print("R92 nullts2 tileset_null=%s" % (1 if layer.tile_set == null else 0))
	match arm:
		"fresh_td":
			print("R92 nullts2 used=%d" % layer.get_used_cells().size())
			print("R92 nullts2 about_to_call")
			var td = layer.get_cell_tile_data(Vector2i(0, 0))
			print("R92 nullts2 td=%s" % ("null" if td == null else "obj"))
		"setcell_td":
			layer.set_cell(Vector2i(0, 0), 0, Vector2i(0, 0), 0)
			print("R92 nullts2 about_to_call")
			var td = layer.get_cell_tile_data(Vector2i(0, 0))
			print("R92 nullts2 td=%s" % ("null" if td == null else "obj"))
		"setcell_only":
			layer.set_cell(Vector2i(0, 0), 0, Vector2i(0, 0), 0)
			print("R92 nullts2 set_ok used=%d" % layer.get_used_cells().size())
		"fresh_used":
			print("R92 nullts2 used=%d src=%d" % [layer.get_used_cells().size(), layer.get_cell_source_id(Vector2i(0, 0))])
		"fresh_map":
			print("R92 nullts2 local=%s" % str(layer.map_to_local(Vector2i(0, 0))))
		_:
			print("FAIL unknown")
			quit(1)
	print("PASS disc4 %s" % arm)
	quit(0)
