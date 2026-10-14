extends SceneTree
func _initialize():
    print("CRASH_SCOUT: pre-exit signature")
    var args = OS.get_cmdline_user_args()
    if "--hold" in args:
        var until = Time.get_ticks_msec() + 15000
        while Time.get_ticks_msec() < until:
            OS.delay_msec(25)
        quit(2)
    else:
        quit(2)
