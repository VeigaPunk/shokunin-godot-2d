#!/usr/bin/env python3
"""V3 adjunct (r102): dump project.binary strings + marker contexts from exported G packs.

Reads existing packs under <root>/g/out (produced by ver3_export_probe.py);
does not export anything. Usage: python3 ver3_pbin_dump.py /var/tmp/r102-ver3
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver3_export_probe import entry_bytes, parse_pck, scan_markers  # noqa: E402

EXTRA = ["zzfeat", "zzother", " zzother", "ZZFEAT", "zzthird", "V3Feat",
         "V3Base", "9.9.9", "DESC_OTHER", "application/config/features",
         "application/config/name"]


def strings(b, minlen=4):
    out = []
    cur = b""
    for byte in b:
        if 32 <= byte < 127:
            cur += bytes([byte])
        else:
            if len(cur) >= minlen:
                out.append(cur.decode())
            cur = b""
    if len(cur) >= minlen:
        out.append(cur.decode())
    return out


def main(root):
    for pck in sorted(glob.glob(os.path.join(root, "g", "out", "*.pck"))):
        parsed, raw = parse_pck(pck)
        pb = entry_bytes(raw, parsed, "project.binary")
        name = os.path.basename(pck)
        if pb is None:
            print(f"== {name}: NO project.binary")
            continue
        print(f"== {name} pbin={len(pb)} magic={pb[:4].decode('latin1')!r}")
        for s in strings(pb):
            print(f"   str {s!r}")
        for k, v in scan_markers(pb, EXTRA).items():
            if v["count"]:
                print(f"   mark {k!r} count={v['count']}")
                for c in v["ctx"]:
                    print(f"      off={c['off']} {c['ctx']}")
    print("done")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/var/tmp/r102-ver3")
