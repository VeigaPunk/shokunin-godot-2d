#!/usr/bin/env python3
"""r100-boundary: build probes/r100b_seq.gd from the frozen scout probe.

The seq probe is the scout probe (byte-identical cell functions) with `_run`
replaced by a loop that runs all 14 cells in one process, optionally with the
scout's `_cleanup()` between cells (`--clean=1`).  It exists to measure
cross-cell contamination of the 14 payloads (fresh-process vs same-process).
"""
import hashlib
import pathlib

HERE = pathlib.Path(__file__).parent
SRC = HERE / "proj" / "r100_gui.gd"
DST = HERE / "probes" / "r100b_seq.gd"

ARMS = ["census", "routing", "hover", "motion", "localpos", "cursor", "clip",
        "drag", "touch", "subvp", "warp", "focus", "render", "osmeta"]

src = SRC.read_text()
start = src.index("func _run() -> void:")
end = src.index("func _cleanup() -> void:")
assert start < end

match_body = "\n".join(
    '\t\t\t"%s":\n\t\t\t\tawait _cell_%s()' % (a, a) for a in ARMS)
new_run = f'''func _run() -> void:
	var seq_arms := {ARMS!r}
	var do_clean := 0
	for a in OS.get_cmdline_user_args():
		if a == "--clean=1":
			do_clean = 1
	for a in seq_arms:
		arm = a
		match arm:
{match_body}
			_:
				pass
		if do_clean == 1:
			await _cleanup()
	print("SEQ_DONE clean=%d" % do_clean)
	await _cleanup()
	quit(0)


'''
out = src[:start] + new_run + src[end:]
DST.write_text(out)
print(f"src={SRC.name} sha256={hashlib.sha256(src.encode()).hexdigest()}")
print(f"seq={DST.name} sha256={hashlib.sha256(out.encode()).hexdigest()} bytes={len(out)}")
