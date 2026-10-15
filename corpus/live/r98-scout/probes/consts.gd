extends SceneTree
func _initialize() -> void:
	for cls in ["Node", "CanvasItem", "Node2D", "MainLoop"]:
		var out: Array = []
		for c in ClassDB.class_get_integer_constant_list(cls, true):
			var v := ClassDB.class_get_integer_constant(cls, c)
			if v in [10, 11, 13, 17, 18, 19, 27, 30, 31, 32, 33, 35, 2000, 2010, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035]:
				out.append("%d=%s" % [v, c])
		print("CONSTS %s %s" % [cls, ",".join(out)])
	quit()
