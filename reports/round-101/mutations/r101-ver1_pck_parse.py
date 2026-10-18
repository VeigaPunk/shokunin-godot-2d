#!/usr/bin/env python3
"""Independent from-scratch PCK parser (VER-1 round 101).

Reads a Godot pack file without using any Godot code and prints a census:
header fields, directory entries, per-entry offset/size/md5, and verifies
stored md5 against the actual data slice. Intended for expected-value
cross-checks of export_prod rows s01/s03. Read-only.

Usage: python3 r101-ver1_pck_parse.py <file.pck>
"""
import hashlib
import struct
import sys


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def u64(b, o):
    return struct.unpack_from("<Q", b, o)[0]


def main(path):
    data = open(path, "rb").read()
    size = len(data)
    if size < 104:
        print(f"PCK_TOO_SHORT size={size}")
        return 1
    magic = data[0:4]
    version = u32(data, 4)
    major = u32(data, 8)
    minor = u32(data, 12)
    patch = u32(data, 16)
    flags = u32(data, 20)
    file_base = u64(data, 24)
    dir_offset = u64(data, 32)
    flag_names = []
    if flags & 1:
        flag_names.append("DIR_ENCRYPTED")
    if flags & 2:
        flag_names.append("REL_FILEBASE")
    if flags & 4:
        flag_names.append("SPARSE_BUNDLE")
    print(f"magic={magic!r} ascii={magic.decode('latin1')} version={version} "
          f"engine={major}.{minor}.{patch} flags=0x{flags:02x} "
          f"flag_names={','.join(flag_names) or '-'}")
    print(f"file_base={file_base} dir_offset={dir_offset} file_size={size} "
          f"header_bytes=104")
    if dir_offset >= size:
        print(f"BAD_DIR_OFFSET dir_offset={dir_offset} size={size}")
        return 1
    count = u32(data, dir_offset)
    off = dir_offset + 4
    entries = []
    for i in range(count):
        sl = u32(data, off)
        off += 4
        raw_path = data[off:off + sl]
        off += sl
        path_str = raw_path.rstrip(b"\x00").decode("utf-8", "replace")
        ofs = u64(data, off)
        fsize = u64(data, off + 8)
        md5 = data[off + 16:off + 32]
        eflags = u32(data, off + 32)
        off += 36
        abs_off = file_base + ofs
        blob = data[abs_off:abs_off + fsize]
        calc = hashlib.md5(blob).digest()
        ok = calc == md5
        entries.append((path_str, sl, ofs, fsize, md5.hex(), eflags, ok))
    print(f"entry_count={count} dir_end={off} trailing_dir_bytes={size - off}")
    data_sum = 0
    for (p, sl, ofs, fsize, md5hex, eflags, ok) in entries:
        data_sum += fsize
        print(f"  entry path={p!r} path_field_len={sl} ofs={ofs} size={fsize} "
              f"md5={md5hex} flags=0x{eflags:02x} md5_match={ok} abs_ofs={file_base + ofs}")
    print(f"sum_entry_sizes={data_sum} dir_offset={dir_offset} "
          f"data_region_min={file_base}")
    if file_base > dir_offset:
        print("BAD_FILE_BASE file_base past directory offset")
        return 1
    # First data byte aligns to PCK_PADDING; report observed padding.
    print(f"header_to_file_base_pad={file_base - 104}")
    print(f"pck_sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
