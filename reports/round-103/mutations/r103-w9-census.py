#!/usr/bin/env python3
# r103 W9: PCK/container census for the second-root export-divergence repro.
# Usage: r103-w9-census.py <out_dir> [--pair NAME_A NAME_B ...]
# Prints per-file size/sha256/head40/tail16/GDPC-offsets, and for any container
# parses the PCK (standalone at 0, or the last GDPC that carries project.binary).
# Pure read-only; deterministic; no device tokens pinned.
import hashlib, os, struct, sys


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def u64(b, o):
    return struct.unpack_from("<Q", b, o)[0]


def parse_pck(b, base):
    if base + 40 > len(b) or b[base:base + 4] != b"GDPC":
        return None
    hdr = {
        "version": u32(b, base + 4), "major": u32(b, base + 8),
        "minor": u32(b, base + 12), "patch": u32(b, base + 16),
        "flags": u32(b, base + 20), "file_base": u64(b, base + 0x18),
        "dir_offset": u64(b, base + 0x20),
    }
    doff = base + hdr["dir_offset"]
    if doff + 4 > len(b):
        return None
    count = u32(b, doff)
    off = doff + 4
    entries = {}
    for _ in range(count):
        if off + 4 > len(b):
            return None
        plen = u32(b, off)
        off += 4
        if off + plen + 36 > len(b):
            return None
        name = b[off:off + plen].split(b"\0", 1)[0].decode("utf-8", "replace")
        off += plen
        off = ((off + 3) // 4) * 4
        entries[name] = {"size": u64(b, off + 8), "offset": u64(b, off),
                         "flags": u32(b, off + 32)}
        off += 36
    hdr["count"] = count
    hdr["entries"] = entries
    return hdr


def gdpc_offsets(b):
    out, i = [], b.find(b"GDPC")
    while i != -1:
        out.append(i)
        i = b.find(b"GDPC", i + 1)
    return out


def census(path):
    b = open(path, "rb").read()
    rec = {"bytes": len(b), "sha256": sha(path), "head40_hex": b[:40].hex(),
           "tail16_hex": b[-16:].hex(), "gdpc_offsets": gdpc_offsets(b)}
    hdr = parse_pck(b, 0)
    if hdr is not None:
        rec["kind"] = "pck_standalone"
    else:
        for cand in reversed(rec["gdpc_offsets"]):
            h = parse_pck(b, cand)
            if h and "project.binary" in h["entries"]:
                hdr = h
                rec["kind"] = "elf_with_embedded_pck"
                rec["embedded_pck_offset"] = cand
                break
        else:
            rec["kind"] = "elf_no_pck"
    if hdr is not None:
        rec["pck"] = {
            "v": hdr["version"], "godot": ".".join(str(hdr[k]) for k in ("major", "minor", "patch")),
            "flags": hdr["flags"], "file_base": hdr["file_base"],
            "dir_offset": hdr["dir_offset"], "count": hdr["count"],
            "names_sha256": hashlib.sha256("\n".join(sorted(hdr["entries"])).encode()).hexdigest(),
            "entries": {k: v["size"] for k, v in sorted(hdr["entries"].items())},
        }
    return rec


def main():
    out = sys.argv[1]
    pairs = []
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--pair":
            pairs.append((sys.argv[i + 1], sys.argv[i + 2]))
            i += 3
        else:
            i += 1
    reps = {}
    for name in sorted(os.listdir(out)):
        p = os.path.join(out, name)
        if not os.path.isfile(p) or name.endswith(".log"):
            continue
        try:
            reps[name] = census(p)
        except Exception as e:  # noqa: BLE001
            reps[name] = {"error": str(e)}
    for name, rec in reps.items():
        print("==", name, rec.get("bytes", "?"), "bytes kind=%s" % rec.get("kind"))
        if "error" in rec:
            print("   error", rec["error"])
            continue
        print("   sha256", rec["sha256"])
        print("   head40", rec["head40_hex"])
        print("   tail16", rec["tail16_hex"])
        print("   gdpc_offsets", rec["gdpc_offsets"])
        if "embedded_pck_offset" in rec:
            print("   embedded_pck_offset", rec["embedded_pck_offset"])
        if "pck" in rec:
            pk = rec["pck"]
            print("   pck v=%d %s flags=%d file_base=%d dir_offset=%d count=%d names_sha256=%s"
                  % (pk["v"], pk["godot"], pk["flags"], pk["file_base"], pk["dir_offset"],
                     pk["count"], pk["names_sha256"]))
            for k, v in pk["entries"].items():
                print("      %s %d" % (k, v))
    for a, b in pairs:
        ra, rb = reps.get(a), reps.get(b)
        if not ra or not rb:
            print("== pair %s vs %s: MISSING" % (a, b))
            continue
        same_b = ra.get("sha256") == rb.get("sha256") and ra.get("bytes") == rb.get("bytes")
        print("== pair %s vs %s: sha_bytes_equal=%s sizes=%s/%s"
              % (a, b, same_b, ra.get("bytes"), rb.get("bytes")))
        pa, pb = ra.get("pck"), rb.get("pck")
        if pa and pb:
            print("   names_equal=%s sizes_map_equal=%s flags_equal=%s file_base_equal=%s"
                  % (pa["entries"].keys() == pb["entries"].keys(),
                     pa["entries"] == pb["entries"], pa["flags"] == pb["flags"],
                     pa["file_base"] == pb["file_base"]))


if __name__ == "__main__":
    main()
