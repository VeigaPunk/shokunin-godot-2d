extends SceneTree
# r93 VERIFIER independent probe (seat-owned, untracked) — measures the two
# laws the committed rows encode, OUTSIDE the committed fixtures:
#   (1) await N process_frame => N-1 applied IDLE steps (general N, not just N=1)
#   (2) DEFERRED method-callback flush routes (process frame AND physics frame)
# Prints one machine-readable line per section; never writes anything.

func _anim(keys: Array, length := 1.0) -> Animation:
	var a := Animation.new()
	a.length = length
	var tr := a.add_track(Animation.TYPE_VALUE)
	a.track_set_path(tr, NodePath(".:position:x"))
	for k in keys:
		a.track_insert_key(tr, k[0], k[1])
	return a

class MT extends Node2D:
	var calls: Array = []
	func notify(v: int) -> void:
		calls.append(v)

func _initialize() -> void:
	# ---- (1) N-1 await law -------------------------------------------------
	var t := Node2D.new()
	t.name = "T"
	root.add_child(t)
	var p := AnimationPlayer.new()
	p.name = "AP"
	t.add_child(p)
	var lib := AnimationLibrary.new()
	lib.add_animation("move", _anim([[0.0, 0.0], [1.0, 100.0]]))
	p.add_animation_library("", lib)
	await process_frame
	p.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE
	p.play("move")
	var pos: Array = []
	var dl: Array = []
	for i in range(6):
		var d := root.get_process_delta_time()
		await process_frame
		pos.append(t.position.x)
		dl.append(d)
	p.stop()
	var poss: Array[String] = []
	var dls: Array[String] = []
	for v in pos:
		poss.append(str(v))
	for v in dl:
		dls.append(str(v))
	print("R93V nminus1 pos=[", ",".join(poss), "] deltas=[", ",".join(dls), "]",
		" max_fps=", Engine.max_fps, " fixed=", OS.get_cmdline_user_args())

	# ---- (2) DEFERRED flush routes ----------------------------------------
	var mt := MT.new()
	mt.name = "MT"
	root.add_child(mt)
	var anim := Animation.new()
	anim.length = 1.0
	var trm := anim.add_track(Animation.TYPE_METHOD)
	anim.track_set_path(trm, NodePath("."))
	anim.track_insert_key(trm, 0.2, {"method": "notify", "args": [7]})
	anim.track_insert_key(trm, 0.5, {"method": "notify", "args": [8]})
	var pl := AnimationPlayer.new()
	pl.name = "MP"
	mt.add_child(pl)
	var lib2 := AnimationLibrary.new()
	lib2.add_animation("m", anim)
	pl.add_animation_library("", lib2)
	await process_frame
	pl.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL
	pl.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_DEFERRED
	# route A: process frame
	pl.play("m")
	pl.advance(1.0)
	var a1: Array = mt.calls.duplicate()
	await process_frame
	var a2: Array = mt.calls.duplicate()
	mt.calls.clear()
	# route B: physics frame
	pl.stop()
	pl.play("m")
	pl.advance(1.0)
	var b1: Array = mt.calls.duplicate()
	await physics_frame
	var b2: Array = mt.calls.duplicate()
	mt.calls.clear()
	# route C: two manual advances, one flush
	pl.stop()
	pl.play("m")
	pl.advance(0.3)
	pl.advance(0.8)
	var c1: Array = mt.calls.duplicate()
	await process_frame
	var c2: Array = mt.calls.duplicate()
	mt.calls.clear()
	# route D: IMMEDIATE fires inside advance()
	pl.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
	pl.stop()
	pl.play("m")
	pl.advance(1.0)
	var d1: Array = mt.calls.duplicate()
	await process_frame
	var d2: Array = mt.calls.duplicate()
	print("R93V deferred proc=[", _ps(a1), "->", _ps(a2), "]",
		" phys=[", _ps(b1), "->", _ps(b2), "]",
		" two_adv=[", _ps(c1), "->", _ps(c2), "]",
		" immediate=[", _ps(d1), "->", _ps(d2), "]")
	quit(0)

func _ps(a: Array) -> String:
	var parts: Array[String] = []
	for v in a:
		parts.append(str(v))
	return ",".join(parts)
