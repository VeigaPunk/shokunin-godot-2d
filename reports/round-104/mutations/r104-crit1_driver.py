#!/usr/bin/env python3
"""r104-C1 attack matrix driver.

Builds a fresh scratch Godot project per shape under <root>/matrix/<shape>/,
scans it with the editor, optionally forges state, then runs the C1 reader and
prints the observed lattice line next to the shape's expectation.

Nothing outside <root> is written. run_battery.py is never invoked.

Usage: python3 r104-crit1_driver.py [shape ...]
"""
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
READER = HERE / "r104-crit1_read.gd"
ROOT = Path(os.environ.get("R104_CRIT1_ROOT", "/var/tmp/r104-crit1/matrix"))
GODOT = os.environ.get("GODOT", "godot")

PROJECT = (
    'config_version=5\n\n[application]\nconfig/name="Crit1"\n'
    'config/features=PackedStringArray("4.7")\n'
)


def read_cache(p):
    b = Path(p).read_bytes()
    off = 0
    (n,) = struct.unpack_from("<I", b, off)
    off += 4
    rows = []
    for _ in range(n):
        (uid,) = struct.unpack_from("<q", b, off)
        off += 8
        (ln,) = struct.unpack_from("<I", b, off)
        off += 4
        rows.append([uid, b[off:off + ln].decode()])
        off += ln
    assert off == len(b), (off, len(b))
    return rows


def write_cache(p, rows):
    out = struct.pack("<I", len(rows))
    for uid, path in rows:
        pb = path.encode()
        out += struct.pack("<q", uid) + struct.pack("<I", len(pb)) + pb
    Path(p).write_bytes(out)


def png(path, seed=0):
    import zlib
    w = h = 4
    raw = b"".join(b"\x00" + bytes([255, seed * 37 % 256, 0, 255]) * w for _ in range(h))

    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    data = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    Path(path).write_bytes(data)


def build(proj, with_png=True):
    if proj.exists():
        shutil.rmtree(proj)
    proj.mkdir(parents=True)
    (proj / "project.godot").write_text(PROJECT)
    (proj / "alpha.gd").write_text("extends Node\n")
    (proj / "beta.gd").write_text("extends Node\n")
    (proj / "alpha.gd.uid").write_text("uid://alphaaaaaaaaa\n")
    (proj / "beta.gd.uid").write_text("uid://bbbbbbbbbbbb\n")
    if with_png:
        png(proj / "tex.png")


def scan(proj):
    return subprocess.run([GODOT, "--headless", "--path", str(proj), "--editor", "--quit"],
                          capture_output=True, text=True, timeout=180)


def reader(proj, arm):
    shutil.copy2(READER, proj / "crit1_read.gd")
    p = subprocess.run([GODOT, "--headless", "--path", str(proj), "--script",
                        "res://crit1_read.gd", "--", "--arm=" + arm],
                       capture_output=True, text=True, timeout=60)
    line = next((l for l in (p.stdout + p.stderr).splitlines() if l.startswith("CRIT1")), "<no CRIT1 line>")
    return line, p.returncode


SHAPES = []


def shape(fn):
    SHAPES.append(fn)
    return fn


@shape
def S0_baseline():
    """Baseline: distinct sidecar uids -> every path registered, no collision."""
    proj = ROOT / "S0" / "proj"
    build(proj)
    scan(proj)
    lines = {a: reader(proj, a)[0] for a in ("census", "ident", "remap", "collision")}
    rows = read_cache(proj / ".godot" / "uid_cache.bin")
    ids = {p: u for u, p in rows}
    exp = {
        "census": "alpha/beta/tex each resolve to a nonzero uid",
        "ident": "reuse_same=1 post_reuse_same=1",
        "remap": "load_ok=1 exists_png=1 exists_import=0",
        "collision": "same_id=0, each uid resolves to its own path",
    }
    ok = (ids.get("res://alpha.gd", -1) > 0 and ids.get("res://beta.gd", -1) > 0
          and ids.get("res://alpha.gd") != ids.get("res://beta.gd"))
    return exp, lines, {"cache_ids": ids}, ok


@shape
def A1_sidecar_uid_collision():
    """Forge alpha.gd.uid to beta's uid text BEFORE the scan: one path must lose."""
    proj = ROOT / "A1" / "proj"
    build(proj)
    beta_text = (proj / "beta.gd.uid").read_text().strip()
    (proj / "alpha.gd.uid").write_text(beta_text + "\n")
    r = scan(proj)
    warn = [l for l in (r.stdout + r.stderr).splitlines() if "duplicate" in l.lower()]
    lines = {a: reader(proj, a)[0] for a in ("census", "collision")}
    rows = read_cache(proj / ".godot" / "uid_cache.bin")
    ids = {p: u for u, p in rows}
    loser = [p for p in ("res://alpha.gd", "res://beta.gd") if p not in ids]
    return ({"census": "exactly ONE of alpha/beta registered",
             "collision": "loser uid=-1",
             "engine": "WARNING line naming both paths"},
            dict(lines, engine_warning=warn),
            {"cache_ids": ids, "loser": loser},
            "res://alpha.gd" not in ids and "res://beta.gd" in ids
            and loser == ["res://alpha.gd"] and bool(warn))


@shape
def A2_import_uid_collision():
    """Forge the .import uid= field to collide with beta -> beta must lose."""
    proj = ROOT / "A2" / "proj"
    build(proj)
    scan(proj)
    imp = proj / "tex.png.import"
    beta_text = (proj / "beta.gd.uid").read_text().strip()
    text = imp.read_text()
    import re
    text = re.sub(r'^uid="[^"]*"', 'uid="%s"' % beta_text, text, count=1, flags=re.M)
    imp.write_text(text)
    # The .import uid is only consulted on an actual REIMPORT; with an
    # unchanged source and a live artifact the editor keeps the existing
    # filesystem_cache row and never reads the uid= field. Force a reimport by
    # changing the source bytes.
    png(proj / "tex.png", seed=1)
    r = scan(proj)
    warn = [l for l in (r.stdout + r.stderr).splitlines() if "duplicate" in l.lower()]
    lines = {a: reader(proj, a)[0] for a in ("census", "collision", "remap")}
    rows = read_cache(proj / ".godot" / "uid_cache.bin")
    ids = {p: u for u, p in rows}
    return ({"census": "beta unregistered, tex.png takes the contested id",
             "collision": "beta uid=-1",
             "engine": "incremental reimport is SILENT (fresh scan warns, see shard)"},
            dict(lines, engine_warning=warn),
            {"cache_ids": ids, "tex_rows": [u for u, q in read_cache(
                proj / ".godot" / "uid_cache.bin") if q == "res://tex.png"]},
            "res://beta.gd" not in ids and "res://tex.png" in ids)


@shape
def A3_cache_id_swap():
    """Rewrite uid_cache.bin to swap alpha/beta ids: receipts must echo the swap."""
    proj = ROOT / "A3" / "proj"
    build(proj)
    scan(proj)
    cache = proj / ".godot" / "uid_cache.bin"
    rows = read_cache(cache)
    d = {p: u for u, p in rows}
    a, b = d["res://alpha.gd"], d["res://beta.gd"]
    for r in rows:
        if r[1] == "res://alpha.gd":
            r[0] = b
        elif r[1] == "res://beta.gd":
            r[0] = a
    write_cache(cache, rows)
    line, _ = reader(proj, "census")
    # the sidecars still carry the ORIGINAL texts
    sidecar_a = (proj / "alpha.gd.uid").read_text().strip()
    sidecar_b = (proj / "beta.gd.uid").read_text().strip()
    after = {p: u for u, p in read_cache(cache)}
    ok = (f"alpha.gd={b}" in line and f"beta.gd={a}" in line
          and after["res://alpha.gd"] == b)
    return ({"census": "alpha reports beta's original id and vice versa",
             "sidecar": "unchanged (id:path binding came from the cache alone)"},
            {"census_line": line},
            {"swapped": {a: b, b: a}, "sidecars": [sidecar_a, sidecar_b], "cache_after": after},
            ok)


@shape
def A4_cache_collision():
    """Point beta's cache row at alpha's id: both paths then resolve to one path."""
    proj = ROOT / "A4" / "proj"
    build(proj)
    scan(proj)
    cache = proj / ".godot" / "uid_cache.bin"
    rows = read_cache(cache)
    d = {p: u for u, p in rows}
    for r in rows:
        if r[1] == "res://beta.gd":
            r[0] = d["res://alpha.gd"]
    write_cache(cache, rows)
    lines = {a: reader(proj, a)[0] for a in ("census", "collision")}
    after = read_cache(cache)
    return ({"census": "alpha and beta report the SAME id (no dedupe in the cache)",
             "collision": "same_id=1 and get_id_path returns ONE path for both"},
            lines,
            {"cache_after": after},
            "same_id=1" in lines["collision"]
            and "alpha_resolves=res://beta.gd" in lines["collision"])


@shape
def A5_cache_ghost_path():
    """Forge a cache row to an id whose path does not exist: resolution fabricates it."""
    proj = ROOT / "A5" / "proj"
    build(proj)
    scan(proj)
    cache = proj / ".godot" / "uid_cache.bin"
    rows = read_cache(cache)
    for r in rows:
        if r[1] == "res://alpha.gd":
            r[1] = "res://ghost_never_created.gd"
    write_cache(cache, rows)
    line, _ = reader(proj, "census")
    after = {p: u for u, p in read_cache(cache)}
    ghost = Path(proj) / "ghost_never_created.gd"
    return ({"census": "alpha.gd uid=-1; a nonexistent path holds the id",
             "disk": "ghost path still absent"},
            {"census_line": line},
            {"cache_after": after, "ghost_on_disk": ghost.exists()},
            "alpha.gd=-1" in line
            and after.get("res://ghost_never_created.gd") == 803467965278618112
            and not ghost.exists())


@shape
def A6_sidecar_garbage():
    """Malformed sidecar text (not a uid:// token) -> path unregistered, no cache row."""
    proj = ROOT / "A6" / "proj"
    build(proj)
    (proj / "alpha.gd.uid").write_text("not-a-uid\n")
    scan(proj)
    line, _ = reader(proj, "census")
    ids = {p: u for u, p in read_cache(proj / ".godot" / "uid_cache.bin")}
    return ({"census": "alpha.gd uid=-1 (sidecar rejected)"},
            {"census_line": line},
            {"cache_ids": ids},
            "alpha.gd=-1" in line and "res://alpha.gd" not in ids)


@shape
def A7_sidecar_short_token():
    """A SHORT but well-formed uid:// token is accepted, minting a tiny id."""
    proj = ROOT / "A7" / "proj"
    build(proj)
    (proj / "alpha.gd.uid").write_text("uid://short\n")
    scan(proj)
    line, _ = reader(proj, "census")
    ids = {p: u for u, p in read_cache(proj / ".godot" / "uid_cache.bin")}
    return ({"census": "alpha.gd resolves to a tiny nonzero id (24345957 measured standalone)"},
            {"census_line": line},
            {"cache_ids": ids},
            0 < ids.get("res://alpha.gd", -1) < 2 ** 32)


@shape
def A8_cache_deleted():
    """Delete .godot/uid_cache.bin: the whole lattice zeroes and a plain run does not rebuild it."""
    proj = ROOT / "A8" / "proj"
    build(proj)
    scan(proj)
    cache = proj / ".godot" / "uid_cache.bin"
    before = {p: u for u, p in read_cache(cache)}
    cache.unlink()
    lines = {a: reader(proj, a)[0] for a in ("census", "collision", "remap")}
    regenerated = cache.exists()
    after = {p: u for u, p in read_cache(cache)} if regenerated else {}
    return ({"census": "every path uid=-1",
             "collision": "alpha=beta=-1, same_id=0",
             "remap": "tex.png uid=-1 but load_ok=1 (remap needs no uid)"},
            lines,
            {"cache_before": before, "regenerated": regenerated, "cache_after": after},
            "alpha.gd=-1" in lines["census"] and not regenerated)


@shape
def A9_remap_dest_missing():
    """Delete the imported .ctex: exists() stays true but the load fails."""
    proj = ROOT / "A9" / "proj"
    build(proj)
    scan(proj)
    for f in (proj / ".godot" / "imported").glob("*.ctex"):
        f.unlink()
    line, _ = reader(proj, "remap")
    return ({"remap": "exists_png=1, load_ok=0 (remap target gone)"},
            {"remap_line": line},
            {},
            "exists_png=1" in line and "load_ok=0" in line)


@shape
def A10_remap_import_missing():
    """Delete the .import file: exists() turns false and no loader is found."""
    proj = ROOT / "A10" / "proj"
    build(proj)
    scan(proj)
    (proj / "tex.png.import").unlink()
    line, _ = reader(proj, "remap")
    return ({"remap": "exists_png=0, load_ok=0"},
            {"remap_line": line},
            {},
            "exists_png=0" in line and "load_ok=0" in line)


@shape
def A11_sidecar_overrides_cache_after_rescan():
    """Forge a sidecar to an already-used uid with the cache present, then rescan."""
    proj = ROOT / "A11" / "proj"
    build(proj)
    scan(proj)
    plain_before, _ = reader(proj, "census")
    (proj / "alpha.gd.uid").write_text((proj / "beta.gd.uid").read_text())
    plain_after, _ = reader(proj, "census")
    # An unchanged tree short-circuits the scan; drop the editor's filesystem
    # cache so the sidecars are actually re-read.
    shutil.rmtree(proj / ".godot" / "editor")
    r = scan(proj)
    warn = [l for l in (r.stdout + r.stderr).splitlines() if "duplicate" in l.lower()]
    after_scan, _ = reader(proj, "census")
    return ({"plain_run_before_scan": "unchanged (cache wins over sidecar)",
             "plain_run_after_forge": "unchanged (sidecar not read at runtime)",
             "after_rescan": "the contested id is re-decided; a path goes to -1"},
            {"before": plain_before, "after_forge": plain_after,
             "after_scan": after_scan, "engine_warning": warn},
            {},
            plain_before == plain_after and bool(warn) and after_scan != plain_after)


@shape
def A12_path_move_stale():
    """Rename a registered source: the cache keeps the dead path and its id alive."""
    proj = ROOT / "A12" / "proj"
    build(proj)
    scan(proj)
    cache = proj / ".godot" / "uid_cache.bin"
    before = {p: u for u, p in read_cache(cache)}
    (proj / "alpha.gd").rename(proj / "alpha_moved.gd")
    line, _ = reader(proj, "census")
    after = {p: u for u, p in read_cache(cache)}
    # the dead path still answers, the new path is unregistered
    dead = before.get("res://alpha.gd")
    shutil.rmtree(proj / ".godot" / "editor")
    scan(proj)
    rescanned = {p: u for u, p in read_cache(cache)}
    return ({"census": "alpha.gd still reports its old uid though the file is gone",
             "after_full_rescan": "the new path is bound to a freshly minted id"},
            {"census_line": line},
            {"cache_before": before, "cache_after_plain_run": after,
             "cache_after_rescan": rescanned, "dead_id": dead},
            f"alpha.gd={dead}" in line
            and after.get("res://alpha.gd") == dead
            and "res://alpha.gd" not in rescanned
            and rescanned.get("res://alpha_moved.gd", -1) > 0
            and rescanned.get("res://alpha_moved.gd") != dead)


@shape
def A13_uid_reference_anti_echo():
    """Forge a cache id swap: the engine's own uid:// lookup must follow the cache,
    not the sidecar text -- the decisive anti-echo discriminator."""
    proj = ROOT / "A13" / "proj"
    build(proj)
    scan(proj)
    cache = proj / ".godot" / "uid_cache.bin"
    rows = read_cache(cache)
    d = {p: u for u, p in rows}
    a, b = d["res://alpha.gd"], d["res://beta.gd"]
    text_a = ResourceUID_text(proj, "alpha.gd")
    text_b = ResourceUID_text(proj, "beta.gd")
    for r in rows:
        if r[1] == "res://alpha.gd":
            r[0] = b
        elif r[1] == "res://beta.gd":
            r[0] = a
    write_cache(cache, rows)
    shutil.copy2(READER, proj / "crit1_lookup.gd")
    (proj / "crit1_lookup.gd").write_text(
        "extends SceneTree\nfunc _init():\n"
        '\tfor u in ["%s", "%s"]:\n' % (text_a, text_b) +
        '\t\tvar r = ResourceLoader.load(u)\n'
        '\t\tprint("CRIT1 lookup ", u, " -> ", r.resource_path if r else "<null>")\n'
        "\tquit()\n")
    r = subprocess.run([GODOT, "--headless", "--path", str(proj), "--script",
                        "res://crit1_lookup.gd"], capture_output=True, text=True, timeout=60)
    out = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("CRIT1 lookup")]
    return ({"lookup sidecar_a_text": "resolves to res://beta.gd (cache wins)",
             "lookup sidecar_b_text": "resolves to res://alpha.gd (cache wins)"},
            {"lookup_lines": out},
            {"sidecar_texts": {text_a: "alpha.gd", text_b: "beta.gd"}, "swapped": {a: b, b: a}},
            len(out) == 2 and "-> res://beta.gd" in out[0] and "-> res://alpha.gd" in out[1])


def ResourceUID_text(proj, name):
    """The uid:// text the fixture wrote into <name>.uid (no engine needed)."""
    return (Path(proj) / (name + ".uid")).read_text().strip()


def main():
    want = set(sys.argv[1:])
    ROOT.mkdir(parents=True, exist_ok=True)
    print("root=%s godot=%s" % (ROOT, GODOT))
    fails = 0
    for fn in SHAPES:
        name = fn.__name__
        if want and name not in want:
            continue
        try:
            exp, lines, extra, ok = fn()
        except Exception as exc:  # noqa: BLE001
            print("SHAPE %s EXCEPTION %r" % (name, exc))
            fails += 1
            continue
        print("\n=== SHAPE %s : %s" % (name, "AS_EXPECTED" if ok else "UNEXPECTED"))
        for k, v in exp.items():
            print("   expect %-22s %s" % (k, v))
        for k, v in lines.items():
            print("   obs    %-22s %s" % (k, v))
        for k, v in extra.items():
            print("   data   %-22s %s" % (k, v))
        if not ok:
            fails += 1
    print("\nshapes_run=%d unexpected=%d" % (len([f for f in SHAPES if not want or f.__name__ in want]), fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
