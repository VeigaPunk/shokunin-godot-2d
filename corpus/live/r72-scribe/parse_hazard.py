#!/usr/bin/env python3
"""r72-scribe — parse-convention / parse-survival hazard cells under reorder.

Runs three battery-grammar parent modes (reorder_parent.py) and feeds each
captured stream to two merge conventions:

  last_wins  — the tracked battery's own `parse_arms` (imported read-only
               from corpus/fixtures/pygame_battery.py; dict.update per arm)
  first_wins — a line-streaming convention (first ARM line for a key wins)

Modes:
  arm_lines   buffered parent; descendant emits a complete ARM line first
              -> wire order descendant/parent_head/parent_tail; both
                 conventions parse, attribution diverges
  arm_prefix  buffered parent; descendant bytes (no newline) precede the
              parent's withheld ARM line -> line prefixed, regex fails
  arm_midline flushed parent; ARM line split across the spawn -> descendant
              bytes inside the line body; key value corrupted

Writes corpus/live/r72-scribe/parse-hazard.json.
"""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANE = HERE.parent.parent  # corpus/live/r72-scribe -> lane root
BATTERY = LANE / "fixtures" / "pygame_battery.py"
PARENT = HERE / "reorder_parent.py"
ARM_LINE = re.compile(r"^PYGAME-ARM (\S+) \| (.*)$")


def load_parse_arms():
    sys.dont_write_bytecode = True  # never write into tracked fixtures/__pycache__
    spec = importlib.util.spec_from_file_location("pygame_battery_tracked", BATTERY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_arms


def first_wins(stdout):
    arms = {}
    for line in stdout.splitlines():
        m = ARM_LINE.match(line.strip())
        if not m:
            continue
        arm, body = m.groups()
        kv = dict(p.split("=", 1) for p in body.split() if "=" in p)
        bucket = arms.setdefault(arm, {})
        for k, v in kv.items():
            bucket.setdefault(k, v)
    return arms


def main():
    parse_arms = load_parse_arms()
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    out = {"harness": "r72-scribe parse_hazard.py",
           "battery_parser": str(BATTERY),
           "parent_sha256": hashlib.sha256(PARENT.read_bytes()).hexdigest(),
           "started_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
           "cells": {}}
    for mode in ("arm_lines", "arm_prefix", "arm_midline"):
        proc = subprocess.run([sys.executable, str(PARENT), mode],
                              capture_output=True, text=True, env=env, timeout=30)
        raw = proc.stdout
        lines = [l for l in raw.splitlines() if l.strip()]
        out["cells"][mode] = {
            "raw_repr": repr(raw),
            "raw_bytes": len(raw.encode()),
            "wire_lines": lines,
            "arm_regex_parseable_lines": [l for l in lines
                                          if ARM_LINE.match(l.strip())],
            "last_wins_map": parse_arms(raw),
            "first_wins_map": first_wins(raw),
            "exit": proc.returncode,
        }
    path = HERE / "parse-hazard.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["cells"], indent=2))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
