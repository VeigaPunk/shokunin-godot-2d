#!/usr/bin/env python3
"""r103-CRIT1 mutant driver — attacks on the export_div family (receipt forgery classes).

Runs each mutant against a SCRATCH COPY of corpus/fixtures (/var/tmp/r103-crit1/fxc);
the repo file is never touched (original text is restored from the repo after each run).

Classes:
  M1  s01 ident  — CLI run faked via cp of the preset sidecar + forged "[ DONE ]" log
  M1b s01 ident  — same cp forgery, log without engine banner (gate control)
  M2  s02 xdg    — XDG_DATA_HOME dropped from the child env (isolation spoof)
  M3  s03 seq    — foreign preset beacon appended to pack A (contamination)
  M4  s04 pck    — artifact flags byte flipped post-export (census-echo control)

Usage: r103-crit1_mutants.py [M1 M1b M2 M3 M4 ...]   (default: all)
"""
import pathlib
import shutil
import subprocess
import sys
import os

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FXC = pathlib.Path("/var/tmp/r103-crit1/fxc")
ROOT = "/var/tmp/r103-crit1/mutroot"
GODOT = "/usr/bin/godot"


def patch(name, text, old, new):
    if old not in text:
        raise SystemExit("MISSING anchor in %s: %r" % (name, old[:60]))
    if text.count(old) != 1:
        raise SystemExit("AMBIGUOUS anchor in %s (%d)" % (name, text.count(old)))
    return text.replace(old, new)


FORGE_HELPER = '''

func _forge_cli(sidecar: String, slug: String, name: String) -> String:
	var out_dir := _out_dir(slug)
	_clear_dir(out_dir)
	_mkdir(out_dir)
	var out_path := out_dir.path_join(name)
	var src := FileAccess.open(sidecar, FileAccess.READ)
	var dst := FileAccess.open(out_path, FileAccess.WRITE)
	dst.store_buffer(src.get_buffer(src.get_length()))
	src.close()
	dst.close()
	_write_text(_log_path("export_" + slug), "%s\\n")
	return out_path
'''


def mut_s01(forged_banner):
    src = REPO / "corpus/fixtures/export_div_s01.gd"
    f = FXC / "export_div_s01.gd"
    t = src.read_text()
    t = patch("s01", t,
              '\tvar cli := _export_pack("ident_cli", PRESET_EMBED, "cli.pck")',
              '\tvar cli := _forge_cli(sidecar, "ident_cli", "cli.pck")')
    t += FORGE_HELPER % forged_banner
    f.write_text(t)
    return "s01", "ident"


CONTAM_HELPER = '''

func _contaminate(path: String, beacon: String) -> void:
	var f := FileAccess.open(path, FileAccess.READ_WRITE)
	f.seek_end()
	f.store_buffer(beacon.to_utf8_buffer())
	f.close()
'''

FLAGS_HELPER = '''

func _mutate_flags(path: String) -> void:
	var f := FileAccess.open(path, FileAccess.READ_WRITE)
	var b := f.get_buffer(24)
	b[20] = b[20] + 1
	f.seek(0)
	f.store_buffer(b)
	f.close()
'''


def mut_s02():
    src = REPO / "corpus/fixtures/export_div_s02.gd"
    f = FXC / "export_div_s02.gd"
    t = src.read_text()
    t = patch("s02", t,
              'var env_b := "env XDG_DATA_HOME=" + _q(xdg_b) + " HOME=" + _q(home_a) + " "',
              'var env_b := "env HOME=" + _q(home_a) + " "')
    f.write_text(t)
    return "s02", "xdg"


def mut_s03():
    src = REPO / "corpus/fixtures/export_div_s03.gd"
    f = FXC / "export_div_s03.gd"
    t = src.read_text()
    t = patch("s03", t,
              '\tvar a := _analyze(_out_dir().path_join(OUT_A), TAG_PCK, BEACON_PCK, TAG_EMB, BEACON_EMB)',
              '\t_contaminate(_out_dir().path_join(OUT_A), BEACON_EMB)\n'
              '\tvar a := _analyze(_out_dir().path_join(OUT_A), TAG_PCK, BEACON_PCK, TAG_EMB, BEACON_EMB)')
    t += CONTAM_HELPER
    f.write_text(t)
    return "s03", "seq"


def mut_s04():
    src = REPO / "corpus/fixtures/export_div_s04.gd"
    f = FXC / "export_div_s04.gd"
    t = src.read_text()
    t = patch("s04", t,
              '\t_diag("artifact", pck_path)',
              '\t_mutate_flags(pck_path)\n\t_diag("artifact", pck_path)')
    t += FLAGS_HELPER
    f.write_text(t)
    return "s04", "pck"


MUTS = {
    "M1": lambda: mut_s01("[ DONE ] savepack"),
    "M1b": lambda: mut_s01("cp done"),
    "M2": mut_s02,
    "M3": mut_s03,
    "M4": mut_s04,
}


def run(key):
    fx, arm = MUTS[key]()
    out = pathlib.Path("/var/tmp/r103-crit1/mut-%s-%s.out" % (key, fx))
    env = dict(os.environ)
    env["EXPORT_DIV_ROOT"] = "%s/mut-%s-%s" % (ROOT, key, fx)
    with out.open("w") as fh:
        rc = subprocess.run([GODOT, "--headless", "--path", str(FXC),
                             "--script", "res://export_div_%s.gd" % fx, "--", "--arm=" + arm],
                            stdout=fh, stderr=subprocess.STDOUT, env=env, timeout=120).returncode
    # restore scratch copy from repo
    shutil.copyfile(REPO / ("corpus/fixtures/export_div_%s.gd" % fx), FXC / ("export_div_%s.gd" % fx))
    line = "<no PASS/FAIL line>"
    for ln in out.read_text(errors="replace").splitlines():
        if ln.startswith("PASS ") or ln.startswith("FAIL "):
            line = ln
    print("%s fixture=%s arm=%s rc=%d" % (key, fx, arm, rc))
    print("   " + line[:400])
    return line


if __name__ == "__main__":
    keys = sys.argv[1:] or list(MUTS)
    if not FXC.exists():
        system_exit = "scratch copy missing: cp -a corpus/fixtures %s" % FXC
        raise SystemExit(system_exit)
    for k in keys:
        run(k)
