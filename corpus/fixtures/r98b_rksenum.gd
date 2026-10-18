extends SceneTree
# r98b supplementary ONE-OFF — enumerate the exact class where the scout's
# claimed R*K*S product differs from the engine's Transform2D(r, s, k, p).
# Not part of the batch matrix; receipts land in runs/rksenum/.

func _initialize() -> void:
	_run.call_deferred()

func _it(key: String, value: String) -> void:
	print("R98BRKS %s=%s" % [key, value])

func _tm(t: Transform2D) -> String:
	return "(%.4f,%.4f;%.4f,%.4f)" % [t.x.x, t.x.y, t.y.x, t.y.y]

func _run() -> void:
	var n := Node2D.new()
	root.add_child(n)
	await process_frame
	var rots: Array = [0.0, 0.3, PI / 2.0, -1.2, 4.0]
	var scales: Array = [Vector2(1, 1), Vector2(2, 3), Vector2(-1, 1), Vector2(1, -1),
			Vector2(-2, -3), Vector2(0, 0), Vector2(0, 1), Vector2(1, 0)]
	var skews: Array = [0.0, 0.5, -0.5, PI / 4.0, 2.5]
	var fails: Array = []
	var examples := 0
	var sign_pairs := {}
	var max_diff := 0.0
	var idx := 0
	for r in rots:
		for s in scales:
			for k in skews:
				n.rotation = r
				n.scale = s
				n.skew = k
				var t := n.get_transform()
				var ctor := Transform2D(r, s, k, Vector2.ZERO)
				var rks := Transform2D(r, Vector2.ONE, 0.0, Vector2.ZERO) \
						* Transform2D(0.0, Vector2.ONE, k, Vector2.ZERO) \
						* Transform2D(0.0, s, 0.0, Vector2.ZERO)
				var rsk := Transform2D(r, Vector2.ONE, 0.0, Vector2.ZERO) \
						* Transform2D(0.0, s, 0.0, Vector2.ZERO) \
						* Transform2D(0.0, Vector2.ONE, k, Vector2.ZERO)
				var degenerate: bool = s.x == 0.0 or s.y == 0.0
				if ctor != rks and not degenerate:
					var key := "%s%s" % [("+" if s.x > 0 else "-"), ("+" if s.y > 0 else "-")]
					sign_pairs[key] = int(sign_pairs.get(key, 0)) + 1
					fails.append("%d(r=%.2f,s=%.2f,%.2f,k=%.2f)" % [idx, r, s.x, s.y, k])
					for pair in [[ctor.x.x, rks.x.x], [ctor.x.y, rks.x.y],
							[ctor.y.x, rks.y.x], [ctor.y.y, rks.y.y]]:
						max_diff = max(max_diff, absf(pair[0] - pair[1]))
					if examples < 3:
						examples += 1
						_it("ex%d" % examples, "idx=%d t=%s ctor=%s rks=%s rsk_eq=%s" % [
							idx, _tm(t), _tm(ctor), _tm(rks), str(ctor == rsk)])
				idx += 1
	_it("combos", str(idx))
	_it("nz_fail_n", str(fails.size()))
	var sparts: Array = []
	for k in sign_pairs.keys():
		sparts.append("%s=%d" % [k, sign_pairs[k]])
	var sp := ",".join(sparts)
	_it("sign_pairs", sp)
	_it("max_abs_diff", "%.9f" % max_diff)
	_it("fail_list", "|".join(fails))
	print("PASS r98b_rksenum nz_fail_n=%d sign_pairs=%s" % [fails.size(), sp])
	quit()
