#!/usr/bin/env python3
"""r101-crit1 attack generator: PCK receipt attacks (A1-A5) against measured Godot 4.7.2 bytes.

Inputs : /tmp/r101-CRIT-1/attack/out.keep.pck (real measured export, sha256 in shard).
Outputs: /tmp/r101-CRIT-1/attack/atk-*.pck + printed census table.

Every variant is byte-patched against the real artifact, never fabricated from
scratch, so each attack is exactly what a forger could produce with `dd`/struct.
"""
import hashlib
import struct
import sys

import os

SRC = os.environ.get("CRIT1_BASE", "/var/tmp/r101-CRIT-1") + "/attack/out.keep.pck"
OUT = os.environ.get("CRIT1_BASE", "/var/tmp/r101-CRIT-1") + "/attack"
MAGIC = b"GDPC"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def parse(d):
    """Return (header dict, entries list, tail) for a PCK v4 blob; raise on any
    structural break. Mirrors the measured layout: magic@0, version@4, 4.7.2@8,
    flags@20, file_base u64@24, table_ofs u64@32, table: u32 count then entries
    (u32 path_len, path, pad to 4, u64 ofs, u64 size, md5[16], u32 flags)."""
    if len(d) < 40 or d[:4] != MAGIC:
        raise ValueError("bad magic/too short")
    ver, maj, mi, pa, flags = struct.unpack_from("<5I", d, 4)
    file_base, table_ofs = struct.unpack_from("<2Q", d, 24)
    if not (40 <= table_ofs <= len(d) - 4):
        raise ValueError(f"table_ofs {table_ofs} outside file ({len(d)})")
    cnt = struct.unpack_from("<I", d, table_ofs)[0]
    if cnt > 4096:
        raise ValueError(f"implausible count {cnt}")
    entries, p = [], table_ofs + 4
    for _ in range(cnt):
        if p + 4 > len(d):
            raise ValueError("entry header past EOF")
        ln = struct.unpack_from("<I", d, p)[0]
        p += 4
        if p + ln > len(d):
            raise ValueError("path past EOF")
        path = d[p:p + ln].rstrip(b"\0").decode("utf-8", "replace")
        p += ln + ((-ln) % 4)
        ofs, size = struct.unpack_from("<2Q", d, p)
        md5 = d[p + 16:p + 32]
        ef = struct.unpack_from("<I", d, p + 32)[0]
        p += 36
        entries.append({"path": path, "ofs": ofs, "size": size, "md5": md5, "flags": ef})
    tail = len(d) - p
    hdr = {"ver": ver, "maj": maj, "min": mi, "patch": pa, "flags": flags,
           "file_base": file_base, "table_ofs": table_ofs, "count": cnt}
    return hdr, entries, tail, p


def verify(d):
    """Full structural + md5 walk. Returns (ok, lines, first_fail)."""
    lines, first_fail = [], None
    try:
        hdr, entries, tail, end = parse(d)
    except ValueError as exc:
        return False, [f"parse_error={exc}"], str(exc)
    lines.append(f"magic={d[:4].decode()} ver={hdr['ver']} {hdr['maj']}.{hdr['min']}.{hdr['patch']} "
                 f"flags={hdr['flags']} file_base={hdr['file_base']} table_ofs={hdr['table_ofs']} count={hdr['count']}")
    if hdr["count"] != len(entries):
        first_fail = first_fail or "count mismatch"
    bad = 0
    for e in entries:
        a, b = hdr["file_base"] + e["ofs"], hdr["file_base"] + e["ofs"] + e["size"]
        if a < hdr["file_base"] or b > hdr["table_ofs"] or a > b:
            bad += 1
            first_fail = first_fail or f"range out of bounds {e['path']}"
            continue
        if hashlib.md5(d[a:b]).digest() != e["md5"]:
            bad += 1
            first_fail = first_fail or f"md5 mismatch {e['path']}"
    lines.append(f"entries={len(entries)} md5_bad={bad} walk_end={end} eof={len(d)} tail={tail}")
    ok = bad == 0 and tail == 0 and hdr["count"] == len(entries)
    if tail != 0:
        first_fail = first_fail or f"walk tail={tail}"
    return ok, lines, ("None" if ok else first_fail)


def fragile_checks(d):
    """The three shapes a lazy row can carry: magic-only, size>0, name-substring."""
    return {"magic_only": len(d) >= 4 and d[:4] == MAGIC,
            "size_gt_0": len(d) > 0,
            "has_any_name_substring": b"project.binary" in d}


def main():
    base = open(SRC, "rb").read()
    hdr, entries, tail, end = parse(base)
    print(f"# real artifact sha256={sha(SRC)} size={len(base)} entries={hdr['count']} tail={tail}")
    print("# verify(real):", verify(base))

    variants = {}

    # A1: garbage file, magic patched (classic dd magic-patch forgery)
    a1 = bytearray(4096)
    a1[0:4] = MAGIC
    variants["atk-a1-garbage-magic"] = bytes(a1)

    # A1b: 1 MiB of zeros with magic — "plausible" size, zero structure
    a1b = bytearray(1 << 20)
    a1b[0:4] = MAGIC
    variants["atk-a1b-1mib-zeros-magic"] = bytes(a1b)

    # A2: size>0 vacuity — 4-byte magic-only file
    variants["atk-a2-4byte-magic"] = MAGIC
    # A2b: zero-byte file (fails even the magic check, passes nothing but is the
    # lower bound a `size >= 0` row would accept)
    variants["atk-a2b-empty"] = b""

    # A3: payload byte flip inside sub/note.txt payload (census-visible content)
    tgt = next(e for e in entries if e["path"] == "sub/note.txt")
    off = hdr["file_base"] + tgt["ofs"] + 10
    a3 = bytearray(base)
    a3[off] ^= 0x01
    variants["atk-a3-payload-flip"] = bytes(a3)

    # A3b: payload flip in main.gdc (executed code bytes)
    tgtm = next(e for e in entries if e["path"] == "main.gdc")
    offm = hdr["file_base"] + tgtm["ofs"] + 40
    a3b = bytearray(base)
    a3b[offm] ^= 0xFF
    variants["atk-a3b-exec-flip"] = bytes(a3b)

    # A4: header patches
    a4 = bytearray(base)
    struct.pack_into("<I", a4, 4, 99)          # pack version -> 99
    variants["atk-a4-version99"] = bytes(a4)
    a4b = bytearray(base)
    struct.pack_into("<3I", a4b, 8, 9, 9, 9)   # engine version -> 9.9.9
    variants["atk-a4b-engine999"] = bytes(a4b)
    a4c = bytearray(base)
    struct.pack_into("<Q", a4c, 24, 4096)      # file_base -> 4096 (wrong data window)
    variants["atk-a4c-filebase"] = bytes(a4c)
    a4d = bytearray(base)
    struct.pack_into("<I", a4d, hdr["table_ofs"], hdr["count"] + 500)  # count -> 517
    variants["atk-a4d-count"] = bytes(a4d)
    a4e = bytearray(base)
    struct.pack_into("<I", a4e, hdr["table_ofs"], 1)  # count -> 1 (census truncation)
    variants["atk-a4e-count1"] = bytes(a4e)

    # A5: entry name forge — keep md5/payload of the note.txt slot but rename it
    # to "main.gdc" in the table, so a name census that only checks presence of
    # names (and never hashes the payload) is fooled.
    a5 = bytearray(base)
    p = hdr["table_ofs"] + 4
    name_off = None
    for e in entries:
        q = p + 4
        if a5[q:q + len(e["path"])].rstrip(b"\0").decode() == "sub/note.txt":
            name_off = q
            break
        p = q + len(e["path"]) + ((-len(e["path"])) % 4) + 36
    assert name_off is not None
    a5[name_off:name_off + 12] = b"main.gdc\0\0\0\0"
    variants["atk-a5-name-forge"] = bytes(a5)

    for name, data in variants.items():
        path = f"{OUT}/{name}.pck"
        open(path, "wb").write(data)
        ok, lines, first = verify(data)
        fr = fragile_checks(data)
        print(f"{name}: size={len(data)} sha256={hashlib.sha256(data).hexdigest()}")
        print(f"   fragile={fr} strong_ok={ok} first_fail={first}")

    print("variants written:", " ".join(sorted(variants)))


if __name__ == "__main__":
    sys.exit(main())
