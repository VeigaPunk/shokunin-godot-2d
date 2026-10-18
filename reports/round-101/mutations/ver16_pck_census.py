#!/usr/bin/env python3
"""VER-16 PCK census: parse Godot 4 .pck (GDPC v2) files.

Layout (observed on 4.7.2.stable, linux release pack export):
  0x00 magic "GDPC"
  0x04 u32 version=4
  0x08 u32 ver_major, 0x0C u32 ver_minor, 0x10 u32 ver_patch
  0x14 u32 flags
  0x18 u64 data_offset   (start of file-data region; 112 observed)
  0x20 u64 dir_offset    (start of directory table, EOF side)
  0x28..data_offset reserved zeros
  data region: concatenated file bytes
  dir region: u32 count; per entry: u32 path_len (path padded to 4-byte
              multiple, length includes padding), path bytes, u64 offset
              (relative to data_offset), u64 size, 16-byte md5, u32 flags
  stored paths carry no "res://" prefix

Usage: python3 ver16_pck_census.py file.pck [file2.pck ...]
"""
import hashlib
import struct
import sys


def parse(path, quiet=False):
    with open(path, "rb") as f:
        blob = f.read()
    magic = blob[0:4]
    version = struct.unpack_from("<I", blob, 4)[0]
    v_major, v_minor, v_patch = struct.unpack_from("<III", blob, 8)
    flags = struct.unpack_from("<I", blob, 20)[0]
    data_off, dir_off = struct.unpack_from("<qq", blob, 24)
    reserved = blob[40:data_off]
    count = struct.unpack_from("<I", blob, dir_off)[0]
    if not quiet:
        print(f"# {path}: magic={magic!r} version={version} {v_major}.{v_minor}.{v_patch} flags={flags} "
              f"data_off={data_off} dir_off={dir_off} reserved_len={len(reserved)} reserved_all_zero={reserved == bytes(len(reserved))} "
              f"count={count} total={len(blob)} dir_size={len(blob) - dir_off}")
    off = dir_off + 4
    entries = []
    for i in range(count):
        ln = struct.unpack_from("<I", blob, off)[0]
        off += 4
        p = blob[off:off + ln].split(b"\x00")[0].decode("utf-8", "replace")
        off += ln
        foff, fsize = struct.unpack_from("<qq", blob, off)
        off += 16
        md5 = blob[off:off + 16]
        off += 16
        eflags = struct.unpack_from("<I", blob, off)[0]
        off += 4
        data = blob[data_off + foff:data_off + foff + fsize]
        dsha = hashlib.sha256(data).hexdigest()
        entries.append(dict(idx=i, path=p, off=foff, size=fsize, md5=md5.hex(), sha256=dsha, flags=eflags))
        if not quiet:
            print(f"{i:2d} {p:<52s} off={foff:<7d} size={fsize:<6d} ef={eflags} md5={md5.hex()} sha256={dsha}")
    if not quiet:
        print(f"# dir_consumed={off} trailing={len(blob) - off} tail_hex={blob[off:off + 24].hex()}")
    return entries


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--diff" in sys.argv:
        a = parse(args[0], quiet=True)
        b = parse(args[1], quiet=True)
        da = {e["path"]: e for e in a}
        db = {e["path"]: e for e in b}
        print("path | size_a | size_b | sha_equal")
        for p in sorted(set(da) | set(db)):
            ea, eb = da.get(p), db.get(p)
            sa, sb = (ea["size"] if ea else None), (eb["size"] if eb else None)
            eq = "=" if (ea and eb and ea["sha256"] == eb["sha256"]) else "DIFF"
            print(f"{p} | {sa} | {sb} | {eq}")
        return
    for path in args:
        parse(path)


if __name__ == "__main__":
    main()
