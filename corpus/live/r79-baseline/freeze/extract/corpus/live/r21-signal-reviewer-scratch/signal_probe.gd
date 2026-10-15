extends SceneTree
func _initialize():
    print("SIGNAL_REVIEW_SIGNATURE")
    call_deferred("stay_alive")
func stay_alive():
    while true:
        await process_frame
