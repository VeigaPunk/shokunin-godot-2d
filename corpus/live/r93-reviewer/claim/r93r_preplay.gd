extends SceneTree
# r93-reviewer mechanism probe (NOT part of the landing): is the value read
# after the first awaited process frame the node's PRE-PLAY value or the
# animation's t=0 pose? Node starts at x=5, animation key t=0 is 0.0 -> the two
# hypotheses predict 5.0 vs 0.0. Read-only w.r.t. the fixtures.

func _initialize() -> void:
	var target := Node2D.new()
	target.name = "T"
	root.add_child(target)
	target.position.x = 5.0
	var player := AnimationPlayer.new()
	player.name = "AP"
	target.add_child(player)
	var lib := AnimationLibrary.new()
	var anim := Animation.new()
	anim.length = 1.0
	var tr := anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(tr, NodePath(".:position:x"))
	anim.track_insert_key(tr, 0.0, 0.0)
	anim.track_insert_key(tr, 1.0, 100.0)
	lib.add_animation("move", anim)
	player.add_animation_library("", lib)
	await process_frame
	var pre := target.position.x
	player.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE
	player.play("move")
	var at_play := target.position.x
	await process_frame
	var after1 := target.position.x
	await process_frame
	var after2 := target.position.x
	await process_frame
	var after3 := target.position.x
	print("PASS r93r_preplay pre=", pre, " at_play=", at_play, " after1=", after1,
		" after2=", after2, " after3=", after3,
		" after1_is_t0_pose=", after1 == 0.0, " after1_is_preplay=", after1 == pre)
	quit(0)
