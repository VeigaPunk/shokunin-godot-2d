#!/usr/bin/env python3
"""r103-E3 recon helper: parse a Godot 4.7 .pck OR an embedded-pck binary and
census entries; also byte-search for marker strings. Read-only on the artifacts.

usage: r103-E3_packparse.py FILE [--tags "str1,str2"]
"""
import hashlib
import json
import struct
import sys


def locate_pack(data: bytes):
    """Return (pck_start, pck_end, kind). Standalone: magic at 0, end = len.
    Embedded: trailer = <pck_size u64><0x435044 47 magic 'GDPC'>? measured below."""
    if data[:4] == b"GDPC":
        return 0, len(data), "standalone"
    if data[-4:] == b"GDPC":
        for trailer in (12, 16):  # u32 size? u64 size? variant
            if trailer == 12:
                size = struct.unpack_from("<Q", data, len(data) - 12)[0]
            else:
                size = struct.unpack_from("<Q", data, len(data) - 16)[0]
            start = len(data) - size
            if 0 <= start < len(data) and data[start:start + 4] == b"GDPC":
                return start, len(data) - trailer, f"embedded(trailer={trailer})"
        return -1, -1, "embedded_magic_at_eof_but_no_valid_trailer"
    return -1, -1, "no_magic"


def parse_pack(data: bytes, start: int, end: int):
    pack = data[start:end]
    info = {"pack_bytes": len(pack)}
    if len(pack) < 0x28:
        info["read_ok"] = False
        return info
    info["magic"] = pack[:4].decode("ascii", "replace")
    info["pack_format_version"] = struct.unpack_from("<I", pack, 4)[0]
    info["engine_major"] = struct.unpack_from("<I", pack, 8)[0]
    info["engine_minor"] = struct.unpack_from("<I", pack, 12)[0]
    info["engine_patch"] = struct.unpack_from("<I", pack, 16)[0]
    dir_off = struct.unpack_from("<Q", pack, 0x20)[0]
    info["dir_off"] = dir_off
    count = struct.unpack_from("<I", pack, dir_off)[0]
    info["entries"] = count
    pos = dir_off + 4
    names = []
    sizes = {}
    for _ in range(count):
        name_len = struct.unpack_from("<I", pack, pos)[0]
        pos += 4
        raw = pack[pos:pos + name_len]
        pos += name_len
        nul = raw.find(0)
        name = raw[:nul if nul >= 0 else len(raw)].decode("utf-8", "replace")
        offset, size = struct.unpack_from("<QQ", pack, pos)
        pos += 8 + 8 + 16 + 4
        names.append(name)
        sizes[name] = size
        if name == "project.binary":
            info["pbin_offset"] = offset
            info["pbin_size"] = size
            info["pbin_ecfg"] = pack[offset:offset + 4].decode("ascii", "replace") == "ECFG"
    info["names"] = names
    info["sizes"] = sizes
    info["read_ok"] = True
    return info


def main():
    path = sys.argv[1]
    tags = []
    if len(sys.argv) > 3 and sys.argv[2] == "--tags":
        tags = sys.argv[3].split(",")
    data = open(path, "rb").read()
    start, end, kind = locate_pack(data)
    out = {"file": path, "file_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "location": kind}
    if start >= 0:
        out.update(parse_pack(data, start, end))
    for t in tags:
        out[f"contains:{t}"] = data.count(t.encode()) > 0
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
