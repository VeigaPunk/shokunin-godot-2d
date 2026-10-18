#!/usr/bin/env python3
"""Independent from-scratch ZIP central-directory parser (VER-1 round 101).

Reads a zip archive without using the zipfile module, locates the EOCD,
walks the central directory, cross-checks every entry against its local
file header, decompresses stored payloads (method 0/8) and verifies CRC32
and uncompressed size. Prints a census for expected-value cross-checks of
export_prod row s02. Read-only.

Usage: python3 r101-ver1_zip_parse.py <file.zip>
"""
import hashlib
import struct
import sys
import zlib

EOCD_SIG = b"PK\x05\x06"
CD_SIG = b"PK\x01\x02"
LFH_SIG = b"PK\x03\x04"


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def find_eocd(data):
    last = len(data) - 22
    floor = max(0, last - 65535)
    for pos in range(last, floor - 1, -1):
        if data[pos:pos + 4] == EOCD_SIG:
            return pos
    return -1


def main(path):
    data = open(path, "rb").read()
    size = len(data)
    e = find_eocd(data)
    if e < 0:
        print("NO_EOCD")
        return 1
    disk_no, cd_disk = u16(data, e + 4), u16(data, e + 6)
    entries_disk, entries_total = u16(data, e + 8), u16(data, e + 10)
    cd_size, cd_off = u32(data, e + 12), u32(data, e + 16)
    comment_len = u16(data, e + 20)
    print(f"zip_size={size} eocd_offset={e} eocd_trailing_comment_len={comment_len} "
          f"eocd_to_eof_bytes={size - (e + 22 + comment_len)}")
    print(f"disk_no={disk_no} cd_disk={cd_disk} entries_disk={entries_disk} "
          f"entries_total={entries_total} cd_size={cd_size} cd_offset={cd_off}")
    print(f"eocd_consistency={cd_off + cd_size + 22 + comment_len == size} "
          f"cd_end={cd_off + cd_size}")
    if cd_off + cd_size > size:
        print("BAD_CD_RANGE")
        return 1
    off = cd_off
    entries = []
    for i in range(entries_total):
        if data[off:off + 4] != CD_SIG:
            print(f"BAD_CD_SIG index={i} off={off} bytes={data[off:off + 4]!r}")
            return 1
        made_by = u16(data, off + 4)
        need = u16(data, off + 6)
        flags = u16(data, off + 8)
        method = u16(data, off + 10)
        mtime = u16(data, off + 12)
        mdate = u16(data, off + 14)
        crc = u32(data, off + 16)
        csize = u32(data, off + 20)
        usize = u32(data, off + 24)
        nlen = u16(data, off + 28)
        elen = u16(data, off + 30)
        clen = u16(data, off + 32)
        disk_start = u16(data, off + 34)
        iattr = u16(data, off + 36)
        eattr = u32(data, off + 38)
        local_off = u32(data, off + 42)
        name = data[off + 46:off + 46 + nlen].decode("utf-8", "replace")
        entries.append((name, made_by, need, flags, method, mtime, mdate,
                        crc, csize, usize, local_off, elen, clen, disk_start,
                        iattr, eattr))
        off += 46 + nlen + elen + clen
    print(f"cd_walk_end={off} cd_declared_end={cd_off + cd_size} "
          f"cd_walk_consistent={off == cd_off + cd_size}")
    lfh_ok = 0
    crc_ok = 0
    crc_all = True
    for (name, made_by, need, flags, method, mtime, mdate, crc, csize, usize,
         local_off, elen, clen, disk_start, iattr, eattr) in entries:
        sig = data[local_off:local_off + 4]
        lnlen = u16(data, local_off + 26)
        lelen = u16(data, local_off + 28)
        lname = data[local_off + 30:local_off + 30 + lnlen].decode("utf-8", "replace")
        payload = data[local_off + 30 + lnlen + lelen:local_off + 30 + lnlen + lelen + csize]
        if sig == LFH_SIG and lname == name:
            lfh_ok += 1
        try:
            if method == 0:
                blob = payload
            elif method == 8:
                blob = zlib.decompress(payload, -15)
            else:
                blob = b""
            calc = zlib.crc32(blob) & 0xFFFFFFFF
            ok = (calc == crc) and (len(blob) == usize)
        except zlib.error:
            ok = False
        if ok:
            crc_ok += 1
        else:
            crc_all = False
        print(f"  entry name={name!r} made_by=0x{made_by:04x} need={need} "
              f"method={method} flags=0x{flags:04x} dos_time=0x{mtime:04x} "
              f"dos_date=0x{mdate:04x} crc=0x{crc:08x} csize={csize} "
              f"usize={usize} local_off={local_off} ext_attr=0x{eattr:08x} "
              f"lfh_name_match={sig == LFH_SIG and lname == name} crc_match={ok}")
    print(f"entries={len(entries)} local_headers_ok={lfh_ok} crc_ok={crc_ok} "
          f"crc_all={crc_all} zip64_sentinel="
          f"{any(x[8] == 0xFFFFFFFF or x[9] == 0xFFFFFFFF for x in entries)}")
    print(f"zip_sha256={hashlib.sha256(data).hexdigest()}")
    print(f"first_4_bytes={data[0:4]!r}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
