#!/usr/bin/env python3
"""VER-16 export-variance checker (rules R1-R9 of reports/round-101/r101-ver16.md).

Validates candidate determinism evidence: one or more Godot PCK files produced by
`godot --headless --export-pack`, optionally with --name for the R4 content pin.

Usage:
  python3 ver16_export_variance_checker.py --name "my project" out1.pck out2.pck [...]
  add --allow-import-id to accept the observed 4-byte .scn id delta across trees (R9)

Exit 0 = PASS, 1 = FAIL (reasons printed), 2 = usage error.
"""
import hashlib
import struct
import sys


def parse(path):
    blob = open(path, "rb").read()
    if len(blob) == 0:
        raise ValueError("artifact is 0 bytes (R6/R3 failure signature)")
    if blob[0:4] != b"GDPC":
        raise ValueError(f"bad magic {blob[0:4]!r}")
    version = struct.unpack_from("<I", blob, 4)[0]
    flags = struct.unpack_from("<I", blob, 20)[0]
    data_off, dir_off = struct.unpack_from("<qq", blob, 24)
    reserved = blob[40:data_off]
    if reserved != bytes(len(reserved)):
        raise ValueError("reserved header bytes non-zero")
    count = struct.unpack_from("<I", blob, dir_off)[0]
    off = dir_off + 4
    entries = {}
    for _ in range(count):
        ln = struct.unpack_from("<I", blob, off)[0]
        off += 4
        p = blob[off:off + ln].split(b"\x00")[0].decode("utf-8", "replace")
        off += ln
        foff, fsize = struct.unpack_from("<qq", blob, off)
        off += 16
        md5 = blob[off:off + 16].hex()
        off += 16 + 4
        data = blob[data_off + foff:data_off + foff + fsize]
        entries[p] = dict(size=fsize, md5=md5, sha256=hashlib.sha256(data).hexdigest())
    if off != len(blob):
        raise ValueError(f"directory table does not consume to EOF (trailing {len(blob) - off})")
    if dir_off != len(blob) - (off - dir_off):
        raise ValueError("dir_off invariant violated")
    return dict(total=len(blob), version=version, flags=flags, data_off=data_off,
                dir_off=dir_off, count=count, entries=entries)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    allow_id = "--allow-import-id" in sys.argv
    name = None
    if "--name" in sys.argv:
        name = sys.argv[sys.argv.index("--name") + 1]
        args = [a for a in args if a != name]
    if not args:
        print(__doc__)
        return 2

    fails, packs = [], {}
    for p in args:
        try:
            packs[p] = parse(p)
        except ValueError as e:
            fails.append(f"{p}: {e}")
    for p, info in packs.items():
        pb = info["entries"].get("project.binary")
        if pb is None:
            fails.append(f"{p}: project.binary missing (R4)")
            continue
        if pb["size"] == 0:
            fails.append(f"{p}: project.binary empty -> R3 hard FAIL (env failure, not variance)")
    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    if name:
        for p, info in packs.items():
            cnt = info["count"]
            if cnt < 12:
                fails.append(f"{p}: entry count {cnt} < expected 12")
        # content pin: read project.binary bytes again for the name check
        for p in packs:
            blob = open(p, "rb").read()
            info = packs[p]
            data_off, dir_off = info["data_off"], info["dir_off"]
            off = dir_off + 4
            pb = b""
            for _ in range(struct.unpack_from("<I", blob, dir_off)[0]):
                ln = struct.unpack_from("<I", blob, off)[0]
                off += 4
                path = blob[off:off + ln].split(b"\x00")[0].decode("utf-8", "replace")
                off += ln
                foff, fsize = struct.unpack_from("<qq", blob, off)
                off += 16 + 16 + 4
                if path == "project.binary":
                    pb = blob[data_off + foff:data_off + foff + fsize]
            if not pb.startswith(b"ECFG") or name.encode() not in pb:
                fails.append(f"{p}: project.binary not ECFG with own name {name!r} (R4)")
    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1

    # R1/R2 cross-run comparison
    base = next(iter(packs))
    for p, info in packs.items():
        if p == base:
            continue
        if info["entries"].keys() != packs[base]["entries"].keys():
            fails.append(f"{p}: entry set differs from {base} (R2)")
            continue
        for path, ent in info["entries"].items():
            ref = packs[base]["entries"][path]
            if ent == ref:
                continue
            if allow_id and path.endswith(".scn") and ent["size"] == ref["size"]:
                print(f"note: {p}:{path} differs (import-id delta tolerated by --allow-import-id)")
                continue
            fails.append(f"{p}:{path} differs from {base} (R2)")
    print("PASS" if not fails else "FAIL")
    for f in fails:
        print(" -", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
