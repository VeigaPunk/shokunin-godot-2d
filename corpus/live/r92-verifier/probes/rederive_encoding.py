#!/usr/bin/env python3
"""r92 verifier — independent re-derivation of the pinned tile_map_data encoding.

Decodes the byte arrays pinned in the committed r92_tilemap_encoding signature
with an INDEPENDENT reader (2-byte format header + 12-byte records, six
little-endian int16 fields) and cross-checks the decoded cells against the
other pinned fields of the same row (used-cell lists, sources, atlas coords,
alt ids, lengths).  Nothing here trusts the probe's own decoder: the probe only
prints raw byte arrays.
"""
import ast
import pathlib

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus" / "live" / "r92-verifier" / "tree" / "corpus" / "fixtures" / "run_battery.py"
src = FIX.read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
sig = None
for elt in cases:
    t = ast.literal_eval(elt)
    if t[0] == "r92_tilemap_encoding":
        sig = t[4]
assert sig and sig.startswith("PASS tilemap_lattice encoding ")
fields = {}
for tok in sig.split()[3:]:
    k, _, v = tok.partition("=")
    fields[k] = v

def arr(name):
    s = fields[name]
    assert s.startswith("[") and s.endswith("]"), (name, s)
    body = s[1:-1]
    return [int(x) for x in body.split(",")] if body else []

def i16(b, off):
    v = b[off] | (b[off + 1] << 8)
    return v - 65536 if v >= 32768 else v

def decode(b):
    """2-byte header + 12-byte records -> (header, [record tuples])."""
    header = i16(b, 0)
    recs = []
    i = 2
    while i + 12 <= len(b):
        rec = tuple(i16(b, i + 2 * j) for j in range(6))
        recs.append(rec)
        i += 12
    return header, recs, len(b) - i

checks = []
def ck(name, cond, detail=""):
    checks.append((name, cond, detail))

for nm in ("one_bytes", "two_bytes", "alt_bytes", "tomb_set_bytes",
           "tomb_erase_bytes", "tomb_reset_bytes", "tomb_clear_bytes",
           "tomb_clear_set_bytes"):
    b = arr(nm)
    header, recs, rem = decode(b)
    print(f"{nm:22s} len={len(b):3d} pinned_len={fields.get(nm + '_len', 'n/a'):>4s} "
          f"header={header} records={len(recs)} remainder={rem}")
    for r in recs:
        print(f"      rec x={r[0]:4d} y={r[1]:4d} f2={r[2]:6d} f3={r[3]:6d} f4={r[4]:6d} f5={r[5]:6d}")
    ck(f"{nm}: header==0", header == 0, f"header={header}")
    ck(f"{nm}: len==2+12k", (len(b) - 2) % 12 == 0, f"len={len(b)}")
    if nm + "_len" in fields:
        ck(f"{nm}: len matches pinned", str(len(b)) == fields[nm + "_len"],
           f"{len(b)} vs {fields[nm + '_len']}")
    ck(f"{nm}: no remainder", rem == 0, f"rem={rem}")

# decoded cells vs the row's other pinned fields
h1, r1, _ = decode(arr("one_bytes"))
ck("one_bytes cell == (3,4) src 0 atlas (1,0)",
   r1 == [(3, 4, 0, 1, 0, 0)], f"{r1}")
h2, r2, _ = decode(arr("two_bytes"))
ck("two_bytes records == [(3,4,0,1,0,0), (7,-2,0,0,1,0)]",
   r2 == [(3, 4, 0, 1, 0, 0), (7, -2, 0, 0, 1, 0)], f"{r2}")
ck("stride == 12", fields["stride"] == "12", fields["stride"])
ck("two_bytes_len - one_bytes_len == stride",
   len(arr("two_bytes")) - len(arr("one_bytes")) == 12)
ck("arr_roundtrip_used == n2[3,4;7,-2]",
   fields["arr_roundtrip_used"] == "n2[3,4;7,-2]", fields["arr_roundtrip_used"])
ck("arr_roundtrip_atlas == 0,1 (the (7,-2) record's atlas)",
   fields["arr_roundtrip_atlas"] == "0,1", fields["arr_roundtrip_atlas"])
ha, ra, _ = decode(arr("alt_bytes"))
ck("alt_bytes rec0 == (3,4,0,1,0,alt_id)",
   ra[0] == (3, 4, 0, 1, 0, int(fields["alt_id_created"])), f"{ra[0]}")
ck("alt_bytes rec1 == tombstoned (7,-2) with f3..f5 == -1",
   ra[1] == (7, -2, -1, -1, -1, -1), f"{ra[1]}")
ck("alt_bytes: exactly one live (non-tombstoned) record", sum(
    1 for r in ra if r[2:] == (0, 1, 0, int(fields["alt_id_created"]))) == 1)

# tombstone semantics
hs, rs, _ = decode(arr("tomb_set_bytes"))
he, re_, _ = decode(arr("tomb_erase_bytes"))
ck("tomb_erase: length unchanged (high-water mark)",
   len(arr("tomb_set_bytes")) == len(arr("tomb_erase_bytes")),
   f"{len(arr('tomb_set_bytes'))} -> {len(arr('tomb_erase_bytes'))}")
ck("tomb_erase: x/y preserved, 8-byte tail (fields 2..5) set to -1",
   rs[0][:2] == re_[0][:2] and re_[0][2:] == (-1, -1, -1, -1) and rs[0][2:] == (0, 0, 0, 0),
   f"{rs[0]} -> {re_[0]}")
ck("tomb_erase bytes == tomb_clear bytes (one tombstone encoding)",
   arr("tomb_erase_bytes") == arr("tomb_clear_bytes"))
ck("tombstone tail is exactly 8 x 0xFF at the record end",
   arr("tomb_erase_bytes")[6:] == [255] * 8, f"{arr('tomb_erase_bytes')[6:]}")
ck("tomb_erase_used == n0[]", fields["tomb_erase_used"] == "n0[]", fields["tomb_erase_used"])
ck("tomb_reset == tomb_set (re-set rewrites the record)",
   arr("tomb_reset_bytes") == arr("tomb_set_bytes"))
hc, rc, _ = decode(arr("tomb_clear_bytes"))
ck("tomb_clear: length unchanged, every field after f1 tombstoned",
   len(arr("tomb_clear_bytes")) == len(arr("tomb_set_bytes"))
   and rc[0] == (1, 1, -1, -1, -1, -1), f"{rc[0]}")
hcs, rcs, _ = decode(arr("tomb_clear_set_bytes"))
ck("tomb_clear_set: 2 records, rec0 tombstoned, rec1 == (5,5,0,0,0,0)",
   rcs == [(1, 1, -1, -1, -1, -1), (5, 5, 0, 0, 0, 0)], f"{rcs}")
ck("tomb_clear_set_len == 2+2*12", len(arr("tomb_clear_set_bytes")) == 26)

# truncated / short refusal arithmetic
ck("truncated_len == 14 (one record survives 20-element input)",
   fields["truncated_len"] == "14", fields["truncated_len"])
ck("short_arr_len == 0", fields["short_arr_len"] == "0", fields["short_arr_len"])
ck("20-element input leaves a 6-byte partial record (corrupted)",
   (20 - 2) % 12 == 6)

n_fail = sum(1 for _, ok, _ in checks if not ok)
for name, ok, detail in checks:
    print(f"{'OK  ' if ok else 'FAIL'} {name}" + (f"  [{detail}]" if not ok else ""))
print(f"\nchecks={len(checks)} fails={n_fail}")
raise SystemExit(1 if n_fail else 0)
