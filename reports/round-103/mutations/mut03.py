#!/usr/bin/env python3
"""r103 M3 / mut03 — cross-contamination vs E3 (export_div_s03, multi-preset
sequential export) must REJECT.

E3's row family (C1) exports >=2 presets sequentially in one session and then
probes cross-contamination: preset-A artifact/flow must not be reached by
preset-B content, and vice versa. Two phases kill mutants with REAL machinery:

  replica    (before the real fixture existed, kept for independence) a modeled
             row predicate over a full --export-release A/B sequence, the
             preset-B-onto-A collision and a receipt-echo forger;
  targeted   (runs when corpus/fixtures/export_div_s03.gd is present) the REAL
             fixture, battery launch shape, on staged scratch copies:
             baseline arms seq/order/repeat must PASS; then two flow mutants
             (checker untouched) must trip the fixture's own census —
             m1 Embed's include_filter additionally carries the foreign beacon
                -> `reason=b_foreign_name_present`
             m2 B exported onto OUT_A (shared path)
                -> `reason=a_beacon_entry_missing`.

Replica sub-steps:

  setup      scratch Godot 4.7.2 project (frontier prefix `_` — never imported
             by the battery) with two presets over ONE project:
               A: pck-only (embed_pck=false), include only res://preset_id_a.txt
               B: embedded (embed_pck=true),   include only res://preset_id_b.txt
             Child main.gd prints which preset ids are visible at res:// and
             exits; a pck-only export therefore leaves a GDPC sidecar the child
             reads at boot, an embedded one carries the pack inside the binary.
  genuine    export A -> run A (must see exactly {a}); export B -> run B (must
             see exactly {b}); A's artifacts re-sha'd after B: unchanged
             (independence). Modeled row predicate must PASS both rows.
  mutation   cross-contamination injected: preset B is exported ONTO preset A's
             binary path (shared-path collision, the classic multi-preset
             bleed). The A row's artifact is then preset-B content. Anchored
             predicate must REJECT the A row (run shows {b}, sha moved).
  forge      receipt-echo forger (dead-measure class, cf. r102-mut3): a no-op
             script prints fabricated clean receipt lines. The anchored
             recompute (disk sha + artifact re-run) must keep the run REJECTED.

Verdict convention (r101/r102-mut7): `killed=true` <=> the genuine rows PASS
under the modeled predicate AND the contamination row + forger are REJECTED.

Hard rules honoured: run_battery.py NEVER executed; scratch under
/var/tmp/r103c-M3 (never /tmp — EDQUOT); repo is read-only from here; no
device-census tokens.
"""

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/var/tmp/r103c-M3")
REPO_ROOT = Path(__file__).resolve().parents[3]
PROJ = ROOT / "proj"
OUT = ROOT / "out"
GEN = OUT / "gen"
LOGS = ROOT / "logs"
HOME_DEFAULT = ROOT / "home-default"
GODOT = "godot"
TEMPLATE = Path.home() / ".local/share/godot/export_templates/4.7.2.stable/linux_release.x86_64"
TAG = "r103cM3DivSeq"

PROJECT_GODOT = '''config_version=5

[application]
config/name="R103cM3DivSeq"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")

[display]
window/size/viewport_width=320
window/size/viewport_height=180
'''

MAIN_GD = '''extends Node

func _ready() -> void:
	for id in ["a", "b"]:
		var p := "res://preset_id_%s.txt" % id
		print("M3_ID %s present=%s" % [id, str(FileAccess.file_exists(p))])
	print("M3_QUIT ok")
	get_tree().quit(0)
'''

MAIN_TSCN = '''[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://main.gd" id="1"]

[node name="Main" type="Node"]
script = ExtResource("1")
'''

# Two presets over one project. A: pck-only; B: embedded. include_filter keeps
# exactly one preset marker file per pack (markers are non-resource .txt files
# so they ride include_filter, not the resource export).
EXPORT_PRESETS = '''[preset.0]
name="A"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="resources"
export_files=PackedStringArray("res://main.tscn")
include_filter="res://preset_id_a.txt"
exclude_filter=""
export_path=""

[preset.0.options]
binary_format/architecture="x86_64"
binary_format/embed_pck=false

[preset.1]
name="B"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="resources"
export_files=PackedStringArray("res://main.tscn")
include_filter="res://preset_id_b.txt"
exclude_filter=""
export_path=""

[preset.1.options]
binary_format/architecture="x86_64"
binary_format/embed_pck=true
'''

FORGED_RECEIPT = """#!/bin/sh
# r103-mut03 receipt-echo forger: no export, no launch, no artifact writes.
echo 'Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org'
echo 'M3_ID a present=true'
echo 'M3_ID b present=false'
echo 'M3_QUIT ok'
echo 'PASS export_div_s03_seq_clean preset=A arms=2 clean_a=true clean_b=true independent=true'
exit 0
"""


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def run(cmd, env=None, cwd=None, timeout=120):
    t0 = time.monotonic()
    p = subprocess.run(cmd, env=env, cwd=cwd, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=timeout)
    return {"cmd": " ".join(shlex.quote(c) for c in cmd), "rc": p.returncode,
            "wall_ms": int((time.monotonic() - t0) * 1000),
            "stdout": p.stdout, "stderr": p.stderr,
            "stdout_sha256": sha256_bytes(p.stdout),
            "stderr_sha256": sha256_bytes(p.stderr)}


def rec(run_d, name):
    d = {k: run_d[k] for k in ("cmd", "rc", "wall_ms", "stdout_sha256",
                               "stderr_sha256")}
    d["name"] = name
    d["stdout_bytes"] = len(run_d["stdout"])
    d["stderr_bytes"] = len(run_d["stderr"])
    d["stdout_head"] = run_d["stdout"].decode("utf-8", "replace")[:1500]
    d["stderr_head"] = run_d["stderr"].decode("utf-8", "replace")[:800]
    d["m3_ids"] = ids_from_stdout(run_d)
    return d


def base_env():
    """Editor/export env: ambient (real HOME) — export template lookup reads
    $HOME/.local/share/godot/export_templates and refuses a relocated HOME."""
    return os.environ.copy()


def child_env():
    """Runtime env for the exported children: scratch HOME, no XDG override."""
    env = os.environ.copy()
    env["HOME"] = str(HOME_DEFAULT)
    env.pop("XDG_DATA_HOME", None)
    return env


def wipe(path: Path):
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def trailer_check(binary: Path):
    """u64 pack_size + GDPC magic in the last 12 bytes (embed law)."""
    b = binary.read_bytes()
    if len(b) < 12:
        return False, None, len(b)
    size = int.from_bytes(b[-12:-4], "little")
    return b[-4:] == b"GDPC", size, len(b)


def ids_from_stdout(d):
    got = []
    for line in d["stdout"].decode("utf-8", "replace").split("\n"):
        if line.startswith("M3_ID ") and "present=" in line:
            fid = line.split()[1]
            if line.endswith("present=true"):
                got.append(fid)
    return sorted(got)


def pck_contains(pack: Path, needle: bytes) -> bool:
    return needle in pack.read_bytes()


def classify_rowA(gen: dict, label: str, base: Path = None, run_key: str = None):
    """Modeled E3 acceptance predicate for the preset-A row (pck-only sidecar).

    Clauses (all disk-anchored at classification time; transcript values only
    recorded, never trusted):
      P1 transcript rc==0 and a run happened
      P2 shape: sidecar a.pck exists, GDPC magic; binary has NO GDPC trailer
      P3 marker: A artifact run prints exactly ['a']
      P4 independence: A artifacts on disk still byte-identical to the
         post-export-A shas (no later export touched them)
      P5 pack content: sidecar contains preset_id_a.txt, not preset_id_b.txt
    """
    base = base or GEN
    run_key = run_key or ("runA_mut" if label == "mut" else "runA")
    a_bin = base / "a.x86_64"
    a_pck = base / "a.pck"
    cl = {}
    cl["P1_run_rc0"] = gen[run_key]["rc"] == 0
    cl["P2_sidecar_gdpc"] = a_pck.is_file() and a_pck.read_bytes()[:4] == b"GDPC"
    tr_ok, _sz, _n = trailer_check(a_bin) if a_bin.is_file() else (True, None, 0)
    cl["P2_binary_no_trailer"] = (not tr_ok) and a_bin.is_file()
    cl["P3_marker_a_only"] = gen[run_key]["m3_ids"] == ["a"]
    cl["P4_sha_independent"] = (
        a_bin.is_file() and a_pck.is_file()
        and sha256_file(a_bin) == gen["shaA_pre"]["bin"]
        and sha256_file(a_pck) == gen["shaA_pre"]["pck"])
    cl["P5_pack_content"] = (a_pck.is_file()
                             and pck_contains(a_pck, b"preset_id_a.txt")
                             and not pck_contains(a_pck, b"preset_id_b.txt"))
    verdict = all(cl.values())
    return {"label": label, "base": str(base), "clauses": cl,
            "verdict": "PASS" if verdict else "REJECT",
            "failed": sorted(k for k, v in cl.items() if not v)}


def classify_rowB(gen: dict, label: str):
    b_bin = GEN / "b.x86_64"
    b_pck = GEN / "b.pck"
    tr_ok, pack_size, nbytes = trailer_check(b_bin) if b_bin.is_file() else (False, None, 0)
    cl = {}
    cl["P1_run_rc0"] = gen["runB"]["rc"] == 0
    cl["P2_embedded_trailer"] = tr_ok
    cl["P2_no_sidecar"] = not b_pck.exists()
    cl["P3_marker_b_only"] = gen["runB"]["m3_ids"] == ["b"]
    cl["P5_trailer_pack_size_plausible"] = (pack_size is not None and 12 < pack_size < nbytes)
    verdict = all(cl.values())
    return {"label": label, "clauses": cl, "verdict": "PASS" if verdict else "REJECT",
            "failed": sorted(k for k, v in cl.items() if not v)}


# ------------------------------------------------- targeted phase (real E3) --
# The real fixture landed mid-seat (sha256 60564378fc6343e00668abff30b3d1
# 9954b5719969193e66f67e89b5cd0e3a58, 499 lines). Targeted runs use the
# battery launch shape (run_battery.py:1927): staged fixtures project +
# `--script res://export_div_s03.gd -- --arm=<arm>` with EXPORT_DIV_ROOT.
FIXTURE = REPO_ROOT / "corpus/fixtures/export_div_s03.gd"
STAGE_SRC = REPO_ROOT / "corpus/fixtures/project.godot"


def verdict_lines(raw: bytes):
    return [l for l in raw.decode("utf-8", "replace").split("\n")
            if l.startswith(("PASS ", "FAIL "))]


def stage_fx(dest: Path, script_text: str):
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(STAGE_SRC, dest / "project.godot")
    (dest / "export_div_s03.gd").write_text(script_text)
    return dest


def run_fixture(fx: Path, arm: str, root: Path, timeout=240):
    env = os.environ.copy()
    env["EXPORT_DIV_ROOT"] = str(root)
    return run([GODOT, "--headless", "--path", str(fx), "--script",
                "res://export_div_s03.gd", "--", "--arm=" + arm],
               env=env, timeout=timeout)


def phase_targeted():
    """Baseline (must PASS seq/order/repeat) + two flow mutants that inject
    cross-contamination into the real fixture's own execution path:
      m1 beacon-feed overlap: preset Embed's include_filter also carries
         tag_pck_only.txt -> B's pack must trip its own `b_foreign_name_present`.
      m2 shared-path collision: B exported onto OUT_A -> a's row must trip
         `a_beacon_entry_missing`.
    The row's checker is untouched; only the flow/materials mutate.
    """
    tgt = ROOT / "tgt"
    text = FIXTURE.read_text()
    m1_old = 'include_filter=\\"tag_embed_only.txt\\"\\nexclude_filter=\\"tag_pck_only.txt\\"'
    m1_new = 'include_filter=\\"tag_embed_only.txt,tag_pck_only.txt\\"\\nexclude_filter=\\"\\"'
    assert text.count(m1_old) == 1, "m1 anchor not unique"
    m1_text = text.replace(m1_old, m1_new, 1)
    m2_old = "var ex_b := _export_pack(PRESET_EMB, OUT_B)"
    m2_new = "var ex_b := _export_pack(PRESET_EMB, OUT_A)"
    assert text.count(m2_old) == 1, "m2 anchor not unique"
    m2_text = text.replace(m2_old, m2_new, 1)

    fx_base = stage_fx(tgt / "fx_base", text)
    fx_m1 = stage_fx(tgt / "fx_m1", m1_text)
    fx_m2 = stage_fx(tgt / "fx_m2", m2_text)

    out = {}
    base_root = tgt / "root_base"
    for arm in ("seq", "order", "repeat"):
        r = run_fixture(fx_base, arm, base_root)
        out["baseline_" + arm] = {**rec(r, "baseline_" + arm),
                                  "verdict_lines": verdict_lines(r["stdout"])}
    r = run_fixture(fx_m1, "seq", tgt / "root_m1")
    out["mut_beacon_feed"] = {**rec(r, "mut_beacon_feed"),
                              "verdict_lines": verdict_lines(r["stdout"])}
    r = run_fixture(fx_m2, "seq", tgt / "root_m2")
    out["mut_path_collision"] = {**rec(r, "mut_path_collision"),
                                 "verdict_lines": verdict_lines(r["stdout"])}

    def pass_ok(key, arm):
        lines = out[key]["verdict_lines"]
        return any(l.startswith("PASS export_div s03 arm=%s " % arm) for l in lines)

    def fail_reason(key, reason):
        return any(l.startswith("FAIL export_div s03 arm=seq reason=%s" % reason)
                   for l in out[key]["verdict_lines"])

    out["ok"] = {
        "baseline_seq_pass": pass_ok("baseline_seq", "seq"),
        "baseline_order_pass": pass_ok("baseline_order", "order"),
        "baseline_repeat_pass": pass_ok("baseline_repeat", "repeat"),
        "mut1_rejected_beacon_feed": fail_reason("mut_beacon_feed", "b_foreign_name_present"),
        "mut2_rejected_path_collision": fail_reason("mut_path_collision", "a_beacon_entry_missing"),
    }
    out["killed"] = all(out["ok"].values())
    return out


def main():
    t_start = time.monotonic()
    wipe(ROOT)
    for d in (PROJ, OUT, GEN, LOGS, HOME_DEFAULT, ROOT / "forge"):
        d.mkdir(parents=True, exist_ok=True)

    (PROJ / "project.godot").write_text(PROJECT_GODOT)
    (PROJ / "main.gd").write_text(MAIN_GD)
    (PROJ / "main.tscn").write_text(MAIN_TSCN)
    (PROJ / "preset_id_a.txt").write_text("A\n")
    (PROJ / "preset_id_b.txt").write_text("B\n")
    (PROJ / "export_presets.cfg").write_text(EXPORT_PRESETS)
    forger = ROOT / "forge" / "forged_receipt.sh"
    forger.write_text(FORGED_RECEIPT)
    os.chmod(forger, 0o755)

    gen = {}
    gen["host"] = {
        "uptime": subprocess.run(["uptime"], stdout=subprocess.PIPE).stdout.decode().strip(),
        "loadavg": list(os.getloadavg()),
        "godot_version": subprocess.run([GODOT, "--version"], stdout=subprocess.PIPE).stdout.decode().strip(),
        "template": str(TEMPLATE), "template_exists": TEMPLATE.is_file(),
    }

    r = run([GODOT, "--headless", "--path", str(PROJ), "--import"], env=base_env())
    (LOGS / "import.log").write_bytes(r["stdout"] + b"---STDERR---" + r["stderr"])
    gen["import"] = rec(r, "import")

    # --- genuine sequential arm -------------------------------------------------
    a_bin, b_bin = GEN / "a.x86_64", GEN / "b.x86_64"
    r = run([GODOT, "--headless", "--path", str(PROJ), "--export-release",
             "A", str(a_bin)], env=base_env())
    (LOGS / "expA.log").write_bytes(r["stdout"] + b"---STDERR---" + r["stderr"])
    gen["exportA"] = rec(r, "exportA")
    gen["runA"] = rec(run([str(a_bin), "--headless", "--quit-after", "30"],
                          env=child_env(), cwd=str(GEN)), "runA")
    gen["shaA_pre"] = {"bin": sha256_file(a_bin), "pck": sha256_file(GEN / "a.pck")}

    r = run([GODOT, "--headless", "--path", str(PROJ), "--export-release",
             "B", str(b_bin)], env=base_env())
    (LOGS / "expB.log").write_bytes(r["stdout"] + b"---STDERR---" + r["stderr"])
    gen["exportB"] = rec(r, "exportB")
    gen["shaA_post"] = {"bin": sha256_file(a_bin), "pck": sha256_file(GEN / "a.pck")}
    gen["runB"] = rec(run([str(b_bin), "--headless", "--quit-after", "30"],
                          env=child_env(), cwd=str(GEN)), "runB")

    rowA_gen = classify_rowA(gen, "genuine")
    rowB_gen = classify_rowB(gen, "genuine")

    # --- mutation: cross-contamination (B exported onto A's binary path) -------
    r = run([GODOT, "--headless", "--path", str(PROJ), "--export-release",
             "B", str(a_bin)], env=base_env(), timeout=180)
    (LOGS / "mutB_over_A.log").write_bytes(r["stdout"] + b"---STDERR---" + r["stderr"])
    gen["mut_exportB_onto_A"] = rec(r, "mut_exportB_onto_A")
    gen["runA_mut"] = rec(run([str(a_bin), "--headless", "--quit-after", "30"],
                              env=child_env(), cwd=str(GEN)), "runA_mut")
    gen["shaA_after_mut"] = {"bin": sha256_file(a_bin), "pck": sha256_file(GEN / "a.pck")}
    rowA_mut = classify_rowA(gen, "mut")

    # --- forger: receipt echo, no work -----------------------------------------
    forged = run(["/bin/sh", str(forger)], env=child_env(), cwd=str(ROOT / "forge"))
    gen["forger"] = rec(forged, "forger")
    forge_line = [l for l in forged["stdout"].decode().split("\n") if l.startswith("PASS ")]
    # Anchored recompute at forger time: predicates read disk + artifact, not the
    # transcript. Two forge arms: (a) contaminated disk, (b) fresh empty dir —
    # the echo carries rc0 + a clean M3_ID transcript but conjures no artifacts.
    rowA_forge = classify_rowA(gen, "mut")  # same disk state as mut (forger wrote nothing)
    rowA_forge["forged_claim"] = forge_line[0] if forge_line else None
    rowA_forge["forger_rc"] = forged["rc"]
    fresh = OUT / "forge_empty"
    fresh.mkdir(exist_ok=True)
    g_fresh = dict(gen)
    g_fresh["runA_mut"] = {"rc": forged["rc"], "m3_ids": ids_from_stdout(forged)}
    rowA_forge_fresh = classify_rowA(g_fresh, "mut", base=fresh)
    rowA_forge_fresh["forged_claim"] = forge_line[0] if forge_line else None
    rowA_forge_fresh["forger_rc"] = forged["rc"]

    verdicts = {
        "rowA_genuine": rowA_gen,
        "rowB_genuine": rowB_gen,
        "rowA_contaminated": rowA_mut,
        "rowA_forger_on_contaminated_disk": rowA_forge,
        "rowA_forger_on_fresh_disk": rowA_forge_fresh,
    }
    killed = (rowA_gen["verdict"] == "PASS" and rowB_gen["verdict"] == "PASS"
              and rowA_mut["verdict"] == "REJECT"
              and rowA_forge["verdict"] == "REJECT"
              and rowA_forge_fresh["verdict"] == "REJECT")
    targeted = None
    if FIXTURE.is_file():
        targeted = phase_targeted()
        killed = killed and targeted["killed"]
    payload = {
        "seat": "r103-mut3 (KEY=M3)",
        "mandate": "cross-contamination must REJECT E3 (export_div_s03 multi-preset sequential)",
        "fixture_landed": FIXTURE.is_file(),
        "fixture_sha256": sha256_file(FIXTURE) if FIXTURE.is_file() else None,
        "date": "2026-10-18",
        "host": gen["host"],
        "verdicts": verdicts,
        "targeted": targeted,
        "killed": killed,
        "replay_seconds": round(time.monotonic() - t_start, 1),
        "runs": {k: gen[k] for k in ("import", "exportA", "runA", "exportB", "runB",
                                     "mut_exportB_onto_A", "runA_mut", "forger")},
        "shas": {"shaA_pre": gen["shaA_pre"], "shaA_post": gen["shaA_post"],
                 "shaA_after_mut": gen["shaA_after_mut"]},
    }
    out_path = ROOT / "mut03_verdicts.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"verdicts": {k: (v["verdict"], v.get("failed")) for k, v in verdicts.items()},
                      "targeted_ok": (targeted or {}).get("ok"),
                      "killed": killed,
                      "shas": payload["shas"],
                      "runA_mut_stdout": gen["runA_mut"]["stdout_head"],
                      "forger_stdout": gen["forger"]["stdout_head"],
                      "host": gen["host"],
                      "replay_seconds": payload["replay_seconds"]}, indent=2))
    print("verdicts: %s" % out_path)
    return 0 if killed else 1


if __name__ == "__main__":
    sys.exit(main())
