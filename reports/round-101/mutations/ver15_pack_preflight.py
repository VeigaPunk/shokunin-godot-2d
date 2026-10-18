#!/usr/bin/env python3
"""ver15_pack_preflight — refuse PCK files whose `project.binary` entry is absent or zero-length.

r101 VER-15 context: intermittent `godot --headless --export-pack` invocations on this host
emit a PCK that *logs* "Storing File: res://project.binary" yet packs it with data_size=0.
Launching such a pack with `--main-pack ... --quit-after N` prints only the engine banner and
exits rc=0 (measured), so a launch receipt alone cannot be trusted without this preflight.

Usage:  ver15_pack_preflight.py <pack.pck> [more.pck ...]
Exit:   0 iff every pack is well-formed (magic GDPC, PROJECT.BINARY entry, size > 0,
        absolute data starts with ECFG); 1 otherwise. One line per pack on stdout.

Measured field layout (godot 4.7.2, pack format version 4):
  u32 magic 'GDPC' | u32 fmt_version | u32 major | u32 minor | u32 patch | u32 flags
  | u64 file_base (24) | u64 dir_offset (32) | reserved 16*u32 (40..103)
  dir at dir_offset: u32 file_count, then per entry:
  u32 name_len (padded length incl. NUL padding) | name bytes | u64 file_offset (rel. to
  file_base) | u64 size | md5[16] | u32 flags
  Entry name for the settings blob is literally `project.binary` (16-byte padded name).
"""
import struct
import sys

ECFG = b"ECFG"
NAME = b"project.binary"


def check(path):
    try:
        with open(path, "rb") as fh:
            d = fh.read()
    except OSError as exc:
        return False, f"unreadable: {exc}"
    if len(d) < 40 or d[:4] != b"GDPC":
        return False, "magic != GDPC"
    base, = struct.unpack_from("<Q", d, 24)
    dir_off, = struct.unpack_from("<Q", d, 32)
    if dir_off >= len(d):
        return False, f"dir_offset {dir_off} >= file size {len(d)} (truncated?)"
    idx = d.find(NAME, dir_off)
    if idx < 0:
        return False, "no project.binary entry in directory"
    name_len, = struct.unpack_from("<I", d, idx - 4)
    if name_len < len(NAME) or idx - 4 + 4 + name_len > dir_off + (len(d) - dir_off):
        return False, "project.binary entry name_len out of range"
    j = idx + name_len
    if j + 16 > len(d):
        return False, "project.binary entry fields truncated"
    off, size = struct.unpack_from("<QQ", d, j)
    if size == 0:
        return False, "project.binary entry present but data_size=0 (pack is silently unbootable)"
    abso = base + off
    if abso + 4 > len(d):
        return False, f"project.binary data offset {abso} beyond EOF {len(d)}"
    if d[abso:abso + 4] != ECFG:
        return False, f"project.binary data at {abso} starts {d[abso:abso + 4]!r}, not ECFG"
    return True, f"project.binary size={size} ECFG@{abso}"


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[0])
        return 2
    ok_all = True
    for path in argv[1:]:
        ok, why = check(path)
        ok_all &= ok
        print(f"{'PASS' if ok else 'FAIL'} {path}: {why}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
