#!/usr/bin/env python3
"""r103 S3-R97 — F6 identity + discrimination probe.

Replays the run_battery.py staging recipe (fixture copy, project-name munge,
controls/pickup.tscn staging, causal-chain two-frame readiness fix) into
per-side scratch trees under /var/tmp/r103c-S3/s3r97, swaps
r97_scene_marker.gd for the side's bytes, then launches the single row

    godot --headless --path <scratch> --script res://stree_lattice.gd -- --arm=scene_probe

which is the only r97 row that loads the marker fixture (via r97_scene_a/b.tscn).
Compares merged stdout+stderr bytes and exit codes across sides and reps.

run_battery.py itself is never executed (hard rule 1).
"""
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

SRC = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures")
WT = Path("/var/tmp/r103c-S3/repo")           # worktree carrying the applied patch
WORK = Path("/var/tmp/r103c-S3/s3r97")
FIXTURE = "r97_scene_marker.gd"
REPS = 3
BOUND = 8

COMMITTED = (SRC / FIXTURE).read_bytes()
FOLDED = (WT / "corpus/fixtures" / FIXTURE).read_bytes()


def tooth_extends() -> bytes:
    return FOLDED.replace(b"extends Node2D\n", b"", 1)


def tooth_ready_print() -> bytes:
    return FOLDED + b'\nfunc _ready() -> void:\n\tprint("R97_F6_TOOTH")\n'


def tooth_tag_export() -> bytes:
    return FOLDED.replace(b"@export var tag", b"var tag", 1)


SIDES = {
    "committed": COMMITTED,
    "folded": FOLDED,
    "tooth_no_extends": tooth_extends(),
    "tooth_ready_print": tooth_ready_print(),
    "tooth_tag_no_export": tooth_tag_export(),
}


def stage(label: str, marker: bytes) -> Path:
    scratch = WORK / label
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    for item in sorted(SRC.iterdir()):
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, scratch / item.name)
        else:
            shutil.copy2(item, scratch / item.name)
    project_file = scratch / "project.godot"
    text = project_file.read_text()
    assert 'config/name="MechanicOneShotTest"' in text
    project_file.write_text(
        text.replace('config/name="MechanicOneShotTest"',
                     f'config/name="MechanicOneShotTest-r103s3r97-{label}"', 1))
    shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn")
    chain = scratch / "causal_chain.gd"
    ctext = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in ctext, "causal fixture changed"
    chain.write_text(ctext.replace(anchor, "    await process_frame\n" + anchor, 1))
    assert (scratch / FIXTURE).exists(), f"{FIXTURE} must land in scratch"
    (scratch / FIXTURE).write_bytes(marker)
    return scratch


def run(scratch: Path):
    cmd = ["godot", "--headless", "--path", str(scratch), "--script",
           "res://stree_lattice.gd", "--", "--arm=scene_probe"]
    started = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=BOUND)
        out, err, code, note = proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or b""
        err = exc.stderr or b""
        code, note = None, f"TIMEOUT after {BOUND}s"
    return {
        "command": " ".join(cmd),
        "seconds": round(time.time() - started, 2),
        "stdout_sha256": hashlib.sha256(out).hexdigest(),
        "stderr_sha256": hashlib.sha256(err).hexdigest(),
        "merged_sha256": hashlib.sha256(out + err).hexdigest(),
        "stdout_bytes": len(out),
        "stderr_bytes": len(err),
        "exit": code,
        "note": note,
        "stdout_text": out.decode(errors="replace"),
        "stderr_text": err.decode(errors="replace"),
    }


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    report = {
        "fixture": FIXTURE,
        "fixture_sha256": {
            "committed_HEAD": hashlib.sha256(COMMITTED).hexdigest(),
            "folded_F6_applied": hashlib.sha256(FOLDED).hexdigest(),
        },
        "side_sha256": {k: hashlib.sha256(v).hexdigest() for k, v in SIDES.items()},
        "reps": REPS,
        "sides": {},
    }
    for label, marker in SIDES.items():
        scratch = stage(label, marker)
        reps = [run(scratch) for _ in range(REPS)]
        report["sides"][label] = reps
        status = "STABLE" if len({r["merged_sha256"] for r in reps}) == 1 else "UNSTABLE"
        print(f"{label:20s} {status} exit={reps[0]['exit']} "
              f"merged={reps[0]['merged_sha256'][:16]} {reps[0]['seconds']}s", flush=True)

    def merged(label):
        return report["sides"][label][0]["merged_sha256"]

    def exit_of(label):
        return report["sides"][label][0]["exit"]

    report["checks"] = {
        "committed_eq_folded": merged("committed") == merged("folded"),
        "committed_exit_eq_folded": exit_of("committed") == exit_of("folded"),
        "tooth_no_extends_differs": merged("tooth_no_extends") != merged("committed"),
        "tooth_ready_print_differs": merged("tooth_ready_print") != merged("committed"),
        "tooth_tag_no_export_differs": merged("tooth_tag_no_export") != merged("committed"),
        "all_sides_stable": all(
            len({r["merged_sha256"] for r in report["sides"][s]}) == 1 for s in SIDES),
    }
    (WORK / "result.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report["checks"], indent=2), flush=True)
    print(f"result.json -> {WORK / 'result.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
