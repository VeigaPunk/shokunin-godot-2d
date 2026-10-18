#!/usr/bin/env python3
"""r102 V3 seat — s04/s05 probe driver (filter glob case semantics + preset feature parsing).

Rerunnable receipt generator for reports/round-102/r102-ver3.md.
Never invokes corpus/fixtures/run_battery.py; never writes inside the repo
except nothing (receipts go under --root). Exports run under
`unshare -m --map-root-user` with a private tmpfs /tmp (r101 E0 F1: the 4.7.2
packer writes a fixed /tmp/tmpproject.binary path and silently stores a 0-byte
project.binary when that write hits EDQUOT).

Usage:
  python3 ver3_export_probe.py --root /var/tmp/r102-ver3 [--only-f NAME] [--only-g NAME]

Phases:
  F (s04): one project, 8 presets varying include/exclude filter case/wildcards;
           each exported via `godot --headless --path <proj> --export-pack`.
  G (s05): one project with feature-tagged settings overrides; exported once per
           custom_features variant; project.binary bytes scanned; two packs booted
           via the editor binary with --main-pack to read back resolved settings.
"""

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import time

RECEIPTS = {}
LOG = []


def say(msg):
    LOG.append(msg)
    print(msg, flush=True)


def q(s):
    return "'" + s.replace("'", "'\\''") + "'"


# ---------------------------------------------------------------- pck parsing

def parse_pck(path):
    with open(path, "rb") as fh:
        b = fh.read()
    out = {"bytes": len(b), "entries": {}}
    if len(b) < 0x28 or b[0:4] != b"GDPC":
        out["error"] = "bad_magic:" + repr(b[0:4])
        return out, b
    out["pack_version"] = struct.unpack_from("<I", b, 4)[0]
    out["ver"] = struct.unpack_from("<III", b, 8)
    base = struct.unpack_from("<Q", b, 0x18)[0]
    dir_off = struct.unpack_from("<Q", b, 0x20)[0]
    out["file_base"] = base
    out["dir_offset"] = dir_off
    if dir_off + 4 > len(b):
        out["error"] = "dir_off_oob"
        return out, b
    count = struct.unpack_from("<I", b, dir_off)[0]
    out["count"] = count
    off = dir_off + 4
    for _ in range(count):
        if off + 4 > len(b):
            out["error"] = "entry_off_oob"
            return out, b
        plen = struct.unpack_from("<I", b, off)[0]
        off += 4
        raw = b[off:off + plen]
        off += plen
        off = (off + 3) & ~3
        name = raw.split(b"\x00", 1)[0].decode("utf-8", "replace")
        foff, size = struct.unpack_from("<QQ", b, off)
        flags = struct.unpack_from("<I", b, off + 32)[0]
        off += 36
        out["entries"][name] = {"offset": foff, "size": size, "flags": flags}
    return out, b


def entry_bytes(raw, parsed, name):
    e = parsed["entries"].get(name)
    if e is None:
        return None
    st = parsed["file_base"] + e["offset"]
    return raw[st:st + e["size"]]


def scan_markers(b, needles, max_ctx=4):
    res = {}
    for n in needles:
        nb = n.encode()
        offs = []
        i = b.find(nb)
        while i != -1:
            offs.append(i)
            i = b.find(nb, i + 1)
        ctx = []
        for o in offs[:max_ctx]:
            ctx.append({"off": o, "ctx": repr(b[max(0, o - 24):o + len(nb) + 32])})
        res[n] = {"count": len(offs), "ctx": ctx}
    return res


# ------------------------------------------------------------------- shell

def run_shell(body, log_path, timeout, unshare):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if unshare:
        cmd = ["unshare", "-m", "--map-root-user", "/usr/bin/sh", "-c",
               "mount -t tmpfs -o size=512M tmpfs /tmp || exit 97\n" + body]
    else:
        cmd = ["/usr/bin/sh", "-c", body]
    t0 = time.time()
    with open(log_path, "wb") as lf:
        try:
            r = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, timeout=timeout)
            code = r.returncode
        except subprocess.TimeoutExpired:
            code = "TIMEOUT"
    dt = round(time.time() - t0, 2)
    tail = ""
    try:
        with open(log_path, "rb") as fh:
            data = fh.read()
        lines = data.split(b"\n")
        tail = "\n".join(l.decode("utf-8", "replace") for l in lines[-8:] if l.strip())
    except OSError:
        pass
    return {"exit": code, "secs": dt, "log": log_path, "tail": tail}


def tail_lines(path, n=25):
    try:
        with open(path, "rb") as fh:
            data = fh.read()
        return [l.decode("utf-8", "replace") for l in data.split(b"\n") if l.strip()][-n:]
    except OSError:
        return []


# ------------------------------------------------------------------ builders

def wtext(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def wbytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)


MAT_TRES = '[gd_resource type="Resource" format=3]\n\n[resource]\nmetadata/note="v3"\n'

F_FILES = {
    "case/lower.txt": "lower\n",
    "case/UPPER.txt": "UPPER\n",
    "case/MiXeD.txt": "MiXeD\n",
    "case/sub/inner.txt": "inner\n",
}

# (preset name, include_filter, exclude_filter)
F_PRESETS = [
    ("F_ctl", "case/lower.txt", ""),
    ("F_dir", "CASE/lower.txt", ""),
    ("F_file", "case/LOWER.txt", ""),
    ("F_mix", "case/mixed.txt", ""),
    ("F_star", "case/*", ""),
    ("F_qmark", "case/l?wer.txt", ""),
    ("F_xcase", "case/*", "case/upper.txt"),
    ("F_xcase2", "case/*", "CASE/*.TXT"),
    ("F_extup", "case/*.TXT", ""),
    ("F_upperdir", "CASE/*", ""),
    ("F_resurl", "res://case/lower.txt", ""),
]

CASE_FILES = sorted(F_FILES.keys())

G_MAIN_GD = """extends Node

func _ready() -> void:
	print("V3RUNTIME name=", ProjectSettings.get_setting("application/config/name", "<unset>"))
	print("V3RUNTIME name_ovr=", ProjectSettings.get_setting_with_override("application/config/name"))
	print("V3RUNTIME desc_ovr=", ProjectSettings.get_setting_with_override("application/config/description"))
	print("V3RUNTIME version_ovr=", ProjectSettings.get_setting_with_override("application/config/version"))
	print("V3RUNTIME has_zzfeat=", OS.has_feature("zzfeat"))
	print("V3RUNTIME has_zzother=", OS.has_feature("zzother"))
	print("V3RUNTIME has_spzzother=", OS.has_feature(" zzother"))
	print("V3RUNTIME has_ZZFEAT=", OS.has_feature("ZZFEAT"))
	print("V3RUNTIME has_zzthird=", OS.has_feature("zzthird"))
	print("V3RUNTIME has_47=", OS.has_feature("4.7"))
	print("V3RUNTIME has_48=", OS.has_feature("4.8"))
	print("V3RUNTIME features_setting=", ProjectSettings.get_setting("application/config/features", "<unset>"))
	print("V3RUNTIME has_editor=", OS.has_feature("editor"))
	print("V3RUNTIME has_linux=", OS.has_feature("linux"))
	get_tree().quit(0)
"""

G_MAIN_TSCN = ('[gd_scene load_steps=2 format=3]\n\n'
               '[ext_resource type="Script" path="res://main.gd" id="1"]\n\n'
               '[node name="Main" type="Node"]\nscript = ExtResource("1")\n')

G_MARKERS = ["V3Base", "V3Feat", "BASE_DESC", "DESC_OTHER", "0.0.0", "9.9.9",
             "zzfeat", "zzother", "zzthird", "ZZFEAT", "application/config/name"]

# (variant, custom_features, extra option overrides, project feature array or None)
G_VARIANTS = [
    ("G_base", "", {}, None),
    ("G_feat", "zzfeat", {}, None),
    ("G_comma", "zzfeat,zzother", {}, None),
    ("G_spcomma", "zzfeat, zzother", {}, None),
    ("G_spacesep", "zzfeat zzother", {}, None),
    ("G_double", "zzfeat,,zzother", {}, None),
    ("G_case", "ZZFEAT", {}, None),
    ("G_trail", "zzfeat,", {}, None),
    ("G_pfeat", "", {}, ["4.7", "zzthird"]),
    ("G_unknown", "zzfeat", {"ver3/unknown": "zzz"}, None),
    ("G_arch", "zzfeat", {"binary_format/architecture": "mips"}, None),
    ("G_verfeat", "", {}, ["4.8", "zzthird"]),
    ("G_normfeat", " , zzfeat ,, zzother ,", {}, None),
]


def preset_block(i, name, include, exclude, custom, options):
    lines = [f"[preset.{i}]", f'name="{name}"', 'platform="Linux/X11"',
             "runnable=true", "advanced_options=false", "dedicated_server=false",
             f'custom_features="{custom}"', 'export_filter="all_resources"',
             f'include_filter="{include}"', f'exclude_filter="{exclude}"',
             'export_path=""', "", f"[preset.{i}.options]"]
    for k, v in options.items():
        lines.append(f'{k}="{v}"')
    return "\n".join(lines) + "\n\n"


def build_f(root):
    proj = os.path.join(root, "f", "proj")
    wtext(os.path.join(proj, "project.godot"),
          'config_version=5\n\n[application]\nconfig/name="V3F"\n'
          'config/features=PackedStringArray("4.7")\n')
    for rel, content in F_FILES.items():
        wtext(os.path.join(proj, rel), content)
    wtext(os.path.join(proj, "res/mat.tres"), MAT_TRES)
    blocks = [preset_block(i, n, inc, exc, "", {"binary_format/architecture": "x86_64"})
              for i, (n, inc, exc) in enumerate(F_PRESETS)]
    wtext(os.path.join(proj, "export_presets.cfg"), "".join(blocks))
    os.makedirs(os.path.join(root, "f", "out"), exist_ok=True)
    return proj


def build_g(root, project_features):
    proj = os.path.join(root, "g", "proj")
    feats = 'config/features=PackedStringArray("4.7")'
    if project_features:
        feats = ("config/features=PackedStringArray(%s)"
                 % ", ".join('"%s"' % f for f in project_features))
    wtext(os.path.join(proj, "project.godot"),
          'config_version=5\n\n[application]\nconfig/name="V3Base"\n'
          'config/description="BASE_DESC"\nconfig/version="0.0.0"\n'
          'config/name.zzfeat="V3Feat"\n'
          'config/description.zzother="DESC_OTHER"\n'
          'config/version.zzthird="9.9.9"\n'
          'run/main_scene="res://main.tscn"\n' + feats + "\n\n"
          '[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n')
    wtext(os.path.join(proj, "main.gd"), G_MAIN_GD)
    wtext(os.path.join(proj, "main.tscn"), G_MAIN_TSCN)
    os.makedirs(os.path.join(root, "g", "out"), exist_ok=True)
    return proj


def write_g_preset(proj, custom, extra):
    options = {"binary_format/architecture": "x86_64"}
    options.update(extra)
    wtext(os.path.join(proj, "export_presets.cfg"),
          preset_block(0, "Linux/X11", "", "", custom, options))


# ------------------------------------------------------------------- phases

def phase_f(root, godot, unshare, only=None):
    proj = build_f(root)
    out_dir = os.path.join(root, "f", "out")
    logs = os.path.join(root, "f", "logs")
    res = {"proj": proj, "exports": {}}

    imp = run_shell(f"exec {q(godot)} --headless --path {q(proj)} --import",
                    os.path.join(logs, "import.log"), 120, unshare)
    res["import"] = imp
    say(f"V3_F import exit={imp['exit']} secs={imp['secs']}")

    for name, inc, exc in F_PRESETS:
        if only and name not in only.split(","):
            continue
        pck = os.path.join(out_dir, name + ".pck")
        if os.path.exists(pck):
            os.remove(pck)
        r = run_shell(f"cd {q(proj)}\nexec {q(godot)} --headless --path {q(proj)} "
                      f"--export-pack {q(name)} {q(pck)}",
                      os.path.join(logs, name + ".log"), 150, unshare)
        row = {"exit": r["exit"], "secs": r["secs"], "log_tail": r["tail"]}
        if os.path.exists(pck):
            parsed, raw = parse_pck(pck)
            row["pck_bytes"] = parsed.get("bytes")
            row["pck_error"] = parsed.get("error")
            row["entries"] = sorted(parsed["entries"].keys())
            row["case_hits"] = {f: (f in parsed["entries"]) for f in CASE_FILES}
            row["tres_in"] = "res/mat.tres" in parsed["entries"]
        else:
            row["pck_missing"] = True
        res["exports"][name] = row
        say(f"V3_F {name} inc={inc!r} exc={exc!r} exit={r['exit']} "
            f"entries={len(row.get('entries', []))} case_hits={row.get('case_hits')}")

    # same-preset re-export determinism spot check
    if only is None:
        pck2 = os.path.join(out_dir, "F_ctl_b.pck")
        r = run_shell(f"cd {q(proj)}\nexec {q(godot)} --headless --path {q(proj)} "
                      f"--export-pack {q('F_ctl')} {q(pck2)}",
                      os.path.join(logs, "F_ctl_b.log"), 150, unshare)
        a = os.path.join(out_dir, "F_ctl.pck")
        cmp_row = {"exit": r["exit"]}
        if os.path.exists(a) and os.path.exists(pck2):
            pa, ra = parse_pck(a)
            pb, rb = parse_pck(pck2)
            cmp_row["entries_equal"] = sorted(pa["entries"]) == sorted(pb["entries"])
            cmp_row["bytes_a"], cmp_row["bytes_b"] = pa["bytes"], pb["bytes"]
            cmp_row["byte_equal"] = ra == rb
        res["reexport_F_ctl"] = cmp_row
        say(f"V3_F reexport {cmp_row}")
    return res


def phase_g(root, godot, unshare, only=None):
    proj = build_g(root, None)
    out_dir = os.path.join(root, "g", "out")
    logs = os.path.join(root, "g", "logs")
    res = {"proj": proj, "variants": {}}

    write_g_preset(proj, "", {})
    imp = run_shell(f"exec {q(godot)} --headless --path {q(proj)} --import",
                    os.path.join(logs, "import.log"), 120, unshare)
    res["import"] = imp
    say(f"V3_G import exit={imp['exit']} secs={imp['secs']}")

    for name, custom, extra, pfeat in G_VARIANTS:
        if only and name not in only.split(","):
            continue
        if pfeat is not None:
            proj = build_g(root, pfeat)
        else:
            proj = build_g(root, None)
        write_g_preset(proj, custom, extra)
        pck = os.path.join(out_dir, name + ".pck")
        if os.path.exists(pck):
            os.remove(pck)
        r = run_shell(f"cd {q(proj)}\nexec {q(godot)} --headless --path {q(proj)} "
                      f"--export-pack {q('Linux/X11')} {q(pck)}",
                      os.path.join(logs, name + ".log"), 150, unshare)
        row = {"exit": r["exit"], "secs": r["secs"], "custom_features": custom,
               "extra_options": extra, "project_features": pfeat}
        if os.path.exists(pck):
            parsed, raw = parse_pck(pck)
            row["pck_bytes"] = parsed.get("bytes")
            row["pck_error"] = parsed.get("error")
            pb = entry_bytes(raw, parsed, "project.binary")
            if pb is not None:
                row["pbin_size"] = len(pb)
                row["pbin_magic"] = pb[:4].decode("latin1")
                row["markers"] = scan_markers(pb, G_MARKERS)
        else:
            row["pck_missing"] = True
            row["log_tail_lines"] = tail_lines(r["log"], 25)
        res["variants"][name] = row
        mk = row.get("markers", {})
        say(f"V3_G {name} custom={custom!r} exit={r['exit']} "
            f"pbin={row.get('pbin_size')} "
            f"V3Feat={mk.get('V3Feat', {}).get('count')} "
            f"V3Base={mk.get('V3Base', {}).get('count')} "
            f"desc_other={mk.get('DESC_OTHER', {}).get('count')} "
            f"v999={mk.get('9.9.9', {}).get('count')} "
            f"zzfeat={mk.get('zzfeat', {}).get('count')} "
            f"zzthird={mk.get('zzthird', {}).get('count')}")

    # runtime boots (no unshare: matches r101 E0 pack-run practice)
    boots = {}
    for name in ("G_base", "G_feat", "G_pfeat", "G_case", "G_comma",
                 "G_spcomma", "G_spacesep", "G_double", "G_trail",
                 "G_verfeat", "G_normfeat"):
        if only and name not in only.split(","):
            continue
        pck = os.path.join(out_dir, name + ".pck")
        if not os.path.exists(pck):
            continue
        r = run_shell(f"cd /\nexec {q(godot)} --headless --main-pack {q(pck)} --quit-after 5",
                      os.path.join(logs, f"boot_{name}.log"), 90, False)
        boot = {"exit": r["exit"], "secs": r["secs"]}
        got = [ln.strip() for ln in tail_lines(r["log"], 200) if "V3RUNTIME" in ln]
        boot["runtime_lines"] = got
        boots[name] = boot
        say(f"V3_G boot {name} exit={r['exit']} lines={got}")
    res["boots"] = boots
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/var/tmp/r102-ver3")
    ap.add_argument("--godot", default=shutil.which("godot") or "/usr/bin/godot")
    ap.add_argument("--only-f", default=None)
    ap.add_argument("--only-g", default=None)
    args = ap.parse_args()

    os.makedirs(args.root, exist_ok=True)
    RECEIPTS["godot"] = args.godot
    RECEIPTS["godot_version"] = subprocess.run(
        [args.godot, "--version"], capture_output=True, text=True).stdout.strip()
    RECEIPTS["started_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    unshare = subprocess.run(
        ["unshare", "-m", "--map-root-user", "/usr/bin/sh", "-c",
         "mount -t tmpfs -o size=16M tmpfs /tmp && test -w /tmp"],
        capture_output=True).returncode == 0
    RECEIPTS["unshare_private_tmp"] = unshare
    say(f"V3 godot={RECEIPTS['godot_version']} unshare={unshare} root={args.root}")

    if args.only_f != "SKIP":
        RECEIPTS["f"] = phase_f(args.root, args.godot, unshare, args.only_f or None)
        with open(os.path.join(args.root, "receipts.json"), "w") as fh:
            json.dump(RECEIPTS, fh, indent=1, sort_keys=True)
    if args.only_g != "SKIP":
        RECEIPTS["g"] = phase_g(args.root, args.godot, unshare, args.only_g or None)
        with open(os.path.join(args.root, "receipts.json"), "w") as fh:
            json.dump(RECEIPTS, fh, indent=1, sort_keys=True)

    RECEIPTS["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(args.root, "receipts.json"), "w") as fh:
        json.dump(RECEIPTS, fh, indent=1, sort_keys=True)
    with open(os.path.join(args.root, "receipts.txt"), "w") as fh:
        fh.write("\n".join(LOG) + "\n")
    say("V3 done; receipts: " + os.path.join(args.root, "receipts.json"))


if __name__ == "__main__":
    main()
