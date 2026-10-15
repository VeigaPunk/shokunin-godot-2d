extends SceneTree

const BASELINE := Color(0.7, 0.8, 0.9, 1.0)
const FLASH := Color(1.0, 0.2, 0.1, 1.0)
const MAX_OBSERVATION_FRAMES := 90

func _initialize() -> void:
    var skip_start := "--no-tween" in OS.get_cmdline_user_args()
    var target := Node2D.new()
    target.name = "FlashTarget"
    target.modulate = BASELINE
    root.add_child(target)
    await process_frame

    if not skip_start:
        var tween := target.create_tween()
        tween.tween_property(target, "modulate", FLASH, 0.2)
        tween.tween_property(target, "modulate", BASELINE, 0.2)

    var transient_seen := false
    var transient_snapshot := BASELINE
    var baseline_restored := false
    var frames_observed := 0
    for frame in range(MAX_OBSERVATION_FRAMES):
        await process_frame
        frames_observed += 1
        var snapshot: Color = target.modulate
        if not snapshot.is_equal_approx(BASELINE):
            transient_seen = true
            transient_snapshot = snapshot
        elif transient_seen:
            baseline_restored = true
            break

    if not (transient_seen and baseline_restored):
        push_error("TWEEN ASSERTION FAILED: modulate did not show flash then return to baseline, transient_seen=%s baseline_restored=%s frames_observed=%s final_modulate=%s" % [transient_seen, baseline_restored, frames_observed, target.modulate])
        quit(2)
        return

    print("PASS tween_flash transient_modulate=%s baseline_modulate=%s frames_observed=%s" % [transient_snapshot, target.modulate, frames_observed])
    quit(0)
