#!/usr/bin/env python3
"""r103-CRIT1 — independent PCK census tool (crit1 attack rig).

Parses Godot 4.7.2 PCK blobs from raw bytes only; never trusts a fixture's
printed census. Two jobs:
  pck.py DUMP <file>       -> header fields + entry table + trailing bytes
  pck.py ENTRIES <file>    -> one "path size md5" line per entry (sorted)
  pck.py DIFF <a> <b>      -> byte compare: sizes, shas, first-diff offsets,
                              entry-set diff, per-entry content diff count

Layout derived by the r101-crit1 attack rig on 4.7.2 artifacts and re-verified
here against freshly exported bytes (magic@0, ver@4, 3x u32 version@8, flags@20,
file_base@24, table_ofs@32; table = u32 count then records
[u32 path_len | path | pad4 | u64 ofs | u64 size | md5[16] | u32 flags]).
"""
import hashlib
import struct
import sys

MAGIC = b"GDPC"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def parse(d):
    if len(d) < 40 or d[:4] != MAGIC:
        raise ValueError("bad magic or too short: %r" % d[:8])
    ver, maj, mi, pa, flags = struct.unpack_from("<5I", d, 4)
    file_base, table_ofs = struct.unpack_from("<2Q", d, 24)
    if not (40 <= table_ofs <= len(d) - 4):
        raise ValueError("table_ofs %d outside file (%d)" % (table_ofs, len(d)))
    cnt = struct.unpack_from("<I", d, table_ofs)[0]
    if cnt > 65536:
        raise ValueError("implausible entry count %d" % cnt)
    entries, p = [], table_ofs + 4
    for i in range(cnt):
        if p + 4 > len(d):
            raise ValueError("entry %d header past EOF" % i)
        ln = struct.unpack_from("<I", d, p)[0]
        p += 4
        if p + ln > len(d):
            raise ValueError("entry %d path past EOF" % i)
        name = d[p:p + ln].rstrip(b"\0").decode("utf-8", "replace")
        p += ln + ((-ln) % 4)
        ofs, size = struct.unpack_from("<2Q", d, p)
        md5 = d[p + 16:p + 32]
        ef = struct.unpack_from("<I", d, p + 32)[0]
        p += 36
        entries.append({"path": name, "ofs": ofs, "size": size,
                        "md5": md5.hex(), "flags": ef})
    hdr = {"ver": ver, "version": "%d.%d.%d" % (maj, mi, pa), "flags": flags,
           "file_base": file_base, "table_ofs": table_ofs, "count": cnt,
           "table_end": p, "tail_bytes": len(d) - p}
    return hdr, entries


def dump(path):
    d = open(path, "rb").read()
    hdr, entries = parse(d)
    print("file=%s bytes=%d sha256=%s" % (path, len(d), sha(path)))
    print("header " + " ".join("%s=%s" % (k, v) for k, v in hdr.items()))
    for e in sorted(entries, key=lambda x: x["path"]):
        print("  entry path=%s ofs=%d size=%d flags=%d md5=%s"
              % (e["path"], e["ofs"], e["size"], e["flags"], e["md5"]))
    return 0


def entries_cmd(path):
    d = open(path, "rb").read()
    _, entries = parse(d)
    for e in sorted(entries, key=lambda x: x["path"]):
        print("%s %d %s %d" % (e["path"], e["size"], e["md5"], e["flags"]))
    return 0


def diff(a, b):
    da, db = open(a, "rb").read(), open(b, "rb").read()
    sa, sb = hashlib.sha256(da).hexdigest(), hashlib.sha256(db).hexdigest()
    print("A=%s bytes=%d sha256=%s" % (a, len(da), sa))
    print("B=%s bytes=%d sha256=%s" % (b, len(db), sb))
    print("identical=%s" % (sa == sb))
    n = min(len(da), len(db))
    diffs = [i for i in range(n) if da[i] != db[i]]
    print("size_delta=%d first_diff_offsets=%s diff_bytes_in_common=%d"
          % (len(db) - len(da), diffs[:16], len(diffs)))
    ok_a = da[:4] == MAGIC
    ok_b = db[:4] == MAGIC
    if ok_a and ok_b:
        ha, ea = parse(da)
        hb, eb = parse(db)
        pa = {e["path"]: e for e in ea}
        pb = {e["path"]: e for e in eb}
        only_a = sorted(set(pa) - set(pb))
        only_b = sorted(set(pb) - set(pa))
        print("entries A=%d B=%d only_in_A=%s only_in_B=%s" % (len(ea), len(eb), only_a, only_b))
        for name in sorted(set(pa) & set(pb)):
            x, y = pa[name], pb[name]
            if x["md5"] != y["md5"] or x["size"] != y["size"]:
                print("  entry_changed %s A(size=%d md5=%s) B(size=%d md5=%s)"
                      % (name, x["size"], x["md5"], y["size"], y["md5"]))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "DUMP":
        sys.exit(dump(sys.argv[2]))
    if cmd == "ENTRIES":
        sys.exit(entries_cmd(sys.argv[2]))
    if cmd == "DIFF":
        sys.exit(diff(sys.argv[2], sys.argv[3]))
    print("unknown command %s" % cmd)
    sys.exit(2)
