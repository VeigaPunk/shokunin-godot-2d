#!/usr/bin/env python3
"""r103 M2 / mut02 - user:// spoof mutation for E2 (XDG override silently not applied).

Mandate: the E2 divergence row family (`export_div_s02`: exported-project user://
isolation under an explicit XDG_DATA_HOME override) must REJECT an arm whose
evidence claims `xdg_honored` while the override was silently not applied.

This script (replayable, ~60 s):
  1. builds + exports the real 4.7.2 Linux/X11 artifact for a minimal project
     whose main.gd prints its actual `OS.get_user_data_dir()` and writes+reads
     a user:// marker;
  2. runs the EXPORTED binary under env-varied arms (default HOME, XDG ok,
     XDG empty string, XDG relative, XDG-as-file, XDG unwritable dir) plus
     text-forging spoof wrappers (real run with override silently dropped,
     and a no-run forger);
  3. runs an in-engine replica (`probe.gd`, the `OS.execute` + `/usr/bin/env`
     idiom E2 will use) over genuine and spoof arms, emitting the exact
     ROW/CLASS/FIXTURE_STYLE lines a fixture-style classifier would print;
  4. writes /var/tmp/r103-mut2/out/mut02_verdicts.json (full shas, clause
     matrix) and prints a summary.

Scratch: /var/tmp/r103-mut2 (never /tmp; this host has an EDQUOT /tmp quota).
Override the root with `MUT02_ROOT=<dir>` to run isolated from concurrent
sibling seats that share the default root (their wipe() would clobber ours).
Never runs run_battery.py; touches no shared file.
"""

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("MUT02_ROOT", "/var/tmp/r103-mut2"))
PROJ = ROOT / "proj"
OUT = ROOT / "out"
LOGS = ROOT / "logs"
HOME_DEFAULT = ROOT / "home-default"
XDG_OK = ROOT / "xdg-ok"
XDG_REL = "rel-xdg"
XDG_FILE = ROOT / "xdg-file"
XDG_RO = ROOT / "xdg-ro"
NAME = "Mut2Probe"
MARKER = "mut2_marker.txt"
APP = OUT / "app.x86_64"
PCK = OUT / "app.pck"
GODOT = "godot"
TEMPLATE = Path.home() / ".local/share/godot/export_templates/4.7.2.stable/linux_release.x86_64"

PROJECT_GODOT = '''config_version=5

[application]
config/name="Mut2Probe"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")

[display]
window/size/viewport_width=320
window/size/viewport_height=180
'''

MAIN_GD = '''extends Node

func _ready() -> void:
	var dir := OS.get_user_data_dir()
	print("MUT2_USERDIR %s" % dir)
	var f := FileAccess.open("user://mut2_marker.txt", FileAccess.WRITE)
	if f == null:
		print("MUT2_WRITE ok=false err=%d" % FileAccess.get_open_error())
	else:
		f.store_string("r103-mut2 marker\\n")
		f.close()
		var back := FileAccess.get_file_as_string("user://mut2_marker.txt")
		print("MUT2_WRITE ok=true bytes=%d readback=%s" % [back.length(), str(back.strip_edges())])
	get_tree().quit()
'''

MAIN_TSCN = '''[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://main.gd" id="1"]

[node name="Main" type="Node"]
script = ExtResource("1")
'''

EXPORT_PRESETS = '''[preset.0]
name="Linux/X11"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""

[preset.0.options]
binary_format/architecture="x86_64"
binary_format/embed_pck=false
'''

PROBE_GD = '''extends SceneTree
# r103-mut02 scratch replica of the E2 classification layer: runs the exported
# child through the OS.execute + /usr/bin/env idiom and checks whether the
# user:// marker actually landed under the XDG override root.
const XDG := "@XDG@"
const HOME_DEFAULT := "@HOME@"
const APP := "@APP@"
const OUTDIR := "@OUT@"
const ROOT := "@ROOT@"
const NAME := "Mut2Probe"
const MARKER := "mut2_marker.txt"

var arm := ""


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _q(s: String) -> String:
	return "'" + s.replace("'", "'\\\\''") + "'"


func _userdir_lines(text: String) -> PackedStringArray:
	var out: PackedStringArray = []
	for line in text.split("\\n"):
		if line.begins_with("MUT2_USERDIR "):
			out.append(line.substr(13).strip_edges())
	return out


func _run() -> void:
	var xdg_marker := XDG.path_join("godot").path_join("app_userdata").path_join(NAME).path_join(MARKER)
	var def_marker := HOME_DEFAULT.path_join(".local").path_join("share").path_join("godot").path_join("app_userdata").path_join(NAME).path_join(MARKER)
	DirAccess.remove_absolute(xdg_marker)
	DirAccess.remove_absolute(def_marker)
	var log := ROOT.path_join("out").path_join("probe_" + arm + ".log")
	var inner := ""
	if arm == "genuine":
		inner = "/usr/bin/env " + _q("XDG_DATA_HOME=" + XDG) + " " + _q(APP) + " --headless --quit-after 60"
	elif arm == "spoof":
		inner = _q(OUTDIR.path_join("spoof.sh"))
	else:
		print("FAIL probe unknown_arm")
		quit(1)
		return
	var body := "cd " + _q(OUTDIR) + "\\nexec > " + _q(log) + " 2>&1\\n" + inner
	var rc := OS.execute("/usr/bin/sh", PackedStringArray(["-c", body]))
	var text := FileAccess.get_file_as_string(log)
	var dirs := _userdir_lines(text)
	var first := dirs[0] if dirs.size() > 0 else ""
	var last := dirs[dirs.size() - 1] if dirs.size() > 0 else ""
	var marker_xdg := FileAccess.file_exists(xdg_marker)
	var marker_def := FileAccess.file_exists(def_marker)
	var first_prefix := XDG != "" and first.begins_with(XDG)
	var last_prefix := XDG != "" and last.begins_with(XDG)
	var claim := text.contains("MUT2_XDG_HONORED")
	var naive_pass := rc == 0 and (claim or last_prefix)
	var anchored_pass := rc == 0 and marker_xdg and not marker_def and first_prefix
	print("PROBE_ROW arm=%s rc=%d dirs=%d first=%s last=%s marker_xdg=%s marker_default=%s claim=%s" % [arm, rc, dirs.size(), first, last, str(marker_xdg), str(marker_def), str(claim)])
	print("PROBE_CLASS arm=%s first_prefix=%s last_prefix=%s disk_xdg=%s disk_default=%s" % [arm, str(first_prefix), str(last_prefix), str(marker_xdg), str(marker_def)])
	print("PROBE_STYLE arm=%s naive_pass=%s anchored_pass=%s" % [arm, str(naive_pass), str(anchored_pass)])
	quit(0)
'''


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(cmd, env=None, cwd=None, timeout=60):
    t0 = time.monotonic()
    p = subprocess.run(cmd, env=env, cwd=cwd, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=timeout)
    return {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
            "wall_ms": int((time.monotonic() - t0) * 1000)}


def base_env(**overrides):
    env = os.environ.copy()
    env.pop("XDG_DATA_HOME", None)
    env["HOME"] = str(HOME_DEFAULT)
    for k, v in overrides.items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = v
    return env


def wipe(path: Path):
    if not path.exists():
        return
    for dirpath, dirnames, _ in os.walk(path, topdown=False):
        for d in dirnames:
            try:
                os.chmod(os.path.join(dirpath, d), 0o755)
            except OSError:
                pass
    shutil.rmtree(path, ignore_errors=True)


def find_markers():
    out = []
    for dirpath, _dirnames, filenames in os.walk(ROOT):
        if MARKER in filenames:
            out.append(str(Path(dirpath).relative_to(ROOT) / MARKER))
    return sorted(out)


def userdir_lines(stdout_b: bytes):
    out = []
    for line in stdout_b.decode("utf-8", "replace").split("\n"):
        if line.startswith("MUT2_USERDIR "):
            out.append(line[len("MUT2_USERDIR "):].strip())
    return out


def record(name, cmd, env, cwd):
    r = run(cmd, env=env, cwd=cwd)
    rec = {
        "arm": name,
        "command": " ".join(shlex.quote(c) for c in cmd),
        "env_xdg_data_home": env.get("XDG_DATA_HOME"),
        "env_home": env.get("HOME"),
        "cwd": str(cwd),
        "rc": r["rc"],
        "wall_ms": r["wall_ms"],
        "stdout_bytes": len(r["stdout"]),
        "stderr_bytes": len(r["stderr"]),
        "stdout_sha256": sha256_bytes(r["stdout"]),
        "stderr_sha256": sha256_bytes(r["stderr"]),
        "stdout_head": r["stdout"].decode("utf-8", "replace")[:2000],
        "stderr_head": r["stderr"].decode("utf-8", "replace")[:2000],
        "userdir": userdir_lines(r["stdout"]),
        "markers": [],
    }
    return rec, r


def classify(rec):
    home = str(HOME_DEFAULT)
    xdg = str(XDG_OK)
    rel_marker_xdg = "xdg-ok/godot/app_userdata/%s/%s" % (NAME, MARKER)
    rel_marker_def = "home-default/.local/share/godot/app_userdata/%s/%s" % (NAME, MARKER)
    markers = rec["markers"]
    m_xdg = rel_marker_xdg in markers
    m_def = rel_marker_def in markers
    ud = rec["userdir"]
    first = ud[0] if ud else ""
    last = ud[-1] if ud else ""
    claim = "MUT2_XDG_HONORED" in rec["stdout_head"]
    rec["clause"] = {
        "weak_rc0": rec["rc"] == 0,
        "weak_text_claim": claim,
        "weak_any_marker": len(markers) > 0,
        "transcript_first_dir_prefix": bool(first) and first.startswith(xdg),
        "transcript_last_dir_prefix": bool(last) and last.startswith(xdg),
        "disk_marker_under_xdg": m_xdg,
        "disk_marker_under_default_home": m_def,
        "disk_anchored": m_xdg and not m_def,
        "composite_strict": (rec["rc"] == 0 and m_xdg and not m_def
                             and bool(first) and first.startswith(xdg)),
    }
    rec.pop("stdout_head", None)
    return rec


def main():
    t_start = time.monotonic()
    wipe(ROOT)
    for d in (PROJ, OUT, LOGS, HOME_DEFAULT, XDG_OK):
        d.mkdir(parents=True, exist_ok=True)
    # Export templates live under the REAL home; the arms run with
    # HOME=HOME_DEFAULT (the default-resolution law), so expose them there.
    tp_dir = HOME_DEFAULT / ".local/share/godot/export_templates"
    tp_dir.parent.mkdir(parents=True, exist_ok=True)
    if not tp_dir.exists():
        tp_dir.symlink_to(TEMPLATE.parent.parent)
    XDG_FILE.write_text("not a directory\n")
    XDG_RO.mkdir(parents=True, exist_ok=True)
    os.chmod(XDG_RO, 0o555)

    (PROJ / "project.godot").write_text(PROJECT_GODOT)
    (PROJ / "main.gd").write_text(MAIN_GD)
    (PROJ / "main.tscn").write_text(MAIN_TSCN)
    (PROJ / "export_presets.cfg").write_text(EXPORT_PRESETS)
    (PROJ / "probe.gd").write_text(
        PROBE_GD.replace("@XDG@", str(XDG_OK)).replace("@HOME@", str(HOME_DEFAULT))
        .replace("@APP@", str(APP)).replace("@OUT@", str(OUT)).replace("@ROOT@", str(ROOT)))

    host = {}
    host["uptime"] = subprocess.run(["uptime"], stdout=subprocess.PIPE).stdout.decode().strip()
    host["loadavg"] = list(os.getloadavg())
    host["godot_version"] = run([GODOT, "--version"])["stdout"].decode().strip()
    host["template"] = str(TEMPLATE)
    host["template_exists"] = TEMPLATE.is_file()

    work = {}

    imp = run([GODOT, "--headless", "--path", str(PROJ), "--import"], env=base_env())
    work["import"] = {"rc": imp["rc"], "wall_ms": imp["wall_ms"]}

    exp = run([GODOT, "--headless", "--path", str(PROJ), "--export-release",
               "Linux/X11", str(APP)], env=base_env())
    work["export_release"] = {"rc": exp["rc"], "wall_ms": exp["wall_ms"],
                              "stdout_tail": exp["stdout"].decode("utf-8", "replace")[-400:],
                              "stderr": exp["stderr"].decode("utf-8", "replace")}
    artifact_ok = APP.is_file() and PCK.is_file() and PCK.read_bytes()[:4] == b"GDPC"
    work["export_release"]["artifact_ok"] = artifact_ok
    if not artifact_ok:
        # Fallback: cheap pack + byte copy of the stock release template.
        exp2 = run([GODOT, "--headless", "--path", str(PROJ), "--export-pack",
                    "Linux/X11", str(PCK)], env=base_env())
        work["export_pack_fallback"] = {"rc": exp2["rc"], "wall_ms": exp2["wall_ms"]}
        if PCK.is_file() and PCK.read_bytes()[:4] == b"GDPC" and TEMPLATE.is_file():
            if APP.exists():
                APP.unlink()
            shutil.copyfile(TEMPLATE, APP)  # os.link is EXDEV across /home -> /var/tmp
            os.chmod(APP, 0o755)
            artifact_ok = True
    if not artifact_ok:
        print("FATAL: no usable exported artifact", file=sys.stderr)
        sys.exit(2)
    work["app_sha256"] = sha256_bytes(APP.read_bytes()) if APP.stat().st_size < 80_000_000 else "skipped-large"
    work["pck_bytes"] = PCK.stat().st_size

    # --- spoof wrappers -----------------------------------------------------
    spoof_sh = OUT / "spoof.sh"
    spoof_sh.write_text(
        "#!/bin/sh\n"
        "# r103-mut02 spoof: runs the REAL binary with the override silently dropped\n"
        "# (ambient HOME, no XDG_DATA_HOME), then forges the claim lines.\n"
        "cd " + shlex.quote(str(OUT)) + "\n"
        + shlex.quote(str(APP)) + " --headless --quit-after 60\n"
        "rc=$?\n"
        "echo \"MUT2_XDG_HONORED claim=true\"\n"
        "echo \"MUT2_USERDIR " + str(XDG_OK) + "/godot/app_userdata/" + NAME + "\"\n"
        "exit $rc\n")
    os.chmod(spoof_sh, 0o755)
    spoof_norun = OUT / "spoof_norun.sh"
    spoof_norun.write_text(
        "#!/bin/sh\n"
        "# r103-mut02 no-run forger: nothing executes; the transcript is a claim.\n"
        "echo \"MUT2_XDG_HONORED claim=true\"\n"
        "echo \"MUT2_USERDIR " + str(XDG_OK) + "/godot/app_userdata/" + NAME + "\"\n"
        "echo \"MUT2_WRITE ok=true bytes=16 readback=r103-mut2 marker\"\n"
        "exit 0\n")
    os.chmod(spoof_norun, 0o755)

    # --- env-varied arms over the exported binary ---------------------------
    arms = []

    def add(name, cmd, env, cwd):
        for m in find_markers():
            Path(ROOT / m).unlink()
        rec, _ = record(name, cmd, env, cwd)
        rec["markers"] = find_markers()
        arms.append(rec)

    binary = [str(APP), "--headless", "--quit-after", "60"]
    add("default", binary, base_env(), OUT)
    add("xdg_ok", binary, base_env(XDG_DATA_HOME=str(XDG_OK)), OUT)
    add("xdg_empty", binary, base_env(XDG_DATA_HOME=""), OUT)
    add("xdg_relative", binary, base_env(XDG_DATA_HOME=XDG_REL), OUT)
    add("xdg_file", binary, base_env(XDG_DATA_HOME=str(XDG_FILE)), OUT)
    add("xdg_unwritable", binary, base_env(XDG_DATA_HOME=str(XDG_RO)), OUT)
    add("spoof_text", ["/bin/sh", str(spoof_sh)], base_env(), OUT)
    add("spoof_norun", ["/bin/sh", str(spoof_norun)], base_env(), OUT)
    os.chmod(XDG_RO, 0o755)

    arms = [classify(a) for a in arms]

    # --- in-engine replica (the classification layer export_div_s02 will use)
    probe = {}
    for arm in ("genuine", "spoof"):
        p = run([GODOT, "--headless", "--path", str(PROJ), "--script", "res://probe.gd",
                 "--", "--arm=" + arm], env=base_env(), timeout=60)
        lines = [l for l in p["stdout"].decode("utf-8", "replace").split("\n") if l.startswith("PROBE_")]
        probe[arm] = {"rc": p["rc"], "wall_ms": p["wall_ms"], "lines": lines,
                      "stderr": p["stderr"].decode("utf-8", "replace")[:1000]}

    payload = {
        "seat": "r103-mut2 (KEY=M2)",
        "mandate": "user:// spoof for E2 (XDG override silently not applied) must REJECT",
        "date": "2026-10-18",
        "host": host,
        "work": work,
        "arms": arms,
        "probe": probe,
        "replay_seconds": round(time.monotonic() - t_start, 1),
    }
    out_path = OUT / "mut02_verdicts.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n")

    print(json.dumps({"host": host, "import": work["import"], "export": {
        k: v for k, v in work["export_release"].items() if k != "stdout_tail"},
        "arms": [{"arm": a["arm"], "rc": a["rc"], "userdir": a["userdir"],
                  "markers": a["markers"], "clause": a["clause"]} for a in arms],
        "probe": {k: v["lines"] for k, v in probe.items()}}, indent=2))
    print("verdicts: %s (%.1fs)" % (out_path, payload["replay_seconds"]))


if __name__ == "__main__":
    main()
