extends SceneTree

signal score_changed(value: int)

var score_label: Label

func _initialize() -> void:
    var hud := CanvasLayer.new()
    score_label = Label.new()
    score_label.text = "Score: 0"
    hud.add_child(score_label)
    root.add_child(hud)
    if not OS.get_cmdline_user_args().has("--disconnect-signal"):
        score_changed.connect(_on_score_changed)
    await process_frame
    if not score_label.is_inside_tree() or score_label.text != "Score: 0":
        push_error("UI setup assertion failed: HUD label not in tree with initial text=Score: 0")
        quit(2)
        return
    var connected := score_changed.is_connected(_on_score_changed)
    score_changed.emit(7)
    if score_label.text != "Score: 7" or not score_label.is_inside_tree():
        push_error("UI assertion failed: expected in-tree HUD text=Score: 7")
        quit(2)
        return
    print("PASS ui_signal connected=%s hud_in_tree=true initial=Score: 0 hud_text=Score: 7" % connected)
    quit(0)

func _on_score_changed(value: int) -> void:
    score_label.text = "Score: %d" % value
