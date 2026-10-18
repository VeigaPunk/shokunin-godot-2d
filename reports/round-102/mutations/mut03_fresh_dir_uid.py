#!/usr/bin/env python3
"""mut03 companion — fresh-dir embedded-export UID nondeterminism evidence.

Exports the same minimal project (embed_pck=true) from two pristine dirs and
compares the embedded binaries byte-for-byte. Companion to
mut03_dead_measure_launch.py; cites why receipt sha pins must be warm-warm.
"""
import hashlib
import shutil
import subprocess
from pathlib import Path

ROOT = Path("/var/tmp/r102-mut3/freshuid")
PROJECT_GODOT = 'config_version=5\n\n[application]\n\nconfig/name="freshuid"\nconfig/features=PackedStringArray("4.7")\nrun/main_scene="res://main.tscn"\n'
MAIN_GD = 'extends Node\n\nfunc _ready() -> void:\n\tprint("EXPORT_LAUNCH_READY scene=fixture")\n'
MAIN_TSCN = '[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://main.gd" id="1"]\n\n[node name="Main" type="Node"]\nscript = ExtResource("1")\n'
PRESETS = '[preset.0]\n\nname="Linux/X11"\nplatform="Linux/X11"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=""\nexport_filter="all_resources"\ninclude_filter=""\nexclude_filter=""\nexport_path=""\n\n[preset.0.options]\n\nbinary_format/architecture="x86_64"\nbinary_format/embed_pck=true\n'


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    shas = {}
    for tag in ("a", "b"):
        proj = ROOT / tag
        proj.mkdir(parents=True)
        (proj / "project.godot").write_text(PROJECT_GODOT)
        (proj / "main.gd").write_text(MAIN_GD)
        (proj / "main.tscn").write_text(MAIN_TSCN)
        (proj / "export_presets.cfg").write_text(PRESETS)
        out = proj / "out"
        out.mkdir(parents=True, exist_ok=True)
        inner = proj / "inner.sh"
        inner.write_text("mount -t tmpfs tmpfs /tmp || exit 91\ncd %s\nexec /usr/bin/godot --headless --path %s --export-debug Linux/X11 %s\n" % (proj, proj, out / "launch.x86_64"))
        cmd = ["unshare", "-m", "--map-root-user", "/usr/bin/sh", str(inner)]
        print("CMD:", " ".join(cmd))
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        exe = out / "launch.x86_64"
        data = exe.read_bytes()
        shas[tag] = hashlib.sha256(data).hexdigest()
        print("fresh_%s rc=%d bytes=%d sha256=%s uid_file=%s" % (
            tag, proc.returncode, len(data), shas[tag],
            (proj / "main.gd.uid").read_text().strip() if (proj / "main.gd.uid").exists() else "none"))
    a = (ROOT / "a" / "out" / "launch.x86_64").read_bytes()
    b = (ROOT / "b" / "out" / "launch.x86_64").read_bytes()
    diffs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    print("size_equal=%s sha_equal=%s diff_bytes=%d offsets=%s" % (
        len(a) == len(b), shas["a"] == shas["b"], len(diffs), diffs[:24]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
