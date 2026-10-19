#!/usr/bin/env python3
"""r104 M3 / mut03 — remap forgery must REJECT E3.

Two phases against the ResourceLoader/.import remap lattice:

  P1 (primary, the landed E3 fixture) — `corpus/fixtures/res_uid_s03.gd` stages
     its own child project from in-file constants under `RES_UID_ROOT`, runs a
     child Godot process, and asserts every receipt field against a hard-coded
     expected table. Forgery shapes pre-plant the fixture's scratch inputs
     (`.import`, child transcript, uid_cache.bin, whole staged project) at the
     scratch root before the run; the genuine receipt must survive unchanged.
  P2 (secondary, `res_uid_w07.gd`'s importremap flow) — the live-import remap
     matrix F1..F7 over a battery-staged project (mkpng -> --import ->
     importremap), with `naive` (transcript self-consistency) and `anchored`
     (static + disk-derived + real re-run) predicates.

Measured on Godot 4.7.2: the uid the loader reports is served by
`.godot/uid_cache.bin`, not the `.import` `uid=` line, and is a function of the
*project name* — so in a battery row (timestamped project name) no uid literal
is pinnable. `res_uid_s03.gd` sidesteps this by hand-authoring its own cache
with a fixed id, which is why its uidcache arm CAN pin a literal.

Hard rules honoured: `run_battery.py` NEVER executed; scratch under
/var/tmp/r104-M3 (never /tmp — EDQUOT); the repo is read-only from here; no
device-census tokens; fixtures are never edited in the repo.
"""

import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/var/tmp/r104-M3/mut03")
REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = REPO_ROOT / "corpus" / "fixtures"
GODOT = "godot"
SCRIPT_TIMEOUT = 60
IMPORT_TIMEOUT = 180
S03 = "res_uid_s03.gd"
W07 = "res_uid_w07.gd"
PNG = "res://w07_probe.png"
PNG_FILE = "w07_probe.png"
FORGED_ID = 7777000011112222333

UID_HELPER = """extends SceneTree
func _init() -> void:
\tfor a in OS.get_cmdline_user_args():
\t\tif a.begins_with("--id="):
\t\t\tprint("M3UID id_to_text=%s" % ResourceUID.id_to_text(int(a.substr(5))))
\tquit(0)
"""

CONTENT_HELPER = """extends SceneTree
func _init() -> void:
\tvar t = ResourceLoader.load("res://%s")
\tvar sz := Vector2i(-1, -1)
\tvar px := Color(0, 0, 0, 0)
\tif t != null:
\t\tsz = t.get_size()
\t\tvar img: Image = t.get_image()
\t\tpx = img.get_pixel(0, 0)
\tprint("M3CONTENT cls=%%s size=%%dx%%d pixel0=%%s" %% [
\t\tt.get_class() if t != null else "<null>", sz.x, sz.y, px])
\tquit(0)
""" % PNG_FILE

runs = []
verdicts = {}
ANCHOR_CTEX = PNG_FILE + "-" + hashlib.md5(PNG.encode()).hexdigest() + ".ctex"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, timeout=SCRIPT_TIMEOUT, cwd=None, env=None):
    t0 = time.time()
    full_env = None
    if env:
        full_env = os.environ.copy()
        full_env.update(env)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, cwd=cwd, env=full_env)
        out, rc = proc.stdout + proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") + (exc.stderr or "")
        rc = None
    rec = {"cmd": cmd, "rc": rc, "ms": int((time.time() - t0) * 1000),
           "bytes": len(out), "sha256": hashlib.sha256(out.encode()).hexdigest()}
    runs.append(rec)
    return out, rec


def stage(label):
    dst = ROOT / label
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for item in sorted(FIXTURES.iterdir()):
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dst / item.name)
        else:
            shutil.copy2(item, dst / item.name)
    proj = dst / "project.godot"
    proj.write_text(proj.read_text().replace(
        'config/name="MechanicOneShotTest"',
        f'config/name="M3mut03-{label}"', 1))
    shutil.copy2(dst / "controls" / "pickup.tscn", dst / "pickup.tscn")
    (dst / "m3_uid.gd").write_text(UID_HELPER)
    (dst / "m3_content.gd").write_text(CONTENT_HELPER)
    return dst


def lines_with(output, verb):
    return [ln for ln in output.splitlines() if ln.startswith("PASS " + verb + " ")]


def fields_of(lines):
    f = {}
    for ln in lines:
        for tok in ln.split(" "):
            if "=" in tok:
                k, _, v = tok.partition("=")
                f.setdefault(k, v)
    return f


# =====================================================================  P1

def s03_run(proj, arm, root):
    return run([GODOT, "--headless", "--path", str(proj), "--script",
                "res://%s" % S03, "--", "--arm=%s" % arm],
               cwd=ROOT, env={"RES_UID_ROOT": str(root)})


def phase1():
    proj = stage("p1")
    print("M3P1 fixture=%s sha256=%s" % (S03, sha256_file(FIXTURES / S03)))
    arms = ["resolve", "uidcache", "missing", "refuse", "cache"]
    out, rec = s03_run(proj, "resolve", ROOT / "p1" / "ctrl")
    control = {}
    for arm in arms:
        out, _ = s03_run(proj, arm, ROOT / "p1" / "ctrl")
        control[arm] = lines_with(out, "res_uid_s03")
    print("M3P1 control arms=%s" % {a: (len(v) == 1) for a, v in control.items()})
    for arm in arms:
        print("M3P1 control| " + (control[arm][0] if control[arm] else "<none>"))

    def shape(label, plant):
        root = ROOT / "p1" / label
        if root.exists():
            shutil.rmtree(root)
        (root / "res_uid_s03").mkdir(parents=True)
        plant(root / "res_uid_s03")
        res = {}
        for arm in arms:
            out, rec = s03_run(proj, arm, root)
            got = lines_with(out, "res_uid_s03")
            res[arm] = {"neutralized": got == control[arm], "lines": got,
                        "bytes": rec["bytes"]}
        alln = all(v["neutralized"] for v in res.values())
        print("M3P1 %-22s all_arms_neutralized=%s" % (label, alln))
        return res, alln

    def plant_import(d):
        (d / "resolve" / "proj").mkdir(parents=True, exist_ok=True)
        (d / "resolve" / "proj" / "asset.png.import").write_text(
            '[remap]\nimporter="forged"\ntype="Resource"\n'
            'uid="uid://bqk3m5n7qar1"\npath="res://gen/FORGED.tres"\n')

    def plant_log(d):
        (d / "resolve").mkdir(parents=True, exist_ok=True)
        (d / "resolve" / "child.log").write_text(
            "CHILD resolve load_class=Resource load_name=FORGED "
            "load_path=res://forged.png\nCHILD resolve done\n")

    def plant_cache(d):
        (d / "uidcache" / "proj" / ".godot").mkdir(parents=True, exist_ok=True)
        (d / "uidcache" / "proj" / ".godot" / "uid_cache.bin").write_bytes(
            struct.pack("<Iq", 1, 7777000011112222333))

    def plant_whole(d):
        (d / "resolve" / "proj").mkdir(parents=True, exist_ok=True)
        (d / "resolve" / "proj" / "project.godot").write_text(
            '[application]\nconfig/name="FORGED"\n')
        (d / "resolve" / "proj" / "asset.png").write_bytes(b"not a png\n")
        (d / "resolve" / "proj" / "child.gd").write_text(
            "extends SceneTree\nfunc _init() -> void:\n"
            "\tprint(\"CHILD resolve load_class=Resource load_name=FORGED\")\n"
            "\tprint(\"CHILD resolve done\")\n\tquit(0)\n")

    def plant_all(d):
        plant_import(d)
        plant_log(d)
        plant_cache(d)
        plant_whole(d)

    shapes = {}
    for label, fn in [("S1_import", plant_import), ("S2_childlog", plant_log),
                      ("S3_uidcache", plant_cache), ("S4_wholeproj", plant_whole),
                      ("S5_all", plant_all)]:
        shapes[label], _ = shape(label, fn)
    verdicts["p1"] = {"control": control, "shapes": shapes,
                      "all_neutralized": all(
                          v["neutralized"] for s in shapes.values()
                          for v in s.values())}
    print("M3P1 all_neutralized=%s" % verdicts["p1"]["all_neutralized"])
    return proj


# =====================================================================  P2

def w07_receipt(out):
    return [ln for ln in out.splitlines() if ln.startswith("PASS res_uid_w07 ")]


def static_anchors(lines):
    f = fields_of(lines)
    return {
        "import_exists": f.get("import_exists") == "1",
        "remap_target": f.get("path_line", "").endswith(ANCHOR_CTEX + '"'),
        "id_path_source": f.get("id_path") == PNG,
        "loaded_cls_texture": f.get("loaded_cls") == "CompressedTexture2D",
        "loaded_path_source": f.get("loaded_path") == PNG,
        "remap_exists": f.get("remap_exists") == "1",
    }


def naive_of(lines):
    f = fields_of(lines)
    return bool(lines) and f.get("text_eq") == "1" and \
        f.get("remap_exists") == "1" and f.get("loaded_cls") not in (None, "<null>")


def engine_id_to_text(proj, uid):
    out, _ = run([GODOT, "--headless", "--path", str(proj), "--script",
                  "res://m3_uid.gd", "--", "--id=%d" % uid], cwd=ROOT)
    for ln in out.splitlines():
        if ln.startswith("M3UID id_to_text="):
            return ln.split("=", 1)[1]
    return None


def engine_content(proj):
    out, _ = run([GODOT, "--headless", "--path", str(proj), "--script",
                  "res://m3_content.gd"], cwd=ROOT)
    for ln in out.splitlines():
        if ln.startswith("M3CONTENT "):
            return ln
    return None


def read_import(proj):
    text = (proj / (PNG_FILE + ".import")).read_text()
    uid_text, dest = "", ""
    for ln in text.splitlines():
        if ln.startswith("uid="):
            uid_text = ln.split("=", 1)[1].strip().strip('"')
        elif ln.startswith("path="):
            dest = ln.split("=", 1)[1].strip().strip('"').split("/")[-1]
    return uid_text, dest


def cache_entries(path):
    data = path.read_bytes()
    n = struct.unpack("<I", data[:4])[0]
    off, ents = 4, []
    for _ in range(n):
        idv = struct.unpack("<q", data[off:off + 8])[0]
        off += 8
        ln = struct.unpack("<I", data[off:off + 4])[0]
        off += 4
        ents.append((idv, data[off:off + ln].decode()))
        off += ln
    return ents


def write_cache(path, ents):
    path.write_bytes(struct.pack("<I", len(ents)) + b"".join(
        struct.pack("<q", i) + struct.pack("<I", len(p.encode())) + p.encode()
        for i, p in ents))


def forge_cache_uid(proj, new_id):
    cache = proj / ".godot" / "uid_cache.bin"
    if not cache.exists():
        return False
    write_cache(cache, [(new_id if p == PNG else i, p)
                        for i, p in cache_entries(cache)])
    return True


def set_import_uid(proj, new_uid_text):
    imp = proj / (PNG_FILE + ".import")
    out = []
    for ln in imp.read_text().splitlines():
        out.append('uid="%s"' % new_uid_text if ln.startswith("uid=") else ln)
    imp.write_text("\n".join(out) + "\n")


def retarget_import(proj, dest_basename):
    imp = proj / (PNG_FILE + ".import")
    out = []
    for ln in imp.read_text().splitlines():
        if ln.startswith("path="):
            out.append('path="res://.godot/imported/%s"' % dest_basename)
        elif ln.startswith("dest_files="):
            out.append('dest_files=["res://.godot/imported/%s"]' % dest_basename)
        else:
            out.append(ln)
    imp.write_text("\n".join(out) + "\n")


def disk_clauses(proj, lines):
    uid_text, dest = read_import(proj)
    cache = proj / ".godot" / "uid_cache.bin"
    cache_uid = None
    if cache.exists():
        for i, p in cache_entries(cache):
            if p == PNG:
                cache_uid = i
    canonical = engine_id_to_text(proj, cache_uid) if cache_uid is not None else None
    f = fields_of(lines)
    return {
        "remap_is_declared_dest": f.get("path_line", "").endswith(dest + '"'),
        "remap_is_md5_name": dest == ANCHOR_CTEX,
        "import_uid_matches_cache": canonical is not None and uid_text == canonical,
    }


def w07_sequence(proj):
    run([GODOT, "--headless", "--path", str(proj), "--script",
         "res://%s" % W07, "--", "--arm=mkpng"], cwd=ROOT)
    run([GODOT, "--headless", "--path", str(proj), "--import"],
        timeout=IMPORT_TIMEOUT, cwd=ROOT)
    out, rec = run([GODOT, "--headless", "--path", str(proj), "--script",
                    "res://%s" % W07, "--", "--arm=importremap"], cwd=ROOT)
    return w07_receipt(out), rec


def phase2():
    proj = stage("p2base")
    pin, _ = w07_sequence(proj)
    if len(pin) != 2:
        print("M3P2 ABORT genuine lines=%d" % len(pin))
        return None
    for ln in pin:
        print("M3P2 genuine| " + ln)
    a_ok = all(static_anchors(pin).values()) and \
        all(disk_clauses(proj, pin).values())
    print("M3P2 genuine naive=%s anchored=%s content=%s"
          % (naive_of(pin), a_ok, engine_content(proj)))
    verdicts["p2"] = {"genuine": {"naive": naive_of(pin), "anchored": a_ok,
                                  "lines": pin, "content": engine_content(proj)},
                      "forgeries": {}}

    def measure(label, prep):
        p = stage(label)
        run([GODOT, "--headless", "--path", str(p), "--script",
             "res://%s" % W07, "--", "--arm=mkpng"], cwd=ROOT)
        run([GODOT, "--headless", "--path", str(p), "--import"],
            timeout=IMPORT_TIMEOUT, cwd=ROOT)
        prep(p)
        out, rec = run([GODOT, "--headless", "--path", str(p), "--script",
                        "res://%s" % W07, "--", "--arm=importremap"], cwd=ROOT)
        lines = w07_receipt(out)
        anchors = all(static_anchors(lines).values()) and \
            all(disk_clauses(p, lines).values())
        real, _ = run([GODOT, "--headless", "--path", str(p), "--script",
                       "res://%s" % W07, "--", "--arm=importremap"], cwd=ROOT)
        verdicts["p2"]["forgeries"][label] = {
            "naive": naive_of(lines), "anchored": anchors and w07_receipt(real) == lines,
            "bytes": rec["bytes"], "sha256": rec["sha256"],
            "disk": disk_clauses(p, lines), "lines": lines,
            "content": engine_content(p)}
        v = verdicts["p2"]["forgeries"][label]
        print("M3P2 %-20s naive=%-5s anchored=%-5s disk=%s"
              % (label, v["naive"], v["anchored"], json.dumps(v["disk"])))

    def f2(p):
        set_import_uid(p, "uid://bqk3m5n7qar1")
        (p / ".godot" / "uid_cache.bin").unlink(missing_ok=True)

    def f4(p):
        forge_cache_uid(p, FORGED_ID)
        set_import_uid(p, engine_id_to_text(p, FORGED_ID))

    def f7(p):
        (p / "w07_other.png").write_bytes((p / PNG_FILE).read_bytes())
        run([GODOT, "--headless", "--path", str(p), "--import"],
            timeout=IMPORT_TIMEOUT, cwd=ROOT)
        dest = ""
        for ln in (p / "w07_other.png.import").read_text().splitlines():
            if ln.startswith("path="):
                dest = ln.split("/")[-1].strip().strip('"')
        retarget_import(p, dest)

    measure("F1_import_uid_only", lambda p: set_import_uid(p, "uid://bqk3m5n7qar1"))
    measure("F2_import_uid_nocache", f2)
    measure("F3_cache_uid_only", lambda p: forge_cache_uid(p, FORGED_ID))
    measure("F4_consistent_forge", f4)
    measure("F5_dest_retarget",
            lambda p: retarget_import(p, PNG_FILE
                                      + "-deadbeefdeadbeefdeadbeefdeadbeef.ctex"))
    measure("F7_swap_real_ctex", f7)

    p = stage("F6_forger")
    (p / "m3_forger.gd").write_text(
        "extends SceneTree\nfunc _init() -> void:\n"
        + "".join('\tprint(%s)\n' % json.dumps(ln) for ln in pin)
        + "\tquit(0)\n")
    out, rec = run([GODOT, "--headless", "--path", str(p), "--script",
                    "res://m3_forger.gd"], cwd=ROOT)
    lines = w07_receipt(out)
    real, _ = run([GODOT, "--headless", "--path", str(p), "--script",
                   "res://%s" % W07, "--", "--arm=importremap"], cwd=ROOT)
    verdicts["p2"]["forgeries"]["F6_forger_echo"] = {
        "naive": naive_of(lines), "anchored": w07_receipt(real) == pin,
        "bytes": rec["bytes"], "sha256": rec["sha256"], "disk": {},
        "lines": lines, "recompute_lines": w07_receipt(real),
        "content": engine_content(p)}
    print("M3P2 %-20s naive=%-5s anchored=%-5s" % (
        "F6_forger_echo", naive_of(lines),
        verdicts["p2"]["forgeries"]["F6_forger_echo"]["anchored"]))
    verdicts["p2"]["naive_survivors"] = sorted(
        k for k, v in verdicts["p2"]["forgeries"].items() if v["naive"])
    print("M3P2 naive_survivors=%s" % verdicts["p2"]["naive_survivors"])
    return proj


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)
    if not (FIXTURES / S03).exists():
        print("MUT03 E3 fixture %s missing" % S03)
        return 2
    phase1()
    phase2()
    verdicts["killed_p1"] = verdicts["p1"]["all_neutralized"]
    verdicts["killed_p2_anchored"] = all(
        not v["anchored"] for v in verdicts["p2"]["forgeries"].values())
    out = ROOT / "mut03_verdicts.json"
    out.write_text(json.dumps({
        "fixtures": {S03: sha256_file(FIXTURES / S03),
                     W07: sha256_file(FIXTURES / W07)},
        "runs": runs, "verdicts": verdicts}, indent=2))
    print("MUT03 killed_p1=%s killed_p2_anchored=%s p2_naive_survivors=%s"
          % (verdicts["killed_p1"], verdicts["killed_p2_anchored"],
             verdicts["p2"]["naive_survivors"]))
    print("MUT03 verdicts_json=%s bytes=%d sha256=%s"
          % (out, out.stat().st_size, sha256_file(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
