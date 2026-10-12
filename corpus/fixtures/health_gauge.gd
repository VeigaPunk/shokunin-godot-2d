extends SceneTree

signal health_changed(value: float)

var gauge: TextureProgressBar
var value_changed_count := 0
var last_value_changed := -1.0

func _initialize() -> void:
    var hud := CanvasLayer.new()
    gauge = TextureProgressBar.new()
    gauge.min_value = 0.0
    gauge.max_value = 100.0
    gauge.value = 100.0
    hud.add_child(gauge)
    root.add_child(hud)
    gauge.value_changed.connect(_on_gauge_value_changed)
    if not OS.get_cmdline_user_args().has("--disconnect-signal"):
        health_changed.connect(_on_health_changed)
    await process_frame
    if not gauge.is_inside_tree() or gauge.min_value != 0.0 or gauge.max_value != 100.0 or gauge.value != 100.0:
        push_error("Health gauge setup assertion failed: expected in-tree range=0..100 value=100")
        quit(2)
        return
    health_changed.emit(35.0)
    if gauge.value != 35.0 or value_changed_count != 1 or last_value_changed != 35.0:
        print("HEALTH_GAUGE_NEGATIVE actual_value=%s value_changed_count=%d receipt=%s" % [gauge.value, value_changed_count, last_value_changed])
        push_error("Health gauge assertion failed: expected in-tree TextureProgressBar value=35 value_changed=1 receipt=35")
        quit(2)
        return
    print("PASS health_gauge in_tree=true range=0..100 value=35 value_changed_count=1 receipt=35")
    quit(0)

func _on_health_changed(value: float) -> void:
    gauge.value = value

func _on_gauge_value_changed(value: float) -> void:
    value_changed_count += 1
    last_value_changed = value
