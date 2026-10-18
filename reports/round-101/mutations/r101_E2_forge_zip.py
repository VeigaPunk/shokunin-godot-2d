#!/usr/bin/env python3
"""r101-E2 zip forgery tool (seat E2, scenario 02).

Builds byte-level forgeries of a Godot `--export-pack` zip so the census row in
corpus/fixtures/export_prod_s02.gd can be probed for discrimination. Written
independently of the fixture: for the "content" and "name" kinds it re-writes
the whole archive with Godot's observed header fields (create_version 0,
extract_version 20, flags 0, dos 0/0, no extra field, external_attr 0, method 8,
raw deflate) so that ONLY content/name changes -- no incidental header drift.

usage:
  python3 r101_E2_forge_zip.py <src.zip> <out.zip> <kind>
kinds:
  crc_bit            flip one bit of the last central-directory entry's CRC
  name_cd            flip one byte of the last CD entry's name (local kept)
  name_local         flip one byte of the first local header's name (CD kept)
  count_bump         claim one extra entry in the EOCD counts
  truncate_cd        truncate the central directory, dropping the EOCD
  content:<i>:<off>  rebuild with entry i's inflated payload byte <off> flipped,
                     same inflated length, CRCs and sizes recomputed
  name:<i>           rebuild with CD+local entry i renamed (same content)
exit 0 on success; 2 on a bad kind/argument; 3 on a malformed source zip.
"""
import hashlib
import struct
import sys
import zlib

CD_SIG = b"PK\x01\x02"
LH_SIG = b"PK\x03\x04"
EOCD_SIG = b"PK\x05\x06"


def find_last(buf, sig):
    return buf.rfind(sig)


def parse(buf):
    """Minimal central-directory parse -> list of entry dicts."""
    eocd = find_last(buf, EOCD_SIG)
    if eocd < 0:
        raise ValueError("no EOCD")
    _, _, _, cd_entries, cd_total, cd_size, cd_offset, comment_len = struct.unpack(
        "<4sHHHHIIH", buf[eocd:eocd + 22])
    if comment_len != 0 or cd_entries != cd_total:
        raise ValueError("unexpected EOCD shape")
    if cd_offset + cd_size != eocd:
        raise ValueError("central directory not contiguous")
    entries = []
    cur = cd_offset
    for _ in range(cd_entries):
        if buf[cur:cur + 4] != CD_SIG:
            raise ValueError("bad CD signature at %d" % cur)
        (make_ver, extract_ver, flags, method, dos_time, dos_date, crc, csize,
         usize, nlen, elen, clen, _disk, _int_attr, _ext_attr,
         local_offset) = struct.unpack("<HHHHHHIIIHHHHHII", buf[cur + 4:cur + 46])
        name = buf[cur + 46:cur + 46 + nlen]
        entries.append({
            "cd": cur, "name": name, "crc": crc, "csize": csize, "usize": usize,
            "method": method, "flags": flags, "make_ver": make_ver,
            "extract_ver": extract_ver, "dos_time": dos_time, "dos_date": dos_date,
            "elen": elen, "clen": clen, "local": local_offset,
        })
        cur += 46 + nlen + elen + clen
    return entries


def inflate(buf, entry):
    lh = entry["local"]
    if buf[lh:lh + 4] != LH_SIG:
        raise ValueError("bad local header at %d" % lh)
    nlen, elen = struct.unpack("<HH", buf[lh + 26:lh + 30])
    start = lh + 30 + nlen + elen
    payload = buf[start:start + entry["csize"]]
    data = zlib.decompress(payload, -15)
    if len(data) != entry["usize"]:
        raise ValueError("inflated length %d != %d" % (len(data), entry["usize"]))
    return data


def deflate(data):
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    return compressor.compress(data) + compressor.flush()


def rebuild(entries, payloads, names):
    """Write a zip with Godot's header field profile; returns bytes."""
    out = bytearray()
    locals_ = []
    for entry, data, name in zip(entries, payloads, names):
        payload = deflate(data)
        local = bytearray()
        local += LH_SIG
        local += struct.pack("<HHHHHIIIHH", 20, 0, entry["method"], 0, 0,
                             zlib.crc32(data) & 0xFFFFFFFF, len(payload), len(data),
                             len(name), 0)
        local += name
        local += payload
        locals_.append({"offset": len(out), "name": name, "payload": payload,
                        "crc": zlib.crc32(data) & 0xFFFFFFFF, "usize": len(data)})
        out += local
    cd_offset = len(out)
    for record in locals_:
        out += CD_SIG
        out += struct.pack("<HHHHHHIIIHHHHHII", 0, 20, 0, 8, 0, 0, record["crc"],
                           len(record["payload"]), record["usize"], len(record["name"]),
                           0, 0, 0, 0, 0, record["offset"])
        out += record["name"]
    cd_size = len(out) - cd_offset
    out += EOCD_SIG
    out += struct.pack("<HHHHIIH", 0, 0, len(locals_), len(locals_), cd_size, cd_offset, 0)
    return bytes(out)


def main():
    if len(sys.argv) != 4:
        print("usage: r101_E2_forge_zip.py <src.zip> <out.zip> <kind>")
        return 2
    src_path, out_path, kind = sys.argv[1:4]
    src = open(src_path, "rb").read()
    try:
        entries = parse(src)
    except ValueError as exc:
        print("MALFORMED source zip: %s" % exc)
        return 3
    detail = ""
    if kind == "crc_bit":
        forged = bytearray(src)
        cd = find_last(forged, CD_SIG)
        forged[cd + 16] ^= 0x01
        detail = "flipped CD crc bit of entry %d" % (len(entries) - 1)
        result = bytes(forged)
    elif kind == "name_cd":
        forged = bytearray(src)
        cd = find_last(forged, CD_SIG)
        forged[cd + 46] ^= 0x20
        detail = "flipped CD name byte of entry %d" % (len(entries) - 1)
        result = bytes(forged)
    elif kind == "name_local":
        forged = bytearray(src)
        forged[30] ^= 0x20
        detail = "flipped local name byte of entry 0"
        result = bytes(forged)
    elif kind == "count_bump":
        forged = bytearray(src)
        eocd = find_last(forged, EOCD_SIG)
        count = struct.unpack("<H", forged[eocd + 10:eocd + 12])[0]
        struct.pack_into("<HH", forged, eocd + 8, count + 1, count + 1)
        detail = "EOCD counts raised %d -> %d" % (count, count + 1)
        result = bytes(forged)
    elif kind == "truncate_cd":
        eocd = find_last(src, EOCD_SIG)
        cd_offset = struct.unpack("<I", src[eocd + 16:eocd + 20])[0]
        result = src[:cd_offset + (eocd - cd_offset) // 2]
        detail = "truncated CD to half its size, EOCD dropped (%d bytes)" % len(result)
    elif kind.startswith("content:"):
        _, raw_index, raw_offset = kind.split(":")
        index, offset = int(raw_index), int(raw_offset)
        payloads = [inflate(src, entry) for entry in entries]
        target = bytearray(payloads[index])
        target[offset] ^= 0x01
        payloads[index] = bytes(target)
        detail = "entry %d byte %d flipped, inflated length preserved (%d)" % (
            index, offset, len(payloads[index]))
        result = rebuild(entries, payloads, [entry["name"] for entry in entries])
    elif kind.startswith("name:"):
        index = int(kind.split(":")[1])
        payloads = [inflate(src, entry) for entry in entries]
        names = [entry["name"] for entry in entries]
        names[index] = names[index] + b".forged"
        detail = "entry %d renamed to %s" % (index, names[index].decode())
        result = rebuild(entries, payloads, names)
    else:
        print("unknown kind %r" % kind)
        return 2
    with open(out_path, "wb") as handle:
        handle.write(result)
    print("MUTATION kind=%s detail=%s src_bytes=%d out_bytes=%d src_sha256=%s out_sha256=%s" % (
        kind, detail, len(src), len(result),
        hashlib.sha256(src).hexdigest(), hashlib.sha256(result).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
