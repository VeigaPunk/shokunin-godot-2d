extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var vi := Engine.get_version_info()
	print("VER17 marker engine.string=%s" % vi["string"])
	print("VER17 marker engine.major=%d engine.minor=%d engine.patch=%d engine.hex=%d engine.status=%s" % [
		vi["major"], vi["minor"], vi["patch"], vi["hex"], vi["status"]])
	print("VER17 marker engine.build=%s engine.hash=%s engine.timestamp=%d" % [
		vi["build"], vi["hash"], vi["timestamp"]])
	print("VER17 marker display_server=%s headless_hint=%s" % [
		DisplayServer.get_name(), OS.has_feature("headless")])
	print("VER17 marker os=%s vp=%s tps=%d" % [
		OS.get_name(), str(root.get_visible_rect().size), Engine.physics_ticks_per_second])
	print("VER17 marker render_pre method=%s driver=%s adapter=%s" % [
		RenderingServer.get_current_rendering_method(),
		RenderingServer.get_current_rendering_driver_name(),
		RenderingServer.get_video_adapter_name()])
	await process_frame
	print("VER17 marker render_post method=%s driver=%s adapter=%s" % [
		RenderingServer.get_current_rendering_method(),
		RenderingServer.get_current_rendering_driver_name(),
		RenderingServer.get_video_adapter_name()])
	quit(0)
