#!/usr/bin/env python3
"""mut01_launch.py -- r102 M1: embedded-binary forgery attack on the C1
export_launch rows.

Threat model: a row pins "the embedded (embed_pck=true) export is a
self-contained binary that, when executed with --quit-after N, exits 0 and
prints the launch marker".  If the row's only evidence is rc=0 + marker, then
a *script wrapper* placed at the pinned path -- one that merely prints the
marker -- is accepted.  The row must additionally check that the artifact is
a real ELF and that its size is consistent with a self-contained export
(template + appended pack).  This script measures, on the actual host:

  real  : godot --headless --export-debug <Linux/X11 embed_pck=true preset>
          -> self-contained ELF; launch it and capture rc/marker/frames.
  sh    : /bin/sh wrapper printing the marker        (tiny, non-ELF)
  py    : python3 wrapper printing the marker        (tiny, non-ELF)
  elf   : compiled C stub printing the marker        (real ELF, tiny)  [gcc]
  bigsh : sh wrapper padded past the template size   (non-ELF, big)

and then applies each check class to every artifact:

  naive  = rc==0 and marker appears exactly once          (marker-only row)
  elf    = first 4 bytes are \\x7fELF
  size   = st_size >= stock template size (self-contained lower bound)
  strong = naive and elf and size

Expected discrimination (gated by --expect reject, the default):
  real  -> strong ACCEPT
  sh,py -> naive ACCEPT, elf REJECT, size REJECT
  elf   -> naive ACCEPT, elf ACCEPT, size REJECT   (size is load-bearing)
  bigsh -> naive ACCEPT, elf REJECT, size ACCEPT   (magic is load-bearing)
  every forgery -> strong REJECT

Everything runs under --root (default /var/tmp/r102-mut1); the repo is never
written.  run_battery.py is never executed (hard rule).  Optional --fixture
runs one landed corpus/fixtures/export_launch*.gd in a scratch project and
scans it statically for ELF/size checks (best effort, not gated).

Exit code: 0 iff RESULT: PASS.
"""

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DEFAULT_MARKER = "EXPORT_LAUNCH_READY scene=fixture"
TEMPLATE_REL = Path("godot/export_templates")

PROJECT_GODOT = """[application]
config/name="M1LaunchForge"
config/features=PackedStringArray("4.7")
run/main_scene="res://main.tscn"
"""

MAIN_GD = """extends Node

var frame := 0

func _process(_delta: float) -> void:
\tframe += 1
\tprint("M1_FRAME %d" % frame)
\tif frame == 1:
\t\tprint("__MARKER__")
"""

MAIN_TSCN = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://main.gd" id="1"]

[node name="Main" type="Node"]
script = ExtResource("1")
"""

PRESETS = """[preset.0]
name="Linux/X11"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""

[preset.0.options]
binary_format/architecture="x86_64"
binary_format/embed_pck=true

[preset.1]
name="Linux/X11 Plain"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""

[preset.1.options]
binary_format/architecture="x86_64"
binary_format/embed_pck=false
"""

C_STUB = r"""#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    int headless = 0;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--headless") == 0) headless = 1;
    }
    if (!headless) return 3;
    printf("M1_FRAME 1\n__MARKER__\n");
    for (int f = 2; f <= 5; f++) printf("M1_FRAME %d\n", f);
    return 0;
}
"""


def now():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_if(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def tmp_probe():
    """4096-byte write+readback at the packer's fixed /tmp sink."""
    p = Path("/tmp/.r102-mut1-probe")
    data = b"r102mut1!" * 512
    try:
        p.write_bytes(data)
        ok = p.read_bytes() == data
    except OSError as exc:
        return False, f"{type(exc).__name__}: {exc}"
    finally:
        try:
            p.unlink()
        except OSError:
            pass
    return ok, "ok" if ok else "short/mismatched readback"


def run(cmd, timeout, cwd=None, env=None):
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True,
                              text=True, errors="replace", timeout=timeout)
        return {"command": cmd, "rc": proc.returncode,
                "stdout": proc.stdout, "stderr": proc.stderr,
                "error": None, "elapsed": round(time.monotonic() - started, 2)}
    except subprocess.TimeoutExpired as exc:
        def dec(x):
            if x is None:
                return ""
            return x.decode(errors="replace") if isinstance(x, bytes) else x
        return {"command": cmd, "rc": None,
                "stdout": dec(exc.stdout), "stderr": dec(exc.stderr),
                "error": f"TIMEOUT after {timeout}s",
                "elapsed": round(time.monotonic() - started, 2)}
    except OSError as exc:
        return {"command": cmd, "rc": None, "stdout": "", "stderr": "",
                "error": f"{type(exc).__name__}: {exc}",
                "elapsed": round(time.monotonic() - started, 2)}


def template_size(godot_version):
    """Size of the stock linux release/debug template used by the export."""
    parts = godot_version.split(".")
    tag = ".".join(parts[:4]) if len(parts) >= 4 else godot_version
    base = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    for name in ("linux_debug.x86_64", "linux_release.x86_64"):
        p = base / TEMPLATE_REL / tag / name
        if p.is_file():
            return p, p.stat().st_size
    return None, None


def export_command(godot, project, preset, preset_mode, out_path):
    return [godot, "--headless", "--path", str(project),
            f"--export-{preset_mode}", preset, str(out_path)]


def export_attempt(godot, project, preset, preset_mode, out_path, wrap_mode,
                   timeout):
    base = export_command(godot, project, preset, preset_mode, out_path)
    if wrap_mode == "unshare":
        inner = "mount -t tmpfs -o size=64M tmpfs /tmp && exec " + " ".join(
            shlex.quote(x) for x in base)
        cmd = ["unshare", "-m", "--map-root-user", "/usr/bin/sh", "-c", inner]
    else:
        cmd = base
    rec = run(cmd, timeout)
    rec["wrap_mode"] = wrap_mode
    rec["artifact_exists"] = out_path.is_file()
    rec["artifact_bytes"] = out_path.stat().st_size if out_path.is_file() else 0
    rec["savepack"] = "savepack" in rec["stdout"] + rec["stderr"]
    rec["done_marker"] = "[ DONE ]" in rec["stdout"] + rec["stderr"]
    rec["ok"] = (rec["rc"] == 0 and rec["artifact_exists"]
                 and rec["artifact_bytes"] > 0)
    return rec


def launch(artifact, frames, timeout):
    return run([str(artifact), "--headless", "--quit-after", str(frames)],
               timeout, cwd=str(artifact.parent))


def receipt(out, rc, marker):
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return {
        "rc_zero": rc == 0,
        "marker_count": sum(1 for ln in lines if ln == marker),
        "frames": [ln for ln in lines if ln.startswith("M1_FRAME ")],
        "frames_receipt": ("M1_FRAME 5" in lines and "M1_FRAME 6" not in lines),
        "error_lines": [ln for ln in lines
                        if ln.startswith(("ERROR:", "SCRIPT ERROR:", "Parse Error:"))],
    }


def file_facts(path, floor):
    data = path.read_bytes()
    head = data[:16]
    tail = data[-min(len(data), 4 << 20):]
    gdpc = tail.rfind(b"GDPC")
    return {
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "first16_hex": head.hex(),
        "first16_ascii": "".join(chr(b) if 32 <= b < 127 else "." for b in head),
        "elf_magic": head[:4] == b"\x7fELF",
        "size_ge_template": floor is not None and len(data) >= floor,
        "gdpc_offset_from_end": (len(data) - (len(data) - len(tail) + gdpc))
        if gdpc >= 0 else None,
        "gdpc_present_tail4m": gdpc >= 0,
    }


def make_forgeries(forge_dir, marker, floor, template_bytes_plain_pck, do_elf):
    forge_dir.mkdir(parents=True, exist_ok=True)
    m_single = marker.replace("'", "'\\''")
    sh = forge_dir / "forged-sh.x86_64"
    sh.write_text("#!/bin/sh\n"
                  "printf '%s\\n' 'M1_FRAME 1'\n"
                  f"printf '%s\\n' '{m_single}'\n"
                  "printf '%s\\n' 'M1_FRAME 2' 'M1_FRAME 3' 'M1_FRAME 4' 'M1_FRAME 5'\n"
                  "exit 0\n")
    sh.chmod(0o755)

    py = forge_dir / "forged-py.x86_64"
    py.write_text("#!/usr/bin/env python3\n"
                  "import sys\n"
                  "sys.stdout.write('M1_FRAME 1\\n" + marker.replace("'", "\\'")
                  + "\\n')\n"
                  "for f in (2, 3, 4, 5):\n"
                  "    sys.stdout.write('M1_FRAME %d\\n' % f)\n"
                  "raise SystemExit(0)\n")
    py.chmod(0o755)

    big = forge_dir / "forged-bigsh.x86_64"
    target = (floor if floor else 32 << 20) + 65536
    with open(big, "wb") as fh:
        fh.write(("#!/bin/sh\n"
                  "printf '%s\\n' 'M1_FRAME 1'\n"
                  f"printf '%s\\n' '{m_single}'\n"
                  "printf '%s\\n' 'M1_FRAME 2' 'M1_FRAME 3' 'M1_FRAME 4' 'M1_FRAME 5'\n"
                  "exit 0\n# ").encode())
        have = fh.tell()
        chunk = b"x" * (1 << 20)
        while have < target:
            n = min(len(chunk), target - have)
            fh.write(chunk[:n])
            have += n
    big.chmod(0o755)

    elf = None
    if do_elf:
        src = forge_dir / "forged_stub.c"
        src.write_text(C_STUB.replace(
            "__MARKER__",
            marker.replace("\\", "\\\\").replace('"', '\\"')))
        elf = forge_dir / "forged-elf.x86_64"
        cc = run(["gcc", "-O0", "-o", str(elf), str(src)], 60)
        if cc["rc"] != 0 or not elf.is_file():
            elf = None
        else:
            elf.chmod(0o755)
    return {"sh": sh, "py": py, "bigsh": big, "elf": elf}


def fixture_scan(repo, fixture_arg):
    found = []
    paths = []
    if fixture_arg:
        paths = [Path(fixture_arg)]
    else:
        paths = sorted((repo / "corpus" / "fixtures").glob("export_launch*.gd"))
    tokens = ["\\x7fELF", "\\x7f", "ELF", "st_size", "get_length",
              "file_size", "embed_pck", "binary_format", "size()"]
    for p in paths:
        if not p.is_file():
            continue
        text = p.read_text(errors="replace")
        lines = text.splitlines()
        hits = {t: [i + 1 for i, ln in enumerate(lines) if t in ln][:8]
                for t in tokens}
        found.append({"path": str(p), "bytes": p.stat().st_size,
                      "elf_check_tokens": {k: v for k, v in hits.items()
                                           if v and k in ("\\x7fELF", "\\x7f", "ELF")},
                      "size_check_tokens": {k: v for k, v in hits.items()
                                            if v and k in ("st_size", "get_length", "file_size", "size()")},
                      "embed_tokens": {k: v for k, v in hits.items()
                                       if v and k == "embed_pck"}})
    return found


def fixture_run(repo, fixture_arg, run_dir, godot, preset_mode, timeout):
    src = Path(fixture_arg)
    if not src.is_file():
        return {"error": f"fixture not found: {src}"}
    proj = run_dir / "fixture-project"
    write_if(proj / "project.godot", PROJECT_GODOT)
    write_if(proj / "main.gd", MAIN_GD.replace("__MARKER__", DEFAULT_MARKER))
    write_if(proj / "main.tscn", MAIN_TSCN)
    write_if(proj / "export_presets.cfg", PRESETS)
    shutil.copy2(src, proj / src.name)
    env = os.environ.copy()
    root = run_dir / "fixture-root"
    root.mkdir(parents=True, exist_ok=True)
    for var in ("EXPORT_LAUNCH_ROOT", "EXPORT_PROD_ROOT", "EXPORT_LAUNCH_SCRATCH"):
        env[var] = str(root)
    rec = run([godot, "--headless", "--path", str(proj), "--script",
               "res://" + src.name, "--"], timeout, env=env)
    lines = rec["stdout"].splitlines()
    rec["pass_lines"] = [ln for ln in lines if ln.strip().startswith("PASS")]
    rec["fail_lines"] = [ln for ln in lines if ln.strip().startswith("FAIL")]
    rec["exit"] = rec["rc"]
    return rec


# ---------------------------------------------------------------------------
# Dynamic fixture attack.  A scratch copy of a landed export_launch fixture
# gets one env-triggered substitution spliced in right after its export call:
# when EXPORT_LAUNCH_FORGE is set, the freshly exported binary is moved aside
# (.real) and the forged artifact is copied onto the pinned path.  The
# fixture's own checks then judge the forgery.  The repo fixture is never
# modified; if the anchor does not match exactly once the splice is refused.

FIXTURE_SPECS = {
    "export_launch.gd": {
        "arm": "embed",
        "marker": "EXPORT_LAUNCH_MAIN boot scene=main",
        "frame_prefix": "EXPORT_LAUNCH_FRAME ",
        "frames": 3,
        "anchor": '\tvar code := _export("embed", PRESET_EMBED, bin)',
        "var": "bin",
        "predicate": "emit-only",
    },
    "export_launch_s01.gd": {
        "arm": "embed",
        "marker": "EXPORT_LAUNCH_S01 boot embed",
        "frame_prefix": "EXPORT_LAUNCH_S01_FRAME ",
        "frames": 3,
        "anchor": '\tvar rel := _export(variant, "release", binary)',
        "var": "binary",
        "predicate": "explicit",
    },
    "export_launch_s02.gd": {
        "arm": "embed",
        "marker": "LAUNCH_S02_MARKER",
        "frame_prefix": "LAUNCH_S02_FRAME ",
        "frames": 5,
        "anchor": '\tvar code := _export("embed", exe)',
        "var": "exe",
        "predicate": "explicit",
    },
}

SPLICE_SNIPPET = (
    '\tif OS.get_environment("EXPORT_LAUNCH_FORGE") != "":\n'
    '\t\tvar _forge_src := OS.get_environment("EXPORT_LAUNCH_FORGE")\n'
    '\t\tDirAccess.copy_absolute(<V>, _forge_src + ".real")\n'
    '\t\tDirAccess.remove_absolute(<V>)\n'
    '\t\tDirAccess.copy_absolute(_forge_src, <V>)\n'
    '\t\tOS.execute("/usr/bin/chmod", PackedStringArray(["+x", <V>]))\n'
    '\t\t_diag("forged", _forge_src)\n')


def release_template(godot_version):
    parts = godot_version.split(".")
    tag = ".".join(parts[:4]) if len(parts) >= 4 else godot_version
    base = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    p = base / TEMPLATE_REL / tag / "linux_release.x86_64"
    return (p, p.stat().st_size) if p.is_file() else (None, None)


def c_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def write_shell_dialect(path, marker, frame_prefix, frames, trailer=None):
    text = ("#!/bin/sh\n"
            + "printf '%s\\n' '" + marker.replace("'", "'\\''") + "'\n"
            + "".join("printf '%s\\n' '" + frame_prefix + str(i) + "'\n"
                      for i in range(1, frames + 1))
            + "exit 0\n")
    data = text.encode()
    if trailer:
        tbytes, pbytes = trailer
        pad = tbytes - len(data)
        if pad < 0:
            raise ValueError("stub larger than template size")
        data = (data + b"x" * pad + b"GDPC" + b"x" * (pbytes - 4)
                + int(pbytes).to_bytes(8, "little") + b"GDPC")
    path.write_bytes(data)
    path.chmod(0o755)


def write_elf_stub(path, marker, frame_prefix, frames, trailer=None):
    src = path.with_name(path.name + ".c")
    lines = ["#include <stdio.h>", "int main(void) {"]
    lines.append('    printf("' + c_escape(marker) + '\\n");')
    for i in range(1, frames + 1):
        lines.append('    printf("' + c_escape(frame_prefix + str(i)) + '\\n");')
    lines += ["    return 0;", "}"]
    src.write_text("\n".join(lines) + "\n")
    cc = run(["gcc", "-O0", "-o", str(path), str(src)], 60)
    if cc["rc"] != 0 or not path.is_file():
        return None
    if trailer:
        tbytes, pbytes = trailer
        cur = path.stat().st_size
        if cur >= tbytes:
            return None
        with open(path, "ab") as fh:
            fh.write(b"\x00" * (tbytes - cur) + b"GDPC" + b"\x00" * (pbytes - 4)
                     + int(pbytes).to_bytes(8, "little") + b"GDPC")
    path.chmod(0o755)
    return path


def attack_fixture(repo, fixture_path, run_dir, godot, timeout):
    name = fixture_path.name
    spec = FIXTURE_SPECS[name]
    base_dir = run_dir / ("attack-" + name)
    proj = base_dir / "proj"
    write_if(proj / "project.godot",
             'config_version=5\n\n[application]\nconfig/name="Mut1Attack"\n'
             'config/features=PackedStringArray("4.7")\n')
    text = fixture_path.read_text(errors="replace")
    n = text.count(spec["anchor"])
    if n != 1 or "_diag(" not in text:
        return {"fixture": name, "error": f"splice refused: anchor_count={n}"}
    spliced = text.replace(spec["anchor"],
                           spec["anchor"] + "\n"
                           + SPLICE_SNIPPET.replace("<V>", spec["var"]))
    (proj / name).write_text(spliced)
    root = base_dir / "root"
    root.mkdir(parents=True, exist_ok=True)
    ver = run([godot, "--version"], 20)
    godot_version = ver["stdout"].strip().splitlines()[0] if ver["rc"] == 0 else "unknown"
    _, rel_bytes = release_template(godot_version)
    if not rel_bytes:
        return {"fixture": name, "error": "release template not found"}

    def run_case(forge):
        env = os.environ.copy()
        env["EXPORT_LAUNCH_ROOT"] = str(root)
        if forge:
            env["EXPORT_LAUNCH_FORGE"] = str(forge)
        else:
            env.pop("EXPORT_LAUNCH_FORGE", None)
        rec = run([godot, "--headless", "--path", str(proj), "--script",
                   "res://" + name, "--", "--arm=" + spec["arm"]], timeout, env=env)
        out = rec["stdout"] + rec["stderr"]
        rec["pass_lines"] = [ln.strip() for ln in out.splitlines()
                             if ln.strip().startswith("PASS export_launch")]
        rec["fail_lines"] = [ln.strip() for ln in out.splitlines()
                             if ln.strip().startswith("FAIL export_launch")]
        return rec

    forge_dir = base_dir / "forge"
    forge_dir.mkdir(parents=True, exist_ok=True)
    result = {"fixture": name, "arm": spec["arm"], "predicate": spec["predicate"],
              "spec_source_bytes": fixture_path.stat().st_size,
              "spec_source_sha256": sha256_file(fixture_path),
              "template": {"path": str(release_template(godot_version)[0]),
                           "bytes": rel_bytes},
              "artifacts": {}, "cases": {}}
    control = run_case(None)
    result["control"] = {"rc": control["rc"], "error": control["error"],
                         "pass_lines": control["pass_lines"],
                         "fail_lines": control["fail_lines"]}
    if spec["predicate"] == "explicit":
        result["control"]["classification"] = (
            "ACCEPT" if control["rc"] == 0 and control["pass_lines"]
            else "REJECT-OR-BROKEN")
    else:
        result["control"]["classification"] = (
            "ACCEPT" if control["pass_lines"] and not control["fail_lines"]
            else "REJECT-OR-BROKEN")
    # Match the genuine artifact's declared pack size so the forged wrapper is
    # byte-count-identical to the control export for this fixture/project.
    genuine_pack = 2036
    for ln in control["pass_lines"]:
        m = re.search(r"pack_bytes=(\d+)", ln)
        if m:
            genuine_pack = int(m.group(1))
        else:
            m = re.search(r"(?:binary_bytes|bin_bytes)=(\d+)", ln)
            if m:
                cand = int(m.group(1)) - rel_bytes - 12
                if cand > 0:
                    genuine_pack = cand
    result["control"]["genuine_pack_bytes_used"] = genuine_pack
    trailer = (rel_bytes, genuine_pack)

    artifacts = {}
    plain = forge_dir / "plain-sh.x86_64"
    write_shell_dialect(plain, spec["marker"], spec["frame_prefix"], spec["frames"])
    artifacts["plain_sh"] = plain
    crafted = forge_dir / "crafted-sh.x86_64"
    write_shell_dialect(crafted, spec["marker"], spec["frame_prefix"],
                        spec["frames"], trailer=trailer)
    artifacts["crafted_sh"] = crafted
    elf = forge_dir / "crafted-elf.x86_64"
    elf = write_elf_stub(elf, spec["marker"], spec["frame_prefix"],
                         spec["frames"], trailer=trailer)
    if elf:
        artifacts["crafted_elf"] = elf

    for arm, path in artifacts.items():
        facts = file_facts(path, rel_bytes)
        result["artifacts"][arm] = {
            "path": str(path), "bytes": facts["bytes"],
            "first16_hex": facts["first16_hex"],
            "first16_ascii": facts["first16_ascii"],
            "elf_magic": facts["elf_magic"],
            "size_ge_template": facts["size_ge_template"]}
        rec = run_case(path)
        case = {"rc": rec["rc"], "error": rec["error"],
                "fail_lines": rec["fail_lines"], "pass_lines": rec["pass_lines"],
                "artifact": {"bytes": facts["bytes"], "elf_magic": facts["elf_magic"]}}
        if spec["predicate"] == "explicit":
            if rec["rc"] == 1 and rec["fail_lines"]:
                case["classification"] = "REJECT"
            elif rec["rc"] == 0 and rec["pass_lines"]:
                case["classification"] = "ACCEPT"
            else:
                case["classification"] = "INCONCLUSIVE"
        else:
            if rec["fail_lines"]:
                case["classification"] = "REJECT"
            elif rec["pass_lines"] == control["pass_lines"]:
                case["classification"] = "ACCEPT"
            elif rec["pass_lines"]:
                diffs = []
                for a, b in zip(control["pass_lines"], rec["pass_lines"]):
                    if a != b:
                        diffs.append({"control": a, "forged": b})
                case["classification"] = "PIN-DEPENDENT"
                case["line_diffs"] = diffs
            else:
                case["classification"] = "INCONCLUSIVE"
        result["cases"][arm] = case
        print(f"mut01: ATTACK {name} {arm}: class={case['classification']} "
              f"rc={rec['rc']} elf_magic={facts['elf_magic']} "
              f"bytes={facts['bytes']}")
    print(f"mut01: ATTACK {name} control: class={result['control']['classification']} "
          f"rc={control['rc']} pass_lines={len(control['pass_lines'])}")
    return result


def attack_fixtures(repo, run_dir, godot, timeout):
    out = []
    fixtures = sorted((repo / "corpus" / "fixtures").glob("export_launch*.gd"))
    if not fixtures:
        print("mut01: ATTACK: no corpus/fixtures/export_launch*.gd landed; skipped")
        return out
    for path in fixtures:
        if spec_name(path) not in FIXTURE_SPECS:
            print(f"mut01: ATTACK {path.name}: no registry spec; skipped")
            out.append({"fixture": path.name, "error": "no registry spec"})
            continue
        out.append(attack_fixture(repo, path, run_dir, godot, timeout))
    return out


def spec_name(path):
    return path.name


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--root", default="/var/tmp/r102-mut1")
    ap.add_argument("--marker", default=DEFAULT_MARKER)
    ap.add_argument("--frames", type=int, default=5)
    ap.add_argument("--preset", default="Linux/X11")
    ap.add_argument("--preset-mode", default="debug", choices=["debug", "release"])
    ap.add_argument("--export-wrap", default="auto",
                    choices=["auto", "direct", "unshare"])
    ap.add_argument("--timeout-export", type=int, default=240)
    ap.add_argument("--timeout-launch", type=int, default=30)
    ap.add_argument("--expect", default="reject", choices=["reject", "accept"])
    ap.add_argument("--no-elf-arm", action="store_true")
    ap.add_argument("--fixture", default=None,
                    help="run/scan one landed export_launch fixture (best effort)")
    ap.add_argument("--no-attack", action="store_true",
                    help="skip the dynamic splice-attack on landed fixtures")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    started = now()
    run_dir = Path(args.root) / f"{started}-mut01"
    run_dir.mkdir(parents=True, exist_ok=True)
    ver = run([args.godot, "--version"], 20)
    godot_version = ver["stdout"].strip().splitlines()[0] if ver["rc"] == 0 else "unknown"
    template_path, template_bytes = template_size(godot_version)
    tmp_ok, tmp_detail = tmp_probe()

    print(f"mut01: godot={godot_version!r} rc={ver['rc']}")
    print(f"mut01: template={template_path} bytes={template_bytes}")
    print(f"mut01: /tmp probe ok={tmp_ok} ({tmp_detail})")
    print(f"mut01: scratch={run_dir}")

    project = run_dir / "project"
    write_if(project / "project.godot", PROJECT_GODOT)
    write_if(project / "main.gd", MAIN_GD.replace("__MARKER__", args.marker))
    write_if(project / "main.tscn", MAIN_TSCN)
    write_if(project / "export_presets.cfg", PRESETS)

    # ---- 1. plain (non-embed) export: stock template copy + real pck -----
    plain_dir = run_dir / "out-plain"
    plain_dir.mkdir()
    plain_bin = plain_dir / "plain.x86_64"
    modes = ["unshare", "direct"] if not tmp_ok else ["direct", "unshare"]
    if args.export_wrap != "auto":
        modes = [args.export_wrap]
    attempts = []
    plain_rec = None
    for mode in modes:
        rec = export_attempt(args.godot, project, "Linux/X11 Plain",
                             args.preset_mode, plain_bin, mode,
                             args.timeout_export)
        attempts.append(rec)
        if rec["ok"]:
            plain_rec = rec
            break
    plain_pck = plain_bin.with_suffix(".pck")
    plain = {"attempts": attempts, "artifact": None}
    if plain_rec:
        plain = {
            "artifact": file_facts(plain_bin, template_bytes),
            "pck_bytes": plain_pck.stat().st_size if plain_pck.is_file() else 0,
            "products": sorted(p.name for p in plain_dir.iterdir()),
            "ok": True,
        }
    else:
        plain = {"ok": False, "attempts": attempts}
    print(f"mut01: plain-export ok={plain.get('ok')} "
          f"bin_bytes={plain.get('artifact', {}).get('bytes')} "
          f"pck_bytes={plain.get('pck_bytes')}")

    # ---- 2. embedded export + real launch (control) ----------------------
    embed_dir = run_dir / "out-embed"
    embed_dir.mkdir()
    embed_bin = embed_dir / "embed.x86_64"
    embed_attempts = []
    real = {"ok": False}
    floor = template_bytes
    for mode in modes:
        rec = export_attempt(args.godot, project, args.preset,
                             args.preset_mode, embed_bin, mode,
                             args.timeout_export)
        embed_attempts.append(rec)
        if not rec["ok"]:
            continue
        launch_rec = launch(embed_bin, args.frames, args.timeout_launch)
        facts = file_facts(embed_bin, floor)
        rc = receipt(launch_rec["stdout"] + launch_rec["stderr"],
                     launch_rec["rc"], args.marker)
        corrupt = "Corrupted header in binary project.binary" in (
            launch_rec["stdout"] + launch_rec["stderr"])
        ok = (rc["rc_zero"] and rc["marker_count"] == 1
              and rc["frames_receipt"] and not corrupt)
        real = {"ok": ok, "export": rec, "launch": launch_rec,
                "receipt": rc, "artifact": facts,
                "pck_embedded_delta": (facts["bytes"] - template_bytes
                                       if template_bytes else None),
                "products": sorted(p.name for p in embed_dir.iterdir())}
        if ok:
            break
        print("mut01: embedded control failed; "
              f"corrupt_project_binary={corrupt} rc={launch_rec['rc']} "
              "retrying other /tmp mode")
    real_ok = real.get("ok", False)
    print(f"mut01: embed-export ok={real_ok} "
          f"artifact_bytes={real.get('artifact', {}).get('bytes')} "
          f"delta_vs_template={real.get('pck_embedded_delta')} "
          f"marker_count={real.get('receipt', {}).get('marker_count')}")

    # ---- 3. forgeries + launches ----------------------------------------
    pck_bytes = plain.get("pck_bytes") or 0
    forge_paths = make_forgeries(run_dir / "forge", args.marker, floor,
                                 pck_bytes, not args.no_elf_arm)
    artifacts = {}
    meta = {"real": ("real embedded export", real_ok, real),
            "sh": ("script wrapper (/bin/sh)", None, None),
            "py": ("script wrapper (python3)", None, None),
            "bigsh": ("script wrapper padded > template size", None, None),
            "elf": ("compiled ELF stub (magic ok, tiny)", None, None)}
    for name, path in forge_paths.items():
        if path is None:
            continue
        launch_rec = launch(path, args.frames, args.timeout_launch)
        out = launch_rec["stdout"] + launch_rec["stderr"]
        rc = receipt(out, launch_rec["rc"], args.marker)
        facts = file_facts(path, floor)
        verdict = {
            "naive_accept": rc["rc_zero"] and rc["marker_count"] == 1,
            "elf_ok": facts["elf_magic"],
            "size_ok": facts["size_ge_template"],
            "frames_receipt": rc["frames_receipt"],
        }
        verdict["strong_accept"] = (verdict["naive_accept"] and verdict["elf_ok"]
                                    and verdict["size_ok"])
        artifacts[name] = {"path": str(path), "artifact": facts,
                           "launch": launch_rec, "receipt": rc,
                           "checks": verdict,
                           "description": meta[name][0]}
        print(f"mut01: ARM {name}: naive_accept={verdict['naive_accept']} "
              f"elf_ok={verdict['elf_ok']} size_ok={verdict['size_ok']} "
              f"strong_accept={verdict['strong_accept']} "
              f"bytes={facts['bytes']} first16={facts['first16_hex']}")

    if real_ok:
        facts = real["artifact"]
        verdict = {
            "naive_accept": (real["receipt"]["rc_zero"]
                             and real["receipt"]["marker_count"] == 1),
            "elf_ok": facts["elf_magic"],
            "size_ok": facts["size_ge_template"],
            "frames_receipt": real["receipt"]["frames_receipt"],
        }
        verdict["strong_accept"] = (verdict["naive_accept"] and verdict["elf_ok"]
                                    and verdict["size_ok"])
        artifacts["real"] = {"path": str(embed_bin), "artifact": facts,
                             "launch": real["launch"], "receipt": real["receipt"],
                             "checks": verdict,
                             "size_ge_template_plus_pck": (
                                 facts["bytes"] >= (template_bytes or 0) + pck_bytes),
                             "description": meta["real"][0]}
        print(f"mut01: ARM real: naive_accept={verdict['naive_accept']} "
              f"elf_ok={verdict['elf_ok']} size_ok={verdict['size_ok']} "
              f"strong_accept={verdict['strong_accept']} "
              f"bytes={facts['bytes']} gdpc_tail={facts['gdpc_present_tail4m']}")

    # ---- 4. gate ---------------------------------------------------------
    forged = {k: v for k, v in artifacts.items() if k != "real"}
    forged_accepted = [k for k, v in forged.items()
                       if v["checks"]["strong_accept"]]
    forged_rejected = [k for k, v in forged.items()
                       if not v["checks"]["strong_accept"]]
    single_check_blind = {
        "elf_stub_only_size_rejects": (
            "elf" in forged and forged["elf"]["checks"]["elf_ok"]
            and not forged["elf"]["checks"]["size_ok"]),
        "bigsh_only_elf_rejects": (
            "bigsh" in forged and forged["bigsh"]["checks"]["size_ok"]
            and not forged["bigsh"]["checks"]["elf_ok"]),
        "script_wrappers_naive_accept_but_strong_reject": all(
            forged[k]["checks"]["naive_accept"]
            and not forged[k]["checks"]["strong_accept"]
            for k in ("sh", "py") if k in forged),
    }
    real_strong = artifacts.get("real", {}).get("checks", {}).get("strong_accept", False)
    observed_forged = "accept" if forged_accepted else "reject"
    expectation_met = (observed_forged == args.expect) and real_strong
    if args.expect == "reject":
        expectation_met = expectation_met and all(single_check_blind.values())
    print(f"mut01: forged artifacts: rejected={sorted(forged_rejected)} "
          f"accepted={sorted(forged_accepted)} real_strong_accept={real_strong}")
    print(f"mut01: single-check blind spots: {single_check_blind}")
    print(f"mut01: observed forged outcome={observed_forged} "
          f"expect={args.expect} -> {'met' if expectation_met else 'NOT met'}")

    # ---- 5. optional landed-fixture scan/run ----------------------------
    scan = fixture_scan(REPO, args.fixture)
    scan_paths = [s["path"] for s in scan]
    if scan_paths:
        for s in scan:
            print(f"mut01: FIXTURE {s['path']}: elf_tokens={s['elf_check_tokens']} "
                  f"size_tokens={s['size_check_tokens']} "
                  f"embed_tokens={s['embed_tokens']}")
    else:
        print("mut01: FIXTURE scan: no corpus/fixtures/export_launch*.gd landed at run time")
    fix_run = None
    if args.fixture:
        fix_run = fixture_run(REPO, args.fixture, run_dir, args.godot,
                              args.preset_mode, args.timeout_export)
        print(f"mut01: FIXTURE-RUN exit={fix_run.get('rc')} "
              f"pass_lines={len(fix_run.get('pass_lines', []))} "
              f"fail_lines={len(fix_run.get('fail_lines', []))} "
              f"error={fix_run.get('error')}")

    # ---- 5b. dynamic splice-attack on the landed fixtures ----------------
    attack = []
    attack_gate_ok = True
    if not args.no_attack:
        attack = attack_fixtures(REPO, run_dir, args.godot, args.timeout_export)
        for item in attack:
            if item.get("error"):
                print(f"mut01: ATTACK {item['fixture']}: skipped ({item['error']})")
                continue
            if item.get("control", {}).get("classification") != "ACCEPT":
                attack_gate_ok = False
            for arm, case in item.get("cases", {}).items():
                if case["classification"].startswith("ACCEPT"):
                    attack_gate_ok = False
        print(f"mut01: attack gate ok={attack_gate_ok}")

    # ---- 6. evidence -----------------------------------------------------
    verdict = "PASS" if (expectation_met and attack_gate_ok) else "FAIL"
    payload = {
        "seat": "r102-M1",
        "utc": started,
        "godot": godot_version,
        "template": str(template_path) if template_path else None,
        "template_bytes": template_bytes,
        "tmp_probe": {"ok": tmp_ok, "detail": tmp_detail},
        "scratch": str(run_dir),
        "plain_export": plain,
        "embedded": {"attempts": embed_attempts,
                     "artifact": real.get("artifact"),
                     "launch": real.get("launch"),
                     "receipt": real.get("receipt"),
                     "pck_embedded_delta": real.get("pck_embedded_delta")},
        "artifacts": artifacts,
        "gates": {"forged_accepted": forged_accepted,
                  "forged_rejected": forged_rejected,
                  "single_check_blind": single_check_blind,
                  "real_strong_accept": real_strong,
                  "observed_forged_outcome": observed_forged,
                  "expect": args.expect,
                  "met": expectation_met,
                  "attack_gate_ok": attack_gate_ok},
        "fixture_scan": scan,
        "fixture_run": fix_run,
        "fixture_attack": attack,
        "verdict": verdict,
    }
    out_json = Path(args.json) if args.json else run_dir / "mut01-verdict.json"
    out_json.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"mut01: evidence={out_json}")
    print(f"RESULT: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
