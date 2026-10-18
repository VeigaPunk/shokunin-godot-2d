#!/usr/bin/env python3
"""VER-3 (r101) PCK census tool — byte-exact reader for Godot 4.7.x export packs.

Measured layout (Godot 4.7.2.stable, empirical + md5-verified over 8 packs):
  u32 magic "GDPC"
  u32 pack_format_version (observed 4)
  u32 ver_major, u32 ver_minor, u32 ver_rev   (4, 7, 2)
  u32 pack_flags                              (observed 2; semantics unverified)
  u64 file_base                               (112 in all observed packs)
  u64 dir_offset                              (directory table at EOF)
  [reserved zero bytes up to file_base]
  [file data, offsets relative to file_base]
  directory at dir_offset:
    u32 file_count
    per entry: u32 path_len (padded; path bytes are NUL-padded to the stored length)
               u64 offset (relative to file_base), u64 size,
               16-byte md5 of the STORED bytes at file_base+offset, u32 flags
  (directory end == file size in all observed packs)

Usage: ver3_pck_census.py <pack.pck> [more.pck ...]
Exit 0 when every parsed entry md5-verifies and dir_end == filesize; 1 otherwise.
"""
import struct
import sys
import hashlib


def census(path):
    b = open(path, 'rb').read()
    magic = b[0:4]
    ver, major, minor, rev, flags = struct.unpack_from('<IIIII', b, 4)
    file_base, dir_off = struct.unpack_from('<QQ', b, 24)
    count, = struct.unpack_from('<I', b, dir_off)
    print(f'pck={path} size={len(b)} magic={magic.decode(errors="replace")} '
          f'pack_version={ver} godot={major}.{minor}.{rev} pack_flags={flags} '
          f'file_base={file_base} dir_off={dir_off} count={count}')
    off = dir_off + 4
    entries = []
    for i in range(count):
        plen, = struct.unpack_from('<I', b, off)
        off += 4
        raw = b[off:off + plen]
        off += plen
        eofs, esize = struct.unpack_from('<QQ', b, off)
        off += 16
        md5 = b[off:off + 16]
        off += 16
        eflags, = struct.unpack_from('<I', b, off)
        off += 4
        absofs = file_base + eofs
        ok = hashlib.md5(b[absofs:absofs + esize]).hexdigest() == md5.hex()
        entries.append((raw.rstrip(b'\x00').decode(), eofs, esize, eflags, ok))
        nul_padded = len(raw) != len(raw.rstrip(b'\x00'))
        print(f'{i:2d} path={raw.rstrip(b"\x00").decode()!r} rel_off={eofs} abs_off={absofs} '
              f'size={esize} flags={eflags} md5ok={ok} nul_padded={nul_padded}')
    paths = [e[0] for e in entries]
    good = all(e[4] for e in entries) and off == len(b)
    print(f'n_entries={len(entries)} all_md5_ok={all(e[4] for e in entries)} '
          f'dir_end==size={off == len(b)} sorted_by_path={paths == sorted(paths)} '
          f'sorted_by_offset={[e[1] for e in entries] == sorted(e[1] for e in entries)}')
    return good


if __name__ == '__main__':
    ok = True
    for p in sys.argv[1:]:
        ok = census(p) and ok
    sys.exit(0 if ok else 1)
