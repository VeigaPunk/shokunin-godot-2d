#!/usr/bin/env python3
"""r103 M1 / mut01 — CLI-divergence forgery against E1's export_div_s01 row.

Mandate (mut02 mold): E1's `export_div_s01` row family (preset export vs CLI
`--export-pack` export of the same project) must REJECT an arm whose "CLI
artifact" was forged by `cp` from a foreign source instead of produced by a
real `--export-pack` run of the row's own project in that run — forged/stale/
foreign bytes must never reach the row's census evidence, or the row must FAIL.

Model arms (all bytes REAL godot 4.7.2.stable.arch_linux.ed1daf0bf outputs):
  G   genuine      : preset `--export-release` (embed_pck=true, embedded
                     payload extracted via the `<u64 size><u32 'GDPC'>` EOF
                     trailer) + CLI `--export-pack` of the same project.
  F1  echo-forge   : the extracted embedded payload cp'd in place of the CLI
                     artifact ("zero-divergence" claim).
  F2  foreign-forge: a FOREIGN project's pck (containing resource
                     sentinel_m1.tres holding FORGED_SENTINEL_M1) cp'd in
                     place of the CLI artifact. (Plain .txt files are NOT
                     exported: export_filter=all_resources ships resources
                     only — measured, cf. E1 fixture's nondata=absent.)
  F3  stale-forge  : real CLI pck planted + backdated (2020) mtime, then the
                     export step forced to fail (bogus preset) -> stale
                     resurrection.
Verdict logics over captured bytes (forge read BEFORE any overwrite):
  naive  : presence census (artifact exists + parses -> PASS-shaped row) —
           the defeasible design the mutation must kill.
  honest : fresh export THIS run, nested exit == 0, mtime >= run t0, entry-set
           cross-check, sentinel exclusion -> the fail-closed design.
  honest_reuse : honest checks but WITHOUT the fresh-export requirement —
           measures exactly which forges are catchable under a reuse design.

Phase B: runs the REAL `corpus/fixtures/export_div_s01.gd` read-only (copied
to scratch) with forged pcks pre-planted at the exact per-arm consumption
paths, plus a scratch-only vulnerable variant (_export skip-if-exists +
_export_ok file-exists-only) as the attack-lands control. Never runs
run_battery.py; touches no shared file; corpus is copied, never edited.
Scratch: /var/tmp/r103c-M1 only (never /tmp: EDQUOT quota; exports run under
unshare+tmpfs for the packer's fixed /tmp/tmpproject.binary temp path).
"""

import hashlib
import json
import os
import re
import shlex
import shutil
import struct
import subprocess
import time
from pathlib import Path

ROOT = Path("/var/tmp/r103c-M1")
GODOT = "/usr/bin/godot"
SH = "/usr/bin/sh"
SENTINEL_NAME = "sentinel_m1.tres"
SENTINEL_TOKEN = "FORGED_SENTINEL_M1"
SENTINEL_TRES = ('[gd_resource type="Resource" format=3]\n\n'
                 '[resource]\nmarker = "%s"\n' % SENTINEL_TOKEN)
BACKDATE = 1577836800  # 2020-01-01
CORPUS_FX = (Path(__file__).resolve().parents[3]
             / "corpus" / "fixtures" / "export_div_s01.gd")

BASE_PROJECT = (
    "config_version=5\n\n[application]\n"
    'config/name="DivModel"\n'
    'run/main_scene="res://main.tscn"\n'
    'config/features=PackedStringArray("4.7")\n\n'
    "[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
)
FOREIGN_PROJECT = (
    "config_version=5\n\n[application]\n"
    'config/name="DivForeign"\n'
    'run/main_scene="res://main.tscn"\n'
    'config/features=PackedStringArray("4.7")\n\n'
    "[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
)
PRESETS_EMBED = """[preset.0]
name="Embed"
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
"""
MAIN_TSCN = ("[gd_scene load_steps=2 format=3]\n\n"
             '[ext_resource type="Script" path="res://main.gd" id="1"]\n\n'
             '[node name="Main" type="Node"]\nscript = ExtResource("1")\n')


def q(s):
    return shlex.quote(str(s))


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe_unshare():
    try:
        p = subprocess.run(["unshare", "-m", "--map-root-user", SH, "-c",
                            "mount -t tmpfs -o size=16M tmpfs /tmp && test -w /tmp"],
                           capture_output=True, timeout=30)
        return p.returncode == 0
    except Exception:
        return False


def run_export(proj, mode, preset, out, unshare):
    out.parent.mkdir(parents=True, exist_ok=True)
    body = ("cd %s && exec %s --headless --path %s --%s %s %s"
            % (q(proj), q(GODOT), q(proj), mode, q(preset), q(out)))
    if unshare:
        cmd = ["unshare", "-m", "--map-root-user", SH, "-c",
               "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97; " + body]
    else:
        cmd = [SH, "-c", body]
    t0 = time.monotonic()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    dt = round(time.monotonic() - t0, 2)
    exists = out.is_file()
    return {"mode": mode, "preset": preset, "out": str(out), "exit": p.returncode,
            "seconds": dt, "exists": exists,
            "size": out.stat().st_size if exists else 0,
            "sha256": sha256_file(out) if exists else None,
            "mtime_ns": out.stat().st_mtime_ns if exists else None,
            "log_tail": (p.stdout + p.stderr).strip().splitlines()[-4:]}


def parse_pck(blob):
    """Godot 4.7.2 PCK, layout measured this round (dir_off table + count)."""
    if len(blob) < 0x28 or blob[:4] != b"GDPC":
        return None
    version, major, minor, patch, flags = struct.unpack_from("<5I", blob, 4)
    file_base = struct.unpack_from("<Q", blob, 24)[0]
    dir_off = struct.unpack_from("<Q", blob, 32)[0]
    if not (0 < dir_off <= len(blob) - 4):
        return None
    count = struct.unpack_from("<I", blob, dir_off)[0]
    entries = []
    off = dir_off + 4
    for _ in range(count):
        if off + 4 > len(blob):
            return None
        plen = struct.unpack_from("<I", blob, off)[0]
        if plen == 0 or plen > 4096 or off + 4 + plen + 36 > len(blob):
            return None
        path = blob[off + 4:off + 4 + plen].split(b"\x00")[0].decode("utf-8", "replace")
        rec = off + 4 + plen
        rel_off, size = struct.unpack_from("<QQ", blob, rec)
        md5 = blob[rec + 16:rec + 32].hex()
        eflags = struct.unpack_from("<I", blob, rec + 32)[0]
        entries.append({"path": path, "rel_off": rel_off, "size": size,
                        "md5": md5, "flags": eflags})
        off = rec + 36
    data_base = None
    for b in (file_base, 0):
        if entries and all(0 <= b + e["rel_off"]
                           and b + e["rel_off"] + e["size"] <= len(blob)
                           and hashlib.md5(blob[b + e["rel_off"]:b + e["rel_off"] + e["size"]]).hexdigest() == e["md5"]
                           for e in entries):
            data_base = b
            break
    return {"fmt_version": version, "engine": [major, minor, patch], "flags": flags,
            "file_base": file_base, "dir_off": dir_off, "count": count,
            "entries": entries, "data_base": data_base}


def extract_embedded(bin_blob):
    """<u64 payload_size><u32 'GDPC'> trailer; payload = the pck bytes."""
    if len(bin_blob) < 16 or bin_blob[-4:] != b"GDPC":
        return None
    size = struct.unpack_from("<Q", bin_blob, len(bin_blob) - 12)[0]
    start = len(bin_blob) - 12 - size
    if start < 0 or bin_blob[start:start + 4] != b"GDPC" or start + size != len(bin_blob) - 12:
        return None
    return {"start": start, "size": size, "payload": bin_blob[start:start + size]}


def census(blob):
    pc = parse_pck(blob)
    if pc is None:
        return None
    ents = sorted(pc["entries"], key=lambda e: e["path"])
    paths = "\n".join(e["path"] for e in ents)
    triples = "\n".join("%s:%d:%s:%d" % (e["path"], e["size"], e["md5"], e["flags"])
                        for e in ents)
    return {"blob_len": len(blob), "blob_sha256": hashlib.sha256(blob).hexdigest(),
            "entry_count": len(ents), "paths": [e["path"] for e in ents],
            "files": {e["path"]: e["size"] for e in ents},
            "paths_sha256": hashlib.sha256(paths.encode()).hexdigest(),
            "triples_sha256": hashlib.sha256(triples.encode()).hexdigest(),
            "data_md5_all_ok": pc["data_base"] is not None,
            "container": {"file_base": pc["file_base"], "dir_off": pc["dir_off"],
                          "flags": pc["flags"], "fmt_version": pc["fmt_version"]}}


def divergence_class(preset_cen, cli_cen):
    if preset_cen is None or cli_cen is None:
        return "unparsable"
    if preset_cen["blob_sha256"] == cli_cen["blob_sha256"]:
        return "identical_blob"
    if preset_cen["triples_sha256"] == cli_cen["triples_sha256"]:
        return "entries_equal_container_differs"
    return "entry_mismatch:%d->%d" % (preset_cen["entry_count"], cli_cen["entry_count"])


def _row_pass(cls, cen, extra=""):
    return ("PASS export_div s01 class=%s cli_len=%d entries=%d cli_sha=%s%s"
            % (cls, cen["blob_len"], cen["entry_count"], cen["blob_sha256"][:16], extra))


def naive_verdict(cli_path, preset_cen):
    """Presence-census classifier: trusts whatever artifact is at the path."""
    p = Path(cli_path)
    if not p.is_file():
        return {"verdict": "FAIL", "reason": "cli_artifact_missing", "census": None}
    cen = census(p.read_bytes())
    if cen is None or cen["entry_count"] == 0 or not cen["data_md5_all_ok"]:
        return {"verdict": "FAIL", "reason": "artifact_unparsable", "census": cen}
    sentinel = any(SENTINEL_NAME in x for x in cen["paths"])
    return {"verdict": "PASS", "reason": "",
            "line": _row_pass(divergence_class(preset_cen, cen), cen),
            "census": cen, "sentinel_in_evidence": sentinel}


def honest_verdict(cli_path, preset_cen, run, t0_ns, expected_paths):
    """Fail-closed classifier: only in-run evidence, cross-checked."""
    p = Path(cli_path)
    if run["exit"] != 0:
        return {"verdict": "FAIL", "reason": "export_exit=%d" % run["exit"]}
    if not p.is_file():
        return {"verdict": "FAIL", "reason": "cli_artifact_missing_after_export"}
    if t0_ns is not None and p.stat().st_mtime_ns < t0_ns:
        return {"verdict": "FAIL", "reason": "stale_artifact_mtime"}
    cen = census(p.read_bytes())
    if cen is None or cen["entry_count"] == 0 or not cen["data_md5_all_ok"]:
        return {"verdict": "FAIL", "reason": "artifact_unparsable", "census": cen}
    if any(SENTINEL_NAME in x for x in cen["paths"]):
        return {"verdict": "FAIL", "reason": "foreign_sentinel_in_evidence",
                "census": cen, "sentinel_in_evidence": True}
    if expected_paths is not None and set(cen["paths"]) != set(expected_paths):
        return {"verdict": "FAIL", "reason": "entry_set_mismatch", "census": cen,
                "expected_n": len(set(expected_paths)), "got_n": cen["entry_count"]}
    return {"verdict": "PASS", "reason": "",
            "line": _row_pass(divergence_class(preset_cen, cen), cen, " sentinel=false"),
            "census": cen, "sentinel_in_evidence": False}


def honest_reuse(cli_path, preset_cen, t0_ns, expected_paths):
    """Honest checks WITHOUT the fresh-export requirement (reuse-design probe).
    Deliberately no forged-sha blacklist: an external attacker has no such
    knowledge, and a blacklist is not a self-contained fixture law."""
    p = Path(cli_path)
    if not p.is_file():
        return {"verdict": "FAIL", "reason": "cli_artifact_missing"}
    if t0_ns is not None and p.stat().st_mtime_ns < t0_ns:
        return {"verdict": "FAIL", "reason": "stale_artifact_mtime"}
    cen = census(p.read_bytes())
    if cen is None or cen["entry_count"] == 0 or not cen["data_md5_all_ok"]:
        return {"verdict": "FAIL", "reason": "artifact_unparsable", "census": cen}
    if any(SENTINEL_NAME in x for x in cen["paths"]):
        return {"verdict": "FAIL", "reason": "foreign_sentinel_in_evidence", "census": cen}
    if expected_paths is not None and set(cen["paths"]) != set(expected_paths):
        return {"verdict": "FAIL", "reason": "entry_set_mismatch", "census": cen}
    return {"verdict": "PASS", "reason": "reuse_accepted",
            "line": _row_pass(divergence_class(preset_cen, cen), cen, " sentinel=false"),
            "census": cen}


def write_file(p, text):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def build_project(root, name, project_cfg, main_gd, extra_files):
    proj = Path(root) / name
    if proj.exists():
        shutil.rmtree(proj)
    write_file(proj / "project.godot", project_cfg)
    write_file(proj / "export_presets.cfg", PRESETS_EMBED)
    write_file(proj / "main.tscn", MAIN_TSCN)
    write_file(proj / "main.gd", main_gd)
    for rel, text in extra_files.items():
        write_file(proj / rel, text)
    return proj


def slim(v):
    if v and v.get("census"):
        v = dict(v)
        v["census"] = {kk: v["census"][kk] for kk in
                       ("blob_len", "blob_sha256", "entry_count", "paths_sha256",
                        "triples_sha256", "data_md5_all_ok")}
    return v


def main():
    out = {"seat": "M1", "script": "mut01.py",
           "engine": subprocess.run([GODOT, "--version"], capture_output=True,
                                    text=True).stdout.strip(),
           "date": time.strftime("%Y-%m-%d %H:%M:%S %z"),
           "uptime": open("/proc/uptime").read().split()[0],
           "loadavg": list(os.getloadavg()),
           "scratch": str(ROOT)}
    shutil.rmtree(ROOT, ignore_errors=True)
    (ROOT / "out").mkdir(parents=True)
    unshare = probe_unshare()
    out["unshare_tmpfs"] = unshare

    # ---- genuine artifacts (real exports)
    base = build_project(ROOT / "G", "proj", BASE_PROJECT,
                         'extends Node\n\nfunc _ready() -> void:\n'
                         '\tprint("PACK_DIV_MARKER boot=true")\n',
                         {"data/notes.txt": "div model data\n"})
    g_out = ROOT / "G" / "out"
    r_preset = run_export(base, "export-release", "Embed", g_out / "preset.x86_64", unshare)
    r_cli = run_export(base, "export-pack", "Embed", g_out / "cli.pck", unshare)
    bin_blob = (g_out / "preset.x86_64").read_bytes() if r_preset["exists"] else b""
    emb = extract_embedded(bin_blob)
    if emb:
        (g_out / "embedded_extract.pck").write_bytes(emb["payload"])
    emb_path = g_out / "embedded_extract.pck"
    out["runs"] = {"preset_release": r_preset, "cli_pack": r_cli,
                   "embedded_extract": {"start": emb["start"] if emb else None,
                                        "size": emb["size"] if emb else None,
                                        "sha256": sha256_file(emb_path) if emb else None}}
    preset_cen = census(emb["payload"]) if emb else None
    cli_cen = census((g_out / "cli.pck").read_bytes()) if r_cli["exists"] else None
    genuine_cls = divergence_class(preset_cen, cli_cen)
    expected_paths = preset_cen["paths"] if preset_cen else None
    out["censuses"] = {"preset_embedded": preset_cen, "cli_fresh": cli_cen,
                       "genuine_class": genuine_cls,
                       "entry_triples_equal": bool(preset_cen and cli_cen and
                                                   preset_cen["triples_sha256"] == cli_cen["triples_sha256"])}

    # ---- foreign artifact carrying the sentinel resource
    foreign = build_project(ROOT / "X", "fproj", FOREIGN_PROJECT,
                            'extends Node\n\nfunc _ready() -> void:\n'
                            '\tprint("FOREIGN_MARKER boot=false")\n',
                            {SENTINEL_NAME: SENTINEL_TRES})
    r_foreign = run_export(foreign, "export-pack", "Embed", ROOT / "X" / "out" / "foreign.pck", unshare)
    foreign_blob = (ROOT / "X" / "out" / "foreign.pck").read_bytes() if r_foreign["exists"] else b""
    foreign_cen = census(foreign_blob) if foreign_blob else None
    out["runs"]["foreign_pack"] = r_foreign
    out["censuses"]["foreign"] = foreign_cen
    out["foreign_sentinel_present"] = bool(
        foreign_cen and any(SENTINEL_NAME in x for x in foreign_cen["paths"]))
    out["foreign_token_bytes_present"] = bool(foreign_blob and SENTINEL_TOKEN.encode() in foreign_blob)

    # ---- forge arms (forge read BEFORE any fresh export can overwrite it)
    arms = {}

    # F1 echo-forge: extracted embedded payload cp'd as the CLI artifact
    d1 = ROOT / "F1" / "out"
    d1.mkdir(parents=True)
    if emb:
        shutil.copy(emb_path, d1 / "cli.pck")
    f1_sha = sha256_file(d1 / "cli.pck") if (d1 / "cli.pck").exists() else None
    naive_pre_1 = slim(naive_verdict(d1 / "cli.pck", preset_cen))
    reuse_pre_1 = slim(honest_reuse(d1 / "cli.pck", preset_cen, None, expected_paths))
    t0 = time.time_ns()
    r_f1 = run_export(base, "export-pack", "Embed", d1 / "cli.pck", unshare)
    arms["F1_echo"] = {
        "forge": "cp embedded_extract.pck -> cli.pck", "forged_sha256": f1_sha,
        "naive_on_forge": naive_pre_1, "reuse_on_forge": reuse_pre_1,
        "fresh_export": r_f1,
        "honest_after_fresh": slim(honest_verdict(d1 / "cli.pck", preset_cen, r_f1, t0, expected_paths)),
    }

    # F2 foreign-forge: foreign project pck (sentinel resource) cp'd as CLI artifact
    d2 = ROOT / "F2" / "out"
    d2.mkdir(parents=True)
    shutil.copy(ROOT / "X" / "out" / "foreign.pck", d2 / "cli.pck")
    f2_sha = sha256_file(d2 / "cli.pck")
    naive_raw_2 = naive_verdict(d2 / "cli.pck", preset_cen)
    sentinel_paths_2 = [x for x in (naive_raw_2["census"] or {}).get("paths", [])
                        if SENTINEL_NAME in x]
    naive_pre_2 = slim(naive_raw_2)
    reuse_pre_2 = slim(honest_reuse(d2 / "cli.pck", preset_cen, None, expected_paths))
    t0 = time.time_ns()
    r_f2 = run_export(base, "export-pack", "Embed", d2 / "cli.pck", unshare)
    arms["F2_foreign"] = {
        "forge": "cp foreign.pck -> cli.pck", "forged_sha256": f2_sha,
        "sentinel_paths": sentinel_paths_2,
        "naive_on_forge": naive_pre_2, "reuse_on_forge": reuse_pre_2,
        "fresh_export": r_f2,
        "honest_after_fresh": slim(honest_verdict(d2 / "cli.pck", preset_cen, r_f2, t0, expected_paths)),
    }

    # F3 stale-forge: real pck planted + backdated, export step forced to fail
    d3 = ROOT / "F3" / "out"
    d3.mkdir(parents=True)
    shutil.copy(g_out / "cli.pck", d3 / "cli.pck")
    os.utime(d3 / "cli.pck", (BACKDATE, BACKDATE))
    f3_sha = sha256_file(d3 / "cli.pck")
    t0 = time.time_ns()
    r_f3 = run_export(base, "export-pack", "NoSuchPreset", d3 / "cli.pck", unshare)
    arms["F3_stale"] = {
        "forge": "cp cli.pck; touch -d 2020-01-01; export w/ bogus preset",
        "forged_sha256": f3_sha,
        "stale_mtime": (d3 / "cli.pck").stat().st_mtime if (d3 / "cli.pck").exists() else None,
        "bogus_export": r_f3,
        "file_survives_failed_export": (d3 / "cli.pck").is_file(),
        "naive_on_forge": slim(naive_verdict(d3 / "cli.pck", preset_cen)),
        "honest_after_run": slim(honest_verdict(d3 / "cli.pck", preset_cen, r_f3, t0, expected_paths)),
        "reuse_on_forge": slim(honest_reuse(d3 / "cli.pck", preset_cen, time.time_ns(), expected_paths)),
    }
    out["arms"] = arms

    # ---- assertions
    asserts = {}

    def mk(name, ok, detail):
        asserts[name] = {"ok": bool(ok), "detail": detail}

    naive_g = naive_verdict(g_out / "cli.pck", preset_cen)
    mk("genuine_row_pass_shaped",
       naive_g["verdict"] == "PASS" and genuine_cls.startswith("entries_equal"),
       {"line": naive_g.get("line"), "class": genuine_cls})
    f2_naive = arms["F2_foreign"]["naive_on_forge"]
    mk("naive_accepts_F2_foreign (defect class proof)",
       f2_naive["verdict"] == "PASS" and f2_naive["sentinel_in_evidence"],
       {"line": f2_naive.get("line"),
        "sentinel_paths": arms["F2_foreign"].get("sentinel_paths", [])})
    f3_naive = arms["F3_stale"]["naive_on_forge"]
    mk("naive_accepts_F3_stale (defect class proof)",
       f3_naive["verdict"] == "PASS" and arms["F3_stale"]["bogus_export"]["exit"] != 0,
       {"naive_verdict": f3_naive["verdict"],
        "bogus_exit": arms["F3_stale"]["bogus_export"]["exit"],
        "file_survives": arms["F3_stale"]["file_survives_failed_export"]})
    f1_h = arms["F1_echo"]["honest_after_fresh"]
    mk("honest_neutralizes_F1 (fresh export replaces forged sha)",
       f1_h["verdict"] == "PASS" and f1_h["census"]["blob_sha256"] != f1_sha
       and f1_h["census"]["blob_sha256"] == (cli_cen or {}).get("blob_sha256"),
       {"honest_line": f1_h.get("line"), "forged_sha": f1_sha})
    f2_h = arms["F2_foreign"]["honest_after_fresh"]
    mk("honest_neutralizes_F2 (sentinel absent, genuine sha after fresh export)",
       f2_h["verdict"] == "PASS" and not f2_h["sentinel_in_evidence"]
       and f2_h["census"]["blob_sha256"] == (cli_cen or {}).get("blob_sha256"),
       {"honest_line": f2_h.get("line")})
    f3_h = arms["F3_stale"]["honest_after_run"]
    mk("honest_REJECTS_F3 (failed export cannot resurrect stale artifact)",
       f3_h["verdict"] == "FAIL" and f3_h["reason"].startswith("export_exit="),
       {"reason": f3_h["reason"]})
    f3_r = arms["F3_stale"]["reuse_on_forge"]
    mk("honest_reuse_REJECTS_F3 (backdated mtime)",
       f3_r["verdict"] == "FAIL" and f3_r["reason"] == "stale_artifact_mtime",
       {"reason": f3_r["reason"]})
    f2_r = arms["F2_foreign"]["reuse_on_forge"]
    mk("honest_reuse_REJECTS_F2 (sentinel)",
       f2_r["verdict"] == "FAIL" and f2_r["reason"] == "foreign_sentinel_in_evidence",
       {"reason": f2_r["reason"]})
    f1_r = arms["F1_echo"]["reuse_on_forge"]
    mk("RESIDUAL_honest_reuse_ACCEPTS_F1 (self-content forge)",
       f1_r["verdict"] == "PASS" and f1_r.get("reason") == "reuse_accepted"
       and f1_r["census"]["blob_sha256"] == f1_sha,
       {"verdict": f1_r["verdict"], "reason": f1_r.get("reason"),
        "forged_sha": f1_sha, "genuine_cli_sha": (cli_cen or {}).get("blob_sha256")})
    out["asserts"] = asserts

    # ---- phase B: landed fixture
    out["phase_b"] = phase_b()

    payload = ROOT / "out" / "mut01_verdicts.json"
    payload.write_text(json.dumps(out, indent=1, default=str) + "\n")

    print("== mut01 summary ==")
    print("genuine_class:", genuine_cls,
          "| preset_len:", (preset_cen or {}).get("blob_len"),
          "cli_len:", (cli_cen or {}).get("blob_len"),
          "| triples_equal:", out["censuses"]["entry_triples_equal"])
    print("engine:", out["engine"], "| unshare:", unshare,
          "| foreign_sentinel:", out["foreign_sentinel_present"],
          "| token_bytes:", out["foreign_token_bytes_present"])
    for name, a in asserts.items():
        print(("ASSERT %-66s" % name), "ok=" + str(a["ok"]), a["detail"])
    for k, a in arms.items():
        ho = a.get("honest_after_fresh", a.get("honest_after_run")) or {}
        print("ARM", k, "| naive:", a.get("naive_on_forge", {}).get("verdict"),
              "| honest_fresh:", ho.get("verdict"), ho.get("reason", ""),
              "| honest_reuse:", a.get("reuse_on_forge", {}).get("verdict"),
              a.get("reuse_on_forge", {}).get("reason", ""))
    pb = out["phase_b"]
    print("phase_b status:", pb.get("status", "ran"))
    for k in ("fixture_sha256", "fixture_sha256_end", "fixture_stable_during_run",
              "pristine_pack_artifact", "salient", "variant_applied",
              "variant_pristine_line", "variant_forged_line"):
        if k in pb:
            print(" %s: %s" % (k, pb[k]))
    print("wrote", payload)


# ------------------------------------------------------------------ phase B

def phase_b():
    if not CORPUS_FX.is_file():
        return {"status": "fixture_absent_at_probe_time", "path": str(CORPUS_FX)}
    src = CORPUS_FX.read_text()
    sha_start = hashlib.sha256(src.encode()).hexdigest()
    pb = {"fixture": str(CORPUS_FX), "fixture_sha256": sha_start}
    fx = ROOT / "fx"
    proj = fx / "proj"
    proj.mkdir(parents=True)
    write_file(proj / "project.godot",
               '[application]\nconfig/name="R103M1Fx"\nconfig/features=PackedStringArray("4.7")\n')
    write_file(proj / "export_div_s01.gd", src)
    foreign_src = ROOT / "X" / "out" / "foreign.pck"

    def run_fx(root, arm, script="export_div_s01.gd"):
        env = dict(os.environ, EXPORT_DIV_ROOT=str(root))
        cmd = [GODOT, "--headless", "--path", str(proj), "--script",
               "res://" + script, "--", "--arm=" + arm]
        t0 = time.monotonic()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=240, env=env)
            return {"cmd": cmd, "exit": p.returncode,
                    "seconds": round(time.monotonic() - t0, 2),
                    "pass_lines": [l for l in p.stdout.splitlines() if l.startswith("PASS ")],
                    "fail_lines": [l for l in p.stdout.splitlines() if l.startswith("FAIL ")],
                    "sentinel_in_stdout": SENTINEL_TOKEN in p.stdout or SENTINEL_NAME in p.stdout,
                    "nul_warnings": sum(1 for l in p.stderr.splitlines()
                                        if "Unexpected NUL character" in l),
                    "diag_export_lines": [l for l in p.stdout.splitlines()
                                          if "export_" in l and "=cd" in l][:6],
                    "stdout_tail": p.stdout.splitlines()[-3:]}
        except subprocess.TimeoutExpired:
            return {"cmd": cmd, "exit": None, "state": "timeout_240s"}

    def plant_rel(rel):
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(foreign_src, p)
        return {"path": str(p), "rel": rel, "plant_sha256": sha256_file(p),
                "plant_size": p.stat().st_size}

    # pristine roots
    r1 = run_fx(ROOT / "pb1", "pack")
    r1i = run_fx(ROOT / "pb1i", "ident")
    pb["pristine_pack"] = r1
    pb["pristine_ident"] = r1i
    art_pack = ROOT / "pb1" / "div_s01" / "pack" / "out" / "pack" / "cli.pck"
    art_stock = ROOT / "pb1i" / "div_s01" / "ident" / "out" / "ident_stock" / "stock.pck"
    art_icl = ROOT / "pb1i" / "div_s01" / "ident" / "out" / "ident_cli" / "cli.pck"
    pb["pristine_artifacts"] = {
        "pack_cli_pck": {"sha256": sha256_file(art_pack) if art_pack.is_file() else None,
                         "size": art_pack.stat().st_size if art_pack.is_file() else None},
        "ident_stock_pck": {"sha256": sha256_file(art_stock) if art_stock.is_file() else None,
                            "size": art_stock.stat().st_size if art_stock.is_file() else None},
        "ident_cli_pck": {"sha256": sha256_file(art_icl) if art_icl.is_file() else None,
                          "size": art_icl.stat().st_size if art_icl.is_file() else None},
    }

    # planted roots: forged foreign pck at exact per-arm consumption paths + decoys
    pack_plants = [
        plant_rel("pb2/div_s01/pack/out/pack/cli.pck"),
        plant_rel("pb2/div_s01/pack/out/cli.pck"),
        plant_rel("pb2/div_s01/out/cli.pck"),
        plant_rel("pb2i/div_s01/ident/out/ident_stock/stock.pck"),
        plant_rel("pb2i/div_s01/ident/out/ident_cli/cli.pck"),
    ]
    r2 = run_fx(ROOT / "pb2", "pack")
    r2i = run_fx(ROOT / "pb2i", "ident")
    pb["planted_pack"] = r2
    pb["planted_ident"] = r2i
    refs = {"ident_stock": pb["pristine_artifacts"]["ident_stock_pck"],
            "ident_cli": pb["pristine_artifacts"]["ident_cli_pck"],
            "pack": pb["pristine_artifacts"]["pack_cli_pck"]}
    for pl in pack_plants:
        p = Path(pl["path"])
        pl["post_exists"] = p.is_file()
        pl["post_sha256"] = sha256_file(p) if p.is_file() else None
        pl["overwritten"] = pl["post_sha256"] not in (None, pl["plant_sha256"])
        key = ("ident_stock" if "ident_stock" in pl["rel"]
               else "ident_cli" if "ident_cli" in pl["rel"] else "pack")
        pl["consumption_path"] = key
        pl["equals_pristine_fresh_sha"] = bool(
            pl["post_sha256"] and pl["post_sha256"] == refs[key]["sha256"]
            and pl["post_sha256"] != pl["plant_sha256"])
    pb["plants"] = pack_plants
    pb["planted_bytes_in_stdout"] = bool(r2.get("sentinel_in_stdout") or r2i.get("sentinel_in_stdout"))
    pb["salient"] = {
        "pristine_pack_pass": r1["pass_lines"], "planted_pack_pass": r2["pass_lines"],
        "pass_lines_identical": r1["pass_lines"] == r2["pass_lines"],
        "pristine_ident_pass": r1i["pass_lines"], "planted_ident_pass": r2i["pass_lines"],
        "ident_lines_identical": r1i["pass_lines"] == r2i["pass_lines"],
        "planted_exact_paths_overwritten": [pl["rel"] for pl in pack_plants
                                            if pl["overwritten"]],
        "planted_decoy_paths_untouched": [pl["rel"] for pl in pack_plants
                                          if not pl["overwritten"]],
        "note_cross_root_sha": ("fresh exports are not byte-identical across "
                                "different scratch roots (per-root .godot cache); "
                                "neutrality is proven within-run: planted sha "
                                "replaced, verdict fields unchanged"),
    }

    # ---- scratch-only vulnerable variant: reuse-if-exists (attack-lands control)
    anchor1 = ("\tvar out_dir := _out_dir(slug)\n\t_clear_dir(out_dir)\n")
    repl1 = ("\tvar out_dir := _out_dir(slug)\n\tvar out_path_probe := out_dir.path_join(name)\n"
             "\tif FileAccess.file_exists(out_path_probe):\n\t\treturn out_path_probe\n"
             "\t_clear_dir(out_dir)\n")
    anchor2 = ('var log := FileAccess.get_file_as_string(_log_path("export_" + slug))\n'
               '\treturn log.contains("[ DONE ]")')
    repl2 = "return true"
    variant = src.replace(anchor1, repl1, 1).replace(anchor2, repl2, 1)
    pb["variant_applied"] = {"anchor1_unique": src.count(anchor1) == 1,
                             "anchor2_unique": src.count(anchor2) == 1,
                             "changed": variant != src}
    if variant != src:
        vproj = fx / "vproj"
        vproj.mkdir(parents=True)
        write_file(vproj / "project.godot",
                   '[application]\nconfig/name="R103M1FxV"\nconfig/features=PackedStringArray("4.7")\n')
        write_file(vproj / "mut_variant.gd", variant)

        def run_variant(root, arm):
            env = dict(os.environ, EXPORT_DIV_ROOT=str(root))
            cmd = [GODOT, "--headless", "--path", str(vproj), "--script",
                   "res://mut_variant.gd", "--", "--arm=" + arm]
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=240, env=env)
                return {"cmd": cmd, "exit": p.returncode,
                        "pass_lines": [l for l in p.stdout.splitlines() if l.startswith("PASS ")],
                        "fail_lines": [l for l in p.stdout.splitlines() if l.startswith("FAIL ")]}
            except subprocess.TimeoutExpired:
                return {"exit": None, "state": "timeout_240s"}

        rv1 = run_variant(ROOT / "pbv1", "pack")
        vplant = ROOT / "pbv2" / "div_s01" / "pack" / "out" / "pack" / "cli.pck"
        vplant.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(foreign_src, vplant)
        vplant_sha = sha256_file(vplant)
        rv2 = run_variant(ROOT / "pbv2", "pack")
        pb["variant"] = {
            "vulnerable_shape": "reuse-if-exists (_export returns existing path; "
                                "_export_ok = file-exists-only)",
            "pristine": rv1, "forged": rv2,
            "plant_sha256": vplant_sha, "plant_size": vplant.stat().st_size,
            "plant_survives": vplant.is_file() and sha256_file(vplant) == vplant_sha,
            "attack_lands": bool(rv2.get("pass_lines") and not rv2.get("fail_lines")
                                 and rv2["pass_lines"] != rv1.get("pass_lines")),
        }
        pb["variant_pristine_line"] = (rv1.get("pass_lines") or ["<none>"])[0]
        pb["variant_forged_line"] = (rv2.get("pass_lines") or ["<none>"])[0]

    sha_end = hashlib.sha256(CORPUS_FX.read_text().encode()).hexdigest()
    pb["fixture_sha256_end"] = sha_end
    pb["fixture_stable_during_run"] = sha_end == sha_start
    return pb


if __name__ == "__main__":
    main()
