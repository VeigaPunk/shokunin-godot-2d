extends SceneTree

func _initialize() -> void:
	for pass_no in range(3):
		var out: Array = []
		var rc := OS.execute(OS.get_executable_path(),
			["--headless", "--main-pack", "/tmp/r101-mut7/s01work-d/export_prod_s01.pck", "--script", "res://_census.gd"], out, true)
		var census := 0
		for l in out:
			if String(l).begins_with("CENSUS "):
				census += 1
		print("GD pass=%d rc=%d lines=%d census_lines=%d" % [pass_no, rc, out.size(), census])
	var out2: Array = []
	var rc2 := OS.execute("/bin/sh", ["-c", "echo a; echo b; echo c"], out2, true)
	print("SH rc=%d lines=%d [%s]" % [rc2, out2.size(), "|".join(out2.map(func(x): return String(x)))])
	var out3: Array = []
	var rc3 := OS.execute(OS.get_executable_path(),
		["--headless", "--main-pack", "/tmp/r101-mut7/s01work-d/export_prod_s01.pck", "--script", "res://_census.gd"], out3, false)
	print("GD_NOSTDERR rc=%d lines=%d" % [rc3, out3.size()])
	var out4: Array = []
	var rc4 := OS.execute(OS.get_executable_path(), ["--version"], out4, true)
	print("GD_VER rc=%d lines=%d first=[%s]" % [rc4, out4.size(), String(out4[0]) if out4.size() > 0 else ""])
	quit(0)
