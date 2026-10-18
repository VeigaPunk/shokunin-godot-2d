#!/usr/bin/env python3
"""VER-14 independent structural parser for Godot PCK + export zip (round 101).

No Godot code or Godot tooling is involved: raw struct/zipfile/zlib parsing only.
Layout hypotheses are tested empirically; the one that verifies the most stored
per-file digests wins (defends against layout drift; 4.7.2 uses PCK v4).

Observed 4.7.2 PCK v4 layout (reversed from a real export, see shard):
  header (112 bytes):
    u32 magic 'GDPC' @0x00
    u32 pack_format_version = 4 @0x04
    u32 ver_major, ver_minor, ver_patch @0x08/0x0c/0x10
    u32 unknown word = 2 @0x14
    u64 data_offset @0x18 (112 here; first file byte)
    u64 dir_offset  @0x20 (directory table near EOF here)
    zero padding to 112
  directory @dir_offset:
    u32 file_count
    per entry: u32 path_byte_len (padded to 4), path bytes (NUL-padded, root
    relative, no 'res://'), u64 offset (relative to data_offset), u64 size,
    16-byte MD5 digest, u32 flags

Usage:
  python3 ver14_parse.py pck <file.pck>
  python3 ver14_parse.py zip <file.zip>
  python3 ver14_parse.py compare <file.pck> <file.zip>
"""
import hashlib
import json
import os
import struct
import sys
import zipfile
import zlib


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _mk_entry(path, rel_ofs, size, digest, flags, data_off, blob):
    abs_ofs = data_off + rel_ofs
    content = blob[abs_ofs:abs_ofs + size]
    md5_calc = hashlib.md5(content).digest()
    return {
        "path": path,
        "offset_rel": rel_ofs,
        "offset_abs": abs_ofs,
        "size": size,
        "stored_digest_hex": digest.hex(),
        "md5_calc_hex": md5_calc.hex(),
        "md5_match": md5_calc == digest,
        "sha256": hashlib.sha256(content).hexdigest(),
        "flags": flags,
    }


def _attempt_v4(blob, data_off, dir_off, count):
    """v4: directory at dir_off, entries = path/off/size/md5/flags."""
    if dir_off + 4 > len(blob) or count > 100000:
        return None
    off = dir_off + 4
    entries = []
    for _ in range(count):
        if off + 4 > len(blob):
            return None
        (plen,) = struct.unpack_from("<I", blob, off)
        off += 4
        if plen <= 0 or plen > 8192 or off + plen > len(blob):
            return None
        raw = blob[off:off + plen]
        off += plen
        path_bytes = raw.split(b"\x00", 1)[0]
        try:
            path = path_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return None
        if off + 36 > len(blob):
            return None
        rel_ofs, size = struct.unpack_from("<QQ", blob, off)
        off += 16
        digest = blob[off:off + 16]
        off += 16
        (flags,) = struct.unpack_from("<I", blob, off)
        off += 4
        if off > len(blob):
            return None
        e = _mk_entry(path, rel_ofs, size, digest, flags, data_off, blob)
        entries.append(e)
    return {"entries": entries, "table_end_off": off}


def _attempt_legacy(blob, off, file_base, count, per_entry_flags):
    """v2/v3 style: inline table with 'res://' prefixed paths."""
    entries = []
    for _ in range(count):
        if off + 4 > len(blob):
            return None
        (plen,) = struct.unpack_from("<I", blob, off)
        off += 4
        if plen <= 0 or plen > 8192 or off + plen > len(blob):
            return None
        raw = blob[off:off + plen]
        off += plen
        try:
            path = raw.split(b"\x00", 1)[0].decode("utf-8")
        except UnicodeDecodeError:
            return None
        if off + 32 > len(blob):
            return None
        ofs, size = struct.unpack_from("<QQ", blob, off)
        off += 16
        digest = blob[off:off + 16]
        off += 16
        flags = None
        if per_entry_flags:
            if off + 4 > len(blob):
                return None
            (flags,) = struct.unpack_from("<I", blob, off)
            off += 4
        e = _mk_entry(path, ofs, size, digest, flags, file_base, blob)
        entries.append(e)
    return {"entries": entries, "table_end_off": off}


def _section_stats(data_off, entries):
    spans = sorted((e["offset_abs"], e["offset_abs"] + e["size"]) for e in entries)
    gaps = []
    pos = data_off
    prev_end = None
    for s, ep in spans:
        if prev_end is not None and s < prev_end:
            gaps.append({"overlap_at": s, "prev_end": prev_end})
        if s > pos:
            gaps.append({"gap_start": pos, "gap_size": s - pos})
        pos = max(pos, ep)
        prev_end = pos
    return {"data_last_end": pos, "gaps": gaps}


def parse_pck(path):
    blob = open(path, "rb").read()
    out = {
        "file": path,
        "bytes": len(blob),
        "sha256": sha256_file(path),
        "magic_latin1": blob[:4].decode("latin1"),
        "header_hex128": blob[:128].hex(),
    }
    if len(blob) < 36:
        out["error"] = "too_small"
        return out
    fmtver, vmaj, vmin, vpat = struct.unpack_from("<IIII", blob, 4)
    out["pack_format_version"] = fmtver
    out["engine_version"] = f"{vmaj}.{vmin}.{vpat}"
    out["u32_le_first16"] = [struct.unpack_from("<I", blob, 4 * i)[0] for i in range(16)]

    candidates = []
    tried = []
    if fmtver == 4:
        (word14,) = struct.unpack_from("<I", blob, 0x14)
        (data_off,) = struct.unpack_from("<Q", blob, 0x18)
        (dir_off,) = struct.unpack_from("<Q", blob, 0x20)
        out["hdr_word_0x14"] = word14
        out["data_offset"] = data_off
        out["dir_offset"] = dir_off
        if 0 < dir_off < len(blob) and 0 < data_off < len(blob):
            (count,) = struct.unpack_from("<I", blob, dir_off)
            res = _attempt_v4(blob, data_off, dir_off, count)
            if res:
                verified = sum(1 for e in res["entries"] if e["md5_match"])
                res.update(layout="H4_gdpc4_dir_at_end", file_base=0, pack_flags=None,
                           file_count=count, md5_verified=verified)
                candidates.append(res)
            else:
                tried.append({"layout": "H4_gdpc4_dir_at_end", "rejected": "entry table parse failed"})
    (c2,) = struct.unpack_from("<I", blob, 20)
    for name, off, pef in (("H2_count@20,no_entry_flags", 24, False),
                           ("H2_count@20,entry_flags", 24, True)):
        if 1 <= c2 <= 100000:
            res = _attempt_legacy(blob, off, 0, c2, pef)
            if res:
                verified = sum(1 for e in res["entries"] if e["md5_match"])
                res.update(layout=name, file_base=0, pack_flags=None, file_count=c2,
                           md5_verified=verified)
                candidates.append(res)
            else:
                tried.append({"layout": name, "rejected": "entry table parse failed"})
    out["layout_candidates_tried"] = tried
    if not candidates:
        out["error"] = "no_layout_hypothesis_parsed"
        return out
    best = max(candidates, key=lambda r: r["md5_verified"])
    out.update(best)
    out["all_paths_res_prefix"] = all(e["path"].startswith("res://") for e in out["entries"])
    out["md5_all_match"] = out["md5_verified"] == out["file_count"]
    out["section"] = _section_stats(out.get("data_offset", 0), out["entries"])
    return out


def parse_zip(path):
    out = {
        "file": path,
        "bytes": os.path.getsize(path),
        "sha256": sha256_file(path),
    }
    with zipfile.ZipFile(path) as z:
        infos = []
        for i in z.infolist():
            data = z.read(i.filename)
            infos.append({
                "name": i.filename,
                "file_size": i.file_size,
                "compress_size": i.compress_size,
                "method": i.compress_type,
                "crc32_stored": "%08x" % i.CRC,
                "crc32_computed": "%08x" % (zlib.crc32(data) & 0xFFFFFFFF),
                "sha256": hashlib.sha256(data).hexdigest(),
                "date_time": list(i.date_time),
            })
        out["entries"] = infos
        out["testzip_first_bad"] = z.testzip()
        out["comment"] = z.comment.decode("utf-8", "replace")
    return out


def norm(name):
    for p in ("res://", "/"):
        if name.startswith(p):
            name = name[len(p):]
    return name


def compare(pck_path, zip_path):
    pck = parse_pck(pck_path)
    zipd = parse_zip(zip_path)
    pm = {norm(e["path"]): e for e in pck.get("entries", [])}
    zm = {norm(e["name"]): e for e in zipd.get("entries", [])}
    only_pck = sorted(set(pm) - set(zm))
    only_zip = sorted(set(zm) - set(pm))
    both = sorted(set(pm) & set(zm))
    diffs = []
    for n in both:
        if pm[n]["sha256"] != zm[n]["sha256"] or pm[n]["size"] != zm[n]["file_size"]:
            diffs.append(n)
    keep = ("file", "bytes", "sha256", "magic_latin1", "pack_format_version",
            "engine_version", "layout", "data_offset", "dir_offset", "file_count",
            "md5_verified", "md5_all_match", "all_paths_res_prefix", "section")
    return {
        "pck": {k: pck.get(k) for k in keep},
        "zip": {k: zipd.get(k) for k in ("file", "bytes", "sha256", "testzip_first_bad", "comment")},
        "zip_entry_count": len(zm),
        "only_in_pck": only_pck,
        "only_in_zip": only_zip,
        "content_diffs": diffs,
        "matched": len(both) - len(diffs),
    }


def main(argv):
    if len(argv) >= 3 and argv[1] == "pck":
        print(json.dumps(parse_pck(argv[2]), indent=1))
    elif len(argv) >= 3 and argv[1] == "zip":
        print(json.dumps(parse_zip(argv[2]), indent=1))
    elif len(argv) >= 4 and argv[1] == "compare":
        print(json.dumps(compare(argv[2], argv[3]), indent=1))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
