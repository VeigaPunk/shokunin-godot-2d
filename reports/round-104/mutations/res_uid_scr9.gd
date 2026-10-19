extends SceneTree
const TAG := "[r104R1i]"
func _dump(l: String, v) -> void:
	print("%s %s=%s" % [TAG, l, str(v)])
func _initialize() -> void:
	var alpha := "abcdefghijklmnopqrstuvwxyz0123456789"
	var vals := {}
	var out := []
	for i in range(alpha.length()):
		var c := alpha[i]
		var id := ResourceUID.text_to_id("uid://" + c)
		vals[c] = id
		out.append("%s=%d" % [c, id])
	_dump("single_char_values", " ".join(out))
	# which chars are actually accepted
	var bad := []
	for i in range(128):
		var c := char(i)
		if c == " " or c == "\n" or c == "\t" or c == "/" or c == ":":
			continue
		var id := ResourceUID.text_to_id("uid://" + c)
		if id < 0:
			bad.append(c)
	_dump("rejected_single_chars", " ".join(bad))
	# positional: is it base-32 big-endian?
	for s in ["a", "b", "aa", "ab", "ba", "bb", "a0", "0a", "10", "0", "1", "z", "zz", "100", "vvv"]:
		var id := ResourceUID.text_to_id("uid://" + s)
		_dump("pos", "%s = %d  text=%s" % [s, id, ResourceUID.id_to_text(id)])
	# canonical emission range: which ids emit '0'/'1'?
	var emitted := {}
	for i in [0,1,24,25,26,27,31,32,33,34,35,1023,1024,32767,32768]:
		emitted[str(i)] = ResourceUID.id_to_text(i)
	var pairs := []
	for k in emitted:
		pairs.append("%s->%s" % [k, emitted[k]])
	_dump("canonical_emission", " ".join(pairs))
	print("PASS res_uid_scr9 arm=alphabet")
	quit(0)
