#!/usr/bin/env python3
"""r88 BOUNDARY seat runner.

Every run is a fresh process: `timeout -s KILL 25 godot --headless --path <proj> --script <res> ...`
Split .out/.err/.rc/.wall receipts under runs/.

Two dispatch shapes:
  own      : my probes, arm via `-- --arm=<name>` (OS.get_cmdline_user_args, battery convention)
  scout    : the scout's r88_probe.gd verbatim, arm in engine-arg position (`--arm <name>`),
             because that script reads OS.get_cmdline_args().
"""
import argparse
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent  # corpus/live/<seat> -> repo root
GODOT = "/usr/bin/godot"
PROJ = HERE / "proj"
SCOUT_PROJ = REPO / "corpus/live/r88-scout/proj"
RUNS = HERE / "runs"
TIMEOUT_S = 25

# tag, kind, script, arm, reps, extra user args
PLAN = [
    ("b88_mp.mp_lb", "own", "b88_mp.gd", "mp_lb", 6, []),
    ("b88_mp.mp_names", "own", "b88_mp.gd", "mp_names", 3, []),
    ("b88_mp.mp_cycles", "own", "b88_mp.gd", "mp_cycles", 3, []),
    ("b88_mp.mp_genid", "own", "b88_mp.gd", "mp_genid", 3, []),
    ("b88_mp.mp_offline", "own", "b88_mp.gd", "mp_offline", 3, []),
    ("b88_light.hang_min", "own", "b88_light.gd", "hang_min", 3, []),
    ("b88_light.fixed", "own", "b88_light.gd", "fixed", 6, []),
    ("b88_light.fixed_sync", "own", "b88_light.gd", "fixed_sync", 3, []),
    ("b88_light.fixed_sync_delay", "own", "b88_light.gd", "fixed_sync", 3, ["--delay=200"]),
    ("b88_light.control", "own", "b88_light.gd", "control", 3, []),
    ("b88_audio.timeline", "own", "b88_audio.gd", "timeline", 6, []),
    ("b88_vis.base", "own", "b88_vis.gd", "base", 6, []),
    ("b88_vis.variants", "own", "b88_vis.gd", "variants", 3, []),
    ("b88_vis.forcedraw", "own", "b88_vis.gd", "forcedraw", 3, []),
    ("b88_sprite.oob0", "own", "b88_sprite.gd", "oob0", 3, []),
    ("b88_sprite.oob1", "own", "b88_sprite.gd", "oob1", 3, []),
    ("b88_sprite.oob2", "own", "b88_sprite.gd", "oob2", 3, []),
    ("b88_sprite.oob3", "own", "b88_sprite.gd", "oob3", 6, []),
    ("b88_sprite.oobneg", "own", "b88_sprite.gd", "oobneg", 3, []),
    ("b88_sprite.phys", "own", "b88_sprite.gd", "phys", 6, []),
    ("b88_sprite.fall", "own", "b88_sprite.gd", "fall", 3, []),
    ("b88_sprite.fall_delay", "own", "b88_sprite.gd", "fall", 3, ["--delay=200"]),
    ("b88_sprite.fall_anchor", "own", "b88_sprite.gd", "fall_anchor", 3, []),
    ("b88_sprite.fall_anchor_delay", "own", "b88_sprite.gd", "fall_anchor", 3, ["--delay=200"]),
    ("b88_sprite.fall_sync", "own", "b88_sprite.gd", "fall_sync", 3, []),
    ("b88_sprite.fall_sync_delay", "own", "b88_sprite.gd", "fall_sync", 3, ["--delay=200"]),
    ("b88_sprite.meta", "own", "b88_sprite.gd", "meta", 3, []),
    ("verbatim.light_props_hang", "scout", None, "light_props", 3, []),
    ("verbatim.light_props_fix", "scout", "r88_probe_fix.gd", "light_props", 6, []),
    ("verbatim.rb_gravity", "scout", None, "rb_gravity", 6, []),
    ("verbatim.sprite_phys", "scout", None, "sprite_phys", 6, []),
    ("verbatim.mp_loopback", "scout", None, "mp_loopback", 6, []),
    ("verbatim.audio_pos", "scout", None, "audio_pos", 6, []),
    ("verbatim.vis_not", "scout", None, "vis_not", 6, []),
]


def build_cmd(kind: str, script: str, arm: str, extra: list[str]) -> list[str]:
    if kind == "own":
        cmd = [GODOT, "--headless", "--path", str(PROJ), "--script", f"res://{script}",
               "--", f"--arm={arm}"] + extra
    else:
        res = script or "r88_probe.gd"
        cmd = [GODOT, "--headless", "--path", str(SCOUT_PROJ), "--script", f"res://{res}",
               "--arm", arm]
    return ["timeout", "-s", "KILL", str(TIMEOUT_S)] + cmd


def run_one(tag: str, rep: int, cmd: list[str]) -> tuple[int, float]:
    out = RUNS / f"{tag}.rep{rep}.out"
    err = RUNS / f"{tag}.rep{rep}.err"
    rc = RUNS / f"{tag}.rep{rep}.rc"
    wall = RUNS / f"{tag}.rep{rep}.wall"
    t0 = time.monotonic()
    with open(out, "wb") as fo, open(err, "wb") as fe:
        p = subprocess.run(cmd, stdout=fo, stderr=fe)
    dt = time.monotonic() - t0
    rc.write_text(f"{p.returncode}\n")
    wall.write_text(f"{dt:.3f}\n")
    return p.returncode, dt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="substring filter on tag")
    ap.add_argument("--reps", type=int, default=0, help="override reps (smoke)")
    ap.add_argument("--extra", default="", help="extra user args for own probes")
    args = ap.parse_args()

    RUNS.mkdir(parents=True, exist_ok=True)
    for tag, kind, script, arm, reps, extra in PLAN:
        if args.only and args.only not in tag:
            continue
        n = args.reps if args.reps else reps
        rcs = []
        for rep in range(n):
            extra_args = list(extra)
            if args.extra:
                extra_args += args.extra.split()
            cmd = build_cmd(kind, script, arm, extra_args)
            rc, dt = run_one(tag, rep, cmd)
            rcs.append(rc)
            print(f"  {tag} rep{rep} rc={rc} wall={dt:.2f}s", flush=True)
        print(f"done {tag} rc={rcs}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
