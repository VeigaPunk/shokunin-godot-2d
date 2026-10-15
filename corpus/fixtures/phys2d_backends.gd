extends SceneTree
# r86 fixture — 2D physics backend-select lattice (read-only, nested boot).
# One arm per process, exactly the battery's launch shape:
#   godot --headless --path <scratch> --script res://phys2d_backends.gd -- --arm=<name>
# Boot-selected state (physics/2d/physics_engine, physics/2d/run_on_separate_thread)
# is fixed before any script statement runs, so each boot-variant measurement
# launches a child Godot process into a generated minimal project under
# user://r86bt/ and reads back split stdout/stderr capture files — the parent
# prints digests only and never echoes child streams, so engine ERROR frames stay
# inside the child captures and the parent's own stderr stays empty.
# Prints one final `PASS phys2d_backends <arm> ...` line.
# No object ids / addresses / RIDs are printed (byte-stability).
# The `match arm:` dispatch in _run is the sole arm index (8 arms);
# per-arm measured classes live in r86-author §2.
# Pass --keep to leave the generated child projects in place (receipt harvest).

var arm := ""
var _keep := false
var _boot_dirs: Array = []

const LAT := [
	["default", []],
	["gp2d", ['2d/physics_engine="GodotPhysics2D"']],
	["dummy", ['2d/physics_engine="Dummy"']],
	["jolt", ['2d/physics_engine="Jolt Physics"']],
	["garbage", ['2d/physics_engine="garbage_xyz"']],
	["empty", ['2d/physics_engine=""']],
]
const NAMES2D := ["GodotPhysics2D", "Dummy", "Jolt Physics", "garbage_xyz", ""]
const NAMES3D := ["Jolt Physics", "GodotPhysics3D", "Dummy", "garbage_xyz"]
const THREAD_ON := ['2d/run_on_separate_thread=true']

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a == "--keep":
			_keep = true
	call_deferred("_run")

func _run() -> void:
	match arm:
		"census": _arm_census()
		"lattice": _arm_lattice()
		"jolt3d_live": _arm_jolt3d_live()
		"xcheck": _arm_xcheck()
		"gate_matrix": _arm_gate_matrix()
		"gate_duality": _arm_gate_duality()
		"dummy_degenerate": _arm_dummy_degenerate()
		"dummy_timeout": _arm_dummy_timeout()
		_: _fail("unknown_arm")

func _fail(reason: String) -> void:
	print("FAIL phys2d_backends %s reason=%s" % [arm, reason])
	quit(1)

func _finish(line: String) -> void:
	_cleanup()
	print("PASS phys2d_backends %s %s" % [arm, line])
	quit(0)

func _cleanup() -> void:
	if _keep:
		return
	for d in _boot_dirs:
		OS.execute("rm", ["-rf", d], [], false, false)

# -- nested-boot machinery ----------------------------------------------------

func _work_root() -> String:
	return OS.get_user_data_dir() + "/r86bt"

# Boot a fresh Godot process in a generated minimal project. Returns
# {rc, err, err_bytes, fields, at} — fields is the child's
# `R86C key=value` report parsed key->value (values may contain spaces),
# at is the list of stripped `at:` payload lines from the child's stderr.
func _boot(tag: String, phys_lines: PackedStringArray, child_arg: String, bound_s: int) -> Dictionary:
	var cdir := _work_root() + "/" + arm + "/" + tag
	_boot_dirs.append(_work_root() + "/" + arm)
	DirAccess.make_dir_recursive_absolute(cdir)
	# Purge any stale capture before spawn (r86-critic F7): a leftover
	# out/err/rc set must never be re-read as fresh evidence.
	for stale in ["out.txt", "err.txt", "rc.txt"]:
		if FileAccess.file_exists(cdir + "/" + stale):
			DirAccess.remove_absolute(cdir + "/" + stale)
	var pg := FileAccess.open(cdir + "/project.godot", FileAccess.WRITE)
	pg.store_string("[application]\nconfig/name=\"R86BT\"\nconfig/features=PackedStringArray(\"4.7\")\n")
	if phys_lines.size() > 0:
		pg.store_string("\n[physics]\n")
		for l in phys_lines:
			pg.store_string(l + "\n")
	pg.close()
	var cg := FileAccess.open(cdir + "/child.gd", FileAccess.WRITE)
	cg.store_string(_child_src())
	cg.close()
	var out_f := cdir + "/out.txt"
	var err_f := cdir + "/err.txt"
	var rc_f := cdir + "/rc.txt"
	# OS.execute wraps the call in its own `sh -c --` layer, so a bare `$?` would
	# be expanded by the WRAPPER (always 0) before the inner sh runs; the escaped
	# `\$?` survives to the inner sh and records the child's real exit code.
	var cmd := "timeout %d \"%s\" --headless --path \"%s\" --script res://child.gd -- %s >\"%s\" 2>\"%s\"; echo \\$? >\"%s\"" % [
		bound_s, OS.get_executable_path(), cdir, child_arg, out_f, err_f, rc_f]
	var t0 := Time.get_ticks_msec()
	var xrc := OS.execute("/bin/sh", ["-c", cmd], [], false, false)
	var dur_ms := int(Time.get_ticks_msec() - t0)
	var out_t := FileAccess.get_file_as_string(out_f)
	var err_t := FileAccess.get_file_as_string(err_f)
	var rc_s := FileAccess.get_file_as_string(rc_f).strip_edges()
	var fields := {}
	for line in out_t.split("\n"):
		if line.begins_with("R86C "):
			var kv := line.substr(5)
			var eq := kv.find("=")
			if eq > 0:
				fields[kv.substr(0, eq)] = kv.substr(eq + 1)
	var ats: Array = []
	for line in err_t.split("\n"):
		var s := line.strip_edges()
		if s.begins_with("at: "):
			ats.append(s.substr(4))
	return {"rc": (-998 if xrc != 0 else
			(int(rc_s) if rc_s.is_valid_int() else -999)),
		"err": err_t,
		"err_bytes": FileAccess.get_file_as_bytes(err_f).size(),
		"fields": fields, "at": ats, "dur_ms": dur_ms}

func _err_count(err: String) -> int:
	var n := 0
	for line in err.split("\n"):
		if "ERROR:" in line:
			n += 1
	return n

# 12-frame drop distances are frame-count coupled (17.867 vs 21.104
# both realized) — emit the motion class, not the jittered magnitude.
func _mvclass(m) -> String:
	var s := str(m)
	if not s.is_valid_float():
		return s
	var v := s.to_float()
	return "zero" if v == 0.0 else ("pos" if v > 1.0 else "tiny")

func _slot(r: Dictionary, inner: String) -> String:
	return "{%s,rc=%d,errB=%d}" % [inner, r["rc"], r["err_bytes"]]

# Unique GDScript user-frame names from a child's stderr backtraces, in
# order — `[N] fn (res://child.gd:L)` lines. Provenance evidence the bare
# ERROR count cannot carry (r86-critic F2).
func _frames(err: String) -> String:
	var seen: Array = []
	for line in err.split("\n"):
		var s := line.strip_edges()
		if s.begins_with("[") and "child.gd" in s:
			var fn: String = s.split(" ", true, 1)[1].split(" ")[0]
			if fn not in seen:
				seen.append(fn)
	return ",".join(seen)

# First `at:` entry containing a needle (engine frame or user frame).
func _at_pick(ats: Array, needle: String) -> String:
	for a in ats:
		if needle in a:
			return a
	return "<none>"

# -- arms ---------------------------------------------------------------------

func _arm_census() -> void:
	# No children: everything here is read from the battery's own boot (DEFAULT).
	var h2 := "<absent>"
	var h3 := "<absent>"
	var j2 := 0
	var j3 := 0
	for p in ProjectSettings.get_property_list():
		var nm := str(p.get("name", ""))
		if nm == "physics/2d/physics_engine":
			h2 = str(p.get("hint_string"))
		elif nm == "physics/3d/physics_engine":
			h3 = str(p.get("hint_string"))
		elif nm.begins_with("physics/jolt_physics_2d/"):
			j2 += 1
		elif nm.begins_with("physics/jolt_physics_3d/"):
			j3 += 1
	var ces: Array = []
	for c in ["GodotPhysicsServer2D", "JoltPhysicsServer2D",
			"GodotPhysicsServer3D", "JoltPhysicsServer3D",
			"JoltPhysicsDirectSpaceState2D"]:
		ces.append("%s=%s" % [c, str(ClassDB.class_exists(c))])
	var enums: Array = []
	var probes := ["get_servers_count", "get_server_count",
			"get_server_name", "find_server_id", "has_server"]
	for mgr in ["PhysicsServer2DManager", "PhysicsServer3DManager"]:
		var sing = Engine.get_singleton(mgr)
		var have := 0
		var own: Array = []
		for m in ClassDB.class_get_method_list(mgr, true):
			own.append(str(m.get("name")))
		own.sort()
		for probe in probes:
			if sing != null and sing.has_method(probe):
				have += 1
		enums.append("%s={own=[%s],enum%d=%d}" % [mgr, ",".join(own), probes.size(), have])
	_finish("census self_cfg=[%s] hint2d=[%s] hint3d=[%s] jolt2d_ns=%d jolt3d_ns=%d %s ce=[%s]" % [
		str(ProjectSettings.get_setting("physics/2d/physics_engine")),
		h2, h3, j2, j3, " ".join(enums), ",".join(ces)])

func _arm_lattice() -> void:
	# Six stored 2D engine values; the readback discriminates stored value vs
	# the backend actually instantiated (dss class + space validity + drop test).
	var parts: Array = []
	for row in LAT:
		var r := _boot("lat_" + row[0], PackedStringArray(row[1]), "--mode=probe", 15)
		var f: Dictionary = r["fields"]
		parts.append("%s%s" % [row[0], _slot(r, "stored=%s,has=%s,dss=%s,valid=%s,mv=%s" % [
			f.get("stored", "<?>"), f.get("stored_has", "<?>"), f.get("dss", "<?>"),
			f.get("valid", "<?>"), _mvclass(f.get("moved", "<?>"))])])
	_finish("lattice " + " ".join(parts))

func _arm_jolt3d_live() -> void:
	# Positive control: a real Jolt install must move the dss-class instrument.
	var rj := _boot("j3d", PackedStringArray(['3d/physics_engine="Jolt Physics"']), "--mode=probe3d", 15)
	var rd := _boot("d3d", PackedStringArray(), "--mode=probe3d", 15)
	var fj: Dictionary = rj["fields"]
	var fd: Dictionary = rd["fields"]
	_finish("jolt3d_live jolt%s default%s" % [
		_slot(rj, "stored3d=%s,dss3=%s,valid3=%s" % [fj.get("stored3d", "<?>"), fj.get("dss3", "<?>"), fj.get("valid3d", "<?>")]),
		_slot(rd, "stored3d=%s,dss3=%s,valid3=%s" % [fd.get("stored3d", "<?>"), fd.get("dss3", "<?>"), fd.get("valid3d", "<?>")])])

func _arm_xcheck() -> void:
	# One child process offers identical name lists to both server managers;
	# per-name acceptance is attributed by printerr markers bracketing each call
	# in the child's stderr capture.
	var r := _boot("xc", PackedStringArray(), "--mode=manager", 15)
	var f: Dictionary = r["fields"]
	var errs2 := _window_counts(r["err"], "2d", NAMES2D.size())
	var errs3 := _window_counts(r["err"], "3d", NAMES3D.size())
	var ats: Array = r["at"]
	var at2 := "<none>"
	var at3 := "<none>"
	for a in ats:
		if "physics_server_2d" in a:
			at2 = a
		elif "physics_server_3d" in a:
			at3 = a
	# offered2d/offered3d are the CHILD's own offered lists (r86-critic F4):
	# pin what was actually offered, not the parent's NAMES constants.
	_finish("xcheck offered2d=%s errs2d=[%s] offered3d=%s errs3d=[%s] at2d=%s at3d=%s rc=%d errs_total=%d" % [
		f.get("offered2d", "<?>"), ",".join(errs2),
		f.get("offered3d", "<?>"), ",".join(errs3), at2, at3, r["rc"],
		_err_count(r["err"])])

func _name_labels(names: Array) -> PackedStringArray:
	var out := PackedStringArray()
	for n in names:
		out.append("<>" if n == "" else n)
	return out

# Scan child stderr for printerr windows `R86CM begin<tag> [name]` /
# `R86CM end<tag> [name]`; return per-name ERROR-line counts. The child emits
# begin/end pairs in the same order as the offered name list, so a sequential
# cursor attributes each engine refusal to exactly one offered name.
func _window_counts(err: String, tag: String, n: int) -> PackedStringArray:
	var counts: Array = []
	for i in range(n):
		counts.append(0)
	var idx := 0
	var open := false
	for line in err.split("\n"):
		var s := line.strip_edges()
		if s.begins_with("R86CM begin" + tag):
			open = true
		elif s.begins_with("R86CM end" + tag):
			open = false
			idx += 1
		elif open and idx < n and "ERROR:" in s:
			counts[idx] += 1
	var out := PackedStringArray()
	for c in counts:
		out.append(str(c))
	return out

func _arm_gate_matrix() -> void:
	# The space-state access gate: 7 fetch positions under thread_on vs default,
	# plus a fetch-free baseline proving error counts are attributable.
	var rt := _boot("thr", PackedStringArray(THREAD_ON), "--mode=gate", 15)
	var rd := _boot("def", PackedStringArray(), "--mode=gate", 15)
	var rn := _boot("nf", PackedStringArray(THREAD_ON), "--mode=nofetch", 15)
	var ft: Dictionary = rt["fields"]
	var fd: Dictionary = rd["fields"]
	var fn: Dictionary = rn["fields"]
	# The deferred fetch positions race the threaded server's physics window
	# (observed on the duality prop leg): a position that lands inside the
	# window legitimately reports ok instead of null. Named-mode envelope:
	# refused positions must each carry an engine error, fetched positions
	# report ok, backtrace frames stay inside the refused-fetch paths, and
	# at least 4 refusals remain so the gate keeps evidence.
	var refused := 0
	var nok := 0
	for k in ["A", "B", "C", "D", "E", "F", "G"]:
		if ft.get(k) == "null":
			refused += 1
		elif ft.get(k) == "ok":
			nok += 1
	var tf := _frames(rt["err"])
	var tf_ok: bool = tf != ""
	for fr in tf.split(","):
		if fr not in ["_dss_state", "_loud_state", "_initialize", "_run",
				"_m_gate", "_process", "_physics_process"]:
			tf_ok = false
	var thr_ok: bool = refused + nok == 7 and refused >= 4 and \
		refused == _err_count(rt["err"]) and ft.get("loud") == "ok" and tf_ok
	var at := ""
	if rt["at"].size() > 0:
		at = rt["at"][0]
	# tf/df pin the refused fetch's user frames; nofetch pins its own `thr`
	# readback so an unthreaded baseline cannot pass silently (critic F2/F6).
	_finish("gate_matrix thr_ok=%d def[A=%s,B=%s,C=%s,D=%s,E=%s,F=%s,G=%s,loud=%s,errs=%d,df=%s] nofetch[thr=%s,errs=%d] rc=[%d,%d,%d] errB=[%d,%d] at=%s" % [
		int(thr_ok),
		fd.get("A", "?"), fd.get("B", "?"), fd.get("C", "?"), fd.get("D", "?"),
		fd.get("E", "?"), fd.get("F", "?"), fd.get("G", "?"), fd.get("loud", "?"),
		_err_count(rd["err"]), _frames(rd["err"]),
		fn.get("thr", "<?>"), _err_count(rn["err"]),
		rt["rc"], rd["rc"], rn["rc"],
		rd["err_bytes"], rn["err_bytes"], at])

func _arm_gate_duality() -> void:
	# r77's pinned law said the World2D property path is silent where the
	# explicit server call is loud; both emit the SAME engine error. One refused
	# fetch per child at position B; the `at:` lines are compared byte-wise.
	var rp := _boot("prop", PackedStringArray(THREAD_ON), "--mode=prop", 15)
	var ra := _boot("api", PackedStringArray(THREAD_ON), "--mode=api", 15)
	var fp: Dictionary = rp["fields"]
	var fa: Dictionary = ra["fields"]
	var atp := _at_pick(rp["at"], "space_get_direct_state")
	var ata := _at_pick(ra["at"], "space_get_direct_state")
	var pf := _frames(rp["err"])
	var af := _frames(ra["err"])
	# The deferred _run fetch races the threaded server's physics window:
	# mode a = refused (B=null + engine error + _state frame), mode b =
	# fetched cleanly (B=ok, no error). Both realized on this host; each
	# side gets its own named mode and the emit fail-closes on anything
	# else (critic F2 + observed rep flake).
	var pmode := ""
	if fp.get("B") == "null" and _err_count(rp["err"]) == 1 and pf == "_dss_state,_run":
		pmode = "a"
	elif fp.get("B") == "ok" and _err_count(rp["err"]) == 0 and pf == "":
		pmode = "b"
	var amode := ""
	if fa.get("B") == "null" and _err_count(ra["err"]) == 1 and af == "_loud_state,_run":
		amode = "a"
	elif fa.get("B") == "ok" and _err_count(ra["err"]) == 0 and af == "":
		amode = "b"
	# Independent children race independently: all four mode combos are
	# legitimate. The duality claim (identical engine error) is only
	# checkable when both refused — gate at_eq on that combo only.
	var dual_ok: bool = pmode != "" and amode != "" and \
		rp["rc"] == 0 and ra["rc"] == 0 and \
		(pmode != "a" or amode != "a" or (atp == ata and atp != "<none>"))
	_finish("gate_duality dual_ok=%d" % int(dual_ok))

func _arm_dummy_degenerate() -> void:
	# The Dummy server answers queries with degenerate payloads: no contacts,
	# a hit dict missing `collider`, empty shape/motion results — and no motion.
	var rd := _boot("dum", PackedStringArray(['2d/physics_engine="Dummy"']), "--mode=dummy", 15)
	var rc := _boot("ctl", PackedStringArray(), "--mode=dummy", 15)
	var fd: Dictionary = rd["fields"]
	var fc: Dictionary = rc["fields"]
	# cm0/cm1 pin the cast_motion fractions themselves — the bare array size
	# cannot distinguish a hit from a complete miss (critic F3).
	_finish("dummy_degenerate dummy%s control%s" % [
		_slot(rd, "valid=%s,dss=%s,mv=%s,ray_keys=%s,ray_pos=%s,is_n=%s,cm0=%s,cm1=%s" % [
			fd.get("valid", "?"), fd.get("dss", "?"), _mvclass(fd.get("moved", "?")),
			fd.get("ray_keys", "?"), fd.get("ray_pos", "?"),
			fd.get("is_n", "?"), fd.get("cm0", "?"), fd.get("cm1", "?")]),
		_slot(rc, "valid=%s,dss=%s,mv=%s,ray_keys=%s,ray_pos=%s,is_n=%s,cm0=%s,cm1=%s" % [
			fc.get("valid", "?"), fc.get("dss", "?"), _mvclass(fc.get("moved", "?")),
			fc.get("ray_keys", "?"), fc.get("ray_pos", "?"),
			fc.get("is_n", "?"), fc.get("cm0", "?"), fc.get("cm1", "?")])])

func _arm_dummy_timeout() -> void:
	# The hazard class: under Dummy a ray hit dict lacks `collider`; the access
	# kills the coroutine before quit(), the SceneTree idles forever, and only an
	# external bound ends the process (timeout -> rc=124).
	var bound := 3
	var r := _boot("hang", PackedStringArray(['2d/physics_engine="Dummy"']), "--mode=dummyhang", bound)
	var sig := 0
	for line in r["err"].split("\n"):
		if "Invalid access to property or key 'collider' on a base object of type 'Dictionary'" in line:
			sig += 1
	# dur_ms pins the wall duration: rc=124 alone cannot distinguish an
	# external timeout-kill from a fast self-exit (critic F1).
	_finish("dummy_timeout rc=%d bound_s=%d dur_ge=%d hang_begin=%s collider_sig=%d errs=%d" % [
		r["rc"], bound, int(r["dur_ms"] >= bound * 1000 - 200),
		r["fields"].get("hang_begin", "0"), sig, _err_count(r["err"])])

# -- embedded child project ----------------------------------------------------

# The child script is written verbatim into each generated project dir; it is a
# separate SceneTree so early-position space-state fetches land on the child's
# own boot-selected server. `R86C key=value` lines are the parent's only input;
# printerr `R86CM` markers bracket manager calls inside the stderr capture.
func _child_src() -> String:
	return "\n".join(PackedStringArray([
		'extends SceneTree',
		'var mode := ""',
		'var _gate := {}',
		'func _initialize() -> void:',
		'	for a in OS.get_cmdline_user_args():',
		'		if a.begins_with("--mode="):',
		'			mode = a.substr(7)',
		'	if mode == "gate":',
		'		_gate["A"] = _dss_state()',
		'	call_deferred("_run")',
		'func _world2d():',
		'	return get_root().get_world_2d() if get_root() != null else null',
		'func _dss_state() -> String:',
		'	var w = _world2d()',
		'	if w == null:',
		'		return "noworld"',
		'	return "ok" if w.direct_space_state != null else "null"',
		'func _loud_state() -> String:',
		'	var w = _world2d()',
		'	if w == null:',
		'		return "noworld"',
		'	var d = PhysicsServer2D.space_get_direct_state(w.space)',
		'	return "ok" if d != null else "null"',
		'func _setting(n: String) -> String:',
		'	return str(ProjectSettings.get_setting(n, "<unset>"))',
		'func _run() -> void:',
		'	if mode == "gate":',
		'		_gate["B"] = _dss_state()',
		'	match mode:',
		'		"probe":',
		'			await _m_probe()',
		'		"probe3d":',
		'			_m_probe3d()',
		'		"manager":',
		'			_m_manager()',
		'		"gate":',
		'			await _m_gate()',
		'		"prop":',
		'			print("R86C B=%s" % _dss_state())',
		'		"api":',
		'			print("R86C B=%s" % _loud_state())',
		'		"nofetch":',
		'			print("R86C thr=%s" % _setting("physics/2d/run_on_separate_thread"))',
		'		"dummy":',
		'			await _m_dummy()',
		'		"dummyhang":',
		'			await _m_dummyhang()',
		'		_:',
		'			print("R86C unknown=1")',
		'	if mode != "dummyhang":',
		'		quit()',
		'func _m_probe() -> void:',
		'	var w = _world2d()',
		'	var dss = w.direct_space_state if w != null else null',
		'	var n := Node2D.new()',
		'	root.add_child(n)',
		'	var b := RigidBody2D.new()',
		'	var cs := CollisionShape2D.new()',
		'	var c := CircleShape2D.new()',
		'	c.radius = 5.0',
		'	cs.shape = c',
		'	b.add_child(cs)',
		'	n.add_child(b)',
		'	var y0 := b.global_position.y',
		'	for i in range(12):',
		'		await physics_frame',
		'	var y1 := b.global_position.y',
		'	print("R86C stored=[%s]" % _setting("physics/2d/physics_engine"))',
		'	print("R86C stored_has=%s" % str(ProjectSettings.has_setting("physics/2d/physics_engine")))',
		'	print("R86C dss=%s" % (dss.get_class() if dss != null else "null"))',
		'	print("R86C valid=%s" % str(w != null and w.space.is_valid()))',
		'	print("R86C moved=%.3f" % (y1 - y0))',
		'func _m_probe3d() -> void:',
		'	var w3 = get_root().get_world_3d()',
		'	var d3 = w3.direct_space_state if w3 != null else null',
		'	print("R86C stored3d=[%s]" % _setting("physics/3d/physics_engine"))',
		'	print("R86C dss3=%s" % (d3.get_class() if d3 != null else "null"))',
		'	print("R86C valid3d=%s" % str(w3 != null and w3.space.is_valid()))',
		'func _m_manager() -> void:',
		'	var m2 = Engine.get_singleton("PhysicsServer2DManager")',
		'	var m3 = Engine.get_singleton("PhysicsServer3DManager")',
		'	var l2 := ["GodotPhysics2D", "Dummy", "Jolt Physics", "garbage_xyz", ""]',
		'	var l3 := ["Jolt Physics", "GodotPhysics3D", "Dummy", "garbage_xyz"]',
		'	print("R86C offered2d=[%s]" % ",".join(l2))',
		'	print("R86C offered3d=[%s]" % ",".join(l3))',
		'	for nm in l2:',
		'		printerr("R86CM begin2d [%s]" % nm)',
		'		m2.call("set_default_server", nm, 100)',
		'		printerr("R86CM end2d [%s]" % nm)',
		'	for nm in l3:',
		'		printerr("R86CM begin3d [%s]" % nm)',
		'		m3.call("set_default_server", nm, 100)',
		'		printerr("R86CM end3d [%s]" % nm)',
		'	print("R86C done=1")',
		'func _m_gate() -> void:',
		'	await process_frame',
		'	_gate["C"] = _dss_state()',
		'	for i in range(4):',
		'		await physics_frame',
		'	_gate["D"] = _dss_state()',
		'	_gate["loud"] = _loud_state()',
		'	var n := R86GateNode.new()',
		'	n.gate = self',
		'	root.add_child(n)',
		'	for i in range(3):',
		'		await physics_frame',
		'	await process_frame',
		'	await process_frame',
		'	_gate["G"] = _dss_state()',
		'	await process_frame',
		'	for k in ["A", "B", "C", "D", "E", "F", "G"]:',
		'		print("R86C %s=%s" % [k, _gate.get(k, "<unset>")])',
		'	print("R86C loud=%s" % _gate.get("loud", "<unset>"))',
		'func _mk_world(n: Node2D) -> RigidBody2D:',
		'	var wall := StaticBody2D.new()',
		'	var wcs := CollisionShape2D.new()',
		'	var wr := RectangleShape2D.new()',
		'	wr.size = Vector2(4, 40)',
		'	wcs.shape = wr',
		'	wall.add_child(wcs)',
		'	wall.position = Vector2(100, 0)',
		'	n.add_child(wall)',
		'	var b := RigidBody2D.new()',
		'	var cs := CollisionShape2D.new()',
		'	var c := CircleShape2D.new()',
		'	c.radius = 5.0',
		'	cs.shape = c',
		'	b.add_child(cs)',
		'	n.add_child(b)',
		'	return b',
		'func _m_dummy() -> void:',
		'	var w = _world2d()',
		'	var n := Node2D.new()',
		'	root.add_child(n)',
		'	var b := _mk_world(n)',
		'	var y0 := b.global_position.y',
		'	for i in range(12):',
		'		await physics_frame',
		'	var moved := b.global_position.y - y0',
		'	var dss = w.direct_space_state if w != null else null',
		'	var keys := "<nodss>"',
		'	var ray_pos := "<nodss>"',
		'	var is_n := -1',
		'	var cm_n := -1',
		'	if dss != null:',
		'		var q := PhysicsRayQueryParameters2D.create(Vector2(0, 0), Vector2(200, 0))',
		'		var hit: Dictionary = dss.intersect_ray(q)',
		'		var ks := hit.keys()',
		'		ks.sort()',
		'		keys = str(ks)',
		'		ray_pos = str(hit.get("position", "<absent>"))',
		'		var sq := PhysicsShapeQueryParameters2D.new()',
		'		var circle := CircleShape2D.new()',
		'		circle.radius = 4.0',
		'		sq.shape = circle',
		'		sq.transform = Transform2D(0.0, Vector2(98, 0))',
		'		is_n = dss.intersect_shape(sq, 8).size()',
		'		var mq := PhysicsShapeQueryParameters2D.new()',
		'		mq.shape = circle',
		'		mq.transform = Transform2D(0.0, Vector2(0, 0))',
		'		mq.motion = Vector2(200, 0)',
		'		var cm: Array = dss.cast_motion(mq)',
		'		cm_n = cm.size()',
		'		print("R86C cm0=%.4f" % (cm[0] if cm_n > 0 else -1.0))',
		'		print("R86C cm1=%.4f" % (cm[1] if cm_n > 1 else -1.0))',
		'	print("R86C valid=%s" % str(w != null and w.space.is_valid()))',
		'	print("R86C dss=%s" % (dss.get_class() if dss != null else "null"))',
		'	print("R86C moved=%.3f" % moved)',
		'	print("R86C ray_keys=%s" % keys)',
		'	print("R86C ray_pos=%s" % ray_pos)',
		'	print("R86C is_n=%d" % is_n)',
		'	print("R86C cm_n=%d" % cm_n)',
		'func _m_dummyhang() -> void:',
		'	var n := Node2D.new()',
		'	root.add_child(n)',
		'	_mk_world(n)',
		'	for i in range(4):',
		'		await physics_frame',
		'	var w = _world2d()',
		'	var dss = w.direct_space_state',
		'	var q := PhysicsRayQueryParameters2D.create(Vector2(0, 0), Vector2(200, 0))',
		'	var hit: Dictionary = dss.intersect_ray(q)',
		'	print("R86C hang_begin=1")',
		'	var c = hit.collider',
		'	print("R86C collider_ok=%s" % str(c != null))',
		'	quit()',
		'class R86GateNode extends Node2D:',
		'	var gate = null',
		'	var seen := 0',
		'	func _physics_process(_d: float) -> void:',
		'		seen += 1',
		'		if seen == 1:',
		'			gate._gate["E"] = gate._dss_state()',
		'	func _process(_d: float) -> void:',
		'		if not gate._gate.has("F"):',
		'			gate._gate["F"] = gate._dss_state()',
	]))
