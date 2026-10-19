#!/usr/bin/env python3
"""r103-S3: stage one targeted scratch project exactly as run_battery.py main()
stages its scratch tree (fixture copy, config/name munge, controls/pickup.tscn
root staging, causal_chain two-frame readiness fix), with an optional marker
variant substituted for r97_scene_marker.gd.

usage: stage_targeted.py <fixtures_dir> <dst> <marker_variant|KEEP|MISSING>
"""
import pathlib
import shutil
import sys

src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])
marker = sys.argv[3]

if dst.exists():
    shutil.rmtree(dst)
dst.mkdir(parents=True)
for item in src.iterdir():
    if item.name == "run_battery.py" or item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, dst / item.name)
    else:
        shutil.copy2(item, dst / item.name)
project_file = dst / "project.godot"
text = project_file.read_text()
assert 'config/name="MechanicOneShotTest"' in text
text = text.replace('config/name="MechanicOneShotTest"',
                    'config/name="MechanicOneShotTest-r103S3"', 1)
project_file.write_text(text)
shutil.copy2(dst / "controls" / "pickup.tscn", dst / "pickup.tscn")
chain = dst / "causal_chain.gd"
ctext = chain.read_text()
anchor = "    await process_frame\n    var old := current_scene"
assert anchor in ctext, "causal fixture changed; cannot apply scratch-only readiness fix"
chain.write_text(ctext.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
if marker == "MISSING":
    (dst / "r97_scene_marker.gd").unlink()
elif marker != "KEEP":
    shutil.copy2(marker, dst / "r97_scene_marker.gd")
print(f"staged {dst} marker={marker}")
