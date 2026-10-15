extends SceneTree
# r94b boundary ATTACK probe — scheduler / load / --fixed-fps sensitivity of the
# r94-scout CPUParticles2D + GPUParticles2D claims (round 94, seat BOUNDARY).
#
# Launch shape (identical to the scout's, so the numbers are comparable):
#   godot --headless [--fixed-fps N] --path proj --script res://r94b_particles.gd -- --arm=<arm>
# Every arm prints exactly one `PASS r94b_particles <arm> ...` line.
#
# Harness helpers (_arg/_v2/_sv/_new_cpu/_watch/_free_node/_wait_ph/_okb/_fmt) are
# copied from the scout's frozen probe (sha256 e6a2e0f5…) so tick accounting is the
# scout's own; the arms below are the new attack lanes:
#   frame_ratio  — process/physics frame ratio + observed deltas per condition
#   clock_unit   — is the particle clock a TIME accumulator or a frame counter?
#                  (one-shot L measured in physics ticks AND process frames AND ms)
#   tps30/tps120 — Engine.physics_ticks_per_second changed at runtime (scout §8 gap)
#   ffprop       — engine `fixed_fps` property edge values 1/5/30/60/1000 x fract_delta
#   amount_sync  — is the amount-setter spurious `finished` synchronous in the setter?
#   amount_pre   — amount before emission starts / on a continuous emitter
#   contam_a..h  — minimal trigger + scope of the "process-global contamination" law
#   gpu_probe    — GPUParticles2D inertness measured in ticks and process frames
#   req_var      — request_particles_process lattice: residual arg + tps sensitivity

var PH := 0
var PF := 0

class DeltaProbe extends Node:
	var last_proc := 0.0
	var last_phys := 0.0
	var total_proc := 0.0
	var first_proc := -1.0
	var proc_n := 0
	var phys_n := 0

	func _process(d: float) -> void:
		if first_proc < 0.0:
			first_proc = d
		last_proc = d
		total_proc += d
		proc_n += 1

	func _physics_process(d: float) -> void:
		last_phys = d
		phys_n += 1

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _v2(v: Vector2) -> String:
	return "(%.4f,%.4f)" % [v.x, v.y]

func _new_cpu(cfg: Dictionary) -> CPUParticles2D:
	var n := CPUParticles2D.new()
	for k in cfg:
		n.set(k, cfg[k])
	return n

func _watch(n: CPUParticles2D, st: Dictionary) -> void:
	n.finished.connect(func():
		st["n_fin"] += 1
		if st["fin_ph"] < 0:
			st["fin_ph"] = PH
			st["em_fin"] = n.emitting
			st["ise_fin"] = n.is_emitting())

# tick + process-frame aware watcher (fin_pf is the process-frame index of the finish)
func _watch_t(n: CPUParticles2D, st: Dictionary) -> void:
	n.finished.connect(func():
		st["n_fin"] += 1
		if st["fin_ph"] < 0:
			st["fin_ph"] = PH
			st["fin_pf"] = PF
			st["em_fin"] = n.emitting
			st["ise_fin"] = n.is_emitting())

func _free_node(n: Node) -> void:
	var parent := n.get_parent()
	if parent != null:
		parent.remove_child(n)
	n.free()

func _wait_ph(n: int) -> void:
	var a: int = PH
	while PH < a + n:
		await process_frame

func _okb(delta: int, lo: int, hi: int) -> String:
	return "true" if (delta >= lo and delta <= hi) else "false"

# ------------------------------------------------------------------ mechanism

func _arm_frame_ratio() -> void:
	var probe := DeltaProbe.new()
	root.add_child(probe)
	var pf0: int = Engine.get_process_frames()
	var ph0: int = Engine.get_physics_frames()
	var t0: int = Time.get_ticks_usec()
	var n := 0
	while n < 90:
		await process_frame
		n += 1
	var wall_ms := float(Time.get_ticks_usec() - t0) / 1000.0
	var pf: int = Engine.get_process_frames() - pf0
	var ph: int = Engine.get_physics_frames() - ph0
	print("PASS r94b_particles frame_ratio",
		" proc_frames=%d phys_frames=%d proc_per_phys=%.3f phys_per_proc=%.3f" % [
			pf, ph, float(pf) / float(maxi(1, ph)), float(ph) / float(maxi(1, pf))],
		" last_proc_delta=%.6f last_phys_delta=%.6f proc_n=%d phys_n=%d" % [
			probe.last_proc, probe.last_phys, probe.proc_n, probe.phys_n],
		" wall_ms=%.1f fps=%.1f tps=%d max_fps=%d time_scale=%.2f max_steps=%d jitter=%.2f" % [
			wall_ms, Engine.get_frames_per_second(), Engine.physics_ticks_per_second,
			Engine.max_fps, Engine.time_scale, Engine.max_physics_steps_per_frame,
			Engine.physics_jitter_fix],
		" in_phys=%s" % str(Engine.is_in_physics_frame()))
	_free_node(probe)

# one-shot run measured in physics ticks, process frames and accumulated process ms
func _run_cpu_timed(cfg: Dictionary, bound: int) -> Dictionary:
	var n := _new_cpu(cfg)
	root.add_child(n)
	var probe := DeltaProbe.new()
	root.add_child(probe)
	var st := {"fin_ph": -1, "fin_pf": -1, "n_fin": 0, "em_fin": false, "ise_fin": false}
	_watch_t(n, st)
	n.emitting = true
	var start_ph: int = PH
	var start_pf: int = PF
	var start_proc: float = probe.total_proc
	while PH < start_ph + bound and st["fin_ph"] < 0:
		await process_frame
	var out := {
		"fin_ph": (int(st["fin_ph"]) - start_ph) if int(st["fin_ph"]) >= 0 else -1,
		"fin_pf": (int(st["fin_pf"]) - start_pf) if int(st["fin_pf"]) >= 0 else -1,
		"n_fin": st["n_fin"], "em_fin": st["em_fin"], "ise_fin": st["ise_fin"],
		"proc_ms": (probe.total_proc - start_proc) * 1000.0,
		"ph_total": PH - start_ph, "pf_total": PF - start_pf,
	}
	_free_node(n)
	_free_node(probe)
	return out

func _arm_clock_unit() -> void:
	var out: Array[String] = []
	for L in [0.25, 0.5, 1.0]:
		var r: Dictionary = await _run_cpu_timed(
			{"one_shot": true, "lifetime": L, "amount": 8, "explosiveness": 1.0}, int(L * 60.0) + 40)
		out.append("L%.2f[fin_ph=%d fin_pf=%d proc_ms=%.1f ph_total=%d pf_total=%d n=%d]" % [
			L, r["fin_ph"], r["fin_pf"], r["proc_ms"], r["ph_total"], r["pf_total"], r["n_fin"]])
	print("PASS r94b_particles clock_unit", " | " + " ".join(out))

func _arm_tps30() -> void:
	Engine.physics_ticks_per_second = 30
	var r: Dictionary = await _run_cpu_timed(
		{"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0}, 90)
	print("PASS r94b_particles tps30",
		" fin_ph=%d fin_pf=%d proc_ms=%.1f ph_total=%d pf_total=%d n_fin=%d tps_now=%d" % [
			r["fin_ph"], r["fin_pf"], r["proc_ms"], r["ph_total"], r["pf_total"], r["n_fin"],
			Engine.physics_ticks_per_second])
	Engine.physics_ticks_per_second = 60

func _arm_tps120() -> void:
	Engine.physics_ticks_per_second = 120
	var r: Dictionary = await _run_cpu_timed(
		{"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0}, 120)
	print("PASS r94b_particles tps120",
		" fin_ph=%d fin_pf=%d proc_ms=%.1f ph_total=%d pf_total=%d n_fin=%d tps_now=%d" % [
			r["fin_ph"], r["fin_pf"], r["proc_ms"], r["ph_total"], r["pf_total"], r["n_fin"],
			Engine.physics_ticks_per_second])
	Engine.physics_ticks_per_second = 60

# engine `fixed_fps` PROPERTY edge values (distinct from the --fixed-fps harness flag)
func _arm_ffprop() -> void:
	var out: Array[String] = []
	for spec in [[1, true], [1, false], [5, true], [5, false], [30, true], [30, false], [60, true], [1000, true]]:
		var ffps: int = spec[0]
		var fract: bool = spec[1]
		var r: Dictionary = await _run_cpu_timed(
			{"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0,
			 "fixed_fps": ffps, "fract_delta": fract}, 80)
		out.append("ff%d_fr%s[fin_ph=%d fin_pf=%d proc_ms=%.1f ph_total=%d n=%d]" % [
			ffps, str(fract)[0], r["fin_ph"], r["fin_pf"], r["proc_ms"], r["ph_total"], r["n_fin"]])
	print("PASS r94b_particles ffprop", " | " + " ".join(out))

# ------------------------------------------------------------------ amount hazard

func _arm_amount_sync() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 1.0, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0, "em_fin": false, "ise_fin": false}
	_watch(n, st)
	n.emitting = true
	await _wait_ph(10)
	var before: int = st["n_fin"]
	n.amount = 32
	var sync1: int = st["n_fin"]          # read with NO await in between
	var em1: bool = n.emitting
	var ise1: bool = n.is_emitting()
	var fin_ph1: int = st["fin_ph"]
	await process_frame
	var after_frame: int = st["n_fin"]
	n.amount = 8
	var sync2: int = st["n_fin"]          # second set: does it fire again?
	var set_ph: int = PH
	while PH < set_ph + 80:
		await process_frame
	print("PASS r94b_particles amount_sync",
		" n_fin_before=%d n_fin_sync=%d sync_fired=%s n_fin_after_frame=%d second_n_fin=%d second_sync_fired=%s" % [
			before, sync1, str(sync1 > before), after_frame, sync2, str(sync2 > after_frame)],
		" em1=%s ise1=%s fin_ph_at_set=%d total_n_fin=%d em_at_end=%s ise_at_end=%s ph_end=%d" % [
			str(em1), str(ise1), fin_ph1, st["n_fin"], str(n.emitting), str(n.is_emitting()), PH - set_ph])
	_free_node(n)

func _arm_amount_pre() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0}
	_watch(n, st)
	n.emitting = false          # class default is emitting=true: must be explicit
	await _wait_ph(5)
	n.amount = 16
	await _wait_ph(5)
	var pre_n: int = st["n_fin"]
	n.one_shot = false
	n.emitting = true
	await _wait_ph(10)
	n.amount = 24
	await _wait_ph(10)
	var cont_n: int = st["n_fin"] - pre_n
	print("PASS r94b_particles amount_pre",
		" never_emitting_n_fin=%d continuous_n_fin=%d em_after=%s ise_after=%s" % [
			pre_n, cont_n, str(n.emitting), str(n.is_emitting())])
	_free_node(n)

# ------------------------------------------------------------------ contamination scope

func _never_tail(bound: int) -> String:
	var n := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0}
	_watch(n, st)
	var pf0: int = PF
	n.emitting = false
	var sync_n: int = st["n_fin"]      # did the setter itself emit finished?
	var b: int = PH
	while PH < b + bound and st["fin_ph"] < 0:
		await process_frame
	var fd: int = (int(st["fin_ph"]) - b) if int(st["fin_ph"]) >= 0 else -1
	_free_node(n)
	return "never[fin_delta=%d n=%d sync=%d add_pf=%d]" % [fd, st["n_fin"], sync_n, pf0]

func _arm_contam_a() -> void:  # scout-exact: prior emitter ran 5 ticks, then freed
	var pre := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(pre)
	pre.emitting = true
	await _wait_ph(5)
	_free_node(pre)
	var tail: String = await _never_tail(20)
	print("PASS r94b_particles contam_a", " pre=emitted5_freed", " " + tail)

func _arm_contam_b() -> void:  # prior node UPDATED 5 ticks but never emitting, then freed
	var pre := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(pre)
	pre.emitting = false
	await _wait_ph(5)
	_free_node(pre)
	var tail: String = await _never_tail(20)
	print("PASS r94b_particles contam_b", " pre=updated5_never_emitting_freed", " " + tail)

func _arm_contam_c() -> void:  # prior emitter still LIVE in the tree
	var pre := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(pre)
	pre.emitting = true
	await _wait_ph(5)
	var tail: String = await _never_tail(20)
	_free_node(pre)
	print("PASS r94b_particles contam_c", " pre=emitted5_live", " " + tail)

func _arm_contam_d() -> void:  # prior node INSTANTIATED but never added to the tree
	var pre := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	pre.emitting = true
	_free_node(pre)
	await _wait_ph(2)
	var tail: String = await _never_tail(20)
	print("PASS r94b_particles contam_d", " pre=instantiated_never_added", " " + tail)

func _arm_contam_e() -> void:  # cross-class scope: prior CPUParticles3D emitter
	var pre := CPUParticles3D.new()
	pre.one_shot = false
	pre.lifetime = 0.5
	pre.amount = 8
	pre.explosiveness = 1.0
	root.add_child(pre)
	pre.emitting = true
	await _wait_ph(5)
	_free_node(pre)
	var tail: String = await _never_tail(20)
	print("PASS r94b_particles contam_e", " pre=cpu3d_emitted5_freed", " " + tail)

func _arm_contam_f() -> void:  # prior emitter with ZERO updates (emitting=true, freed same tick)
	var pre := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(pre)
	pre.emitting = true
	_free_node(pre)
	var tail: String = await _never_tail(20)
	print("PASS r94b_particles contam_f", " pre=emitted0_freed", " " + tail)

func _arm_contam_g() -> void:  # control: nothing before the never-emitting node
	var tail: String = await _never_tail(20)
	print("PASS r94b_particles contam_g", " pre=none", " " + tail)

func _arm_contam_h() -> void:  # first node is itself a never-emitting node, kept live
	var first := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(first)
	first.emitting = false
	await _wait_ph(3)
	var tail: String = await _never_tail(20)
	_free_node(first)
	print("PASS r94b_particles contam_h", " pre=never_emitting_live3", " " + tail)

func _arm_contam_j() -> void:  # pure-wait control: no prior particle instance at all
	await _wait_ph(2)
	var tail: String = await _never_tail(20)
	print("PASS r94b_particles contam_j", " pre=none_wait2", " " + tail)

func _arm_contam_k() -> void:  # prior node instantiated outside the tree (no property writes), freed, wait
	var pre := _new_cpu({})
	_free_node(pre)
	await _wait_ph(2)
	var tail: String = await _never_tail(20)
	print("PASS r94b_particles contam_k", " pre=instantiated_only_freed", " " + tail)

# decisive test of the "process-global state" framing: is a never-emitting emitter
# clean only when its FIRST update lands on the process's first frame?
func _arm_contam_first() -> void:
	var p0 := DeltaProbe.new()
	root.add_child(p0)
	var n0 := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n0)
	var s0 := {"fin_ph": -1, "n_fin": 0}
	_watch(n0, s0)
	n0.emitting = false
	await _wait_ph(2)
	var d0: int = int(s0["fin_ph"]) if int(s0["fin_ph"]) >= 0 else -1
	var late := DeltaProbe.new()
	root.add_child(late)
	await process_frame
	var fd0: float = p0.first_proc
	var fdl: float = late.first_proc
	var n1 := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n1)
	var s1 := {"fin_ph": -1, "n_fin": 0}
	_watch(n1, s1)
	n1.emitting = false
	var b1: int = PH
	while PH < b1 + 10 and s1["fin_ph"] < 0:
		await process_frame
	var d1: int = (int(s1["fin_ph"]) - b1) if int(s1["fin_ph"]) >= 0 else -1
	print("PASS r94b_particles contam_first",
		" frame0_never[fin_delta=%d n=%d] late_never[fin_delta=%d n=%d]" % [d0, s0["n_fin"], d1, s1["n_fin"]],
		" frame0_probe_first_delta=%.6f late_probe_first_delta=%.6f ph_now=%d" % [fd0, fdl, PH])
	_free_node(n0)
	_free_node(n1)
	_free_node(p0)
	_free_node(late)

# continuous-emitter amount hazard as a function of the set tick (cycle phase sweep)
func _arm_amount_phase() -> void:
	var out: Array[String] = []
	for t in [5, 10, 20, 29, 30, 31, 45, 60]:
		var n := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
		root.add_child(n)
		var st := {"fin_ph": -1, "n_fin": 0}
		_watch(n, st)
		n.emitting = true
		var b: int = PH
		while PH < b + t:
			await process_frame
		var before: int = st["n_fin"]
		n.amount = 32
		await process_frame
		var at_set: int = st["n_fin"] - before
		await _wait_ph(3)
		out.append("t%d[fire=%d total=%d]" % [t, at_set, st["n_fin"]])
		_free_node(n)
	print("PASS r94b_particles amount_phase", " | " + " ".join(out))

# continuous-emitter amount control matrix (attacks the scout's F17 "no spurious finish
# for continuous emitters": their control was a fresh one_shot=false node only)
func _arm_amount_cont() -> void:
	var out: Array[String] = []
	# c1 scout-exact: one_shot=false from creation, emitting from the start
	var n1 := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n1)
	var s1 := {"fin_ph": -1, "n_fin": 0}
	_watch(n1, s1)
	n1.emitting = true
	await _wait_ph(10)
	n1.amount = 32
	await process_frame
	var a1: int = s1["n_fin"]
	await _wait_ph(15)
	out.append("c1_fresh_cont[at_set=%d end=%d em=%s]" % [a1, s1["n_fin"], str(n1.emitting)])
	_free_node(n1)
	# c2 one_shot=true from creation, emitting from the start, flipped to false, then amount set
	var n2 := _new_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n2)
	var s2 := {"fin_ph": -1, "n_fin": 0}
	_watch(n2, s2)
	n2.emitting = true
	await _wait_ph(5)
	n2.one_shot = false
	await _wait_ph(5)
	n2.amount = 32
	await process_frame
	var a2: int = s2["n_fin"]
	await _wait_ph(15)
	out.append("c2_flip_mid[at_set=%d end=%d em=%s]" % [a2, s2["n_fin"], str(n2.emitting)])
	_free_node(n2)
	# c3 one_shot=false, emitting=false, delayed start (emitting=true later), then amount set
	var n3 := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n3)
	var s3 := {"fin_ph": -1, "n_fin": 0}
	_watch(n3, s3)
	n3.emitting = false
	await _wait_ph(5)
	n3.emitting = true
	await _wait_ph(10)
	n3.amount = 32
	await process_frame
	var a3: int = s3["n_fin"]
	await _wait_ph(15)
	out.append("c3_delayed_start[at_set=%d end=%d em=%s]" % [a3, s3["n_fin"], str(n3.emitting)])
	_free_node(n3)
	print("PASS r94b_particles amount_cont", " | " + " ".join(out))

# ------------------------------------------------------------------ gpu

func _arm_gpu_probe() -> void:
	var out: Array[String] = []
	for name in ["os", "cont"]:
		var n := GPUParticles2D.new()
		n.process_material = ParticleProcessMaterial.new()
		n.lifetime = 0.25
		n.amount = 8
		n.explosiveness = 1.0
		n.one_shot = (name == "os")
		root.add_child(n)
		var st := {"fin_ph": -1, "n_fin": 0}
		n.finished.connect(func():
			st["n_fin"] += 1
			if st["fin_ph"] < 0:
				st["fin_ph"] = PH)
		n.emitting = true
		var start: int = PH
		var spf: int = PF
		var flip_ph: int = -1
		var flip_pf: int = -1
		while PH < start + 40:
			await process_frame
			if flip_ph < 0 and not n.emitting:
				flip_ph = PH
				flip_pf = PF
		out.append("%s[fin_delta=%d n=%d flip_ph=%d flip_pf=%d em_after=%s ise_after=%s]" % [
			name, (int(st["fin_ph"]) - start) if int(st["fin_ph"]) >= 0 else -1, st["n_fin"],
			(flip_ph - start) if flip_ph >= 0 else -1, (flip_pf - spf) if flip_pf >= 0 else -1,
			str(n.emitting), str(n.is_emitting())])
		_free_node(n)
	var g := GPUParticles2D.new()
	g.process_material = ParticleProcessMaterial.new()
	g.lifetime = 0.25
	g.amount = 8
	g.one_shot = true
	root.add_child(g)
	g.emitting = true
	await _wait_ph(10)
	var r: Rect2 = g.capture_rect()
	var st2 := {"fin_ph": -1, "n_fin": 0}
	g.finished.connect(func():
		st2["n_fin"] += 1
		if st2["fin_ph"] < 0:
			st2["fin_ph"] = PH)
	Engine.time_scale = 0.0
	for i in range(10):
		g.request_particles_process(0.1)
		await process_frame
	Engine.time_scale = 1.0
	out.append("capture[rect=(%.4f,%.4f,%.4f,%.4f) em_after=%s req_n_fin=%d req_fin_ph=%d]" % [
		r.position.x, r.position.y, r.size.x, r.size.y, str(g.emitting), st2["n_fin"], st2["fin_ph"]])
	_free_node(g)
	print("PASS r94b_particles gpu_probe", " | " + " ".join(out))

# ------------------------------------------------------------------ request lattice

func _req_case(step: float, res: float, bound: int) -> String:
	var n := _new_cpu({"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin": -1, "n_fin": 0, "calls": 0}
	n.finished.connect(func():
		st["n_fin"] += 1
		if st["fin"] < 0:
			st["fin"] = st["calls"])
	n.emitting = true
	await process_frame
	var calls := 0
	while calls < bound and st["fin"] < 0:
		n.request_particles_process(step, res)
		st["calls"] = calls
		calls += 1
		await process_frame
	var expected: int = int(round(0.5 / step)) + 1
	var s := "step%.2f_res%.2f[fin_call1=%d raw=%d expected=%d n_fin=%d]" % [
		step, res, calls, st["fin"], expected, st["n_fin"]]
	_free_node(n)
	return s

func _arm_req_var() -> void:
	Engine.time_scale = 0.0
	var parts: Array[String] = []
	# step table: L=0.5 so L/step = 5, 10, 3.33, 2.5, 2, 1.67, 1.25
	for step in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4]:
		var s: String = await _req_case(step, 0.0, 40)
		parts.append(s)
	# residual argument (second arg of request_particles_process)
	var r1: String = await _req_case(0.1, 0.02, 40)
	parts.append("res0.02_" + r1)
	# tps independence of the clock-free lattice
	Engine.physics_ticks_per_second = 120
	var r2: String = await _req_case(0.1, 0.0, 40)
	parts.append("tps120_" + r2)
	var r3: String = await _req_case(0.2, 0.0, 40)
	parts.append("tps120_" + r3)
	Engine.physics_ticks_per_second = 60
	Engine.time_scale = 1.0
	print("PASS r94b_particles req_var", " | " + " ".join(parts))

# `fixed_fps=1` (1 s quantum) with a long bound: does the cycle ever end?
func _arm_ff1_long() -> void:
	var r: Dictionary = await _run_cpu_timed(
		{"one_shot": true, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0,
		 "fixed_fps": 1, "fract_delta": true}, 240)
	print("PASS r94b_particles ff1_long",
		" fin_ph=%d fin_pf=%d proc_ms=%.1f ph_total=%d pf_total=%d n_fin=%d" % [
			r["fin_ph"], r["fin_pf"], r["proc_ms"], r["ph_total"], r["pf_total"], r["n_fin"]])

# attribution of the amount-setter spurious finish: physics ticks vs process frames
func _arm_amount_attr() -> void:
	var n := _new_cpu({"one_shot": true, "lifetime": 1.0, "amount": 8, "explosiveness": 1.0})
	root.add_child(n)
	var st := {"fin_ph": -1, "fin_pf": -1, "n_fin": 0}
	_watch_t(n, st)
	n.emitting = true
	await _wait_ph(10)
	var set_ph: int = PH
	var set_pf: int = PF
	n.amount = 32
	var sync_n: int = st["n_fin"]
	var pfs := 0
	while st["n_fin"] == 0 and pfs < 20:
		await process_frame
		pfs += 1
	var d_ph: int = (int(st["fin_ph"]) - set_ph) if int(st["fin_ph"]) >= 0 else -1
	var d_pf: int = (int(st["fin_pf"]) - set_pf) if int(st["fin_pf"]) >= 0 else -1
	print("PASS r94b_particles amount_attr",
		" sync_n_fin=%d frames_to_fire=%d d_ph=%d d_pf=%d ph_set=%d pf_set=%d" % [
			sync_n, pfs, d_ph, d_pf, set_ph, set_pf])
	_free_node(n)

# ------------------------------------------------------------------ amount bisect
# The scout's discover6 `amount_cont` arm reports n_fin=0 (no spurious finish for a
# continuous emitter); this seat's equivalent-config arms report a fire.  These four
# arms isolate the ingredient: each is the FIRST node of its own process, so node
# order cannot confound them.
func _scout_cont_body(set_tick: int, watch: bool, use_set: bool) -> String:
	var n: CPUParticles2D
	if use_set:
		n = _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	else:
		n = CPUParticles2D.new()
		n.one_shot = false
		n.lifetime = 0.5
		n.amount = 8
		n.explosiveness = 1.0
	root.add_child(n)
	var st := {"fin_ph": -1, "n_fin": 0, "em_fin": false, "ise_fin": false}
	if watch:
		_watch(n, st)
	else:
		n.finished.connect(func(): st["n_fin"] += 1)
	n.emitting = true
	var b: int = PH
	while PH < b + set_tick:
		await process_frame
	var before: int = st["n_fin"]
	n.amount = 32
	await process_frame
	var at_set: int = st["n_fin"] - before
	var end: int = PH
	while PH < end + 60:
		await process_frame
	return "at_set=%d total=%d em=%s" % [at_set, st["n_fin"], str(n.emitting)]

func _arm_amount_b1() -> void:  # scout-exact: direct assign, plain counter, set at tick 30
	var s: String = await _scout_cont_body(30, false, false)
	print("PASS r94b_particles amount_b1 scout_exact_t30", " " + s)

func _arm_amount_b2() -> void:  # scout-exact but set at tick 10
	var s: String = await _scout_cont_body(10, false, false)
	print("PASS r94b_particles amount_b2 scout_exact_t10", " " + s)

func _arm_amount_b3() -> void:  # scout-exact + this seat's _watch handler (reads is_emitting)
	var s: String = await _scout_cont_body(30, true, false)
	print("PASS r94b_particles amount_b3 watch_handler_t30", " " + s)

func _arm_amount_b4() -> void:  # scout-exact but config applied via Object.set()
	var s: String = await _scout_cont_body(30, false, true)
	print("PASS r94b_particles amount_b4 set_api_t30", " " + s)

# ------------------------------------------------------------------ dispatch

func _initialize() -> void:
	physics_frame.connect(func(): PH += 1)
	process_frame.connect(func(): PF += 1)
	var arm := _arg("arm", "frame_ratio")
	match arm:
		"frame_ratio": await _arm_frame_ratio()
		"clock_unit": await _arm_clock_unit()
		"tps30": await _arm_tps30()
		"tps120": await _arm_tps120()
		"ffprop": await _arm_ffprop()
		"amount_sync": await _arm_amount_sync()
		"amount_pre": await _arm_amount_pre()
		"contam_a": await _arm_contam_a()
		"contam_b": await _arm_contam_b()
		"contam_c": await _arm_contam_c()
		"contam_d": await _arm_contam_d()
		"contam_e": await _arm_contam_e()
		"contam_f": await _arm_contam_f()
		"contam_g": await _arm_contam_g()
		"contam_h": await _arm_contam_h()
		"contam_j": await _arm_contam_j()
		"contam_k": await _arm_contam_k()
		"contam_first": await _arm_contam_first()
		"amount_cont": await _arm_amount_cont()
		"amount_phase": await _arm_amount_phase()
		"amount_b1": await _arm_amount_b1()
		"amount_b2": await _arm_amount_b2()
		"amount_b3": await _arm_amount_b3()
		"amount_b4": await _arm_amount_b4()
		"gpu_probe": await _arm_gpu_probe()
		"req_var": await _arm_req_var()
		"ff1_long": await _arm_ff1_long()
		"amount_attr": await _arm_amount_attr()
		_: print("PASS r94b_particles unknown arm=" + arm)
	quit(0)
