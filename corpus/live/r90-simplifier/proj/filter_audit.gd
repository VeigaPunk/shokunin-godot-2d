extends SceneTree
# r90-simplifier audit probe (lane-local, NOT a fixture): which method-filter term
# in _arm_props contributes unique matches on this build? Prints, per term, the
# matching methods and the unique (only-this-term) matches.
func _initialize() -> void:
	var terms := ["impulse", "force", "torque", "state", "gravity", "damp", "constant"]
	var all: Array = []
	for m in ClassDB.class_get_method_list("RigidBody2D"):
		all.append(String(m["name"]))
	for t in terms:
		var hits: Array = []
		for n in all:
			if n.contains(t):
				hits.append(n)
		print("TERM %s n=%d uniq=%s" % [t, hits.size(), str(_uniq(hits, terms, t))])
	# the shipped filter result, for byte comparison
	var shipped: Array = []
	for n in all:
		if n.contains("impulse") or n.contains("force") or n.contains("torque") \
				or n.contains("state") or n.contains("gravity") or n.contains("damp") \
				or n.contains("constant"):
			shipped.append(n)
	shipped.sort()
	var no_constant: Array = []
	for n in all:
		if n.contains("impulse") or n.contains("force") or n.contains("torque") \
				or n.contains("state") or n.contains("gravity") or n.contains("damp"):
			no_constant.append(n)
	no_constant.sort()
	print("SHIPPED=[%s]" % "|".join(shipped))
	print("NO_CONSTANT=[%s]" % "|".join(no_constant))
	print("IDENTICAL=%s" % str(shipped == no_constant))
	quit()

func _uniq(hits: Array, terms: Array, self_term: String) -> Array:
	var out: Array = []
	for h in hits:
		var only_here := true
		for t in terms:
			if t != self_term and h.contains(t):
				only_here = false
		if only_here:
			out.append(h)
	return out
