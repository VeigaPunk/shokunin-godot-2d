extends Node

func _ready() -> void:
    print("EXPORT_LAUNCH_READY scene=fixture")
    get_tree().quit()
