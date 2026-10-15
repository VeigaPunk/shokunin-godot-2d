extends SceneTree

const EXPECTED := "EXPECTED_NEGATIVE: deliberate assertion rejected"
const UNRELATED := "UNRELATED_FAULT: unrelated engine diagnostic"

func _initialize() -> void:
    var user_args := OS.get_cmdline_user_args()
    push_error(EXPECTED)
    if "--unrelated-error" in user_args:
        push_error(UNRELATED)
    quit(1)
