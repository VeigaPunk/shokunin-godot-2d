#!/usr/bin/env python3
"""r101 VER-5 — reproduce the cells 1-7 contamination bisection for r100b_seq.gd.

Reads the frozen fixture (never modifies the repo), writes scratch variants under
/tmp/r101-ver5/, and runs each with godot --headless. The variants:

  v1: add the missing RIGHT-button release after routing's s9 push.
  v2: add a release after the cursor cell's parsed ScreenTouch press (c6).
  v3: both edits.
  v5: debug instrumentation (prints, per sink, the last _gui_input entry) at
      motion m1, localpos push 1/2, and clip presses at x=62 / x=90.

Usage: python3 reports/round-101/mutations/r101-ver5_bisect.py [--run]
  without --run only the variants are written; with --run the four Godot runs
  are executed and the DBG_* / PASS lines are printed.

Expected (observed 2026-10-18, load ~39): v1 restores motion m1/m2/m3, localpos
push 1, and clip (90,4)->FA; v2 leaves cells 1-7 unchanged but loses all clip
presses; v5 shows routing P receiving motion m1 and localpos push 1 while the
hovered control is S/C, and the clip's own ED receiving the (90,4) press.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIXTURE = REPO / "corpus/fixtures/r100b_seq.gd"
PROJECT = REPO / "corpus/live/r100-boundary/proj/project.godot"
SCRATCH = Path("/tmp/r101-ver5")

REL_RB = '\troot.push_input(rb)\n\tawait process_frame\n\tout.append("s9_rb'
REL_RB_NEW = ('\troot.push_input(rb)\n\tvar rb2 := _mb(Vector2(8, 8), false)\n'
              '\trb2.button_index = MOUSE_BUTTON_RIGHT\n\troot.push_input(rb2)\n'
              '\tawait process_frame\n\tout.append("s9_rb')
TOUCH_REL = ('\tInput.parse_input_event(st)\n\tawait process_frame\n'
             '\tout.append("c6_parse_st')
TOUCH_REL_NEW = ('\tInput.parse_input_event(st)\n\tawait process_frame\n'
                 '\tvar st2 := InputEventScreenTouch.new()\n\tst2.index = 0\n'
                 '\tst2.pressed = false\n\tst2.position = Vector2(44, 44)\n'
                 '\tInput.parse_input_event(st2)\n\tawait process_frame\n'
                 '\tout.append("c6_parse_st')

DBG_HELPER = '''
func _dbg_sinks() -> String:
	var out: Array = []
	for i in range(_nodes.size()):
		var n = _nodes[i]
		if is_instance_valid(n) and n is Sink:
			var s := n as Sink
			if not s.log.is_empty():
				out.append("%d:%s:n%d:LAST=%s" % [i, s.tag, s.log.size(), s.log[-1]])
	out.append("hovered=%s" % _tag_of(root.gui_get_hovered_control()))
	return " | ".join(out)


'''


def write_variant(name: str, text: str) -> Path:
    d = SCRATCH / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "project.godot").write_text(PROJECT.read_text())
    (d / "r100b_seq.gd").write_text(text)
    return d


def main() -> int:
    src = FIXTURE.read_text()
    assert 'func _mk_sink(' in src
    v1 = src.replace(REL_RB, REL_RB_NEW, 1)
    v2 = src.replace(TOUCH_REL, TOUCH_REL_NEW, 1)
    v3 = v1.replace(TOUCH_REL, TOUCH_REL_NEW, 1)
    assert v1 != src and v2 != src and v3 != v1, "edit pattern miss"

    dbg = src.replace('func _mk_sink(', DBG_HELPER + 'func _mk_sink(', 1)
    e = '\troot.push_input(_mm(Vector2(10, 10), Vector2(5, 7)))\n\tawait process_frame\n\tout.append("m1[%s]" % _fmt(s.log))'
    dbg = dbg.replace(e, e + '\n\tprint("DBG_M1 " + _dbg_sinks())', 1)
    e = '\troot.push_input(_mb(Vector2(30, 14), true))\n\tawait process_frame\n\tout.append("lp_push_p[%s] c[%s] loc_c=%.1f,%.1f" % ['
    dbg = dbg.replace(e, '\troot.push_input(_mb(Vector2(30, 14), true))\n\tawait process_frame\n\tprint("DBG_LP1 " + _dbg_sinks())\n\tout.append("lp_push_p[%s] c[%s] loc_c=%.1f,%.1f" % [', 1)
    e = '\troot.push_input(_mb(Vector2(30, 14), true), true)\n\tawait process_frame\n\tout.append("lp_push_local_p[%s] c[%s]" % [_fmt(parent.log), _fmt(child.log)])'
    dbg = dbg.replace(e, '\troot.push_input(_mb(Vector2(30, 14), true), true)\n\tawait process_frame\n\tprint("DBG_LP2 " + _dbg_sinks())\n\tout.append("lp_push_local_p[%s] c[%s]" % [_fmt(parent.log), _fmt(child.log)])', 1)
    e = '\t\tout.append("cp_press%s in=%s ed=%s fa=%s" % [\n\t\t\tstr(p), _fmt(inb.log), _fmt(ed.log), _fmt(fa.log)])'
    dbg = dbg.replace(e, e + '\n\t\tif p.x == 62.0 or p.x == 90.0:\n\t\t\tprint("DBG_CLIP_%d " % int(p.x) + _dbg_sinks())', 1)
    assert dbg.count("DBG_") == 4, dbg.count("DBG_")

    dirs = {n: write_variant(n, t) for n, t in
            (("v1", v1), ("v2", v2), ("v3", v3), ("v5", dbg))}
    print("variants written:", ", ".join(str(p) for p in dirs.values()))
    if "--run" not in sys.argv:
        return 0
    for name, d in dirs.items():
        out = SCRATCH / f"{name}.out"
        err = SCRATCH / f"{name}.err"
        rc = subprocess.run(
            ["godot", "--headless", "--path", str(d), "--script", "res://r100b_seq.gd", "--", "--clean=0"],
            stdout=out.open("wb"), stderr=err.open("wb")).returncode
        print(f"{name} rc={rc}")
        for ln in out.read_text().splitlines():
            if ln.startswith(("DBG_", "PASS r100_gui motion", "PASS r100_gui localpos",
                              "PASS r100_gui clip", "PASS r100_gui hover")):
                print(" ", ln[:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
